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
numbers ship in a separate companion add-on. This module looks for
that add-on and asks it where its accessory models are; if it is not
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
# Every finish and fabric the accessories are sold in. An accessory
# offers its own subset, in the order the prior library listed it, so
# the dropdown reads the same as the one the person is used to.
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
    'Fabric Beach',
    'Fabric Slate',
    'Fabric Black',
)

COLORS_PULLOUT = ('Black', 'Matte Aluminum', 'Slate', 'Matte Nickel',
                  'Matte Gold')
COLORS_DRAWER = ('Black', 'Slate', 'Matte Nickel', 'Matte Aluminum',
                 'Matte Gold')
COLORS_HAMPER = ('Black', 'Matte Aluminum', 'Chrome', 'Slate',
                 'Matte Nickel', 'Matte Gold')
COLORS_BASKET = ('Chrome', 'Black', 'Slate', 'Matte Nickel',
                 'Matte Aluminum', 'Matte Gold', 'White')
COLORS_LIFT = ('Black', 'Chrome')

FABRICS_PULLOUT = ('Fabric Beach', 'Fabric Slate')
FABRICS_HAMPER = ('Fabric Beach', 'Fabric Slate', 'Fabric Black')

# An accessory model is drawn with its origin on its front face and
# its depth running back down +Y. This library runs the same way -
# back to front is +Y here too - so a model needs no turning, only
# putting at the front of the opening it belongs to. What differs is
# where the front IS: the prior library had it at y=0, this one has it
# at minus the depth.
MODEL_DEPTH_RUNS_BACK = True

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
    model       blend filename in the host add-on's model folder, for
                an accessory sold at one size only
    bands       (label, width, filename) for an accessory sold in
                widths. The person picks one; it is not stretched to
                fit, which is why a mismatch is worth a warning.
    width       nominal size (m) of the space it wants, 0 = takes the
                width it is given
    height      nominal height (m) it occupies, 0 = as it comes
    depth       nominal depth (m) it needs, 0 = as it comes
    space_above the room (m) wanted above the mounting line, where the
                model's own origin sits
    space_below the room (m) wanted below that line. An accessory
                hangs off its runners, so most of it is below.
    model_drop  how far (m) to lower the model inside that space, for
                the one accessory whose mesh would otherwise poke out
    stretch     True when the model is drawn to the opening width
                rather than picked from a band
    model_y     how far (m) back from the opening front the model sits
    model_z     how far (m) up from the bottom of its space it sits
    colors      finish names offered, () = no finish choice
    fabrics     fabric names offered, () = no fabric choice
    ready       True once the accessory is built out. Everything else
                is catalogued but not yet offered, so the list can be
                filled in a family at a time without the menu growing
                entries that do nothing.
    """

    __slots__ = ('key', 'label', 'family', 'model', 'bands', 'width',
                 'height', 'depth', 'space_above', 'space_below',
                 'model_drop', 'stretch', 'model_y', 'model_z',
                 'colors', 'fabrics', 'ready', 'description')

    def __init__(self, key, label, family, model='', bands=(),
                 width=0.0, height=0.0, depth=0.0, space_above=0.0,
                 space_below=0.0, model_drop=0.0, stretch=False,
                 model_y=0.0, model_z=0.0, colors=(), fabrics=(),
                 ready=False, description=""):
        self.key = key
        self.label = label
        self.family = family
        self.model = model
        self.bands = tuple(bands)
        self.width = width
        self.height = height
        self.depth = depth
        self.space_above = space_above
        self.space_below = space_below
        self.model_drop = model_drop
        self.stretch = stretch
        self.model_y = model_y
        self.model_z = model_z
        self.colors = tuple(colors)
        self.fabrics = tuple(fabrics)
        self.ready = ready
        self.description = description or label

    @property
    def reserved_height(self):
        """The vertical space the accessory asks an opening for. An
        accessory with clearances asks for the sum of them; one
        without asks for its own height."""
        span = self.space_above + self.space_below
        return span if span > 0.0 else self.height

    def band_for_width(self, width):
        """The band closest to a width - what an accessory should
        arrive as when it is dropped into an opening of that size."""
        if not self.bands:
            return None
        return min(self.bands, key=lambda b: abs(b[1] - width))

    def band_by_model(self, filename):
        """The band a stored filename names, or None if the catalog
        has moved on and no longer offers it."""
        for band in self.bands:
            if band[2] == filename:
                return band
        return None

    def band_items(self):
        """(filename, label, description) tuples for a dropdown."""
        return [(b[2], b[0], "%s wide" % _in_label(b[1]))
                for b in self.bands]


def _inch(value):
    """Local inch->m, so the catalog reads in the units it is sold in
    without this module reaching up into the package at import time."""
    return value * 0.0254


def _in_label(value):
    """A metre figure written back out in inches, for a dropdown."""
    return '%g"' % round(value / 0.0254, 2)


# The 21 accessories the prior library offered, in the order it
# offered them. Only the ready ones reach the menu.
CATALOG = (
    # --- opening accessories -------------------------------------
    # The pull-outs. Each is bought at a set width rather than cut to
    # fit, so each carries the widths it is sold in and the person
    # picks one; dropping it into an opening picks the nearest. The
    # two clearance figures are the room it wants above and below its
    # runners, which is where the model's own origin sits.
    AccessoryDef(
        'DIVIDED_DRAWER', "Divided Drawer", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0), 'Divided Drawer 18.blend'),
               ('24" Wide', _inch(24.0), 'Divided Drawer 24.blend'),
               ('30" Wide', _inch(30.0), 'Divided Drawer 30.blend')),
        depth=_inch(14.0),
        space_above=_inch(1.25984), space_below=_inch(9.24016),
        colors=COLORS_DRAWER, fabrics=FABRICS_PULLOUT, ready=True,
        description="Lined drawer on runners, divided into "
                    "compartments"),
    AccessoryDef(
        'FOLDING_STATION', "Folding Station", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Folding Station - Flat - 18 x 14.blend'),
               ('24" Wide', _inch(24.0),
                'Folding Station - Flat - 24 x 14.blend'),
               ('30" Wide', _inch(30.0),
                'Folding Station - Flat - 30 x 14.blend')),
        depth=_inch(14.0),
        space_above=_inch(0.88583), space_below=_inch(3.77953),
        colors=COLORS_PULLOUT, fabrics=FABRICS_PULLOUT, ready=True,
        description="Flat surface that slides out to fold on"),
    AccessoryDef(
        'PULLOUT_SHELF', "Pullout Shelf", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Divided Pull Out Shelf 18 x 14.blend'),
               ('24" Wide', _inch(24.0),
                'Divided Pull Out Shelf 24 x 14.blend'),
               ('30" Wide', _inch(30.0),
                'Divided Pull Out Shelf 30 x 14.blend')),
        depth=_inch(14.0),
        space_above=_inch(2.14567), space_below=_inch(2.8937),
        colors=COLORS_PULLOUT, fabrics=FABRICS_PULLOUT, ready=True,
        description="Divided shelf on a pair of runners"),
    AccessoryDef(
        'JEWELRY_ORGANIZER', "Jewelry Organizer", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Pull Out Jewelry Organizer 18 x 14.blend'),
               ('24" Wide', _inch(24.0),
                'Pull Out Jewelry Organizer 24 x 14.blend'),
               ('30" Wide', _inch(30.0),
                'Pull Out Jewelry Organizer 30 X 14.blend')),
        depth=_inch(14.0),
        space_above=_inch(0.88583), space_below=_inch(2.51969),
        colors=COLORS_PULLOUT, fabrics=FABRICS_PULLOUT, ready=True,
        description="Lined tray of jewelry compartments on runners"),
    AccessoryDef(
        'LINGERIE_DRAWER', "Lingerie Drawer", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Pull Out Lingerie Drawer 18 x 14.blend'),
               ('24" Wide', _inch(24.0),
                'Pull Out Lingerie Drawer 24 x 14.blend'),
               ('30" Wide', _inch(30.0),
                'Pull Out Lingerie Drawer 30 x 14.blend')),
        depth=_inch(14.0),
        space_above=_inch(0.88583), space_below=_inch(5.41339),
        colors=COLORS_PULLOUT, fabrics=FABRICS_PULLOUT, ready=True,
        description="Shallow divided drawer on runners"),
    AccessoryDef(
        'PULLOUT_HAMPER', "Pullout Hamper", FAMILY_OPENING,
        bands=(('Engage 18" Wide', _inch(18.0),
                'Pull Out Hamper Engage 18 x 14.blend'),
               ('Engage 24" Wide', _inch(24.0),
                'Pull Out Hamper Engage 24 x 14.blend'),
               ('Engage 30" Wide', _inch(30.0),
                'Pull Out Hamper Engage 30 x 14.blend'),
               ('Synergy 18" Wide', _inch(18.0),
                'Pull Out Hamper Synergy 18.blend'),
               ('Synergy 24" Wide', _inch(24.0),
                'Pull Out Hamper Synergy 24.blend'),
               ('Synergy 30" Wide', _inch(30.0),
                'Pull Out Hamper Synergy 30.blend')),
        depth=_inch(14.0),
        space_above=_inch(0.88583), space_below=_inch(22.36417),
        colors=COLORS_HAMPER, fabrics=FABRICS_HAMPER, ready=True,
        description="Laundry basket on full-extension runners"),
    AccessoryDef(
        'SHOE_ORGANIZER', "Shoe Organizer", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Shoe Organizer 18 x 14.blend'),
               ('24" Wide', _inch(24.0),
                'Shoe Organizer 24 x 14.blend'),
               ('30" Wide', _inch(30.0),
                'Shoe Organizer 30 x 14.blend')),
        depth=_inch(14.0),
        space_above=_inch(8.5), space_below=_inch(6.0),
        colors=COLORS_PULLOUT, ready=True,
        description="Sliding rack of angled shoe shelves"),
    AccessoryDef(
        'SLIDING_PANTS_RACK', "Sliding Pants Rack", FAMILY_OPENING,
        bands=(('18" Wide', _inch(18.0),
                'Pull Out Pants Rack 18.blend'),
               ('24" Wide', _inch(24.0),
                'Pull Out Pants Rack 24.blend'),
               ('30" Wide', _inch(30.0),
                'Pull Out Pants Rack 30.blend')),
        depth=_inch(14.0),
        space_above=_inch(0.88583), space_below=_inch(26.11417),
        model_drop=_inch(0.33858),
        colors=COLORS_PULLOUT, ready=True,
        description="Pull-out frame of trouser bars"),
    AccessoryDef(
        'STORAGE_BOX', "Storage Box", FAMILY_OPENING,
        bands=(('15" Wide', _inch(15.0), 'Storage Box 15 x 14.blend'),
               ('18" Wide', _inch(18.0), 'Storage Box 18 x 14.blend'),
               ('24" Wide', _inch(24.0), 'Storage Box 24 x 14.blend')),
        height=_inch(7.43), depth=_inch(13.55),
        fabrics=FABRICS_PULLOUT,
        description="Fabric bin that sits on a shelf"),
    AccessoryDef(
        'WIRE_BASKET', "Wire Basket", FAMILY_OPENING,
        height=_inch(11.0), depth=_inch(14.0),
        space_above=_inch(6.23), space_below=_inch(0.25),
        colors=COLORS_BASKET,
        description="Sliding wire basket, banded 18/24/30 wide"),
    AccessoryDef(
        'WARDROBE_LIFT', "Wardrobe Lift", FAMILY_OPENING,
        model='Wardrobe Lift.blend',
        height=_inch(39.0), depth=_inch(5.79),
        stretch=True, model_y=_inch(5.0), model_z=_inch(4.35),
        colors=COLORS_LIFT,
        description="Pull-down hanging rod for a high opening"),
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
