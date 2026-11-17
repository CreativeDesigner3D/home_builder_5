"""What a frameless bay is built as, read against the Change Configuration
presets, and a pick of another.

A bay's fronts are read top to bottom, one token each: a door by its
swing (D0 left, D1 right, D2 double), a lift up door, a drawer, a false
front, a pullout, an appliance opening, an open opening with shelves.
Each preset is the stack of tokens Change Configuration builds; the
first preset of the cabinet's list that matches names the bay, and a
bay changed since (an opening split, a front swapped) reads as Custom.
"""

import bpy

CUSTOM = 'CUSTOM'

# The presets the right-click Change Configuration menu offers, by
# cabinet type, in its order.
PRESETS = {
    'BASE': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('DOOR_DRAWER', "1 Drawer 1 Door"),
        ('1_DRAWER_2_DOOR', "1 Drawer 2 Door"),
        ('2_DRAWER_2_DOOR', "2 Drawer 2 Door"),
        ('4_DRAWER_STACK', "4 Drawers"),
        ('3_DRAWER_STACK', "3 Drawers"),
        ('2_DRAWER_STACK', "2 Drawers"),
        ('SINGLE_DRAWER', "1 Drawer"),
        ('FALSE_FRONT', "False Front"),
        ('PULLOUT', "Pullout"),
        ('PULLOUT_WITH_DRAWER', "Pullout with Drawer"),
        ('MICROWAVE_DRAWER', "Microwave with Drawer"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
    'UPPER': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('FLIP_UP_DOOR', "Lift Up Door"),
        ('LEFT_STACKED_DOOR', "Left Swing Stacked Door"),
        ('RIGHT_STACKED_DOOR', "Right Swing Stacked Door"),
        ('DOUBLE_STACKED_DOOR', "Double Stacked Door"),
        ('DOORS_WITH_1_DRAWER', "Doors with 1 Drawer"),
        ('DOORS_WITH_2_DRAWER', "Doors with 2 Drawers"),
        ('DOORS_WITH_3_DRAWER', "Doors with 3 Drawers"),
        ('DOORS_WITH_PULLOUT', "Doors with Pullout"),
        ('PULLOUT', "Pullout"),
        ('FALSE_FRONT', "False Front"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
    'TALL': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('LEFT_STACKED_DOOR', "Left Swing Stacked Door"),
        ('RIGHT_STACKED_DOOR', "Right Swing Stacked Door"),
        ('DOUBLE_STACKED_DOOR', "Double Stacked Door"),
        ('LEFT_3_STACKED_DOOR', "Left Swing 3 Stacked Door"),
        ('RIGHT_3_STACKED_DOOR', "Right Swing 3 Stacked Door"),
        ('DOUBLE_3_STACKED_DOOR', "Double 3 Stacked Door"),
        ('APPLIANCE', "Built In Appliance"),
        ('DOUBLE_APPLIANCE', "Built In Double Appliance"),
        ('DOORS_WITH_TALL_PULLOUT', "Doors with Tall Pullout"),
        ('TALL_PULLOUT', "Tall Pullout"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
}

# The fronts each preset builds, top to bottom.
SIGNATURES = {
    'LEFT_DOOR': ('D0',),
    'RIGHT_DOOR': ('D1',),
    'DOUBLE_DOORS': ('D2',),
    'FLIP_UP_DOOR': ('LIFT',),
    'LEFT_STACKED_DOOR': ('D0', 'D0'),
    'RIGHT_STACKED_DOOR': ('D1', 'D1'),
    'DOUBLE_STACKED_DOOR': ('D2', 'D2'),
    'LEFT_3_STACKED_DOOR': ('D0', 'D0', 'D0'),
    'RIGHT_3_STACKED_DOOR': ('D1', 'D1', 'D1'),
    'DOUBLE_3_STACKED_DOOR': ('D2', 'D2', 'D2'),
    'DOOR_DRAWER': ('DRAWER', 'D0'),
    '1_DRAWER_2_DOOR': ('DRAWER', 'D2'),
    '2_DRAWER_2_DOOR': ('DRAWER', 'DRAWER', 'D2'),
    'SINGLE_DRAWER': ('DRAWER',),
    '2_DRAWER_STACK': ('DRAWER',) * 2,
    '3_DRAWER_STACK': ('DRAWER',) * 3,
    '4_DRAWER_STACK': ('DRAWER',) * 4,
    'PULLOUT': ('PULLOUT',),
    'TALL_PULLOUT': ('PULLOUT',),
    'PULLOUT_WITH_DRAWER': ('DRAWER', 'PULLOUT'),
    'DOORS_WITH_TALL_PULLOUT': ('D2', 'PULLOUT'),
    'DOORS_WITH_PULLOUT': ('D2', 'PULLOUT'),
    'DOORS_WITH_1_DRAWER': ('D2', 'DRAWER'),
    'DOORS_WITH_2_DRAWER': ('D2', 'DRAWER', 'DRAWER'),
    'DOORS_WITH_3_DRAWER': ('D2', 'DRAWER', 'DRAWER', 'DRAWER'),
    'FALSE_FRONT': ('FALSE_FRONT',),
    'MICROWAVE_DRAWER': ('APPLIANCE', 'DRAWER'),
    'APPLIANCE': ('D2', 'APPLIANCE', 'D2'),
    'DOUBLE_APPLIANCE': ('D2', 'APPLIANCE', 'APPLIANCE', 'DRAWER'),
    'OPEN_WITH_SHELVES': ('SHELVES',),
    'OPEN': (),
}


def cabinet_kind(bay_obj):
    """The preset list a bay takes: its cabinet's type, base otherwise."""
    from ... import hb_utils
    root = hb_utils.get_cabinet_bp(bay_obj)
    kind = root.get('CABINET_TYPE', 'BASE') if root is not None else 'BASE'
    return kind if kind in PRESETS else 'BASE'


def _leaf_openings(bay_obj):
    leaves = [o for o in bay_obj.children_recursive
              if o.get('IS_FRAMELESS_OPENING_CAGE')
              and not any(c.get('IS_FRAMELESS_OPENING_CAGE')
                          for c in o.children_recursive)]
    leaves.sort(key=lambda o: -o.matrix_world.translation.z)
    return leaves


def _token(opening):
    children = list(opening.children)
    if any(c.get('IS_FLIP_UP_DOOR') for c in children):
        return 'LIFT'
    if 'Door Swing' in opening:
        try:
            return 'D%d' % int(opening['Door Swing'])
        except (TypeError, ValueError):
            return 'D?'
    if any(c.get('IS_PULLOUT_FRONT') for c in children):
        return 'PULLOUT'
    if any(c.get('IS_DRAWER_FRONT') for c in children):
        if any(c.get('IS_DRAWER_FRONT') and c.get('False Front')
               for c in children):
            return 'FALSE_FRONT'
        return 'DRAWER'
    if any(c.get('IS_APPLIANCE_TEXT') for c in children):
        return 'APPLIANCE'
    if 'Shelf Quantity' in opening:
        return 'SHELVES'
    return 'OTHER'


def signature(bay_obj):
    return tuple(_token(o) for o in _leaf_openings(bay_obj))


def detect(bay_obj):
    """The preset the bay is built as, or CUSTOM."""
    sig = signature(bay_obj)
    for key, _label in PRESETS[cabinet_kind(bay_obj)]:
        if SIGNATURES.get(key) == sig:
            return key
    return CUSTOM


def items(kind):
    return list(PRESETS[kind]) + [(CUSTOM, "Custom")]


def apply(bay_obj, key):
    """Rebuild the bay as the preset ``key``, as Change Configuration
    does."""
    if key == CUSTOM or key not in SIGNATURES:
        return
    with bpy.context.temp_override(active_object=bay_obj, object=bay_obj,
                                   selected_objects=[bay_obj]):
        bpy.ops.hb_frameless.change_bay_opening(opening_type=key)


# ---- The page's field ---------------------------------------------------------

SCHEMA_PREFIX = 'FL_BAY_'


def schema_key(bay_obj):
    return SCHEMA_PREFIX + cabinet_kind(bay_obj)


def _config(kind):
    from ...operators import prop_proxy

    def get(obj):
        return detect(obj)

    def set(obj, value):
        if value != detect(obj):
            apply(obj, value)
    return prop_proxy.computed(get, set, type='ENUM', items=items(kind))


def register_schemas():
    from ...operators import prop_proxy
    for kind in PRESETS:
        prop_proxy.register(SCHEMA_PREFIX + kind, {'config': _config(kind)})


def unregister_schemas():
    from ...operators import prop_proxy
    for kind in PRESETS:
        prop_proxy.unregister(SCHEMA_PREFIX + kind)
