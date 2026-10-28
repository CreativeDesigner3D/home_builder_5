"""Stairs: a stair's settings, how it climbs between levels, and where a
drawn one stands.

A stair is one object tagged IS_STAIR (its mesh from
operators/ops_stairs), its settings custom properties on it (STAIR_*),
read and written in the HUD through Object.hb_stair. On a house level it
climbs to the level above, its rise following the levels' heights (Rise
from Levels) - its risers counted again from its Max Riser whenever they
change - and it opens the floor above (hb_rooms' stairwells).

Its own frame: the first flight's foot at the origin, the stair as wide
as +x and climbing +y. Drawn, it is placed by one of two edges: its
start (the foot of its first flight) from the level it stands on, or its
end (the head of its last flight) from the level it climbs to.
"""

import math

import bpy
from mathutils import Matrix, Vector

from . import hb_house
from .units import inch

STAIR_KEY = 'IS_STAIR'
TYPE_ITEMS = [
    ('STRAIGHT', "Straight", "One straight flight"),
    ('L_SHAPE', "L-Shaped", "Two flights at a right angle, a landing at the turn"),
    ('U_SHAPE', "U-Shaped", "Two flights side by side, a landing across both"),
]
TURN_ITEMS = [('LEFT', "Left", "The second flight turns left"),
              ('RIGHT', "Right", "The second flight turns right")]
FROM_ITEMS = [('BOTTOM', "Bottom", "Click where the stair starts, on this level, and drag the way it climbs"),
              ('TOP', "Top", "Click where the stair arrives, on this level, and drag the way it goes down")]

WIDTH = inch(36)
MAX_RISER = inch(7.75)
TREAD = inch(10.5)
TREAD_T = inch(1)
HEADROOM = inch(80)

# What the codes (IRC R311.7) ask of a stair in a house
CODE_RISER = inch(7.75)
CODE_TREAD = inch(10)
CODE_WIDTH = inch(36)
CODE_HEADROOM = inch(80)

SNAP_SIDE = 0.3                 # a stair's side this near a wall's face goes to it
SNAP_ANGLE = math.radians(10)   # a drawn direction this near a wall's goes along it
ANGLE_STEP = math.radians(15)


def is_stair(obj):
    return obj is not None and bool(obj.get(STAIR_KEY))


def stair_of(obj):
    """The stair an object is, or belongs to (its guard), or None."""
    while obj is not None:
        if is_stair(obj):
            return obj
        obj = obj.parent
    return None


def riser_count(rise, max_riser):
    """As few risers as climb `rise` with none over `max_riser`."""
    return max(1, math.ceil(rise / max(max_riser, inch(4)) - 1e-6))


def split_flights(rise, max_riser, landing_height):
    """(risers in the first flight, in the second, the riser) for a stair
    with a landing: every riser the same, the landing on the riser nearest
    the height asked for."""
    steps = max(2, riser_count(rise, max_riser))
    riser = rise / steps
    first = min(max(round(landing_height / riser), 1), steps - 1)
    return first, steps - first, riser


# ---- A stair's numbers --------------------------------------------------------------

def values(obj):
    """A stair's settings as a dict, defaults filled in."""
    width = float(obj.get('STAIR_WIDTH', WIDTH))
    rise = float(obj.get('STAIR_TOTAL_RISE', inch(108)))
    return {
        'type': obj.get('STAIR_TYPE', 'STRAIGHT'),
        'turn': obj.get('STAIR_TURN_DIRECTION', 'LEFT'),
        'width': width,
        'rise': rise,
        'max_riser': float(obj.get('STAIR_RISER_HEIGHT', MAX_RISER)),
        'tread': float(obj.get('STAIR_TREAD_DEPTH', TREAD)),
        'tread_t': float(obj.get('STAIR_TREAD_THICKNESS', TREAD_T)),
        'landing_depth': float(obj.get('STAIR_LANDING_DEPTH', width)),
        'landing_height': float(obj.get('STAIR_LANDING_HEIGHT', rise / 2.0)),
        'gap': float(obj.get('STAIR_GAP', 0.0)),
        'headroom': float(obj.get('STAIR_HEADROOM', HEADROOM)),
    }


def counts(v):
    """(risers, riser height, run of the first flight, of the second)."""
    if v['type'] == 'STRAIGHT':
        n = riser_count(v['rise'], v['max_riser'])
        return n, v['rise'] / n, n * v['tread'], 0.0
    a, b, riser = split_flights(v['rise'], v['max_riser'], v['landing_height'])
    return a + b, riser, a * v['tread'], b * v['tread']


def ends(v):
    """The stair's two edges in its own frame, each (middle, the way up
    there): its start, at the foot of the first flight, and its end, at
    the head of the last."""
    w = v['width']
    _n, _r, run1, run2 = counts(v)
    start = (Vector((w / 2.0, 0.0)), Vector((0.0, 1.0)))
    if v['type'] == 'L_SHAPE':
        if v['turn'] == 'LEFT':
            end = (Vector((-run2, run1 + w / 2.0)), Vector((-1.0, 0.0)))
        else:
            end = (Vector((w + run2, run1 + w / 2.0)), Vector((1.0, 0.0)))
    elif v['type'] == 'U_SHAPE':
        if v['turn'] == 'LEFT':
            end = (Vector((-v['gap'] - w / 2.0, run1 - run2)), Vector((0.0, -1.0)))
        else:
            end = (Vector((1.5 * w + v['gap'], run1 - run2)), Vector((0.0, -1.0)))
    else:
        end = (Vector((w / 2.0, run1)), Vector((0.0, 1.0)))
    return start, end


def placement(v, anchor, point, up):
    """(location xy, turn) that stands the stair's `anchor` edge ('START'
    or 'END') with its middle at `point`, climbing along `up` there."""
    start, end = ends(v)
    a, d = start if anchor == 'START' else end
    turn = math.atan2(up.y, up.x) - math.atan2(d.y, d.x)
    rot = Matrix.Rotation(turn, 2)
    loc = Vector((point.x, point.y)) - rot @ a
    return loc, turn


def warnings(obj):
    """What the stair does that a house's stair shouldn't, as short notes."""
    v = values(obj)
    n, riser, _r1, _r2 = counts(v)
    out = []
    if riser > CODE_RISER + 1e-4:
        out.append("Risers over 7 3/4\"")
    if v['tread'] < CODE_TREAD - 1e-4:
        out.append("Treads under 10\"")
    if v['width'] < CODE_WIDTH - 1e-4:
        out.append("Narrower than 36\"")
    if v['headroom'] < CODE_HEADROOM - 1e-4:
        out.append("Headroom under 6'8\"")
    return out


# ---- Its levels ------------------------------------------------------------------------

def level_of(obj):
    uid = obj.get(hb_house.LEVEL_KEY, '')
    return hb_house.get_level(uid) if uid else None


def rise_for(level, scene=None):
    """How far a stair on `level` climbs: to the level above; with no
    house, the room's ceiling height."""
    if level is None:
        scene = scene or bpy.context.scene
        return scene.home_builder.ceiling_height
    from . import hb_rooms
    return hb_rooms.stair_rise(level)


def follows_levels(obj):
    return bool(obj.get('STAIR_AUTO_RISE', True)) and level_of(obj) is not None


def rebuild(obj):
    """A stair's mesh from its settings, and its opening in the floor
    above."""
    from .operators import ops_stairs
    ops_stairs.rebuild_stair_mesh(obj)
    if obj.get(hb_house.LEVEL_KEY):
        from . import hb_rooms
        hb_rooms.apply_stairwells(bpy.context.scene)


def follow_levels(scene):
    """Every stair that rises from its levels: up to the level above as it
    is now, standing on its own level's floor, its landing as far up the
    stair as it was. Returns the stairs changed."""
    changed = []
    for obj in scene.objects:
        if not is_stair(obj):
            continue
        level = level_of(obj)
        if level is None:
            continue
        moved = abs(obj.location.z - level.elevation) > 1e-5
        if moved:
            obj.location.z = level.elevation
        if follows_levels(obj):
            rise = rise_for(level)
            old = float(obj.get('STAIR_TOTAL_RISE', rise))
            if abs(rise - old) > 1e-5:
                if old > 1e-6 and 'STAIR_LANDING_HEIGHT' in obj:
                    obj['STAIR_LANDING_HEIGHT'] = float(obj['STAIR_LANDING_HEIGHT']) * rise / old
                obj['STAIR_TOTAL_RISE'] = rise
                from .operators import ops_stairs
                ops_stairs.rebuild_stair_mesh(obj)
                changed.append(obj)
                continue
        if moved:
            changed.append(obj)
    return changed


# ---- Snapping a drawn stair to walls --------------------------------------------------

def wall_faces(scene, level_uids):
    """[(a, b)] the long faces of the walls on these levels, in plan."""
    from . import hb_types
    out = []
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP') or obj.get(hb_house.LEVEL_KEY, '') not in level_uids:
            continue
        w = hb_types.GeoNodeWall(obj)
        try:
            length, t = w.get_input('Length'), w.get_input('Thickness')
        except Exception:
            continue
        m = obj.matrix_world
        for y in (0.0, t):
            a, b = m @ Vector((0.0, y, 0.0)), m @ Vector((length, y, 0.0))
            out.append((Vector((a.x, a.y)), Vector((b.x, b.y))))
    return out


def snap(point, up, width, faces):
    """A drawn stair's edge middle and its way up, put along a wall: its
    direction along a wall's that it is nearly along, near the stair, and
    its side against a wall's face it is near; else its direction to the
    nearest 15 degrees. Returns (point, up, snapped to a wall)."""
    p = Vector((point.x, point.y))
    u = Vector((up.x, up.y)).normalized()
    reach = width / 2.0 + SNAP_SIDE
    best_dir, best_d = None, None
    for a, b in faces:
        f = b - a
        if f.length < 1e-6:
            continue
        f.normalize()
        t = (p - a).dot(f)
        if t < -reach or t > (b - a).length + reach:
            continue
        d = abs((p - a).cross(f))
        if d > reach + 1.0:
            continue
        ang = math.acos(max(-1.0, min(1.0, abs(u.dot(f)))))
        if ang < SNAP_ANGLE and (best_d is None or d < best_d):
            best_dir, best_d = (f if u.dot(f) > 0 else -f), d
    on_wall = False
    if best_dir is not None:
        u = best_dir
    else:
        ang = math.atan2(u.y, u.x)
        ang = round(ang / ANGLE_STEP) * ANGLE_STEP
        u = Vector((math.cos(ang), math.sin(ang)))
    # A side against a face along the stair
    side = Vector((-u.y, u.x))
    best = None
    for a, b in faces:
        f = b - a
        if f.length < 1e-6 or abs(f.normalized().cross(u)) > 0.02:
            continue
        t = (p - a).dot(f.normalized())
        if t < -reach or t > f.length + reach:
            continue
        off = (p - a).dot(side)              # where the face is, across the stair
        gap = abs(off) - width / 2.0
        if abs(gap) < SNAP_SIDE and (best is None or abs(gap) < abs(best[0])):
            best = (gap, off)
    if best is not None:
        gap, off = best
        p = p - side * (math.copysign(gap, off))
        on_wall = True
    return p, u, on_wall


# ---- Settings in the HUD -----------------------------------------------------------

def _changed(obj):
    rebuild(obj)


def _prop(key, default, cast=float):
    def get(self):
        return cast(self.id_data.get(key, default))

    def set(self, value):
        self.id_data[key] = cast(value)
        _changed(self.id_data)
    return get, set


def _enum(key, items, default):
    ids = [i[0] for i in items]

    def get(self):
        value = self.id_data.get(key, default)
        return ids.index(value) if value in ids else 0

    def set(self, index):
        self.id_data[key] = ids[index]
        _changed(self.id_data)
    return get, set


def _get_rise(self):
    return float(self.id_data.get('STAIR_TOTAL_RISE', inch(108)))


def _set_rise(self, value):
    obj = self.id_data
    obj['STAIR_TOTAL_RISE'] = float(value)
    obj['STAIR_AUTO_RISE'] = False      # set by hand: it no longer follows the levels
    _changed(obj)


def _get_auto(self):
    return bool(self.id_data.get('STAIR_AUTO_RISE', True))


def _set_auto(self, value):
    obj = self.id_data
    obj['STAIR_AUTO_RISE'] = bool(value)
    if value:
        follow_levels(bpy.context.scene)
    _changed(obj)


_type = _enum('STAIR_TYPE', TYPE_ITEMS, 'STRAIGHT')
_turn = _enum('STAIR_TURN_DIRECTION', TURN_ITEMS, 'LEFT')
_width = _prop('STAIR_WIDTH', WIDTH)
_riser = _prop('STAIR_RISER_HEIGHT', MAX_RISER)
_tread = _prop('STAIR_TREAD_DEPTH', TREAD)
_landing_h = _prop('STAIR_LANDING_HEIGHT', inch(54))
_landing_d = _prop('STAIR_LANDING_DEPTH', WIDTH)
_gap = _prop('STAIR_GAP', 0.0)
_headroom = _prop('STAIR_HEADROOM', HEADROOM)
_guard = _prop('STAIR_GUARD', True, bool)
_guard_h = _prop('STAIR_GUARD_HEIGHT', inch(36))


class HB_Stair(bpy.types.PropertyGroup):
    """A stair's settings, read from and written to its object."""
    stair_type: bpy.props.EnumProperty(name="Type", items=TYPE_ITEMS, get=_type[0], set=_type[1])  # type: ignore
    turn: bpy.props.EnumProperty(name="Turn", items=TURN_ITEMS, get=_turn[0], set=_turn[1])  # type: ignore
    width: bpy.props.FloatProperty(name="Width", min=inch(24), max=inch(96), subtype='DISTANCE',
                                   precision=4, get=_width[0], set=_width[1])  # type: ignore
    max_riser: bpy.props.FloatProperty(
        name="Max Riser", description="The tallest a riser may be: the stair takes as few as climb its rise",
        min=inch(4), max=inch(9), subtype='DISTANCE', precision=4, get=_riser[0], set=_riser[1])  # type: ignore
    tread_depth: bpy.props.FloatProperty(name="Tread Depth", min=inch(8), max=inch(16), subtype='DISTANCE',
                                         precision=4, get=_tread[0], set=_tread[1])  # type: ignore
    auto_rise: bpy.props.BoolProperty(
        name="Rise from Levels", description="Climb to the level above, following the levels' heights",
        get=_get_auto, set=_set_auto)  # type: ignore
    total_rise: bpy.props.FloatProperty(name="Total Rise", min=inch(12), max=inch(240), subtype='DISTANCE',
                                        precision=4, get=_get_rise, set=_set_rise)  # type: ignore
    landing_height: bpy.props.FloatProperty(name="Landing Height", min=inch(7), subtype='DISTANCE',
                                            precision=4, get=_landing_h[0], set=_landing_h[1])  # type: ignore
    landing_depth: bpy.props.FloatProperty(name="Landing Depth", min=inch(24), max=inch(120), subtype='DISTANCE',
                                           precision=4, get=_landing_d[0], set=_landing_d[1])  # type: ignore
    gap: bpy.props.FloatProperty(name="Gap Between Flights", min=0.0, max=inch(48), subtype='DISTANCE',
                                 precision=4, get=_gap[0], set=_gap[1])  # type: ignore
    headroom: bpy.props.FloatProperty(
        name="Headroom", description="Clear height over the nosings: the floor above is opened wherever it would come lower",
        min=inch(60), max=inch(120), subtype='DISTANCE', precision=4, get=_headroom[0], set=_headroom[1])  # type: ignore
    guard: bpy.props.BoolProperty(name="Guard Rail", description="A rail round the opening in the floor above",
                                  get=_guard[0], set=_guard[1])  # type: ignore
    guard_height: bpy.props.FloatProperty(name="Guard Height", min=inch(30), max=inch(48), subtype='DISTANCE',
                                          precision=4, get=_guard_h[0], set=_guard_h[1])  # type: ignore


def describe(obj, unit_settings):
    """'14 risers of 7 11/16" · 11'4" run' for a stair."""
    from .units import unit_to_string
    v = values(obj)
    n, riser, run1, run2 = counts(v)
    run = run1 + run2
    return f"{n} risers of {unit_to_string(unit_settings, riser)} · {unit_to_string(unit_settings, run)} run"


def register():
    bpy.utils.register_class(HB_Stair)
    bpy.types.Object.hb_stair = bpy.props.PointerProperty(type=HB_Stair)


def unregister():
    if hasattr(bpy.types.Object, 'hb_stair'):
        del bpy.types.Object.hb_stair
    bpy.utils.unregister_class(HB_Stair)
