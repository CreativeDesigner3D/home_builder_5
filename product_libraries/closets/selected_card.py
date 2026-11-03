"""Closets on the viewport panel's SELECTED tab.

Picking a closet, a bay or an opening shows it there, read down from
the closet to what is picked -- Closet > Bay 2 > Opening 1 -- the way
face frame cabinets read. The part picked is the section that starts
open; the title is a breadcrumb, and a click on a step above selects it.

The sizes and switches that rebuild the closet as they change are
fields here. What an opening holds is worked out by its dialog from
several settings at once, so the opening section says what it holds and
leaves the change to its commands -- the right-click menu's own.
"""

import bpy

from . import types_closets
from ... import units


SOURCE_KEY = 'CLOSETS'

STARTER_GROUP = 'cl_starter'
BAY_GROUP = 'cl_bay'
OPENING_GROUP = 'cl_opening'

LEVELS = ('Starters', 'Bays', 'Openings', 'Parts')

_last_kind = None


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, root, bay_obj, opening_obj) for a picked closet or part of
    one, or None. `kind` is 'starter', 'bay' or 'opening' -- the
    nearest of them above what was clicked."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    root = types_closets.find_starter_root(obj)
    if root is None:
        return None
    bay = opening = None
    o = obj
    while o is not None and o != root:
        if opening is None and bay is None and o.get(types_closets.TAG_OPENING_CAGE):
            opening = o
        elif bay is None and o.get(types_closets.TAG_BAY_CAGE):
            bay = o
        o = o.parent
    if opening is not None:
        return ('opening', root, bay, opening)
    if bay is not None:
        return ('bay', root, bay, None)
    return ('starter', root, None, None)


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _starter_summary(sp):
    return f"{_dist(sp.width)} x {_dist(sp.height)} x {_dist(sp.depth)}"


def _bay_summary(bp):
    return f"{_dist(bp.width)} x {_dist(bp.height)}"


def _kicked(sp):
    return sp.closet_type in ('BASE', 'TALL', 'ISLAND')


def _countertop(sp):
    return sp.include_countertop


def _backsplash(sp):
    return sp.include_countertop and sp.include_backsplash


def _accent(sp):
    return sp.add_top_accent_shelf


def _fill(op):
    """What fills the opening, and how many, as its dialog reads it."""
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


def _opening_size(op):
    from ...hb_types import GeoNodeObject
    try:
        node = GeoNodeObject(op.id_data)
        return f"{_dist(node.get_input('Dim X'))} x {_dist(node.get_input('Dim Z'))}"
    except Exception:
        return None


def _door(op):
    swing = op.door_swing or 'NONE'
    return None if swing == 'NONE' else swing.replace('_', ' ').title()


# ---- Fields -----------------------------------------------------------------

STARTER_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('group', 'cl_starter_construction', "Construction", {'icon': 'cab_construction', 'fields': (
        ('distance', 'toe_kick_height', "Kick Height", {'when': _kicked}),
        ('distance', 'toe_kick_setback', "Kick Setback", {'when': _kicked}),
        ('bool', 'left_finished_end', "Finished Left End"),
        ('bool', 'right_finished_end', "Finished Right End"),
        ('bool', 'remove_hang_rail', "Remove Hang Rail"),
        ('bool', 'add_top_accent_shelf', "Top Accent Shelf"),
        ('distance', 'top_accent_overhang', "Accent Overhang", {'when': _accent}),
    )}),
    ('group', 'cl_starter_top', "Countertop", {
        'summary': lambda sp: "On" if sp.include_countertop else "Off", 'fields': (
            ('bool', 'include_countertop', "Countertop"),
            ('distance', 'countertop_overhang_front', "Front Overhang", {'when': _countertop}),
            ('distance', 'countertop_overhang_left', "Left Overhang", {'when': _countertop}),
            ('distance', 'countertop_overhang_right', "Right Overhang", {'when': _countertop}),
            ('bool', 'include_backsplash', "Backsplash", {'when': _countertop}),
            ('distance', 'backsplash_height', "Backsplash Height", {'when': _backsplash}),
        )}),
)

BAY_FIELDS = (
    ('locked', 'width', "Width", {'unlock': 'unlock_width'}),
    ('locked', 'height', "Height", {'unlock': 'unlock_height'}),
    ('locked', 'depth', "Depth", {'unlock': 'unlock_depth'}),
    ('bool', 'floor_mounted', "Floor Mounted"),
    ('group', 'cl_bay_more', "More", {'fields': (
        ('bool', 'remove_bottom', "Remove Bottom"),
        ('bool', 'remove_cleat', "Remove Cleat"),
        ('bool', 'double_panel_right', "Double Panel Right"),
        ('bool', 'include_center_back', "Center Back"),
        ('bool', 'is_hamper', "Hamper"),
    )}),
)

OPENING_FIELDS = (
    ('value', _opening_size, "Size"),
    ('value', _fill, "Holds"),
    ('value', _door, "Door"),
)


# ---- The page ---------------------------------------------------------------

def _fold_for(context, kind):
    global _last_kind
    if kind == _last_kind:
        return
    _last_kind = kind
    from ...operators import options_panel
    primary = {'starter': STARTER_GROUP, 'bay': BAY_GROUP,
               'opening': OPENING_GROUP}[kind]
    for key in (STARTER_GROUP, BAY_GROUP, OPENING_GROUP):
        method = 'group:' + key
        if bool(options_panel.section_expanded(context, method)) != (key == primary):
            options_panel.toggle_section(context, method)


def _bay_label(bay_obj):
    return f"Bay {bay_obj.hb_closet_bay.bay_index + 1}"


def _opening_label(bay_obj, opening_obj):
    """Opening N, counted down the bay as the openings stand."""
    holder = bay_obj if bay_obj is not None else opening_obj.parent
    if holder is not None:
        openings = [o for o in holder.children_recursive
                    if o.get(types_closets.TAG_OPENING_CAGE)]
        openings.sort(key=lambda o: -o.matrix_world.translation.z)
        if opening_obj in openings and len(openings) > 1:
            return f"Opening {openings.index(opening_obj) + 1}"
    return "Opening"


def blocks(context, item):
    from ...operators import options_panel, generic_page
    kind, root, bay_obj, opening_obj = item
    sp = root.hb_closet_starter
    trail = [root.name]
    if bay_obj is not None:
        trail.append(_bay_label(bay_obj))
    if opening_obj is not None:
        trail.append(_opening_label(bay_obj, opening_obj))
    out = [('head', (" › ".join(trail), False, None))]
    _fold_for(context, kind)

    out.extend(options_panel.field_blocks(context, (
        ('group', STARTER_GROUP, f"Closet  ({sp.closet_type.title()})",
         {'icon': 'closet_starter', 'summary': _starter_summary,
          'fields': STARTER_FIELDS}),
    ), sp))
    if bay_obj is not None:
        out.extend(options_panel.field_blocks(context, (
            ('group', BAY_GROUP, trail[1],
             {'icon': 'cab_bay', 'summary': _bay_summary, 'fields': BAY_FIELDS}),
        ), bay_obj.hb_closet_bay))
    if opening_obj is not None:
        out.extend(options_panel.field_blocks(context, (
            ('group', OPENING_GROUP, trail[-1],
             {'icon': 'cab_opening', 'summary': _fill, 'fields': OPENING_FIELDS}),
        ), opening_obj.hb_closet_opening))
    # The commands of what is picked: its right-click menu.
    picked = {'starter': root, 'bay': bay_obj, 'opening': opening_obj}[kind]
    menu = generic_page.menu_id(context.active_object) or generic_page.menu_id(picked)
    if menu:
        out.append(('gap', None))
        out.extend(generic_page.command_blocks(context, menu))
    return out


def crumbs(context, item):
    kind, root, bay_obj, opening_obj = item
    op = 'hb_closets.select_level'
    out = [(root.name, (op, {'name': root.name, 'level': 'Starters'}))]
    if bay_obj is not None:
        out.append((_bay_label(bay_obj),
                    (op, {'name': bay_obj.name, 'level': 'Bays'})))
    if opening_obj is not None:
        out.append((_opening_label(bay_obj, opening_obj),
                    (op, {'name': opening_obj.name, 'level': 'Openings'})))
    out[-1] = (out[-1][0], None)
    return out


class hb_closets_OT_select_level(bpy.types.Operator):
    """Pick this closet or bay, moving the selection mode to its level"""
    bl_idname = "hb_closets.select_level"
    bl_label = "Select"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()  # type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        obj = context.view_layer.objects.get(self.name)
        props = getattr(context.scene, 'hb_closets', None)
        if obj is None or props is None or self.level not in LEVELS:
            return {'CANCELLED'}
        if props.closet_selection_mode != self.level:
            props.closet_selection_mode = self.level
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


# ---- Lifecycle --------------------------------------------------------------

def register():
    bpy.utils.register_class(hb_closets_OT_select_level)
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)


def unregister():
    try:
        from ...operators import selected_tab
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
    bpy.utils.unregister_class(hb_closets_OT_select_level)
