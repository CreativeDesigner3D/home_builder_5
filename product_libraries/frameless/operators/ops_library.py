import bpy
import math
import os
import platform
import subprocess
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_placement, hb_snap, units

def get_user_library_path():
    """Get the default user library path for cabinet groups."""
    return os.path.join(os.path.expanduser("~"), "Documents", "Home Builder Library", "Cabinet Groups")

def get_all_cabinet_group_paths():
    """Get all cabinet group library paths (default + user libraries with cabinet_groups/)."""
    from .... import hb_assets
    all_paths = hb_assets.get_all_subfolder_paths("cabinet_groups")
    default_path = get_user_library_path()
    if os.path.isdir(default_path) and default_path not in all_paths:
        all_paths.insert(0, default_path)
    return all_paths

def get_cabinet_group_categories():
    """Get list of cabinet group categories across all library paths.
    
    Loose .blend files in the root are grouped under 'General'.
    """
    categories_set = set()
    has_loose_files = False
    
    for groups_path in get_all_cabinet_group_paths():
        if not os.path.exists(groups_path):
            continue
        for item in os.listdir(groups_path):
            item_path = os.path.join(groups_path, item)
            if os.path.isdir(item_path):
                # Only count as category if it has .blend files
                if any(f.endswith('.blend') for f in os.listdir(item_path)):
                    categories_set.add(item)
            elif item.endswith('.blend'):
                has_loose_files = True
    
    categories = [('ALL', 'All', 'Show all cabinet groups')]
    if has_loose_files:
        categories.append(('General', 'General', 'Uncategorized cabinet groups'))
    for c in sorted(categories_set):
        categories.append((c, c, c))
    
    return categories

def get_cabinet_group_category_enum_items(self, context):
    """Dynamic enum items for cabinet group category selection."""
    return get_cabinet_group_categories()

def get_user_library_items(category=None):
    """Get list of cabinet group files, optionally filtered by category."""
    items = []
    seen_names = set()

    def _scan_dir(search_path):
        """Scan a directory for .blend files and add to items."""
        if not os.path.exists(search_path):
            return
        for filename in sorted(os.listdir(search_path)):
            if filename.endswith('.blend'):
                name = filename[:-6]
                if name not in seen_names:
                    seen_names.add(name)
                    filepath = os.path.join(search_path, filename)
                    thumbnail_path = os.path.join(search_path, f"{name}.png")
                    has_thumbnail = os.path.exists(thumbnail_path)
                    items.append({
                        'name': name,
                        'filepath': filepath,
                        'thumbnail': thumbnail_path if has_thumbnail else None
                    })

    for library_path in get_all_cabinet_group_paths():
        if not os.path.exists(library_path):
            continue

        if category and category != 'NONE':
            if category == 'General':
                _scan_dir(library_path)
            else:
                _scan_dir(os.path.join(library_path, category))
        else:
            # No category filter - scan root and all subfolders
            _scan_dir(library_path)
            for item in sorted(os.listdir(library_path)):
                item_path = os.path.join(library_path, item)
                if os.path.isdir(item_path):
                    _scan_dir(item_path)

    return items


class hb_frameless_OT_save_cabinet_group_to_user_library(bpy.types.Operator):
    """Save Cabinet Group to User Library"""
    bl_idname = "hb_frameless.save_cabinet_group_to_user_library"
    bl_label = 'Save Cabinet Group to User Library'
    bl_description = "This will save the cabinet group to the user library"
    bl_options = {'UNDO'}

    cabinet_group_name: bpy.props.StringProperty(
        name="Cabinet Group Name",
        default=""
    )  # type: ignore
    
    save_path: bpy.props.StringProperty(
        name="Save Location",
        subtype='DIR_PATH',
        default=""
    )  # type: ignore

    save_category: bpy.props.StringProperty(
        name="Category",
        description="Category subfolder to save into (leave empty for root)",
        default=""
    )  # type: ignore
    
    create_thumbnail: bpy.props.BoolProperty(
        name="Create Thumbnail",
        description="Generate a thumbnail image for the library",
        default=True
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return False
        # Check if it's a cabinet group (cabinet cage with cabinet children)
        if 'IS_CAGE_GROUP' in obj:
            return True
        return False
    
    def invoke(self, context, event):
        self.cabinet_group_name = context.object.name
        
        # Set default save path to user documents
        
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "Home Builder Library", "Cabinet Groups")
        self.save_path = default_path
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "cabinet_group_name")
        layout.prop(self, "save_path")
        layout.prop(self, "save_category")
        layout.prop(self, "create_thumbnail")
    
    def execute(self, context):
        cabinet_group = context.object
        
        if not self.cabinet_group_name:
            self.report({'ERROR'}, "Please enter a name for the cabinet group")
            return {'CANCELLED'}
        
        if not self.save_path:
            self.report({'ERROR'}, "Please select a save location")
            return {'CANCELLED'}
        
        # Append category subfolder if specified
        actual_save_path = self.save_path
        if self.save_category.strip():
            actual_save_path = os.path.join(self.save_path, self.save_category.strip())

        # Create directory if it doesn't exist
        os.makedirs(actual_save_path, exist_ok=True)
        
        # Sanitize filename
        safe_name = "".join(c for c in self.cabinet_group_name if c.isalnum() or c in (' ', '-', '_')).strip()
        blend_filename = f"{safe_name}.blend"
        blend_filepath = os.path.join(actual_save_path, blend_filename)
        
        # Check if file already exists
        if os.path.exists(blend_filepath):
            self.report({'WARNING'}, f"File already exists: {blend_filename}. Overwriting.")
        
        # Collect all objects to save (cabinet group and all descendants)
        objects_to_save = self._collect_objects_recursive(cabinet_group)
        
        # Collect all data blocks used by these objects
        data_blocks = self._collect_data_blocks(objects_to_save)
        
        # Save to blend file
        bpy.data.libraries.write(
            blend_filepath,
            data_blocks,
            path_remap='RELATIVE_ALL',
            fake_user=True
        )
        
        # Generate thumbnail if requested
        if self.create_thumbnail:
            self._create_thumbnail(context, cabinet_group, actual_save_path, safe_name)
        
        self.report({'INFO'}, f"Saved cabinet group to: {blend_filepath}")
        return {'FINISHED'}
    
    def _collect_objects_recursive(self, obj):
        """Collect object and all its descendants."""
        objects = {obj}
        for child in obj.children:
            objects.update(self._collect_objects_recursive(child))
        return objects
    
    def _collect_data_blocks(self, objects):
        """Collect all data blocks needed to save the objects."""
        data_blocks = set()
        
        for obj in objects:
            data_blocks.add(obj)
            
            # Add object data (mesh, curve, etc.)
            if obj.data:
                data_blocks.add(obj.data)
            
            # Add materials
            if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'materials'):
                for mat in obj.data.materials:
                    if mat:
                        data_blocks.add(mat)
                        # Add material node tree textures
                        if mat.use_nodes and mat.node_tree:
                            for node in mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE' and node.image:
                                    data_blocks.add(node.image)
            
            # Add modifiers' objects (like geometry nodes)
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    data_blocks.add(mod.node_group)
        
        return data_blocks
    
    def _create_thumbnail(self, context, cabinet_group, save_path, name):
        """Create a thumbnail image for the cabinet group."""

        # Store current state
        original_camera = context.scene.camera
        original_render_x = context.scene.render.resolution_x
        original_render_y = context.scene.render.resolution_y
        original_render_percentage = context.scene.render.resolution_percentage
        original_engine = context.scene.render.engine
        original_filepath = context.scene.render.filepath
        
        try:
            # Get cabinet group bounds
            cage = types_frameless.Cabinet(cabinet_group)
            width = cage.get_input('Dim X')
            depth = cage.get_input('Dim Y')
            height = cage.get_input('Dim Z')
            
            # Create temporary camera
            cam_data = bpy.data.cameras.new("ThumbnailCam")
            cam_data.type = 'ORTHO'
            cam_obj = bpy.data.objects.new("ThumbnailCam", cam_data)
            context.scene.collection.objects.link(cam_obj)
            
            # Position camera for isometric-ish view
            center = cabinet_group.matrix_world @ Vector((width/2, -depth/2, height/2))
            
            # Camera distance based on largest dimension
            max_dim = max(width, depth, height)
            cam_data.ortho_scale = max_dim * 1.5
            
            # Position for 3/4 view
            cam_obj.location = center + Vector((max_dim, -max_dim, max_dim * 0.8))
            
            # Point camera at center
            direction = center - cam_obj.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.rotation_euler = rot_quat.to_euler()
            
            # Set up render
            context.scene.camera = cam_obj
            context.scene.render.resolution_x = 256
            context.scene.render.resolution_y = 256
            context.scene.render.resolution_percentage = 100
            context.scene.render.engine = 'BLENDER_WORKBENCH'
            context.scene.render.film_transparent = True
            context.scene.render.use_freestyle = True
            context.scene.render.line_thickness = .5
            
            # Render thumbnail
            thumbnail_path = os.path.join(save_path, f"{name}.png")
            context.scene.render.filepath = thumbnail_path
            bpy.ops.render.render(write_still=True)
            
            # Cleanup
            bpy.data.objects.remove(cam_obj)
            bpy.data.cameras.remove(cam_data)
            
        except Exception as e:
            print(f"Failed to create thumbnail: {e}")
        
        finally:
            # Restore original state
            context.scene.camera = original_camera
            context.scene.render.resolution_x = original_render_x
            context.scene.render.resolution_y = original_render_y
            context.scene.render.resolution_percentage = original_render_percentage
            context.scene.render.engine = original_engine
            context.scene.render.filepath = original_filepath


class hb_frameless_OT_load_cabinet_group_from_library(bpy.types.Operator, hb_placement.PlacementMixin):
    """Load Cabinet Group from User Library"""
    bl_idname = "hb_frameless.load_cabinet_group_from_library"
    bl_label = 'Load Cabinet Group from Library'
    bl_description = "Load a cabinet group from the user library. Click to place, Right-click or ESC to cancel"
    bl_options = {'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )  # type: ignore

    root_objects: list = []
    orphan_offsets: dict = {}  # {obj: Vector offset from first root}
    geo_node_refs: set = set()  # Objects referenced by geometry node modifiers

    @classmethod
    def poll(cls, context):
        return True

    def load_objects(self, context):
        """Load objects from the library file and return root objects."""
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
            data_to.meshes = data_from.meshes
            data_to.materials = data_from.materials
            data_to.node_groups = data_from.node_groups

        # Link all objects to the scene first so parent relationships resolve
        loaded_objects = []
        for obj in data_to.objects:
            if obj is not None:
                context.scene.collection.objects.link(obj)
                loaded_objects.append(obj)

        # Find root cabinet group objects (IS_CAGE_GROUP with no parent)
        self.root_objects = []
        for obj in loaded_objects:
            if obj.get('IS_CAGE_GROUP') and obj.parent is None:
                self.root_objects.append(obj)
                self.register_placement_object(obj)
            elif obj.parent is None:
                # Register orphan objects (e.g. pulls) for cleanup on cancel
                self.register_placement_object(obj)
        
        # Find objects referenced by geometry node Object inputs (e.g. hardware meshes)
        # These need to stay in the scene but should be hidden
        geo_node_refs = set()
        for obj in loaded_objects:
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    for item in mod.node_group.interface.items_tree:
                        if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.socket_type == 'NodeSocketObject':
                            try:
                                ref_obj = mod[item.identifier]
                                if ref_obj:
                                    geo_node_refs.add(ref_obj)
                            except (KeyError, TypeError):
                                pass

        # Hide geometry node reference objects (they must stay for modifiers)
        self.geo_node_refs = geo_node_refs
        for ref_obj in geo_node_refs:
            ref_obj.hide_set(True)
            ref_obj.hide_viewport = True
            ref_obj.hide_render = True

        # Compute offsets for remaining orphan parentless objects relative to first root
        # Exclude geo node reference objects from position tracking
        self.orphan_offsets = {}
        if self.root_objects:
            root_loc = self.root_objects[0].location.copy()
            for obj in self.placement_objects:
                if obj not in self.root_objects and obj.parent is None and obj not in geo_node_refs:
                    self.orphan_offsets[obj] = obj.location - root_loc

    def _set_hide_recursive(self, hide):
        """Hide/unhide root objects and all their children recursively.
        Skips geometry node reference objects (they stay permanently hidden)."""
        def _hide(obj):
            try:
                if obj in self.geo_node_refs:
                    return
                obj.hide_set(hide)
                for child in obj.children:
                    _hide(child)
            except ReferenceError:
                pass
        for obj in self.root_objects:
            _hide(obj)
        for obj in self.orphan_offsets:
            try:
                obj.hide_set(hide)
            except ReferenceError:
                pass

    def update_header(self, context):
        """Update header text with instructions."""
        text = "Click to place cabinet group | R: rotate 90° | Right-click/Esc: cancel"
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}

        self.init_placement(context)
        self.load_objects(context)

        if not self.root_objects:
            self.cancel_placement(context)
            self.report({'WARNING'}, "No cabinet groups found in file")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.root_objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj

        self.update_header(context)
        context.window.cursor_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        # Hide all loaded objects during raycast so we don't hit ourselves
        self._set_hide_recursive(True)
        self.update_snap(context, event)
        self._set_hide_recursive(False)

        # Update position to follow cursor
        if self.hit_location:
            snapped = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            for obj in self.root_objects:
                obj.location = snapped
            # Move orphan objects maintaining their offset from root
            for obj, offset in self.orphan_offsets.items():
                obj.location = snapped + offset

        # Left click - confirm placement
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            self.report({'INFO'}, f"Placed cabinet group from: {os.path.basename(self.filepath)}")
            return {'FINISHED'}

        # R key - rotate 90 degrees
        if event.type == 'R' and event.value == 'PRESS':
            for obj in self.root_objects:
                obj.rotation_euler.z += math.radians(90)
            return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # Pass through navigation events
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class hb_frameless_OT_refresh_user_library(bpy.types.Operator):
    """Refresh User Library"""
    bl_idname = "hb_frameless.refresh_user_library"
    bl_label = 'Refresh User Library'
    bl_description = "Refresh the list of items in the user library"

    def execute(self, context):
        # Clear cached previews so they get reloaded
        props_hb_frameless.clear_library_previews()
        
        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, "User library refreshed")
        return {'FINISHED'}


class hb_frameless_OT_open_user_library_folder(bpy.types.Operator):
    """Open User Library Folder"""
    bl_idname = "hb_frameless.open_user_library_folder"
    bl_label = 'Open User Library Folder'
    bl_description = "Open the user library folder in file explorer"

    def execute(self, context):
        
        library_path = get_user_library_path()
        
        if not os.path.exists(library_path):
            os.makedirs(library_path, exist_ok=True)
        
        # Open folder in system file explorer
        if platform.system() == 'Windows':
            os.startfile(library_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', library_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', library_path])
        
        return {'FINISHED'}


class hb_frameless_OT_delete_library_item(bpy.types.Operator):
    """Delete Item from User Library"""
    bl_idname = "hb_frameless.delete_library_item"
    bl_label = 'Delete Library Item'
    bl_description = "Delete a cabinet group from the user library"

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )  # type: ignore
    
    item_name: bpy.props.StringProperty(
        name="Item Name"
    )  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Delete the blend file
        os.remove(self.filepath)
        
        # Delete thumbnail if it exists
        thumbnail_path = self.filepath.replace('.blend', '.png')
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        # Clear preview cache so it doesn't show deleted item
        props_hb_frameless.clear_library_previews()
        
        self.report({'INFO'}, f"Deleted: {self.item_name}")
        
        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        return {'FINISHED'}


classes = (
    hb_frameless_OT_save_cabinet_group_to_user_library,
    hb_frameless_OT_load_cabinet_group_from_library,
    hb_frameless_OT_refresh_user_library,
    hb_frameless_OT_open_user_library_folder,
    hb_frameless_OT_delete_library_item,
)

register, unregister = bpy.utils.register_classes_factory(classes)
