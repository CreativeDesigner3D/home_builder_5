"""The frameless product library, as data.

Every product used to live inline in the sidebar's ``draw_*_library_ui``
methods, so the list existed only as a side effect of drawing it and
nothing else could ask what the library contains. The viewport browser
needs to ask -- to search it, to filter it, to lay it out as a grid --
so the products live here and the sidebar renders FROM this.

Shape
-----
``SECTIONS`` is the display order: each section has a ``key``, a
``label``, the sidebar's fold-open property, and ``rows`` of
``(row_label, ((display, cabinet_name, thumbnail), ...))``.

A row label captions a group inside a section ("Base Cabinets" against
"Upper & Tall Cabinets"); an empty one means the products just follow
the section heading.

Unlike the face frame library, a product's THUMBNAIL name is not always
its cabinet name -- "Base Drawer" is drawn from Base Drw.png, and the
three legs share one picture -- so the two are carried separately and
``thumbnail_path`` resolves one from the other.

This module fulfils the contract in
``operators/library_panel.register_catalog``: SECTIONS, section_by_key,
category_items, search_products, thumbnail_path, place(), and the
optional SIZES_FORM / AUTO_JOIN header controls.
"""

import os

import bpy

SECTIONS = (
    {
        'key': 'cabinets',
        'label': "Cabinets",
        'prop': 'show_cabinet_library',
        'rows': (
            ("Base", (("Door", "Base Door", "Base Door"),
                      ("Door Drw", "Base Door Drw", "Base Door Drw"),
                      ("Drawer", "Base Drawer", "Base Drw"),
                      ("Lap Drawer", "Lap Drawer", "Lap Drw"),
                      ("Sink", "Sink Base", "Sink Cabinet"),
                      ("Open", "Base Open", "Base Open"))),
            ("Upper & Tall", (("Upper", "Upper", "Upper"),
                              ("Upper Stacked", "Upper Stacked",
                               "Upper Stacked"),
                              ("Upper Open", "Upper Open", "Upper Open"),
                              ("Tall", "Tall", "Tall"),
                              ("Tall Stacked", "Tall Stacked",
                               "Tall Stacked"),
                              ("Tall Open", "Tall Open", "Tall Open"))),
        ),
    },
    {
        'key': 'corner',
        'label': "Corner Cabinets",
        'prop': 'show_corner_cabinet_library',
        'rows': (
            ("Pie Cut", (("Base", "Pie Cut Corner Base",
                          "Frameless Base Corner"),
                         ("Tall", "Pie Cut Corner Tall",
                          "Frameless Tall Corner"),
                         ("Upper", "Pie Cut Corner Upper",
                          "Frameless Upper Corner"))),
            # Placed like a plain cabinet (their key carries no 'Corner',
            # which is what the placement tool snaps corner products on).
            ("Blind", (("Base", "Blind Base", "Blind Base"),
                       ("Tall", "Blind Tall", "Blind Tall"),
                       ("Upper", "Blind Upper", "Blind Upper"))),
        ),
    },
    {
        'key': 'appliance',
        'label': "Appliances",
        'prop': 'show_appliance_library',
        'toggle': ("Show Model", 'home_builder', 'show_appliance_models'),
        'rows': (
            ("", (("Fridge Cabinet", "Refrigerator Cabinet",
                   "Refrigerator Frameless Cabinet"),
                  ("Oven Tower", "Tall Oven", "Tall Oven"),
                  ("Double Oven", "Tall Double Oven", "Tall Double Oven"),
                  ("Oven Micro", "Tall Oven Microwave", "Tall Oven Microwave"),
                  ("Dishwasher", "Dishwasher", "Dishwasher"),
                  ("Under Counter", "Under Counter Appliance",
                   "Under Counter Appliance"),
                  ("Refrigerator", "Refrigerator", "Refrigerator"),
                  ("Range", "Range", "Range"),
                  ("Range Hood", "Range Hood", "Range Hood"))),
        ),
    },
    {
        'key': 'parts',
        'label': "Parts & Miscellaneous",
        'prop': 'show_part_library',
        'rows': (
            # The three legs differ in what they are placed against, not
            # in what they look like, so one picture serves all three.
            ("", (("Floating Shelves", "Floating Shelves",
                   "Floating Shelves"),
                  ("Valance", "Valance", "Valance"),
                  ("Support Frame", "Support Frame", "Support Frame"),
                  ("Base Assembly", "Base Assembly", "Base Assembly"),
                  ("Half Wall", "Half Wall", "Half Wall"),
                  ("Misc Part", "Misc Part", "Misc Part"),
                  ("Leg", "Leg", "Leg"),
                  ("Tall Leg", "Tall Leg", "Leg"),
                  ("Upper Leg", "Upper Leg", "Leg"),
                  ("Panel", "Panel", "Panel"))),
        ),
    },
)


def section_by_key(key):
    for section in SECTIONS:
        if section['key'] == key:
            return section
    return None


def products(section_key=None):
    """Flat list of every product, or just one section's.

    Each is a dict of ``{'key', 'label', 'thumbnail', 'section',
    'section_label', 'row_label', 'search'}``. ``key`` is the name the
    place operator takes; ``search`` is the pre-lowered haystack a
    search box matches against.
    """
    out = []
    for section in SECTIONS:
        if section_key and section['key'] != section_key:
            continue
        for row_label, items in section['rows']:
            for display, cabinet_name, thumbnail in items:
                out.append({
                    'key': cabinet_name,
                    'label': display,
                    'thumbnail': thumbnail,
                    'section': section['key'],
                    'section_label': section['label'],
                    'row_label': row_label,
                    'search': ' '.join((display, cabinet_name,
                                        section['label'],
                                        row_label)).lower(),
                })
    return out


def category_items():
    """EnumProperty items for a category filter: All, then each section."""
    items = [('ALL', "All Categories", "Every product in the library")]
    for section in SECTIONS:
        items.append((section['key'].upper(), section['label'],
                      "Only %s" % section['label']))
    return items


def search_products(query='', section_key='ALL'):
    """Products matching a category and a free-text query.

    Every whitespace-separated term must appear somewhere in the
    product's search text, so "pie upper" finds the Pie Cut Corner
    Upper without the exact name.
    """
    key = None if not section_key or section_key == 'ALL' else section_key.lower()
    terms = (query or '').lower().split()
    out = []
    for product in products(key):
        if all(term in product['search'] for term in terms):
            out.append(product)
    return out


def thumbnail_dir():
    return os.path.join(os.path.dirname(__file__), 'frameless_thumbnails')


_BY_KEY = None


def thumbnail_path(cabinet_name):
    """Resolve a product to a thumbnail file on disk, or None.

    Takes the product's key rather than its picture's name, because that
    is what a browser holds -- the mapping between the two is this
    library's business and lives here.
    """
    global _BY_KEY
    if _BY_KEY is None:
        _BY_KEY = {p['key']: p['thumbnail'] for p in products()}
    name = _BY_KEY.get(cabinet_name, cabinet_name)
    path = os.path.join(thumbnail_dir(), '%s.png' % name)
    return path if os.path.isfile(path) else None


# ---- Viewport browser contract ---------------------------------------------

# The scene property group this library keeps its settings on.
PROPS_GROUP = 'hb_frameless'

# No auto-join mode here; the browser simply shows no button.
AUTO_JOIN = None

# The form behind the browser's sizes button.
SIZES_FORM = 'draw_cabinet_sizes_ui'

# The library's settings, as the OPTIONS tab lists them. Cabinet Styles
# is a named pool like the face frame library's, but it opens as a
# dialog here rather than being drawn as a list -- the same UI the
# sidebar shows, which is enough until it is reached for as often.
OPTION_FORMS = (
    ("Cabinet Styles", 'draw_cabinet_styles_ui'),
    ("Door and Drawer Front Styles", 'draw_door_styles_ui'),
    ("Handles", 'draw_cabinet_options_handles'),
    ("General Construction", 'draw_cabinet_options_general'),
    ("Molding", 'draw_molding_ui'),
    ("Countertops & Backsplash", 'draw_countertop_ui'),
)

# Sections drawn INSIDE the viewport panel rather than opened as a
# dialog, keyed by the same draw-method name as OPTION_FORMS: a row
# named here folds open in place like a library category, and any
# other row still opens its form. A 'pool' page is a named list you
# pick from, add to and assign, with the active item's fields and
# commands below it. Fields are (kind, property, label); actions are
# rows of (label, operator).
OPTION_PAGES = {
    'draw_cabinet_styles_ui': {
        'kind': 'pool',
        'title': "Cabinet Styles",
        'props': 'hb_frameless',
        'collection': 'cabinet_styles',
        'index': 'active_cabinet_style_index',
        'add_op': 'hb_frameless.add_cabinet_style',
        'remove_op': 'hb_frameless.remove_cabinet_style',
        'duplicate_op': 'hb_frameless.duplicate_cabinet_style',
        'fields': (
            ('enum', 'sheet_material', "Material"),
            ('enum', 'front_material', "Fronts"),
            ('enum', 'edge_material', "Cabinet Edge"),
            ('enum', 'front_edge_material', "Front Edge"),
            ('enum', 'door_overlay_type', "Door Overlay"),
        ),
        'actions': (
            (("Assign Style",
              'hb_frameless.assign_cabinet_style_to_selected_cabinets'),
             ("Update Cabinets", 'hb_frameless.update_cabinets_from_style')),
        ),
    },
    'draw_door_styles_ui': {
        'kind': 'pool',
        'title': "Door and Drawer Front Styles",
        'props': 'hb_frameless',
        'collection': 'door_styles',
        'index': 'active_door_style_index',
        'add_op': 'hb_frameless.add_door_style',
        'remove_op': 'hb_frameless.remove_door_style',
        'duplicate_op': 'hb_frameless.duplicate_door_style',
        'fields': (
            ('enum', 'front_style', "Front Style"),
            ('enum', 'panel_type', "Door Panel"),
            ('enum', 'door_edgeband', "Edgebanding"),
        ),
        'actions': (
            (("Assign Style",
              'hb_frameless.assign_door_style_to_selected_fronts'),
             ("Update Fronts", 'hb_frameless.update_fronts_from_style')),
        ),
        # Room-level, not per style: what a NEW door opening is seeded
        # with. Drawn under the style's commands.
        'scene_fields': (
            ('bool', 'seed_door_shelves', "Shelves Behind Doors"),
        ),
    },
    # A 'form' page is fields on the library's property group itself
    # (scope 'main' = the project-wide copy on the main scene). A field
    # may carry a dict: 'when' hides it unless the callable says so,
    # 'thumb' gives a 'thumb' field the picture for each choice.
    'draw_cabinet_options_handles': {
        'kind': 'form',
        'title': "Handles",
        'props': 'hb_frameless',
        'scope': 'main',
        'fields': (
            ('thumb', 'door_pull_selection', "Door Pull",
             {'thumb': lambda ident: _pull_thumbnail(ident)}),
            ('thumb', 'drawer_pull_selection', "Drawer Pull",
             {'thumb': lambda ident: _pull_thumbnail(ident)}),
            ('distance', 'custom_pull_size', "Center to Center",
             {'when': lambda p: 'CUSTOM' in (p.door_pull_selection,
                                             p.drawer_pull_selection)}),
            ('enum', 'pull_finish', "Finish"),
            ('gap', None, None),
            ('distance', 'pull_dim_from_edge', "From Edge"),
            ('distance', 'pull_vertical_location_base', "Base Vertical"),
            ('distance', 'pull_vertical_location_tall', "Tall Vertical"),
            ('distance', 'pull_vertical_location_upper', "Upper Vertical"),
            ('bool', 'center_pulls_on_drawer_front', "Center Drawer Pulls"),
            ('distance', 'pull_vertical_location_drawers', "Drawer Vertical",
             {'when': lambda p: not p.center_pulls_on_drawer_front}),
        ),
        'actions': (
            (("Update Pulls", 'hb_frameless.update_all_pulls'),),
        ),
    },
    # Room-level construction defaults. Every field pushes itself onto
    # the cabinets already in the room, so there are no refresh buttons.
    # The drawer stack fields shape NEW drawer stacks only.
    'draw_cabinet_options_general': {
        'kind': 'form',
        'title': "General Construction",
        'props': 'hb_frameless',
        'scope': 'scene',
        'fields': (
            ('distance', 'default_carcass_part_thickness', "Material Thickness"),
            ('gap', None, None),
            ('distance', 'default_toe_kick_height', "Toe Kick Height"),
            ('distance', 'default_toe_kick_setback', "Toe Kick Setback"),
            ('enum', 'default_toe_kick_type', "Toe Kick Type"),
            ('distance', 'default_leg_leveler_inset', "Leveler Inset",
             {'when': lambda p: p.default_toe_kick_type == 'Leg Levelers'}),
            # One base under each run of Ladder Style cabinets.
            ('actions', (("Add Base Assemblies",
                          'hb_frameless.add_base_assemblies',
                          'selected_only', False),
                         ("Add to Selected",
                          'hb_frameless.add_base_assemblies',
                          'selected_only', True)), None),
            ('actions', (("Edit Base Assemblies",
                          'hb_frameless.edit_base_assemblies'),
                         ("Remove",
                          'hb_frameless.remove_base_assemblies')), None),
            ('gap', None, None),
            ('enum', 'base_top_construction', "Base Top"),
            ('gap', None, None),
            ('bool', 'equal_drawer_stack_heights', "Equal Drawer Stack Heights"),
            ('distance', 'top_drawer_front_height', "Top Drawer Height",
             {'when': lambda p: not p.equal_drawer_stack_heights}),
            ('bool', 'include_drawer_boxes', "Include Drawer Boxes"),
        ),
    },
    # Crown molding, the closet library's way: one profile for the room
    # and a command that runs it along every cabinet tall enough.
    'draw_molding_ui': {
        'kind': 'form',
        'title': "Molding",
        'props': 'hb_frameless',
        'scope': 'scene',
        'fields': (
            ('thumb', 'crown_profile', "Crown Profile",
             {'thumb': lambda ident: _crown_thumbnail(ident)}),
        ),
        'actions': (
            (("Add Crown Molding", 'hb_frameless.add_molding'),
             ("Remove", 'hb_frameless.delete_molding')),
        ),
    },
    # Countertops and backsplash. The sizes shape the NEXT Add
    # Countertops (rebuilding on every keystroke would throw away sink
    # cut-outs), so the commands sit right under them.
    'draw_countertop_ui': {
        'kind': 'form',
        'title': "Countertops & Backsplash",
        'props': 'hb_frameless',
        'scope': 'main',
        'fields': (
            ('label', None, "Countertops"),
            ('distance', 'countertop_thickness', "Thickness"),
            ('distance', 'countertop_overhang_front', "Front Overhang"),
            ('distance', 'countertop_overhang_sides', "Side Overhang"),
            ('distance', 'countertop_overhang_back', "Back Overhang"),
            ('actions', (("Add Countertops", 'hb_frameless.add_countertops',
                          'selected_only', False),
                         ("Add to Selected", 'hb_frameless.add_countertops',
                          'selected_only', True)), None),
            ('actions', (("Cut Hole (Select 2)",
                          'hb_frameless.countertop_boolean_cut'),
                         ("Remove", 'hb_frameless.remove_countertops')), None),
            ('gap', None, None),
            ('label', None, "Backsplash"),
            ('actions', (("Add Backsplash", 'home_builder.add_backsplash'),
                         ("Edit Edges", 'home_builder.edit_backsplash')), None),
            ('actions', (("Material", 'home_builder.surface_material'),
                         ("Remove", 'home_builder.remove_backsplash')), None),
        ),
    },
}


def _crown_thumbnail(ident):
    from . import molding_frameless
    return molding_frameless.profile_thumbnail(ident)


def _pull_thumbnail(ident):
    """The closet library's picture for a handle file, or None for the
    choices that have none (None, Custom)."""
    from ..closets import pulls_closets
    stem, ext = os.path.splitext(ident or '')
    if ext.lower() != '.blend':
        return None
    path = os.path.join(pulls_closets.HANDLES_DIR, stem + '.png')
    return path if os.path.exists(path) else None


def place(context, product):
    """Put one product in the scene -- the same operator the sidebar's
    library buttons fire, so there is no second placement path."""
    bpy.ops.hb_frameless.draw_cabinet('INVOKE_DEFAULT',
                                      cabinet_name=product['key'])
