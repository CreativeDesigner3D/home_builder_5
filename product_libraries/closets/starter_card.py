"""A closet starter's settings as fields on the SELECTED tab.

Everything the starter's dialog held, as groups that fold: where it
stands, what happens at its top, its hang rail, panels, insets, toe
kick and countertop, and for a corner unit or filler what it is cut to
and how it is mounted. The fields go through a schema (prop_proxy) so
the ones that are not properties of the run - its place on the wall, a
corner's mounting, a height picked off the standard list - sit among
the ones that are. The run's own properties re-solve it as they
change.

What belongs to one bay (its sizes, mounting, bottom, cleat and double
panel) is the bay's section, a level down.
"""

import bpy

from . import const_closets as const
from . import types_closets
from ... import units


SCHEMA = 'CL_STARTER'

_CUSTOM = ('CUSTOM', "Custom")

# The run's own properties shown as they stand.
_OWN = (
    'width', 'height', 'depth',
    'toe_kick_height', 'toe_kick_setback',
    'include_countertop', 'countertop_overhang_front',
    'countertop_overhang_rear', 'countertop_overhang_left',
    'countertop_overhang_right', 'countertop_left_finished_end',
    'countertop_right_finished_end', 'countertop_radius_finished_ends',
    'include_backsplash', 'backsplash_height',
    'back_to_floor', 'applied_back_overlay',
    'extend_panels_to_countertop', 'extend_panel_amount',
    'bridge_left', 'bridge_right', 'bridge_left_width',
    'bridge_right_width', 'include_bottom_bridge_left',
    'include_bottom_bridge_right',
    'inset_bottom', 'inset_cleat', 'bottom_cleat',
    'left_finished_end', 'right_finished_end',
    'turn_off_left_panel', 'turn_off_right_panel',
    'drill_through_left', 'drill_through_right',
    'include_batten_left', 'include_batten_right',
    'add_top_accent_shelf', 'top_accent_overhang', 'top_accent_set_sides',
    'top_accent_overhang_left', 'top_accent_overhang_right',
    'remove_hang_rail', 'extend_hang_rail_left', 'extend_hang_rail_right',
    'use_one_hang_rail_height', 'hang_rail_height_location',
    'left_side_wall_filler', 'right_side_wall_filler',
    'l_left_depth', 'l_right_depth', 'filler_left_width',
    'filler_right_width', 'l_interior', 'l_rod_on_left',
    'l_top_opening_height', 'l_shelf_qty', 'l_back_width',
    'l_flip_partition', 'l_use_radius', 'l_corner_radius', 'l_radius_top',
    'l_radius_shelves', 'l_radius_bottom', 'l_add_cleat',
)


def _ops():
    from .operators import ops_closet
    return ops_closet


def _sp(root):
    return root.hb_closet_starter


def _cls(root):
    return types_closets.WRAP_CLASS_REGISTRY.get(
        root.get('CLASS_NAME', ''), types_closets.ClosetStarter)


def _on_wall(root):
    from . import props_closets
    return props_closets.starter_wall(root) is not None


# ---- Settings that are not the run's own properties -------------------------

def _get_x(root):
    # On a wall X reads from the left end of the side of the wall the
    # run is on.
    return float(_sp(root).wall_offset if _on_wall(root)
                 else root.location.x)


def _set_x(root, value):
    if _on_wall(root):
        _sp(root).wall_offset = float(value)
    else:
        root.location.x = float(value)


def _axis(index):
    def get(root):
        return float(root.location[index])

    def set(root, value):
        root.location[index] = float(value)
    return get, set


def _get_turn(root):
    return float(root.rotation_euler.z)


def _set_turn(root, value):
    root.rotation_euler.z = float(value)


def _get_hang(root):
    from . import props_closets
    return const.nearest_hang_line_key(
        props_closets.hang_line(_sp(root))) or 'CUSTOM'


def _set_hang(root, value):
    if value != 'CUSTOM':
        _sp(root).hanging_height_preset = value


def _get_all_heights(root):
    """The height the bays share, or Mixed where they differ (or stand
    off the standard heights)."""
    heights = [float(b.hb_closet_bay.height)
               for b in _ops()._starter_bays(root)]
    if not heights or max(heights) - min(heights) > 1e-5:
        return 'CUSTOM'
    return const.nearest_panel_height_key(heights[0]) or 'CUSTOM'


def _set_all_heights(root, value):
    """One height to every bay, as the dialog's Overall Height gave it
    behind its padlock. The padlock is closed again, so a bay can take
    its own height back afterwards."""
    if value == 'CUSTOM':
        return
    sp = _sp(root)
    _ops()._set_enum_silent(sp, 'overall_height_preset', value)
    sp.set_all_heights = True
    sp['set_all_heights'] = False


def _get_kick(root):
    return const.kick_height_key(_sp(root).toe_kick_height) or 'CUSTOM'


def _set_kick(root, value):
    if value != 'CUSTOM':
        _sp(root).toe_kick_height_preset = value


def _get_floor(root):
    return bool(_ops()._corner_is_floor(root))


def _set_floor(root, value):
    _ops()._set_corner_mounting(root, bool(value))


def _get_corner_hang(root):
    ops = _ops()
    return ops._nearest_panel_height_key(ops._corner_hang_top(root))


def _set_corner_hang(root, value):
    _ops()._set_corner_mounting(root, False, const.millimeter(int(value)))


def _after(root, context):
    # A run moved by its origin has nothing to solve, and the run's own
    # properties solve themselves; the views only need drawing again.
    _ops()._redraw_viewports(context)


def _ensure():
    from ...operators import prop_proxy as P
    if SCHEMA in P._schemas:
        return
    from . import opening_card, props_closets
    props = {
        name: opening_card.rna_prop(
            P, props_closets.Closet_Starter_Props, _sp, name)
        for name in _OWN}
    y_get, y_set = _axis(1)
    z_get, z_set = _axis(2)
    props.update({
        'name': P.computed(lambda root: root.name,
                           lambda root, value: setattr(root, 'name',
                                                       str(value)),
                           type='STRING'),
        'hidden': P.computed(
            lambda root: bool(root.hide_viewport),
            lambda root, value: setattr(root, 'hide_viewport', bool(value)),
            type='BOOLEAN'),
        'loc_x': P.computed(_get_x, _set_x, unit='LENGTH', precision=4),
        'loc_y': P.computed(y_get, y_set, unit='LENGTH', precision=4),
        'loc_z': P.computed(z_get, z_set, unit='LENGTH', precision=4),
        'turn': P.computed(_get_turn, _set_turn, unit='ROTATION',
                           precision=2),
        'hang_height': P.computed(
            _get_hang, _set_hang, type='ENUM',
            items=[i[:2] for i in const.HANG_LINE_ITEMS] + [_CUSTOM]),
        'all_heights': P.computed(
            _get_all_heights, _set_all_heights, type='ENUM',
            items=([i[:2] for i in const.PANEL_HEIGHT_ITEMS]
                   + [('CUSTOM', "Mixed")])),
        'kick_standard': P.computed(
            _get_kick, _set_kick, type='ENUM',
            items=[i[:2] for i in const.KICK_HEIGHT_ITEMS] + [_CUSTOM]),
        'corner_floor': P.computed(_get_floor, _set_floor, type='BOOLEAN'),
        'corner_hang': P.computed(
            _get_corner_hang, _set_corner_hang, type='ENUM',
            items=[i[:2] for i in const.HANG_LINE_ITEMS]),
    })
    P.register(SCHEMA, props, after=_after)


def owner(root):
    """The starter as the field engine takes it."""
    from ...operators import prop_proxy
    _ensure()
    return prop_proxy.owner(root, SCHEMA)


# ---- Fields -----------------------------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def summary(root):
    sp = _sp(root)
    return f"{_dist(sp.width)} x {_dist(sp.height)} x {_dist(sp.depth)}"


def _location_fields(root):
    return (
        ('distance', 'loc_x', "X"),
        ('distance', 'loc_y', "Y"),
        ('distance', 'loc_z', "Z"),
        ('number', 'turn', "Z Rotation",
         {'when': lambda _ow: not _on_wall(root)}),
    )


def _mount_fields(root, label):
    return (
        ('bool', 'corner_floor', label),
        ('enum', 'corner_hang', "Hanging Height",
         {'when': lambda _ow: not _get_floor(root)}),
    )


def _corner_fields(root):
    sp = _sp(root)

    def interior(*kinds):
        return lambda _ow: sp.l_interior in kinds

    def rounded(_ow):
        return sp.l_use_radius

    def warning(_context):
        text = root.get(types_closets.PROP_ACCESSORY_WARNING, '')
        return (text,) if text else ()

    return _mount_fields(root, "Floor Mounted") + (
        ('distance', 'l_left_depth', "Left Depth"),
        ('distance', 'l_right_depth', "Right Depth"),
        ('enum', 'l_interior', "Interior"),
        ('number', 'l_shelf_qty', "Shelves",
         {'when': interior('ADJ', 'LOCK')}),
        ('bool', 'l_rod_on_left', "Rod On Left",
         {'when': interior('ROD', 'DOUBLE')}),
        ('distance', 'l_top_opening_height', "Top Opening Height",
         {'when': interior('DOUBLE')}),
        ('notes', warning, ""),
        ('distance', 'l_back_width', "Back Width"),
        ('bool', 'l_flip_partition', "Flip Partition"),
        ('bool', 'l_use_radius', "Radius Corner"),
        ('distance', 'l_corner_radius', "Radius", {'when': rounded}),
        ('bool', 'l_radius_top', "Radius Top", {'when': rounded}),
        ('bool', 'l_radius_shelves', "Radius Shelves", {'when': rounded}),
        ('bool', 'l_radius_bottom', "Radius Bottom", {'when': rounded}),
        ('bool', 'l_add_cleat', "Add Cleat"),
    )


def _filler_fields(root):
    return (
        ('distance', 'filler_left_width', "Left Width"),
        ('distance', 'filler_right_width', "Right Width"),
    ) + _mount_fields(root, "Floor Mounted")


def _top_fields(root):
    sp = _sp(root)

    def accent(_ow):
        return sp.add_top_accent_shelf

    def sides(_ow):
        return sp.add_top_accent_shelf and sp.top_accent_set_sides

    return (
        ('bool', 'add_top_accent_shelf', "Accent Shelf"),
        ('distance', 'top_accent_overhang', "Overhang", {'when': accent}),
        ('bool', 'top_accent_set_sides', "Set Side Overhangs",
         {'when': accent}),
        ('distance', 'top_accent_overhang_left', "Left Overhang",
         {'when': sides}),
        ('distance', 'top_accent_overhang_right', "Right Overhang",
         {'when': sides}),
    )


def _rail_fields(root):
    sp = _sp(root)

    def railed(_ow):
        return not sp.remove_hang_rail

    return (
        ('bool', 'remove_hang_rail', "Remove Hang Rail"),
        ('distance', 'extend_hang_rail_left', "Extend Left",
         {'when': railed}),
        ('distance', 'extend_hang_rail_right', "Extend Right",
         {'when': railed}),
        ('bool', 'use_one_hang_rail_height', "One Rail Height",
         {'when': railed}),
        ('distance', 'hang_rail_height_location', "Rail Height",
         {'when': lambda _ow: (not sp.remove_hang_rail
                               and sp.use_one_hang_rail_height)}),
    )


def _panel_fields(root, is_corner):
    """What each end panel is, then what reaches every panel in the
    run. A corner has no use for the wall filler, the batten or the
    bridge: all three want a neighbouring run to sit against."""
    sp = _sp(root)
    out = []
    for side, cap in (('left', "Left"), ('right', "Right")):
        out.append(('label', None, cap + " End"))
        if not is_corner:
            out.append(('distance', side + '_side_wall_filler',
                        "Wall Filler"))
            out.append(('bool', 'include_batten_' + side, "Batten"))
        out.append(('bool', 'turn_off_%s_panel' % side, "Turn Off Panel"))
        out.append(('bool', side + '_finished_end', "Finished End"))
        out.append(('bool', 'drill_through_' + side, "Drill Through"))
        if not is_corner:
            def bridged(_ow, s=side):
                return getattr(sp, 'bridge_' + s)
            out.append(('bool', 'bridge_' + side, "Bridge"))
            out.append(('distance', 'bridge_%s_width' % side,
                        "Bridge Shelf Width", {'when': bridged}))
            out.append(('bool', 'include_bottom_bridge_' + side,
                        "Bottom Bridge", {'when': bridged}))
    out.append(('label', None, "Every Panel"))
    out.append(('bool', 'extend_panels_to_countertop',
                "Extend To Countertop"))
    out.append(('distance', 'extend_panel_amount', "Extend Amount",
                {'when': lambda _ow: sp.extend_panels_to_countertop}))
    return tuple(out)


def _inset_fields(root):
    def hangs(_ow):
        return any(not b.hb_closet_bay.floor_mounted
                   for b in _ops()._starter_bays(root))

    return (
        ('distance', 'inset_bottom', "Inset Bottom"),
        ('distance', 'inset_cleat', "Inset Cleat"),
        ('hints', lambda _context: ("Floor bays only",), ""),
        ('bool', 'bottom_cleat', "Bottom Cleat", {'when': hangs}),
    )


def _kick_fields(root):
    return (
        ('enum', 'kick_standard', "Standard Height"),
        ('distance', 'toe_kick_height', "Height"),
        ('distance', 'toe_kick_setback', "Setback"),
    )


def _countertop_fields(root):
    sp = _sp(root)

    def topped(_ow):
        return sp.include_countertop

    def ended(_ow):
        return sp.include_countertop and (
            sp.countertop_left_finished_end
            or sp.countertop_right_finished_end)

    return (
        ('bool', 'include_countertop', "Countertop"),
        # Fixed by what the top is made of (the room's Countertops), so
        # it is said rather than offered.
        ('value', lambda _ow: (_dist(sp.countertop_thickness)
                               if sp.include_countertop else None),
         "Thickness"),
        ('distance', 'countertop_overhang_front', "Front Overhang",
         {'when': topped}),
        ('distance', 'countertop_overhang_rear', "Rear Overhang",
         {'when': topped}),
        ('distance', 'countertop_overhang_left', "Left Overhang",
         {'when': topped}),
        ('distance', 'countertop_overhang_right', "Right Overhang",
         {'when': topped}),
        ('bool', 'countertop_left_finished_end', "Left Finished End",
         {'when': topped}),
        ('bool', 'countertop_right_finished_end', "Right Finished End",
         {'when': topped}),
        ('bool', 'countertop_radius_finished_ends', "Radius Finished Ends",
         {'when': ended}),
        ('bool', 'include_backsplash', "Backsplash", {'when': topped}),
        ('distance', 'backsplash_height', "Backsplash Height",
         {'when': lambda _ow: (sp.include_countertop
                               and sp.include_backsplash)}),
    )


def fields(root):
    """The starter's section: its overall size, then a group for each
    part of it, read down the closet the way it stands."""
    sp = _sp(root)
    cls = _cls(root)
    is_corner = bool(getattr(cls, 'is_corner', False))
    is_filler = bool(getattr(cls, 'is_filler', False))
    hangs = _ops()._has_hang_line(sp, is_corner, is_filler)
    out = [
        ('text', 'name', "Name"),
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
    ]
    if hangs:
        # A run its bays hang from: the hang line on its own, and one
        # height written to every bay at once.
        out.append(('enum', 'hang_height', "Hanging Height"))
        out.append(('enum', 'all_heights', "Set All Bay Heights"))
    out.append(('group', 'cl_st_location', "Location", {
        'summary': lambda _ow: "X " + _dist(_get_x(root)),
        'fields': _location_fields(root)
        + (('bool', 'hidden', "Hide In Viewport"),)}))
    if is_filler:
        out.append(('group', 'cl_st_filler', "Filler",
                    {'fields': _filler_fields(root)}))
    elif is_corner:
        out.append(('group', 'cl_st_corner', "Corner", {
            'summary': lambda _ow: ("Floor" if _get_floor(root)
                                    else "Hanging"),
            'fields': _corner_fields(root)}))
    if not is_filler:
        out.append(('group', 'cl_st_top', "Top", {
            'summary': lambda _ow: ("Accent Shelf"
                                    if sp.add_top_accent_shelf else ""),
            'fields': _top_fields(root)}))
    if getattr(cls, 'has_hang_rail', False):
        out.append(('group', 'cl_st_rail', "Hang Rail", {
            'summary': lambda _ow: "Removed" if sp.remove_hang_rail else "",
            'fields': _rail_fields(root)}))
    out.append(('group', 'cl_st_panels', "Panels",
                {'fields': _panel_fields(root, is_corner)}))
    if getattr(cls, 'has_applied_back', False):
        out.append(('group', 'cl_st_back', "Applied Back", {'fields': (
            ('bool', 'back_to_floor', "Back To Floor"),
            ('distance', 'applied_back_overlay', "Overlay"),
        )}))
    out.append(('group', 'cl_st_insets', "Insets",
                {'fields': _inset_fields(root)}))
    out.append(('group', 'cl_st_kick', "Toe Kick", {
        'summary': lambda _ow: _dist(sp.toe_kick_height),
        'fields': _kick_fields(root)}))
    if getattr(cls, 'has_countertop', False):
        out.append(('group', 'cl_st_ctop', "Countertop", {
            'summary': lambda _ow: "On" if sp.include_countertop else "Off",
            'fields': _countertop_fields(root)}))
    return tuple(out)
