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

# A model the library draws itself rather than reads off disk. The
# built-in builders answer to the same model names the catalog uses,
# so a saved drawing keeps meaning the same thing; a real installed
# file always wins over a builder.
BUILTIN_SCHEME = 'builtin://'


def _builders():
    try:
        from . import accessory_models
    except Exception:
        return None
    return accessory_models


def _builtin_path(model_name):
    """A loadable pseudo-path for a model the library can draw
    itself, or '' when it cannot."""
    reg = _builders()
    if reg is not None and model_name and reg.offers(model_name):
        return BUILTIN_SCHEME + model_name
    return ''


def is_builtin(path):
    """Whether a path names a model the library draws itself."""
    return bool(path) and path.startswith(BUILTIN_SCHEME)


def build_sized_model(path, name, w, h, d):
    """A built model at given measures - the basket path. Returns a
    fresh object or None; the caller parents and places it."""
    reg = _builders()
    if reg is None or not is_builtin(path):
        return None
    obj = reg.build_sized(path[len(BUILTIN_SCHEME):], w, h, d)
    if obj is not None:
        obj.name = name
    return obj


def restretch_builtin(model, width):
    """Pull a built telescoping model out to a width by rebuilding
    its mesh in place. Says whether it handled the model."""
    reg = _builders()
    if reg is None or model is None:
        return False
    name = model.get('hb_accessory_model', '')
    if name not in getattr(reg, 'STRETCH', {}):
        return False
    if abs(float(model.get('hb_stretch_w', 0.0)) - width) < 1e-5:
        return True
    fresh = reg.build_stretch(name, width)
    if fresh is None:
        return False
    old = model.data
    model.data = fresh.data
    bpy.data.objects.remove(fresh, do_unlink=True)
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    model['hb_stretch_w'] = width
    return True


def apply_finish(obj, color='', fabric=''):
    """Dress a built instance in its chosen finish, where the
    builders are present and the names are known. Quiet otherwise."""
    reg = _builders()
    if reg is not None:
        try:
            reg.apply_finish(obj, color, fabric)
        except Exception:
            pass


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
# A board across the back of an opening with things hung off it. Not a
# panel accessory, whatever the name of the one that uses it suggests:
# it spans the opening rather than screwing to a panel face.
FAMILY_CLEAT = 'CLEAT'

FAMILY_LABELS = {
    FAMILY_OPENING: "Opening",
    FAMILY_PANEL: "Panel",
    FAMILY_INSERT: "Insert",
    FAMILY_CLEAT: "Cleat",
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
    re-appended rather than handed back dead. A builtin path builds
    its model by code instead of reading a file."""
    if not path:
        return None
    cached = _accessory_models.get(path)
    if cached is not None:
        try:
            cached.name
            return cached
        except ReferenceError:
            pass
    if path.startswith(BUILTIN_SCHEME):
        reg = _builders()
        obj = (reg.build(path[len(BUILTIN_SCHEME):])
               if reg is not None else None)
        if obj is not None:
            _accessory_models[path] = obj
        return obj
    if not os.path.isfile(path):
        return None
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
    except Exception:
        return None
    # The model is the first MESH - a file can carry empties or lights
    # that sort ahead of it, and handing one of those back would skip
    # the red not-installed block without drawing anything.
    obj = next((o for o in dst.objects
                if o is not None and o.type == 'MESH'), None)
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


def instance_rig_model(path, name):
    """Every mesh of a model that is drawn to be sized, together with
    the markers those meshes are hung off.

    A telescoping accessory is one mesh and two markers; a wire basket
    is four meshes and four. Either way the markers cannot be shared
    between two of them, so this brings in a copy of the whole rig.

    Returns (meshes, markers), both empty when there is nothing to
    bring in or when what is there turns out not to be a rig."""
    if path and path.startswith(BUILTIN_SCHEME):
        # A built model has no marker rig (yet): it comes back as a
        # plain mesh with no markers, and draws at its natural size.
        obj = instance_accessory_model(path, name)
        return ((obj,), ()) if obj is not None else ((), ())
    if not path or not os.path.isfile(path):
        return (), ()
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
    except Exception:
        return (), ()
    brought = [o for o in dst.objects if o is not None]
    meshes = [o for o in brought
              if o.type == 'MESH'
              and any(m.type == 'HOOK' for m in o.modifiers)]
    if not meshes:
        for obj in brought:
            bpy.data.objects.remove(obj, do_unlink=True)
        return (), ()
    markers = []
    for mesh in meshes:
        for mod in mesh.modifiers:
            if mod.type == 'HOOK' and mod.object is not None \
                    and mod.object not in markers:
                markers.append(mod.object)
    keep = set(meshes) | set(markers)
    for obj in brought:
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    for obj in keep:
        obj.parent = None
    # The markers are read in the frame the meshes were drawn in, so
    # they are put back where they were before anything is moved.
    for marker in markers:
        marker['hb_rig_at'] = tuple(marker.location)
    return tuple(meshes), tuple(markers)


def instance_stretch_model(path, name):
    """A model that is drawn to be pulled out to a width, together
    with the markers its ends are hung off.

    Some accessories telescope. Their model is one mesh with a hook
    at each moving point, and pulling a marker along takes that part
    of the mesh with it while the ends keep their shape - which is
    what a plain scale would ruin. Two of these cannot share a mesh
    the way the fixed models do, because each one has to be hooked to
    markers of its own, so this brings in a copy of the whole rig.

    Returns (model, markers). Both are empty when there is no model
    to bring in, or when the one there is turns out not to telescope
    after all."""
    meshes, markers = instance_rig_model(path, name)
    if not meshes:
        return None, ()
    model = meshes[0]
    model.name = name
    model.matrix_basis.identity()
    return model, markers


# ---------------------------------------------------------------------------
# The catalog
# ---------------------------------------------------------------------------
class AccessoryDef:
    """One line of the catalog.

    key         stable identifier written on the object; renaming the
                label never breaks a saved file
    label       what the person sees in the menu
    family      FAMILY_OPENING / FAMILY_PANEL / FAMILY_INSERT /
                FAMILY_CLEAT
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
    widths      the widths a sized accessory is made in, when it is
                drawn from a rig rather than bought whole. Empty for
                everything that comes at one size or picks a band.
    heights     the heights the same accessory is made in
    depths      the depths it is made in
    min_width   narrowest opening a stretched accessory is made for,
                0 = no lower limit
    max_width   widest one it reaches, 0 = no upper limit
    model_y     how far (m) back from the opening front the model's
                own origin sits. A fact about how the model was drawn,
                not a choice: some are drawn from their front face and
                some about their middle.
    setback     how far (m) back from the front of the opening the
                accessory itself is mounted, measured to its own front
                edge. A choice rather than a fact, and one the person
                can overrule per accessory.
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
                 'model_drop', 'stretch', 'widths', 'heights',
                 'depths', 'min_width', 'max_width', 'setback',
                 'model_y', 'model_z',
                 'floor_snap',
                 'colors', 'fabrics', 'ready', 'description')

    def __init__(self, key, label, family, model='', model_path='',
                 bands=(), band_axis=BAND_BY_WIDTH, width=0.0, height=0.0,
                 depth=0.0, space_above=0.0, space_below=0.0,
                 model_drop=0.0, stretch=False, widths=(),
                 heights=(), depths=(), min_width=0.0,
                 max_width=0.0, setback=0.0, model_y=0.0,
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
        self.widths = tuple(widths)
        self.heights = tuple(heights)
        self.depths = tuple(depths)
        self.setback = setback
        self.min_width = min_width
        self.max_width = max_width
        self.model_y = model_y
        self.model_z = model_z
        self.floor_snap = floor_snap
        self.colors = tuple(colors)
        self.fabrics = tuple(fabrics)
        self.ready = ready
        self.description = description or label

    @property
    def is_sized(self):
        """Whether this one is drawn to a size that is chosen on three
        axes rather than bought at a band."""
        return bool(self.widths and self.heights and self.depths)

    def nearest(self, sizes, want):
        """The size in a list closest to one asked for."""
        if not sizes:
            return 0.0
        return min(sizes, key=lambda s: abs(s - want))

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


def _sizes(raw):
    """A list of sizes from the catalog as metres, in order."""
    return tuple(float(v) for v in (raw or ()))


def _def_from_item(item):
    """One catalog line built from whatever the provider handed over.

    Everything is optional but the code and the name. An item that
    says nothing about its size takes the size of the opening it is
    put in, which is the same as saying it is cut to fit."""
    sizes = []
    for s in item.get('sizes') or ():
        # (label, size, name, path). The name is what a drawing
        # remembers - it has to mean the same thing on the next
        # machine - and the path is only good for this session. A
        # model that is not installed falls back to the library's
        # own light builder for that name, where there is one.
        name = s.get('model') or ''
        path = s.get('model_path') or ''
        if not model_is_installed(path):
            path = _builtin_path(name) or path
        sizes.append((s.get('name') or '',
                      float(s.get('size') or 0.0),
                      name, path))
    model_path = item.get('model_path') or ''
    if not model_is_installed(model_path):
        model_path = _builtin_path(item.get('model') or '') \
            or model_path
    return AccessoryDef(
        key=item.get('code') or '',
        label=item.get('name') or item.get('code') or '',
        family=item.get('family') or FAMILY_OPENING,
        model=item.get('model') or '',
        model_path=model_path,
        bands=tuple(sizes),
        band_axis=item.get('band_axis') or BAND_BY_WIDTH,
        width=float(item.get('width') or 0.0),
        height=float(item.get('height') or 0.0),
        depth=float(item.get('depth') or 0.0),
        space_above=float(item.get('space_above') or 0.0),
        space_below=float(item.get('space_below') or 0.0),
        model_drop=float(item.get('model_drop') or 0.0),
        stretch=bool(item.get('stretch')),
        widths=_sizes(item.get('widths')),
        heights=_sizes(item.get('heights')),
        depths=_sizes(item.get('depths')),
        setback=float(item.get('setback') or 0.0),
        min_width=float(item.get('min_width') or 0.0),
        max_width=float(item.get('max_width') or 0.0),
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
    items = registry_items()
    if not items:
        # Nothing is offering a catalog: the library falls back to
        # its own generic set, drawn by its own light builders. A
        # host add-on that registers later takes over - with its own
        # names, its sizes and its size limits.
        reg = _builders()
        items = list(getattr(reg, 'BUILTIN_ITEMS', ()) or ()) \
            if reg is not None else []
    built = []
    seen = set()
    for item in items:
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
    if path.startswith(BUILTIN_SCHEME):
        return True
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
