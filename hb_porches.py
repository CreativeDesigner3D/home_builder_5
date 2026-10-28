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
from mathutils import Matrix, Vector

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


RISER_MAX = 0.1969              # 7 3/4": the most a porch step rises
STEP_TREAD = 0.2794             # 11"
STEP_GAP = 0.005                # m; posts this near a step opening's ends stay
WOOD_TREAD = 0.032              # 1 1/4" treads
WOOD_NOSING = 0.025             # 1" over the riser below
WOOD_RISER = 0.019              # 3/4" riser boards
CHEEK = 0.025                   # the boards closing wood steps' ends
SKIRT_T = 0.025
RAISED = 0.025                  # m; a ground level this far over the grid stands on it


def ground_z(level):
    """The ground's height, relative to `level`'s floor. Ground Auto: the
    grid (Z 0) when the ground level stands above it, else Ground Below
    Floor under the ground level's floor."""
    house = level.id_data.hb_house
    ground = hb_house.ground_level(house)
    base = ground.elevation if ground is not None else level.elevation
    if house.ground_auto and base > RAISED:
        return -level.elevation
    return base - house.ground_below_floor - level.elevation


def step_chains(polygon, segs, room):
    """The lines a porch's steps come off: [(points, outward normals per
    span, (s0, s1) or None)] - a set width on one edge, a whole edge, or
    each run of open edges round the porch, corner to corner."""
    if room.porch_steps <= 0:
        return []
    edges = porch_edges(polygon, segs)
    if not edges:
        return []
    out_of = lambda n: (-n[0], -n[1])
    if room.porch_steps_span == 'WRAP':
        return [(pts, normals, None) for pts, normals in _chains(edges)]
    a, b, n_in = sorted(edges, key=lambda e: -math.dist(e[0], e[1]))[min(room.porch_steps, len(edges)) - 1]
    if room.porch_steps_span == 'EDGE':
        return [([a, b], [out_of(n_in)], None)]
    length = math.dist(a, b)
    w = min(room.porch_steps_width, length)
    mid = min(max(length / 2.0 + room.porch_steps_offset, w / 2.0), length - w / 2.0)
    s0, s1 = mid - w / 2.0, mid + w / 2.0
    return [([_along(a, b, s0), _along(a, b, s1)], [out_of(n_in)], (s0, s1))]


def _chains(edges):
    """Open edges joined end to end: [(points, outward normals)]."""
    left = [(a, b, (-n[0], -n[1])) for a, b, n in edges]
    chains = []
    while left:
        a, b, n = left.pop()
        pts, normals = [a, b], [n]
        grown = True
        while grown:
            grown = False
            for i, (c, d, m) in enumerate(left):
                if math.dist(c, pts[-1]) < 0.01:
                    pts.append(d); normals.append(m)
                elif math.dist(d, pts[-1]) < 0.01:
                    pts.append(c); normals.append(m)
                elif math.dist(d, pts[0]) < 0.01:
                    pts.insert(0, c); normals.insert(0, m)
                elif math.dist(c, pts[0]) < 0.01:
                    pts.insert(0, d); normals.insert(0, m)
                else:
                    continue
                left.pop(i)
                grown = True
                break
        chains.append((pts, normals))
    return chains


def _offset(pts, normals, d):
    """A chain of points moved out by d, mitred where its spans meet."""
    out = []
    k = len(pts)
    for j in range(k):
        if j == 0:
            n = normals[0]
        elif j == k - 1:
            n = normals[-1]
        else:
            n1, n2 = normals[j - 1], normals[j]
            sx, sy = n1[0] + n2[0], n1[1] + n2[1]
            dot = 1.0 + n1[0] * n2[0] + n1[1] * n2[1]
            n = (sx / dot, sy / dot) if dot > 1e-6 else n1
        out.append((pts[j][0] + n[0] * d, pts[j][1] + n[1] * d))
    return out


def _band(bm, pts, normals, d0, d1, z0, z1, mat):
    """A solid between two offsets of a chain, z0 to z1."""
    if z1 - z0 < 1e-5 or d1 - d0 < 1e-5:
        return
    ring = _offset(pts, normals, d0) + list(reversed(_offset(pts, normals, d1)))
    bottom = [bm.verts.new((x, y, z0)) for x, y in ring]
    top = [bm.verts.new((x, y, z1)) for x, y in ring]
    start = len(bm.faces)
    try:
        bm.faces.new(bottom[::-1])
        bm.faces.new(top)
    except ValueError:
        pass
    k = len(ring)
    for i in range(k):
        j = (i + 1) % k
        try:
            bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
        except ValueError:
            pass
    bm.faces.ensure_lookup_table()
    for f in bm.faces[start:]:
        f.material_index = mat


def step_count(drop):
    """(risers, riser) for steps down `drop`: as few as keep each under
    7 3/4"; (0, 0) when there's nothing to step down."""
    if drop < 0.02:
        return 0, 0.0
    n = max(1, math.ceil(drop / RISER_MAX - 1e-6))
    return n, drop / n


def notes(room):
    """What the porch's steps come to, for its HUD group."""
    if room.porch_steps <= 0 or room.porch_obj is None:
        return []
    n = room.porch_obj.get('HB_PORCH_STEPS', 0)
    if not n:
        return ["No steps: the porch floor is on the ground"]
    return [f"Steps: {n} risers of {room.porch_obj.get('HB_PORCH_RISER', 0.0) / 0.0254:.2f}\""]


def _along(a, b, s):
    d = (b[0] - a[0], b[1] - a[1])
    L = math.hypot(*d)
    return (a[0] + d[0] * s / L, a[1] + d[1] * s / L)


def _steps(B, room, chains, floor_z, gz, mats):
    """The steps down from each chain to the ground: solid, or wood treads
    over risers with boards at the ends. Returns (risers, riser)."""
    from .hb_stair_build import _railing_along
    bm = B.bm
    n, r = step_count(floor_z - gz)
    if n == 0:
        return 0, 0.0
    T = STEP_TREAD
    top = lambda i: floor_z - (i + 1) * r          # step i's top, i = 0 the highest
    wood = room.porch_steps_style == 'WOOD'
    for pts, normals, _span in chains:
        if not wood:
            for i in range(n - 1):
                _band(bm, pts, normals, i * T, (i + 1) * T, gz, top(i), 1)
            continue
        # The riser off the porch's own edge, then each step's tread and riser
        _band(bm, pts, normals, 0.0, WOOD_RISER, top(0), floor_z, 5)
        for i in range(n - 1):
            _band(bm, pts, normals, i * T, (i + 1) * T + WOOD_NOSING, top(i) - WOOD_TREAD, top(i), 4)
            _band(bm, pts, normals, (i + 1) * T - WOOD_RISER, (i + 1) * T, top(i) - r, top(i) - WOOD_TREAD, 5)
        # Boards closing the ends, stepped to the treads
        run = (n - 1) * T
        for end, inward in ((0, 1), (len(pts) - 1, -1)):
            p = pts[end]
            nrm = normals[0] if end == 0 else normals[-1]
            q = pts[end + inward]
            L = math.dist(p, q)
            u = ((q[0] - p[0]) / L, (q[1] - p[1]) / L)
            prof = [(0.0, gz), (run + WOOD_NOSING, gz)]
            for i in range(n - 2, -1, -1):
                prof += [((i + 1) * T, top(i)), (i * T, top(i))]
            prof += [(0.0, floor_z)]
            a = [bm.verts.new((p[0] + nrm[0] * o, p[1] + nrm[1] * o, z)) for o, z in prof]
            b = [bm.verts.new((p[0] + nrm[0] * o + u[0] * CHEEK, p[1] + nrm[1] * o + u[1] * CHEEK, z))
                 for o, z in prof]
            start = len(bm.faces)
            for face in (a, b[::-1]):
                try:
                    bm.faces.new(face)
                except ValueError:
                    pass
            k = len(prof)
            for i in range(k):
                j = (i + 1) % k
                try:
                    bm.faces.new((a[i], a[j], b[j], b[i]))
                except ValueError:
                    pass
            bm.faces.ensure_lookup_table()
            for f in bm.faces[start:]:
                f.material_index = 5
    # Handrails both sides of a set-width flight of four risers or more
    if n >= 4 and room.porch_railing != 'NONE':
        from mathutils import Vector
        c = {'baluster': room.porch_railing if room.porch_railing != 'SOLID' else 'SQUARE',
             'rail_height': room.porch_rail_height}
        for pts, normals, span in chains:
            if span is None:
                continue
            pa, pb = Vector(pts[0]), Vector(pts[-1])
            out = Vector(normals[0])
            for p, s in ((pa, 1.0), (pb, -1.0)):
                start = p + (pb - pa).normalized() * 0.05 * s
                end = start + out * (n - 1) * T
                _railing_along(B, Matrix.Identity(4), start, end,
                               lambda t: floor_z - (n - 1) * r * t,
                               lambda t: floor_z - (n - 1) * r * t + room.porch_rail_height, c, mats)
    return n, r


def porch_mesh(name, polygon, segs, room, ceiling, level=None):
    """The mesh of a porch's posts, beams, risers, base, railings, steps and
    the posts under an upper one (level-relative). Material slots: 0 posts
    and railings, 1 the floor's (risers, solid steps), 2 glass, 3 its
    concrete base, 4 wood treads, 5 painted risers, boards and skirt."""
    from .hb_stair_build import _B, _railing_along
    w = room.post_width
    half = w / 2.0
    posts, beams = layout(polygon, segs, w, room.post_spacing)
    floor_z = -room.floor_drop
    beam_bottom = ceiling - room.beam_depth
    chains = step_chains(polygon, segs, room)
    # Gaps in the railing where steps come off an edge: [(a, b, s0, s1)]
    gaps = []
    for pts, normals, span in chains:
        if span is not None:
            a, b, n_in = sorted(porch_edges(polygon, segs), key=lambda e: -math.dist(e[0], e[1]))[
                min(room.porch_steps, len(porch_edges(polygon, segs))) - 1]
            gaps.append((a, b, span[0], span[1]))
        else:
            for p, q in zip(pts, pts[1:]):
                gaps.append((p, q, 0.0, math.dist(p, q)))
    # Posts in a set width of steps' way go: the beam spans the opening
    for a, b, s0, s1 in gaps:
        if s0 <= 0.0 and s1 >= math.dist(a, b) - 1e-6:
            continue                # steps the edge's length: the posts stand at their top
        L = math.dist(a, b)
        u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)

        def in_gap(p, a=a, u=u, s0=s0, s1=s1):
            rel = (p[0] - a[0], p[1] - a[1])
            t = rel[0] * u[0] + rel[1] * u[1]
            off = abs(rel[0] * u[1] - rel[1] * u[0])
            return off < w and s0 - half + STEP_GAP < t < s1 + half - STEP_GAP
        posts = [p for p in posts if not in_gap(p)]
    B = _B()
    bm = B.bm
    mats = (0, 0, 2, 0)
    I = Matrix.Identity(4)

    def box(corners, z0, z1, mat):
        start = len(bm.faces)
        _box(bm, corners, z0, z1)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[start:]:
            f.material_index = mat

    structure = room.porch_structure == 'POSTS'
    if structure:
        for x, y in posts:
            box([(x - half, y - half), (x + half, y - half), (x + half, y + half), (x - half, y + half)],
                floor_z, beam_bottom, 0)
        if room.beam_depth > 0:
            for a, b, n in beams:
                box(_strip(a, b, n, w), beam_bottom, ceiling, 0)
    if room.floor_drop > 0:
        for a, b, n, depth in risers(polygon, segs):
            box(_strip(a, b, n, depth), floor_z, 0.0, 1)
    gz = ground_z(level) if level is not None else floor_z - 0.45
    on_posts = room.porch_supports and level is not None and floor_z - gz > 0.5
    # Under the floor, down to the ground: solid, a skirt, or posts under an upper porch
    if not on_posts and floor_z - gz > 0.02 and room.porch_base != 'NONE':
        under = floor_z - 0.012
        if room.porch_base == 'SOLID':
            ring = [(x, y) for x, y in polygon]
            bottom = [bm.verts.new((x, y, gz)) for x, y in ring]
            topv = [bm.verts.new((x, y, under)) for x, y in ring]
            start = len(bm.faces)
            bm.faces.new(bottom[::-1])
            bm.faces.new(topv)
            for i in range(len(ring)):
                j = (i + 1) % len(ring)
                bm.faces.new((bottom[i], bottom[j], topv[j], topv[i]))
            bm.faces.ensure_lookup_table()
            for f in bm.faces[start:]:
                f.material_index = 3
        else:
            for a, b, n in beams:
                box(_strip(a, b, n, SKIRT_T), gz, under, 5)
    if on_posts:
        from . import hb_rooms
        slab = hb_rooms.floor_slab_thickness(level)
        under = floor_z - slab
        depth = max(room.beam_depth, 0.2)
        for a, b, n in beams:
            box(_strip(a, b, n, w), under - depth, under, 0)
        for x, y in posts:
            box([(x - half, y - half), (x + half, y - half), (x + half, y + half), (x - half, y + half)],
                gz, under - depth, 0)
    # Railings along the open edges, between the posts, not across the steps
    rail_h = room.porch_rail_height
    if room.porch_railing != 'NONE':
        c = {'baluster': room.porch_railing, 'rail_height': rail_h}
        for a, b, n in beams:
            L = math.dist(a, b)
            u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            line_a = (a[0] + n[0] * half, a[1] + n[1] * half)
            line_b = (line_a[0] + u[0] * L, line_a[1] + u[1] * L)
            ts = sorted({half, L - half} | {
                (p[0] - line_a[0]) * u[0] + (p[1] - line_a[1]) * u[1] for p in posts
                if abs((p[0] - line_a[0]) * n[0] + (p[1] - line_a[1]) * n[1]) < 0.01})
            ts = [t for t in ts if half - 1e-6 <= t <= L - half + 1e-6]
            here = [(g0, g1) for ga, gb, g0, g1 in gaps
                    if (math.dist(ga, a) < 1e-4 and math.dist(gb, b) < 1e-4)]
            here += [(L - g1, L - g0) for ga, gb, g0, g1 in gaps
                     if (math.dist(ga, b) < 1e-4 and math.dist(gb, a) < 1e-4)]
            for t0, t1 in zip(ts, ts[1:]):
                pieces = [(t0, t1)]
                for g0, g1 in here:
                    nxt = []
                    for p0, p1 in pieces:
                        if p1 <= g0 or p0 >= g1:
                            nxt.append((p0, p1))
                            continue
                        if p0 < g0:
                            nxt.append((p0, g0))
                        if p1 > g1:
                            nxt.append((g1, p1))
                    pieces = nxt
                for p0, p1 in pieces:
                    if p1 - p0 < 0.05:
                        continue
                    # its own posts where no porch post stands: ends at a
                    # step opening, or every end with no structure
                    at_gap = lambda t: any(abs(t - g) < 1e-6 for gp in here for g in gp)
                    own = (not structure or at_gap(p0), not structure or at_gap(p1))
                    pa = Vector(_along(line_a, line_b, p0))
                    pb = Vector(_along(line_a, line_b, p1))
                    _railing_along(B, I, pa, pb, lambda t: floor_z, lambda t: floor_z + rail_h, c, mats, posts=own)
    n_steps, riser = _steps(B, room, chains, floor_z, gz, mats) if chains else (0, 0.0)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh, len(posts), n_steps, riser


def _glass_material():
    from .hb_stair_build import _mat
    return _mat("HB Stair Glass", (0.85, 0.92, 0.95), 0.05, glass=True)


def build_porch(scene, level, room, polygon, segs, floor_material):
    """Make (or remake) a porch room's posts, beams, risers, base,
    railings and steps."""
    from . import hb_rooms, hb_foundation
    from .hb_stair_build import _mat
    ceiling = hb_rooms.room_height(room, level)
    mesh, _count, n_steps, riser = porch_mesh(f"Porch - {room.name}", polygon, segs, room, ceiling, level)
    post = room.post_material or _post_material()
    mesh.materials.append(post)
    mesh.materials.append(floor_material or post)
    mesh.materials.append(_glass_material())
    mesh.materials.append(hb_foundation.concrete_material())
    mesh.materials.append(_mat("HB Stair Tread", (0.52, 0.34, 0.18), 0.45))
    mesh.materials.append(post)
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
    room.porch_obj['HB_PORCH_STEPS'] = n_steps
    room.porch_obj['HB_PORCH_RISER'] = riser
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
