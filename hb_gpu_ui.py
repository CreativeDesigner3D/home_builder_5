"""Widget layer for Home Builder's GPU-drawn viewport UI.

`hb_gpu_draw` owns the primitives -- a rect, a line, a run of text, the
visible-region maths. This module sits on top of it and owns the pieces
every panel repeats: UI scale, text fitting, the small glyph set, the
frame-and-button paint idiom, and the arithmetic behind a scrolling
list.

It deliberately knows nothing about scenes, cabinets or libraries. A
panel module supplies its own data, decides what a row means and what a
click does; this module only answers "where does it go" and "how is it
painted".

Everything is in UNSCALED pixels at the boundary: pass unscaled sizes,
multiply by `scale()` yourself, or use the *_s helpers that do it for
you. Fonts are the exception -- blf wants final pixel sizes, so text
helpers take an already-scaled size.
"""

import math
import bpy
import blf

from .hb_gpu_draw import (
    draw_rect,
    draw_rect_outline,
    draw_lines,
)


# ---- Scale ------------------------------------------------------------------

def scale():
    """Global UI scale (Resolution Scale x DPI).

    Viewport panels are drawn in raw device pixels, so every dimension
    and font size has to be multiplied by this to track Blender's UI --
    otherwise the panel stays device-pixel sized and reads as a postage
    stamp on a high-DPI or scaled display.
    """
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


# ---- Theme ------------------------------------------------------------------
# One palette so panels match each other instead of each inventing greys.
# Names describe the ROLE, not the colour, so a future themed variant can
# repoint them without touching call sites.

class Theme:
    PANEL_BG      = (0.08, 0.08, 0.08, 0.93)
    PANEL_BORDER  = (1.0, 1.0, 1.0, 0.10)
    SEPARATOR     = (1.0, 1.0, 1.0, 0.10)

    ROW_HOVER_BG  = (1.0, 1.0, 1.0, 0.06)

    TEXT_PRIMARY  = (0.95, 0.95, 0.95, 1.0)
    TEXT_NORMAL   = (0.78, 0.78, 0.78, 1.0)
    TEXT_DIM      = (0.45, 0.45, 0.45, 1.0)
    TEXT_HEADER   = (0.55, 0.55, 0.55, 1.0)

    BTN_BG        = (0.13, 0.13, 0.14, 0.95)
    BTN_HOVER_BG  = (0.25, 0.25, 0.27, 0.96)
    BTN_ACTIVE_BG = (0.20, 0.43, 0.70, 0.98)
    BTN_BORDER    = (1.0, 1.0, 1.0, 0.14)

    ACTION_BG            = (1.0, 1.0, 1.0, 0.07)
    ACTION_HOVER_BG      = (1.0, 1.0, 1.0, 0.16)
    ACTION_DANGER_BG     = (0.80, 0.22, 0.20, 0.65)
    GLYPH                = (0.78, 0.78, 0.78, 1.0)
    GLYPH_HOVER          = (1.0, 1.0, 1.0, 1.0)
    GLYPH_STRONG         = (0.92, 0.92, 0.92, 1.0)

    ACCENT_BG            = (0.20, 0.43, 0.70, 1.0)
    NEUTRAL_BG           = (0.18, 0.18, 0.20, 1.0)

    SCROLLBAR_TRACK      = (1.0, 1.0, 1.0, 0.06)
    SCROLLBAR_THUMB      = (1.0, 1.0, 1.0, 0.28)


# ---- Text -------------------------------------------------------------------

def text_width(font_id, size, text):
    """Width in px of `text` at an already-scaled `size`."""
    blf.size(font_id, size)
    return blf.dimensions(font_id, text)[0]


def fit_text(font_id, size, text, max_w):
    """`text` if it fits in `max_w`, else the longest prefix that fits
    with a trailing ellipsis. Binary search -- measuring every prefix is
    the obvious version and is markedly slower on long lists."""
    if text_width(font_id, size, text) <= max_w:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_width(font_id, size, text[:mid].rstrip() + ell) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return (text[:lo].rstrip() + ell) if lo > 0 else ell


def draw_centered_text(font_id, rect, size, color, text):
    """Draw `text` centred both ways inside `rect`."""
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    blf.color(font_id, *color)
    tw, th = blf.dimensions(font_id, text)
    blf.position(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0, 0)
    blf.draw(font_id, text)


# ---- Vector helpers ---------------------------------------------------------
# draw_lines consumes points two at a time as independent segments, so a
# polyline has to double its interior points. Both tool palettes need
# that, plus arcs, so it lives here rather than in each of them.

def draw_polyline(shader, pts, color, closed=False):
    """Connected line run through `pts`."""
    segs = []
    for i in range(len(pts) - 1):
        segs.extend((pts[i], pts[i + 1]))
    if closed and len(pts) > 2:
        segs.extend((pts[-1], pts[0]))
    if segs:
        draw_lines(shader, segs, color)


def arc_points(cx, cy, r, start, end, segments=12):
    """Points along an arc from `start` to `end` radians."""
    if segments < 1:
        segments = 1
    step = (end - start) / segments
    return [(cx + r * math.cos(start + step * i),
             cy + r * math.sin(start + step * i))
            for i in range(segments + 1)]


def circle_points(cx, cy, r, segments=20):
    """Points around a full circle (open ring -- close it when drawing)."""
    return arc_points(cx, cy, r, 0.0, 2.0 * math.pi, segments)[:-1]


def draw_arrow_head(shader, tip, direction, size, color):
    """Two barbs swept back from `tip` against `direction`."""
    ang = math.atan2(direction[1], direction[0])
    for off in (2.6, -2.6):
        a = ang + off
        draw_lines(shader,
                   [tip, (tip[0] + size * math.cos(a),
                          tip[1] + size * math.sin(a))],
                   color)


# ---- Glyphs -----------------------------------------------------------------
# Small vector affordances. Sizes arrive pre-scaled; each is drawn from
# the rect or centre it is given so callers keep control of placement.

def glyph_rename(shader, rect, color):
    """A text-field box with a cursor bar -- the rename affordance."""
    rx, ry, rw, rh = rect
    s = scale()
    pad = 4 * s
    bx, by = rx + pad, ry + pad
    bw, bh = rw - pad * 2, rh - pad * 2
    draw_rect_outline(shader, bx, by, bw, bh, color)
    cx = bx + bw / 3.0
    draw_rect(shader, cx, by + 2 * s, 1.5 * s, bh - 4 * s, color)


def glyph_delete(shader, rect, color):
    """An X -- the delete affordance."""
    rx, ry, rw, rh = rect
    pad = 5 * scale()
    x0, y0 = rx + pad, ry + pad
    x1, y1 = rx + rw - pad, ry + rh - pad
    draw_lines(shader, [(x0, y0), (x1, y1), (x0, y1), (x1, y0)], color)


def glyph_plus(shader, cx, cy, size, color):
    """A plus sign centred at (cx, cy). `size` arrives pre-scaled."""
    half = size / 2.0
    thick = 1.5 * scale()
    draw_rect(shader, cx - half, cy - thick / 2.0, size, thick, color)
    draw_rect(shader, cx - thick / 2.0, cy - half, thick, size, color)


def glyph_pin(shader, rect, color):
    """A thumbtack -- flat head with a short needle dropping from it."""
    rx, ry, rw, rh = rect
    s = scale()
    cx = rx + rw / 2.0
    head_w, head_h = 9 * s, 4 * s
    head_y = ry + rh - 5 * s - head_h
    draw_rect(shader, cx - head_w / 2.0, head_y, head_w, head_h, color)
    draw_lines(shader, [(cx, head_y), (cx, ry + 4 * s)], color)


def glyph_chevron(shader, cx, cy, size, collapsed, color):
    """Disclosure chevron centred at (cx, cy): points right when
    collapsed, down when expanded. `size` is pre-scaled."""
    h = size / 2.0
    if collapsed:
        pts = [(cx - h / 2.0, cy + h), (cx + h / 2.0, cy),
               (cx + h / 2.0, cy), (cx - h / 2.0, cy - h)]
    else:
        pts = [(cx - h, cy + h / 2.0), (cx, cy - h / 2.0),
               (cx, cy - h / 2.0), (cx + h, cy + h / 2.0)]
    draw_lines(shader, pts, color)


# ---- Paint idioms -----------------------------------------------------------

def paint_frame(shader, rect, bg=Theme.PANEL_BG, border=Theme.PANEL_BORDER):
    """Filled panel background plus its 1px border."""
    x, y, w, h = rect
    draw_rect(shader, x, y, w, h, bg)
    if border is not None:
        draw_rect_outline(shader, x, y, w, h, border)


def paint_button(shader, rect, hovered=False, active=False,
                 bg=Theme.BTN_BG, hover_bg=Theme.BTN_HOVER_BG,
                 active_bg=Theme.BTN_ACTIVE_BG, border=Theme.BTN_BORDER):
    """The fill-then-border button idiom, with active winning over hover.

    Returns the fill colour used, so a caller can pick a matching glyph
    or label colour without repeating the same three-way choice.
    """
    x, y, w, h = rect
    fill = active_bg if active else (hover_bg if hovered else bg)
    draw_rect(shader, x, y, w, h, fill)
    if border is not None:
        draw_rect_outline(shader, x, y, w, h, border)
    return fill


# ---- Panel geometry ---------------------------------------------------------

def panel_box(bounds, needed_w, panel_h, min_w, max_w, margin,
              anchor_x=-1.0, anchor_top=-1.0):
    """Place a panel inside `bounds` = (x_min, x_max, y_min, y_max).

    Width grows with the content (`needed_w`) but is clamped to
    min/max and to what the region can actually show. With `anchor_x` /
    `anchor_top` set the panel hangs off that point -- clamped so a wide
    panel cannot run off-screen -- otherwise it is centred horizontally
    and pinned `margin` below the top of the visible region.

    Returns (x, y, w, h) with y as the BOTTOM edge, matching every other
    rect in the GPU layer.
    """
    x_min, x_max, y_min, y_max = bounds
    top = anchor_top if anchor_top >= 0.0 else y_max - margin
    avail_w = (x_max - x_min) - margin * 2
    w = max(min_w, min(needed_w, max_w, avail_w))
    visible_w = max(x_max - x_min, w)
    if anchor_top >= 0.0:
        x = min(max(anchor_x, x_min), x_max - w)
    else:
        x = x_min + (visible_w - w) / 2.0
    return (x, top - panel_h, w, panel_h)


# ---- Scrolling list ---------------------------------------------------------

class ScrollList:
    """Geometry and scroll state for a vertically scrolling list.

    Owns the offset (in scaled px from the top of the content) and the
    arithmetic every scrolling panel repeats: does it scroll at all, how
    tall is the viewport, where do the scrollbar track and thumb sit,
    which items survive the clip, and how to nudge a particular item
    into view.

    The offset is deliberately plain state on the instance -- panels
    keep one of these at module level so scroll position is sticky
    across rebuilds, the same way a real scrollbar behaves.
    """

    def __init__(self, bar_width=4, bar_pad=4, min_rows=3):
        self.offset = 0.0
        self.bar_width = bar_width      # unscaled
        self.bar_pad = bar_pad          # unscaled
        self.min_rows = min_rows

    # -- measurement ----------------------------------------------------

    def measure(self, content_h, max_h, row_h):
        """Decide the viewport height for `content_h` of content.

        Returns (list_h, scrollable, bar_reserve). `bar_reserve` is the
        horizontal room the scrollbar needs -- zero when the content
        fits, so a short list uses the full width.
        """
        s = scale()
        scrollable = content_h > max_h
        if not scrollable:
            return content_h, False, 0.0
        list_h = max(max_h, row_h * self.min_rows)
        reserve = (self.bar_width + self.bar_pad) * s
        return list_h, True, reserve

    def clamp(self, content_h, list_h):
        """Hold the offset inside [0, content_h - list_h]."""
        self.offset = min(max(self.offset, 0.0), max(content_h - list_h, 0.0))
        return self.offset

    def scroll_by(self, rows, row_h):
        """Scroll by `rows` row-heights; positive scrolls down. Left
        unclamped -- the next measure/clamp pass bounds it."""
        self.offset += rows * row_h

    def scroll_into_view(self, item_offset, item_h, list_h):
        """Nudge the offset so an item at `item_offset` is visible, and
        no further -- scrolling the user did themselves is preserved
        whenever the item is already on screen."""
        if item_offset < self.offset:
            self.offset = item_offset
        elif item_offset + item_h > self.offset + list_h:
            self.offset = item_offset + item_h - list_h

    # -- geometry -------------------------------------------------------

    def bar_rects(self, content_x, content_w, list_top, list_h,
                  content_h, row_h):
        """(track_rect, thumb_rect) for the scrollbar, or (None, None)
        when the content fits. Assumes the offset is already clamped."""
        if content_h <= list_h:
            return None, None
        s = scale()
        bar_w = self.bar_width * s
        max_scroll = content_h - list_h
        track = (content_x + content_w - bar_w, list_top - list_h,
                 bar_w, list_h)
        thumb_h = max(list_h * (list_h / content_h), row_h)
        thumb_y = (list_top - thumb_h
                   - (list_h - thumb_h) * (self.offset / max_scroll))
        return track, (track[0], thumb_y, bar_w, thumb_h)

    def visible(self, items, list_top, list_bottom, height_of):
        """Walk `items` top-down yielding (item, item_top, item_bottom)
        for the ones the clip rect can show.

        Partially visible items are KEPT -- the painter clips them and
        hit-testing checks the clip rect, so a half-row at the edge
        still behaves. Items entirely outside are skipped so a long
        list costs no draw time for what nobody sees.
        """
        y = list_top + self.offset
        for item in items:
            h = height_of(item)
            item_top, item_bottom = y, y - h
            y -= h
            if item_bottom >= list_top or item_top <= list_bottom:
                continue
            yield item, item_top, item_bottom
