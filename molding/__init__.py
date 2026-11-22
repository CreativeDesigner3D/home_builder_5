"""Room molding packages.

One-click molding for a whole room: the user picks a crown, base or
light-rail PACKAGE from a dropdown on the room and the molding is
swept across every eligible cabinet - runs chained across corner
cabinets and multiple walls, islands wrapped, appliances skipped -
with no per-cabinet assignment step.

Modules:
    engine    - library-agnostic sweep geometry (spans, chains,
                perimeter walks, mitred offsets)
    adapters  - per-library fact providers (face frame / frameless)
    packages  - shipped package presets + built-in placeholder profiles
    ops       - apply/refresh operators and sweep object creation
"""

import bpy

from . import ops
from . import packages


def register():
    ops.register()
    if packages.remap_retired_picks not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(packages.remap_retired_picks)


def unregister():
    if packages.remap_retired_picks in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(packages.remap_retired_picks)
    ops.unregister()
