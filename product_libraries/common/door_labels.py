"""Shared display names for door configurations.

Every library's menus, enum items and cards take their door wording from
here so the same configuration reads the same in every menu. These are
display labels only: enum identifiers, config ids and stored property
keys never change, so saved files keep their meaning.

Vocabulary:
- a single door is named by its hinge side: "Left Swing Door"
- a pair meeting in the middle is "Double Doors"
- counts are plural where more than one: "1 Drawer 2 Doors"
- a door hinged on its top edge is a "Lift-up Door"; its stay hardware
  is picked separately (Lift-up, Deluxe Lift-up, Deluxe Bi-fold Lift-up)
"""

# Single doors and pairs
LEFT_SWING = "Left Swing Door"
RIGHT_SWING = "Right Swing Door"
DOUBLE = "Double Doors"

# Top-hinged door, and the stay hardware it can carry
LIFT_UP = "Lift-up Door"
LIFT_UP_HW = "Lift-up"
LIFT_UP_DELUXE_HW = "Deluxe Lift-up"
LIFT_UP_BIFOLD_HW = "Deluxe Bi-fold Lift-up"

# Stacked doors (two high)
LEFT_STACKED = "Left Swing Stacked Door"
RIGHT_STACKED = "Right Swing Stacked Door"
DOUBLE_STACKED = "Double Stacked Doors"

# Stacked doors (three high)
LEFT_3_STACKED = "Left Swing 3 Stacked Door"
RIGHT_3_STACKED = "Right Swing 3 Stacked Door"
DOUBLE_3_STACKED = "Double 3 Stacked Doors"

# Pairs built from battened doors
DOUBLE_2_HIGH = "Double Doors - 2 Doors High"
DOUBLE_3_HIGH = "Double Doors - 3 Doors High"

# Bi-fold pairs, named by the hinge side
BIFOLD_LEFT = "Bi-fold Left Swing"
BIFOLD_RIGHT = "Bi-fold Right Swing"

# Retracting pair
RETRACTING_DOUBLE = "Retracting Double Doors"

# Drawer / door combinations
DRAWER_1_DOOR = "1 Drawer 1 Door"
DRAWER_2_DOORS = "1 Drawer 2 Doors"
TWO_DRAWERS_2_DOORS = "2 Drawers 2 Doors"
FALSE_FRONT_1_DOOR = "False Front 1 Door"
FALSE_FRONT_2_DOORS = "False Front 2 Doors"
DOORS_WITH_1_DRAWER = "Doors with 1 Drawer"
DOORS_WITH_2_DRAWERS = "Doors with 2 Drawers"
DOORS_WITH_3_DRAWERS = "Doors with 3 Drawers"
