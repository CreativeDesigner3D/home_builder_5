"""
Walk Through - walk around the house at eye height.

Our own first-person walk, rather than Blender's walk navigation, so it
can do what a house needs:

* Stairs climb smoothly. The eye eases up and down to the ground under
  it instead of dropping off each tread and snapping onto the next.
* Walls stop you. Short rays ahead at knee and chest height find walls
  (and closed doors, cabinets, railings) and you slide along them; an
  opening or a doorway lets you through. The rays pass through what
  isn't solid - door and window outlines, plan swing arcs, labels,
  room dividers and porch edges.
* Doors open. E opens or closes the door in the middle of the view,
  swinging its leaf (or sliding a pocket, barn or bypass door, rolling
  a garage door) over DOOR_SWING_TIME. E again mid-swing turns it back
  from where it is.
* The cursor is captured. It is hidden and held at the middle of the
  viewport, so you can turn round and round without it leaving the
  window.
* It keeps pace in any shading. Motion uses the real time between
  ticks, and the view is moved once a tick rather than on every mouse
  event, so Material Preview and Rendered - slower to draw than Solid -
  walk at the same speed, just at a lower frame rate.

For the walk the house is shown the way it would be lived in: every
level visible, the ceilings on, and the room labels and markers out of
the way. When the walk ends those go back.

It starts where you choose. The view stays as it is and a marker on the
floor follows the mouse: click where to stand, or click and drag to face
a way (Enter starts in the room under the middle of the view, as
before). The view then glides down to eye height there, and a card of
the keys shows for a few seconds (H brings it back). Esc glides back
out to the view you started from.

Keys: mouse to look, W A S D (or the arrows) to move, Shift to run,
wheel to change speed, E to open or close a door, H for the keys. Click
or Enter to stop where you are; Esc or right-click to stop and go back
to the view you started from.
"""

import math
import time

import blf
import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Euler, Vector

from . import hb_house, hb_wall_graph

# Body
BODY_RADIUS = 0.25          # how close you get to a wall (m)
STEP_UP = 0.45              # the highest step you can climb in one go (m)
KNEE = 0.5                  # wall rays, above the feet (m)
CHEST = 1.3
# Motion
WALK_SPEED = 1.4            # m/s
RUN_FACTOR = 2.5
CLIMB_RATE = 8.0            # how fast the eye eases onto a new floor height (1/s)
FALL_ACCEL = 9.8            # m/s2, when there is nothing just underfoot
LOOK_SENSITIVITY = 0.0025   # radians per pixel, times Blender's mouse speed
PITCH_LIMIT = math.radians(85.0)
TICK = 1.0 / 60.0
MAX_STEP = 0.1              # longest tick moved in one go (s), after a stall
# Doors
DOOR_REACH = 2.5            # how far away a door can be opened (m)
OPEN_SWING = 90.0           # degrees a hinged door opens to
OPEN_SLIDE = 100.0          # percent a pocket, barn or bypass door opens
DOOR_SWING_TIME = 0.6       # s for a door to open or close
# Starting and ending
GLIDE_TIME = 0.7            # s for the view to glide in or out
# The viewport lens while walking: 50 mm (Blender's default) frames a
# room too tight from inside it. 30 mm shows about 100 degrees across, a
# person's useful field of view, so rooms read at their real size.
WALK_LENS = 30.0
DRAG_TO_FACE = 0.3          # m of drag from the spot before it sets the facing
MARKER_RADIUS = 0.3         # m, the spot marker on the floor
CARD_TIME = 4.0             # s the keys card shows at the start
CARD_FADE = 1.0             # s it takes to fade
CARD_LINES = (
    ("Mouse", "Look around"),
    ("W A S D", "Walk"),
    ("Shift", "Run    Wheel: speed"),
    ("E", "Open or close a door"),
    ("Click", "Stop here"),
    ("Esc", "Go back"),
    ("H", "Show these keys"),
)
NAVIGATION = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE',
              'WHEELOUTMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE',
              'NDOF_MOTION', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
              'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9',
              'NUMPAD_0', 'NUMPAD_PERIOD', 'HOME'}

MOVE_KEYS = {
    'W': (0, 1), 'UP_ARROW': (0, 1),
    'S': (0, -1), 'DOWN_ARROW': (0, -1),
    'A': (-1, 0), 'LEFT_ARROW': (-1, 0),
    'D': (1, 0), 'RIGHT_ARROW': (1, 0),
}


# ---- Where to start -------------------------------------------------------------

def _ordered(points):
    """A floor's top-face vertices in order around their centre."""
    cx = sum(x for x, _y in points) / len(points)
    cy = sum(y for _x, y in points) / len(points)
    return sorted(points, key=lambda q: math.atan2(q[1] - cy, q[0] - cx))


def _start_point(level, view_center):
    """Where to stand: the view's centre if it is inside a room on the
    level, else the middle of the nearest room."""
    rooms = [r for r in level.rooms if not r.orphaned and r.marker is not None]
    p = (view_center.x, view_center.y)
    for room in rooms:
        floor = room.floor_obj
        if floor is None or floor.type != 'MESH':
            continue
        verts = [floor.matrix_world @ v.co for v in floor.data.vertices]
        if not verts:
            continue
        top = max(v.z for v in verts)
        poly = [(v.x, v.y) for v in verts if abs(v.z - top) < 1e-4]
        if len(poly) >= 3 and hb_wall_graph.point_in_polygon(p, _ordered(poly)):
            return Vector(p)
    if rooms:
        nearest = min(rooms, key=lambda r: (r.marker.location.xy - Vector(p)).length)
        return nearest.marker.location.xy.copy()
    return Vector(p)


def _heading(r3d):
    """The direction the view faces, flattened onto the floor. Looking
    straight down, it is the way the top of the screen points."""
    forward = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))
    if Vector((forward.x, forward.y)).length < 1e-3:
        forward = r3d.view_rotation @ Vector((0.0, 1.0, 0.0))
    return math.atan2(forward.y, forward.x)


# ---- What is solid ------------------------------------------------------------------

def _door_geo():
    from .product_libraries.common import door_window_geo
    return door_window_geo


def _is_opening(obj):
    return obj is not None and bool(obj.get('IS_ENTRY_DOOR_BP') or obj.get('IS_WINDOW_BP'))


def passes_through(obj):
    """True for what the walk goes through: a door or window's outline
    (its cage) and the plan drawing and cutters that hang off it, text
    and empties, and walls that only close rooms. A door's modelled leaf
    and frame, and a window's, are solid."""
    if obj is None:
        return False
    if obj.type in {'FONT', 'CURVE', 'EMPTY'}:
        return True
    if _is_opening(obj):
        return True
    if obj.get('IS_CUTTING_OBJ') or 'reveal_cutter' in obj.name:
        return True
    if obj.get('WALL_TYPE') in ('Divider', 'Porch'):
        return True
    if obj.get('IS_FRAMING'):
        return True             # framing inside the walls and floors
    if _is_opening(obj.parent) and not obj.get(_door_geo().GEO_CHILD_FLAG):
        return True             # swing annotation, label
    return False


def walk_cast(scene, origin, direction, distance, passed=None):
    """The first solid thing along a ray: (hit, location, normal, object).
    Things the walk passes through are stepped past, and listed in
    `passed` when one is given."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    d = direction.normalized()
    o = origin.copy()
    left = distance
    for _ in range(32):
        hit, loc, normal, _i, obj, _m = scene.ray_cast(depsgraph, o, d, distance=left)
        if not hit:
            break
        if obj is not None and passes_through(obj.original):
            if passed is not None:
                passed.append(obj.original)
            left -= (loc - o).length + 1e-4
            if left <= 0.0:
                break
            o = loc + d * 1e-4
            continue
        return True, loc, normal, (obj.original if obj is not None else None)
    return False, Vector(), Vector(), None


# ---- Doors --------------------------------------------------------------------------

def door_ahead(scene, eye, direction):
    """The door (its cage) in front of the eye within reach: one whose
    leaf or frame you are looking at, or else one whose opening you are
    looking through - an open door's leaf is swung out of the way. None
    for nothing, or an open doorway (it has nothing to open)."""
    passed = []
    hit, _loc, _n, obj = walk_cast(scene, eye, direction, DOOR_REACH, passed)
    while hit and obj is not None:
        if obj.get('IS_ENTRY_DOOR_BP'):
            return obj if _door_geo().stored_opts(obj) is not None else None
        obj = obj.parent
    for obj in passed:
        if obj.get('IS_ENTRY_DOOR_BP') and _door_geo().stored_opts(obj) is not None:
            return obj
    return None


def is_open(cage):
    opts = _door_geo().merged_opts(cage)
    return opts is not None and float(opts.get('open_angle', 0.0)) > 1.0


def full_open(cage):
    """How far the door opens: degrees for a hinged door, percent for the rest."""
    geo = _door_geo()
    return OPEN_SWING if geo.door_type(geo.merged_opts(cage)) == 'SWING' else OPEN_SLIDE


def door_open_amount(cage):
    opts = _door_geo().merged_opts(cage)
    return float(opts.get('open_angle', 0.0)) if opts else 0.0


def set_door_open(cage, amount):
    """Set how far a door is open and remake its leaf. Only the door's
    own geometry: the hole in the wall doesn't change, so the wall isn't
    re-cut every frame of a swing."""
    geo = _door_geo()
    opts = geo.stored_opts(cage)
    if opts is None:
        return
    opts['open_angle'] = amount
    geo.set_opts(cage, opts)
    geo.build_door_geometry(cage)


def toggle_door(cage):
    """Open a closed door or close an open one, at once. Returns True when
    it is now open."""
    if _door_geo().stored_opts(cage) is None:
        return False
    now_open = not is_open(cage)
    set_door_open(cage, full_open(cage) if now_open else 0.0)
    return now_open


def ease(f):
    """Smooth in and out over 0..1."""
    f = min(max(f, 0.0), 1.0)
    return f * f * (3.0 - 2.0 * f)


class DoorSwings:
    """Doors in the middle of opening or closing: each eases from where
    it was to fully open or shut over DOOR_SWING_TIME."""

    def __init__(self):
        self.moving = {}            # cage name -> (from, to, start time)

    def _now_amount(self, name, cage, now):
        if name in self.moving:
            a, b, t0 = self.moving[name]
            return a + (b - a) * ease((now - t0) / DOOR_SWING_TIME)
        return door_open_amount(cage)

    def toggle(self, cage, now):
        """Start a door towards open, or shut if it is open or opening.
        Returns True when it is heading open."""
        name = cage.name
        here = self._now_amount(name, cage, now)
        heading_open = (self.moving[name][1] > 0.0) if name in self.moving else here > 1.0
        target = 0.0 if heading_open else full_open(cage)
        self.moving[name] = (here, target, now)
        return target > 0.0

    def step(self, now):
        """Move every swinging door on; returns True while any moved."""
        done = []
        for name, (a, b, t0) in self.moving.items():
            cage = bpy.data.objects.get(name)
            if cage is None:
                done.append(name)
                continue
            f = (now - t0) / DOOR_SWING_TIME
            set_door_open(cage, a + (b - a) * ease(f))
            if f >= 1.0:
                done.append(name)
        for name in done:
            self.moving.pop(name, None)
        return bool(self.moving) or bool(done)

    def finish(self):
        """Put every swinging door where it was going."""
        for name, (_a, b, _t0) in self.moving.items():
            cage = bpy.data.objects.get(name)
            if cage is not None:
                set_door_open(cage, b)
        self.moving.clear()


# ---- Moving through the house ------------------------------------------------------

def ground_under(cast, xy, feet_z):
    """The floor height under a point, looking down from one step above
    the feet - so the next tread up counts as floor and a wall top or a
    ceiling above head height doesn't. None when there is nothing below."""
    hit, loc = cast(Vector((xy.x, xy.y, feet_z + STEP_UP)), Vector((0, 0, -1)), 100.0)
    return loc.z if hit else None


def slide(cast, feet, move):
    """The horizontal move that stays BODY_RADIUS off any wall: rays at
    knee and chest height along the move, and on contact the part of the
    move into the wall is dropped so you slide along it. Two passes, for
    a corner."""
    for _ in range(2):
        length = move.length
        if length < 1e-6:
            return move
        d = move / length
        here = Vector((feet.x, feet.y))
        nearest = None              # (gap square to the wall, wall normal)
        for height in (KNEE, CHEST):
            origin = Vector((feet.x, feet.y, feet.z + height))
            # Far enough to see a wall the step would bring within reach,
            # even at a glancing angle
            hit, loc, normal = cast(origin, Vector((d.x, d.y, 0.0)),
                                    length + 4.0 * BODY_RADIUS, with_normal=True)
            if not hit:
                continue
            n = Vector((normal.x, normal.y))
            if n.length < 1e-6:
                continue
            n.normalize()
            if n.dot(d) > 0:
                n = -n              # hit the back of a face: face it towards us
            gap = (here - Vector((loc.x, loc.y))).dot(n)
            if nearest is None or gap < nearest[0]:
                nearest = (gap, n)
        if nearest is None:
            return move
        gap, n = nearest
        into = -move.dot(n)         # how far this step goes towards the wall
        room = max(0.0, gap - BODY_RADIUS)
        if into <= room:
            return move
        # Close in to a body radius off the wall, then only along it
        move = move + n * (into - room)
    return move


def floor_point(origin, direction, z):
    """Where a ray from the eye meets the floor at height z, or None."""
    if abs(direction.z) < 1e-6:
        return None
    t = (z - origin.z) / direction.z
    return origin + direction * t if t > 0 else None


def facing_from_drag(spot, to, default):
    """The way to face from a spot dragged towards a point: along the
    drag, once it is long enough; else `default`."""
    if to is None:
        return default
    d = Vector((to.x - spot.x, to.y - spot.y))
    if d.length < DRAG_TO_FACE:
        return default
    return math.atan2(d.y, d.x)


def view_eye(location, rotation, distance):
    """Where a viewport's eye is: its view centre, backed off along
    its view by its distance."""
    return location + rotation @ Vector((0.0, 0.0, distance))




def glide(f, eye0, rot0, eye1, rot1):
    """The view part of the way (0..1, eased) from one eye and
    rotation to another."""
    e = ease(f)
    return eye0.lerp(eye1, e), rot0.slerp(rot1, e)


def walk_rotation(pitch, yaw):
    """The view's rotation for a pitch (up from level) and heading."""
    return Euler((pitch + math.pi / 2.0, 0.0, yaw - math.pi / 2.0)).to_quaternion()


def card_alpha(elapsed):
    """How much of the keys card shows, `elapsed` s after it came up."""
    if elapsed < CARD_TIME:
        return 1.0
    return max(0.0, 1.0 - (elapsed - CARD_TIME) / CARD_FADE)


def step_feet(feet_z, target_z, fall_speed, dt):
    """Ease the feet to the floor under them: up smoothly (stairs), down
    smoothly a step at a time, and fall when the floor is far below (off
    the top of a stairwell). Returns (feet_z, fall_speed)."""
    if target_z is None:
        return feet_z, fall_speed
    gap = target_z - feet_z
    if gap >= -STEP_UP:
        return feet_z + gap * min(1.0, dt * CLIMB_RATE), 0.0
    fall_speed += FALL_ACCEL * dt
    return max(target_z, feet_z - fall_speed * dt), fall_speed


# ---- Operator --------------------------------------------------------------------

class HOME_BUILDER_OT_walk_through(bpy.types.Operator):
    bl_idname = "home_builder.walk_through"
    bl_label = "Walk Through"
    bl_description = ("Walk around the house at eye height, starting on the "
                      "active level: click where to stand (drag to face a way). "
                      "Mouse to look, WASD to move, Shift to run, click to stop, "
                      "Esc to go back")

    @classmethod
    def poll(cls, context):
        area = context.area
        return (hb_house.active_level(context) is not None
                and area is not None and area.type == 'VIEW_3D')

    # -- setup / teardown --
    #
    # The walk goes through phases: PICK (choose where to stand), GLIDE_IN
    # (the view eases down to the eye), WALK, and GLIDE_OUT (back to the
    # view it started from, on Esc).

    def invoke(self, context, event):
        level = hb_house.active_level(context)
        self.level_uid = level.uid
        self.scene = hb_house.house_scene_of(context.scene)
        self.area = context.area
        self.region = next((r for r in self.area.regions if r.type == 'WINDOW'), context.region)
        self.r3d = self.area.spaces.active.region_3d
        prefs = context.preferences.inputs
        self.eye_height = prefs.walk_navigation.view_height
        self.sensitivity = LOOK_SENSITIVITY * max(prefs.walk_navigation.mouse_speed, 0.1)
        self.speed = WALK_SPEED

        r3d = self.r3d
        self.saved_view = (r3d.view_location.copy(), r3d.view_rotation.copy(),
                           r3d.view_distance, r3d.view_perspective)
        self.space = self.area.spaces.active
        self.saved_lens = self.space.lens
        house = self.scene.hb_house
        self.saved_house = (house.show_ceilings, house.level_display)
        self.house_changed = False

        self.phase = 'PICK'
        self.hover = None           # the floor point under the cursor
        self.spot = None            # where the click went down
        self.yaw = _heading(r3d)
        self.default_yaw = self.yaw
        self.pitch = 0.0
        self.feet = Vector((0.0, 0.0, level.elevation))
        self.fall = 0.0
        self.keys = set()
        self.run = False
        self.glide_from = self.glide_to = None
        self.glide_start = 0.0
        self.card_start = None

        window = context.window
        self.window = window
        self.center = (self.region.x + self.region.width // 2,
                       self.region.y + self.region.height // 2)
        window.cursor_modal_set('CROSSHAIR')
        self.timer = context.window_manager.event_timer_add(TICK, window=window)
        self.last_tick = time.perf_counter()
        self.doors = DoorSwings()
        self.aim_handle = bpy.types.SpaceView3D.draw_handler_add(
            self._draw, (), 'WINDOW', 'POST_PIXEL')
        self._header(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _level(self):
        return next((l for l in self.scene.hb_house.levels if l.uid == self.level_uid), None)

    def _start_walk(self, context, spot, yaw):
        """Stand at a spot facing a way: the house is shown as lived in, and
        the view starts gliding down to the eye."""
        level = self._level()
        house = self.scene.hb_house
        house.show_ceilings = True
        house.level_display = 'ALL'
        self.house_changed = True
        from . import hb_rooms
        self._labels_off(hb_rooms)
        self.yaw, self.pitch = yaw, 0.0
        self.feet = Vector((spot.x, spot.y, level.elevation if level else spot.z))
        context.view_layer.update()
        ground = ground_under(self._cast, self.feet.xy, self.feet.z)
        if ground is not None:
            self.feet.z = ground
        r3d = self.r3d
        eye0 = view_eye(r3d.view_location, r3d.view_rotation, r3d.view_distance)
        rot0 = r3d.view_rotation.copy()
        r3d.view_perspective = 'PERSP'
        r3d.view_distance = 0.01
        self.glide_from = (eye0, rot0)
        self.glide_to = (self._eye(), self._walk_rotation())
        self.glide_start = time.perf_counter()
        self.phase = 'GLIDE_IN'
        self.window.cursor_modal_set('NONE')
        self._header(context)

    def _begin_walking(self):
        self.phase = 'WALK'
        self._apply_view()
        self.window.cursor_warp(*self.center)
        self.last_tick = time.perf_counter()
        self.card_start = self.last_tick

    def _go_back(self, context):
        """Esc: glide back out to the view the walk started from."""
        loc, rot, dist, _persp = self.saved_view
        self.glide_from = (self._eye(), self.r3d.view_rotation.copy())
        self.glide_to = (view_eye(loc, rot, dist), rot.copy())
        self.glide_start = time.perf_counter()
        self.phase = 'GLIDE_OUT'
        self.doors.finish()
        self._header(context)

    def _finish(self, context, go_back):
        context.window_manager.event_timer_remove(self.timer)
        self.doors.finish()
        bpy.types.SpaceView3D.draw_handler_remove(self.aim_handle, 'WINDOW')
        self.window.cursor_modal_restore()
        self.area.header_text_set(None)
        house = self.scene.hb_house
        if self.house_changed:
            from . import hb_rooms
            hb_rooms.apply_label_visibility(self.scene)       # back as the house has them
            ceilings, display = self.saved_house
            if house.show_ceilings != ceilings:
                house.show_ceilings = ceilings
            if house.level_display != display:
                house.level_display = display
        self.space.lens = self.saved_lens
        if go_back:
            loc, rot, dist, persp = self.saved_view
            self.r3d.view_location = loc
            self.r3d.view_rotation = rot
            self.r3d.view_distance = dist
            self.r3d.view_perspective = persp
        self.area.tag_redraw()

    def _labels_off(self, hb_rooms):
        """Room labels and markers hide for the walk (the house's own
        Show Room Labels is left as it is)."""
        for level in self.scene.hb_house.levels:
            for room in level.rooms:
                for obj in (room.label_obj, room.marker):
                    if obj is not None:
                        obj.hide_viewport = True

    def _header(self, context):
        if self.phase == 'PICK':
            text = ("Walk Through: click where to stand (drag to face a way) | "
                    "Enter: start in the room in view | Esc: cancel")
        elif self.phase == 'WALK':
            text = (f"Walk Through: mouse look | WASD move | Shift run | wheel speed "
                    f"({self.speed:.1f} m/s) | E open/close door | H keys | "
                    f"click/Enter stop here | Esc go back")
        else:
            text = "Walk Through"
        self.area.header_text_set(text)

    # -- the world --

    def _cast(self, origin, direction, distance, with_normal=False):
        hit, loc, normal, _obj = walk_cast(self.scene, origin, direction, distance)
        if with_normal:
            return hit, loc, normal
        return hit, loc

    def _eye(self):
        return Vector((self.feet.x, self.feet.y, self.feet.z + self.eye_height))

    def _look(self):
        return self.r3d.view_rotation @ Vector((0.0, 0.0, -1.0))

    def _walk_rotation(self):
        return walk_rotation(self.pitch, self.yaw)

    def _apply_view(self):
        self.r3d.view_rotation = walk_rotation(self.pitch, self.yaw)
        self.r3d.view_location = Vector((self.feet.x, self.feet.y,
                                         self.feet.z + self.eye_height))

    def _floor_under_cursor(self, event):
        """The point on the level's floor under the mouse, or None."""
        level = self._level()
        if level is None:
            return None
        coord = (event.mouse_x - self.region.x, event.mouse_y - self.region.y)
        if not (0 <= coord[0] < self.region.width and 0 <= coord[1] < self.region.height):
            return None
        rv3d = self.r3d
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)
        return floor_point(origin, direction, level.elevation)

    # -- drawing --

    def _draw(self):
        if bpy.context.area != self.area:
            return
        if self.phase == 'PICK':
            self._draw_spot()
        elif self.phase == 'WALK':
            self._draw_aim()
            self._draw_card()

    def _draw_spot(self):
        """Where you'd stand, and which way you'd face: a ring on the floor
        with an arrow."""
        spot = self.spot or self.hover
        if spot is None:
            return
        rv3d = self.r3d
        to2 = lambda p: view3d_utils.location_3d_to_region_2d(self.region, rv3d, p)
        yaw = facing_from_drag(self.spot, self.hover, self.default_yaw) if self.spot else self.default_yaw
        ring = [to2(spot + Vector((math.cos(a) * MARKER_RADIUS, math.sin(a) * MARKER_RADIUS, 0.0)))
                for a in [i * math.pi / 16.0 for i in range(33)]]
        tip = spot + Vector((math.cos(yaw), math.sin(yaw), 0.0)) * MARKER_RADIUS * 2.2
        side = Vector((-math.sin(yaw), math.cos(yaw), 0.0)) * MARKER_RADIUS * 0.6
        base = spot + Vector((math.cos(yaw), math.sin(yaw), 0.0)) * MARKER_RADIUS * 1.2
        arrow = [to2(base + side), to2(tip), to2(base - side)]
        if None in ring or None in arrow:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        shader.bind()
        shader.uniform_float("color", (0.45, 0.85, 1.0, 0.35))
        batch_for_shader(shader, 'TRI_FAN', {"pos": [to2(spot)] + ring}).draw(shader)
        shader.uniform_float("color", (0.45, 0.85, 1.0, 1.0))
        batch_for_shader(shader, 'LINE_STRIP', {"pos": ring}).draw(shader)
        batch_for_shader(shader, 'TRIS', {"pos": arrow}).draw(shader)
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')

    def _draw_aim(self):
        """A small dot at the middle of the view, to aim at doors."""
        cx, cy, r = self.region.width / 2.0, self.region.height / 2.0, 3.0
        ring = [(cx + r * math.cos(a * math.pi / 6.0), cy + r * math.sin(a * math.pi / 6.0))
                for a in range(13)]
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRI_FAN', {"pos": [(cx, cy)] + ring})
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 0.8))
        batch.draw(shader)
        gpu.state.blend_set('NONE')

    def _draw_card(self):
        """The keys, low in the middle of the view, fading after a while."""
        if self.card_start is None:
            return
        alpha = card_alpha(time.perf_counter() - self.card_start)
        if alpha <= 0.0:
            return
        try:
            s = bpy.context.preferences.system.ui_scale
        except AttributeError:
            s = 1.0
        size, row, pad, gap = 13 * s, 20 * s, 12 * s, 16 * s
        blf.size(0, size)
        key_w = max(blf.dimensions(0, k)[0] for k, _t in CARD_LINES)
        text_w = max(blf.dimensions(0, t)[0] for _k, t in CARD_LINES)
        w = pad * 2 + key_w + gap + text_w
        h = pad * 2 + row * len(CARD_LINES) - (row - size)
        x = (self.region.width - w) / 2.0
        y = 60 * s
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", (0.06, 0.06, 0.07, 0.82 * alpha))
        batch_for_shader(shader, 'TRI_FAN', {"pos": [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]}).draw(shader)
        for i, (key, text) in enumerate(CARD_LINES):
            ty = y + h - pad - size - i * row
            blf.color(0, 0.55, 0.85, 1.0, alpha)
            blf.position(0, x + pad + key_w - blf.dimensions(0, key)[0], ty, 0)
            blf.draw(0, key)
            blf.color(0, 0.92, 0.92, 0.92, alpha)
            blf.position(0, x + pad + key_w + gap, ty, 0)
            blf.draw(0, text)
        gpu.state.blend_set('NONE')

    # -- events --

    def modal(self, context, event):
        if self.phase == 'PICK':
            return self._pick(context, event)
        if self.phase in ('GLIDE_IN', 'GLIDE_OUT'):
            return self._gliding(context, event)
        return self._walk(context, event)

    def _pick(self, context, event):
        if event.type in NAVIGATION:
            return {'PASS_THROUGH'}         # orbit and zoom to find the spot
        if event.type == 'MOUSEMOVE':
            self.hover = self._floor_under_cursor(event)
            self.area.tag_redraw()
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                try:
                    from .operators import viewport_hud
                    if viewport_hud.click_hits_widget(context, self.area,
                                                      event.mouse_x - self.region.x,
                                                      event.mouse_y - self.region.y):
                        return {'PASS_THROUGH'}
                except Exception:
                    pass
                self.hover = self._floor_under_cursor(event)
                self.spot = self.hover
                return {'RUNNING_MODAL'}
            if event.value == 'RELEASE' and self.spot is not None:
                self.hover = self._floor_under_cursor(event)
                yaw = facing_from_drag(self.spot, self.hover, self.default_yaw)
                self._start_walk(context, self.spot, yaw)
                return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.type in {'RET', 'NUMPAD_ENTER', 'SPACE'}:
            level = self._level()
            spot = _start_point(level, self.r3d.view_location)
            self._start_walk(context, Vector((spot.x, spot.y, level.elevation)), self.default_yaw)
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context, go_back=False)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def _gliding(self, context, event):
        if event.type == 'TIMER':
            f = (time.perf_counter() - self.glide_start) / GLIDE_TIME
            (eye0, rot0), (eye1, rot1) = self.glide_from, self.glide_to
            eye, rot = glide(f, eye0, rot0, eye1, rot1)
            self.r3d.view_rotation = rot
            self.r3d.view_location = eye
            # The lens widens on the way in and narrows on the way out
            k = min(max(f, 0.0), 1.0)
            if self.phase == 'GLIDE_OUT':
                k = 1.0 - k
            self.space.lens = self.saved_lens + (WALK_LENS - self.saved_lens) * k
            if f >= 1.0:
                if self.phase == 'GLIDE_IN':
                    self._begin_walking()
                    self._header(context)
                else:
                    self._finish(context, go_back=True)
                    return {'CANCELLED'}
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.type in {'ESC', 'RIGHTMOUSE'}:
            # Esc again: don't wait for the glide
            self._finish(context, go_back=True)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _walk(self, context, event):
        if event.type == 'MOUSEMOVE':
            dx = event.mouse_x - self.center[0]
            dy = event.mouse_y - self.center[1]
            if dx or dy:
                self.yaw -= dx * self.sensitivity
                self.pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT,
                                                   self.pitch + dy * self.sensitivity))
                self.window.cursor_warp(*self.center)
                # The view follows on the next tick: redrawing for every
                # mouse event queues up frames when drawing is slow
            return {'RUNNING_MODAL'}

        if event.type == 'TIMER':
            self._tick()
            return {'RUNNING_MODAL'}

        if event.type in MOVE_KEYS:
            if event.value == 'PRESS':
                self.keys.add(event.type)
            elif event.value == 'RELEASE':
                self.keys.discard(event.type)
            return {'RUNNING_MODAL'}

        if event.type == 'E' and event.value == 'PRESS':
            cage = door_ahead(self.scene, self._eye(), self._look())
            if cage is not None:
                self.doors.toggle(cage, time.perf_counter())
            return {'RUNNING_MODAL'}

        if event.type == 'H' and event.value == 'PRESS':
            shown = self.card_start is not None and card_alpha(time.perf_counter() - self.card_start) > 0
            self.card_start = None if shown else time.perf_counter()
            return {'RUNNING_MODAL'}

        if event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT'}:
            self.run = event.value == 'PRESS'
            return {'RUNNING_MODAL'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            factor = 1.15 if event.type == 'WHEELUPMOUSE' else 1.0 / 1.15
            self.speed = max(0.3, min(10.0, self.speed * factor))
            self._header(context)
            return {'RUNNING_MODAL'}

        if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE'}:
            self._finish(context, go_back=False)
            return {'FINISHED'}

        if event.value == 'PRESS' and event.type in {'ESC', 'RIGHTMOUSE'}:
            self._go_back(context)
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def _tick(self):
        # The time since the last tick, not the timer's nominal step: a
        # tick waits for the frame before it to draw
        now = time.perf_counter()
        dt = min(max(now - self.last_tick, 0.0), MAX_STEP)
        self.last_tick = now
        doors = getattr(self, 'doors', None)
        if doors is not None and doors.moving:
            doors.step(now)
        x = sum(MOVE_KEYS[k][0] for k in self.keys)
        y = sum(MOVE_KEYS[k][1] for k in self.keys)
        if x or y:
            forward = Vector((math.cos(self.yaw), math.sin(self.yaw)))
            right = Vector((math.sin(self.yaw), -math.cos(self.yaw)))
            wish = forward * y + right * x
            wish.normalize()
            speed = self.speed * (RUN_FACTOR if self.run else 1.0)
            move = slide(self._cast, self.feet, wish * speed * dt)
            new_xy = self.feet.xy + move
            ground = ground_under(self._cast, new_xy, self.feet.z)
            # Too high to step onto - a wall top, a counter: stay put
            if ground is None or ground - self.feet.z <= STEP_UP:
                self.feet.x, self.feet.y = new_xy.x, new_xy.y
        target = ground_under(self._cast, self.feet.xy, self.feet.z)
        self.feet.z, self.fall = step_feet(self.feet.z, target, self.fall, dt)
        self._apply_view()
        # The keys card fades on its own: keep drawing while it shows
        card = getattr(self, 'card_start', None)
        if card is not None and card_alpha(now - card) > 0:
            self.area.tag_redraw()



classes = (
    HOME_BUILDER_OT_walk_through,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
