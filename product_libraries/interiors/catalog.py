"""The Furnish tool's catalog: what it places, by category.

Plain data, so the tool, its TOOL page and the tests read one table.
Each item: (key, label, category, placement, appliance type). Placement
'WALL' stands it against a wall, its back to it, like a cabinet. Keys
are only ever appended within a category: a saved choice is its key.
"""

ITEMS = (
    ('TOILET', "Toilet", 'Bath', 'WALL', 'TOILET'),
    ('PEDESTAL_SINK', "Pedestal Sink", 'Bath', 'WALL', 'PEDESTAL_SINK'),
    ('ALCOVE_TUB', "Alcove Tub", 'Bath', 'WALL', 'ALCOVE_TUB'),
    ('FREESTANDING_TUB', "Freestanding Tub", 'Bath', 'WALL', 'FREESTANDING_TUB'),
    ('SHOWER', "Shower", 'Bath', 'WALL', 'SHOWER'),
    ('TUB_SHOWER', "Tub Shower", 'Bath', 'WALL', 'TUB_SHOWER'),
)

CATEGORIES = ('Bath',)


def _enum_items():
    out = []
    for category in CATEGORIES:
        out.append(('HEADER_' + category.upper(), category, ""))
        out.extend((key, label, f"Place a {label.lower()}")
                   for key, label, cat, _p, _t in ITEMS if cat == category)
    return out


# For an EnumProperty: category headings ('HEADER_...') and their items
ENUM_ITEMS = _enum_items()


def item(key):
    """The catalog row for a key, or None."""
    return next((row for row in ITEMS if row[0] == key), None)


def item_class(key):
    """The class that creates the item: an appliance type's class."""
    from ..common import types_appliances
    row = item(key)
    if row is None:
        return None
    for cls in vars(types_appliances).values():
        if isinstance(cls, type) and getattr(cls, 'APPLIANCE_TYPE', None) == row[4]:
            return cls
    return None
