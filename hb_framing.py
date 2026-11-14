"""Framing: the studs, joists and rafters inside a house's simple shapes.

The house is modelled as plain solids - a wall is a box, a floor a slab,
a roof a shell - which is what is wanted while laying it out. Show
Framing (on the house) builds the framing those solids stand for, and
ghosts the solids so it can be seen:

* Walls: a bottom plate, a double top plate and studs on centres from
  the wall's start, sized from the wall's thickness (2x6 in a 6" wall,
  2x4 in a 4 1/2" one). At a square corner one wall runs through and
  the other butts into it, their upper top plates lapped the other way
  (see corner_plan). At each door and window: king and jack studs, a
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
FRAMED_WALLS = ('Exterior', 'Interior', 'Half', 'Dormer', 'Bay')


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

    def local_box(self, m, x0, x1, y0, y1, z0, z1, z1_end=None, x0_far=None, x1_far=None,
                  z0_end=None):
        """An axis-aligned board in a wall's own space (m its matrix); the
        top may slope from z1 at x0 to z1_end at x1, and the underside
        with it from z0 to `z0_end` (a plate under a roof's slope).
        `x0_far` and `x1_far` are its ends on the y1 side, for an end cut
        on the skew (a plate at a corner that isn't square)."""
        xa = x0 if x0_far is None else x0_far
        xb = x1 if x1_far is None else x1_far
        ze = z1 if z1_end is None else z1_end
        zb = z0 if z0_end is None else z0_end
        if max(x1 - x0, xb - xa) < 1e-4 or y1 - y0 < 1e-4 or max(z1 - z0, ze - zb) < 1e-4:
            return
        pts = [(x0, y0, z0), (x1, y0, zb), (xb, y1, zb), (xa, y1, z0),
               (x0, y0, z1), (x1, y0, ze), (xb, y1, ze), (xa, y1, z1)]
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


FIRE_BLOCK_OVER = 3.048     # walls taller than 10' get a row of fire blocks
BRIDGING_OVER = 2.44        # joist spans longer than 8' get bridging
JOIST_LAP = inch(3)         # joists lap this far past a bearing
COLLAR_DEPTH = inch(5.5)    # 2x6 collar ties


def junction_studs(scene, level, walls):
    """Extra studs where walls meet: on each wall, one just outside each
    face of a wall ending against it (both sides of a T, the inside of an
    L), so the drywall has backing in the corner. {wall name: [x]} with x
    a stud's start along the wall."""
    from .operators import walls as hb_walls
    segs = {}
    for obj in walls:
        seg = hb_walls.wall_seg(obj)
        if seg is not None:
            segs[obj.name] = (obj, seg)
    out = {}
    for name, (obj, seg) in segs.items():
        ext = hb_walls.wall_face_extents(obj)
        x0, x1 = (0.0, seg.length) if ext is None else (
            (ext['back'][0] + ext['front'][0]) / 2.0, (ext['back'][1] + ext['front'][1]) / 2.0)
        c = Vector(seg.face_point(seg.thickness / 2.0))
        d = Vector(seg.dir)
        xs = []
        for other, (oobj, oseg) in segs.items():
            if other == name:
                continue
            od = Vector(oseg.dir)
            if abs(d.dot(od)) > 0.5:
                continue                # parallel-ish: no corner on this wall
            on = Vector(oseg.normal)
            for w in (0.0, oseg.thickness):
                p = Vector(oseg.face_point(w))
                den = d.x * od.y - d.y * od.x
                if abs(den) < 1e-9:
                    continue
                rel = p - c
                s = (rel.x * od.y - rel.y * od.x) / den       # along this wall
                t = (rel.x * d.y - rel.y * d.x) / den         # along the other
                reach = seg.thickness + 0.05
                if not (-reach <= t <= reach or oseg.length - reach <= t <= oseg.length + reach):
                    continue            # the other wall doesn't end here
                if not (x0 + T < s < x1 - T):
                    continue            # at this wall's own end: its end stud
                # Just outside the other wall's body
                outward = on * (-1.0 if w == 0.0 else 1.0)
                xs.append(s if d.dot(outward) > 0 else s - T)
        if xs:
            out[name] = xs
    return out


def _wall_top(wall_obj, tree=None):
    """top(x): how high the wall stands at x along it - its height, or
    the roof's underside where that comes lower."""
    wall = hb_types.GeoNodeWall(wall_obj)
    length = wall.get_input('Length')
    height = wall.get_input('Height')
    end_h = wall.get_input('End Height') if wall.has_input('End Height') else 0.0
    ymid = wall.get_input('Thickness') / 2.0
    m = wall_obj.matrix_world

    def top(x):
        h = height if end_h <= 0.0 else height + (end_h - height) * (x / max(length, 1e-6))
        return _roof_above(tree, m, x, ymid, 0.0, h)
    return top


def corner_plan(walls, tree=None, rooms=None):
    """How each wall's framing ends where two walls turn a corner.

    The walls' solids are mitred there; framing isn't. At a square
    corner one wall runs THROUGH to the outside and the other BUTTs into
    its inside face - the wall whose end is at the corner runs through,
    the one starting there butts, so round a room every wall does one of
    each. Their upper top plates lap the other way, tying the two walls
    together. A corner that isn't square stays a MITRE: its plates are
    cut on the mitre line, so they meet without crossing.

    {wall name: {'start' | 'end': ('MITRE',) or (role, near, far, lap)}}
    with near and far the faces of the other wall's framing along this
    wall (near the room side, far the outside), and lap whether the
    upper plates cross. An end not in the plan is square: nothing to do."""
    from .operators import walls as hb_walls
    from . import hb_assemblies
    info = {}
    for obj in walls:
        wall = hb_types.GeoNodeWall(obj)
        if not wall.has_modifier() or hb_types.is_curved_wall(obj):
            continue
        ext = hb_walls.wall_face_extents(obj)
        if ext is None:
            continue
        pts = {}
        for end, face, pt in hb_walls.wall_plan_corners(obj):
            pts.setdefault(end, {})[face] = pt
        info[obj.name] = (obj, ext, pts)

    def same(a, b):
        return (a - b).length < 0.002

    plan = {}
    names = sorted(info)
    for name in names:
        obj, ext, pts = info[name]
        m = obj.matrix_world
        inv = m.inverted()
        d = (m.to_3x3() @ Vector((1.0, 0.0, 0.0))).to_2d().normalized()
        for i, end in enumerate(('start', 'end')):
            if abs(ext['back'][i] - ext['front'][i]) < 1e-4:
                continue            # cut square: a free end, or one against another wall
            role = ('MITRE',)
            mine = pts[end]
            for other in names:
                if other == name or role[0] != 'MITRE':
                    continue
                oobj, oext, opts = info[other]
                for j, oend in enumerate(('start', 'end')):
                    theirs = opts[oend]
                    if not ((same(mine['back'], theirs['back']) and same(mine['front'], theirs['front']))
                            or (same(mine['back'], theirs['front']) and same(mine['front'], theirs['back']))):
                        continue
                    om = oobj.matrix_world
                    od = (om.to_3x3() @ Vector((1.0, 0.0, 0.0))).to_2d().normalized()
                    if abs(d.dot(od)) > 0.02:
                        break       # not square: mitred
                    through = (end == 'end') if end != oend else (name < other)
                    oy0, oy1 = hb_assemblies.framing_band(oobj, rooms)
                    xs = sorted((inv @ (om @ Vector((0.0, oy, 0.0)))).x for oy in (oy0, oy1))
                    near, far = (xs[0], xs[1]) if end == 'end' else (xs[1], xs[0])
                    # The upper plates cross only where the two walls top out together
                    half = 'Half' in (obj.get('WALL_TYPE'), oobj.get('WALL_TYPE'))
                    here = _wall_top(obj, tree)((ext['back'][i] + ext['front'][i]) / 2.0)
                    there = _wall_top(oobj, tree)((oext['back'][j] + oext['front'][j]) / 2.0)
                    lap = not half and abs(here - there) < 0.002
                    role = ('THROUGH' if through else 'BUTT', near, far, lap)
                    break
            plan.setdefault(name, {})[end] = role
    return plan


def corner_studs(plan):
    """A backing stud in each wall that runs through a corner, just inside
    the wall butting into it: with its end stud, the corner the drywall
    on both walls nails to. {wall name: [x]}."""
    out = {}
    for name, ends in plan.items():
        for end, role in ends.items():
            if role[0] == 'THROUGH':
                out.setdefault(name, []).append(role[1] if end == 'start' else role[1] - T)
    return out


def frame_wall(boards, wall_obj, step, tree=None, gables=None, extra=(), blocking=False,
               rooms=None, corners=None):
    """Plates, studs and opening framing for one wall; `extra` stud
    positions (corners), with `blocking` a row of fire blocks in a
    wall over 10' tall, and `corners` how its ends meet the walls round
    the corner (see corner_plan)."""
    from .operators import walls as hb_walls
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier() or hb_types.is_curved_wall(wall_obj):
        return              # curved walls aren't framed yet
    length = wall.get_input('Length')
    t = wall.get_input('Thickness')
    height = wall.get_input('Height')
    if length < 0.05 or height < 0.3:
        return
    ext = hb_walls.wall_face_extents(wall_obj)
    if ext is not None:
        x0 = (ext['back'][0] + ext['front'][0]) / 2.0
        x1 = (ext['back'][1] + ext['front'][1]) / 2.0
    else:
        x0, x1 = 0.0, length
    # The studs sit in the wall's framing layer (centred, without an assembly)
    from . import hb_assemblies
    y0, y1 = hb_assemblies.framing_band(wall_obj, rooms)
    ymid = t / 2.0
    m = wall_obj.matrix_world
    top = _wall_top(wall_obj, tree)

    half = wall_obj.get('WALL_TYPE') == 'Half'
    plates = T if half else 2 * T
    openings = _openings(wall_obj)
    corners = corners if (corners and ext is not None) else {}

    def edge(i, y, upper=False):
        """Where a plate stops at the wall's start (i 0) or end (i 1), on
        the line y across the wall; `upper` for the upper top plate."""
        c = corners.get(('start', 'end')[i])
        if c is None:
            return (x0, x1)[i]
        if c[0] == 'MITRE':
            back, front = ext['back'][i], ext['front'][i]
            return back + (front - back) * (y / max(t, 1e-6))
        role, near, far, lap = c
        through = (role == 'THROUGH') != (upper and lap)
        return far if through else near

    def plate(a, b, lo, hi, z0, z1, z1_end=None, upper=False, z0_end=None):
        """A plate from a to b, its ends cut to the corner where they are
        the wall's own (lo and hi)."""
        boards.local_box(
            m, edge(0, y0, upper) if a == lo else a, edge(1, y0, upper) if b == hi else b,
            y0, y1, z0, z1, z1_end,
            x0_far=edge(0, y1, upper) if a == lo else a,
            x1_far=edge(1, y1, upper) if b == hi else b, z0_end=z0_end)

    def reach(upper=False):
        """The ends of a plate, at their longest."""
        return (min(edge(0, y0, upper), edge(0, y1, upper)),
                max(edge(1, y0, upper), edge(1, y1, upper)))

    # The studs stand between the plates' ends at their shortest
    x0 = max(edge(0, y0), edge(0, y1))
    x1 = min(edge(1, y0), edge(1, y1))

    # Bottom plate, broken at doors
    p0, p1 = reach()
    runs = [(p0, p1)]
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
        plate(a, b, p0, p1, 0.0, T)

    # Top plates, following the top: one board per layer along each
    # straight stretch, in steps only where a roof bends it. The upper
    # one laps the corner the other way from the lower.
    layers = int(round(plates / T))
    for k in range(layers):
        upper = layers > 1 and k == layers - 1
        q0, q1 = reach(upper)
        marks = sorted({q0, q1} | {min(max(q0 + j * step, q0), q1)
                                   for j in range(1, int((q1 - q0) / step) + 1)})
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
        lo = k * T - plates
        for a, b, ta, tb in pieces:
            # A board as thick at one end as the other: under a slope its
            # underside rises with its top
            plate(a, b, q0, q1, ta + lo, ta + lo + T, tb + lo + T, upper, z0_end=tb + lo)

    def stud(xa, z_lo, z_hi=None):
        z_hi = top(xa + T / 2.0) - plates if z_hi is None else z_hi
        boards.local_box(m, xa, xa + T, y0, y1, z_lo, z_hi)

    # Openings: kings, jacks, header, sill and cripples
    taken = []
    for ox0, ox1, oz0, oz1, door in openings:
        hd = header_depth(ox1 - ox0)
        head_top = min(oz1 + hd, top((ox0 + ox1) / 2.0) - plates)
        # An opening hard against the wall's end (a bay's side window) has
        # no room there for both: the king goes, and the stud beside the
        # opening stands full height in its place - never past the wall's
        # own framing, into the wall round the corner.
        h0, h1 = ox0 - T, ox1 + T
        for king, jack, left in ((ox0 - 2 * T, ox0 - T, True), (ox1 + T, ox1, False)):
            fits = lambda xa: xa >= x0 - 1e-4 and xa + T <= x1 + 1e-4
            if fits(king):
                stud(king, T)
                if fits(jack):
                    stud(jack, T, oz1)
            elif fits(jack):
                stud(jack, T)
                if left:
                    h0 = ox0
                else:
                    h1 = ox1
        boards.local_box(m, max(h0, x0), min(h1, x1), y0, y1, oz1, head_top)
        if not door and oz0 > 2 * T:
            boards.local_box(m, ox0, ox1, y0, y1, oz0 - T, oz0)
        taken.append((ox0 - 2 * T, ox1 + 2 * T, ox0, ox1, oz0, head_top, door))

    # Studs on centres from the start, the end stud, corner studs, and cripples
    xs = [x0] + [x0 + k * step - T / 2.0 for k in range(1, int((x1 - x0) / step) + 1)]
    xs = [x for x in xs if x + T <= x1 - T] + [x1 - T]
    for xe in extra:
        if x0 + T <= xe <= x1 - 2 * T and all(abs(xe - x) > T * 0.9 for x in xs):
            xs.append(xe)
    xs.sort()
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

    # Fire blocking: a row between the studs halfway up a tall wall
    if blocking and height > FIRE_BLOCK_OVER:
        zb = height / 2.0
        for xa, xb in zip(xs, xs[1:]):
            if xb - (xa + T) < 0.02:
                continue
            if any(o[0] - 1e-4 < xb and xa + T < o[1] + 1e-4 and o[4] - T < zb + T and zb < o[5]
                   for o in taken):
                continue
            boards.local_box(m, xa + T, xb, y0, y1, zb, zb + T)

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


BEARING_WALLS = ('Exterior', 'Interior', 'Foundation')


def bearing_lines(scene, below, joist_bottom):
    """What a level's floor joists bear on, as plan lines: the walls of
    the level below (their middles) and its beams and girders whose tops
    come up to the joists."""
    from . import hb_members
    from .operators import walls as hb_walls
    out = []
    if below is None:
        return out
    _objs, segs = hb_walls.level_wall_segs(scene, below.uid)
    for seg in segs:
        if seg.wall_type not in BEARING_WALLS or seg.length < 0.1:
            continue
        p = seg.face_point(seg.thickness / 2.0)
        out.append((p, (p[0] + seg.dir[0] * seg.length, p[1] + seg.dir[1] * seg.length)))
    for m in hb_members.members_of(scene, below):
        if m.get('MEMBER_KIND') not in ('BEAM', 'GIRDER'):
            continue
        if m.location.z < joist_bottom - 0.06:
            continue                    # dropped too low to carry them
        # From its location and turn, not matrix_world: a member just
        # made has not been evaluated yet
        rz = m.rotation_euler.z
        length = float(m['MEMBER_LENGTH'])
        a = (m.location.x, m.location.y)
        out.append((a, (a[0] + math.cos(rz) * length, a[1] + math.sin(rz) * length)))
    return out


def joist_axis(level, polys, bearings):
    """The axis joists are spaced along (they run square to it): as the
    level says, or the way whose longest span between bearings is the
    shortest."""
    from . import hb_structure_geom as geom
    if level.joist_direction == 'X':
        return (0.0, 1.0)
    if level.joist_direction == 'Y':
        return (1.0, 0.0)
    best = None
    for axis in ((1.0, 0.0), (0.0, 1.0)):
        worst = 0.0
        for poly in polys:
            for a, b in scan(poly, axis, 0.6, margin=T):
                worst = max(worst, geom.longest_span(tuple(a), tuple(b), bearings))
        if best is None or worst < best[0] - 0.05:
            best = (worst, axis)
    return best[1] if best else (1.0, 0.0)


def frame_deck(boards, poly, z_top, depth, step, axis, bearings, openings=(), bridging=False):
    """A level's floor over one building's outline: a rim round it, and
    joists across it the way `axis` says, broken and lapped over the
    bearing lines, headed off round openings, bridged at mid-span."""
    from . import hb_structure_geom as geom
    n = len(poly)
    ccw = geom.polygon_area(poly) > 0
    for i in range(n):
        p, q = Vector(poly[i]), Vector(poly[(i + 1) % n])
        d = q - p
        if d.length < T:
            continue
        inward = Vector((-d.y, d.x)).normalized() * (T / 2.0)
        if not ccw:
            inward = -inward
        boards.run(p + inward, q + inward, z_top, T, depth)
    deck = geom.offset_polygon(poly, -T)
    holes = [_grown(cell, 2 * T) for cells, _edges in openings for cell in cells]
    ax = Vector(axis)
    lines = {}
    joist_dir = None
    for a, b in scan(deck, axis, step, margin=T):
        a, b = Vector(a), Vector(b)
        if joist_dir is None:
            joist_dir = b - a
        pos = round(a.dot(ax), 4)
        pieces = []
        for t0, t1 in geom.joist_pieces(tuple(a), tuple(b), bearings, JOIST_LAP):
            pa, pb = a + (b - a) * t0, a + (b - a) * t1
            spans = [(0.0, 1.0)]
            for hole in holes:
                cut = geom.segment_in_polygon_spans(tuple(pa), tuple(pb), hole)
                spans = [s for sp in spans for s in geom.subtract_intervals(sp, cut)]
            for s0, s1 in spans:
                p, q = pa + (pb - pa) * s0, pa + (pb - pa) * s1
                if (q - p).length > 2.5 * T:
                    boards.run(p, q, z_top, T, depth)
                    pieces.append((p, q))
        lines.setdefault(pos, []).extend(pieces)
    if joist_dir is not None:
        for cells, edges in openings:
            if any(geom._inside(tuple((Vector(c[0]) + Vector(c[2])) / 2.0), poly) for c in cells):
                _frame_opening(boards, poly, z_top, depth, edges, joist_dir)
    if not bridging:
        return
    # Solid blocks between neighbouring joists at the middle of long spans
    positions = sorted(lines)
    for k in range(len(positions) - 1):
        for p, q in lines[positions[k]]:
            if (q - p).length < BRIDGING_OVER:
                continue
            mid = (p + q) / 2.0
            gap = positions[k + 1] - positions[k]
            other = mid + ax * gap
            if any(min(r.dot(q - p), s.dot(q - p)) - 1e-4 <= other.dot(q - p) <= max(r.dot(q - p), s.dot(q - p)) + 1e-4
                   for r, s in lines[positions[k + 1]]):
                boards.run(mid + ax * (T / 2.0), other - ax * (T / 2.0), z_top, T, depth)


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
    polys = hb_house.level_outlines(scene, level)
    if not polys:
        for area in _room_areas(scene, level):
            frame_floor(boards, area.polygon, z_top, depth, step, openings=openings)
        return
    bearings = bearing_lines(scene, below, z_top - depth)
    axis = joist_axis(level, polys, bearings)
    for poly in polys:
        frame_deck(boards, poly, z_top, depth, step, axis, bearings, openings,
                   bridging=house.framing_blocking)


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
        if _under_trusses(scene, level, p):
            continue                    # the trusses' bottom chords are its ceiling
        _axis, span = short_axis(area.polygon)
        depth = joist_depth(span)
        z_bottom = level.elevation + hb_rooms.room_height(room, level)
        frame_floor(boards, area.polygon, z_bottom + depth, depth, step, tree)


# =============================================================================
# ROOFS
# =============================================================================

VALLEY_REACH = 2.0          # m: how far a rafter runs on to the valley it lands on


def frame_roof(boards, obj, depsgraph, step, depth=RAFTER_DEPTH, sits_on=False, base=None):
    """Rafters up from every sloped underside face of a roof, inside its
    thickness, and a board along each crease between two of them (ridges,
    hips, valleys). Where the roof is cut to meet another: a valley rafter
    under the cut, or - for a roof that `sits_on` another (a cross gable,
    a porch) - a flat valley board on that roof for its rafters to land on.

    The roof is modelled cut away under the whole of a roof that meets
    it - back to where that roof's TOP comes through its underside - but
    a valley rafter stands where the two undersides meet, further in. So
    the valley is put there, and this roof's rafters run on past the cut
    to land on it.

    `base` is what framing the roof it sits on returned, when that roof
    has rafters of its own: this roof's rafters then run on down to that
    same valley, so the jacks of both roofs land on the one valley
    rafter, and the flat boards are left out. Returns (shell, [(normal,
    plane offset, thickness)], its valleys) of this roof, to be the
    `base` of another."""
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
        faces.append((poly.index, n, pts, d_face, dist))
    by_index = {f[0]: f for f in faces}

    # Where a slope is cut to meet another roof: the edges it shares with
    # a cut through its thickness that isn't square to it (square is the
    # fascia at the eaves)
    edge_faces = {}
    for poly in mesh.polygons:
        if poly.index not in by_index and poly.index not in cuts:
            continue
        for key in poly.edge_keys:
            edge_faces.setdefault(key, []).append(poly.index)
    meets = {}              # edge -> (a, b, the slope's face, the cut's normal, shift)
    for (i, j), owners in edge_faces.items():
        framed = [o for o in owners if o in by_index]
        if len(owners) != 2 or len(framed) != 1:
            continue
        f1 = by_index[framed[0]]
        n_cut = cuts[owners[0] if owners[0] not in by_index else owners[1]]
        if abs(f1[1].dot(n_cut)) < 0.2:
            continue
        a, b = m @ mesh.vertices[i].co, m @ mesh.vertices[j].co
        if (b - a).length < T:
            continue
        # From the cut's edge to the valley: out of the face, along the
        # slope, to where the other roof's underside (its top, a roof's
        # thickness down) comes through
        shift = None
        if not sits_on:
            # (the way that goes deeper under the other roof's top)
            out = (b - a).cross(f1[1]).normalized()
            if n_cut.dot(out) < 0.0:
                out = -out
            den = n_cut.dot(out)
            if den > 1e-6 and f1[4] / den < VALLEY_REACH:
                shift = out * (f1[4] / den)
        meets[(i, j)] = (a, b, f1, n_cut, shift)

    # A rafter runs on from face to face within one plane (the eave strip
    # beside the rest of a slope): spans are gathered per plane and joined
    planes = {}
    for _i, n, pts, d_face, _dist in faces:
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

    ran_on = []             # where rafters that run on to a valley left this roof
    for plane in planes.values():
        n, d_face = plane['n'], plane['depth']
        plane_d = n.dot(plane['p0'])
        down = Vector((-n.x, -n.y)).normalized()
        across = Vector((-down.y, down.x))
        w = Vector((across.x, across.y, 0.0)) * (T / 2.0)
        # The slope's own reach, up and down: a rafter run on to a valley
        # stays within it
        reach = (min(lo for spans in plane['lines'].values() for lo, _hi in spans),
                 max(hi for spans in plane['lines'].values() for _lo, hi in spans))

        def rise(p, inward):
            """Ends cut plumb, as a rafter's are, no deeper than the roof
            is thick there (less where another roof cuts its top)."""
            d = d_face
            for k in (0.003, 0.02, 0.05):
                hit = shell.ray_cast(p + inward * k - n * 0.001, -n, 2.0)
                # Leaving the roof by its top. Not by a plumb face: an eave or
                # a gable end cut plumb is the rafter's own plumb cut, and
                # takes nothing off its depth.
                if hit[0] is not None and hit[1].dot(n) < 0.0 and hit[1].z > 0.05:
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
                # On to the valley: this roof's own, past where it is cut,
                # or that of the roof this one sits on
                full = Vector((0.0, 0.0, d_face / abs(n.z)))
                landed = [None, None]
                for k, (end, outward) in enumerate(((ta, -along), (tb, along))):
                    if base is not None:
                        landed[k] = _to_valley(base, end, outward, n)
                    else:
                        landed[k] = _past_cut(meets.values(), end, outward, n)
                for k in (0, 1):
                    if landed[k] is not None and not (
                            reach[0] - 1e-3 <= Vector((landed[k].x, landed[k].y)).dot(down)
                            <= reach[1] + 1e-3):
                        landed[k] = None
                    if landed[k] is not None and base is not None:
                        ran_on.append((ta, tb)[k])
                if landed[0] is not None:
                    ta, ra = landed[0], full
                if landed[1] is not None:
                    tb, rb = landed[1], full
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

    # The valleys, moved in from the cuts: two that cross (either side of
    # a cross gable, at its ridge) stop at each other
    valleys = {key: [v[0] + v[4], v[1] + v[4]] for key, v in meets.items() if v[4] is not None}
    keys = list(valleys)
    for x, ka in enumerate(keys):
        for kb in keys[x + 1:]:
            hit = _cross_2d(valleys[ka], valleys[kb])
            if hit is None:
                continue
            for key, t in ((ka, hit[0]), (kb, hit[1])):
                a, b = valleys[key]
                at = a + (b - a) * t
                valleys[key] = [a, at] if t > 0.5 else [at, b]

    # Creases: edges two sloped faces share where they are not one plane
    for (i, j), owners in edge_faces.items():
        if len(owners) != 2:
            continue
        framed = [o for o in owners if o in by_index]
        if (i, j) in meets:
            # A slope cut to meet another roof
            a, b, f1, n_cut, shift = meets[(i, j)]
            if sits_on:
                inner = Vector(f1[2][0])
                for q in f1[2]:
                    inner = inner + q
                inner = inner / (len(f1[2]) + 1)
                # A board laid on the roof this one sits on, for its rafters
                # to land on - but not along the stretch whose rafters run on
                # to that roof's valley instead
                ab = b - a
                ts = [(q - a).dot(ab) / ab.length_squared for q in ran_on
                      if (a + ab * max(0.0, min(1.0, (q - a).dot(ab) / ab.length_squared)) - q).length < 0.03]
                pad = step / ab.length
                runs = [(0.0, 1.0)] if not ts else [(0.0, min(ts) - pad), (max(ts) + pad, 1.0)]
                least = step * 1.5 if ts else inch(6)      # no stub past the last rafter
                for t0, t1 in runs:
                    t0, t1 = max(t0, 0.0), min(t1, 1.0)
                    if (t1 - t0) * ab.length > least:
                        _flat_board(boards, a + ab * t0, a + ab * t1, n_cut, inch(5.5), inner)
            elif shift is not None:
                crease(valleys[(i, j)][0], valleys[(i, j)][1],
                       f1[3] / abs(f1[1].z))                    # the valley rafter
            else:
                crease(a, b, f1[3] / abs(f1[1].z))
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
        if base is not None:
            # A ridge that runs into the roof this one sits on carries on
            # to the valleys' meeting
            along = (b - a).normalized()
            a = _to_valley(base, a, -along) or a
            b = _to_valley(base, b, along) or b
        crease(a, b, min(f1[3] / abs(n1.z), f2[3] / abs(n2.z)))
    ev.to_mesh_clear()
    thick = {}
    for _i, n, pts, _d, dist in faces:
        key = (round(n.x, 3), round(n.y, 3), round(n.z, 3), round(n.dot(pts[0]), 3))
        thick[key] = max(thick.get(key, 0.0), dist)
    return (shell, [(plane['n'], plane['n'].dot(plane['p0']), thick[key])
                    for key, plane in planes.items()], list(valleys.values()))


def _short_of_valley(s, outward, valley):
    """A rafter's run to a valley's line, less half the valley rafter."""
    sin = outward.cross(valley.normalized()).length
    return s - (T / 2.0) / max(sin, 0.3)


def _past_cut(meets, p, outward, n):
    """Where a rafter ending at p - on an edge its slope is cut along to
    meet another roof - lands on the valley, carried on `outward`. None
    if p isn't on such an edge, or the rafter doesn't run that way."""
    for a, b, f1, _n_cut, shift in meets:
        if shift is None or f1[1].dot(n) < 0.999:
            continue
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        if (a + ab * t - p).length > 0.02:
            continue
        # The valley is the edge moved by `shift`: along the rafter, that far
        # square to the edge
        square = shift - ab * (shift.dot(ab) / ab.length_squared)
        den = outward.dot(square.normalized())
        if den < 0.05:
            return None
        s = _short_of_valley(square.length / den, outward, ab)
        return p + outward * s if s > 0.0 else None
    return None


def _cross_2d(s1, s2):
    """Where two segments cross in plan, as (t along the first, t along
    the second), or None."""
    p, r = s1[0].to_2d(), (s1[1] - s1[0]).to_2d()
    q, d = s2[0].to_2d(), (s2[1] - s2[0]).to_2d()
    den = r.x * d.y - r.y * d.x
    if abs(den) < 1e-9:
        return None
    t = ((q.x - p.x) * d.y - (q.y - p.y) * d.x) / den
    u = ((q.x - p.x) * r.y - (q.y - p.y) * r.x) / den
    return (t, u) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else None


def _to_valley(base, p, outward, n=None):
    """Where a rafter ending at p - where its roof lands on the roof it
    sits on - meets that roof's underside, carried on down `outward`: the
    valley, less half the valley rafter standing there. None if p isn't
    on that roof's top, or there is no valley rafter where it would land.
    Without `n` (the rafter's slope) it is a ridge, level, carried to the
    valley itself."""
    shell, planes, valleys = base
    if n is not None and outward.z >= 0.0:
        return None
    if shell.find_nearest(p, 0.03)[0] is not None:
        return None             # that roof is whole here: this one lands on it
    best = None
    for bn, bd, thick in planes:
        # On that slope's top: its underside's plane, its thickness up
        # (the roof itself is cut away there, so there is no face to find)
        if abs(bn.dot(p) - (bd - thick)) > 0.03:
            continue
        den = bn.dot(outward)
        if abs(den) < 1e-6:
            continue
        s = (bd - bn.dot(p)) / den
        if 0.01 < s < VALLEY_REACH and (best is None or s < best[0]):
            best = (s, bn)
    if best is None:
        return None
    s, bn = best
    q = p + outward * s
    for a, b in valleys:
        ab = b - a
        t = max(0.0, min(1.0, (q - a).dot(ab) / max(ab.length_squared, 1e-9)))
        if (a + ab * t - q).length < 0.1:
            break
    else:
        return None             # no valley rafter there to land on
    if n is None:
        return q
    valley = n.cross(bn)
    if valley.length < 1e-6:
        return None
    s = _short_of_valley(s, outward, valley)
    return p + outward * s if s > 0.0 else None


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

def frame_collar_ties(boards, scene, level, step):
    """Collar ties in a gable or gambrel rafter roof: across every other
    rafter pair, a third of the way down from the ridge, beside the
    rafter; none over a vaulted room."""
    from . import hb_roofs, hb_rooms
    roof = level.roof
    if not roof.enabled or roof.style not in ('GABLE', 'GAMBREL'):
        return
    frame = hb_roofs.roof_frame(scene, level)
    if frame is None:
        return
    z_tie = frame['ridge_z'] - (frame['ridge_z'] - frame['plate']) / 3.0
    under = frame['under']
    us = []
    for (a, za), (b, zb) in zip(under, under[1:]):
        if (za - z_tie) * (zb - z_tie) < 0 and abs(zb - za) > 1e-9:
            us.append(a + (b - a) * (z_tie - za) / (zb - za))
    if len(us) < 2:
        return
    ua, ub = min(us), max(us)
    vaulted = []
    for room in level.rooms:
        if not room.orphaned and room.ceiling_style in ('VAULTED', 'ATTIC'):
            poly = hb_rooms.room_polygon(scene, level, room)
            if poly:
                vaulted.append(poly)
    k = math.ceil(frame['v0'] / step)
    while k * step < frame['v1']:
        v = k * step
        k += 1
        if (k - 1) % 2 or v - frame['v0'] < step / 2.0 or frame['v1'] - v < step / 2.0:
            continue
        mid = hb_roofs._world(frame, (ua + ub) / 2.0, v + T, 0.0)
        if any(hb_wall_graph.point_in_polygon((mid[0], mid[1]), poly) for poly in vaulted):
            continue
        a = hb_roofs._world(frame, ua, v + T, 0.0)
        b = hb_roofs._world(frame, ub, v + T, 0.0)
        boards.run((a[0], a[1]), (b[0], b[1]), z_tie, T, COLLAR_DEPTH)


TRUSS_CHORD = inch(3.5)     # 2x4 chords and webs


def _plane_member(boards, frame, v, a, b, depth):
    """A truss member in the plane at v: centreline a-b in (u, z), `depth`
    deep in the plane, a board's thickness across it."""
    from . import hb_roofs
    du, dz = b[0] - a[0], b[1] - a[1]
    length = (du * du + dz * dz) ** 0.5
    if length < 1e-4:
        return
    nu, nz = -dz / length * depth / 2.0, du / length * depth / 2.0
    ring = [(a[0] - nu, a[1] - nz), (b[0] - nu, b[1] - nz), (b[0] + nu, b[1] + nz), (a[0] + nu, a[1] + nz)]
    w = lambda u, vv, z: Vector(hb_roofs._world(frame, u, vv, z))
    boards.box([w(u, v - T / 2.0, z) for u, z in ring] + [w(u, v + T / 2.0, z) for u, z in ring])


def frame_trusses(boards, scene, level):
    """Trusses along a gable roof in place of its rafters and ceiling
    joists, every truss spacing between the gable walls, each bearing on
    the side walls' outside faces. True if it framed any."""
    from . import hb_roofs, hb_structure_geom as geom
    roof = level.roof
    kind = hb_roofs.trusses_of(roof)
    if not roof.enabled or kind is None:
        return False
    frame = hb_roofs.roof_frame(scene, level)
    if frame is None:
        return False
    members = geom.truss(frame['u0'], frame['u1'], frame['base'], frame['plate'],
                         frame['p'], roof.eave_overhang, kind, TRUSS_CHORD)
    # Just inside the gable walls, and every spacing between
    inset = inch(6)
    v0, v1 = frame['v0'] + inset, frame['v1'] - inset
    n = max(1, math.ceil((v1 - v0) / roof.truss_spacing))
    for k in range(n + 1):
        v = v0 + (v1 - v0) * k / n
        for a, b in members:
            _plane_member(boards, frame, v, a, b, TRUSS_CHORD)
    return True


def _under_trusses(scene, level, point):
    """Whether a plan point is under a level's trussed roof."""
    from . import hb_roofs
    if hb_roofs.trusses_of(level.roof) is None or not level.roof.enabled:
        return False
    frame = hb_roofs.roof_frame(scene, level)
    if frame is None:
        return False
    u, v = hb_roofs._uv(frame, point)
    return frame['u0'] <= u <= frame['u1'] and frame['v0'] <= v <= frame['v1']


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
        walls = [obj for obj in scene.objects if obj.get('IS_WALL_BP')
                 and obj.get(hb_house.LEVEL_KEY) == level.uid
                 and obj.get('WALL_TYPE', 'Exterior') in FRAMED_WALLS]
        extras = junction_studs(scene, level, walls) if house.framing_corners else {}
        from . import hb_exterior
        rooms = hb_exterior._indoor_polygons(scene) if any(
            o.get('HB_ASSEMBLY') for o in walls) else None
        corners = corner_plan(walls, tree, rooms)
        if house.framing_corners:
            for name, xs in corner_studs(corners).items():
                extras[name] = list(extras.get(name, ())) + xs
        for obj in walls:
            frame_wall(boards, obj, step, tree, gables, extras.get(obj.name, ()),
                       house.framing_blocking, rooms, corners.get(obj.name))
    if house.framing_floors:
        frame_level_floor(boards, scene, level, step)
    if house.framing_ceilings:
        frame_level_ceilings(boards, scene, level, step, tree)
    trussed = house.framing_roofs and frame_trusses(boards, scene, level)
    if house.framing_roofs and house.framing_collar_ties and not trussed:
        frame_collar_ties(boards, scene, level, inch(24) if house.framing_spacing == '24' else step)
    if house.framing_roofs and level.roof.enabled:
        base = None             # the main roof's undersides, for what sits on it
        for obj, sits_on in ((level.roof.roof_obj, False), (level.roof.dormer_obj, True)):
            if trussed and obj == level.roof.roof_obj:
                continue                # trusses, not rafters
            if obj is not None and obj.type == 'MESH' and obj.name in scene.objects:
                made = frame_roof(boards, obj, depsgraph,
                                  inch(24) if house.framing_spacing == '24' else step,
                                  sits_on=sits_on, base=base if sits_on else None)
                if not sits_on:
                    base = made
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
