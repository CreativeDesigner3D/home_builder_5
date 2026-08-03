"""Cabinet pull asset discovery + loading for the face frame library.

Pulls live as .blend files under <root>/<category>/, each with a
matching .png thumbnail. Two roots are searched: the addon's shipped
face_frame_assets/cabinet_pulls folder, and a per-user folder that
installed pull libraries land in (see get_user_pulls_root and
operators/ops_pull_library). The user root is searched first so a
user-installed pull can override a shipped one of the same name, and
it lives outside the addon folder so installed packs survive addon
updates. Loading a pull returns the first mesh object found in the
.blend; downstream code links the same object into pull instances so
swapping the source updates every cabinet at once.
"""

import os
import bpy

from . import props_hb_face_frame  # for the existing thumbnail preview collection


# Pull finish materials come from the shared accessory-finishes
# library (the same materials the closets library swaps onto its
# handles). AS_MODELED is first so it's the dynamic-enum default:
# leave the pull's own materials alone, which is the pre-finish
# behavior.
FINISHES_BLEND = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'closets', 'assets',
    'materials', 'accessory_finishes.blend')

PULL_FINISHES = [
    ('AS_MODELED', "As Modeled", "Keep the pull asset's own materials"),
    ('Black', "Black", ""),
    ('Matte Aluminum', "Matte Aluminum", ""),
    ('Matte Gold', "Matte Gold", ""),
    ('Matte Nickel', "Matte Nickel", ""),
    ('Polished Chrome', "Polished Chrome", ""),
    ('Slate', "Slate", ""),
]


def load_finish_material(name):
    """Existing-or-appended finish material by name; None if missing."""
    if not name:
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    try:
        with bpy.data.libraries.load(FINISHES_BLEND) as (src, dst):
            if name in src.materials:
                dst.materials = [name]
    except Exception:
        return None
    return bpy.data.materials.get(name)


def apply_finish_to_pull(pull_obj, finish):
    """Swap the shared pull mesh's material to the selected finish.
    Pull instances link this mesh data, so every placed pull follows.
    AS_MODELED leaves the asset's own materials untouched.
    """
    if not finish or finish == 'AS_MODELED':
        return
    if pull_obj is None or pull_obj.data is None:
        return
    mat = load_finish_material(finish)
    if mat is None:
        return
    mats = pull_obj.data.materials
    if len(mats) == 1 and mats[0] is mat:
        return
    mats.clear()
    mats.append(mat)


def get_pulls_root():
    """Absolute path to the shipped cabinet_pulls assets folder."""
    return os.path.join(
        os.path.dirname(__file__), 'face_frame_assets', 'cabinet_pulls'
    )


def get_user_pulls_root(create=False):
    """Absolute path to the per-user pulls folder (installed pull
    libraries). Prefers Blender's per-extension user directory, which
    survives addon updates; falls back to the user datafiles resource
    when the addon isn't running as an extension.
    """
    addon_pkg = __package__.split('.product_libraries')[0]
    try:
        return bpy.utils.extension_path_user(
            addon_pkg, path='cabinet_pulls', create=create)
    except Exception:
        base = bpy.utils.user_resource(
            'DATAFILES', path='home_builder_5', create=create)
        path = os.path.join(base, 'cabinet_pulls')
        if create:
            os.makedirs(path, exist_ok=True)
        return path


def get_pulls_roots():
    """Existing pull roots in search order: user first (so an installed
    pull overrides a shipped one of the same name), then shipped.
    """
    return [r for r in (get_user_pulls_root(), get_pulls_root())
            if os.path.isdir(r)]


def get_pull_categories():
    """Return [(id, label, desc), ...] of category subfolders across
    every pull root. The id is the folder name, uppercased; label is
    the folder name as-is. Same-named categories in both roots merge
    into one entry. Real categories come first so the EnumProperty
    defaults to the first real one (turning pulls on by default);
    'NONE' is appended at the end so the user can still opt out.
    """
    by_id = {}
    for root in get_pulls_roots():
        for entry in sorted(os.listdir(root)):
            full = os.path.join(root, entry)
            if os.path.isdir(full):
                by_id.setdefault(entry.upper(), entry)
    items = [(cat_id, label, f"Pulls in {label}")
             for cat_id, label in sorted(by_id.items())]
    items.append(('NONE', "None", "No pull"))
    return items


def get_pulls_in_category(category):
    """Return [(id, label, desc), ...] for every .blend in `category`
    (the original folder name, not the lowercased id) across every
    pull root. Each id is the filename WITH .blend so the loader can
    find the file directly; a same-named file in the user root shadows
    the shipped one (roots are in search order).
    """
    items = []
    if not category or category == 'NONE':
        return items
    seen = set()
    for root in get_pulls_roots():
        folder = os.path.join(root, category)
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            if not name.lower().endswith('.blend'):
                continue
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            stem = os.path.splitext(name)[0]
            items.append((name, stem, f"{stem} ({category})"))
    items.sort(key=lambda it: it[1].lower())
    return items


def find_pull_file(filename, category=None):
    """Resolve `filename` (something like 'Round Knob.blend' or
    'Round Knob.png') to an absolute path, searching every pull root
    in order. If `category` is provided we only look in that subfolder;
    otherwise we walk every category. Returns None if not found.
    """
    for root in get_pulls_roots():
        if category and category != 'NONE':
            candidate = os.path.join(root, category, filename)
            if os.path.exists(candidate):
                return candidate
            continue
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
        apply_finish_to_pull(cached, scene_props.pull_finish)
        return cached

    real_cat = _resolve_real_category(scene_props.door_pull_category)
    pull_obj = load_pull_object(selection, real_cat)
    if pull_obj is None:
        return None
    apply_finish_to_pull(pull_obj, scene_props.pull_finish)

    if kind == 'door':
        scene_props.current_door_pull_object = pull_obj
    else:
        scene_props.current_drawer_pull_object = pull_obj
    return pull_obj


# Loaded source objects for assignment- and override-resolved pulls,
# keyed by (category, filename). Several can be live at once (each
# zone / overridden opening may use a different pull); instances share
# each source's mesh data. Dead references (file reload / purge) are
# detected and reloaded on demand.
_override_cache = {}

# Door zones by cabinet type. Anything unlisted (LAP_DRAWER, panels)
# reads the Base assignment.
_ZONE_BY_CABINET_TYPE = {'BASE': 'base', 'TALL': 'tall', 'UPPER': 'upper'}


def resolve_pull_for(scene_props, kind, cabinet_type):
    """Zone-assignment pull resolution: drawer-kind fronts (drawers,
    pullouts, tilt-outs) read the Drawers assignment; doors read the
    assignment for their cabinet type (Base / Tall / Upper). A zone
    assigned NONE drops the pull; an UNASSIGNED zone falls back to the
    legacy scene-wide selection, so scenes saved before zone
    assignment (and fresh scenes before the first Assign) keep their
    pulls.
    """
    zone = ('drawers' if kind == 'drawer'
            else _ZONE_BY_CABINET_TYPE.get(cabinet_type, 'base'))
    selection = getattr(scene_props, 'pull_assign_' + zone, '')
    if selection == 'NONE':
        return None
    if selection:
        category = getattr(
            scene_props, 'pull_assign_' + zone + '_category', '')
        pull_obj = resolve_pull_override(category, selection, scene_props)
        if pull_obj is not None:
            return pull_obj
    return resolve_pull_object(scene_props, kind)


def resolve_pull_override(category, filename, scene_props):
    """Loaded pull object for a per-opening override, with the scene
    finish applied. Falls back to an any-category search when the
    stored category no longer exists (e.g. a pack was removed and
    reinstalled under a different folder). Returns None when the file
    can't be found - callers then use the scene-wide selection.
    """
    if not filename or filename == 'NONE':
        return None
    key = (category or '', filename)
    cached = _override_cache.get(key)
    if cached is not None:
        try:
            cached.name  # dead-reference check
            apply_finish_to_pull(cached, scene_props.pull_finish)
            return cached
        except ReferenceError:
            pass
    pull_obj = load_pull_object(filename, category or None)
    if pull_obj is None and category:
        pull_obj = load_pull_object(filename, None)
    if pull_obj is None:
        return None
    _override_cache[key] = pull_obj
    apply_finish_to_pull(pull_obj, scene_props.pull_finish)
    return pull_obj


def pull_length(pull_obj):
    """Length of `pull_obj` along its asset-local X axis - the bar's
    long dimension for bar pulls, the diameter for round knobs. Returns
    0.0 for None / non-mesh / empty meshes so callers can use the
    result unconditionally as a placement offset.

    Asset convention: pull origin is at the geometric center of the
    mounting face, with the bar axis running along asset X. Reading
    raw vertex coords (rather than obj.dimensions) avoids any object-
    level scale skewing the result.
    """
    if pull_obj is None or pull_obj.data is None:
        return 0.0
    verts = getattr(pull_obj.data, 'vertices', None)
    if not verts:
        return 0.0
    xs = [v.co.x for v in verts]
    return max(xs) - min(xs)
