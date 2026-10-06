"""Closet user library - save a closet to your own library and drop it
back into a later project (the prior library's Save Closet / user
Closet Library).

A saved closet is its starter root and everything under it, written with
bpy.data.libraries.write the way face_frame saves a cabinet group (same
data-block gathering and thumbnail), so every bay, opening and finish
comes along - closets keep their state in their prop groups and part
idprops, not in drivers. Files live in the extension user folder under
closet_groups/ (a subfolder per category), plus any registered asset
library's closet_groups/ folder.

Loading appends the closet hidden and hands it to the closet placement
(hb_closets.place_starter in duplicate mode), so a library closet snaps
to walls, fills a gap and asks for corner clearance like any other; the
appended source is removed when the placement ends either way.
"""
import os
import platform
import subprocess

import bpy

from .. import types_closets
from ...face_frame.operators import ops_library as ff_library

LIBRARY_FOLDER = "closet_groups"
PREVIEW_PREFIX = "userlib_"


def get_user_library_path():
    """The default closet library folder under the extension user dir."""
    return bpy.utils.extension_path_user(
        '.'.join(__package__.split('.')[:3]),
        path=LIBRARY_FOLDER,
        create=True,
    )


def get_all_library_paths():
    """The default folder plus any registered asset library's
    closet_groups/ subfolder."""
    from .... import hb_assets
    paths = hb_assets.get_all_subfolder_paths(LIBRARY_FOLDER)
    default = get_user_library_path()
    if os.path.isdir(default) and default not in paths:
        paths.insert(0, default)
    return paths


def get_library_items():
    """[{name, category, filepath, thumbnail}] for every saved closet,
    loose files first, then each category folder; a name already seen
    in an earlier folder is skipped."""
    items = []
    seen = set()

    def _scan(folder, category):
        if not os.path.isdir(folder):
            return
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith('.blend'):
                continue
            name = filename[:-6]
            key = (category, name)
            if key in seen:
                continue
            seen.add(key)
            thumb = os.path.join(folder, name + '.png')
            items.append({
                'name': name,
                'category': category,
                'filepath': os.path.join(folder, filename),
                'thumbnail': thumb if os.path.exists(thumb) else None,
            })

    for root in get_all_library_paths():
        _scan(root, '')
        if os.path.isdir(root):
            for entry in sorted(os.listdir(root)):
                if os.path.isdir(os.path.join(root, entry)):
                    _scan(os.path.join(root, entry), entry)
    return items


def thumbnail_icon(path):
    """Icon id for a saved closet's thumbnail (0 when it has none)."""
    if not path:
        return 0
    from .. import props_closets
    pcoll = props_closets.get_starter_previews()
    key = PREVIEW_PREFIX + path
    if key in pcoll:
        return pcoll[key].icon_id
    try:
        return pcoll.load(key, path, 'IMAGE').icon_id
    except Exception:
        return 0


def clear_previews():
    """Drop the library thumbnails so changed files reload."""
    from .. import props_closets
    pcoll = props_closets.get_starter_previews()
    for key in [k for k in pcoll.keys() if k.startswith(PREVIEW_PREFIX)]:
        del pcoll[key]


def _safe_name(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')
                   ).strip()


class hb_closets_OT_save_closet_to_library(bpy.types.Operator):
    """Save the selected closet to your closet library"""
    bl_idname = "hb_closets.save_closet_to_library"
    bl_label = "Save Closet to Library"
    bl_options = {'UNDO'}

    closet_name: bpy.props.StringProperty(
        name="Name", default="")  # type: ignore
    category: bpy.props.StringProperty(
        name="Category",
        description="Folder in the library to save into (empty for none)",
        default="")  # type: ignore
    create_thumbnail: bpy.props.BoolProperty(
        name="Create Thumbnail", default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and types_closets.find_starter_root(obj) is not None)

    def invoke(self, context, event):
        root = types_closets.find_starter_root(context.active_object)
        self.closet_name = root.name
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'closet_name')
        layout.prop(self, 'category')
        layout.prop(self, 'create_thumbnail')

    def execute(self, context):
        root = types_closets.find_starter_root(context.active_object)
        if root is None:
            return {'CANCELLED'}
        name = _safe_name(self.closet_name)
        if not name:
            self.report({'ERROR'}, "Enter a name for the closet")
            return {'CANCELLED'}
        folder = get_user_library_path()
        if self.category.strip():
            folder = os.path.join(folder, _safe_name(self.category))
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, name + '.blend')

        # Saved free of the room: off its wall, at the origin, square to
        # the world (4.3 unparented the closet from its wall to save it).
        parent = root.parent
        matrix = root.matrix_world.copy()
        parent_inverse = root.matrix_parent_inverse.copy()
        loc = root.location.copy()
        rot = root.rotation_euler.copy()
        try:
            root.parent = None
            root.location = (0.0, 0.0, 0.0)
            root.rotation_euler = (0.0, 0.0, 0.0)
            context.view_layer.update()
            saver = ff_library.hb_face_frame_OT_save_cabinet_group_to_user_library
            objects = {root} | set(root.children_recursive)
            blocks = saver._collect_data_blocks(None, objects)
            bpy.data.libraries.write(filepath, blocks,
                                     path_remap='RELATIVE_ALL',
                                     fake_user=True)
            if self.create_thumbnail:
                saver._create_thumbnail(None, context, root, folder, name)
        finally:
            root.parent = parent
            root.matrix_parent_inverse = parent_inverse
            root.location = loc
            root.rotation_euler = rot
            if parent is None:
                root.matrix_world = matrix
        clear_previews()
        self.report({'INFO'}, f"Saved {name} to the closet library")
        return {'FINISHED'}


class hb_closets_OT_load_closet_from_library(bpy.types.Operator):
    """Place a closet from your closet library"""
    bl_idname = "hb_closets.load_closet_from_library"
    bl_label = "Place Library Closet"
    bl_options = {'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File", subtype='FILE_PATH')  # type: ignore

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        with bpy.data.libraries.load(self.filepath, link=False) as (src, dst):
            dst.objects = list(src.objects)
        loaded = [o for o in dst.objects if o is not None]
        root = next((o for o in loaded
                     if o.get(types_closets.TAG_STARTER_CAGE)
                     and o.parent is None), None)
        if root is None:
            for o in loaded:
                bpy.data.objects.remove(o, do_unlink=True)
            self.report({'WARNING'}, "No closet found in that file")
            return {'CANCELLED'}
        for o in loaded:
            context.scene.collection.objects.link(o)
            o.hide_set(True)
        # The placement copies this source where it is dropped and then
        # removes it (discard_source), on a drop or a cancel alike.
        try:
            result = bpy.ops.hb_closets.place_starter(
                'INVOKE_DEFAULT', source_starter_name=root.name,
                discard_source=True)
        except RuntimeError as e:
            result = set()
            self.report({'WARNING'}, f"Could not start placement: {e}")
        if 'RUNNING_MODAL' not in result and 'FINISHED' not in result:
            # The placement never took the source over, so it is ours
            # to remove.
            if root.name in bpy.data.objects:
                types_closets._remove_part_tree(root)
            return {'CANCELLED'}
        return {'FINISHED'}


class hb_closets_OT_refresh_closet_library(bpy.types.Operator):
    """Re-read the closet library"""
    bl_idname = "hb_closets.refresh_closet_library"
    bl_label = "Refresh Closet Library"

    def execute(self, context):
        clear_previews()
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class hb_closets_OT_open_closet_library_folder(bpy.types.Operator):
    """Open the closet library folder"""
    bl_idname = "hb_closets.open_closet_library_folder"
    bl_label = "Open Closet Library Folder"

    def execute(self, context):
        path = get_user_library_path()
        os.makedirs(path, exist_ok=True)
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
        return {'FINISHED'}


class hb_closets_OT_delete_library_closet(bpy.types.Operator):
    """Delete a closet from your closet library"""
    bl_idname = "hb_closets.delete_library_closet"
    bl_label = "Delete Library Closet"

    filepath: bpy.props.StringProperty(
        name="File", subtype='FILE_PATH')  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            return {'CANCELLED'}
        os.remove(self.filepath)
        thumb = self.filepath[:-6] + '.png'
        if os.path.exists(thumb):
            os.remove(thumb)
        clear_previews()
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


def draw_library_section(layout, context):
    """'My Closets': every saved closet, click to place."""
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator('hb_closets.open_closet_library_folder', text="Open Folder",
                 icon='FILE_FOLDER')
    row.operator('hb_closets.refresh_closet_library', text="", icon='FILE_REFRESH')
    items = get_library_items()
    if not items:
        col.label(text="Right-click a closet > Save Closet to Library",
                  icon='INFO')
        return
    category = None
    for item in items:
        if item['category'] != category:
            category = item['category']
            if category:
                col.label(text=category)
        row = col.row(align=True)
        icon = thumbnail_icon(item['thumbnail'])
        if icon:
            op = row.operator('hb_closets.load_closet_from_library',
                              text=item['name'], icon_value=icon)
        else:
            op = row.operator('hb_closets.load_closet_from_library',
                              text=item['name'], icon='MESH_CUBE')
        op.filepath = item['filepath']
        op = row.operator('hb_closets.delete_library_closet', text="",
                          icon='X')
        op.filepath = item['filepath']


classes = (
    hb_closets_OT_save_closet_to_library,
    hb_closets_OT_load_closet_from_library,
    hb_closets_OT_refresh_closet_library,
    hb_closets_OT_open_closet_library_folder,
    hb_closets_OT_delete_library_closet,
)

register, unregister = bpy.utils.register_classes_factory(classes)
