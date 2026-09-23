"""The closet product library, as data the viewport browser can read.

Unlike the other two libraries this one needed no extracting: its
products already live as data in ``starter_presets``, which the sidebar
renders from. So this is an adapter rather than a second copy -- it
reshapes those tables into the contract in
``operators/library_panel.register_catalog`` and nothing here restates
what a product is. Add a closet product to ``starter_presets`` and both
browsers get it.

Two kinds of product sit side by side. A STARTER is a run placed by one
operator that takes its name; a PART is dropped on its own and names the
operator that places it, with its own arguments. ``place`` is what
papers over the difference, so the browser does not have to know.
"""

import os

import bpy

from . import starter_presets


def _section_key(label):
    return label.lower().replace(' ', '_')


def _build_sections():
    """STARTER_SECTIONS then PART_SECTIONS, in the order the sidebar
    shows them, as the browser's section shape."""
    sections = []
    for label, entries in starter_presets.STARTER_SECTIONS:
        sections.append({
            'key': _section_key(label),
            'label': label,
            'rows': (("", tuple((name, text) for name, text, _d in entries)),),
            'starter': True,
        })
    for label, entries in starter_presets.PART_SECTIONS:
        sections.append({
            'key': _section_key(label),
            'label': label,
            'rows': (("", tuple((name, text) for name, text, _d, _op, _p
                                in entries)),),
            'starter': False,
        })
    return tuple(sections)


SECTIONS = _build_sections()

# name -> (operator id, properties) for the loose parts, so place() can
# hand a part to the operator that knows how to drop it.
_PART_OPS = {name: (op_id, dict(props or {}))
             for _label, entries in starter_presets.PART_SECTIONS
             for name, _text, _desc, op_id, props in entries}


def section_by_key(key):
    for section in SECTIONS:
        if section['key'] == key:
            return section
    return None


def products(section_key=None):
    """Flat list of every product, or just one section's.

    Each is a dict of ``{'key', 'label', 'section', 'section_label',
    'row_label', 'search'}``. ``key`` is the starter or part name.
    """
    out = []
    for section in SECTIONS:
        if section_key and section['key'] != section_key:
            continue
        for row_label, items in section['rows']:
            for name, label in items:
                out.append({
                    'key': name,
                    'label': label,
                    'section': section['key'],
                    'section_label': section['label'],
                    'row_label': row_label,
                    # The name matters as much as the label here: half
                    # the labels are "Base" or "Tall" and only the name
                    # says which run they belong to.
                    'search': ' '.join((label, name,
                                        section['label'])).lower(),
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
    """Products matching a category and a free-text query -- every
    whitespace-separated term must appear in the product's search text."""
    key = None if not section_key or section_key == 'ALL' else section_key.lower()
    terms = (query or '').lower().split()
    out = []
    for product in products(key):
        if all(term in product['search'] for term in terms):
            out.append(product)
    return out


def thumbnail_dir():
    return os.path.join(os.path.dirname(__file__), 'closet_thumbnails')


def thumbnail_path(name):
    """Resolve a product to a thumbnail file on disk, or None.

    Most of this library has no render yet; a product without one draws
    as a plain tile rather than being hidden.
    """
    path = os.path.join(thumbnail_dir(), '%s.png' % name)
    return path if os.path.isfile(path) else None


# ---- Viewport browser contract ---------------------------------------------

# The scene property group this library keeps its settings on.
PROPS_GROUP = 'hb_closets'

# No auto-join mode in this library; the browser shows no button for one.
AUTO_JOIN = None

# The form behind the browser's sizes button.
SIZES_FORM = 'draw_closet_sizes_ui'

# The library's settings, as the OPTIONS tab lists them. Design Warnings
# is deliberately not among them: it reports on the design rather than
# setting anything, and the warnings already show on the model.
OPTION_FORMS = (
    ("Materials", 'draw_material_options_ui'),
    ("Doors & Drawer Fronts", 'draw_front_options_ui'),
    ("Pulls", 'draw_pull_options_ui'),
    ("Drawers", 'draw_drawer_box_options_ui'),
    ("Rods & Hangers", 'draw_rod_options_ui'),
    ("Accessories", 'draw_accessory_options_ui'),
    ("Countertops", 'draw_countertop_options_ui'),
    ("Molding", 'draw_molding_options_ui'),
)


def _asset_thumbnail(directory, ident):
    """The picture beside a .blend asset, or None for the choices that
    have none (None, Custom)."""
    stem, ext = os.path.splitext(ident or '')
    if ext.lower() != '.blend':
        return None
    path = os.path.join(directory, stem + '.png')
    return path if os.path.exists(path) else None


def _pull_thumbnail(ident):
    from . import pulls_closets
    return _asset_thumbnail(pulls_closets.HANDLES_DIR, ident)


def _crown_thumbnail(ident):
    from . import molding_closets
    return _asset_thumbnail(molding_closets.CROWN_DIR, ident)


def _base_thumbnail(ident):
    from . import molding_closets
    return _asset_thumbnail(molding_closets.BASE_DIR, ident)


def _accessory_notes(context):
    """The accessories the room's finish does not come in, as lines."""
    from . import accessories_closets
    rows = accessories_closets.unavailable_finishes(context.scene)
    if not rows:
        return ()
    return (("Not available in this finish:",)
            + tuple(accessories_closets.notice_lines(rows)))


# Every section is drawn INSIDE the viewport panel, as a 'form' page on
# the room's own copy of the group: the closet options are room-wide and
# each one re-applies itself to the room as it changes. See the
# frameless catalog for the page contract. Where the sidebar greys a
# field out, the page leaves it out.
OPTION_PAGES = {
    'draw_material_options_ui': {
        'kind': 'form',
        'title': "Materials",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('enum', 'closet_material', "Closet"),
            ('enum', 'closet_front_material', "Fronts"),
            ('gap', None, None),
            ('label', None, "Edgebanding"),
            ('enum', 'closet_edge_material', "Closet Edge"),
            ('enum', 'closet_front_edge_material', "Front Edge"),
        ),
    },
    'draw_front_options_ui': {
        'kind': 'form',
        'title': "Door & Drawer Front Styles",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('enum', 'closet_front_style', "Front Style"),
            ('enum', 'closet_panel_type', "Door Panel"),
            ('enum', 'closet_door_edgeband', "Edgebanding"),
            ('gap', None, None),
            ('bool', 'closet_seed_door_shelves', "Shelves Behind Doors"),
        ),
    },
    'draw_pull_options_ui': {
        'kind': 'form',
        'title': "Pulls",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('thumb', 'closet_pull', "Pull",
             {'thumb': lambda ident: _pull_thumbnail(ident)}),
            ('distance', 'closet_custom_pull_size', "Center to Center",
             {'when': lambda p: p.closet_pull == 'CUSTOM'}),
            ('enum', 'closet_pull_finish', "Finish"),
            ('gap', None, None),
            ('label', None, "Position"),
            ('distance', 'pull_horizontal_offset', "From Edge"),
            ('distance', 'pull_vertical_location_base', "Base Vertical"),
            ('distance', 'pull_vertical_location_tall', "Tall Vertical"),
            ('distance', 'pull_vertical_location_upper', "Upper Vertical"),
            ('bool', 'center_pulls_on_drawer_front', "Center Drawer Pulls"),
            ('distance', 'pull_vertical_location_drawers', "Drawer Vertical",
             {'when': lambda p: not p.center_pulls_on_drawer_front}),
        ),
    },
    'draw_drawer_box_options_ui': {
        'kind': 'form',
        'title': "Drawers",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('enum', 'closet_drawer_box', "Drawer Box"),
            ('bool', 'closet_drawer_vertical_grain', "Vertical Grain"),
        ),
    },
    'draw_rod_options_ui': {
        'kind': 'form',
        'title': "Rods & Hangers",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('label', None, "Hanging Rods"),
            ('enum', 'closet_rod_type', "Type"),
            ('enum', 'closet_rod_finish', "Finish"),
            ('gap', None, None),
            ('label', None, "Hangers"),
            ('enum', 'closet_hanger_model', "Model"),
            ('actions', (("Randomize Hangers",
                          'hb_closets.randomize_hangers'),
                         ("Install Model Pack",
                          'hb_closets.install_model_pack')), None),
        ),
    },
    'draw_accessory_options_ui': {
        'kind': 'form',
        'title': "Accessories",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('enum', 'default_accessory_color', "Metal"),
            ('enum', 'default_accessory_fabric', "Fabric"),
            ('notes', _accessory_notes, None),
        ),
    },
    # With the toggle on, tops take the closet material and the shelf
    # thickness, so neither field below it applies.
    'draw_countertop_options_ui': {
        'kind': 'form',
        'title': "Countertops",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('bool', 'use_closet_material_for_countertops',
             "Use Closet Material for Tops"),
            ('enum', 'closet_countertop_material', "Material",
             {'when': lambda p: not p.use_closet_material_for_countertops}),
            ('distance', 'countertop_thickness', "Thickness",
             {'when': lambda p: not p.use_closet_material_for_countertops}),
        ),
    },
    'draw_molding_options_ui': {
        'kind': 'form',
        'title': "Molding",
        'props': 'hb_closets',
        'scope': 'scene',
        'fields': (
            ('label', None, "Crown"),
            ('thumb', 'closet_crown_profile', "Profile",
             {'thumb': lambda ident: _crown_thumbnail(ident)}),
            ('actions', (("Add Crown Molding", 'hb_closets.add_molding',
                          'molding_kind', 'CROWN'),
                         ("Remove", 'hb_closets.delete_molding',
                          'molding_kind', 'CROWN')), None),
            ('gap', None, None),
            ('label', None, "Base"),
            ('thumb', 'closet_base_profile', "Profile",
             {'thumb': lambda ident: _base_thumbnail(ident)}),
            ('actions', (("Add Base Molding", 'hb_closets.add_molding',
                          'molding_kind', 'BASE'),
                         ("Remove", 'hb_closets.delete_molding',
                          'molding_kind', 'BASE')), None),
        ),
    },
}


def place(context, product):
    """Put one product in the scene, through whichever operator owns it --
    a starter by name, a loose part by the operator it carries."""
    name = product['key']
    spec = _PART_OPS.get(name)
    if spec is None:
        bpy.ops.hb_closets.place_starter('INVOKE_DEFAULT', starter_name=name)
        return
    op_id, props = spec
    mod, op_name = op_id.split('.', 1)
    getattr(getattr(bpy.ops, mod), op_name)('INVOKE_DEFAULT', **props)
