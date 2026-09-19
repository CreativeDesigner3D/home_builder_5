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
import gpu

from .hb_gpu_draw import (
    draw_rect,
    draw_rect_outline,
    draw_lines,
    draw_glyphs,
    draw_text,
    vcenter_baseline,
    point_in_rect,
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
    draw_glyphs(font_id, text)


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

# ---- Clipping ---------------------------------------------------------------

def begin_clip(rect):
    """Restrict drawing to `rect`, returning the box to give end_clip.

    Rounds the box OUTWARD, which is the whole point of having this in
    one place. Panel geometry lands on half pixels, and a box truncated
    inward loses the pixel column that the rect's own right-hand border
    is drawn in -- so a bordered button sized flush with a panel's
    content width came out with no right edge at all. Rounding out puts
    the slack inside the panel's padding, where nothing else draws.

    `rect` is region-local; gpu scissor coords are framebuffer-relative,
    so it is offset by whatever box is already current (the region's own)
    and that box is what gets restored.
    """
    prev = gpu.state.scissor_get()
    x, y, w, h = rect
    x0 = int(math.floor(prev[0] + x))
    y0 = int(math.floor(prev[1] + y))
    # floor + 1, not ceil. A far edge on a whole pixel -- which is what a
    # button sized to the content width gives -- draws its border line IN
    # that pixel, and ceil() of a whole number lands one short of it. The
    # tab strip happened to sit on half pixels, which is why it looked
    # fixed and the panel rows did not.
    x1 = int(math.floor(prev[0] + x + w)) + 1
    y1 = int(math.floor(prev[1] + y + h)) + 1
    gpu.state.scissor_test_set(True)
    gpu.state.scissor_set(x0, y0, max(x1 - x0, 0), max(y1 - y0, 0))
    return prev


def end_clip(prev):
    """Undo begin_clip. Always pair them in a finally."""
    gpu.state.scissor_set(*prev)
    gpu.state.scissor_test_set(False)


def paint_frame(shader, rect, bg=Theme.PANEL_BG, border=Theme.PANEL_BORDER):
    """Filled panel background plus its 1px border."""
    x, y, w, h = rect
    draw_rect(shader, x, y, w, h, bg)
    if border is not None:
        draw_rect_outline(shader, x, y, w, h, border)


def paint_button(shader, rect, hovered=False, active=False,
                 bg=Theme.BTN_BG, hover_bg=Theme.BTN_HOVER_BG,
                 active_bg=Theme.BTN_ACTIVE_BG, border=Theme.PANEL_BORDER):
    """The fill-then-border button idiom, with active winning over hover.

    Returns the fill colour used, so a caller can pick a matching glyph
    or label colour without repeating the same three-way choice.

    The border defaults to the PANEL edge, not the louder button edge.
    A button sitting ON a dark viewport wants to announce itself; a row
    of them inside a panel does not, and at panel density the brighter
    edge reads as a grid of white boxes. The HUD passes BTN_BORDER
    explicitly for the buttons that do float on the viewport.
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


# ---- Inline text editing ----------------------------------------------------

def _prefix_width(font_id, size, text):
    """Width of `text` as the start of a longer line. Measured with a
    sentinel after it, because a trailing space has no ink and would
    otherwise measure as nothing -- and the caret would not move when
    a space is typed."""
    return (text_width(font_id, size, text + ".")
            - text_width(font_id, size, "."))


def begin_clip_nested(rect):
    """begin_clip for use INSIDE another clip: the box is the part of
    `rect` that is also inside the clip already current, and that
    current box is what end_clip_nested puts back. begin_clip cannot
    nest, because it reads the current box as the region's origin."""
    prev = gpu.state.scissor_get()
    origin = gpu.state.viewport_get()
    x, y, w, h = rect
    x0 = max(int(math.floor(origin[0] + x)), prev[0])
    y0 = max(int(math.floor(origin[1] + y)), prev[1])
    x1 = min(int(math.floor(origin[0] + x + w)) + 1, prev[0] + prev[2])
    y1 = min(int(math.floor(origin[1] + y + h)) + 1, prev[1] + prev[3])
    gpu.state.scissor_test_set(True)
    gpu.state.scissor_set(x0, y0, max(x1 - x0, 0), max(y1 - y0, 0))
    return prev


def end_clip_nested(prev):
    gpu.state.scissor_set(*prev)


def paint_inline_edit(shader, font_id, rect, size, edit, pad=0.0):
    """The text of an InlineEdit inside `rect`: its selection, the text,
    and the caret. A text longer than the field scrolls sideways to keep
    the cursor in view, clipped to the field. Records where it painted
    on the edit, so a mouse position can be turned back into a
    character. `pad` is scaled."""
    s = scale()
    x, y, w, h = rect
    avail = max(w - 2 * pad, 1.0)
    room = max(avail - 2 * s, 1.0)      # leaves the caret inside the clip
    text = edit.text
    cx = _prefix_width(font_id, size, edit.before())
    total = _prefix_width(font_id, size, text)
    scroll = edit.scroll_x
    if cx < scroll:
        scroll = cx
    elif cx > scroll + room:
        scroll = cx - room
    scroll = max(0.0, min(scroll, max(total - room, 0.0)))
    edit.scroll_x = scroll
    x0 = x + pad - scroll
    edit.layout = (font_id, size, x0, rect)
    prev = begin_clip_nested((x + pad - 1 * s, y, avail + 2 * s, h))
    try:
        rng = edit.sel_range()
        if rng is not None:
            ax = _prefix_width(font_id, size, text[:rng[0]])
            bx = _prefix_width(font_id, size, text[:rng[1]])
            draw_rect(shader, x0 + ax, y + 3 * s, bx - ax, h - 6 * s,
                      Theme.ACCENT_BG)
        draw_text(font_id, x0, vcenter_baseline(rect, font_id, size), size,
                  Theme.TEXT_PRIMARY, text)
        if rng is None:
            draw_rect(shader, x0 + cx, y + 4 * s, 1.5 * s, h - 8 * s,
                      Theme.TEXT_PRIMARY)
    finally:
        end_clip_nested(prev)


class InlineEdit:
    """A one-line text field for a row of a GPU panel.

    Owns the buffer and the keystroke grammar; the caller owns what is
    being edited and what committing means. `key` is whatever the caller
    recognises a row by -- a scene name, a list index -- and is handed
    back on commit so it does not have to remember separately.

    Lifted here when the second panel needed it. The typing grammar is
    small but it is exactly the kind of thing that drifts: one copy
    handling Backspace and another not is how two lists that look
    identical stop behaving identically.

    The grammar: a cursor moved by the arrows, Home and End, which
    select with Shift held; Backspace and Delete; Ctrl+A, C, X and V;
    any printable character, not only ASCII; and the mouse -- a press
    places the cursor, a drag selects, a double click takes the word.
    paint_inline_edit draws it.
    """

    def __init__(self):
        self.key = None
        self.text = ''
        self.cursor = 0
        # The other end of the selection, or None. What is selected is
        # whatever lies between it and the cursor.
        self.anchor = None
        # Sideways scroll of a text longer than its field, and where the
        # field was last painted -- kept for paint_inline_edit and for
        # turning a mouse position back into a character.
        self.scroll_x = 0.0
        self.layout = None
        self.dragging = False

    def begin(self, key, text='', select=False):
        """Start editing `key` from `text`, the cursor at its end. With
        `select` the whole of it starts selected, so typing replaces it
        and an arrow key keeps it -- what clicking into a field does."""
        self.key = key
        self.text = text
        self.cursor = len(text)
        self.anchor = 0 if (select and text) else None
        self.scroll_x = 0.0
        self.layout = None
        self.dragging = False

    def cancel(self):
        self.begin(None)

    @property
    def active(self):
        return self.key is not None

    def editing(self, key):
        """Whether THIS row is the one being edited."""
        return self.key is not None and self.key == key

    def sel_range(self):
        """(start, end) of the selection, or None when nothing is."""
        if self.anchor is None or self.anchor == self.cursor:
            return None
        return (min(self.anchor, self.cursor), max(self.anchor, self.cursor))

    @property
    def selected(self):
        return self.sel_range() is not None

    def before(self):
        """The text left of the cursor -- what a caller measures to put
        a caret of its own in the right place."""
        return self.text[:self.cursor]

    def display(self, caret="|"):
        """The text with the caret in it, for a caller that draws the
        edit as one string; none while there is a selection."""
        if self.selected:
            return self.text
        return self.text[:self.cursor] + caret + self.text[self.cursor:]

    def _delete_selection(self):
        rng = self.sel_range()
        self.anchor = None
        if rng is None:
            return False
        self.text = self.text[:rng[0]] + self.text[rng[1]:]
        self.cursor = rng[0]
        return True

    def _insert(self, chars):
        self._delete_selection()
        self.text = (self.text[:self.cursor] + chars
                     + self.text[self.cursor:])
        self.cursor += len(chars)

    def _move(self, index, extend):
        """Put the cursor at `index`; with `extend` (Shift, or a drag)
        the selection stretches to it from where it started."""
        if extend:
            if self.anchor is None:
                self.anchor = self.cursor
        else:
            self.anchor = None
        self.cursor = min(max(index, 0), len(self.text))

    def _word_bounds(self, index):
        text = self.text
        index = min(max(index, 0), len(text))
        a = b = index
        while a > 0 and not text[a - 1].isspace():
            a -= 1
        while b < len(text) and not text[b].isspace():
            b += 1
        return a, b

    # ---- Mouse ----

    def index_at(self, px):
        """The character boundary nearest region x `px`, by where the
        text was last painted; the end of the text when it has not
        been."""
        if self.layout is None:
            return len(self.text)
        font_id, size, x0, _rect = self.layout
        rel = px - x0
        best, best_d = 0, None
        for i in range(len(self.text) + 1):
            d = abs(_prefix_width(font_id, size, self.text[:i]) - rel)
            if best_d is None or d < best_d:
                best, best_d = i, d
        return best

    def contains(self, mx, my):
        """Whether a region point is inside the painted field."""
        return (self.layout is not None
                and point_in_rect(mx, my, self.layout[3]))

    def mouse(self, event, mx, my):
        """Take one mouse event with its region position. True when the
        edit used it; False for a press outside the field, which the
        caller treats as the field losing focus. A press places the
        cursor (Shift extends), a drag selects, a double click takes
        the word."""
        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                was, self.dragging = self.dragging, False
                return was
            if not self.contains(mx, my):
                return False
            index = self.index_at(mx)
            if event.value == 'DOUBLE_CLICK':
                self.anchor, self.cursor = self._word_bounds(index)
                self.dragging = False
            elif event.value == 'PRESS':
                self._move(index, event.shift)
                if self.anchor is None:
                    self.anchor = self.cursor
                self.dragging = True
            return True
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            if self.dragging:
                self.cursor = self.index_at(mx)
                return True
        return False

    # ---- Keys ----

    def feed(self, event):
        """Take one key event. Returns 'COMMIT', 'CANCEL', 'NEXT' or
        'PREV' (Tab and Shift+Tab, for a caller with a next field to go
        to), or None while the user is still typing."""
        if event.value != 'PRESS':
            return None
        kind = event.type
        if kind in {'RET', 'NUMPAD_ENTER'}:
            return 'COMMIT'
        if kind == 'ESC':
            return 'CANCEL'
        if kind == 'TAB':
            return 'PREV' if event.shift else 'NEXT'
        rng = self.sel_range()
        if event.ctrl or event.oskey:
            if kind == 'A':
                self.anchor, self.cursor = 0, len(self.text)
            elif kind in {'C', 'X'}:
                # With nothing selected, the whole value.
                bpy.context.window_manager.clipboard = (
                    self.text[rng[0]:rng[1]] if rng else self.text)
                if kind == 'X':
                    if rng is None:
                        self.anchor, self.cursor = 0, len(self.text)
                    self._delete_selection()
            elif kind == 'V':
                pasted = bpy.context.window_manager.clipboard or ''
                line = pasted.splitlines()[0] if pasted.strip() else ''
                self._insert(''.join(c for c in line if c.isprintable()))
            return None
        if kind in {'LEFT_ARROW', 'RIGHT_ARROW'}:
            step = -1 if kind == 'LEFT_ARROW' else 1
            if rng and not event.shift:
                # An arrow collapses a selection to the end it points at.
                self._move(rng[0] if step < 0 else rng[1], False)
            else:
                self._move(self.cursor + step, event.shift)
        elif kind == 'HOME':
            self._move(0, event.shift)
        elif kind == 'END':
            self._move(len(self.text), event.shift)
        elif kind in {'BACK_SPACE', 'DEL'}:
            if not self._delete_selection():
                if kind == 'BACK_SPACE' and self.cursor > 0:
                    self.text = (self.text[:self.cursor - 1]
                                 + self.text[self.cursor:])
                    self.cursor -= 1
                elif kind == 'DEL':
                    self.text = (self.text[:self.cursor]
                                 + self.text[self.cursor + 1:])
        else:
            char = event.unicode or event.ascii
            if char and char.isprintable() and not event.alt:
                self._insert(char)
        return None

    def take(self):
        """(key, stripped text), with the edit cleared."""
        key, text = self.key, self.text.strip()
        self.cancel()
        return key, text


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

    def __init__(self, bar_width=4, bar_pad=4, min_rows=3, show_bar=True):
        self.offset = 0.0
        self.bar_width = bar_width      # unscaled
        self.bar_pad = bar_pad          # unscaled
        self.min_rows = min_rows
        # A list can scroll without advertising it. One flag covers both
        # halves of that: no bar drawn AND no width reserved for one --
        # reserving space for something invisible just narrows the
        # content for no reason.
        self.show_bar = show_bar

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
        reserve = ((self.bar_width + self.bar_pad) * s
                   if self.show_bar else 0.0)
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
        when the content fits or the bar is hidden. Assumes the offset is
        already clamped."""
        if content_h <= list_h or not self.show_bar:
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


# ---- Form widgets -----------------------------------------------------------
# The pieces a settings page repeats: a labelled value that opens a
# picker, and a checkbox. Both are painted here and hit-tested by the
# caller against the rect this returns, so pixels and hits cannot drift.

def glyph_caret(shader, cx, cy, size, up, color):
    """Chevron pointing up or down, centred at (cx, cy). The disclosure
    chevron's shape stood on end; `size` is pre-scaled."""
    h = size / 2.0
    if up:
        pts = [(cx - h, cy - h / 2.0), (cx, cy + h / 2.0),
               (cx, cy + h / 2.0), (cx + h, cy - h / 2.0)]
    else:
        pts = [(cx - h, cy + h / 2.0), (cx, cy - h / 2.0),
               (cx, cy - h / 2.0), (cx + h, cy + h / 2.0)]
    draw_lines(shader, pts, color)


def glyph_check(shader, rect, color):
    """A tick inside `rect` (pre-scaled)."""
    x, y, w, h = rect
    pts = [(x + w * 0.22, y + h * 0.50), (x + w * 0.42, y + h * 0.28),
           (x + w * 0.42, y + h * 0.28), (x + w * 0.80, y + h * 0.74)]
    draw_lines(shader, pts, color)


def paint_field(shader, font_id, rect, size, label, value, hovered,
                label_frac=0.42, pad=6.0, caret=True, active=False,
                text_inset=0.0, enabled=True):
    """A labelled value: the label at the left, the current value in a
    button on the right. With `caret` it says it drops down; without,
    it is a value you click into and type (`active` while typing).
    `text_inset` shifts the value text right, for a picture drawn in
    front of it by the caller. Not `enabled`, it is a value to read and
    not to change: greyed, flat, and deaf to the pointer. Returns the value button's rect -- the
    part a click means something on. `size` is the scaled font size;
    `pad` unscaled, `text_inset` scaled."""
    s = scale()
    x, y, w, h = rect
    label_w = w * label_frac
    value_rect = (x + label_w, y + 2 * s, w - label_w, h - 4 * s)
    if not enabled:
        hovered = active = False
    draw_text(font_id, x + pad * s, vcenter_baseline(rect, font_id, size),
              size, Theme.TEXT_NORMAL if enabled else Theme.TEXT_DIM,
              fit_text(font_id, size, label, label_w - pad * s))
    if enabled:
        paint_button(shader, value_rect, hovered=hovered, active=active)
    else:
        # No fill: a well with only its outline reads as not pressable.
        draw_rect_outline(shader, *value_rect, Theme.PANEL_BORDER)
    vx, vy, vw, vh = value_rect
    caret_w = 7 * s if caret else 0.0
    draw_text(font_id, vx + pad * s + text_inset,
              vcenter_baseline(value_rect, font_id, size),
              size, Theme.TEXT_DIM if not enabled
              else Theme.TEXT_PRIMARY if (hovered or active)
              else Theme.TEXT_NORMAL,
              fit_text(font_id, size, value,
                       vw - caret_w - 3 * pad * s - text_inset))
    if caret:
        glyph_caret(shader, vx + vw - pad * s - caret_w / 2.0, vy + vh / 2.0,
                    caret_w, False,
                    Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
    return value_rect


def paint_check(shader, font_id, rect, size, label, checked, hovered,
                pad=6.0):
    """A checkbox row: the box at the left, the label after it. The
    whole row is the hit target, so nothing is returned."""
    s = scale()
    x, y, w, h = rect
    if hovered:
        draw_rect(shader, x, y, w, h, Theme.ROW_HOVER_BG)
    box = 12 * s
    box_rect = (x + pad * s, y + (h - box) / 2.0, box, box)
    paint_button(shader, box_rect, hovered=hovered, active=checked,
                 border=Theme.BTN_BORDER)
    if checked:
        glyph_check(shader, box_rect, Theme.GLYPH_HOVER)
    draw_text(font_id, x + (pad * 2) * s + box,
              vcenter_baseline(rect, font_id, size), size,
              Theme.TEXT_PRIMARY if hovered else Theme.TEXT_NORMAL,
              fit_text(font_id, size, label, w - box - 3 * pad * s))


# ---- Property helpers -------------------------------------------------------

def enum_items(owner, prop):
    """[(identifier, label)] for an EnumProperty on `owner`, static or
    dynamic. RNA lists a dynamic enum's items as empty, so those are
    asked of the items callback the property was declared with."""
    try:
        rna = owner.bl_rna.properties[prop]
    except (KeyError, AttributeError):
        return []
    items = [(it.identifier, it.name) for it in rna.enum_items]
    if items:
        return items
    # Assigned onto the class (the way a property is added to, or
    # replaced on, a registered type at run time -- which wins in
    # Blender too), else declared as an annotation.
    deferred = None
    for cls in type(owner).__mro__:
        deferred = (cls.__dict__.get(prop)
                    or getattr(cls, '__annotations__', {}).get(prop))
        if deferred is not None:
            break
    fn = getattr(deferred, 'keywords', {}).get('items')
    if not callable(fn):
        return []
    try:
        return [(it[0], it[1]) for it in fn(owner, bpy.context)]
    except Exception:
        return []


def enum_label(owner, prop):
    """The label of the current value of an EnumProperty."""
    value = getattr(owner, prop, '')
    for ident, label in enum_items(owner, prop):
        if ident == value:
            return label
    return str(value)
