"""Bath fixtures beyond the toilet and pedestal sink: an alcove tub, a
freestanding tub, a shower with its glass, and a tub-shower.

Like the toilet, each is an appliance whose model is cut to its cage at
build time (see appliance_geo), built in the cage's space: x across, the
wall at y = 0 and the front at y = -dim_y, the floor at z = 0. This
module adds its builders, defaults and types to appliance_geo's tables
when appliance_geo loads it.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from ...units import inch
from . import appliance_geo as AG

TUB_TYPES = {'ALCOVE_TUB', 'FREESTANDING_TUB', 'TUB_SHOWER'}
SHOWER_TYPES = {'SHOWER', 'TUB_SHOWER'}

TUB_H = inch(20.0)                  # a tub's rim off the floor
TUB_RIM = inch(3.0)                 # its deck round the well
TUB_FLOOR = inch(2.5)               # the well's floor off the floor
TUB_TAPER = 0.92                    # the well's floor, against its top
SPOUT_UP = inch(4.0)                # the spout, above the rim
VALVE_UP = inch(16.0)               # a tub's valve, above the rim
SHOWER_HEAD_Z = inch(78.0)
SHOWER_VALVE_Z = inch(48.0)
PAN_H = inch(3.0)
CURB_H = inch(4.5)
CURB_D = inch(4.0)
GLASS_T = inch(0.375)
GLASS_TOP = inch(4.0)               # the glass stops this far under the cage's top
DOOR_W = inch(24.0)
CHANNEL = inch(0.75)
ROD_Z = inch(4.0)                   # a curtain rod, under the cage's top
FILLER_GAP = inch(8.0)              # a freestanding tub's floor filler stands here

GLASS_ITEMS = AG.SHOWER_GLASS_ITEMS
SIDE_ITEMS = AG.DOOR_SIDE_ITEMS
ENCLOSURE_ITEMS = AG.ENCLOSURE_ITEMS


# ---- Parts --------------------------------------------------------------------------

def _water_material():
    return AG._material('Fixture Well', (0.86, 0.86, 0.85), 0.0, 0.06)


def _fabric_material():
    return AG._material('Shower Curtain', (0.90, 0.90, 0.88), 0.0, 0.85)


def _pan_material():
    return AG._material('Shower Pan', (0.88, 0.88, 0.86), 0.0, 0.3)


def _tub_shell(x0, x1, y0, y1, h, rim=TUB_RIM, floor=TUB_FLOOR):
    """An alcove tub's body: a box with the well sunk into its top, the
    well's floor a little smaller than its mouth and rounded into it."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = (v.co.z + 0.5) * h
    bm.faces.ensure_lookup_table()
    top = next(f for f in bm.faces if f.normal.z > 0.9)
    bmesh.ops.inset_individual(bm, faces=[top], thickness=min(rim, (x1 - x0) * 0.3, (y1 - y0) * 0.3))
    ret = bmesh.ops.extrude_face_region(bm, geom=[top])
    # The face the well was pulled from stays behind as a lid: open it
    bmesh.ops.delete(bm, geom=[top], context='FACES_ONLY')
    verts = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -(h - floor)), verts=verts)
    c = sum((v.co for v in verts), Vector()) / max(len(verts), 1)
    for v in verts:
        v.co.x = c.x + (v.co.x - c.x) * TUB_TAPER
        v.co.y = c.y + (v.co.y - c.y) * TUB_TAPER
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    floor_edges = list({e for v in verts for e in v.link_edges
                         if all(abs(w.co.z - floor) < 1e-6 for w in e.verts)})
    try:
        bmesh.ops.bevel(bm, geom=floor_edges, offset=inch(2.0), segments=4,
                        affect='EDGES', profile=0.5, clamp_overlap=True)
    except Exception:
        pass
    return bm


def _disc(cx, cy, z, r, t=inch(0.1)):
    return AG._oval_solid([(r, z), (r, z + t), (0.001, z + t)], cx, cy, 1.0, 1.0, 24)


def _drain_x(x0, x1, side, inset):
    return x0 + inset if side == 'LEFT' else x1 - inset


def _tub_trim(cg, x0, x1, y0, y1, h, side, metal):
    """The drain and overflow at a tub's drain end, the spout and valve on
    the wall over it."""
    cy = (y0 + y1) / 2.0
    dx = _drain_x(x0, x1, side, TUB_RIM + inch(4.0))
    AG._bm_child(cg, "Tub Drain", _disc(dx, cy, TUB_FLOOR + 0.001, inch(1.5)), metal)
    ox = _drain_x(x0, x1, side, TUB_RIM + inch(1.0))
    AG._bm_child(cg, "Tub Overflow", AG._soft_box(
        ox - inch(0.3), ox + inch(0.3), cy - inch(1.5), cy + inch(1.5),
        h - inch(5.0), h - inch(2.0), inch(0.2)), metal)
    sx = _drain_x(x0, x1, side, TUB_RIM + inch(3.0))
    AG._bm_child(cg, "Tub Spout", AG._soft_box(
        sx - inch(0.9), sx + inch(0.9), -inch(6.0), 0.0, h + SPOUT_UP, h + SPOUT_UP + inch(1.6),
        inch(0.6)), metal)
    AG._bm_child(cg, "Tub Valve", AG._oval_solid(
        [(inch(3.5), 0.0), (inch(3.3), inch(0.4)), (0.001, inch(0.5))], 0.0, 0.0, 1.0, 1.0, 24),
        metal).matrix_basis = _wall_disc(sx, h + VALVE_UP)


def _wall_disc(x, z):
    """A matrix standing a z-up disc on the wall at (x, z), facing out."""
    from mathutils import Matrix
    return Matrix.Translation((x, 0.0, z)) @ Matrix.Rotation(math.radians(90.0), 4, 'X')


def _shower_head(cg, x, z, metal):
    AG._bm_child(cg, "Shower Arm", AG._soft_box(
        x - inch(0.4), x + inch(0.4), -inch(8.0), 0.0, z - inch(0.4), z + inch(0.4), inch(0.3)), metal)
    head = AG._oval_solid([(inch(0.6), 0.0), (inch(3.0), inch(1.2)), (inch(3.0), inch(1.6)),
                           (0.001, inch(1.6))], x, -inch(8.5), 1.0, 1.0, 24)
    for v in head.verts:
        v.co.z = z - inch(0.5) - v.co.z
    bmesh.ops.recalc_face_normals(head, faces=head.faces[:])
    AG._bm_child(cg, "Shower Head", head, metal)


def _glass(cg, name, x0, x1, y0, y1, z0, z1, glass):
    if x1 - x0 > 1e-4 and y1 - y0 > 1e-4 and z1 - z0 > 1e-4:
        AG._bm_child(cg, name, AG._soft_box(x0, x1, y0, y1, z0, z1, inch(0.05)), glass, smooth=False)


def _channel(cg, name, x0, x1, y0, y1, z0, z1, metal):
    AG._bm_child(cg, name, AG._soft_box(x0, x1, y0, y1, z0, z1, inch(0.05)), metal, smooth=False)


def _front_glass(cg, opts, w, y, z0, z1, glass, metal):
    """Glass across the front at y: a panel, or a door and a panel."""
    kind = opts.get('shower_glass', 'DOOR')
    if kind == 'NONE':
        return
    side = opts.get('door_side', 'LEFT')
    door = min(DOOR_W, w * 0.5)
    open_w = min(inch(24.0), w * 0.5)
    y0, y1 = y - GLASS_T / 2.0, y + GLASS_T / 2.0
    if kind == 'PANEL':
        a, b = (open_w, w) if side == 'LEFT' else (0.0, w - open_w)
        _glass(cg, "Shower Panel", a, b, y0, y1, z0, z1, glass)
        _channel(cg, "Glass Channel", (b - CHANNEL) if side == 'LEFT' else a,
                 b if side == 'LEFT' else a + CHANNEL, y0 - inch(0.2), y1 + inch(0.2), z0, z1, metal)
        return
    # A door at the door side, a fixed panel beside it
    if side == 'LEFT':
        da, db, pa, pb = 0.0, door, door + inch(0.25), w
    else:
        da, db, pa, pb = w - door, w, 0.0, w - door - inch(0.25)
    _glass(cg, "Shower Door", da + inch(0.25), db - inch(0.25), y0, y1, z0 + inch(0.25), z1, glass)
    _glass(cg, "Shower Panel", pa, pb, y0, y1, z0, z1, glass)
    hx = db - inch(2.5) if side == 'LEFT' else da + inch(2.5)
    AG._bm_child(cg, "Door Handle", AG._soft_box(
        hx - inch(0.4), hx + inch(0.4), y0 - inch(1.6), y0 - inch(0.8),
        z0 + inch(36.0), z0 + inch(48.0), inch(0.2)), metal)
    for x in (0.0, w - CHANNEL):
        _channel(cg, "Glass Channel", x, x + CHANNEL, y0 - inch(0.2), y1 + inch(0.2), z0, z1, metal)


# ---- Builders -----------------------------------------------------------------------

def _build_alcove_tub(cage_obj, opts):
    cg = AG._Cage(cage_obj)
    w, d, h = AG._cage_dims(cg)
    china = AG._china_material()
    metal = AG._metal_material()
    th = min(h, TUB_H)
    AG._bm_child(cg, "Tub", _tub_shell(0.0, w, -d, 0.0, th), china)
    _tub_trim(cg, 0.0, w, -d, 0.0, th, opts.get('drain_side', 'LEFT'), metal)


def _build_freestanding_tub(cage_obj, opts):
    cg = AG._Cage(cage_obj)
    w, d, h = AG._cage_dims(cg)
    china = AG._china_material()
    metal = AG._metal_material()
    side = opts.get('drain_side', 'LEFT')
    length = max(w - FILLER_GAP, w * 0.6)
    x0 = FILLER_GAP if side == 'LEFT' else 0.0
    cx, cy = x0 + length / 2.0, -d / 2.0
    half = length / 2.0
    sy = (d / 2.0) / half
    rim = inch(1.25)
    profile = [(half * 0.78, 0.0), (half * 0.84, h * 0.08), (half * 0.95, h * 0.55),
               (half, h), (half - rim, h), (half - rim - inch(0.5), h * 0.55),
               (half * 0.7, TUB_FLOOR + inch(1.0)), (half * 0.55, TUB_FLOOR), (0.001, TUB_FLOOR)]
    AG._bm_child(cg, "Tub", AG._oval_solid(profile, cx, cy, 1.0, sy, 48), china)
    dx = cx - half * 0.55 if side == 'LEFT' else cx + half * 0.55
    AG._bm_child(cg, "Tub Drain", _disc(dx, cy, TUB_FLOOR + 0.001, inch(1.5)), metal)
    # A floor-mounted filler at the drain end
    fx = FILLER_GAP / 2.0 if side == 'LEFT' else w - FILLER_GAP / 2.0
    fz = h + inch(8.0)
    AG._bm_child(cg, "Tub Filler", AG._oval_solid(
        [(inch(2.0), 0.0), (inch(1.6), inch(0.6)), (inch(0.7), inch(1.2)),
         (inch(0.6), fz), (0.001, fz + inch(0.2))], fx, cy, 1.0, 1.0, 24), metal)
    reach = (dx - fx) * 0.6
    a, b = sorted((fx, fx + reach))
    AG._bm_child(cg, "Filler Spout", AG._soft_box(
        a, b, cy - inch(0.45), cy + inch(0.45), fz - inch(0.9), fz, inch(0.3)), metal)


def _build_shower(cage_obj, opts):
    cg = AG._Cage(cage_obj)
    w, d, h = AG._cage_dims(cg)
    metal = AG._metal_material()
    glass = AG._glass_material()
    pan = _pan_material()
    curb = bool(opts.get('curb', True))
    AG._bm_child(cg, "Shower Pan", AG._soft_box(0.0, w, -d, 0.0, 0.0, PAN_H, inch(0.5)), pan, smooth=False)
    z0 = PAN_H
    y = -d + inch(2.5)              # in far enough for the door's handle
    if curb:
        AG._bm_child(cg, "Shower Curb", AG._soft_box(0.0, w, -d, -d + CURB_D, 0.0, CURB_H, inch(0.5)),
                     pan, smooth=False)
        z0, y = CURB_H, -d + CURB_D / 2.0
    AG._bm_child(cg, "Shower Drain", _disc(w / 2.0, -d / 2.0, PAN_H, inch(2.0)), metal)
    z1 = h - GLASS_TOP
    _front_glass(cg, opts, w, y, z0, z1, glass, metal)
    if opts.get('shower_glass') == 'THREE':
        for x in (0.0, w - GLASS_T):
            _glass(cg, "Side Panel", x, x + GLASS_T, y + GLASS_T, 0.0, PAN_H, z1, glass)
    _shower_head(cg, w / 2.0, min(SHOWER_HEAD_Z, h - inch(1.0)), metal)
    AG._bm_child(cg, "Shower Valve", AG._oval_solid(
        [(inch(3.5), 0.0), (inch(3.3), inch(0.4)), (0.001, inch(0.5))], 0.0, 0.0, 1.0, 1.0, 24),
        metal).matrix_basis = _wall_disc(w / 2.0, SHOWER_VALVE_Z)


def _build_tub_shower(cage_obj, opts):
    cg = AG._Cage(cage_obj)
    w, d, h = AG._cage_dims(cg)
    china = AG._china_material()
    metal = AG._metal_material()
    th = min(TUB_H, h * 0.5)
    side = opts.get('drain_side', 'LEFT')
    AG._bm_child(cg, "Tub", _tub_shell(0.0, w, -d, 0.0, th), china)
    cy = -d / 2.0
    dx = _drain_x(0.0, w, side, TUB_RIM + inch(4.0))
    AG._bm_child(cg, "Tub Drain", _disc(dx, cy, TUB_FLOOR + 0.001, inch(1.5)), metal)
    sx = _drain_x(0.0, w, side, TUB_RIM + inch(3.0))
    AG._bm_child(cg, "Tub Spout", AG._soft_box(
        sx - inch(0.9), sx + inch(0.9), -inch(6.0), 0.0, th + SPOUT_UP, th + SPOUT_UP + inch(1.6),
        inch(0.6)), metal)
    AG._bm_child(cg, "Shower Valve", AG._oval_solid(
        [(inch(3.5), 0.0), (inch(3.3), inch(0.4)), (0.001, inch(0.5))], 0.0, 0.0, 1.0, 1.0, 24),
        metal).matrix_basis = _wall_disc(sx, th + inch(28.0))
    _shower_head(cg, sx, min(SHOWER_HEAD_Z, h - inch(1.0)), metal)
    enclosure = opts.get('enclosure', 'CURTAIN')
    if enclosure == 'CURTAIN':
        rz = h - ROD_Z
        ry = -d + TUB_RIM / 2.0
        AG._bm_child(cg, "Curtain Rod", AG._soft_box(
            0.0, w, ry - inch(0.5), ry + inch(0.5), rz - inch(0.5), rz + inch(0.5), inch(0.45)), metal)
        # The curtain drawn back to the far end from the shower head
        cw = w * 0.22
        a, b = (w - cw, w) if side == 'LEFT' else (0.0, cw)
        AG._bm_child(cg, "Shower Curtain", AG._soft_box(
            a, b, ry - inch(1.0), ry + inch(1.0), th + inch(6.0), rz - inch(0.5), inch(0.8)),
            _fabric_material())
    elif enclosure == 'SCREEN':
        screen = min(inch(34.0), w * 0.55)
        a, b = (0.0, screen) if side == 'LEFT' else (w - screen, w)
        y = -d + TUB_RIM / 2.0
        _glass(cg, "Shower Screen", a, b, y - GLASS_T / 2.0, y + GLASS_T / 2.0, th, h - GLASS_TOP,
               AG._glass_material())
        wall_end = 0.0 if side == 'LEFT' else w - CHANNEL
        _channel(cg, "Glass Channel", wall_end, wall_end + CHANNEL, y - inch(0.3), y + inch(0.3),
                 th, h - GLASS_TOP, metal)


# ---- Fit between walls -------------------------------------------------------------

def fit_between_walls(cage_obj):
    """Size a fixture standing against a wall to the gap between the walls
    either side of it - an alcove's ends - and move it into the gap.
    Returns the new width, or None when it isn't on a wall."""
    from ... import hb_house, hb_types, hb_wall_graph
    from ...operators import walls as hb_walls
    wall = cage_obj.parent
    if wall is None or not wall.get('IS_WALL_BP'):
        return None
    cg = AG._Cage(cage_obj)
    w, d, _h = AG._cage_dims(cg)
    flipped = abs(abs(cage_obj.rotation_euler.z) - math.pi) < 0.1
    t = hb_types.GeoNodeWall(wall).get_input('Thickness')
    ext = hb_walls.wall_face_extents(wall)
    lo, hi = ext['front' if flipped else 'back'] if ext else (0.0, hb_types.GeoNodeWall(wall).get_input('Length'))
    face_y = t if flipped else 0.0
    out = 1.0 if flipped else -1.0         # into the room
    inv = wall.matrix_world.inverted()
    x0 = cage_obj.location.x - (w if flipped else 0.0)
    mid = x0 + w / 2.0
    band = (0.01, d)
    for other in wall.users_scene[0].objects if wall.users_scene else ():
        if other is wall or not other.get('IS_WALL_BP') or not hb_house.same_level(other, wall):
            continue
        if other.get('WALL_TYPE') in hb_wall_graph.MODULE_WALL_TYPES:
            continue
        pts = []
        for _e, _f, p in hb_walls.wall_plan_corners(other):
            q = inv @ Vector((p.x, p.y, wall.matrix_world.translation.z))
            pts.append((q.x, (q.y - face_y) * out))
        if len(pts) < 4:
            continue
        poly = [pts[0], pts[1], pts[3], pts[2]]     # back start, back end, front end, front start
        xs = []
        for i in range(4):
            (ax, ao), (bx, bo) = poly[i], poly[(i + 1) % 4]
            for (px, po) in ((ax, ao),):
                if band[0] <= po <= band[1]:
                    xs.append(px)
            for edge_o in band:
                if (ao - edge_o) * (bo - edge_o) < 0:
                    xs.append(ax + (bx - ax) * (edge_o - ao) / (bo - ao))
        if not xs:
            continue
        a, b = min(xs), max(xs)
        if b <= mid:
            lo = max(lo, b)
        elif a >= mid:
            hi = min(hi, a)
    width = hi - lo
    if width < inch(12.0):
        return None
    AG._CageWrap(cage_obj).set_input('Dim X', width)
    cage_obj.location.x = hi if flipped else lo
    AG.build_geometry(cage_obj)
    return width


class HOME_BUILDER_OT_fit_fixture_between_walls(bpy.types.Operator):
    bl_idname = "home_builder.fit_fixture_between_walls"
    bl_label = "Fit Between Walls"
    bl_description = "Size the fixture to the walls either side of it, an alcove's ends"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        from ... import hb_utils
        obj = context.object
        cage = hb_utils.get_appliance_bp(obj) if obj is not None else None
        return cage is not None and AG.appliance_type(cage) in AG.FIXTURE_TYPES and cage.parent is not None

    def execute(self, context):
        from ... import hb_utils
        cage = hb_utils.get_appliance_bp(context.object)
        if fit_between_walls(cage) is None:
            self.report({'WARNING'}, "No walls either side to fit between")
            return {'CANCELLED'}
        return {'FINISHED'}


# ---- Into appliance_geo's tables --------------------------------------------------

_DEFAULTS = {
    'ALCOVE_TUB': dict(AG._COMMON_DEFAULTS, finish='WHITE', drain_side='LEFT'),
    'FREESTANDING_TUB': dict(AG._COMMON_DEFAULTS, finish='WHITE', drain_side='LEFT'),
    'SHOWER': dict(AG._COMMON_DEFAULTS, finish='WHITE', shower_glass='DOOR', door_side='LEFT', curb=True),
    'TUB_SHOWER': dict(AG._COMMON_DEFAULTS, finish='WHITE', drain_side='LEFT', enclosure='CURTAIN'),
}
_NEW_BUILDERS = {
    'ALCOVE_TUB': _build_alcove_tub,
    'FREESTANDING_TUB': _build_freestanding_tub,
    'SHOWER': _build_shower,
    'TUB_SHOWER': _build_tub_shower,
}
AG._BUILDERS.update(_NEW_BUILDERS)
AG._DEFAULTS_BY_TYPE.update(_DEFAULTS)
AG.SUPPORTED_TYPES.update(_NEW_BUILDERS)
AG.FIXTURE_TYPES.update(_NEW_BUILDERS)

classes = (HOME_BUILDER_OT_fit_fixture_between_walls,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
