import bpy
import math
from mathutils import Vector
from .... import hb_types, hb_project, hb_snap, hb_utils, units


def create_snap_line_mesh(wall_obj, x_position):
    """Create a visible vertical line mesh on a wall at the given X position."""
    wall_node = hb_types.GeoNodeWall(wall_obj)
    wall_height = wall_node.get_input('Height')
    wall_thickness = wall_node.get_input('Thickness')
    
    line_width = units.inch(0.25)
    
    verts = [
        (0, 0, 0),
        (line_width, 0, 0),
        (line_width, 0, wall_height),
        (0, 0, wall_height),
        (0, wall_thickness, 0),
        (line_width, wall_thickness, 0),
        (line_width, wall_thickness, wall_height),
        (0, wall_thickness, wall_height),
    ]
    
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 3, 7, 4),
        (1, 5, 6, 2),
    ]
    
    mesh = bpy.data.meshes.new('Snap Line')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new('Snap Line', mesh)
    obj.parent = wall_obj
    obj.location.x = x_position - line_width / 2
    
    obj['IS_SNAP_LINE'] = True
    obj['SNAP_X_POSITION'] = x_position
    obj['MENU_ID'] = 'HOME_BUILDER_MT_snap_line_commands'
    
    mat = bpy.data.materials.new(name="Snap Line Material")
    mat.use_nodes = True
    mat.diffuse_color = (1.0, 0.6, 0.0, 0.7)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 0.6, 0.0, 1.0)
        bsdf.inputs['Alpha'].default_value = 0.7
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    obj.data.materials.append(mat)
    
    obj.color = (1.0, 0.6, 0.0, 0.7)
    obj.show_in_front = True
    
    return obj


def get_dimension_rotation(context, base_rotation_z):
    """Calculate dimension rotation to face the camera based on view angle."""
    region_3d = None
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            region_3d = area.spaces.active.region_3d
            break
    
    if not region_3d:
        return (0, 0, base_rotation_z), True
    
    view_matrix = region_3d.view_matrix
    view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
    vertical_component = abs(view_dir.z)
    
    if vertical_component > 0.7:
        return (0, 0, base_rotation_z), True
    else:
        return (math.radians(90), 0, base_rotation_z), False


class hb_frameless_OT_place_snap_line(bpy.types.Operator):
    """Place a snap line on a wall to create a cabinet placement boundary"""
    bl_idname = "hb_frameless.place_snap_line"
    bl_label = "Place Snap Line"
    bl_description = "Click on a wall to place a snap line boundary"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Modal state
    preview_obj = None
    selected_wall = None
    region = None
    mouse_pos = None
    hit_location = None
    hit_object = None
    hit_face_index = None
    hit_grid = False
    view_point = None
    
    # Snap line position
    snap_x = 0.0
    wall_length = 0.0
    
    # Dimensions
    dim_left = None
    dim_right = None
    
    # Typing state
    typing_active = False
    typing_target = None  # 'LEFT' or 'RIGHT'
    typed_value = ""
    
    _header_text = "Click on a wall to place snap line | ESC to cancel"
    
    def find_wall_from_hit(self, hit_obj):
        """Walk up parent chain to find wall."""
        obj = hit_obj
        while obj:
            if obj.get('IS_WALL_BP'):
                return obj
            obj = obj.parent
        return None
    
    def create_dimensions(self, context):
        """Create left and right dimension annotations."""
        placement_text_size = units.inch(3)
        
        self.dim_left = hb_types.GeoNodeDimension()
        self.dim_left.create("Dim_SnapLine_Left")
        self.dim_left.set_input("Text Size", placement_text_size)
        self.dim_left.obj.show_in_front = True
        
        self.dim_right = hb_types.GeoNodeDimension()
        self.dim_right.create("Dim_SnapLine_Right")
        self.dim_right.set_input("Text Size", placement_text_size)
        self.dim_right.obj.show_in_front = True
    
    def update_dimensions(self, context):
        """Update dimension positions and values."""
        if not self.dim_left or not self.dim_right or not self.selected_wall:
            return
        
        wall_node = hb_types.GeoNodeWall(self.selected_wall)
        wall_height = wall_node.get_input('Height')
        wall_thickness = wall_node.get_input('Thickness')
        wall_rotation_z = self.selected_wall.rotation_euler.z
        wall_matrix = self.selected_wall.matrix_world
        
        dim_rotation, is_plan_view = get_dimension_rotation(context, wall_rotation_z)
        
        left_dist = self.snap_x
        right_dist = self.wall_length - self.snap_x
        
        if is_plan_view:
            dim_z = wall_height + units.inch(4)
            dim_y = -units.inch(2)
        else:
            dim_z = wall_height / 2
            dim_y = 0
        
        # Left dimension (wall start to snap line)
        self.dim_left.obj.parent = None
        if left_dist > units.inch(0.5):
            local_pos = Vector((0, dim_y, dim_z))
            self.dim_left.obj.location = wall_matrix @ local_pos
            self.dim_left.obj.rotation_euler = dim_rotation
            self.dim_left.obj.data.splines[0].points[1].co = (left_dist, 0, 0, 1)
            self.dim_left.set_decimal()
            self.dim_left.obj.hide_set(False)
        else:
            self.dim_left.obj.hide_set(True)
        
        # Right dimension (snap line to wall end)
        self.dim_right.obj.parent = None
        if right_dist > units.inch(0.5):
            local_pos = Vector((self.snap_x, dim_y, dim_z))
            self.dim_right.obj.location = wall_matrix @ local_pos
            self.dim_right.obj.rotation_euler = dim_rotation
            self.dim_right.obj.data.splines[0].points[1].co = (right_dist, 0, 0, 1)
            self.dim_right.set_decimal()
            self.dim_right.obj.hide_set(False)
        else:
            self.dim_right.obj.hide_set(True)
    
    def cleanup_dimensions(self):
        """Remove dimension objects."""
        if self.dim_left and self.dim_left.obj:
            bpy.data.objects.remove(self.dim_left.obj, do_unlink=True)
            self.dim_left = None
        if self.dim_right and self.dim_right.obj:
            bpy.data.objects.remove(self.dim_right.obj, do_unlink=True)
            self.dim_right = None
    
    def set_snap_position(self, x_pos):
        """Set the snap line X position, clamped to wall length."""
        self.snap_x = max(0, min(x_pos, self.wall_length))
        if self.preview_obj:
            line_width = units.inch(0.25)
            self.preview_obj.location.x = self.snap_x - line_width / 2
            self.preview_obj['SNAP_X_POSITION'] = self.snap_x
    
    def start_typing(self, target):
        """Start typing mode for left or right distance."""
        self.typing_active = True
        self.typing_target = target
        self.typed_value = ""
    
    def cancel_typing(self):
        """Cancel typing mode."""
        self.typing_active = False
        self.typing_target = None
        self.typed_value = ""
    
    def apply_typed_value(self, context):
        """Apply the typed distance value."""
        if not self.typed_value:
            self.cancel_typing()
            return
        
        try:
            value = float(self.typed_value)
        except ValueError:
            self.cancel_typing()
            return
        
        # Plain typed numbers are interpreted using the scene's unit
        # system, matching how other placement operators (doors/windows)
        # parse typed distances - not hardcoded to inches.
        unit_settings = context.scene.unit_settings
        if unit_settings.system == 'IMPERIAL':
            value_meters = units.inch(value)
        elif unit_settings.length_unit == 'MILLIMETERS':
            value_meters = units.millimeter(value)
        elif unit_settings.length_unit == 'CENTIMETERS':
            value_meters = units.centimeter(value)
        else:
            value_meters = value  # meters

        if self.typing_target == 'LEFT':
            self.set_snap_position(value_meters)
        elif self.typing_target == 'RIGHT':
            self.set_snap_position(self.wall_length - value_meters)
        
        self.update_dimensions(context)
        self.cancel_typing()
    
    def handle_typing_event(self, event):
        """Handle keyboard input during typing mode. Returns True if event was consumed."""
        if not self.typing_active:
            return False
        
        if event.type == 'RET' and event.value == 'PRESS':
            return True  # Consumed but applied in modal
        
        if event.type == 'ESC' and event.value == 'PRESS':
            self.cancel_typing()
            return True
        
        if event.value != 'PRESS':
            return False
        
        if event.type == 'BACK_SPACE':
            if self.typed_value:
                self.typed_value = self.typed_value[:-1]
            return True
        
        # Number keys
        char = None
        num_types = {
            'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
            'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9',
            'NUMPAD_0': '0', 'NUMPAD_1': '1', 'NUMPAD_2': '2', 'NUMPAD_3': '3',
            'NUMPAD_4': '4', 'NUMPAD_5': '5', 'NUMPAD_6': '6', 'NUMPAD_7': '7',
            'NUMPAD_8': '8', 'NUMPAD_9': '9',
            'PERIOD': '.', 'NUMPAD_PERIOD': '.',
        }
        
        char = num_types.get(event.type)
        if char:
            if char == '.' and '.' in self.typed_value:
                return True  # Only one decimal point
            self.typed_value += char
            return True
        
        return False
    
    def update_header_text(self, context):
        """Update the header text based on current state."""
        unit_settings = context.scene.unit_settings
        
        if self.typing_active:
            side = "Left" if self.typing_target == 'LEFT' else "Right"
            text = f"{side} Distance: {self.typed_value}_ | Enter to confirm | ESC to cancel typing"
        elif self.selected_wall:
            left_str = units.unit_to_string(unit_settings, self.snap_x)
            right_str = units.unit_to_string(unit_settings, self.wall_length - self.snap_x)
            text = f"← {left_str} | {right_str} → | ← set left | → set right | Click place | ESC cancel"
        else:
            text = "Move cursor over a wall | ← set left | → set right | ESC to cancel"
        
        context.area.header_text_set(text)
    
    def update_preview(self, context):
        """Update the preview snap line position based on cursor."""
        if not self.hit_location or not self.hit_object:
            if self.preview_obj:
                self.preview_obj.hide_set(True)
            self.cleanup_dimensions()
            self.selected_wall = None
            return
        
        wall_obj = self.find_wall_from_hit(self.hit_object)
        if not wall_obj:
            if self.preview_obj:
                self.preview_obj.hide_set(True)
            self.cleanup_dimensions()
            self.selected_wall = None
            return
        
        # Get X position in wall local space
        local_loc = wall_obj.matrix_world.inverted() @ Vector(self.hit_location)
        cursor_x = local_loc.x
        cursor_x = hb_snap.snap_value_to_grid(cursor_x)
        
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall_node.get_input('Length')
        cursor_x = max(0, min(cursor_x, wall_length))
        
        # Wall changed - recreate everything
        if self.selected_wall != wall_obj:
            if self.preview_obj:
                bpy.data.objects.remove(self.preview_obj, do_unlink=True)
                self.preview_obj = None
            self.cleanup_dimensions()
            
            self.selected_wall = wall_obj
            self.wall_length = wall_length
            self.snap_x = cursor_x
            
            self.preview_obj = create_snap_line_mesh(wall_obj, cursor_x)
            context.scene.collection.objects.link(self.preview_obj)
            self.preview_obj.color = (1.0, 0.6, 0.0, 0.4)
            
            self.create_dimensions(context)
        else:
            # Same wall, update position (only if not typing)
            if not self.typing_active:
                self.snap_x = cursor_x
                self.wall_length = wall_length
                self.set_snap_position(cursor_x)
        
        self.preview_obj.hide_set(False)
        self.update_dimensions(context)
    
    def confirm_placement(self, context):
        """Finalize the snap line placement."""
        if not self.preview_obj or not self.selected_wall:
            return False
        
        x_pos = self.snap_x
        
        # Remove preview
        bpy.data.objects.remove(self.preview_obj, do_unlink=True)
        self.preview_obj = None
        
        # Create final snap line
        snap_line = create_snap_line_mesh(self.selected_wall, x_pos)
        context.scene.collection.objects.link(snap_line)
        
        unit_settings = context.scene.unit_settings
        self.report({'INFO'}, f"Snap line placed at {units.unit_to_string(unit_settings, x_pos)}")
        return True
    
    def cleanup(self, context):
        """Remove preview objects, dimensions, and header text."""
        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None
        self.cleanup_dimensions()
        context.area.header_text_set(None)
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        
        # Handle typing events first
        if self.typing_active:
            if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
                self.apply_typed_value(context)
                if self.confirm_placement(context):
                    self.cleanup(context)
                    return {'FINISHED'}
                self.update_header_text(context)
                return {'RUNNING_MODAL'}
            
            if self.handle_typing_event(event):
                self.update_header_text(context)
                return {'RUNNING_MODAL'}
        
        # Arrow keys to start typing
        if event.value == 'PRESS':
            if event.type == 'LEFT_ARROW':
                if self.typing_active:
                    self.apply_typed_value(context)
                self.start_typing('LEFT')
                self.update_header_text(context)
                return {'RUNNING_MODAL'}
            
            if event.type == 'RIGHT_ARROW':
                if self.typing_active:
                    self.apply_typed_value(context)
                self.start_typing('RIGHT')
                self.update_header_text(context)
                return {'RUNNING_MODAL'}
        
        # Update snap/raycast (only when not typing)
        if not self.typing_active:
            self.mouse_pos = Vector((
                event.mouse_x - self.region.x,
                event.mouse_y - self.region.y
            ))
            
            if self.preview_obj:
                self.preview_obj.hide_set(True)
            hb_snap.main(self, event.ctrl, context)
            
            self.update_preview(context)
        
        self.update_header_text(context)
        
        # Left click to place
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.typing_active:
                self.apply_typed_value(context)
            if self.confirm_placement(context):
                self.cleanup(context)
                return {'FINISHED'}
        
        # ESC or right click to cancel
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.typing_active:
                self.cancel_typing()
                self.update_header_text(context)
                return {'RUNNING_MODAL'}
            self.cleanup(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Must be used in 3D viewport")
            return {'CANCELLED'}
        
        self.region = context.region
        self.selected_wall = None
        self.preview_obj = None
        self.dim_left = None
        self.dim_right = None
        self.typing_active = False
        self.typing_target = None
        self.typed_value = ""
        
        context.area.header_text_set(self._header_text)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class hb_frameless_OT_delete_snap_line(bpy.types.Operator):
    """Delete the selected snap line"""
    bl_idname = "hb_frameless.delete_snap_line"
    bl_label = "Delete Snap Line"
    bl_description = "Delete the selected snap line"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.get('IS_SNAP_LINE'):
            return True
        return False
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.get('IS_SNAP_LINE'):
            bpy.data.objects.remove(obj, do_unlink=True)
            self.report({'INFO'}, "Snap line deleted")
        return {'FINISHED'}


class hb_frameless_OT_delete_all_snap_lines(bpy.types.Operator):
    """Delete all snap lines in the scene"""
    bl_idname = "hb_frameless.delete_all_snap_lines"
    bl_label = "Delete All Snap Lines"
    bl_description = "Delete all snap lines from the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        removed = 0
        for obj in list(context.scene.objects):
            if obj.get('IS_SNAP_LINE'):
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
        self.report({'INFO'}, f"Removed {removed} snap line(s)")
        return {'FINISHED'}


class HOME_BUILDER_MT_snap_line_commands(bpy.types.Menu):
    bl_label = "Snap Line Commands"
    bl_idname = "HOME_BUILDER_MT_snap_line_commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.delete_snap_line", text="Delete Snap Line", icon='X')
        layout.operator("hb_frameless.delete_all_snap_lines", text="Delete All Snap Lines", icon='TRASH')


classes = (
    hb_frameless_OT_place_snap_line,
    hb_frameless_OT_delete_snap_line,
    hb_frameless_OT_delete_all_snap_lines,
    HOME_BUILDER_MT_snap_line_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
