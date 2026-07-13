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


def unregister_profile_path(path):
    if path in _PROFILE_PATHS:
        _PROFILE_PATHS.remove(path)


def profile_paths():
    return tuple(_PROFILE_PATHS)


# (identifier, label, description, stack)
CROWN_PACKAGES = [
    ('SIMPLE', "Simple Crown",
     "One crown profile along the cabinet tops",
     [('Crown Molding/51 Crown', 'crown_simple', 0.0, 0.0)]),
    ('STACKED', "Stacked w/ Spacer",
     "Flat-stock spacer with a crown profile on top",
     [('Spacer/Square Edge Spacer', 'flat_stock', 0.0, 0.0),
      ('Crown Molding/51 Crown', 'crown_simple', 0.0, _in(3.5))]),
    ('FURNITURE', "Furniture Cap",
     "A flat furniture cap overhanging the cabinet tops",
     [('Furniture Caps/Furniture 3 Inch', 'furniture_cap', 0.0, 0.0)]),
]

BASE_PACKAGES = [
    ('SIMPLE', "Simple Base",
     "One base profile along the toe kicks",
     [('Base Molding/Base Shoe', 'base_simple', 0.0, 0.0)]),
]

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
