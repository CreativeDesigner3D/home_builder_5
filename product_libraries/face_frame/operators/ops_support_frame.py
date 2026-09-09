"""Draw a support frame through points, instead of dropping one box.

A frame that wraps two sides of an island, or steps around a peninsula,
was three separate placements the user then had to line up by eye. This
is the other way in: click the corners the frame runs through and the
whole run is built at once, each leg of it an ordinary support frame so
nothing downstream has to know it was drawn rather than placed.

The path is the BACK of the frame and the body stands to the right of
the direction it is drawn, which is the same relationship a placed frame
has to its own origin. F turns the path around when the body lands on
the wrong side.
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import intersect_line_plane

from .... import hb_placement, hb_snap
from ....units import inch
from ...common import support_frame_shape
from .. import types_face_frame
from . import ops_cabinet


# How near the first point the cursor has to come to close the run into a
# loop, in metres of world space.
CLOSE_THRESHOLD = 0.15

# Snap radius in pixels for landing a point on existing geometry -- a
# cabinet corner, mostly, since a support frame is nearly always lined up
# with the run it carries.
SNAP_PIXELS = 20.0

_PATH_COLOR = (1.0, 0.65, 0.2, 0.95)
_PENDING_COLOR = (1.0, 0.75, 0.4, 0.7)
_BODY_COLOR = (1.0, 0.65, 0.2, 0.18)
_CLOSE_COLOR = (0.0, 1.0, 0.4, 0.9)


def _right_of(vec):
    """``vec`` turned 90 degrees to the right, on the floor plane."""
    return Vector((vec.y, -vec.x, 0.0))


def _body_quads(points, depth):
    """Screen-space corners of the frame body each span would fill.

    Drawn as a translucent band so the side the frame stands on is
    visible while the path is still being drawn -- which side that is is
    the one thing about this tool a user cannot guess.
    """
    quads = []
    for i in range(len(points) - 1):
        start, end = points[i], points[i + 1]
        run = end - start
        if run.length <= 1e-6:
            continue
        offset = _right_of(run.normalized()) * depth
        quads.append((start, end, end + offset, start + offset))
    return quads


def draw_support_frame_preview(op, context):
    """GPU overlay: the path so far, where the cursor would take it, and
    the footprint the frame would fill."""
    region = op.region
    if region is None:
        return
    rv3d = region.data
    if rv3d is None:
        return

    def to2d(point):
        return view3d_utils.location_3d_to_region_2d(region, rv3d, point)

    points = list(op.confirmed_points)
    if op.cursor_point is not None:
        points.append(op.cursor_point)
    if not points:
        return

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    # --- the body each span would fill ---
    tris = []
    for quad in _body_quads(points, op.depth):
        flat = [to2d(corner) for corner in quad]
        if any(c is None for c in flat):
            continue
        a, b, c, d = flat
        tris.extend([(a.x, a.y), (b.x, b.y), (c.x, c.y),
                     (a.x, a.y), (c.x, c.y), (d.x, d.y)])
    if tris:
        shader.uniform_float("color", _BODY_COLOR)
        batch_for_shader(shader, 'TRIS', {"pos": tris}).draw(shader)

    screen = [to2d(p) for p in points]
    if any(s is None for s in screen):
        gpu.state.blend_set('NONE')
        return

    # --- the path itself: confirmed solid, the span under the cursor faint ---
    gpu.state.line_width_set(2.0)
    confirmed_n = len(op.confirmed_points)
    solid = []
    for i in range(confirmed_n - 1):
        solid.extend([(screen[i].x, screen[i].y),
                      (screen[i + 1].x, screen[i + 1].y)])
    if solid:
        shader.uniform_float("color", _PATH_COLOR)
        batch_for_shader(shader, 'LINES', {"pos": solid}).draw(shader)
    if op.cursor_point is not None and confirmed_n:
        last, cur = screen[confirmed_n - 1], screen[-1]
        shader.uniform_float("color", _PENDING_COLOR)
        batch_for_shader(shader, 'LINES', {
            "pos": [(last.x, last.y), (cur.x, cur.y)]}).draw(shader)

    # --- the corners ---
    gpu.state.point_size_set(8.0)
    dots = [(s.x, s.y) for s in screen[:confirmed_n]]
    if dots:
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch_for_shader(shader, 'POINTS', {"pos": dots}).draw(shader)
    if op.cursor_point is not None:
        cur = screen[-1]
        gpu.state.point_size_set(6.0)
        colour = _CLOSE_COLOR if op.close_snap else (1.0, 1.0, 0.0, 0.9)
        shader.uniform_float("color", colour)
        batch_for_shader(shader, 'POINTS',
                         {"pos": [(cur.x, cur.y)]}).draw(shader)

    gpu.state.point_size_set(1.0)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


class hb_face_frame_OT_draw_support_frame(bpy.types.Operator,
                                          hb_placement.PlacementMixin):
    bl_idname = "hb_face_frame.draw_support_frame"
    bl_label = "Draw Support Frame"
    bl_description = ("Click the corners a support frame runs through. The "
                      "frame is built along the path, one span per leg")
    bl_options = {'UNDO'}

    confirmed_points: list = None
    cursor_point: Vector = None
    close_snap: bool = False
    closed: bool = False
    depth: float = inch(24)
    _draw_handle = None

    # ---- cursor -> a point on the floor ----------------------------------
    def _floor_point(self, context):
        """Where the mouse is pointing on the floor plane, snapped.

        Geometry first -- a support frame is nearly always lined up with
        the cabinets it carries, so landing on a cabinet corner matters
        more than landing on a round number. Failing that, the floor
        plane on the inch grid.
        """
        if self.region is None:
            return None
        rv3d = self.region.data
        coord = (self.mouse_pos.x, self.mouse_pos.y)

        hit = self._geometry_snap(context, coord, rv3d)
        if hit is not None:
            return Vector((hit.x, hit.y, 0.0))

        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d,
                                                        coord)
        point = intersect_line_plane(origin, origin + direction,
                                     Vector((0, 0, 0)), Vector((0, 0, 1)))
        if point is None:
            return None
        snapped = hb_snap.snap_vector_to_grid(point)
        return Vector((snapped.x, snapped.y, 0.0))

    def _geometry_snap(self, context, coord, rv3d):
        """A vertex / edge / midpoint under the cursor, or None.

        Held off while Ctrl is down, matching the convention the rest of
        the add-on's tools use for suspending a snap.
        """
        if self.suspend_snap:
            return None
        try:
            from .... import hb_snap_engine
            hit = hb_snap_engine.engine().snap(
                context, self.region, rv3d, coord)
        except Exception:
            return None
        return hit.location if hit is not None else None

    def _check_close(self):
        self.close_snap = False
        if len(self.confirmed_points) < 3 or self.cursor_point is None:
            return
        first = self.confirmed_points[0]
        flat = Vector((self.cursor_point.x - first.x,
                       self.cursor_point.y - first.y))
        self.close_snap = flat.length < CLOSE_THRESHOLD

    # ---- building --------------------------------------------------------
    def _build(self, context):
        """Turn the drawn path into a run of support frames."""
        product_cls = types_face_frame.SupportFrameFaceFrameProduct

        def make_frame(length):
            product = product_cls()
            product.width = length
            product.create("Support Frame")
            return product

        roots = support_frame_shape.build_path_frame(
            [(p.x, p.y) for p in self.confirmed_points],
            make_frame,
            depth=self.depth,
            z=product_cls.default_z_location,
            closed=self.closed,
        )
        if not roots:
            return None
        if len(roots) > 1:
            # One item to select, move and save: the run was drawn as a
            # single shape, so it should not come apart into loose boxes.
            ops_cabinet.create_cabinet_group_from_roots(
                roots, name="Support Frame Shape")
        return roots

    # ---- modal -----------------------------------------------------------
    def _teardown(self, context):
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle,
                                                      'WINDOW')
            self._draw_handle = None
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')

    def _finish(self, context, closed=False):
        self.closed = closed
        self._teardown(context)
        if len(self.confirmed_points) < 2:
            self.report({'WARNING'}, "Need at least two points to draw a frame")
            return {'CANCELLED'}
        roots = self._build(context)
        if not roots:
            self.report({'WARNING'}, "The path was too short to build a frame")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Built a support frame in {len(roots)} span(s)")
        return {'FINISHED'}

    def cancel(self, context):
        self._teardown(context)

    def update_header(self, context):
        count = len(self.confirmed_points)
        if count == 0:
            state = "Click the first corner"
        elif count == 1:
            state = "Click the next corner"
        else:
            state = f"{count} corners"
            if self.close_snap:
                state += " [CLOSE]"
            state += " -- Enter to finish"
        hb_placement.draw_header_text(context, " | ".join([
            state,
            "F: flip which side the frame stands on",
            "Backspace: undo | Ctrl: no snap | Esc: cancel",
        ]))

    def execute(self, context):
        self.init_placement(context)
        self.confirmed_points = []
        self.cursor_point = None
        self.close_snap = False
        self.closed = False
        self.suspend_snap = False
        self.depth = types_face_frame.SupportFrameFaceFrameProduct().depth
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_support_frame_preview, (self, context), 'WINDOW',
            'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        self.update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        self.suspend_snap = event.ctrl
        self.update_snap(context, event)
        self.cursor_point = self._floor_point(context)
        self._check_close()
        if context.area:
            context.area.tag_redraw()

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.cursor_point is None:
                return {'RUNNING_MODAL'}
            if self.close_snap:
                return self._finish(context, closed=True)
            self.confirmed_points.append(self.cursor_point.copy())
            self.update_header(context)
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if len(self.confirmed_points) >= 2:
                return self._finish(context)
            self.report({'WARNING'}, "Need at least two points")
            return {'RUNNING_MODAL'}

        if event.type == 'C' and event.value == 'PRESS':
            if len(self.confirmed_points) >= 3:
                return self._finish(context, closed=True)
            return {'RUNNING_MODAL'}

        if event.type == 'F' and event.value == 'PRESS':
            # The body stands to the right of the way the path runs, so
            # drawing it backwards is what puts it on the other side.
            self.confirmed_points.reverse()
            self.update_header(context)
            return {'RUNNING_MODAL'}

        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.confirmed_points:
                self.confirmed_points.pop()
                self.update_header(context)
            return {'RUNNING_MODAL'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if len(self.confirmed_points) >= 2:
                return self._finish(context)
            self.cancel(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


classes = (
    hb_face_frame_OT_draw_support_frame,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
