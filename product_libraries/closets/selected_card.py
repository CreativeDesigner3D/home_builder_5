"""Closets on the viewport panel's SELECTED tab.

Picking a closet, a bay or an opening shows it there, read down from
the closet to what is picked -- Closet > Bay 2 > Opening 1 -- the way
face frame cabinets read. The part picked is the section that starts
open; the title is a breadcrumb, and a click on a step above selects it.

The sizes and switches that rebuild the closet as they change are
fields here. Each section holds what its dialog did -- the closet's
(starter_card), the bay's (bay_card) and the opening's, with its
interior, rod, front, overlays, pulls and back (opening_card) -- in
groups that fold, so there is no dialog to open for any of them.
"""

import bpy

from . import types_closets


SOURCE_KEY = 'CLOSETS'

STARTER_GROUP = 'cl_starter'
BAY_GROUP = 'cl_bay'
OPENING_GROUP = 'cl_opening'

LEVELS = ('Starters', 'Bays', 'Openings', 'Parts')

_last_kind = None


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, root, bay_obj, opening_obj) for a picked closet or part of
    one, or None. `kind` is 'part' for a piece of the run picked in
    Parts mode (the active object), else 'starter', 'bay' or
    'opening' -- the nearest of them above what was clicked."""
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
    from . import part_page
    if part_page.is_part(obj, root):
        return ('part', root, bay, opening)
    if opening is not None:
        return ('opening', root, bay, opening)
    if bay is not None:
        return ('bay', root, bay, None)
    return ('starter', root, None, None)


# ---- The page ---------------------------------------------------------------

def _fold_for(context, kind):
    global _last_kind
    if kind == _last_kind:
        return
    _last_kind = kind
    from ...operators import options_panel
    primary = {'starter': STARTER_GROUP, 'bay': BAY_GROUP,
               'opening': OPENING_GROUP}.get(kind)
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
    part = context.active_object if kind == 'part' else None
    if part is not None:
        from . import part_page
        trail.append(part_page.label(part))
    out = [('head', (" › ".join(trail), False, None))]
    _fold_for(context, kind)

    from . import starter_card
    if kind == 'part':
        # Parts mode: the part's own page, its size and what builds it.
        from . import part_page
        shown = part_page.blocks(context, part, root, bay_obj, opening_obj)
        out.extend(shown)
        _actions(context, out, part, skip=part_page.ON_PAGE)
        return out
    if kind == 'starter':
        # Starters mode: the closet's own page, its size on top and its
        # parts in folds, with nothing of a bay or opening under it.
        out.extend(options_panel.field_blocks(
            context, starter_card.page_fields(root), starter_card.owner(root)))
        _actions(context, out, root)
        return out
    if kind == 'bay':
        # Bays mode: the bay's own page, what it is built as and its
        # sizes on top, the rest in folds.
        from . import bay_card
        out.extend(options_panel.field_blocks(
            context, bay_card.page_fields(bay_obj), bay_card.owner(bay_obj)))
        # Bay Configuration is the dropdown at the top of the page.
        _actions(context, out, bay_obj,
                 skip=('HOME_BUILDER_MT_closet_change_bay',))
        return out
    if kind == 'opening':
        # Openings mode: the opening's own page.
        from . import opening_card
        out.extend(options_panel.field_blocks(
            context, opening_card.page_fields(opening_obj),
            opening_card.owner(opening_obj)))
        # Change Opening is the dropdown at the top of the page.
        _actions(context, out, opening_obj,
                 skip=('HOME_BUILDER_MT_closet_change_opening',))
        return out
    out.extend(options_panel.field_blocks(context, (
        ('group', STARTER_GROUP, f"Closet  ({sp.closet_type.title()})",
         {'icon': 'closet_starter',
          'summary': lambda _ow: starter_card.summary(root),
          'fields': starter_card.fields(root)}),
    ), starter_card.owner(root)))
    if bay_obj is not None:
        from . import bay_card
        out.extend(options_panel.field_blocks(context, (
            ('group', BAY_GROUP, trail[1],
             {'icon': 'cab_bay',
              'summary': lambda _ow: bay_card.summary(bay_obj),
              'fields': bay_card.fields(bay_obj)}),
        ), bay_card.owner(bay_obj)))
    if opening_obj is not None:
        from . import opening_card
        out.extend(options_panel.field_blocks(context, (
            ('group', OPENING_GROUP, trail[-1],
             {'icon': 'cab_opening',
              'summary': lambda _ow: opening_card.fill_text(opening_obj),
              'fields': opening_card.fields(opening_obj)}),
        ), opening_card.owner(opening_obj)))
    picked = {'starter': root, 'bay': bay_obj, 'opening': opening_obj}[kind]
    _actions(context, out, picked)
    return out


QUICK_FOLD = 'cl_quick_actions'


def _actions(context, out, picked, skip=()):
    """The commands of what is picked, from its right-click menu, in a
    Quick Actions fold that stays closed until opened, then All Actions
    at the foot."""
    from ...operators import options_panel, generic_page, quick_actions
    menu = generic_page.menu_id(context.active_object) or generic_page.menu_id(picked)
    if menu:
        fold = quick_actions.fields(
            quick_actions.from_menu(context, menu, skip=skip), fold=QUICK_FOLD)
        if fold:
            if out and out[-1] != ('gap', None):
                out.append(('gap', None))
            out.extend(options_panel.field_blocks(context, fold, picked))
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.append(('actions', (("All Actions", 'home_builder.all_actions',
                             None, None),)))


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
    if kind == 'part' and context.active_object is not None:
        from . import part_page
        out.append((part_page.label(context.active_object), None))
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
