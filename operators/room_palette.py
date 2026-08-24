"""Viewport tool palette for building a room.

The room-shell tools -- draw walls, hang doors and windows, add a floor
or ceiling -- live several sidebar sub-panels deep, which is a long way
from the model you are pointing at. This paints them as a compact glyph
strip down the left of the viewport while a room scene is active.

It launches the same operators the sidebar buttons do; no tool logic
lives here, and the sidebar keeps working exactly as before.

Pattern (see the autosave note in ``viewport_hud``): a permanent
POST_PIXEL draw handler plus addon keymap entries that hit-test and pass
every other event through. NEVER a persistent modal operator -- Blender
skips autosave for as long as any modal is running.

Gated on the ``use_room_palette`` addon preference AND the active scene
being a room, so it is silent on layout and detail scenes -- where the
drafting palette takes the same strip.
"""

import bpy
import gpu

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    draw_rect,
    draw_rect_outline,
    draw_lines,
    draw_text,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    scale,
    text_width,
    draw_centered_text,
    paint_frame,
    paint_button,
    draw_polyline,
    arc_points,
)

_ADDON_PKG = __package__.rsplit(".", 1)[0]

# ---- Layout (unscaled px; multiplied by scale() at use) --------------------
MARGIN_X = 8            # inset from the visible region's left edge
TOP_OFFSET = 54         # clears the HUD's scene-navigator button
BTN = 26
BTN_GAP = 3
GROUP_GAP = 10
LABEL_GAP = 8
LABEL_PAD_X = 6
LABEL_TEXT_GAP = 4      # glyph to its name, on a labelled strip
LABEL_HEIGHT = 18
FONT_SIZE = 11
GLYPH_INSET = 6

# ---- Module state ----------------------------------------------------------
_draw_handle = None
_shutdown = False
_addon_keymaps = []
_mouse_region = None
_hover = None
_hover_caret = False     # cursor is on the options corner, not the tool


# ---- Glyphs ----------------------------------------------------------------
# Plan-view symbols, drawn to read at 26px. Local to this palette: they
# are room marks, and nothing else needs them yet.

def _g_wall(shader, box, color):
    """Two parallel runs turning a corner -- walls in plan."""
    x, y, w, h = box
    t = h * 0.28
    draw_polyline(shader, [(x, y + h), (x, y), (x + w, y)], color)
    draw_polyline(shader, [(x + t, y + h), (x + t, y + t), (x + w, y + t)],
                  color)


def _g_door(shader, box, color):
    """Jamb, leaf and swing arc -- the plan door symbol."""
    import math
    x, y, w, h = box
    draw_lines(shader, [(x, y), (x, y + h * 0.18)], color)
    draw_lines(shader, [(x + w, y), (x + w, y + h * 0.18)], color)
    draw_lines(shader, [(x, y), (x, y + h)], color)          # leaf, open 90
    draw_polyline(shader, arc_points(x, y, w, math.pi / 2.0, 0.0, 8), color)


def _g_double_door(shader, box, color):
    """Two leaves meeting in the middle, swinging opposite ways."""
    import math
    x, y, w, h = box
    half = w / 2.0
    draw_lines(shader, [(x, y), (x, y + h * 0.7)], color)
    draw_lines(shader, [(x + w, y), (x + w, y + h * 0.7)], color)
    draw_polyline(shader, arc_points(x, y, half, math.pi / 2.0, 0.0, 6), color)
    draw_polyline(shader, arc_points(x + w, y, half, math.pi / 2.0,
                                     math.pi, 6), color)


def _g_open_door(shader, box, color):
    """A cased opening: jambs, no leaf."""
    x, y, w, h = box
    t = h * 0.22
    draw_lines(shader, [(x, y), (x, y + h), (x + w, y), (x + w, y + h)], color)
    draw_lines(shader, [(x, y + t), (x, y + t)], color)
    draw_rect(shader, x, y + h * 0.45, w * 0.16, t * 0.5, color)
    draw_rect(shader, x + w - w * 0.16, y + h * 0.45, w * 0.16, t * 0.5, color)


def _g_window(shader, box, color):
    """Wall band with the glazing line through it."""
    x, y, w, h = box
    top = y + h * 0.72
    bot = y + h * 0.28
    draw_lines(shader, [(x, bot), (x + w, bot), (x, top), (x + w, top)], color)
    draw_lines(shader, [(x, (top + bot) / 2.0), (x + w, (top + bot) / 2.0)],
               color)
    draw_lines(shader, [(x, bot), (x, top), (x + w, bot), (x + w, top)], color)


def _g_floor(shader, box, color):
    """A slab seen in plan, with a hatched near edge."""
    x, y, w, h = box
    draw_rect_outline(shader, x, y + h * 0.15, w, h * 0.7, color)
    for i in range(1, 4):
        fx = x + w * (i / 4.0)
        draw_lines(shader, [(fx, y + h * 0.15), (fx - w * 0.12, y)], color)


def _g_ceiling(shader, box, color):
    """The same slab, hatched upward -- the ceiling above."""
    x, y, w, h = box
    draw_rect_outline(shader, x, y + h * 0.15, w, h * 0.7, color)
    for i in range(1, 4):
        fx = x + w * (i / 4.0)
        draw_lines(shader, [(fx, y + h * 0.85), (fx - w * 0.12, y + h)], color)


# ---- Tool table ------------------------------------------------------------
# (operator, label, glyph, group, options, options_label)
#   group   -- only controls the gap between runs of buttons
#   options -- name of a sidebar draw function holding this tool's
#              settings, or None. A tool with settings shows a corner
#              caret; clicking that, or right-clicking the button,
#              opens them. Wall height and thickness are wanted while
#              you draw walls, not several sidebar panels away, and the
#              same is true of the door and window defaults.
#   options_label -- what those settings are CALLED. Spelled out
#              rather than derived: 'Draw Walls' + ' Settings' reads
#              badly, and several tools share one form, so the name
#              has to describe the form and not the button.

BUILTIN_TOOLS = (
    ("home_builder_walls.draw_walls", "Draw Walls", _g_wall, 0,
     'draw_wall_settings', "Wall Settings"),
    ("home_builder_doors_windows.place_door", "Single Door", _g_door, 1,
     'draw_door_window_defaults', "Door & Window Settings"),
    ("home_builder_doors_windows.place_double_door", "Double Door",
     _g_double_door, 1, 'draw_door_window_defaults', "Door & Window Settings"),
    ("home_builder_doors_windows.place_open_door", "Open Doorway",
     _g_open_door, 1, 'draw_door_window_defaults', "Door & Window Settings"),
    ("home_builder_doors_windows.place_window", "Window", _g_window, 1,
     'draw_door_window_defaults', "Door & Window Settings"),
    ("home_builder_walls.add_floor", "Add Floor", _g_floor, 2, None, None),
    ("home_builder_walls.add_ceiling", "Add Ceiling", _g_ceiling, 2, None, None),
)

# Contributed tools. A downstream add-on may have room commands that
# belong on this strip, and this module must not depend on any of them.
# `supersedes` lets a contribution REPLACE a built-in rather than sit
# next to it -- otherwise a richer version of a command (a floor that
# also gets a material, say) would show up as a second button doing
# almost the same thing.
_extra_tools = []        # (order, key, entry, supersedes)


# Option forms contributed alongside a tool. `options` on a tool is a
# NAME, not a function, because it has to survive as an operator
# property -- so a contributor registers the draw function here under
# that name. Built-in tools name a function on the sidebar module
# instead; the popup checks this registry first.
_option_forms = {}       # name -> draw(layout, context)


def register_tool_options(name, draw_fn):
    _option_forms[name] = draw_fn


def unregister_tool_options(name):
    _option_forms.pop(name, None)


def register_tool(key, label, glyph, operator, group=3, options=None,
                  options_label=None, order=100, supersedes=None):
    """Add a tool button. `glyph` is a callable (shader, box, color).
    Re-registering a key replaces it."""
    unregister_tool(key)
    entry = (operator, label, glyph, group, options, options_label)
    _extra_tools.append((order, key, entry, supersedes))
    _extra_tools.sort(key=lambda t: (t[0], t[2][1]))


def unregister_tool(key):
    for i, tool in enumerate(list(_extra_tools)):
        if tool[1] == key:
            del _extra_tools[i]
            return


def tools():
    """The effective tool list: built-ins, minus anything a
    contribution supersedes, plus the contributions.

    Sorted by (group, order) so a contribution can land WHERE it
    belongs rather than merely after everything. Built-ins take an
    implicit order from their position, spaced so a contribution
    can be slotted between two of them.
    """
    replaced = {t[3] for t in _extra_tools if t[3]}
    out = [(t[3], i * 10, t) for i, t in enumerate(BUILTIN_TOOLS)
           if t[0] not in replaced]
    out.extend((t[2][3], t[0], t[2]) for t in _extra_tools)
    out.sort(key=lambda row: (row[0], row[1]))
    return tuple(row[2] for row in out)

CARET = 11              # unscaled; corner affordance on tools with options.
                        # Small, but the whole button also opens options
                        # on right-click, so this is the shortcut not the
                        # only way in.


# ---- Gating ----------------------------------------------------------------

def _get_prefs():
    try:
        return bpy.context.preferences.addons[_ADDON_PKG].preferences
    except (KeyError, AttributeError):
        return None


def palette_enabled():
    p = _get_prefs()
    return bool(p and getattr(p, "use_room_palette", False))


def show_labels():
    """Whether tools are named on the strip rather than only on hover.

    A glyph strip is fast once the marks are learned and opaque before
    then, which is the whole of a new user's first week. Labelling is a
    preference rather than a guess about who is looking.
    """
    p = _get_prefs()
    return bool(p and getattr(p, "palette_show_labels", False))


def is_room_scene(scene):
    """A 3D room scene -- not a 2D layout sheet or a detail card. Same
    test the scene navigator groups by."""
    if scene is None:
        return False
    return not scene.get('IS_LAYOUT_VIEW') and not scene.get('IS_DETAIL_VIEW')


def _palette_active(context):
    area = getattr(context, "area", None)
    if area is None or area.type != 'VIEW_3D':
        return False
    if _shutdown or not palette_enabled():
        return False
    return is_room_scene(context.scene)


# ---- Layout ----------------------------------------------------------------

def _clear_of_panel(area, x, gap):
    """Put the strip to the right of the open panel, always.

    Not only when the two would overlap: shifting conditionally means
    the tools jump sideways as the panel grows and shrinks, or as you
    switch to a shorter tab. The panel owns that corner whenever it is
    open, the tools sit beside it, and neither moves.
    """
    from . import viewport_hud
    nav = viewport_hud.pinned_panel_rect(bpy.context, area)
    if nav is None:
        return x
    return max(x, nav[0] + nav[2] + gap)


def button_width(s, labelled=None):
    """Button width: square for glyphs alone, or wide enough for the
    longest tool name when the strip is labelled.

    One width for every button, not each to its own label -- a ragged
    column of buttons reads as a list of unrelated things rather than
    one strip.
    """
    btn = BTN * s
    if labelled is None:
        labelled = show_labels()
    if not labelled:
        return btn
    widest = 0.0
    for tool in tools():
        widest = max(widest, text_width(0, FONT_SIZE * s, tool[1]))
    return btn + LABEL_TEXT_GAP * s + widest + LABEL_PAD_X * s


def compute_layout(area):
    """[(tool_index, rect)] top-down, in WINDOW-local pixels."""
    s = scale()
    x_min, _x_max, _y_min, y_max = get_visible_window_bounds(area)
    x = x_min + MARGIN_X * s
    y_top = y_max - TOP_OFFSET * s
    btn = BTN * s
    width = button_width(s)

    x = _clear_of_panel(area, x, MARGIN_X * s)

    y = y_top
    out = []
    last_group = None
    for i, (_op, _label, _glyph, group, _opts, _olbl) in enumerate(tools()):
        if last_group is not None:
            y -= (GROUP_GAP if group != last_group else BTN_GAP) * s
        last_group = group
        y -= btn
        out.append((i, (x, y, width, btn)))
    return out

def _hit(mx, my, layout):
    for index, rect in layout:
        if point_in_rect(mx, my, rect):
            return index
    return None


def _caret_rect(rect):
    """Bottom-right corner of a button: the options affordance."""
    s = scale()
    c = CARET * s
    x, y, w, _h = rect
    return (x + w - c, y, c, c)


def _hit_caret(mx, my, layout):
    """Index of the tool whose caret was clicked, or None."""
    for index, rect in layout:
        if tools()[index][4] is None:
            continue
        if point_in_rect(mx, my, _caret_rect(rect)):
            return index
    return None


# ---- Draw ------------------------------------------------------------------

def _draw():
    context = bpy.context
    if not _palette_active(context):
        return
    region = context.region
    hover = _hover
    if region is None or (_mouse_region is not None
                          and region != _mouse_region):
        hover = None

    s = scale()
    font_id = 0
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    layout = compute_layout(context.area)
    # Snapshot once: the list is rebuilt from the registry on every
    # call, and the indices in `layout` refer to this ordering.
    TOOLS_NOW = tools()
    labelled = show_labels()
    inset = GLYPH_INSET * s
    btn = BTN * s
    for index, rect in layout:
        hovered = index == hover
        # Brighter edge: this strip floats on the viewport, not
        # inside a panel, so it should announce itself.
        paint_button(shader, rect, hovered=hovered,
                     border=Theme.BTN_BORDER)
        x, y, w, h = rect
        # The glyph keeps its square regardless of how wide the button
        # grew, so a labelled strip and a bare one show the same marks.
        TOOLS_NOW[index][2](
            shader, (x + inset, y + inset, btn - inset * 2, h - inset * 2),
            Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
        if labelled:
            draw_text(font_id, x + btn + LABEL_TEXT_GAP * s,
                      y + h * 0.30, FONT_SIZE * s,
                      Theme.TEXT_PRIMARY if hovered else Theme.TEXT_NORMAL,
                      TOOLS_NOW[index][1])
        if TOOLS_NOW[index][4] is not None:
            # A small filled corner: this tool has settings behind it.
            cx, cy, cw, ch = _caret_rect(rect)
            draw_polyline(shader,
                          [(cx + cw, cy), (cx + cw, cy + ch), (cx, cy)],
                          Theme.GLYPH_HOVER if hovered else Theme.TEXT_DIM,
                          closed=True)

    # Name what is under the cursor, not what the button is: the corner
    # opens settings, so it should say so. On a labelled strip the tool's
    # own name is already written on it, so only the corner still has
    # something to add.
    label = None
    if hover is not None:
        caret_label = TOOLS_NOW[hover][5] if _hover_caret else None
        label = caret_label or (None if labelled else TOOLS_NOW[hover][1])
    if label:
        _, (bx, by, bw, bh) = layout[hover]
        lw = text_width(font_id, FONT_SIZE * s, label) + LABEL_PAD_X * s * 2
        lh = LABEL_HEIGHT * s
        lrect = (bx + bw + LABEL_GAP * s, by + (bh - lh) / 2.0, lw, lh)
        paint_frame(shader, lrect, Theme.PANEL_BG, Theme.PANEL_BORDER)
        draw_centered_text(font_id, lrect, FONT_SIZE * s,
                           Theme.TEXT_PRIMARY, label)

    gpu.state.blend_set('NONE')


# ---- Operators -------------------------------------------------------------

class home_builder_OT_room_palette_click(bpy.types.Operator):
    """Launch the room tool under the cursor. Passes through when the
    click isn't on a palette button"""
    bl_idname = "home_builder.room_palette_click"
    bl_label = "Room Palette Click"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _palette_active(context)

    def invoke(self, context, event):
        layout = compute_layout(context.area)
        mx, my = event.mouse_region_x, event.mouse_region_y
        # The caret is checked first: it sits inside the button, so a
        # hit there must not also fire the tool.
        index = _hit_caret(mx, my, layout)
        if index is None and event.type == 'RIGHTMOUSE':
            index = _hit(mx, my, layout)
            if index is not None and tools()[index][4] is None:
                return {'PASS_THROUGH'}
        if index is not None:
            bpy.ops.home_builder.tool_options(
                'INVOKE_DEFAULT', section=tools()[index][4],
                title=tools()[index][5])
            return {'FINISHED'}
        if event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}
        index = _hit(mx, my, layout)
        if index is None:
            return {'PASS_THROUGH'}
        mod, name = tools()[index][0].split(".", 1)
        try:
            getattr(getattr(bpy.ops, mod), name)('INVOKE_DEFAULT')
        except Exception as ex:
            self.report({'WARNING'}, str(ex))
        return {'FINISHED'}


class home_builder_OT_room_palette_hover(bpy.types.Operator):
    """Track the cursor so the palette can highlight and label the button
    under it. Always passes the event through"""
    bl_idname = "home_builder.room_palette_hover"
    bl_label = "Room Palette Hover"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _palette_active(context)

    def invoke(self, context, event):
        global _mouse_region, _hover, _hover_caret
        _mouse_region = context.region
        mx, my = event.mouse_region_x, event.mouse_region_y
        layout = compute_layout(context.area)
        hit = _hit(mx, my, layout)
        on_caret = _hit_caret(mx, my, layout) is not None
        if hit != _hover or on_caret != _hover_caret:
            _hover, _hover_caret = hit, on_caret
            context.area.tag_redraw()
        return {'PASS_THROUGH'}


class home_builder_OT_tool_options(bpy.types.Operator):
    """Settings for the tool under the cursor"""
    bl_idname = "home_builder.tool_options"
    bl_label = "Tool Options"

    section: bpy.props.StringProperty()  # type: ignore
    title: bpy.props.StringProperty()  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.title)
        fn = _option_forms.get(self.section)
        if fn is None:
            from ..ui import view3d_sidebar
            fn = getattr(view3d_sidebar, self.section, None)
        if fn is None:
            layout.label(text="These settings are unavailable.", icon='ERROR')
            return
        # The sidebar's own form, called verbatim -- see styles_panel for
        # why a GPU panel should not be reimplementing property rows.
        fn(layout, context)

    def execute(self, context):
        return {'FINISHED'}


classes = (
    home_builder_OT_tool_options,
    home_builder_OT_room_palette_click,
    home_builder_OT_room_palette_hover,
)


# ---- Lifecycle -------------------------------------------------------------

def tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        home_builder_OT_room_palette_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        home_builder_OT_room_palette_hover.bl_idname, 'MOUSEMOVE', 'ANY',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    # Right-click over a button opens that tool's settings; the
    # click operator passes through when it is not over one, so
    # the viewport context menu still works everywhere else.
    kmi = km.keymap_items.new(
        home_builder_OT_room_palette_click.bl_idname, 'RIGHTMOUSE',
        'PRESS', any=True, head=True)
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    global _draw_handle, _shutdown, _hover, _hover_caret
    _shutdown = False
    _hover = None
    _hover_caret = False
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    _register_keymaps()


def unregister():
    global _draw_handle, _shutdown, _hover, _hover_caret
    _shutdown = True
    _hover = None
    _hover_caret = False
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
