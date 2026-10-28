"""Edit handles on a selected house wall.

Selecting a wall in a house shows three arrows on it:

* an arrow at each end, pointing out along the wall, drags that end to
  make the wall longer or shorter. Where the end turns a corner the wall
  around the corner slides over with it (and pivots, if it meets at an
  angle) so the corner stays closed; a free end just moves.
* an arrow at the middle, pointing out of the room, slides the whole
  wall sideways. The walls at its corners stretch to follow.

While an arrow is dragged, the moving corners snap into line with the
corners of the other walls on the level and a dashed tracking line shows
what they line up with. Every wall whose length the drag changes is
labelled with its new length. Hold Ctrl to drag without snapping,
Shift for fine steps; Esc or right-click puts the walls back.

The arrows are a gizmo group, so they appear with the selection and
need nothing running. A click on one starts the drag operator, which
does the moving with the same helpers as Change Room Size
(offset_wall_perpendicular and the room-loop length solve) and is one
undo step. The walls move live; the rooms they enclose are rebuilt once,
when the drag ends.
"""
import math

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .. import hb_house, hb_types, hb_wall_graph, units
from . import walls as hb_walls

SNAP_PX = 10.0               # how near a corner comes before it lines up
MIN_LENGTH = 0.1             # the shortest a drag may leave a wall (m)
DASH_PX = 6.0
FONT_SIZE = 12.0

ARROW_COLOR = (0.30, 0.62, 1.0)
ARROW_HOVER = (1.0, 0.85, 0.30)
TRACK_COLOR = (1.0, 0.55, 0.15, 0.95)
DIM_TEXT = (1.0, 1.0, 1.0, 1.0)
DIM_BG = (0.10, 0.30, 0.55, 0.92)

HANDLES = ('START', 'END', 'MIDDLE')

HINT = "Drag to move   Ctrl: no snapping   Shift: fine   Esc / right-click: cancel"


# =============================================================================
# READING A WALL
# =============================================================================

def is_house_wall(obj):
    return (obj is not None and obj.get('IS_WALL_BP')
            and obj.get('WALL_TYPE') not in hb_wall_graph.MODULE_WALL_TYPES
            and hb_types.GeoNodeWall(obj).has_modifier())


def wall_frame(obj):
    """(start, axis, length, thickness, height) of a wall in plan: start
    is its reference end, axis the unit direction to the other end."""
    wall = hb_types.GeoNodeWall(obj)
    m = obj.matrix_world
    rot = m.to_euler().z
    axis = Vector((math.cos(rot), math.sin(rot)))
    return (m.translation.to_2d(), axis, wall.get_input('Length'),
            wall.get_input('Thickness'), wall.get_input('Height'))


def neighbours(obj):
    """(walls joined at its start, at its end, chain) along the wall's
    chain - None where an end is free."""
    chain, idx, closed = hb_walls.get_wall_chain_info(obj)
    if chain is None:
        return None, None, None
    n = len(chain)
    before = chain[(idx - 1) % n] if (closed or idx > 0) else None
    after = chain[(idx + 1) % n] if (closed or idx < n - 1) else None
    if before is obj:
        before = None
    if after is obj:
        after = None
    return before, after, chain


def outward(obj):
    """The unit plan direction out of the room for a wall (its left side
    on an open run)."""
    normal, _closed = hb_walls.home_builder_walls_OT_change_room_size._compute_outward_normal(obj)
    if normal is None:
        rot = obj.matrix_world.to_euler().z
        return Vector((-math.sin(rot), math.cos(rot)))
    return normal.to_2d().normalized()


def handle_places(obj):
    """{handle: (point, direction)} in plan - where each arrow sits and
    which way it points."""
    start, axis, length, t, _h = wall_frame(obj)
    side = Vector((-axis.y, axis.x)) * (t / 2.0)
    return {
        'START': (start + side, -axis),
        'END': (start + axis * length + side, axis),
        'MIDDLE': (start + axis * (length / 2.0) + side, outward(obj)),
    }


# =============================================================================
# TRACKING
# =============================================================================

AXES = (Vector((1.0, 0.0)), Vector((0.0, 1.0)))


def track(moving, direction, t, keys, tol):
    """Line a drag up with the corners around it.

    The drag moves each of `moving` (plan points at t = 0) to p + direction
    * t. Returns (t, lines): t snapped to the nearest value within `tol`
    where a moving point lines up across or along the plan with one of
    `keys`, and the tracking lines [(key, moved point)] that hold at it."""
    best = None
    for p in moving:
        for k in keys:
            for a in AXES:
                n = Vector((-a.y, a.x))
                rate = n.dot(direction)
                if abs(rate) < 0.2:
                    continue        # moving along this axis: never lines up
                at = -n.dot(p - k) / rate
                d = abs(at - t)
                if d <= tol and (best is None or d < best):
                    best, snapped = d, at
    if best is None:
        return t, []
    t = snapped
    lines = []
    for p in moving:
        q = p + direction * t
        for a in AXES:
            n = Vector((-a.y, a.x))
            near = [k for k in keys if abs(n.dot(q - k)) < 1e-4]
            if near:
                k = min(near, key=lambda k: (k - q).length)
                if (k - q).length > 1e-4:
                    lines.append((k, q))
    return t, lines


def key_corners(obj, skip):
    """Plan corners of the other walls on obj's level, leaving out the
    walls in `skip` (the ones the drag moves)."""
    keys = []
    for other in bpy.context.scene.objects:
        if other is obj or other in skip or not other.get('IS_WALL_BP'):
            continue
        if other.get('WALL_TYPE') in hb_wall_graph.MODULE_WALL_TYPES or not hb_house.same_level(other, obj):
            continue
        keys.extend(Vector(p) for _end, _face, p in hb_walls.wall_plan_corners(other))
    return keys


# =============================================================================
# MOVING
# =============================================================================

def _solve_offset(v, n, target, sign):
    """How far to slide a neighbour (along its outward normal n) so a wall
    whose vector is v ends up `target` long. Sliding the neighbour moves
    the shared corner by d * n, which adds sign * d * n to v."""
    vn = v.dot(n) * sign
    disc = vn * vn - v.length_squared + target * target
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    d1, d2 = -vn + root, -vn - root
    return d1 if abs(d1) <= abs(d2) else d2


def set_length(obj, handle, target):
    """Make the wall `target` long by moving its START or END. Returns
    (ok, message)."""
    before, after, _chain = neighbours(obj)
    start, axis, length, _t, _h = wall_frame(obj)
    joined = before if handle == 'START' else after
    if joined is not None:
        n = outward(joined)
        v = axis * length
        if handle == 'END':
            d = _solve_offset(v, n, target, 1.0)
        else:
            d = _solve_offset(v, n, target, -1.0)
        if d is None:
            return False, "That length is out of reach of the wall around the corner"
        if abs(d) < 1e-9:
            return True, ""
        return hb_walls.offset_wall_perpendicular(joined, d)
    # A free end: the wall itself grows, its other end stays put
    scene = obj.users_scene[0] if obj.users_scene else bpy.context.scene
    tees = hb_walls.capture_tees(scene, hb_house.level_of(obj))
    hb_types.GeoNodeWall(obj).set_input('Length', target)
    if handle == 'START':
        new_start = start + axis * (length - target)
        obj.location.x, obj.location.y = new_start
    obj.update_tag()
    hb_walls.restore_tees(tees, scene)
    hb_walls.calculate_wall_miter_angles(obj)
    return True, ""


def slide(obj, offset):
    return hb_walls.offset_wall_perpendicular(obj, offset)


class Drag:
    """One drag of one handle, in plan terms: the operator feeds it the
    plan point under the cursor and draws what it reports."""

    def __init__(self, obj, handle, grab):
        self.obj = obj
        self.handle = handle
        self.snapshot = hb_walls.home_builder_walls_OT_change_room_size._snapshot_walls()
        start, axis, length, t, _h = wall_frame(obj)
        self.length0 = length
        before, after, _chain = neighbours(obj)
        corners = {(end, face): Vector(p) for end, face, p in hb_walls.wall_plan_corners(obj)}
        if handle == 'MIDDLE':
            self.direction = outward(obj)
            self.moving = list(corners.values())
            skip = {before, after}
        else:
            self.direction = axis if handle == 'END' else -axis
            which = 'end' if handle == 'END' else 'start'
            self.moving = [p for (end, _face), p in corners.items() if end == which]
            skip = {before if handle == 'START' else after}
        self.keys = key_corners(obj, skip)
        self.grab = Vector(grab)
        self.t = 0.0
        self.lines = []
        self.error = ""

    def update(self, point, tol, snap=True, step=None):
        """Move to where the cursor's plan point says. tol is the snap
        distance in metres; step rounds the move when nothing snaps."""
        t = (Vector(point) - self.grab).dot(self.direction)
        lines = []
        if snap:
            t2, lines = track(self.moving, self.direction, t, self.keys, tol)
            if not lines and step:
                if self.handle == 'MIDDLE':
                    t2 = round(t / step) * step
                else:               # whole steps of length, not of move
                    t2 = round((self.length0 + t) / step) * step - self.length0
            t = t2
        if self.handle != 'MIDDLE':
            t = max(t, MIN_LENGTH - self.length0)
        with hb_walls.rooms_held():
            self.restore()
            if abs(t) < 1e-9:
                ok, msg = True, ""
            elif self.handle == 'MIDDLE':
                ok, msg = slide(self.obj, t)
            else:
                ok, msg = set_length(self.obj, self.handle, self.length0 + t)
            if not ok:
                self.restore()
                hb_walls.calculate_wall_miter_angles(self.obj)
                self.error = msg
                return False
        self.t, self.lines, self.error = t, lines, ""
        return True

    def restore(self):
        hb_walls.home_builder_walls_OT_change_room_size._restore_walls(self.snapshot)

    def cancel(self):
        self.restore()
        hb_walls.calculate_wall_miter_angles(self.obj)

    def finish(self):
        """Rebuild the rooms the walls enclose, held back during the drag."""
        hb_walls.calculate_wall_miter_angles(self.obj)

    def changed(self):
        """[(wall, length)] for the dragged wall and every wall the drag
        has made longer or shorter."""
        out = []
        for name, state in self.snapshot.items():
            obj = bpy.data.objects.get(name)
            if obj is None:
                continue
            length = hb_types.GeoNodeWall(obj).get_input('Length')
            if obj is self.obj or abs(length - state['length']) > 1e-5:
                out.append((obj, length))
        return out


# =============================================================================
# DRAWING
# =============================================================================

def length_text(scene, value):
    us = scene.unit_settings
    if us.system == 'IMPERIAL':
        inches = round(units.meter_to_inch(value) * 4) / 4
        feet = int(inches // 12)
        rest = inches - feet * 12
        return f"{feet}' {units.format_number(rest)}\"" if feet else f"{units.format_number(rest)}\""
    return units.unit_to_string(us, value)


def _scale():
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


def _to_px(region, rv3d, p, z):
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    return location_3d_to_region_2d(region, rv3d, Vector((p[0], p[1], z)))


def _dashes(a, b):
    out = []
    d = b - a
    n = d.length
    if n < 1:
        return out
    u = d / n
    s = 0.0
    while s < n:
        out.extend((a + u * s, a + u * min(s + DASH_PX, n)))
        s += DASH_PX * 2
    return out


def _label(x, y, text):
    s = _scale()
    blf.size(0, FONT_SIZE * s)
    w, h = blf.dimensions(0, text)
    pad = 4 * s
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    x0, y0, x1, y1 = x - w / 2 - pad, y - h / 2 - pad, x + w / 2 + pad, y + h / 2 + pad
    batch = batch_for_shader(shader, 'TRIS', {"pos": [(x0, y0), (x1, y0), (x1, y1), (x0, y0), (x1, y1), (x0, y1)]})
    shader.uniform_float("color", DIM_BG)
    batch.draw(shader)
    blf.color(0, *DIM_TEXT)
    blf.position(0, x - w / 2, y - h / 2, 0)
    blf.draw(0, text)


def draw_drag(op, context):
    drag = op.drag
    if drag is None or context.region != op.region:
        return
    region, rv3d = context.region, context.region_data
    z = op.z
    gpu.state.blend_set('ALPHA')
    coords = []
    for k, q in drag.lines:
        a, b = _to_px(region, rv3d, k, z), _to_px(region, rv3d, q, z)
        if a is not None and b is not None:
            coords.extend(_dashes(a, b))
    if coords:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.line_width_set(1.5 * _scale())
        shader.uniform_float("color", TRACK_COLOR)
        batch_for_shader(shader, 'LINES', {"pos": coords}).draw(shader)
        gpu.state.line_width_set(1.0)
    scene = context.scene
    for obj, length in drag.changed():
        try:
            start, axis, _l, t, _h = wall_frame(obj)
        except Exception:
            continue
        mid = start + axis * (length / 2.0) + Vector((-axis.y, axis.x)) * (t / 2.0)
        p = _to_px(region, rv3d, mid, z)
        if p is not None:
            _label(p.x, p.y, length_text(scene, length))
    if drag.handle == 'MIDDLE' and abs(drag.t) > 1e-6 and op.mouse is not None:
        _label(op.mouse[0] + 40 * _scale(), op.mouse[1] + 24 * _scale(),
               ("+" if drag.t > 0 else "−") + length_text(scene, abs(drag.t)))
    if drag.error and op.mouse is not None:
        _label(op.mouse[0], op.mouse[1] - 30 * _scale(), drag.error)
    gpu.state.blend_set('NONE')


# =============================================================================
# THE DRAG OPERATOR
# =============================================================================

class HOME_BUILDER_OT_wall_handle_drag(bpy.types.Operator):
    """Drag to move this end of the wall, or slide the wall sideways"""
    bl_idname = "home_builder.wall_handle_drag"
    bl_label = "Move Wall"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    handle: bpy.props.EnumProperty(
        items=[(h, h.title(), "") for h in HANDLES],
        options={'SKIP_SAVE'})  # type: ignore

    drag = None
    region = None
    z = 0.0
    mouse = None
    _handle = None

    def _plan_point(self, context, event):
        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
        region, rv3d = context.region, context.region_data
        co = (event.mouse_region_x, event.mouse_region_y)
        o = region_2d_to_origin_3d(region, rv3d, co)
        d = region_2d_to_vector_3d(region, rv3d, co)
        if abs(d.z) < 1e-9:
            return None
        t = (self.z - o.z) / d.z
        return (o + d * t).to_2d()

    def _tol(self, context, point):
        from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
        region, rv3d = context.region, context.region_data
        p = Vector((point[0], point[1], self.z))
        a = location_3d_to_region_2d(region, rv3d, p)
        if a is None:
            return 0.0
        q = region_2d_to_location_3d(region, rv3d, (a.x + SNAP_PX * _scale(), a.y), p)
        return (q - p).length

    def invoke(self, context, event):
        obj = context.active_object
        if not is_house_wall(obj) or context.region_data is None:
            return {'CANCELLED'}
        self.z = obj.matrix_world.translation.z
        point = self._plan_point(context, event)
        if point is None:
            return {'CANCELLED'}
        self.drag = Drag(obj, self.handle, point)
        self.region = context.region
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_drag, (self, context), 'WINDOW', 'POST_PIXEL')
        context.workspace.status_text_set(HINT)
        context.window.cursor_modal_set('SCROLL_XY' if self.handle == 'MIDDLE' else 'MOVE_X')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        context.workspace.status_text_set(None)
        context.window.cursor_modal_restore()
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            point = self._plan_point(context, event)
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            if point is not None:
                scene = context.scene
                imperial = scene.unit_settings.system != 'METRIC'
                if imperial:
                    step = units.inch(0.25) if event.shift else units.inch(1)
                else:
                    step = 0.001 if event.shift else 0.01
                self.drag.update(point, self._tol(context, point),
                                 snap=not event.ctrl, step=step)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.drag.finish()
            self._finish(context)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self.drag.cancel()
            self._finish(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


# =============================================================================
# THE ARROWS
# =============================================================================

class HOME_BUILDER_GGT_wall_handles(bpy.types.GizmoGroup):
    bl_idname = "HOME_BUILDER_GGT_wall_handles"
    bl_label = "Wall Handles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None or not scene.get(hb_house.HOUSE_SCENE_KEY):
            return False
        if context.mode != 'OBJECT':
            return False
        obj = context.active_object
        return obj is not None and obj.select_get() and bool(is_house_wall(obj))

    def setup(self, context):
        self.arrows = {}
        for handle in HANDLES:
            gz = self.gizmos.new('GIZMO_GT_arrow_3d')
            gz.draw_style = 'NORMAL'
            gz.color = ARROW_COLOR
            gz.color_highlight = ARROW_HOVER
            gz.alpha = 0.9
            gz.alpha_highlight = 1.0
            gz.scale_basis = 0.9
            gz.line_width = 3.0
            props = gz.target_set_operator(HOME_BUILDER_OT_wall_handle_drag.bl_idname)
            props.handle = handle
            self.arrows[handle] = gz

    def draw_prepare(self, context):
        obj = context.active_object
        if not is_house_wall(obj):
            return
        try:
            places = handle_places(obj)
            _s, _a, _l, _t, height = wall_frame(obj)
        except Exception:
            return
        z = obj.matrix_world.translation.z + height
        for handle, gz in self.arrows.items():
            p, d = places[handle]
            rot = Vector((d.x, d.y, 0.0)).to_track_quat('Z', 'Y').to_matrix().to_4x4()
            rot.translation = (p.x, p.y, z)
            gz.matrix_basis = rot


classes = (
    HOME_BUILDER_OT_wall_handle_drag,
    HOME_BUILDER_GGT_wall_handles,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
