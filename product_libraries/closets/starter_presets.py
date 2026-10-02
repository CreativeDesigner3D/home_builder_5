"""Declarative closet starter catalog.

One entry per library item. The class name resolves through
types_closets.CLOSET_NAME_DISPATCH; per-type geometry defaults live as
class attributes on the starter classes (face_frame pattern). This module
stays import-light (no bpy) so the solver/types can be smoke-reloaded.
"""

# Library sections: (section label, [(catalog name, button label, desc)]).
# The library UI draws one collapsible-free header row per section.
STARTER_SECTIONS = [
    ("Closets", [
        ('Base', "Base", "Floor-mounted base closet starter"),
        ('Tall', "Tall", "Floor-mounted full-height closet starter"),
        ('Hanging', "Hanging", "Wall-mounted hanging closet starter"),
    ]),
    ("L Shelves", [
        ('L Shelf Base', "Base", "Floor-mounted corner L-shelf unit"),
        ('L Shelf Tall', "Tall", "Floor-mounted full-height corner L-shelf unit"),
        ('L Shelf Upper', "Hanging", "Wall-mounted corner L-shelf unit"),
    ]),
    ("Fillers", [
        ('Corner Filler', "Corner",
         "Closes the corner where two runs meet at a right angle"),
    ]),
    ("Islands", [
        ('Island', "Single", "Single-sided island with countertop and applied back"),
        ('Island Double', "Double", "Double-sided island with center back"),
    ]),
]

# Loose parts: dropped on their own rather than built into a run, so
# each entry names the operator that places it instead of resolving
# through the starter dispatch, and carries whatever that operator
# needs to be told. Same shape otherwise, so the library UI draws
# these rows exactly like the starter rows above them.
PART_SECTIONS = [
    ("Parts", [
        ('Misc Part', "Misc Part",
         "A part you size and place yourself",
         'hb_closets.place_misc_part', {'kind': 'MISC'}),
        ('Back', "Back",
         "A back panel. Dropped in an opening it closes it; "
         "anywhere else it stands on its own for a site fix",
         'hb_closets.place_misc_part', {'kind': 'BACK'}),
        ('Cleat', "Cleat",
         "A cleat. Dropped in an opening it spans it at the height "
         "it is dropped; anywhere else it fixes to a wall",
         'hb_closets.place_misc_part', {'kind': 'CLEAT'}),
        ('Shelf', "Shelf",
         "A shelf. Dropped in an opening it is cut to it and lands "
         "on the nearest system hole; anywhere else it stands alone",
         'hb_closets.place_misc_part', {'kind': 'SHELF'}),
        ('Countertop', "Countertop",
         "A countertop over some of a run's bays: hover a bay lower "
         "than its run and it covers that bay and its neighbours of "
         "the same height",
         'hb_closets.place_bay_countertop', {}),
        ('Slab Countertop', "Slab Top",
         "A 1 1/8 inch laminate countertop as a part of its own: hover "
         "a closet or a run of cabinets and it sits on it, or put it "
         "down anywhere",
         'hb_closets.place_slab_countertop', {}),
        # Fitted rather than dropped loose: these hover an opening,
        # preview at the cursor height and go on placing until you
        # stop. They were two buttons on the viewport overlay, which
        # was the one place in the product that made a part without
        # going through the library.
        ('Fixed Shelf', "Fixed Shelf",
         "A shelf fixed in an opening at the height it is dropped, "
         "landing on the nearest system hole",
         'hb_closets.add_part', {'part_type': 'FIXED_SHELF'}),
        ('Closet Rod', "Rod",
         "A hanging rod in an opening at the height it is dropped",
         'hb_closets.add_part', {'part_type': 'ROD'}),
    ]),
]

# Flat list retained for anything iterating the whole catalog
# (thumbnail checks etc.).
STARTER_MENU_ENTRIES = [entry for _sec, entries in STARTER_SECTIONS
                        for entry in entries]

# Bay-level override defaults, mirrored by Closet_Bay_Props. Kept as
# data so Change Bay-style mechanisms can reset overrides the same way
# face_frame's BAY_PROPS does.
BAY_PROP_DEFAULTS = {
    'unlock_width': False,
    'unlock_height': False,
    'unlock_depth': False,
    'remove_bottom': False,
    'remove_cleat': False,
    'remove_shelf_cleat': False,
}
