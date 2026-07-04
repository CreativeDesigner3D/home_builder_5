"""Closet pull (handle) selection.

Handles live as .blend files under assets/handles/ with matching .png
thumbnails; one scene-level selection covers every closet front (doors,
drawers, hampers), with a finish dropdown that swaps the material on
the shared pull mesh. Pull instances link the SAME mesh data, so both a
pull swap and a finish change propagate to every closet in the room
through one recalculate pass (update_room).

Same mechanism family as materials_closets: folder scan -> cached enum
items (with thumbnail icons) -> append-on-first-use. The finish
materials come from assets/materials/accessory_finishes.blend.
"""
import os
import bpy

# Shared asset convention (origin at mounting-face center, bar along X);
# the length helper is library-agnostic, so reuse it.
from ..face_frame.pulls import pull_length  # noqa: F401  (re-exported)


HANDLES_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'handles')
FINISHES_BLEND = os.path.join(os.path.dirname(__file__), 'assets',
                              'materials', 'accessory_finishes.blend')

PULL_FINISHES = [
    ('Black', "Black", ""),
    ('Matte Aluminum', "Matte Aluminum", ""),
    ('Matte Gold', "Matte Gold", ""),
    ('Matte Nickel', "Matte Nickel", ""),
    ('Polished Chrome', "Polished Chrome", ""),
    ('Slate', "Slate", ""),
]

ROD_FINISHES = [
    ('Black', "Black", ""),
    ('Matte Aluminum', "Matte Aluminum", ""),
    ('Matte Gold', "Matte Gold", ""),
    ('Matte Nickel', "Matte Nickel", ""),
    ('Polished Chrome', "Polished Chrome", ""),
    ('Slate Graphite', "Slate Graphite", ""),
]

ROD_TYPES = [
    ('OVAL', "Signature", "Oval profile"),
    ('ROUND', "Round", "Round profile"),
]

_enum_cache = None
# One loaded source object per selection; instances share its mesh data.
_pull_cache = {'selection': '', 'object': None}


DEFAULT_PULL = 'CLASSIC 96.blend'


def get_pull_files():
    """Sorted .blend filenames in the handles folder, with the standard
    handle hoisted to the front - a dynamic enum defaults to its first
    item, so this doubles as the dropdown default."""
    if not os.path.isdir(HANDLES_DIR):
        return []
    files = sorted(f for f in os.listdir(HANDLES_DIR)
                   if f.lower().endswith('.blend'))
    if DEFAULT_PULL in files:
        files.remove(DEFAULT_PULL)
        files.insert(0, DEFAULT_PULL)
    return files


def _thumb_icon(stem):
    """Icon id for a handle thumbnail, cached in the shared closets
    preview collection (props_closets owns its lifetime)."""
    from . import props_closets
    pcoll = props_closets.get_starter_previews()
    key = f'pull_{stem}'
    if key in pcoll:
        return pcoll[key].icon_id
    path = os.path.join(HANDLES_DIR, stem + '.png')
    if os.path.exists(path):
        return pcoll.load(key, path, 'IMAGE').icon_id
    return 0


def pull_enum_items(self, context):
    """Dropdown items: every handle (thumbnail icon inline), None last
    so pulls are on by default (mirrors the cabinet pulls convention).
    Cached module-level - dynamic-enum string-lifetime gotcha."""
    global _enum_cache
    if _enum_cache is None:
        items = []
        for i, fname in enumerate(get_pull_files()):
            stem = os.path.splitext(fname)[0]
            items.append((fname, stem, "", _thumb_icon(stem), i))
        items.append(('NONE', "None", "No pulls", 'X', len(items)))
        _enum_cache = items
    return _enum_cache


def refresh():
    global _enum_cache
    _enum_cache = None
    _pull_cache['selection'] = ''
    _pull_cache['object'] = None


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


def _apply_finish_to_pull(pull_obj, finish=None):
    """Swap the shared pull mesh's material to the selected finish.
    Instances link this mesh data, so the whole room follows."""
    if finish is None:
        finish = getattr(bpy.context.scene.hb_closets,
                         'closet_pull_finish', 'Polished Chrome')
    mat = load_finish_material(finish)
    if mat is None or pull_obj.data is None:
        return
    mats = pull_obj.data.materials
    if len(mats) == 1 and mats[0] is mat:
        return
    mats.clear()
    mats.append(mat)


def resolve_pull_object(selection=None, finish=None):
    """The loaded source object for the pull selection (scene prop when
    not overridden; cached, reloaded when the selection changes), with
    the finish applied. Returns None for NONE / missing assets -
    callers drop the pull."""
    if selection is None:
        # Fallback = the standard handle when the scene prop is not
        # registered.
        selection = getattr(bpy.context.scene.hb_closets,
                            'closet_pull', DEFAULT_PULL)
    if not selection or selection == 'NONE':
        return None

    cached = _pull_cache['object']
    if _pull_cache['selection'] == selection and cached is not None:
        try:
            cached.name  # dead reference check (file reload / purge)
            _apply_finish_to_pull(cached, finish)
            return cached
        except ReferenceError:
            pass

    path = os.path.join(HANDLES_DIR, selection)
    if not os.path.exists(path):
        return None
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
    except Exception:
        return None
    pull_obj = next((o for o in dst.objects if o is not None), None)
    if pull_obj is None:
        return None
    _pull_cache['selection'] = selection
    _pull_cache['object'] = pull_obj
    _apply_finish_to_pull(pull_obj, finish)
    return pull_obj


def update_room(self=None, context=None):
    """Dropdown update callback: recalculate every starter - the recalc
    repositions each front's pull and swaps instance data to the new
    selection (see types_closets._position_front_pull)."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
