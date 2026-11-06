"""The SELECTED tab's page for one face frame part, by what the part is.

A left side shows that end's finished settings, a stile its width and
scribe, a rail its width and profile, a door its front and hardware --
the settings its right-click dialogs edit, laid out on the page. Each
page keeps the part's size at the top and All Actions at the foot.

Picking several parts of one kind (two end stiles, four doors) edits
them all: the page names the others as peers of the one it shows.
"""

import bpy

from . import types_face_frame
from . import types_face_frame_corner


# ---- What a part is ---------------------------------------------------------

_SIDES = {
    types_face_frame.PART_ROLE_LEFT_SIDE: 'left',
    types_face_frame.PART_ROLE_RIGHT_SIDE: 'right',
    types_face_frame.PART_ROLE_LEFT_SIDE_SEAM: 'left',
    types_face_frame.PART_ROLE_RIGHT_SIDE_SEAM: 'right',
    types_face_frame_corner.PART_ROLE_CORNER_LEFT_SIDE: 'left',
    types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE: 'right',
}
_BACKS = (types_face_frame.PART_ROLE_BACK,
          types_face_frame.PART_ROLE_FINISHED_BACK)
_END_STILES = {
    types_face_frame.PART_ROLE_LEFT_STILE: 'left',
    types_face_frame.PART_ROLE_RIGHT_STILE: 'right',
}
_FRONTS = (types_face_frame.PART_ROLE_DOOR,
           types_face_frame.PART_ROLE_DRAWER_FRONT,
           types_face_frame.PART_ROLE_PULLOUT_FRONT,
           types_face_frame.PART_ROLE_TILT_OUT,
           types_face_frame.PART_ROLE_FALSE_FRONT)


def role_of(obj):
    return str(obj.get('hb_part_role', '') or '')


def _root(obj):
    return types_face_frame.find_cabinet_root(obj)


def _ops():
    from .operators import ops_part_commands
    return ops_part_commands


# ---- Several picked ---------------------------------------------------------
# The parts picked with the shown one that share its role. Their
# cabinets (and openings, for fronts) are the peers the field engine
# writes along with it; the width proxy has its own peers.

_part_peers = []        # the picked parts of the shown part's role
# Set by a width write that has already gone to every picked part, so
# the field engine's pass over the peers that follows finds none: by
# then the rebuild has replaced them.
_wrote_all = [False]


def same_role_parts(context, part_obj):
    from ...operators import generic_page
    from . import selected_card
    role = role_of(part_obj)
    out = [part_obj]
    for obj in context.selected_objects:
        if (obj != part_obj and role_of(obj) == role
                and generic_page.menu_id(obj) == selected_card.PART_MENU):
            out.append(obj)
    return out


def gather(context, part_obj, picked):
    """Point the page's peers at the parts picked of the shown one's
    kind: their cabinets, their openings, the parts themselves."""
    parts = same_role_parts(context, part_obj)
    _part_peers[:] = parts
    roots, openings = [], []
    for obj in parts:
        root = _root(obj)
        if root is not None and root not in roots:
            roots.append(root)
        opening = _opening_of(obj)
        if opening is not None and opening not in openings:
            openings.append(opening)
    picked['face_frame_cabinet'] = roots
    picked['face_frame_opening'] = openings
    picked['face_frame_bay'] = []
    return len(parts)


def proxy_peers(owner):
    """Peers for a part seen through the width schema."""
    from ...operators import prop_proxy
    try:
        if owner.path_from_id() != prop_proxy.PATH_PREFIX + WIDTH_KEY:
            return ()
        if _wrote_all[0]:
            _wrote_all[0] = False
            return ()
        obj = owner.id_data
        if obj not in _part_peers:
            return ()
        return [prop_proxy.owner(o, WIDTH_KEY) for o in _part_peers
                if o != obj]
    except ReferenceError:
        return ()


def _opening_of(obj):
    while obj is not None:
        if obj.get(types_face_frame.TAG_OPENING_CAGE):
            return obj
        obj = obj.parent
    return None


def plural(role, n):
    words = role.replace('_', ' ').title()
    return f"{n} {words}s"


# ---- Width, as a field ------------------------------------------------------
# A stile's or rail's width is not one property: a rail spans the bays
# of its segment, a mid rail keeps its own override on its split. The
# right-click Set Width reads and writes it through ops_part_commands;
# this schema does the same, so the page has a Width field with a lock.

WIDTH_KEY = 'FF_PART_WIDTH'


def _width_get(obj):
    root = _root(obj)
    if root is None:
        return 0.0
    try:
        return float(_ops()._get_current_width(obj, role_of(obj), root)
                     or 0.0)
    except Exception:
        return 0.0


def _targets(obj):
    """`obj` and the parts picked with it, while all are still there.
    Two rails of one cabinet go together: written one at a time, the
    first one's rebuild would replace the second."""
    out = [obj]
    if obj in _part_peers:
        for other in _part_peers:
            try:
                if other != obj and other.name:
                    out.append(other)
            except ReferenceError:
                pass
        _wrote_all[0] = True
    return out


def _each(obj, fn):
    ops = _ops()
    # One recalc for the lot: the unlock flips and the per-bay writes
    # would each rebuild the cabinet, and a rebuild replaces the parts.
    with types_face_frame.suspend_recalc():
        for part in _targets(obj):
            root = _root(part)
            if root is not None:
                fn(ops, part, role_of(part), root)


def _width_set(obj, value):
    def apply(ops, part, role, root):
        ops._flip_unlock_for_role(part, role, root)
        ops._fan_out_value(part, role, root, float(value))
    _each(obj, apply)


def _unlocked_get(obj):
    root = _root(obj)
    if root is None:
        return False
    cab = root.face_frame_cabinet
    role = role_of(obj)
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        return cab.unlock_left_stile
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        return cab.unlock_right_stile
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            return cab.mid_stile_widths[msi].unlock
        return False
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        attr = ('unlock_top_rail' if role == types_face_frame.PART_ROLE_TOP_RAIL
                else 'unlock_bottom_rail')
        if cab.corner_type != 'NONE':
            return getattr(cab, attr)
        bay = _ops()._find_bay_with_index(
            root, obj.get('hb_segment_start_bay', 0))
        return getattr(bay.face_frame_bay, attr) if bay else getattr(cab, attr)
    split = _ops()._find_owning_split_node(obj)
    if split is None:
        return False
    idx = obj.get('hb_splitter_index', 0)
    coll = split.face_frame_split.splitter_widths
    return bool(0 <= idx < len(coll) and coll[idx].active)


def _unlocked_set(obj, value):
    def apply(ops, part, role, root):
        if value:
            width = _width_get(part)
            ops._flip_unlock_for_role(part, role, root)
            ops._fan_out_value(part, role, root, width)
        else:
            ops._lock_for_role(part, role, root)
    _each(obj, apply)


def _width_owner(obj):
    from ...operators import prop_proxy
    if WIDTH_KEY not in prop_proxy._schemas:
        prop_proxy.register(WIDTH_KEY, {
            'width': prop_proxy.computed(_width_get, _width_set,
                                         unit='LENGTH', precision=4,
                                         hard_min=0.0),
            'unlocked': prop_proxy.computed(_unlocked_get, _unlocked_set,
                                            type='BOOLEAN'),
        })
    return prop_proxy.owner(obj, WIDTH_KEY)


def _width_blocks(context, part_obj):
    from ...operators import options_panel
    if role_of(part_obj) not in _ops()._ROLES_WITH_WIDTH:
        return []
    return options_panel.field_blocks(context, (
        ('locked', 'width', "Width", {'unlock': 'unlocked'}),
    ), _width_owner(part_obj))


# ---- Finished ends ----------------------------------------------------------
# The fields of an end's Set Finished End dialog, each shown while it
# means something: the flush strip on a Flush-X end, the extend on one
# that carries a finished part, the return once it is extended past a
# finished back, the drop on an upper.

def _cond(side):
    return f'{side}_finished_end_condition'


def _covered(side):
    def test(cab):
        from . import island_pair
        return side not in {s.lower() for s in
                            island_pair.covered_sides(cab.id_data)}
    return test


def _carries(side):
    return lambda cab: getattr(cab, _cond(side)) not in ('UNFINISHED',
                                                         'FLUSH_X')


def _flush(side):
    return lambda cab: getattr(cab, _cond(side)) == 'FLUSH_X'


def _texture(side, kind):
    return lambda cab: getattr(cab, _cond(side)) == kind


def _returns(side):
    def test(cab):
        return (getattr(cab, _cond(side)) in types_face_frame.RETURN_SIDE_CONDITIONS
                and getattr(cab, f'{side}_side_finished_extend_back') != 0.0
                and (cab.back_finished_end_condition
                     in types_face_frame.RETURN_BACK_CONDITIONS
                     or not types_face_frame.returns_need_back(cab.id_data)))
    return test


def _has_return(side):
    returns = _returns(side)
    return lambda cab: (returns(cab)
                        and getattr(cab, f'{side}_side_return_width') != 0.0)


def _shows_inside(side):
    def test(cab):
        from . import ui_face_frame
        return ui_face_frame._side_shows_inside(cab, side)
    return test


def _upper(cab):
    return cab.cabinet_type == 'UPPER'


def _dropped(side):
    return lambda cab: _upper(cab) and getattr(cab, f'extend_{side}_end_down')


def _both(*tests):
    return lambda cab: all(t(cab) for t in tests)


def end_fields(side, label):
    """The fields of one end, the condition labelled `label`."""
    keep = _covered(side)
    return (
        ('enum', _cond(side), label, {'when': keep}),
        ('label', None, "Combined into the run behind",
         {'when': lambda cab: not keep(cab)}),
        ('distance', f'{side}_flush_x_amount', "Flush Amount",
         {'when': _flush(side)}),
        ('distance', f'{side}_flush_x_thickness', "Flush Thickness",
         {'when': _flush(side)}),
        ('distance', f'{side}_side_finished_extend_back', "Extend Back",
         {'when': _both(keep, _carries(side))}),
        ('distance', f'{side}_side_return_width', "Return Width",
         {'when': _both(keep, _returns(side))}),
        ('enum', f'{side}_side_return_panel_type', "Side Return",
         {'when': _both(keep, _has_return(side))}),
        ('enum', f'{side}_side_return_stile_type', "Return Stile",
         {'when': _both(keep, _has_return(side))}),
        ('distance', 'return_back_void', "Back Void",
         {'when': _both(keep, _has_return(side))}),
        ('bool', f'extend_{side}_end_down', "Extend Down", {'when': _upper}),
        ('distance', f'extend_{side}_end_down_amount', "Drop",
         {'when': _dropped(side)}),
        ('bool', f'{side}_side_finish_inside', "Finish Inside Face",
         {'when': _shows_inside(side)}),
        ('distance', 'shiplap_board_width', "Shiplap Width",
         {'when': _texture(side, 'SHIPLAP')}),
        ('enum', 'shiplap_direction', "Shiplap Direction",
         {'when': _texture(side, 'SHIPLAP')}),
        ('enum', 'beadboard_pattern', "Beadboard Pattern",
         {'when': _texture(side, 'BEADBOARD')}),
        ('enum', 'beadboard_material', "Beadboard Stock",
         {'when': _texture(side, 'BEADBOARD')}),
        ('distance', 'v_groove_spacing', "V-Groove Spacing",
         {'when': _texture(side, 'V_GROOVE')}),
    )


def _back_finished(cab):
    return cab.back_finished_end_condition != 'UNFINISHED'


def back_fields(label):
    return (
        ('enum', 'back_finished_end_condition', label),
        ('distance', 'back_finished_extend_left', "Extend Left",
         {'when': _back_finished}),
        ('distance', 'back_finished_extend_right', "Extend Right",
         {'when': _back_finished}),
        ('distance', 'back_finished_rise', "Arch Rise",
         {'when': lambda cab: cab.back_finished_end_condition == 'FINISHED'}),
    )


# ---- The pages --------------------------------------------------------------

def _act(label, op_id, kwargs=None):
    return (label, op_id, dict(kwargs or {}), None)


def _rows(actions):
    actions = [a for a in actions if a is not None]
    return [('actions', tuple(actions[i:i + 2]))
            for i in range(0, len(actions), 2)]


def _cutout_actions(part_obj):
    ops = _ops()
    try:
        if not ops._is_cutpart(part_obj):
            return []
    except Exception:
        return []
    return [_act("Add Cutout", 'hb_face_frame.add_part_cutout')]


def _side_page(context, part_obj, root, side):
    from ...operators import options_panel
    ops = _ops()
    cab = root.face_frame_cabinet
    out = options_panel.field_blocks(
        context, end_fields(side, "Finished End"), cab)
    if ops.seam_available(part_obj):
        out.extend(options_panel.field_blocks(context, (
            ('bool', f'{side}_side_no_seam', "No Seam"),
            ('distance', f'{side}_side_seam_height', "Seam Height",
             {'when': lambda c: not getattr(c, f'{side}_side_no_seam')}),
        ), cab))
    other = 'Right' if side == 'left' else 'Left'
    out.append(('gap', None))
    out.extend(_rows([
        _act(f"Apply to {other} Side",
             'hb_face_frame.apply_finished_end_to_other_side',
             {'cabinet_name': root.name, 'side': side.upper()}),
    ] + _cutout_actions(part_obj)))
    return out


def _back_page(context, part_obj, root):
    from ...operators import options_panel
    out = options_panel.field_blocks(
        context, back_fields("Back"), root.face_frame_cabinet)
    rows = _rows(_cutout_actions(part_obj))
    if rows:
        out.append(('gap', None))
        out.extend(rows)
    return out


def _end_stile_page(context, part_obj, root, side):
    from ...operators import options_panel
    from . import selected_card
    cab = root.face_frame_cabinet
    out = _width_blocks(context, part_obj)
    scribes = types_face_frame.shows_scribe_options(root)
    out.extend(options_panel.field_blocks(context, (
        ('distance', f'{side}_scribe', "Scribe", {'when': lambda c: scribes}),
        ('distance', f'{side}_stile_extension', "Extension"),
        ('enum', f'{side}_stile_type', "Stile Type"),
        ('bool', f'extend_{side}_stile_to_floor', "Stile to Floor",
         {'when': selected_card._has_kick}),
    ), cab))
    out.append(('gap', None))
    out.extend(_rows([_act("Cabinet Column", 'hb_face_frame.set_cabinet_column')]))
    return out


def _top_rail_page(context, part_obj, root):
    from ...operators import options_panel
    cab = root.face_frame_cabinet
    scribes = types_face_frame.shows_scribe_options(root)
    out = _width_blocks(context, part_obj)
    out.extend(options_panel.field_blocks(context, (
        ('distance', 'top_scribe', "Scribe", {'when': lambda c: scribes}),
        ('distance', 'top_rail_extension', "Extension"),
        ('bool', 'paneled_top_rail', "Paneled Top Rail"),
    ), cab))
    return out


def _bottom_rail_page(context, part_obj, root):
    from . import selected_card
    ops = _ops()
    out = _width_blocks(context, part_obj)
    actions = [selected_card._menu(
        "Profile", 'HOME_BUILDER_MT_face_frame_bottom_rail_profile')]
    flush_root = ops._flush_rail_root(part_obj)
    if flush_root is not None:
        flush = flush_root.face_frame_cabinet.toe_kick_type == 'FLUSH'
        actions.append(_act("Remove Flush" if flush else "Make Flush",
                            'hb_face_frame.toggle_flush_bottom_rail'))
    actions.append(_act("Remove Rail", 'hb_face_frame.remove_bottom_rail'))
    out.append(('gap', None))
    out.extend(_rows(actions))
    return out


def _pull_locations(context):
    ops = _ops()
    return [(label, 'hb_face_frame.set_pull_location', {'location': ident})
            for ident, label, _desc in ops._PULL_LOCATION_ITEMS]


def _front_page(context, part_obj, root):
    from ...operators import options_panel
    from . import selected_card
    ops = _ops()
    role = role_of(part_obj)
    out = []
    opening = _opening_of(part_obj)
    if opening is not None:
        op = opening.face_frame_opening
        out.extend(options_panel.field_blocks(context, (
            ('enum', 'front_type', "Front"),
            ('enum', 'hinge_side', "Hinge Side", {'when': selected_card._hinged}),
            ('enum', 'door_mechanism', "Mechanism", {'when': selected_card._is_door}),
        ), op))
    actions = [_act("Set Pull", 'hb_face_frame.set_front_pull')]
    styled = ops.has_door_style_modifier(part_obj)
    if styled:
        actions.append(_act("Door Frame", 'hb_face_frame.set_door_frame'))
    if role == types_face_frame.PART_ROLE_DOOR:
        actions.append(_act("Hardware", 'hb_face_frame.set_door_hardware'))
        if styled:
            from . import props_hb_face_frame
            glass = props_hb_face_frame.front_glass_door(part_obj)
            actions.append(_act("Glass Options" if glass else "Make Glass",
                                'hb_face_frame.make_glass_door'))
            if glass:
                actions.append(_act("Remove Glass",
                                    'hb_face_frame.remove_glass_door'))
    if ops.door_shape_available(part_obj):
        actions.append(_act("Door Shape", 'hb_face_frame.set_door_shape'))
    out.append(('gap', None))
    out.extend(_rows(actions))
    if role in ('DOOR', 'PULLOUT_FRONT'):
        out.append(('pick', ("Pull Location", _pull_locations)))
    return out


def page_blocks(context, part_obj):
    """The role's fields and commands for a picked part, or None for a
    part with no page of its own (it gets its menu's quick actions)."""
    role = role_of(part_obj)
    root = _root(part_obj)
    if root is None:
        return None
    if role in _SIDES:
        return _side_page(context, part_obj, root, _SIDES[role])
    if role in _BACKS:
        return _back_page(context, part_obj, root)
    if role in _END_STILES:
        return _end_stile_page(context, part_obj, root, _END_STILES[role])
    if role == types_face_frame.PART_ROLE_TOP_RAIL:
        return _top_rail_page(context, part_obj, root)
    if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
        return _bottom_rail_page(context, part_obj, root)
    if role in _FRONTS:
        return _front_page(context, part_obj, root)
    if role == types_face_frame.PART_ROLE_MID_STILE:
        out = _width_blocks(context, part_obj)
        out.append(('gap', None))
        out.extend(_rows([
            _act("Stile to Floor", 'hb_face_frame.toggle_stile_to_floor'),
            _act("Mid Stile Properties", 'hb_face_frame.mid_stile_prompts'),
        ]))
        return out
    if role == types_face_frame.PART_ROLE_BAY_MID_RAIL:
        out = _width_blocks(context, part_obj)
        if not (root.get(types_face_frame.TAG_APPLIED_PANEL_SIDE)
                or types_face_frame._is_standalone_panel(root)):
            out.append(('gap', None))
            out.extend(_rows([_act("Remove Mid Rail",
                                   'hb_face_frame.remove_mid_rail')]))
        return out
    if role in _ops()._ROLES_WITH_WIDTH:
        return _width_blocks(context, part_obj)
    return None
