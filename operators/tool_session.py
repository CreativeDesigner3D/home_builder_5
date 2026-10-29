"""Sticky tools and the TOOL page, in house projects (and anywhere for
the tools whose settings are only on the page).

A placement tool started in a house scene - Draw Walls, the door and
window tools, Obstacle, Stairs - runs as a tool session:

* It stays on. Draw Walls and the doors and windows keep placing (their
  own Continuous Drawing, switched on by the house's Tools Stay On);
  Obstacle starts again after each one is dropped. Esc or right-click
  ends it, as before. Stairs place once - a house rarely wants two in a
  row - but still get the page and the switching below.
* The HUD panel shows its settings. The panel switches to a TOOL tab
  with the tool's fields (a wall's type and thickness, a door's width
  and style), which can be changed while the tool runs; the next thing
  placed takes them. When the tool ends the panel goes back to the tab
  it was on.
* Mouse events over the HUD - the panel and the tool strip - pass
  through to it, so both stay clickable while the tool runs. Picking a
  different tool on the strip ends this one and starts that one;
  picking another tab on the panel ends it.

A tool joins in with two lines: begin(self, context) where it adds its
modal handler, @session_modal on its modal(), and a stop_tool(context)
saying how it tears down when asked to stop (what its Esc does). The
stop is asked for through viewport_hud's active-modal registry, which
wakes the modal at once with a timer.
"""
import functools
import sys

import bpy

from .. import hb_house

TAB_KEY = 'TOOL'
TAB_LABEL = "TOOL"
TAB_ORDER = 4           # before HOUSE (5): the thing in hand comes first
PREFERRED_WIDTH = 280   # unscaled

_tool = None            # bl_idname of the tool the session is running
_owner = None           # the operator instance running it
_prev = None            # (panel was open, tab) before the session began
_relaunch = None        # (bl_idname, window, area, region) to start again
_restart = False        # the stop asked for is to start the tool again
_list = None            # the TOOL page's ScrollList

MOUSE_EVENTS = {'MOUSEMOVE', 'LEFTMOUSE', 'RIGHTMOUSE', 'WHEELUPMOUSE',
                'WHEELDOWNMOUSE', 'TRACKPADPAN'}


# =============================================================================
# THE SESSION
# =============================================================================

def is_house(scene):
    return scene is not None and bool(scene.get(hb_house.HOUSE_SCENE_KEY))


def joins(scene, idname):
    """Whether a tool runs as a session in this scene: every tool in a
    house; anywhere, the tools whose settings are only on the TOOL page
    (Fireplace, Bay Window, Furnish, Obstacle...) - with no page they
    would run blind."""
    return scene is not None and (is_house(scene) or idname in HOUSE_PAGES
                                  or idname in ANYWHERE)


def stays_on(context):
    """Whether tools keep going after each placement here."""
    scene = context.scene
    return joins(scene, _tool) and scene.hb_house.tools_stay_on


def active_tool():
    """bl_idname of the tool running in a session, or None."""
    return _tool


def begin(op, context):
    """A tool is starting: make it the session's, and show its page.
    Call where the tool adds its modal handler."""
    global _tool, _owner, _prev
    if not joins(context.scene, type(op).bl_idname):
        return
    from . import viewport_hud, scene_navigator as nav
    op._exit_requested = False
    viewport_hud.register_active_modal(op)
    if _tool is None:
        _prev = (nav.panel_open(), nav.active_tab())
    _tool = type(op).bl_idname
    _owner = op
    nav.set_active_tab(TAB_KEY)
    if not nav.panel_open():
        nav.open_panel()
    _tag_redraw()


def _end():
    """The session is over: put the panel back the way it was."""
    global _tool, _owner, _prev
    from . import scene_navigator as nav
    # Read the tab while the TOOL tab still exists: with no tool it is
    # gone, and the panel would already have fallen back to another.
    on_page = nav.active_tab() == TAB_KEY
    _tool = None
    _owner = None
    prev, _prev = _prev, None
    if prev is not None and on_page:
        was_open, tab = prev
        if tab != TAB_KEY and tab in nav.tabs():
            nav.set_active_tab(tab)
        if not was_open:
            nav.close_panel()
    _tag_redraw()


def stop(context):
    """Ask the running tool to stop, as its Esc would. True if one was
    running."""
    if _owner is None:
        return False
    from . import viewport_hud
    return viewport_hud.request_exit_active_modal(context)


def restart(context):
    """Stop the running tool and start it again at once, the page staying
    up - for a setting it reads only when it starts (which obstacle)."""
    global _restart
    if _owner is None:
        return False
    _restart = True
    return stop(context)


def _after(op, context, result, stopped):
    """A session tool's modal has returned its last result."""
    global _owner, _relaunch, _restart
    from . import viewport_hud
    timer = getattr(op, '_exit_timer', None)
    if timer is not None:
        try:
            context.window_manager.event_timer_remove(timer)
        except Exception:
            pass
        op._exit_timer = None
    viewport_hud.unregister_active_modal(op)
    if _owner is not op:
        return                      # another tool has already taken over
    if stopped and _restart:
        _restart = False
        _owner = None
        _relaunch = (type(op).bl_idname, context.window, context.area,
                     context.region)
        bpy.app.timers.register(_relaunch_tick, first_interval=0.01)
        return
    if (not stopped and 'FINISHED' in result
            and getattr(op, 'RELAUNCH', False) and stays_on(context)):
        # Start the same tool again once this one has gone; the page
        # stays up in between.
        _owner = None
        _relaunch = (type(op).bl_idname, context.window, context.area,
                     context.region)
        bpy.app.timers.register(_relaunch_tick, first_interval=0.01)
        return
    _end()


def _relaunch_tick():
    global _relaunch
    if _relaunch is None:
        return None
    idname, window, area, region = _relaunch
    _relaunch = None
    try:
        with bpy.context.temp_override(window=window, area=area, region=region):
            _call(idname)
    except Exception as ex:
        print(f"Home Builder: could not restart {idname}: {ex}")
    if _owner is None:
        _end()                      # it did not start again
    return None


def _call(idname):
    mod, name = idname.split(".", 1)
    getattr(getattr(bpy.ops, mod), name)('INVOKE_DEFAULT')


def launch(context, idname):
    """Start a tool from the strip: the running one, if any, is asked
    to stop first. Picking the tool that is already running does
    nothing."""
    if idname == _tool and _owner is not None:
        return
    stop(context)
    _call(idname)


def _over_hud(context, event):
    """Whether a mouse event lands on the HUD - its widgets, the panel,
    or the tool strip."""
    from . import viewport_hud, room_palette
    area = context.area
    if area is None:
        return False
    region = context.region
    if region is None or region.type != 'WINDOW':
        return False
    mx, my = event.mouse_region_x, event.mouse_region_y
    try:
        if viewport_hud.click_hits_widget(context, area, mx, my):
            return True
        if room_palette._palette_active(context):
            layout = room_palette.compute_layout(area)
            if (room_palette._hit(mx, my, layout) is not None
                    or room_palette._hit_settings(mx, my, layout) is not None
                    or room_palette._hit_toggle(mx, my, layout)):
                return True
    except Exception:
        return False
    return False


def _tab_left(context):
    """The user picked another tab on the panel while the tool ran."""
    from . import scene_navigator as nav
    return nav.panel_open() and nav.active_tab() != TAB_KEY


def session_modal(fn):
    """Wrap a tool's modal(): HUD events pass through, a stop request or
    a tab change ends the tool (through its stop_tool), and the session
    hears when it is done."""
    @functools.wraps(fn)
    def modal(self, context, event):
        # A stop asked of a tool that has just been replaced still has
        # to reach it, so this one is not only for the owner.
        if getattr(self, '_exit_requested', False) or (_owner is self and _tab_left(context)):
            self._exit_requested = False
            result = self.stop_tool(context)
            _after(self, context, result, stopped=True)
            return result
        if (_owner is self and event.type in MOUSE_EVENTS
                and _over_hud(context, event)):
            return {'PASS_THROUGH'}
        result = fn(self, context, event)
        if _owner is self and not ({'RUNNING_MODAL', 'PASS_THROUGH'} & result):
            _after(self, context, result, stopped=False)
        return result
    return modal


def _tag_redraw():
    wm = bpy.context.window_manager
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# =============================================================================
# THE TOOL PAGE
# =============================================================================

def _wall_notes(context, hb):
    if hb.wall_type in ('Exterior', 'Interior'):
        return ["Height follows the level's ceiling height."]
    if hb.wall_type == 'Porch':
        return ["The open side of a porch: draw from the house",
                "round its outer edge."]
    if hb.wall_type == 'Divider':
        return ["Splits an open space into rooms.",
                "Draw it across the opening, wall to wall."]
    return []


def _is(*types):
    return lambda hb: hb.wall_type in types


WALL_FIELDS = (
    ('choices', 'wall_type', "Wall Type", {'cols': 3}),
    ('distance', 'exterior_wall_thickness', "Thickness", {'when': _is('Exterior')}),
    ('distance', 'interior_wall_thickness', "Thickness", {'when': _is('Interior', 'Half')}),
    ('distance', 'half_wall_height', "Height", {'when': _is('Half')}),
    ('distance', 'fake_wall_height', "Height", {'when': _is('Fake')}),
    ('distance', 'railing_height', "Height", {'when': _is('Railing')}),
    ('distance', 'railing_thickness', "Thickness", {'when': _is('Railing')}),
    ('notes', _wall_notes, "", {'owner': True}),
)

DOOR_FIELDS = (
    ('distance', 'door_single_width', "Width"),
    ('distance', 'door_height', "Height"),
    ('choices', 'entry_door_type', "Door Type", {'cols': 3}),
    ('choices', 'entry_door_style', "Style", {'cols': 2}),
)

DOUBLE_DOOR_FIELDS = (
    ('distance', 'door_double_width', "Width"),
    ('distance', 'door_height', "Height"),
    ('choices', 'entry_door_type', "Door Type", {'cols': 3}),
    ('choices', 'entry_door_style', "Style", {'cols': 2}),
)

OPENING_FIELDS = (
    ('distance', 'door_single_width', "Width"),
    ('distance', 'door_height', "Height"),
)

WINDOW_FIELDS = (
    ('distance', 'window_width', "Width"),
    ('distance', 'window_height', "Height"),
    ('distance', 'window_height_from_floor', "From Floor"),
    ('choices', 'window_style', "Style", {'cols': 2}),
)

# On scene.hb_house: what goes on a window outdoors
WINDOW_OUTDOOR_FIELDS = (
    ('choices', 'window_shutters', "Shutters", {'cols': 2}),
    ('choices', 'window_ext_trim', "Exterior Trim", {'cols': 2}),
)

# On scene.hb_obstacles: the whole library, grouped as it is listed, then
# the size of the one picked. Picking another restarts the tool with it.
OBSTACLE_FIELDS = (
    ('choices', 'obstacle_type', "", {'cols': 2}),
    ('gap', None, ""),
    ('distance', 'obstacle_width', "Width"),
    ('distance', 'obstacle_height', "Height"),
    ('distance', 'obstacle_depth', "Depth"),
    ('distance', 'obstacle_height_from_floor', "From Floor"),
)

def _mat(*kinds):
    return lambda house: house.member_material in kinds


# On scene.hb_house: what the next beam or post placed is
BEAM_FIELDS = (
    ('choices', 'member_material', "Material", {'cols': 4}),
    ('choices', 'member_lumber', "Size", {'cols': 4, 'when': _mat('LUMBER')}),
    ('number', 'member_plies', "Plies", {'when': _mat('LUMBER', 'LVL')}),
    ('distance', 'member_depth', "Depth", {'when': _mat('LVL', 'GLULAM', 'STEEL')}),
    ('distance', 'member_width', "Width", {'when': _mat('GLULAM', 'STEEL')}),
    ('choices', 'beam_position', "Position", {'cols': 2}),
    ('bool', 'beam_end_posts', "Posts at Ends"),
    ('choices', 'post_size', "Post", {'cols': 4,
                                      'when': lambda house: house.beam_end_posts
                                      and house.member_material != 'STEEL'}),
)

POST_FIELDS = (
    ('choices', 'member_material', "Material", {'cols': 4}),
    ('choices', 'post_size', "Size", {'cols': 4, 'when': lambda house: house.member_material != 'STEEL'}),
    ('distance', 'member_width', "Width", {'when': _mat('STEEL')}),
)

# On scene.hb_house: the Furnish catalog, by category; picking one
# restarts the tool with it
FURNISH_FIELDS = (
    ('choices', 'furnish_item', "", {'cols': 2}),
)


def _bay_is(*kinds):
    return lambda house: house.bay_kind in kinds


BAY_FIELDS = (
    ('choices', 'bay_kind', "Kind", {'cols': 3}),
    ('distance', 'bay_width', "Width"),
    ('distance', 'bay_projection', "Projection"),
    ('number', 'bay_side_angle', "Side Angle", {'when': _bay_is('BAY')}),
    ('number', 'bay_segments', "Segments", {'when': _bay_is('BOW')}),
    ('choices', 'bay_base', "Base", {'cols': 2}),
    ('distance', 'bay_seat_height', "Seat Height", {'when': lambda house: house.bay_base == 'SEAT'}),
    ('distance', 'bay_head_height', "Head Height"),
    ('choices', 'bay_roof', "Roof", {'cols': 3}),
    ('number', 'bay_roof_pitch', "Roof Pitch (in 12)", {'when': lambda house: house.bay_roof != 'NONE'}),
)

FIREPLACE_FIELDS = (
    ('distance', 'fireplace_width', "Opening Width"),
    ('distance', 'fireplace_height', "Opening Height"),
    ('choices', 'fireplace_chimney', "Chimney", {'cols': 3}),
    ('choices', 'fireplace_style', "Chimney Style", {'cols': 2}),
    ('choices', 'fireplace_mantel', "Mantel", {'cols': 3}),
)

STAIR_FIELDS = (
    ('choices', 'stair_from', "Draw From", {'cols': 2}),
    ('choices', 'stair_type', "Type", {'cols': 3}),
    ('choices', 'stair_turn', "Turn", {'cols': 2, 'when': lambda h: h.stair_type != 'STRAIGHT'}),
    ('bool', 'stair_winders', "Winders", {'when': lambda h: h.stair_type in ('L_SHAPE', 'U_SHAPE')}),
    ('distance', 'stair_radius', "Inside Radius", {'when': lambda h: h.stair_type == 'CURVED'}),
    ('distance', 'stair_diameter', "Diameter", {'when': lambda h: h.stair_type == 'SPIRAL'}),
    ('distance', 'stair_width', "Width", {'when': lambda h: h.stair_type != 'SPIRAL'}),
    ('distance', 'stair_max_riser', "Max Riser"),
    ('distance', 'stair_tread', "Tread Depth", {'when': lambda h: h.stair_type != 'SPIRAL'}),
    ('choices', 'stair_risers', "Risers", {'cols': 2}),
    ('choices', 'stair_stringer', "Stringers", {'cols': 3, 'when': lambda h: h.stair_type != 'SPIRAL'}),
    ('choices', 'stair_railing', "Railings", {'cols': 2}),
    ('choices', 'stair_baluster', "Railing Style", {'cols': 2, 'when': lambda h: h.stair_railing != 'NONE'}),
)

SKYLIGHT_FIELDS = (
    ('distance', 'skylight_width', "Width"),
    ('distance', 'skylight_length', "Length"),
    ('choices', 'skylight_curb', "Mounting", {'cols': 2}),
    ('choices', 'skylight_shaft', "Light Shaft", {'cols': 2}),
)

# Tools whose fields are on scene.hb_house rather than scene.home_builder
HOUSE_PAGES = {
    "home_builder.place_skylight": ("Skylight", SKYLIGHT_FIELDS),
    "home_builder_doors_windows.place_fireplace": ("Fireplace", FIREPLACE_FIELDS),
    "home_builder_doors_windows.place_bay": ("Bay Window", BAY_FIELDS),
    "home_builder.furnish": ("Furnish", FURNISH_FIELDS),
    "home_builder_stairs.place_stairs": ("Stairs", STAIR_FIELDS),
    "home_builder.place_beam": ("Beam", BEAM_FIELDS),
    "home_builder.place_post": ("Post", POST_FIELDS),
}

# Tools on scene.home_builder's pages that also run as sessions outside
# a house
ANYWHERE = {"home_builder_obstacles.place_obstacle"}

# bl_idname: (title, fields on scene.home_builder)
PAGES = {
    "home_builder_walls.draw_walls": ("Draw Walls", WALL_FIELDS),
    "home_builder_doors_windows.place_door": ("Single Door", DOOR_FIELDS),
    "home_builder_doors_windows.place_double_door": ("Double Door", DOUBLE_DOOR_FIELDS),
    "home_builder_doors_windows.place_open_door": ("Open Doorway", OPENING_FIELDS),
    "home_builder_doors_windows.place_window": ("Window", WINDOW_FIELDS),
    "home_builder_obstacles.place_obstacle": ("Obstacle", ()),
}

HINTS = {
    "home_builder_walls.draw_walls": "C closes the room · T tracks a point",
    "home_builder_obstacles.place_obstacle": "Pick one above, then click a wall, floor or ceiling",
    "home_builder_stairs.place_stairs": "R turns it, click to place · or press and drag the way it "
                                        "climbs · sides snap to walls · T type · D turn side",
    "home_builder.place_beam": "Snaps to wall corners and faces, posts and beam ends",
    "home_builder.place_post": "Runs up to the beam over it, or to the ceiling",
    "home_builder.place_skylight": "Click on the roof: it lies on the slope there",
    "home_builder_doors_windows.place_fireplace": "Click a wall · arrow keys for offset, W for width",
    "home_builder_doors_windows.place_bay": "Click an outside wall · arrow keys for offset, W for width",
    "home_builder.furnish": "Pick one above · click a wall face, or furniture on the floor (R turns it)",
}


def available(scene):
    return _tool is not None and joins(scene, _tool)


def _blocks(context):
    from . import options_panel
    title, fields = PAGES.get(_tool, ("Tool", ()))
    hb = context.scene.home_builder
    if _tool in HOUSE_PAGES:
        title, fields = HOUSE_PAGES[_tool]
        hb = context.scene.hb_house
    blocks = [('head', (title, False, None))]
    if _tool == "home_builder_obstacles.place_obstacle":
        blocks.extend(options_panel.field_blocks(
            context, OBSTACLE_FIELDS, context.scene.hb_obstacles))
    blocks.extend(options_panel.field_blocks(context, fields, hb))
    if _tool == "home_builder_doors_windows.place_window":
        blocks.extend(options_panel.field_blocks(
            context, WINDOW_OUTDOOR_FIELDS, context.scene.hb_house))
    if _tool == "home_builder_walls.draw_walls":
        blocks.append(('note', "Changes apply to the wall you are drawing."))
    elif fields:
        blocks.append(('note', "Changes take effect on the next one placed."))
    hint = HINTS.get(_tool)
    if hint:
        blocks.append(('note', hint))
    blocks.append(('gap', None))
    blocks.extend(options_panel.field_blocks(context, (
        ('bool', 'tools_stay_on', "Tools Stay On"),
        ('notes', lambda context: ["Esc or right-click when you are done."], ""),
        ('actions', (("Done", "home_builder.end_tool"),), ""),
    ), context.scene.hb_house))
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


class HOME_BUILDER_OT_end_tool(bpy.types.Operator):
    """Finish with the tool that is running"""
    bl_idname = "home_builder.end_tool"
    bl_label = "Done"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        stop(context)
        return {'FINISHED'}


def register():
    from . import scene_navigator
    bpy.utils.register_class(HOME_BUILDER_OT_end_tool)
    scene_navigator.register_tab(TAB_KEY, sys.modules[__name__],
                                 label=TAB_LABEL, order=TAB_ORDER,
                                 available=available)


def unregister():
    from . import scene_navigator
    try:
        scene_navigator.unregister_tab(TAB_KEY)
    except Exception:
        pass
    bpy.utils.unregister_class(HOME_BUILDER_OT_end_tool)
