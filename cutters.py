"""
Cutters: the boolean shapes that cut an opening through a wall, a floor
or a ceiling.

A cutter keeps its shape the way a countertop does -- an outline of local
(x, y) corners with a local Z range, held on the object under
countertop_common's keys -- so Edit Shape reshapes one with the same
handles a top has: drag an edge or a corner, add a corner for a step or
an L, clip or round a corner (two rounded corners make an arch). The
prism is rebuilt from that outline on every change, and the host's
BOOLEAN modifier picks the new shape up on its own.

A cutter's local Z is the direction it cuts. A floor or ceiling cutter
sits square to its host, so its XY is plan. A wall cutter is turned a
quarter turn about X, so its XY is the wall face (X along the wall, Y up)
and its Z runs back through the wall. FACE_KEY is the local Z of the
surface being cut, which is where Edit Shape puts its handles.

Cutters drawn before outlines existed are a box in wall space (wall) or a
prism in plan (floor) written straight into the mesh. ensure_outline()
reads the shape back out of the mesh the first time one is edited.
"""

import math

import bmesh
import bpy
from mathutils import Matrix

from .product_libraries.common import countertop_common as ct

MENU_ID = 'HOME_BUILDER_MT_cutter_commands'

WALL = 'IS_WALL_CUTTER'
FLOOR = 'IS_FLOOR_CUTTER'
CEILING = 'IS_CEILING_CUTTER'
TAGS = (WALL, FLOOR, CEILING)
NAMES = {WALL: "Wall_Cutter", FLOOR: "Floor_Cutter", CEILING: "Ceiling_Cutter"}

FACE_KEY = 'cut_face_z'

# How far a wall cutter overshoots each face of the wall, and how far a
# floor or ceiling cutter reaches either side of the surface it cuts.
WALL_MARGIN = 0.01
SLAB_REACH = 0.1

# Wall space from a wall cutter's own: local (x, y, z) -> wall (x, -z, y),
# so the outline lies on the room face and local +Z points into the room.
WALL_BASIS = Matrix.Rotation(math.radians(90.0), 4, 'X')


def is_cutter(obj):
    return bool(obj is not None and obj.type == 'MESH'
                and obj.get('IS_CUTTING_OBJ')
                and any(obj.get(tag) for tag in TAGS))


def kind_of(obj):
    for tag in TAGS:
        if obj.get(tag):
            return tag
    return None


def face_z(obj):
    return float(obj.get(FACE_KEY, 0.0))


def host_face_z(host, kind):
    """Local Z of the surface a floor or ceiling cutter cuts: the top of
    the floor slab, the underside of the ceiling."""
    verts = getattr(getattr(host, 'data', None), 'vertices', None)
    if not verts:
        return 0.0
    zs = [v.co.z for v in verts]
    return max(zs) if kind == FLOOR else min(zs)


def rebuild(obj):
    """Rewrite the cutter's prism from its stored outline. True if built."""
    points = ct.built_outline(obj)
    if len(points) < 3:
        return False
    bottom = float(obj.get(ct.TOP_KEY, 0.0))
    depth = float(obj.get(ct.THICKNESS_KEY, 0.0))
    if depth <= 0.0:
        return False
    bm = bmesh.new()
    lower = [bm.verts.new((x, y, bottom)) for x, y in points]
    upper = [bm.verts.new((x, y, bottom + depth)) for x, y in points]
    bm.faces.new(list(reversed(lower)))
    bm.faces.new(upper)
    count = len(points)
    for i in range(count):
        j = (i + 1) % count
        bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return True


def add_boolean(host, cutter):
    mod = host.modifiers.new(name=f"Cut - {cutter.name}", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    # A ceiling is a single sheet with no inside to it; the exact solver
    # only cuts an open mesh like that cleanly when told to expect holes.
    if kind_of(cutter) == CEILING:
        mod.use_hole_tolerant = True
    return mod


def _anticlockwise(points):
    points = [(float(x), float(y)) for x, y in points]
    return points if ct.signed_area(points) >= 0.0 else points[::-1]


def create(context, host, kind, points, bottom, depth, face):
    """Make a cutter on ``host`` from an outline in the cutter's own
    space, hook up its boolean, and return it."""
    name = NAMES[kind]
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    obj.parent = host
    obj.matrix_parent_inverse.identity()
    if kind == WALL:
        obj.matrix_basis = WALL_BASIS
    obj['IS_CUTTING_OBJ'] = True
    obj[kind] = True
    obj['MENU_ID'] = MENU_ID
    obj[ct.TOP_KEY] = float(bottom)
    obj[ct.THICKNESS_KEY] = float(depth)
    obj[FACE_KEY] = float(face)
    ct.set_outline(obj, _anticlockwise(points))
    obj.display_type = 'WIRE'
    obj.hide_render = True
    if not rebuild(obj):
        # Two clicks on one spot: nothing to cut with.
        remove(obj)
        return None
    add_boolean(host, obj)
    return obj


def create_wall_cutter(context, wall, thickness, x0, z0, x1, z1):
    """A rectangle on the wall's room face, x along the wall, z up."""
    points = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    return create(context, wall, WALL, points,
                  -(thickness + WALL_MARGIN), thickness + 2.0 * WALL_MARGIN,
                  0.0)


def create_slab_cutter(context, host, kind, points):
    """A plan outline cut through a floor or a ceiling, points in the
    host's local XY."""
    face = host_face_z(host, kind)
    return create(context, host, kind, points,
                  face - SLAB_REACH, 2.0 * SLAB_REACH, face)


def ensure_outline(obj):
    """Give a cutter from before outlines existed its outline. True when
    one is there.

    The old cutter's corners are read in its parent's space, then the
    object is reset to the frame a new cutter of its kind would have, so
    the prism rebuilt from the outline lands exactly where the old mesh
    was.
    """
    if ct.has_outline(obj):
        return True
    kind = kind_of(obj)
    verts = obj.data.vertices
    if kind is None or len(verts) < 6:
        return False
    to_parent = obj.matrix_parent_inverse @ obj.matrix_basis
    pts = [to_parent @ v.co for v in verts]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]

    if kind == WALL:
        # A box: X along the wall, Z up, Y through it.
        outline = [(min(xs), min(zs)), (max(xs), min(zs)),
                   (max(xs), max(zs)), (min(xs), max(zs))]
        bottom, depth, face = -max(ys), max(ys) - min(ys), 0.0
        basis = WALL_BASIS
    else:
        # A prism: the drawn polygon is the first half of the verts.
        half = len(pts) // 2
        outline = [(p.x, p.y) for p in pts[:half]]
        if len(pts) % 2 or not ct.is_simple(outline):
            outline = [(min(xs), min(ys)), (max(xs), min(ys)),
                       (max(xs), max(ys)), (min(xs), max(ys))]
        bottom, depth = min(zs), max(zs) - min(zs)
        face = (host_face_z(obj.parent, kind) if obj.parent is not None
                else (bottom + depth / 2.0))
        basis = Matrix.Identity(4)
    if depth <= 0.0:
        return False

    obj.matrix_parent_inverse.identity()
    obj.matrix_basis = basis
    obj[ct.TOP_KEY] = float(bottom)
    obj[ct.THICKNESS_KEY] = float(depth)
    obj[FACE_KEY] = float(face)
    obj['MENU_ID'] = MENU_ID
    ct.set_outline(obj, _anticlockwise(outline))
    return rebuild(obj)


def hosts_of(obj):
    """Every object with a boolean cutting by ``obj``."""
    out = []
    for other in bpy.data.objects:
        for mod in other.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == obj:
                out.append((other, mod))
    return out


def remove(obj):
    """Delete a cutter and the booleans it drove, so the host is whole
    again rather than left carrying an empty modifier."""
    for other, mod in hosts_of(obj):
        other.modifiers.remove(mod)
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
