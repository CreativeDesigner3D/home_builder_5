"""The face-frame product library, as data.

Every product used to live inline in the sidebar's ``draw_*_library_ui``
methods, which meant the list existed only as a side effect of drawing
it. Anything else that wanted to know what the library contains -- the
viewport library panel, a search box, a category filter -- had no way to
ask, short of a second hand-maintained copy that would drift.

So the products live here and the sidebar renders FROM this. One list,
one order, one place to add a product.

Shape
-----
``SECTIONS`` is an ordered tuple of sections. Each section is::

    {'key':   short id, used by the viewport panel's category filter
     'label': section header text, shown in both browsers
     'prop':  the expand/collapse BoolProperty backing the sidebar box
     'rows':  ((row_label, ((display, cabinet_name), ...)), ...)}

``row_label`` is the small left-hand caption in the sidebar ("Pie Cut",
"Diagonal", "Cabinet", "Standalone"); blank means an unlabelled row.
It is kept because it carries real meaning -- "Base" under "Pie Cut" and
"Base" under "Diagonal" are different products -- and the viewport panel
folds it into the searchable text for exactly that reason.

``display`` is the short button label; ``cabinet_name`` is the payload
for ``hb_face_frame.draw_cabinet`` AND the thumbnail filename in
``face_frame_thumbnails/``. Those two being the same string is a
convention of the library, not a coincidence -- see
``load_cabinet_thumbnail``.

Deliberately NOT here: the User library (read off disk at draw time) and
the Angled section (hidden until those products have builders). Both
keep their own draw methods.
"""

import os

import bpy


SECTIONS = (
    {
        'key': 'standard',
        'label': "Standard Cabinets",
        'prop': 'show_cabinet_library',
        'rows': (
            ("", (("Base", "Base"), ("Tall", "Tall"), ("Upper", "Upper"),
                  ("Lap", "Lap Drawer"), ("Stacked", "Upper Stacked"))),
        ),
    },
    {
        'key': 'appliance',
        'label': "Appliance Products",
        'prop': 'show_appliance_library',
        'rows': (
            # No dedicated Oven product: the Oven button places the
            # built-in tall oven tower.
            ("Cabinet", (("Sink", "Sink"),
                         ("Refrigerator", "Refrigerator Cabinet"),
                         ("Oven", "Built in Tall"))),
            ("Standalone", (("Dishwasher", "Dishwasher"),
                            ("Range", "Range"),
                            ("Hood", "Range Hood"),
                            ("Refrigerator", "Standalone Refrigerator"))),
            # Generic under-counter appliance (beverage centre, wine
            # fridge, ice maker) - relabel after placing via Set Label.
            ("", (("Under Counter", "Under Counter Appliance"),)),
        ),
    },
    {
        'key': 'corner',
        'label': "Corner Cabinets",
        'prop': 'show_corner_cabinet_library',
        'rows': (
            ("Pie Cut", (("Base", "Pie Cut Base"),
                         ("Drawer", "Pie Cut Drawer"),
                         ("Upper", "Pie Cut Upper"))),
            ("Diagonal", (("Base", "Diagonal Base"),
                          ("Tall", "Diagonal Tall"),
                          ("Upper", "Diagonal Upper"))),
        ),
    },
    {
        'key': 'vanity',
        'label': "Vanities",
        'prop': 'show_vanity_library',
        'rows': (
            ("Vanity", (("Special", "Special"),
                        ("Combination", "Combination"),
                        ("Deluxe", "Deluxe"))),
        ),
    },
    {
        'key': 'parts',
        'label': "Parts",
        'prop': 'show_part_library',
        'rows': (
            ("", (("Panel", "Panel"), ("Leg", "Leg Product"),
                  ("Door", "Door"))),
            ("", (("Misc", "Misc Part"),
                  ("Floating Shelf", "Floating Shelves"),
                  ("Valance", "Valance"))),
            ("", (("Wood Top", "Wood Top"), ("Mantle", "Mantle"))),
        ),
    },
    {
        'key': 'bath',
        'label': "Specialty Bath",
        'prop': 'show_specialty_bath_library',
        'rows': (
            ("Medicine", (("Recessed", "Standard Recessed Medicine Cabinet"),
                          ("Standard", "Medicine Cabinet"),
                          ("Tri-View", "Tri-View Medicine Cabinet"))),
            ("Other", (("Overstool", "Overstool Cabinet"),
                       ("Mirror", "Mirror Frame"),
                       ("Tub Skirt", "Tub Skirt"))),
        ),
    },
    {
        'key': 'bedroom',
        'label': "Specialty Bedroom & Bookcases",
        'prop': 'show_bedroom_bookcase_library',
        'rows': (
            ("Bookcase", (("Base", "Bookcase"),
                          ("Storage", "Bookcase Storage Unit"),
                          ("Upper", "Bookcase Upper"))),
            ("Dresser", (("5 Drawer", "5 Drawer Dresser"),
                         ("6 Drawer", "6 Drawer Dresser"))),
            ("Night Stand", (("Standard", "Night Stand"),
                             ("3 Drawer", "3 Drawer Night Stand"))),
            ("Other", (("Hutch", "Hutch Upper"),
                       ("Window Seat", "Window Seat"))),
        ),
    },
    {
        'key': 'misc',
        'label': "Misc",
        'prop': 'show_misc_library',
        'rows': (
            # X-Frame Ends hidden until that product has a builder.
            ("", (("Half Wall", "Half Wall"), ("Support", "Support Frame"),
                  ("FF & Doors", "Face Frame and Doors"))),
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

    Yields dicts so callers can filter and display without knowing the
    nested row shape::

        {'display', 'cabinet_name', 'section', 'section_label',
         'row_label', 'search'}

    ``search`` is the pre-lowered haystack a search box matches
    against: the display name, the real product name, the section and
    the row caption. The row caption matters -- it is the only thing
    separating a Pie Cut "Base" from a Diagonal "Base".
    """
    out = []
    for section in SECTIONS:
        if section_key and section['key'] != section_key:
            continue
        for row_label, items in section['rows']:
            for display, cabinet_name in items:
                out.append({
                    # 'key' and 'label' are what a product browser reads;
                    # 'display' / 'cabinet_name' are this library's own
                    # names for the same two things, kept because the
                    # sidebar has always used them.
                    'key': cabinet_name,
                    'label': display,
                    'display': display,
                    'cabinet_name': cabinet_name,
                    'section': section['key'],
                    'section_label': section['label'],
                    'row_label': row_label,
                    'search': ' '.join((display, cabinet_name,
                                        section['label'], row_label)).lower(),
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

    The query is matched as whitespace-separated terms, ALL of which
    must appear somewhere in the product's search text -- so "pie
    upper" finds the Pie Cut Upper without needing the exact name.
    """
    key = None if not section_key or section_key == 'ALL' else section_key.lower()
    terms = (query or '').lower().split()
    out = []
    for product in products(key):
        if all(term in product['search'] for term in terms):
            out.append(product)
    return out


# ---- Thumbnails ------------------------------------------------------------

def thumbnail_dir():
    """The bundled face_frame_thumbnails folder."""
    return os.path.join(os.path.dirname(__file__), 'face_frame_thumbnails')


def frameless_thumbnail_dir():
    """Fallback folder, so a product without a face-frame render still
    shows something. A face-frame thumbnail of the same name wins."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'frameless', 'frameless_thumbnails')


def thumbnail_path(cabinet_name):
    """Resolve a product to a thumbnail file on disk, or None.

    face_frame first, frameless second -- the rule
    ``load_cabinet_thumbnail`` has always used. It lives here so the
    sidebar (which turns it into a preview icon_id) and the viewport
    panel (which uploads it to a GPU texture) can never disagree about
    which file belongs to a product.
    """
    for folder in (thumbnail_dir(), frameless_thumbnail_dir()):
        path = os.path.join(folder, '%s.png' % cabinet_name)
        if os.path.isfile(path):
            return path
    return None


# ---- Viewport browser contract ---------------------------------------------
# What the HUD's library panel needs from a product library, so it can
# browse this one without knowing anything about face frames. Another
# library becomes browsable by exposing the same names and registering
# itself (see operators/library_panel.register_catalog).

# The scene property group this library keeps its settings on. Every
# form named below is a method on it, so they name only the method.
PROPS_GROUP = 'hb_face_frame'

# A bool the browser offers in its header, or None where the library has
# no such mode.
AUTO_JOIN = 'auto_join_cabinets'

# The form behind the browser's sizes button.
SIZES_FORM = 'draw_cabinet_sizes_ui'

# The library's settings, as the OPTIONS tab lists them: (label, the
# method that draws that form). Each opens as a dialog showing the
# sidebar's own UI -- these are property sheets, and a GPU panel has no
# business reimplementing a unit field. Cabinet Styles is missing on
# purpose: it is a named pool you pick from mid-design, so the tab draws
# it as a real list above these.
OPTION_FORMS = (
    ("Door & Drawer Front Styles", 'draw_door_styles_ui'),
    ("Finished Ends and Backs", 'draw_finished_ends_ui'),
    ("Pulls", 'draw_pulls_ui'),
    ("Drawer Boxes", 'draw_drawer_box_ui'),
    ("Countertops", 'draw_countertop_ui'),
    ("Molding", 'draw_molding_ui'),
)


def place(context, product):
    """Put one product in the scene -- the same operator the sidebar's
    library buttons fire, so there is no second placement path."""
    bpy.ops.hb_face_frame.draw_cabinet(
        'INVOKE_DEFAULT', cabinet_name=product['key'])
