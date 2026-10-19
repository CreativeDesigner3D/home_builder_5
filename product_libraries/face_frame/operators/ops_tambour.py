"""Tambour: draw it by clicking points, change it from its menu.

Drawing is three clicks on the floor plan: the start of the run, its
end, then a third that bows the run into an arc through those ends
(Enter on the third keeps it straight). Points land on cabinet and wall
corners when the cursor is near one, the inch grid otherwise; a length
can be typed for the second point and a bow for the third. F swaps the
side the slat faces show on. The slats stand on the floor at the base
cabinet height; Tambour Properties changes that and the slats.
"""

import math

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import intersect_line_plane

from .... import hb_placement, hb_snap, units
from ....units import inch
from ...common import tambour
from .. import types_face_frame

_ARC_COLOR = (1.0, 0.65, 0.2, 0.95)
_FACE_COLOR = (1.0, 0.65, 0.2, 0.35)
_CHORD_COLOR = (1.0, 1.0, 1.0, 0.35)


def _draw_preview(op, context):
    region = op.region
    if region is None or region.data is None:
        return
    rv3d = region.data

    def to2d(p):
        return view3d_utils.location_3d_to_region_2d(region, rv3d, p)

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    gpu.state.line_width_set(2.0)

    run = op.preview_run()
    if run is not None:
        start, chord, angle, sagitta, face = run
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def world(p):
            return Vector((start.x + p.x * cos_a - p.y * sin_a,
                           start.y + p.x * sin_a + p.y * cos_a, 0.0))
        pts = tambour.arc_points(chord, sagitta, 48)
        screen = [to2d(world(p)) for p in pts]
        if all(s is not None for s in screen):
            line = []
            for a, b in zip(screen, screen[1:]):
                line += [(a.x, a.y), (b.x, b.y)]
            shader.uniform_float("color", _ARC_COLOR)
            batch_for_shader(shader, 'LINES', {"pos": line}).draw(shader)
            # Ticks on the face side, so which way the slats show is
            # visible before the click.
            ticks = []
            depth = max(op.settings['thickness'], inch(1.0))
            for i in range(0, len(pts) - 1, 4):
                a, b = pts[i], pts[i + 1]
                t = (b - a)
                if t.length < 1e-9:
                    continue
                n = Vector((-t.y, t.x)).normalized() * (depth * face)
                p0, p1 = to2d(world(a)), to2d(world(a + n))
                if p0 and p1:
                    ticks += [(p0.x, p0.y), (p1.x, p1.y)]
            if ticks:
                shader.uniform_float("color", _FACE_COLOR)
                batch_for_shader(shader, 'LINES', {"pos": ticks}).draw(shader)
        if abs(sagitta) > 1e-6:
            a, b = to2d(world(Vector((0, 0)))), to2d(world(Vector((chord, 0))))
            if a and b:
                shader.uniform_float("color", _CHORD_COLOR)
                batch_for_shader(shader, 'LINES',
                                 {"pos": [(a.x, a.y), (b.x, b.y)]}).draw(shader)

    dots = [to2d(p) for p in op.points]
    if op.cursor is not None and len(op.points) < 2:
        dots.append(to2d(op.cursor))
    dots = [(d.x, d.y) for d in dots if d is not None]
    if dots:
        gpu.state.point_size_set(8.0)
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch_for_shader(shader, 'POINTS', {"pos": dots}).draw(shader)
        gpu.state.point_size_set(1.0)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


class hb_face_frame_OT_draw_tambour(bpy.types.Operator,
                                    hb_placement.PlacementMixin):
    """Draw a tambour: click the start, the end, then bow it into an arc"""
    bl_idname = "hb_face_frame.draw_tambour"
    bl_label = "Draw Tambour"
    bl_options = {'UNDO'}

    points: list = None
    cursor: Vector = None
    sagitta: float = 0.0
    face: int = 0              # 0 = the default side for the bow
    settings: dict = None
    _handle = None

    # ---- cursor -> floor point --------------------------------------------
    def _floor_point(self, context):
        if self.region is None:
            return None, False
        rv3d = self.region.data
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        if not self.suspend_snap:
            try:
                from .... import hb_snap_engine
                hit = hb_snap_engine.engine().snap(
                    context, self.region, rv3d, coord)
            except Exception:
                hit = None
            if hit is not None:
                loc = hit.location
                return Vector((loc.x, loc.y, 0.0)), True
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        aim = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)
        p = intersect_line_plane(origin, origin + aim, Vector((0, 0, 0)),
                                 Vector((0, 0, 1)))
        if p is None:
            return None, False
        return Vector((p.x, p.y, 0.0)), False

    def _resolve(self, context):
        raw, exact = self._floor_point(context)
        if raw is None:
            return
        if len(self.points) == 2:
            # Third point: how far off the chord, signed.
            self.cursor = raw
            a, b = self.points
            chord = b - a
            if chord.length > 1e-6:
                left = Vector((-chord.y, chord.x, 0.0)).normalized()
                bow = (raw - a).dot(left)
                if not exact:
                    bow = hb_snap.snap_value_to_grid(bow, fine=self.fine_snap)
                self.sagitta = bow
            return
        if exact:
            self.cursor = raw
        else:
            snapped = hb_snap.snap_vector_to_grid(raw, fine=self.fine_snap)
            self.cursor = Vector((snapped.x, snapped.y, 0.0))

    def preview_run(self):
        """(start, chord, angle, sagitta, face) for what would be built."""
        if not self.points:
            return None
        start = self.points[0]
        end = self.points[1] if len(self.points) > 1 else self.cursor
        if end is None:
            return None
        run = end - start
        if run.length < 1e-6:
            return None
        sagitta = self.sagitta if len(self.points) > 1 else 0.0
        # A bow can't pass the half circle by much before it stops
        # reading as a corner; cap it at the chord.
        sagitta = max(-run.length, min(run.length, sagitta))
        face = self.face or tambour.default_face(sagitta)
        return start, run.length, math.atan2(run.y, run.x), sagitta, face

    # ---- typing ---------------------------------------------------------------
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.LENGTH

    def apply_typed_value(self):
        value = self.parse_typed_distance()
        self.stop_typing()
        if value is None:
            return
        if len(self.points) == 1 and self.cursor is not None:
            run = self.cursor - self.points[0]
            if run.length > 1e-6 and value > 0:
                self.points.append(self.points[0] + run.normalized() * value)
                self.sagitta = 0.0
        elif len(self.points) == 2:
            # A typed bow goes the way the cursor is.
            sign = -1.0 if self.sagitta < 0 else 1.0
            self.sagitta = abs(value) * sign
        self.update_header(bpy.context)

    # ---- header ----------------------------------------------------------------
    def update_header(self, context):
        if self.placement_state == hb_placement.PlacementState.TYPING:
            what = "Length" if len(self.points) == 1 else "Bow"
            hb_placement.draw_header_text(
                context, f"{what}: {self.typed_value}_  |  Enter: apply  |  "
                         "Esc: stop typing")
            return
        us = context.scene.unit_settings
        n = len(self.points)
        if n == 0:
            state = "Click the start of the tambour"
        elif n == 1:
            state = "Click the end, or type a length"
        else:
            run = self.preview_run()
            state = ("Move to bow it, click to place (Enter: straight)"
                     + (f"  -  bow {units.unit_to_string(us, abs(run[3]))}"
                        if run else ""))
        side = "flip side the slats face"
        hb_placement.draw_header_text(context, " | ".join([
            state, f"F: {side}",
            "Backspace: undo | Shift: fine | Ctrl: no snap | Esc: cancel"]))

    # ---- run -------------------------------------------------------------------
    def invoke(self, context, event):
        self.init_placement(context)
        if self.region is None:
            self.report({'WARNING'}, "No 3D viewport available")
            return {'CANCELLED'}
        scene_props = context.scene.hb_face_frame
        w, t = tambour.PROFILE_DEFAULTS['HALF_ROUND']
        self.settings = {
            'chord': 0.0, 'sagitta': 0.0, 'face': 0,
            'height': scene_props.base_cabinet_height,
            'profile': 'HALF_ROUND', 'width': w, 'thickness': t, 'gap': 0.0,
        }
        self.points = []
        self.cursor = None
        self.sagitta = 0.0
        self.face = 0
        self.suspend_snap = False
        self.fine_snap = False
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_preview, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        self.update_header(context)
        return {'RUNNING_MODAL'}

    def _teardown(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        hb_placement.clear_header_text(context)
        if context.area:
            context.area.tag_redraw()

    def _finish(self, context):
        run = self.preview_run()
        self._teardown(context)
        if run is None:
            return {'CANCELLED'}
        start, chord, angle, sagitta, face = run
        settings = dict(self.settings, chord=chord, sagitta=sagitta,
                        face=face)
        obj = tambour.create(context, settings)
        obj.location = (start.x, start.y, 0.0)
        obj.rotation_euler = (0.0, 0.0, angle)
        types_face_frame.apply_tambour_finish(obj)
        for o in context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        self.report({'INFO'}, "Placed a tambour of %d slats"
                    % tambour.slat_count(settings))
        return {'FINISHED'}

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
            self._resolve(context)
        if context.area:
            context.area.tag_redraw()
        if self.handle_typing_event(event):
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.cursor is None:
                return {'RUNNING_MODAL'}
            if len(self.points) < 2:
                if self.points and (self.cursor - self.points[0]).length < 1e-4:
                    return {'RUNNING_MODAL'}
                self.points.append(self.cursor.copy())
                self.sagitta = 0.0
                self.update_header(context)
                return {'RUNNING_MODAL'}
            return self._finish(context)
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if len(self.points) == 2:
                self.sagitta = 0.0
                return self._finish(context)
            return {'RUNNING_MODAL'}
        if event.type == 'F' and event.value == 'PRESS':
            run = self.preview_run()
            current = run[4] if run else (self.face or -1)
            self.face = -current
            self.update_header(context)
            return {'RUNNING_MODAL'}
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.points:
                self.points.pop()
                self.sagitta = 0.0
            self.update_header(context)
            return {'RUNNING_MODAL'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._teardown(context)
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            self.update_header(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._teardown(context)


class hb_face_frame_OT_tambour_prompts(bpy.types.Operator):
    """Change the tambour's height, slats and shape"""
    bl_idname = "hb_face_frame.tambour_prompts"
    bl_label = "Tambour Properties"
    bl_options = {'REGISTER', 'UNDO'}

    height: bpy.props.FloatProperty(
        name="Height", subtype='DISTANCE', min=inch(1.0))  # type: ignore
    bottom: bpy.props.FloatProperty(
        name="Bottom", subtype='DISTANCE',
        description="Height of the bottom of the slats off the floor"
    )  # type: ignore
    def _profile_changed(self, context):
        # A new slat shape starts at that shape's stock size.
        self.width, self.thickness = tambour.PROFILE_DEFAULTS[self.profile]

    profile: bpy.props.EnumProperty(
        name="Slat", items=tambour.PROFILE_ITEMS,
        update=_profile_changed)  # type: ignore
    width: bpy.props.FloatProperty(
        name="Slat Width", subtype='DISTANCE', min=inch(1.0 / 16.0))  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Slat Thickness", subtype='DISTANCE', min=inch(1.0 / 32.0))  # type: ignore
    gap: bpy.props.FloatProperty(
        name="Gap", subtype='DISTANCE', min=0.0,
        description="Space between slats")  # type: ignore
    bow: bpy.props.FloatProperty(
        name="Bow", subtype='DISTANCE',
        description="How far the middle of the run sits off a straight "
                    "line between its ends (0 = straight)")  # type: ignore
    flip: bpy.props.BoolProperty(
        name="Flip Face Side",
        description="Show the slat faces on the other side of the run"
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return tambour.tambour_root(context.active_object) is not None

    def invoke(self, context, event):
        obj = tambour.tambour_root(context.active_object)
        s = tambour.read(obj)
        self.height = s['height']
        self.bottom = obj.location.z
        self.profile = s['profile']
        self.width = s['width']
        self.thickness = s['thickness']
        self.gap = s['gap']
        self.bow = s['sagitta']
        self.flip = False
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        col = self.layout.column()
        col.prop(self, 'height')
        col.prop(self, 'bottom')
        col.separator()
        col.prop(self, 'profile')
        col.prop(self, 'width')
        col.prop(self, 'thickness')
        col.prop(self, 'gap')
        col.separator()
        col.prop(self, 'bow')
        col.prop(self, 'flip')
        obj = tambour.tambour_root(context.active_object)
        if obj is not None:
            s = dict(tambour.read(obj), width=self.width, gap=self.gap,
                     sagitta=self.bow)
            col.label(text="%d slats" % tambour.slat_count(s), icon='INFO')

    def execute(self, context):
        obj = tambour.tambour_root(context.active_object)
        if obj is None:
            return {'CANCELLED'}
        s = tambour.read(obj)
        s.update(height=self.height, profile=self.profile, width=self.width,
                 thickness=self.thickness, gap=self.gap, sagitta=self.bow)
        if self.flip:
            s['face'] = -s['face']
        tambour.write(obj, s)
        obj.location.z = self.bottom
        tambour.rebuild(obj)
        return {'FINISHED'}


class hb_face_frame_OT_delete_tambour(bpy.types.Operator):
    """Delete the selected tambours"""
    bl_idname = "hb_face_frame.delete_tambour"
    bl_label = "Delete Tambour"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return tambour.tambour_root(context.active_object) is not None

    def execute(self, context):
        for obj in list(context.selected_objects):
            root = tambour.tambour_root(obj)
            if root is not None and root.name in bpy.data.objects:
                bpy.data.objects.remove(root, do_unlink=True)
        return {'FINISHED'}


class HOME_BUILDER_MT_tambour_commands(bpy.types.Menu):
    bl_label = "Tambour Commands"

    def draw(self, context):
        layout = self.layout
        obj = tambour.tambour_root(context.active_object)
        if obj is not None:
            s = tambour.read(obj)
            layout.label(text="Tambour - %d %s slats" % (
                tambour.slat_count(s), tambour.profile_label(s).lower()))
            layout.separator()
        layout.operator("hb_face_frame.tambour_prompts",
                        text="Tambour Properties...", icon='WINDOW')
        layout.operator("object.duplicate_move", text="Duplicate",
                        icon='DUPLICATE')
        layout.separator()
        layout.operator("hb_face_frame.delete_tambour",
                        text="Delete Tambour")


classes = (
    hb_face_frame_OT_draw_tambour,
    hb_face_frame_OT_tambour_prompts,
    hb_face_frame_OT_delete_tambour,
    HOME_BUILDER_MT_tambour_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
