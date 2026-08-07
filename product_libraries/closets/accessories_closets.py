"""Closet accessories: the catalog, and where their models come from.

An accessory is a bought item that hangs in a closet - a valet rod, a
wire basket, a pullout hamper, an ironing board. The library builds
nothing for most of them; it places a model, sizes the space it needs
and leaves the rest to the person who buys it. A few (the ironing
board drawer is the one this module ships with) also want melamine
parts of their own, and those the library does build.

Where the catalog lives
-----------------------
Not here. Which accessories there are, what sizes they come in, what
finishes they are offered in and what their models are called is
product data, and it belongs to whoever sells them. It arrives through
HB5's accessory provider registry: the host application registers a
provider for the closet accessory host key, and this module turns
whatever comes back into the catalog the library reads.

Nothing here imports the host. If no provider is registered the
catalog is simply empty and the Add Accessory menu has nothing in it.
If a provider is there but a particular model file is not, the
accessory still lands, still holds its space, still carries its
prompts and still measures - it draws a red block instead of the
thing. Each item brings its own resolved model path, so this module
never has to know where the host keeps its assets.
"""
import os

import bpy

HOST_KEY = 'closet_accessory'


def _registry():
    """HB5's accessory provider registry, or None if it is not there
    (an older build of the add-on)."""
    try:
        from ... import accessory_registry
    except Exception:
        return None
    return accessory_registry


def registry_items():
    """Whatever the host application offers for closet accessories."""
    reg = _registry()
    if reg is None:
        return []
    try:
        return list(reg.get_items(HOST_KEY))
    except Exception:
        return []


def has_provider():
    """True when something has registered closet accessory data. The
    catalog does not need this - an empty catalog behaves - but the
    Add dialog says something useful when the answer is no."""
    reg = _registry()
    return bool(reg is not None and reg.has_provider(HOST_KEY))


# The finishes and fabrics an accessory can be ordered in are named by
# whatever provides the catalog; these are only the fallbacks used
# when nothing is offered, and for the dropdowns to have a shape.
ACCESSORY_COLORS = (
    'Chrome', 'Black', 'Slate', 'Matte Nickel', 'Matte Aluminum',
    'Matte Gold', 'White',
)
ACCESSORY_FABRICS = ('Fabric Beach', 'Fabric Slate', 'Fabric Black')

# An accessory model is drawn with its origin on its front face and
# its depth running back down +Y. This library runs the same way, so a
# model needs no turning, only putting at the front of the opening it
# belongs to.
MODEL_DEPTH_RUNS_BACK = True

# A panel accessory screws to the face of a panel, and there are four
# faces going: the two sides of the panel at each end of the opening.
PANEL_OUTSIDE_LEFT = 'OUTSIDE_LEFT'
PANEL_INSIDE_LEFT = 'INSIDE_LEFT'
PANEL_INSIDE_RIGHT = 'INSIDE_RIGHT'
PANEL_OUTSIDE_RIGHT = 'OUTSIDE_RIGHT'

PANEL_LOCATIONS = (
    (PANEL_OUTSIDE_LEFT, "Outside Left", "On the far face of the left "
                                         "panel, facing away"),
    (PANEL_INSIDE_LEFT, "Inside Left", "On the left panel, facing "
                                       "into the opening"),
    (PANEL_INSIDE_RIGHT, "Inside Right", "On the right panel, facing "
                                         "into the opening"),
    (PANEL_OUTSIDE_RIGHT, "Outside Right", "On the far face of the "
                                           "right panel, facing away"),
)
PANEL_LOCATION_KEYS = tuple(p[0] for p in PANEL_LOCATIONS)
PANEL_DEFAULT_LOCATION = PANEL_INSIDE_LEFT

# Which figure a size band is measuring. A pull-out is bought by how
# wide it is; a rack on a panel is bought by how far it reaches back;
# a hook comes in patterns rather than sizes.
BAND_BY_WIDTH = 'WIDTH'
BAND_BY_DEPTH = 'DEPTH'
BAND_BY_STYLE = 'STYLE'

FAMILY_OPENING = 'OPENING'
FAMILY_PANEL = 'PANEL'
FAMILY_INSERT = 'INSERT'

FAMILY_LABELS = {
    FAMILY_OPENING: "Opening",
    FAMILY_PANEL: "Panel",
    FAMILY_INSERT: "Insert",
}

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
# One appended source object per model file. Instances link its mesh,
# so a room full of one accessory carries one mesh between them.
_accessory_models = {}


def clear_model_cache():
    """Drop the cache - the host was installed or updated mid-session,
    or the catalog was rebuilt underneath us."""
    _accessory_models.clear()
    clear_catalog_cache()


def load_accessory_model(path):
    """Appended source object for one model file, or None. Cached per
    path; a stale entry (the file reloaded underneath us) is
    re-appended rather than handed back dead."""
    if not path or not os.path.isfile(path):
        return None
    cached = _accessory_models.get(path)
    if cached is not None:
        try:
            cached.name
            return cached
        except ReferenceError:
            pass
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
    except Exception:
        return None
    obj = next((o for o in dst.objects if o is not None), None)
    if obj is None:
        return None
    _accessory_models[path] = obj
    return obj


def instance_accessory_model(path, name):
    """A fresh object sharing the source model's data, or None when
    there is no model to share. The caller parents and places it."""
    src = load_accessory_model(path)
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
    floor_snap  True for the ones that hang down to the floor. Dropped
                near it they sit on it; everything else is taken to
                belong on the floor from much further up
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

    __slots__ = ('key', 'label', 'family', 'model', 'model_path',
                 'bands', 'band_axis', 'width',
                 'height', 'depth', 'space_above', 'space_below',
                 'model_drop', 'stretch', 'model_y', 'model_z',
                 'floor_snap',
                 'colors', 'fabrics', 'ready', 'description')

    def __init__(self, key, label, family, model='', model_path='',
                 bands=(), band_axis=BAND_BY_WIDTH, width=0.0, height=0.0,
                 depth=0.0, space_above=0.0, space_below=0.0,
                 model_drop=0.0, stretch=False, model_y=0.0,
                 model_z=0.0, floor_snap=False, colors=(), fabrics=(),
                 ready=False, description=""):
        self.key = key
        self.label = label
        self.family = family
        self.model = model
        self.model_path = model_path
        self.bands = tuple(bands)
        self.band_axis = band_axis
        self.width = width
        self.height = height
        self.depth = depth
        self.space_above = space_above
        self.space_below = space_below
        self.model_drop = model_drop
        self.stretch = stretch
        self.model_y = model_y
        self.model_z = model_z
        self.floor_snap = floor_snap
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

    def path_for(self, band):
        """Where the model for a band actually is on this machine, or
        "" when it has not been installed. A band with no path is a
        normal state - the accessory draws a block instead."""
        if band is not None and len(band) > 3:
            return band[3]
        if band is not None:
            return ''
        return self.model_path

    def band_items(self):
        """(filename, label, description) tuples for a dropdown."""
        if self.band_axis == BAND_BY_STYLE:
            return [(b[2], b[0], "") for b in self.bands]
        word = ("deep" if self.band_axis == BAND_BY_DEPTH else "wide")
        return [(b[2], b[0], "%s %s" % (_in_label(b[1]), word))
                for b in self.bands]

    def band_width(self, band):
        """How wide the chosen band is, or 0 when its bands are not
        measuring width."""
        if band is None or self.band_axis != BAND_BY_WIDTH:
            return self.width
        return band[1]

    def band_depth(self, band):
        """How deep the chosen band is, falling back to the depth the
        catalog gives the accessory."""
        if band is None or self.band_axis != BAND_BY_DEPTH:
            return self.depth
        return band[1]


def _inch(value):
    """Local inch->m, for anything still written in the units the
    accessories are sold in."""
    return value * 0.0254


def _in_label(value):
    """A metre figure written back out in inches, for a dropdown."""
    return '%g"' % round(value / 0.0254, 2)


def _def_from_item(item):
    """One catalog line built from whatever the provider handed over.

    Everything is optional but the code and the name. An item that
    says nothing about its size takes the size of the opening it is
    put in, which is the same as saying it is cut to fit."""
    sizes = []
    for s in item.get('sizes') or ():
        # (label, size, name, path). The name is what a drawing
        # remembers - it has to mean the same thing on the next
        # machine - and the path is only good for this session.
        sizes.append((s.get('name') or '',
                      float(s.get('size') or 0.0),
                      s.get('model') or '',
                      s.get('model_path') or ''))
    return AccessoryDef(
        key=item.get('code') or '',
        label=item.get('name') or item.get('code') or '',
        family=item.get('family') or FAMILY_OPENING,
        model=item.get('model') or '',
        model_path=item.get('model_path') or '',
        bands=tuple(sizes),
        band_axis=item.get('band_axis') or BAND_BY_WIDTH,
        width=float(item.get('width') or 0.0),
        height=float(item.get('height') or 0.0),
        depth=float(item.get('depth') or 0.0),
        space_above=float(item.get('space_above') or 0.0),
        space_below=float(item.get('space_below') or 0.0),
        model_drop=float(item.get('model_drop') or 0.0),
        stretch=bool(item.get('stretch')),
        model_y=float(item.get('model_y') or 0.0),
        model_z=float(item.get('model_z') or 0.0),
        floor_snap=bool(item.get('floor_snap')),
        colors=tuple(item.get('colors') or ()),
        fabrics=tuple(item.get('fabrics') or ()),
        ready=bool(item.get('ready')),
        description=item.get('description') or '')


_catalog_cache = None
_by_key_cache = None
# Whether a model file is on disk. Asked for every accessory on every
# recalculation, and the answer only changes when something is
# installed, so it is remembered rather than asked of the disk again.
_installed_cache = {}


def clear_catalog_cache():
    """Forget the built catalog, so the next read picks up a provider
    that has just registered or a data file that has just changed."""
    global _catalog_cache, _by_key_cache
    _catalog_cache = None
    _by_key_cache = None
    _installed_cache.clear()


def catalog():
    """Every accessory on offer, in the order the provider gave them.

    Rebuilt whenever it is empty rather than cached as empty, because
    the host application may register its provider after this module
    is first read."""
    global _catalog_cache
    if _catalog_cache:
        return _catalog_cache
    built = []
    seen = set()
    for item in registry_items():
        code = item.get('code')
        if not code or code in seen:
            continue
        seen.add(code)
        try:
            built.append(_def_from_item(item))
        except Exception:
            continue
    _catalog_cache = tuple(built)
    return _catalog_cache


def catalog_by_key():
    """The catalog keyed for lookup. Built once alongside the catalog
    itself - get() is called for every accessory on every
    recalculation, and rebuilding the whole map each time is work for
    nothing."""
    global _by_key_cache
    built = catalog()
    if _by_key_cache is None or len(_by_key_cache) != len(built):
        _by_key_cache = {d.key: d for d in built}
    return _by_key_cache


def __getattr__(name):
    """CATALOG and CATALOG_BY_KEY read like the constants they used to
    be, but the data behind them arrives at run time."""
    if name == 'CATALOG':
        return catalog()
    if name == 'CATALOG_BY_KEY':
        return catalog_by_key()
    raise AttributeError(name)


def get(key):
    """The catalog line for a key, or None."""
    return catalog_by_key().get(key)


def catalog_items(family=None, ready_only=True):
    """Catalog lines, optionally one family's worth. ready_only keeps
    the not-yet-built entries out of the menu while leaving them in
    the catalog."""
    out = []
    for d in catalog():
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


def model_is_installed(path):
    """True when a resolved path points at a file that is there.

    Remembered per path: this is asked for every accessory on every
    recalculation, and a file does not appear or vanish between two
    of them. clear_model_cache() forgets it."""
    if not path:
        return False
    known = _installed_cache.get(path)
    if known is None:
        known = os.path.isfile(path)
        _installed_cache[path] = known
    return known


def accessory_model_path(name):
    """The path a model name resolves to, or None when the catalog
    does not offer it or it has not been installed."""
    if not name:
        return None
    for d in catalog():
        if d.model == name and model_is_installed(d.model_path):
            return d.model_path
        for b in d.bands:
            if b[2] == name and model_is_installed(d.path_for(b)):
                return d.path_for(b)
    return None


def is_host_addon_active():
    """True when something is offering closet accessories AND at least
    one of them has a model that is actually installed. The catalog
    does not consult this - an accessory is offered either way - but
    the drop does, to say whether anything will draw."""
    for d in catalog():
        if model_is_installed(d.model_path):
            return True
        for b in d.bands:
            if model_is_installed(d.path_for(b)):
                return True
    return False
