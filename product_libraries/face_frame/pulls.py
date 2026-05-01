"""Cabinet pull asset discovery + loading for the face frame library.

Pulls live as .blend files under face_frame_assets/cabinet_pulls/<category>/,
each with a matching .png thumbnail. Loading a pull returns the first
mesh object found in the .blend; downstream code links the same object
into pull instances so swapping the source updates every cabinet at once.
"""

import os
import bpy

from . import props_hb_face_frame  # for the existing thumbnail preview collection


def get_pulls_root():
    """Absolute path to the cabinet_pulls assets folder."""
    return os.path.join(
        os.path.dirname(__file__), 'face_frame_assets', 'cabinet_pulls'
    )


def get_pull_categories():
    """Return [(id, label, desc), ...] of subfolders inside the pulls root.
    The id is the folder name, uppercased; label is the folder name as-is.
    Real categories come first so the EnumProperty defaults to the first
    real one (turning pulls on by default); 'NONE' is appended at the end
    so the user can still opt out.
    """
    items = []
    root = get_pulls_root()
    if os.path.isdir(root):
        for entry in sorted(os.listdir(root)):
            full = os.path.join(root, entry)
            if os.path.isdir(full):
                items.append((entry.upper(), entry, f"Pulls in {entry}"))
    items.append(('NONE', "None", "No pull"))
    return items


def get_pulls_in_category(category):
    """Return [(id, label, desc), ...] for every .blend in `category`
    (the original folder name, not the lowercased id). Each id is the
    filename WITH .blend so the loader can find the file directly.
    """
    items = []
    if not category or category == 'NONE':
        return items
    folder = os.path.join(get_pulls_root(), category)
    if not os.path.isdir(folder):
        return items
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith('.blend'):
            stem = os.path.splitext(name)[0]
            items.append((name, stem, f"{stem} ({category})"))
    return items



def find_pull_file(filename, category=None):
    """Resolve `filename` (something like 'Round Knob.blend' or
    'Round Knob.png') to an absolute path. If `category` is provided
    we only look in that subfolder; otherwise we walk every category.
    Returns None if not found.
    """
    root = get_pulls_root()
    if not os.path.isdir(root):
        return None
    if category and category != 'NONE':
        candidate = os.path.join(root, category, filename)
        return candidate if os.path.exists(candidate) else None
    for entry in os.listdir(root):
        full = os.path.join(root, entry, filename)
        if os.path.exists(full):
            return full
    return None


def load_pull_object(filename, category=None):
    """Load the first mesh object out of `filename` (a .blend in the
    pulls assets folder) and return it. Returns None if the file is
    missing or contains no objects. The loaded object is linked into
    bpy.data.objects but NOT into any scene collection - callers handle
    placement.
    """
    path = find_pull_file(filename, category)
    if path is None:
        return None
    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    for obj in data_to.objects:
        if obj is not None:
            return obj
    return None


def load_pull_thumbnail_icon(filename, category=None):
    """Load the .png matching `filename` (a .blend) into the existing
    face_frame library preview collection. Returns the icon_id (0 if
    the thumbnail file isn't present). Cached by name so repeated
    lookups are cheap.
    """
    if not filename or filename == 'NONE':
        return 0
    stem = os.path.splitext(filename)[0]
    png_path = find_pull_file(stem + '.png', category)
    if png_path is None:
        return 0
    return props_hb_face_frame.load_library_thumbnail(png_path, f'pull_{stem}')



def _resolve_real_category(category_id):
    """Map an upper-case category id back to its on-disk folder name.
    Returns None for the 'NONE' sentinel or unknown ids.
    """
    if not category_id or category_id == 'NONE':
        return None
    for entry_id, label, _ in get_pull_categories():
        if entry_id == category_id:
            return label
    return None


def resolve_pull_object(scene_props, kind):
    """Return the loaded pull object for `kind` ('door' or 'drawer'),
    pulling from cache when the cached object matches the current
    selection and reloading from .blend otherwise. Returns None when the
    user selected NONE or the file can't be found.

    Cache match is by name stem - Blender's library load gives loaded
    objects the source name (with optional .NNN suffix on duplicate),
    so a stem-prefix match is tolerant to that suffix.
    """
    if kind == 'door':
        selection = scene_props.door_pull_selection
        cached = scene_props.current_door_pull_object
    elif kind == 'drawer':
        selection = scene_props.drawer_pull_selection
        cached = scene_props.current_drawer_pull_object
    else:
        return None

    if not selection or selection == 'NONE':
        return None

    sel_stem = os.path.splitext(selection)[0]
    if cached is not None and cached.name and (
        cached.name == sel_stem or cached.name.startswith(sel_stem + '.')
    ):
        return cached

    real_cat = _resolve_real_category(scene_props.door_pull_category)
    pull_obj = load_pull_object(selection, real_cat)
    if pull_obj is None:
        return None

    if kind == 'door':
        scene_props.current_door_pull_object = pull_obj
    else:
        scene_props.current_drawer_pull_object = pull_obj
    return pull_obj
