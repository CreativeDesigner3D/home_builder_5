"""The drawing set: sheets of placed views, as plain data.

    {'sheets': [{'views': [{'kind': 'ELEVATION', 'wall': 'Wall.001'},
                           {'kind': 'PLAN', 'wall': 'Wall.001'}]},
                {'views': [{'kind': 'SECTION', 'wall': 'Wall.001',
                            'x': 0.66}]}]}

A room that has no set of its own gets one made by rule each time it is
asked for, so nothing has to be created, kept in step or cleaned up. A
set is only stored once the user has changed it.

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

def default_set(scene):
    """The set made by rule: for each wall with products, its plan strip
    over its elevation, then its sections on the sheets after."""
    sheets = []
    for wall in em.room_walls(scene):
        if not any(it.kind != 'OPENING'
                   for it in views.wall_items(scene, wall)):
            continue
        sheets.append({'views': [{'kind': 'ELEVATION', 'wall': wall.name},
                                 {'kind': 'PLAN', 'wall': wall.name}]})
        cuts = [{'kind': 'SECTION', 'wall': wall.name, 'x': x}
                for x in section.wall_cuts(scene, wall)]
        for i in range(0, len(cuts), SECTIONS_A_SHEET):
            sheets.append({'views': cuts[i:i + SECTIONS_A_SHEET]})
    return {'sheets': sheets}


def stored_set(scene):
    try:
        data = json.loads(scene.get(SET_PROP) or 'null')
    except (TypeError, ValueError):
        return None
    if isinstance(data, dict) and isinstance(data.get('sheets'), list):
        return data
    return None


def store_set(scene, data):
    """Keep `data` as the room's own set; None goes back to the rule."""
    if data is None:
        if SET_PROP in scene:
            del scene[SET_PROP]
    else:
        scene[SET_PROP] = json.dumps(data)


def drawing_set(scene):
    """The room's set with every view marked: '_mark' (A, S1), '_sheet'
    (the sheet it is on), and on an elevation '_cuts', the sections cut
    from its wall, wherever they ended up."""
    data = stored_set(scene) or default_set(scene)
    sheets = [{'views': [dict(v) for v in s.get('views', [])
                         if isinstance(v, dict)]}
              for s in data['sheets']]
    letters, cuts = {}, {}
    n_sections = 0
    for number, sheet in enumerate(sheets, 1):
        for view in sheet['views']:
            view['_sheet'] = number
            wall = view.get('wall')
            if view.get('kind') == 'ELEVATION':
                letters.setdefault(wall, (_letter(len(letters)), number))
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


def _fit_section(context, view, height):
    """The section at the largest scale that stands in `height`."""
    for n, text in SECTION_SCALES:
        k = 72.0 / 0.0254 / n
        drawing = views.resolve(context, dict(view, k=k), 0.0, 0.0)
        if drawing is None:
            return None, None
        _x0, y0, _x1, y1 = drawing.bounds()
        if y1 - y0 <= height:
            break
    return drawing, f"{text} = 1'"


def compose(context, sheets, index):
    """Sheet `index` of `sheets` (from drawing_set) as one Drawing."""
    scene = context.scene
    width, height = PAPER
    sheet = sheets[index]
    page = Drawing(width, height)
    info = {'number': index + 1, 'count': len(sheets), 'sheet': sheet}
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
            e.place(page, x0, y0)
            ax, ay = e.anchors['wall_start']
            k = e.info['k']
            draft.view_title(
                page, x0 + 40.0, y0 + 30.0, elev['_mark'], elev['_sheet'],
                f"ELEVATION: {_wall_title(scene, elev.get('wall'))}",
                _scale_text(e.info.get('scale')),
                width=min(250.0, column_x - x0 - 80.0))
            top = e.anchors['wall_top'][1]
            for x_cut, mark, number in elev.get('_cuts', ()):
                draft.section_marker(page, x0 + ax + x_cut * k,
                                     y0 + top + 30.0, mark, number)
            if plan is not None:
                p = views.resolve(context, dict(plan, k=k), 0.0, 0.0)
                if p is not None:
                    px, py = x0 + ax, y1 - 6.0 - p.info['top']
                    p.place(page, px, py)
                    mx, my = p.anchors['marker']
                    draft.elevation_marker(page, px + mx, py + my,
                                           elev['_mark'], elev['_sheet'])
    for i, view in enumerate(sections):
        s, scale = _fit_section(context, view, (y1 - y0) - 110.0)
        if s is None:
            continue
        wall_x = column_x + SECTION_COLUMN * (i + 1) - 90.0
        s.place(page, wall_x, y0 + 92.0)
        draft.view_title(page, wall_x - 130.0, y0 + 26.0, view['_mark'],
                         view['_sheet'], 'SECTION', scale, width=150.0)
    return page


def compose_all(context):
    sheets = drawing_set(context.scene)
    return [compose(context, sheets, i) for i in range(len(sheets))]


def write_pdf(context, path, pages=None):
    """The room's set as a PDF. Returns the path written (beside `path`
    under another name when a viewer has that file locked)."""
    if pages is None:
        pages = compose_all(context)
    doc = hb_pdf.Document()
    for drawing in pages:
        drawing.place(doc.add_page(drawing.width, drawing.height))
    return em._print_save(doc, path)
