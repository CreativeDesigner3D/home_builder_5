"""Face frame user library - save, load, and manage cabinet groups.

A "cabinet group" is a generic GeoNodeCage with the IS_CAGE_GROUP marker
that wraps one or more cabinets so they can be saved as a single library
item and re-placed in future projects. The marker is shared with the
frameless library, so groups created in either style appear in both UIs
and load identically. This module's create-flow lives in
ops_cabinet.create_cabinet_group; here we cover save, load (modal
placement), refresh, open-folder, and delete.

Save format: bpy.data.libraries.write of the group cage plus all
descendants and their data blocks (meshes, materials, image textures,
geometry node groups). An optional 256x256 workbench thumbnail is
rendered next to the .blend.
"""
import bpy
import math
import os
import platform
import subprocess
from mathutils import Vector
from .. import props_hb_face_frame
from .... import hb_types, hb_placement, hb_snap


# ---------------------------------------------------------------------------
# Library path resolution (shared with frameless)
# ---------------------------------------------------------------------------
def get_user_library_path():
    """Path to the shared cabinet-groups folder under the extension user dir."""
    return bpy.utils.extension_path_user(
        '.'.join(__package__.split('.')[:3]),
        path="cabinet_groups",
        create=True,
    )


def get_all_cabinet_group_paths():
    """All cabinet-group library paths: the user default plus any registered
    asset library subfolders named cabinet_groups/.
    """
    from .... import hb_assets
    all_paths = hb_assets.get_all_subfolder_paths("cabinet_groups")
    default_path = get_user_library_path()
    if os.path.isdir(default_path) and default_path not in all_paths:
        all_paths.insert(0, default_path)
    return all_paths


def get_cabinet_group_categories():
    """Categories across all library paths. Loose .blend files in any root
    fall under 'General'.
    """
    categories_set = set()
    has_loose_files = False
    for groups_path in get_all_cabinet_group_paths():
        if not os.path.exists(groups_path):
            continue
        for item in os.listdir(groups_path):
            item_path = os.path.join(groups_path, item)
            if os.path.isdir(item_path):
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
    return get_cabinet_group_categories()


def get_user_library_items(category=None):
    """List of {name, filepath, thumbnail} for .blend files matching category.

    'ALL' / None scans every library root and every category subfolder.
    'General' scans only loose .blend files in roots. Specific category
    names scan only that subfolder. Names are de-duped across roots so
    the first wins (default user path is inserted first).
    """
    items = []
    seen_names = set()

    def _scan_dir(search_path):
        if not os.path.exists(search_path):
            return
        for filename in sorted(os.listdir(search_path)):
            if not filename.endswith('.blend'):
                continue
            name = filename[:-6]
            if name in seen_names:
                continue
            seen_names.add(name)
            filepath = os.path.join(search_path, filename)
            thumbnail_path = os.path.join(search_path, f"{name}.png")
            items.append({
                'name': name,
                'filepath': filepath,
                'thumbnail': thumbnail_path if os.path.exists(thumbnail_path) else None,
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
            _scan_dir(library_path)
            for item in sorted(os.listdir(library_path)):
                item_path = os.path.join(library_path, item)
                if os.path.isdir(item_path):
                    _scan_dir(item_path)

    return items


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
class hb_face_frame_OT_save_cabinet_group_to_user_library(bpy.types.Operator):
    """Save Cabinet Group to User Library"""
    bl_idname = "hb_face_frame.save_cabinet_group_to_user_library"
    bl_label = 'Save Cabinet Group to User Library'
    bl_description = "Save the selected cabinet group to the user library"
    bl_options = {'UNDO'}

    cabinet_group_name: bpy.props.StringProperty(name="Cabinet Group Name", default="")  # type: ignore
    save_path: bpy.props.StringProperty(name="Save Location", subtype='DIR_PATH', default="")  # type: ignore
    save_category: bpy.props.StringProperty(
        name="Category",
        description="Category subfolder to save into (leave empty for root)",
        default="",
    )  # type: ignore
    create_thumbnail: bpy.props.BoolProperty(
        name="Create Thumbnail",
        description="Generate a thumbnail image for the library",
        default=True,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        return bool(obj and 'IS_CAGE_GROUP' in obj)

    def invoke(self, context, event):
        self.cabinet_group_name = context.object.name
        self.save_path = get_user_library_path()
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

        actual_save_path = self.save_path
        if self.save_category.strip():
            actual_save_path = os.path.join(self.save_path, self.save_category.strip())
        os.makedirs(actual_save_path, exist_ok=True)

        safe_name = "".join(
            c for c in self.cabinet_group_name
            if c.isalnum() or c in (' ', '-', '_')
        ).strip()
        blend_filename = f"{safe_name}.blend"
        blend_filepath = os.path.join(actual_save_path, blend_filename)

        if os.path.exists(blend_filepath):
            self.report({'WARNING'}, f"File already exists: {blend_filename}. Overwriting.")

        objects_to_save = self._collect_objects_recursive(cabinet_group)
        data_blocks = self._collect_data_blocks(objects_to_save)

        bpy.data.libraries.write(
            blend_filepath,
            data_blocks,
            path_remap='RELATIVE_ALL',
            fake_user=True,
        )

        if self.create_thumbnail:
            self._create_thumbnail(context, cabinet_group, actual_save_path, safe_name)

        self.report({'INFO'}, f"Saved cabinet group to: {blend_filepath}")
        return {'FINISHED'}

    def _collect_objects_recursive(self, obj):
        objects = {obj}
        for child in obj.children:
            objects.update(self._collect_objects_recursive(child))
        return objects

    def _collect_data_blocks(self, objects):
        """Mesh / material / image / node-group dependencies for the given
        objects. Without these the saved .blend would re-load with broken
        materials and zeroed-out geometry node modifiers.
        """
        data_blocks = set()
        for obj in objects:
            data_blocks.add(obj)
            if obj.data:
                data_blocks.add(obj.data)
            if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'materials'):
                for mat in obj.data.materials:
                    if mat:
                        data_blocks.add(mat)
                        if mat.use_nodes and mat.node_tree:
                            for node in mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE' and node.image:
                                    data_blocks.add(node.image)
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    data_blocks.add(mod.node_group)
        return data_blocks

    def _create_thumbnail(self, context, cabinet_group, save_path, name):
        """Render an isometric workbench preview for the library list.

        Group cage is a generic GeoNodeCage, so its Dim X/Y/Z inputs can
        be read through the base wrapper - no style-specific class needed.
        Render state is snapshotted and restored even on failure so we
        don't leak engine / camera / resolution changes back into the
        user's scene.
        """
        original_camera = context.scene.camera
        original_render_x = context.scene.render.resolution_x
        original_render_y = context.scene.render.resolution_y
        original_render_percentage = context.scene.render.resolution_percentage
        original_engine = context.scene.render.engine
        original_filepath = context.scene.render.filepath

        try:
            cage = hb_types.GeoNodeCage(cabinet_group)
            width = cage.get_input('Dim X')
            depth = cage.get_input('Dim Y')
            height = cage.get_input('Dim Z')

            cam_data = bpy.data.cameras.new("ThumbnailCam")
            cam_data.type = 'ORTHO'
            cam_obj = bpy.data.objects.new("ThumbnailCam", cam_data)
            context.scene.collection.objects.link(cam_obj)

            # Cabinets occupy local X = [0, w], Y = [-d, 0] (Mirror Y),
            # Z = [0, h]; aim camera at that center in world space.
            center = cabinet_group.matrix_world @ Vector((width / 2, -depth / 2, height / 2))
            max_dim = max(width, depth, height)
            cam_data.ortho_scale = max_dim * 1.5
            cam_obj.location = center + Vector((max_dim, -max_dim, max_dim * 0.8))

            direction = center - cam_obj.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.rotation_euler = rot_quat.to_euler()

            context.scene.camera = cam_obj
            context.scene.render.resolution_x = 256
            context.scene.render.resolution_y = 256
            context.scene.render.resolution_percentage = 100
            context.scene.render.engine = 'BLENDER_WORKBENCH'
            context.scene.render.film_transparent = True
            context.scene.render.use_freestyle = True
            context.scene.render.line_thickness = .5

            thumbnail_path = os.path.join(save_path, f"{name}.png")
            context.scene.render.filepath = thumbnail_path
            bpy.ops.render.render(write_still=True)

            bpy.data.objects.remove(cam_obj)
            bpy.data.cameras.remove(cam_data)

        except Exception as e:
            print(f"Failed to create thumbnail: {e}")

        finally:
            context.scene.camera = original_camera
            context.scene.render.resolution_x = original_render_x
            context.scene.render.resolution_y = original_render_y
            context.scene.render.resolution_percentage = original_render_percentage
            context.scene.render.engine = original_engine
            context.scene.render.filepath = original_filepath


# ---------------------------------------------------------------------------
# Load (modal placement)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_load_cabinet_group_from_library(bpy.types.Operator, hb_placement.PlacementMixin):
    """Load Cabinet Group from User Library"""
    bl_idname = "hb_face_frame.load_cabinet_group_from_library"
    bl_label = 'Load Cabinet Group from Library'
    bl_description = "Load a cabinet group from the user library. Click to place, Right-click or ESC to cancel"
    bl_options = {'UNDO'}

    filepath: bpy.props.StringProperty(name="File Path", subtype='FILE_PATH')  # type: ignore

    root_objects: list = []
    orphan_offsets: dict = {}  # {obj: Vector offset from first root}
    geo_node_refs: set = set()  # Objects referenced by geometry node Object inputs

    @classmethod
    def poll(cls, context):
        return True

    def load_objects(self, context):
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
            data_to.meshes = data_from.meshes
            data_to.materials = data_from.materials
            data_to.node_groups = data_from.node_groups

        loaded_objects = []
        for obj in data_to.objects:
            if obj is not None:
                context.scene.collection.objects.link(obj)
                loaded_objects.append(obj)

        self.root_objects = []
        for obj in loaded_objects:
            if obj.get('IS_CAGE_GROUP') and obj.parent is None:
                self.root_objects.append(obj)
                self.register_placement_object(obj)
            elif obj.parent is None:
                # Orphan parentless objects (pulls etc.) tracked for cancel cleanup.
                self.register_placement_object(obj)

        # Hide objects referenced by geometry node Object inputs - they have to
        # exist for modifiers to resolve, but shouldn't render in the scene.
        geo_node_refs = set()
        for obj in loaded_objects:
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    for item in mod.node_group.interface.items_tree:
                        if (item.item_type == 'SOCKET'
                                and item.in_out == 'INPUT'
                                and item.socket_type == 'NodeSocketObject'):
                            try:
                                ref_obj = mod[item.identifier]
                                if ref_obj:
                                    geo_node_refs.add(ref_obj)
                            except (KeyError, TypeError):
                                pass

        self.geo_node_refs = geo_node_refs
        for ref_obj in geo_node_refs:
            ref_obj.hide_set(True)
            ref_obj.hide_viewport = True
            ref_obj.hide_render = True

        # Track offsets of remaining orphan parentless objects relative to the
        # first root, so they follow placement together. Geo-node refs are
        # excluded - they stay where they were loaded and stay hidden.
        self.orphan_offsets = {}
        if self.root_objects:
            root_loc = self.root_objects[0].location.copy()
            for obj in self.placement_objects:
                if (obj not in self.root_objects
                        and obj.parent is None
                        and obj not in geo_node_refs):
                    self.orphan_offsets[obj] = obj.location - root_loc

    def _set_hide_recursive(self, hide):
        """Toggle visibility of root + descendants for raycast suppression
        during modal placement. Geo-node refs stay permanently hidden so
        they're never re-shown by the unhide pass.
        """
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
        text = "Click to place cabinet group | R: rotate 90 | Right-click/Esc: cancel"
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

        # Hide loaded objects during raycast so the cursor ray doesn't hit
        # the very thing it's meant to be placing.
        self._set_hide_recursive(True)
        self.update_snap(context, event)
        self._set_hide_recursive(False)

        if self.hit_location:
            snapped = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            for obj in self.root_objects:
                obj.location = snapped
            for obj, offset in self.orphan_offsets.items():
                obj.location = snapped + offset

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            self.report({'INFO'}, f"Placed cabinet group from: {os.path.basename(self.filepath)}")
            return {'FINISHED'}

        if event.type == 'R' and event.value == 'PRESS':
            for obj in self.root_objects:
                obj.rotation_euler.z += math.radians(90)
            return {'RUNNING_MODAL'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


# ---------------------------------------------------------------------------
# Refresh, open folder, delete
# ---------------------------------------------------------------------------
class hb_face_frame_OT_refresh_user_library(bpy.types.Operator):
    """Refresh User Library"""
    bl_idname = "hb_face_frame.refresh_user_library"
    bl_label = 'Refresh User Library'
    bl_description = "Refresh the list of items in the user library"

    def execute(self, context):
        # Drop cached preview icons so deleted / replaced thumbnails reload
        # from disk on the next UI tick.
        props_hb_face_frame.clear_library_previews()
        for area in context.screen.areas:
            area.tag_redraw()
        self.report({'INFO'}, "User library refreshed")
        return {'FINISHED'}


class hb_face_frame_OT_open_user_library_folder(bpy.types.Operator):
    """Open User Library Folder"""
    bl_idname = "hb_face_frame.open_user_library_folder"
    bl_label = 'Open User Library Folder'
    bl_description = "Open the user library folder in file explorer"

    def execute(self, context):
        library_path = get_user_library_path()
        if not os.path.exists(library_path):
            os.makedirs(library_path, exist_ok=True)
        if platform.system() == 'Windows':
            os.startfile(library_path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', library_path])
        else:
            subprocess.Popen(['xdg-open', library_path])
        return {'FINISHED'}


class hb_face_frame_OT_delete_library_item(bpy.types.Operator):
    """Delete Item from User Library"""
    bl_idname = "hb_face_frame.delete_library_item"
    bl_label = 'Delete Library Item'
    bl_description = "Delete a cabinet group from the user library"

    filepath: bpy.props.StringProperty(name="File Path", subtype='FILE_PATH')  # type: ignore
    item_name: bpy.props.StringProperty(name="Item Name")  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        os.remove(self.filepath)
        # Remove the matching thumbnail too - leaving it would point at a
        # deleted .blend and clutter the library folder.
        thumbnail_path = self.filepath.replace('.blend', '.png')
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        props_hb_face_frame.clear_library_previews()
        self.report({'INFO'}, f"Deleted: {self.item_name}")
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_save_cabinet_group_to_user_library,
    hb_face_frame_OT_load_cabinet_group_from_library,
    hb_face_frame_OT_refresh_user_library,
    hb_face_frame_OT_open_user_library_folder,
    hb_face_frame_OT_delete_library_item,
)

register, unregister = bpy.utils.register_classes_factory(classes)
