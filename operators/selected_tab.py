"""The SELECTED tab: the settings of the bay window, fireplace, light,
stair, obstacle or piece of furniture picked, in any project.

It is there while one of them is selected; the panel switches to it when
one is picked, and goes back to the tab it was on when it is let go.
This is the one place they are shown.
"""
import sys

import bpy
from bpy.app.handlers import persistent


TAB_KEY = 'SELECTED'
TAB_LABEL = "SELECTED"
TAB_ORDER = 3           # before TOOL (4)
PREFERRED_WIDTH = 280   # unscaled, as the HOUSE tab

_list = None
_shown = set()          # the groups opened here once this session
_prev = None            # (panel was open, tab) before the tab took over
_owner = object()


def _on_wall(obstacle):
    parent = obstacle.id_data.parent
    return parent is not None and bool(parent.get('IS_WALL_BP'))


def _obstacle_summary(o):
    from .. import units
    us = bpy.context.scene.unit_settings
    return f"{units.unit_to_string(us, o.width)} x {units.unit_to_string(us, o.height)}"


OBSTACLE_FIELDS = (
    ('group', 'selected_obstacle', "Selected Obstacle", {'summary': _obstacle_summary, 'fields': (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('choices', 'anchor_x', "Measure From", {'cols': 2, 'when': _on_wall}),
        ('distance', 'from_side', "From Side", {'when': _on_wall}),
        ('choices', 'anchor_z', "Height To", {'cols': 2, 'when': _on_wall}),
        ('distance', 'from_floor', "From Floor", {'when': _on_wall}),
        ('bool', 'blocks_placement', "Block Placement", {'when': _on_wall}),
        ('actions', (("Delete", "home_builder_obstacles.delete_obstacle"),), ""),
    )}),
)


def _selected_obstacle(context):
    for obj in [context.active_object] + list(context.selected_objects):
        if obj is not None and obj.get('IS_OBSTACLE'):
            return obj
    return None


def _item(context):
    """(kind, cage) of what is selected, or None."""
    from . import house_panel_tab as hpt
    for kind, find in (('BAY', hpt._selected_bay), ('FIREPLACE', hpt._selected_fireplace),
                       ('LIGHT', hpt._selected_light), ('FURNITURE', hpt._selected_furnishing),
                       ('STAIR', hpt._selected_stair), ('OBSTACLE', _selected_obstacle)):
        try:
            cage = find(context)
        except Exception:
            cage = None
        if cage is not None:
            return kind, cage
    return None


def available(scene):
    from . import tool_session
    if scene is None or tool_session.active_tool():
        return False
    return _item(bpy.context) is not None


def _blocks(context):
    from . import house_panel_tab as hpt, options_panel
    found = _item(context)
    if found is None:
        return [('note', "Select a bay window, fireplace, light, stair, obstacle or piece of furniture.")]
    kind, cage = found
    fields, owner = {
        'BAY': (hpt.BAY_FIELDS, cage.hb_bay),
        'FIREPLACE': (hpt.FIREPLACE_FIELDS, cage.hb_fireplace),
        'LIGHT': (hpt.LIGHT_FIELDS, cage.hb_light),
        'FURNITURE': (hpt.FURNITURE_FIELDS, cage.hb_furniture),
        'STAIR': (hpt.STAIR_FIELDS, cage.hb_stair),
        'OBSTACLE': (OBSTACLE_FIELDS, cage.hb_obstacle),
    }[kind]
    # The page's one group starts open (the first time; closed after
    # that, it stays closed)
    method = 'group:' + fields[0][1]
    if method not in _shown:
        _shown.add(method)
        if not options_panel.section_expanded(context, method):
            options_panel.toggle_section(context, method)
    blocks = [('head', (cage.name, False, None))]
    blocks.extend(options_panel.field_blocks(context, fields, owner))
    return blocks


def _scroll_list():
    global _list
    if _list is None:
        from . import options_panel
        _list = options_panel.new_scroll_list()
    return _list


def build(rect, context):
    from . import options_panel
    return options_panel.build_page(rect, context, _blocks, _scroll_list())


def paint(entries, mx, my):
    from . import options_panel
    options_panel.paint(entries, mx, my)


def hit(context, mx, my, entries):
    from . import options_panel
    return options_panel.hit(context, mx, my, entries)


def scroll(mx, my, entries, rows):
    from . import options_panel
    return options_panel.scroll_page(mx, my, entries, rows, _scroll_list())


# ---- Following the selection -------------------------------------------------------

def _active_changed():
    """Something else was picked: show its settings, or, let go, put the
    panel back the way it was."""
    global _prev
    from . import scene_navigator as nav, tool_session
    try:
        scene = bpy.context.scene
        here = available(scene)
        if here and nav.active_tab() != TAB_KEY:
            _prev = (nav.panel_open(), nav.active_tab())
            nav.set_active_tab(TAB_KEY)
            if not nav.panel_open():
                nav.open_panel()
        elif not here and _prev is not None:
            was_open, tab = _prev
            _prev = None
            if not tool_session.active_tool() and tab in nav.tabs():
                nav.set_active_tab(tab)
                if not was_open:
                    nav.close_panel()
        tool_session._tag_redraw()
    except Exception as e:
        print(f"selected tab: {e}")


def _subscribe():
    bpy.msgbus.clear_by_owner(_owner)
    bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects, "active"), owner=_owner,
                             args=(), notify=lambda: bpy.app.timers.register(_deferred, first_interval=0.0))


def _deferred():
    # After the furniture and light redirects have picked the whole piece
    _active_changed()
    return None


@persistent
def _load_post(_dummy):
    global _prev
    _prev = None
    _subscribe()


def register():
    from . import scene_navigator
    scene_navigator.register_tab(TAB_KEY, sys.modules[__name__], label=TAB_LABEL,
                                 order=TAB_ORDER, available=available)
    _subscribe()
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)


def unregister():
    from . import scene_navigator
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)
    bpy.msgbus.clear_by_owner(_owner)
    try:
        scene_navigator.unregister_tab(TAB_KEY)
    except Exception:
        pass
