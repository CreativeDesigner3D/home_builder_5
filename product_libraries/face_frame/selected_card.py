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
from . import part_pages
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
    """The pick, as _find gives it; an Interior page left open on an
    opening closes once the pick is somewhere else."""
    from . import interior_page
    item = _find(context)
    if interior_page._shown_for and (
            item is None or item[3] is None
            or item[3].name != interior_page._shown_for):
        interior_page.show(None)
    return item


def _find(context):
    """(kind, root, bay_obj, opening_obj, part_obj) for a picked face
    frame cabinet or part of one, or None. `kind` is the level the page
    is on: 'cabinet', 'bay', 'opening' or 'part' -- a door, a stile, a
    rail, anything inside with a right-click menu of its own -- or
    'interior': an interior region, an interior part, or an opening
    whose Interior page is open (part_obj is the region or part)."""
    from . import ui_face_frame, interior_page
    from ...operators import generic_page
    # The Interior page on a hidden region or split, while the visible
    # object it keeps as the pick stays picked.
    found = interior_page.focused(context)
    if found is not None:
        opening, region, page = found
        root = types_face_frame.find_cabinet_root(opening)
        if root is not None and page == 'opening':
            return ('opening', root, _owning_bay(opening), opening, None)
        if root is not None:
            return ('interior', root, _owning_bay(opening), opening, region)
    sel = ui_face_frame.find_active_selection(context)
    kind = sel[0]
    if kind == 'none':
        return None
    root = sel[-1]
    if root is None or any(root.get(tag) for tag in _OWN_FORMS):
        return None
    if kind == 'bay':
        return ('bay', root, sel[1], None, None)
    if kind == 'interior_region':
        region, opening = sel[1], sel[2]
        return ('interior', root, _owning_bay(opening), opening, region)
    if kind == 'opening':
        opening = sel[1]
        if interior_page.showing(opening):
            return ('interior', root, _owning_bay(opening), opening, None)
        return ('opening', root, _owning_bay(opening), opening, None)
    if kind != 'cabinet':
        part = sel[1]
        from . import accessory_place
        if accessory_place.is_drawer_box(part):
            # A drawer box has a page of its own: the Drawer page.
            opening = _owning(part, types_face_frame.TAG_OPENING_CAGE)
            return ('drawer', root, _owning_bay(part), opening, part)
        if interior_page.is_interior_part(part):
            # A shelf, a division, anything inside: the Interior page.
            opening = interior_page.opening_of(part)
            if opening is not None:
                return ('interior', root, _owning_bay(part), opening, part)
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
    from ...operators import prop_proxy
    if path == prop_proxy.PATH_PREFIX + OVERLAY_KEY:
        # An opening's overlays are read through a schema, not straight
        # off its properties; its peers are the other picked openings
        # seen the same way.
        try:
            objs = _picked.get('face_frame_opening', ())
            if obj not in objs:
                return ()
            return [prop_proxy.owner(o, OVERLAY_KEY) for o in objs
                    if o != obj]
        except ReferenceError:
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


def _several_bays(bp):
    root = types_face_frame.find_cabinet_root(bp.id_data)
    return root is not None and sum(
        1 for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)) > 1


def _mech(*kinds):
    return lambda op: op.front_type == 'DOOR' and op.door_mechanism in kinds


def _retract_partitions(op):
    return (_mech('RETRACTING', 'RETRACTING_BIFOLD')(op)
            and op.retracting_interior == 'PARTITIONS')


def _retract_box(op):
    return (_mech('RETRACTING', 'RETRACTING_BIFOLD')(op)
            and op.retracting_interior != 'PARTITIONS')


def _retract_shelf(op):
    return (_mech('RETRACTING', 'RETRACTING_BIFOLD')(op)
            and op.retracting_interior == 'COMPONENT_SHELF')


def _swings(op):
    return op.front_type not in ('NONE', 'INSET_PANEL', 'APPLIANCE')


def _single_door(op):
    return op.front_type == 'DOOR' and op.hinge_side in ('LEFT', 'RIGHT')


def _drawer_look_ok(op):
    return _single_door(op) or op.front_type == 'DRAWER_FRONT'


def _drawer_split_ok(op):
    """One drawer front built as several faces side by side: drawer
    fronts on the box construction that takes applied faces, and not
    while the stacked drawer look is on."""
    return (op.front_type == 'DRAWER_FRONT'
            and op.drawer_look_divisions == 'NONE'
            and types_face_frame.drawer_split_look_allowed(op.id_data))


def _drawer_split_on(op):
    return _drawer_split_ok(op) and op.drawer_split_look != 'NONE'


def _door_look_ok(op):
    return ((_single_door(op) and op.drawer_look_divisions == 'NONE')
            or (op.front_type == 'DOOR' and op.hinge_side == 'DOUBLE'))


def _door_look_on(op):
    return (op.front_type == 'DOOR'
            and op.hinge_side in ('LEFT', 'RIGHT', 'DOUBLE')
            and op.door_look_divisions != 'NONE'
            and op.drawer_look_divisions == 'NONE')


def _door_look_layout(op):
    return _door_look_on(op) and op.hinge_side != 'DOUBLE'


def _door_look_top(op):
    return _door_look_on(op) and (op.hinge_side == 'DOUBLE'
                                  or op.door_look_direction == 'STACKED')


def _chase(op):
    if op.front_type not in ('DRAWER_FRONT', 'PULLOUT'):
        return False
    root = types_face_frame.find_cabinet_root(op.id_data)
    return root is not None and getattr(root.face_frame_cabinet,
                                        'chase_enabled', False)


def _appliance(op):
    return op.front_type == 'APPLIANCE'


def _appliance_width_shown(op):
    return _appliance(op) and (op.appliance_fit == 'NOTCH'
                               or op.include_fillers)


def _appliance_width_set(op):
    return _appliance_width_shown(op) and op.set_appliance_width


def _fillers_typed(op):
    return (_appliance_width_shown(op) and not op.set_appliance_width
            and op.appliance_fit != 'NOTCH')


def _notches_typed(op):
    return (_appliance_width_shown(op) and not op.set_appliance_width
            and op.appliance_fit == 'NOTCH')


# An opening's overlays: locked, an overlay is the cabinet's default, so
# the field reads what is built rather than the stored (ignored) value.
OVERLAY_KEY = 'FF_OPENING_OVERLAYS'


def _overlay_owner(opening_obj):
    from ...operators import prop_proxy
    if OVERLAY_KEY not in prop_proxy._schemas:
        def getter(side):
            def get(obj):
                op = obj.face_frame_opening
                if getattr(op, f'unlock_{side}_overlay'):
                    return getattr(op, f'{side}_overlay')
                from . import solver_face_frame
                root = types_face_frame.find_cabinet_root(obj)
                if root is None:
                    return getattr(op, f'{side}_overlay')
                return solver_face_frame.resolved_overlay(
                    root.face_frame_cabinet, op, side)
            return get

        def setter(side):
            def set(obj, value):
                op = obj.face_frame_opening
                # A typed overlay is the opening's own. The picked field
                # is unlocked already; another opening picked with it
                # may not be, and would ignore the value.
                if not getattr(op, f'unlock_{side}_overlay'):
                    setattr(op, f'unlock_{side}_overlay', True)
                setattr(op, f'{side}_overlay', value)
            return set

        def lock_get(side):
            return lambda obj: getattr(obj.face_frame_opening,
                                       f'unlock_{side}_overlay')

        def lock_set(side):
            def set(obj, value):
                op = obj.face_frame_opening
                if value and not getattr(op, f'unlock_{side}_overlay'):
                    # Unlocking starts from what is built, not the
                    # stored default.
                    current = getter(side)(obj)
                    setattr(op, f'unlock_{side}_overlay', True)
                    setattr(op, f'{side}_overlay', current)
                else:
                    setattr(op, f'unlock_{side}_overlay', bool(value))
            return set
        props = {}
        for side in ('top', 'bottom', 'left', 'right'):
            props[side] = prop_proxy.computed(
                getter(side), setter(side), unit='LENGTH', precision=4)
            props['unlock_' + side] = prop_proxy.computed(
                lock_get(side), lock_set(side), type='BOOLEAN')
        prop_proxy.register(OVERLAY_KEY, props)
    return prop_proxy.owner(opening_obj, OVERLAY_KEY)


def opening_overlay_blocks(context, opening_obj):
    from ...operators import options_panel
    return options_panel.field_blocks(context, (
        ('group', 'ff_opening_overlays', "Overlays", {'fields': tuple(
            ('locked', side, side.title(), {'unlock': 'unlock_' + side})
            for side in ('top', 'bottom', 'left', 'right'))}),
    ), _overlay_owner(opening_obj))


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


def _style_menu_actions(owner):
    """Under the styles in the Style dropdown: start a new one."""
    cs = _cabinet_style(owner)[1]
    return [("Add Style Section", 'hb_face_frame.add_style_section',
             {'source': cs.name if cs is not None else ""}, 'ADD')]


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
          'action': _style_settings, 'menu_actions': _style_menu_actions}),
    ), owner)


def _menu(label, menu_id, icon=None):
    """A button that drops down one of the right-click menu's own
    lists, the way the menu's submenu does."""
    from ...operators import generic_page
    return (label + "  ›", generic_page._opener(menu_id, label), None, None,
            1.0, icon)


def _act(label, op_id, kwargs=None, icon=None):
    return (label, op_id, dict(kwargs or {}), None, 1.0, icon)


def _quick(owner, rows):
    """The quick actions a page leads with, a row at a time: each row is
    (action, when) pairs and keeps the ones that apply, so a pair such
    as Insert Before / Insert After always shares a row. Every one is
    also on the right-click menu, and so in All Actions."""
    out = []
    for row in rows:
        kept = []
        for action, when in row:
            try:
                if when is not None and not when(owner):
                    continue
            except Exception:
                continue
            kept.append(action)
        if kept:
            out.append(('actions', tuple(kept), None))
    return (('label', None, "Quick Actions"),) + tuple(out) if out else ()


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
        ((_act("Duplicate", 'hb_face_frame.place_cabinet',
               {'source_cabinet_name': name}, 'duplicate'), _one_plain),
         (_act("Duplicate Mirror", 'hb_face_frame.place_cabinet',
               {'source_cabinet_name': name, 'mirror': True}, 'cab_mirror'),
          _one_plain)),
        ((_act("Join Cabinets", 'hb_face_frame.join_cabinets', None,
               'cab_join'), _cabinets_selected),
         (_act("Equalize Bays", 'hb_face_frame.equalize_bays', None,
               'cab_equalize_bays'), None)),
        ((_act("Blind Corner", 'hb_face_frame.edit_blind_corner', None,
               'cab_blind'), _blind),
         (_act("Swap Blind", 'hb_face_frame.swap_blind_corner', None,
               'cab_swap_blind'), _blind)),
        ((_menu("Change Opening",
                'HOME_BUILDER_MT_face_frame_corner_change_opening',
                'cab_change_opening'), _corner_opening),
         (_act("Wedge Calculator", 'hb_face_frame.add_refrigerator_wedge',
               None, 'cab_wedge'), _wedge)),
        ((_act("Copy Cabinet", 'home_builder.copy_cabinet'), _one_plain),
         (_act("Hide Cabinet", 'hb_general.hide',
               {'scope': 'PRODUCT', 'isolate': False}), None)),
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
            ('bool', 'corner_remove_bottom', "Remove Bottom", {'when': _corner_interior}),
            ('bool', 'corner_finish_interior', "Finish Interior", {'when': _corner_interior}),
        )}),
        ('group', 'ff_cab_construction', "Construction", {
            'icon': 'cab_construction', 'summary': _construction_summary, 'fields': (
                ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
                ('enum', 'bun_foot_style', "Foot", {'when': _bun_feet}),
                ('bool', 'bun_feet_open', "Open Underneath", {'when': _bun_square}),
                ('enum', 'bun_foot_corner_mode', "Foot Corners", {'when': _bun_square}),
                ('bool', 'bun_foot_front_left', "Front Left Foot", {'when': _bun_custom}),
                ('bool', 'bun_foot_front_right', "Front Right Foot", {'when': _bun_custom}),
                ('bool', 'bun_foot_back_left', "Back Left Foot", {'when': _bun_custom}),
                ('bool', 'bun_foot_back_right', "Back Right Foot", {'when': _bun_custom}),
                ('distance', 'bun_foot_offset_front', "Foot Offset Front", {'when': _bun_square}),
                ('distance', 'bun_foot_offset_back', "Foot Offset Back", {'when': _bun_square}),
                ('distance', 'bun_foot_offset_left', "Foot Offset Left", {'when': _bun_square}),
                ('distance', 'bun_foot_offset_right', "Foot Offset Right", {'when': _bun_square}),
                ('distance', 'toe_kick_height', "Kick Height", {'when': _has_kick}),
                ('bool', 'floating_vanity', "Floating Vanity",
                 {'when': lambda c: _has_kick(c) and c.toe_kick_type == 'FLOATING'}),
                ('distance', 'toe_kick_setback', "Kick Setback", {'when': _kick_closed}),
                ('distance', 'inset_toe_kick_left', "Left Inset", {'when': _kick_closed}),
                ('distance', 'inset_toe_kick_right', "Right Inset", {'when': _kick_closed}),
                ('distance', 'inset_toe_kick_rear', "Rear Inset", {'when': _kick_rear}),
                ('distance', 'inset_toe_kick_back_left', "Back Left Inset",
                 {'when': lambda c: _has_kick(c) and c.corner_type != 'NONE'}),
                ('distance', 'inset_toe_kick_back_right', "Back Right Inset",
                 {'when': lambda c: _has_kick(c) and c.corner_type != 'NONE'}),
                ('bool', 'include_finish_toe_kick', "Finish Toe Kick", {'when': _kick_closed}),
                ('enum', 'finish_toe_kick_type', "Finish Kick Type",
                 {'when': lambda c: _kick_closed(c) and c.include_finish_toe_kick}),
                ('bool', 'existing_cabinet', "Existing (on site)"),
            )}),
        ('group', 'ff_cab_ends', "Finished Ends & Back", {
            'summary': _ends_summary,
            'fields': (part_pages.end_fields('left', "Left End")
                       + (('gap', None, None),)
                       + part_pages.end_fields('right', "Right End")
                       + (('gap', None, None),)
                       + part_pages.back_fields("Back"))}),
        ('group', 'ff_cab_angled_back', "Angled Back", {
            'summary': _angled_summary, 'when': _no_corner, 'fields': (
                ('distance', 'extend_back_left', "Extend Back Left"),
                ('bool', 'wing_attached_left', "Left as Wing",
                 {'when': lambda c: c.extend_back_left != 0.0}),
                ('bool', 'open_left_end', "Open Left into Corner",
                 {'when': lambda c: c.extend_back_left > 0.0 and not c.wing_attached_left}),
                ('distance', 'wing_width_left', "Left Wing Width",
                 {'when': lambda c: c.wing_attached_left and c.extend_back_left != 0.0}),
                ('distance', 'extend_back_right', "Extend Back Right"),
                ('bool', 'wing_attached_right', "Right as Wing",
                 {'when': lambda c: c.extend_back_right != 0.0}),
                ('bool', 'open_right_end', "Open Right into Corner",
                 {'when': lambda c: c.extend_back_right > 0.0 and not c.wing_attached_right}),
                ('distance', 'wing_width_right', "Right Wing Width",
                 {'when': lambda c: c.wing_attached_right and c.extend_back_right != 0.0}),
            )}),
        ('group', 'ff_cab_upper_ext', "Upper Extensions", {
            'when': _is_type('UPPER'), 'fields': (
                ('bool', 'hutch_finished_back', "Finished Back in Recess",
                 {'when': lambda c: c.extend_left_end_down or c.extend_right_end_down}),
                ('bool', 'extend_sides_down', "Extend Sides Down"),
                ('distance', 'extend_sides_down_amount', "Sides Drop",
                 {'when': lambda c: c.extend_sides_down}),
                ('distance', 'overall_height', "Overall Height",
                 {'when': lambda c: c.extend_sides_down}),
                ('bool', 'side_front_profile', "Front Profile",
                 {'when': lambda c: c.extend_sides_down}),
                ('enum', 'overstool_accessory', "Accessory",
                 {'when': lambda c: c.extend_sides_down}),
                ('distance', 'extend_bottom_left', "Extend Bottom Left"),
                ('distance', 'extend_bottom_right', "Extend Bottom Right"),
                ('distance', 'extend_top_left', "Extend Top Left"),
                ('distance', 'extend_top_right', "Extend Top Right"),
            )}),
        ('group', 'ff_cab_deco_corners', "Decorative Corners", {
            'summary': lambda c: _label_of(c, 'decorative_corner_style'),
            'when': _no_corner, 'fields': (
                ('enum', 'decorative_corner_style', "Style"),
                ('bool', 'decorative_corner_front_left', "Front Left", {'when': _deco}),
                ('bool', 'decorative_corner_front_right', "Front Right", {'when': _deco}),
                ('bool', 'decorative_corner_back_left', "Back Left", {'when': _deco}),
                ('bool', 'decorative_corner_back_right', "Back Right", {'when': _deco}),
                ('enum', 'decorative_corner_bottom', "Bottom", {'when': _deco}),
                ('bool', 'decorative_corner_top_detail', "Top Transition", {'when': _deco}),
                ('distance', 'decorative_corner_detail_height', "Transition Height",
                 {'when': _deco}),
                ('distance', 'decorative_corner_block_run', "Square Block Run",
                 {'when': _deco}),
            )}),
        ('group', 'ff_cab_wood_top', "Furniture Top", {
            'summary': lambda c: (_label_of(c, 'furniture_top_shape')
                                  if c.furniture_top else "Off"),
            'fields': (
                ('bool', 'furniture_top', "Wood Top"),
                ('distance', 'furniture_top_thickness', "Thickness", {'when': _wood_top}),
                ('distance', 'furniture_top_overhang_front', "Overhang Front", {'when': _wood_top}),
                ('distance', 'furniture_top_overhang_back', "Overhang Back", {'when': _wood_top}),
                ('distance', 'furniture_top_overhang_left', "Overhang Left", {'when': _wood_top}),
                ('distance', 'furniture_top_overhang_right', "Overhang Right", {'when': _wood_top}),
                ('enum', 'furniture_top_shape', "Shape", {'when': _wood_top}),
                ('distance', 'furniture_top_bow_altitude', "Bow Altitude",
                 {'when': _top_shape('BOW_BACK')}),
                ('distance', 'furniture_top_radius_front_left', "Radius Front Left",
                 {'when': _top_shape('RADIUS')}),
                ('distance', 'furniture_top_radius_front_right', "Radius Front Right",
                 {'when': _top_shape('RADIUS')}),
                ('distance', 'furniture_top_radius_back_left', "Radius Back Left",
                 {'when': _top_shape('RADIUS')}),
                ('distance', 'furniture_top_radius_back_right', "Radius Back Right",
                 {'when': _top_shape('RADIUS')}),
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
                ('enum', 'bottom_rail_profile', "Bottom Rail Profile",
                 {'when': _is_type('BASE', 'TALL', 'UPPER')}),
            )}),
    )


def _bun_feet(cab):
    return _has_kick(cab) and cab.toe_kick_type == 'BUN_FEET'


def _bun_square(cab):
    return _bun_feet(cab) and cab.corner_type == 'NONE'


def _bun_custom(cab):
    return _bun_square(cab) and cab.bun_foot_corner_mode == 'CUSTOM'


def _kick_closed(cab):
    return _has_kick(cab) and not (_bun_square(cab) and cab.bun_feet_open)


def _kick_rear(cab):
    return (_kick_closed(cab) and cab.corner_type == 'NONE'
            and cab.toe_kick_type in ('NOTCH', 'LOOSE', 'LOOSE_FLUSH',
                                      'BUN_FEET'))


def _angled_summary(cab):
    sides = [s for s, v in (("Left", cab.extend_back_left),
                            ("Right", cab.extend_back_right)) if v != 0.0]
    return ", ".join(sides) if sides else ""


def _deco(cab):
    return cab.decorative_corner_style != 'NONE'


def _wood_top(cab):
    return cab.furniture_top


def _top_shape(shape):
    return lambda cab: cab.furniture_top and cab.furniture_top_shape == shape


# ---- A bay's appliances -------------------------------------------------------
# A base bay can hold a sink or a cooktop (stamped on the bay by the Add
# Appliance dialog); an upper bay can have a microwave or a vent hood
# hanging under it (the bay's own properties).

_SINK_KINDS = (('KITCHEN_SINK', "Kitchen Sink"), ('FARM_SINK', "Farm Sink"),
               ('VANITY_SINK', "Vanity Sink"), ('COOKTOP', "Cooktop"))


def _bay_appliance(bp):
    """'SINK', 'COOKTOP' or None for a base bay."""
    kind = bp.id_data.get('APPLIANCE_BAY')
    return kind if kind in ('SINK', 'COOKTOP') else None


def _bay_appliance_kind(bp):
    return bp.id_data.get('APPLIANCE_BAY_KIND') or (
        'COOKTOP' if _bay_appliance(bp) == 'COOKTOP' else 'KITCHEN_SINK')


def _bay_appliance_name(bp):
    if _cab_type(bp) == 'UPPER':
        if bp.under_cabinet_appliance == 'NONE':
            return None
        return {'MICROWAVE': "Microwave", 'HOOD': "Vent Hood"}.get(
            bp.under_cabinet_appliance, bp.under_cabinet_appliance.title())
    if _bay_appliance(bp) is None:
        return None
    return dict(_SINK_KINDS).get(_bay_appliance_kind(bp), "Sink")


def _appliance_summary(bp):
    return _bay_appliance_name(bp) or "None"


def _takes_appliance(bp):
    return _cab_type(bp) in ('BASE', 'UPPER')


def _base_free(bp):
    return _cab_type(bp) == 'BASE' and _bay_appliance(bp) is None


def _base_held(bp):
    return _cab_type(bp) == 'BASE' and _bay_appliance(bp) is not None


def _upper_free(bp):
    return _cab_type(bp) == 'UPPER' and bp.under_cabinet_appliance == 'NONE'


def _upper_held(bp):
    return _cab_type(bp) == 'UPPER' and bp.under_cabinet_appliance != 'NONE'


def _dropped(bp):
    return _base_held(bp) and bp.front_drop > 0.0


def _drop_fillers(bp):
    return _dropped(bp) and bp.front_drop_include_fillers


def _bay_appliance_fields(bay_obj):
    name = bay_obj.name
    add = 'hb_face_frame.add_appliance_to_bay'
    under = 'hb_face_frame.set_under_cabinet_appliance'

    def sink_add(label, kind):
        return _act(label, add, {'appliance_kind': kind, 'bay_name': name})
    edit = _act("Edit...", add, {
        'appliance_kind': _bay_appliance_kind(bay_obj.face_frame_bay),
        'bay_name': name})
    return (
        # Base bays: a sink or a cooktop
        ('actions', (sink_add("Kitchen Sink", 'KITCHEN_SINK'),
                     sink_add("Farm Sink", 'FARM_SINK')), None,
         {'when': _base_free}),
        ('actions', (sink_add("Vanity Sink", 'VANITY_SINK'),
                     sink_add("Cooktop", 'COOKTOP')), None,
         {'when': _base_free}),
        ('value', _bay_appliance_name, "Appliance", {'when': _base_held}),
        ('distance', 'front_drop', "Drop Bay", {'when': _base_held}),
        ('bool', 'front_drop_include_fillers', "Drop Fillers", {'when': _dropped}),
        ('bool', 'front_drop_set_appliance_width', "Set Appliance Width",
         {'when': _drop_fillers}),
        ('distance', 'front_drop_appliance_width', "Appliance Width",
         {'when': lambda bp: _drop_fillers(bp) and bp.front_drop_set_appliance_width}),
        ('distance', 'front_drop_left_filler', "Left Filler",
         {'when': lambda bp: _drop_fillers(bp) and not bp.front_drop_set_appliance_width}),
        ('distance', 'front_drop_right_filler', "Right Filler",
         {'when': lambda bp: _drop_fillers(bp) and not bp.front_drop_set_appliance_width}),
        ('bool', 'sink_removable_floor', "Removable Floor",
         {'when': lambda bp: _base_held(bp) and _bay_appliance(bp) == 'SINK'}),
        ('bool', 'farm_sink_custom_fit', "Custom Fit by Shop",
         {'when': lambda bp: _base_held(bp) and _bay_appliance_kind(bp) == 'FARM_SINK'}),
        ('actions', (edit, _act("Remove", 'hb_face_frame.remove_appliance_from_bay',
                                {'bay_name': name})), None,
         {'when': _base_held}),
        # Upper bays: a microwave or a vent hood under it
        ('actions', (_act("Microwave", under, {'start_kind': 'MICROWAVE', 'bay_name': name}),
                     _act("Vent Hood", under, {'start_kind': 'HOOD', 'bay_name': name})),
         None, {'when': _upper_free}),
        ('enum', 'under_cabinet_appliance', "Appliance", {'when': _upper_held}),
        ('distance', 'under_cabinet_appliance_width', "Width", {'when': _upper_held}),
        ('distance', 'under_cabinet_appliance_height', "Height", {'when': _upper_held}),
        ('distance', 'under_cabinet_appliance_depth', "Depth", {'when': _upper_held}),
        ('enum', 'under_cabinet_appliance_finish', "Finish", {'when': _upper_held}),
        ('actions', (_act("Remove", 'hb_face_frame.remove_under_cabinet_appliance',
                          {'bay_name': name}),), None, {'when': _upper_held}),
    )


def _bay_fields(bay_obj, bp):
    index = bp.bay_index
    quick = _quick(bp, (
        ((_act("Insert Before", 'hb_face_frame.insert_bay',
               {'bay_index': index, 'direction': 'BEFORE'},
               'cab_insert_before'), None),
         (_act("Insert After", 'hb_face_frame.insert_bay',
               {'bay_index': index, 'direction': 'AFTER'},
               'cab_insert_after'), None)),
        ((_act("Break Left", 'hb_face_frame.break_cabinet_left'), _several_bays),
         (_act("Break Right", 'hb_face_frame.break_cabinet_right'), _several_bays)),
        ((_act("Equal Doors", 'hb_face_frame.set_equal_door_width', None,
               'cab_equal_doors'), None),
         (_act("Flush Toe Kick", 'hb_face_frame.toggle_flush_toe_kick', None,
               'cab_flush_kick'), _is_type('BASE', 'TALL'))),
        ((_act("Finish Bay", 'hb_face_frame.finish_bay_prompts'), None),),
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
        ('group', 'ff_bay_appliances', "Appliances", {
            'summary': _appliance_summary, 'when': _takes_appliance,
            'fields': _bay_appliance_fields(bay_obj)}),
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
        ((_act("Split Horizontal", 'hb_face_frame.split_opening', {'axis': 'H'},
               'cab_split_h'), None),
         (_act("Split Vertical", 'hb_face_frame.split_opening', {'axis': 'V'},
               'cab_split_v'), None)),
        ((_act("Interior Options", 'hb_face_frame.interior_options', None,
               'cab_interior'), None),
         (_act("Equalize Heights", 'hb_face_frame.equalize_opening_heights',
               None, 'cab_equalize_heights'), None)),
        ((_act("Accessories", 'hb_face_frame.accessory_menu', None,
               'cab_accessories'), _accessories),),
    ))
    return (
        ('value', _opening_root_size, "Size"),
        ('locked', 'size', "Size",
         {'unlock': 'unlock_size', 'when': _split_child}),
    ) + front_fields() + (
        ('gap', None, None),
    ) + quick + (
        ('gap', None, None),
    )


def front_fields():
    """An opening's front and how it opens: on the opening's page and
    on the page of the door or drawer front in it."""
    return (
        ('enum', 'front_type', "Front"),
        ('enum', 'hinge_side', "Hinge Side", {'when': _hinged}),
        ('enum', 'door_mechanism', "Mechanism", {'when': _is_door}),
        ('bool', 'lift_up_servo', "Servo Drive",
         {'when': _mech('LIFT_UP_DELUXE', 'LIFT_UP_BIFOLD')}),
        ('enum', 'bifold_fold_side', "Folds To", {'when': _mech('RETRACTING_BIFOLD')}),
        ('enum', 'bifold_pull', "Bifold Pull",
         {'when': _mech('RETRACTING_BIFOLD', 'BIFOLD_LEFT', 'BIFOLD_RIGHT')}),
        ('enum', 'retracting_interior', "Pocket Interior",
         {'when': _mech('RETRACTING', 'RETRACTING_BIFOLD')}),
        ('enum', 'retracting_partitions', "Partitions", {'when': _retract_partitions}),
        ('distance', 'retracting_box_setback', "Box Setback", {'when': _retract_box}),
        ('distance', 'component_shelf_clearance', "Clearance Above",
         {'when': _retract_shelf}),
        ('number', 'swing_percent', "Open", {'when': _swings}),
    )


def front_detail_fields():
    return (
        ('bool', 'add_apron', "Add Apron", {'when': _is_door}),
        ('distance', 'apron_height', "Apron Height", {'when': _apron}),
        ('enum', 'drawer_look_divisions', "Drawer-Look", {'when': _drawer_look_ok}),
        ('enum', 'drawer_split_look', "Side-by-Side Look", {'when': _drawer_split_ok}),
        ('distance', 'drawer_split_stile_width', "Integral Stile",
         {'when': _drawer_split_on}),
        ('distance', 'drawer_split_groove_width', "Groove Width",
         {'when': _drawer_split_on}),
        ('distance', 'drawer_split_groove_depth', "Groove Depth",
         {'when': _drawer_split_on}),
        ('enum', 'door_look_divisions', "Door-Look", {'when': _door_look_ok}),
        ('enum', 'door_look_direction', "Door-Look Layout", {'when': _door_look_layout}),
        ('distance', 'door_look_top_height', "Top Door Height", {'when': _door_look_top}),
        ('enum', 'chase_fit', "Chase Fit", {'when': _chase}),
        ('bool', 'is_tilt_out', "Tilt-Out", {'when': _false_front}),
        ('bool', 'false_front_pull', "Add Pull", {'when': _false_front}),
        ('enum', 'inset_panel_type', "Panel Type", {'when': _inset_panel}),
        ('enum', 'appliance_kind', "Appliance", {'when': _appliance}),
        ('enum', 'appliance_fit', "Fit With", {'when': _appliance}),
        ('bool', 'include_fillers', "Include Fillers",
         {'when': lambda op: _appliance(op) and op.appliance_fit != 'NOTCH'}),
        ('bool', 'set_appliance_width', "Set Appliance Width",
         {'when': _appliance_width_shown}),
        ('distance', 'appliance_width', "Appliance Width", {'when': _appliance_width_set}),
        ('distance', 'left_filler_amount', "Left Filler", {'when': _fillers_typed}),
        ('distance', 'right_filler_amount', "Right Filler", {'when': _fillers_typed}),
        ('distance', 'left_filler_amount', "Left Notch", {'when': _notches_typed}),
        ('distance', 'right_filler_amount', "Right Notch", {'when': _notches_typed}),
    )


def finish_fields():
    """An opening's finish, as the Finish Opening dialog has it."""
    def on(op):
        return op.finish_opening

    def textured(op):
        return on(op) and op.finish_opening_texture not in ('NONE', '')

    def flush(op):
        return on(op) and op.finish_opening_flush
    return (
        ('bool', 'finish_opening', "Finish Opening"),
        ('enum', 'finish_opening_material', "Finish Color", {'when': on}),
        ('enum', 'finish_opening_texture', "Texture", {'when': on}),
        ('enum', 'finish_opening_texture_scope', "Texture On", {'when': textured}),
        ('enum', 'finish_opening_beadboard_pattern', "Beadboard",
         {'when': lambda op: on(op) and op.finish_opening_texture == 'BEADBOARD'}),
        ('bool', 'finish_opening_flush', "Finish Flush", {'when': on}),
        ('distance', 'finish_opening_flush_depth', "Flush Depth", {'when': flush}),
        ('bool', 'finish_opening_flush_top', "Flush Top", {'when': flush}),
    )


def _finish_summary(op):
    if not op.finish_opening:
        return "Off"
    return _label_of(op, 'finish_opening_material')


def _cab_texture_fields(op):
    """The cabinet's own texture settings an opening's choices reach:
    an inset beadboard panel's pattern and material, and a textured
    finish's boards, as (front details, finish). Shared with the rest
    of the cabinet, so labelled."""
    def inset_bead(_cab):
        return (op.front_type == 'INSET_PANEL'
                and op.inset_panel_type == 'BEADBOARD')

    def finish_tex(kind):
        return lambda _cab: (op.finish_opening
                             and op.finish_opening_texture == kind)
    inset = (
        ('enum', 'beadboard_pattern', "Pattern (Cabinet)", {'when': inset_bead}),
        ('enum', 'beadboard_material', "Material (Cabinet)", {'when': inset_bead}),
    )
    return inset, (
        ('enum', 'beadboard_material', "Beadboard Material (Cabinet)",
         {'when': finish_tex('BEADBOARD')}),
        ('distance', 'v_groove_spacing', "V-Groove Spacing (Cabinet)",
         {'when': finish_tex('V_GROOVE')}),
        ('enum', 'shiplap_board_width', "Shiplap Width (Cabinet)",
         {'when': finish_tex('SHIPLAP')}),
        ('enum', 'shiplap_direction', "Shiplap Direction (Cabinet)",
         {'when': finish_tex('SHIPLAP')}),
    )


def _drawer_look_rows(op):
    """[(fields, owner)] for a drawer-look stack's rows, top to bottom:
    each row's height, and between two rows the rail that can come out."""
    if not (_drawer_look_ok(op) and op.drawer_look_divisions != 'NONE'):
        return []
    rows = op.drawer_look_openings
    out = []
    for idx in range(len(rows) - 1, -1, -1):
        out.append(((('locked', 'size', "Drawer %d" % (len(rows) - idx),
                      {'unlock': 'unlock_size'}),), rows[idx]))
        if idx > 0:
            out.append(((('bool', 'no_rail_above', "Remove Rail Below"),),
                        rows[idx - 1]))
    return out


def _drawer_split_rows(op):
    """[(fields, owner)] for a side-by-side drawer front's face widths,
    left to right."""
    if not _drawer_split_on(op):
        return []
    return [((('locked', 'size', "Face %d" % (idx + 1),
               {'unlock': 'unlock_size'}),), face)
            for idx, face in enumerate(op.drawer_split_faces)]


def _owners_group(context, key, label, summary, parts):
    """A folding group, as a 'group' field draws one, whose fields sit
    on more than one owner: [(fields, owner)]. Left out when nothing in
    it is shown."""
    from ...operators import options_panel
    inner = []
    for fields, owner in parts:
        if owner is not None:
            inner.extend(options_panel.field_blocks(context, fields, owner))
    if not inner:
        return []
    method = 'group:' + key
    expanded = options_panel.section_expanded(context, method)

    def toggle(m=method):
        options_panel.toggle_section(bpy.context, m)
    blocks = [('section', (label, method, expanded, toggle, summary, None))]
    if expanded:
        blocks.extend(('indent', b) for b in inner)
        blocks.append(('gap', None))
    return blocks


def opening_group_blocks(context, opening_obj):
    """The opening page's folding groups past its main fields: the
    front's details, a drawer-look stack's row heights and the finish."""
    op = opening_obj.face_frame_opening
    root = types_face_frame.find_cabinet_root(opening_obj)
    cab = root.face_frame_cabinet if root is not None else None
    inset_tex, finish_tex = _cab_texture_fields(op)
    out = _owners_group(context, 'ff_opening_more', "Front Details",
                        _opening_summary(op),
                        [(front_detail_fields(), op), (inset_tex, cab)])
    rows = _drawer_look_rows(op)
    if rows:
        out += _owners_group(context, 'ff_opening_rows', "Drawer Heights",
                             "%d rows" % len(op.drawer_look_openings), rows)
    faces = _drawer_split_rows(op)
    if faces:
        out += _owners_group(context, 'ff_opening_faces', "Drawer Face Widths",
                             "%d faces" % len(op.drawer_split_faces), faces)
    out += _owners_group(context, 'ff_opening_finish', "Finish",
                         _finish_summary(op),
                         [(finish_fields(), op), (finish_tex, cab)])
    return out


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
    page = part_pages.page_blocks(context, part_obj)
    if page is not None:
        if out and page:
            out.append(('gap', None))
        out.extend(page)
        return out
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
    n_box = n_same = 0
    if kind == 'part':
        # Parts of one kind picked together edit together.
        n_same = part_pages.gather(context, part_obj, _picked)
        several = n_same > 1
    if kind == 'drawer':
        from . import accessory_place
        n_box = len(accessory_place.picked_drawer_boxes(context, part_obj))
        several = n_box > 1
    if kind == 'drawer' and several:
        out = [('head', (f"{n_box} Drawer Boxes", False, None)),
               ('label', f"Changes apply to all {n_box}")]
    elif kind == 'part' and several:
        out = [('head', (part_pages.plural(part_pages.role_of(part_obj),
                                           n_same), False, None)),
               ('label', f"Changes apply to all {n_same}")]
    elif kind == 'cabinet' and several:
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
        # What the bay is built as, and a pick of another layout.
        from . import bay_config
        out.extend(bay_config.field_blocks(context, bay_obj))
        out.extend(options_panel.field_blocks(
            context, _bay_fields(bay_obj, bp), bp))
        _footer(out, 'hb_face_frame.bay_prompts')
    elif kind == 'opening':
        op = opening_obj.face_frame_opening
        from . import bay_config
        out.extend(bay_config.opening_field_blocks(context, opening_obj))
        out.extend(options_panel.field_blocks(context, _opening_fields(op), op))
        # What is inside, said here; changed on the Interior page.
        from . import interior_page
        if interior_page.has_tree(opening_obj):
            inside = "%d sections" % len(interior_page.regions_of(opening_obj))
        else:
            inside = interior_page.interior_summary(op) or "Empty"
        out.append(('value', ("Interior", inside)))
        out.append(('actions', (
            _act("Edit Interior", 'hb_face_frame.show_interior_page',
                 {'opening_name': opening_obj.name}, 'cab_interior'),)))
        out.extend(opening_group_blocks(context, opening_obj))
        out.extend(opening_overlay_blocks(context, opening_obj))
        _footer(out, 'hb_face_frame.opening_prompts')
    elif kind == 'interior':
        from . import interior_page
        out.extend(interior_page.blocks(context, item))
        _footer(out, None)
    elif kind == 'drawer':
        from . import accessory_place
        out.extend(accessory_place.drawer_blocks(context, part_obj))
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
    if kind == 'drawer':
        from . import accessory_place
        if len(accessory_place.picked_drawer_boxes(context, part_obj)) > 1:
            return None
    if kind == 'part' and len(part_pages.same_role_parts(context, part_obj)) > 1:
        return None
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
    from . import interior_page
    interior_page.register()
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)
    from ...operators import options_panel
    options_panel.register_peers(_peers)
    options_panel.register_peers(part_pages.proxy_peers)


def unregister():
    from . import interior_page
    interior_page.unregister()
    try:
        from ...operators import options_panel, selected_tab
        options_panel.unregister_peers(_peers)
        options_panel.unregister_peers(part_pages.proxy_peers)
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
