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

# Products with their own forms (and no cabinet carcass) keep them.
_OWN_FORMS = ('IS_LEG_PRODUCT', 'IS_FLOATING_SHELF', 'IS_END_SHELVES')


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


def _not_type(*types):
    return lambda owner: _cab_type(owner) not in types


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
    roots = {types_face_frame.find_cabinet_root(o)
             for o in bpy.context.selected_objects}
    roots.discard(None)
    return len(roots) >= 2


def _one_cabinet(owner):
    return not _cabinets_selected(owner)


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


def _menu(label, menu_id):
    """A command button that drops down one of the right-click menu's
    own preset lists."""
    return (label, 'wm.call_menu', {'name': menu_id}, None)


# ---- Fields -----------------------------------------------------------------
# Each section: the settings changed on nearly every cabinet, then the
# rest of the everyday ones under folds of their own, then commands.
# Anything destructive or rare stays on the right-click menu, and the
# last button opens the full dialog.

def _cabinet_fields(root):
    name = root.name
    return (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height_above_floor', "Above Floor", {'when': _raised}),
        ('choices', 'anchor_side', "Anchor", {'cols': 3, 'when': _no_corner}),
        ('group', 'ff_cab_corner', "Corner", {'when': _corner, 'fields': (
            ('locked', 'left_depth', "Left Depth", {'unlock': 'unlock_left_depth'}),
            ('locked', 'right_depth', "Right Depth", {'unlock': 'unlock_right_depth'}),
            ('enum', 'exterior_option', "Door Swing", {'when': _pie_cut}),
            ('enum', 'diag_door_swing', "Door Swing", {'when': _diagonal}),
            ('enum', 'interior_option', "Interior", {'when': _corner_interior}),
        )}),
        ('group', 'ff_cab_construction', "Construction", {'fields': (
            ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
            ('distance', 'toe_kick_height', "Kick Height", {'when': _has_kick}),
            ('distance', 'toe_kick_setback', "Kick Setback", {'when': _has_kick}),
            ('enum', 'left_finished_end_condition', "Left End"),
            ('enum', 'right_finished_end_condition', "Right End"),
            ('enum', 'back_finished_end_condition', "Back"),
            ('bool', 'existing_cabinet', "Existing (on site)"),
            ('actions', (("More Construction...", 'hb_face_frame.cabinet_prompts',
                          {'active_tab': 'CONSTRUCTION'}, None),), ""),
        )}),
        ('group', 'ff_cab_face_frame', "Face Frame", {'fields': (
            ('locked', 'top_rail_width', "Top Rail", {'unlock': 'unlock_top_rail'}),
            ('locked', 'bottom_rail_width', "Bottom Rail", {'unlock': 'unlock_bottom_rail'}),
            ('locked', 'left_stile_width', "Left Stile", {'unlock': 'unlock_left_stile'}),
            ('locked', 'right_stile_width', "Right Stile", {'unlock': 'unlock_right_stile'}),
            ('distance', 'left_scribe', "Left Scribe", {'when': _scribes}),
            ('distance', 'right_scribe', "Right Scribe", {'when': _scribes}),
            ('distance', 'top_scribe', "Top Scribe", {'when': _scribes}),
            ('bool', 'extend_left_stile_to_floor', "Left Stile to Floor", {'when': _has_kick}),
            ('bool', 'extend_right_stile_to_floor', "Right Stile to Floor", {'when': _has_kick}),
            ('actions', (("More Face Frame...", 'hb_face_frame.cabinet_prompts',
                          {'active_tab': 'FACE_FRAME'}, None),), ""),
        )}),
        ('actions', (_menu("Change Opening...",
                           'HOME_BUILDER_MT_face_frame_corner_change_opening'),),
         "", {'when': _corner_opening}),
        ('actions', (
            ("Blind/Corner...", 'hb_face_frame.edit_blind_corner'),
            ("Swap Blind", 'hb_face_frame.swap_blind_corner'),
        ), "", {'when': _blind}),
        ('actions', (("Wedge Calculator...", 'hb_face_frame.add_refrigerator_wedge'),),
         "", {'when': _wedge}),
        ('actions', (
            ("Duplicate", 'hb_face_frame.place_cabinet',
             {'source_cabinet_name': name}, None),
            ("Duplicate Mirror", 'hb_face_frame.place_cabinet',
             {'source_cabinet_name': name, 'mirror': True}, None),
        ), "", {'when': _no_corner}),
        ('actions', (
            ("Equalize Bays", 'hb_face_frame.equalize_bays'),
            ("Join Cabinets", 'hb_face_frame.join_cabinets'),
        ), "", {'when': _cabinets_selected}),
        ('actions', (("Equalize Bays", 'hb_face_frame.equalize_bays'),),
         "", {'when': _one_cabinet}),
        ('actions', (("All Cabinet Settings...", 'hb_face_frame.cabinet_prompts'),), ""),
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
        ('actions', (
            ("Insert Before", 'hb_face_frame.insert_bay',
             {'bay_index': index, 'direction': 'BEFORE'}, None),
            ("Insert After", 'hb_face_frame.insert_bay',
             {'bay_index': index, 'direction': 'AFTER'}, None),
        ), ""),
    ]
    # The bay's own commands act on the active object, so they are only
    # offered when the bay itself is what is picked.
    if picked:
        fields.extend((
            ('actions', (_menu("Change Bay...", 'HOME_BUILDER_MT_face_frame_change_bay'),),
             "", {'when': _has_bay_presets}),
            ('actions', (
                ("Equal Door Width", 'hb_face_frame.set_equal_door_width'),
                ("Flush Toe Kick", 'hb_face_frame.toggle_flush_toe_kick'),
            ), "", {'when': _is_type('BASE', 'TALL')}),
            ('actions', (
                ("Equal Door Width", 'hb_face_frame.set_equal_door_width'),
            ), "", {'when': _not_type('BASE', 'TALL')}),
            ('actions', (
                ("Finish Bay...", 'hb_face_frame.finish_bay_prompts'),
                ("All Bay Settings...", 'hb_face_frame.bay_prompts'),
            ), ""),
        ))
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
        ('actions', (_menu("Change Opening...", 'HOME_BUILDER_MT_face_frame_change_opening'),
                     ("Equalize Heights", 'hb_face_frame.equalize_opening_heights')), ""),
        ('actions', (
            ("Split Horizontal", 'hb_face_frame.split_opening', {'axis': 'H'}, None),
            ("Split Vertical", 'hb_face_frame.split_opening', {'axis': 'V'}, None),
        ), ""),
        ('actions', (
            ("Interior...", 'hb_face_frame.interior_options'),
            ("Finish...", 'hb_face_frame.finish_opening_prompts'),
        ), ""),
        ('actions', (("Accessories...", 'hb_face_frame.accessory_menu'),),
         "", {'when': _accessories}),
        ('actions', (("All Opening Settings...", 'hb_face_frame.opening_prompts'),), ""),
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

    trail = ["Cabinet"]
    if bay_obj is not None:
        trail.append(f"Bay {bay_obj.face_frame_bay.bay_index + 1}")
    if opening_obj is not None:
        trail.append(f"Opening {opening_obj.face_frame_opening.opening_index + 1}")

    out = [('head', (root.name, False, None)),
           ('label', " > ".join(trail))]

    _fold_for(context, kind)

    out.extend(options_panel.field_blocks(context, (
        ('group', CABINET_GROUP, f"Cabinet  ({cab.cabinet_type.title()})",
         {'summary': _cabinet_summary, 'fields': _cabinet_fields(root)}),
    ), cab))
    if bay_obj is not None:
        bp = bay_obj.face_frame_bay
        out.extend(options_panel.field_blocks(context, (
            ('group', BAY_GROUP, trail[1],
             {'summary': _bay_summary,
              'fields': _bay_fields(bay_obj, kind == 'bay')}),
        ), bp))
    if opening_obj is not None:
        op = opening_obj.face_frame_opening
        out.extend(options_panel.field_blocks(context, (
            ('group', OPENING_GROUP, trail[-1],
             {'summary': _opening_summary, 'fields': _opening_fields()}),
        ), op))
    return out


# ---- Lifecycle --------------------------------------------------------------

def register():
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks)


def unregister():
    try:
        from ...operators import selected_tab
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
