"""Install and manage user pull libraries for the face frame library.

A pull pack is a zip carrying <Category>/<Pull>.blend files with
matching .png thumbnails - either at the zip root, under a
cabinet_pulls/ folder, or wrapped one level deeper (the layout a
repository download zip produces). Install extracts the categories
into the per-user pulls folder (pulls.get_user_pulls_root()), which
merges with the shipped assets in every pull dropdown and survives
addon updates.
"""
import os
import shutil
import zipfile

import bpy
from bpy.props import StringProperty

from .. import pulls

# Files worth extracting from a pack: the pulls themselves plus their
# thumbnails. Everything else (README, LICENSE, .git internals) stays
# in the zip.
_INSTALL_EXTS = ('.blend', '.png')


def _zip_pull_entries(zf):
    """Return [(category, filename, member), ...] of installable files
    in the zip. Handles three layouts:

    - paths containing a cabinet_pulls/ segment (optionally under a
      wrapper folder, e.g. a repository download zip),
    - category folders holding the files (at the root or one wrapper
      level down),
    - loose files at the zip root, installed under a 'Custom' category.

    Only categories that actually contain a .blend survive - keeps a
    pack's stray images from creating empty categories.
    """
    parsed = []
    for member in zf.namelist():
        if member.endswith('/'):
            continue
        parts = [p for p in member.replace('\\', '/').split('/')
                 if p not in ('', '.')]
        if not parts or any(p == '..' for p in parts):
            continue
        parsed.append((parts, member))

    entries = []
    for parts, member in parsed:
        if 'cabinet_pulls' in parts[:-1]:
            rel = parts[parts.index('cabinet_pulls') + 1:]
            if len(rel) == 2:
                entries.append((rel[0], rel[1], member))
            elif len(rel) == 1:
                entries.append(('Custom', rel[0], member))
    if not entries:
        for parts, member in parsed:
            if len(parts) >= 2:
                entries.append((parts[-2], parts[-1], member))
            else:
                entries.append(('Custom', parts[-1], member))

    entries = [(cat, fn, member) for cat, fn, member in entries
               if os.path.splitext(fn)[1].lower() in _INSTALL_EXTS]
    cats_with_pulls = {cat for cat, fn, _m in entries
                       if fn.lower().endswith('.blend')}
    return [(cat, fn, member) for cat, fn, member in entries
            if cat in cats_with_pulls]


class hb_face_frame_OT_install_pull_library(bpy.types.Operator):
    """Install a downloaded pull library zip into the user pulls
    folder. The pack's categories merge into the pull dropdowns
    immediately; same-named files overwrite previously installed ones
    (updating a pack in place)."""
    bl_idname = "hb_face_frame.install_pull_library"
    bl_label = "Install Pull Library"
    bl_description = ("Install a pull library zip (categories of .blend "
                      "pulls with .png thumbnails) into the user pulls "
                      "folder")

    filepath: StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: StringProperty(
        default='*.zip', options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath or not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "Select a downloaded .zip file")
            return {'CANCELLED'}
        dest_root = os.path.abspath(pulls.get_user_pulls_root(create=True))
        installed = 0
        categories = set()
        try:
            with zipfile.ZipFile(self.filepath) as zf:
                for cat, fn, member in _zip_pull_entries(zf):
                    target_dir = os.path.join(dest_root, cat)
                    target = os.path.abspath(os.path.join(target_dir, fn))
                    # Zip-slip guard: the target must stay inside the
                    # user pulls folder.
                    if not target.startswith(dest_root + os.sep):
                        continue
                    os.makedirs(target_dir, exist_ok=True)
                    with zf.open(member) as src, open(target, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    if fn.lower().endswith('.blend'):
                        installed += 1
                        categories.add(cat)
        except zipfile.BadZipFile:
            self.report({'ERROR'}, "Not a valid zip file")
            return {'CANCELLED'}
        if installed == 0:
            self.report(
                {'WARNING'},
                "No pulls found - expected <Category> folders of .blend "
                "files (a cabinet_pulls folder inside the zip also works)")
            return {'CANCELLED'}
        cat_word = "category" if len(categories) == 1 else "categories"
        self.report(
            {'INFO'},
            f"Installed {installed} pull(s) in {len(categories)} "
            f"{cat_word}: {', '.join(sorted(categories))}")
        # The category / pull enums enumerate the disk on every draw,
        # so a redraw is all the refresh needed.
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}


class hb_face_frame_OT_assign_pull(bpy.types.Operator):
    """Assign the browsed pull (library dropdowns above the buttons)
    to a zone - Base / Tall / Upper doors, Drawers - or to the
    openings of the selected fronts. Zone assignments live on the
    scene; Selected writes per-opening overrides that win over the
    zone."""
    bl_idname = "hb_face_frame.assign_pull"
    bl_label = "Assign Pull"
    bl_description = ("Assign the browsed pull to a cabinet zone or "
                      "to the selected fronts")
    bl_options = {'UNDO'}

    target: bpy.props.EnumProperty(
        name="Assign To",
        items=[
            ('BASE', "Base", "Doors on base cabinets"),
            ('TALL', "Tall", "Doors on tall cabinets"),
            ('UPPER', "Upper", "Doors on upper cabinets"),
            ('DRAWERS', "Drawers",
             "Drawer, pullout, and tilt-out fronts"),
            ('SELECTED', "Selected",
             "The selected fronts only (stored per opening)"),
        ],
    )  # type: ignore

    def execute(self, context):
        from .. import types_face_frame
        scene_props = context.scene.hb_face_frame
        selection = scene_props.pull_browser_selection
        if not selection:
            self.report({'WARNING'}, "Pick a pull in the library first")
            return {'CANCELLED'}
        category = pulls._resolve_real_category(
            scene_props.door_pull_category) or ''
        stem = ("No Pull" if selection == 'NONE'
                else os.path.splitext(selection)[0])

        if self.target == 'SELECTED':
            from . import ops_cabinet
            from . import ops_part_commands
            openings = {}
            skipped = 0
            for obj in context.selected_objects:
                if (obj.get('hb_part_role')
                        not in ops_part_commands._ROLES_WITH_PULL):
                    continue
                opening = ops_cabinet._find_owning_opening(obj)
                if opening is None:
                    skipped += 1
                    continue
                openings[opening.name] = opening
            if not openings:
                self.report(
                    {'WARNING'},
                    "Select door or drawer fronts first"
                    + (" (corner doors follow the zone assignment)"
                       if skipped else ""))
                return {'CANCELLED'}
            with types_face_frame.suspend_recalc():
                for opening in openings.values():
                    op_props = opening.face_frame_opening
                    op_props.pull_override_category = (
                        '' if selection == 'NONE' else category)
                    op_props.pull_override = selection
            msg = f"{stem} assigned to {len(openings)} opening(s)"
            if skipped:
                msg += f"; {skipped} corner front(s) skipped"
            self.report({'INFO'}, msg)
            return {'FINISHED'}

        zone = self.target.lower()
        setattr(scene_props, 'pull_assign_' + zone, selection)
        setattr(scene_props, 'pull_assign_' + zone + '_category',
                '' if selection == 'NONE' else category)
        # Zone strings carry no update callback - rebuild the room here.
        with types_face_frame.suspend_recalc():
            for obj in context.scene.objects:
                if obj.get(types_face_frame.TAG_CABINET_CAGE):
                    types_face_frame.recalculate_face_frame_cabinet(obj)
        self.report({'INFO'},
                    f"{stem} assigned to {self.target.title()}")
        return {'FINISHED'}


class hb_face_frame_OT_open_pull_library_folder(bpy.types.Operator):
    """Open the user pulls folder in the system file browser (drop
    category folders of .blend pulls here to install by hand)."""
    bl_idname = "hb_face_frame.open_pull_library_folder"
    bl_label = "Open Pull Library Folder"
    bl_description = ("Open the user pulls folder in the file browser; "
                      "category folders of .blend pulls dropped here "
                      "appear in the pull dropdowns")

    def execute(self, context):
        root = pulls.get_user_pulls_root(create=True)
        bpy.ops.wm.path_open(filepath=root)
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_install_pull_library,
    hb_face_frame_OT_assign_pull,
    hb_face_frame_OT_open_pull_library_folder,
)


register, unregister = bpy.utils.register_classes_factory(classes)
