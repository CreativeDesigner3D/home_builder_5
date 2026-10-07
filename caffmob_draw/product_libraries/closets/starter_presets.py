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
    ("Islands", [
        ('Island', "Single", "Single-sided island with countertop and applied back"),
        ('Island Double', "Double", "Double-sided island with center back"),
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
    'width_locked': False,
    'remove_bottom': False,
    'remove_cleat': False,
}
