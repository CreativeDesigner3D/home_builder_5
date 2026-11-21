"""Frameless cabinets and products on the viewport panel's SELECTED tab.

The page reads the way the face frame cabinet's does. The title is
where the pick sits -- Cabinet > Bay 2 > Opening 1 > Door -- and a click
on a step above selects it. Under it are the cabinet's style, then tabs
that move between the cabinet and the bay, opening and part last picked
inside it, then the page for the level picked:

  Cabinet  -- size, toe kick, construction prompts
  Bay      -- its size and what its opening is built as
  Opening  -- the front, what is inside, its accessories
  Interior -- a shelf, a division or the interior itself
  Drawer   -- box construction, slides and what is in the drawer
  Part     -- a door, a side, anything with its own right-click menu

Each page ends with quick actions from the pick's right-click menu, All
Actions and the pick's own Properties dialog. Picking several cabinets
(or openings) and typing a value sets them all.

A frameless cabinet keeps its settings as custom properties and
geometry-node inputs rather than in a property group, so the fields go
through prop_proxy schemas: each write is followed by the solve the
cabinet's own dialog runs. Products (legs, panels, floating shelves,
valances ...) get their size and height off the floor.
"""

import bpy

from ... import hb_utils, hb_project, units


SOURCE_KEY = 'FRAMELESS'

BAY_GROUP = 'fl_bay'
OPENING_GROUP = 'fl_opening'
PRODUCT_GROUP = 'fl_product'

CABINET_SCHEMA = 'FL_CABINET'
OPENING_SCHEMA = 'FL_OPENING'
PRODUCT_SCHEMA = 'FL_PRODUCT'
MISC_PART_SCHEMA = 'FL_MISC_PART'
PART_EDGES_SCHEMA = 'FL_PART_EDGES'
PART_EDGES_GROUP = 'fl_part_edges'
FRONT_SCHEMA = 'FL_FRONT'
DOOR_STYLE_PREFIX = 'FL_DOOR_STYLE_'
STYLE_PREFIX = 'FL_STYLE_'
SCOPE_PREFIX = 'FL_SCOPE_'

TAG_BAY = 'IS_FRAMELESS_BAY_CAGE'
TAG_OPENING = 'IS_FRAMELESS_OPENING_CAGE'
TAG_INTERIOR = 'IS_FRAMELESS_INTERIOR_CAGE'

TOE_KICK_TYPES = ("Notch Ends to Floor", "Ladder Style", "Floating",
                  "Leg Levelers")

FINISHED_BOTTOMS = ("None", "1/4\" Panel", "3/4\" Panel")



# ---- Finding what is picked -------------------------------------------------

def _owning(obj, tag):
    while obj is not None:
        if obj.get(tag):
            return obj
        obj = obj.parent
    return None


def _under(obj, root):
    o = obj.parent if obj is not None else None
    while o is not None:
        if o == root:
            return True
        o = o.parent
    return False


def _items():
    from . import interior_items
    return interior_items


def _is_drawer_part(obj):
    return bool(obj.get('IS_DRAWER_BOX') or obj.get('IS_DRAWER_FRONT')
                or obj.get('IS_PULLOUT_FRONT'))


def _is_interior_part(obj):
    return bool(obj.get(TAG_INTERIOR) or obj.get('IS_FRAMELESS_INTERIOR_PART')
                or obj.get('IS_FRAMELESS_INTERIOR_SECTION')
                or hb_utils.get_interior_bp(obj) is not None)


def find(context):
    """(kind, root, bay, opening, part) for a picked frameless cabinet or
    part of one, or ('product', root, None, None, None), or None. `kind`
    is the level the page is on: 'cabinet', 'bay', 'opening',
    'interior' (the interior, a section or a shelf: `part`), 'drawer'
    (a drawer or pull-out's front or box: `part`, with `opening` the
    drawer's opening) or 'part' -- anything else with a right-click
    menu of its own."""
    from . import interior_page
    found = interior_page.focused(context)
    if found is not None:
        # The Interior page on a hidden section (or the whole interior),
        # while a visible object stays the pick.
        host, section = found
        root = hb_utils.get_cabinet_bp(host)
        if root is not None and 'IS_FRAMELESS_PRODUCT_CAGE' not in root:
            return ('interior', root, _owning(host, TAG_BAY),
                    host if host.get(TAG_OPENING) else None, section)
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    root = hb_utils.get_cabinet_bp(obj)
    if root is None:
        return None
    if 'IS_FRAMELESS_PRODUCT_CAGE' in root:
        return ('product', root, None, None, None)
    if obj == root:
        return ('cabinet', root, None, None, None)
    bay = _owning(obj, TAG_BAY)
    bay = bay if _under(bay, root) else None
    opening = _owning(obj, TAG_OPENING)
    opening = opening if _under(opening, root) else None
    if obj.get(TAG_BAY):
        return ('bay', root, obj, None, None)
    if obj.get(TAG_OPENING):
        return ('opening', root, bay, obj, None)
    if _is_drawer_part(obj):
        drawer = _items().drawer_opening_for(obj)
        if drawer is not None:
            return ('drawer', root, bay, drawer, obj)
    if _is_interior_part(obj):
        return ('interior', root, bay, opening, obj)
    from ...operators import generic_page
    if generic_page.menu_id(obj):
        return ('part', root, bay, opening, obj)
    # A piece with no menu of its own reads as the level that holds it.
    if opening is not None:
        return ('opening', root, bay, opening, None)
    if bay is not None:
        return ('bay', root, bay, None, None)
    return ('cabinet', root, None, None, None)


# ---- Several picked at once -------------------------------------------------
# Picking five cabinets and typing a depth sets all five. The page shows
# the active one; the others of the same kind in the selection are its
# peers, which the field engine reads for "Mixed" and writes along with
# it. Gathered once per page build -- the engine asks for every field.

_picked = {'cabinet': [], 'opening': [], 'product': [], 'drawer': []}


def _gather(context):
    roots, openings, products, drawers = [], [], [], []
    for obj in context.selected_objects:
        root = hb_utils.get_cabinet_bp(obj)
        if root is None:
            continue
        if 'IS_FRAMELESS_PRODUCT_CAGE' in root:
            if root not in products:
                products.append(root)
            continue
        if root not in roots:
            roots.append(root)
        if obj.get(TAG_OPENING):
            openings.append(obj)
        elif _is_drawer_part(obj):
            drawer = _items().drawer_opening_for(obj)
            if drawer is not None and drawer not in drawers:
                drawers.append(drawer)
    _picked.update({'cabinet': roots, 'opening': openings,
                    'product': products, 'drawer': drawers})


def _peer_kind(key):
    if key in (CABINET_SCHEMA,) or key.startswith(STYLE_PREFIX):
        return 'cabinet'
    if key == OPENING_SCHEMA:
        return 'opening'
    if key in (PRODUCT_SCHEMA, MISC_PART_SCHEMA):
        return 'product'
    return None


def _peers(owner):
    """The other picked objects of the owner's kind, seen through the
    same schema -- none unless the owner is itself one of the picked."""
    from ...operators import prop_proxy
    try:
        path = owner.path_from_id()
        obj = owner.id_data
    except Exception:
        return ()
    if not path.startswith(prop_proxy.PATH_PREFIX):
        return ()
    key = path[len(prop_proxy.PATH_PREFIX):]
    kind = _peer_kind(key)
    if kind is None:
        return ()
    objs = _picked.get(kind, ())
    try:
        if obj not in objs:
            return ()
        return [prop_proxy.owner(o, key) for o in objs
                if o != obj and o.name in bpy.data.objects]
    except ReferenceError:
        return ()           # one was deleted since the page was built


def _count(kind):
    return len(_picked.get(kind, ()))


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _size_summary(owner):
    return f"{_dist(owner.width)} x {_dist(owner.height)} x {_dist(owner.depth)}"


def _has(key):
    return lambda owner: key in owner.id_data


def _hung(owner):
    return owner.id_data.get('CABINET_TYPE') == 'UPPER'


def _scribe_filler(owner):
    return owner.id_data.get('PART_TYPE') == 'CORNER_FILLER'


def _upper_scribe_filler(owner):
    from . import scribe_fit
    obj = owner.id_data
    return (scribe_fit.is_wall_scribe_filler(obj)
            and scribe_fit.filler_kind(obj) != 'BASE')


def _filler_top_return():
    """A wall scribe filler's top return turned on by hand. Off, it
    still comes on by itself over a finished cabinet top."""
    from ...operators import prop_proxy
    from . import types_products

    def get(obj):
        return bool(obj.get(types_products.TOP_RETURN_KEY, False))

    def set(obj, value):
        obj[types_products.TOP_RETURN_KEY] = bool(value)
    return prop_proxy.computed(get, set, type='BOOLEAN')


def _filler_trim_scribe():
    """How much wider than it shows a wall scribe filler is cut, into
    the wall."""
    from ...operators import prop_proxy
    from . import types_products

    def get(obj):
        return float(obj.get(types_products.TRIM_SCRIBE_KEY, 0.0) or 0.0)

    def set(obj, value):
        obj[types_products.TRIM_SCRIBE_KEY] = max(0.0, float(value))
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _houses_appliance(owner):
    from . import types_frameless
    return types_frameless.appliance_opening(owner.id_data) is not None


def _blind_corner(owner):
    return bool(owner.id_data.get('IS_BLIND_CORNER'))


def _kicked(owner):
    return 'Toe Kick Height' in owner.id_data


def _kick_panel(owner):
    return _kicked(owner) and bool(owner.id_data.get('Toe Kick Panel'))


def _bay_size(bay_obj):
    from ...hb_types import GeoNodeObject
    try:
        node = GeoNodeObject(bay_obj)
        return f"{_dist(node.get_input('Dim X'))} x {_dist(node.get_input('Dim Z'))}"
    except Exception:
        return None


def _door(owner):
    return 'Door Swing' in owner.id_data


def _flip_up(owner):
    return any(c.get('IS_FLIP_UP_DOOR') for c in owner.id_data.children)


def _drawer_look_on(owner):
    from . import drawer_look
    return drawer_look.count(owner.id_data) > 0


def _apron_on(owner):
    from . import opening_apron
    return opening_apron.wanted(owner.id_data)


def _drawer_look():
    """How many drawer fronts a doors opening is shown as. An opening
    that never had the look keeps no prompt for it."""
    from ...operators import prop_proxy
    from . import drawer_look

    def get(obj):
        return str(drawer_look.count(obj))

    def set(obj, value):
        if int(value) or drawer_look.COUNT_KEY in obj:
            obj[drawer_look.COUNT_KEY] = int(value)
    return prop_proxy.computed(
        get, set, type='ENUM',
        items=[(key, label) for key, label, _tip in drawer_look.COUNT_ITEMS])


# ---- Schemas ----------------------------------------------------------------

def _solve(obj, context):
    try:
        obj.name
    except ReferenceError:
        # Rebuilt away by the change (a new front replaces its insert).
        return
    hb_utils.run_calc_fix(context, obj)


def _solve_product(obj, context):
    from . import types_products
    types_products.recalculate_product(obj)
    if obj.get('PART_TYPE') == 'SUPPORT_FRAME':
        from .operators import ops_products
        tl = ops_products._turned_leg()
        if tl.LEG_STYLE_PROP in obj:
            tl.sync_frame_legs(obj)


def _toe_kick_type():
    from ...operators import prop_proxy

    def get(obj):
        try:
            return str(int(obj.get('Toe Kick Type', 0)))
        except (TypeError, ValueError):
            return '0'

    def set(obj, value):
        from . import types_frameless
        if int(value) != int(obj.get('Toe Kick Type', 0)):
            types_frameless.set_toe_kick_type(obj, int(value))
    return prop_proxy.computed(
        get, set, type='ENUM',
        items=[(str(i), label) for i, label in enumerate(TOE_KICK_TYPES)])


# Which part of a cabinet stays put when its width is typed, as on a face
# frame cabinet: the left edge (the cabinet grows to the right, as it
# always has), the centreline, or the right edge. Kept on the cabinet.
ANCHOR_KEY = 'HB_ANCHOR_SIDE'
ANCHOR_SIDES = (('LEFT', "Left"), ('CENTER', "Center"), ('RIGHT', "Right"))
_ANCHOR_SHARE = {'CENTER': 0.5, 'RIGHT': 1.0}


def _anchor_side():
    from ...operators import prop_proxy

    def get(obj):
        value = obj.get(ANCHOR_KEY, 'LEFT')
        return value if value in _ANCHOR_SHARE or value == 'LEFT' else 'LEFT'

    def set(obj, value):
        if value == 'LEFT':
            obj.pop(ANCHOR_KEY, None)
        else:
            obj[ANCHOR_KEY] = value
    return prop_proxy.computed(get, set, type='ENUM', items=list(ANCHOR_SIDES))


def _width_axis(obj):
    """The way the cabinet's width grows, in its parent's space."""
    from mathutils import Vector
    axis = obj.matrix_basis.to_3x3() @ Vector((1.0, 0.0, 0.0))
    return axis.normalized() if axis.length > 1e-9 else Vector((1.0, 0.0, 0.0))


def _cabinet_width():
    """The cabinet's width. Anchored right the cabinet moves by the
    change so its right edge holds; anchored centre by half of it."""
    from ...operators import prop_proxy

    def get(obj):
        try:
            return float(_cage(obj).get_input('Dim X'))
        except Exception:
            return 0.0

    def set(obj, value):
        cage = _cage(obj)
        old = float(cage.get_input('Dim X'))
        share = _ANCHOR_SHARE.get(obj.get(ANCHOR_KEY, 'LEFT'), 0.0)
        if share and not obj.get('IS_CORNER_CABINET'):
            obj.location -= _width_axis(obj) * ((float(value) - old) * share)
        cage.set_input('Dim X', float(value))
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def _straight(owner):
    return not owner.id_data.get('IS_CORNER_CABINET')


def _cabinet_height():
    """The cabinet's height; an upper keeps its top or bottom in place
    by the room's setting."""
    from ...operators import prop_proxy

    def get(obj):
        try:
            return float(_cage(obj).get_input('Dim Z'))
        except Exception:
            return 0.0

    def set(obj, value):
        from . import types_frameless
        types_frameless.set_cabinet_height(obj, float(value))
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def _upper_box(owner):
    """A straight upper cabinet: the one kind a panel is applied under."""
    from . import solver_frameless
    obj = owner.id_data
    return (not obj.get('IS_CORNER_CABINET')
            and solver_frameless.carcass_kind(obj) == 'UPPER')


def _fb_on(owner):
    from . import solver_frameless
    return _upper_box(owner) and bool(
        owner.id_data.get(solver_frameless.FINISHED_BOTTOM_KEY))


def _lv_on(owner):
    from . import solver_frameless
    return _upper_box(owner) and bool(
        owner.id_data.get(solver_frameless.LV_KEY))


def _fb_led(owner):
    from . import solver_frameless
    return _fb_on(owner) and bool(
        owner.id_data.get(solver_frameless.FB_LED_KEY))


def _fb_summary(owner):
    from . import solver_frameless
    number = int(owner.id_data.get(solver_frameless.FINISHED_BOTTOM_KEY, 0) or 0)
    text = FINISHED_BOTTOMS[number] if 0 <= number < len(FINISHED_BOTTOMS) else ""
    if number and owner.id_data.get(solver_frameless.FB_LED_KEY):
        text += ", LED route"
    return text


def _construction_summary(owner):
    obj = owner.id_data
    said = []
    if 'Toe Kick Height' in obj:
        kind = int(obj.get('Toe Kick Type', 0) or 0)
        name = TOE_KICK_TYPES[kind] if 0 <= kind < len(TOE_KICK_TYPES) else ""
        said.append(f"{_dist(obj['Toe Kick Height'])} kick" +
                    (f" ({name})" if name else ""))
    said.extend(label for key, label in (('Remove Bottom', "No bottom"),
                                         ('Finished Interior', "Finished interior"))
                if obj.get(key))
    return " · ".join(said) or "Standard"


def _leg_levelers(owner):
    return 'Leg Leveler Inset' in owner.id_data and int(
        owner.id_data.get('Toe Kick Type', 0) or 0) == 3


def _stretchers(owner):
    return 'Stretcher Width' in owner.id_data and int(
        owner.id_data.get('Base Top Construction', 0) or 0) == 1


def _sink_top(owner):
    return 'Sink Apron Width' in owner.id_data and int(
        owner.id_data.get('Base Top Construction', 0) or 0) == 2


# ---- Finished ends ------------------------------------------------------------
# Each side's finish as the right-click Finish Condition menu sets it. An
# end picked here stays as picked; Follow Neighbors hands it back to
# finishing itself from what is beside it.

_PANEL_CONDITIONS = ('LEFT', 'RIGHT', 'BACK')


def _finish_condition(side):
    from ...operators import prop_proxy
    from .operators import ops_finished_ends as fe

    def get(obj):
        return fe.finish_condition(obj, side) or 'UNFINISHED'

    def set(obj, value):
        if value == get(obj):
            return
        context = bpy.context
        if not fe.set_finish_condition(context, obj, side, value):
            return
        from . import exposure
        if side in exposure.AUTO_SIDES:
            exposure.set_manual(obj, side)
        fe._paint(obj)
        hb_utils.run_calc_fix(context, obj)
    items = [(key, label) for key, label, _tip in fe.FINISH_CONDITIONS
             if side in _PANEL_CONDITIONS or key in ('UNFINISHED', 'FINISHED')]
    return prop_proxy.computed(get, set, type='ENUM', items=items)


def _finish_side(side):
    def shown(owner):
        from .operators import ops_finished_ends as fe
        return fe.finish_condition(owner.id_data, side) is not None
    return shown


def _top_finish_shown(owner):
    """A top shows on a wall or tall cabinet; a base top is under the
    countertop."""
    from . import solver_frameless
    return (_finish_side('TOP')(owner) and solver_frameless.carcass_kind(
        owner.id_data) not in ('BASE', 'CORNER_BASE', 'LAP_DRAWER'))


def _manual(side):
    def test(owner):
        from . import exposure
        return exposure.is_manual(owner.id_data, side)
    return test


def _ends_summary(owner):
    from .operators import ops_finished_ends as fe
    words = {'FINISHED': "finished", 'SLAB': "slab panel",
             '5PIECE': "5-piece panel"}
    said = []
    for side, name in (('LEFT', "Left"), ('RIGHT', "Right"), ('BACK', "Back")):
        cond = fe.finish_condition(owner.id_data, side)
        if cond in words:
            said.append(f"{name} {words[cond]}")
    return ", ".join(said) or "Unfinished"


def _ends_fields():
    fields = []
    for side, prop, label in (('LEFT', 'left_finish', "Left End"),
                              ('RIGHT', 'right_finish', "Right End"),
                              ('BACK', 'back_finish', "Back")):
        fields.append(('enum', prop, label, {'when': _finish_side(side)}))
        fields.append(('actions', (
            _act(f"{label}: Follow Neighbors",
                 'hb_frameless.auto_finish_condition', {'side': side}),),
            None, {'when': _manual(side)}))
    fields.append(('enum', 'top_finish', "Top", {'when': _top_finish_shown}))
    fields.extend((
        ('enum', 'finished_bottom', "Bottom Panel", {'when': _upper_box}),
        ('bool', 'fb_doors_cover', "Doors Cover Panel", {'when': _fb_on}),
        ('bool', 'fb_led_route', "LED Route", {'when': _fb_on}),
        ('distance', 'fb_led_width', "Route Width", {'when': _fb_led}),
        ('distance', 'fb_led_depth', "Route Depth", {'when': _fb_led}),
        ('distance', 'fb_led_inset', "Route From Front", {'when': _fb_led}),
        ('bool', 'light_valance', "Light Valance", {'when': _upper_box}),
        ('distance', 'lv_depth', "Valance Depth", {'when': _lv_on}),
        ('bool', 'lv_doors_cover', "Doors Cover Valance", {'when': _lv_on}),
    ))
    return tuple(fields)


# ---- Quick actions -------------------------------------------------------------

def _cabinets_selected(_owner):
    return _count('cabinet') >= 2


def _one_cabinet(owner):
    return not _cabinets_selected(owner)


def _quick_fields(owner, rows, fold='fl_quick_actions'):
    """The quick actions a page leads with, a row at a time: each row is
    (action, when) pairs and keeps the ones that apply. Every one is
    also on the right-click menu, and so in All Actions."""
    kept = []
    for row in rows:
        for action, when in row:
            try:
                if when is not None and not when(owner):
                    continue
            except Exception:
                continue
            kept.append(action)
    from ...operators import quick_actions
    return quick_actions.fields(kept, fold=fold)


def _finished_interior():
    """Finishing the interior repaints the cabinet in its style."""
    from ...operators import prop_proxy

    def get(obj):
        return bool(obj.get('Finished Interior', False))

    def set(obj, value):
        if bool(value) == bool(obj.get('Finished Interior', False)):
            return
        obj['Finished Interior'] = bool(value)
        try:
            styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
            if len(styles):
                index = int(obj.get('CABINET_STYLE_INDEX', 0) or 0)
                style = styles[index] if index < len(styles) else styles[0]
                style.assign_style_to_cabinet(obj)
        except Exception as ex:
            print('Home Builder: repainting %s failed: %s' % (obj.name, ex))
    return prop_proxy.computed(get, set, type='BOOLEAN')


def _finished_bottom():
    """The panel applied under an upper. A cabinet that never had one
    keeps no prompt for it until one is picked."""
    from ...operators import prop_proxy
    from . import solver_frameless
    key = solver_frameless.FINISHED_BOTTOM_KEY

    def get(obj):
        try:
            return str(int(obj.get(key, 0) or 0))
        except (TypeError, ValueError):
            return '0'

    def set(obj, value):
        if int(value) or key in obj:
            obj[key] = int(value)
    return prop_proxy.computed(
        get, set, type='ENUM',
        items=[(str(i), label) for i, label in enumerate(FINISHED_BOTTOMS)])


def _upper_height_anchor():
    """Which edge of an upper stays put when its height is typed: a
    setting of the room, shown beside the height it steers."""
    from ...operators import prop_proxy

    def _props():
        return hb_project.get_settings_scene(bpy.context).hb_frameless

    def get(obj):
        return _props().upper_height_anchor

    def set(obj, value):
        _props().upper_height_anchor = value
    items = [('TOP', "Top"), ('BOTTOM', "Bottom")]
    return prop_proxy.computed(get, set, type='ENUM', items=items)


def _top_off_floor():
    from ...operators import prop_proxy

    def get(obj):
        from . import types_frameless
        try:
            return float(types_frameless.cabinet_top_off_floor(obj))
        except Exception:
            return 0.0

    def set(obj, value):
        from . import types_frameless
        types_frameless.set_cabinet_top_off_floor(obj, value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _product_depth():
    """A product's depth as built (a wall scribe filler flush with the
    carcass reads to its own face, not the door plane)."""
    from ...operators import prop_proxy

    def get(obj):
        from . import types_products
        try:
            return float(types_products.product_depth(obj))
        except Exception:
            return 0.0

    def set(obj, value):
        from . import types_products
        types_products.set_product_depth(obj, float(value))
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def _appliance_opening(axis):
    """Width (0) or height (1) of the opening that houses a refrigerator,
    column or laundry unit; the cabinet or the doors over it follow."""
    from ...operators import prop_proxy

    def get(obj):
        from . import types_frameless
        size = types_frameless.appliance_opening_size(obj)
        return float(size[axis]) if size else 0.0

    def set(obj, value):
        from . import types_frameless
        if axis == 0:
            types_frameless.set_appliance_opening_width(obj, value)
        else:
            types_frameless.set_appliance_opening_height(obj, value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


_OVERLAY_SIDES = ('Top', 'Bottom', 'Left', 'Right')


def _half_overlay(side):
    """The half overlay switch for one side. Using it hands the side
    back to the switch: a typed overlay there is dropped."""
    from ...operators import prop_proxy
    key = 'Half Overlay ' + side

    def get(obj):
        return bool(obj.get(key, False))

    def set(obj, value):
        obj[key] = bool(value)
        if 'Typed Overlay ' + side in obj:
            del obj['Typed Overlay ' + side]
    return prop_proxy.computed(get, set, type='BOOLEAN')


def _overlay_amount(side):
    """How far the front laps the opening on one side. Reads what the
    cabinet builds; typing a value overrides that side."""
    from ...operators import prop_proxy
    index = _OVERLAY_SIDES.index(side)

    def get(obj):
        from . import solver_frameless
        return float(solver_frameless.front_overlays(obj)[index])

    def set(obj, value):
        obj['Typed Overlay ' + side] = float(value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _overlay_summary(owner):
    obj = owner.id_data
    parts = []
    for side in _OVERLAY_SIDES:
        if 'Typed Overlay ' + side in obj:
            parts.append(side + " typed")
        elif obj.get('Half Overlay ' + side):
            parts.append(side + " half")
    return ", ".join(parts) or "Full"


def _overlaid(owner):
    obj = owner.id_data
    return 'Half Overlay Top' in obj and not obj.get('Inset Front')


def _blind_opening_width():
    """Width of a blind corner's door opening; the blind panel takes up
    the difference, the cabinet keeps its width."""
    from ...operators import prop_proxy

    def get(obj):
        from . import types_frameless
        return float(types_frameless.blind_opening_width(obj) or 0.0)

    def set(obj, value):
        from . import types_frameless
        types_frameless.set_blind_opening_width(obj, value)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def _cage(obj):
    from ...hb_types import GeoNodeCage
    return GeoNodeCage(obj)


def _edge_state(socket):
    """How one edge of a cabinet part is banded."""
    from ...operators import prop_proxy
    from . import edgebanding_frameless as eb

    def get(obj):
        return eb.edge_state(obj, socket)

    def set(obj, value):
        eb.set_edge_state(obj, socket, value)
    return prop_proxy.computed(get, set, type='ENUM',
                               items=list(eb.EDGE_STATES))


def _edge_summary(owner):
    from . import edgebanding_frameless as eb
    obj = owner.id_data
    count = sum(1 for e in eb.EDGE_SOCKETS if eb.edge_state(obj, e) != 'NONE')
    return "%d of %d" % (count, len(eb.EDGE_SOCKETS))


def edge_blocks(context, part_obj):
    """The Edgebanding group of a cabinet or product part: each edge by where it
    lies in the cabinet, banded or not and in which banding."""
    from ...operators import options_panel, prop_proxy
    from . import edgebanding_frameless as eb
    if not eb.takes_edge_override(part_obj):
        return []
    labels = eb.edge_labels(part_obj)
    order = ("Front", "Back", "Top", "Bottom", "Left", "Right")
    sockets = sorted(eb.EDGE_SOCKETS, key=lambda e: (
        order.index(labels[e]) if labels[e] in order else len(order)))
    fields = tuple(('enum', 'edge_' + e.lower(), labels[e] + " Edge")
                   for e in sockets)
    return options_panel.field_blocks(context, (
        ('group', PART_EDGES_GROUP, "Edgebanding",
         {'summary': _edge_summary, 'fields': fields}),
    ), prop_proxy.owner(part_obj, PART_EDGES_SCHEMA))


PART_MATERIAL_SCHEMA = 'FL_PART_MATERIAL'
PART_MATERIAL_GROUP = 'fl_part_material'


def material_blocks(context, part_obj):
    """The Material group of a cabinet or product part: which of a
    style's materials it wears, Automatic leaving it to its place in the
    cabinet. Registered on each draw so the style list is current."""
    from ...operators import options_panel, prop_proxy as P
    from . import part_material as pm
    if not pm.takes_override(part_obj):
        return []
    styles = [pm.OWN_STYLE] + pm.style_names()
    P.register(PART_MATERIAL_SCHEMA, {
        'material': P.computed(pm.choice, pm.set_choice, type='ENUM',
                               items=list(pm.CHOICES)),
        'material_style': P.computed(pm.style_choice, pm.set_style,
                                     type='ENUM',
                                     items=[(n, n) for n in styles]),
    })
    fields = (('enum', 'material', "Material"),)
    if len(styles) > 2:
        fields += (('enum', 'material_style', "From Style",
                    {'when': lambda o: pm.choice(o.id_data) != pm.AUTO}),)
    return options_panel.field_blocks(context, (
        ('group', PART_MATERIAL_GROUP, "Material",
         {'summary': lambda o: pm.summary(o.id_data), 'fields': fields}),
    ), P.owner(part_obj, PART_MATERIAL_SCHEMA))


def _name_prop():
    """The product's own name, which the cut list and reports carry. A
    misc part is its own product, so its part takes the same name."""
    from ...operators import prop_proxy as P

    def set_name(obj, value):
        value = str(value).strip()
        if value:
            obj.name = value
    return P.computed(lambda obj: obj.name, set_name, type='STRING',
                      solve=False)


def _register_schemas():
    from ...operators import prop_proxy as P
    from . import solver_frameless
    from . import bay_config
    bay_config.register()
    P.register(CABINET_SCHEMA, {
        'name': _name_prop(),
        'width': _cabinet_width(),
        'anchor_side': _anchor_side(),
        'depth': P.node_input('Dim Y'),
        'height': _cabinet_height(),
        'height_off_floor': P.height_off_floor(),
        'top_off_floor': _top_off_floor(),
        'appliance_opening_width': _appliance_opening(0),
        'appliance_opening_height': _appliance_opening(1),
        'blind_opening_width': _blind_opening_width(),
        'toe_kick_type': _toe_kick_type(),
        'toe_kick_height': P.length('Toe Kick Height'),
        'toe_kick_setback': P.length('Toe Kick Setback'),
        'flush_toe_kick': P.flag('Flush Toe Kick'),
        'toe_kick_panel': P.flag('Toe Kick Panel'),
        'toe_kick_panel_thickness': P.length('Toe Kick Panel Thickness', units.inch(0.375)),
        'toe_kick_end_inset': P.length('Toe Kick End Inset'),
        'remove_bottom': P.flag('Remove Bottom'),
        'finished_interior': _finished_interior(),
        'finished_bottom': _finished_bottom(),
        'fb_doors_cover': P.flag(solver_frameless.FB_DOORS_COVER_KEY, True),
        'fb_led_route': P.flag(solver_frameless.FB_LED_KEY),
        'fb_led_width': P.length(solver_frameless.FB_LED_WIDTH_KEY, units.inch(0.875)),
        'fb_led_depth': P.length(solver_frameless.FB_LED_DEPTH_KEY, units.inch(0.375)),
        'fb_led_inset': P.length(solver_frameless.FB_LED_INSET_KEY, units.inch(1.5)),
        'light_valance': P.flag(solver_frameless.LV_KEY),
        'lv_depth': P.length(solver_frameless.LV_DEPTH_KEY, solver_frameless.LV_DEPTH_DEFAULT),
        'lv_doors_cover': P.flag(solver_frameless.LV_DOORS_COVER_KEY, True),
        'left_depth': P.length('Left Depth'),
        'right_depth': P.length('Right Depth'),
        'material_thickness': P.length('Material Thickness', units.inch(0.75)),
        'leg_leveler_inset': P.length('Leg Leveler Inset'),
        'base_top_construction': P.index_enum(
            'Base Top Construction', ("Full Top", "Stretchers", "Sink")),
        'stretcher_width': P.length('Stretcher Width'),
        'sink_apron_width': P.length('Sink Apron Width'),
        'left_finish': _finish_condition('LEFT'),
        'right_finish': _finish_condition('RIGHT'),
        'back_finish': _finish_condition('BACK'),
        'top_finish': _finish_condition('TOP'),
        'upper_height_anchor': _upper_height_anchor(),
    }, after=_solve)
    P.register(OPENING_SCHEMA, {
        **bay_config.opening_props(),
        'door_swing': P.index_enum('Door Swing', ("Left", "Right", "Double"), 2),
        'door_mechanism': P.index_enum('Door Mechanism', ("Standard", "Retracting")),
        'drawer_look': _drawer_look(),
        'drawer_look_top_height': P.length('Drawer Look Top Height'),
        'add_apron': P.flag('Add Apron'),
        'apron_height': P.length('Apron Height', units.inch(7.0)),
        'lift_mechanism': P.index_enum('Lift Mechanism', (
            "Stay Lift", "Bi-Fold Lift", "Up and Over", "Vertical Lift")),
        'inset_front': P.flag('Inset Front'),
        'half_overlay_top': _half_overlay('Top'),
        'half_overlay_bottom': _half_overlay('Bottom'),
        'half_overlay_left': _half_overlay('Left'),
        'half_overlay_right': _half_overlay('Right'),
        'overlay_top': _overlay_amount('Top'),
        'overlay_bottom': _overlay_amount('Bottom'),
        'overlay_left': _overlay_amount('Left'),
        'overlay_right': _overlay_amount('Right'),
    }, after=_solve)
    P.register(PRODUCT_SCHEMA, {
        'name': _name_prop(),
        'width': P.node_input('Dim X'),
        'depth': _product_depth(),
        'height': P.node_input('Dim Z'),
        'height_off_floor': P.height_off_floor(),
        'top_off_floor': _top_off_floor(),
        'top_return': _filler_top_return(),
        'trim_scribe': _filler_trim_scribe(),
    }, after=_solve_product)
    # A misc part is a cut part: its size is length, width and thickness.
    P.register(MISC_PART_SCHEMA, {
        'name': _name_prop(),
        'width': P.node_input('Length'),
        'depth': P.node_input('Width'),
        'height': P.node_input('Thickness'),
        'height_off_floor': P.height_off_floor(),
        **{'band_' + socket.lower(): _misc_band(socket)
           for socket in ('W1', 'W2', 'L1', 'L2')},
    }, after=_solve_product)
    P.register(FRONT_SCHEMA, {
        'hinge': _front_hinge(),
        'handle': _front_handle(),
        'left_stile': _frame_input('Left Stile Width'),
        'right_stile': _frame_input('Right Stile Width'),
        'top_rail': _frame_input('Top Rail Width'),
        'bottom_rail': _frame_input('Bottom Rail Width'),
        'add_mid_rail': _frame_input('Add Mid Rail', 'BOOLEAN'),
        'mid_rail_width': _frame_input('Mid Rail Width'),
        'center_mid_rail': _frame_input('Center Mid Rail', 'BOOLEAN'),
        'mid_rail_location': _frame_input('Mid Rail Location'),
    }, after=_solve_front)
    P.register(PART_EDGES_SCHEMA, {
        'edge_' + socket.lower(): _edge_state(socket)
        for socket in ('W1', 'W2', 'L1', 'L2')})


def _unregister_schemas():
    from ...operators import prop_proxy
    from . import bay_config
    bay_config.unregister()
    for key in (CABINET_SCHEMA, OPENING_SCHEMA, PRODUCT_SCHEMA,
                MISC_PART_SCHEMA, PART_EDGES_SCHEMA, FRONT_SCHEMA,
                PART_MATERIAL_SCHEMA):
        prop_proxy.unregister(key)


# ---- Fields -----------------------------------------------------------------

def _cabinet_fields(root):
    """The cabinet page, laid out as the face frame cabinet's: its size,
    then the rest in folds that say what is set in them, and last the
    quick actions in a fold of their own. Every command is also in All
    Actions at the foot."""
    quick = _quick_fields(root, (
        ((_act("Duplicate", 'hb_frameless.duplicate_cabinet', None,
               'duplicate'), _one_cabinet),
         (_act("Copy Cabinet", 'home_builder.copy_cabinet'), _one_cabinet)),
        ((_act("Equal Widths", 'hb_frameless.equalize_cabinet_widths'),
          _cabinets_selected),
         (_act("Adjust Cabinet Sizes",
               'hb_frameless.adjust_multiple_cabinet_widths'), None)),
        ((_act("Create Cabinet Group", 'hb_frameless.create_cabinet_group'),
          _cabinets_selected),),
        ((_act("Drop to Countertop", 'hb_frameless.drop_cabinet_to_countertop'),
          _hung),
         (_act("Hide Cabinet", 'hb_general.hide',
               {'scope': 'PRODUCT', 'isolate': False}), None)),
    ))
    return (
        ('text', 'name', "Name"),
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        # An angled front's depth is its deeper end, kept by the cabinet
        # dialog (Properties) with the two end depths.
        ('distance', 'depth', "Depth", {'when': _square_front}),
        ('distance', 'height_off_floor', "Above Floor", {'when': _hung}),
        ('distance', 'top_off_floor', "Top Above Floor", {'when': _hung}),
        ('enum', 'upper_height_anchor', "Height Keeps", {'when': _hung}),
        ('distance', 'appliance_opening_width', "Appliance Opening Width",
         {'when': _houses_appliance}),
        ('distance', 'appliance_opening_height', "Appliance Opening Height",
         {'when': _houses_appliance}),
        ('distance', 'blind_opening_width', "Door Opening Width",
         {'when': _blind_corner}),
        ('choices', 'anchor_side', "Anchor", {'cols': 3, 'when': _straight}),
        ('gap', None, None),
        ('group', 'fl_cab_corner', "Corner", {
            'icon': 'cab_corner', 'when': _has('Left Depth'), 'fields': (
                ('distance', 'left_depth', "Left Depth"),
                ('distance', 'right_depth', "Right Depth"),
            )}),
        ('group', 'fl_cab_construction', "Construction", {
            'icon': 'cab_construction', 'summary': _construction_summary,
            'fields': (
                ('enum', 'toe_kick_type', "Toe Kick", {'when': _has('Toe Kick Type')}),
                ('distance', 'toe_kick_height', "Kick Height", {'when': _kicked}),
                ('distance', 'toe_kick_setback', "Kick Setback",
                 {'when': _has('Toe Kick Setback')}),
                ('bool', 'flush_toe_kick', "Flush Toe Kick",
                 {'when': _has('Flush Toe Kick')}),
                ('bool', 'toe_kick_panel', "Kick Panel",
                 {'when': _has('Toe Kick Panel')}),
                ('distance', 'toe_kick_panel_thickness', "Kick Panel Thickness",
                 {'when': _kick_panel}),
                ('distance', 'toe_kick_end_inset', "Kick Inset From Ends",
                 {'when': _has('Toe Kick End Inset')}),
                ('distance', 'leg_leveler_inset', "Leg Leveler Inset",
                 {'when': _leg_levelers}),
                ('enum', 'base_top_construction', "Top",
                 {'when': _has('Base Top Construction')}),
                ('distance', 'stretcher_width', "Stretcher Width",
                 {'when': _stretchers}),
                ('distance', 'sink_apron_width', "Sink Apron Width",
                 {'when': _sink_top}),
                ('distance', 'material_thickness', "Carcass Thickness",
                 {'when': _has('Material Thickness')}),
                ('bool', 'remove_bottom', "Remove Bottom",
                 {'when': _has('Remove Bottom')}),
                ('bool', 'finished_interior', "Finished Interior"),
            )}),
        ('group', 'fl_cab_ends', "Finished Ends & Back", {
            'summary': _ends_summary, 'fields': _ends_fields()}),
    ) + quick


def _in_stack(owner):
    from . import bay_config
    return bay_config.opening_front_row(owner.id_data) is not None


def _front_height_chip(owner):
    from . import bay_config
    row = bay_config.opening_front_row(owner.id_data)
    if row is None or not row[3]:
        return None
    return ('hb_frameless.release_front_height',
            {'splitter_name': row[0].name, 'index': row[1]},
            'lock', "Held. Click to let it share what is left")


def _front_details(owner):
    return (_door(owner) or _has('Inset Front')(owner))


def _front_summary(owner):
    from . import bay_config
    kind = bay_config.front_kind(owner.id_data)
    return dict(bay_config.FRONT_KINDS).get(kind, "")


OPENING_FIELDS = (
    ('value', lambda o: _bay_size(o.id_data), "Size (W x H)"),
    ('enum', 'front_type', "Front"),
    ('enum', 'door_swing', "Hinge Side", {'when': _door}),
    ('enum', 'door_mechanism', "Mechanism", {'when': _door}),
    ('enum', 'lift_mechanism', "Lift", {'when': _flip_up}),
    ('distance', 'front_height', "Front Height",
     {'when': _in_stack, 'action': _front_height_chip}),
    ('gap', None, None),
)

OPENING_FOLDS = (
    ('group', 'fl_opening_front', "Front Details", {
        'when': _front_details,
        'summary': _front_summary,
        'fields': (
            ('enum', 'drawer_look', "Drawer Look", {'when': _door}),
            ('distance', 'drawer_look_top_height', "Top Front Height",
             {'when': _drawer_look_on}),
            ('bool', 'add_apron', "Add Apron", {'when': _door}),
            ('distance', 'apron_height', "Apron Height", {'when': _apron_on}),
            ('bool', 'inset_front', "Inset Front", {'when': _has('Inset Front')}),
        )}),
    ('group', 'fl_opening_overlays', "Overlays", {
        'when': _has('Half Overlay Top'),
        'summary': _overlay_summary,
        'fields': (
            ('bool', 'half_overlay_top', "Half Top"),
            ('bool', 'half_overlay_bottom', "Half Bottom"),
            ('bool', 'half_overlay_left', "Half Left"),
            ('bool', 'half_overlay_right', "Half Right"),
            ('distance', 'overlay_top', "Top", {'when': _overlaid}),
            ('distance', 'overlay_bottom', "Bottom", {'when': _overlaid}),
            ('distance', 'overlay_left', "Left", {'when': _overlaid}),
            ('distance', 'overlay_right', "Right", {'when': _overlaid}),
        )}),
)

PRODUCT_FIELDS = (
    ('text', 'name', "Name"),
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('distance', 'height_off_floor', "Above Floor"),
    ('distance', 'top_off_floor', "Top Above Floor",
     {'when': _upper_scribe_filler}),
    ('bool', 'top_return', "Top Return", {'when': _scribe_filler}),
    ('distance', 'trim_scribe', "Wall Trim Scribe", {'when': _scribe_filler}),
)


# ---- Fronts -----------------------------------------------------------------
# A door or drawer front's own settings: the style it wears, its hinge
# and handle, where its pull sits, and a five piece door's frame.

def _solve_front(obj, context):
    from . import solver_frameless
    solver_frameless.recalculate_cabinet(obj)
    obj.update_tag()


def _front_insert(front):
    from .operators import ops_front
    return ops_front._front_insert(front)


def _frame_mod(front):
    """The five piece door modifier on a front, or None for a slab."""
    for mod in front.modifiers:
        if (mod.type == 'NODES' and 'Door Style' in mod.name and mod.node_group
                and 'CPM_5PIECEDOOR' in mod.node_group.name):
            return mod
    return None


def _framed(owner):
    return _frame_mod(owner.id_data) is not None


def _mid_railed(owner):
    return _framed(owner) and bool(owner.add_mid_rail)


def _mid_rail_placed(owner):
    return _mid_railed(owner) and not bool(owner.center_mid_rail)


def _hinged(owner):
    insert = _front_insert(owner.id_data)
    return insert is not None and 'Door Swing' in insert


def _frame_input(name, kind='FLOAT'):
    """An input of the front's five piece door modifier."""
    from ...operators import prop_proxy
    from ...hb_types import CabinetPartModifier
    cast = bool if kind == 'BOOLEAN' else float

    def _cpm(obj):
        mod = _frame_mod(obj)
        if mod is None or name not in mod.node_group.interface.items_tree:
            return None
        cpm = CabinetPartModifier(obj)
        cpm.mod = mod
        return cpm

    def get(obj):
        cpm = _cpm(obj)
        try:
            return cast(cpm.get_input(name)) if cpm is not None else cast(0)
        except Exception:
            return cast(0)

    def set(obj, value):
        cpm = _cpm(obj)
        if cpm is not None:
            cpm.set_input(name, cast(value))
    if kind == 'BOOLEAN':
        return prop_proxy.computed(get, set, type='BOOLEAN')
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4,
                               hard_min=0.0)


def _front_hinge():
    """Which way the doors of the front's opening swing; kept on the
    doors insert, shown on the door."""
    from ...operators import prop_proxy

    def get(obj):
        insert = _front_insert(obj)
        try:
            return str(int(insert.get('Door Swing', 2)))
        except (AttributeError, TypeError, ValueError):
            return '2'

    def set(obj, value):
        insert = _front_insert(obj)
        if insert is not None and 'Door Swing' in insert:
            insert['Door Swing'] = int(value)
    return prop_proxy.computed(get, set, type='ENUM', items=[
        ('0', "Left"), ('1', "Right"), ('2', "Double")])


def _front_handle():
    """How the front is opened: the room's handle, or one of its own."""
    from ...operators import prop_proxy
    from . import edge_pulls

    def get(obj):
        value = obj.get(edge_pulls.HANDLE_KEY, '') or 'DEFAULT'
        return value if value in known else 'DEFAULT'

    def set(obj, value):
        if value == 'DEFAULT':
            obj.pop(edge_pulls.HANDLE_KEY, None)
        else:
            obj[edge_pulls.HANDLE_KEY] = value
    items = [('DEFAULT', "Room Default")] + [
        (key, label) for key, label, _tip in edge_pulls.HANDLE_TYPES]
    known = {key for key, _label in items}
    return prop_proxy.computed(get, set, type='ENUM', items=items)


def _door_styles():
    try:
        return list(hb_project.get_main_scene().hb_frameless.door_styles)
    except Exception:
        return []


def _door_style_schema(names):
    from ...operators import prop_proxy
    key = DOOR_STYLE_PREFIX + str(abs(hash(tuple(names))))

    def get(obj):
        try:
            index = int(obj.get('DOOR_STYLE_INDEX', 0))
        except (TypeError, ValueError):
            index = 0
        return str(index if 0 <= index < len(names) else 0)

    def set(obj, value):
        styles = _door_styles()
        index = int(value)
        if not 0 <= index < len(styles):
            return
        if index == int(obj.get('DOOR_STYLE_INDEX', -1)):
            return
        obj['DOOR_STYLE_INDEX'] = index
        styles[index].assign_style_to_front(obj)
    if key not in prop_proxy._schemas:
        prop_proxy.register(key, {
            'door_style': prop_proxy.computed(
                get, set, type='ENUM',
                items=[(str(i), n) for i, n in enumerate(names)]),
        }, after=_solve_front)
    return key


# The pull prompts a front shows: where the pull sits, then how far along
# that edge. Only the vertical location of the place in use is offered.
_PULL_VERTICAL = ('Base Pull Vertical Location', 'Tall Pull Vertical Location',
                  'Upper Pull Vertical Location')


def _pull_blocks(context, front):
    from ...operators import generic_page, options_panel
    if 'Pull Location' not in front:
        return []
    try:
        place = int(front.get('Pull Location', 0))
    except (TypeError, ValueError):
        place = 0
    wanted = ['Pull Location', 'Handle Horizontal Location']
    if 0 <= place < len(_PULL_VERTICAL):
        wanted.insert(1, _PULL_VERTICAL[place])
    owner, fields = generic_page.prompt_owner(
        front, exclude=[k for k in generic_page.prompt_keys(front)
                        if k not in wanted])
    if owner is None:
        return []
    names = {'Pull Location': "Location",
             'Handle Horizontal Location': "Horizontal Location"}
    names.update({key: "Vertical Location" for key in _PULL_VERTICAL})
    fields = tuple((kind, ident, names.get(label, label))
                   for kind, ident, label in fields)
    return options_panel.field_blocks(context, (
        ('group', 'fl_front_pull', "Pull", {'fields': fields}),
    ), owner)


FRONT_FIELDS = (
    ('enum', 'hinge', "Hinge", {'when': _hinged}),
    ('enum', 'handle', "Handle"),
)

FRONT_FRAME_FIELDS = (
    ('group', 'fl_front_frame', "Frame Sizes", {'when': _framed, 'fields': (
        ('distance', 'left_stile', "Left Stile"),
        ('distance', 'right_stile', "Right Stile"),
        ('distance', 'top_rail', "Top Rail"),
        ('distance', 'bottom_rail', "Bottom Rail"),
    )}),
    ('group', 'fl_front_mid_rail', "Mid Rail", {'when': _framed, 'fields': (
        ('bool', 'add_mid_rail', "Add Mid Rail"),
        ('distance', 'mid_rail_width', "Width", {'when': _mid_railed}),
        ('bool', 'center_mid_rail', "Center Mid Rail", {'when': _mid_railed}),
        ('distance', 'mid_rail_location', "Location", {'when': _mid_rail_placed}),
    )}),
)


def front_blocks(context, front):
    """Everything the front's dialog held, on the page."""
    from ...operators import options_panel, prop_proxy
    out = []
    names = [style.name for style in _door_styles()]
    if names:
        out.extend(options_panel.field_blocks(context, (
            ('enum', 'door_style', "Door Style"),
        ), prop_proxy.owner(front, _door_style_schema(names))))
    owner = prop_proxy.owner(front, FRONT_SCHEMA)
    out.extend(options_panel.field_blocks(context, FRONT_FIELDS, owner))
    out.extend(_pull_blocks(context, front))
    out.extend(options_panel.field_blocks(context, FRONT_FRAME_FIELDS, owner))
    return out


# ---- Product options --------------------------------------------------------
# A product's prompts, folded by what they are about instead of one long
# list. A product with only a few keeps the single Options group.

_OPTION_GROUPS = (
    ("Legs", lambda key: 'Leg' in key),
    ("LED Routing", lambda key: 'LED' in key),
    ("Finish", lambda key: 'Finish' in key or 'Skin' in key),
    ("Cleats", lambda key: 'Cleat' in key),
)
_OPTION_GROUP_MIN = 7


def _square_front(owner):
    """False for a cabinet with an angled front (end depths set)."""
    from . import solver_frameless
    return owner.id_data.get(solver_frameless.FRONT_LEFT_DEPTH_KEY) is None


# Stamped on a support frame with the Base Molding On Legs value the room
# molding was last rebuilt for, so a page edit rebuilds it only on change.
_LEG_BASE_APPLIED = 'hb_leg_base_molding_applied'


def _product_solve(obj, context):
    """Solve a product after a page edit, plus what its options dialog
    did beyond the solve: a support frame whose Base Molding On Legs
    changed rebuilds the room's molding, which runs round its legs."""
    from ...operators import generic_page
    generic_page._solve(obj, context)
    if obj.get('PART_TYPE') != 'SUPPORT_FRAME':
        return
    from . import types_products
    leg_base = bool(obj.get(types_products.LEG_BASE_MOLDING_KEY, False))
    if obj.get(_LEG_BASE_APPLIED) is not None and \
            bool(obj.get(_LEG_BASE_APPLIED)) == leg_base:
        return
    obj[_LEG_BASE_APPLIED] = leg_base
    from ...molding import ops as molding_ops
    context.view_layer.update()
    molding_ops.apply_scene_packages(context.scene)


def product_option_blocks(context, root):
    from ...operators import generic_page, options_panel
    owner, fields = generic_page.prompt_owner(root, after=_product_solve)
    if owner is None:
        return []
    buckets = {}
    for field in fields:
        label = next((name for name, test in _OPTION_GROUPS if test(field[2])),
                     "Options")
        buckets.setdefault(label, []).append(field)
    if len(fields) < _OPTION_GROUP_MIN or len(buckets) < 2:
        return generic_page.prompt_blocks(context, root, 'fl_product_prompts',
                                          "Options", after=_product_solve)
    order = ["Options"] + [name for name, _test in _OPTION_GROUPS]
    groups = tuple(
        ('group', 'fl_product_' + name.lower().replace(' ', '_'), name,
         {'icon': 'settings', 'fields': tuple(buckets[name])})
        for name in order if name in buckets)
    return options_panel.field_blocks(context, groups, owner)


def _misc_band(socket):
    """One edge of a misc part: banded or bare."""
    from ...operators import prop_proxy
    from . import edgebanding_frameless as eb

    def get(obj):
        return bool(obj.get(eb.MISC_FLAG + socket))

    def set(obj, value):
        obj[eb.MISC_FLAG + socket] = bool(value)
        eb.refresh_banding(obj)
    return prop_proxy.computed(get, set, type='BOOLEAN')


def _band_summary(owner):
    from . import edgebanding_frameless as eb
    on = [e for e in eb.EDGE_SOCKETS if owner.id_data.get(eb.MISC_FLAG + e)]
    return ", ".join(on) if on else "None"


MISC_BAND_FIELDS = (
    ('group', 'fl_misc_banding', "Edgebanding", {'summary': _band_summary, 'fields': (
        ('bool', 'band_w1', "W1"),
        ('bool', 'band_w2', "W2"),
        ('bool', 'band_l1', "L1"),
        ('bool', 'band_l2', "L2"),
    )}),
)


# ---- Style ------------------------------------------------------------------
# The cabinet style leads every cabinet page, whatever part is picked: it
# is the cabinet's, and switching it here saves a trip to the styles.

def _styles():
    try:
        return list(hb_project.get_main_scene().hb_frameless.cabinet_styles)
    except Exception:
        return []


def _style_schema(names):
    from ...operators import prop_proxy
    key = STYLE_PREFIX + str(abs(hash(tuple(names))))

    def get(obj):
        name = obj.get('CABINET_STYLE_NAME')
        if name in names:
            return name
        try:
            return names[int(obj.get('CABINET_STYLE_INDEX', 0))]
        except (TypeError, ValueError, IndexError):
            return names[0]

    def set(obj, value):
        styles = _styles()
        index = next((i for i, s in enumerate(styles) if s.name == value), -1)
        if index < 0 or obj.get('CABINET_STYLE_NAME') == value:
            return
        obj['CABINET_STYLE_INDEX'] = index
        obj['CABINET_STYLE_NAME'] = value
        styles[index].assign_style_to_cabinet(obj)
    if key not in prop_proxy._schemas:
        prop_proxy.register(key, {
            'style': prop_proxy.computed(
                get, set, type='ENUM', items=[(n, n) for n in names]),
        })
    return key


def style_blocks(context, root):
    """The Style row: which style the cabinet carries, switched in
    place. Nothing while the project has no styles."""
    from ...operators import options_panel, prop_proxy
    names = [s.name for s in _styles()]
    if not names:
        return []
    return options_panel.field_blocks(context, (
        ('enum', 'style', "Style"),
    ), prop_proxy.owner(root, _style_schema(names)))


# ---- Labels -----------------------------------------------------------------

def _index_label(obj, tag, word):
    """Bay N / Opening N, counted the way they stand: bays left to right,
    openings top down, among the ones the parent holds."""
    parent = obj.parent
    if parent is None:
        return word
    peers = [o for o in parent.children if o.get(tag)]
    if len(peers) < 2:
        return word
    if word == "Bay":
        peers.sort(key=lambda o: o.matrix_world.translation.x)
    else:
        peers.sort(key=lambda o: -o.matrix_world.translation.z)
    return f"{word} {peers.index(obj) + 1}"


def _type_label(root):
    kind = (root.get('CABINET_TYPE') or root.get('PART_TYPE') or "")
    return str(kind).replace('_', ' ').title()


def _part_label(part_obj):
    if part_obj.get('IS_DRAWER_BOX'):
        return "Drawer Box"
    if part_obj.get('IS_DRAWER_FRONT'):
        return "Drawer"
    if part_obj.get('IS_PULLOUT_FRONT'):
        return "Pullout"
    if part_obj.get('IS_CABINET_FRONT'):
        return "Door"
    if part_obj.get(TAG_INTERIOR):
        return "Interior"
    if part_obj.get('IS_FRAMELESS_INTERIOR_SECTION'):
        return "Section"
    from . import interior_page
    if interior_page.is_bar_part(part_obj):
        return interior_page.split_label(part_obj.parent)
    role = str(part_obj.get('hb_part_role', '') or '')
    if 'SHELF' in role:
        return "Shelf"
    if role:
        return role.replace('_', ' ').title()
    return "Part"


def _interior_of(opening_obj):
    for child in opening_obj.children:
        if child.get(TAG_INTERIOR):
            return child
    return None


def _interior_summary(interior):
    """What is inside, in a few words."""
    if interior is None:
        return "Empty"
    ii = _items()
    if ii.is_items_interior(interior):
        kinds = []
        for it in ii.item_props(interior).interior_items:
            word = str(it.kind).replace('_', ' ').title()
            if word not in kinds:
                kinds.append(word)
        return ", ".join(kinds) or "Empty"
    sections = [c for c in interior.children
                if c.get('IS_FRAMELESS_INTERIOR_SECTION')]
    if sections:
        return "%d sections" % len(sections)
    if 'Shelf Quantity' in interior:
        n = int(interior.get('Shelf Quantity', 0))
        return "%d Shelf" % n if n == 1 else "%d Shelves" % n
    return interior.name.split('.')[0]


# ---- Actions ----------------------------------------------------------------

def _act(label, op_id, kwargs=None, icon=None):
    return (label, op_id, dict(kwargs or {}), None, 1.0, icon)


def _menu(label, menu_id, icon=None):
    """A button that drops down one of the right-click menu's own lists."""
    from ...operators import generic_page
    return (label + "  ›", generic_page._opener(menu_id, label), None, None,
            1.0, icon)


def _menu_actions(context, obj, skip=(), limit=8):
    """The first commands of `obj`'s right-click menu, as buttons. Add
    Accessory is left out: the page's Accessories list has it."""
    from ...operators import generic_page, quick_actions
    skip = tuple(skip) + ('hb_frameless.add_opening_accessory',)
    return quick_actions.from_menu(context, generic_page.menu_id(obj),
                                   skip=skip, limit=limit)


def _quick(out, picked, title=None, owner=None):
    """The page's quick actions, in the sections every library uses,
    in a fold of their own that stays closed until opened."""
    from ...operators import options_panel, quick_actions
    fold = quick_actions.fields(picked, title or quick_actions.TITLE,
                                fold='fl_quick_actions')
    if not fold:
        return
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.extend(options_panel.field_blocks(bpy.context, fold, owner))


def _footer(out, prompts_op):
    row = [("All Actions", 'home_builder.all_actions', None, None)]
    if prompts_op:
        row.append(("Properties…", prompts_op, None, None))
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.append(('actions', tuple(row)))


# ---- Accessories ------------------------------------------------------------

_add_open = set()       # hosts whose Add Accessory fold is open


def _toggler(name):
    def toggle():
        if name in _add_open:
            _add_open.discard(name)
        else:
            _add_open.add(name)
    return toggle


def _accessory_rows(out, hosts, where):
    rows = 0
    for host in hosts:
        for index, item in _items().opening_accessories(host):
            text = item.accessory_label or item.accessory_code
            if len(hosts) > 1:
                text = "%s  (%s)" % (text, host.name)
            out.append(('list_row', {
                'key': 'flacc:%s:%d' % (host.name, index),
                'text': text,
                'summary': item.accessory_code,
                'remove': ('hb_frameless.remove_opening_accessory',
                           {'host_name': host.name, 'index': index}),
                'remove_tip': "Remove Accessory",
                'confirm': False,
            }))
            rows += 1
    if not rows:
        out.append(('note', "None in %s." % where))


def _add_fold(context, out, key, hosts, label):
    from ..face_frame import accessory_place
    name = key + ':' + "|".join(h.name for h in hosts)
    open_ = name in _add_open
    out.append(('section', (label, 'fl_add_accessory:' + name, open_,
                            _toggler(name))))
    if open_:
        out.extend(('indent', b) for b in
                   accessory_place.browse_blocks(context, key, hosts))


def accessory_blocks(context, obj):
    """The catalog accessories kept on the door or open opening (or the
    division section) `obj` sits in, each with a remove button, and the
    catalog to add from. Nothing outside such an opening."""
    ii = _items()
    host = ii.accessory_host(obj)
    if host is None:
        return []
    has_catalog = bool(ii.catalog_for(host))
    if not has_catalog and not ii.opening_accessories(host):
        return []
    out = [('gap', None), ('label', "Accessories")]
    _accessory_rows(out, [host], "this opening")
    if has_catalog:
        _add_fold(context, out, 'opening', [host], "Add Accessory")
    return out


# ---- The pages --------------------------------------------------------------

def _size_value(context, obj):
    from ...operators import generic_page
    size = generic_page._size_text(context, obj)
    if not size and any(obj.dimensions):
        us = context.scene.unit_settings
        size = "  x  ".join(units.unit_to_string(us, d) for d in obj.dimensions)
    return ('value', ("Size (W x D x H)", size)) if size else None


def _cabinet_page(context, out, root):
    from ...operators import options_panel, prop_proxy
    out.extend(options_panel.field_blocks(
        context, _cabinet_fields(root), prop_proxy.owner(root, CABINET_SCHEMA)))
    _footer(out, 'hb_frameless.cabinet_prompts')


def _has_splitter(owner):
    return any(c.get('IS_FRAMELESS_SPLITTER_VERTICAL_CAGE')
               or c.get('IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE')
               for c in owner.id_data.children_recursive)


def _has_fronts(owner):
    from .operators.ops_opening import front_height_splitter
    try:
        return front_height_splitter(owner.id_data) is not None
    except Exception:
        return False


def _bay_fields(bay_obj):
    """The bay page, laid out as the face frame bay's: what it is built
    as, its size, and the quick actions folded at the foot. A frameless
    bay is the cabinet's whole box, so its size follows the cabinet."""
    quick = _quick_fields(bay_obj, (
        ((_act("Edit Opening Sizes", 'hb_frameless.edit_splitter_openings'),
          _has_splitter),
         (_act("Edit Door/Drawer Sizes", 'hb_frameless.edit_front_heights'),
          _has_fronts)),
        ((_act("Finish Interior", 'hb_frameless.finish_interior'), None),),
    ), fold='fl_bay_quick_actions')
    return (
        ('enum', 'config', "Configuration"),
        ('value', lambda _o, b=bay_obj: _bay_size(b), "Size (W x H)"),
        ('gap', None, None),
    ) + _front_fields(bay_obj) + quick


def _front_fields(bay_obj):
    """The fronts typed by height, top to bottom. A typed height is held
    (its padlock lets it go again); the fronts left free share the rest."""
    from . import bay_config
    try:
        rows = bay_config.front_rows(bay_obj)
    except Exception:
        rows = []
    rows = [r for r in rows if r[0] <= bay_config.FRONT_ROWS]
    if not rows:
        return ()

    def chip(index):
        def action(owner):
            for i, _label, _height, held in bay_config.front_rows(owner.id_data):
                if i == index and held:
                    return ('hb_frameless.release_front_height',
                            {'bay_name': owner.id_data.name, 'index': index},
                            'lock', "Held. Click to let it share what is left")
            return None
        return action
    fields = [('label', None, "Front Heights")]
    fields += [('distance', 'front_%d' % i, label, {'action': chip(i)})
               for i, label, _height, _held in rows]
    fields.append(('gap', None, None))
    return tuple(fields)


def _bay_page(context, out, bay_obj, title):
    from ...operators import options_panel, prop_proxy
    from . import bay_config, solver_frameless
    page = list(options_panel.field_blocks(
        context, _bay_fields(bay_obj),
        prop_proxy.owner(bay_obj, bay_config.schema_key(bay_obj))))
    root = solver_frameless.cabinet_root(bay_obj)
    if root is not None and root.get('IS_BLIND_CORNER'):
        # A blind corner's bay is its door opening: the one bay width
        # that is typed rather than read.
        blocks = options_panel.field_blocks(context, (
            ('distance', 'blind_opening_width', "Door Opening Width"),
        ), prop_proxy.owner(root, CABINET_SCHEMA))
        at = next((i for i, b in enumerate(page) if b[0] == 'gap'), len(page))
        page[at:at] = blocks
    out.extend(page)
    _footer(out, None)


def _in_splitter(owner):
    from . import bay_config
    outer = bay_config.outer_opening(owner.id_data)
    return outer.parent is not None and any(
        outer.parent.get(t) for t in bay_config._SPLITTER_TAGS)


def _stacked_fronts(owner):
    from .operators.ops_opening import front_height_splitter
    try:
        return front_height_splitter(owner.id_data) is not None
    except Exception:
        return False


def _opening_quick(opening_obj, has_interior):
    actions = [
        ((_act("Edit Opening Sizes", 'hb_frameless.edit_splitter_openings'),
          _in_splitter),
         (_act("Edit Door/Drawer Sizes", 'hb_frameless.edit_front_heights'),
          _stacked_fronts)),
    ]
    if has_interior and hasattr(bpy.types, 'HOME_BUILDER_MT_interior_change'):
        actions.append(((_menu("Change Interior",
                               'HOME_BUILDER_MT_interior_change'), None),))
    actions += [
        ((_act("Split Vertical", 'hb_frameless.custom_vertical_splitter'), None),
         (_act("Split Horizontal", 'hb_frameless.custom_horizontal_splitter'),
          None)),
        ((_act("Finish Interior", 'hb_frameless.finish_interior'), None),),
    ]
    return _quick_fields(opening_obj, actions, fold='fl_opening_quick_actions')


def _opening_page(context, out, opening_obj):
    """The opening page, laid out as the face frame opening's: its size
    and front, what is inside, the front's details and overlays in folds,
    and the quick actions folded at the foot."""
    from ...operators import options_panel, prop_proxy
    from . import bay_config
    front = bay_config.front_opening(opening_obj)
    owner = prop_proxy.owner(front, OPENING_SCHEMA)
    out.extend(options_panel.field_blocks(context, OPENING_FIELDS, owner))
    # What is inside, said here; its settings are on its own page.
    interior = _interior_of(front)
    has_interior = (interior is not None
                    or _items().accessory_host(front) is not None)
    if _items().drawer_opening_for(front) is None and not bay_config.is_split(front):
        out.append(('value', ("Interior", _interior_summary(interior))))
    if has_interior:
        out.append(('actions', (
            _act("Edit Interior", 'hb_frameless.show_interior_page',
                 {'opening_name': front.name}, 'cab_interior'),)))
    out.extend(options_panel.field_blocks(context, OPENING_FOLDS, owner))
    out.extend(accessory_blocks(context, front))
    out.extend(options_panel.field_blocks(
        context, _opening_quick(front, has_interior), owner))
    # Every setting of the opening dialog is on the page above.
    _footer(out, None)


def _interior_page(context, out, part_obj, opening_obj, bay_obj):
    """The Interior page: a picture of the interior with its fixed
    shelves and divisions, then what the pick holds. `part_obj` is a
    shelf or board, a section, or None for the whole interior."""
    from . import interior_page
    host = (interior_page.host_of(part_obj) if part_obj is not None
            else opening_obj or bay_obj)
    if host is None:
        _footer(out, None)
        return
    start = len(out)
    out.extend(interior_page.blocks(context, host, part_obj))
    # A part picked in the viewport: its own size and commands too.
    real = (part_obj is not None and not part_obj.get(TAG_INTERIOR)
            and not part_obj.get('IS_FRAMELESS_INTERIOR_SECTION'))
    if real and not interior_page.is_bar_part(part_obj):
        size = _size_value(context, part_obj)
        if size:
            out.insert(start + 1, size)     # under the picture
    out.extend(accessory_blocks(context, part_obj or host))
    if real:
        out.extend(material_blocks(context, part_obj))
        out.extend(edge_blocks(context, part_obj))
        _quick(out, _menu_actions(context, part_obj, skip=(
            'hb_frameless.interior_prompts', 'HOME_BUILDER_MT_interior_change')))
    _footer(out, None)


def _drawer_page(context, out, part_obj, drawers):
    """The drawer's size, box construction and slides, its commands and
    what is in it -- the face frame Drawer page, on frameless drawers."""
    from ..face_frame import accessory_place
    ops_cabinet = accessory_place.ops_cabinet
    one = len(drawers) <= 1
    if one:
        size = _size_value(context, part_obj)
        if size:
            out.append(size)
        out.extend(_front_opening_blocks(context, drawers[0]))
    options = ops_cabinet.drawer_box_construction_options()
    if options:
        out.append(accessory_place._option_pick(
            'CONSTRUCTION', "Construction", options,
            ops_cabinet.drawer_box_construction_label, drawers))
    options = ops_cabinet.drawer_slides_options()
    if options:
        out.append(accessory_place._option_pick(
            'SLIDES', "Slides", options, ops_cabinet.drawer_slides_label,
            drawers))
    if one:
        out.append(('gap', None))
        out.append(('actions', (
            ("Drawer Interior", 'hb_frameless.drawer_interior', None, None),
            ("Open / Close", 'hb_frameless.toggle_front_open', None, None))))
        if any(c.get('IS_PULLOUT_FRONT') for c in drawers[0].children):
            out.append(('actions', (
                ("Pullout Model", 'hb_frameless.pullout_model', None, None),)))
    out.append(('gap', None))
    out.append(('label', "Accessories"))
    _accessory_rows(out, drawers, "this drawer" if one else "these drawers")
    _add_fold(context, out, 'drawer', drawers,
              "Add Accessory" if one
              else "Add Accessory to %d Drawers" % len(drawers))
    if one and part_obj.get('IS_CABINET_FRONT'):
        out.append(('gap', None))
        out.append(('label', "Front"))
        out.extend(front_blocks(context, part_obj))
    if one:
        _quick(out, _menu_actions(context, part_obj, skip=(
            'hb_frameless.drawer_interior', 'hb_frameless.toggle_front_open',
            'hb_frameless.door_front_prompts',
            'hb_frameless.set_front_handle_type')))
    _footer(out, None)


# ---- Carcass parts -------------------------------------------------------------
# A side, back, top or bottom shows how that face of its cabinet is
# finished, as the face frame side and back pages do; the cabinet page
# has every face at once.

_SIDE_FINISH = {'LEFT': ('left_finish', "Finished End"),
                'RIGHT': ('right_finish', "Finished End"),
                'BACK': ('back_finish', "Back")}
_OTHER_SIDE = {'LEFT': ('RIGHT', "Right"), 'RIGHT': ('LEFT', "Left")}


def _carcass_side(part_obj):
    from . import solver_frameless
    from .operators import ops_finished_ends as fe
    side = fe.FINISH_ROLE_SIDES.get(part_obj.get(solver_frameless.PART_ROLE_KEY))
    cabinet = hb_utils.get_cabinet_bp(part_obj)
    if side is None or cabinet is None \
            or not cabinet.get('IS_FRAMELESS_CABINET_CAGE'):
        return None, None
    return side, cabinet


def _panel_options(side):
    """The applied panel's own sizes, while the side has one."""
    def action(owner):
        from .operators import ops_finished_ends as fe
        cond = fe.finish_condition(owner.id_data, side)
        if cond == '5PIECE':
            return ('hb_frameless.update_finished_end',
                    {'side': side, 'finished_end_type': '5PIECE'},
                    'settings', "5-Piece Panel Options")
        if cond == 'SLAB':
            return ('hb_frameless.applied_end_prompts', {'side': side},
                    'settings', "End Panel Options")
        return None
    return action


def _carcass_fields(side, cabinet):
    if side in _SIDE_FINISH:
        prop, label = _SIDE_FINISH[side]
        fields = [('enum', prop, label, {'action': _panel_options(side)})]
        fields.append(('actions', (
            _act("Follow Neighbors", 'hb_frameless.auto_finish_condition',
                 {'side': side}),), None, {'when': _manual(side)}))
        if side in _OTHER_SIDE:
            from .operators import ops_finished_ends as fe
            other, name = _OTHER_SIDE[side]
            cond = fe.finish_condition(cabinet, side) or 'UNFINISHED'
            fields.append(('actions', (
                _act("Apply to %s Side" % name,
                     'hb_frameless.set_finish_condition',
                     {'side': other, 'condition': cond}),), None))
        return tuple(fields)
    if side == 'TOP':
        return (('enum', 'top_finish', "Top", {'when': _top_finish_shown}),)
    if side == 'BOTTOM':
        return (
            ('enum', 'finished_bottom', "Bottom Panel", {'when': _upper_box}),
            ('bool', 'fb_doors_cover', "Doors Cover Panel", {'when': _fb_on}),
            ('bool', 'fb_led_route', "LED Route", {'when': _fb_on}),
            ('distance', 'fb_led_width', "Route Width", {'when': _fb_led}),
            ('distance', 'fb_led_depth', "Route Depth", {'when': _fb_led}),
            ('distance', 'fb_led_inset', "Route From Front", {'when': _fb_led}),
            ('bool', 'light_valance', "Light Valance", {'when': _upper_box}),
            ('distance', 'lv_depth', "Valance Depth", {'when': _lv_on}),
            ('bool', 'lv_doors_cover', "Doors Cover Valance", {'when': _lv_on}),
        )
    return ()


# Commands the page shows as fields: left out of its quick actions.
_ON_PAGE = ('hb_frameless.door_front_prompts',
            'hb_frameless.set_front_handle_type',
            'hb_frameless.set_finish_condition',
            'hb_frameless.auto_finish_condition',
            'hb_frameless.set_finished_bottom_panel',
            'hb_frameless.applied_end_prompts',
            'hb_frameless.update_finished_end')


def _front_opening_blocks(context, part_obj):
    """For a front: its opening's Front, hinge side and height, as on
    the opening page."""
    from ...operators import options_panel, prop_proxy
    from . import bay_config
    opening = hb_utils.get_opening_bp(part_obj)
    if opening is None:
        return []
    owner = prop_proxy.owner(bay_config.front_opening(opening), OPENING_SCHEMA)
    return list(options_panel.field_blocks(context, OPENING_FIELDS[1:], owner))


def _part_page(context, out, part_obj):
    from ...operators import options_panel, prop_proxy
    size = _size_value(context, part_obj)
    if size:
        out.append(size)
    side, cabinet = _carcass_side(part_obj)
    if side is not None:
        fields = _carcass_fields(side, cabinet)
        shown = options_panel.field_blocks(
            context, fields, prop_proxy.owner(cabinet, CABINET_SCHEMA))
        if shown:
            out.extend(shown)
            out.append(('gap', None))
    front = bool(part_obj.get('IS_CABINET_FRONT'))
    if front:
        out.extend(_front_opening_blocks(context, part_obj))
        out.extend(front_blocks(context, part_obj))
        out.extend(accessory_blocks(context, part_obj))
    out.extend(material_blocks(context, part_obj))
    out.extend(edge_blocks(context, part_obj))
    _quick(out, _menu_actions(context, part_obj, skip=_ON_PAGE),
           owner=part_obj)
    _footer(out, None)


def _product_page(context, out, root):
    from ...operators import options_panel, prop_proxy, generic_page
    if root.get('IS_FACE_FRAME_PRODUCT_CAGE'):
        # A face frame product built on frameless parts (a Half Wall,
        # a Support Frame) wears the face frame cabinet styles.
        from ..face_frame import selected_card as ff_card
        out.extend(ff_card.style_blocks(context, root, 'hb_style_section'))
    schema = (MISC_PART_SCHEMA if root.get('IS_FRAMELESS_MISC_PART')
              else PRODUCT_SCHEMA)
    label = _type_label(root)
    out.extend(options_panel.field_blocks(context, (
        ('group', PRODUCT_GROUP, label or "Product",
         {'icon': 'cab_parts', 'summary': _size_summary, 'fields': PRODUCT_FIELDS}),
    ), prop_proxy.owner(root, schema)))
    if root.get('IS_FRAMELESS_MISC_PART'):
        out.extend(options_panel.field_blocks(
            context, MISC_BAND_FIELDS, prop_proxy.owner(root, schema)))
        out.extend(material_blocks(context, root))
    out.extend(product_option_blocks(context, root))
    # One part of the product picked (a filler's face, a toe skin, a
    # ceiling closure board): its edges can be set one by one.
    part_obj = context.active_object
    if part_obj is not None and part_obj is not root:
        out.extend(material_blocks(context, part_obj))
        out.extend(edge_blocks(context, part_obj))
    _quick(out, _menu_actions(context, root,
                              skip=('hb_frameless.product_prompts',)))
    _footer(out, None)


# ---- Scope: which level of the cabinet the page is on ----------------------
# The tabs under the style move between the cabinet and the bay, opening
# and part last picked inside it, selecting that level the way the
# breadcrumb does -- so a bay's page is one click from its cabinet's and
# back, without finding the bay in the viewport again.

SCOPE_LEVELS = ('Cabinets', 'Bays', 'Openings', 'Parts')
_chain = {}             # cabinet name -> {level: object name}
_scope_now = 'Cabinets'


def _remember(root, bay_obj, opening_obj, part_obj):
    """Note the levels picked inside `root`, dropping any remembered
    below a level that has just changed. Returns the picked level."""
    chain = _chain.setdefault(root.name, {})
    picked = {'Cabinets': root, 'Bays': bay_obj, 'Openings': opening_obj,
              'Parts': part_obj}
    deepest = 0
    for i, level in enumerate(SCOPE_LEVELS):
        obj = picked[level]
        if obj is None:
            continue
        deepest = i
        if chain.get(level) != obj.name:
            for lower in SCOPE_LEVELS[i + 1:]:
                if picked[lower] is None:
                    chain.pop(lower, None)
        chain[level] = obj.name
    # What is remembered must still be in this cabinet.
    for level in SCOPE_LEVELS[1:]:
        name = chain.get(level)
        obj = bpy.data.objects.get(name) if name else None
        if obj is None or hb_utils.get_cabinet_bp(obj) != root:
            chain.pop(level, None)
    return SCOPE_LEVELS[deepest]


def _scope_level(part_obj):
    """The selection mode a remembered part is picked in."""
    if part_obj is not None and part_obj.get('IS_FRAMELESS_INTERIOR_PART'):
        return 'Interiors'
    return 'Parts'


def _scope_schema(levels, labels):
    from ...operators import prop_proxy
    key = SCOPE_PREFIX + '_'.join(levels) + '_' + labels[-1]

    def get(_obj):
        return _scope_now

    def set(obj, value):
        name = _chain.get(obj.name, {}).get(value)
        if not name:
            return
        level = value
        if value == 'Parts':
            level = _scope_level(bpy.data.objects.get(name))
        bpy.ops.hb_frameless.select_level(name=name, level=level)
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
    levels = [level for level in SCOPE_LEVELS if chain.get(level)]
    if len(levels) < 2:
        return []
    labels = [_part_label(bpy.data.objects[chain[level]]) if level == 'Parts'
              else level[:-1] for level in levels]
    _scope_now = current
    key = _scope_schema(levels, labels)
    return options_panel.field_blocks(context, (
        ('choices', 'scope', "", {'cols': len(levels)}),
    ), prop_proxy.owner(root, key))


# ---- The page ---------------------------------------------------------------

def _trail(root, bay_obj, opening_obj, part_obj):
    trail = [root.name]
    if bay_obj is not None:
        trail.append(_index_label(bay_obj, TAG_BAY, "Bay"))
    if opening_obj is not None:
        trail.append(_index_label(opening_obj, TAG_OPENING, "Opening"))
    if part_obj is not None:
        trail.append(_part_label(part_obj))
    return trail


def _part_name_block(part_obj):
    """The picked part's name ("Base Left Side Finished"), or None when
    the pick is not a cut part."""
    if part_obj is None or not part_obj.get('CABINET_PART'):
        return None
    try:
        from . import part_names
        name = part_names.part_name(part_obj)
    except Exception:
        name = None
    return ('value', ("Part Name", name)) if name else None


def _several(kind):
    """How many of the pick's kind are picked, when it is more than one."""
    n = _count({'cabinet': 'cabinet', 'opening': 'opening',
                'product': 'product', 'drawer': 'drawer'}.get(kind, ''))
    return n if n > 1 else 0


def blocks(context, item):
    kind, root, bay_obj, opening_obj, part_obj = item
    _gather(context)

    if kind == 'product':
        n = _several('product')
        out = ([('head', (f"{n} Products", False, None)),
                ('label', f"Changes apply to all {n}")] if n
               else [('head', (root.name, False, None))])
        if not n:
            named = _part_name_block(context.active_object)
            if named:
                out.append(named)
        _product_page(context, out, root)
        return out

    # A hidden section is not a level to come back to from the tabs.
    shown = (None if part_obj is not None
             and part_obj.get('IS_FRAMELESS_INTERIOR_SECTION') else part_obj)
    level = _remember(root, bay_obj, opening_obj, shown)
    trail = _trail(root, bay_obj, opening_obj, part_obj)
    n = _several(kind)
    if n:
        word = {'cabinet': "Cabinets", 'opening': "Openings",
                'drawer': "Drawers"}[kind]
        out = [('head', (f"{n} {word}", False, None)),
               ('label', f"Changes apply to all {n}")]
    else:
        out = [('head', (" › ".join(trail), False, None))]

    out.extend(style_blocks(context, root))
    if not n:
        out.extend(_scope_blocks(context, root, level))
        named = _part_name_block(part_obj or context.active_object)
        if named:
            out.append(named)
    out.append(('gap', None))

    if kind == 'cabinet':
        _cabinet_page(context, out, root)
    elif kind == 'bay':
        _bay_page(context, out, bay_obj, trail[-1])
    elif kind == 'opening':
        _opening_page(context, out, opening_obj)
    elif kind == 'interior':
        _interior_page(context, out, part_obj, opening_obj, bay_obj)
    elif kind == 'drawer':
        drawers = list(_picked['drawer']) or [opening_obj]
        if opening_obj in drawers:
            drawers.remove(opening_obj)
            drawers.insert(0, opening_obj)
        _drawer_page(context, out, part_obj, drawers)
    else:
        _part_page(context, out, part_obj)
    return out


def crumbs(context, item):
    """Cabinet, bay, opening, part: each step above the pick selects
    that level. None while several are picked -- the head says how
    many."""
    kind, root, bay_obj, opening_obj, part_obj = item
    if kind == 'product':
        return None
    _gather(context)
    if _several(kind):
        return None
    op = 'hb_frameless.select_level'
    out = [(root.name, (op, {'name': root.name, 'level': 'Cabinets'}))]
    if bay_obj is not None:
        out.append((_index_label(bay_obj, TAG_BAY, "Bay"),
                    (op, {'name': bay_obj.name, 'level': 'Bays'})))
    if opening_obj is not None:
        out.append((_index_label(opening_obj, TAG_OPENING, "Opening"),
                    (op, {'name': opening_obj.name, 'level': 'Openings'})))
    if part_obj is not None:
        out.append((_part_label(part_obj), None))
    # The last is the pick itself: named, not a click.
    out[-1] = (out[-1][0], None)
    return out


class hb_frameless_OT_select_level(bpy.types.Operator):
    """Pick this cabinet, bay, opening or part, moving the selection mode
    to its level"""
    bl_idname = "hb_frameless.select_level"
    bl_label = "Select"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()  # type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        from . import drill_frameless as drill
        obj = context.view_layer.objects.get(self.name)
        props = getattr(context.scene, 'hb_frameless', None)
        if obj is None or props is None or self.level not in drill.RANK:
            return {'CANCELLED'}
        # Still below the mode bar's level: the drill holds. At or above
        # it, the drill has come all the way back out.
        base = drill.base_level()
        if base is None or drill.RANK[self.level] <= drill.RANK[base]:
            base = None
        drill.set_mode(context, self.level)
        drill.set_base(base)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


# ---- Lifecycle --------------------------------------------------------------

def register():
    bpy.utils.register_class(hb_frameless_OT_select_level)
    from . import interior_page
    interior_page.register()
    _register_schemas()
    from ...operators import selected_tab, options_panel
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)
    options_panel.register_peers(_peers)


def unregister():
    try:
        from ...operators import selected_tab, options_panel
        options_panel.unregister_peers(_peers)
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
    _unregister_schemas()
    from . import interior_page
    interior_page.unregister()
    try:
        from ...operators import prop_proxy
        for key in [k for k in prop_proxy._schemas
                    if k.startswith((STYLE_PREFIX, SCOPE_PREFIX))]:
            prop_proxy.unregister(key)
    except Exception:
        pass
    bpy.utils.unregister_class(hb_frameless_OT_select_level)
