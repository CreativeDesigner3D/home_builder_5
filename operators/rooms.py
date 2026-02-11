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
# ROOM LINKING
# =============================================================================

def get_room_scenes_enum(self, context):
    """Get enum items for room scenes (excluding current scene)."""
    scenes = [s for s in bpy.data.scenes
              if s != context.scene and not s.get('IS_LAYOUT_VIEW') and not s.get('IS_DETAIL_VIEW')]
    scenes.sort(key=lambda s: s.home_builder.sort_order)
    items = [(s.name, s.name, f"Link {s.name} into current scene") for s in scenes]
    if not items:
        items.append(('NONE', 'No Rooms Available', ''))
    return items


def organize_room_collections(scene):
    """
    Organize a room scene's objects into sub-collections by type.
    Creates: '{SceneName} - Walls', '{SceneName} - Lights', '{SceneName} - Products'
    Returns dict with keys 'walls', 'lights', 'products' mapping to collections.
    """
    name = scene.name
    
    # Collection names
    col_names = {
        'walls': f"{name} - Walls",
        'lights': f"{name} - Lights",
        'products': f"{name} - Products",
    }
    
    # Create or get sub-collections
    collections = {}
    for key, col_name in col_names.items():
        if col_name in bpy.data.collections:
            collections[key] = bpy.data.collections[col_name]
        else:
            col = bpy.data.collections.new(col_name)
            scene.collection.children.link(col)
            collections[key] = col
    
    # Gather top-level objects by category
    # We identify "root" objects and move them + all children
    
    wall_roots = set()
    light_objects = set()
    product_roots = set()
    floor_objects = set()
    
    for obj in scene.objects:
        if obj.get('IS_WALL_BP'):
            wall_roots.add(obj)
        elif obj.get('IS_ROOM_LIGHT'):
            light_objects.add(obj)
        elif obj.get('IS_FRAMELESS_CABINET_CAGE'):
            product_roots.add(obj)
        elif obj.get('IS_FLOOR_BP'):
            floor_objects.add(obj)
        elif obj.get('IS_ENTRY_DOOR_BP') or obj.get('IS_WINDOW_BP'):
            # Doors/windows on walls - treat as wall category
            wall_roots.add(obj)
        elif obj.get('IS_OBSTACLE'):
            product_roots.add(obj)
    
    def get_all_children(obj):
        """Recursively get all children of an object."""
        children = set()
        for child in obj.children:
            children.add(child)
            children.update(get_all_children(child))
        return children
    
    def move_to_collection(objects, target_col):
        """Move objects to target collection, removing from others."""
        for obj in objects:
            # Skip if already in target
            if obj.name in target_col.objects:
                continue
            # Link to target
            target_col.objects.link(obj)
            # Unlink from scene collection (but not from other sub-collections)
            if obj.name in scene.collection.objects:
                scene.collection.objects.unlink(obj)
    
    # Move walls + their children (exclude GeoNodeCage objects)
    wall_objects = set()
    for root in wall_roots:
        wall_objects.add(root)
        wall_objects.update(get_all_children(root))
    wall_objects = {obj for obj in wall_objects if not obj.get('IS_GEONODE_CAGE')}
    move_to_collection(wall_objects, collections['walls'])
    
    # Move lights
    move_to_collection(light_objects, collections['lights'])
    # Also move lights from "Room Lights" collection if it exists
    if "Room Lights" in bpy.data.collections:
        old_light_col = bpy.data.collections["Room Lights"]
        for obj in list(old_light_col.objects):
            if obj not in light_objects:
                light_objects.add(obj)
                collections['lights'].objects.link(obj)
            old_light_col.objects.unlink(obj)
        # Remove old collection if empty
        if len(old_light_col.objects) == 0:
            # Unlink from scene
            if old_light_col.name in scene.collection.children:
                scene.collection.children.unlink(old_light_col)
            bpy.data.collections.remove(old_light_col)
    
    # Move products + their children (cabinets, obstacles, floors)
    # Exclude GeoNodeCage objects (invisible parametric control objects)
    product_objects = set()
    for root in product_roots:
        product_objects.add(root)
        product_objects.update(get_all_children(root))
    for obj in floor_objects:
        product_objects.add(obj)
        product_objects.update(get_all_children(obj))
    product_objects = {obj for obj in product_objects if not obj.get('IS_GEONODE_CAGE')}
    move_to_collection(product_objects, collections['products'])
    
    return collections


class home_builder_OT_link_room(bpy.types.Operator):
    bl_idname = "home_builder.link_room"
    bl_label = "Link Room"
    bl_description = "Link a room's objects into the current scene as a collection instance"
    bl_options = {'UNDO'}
    
    room_scene: bpy.props.EnumProperty(
        name="Room",
        description="Room to link",
        items=get_room_scenes_enum
    )  # type: ignore
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Select Room to Link", icon='LINKED')
        box.prop(self, "room_scene", text="")
    
    def execute(self, context):
        if self.room_scene == 'NONE':
            self.report({'WARNING'}, "No room selected")
            return {'CANCELLED'}
        
        source_scene = bpy.data.scenes.get(self.room_scene)
        if not source_scene:
            self.report({'WARNING'}, f"Scene '{self.room_scene}' not found")
            return {'CANCELLED'}
        
        target_scene = context.scene
        room_name = source_scene.name
        
        # Check if already linked
        for obj in target_scene.objects:
            if obj.get('IS_LINKED_ROOM') and obj.get('LINKED_ROOM_SOURCE') == room_name:
                self.report({'WARNING'}, f"'{room_name}' is already linked. Unlink first to re-link.")
                return {'CANCELLED'}
        
        # Step 1: Organize source scene into sub-collections
        sub_collections = organize_room_collections(source_scene)
        
        # Step 2: Create a link collection with all categories
        link_col_name = f"{room_name} - Link"
        
        # Remove old link collection if it exists
        if link_col_name in bpy.data.collections:
            old_col = bpy.data.collections[link_col_name]
            for child in list(old_col.children):
                old_col.children.unlink(child)
            bpy.data.collections.remove(old_col)
        
        link_col = bpy.data.collections.new(link_col_name)
        
        # Link all sub-collections by default
        link_col.children.link(sub_collections['walls'])
        link_col.children.link(sub_collections['lights'])
        link_col.children.link(sub_collections['products'])
        
        # Link the link collection into the source scene
        if link_col.name not in source_scene.collection.children:
            source_scene.collection.children.link(link_col)
        
        # Hide the link collection in the source scene viewport
        for layer_col in source_scene.view_layers[0].layer_collection.children:
            if layer_col.name == link_col_name:
                layer_col.exclude = True
                break
        
        # Step 3: Create collection instance empty in the target scene
        empty = bpy.data.objects.new(f"Linked: {room_name}", None)
        empty.instance_type = 'COLLECTION'
        empty.instance_collection = link_col
        empty.empty_display_size = 0.5
        empty.empty_display_type = 'PLAIN_AXES'
        
        # Mark with custom properties
        empty['IS_LINKED_ROOM'] = True
        empty['LINKED_ROOM_SOURCE'] = room_name
        empty['LINKED_INCLUDE_WALLS'] = True
        empty['LINKED_INCLUDE_LIGHTS'] = True
        empty['LINKED_INCLUDE_PRODUCTS'] = True
        
        target_scene.collection.objects.link(empty)
        
        # Select the new empty so user can position it
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty
        
        self.report({'INFO'}, f"Linked '{room_name}' into '{target_scene.name}'")
        return {'FINISHED'}


class home_builder_OT_toggle_linked_room_category(bpy.types.Operator):
    bl_idname = "home_builder.toggle_linked_room_category"
    bl_label = "Toggle Linked Category"
    bl_description = "Toggle whether a category is included in the linked room"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name")  # type: ignore
    category: bpy.props.StringProperty(name="Category")  # type: ignore
    
    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        if not obj or not obj.get('IS_LINKED_ROOM'):
            self.report({'WARNING'}, "Linked room not found")
            return {'CANCELLED'}
        
        room_name = obj.get('LINKED_ROOM_SOURCE')
        link_col = obj.instance_collection
        if not link_col:
            self.report({'WARNING'}, "Link collection not found")
            return {'CANCELLED'}
        
        # Map category to property key and collection name
        cat_map = {
            'walls': ('LINKED_INCLUDE_WALLS', f"{room_name} - Walls"),
            'lights': ('LINKED_INCLUDE_LIGHTS', f"{room_name} - Lights"),
            'products': ('LINKED_INCLUDE_PRODUCTS', f"{room_name} - Products"),
        }
        
        if self.category not in cat_map:
            return {'CANCELLED'}
        
        prop_key, col_name = cat_map[self.category]
        sub_col = bpy.data.collections.get(col_name)
        if not sub_col:
            self.report({'WARNING'}, f"Collection '{col_name}' not found")
            return {'CANCELLED'}
        
        # Toggle
        currently_included = obj.get(prop_key, True)
        
        if currently_included:
            # Remove from link collection
            if sub_col.name in link_col.children:
                link_col.children.unlink(sub_col)
            obj[prop_key] = False
        else:
            # Add to link collection
            if sub_col.name not in link_col.children:
                link_col.children.link(sub_col)
            obj[prop_key] = True
        
        # Force viewport update
        context.view_layer.update()
        
        return {'FINISHED'}


class home_builder_OT_unlink_room(bpy.types.Operator):
    bl_idname = "home_builder.unlink_room"
    bl_label = "Unlink Room"
    bl_description = "Remove a linked room from the current scene"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name")  # type: ignore
    
    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        if not obj or not obj.get('IS_LINKED_ROOM'):
            self.report({'WARNING'}, "Linked room not found")
            return {'CANCELLED'}
        
        room_name = obj.get('LINKED_ROOM_SOURCE', 'Unknown')
        
        # Clean up the link collection
        link_col = obj.instance_collection
        if link_col:
            # Unlink children (don't delete the sub-collections)
            for child in list(link_col.children):
                link_col.children.unlink(child)
            
            # Remove from source scene if linked there
            source_scene = bpy.data.scenes.get(room_name)
            if source_scene and link_col.name in source_scene.collection.children:
                source_scene.collection.children.unlink(link_col)
            
            bpy.data.collections.remove(link_col)
        
        # Remove the empty
        bpy.data.objects.remove(obj, do_unlink=True)
        
        self.report({'INFO'}, f"Unlinked '{room_name}'")
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
    home_builder_OT_link_room,
    home_builder_OT_toggle_linked_room_category,
    home_builder_OT_unlink_room,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
