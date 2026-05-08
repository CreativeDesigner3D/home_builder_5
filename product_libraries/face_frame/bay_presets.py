"""Bay configuration presets for the face frame library.

Each preset describes how to populate a bay: a tree of split nodes and
opening leaves, where each leaf carries an opening preset name (the same
strings the change_opening operator accepts) plus optional per-leaf
overrides.

Tree shape:
    leaf:  ('leaf', config_str, overrides_dict)
    split: ('split', axis, [child, child, ...])      # axis = 'H' or 'V'

The H-split / V-split convention matches split_opening: H children are
stacked top -> bottom (child[0] is top, child[-1] is bottom); V children
run left -> right (child[0] is left, child[-1] is right).

PRESETS is keyed by cabinet_type. The change_bay operator reads
PRESETS[cabinet_type][config] to find the recipe.

MENU_ENTRIES drives the right-click submenu order and grouping per
cabinet type. ('SEP',) marks a horizontal separator. The special
configs CUSTOM_VERTICAL and CUSTOM_HORIZONTAL are not in PRESETS - the
operator wipes the bay to one opening and routes to the existing
split_opening dialog.
"""

from ...units import inch


# Recipe tuples carry a trailing `size_role` slot. The size_role tells
# the bay builder to look up a cabinet-level size preference and pin
# that node's size + unlock_size. Currently only 'TOP_DRAWER' is
# defined; it resolves to a scene-level size preference.
def L(config, size_role=None, **overrides):
    """Leaf node: one opening with the given change_opening preset and
    optional overrides such as accessory_label='Microwave'. size_role
    is one of: None, 'TOP_DRAWER'.
    """
    return ('leaf', config, overrides, size_role)


def H(*children, size_role=None):
    """Horizontal split: children stacked vertically (mid rails between)."""
    return ('split', 'H', list(children), size_role)


def V(*children, size_role=None):
    """Vertical split: children side by side (mid stiles between)."""
    return ('split', 'V', list(children), size_role)


# ---------------------------------------------------------------------------
# BASE cabinet presets
# ---------------------------------------------------------------------------
# Door+drawer combos use a fixed RIGHT_DOOR hinge for any single-door zone;
# DOUBLE_DOOR is used wherever the menu name says "2 Door" / "Doors".
BASE_PRESETS = {
    'LEFT_SWING_DOOR':         L('LEFT_DOOR'),
    'RIGHT_SWING_DOOR':        L('RIGHT_DOOR'),
    'DOUBLE_DOOR':             L('DOUBLE_DOOR'),
    # Top zone in drawer+door combos pins to top_drawer_opening_height. For
    # 2 Drawer 2 Door the V split (containing two side-by-side drawers)
    # is the top zone, so the role goes on the V node.
    'DRAWER_DOOR':             H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('RIGHT_DOOR')),
    'DRAWER_DOUBLE_DOOR':      H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('DOUBLE_DOOR')),
    'TWO_DRAWERS_DOUBLE_DOOR': H(V(L('DRAWER'), L('DRAWER'),
                                   size_role='TOP_DRAWER'),
                                 L('DOUBLE_DOOR')),
    'FOUR_DRAWERS':            H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('DRAWER'), L('DRAWER'), L('DRAWER')),
    'THREE_DRAWERS':           H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('DRAWER'), L('DRAWER')),
    'TWO_DRAWERS':             H(L('DRAWER'), L('DRAWER')),
    'ONE_DRAWER':              L('DRAWER'),
    'FALSE_FRONT':             L('FALSE_FRONT'),
    'PULLOUT':                 L('PULLOUT'),
    'PULLOUT_WITH_DRAWER':     H(L('DRAWER'), L('PULLOUT')),
    'MICROWAVE_WITH_DRAWER':   H(L('APPLIANCE', accessory_label='Microwave'),
                                 L('DRAWER')),
    'OPEN_WITH_SHELVES':       L('OPEN_WITH_SHELVES'),
    'OPEN':                    L('OPEN'),
}


# ---------------------------------------------------------------------------
# TALL cabinet presets
# ---------------------------------------------------------------------------
# "Stacked" = one door style repeated in each H-zone. "Built In Appliance"
# packs the appliance label between two banks of double doors (top & bottom);
# "Built In Double Appliance" stacks doors / appliance / appliance / drawer.
TALL_PRESETS = {
    'LEFT_SWING_DOOR':            L('LEFT_DOOR'),
    'RIGHT_SWING_DOOR':           L('RIGHT_DOOR'),
    'DOUBLE_DOOR':                L('DOUBLE_DOOR'),
    # Stacked door presets pin the BOTTOM leaf to tall_cabinet_split_height
    # so the upper section flexes with the cabinet's overall height.
    'LEFT_STACKED_DOOR':          H(L('LEFT_DOOR'),
                                    L('LEFT_DOOR', size_role='TALL_SPLIT_BOTTOM')),
    'RIGHT_STACKED_DOOR':         H(L('RIGHT_DOOR'),
                                    L('RIGHT_DOOR', size_role='TALL_SPLIT_BOTTOM')),
    'DOUBLE_STACKED_DOOR':        H(L('DOUBLE_DOOR'),
                                    L('DOUBLE_DOOR', size_role='TALL_SPLIT_BOTTOM')),
    'LEFT_3_STACKED_DOOR':        H(L('LEFT_DOOR'), L('LEFT_DOOR'), L('LEFT_DOOR')),
    'RIGHT_3_STACKED_DOOR':       H(L('RIGHT_DOOR'), L('RIGHT_DOOR'), L('RIGHT_DOOR')),
    'DOUBLE_3_STACKED_DOOR':      H(L('DOUBLE_DOOR'), L('DOUBLE_DOOR'), L('DOUBLE_DOOR')),
    'BUILT_IN_APPLIANCE':         H(L('DOUBLE_DOOR'), L('APPLIANCE'), L('DOUBLE_DOOR')),
    'BUILT_IN_DOUBLE_APPLIANCE':  H(L('DOUBLE_DOOR'), L('APPLIANCE'),
                                    L('APPLIANCE'), L('DRAWER')),
    # Refrigerator cabinet: doors above, refrigerator zone below pinned
    # to refrigerator_height so the door zone flexes with cabinet height.
    'BUILT_IN_REFRIGERATOR':      H(L('DOUBLE_DOOR'),
                                    L('APPLIANCE', size_role='REFRIGERATOR',
                                      accessory_label='Refrigerator')),
    'DOORS_WITH_TALL_PULLOUT':    H(L('DOUBLE_DOOR'), L('PULLOUT')),
    'TALL_PULLOUT':               L('PULLOUT'),
    'OPEN_WITH_SHELVES':          L('OPEN_WITH_SHELVES'),
    'OPEN':                       L('OPEN'),
}


# ---------------------------------------------------------------------------
# UPPER cabinet presets
# ---------------------------------------------------------------------------
# Lift Up Door uses front_type=DOOR with hinge=TOP (the FLIP_UP_DOOR opening
# preset). Doors-with-N-drawers stacks DOUBLE_DOOR on top with N drawers
# below.
UPPER_PRESETS = {
    'LEFT_SWING_DOOR':         L('LEFT_DOOR'),
    'RIGHT_SWING_DOOR':        L('RIGHT_DOOR'),
    'DOUBLE_DOOR':             L('DOUBLE_DOOR'),
    'LIFT_UP_DOOR':            L('FLIP_UP_DOOR'),
    # Stacked door presets pin the TOP leaf to upper_top_stacked_cabinet_height
    # so the lower section flexes with the cabinet's overall height.
    'LEFT_STACKED_DOOR':       H(L('LEFT_DOOR', size_role='UPPER_STACKED_TOP'),
                                 L('LEFT_DOOR')),
    'RIGHT_STACKED_DOOR':      H(L('RIGHT_DOOR', size_role='UPPER_STACKED_TOP'),
                                 L('RIGHT_DOOR')),
    'DOUBLE_STACKED_DOOR':     H(L('DOUBLE_DOOR', size_role='UPPER_STACKED_TOP'),
                                 L('DOUBLE_DOOR')),
    'DOORS_WITH_DRAWER':       H(L('DOUBLE_DOOR'), L('DRAWER')),
    'DOORS_WITH_2_DRAWERS':    H(L('DOUBLE_DOOR'), L('DRAWER'), L('DRAWER')),
    'DOORS_WITH_3_DRAWERS':    H(L('DOUBLE_DOOR'), L('DRAWER'), L('DRAWER'), L('DRAWER')),
    'DOORS_WITH_UPPER_PULLOUT': H(L('DOUBLE_DOOR'), L('PULLOUT')),
    'UPPER_PULLOUT':           L('PULLOUT'),
    'FALSE_FRONT':             L('FALSE_FRONT'),
    'OPEN_WITH_SHELVES':       L('OPEN_WITH_SHELVES'),
    'OPEN':                    L('OPEN'),
}


PRESETS = {
    'BASE': BASE_PRESETS,
    'TALL': TALL_PRESETS,
    'UPPER': UPPER_PRESETS,
}


# ---------------------------------------------------------------------------
# Menu rendering data: per cabinet type, the order and grouping of entries
# in the right-click "Change Bay" submenu. ('SEP',) inserts a separator;
# all other tuples are (config_id, display_label).
# ---------------------------------------------------------------------------
SEP = ('SEP',)

BASE_MENU_ENTRIES = [
    ('LEFT_SWING_DOOR',          "Left Swing Door"),
    ('RIGHT_SWING_DOOR',         "Right Swing Door"),
    ('DOUBLE_DOOR',              "Double Door"),
    SEP,
    ('DRAWER_DOOR',              "1 Drawer 1 Door"),
    ('DRAWER_DOUBLE_DOOR',       "1 Drawer 2 Door"),
    ('TWO_DRAWERS_DOUBLE_DOOR',  "2 Drawer 2 Door"),
    SEP,
    ('FOUR_DRAWERS',             "4 Drawers"),
    ('THREE_DRAWERS',            "3 Drawers"),
    ('TWO_DRAWERS',              "2 Drawers"),
    ('ONE_DRAWER',               "1 Drawer"),
    ('FALSE_FRONT',              "False Front"),
    SEP,
    ('PULLOUT',                  "Pullout"),
    ('PULLOUT_WITH_DRAWER',      "Pullout with Drawer"),
    ('MICROWAVE_WITH_DRAWER',    "Microwave with Drawer"),
    SEP,
    ('OPEN_WITH_SHELVES',        "Open with Shelves"),
    ('OPEN',                     "Open"),
    SEP,
    ('CUSTOM_VERTICAL',          "Custom Vertical"),
    ('CUSTOM_HORIZONTAL',        "Custom Horizontal"),
]

TALL_MENU_ENTRIES = [
    ('LEFT_SWING_DOOR',           "Left Swing Door"),
    ('RIGHT_SWING_DOOR',          "Right Swing Door"),
    ('DOUBLE_DOOR',               "Double Door"),
    SEP,
    ('LEFT_STACKED_DOOR',         "Left Swing Stacked Door"),
    ('RIGHT_STACKED_DOOR',        "Right Swing Stacked Door"),
    ('DOUBLE_STACKED_DOOR',       "Double Stacked Door"),
    SEP,
    ('LEFT_3_STACKED_DOOR',       "Left Swing 3 Stacked Door"),
    ('RIGHT_3_STACKED_DOOR',      "Right Swing 3 Stacked Door"),
    ('DOUBLE_3_STACKED_DOOR',     "Double 3 Stacked Door"),
    SEP,
    ('BUILT_IN_APPLIANCE',        "Built In Appliance"),
    ('BUILT_IN_DOUBLE_APPLIANCE', "Built In Double Appliance"),
    SEP,
    ('DOORS_WITH_TALL_PULLOUT',   "Doors with Tall Pullout"),
    ('TALL_PULLOUT',              "Tall Pullout"),
    SEP,
    ('OPEN_WITH_SHELVES',         "Open with Shelves"),
    ('OPEN',                      "Open"),
    SEP,
    ('CUSTOM_VERTICAL',           "Custom Vertical"),
    ('CUSTOM_HORIZONTAL',         "Custom Horizontal"),
]

UPPER_MENU_ENTRIES = [
    ('LEFT_SWING_DOOR',           "Left Swing Door"),
    ('RIGHT_SWING_DOOR',          "Right Swing Door"),
    ('DOUBLE_DOOR',               "Double Door"),
    ('LIFT_UP_DOOR',              "Lift Up Door"),
    SEP,
    ('LEFT_STACKED_DOOR',         "Left Swing Stacked Door"),
    ('RIGHT_STACKED_DOOR',        "Right Swing Stacked Door"),
    ('DOUBLE_STACKED_DOOR',       "Double Stacked Door"),
    SEP,
    ('DOORS_WITH_DRAWER',         "Doors with Drawer"),
    ('DOORS_WITH_2_DRAWERS',      "Doors with 2 Drawers"),
    ('DOORS_WITH_3_DRAWERS',      "Doors with 3 Drawers"),
    SEP,
    ('DOORS_WITH_UPPER_PULLOUT',  "Doors with Upper Pullout"),
    ('UPPER_PULLOUT',             "Upper Pullout"),
    SEP,
    ('FALSE_FRONT',               "False Front"),
    SEP,
    ('OPEN_WITH_SHELVES',         "Open with Shelves"),
    ('OPEN',                      "Open"),
    SEP,
    ('CUSTOM_VERTICAL',           "Custom Vertical"),
    ('CUSTOM_HORIZONTAL',         "Custom Horizontal"),
]


MENU_ENTRIES = {
    'BASE': BASE_MENU_ENTRIES,
    'TALL': TALL_MENU_ENTRIES,
    'UPPER': UPPER_MENU_ENTRIES,
}



# ---------------------------------------------------------------------------
# Default bay configuration on cabinet placement
# ---------------------------------------------------------------------------
DOUBLE_DOOR_WIDTH_THRESHOLD = inch(18.0)


def default_bay_config(cabinet_name, bay_width):
    """Return the bay preset id to apply when a fresh cabinet is dropped,
    or None if the cabinet has no automatic default (e.g., LAP_DRAWER).
    Width-based picks use DOUBLE_DOOR_WIDTH_THRESHOLD; below it use the
    single-door variant, at or above it use the double / stacked variant.
    """
    is_wide = bay_width >= DOUBLE_DOOR_WIDTH_THRESHOLD
    if cabinet_name in ('Base', 'Base Cabinet', 'Floating Base Cabinet'):
        # Generic Base cabinet defaults to drawer-on-top-of-door, the
        # most common base configuration in residential kitchens. The
        # floating variant uses the same recipe; only its toe kick
        # construction differs from a standard base.
        return 'DRAWER_DOUBLE_DOOR' if is_wide else 'DRAWER_DOOR'
    if cabinet_name == 'Base Door':
        return 'DOUBLE_DOOR' if is_wide else 'LEFT_SWING_DOOR'
    if cabinet_name == 'Base Door Drw':
        return 'DRAWER_DOUBLE_DOOR' if is_wide else 'DRAWER_DOOR'
    if cabinet_name == 'Base Drawer':
        return 'THREE_DRAWERS'
    if cabinet_name == 'Lap Drawer':
        return 'ONE_DRAWER'
    if cabinet_name == 'Upper':
        return 'DOUBLE_DOOR' if is_wide else 'LEFT_SWING_DOOR'
    if cabinet_name == 'Upper Stacked':
        return 'DOUBLE_STACKED_DOOR' if is_wide else 'LEFT_STACKED_DOOR'
    if cabinet_name in ('Tall', 'Tall Stacked'):
        # Stacked-door default; the bottom leaf carries size_role
        # 'TALL_SPLIT_BOTTOM' so apply_bay_preset pins it to
        # tall_cabinet_split_height and the top section flexes with
        # the cabinet's overall height.
        return 'DOUBLE_STACKED_DOOR' if is_wide else 'LEFT_STACKED_DOOR'
    if cabinet_name == 'Refrigerator Cabinet':
        return 'BUILT_IN_REFRIGERATOR'
    return None
