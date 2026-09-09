"""Draw a product through points, instead of dropping one box.

A support frame that wraps two sides of an island, or a run of panels
that steps around a peninsula, was several placements the user then had
to line up by eye. This is the other way in: click the corners the run
passes through and the whole run is built at once, each span of it an
ordinary product so nothing downstream has to know it was drawn rather
than placed.

The path is the BACK of the product and the body stands to the right of
the direction it is drawn, which is the same relationship a placed
product has to its own origin. F puts it on the other side. Which
products can be drawn this way, and how each turns a span into an
object, lives in ``PATH_PRODUCTS``.
"""

import math

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import intersect_line_plane

from .... import hb_placement, hb_snap, units
from ....units import inch
from ...common import support_frame_shape
from .. import types_face_frame
from .. import props_hb_face_frame
from . import ops_cabinet


# How near the first point the cursor has to come to close the run into a
# loop, in metres of world space.
CLOSE_THRESHOLD = 0.15

# Snap radius in pixels for landing a point on existing geometry -- a
# cabinet corner, mostly, since a drawn run is nearly always lined up
# with the cabinets beside it.
SNAP_PIXELS = 20.0

# Angle step when the straight-segment lock is off. Same ladder the wall
# tool offers, so the two drawing tools behave alike.
FREE_ANGLE_STEP = 15.0

# A panel is three quarters of an inch thick, so a band drawn at its true
# depth would be a hairline. The band's job is to show which side the
# face is on, so a thin product gets a band this wide instead.
MIN_PREVIEW_BAND = inch(6.0)

_PATH_COLOR = (1.0, 0.65, 0.2, 0.95)
_PENDING_COLOR = (1.0, 0.75, 0.4, 0.7)
_BODY_COLOR = (1.0, 0.65, 0.2, 0.18)
_CLOSE_COLOR = (0.0, 1.0, 0.4, 0.9)


# ---- the products that can be drawn -----------------------------------------
# Each builder takes the path as (x, y) pairs already walked in the
# direction that puts the body on the right, and returns the span roots.

def _build_support_frames(context, points, depth, z, closed):
    product_cls = types_face_frame.SupportFrameFaceFrameProduct

    def make_frame(length):
        product = product_cls()
        product.width = length
        product.create("Support Frame")
        return product

    return support_frame_shape.build_path_frame(
        points, make_frame, depth=depth, z=z, closed=closed)


def _build_panels(context, points, depth, z, closed):
    """One panel per span, butted at the corners.

    The same corner rule as the frame: whichever span turns toward the
    face stops a panel's thickness short, so the two never overlap and
    the corner is closed by the one running through.
    """
    product_cls = types_face_frame.PanelFaceFrameCabinet
    roots = []
    for span in support_frame_shape.spans_for_path(points, depth,
                                                   closed=closed):
        if span['length'] < support_frame_shape.MIN_SPAN_LENGTH:
            continue
        panel = product_cls()
        panel.create("Panel")
        obj = panel.obj
        obj.location = (span['origin'][0], span['origin'][1], z)
        obj.rotation_euler = (0.0, 0.0, span['angle'])
        # Sized through the property so the same update the placement
        # tool relies on rebuilds the frame to the span.
        obj.face_frame_cabinet.width = span['length']
        roots.append(obj)
    return roots


def _support_frame_spec():
    cls = types_face_frame.SupportFrameFaceFrameProduct
    return {
        'noun': "support frame",
        'depth': cls().depth,
        'z': cls.default_z_location,
        'side': "frame stands on the",
        'build': _build_support_frames,
        'group': "Support Frame Shape",
        'styled': False,
    }


def _panel_spec():
    cls = types_face_frame.PanelFaceFrameCabinet
    return {
        'noun': "panel",
        'depth': cls().default_depth,
        'z': 0.0,
        'side': "face looks to the",
        'build': _build_panels,
        'group': "Panel Run",
        # A panel takes the active style the way a placed one does; the
        # support frame already applies its finish inside create().
        'styled': True,
    }


# Product name -> a function returning how it is drawn. Functions rather
# than dicts because the depths read scene defaults at the time the tool
# starts, not at import.
PATH_PRODUCTS = {
    'Support Frame': _support_frame_spec,
    'Panel': _panel_spec,
}


def can_draw_path(cabinet_name):
    """True for a product the browser should offer a draw affordance on."""
    return cabinet_name in PATH_PRODUCTS


def _right_of(vec):
    """``vec`` turned 90 degrees to the right, on the floor plane."""
    return Vector((vec.y, -vec.x, 0.0))


def _body_quads(points, depth, flipped=False):
    """Corners of the body each span would fill.

    Drawn as a translucent band so the side the product stands on is
    visible while the path is still being drawn -- which side that is is
    the one thing about this tool a user cannot guess.
    """
    side = -depth if flipped else depth
    quads = []
    for i in range(len(points) - 1):
        start, end = points[i], points[i + 1]
        run = end - start
        if run.length <= 1e-6:
            continue
        offset = _right_of(run.normalized()) * side
        quads.append((start, end, end + offset, start + offset))
    return quads


def draw_path_preview(op, context):
    """GPU overlay: the path so far, where the cursor would take it, and
    the footprint the run would fill."""
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
    for quad in _body_quads(points, op.preview_depth, op.flipped):
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

    # --- how long the span being drawn is ---
    if op.cursor_point is not None and confirmed_n:
        last = op.confirmed_points[-1]
        span = (op.cursor_point - last).length
        if span > 1e-4:
            mid = to2d((last + op.cursor_point) * 0.5)
            if mid is not None:
                text = op.typed_value + "_" if op.typed_value else \
                    units.unit_to_string(
                    context.scene.unit_settings, span)
                blf.size(0, 14)
                blf.color(0, 1.0, 1.0, 1.0, 1.0)
                width = blf.dimensions(0, text)[0]
                blf.position(0, mid.x - width * 0.5, mid.y + 10.0, 0)
                blf.draw(0, text)


class hb_face_frame_OT_draw_product_path(bpy.types.Operator,
                                         hb_placement.PlacementMixin):
    bl_idname = "hb_face_frame.draw_product_path"
    bl_label = "Draw Through Points"
    bl_description = ("Click the corners the run passes through. One "
                      "product is built per span, grouped as a single item")
    bl_options = {'UNDO'}

    cabinet_name: bpy.props.StringProperty(  # type: ignore
        name="Product", default="Support Frame")

    confirmed_points: list = None
    cursor_point: Vector = None
    close_snap: bool = False
    closed: bool = False
    depth: float = inch(24)
    preview_depth: float = inch(24)
    spec: dict = None
    # Straight segments unless the user asks otherwise, because a drawn
    # run almost always sits square to the cabinets beside it. Alt opens
    # it up to the free angle step.
    free_rotation: bool = False
    fine_snap: bool = False
    # Which side of the path the body stands on. Held as a flag rather
    # than by turning the points round, so flipping mid-run does not move
    # the end the next corner is being drawn from.
    flipped: bool = False
    # Direction of the span being drawn, once there is a point to draw
    # from. A typed length is measured along it.
    direction: Vector = None
    _draw_handle = None

    # ---- cursor -> a point on the floor ----------------------------------
    def _floor_point(self, context):
        """Where the mouse is pointing on the floor plane.

        Geometry first -- a drawn run is nearly always lined up with the
        cabinets beside it, so landing on a cabinet corner matters more
        than landing on a round number, and a corner found there is
        taken exactly. Failing that, the raw floor plane, which the
        straight-segment lock then squares up.
        """
        if self.region is None:
            return None, False
        rv3d = self.region.data
        coord = (self.mouse_pos.x, self.mouse_pos.y)

        hit = self._geometry_snap(context, coord, rv3d)
        if hit is not None:
            return Vector((hit.x, hit.y, 0.0)), True

        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        aim = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)
        point = intersect_line_plane(origin, origin + aim,
                                     Vector((0, 0, 0)), Vector((0, 0, 1)))
        if point is None:
            return None, False
        return Vector((point.x, point.y, 0.0)), False

    def _square_up(self, point):
        """``point`` pulled onto a straight run from the last corner.

        The span locks to the axis the cursor has travelled furthest
        along -- the same rule the wall tool uses, and the reason a run
        drawn by eye comes out square. Alt swaps that for a coarse angle
        step. The length lands on the inch grid either way, or the
        sixteenth grid while Shift is held.
        """
        if not self.confirmed_points:
            snapped = hb_snap.snap_vector_to_grid(point, fine=self.fine_snap)
            return Vector((snapped.x, snapped.y, 0.0))

        base = self.confirmed_points[-1]
        run = Vector((point.x - base.x, point.y - base.y))
        if run.length <= 1e-6:
            return base.copy()

        if self.free_rotation:
            step = math.radians(FREE_ANGLE_STEP)
            angle = round(math.atan2(run.y, run.x) / step) * step
            length = run.length
        elif abs(run.x) >= abs(run.y):
            angle = 0.0 if run.x > 0 else math.pi
            length = abs(run.x)
        else:
            angle = math.pi / 2 if run.y > 0 else -math.pi / 2
            length = abs(run.y)

        length = hb_snap.snap_value_to_grid(length, fine=self.fine_snap)
        return base + Vector((math.cos(angle), math.sin(angle), 0.0)) * length

    def _resolve_cursor(self, context):
        """Set ``cursor_point`` and the direction a typed length runs in."""
        raw, on_geometry = self._floor_point(context)
        if raw is None:
            self.cursor_point = None
            return
        # A corner found on real geometry is the point the user asked
        # for, so it is taken as it stands; anything else is squared up.
        self.cursor_point = raw if on_geometry else self._square_up(raw)
        if self.confirmed_points:
            run = self.cursor_point - self.confirmed_points[-1]
            if run.length > 1e-6:
                self.direction = run.normalized()

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

    # ---- typed length ----------------------------------------------------
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.LENGTH

    def _typed_point(self):
        """Where a typed length would put the next corner, or None."""
        if not self.confirmed_points or self.direction is None:
            return None
        parsed = self.parse_typed_distance()
        if parsed is None:
            return None
        return self.confirmed_points[-1] + self.direction * parsed

    def on_typed_value_changed(self):
        """Show the corner a typed length would land on as it is typed."""
        point = self._typed_point()
        if point is not None:
            self.cursor_point = point
        self.update_header(bpy.context)
        area = bpy.context.area
        if area:
            area.tag_redraw()

    def apply_typed_value(self):
        """Enter on a typed length places that corner and carries on."""
        point = self._typed_point()
        if point is not None:
            self.confirmed_points.append(point)
        self.stop_typing()
        self.update_header(bpy.context)

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
        """Turn the drawn path into a run of the product."""
        # The body always stands to the right of the way the path runs,
        # so the other side is the same path walked backwards.
        points = list(self.confirmed_points)
        if self.flipped:
            points.reverse()
        roots = self.spec['build'](
            context, [(p.x, p.y) for p in points],
            self.depth, self.spec['z'], self.closed)
        if not roots:
            return None
        if self.spec['styled']:
            props_hb_face_frame.ensure_default_styles(context)
            scene_props = props_hb_face_frame.get_style_props(context)
            idx = scene_props.active_cabinet_style_index
            if 0 <= idx < len(scene_props.cabinet_styles):
                style = scene_props.cabinet_styles[idx]
                for root in roots:
                    style.assign_style_to_cabinet(root)
        target = roots[-1]
        if len(roots) > 1:
            # One item to select, move and save: the run was drawn as a
            # single shape, so it should not come apart into loose boxes.
            target = ops_cabinet.create_cabinet_group_from_roots(
                roots, name=self.spec['group'])
        # A fresh drop is only reachable in the current selection mode
        # once it has been put through it.
        for root in roots:
            ops_cabinet.apply_face_frame_selection_mode(context, root)
        for obj in context.selected_objects:
            obj.select_set(False)
        target.select_set(True)
        context.view_layer.objects.active = target
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
        noun = self.spec['noun']
        if len(self.confirmed_points) < 2:
            self.report({'WARNING'},
                        f"Need at least two points to draw a {noun}")
            return {'CANCELLED'}
        roots = self._build(context)
        if not roots:
            self.report({'WARNING'},
                        f"The path was too short to build a {noun}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Built a {noun} run in {len(roots)} span(s)")
        return {'FINISHED'}

    def cancel(self, context):
        self._teardown(context)

    def update_header(self, context):
        if self.placement_state == hb_placement.PlacementState.TYPING:
            hb_placement.draw_header_text(context, " | ".join([
                f"Length: {self.typed_value}_",
                "Enter to place the corner",
                "Esc to stop typing",
            ]))
            return
        count = len(self.confirmed_points)
        if count == 0:
            state = "Click the first corner"
        elif count == 1:
            state = "Click the next corner, or type a length"
        else:
            state = f"{count} corners"
            if self.close_snap:
                state += " [CLOSE]"
            state += " -- Enter to finish"
        angles = ("Free (%d deg)" % int(FREE_ANGLE_STEP)
                  if self.free_rotation else "Straight")
        side = "left" if self.flipped else "right"
        hb_placement.draw_header_text(context, " | ".join([
            state,
            "Alt: %s" % angles,
            "F: %s %s (flip)" % (self.spec['side'], side),
            "Backspace: undo | Shift: fine | Ctrl: no snap | Esc: cancel",
        ]))

    def execute(self, context):
        make_spec = PATH_PRODUCTS.get(self.cabinet_name)
        if make_spec is None:
            self.report({'WARNING'},
                        f"{self.cabinet_name} cannot be drawn through points")
            return {'CANCELLED'}
        self.spec = make_spec()
        self.init_placement(context)
        self.confirmed_points = []
        self.cursor_point = None
        self.close_snap = False
        self.closed = False
        self.suspend_snap = False
        self.free_rotation = False
        self.fine_snap = False
        self.flipped = False
        self.direction = None
        self.depth = self.spec['depth']
        self.preview_depth = max(self.depth, MIN_PREVIEW_BAND)
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_path_preview, (self, context), 'WINDOW', 'POST_PIXEL')
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
        self.fine_snap = event.shift
        self.update_snap(context, event)
        if self.placement_state != hb_placement.PlacementState.TYPING:
            self._resolve_cursor(context)
            self._check_close()
        if context.area:
            context.area.tag_redraw()

        # Typing owns the number keys, Backspace, Enter and Esc while it
        # is running, so it is offered the event before anything else.
        if self.handle_typing_event(event):
            return {'RUNNING_MODAL'}

        if event.type in {'LEFT_ALT', 'RIGHT_ALT'} and event.value == 'PRESS':
            self.free_rotation = not self.free_rotation
            self.update_header(context)
            return {'RUNNING_MODAL'}

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
            self.flipped = not self.flipped
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
    hb_face_frame_OT_draw_product_path,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
