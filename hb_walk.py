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
  swinging its leaf (or sliding a pocket, barn or bypass door) open.
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

Keys: mouse to look, W A S D (or the arrows) to move, Shift to run,
wheel to change speed, E to open or close a door. Click or Enter to
stop where you are; Esc or right-click to stop and go back to the view
you started from.
"""

import math
import time

import bpy
import gpu
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


def toggle_door(cage):
    """Open a closed door or close an open one. Returns True when it is
    now open."""
    geo = _door_geo()
    opts = geo.stored_opts(cage)
    if opts is None:
        return False
    full = OPEN_SWING if geo.door_type(geo.merged_opts(cage)) == 'SWING' else OPEN_SLIDE
    now_open = not is_open(cage)
    opts['open_angle'] = full if now_open else 0.0
    geo.set_opts(cage, opts)
    geo.build_geometry(cage)
    return now_open


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
        from . import hb_rooms
        self._labels_off(hb_rooms)

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
        self.last_tick = time.perf_counter()
        self.aim_handle = bpy.types.SpaceView3D.draw_handler_add(
            self._draw_aim, (), 'WINDOW', 'POST_PIXEL')
        self._header(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _finish(self, context, go_back):
        context.window_manager.event_timer_remove(self.timer)
        bpy.types.SpaceView3D.draw_handler_remove(self.aim_handle, 'WINDOW')
        self.window.cursor_modal_restore()
        self.area.header_text_set(None)
        house = self.scene.hb_house
        from . import hb_rooms
        hb_rooms.apply_label_visibility(self.scene)       # back as the house has them
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

    def _labels_off(self, hb_rooms):
        """Room labels and markers hide for the walk (the house's own
        Show Room Labels is left as it is)."""
        for level in self.scene.hb_house.levels:
            for room in level.rooms:
                for obj in (room.label_obj, room.marker):
                    if obj is not None:
                        obj.hide_viewport = True

    def _header(self, context):
        self.area.header_text_set(
            f"Walk Through: mouse look | WASD move | Shift run | wheel speed "
            f"({self.speed:.1f} m/s) | E open/close door | click/Enter stop here | "
            f"Esc go back")

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
                toggle_door(cage)
                self.area.tag_redraw()
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
        # The time since the last tick, not the timer's nominal step: a
        # tick waits for the frame before it to draw
        now = time.perf_counter()
        dt = min(max(now - self.last_tick, 0.0), MAX_STEP)
        self.last_tick = now
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
