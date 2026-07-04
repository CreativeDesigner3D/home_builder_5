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
from ...units import inch


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

# ---------------------------------------------------------------------------
# Display hangers: three per rod (ends + center), instancing a model
# from assets/hangers/. Instances share the model's mesh data, so a
# model swap updates every rod in the room in one write.
# ---------------------------------------------------------------------------
HANGERS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'hangers')
DEFAULT_HANGER = 'Hanger Model.blend'
TAG_HANGER = 'IS_CLOSET_HANGER'
_HANGER_END_OFFSET = inch(6.0)


def user_hangers_dir(create=False):
    """User-installed hanger models. Only the bare hanger ships with
    the library; the clothes models install as a downloadable pack
    (Install Model Pack button) into the extension's user data folder,
    so they never live in the repo."""
    root = bpy.utils.extension_path_user(
        '.'.join(__package__.split('.')[:3]), path='user_data',
        create=create)
    d = os.path.join(root, 'hangers')
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def _hanger_path(filename):
    """Resolve a hanger blend across the bundled folder and the
    user-installed pack (bundled wins on a name clash)."""
    for folder in (HANGERS_DIR, user_hangers_dir()):
        p = os.path.join(folder, filename)
        if os.path.exists(p):
            return p
    return None

_hanger_enum_cache = None
_hanger_override_enum_cache = None
# One loaded source object per model file (several can be live at once
# when hangers carry per-object overrides).
_hanger_models = {}
# Garment drop length per model file (measured from the mesh, cached).
_hanger_drops = {}


def get_hanger_files():
    """Sorted hanger model blends from the bundled folder AND the
    user-installed pack, the bare hanger hoisted first (= dynamic-enum
    default)."""
    names = set()
    for folder in (HANGERS_DIR, user_hangers_dir()):
        if os.path.isdir(folder):
            names.update(f for f in os.listdir(folder)
                         if f.lower().endswith('.blend'))
    files = sorted(names)
    if DEFAULT_HANGER in files:
        files.remove(DEFAULT_HANGER)
        files.insert(0, DEFAULT_HANGER)
    return files


def hanger_enum_items(self, context):
    global _hanger_enum_cache
    if _hanger_enum_cache is None:
        items = [(f, os.path.splitext(f)[0], "")
                 for f in get_hanger_files()]
        items.append(('NONE', "None", "No hangers"))
        _hanger_enum_cache = items
    return _hanger_enum_cache


def hanger_override_enum_items(self, context):
    """Items for the per-hanger right-click override: Room Default
    first (follow the scene Hangers option), then the models."""
    global _hanger_override_enum_cache
    if _hanger_override_enum_cache is None:
        items = [('SCENE', "Room Default",
                  "Follow the Hangers option in the sidebar")]
        items += [(f, os.path.splitext(f)[0], "")
                  for f in get_hanger_files()]
        _hanger_override_enum_cache = items
    return _hanger_override_enum_cache


def resolve_hanger_object(selection):
    """Loaded source object for a hanger model (one cache slot per
    model - overrides can keep several live at once). None for NONE /
    missing assets."""
    if not selection or selection == 'NONE':
        return None
    cached = _hanger_models.get(selection)
    if cached is not None:
        try:
            cached.name
            return cached
        except ReferenceError:
            pass
    path = _hanger_path(selection)
    if path is None:
        return None
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
    except Exception:
        return None
    obj = next((o for o in dst.objects if o is not None), None)
    if obj is None:
        return None
    _hanger_models[selection] = obj
    return obj


def hanger_drop_length(selection):
    """How far a model's garment hangs below the rod, measured from the
    mesh (origin sits at the rod hook; the drop is the extent below
    it). Cached per model file."""
    drop = _hanger_drops.get(selection)
    if drop is not None:
        return drop
    obj = resolve_hanger_object(selection)
    if obj is None or obj.data is None or not len(obj.data.vertices):
        drop = 0.0
    else:
        drop = max(0.0, -min(v.co.z for v in obj.data.vertices))
    _hanger_drops[selection] = drop
    return drop


def hangers_that_fit(clearance):
    """Model files whose garment clears the space below a rod (with a
    little air). Long dresses/coats only qualify in long-hang sections;
    everything falls back to the shortest model so a very low rod still
    gets SOMETHING on it."""
    files = get_hanger_files()
    limit = clearance - inch(0.5)
    fits = [f for f in files if hanger_drop_length(f) <= limit]
    if fits:
        return fits
    shortest = min(files, key=hanger_drop_length, default=None)
    return [shortest] if shortest else []


def reconcile_rod_hangers(rod_obj, rod_length):
    """Create/remove/refresh the three display hangers on one rod
    (called from the rod layout every recalc). Hangers parent to the
    rod at 6" in from each end plus the center, hanging in the rod's
    local frame the way the models were authored. Rods too short for
    the end offsets - and the None selection - carry no hangers.

    A hanger can carry a per-object model override (hb_hanger_model,
    set from its right-click menu); overridden hangers keep their model
    when the room selection changes."""
    existing = [c for c in rod_obj.children if c.get(TAG_HANGER)]
    # Placement previews carry no hangers - the preview rod is deleted
    # on every commit/cancel and its hangers would be left behind.
    if rod_obj.get('hb_preview'):
        for c in existing:
            bpy.data.objects.remove(c, do_unlink=True)
        return
    selection = getattr(bpy.context.scene.hb_closets,
                        'closet_hanger_model', DEFAULT_HANGER)
    show = (selection and selection != 'NONE'
            and rod_length > 2.0 * _HANGER_END_OFFSET + inch(2.0))
    model = resolve_hanger_object(selection) if show else None
    if model is None:
        for c in existing:
            bpy.data.objects.remove(c, do_unlink=True)
        return
    while len(existing) > 3:
        bpy.data.objects.remove(existing.pop(), do_unlink=True)
    while len(existing) < 3:
        o = bpy.data.objects.new('Hanger', model.data)
        try:
            bpy.context.scene.collection.objects.link(o)
        except RuntimeError:
            pass
        o.parent = rod_obj
        o[TAG_HANGER] = True
        o['MENU_ID'] = 'HOME_BUILDER_MT_closet_hanger_commands'
        existing.append(o)
    xs = (_HANGER_END_OFFSET, rod_length / 2.0,
          rod_length - _HANGER_END_OFFSET)
    for o, x in zip(existing, xs):
        override = o.get('hb_hanger_model', '')
        m = resolve_hanger_object(override) if override else None
        if m is None:
            m = model
        if o.data is not m.data:
            o.data = m.data
        if not o.get('MENU_ID'):
            o['MENU_ID'] = 'HOME_BUILDER_MT_closet_hanger_commands'
        o.location = (x, 0.0, 0.0)
        o.rotation_euler = (0.0, 0.0, 0.0)

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
    global _enum_cache, _hanger_enum_cache, _hanger_override_enum_cache
    _enum_cache = None
    _pull_cache['selection'] = ''
    _pull_cache['object'] = None
    _hanger_enum_cache = None
    _hanger_override_enum_cache = None
    _hanger_models.clear()
    _hanger_drops.clear()


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


def current_pull_stem():
    """Display name of the active pull selection (file stem)."""
    selection = getattr(bpy.context.scene.hb_closets,
                        'closet_pull', DEFAULT_PULL)
    if not selection or selection == 'NONE':
        return ''
    return os.path.splitext(selection)[0]


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
