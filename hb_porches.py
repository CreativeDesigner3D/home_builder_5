"""
Porches.

A porch is a room closed on its open sides by Porch Edge walls: lines
that build nothing themselves (like room dividers) but mark where the
porch's posts and beam go. hb_rooms finds the porch as a room, builds its
floor a step down and its ceiling at the porch's own height; this module
builds the rest - one object per porch holding:

  - posts along each porch edge, no further apart than the porch's post
    spacing, with one at every free end and corner (none where an edge
    meets the house: the beam bears on the wall there),
  - a beam along each edge under the ceiling, carried on the posts,
  - a riser under each house wall the porch steps down from, so the step
    reads as solid rather than a slot under the wall.

Posts and beam sit inside the edge line, so their outer faces are flush
with it. Sizes come from the room (post width, spacing, beam depth, step
down). Geometry is level-relative, like the floors.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from . import hb_house, hb_wall_graph

PORCH_WALL = 'Porch'
POST_MATERIAL = "Porch Post"
POST_COLOR = (0.92, 0.91, 0.88, 1.0)
WALL_REACH = 0.25               # m; an edge end this near a wall bears on it
ON_EDGE = 0.01                  # m


def is_porch_area(area):
    return PORCH_WALL in area.wall_types


# ---- Layout (plain tuples, no bpy) -------------------------------------------

def _dist_to_band(pt, seg):
    """Distance in plan from pt to a wall's footprint (its reference line
    swept across its thickness)."""
    rel = hb_wall_graph._sub(pt, seg.start)
    t = hb_wall_graph._dot(rel, seg.dir)
    w = hb_wall_graph._dot(rel, seg.normal)
    dt = max(0.0, -t, t - seg.length)
    dw = max(0.0, -w, w - seg.thickness)
    return math.hypot(dt, dw)


def _on_polygon(pt, poly):
    return hb_wall_graph._dist_to_edges(pt, poly) < ON_EDGE


def porch_edges(polygon, segs):
    """The porch edge segments round a porch's outline, each as
    (start, end, inward normal)."""
    out = []
    for s in segs:
        if s.wall_type != PORCH_WALL or s.length < 1e-6:
            continue
        mid = hb_wall_graph._mul(hb_wall_graph._add(s.start, s.end), 0.5)
        if not _on_polygon(mid, polygon):
            continue
        n = s.normal
        probe = hb_wall_graph._add(mid, hb_wall_graph._mul(n, 0.05))
        if not hb_wall_graph.point_in_polygon(probe, polygon):
            n = hb_wall_graph._mul(n, -1.0)
        out.append((s.start, s.end, n))
    return out


def layout(polygon, segs, post_width, spacing):
    """(posts, beams): post centres [(x, y)], and beams as
    (start, end, inward normal) - the edge lines, posts and beam sitting
    on their inward side."""
    walls = [s for s in segs if s.wall_type not in hb_wall_graph.ROOM_ONLY_WALLS
             and s.wall_type not in hb_wall_graph.NOT_ROOM_WALLS]
    edges = porch_edges(polygon, segs)
    half = post_width / 2.0

    def at_wall(p):
        return any(_dist_to_band(p, w) < WALL_REACH for w in walls)

    posts = []

    def add(p):
        if all(math.dist(p, q) > 0.01 for q in posts):
            posts.append(p)

    for a, b, n in edges:
        d = hb_wall_graph._sub(b, a)
        length = hb_wall_graph._len(d)
        d = hb_wall_graph._mul(d, 1.0 / length)
        bays = max(1, math.ceil(length / max(spacing, post_width * 2) - 1e-6))
        for i in range(bays + 1):
            if i == 0 and at_wall(a):
                continue
            if i == bays and at_wall(b):
                continue
            along = length * i / bays
            # End posts tuck inside the edge, so a corner post is shared
            along = min(max(along, half), length - half)
            p = hb_wall_graph._add(a, hb_wall_graph._mul(d, along))
            add(hb_wall_graph._add(p, hb_wall_graph._mul(n, half)))
    return posts, edges


def risers(polygon, segs):
    """Strips under the house walls a porch steps down from: (a, b, outward
    normal, depth) for each stretch of the porch's outline along a built
    wall, reaching to the middle of that wall."""
    walls = [s for s in segs if s.wall_type not in hb_wall_graph.ROOM_ONLY_WALLS
             and s.wall_type not in hb_wall_graph.NOT_ROOM_WALLS]
    out = []
    n_pts = len(polygon)
    for i in range(n_pts):
        a, b = polygon[i], polygon[(i + 1) % n_pts]
        d = hb_wall_graph._sub(b, a)
        length = hb_wall_graph._len(d)
        if length < 1e-6:
            continue
        mid = hb_wall_graph._mul(hb_wall_graph._add(a, b), 0.5)
        host = next((w for w in walls if _dist_to_band(mid, w) < ON_EDGE), None)
        if host is None:
            continue
        n = hb_wall_graph._left(hb_wall_graph._mul(d, 1.0 / length))
        probe = hb_wall_graph._add(mid, hb_wall_graph._mul(n, 0.05))
        if hb_wall_graph.point_in_polygon(probe, polygon):
            n = hb_wall_graph._mul(n, -1.0)
        out.append((a, b, n, host.thickness / 2.0))
    return out


# ---- Building ------------------------------------------------------------------

def _box(bm, corners_2d, z0, z1):
    """A prism over a 4-point plan outline from z0 to z1."""
    bottom = [bm.verts.new((x, y, z0)) for x, y in corners_2d]
    top = [bm.verts.new((x, y, z1)) for x, y in corners_2d]
    bm.faces.new(bottom[::-1])
    bm.faces.new(top)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))


def _strip(a, b, n, width):
    """Plan outline of a strip `width` wide from line a-b towards n."""
    off = (n[0] * width, n[1] * width)
    return [a, b, (b[0] + off[0], b[1] + off[1]), (a[0] + off[0], a[1] + off[1])]


def _post_material():
    mat = bpy.data.materials.get(POST_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(POST_MATERIAL)
        mat.diffuse_color = POST_COLOR
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = POST_COLOR
            bsdf.inputs["Roughness"].default_value = 0.5
    return mat


def porch_mesh(name, polygon, segs, room, ceiling):
    """The mesh of a porch's posts, beams and risers (level-relative)."""
    w = room.post_width
    posts, beams = layout(polygon, segs, w, room.post_spacing)
    floor_z = -room.floor_drop
    beam_bottom = ceiling - room.beam_depth
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for x, y in posts:
        h = w / 2.0
        _box(bm, [(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h)],
             floor_z, beam_bottom)
    if room.beam_depth > 0:
        for a, b, n in beams:
            _box(bm, _strip(a, b, n, w), beam_bottom, ceiling)
    post_faces = len(bm.faces)
    if room.floor_drop > 0:
        for a, b, n, depth in risers(polygon, segs):
            _box(bm, _strip(a, b, n, depth), floor_z, 0.0)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()
    for i, f in enumerate(bm.faces):
        f.material_index = 0 if i < post_faces else 1
    bm.to_mesh(mesh)
    bm.free()
    return mesh, len(posts)


def build_porch(scene, level, room, polygon, segs, floor_material):
    """Make (or remake) a porch room's posts, beams and risers."""
    from . import hb_rooms
    ceiling = hb_rooms.room_height(room, level)
    mesh, _count = porch_mesh(f"Porch - {room.name}", polygon, segs, room, ceiling)
    mesh.materials.append(room.post_material or _post_material())
    mesh.materials.append(floor_material or room.post_material or _post_material())
    if room.porch_obj is None:
        room.porch_obj = hb_rooms._generated(scene, level, room, f"Porch - {room.name}",
                                             mesh, ('IS_PORCH_BP',))
    else:
        old = room.porch_obj.data
        room.porch_obj.data = mesh
        room.porch_obj.name = f"Porch - {room.name}"
        if old is not None and old.users == 0:
            bpy.data.meshes.remove(old)
    room.porch_obj.location = (0.0, 0.0, level.elevation)
    from . import hb_roofs
    hb_roofs.build_porch_roof(scene, level, room, polygon, segs)


def remove_porch(room):
    from . import hb_rooms, hb_roofs
    hb_rooms._remove(room.porch_obj)
    room.porch_obj = None
    hb_roofs.remove_porch_roof(room)


# ---- The porch's own roof -------------------------------------------------------

def shed_plan(polygon, segs):
    """How a shed roof lies over a porch: (origin, along, up_slope, s0,
    s1, depth) - the porch's longest open edge is the low side, `along`
    runs down it from `origin`, `up_slope` points in towards the house,
    s0..s1 is the porch's extent along it and `depth` how far it reaches
    back. None for a porch with no open edge."""
    edges = porch_edges(polygon, segs)
    if not edges:
        return None
    a, b, n_in = max(edges, key=lambda e: math.dist(e[0], e[1]))
    d = hb_wall_graph._sub(b, a)
    e = hb_wall_graph._mul(d, 1.0 / hb_wall_graph._len(d))
    ss = [hb_wall_graph._dot(hb_wall_graph._sub(p, a), e) for p in polygon]
    ds = [hb_wall_graph._dot(hb_wall_graph._sub(p, a), n_in) for p in polygon]
    return a, e, n_in, min(ss), max(ss), max(ds)
