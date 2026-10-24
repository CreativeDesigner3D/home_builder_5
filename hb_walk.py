"""
Walk Through - walk around the house at eye height.

Our own first-person walk, rather than Blender's walk navigation, so it
can do what a house needs:

* Stairs climb smoothly. The eye eases up and down to the ground under
  it instead of dropping off each tread and snapping onto the next.
* Walls stop you. Short rays ahead at knee and chest height find walls
  (and closed doors, cabinets, railings) and you slide along them; an
  opening or a doorway lets you through.
* The cursor is captured. It is hidden and held at the middle of the
  viewport, so you can turn round and round without it leaving the
  window.

For the walk the house is shown the way it would be lived in: every
level visible and the ceilings on. When the walk ends those go back.

Keys: mouse to look, W A S D (or the arrows) to move, Shift to run,
wheel to change speed. Click or Enter to stop where you are; Esc or
right-click to stop and go back to the view you started from.
"""

import math

import bpy
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
                      "active level. Mouse to look, WASD to move, Shift to run, "
                      "click to stop, Esc to go back")

    @classmethod
    def poll(cls, context):
        area = context.area
        return (hb_house.active_level(context) is not None
                and area is not None and area.type == 'VIEW_3D')

    # -- setup / teardown --

    def invoke(self, context, event):
        level = hb_house.active_level(context)
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
        house = self.scene.hb_house
        self.saved_house = (house.show_ceilings, house.level_display)
        house.show_ceilings = True
        house.level_display = 'ALL'

        spot = _start_point(level, r3d.view_location)
        self.yaw = _heading(r3d)
        self.pitch = 0.0
        self.feet = Vector((spot.x, spot.y, level.elevation))
        self.fall = 0.0
        self.keys = set()
        self.run = False
        context.view_layer.update()
        ground = ground_under(self._cast, self.feet.xy, self.feet.z)
        if ground is not None:
            self.feet.z = ground
        r3d.view_perspective = 'PERSP'
        r3d.view_distance = 0.01
        self._apply_view()

        window = context.window
        self.window = window
        self.center = (self.region.x + self.region.width // 2,
                       self.region.y + self.region.height // 2)
        window.cursor_modal_set('NONE')
        window.cursor_warp(*self.center)
        self.timer = context.window_manager.event_timer_add(TICK, window=window)
        self._header(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _finish(self, context, go_back):
        context.window_manager.event_timer_remove(self.timer)
        self.window.cursor_modal_restore()
        self.area.header_text_set(None)
        house = self.scene.hb_house
        ceilings, display = self.saved_house
        if house.show_ceilings != ceilings:
            house.show_ceilings = ceilings
        if house.level_display != display:
            house.level_display = display
        if go_back:
            loc, rot, dist, persp = self.saved_view
            self.r3d.view_location = loc
            self.r3d.view_rotation = rot
            self.r3d.view_distance = dist
            self.r3d.view_perspective = persp
        self.area.tag_redraw()

    def _header(self, context):
        self.area.header_text_set(
            f"Walk Through: mouse look | WASD move | Shift run | wheel speed "
            f"({self.speed:.1f} m/s) | click/Enter stop here | Esc go back")

    # -- the world --

    def _cast(self, origin, direction, distance, with_normal=False):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        hit, loc, normal, _i, _obj, _m = self.scene.ray_cast(
            depsgraph, origin, direction, distance=distance)
        if with_normal:
            return hit, loc, normal
        return hit, loc

    def _apply_view(self):
        self.r3d.view_rotation = Euler(
            (self.pitch + math.pi / 2.0, 0.0, self.yaw - math.pi / 2.0)).to_quaternion()
        self.r3d.view_location = Vector((self.feet.x, self.feet.y,
                                         self.feet.z + self.eye_height))

    # -- events --

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            dx = event.mouse_x - self.center[0]
            dy = event.mouse_y - self.center[1]
            if dx or dy:
                self.yaw -= dx * self.sensitivity
                self.pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT,
                                                   self.pitch + dy * self.sensitivity))
                self.window.cursor_warp(*self.center)
                self._apply_view()
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
            self._finish(context, go_back=True)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _tick(self):
        dt = TICK
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


classes = (
    HOME_BUILDER_OT_walk_through,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
