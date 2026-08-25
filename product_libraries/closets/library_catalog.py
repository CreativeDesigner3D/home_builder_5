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
    ("Door & Drawer Front Styles", 'draw_front_options_ui'),
    ("Pulls", 'draw_pull_options_ui'),
    ("Drawers", 'draw_drawer_box_options_ui'),
    ("Rods & Hangers", 'draw_rod_options_ui'),
    ("Countertops", 'draw_countertop_options_ui'),
    ("Molding", 'draw_molding_options_ui'),
)


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
