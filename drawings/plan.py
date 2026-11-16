"""PLAN view: the strip of floor in front of one wall, drawn from the
products' own boxes rather than projected from their meshes.

Origin = the wall's start at its face; x runs along the wall, the room
is below (negative y). Drawn at the view's 'k' (points to the metre),
so it can stand over an elevation of the same wall and line up with it.

First cut: walls, product outlines, numbers, the wall's length and the
depths. Door swings, countertops and whole-room plans come later.
"""

from mathutils import Vector

from ..operators import elevation_mode as em
from . import draft
from .drawing import Drawing
from . import views

DEFAULT_DEPTH = 44.0 * draft.INCH       # how far into the room the strip shows


def _number(obj):
    """A product's number as short as it reads on a drawing: what
    follows the last dot of a dotted number."""
    for key in obj.keys():
        if key.endswith('UNIT_NUMBER') and obj.get(key):
            return str(obj[key]).split('.')[-1]
    return None


def resolve(context, view, _width, _height):
    wall = views.wall_of(view)
    if wall is None:
        return None
    scene = context.scene
    k = view.get('k') or views.HALF_INCH_SCALE
    depth = view.get('depth') or DEFAULT_DEPTH
    _F, Fi, length, _Hw = em._frame(wall)
    thickness = em._wall_dims(wall)[2]
    deps = context.evaluated_depsgraph_get()
    floor = -depth
    out = Drawing()

    def P(x, y):
        return (x * k, y * k)

    def box(obj):
        ev = obj.evaluated_get(deps)
        return [Fi @ (ev.matrix_world @ Vector(c)) for c in ev.bound_box]

    # This wall, and whatever of the others shows in the strip.
    for other in em.room_walls(scene):
        poly = draft.clip_below(
            draft.hull([(p.x, p.y) for p in box(other)]), floor)
        if len(poly) >= 3:
            draft.hatch(out, [P(*p) for p in poly])
    boxes = []
    for it in views.wall_items(scene, wall):
        if it.kind == 'OPENING':
            continue
        y0 = min(p.y for p in box(it.obj))
        boxes.append((it, it.x0, it.x1, max(y0, floor)))
    # What hangs is drawn first, dashed, under what stands on the floor.
    for it, x0, x1, y0 in sorted(boxes, key=lambda b: b[0].kind != 'UPPER'):
        a, b = P(x0, y0), P(x1, 0.0)
        appliance = bool(it.obj.get('IS_APPLIANCE'))
        out.stroke_color(draft.INK)
        if it.kind == 'UPPER':
            out.line_width(0.45)
            out.dash(5.0, 3.0)
        elif appliance:
            out.line_width(0.45)
            out.dash(8.0, 2.0)
        else:
            out.line_width(0.8)
            out.dash()
        out.lines([((a[0], a[1]), (b[0], a[1])), ((b[0], a[1]), (b[0], b[1])),
                   ((a[0], a[1]), (a[0], b[1]))])
        out.dash()
        cx = (a[0] + b[0]) / 2.0
        cy = a[1] + (b[1] - a[1]) * (0.5 if it.kind == 'UPPER' else 0.28)
        number = _number(it.obj)
        if number and (b[0] - a[0]) > 16.0:
            w, h = 22.0, 7.5
            out.fill_color(draft.WHITE)
            out.stroke_color(draft.INK)
            out.line_width(0.4)
            out.rect(cx - w / 2, cy - h / 2, w, h, fill=True, stroke=True)
            draft.text_centered(out, cx, cy - 2.0, number, 5.5, halo=False)
        elif appliance:
            draft.text_centered(out, cx, cy, it.name.upper()[:12], 5.0)
    # The wall's length over the top, one depth each down the left.
    top = thickness * k
    draft.dim_h(out, 0.0, length * k, top + 22.0,
                em.format_length(scene, length), ext_to=top)
    depths = []
    for it, _x0, _x1, y0 in boxes:
        d = round(-y0 / draft.INCH * 16) / 16.0
        if (d > 1.0 and not it.obj.get('IS_APPLIANCE')
                and all(abs(d - e) > 0.2 for e in depths)):
            depths.append(d)
    x = -thickness * k - 14.0
    for d in sorted(depths, reverse=True):
        draft.dim_v(out, -d * draft.INCH * k, 0.0, x,
                    em.format_length(scene, d * draft.INCH), ext_to=0.0)
        x -= 34.0
    out.anchors['wall_start'] = (0.0, 0.0)
    out.anchors['marker'] = (length * k / 2.0, floor * k - 2.0)
    out.info = {'k': k, 'top': top + 34.0}
    return out
