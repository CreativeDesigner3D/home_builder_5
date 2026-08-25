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
                      ("Lap Drawer", "Lap Drawer", "Lap Drw"))),
            ("Upper & Tall", (("Upper", "Upper", "Upper"),
                              ("Upper Stacked", "Upper Stacked",
                               "Upper Stacked"),
                              ("Tall", "Tall", "Tall"),
                              ("Tall Stacked", "Tall Stacked",
                               "Tall Stacked"))),
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
        ),
    },
    {
        'key': 'appliance',
        'label': "Appliances",
        'prop': 'show_appliance_library',
        'rows': (
            ("", (("Fridge Cabinet", "Refrigerator Cabinet",
                   "Refrigerator Frameless Cabinet"),
                  ("Dishwasher", "Dishwasher", "Dishwasher"),
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
    ("Drawer Boxes", 'draw_drawer_box_ui'),
    ("Crown Details", 'draw_crown_details_ui'),
    ("Toe Kick Details", 'draw_toe_kick_details_ui'),
    ("Upper Bottom Details", 'draw_upper_bottom_details_ui'),
    ("Countertops", 'draw_countertop_ui'),
)


def place(context, product):
    """Put one product in the scene -- the same operator the sidebar's
    library buttons fire, so there is no second placement path."""
    bpy.ops.hb_frameless.draw_cabinet('INVOKE_DEFAULT',
                                      cabinet_name=product['key'])
