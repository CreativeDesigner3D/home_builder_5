import bpy
from mathutils import Vector

from .. import hb_types
from .. import units


class HOME_BUILDER_OT_change_units(bpy.types.Operator):
    bl_idname = "home_builder.change_units"
    bl_label = "Change Units"
    bl_description = "Change the scene unit system"

    unit_system: bpy.props.StringProperty(name="Unit System")
    length_unit: bpy.props.StringProperty(name="Length Unit")

    def execute(self, context):
        context.scene.unit_settings.system = self.unit_system
        context.scene.unit_settings.length_unit = self.length_unit
        return {'FINISHED'}


class HOME_BUILDER_MT_main_menu(bpy.types.Menu):
    bl_label = "Home Builder"
    bl_idname = "HOME_BUILDER_MT_main_menu"

    def draw(self, context):
        layout = self.layout
        
        # Room operations
        layout.operator("home_builder.create_room", text="New Room", icon='ADD')
        layout.menu("HOME_BUILDER_MT_room_list", text="Switch Room", icon='LOOP_BACK')
        
        layout.separator()
        
        # Layout views submenu
        layout.menu("HOME_BUILDER_MT_layout_views_create", text="Create View", icon='VIEW_ORTHO')
        
        layout.separator()
        
        # Camera
        layout.operator("home_builder.create_camera", text="Create Camera", icon='CAMERA_DATA')
        
        layout.separator()
        
        # Units
        layout.menu("HOME_BUILDER_MT_change_units", text="Change Units", icon='DRIVER_DISTANCE')
        
        layout.separator()
        
        # Settings
        prefs = context.preferences.addons[__package__.rsplit('.', 1)[0]].preferences
        layout.prop(prefs, "use_viewport_hud")
        layout.operator("home_builder.set_recommended_settings", 
                       text="Recommended Settings", icon='PREFERENCES')
        layout.operator("home_builder.rendering_settings",
                       text="Rendering Settings", icon='RENDER_STILL')
        
        layout.separator()
        
        # Export
        layout.operator("home_builder.prepare_for_export", icon='EXPORT')


class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.wall_prompts", text="Wall Prompts")
        layout.operator("home_builder_walls.change_room_size", text="Change Room Size", icon='ARROW_LEFTRIGHT')
        layout.separator()
        layout.operator("home_builder_walls.hide_wall", text="Hide Wall", icon='HIDE_ON')
        layout.operator("home_builder_walls.isolate_selected_walls", text="Isolate Selected Walls", icon='ZOOM_SELECTED')
        layout.operator("home_builder_walls.show_all_walls", text="Show All Walls", icon='HIDE_OFF')
        layout.separator()
        layout.operator("home_builder_walls.draw_wall_cutter", text="Draw Wall Cutter", icon='MOD_BOOLEAN')
        layout.operator("home_builder_walls.add_soffit", text="Add Soffit", icon='MESH_CUBE')
        layout.separator()
        layout.operator("hb_frameless.place_snap_line", text="Place Snap Line", icon='SNAP_MIDPOINT')
        layout.operator("hb_frameless.delete_all_snap_lines", text="Delete All Snap Lines", icon='TRASH')
        layout.separator()
        layout.operator("home_builder_walls.delete_wall", text="Delete Wall", icon='X')


class HOME_BUILDER_MT_soffit_commands(bpy.types.Menu):
    bl_label = "Soffit Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.soffit_prompts", text="Soffit Prompts")
        layout.separator()
        layout.operator("home_builder_walls.delete_soffit", text="Delete Soffit", icon='X')


class HOME_BUILDER_MT_door_commands(bpy.types.Menu):
    bl_label = "Door Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_doors_windows.door_prompts", text="Door Prompts")
        layout.separator()
        layout.operator("home_builder_doors_windows.flip_door_swing", text="Flip Door Swing")
        layout.operator("home_builder_doors_windows.flip_door_hand", text="Flip Door Hand")
        layout.operator("home_builder_doors_windows.toggle_double_door", text="Toggle Double Door")
        layout.separator()
        layout.operator("home_builder_doors_windows.duplicate_door", text="Duplicate Door")
        layout.separator()
        layout.operator("home_builder_doors_windows.delete_door_window", text="Delete Door").object_type = 'DOOR'


class HOME_BUILDER_MT_window_commands(bpy.types.Menu):
    bl_label = "Window Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_doors_windows.window_prompts", text="Window Prompts")
        layout.separator()
        layout.operator("home_builder_doors_windows.duplicate_window", text="Duplicate Window")
        layout.separator()
        layout.operator("home_builder_doors_windows.delete_door_window", text="Delete Window").object_type = 'WINDOW'


class HOME_BUILDER_MT_change_units(bpy.types.Menu):
    bl_label = "Change Units"
    bl_idname = "HOME_BUILDER_MT_change_units"

    def draw(self, context):
        layout = self.layout
        unit_settings = context.scene.unit_settings

        units = [
            ("METRIC", "METERS", "Meters"),
            ("METRIC", "CENTIMETERS", "Centimeters"),
            ("METRIC", "MILLIMETERS", "Millimeters"),
            ("IMPERIAL", "FEET", "Feet"),
            ("IMPERIAL", "INCHES", "Inches"),
        ]

        for system, length, label in units:
            is_active = (unit_settings.system == system and unit_settings.length_unit == length)
            icon = 'CHECKMARK' if is_active else 'NONE'
            op = layout.operator("home_builder.change_units", text=label, icon=icon)
            op.unit_system = system
            op.length_unit = length



class HOME_BUILDER_OT_flip_dimensions(bpy.types.Operator):
    bl_idname = "home_builder.flip_dimensions"
    bl_label = "Flip Dimensions"
    bl_description = "Flip the leader side of all selected dimensions"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            # Dimensions carry IS_DIMENSION (set in GeoNodeDimension.create);
            # the leader sits on whichever side Leader Length points, so
            # negating it (and the matching small-dim text offset) mirrors
            # the whole dimension to the opposite side of the line.
            if not obj.get('IS_DIMENSION'):
                continue
            dim = hb_types.GeoNodeDimension(obj)
            dim.set_input("Leader Length", dim.get_input("Leader Length") * -1)
            dim.set_input("Offset Text Amount", dim.get_input("Offset Text Amount") * -1)
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class HOME_BUILDER_OT_flip_dimension_text(bpy.types.Operator):
    bl_idname = "home_builder.flip_dimension_text"
    bl_label = "Flip Text"
    bl_description = "Toggle the Flip Text input on all selected dimensions"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if not obj.get('IS_DIMENSION'):
                continue
            dim = hb_types.GeoNodeDimension(obj)
            dim.set_input("Flip Text", not dim.get_input("Flip Text"))
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class HOME_BUILDER_OT_update_dimensions(bpy.types.Operator):
    bl_idname = "home_builder.update_dimensions"
    bl_label = "Update Dimensions"
    bl_description = "Recompute text placement and decimal precision for all selected dimensions"
    bl_options = {'UNDO'}

    def execute(self, context):
        # HB5's GeoNodeDimension has no update() method (unlike pyclone), so
        # the per-dimension refresh logic is folded in here: hide zero-length
        # dims, push the text off short dims so it doesn't collide with the
        # ticks, re-snap the decimal precision, and clear any stray manual X
        # text offset.
        small = units.inch(7)
        for obj in context.selected_objects:
            if not obj.get('IS_DIMENSION'):
                continue
            dim = hb_types.GeoNodeDimension(obj)
            pts = obj.data.splines[0].points
            p1 = Vector(pts[0].co[:3])
            p2 = Vector(pts[1].co[:3])
            dist = (p2 - p1).length
            if dist == 0:
                obj.hide_viewport = True
                continue
            obj.hide_viewport = False
            if dist <= small:
                offset = units.inch(3)
                if dim.get_input("Leader Length") < 0:
                    offset = -offset
                dim.set_input("Offset Text Amount", offset)
                dim.set_input("Offset Text From Line", True)
            else:
                dim.set_input("Offset Text From Line", False)
            dim.set_decimal(fine=True)
            dim.set_input("Offset Text X Amount", 0)
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class HOME_BUILDER_OT_adjust_dimension_leader_length(bpy.types.Operator):
    bl_idname = "home_builder.adjust_dimension_leader_length"
    bl_label = "Adjust Leader Length"
    bl_description = "Interactively adjust the leader length of all selected dimensions based on mouse position"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.get('IS_DIMENSION') for obj in context.selected_objects)

    def get_mouse_distance_from_line(self, context, event, dim):
        """Signed perpendicular world distance from the mouse to the
        dimension line, used as the live leader length. Works in screen
        space then converts back to world using a 100px probe at the line
        midpoint so it stays correct at any zoom / ortho scale."""
        from bpy_extras.view3d_utils import (region_2d_to_location_3d,
                                             location_3d_to_region_2d)
        region = context.region
        rv3d = context.region_data
        mouse_2d = Vector((event.mouse_region_x, event.mouse_region_y))

        obj = dim.obj
        # HB5 dimension splines are POLY (4-component points), not bezier.
        pts = obj.data.splines[0].points
        p1_world = obj.matrix_world @ Vector(pts[0].co[:3])
        p2_world = obj.matrix_world @ Vector(pts[1].co[:3])

        p1_2d = location_3d_to_region_2d(region, rv3d, p1_world)
        p2_2d = location_3d_to_region_2d(region, rv3d, p2_world)
        if p1_2d is None or p2_2d is None:
            return 0

        line_vec = p2_2d - p1_2d
        line_len = line_vec.length
        if line_len == 0:
            return 0
        line_unitvec = line_vec / line_len
        point_vec = mouse_2d - p1_2d
        # 2D cross product -> signed perpendicular distance in pixels.
        cross = line_unitvec.x * point_vec.y - line_unitvec.y * point_vec.x

        mid_world = (p1_world + p2_world) / 2
        ref_2d = (p1_2d + p2_2d) / 2
        ref_world = region_2d_to_location_3d(region, rv3d, ref_2d, mid_world)
        ref_world_offset = region_2d_to_location_3d(
            region, rv3d, ref_2d + Vector((0, 100)), mid_world)
        if ref_world is None or ref_world_offset is None:
            return cross * 0.001  # fallback scale
        world_per_pixel = (ref_world_offset - ref_world).length / 100
        return cross * world_per_pixel

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            current = self.get_mouse_distance_from_line(
                context, event, self.reference_dim)
            delta = current - self.reference_initial_length
            for dim, initial_length in self.dimensions:
                dim.set_input("Leader Length", initial_length + delta)
            if context.area:
                context.area.header_text_set(
                    "Delta: %s | %d dimension(s) | LMB: Confirm | RMB/ESC: Cancel"
                    % (units.unit_to_string(
                        context.scene.unit_settings, abs(delta)),
                       len(self.dimensions)))

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if context.area:
                context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for dim, initial_length in self.dimensions:
                dim.set_input("Leader Length", initial_length)
            if context.area:
                context.area.header_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.dimensions = []
        self.reference_dim = None
        self.reference_initial_length = 0
        for obj in context.selected_objects:
            if not obj.get('IS_DIMENSION'):
                continue
            dim = hb_types.GeoNodeDimension(obj)
            initial_length = dim.get_input("Leader Length")
            self.dimensions.append((dim, initial_length))
            # Active object is the reference; first found otherwise.
            if obj == context.active_object or self.reference_dim is None:
                self.reference_dim = dim
                self.reference_initial_length = initial_length

        if not self.dimensions:
            self.report({'WARNING'}, "No dimensions selected")
            return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)
        if context.area:
            context.area.header_text_set(
                "Move mouse to adjust leader length | %d dimension(s) | "
                "LMB: Confirm | RMB/ESC: Cancel" % len(self.dimensions))
        return {'RUNNING_MODAL'}


class HOME_BUILDER_OT_move_dimension_text(bpy.types.Operator):
    """Freely place a dimension's text with the mouse. Drives the
    'Offset Text X Amount' (along the line) and 'Offset Text Amount'
    (perpendicular) GeoNode inputs together, so the text follows the
    cursor instead of the user hand-tuning two offset fields. Applies
    the same delta to every selected dimension (active is the
    reference), mirroring Adjust Leader Length."""
    bl_idname = "home_builder.move_dimension_text"
    bl_label = "Move Text"
    bl_description = "Interactively move the dimension text of all selected dimensions with the mouse"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.get('IS_DIMENSION') for obj in context.selected_objects)

    def get_mouse_offset_components(self, context, event):
        """(along, perp) world offsets of the mouse from its invoke
        position, decomposed against the reference dimension's line
        direction. Screen-space math with a 100px world probe at the
        line midpoint (same approach as Adjust Leader Length) so it
        stays correct at any zoom / ortho scale and any dim rotation."""
        from bpy_extras.view3d_utils import (region_2d_to_location_3d,
                                             location_3d_to_region_2d)
        region = context.region
        rv3d = context.region_data
        mouse_2d = Vector((event.mouse_region_x, event.mouse_region_y))

        obj = self.reference_dim.obj
        pts = obj.data.splines[0].points
        p1_world = obj.matrix_world @ Vector(pts[0].co[:3])
        p2_world = obj.matrix_world @ Vector(pts[1].co[:3])
        p1_2d = location_3d_to_region_2d(region, rv3d, p1_world)
        p2_2d = location_3d_to_region_2d(region, rv3d, p2_world)
        if p1_2d is None or p2_2d is None:
            return 0.0, 0.0
        line_vec = p2_2d - p1_2d
        if line_vec.length == 0:
            return 0.0, 0.0
        line_unit = line_vec / line_vec.length

        d = mouse_2d - self.initial_mouse_2d
        along_px = d.dot(line_unit)
        # 2D cross -> signed perpendicular, same sign convention as the
        # leader modal (positive = leader side of the line).
        perp_px = line_unit.x * d.y - line_unit.y * d.x

        mid_world = (p1_world + p2_world) / 2
        ref_2d = (p1_2d + p2_2d) / 2
        ref_world = region_2d_to_location_3d(region, rv3d, ref_2d, mid_world)
        ref_world_offset = region_2d_to_location_3d(
            region, rv3d, ref_2d + Vector((0, 100)), mid_world)
        if ref_world is None or ref_world_offset is None:
            wpp = 0.001  # fallback scale
        else:
            wpp = (ref_world_offset - ref_world).length / 100
        return along_px * wpp, perp_px * wpp

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            along, perp = self.get_mouse_offset_components(context, event)
            for dim, init_x, init_y, _init_flag in self.dimensions:
                dim.set_input("Offset Text X Amount", init_x + along)
                dim.set_input("Offset Text Amount", init_y + perp)
            if context.area:
                context.area.header_text_set(
                    "Move text | %d dimension(s) | "
                    "LMB: Confirm | RMB/ESC: Cancel"
                    % len(self.dimensions))

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if context.area:
                context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for dim, init_x, init_y, init_flag in self.dimensions:
                dim.set_input("Offset Text X Amount", init_x)
                dim.set_input("Offset Text Amount", init_y)
                dim.set_input("Offset Text From Line", init_flag)
            if context.area:
                context.area.header_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # Files saved before the text-offset fix carry the old node
        # group where vertical dims could only move horizontally --
        # heal it before driving the offsets (no-op when current).
        hb_types.ensure_dimension_text_offset_basis(
            bpy.data.node_groups.get('GeoNodeDimension'))
        self.dimensions = []
        self.reference_dim = None
        self.initial_mouse_2d = Vector((event.mouse_region_x,
                                        event.mouse_region_y))
        for obj in context.selected_objects:
            if not obj.get('IS_DIMENSION'):
                continue
            dim = hb_types.GeoNodeDimension(obj)
            init_x = dim.get_input("Offset Text X Amount") or 0.0
            init_y = dim.get_input("Offset Text Amount") or 0.0
            init_flag = bool(dim.get_input("Offset Text From Line"))
            # The perpendicular amount only applies while 'Offset Text
            # From Line' is on -- enable it for the session so the text
            # tracks the cursor in Y; cancel restores the stored flag.
            dim.set_input("Offset Text From Line", True)
            self.dimensions.append((dim, init_x, init_y, init_flag))
            if obj == context.active_object or self.reference_dim is None:
                self.reference_dim = dim

        if not self.dimensions:
            self.report({'WARNING'}, "No dimensions selected")
            return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)
        if context.area:
            context.area.header_text_set(
                "Move mouse to place text | %d dimension(s) | "
                "LMB: Confirm | RMB/ESC: Cancel" % len(self.dimensions))
        return {'RUNNING_MODAL'}


class HOME_BUILDER_OT_show_dimension_properties(bpy.types.Operator):
    bl_idname = "home_builder.dimension_options"
    bl_label = "Dimension Options"
    bl_description = "Edit the options for the active dimension and optionally push sizes to all dimensions / defaults"
    bl_options = {'UNDO'}

    # Batch actions (run in execute, after the live-preview check() edits).
    update_all_dimensions: bpy.props.BoolProperty(name="Update All Dimensions")  # type: ignore
    update_selected_dimensions: bpy.props.BoolProperty(name="Update Selected Dimensions")  # type: ignore
    set_defaults: bpy.props.BoolProperty(name="Set As Default")  # type: ignore

    # Per-dimension inputs. HB5 dimensions are TICK-based (no arrow inputs)
    # and have no Replace Text input - both dropped vs the pyclone original.
    text_size: bpy.props.FloatProperty(name="Text Size", default=units.inch(2), subtype='DISTANCE')  # type: ignore
    tick_length: bpy.props.FloatProperty(name="Tick Length", default=units.inch(1), subtype='DISTANCE')  # type: ignore
    tick_thickness: bpy.props.FloatProperty(name="Tick Thickness", default=units.inch(0.05), subtype='DISTANCE')  # type: ignore
    leader_length: bpy.props.FloatProperty(name="Leader Length", default=units.inch(5), subtype='DISTANCE')  # type: ignore
    line_thickness: bpy.props.FloatProperty(name="Line Thickness", default=units.inch(0.05), subtype='DISTANCE')  # type: ignore
    extend_line_amount: bpy.props.FloatProperty(name="Extend Line Amount", default=units.inch(1), subtype='DISTANCE')  # type: ignore
    offset_text: bpy.props.BoolProperty(name="Offset Text from Line")  # type: ignore
    offset_text_amount: bpy.props.FloatProperty(name="Offset Text Amount", default=units.inch(1), subtype='DISTANCE')  # type: ignore
    align_text_to_curve: bpy.props.BoolProperty(name="Align Text to Curve")  # type: ignore
    decimals: bpy.props.IntProperty(name="Decimals")  # type: ignore
    flip_arrows: bpy.props.BoolProperty(name="Flip Arrows")  # type: ignore
    flip_text: bpy.props.BoolProperty(name="Flip Text")  # type: ignore
    text_x_offset_amount: bpy.props.FloatProperty(name="Text X Offset Amount", default=0, subtype='DISTANCE')  # type: ignore
    additional_text: bpy.props.StringProperty(name="Additional Text")  # type: ignore
    additional_text_offset_y_amount: bpy.props.FloatProperty(name="Additional Text Offset Y Amount", default=0, subtype='DISTANCE')  # type: ignore
    additional_text_offset_x_amount: bpy.props.FloatProperty(name="Additional Text Offset X Amount", default=0, subtype='DISTANCE')  # type: ignore
    additional_text_size: bpy.props.FloatProperty(name="Additional Text Size", default=units.inch(2), subtype='DISTANCE')  # type: ignore
    replace_text: bpy.props.StringProperty(name="Replace Text")  # type: ignore

    # The active dimension being live-previewed; set in invoke().
    dimension = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        return bool(obj and obj.get('IS_DIMENSION'))

    def execute(self, context):
        hb_props = context.scene.home_builder

        if self.update_all_dimensions:
            for obj in context.scene.objects:
                if not obj.get('IS_DIMENSION'):
                    continue
                dim = hb_types.GeoNodeDimension(obj)
                dim.set_input('Tick Length', self.tick_length)
                dim.set_input('Tick Thickness', self.tick_thickness)
                dim.set_input('Line Thickness', self.line_thickness)
                dim.set_input('Text Size', self.text_size)
                dim.set_input('Extend Line', self.extend_line_amount)

        if self.update_selected_dimensions:
            for obj in context.selected_objects:
                if not obj.get('IS_DIMENSION'):
                    continue
                dim = hb_types.GeoNodeDimension(obj)
                dim.set_input('Leader Length', self.leader_length)

        if self.set_defaults:
            hb_props.annotation_dimension_tick_length = self.tick_length
            hb_props.annotation_dimension_tick_thickness = self.tick_thickness
            hb_props.annotation_dimension_line_thickness = self.line_thickness
            hb_props.annotation_dimension_text_size = self.text_size
            hb_props.annotation_dimension_extend_line = self.extend_line_amount

        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

    def check(self, context):
        """Live-apply the dialog values to the active dimension so edits
        preview in the viewport while the dialog is open."""
        d = self.dimension
        if d is None:
            return True
        d.set_input('Tick Length', self.tick_length)
        d.set_input('Tick Thickness', self.tick_thickness)
        d.set_input('Line Thickness', self.line_thickness)
        d.set_input('Text Size', self.text_size)
        d.set_input('Leader Length', self.leader_length)
        d.set_input('Extend Line', self.extend_line_amount)
        d.set_input('Align Text To Curve', self.align_text_to_curve)
        d.set_input('Offset Text From Line', self.offset_text)
        d.set_input('Offset Text Amount', self.offset_text_amount)
        d.set_input('Flip Arrows', self.flip_arrows)
        d.set_input('Flip Text', self.flip_text)
        d.set_input('Decimals', self.decimals)
        d.set_input('Additional Text', self.additional_text)
        d.set_input('Additional Text Y Offset', self.additional_text_offset_y_amount)
        d.set_input('Additional Text X Offset', self.additional_text_offset_x_amount)
        d.set_input('Additional Text Size', self.additional_text_size)
        d.set_input('Replace Text', self.replace_text)
        d.set_input('Offset Text X Amount', self.text_x_offset_amount)
        if context.area:
            context.area.tag_redraw()
        return True

    def invoke(self, context, event):
        self.dimension = hb_types.GeoNodeDimension(context.object)
        d = self.dimension
        self.tick_length = d.get_input("Tick Length")
        self.tick_thickness = d.get_input("Tick Thickness")
        self.line_thickness = d.get_input("Line Thickness")
        self.text_size = d.get_input("Text Size")
        self.leader_length = d.get_input("Leader Length")
        self.extend_line_amount = d.get_input("Extend Line")
        self.align_text_to_curve = d.get_input("Align Text To Curve")
        self.offset_text = d.get_input("Offset Text From Line")
        self.offset_text_amount = d.get_input("Offset Text Amount")
        self.flip_arrows = d.get_input("Flip Arrows")
        self.flip_text = d.get_input("Flip Text")
        self.decimals = d.get_input("Decimals")
        self.additional_text = d.get_input("Additional Text") or ""
        self.additional_text_offset_y_amount = d.get_input("Additional Text Y Offset")
        self.additional_text_offset_x_amount = d.get_input("Additional Text X Offset")
        self.additional_text_size = d.get_input("Additional Text Size")
        self.replace_text = d.get_input("Replace Text") or ""
        self.text_x_offset_amount = d.get_input("Offset Text X Amount")
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.label(text="Leader Length")
        row.prop(self, 'leader_length', text="")
        box.prop(self, 'update_selected_dimensions')
        row = box.row()
        row.label(text="Decimals")
        row.prop(self, 'decimals', text="")
        row = box.row()
        row.label(text="Replace Text")
        row.prop(self, 'replace_text', text="")
        row = box.row()
        row.prop(self, 'flip_arrows', text="Flip Arrows")
        row.prop(self, 'flip_text', text="Flip Text")
        row = box.row()
        row.prop(self, 'offset_text')
        if self.offset_text:
            row.prop(self, 'offset_text_amount', text="")

        box = layout.box()
        row = box.row()
        row.label(text="Text Size")
        row.prop(self, 'text_size', text="")
        row = box.row()
        row.label(text="Tick Length")
        row.prop(self, 'tick_length', text="")
        row = box.row()
        row.label(text="Tick Thickness")
        row.prop(self, 'tick_thickness', text="")
        row = box.row()
        row.label(text="Line Thickness")
        row.prop(self, 'line_thickness', text="")
        row = box.row()
        row.label(text="Extend Line Amount")
        row.prop(self, 'extend_line_amount', text="")
        box.prop(self, 'align_text_to_curve')
        row = box.row()
        row.label(text="Text X Offset Amount")
        row.prop(self, 'text_x_offset_amount', text="")

        box = layout.box()
        row = box.row()
        row.label(text="Additional Text")
        row.prop(self, 'additional_text', text="")
        if self.additional_text != "":
            row = box.row()
            row.label(text="Offset")
            row.prop(self, 'additional_text_offset_x_amount', text="X")
            row.prop(self, 'additional_text_offset_y_amount', text="Y")
            row = box.row()
            row.label(text="Size")
            row.prop(self, 'additional_text_size', text="")

        box = layout.box()
        row = box.row()
        row.prop(self, 'update_all_dimensions')
        row.prop(self, 'set_defaults')


class HOME_BUILDER_MT_dimension_commands(bpy.types.Menu):
    bl_label = "Dimension Commands"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        # Honor a per-object prompt operator if one was tagged on the dim.
        if obj and obj.get("PROMPT_ID"):
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator(obj["PROMPT_ID"], icon='WINDOW')
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("home_builder.dimension_options", text="Dimension Options", icon='WINDOW')
        layout.separator()
        layout.operator("home_builder.flip_dimensions", text="Flip Dimensions", icon='ARROW_LEFTRIGHT')
        layout.operator("home_builder.flip_dimension_text", text="Flip Text", icon='FILE_FONT')
        layout.operator("home_builder.adjust_dimension_leader_length", text="Adjust Leader Length", icon='DRIVER_DISTANCE')
        layout.operator("home_builder.move_dimension_text", text="Move Text", icon='FONT_DATA')
        layout.operator("home_builder.update_dimensions", text="Update Dimensions", icon='FILE_REFRESH')
        layout.separator()
        layout.operator("object.delete", text="Delete Dimension", icon='X')


def draw_home_builder_menu(self, context):
    self.layout.menu("HOME_BUILDER_MT_main_menu")


classes = (
    HOME_BUILDER_OT_change_units,
    HOME_BUILDER_MT_change_units,
    HOME_BUILDER_MT_main_menu,
    HOME_BUILDER_MT_wall_commands,
    HOME_BUILDER_MT_soffit_commands,
    HOME_BUILDER_MT_door_commands,
    HOME_BUILDER_MT_window_commands,
    HOME_BUILDER_OT_flip_dimensions,
    HOME_BUILDER_OT_flip_dimension_text,
    HOME_BUILDER_OT_update_dimensions,
    HOME_BUILDER_OT_adjust_dimension_leader_length,
    HOME_BUILDER_OT_move_dimension_text,
    HOME_BUILDER_OT_show_dimension_properties,
    HOME_BUILDER_MT_dimension_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder_menu)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_home_builder_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
