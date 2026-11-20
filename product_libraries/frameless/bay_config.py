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
from ..common import door_labels as DL

CUSTOM = 'CUSTOM'

# The presets the right-click Change Configuration menu offers, by
# cabinet type, in its order.
PRESETS = {
    'BASE': (
        ('LEFT_DOOR', DL.LEFT_SWING),
        ('RIGHT_DOOR', DL.RIGHT_SWING),
        ('DOUBLE_DOORS', DL.DOUBLE),
        ('DOOR_DRAWER', DL.DRAWER_1_DOOR),
        ('1_DRAWER_2_DOOR', DL.DRAWER_2_DOORS),
        ('2_DRAWER_2_DOOR', DL.TWO_DRAWERS_2_DOORS),
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
        ('LEFT_DOOR', DL.LEFT_SWING),
        ('RIGHT_DOOR', DL.RIGHT_SWING),
        ('DOUBLE_DOORS', DL.DOUBLE),
        ('FLIP_UP_DOOR', "Lift Up Door"),
        ('LEFT_STACKED_DOOR', DL.LEFT_STACKED),
        ('RIGHT_STACKED_DOOR', DL.RIGHT_STACKED),
        ('DOUBLE_STACKED_DOOR', DL.DOUBLE_STACKED),
        ('DOORS_WITH_1_DRAWER', DL.DOORS_WITH_1_DRAWER),
        ('DOORS_WITH_2_DRAWER', DL.DOORS_WITH_2_DRAWERS),
        ('DOORS_WITH_3_DRAWER', DL.DOORS_WITH_3_DRAWERS),
        ('DOORS_WITH_PULLOUT', "Doors with Pullout"),
        ('PULLOUT', "Pullout"),
        ('FALSE_FRONT', "False Front"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('OPEN', "Open"),
    ),
    'TALL': (
        ('LEFT_DOOR', DL.LEFT_SWING),
        ('RIGHT_DOOR', DL.RIGHT_SWING),
        ('DOUBLE_DOORS', DL.DOUBLE),
        ('LEFT_STACKED_DOOR', DL.LEFT_STACKED),
        ('RIGHT_STACKED_DOOR', DL.RIGHT_STACKED),
        ('DOUBLE_STACKED_DOOR', DL.DOUBLE_STACKED),
        ('LEFT_3_STACKED_DOOR', DL.LEFT_3_STACKED),
        ('RIGHT_3_STACKED_DOOR', DL.RIGHT_3_STACKED),
        ('DOUBLE_3_STACKED_DOOR', DL.DOUBLE_3_STACKED),
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
    keep_picked(bpy.context, bay_obj)


def keep_picked(context, obj):
    """After a rebuild: give the cabinet's new cages the look of the
    selection mode (they come in plain, so the mode's own cages would be
    hidden and unclickable), and leave ``obj`` picked and active so the
    page stays on it."""
    from ... import hb_utils
    try:
        layer = context.view_layer
        for o in list(layer.objects):
            if o.select_get(view_layer=layer):
                o.select_set(False, view_layer=layer)
        obj.select_set(True, view_layer=layer)
        layer.objects.active = obj
    except Exception as ex:
        print('Home Builder: could not pick %s: %s' % (obj.name, ex))
    cabinet = hb_utils.get_cabinet_bp(obj)
    if cabinet is not None:
        # Cages start hidden, as the mode leaves those it does not offer
        # (and an outer opening around the insert it offers), then the
        # mode shows its own again.
        for o in cabinet.children_recursive:
            if 'IS_GEONODE_CAGE' in o and o is not obj:
                o.display_type = 'WIRE'
                o.hide_viewport = True
        from .operators.ops_interior import show_in_selection_mode
        show_in_selection_mode(context, cabinet)
    _hold_pick(obj.name)


def _hold_pick(name):
    """A dialog the change opens behind itself (a new pullout asks which
    product it holds) drops the selection as it comes up, leaving the
    pick active but unselected and the page empty. Pick it again once
    that has happened, if it is still the active object."""
    def again():
        try:
            layer = bpy.context.view_layer
            obj = bpy.data.objects.get(name)
            if obj is not None and layer.objects.active is obj \
                    and not obj.select_get(view_layer=layer):
                obj.select_set(True, view_layer=layer)
        except Exception:
            pass
        return None
    for delay in (0.1, 0.3, 0.8):
        bpy.app.timers.register(again, first_interval=delay)


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
    splitter = _splitter(bay_obj)
    if splitter is not None:
        set_splitter_front(context, splitter, index, value)


def set_splitter_front(context, splitter, index, value):
    from .operators.ops_opening import set_front_heights
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
    splitter = _splitter(bay_obj)
    if splitter is not None:
        release_splitter_front(context, splitter, index)


def release_splitter_front(context, splitter, index):
    from .operators.ops_opening import set_front_heights
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
    splitter_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        splitter = bpy.data.objects.get(self.splitter_name) \
            if self.splitter_name else None
        if splitter is not None:
            release_splitter_front(context, splitter, self.index)
            return {'FINISHED'}
        bay_obj = bpy.data.objects.get(self.bay_name)
        if bay_obj is None:
            return {'CANCELLED'}
        release_front(context, bay_obj, self.index)
        return {'FINISHED'}


# ---- An opening's front ---------------------------------------------------------
#
# An opening holds its front as an insert, itself an opening; a page
# picked on either shows the same front. Changing the front rebuilds the
# outer opening, as Change Opening does.

OPENING_TAG = 'IS_FRAMELESS_OPENING_CAGE'
_SPLITTER_TAGS = ('IS_FRAMELESS_SPLITTER_VERTICAL_CAGE',
                  'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE')

FRONT_KINDS = (
    ('DOOR', "Door"),
    ('FLIP_UP_DOOR', "Lift Up Door"),
    ('SINGLE_DRAWER', "Drawer"),
    ('PULLOUT', "Pullout"),
    ('FALSE_FRONT', "False Front"),
    ('APPLIANCE', "Appliance"),
    ('OPEN_WITH_SHELVES', "Open with Shelves"),
    ('OPEN', "Open"),
    ('SPLIT', "Split"),
)
_KIND_OF_TOKEN = {'LIFT': 'FLIP_UP_DOOR', 'DRAWER': 'SINGLE_DRAWER',
                  'PULLOUT': 'PULLOUT', 'FALSE_FRONT': 'FALSE_FRONT',
                  'APPLIANCE': 'APPLIANCE', 'SHELVES': 'OPEN_WITH_SHELVES'}
_WIDE_DOOR = 24 * 0.0254     # wider than this a new door is a pair


def outer_opening(opening_obj):
    """The opening a splitter (or the bay) holds, around its insert."""
    o = opening_obj
    while o.parent is not None and o.parent.get(OPENING_TAG) \
            and not any(o.parent.get(t) for t in _SPLITTER_TAGS):
        o = o.parent
    return o


def front_opening(opening_obj):
    """The insert that carries the front's settings: the opening itself
    or the one opening inside it."""
    o = opening_obj
    while True:
        if 'Door Swing' in o or any(
                c.get(t) for c in o.children for t in _SPLITTER_TAGS):
            return o
        kids = [c for c in o.children if c.get(OPENING_TAG)]
        if len(kids) != 1:
            return o
        o = kids[0]


def is_split(opening_obj):
    return any(c.get(t) for c in outer_opening(opening_obj).children_recursive
               for t in _SPLITTER_TAGS)


def front_kind(opening_obj):
    outer = outer_opening(opening_obj)
    if is_split(outer):
        return 'SPLIT'
    leaves = _leaf_openings(outer) or [outer]
    token = _token(leaves[0])
    if _kind_name(token) == "Door":
        return 'DOOR'
    return _KIND_OF_TOKEN.get(token, 'OPEN')


def set_front_kind(context, opening_obj, value):
    """Rebuild the opening with another front. The outer opening is left
    picked, as the insert the page was on is replaced."""
    if value == 'SPLIT' or value == front_kind(opening_obj):
        return
    outer = outer_opening(opening_obj)
    opening_type = value
    if value == 'DOOR':
        from ...hb_types import GeoNodeObject
        try:
            width = float(GeoNodeObject(outer).get_input('Dim X'))
        except Exception:
            width = 0.0
        opening_type = 'DOUBLE_DOORS' if width > _WIDE_DOOR else 'LEFT_DOOR'
    parent = outer.parent
    if parent is not None and parent.get('IS_FRAMELESS_BAY_CAGE')             and opening_type in SIGNATURES:
        # The bay's only opening: rebuilt from the bay, as a layout of
        # one front, so no insert is left nested in the old one.
        with context.temp_override(active_object=parent, object=parent,
                                   selected_objects=[parent]):
            bpy.ops.hb_frameless.change_bay_opening(opening_type=opening_type)
        outer = next((c for c in parent.children if c.get(OPENING_TAG)), parent)
    else:
        with context.temp_override(active_object=outer, object=outer,
                                   selected_objects=[outer]):
            bpy.ops.hb_frameless.change_opening_type(opening_type=opening_type)
    keep_picked(context, front_opening(outer))


def opening_front_row(opening_obj):
    """(splitter, index, height, held) for an opening that is one of
    several fronts in a stack, else None."""
    from . import solver_frameless
    from .operators.ops_opening import front_height_rows
    outer = outer_opening(opening_obj)
    splitter = outer.parent
    if splitter is None or not splitter.get(solver_frameless.SPLITTER_VERTICAL_TAG):
        return None
    index = next((key[1] for key, o in
                  solver_frameless.split_parts(splitter).items()
                  if key[0] == 'OPENING' and o == outer), None)
    if index is None:
        return None
    rows = front_height_rows(splitter)
    if sum(1 for r in rows if r[4]) < 2:
        return None
    for i, _label, height, held, has_front in rows:
        if i == index and has_front:
            return splitter, index, height, held
    return None


def _opening_front_type():
    from ...operators import prop_proxy

    def get(obj):
        return front_kind(obj)

    def set(obj, value):
        set_front_kind(bpy.context, obj, value)
    return prop_proxy.computed(get, set, type='ENUM', items=list(FRONT_KINDS))


def _opening_front_height():
    from ...operators import prop_proxy

    def get(obj):
        row = opening_front_row(obj)
        return float(row[2]) if row else 0.0

    def set(obj, value):
        row = opening_front_row(obj)
        if row is not None:
            set_splitter_front(bpy.context, row[0], row[1], value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def opening_props():
    """The opening page's front fields, for its schema."""
    return {'front_type': _opening_front_type(),
            'front_height': _opening_front_height()}


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
