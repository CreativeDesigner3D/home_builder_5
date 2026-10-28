"""The Furnish tool's catalog: what it places, by category.

Plain data, so the tool, its TOOL page and the tests read one table.
Each item: (key, label, category, placement, type) - the type an
appliance type for Bath, a fixture kind for Lighting. Placement 'WALL'
stands it against a wall, its back to it, like a cabinet; 'WALL_MOUNT'
up a wall at its mounting height; 'CEILING' hung from the ceiling;
'FLOOR' free on the floor. Keys are only ever appended within a
category: a saved choice is its key.
"""

ITEMS = (
    ('TOILET', "Toilet", 'Bath', 'WALL', 'TOILET'),
    ('PEDESTAL_SINK', "Pedestal Sink", 'Bath', 'WALL', 'PEDESTAL_SINK'),
    ('ALCOVE_TUB', "Alcove Tub", 'Bath', 'WALL', 'ALCOVE_TUB'),
    ('FREESTANDING_TUB', "Freestanding Tub", 'Bath', 'WALL', 'FREESTANDING_TUB'),
    ('SHOWER', "Shower", 'Bath', 'WALL', 'SHOWER'),
    ('TUB_SHOWER', "Tub Shower", 'Bath', 'WALL', 'TUB_SHOWER'),
    ('PENDANT', "Pendant", 'Lighting', 'CEILING', 'PENDANT'),
    ('FLUSH_MOUNT', "Flush Mount", 'Lighting', 'CEILING', 'FLUSH'),
    ('RECESSED', "Recessed Can", 'Lighting', 'CEILING', 'RECESSED'),
    ('CHANDELIER', "Chandelier", 'Lighting', 'CEILING', 'CHANDELIER'),
    ('CEILING_FAN', "Ceiling Fan", 'Lighting', 'CEILING', 'FAN'),
    ('SCONCE', "Wall Sconce", 'Lighting', 'WALL_MOUNT', 'SCONCE'),
    ('VANITY_LIGHT', "Vanity Light", 'Lighting', 'WALL_MOUNT', 'VANITY'),
)

CATEGORIES = ('Bath', 'Lighting')


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
    """The class that creates the item: a fixture kind's for Lighting, an
    appliance type's for Bath."""
    from ..common import types_appliances
    row = item(key)
    if row is None:
        return None
    if row[2] == 'Lighting':
        from . import types_lighting
        return types_lighting.class_for(row[4])
    for cls in vars(types_appliances).values():
        if isinstance(cls, type) and getattr(cls, 'APPLIANCE_TYPE', None) == row[4]:
            return cls
    return None
