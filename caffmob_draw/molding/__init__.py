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

from . import ops


def register():
    ops.register()


def unregister():
    ops.unregister()
