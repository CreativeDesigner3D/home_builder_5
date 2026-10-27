"""Framing: the studs, joists and rafters inside a house's simple shapes.

The house is modelled as plain solids - a wall is a box, a floor a slab,
a roof a shell - which is what is wanted while laying it out. Show
Framing (on the house) builds the framing those solids stand for, and
ghosts the solids so it can be seen:

* Walls: a bottom plate, a double top plate and studs on centres from
  the wall's start, sized from the wall's thickness (2x6 in a 6" wall,
  2x4 in a 4 1/2" one). At each door and window: king and jack studs, a
  header sized to the opening, and for a window a sill with cripples
  above and below; a door's opening takes out the bottom plate. A wall
  that runs up under a roof (a gable end) stops its studs at the roof's
  underside; one that stops at the eaves under a cross gable's filled-in
  end gets gable studs up to the roof.
* Floors: joists across each room's short way, with a rim round it, in
  the upper levels' floor depth - and on the ground level when it is
  framed over a crawlspace rather than a slab.
* Ceilings: joists over a flat ceiling with nothing built above it,
  sized from the span, in a rim - their tops cut to the roof's slope
  where it comes down over them at the eaves.
* Roofs: rafters down every sloped face of the roofs (so a hip's ends
  get their jacks and a dormer its own), inside the roof's thickness -
  the roof is drawn as thick as its rafters and sheathing, its underside
  on the plates at the eaves - and a board along every crease between
  two faces: ridges, hips and valleys. Where a cross gable meets the
  roof, the roof gets valley rafters and the gable's rafters land on
  flat valley boards laid on it.

Each level's framing is one object in its Framing collection, rebuilt
while the switch is on whenever the rooms or the roof are, and removed
when it is turned off. Nothing here changes the house: the ghosting is
the solids' viewport display, put back as it was.
"""

import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import hb_house, hb_types, hb_wall_graph
from .units import inch

FRAMING_KEY = 'IS_FRAMING'
GHOST_KEY = 'HB_FRAMING_DISPLAY'    # a solid's display before it was ghosted
PART = 'Framing'                    # the level sub-collection
MATERIAL = "HB Framing Lumber"
LUMBER_COLOR = (0.78, 0.62, 0.42, 1.0)

T = inch(1.5)               # a board's thickness
SUBFLOOR = inch(0.75)       # floor sheathing over the joists
SHEATHING = inch(0.5)       # roof sheathing over the rafters
RAFTER_DEPTH = inch(7.25)   # 2x8
GROUND_JOIST = inch(9.25)   # 2x10 over a crawlspace
FRAMED_WALLS = ('Exterior', 'Interior', 'Half', 'Dormer')


# =============================================================================
# SIZES
# =============================================================================

def stud_depth(thickness):
    """A wall's studs: 2x6 in a wall 5 1/2" thick or more, else 2x4 (or
    as deep as a thinner wall)."""
    if thickness >= inch(5.5) - 1e-4:
        return inch(5.5)
    return min(inch(3.5), thickness)


def header_depth(width):
    """A header over an opening this wide: 2x6, 2x10 or 2x12."""
    if width <= inch(36) + 1e-4:
        return inch(5.5)
    if width <= inch(72) + 1e-4:
        return inch(9.25)
    return inch(11.25)


def joist_depth(span):
    """Ceiling joists for a span: 2x6 to 12', 2x8 to 16', then 2x10."""
    if span <= 12 * 0.3048:
        return inch(5.5)
    if span <= 16 * 0.3048:
        return inch(7.25)
    return inch(9.25)


def spacing(house):
    return inch(24) if house.framing_spacing == '24' else inch(16)


# =============================================================================
# BUILDING BLOCKS
# =============================================================================

class Boards:
    """Boxes collected into one bmesh."""

    def __init__(self):
        self.bm = bmesh.new()
        self.count = 0

    def box(self, corners):
        """A board from its 8 corners: bottom 4 then top 4, each in order
        round the face."""
        v = [self.bm.verts.new(c) for c in corners]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                  (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.bm.faces.new([v[i] for i in f])
        self.count += 1

    def local_box(self, m, x0, x1, y0, y1, z0, z1, z1_end=None):
        """An axis-aligned board in a wall's own space (m its matrix); the
        top may slope from z1 at x0 to z1_end at x1."""
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        ze = z1 if z1_end is None else z1_end
        pts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
               (x0, y0, z1), (x1, y0, ze), (x1, y1, ze), (x0, y1, z1)]
        self.box([m @ Vector(p) for p in pts])

    def run(self, a, b, z_top, width, depth):
        """A level board from plan point a to b, `width` across, its top
        at z_top and `depth` deep."""
        a, b = Vector((a[0], a[1])), Vector((b[0], b[1]))
        d = b - a
        if d.length < 1e-4:
            return
        side = Vector((-d.y, d.x)).normalized() * (width / 2.0)
        z0 = z_top - depth
        quad = [a - side, b - side, b + side, a + side]
        self.box([Vector((p.x, p.y, z0)) for p in quad]
                 + [Vector((p.x, p.y, z_top)) for p in quad])

    def mesh(self, name):
        mesh = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(mesh)
        self.bm.free()
        return mesh


def scan(polygon, axis, step, offset=0.0, margin=T / 2.0):
    """Lines across a plan polygon: for each position k * step + offset
    along `axis` (a unit 2D vector), the spans of the line through it
    (running across `axis`) inside the polygon, as point pairs. None
    closer than `margin` to the polygon's ends along `axis`."""
    ax = Vector(axis).normalized()
    across = Vector((-ax.y, ax.x))
    pts = [Vector(p) for p in polygon]
    a_vals = [p.dot(ax) for p in pts]
    lo, hi = min(a_vals), max(a_vals)
    out = []
    k = math.ceil((lo - offset) / step)
    while k * step + offset < hi:
        a = k * step + offset
        k += 1
        if a - lo < margin or hi - a < margin:
            continue
        hits = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            pa, qa = p.dot(ax), q.dot(ax)
            if (pa <= a < qa) or (qa <= a < pa):
                t = (a - pa) / (qa - pa)
                hits.append((p + (q - p) * t).dot(across))
        hits.sort()
        for j in range(0, len(hits) - 1, 2):
            b0, b1 = hits[j], hits[j + 1]
            if b1 - b0 > T:
                out.append((ax * a + across * b0, ax * a + across * b1))
    return out


def short_axis(polygon):
    """(axis joists are spaced along, span across): joists run the short
    way, so they are spaced along the long side."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if w >= h:
        return (1.0, 0.0), h
    return (0.0, 1.0), w


# =============================================================================
# WALLS
# =============================================================================

def _openings(wall_obj):
    """(x0, x1, z0, z1, is_door) for each door and window in a wall, in
    its own space."""
    out = []
    for child in wall_obj.children:
        door = bool(child.get('IS_ENTRY_DOOR_BP'))
        if not (door or child.get('IS_WINDOW_BP')):
            continue
        cage = hb_types.GeoNodeCage(child)
        if not cage.has_modifier():
            continue
        x0, z0 = child.location.x, child.location.z
        out.append((x0, x0 + cage.get_input('Dim X'), z0, z0 + cage.get_input('Dim Z'), door))
    return sorted(out)


def _roof_tree(scene, depsgraph, level):
    """A BVH of a level's own roof and dormer roofs, for its walls that
    run up under them (gable ends, dormer fronts). Only its own: a lower
    level's roof can slope up against an upper level's walls, as a porch
    roof does against the house, and neither may cut them."""
    from . import hb_roofs
    return hb_roofs.roof_bvh(scene, depsgraph, [level], porches=False)


def _roof_above(tree, m, x, y, z0, top):
    """The wall's top at (x, y) in its own space: `top`, or lower where
    a roof's underside comes down below it."""
    if tree is None:
        return top
    start = m @ Vector((x, y, z0 + 0.05))
    hit, _n, _i, dist = tree.ray_cast(start, Vector((0.0, 0.0, 1.0)), top - z0 + 1.0)
    if hit is None:
        return top
    local = m.inverted() @ hit
    return min(top, local.z - 0.005)


def _gable_tree(scene, depsgraph, level):
    """A BVH of a level's filled-in gable ends (cross gables, shed dormer
    walls): closed shapes standing on walls that stop at the eaves."""
    verts, polys = [], []
    for obj in (level.roof.gables_obj, level.roof.dormer_walls_obj):
        if obj is None or obj.type != 'MESH' or obj.name not in scene.objects:
            continue
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        m = obj.matrix_world
        base = len(verts)
        verts.extend(m @ v.co for v in mesh.vertices)
        polys.extend([base + i for i in p.vertices] for p in mesh.polygons)
        ev.to_mesh_clear()
    if not polys:
        return None
    return BVHTree.FromPolygons(verts, polys)


def _gable_above(gables, m, x, y, z):
    """The top of a filled-in gable standing on a wall at (x, y), in the
    wall's space, or None where there is none."""
    if gables is None:
        return None
    start = m @ Vector((x, y, z + 0.01))
    hit, n, _i, _d = gables.ray_cast(start, Vector((0.0, 0.0, 1.0)), 30.0)
    if hit is None or n.z <= 0.0:
        return None             # above the shape, or it is not on this wall
    return (m.inverted() @ hit).z


def frame_wall(boards, wall_obj, step, tree=None, gables=None):
    """Plates, studs and opening framing for one wall."""
    from .operators import walls as hb_walls
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return
    length = wall.get_input('Length')
    t = wall.get_input('Thickness')
    height = wall.get_input('Height')
    end_h = wall.get_input('End Height') if wall.has_input('End Height') else 0.0
    if length < 0.05 or height < 0.3:
        return
    ext = hb_walls.wall_face_extents(wall_obj)
    if ext is not None:
        x0 = (ext['back'][0] + ext['front'][0]) / 2.0
        x1 = (ext['back'][1] + ext['front'][1]) / 2.0
    else:
        x0, x1 = 0.0, length
    d = stud_depth(t)
    y0 = (t - d) / 2.0
    y1 = y0 + d
    ymid = t / 2.0
    m = wall_obj.matrix_world

    def top(x):
        h = height if end_h <= 0.0 else height + (end_h - height) * (x / max(length, 1e-6))
        return _roof_above(tree, m, x, ymid, 0.0, h)

    half = wall_obj.get('WALL_TYPE') == 'Half'
    plates = T if half else 2 * T
    openings = _openings(wall_obj)

    # Bottom plate, broken at doors
    runs = [(x0, x1)]
    for ox0, ox1, _z0, _z1, door in openings:
        if not door:
            continue
        cut = []
        for a, b in runs:
            if ox1 <= a or ox0 >= b:
                cut.append((a, b))
                continue
            if ox0 > a:
                cut.append((a, ox0))
            if ox1 < b:
                cut.append((ox1, b))
        runs = cut
    for a, b in runs:
        boards.local_box(m, a, b, y0, y1, 0.0, T)

    # Top plates, following the top: one board per layer along each
    # straight stretch, in steps only where a roof bends it
    marks = sorted({x0, x1} | {min(max(x0 + k * step, x0), x1)
                               for k in range(1, int((x1 - x0) / step) + 1)})
    tops = [top(x) for x in marks]
    pieces = []
    for i in range(len(marks) - 1):
        a, b, ta, tb = marks[i], marks[i + 1], tops[i], tops[i + 1]
        if pieces:
            pa, _pb, pta, _ptb = pieces[-1]
            slope = (tb - ta) / max(b - a, 1e-6)
            if abs(pta + slope * (a - pa) - ta) < 1e-4 and abs(
                    (ta - pta) / max(a - pa, 1e-6) - slope) < 1e-4:
                pieces[-1] = (pa, b, pta, tb)
                continue
        pieces.append((a, b, ta, tb))
    for a, b, ta, tb in pieces:
        for k in range(int(round(plates / T))):
            lo = k * T - plates
            boards.local_box(m, a, b, y0, y1, min(ta, tb) + lo, ta + lo + T, tb + lo + T)

    def stud(xa, z_lo, z_hi=None):
        z_hi = top(xa + T / 2.0) - plates if z_hi is None else z_hi
        boards.local_box(m, xa, xa + T, y0, y1, z_lo, z_hi)

    # Openings: kings, jacks, header, sill and cripples
    taken = []
    for ox0, ox1, oz0, oz1, door in openings:
        hd = header_depth(ox1 - ox0)
        head_top = min(oz1 + hd, top((ox0 + ox1) / 2.0) - plates)
        for xa in (ox0 - 2 * T, ox1 + T):
            stud(xa, T)
        for xa in (ox0 - T, ox1):
            stud(xa, T, oz1)
        boards.local_box(m, ox0 - T, ox1 + T, y0, y1, oz1, head_top)
        if not door and oz0 > 2 * T:
            boards.local_box(m, ox0, ox1, y0, y1, oz0 - T, oz0)
        taken.append((ox0 - 2 * T, ox1 + 2 * T, ox0, ox1, oz0, head_top, door))

    # Studs on centres from the start, the end stud, and cripples
    xs = [x0] + [x0 + k * step - T / 2.0 for k in range(1, int((x1 - x0) / step) + 1)]
    xs = [x for x in xs if x + T <= x1 - T] + [x1 - T]
    for xa in xs:
        hit = next((o for o in taken if o[0] - 1e-4 < xa + T and xa < o[1] + 1e-4), None)
        if hit is None:
            stud(xa, T)
            continue
        _a, _b, ox0, ox1, oz0, head_top, door = hit
        if not (ox0 <= xa and xa + T <= ox1):
            continue
        z_hi = top(xa + T / 2.0) - plates
        if z_hi - head_top > 0.02:
            stud(xa, head_top, z_hi)
        if not door and oz0 - T - T > 0.02:
            stud(xa, T, oz0 - T)

    # Gable studs on the plates, up to a filled-in gable's slope
    if gables is not None:
        for xa in xs:
            za = _gable_above(gables, m, xa, ymid, top(xa))
            zb = _gable_above(gables, m, xa + T, ymid, top(xa + T))
            if za is None or zb is None:
                continue
            z0 = max(top(xa), top(xa + T))
            if min(za, zb) - z0 > 0.05:
                boards.local_box(m, xa, xa + T, y0, y1, z0, za, zb)


# =============================================================================
# FLOORS AND CEILINGS
# =============================================================================

def _room_areas(scene, level):
    """The level's rooms (porches left out), as found from its walls."""
    from . import hb_porches
    from .operators import walls as hb_walls
    _objs, segs = hb_walls.level_wall_segs(scene, level.uid)
    return [a for a in hb_wall_graph.find_rooms(segs) if not hb_porches.is_porch_area(a)]


def _ceiling_run(boards, tree, a, b, z_top, depth):
    """A level board from plan point a to b (as Boards.run) under a roof
    (`tree`): its top cut down to the roof's underside where that comes
    lower - as a ceiling joist's end is cut to the slope, so the rafters
    pass over it - and none of it where the roof comes down below the
    board altogether."""
    if tree is None:
        boards.run(a, b, z_top, T, depth)
        return
    z0 = z_top - depth
    steps = max(1, int((b - a).length / 0.05))
    tops = []
    for k in range(steps + 1):
        p = a + (b - a) * (k / steps)
        if tree.ray_cast(Vector((p.x, p.y, z0 - 0.005)), Vector((0.0, 0.0, -1.0)), 3.0)[0] is not None:
            tops.append(None)                   # the roof is below it here
            continue
        hit = tree.ray_cast(Vector((p.x, p.y, z0 + 0.005)), Vector((0.0, 0.0, 1.0)), depth)
        z = z_top if hit[0] is None else hit[0].z - 0.005
        tops.append(z if z - z0 > 0.02 else None)
    # Pieces between samples, joined where they run on in a straight line
    d = b - a
    side = Vector((-d.y, d.x, 0.0)).normalized() * (T / 2.0)
    piece = None            # [start, end, start top, end top, length]
    for k in range(steps):
        ta, tb = tops[k], tops[k + 1]
        if ta is None or tb is None:
            if piece is not None:
                _emit(boards, piece, side, z0)
            piece = None
            continue
        pa = a + d * (k / steps)
        pb = a + d * ((k + 1) / steps)
        if piece is not None:
            run = (pb - piece[0]).length
            on_line = piece[2] + (piece[3] - piece[2]) * run / max(piece[4], 1e-9)
            if abs(on_line - tb) < 0.002 and abs(piece[3] - ta) < 1e-6:
                piece[1], piece[3], piece[4] = pb, tb, run
                continue
            _emit(boards, piece, side, z0)
        piece = [pa, pb, ta, tb, (pb - pa).length]
    if piece is not None:
        _emit(boards, piece, side, z0)


def _emit(boards, piece, side, z0):
    pa, pb, ta, tb, _length = piece
    pa = Vector((pa.x, pa.y, 0.0))
    pb = Vector((pb.x, pb.y, 0.0))
    quad = [pa - side, pb - side, pb + side, pa + side]
    z_tops = (ta, tb, tb, ta)
    boards.box([Vector((q.x, q.y, z0)) for q in quad]
               + [Vector((q.x, q.y, z)) for q, z in zip(quad, z_tops)])


def _grown(cell, by):
    """A 4-point cell polygon grown by `by` on every side."""
    p0, p1, _p2, p3 = (Vector(p) for p in cell)
    u = (p1 - p0).normalized()
    v = (p3 - p0).normalized()
    w, h = (p1 - p0).length, (p3 - p0).length
    o = p0 - (u + v) * by
    return [tuple(o), tuple(o + u * (w + 2 * by)),
            tuple(o + u * (w + 2 * by) + v * (h + 2 * by)), tuple(o + v * (h + 2 * by))]


def _frame_opening(boards, polygon, z_top, depth, edges, joist_dir):
    """Double trimmers along an opening's sides that run with the joists,
    from rim to rim, and double headers across its ends between them."""
    from . import hb_structure_geom as geom
    jd = Vector(joist_dir).normalized()
    for a, b, n in edges:
        a, b, n = Vector(a), Vector(b), Vector(n).normalized()
        d = b - a
        if d.length < T:
            continue
        u = d.normalized()
        for k in (0.5, 1.5):
            off = n * (T * k)
            if abs(u.dot(jd)) > 0.7:
                # A trimmer: the whole joist line beside the opening
                p, q = a + off - u * 100.0, b + off + u * 100.0
                mid = (a + b) / 2.0 + off
                for t0, t1 in geom.segment_in_polygon_spans(tuple(p), tuple(q), polygon):
                    s, e = p + (q - p) * t0, p + (q - p) * t1
                    if (mid - s).dot(u) >= 0 and (e - mid).dot(u) >= 0 and (e - s).length > 2.5 * T:
                        _ceiling_run(boards, None, s + u * T, e - u * T, z_top, depth)
            else:
                # A header: across the end, out to the outer trimmers
                _ceiling_run(boards, None, a + off - u * 2 * T, b + off + u * 2 * T,
                             z_top, depth)


def frame_floor(boards, polygon, z_top, depth, step, tree=None, openings=()):
    """Joists across a room the short way, between a rim round it - cut
    down under `tree` (a roof) where it comes low (see _ceiling_run), and
    headed off round `openings` (stairwells: [(cells, edges)] in world XY,
    see hb_rooms.stairwell_openings)."""
    from . import hb_structure_geom as geom
    axis, _span = short_axis(polygon)
    # Joists stop at an opening's headers and give way to its trimmers
    holes = [_grown(cell, 2 * T) for cells, _edges in openings for cell in cells]
    joist_dir = None
    for a, b in scan(polygon, axis, step, margin=1.5 * T):
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized() * T
        if joist_dir is None:
            joist_dir = b - a
        if (b - a).length <= 2.5 * T:
            continue
        a, b = a + d, b - d
        spans = [(0.0, 1.0)]
        for hole in holes:
            cut = geom.segment_in_polygon_spans(tuple(a), tuple(b), hole)
            spans = [piece for s in spans for piece in geom.subtract_intervals(s, cut)]
        for t0, t1 in spans:
            p, q = a + (b - a) * t0, a + (b - a) * t1
            if (q - p).length > 2.5 * T:
                _ceiling_run(boards, tree, p, q, z_top, depth)
    if joist_dir is not None:
        for cells, edges in openings:
            if any(geom._inside(tuple((Vector(c[0]) + Vector(c[2])) / 2.0), polygon) for c in cells):
                _frame_opening(boards, polygon, z_top, depth, edges, joist_dir)
    n = len(polygon)
    for i in range(n):
        p, q = Vector(polygon[i]), Vector(polygon[(i + 1) % n])
        d = q - p
        if d.length < T:
            continue
        inward = Vector((-d.y, d.x)).normalized() * (T / 2.0)
        if hb_wall_graph.polygon_area(polygon) < 0:
            inward = -inward
        _ceiling_run(boards, tree, p + inward, q + inward, z_top, depth)


def ground_framed(house):
    """Whether the ground level's floor is framed: over a crawlspace or a
    basement, and not on a slab; with no foundation drawn, as the house's
    Ground Floor setting says."""
    if house.foundation_type in ('CRAWL', 'BASEMENT'):
        return True
    if house.foundation_type == 'SLAB':
        return False
    return house.ground_floor == 'CRAWL'


def frame_level_floor(boards, scene, level, step):
    house = scene.hb_house
    if level.kind == 'FOUNDATION':
        return                      # a slab or bare ground
    below = hb_house.level_below(house, level)
    if below is None or below.kind == 'FOUNDATION':
        if not ground_framed(house):
            return
        depth = GROUND_JOIST
    else:
        depth = min(max(level.floor_thickness - SUBFLOOR, inch(5.5)), inch(11.25))
    z_top = level.elevation - SUBFLOOR
    from . import hb_rooms
    openings = hb_rooms.stairwell_openings(scene, level)
    for area in _room_areas(scene, level):
        frame_floor(boards, area.polygon, z_top, depth, step, openings=openings)


def _covered(scene, level, point):
    """Whether a level above has a room over this plan point."""
    house = scene.hb_house
    for upper in house.levels:
        if upper.elevation <= level.elevation + 1e-6:
            continue
        if any(hb_wall_graph.point_in_polygon(point, a.polygon) for a in _room_areas(scene, upper)):
            return True
    return False


def frame_level_ceilings(boards, scene, level, step, tree=None):
    from . import hb_rooms
    areas = _room_areas(scene, level)
    for room in level.rooms:
        if room.orphaned or not room.has_ceiling or room.ceiling_style != 'FLAT':
            continue
        if room.marker is None:
            continue
        p = (room.marker.location.x, room.marker.location.y)
        area = next((a for a in areas if hb_wall_graph.point_in_polygon(p, a.polygon)), None)
        if area is None or _covered(scene, level, p):
            continue
        _axis, span = short_axis(area.polygon)
        depth = joist_depth(span)
        z_bottom = level.elevation + hb_rooms.room_height(room, level)
        frame_floor(boards, area.polygon, z_bottom + depth, depth, step, tree)


# =============================================================================
# ROOFS
# =============================================================================

def frame_roof(boards, obj, depsgraph, step, depth=RAFTER_DEPTH, sits_on=False):
    """Rafters up from every sloped underside face of a roof, inside its
    thickness, and a board along each crease between two of them (ridges,
    hips, valleys). Where the roof is cut to meet another: a valley rafter
    under the cut, or - for a roof that `sits_on` another (a cross gable,
    a porch) - a flat valley board on that roof for its rafters to land on."""
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    m = obj.matrix_world
    rot = m.to_3x3()
    shell = BVHTree.FromPolygons([m @ v.co for v in mesh.vertices],
                                 [list(p.vertices) for p in mesh.polygons])
    # Points inside each face, to look up from: a face's centre can fall
    # outside it where it is notched (where a cross gable meets it)
    mesh.calc_loop_triangles()
    inside = {}
    for tri in mesh.loop_triangles:
        inside.setdefault(tri.polygon_index, []).append((tri.area, m @ tri.center))
    faces = []
    cuts = {}               # the downward faces cut through the thickness
    for poly in mesh.polygons:
        n = (rot @ poly.normal).normalized()
        if not (-0.985 < n.z < -0.08):
            continue                    # only the sloped undersides
        # A true underside has the roof's top over it, parallel, a roof's
        # thickness away. The other downward faces are cuts through the
        # thickness - the fascia at the eaves, and where a cross gable is
        # cut to sit on the roof it meets - and carry no rafters.
        dist = None
        for _area, mid in sorted(inside.get(poly.index, ()), key=lambda t: -t[0]):
            hit, hit_n, _hi, d = shell.ray_cast(mid - n * 0.001, -n, 2.0)
            if hit is not None and hit_n.normalized().dot(n) < -0.98:
                dist = d
                break
        if dist is None:
            cuts[poly.index] = n
            continue
        pts = [m @ mesh.vertices[i].co for i in poly.vertices]
        # As deep as the roof is thick, less its sheathing
        d_face = max(min(depth, dist + 0.001 - SHEATHING), inch(3.5))
        faces.append((poly.index, n, pts, d_face))
    by_index = {f[0]: f for f in faces}

    # A rafter runs on from face to face within one plane (the eave strip
    # beside the rest of a slope): spans are gathered per plane and joined
    planes = {}
    for _i, n, pts, d_face in faces:
        key = (round(n.x, 3), round(n.y, 3), round(n.z, 3), round(n.dot(pts[0]), 3))
        plane = planes.setdefault(key, {'n': n, 'p0': pts[0], 'depth': d_face, 'lines': {}})
        plane['depth'] = min(plane['depth'], d_face)
        down = Vector((-n.x, -n.y)).normalized()     # downhill, in plan
        across = Vector((-down.y, down.x))
        plan = [Vector((p.x, p.y)) for p in pts]
        for a, b in scan(plan, across, step):
            pos = round(a.dot(across), 4)
            lo, hi = sorted((a.dot(down), b.dot(down)))
            plane['lines'].setdefault(pos, []).append((lo, hi))

    for plane in planes.values():
        n, d_face = plane['n'], plane['depth']
        plane_d = n.dot(plane['p0'])
        down = Vector((-n.x, -n.y)).normalized()
        across = Vector((-down.y, down.x))
        w = Vector((across.x, across.y, 0.0)) * (T / 2.0)

        def rise(p, inward):
            """Ends cut plumb, as a rafter's are, no deeper than the roof
            is thick there (less where another roof cuts its top)."""
            d = d_face
            for k in (0.003, 0.02, 0.05):
                hit = shell.ray_cast(p + inward * k - n * 0.001, -n, 2.0)
                if hit[0] is not None and hit[1].dot(n) < 0.0:      # leaving the roof
                    d = min(d, max(hit[3] - SHEATHING, hit[3] * 0.6))
            # Plumb if that stays in the roof; square to the slope where a
            # steeper one meets a flatter (a gambrel's break); else shorter
            start = p + inward * 0.003
            plumb = Vector((0.0, 0.0, d / abs(n.z)))
            for cut in (plumb, -n * d):
                if shell.ray_cast(start + cut.normalized() * 0.001, cut.normalized(), cut.length)[0] is None:
                    return cut
            hit = shell.ray_cast(start + Vector((0.0, 0.0, 0.001)), Vector((0.0, 0.0, 1.0)), plumb.length)
            return Vector((0.0, 0.0, max(hit[3] - SHEATHING, hit[3] * 0.6) if hit[0] else plumb.length))

        for pos, spans in plane['lines'].items():
            spans.sort()
            joined = [list(spans[0])]
            for lo, hi in spans[1:]:
                if lo <= joined[-1][1] + 1e-3:
                    joined[-1][1] = max(joined[-1][1], hi)
                else:
                    joined.append([lo, hi])
            for lo, hi in joined:
                ends = []
                for t in (lo, hi):
                    xy = across * pos + down * t
                    ends.append(Vector((xy.x, xy.y, (plane_d - n.x * xy.x - n.y * xy.y) / n.z)))
                ta, tb = ends
                along = (tb - ta).normalized()
                ra, rb = rise(ta, along), rise(tb, -along)
                bottom = [ta - w, tb - w, tb + w, ta + w]
                boards.box(bottom + [bottom[0] + ra, bottom[1] + rb,
                                     bottom[2] + rb, bottom[3] + ra])

    def crease(a, b, plumb):
        """A ridge, hip or valley board on edge along a to b (on the
        underside), its top with the rafters' tops, a size deeper - and
        kept inside the roof at its ends."""
        tops = []
        for p, q in ((a, b), (b, a)):
            inward = (q - p).normalized() * 0.02
            up = plumb
            hit = shell.ray_cast(p + inward + Vector((0.0, 0.0, 0.001)), Vector((0.0, 0.0, 1.0)), 3.0)
            if hit[0] is not None and hit[1].z > 0.0:           # leaving the roof
                up = min(up, max(hit[3] - SHEATHING, hit[3] * 0.6))
            tops.append(p + Vector((0.0, 0.0, up)))
        _sloped_board(boards, tops[0], tops[1], plumb + inch(1.5))

    # Creases: edges two sloped faces share where they are not one plane
    edge_faces = {}
    for poly in mesh.polygons:
        if poly.index not in by_index and poly.index not in cuts:
            continue
        for key in poly.edge_keys:
            edge_faces.setdefault(key, []).append(poly.index)
    for (i, j), owners in edge_faces.items():
        if len(owners) != 2:
            continue
        framed = [o for o in owners if o in by_index]
        if len(framed) == 1:
            # A framed slope against a cut. Square to it is the fascia at
            # the eaves; at an angle, where this roof meets another
            f1 = by_index[framed[0]]
            n_cut = cuts[owners[0] if owners[0] not in by_index else owners[1]]
            if abs(f1[1].dot(n_cut)) < 0.2:
                continue
            a, b = m @ mesh.vertices[i].co, m @ mesh.vertices[j].co
            if (b - a).length < T:
                continue
            if sits_on:
                inner = Vector(f1[2][0])
                for q in f1[2]:
                    inner = inner + q
                inner = inner / (len(f1[2]) + 1)
                _flat_board(boards, a, b, n_cut, inch(5.5), inner)
            else:
                crease(a, b, f1[3] / abs(f1[1].z))     # a valley rafter
            continue
        if len(framed) != 2:
            continue
        f1, f2 = by_index[owners[0]], by_index[owners[1]]
        n1, n2 = f1[1], f2[1]
        if n1.dot(n2) > 0.999:
            continue
        a, b = m @ mesh.vertices[i].co, m @ mesh.vertices[j].co
        if (b - a).length < T:
            continue
        crease(a, b, min(f1[3] / abs(n1.z), f2[3] / abs(n2.z)))
    ev.to_mesh_clear()


def _flat_board(boards, a, b, n, width, toward):
    """A board laid flat on a roof (n the normal of the face resting on
    it, pointing down into it), from the line a to b over to the side
    `toward` is on."""
    side = n.cross(b - a).normalized() * width
    if side.dot(toward - a) < 0.0:
        side = -side
    up = -n * T
    bottom = [a, b, b + side, a + side]
    boards.box(bottom + [p + up for p in bottom])


def _sloped_board(boards, a, b, depth):
    """A hip or valley board: on edge, from a to b, `depth` deep below it."""
    d = b - a
    side = Vector((-d.y, d.x, 0.0)).normalized() * (T / 2.0)
    down = Vector((0.0, 0.0, -depth))
    top = [a - side, b - side, b + side, a + side]
    boards.box([p + down for p in top] + top)


# =============================================================================
# THE FRAMING OBJECTS
# =============================================================================

def lumber_material():
    mat = bpy.data.materials.get(MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(MATERIAL)
        mat.diffuse_color = LUMBER_COLOR
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = LUMBER_COLOR
            bsdf.inputs['Roughness'].default_value = 0.85
    return mat


def _collection(scene, level):
    hb_house.ensure_level_collections(scene, level)
    col = hb_house.level_subcollection(level, PART)
    if col is None:
        col = bpy.data.collections.new(f"{level.name} - {PART}")
        col['HB_LEVEL_PART'] = PART
        level.collection.children.link(col)
    return col


def framing_objects(scene, level=None):
    return [o for o in scene.objects if o.get(FRAMING_KEY)
            and (level is None or o.get(hb_house.LEVEL_KEY) == level.uid)]


def level_framing(scene, level, depsgraph, tree):
    """All of a level's framing, as one mesh."""
    house = scene.hb_house
    step = spacing(house)
    boards = Boards()
    gables = _gable_tree(scene, depsgraph, level) if level.roof.enabled else None
    if house.framing_walls:
        for obj in scene.objects:
            if not obj.get('IS_WALL_BP') or obj.get(hb_house.LEVEL_KEY) != level.uid:
                continue
            if obj.get('WALL_TYPE', 'Exterior') not in FRAMED_WALLS:
                continue
            frame_wall(boards, obj, step, tree, gables)
    if house.framing_floors:
        frame_level_floor(boards, scene, level, step)
    if house.framing_ceilings:
        frame_level_ceilings(boards, scene, level, step, tree)
    if house.framing_roofs and level.roof.enabled:
        for obj, sits_on in ((level.roof.roof_obj, False), (level.roof.dormer_obj, True)):
            if obj is not None and obj.type == 'MESH' and obj.name in scene.objects:
                frame_roof(boards, obj, depsgraph, inch(24) if house.framing_spacing == '24' else step,
                           sits_on=sits_on)
    if house.framing_roofs:
        for room in level.rooms:
            obj = room.porch_roof_obj
            if obj is not None and obj.type == 'MESH' and obj.name in scene.objects:
                frame_roof(boards, obj, depsgraph, step, sits_on=True)
    count = boards.count
    return boards.mesh(f"Framing - {level.name}"), count


def build(scene):
    """Build (or rebuild) every level's framing and ghost the solids."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return 0
    try:
        scene.view_layers[0].update() if scene != bpy.context.scene else bpy.context.view_layer.update()
    except Exception:
        pass
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mat = lumber_material()
    total = 0
    for level in scene.hb_house.levels:
        tree = _roof_tree(scene, depsgraph, level)
        mesh, count = level_framing(scene, level, depsgraph, tree)
        mesh.materials.append(mat)
        total += count
        old = next(iter(framing_objects(scene, level)), None)
        if old is None:
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj[FRAMING_KEY] = True
            obj[hb_house.LEVEL_KEY] = level.uid
            obj.hide_select = True
            _collection(scene, level).objects.link(obj)
        else:
            prev = old.data
            old.data = mesh
            old.name = mesh.name
            if prev.users == 0:
                bpy.data.meshes.remove(prev)
    ghost(scene, True)
    return total


def clear(scene):
    """Remove the framing and put the solids back."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    for obj in framing_objects(scene):
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    ghost(scene, False)


def _ghosted(scene):
    """The solids framing stands for: walls, floors, ceilings, roofs and
    the siding built on them."""
    from . import hb_exterior
    out = []
    for obj in scene.objects:
        if obj.get('IS_WALL_BP') and obj.get('WALL_TYPE', 'Exterior') in FRAMED_WALLS:
            out.append(obj)
        elif obj.get('IS_FLOOR_BP') or obj.get('IS_CEILING_BP'):
            out.append(obj)
        elif obj.get(hb_exterior.GEO_KEY):
            out.append(obj)
    for level in scene.hb_house.levels:
        out += [o for o in (level.roof.roof_obj, level.roof.dormer_obj, level.roof.gables_obj)
                if o is not None]
        out += [room.porch_roof_obj for room in level.rooms if room.porch_roof_obj is not None]
    return out


def ghost(scene, on):
    """Draw the solids as wire while framing shows (render is untouched),
    or put back how they were drawn."""
    for obj in _ghosted(scene):
        if on:
            if GHOST_KEY not in obj:
                obj[GHOST_KEY] = obj.display_type
            obj.display_type = 'WIRE'
        elif GHOST_KEY in obj:
            obj.display_type = obj[GHOST_KEY]
            del obj[GHOST_KEY]


_held = 0       # > 0 while a larger rebuild will refresh once at its end


class held:
    """While inside, refresh does nothing: a wall edit rebuilds rooms and
    every roof, and the framing once after them."""

    def __enter__(self):
        global _held
        _held += 1

    def __exit__(self, *exc):
        global _held
        _held -= 1


def refresh(scene):
    """Rebuild the framing if it is showing (after walls, rooms or roofs
    change)."""
    scene = hb_house.house_scene_of(scene)
    if _held or scene is None or not scene.hb_house.show_framing:
        return
    try:
        build(scene)
    except Exception as ex:
        print('Home Builder: framing failed: %s' % ex)


# =============================================================================
# OPERATORS
# =============================================================================

class HOME_BUILDER_OT_rebuild_framing(bpy.types.Operator):
    """Build the framing again from the walls, rooms and roofs"""
    bl_idname = "home_builder.rebuild_framing"
    bl_label = "Rebuild Framing"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = hb_house.house_scene_of(context.scene)
        return scene is not None and scene.hb_house.show_framing

    def execute(self, context):
        n = build(context.scene)
        self.report({'INFO'}, f"Framing: {n} boards")
        return {'FINISHED'}


classes = (HOME_BUILDER_OT_rebuild_framing,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
