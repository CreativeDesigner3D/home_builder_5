"""The drawings preview's on-screen controls.

Three groups of buttons, drawn like the rest of the viewport HUD:

- down the left, the page list: each room, and the sheets of that room
  under it,
- a bar at the bottom centre (previous / next sheet, fit, read again,
  print, reset, close),
- a small toolbar over the view that is selected on the sheet, with
  what can be done to that view (its scale, its place, its sections).

`layout(st, area)` is the one description of what is on screen: a list
of (id, rect, label, state) in region pixels, used both to draw and to
find what is under the cursor, so the two can never disagree.
"""

import blf
import gpu
from gpu_extras.batch import batch_for_shader

from .. import hb_gpu_ui
from ..hb_gpu_draw import (draw_glyphs, draw_lines, draw_round_rect,
                           draw_round_rect_outline, draw_soft_shadow,
                           get_visible_window_bounds, point_in_rect)
from . import sheets

Theme = hb_gpu_ui.Theme
SELECTED = (0.20, 0.52, 0.95, 1.0)
HOVERED = (0.20, 0.52, 0.95, 0.45)
FONT = 12.0
BUTTON = 28.0
GAP = 3.0

# What each button says when the cursor rests on it.
HINTS = {
    'PREV': "Previous sheet", 'NEXT': "Next sheet",
    'FIT': "Fit the sheet in the view",
    'REFRESH': "Read the model again",
    'PRINT': "Write the sheets to a PDF and open it",
    'RESET': "Put every sheet back to the automatic layout",
    'CLOSE': "Back to the 3D model",
    'SCALE_DOWN': "Draw this view at the next smaller scale",
    'SCALE_UP': "Draw this view at the next larger scale",
    'HOME': "Put this view back where the layout placed it",
    'ADD_CUT': "Then click on the elevation where the section should cut",
    'REMOVE': "Take this section off the drawings",
    'TOGETHER': "Keep this wall's sections on its elevation's sheet, "
                "or on sheets of their own",
    'ADD_NOTE': "Then click on the view where the note should go",
    'NOTE_EDIT': "Type this note again",
    'NOTE_LEADER': "Point this note at something, or take its leader off",
    'NOTE_REMOVE': "Take this note off the drawing",
}


def _s():
    try:
        return hb_gpu_ui.scale()
    except Exception:
        return 1.0


def _wide(label, s, pad=22.0):
    blf.size(0, FONT * s)
    return blf.dimensions(0, label)[0] + pad * s


def _row(items, x_centre, y, s):
    """Lay (id, label, width, state) out in a row centred on x_centre."""
    total = sum(w for _i, _l, w, _st in items) + GAP * s * (len(items) - 1)
    x = x_centre - total / 2.0
    out = []
    for ident, label, w, state in items:
        out.append((ident, (x, y, w, BUTTON * s), label, state))
        x += w + GAP * s
    return out


def selected_item(st):
    """The placed view that is selected, on the sheet on show."""
    key = st.get('selected')
    placed = st.get('placed') or []
    if not key or st['page'] >= len(placed):
        return None
    return next((it for it in placed[st['page']] if it['key'] == key), None)


def view_rect(st, item):
    """A placed view's box in region pixels (x, y, w, h)."""
    rect = st.get('rect')
    if rect is None:
        return None
    x, y, f = rect
    bx0, by0, bx1, by1 = item['box']
    return (x + bx0 * f, y + by0 * f, (bx1 - bx0) * f, (by1 - by0) * f)


def _bar(st, bounds, scene, s):
    xmin, xmax, ymin, _ymax = bounds
    count = len(st.get('compiled') or ())
    names = st.get('names') or []
    title = "No sheets"
    if count:
        name = names[st['page']] if st['page'] < len(names) else ""
        rooms = st.get('rooms') or []
        if len(set(rooms)) > 1 and st['page'] < len(rooms):
            name = f"{rooms[st['page']]} - {name}"
        title = f"{st['page'] + 1} of {count}   {name}".rstrip()
    items = []
    if count > 1:
        items.append(('PREV', None, BUTTON * s, None))
    items.append(('TITLE', title, _wide(title, s, 28.0), 'TITLE'))
    if count > 1:
        items.append(('NEXT', None, BUTTON * s, None))
    for ident, label in (('FIT', "Fit"), ('REFRESH', "Refresh"),
                         ('PRINT', "Print PDF")):
        items.append((ident, label, _wide(label, s), None))
    if scene is not None and sheets.has_layout_edits(scene):
        items.append(('RESET', "Reset Layout", _wide("Reset Layout", s),
                      None))
    items.append(('CLOSE', "Close", _wide("Close", s), None))
    return _row(items, (xmin + xmax) / 2.0, ymin + 16 * s, s)


LIST_W = 190.0              # the page list down the left
ROW_H = 24.0
HEAD_H = 26.0


def list_width(st):
    """Pixels the page list takes from the left of the view, gap
    included: none when there is only one sheet."""
    if len(st.get('names') or ()) < 2:
        return 0.0
    return (LIST_W + 20.0) * _s()


def _fit_label(label, room, s):
    blf.size(0, FONT * s)
    if blf.dimensions(0, label)[0] <= room:
        return label
    while label and blf.dimensions(0, label + "...")[0] > room:
        label = label[:-1]
    return label + "..."


def _pages(st, bounds, s):
    """The page list: each room's name, the sheets of that room under
    it. It scrolls (st['list_scroll']) when the set is longer than the
    view, keeping the sheet on show in sight."""
    xmin, _xmax, ymin, ymax = bounds
    names = st.get('names') or []
    if len(names) < 2:
        return []
    rooms = st.get('rooms') or [''] * len(names)
    order = list(dict.fromkeys(rooms))
    x, w = xmin + 10 * s, LIST_W * s
    rows = []                   # (ident, label, height, state)
    for room in order:
        if len(order) > 1:
            rows.append((('ROOM', room), room.upper(), HEAD_H * s, 'HEAD'))
        for i, name in enumerate(names):
            if rooms[i] == room:
                rows.append((('TAB', i), f"{i + 1}   {name}", ROW_H * s,
                             'ROW_ON' if i == st['page'] else 'ROW'))
    top = ymax - 10 * s
    bottom = ymin + (BUTTON + 40) * s
    room = top - bottom
    total = sum(h for _i, _l, h, _st in rows)
    scroll = min(max(st.get('list_scroll', 0.0), 0.0),
                 max(0.0, total - room))
    # The sheet on show is kept in sight, unless the list was scrolled
    # since it came up.
    if st.get('list_page') != st['page']:
        st['list_page'], st['list_free'] = st['page'], False
    y = 0.0
    for ident, _label, h, state in rows:
        if state == 'ROW_ON' and not st.get('list_free'):
            if y < scroll:
                scroll = y
            elif y + h > scroll + room:
                scroll = y + h - room
        y += h
    st['list_scroll'] = scroll
    out = [('PANEL', (x - 4 * s, max(bottom, top - total) - 4 * s,
                      w + 8 * s, min(room, total) + 8 * s), None, 'LABEL')]
    y = top + scroll
    for ident, label, h, state in rows:
        y -= h
        if y < bottom - 1 or y + h > top + 1:
            continue
        pad = 10 * s
        out.append((ident, (x, y, w, h - 2 * s),
                    _fit_label(label, w - 2 * pad, s), state))
    return out


LIST_STATES = ('HEAD', 'ROW', 'ROW_ON')


def _draw_list(shader, listed, hover, s):
    """The page list's rows: the sheet on show lit, the room names
    small over their sheets, the text from the left."""
    for ident, (rx, ry, rw, rh), label, state in listed:
        hovered = hover == ident
        if state == 'ROW_ON':
            shader.bind()
            draw_round_rect(shader, rx, ry, rw, rh, 4 * s, Theme.ACCENT_BG)
        elif hovered:
            shader.bind()
            draw_round_rect(shader, rx, ry, rw, rh, 4 * s,
                            Theme.BTN_HOVER_BG)
        size = FONT * s * (0.85 if state == 'HEAD' else 1.0)
        blf.size(0, size)
        th = blf.dimensions(0, "Ag")[1]
        bright = hovered or state == 'ROW_ON'
        blf.color(0, *(Theme.TEXT_PRIMARY if bright else Theme.TEXT_NORMAL))
        pad = (8 if state == 'HEAD' else 14) * s
        y = ry + (rh - th) / 2.0 + 1
        if state == 'HEAD':
            y = ry + 4 * s
        blf.position(0, rx + pad, y, 0)
        draw_glyphs(0, label)


def over_list(st, area, mx, my):
    """True when (mx, my) is over the page list."""
    for ident, rect, _label, _state in _pages(
            st, get_visible_window_bounds(area), _s()):
        if ident == 'PANEL':
            return point_in_rect(mx, my, rect)
    return False


def selected_note(st):
    """The note that is selected, on the sheet on show."""
    sel = st.get('note_sel')
    notes = st.get('notes') or []
    if not sel or st['page'] >= len(notes):
        return None
    return next((n for n in notes[st['page']]
                 if n['view']['key'] == sel[0] and n['index'] == sel[1]),
                None)


def sheet_rect(st, box):
    """A box in sheet points as (x, y, w, h) in region pixels."""
    rect = st.get('rect')
    if rect is None:
        return None
    x, y, f = rect
    return (x + box[0] * f, y + box[1] * f, (box[2] - box[0]) * f,
            (box[3] - box[1]) * f)


def _note_tools(st, bounds, s):
    entry = selected_note(st)
    box = sheet_rect(st, entry['box']) if entry else None
    if box is None or st.get('typing'):
        return []
    leader = "Remove Leader" if entry.get('tip') else "Add Leader"
    items = [('NOTE_EDIT', "Edit Text", _wide("Edit Text", s), None),
             ('NOTE_LEADER', leader, _wide(leader, s),
              'ON' if st.get('pick') == 'TIP' else None),
             ('NOTE_REMOVE', "Remove Note", _wide("Remove Note", s), None)]
    xmin, xmax, ymin, ymax = bounds
    total = sum(w for _i, _l, w, _st in items) + GAP * s * (len(items) - 1)
    cx = min(max(box[0] + box[2] / 2.0, xmin + total / 2.0 + 8 * s),
             xmax - total / 2.0 - 8 * s)
    y = min(box[1] + box[3] + 10 * s, ymax - (3 * BUTTON + 30) * s)
    return _row(items, cx, y, s)


def _tools(st, bounds, scene, s):
    """The toolbar of the selected view, over the view."""
    if st.get('note_sel'):
        return _note_tools(st, bounds, s)
    item = selected_item(st)
    box = view_rect(st, item) if item else None
    if box is None:
        return []
    items = []
    n = item.get('n')
    if n in sheets.SCALE_TEXT:
        text = sheets.SCALE_TEXT[n] + " = 1'"
        items += [('SCALE_DOWN', "-", BUTTON * s, None),
                  ('SCALE', text, _wide(text, s, 16.0), 'LABEL'),
                  ('SCALE_UP', "+", BUTTON * s, None)]
    kept = sheets.edits(scene) if scene is not None else None
    if kept and item['key'] in kept['moved']:
        items.append(('HOME', "Reset Position",
                      _wide("Reset Position", s), None))
    wall = item.get('wall')
    if item['kind'] == 'ELEVATION':
        items.append(('ADD_CUT', "+ Section", _wide("+ Section", s),
                      'ON' if st.get('pick') == 'CUT' else None))
    if item['kind'] == 'SECTION':
        items.append(('REMOVE', "Remove Section",
                      _wide("Remove Section", s), None))
    if wall and item['kind'] in ('ELEVATION', 'SECTION') and kept is not None:
        label = ("Sections on Own Sheet" if kept['together'].get(wall)
                 else "Sections on This Sheet")
        if item['kind'] == 'SECTION' and not kept['together'].get(wall):
            label = "Sections with Elevation"
        items.append(('TOGETHER', label, _wide(label, s), None))
    if item.get('k') and item.get('origin'):
        items.append(('ADD_NOTE', "+ Note", _wide("+ Note", s),
                      'ON' if st.get('pick') == 'NOTE' else None))
    if not items:
        return []
    xmin, xmax, ymin, ymax = bounds
    bx, by, bw, bh = box
    total = sum(w for _i, _l, w, _st in items) + GAP * s * (len(items) - 1)
    cx = min(max(bx + bw / 2.0, xmin + total / 2.0 + 8 * s),
             xmax - total / 2.0 - 8 * s)
    top_limit = ymax - (BUTTON + 20) * s
    y = by + bh + 10 * s
    if y > top_limit:
        y = max(ymin + (BUTTON + 30) * s, min(top_limit, by + bh - 40 * s))
    return _row(items, cx, y, s)


def layout(st, area, scene=None):
    if area is None:
        return []
    s = _s()
    bounds = get_visible_window_bounds(area)
    # The page list last: hit() takes the first thing under the cursor,
    # and its panel stands behind its rows.
    pages = _pages(st, bounds, s)
    return ([p for p in pages if p[0] != 'PANEL']
            + _bar(st, bounds, scene, s) + _tools(st, bounds, scene, s)
            + [p for p in pages if p[0] == 'PANEL'])


def hit(st, area, scene, mx, my):
    """The id of the button at a region point, or None. Labels (the
    sheet's name, the scale's text) are not buttons."""
    for ident, rect, _label, state in layout(st, area, scene):
        if state in ('TITLE', 'LABEL'):
            if point_in_rect(mx, my, rect):
                return 'LABEL'          # over the HUD, but nothing to press
            continue
        if point_in_rect(mx, my, rect):
            return ident
    return None


def _outline(shader, rect, color, width):
    x, y, w, h = rect
    gpu.state.line_width_set(width)
    shader.uniform_float('color', color)
    batch_for_shader(shader, 'LINE_LOOP', {'pos': [
        (x, y), (x + w, y), (x + w, y + h), (x, y + h)]}).draw(shader)
    gpu.state.line_width_set(1.0)


def draw(st, area, scene):
    """Outlines of the hovered and selected views, then the buttons."""
    s = _s()
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    placed = st.get('placed') or []
    on_sheet = placed[st['page']] if st['page'] < len(placed) else []
    hover_key = st.get('hover_view')
    for item in on_sheet:
        rect = view_rect(st, item)
        if rect is None:
            continue
        pad = 5 * s
        grown = (rect[0] - pad, rect[1] - pad, rect[2] + 2 * pad,
                 rect[3] + 2 * pad)
        if item['key'] == st.get('selected'):
            _outline(shader, grown, SELECTED, 2.0)
        elif item['key'] == hover_key and not st.get('move'):
            _outline(shader, grown, HOVERED, 1.0)
    # The selected note: its text boxed, a handle on its leader's tip.
    entry = selected_note(st)
    if entry is not None and not st.get('typing'):
        rect = sheet_rect(st, entry['box'])
        if rect is not None:
            pad = 3 * s
            _outline(shader, (rect[0] - pad, rect[1] - pad,
                              rect[2] + 2 * pad, rect[3] + 2 * pad),
                     SELECTED, 2.0)
        if entry.get('tip'):
            x, y, f = st['rect']
            tx, ty = x + entry['tip'][0] * f, y + entry['tip'][1] * f
            h = 4 * s
            shader.bind()
            draw_round_rect(shader, tx - h, ty - h, 2 * h, 2 * h, h,
                            SELECTED)
    typing = st.get('typing')
    if typing and st.get('rect'):
        _draw_typing(shader, st, typing, s)
    parts = layout(st, area, scene)
    hover = st.get('hover')
    for ident, rect, _label, _state in parts:
        if ident == 'PANEL':
            shader.bind()
            draw_soft_shadow(shader, *rect, 6 * s)
            draw_round_rect(shader, *rect, 6 * s, Theme.BTN_BG)
    parts = [p for p in parts if p[0] != 'PANEL']
    listed = [p for p in parts if p[3] in LIST_STATES]
    parts = [p for p in parts if p[3] not in LIST_STATES]
    _draw_list(shader, listed, hover, s)
    # One soft shadow under each row of buttons.
    rows = {}
    for _ident, rect, _label, _state in parts:
        rows.setdefault(round(rect[1]), []).append(rect)
    for rects in rows.values():
        x0 = min(r[0] for r in rects)
        x1 = max(r[0] + r[2] for r in rects)
        draw_soft_shadow(shader, x0, rects[0][1], x1 - x0, rects[0][3],
                         6 * s)
    hint = None
    for ident, rect, label, state in parts:
        rx, ry, rw, rh = rect
        hovered = hover == ident and state not in ('TITLE', 'LABEL')
        if state in ('TITLE', 'ON'):
            bg = Theme.ACCENT_BG
        elif state == 'LABEL':
            bg = Theme.NEUTRAL_BG
        else:
            bg = Theme.BTN_HOVER_BG if hovered else Theme.BTN_BG
        shader.bind()
        draw_round_rect(shader, rx, ry, rw, rh, 5 * s, bg)
        if state is None or state == 'ON':
            draw_round_rect_outline(shader, rx, ry, rw, rh, 5 * s,
                                    Theme.BTN_BORDER)
        if ident in ('PREV', 'NEXT'):
            cx, cy = rx + rw / 2.0, ry + rh / 2.0
            a = 4 * s
            d = -1 if ident == 'PREV' else 1
            draw_lines(shader, [(cx - d * a * 0.6, cy + a),
                                (cx + d * a * 0.6, cy),
                                (cx + d * a * 0.6, cy),
                                (cx - d * a * 0.6, cy - a)],
                       Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
        elif label:
            blf.size(0, FONT * s)
            tw = blf.dimensions(0, label)[0]
            th = blf.dimensions(0, "Ag")[1]
            bright = hovered or state in ('TITLE', 'ON')
            blf.color(0, *(Theme.TEXT_PRIMARY if bright
                           else Theme.TEXT_NORMAL))
            blf.position(0, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0 + 1,
                         0)
            draw_glyphs(0, label)
        if hovered:
            key = ident if isinstance(ident, str) else None
            if key in HINTS:
                hint = (rect, HINTS[key])
    banner = None
    if st.get('typing'):
        banner = ("Type the note.  Enter: done   Shift+Enter: new line   "
                  "Esc: cancel")
    elif st.get('pick') == 'NOTE':
        banner = "Click on the view where the note should go"
    elif st.get('pick') == 'TIP':
        banner = "Click on what the note should point at"
    elif st.get('pick') == 'CUT':
        banner = "Click on the elevation where the section should cut"
    elif st.get('note'):
        banner = st['note']
    if banner:
        xmin, xmax, ymin, _ymax = get_visible_window_bounds(area)
        blf.size(0, 11 * s)
        tw = blf.dimensions(0, banner)[0]
        blf.color(0, *(Theme.TEXT_PRIMARY if st.get('pick')
                       or st.get('typing') else Theme.TEXT_NORMAL))
        blf.position(0, (xmin + xmax) / 2.0 - tw / 2.0,
                     ymin + (BUTTON + 26) * s, 0)
        draw_glyphs(0, banner)
    if hint is not None:
        _draw_hint(shader, hint[0], hint[1], s, area)
    gpu.state.blend_set('NONE')


def _draw_hint(shader, rect, text, s, area):
    rx, ry, rw, rh = rect
    xmin, xmax, _ymin, ymax = get_visible_window_bounds(area)
    blf.size(0, 11 * s)
    tw = blf.dimensions(0, text)[0]
    th = blf.dimensions(0, "Ag")[1]
    w, h = tw + 14 * s, th + 10 * s
    x = min(max(rx + (rw - w) / 2.0, xmin + 4 * s), xmax - w - 4 * s)
    y = ry + rh + 6 * s
    if y + h > ymax:
        y = ry - h - 6 * s
    shader.bind()
    draw_soft_shadow(shader, x, y, w, h, 4 * s)
    draw_round_rect(shader, x, y, w, h, 4 * s, Theme.BTN_BG)
    blf.color(0, *Theme.TEXT_PRIMARY)
    blf.position(0, x + 7 * s, y + (h - th) / 2.0 + 1, 0)
    draw_glyphs(0, text)


def _draw_typing(shader, st, typing, s):
    """The note being typed: a field on the sheet where it will stand,
    at the size it will print at this zoom."""
    x, y, f = st['rect']
    ax, ay = x + typing['at'][0] * f, y + typing['at'][1] * f
    size = max(9.0 * s, 6.5 * f)
    rows = (typing['text'] + "|").split('\n')
    blf.size(0, size)
    w = max(max(blf.dimensions(0, r)[0] for r in rows), 60 * s) + 12 * s
    step = size * 1.3
    h = step * len(rows) + 8 * s
    bx, by = ax - 6 * s, ay - h / 2.0
    shader.bind()
    draw_soft_shadow(shader, bx, by, w, h, 4 * s)
    draw_round_rect(shader, bx, by, w, h, 4 * s, (1.0, 1.0, 1.0, 1.0))
    draw_round_rect_outline(shader, bx, by, w, h, 4 * s, SELECTED)
    blf.color(0, 0.0, 0.0, 0.0, 1.0)
    for i, row in enumerate(rows):
        blf.position(0, bx + 6 * s, by + h - 4 * s - step * (i + 1)
                     + size * 0.3, 0)
        draw_glyphs(0, row)
