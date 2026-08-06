"""Closet accessories: the catalog, and where their models come from.

An accessory is a bought item that hangs in a closet - a valet rod, a
wire basket, a pullout hamper, an ironing board. The library builds
nothing for most of them; it places a model, sizes the space it needs
and leaves the rest to the person who buys it. A few (the ironing
board drawer is the one this module ships with) also want melamine
parts of their own, and those the library does build.

Where the models live
---------------------
They do not live here. The 3D models, the finishes and the part
numbers are the manufacturing side of this, and that side is a
separate add-on ("Spaces Manufacturing"). This module looks for that
add-on and asks it where its accessory models are; if it is not
installed the catalog still works, the accessory still takes up its
space, still carries its prompts and still reports its size - it just
draws nothing. Nothing here imports the host add-on at module level,
so the library loads the same either way.

The host is expected to expose ONE of:

    get_closet_accessory_path()   -> folder holding the model blends
    CLOSET_ACCESSORY_PATH         -> the same, as a plain attribute

Mounting families
-----------------
Three, and they decide where an accessory can be dropped and what
sizes it against:

    FAMILY_OPENING  fills an opening, floor to whatever it needs.
                    Sized off the opening; warns when it will not fit.
    FAMILY_PANEL    mounts on the face of a panel. Sized off nothing -
                    it hangs where it is put, at the height it is put.
    FAMILY_INSERT   takes the opening over the way a drawer does: it
                    builds parts of its own, carries a front and
                    leaves an opening above for the rest of the bay.

Model loading follows pulls_closets.resolve_hanger_object: append the
source object once per file, keep it in a module cache, and link the
mesh data into every instance so a room full of one accessory carries
one mesh between them.
"""
import os
import bpy


# ---------------------------------------------------------------------------
# The companion add-on that carries the models
# ---------------------------------------------------------------------------
# Looked up by name rather than imported, so this library has no
# dependency on it and installs on its own.
HOST_ADDON_KEYS = (
    'spaces_manufacturing',
    'pulito_spaces_manufacturing',
    'bl_ext.user_default.spaces_manufacturing',
    'bl_ext.vscode_development.spaces_manufacturing',
)
HOST_PATH_FUNC = 'get_closet_accessory_path'
HOST_PATH_ATTR = 'CLOSET_ACCESSORY_PATH'

# Finishes an accessory can be ordered in. The host add-on prices them
# and holds the part numbers; the library only needs the names so the
# dropdown has something in it before the host is installed.
ACCESSORY_COLORS = (
    'Chrome',
    'Black',
    'Slate',
    'Matte Nickel',
    'Matte Aluminum',
    'Matte Gold',
    'White',
)
ACCESSORY_FABRICS = (
    'Beige',
    'Gray',
    'Black',
)

FAMILY_OPENING = 'OPENING'
FAMILY_PANEL = 'PANEL'
FAMILY_INSERT = 'INSERT'

FAMILY_LABELS = {
    FAMILY_OPENING: "Opening",
    FAMILY_PANEL: "Panel",
    FAMILY_INSERT: "Insert",
}


def _candidate_modules():
    """Every module name worth trying for the host add-on, enabled
    ones first. Extensions land in sys.modules under a repo-prefixed
    name that changes with where the person installed it from, so the
    enabled-addon list is the only reliable source for it."""
    seen = []
    try:
        addons = bpy.context.preferences.addons
    except AttributeError:
        addons = ()
    for addon in addons:
        name = getattr(addon, 'module', '')
        if name and name.split('.')[-1] in (
                'spaces_manufacturing', 'pulito_spaces_manufacturing'):
            if name not in seen:
                seen.append(name)
    for name in HOST_ADDON_KEYS:
        if name not in seen:
            seen.append(name)
    return seen


def host_addon_module():
    """The loaded host add-on module, or None when it is not
    installed / not enabled. Never imports - an add-on that is on is
    already in sys.modules, and one that is off should stay off."""
    import sys
    for name in _candidate_modules():
        mod = sys.modules.get(name)
        if mod is not None:
            return mod
    return None


def accessory_model_dir():
    """Folder the host add-on keeps its accessory blends in, or None.

    The host may answer with a function or a plain attribute; both are
    accepted so the two add-ons can be versioned apart."""
    mod = host_addon_module()
    if mod is None:
        return None
    func = getattr(mod, HOST_PATH_FUNC, None)
    if callable(func):
        try:
            path = func()
        except Exception:
            path = None
    else:
        path = getattr(mod, HOST_PATH_ATTR, None)
    if path and os.path.isdir(path):
        return path
    return None


def is_host_addon_active():
    """True when the models are actually reachable. The catalog does
    not consult this - an accessory is offered either way - but the
    drop does, to decide whether to look for a model at all."""
    return accessory_model_dir() is not None


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
# One appended source object per blend file. Instances link its mesh,
# so a room full of one accessory carries one mesh between them.
_accessory_models = {}


def clear_model_cache():
    """Drop the cache (host add-on installed or updated mid-session)."""
    _accessory_models.clear()


def accessory_model_path(filename):
    """Full path to one accessory blend, or None when the host add-on
    is absent or does not carry that file."""
    folder = accessory_model_dir()
    if folder is None or not filename:
        return None
    path = os.path.join(folder, filename)
    return path if os.path.exists(path) else None


def load_accessory_model(filename):
    """Appended source object for one accessory blend, or None. Cached
    per file; a stale cache entry (file reloaded underneath us) is
    re-appended rather than handed back dead."""
    if not filename:
        return None
    cached = _accessory_models.get(filename)
    if cached is not None:
        try:
            cached.name
            return cached
        except ReferenceError:
            pass
    path = accessory_model_path(filename)
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
    _accessory_models[filename] = obj
    return obj


def instance_accessory_model(filename, name):
    """A fresh object sharing the source model's data, or None when
    there is no model to share. The caller parents and places it."""
    src = load_accessory_model(filename)
    if src is None:
        return None
    obj = bpy.data.objects.new(name, src.data)
    obj.matrix_world = src.matrix_world.copy()
    return obj


# ---------------------------------------------------------------------------
# The catalog
# ---------------------------------------------------------------------------
class AccessoryDef:
    """One line of the catalog.

    key         stable identifier written on the object; renaming the
                label never breaks a saved file
    label       what the person sees in the menu
    family      FAMILY_OPENING / FAMILY_PANEL / FAMILY_INSERT
    model       blend filename in the host add-on's model folder
    width       nominal size (m) of the space it wants, 0 = takes the
                width it is given
    height      nominal height (m) it occupies, 0 = as it comes
    depth       nominal depth (m) it needs, 0 = as it comes
    space_above clearance (m) it needs above itself to be used
    space_below clearance (m) it needs below itself
    colors      finish names offered, () = no finish choice
    fabrics     fabric names offered, () = no fabric choice
    ready       True once the accessory is built out. Everything else
                is catalogued but not yet offered, so the list can be
                filled in a family at a time without the menu growing
                entries that do nothing.
    """

    __slots__ = ('key', 'label', 'family', 'model', 'width', 'height',
                 'depth', 'space_above', 'space_below', 'colors',
                 'fabrics', 'ready', 'description')

    def __init__(self, key, label, family, model='', width=0.0,
                 height=0.0, depth=0.0, space_above=0.0,
                 space_below=0.0, colors=(), fabrics=(), ready=False,
                 description=""):
        self.key = key
        self.label = label
        self.family = family
        self.model = model
        self.width = width
        self.height = height
        self.depth = depth
        self.space_above = space_above
        self.space_below = space_below
        self.colors = tuple(colors)
        self.fabrics = tuple(fabrics)
        self.ready = ready
        self.description = description or label


def _inch(value):
    """Local inch->m, so the catalog reads in the units it is sold in
    without this module reaching up into the package at import time."""
    return value * 0.0254


# The 21 accessories the prior library offered, in the order it
# offered them. Only the ready ones reach the menu.
CATALOG = (
    # --- opening accessories -------------------------------------
    AccessoryDef(
        'WARDROBE_LIFT', "Wardrobe Lift", FAMILY_OPENING,
        model='Wardrobe Lift.blend',
        height=_inch(26.0), depth=_inch(12.0),
        space_above=_inch(3.13), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS,
        description="Pull-down hanging rod for a high opening"),
    AccessoryDef(
        'DIVIDED_DRAWER', "Divided Drawer", FAMILY_OPENING,
        model='Divided Drawer.blend',
        height=_inch(4.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS, fabrics=ACCESSORY_FABRICS,
        description="Compartment insert that drops into a drawer"),
    AccessoryDef(
        'FOLDING_STATION', "Folding Station", FAMILY_OPENING,
        model='Folding Station.blend',
        height=_inch(4.0), depth=_inch(14.0),
        space_above=_inch(3.13), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS,
        description="Pull-out folding surface"),
    AccessoryDef(
        'PULLOUT_SHELF', "Pullout Shelf", FAMILY_OPENING,
        model='Pullout Shelf.blend',
        height=_inch(4.0), depth=_inch(14.0),
        space_above=_inch(3.13), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS,
        description="Sliding shelf on a pair of runners"),
    AccessoryDef(
        'JEWELRY_ORGANIZER', "Jewelry Organizer", FAMILY_OPENING,
        model='Jewelry Organizer.blend',
        height=_inch(2.5), depth=_inch(14.0),
        space_above=_inch(3.13), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS, fabrics=ACCESSORY_FABRICS,
        description="Lined tray with jewelry compartments"),
    AccessoryDef(
        'LINGERIE_DRAWER', "Lingerie Drawer", FAMILY_OPENING,
        model='Lingerie Drawer.blend',
        height=_inch(4.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS, fabrics=ACCESSORY_FABRICS,
        description="Shallow divided drawer insert"),
    AccessoryDef(
        'PULLOUT_HAMPER', "Pullout Hamper", FAMILY_OPENING,
        model='Pullout Hamper.blend',
        height=_inch(21.0), depth=_inch(14.0),
        space_above=_inch(1.0), space_below=_inch(0.25),
        colors=ACCESSORY_COLORS, fabrics=ACCESSORY_FABRICS,
        description="Laundry basket on full-extension runners"),
    AccessoryDef(
        'SHOE_ORGANIZER', "Shoe Organizer", FAMILY_OPENING,
        model='Shoe Organizer.blend',
        height=_inch(6.0), depth=_inch(14.0),
        space_above=_inch(3.13), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS,
        description="Sliding shoe rack"),
    AccessoryDef(
        'SLIDING_PANTS_RACK', "Sliding Pants Rack", FAMILY_OPENING,
        model='Sliding Pants Rack.blend',
        height=_inch(3.0), depth=_inch(14.0),
        space_above=_inch(20.0), space_below=_inch(1.14),
        colors=ACCESSORY_COLORS,
        description="Pull-out rack of trouser bars"),
    AccessoryDef(
        'STORAGE_BOX', "Storage Box", FAMILY_OPENING,
        model='Storage Box.blend',
        height=_inch(11.0), depth=_inch(14.0),
        fabrics=ACCESSORY_FABRICS,
        description="Fabric bin that sits on a shelf"),
    AccessoryDef(
        'WIRE_BASKET', "Wire Basket", FAMILY_OPENING,
        model='Wire Basket.blend',
        height=_inch(11.0), depth=_inch(14.0),
        space_above=_inch(6.23), space_below=_inch(0.25),
        colors=ACCESSORY_COLORS,
        description="Sliding wire basket, banded 18/24/30 wide"),
    # --- panel accessories ---------------------------------------
    AccessoryDef(
        'BELT_RACK', "Belt Rack", FAMILY_PANEL,
        model='Belt Rack.blend',
        width=_inch(2.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS,
        description="Sliding belt rack on a panel face"),
    AccessoryDef(
        'TIE_RACK', "Tie Rack", FAMILY_PANEL,
        model='Tie Rack.blend',
        width=_inch(2.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS,
        description="Sliding tie rack on a panel face"),
    AccessoryDef(
        'SCARF_RACK', "Scarf Rack", FAMILY_PANEL,
        model='Scarf Rack.blend',
        width=_inch(2.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS,
        description="Sliding scarf rack on a panel face"),
    AccessoryDef(
        'VALET_ROD', "Valet Rod", FAMILY_PANEL,
        model='Valet Rod.blend',
        width=_inch(2.0), depth=_inch(14.0),
        colors=ACCESSORY_COLORS,
        description="Pull-out rod for laying out an outfit"),
    AccessoryDef(
        'VALET_PIN', "Valet Pin", FAMILY_PANEL,
        model='Valet Pin.blend',
        width=_inch(1.0), depth=_inch(3.0),
        colors=ACCESSORY_COLORS,
        description="Single hanging pin on a panel face"),
    AccessoryDef(
        'HOOKS', "Hooks", FAMILY_PANEL,
        model='Hooks.blend',
        width=_inch(2.0), depth=_inch(3.0),
        colors=ACCESSORY_COLORS,
        description="Row of hooks on a panel face"),
    AccessoryDef(
        'CLEAT_HOOKS', "Cleat Hooks", FAMILY_PANEL,
        model='Cleat Hooks.blend',
        width=_inch(2.0), depth=_inch(3.0),
        colors=ACCESSORY_COLORS,
        description="Hooks on a mounting cleat"),
    AccessoryDef(
        'IRONING_BOARD', "Ironing Board", FAMILY_PANEL,
        model='Ironing Board.blend',
        width=_inch(14.0), depth=_inch(4.0),
        colors=ACCESSORY_COLORS,
        description="Fold-down ironing board on a panel face"),
    AccessoryDef(
        'MIRROR', "Mirror", FAMILY_PANEL,
        model='Mirror.blend',
        width=_inch(14.0), depth=_inch(1.0),
        colors=ACCESSORY_COLORS,
        description="Mirror mounted on a panel face"),
    # --- insert accessories --------------------------------------
    AccessoryDef(
        'IRONING_BOARD_DRAWER', "Ironing Board Drawer", FAMILY_INSERT,
        model='Ironing Board Shelf Mount Sidelines Elite.blend',
        width=_inch(12.0), height=_inch(5.0), depth=_inch(13.625),
        ready=True,
        description="Ironing board on a shelf mount, behind a drawer "
                    "front, with the rest of the opening left above"),
)

CATALOG_BY_KEY = {d.key: d for d in CATALOG}


def get(key):
    """The catalog line for a key, or None."""
    return CATALOG_BY_KEY.get(key)


def catalog_items(family=None, ready_only=True):
    """Catalog lines, optionally one family's worth. ready_only keeps
    the not-yet-built entries out of the menu while leaving them in
    the catalog for the verify suite to count."""
    out = []
    for d in CATALOG:
        if ready_only and not d.ready:
            continue
        if family is not None and d.family != family:
            continue
        out.append(d)
    return out


def enum_items(family=None):
    """(key, label, description) tuples for a dropdown."""
    return [(d.key, d.label, d.description)
            for d in catalog_items(family)]
