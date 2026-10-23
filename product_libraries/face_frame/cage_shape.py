"""Cabinet cage shaped like the cabinet.

A face frame cabinet's root cage is the box its Width / Depth / Height
describe - what selecting a cabinet outlines, washes and clicks. A bay
built deeper, taller or shorter than the cabinet (a deep section behind
a shallow run, a stepped upper) doesn't match that box, so the selected
cabinet showed a box cutting through it or wrapping empty space.

After each recalc the cage is reshaped to the cabinet's real outline,
traced from its carcass, face frame and sub kick and stepping wherever
the depth or height changes along the width (fronts and hardware stand
proud of the face frame and are left out). The stepped mesh is written
into the cage's own mesh with the cage modifier switched off - the same
static-mesh swap shaped parts use - so the modifier's Dim inputs, which
placement, snapping, dimensions, drawings and pricing read, keep the
cabinet's nominal size. Edges within 1/4" of the box land on it and
narrow strips (a stile over the scribe, a division between bays) fold
into their neighbour; a cabinet whose shape is its box keeps the live
modifier box.

The reshape runs on a timer after the recalc, once the parts it reads
have been evaluated, and over every cabinet when a file opens.
"""

import bmesh
import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

from ... import hb_utils
from . import types_face_frame

# Two boundaries closer than this are the same boundary.
_EPS = 0.0008

# A section edge this close to the cabinet box is taken as the box's
# own edge: scribes, a 1/4 back and the kick setback stay inside it.
_SNAP = 0.00635
# Sections at most this wide fold into a neighbour that contains them.
_SLIVER = 0.0254

# Stamped on a root whose cage carries the stepped mesh.
TAG_SHAPED_CAGE = 'HB_SHAPED_CAGE'

# Parts that set the cabinet's real extent: carcass, face frame and the
# sub kick, and a leg's panels, stile, kick, back and nailers (a leg's
# panels and back can run deeper than its box). Fronts, hardware and
# finish kicks stand proud of the face frame and are left out.
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
    types_face_frame.PART_ROLE_LEG_PANEL_LEFT,
    types_face_frame.PART_ROLE_LEG_PANEL_RIGHT,
    types_face_frame.PART_ROLE_LEG_STILE,
    types_face_frame.PART_ROLE_LEG_TK_STILE,
    types_face_frame.PART_ROLE_LEG_TK_FILLER,
    types_face_frame.PART_ROLE_LEG_FINISH_X_LEFT,
    types_face_frame.PART_ROLE_LEG_FINISH_X_RIGHT,
    types_face_frame.PART_ROLE_LEG_BACK,
    types_face_frame.PART_ROLE_LEG_NAILER_LEFT,
    types_face_frame.PART_ROLE_LEG_NAILER_RIGHT,
    types_face_frame.PART_ROLE_LEG_CURVED_PANEL,
)) | types_face_frame.FACE_FRAME_PART_ROLES

_pending = set()


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


def shape_sections(root):
    """The cabinet's outline as X sections [(x0, x1, (y0, y1, z0, z1))]
    in the root's local frame, or None when it is the cabinet box."""
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is None or cab.cabinet_type == 'PANEL':
        return None
    (cab_lo, cab_hi), parts = _boxes(root)
    raw = _absorb_slivers(_sections(parts))
    if not raw:
        return None
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
        return None
    return sections


def _spans(lo, hi, values):
    """(lo, hi) split at every value strictly inside it."""
    pts = sorted({lo, hi} | {v for v in values if lo + _EPS < v < hi - _EPS})
    return list(zip(pts, pts[1:]))


def _plane_cells(a, b, ys, zs):
    """Grid cells of the plane between section rects a and b (either may
    be None) that exactly one side covers: the step faces."""
    lo_y = min(r[0] for r in (a, b) if r)
    hi_y = max(r[1] for r in (a, b) if r)
    lo_z = min(r[2] for r in (a, b) if r)
    hi_z = max(r[3] for r in (a, b) if r)

    def inside(r, y, z):
        return r is not None and r[0] < y < r[1] and r[2] < z < r[3]

    cells = []
    for y0, y1 in _spans(lo_y, hi_y, ys):
        for z0, z1 in _spans(lo_z, hi_z, zs):
            y, z = (y0 + y1) * 0.5, (z0 + z1) * 0.5
            if inside(a, y, z) != inside(b, y, z):
                cells.append((y0, y1, z0, z1))
    return cells


def build_mesh(sections, mesh):
    """Write the closed solid of the sections into mesh."""
    bm = bmesh.new()

    def quad(pts):
        bm.faces.new([bm.verts.new(p) for p in pts])

    # Every face is split at every section edge running across it, so a
    # step's corners always land on vertices (no T-junctions).
    ys = {v for _x0, _x1, r in sections for v in r[:2]}
    zs = {v for _x0, _x1, r in sections for v in r[2:]}
    for x0, x1, (y0, y1, z0, z1) in sections:
        for za, zb in _spans(z0, z1, zs):
            quad(((x0, y0, za), (x1, y0, za), (x1, y0, zb), (x0, y0, zb)))
            quad(((x0, y1, za), (x0, y1, zb), (x1, y1, zb), (x1, y1, za)))
        for ya, yb in _spans(y0, y1, ys):
            quad(((x0, ya, z0), (x0, yb, z0), (x1, yb, z0), (x1, ya, z0)))
            quad(((x0, ya, z1), (x1, ya, z1), (x1, yb, z1), (x0, yb, z1)))
    planes = []
    for i, (x0, x1, rect) in enumerate(sections):
        prev = sections[i - 1] if i else None
        if prev is None or abs(prev[1] - x0) > _EPS:
            planes.append((x0, None, rect))
            if prev is not None:
                planes.append((prev[1], prev[2], None))
        else:
            planes.append((x0, prev[2], rect))
    planes.append((sections[-1][1], sections[-1][2], None))
    for x, a, b in planes:
        for y0, y1, z0, z1 in _plane_cells(a, b, ys, zs):
            quad(((x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=_EPS * 0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def _cage_modifier(root):
    mod_name = getattr(root.home_builder, 'mod_name', '')
    mod = root.modifiers.get(mod_name) if mod_name else None
    if mod is None:
        mod = next((m for m in root.modifiers if m.type == 'NODES'), None)
    return mod


def reshape(root):
    """Give the root cage the cabinet's outline, or put it back on the
    live box when the cabinet is its box."""
    mod = _cage_modifier(root)
    if mod is None:
        return
    sections = shape_sections(root)
    if sections is None:
        if root.get(TAG_SHAPED_CAGE):
            root.data.clear_geometry()
            root.data.update()
            mod.show_viewport = True
            del root[TAG_SHAPED_CAGE]
        return
    if root.data.users > 1:
        # A duplicate may share the mesh; never reshape the other copy.
        root.data = root.data.copy()
    build_mesh(sections, root.data)
    if mod.show_viewport:
        mod.show_viewport = False
    root[TAG_SHAPED_CAGE] = True


def flush():
    """Reshape every cabinet a recalc queued. One-shot timer."""
    names = list(_pending)
    _pending.clear()
    if not names:
        return None
    try:
        bpy.context.view_layer.update()
    except Exception:
        pass
    for name in names:
        root = bpy.data.objects.get(name)
        if root is None or not root.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        try:
            reshape(root)
        except (ReferenceError, RuntimeError):
            pass
    return None


def _queue(root):
    if root is None:
        return
    _pending.add(root.name)
    if not bpy.app.timers.is_registered(flush):
        bpy.app.timers.register(flush, first_interval=0.0)


@persistent
def _on_load_post(_dummy):
    for obj in bpy.data.objects:
        if obj.get(types_face_frame.TAG_CABINET_CAGE):
            _pending.add(obj.name)
    if _pending and not bpy.app.timers.is_registered(flush):
        bpy.app.timers.register(flush, first_interval=0.2)


def register():
    if _queue not in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.append(_queue)
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)


def unregister():
    if _queue in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.remove(_queue)
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    if bpy.app.timers.is_registered(flush):
        bpy.app.timers.unregister(flush)
    _pending.clear()
