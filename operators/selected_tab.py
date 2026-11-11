"""The page of what is picked: the settings of the bay window,
fireplace, light, stair, obstacle or piece of furniture selected, in any
project, drawn by the selection inspector (``selection_inspector``),
docked down the right side or floating.

A product library can show its own products here too: it registers a
source with ``register_source`` -- a finder that says whether the
selection is one of its products, and a function that lays out that
product's page as Options-tab blocks. Sources are asked before the
house items, in the order they register.

This was once the panel's SELECTED tab, which took the panel over at
every pick; the page lives in the inspector alone now, and the panel
stays on whatever tab the user has it on.
"""
import bpy
from bpy.app.handlers import persistent


_shown = set()          # the groups opened here once this session
_owner = object()
_sources = []           # (key, find(context) -> item or None, blocks(context, item), crumbs)
_pages = []             # (key, find(context) -> bool, provider module)


def register_source(key, find, blocks, crumbs=None, first=False):
    """Show a library's products on this tab. `find(context)` returns
    whatever `blocks(context, item)` needs to lay the page out, or None
    when the selection is not one of them. `crumbs(context, item)`, if
    given, names where the pick sits -- [(text, (operator, kwargs) or
    None)], outermost first, the last being the pick itself -- for the
    inspector's title, where each step up is a click. `first` puts it
    ahead of the sources already registered. Re-registering a key
    replaces it."""
    unregister_source(key)
    if first:
        _sources.insert(0, (key, find, blocks, crumbs))
    else:
        _sources.append((key, find, blocks, crumbs))


def unregister_source(key):
    _sources[:] = [src for src in _sources if src[0] != key]


def register_page(key, find, provider):
    """Show a pick whose page draws itself -- a picture to edit on, not
    a run of fields. `provider` lays the page out and takes its input
    the way a panel tab does (build(rect, context) -> entries, paint,
    hit, scroll), with title(context) naming it; `find(context)` says
    whether the selection is one of its picks. Asked before the
    sources. Re-registering a key replaces it."""
    unregister_page(key)
    _pages.append((key, find, provider))


def unregister_page(key):
    _pages[:] = [page for page in _pages if page[0] != key]


def page_provider(context):
    """The provider drawing the page of what is picked, or None when
    the page is made of blocks."""
    for _key, find, provider in list(_pages):
        try:
            if find(context):
                return provider
        except Exception:
            continue
    return None


def _source_item(context):
    """(blocks function, item) from the first source claiming the
    selection, or None."""
    found = _claim(context)
    return (found[0][2], found[1]) if found is not None else None


def _claim(context):
    """(source, item) for the first source claiming the selection."""
    for src in list(_sources):
        try:
            item = src[1](context)
        except Exception:
            item = None
        if item is not None:
            return src, item
    return None


def crumbs(context):
    """Where the pick sits, from its source, or None."""
    found = _claim(context)
    if found is None or found[0][3] is None:
        return None
    try:
        return found[0][3](context, found[1]) or None
    except Exception:
        return None


def _on_wall(obstacle):
    parent = obstacle.id_data.parent
    return parent is not None and bool(parent.get('IS_WALL_BP'))


def _off_wall(obstacle):
    """A floor or ceiling obstacle with a wall to be measured from."""
    from . import ops_obstacles
    return (not _on_wall(obstacle)
            and ops_obstacles.reference_wall(obstacle.id_data) is not None)


def _has_wall(obstacle):
    return _on_wall(obstacle) or _off_wall(obstacle)


def _obstacle_summary(o):
    from .. import units
    us = bpy.context.scene.unit_settings
    return f"{units.unit_to_string(us, o.width)} x {units.unit_to_string(us, o.height)}"


OBSTACLE_FIELDS = (
    ('group', 'selected_obstacle', "Selected Obstacle", {'summary': _obstacle_summary, 'fields': (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('choices', 'anchor_x', "Measure From", {'cols': 2, 'when': _has_wall}),
        ('distance', 'from_side', "From Side", {'when': _has_wall}),
        ('distance', 'from_wall', "Off Wall", {'when': _off_wall}),
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
    return (page_provider(context) is not None
            or _source_item(context) is not None or _item(context) is not None
            or _generic(context) is not None)


def _generic(context):
    """A pick nothing else has a page for, shown by its right-click
    menu's commands (generic_page), or None."""
    from . import generic_page
    try:
        return generic_page.find(context)
    except Exception:
        return None


def _blocks(context):
    from . import house_panel_tab as hpt, options_panel, all_actions
    # The pick's whole right-click menu, opened from its page.
    if all_actions.showing(context):
        return all_actions.page_blocks(context)
    sourced = _source_item(context)
    if sourced is not None:
        blocks_fn, item = sourced
        blocks = list(blocks_fn(context, item))
        return blocks
    found = _item(context)
    if found is None:
        from . import generic_page
        obj = _generic(context)
        if obj is None:
            return [('note', "Select a product to see its settings here.")]
        return list(generic_page.blocks(context, obj))
    kind, cage = found
    blocks = []
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


# ---- Following the selection -------------------------------------------------------

def _active_changed():
    """Something else was picked: the inspector shows it."""
    from . import tool_session
    tool_session._tag_redraw()


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
    _subscribe()


def register():
    from . import selection_inspector
    selection_inspector.register()
    _subscribe()
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)


def unregister():
    from . import selection_inspector
    selection_inspector.unregister()
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)
    bpy.msgbus.clear_by_owner(_owner)
