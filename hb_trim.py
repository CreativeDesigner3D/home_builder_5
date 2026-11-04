"""Interior trim through the house: baseboard, shoe, chair rail and crown
in every room, set per room with house defaults by the kind of room.

Each room's trim runs round its own outline - the inside faces of its
walls - so a corner is where two faces meet and the sweep mitres itself
there. A run breaks where the outline leaves a wall (a room divider), and
where an opening crosses its height: doors (and a fireplace's surround,
a bay's mouth) the base and shoe, doors and windows the chair rail,
openings up to the ceiling the crown. Built as one mesh per room, a
section swept along each run, replaced on every rebuild.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from . import hb_house, hb_types
from .units import inch

TRIM_KEY = 'IS_ROOM_TRIM'
MATERIAL_PREFIX = "HB Trim "
EPS = 1e-4
FACE_TOL = 0.01                 # an outline edge this close to a wall face is on it

BASE_T = inch(0.625)
SHOE_R = inch(0.75)
CROWN_H, CROWN_P = inch(3.5), inch(2.75)


def base_section(h):
    """(out from the wall, up) round a baseboard h tall, eased at its top."""
    return [(0.0, 0.0), (BASE_T, 0.0), (BASE_T, h - inch(0.6)), (BASE_T - inch(0.2), h - inch(0.15)),
            (inch(0.2), h), (0.0, h)]


def shoe_section():
    r = SHOE_R
    pts = [(BASE_T, 0.0), (BASE_T + r, 0.0)]
    for k in range(1, 6):
        a = math.radians(90.0 * k / 6.0)
        pts.append((BASE_T + r * math.cos(a), r * math.sin(a)))
    pts.append((BASE_T, r))
    return pts


def crown_section():
    """Hung from the ceiling: z down from it."""
    h, p = CROWN_H, CROWN_P
    return [(0.0, 0.0), (0.0, -h), (inch(0.3), -h), (inch(0.35), -h + inch(0.4)),
            (p * 0.45, -h * 0.5), (p * 0.8, -h * 0.18), (p, -inch(0.25)), (p, 0.0)]


def chair_section():
    """Its top at the rail's height."""
    return [(0.0, -inch(1.5)), (inch(0.4), -inch(1.5)), (inch(0.75), -inch(1.0)),
            (inch(0.75), -inch(0.5)), (inch(0.4), 0.0), (0.0, 0.0)]


# ---- What a room has ---------------------------------------------------------------

def room_trim(house, room):
    """{'base': height or 0, 'shoe': bool, 'chair': height or 0, 'crown':
    bool, 'color': rgb}: the room's own, or the house's for its kind."""
    if room.trim_auto:
        kind = hb_house.floor_kind(room)
        return {'base': house.trim_base_height if house.trim_base else 0.0,
                'shoe': house.trim_shoe and kind != 'garage',
                'chair': house.trim_chair_height if kind == 'room' else 0.0,
                'crown': house.trim_crown and kind == 'room',
                'color': tuple(house.trim_color)}
    return {'base': room.trim_base_height if room.trim_base else 0.0,
            'shoe': room.trim_shoe, 'chair': room.trim_chair_height,
            'crown': room.trim_crown, 'color': tuple(room.trim_color)}


def trim_material(color):
    c = tuple(round(float(v), 3) for v in color[:3])
    name = MATERIAL_PREFIX + "%02x%02x%02x" % tuple(round(v * 255) for v in c)
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = c + (1.0,)
            bsdf.inputs['Roughness'].default_value = 0.35
        mat.diffuse_color = c + (1.0,)
    return mat


# ---- The outline's edges on the walls -----------------------------------------------

def _openings(wall_obj):
    """(x0, x1, z0, z1, kind) in a wall's own space for what breaks trim on
    it: doors and windows, a fireplace across its surround, a bay's mouth."""
    out = []
    for child in wall_obj.children:
        kind = ('DOOR' if child.get('IS_ENTRY_DOOR_BP') else 'WINDOW' if child.get('IS_WINDOW_BP')
                else 'FIREPLACE' if child.get('IS_FIREPLACE_BP') else 'BAY' if child.get('IS_BAY_BP')
                else None)
        if kind is None:
            continue
        cage = hb_types.GeoNodeCage(child)
        if not cage.has_modifier():
            continue
        x0, z0 = child.location.x, child.location.z
        x1, z1 = x0 + cage.get_input('Dim X'), z0 + cage.get_input('Dim Z')
        if kind == 'FIREPLACE':
            sw = child.hb_fireplace.surround_width + inch(1.0)
            x0, x1, z0 = x0 - sw, x1 + sw, 0.0
            z1 = cage.get_input('Dim Z') + z0 + child.hb_fireplace.surround_width + inch(12)
        elif kind == 'BAY':
            z0 = 0.0
        out.append((x0, x1, z0, z1, kind))
    return out


def _edge_walls(scene, polygon, faces):
    """For each outline edge, (wall object, t at its start, t at its end)
    when it lies on a wall face the room sees, else None."""
    from .operators import walls
    segs = {}
    for name, side, t0, t1 in faces:
        obj = scene.objects.get(name)
        if obj is None:
            continue
        s = walls.wall_seg(obj)
        if s is None:
            continue
        w = 0.0 if side == 'REF' else s.thickness
        fp = s.face_point(w)
        origin = Vector((fp[0], fp[1]))
        segs.setdefault(name, []).append((obj, origin, Vector((s.dir[0], s.dir[1])), t0, t1))
    out = []
    n = len(polygon)
    for i in range(n):
        a, b = Vector(polygon[i]), Vector(polygon[(i + 1) % n])
        found = None
        for entries in segs.values():
            for obj, origin, d, t0, t1 in entries:
                ta, tb = (a - origin).dot(d), (b - origin).dot(d)
                off_a = abs((a.x - origin.x) * d.y - (a.y - origin.y) * d.x)
                off_b = abs((b.x - origin.x) * d.y - (b.y - origin.y) * d.x)
                if off_a > FACE_TOL or off_b > FACE_TOL:
                    continue
                if min(ta, tb) < t0 - FACE_TOL or max(ta, tb) > t1 + FACE_TOL:
                    continue
                found = (obj, ta, tb)
                break
            if found:
                break
        out.append(found)
    return out


def _kept(length, ta, tb, blocks):
    """The stretches [(s0, s1)] of an edge `length` long, running from t =
    ta to tb along its wall, that no block (x0, x1) on the wall covers."""
    cuts = []
    for x0, x1 in blocks:
        if abs(tb - ta) < EPS:
            continue
        s0 = (x0 - ta) / (tb - ta) * length
        s1 = (x1 - ta) / (tb - ta) * length
        s0, s1 = sorted((s0, s1))
        if s1 > EPS and s0 < length - EPS:
            cuts.append((max(s0, 0.0), min(s1, length)))
    cuts.sort()
    out, at = [], 0.0
    for s0, s1 in cuts:
        if s0 - at > 0.02:
            out.append((at, s0))
        at = max(at, s1)
    if length - at > 0.02:
        out.append((at, length))
    return out


def runs(polygon, edge_walls, blocked):
    """The outline cut into runs: [(points, normals, cyclic)] - points in
    plan, normals into the room per segment. `blocked(wall, z-test)` is
    given each edge's wall and gives the x spans to leave out."""
    n = len(polygon)
    pts = [Vector(p) for p in polygon]
    area = sum(pts[i].x * pts[(i + 1) % n].y - pts[(i + 1) % n].x * pts[i].y for i in range(n))
    pieces = []                 # (edge, s0, s1, length)
    for i in range(n):
        ew = edge_walls[i]
        if ew is None:
            continue
        a, b = pts[i], pts[(i + 1) % n]
        length = (b - a).length
        if length < 0.02:
            continue
        obj, ta, tb = ew
        for s0, s1 in _kept(length, ta, tb, blocked(obj)):
            pieces.append((i, s0, s1, length))
    if not pieces:
        return []

    def inward(i):
        a, b = pts[i], pts[(i + 1) % n]
        d = (b - a).normalized()
        return Vector((-d.y, d.x)) if area > 0 else Vector((d.y, -d.x))

    def point(i, s):
        a, b = pts[i], pts[(i + 1) % n]
        return a + (b - a).normalized() * s

    def joins(p, q):
        """Does piece q carry on from piece p round a corner?"""
        return (p[2] >= p[3] - 0.005 and q[1] <= 0.005 and q[0] == (p[0] + 1) % n)

    # Start from a piece that doesn't carry on from the one before
    m = len(pieces)
    start = next((k for k in range(m) if not joins(pieces[k - 1], pieces[k])), None)
    if start is None:
        # The whole outline, unbroken
        normals = [inward(p[0]) for p in pieces]
        return [([pts[p[0]] for p in pieces], normals, True)]
    out = []
    k = start
    for _ in range(m):
        p = pieces[k % m]
        if k == start or not joins(pieces[(k - 1) % m], p):
            run_pts, run_ns = [point(p[0], p[1])], []
            out.append((run_pts, run_ns, False))
        run_pts.append(point(p[0], p[2]))
        run_ns.append(inward(p[0]))
        k += 1
    return out


# ---- Sweeping -----------------------------------------------------------------------

def _miter(n1, n2):
    d = 1.0 + n1.dot(n2)
    if d < 1e-3:
        return n1
    return (n1 + n2) / d


def sweep(bm, points, normals, cyclic, section, z0, mat=0):
    """The section [(out, up)] swept along a run in plan at height z0,
    mitred at its corners and capped at its ends."""
    m = len(points)
    if m < 2 and not cyclic:
        return
    stations = []
    for i in range(m):
        if cyclic:
            n_in, n_out = normals[i - 1], normals[i % len(normals)]
        else:
            n_in = normals[i - 1] if i > 0 else normals[0]
            n_out = normals[i] if i < len(normals) else normals[-1]
        mv = _miter(n_in, n_out)
        p = points[i]
        stations.append([bm.verts.new((p.x + mv.x * d, p.y + mv.y * d, z0 + z)) for d, z in section])
    k = len(section)
    links = list(zip(stations, stations[1:])) + ([(stations[-1], stations[0])] if cyclic else [])
    for ra, rb in links:
        for j in range(k):
            jj = (j + 1) % k
            f = bm.faces.new((ra[j], ra[jj], rb[jj], rb[j]))
            f.material_index = mat
    if not cyclic:
        for ring in (stations[0], stations[-1]):
            bm.faces.new(ring).material_index = mat


# ---- Building ---------------------------------------------------------------------

def _clip(openings, test):
    return [(x0, x1) for x0, x1, z0, z1, kind in openings if test(z0, z1, kind)]


def build(scene, level, room, area):
    """Make or remove a room's trim."""
    from . import hb_rooms
    house = scene.hb_house
    want = house.trim_by_room and not (room.is_porch or room.outdoor or room.orphaned) and area is not None
    spec = room_trim(house, room) if want else None
    if spec is None or not (spec['base'] or spec['chair'] or spec['crown']):
        hb_rooms._remove(room.trim_obj)
        room.trim_obj = None
        return None
    edge_walls = _edge_walls(scene, area.polygon, area.faces)
    cache = {}

    def openings(wall):
        if wall.name not in cache:
            cache[wall.name] = _openings(wall)
        return cache[wall.name]

    floor = level.elevation
    ceiling = hb_rooms.room_height(room, level)
    bm = bmesh.new()
    if spec['base']:
        h = spec['base']
        rs = runs(area.polygon, edge_walls,
                  lambda w: _clip(openings(w), lambda z0, z1, kind: z0 < h or kind == 'BAY'))
        for pts, ns, cyc in rs:
            sweep(bm, pts, ns, cyc, base_section(h), floor)
            if spec['shoe']:
                sweep(bm, pts, ns, cyc, shoe_section(), floor)
    if spec['chair']:
        z = spec['chair']
        rs = runs(area.polygon, edge_walls,
                  lambda w: _clip(openings(w), lambda z0, z1, kind: z0 < z and z1 > z - inch(1.5)))
        for pts, ns, cyc in rs:
            sweep(bm, pts, ns, cyc, chair_section(), floor + z)
    if spec['crown'] and room.has_ceiling and room.ceiling_style == 'FLAT':
        rs = runs(area.polygon, edge_walls,
                  lambda w: _clip(openings(w), lambda z0, z1, kind: z1 > ceiling - CROWN_H))
        for pts, ns, cyc in rs:
            sweep(bm, pts, ns, cyc, crown_section(), floor + ceiling)
    if not bm.faces:
        bm.free()
        hb_rooms._remove(room.trim_obj)
        room.trim_obj = None
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(f"Trim - {room.name}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(trim_material(spec['color']))
    obj = room.trim_obj
    if obj is None or obj.name not in bpy.data.objects:
        obj = hb_rooms._generated(scene, level, room, f"Trim - {room.name}", mesh, (TRIM_KEY,))
        room.trim_obj = obj
    else:
        old = obj.data
        obj.data = mesh
        obj.name = f"Trim - {room.name}"
        if old is not None and old.users == 0:
            bpy.data.meshes.remove(old)
    obj.color = mesh.materials[0].diffuse_color
    return obj


def rebuild_level(scene, level):
    """Every room's trim on a level again (after doors and windows move)."""
    from . import hb_rooms
    for i in range(len(level.rooms)):
        room = level.rooms[i]
        area = hb_rooms.room_area(scene, level, room) if not room.orphaned else None
        build(scene, level, room, area)


def rebuild_all(scene):
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    for level in scene.hb_house.levels:
        rebuild_level(scene, level)


def changed(self, context):
    rebuild_all(context.scene if context else bpy.context.scene)


def refresh_for_wall(wall_obj):
    """A door or window went into (or came out of) a wall: its level's trim."""
    scene = hb_house.house_scene_of(bpy.context.scene)
    if scene is None or wall_obj is None or not scene.hb_house.trim_by_room:
        return
    level = hb_house.get_level(wall_obj.get(hb_house.LEVEL_KEY, ''))
    if level is not None:
        rebuild_level(scene, level)
