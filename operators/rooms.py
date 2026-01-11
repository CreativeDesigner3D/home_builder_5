import bpy
from .. import hb_utils

# =============================================================================
# ROOM MANAGEMENT OPERATORS
# =============================================================================

class home_builder_OT_create_room(bpy.types.Operator):
    bl_idname = "home_builder.create_room"
    bl_label = "Create Room"
    bl_description = "Create a new room scene"
    bl_options = {'UNDO'}
    
    room_name: bpy.props.StringProperty(
        name="Room Name",
        description="Name for the new room",
        default="Room"
    )  # type: ignore
    
    def invoke(self, context, event):
        # Generate default name based on existing rooms
        existing_rooms = [s for s in bpy.data.scenes if s.get('IS_ROOM_SCENE')]
        self.room_name = f"Room {len(existing_rooms) + 1}"
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "room_name")
    
    def execute(self, context):
        # Store original scene settings
        original_scene = context.scene
        
        # Store unit settings
        unit_system = original_scene.unit_settings.system
        unit_scale = original_scene.unit_settings.scale_length
        unit_length = original_scene.unit_settings.length_unit
        
        # Store tool settings (snapping)
        tool_settings = context.tool_settings
        snap_elements = set(tool_settings.snap_elements)
        use_snap = tool_settings.use_snap
        snap_target = tool_settings.snap_target
        use_snap_grid_absolute = tool_settings.use_snap_grid_absolute
        use_snap_align_rotation = tool_settings.use_snap_align_rotation
        use_snap_backface_culling = tool_settings.use_snap_backface_culling
        
        # Create new scene
        new_scene = bpy.data.scenes.new(self.room_name)
        new_scene['IS_ROOM_SCENE'] = True
        
        # Save view state of original scene if it's a room
        if hb_utils.is_room_scene(original_scene):
            hb_utils.save_view_state(original_scene)
        
        # Switch to new scene
        context.window.scene = new_scene
        
        # Copy unit settings
        new_scene.unit_settings.system = unit_system
        new_scene.unit_settings.scale_length = unit_scale
        new_scene.unit_settings.length_unit = unit_length
        
        # Copy snap settings
        new_tool_settings = context.tool_settings
        new_tool_settings.snap_elements = snap_elements
        new_tool_settings.use_snap = use_snap
        new_tool_settings.snap_target = snap_target
        new_tool_settings.use_snap_grid_absolute = use_snap_grid_absolute
        new_tool_settings.use_snap_align_rotation = use_snap_align_rotation
        new_tool_settings.use_snap_backface_culling = use_snap_backface_culling
        
        # Mark original scene as room if not already marked and not a layout
        if not original_scene.get('IS_LAYOUT_VIEW') and not original_scene.get('IS_ROOM_SCENE'):
            original_scene['IS_ROOM_SCENE'] = True
        
        self.report({'INFO'}, f"Created room: {self.room_name}")
        return {'FINISHED'}


class home_builder_OT_switch_room(bpy.types.Operator):
    bl_idname = "home_builder.switch_room"
    bl_label = "Switch Room"
    bl_description = "Switch to a different room scene"
    bl_options = {'UNDO'}
    
    scene_name: bpy.props.StringProperty(name="Scene Name")  # type: ignore
    
    def execute(self, context):
        if self.scene_name in bpy.data.scenes:
            # Save current view state if in a room scene
            current_scene = context.scene
            if hb_utils.is_room_scene(current_scene):
                hb_utils.save_view_state(current_scene)
            
            # Switch to target scene
            target_scene = bpy.data.scenes[self.scene_name]
            context.window.scene = target_scene
            
            # Restore view state for the target room
            if hb_utils.is_room_scene(target_scene):
                hb_utils.restore_view_state(target_scene)
            
            self.report({'INFO'}, f"Switched to: {self.scene_name}")
        else:
            self.report({'WARNING'}, f"Scene not found: {self.scene_name}")
        return {'FINISHED'}


class home_builder_OT_delete_room(bpy.types.Operator):
    bl_idname = "home_builder.delete_room"
    bl_label = "Delete Room"
    bl_description = "Delete a room scene"
    bl_options = {'UNDO'}
    
    scene_name: bpy.props.StringProperty(name="Scene Name")  # type: ignore
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        if self.scene_name not in bpy.data.scenes:
            self.report({'WARNING'}, f"Scene not found: {self.scene_name}")
            return {'CANCELLED'}
        
        scene_to_delete = bpy.data.scenes[self.scene_name]
        
        # Don't allow deleting the last room
        room_scenes = [s for s in bpy.data.scenes if s.get('IS_ROOM_SCENE') or (not s.get('IS_LAYOUT_VIEW'))]
        if len(room_scenes) <= 1:
            self.report({'WARNING'}, "Cannot delete the last room")
            return {'CANCELLED'}
        
        # If deleting current scene, switch to another first
        if context.scene == scene_to_delete:
            for scene in bpy.data.scenes:
                if scene != scene_to_delete and not scene.get('IS_LAYOUT_VIEW'):
                    context.window.scene = scene
                    break
        
        scene_name = scene_to_delete.name
        bpy.data.scenes.remove(scene_to_delete)
        
        self.report({'INFO'}, f"Deleted room: {scene_name}")
        return {'FINISHED'}


class home_builder_OT_rename_room(bpy.types.Operator):
    bl_idname = "home_builder.rename_room"
    bl_label = "Rename Room"
    bl_description = "Rename the current room"
    bl_options = {'UNDO'}
    
    new_name: bpy.props.StringProperty(
        name="New Name",
        description="New name for the room"
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def invoke(self, context, event):
        self.new_name = context.scene.name
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")
    
    def execute(self, context):
        old_name = context.scene.name
        context.scene.name = self.new_name
        self.report({'INFO'}, f"Renamed '{old_name}' to '{self.new_name}'")
        return {'FINISHED'}


class home_builder_OT_duplicate_room(bpy.types.Operator):
    bl_idname = "home_builder.duplicate_room"
    bl_label = "Duplicate Room"
    bl_description = "Duplicate the current room scene"
    bl_options = {'UNDO'}
    
    new_name: bpy.props.StringProperty(
        name="New Name",
        description="Name for the duplicated room"
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def invoke(self, context, event):
        self.new_name = context.scene.name + " Copy"
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")
    
    def execute(self, context):
        original_scene = context.scene
        
        # Create new scene by copying
        new_scene = original_scene.copy()
        new_scene.name = self.new_name
        new_scene['IS_ROOM_SCENE'] = True
        
        # Save view state of original scene if it's a room
        if hb_utils.is_room_scene(original_scene):
            hb_utils.save_view_state(original_scene)
        
        # Save view state of original scene
        if hb_utils.is_room_scene(original_scene):
            hb_utils.save_view_state(original_scene)
        
        # Switch to new scene
        context.window.scene = new_scene
        
        self.report({'INFO'}, f"Duplicated room as: {self.new_name}")
        return {'FINISHED'}


class home_builder_OT_move_room_scene(bpy.types.Operator):
    """Move room scene up or down in the list"""
    bl_idname = "home_builder.move_room_scene"
    bl_label = "Move Room Scene"
    bl_description = "Move room scene up or down in the list"
    bl_options = {'UNDO'}
    
    move_up: bpy.props.BoolProperty(name="Move Up") # type: ignore

    def ensure_sort_orders_initialized(self, room_scenes):
        """Make sure all scenes have unique sort_order values."""
        orders = [s.home_builder.sort_order for s in room_scenes]
        if len(set(orders)) <= 1:
            # Initialize based on name order
            sorted_by_name = sorted(room_scenes, key=lambda s: s.name)
            for i, scene in enumerate(sorted_by_name):
                scene.home_builder.sort_order = i

    def execute(self, context):
        # Get room scenes (not layout or detail views)
        room_scenes = [s for s in bpy.data.scenes 
                      if not s.get('IS_LAYOUT_VIEW') and not s.get('IS_DETAIL_VIEW')]
        
        if len(room_scenes) < 2:
            return {'CANCELLED'}
        
        # Ensure sort orders are initialized
        self.ensure_sort_orders_initialized(room_scenes)
        
        # Sort by sort_order
        room_scenes = sorted(room_scenes, key=lambda s: s.home_builder.sort_order)
        
        scene = context.scene
        
        # Check if current scene is a room scene
        if scene not in room_scenes:
            return {'CANCELLED'}
        
        idx = room_scenes.index(scene)
        
        # Check boundaries
        if idx == 0 and self.move_up:
            return {'CANCELLED'}
        if idx == len(room_scenes) - 1 and not self.move_up:
            return {'CANCELLED'}
        
        # Get neighbor scene
        if self.move_up:
            neighbor = room_scenes[idx - 1]
        else:
            neighbor = room_scenes[idx + 1]
        
        # Swap sort_order values
        scene.home_builder.sort_order, neighbor.home_builder.sort_order = \
            neighbor.home_builder.sort_order, scene.home_builder.sort_order
        
        return {'FINISHED'}


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    home_builder_OT_create_room,
    home_builder_OT_switch_room,
    home_builder_OT_delete_room,
    home_builder_OT_rename_room,
    home_builder_OT_duplicate_room,
    home_builder_OT_move_room_scene,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
