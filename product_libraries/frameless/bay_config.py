"""What a frameless bay is built as, read against the Change Configuration
presets, and a pick of another.

A bay's fronts are read top to bottom, one token each: a door by its
swing (D0 left, D1 right, D2 double), a lift up door, a drawer, a false
front, a pullout, an appliance opening, an open opening with shelves.
Each preset is the stack of tokens Change Configuration builds; the
first preset of the cabinet's list that matches names the bay, and a
bay changed since (an opening split, a front swapped) reads as Custom.
"""

import bpy

CUSTOM = 'CUSTOM'

# The presets the right-click Change Configuration menu offers, by
# cabinet type, in its order.
PRESETS = {
    'BASE': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('DOOR_DRAWER', "1 Drawer 1 Door"),
        ('1_DRAWER_2_DOOR', "1 Drawer 2 Door"),
        ('2_DRAWER_2_DOOR', "2 Drawer 2 Door"),
        ('4_DRAWER_STACK', "4 Drawers"),
        ('3_DRAWER_STACK', "3 Drawers"),
        ('2_DRAWER_STACK', "2 Drawers"),
        ('SINGLE_DRAWER', "1 Drawer"),
        ('FALSE_FRONT', "False Front"),
        ('PULLOUT', "Pullout"),
        ('PULLOUT_WITH_DRAWER', "Pullout with Drawer"),
        ('MICROWAVE_DRAWER', "Microwave with Drawer"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
    'UPPER': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('FLIP_UP_DOOR', "Lift Up Door"),
        ('LEFT_STACKED_DOOR', "Left Swing Stacked Door"),
        ('RIGHT_STACKED_DOOR', "Right Swing Stacked Door"),
        ('DOUBLE_STACKED_DOOR', "Double Stacked Door"),
        ('DOORS_WITH_1_DRAWER', "Doors with 1 Drawer"),
        ('DOORS_WITH_2_DRAWER', "Doors with 2 Drawers"),
        ('DOORS_WITH_3_DRAWER', "Doors with 3 Drawers"),
        ('DOORS_WITH_PULLOUT', "Doors with Pullout"),
        ('PULLOUT', "Pullout"),
        ('FALSE_FRONT', "False Front"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
    'TALL': (
        ('LEFT_DOOR', "Left Swing Door"),
        ('RIGHT_DOOR', "Right Swing Door"),
        ('DOUBLE_DOORS', "Double Doors"),
        ('LEFT_STACKED_DOOR', "Left Swing Stacked Door"),
        ('RIGHT_STACKED_DOOR', "Right Swing Stacked Door"),
        ('DOUBLE_STACKED_DOOR', "Double Stacked Door"),
        ('LEFT_3_STACKED_DOOR', "Left Swing 3 Stacked Door"),
        ('RIGHT_3_STACKED_DOOR', "Right Swing 3 Stacked Door"),
        ('DOUBLE_3_STACKED_DOOR', "Double 3 Stacked Door"),
        ('APPLIANCE', "Built In Appliance"),
        ('DOUBLE_APPLIANCE', "Built In Double Appliance"),
        ('DOORS_WITH_TALL_PULLOUT', "Doors with Tall Pullout"),
        ('TALL_PULLOUT', "Tall Pullout"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
}

# The fronts each preset builds, top to bottom.
SIGNATURES = {
    'LEFT_DOOR': ('D0',),
    'RIGHT_DOOR': ('D1',),
    'DOUBLE_DOORS': ('D2',),
    'FLIP_UP_DOOR': ('LIFT',),
    'LEFT_STACKED_DOOR': ('D0', 'D0'),
    'RIGHT_STACKED_DOOR': ('D1', 'D1'),
    'DOUBLE_STACKED_DOOR': ('D2', 'D2'),
    'LEFT_3_STACKED_DOOR': ('D0', 'D0', 'D0'),
    'RIGHT_3_STACKED_DOOR': ('D1', 'D1', 'D1'),
    'DOUBLE_3_STACKED_DOOR': ('D2', 'D2', 'D2'),
    'DOOR_DRAWER': ('DRAWER', 'D0'),
    '1_DRAWER_2_DOOR': ('DRAWER', 'D2'),
    '2_DRAWER_2_DOOR': ('DRAWER', 'DRAWER', 'D2'),
    'SINGLE_DRAWER': ('DRAWER',),
    '2_DRAWER_STACK': ('DRAWER',) * 2,
    '3_DRAWER_STACK': ('DRAWER',) * 3,
    '4_DRAWER_STACK': ('DRAWER',) * 4,
    'PULLOUT': ('PULLOUT',),
    'TALL_PULLOUT': ('PULLOUT',),
    'PULLOUT_WITH_DRAWER': ('DRAWER', 'PULLOUT'),
    'DOORS_WITH_TALL_PULLOUT': ('D2', 'PULLOUT'),
    'DOORS_WITH_PULLOUT': ('D2', 'PULLOUT'),
    'DOORS_WITH_1_DRAWER': ('D2', 'DRAWER'),
    'DOORS_WITH_2_DRAWER': ('D2', 'DRAWER', 'DRAWER'),
    'DOORS_WITH_3_DRAWER': ('D2', 'DRAWER', 'DRAWER', 'DRAWER'),
    'FALSE_FRONT': ('FALSE_FRONT',),
    'MICROWAVE_DRAWER': ('APPLIANCE', 'DRAWER'),
    'APPLIANCE': ('D2', 'APPLIANCE', 'D2'),
    'DOUBLE_APPLIANCE': ('D2', 'APPLIANCE', 'APPLIANCE', 'DRAWER'),
    'OPEN_WITH_SHELVES': ('SHELVES',),
    'OPEN': (),
}


def cabinet_kind(bay_obj):
    """The preset list a bay takes: its cabinet's type, base otherwise."""
    from ... import hb_utils
    root = hb_utils.get_cabinet_bp(bay_obj)
    kind = root.get('CABINET_TYPE', 'BASE') if root is not None else 'BASE'
    return kind if kind in PRESETS else 'BASE'


def _leaf_openings(bay_obj):
    leaves = [o for o in bay_obj.children_recursive
              if o.get('IS_FRAMELESS_OPENING_CAGE')
              and not any(c.get('IS_FRAMELESS_OPENING_CAGE')
                          for c in o.children_recursive)]
    leaves.sort(key=lambda o: -o.matrix_world.translation.z)
    return leaves


def _token(opening):
    children = list(opening.children)
    if any(c.get('IS_FLIP_UP_DOOR') for c in children):
        return 'LIFT'
    if 'Door Swing' in opening:
        try:
            return 'D%d' % int(opening['Door Swing'])
        except (TypeError, ValueError):
            return 'D?'
    if any(c.get('IS_PULLOUT_FRONT') for c in children):
        return 'PULLOUT'
    if any(c.get('IS_DRAWER_FRONT') for c in children):
        if any(c.get('IS_DRAWER_FRONT') and c.get('False Front')
               for c in children):
            return 'FALSE_FRONT'
        return 'DRAWER'
    if any(c.get('IS_APPLIANCE_TEXT') for c in children):
        return 'APPLIANCE'
    if 'Shelf Quantity' in opening:
        return 'SHELVES'
    return 'OTHER'


def signature(bay_obj):
    return tuple(_token(o) for o in _leaf_openings(bay_obj))


def detect(bay_obj):
    """The preset the bay is built as, or CUSTOM."""
    sig = signature(bay_obj)
    for key, _label in PRESETS[cabinet_kind(bay_obj)]:
        if SIGNATURES.get(key) == sig:
            return key
    return CUSTOM


def items(kind):
    return list(PRESETS[kind]) + [(CUSTOM, "Custom")]


def apply(bay_obj, key):
    """Rebuild the bay as the preset ``key``, as Change Configuration
    does."""
    if key == CUSTOM or key not in SIGNATURES:
        return
    with bpy.context.temp_override(active_object=bay_obj, object=bay_obj,
                                   selected_objects=[bay_obj]):
        bpy.ops.hb_frameless.change_bay_opening(opening_type=key)


# ---- The page's field ---------------------------------------------------------

SCHEMA_PREFIX = 'FL_BAY_'


def schema_key(bay_obj):
    return SCHEMA_PREFIX + cabinet_kind(bay_obj)


def _config(kind):
    from ...operators import prop_proxy

    def get(obj):
        return detect(obj)

    def set(obj, value):
        if value != detect(obj):
            apply(obj, value)
    return prop_proxy.computed(get, set, type='ENUM', items=items(kind))


# ---- Front heights -------------------------------------------------------------
#
# The bay's fronts typed by height, as the Door/Drawer Sizes dialog types
# them: a typed height is held and the fronts left free share what is
# left. Where doors stand with drawers or pullouts only the others are
# offered, and the doors take up the rest.

FRONT_ROWS = 8

_KIND_NAMES = {'DRAWER': "Drawer", 'PULLOUT': "Pullout", 'LIFT': "Lift Up Door",
               'FALSE_FRONT': "False Front"}
_PLACES = {2: ("Top", "Bottom"), 3: ("Top", "Middle", "Bottom"),
           4: ("Top", "Second", "Third", "Bottom")}


def _splitter(bay_obj):
    from .operators.ops_opening import front_height_splitter
    return front_height_splitter(bay_obj)


def _kind_name(token):
    if token.startswith('D') and (token[1:].isdigit() or token == 'D?'):
        return "Door"
    return _KIND_NAMES.get(token, "Front")


def front_rows(bay_obj):
    """The fronts the page offers, top to bottom:
    ``(index, label, height, held)``, index being the opening's place in
    the bay's splitter."""
    from . import solver_frameless
    from .operators.ops_opening import front_height_rows
    splitter = _splitter(bay_obj)
    if splitter is None:
        return []
    parts = solver_frameless.split_parts(splitter)
    rows = []
    for i, _label, height, held, has_front in front_height_rows(splitter):
        if not has_front:
            continue
        opening = parts.get(('OPENING', i))
        leaves = _leaf_openings(opening) if opening is not None else []
        token = _token(leaves[0] if leaves else opening)
        name = _kind_name(token)
        if len(leaves) > 1 and name != "Door":
            # Fronts side by side across the row, sized together.
            name += "s"
        rows.append((i, name, height, held))
    if len(rows) < 2:
        return []
    names = {r[1] for r in rows}
    if "Door" in names and len(names) > 1:
        rows = [r for r in rows if r[1] != "Door"]
    out = []
    for name in dict.fromkeys(r[1] for r in rows):
        same = [r for r in rows if r[1] == name]
        places = _PLACES.get(len(same))
        for n, (i, _name, height, held) in enumerate(same):
            if len(same) == 1:
                label = name
            elif places:
                label = "%s %s" % (places[n], name)
            else:
                label = "%s %d" % (name, n + 1)
            out.append((i, label, height, held))
    out.sort(key=lambda r: r[0])
    return out


def _heights(splitter):
    from .operators.ops_opening import front_height_rows
    rows = front_height_rows(splitter)
    return [r[2] for r in rows], [r[3] for r in rows]


def set_front(context, bay_obj, index, value):
    """Hold front ``index`` at ``value``. With every front then held, one
    is let go to take up the difference: the bottom one, or the one above
    it when the bottom was typed."""
    from .operators.ops_opening import set_front_heights
    splitter = _splitter(bay_obj)
    if splitter is None:
        return
    heights, holds = _heights(splitter)
    if not 1 <= index <= len(heights):
        return
    heights[index - 1] = float(value)
    holds[index - 1] = True
    count = len(heights)
    if count > 1 and all(holds):
        release = count - 1 if index == count else count
        holds[release - 1] = False
    set_front_heights(context, splitter,
                      [h if held else None for h, held in zip(heights, holds)])


def release_front(context, bay_obj, index):
    """Let front ``index`` go back to sharing what the held ones leave."""
    from .operators.ops_opening import set_front_heights
    splitter = _splitter(bay_obj)
    if splitter is None:
        return
    heights, holds = _heights(splitter)
    if 1 <= index <= len(heights):
        holds[index - 1] = False
    set_front_heights(context, splitter,
                      [h if held else None for h, held in zip(heights, holds)])


def _front(index):
    from ...operators import prop_proxy

    def get(obj):
        for i, _label, height, _held in front_rows(obj):
            if i == index:
                return float(height)
        return 0.0

    def set(obj, value):
        set_front(bpy.context, obj, index, value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


class hb_frameless_OT_release_front_height(bpy.types.Operator):
    bl_idname = "hb_frameless.release_front_height"
    bl_label = "Let Height Share"
    bl_description = ("Stop holding this front's height; it shares what the "
                      "held fronts leave")
    bl_options = {'UNDO', 'INTERNAL'}

    bay_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        bay_obj = bpy.data.objects.get(self.bay_name)
        if bay_obj is None:
            return {'CANCELLED'}
        release_front(context, bay_obj, self.index)
        return {'FINISHED'}


def register_schemas():
    from ...operators import prop_proxy
    for kind in PRESETS:
        props = {'config': _config(kind)}
        for i in range(1, FRONT_ROWS + 1):
            props['front_%d' % i] = _front(i)
        prop_proxy.register(SCHEMA_PREFIX + kind, props)


def register():
    bpy.utils.register_class(hb_frameless_OT_release_front_height)
    register_schemas()


def unregister():
    unregister_schemas()
    try:
        bpy.utils.unregister_class(hb_frameless_OT_release_front_height)
    except RuntimeError:
        pass


def unregister_schemas():
    from ...operators import prop_proxy
    for kind in PRESETS:
        prop_proxy.unregister(SCHEMA_PREFIX + kind)
