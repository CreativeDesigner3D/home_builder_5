"""The SELECTED tab: the settings of the bay window, fireplace, light,
stair, obstacle or piece of furniture picked, in any project.

It is there while one of them is selected; the panel switches to it when
one is picked, and goes back to the tab it was on when it is let go.
This is the one place they are shown.

A product library can show its own products here too: it registers a
source with ``register_source`` -- a finder that says whether the
selection is one of its products, and a function that lays out that
product's page as Options-tab blocks. Sources are asked before the
house items, in the order they register.

Unless a user has put it back in the panel, the page is drawn by the
selection inspector (``selection_inspector``) instead, docked down the
right side or floating. While it is out, this tab steps aside: it
leaves the tab strip and no longer takes the panel over when something
is picked.
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
_sources = []           # (key, find(context) -> item or None, blocks(context, item))


def register_source(key, find, blocks):
    """Show a library's products on this tab. `find(context)` returns
    whatever `blocks(context, item)` needs to lay the page out, or None
    when the selection is not one of them. Re-registering a key
    replaces it."""
    unregister_source(key)
    _sources.append((key, find, blocks))


def unregister_source(key):
    _sources[:] = [src for src in _sources if src[0] != key]


def _source_item(context):
    """(blocks function, item) from the first source claiming the
    selection, or None."""
    for _key, find, blocks in list(_sources):
        try:
            item = find(context)
        except Exception:
            item = None
        if item is not None:
            return blocks, item
    return None


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


def has_selection(context):
    """Whether what is picked has a page, wherever the page is drawn."""
    from . import tool_session
    if tool_session.active_tool():
        return False
    return _source_item(context) is not None or _item(context) is not None


def available(scene):
    from . import selection_inspector
    if scene is None or selection_inspector.detached():
        return False
    return has_selection(bpy.context)


def _blocks(context):
    from . import house_panel_tab as hpt, options_panel
    sourced = _source_item(context)
    if sourced is not None:
        blocks_fn, item = sourced
        blocks = list(blocks_fn(context, item))
        # After the page's title, so the name still leads.
        at = 1 if blocks and blocks[0][0] == 'head' else 0
        blocks[at:at] = _pop_out_blocks()
        return blocks
    found = _item(context)
    if found is None:
        return [('note', "Select a bay window, fireplace, light, stair, obstacle or piece of furniture.")]
    kind, cage = found
    blocks = _pop_out_blocks()
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
    blocks[:0] = [('head', (cage.name, False, None))]
    blocks.extend(options_panel.field_blocks(context, fields, owner))
    return blocks


def _pop_out_blocks():
    """On the tab, the command that pops the page out of the panel."""
    from . import selection_inspector
    if selection_inspector.detached():
        return []
    return [('actions', (("Pop Out to Right Side", "home_builder.inspector_dock",
                          {'mode': selection_inspector.MODE_RIGHT}, None),))]


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
    from . import scene_navigator as nav, tool_session, selection_inspector
    if selection_inspector.detached():
        # The inspector follows the selection by itself; the panel is
        # left on whatever tab the user has it on.
        tool_session._tag_redraw()
        return
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


def hand_off():
    """The page has just been popped out: put the panel back the way it
    was before this tab took it over."""
    global _prev
    from . import scene_navigator as nav
    if _prev is not None:
        was_open, tab = _prev
        _prev = None
        if tab in nav.tabs() and tab != TAB_KEY:
            nav.set_active_tab(tab)
        if not was_open:
            nav.close_panel()
    elif nav.active_tab() == TAB_KEY:
        nav.close_panel()


def take_back():
    """The page is back on the tab: show it, if something is picked."""
    _active_changed()


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
    from . import scene_navigator, selection_inspector
    selection_inspector.register()
    scene_navigator.register_tab(TAB_KEY, sys.modules[__name__], label=TAB_LABEL,
                                 order=TAB_ORDER, available=available)
    _subscribe()
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)


def unregister():
    from . import scene_navigator, selection_inspector
    selection_inspector.unregister()
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)
    bpy.msgbus.clear_by_owner(_owner)
    try:
        scene_navigator.unregister_tab(TAB_KEY)
    except Exception:
        pass
