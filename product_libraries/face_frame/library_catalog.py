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
     'rows':  ((row_label, ((display, cabinet_name), ...)), ...)
     'toggle': optional (label, scene group, bool name) -- a switch the
               viewport panel draws on the section's header row}

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
        # Cages or 3D models, room-wide. Which appliances HAVE a model is
        # each one's own choice, in its prompts.
        'toggle': ("Show Model", 'home_builder', 'show_appliance_models'),
        'rows': (
            # No dedicated Oven product: the Oven button places the
            # built-in tall oven tower.
            ("Cabinet", (("Sink", "Sink"),
                         ("Cooktop", "Cooktop Base"),
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
        # Galley workstation sink bases, one per workstation size.
        'key': 'galley',
        'label': "Galley Workstations",
        'prop': 'show_galley_library',
        'rows': (
            ("", (("IWS 2", "Galley IWS 2"), ("IWS 3", "Galley IWS 3"),
                  ("IWS 4", "Galley IWS 4"))),
            ("", (("IWS 5", "Galley IWS 5"), ("IWS 6", "Galley IWS 6"),
                  ("IWS 7", "Galley IWS 7"))),
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
            ("Wall Hung", (("Floating", "Floating Vanity"),)),
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
            ("Wrap", (("Column", "Column"), ("Beam", "Beam"))),
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
            ("Sink", (("ADA", "ADA Sink"),)),
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
         'row_label', 'search', 'path_draw'}

    ``path_draw`` is True for a product that can also be drawn through
    points -- a run of it built along a clicked path -- so a browser
    can offer that as a second way in on the same tile.

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
                    'path_draw': can_draw_path(cabinet_name),
                })
    return out


def can_draw_path(cabinet_name):
    """True when the product has a path-drawing builder."""
    from .operators import ops_draw_path
    return ops_draw_path.can_draw_path(cabinet_name)


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
# method that draws that form in the sidebar). Cabinet Styles comes
# first and starts unfolded: it is the pool reached for mid-design. The
# sidebar keeps door and drawer front styles behind one tabbed form;
# they are two pools, so here each gets a row, and the second row's
# name is only a key for its page.
OPTION_FORMS = (
    ("Cabinet Styles", 'draw_cabinet_styles_ui'),
    ("Door Styles", 'draw_door_styles_ui'),
    ("Drawer Front Styles", 'draw_drawer_front_styles_ui'),
    ("Finished Ends and Backs", 'draw_finished_ends_ui'),
    ("Pulls", 'draw_pulls_ui'),
    ("Drawer Boxes", 'draw_drawer_box_ui'),
    ("Countertops & Backsplash", 'draw_countertop_ui'),
    ("Molding", 'draw_molding_ui'),
)


def _front_style_fields(kind):
    """The fields of one door or drawer front style. The catalog pick
    (series, shape, panel) decides the construction; the widths follow
    it until their padlock is opened. Hardware callouts and the profile overrides stay
    in the sidebar."""
    five_piece = lambda p: p.door_type == '5_PIECE'
    fields = [
        ('label', None, "Catalog"),
        ('enum', 'front_series', "Series"),
        ('enum', 'front_shape', "Shape"),
        ('enum', 'front_panel', "Panel"),
        ('enum', 'grain_direction', "Grain Direction"),
        ('gap', None, None, {'when': five_piece}),
        ('label', None, "Frame Widths", {'when': five_piece}),
        ('locked', 'stile_width', "Stile Width",
         {'unlock': 'unlock_stile_width', 'when': five_piece}),
        ('locked', 'rail_width', "Rail Width",
         {'unlock': 'unlock_rail_width', 'when': five_piece}),
        ('bool', 'show_rail_annotation', "Show Rail Callout",
         {'when': five_piece}),
    ]
    if kind == 'DRAWER':
        fields.append(('bool', 'match_door_rail_width',
                       "Match Door Rail Width", {'when': five_piece}))
    return tuple(fields)


def _ref_fields(name_attr, image_attr, label, when=None):
    """A finish reference: its name, its picture, and a second picture
    once the first is set. Shown only with References switched on."""
    def second(p):
        return bool(getattr(p, image_attr, "")
                    or getattr(p, image_attr + "_2", ""))
    shown = when or (lambda p: True)
    return (
        ('text', name_attr, label + " Ref", {'when': shown}),
        ('file', image_attr, "Ref Image", {'when': shown}),
        ('file', image_attr + "_2", "Ref Image 2",
         {'when': lambda p: shown(p) and second(p)}),
    )


def _active_cabinet_style(context):
    from .props_hb_face_frame import get_style_props
    sp = get_style_props(context)
    styles = getattr(sp, 'cabinet_styles', None)
    if not styles:
        return None
    i = sp.active_cabinet_style_index
    return styles[i] if 0 <= i < len(styles) else None


def _special_effect_choices(context):
    """The effects this style's wood and colour allow, less the ones it
    already has, as menu entries that each add one."""
    from . import style_options
    style = _active_cabinet_style(context)
    if style is None:
        return ()
    have = {e.name for e in style.special_effects}
    return tuple((name, 'hb_face_frame.add_special_effect',
                  {'effect_name': name})
                 for name in style_options.special_effects_for(
                     style.finish_wood, style.finish_color)
                 if name not in have)


def _alternate_drawer_notes(context, style):
    from . import props_hb_face_frame
    return props_hb_face_frame.alternate_drawer_notes(style, context)


def _cabinet_style_fields():
    """The fields of one cabinet style, in the sidebar form's order.
    A 'choice' is a dropdown whose chip turns it into typed text, for a
    value outside the list; the typed value only prints, the dropdown
    still drives the geometry and material."""
    refs = lambda p: p.show_finish_references

    def custom_finish(p):
        from . import style_options
        return style_options.is_custom_finish(p.finish_color)

    fields = [
        ('label', None, "Cabinet"),
        ('choice', 'finish_wood', "Wood", {'custom': 'ss_wood'}),
        ('choice', 'interior_material_type', "Interior",
         {'custom': 'ss_interior'}),
        ('native', 'custom_interior_material', "Interior Material",
         {'when': lambda p: (not p.ss_interior_is_custom
                             and p.interior_material_type == 'CUSTOM')}),
        ('choice', 'finish_overlay', "Overlay", {'custom': 'ss_overlay'}),
        ('choice', 'ss_corner_treatment', "Corner Treatment"),
        ('choice', 'ss_fin_opening_edge', "Fin Opening Edge"),
        # Sixteen sizes by three cabinet types read best as the grid they
        # are, so they open in one rather than filling the panel a greyed
        # row at a time. A rail follows the overlay until its padlock is
        # opened there.
        ('actions', (("Face Frame Sizes...",
                      'hb_face_frame.face_frame_sizes'),), None),
    ]
    fields += [
        ('gap', None, None),
        ('label', None, "Finish"),
        ('bool', 'show_finish_references', "References"),
        ('choice', 'finish_color', "Color", {'custom': 'ss_color'}),
        # A custom finish is matched to a sample, so there is no colour
        # on file for it -- this is the one to render in.
        ('native', 'custom_finish_color', "Custom Color",
         {'when': custom_finish}),
    ]
    fields += _ref_fields('ss_color_ref_name', 'ss_color_ref_image',
                          "Color", refs)
    fields.append(('choice', 'finish_varnish', "Varnish",
                   {'custom': 'ss_varnish'}))
    fields += _ref_fields('ss_varnish_ref_name', 'ss_varnish_ref_image',
                          "Varnish", refs)
    fields.append(('choice', 'finish_glaze', "Glaze", {'custom': 'ss_glaze'}))
    fields += _ref_fields('ss_glaze_ref_name', 'ss_glaze_ref_image',
                          "Glaze", refs)
    fields += [
        ('items', 'special_effects', None,
         # A name to read, not a locked value: plain, so it is not greyed.
         {'kind': 'text', 'prop': 'name',
          'row': {'readonly': True, 'plain': True},
          'remove': ('hb_face_frame.remove_special_effect',
                     lambda i, item: {'effect_name': item.name}),
          'fields': lambda style, item: (
              _ref_fields('ref_name', 'ref_image', "Effect")
              if style.show_finish_references else ())}),
        ('pick', _special_effect_choices, "Add Special Effect"),
        ('gap', None, None),
        ('label', None, "Fronts"),
        ('choice', 'door_style', "Door", {'custom': 'ss_door'}),
        # Extra styles document the other fronts in use on the Style
        # Section page; only the first extra drawer style has a geometric
        # effect (the Use Extra Style At height below).
        ('items', 'extra_door_styles', None,
         {'kind': 'enum', 'prop': 'style',
          'remove': ('hb_face_frame.remove_cabinet_extra_front_style',
                     lambda i, item: {'kind': 'DOOR', 'index': i})}),
        ('actions', (("Add Door Style",
                      'hb_face_frame.add_cabinet_extra_front_style',
                      'kind', 'DOOR'),), None),
        ('choice', 'drawer_front_style', "Drawer Front",
         {'custom': 'ss_drawer'}),
        ('items', 'extra_drawer_front_styles', None,
         {'kind': 'enum', 'prop': 'style',
          'remove': ('hb_face_frame.remove_cabinet_extra_front_style',
                     lambda i, item: {'kind': 'DRAWER', 'index': i})}),
        ('actions', (("Add Drawer Front Style",
                      'hb_face_frame.add_cabinet_extra_front_style',
                      'kind', 'DRAWER'),), None),
        # Drawer fronts this tall take the first extra style (0 = off).
        ('distance', 'extra_drawer_front_height', "Alternate Style Over",
         {'when': lambda p: len(p.extra_drawer_front_styles) > 0}),
        ('notes', _alternate_drawer_notes, None, {'owner': True}),
        ('gap', None, None),
        ('label', None, "Doors"),
        ('choice', 'finish_hinge', "Hinge", {'custom': 'ss_hinge'}),
        ('gap', None, None),
        ('label', None, "Drawers"),
        ('choice', 'ss_drawer_slides', "Drawer Slides"),
        ('choice', 'ss_drawer_box_construction', "Box Construction"),
        ('file', 'ss_drawer_box_brand', "Box Brand Logo"),
        ('gap', None, None),
        ('label', None, "Door & Drawer Edge Profile"),
        ('choice', 'ss_edge_profile', "Edge Profile"),
        ('gap', None, None),
        # Printed at the end of the style's Style Section block.
        ('label', None, "Notes"),
        ('items', 'ss_notes', None,
         {'kind': 'text', 'prop': 'text',
          'remove': ('hb_face_frame.remove_style_note',
                     lambda i, item: {'index': i})}),
        ('actions', (("Add Note", 'hb_face_frame.add_style_note'),), None),
    ]
    return tuple(fields)


def _front_style_actions(kind):
    return ((("Assign by Painting", 'hb_face_frame.paint_assign_front_style',
              'kind', kind),
             ("Update Fronts", 'hb_face_frame.update_fronts_from_style',
              'kind', kind)),)


def _flush_x(p):
    return 'FLUSH_X' in (p.default_finished_end_type,
                         p.default_finished_back_type,
                         p.dishwasher_finished_end_type)


def _not_blum(p):
    return p.drawer_box_sizing != 'BLUM_TANDEM'


def _pull_thumbnail(ident):
    from . import pulls
    stem, ext = os.path.splitext(ident or '')
    if ext.lower() != '.blend':
        return None
    return pulls.find_pull_file(stem + '.png')


def _pull_assignment_notes(context):
    """What each zone is wearing. An unassigned zone rides the legacy
    scene-wide selections, so the effective pull is what is shown."""
    props = context.scene.hb_face_frame
    lines = []
    for zone_prop, label, legacy in (
            ('pull_assign_base', "Base", props.door_pull_selection),
            ('pull_assign_tall', "Tall", props.door_pull_selection),
            ('pull_assign_upper', "Upper", props.door_pull_selection),
            ('pull_assign_drawers', "Drawers", props.drawer_pull_selection)):
        sel = getattr(props, zone_prop) or legacy
        stem = "None" if sel in ('NONE', '') else os.path.splitext(sel)[0]
        lines.append("%s: %s" % (label, stem))
    return lines


def _has_molding_pack(_p=None):
    from ...molding import packages
    return bool(packages.profile_paths())


def _crown_uses(p, category):
    from ...molding import packages
    return packages.stack_uses_category('CROWN', p.molding_crown_package,
                                        category)


# Sections drawn INSIDE the viewport panel rather than opened as a
# dialog -- see the frameless catalog for the page contract. Where the
# sidebar greys a field out, the page leaves it out.
OPTION_PAGES = {
    # The commands sit straight under the list: a style has more fields
    # than fit on screen, and the brushes are what the list is reached
    # for. Order is what the list means -- the first style is the one
    # drawings leave white -- hence the move arrows.
    'draw_cabinet_styles_ui': {
        'kind': 'pool',
        'title': "Cabinet Styles",
        'props': 'hb_face_frame',
        'collection': 'cabinet_styles',
        'index': 'active_cabinet_style_index',
        'add_op': 'hb_face_frame.add_cabinet_style',
        'remove_op': 'hb_face_frame.remove_cabinet_style',
        'move_op': 'hb_face_frame.move_cabinet_style',
        'actions_first': True,
        'fields': _cabinet_style_fields(),
        'actions': (
            (("Assign to Selected",
              'hb_face_frame.assign_style_to_selected_cabinets'),
             ("Update Cabinets", 'hb_face_frame.update_cabinets_from_style')),
            (("Paint Cabinet", 'hb_face_frame.paint_assign_cabinet_style'),
             ("Paint Part", 'hb_face_frame.paint_part_material',
              'brush', 'FINISH')),
            (("Paint Interior", 'hb_face_frame.paint_part_material',
              'brush', 'INTERIOR'),
             ("Reset Part", 'hb_face_frame.paint_part_material',
              'brush', 'RESET')),
        ),
    },
    'draw_door_styles_ui': {
        'kind': 'pool',
        'title': "Door Styles",
        'props': 'hb_face_frame',
        'collection': 'door_styles',
        'index': 'active_door_style_index',
        'add_op': 'hb_face_frame.add_door_style',
        'remove_op': 'hb_face_frame.remove_door_style',
        'fields': _front_style_fields('DOOR'),
        'actions': _front_style_actions('DOOR'),
    },
    'draw_drawer_front_styles_ui': {
        'kind': 'pool',
        'title': "Drawer Front Styles",
        'props': 'hb_face_frame',
        'collection': 'drawer_front_styles',
        'index': 'active_drawer_front_style_index',
        'add_op': 'hb_face_frame.add_drawer_front_style',
        'remove_op': 'hb_face_frame.remove_drawer_front_style',
        'fields': _front_style_fields('DRAWER'),
        'actions': _front_style_actions('DRAWER'),
    },
    # Room-level. Apply writes the type to every side flagged exposed;
    # the other defaults are read by the solver per cabinet.
    'draw_finished_ends_ui': {
        'kind': 'form',
        'title': "Finished Ends and Backs",
        'props': 'hb_face_frame',
        'scope': 'scene',
        'fields': (
            ('enum', 'default_finished_end_type', "Type"),
            ('enum', 'default_finished_back_type', "Back Type"),
            ('enum', 'dishwasher_finished_end_type', "Dishwasher Side"),
            ('distance', 'default_flush_x_amount', "Flush X Amount",
             {'when': _flush_x}),
            ('actions', (("Apply to All Exposed",
                          'hb_face_frame.apply_finished_ends_to_exposed'),),
             None),
            ('actions', (("Recalculate Side Exposure",
                          'hb_face_frame.recalculate_side_exposure'),), None),
            ('actions', (("Show Applied Panels",
                          'hb_face_frame.show_applied_panels'),), None,
             {'when': lambda p: (p.default_finished_end_type != 'FINISHED'
                                 or p.default_finished_back_type
                                 != 'FINISHED')}),
        ),
    },
    # The pull picked here is inert until one of the Assign commands
    # puts it on a zone.
    'draw_pulls_ui': {
        'kind': 'form',
        'title': "Pulls",
        'props': 'hb_face_frame',
        'scope': 'scene',
        'fields': (
            ('label', None, "Pull Library"),
            ('enum', 'door_pull_category', "Category"),
            ('thumb', 'pull_browser_selection', "Pull",
             {'thumb': lambda ident: _pull_thumbnail(ident)}),
            ('enum', 'pull_finish', "Finish"),
            ('gap', None, None),
            ('label', None, "Assign To"),
            ('actions', (("Base", 'hb_face_frame.assign_pull',
                          'target', 'BASE'),
                         ("Tall", 'hb_face_frame.assign_pull',
                          'target', 'TALL'),
                         ("Upper", 'hb_face_frame.assign_pull',
                          'target', 'UPPER'),
                         ("Drawers", 'hb_face_frame.assign_pull',
                          'target', 'DRAWERS')), None),
            ('actions', (("Assign to Selected Fronts",
                          'hb_face_frame.assign_pull',
                          'target', 'SELECTED'),), None),
            ('notes', _pull_assignment_notes, None),
            ('gap', None, None),
            ('label', None, "Position"),
            ('distance', 'pull_horizontal_offset', "Horizontal Offset"),
            ('distance', 'pull_vertical_location_base', "Base Vertical"),
            ('distance', 'pull_vertical_location_tall', "Tall Vertical"),
            ('distance', 'pull_vertical_location_upper', "Upper Vertical"),
            ('bool', 'center_pulls_on_drawer_front', "Center Drawer Pulls"),
            ('gap', None, None),
            ('actions', (("Install Pull Library",
                          'hb_face_frame.install_pull_library'),
                         ("Open Folder",
                          'hb_face_frame.open_pull_library_folder')), None),
        ),
    },
    'draw_drawer_box_ui': {
        'kind': 'form',
        'title': "Drawer Boxes",
        'props': 'hb_face_frame',
        'scope': 'main',
        'fields': (
            ('bool', 'include_drawer_boxes', "Include Drawer Boxes"),
            ('enum', 'drawer_box_sizing', "Sizing"),
            ('notes', lambda context: (
                "Sides 3/16\", Bottom 9/16\", Top 5/16\" min",
                "Stock heights, runner depth (15/16\" rear min)"), None,
             {'when': lambda p: p.drawer_box_sizing == 'BLUM_TANDEM'}),
            ('bool', 'use_stock_drawer_box_heights', "Stock Box Heights",
             {'when': _not_blum}),
            ('gap', None, None,
             {'when': _not_blum}),
            ('label', None, "Clearances",
             {'when': _not_blum}),
            ('distance', 'drawer_box_side_clearance', "Side",
             {'when': _not_blum}),
            ('distance', 'drawer_box_top_clearance', "Top",
             {'when': _not_blum}),
            ('distance', 'drawer_box_bottom_clearance', "Bottom",
             {'when': _not_blum}),
            ('distance', 'drawer_box_rear_clearance', "Rear",
             {'when': _not_blum}),
        ),
    },
    # The sizes shape the NEXT Add Countertops, so the commands sit
    # right under them.
    'draw_countertop_ui': {
        'kind': 'form',
        'title': "Countertops & Backsplash",
        'props': 'hb_face_frame',
        'scope': 'main',
        'fields': (
            ('label', None, "Countertops"),
            ('distance', 'countertop_thickness', "Thickness"),
            ('distance', 'countertop_overhang_front', "Front Overhang"),
            ('distance', 'countertop_overhang_sides', "Side Overhang"),
            ('distance', 'countertop_overhang_back', "Back Overhang"),
            ('actions', (("Add Countertops", 'hb_face_frame.add_countertops',
                          'selected_only', False),
                         ("Add to Selected", 'hb_face_frame.add_countertops',
                          'selected_only', True)), None),
            ('actions', (("Cut Hole (Select 2)",
                          'hb_face_frame.countertop_boolean_cut'),
                         ("Remove", 'hb_face_frame.remove_countertops')), None),
            ('gap', None, None),
            ('label', None, "Backsplash"),
            ('actions', (("Add Backsplash", 'home_builder.add_backsplash'),
                         ("Edit Edges", 'home_builder.edit_backsplash')), None),
            ('actions', (("Material", 'home_builder.surface_material'),
                         ("Remove", 'home_builder.remove_backsplash')), None),
        ),
    },
    # Room molding packages live on the room's home_builder group, not
    # on this library's; picking one applies it to the room at once. The
    # profile overrides only show with a molding pack installed.
    'draw_molding_ui': {
        'kind': 'form',
        'title': "Molding",
        'props': 'home_builder',
        'scope': 'scene',
        'fields': (
            ('label', None, "Crown"),
            ('enum', 'molding_crown_package', "Package"),
            ('distance', 'molding_crown_reveal', "Reveal",
             {'when': lambda p: p.molding_crown_package != 'NONE'}),
            ('bool', 'molding_crown_to_ceiling', "Molding to Ceiling",
             {'when': lambda p: p.molding_crown_package != 'NONE'}),
            ('distance', 'molding_spacer_height', "Spacer Height",
             {'when': lambda p: (_crown_uses(p, 'Spacer')
                                 and not p.molding_crown_to_ceiling)}),
            ('enum', 'molding_crown_profile', "Profile",
             {'when': lambda p: (_has_molding_pack()
                                 and _crown_uses(p, 'Crown Molding'))}),
            ('enum', 'molding_spacer_profile', "Spacer",
             {'when': lambda p: (_has_molding_pack()
                                 and _crown_uses(p, 'Spacer'))}),
            ('bool', 'molding_crown_furniture_cap', "Furniture Cap"),
            ('distance', 'molding_cap_offset', "Height Offset",
             {'when': lambda p: p.molding_crown_furniture_cap}),
            ('distance', 'molding_cap_overhang', "Overhang",
             {'when': lambda p: p.molding_crown_furniture_cap}),
            ('enum', 'molding_cap_profile', "Cap Profile",
             {'when': lambda p: (_has_molding_pack()
                                 and p.molding_crown_furniture_cap)}),
            ('gap', None, None),
            ('label', None, "Base"),
            ('enum', 'molding_base_package', "Package"),
            ('enum', 'molding_base_profile', "Profile",
             {'when': lambda p: (_has_molding_pack()
                                 and p.molding_base_package != 'NONE')}),
            ('bool', 'molding_base_size_override', "Override Size",
             {'when': lambda p: p.molding_base_package != 'NONE'}),
            ('distance', 'molding_base_height', "Height",
             {'when': lambda p: (p.molding_base_package != 'NONE'
                                 and p.molding_base_size_override)}),
            ('distance', 'molding_base_thickness', "Thickness",
             {'when': lambda p: (p.molding_base_package != 'NONE'
                                 and p.molding_base_size_override)}),
            # The shoe is independent of the package: alone it runs at
            # the kick face, with a package it applies to its front.
            ('bool', 'molding_base_shoe', "Base Shoe"),
            ('bool', 'molding_base_include_recessed',
             "Include Recessed Toe Kicks",
             {'when': lambda p: (p.molding_base_package != 'NONE'
                                 or p.molding_base_shoe)}),
            ('gap', None, None),
            ('label', None, "Light Rail"),
            ('enum', 'molding_light_rail_package', "Package"),
            ('enum', 'molding_light_rail_profile', "Profile",
             {'when': lambda p: (_has_molding_pack()
                                 and p.molding_light_rail_package
                                 != 'NONE')}),
        ),
        'actions': (
            (("Refresh Molding", 'home_builder.refresh_room_molding'),),
        ),
    },
}


def place(context, product):
    """Put one product in the scene -- the same operator the sidebar's
    library buttons fire, so there is no second placement path."""
    bpy.ops.hb_face_frame.draw_cabinet(
        'INVOKE_DEFAULT', cabinet_name=product['key'])


def draw_path(context, product):
    """Draw a run of the product through clicked points. Only offered
    for products whose ``path_draw`` is set."""
    bpy.ops.hb_face_frame.draw_product_path(
        'INVOKE_DEFAULT', cabinet_name=product['key'])
