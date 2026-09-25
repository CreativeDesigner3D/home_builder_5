"""Edge handles on frameless fronts.

Besides a pull model on the face, a front can be opened by its edge: a
tab pull fixed to the back and folded over the edge, a continuous pull
running the whole edge, or a finger notch cut into it. These are drawn
from the front's own size, so they follow it when it is resized.

Which edge: drawer and pullout fronts, base doors -- the top; upper and
flip-up doors -- the bottom; tall doors -- the latch side. A tab on a door
sits the pull offset in from the latch side, the way a pull does; on a
drawer it is centred.

The handle type is the room's door or drawer default unless the front
carries its own (HANDLE_TYPE).
"""

import bpy
import bmesh
import math
from ...units import inch
from ...hb_types import GeoNodeCutpart

HANDLE_TYPES = [
    ('PULL', "Pull", "The pull model picked for the room"),
    ('TAB', "Tab Pull", "A tab fixed to the back of the front and folded over its edge"),
    ('CONTINUOUS', "Continuous Pull", "An extruded pull along the whole edge"),
    ('FINGER_NOTCH', "Finger Notch", "A notch cut into the edge"),
    ('NONE', "None", "No handle"),
]
HANDLE_KEY = 'HANDLE_TYPE'
PART_TAG = 'IS_EDGE_PULL'
SIGNATURE_KEY = 'hb_edge_pull_signature'
NOTCH_MOD = 'Finger Notch'

PLATE_T = inch(0.0625)      # tab / extrusion stock
TAB_RISE = inch(0.625)      # how far a tab stands past the edge
TAB_DROP = inch(1.0)        # how far it runs down the back of the front
LIP_CLEAR = inch(0.0625)    # the folded lip clears the face by this
CONT_PROJECT = inch(0.625)  # a continuous pull's lip stands off the face
CONT_LIP = inch(0.625)      # and turns down this far
NOTCH_WIDTH = inch(3.0)
NOTCH_DEPTH = inch(1.0)
_EDGE_BY_LOCATION = {0: 'TOP', 1: 'LATCH', 2: 'BOTTOM'}


def _room():
    from ... import hb_project
    return hb_project.get_main_scene().hb_frameless


def _is_drawer(front_obj):
    return bool(front_obj.get('IS_DRAWER_FRONT')
                or front_obj.get('IS_PULLOUT_FRONT'))


def handle_type(front_obj):
    """The handle a front is opened by: its own pick, else the room's
    door or drawer default."""
    own = front_obj.get(HANDLE_KEY, '')
    if own:
        return own
    room = _room()
    attr = 'drawer_handle_type' if _is_drawer(front_obj) else 'door_handle_type'
    return getattr(room, attr, 'PULL')


def _prompt(obj, name, default):
    value = obj.get(name, default)
    return default if value is None else float(value)


def _layout(front_obj, length, width):
    """(edge, mapping, span along the edge, centre of a short handle).

    The mapping turns edge coordinates -- u along the edge, v out past it,
    w through the front (0 at the back, the thickness at the face) -- into
    the front's local space, where X runs up the front, Y across it and
    Z out of its face."""
    try:
        mirrored = bool(GeoNodeCutpart(front_obj).get_input('Mirror Y'))
    except Exception:
        mirrored = False
    y_lo, y_hi = (-width, 0.0) if mirrored else (0.0, width)
    # The origin is the hinge side; the latch is the far side.
    latch = y_lo if mirrored else y_hi
    offset = _prompt(front_obj, 'Handle Horizontal Location', inch(2.0))
    if _is_drawer(front_obj):
        edge = 'TOP'
    elif front_obj.get('IS_FLIP_UP_DOOR'):
        edge = 'BOTTOM'
    else:
        edge = _EDGE_BY_LOCATION.get(int(_prompt(front_obj, 'Pull Location', 0)),
                                     'TOP')
    if edge in ('TOP', 'BOTTOM'):
        sign = 1.0 if edge == 'TOP' else -1.0
        base = length if edge == 'TOP' else 0.0

        def to_local(u, v, w):
            return (base + sign * v, u, w)
        span = (y_lo, y_hi)
        if _is_drawer(front_obj) or front_obj.get('IS_FLIP_UP_DOOR'):
            centre = (y_lo + y_hi) / 2.0
        else:
            centre = latch + offset if mirrored else latch - offset
    else:
        sign = -1.0 if mirrored else 1.0

        def to_local(u, v, w):
            return (u, latch + sign * v, w)
        span = (0.0, length)
        centre = _prompt(front_obj, 'Tall Pull Vertical Location', length / 2.0)
    return edge, to_local, span, centre


def _clamp_centre(centre, span, size):
    lo, hi = min(span), max(span)
    half = min(size, hi - lo) / 2.0
    return min(max(centre, lo + half), hi - half)


def _prism(bm, to_local, u0, u1, profile):
    """A (v, w) profile swept along u from u0 to u1."""
    a = [bm.verts.new(to_local(u0, v, w)) for v, w in profile]
    b = [bm.verts.new(to_local(u1, v, w)) for v, w in profile]
    n = len(profile)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))


def _new_mesh_object(front_obj, name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    for coll in front_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = front_obj
    obj[PART_TAG] = True
    return obj


def _finish_material():
    from ..closets import pulls_closets
    return pulls_closets.load_finish_material(
        getattr(_room(), 'pull_finish', 'Polished Chrome'))


def _build_tab(front_obj, to_local, u0, u1, thickness):
    t = PLATE_T
    bm = bmesh.new()
    # Leg fixed to the back of the front, standing past the edge ...
    _prism(bm, to_local, u0, u1,
           [(-TAB_DROP, -t), (TAB_RISE, -t), (TAB_RISE, 0.0), (-TAB_DROP, 0.0)])
    # ... and the lip folded over the edge towards the face.
    _prism(bm, to_local, u0, u1,
           [(TAB_RISE - t, 0.0), (TAB_RISE, 0.0),
            (TAB_RISE, thickness + LIP_CLEAR), (TAB_RISE - t, thickness + LIP_CLEAR)])
    obj = _new_mesh_object(front_obj, 'Tab Pull', bm)
    obj['hb_part_role'] = 'TAB_PULL'
    return obj


def _build_continuous(front_obj, to_local, u0, u1, thickness):
    t = PLATE_T
    reach = thickness + CONT_PROJECT
    bm = bmesh.new()
    # A cap on the edge running out past the face ...
    _prism(bm, to_local, u0, u1,
           [(0.0, 0.0), (t, 0.0), (t, reach), (0.0, reach)])
    # ... turned down into the lip the fingers find.
    _prism(bm, to_local, u0, u1,
           [(-CONT_LIP, reach - t), (0.0, reach - t), (0.0, reach), (-CONT_LIP, reach)])
    obj = _new_mesh_object(front_obj, 'Continuous Pull', bm)
    obj['hb_part_role'] = 'CONTINUOUS_PULL'
    return obj


def _build_notch(front_obj, to_local, centre, thickness):
    """A shallow arch cut into the edge, through the front."""
    margin = inch(0.25)
    half = NOTCH_WIDTH / 2.0
    segments = 16
    outline = [(centre + half, margin)]
    for k in range(segments + 1):
        a = math.pi * k / segments
        outline.append((centre + half * math.cos(a), -NOTCH_DEPTH * math.sin(a)))
    outline.append((centre - half, margin))
    bm = bmesh.new()
    lo = [bm.verts.new(to_local(u, v, -margin)) for u, v in outline]
    hi = [bm.verts.new(to_local(u, v, thickness + margin)) for u, v in outline]
    n = len(outline)
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    cutter = _new_mesh_object(front_obj, 'Finger Notch Cutter', bm)
    cutter['hb_part_role'] = 'FINGER_NOTCH_CUTTER'
    cutter.display_type = 'WIRE'
    cutter.hide_viewport = True
    cutter.hide_render = True
    try:
        mat = GeoNodeCutpart(front_obj).get_input('Top Surface')
    except Exception:
        mat = None
    if mat is not None:
        cutter.data.materials.append(mat)
    mod = front_obj.modifiers.new(NOTCH_MOD, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.material_mode = 'TRANSFER'
    mod.solver = 'MANIFOLD'
    mod.object = cutter
    return cutter


def _clear(front_obj):
    mod = front_obj.modifiers.get(NOTCH_MOD)
    if mod is not None:
        front_obj.modifiers.remove(mod)
    for child in list(front_obj.children):
        if child.get(PART_TAG):
            data = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)


def solve_front(front_obj, length, width, thickness, hidden):
    """Build the edge handle a front asks for, or take it off. Rebuilt
    only when something that shapes it has changed."""
    kind = 'NONE' if hidden else handle_type(front_obj)
    if kind not in ('TAB', 'CONTINUOUS', 'FINGER_NOTCH'):
        if SIGNATURE_KEY in front_obj or front_obj.modifiers.get(NOTCH_MOD):
            _clear(front_obj)
            front_obj.pop(SIGNATURE_KEY, None)
        return
    edge, to_local, span, centre = _layout(front_obj, length, width)
    room = _room()
    tab_width = float(getattr(room, 'tab_pull_width', inch(2.0)))
    signature = repr((kind, edge, round(length, 5), round(width, 5),
                      round(thickness, 5), round(centre, 5),
                      round(tab_width, 5), getattr(room, 'pull_finish', '')))
    parts = [c for c in front_obj.children if c.get(PART_TAG)]
    if front_obj.get(SIGNATURE_KEY) == signature and parts:
        return
    _clear(front_obj)
    if kind == 'CONTINUOUS':
        obj = _build_continuous(front_obj, to_local, min(span), max(span),
                                thickness)
    elif kind == 'TAB':
        c = _clamp_centre(centre, span, tab_width)
        obj = _build_tab(front_obj, to_local, c - tab_width / 2.0,
                         c + tab_width / 2.0, thickness)
    else:
        c = _clamp_centre(centre, span, NOTCH_WIDTH)
        obj = _build_notch(front_obj, to_local, c, thickness)
    if kind in ('TAB', 'CONTINUOUS'):
        mat = _finish_material()
        if mat is not None:
            obj.data.materials.append(mat)
    front_obj[SIGNATURE_KEY] = signature
