"""A closet opening's settings as fields on the SELECTED tab.

What an opening holds is several settings read together: picking
drawers clears the door, a hamper clears the interior, a figure left
locked is the room's and one unlocked is the opening's own. The fields
here go through a schema (prop_proxy) whose reads and writes say that,
so the page can be edited a field at a time and the closet follows each
change, with nothing to accept at the end.
"""

import bpy

from . import const_closets as const
from . import materials_closets
from . import types_closets
from ... import units


SCHEMA = 'CL_OPENING'

SIDES = ('left', 'right', 'top', 'bottom')

_DOOR_ITEMS = (
    ('NONE', "None"),
    ('LEFT', "Left Swing"),
    ('RIGHT', "Right Swing"),
    ('DOUBLE', "Double Door"),
    ('LIFT_UP', "Lift Up"),
    ('TILT_OUT', "Tilt Out Hamper"),
)


def _ops():
    from .operators import ops_closet
    return ops_closet


def _pg(obj):
    return obj.hb_closet_opening


def _room():
    return bpy.context.scene.hb_closets


# ---- What the opening holds -------------------------------------------------

def _fill(obj):
    return _ops()._opening_fill(obj)


def _clear_fills(op, keep=None):
    if keep != 'ADJ_SHELVES':
        op.adj_shelf_qty = 0
    if keep != 'DRAWERS':
        op.drawer_qty = 0
    if keep != 'ROLLOUTS':
        op.rollout_qty = 0
    if keep != 'SLANTED_SHELVES':
        op.slant_qty = 0
    if keep != 'CUBBIES':
        op.cubby_cols = 1
        op.cubby_rows = 1


def _set_fill(obj, value):
    """One interior at a time: the one picked goes in at its standard
    count, the rest are cleared. Drawers are their own front, so they
    take the door off with them."""
    op = _pg(obj)
    if value == _fill(obj):
        return
    _clear_fills(op)
    if value == 'ADJ_SHELVES':
        op.adj_shelf_qty = min(types_closets.default_adj_shelf_qty(obj),
                               const.ADJ_SHELF_QTY_MAX)
    elif value == 'DRAWERS':
        op.drawer_qty = min(types_closets.default_drawer_qty(obj),
                            _ops()._DRAWER_QTY_MAX)
        op.door_swing = ''
    elif value == 'ROLLOUTS':
        op.rollout_qty = const.ROLLOUT_DEFAULT_QTY
    elif value == 'SLANTED_SHELVES':
        op.slant_qty = types_closets.default_slant_qty(obj)
    elif value == 'CUBBIES':
        op.cubby_cols = 3
        op.cubby_rows = 3


def _set_shelf_qty(obj, value):
    # A count typed over what the opening holds closes its padlock, or
    # the opening deals its count by height again and the figure snaps
    # back.
    op = _pg(obj)
    held = int(op.adj_shelf_qty) or types_closets.default_adj_shelf_qty(obj)
    if int(value) != held:
        op.unlock_adj_qty = True
    op.adj_shelf_qty = int(value)


def _get_drawer_box(obj):
    return _pg(obj).drawer_box_override or 'DEFAULT'


def _set_drawer_box(obj, value):
    op = _pg(obj)
    if value and value != 'DEFAULT':
        op.drawer_box_override = value
    else:
        op.property_unset('drawer_box_override')


def _get_door(obj):
    return _pg(obj).door_swing or 'NONE'


def _set_door(obj, value):
    """A tilt-out hamper's basket stands in the whole opening, so
    picking one clears the interior."""
    op = _pg(obj)
    op.door_swing = '' if value == 'NONE' else value
    if value == 'TILT_OUT':
        _clear_fills(op)


def _open_setter(name, role):
    def set(obj, value):
        op = _pg(obj)
        # A front someone clicked open goes back to following the
        # percentage only once the number is changed.
        if abs(float(value) - getattr(op, name)) > 1e-4:
            _ops()._clear_front_open_state(obj, role)
        setattr(op, name, float(value))
    return set


def _set_cubby_band(name):
    """Placement and band height split or merge openings, so they are
    rebuilt through the cubby edit and the opening the grid ends up in
    is picked again."""
    def set(obj, value):
        op = _pg(obj)
        placement = value if name == 'cubby_placement' else _cubby_placement(obj)
        height = float(value) if name == 'cubby_height' else _cubby_height(obj)
        target = types_closets.edit_cubbies(
            obj, int(op.cubby_cols), int(op.cubby_rows),
            float(op.cubby_setback), placement, height)
        if target is not None and target != obj:
            try:
                bpy.ops.object.select_all(action='DESELECT')
                target.select_set(True)
                bpy.context.view_layer.objects.active = target
            except Exception:
                pass
            _after(target, bpy.context)
    return set


def _cubby_placement(obj):
    if types_closets.cubby_band_cap(obj) is not None:
        return _pg(obj).cubby_placement
    return 'FILL'


def _cubby_height(obj):
    if types_closets.cubby_band_cap(obj) is not None:
        return float(_pg(obj).cubby_height)
    return const.CUBBY_HEIGHT


# ---- Figures the room holds until the opening takes them over ---------------

def _overlay_figures(obj, side):
    """(half, full, run) for one side, or None off a run."""
    return _ops()._side_overlay_options(obj, side)


def _run_overlay(obj, side):
    figures = _overlay_figures(obj, side)
    return figures[2] if figures else float(getattr(_pg(obj), side + '_overlay'))


def _door_rule(obj):
    """The convention this opening's door pulls are placed by: the one
    named, or on Auto the one its door lands on."""
    op = _pg(obj)
    rule = op.door_pull_location
    if rule != 'AUTO':
        return rule
    for child in obj.children:
        if (child.get('hb_part_role') == types_closets.PART_ROLE_DOOR
                and not child.get('hb_is_hamper')
                and child.get('hb_hinge') != 'TOP'):
            try:
                height = types_closets.front_size(child)[1]
                return types_closets.door_pull_rule(child, obj, op, height)[0]
            except Exception:
                break
    return 'BASE'


def _room_door_pull_v(obj):
    cp = _room()
    return float({'BASE': cp.pull_vertical_location_base,
                  'TALL': cp.pull_vertical_location_tall}.get(
                      _door_rule(obj), cp.pull_vertical_location_upper))


# (field, the opening's property, its padlock, the room's figure)
_TAKEOVERS = (
    ('clip_gap', 'shelf_clip_gap', 'unlock_shelf_clip_gap',
     lambda obj: float(_room().shelf_clip_gap)),
    ('setback', 'shelf_setback', 'unlock_shelf_setback',
     lambda obj: float(_room().shelf_setback)),
    ('door_pull_v', 'door_pull_vertical_location',
     'unlock_door_pull_vertical', _room_door_pull_v),
    ('door_pull_edge', 'door_pull_horizontal_offset',
     'unlock_door_pull_edge',
     lambda obj: float(_room().pull_horizontal_offset)),
    ('drawer_pull_v', 'drawer_pull_vertical_location',
     'unlock_pull_location',
     lambda obj: float(_room().pull_vertical_location_drawers)),
) + tuple(
    (side + '_overlay', side + '_overlay', 'unlock_%s_overlay' % side,
     lambda obj, s=side: _run_overlay(obj, s))
    for side in SIDES)


def _takeover_props(P, value_prop, lock_prop, room_value):
    """The figure (the room's while locked) and its padlock. Opening
    the padlock starts the opening on the room's figure, so nothing
    moves until a new one is typed."""
    def get(obj):
        op = _pg(obj)
        return (float(getattr(op, value_prop)) if getattr(op, lock_prop)
                else room_value(obj))

    def set(obj, value):
        setattr(_pg(obj), value_prop, float(value))
        if value_prop == 'door_pull_vertical_location':
            obj[types_closets.PROP_PULL_V_FROM_BOTTOM] = 1

    def get_lock(obj):
        return bool(getattr(_pg(obj), lock_prop))

    def set_lock(obj, value):
        op = _pg(obj)
        if value and not getattr(op, lock_prop):
            setattr(op, value_prop, room_value(obj))
            if value_prop == 'door_pull_vertical_location':
                obj[types_closets.PROP_PULL_V_FROM_BOTTOM] = 1
        setattr(op, lock_prop, bool(value))

    return (P.computed(get, set, unit='LENGTH', precision=4),
            P.computed(get_lock, set_lock, type='BOOLEAN'))


def _half_overlay_props(P, side):
    """Half overlay on a side, or full (held back only by the reveal).
    The side is the opening's own only where that differs from the
    run's."""
    def get(obj):
        figures = _overlay_figures(obj, side)
        if figures is None:
            return True
        op = _pg(obj)
        value = (float(getattr(op, side + '_overlay'))
                 if getattr(op, 'unlock_%s_overlay' % side) else figures[2])
        return abs(value - figures[0]) <= 1e-5

    def set(obj, value):
        figures = _overlay_figures(obj, side)
        if figures is None:
            return
        half, full, run_value = figures
        figure = half if value else full
        op = _pg(obj)
        setattr(op, 'unlock_%s_overlay' % side,
                abs(figure - run_value) > 1e-6)
        setattr(op, side + '_overlay', figure)

    return P.computed(get, set, type='BOOLEAN')


# ---- The rod ----------------------------------------------------------------

def _rods(obj):
    return _ops()._opening_rods(obj)


def _top_rod(obj):
    return _ops()._single_top_rod(obj)


def _get_rod_top(obj):
    rod = _top_rod(obj)
    return float(rod.get('hb_z_offset', const.ROD_TOP_OFFSET)
                 if rod is not None else const.ROD_TOP_OFFSET)


def _set_rod_top(obj, value):
    rod = _top_rod(obj)
    if rod is not None:
        rod['hb_z_offset'] = float(value)


# ---- The schema -------------------------------------------------------------

def rna_prop(P, group_cls, group_of, name, **over):
    """A property of a property group, read and written as it stands
    and described as its RNA describes it. `group_of(obj)` is the group
    on the object the schema is over."""
    rna = group_cls.bl_rna.properties[name]
    kw = {'type': rna.type}
    if rna.type == 'ENUM':
        kw['items'] = [(i.identifier, i.name) for i in rna.enum_items]
    elif rna.type in ('FLOAT', 'INT'):
        kw['hard_min'] = rna.hard_min
        kw['hard_max'] = rna.hard_max
        if rna.type == 'FLOAT':
            kw['unit'] = rna.unit
            kw['precision'] = rna.precision
    kw.update(over)
    cast = {'FLOAT': float, 'INT': int, 'BOOLEAN': bool}.get(rna.type, str)
    return P.computed(
        lambda obj: getattr(group_of(obj), name),
        lambda obj, value: setattr(group_of(obj), name, cast(value)),
        **kw)


def _own(P, name, **over):
    """One of the opening's own properties."""
    from . import props_closets
    return rna_prop(P, props_closets.Closet_Opening_Props, _pg, name, **over)


def _after(obj, context):
    try:
        root = types_closets.find_starter_root(obj)
    except ReferenceError:
        return      # the opening was merged away by the write
    if root is None:
        return
    ops = _ops()
    # What was picked: the opening itself, or a part standing in it.
    active = context.view_layer.objects.active
    names = [active.name if active is not None else "", obj.name]
    types_closets.recalculate_closet_starter(root)
    ops._apply_finish(root)
    # The shading pass deselects everything. What was picked is picked
    # again - the part if it is still there, else its opening, else the
    # closet - or the page being edited would close under the field
    # that was just changed.
    ops._apply_selection_shading(context, root, keep_active=False)
    for name in names:
        target = bpy.data.objects.get(name) if name else None
        if target is None or types_closets.find_opening_cage(target) is None:
            continue
        try:
            target.select_set(True)
        except (RuntimeError, ReferenceError):
            continue
        if target.select_get():
            context.view_layer.objects.active = target
            return
    root.select_set(True)
    context.view_layer.objects.active = root


def _ensure():
    from ...operators import prop_proxy as P
    if SCHEMA in P._schemas:
        return
    ops = _ops()
    props = {
        'fill': P.computed(_fill, _set_fill, type='ENUM',
                           items=[i[:2] for i in ops._OPENING_FILL_ITEMS]),
        'shelf_qty': P.computed(
            lambda obj: int(_pg(obj).adj_shelf_qty), _set_shelf_qty,
            type='INT', hard_min=0, hard_max=const.ADJ_SHELF_QTY_MAX),
        'drawer_qty': _own(P, 'drawer_qty', hard_min=1),
        'drawer_box': P.computed(
            _get_drawer_box, _set_drawer_box, type='ENUM',
            items=[i[:2] for i in ops._DRAWER_BOX_OVERRIDE_ITEMS]),
        'open_drawer': P.computed(
            lambda obj: float(_pg(obj).open_drawer),
            _open_setter('open_drawer', types_closets.PART_ROLE_DRAWER_FRONT),
            precision=0, hard_min=0.0, hard_max=100.0),
        'open_door': P.computed(
            lambda obj: float(_pg(obj).open_door),
            _open_setter('open_door', types_closets.PART_ROLE_DOOR),
            precision=0, hard_min=0.0, hard_max=100.0),
        'cubby_placement': P.computed(
            _cubby_placement, _set_cubby_band('cubby_placement'),
            type='ENUM', items=[i[:2] for i in const.CUBBY_PLACEMENT_ITEMS]),
        'cubby_height': P.computed(
            _cubby_height, _set_cubby_band('cubby_height'),
            unit='LENGTH', precision=4, hard_min=0.0),
        'rollout_qty': _own(P, 'rollout_qty', hard_min=1),
        'slant_qty': _own(P, 'slant_qty', hard_min=1),
        'slant_color': P.computed(
            lambda obj: types_closets.shoe_fence_color(_pg(obj).slant_color),
            lambda obj, value: setattr(_pg(obj), 'slant_color', value),
            type='ENUM',
            items=[i[:2] for i in types_closets.SHOE_FENCE_COLOR_ITEMS]),
        'accent_material': P.computed(
            lambda obj: materials_closets.opening_color(
                _pg(obj).accent_material),
            lambda obj, value: setattr(
                _pg(obj), 'accent_material',
                '' if value == materials_closets.ROOM_COLOR else value),
            type='ENUM', items=materials_closets.opening_color_items()),
        'door_swing': P.computed(_get_door, _set_door, type='ENUM',
                                 items=_DOOR_ITEMS),
        'rod_top_offset': P.computed(_get_rod_top, _set_rod_top,
                                     unit='LENGTH', precision=4,
                                     hard_min=0.0),
    }
    for name in ('drawer_stretcher_width', 'drawer_grain',
                 'cubby_cols', 'cubby_rows', 'cubby_setback',
                 'rollout_height', 'slant_spacing', 'slant_angle',
                 'slant_fence_inset', 'slant_back_inset', 'slant_z',
                 'rod_set_from_front', 'rod_from_front', 'rod_from_rear',
                 'rod_width_deduction', 'remove_hangers',
                 'add_back', 'back_inset', 'back_notch_left',
                 'back_notch_right', 'back_notch_width',
                 'back_notch_height',
                 'no_pulls', 'door_pull_location', 'unlock_center_pull',
                 'center_pull_on_front', 'double_pull_on_front',
                 'distance_between_pulls'):
        props[name] = _own(P, name)
    for field, value_prop, lock_prop, room_value in _TAKEOVERS:
        props[field], props['own_' + field] = _takeover_props(
            P, value_prop, lock_prop, room_value)
    for side in SIDES:
        props['half_' + side] = _half_overlay_props(P, side)
    P.register(SCHEMA, props, after=_after)


def owner(opening):
    """The opening as the field engine takes it."""
    from ...operators import prop_proxy
    _ensure()
    return prop_proxy.owner(opening, SCHEMA)


# ---- Fields -----------------------------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def size_text(obj):
    width, depth, height = _ops()._opening_dims(obj)
    return f"{_dist(width)} x {_dist(height)} x {_dist(depth)}"


def fill_text(obj):
    op = _pg(obj)
    if (op.door_swing or '') == 'TILT_OUT':
        return "Hamper"
    if int(op.drawer_qty):
        return f"{int(op.drawer_qty)} Drawers"
    if int(op.rollout_qty):
        return f"{int(op.rollout_qty)} Rollout Trays"
    if int(op.slant_qty):
        return f"{int(op.slant_qty)} Slanted Shoe Shelves"
    if int(op.cubby_cols) > 1 or int(op.cubby_rows) > 1:
        return f"Cubbies {int(op.cubby_cols)} x {int(op.cubby_rows)}"
    if int(op.adj_shelf_qty):
        return f"{int(op.adj_shelf_qty)} Adjustable Shelves"
    return "Empty"


def _door_text(obj):
    if _fill(obj) == 'DRAWERS':
        return "Drawers"
    return dict(_DOOR_ITEMS).get(_get_door(obj), "None")


def _takeover(field, label, **options):
    options['unlock'] = 'own_' + field
    return ('locked', field, label, options)


def _interior_fields(obj):
    def holds(*fills):
        return lambda _ow: _fill(obj) in fills

    def banded(_ow):
        return _fill(obj) == 'CUBBIES' and _cubby_placement(obj) != 'FILL'

    if (_pg(obj).door_swing or '') == 'TILT_OUT':
        # A hamper is its own interior.
        return (('label', None, "Hamper basket fills the opening"),)
    return (
        ('enum', 'fill', "Holds"),
        ('number', 'shelf_qty', "Shelves", {'when': holds('ADJ_SHELVES')}),
        _takeover('clip_gap', "Clip Gap",
                  when=holds('ADJ_SHELVES', 'SLANTED_SHELVES')),
        _takeover('setback', "Setback", when=holds('ADJ_SHELVES')),
        ('number', 'drawer_qty', "Drawers", {'when': holds('DRAWERS')}),
        ('enum', 'drawer_box', "Drawer Box", {'when': holds('DRAWERS')}),
        ('distance', 'drawer_stretcher_width', "Stretcher Width",
         {'when': holds('DRAWERS')}),
        ('enum', 'drawer_grain', "Grain", {'when': holds('DRAWERS')}),
        ('number', 'open_drawer', "Open Drawer %",
         {'when': holds('DRAWERS')}),
        ('number', 'cubby_cols', "Columns", {'when': holds('CUBBIES')}),
        ('number', 'cubby_rows', "Rows", {'when': holds('CUBBIES')}),
        ('distance', 'cubby_setback', "Setback", {'when': holds('CUBBIES')}),
        ('enum', 'cubby_placement', "Placement", {'when': holds('CUBBIES')}),
        ('distance', 'cubby_height', "Cubby Height", {'when': banded}),
        ('number', 'rollout_qty', "Trays", {'when': holds('ROLLOUTS')}),
        ('distance', 'rollout_height', "Tray Height",
         {'when': holds('ROLLOUTS')}),
        ('number', 'slant_qty', "Shelves",
         {'when': holds('SLANTED_SHELVES')}),
        ('distance', 'slant_spacing', "Between Shelves",
         {'when': holds('SLANTED_SHELVES')}),
        ('number', 'slant_angle', "Shelf Angle",
         {'when': holds('SLANTED_SHELVES')}),
        ('enum', 'slant_color', "Fence Color",
         {'when': holds('SLANTED_SHELVES')}),
        ('distance', 'slant_fence_inset', "Lip Width Inset",
         {'when': holds('SLANTED_SHELVES')}),
        ('distance', 'slant_back_inset', "Back Inset",
         {'when': holds('SLANTED_SHELVES')}),
        ('distance', 'slant_z', "Vertical Location",
         {'when': holds('SLANTED_SHELVES')}),
    )


def _rod_fields(obj):
    op = _pg(obj)
    return (
        ('distance', 'rod_top_offset', "From Top",
         {'when': lambda _ow: _top_rod(obj) is not None}),
        ('bool', 'rod_set_from_front', "Measure From Front"),
        ('distance', 'rod_from_front', "From Front",
         {'when': lambda _ow: op.rod_set_from_front}),
        ('distance', 'rod_from_rear', "From Rear",
         {'when': lambda _ow: not op.rod_set_from_front}),
        ('distance', 'rod_width_deduction', "Width Deduction"),
        ('bool', 'remove_hangers', "Remove Hangers"),
    )


def _front_fields(obj):
    if _fill(obj) == 'DRAWERS':
        # Drawers are their own front, so there is no door to set.
        return (('label', None, "The drawers are this opening's front"),)

    def has_door(_ow):
        return _get_door(obj) != 'NONE'

    return (
        ('enum', 'door_swing', "Door"),
        ('number', 'open_door', "Open Door %", {'when': has_door}),
        ('label', None, "Half Overlays", {'when': has_door}),
    ) + tuple(('bool', 'half_' + side, side.title(), {'when': has_door})
              for side in SIDES)


def _overlay_fields(obj):
    return tuple(_takeover(side + '_overlay', side.title())
                 for side in SIDES)


def _pull_fields(obj):
    op = _pg(obj)
    cp = _room()

    def pulled(_ow):
        return not op.no_pulls

    def door_v(_ow):
        return not op.no_pulls and op.door_pull_location != 'MIDDLE'

    def own_centering(_ow):
        return not op.no_pulls and op.unlock_center_pull

    def measured(_ow):
        # A tilt-out hamper's pull is measured from the top even where
        # drawer pulls are centered.
        centered = (op.center_pull_on_front if op.unlock_center_pull
                    else cp.center_pulls_on_drawer_front)
        return not op.no_pulls and (
            (op.door_swing or '') == 'TILT_OUT' or not centered)

    v_label = "From Top" if _door_rule(obj) == 'BASE' else "From Bottom"
    return (
        ('bool', 'no_pulls', "No Pulls"),
        ('label', None, "Doors", {'when': pulled}),
        ('enum', 'door_pull_location', "Location", {'when': pulled}),
        _takeover('door_pull_v', v_label, when=door_v),
        _takeover('door_pull_edge', "From Edge", when=pulled),
        ('label', None, "Drawer Fronts", {'when': pulled}),
        ('bool', 'unlock_center_pull', "Own Centering", {'when': pulled}),
        ('bool', 'center_pull_on_front', "Centered On Front",
         {'when': own_centering}),
        _takeover('drawer_pull_v', "From Top", when=measured),
        ('bool', 'double_pull_on_front', "Two Per Front", {'when': pulled}),
        ('distance', 'distance_between_pulls', "Between Pulls",
         {'when': lambda _ow: not op.no_pulls and op.double_pull_on_front}),
    )


def _back_fields(obj):
    op = _pg(obj)

    def backed(_ow):
        return op.add_back

    def notched(_ow):
        return op.add_back and (op.back_notch_left or op.back_notch_right)

    return (
        ('bool', 'add_back', "Add Back"),
        ('distance', 'back_inset', "Inset", {'when': backed}),
        ('bool', 'back_notch_left', "Notch Left", {'when': backed}),
        ('bool', 'back_notch_right', "Notch Right", {'when': backed}),
        ('distance', 'back_notch_width', "Notch Width", {'when': notched}),
        ('distance', 'back_notch_height', "Notch Height", {'when': notched}),
    )


def fields(obj):
    """The opening's section: its size, then a group for each part of
    it, each saying what is set in it while folded."""
    op = _pg(obj)
    return (
        ('value', lambda _ow: size_text(obj), "Size"),
        ('enum', 'accent_material', "Color"),
        ('group', 'cl_op_interior', "Interior", {
            'summary': lambda _ow: fill_text(obj),
            'fields': _interior_fields(obj)}),
        ('group', 'cl_op_rod', "Rod", {
            'when': lambda _ow: bool(_rods(obj)),
            'fields': _rod_fields(obj)}),
        ('group', 'cl_op_front', "Front", {
            'summary': lambda _ow: _door_text(obj),
            'fields': _front_fields(obj)}),
        ('group', 'cl_op_overlays', "Overlays", {
            'summary': lambda _ow: "Own" if any(
                getattr(op, 'unlock_%s_overlay' % s) for s in SIDES) else "",
            'fields': _overlay_fields(obj)}),
        ('group', 'cl_op_pulls', "Pulls", {
            'summary': lambda _ow: "None" if op.no_pulls else "",
            'fields': _pull_fields(obj)}),
        ('group', 'cl_op_back', "Back", {
            'summary': lambda _ow: "On" if op.add_back else "Off",
            'fields': _back_fields(obj)}),
    )
