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
    # Drawer-look doors: one working door leaf shown as N stacked drawer
    # fronts (front_type DOOR + drawer_look_divisions). Single opening.
    'DOOR_LOOKS_2_DRAWER':     L('DOOR_LOOKS_2_DRAWER'),
    'DOOR_LOOKS_3_DRAWER':     L('DOOR_LOOKS_3_DRAWER'),
    'DOOR_LOOKS_4_DRAWER':     L('DOOR_LOOKS_4_DRAWER'),
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
    # Sink-style: false front (apron above the basin) over door(s). Top
    # zone size pinned to top_drawer_opening_height like the drawer
    # combos so the apron lines up with adjacent drawer fronts. The
    # door zone is the plumbing space under the basin -- no_shelves
    # strips the shelf that _update_front_type auto-seeds on doors.
    'FALSE_FRONT_DOOR':        H(L('FALSE_FRONT', size_role='TOP_DRAWER'),
                                 L('RIGHT_DOOR', no_shelves=True)),
    'FALSE_FRONT_DOUBLE_DOOR': H(L('FALSE_FRONT', size_role='TOP_DRAWER'),
                                 L('DOUBLE_DOOR', no_shelves=True)),
    # Vanity Special: false front apron over a door beside a stack of two
    # drawers. The apron pins to top_drawer_opening_height like the other
    # false-front presets.
    # The door is the plumbing zone (no_shelves) and always lands 4"
    # wider than the drawer stack beside it (VANITY_DOOR size role; the
    # redistribution rule lives in solver_face_frame._redistribute_sizes).
    'VANITY_SPECIAL':          H(L('FALSE_FRONT', size_role='TOP_DRAWER'),
                                 V(L('LEFT_DOOR', size_role='VANITY_DOOR',
                                     no_shelves=True),
                                   H(L('DRAWER'), L('DRAWER')))),
    # Vanity Combination: a top row of drawer / sink false front / drawer
    # over a double door. The false front pins to a fixed sink width
    # (VANITY_SINK_WIDTH); the flanking drawers absorb width changes. The
    # top row height pins to top_drawer_opening_height via the V node.
    'VANITY_COMBINATION':      H(V(L('DRAWER'),
                                   L('FALSE_FRONT', size_role='VANITY_SINK_WIDTH'),
                                   L('DRAWER'),
                                   size_role='TOP_DRAWER'),
                                 L('DOUBLE_DOOR', no_shelves=True)),
    # Vanity Deluxe: the Combination's drawer / sink false front / drawer
    # top row over a bottom row of a door beside a stack of two drawers.
    'VANITY_DELUXE':           H(V(L('DRAWER'),
                                   L('FALSE_FRONT', size_role='VANITY_SINK_WIDTH'),
                                   L('DRAWER'),
                                   size_role='TOP_DRAWER'),
                                 V(L('LEFT_DOOR', size_role='VANITY_DOOR',
                                     no_shelves=True),
                                   H(L('DRAWER'), L('DRAWER')))),
    'TWO_DRAWERS_DOUBLE_DOOR': H(V(L('DRAWER'), L('DRAWER'),
                                   size_role='TOP_DRAWER'),
                                 L('DOUBLE_DOOR')),
    'FOUR_DRAWERS':            H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('DRAWER'), L('DRAWER'), L('DRAWER')),
    # Dresser stacks - all rows EQUAL height (no TOP_DRAWER pin), so the
    # mid rails space evenly. BOTH split the TOP row into two side-by-side
    # drawers (V node): FIVE_DRAWERS has three single rows below it (five
    # fronts, four rows); SIX_DRAWERS has four single rows below (six
    # fronts, five rows).
    'FIVE_DRAWERS':            H(V(L('DRAWER'), L('DRAWER')),
                                 L('DRAWER'), L('DRAWER'), L('DRAWER')),
    'SIX_DRAWERS':             H(V(L('DRAWER'), L('DRAWER')),
                                 L('DRAWER'), L('DRAWER'), L('DRAWER'),
                                 L('DRAWER')),
    'THREE_DRAWERS':           H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('DRAWER'), L('DRAWER')),
    # Night stand: three EQUAL-height drawers (no TOP_DRAWER pin),
    # matching the furniture line's even spacing.
    'THREE_DRAWERS_EQUAL':     H(L('DRAWER'), L('DRAWER'), L('DRAWER')),
    'TWO_DRAWERS':             H(L('DRAWER'), L('DRAWER')),
    'ONE_DRAWER':              L('DRAWER'),
    'FALSE_FRONT':             L('FALSE_FRONT'),
    'PULLOUT':                 L('PULLOUT'),
    # Top drawer pins to top_drawer_opening_height (like the drawer+door
    # combos) so it lines up with adjacent drawer fronts instead of
    # splitting the bay evenly with the pullout below.
    'PULLOUT_WITH_DRAWER':     H(L('DRAWER', size_role='TOP_DRAWER'),
                                 L('PULLOUT')),
    'MICROWAVE_WITH_DRAWER':   H(L('APPLIANCE', accessory_label='MICROWAVE'),
                                 L('DRAWER')),
    'OPEN_WITH_SHELVES':       L('OPEN_WITH_SHELVES'),
    'OPEN':                    L('OPEN'),
    # Single opening filled by a recessed 1/4" inset panel (no overlay,
    # no swing). Default front for the Window Seat product.
    'INSET_PANEL':             L('INSET_PANEL'),
    # Lap drawer bay: a single drawer front in a bay floated to lap
    # height. The recipe is only the front; the floating construction
    # and 24" kick come from BAY_PROPS below.
    'LAP_DRAWER':              L('DRAWER'),
    # Support frame bay: an open, bottomless frame (e.g. counter support
    # over a knee space). Open front here; the removed bottom comes from
    # BAY_PROPS below.
    'SUPPORT_FRAME':           L('OPEN'),
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
                                      accessory_label='REFRIGERATOR')),
    'DOORS_WITH_TALL_PULLOUT':    H(L('DOUBLE_DOOR'), L('PULLOUT')),
    'TALL_PULLOUT':               L('PULLOUT'),
    'OPEN_WITH_SHELVES':          L('OPEN_WITH_SHELVES'),
    'OPEN':                       L('OPEN'),
    # Bookcase Storage Unit: open adjustable shelves on top over a double-
    # door storage base. The bottom doors pin to tall_cabinet_split_height
    # (TALL_SPLIT_BOTTOM) so the shelf zone above flexes with cabinet height.
    'BOOKCASE_STORAGE':           H(L('OPEN_WITH_SHELVES'),
                                    L('DOUBLE_DOOR', size_role='BOOKCASE_STORAGE_BOTTOM')),
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
# Bay-level construction props per config
# ---------------------------------------------------------------------------
# Most presets only describe the opening tree; a few also change how the
# bay itself is BUILT. BAY_PROPS[config] maps Face_Frame_Bay_Props names
# to values written after the tree is rebuilt.
#
# BAY_PROP_DEFAULTS lists the managed props with their stock values. The
# change_bay operator resets these on every preset swap
# (reset_bay_props=True) so switching a bay from Lap Drawer / Support
# Frame back to a normal layout restores standard construction.
# Placement-time preset application keeps reset_bay_props=False so
# cabinet classes that pre-set these flags on their bays (e.g. removed
# bottoms) are not undone.
BAY_PROP_DEFAULTS = {
    'floating_bay': False,
    'remove_bottom': False,
    # Re-locking kick height lets the recalc's kick-height distribution
    # re-sync the bay to the cabinet's toe_kick_height.
    'unlock_kick_height': False,
}

BAY_PROPS = {
    # Lap drawer bay: floats 24" off the floor. Writing kick_height
    # auto-locks unlock_kick_height via its update callback, so the
    # distribution pass leaves the 24" lift alone afterwards.
    'LAP_DRAWER': {
        'floating_bay': True,
        'kick_height': inch(24.0),
    },
    # Support frame bay: no bottom panel / bottom rail behind an open
    # front, and no toe kick - the frame runs to the floor. Writing
    # kick_height auto-locks unlock_kick_height (same as LAP_DRAWER)
    # so the distribution pass leaves the 0 alone; the reset on a swap
    # away unlocks it and re-syncs to the cabinet's toe_kick_height.
    'SUPPORT_FRAME': {
        'remove_bottom': True,
        'kick_height': 0.0,
    },
}

# Configs whose construction exposes the kick zone beside the bay (the
# bay floats or has no bottom). The change_bay apply drops the stiles
# flanking such a bay to the floor (mid stile to_floor / end stile
# extend_*_stile_to_floor) so they carry through the exposed zone, and
# clears them again on a swap back to a normal preset.
FLOOR_STILE_CONFIGS = {'LAP_DRAWER', 'SUPPORT_FRAME'}


# ---------------------------------------------------------------------------
# Menu rendering data: per cabinet type, the order and grouping of entries
# in the right-click "Change Bay" submenu. ('SEP',) inserts a separator;
# all other tuples are (config_id, display_label), with an optional
# trailing icon: (config_id, display_label, icon).
# ---------------------------------------------------------------------------
SEP = ('SEP',)

BASE_MENU_ENTRIES = [
    ('LEFT_SWING_DOOR',          "Left Swing Door"),
    ('RIGHT_SWING_DOOR',         "Right Swing Door"),
    ('DOUBLE_DOOR',              "Double Door"),
    ('DOOR_LOOKS_2_DRAWER',      "Door - Looks like 2 Drawers"),
    ('DOOR_LOOKS_3_DRAWER',      "Door - Looks like 3 Drawers"),
    ('DOOR_LOOKS_4_DRAWER',      "Door - Looks like 4 Drawers"),
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
    ('FALSE_FRONT_DOOR',         "False Front 1 Door"),
    ('FALSE_FRONT_DOUBLE_DOOR',  "False Front 2 Door"),
    SEP,
    ('PULLOUT',                  "Pullout"),
    ('PULLOUT_WITH_DRAWER',      "Pullout with Drawer"),
    ('MICROWAVE_WITH_DRAWER',    "Microwave with Drawer"),
    SEP,
    ('OPEN_WITH_SHELVES',        "Open with Shelves"),
    ('OPEN',                     "Open"),
    SEP,
    ('LAP_DRAWER',               "Lap Drawer"),
    ('SUPPORT_FRAME',            "Support Frame"),
    SEP,
    ('CUSTOM_HORIZONTAL', "Custom Horizontal", 'SNAP_EDGE'),
    ('CUSTOM_VERTICAL',   "Custom Vertical",   'PAUSE'),
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
    ('CUSTOM_HORIZONTAL', "Custom Horizontal", 'SNAP_EDGE'),
    ('CUSTOM_VERTICAL',   "Custom Vertical",   'PAUSE'),
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
    ('CUSTOM_HORIZONTAL', "Custom Horizontal", 'SNAP_EDGE'),
    ('CUSTOM_VERTICAL',   "Custom Vertical",   'PAUSE'),
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
    if cabinet_name == 'Hutch Upper':
        # Hutch upper: a standard upper front (width-based door); the
        # dropped ends come from the cabinet class, not the bay preset.
        return 'DOUBLE_DOOR' if is_wide else 'LEFT_SWING_DOOR'
    if cabinet_name == 'Standard Recessed Medicine Cabinet':
        # Medicine cabinet: a single door at the narrow default width
        # (width-based so it still doubles up if widened).
        return 'DOUBLE_DOOR' if is_wide else 'LEFT_SWING_DOOR'
    if cabinet_name == 'Tri-View Medicine Cabinet':
        # Single full-width DOOR opening; the three mirror doors come from
        # the HB_TRIVIEW_DOORS flag in solver.front_leaves, not the preset.
        return 'LEFT_SWING_DOOR'
    if cabinet_name == 'Medicine Cabinet':
        # Surface-mounted medicine cabinet: standard upper front
        # (width-based door).
        return 'DOUBLE_DOOR' if is_wide else 'LEFT_SWING_DOOR'
    if cabinet_name == 'Overstool Cabinet':
        # Over-stool cabinet: standard upper front (width-based door);
        # the extended legs come from the cabinet class, not the bay.
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
    if cabinet_name == 'Built in Tall':
        # Tall cabinet with a built-in appliance opening: doors above and
        # below an open APPLIANCE zone. Same recipe as the Change Bay
        # menu's "Built In Appliance" option.
        return 'BUILT_IN_APPLIANCE'
    if cabinet_name == 'Sink':
        return 'FALSE_FRONT_DOUBLE_DOOR' if is_wide else 'FALSE_FRONT_DOOR'
    if cabinet_name == 'Special':
        # Vanity "Special": a standard base cabinet with the VANITY_SPECIAL
        # bay configuration.
        return 'VANITY_SPECIAL'
    if cabinet_name == 'Combination':
        # Vanity "Combination": a standard base cabinet with the
        # VANITY_COMBINATION bay configuration.
        return 'VANITY_COMBINATION'
    if cabinet_name == 'Deluxe':
        # Vanity "Deluxe": a standard base cabinet with the VANITY_DELUXE
        # bay configuration.
        return 'VANITY_DELUXE'
    if cabinet_name == 'Bookcase':
        # Bookcase: a 12" deep tall cabinet with a single open bay of
        # adjustable shelves.
        return 'OPEN_WITH_SHELVES'
    if cabinet_name == 'Bookcase Storage Unit':
        # Bookcase with a storage base: open shelves on top, double doors
        # (pinned to the standard lower height) below.
        return 'BOOKCASE_STORAGE'
    if cabinet_name == 'Bookcase Upper':
        # Open-shelf upper bookcase: a single open bay of adjustable shelves
        # (bottom panel removed per the cabinet class).
        return 'OPEN_WITH_SHELVES'
    if cabinet_name == '5 Drawer Dresser':
        # Dresser: split top row (two drawers) over three single equal
        # drawers - five fronts.
        return 'FIVE_DRAWERS'
    if cabinet_name == '6 Drawer Dresser':
        # Dresser: five equal rows, the top row split into two
        # side-by-side drawers (six fronts).
        return 'SIX_DRAWERS'
    if cabinet_name == 'Night Stand':
        # Furniture night stand: double doors by default.
        return 'DOUBLE_DOOR'
    if cabinet_name == '3 Drawer Night Stand':
        # Furniture night stand: a single column of three equal drawers.
        return 'THREE_DRAWERS_EQUAL'
    if cabinet_name == 'Window Seat':
        # Window seat: each bay opening gets a recessed inset panel by
        # default (flush-kick base; see WindowSeatFaceFrameCabinet).
        return 'INSET_PANEL'
    return None
