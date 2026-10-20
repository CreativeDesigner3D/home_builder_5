"""Selection outline that follows a cabinet's actual shape.

A selected cabinet is outlined by its root cage, which is sized from
the cabinet's Width / Depth / Height. A bay built deeper, taller or
shorter than the cabinet (a deep section behind a shallow run, a
stepped upper) doesn't match that box, so the outline cut through the
cabinet or wrapped empty space.

A POST_VIEW draw handler traces each selected cabinet's real outline in
the selection colour, from its carcass, face frame and sub kick,
stepping wherever the depth or height changes along the width. Fronts
and hardware are left out so the outline doesn't jog at every door.
Edges within 1/4" of the cabinet box land on it, and narrow strips (a
stile over the scribe) fold into their neighbour, so a cabinet whose
shape is its box draws nothing extra - the cage outline already is its
outline.
The cage itself, and everything that reads it (snapping, placement,
dimensions, drawings), is unchanged.
"""

import bpy
import gpu
from mathutils import Vector

from ... import hb_utils
from . import types_face_frame

LINE_WIDTH = 2.0
# Two boundaries closer than this are the same boundary.
_EPS = 0.0008

# A section edge this close to the cabinet box is taken as the box's
# own edge: scribes, a 1/4 back and the kick setback stay inside it.
_SNAP = 0.00635
# Sections at most this wide fold into a neighbour that contains them.
_SLIVER = 0.0254

# Parts that set the cabinet's real extent: carcass, face frame and the
# sub kick. Fronts and hardware stand proud of the face frame and are
# left out.
_STRUCTURE_ROLES = frozenset((
    types_face_frame.PART_ROLE_LEFT_SIDE,
    types_face_frame.PART_ROLE_RIGHT_SIDE,
    types_face_frame.PART_ROLE_BACK,
    types_face_frame.PART_ROLE_BOTTOM,
    types_face_frame.PART_ROLE_TOP,
    types_face_frame.PART_ROLE_MID_DIVISION,
    types_face_frame.PART_ROLE_PARTITION_SKIN,
    types_face_frame.PART_ROLE_FRONT_STRETCHER,
    types_face_frame.PART_ROLE_REAR_STRETCHER,
    types_face_frame.PART_ROLE_TOE_KICK_SUBFRONT,
    types_face_frame.PART_ROLE_TOE_KICK_SUBREAR,
    types_face_frame.PART_ROLE_LOOSE_KICK_FRONT,
    types_face_frame.PART_ROLE_LOOSE_KICK_REAR,
    types_face_frame.PART_ROLE_LOOSE_KICK_END_LEFT,
    types_face_frame.PART_ROLE_LOOSE_KICK_END_RIGHT,
)) | types_face_frame.FACE_FRAME_PART_ROLES

_draw_handle = None
_shutdown = False


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def _local_box(obj, to_root):
    """(min, max) of obj's bound box in the root's local frame."""
    m = to_root @ obj.matrix_world
    pts = [m @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts),
                 min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts),
                 max(p.z for p in pts)))
    return lo, hi


def _cage_box(root, to_root):
    """The cabinet box from the root cage's Dim / Mirror inputs (its
    bound box is empty while the cage is hidden or unevaluated)."""
    for m in root.modifiers:
        if m.type != 'NODES' or m.node_group is None:
            continue
        ids = {it.name: it.identifier
               for it in m.node_group.interface.items_tree
               if getattr(it, 'in_out', None) == 'INPUT'}
        vals = [hb_utils.try_get_gn_input(m, ids.get(k, ''))
                for k in ('Dim X', 'Dim Y', 'Dim Z')]
        if any(v is None for v in vals):
            continue
        lo, hi = Vector(), Vector()
        for i, (dim, mirror) in enumerate(zip(vals, ('Mirror X', 'Mirror Y',
                                                     'Mirror Z'))):
            if hb_utils.try_get_gn_input(m, ids.get(mirror, '')):
                lo[i], hi[i] = -dim, 0.0
            else:
                lo[i], hi[i] = 0.0, dim
        return lo, hi
    return _local_box(root, to_root)


def _boxes(root):
    """(cabinet box, [visible structural part boxes]), root-local."""
    to_root = root.matrix_world.inverted()
    parts = []
    for part in root.children_recursive:
        if part.type != 'MESH' or part.hide_viewport:
            continue
        if part.get('hb_part_role') not in _STRUCTURE_ROLES:
            continue
        parts.append(_local_box(part, to_root))
    return _cage_box(root, to_root), parts


def _snap(v, targets):
    for t in targets:
        if abs(v - t) <= _SNAP:
            return t
    return v


def _same(a, b):
    return all(abs(x - y) <= _EPS for x, y in zip(a, b))


def _sections(boxes):
    """Slice the boxes along X: [(x0, x1, (y0, y1, z0, z1))], adjacent
    slices with the same cross-section merged. A slice's section is the
    span of every box covering it."""
    xs = sorted({round(v, 5) for lo, hi in boxes for v in (lo.x, hi.x)})
    out = []
    for x0, x1 in zip(xs, xs[1:]):
        if x1 - x0 <= _EPS:
            continue
        mid = (x0 + x1) * 0.5
        cover = [(lo, hi) for lo, hi in boxes if lo.x <= mid <= hi.x]
        if not cover:
            continue
        rect = (min(lo.y for lo, _hi in cover), max(hi.y for _lo, hi in cover),
                min(lo.z for lo, _hi in cover), max(hi.z for _lo, hi in cover))
        if out and abs(out[-1][1] - x0) <= _EPS and _same(out[-1][2], rect):
            out[-1] = (out[-1][0], x1, rect)
        else:
            out.append((x0, x1, rect))
    return out


def _contains(outer, inner):
    return (outer[0] <= inner[0] + _EPS and outer[1] >= inner[1] - _EPS
            and outer[2] <= inner[2] + _EPS and outer[3] >= inner[3] - _EPS)


def _absorb_slivers(sections):
    """Fold narrow sections into a neighbour that contains them: a stile
    overhanging the scribe at the run's end, a division between bays."""
    sections = list(sections)
    changed = True
    while changed and len(sections) > 1:
        changed = False
        for i, (x0, x1, rect) in enumerate(sections):
            if x1 - x0 > _SLIVER:
                continue
            for j in (i - 1, i + 1):
                if not 0 <= j < len(sections):
                    continue
                nx0, nx1, nrect = sections[j]
                touching = (abs(nx1 - x0) <= _EPS if j < i
                            else abs(nx0 - x1) <= _EPS)
                if touching and _contains(nrect, rect):
                    sections[j] = (min(nx0, x0), max(nx1, x1), nrect)
                    del sections[i]
                    changed = True
                    break
            if changed:
                break
    return sections


def _subtract(span, cuts):
    """Parts of the 1D span (a, b) not covered by any of cuts."""
    pieces = [span]
    for c0, c1 in cuts:
        nxt = []
        for a, b in pieces:
            if c1 <= a + _EPS or c0 >= b - _EPS:
                nxt.append((a, b))
                continue
            if c0 > a + _EPS:
                nxt.append((a, c0))
            if c1 < b - _EPS:
                nxt.append((c1, b))
        pieces = nxt
    return pieces


def _rect_edges(rect, other):
    """Edges of one cross-section rectangle on a boundary plane, minus
    the stretches the neighbouring section continues smoothly (its edge
    on the same line and the same side). (y0, y1, z0, z1) each."""
    y0, y1, z0, z1 = rect
    edges = []
    for z, is_top in ((z0, False), (z1, True)):        # along Y
        cuts = []
        if other is not None:
            oz = other[3] if is_top else other[2]
            if abs(oz - z) <= _EPS:
                cuts.append((other[0], other[1]))
        edges += [('Y', a, b, z) for a, b in _subtract((y0, y1), cuts)]
    for y, is_back in ((y0, False), (y1, True)):       # along Z
        cuts = []
        if other is not None:
            oy = other[1] if is_back else other[0]
            if abs(oy - y) <= _EPS:
                cuts.append((other[2], other[3]))
        edges += [('Z', a, b, y) for a, b in _subtract((z0, z1), cuts)]
    return edges


def outline_segments(root):
    """Root-local line segments [(p, q), ...] tracing the cabinet's
    outline, or [] when its carcass stays inside the cabinet box."""
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is not None and cab.cabinet_type == 'PANEL':
        return []
    (cab_lo, cab_hi), parts = _boxes(root)
    raw = _absorb_slivers(_sections(parts))
    if not raw:
        return []
    # Snap near-box edges onto the box (the run's ends onto its sides),
    # then re-merge what snapping made equal.
    ys, zs = (cab_lo.y, cab_hi.y), (cab_lo.z, cab_hi.z)
    sections = []
    for i, (x0, x1, (y0, y1, z0, z1)) in enumerate(raw):
        if i == 0:
            x0 = _snap(x0, (cab_lo.x,))
        if i == len(raw) - 1:
            x1 = _snap(x1, (cab_hi.x,))
        rect = (_snap(y0, ys), _snap(y1, ys), _snap(z0, zs), _snap(z1, zs))
        if (sections and abs(sections[-1][1] - x0) <= _EPS
                and _same(sections[-1][2], rect)):
            sections[-1] = (sections[-1][0], x1, rect)
        else:
            sections.append((x0, x1, rect))
    cab_rect = (cab_lo.y, cab_hi.y, cab_lo.z, cab_hi.z)
    if (len(sections) == 1 and abs(sections[0][0] - cab_lo.x) <= _EPS
            and abs(sections[0][1] - cab_hi.x) <= _EPS
            and _same(sections[0][2], cab_rect)):
        return []
    segs = []
    # Edges running along the width.
    for x0, x1, (y0, y1, z0, z1) in sections:
        for y in (y0, y1):
            for z in (z0, z1):
                segs.append((Vector((x0, y, z)), Vector((x1, y, z))))
    # Edges on each boundary plane, between a section and its neighbour
    # (or open air at the ends and at a gap).
    for i, (x0, x1, rect) in enumerate(sections):
        prev = sections[i - 1] if i > 0 else None
        left = prev[2] if prev and abs(prev[1] - x0) <= _EPS else None
        nxt = sections[i + 1] if i + 1 < len(sections) else None
        right = nxt[2] if nxt and abs(nxt[0] - x1) <= _EPS else None
        planes = [(x0, rect, left)]
        if right is None:
            planes.append((x1, rect, None))
        if left is not None:
            # The neighbour's half of this shared plane.
            planes.append((x0, left, rect))
        for x, r, other in planes:
            for axis, a, b, c in _rect_edges(r, other):
                if axis == 'Y':
                    segs.append((Vector((x, a, c)), Vector((x, b, c))))
                else:
                    segs.append((Vector((x, c, a)), Vector((x, c, b))))
    return segs


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _selected_roots(context):
    seen = set()
    for obj in context.selected_objects:
        root = obj if obj.get(types_face_frame.TAG_CABINET_CAGE) else None
        if root is None or root.name in seen:
            continue
        seen.add(root.name)
        yield root


def _draw():
    if _shutdown:
        return
    context = bpy.context
    region = context.region
    if region is None or region.type != 'WINDOW':
        return
    overlay = getattr(context.space_data, 'overlay', None)
    if overlay is not None and not (overlay.show_overlays
                                    and overlay.show_outline_selected):
        return
    try:
        roots = list(_selected_roots(context))
        active = context.active_object
    except (AttributeError, RuntimeError):
        return
    # Same colours as Blender's own outline: active, then selected.
    coords = {True: [], False: []}
    for root in roots:
        try:
            segs = outline_segments(root)
        except (ReferenceError, RuntimeError):
            continue
        mw = root.matrix_world
        out = coords[root == active]
        for p, q in segs:
            out.append(mw @ p)
            out.append(mw @ q)
    if not (coords[True] or coords[False]):
        return
    theme = context.preferences.themes[0].view_3d
    colors = {True: tuple(theme.object_active) + (1.0,),
              False: tuple(theme.object_selected) + (1.0,)}
    s = 1.0
    try:
        s = context.preferences.system.ui_scale
    except AttributeError:
        pass
    from gpu_extras.batch import batch_for_shader
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float('viewportSize', (region.width, region.height))
    shader.uniform_float('lineWidth', LINE_WIDTH * s)
    for is_active, pts in coords.items():
        if not pts:
            continue
        shader.uniform_float('color', colors[is_active])
        batch_for_shader(shader, 'LINES', {'pos': pts}).draw(shader)
    gpu.state.blend_set('NONE')


def register():
    global _draw_handle, _shutdown
    _shutdown = False
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global _draw_handle, _shutdown
    _shutdown = True
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
