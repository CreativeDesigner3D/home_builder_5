"""Face frame cabinets on the viewport panel's SELECTED tab.

Picking a cabinet, a bay or an opening shows it there, in the place the
panel already sits, instead of in a dialog that opens wherever the
cursor happens to be. The page reads down from the cabinet to what is
picked -- Cabinet > Bay 2 > Opening 1 -- and the part picked is the
section that starts open; the ones above it fold under a header
summarising them.

Only the settings reached for most are fields here, edited in place.
Everything else stays in the dialogs, which already draw it all: each
section ends with the commands that open them, so the page is the
quick way in and the dialogs remain the whole form.
"""

import bpy

from . import types_face_frame
from ... import units


SOURCE_KEY = 'FACE_FRAME'

# Section keys: the open/folded state is remembered per kind, so a bay
# page looks the same from one bay to the next.
CABINET_GROUP = 'ff_cabinet'
BAY_GROUP = 'ff_bay'
OPENING_GROUP = 'ff_opening'

_last_kind = None       # the part the page last opened on

# Products with their own forms (and no cabinet carcass) keep them:
# their pages are selected_products'.
_OWN_FORMS = ('IS_LEG_PRODUCT', 'IS_FLOATING_SHELF', 'IS_END_SHELVES',
              'IS_MANTLE_PRODUCT', 'IS_VALANCE_PRODUCT',
              'IS_COLUMN_BEAM_PRODUCT')


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, root, bay_obj, opening_obj) for a picked face frame
    cabinet or part of one, or None. `kind` is the part the page opens
    on: 'cabinet', 'bay' or 'opening'."""
    from . import ui_face_frame
    sel = ui_face_frame.find_active_selection(context)
    kind = sel[0]
    if kind == 'none':
        return None
    root = sel[-1]
    if root is None or any(root.get(tag) for tag in _OWN_FORMS):
        return None
    if kind == 'bay':
        return ('bay', root, sel[1], None)
    if kind in ('opening', 'interior_region'):
        opening = sel[1] if kind == 'opening' else sel[2]
        return ('opening', root, _owning_bay(opening), opening)
    return ('cabinet', root, None, None)


# ---- Several picked at once -------------------------------------------------
# Picking five cabinets and typing a depth sets all five. The page shows
# the active one; the others of the same kind in the selection are its
# peers, which the field engine reads for "Mixed" and writes along with
# it. Gathered once per page build -- the engine asks for every field.

_PEER_PATHS = ('face_frame_cabinet', 'face_frame_bay', 'face_frame_opening')
_picked = {}            # property path -> [objects], from the last build


def _gather(context):
    roots, bays, openings = [], [], []
    for obj in context.selected_objects:
        if obj.get(types_face_frame.TAG_BAY_CAGE):
            bays.append(obj)
        elif obj.get(types_face_frame.TAG_OPENING_CAGE):
            openings.append(obj)
        root = types_face_frame.find_cabinet_root(obj)
        if (root is not None and root not in roots
                and not any(root.get(tag) for tag in _OWN_FORMS)):
            roots.append(root)
    _picked.clear()
    _picked.update({'face_frame_cabinet': roots, 'face_frame_bay': bays,
                    'face_frame_opening': openings})


def _peers(owner):
    """The other picked parts of the owner's kind -- none unless the
    owner is itself one of the picked."""
    try:
        path = owner.path_from_id()
        obj = owner.id_data
    except Exception:
        return ()
    if path not in _PEER_PATHS:
        return ()
    objs = _picked.get(path, ())
    out = []
    try:
        if obj not in objs:
            return ()
        for other in objs:
            if other != obj:
                out.append(getattr(other, path))
    except ReferenceError:
        return ()           # one was deleted since the page was built
    return out


def _count(path):
    return len(_picked.get(path, ()))


def _owning_bay(obj):
    """The bay cage above an opening. An opening made by a split sits
    under its split node, not directly under the bay."""
    while obj is not None:
        if obj.get(types_face_frame.TAG_BAY_CAGE):
            return obj
        obj = obj.parent
    return None


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _cab_type(owner):
    """The cabinet type of whatever cabinet `owner` belongs to."""
    root = types_face_frame.find_cabinet_root(owner.id_data)
    return root.face_frame_cabinet.cabinet_type if root is not None else ''


def _has_kick(owner):
    return _cab_type(owner) in ('BASE', 'TALL', 'LAP_DRAWER')


def _cabinet_summary(cab):
    return f"{_dist(cab.width)} x {_dist(cab.height)} x {_dist(cab.depth)}"


def _bay_summary(bp):
    return f"{_dist(bp.width)} x {_dist(bp.height)}"


def _opening_summary(op):
    item = next((label for ident, label in _enum_pairs(op, 'front_type')
                 if ident == op.front_type), op.front_type)
    return item


def _enum_pairs(owner, prop):
    try:
        return [(i.identifier, i.name)
                for i in owner.bl_rna.properties[prop].enum_items]
    except Exception:
        return []


def _no_corner(cab):
    return cab.corner_type == 'NONE'


def _corner(cab):
    return cab.corner_type != 'NONE'


def _pie_cut(cab):
    return cab.corner_type == 'PIE_CUT'


def _diagonal(cab):
    return cab.corner_type == 'DIAGONAL'


def _corner_interior(cab):
    return cab.corner_type in ('PIE_CUT', 'DIAGONAL')


def _raised(cab):
    """Uppers, and anything already lifted off the floor."""
    return (cab.cabinet_type == 'UPPER'
            or abs(cab.id_data.location.z) > 0.001)


def _scribes(cab):
    return types_face_frame.shows_scribe_options(cab.id_data)


def _is_type(*types):
    return lambda owner: _cab_type(owner) in types


def _is_door(op):
    return op.front_type == 'DOOR'


def _hinged(op):
    return op.front_type in ('DOOR', 'PULLOUT')


def _drawer_look(op):
    return op.front_type in ('DOOR', 'DRAWER_FRONT')


def _apron(op):
    return op.front_type == 'DOOR' and op.add_apron


def _false_front(op):
    return op.front_type == 'FALSE_FRONT'


def _inset_panel(op):
    return op.front_type == 'INSET_PANEL'


def _opening_root_size(op):
    """The height of a bay's root opening, which the bay sets: read
    only. None for a split child, whose size is its own field."""
    from . import ui_face_frame
    size = ui_face_frame._root_opening_size(op.id_data)
    return None if size is None else _dist(size)


def _split_child(op):
    return _opening_root_size(op) is None


def _cabinets_selected(_owner):
    return _count('face_frame_cabinet') >= 2


def _one_cabinet(owner):
    return not _cabinets_selected(owner)


def _one_plain(cab):
    """One cabinet, not a corner: what Duplicate copies."""
    return _no_corner(cab) and _one_cabinet(cab)


def _blind(cab):
    root = cab.id_data
    return ('HB_BLIND_VOID_LEFT' in root or 'HB_BLIND_VOID_RIGHT' in root
            or 'HB_BLIND_PAIR' in root
            or cab.left_stile_type == 'BLIND'
            or cab.right_stile_type == 'BLIND')


def _wedge(cab):
    from .operators import ops_wedge
    return ops_wedge.is_wedge_cabinet(cab.id_data)


def _corner_opening(cab):
    from . import types_face_frame_corner
    return types_face_frame_corner.corner_opening_root(cab.id_data) is not None


def _has_bay_presets(bp):
    from . import bay_presets
    return _cab_type(bp) in bay_presets.MENU_ENTRIES


def _accessories(_op):
    from ... import accessory_registry
    return accessory_registry.available()


def _cabinet_style(cab):
    """(index, style) of the cabinet style the cabinet carries, or
    (-1, None)."""
    from . import props_hb_face_frame
    name = cab.id_data.get('STYLE_NAME')
    for i, cs in enumerate(props_hb_face_frame.get_style_props().cabinet_styles):
        if cs.name == name:
            return i, cs
    return -1, None


def _has_styles(_cab):
    from . import props_hb_face_frame
    return len(props_hb_face_frame.get_style_props().cabinet_styles) > 0


def _style_color(cab):
    """The colour the style paints its cabinets with Style Colors on."""
    from . import props_hb_face_frame as pf
    i, cs = _cabinet_style(cab)
    if cs is None:
        return None
    return pf.style_viewport_color(pf.style_palette_color(i))


def _style_details(cab):
    """What the style is, read on hover: species and finish, then the
    door and drawer fronts it puts on."""
    cs = _cabinet_style(cab)[1]
    if cs is None:
        return "No style assigned"
    from .library_catalog import _join, _value
    parts = [_join(_value(cs, 'finish_wood', 'ss_wood'),
                   _value(cs, 'finish_color', 'ss_color'))]
    door = _value(cs, 'door_style')
    drawer = _value(cs, 'drawer_front_style')
    if door:
        parts.append("Door: " + door)
    if drawer:
        parts.append("Drawer: " + drawer)
    return " · ".join(p for p in parts if p)


def _menu(icon, label, menu_id, when=None):
    """An icon that drops down one of the right-click menu's own preset
    lists."""
    return (icon, label, 'wm.call_menu', {'name': menu_id}, when)


# ---- Fields -----------------------------------------------------------------
# Each section: the settings changed on nearly every cabinet, then the
# rest of the everyday ones under folds of their own, then a row of
# icon commands. Anything destructive or rare stays on the right-click
# menu, and the last icon opens the full dialog.

def _cabinet_fields(root):
    name = root.name
    return (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height_above_floor', "Above Floor", {'when': _raised}),
        ('choices', 'anchor_side', "Anchor", {'cols': 3, 'when': _no_corner}),
        ('group', 'ff_cab_corner', "Corner", {'icon': 'cab_corner', 'when': _corner, 'fields': (
            ('locked', 'left_depth', "Left Depth", {'unlock': 'unlock_left_depth'}),
            ('locked', 'right_depth', "Right Depth", {'unlock': 'unlock_right_depth'}),
            ('enum', 'exterior_option', "Door Swing", {'when': _pie_cut}),
            ('enum', 'diag_door_swing', "Door Swing", {'when': _diagonal}),
            ('enum', 'interior_option', "Interior", {'when': _corner_interior}),
        )}),
        ('group', 'ff_cab_construction', "Construction", {'icon': 'cab_construction', 'fields': (
            ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
            ('distance', 'toe_kick_height', "Kick Height", {'when': _has_kick}),
            ('distance', 'toe_kick_setback', "Kick Setback", {'when': _has_kick}),
            ('enum', 'left_finished_end_condition', "Left End"),
            ('enum', 'right_finished_end_condition', "Right End"),
            ('enum', 'back_finished_end_condition', "Back"),
            ('bool', 'existing_cabinet', "Existing (on site)"),
        )}),
        ('group', 'ff_cab_face_frame', "Face Frame", {'icon': 'cab_face_frame', 'fields': (
            ('locked', 'top_rail_width', "Top Rail", {'unlock': 'unlock_top_rail'}),
            ('locked', 'bottom_rail_width', "Bottom Rail", {'unlock': 'unlock_bottom_rail'}),
            ('locked', 'left_stile_width', "Left Stile", {'unlock': 'unlock_left_stile'}),
            ('locked', 'right_stile_width', "Right Stile", {'unlock': 'unlock_right_stile'}),
            ('distance', 'left_scribe', "Left Scribe", {'when': _scribes}),
            ('distance', 'right_scribe', "Right Scribe", {'when': _scribes}),
            ('distance', 'top_scribe', "Top Scribe", {'when': _scribes}),
            ('bool', 'extend_left_stile_to_floor', "Left Stile to Floor", {'when': _has_kick}),
            ('bool', 'extend_right_stile_to_floor', "Right Stile to Floor", {'when': _has_kick}),
        )}),
        ('icons', (
            ('duplicate', "Duplicate", 'hb_face_frame.place_cabinet',
             {'source_cabinet_name': name}, _one_plain),
            ('cab_mirror', "Duplicate Mirror", 'hb_face_frame.place_cabinet',
             {'source_cabinet_name': name, 'mirror': True}, _one_plain),
            ('cab_equalize_bays', "Equalize Bays", 'hb_face_frame.equalize_bays'),
            ('cab_join', "Join Cabinets", 'hb_face_frame.join_cabinets',
             None, _cabinets_selected),
            _menu('cab_change_opening', "Change Opening",
                  'HOME_BUILDER_MT_face_frame_corner_change_opening', _corner_opening),
            ('cab_blind', "Blind Corner", 'hb_face_frame.edit_blind_corner',
             None, _blind),
            ('cab_swap_blind', "Swap Blind", 'hb_face_frame.swap_blind_corner',
             None, _blind),
            ('cab_wedge', "Wedge Calculator", 'hb_face_frame.add_refrigerator_wedge',
             None, _wedge),
            ('settings', "All Cabinet Settings", 'hb_face_frame.cabinet_prompts'),
        ), ""),
    )


def _bay_fields(bay_obj, picked):
    index = bay_obj.face_frame_bay.bay_index
    fields = [
        ('locked', 'width', "Width", {'unlock': 'unlock_width'}),
        ('locked', 'height', "Height", {'unlock': 'unlock_height'}),
        ('locked', 'depth', "Depth", {'unlock': 'unlock_depth'}),
        ('locked', 'kick_height', "Kick Height",
         {'unlock': 'unlock_kick_height', 'when': _has_kick}),
        ('enum', 'back_condition', "Back"),
        ('group', 'ff_bay_more', "More", {'fields': (
            ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
            ('distance', 'top_offset', "Top Offset", {'when': _is_type('UPPER')}),
            ('bool', 'appliance_garage', "Appliance Garage", {'when': _is_type('UPPER')}),
            ('distance', 'front_drop', "Front Drop", {'when': _is_type('BASE', 'LAP_DRAWER')}),
            ('bool', 'bread_board', "Bread Board", {'when': _is_type('BASE')}),
            ('enum', 'bottom_rail_profile', "Bottom Rail",
             {'when': _is_type('BASE', 'UPPER')}),
            ('bool', 'remove_bottom', "Remove Bottom"),
            ('bool', 'remove_carcass', "Remove Carcass"),
        )}),
    ]
    icons = [
        ('cab_insert_before', "Insert Bay Before", 'hb_face_frame.insert_bay',
         {'bay_index': index, 'direction': 'BEFORE'}),
        ('cab_insert_after', "Insert Bay After", 'hb_face_frame.insert_bay',
         {'bay_index': index, 'direction': 'AFTER'}),
    ]
    # The bay's own commands act on the active object, so they are only
    # offered when the bay itself is what is picked.
    if picked:
        icons.extend((
            _menu('cab_change_bay', "Change Bay",
                  'HOME_BUILDER_MT_face_frame_change_bay', _has_bay_presets),
            ('cab_equal_doors', "Equal Door Width", 'hb_face_frame.set_equal_door_width'),
            ('cab_flush_kick', "Flush Toe Kick", 'hb_face_frame.toggle_flush_toe_kick',
             None, _is_type('BASE', 'TALL')),
            ('brush', "Finish Bay", 'hb_face_frame.finish_bay_prompts'),
            ('settings', "All Bay Settings", 'hb_face_frame.bay_prompts'),
        ))
    fields.append(('icons', tuple(icons), ""))
    return tuple(fields)


def _opening_fields():
    return (
        ('value', _opening_root_size, "Size"),
        ('locked', 'size', "Size",
         {'unlock': 'unlock_size', 'when': _split_child}),
        ('enum', 'front_type', "Front"),
        ('enum', 'hinge_side', "Hinge Side", {'when': _hinged}),
        ('enum', 'door_mechanism', "Mechanism", {'when': _is_door}),
        ('group', 'ff_opening_more', "More", {'fields': (
            ('bool', 'add_apron', "Add Apron", {'when': _is_door}),
            ('distance', 'apron_height', "Apron Height", {'when': _apron}),
            ('enum', 'drawer_look_divisions', "Drawer-Look", {'when': _drawer_look}),
            ('enum', 'door_look_divisions', "Door-Look", {'when': _is_door}),
            ('bool', 'is_tilt_out', "Tilt-Out", {'when': _false_front}),
            ('bool', 'false_front_pull', "Add Pull", {'when': _false_front}),
            ('enum', 'inset_panel_type', "Panel Type", {'when': _inset_panel}),
        )}),
        ('icons', (
            _menu('cab_change_opening', "Change Opening",
                  'HOME_BUILDER_MT_face_frame_change_opening'),
            ('cab_equalize_heights', "Equalize Heights",
             'hb_face_frame.equalize_opening_heights'),
            ('cab_split_h', "Split Horizontal", 'hb_face_frame.split_opening',
             {'axis': 'H'}),
            ('cab_split_v', "Split Vertical", 'hb_face_frame.split_opening',
             {'axis': 'V'}),
            ('cab_interior', "Interior", 'hb_face_frame.interior_options'),
            ('brush', "Finish", 'hb_face_frame.finish_opening_prompts'),
            ('cab_accessories', "Accessories", 'hb_face_frame.accessory_menu',
             None, _accessories),
            ('settings', "All Opening Settings", 'hb_face_frame.opening_prompts'),
        ), ""),
    )


# ---- The page ---------------------------------------------------------------

def _fold_for(context, kind):
    """Open the picked part's section and fold the others, each time the
    page moves to a different kind of part. While the same kind stays
    picked, whatever the user opened or folded stays that way."""
    global _last_kind
    if kind == _last_kind:
        return
    _last_kind = kind
    from ...operators import options_panel
    primary = {'cabinet': CABINET_GROUP, 'bay': BAY_GROUP,
               'opening': OPENING_GROUP}[kind]
    for key in (CABINET_GROUP, BAY_GROUP, OPENING_GROUP):
        method = 'group:' + key
        if bool(options_panel.section_expanded(context, method)) != (key == primary):
            options_panel.toggle_section(context, method)


def blocks(context, item):
    from ...operators import options_panel
    kind, root, bay_obj, opening_obj = item
    cab = root.face_frame_cabinet
    _gather(context)
    n_cab = _count('face_frame_cabinet')
    n_part = _count({'bay': 'face_frame_bay',
                     'opening': 'face_frame_opening'}.get(kind, ''))

    trail = ["Cabinet"]
    if bay_obj is not None:
        trail.append(f"Bay {bay_obj.face_frame_bay.bay_index + 1}")
    if opening_obj is not None:
        trail.append(f"Opening {opening_obj.face_frame_opening.opening_index + 1}")

    # Several picked: the page says how many, and that an edit is to all.
    # One picked: the head is where it sits, said once.
    if kind == 'cabinet' and n_cab > 1:
        out = [('head', (f"{n_cab} Cabinets", False, None)),
               ('label', f"Changes apply to all {n_cab}")]
    elif kind in ('bay', 'opening') and n_part > 1:
        out = [('head', (f"{n_part} {kind.title()}s", False, None)),
               ('label', f"Changes apply to all {n_part}")]
    else:
        out = [('head', (" \u203a ".join([root.name] + trail[1:]), False, None))]

    _fold_for(context, kind)

    # The style section leads, whatever part is picked: it is the
    # cabinet's, and switching it here saves a trip to Options.
    out.extend(options_panel.field_blocks(context, (
        ('enum', 'style_section', "Style",
         {'when': _has_styles, 'color': _style_color, 'tip': _style_details}),
    ), cab))

    if n_cab > 1:
        types = {r.face_frame_cabinet.cabinet_type
                 for r in _picked['face_frame_cabinet']}
        cab_label = (f"{n_cab} Cabinets  ({cab.cabinet_type.title()})"
                     if len(types) == 1 else f"{n_cab} Cabinets  (Mixed)")
    else:
        cab_label = f"Cabinet  ({cab.cabinet_type.title()})"
    out.extend(options_panel.field_blocks(context, (
        ('group', CABINET_GROUP, cab_label,
         {'icon': 'cab_cabinet', 'summary': _cabinet_summary, 'fields': _cabinet_fields(root)}),
    ), cab))
    if bay_obj is not None:
        bp = bay_obj.face_frame_bay
        label = f"{n_part} Bays" if kind == 'bay' and n_part > 1 else trail[1]
        out.extend(options_panel.field_blocks(context, (
            ('group', BAY_GROUP, label,
             {'icon': 'cab_bay', 'summary': _bay_summary,
              'fields': _bay_fields(bay_obj, kind == 'bay')}),
        ), bp))
    if opening_obj is not None:
        op = opening_obj.face_frame_opening
        label = (f"{n_part} Openings" if kind == 'opening' and n_part > 1
                 else trail[-1])
        out.extend(options_panel.field_blocks(context, (
            ('group', OPENING_GROUP, label,
             {'icon': 'cab_opening', 'summary': _opening_summary, 'fields': _opening_fields()}),
        ), op))
    return out


def crumbs(context, item):
    """Cabinet, bay, opening: each step above the pick selects that
    level. None while several are picked -- the head says how many."""
    kind, root, bay_obj, opening_obj = item
    _gather(context)
    if _count('face_frame_cabinet') > 1 or (
            kind in ('bay', 'opening') and _count(
                'face_frame_bay' if kind == 'bay' else 'face_frame_opening') > 1):
        return None
    op = 'hb_face_frame.select_level'
    out = [(root.name, (op, {'name': root.name, 'level': 'Cabinets'}))]
    if bay_obj is not None:
        out.append((f"Bay {bay_obj.face_frame_bay.bay_index + 1}",
                    (op, {'name': bay_obj.name, 'level': 'Bays'})))
    if opening_obj is not None:
        out.append((f"Opening {opening_obj.face_frame_opening.opening_index + 1}",
                    (op, {'name': opening_obj.name, 'level': 'Openings'})))
    # The last is the pick itself: named, not a click.
    out[-1] = (out[-1][0], None)
    return out


# ---- Lifecycle --------------------------------------------------------------

def register():
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)
    from ...operators import options_panel
    options_panel.register_peers(_peers)


def unregister():
    try:
        from ...operators import options_panel, selected_tab
        options_panel.unregister_peers(_peers)
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
