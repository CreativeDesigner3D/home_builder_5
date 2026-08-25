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
LABEL_TEXT_GAP = 4      # glyph to its name, on an expanded strip
HEADER_H = 15           # group caption row
HEADER_GAP = 3          # caption to the first tool under it
SETTINGS_MARK = 14      # settings affordance at the end of a tool row
SETTINGS_PAD = 7        # its inset from the row's right edge
FONT_HEADER = 9
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
_hover_settings = None   # options form under the cursor, if any
_hover_toggle = False    # cursor is on the compact/expanded toggle


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
    """Two leaves side by side, seen face on.

    The only mark here drawn in elevation rather than plan, and
    deliberately. In plan a double door is two quarter arcs, and at this
    size two arcs side by side are two humps: the mark read as the letter
    M however the leaves were sized or the wall was drawn. Tried and
    rejected: matched leaf and radius, hinges brought inboard onto a
    length of wall, leaves swung to 58 degrees, leaves folded into a
    cased opening. All of them stayed a pair of bumps.

    What separates this tool from Single Door is not the swing -- both
    swing -- it is that there are two leaves, so the mark shows the two
    leaves. Same reasoning as the other marks on this strip: draw what
    the tool makes.
    """
    x, y, w, h = box
    draw_polyline(shader, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                  color, closed=True)
    cx = x + w / 2.0
    draw_lines(shader, [(cx, y), (cx, y + h)], color)
    k = max(1.0, w * 0.09)
    draw_rect(shader, cx - w * 0.20 - k / 2.0, y + h * 0.46, k, k, color)
    draw_rect(shader, cx + w * 0.20 - k / 2.0, y + h * 0.46, k, k, color)


def _g_open_door(shader, box, color):
    """A cased opening: the wall broken, jambs returned, no leaf.

    What makes an opening an opening is the ABSENCE of a swing, so the
    wall has to be legible for the gap in it to mean anything. Two bare
    jamb lines -- which is what this was -- carry no wall, and read as
    two unrelated strokes.
    """
    x, y, w, h = box
    mid = y + h * 0.5
    t = h * 0.17                        # half the wall thickness
    gap0, gap1 = x + w * 0.34, x + w * 0.66
    for x0, x1 in ((x, gap0), (gap1, x + w)):
        draw_lines(shader, [(x0, mid - t), (x1, mid - t),
                            (x0, mid + t), (x1, mid + t)], color)
    draw_lines(shader, [(gap0, mid - t), (gap0, mid + t),
                        (gap1, mid - t), (gap1, mid + t)], color)


def _g_window(shader, box, color):
    """Wall band with the glazing line through it."""
    x, y, w, h = box
    top = y + h * 0.72
    bot = y + h * 0.28
    draw_lines(shader, [(x, bot), (x + w, bot), (x, top), (x + w, top)], color)
    draw_lines(shader, [(x, (top + bot) / 2.0), (x + w, (top + bot) / 2.0)],
               color)
    draw_lines(shader, [(x, bot), (x, top), (x + w, bot), (x + w, top)], color)


# Floor and ceiling are the same thing at opposite ends of a room, and
# the marks used to say so too literally: one box hatched along its
# bottom edge, one hatched along its top, indistinguishable at a glance
# and neither reading as a horizontal surface. They are now a plane in
# perspective -- and the two differ twice over, in where the plane sits
# in the button and in which way the trapezoid tapers, because a floor is
# seen from above and a ceiling from below.

# Floor and ceiling are one slab drawn twice, and the pair has to be
# told apart at a glance. They used to be a box hatched along its bottom
# edge and the same box hatched along its top -- indistinguishable, and
# neither reading as a surface. A slab in section does read: a band with
# structure hatched off the far side of it, low and hatched below for a
# floor, high and hatched above for a ceiling. Two cues, not one.
#
# Also tried: the slab as a plane in perspective. A floor seen from above
# and a ceiling seen from below recede the same way, so the shape came
# out identical and only position separated them; adding walls to say
# which side the room was on made a cluttered blob of one and a table of
# the other.

def _slab(shader, box, low, up, color):
    """A slab band with structure hatched off one face."""
    x, y, w, h = box
    lo = y + h * low
    hi = lo + h * 0.20
    draw_lines(shader, [(x, lo), (x + w, lo), (x, hi), (x + w, hi)], color)
    face = hi if up else lo
    step = h * 0.26 * (1.0 if up else -1.0)
    for i in range(4):
        fx = x + w * (0.10 + 0.25 * i)
        draw_lines(shader, [(fx, face), (fx - w * 0.16, face + step)], color)


def _g_floor(shader, box, color):
    """A floor slab in section, hatched below."""
    _slab(shader, box, 0.34, False, color)


def _g_ceiling(shader, box, color):
    """The same slab high in the button, hatched above."""
    _slab(shader, box, 0.46, True, color)


def _g_measure(shader, box, color):
    """A dimension line: what the tool leaves on screen.

    Not a tape-measure case -- a curled tape needs a spiral and a body to
    be recognisable, and both turn to mush at this size, the same way the
    gear's teeth did. Two witness lines and an arrowed span between them
    survive the shrink and say the same thing.
    """
    x, y, w, h = box
    top = y + h
    mid = y + h * 0.42
    # Witness lines run down past the span and stop, the way an extension
    # line crosses a dimension line on a drawing.
    draw_lines(shader, [(x, mid - h * 0.14), (x, top),
                        (x + w, mid - h * 0.14), (x + w, top)], color)
    draw_lines(shader, [(x, mid), (x + w, mid)], color)
    # Slashes, not arrowheads. A two-line barb collapses into a pair of
    # stray pixels at the size this is actually drawn -- and a tick is
    # how the add-on dimensions a drawing anyway.
    tick = min(w, h) * 0.22
    for cx in (x, x + w):
        draw_lines(shader, [(cx - tick, mid - tick), (cx + tick, mid + tick)],
                   color)


def _g_stairs(shader, box, color):
    """A flight in section: three risers and their treads.

    The stepped line is the whole mark. Three steps rather than a truer
    count because at this size the treads have to stay wide enough to
    read as treads -- more of them closes the line into a diagonal.
    """
    x, y, w, h = box
    steps = 3
    tread = w / float(steps)
    rise = h / float(steps)
    pts = [(x, y)]
    for i in range(steps):
        pts.append((x + tread * i, y + rise * (i + 1)))
        pts.append((x + tread * (i + 1), y + rise * (i + 1)))
    draw_polyline(shader, pts, color)


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
    # Named for the thing, not the act: every button on the strip adds
    # something, so "Add" on three of them is a word the eye has to read
    # past to get to what differs. The group reads Floor / Ceiling /
    # Stairs down the column.
    ("home_builder_walls.add_floor", "Floor", _g_floor, 2, None, None),
    ("home_builder_walls.add_ceiling", "Ceiling", _g_ceiling, 2, None, None),
    ("home_builder_stairs.place_stairs", "Stairs", _g_stairs, 2, None, None),
    # Group 4, not 3: a downstream add-on has claimed 3 for its own run,
    # and measuring belongs at the end of the strip anyway -- it is the
    # one tool here that adds nothing to the room.
    ("home_builder.measure", "Measure", _g_measure, 4,
     'measure_options', "Measure Settings"),
)

# Group captions, shown only in expanded mode. A group is just an int on
# a tool -- it controls the gap in compact mode and needs a name to head
# it in expanded mode. A contributor that owns a group can name it;
# unnamed groups head with nothing rather than a number.
_group_labels = {
    0: "Walls",
    1: "Doors & Windows",
    2: "Room",
    4: "Measure",
}


def register_group_label(group, label):
    _group_labels[group] = label


def unregister_group_label(group):
    _group_labels.pop(group, None)


def group_label(group):
    return _group_labels.get(group)


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


# Count badges. A tool whose command leaves something behind needs to say
# so while it is NOT running -- otherwise the only evidence sits in the
# viewport with no clue as to what put it there or how to be rid of it.
# The provider is a callable taking the scene and returning a count; zero
# or None draws nothing.
_tool_badges = {}        # operator -> callable(scene) -> int | None


def register_tool_badge(operator, count_fn):
    _tool_badges[operator] = count_fn


def unregister_tool_badge(operator):
    _tool_badges.pop(operator, None)


def tool_badge(operator, scene):
    provider = _tool_badges.get(operator)
    if provider is None:
        return None
    try:
        count = provider(scene)
    except Exception:
        return None
    return count if count else None


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


def _g_settings(shader, box, color):
    """Two sliders -- the mark for "there are settings behind this".

    Sliders rather than a gear: a gear is teeth around a ring, and at
    fourteen pixels the teeth close up into a blob. Two rules with a
    knob on each survive the size, and say adjustable besides.
    """
    x, y, w, h = box
    for row, knob in ((0.34, 0.62), (0.66, 0.34)):
        ly = y + h * row
        draw_lines(shader, [(x, ly), (x + w, ly)], color)
        kx = x + w * knob
        draw_rect(shader, kx - w * 0.09, ly - h * 0.13,
                  w * 0.18, h * 0.26, color)


def _g_expand(shader, box, color):
    """A double chevron: pointing right to open the strip out, left to
    fold it back. The direction is the direction the strip will move."""
    x, y, w, h = box
    opening = not expanded()
    cy = y + h / 2.0
    span = w * 0.30
    for i in (0, 1):
        ox = x + w * (0.22 + i * 0.34)
        if opening:
            draw_polyline(shader, [(ox, cy + span), (ox + span, cy),
                                   (ox, cy - span)], color)
        else:
            draw_polyline(shader, [(ox + span, cy + span), (ox, cy),
                                   (ox + span, cy - span)], color)


# ---- Gating ----------------------------------------------------------------

def _get_prefs():
    try:
        return bpy.context.preferences.addons[_ADDON_PKG].preferences
    except (KeyError, AttributeError):
        return None


def palette_enabled():
    p = _get_prefs()
    return bool(p and getattr(p, "use_room_palette", False))


def expanded():
    """Whether the strip is in expanded mode.

    Compact is a column of glyphs: fast once the marks are learned, and
    opaque before then -- which is the whole of a new user's first week.
    Expanded names every tool, heads each group with a caption, and
    gives a tool's settings a row of their own instead of an 11px
    corner nobody can hit on purpose. Which one suits is about who is
    looking, so it is a preference rather than a guess.
    """
    p = _get_prefs()
    return bool(p and getattr(p, "palette_expanded", False))



def set_expanded(value):
    """Write the expanded preference. Used by the strip's own toggle, so
    the mode can be changed from the thing it changes rather than only
    from the add-on preferences.

    Guarded: this runs from a click handler, and a preferences class
    without the property (an add-on mid-upgrade, a reload that has not
    re-registered yet) must leave the click harmless rather than raise
    into the event loop.
    """
    p = _get_prefs()
    if p is None:
        return False
    try:
        p.palette_expanded = bool(value)
    except AttributeError:
        return False
    return True


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


def button_width(s, is_expanded=None):
    """Strip width: square for glyphs alone, or wide enough for the
    longest thing the expanded strip has to write.

    One width for the whole strip, not each row to its own label -- a
    ragged column reads as a list of unrelated things rather than one
    tool set.
    """
    btn = BTN * s
    if is_expanded is None:
        is_expanded = expanded()
    if not is_expanded:
        return btn
    now = tools()
    widest = 0.0
    for tool in now:
        widest = max(widest, text_width(0, FONT_SIZE * s, tool[1]))
    for group in {t[3] for t in now}:
        caption = group_label(group)
        if caption:
            widest = max(widest, text_width(0, FONT_HEADER * s, caption))
    # Room at the end for the settings mark, so the longest label cannot
    # run into it.
    return (btn + LABEL_TEXT_GAP * s + widest
            + (LABEL_PAD_X + SETTINGS_MARK + SETTINGS_PAD) * s)


def compute_layout(area):
    """Rows top-down, in WINDOW-local pixels.

    [(kind, payload, rect)] where kind is:
        'tool'     payload = index into tools()
        'header'   payload = the group caption (never hit-tested)

    Settings have no row of their own in either mode -- they are a mark
    inside the row of the tool they belong to (see _settings_rect), so
    the strip is a list of tools and nothing else.
    """
    s = scale()
    x_min, _x_max, _y_min, y_max = get_visible_window_bounds(area)
    x = x_min + MARGIN_X * s
    y_top = y_max - TOP_OFFSET * s
    btn = BTN * s
    is_expanded = expanded()
    width = button_width(s, is_expanded)

    x = _clear_of_panel(area, x, MARGIN_X * s)

    now = tools()
    out = []
    y = y_top

    # The mode toggle heads the strip. It is the one control that is
    # about the tool bar rather than about the room, so it sits apart
    # from the groups, above all of them.
    y -= btn
    out.append(('toggle', is_expanded, (x, y, width, btn)))
    y -= GROUP_GAP * s

    last_group = None
    for i, tool in enumerate(now):
        group = tool[3]
        new_group = group != last_group
        if last_group is not None:
            y -= (GROUP_GAP if new_group else BTN_GAP) * s
        if is_expanded and new_group:
            caption = group_label(group)
            if caption:
                y -= HEADER_H * s
                out.append(('header', caption, (x, y, width, HEADER_H * s)))
                y -= HEADER_GAP * s
        last_group = group
        y -= btn
        out.append(('tool', i, (x, y, width, btn)))
    return out


def _hit_toggle(mx, my, layout):
    for kind, _payload, rect in layout:
        if kind == 'toggle' and point_in_rect(mx, my, rect):
            return True
    return False


def _rows(layout, kind):
    return [(payload, rect) for k, payload, rect in layout if k == kind]


def _hit(mx, my, layout):
    """Index of the tool under the cursor, or None."""
    for kind, payload, rect in layout:
        if kind == 'tool' and point_in_rect(mx, my, rect):
            return payload
    return None


def _hit_settings(mx, my, layout):
    """(options_name, options_label) under the cursor, or None.

    One question for the click operator to ask, in either mode: the
    affordance always lives inside a tool row, so this walks the tool
    rows and asks each one where its mark is.
    """
    for kind, payload, rect in layout:
        if kind != 'tool':
            continue
        tool = tools()[payload]
        if tool[4] is None:
            continue
        if point_in_rect(mx, my, _settings_rect(rect)):
            return (tool[4], tool[5])
    return None


BADGE_H = 13            # unscaled; count plate on a tool that left something
BADGE_FONT = 9


def _draw_badge(shader, font_id, rect, count, s):
    """Count plate on the top-right of a button.

    Top-right because the settings affordance already owns the bottom-right
    corner in compact mode, and the two must never land on each other.
    """
    x, y, w, h = rect
    text = str(count) if count < 100 else "99+"
    size = BADGE_FONT * s
    bh = BADGE_H * s
    bw = max(bh, text_width(font_id, size, text) + 6 * s)
    bx = x + w - bw * 0.6
    by = y + h - bh * 0.6
    draw_rect(shader, bx, by, bw, bh, Theme.ACCENT_BG)
    draw_centered_text(font_id, (bx, by, bw, bh), size,
                       Theme.TEXT_PRIMARY, text)


def _settings_rect(rect):
    """Where a tool row keeps its settings affordance.

    Compact has only the button's own square to work with, so the mark
    is a corner of it. Expanded has a row, so the mark sits at the end
    of it, clear of the label and big enough to hit.
    """
    s = scale()
    x, y, w, h = rect
    if not expanded():
        c = CARET * s
        return (x + w - c, y, c, c)
    m = SETTINGS_MARK * s
    return (x + w - m - SETTINGS_PAD * s, y + (h - m) / 2.0, m, m)



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
    is_expanded = expanded()
    inset = GLYPH_INSET * s
    btn = BTN * s
    hover_rect = None

    for kind, payload, rect in layout:
        x, y, w, h = rect
        if kind == 'toggle':
            hovered = _hover_toggle
            paint_button(shader, rect, hovered=hovered,
                         border=Theme.BTN_BORDER)
            _g_expand(shader,
                      (x + inset, y + inset, btn - inset * 2, h - inset * 2),
                      Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
            if payload:
                draw_text(font_id, x + btn + LABEL_TEXT_GAP * s,
                          y + h * 0.30, FONT_SIZE * s,
                          Theme.TEXT_PRIMARY if hovered else Theme.TEXT_DIM,
                          "Collapse")
            if hovered:
                hover_rect = rect
            continue
        if kind == 'header':
            # A caption, not a control: no frame, and dimmer than the
            # tools, so the eye goes to what it can actually press.
            draw_text(font_id, x + 2 * s, y + h * 0.25, FONT_HEADER * s,
                      Theme.TEXT_HEADER, payload.upper())
            continue

        index = payload
        hovered = index == hover
        # Brighter edge: this strip floats on the viewport, not
        # inside a panel, so it should announce itself.
        paint_button(shader, rect, hovered=hovered,
                     border=Theme.BTN_BORDER)
        # The glyph keeps its square regardless of how wide the button
        # grew, so both modes show the same marks in the same place.
        TOOLS_NOW[index][2](
            shader, (x + inset, y + inset, btn - inset * 2, h - inset * 2),
            Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
        if is_expanded:
            draw_text(font_id, x + btn + LABEL_TEXT_GAP * s,
                      y + h * 0.30, FONT_SIZE * s,
                      Theme.TEXT_PRIMARY if hovered else Theme.TEXT_NORMAL,
                      TOOLS_NOW[index][1])
        if TOOLS_NOW[index][4] is not None:
            # Settings live on the tool's own row in both modes. Groups
            # that share one form (the four door and window tools) show
            # the mark on each of them: it is the same form four times,
            # but it is where the tool is, which is where it is looked
            # for -- and the two modes then behave alike.
            on_mark = hovered and _hover_caret
            mark = Theme.GLYPH_HOVER if on_mark else (
                Theme.GLYPH if hovered else Theme.TEXT_DIM)
            mx_, my_, mw_, mh_ = _settings_rect(rect)
            if is_expanded:
                _g_settings(shader, (mx_, my_, mw_, mh_), mark)
            else:
                # Compact: a filled corner of the button, because there
                # is no room beside the glyph for anything more.
                draw_polyline(shader,
                              [(mx_ + mw_, my_), (mx_ + mw_, my_ + mh_),
                               (mx_, my_)], mark, closed=True)
        badge = tool_badge(TOOLS_NOW[index][0], context.scene)
        if badge is not None:
            _draw_badge(shader, font_id, rect, badge, s)
        if hovered:
            hover_rect = rect

    # The hover chip names what is under the cursor. Expanded mode has
    # written every tool name on the strip already, so it needs a chip
    # only over the settings mark -- which opens something the row does
    # not name. Compact needs one for the tool as well.
    label = None
    on_mark = hover is not None and _hover_caret and TOOLS_NOW[hover][5]
    if not is_expanded and _hover_toggle:
        label = "Expand Tool Bar"
    elif on_mark:
        label = TOOLS_NOW[hover][5]
    elif not is_expanded and hover is not None:
        label = TOOLS_NOW[hover][1]
    if label and hover_rect is not None:
        bx, by, bw, bh = hover_rect
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
        # Settings first: in compact mode the caret sits INSIDE a tool
        # button, so a hit there must not also fire the tool.
        if _hit_toggle(mx, my, layout):
            if event.type == 'RIGHTMOUSE':
                return {'PASS_THROUGH'}
            set_expanded(not expanded())
            context.area.tag_redraw()
            return {'FINISHED'}
        settings = _hit_settings(mx, my, layout)
        if settings is None and event.type == 'RIGHTMOUSE':
            # Right-clicking a tool still opens its settings, which is
            # the forgiving way in when the strip is compact and the
            # corner is an 11px target.
            index = _hit(mx, my, layout)
            if index is not None and tools()[index][4] is not None:
                settings = (tools()[index][4], tools()[index][5])
        if settings is not None:
            bpy.ops.home_builder.tool_options(
                'INVOKE_DEFAULT', section=settings[0], title=settings[1])
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
        global _mouse_region, _hover, _hover_caret, _hover_settings
        global _hover_toggle
        _mouse_region = context.region
        mx, my = event.mouse_region_x, event.mouse_region_y
        layout = compute_layout(context.area)
        hit = _hit(mx, my, layout)
        settings = _hit_settings(mx, my, layout)
        toggle = _hit_toggle(mx, my, layout)
        # The settings mark always sits inside a tool row, so a
        # settings hit means the cursor is on the mark rather than on
        # the rest of the button.
        on_caret = settings is not None and hit is not None
        name = settings[0] if settings is not None else None
        if ((hit, on_caret, name, toggle)
                != (_hover, _hover_caret, _hover_settings, _hover_toggle)):
            (_hover, _hover_caret, _hover_settings,
             _hover_toggle) = hit, on_caret, name, toggle
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
        # The sidebar's own form, called verbatim -- see options_panel for
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
