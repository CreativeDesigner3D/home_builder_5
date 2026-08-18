"""
Scene Navigator -- GPU-drawn quick scene picker for Home Builder 5.

A modal overlay listing project scenes grouped by Rooms / Layout Views /
Details. The panel header shows the current scene and carries a pin
toggle; clicking a row switches scenes. When pinned, the navigator stays
open after a switch so several scenes can be picked in a row -- otherwise
it closes on the first pick. Room rows carry rename and delete buttons,
and a New Room button sits at the bottom -- each of those closes the
navigator and opens the corresponding operator dialog. Click outside /
Esc / RMB dismisses.

The panel sizes itself to its longest name (within limits; longer names are
ellipsized), its list is clamped to the viewport and scrolls with the mouse
wheel, and section headers click to collapse.
"""

import bpy
import gpu
import blf

from ..hb_gpu_draw import (
    get_visible_window_bounds as _get_visible_window_bounds,
    draw_rect as _draw_rect,
    draw_rect_outline as _draw_rect_outline,
    draw_lines as _draw_lines,
    draw_text as _draw_text,
    vcenter_baseline as _vcenter_baseline,
    point_in_rect as _point_in_rect,
)


# ---- Layout constants -------------------------------------------------------
# All in unscaled pixels -- every one is multiplied by _s() at use, so the
# panel tracks Blender's UI scale instead of shrinking on high-DPI screens.

PANEL_TOP_MARGIN      = 12      # distance from top of visible window region
PANEL_BOTTOM_MARGIN   = 12      # the panel never reaches closer to the bottom
PANEL_MIN_WIDTH       = 250     # width grows with the longest name up to MAX
PANEL_MAX_WIDTH       = 440
PANEL_PADDING_X       = 10
PANEL_PADDING_Y       = 8

ROW_HEIGHT            = 24
SECTION_GAP           = 6
SECTION_HEADER_HEIGHT = 22
SECTION_CHEVRON_W     = 12      # collapse chevron column ahead of the label
ACCENT_WIDTH          = 3
ACCENT_LEFT_PAD       = 6
ROW_TEXT_LEFT_PAD     = ACCENT_LEFT_PAD + ACCENT_WIDTH + 8
ROW_TEXT_RIGHT_PAD    = 8       # gap kept between text and the row's right edge
PARENT_MIN_NAME_W     = 60      # drop the parent prefix if the name gets narrower

LIST_MIN_ROWS         = 3       # scrolling list never shrinks below this
SCROLL_STEP_ROWS      = 2       # rows per wheel notch
SCROLLBAR_WIDTH       = 4
SCROLLBAR_PAD         = 4

PANEL_HEADER_HEIGHT   = 26
ACTION_BTN_SIZE       = 18
ACTION_BTN_GAP        = 4
ACTION_BTN_RIGHT_PAD  = 5
NEW_ROOM_BTN_HEIGHT   = 26
NEW_ROOM_GAP          = 8

ROW_FONT_SIZE         = 12
HEADER_FONT_SIZE      = 10
PARENT_FONT_SIZE      = 11

# ---- Colors -----------------------------------------------------------------

COLOR_ROOMS    = (0.59, 0.77, 0.35)
COLOR_LAYOUTS  = (0.52, 0.72, 0.92)
COLOR_DETAILS  = (0.94, 0.62, 0.15)

PANEL_BG       = (0.08, 0.08, 0.08, 0.93)
PANEL_BORDER   = (1.0, 1.0, 1.0, 0.10)

ROW_HOVER_BG   = (1.0, 1.0, 1.0, 0.06)

TEXT_PRIMARY   = (0.95, 0.95, 0.95, 1.0)
TEXT_NORMAL    = (0.78, 0.78, 0.78, 1.0)
TEXT_DIM       = (0.45, 0.45, 0.45, 1.0)
HEADER_TEXT    = (0.55, 0.55, 0.55, 1.0)

ACTION_BG              = (1.0, 1.0, 1.0, 0.07)
ACTION_HOVER_BG        = (1.0, 1.0, 1.0, 0.16)
ACTION_DELETE_HOVER_BG = (0.80, 0.22, 0.20, 0.65)
ACTION_GLYPH           = (0.78, 0.78, 0.78, 1.0)
ACTION_GLYPH_HOVER     = (1.0, 1.0, 1.0, 1.0)
NEW_ROOM_BG            = (0.18, 0.18, 0.20, 1.0)
NEW_ROOM_HOVER_BG      = (0.20, 0.43, 0.70, 1.0)
SEPARATOR_COLOR        = (1.0, 1.0, 1.0, 0.10)

PIN_GLYPH              = (0.78, 0.78, 0.78, 1.0)
PIN_GLYPH_ACTIVE       = (1.0, 1.0, 1.0, 1.0)
PIN_ACTIVE_BG          = (0.20, 0.43, 0.70, 1.0)

SCROLLBAR_TRACK        = (1.0, 1.0, 1.0, 0.06)
SCROLLBAR_THUMB        = (1.0, 1.0, 1.0, 0.28)


# ---- Module state -----------------------------------------------------------

# When pinned, the navigator stays open after a scene is picked so several
# scenes can be switched in a row. Clicking away (or Esc) still closes it.
# Sticky for the session -- a module global, intentionally not per-instance.
_pinned = False

# List scroll offset in scaled px (0 = top). Clamped by _build_layout, which
# also nudges it so the current scene's row is in view whenever the current
# scene changes -- otherwise the user's own scrolling wins.
_scroll = 0.0
_last_current = None

# Section labels the user has collapsed (sticky for the session). Switching
# into a scene re-expands the section that contains it.
_collapsed = set()


# ---- Scale ------------------------------------------------------------------

def _s():
    """Global UI scale (Resolution Scale x DPI). This panel is GPU-drawn in
    raw pixels, so every dimension and font size is multiplied by this to
    track Blender's UI -- otherwise it stays device-pixel sized and reads
    as a postage stamp on high-DPI / scaled displays. Same helper the
    viewport HUD uses."""
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


# ---- Scene helpers ----------------------------------------------------------

def _is_room(scene):
    return not scene.get('IS_LAYOUT_VIEW') and not scene.get('IS_DETAIL_VIEW')

def _is_layout(scene):
    return bool(scene.get('IS_LAYOUT_VIEW'))

def _is_detail(scene):
    return bool(scene.get('IS_DETAIL_VIEW'))

def _sort_key(scene):
    so = 0
    if hasattr(scene, 'home_builder'):
        so = getattr(scene.home_builder, 'sort_order', 0) or 0
    return (so, scene.name.lower())

def _parent_room_name(scene):
    """Resolve a layout view's source wall back to the room scene that owns it.

    Returns None when the layout view's own name already leads with that
    room name -- shown as a parent prefix it would just duplicate the room
    name the row already displays."""
    sw_name = scene.get('SOURCE_WALL')
    if not sw_name:
        return None
    wall = bpy.data.objects.get(sw_name)
    if not wall:
        return None
    for us in wall.users_scene:
        if _is_room(us):
            if scene.name.lower().startswith(us.name.lower()):
                return None
            return us.name
    return None

def _collect_groups():
    """Return list of (label, color, sorted_scenes, parent_fn) for non-empty sections."""
    rooms, layouts, details = [], [], []
    for s in bpy.data.scenes:
        if _is_layout(s):
            layouts.append(s)
        elif _is_detail(s):
            details.append(s)
        else:
            rooms.append(s)
    rooms.sort(key=_sort_key)
    layouts.sort(key=_sort_key)
    details.sort(key=_sort_key)
    raw = [
        ('ROOMS',        COLOR_ROOMS,   rooms,   None),
        ('LAYOUT VIEWS', COLOR_LAYOUTS, layouts, _parent_room_name),
        ('DETAILS',      COLOR_DETAILS, details, None),
    ]
    return [g for g in raw if g[2]]

# ---- Glyph helpers ----------------------------------------------------------

def _draw_rename_glyph(shader, rect, color):
    """A small text-field box with a cursor bar -- the rename affordance."""
    rx, ry, rw, rh = rect
    s = _s()
    pad = 4 * s
    bx, by = rx + pad, ry + pad
    bw, bh = rw - pad * 2, rh - pad * 2
    _draw_rect_outline(shader, bx, by, bw, bh, color)
    cx = bx + bw / 3.0
    _draw_rect(shader, cx, by + 2 * s, 1.5 * s, bh - 4 * s, color)


def _draw_delete_glyph(shader, rect, color):
    """An X -- the delete affordance."""
    rx, ry, rw, rh = rect
    pad = 5 * _s()
    x0, y0 = rx + pad, ry + pad
    x1, y1 = rx + rw - pad, ry + rh - pad
    _draw_lines(shader, [(x0, y0), (x1, y1), (x0, y1), (x1, y0)], color)


def _draw_plus_glyph(shader, cx, cy, size, color):
    """A plus sign centered at (cx, cy). ``size`` arrives pre-scaled."""
    half = size / 2.0
    thick = 1.5 * _s()
    _draw_rect(shader, cx - half, cy - thick / 2.0, size, thick, color)
    _draw_rect(shader, cx - thick / 2.0, cy - half, thick, size, color)


def _draw_pin_glyph(shader, rect, color):
    """A small thumbtack -- the pin toggle affordance: a flat head with a
    short needle dropping from it."""
    rx, ry, rw, rh = rect
    s = _s()
    cx = rx + rw / 2.0
    head_w, head_h = 9 * s, 4 * s
    head_y = ry + rh - 5 * s - head_h
    _draw_rect(shader, cx - head_w / 2.0, head_y, head_w, head_h, color)
    _draw_lines(shader, [(cx, head_y), (cx, ry + 4 * s)], color)


def _draw_chevron(shader, cx, cy, size, collapsed, color):
    """Section disclosure chevron centered at (cx, cy): points right when
    the section is collapsed, down when expanded. ``size`` is pre-scaled."""
    h = size / 2.0
    if collapsed:
        pts = [(cx - h / 2.0, cy + h), (cx + h / 2.0, cy),
               (cx + h / 2.0, cy), (cx - h / 2.0, cy - h)]
    else:
        pts = [(cx - h, cy + h / 2.0), (cx, cy - h / 2.0),
               (cx, cy - h / 2.0), (cx + h, cy + h / 2.0)]
    _draw_lines(shader, pts, color)


# ---- Text fitting -----------------------------------------------------------

def _text_w(font_id, size, text):
    blf.size(font_id, size)
    return blf.dimensions(font_id, text)[0]


def _fit_text(font_id, size, text, max_w):
    """Return ``text`` if it fits in ``max_w`` px at ``size``, else the
    longest prefix that fits with a trailing ellipsis."""
    if _text_w(font_id, size, text) <= max_w:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _text_w(font_id, size, text[:mid].rstrip() + ell) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return (text[:lo].rstrip() + ell) if lo > 0 else ell


# ---- Layout computation -----------------------------------------------------

def _build_layout(region, area, current_scene_name,
                  anchor_x=-1.0, anchor_top=-1.0):
    """Compute panel rect + entry rects from current region size and scenes.

    The panel is as wide as its longest row (clamped to MIN/MAX and the
    viewport); the section list is clamped to the viewport height and
    scrolls -- rows scrolled out of the clip rect are omitted, partially
    visible ones are kept (the painter clips them, hit-testing checks the
    clip rect). Collapsed sections contribute only their header.

    Returns (panel_rect, entries). panel_rect is (x, y, w, h) in region px
    (y is the bottom edge). entries is a list of tuples:
        ('panel_header', current_scene_name, rect, pin_rect)
        ('list', clip_rect, track_rect_or_None, thumb_rect_or_None)
        ('header', label, color, rect, collapsed, count)
        ('row', scene, parent, color, is_current, rect,
                rename_rect_or_None, delete_rect_or_None)
        ('new_room', rect)
    Room rows carry rename/delete sub-rects; other rows carry None.
    """
    global _scroll, _last_current
    groups = _collect_groups()

    s = _s()
    panel_hdr_h = PANEL_HEADER_HEIGHT * s
    section_gap = SECTION_GAP * s
    section_hdr_h = SECTION_HEADER_HEIGHT * s
    row_h = ROW_HEIGHT * s
    new_room_gap = NEW_ROOM_GAP * s
    new_room_h = NEW_ROOM_BTN_HEIGHT * s
    pad_x = PANEL_PADDING_X * s
    pad_y = PANEL_PADDING_Y * s
    btn = ACTION_BTN_SIZE * s
    btn_gap = ACTION_BTN_GAP * s
    btn_right_pad = ACTION_BTN_RIGHT_PAD * s
    row_font = ROW_FONT_SIZE * s
    parent_font = PARENT_FONT_SIZE * s
    hdr_font = HEADER_FONT_SIZE * s
    font_id = 0

    # A scene switch re-expands its section and re-targets the scroll.
    current_changed = current_scene_name != _last_current
    _last_current = current_scene_name
    if current_changed:
        for label, _c, scenes, _p in groups:
            if any(sc.name == current_scene_name for sc in scenes):
                _collapsed.discard(label)

    # ---- Flatten the list into items + measure the widest row ----------
    # items: (kind, payload, height, needed_w) in display order.
    room_reserve = btn_right_pad + btn * 2 + btn_gap + 6 * s
    plain_reserve = ROW_TEXT_RIGHT_PAD * s
    text_left = ROW_TEXT_LEFT_PAD * s
    items = []
    for i, (label, color, scenes, parent_fn) in enumerate(groups):
        collapsed = label in _collapsed
        if i > 0:
            items.append(('gap', None, section_gap, 0.0))
        hdr_w = (SECTION_CHEVRON_W * s + _text_w(font_id, hdr_font, label)
                 + (_text_w(font_id, hdr_font, f"  {len(scenes)}")
                    if collapsed else 0.0))
        items.append(('header', (label, color, collapsed, len(scenes)),
                      section_hdr_h, hdr_w))
        if collapsed:
            continue
        for sc in scenes:
            parent = parent_fn(sc) if parent_fn else None
            tw = _text_w(font_id, row_font, sc.name)
            if parent:
                tw += _text_w(font_id, parent_font, parent + "  ·  ")
            reserve = room_reserve if _is_room(sc) else plain_reserve
            items.append(('row', (sc, parent, color), row_h,
                          text_left + tw + reserve))
    list_h_full = sum(it[2] for it in items)

    # ---- Panel geometry --------------------------------------------------
    x_min, x_max, y_min, y_max = _get_visible_window_bounds(area)
    panel_top = anchor_top if anchor_top >= 0.0 else y_max - PANEL_TOP_MARGIN * s

    fixed_h = (pad_y * 2 + panel_hdr_h + section_gap
               + new_room_gap + new_room_h)
    max_list_h = (panel_top - (y_min + PANEL_BOTTOM_MARGIN * s)) - fixed_h
    list_h = list_h_full
    scrollable = list_h_full > max_list_h
    sb_reserve = (SCROLLBAR_WIDTH + SCROLLBAR_PAD) * s if scrollable else 0.0
    if scrollable:
        list_h = max(max_list_h, row_h * LIST_MIN_ROWS)
    panel_h = fixed_h + list_h
    panel_y = panel_top - panel_h

    hdr_needed = (_text_w(font_id, hdr_font, "CURRENT") + 8 * s
                  + _text_w(font_id, row_font, current_scene_name)
                  + 8 * s + btn + btn_right_pad)
    needed_w = max([hdr_needed]
                   + [it[3] + sb_reserve for it in items]) + pad_x * 2
    avail_w = (x_max - x_min) - PANEL_TOP_MARGIN * s * 2
    panel_w = max(PANEL_MIN_WIDTH * s,
                  min(needed_w, PANEL_MAX_WIDTH * s, avail_w))
    visible_w = max(x_max - x_min, panel_w)

    if anchor_top >= 0.0:
        # Anchored under a specific button (the viewport HUD trigger);
        # clamp so a wide panel stays on screen.
        panel_x = min(max(anchor_x, x_min), x_max - panel_w)
    else:
        # Center horizontally within the visible window area; anchor to top.
        panel_x = x_min + (visible_w - panel_w) / 2.0

    panel_rect = (panel_x, panel_y, panel_w, panel_h)
    content_x = panel_x + pad_x
    content_w = panel_w - pad_x * 2
    entries = []

    # ---- Panel header ----------------------------------------------------
    cursor_y = panel_top - pad_y
    ph_rect = (content_x, cursor_y - panel_hdr_h, content_w, panel_hdr_h)
    pin_y = ph_rect[1] + (panel_hdr_h - btn) / 2.0
    pin_x = content_x + content_w - btn_right_pad - btn
    pin_rect = (pin_x, pin_y, btn, btn)
    entries.append(('panel_header', current_scene_name, ph_rect, pin_rect))
    cursor_y -= panel_hdr_h + section_gap

    # ---- Scrolling list --------------------------------------------------
    list_top = cursor_y
    list_bottom = list_top - list_h
    row_w = content_w - sb_reserve
    track_rect = thumb_rect = None
    if scrollable:
        sb_w = SCROLLBAR_WIDTH * s
        max_scroll = list_h_full - list_h
        # Bring the current scene's row into view on a scene switch.
        if current_changed:
            off = 0.0
            for kind, payload, h, _w in items:
                if kind == 'row' and payload[0].name == current_scene_name:
                    if off < _scroll:
                        _scroll = off
                    elif off + h > _scroll + list_h:
                        _scroll = off + h - list_h
                    break
                off += h
        _scroll = min(max(_scroll, 0.0), max_scroll)
        track_rect = (content_x + content_w - sb_w, list_bottom, sb_w, list_h)
        thumb_h = max(list_h * (list_h / list_h_full), row_h)
        thumb_y = (list_top - thumb_h
                   - (list_h - thumb_h) * (_scroll / max_scroll))
        thumb_rect = (track_rect[0], thumb_y, sb_w, thumb_h)
    else:
        _scroll = 0.0
    clip_rect = (content_x, list_bottom, content_w, list_h)
    entries.append(('list', clip_rect, track_rect, thumb_rect))

    y = list_top + _scroll          # top edge of the first item
    for kind, payload, h, _w in items:
        item_top, item_bot = y, y - h
        y -= h
        if kind == 'gap' or item_bot >= list_top or item_top <= list_bottom:
            continue                # entirely outside the clip -> skip
        if kind == 'header':
            label, color, collapsed, count = payload
            entries.append(('header', label, color,
                            (content_x, item_bot, row_w, h),
                            collapsed, count))
        else:
            sc, parent, color = payload
            row_rect = (content_x, item_bot, row_w, h)
            rename_rect = delete_rect = None
            if _is_room(sc):
                by = item_bot + (h - btn) / 2.0
                dx = content_x + row_w - btn_right_pad - btn
                rnx = dx - btn_gap - btn
                delete_rect = (dx, by, btn, btn)
                rename_rect = (rnx, by, btn, btn)
            entries.append((
                'row', sc, parent, color,
                sc.name == current_scene_name, row_rect,
                rename_rect, delete_rect,
            ))

    # ---- New Room button -------------------------------------------------
    cursor_y = list_bottom - new_room_gap
    new_room_rect = (content_x, cursor_y - new_room_h, content_w, new_room_h)
    entries.append(('new_room', new_room_rect))

    return panel_rect, entries


def _list_clip(entries):
    for entry in entries or ():
        if entry[0] == 'list':
            return entry[1]
    return None


def scroll_by(rows):
    """Scroll the list by ``rows`` row-heights (positive = down). The next
    _build_layout clamps it."""
    global _scroll
    _scroll += rows * ROW_HEIGHT * _s()


def is_scrollable(entries):
    for entry in entries or ():
        if entry[0] == 'list':
            return entry[2] is not None
    return False


def hit_test(mx, my, entries):
    """Resolve a point against navigator entries.

    Returns (kind, payload) or None:
        ('pin', None)          panel-header pin toggle
        ('section', label)     section header (collapse / expand)
        ('rename', scene) / ('delete', scene) / ('row', scene)
        ('new_room', None)
    List entries scrolled partly out of the clip rect only hit on their
    visible part. Shared by the modal and the pinned/HUD click path so the
    two can't disagree.
    """
    clip = _list_clip(entries)
    for entry in entries or ():
        kind = entry[0]
        if kind == 'panel_header':
            if _point_in_rect(mx, my, entry[3]):
                return ('pin', None)
        elif kind == 'header':
            if clip and not _point_in_rect(mx, my, clip):
                continue
            if _point_in_rect(mx, my, entry[3]):
                return ('section', entry[1])
        elif kind == 'row':
            if clip and not _point_in_rect(mx, my, clip):
                continue
            (_, scene, _parent, _color, _is_current, rect,
             rename_rect, delete_rect) = entry
            if rename_rect and _point_in_rect(mx, my, rename_rect):
                return ('rename', scene)
            if delete_rect and _point_in_rect(mx, my, delete_rect):
                return ('delete', scene)
            if _point_in_rect(mx, my, rect):
                return ('row', scene)
        elif kind == 'new_room':
            if _point_in_rect(mx, my, entry[1]):
                return ('new_room', None)
    return None


def toggle_section(label):
    if label in _collapsed:
        _collapsed.discard(label)
    else:
        _collapsed.add(label)


# ---- Draw helpers -----------------------------------------------------------

def _draw_panel_header(shader, font_id, rect, current_name, pin_rect, mx, my):
    rx, ry, rw, rh = rect
    s = _s()
    hdr_font = HEADER_FONT_SIZE * s
    row_font = ROW_FONT_SIZE * s
    blf.size(font_id, hdr_font)
    label = "CURRENT"
    label_w = blf.dimensions(font_id, label)[0]
    baseline = _vcenter_baseline(rect, font_id, row_font)
    _draw_text(font_id, rx, baseline, hdr_font, HEADER_TEXT, label)
    name_x = rx + label_w + 8 * s
    name_w = pin_rect[0] - 8 * s - name_x
    _draw_text(font_id, name_x, baseline, row_font, TEXT_PRIMARY,
               _fit_text(font_id, row_font, current_name, name_w))
    # separator line at the bottom of the header rect
    _draw_rect(shader, rx, ry, rw, max(1.0, s), SEPARATOR_COLOR)
    # pin toggle -- when lit, the navigator stays open across scene picks
    px, py, pw, ph = pin_rect
    hovered = _point_in_rect(mx, my, pin_rect)
    if _pinned:
        bg = PIN_ACTIVE_BG
    elif hovered:
        bg = ACTION_HOVER_BG
    else:
        bg = ACTION_BG
    _draw_rect(shader, px, py, pw, ph, bg)
    glyph = PIN_GLYPH_ACTIVE if (_pinned or hovered) else PIN_GLYPH
    _draw_pin_glyph(shader, pin_rect, glyph)


def _draw_row(shader, font_id, entry, mx, my):
    (_, scene, parent, color, is_current, rect,
     rename_rect, delete_rect) = entry
    rx, ry, rw, rh = rect
    hovered = _point_in_rect(mx, my, rect)

    if is_current:
        _draw_rect(shader, rx, ry, rw, rh, (*color, 0.14))
    elif hovered:
        _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)

    s = _s()
    row_font = ROW_FONT_SIZE * s
    parent_font = PARENT_FONT_SIZE * s

    accent_alpha = 1.0 if is_current else (0.85 if hovered else 0.55)
    _draw_rect(shader, rx + ACCENT_LEFT_PAD * s, ry + 4 * s,
               ACCENT_WIDTH * s, rh - 8 * s, (*color, accent_alpha))

    text_x = rx + ROW_TEXT_LEFT_PAD * s
    name_color = TEXT_PRIMARY if is_current else TEXT_NORMAL
    baseline = _vcenter_baseline(rect, font_id, row_font)

    # Text must stop short of the action buttons (room rows) or the row's
    # right edge; the parent prefix is dropped first, then the name is
    # ellipsized, so long names never run under the buttons or the border.
    if rename_rect is not None:
        avail = rename_rect[0] - 6 * s - text_x
    else:
        avail = rx + rw - ROW_TEXT_RIGHT_PAD * s - text_x

    if parent:
        blf.size(font_id, parent_font)
        parent_w = blf.dimensions(font_id, parent)[0]
        sep = "  \u00b7  "
        sep_w = blf.dimensions(font_id, sep)[0]
        if parent_w + sep_w + PARENT_MIN_NAME_W * s > avail:
            parent = None
    if parent:
        _draw_text(font_id, text_x, baseline,
                   parent_font, TEXT_DIM, parent)
        _draw_text(font_id, text_x + parent_w, baseline,
                   parent_font, TEXT_DIM, sep)
        name = _fit_text(font_id, row_font, scene.name,
                         avail - parent_w - sep_w)
        _draw_text(font_id, text_x + parent_w + sep_w, baseline,
                   row_font, name_color, name)
    else:
        name = _fit_text(font_id, row_font, scene.name, avail)
        _draw_text(font_id, text_x, baseline, row_font, name_color, name)

    if rename_rect is not None:
        r_hover = _point_in_rect(mx, my, rename_rect)
        brx, bry, brw, brh = rename_rect
        _draw_rect(shader, brx, bry, brw, brh,
                   ACTION_HOVER_BG if r_hover else ACTION_BG)
        _draw_rename_glyph(shader, rename_rect,
                           ACTION_GLYPH_HOVER if r_hover else ACTION_GLYPH)
    if delete_rect is not None:
        d_hover = _point_in_rect(mx, my, delete_rect)
        bdx, bdy, bdw, bdh = delete_rect
        _draw_rect(shader, bdx, bdy, bdw, bdh,
                   ACTION_DELETE_HOVER_BG if d_hover else ACTION_BG)
        _draw_delete_glyph(shader, delete_rect,
                           ACTION_GLYPH_HOVER if d_hover else ACTION_GLYPH)


def _draw_new_room_button(shader, font_id, rect, mx, my):
    rx, ry, rw, rh = rect
    hovered = _point_in_rect(mx, my, rect)
    _draw_rect(shader, rx, ry, rw, rh,
               NEW_ROOM_HOVER_BG if hovered else NEW_ROOM_BG)
    _draw_rect_outline(shader, rx, ry, rw, rh, PANEL_BORDER)
    label = "New Room"
    s = _s()
    row_font = ROW_FONT_SIZE * s
    blf.size(font_id, row_font)
    label_w = blf.dimensions(font_id, label)[0]
    plus_size = 10 * s
    gap = 8 * s
    group_w = plus_size + gap + label_w
    gx = rx + (rw - group_w) / 2.0
    cy = ry + rh / 2.0
    _draw_plus_glyph(shader, gx + plus_size / 2.0, cy, plus_size, TEXT_PRIMARY)
    baseline = _vcenter_baseline(rect, font_id, row_font)
    _draw_text(font_id, gx + plus_size + gap, baseline,
               row_font, TEXT_PRIMARY, label)


# ---- Draw callback ----------------------------------------------------------

def paint_navigator(panel_rect, entries, mx, my):
    """Stateless GPU paint of the navigator panel.

    Factored out of the modal draw callback so the persistent viewport HUD
    can render the SAME panel when the navigator is pinned -- the HUD owns a
    permanent draw handler that survives designing, where the modal's own
    handler does not.
    """
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    px, py, pw, ph = panel_rect
    _draw_rect(shader, px, py, pw, ph, PANEL_BG)
    _draw_rect_outline(shader, px, py, pw, ph, PANEL_BORDER)

    font_id = 0
    s = _s()
    # The list is scissor-clipped so partially scrolled rows cut off cleanly
    # at the list edges. gpu scissor coords are framebuffer-relative, so
    # offset our region-local clip rect by whatever scissor is current
    # (the region's own), and restore it afterwards.
    clip = _list_clip(entries)
    saved_scissor = None
    if clip is not None:
        saved_scissor = gpu.state.scissor_get()
        ox, oy = saved_scissor[0], saved_scissor[1]
        cx, cy, cw, ch = clip
        gpu.state.scissor_test_set(True)
        gpu.state.scissor_set(int(ox + cx), int(oy + cy),
                              int(cw) + 1, int(ch) + 1)

    # Hover inside the list only counts on the visible part of the clip.
    if clip is not None and not _point_in_rect(mx, my, clip):
        lmx = lmy = -1.0
    else:
        lmx, lmy = mx, my

    for entry in entries:
        kind = entry[0]
        if kind == 'header':
            _, label, color, rect, collapsed, count = entry
            rx, ry, rw, rh = rect
            hdr_font = HEADER_FONT_SIZE * s
            hovered = _point_in_rect(lmx, lmy, rect)
            if hovered:
                _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)
            baseline = _vcenter_baseline(rect, font_id, hdr_font)
            chev = SECTION_CHEVRON_W * s
            _draw_chevron(shader, rx + chev / 2.0 - 1 * s, ry + rh / 2.0,
                          6 * s, collapsed,
                          TEXT_NORMAL if hovered else HEADER_TEXT)
            _draw_text(font_id, rx + chev, baseline, hdr_font,
                       TEXT_NORMAL if hovered else HEADER_TEXT, label)
            if collapsed:
                lw = _text_w(font_id, hdr_font, label)
                _draw_text(font_id, rx + chev + lw, baseline, hdr_font,
                           TEXT_DIM, f"  {count}")
        elif kind == 'row':
            _draw_row(shader, font_id, entry, lmx, lmy)

    if saved_scissor is not None:
        gpu.state.scissor_set(*saved_scissor)
        gpu.state.scissor_test_set(False)

    for entry in entries:
        kind = entry[0]
        if kind == 'panel_header':
            _draw_panel_header(shader, font_id, entry[2], entry[1],
                               entry[3], mx, my)
        elif kind == 'list':
            _, _clip, track, thumb = entry
            if track is not None:
                _draw_rect(shader, *track, SCROLLBAR_TRACK)
                _draw_rect(shader, *thumb, SCROLLBAR_THUMB)
        elif kind == 'new_room':
            _draw_new_room_button(shader, font_id, entry[1], mx, my)

    gpu.state.blend_set('NONE')


def draw_scene_navigator(op):
    """GPU draw callback for the transient (unpinned) scene-navigator modal."""
    if op.region is None or op.entries is None:
        return
    # Only draw in the region this modal was bound to (skip other 3D views)
    if bpy.context.region != op.region:
        return
    paint_navigator(op.panel_rect, op.entries, op.mouse_x, op.mouse_y)


# ---- Persistent-HUD interface ----------------------------------------------
# Let the always-on viewport HUD host the navigator while it's pinned, instead
# of the transient modal below. The HUD calls build_pinned_layout() +
# paint_navigator() each redraw, and handle_navigator_click() on a press.

def is_pinned():
    return _pinned


def set_pinned(value):
    global _pinned
    _pinned = bool(value)


def build_pinned_layout(context, area, region, anchor_x=-1.0, anchor_top=-1.0):
    """Return (panel_rect, entries) for the pinned navigator, else None.

    None when not pinned or the geometry can't be built. Anchored under the
    HUD nav button via anchor_x / anchor_top, matching the modal drop-down.
    """
    if not _pinned or region is None or area is None:
        return None
    return _build_layout(region, area, context.scene.name, anchor_x, anchor_top)


def handle_navigator_click(context, mx, my, entries):
    """Dispatch a left-press against pinned-navigator entries.

    Stateless mirror of the modal's hit-testing. Returns True if a navigator
    element was hit (caller consumes the click), False on a miss (caller
    passes it through so the viewport stays interactive while pinned). Hits
    never close the panel -- it's pinned; only the header pin glyph un-pins.
    """
    global _pinned
    hit = hit_test(mx, my, entries)
    if hit is None:
        return False
    kind, scene = hit
    try:
        if kind == 'pin':
            _pinned = False          # pin glyph un-pins (hides the panel)
        elif kind == 'section':
            toggle_section(scene)
        elif kind == 'rename':
            with context.temp_override(scene=scene):
                bpy.ops.home_builder.rename_room(
                    'INVOKE_DEFAULT', scene_name=scene.name)
        elif kind == 'delete':
            bpy.ops.home_builder.delete_room(
                'INVOKE_DEFAULT', scene_name=scene.name)
        elif kind == 'row':
            if scene.name != context.scene.name:
                bpy.ops.home_builder_layouts.go_to_layout_view(
                    scene_name=scene.name)
        elif kind == 'new_room':
            bpy.ops.home_builder.create_room('INVOKE_DEFAULT')
    except Exception:
        pass
    return True


def handle_navigator_scroll(context, mx, my, entries, rows):
    """Wheel over the pinned navigator: scroll its list. Returns True when
    consumed (cursor over a scrollable list), False to pass through."""
    if not is_scrollable(entries):
        return False
    clip = _list_clip(entries)
    if clip is None or not _point_in_rect(mx, my, clip):
        return False
    scroll_by(rows)
    return True


# ---- Modal operator ---------------------------------------------------------

class home_builder_OT_scene_navigator(bpy.types.Operator):
    bl_idname = "home_builder.scene_navigator"
    bl_label = "Scene Navigator"
    bl_description = "Quick switch between rooms, layout views, and details"

    # Optional anchor (WINDOW-local px). When set, the panel is placed with
    # its top-left here instead of centered at the top -- used by the
    # viewport HUD to drop the panel directly under its trigger button.
    anchor_x: bpy.props.FloatProperty(default=-1.0)  # type: ignore
    anchor_top: bpy.props.FloatProperty(default=-1.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        # The click may have come from a sidebar button (UI region) rather
        # than the viewport itself, so explicitly resolve the 3D viewport's
        # WINDOW region. All coords below are kept WINDOW-local.
        if context.area is None or context.area.type != 'VIEW_3D':
            return {'CANCELLED'}

        window_region = None
        for r in context.area.regions:
            if r.type == 'WINDOW':
                window_region = r
                break
        if window_region is None:
            return {'CANCELLED'}

        self.region = window_region
        self.area = context.area
        self.mouse_x = event.mouse_x - window_region.x
        self.mouse_y = event.mouse_y - window_region.y
        self.entries = None
        self.panel_rect = (0, 0, 0, 0)
        self._draw_handle = None

        self._rebuild_layout(context)

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_scene_navigator, (self,), 'WINDOW', 'POST_PIXEL'
        )
        context.window_manager.modal_handler_add(self)
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _rebuild_layout(self, context):
        current = context.scene.name
        self.panel_rect, self.entries = _build_layout(
            self.region, self.area, current, self.anchor_x, self.anchor_top
        )

    def _cleanup(self, context):
        if self._draw_handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    self._draw_handle, 'WINDOW'
                )
            except Exception:
                pass
            self._draw_handle = None
        if context.area:
            context.area.tag_redraw()

    def _switch_to(self, context, scene_name):
        try:
            bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene_name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not switch to {scene_name}: {e}")

    def _create_room(self, context):
        try:
            bpy.ops.home_builder.create_room('INVOKE_DEFAULT')
        except Exception as e:
            self.report({'WARNING'}, f"Could not create room: {e}")

    def _rename_room(self, context, scene):
        # temp_override(scene=...) so rename_room's poll and invoke see the
        # target room; execute targets it explicitly via scene_name.
        try:
            with context.temp_override(scene=scene):
                bpy.ops.home_builder.rename_room(
                    'INVOKE_DEFAULT', scene_name=scene.name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not rename {scene.name}: {e}")

    def _delete_room(self, context, scene):
        try:
            bpy.ops.home_builder.delete_room(
                'INVOKE_DEFAULT', scene_name=scene.name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not delete {scene.name}: {e}")

    def modal(self, context, event):
        global _pinned
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_x - self.region.x
            self.mouse_y = event.mouse_y - self.region.y
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} \
                and event.value == 'PRESS':
            if is_scrollable(self.entries):
                scroll_by(-SCROLL_STEP_ROWS if event.type == 'WHEELUPMOUSE'
                          else SCROLL_STEP_ROWS)
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx = event.mouse_x - self.region.x
            my = event.mouse_y - self.region.y
            hit = hit_test(mx, my, self.entries)
            if hit is None:
                # nothing hit -- dismiss
                self._cleanup(context)
                return {'CANCELLED'}
            kind, scene = hit
            if kind == 'pin':
                _pinned = not _pinned
                if _pinned:
                    # Hand the navigator to the persistent viewport HUD,
                    # which draws + routes it while you design. Close this
                    # transient modal so it isn't drawn twice. If the HUD is
                    # disabled there's nothing to hand off to -- fall back
                    # to the old in-modal pinned behavior (stay open across
                    # picks).
                    from . import viewport_hud
                    if viewport_hud._hud_enabled():
                        self._cleanup(context)
                        return {'FINISHED'}
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if kind == 'section':
                toggle_section(scene)
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if kind == 'rename':
                self._cleanup(context)
                self._rename_room(context, scene)
                return {'FINISHED'}
            if kind == 'delete':
                self._cleanup(context)
                self._delete_room(context, scene)
                return {'FINISHED'}
            if kind == 'row':
                # Pinned: switch but keep the navigator open so the user
                # can pick another scene. Unpinned: switch and close --
                # the original behavior.
                if _pinned:
                    if scene.name != context.scene.name:
                        self._switch_to(context, scene.name)
                        self._rebuild_layout(context)
                        if context.area:
                            context.area.tag_redraw()
                    return {'RUNNING_MODAL'}
                self._cleanup(context)
                if scene.name != context.scene.name:
                    self._switch_to(context, scene.name)
                return {'FINISHED'}
            if kind == 'new_room':
                self._cleanup(context)
                self._create_room(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._cleanup(context)
            return {'CANCELLED'}

        # Swallow everything else so it doesn't leak to the viewport
        return {'RUNNING_MODAL'}


# ---- Registration -----------------------------------------------------------

classes = (
    home_builder_OT_scene_navigator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
