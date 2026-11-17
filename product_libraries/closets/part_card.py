"""Closet parts that stand on their own, on the viewport panel's
SELECTED tab: a slab countertop, a countertop placed over some of a
run's bays, a rod hung on a bare wall, a misc part and an accessory (its page is
accessory_card's).

Each had a dialog of its own. Its settings are fields here instead, in
groups that fold, and every change shows as it is made. The part's
commands follow under Quick Actions, as on every other page.
"""

import bpy

from ... import hb_types, units
from . import materials_closets, types_closets


SOURCE_KEY = 'CLOSET_PARTS'

WALL_ROD_SCHEMA = 'CL_WALL_ROD'
MISC_SCHEMA = 'CL_MISC_PART'


def _ops():
    from .operators import ops_closet
    return ops_closet


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, object) for a picked closet part with a page of its own,
    or None."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    from . import accessory_card
    cage = accessory_card.cage_of(obj)
    if cage is not None:
        return ('accessory', cage)
    slab = _ops()._slab_of(obj)
    if slab is not None:
        return ('slab', slab)
    if types_closets.bay_countertop_entry(obj)[1] is not None:
        return ('bay_top', obj)
    role = obj.get('hb_part_role')
    if role == types_closets.PART_ROLE_ROD and obj.get(types_closets.PROP_WALL_ROD):
        return ('wall_rod', obj)
    if role == types_closets.PART_ROLE_MISC:
        return ('misc', obj)
    return None


# ---- Schemas ----------------------------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _off_wall(obj):
    return max(0.0, -float(obj.location.y))


def _layout_rod(obj, context):
    types_closets.layout_wall_rod(obj)


def _after_misc(obj, context):
    if types_closets.is_loose_l_shelf(obj):
        types_closets.layout_loose_l_shelf(obj)
    if materials_closets.is_bandable_misc_part(obj):
        # Show the banded edges in the band, the rest as bare core.
        materials_closets.apply_to_part(obj)


def _register_schemas():
    from ...operators import prop_proxy as P

    def id_flag(key):
        return P.computed(lambda o: bool(o.get(key)),
                          lambda o, v: o.__setitem__(key, 1 if v else 0),
                          type='BOOLEAN')

    def rod_width_get(obj):
        try:
            return float(hb_types.GeoNodeObject(obj).get_input('Dim X') or 0.0)
        except Exception:
            return float(types_closets.WALL_ROD_LENGTH)

    def rod_width_set(obj, value):
        hb_types.GeoNodeObject(obj).set_input(
            'Dim X', max(float(value), units.inch(1.0)))

    def rod_depth(key):
        # A rod saved before it carried its own figures reads its
        # distance off the wall from where it stands.
        return P.computed(lambda o: float(o.get(key, _off_wall(o))),
                          lambda o, v: o.__setitem__(key, float(v)),
                          unit='LENGTH', precision=4, hard_min=0.0)

    def axis(attr, index, unit):
        def get(obj):
            return float(getattr(obj, attr)[index])

        def set(obj, value):
            getattr(obj, attr)[index] = float(value)
        return P.computed(get, set, unit=unit, precision=4)

    P.register(WALL_ROD_SCHEMA, {
        'width': P.computed(rod_width_get, rod_width_set, unit='LENGTH',
                            precision=4, hard_min=0.0),
        'height': axis('location', 2, 'LENGTH'),
        'set_from_front': id_flag(types_closets.PROP_WALL_ROD_SET_FROM_FRONT),
        'from_front': rod_depth(types_closets.PROP_WALL_ROD_FROM_FRONT),
        'from_rear': rod_depth(types_closets.PROP_WALL_ROD_FROM_REAR),
        'remove_hangers': id_flag(types_closets.PROP_WALL_ROD_REMOVE_HANGERS),
    }, after=_layout_rod)

    def l_value(key, default=0.0):
        return P.computed(lambda o: float(o.get(key, default)),
                          lambda o, v: o.__setitem__(key, float(v)),
                          unit='LENGTH', precision=4, hard_min=0.0)

    props = {
        'name': P.computed(lambda o: o.name,
                           lambda o, v: setattr(o, 'name', str(v)) if v else None,
                           type='STRING'),
        'length': P.node_input('Length'),
        'width': P.node_input('Width'),
        'l_left_depth': l_value(types_closets.PROP_LOOSE_L_LEFT),
        'l_right_depth': l_value(types_closets.PROP_LOOSE_L_RIGHT),
        'l_use_radius': P.computed(
            lambda o: bool(o.get(types_closets.PROP_LOOSE_L_ROUND, True)),
            lambda o, v: o.__setitem__(types_closets.PROP_LOOSE_L_ROUND, bool(v)),
            type='BOOLEAN'),
        'l_corner_radius': l_value(types_closets.PROP_LOOSE_L_RADIUS),
        'loc_x': axis('location', 0, 'LENGTH'),
        'loc_y': axis('location', 1, 'LENGTH'),
        'loc_z': axis('location', 2, 'LENGTH'),
        'rot_x': axis('rotation_euler', 0, 'ROTATION'),
        'rot_y': axis('rotation_euler', 1, 'ROTATION'),
        'rot_z': axis('rotation_euler', 2, 'ROTATION'),
    }
    for edge in materials_closets.MISC_BAND_EDGES:
        key = 'hb_band_' + edge
        props['band_' + edge.lower()] = P.computed(
            lambda o, key=key: bool(o.get(key)),
            lambda o, v, key=key: o.__setitem__(key, bool(v)),
            type='BOOLEAN')
    P.register(MISC_SCHEMA, props, after=_after_misc)


# ---- Fields -----------------------------------------------------------------

def _rod_from_front(owner):
    return bool(owner.id_data.get(types_closets.PROP_WALL_ROD_SET_FROM_FRONT))


def _rod_from_rear(owner):
    return not _rod_from_front(owner)


WALL_ROD_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Vertical Location"),
    ('bool', 'set_from_front', "Measure From Front"),
    ('distance', 'from_front', "From Front", {'when': _rod_from_front}),
    ('distance', 'from_rear', "From Rear", {'when': _rod_from_rear}),
    ('bool', 'remove_hangers', "Remove Hangers"),
)


def _loose_l(owner):
    return types_closets.is_loose_l_shelf(owner.id_data)


def _l_rounded(owner):
    return _loose_l(owner) and bool(
        owner.id_data.get(types_closets.PROP_LOOSE_L_ROUND, True))


def _bandable(owner):
    return materials_closets.is_bandable_misc_part(owner.id_data)


def _thickness_text(owner):
    try:
        return _dist(float(hb_types.GeoNodeCutpart(owner.id_data)
                           .get_input('Thickness')))
    except Exception:
        return ""


def _band_summary(owner):
    on = [edge for edge in materials_closets.MISC_BAND_EDGES
          if owner.id_data.get('hb_band_' + edge)]
    return ", ".join(on) if on else "None"


def _place_summary(owner):
    obj = owner.id_data
    return "%s, %s off floor" % (_dist(obj.location.x), _dist(obj.location.z))


MISC_FIELDS = (
    ('text', 'name', "Part Name"),
    ('distance', 'length', "Length"),
    ('distance', 'width', "Width"),
    # Thickness comes from the board the part is cut from.
    ('value', _thickness_text, "Thickness"),
    ('group', 'cl_misc_corner', "Corner", {'when': _loose_l, 'fields': (
        ('distance', 'l_left_depth', "Side Wall Wing Depth"),
        ('distance', 'l_right_depth', "Back Wall Wing Depth"),
        ('bool', 'l_use_radius', "Radius Front Corner"),
        ('distance', 'l_corner_radius', "Corner Radius", {'when': _l_rounded}),
    )}),
    ('group', 'cl_misc_location', "Location", {'summary': _place_summary, 'fields': (
        ('distance', 'loc_x', "Horizontal"),
        ('distance', 'loc_z', "Vertical"),
        ('distance', 'loc_y', "Off Wall"),
    )}),
    ('group', 'cl_misc_rotation', "Rotation", {'fields': (
        ('number', 'rot_x', "X"),
        ('number', 'rot_y', "Y"),
        ('number', 'rot_z', "Z"),
    )}),
    # Only a true misc part picks its banding; a loose back, cleat or
    # shelf bands the way that part always does.
    ('group', 'cl_misc_banding', "Edgebanding", {
        'when': _bandable, 'summary': _band_summary, 'fields': tuple(
            ('bool', 'band_' + edge.lower(), edge)
            for edge in materials_closets.MISC_BAND_EDGES)}),
)


def _cut_text(obj, name):
    try:
        return _dist(float(hb_types.GeoNodeCutpart(obj).get_input(name)))
    except Exception:
        return ""


def _top_fields(top_obj, sized):
    """A countertop's fields: a slab is sized by hand, one over a run's
    bays takes its size from them."""
    fields = []
    if sized:
        fields += [('distance', 'width', "Width"),
                   ('distance', 'depth', "Depth")]
    if top_obj is not None:
        fields += [
            ('value', lambda _o: _cut_text(top_obj, 'Length'), "Cut Length"),
            ('value', lambda _o: _cut_text(top_obj, 'Width'), "Cut Depth"),
        ]
        if sized:
            fields.append(('value', lambda _o: _cut_text(top_obj, 'Thickness'),
                           "Thickness"))
    fields += [
        ('group', 'cl_top_overhang', "Overhang", {
            'summary': lambda o: " / ".join(_dist(v) for v in (
                o.overhang_left, o.overhang_right, o.overhang_front)),
            'fields': (
                ('distance', 'overhang_left', "Left"),
                ('distance', 'overhang_right', "Right"),
                ('distance', 'overhang_front', "Front"),
            )}),
        ('bool', 'left_finished_end', "Finished End Left"),
        ('bool', 'right_finished_end', "Finished End Right"),
        ('bool', 'include_backsplash', "Backsplash"),
        ('distance', 'backsplash_height', "Backsplash Height",
         {'when': lambda o: o.include_backsplash}),
    ]
    return tuple(fields)


def _bay_top_part(root, entry):
    for child in root.children:
        if (child.get(types_closets.PROP_BAY_CTOP) == entry.uid
                and child.get(types_closets.PROP_BAY_CTOP_SLOT) == 'TOP'):
            return child
    return None


# ---- The page ---------------------------------------------------------------

def blocks(context, item):
    from ...operators import options_panel, prop_proxy
    kind, obj = item
    if kind == 'accessory':
        from . import accessory_card
        return accessory_card.blocks(context, obj)
    out = [('head', (obj.name, False, None))]
    if kind == 'slab':
        out.extend(options_panel.field_blocks(
            context, _top_fields(obj, True), obj.hb_closet_slab))
        props = context.scene.hb_closets
        out.append(('hint', "Material: %s (room Countertops option)" % (
            "closet material" if props.use_closet_material_for_countertops
            else props.closet_countertop_material)))
    elif kind == 'bay_top':
        root, entry = types_closets.bay_countertop_entry(obj)
        out.extend(options_panel.field_blocks(
            context, _top_fields(_bay_top_part(root, entry), False), entry))
        out.append(('hint', "Thickness follows the run's countertop"))
    elif kind == 'wall_rod':
        out.extend(options_panel.field_blocks(
            context, WALL_ROD_FIELDS, prop_proxy.owner(obj, WALL_ROD_SCHEMA)))
    else:
        out.extend(options_panel.field_blocks(
            context, MISC_FIELDS, prop_proxy.owner(obj, MISC_SCHEMA)))
    # The part's dialog is this page.
    from .selected_card import _actions
    _actions(context, out, obj, skip=(
        'hb_closets.slab_countertop_prompts', 'hb_closets.bay_countertop_prompts',
        'hb_closets.wall_rod_prompts', 'hb_closets.misc_part_prompts'))
    return out


def crumbs(context, item):
    return [(item[1].name, None)]


# ---- Lifecycle --------------------------------------------------------------

def register():
    _register_schemas()
    from ...operators import selected_tab
    # Ahead of the closet's own page: a countertop over a run's bays is
    # part of a closet, and is what was picked.
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs, first=True)


def unregister():
    try:
        from ...operators import prop_proxy, selected_tab
        selected_tab.unregister_source(SOURCE_KEY)
        prop_proxy.unregister(WALL_ROD_SCHEMA)
        prop_proxy.unregister(MISC_SCHEMA)
        from . import accessory_card
        accessory_card.unregister()
    except Exception:
        pass
