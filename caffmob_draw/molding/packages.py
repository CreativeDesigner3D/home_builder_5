"""Shipped molding package presets and profile resolution.

A package is a named STACK of moldings: each entry is
(profile_ref, fallback_key, forward_offset, vertical_offset). Stacks
let one package build layered setups - a spacer with a crown on top,
or a furniture cap - without any per-cabinet configuration.

Profile GEOMETRY does not ship with this addon. Separately installed
molding asset packs call register_profile_path() with a folder of
category subfolders holding profile .blends (each containing a curve
object named like the file stem); profile_ref is the
"Category/Profile Name" path into whichever pack provides it. When no
installed pack provides a profile, a code-generated placeholder
cross-section (fallback_key) keeps the package functional.
"""

import os

import bpy

from .. import units


def _in(v):
    return units.inch(v)


# ---------------------------------------------------------------------------
# Profile providers (installed separately)
# ---------------------------------------------------------------------------

_PROFILE_PATHS = []


def register_profile_path(path):
    """Register a molding asset pack's root folder. Called by the
    pack's own register(); safe to call repeatedly."""
    if path and os.path.isdir(path) and path not in _PROFILE_PATHS:
        _PROFILE_PATHS.append(path)
        _category_enum_cache.clear()
        _profile_height_cache.clear()


def unregister_profile_path(path):
    if path in _PROFILE_PATHS:
        _PROFILE_PATHS.remove(path)
        _category_enum_cache.clear()
        _profile_height_cache.clear()


def profile_paths():
    return tuple(_PROFILE_PATHS)


# Cached per category: Blender keeps only weak references to dynamic
# enum strings, so the item lists must outlive the property callbacks.
_category_enum_cache = {}


def profile_enum_items(category):
    """Enum items for a pack category: DEFAULT (the package preset's
    profile) plus every profile .blend found across the registered
    packs. Used by the room's profile-override dropdowns."""
    cached = _category_enum_cache.get(category)
    if cached is not None:
        return cached
    names = []
    seen = set()
    for base in _PROFILE_PATHS:
        folder = os.path.join(base, category)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith('.blend'):
                stem = f[:-6]
                if stem not in seen:
                    seen.add(stem)
                    names.append(stem)
    items = tuple(
        [('DEFAULT', "Default", "Use the package's standard profile")]
        + [(n, n, "") for n in names])
    _category_enum_cache[category] = items
    return items


# (identifier, label, description, stack)
CROWN_PACKAGES = [
    ('SIMPLE', "Simple Crown",
     "One crown profile along the cabinet tops",
     [('Crown Molding/51 Crown', 'crown_simple', 0.0, 0.0)]),
    ('STACKED', "Stacked w/ Spacer",
     "Flat-stock spacer with a crown profile on top",
     [('Spacer/Square Edge Spacer', 'flat_stock', 0.0, 0.0),
      # The crown mounts ON the spacer: STACK_FRONT pushes its path
      # forward by the spacer's measured thickness, and STACK_OFFSET
      # resolves to the room's adjustable height on the spacer.
      ('Crown Molding/51 Crown', 'crown_simple', 'STACK_FRONT',
       'STACK_OFFSET')]),
    ('SPACER', "Spacer Only",
     "Flat-stock spacer at the reveal line with no crown profile",
     [('Spacer/Square Edge Spacer', 'flat_stock', 0.0, 0.0)]),
]

# The furniture cap is an independent room TOGGLE, not a crown package:
# it caps the cabinet TOP line and composes with whichever crown
# package (or none) sits at the reveal below it.
FURNITURE_CAP_STACK = [
    ('Furniture Caps/Furniture 3 Inch', 'furniture_cap', 0.0, 0.0),
]

BASE_PACKAGES = [
    ('SIMPLE', "Simple Base",
     "One base profile along the toe kicks",
     [('Base Molding/Standard Base', 'base_simple', 0.0, 0.0)]),
]

# Optional base shoe, toggled per room and applied against the FRONT
# of the base molding (its sweep path shifts forward by the shoe's own
# measured depth so its back face lands on the base molding's face).
BASE_SHOE_REF = 'Base Molding/Base Shoe'
BASE_SHOE_FALLBACK = 'base_shoe'

LIGHT_RAIL_PACKAGES = [
    ('SIMPLE', "Simple Light Rail",
     "One light-rail profile under the upper cabinet fronts",
     [('Light Rail/Cove Cut LR', 'light_rail_simple', 0.0, 0.0)]),
]

PACKAGES = {
    'CROWN': CROWN_PACKAGES,
    'BASE': BASE_PACKAGES,
    'LIGHT_RAIL': LIGHT_RAIL_PACKAGES,
}


def package_stack(molding_type, identifier):
    for ident, _label, _desc, stack in PACKAGES[molding_type]:
        if ident == identifier:
            return stack
    return None


def stack_has_adjustable_offset(molding_type, identifier):
    """True when the package's stack contains a STACK_OFFSET entry -
    used to enable the room's stack-offset field in the UI."""
    stack = package_stack(molding_type, identifier)
    return bool(stack) and any(dy == 'STACK_OFFSET'
                               for _r, _f, _dx, dy in stack)


def stack_uses_category(molding_type, identifier, category):
    """True when the package's stack has an entry whose profile lives
    in `category` - used to enable that category's profile-override
    dropdown in the UI."""
    stack = package_stack(molding_type, identifier)
    return bool(stack) and any(
        ref.replace("\\", "/").split("/")[0] == category
        for ref, _f, _dx, _dy in stack)


# Enum item lists are cached at module level: Blender keeps only weak
# references to dynamic enum strings, so the lists handed to the
# property callbacks must stay alive.
_ENUM_CACHE = {}
for _mtype, _pkgs in PACKAGES.items():
    _ENUM_CACHE[_mtype] = tuple(
        [('NONE', "None", "No molding")]
        + [(ident, label, desc) for ident, label, desc, _stack in _pkgs])


def enum_items(molding_type):
    return _ENUM_CACHE[molding_type]


# ---------------------------------------------------------------------------
# Built-in placeholder profiles
# ---------------------------------------------------------------------------
# Closed 2D outlines in profile-local coordinates: +Y is up along the
# cabinet face, X is the depth direction (negative back toward the
# cabinet). Authored so the outline sits against the swept path line;
# swap for curated profile assets without touching the sweep code.

_PROFILE_OUTLINES = {
    # Sprung crown look-alike: rises above the top line, leaning back.
    'crown_simple': [
        (0.0, 0.0), (0.0, _in(0.5)), (-_in(0.125), _in(0.75)),
        (-_in(0.625), _in(2.5)), (-_in(0.75), _in(2.75)),
        (-_in(0.75), _in(3.0)), (-_in(0.875), _in(3.0)),
        (-_in(0.875), 0.0),
    ],
    # 1x4 flat stock spacer.
    'flat_stock': [
        (0.0, 0.0), (0.0, _in(3.5)),
        (-_in(0.75), _in(3.5)), (-_in(0.75), 0.0),
    ],
    # Flat cap slab with a nose overhanging the face.
    'furniture_cap': [
        (_in(0.375), 0.0), (_in(0.375), _in(1.0)),
        (-_in(0.75), _in(1.0)), (-_in(0.75), 0.0),
    ],
    # Base profile: flat stock with an eased top edge.
    'base_simple': [
        (0.0, 0.0), (0.0, _in(2.5)), (-_in(0.25), _in(3.0)),
        (-_in(0.625), _in(3.0)), (-_in(0.625), 0.0),
    ],
    # Base shoe: small quarter-round-ish trim at the floor line.
    'base_shoe': [
        (0.0, 0.0), (0.0, _in(0.375)), (-_in(0.1875), _in(0.75)),
        (-_in(0.4375), _in(0.75)), (-_in(0.4375), 0.0),
    ],
    # Light rail hanging below the upper's bottom line.
    'light_rail_simple': [
        (0.0, 0.0), (0.0, -_in(1.25)), (-_in(0.25), -_in(1.5)),
        (-_in(0.75), -_in(1.5)), (-_in(0.75), 0.0),
    ],
}


def _finish_profile(obj, collection):
    collection.objects.link(obj)
    if obj.type == 'CURVE':
        # Order matters: fill_mode='NONE' is rejected on 3D curves.
        obj.data.dimensions = '2D'
        obj.data.bevel_depth = 0.0
        obj.data.fill_mode = 'NONE'
    obj.scale = (1.0, 1.0, 1.0)
    obj.hide_viewport = True
    obj.hide_render = True
    obj['IS_HB_MOLDING_PROFILE'] = True
    return obj


def _load_library_profile(profile_ref, collection):
    """Append `Category/Profile Name` from the first registered asset
    pack that provides it. The .blend contains an object named like the
    file stem (the molding-library convention)."""
    parts = profile_ref.replace("\\", "/").split("/")
    stem = parts[-1]
    for base in _PROFILE_PATHS:
        path = os.path.join(base, *parts) + ".blend"
        if not os.path.isfile(path):
            continue
        try:
            with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.objects = ([stem] if stem in data_from.objects
                                   else [])
        except Exception:
            continue
        if not data_to.objects or data_to.objects[0] is None:
            continue
        return _finish_profile(data_to.objects[0], collection)
    return None


# Profile cross-section metrics, cached per ref: measuring a library
# profile means loading its .blend once. Each entry is (top, depth) -
# how far the outline rises above its mount line and how far it
# projects back from its face line.
_profile_height_cache = {}


def _curve_metrics(obj):
    xs = []
    ys = []
    for spline in obj.data.splines:
        points = (spline.bezier_points if spline.type == 'BEZIER'
                  else spline.points)
        for p in points:
            xs.append(p.co.x)
            ys.append(p.co.y)
    if not ys:
        return (0.0, 0.0)
    # Thickness is the full X extent of the outline - sign-agnostic,
    # since packs may author the section on either side of the origin.
    return (max(ys), max(xs) - min(xs))


def _profile_metrics(profile_ref, fallback_key):
    if profile_ref in _profile_height_cache:
        return _profile_height_cache[profile_ref]
    metrics = None
    parts = profile_ref.replace("\\", "/").split("/")
    stem = parts[-1]
    for base in _PROFILE_PATHS:
        path = os.path.join(base, *parts) + ".blend"
        if not os.path.isfile(path):
            continue
        try:
            with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.objects = ([stem] if stem in data_from.objects
                                   else [])
        except Exception:
            continue
        if not data_to.objects or data_to.objects[0] is None:
            continue
        obj = data_to.objects[0]
        if obj.type == 'CURVE':
            metrics = _curve_metrics(obj)
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.curves.remove(data)
        if metrics is not None:
            break
    if metrics is None:
        outline = _PROFILE_OUTLINES.get(fallback_key) or []
        xs = [x for x, _y in outline]
        metrics = (max((y for _x, y in outline), default=0.0),
                   (max(xs) - min(xs)) if xs else 0.0)
    _profile_height_cache[profile_ref] = metrics
    return metrics


def profile_top_height(profile_ref, fallback_key):
    """How far the profile rises above the sweep path (max Y). Used to
    sit the furniture cap on top of the tallest crown-stack element."""
    return _profile_metrics(profile_ref, fallback_key)[0]


def profile_front_depth(profile_ref, fallback_key):
    """The profile's thickness off the sweep path (max X extent on the
    mounted side). Used to push the base shoe's path forward by the
    base MOLDING's thickness so the shoe applies to its front."""
    return _profile_metrics(profile_ref, fallback_key)[1]


def make_profile_object(profile_ref, fallback_key, name, collection):
    """Profile curve for a sweep's bevel_object: the library profile
    from an installed asset pack when available, else the built-in
    placeholder outline for `fallback_key`. Returns None when neither
    resolves."""
    obj = _load_library_profile(profile_ref, collection)
    if obj is not None:
        return obj
    outline = _PROFILE_OUTLINES.get(fallback_key)
    if outline is None:
        return None
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '2D'
    curve.fill_mode = 'NONE'
    spline = curve.splines.new('POLY')
    spline.points.add(len(outline) - 1)
    for pt, (x, y) in zip(spline.points, outline):
        pt.co = (x, y, 0.0, 1.0)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    return _finish_profile(obj, collection)
