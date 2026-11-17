"""The drawing set: sheets of placed views, as plain data.

    {'sheets': [{'views': [{'kind': 'ELEVATION', 'wall': 'Wall.001'},
                           {'kind': 'PLAN', 'wall': 'Wall.001'}]},
                {'views': [{'kind': 'SECTION', 'wall': 'Wall.001',
                            'x': 0.66}]}]}

The set is made by rule each time it is asked for, so nothing has to be
created, kept in step or cleaned up, and a wall added to the room is on
the next sheet without anyone asking. What the user changes is kept as
a short list of edits laid over the rule (a view moved, a scale chosen,
a wall's section cuts, sections kept on their elevation's sheet), keyed
to the wall they belong to, so the edits survive the rule running again.

The composer turns a sheet into one Drawing: it gives each view its
room, lines views up on each other's anchors, and adds what belongs to
the sheet rather than to a view -- titles, the marks that point from
one view to another, the border.
"""

import json

from .. import hb_pdf
from ..operators import elevation_mode as em
from . import draft, section, views
from .drawing import Drawing

PAPER = (17 * 72.0, 11 * 72.0)
MARGIN = 18.0
SET_PROP = 'HB_DRAWING_SET'
SECTION_COLUMN = 285.0      # width a section takes with its dimensions
SECTIONS_A_SHEET = 4
SECTIONS_WITH_ELEVATION = 2
SECTION_SCALES = ((12, '1"'), (16, '3/4"'), (24, '1/2"'), (32, '3/8"'))


# ---- Sheet furniture ---------------------------------------------------------
#
# What is on every sheet whatever it shows. Another add-on may draw its
# own (a title block): fn(page, context, sheet, width, height) returning
# the rectangle (x0, y0, x1, y1) left for the views. `sheet` carries
# 'number', 'count' and the sheet's own data.

_furniture = []


def register_sheet_furniture(fn):
    if fn not in _furniture:
        _furniture.append(fn)


def unregister_sheet_furniture(fn):
    if fn in _furniture:
        _furniture.remove(fn)


def _plain_furniture(page, context, sheet, width, height):
    page.stroke_color(draft.INK)
    page.line_width(1.0)
    page.rect(MARGIN, MARGIN, width - 2 * MARGIN, height - 2 * MARGIN,
              stroke=True)
    label = (f"{context.scene.name}   -   SHEET {sheet['number']} "
             f"OF {sheet['count']}")
    page.fill_color(draft.INK)
    page.text(width - MARGIN - 8.0 - hb_pdf.text_width(label, 7.0),
              MARGIN + 7.0, label, 7.0)
    return (MARGIN, MARGIN + 14.0, width - MARGIN, height - MARGIN)


# ---- The set -------------------------------------------------------------------
#
# Another add-on may add to the rule-made set (a cover sheet of its own
# view kind): fn(scene, data) changes `data` in place.

_set_extensions = []


def register_set_extension(fn):
    if fn not in _set_extensions:
        _set_extensions.append(fn)


def unregister_set_extension(fn):
    if fn in _set_extensions:
        _set_extensions.remove(fn)


def default_set(scene, room_index=0):
    """The set made by rule: for each wall with products, its plan strip
    over its elevation, then its sections on the sheets after.
    `room_index` is the room's place among the project's rooms, for an
    extension that adds something once for the whole project."""
    sheets = []
    kept = edits(scene)
    walls = [wall for wall in em.room_walls(scene)
             if any(it.kind != 'OPENING'
                    for it in views.wall_items(scene, wall))]
    # A room with products on more than one wall gets a plan of the
    # whole room; a single wall's plan strip rides over its elevation.
    whole_room = len(walls) > 1
    if whole_room:
        sheets.append({'views': [{'kind': 'ROOM_PLAN'}]})
    for wall in walls:
        on_sheet = [{'kind': 'ELEVATION', 'wall': wall.name}]
        if not whole_room:
            on_sheet.append({'kind': 'PLAN', 'wall': wall.name})
        cuts = [{'kind': 'SECTION', 'wall': wall.name, 'x': x}
                for x in _wall_cuts(scene, wall, kept)]
        if kept['together'].get(wall.name):
            on_sheet += cuts[:SECTIONS_WITH_ELEVATION]
            cuts = cuts[SECTIONS_WITH_ELEVATION:]
        sheets.append({'views': on_sheet})
        for i in range(0, len(cuts), SECTIONS_A_SHEET):
            sheets.append({'views': cuts[i:i + SECTIONS_A_SHEET]})
    data = {'sheets': sheets, 'room_index': room_index}
    for extend in list(_set_extensions):
        try:
            extend(scene, data)
        except Exception as exc:
            print(f"Drawings: set extension: {exc}")
    return data


# ---- The user's edits ----------------------------------------------------------

EDIT_KEYS = ('moved', 'scales', 'cuts', 'together')
SCALE_LADDER = (8, 12, 16, 24, 32, 48, 64, 96)      # the n of 1:n


def edits(scene):
    """{'moved': {view key: [dx, dy] in points}, 'scales': {view key: n},
    'cuts': {wall: [metres along it, ...]}, 'together': {wall: True}}."""
    try:
        data = json.loads(scene.get(SET_PROP) or '{}')
    except (TypeError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    return {k: (data.get(k) if isinstance(data.get(k), dict) else {})
            for k in EDIT_KEYS}


def store_edits(scene, data):
    if not any(data.get(k) for k in EDIT_KEYS):
        if SET_PROP in scene:
            del scene[SET_PROP]
    else:
        scene[SET_PROP] = json.dumps({k: data.get(k) or {}
                                      for k in EDIT_KEYS})


def view_key(view):
    """What an edit to a view is kept under: its kind and its wall, and
    for a section where along the wall it is cut."""
    parts = [str(view.get('kind')), str(view.get('wall') or '')]
    if view.get('kind') == 'SECTION':
        parts.append(str(int(round((view.get('x') or 0.0) * 1000))))
    return ':'.join(parts)


def _wall_cuts(scene, wall, data):
    kept = data['cuts'].get(wall.name)
    if isinstance(kept, list):
        return [float(x) for x in kept]
    return section.wall_cuts(scene, wall)


def move_view(scene, key, dx, dy):
    data = edits(scene)
    old = data['moved'].get(key) or [0.0, 0.0]
    new = [round(old[0] + dx, 2), round(old[1] + dy, 2)]
    if abs(new[0]) < 0.5 and abs(new[1]) < 0.5:
        data['moved'].pop(key, None)
    else:
        data['moved'][key] = new
    store_edits(scene, data)


def step_scale(scene, key, current, larger):
    """Draw the view one drafting scale larger or smaller than `current`
    (the n of 1:n it is drawn at now)."""
    ladder = list(SCALE_LADDER)
    i = min(range(len(ladder)), key=lambda j: abs(ladder[j] - current))
    i = max(0, min(len(ladder) - 1, i + (-1 if larger else 1)))
    data = edits(scene)
    data['scales'][key] = ladder[i]
    store_edits(scene, data)
    return ladder[i]


def add_cut(scene, wall, x, current=None):
    """Cut a section at `x` metres along `wall`. `current` is the
    wall's cuts as they stand on the sheets (so a room that is not on
    screen need not be read to find them)."""
    data = edits(scene)
    cuts = (list(current) if current is not None
            else _wall_cuts(scene, wall, data))
    if all(abs(x - c) > 0.02 for c in cuts):
        data['cuts'][wall.name] = sorted(round(c, 4) for c in cuts + [x])
        store_edits(scene, data)


def remove_cut(scene, wall, x, current=None):
    data = edits(scene)
    cuts = (list(current) if current is not None
            else _wall_cuts(scene, wall, data))
    data['cuts'][wall.name] = [round(c, 4) for c in cuts
                               if abs(c - x) > 0.002]
    store_edits(scene, data)


def toggle_together(scene, wall_name):
    """Keep a wall's sections on its elevation's sheet, or on sheets of
    their own."""
    data = edits(scene)
    if data['together'].pop(wall_name, None) is None:
        data['together'][wall_name] = True
    store_edits(scene, data)


def home_view(scene, key):
    """Put a moved view back where the layout places it."""
    data = edits(scene)
    if data['moved'].pop(key, None) is not None:
        store_edits(scene, data)


def reset_edits(scene):
    store_edits(scene, {})


def sheet_name(scene, sheet):
    """A short name for a sheet, from what is on it: 'Plan', 'Wall 2',
    'Sections S1-S3'."""
    kinds = [v.get('kind') for v in sheet.get('views', ())]
    for view in sheet.get('views', ()):
        if view.get('kind') == 'ELEVATION':
            return _wall_title(scene, view.get('wall')).title()
    if 'ROOM_PLAN' in kinds:
        return "Plan"
    marks = [v.get('_mark') for v in sheet.get('views', ())
             if v.get('kind') == 'SECTION' and v.get('_mark')]
    if marks:
        return ("Section " + marks[0] if len(marks) == 1
                else f"Sections {marks[0]}-{marks[-1]}")
    if kinds:
        return str(kinds[0]).replace('_', ' ').title()
    return "Sheet"


def drawing_set(scene, counters=None):
    """The room's set with every view marked: '_mark' (A, S1), '_sheet'
    (the sheet it is on), and on an elevation '_cuts', the sections cut
    from its wall, wherever they ended up.

    `counters` carries the numbering on from the room before, so a
    project's sheets, elevation letters and section numbers run
    through every room: {'sheets', 'letters', 'sections', 'rooms'}.
    It is moved on to where this room ends."""
    if counters is None:
        counters = {}
    first_sheet = counters.get('sheets', 0)
    first_letter = counters.get('letters', 0)
    data = default_set(scene, counters.get('rooms', 0))
    kept = edits(scene)
    sheets = [{'views': [dict(v) for v in s.get('views', [])
                         if isinstance(v, dict)]}
              for s in data['sheets']]
    for sheet in sheets:
        for view in sheet['views']:
            key = view_key(view)
            view['_key'] = key
            view['_move'] = tuple(kept['moved'].get(key) or (0.0, 0.0))
            if key in kept['scales']:
                view['scale'] = int(kept['scales'][key])
    letters, cuts = {}, {}
    n_sections = counters.get('sections', 0)
    for number, sheet in enumerate(sheets, first_sheet + 1):
        sheet['_number'] = number
        for view in sheet['views']:
            view['_sheet'] = number
            wall = view.get('wall')
            if view.get('kind') == 'ELEVATION':
                letters.setdefault(
                    wall, (_letter(first_letter + len(letters)), number))
                view['_mark'] = letters[wall][0]
            elif view.get('kind') == 'SECTION':
                n_sections += 1
                view['_mark'] = f"S{n_sections}"
                cuts.setdefault(wall, []).append(
                    (view.get('x') or 0.0, view['_mark'], number))
    for sheet in sheets:
        for view in sheet['views']:
            wall = view.get('wall')
            if view.get('kind') == 'ELEVATION':
                view['_cuts'] = cuts.get(wall, [])
            elif view.get('kind') == 'PLAN' and wall in letters:
                view['_mark'], view['_looks_from'] = letters[wall]
            elif view.get('kind') == 'ROOM_PLAN':
                view['_marks'] = dict(letters)
    counters['sheets'] = first_sheet + len(sheets)
    counters['letters'] = first_letter + len(letters)
    counters['sections'] = n_sections
    counters['rooms'] = counters.get('rooms', 0) + 1
    return sheets


def _letter(i):
    return chr(ord('A') + i % 26) * (i // 26 + 1)


# ---- Composing a sheet ---------------------------------------------------------

def _wall_title(scene, wall_name):
    names = [w.name for w in em.room_walls(scene)]
    if wall_name in names:
        return f"WALL {names.index(wall_name) + 1}"
    return str(wall_name).upper()


def _scale_text(label):
    return (label or 'NOT TO SCALE').replace('-0"', '')


def _scale_n(drawing):
    """The n of 1:n a drawing was made at."""
    k = (drawing.info or {}).get('k')
    return int(round(72.0 / 0.0254 / k)) if k else None


def _placed(page, view, drawing, x, y, origin=None):
    """Note where a view landed on the sheet, for whatever lets the
    user pick it up there."""
    bx0, by0, bx1, by1 = drawing.bounds()
    page.info.setdefault('placed', []).append({
        'key': view.get('_key'), 'kind': view.get('kind'),
        'wall': view.get('wall'), 'x': view.get('x'),
        'box': (x + bx0, y + by0, x + bx1, y + by1),
        'n': _scale_n(drawing), 'k': (drawing.info or {}).get('k'),
        'origin': origin})


SCALE_TEXT = {8: '1 1/2"', 12: '1"', 16: '3/4"', 24: '1/2"', 32: '3/8"',
              48: '1/4"', 64: '3/16"', 96: '1/8"'}


def _fit_section(context, view, height):
    """The section at the largest scale that stands in `height`, or at
    the scale the user chose for it."""
    if view.get('scale') in SCALE_TEXT:
        n = view['scale']
        drawing = views.resolve(context, dict(view, k=72.0 / 0.0254 / n),
                                0.0, 0.0)
        return drawing, f"{SCALE_TEXT[n]} = 1'"
    for n, text in SECTION_SCALES:
        k = 72.0 / 0.0254 / n
        drawing = views.resolve(context, dict(view, k=k), 0.0, 0.0)
        if drawing is None:
            return None, None
        _x0, y0, _x1, y1 = drawing.bounds()
        if y1 - y0 <= height:
            break
    return drawing, f"{text} = 1'"


def compose(context, sheets, index, count=None):
    """Sheet `index` of `sheets` (from drawing_set) as one Drawing.
    `count` is how many sheets the whole set has when these are only
    one room's part of it."""
    scene = context.scene
    width, height = PAPER
    sheet = sheets[index]
    page = Drawing(width, height)
    page.info['room'] = scene.name
    page.info['name'] = sheet_name(scene, sheet)
    info = {'number': sheet.get('_number', index + 1),
            'count': count or len(sheets), 'sheet': sheet}
    furniture = _furniture[-1] if _furniture else _plain_furniture
    x0, y0, x1, y1 = furniture(page, context, info, width, height)

    by_kind = {}
    for view in sheet['views']:
        by_kind.setdefault(view.get('kind'), []).append(view)
    sections = by_kind.get('SECTION', [])
    elevations = by_kind.get('ELEVATION', [])
    plans = by_kind.get('PLAN', [])

    # Sections stand in columns from the right; an elevation takes what
    # is left, with its plan strip over it.
    column_x = x1 - SECTION_COLUMN * len(sections)
    if not elevations:
        column_x = x0
    if elevations:
        elev = elevations[0]
        plan = next((p for p in plans if p.get('wall') == elev.get('wall')),
                    None)
        plan_room = 0.0
        if plan is not None:
            depth = plan.get('depth') or 44.0 * draft.INCH
            plan_room = depth * views.HALF_INCH_SCALE + 70.0
        e = views.resolve(context, elev, column_x - x0,
                          (y1 - y0) - plan_room)
        if e is not None:
            ex, ey = x0 + elev['_move'][0], y0 + elev['_move'][1]
            e.place(page, ex, ey)
            ax, ay = e.anchors['wall_start']
            k = e.info['k']
            _placed(page, elev, e, ex, ey, origin=(ex + ax, ey + ay))
            draft.view_title(
                page, ex + 40.0, ey + 30.0, elev['_mark'], elev['_sheet'],
                f"ELEVATION: {_wall_title(scene, elev.get('wall'))}",
                _scale_text(e.info.get('scale')),
                width=min(250.0, column_x - x0 - 80.0))
            top = e.anchors['wall_top'][1]
            for x_cut, mark, number in elev.get('_cuts', ()):
                draft.section_marker(page, ex + ax + x_cut * k,
                                     ey + top + 30.0, mark, number)
            if plan is not None:
                p = views.resolve(context, dict(plan, k=k), 0.0, 0.0)
                if p is not None:
                    px = ex + ax + plan['_move'][0]
                    py = y1 - 6.0 - p.info['top'] + plan['_move'][1]
                    p.place(page, px, py)
                    _placed(page, plan, p, px, py)
                    mx, my = p.anchors['marker']
                    draft.elevation_marker(page, px + mx, py + my,
                                           elev['_mark'], elev['_sheet'])
    for view in by_kind.get('ROOM_PLAN', [])[:1]:
        room = views.resolve(context, view, column_x - x0 if elevations
                             else x1 - x0, (y1 - y0) - 50.0)
        if room is None:
            continue
        rx, ry = x0 + view['_move'][0], y0 + 50.0 + view['_move'][1]
        room.place(page, rx, ry)
        _placed(page, view, room, rx, ry)
        draft.view_title(page, x0 + 40.0, y0 + 30.0, 'P', view['_sheet'],
                         f"PLAN: {scene.name.upper()}",
                         _scale_text(room.info.get('scale')))
        for wall_name, (mark, number) in view.get('_marks', {}).items():
            at = room.anchors.get('marker:' + wall_name)
            if at is not None:
                draft.elevation_marker_toward(
                    page, rx + at[0], ry + at[1], (at[2], at[3]),
                    mark, number)
    # Any other kind of view is sized by its own drawing: they stand in
    # a row from the top left of what the others left free.
    cursor = x0 + 22.0
    for view in sheet['views']:
        if view.get('kind') in ('ELEVATION', 'PLAN', 'SECTION',
                                'ROOM_PLAN'):
            continue
        d = views.resolve(context, view, x1 - cursor, y1 - y0)
        if d is None:
            continue
        ox, oy = cursor + view['_move'][0], (y1 - 22.0 - d.height
                                             + view['_move'][1])
        d.place(page, ox, oy)
        _placed(page, view, d, ox, oy)
        cursor += d.width + 22.0
    for i, view in enumerate(sections):
        s, scale = _fit_section(context, view, (y1 - y0) - 110.0)
        if s is None:
            continue
        wall_x = (column_x + SECTION_COLUMN * (i + 1) - 90.0
                  + view['_move'][0])
        base_y = y0 + view['_move'][1]
        s.place(page, wall_x, base_y + 92.0)
        _placed(page, view, s, wall_x, base_y + 92.0)
        draft.view_title(page, wall_x - 130.0, base_y + 26.0, view['_mark'],
                         view['_sheet'], 'SECTION', scale, width=150.0)
    return page


def compose_all(context):
    """The sheets of the room on screen alone."""
    sheets = drawing_set(context.scene)
    return [compose(context, sheets, i) for i in range(len(sheets))]


def project_rooms():
    """The project's rooms, in the order the project lists them."""
    return list(em._room_scenes())


_page_cache = {}


def compose_project(context):
    """Every room's sheets as one set: numbered straight through, the
    marks of one room carrying on from the room before. A sheet whose
    room has not changed since it was last composed is reused."""
    rooms = project_rooms()
    pages = []
    with views.showing_cages(rooms):
        counters = {}
        made = []
        for room in rooms:
            with views.in_room(context, room) as ctx:
                try:
                    made.append((room, drawing_set(ctx.scene, counters)))
                except Exception as exc:
                    print(f"Drawings: {room.name}: {exc}")
        count = counters.get('sheets', 0)
        live = set()
        for room, sheets in made:
            if not sheets:
                continue
            stamp = (views._project_generation(room),
                     room.get(SET_PROP) or '', count)
            with views.in_room(context, room) as ctx:
                for i, sheet in enumerate(sheets):
                    key = (room.name, i, sheet.get('_number'),
                           json.dumps(sheet, sort_keys=True, default=str))
                    live.add(key)
                    hit = _page_cache.get(key)
                    if hit is None or hit[0] != stamp:
                        hit = (stamp, compose(ctx, sheets, i, count))
                        _page_cache[key] = hit
                    pages.append(hit[1])
        for key in [k for k in _page_cache if k not in live]:
            del _page_cache[key]
    return pages


def write_pdf(context, path, pages=None):
    """The project's set as a PDF. Returns the path written (beside
    `path` under another name when a viewer has that file locked)."""
    if pages is None:
        pages = compose_project(context)
    doc = hb_pdf.Document()
    for drawing in pages:
        drawing.place(doc.add_page(drawing.width, drawing.height))
    return em._print_save(doc, path)
