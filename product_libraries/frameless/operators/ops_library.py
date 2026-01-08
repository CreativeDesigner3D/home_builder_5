import bpy
import math
import os
import platform
import subprocess
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, units

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
        layout.prop(self, "create_thumbnail")
    
    def execute(self, context):
        cabinet_group = context.object
        
        if not self.cabinet_group_name:
            self.report({'ERROR'}, "Please enter a name for the cabinet group")
            return {'CANCELLED'}
        
        if not self.save_path:
            self.report({'ERROR'}, "Please select a save location")
            return {'CANCELLED'}
        
        # Create directory if it doesn't exist
        os.makedirs(self.save_path, exist_ok=True)
        
        # Sanitize filename
        safe_name = "".join(c for c in self.cabinet_group_name if c.isalnum() or c in (' ', '-', '_')).strip()
        blend_filename = f"{safe_name}.blend"
        blend_filepath = os.path.join(self.save_path, blend_filename)
        
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
            self._create_thumbnail(context, cabinet_group, self.save_path, safe_name)
        
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


class hb_frameless_OT_load_cabinet_group_from_library(bpy.types.Operator):
    """Load Cabinet Group from User Library"""
    bl_idname = "hb_frameless.load_cabinet_group_from_library"
    bl_label = 'Load Cabinet Group from Library'
    bl_description = "Load a cabinet group from the user library into the current scene"
    bl_options = {'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Link or append the cabinet group from the library file
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            # Get all objects from the file
            data_to.objects = data_from.objects
            data_to.meshes = data_from.meshes
            data_to.materials = data_from.materials
            data_to.node_groups = data_from.node_groups
        
        # Find the root cabinet group (the one without a parent that is a cabinet cage)
        root_objects = []
        for obj in data_to.objects:
            if obj is not None:
                # Link to scene
                context.scene.collection.objects.link(obj)
                
                # Check if it's a root cabinet group
                if 'IS_FRAMELESS_CABINET_CAGE' in obj and obj.parent is None:
                    root_objects.append(obj)
        
        # Select the imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in root_objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj
        
        # Position at 3D cursor
        for obj in root_objects:
            obj.location = context.scene.cursor.location
        
        self.report({'INFO'}, f"Loaded cabinet group from: {os.path.basename(self.filepath)}")
        return {'FINISHED'}


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


def get_user_library_path():
    """Get the default user library path for cabinet groups."""
    return os.path.join(os.path.expanduser("~"), "Documents", "Home Builder Library", "Cabinet Groups")


def get_user_library_items():
    """Get list of cabinet group files in the user library."""
    
    library_path = get_user_library_path()
    items = []
    
    if not os.path.exists(library_path):
        return items
    
    for filename in os.listdir(library_path):
        if filename.endswith('.blend'):
            name = filename[:-6]  # Remove .blend extension
            filepath = os.path.join(library_path, filename)
            
            # Check for thumbnail
            thumbnail_path = os.path.join(library_path, f"{name}.png")
            has_thumbnail = os.path.exists(thumbnail_path)
            
            items.append({
                'name': name,
                'filepath': filepath,
                'thumbnail': thumbnail_path if has_thumbnail else None
            })
    
    return items




# =============================================================================
# CABINET STYLE OPERATORS
# =============================================================================


classes = (
    hb_frameless_OT_save_cabinet_group_to_user_library,
    hb_frameless_OT_load_cabinet_group_from_library,
    hb_frameless_OT_refresh_user_library,
    hb_frameless_OT_open_user_library_folder,
    hb_frameless_OT_delete_library_item,
)

register, unregister = bpy.utils.register_classes_factory(classes)
