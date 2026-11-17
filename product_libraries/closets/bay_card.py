"""A closet bay's settings as fields on the SELECTED tab.

Everything the bay's dialog held: the sizes it can take over from the
run, how it is mounted, its construction, the height of its top
opening, the front across it, and on a double-sided island where the
divider between the two faces stands. The bay's own properties re-solve
the run as they change; the top opening height moves the shelf (or
rod) under that opening and goes through a schema (prop_proxy) to do
it.
"""

import bpy

from . import const_closets as const
from . import types_closets
from ... import units


SCHEMA = 'CL_BAY'

_OWN = (
    'width', 'unlock_width', 'height', 'unlock_height', 'depth',
    'unlock_depth', 'floor_mounted', 'remove_bottom', 'remove_cleat',
    'remove_shelf_cleat', 'bottom_shelf_inset', 'double_panel_right',
    'include_center_back', 'center_back_location', 'remove_center_back',
    'door_pull_location', 'open_door',
)


def _ops():
    from .operators import ops_closet
    return ops_closet


def _bp(bay):
    return bay.hb_closet_bay


def _root(bay):
    return types_closets.find_starter_root(bay)


# ---- The top opening --------------------------------------------------------

def _top_height(bay):
    return _ops()._top_opening_height(bay)


def _get_top(bay):
    return float(_top_height(bay) or 0.0)


def _set_top(bay, target):
    """The top opening is as tall as the gap between the top shelf and
    the top of the bay, so a new height moves that shelf by the
    difference; what is below it stays where it was put. A double hang
    has no shelf, so the rod the upper hang finishes at moves instead."""
    ops = _ops()
    current = ops._top_opening_height(bay)
    target = max(float(target), units.inch(1.0))
    if current is None or abs(current - target) <= 1e-6:
        return
    shelves = ops._bay_split_shelves(bay)
    if shelves:
        shelf = shelves[-1]
        below = (float(shelves[-2].get('hb_z_offset', 0.0))
                 if len(shelves) > 1 else 0.0)
        st = types_closets.run_sizes(bay).shelf_thickness
        floor = below + (st if len(shelves) > 1 else 0.0) + units.inch(1.0)
        z = float(shelf.get('hb_z_offset', 0.0)) + (current - target)
        shelf['hb_z_offset'] = float(max(floor, z))
    else:
        rod = ops._double_hang_lower_rod(bay)
        if rod is None:
            return
        rod['hb_z_offset'] = float(target + const.ROD_TOP_OFFSET)
        rod['hb_anchor_top'] = 1
    root = _root(bay)
    if root is not None:
        types_closets.recalculate_closet_starter(root)


def _get_top_standard(bay):
    return const.nearest_opening_height_key(_get_top(bay)) or 'CUSTOM'


def _set_top_standard(bay, value):
    if value != 'CUSTOM':
        _set_top(bay, const.opening_height(value))


def _get_height_standard(bay):
    """The standard height the bay stands at, or Custom while its
    height sits off the 32mm system."""
    return const.nearest_panel_height_key(_bp(bay).height) or 'CUSTOM'


def _set_height_standard(bay, value):
    """A height picked for one bay is that bay's own, as a typed one
    is behind its padlock."""
    if value == 'CUSTOM':
        return
    bp = _bp(bay)
    with types_closets.suspend_recalc():
        if not bp.unlock_height:
            bp.unlock_height = True
        bp.height = const.millimeter(int(value))
    root = _root(bay)
    if root is not None:
        types_closets.recalculate_closet_starter(root)


# ---- What the bay is built as ----------------------------------------------
# A bay keeps the standard configuration it was last built as, with a
# note of the parts that made it; once its parts change (a shelf or a
# drawer added, an opening changed) it reads as Custom. A bay never
# built as one, or cleared, reads as Open.

CONFIG_KEY = 'hb_bay_config'
CONFIG_PARTS_KEY = 'hb_bay_config_parts'
CUSTOM = 'CUSTOM'
OPEN = 'OPEN'


def _parts_note(bay):
    import re
    names = sorted(re.sub(r'\.\d+$', '', o.name) for o in bay.children_recursive)
    return "|".join(names)


def remember_config(bay, config):
    """Note that ``bay`` has just been built as ``config``."""
    bay[CONFIG_KEY] = str(config)
    bay[CONFIG_PARTS_KEY] = _parts_note(bay)


def forget_config(bay):
    """Note that ``bay`` is empty again, so it reads as Open."""
    for key in (CONFIG_KEY, CONFIG_PARTS_KEY):
        if key in bay:
            del bay[key]


def config_of(bay):
    key = bay.get(CONFIG_KEY)
    if not key:
        return OPEN
    if bay.get(CONFIG_PARTS_KEY) == _parts_note(bay):
        return key
    return CUSTOM


def _config_items():
    return ([(OPEN, "Open")]
            + [(cid, label) for group in types_closets.BAY_CONFIG_GROUPS
               for cid, label in group] + [(CUSTOM, "Custom")])


def _get_config(bay):
    key = config_of(bay)
    return key if key in dict(_config_items()) else CUSTOM


def _set_config(bay, value):
    """Rebuild the bay as a standard configuration, as Bay
    Configuration does, and leave it picked."""
    if value == CUSTOM or value == _get_config(bay):
        return
    context = bpy.context
    with context.temp_override(active_object=bay, object=bay,
                               selected_objects=[bay]):
        if value == OPEN:
            bpy.ops.hb_closets.clear_bay()
        else:
            bpy.ops.hb_closets.change_bay(config=value)
    try:
        layer = context.view_layer
        if layer.objects.get(bay.name) is bay:
            for o in list(layer.objects):
                if o is not bay and o.select_get(view_layer=layer):
                    o.select_set(False, view_layer=layer)
            bay.select_set(True, view_layer=layer)
            layer.objects.active = bay
    except Exception:
        pass


def _ensure():
    from ...operators import prop_proxy as P
    if SCHEMA in P._schemas:
        return
    from . import opening_card, props_closets
    props = {
        name: opening_card.rna_prop(
            P, props_closets.Closet_Bay_Props, _bp, name)
        for name in _OWN}
    props.update({
        'config': P.computed(_get_config, _set_config, type='ENUM',
                             items=_config_items()),
        'top_opening': P.computed(_get_top, _set_top, unit='LENGTH',
                                  precision=4, hard_min=units.inch(1.0)),
        'height_standard': P.computed(
            _get_height_standard, _set_height_standard, type='ENUM',
            items=([i[:2] for i in const.PANEL_HEIGHT_ITEMS]
                   + [('CUSTOM', "Custom (off the 32mm holes)")])),
        'top_standard': P.computed(
            _get_top_standard, _set_top_standard, type='ENUM',
            items=([i[:2] for i in const.OPENING_HEIGHT_ITEMS]
                   + [('CUSTOM', "Custom")])),
    })
    P.register(SCHEMA, props)


def owner(bay):
    """The bay as the field engine takes it."""
    from ...operators import prop_proxy
    _ensure()
    return prop_proxy.owner(bay, SCHEMA)


# ---- Fields -----------------------------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def summary(bay):
    bp = _bp(bay)
    return f"{_dist(bp.width)} x {_dist(bp.height)}"


def _construction_fields(bay):
    bp = _bp(bay)

    def shelf_cleat(_ow):
        # Only the mid-shelf configuration stands a cleat behind a shelf.
        return any(c.get('hb_shelf_cleat') for c in bay.children)

    def shares_panel(_ow):
        # A double panel splits the junction with the bay on the right,
        # so the last bay has none to double up on.
        root = _root(bay)
        count = len(_ops()._starter_bays(root)) if root is not None else 1
        return bp.bay_index < count - 1

    return (
        ('bool', 'remove_bottom', "Remove Bottom"),
        ('bool', 'remove_cleat', "Remove Cleat"),
        ('bool', 'remove_shelf_cleat', "Remove Shelf Cleat",
         {'when': shelf_cleat}),
        ('bool', 'double_panel_right', "Double Panel Right",
         {'when': shares_panel}),
        # On top of the run's Inset Bottom, and like it only where there
        # is a bottom shelf to set in.
        ('distance', 'bottom_shelf_inset', "Bottom Shelf Inset",
         {'when': lambda _ow: bp.floor_mounted and not bp.remove_bottom}),
    )


def _construction_summary(bay):
    bp = _bp(bay)
    said = []
    if bp.remove_bottom:
        said.append("No bottom")
    if bp.remove_cleat:
        said.append("No cleat")
    if bp.double_panel_right:
        said.append("Double panel")
    return ", ".join(said)


def _opening_fields(bay):
    def bottom(_ow):
        value = _ops()._bottom_opening_height(bay)
        return _dist(value) if value is not None else None

    return (
        ('enum', 'top_standard', "Top Opening"),
        ('distance', 'top_opening', "Top Height"),
        # What is left under it follows the top opening and the bay
        # height rather than being set itself.
        ('value', bottom, "Bottom Height"),
    )


def _front_fields(bay):
    bp = _bp(bay)
    return (
        ('number', 'open_door', "Open Door %"),
        ('enum', 'door_pull_location', "Pull Location",
         {'when': lambda _ow: bp.door_swing in ('LEFT', 'RIGHT', 'DOUBLE')}),
    )


def _divider_fields(bay):
    bp = _bp(bay)
    return (
        ('bool', 'include_center_back', "Centered"),
        ('distance', 'center_back_location', "From Front",
         {'when': lambda _ow: not bp.include_center_back}),
        # Only an older file can have the divider out; offered so it can
        # be put back.
        ('bool', 'remove_center_back', "Removed",
         {'when': lambda _ow: bp.remove_center_back}),
    )


def fields(bay):
    bp = _bp(bay)
    root = _root(bay)
    cls = types_closets.WRAP_CLASS_REGISTRY.get(
        root.get('CLASS_NAME', '') if root is not None else '',
        types_closets.ClosetStarter)

    def off_holes():
        return not const.nearest_panel_height_key(bp.height)

    out = [
        ('locked', 'width', "Width", {'unlock': 'unlock_width'}),
        # The height is a pick off the standard list; the typed field
        # shows only for a bay standing off the holes.
        ('locked', 'height', "Height",
         {'unlock': 'unlock_height', 'pick': 'height_standard',
          'when': lambda _ow: not off_holes()}),
        ('locked', 'height', "Height",
         {'unlock': 'unlock_height', 'when': lambda _ow: off_holes()}),
        ('enum', 'height_standard', "Standard Height",
         {'when': lambda _ow: off_holes()}),
        ('locked', 'depth', "Depth", {'unlock': 'unlock_depth'}),
        ('bool', 'floor_mounted', "Floor Mounted"),
        ('group', 'cl_bay_more', "Construction",
         {'summary': lambda _ow: _construction_summary(bay),
          'fields': _construction_fields(bay)}),
    ]
    # Only a bay with a shelf across it (or a double hang) has a top
    # opening to size.
    if _top_height(bay) is not None:
        out.append(('group', 'cl_bay_openings', "Openings", {
            'summary': lambda _ow: _dist(_get_top(bay)),
            'fields': _opening_fields(bay)}))
    # A front across the whole bay has no opening to hold its settings.
    if bp.door_swing:
        out.append(('group', 'cl_bay_front', "Front", {
            'summary': lambda _ow: bp.door_swing.replace('_', ' ').title(),
            'fields': _front_fields(bay)}))
    # The divider between a double-sided island's two faces.
    if getattr(cls, 'is_double', False):
        out.append(('group', 'cl_bay_divider', "Center Divider", {
            'summary': lambda _ow: ("Centered" if bp.include_center_back
                                    else _dist(bp.center_back_location)),
            'fields': _divider_fields(bay)}))
    return tuple(out)


def page_fields(bay):
    """The bay's own page, laid out as a cabinet bay's: what it is built
    as, its sizes, then the rest in folds."""
    out = [('enum', 'config', "Configuration")] + list(fields(bay))
    at = next((i for i, f in enumerate(out) if f[0] == 'group'), len(out))
    out.insert(at, ('gap', None, None))
    return tuple(out)
