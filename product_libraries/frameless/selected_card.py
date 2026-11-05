"""Frameless cabinets and products on the viewport panel's SELECTED tab.

Picking a cabinet, a bay or an opening shows it there, read down from
the cabinet to what is picked -- Cabinet > Bay 2 > Opening 1 -- as face
frame cabinets and closets read; the title is a breadcrumb, and a click
on a step above selects it. Products (legs, panels, floating shelves,
valances ...) get their size and height off the floor.

A frameless cabinet keeps its settings as custom properties and
geometry-node inputs rather than in a property group, so the fields go
through prop_proxy schemas: each write is followed by the solve the
cabinet's own dialog runs. The commands under the fields are the pick's
right-click menu.
"""

import bpy

from ... import hb_utils, units


SOURCE_KEY = 'FRAMELESS'

CABINET_GROUP = 'fl_cabinet'
BAY_GROUP = 'fl_bay'
OPENING_GROUP = 'fl_opening'
PRODUCT_GROUP = 'fl_product'

CABINET_SCHEMA = 'FL_CABINET'
OPENING_SCHEMA = 'FL_OPENING'
PRODUCT_SCHEMA = 'FL_PRODUCT'
MISC_PART_SCHEMA = 'FL_MISC_PART'

LEVELS = ('Cabinets', 'Bays', 'Openings', 'Interiors', 'Parts')

TOE_KICK_TYPES = ("Notch Ends to Floor", "Ladder Style", "Floating",
                  "Leg Levelers")

_last_kind = None

# Prompts that take more than a write -- a toe kick type swaps parts, a
# finished interior repaints the cabinet: the Toe Kick group and the
# dialog handle them.
_DIALOG_ONLY = ('Toe Kick Type', 'Finished Interior')


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """('product', root, None, None) for a frameless product, or
    (kind, root, bay, opening) for a cabinet or part of one -- `kind`
    being 'cabinet', 'bay' or 'opening' -- or None."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    root = hb_utils.get_cabinet_bp(obj)
    if root is None:
        return None
    if 'IS_FRAMELESS_PRODUCT_CAGE' in root:
        return ('product', root, None, None)
    opening = hb_utils.get_opening_bp(obj)
    bay = hb_utils.get_bay_bp(obj)
    if opening is not None and _under(opening, root):
        return ('opening', root, bay if _under(bay, root) else None, opening)
    if bay is not None and _under(bay, root):
        return ('bay', root, bay, None)
    return ('cabinet', root, None, None)


def _under(obj, root):
    o = obj.parent if obj is not None else None
    while o is not None:
        if o == root:
            return True
        o = o.parent
    return False


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _size_summary(owner):
    return f"{_dist(owner.width)} x {_dist(owner.height)} x {_dist(owner.depth)}"


def _has(key):
    return lambda owner: key in owner.id_data


def _hung(owner):
    return owner.id_data.get('CABINET_TYPE') == 'UPPER'


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


# ---- Schemas ----------------------------------------------------------------

def _solve(obj, context):
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


def _register_schemas():
    from ...operators import prop_proxy as P
    P.register(CABINET_SCHEMA, {
        'width': P.node_input('Dim X'),
        'depth': P.node_input('Dim Y'),
        'height': P.node_input('Dim Z'),
        'height_off_floor': P.height_off_floor(),
        'toe_kick_type': _toe_kick_type(),
        'toe_kick_height': P.length('Toe Kick Height'),
        'toe_kick_setback': P.length('Toe Kick Setback'),
        'flush_toe_kick': P.flag('Flush Toe Kick'),
        'toe_kick_panel': P.flag('Toe Kick Panel'),
        'toe_kick_panel_thickness': P.length('Toe Kick Panel Thickness', units.inch(0.375)),
        'toe_kick_end_inset': P.length('Toe Kick End Inset'),
        'remove_bottom': P.flag('Remove Bottom'),
    }, after=_solve)
    P.register(OPENING_SCHEMA, {
        'door_swing': P.index_enum('Door Swing', ("Left", "Right", "Double"), 2),
        'door_mechanism': P.index_enum('Door Mechanism', ("Standard", "Retracting")),
        'lift_mechanism': P.index_enum('Lift Mechanism', (
            "Stay Lift", "Bi-Fold Lift", "Up and Over", "Vertical Lift")),
        'inset_front': P.flag('Inset Front'),
        'half_overlay_top': P.flag('Half Overlay Top'),
        'half_overlay_bottom': P.flag('Half Overlay Bottom'),
        'half_overlay_left': P.flag('Half Overlay Left'),
        'half_overlay_right': P.flag('Half Overlay Right'),
    }, after=_solve)
    P.register(PRODUCT_SCHEMA, {
        'width': P.node_input('Dim X'),
        'depth': P.node_input('Dim Y'),
        'height': P.node_input('Dim Z'),
        'height_off_floor': P.height_off_floor(),
    }, after=_solve_product)
    # A misc part is a cut part: its size is length, width and thickness.
    P.register(MISC_PART_SCHEMA, {
        'width': P.node_input('Length'),
        'depth': P.node_input('Width'),
        'height': P.node_input('Thickness'),
        'height_off_floor': P.height_off_floor(),
    }, after=_solve_product)


def _unregister_schemas():
    from ...operators import prop_proxy
    for key in (CABINET_SCHEMA, OPENING_SCHEMA, PRODUCT_SCHEMA, MISC_PART_SCHEMA):
        prop_proxy.unregister(key)


# ---- Fields -----------------------------------------------------------------

CABINET_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('distance', 'height_off_floor', "Above Floor", {'when': _hung}),
    ('group', 'fl_cab_kick', "Toe Kick", {'icon': 'cab_construction', 'when': _kicked, 'fields': (
        ('enum', 'toe_kick_type', "Type"),
        ('distance', 'toe_kick_height', "Height"),
        ('distance', 'toe_kick_setback', "Setback"),
        ('bool', 'flush_toe_kick', "Flush Toe Kick"),
        ('bool', 'toe_kick_panel', "Kick Panel"),
        ('distance', 'toe_kick_panel_thickness', "Panel Thickness", {'when': _kick_panel}),
        ('distance', 'toe_kick_end_inset', "Hold In From Ends"),
    )}),
    ('bool', 'remove_bottom', "Remove Bottom", {'when': _has('Remove Bottom')}),
)

OPENING_FIELDS = (
    ('enum', 'door_swing', "Door Swing", {'when': _door}),
    ('enum', 'door_mechanism', "Mechanism", {'when': _door}),
    ('enum', 'lift_mechanism', "Lift", {'when': _flip_up}),
    ('bool', 'inset_front', "Inset Front", {'when': _has('Inset Front')}),
    ('group', 'fl_opening_overlays', "Half Overlays", {
        'when': _has('Half Overlay Top'),
        'summary': lambda o: ", ".join(
            n for n, p in (("Top", 'half_overlay_top'), ("Bottom", 'half_overlay_bottom'),
                           ("Left", 'half_overlay_left'), ("Right", 'half_overlay_right'))
            if getattr(o, p)) or "None",
        'fields': (
            ('bool', 'half_overlay_top', "Top"),
            ('bool', 'half_overlay_bottom', "Bottom"),
            ('bool', 'half_overlay_left', "Left"),
            ('bool', 'half_overlay_right', "Right"),
        )}),
)

PRODUCT_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('distance', 'height_off_floor', "Above Floor"),
)


# ---- The page ---------------------------------------------------------------

def _fold_for(context, kind):
    global _last_kind
    if kind == _last_kind:
        return
    _last_kind = kind
    from ...operators import options_panel
    primary = {'cabinet': CABINET_GROUP, 'bay': BAY_GROUP,
               'opening': OPENING_GROUP, 'product': PRODUCT_GROUP}[kind]
    for key in (CABINET_GROUP, BAY_GROUP, OPENING_GROUP, PRODUCT_GROUP):
        method = 'group:' + key
        if bool(options_panel.section_expanded(context, method)) != (key == primary):
            options_panel.toggle_section(context, method)


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


def blocks(context, item):
    from ...operators import options_panel, prop_proxy, generic_page
    kind, root, bay_obj, opening_obj = item
    _fold_for(context, kind)
    trail = [root.name]
    if bay_obj is not None:
        trail.append(_index_label(bay_obj, 'IS_FRAMELESS_BAY_CAGE', "Bay"))
    if opening_obj is not None:
        trail.append(_index_label(opening_obj, 'IS_FRAMELESS_OPENING_CAGE', "Opening"))
    out = [('head', (" › ".join(trail), False, None))]
    label = _type_label(root)

    if kind == 'product':
        if root.get('IS_FACE_FRAME_PRODUCT_CAGE'):
            # A face frame product built on frameless parts (a Half Wall,
            # a Support Frame) wears the face frame cabinet styles.
            from ..face_frame import selected_card as ff_card
            out.extend(ff_card.style_blocks(context, root, 'hb_style_section'))
        schema = (MISC_PART_SCHEMA if root.get('IS_FRAMELESS_MISC_PART')
                  else PRODUCT_SCHEMA)
        out.extend(options_panel.field_blocks(context, (
            ('group', PRODUCT_GROUP, label or "Product",
             {'icon': 'cab_parts', 'summary': _size_summary, 'fields': PRODUCT_FIELDS}),
        ), prop_proxy.owner(root, schema)))
    else:
        out.extend(options_panel.field_blocks(context, (
            ('group', CABINET_GROUP, f"Cabinet  ({label})" if label else "Cabinet",
             {'icon': 'cab_cabinet', 'summary': _size_summary, 'fields': CABINET_FIELDS}),
        ), prop_proxy.owner(root, CABINET_SCHEMA)))
        if bay_obj is not None:
            out.extend(options_panel.field_blocks(context, (
                ('group', BAY_GROUP, trail[1], {'icon': 'cab_bay', 'fields': (
                    ('value', lambda _o, b=bay_obj: _bay_size(b), "Size"),
                )}),
            ), bay_obj))
        if opening_obj is not None:
            out.extend(options_panel.field_blocks(context, (
                ('group', OPENING_GROUP, trail[-1],
                 {'icon': 'cab_opening', 'fields': OPENING_FIELDS}),
            ), prop_proxy.owner(opening_obj, OPENING_SCHEMA)))
    # Every other prompt the pick carries, under folds: the product's
    # options, the cabinet's construction, an interior's shelves.
    if kind == 'product':
        out.extend(generic_page.prompt_blocks(context, root, 'fl_product_prompts',
                                              "Options"))
    else:
        out.extend(generic_page.prompt_blocks(context, root, 'fl_cabinet_prompts',
                                              "All Cabinet Prompts", open_first=False,
                                              exclude=_DIALOG_ONLY))
        interior = hb_utils.get_interior_bp(context.active_object)
        for obj, key, title in ((bay_obj, 'fl_bay_prompts', "Bay Prompts"),
                                (opening_obj, 'fl_opening_prompts', "All Opening Prompts"),
                                (interior, 'fl_interior_prompts', "Interior")):
            if obj is not None and _under(obj, root):
                out.extend(generic_page.prompt_blocks(
                    context, obj, key, title, open_first=key == 'fl_interior_prompts'))
    menu = generic_page.menu_id(context.active_object)
    if menu:
        out.append(('gap', None))
        out.extend(generic_page.command_blocks(context, menu))
    return out


def crumbs(context, item):
    kind, root, bay_obj, opening_obj = item
    if kind == 'product':
        return None
    op = 'hb_frameless.select_level'
    out = [(root.name, (op, {'name': root.name, 'level': 'Cabinets'}))]
    if bay_obj is not None:
        out.append((_index_label(bay_obj, 'IS_FRAMELESS_BAY_CAGE', "Bay"),
                    (op, {'name': bay_obj.name, 'level': 'Bays'})))
    if opening_obj is not None:
        out.append((_index_label(opening_obj, 'IS_FRAMELESS_OPENING_CAGE', "Opening"),
                    (op, {'name': opening_obj.name, 'level': 'Openings'})))
    out[-1] = (out[-1][0], None)
    return out


class hb_frameless_OT_select_level(bpy.types.Operator):
    """Pick this cabinet or bay, moving the selection mode to its level"""
    bl_idname = "hb_frameless.select_level"
    bl_label = "Select"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()  # type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        obj = context.view_layer.objects.get(self.name)
        props = getattr(context.scene, 'hb_frameless', None)
        if obj is None or props is None or self.level not in LEVELS:
            return {'CANCELLED'}
        if props.frameless_selection_mode != self.level:
            props.frameless_selection_mode = self.level
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


# ---- Lifecycle --------------------------------------------------------------

def register():
    bpy.utils.register_class(hb_frameless_OT_select_level)
    _register_schemas()
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)


def unregister():
    try:
        from ...operators import selected_tab
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
    _unregister_schemas()
    bpy.utils.unregister_class(hb_frameless_OT_select_level)
