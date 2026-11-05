"""The selection inspector: the settings of what is picked, in a box
of their own on the right of the viewport.

It sits apart from the panel at the top left, so the library (or any
other tab) can stay open there while the picked cabinet's settings
show on the right. A user can put it where it suits the way they work:

* **Docked right** (the default) -- down the right side, under the
  viewport controls and beside the navigation gizmo.
* **Floating** -- wherever its header was dragged to. Dropped near the
  right side it docks there again.

It used to go back on the panel's SELECTED tab too, but there it took
the panel over at every pick, turning it away from the library or the
drawings it was on; a layout saved that way now opens docked right.

Its header carries the commands: drag it by the title (a click on the
title, without dragging, folds it to just the header and back), fold it
with the chevron, and dock it again with the bar. Each button names
itself on hover. Where it is, and whether it is folded, is remembered for the
user rather than the file, so everyone keeps their own layout and
nobody else's changes.

It shows only while something with a page is picked; the page is
``selected_tab._blocks``, laid out by the Options tab's widgets.

Like the rest of the HUD it adds no persistent modal operator: the
viewport HUD's keymap operators route presses, hover and the wheel to
it, and a drag lives only from press to release.
"""

import json
import os

import bpy
import gpu

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    navigation_gizmo_reserve,
    draw_rect,
    draw_lines,
    draw_text,
    vcenter_baseline,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    scale as _s,
    paint_frame,
    paint_button,
    glyph_chevron,
    fit_text,
    semibold_font,
    text_width,
)


MODE_PANEL = 'PANEL'        # retired: was the panel's SELECTED tab
MODE_RIGHT = 'RIGHT'        # docked down the right side (the default)
MODE_FLOAT = 'FLOAT'        # wherever it was dragged

# ---- Layout (unscaled px; every one is multiplied by _s() at use) ----------
WIDTH = 280                 # as the SELECTED tab
HEADER_H = 24
PAD = 8
MARGIN = 8
BTN = 18                    # header button
BTN_GAP = 4
TITLE_FONT = 11
# Below the HUD's top row of buttons: how far down it reaches is read
# from the HUD (_top_reserve); this is the gap left under it.
TOP_GAP = 8
# Clear of the corner icons drawn at the bottom right of the viewport.
BOTTOM_RESERVE = 44
# How near the docked spot a dropped box has to land to dock again. Small,
# so a box nudged a little way off the dock stays where it was put.
SNAP = 16
# A page that draws itself asks for this much height, less where the
# viewport is shorter; it scrolls within what it gets.
PROVIDER_H = 620

_STATE_FILE = 'selection_inspector.json'

_state = None               # {'mode', 'collapsed', 'float': [x_frac, top_px]}
_list = None
_drag = None                # (grab dx, grab dy) while the header is held


# ---- Remembered placement ----------------------------------------------------

def _state_path(create=False):
    from . import options_panel
    path = options_panel._state_path(create=create)
    return os.path.join(os.path.dirname(path), _STATE_FILE) if path else None


def _load():
    global _state
    if _state is None:
        _state = {'mode': MODE_RIGHT, 'collapsed': False, 'float': None}
        try:
            with open(_state_path(), encoding='utf-8') as fh:
                saved = json.load(fh)
            if saved.get('mode') in (MODE_RIGHT, MODE_FLOAT):
                _state['mode'] = saved['mode']
            _state['collapsed'] = bool(saved.get('collapsed', False))
            pos = saved.get('float')
            if isinstance(pos, list) and len(pos) == 2:
                _state['float'] = [float(pos[0]), float(pos[1])]
        except Exception:
            pass            # no file yet, or one that cannot be read
    return _state


def _save():
    try:
        with open(_state_path(create=True), 'w', encoding='utf-8') as fh:
            json.dump(_load(), fh, indent=1)
    except Exception as ex:
        print('Home Builder: could not save the inspector layout: %s' % ex)


def mode():
    return _load()['mode']


def detached():
    """Whether the page is drawn here rather than on the panel's tab."""
    return mode() != MODE_PANEL


def collapsed():
    return _load()['collapsed']


def set_mode(new_mode):
    if new_mode == MODE_PANEL:
        new_mode = MODE_RIGHT
    state = _load()
    if new_mode == state['mode']:
        return
    state['mode'] = new_mode
    _save()
    _tag()


def toggle_collapsed():
    state = _load()
    state['collapsed'] = not state['collapsed']
    _save()
    _tag()


# ---- Layout -------------------------------------------------------------------

def _scroll_list():
    global _list
    if _list is None:
        from . import options_panel
        _list = options_panel.new_scroll_list()
    return _list


def _hud_on():
    from . import viewport_hud
    return viewport_hud.enabled()


def showing(context):
    if not detached() or not _hud_on():
        return False
    from . import selected_tab
    return selected_tab.has_selection(context)


def _top_reserve():
    """Unscaled px from the top the HUD's top row takes: its margin, the
    groups' headings, a button and the bar round it."""
    from . import viewport_hud as hud
    return (hud.HUD_MARGIN_Y + hud.CAPTION_H + hud.BTN_HEIGHT
            + hud.GROUP_PAD + TOP_GAP)


def _limits(area):
    """(x_min, x_max, bottom, top) the box has to stay inside."""
    s = _s()
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    return (x_min + MARGIN * s, x_max - MARGIN * s,
            y_min + BOTTOM_RESERVE * s, y_max - _top_reserve() * s)


def _docked_xy(area, w):
    """(x, top) of the box docked right: beside the navigation gizmo,
    under the row of viewport controls."""
    x_lo, x_hi, _bottom, top = _limits(area)
    gizmo_w = navigation_gizmo_reserve(area)[0]
    return max(x_lo, x_hi - gizmo_w - w), top


def _float_xy(area, w):
    x_lo, x_hi, bottom, top = _limits(area)
    pos = _load().get('float')
    if not pos:
        return _docked_xy(area, w)
    span = max(x_hi - x_lo - w, 0.0)
    x = x_lo + span * min(max(pos[0], 0.0), 1.0)
    y = top - pos[1] * _s()
    return x, min(max(y, bottom + HEADER_H * _s()), top)


def _page_blocks(context):
    """The SELECTED page without its title row: the header already
    names what is picked."""
    from . import selected_tab
    blocks = selected_tab._blocks(context)
    if blocks and blocks[0][0] == 'head':
        blocks = blocks[1:]
    return blocks


def _title(context, provider=None):
    from . import selected_tab
    if provider is not None:
        try:
            return str(provider.title(context))
        except Exception:
            return "Selected"
    blocks = selected_tab._blocks(context)
    for block in blocks:
        if block[0] == 'head':
            return str(block[1][0])
    return "Selected"


CRUMB_SEP = "  \u203a  "


def _crumb_rects(context, header, right):
    """[(text, rect, action)] for the title's breadcrumb, laid left to
    right in the header; separators are drawn between them. Steps that
    do not fit drop off the front behind an ellipsis, so the pick
    itself always shows. None when the page has no crumbs."""
    from . import selected_tab
    crumbs = selected_tab.crumbs(context)
    if not crumbs:
        return None
    s = _s()
    font_id = semibold_font()
    size = TITLE_FONT * s
    hx, hy, _hw, hh = header
    x0 = hx + PAD * s
    room = right - x0 - PAD * s
    sep_w = text_width(font_id, size, CRUMB_SEP)
    widths = [text_width(font_id, size, t.upper()) for t, _a in crumbs]
    first = 0
    lead = 0.0
    while first < len(crumbs) - 1 and (
            sum(widths[first:]) + sep_w * (len(crumbs) - first - 1) + lead > room):
        first += 1
        lead = text_width(font_id, size, "\u2026") + sep_w
    out = []
    x = x0 + lead
    for i in range(first, len(crumbs)):
        text, action = crumbs[i]
        w = min(widths[i], max(0.0, x0 + room - x))
        out.append((text, (x, hy, w, hh), action))
        x += w + sep_w
    return out, first > 0


def layout(context, area, region):
    """The box and what is in it, or None when it is not showing:
    {'rect', 'header', 'title', 'buttons': [(action, rect)], 'body',
    'entries'}. Shared by draw and hit-testing so they cannot drift."""
    if area is None or region is None or not showing(context):
        return None
    from . import options_panel, selected_tab
    s = _s()
    w = WIDTH * s
    header_h = HEADER_H * s
    pad = PAD * s
    # A page that draws itself (an appliance's panel run) instead of
    # blocks: it fills the room it is given, and scrolls within it.
    provider = selected_tab.page_provider(context)
    blocks = [] if provider is not None else _page_blocks(context)
    folded = collapsed()

    if mode() == MODE_FLOAT:
        x, top = _float_xy(area, w)
    else:
        x, top = _docked_xy(area, w)
    _x_lo, _x_hi, bottom, _top = _limits(area)

    if folded:
        h = header_h
    else:
        if provider is not None:
            content_h = PROVIDER_H * s
        else:
            content_h = sum(options_panel._block_h(b, s) for b in blocks)
        h = header_h + content_h + pad * 2
        h = min(h, top - bottom)
    h = max(h, header_h)
    rect = (x, top - h, w, h)
    header = (x, top - header_h, w, header_h)

    # Header buttons, right to left: fold, then dock when floating.
    bsz = BTN * s
    by = top - header_h + (header_h - bsz) / 2.0
    bx = x + w - pad / 2.0 - bsz
    buttons = [('collapse', (bx, by, bsz, bsz))]
    if mode() == MODE_FLOAT:
        bx -= bsz + BTN_GAP * s
        buttons.append(('dock', (bx, by, bsz, bsz)))

    entries = []
    body = None
    if not folded:
        body = (x + pad, rect[1] + pad, w - pad * 2, h - header_h - pad * 2)
        try:
            if provider is not None:
                entries = provider.build(body, context)
            else:
                entries = options_panel.build_page(
                    body, context, _page_blocks, _scroll_list())
        except Exception as ex:
            print('Home Builder: the inspector failed to build: %s' % ex)
    return {'rect': rect, 'header': header,
            'title': _title(context, provider),
            'buttons': buttons, 'body': body, 'entries': entries,
            'title_right': bx, 'provider': provider,
            'crumbs': (None if provider is not None
                       else _crumb_rects(context, header, bx))}


def rect(context, area):
    """The box's rect in WINDOW-region px, or None -- for overlays that
    keep clear of the HUD."""
    if area is None:
        return None
    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    lay = layout(context, area, region)
    return lay['rect'] if lay else None


# ---- Drawing ------------------------------------------------------------------

_TIPS = {
    'dock': "Dock on the right",
}


def _tip(action):
    if action == 'collapse':
        return "Unfold" if collapsed() else "Fold"
    return _TIPS.get(action, "")


def _paint_glyph(shader, action, rect, color):
    x, y, w, h = rect
    cx, cy = x + w / 2.0, y + h / 2.0
    size = w * 0.5
    if action == 'collapse':
        if collapsed():
            # Points down: the page unfolds below.
            glyph_chevron(shader, cx, cy, size, False, color)
        else:
            # Points up: the page folds up into the header.
            half = size / 2.0
            draw_lines(shader, [(cx - half, cy - half / 2.0), (cx, cy + half / 2.0),
                                (cx, cy + half / 2.0), (cx + half, cy - half / 2.0)],
                       color)
    elif action == 'dock':
        # A bar at the right edge with a chevron pointing at it.
        glyph_chevron(shader, cx - size * 0.15, cy, size, True, color)
        draw_rect(shader, x + w * 0.72, y + h * 0.22, 1.5 * _s(),
                  h * 0.56, color)


def draw(context, area, region, mx, my):
    lay = layout(context, area, region)
    if lay is None:
        return
    from . import options_panel
    s = _s()
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    paint_frame(shader, lay['rect'])
    hx, hy, hw, hh = lay['header']
    from ..hb_gpu_draw import draw_round_rect
    from ..hb_gpu_ui import FRAME_RADIUS
    draw_round_rect(shader, hx + 1, hy, hw - 2, hh - 1, (FRAME_RADIUS - 1) * s,
                    Theme.NEUTRAL_BG,
                    corners=(True, True, not lay['body'], not lay['body']))
    for action, brect in lay['buttons']:
        hovered = point_in_rect(mx, my, brect)
        paint_button(shader, brect, hovered=hovered)
        _paint_glyph(shader, action, brect,
                     Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
    font_id = semibold_font()
    size = TITLE_FONT * s
    baseline = vcenter_baseline(lay['header'], font_id, size)
    if lay['crumbs']:
        # Where the pick sits: each step above it a click that selects
        # it, the pick itself bright at the end.
        crumbs, cut = lay['crumbs']
        sep_w = text_width(font_id, size, CRUMB_SEP)
        if cut:
            x0 = crumbs[0][1][0] - sep_w - text_width(font_id, size, "\u2026")
            draw_text(font_id, x0, baseline, size, Theme.TEXT_DIM, "\u2026")
            draw_text(font_id, crumbs[0][1][0] - sep_w, baseline, size,
                      Theme.TEXT_DIM, CRUMB_SEP)
        for i, (text, crect, action) in enumerate(crumbs):
            cx, cy, cw, ch = crect
            hot = action is not None and point_in_rect(mx, my, crect)
            color = (Theme.TEXT_PRIMARY if action is None or hot
                     else Theme.TEXT_DIM)
            draw_text(font_id, cx, baseline, size, color,
                      fit_text(font_id, size, text.upper(), cw))
            if hot:
                draw_rect(shader, cx, baseline - 3 * s, cw, 1 * s, color)
            if i < len(crumbs) - 1:
                draw_text(font_id, cx + cw, baseline, size, Theme.TEXT_DIM,
                          CRUMB_SEP)
    else:
        tx = hx + PAD * s
        room = lay['title_right'] - tx - PAD * s
        title = fit_text(font_id, size, lay['title'].upper(), room)
        draw_text(font_id, tx, baseline, size, Theme.TEXT_PRIMARY, title)
    gpu.state.blend_set('NONE')
    if lay['entries']:
        (lay['provider'] or options_panel).paint(lay['entries'], mx, my)
    # Name the header button under the cursor, after the page so the
    # chip sits over it.
    for action, brect in lay['buttons']:
        if point_in_rect(mx, my, brect):
            from . import viewport_hud
            gpu.state.blend_set('ALPHA')
            shader.bind()
            viewport_hud._draw_hover_chip(shader, 0, brect, area, _tip(action))
            gpu.state.blend_set('NONE')
            break


# ---- Input --------------------------------------------------------------------

def hit(context, area, region, mx, my):
    """Take a press. None when it is not on the box; 'drag' when it is
    on the header (the caller starts the drag); True otherwise -- a
    press anywhere on the box is the box's, even on empty space."""
    lay = layout(context, area, region)
    if lay is None or not point_in_rect(mx, my, lay['rect']):
        return None
    for action, brect in lay['buttons']:
        if point_in_rect(mx, my, brect):
            if action == 'collapse':
                toggle_collapsed()
            elif action == 'dock':
                set_mode(MODE_RIGHT)
            return True
    for _text, crect, action in (lay['crumbs'] or ((),))[0]:
        if action is not None and point_in_rect(mx, my, crect):
            op_id, kwargs = action
            ns, name = op_id.split('.')
            try:
                getattr(getattr(bpy.ops, ns), name)(**kwargs)
            except Exception as ex:
                print('Home Builder: %s failed: %s' % (op_id, ex))
            _tag()
            return True
    if point_in_rect(mx, my, lay['header']):
        return 'drag'
    if lay['entries']:
        from . import options_panel
        (lay['provider'] or options_panel).hit(context, mx, my, lay['entries'])
    _tag()
    return True


def scroll(context, area, region, mx, my, rows):
    lay = layout(context, area, region)
    if lay is None or not point_in_rect(mx, my, lay['rect']):
        return False
    if lay['entries']:
        if lay['provider'] is not None:
            lay['provider'].scroll(mx, my, lay['entries'], rows)
        else:
            from . import options_panel
            options_panel.scroll_page(mx, my, lay['entries'], rows,
                                      _scroll_list())
    return True             # the wheel over the box never zooms the view


def begin_drag(context, area, region, mx, my):
    global _drag
    lay = layout(context, area, region)
    if lay is None:
        return False
    x, y, w, h = lay['rect']
    _drag = (mx - x, (y + h) - my)
    return True


def drag_to(context, area, mx, my):
    """Follow the cursor, kept on screen. While held it floats."""
    if _drag is None:
        return
    s = _s()
    state = _load()
    w = WIDTH * s
    x_lo, x_hi, bottom, top = _limits(area)
    x = min(max(mx - _drag[0], x_lo), max(x_hi - w, x_lo))
    t = min(max(my + _drag[1], bottom + HEADER_H * s), top)
    span = max(x_hi - x_lo - w, 0.0)
    state['mode'] = MODE_FLOAT
    state['float'] = [((x - x_lo) / span) if span > 0 else 0.0,
                      (top - t) / s]
    _tag()


def end_drag(context, area, cancelled=False):
    """Drop it: near the docked spot it docks, anywhere else it stays
    where it was let go."""
    global _drag
    _drag = None
    state = _load()
    if not cancelled and state['mode'] == MODE_FLOAT:
        s = _s()
        w = WIDTH * s
        dx, dtop = _docked_xy(area, w)
        fx, ftop = _float_xy(area, w)
        if abs(fx - dx) <= SNAP * s and abs(ftop - dtop) <= SNAP * s * 2:
            state['mode'] = MODE_RIGHT
    _save()
    _tag()


class home_builder_OT_inspector_drag(bpy.types.Operator):
    """Move the selection inspector by its header"""
    bl_idname = "home_builder.inspector_drag"
    bl_label = "Move Inspector"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        self._area = context.area
        if not begin_drag(context, context.area, context.region,
                          event.mouse_region_x, event.mouse_region_y):
            return {'CANCELLED'}
        self._start = (event.mouse_region_x, event.mouse_region_y)
        self._moved = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        mx, my = event.mouse_region_x, event.mouse_region_y
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            # A click on the title, released in place, moves nothing.
            if (self._moved or abs(mx - self._start[0])
                    + abs(my - self._start[1]) > 4 * _s()):
                self._moved = True
                drag_to(context, self._area, mx, my)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            end_drag(context, self._area, cancelled=not self._moved)
            if not self._moved:
                # A click on the title, not a drag: fold or unfold.
                toggle_collapsed()
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            end_drag(context, self._area, cancelled=True)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class home_builder_OT_inspector_dock(bpy.types.Operator):
    """Pop the selection's settings out of the panel, or put them back"""
    bl_idname = "home_builder.inspector_dock"
    bl_label = "Dock Selection Settings"
    bl_options = {'INTERNAL'}

    mode: bpy.props.EnumProperty(items=(
        (MODE_PANEL, "In Panel", "On the panel's SELECTED tab"),
        (MODE_RIGHT, "Docked Right", "Down the right side of the viewport"),
        (MODE_FLOAT, "Floating", "Where it was last dragged"),
    ), default=MODE_RIGHT)  # type: ignore

    def execute(self, context):
        set_mode(self.mode)
        return {'FINISHED'}


def _tag():
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass


classes = (
    home_builder_OT_inspector_drag,
    home_builder_OT_inspector_dock,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
