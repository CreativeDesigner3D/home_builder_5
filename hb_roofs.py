"""
Home Builder Roofs

A roof over a level of a house: built over the outside faces of the
level's exterior walls, with the ridge the long way (or the way you
choose). It sits on top of the level's walls, or starts at the level's
floor so the level is inside it. Styles: gable (two slopes meeting at a
ridge) and barn / gambrel (a steep lower slope and a shallow upper one
on each side). Every style is one profile - the roof's underside traced
across the house - and the roof, its trim and the dormer valleys are
all built from that.

The roof also shapes the level above it, so the upper floor lives inside
it:

* A trim volume - everything above the roof's underside - cuts the upper
  level's walls and room ceilings with a Boolean. Side walls become knee
  walls, interior walls stop under the slope, and ceilings only remain
  where there is headroom, so the rooms get sloped ceilings.
* Exterior walls of the upper level that run square to the ridge are the
  gable walls: they are raised to the ridge so the trim can cut them
  into the gable's triangle.

Dormers come from the walls: a bump-out under the roof - an outer wall
along the ridge, joined at both ends by short walls back to the main
side wall - gets a gable dormer. Its roof runs out from the main roof
and stops where it meets it (a valley); the main roof is opened under
it; and the trim leaves the dormer alone, so its side walls stop at the
dormer eave and its front wall takes the dormer's gable.

Settings live on the level (HB_Roof in hb_house); the roof is rebuilt
when they change and whenever walls are edited.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from . import hb_house, hb_utils
from .units import inch

ROOF_KEY = 'IS_ROOF'
ROOF_CUTTER_KEY = 'IS_ROOF_CUTTER'
TRIM_PREFIX = "Roof - "
DORMER_CUT = "Dormers"          # the Boolean that opens the main roof / trim
VALLEY_CUT = "Valley"           # the one that stops the dormer roofs
CUTTER_REACH = 2.0          # how far the trim volume runs past the house (m)
CUTTER_HEIGHT = 50.0        # and up
GABLE_MARGIN = 0.05         # gable walls run this far past the roof underside
SET_BACK_MIN = 0.05         # an eave-side wall this far inside the outline is set back
DORMER_MARGIN = 0.5         # dormer volumes reach this far past the front wall
GABLE_INFILL = 0.15         # thickness of a cross gable's filled-in gable end
DORMER_WALL = 0.12          # thickness of a shed dormer's front and cheeks
SHED_SET_BACK = 0.9         # a new shed dormer's front, in from the wall line
SHED_FRONT_RISE = 1.07      # and how far its front wall stands above the roof
SHED_WIDTH = 3.05           # its width, at most
SHINGLE_MATERIAL = "HB Roof Shingles"
SHINGLE_COLOR = (0.15, 0.19, 0.16, 1.0)

# Dormer front walls and the height they need, per roof level uid, from
# the last rebuild: {level uid: {wall name: top z}}
_dormer_fronts = {}


# =============================================================================
# LOOKUPS
# =============================================================================

def level_of_roof(roof):
    """The HB_Level holding a roof ('hb_house.levels[i].roof')."""
    path = roof.path_from_id()
    return roof.id_data.path_resolve(path[:path.rindex('.roof')])


def _exterior_walls(scene, level):
    return [o for o in scene.objects
            if o.get('IS_WALL_BP') and o.get(hb_house.LEVEL_KEY) == level.uid
            and o.get('WALL_TYPE', 'Exterior') == 'Exterior']


def roof_frame(scene, level):
    """The geometry a level's roof is built from, or None without walls.

    u runs across the roof (square to the ridge), v along it. The roof
    meets the outside faces of the exterior walls at the plate: the top
    of the walls, or the level's floor, plus the eave height. 'under' is
    the underside traced across from one wall face to the other, through
    the ridge (and a barn roof's breaks); 'p_out' the slope at the eaves,
    which the overhangs carry on."""
    from .operators import walls
    roof = level.roof
    outline_levels = [level]
    if roof.base == 'FLOOR':
        # A roof that starts at the floor covers the walls below too
        below = hb_house.level_below(level.id_data.hb_house, level)
        if below is not None:
            outline_levels.append(below)
    corners = []
    for lv in outline_levels:
        for obj in _exterior_walls(scene, lv):
            corners.extend(pt for _e, _f, pt in walls.wall_plan_corners(obj))
    if len(corners) < 3:
        return None
    x0, x1 = min(p.x for p in corners), max(p.x for p in corners)
    y0, y1 = min(p.y for p in corners), max(p.y for p in corners)
    if roof.use_extents and roof.ext_x1 - roof.ext_x0 > 0.3 and roof.ext_y1 - roof.ext_y0 > 0.3:
        x0, x1, y0, y1 = roof.ext_x0, roof.ext_x1, roof.ext_y0, roof.ext_y1
    along_x = (x1 - x0) >= (y1 - y0) if roof.ridge == 'AUTO' else roof.ridge == 'X'
    if along_x:
        u0, u1, v0, v1 = y0, y1, x0, x1
    else:
        u0, u1, v0, v1 = x0, x1, y0, y1
    half = (u1 - u0) / 2.0
    uc = (u0 + u1) / 2.0
    if roof.base == 'FLOOR':
        base = level.elevation
    else:
        # The level's own wall height, not the walls' current tops: the
        # roof raises its gable walls, and reading those back would lift
        # the roof on every rebuild
        base = level.elevation + hb_house.exterior_wall_height(level)
    plate = base + roof.eave_height
    p = roof.pitch / 12.0

    if roof.style == 'GAMBREL':
        p_low = roof.lower_pitch / 12.0
        z_break = base + roof.break_height
        inset = (z_break - plate) / p_low if z_break > plate else 0.0
        inset = min(max(inset, 0.0), half * 0.95)
        z_break = plate + inset * p_low
        ridge_z = z_break + (half - inset) * p
        under = [(u0, plate), (u0 + inset, z_break), (uc, ridge_z),
                 (u1 - inset, z_break), (u1, plate)]
        p_out = p_low
    else:
        ridge_z = plate + half * p
        under = [(u0, plate), (uc, ridge_z), (u1, plate)]
        p_out = p
    return {
        'along_x': along_x, 'u0': u0, 'u1': u1, 'v0': v0, 'v1': v1,
        'uc': uc, 'half': half, 'p': p, 'p_out': p_out,
        'angle': math.atan(p), 'plate': plate, 'base': base,
        'ridge_z': ridge_z,                 # underside at the ridge
        'under': under,
        'level_uid': level.uid,
        'custom': bool(roof.use_extents),
    }


def _extended(frame, reach):
    """The underside carried on past both wall faces by `reach`, down the
    eave slope."""
    under = frame['under']
    drop = reach * frame['p_out']
    return ([(under[0][0] - reach, under[0][1] - drop)] + list(under)
            + [(under[-1][0] + reach, under[-1][1] - drop)])


def _offset_up(points, t):
    """A polyline moved up off itself by t, square to each segment, with
    the corners mitred."""
    normals = []
    for (a0, z0), (a1, z1) in zip(points, points[1:]):
        da, dz = a1 - a0, z1 - z0
        length = math.hypot(da, dz) or 1.0
        n = (-dz / length, da / length)
        if n[1] < 0:
            n = (-n[0], -n[1])
        normals.append(n)
    out = [(points[0][0] + normals[0][0] * t, points[0][1] + normals[0][1] * t)]
    for i in range(1, len(points) - 1):
        (pa, pz), n1, n2 = points[i], normals[i - 1], normals[i]
        # Where the two offset lines cross: along the bisector, far enough
        # that each line is t from the corner
        bx, bz = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, bz)
        if bl < 1e-9:
            out.append((pa + n1[0] * t, pz + n1[1] * t))
            continue
        bx, bz = bx / bl, bz / bl
        k = t / max(bx * n1[0] + bz * n1[1], 1e-6)
        out.append((pa + bx * k, pz + bz * k))
    out.append((points[-1][0] + normals[-1][0] * t, points[-1][1] + normals[-1][1] * t))
    return out


def _dedupe(points):
    out = []
    for q in points:
        if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > 1e-6:
            out.append(q)
    return out


def _uv(frame, point):
    """(u, v) of a world XY point."""
    return (point[1], point[0]) if frame['along_x'] else (point[0], point[1])


def _world(frame, u, v, z):
    return (v, u, z) if frame['along_x'] else (u, v, z)


# =============================================================================
# GEOMETRY
# =============================================================================

def _add_prism(bm, section, b0, b1, to_world):
    """Add a closed prism to bm: the (a, z) section swept along b from b0
    to b1, placed by to_world(a, b, z)."""
    first = [bm.verts.new(to_world(a, b0, z)) for a, z in section]
    last = [bm.verts.new(to_world(a, b1, z)) for a, z in section]
    bm.faces.new(first)
    bm.faces.new(list(reversed(last)))
    n = len(section)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((first[i], first[j], last[j], last[i]))


def _mesh(name, prisms):
    """A mesh of prisms [(section, b0, b1, to_world)]."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for section, b0, b1, to_world in prisms:
        _add_prism(bm, section, b0, b1, to_world)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = (co.x + co.z, co.y + co.z)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _along_ridge(frame):
    """to_world for a section across the roof (a = u) swept along it (b = v)."""
    return lambda a, b, z: _world(frame, a, b, z)


def _across_ridge(frame):
    """to_world for a section along the ridge (a = v) swept across it (b = u)."""
    return lambda a, b, z: _world(frame, b, a, z)


def roof_section(frame, roof):
    """The roof slab across: the underside from eave to eave (past the
    walls by the overhang), then back along the top, the thickness above
    it measured square to each slope."""
    under = _dedupe(_extended(frame, roof.eave_overhang))
    top = _offset_up(under, roof.thickness)
    return under + list(reversed(top))


WING_REACH = 100.0          # m: a part-house roof's trim runs out this far
                            # over the wings, at its eaves' height


def trim_section(frame):
    """Everything above the roof's underside, well past the house. A
    roof over only part of the house (a custom footprint) trims the rest
    level with its eaves rather than down its slope: the wings' walls
    stop at the eaves, and their own cross gables keep their insides."""
    if frame.get('custom'):
        under = _dedupe([(frame['u0'] - WING_REACH, frame['plate'])] + list(frame['under'])
                        + [(frame['u1'] + WING_REACH, frame['plate'])])
    else:
        under = _dedupe(_extended(frame, CUTTER_REACH))
    top = frame['ridge_z'] + CUTTER_HEIGHT
    return under + [(under[-1][0], top), (under[0][0], top)]


def top_volume_section(frame, roof):
    """Everything under the roof's top surface, well past the house - what
    a dormer roof is cut back to, so it stops where it meets the roof."""
    surface = _offset_up(_dedupe(_extended(frame, CUTTER_REACH)), roof.thickness)
    bottom = frame['plate'] - CUTTER_HEIGHT
    return [(surface[0][0], bottom), (surface[-1][0], bottom)] + list(reversed(surface))


# =============================================================================
# DORMERS
# =============================================================================

def _parallel(seg, ridge_dir, tol=1e-3):
    return abs(seg.dir[0] * ridge_dir[1] - seg.dir[1] * ridge_dir[0]) < tol


def find_dormers(scene, level, frame):
    """The bump-outs under a roof that become dormers.

    A dormer front is an exterior wall along the ridge whose ends both
    join (in a corner) a wall square to the ridge - a cheek - whose other
    end joins a wall along the ridge nearer the middle of the house: the
    side wall the bump-out comes out of. Returns dicts with the front
    wall's name, the dormer's span along the ridge (outside faces of the
    cheeks), its front (outside face of the front wall), and which side
    of the ridge it is on (+1 / -1 in u)."""
    from .operators import walls
    from . import hb_wall_graph
    ridge_dir = (1.0, 0.0) if frame['along_x'] else (0.0, 1.0)
    out = []
    for upper in _levels_under(scene, frame):
        objs, segs = walls.level_wall_segs(scene, upper.uid)
        segs = [s for s in segs if s.wall_type == 'Exterior']
        graph = hb_wall_graph.build_graph(segs)
        by_id = graph.segs
        uc = frame['uc']

        def across(seg):
            """Signed distance of the wall's middle from the ridge line."""
            mid = ((seg.start[0] + seg.end[0]) / 2, (seg.start[1] + seg.end[1]) / 2)
            return _uv(frame, mid)[0] - uc

        def other_end(seg_id, which):
            node = graph.node_of.get((seg_id, which))
            if node is None or len(node.ends) != 2:
                return None
            return next(e for e in node.ends if e != (seg_id, which))

        for front in by_id.values():
            if not _parallel(front, ridge_dir):
                continue
            ok = True
            for which in (hb_wall_graph.START, hb_wall_graph.END):
                cheek_end = other_end(front.id, which)
                if cheek_end is None or _parallel(by_id[cheek_end[0]], ridge_dir):
                    ok = False
                    break
                cheek = by_id[cheek_end[0]]
                # A dormer's cheeks are short: a bump-out, not a wing
                if cheek.length > frame['half'] * 0.5:
                    ok = False
                    break
                far = hb_wall_graph.END if cheek_end[1] == hb_wall_graph.START else hb_wall_graph.START
                side_end = other_end(cheek.id, far)
                if side_end is None:
                    ok = False
                    break
                side = by_id[side_end[0]]
                # The side wall it comes out of is on the same side of the
                # ridge, nearer the middle
                a_side, a_front = across(side), across(front)
                if (not _parallel(side, ridge_dir) or a_side * a_front <= 0
                        or abs(a_side) >= abs(a_front) - 0.01):
                    ok = False
                    break
            if not ok:
                continue
            corners = walls.wall_plan_corners(objs[front.id])
            us = [_uv(frame, pt)[0] for _e, _f, pt in corners]
            vs = [_uv(frame, pt)[1] for _e, _f, pt in corners]
            sign = 1.0 if (sum(us) / len(us)) > uc else -1.0
            u_front = max(us) if sign > 0 else min(us)
            out.append({'front': front.id, 'level': upper,
                        'v0': min(vs), 'v1': max(vs),
                        'u_front': u_front, 'sign': sign})
    return out


def dormer_dims(dormer, roof):
    """Plate, ridge (underside) and the pieces of a dormer's gable. A
    roof piece carries its own pitch and plate; a dormer found from the
    walls takes the roof's dormer settings."""
    v0, v1 = dormer['v0'], dormer['v1']
    vc, half = (v0 + v1) / 2.0, (v1 - v0) / 2.0
    p = dormer.get('pitch', roof.dormer_pitch) / 12.0
    plate = dormer.get('plate', dormer['level'].elevation + roof.dormer_wall_height)
    return vc, half, p, plate, plate + half * p


def piece_dormers(frame, roof, level):
    """The roof's pieces as dormer descriptions: (cross gables, sheds).
    Each faces out from the ridge on its rectangle's far edge."""
    cross, sheds = [], []
    for index, piece in enumerate(roof.pieces):
        if frame['along_x']:
            v0, v1, ua, ub = piece.x0, piece.x1, piece.y0, piece.y1
        else:
            v0, v1, ua, ub = piece.y0, piece.y1, piece.x0, piece.x1
        v0, v1 = sorted((v0, v1))
        ua, ub = sorted((ua, ub))
        if v1 - v0 < 0.1:
            continue
        s, u_front = (-1, ua) if (ua + ub) / 2.0 < frame['uc'] else (1, ub)
        d = {'v0': v0, 'v1': v1, 'sign': s, 'u_front': u_front, 'level': level,
             'pitch': piece.pitch, 'plate': level.elevation + piece.eave_height,
             'overhang': piece.overhang, 'index': index}
        (sheds if piece.kind == 'SHED' else cross).append(d)
    return cross, sheds


def _infill_prisms(frame, roof, cross):
    """The filled-in gable end of each cross gable, from its eaves up
    under its roof, just inside its front. A wall below it stops at the
    eaves; over a porch it stands on the beam."""
    to_world = _across_ridge(frame)
    out = []
    for d in cross:
        vc, _half, _p, plate, ridge = dormer_dims(d, roof)
        out.append(([(d['v0'], plate), (d['v1'], plate), (vc, ridge)],
                    d['u_front'] - d['sign'] * GABLE_INFILL, d['u_front'], to_world))
    return out


def _under_z(frame, u):
    """Height of the roof's underside at u (within the walls' outline)."""
    pts = frame['under']
    for (a, za), (b, zb) in zip(pts, pts[1:]):
        if min(a, b) - 1e-9 <= u <= max(a, b) + 1e-9 and abs(b - a) > 1e-9:
            return za + (zb - za) * (u - a) / (b - a)
    return frame['plate']


def _clip_to_frame(frame, a, b):
    """The part of plan segment a-b inside the walls' outline, as
    parameters (t0, t1) along it, or None."""
    (ua, va), (ub, vb) = _uv(frame, a), _uv(frame, b)
    t0, t1 = 0.0, 1.0
    for p0, d, lo, hi in ((ua, ub - ua, frame['u0'], frame['u1']),
                          (va, vb - va, frame['v0'], frame['v1'])):
        if abs(d) < 1e-12:
            if not lo - 1e-6 <= p0 <= hi + 1e-6:
                return None
            continue
        e0, e1 = sorted(((lo - p0) / d, (hi - p0) / d))
        t0, t1 = max(t0, e0), min(t1, e1)
    return (t0, t1) if t1 - t0 > 1e-6 else None


def _under_piece(frame, cross, point):
    """True when a plan point is under one of the roof's cross gables."""
    u, v = _uv(frame, point)
    for d in cross:
        ov = d['overhang']
        if not d['v0'] - ov <= v <= d['v1'] + ov:
            continue
        front = d['u_front'] + d['sign'] * ov
        if min(front, frame['uc']) <= u <= max(front, frame['uc']):
            return True
    return False


def _porch_infill_prisms(scene, level, frame, cross):
    """Close the roof over its porches: above each porch edge, from the
    top of the porch's beam up to the roof's underside, flush with the
    edge. At the roof's gable end this carries the gable across the
    porch; along an eave it fills the band between beam and roof. A
    porch under a cross gable of its own is closed by that gable."""
    from . import hb_porches, hb_rooms, hb_wall_graph
    from .operators import walls
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    areas = [a for a in hb_wall_graph.find_rooms(segs) if hb_porches.is_porch_area(a)]
    out = []
    for room in level.rooms:
        if not room.is_porch or room.orphaned or room.marker is None:
            continue
        mark = (room.marker.location.x, room.marker.location.y)
        area = next((a for a in areas if hb_wall_graph.point_in_polygon(mark, a.polygon)), None)
        if area is None:
            continue
        z_beam = level.elevation + hb_rooms.room_height(room, level)
        for a, b, n in hb_porches.porch_edges(area.polygon, segs):
            span = _clip_to_frame(frame, a, b)
            if span is None:
                continue
            d = (b[0] - a[0], b[1] - a[1])
            p0 = (a[0] + d[0] * span[0], a[1] + d[1] * span[0])
            p1 = (a[0] + d[0] * span[1], a[1] + d[1] * span[1])
            mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
            if _under_piece(frame, cross, mid):
                continue
            length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
            # The underside's bends between the two ends, along the edge
            u_start, u_end = _uv(frame, p0)[0], _uv(frame, p1)[0]
            ts = {0.0, length}
            if abs(u_end - u_start) > 1e-9:
                for u, _z in frame['under']:
                    t = (u - u_start) / (u_end - u_start) * length
                    if 1e-6 < t < length - 1e-6:
                        ts.add(t)
            tops = []
            for t in sorted(ts, reverse=True):
                u = u_start + (u_end - u_start) * t / length
                tops.append((t, max(_under_z(frame, u), z_beam)))
            if max(z for _t, z in tops) - z_beam < 0.01:
                continue
            section = _dedupe([(0.0, z_beam), (length, z_beam)] + tops)
            to_world = (lambda p0, ux, uy, n: lambda s, w, z: (
                p0[0] + ux * s + n[0] * w, p0[1] + uy * s + n[1] * w, z))(p0, ux, uy, n)
            out.append((section, 0.0, GABLE_INFILL, to_world))
    return out


def _shed_prisms(frame, roof, sheds):
    """Shed dormers: (roofs, walls). The roof slopes up from over the
    front wall into the main roof; the front wall and cheeks rise from
    below the roof and are cut back to it, like the roof's own end."""
    along, across = _along_ridge(frame), _across_ridge(frame)
    roofs, walls = [], []
    for d in sheds:
        p, ov, s = d['pitch'] / 12.0, d['overhang'], d['sign']
        uf, plate, ub = d['u_front'], d['plate'], frame['uc']
        tv = roof.thickness / math.cos(math.atan(p))
        rise = abs(ub - uf) * p
        uf_o, z_o = uf + s * ov, plate - ov * p
        roofs.append(([(uf_o, z_o), (ub, plate + rise), (ub, plate + rise + tv), (uf_o, z_o + tv)],
                      d['v0'] - ov, d['v1'] + ov, along))
        low = d['level'].elevation
        # The front is a wall of its own (see _shed_front_wall); these are
        # the cheeks either side, behind it
        cheek = [(uf, low), (uf, plate), (ub, plate + rise), (ub, low)]
        walls.append((cheek, d['v0'], d['v0'] + DORMER_WALL, along))
        walls.append((cheek, d['v1'] - DORMER_WALL, d['v1'], along))
    return roofs, walls


DORMER_WALL_TYPE = 'Dormer'
FRONT_SINK = 0.1            # a dormer front starts this far down in the roof


def _delete_tree(obj):
    """Delete an object and everything parented under it (a wall's
    windows, their cutters and labels)."""
    for child in list(obj.children):
        _delete_tree(child)
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and data.users == 0:
        for pool in (bpy.data.meshes, bpy.data.curves):
            if data.name in pool and pool[data.name] == data:
                pool.remove(data)
                break


ROOF_HIDDEN_KEY = 'HB_HIDDEN_WITH_ROOF'


def _set_tree_hidden(obj, hide):
    """Hide or show a dormer front and what hangs off it (its windows).
    Showing brings back only what hiding hid: a window's cutters stay
    hidden as they always are."""
    for o in [obj] + list(obj.children_recursive):
        if hide:
            if not o.hide_viewport:
                o[ROOF_HIDDEN_KEY] = True
                o.hide_viewport = True
        elif o.get(ROOF_HIDDEN_KEY):
            del o[ROOF_HIDDEN_KEY]
            o.hide_viewport = False


def _wall_inputs_like(scene, level, wall_obj):
    """Give a roof-made wall the colour and surfaces of the level's walls."""
    from . import hb_types
    model = next((o for o in _exterior_walls(scene, level)), None)
    if model is None:
        return
    src, dst = hb_types.GeoNodeWall(model), hb_types.GeoNodeWall(wall_obj)
    for name in ('Top Surface', 'Bottom Surface', 'Inside Face', 'Outside Face',
                 'Left Edge', 'Right Edge'):
        try:
            if src.has_input(name):
                dst.set_input(name, src.get_input(name))
        except Exception:
            pass
    wall_obj.color = model.color


def _shed_front_wall(scene, level, frame, roof, piece, d):
    """Make or move a shed dormer's front wall: a GeoNodeWall standing in
    the roof at the dormer's front, its thickness inward, up to the
    dormer's eaves. It is tagged as a dormer front, so rooms, corners and
    the roof's trim leave it alone; windows placed in it stay with it."""
    from . import hb_types
    wall_obj = piece.front_wall
    if wall_obj is None or wall_obj.name not in scene.objects:
        wall = hb_types.GeoNodeWall()
        wall.create("Dormer Front")
        wall.obj['WALL_TYPE'] = DORMER_WALL_TYPE
        wall.obj['IS_DORMER_FRONT'] = True
        hb_house.assign_wall_to_level(wall.obj, level, scene)
        piece.front_wall = wall.obj
        wall_obj = wall.obj
    wall = hb_types.GeoNodeWall(wall_obj)
    s, uf = d['sign'], d['u_front']
    inward = (0.0, -s) if frame['along_x'] else (-s, 0.0)
    direction = (inward[1], -inward[0])      # thickness falls to its left
    p0 = _world(frame, uf, d['v0'], 0.0)
    p1 = _world(frame, uf, d['v1'], 0.0)
    forward = (p1[0] - p0[0]) * direction[0] + (p1[1] - p0[1]) * direction[1] > 0
    start = p0 if forward else p1
    base = roof_top_z(frame, roof, uf) - FRONT_SINK
    wall.set_input('Length', d['v1'] - d['v0'])
    wall.set_input('Thickness', DORMER_WALL)
    wall.set_input('Height', max(d['plate'] - base, 0.05))
    wall_obj.location = (start[0], start[1], base)
    wall_obj.rotation_euler = (0.0, 0.0, math.atan2(direction[1], direction[0]))
    _set_tree_hidden(wall_obj, not scene.hb_house.show_roofs)
    _wall_inputs_like(scene, level, wall_obj)
    wall_obj.update_tag()


def _clear_front_walls(roof, keep=()):
    """Delete the front walls of pieces that aren't shed dormers any more."""
    for i, piece in enumerate(roof.pieces):
        if i in keep or piece.front_wall is None:
            continue
        _delete_tree(piece.front_wall)
        piece.front_wall = None


def roof_top_z(frame, roof, u):
    """Height of the main roof's top surface at u."""
    surface = _offset_up(_dedupe(_extended(frame, CUTTER_REACH)), roof.thickness)
    for (a, za), (b, zb) in zip(surface, surface[1:]):
        if min(a, b) - 1e-9 <= u <= max(a, b) + 1e-9 and abs(b - a) > 1e-9:
            return za + (zb - za) * (u - a) / (b - a)
    return frame['plate']


def _dormer_prisms(frame, roof, dormers):
    """The dormer roofs, the volumes under their tops (opened in the main
    roof) and under their undersides (kept out of the trim)."""
    to_world = _across_ridge(frame)
    roofs, tops, insides = [], [], []
    for d in dormers:
        vc, half, p, plate, ridge = dormer_dims(d, roof)
        tv = roof.thickness / math.cos(math.atan(p))
        ov = d.get('overhang', roof.dormer_overhang)
        v0, v1, s = d['v0'], d['v1'], d['sign']
        front = d['u_front'] + s * ov
        back = frame['uc']
        z_eave = plate - ov * p
        roofs.append(([(v0 - ov, z_eave), (vc, ridge), (v1 + ov, z_eave),
                       (v1 + ov, z_eave + tv), (vc, ridge + tv), (v0 - ov, z_eave + tv)],
                      front, back, to_world))
        low = d['level'].elevation - 1.0
        # The main roof opens from the dormer front's outside face in: the
        # roof in front of and below the dormer stays, so the front wall
        # stands on it rather than in a hole down to the eave
        # A roof piece's gable comes down to the main roof's eaves, so the
        # main roof opens all the way out under it
        start = d['u_front'] + s * CUTTER_REACH if 'pitch' in d else d['u_front']
        tops.append(([(v0, low), (v1, low), (v1, plate + tv), (vc, ridge + tv), (v0, plate + tv)],
                     start, back, to_world))
        # The trim stays off the whole dormer, its front wall included
        reach = d['u_front'] + s * DORMER_MARGIN
        insides.append(([(v0, low), (v1, low), (v1, plate), (vc, ridge), (v0, plate)],
                        reach, back, to_world))
    return roofs, tops, insides


def _set_boolean(obj, name, operand, hole_tolerant=False):
    mod = obj.modifiers.get(name)
    if operand is None:
        if mod is not None:
            obj.modifiers.remove(mod)
        return
    if mod is None:
        mod = obj.modifiers.new(name=name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
    mod.use_hole_tolerant = hole_tolerant
    # Pieces of a roof can overlap (a porch gable in front of a wing's):
    # the exact solver needs telling, or it drops the result
    mod.use_self = True
    mod.object = operand


def _helper(scene, roof, attr, name, mesh, tag):
    """A hidden volume the Booleans cut with, kept in the house's root
    collection so hiding a level doesn't stop it cutting."""
    obj = getattr(roof, attr)
    if mesh is None:
        if obj is not None:
            _delete(obj)
            setattr(roof, attr, None)
        return None
    if obj is None:
        obj = _new_object(name, mesh, hb_house._house_root_collection(scene))
        obj[tag] = True
        obj['IS_CUTTING_OBJ'] = True
        obj.display_type = 'WIRE'
        obj.hide_render = True
        setattr(roof, attr, obj)
    else:
        _set_mesh(obj, mesh)
    obj.hide_viewport = True
    return obj


# =============================================================================
# MATERIAL AND OBJECT HELPERS
# =============================================================================

def _shingles():
    mat = bpy.data.materials.get(SHINGLE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(SHINGLE_MATERIAL)
        mat.diffuse_color = SHINGLE_COLOR
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = SHINGLE_COLOR
            bsdf.inputs["Roughness"].default_value = 0.9
    return mat


def _set_mesh(obj, mesh):
    old = obj.data
    obj.data = mesh
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)


def _new_object(name, mesh, collection):
    obj = hb_utils.new_object(name, mesh)
    collection.objects.link(obj)
    return obj


def _delete(obj):
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


# =============================================================================
# WHAT THE ROOF SHAPES
# =============================================================================

def _levels_under(scene, frame):
    """The levels inside the roof: those whose floor is at or above where
    it starts - the top of the walls it sits on, or the floor of the
    level it encloses - and the roof's own level whenever the roof comes
    down below the tops of its walls (a negative eave height), since
    then that level lives inside it too - and when no level stands above
    it under the roof: a one-storey house, whose own end walls make the
    gables."""
    start = min(frame['plate'], frame['base'])
    out = [l for l in scene.hb_house.levels if l.elevation >= start - 0.01]
    if frame['plate'] < frame['base'] - 0.01 or not out:
        own = next((l for l in scene.hb_house.levels
                    if l.uid == frame['level_uid']), None)
        if own is not None and own not in out:
            out.append(own)
    return out


def _roofs(scene):
    """(level, frame) for every enabled roof in the house."""
    out = []
    for level in scene.hb_house.levels:
        if level.roof.enabled:
            frame = roof_frame(scene, level)
            if frame is not None:
                out.append((level, frame))
    return out


def _within_roof(frame, wall_obj, d):
    """True when some of a wall's length lies inside the roof's footprint."""
    from . import hb_types
    wall = hb_types.GeoNodeWall(wall_obj)
    p = wall_obj.matrix_world.translation
    length = wall.get_input('Length')
    a = _uv(frame, (p.x, p.y))
    b = _uv(frame, (p.x + d.x * length, p.y + d.y * length))
    tol = 0.05
    return (min(a[0], b[0]) < frame['u1'] - tol and max(a[0], b[0]) > frame['u0'] + tol
            and min(a[1], b[1]) < frame['v1'] + tol and max(a[1], b[1]) > frame['v0'] - tol)


def _set_back_from_eaves(frame, wall_obj, d):
    """True when a wall running along the ridge stands inside the roof's
    outline, clear of both eave lines, rather than forming one of them."""
    from . import hb_types
    wall = hb_types.GeoNodeWall(wall_obj)
    t = wall.get_input('Thickness')
    p = wall_obj.matrix_world.translation
    normal = Vector((-d.y, d.x))            # thickness side
    ref_u = p.y if frame['along_x'] else p.x
    far_u = ref_u + t * (normal.y if frame['along_x'] else normal.x)
    lo, hi = min(ref_u, far_u), max(ref_u, far_u)
    return lo - frame['u0'] > SET_BACK_MIN and frame['u1'] - hi > SET_BACK_MIN


def gable_wall_height(scene, wall_obj, height):
    """The height an exterior wall needs under the roofs: a wall inside a
    roof that runs square to its ridge is a gable wall, raised to the
    ridge so the trim cuts it into the gable; a dormer's front wall is
    raised to the dormer's ridge. Others keep `height`."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return height
    level_uid = wall_obj.get(hb_house.LEVEL_KEY, '')
    m = wall_obj.matrix_world
    rot = m.to_euler().z
    d = Vector((math.cos(rot), math.sin(rot)))
    for level, frame in _roofs(scene):
        top = _dormer_fronts.get(level.uid, {}).get(wall_obj.name)
        if top is not None:
            height = max(height, top - m.translation.z + GABLE_MARGIN)
            continue
        under = {l.uid for l in _levels_under(scene, frame)}
        if level_uid not in under:
            continue
        if not _within_roof(frame, wall_obj, d):
            continue                    # a wing's wall, beyond this roof
        ridge_dir = Vector((1.0, 0.0)) if frame['along_x'] else Vector((0.0, 1.0))
        if abs(d.dot(ridge_dir)) > 0.01:
            # Runs along the ridge. Set back from the eaves - behind a
            # porch, say - the roof is above its top: raise it into the
            # roof like a gable wall so it closes up to the roof's
            # underside. Only where the roof sits on its own level's walls;
            # under a barn or cape roof the walls stop at the sloped ceiling.
            if (level_uid == frame['level_uid'] and level.roof.base == 'WALLS'
                    and frame['plate'] >= frame['base'] - 0.01
                    and _set_back_from_eaves(frame, wall_obj, d)):
                height = max(height, frame['ridge_z'] - m.translation.z + GABLE_MARGIN)
            continue                    # not square to the ridge
        needed = frame['ridge_z'] - m.translation.z + GABLE_MARGIN
        height = max(height, needed)
    return height


def apply_trims(scene):
    """Cut every level inside a roof with that roof's trim volume: walls
    and room ceilings. Trims of roofs that are gone come off."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    wanted = {}                     # object -> {modifier name: (cutter, sheet)}
    for level, frame in _roofs(scene):
        cutter = level.roof.cutter_obj
        if cutter is None:
            continue
        name = TRIM_PREFIX + level.name
        for upper in _levels_under(scene, frame):
            for obj in scene.objects:
                if (obj.get('IS_WALL_BP') and obj.get(hb_house.LEVEL_KEY) == upper.uid
                        and obj.get('WALL_TYPE') != DORMER_WALL_TYPE):
                    wanted.setdefault(obj, {})[name] = (cutter, False)
            for room in upper.rooms:
                if room.ceiling_obj is not None:
                    wanted.setdefault(room.ceiling_obj, {})[name] = (cutter, True)
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        keep = wanted.get(obj, {})
        for mod in list(obj.modifiers):
            if (mod.type == 'BOOLEAN' and mod.name.startswith(TRIM_PREFIX)
                    and mod.name not in keep):
                obj.modifiers.remove(mod)
        for name, (cutter, sheet) in keep.items():
            _set_boolean(obj, name, cutter, sheet)


def apply_roof_visibility(scene):
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    hide = not scene.hb_house.show_roofs
    for level in scene.hb_house.levels:
        for obj in (level.roof.roof_obj, level.roof.dormer_obj,
                    level.roof.gables_obj, level.roof.dormer_walls_obj):
            if obj is not None:
                obj.hide_viewport = hide
        if level.roof.enabled:
            for piece in level.roof.pieces:
                if piece.front_wall is not None:
                    _set_tree_hidden(piece.front_wall, hide)


# =============================================================================
# BUILDING
# =============================================================================

_PIECES = ('roof_obj', 'dormer_obj', 'cutter_obj', 'dormer_tops_obj',
           'dormer_inside_obj', 'roof_top_obj', 'gables_obj', 'dormer_walls_obj')


def _remove_roof(roof):
    for attr in _PIECES:
        obj = getattr(roof, attr)
        if obj is not None:
            _delete(obj)
            setattr(roof, attr, None)


def _update_gable_walls(scene):
    for level in scene.hb_house.levels:
        hb_house.set_exterior_wall_heights(scene, level)


def _visible_piece(scene, level, roof, attr, name, mesh):
    obj = getattr(roof, attr)
    if mesh is None:
        if obj is not None:
            _delete(obj)
            setattr(roof, attr, None)
        return None
    mesh.materials.append(roof.material or _shingles())
    if obj is None:
        obj = _new_object(name, mesh, hb_house.level_subcollection(level, 'Rooms'))
        obj[ROOF_KEY] = True
        obj[hb_house.LEVEL_KEY] = level.uid
        setattr(roof, attr, obj)
    else:
        _set_mesh(obj, mesh)
    # Solid shading coloured by object shows the object colour, not the
    # material's: give the roof the material's colour
    mat = roof.material or _shingles()
    obj.color = tuple(mat.diffuse_color)
    return obj


def rebuild_roof(scene, level):
    """Build (or remove) a level's roof and everything it shapes."""
    scene = hb_house.house_scene_of(scene)
    if scene is None or level is None:
        return False
    roof = level.roof
    frame = roof_frame(scene, level) if roof.enabled else None
    if frame is None:
        _dormer_fronts.pop(level.uid, None)
        _remove_roof(roof)
        # Dormer fronts keep their windows: hidden with the roof, not deleted
        for piece in roof.pieces:
            if piece.front_wall is not None:
                _set_tree_hidden(piece.front_wall, True)
        _update_gable_walls(scene)
        apply_trims(scene)
        return False

    hb_house.ensure_level_collections(scene, level)
    dormers = find_dormers(scene, level, frame) if roof.dormers else []
    _dormer_fronts[level.uid] = {
        d['front']: dormer_dims(d, roof)[4] for d in dormers}
    # Pieces added to the roof: cross gables work like dormers found from
    # the walls; shed dormers only sit on the roof
    cross, sheds = piece_dormers(frame, roof, level)
    gabled = dormers + cross

    # The main roof, opened under the dormers
    main = _visible_piece(scene, level, roof, 'roof_obj', f"Roof - {level.name}",
                          _mesh("Roof", [(roof_section(frame, roof),
                                          frame['v0'] - roof.gable_overhang,
                                          frame['v1'] + roof.gable_overhang,
                                          _along_ridge(frame))]))
    d_roofs, d_tops, d_insides = _dormer_prisms(frame, roof, gabled)
    s_roofs, s_walls = _shed_prisms(frame, roof, sheds)
    d_roofs += s_roofs
    tops = _helper(scene, roof, 'dormer_tops_obj', f"Roof Dormer Tops - {level.name}",
                   _mesh("Roof Dormer Tops", d_tops) if gabled else None,
                   ROOF_CUTTER_KEY)
    _set_boolean(main, DORMER_CUT, tops)

    # The dormer and piece roofs, stopped where they meet the main roof
    dormer_roofs = _visible_piece(scene, level, roof, 'dormer_obj', f"Dormers - {level.name}",
                                  _mesh("Dormers", d_roofs) if d_roofs else None)
    top_volume = _helper(scene, roof, 'roof_top_obj', f"Roof Top Volume - {level.name}",
                         _mesh("Roof Top Volume", [(top_volume_section(frame, roof),
                                                    frame['v0'] - CUTTER_REACH,
                                                    frame['v1'] + CUTTER_REACH,
                                                    _along_ridge(frame))]) if d_roofs else None,
                         ROOF_CUTTER_KEY)
    if dormer_roofs is not None:
        _set_boolean(dormer_roofs, VALLEY_CUT, top_volume)

    # Cross gables' filled-in ends, and shed dormers' walls cut back to the
    # roof they stand on - both finished like the house's walls
    infill = _infill_prisms(frame, roof, cross) + _porch_infill_prisms(scene, level, frame, cross)
    gables = _visible_piece(scene, level, roof, 'gables_obj', f"Roof Gables - {level.name}",
                            _mesh("Roof Gables", infill) if infill else None)
    dormer_walls = _visible_piece(scene, level, roof, 'dormer_walls_obj',
                                  f"Dormer Walls - {level.name}",
                                  _mesh("Dormer Walls", s_walls) if s_walls else None)
    if dormer_walls is not None:
        _set_boolean(dormer_walls, VALLEY_CUT, top_volume)
    for obj in (gables, dormer_walls):
        if obj is not None:
            _wall_finish(scene, level, obj)
    for d in sheds:
        _shed_front_wall(scene, level, frame, roof, roof.pieces[d['index']], d)
    _clear_front_walls(roof, keep={d['index'] for d in sheds})

    # The trim: everything above the roof, less the inside of the dormers
    cutter = _helper(scene, roof, 'cutter_obj', f"Roof Trim - {level.name}",
                     _mesh("Roof Trim", [(trim_section(frame),
                                          frame['v0'] - CUTTER_REACH,
                                          frame['v1'] + CUTTER_REACH,
                                          _along_ridge(frame))]),
                     ROOF_CUTTER_KEY)
    inside = _helper(scene, roof, 'dormer_inside_obj', f"Roof Dormer Insides - {level.name}",
                     _mesh("Roof Dormer Insides", d_insides) if gabled else None,
                     ROOF_CUTTER_KEY)
    _set_boolean(cutter, DORMER_CUT, inside)

    apply_roof_visibility(scene)
    _update_gable_walls(scene)
    apply_trims(scene)
    # Vaulted ceilings follow the roof: remake them to its new shape
    if any(r.ceiling_style == 'VAULTED' for r in level.rooms):
        from . import hb_rooms
        hb_rooms.rebuild_level(scene, level)
    # Gable ends and dormer walls just made take the house's siding
    from . import hb_exterior
    hb_exterior.apply_exterior_finish(scene)
    return True


def _wall_finish(scene, level, obj):
    """Give a roof-made wall piece the look of the level's exterior walls."""
    wall = next((o for o in _exterior_walls(scene, level)), None)
    if wall is None:
        return
    mats = [s.material for s in wall.material_slots if s.material is not None]
    obj.data.materials.clear()          # not the shingles _visible_piece gave it
    if mats:
        obj.data.materials.append(mats[0])
    obj.color = wall.color


def rebuild_roof_of(roof):
    rebuild_roof(roof.id_data, level_of_roof(roof))


def rebuild_roofs(scene):
    """Rebuild every roof in the house (after walls changed)."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    for level in scene.hb_house.levels:
        if level.roof.enabled or level.roof.roof_obj is not None:
            rebuild_roof(scene, level)


# =============================================================================
# OPERATORS
# =============================================================================

def _selection_bounds(context):
    """Plan bounds (x0, y0, x1, y1) of the selected objects, or None."""
    xs, ys = [], []
    for obj in context.selected_objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            xs.append(p.x)
            ys.append(p.y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _selected_porch_height(context, level):
    """The ceiling of a porch whose posts are selected, or None."""
    from . import hb_rooms
    for obj in context.selected_objects:
        if obj.get('IS_PORCH_BP'):
            uid = obj.get(hb_rooms.ROOM_KEY)
            room = next((r for r in level.rooms if r.uid == uid), None)
            if room is not None:
                return hb_rooms.room_height(room, level)
    return None


# ---- Fitting a roof to the house's outline ---------------------------------------

FIT_CELL = 0.15             # m: the footprint is sampled on this grid
CORE_COVER = 0.8            # a row this full of house is part of the core
WING_STEP = 0.9             # m: a wing's depth changing more than this starts another
WING_MIN_WIDTH = 1.2        # m
WING_MIN_DEPTH = 0.45       # m


def footprint_cells(scene, level):
    """The level's footprint sampled on a grid: (x0, y0, nx, ny, filled)
    with filled[j][i] for the cell centred at (x0 + (i + .5) * FIT_CELL,
    y0 + (j + .5) * FIT_CELL). Rooms (porches left out) and the exterior
    walls round them, so it reaches the walls' outside faces."""
    from . import hb_porches
    from . import hb_wall_graph as G
    from .operators import walls
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    rooms = [a.polygon for a in G.find_rooms(segs) if not hb_porches.is_porch_area(a)]
    # Every built wall: rooms stop at walls' faces, so the walls between
    # them are footprint too
    bands = [s for s in segs if s.wall_type not in G.ROOM_ONLY_WALLS
             and s.wall_type not in G.NOT_ROOM_WALLS]
    if not rooms or not bands:
        return None
    pts = [p for poly in rooms for p in poly]
    for s in bands:
        pts += [s.start, s.end, s.face_point(s.thickness),
                (s.end[0] + s.normal[0] * s.thickness, s.end[1] + s.normal[1] * s.thickness)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    nx = max(1, int(math.ceil((x1 - x0) / FIT_CELL)))
    ny = max(1, int(math.ceil((y1 - y0) / FIT_CELL)))
    boxes = [(min(p[0] for p in poly), max(p[0] for p in poly),
              min(p[1] for p in poly), max(p[1] for p in poly), poly) for poly in rooms]
    filled = []
    for j in range(ny):
        y = y0 + (j + 0.5) * FIT_CELL
        row = []
        for i in range(nx):
            x = x0 + (i + 0.5) * FIT_CELL
            inside = any(bx0 <= x <= bx1 and by0 <= y <= by1 and G.point_in_polygon((x, y), poly)
                         for bx0, bx1, by0, by1, poly in boxes)
            if not inside:
                inside = any(hb_porches._dist_to_band((x, y), s) < 1e-6 for s in bands)
            row.append(inside)
        filled.append(row)
    return x0, y0, nx, ny, filled


def plan_roof(scene, level, along_x=None):
    """Work out a roof that follows the level's outline: the core - the
    longest band of rows that run (nearly) the house's whole length along
    the ridge - under the main roof, and each wing out the front or back
    of it under a cross gable. Returns {'along_x', 'core': (x0, y0, x1,
    y1), 'wings': [(x0, y0, x1, y1)]}, or None."""
    grid = footprint_cells(scene, level)
    if grid is None:
        return None
    gx0, gy0, nx, ny, filled = grid
    if along_x is None:
        along_x = nx >= ny
    # Work in (u across the ridge, v along it)
    nu, nv = (ny, nx) if along_x else (nx, ny)
    if along_x:
        cell = lambda u, v: filled[u][v]
    else:
        cell = lambda u, v: filled[v][u]
    cover = [sum(1 for v in range(nv) if cell(u, v)) / nv for u in range(nu)]
    best, run = None, None
    for u in range(nu + 1):
        if u < nu and cover[u] >= CORE_COVER:
            run = (run[0], u) if run else (u, u)
        elif run:
            if best is None or run[1] - run[0] > best[1] - best[0]:
                best = run
            run = None
    if best is None:
        return None
    cu0, cu1 = best
    core_v = [v for u in range(cu0, cu1 + 1) for v in range(nv) if cell(u, v)]
    cv0, cv1 = min(core_v), max(core_v)
    ou, ov = (gy0, gx0) if along_x else (gx0, gy0)

    def rect(u_lo, u_hi, v_lo, v_hi):
        """Cell ranges (inclusive) to a plan rectangle (x0, y0, x1, y1)."""
        a0, a1 = ou + u_lo * FIT_CELL, ou + (u_hi + 1) * FIT_CELL
        b0, b1 = ov + v_lo * FIT_CELL, ov + (v_hi + 1) * FIT_CELL
        return (b0, a0, b1, a1) if along_x else (a0, b0, a1, b1)

    wings = []
    for step, edge in ((-1, cu0), (1, cu1)):
        depths = []
        for v in range(nv):
            d, u = 0, edge + step
            while 0 <= u < nu and cell(u, v):
                d += 1
                u += step
            depths.append(d)
        runs, cur = [], None
        for v, d in enumerate(depths + [0]):
            if d > 0 and cur and abs(d - cur['ref']) * FIT_CELL <= WING_STEP:
                cur['v1'] = v
                cur['depth'] = max(cur['depth'], d)
            else:
                if cur:
                    runs.append(cur)
                cur = {'v0': v, 'v1': v, 'ref': d, 'depth': d} if d > 0 else None
        for r in runs:
            width = (r['v1'] - r['v0'] + 1) * FIT_CELL
            if width < WING_MIN_WIDTH or r['depth'] * FIT_CELL < WING_MIN_DEPTH:
                continue
            if step < 0:
                wings.append(rect(edge - r['depth'], edge - 1, r['v0'], r['v1']))
            else:
                wings.append(rect(edge + 1, edge + r['depth'], r['v0'], r['v1']))
    return {'along_x': along_x, 'core': rect(cu0, cu1, cv0, cv1), 'wings': wings}


def fit_roof_to_outline(scene, level):
    """Set the level's roof to follow its outline: the main roof over the
    core, a cross gable over each wing. Pieces made by an earlier fit are
    replaced; ones you added stay. Returns the plan, or None."""
    roof = level.roof
    along = None if roof.ridge == 'AUTO' else roof.ridge == 'X'
    plan = plan_roof(scene, level, along)
    if plan is None:
        return None
    for i in reversed(range(len(roof.pieces))):
        if roof.pieces[i].auto:
            if roof.pieces[i].front_wall is not None:
                _delete_tree(roof.pieces[i].front_wall)
            roof.pieces.remove(i)
    x0, y0, x1, y1 = plan['core']
    roof['ridge'] = 1 if plan['along_x'] else 2
    roof['use_extents'] = True
    roof['ext_x0'], roof['ext_y0'], roof['ext_x1'], roof['ext_y1'] = x0, y0, x1, y1
    eave = hb_house.exterior_wall_height(level)
    pitch = roof.pitch if roof.style == 'GABLE' else 12.0
    for n, (wx0, wy0, wx1, wy1) in enumerate(plan['wings']):
        index = len(roof.pieces)
        piece = roof.pieces.add()
        piece['name'] = "Wing Gable %d" % (n + 1)
        piece['kind'] = 0
        piece['x0'], piece['y0'], piece['x1'], piece['y1'] = wx0, wy0, wx1, wy1
        piece['eave_height'] = eave
        piece['pitch'] = pitch
        piece['overhang'] = roof.eave_overhang
        roof.pieces[index]['auto'] = True
    roof['enabled'] = True
    rebuild_roof(scene, level)
    return plan


class HOME_BUILDER_OT_fit_roof_to_outline(bpy.types.Operator):
    bl_idname = "home_builder.fit_roof_to_outline"
    bl_label = "Fit Roof to Outline"
    bl_description = ("Fit the active level's roof to the house's outline: the main roof "
                      "over the core, a cross gable over each wing out the front or back")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_house.active_level(context) is not None

    def execute(self, context):
        level = hb_house.active_level(context)
        plan = fit_roof_to_outline(context.scene, level)
        if plan is None:
            self.report({'WARNING'}, "No closed rooms to fit a roof to")
            return {'CANCELLED'}
        self.report({'INFO'}, "Main roof over the core, %d wing gable(s)" % len(plan['wings']))
        return {'FINISHED'}


class HOME_BUILDER_OT_add_roof_piece(bpy.types.Operator):
    bl_idname = "home_builder.add_roof_piece"
    bl_label = "Add Roof Piece"
    bl_description = ("Add a piece to the active level's roof over the selected walls "
                      "or porch: a cross gable, or a shed dormer on the roof's slope")
    bl_options = {'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('GABLE', "Cross Gable", ""), ('SHED', "Shed Dormer", "")],
        default='GABLE')  # type: ignore

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        return level is not None and level.roof.enabled

    def execute(self, context):
        scene = context.scene
        level = hb_house.active_level(context)
        roof = level.roof
        frame = roof_frame(scene, level)
        bounds = _selection_bounds(context)
        if frame is None or bounds is None:
            self.report({'WARNING'}, "Select the walls or porch the roof piece goes over")
            return {'CANCELLED'}
        x0, y0, x1, y1 = bounds
        # Work in the roof's own terms - v along the ridge, u across it -
        # and store the plan rectangle
        if frame['along_x']:
            v0, v1, ua, ub = x0, x1, y0, y1
        else:
            v0, v1, ua, ub = y0, y1, x0, x1
        front_low = (ua + ub) / 2.0 < frame['uc']
        if self.kind == 'SHED':
            vc = (v0 + v1) / 2.0
            half = min((v1 - v0) / 2.0, SHED_WIDTH / 2.0)
            v0, v1 = vc - half, vc + half
            if front_low:
                ua, ub = frame['u0'] + SHED_SET_BACK, frame['uc']
                u_front = ua
            else:
                ua, ub = frame['uc'], frame['u1'] - SHED_SET_BACK
                u_front = ub
            eave = roof_top_z(frame, roof, u_front) + SHED_FRONT_RISE - level.elevation
            pitch, overhang, name = 3.0, inch(6), "Shed Dormer"
        else:
            porch = _selected_porch_height(context, level)
            eave = porch if porch is not None else hb_house.exterior_wall_height(level)
            pitch = roof.pitch if roof.style == 'GABLE' else 12.0
            overhang = roof.eave_overhang
            name = "Porch Gable" if porch is not None else "Cross Gable"
        if frame['along_x']:
            rect = (v0, ua, v1, ub)
        else:
            rect = (ua, v0, ub, v1)

        index = len(roof.pieces)
        piece = roof.pieces.add()
        # Set quietly; one rebuild once it is complete
        piece['name'] = name
        piece['kind'] = 0 if self.kind == 'GABLE' else 1
        for key, value in zip(('x0', 'y0', 'x1', 'y1'), rect):
            piece[key] = value
        piece['eave_height'] = eave
        piece['pitch'] = pitch
        piece['overhang'] = overhang
        roof.active_piece_index = index
        rebuild_roof(scene, level)
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_roof_piece(bpy.types.Operator):
    bl_idname = "home_builder.remove_roof_piece"
    bl_label = "Remove Roof Piece"
    bl_description = "Remove the active piece from the level's roof"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        return level is not None and 0 <= level.roof.active_piece_index < len(level.roof.pieces)

    def execute(self, context):
        level = hb_house.active_level(context)
        roof = level.roof
        front = roof.pieces[roof.active_piece_index].front_wall
        if front is not None:
            _delete_tree(front)
        roof.pieces.remove(roof.active_piece_index)
        roof.active_piece_index = max(0, min(roof.active_piece_index, len(roof.pieces) - 1))
        rebuild_roof(context.scene, level)
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_fit_roof_to_outline,
    HOME_BUILDER_OT_add_roof_piece,
    HOME_BUILDER_OT_remove_roof_piece,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
