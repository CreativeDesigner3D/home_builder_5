"""
Wall backsplashes: a thin tiled skin on the room face of a wall, above
the countertop.

Rendering dressing, not cabinetry. A backsplash carries IS_RENDER_ONLY,
which keeps it out of every 2D layout view -- is_helper_object skips
those objects when a view walks a wall's children.

Geometry lives in WALL-LOCAL space, the same frame the countertop
generator uses: X runs along the wall, the wall body spans Y from 0 (the
origin line, its back face) to +thickness, so local -Y is the room and a
front-side splash sits between -thickness and 0. Cabinets on the far face
of a wall are parented with a 180-degree Z rotation and get a back-side
splash on the other side; the two are independent.

The shape is a rectilinear profile in XZ, extruded through the slab
thickness: one segment per span of constant height, so a run whose
uppers stop over the range steps up over the gap the way tile really
does. Segments are the object's own stored state -- the edit modal in
operators/ops_surfaces.py drags their edges and calls rebuild(), so
what is adjusted by hand survives every later rebuild.

Doors and windows cut a wall with BOOLEAN modifiers on the wall object
itself. A child does not inherit those, so the wall's cutters are
mirrored onto the splash (sync_cutters) or a window over the sink comes
out tiled over.
"""

import bmesh
import bpy
from mathutils import Vector

from . import hb_types

TAG = 'IS_BACKSPLASH'
RENDER_ONLY_TAG = 'IS_RENDER_ONLY'
MENU_ID = 'HOME_BUILDER_MT_backsplash_commands'
CUT_PREFIX = "Splash Cut - "

INCH = 0.0254
TOL = 1e-5

# Cabinet cage markers for both product libraries -- a backsplash does
# not care which one drew the kitchen.
CABINET_CAGE_TAGS = (
    'IS_FACE_FRAME_CABINET_CAGE',
    'IS_FRAMELESS_CABINET_CAGE',
)

# A gap in the base run wider than this reads as two separate runs (a
# doorway, a walk-through) rather than an appliance. Tile carries across
# a range or a dishwasher, so anything narrower stays one splash.
RUN_SPLIT_GAP = 36 * INCH

# Fallbacks when the scene has not been told otherwise.
DEFAULT_THICKNESS = 0.375 * INCH
DEFAULT_HEIGHT = 18 * INCH
DEFAULT_COUNTERTOP_THICKNESS = 1.5 * INCH
MIN_HEIGHT = 2 * INCH
MIN_SPAN = 2 * INCH

HEIGHT_MODE_ITEMS = [
    ('FIXED', "Fixed Height",
     "One height for the whole run, measured up from the countertop",
     'DRIVER_DISTANCE', 0),
    ('UPPERS', "Up to the Uppers",
     "Run to the underside of the upper cabinets, and to the fixed "
     "height across the gaps between them", 'ALIGN_TOP', 1),
    ('CEILING', "Full Height",
     "Run all the way up the wall", 'SORT_DESC', 2),
]


# ---------------------------------------------------------------------------
# Reading the room
# ---------------------------------------------------------------------------

def is_backsplash(obj):
    return bool(obj is not None and obj.get(TAG))


def wall_of(obj):
    """The wall a backsplash hangs on, or None."""
    node = obj
    while node is not None:
        if node.get('IS_WALL_BP'):
            return node
        node = node.parent
    return None


def wall_dims(wall):
    """(length, height, thickness) of a wall, in metres."""
    node = hb_types.GeoNodeWall(wall)
    return (node.get_input('Length'), node.get_input('Height'),
            node.get_input('Thickness'))


def _is_cabinet_cage(obj):
    return any(obj.get(tag) for tag in CABINET_CAGE_TAGS)


def _is_back_side(obj):
    """Product on the far face of a wall is parented rotated 180 degrees."""
    rz = abs(obj.rotation_euler.z)
    return abs(rz - 3.14159265) < 0.1


def _cabinet_x_range(obj):
    """Wall-local (x0, x1). A back-side cabinet's origin sits at its
    geometric right edge with the body running in -X."""
    dim_x = hb_types.GeoNodeCage(obj).get_input('Dim X')
    if _is_back_side(obj):
        return (obj.location.x - dim_x, obj.location.x)
    return (obj.location.x, obj.location.x + dim_x)


def _cabinets_on(wall, is_back, cabinet_type):
    out = []
    for child in wall.children:
        if not _is_cabinet_cage(child):
            continue
        if child.get('CABINET_TYPE') != cabinet_type:
            continue
        if _is_back_side(child) != is_back:
            continue
        out.append(child)
    return out


def _countertop_top(wall, x0, x1):
    """Top Z of any countertop on this wall overlapping the run, or None.

    Countertop meshes are built directly in wall-local coordinates, so
    the mesh bounds are already in the frame the splash works in -- but
    go through matrix_local anyway in case one has been nudged.
    """
    best = None
    for child in wall.children:
        if not child.get('IS_COUNTERTOP') or child.type != 'MESH':
            continue
        mat = child.matrix_local
        corners = [mat @ Vector(c) for c in child.bound_box]
        cx0 = min(c.x for c in corners)
        cx1 = max(c.x for c in corners)
        if cx1 < x0 + TOL or cx0 > x1 - TOL:
            continue
        top = max(c.z for c in corners)
        best = top if best is None else max(best, top)
    return best


def _countertop_thickness(context):
    scene_props = getattr(context.scene, 'hb_face_frame', None)
    value = getattr(scene_props, 'countertop_thickness', 0.0) or 0.0
    return value or DEFAULT_COUNTERTOP_THICKNESS


def upper_spans(wall, is_back, x0, x1):
    """(start, end, underside Z) for the upper cabinets over a run,
    clipped to it, sorted, and never overlapping.

    Where two uppers overlap in X the lower underside wins: tile has to
    stop at whichever cabinet it reaches first.
    """
    raw = []
    for cab in _cabinets_on(wall, is_back, 'UPPER'):
        cx0, cx1 = _cabinet_x_range(cab)
        cx0, cx1 = max(cx0, x0), min(cx1, x1)
        if cx1 - cx0 < TOL:
            continue
        raw.append((cx0, cx1, cab.location.z))
    raw.sort(key=lambda s: (s[0], s[2]))

    spans = []
    cursor = x0
    for sx0, sx1, z in raw:
        sx0 = max(sx0, cursor)
        if sx1 - sx0 < TOL:
            continue
        spans.append((sx0, sx1, z))
        cursor = sx1
    return spans


def base_runs(context, wall_names=None):
    """Every stretch of base cabinets that could carry a backsplash.

    Each run is a dict of wall, side, wall-local X extents and the Z the
    tile starts at (the countertop top). Runs are per wall and per face;
    an appliance gap stays inside one run because tile carries behind a
    range, but a doorway-sized gap splits it.
    """
    groups = {}
    for obj in context.scene.objects:
        if not _is_cabinet_cage(obj) or obj.get('CABINET_TYPE') != 'BASE':
            continue
        wall = obj.parent
        if wall is None or not wall.get('IS_WALL_BP'):
            continue
        if wall_names is not None and wall.name not in wall_names:
            continue
        groups.setdefault((wall.name, _is_back_side(obj)), []).append(obj)

    ct_thickness = _countertop_thickness(context)
    runs = []
    for (wall_name, is_back), cabs in groups.items():
        wall = bpy.data.objects.get(wall_name)
        if wall is None:
            continue
        spans = sorted(_cabinet_x_range(c) for c in cabs)
        tops = {}
        for cab in cabs:
            cx0, cx1 = _cabinet_x_range(cab)
            cage = hb_types.GeoNodeCage(cab)
            tops[(cx0, cx1)] = cab.location.z + cage.get_input('Dim Z')

        for group in _split_on_gaps(spans, RUN_SPLIT_GAP):
            x0, x1 = group[0][0], max(s[1] for s in group)
            deck = _countertop_top(wall, x0, x1)
            if deck is None:
                highest = max(tops.get(s, 0.0) for s in group)
                deck = highest + ct_thickness
            runs.append({'wall': wall, 'is_back': is_back,
                         'x0': x0, 'x1': x1, 'z0': deck})
    return runs


def _split_on_gaps(spans, max_gap):
    """Group sorted (x0, x1) spans, breaking where the clear gap between
    consecutive cabinets exceeds max_gap."""
    groups = []
    current = []
    reach = None
    for span in spans:
        if current and span[0] - reach > max_gap:
            groups.append(current)
            current = []
        current.append(span)
        reach = span[1] if reach is None else max(reach, span[1])
    if current:
        groups.append(current)
    return groups


# ---------------------------------------------------------------------------
# Segments -- the stored shape
# ---------------------------------------------------------------------------

def segments_for(wall, is_back, x0, x1, z0, mode, height):
    """Build the (x0, x1, top Z) list for one run under a height mode."""
    _, wall_height, _ = wall_dims(wall)
    if mode == 'CEILING':
        return merge_segments([(x0, x1, wall_height)])
    if mode != 'UPPERS':
        return merge_segments([(x0, x1, z0 + height)])

    fallback = z0 + height
    segs = []
    cursor = x0
    for sx0, sx1, under in upper_spans(wall, is_back, x0, x1):
        if sx0 - cursor > TOL:
            segs.append((cursor, sx0, fallback))
        segs.append((max(sx0, cursor), sx1, max(under, z0 + MIN_HEIGHT)))
        cursor = sx1
    if x1 - cursor > TOL:
        segs.append((cursor, x1, fallback))
    if not segs:
        segs = [(x0, x1, fallback)]
    return merge_segments(segs)


def merge_segments(segs):
    """Drop empty segments and fuse neighbours that share a top, so the
    profile never carries a zero-length step (which would put two verts
    in the same place and break the face)."""
    out = []
    for x0, x1, top in segs:
        if x1 - x0 < TOL:
            continue
        if out and abs(out[-1][2] - top) < TOL and abs(out[-1][1] - x0) < TOL:
            out[-1] = (out[-1][0], x1, top)
        else:
            out.append((x0, x1, top))
    return out


def segments_of(obj):
    """Stored segments as a list of (x0, x1, top). Flat float triples on
    the object, because that is what an ID property can hold."""
    flat = obj.get('bs_segments') or []
    return [(flat[i], flat[i + 1], flat[i + 2])
            for i in range(0, len(flat) - 2, 3)]


def set_segments(obj, segs):
    flat = []
    for x0, x1, top in segs:
        flat.extend((float(x0), float(x1), float(top)))
    obj['bs_segments'] = flat


def bounds_of(obj):
    """(x0, x1, z0, z_top_max) of a backsplash, wall-local."""
    segs = segments_of(obj)
    z0 = obj.get('bs_z0', 0.0)
    if not segs:
        return (0.0, 0.0, z0, z0)
    return (segs[0][0], segs[-1][1], z0, max(s[2] for s in segs))


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def profile_points(segs, z0):
    """The rectilinear outline in (x, z), closed, no repeated points.

    Runs along the bottom left to right, up the right end, back across
    the tops with a vertical step at every change of height, then down
    the left end.
    """
    pts = [(segs[0][0], z0), (segs[-1][1], z0)]
    for x0, x1, top in reversed(segs):
        pts.append((x1, top))
        pts.append((x0, top))

    out = []
    for p in pts:
        if out and abs(out[-1][0] - p[0]) < TOL and abs(out[-1][1] - p[1]) < TOL:
            continue
        out.append(p)
    if (len(out) > 1 and abs(out[0][0] - out[-1][0]) < TOL
            and abs(out[0][1] - out[-1][1]) < TOL):
        out.pop()
    return out


def slab_y(obj, wall):
    """(back Y, front Y) of the slab in wall-local space.

    The back face is buried a hair inside the wall so the two coplanar
    surfaces cannot z-fight in the viewport.
    """
    thickness = obj.get('bs_thickness', DEFAULT_THICKNESS)
    bite = min(0.0005, thickness * 0.25)
    if obj.get('bs_side') == 'BACK':
        _, _, wall_thickness = wall_dims(wall)
        return (wall_thickness - bite, wall_thickness + thickness)
    return (bite, -thickness)


def rebuild(obj):
    """Rewrite the mesh from the object's stored segments.

    Writes into the existing mesh datablock so material slots survive,
    lays down world-scale UVs (1 unit = 1 m, matching the procedural
    surface shaders), and re-mirrors the wall's cutters.
    """
    wall = wall_of(obj)
    if wall is None:
        return
    segs = merge_segments(segments_of(obj))
    if not segs:
        return
    set_segments(obj, segs)
    z0 = obj.get('bs_z0', 0.0)
    y_back, y_front = slab_y(obj, wall)
    profile = profile_points(segs, z0)
    if len(profile) < 3:
        return

    bm = bmesh.new()
    back = [bm.verts.new((x, y_back, z)) for x, z in profile]
    front = [bm.verts.new((x, y_front, z)) for x, z in profile]
    bm.faces.new(back)
    bm.faces.new(list(reversed(front)))
    n = len(profile)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((back[i], back[j], front[j], front[i]))

    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    # World-scale UVs from the wall-local X/Z of each corner: the tile
    # then lays out in real inches however long the run is, and every
    # splash in the room shares one grout grid.
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        for loop in face.loops:
            co = loop.vert.co
            loop[uv_layer].uv = (co.x, co.z)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    sync_cutters(obj, wall)


def sync_cutters(obj, wall):
    """Mirror the wall's door / window boolean cutters onto the splash.

    MANIFOLD rather than EXACT: the 5.1 EXACT solver degenerates on
    meshes made of several islands, and a splash that has already been
    cut once is exactly that.
    """
    for mod in list(obj.modifiers):
        if mod.name.startswith(CUT_PREFIX):
            obj.modifiers.remove(mod)
    for mod in wall.modifiers:
        if (mod.type != 'BOOLEAN' or mod.object is None
                or mod.operation != 'DIFFERENCE'):
            continue
        new = obj.modifiers.new(name=CUT_PREFIX + mod.object.name,
                                type='BOOLEAN')
        new.operation = 'DIFFERENCE'
        new.object = mod.object
        try:
            new.solver = 'MANIFOLD'
        except TypeError:
            new.solver = 'EXACT'


def create(context, wall, is_back, segs, z0, thickness=DEFAULT_THICKNESS):
    """Make one backsplash on a wall and return it."""
    mesh = bpy.data.meshes.new("Backsplash")
    obj = bpy.data.objects.new("Backsplash", mesh)
    obj.parent = wall
    obj.matrix_parent_inverse.identity()
    obj[TAG] = True
    obj[RENDER_ONLY_TAG] = True
    obj['MENU_ID'] = MENU_ID
    obj['bs_side'] = 'BACK' if is_back else 'FRONT'
    obj['bs_thickness'] = float(thickness)
    obj['bs_z0'] = float(z0)
    set_segments(obj, segs)
    context.scene.collection.objects.link(obj)
    rebuild(obj)
    return obj


def existing(context, wall=None, is_back=None):
    """Backsplashes in the scene, optionally narrowed to one wall face."""
    out = []
    for obj in context.scene.objects:
        if not is_backsplash(obj):
            continue
        if wall is not None and wall_of(obj) is not wall:
            continue
        if is_back is not None:
            side = 'BACK' if is_back else 'FRONT'
            if obj.get('bs_side') != side:
                continue
        out.append(obj)
    return out
