"""Face frame cabinets on the viewport panel's SELECTED tab.

Picking a cabinet, a bay or an opening shows it there, in the place the
panel already sits, instead of in a dialog that opens wherever the
cursor happens to be. The page reads down from the cabinet to what is
picked -- Cabinet > Bay 2 > Opening 1 -- and the part picked is the
section that starts open; the ones above it fold under a header
summarising them.

Tabs under the style move between the cabinet and the bay, opening and
part picked inside it. Each level's page leads with its size and its
quick actions, labelled rather than drawn as icons; the rest of its
settings fold under headers that say what is set. Every command of the
level's right-click menu is a click away under All Actions, and
Properties opens the full dialog.
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

PART_MENU = 'HOME_BUILDER_MT_face_frame_part_commands'

# Products with their own forms (and no cabinet carcass) keep them:
# their pages are selected_products'.
_OWN_FORMS = ('IS_LEG_PRODUCT', 'IS_FLOATING_SHELF', 'IS_END_SHELVES',
              'IS_MANTLE_PRODUCT', 'IS_VALANCE_PRODUCT',
              'IS_COLUMN_BEAM_PRODUCT')


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, root, bay_obj, opening_obj, part_obj) for a picked face
    frame cabinet or part of one, or None. `kind` is the level the page
    is on: 'cabinet', 'bay', 'opening' or 'part' -- a door, a stile, a
    rail, anything inside with a right-click menu of its own."""
    from . import ui_face_frame
    from ...operators import generic_page
    sel = ui_face_frame.find_active_selection(context)
    kind = sel[0]
    if kind == 'none':
        return None
    root = sel[-1]
    if root is None or any(root.get(tag) for tag in _OWN_FORMS):
        return None
    if kind == 'bay':
        return ('bay', root, sel[1], None, None)
    if kind in ('opening', 'interior_region'):
        opening = sel[1] if kind == 'opening' else sel[2]
        return ('opening', root, _owning_bay(opening), opening, None)
    if kind != 'cabinet':
        part = sel[1]
        if generic_page.menu_id(part) == PART_MENU:
            opening = _owning(part, types_face_frame.TAG_OPENING_CAGE)
            return ('part', root, _owning_bay(part), opening, part)
    return ('cabinet', root, None, None, None)


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


def _cabinet_style(owner):
    """(index, style) of the cabinet style the owner's pick carries, or
    (-1, None). The owner is a cabinet's face_frame_cabinet, or the
    object itself for a styled pick that is not a cabinet."""
    from . import props_hb_face_frame
    name = props_hb_face_frame._style_holder(owner).get('STYLE_NAME')
    for i, cs in enumerate(props_hb_face_frame.get_style_props().cabinet_styles):
        if cs.name == name:
            return i, cs
    return -1, None


def _has_styles(owner):
    """Styles to pick from, and a pick a style goes on."""
    from . import props_hb_face_frame as pf
    if not len(pf.get_style_props().cabinet_styles):
        return False
    if not isinstance(owner, bpy.types.Object):
        return True             # a cabinet
    # A part on a cabinet (a wood top on its base) takes the cabinet's
    # style; its own page must not offer to restyle the cabinet.
    target = pf.style_target(owner)
    return target is not None and target[1] == owner


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


def _style_settings(owner):
    """The chip that opens the style's everyday settings."""
    cs = _cabinet_style(owner)[1]
    if cs is None:
        return None
    return ('hb_face_frame.style_quick_settings', {'style_name': cs.name},
            'settings', "Style Settings")


def style_blocks(context, owner, prop='style_section'):
    """The style section row: which style the pick carries, switched in
    place, with its everyday settings a click away. `owner` is a
    cabinet's face_frame_cabinet (prop 'style_section') or a styled
    object that is not a cabinet (prop 'hb_style_section'). Nothing
    while the project has no styles."""
    from ...operators import options_panel
    return options_panel.field_blocks(context, (
        ('enum', prop, "Style",
         {'when': _has_styles, 'color': _style_color, 'tip': _style_details,
          'action': _style_settings}),
    ), owner)


def _menu(label, menu_id):
    """A button that drops down one of the right-click menu's own
    lists, the way the menu's submenu does."""
    from ...operators import generic_page
    return (label + "  ›", generic_page._opener(menu_id, label), None, None)


def _act(label, op_id, kwargs=None):
    return (label, op_id, dict(kwargs or {}), None)


def _quick(owner, candidates, limit=6):
    """The quick actions a page leads with: the first `limit` of
    (action, when) that apply, two to a row so each reads in full.
    Every one is also on the right-click menu, and so in All Actions."""
    picked = []
    for action, when in candidates:
        try:
            if when is not None and not when(owner):
                continue
        except Exception:
            continue
        picked.append(action)
        if len(picked) == limit:
            break
    rows = [('actions', tuple(picked[i:i + 2]), None)
            for i in range(0, len(picked), 2)]
    return (('label', None, "Quick Actions"),) + tuple(rows) if rows else ()


# ---- Summaries of the folded groups ----------------------------------------

def _label_of(owner, prop):
    value = getattr(owner, prop, '')
    return next((label for ident, label in _enum_pairs(owner, prop)
                 if ident == value), str(value))


def _construction_summary(cab):
    parts = []
    if _has_kick(cab):
        parts.append(f"{_dist(cab.toe_kick_height)} kick")
    if cab.existing_cabinet:
        parts.append("Existing")
    return " · ".join(parts)


def _ends_summary(cab):
    ends = [side for side, prop in (("Left", 'left_finished_end_condition'),
                                    ("Right", 'right_finished_end_condition'),
                                    ("Back", 'back_finished_end_condition'))
            if getattr(cab, prop, 'UNFINISHED') != 'UNFINISHED']
    return ", ".join(ends) + " finished" if ends else "Unfinished"


def _frame_summary(cab):
    return f"{_dist(cab.left_stile_width)} stiles"


def _bay_details_summary(bp):
    return _label_of(bp, 'toe_kick_type') if _has_kick(bp) else ""


# ---- Fields -----------------------------------------------------------------
# Each scope: its size, then the quick actions, then everything else in
# folds that say what is set in them. Every command -- the quick ones and
# the rest -- is in All Actions at the foot of the page.

def _cabinet_fields(root, cab):
    name = root.name
    quick = _quick(cab, (
        (_act("Duplicate", 'hb_face_frame.place_cabinet',
              {'source_cabinet_name': name}), _one_plain),
        (_act("Duplicate Mirror", 'hb_face_frame.place_cabinet',
              {'source_cabinet_name': name, 'mirror': True}), _one_plain),
        (_act("Join Cabinets", 'hb_face_frame.join_cabinets'), _cabinets_selected),
        (_menu("Change Opening", 'HOME_BUILDER_MT_face_frame_corner_change_opening'),
         _corner_opening),
        (_act("Blind Corner", 'hb_face_frame.edit_blind_corner'), _blind),
        (_act("Swap Blind", 'hb_face_frame.swap_blind_corner'), _blind),
        (_act("Copy Cabinet", 'home_builder.copy_cabinet'), _one_plain),
        (_act("Equalize Bays", 'hb_face_frame.equalize_bays'), None),
        (_act("Wedge Calculator", 'hb_face_frame.add_refrigerator_wedge'), _wedge),
        (_act("Hide Cabinet", 'hb_general.hide',
              {'scope': 'PRODUCT', 'isolate': False}), None),
    ))
    return (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height_above_floor', "Above Floor", {'when': _raised}),
        ('choices', 'anchor_side', "Anchor", {'cols': 3, 'when': _no_corner}),
        ('gap', None, None),
    ) + quick + (
        ('gap', None, None),
        ('group', 'ff_cab_corner', "Corner", {'icon': 'cab_corner', 'when': _corner, 'fields': (
            ('locked', 'left_depth', "Left Depth", {'unlock': 'unlock_left_depth'}),
            ('locked', 'right_depth', "Right Depth", {'unlock': 'unlock_right_depth'}),
            ('enum', 'exterior_option', "Door Swing", {'when': _pie_cut}),
            ('enum', 'diag_door_swing', "Door Swing", {'when': _diagonal}),
            ('enum', 'interior_option', "Interior", {'when': _corner_interior}),
        )}),
        ('group', 'ff_cab_construction', "Construction", {
            'icon': 'cab_construction', 'summary': _construction_summary, 'fields': (
                ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
                ('distance', 'toe_kick_height', "Kick Height", {'when': _has_kick}),
                ('distance', 'toe_kick_setback', "Kick Setback", {'when': _has_kick}),
                ('bool', 'existing_cabinet', "Existing (on site)"),
            )}),
        ('group', 'ff_cab_ends', "Finished Ends & Back", {
            'summary': _ends_summary, 'fields': (
                ('enum', 'left_finished_end_condition', "Left End"),
                ('enum', 'right_finished_end_condition', "Right End"),
                ('enum', 'back_finished_end_condition', "Back"),
            )}),
        ('group', 'ff_cab_face_frame', "Face Frame", {
            'icon': 'cab_face_frame', 'summary': _frame_summary, 'fields': (
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
    )


def _bay_fields(bay_obj, bp):
    index = bp.bay_index
    quick = _quick(bp, (
        (_menu("Change Bay", 'HOME_BUILDER_MT_face_frame_change_bay'),
         _has_bay_presets),
        (_act("Insert Bay Before", 'hb_face_frame.insert_bay',
              {'bay_index': index, 'direction': 'BEFORE'}), None),
        (_act("Insert Bay After", 'hb_face_frame.insert_bay',
              {'bay_index': index, 'direction': 'AFTER'}), None),
        (_act("Equal Door Width", 'hb_face_frame.set_equal_door_width'), None),
        (_act("Finish Bay", 'hb_face_frame.finish_bay_prompts'), None),
        (_act("Flush Toe Kick", 'hb_face_frame.toggle_flush_toe_kick'),
         _is_type('BASE', 'TALL')),
    ))
    return (
        ('locked', 'width', "Width", {'unlock': 'unlock_width'}),
        ('locked', 'height', "Height", {'unlock': 'unlock_height'}),
        ('locked', 'depth', "Depth", {'unlock': 'unlock_depth'}),
        ('locked', 'kick_height', "Kick Height",
         {'unlock': 'unlock_kick_height', 'when': _has_kick}),
        ('enum', 'back_condition', "Back"),
        ('gap', None, None),
    ) + quick + (
        ('gap', None, None),
        ('group', 'ff_bay_more', "Bay Details", {
            'summary': _bay_details_summary, 'fields': (
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
    )


def _opening_fields(op):
    quick = _quick(op, (
        (_menu("Change Opening", 'HOME_BUILDER_MT_face_frame_change_opening'), None),
        (_act("Interior Options", 'hb_face_frame.interior_options'), None),
        (_act("Split Horizontal", 'hb_face_frame.split_opening', {'axis': 'H'}), None),
        (_act("Split Vertical", 'hb_face_frame.split_opening', {'axis': 'V'}), None),
        (_act("Equalize Heights", 'hb_face_frame.equalize_opening_heights'), None),
        (_act("Accessories", 'hb_face_frame.accessory_menu'), _accessories),
        (_act("Finish Opening", 'hb_face_frame.finish_opening_prompts'), None),
    ))
    return (
        ('value', _opening_root_size, "Size"),
        ('locked', 'size', "Size",
         {'unlock': 'unlock_size', 'when': _split_child}),
        ('enum', 'front_type', "Front"),
        ('enum', 'hinge_side', "Hinge Side", {'when': _hinged}),
        ('enum', 'door_mechanism', "Mechanism", {'when': _is_door}),
        ('gap', None, None),
    ) + quick + (
        ('gap', None, None),
        ('group', 'ff_opening_more', "Front Details", {
            'summary': _opening_summary, 'fields': (
                ('bool', 'add_apron', "Add Apron", {'when': _is_door}),
                ('distance', 'apron_height', "Apron Height", {'when': _apron}),
                ('enum', 'drawer_look_divisions', "Drawer-Look", {'when': _drawer_look}),
                ('enum', 'door_look_divisions', "Door-Look", {'when': _is_door}),
                ('bool', 'is_tilt_out', "Tilt-Out", {'when': _false_front}),
                ('bool', 'false_front_pull', "Add Pull", {'when': _false_front}),
                ('enum', 'inset_panel_type', "Panel Type", {'when': _inset_panel}),
            )}),
    )


def _part_blocks(context, part_obj):
    """A picked face frame part (a door, a stile, a rail): its size, and
    the first commands of its own right-click menu as quick actions. The
    rest are in All Actions."""
    from ...operators import generic_page
    out = []
    size = generic_page._size_text(context, part_obj)
    if not size and any(part_obj.dimensions):
        us = context.scene.unit_settings
        size = "  x  ".join(units.unit_to_string(us, d)
                            for d in part_obj.dimensions)
    if size:
        out.append(('value', ("Size (W x D x H)", size)))
    picked = []
    for rec in generic_page._record(context, generic_page.menu_id(part_obj)):
        if rec[0] == 'op':
            label = (rec[1] or generic_page._op_label(rec[2])).rstrip('.')
            picked.append((label, rec[2], dict(rec[3]._values), None))
        elif rec[0] == 'menu':
            picked.append(_menu(rec[1] or generic_page._menu_label(rec[2]),
                                rec[2]))
        if len(picked) == 6:
            break
    if picked:
        if out:
            out.append(('gap', None))
        out.append(('label', "Quick Actions"))
        for i in range(0, len(picked), 2):
            out.append(('actions', tuple(picked[i:i + 2])))
    return out


# ---- Scope: which level of the cabinet the page is on ----------------------
# The tabs under the style move between the cabinet and the bay, opening
# and part last picked inside it, selecting that level the way the
# breadcrumb does -- so a bay's page is one click from its cabinet's and
# back, without finding the bay in the viewport again.

LEVELS = ('Cabinets', 'Bays', 'Openings', 'Parts')
_chain = {}             # cabinet name -> {level: object name}
_scope_now = 'Cabinets'


def _owning(obj, tag):
    while obj is not None:
        if obj.get(tag):
            return obj
        obj = obj.parent
    return None


def _part_label(part_obj):
    role = str(part_obj.get('hb_part_role', '') or '')
    if 'DRAWER' in role:
        return "Drawer"
    if 'DOOR' in role:
        return "Door"
    return "Part"


def _remember(root, bay_obj, opening_obj, part_obj):
    """Note the levels picked inside `root`, dropping any remembered
    below a level that has just changed. Returns the picked level."""
    chain = _chain.setdefault(root.name, {})
    picked = {'Cabinets': root, 'Bays': bay_obj, 'Openings': opening_obj,
              'Parts': part_obj}
    deepest = 0
    for i, level in enumerate(LEVELS):
        obj = picked[level]
        if obj is None:
            continue
        deepest = i
        if chain.get(level) != obj.name:
            for lower in LEVELS[i + 1:]:
                if picked[lower] is None:
                    chain.pop(lower, None)
        chain[level] = obj.name
    # What is remembered must still be in this cabinet.
    for level in LEVELS[1:]:
        name = chain.get(level)
        obj = bpy.data.objects.get(name) if name else None
        if obj is None or types_face_frame.find_cabinet_root(obj) != root:
            chain.pop(level, None)
    return LEVELS[deepest]


def _scope_schema(levels, labels):
    from ...operators import prop_proxy
    key = 'FF_SCOPE_' + '_'.join(levels) + '_' + labels[-1]

    def get(_obj):
        return _scope_now

    def set(obj, value):
        name = _chain.get(obj.name, {}).get(value)
        if name:
            bpy.ops.hb_face_frame.select_level(name=name, level=value)
    if key not in prop_proxy._schemas:
        prop_proxy.register(key, {
            'scope': prop_proxy.computed(
                get, set, type='ENUM', items=list(zip(levels, labels))),
        })
    return key


def _scope_blocks(context, root, current):
    """The level tabs: Cabinet, then each level picked inside it."""
    from ...operators import options_panel, prop_proxy
    global _scope_now
    chain = _chain.get(root.name, {})
    levels = [level for level in LEVELS if chain.get(level)]
    if len(levels) < 2:
        return []
    labels = [_part_label(bpy.data.objects[chain[level]]) if level == 'Parts'
              else level[:-1] for level in levels]
    _scope_now = current
    key = _scope_schema(levels, labels)
    return options_panel.field_blocks(context, (
        ('choices', 'scope', "", {'cols': len(levels)}),
    ), prop_proxy.owner(root, key))


def _footer(out, prompts_op):
    row = [("All Actions", 'home_builder.all_actions', None, None)]
    if prompts_op:
        row.append(("Properties…", prompts_op, None, None))
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.append(('actions', tuple(row)))


# ---- The page ---------------------------------------------------------------

def blocks(context, item):
    from ...operators import options_panel
    kind, root, bay_obj, opening_obj, part_obj = item
    cab = root.face_frame_cabinet
    _gather(context)
    n_cab = _count('face_frame_cabinet')
    n_part = _count({'bay': 'face_frame_bay',
                     'opening': 'face_frame_opening'}.get(kind, ''))
    level = _remember(root, bay_obj, opening_obj, part_obj)

    trail = [root.name]
    if bay_obj is not None:
        trail.append(f"Bay {bay_obj.face_frame_bay.bay_index + 1}")
    if opening_obj is not None:
        trail.append(f"Opening {opening_obj.face_frame_opening.opening_index + 1}")
    if part_obj is not None:
        trail.append(part_obj.name)

    # Several picked: the page says how many, and that an edit is to all.
    # One picked: the head is where it sits, said once.
    several = (n_cab > 1 if kind == 'cabinet'
               else kind in ('bay', 'opening') and n_part > 1)
    if kind == 'cabinet' and several:
        out = [('head', (f"{n_cab} Cabinets", False, None)),
               ('label', f"Changes apply to all {n_cab}")]
    elif several:
        out = [('head', (f"{n_part} {kind.title()}s", False, None)),
               ('label', f"Changes apply to all {n_part}")]
    else:
        out = [('head', (" › ".join(trail), False, None))]

    # The style leads, whatever part is picked: it is the cabinet's, and
    # switching it here saves a trip to Options.
    out.extend(style_blocks(context, cab))
    if not several:
        out.extend(_scope_blocks(context, root, level))
    out.append(('gap', None))

    if kind == 'cabinet':
        out.extend(options_panel.field_blocks(
            context, _cabinet_fields(root, cab), cab))
        _footer(out, 'hb_face_frame.cabinet_prompts')
    elif kind == 'bay':
        bp = bay_obj.face_frame_bay
        out.extend(options_panel.field_blocks(
            context, _bay_fields(bay_obj, bp), bp))
        _footer(out, 'hb_face_frame.bay_prompts')
    elif kind == 'opening':
        op = opening_obj.face_frame_opening
        out.extend(options_panel.field_blocks(context, _opening_fields(op), op))
        _footer(out, 'hb_face_frame.opening_prompts')
    else:
        out.extend(_part_blocks(context, part_obj))
        _footer(out, None)
    return out


def crumbs(context, item):
    """Cabinet, bay, opening, part: each step above the pick selects
    that level. None while several are picked -- the head says how
    many."""
    kind, root, bay_obj, opening_obj, part_obj = item
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
    if part_obj is not None:
        out.append((part_obj.name, None))
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
