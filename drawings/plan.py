"""PLAN view: the strip of floor in front of one wall, drawn from the
products' own boxes rather than projected from their meshes.

Origin = the wall's start at its face; x runs along the wall, the room
is below (negative y). Drawn at the view's 'k' (points to the metre),
so it can stand over an elevation of the same wall and line up with it.

First cut: walls, product outlines, numbers, the wall's length and the
depths. Door swings, countertops and whole-room plans come later.
"""

import math

from mathutils import Vector

from .. import hb_pdf

from ..operators import elevation_mode as em
from . import draft
from .drawing import Drawing
from . import views

DEFAULT_DEPTH = 44.0 * draft.INCH       # how far into the room the strip shows


def _number(obj):
    return views.unit_number(obj)


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
            views.number_tag(out, cx, cy, number, (b[0] - a[0]) - 3.0)
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


# ---- The whole room ------------------------------------------------------------

ROOM_SCALES = ((24, '1/2"'), (32, '3/8"'), (48, '1/4"'), (64, '3/16"'),
               (96, '1/8"'), (128, '3/32"'))
DOOR_OPEN = math.radians(30.0)
DOOR_ROLES = {'LEFT_DOOR': -1, 'RIGHT_DOOR': 1}     # the side it is hinged


def _ancestors(obj):
    obj = obj.parent
    while obj is not None:
        yield obj
        obj = obj.parent


def _room_parts(context):
    """The room from above, in metres: walls, product footprints, door
    swings, countertops, and where each wall's elevation looks from."""
    scene = context.scene
    deps = context.evaluated_depsgraph_get()
    out = {'walls': [], 'boxes': [], 'swings': [], 'tops': [], 'dims': [],
           'markers': {}}

    def world_hull(obj):
        ev = obj.evaluated_get(deps)
        pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
        return draft.hull([(p.x, p.y) for p in pts])

    on_walls = set()
    for wall in em.room_walls(scene):
        F, Fi, length, _Hw = em._frame(wall)
        thickness = em._wall_dims(wall)[2]
        out['walls'].append(world_hull(wall))

        def W(x, y, F=F):
            p = F @ Vector((x, y, 0.0))
            return (p.x, p.y)

        deepest = 0.0
        items = [it for it in views.wall_items(scene, wall)
                 if it.kind != 'OPENING']
        for it in items:
            on_walls.add(it.obj.name)
            ev = it.obj.evaluated_get(deps)
            y0 = min((Fi @ (ev.matrix_world @ Vector(c))).y
                     for c in ev.bound_box)
            deepest = min(deepest, y0)
            appliance = bool(it.obj.get('IS_APPLIANCE'))
            out['boxes'].append({
                'poly': [W(it.x0, y0), W(it.x1, y0), W(it.x1, 0.0),
                         W(it.x0, 0.0)],
                'kind': 'APPLIANCE' if appliance else it.kind,
                'label': (it.name.upper()[:12] if appliance
                          else _number(it.obj)),
                'at': W((it.x0 + it.x1) / 2.0,
                        y0 * (0.5 if it.kind == 'UPPER' else 0.72))})
            for part in it.obj.children_recursive:
                side = DOOR_ROLES.get(part.get('hb_part_role'))
                if side is None or part.type != 'MESH' or part.hide_render:
                    continue
                pe = part.evaluated_get(deps)
                pts = [Fi @ (pe.matrix_world @ Vector(c))
                       for c in pe.bound_box]
                px0, px1 = min(p.x for p in pts), max(p.x for p in pts)
                front = min(p.y for p in pts)
                width = px1 - px0
                if width < 0.05:
                    continue
                hinge = px0 if side < 0 else px1
                arc = []
                for i in range(7):
                    a = DOOR_OPEN * i / 6.0
                    arc.append(W(hinge - side * width * math.cos(a),
                                 front - width * math.sin(a)))
                out['swings'].append((W(hinge, front), arc))
        if items:
            out['dims'].append((W(0.0, thickness), W(length, thickness),
                                W(0.0, thickness + 1.0), length))
            # Its elevation looks at it from out in the room.
            stand = W(length / 2.0, deepest - 0.25)
            toward = W(length / 2.0, deepest)
            out['markers'][wall.name] = (
                stand, (toward[0] - stand[0], toward[1] - stand[1]))
    for obj in scene.objects:
        if obj.get('IS_COUNTERTOP') and obj.type == 'MESH':
            out['tops'].append(world_hull(obj))
        elif (em._is_product(obj) and obj.name not in on_walls
                and em._wall_of(obj) is None and not obj.hide_render
                and not any(em._is_product(p) for p in _ancestors(obj))):
            poly = world_hull(obj)
            if len(poly) >= 3:
                cx = sum(p[0] for p in poly) / len(poly)
                cy = sum(p[1] for p in poly) / len(poly)
                out['boxes'].append({'poly': poly, 'kind': 'LOWER',
                                     'label': _number(obj), 'at': (cx, cy)})
    return out


def resolve_room(context, view, width, height):
    """ROOM_PLAN view: the whole room from above, at the largest
    drafting scale that goes in the room the sheet gives it."""
    scene = context.scene
    parts = _room_parts(context)
    pts = [p for poly in parts['walls'] for p in poly]
    pts += [p for b in parts['boxes'] for p in b['poly']]
    if not pts:
        return None
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = 60.0              # points round the room for its dimensions
    k, label = None, None
    for n, text in ROOM_SCALES:
        k = 72.0 / 0.0254 / n
        label = text + " = 1'-0\""
        if ((x1 - x0) * k + 2 * pad <= width
                and (y1 - y0) * k + 2 * pad <= height):
            break
    else:
        k = min((width - 2 * pad) / max(x1 - x0, 1e-6),
                (height - 2 * pad) / max(y1 - y0, 1e-6))
        label = None
    out = Drawing(width, height)
    ox = (width - (x1 - x0) * k) / 2.0
    oy = (height - (y1 - y0) * k) / 2.0

    def P(p):
        return (ox + (p[0] - x0) * k, oy + (p[1] - y0) * k)

    def outline(poly):
        pp = [P(p) for p in poly]
        out.lines([(pp[i], pp[(i + 1) % len(pp)]) for i in range(len(pp))])

    for poly in parts['walls']:
        if len(poly) >= 3:
            draft.hatch(out, [P(p) for p in poly])
    out.stroke_color(draft.GREY)
    out.line_width(0.35)
    for poly in parts['tops']:
        if len(poly) >= 3:
            outline(poly)
    order = {'UPPER': 0, 'APPLIANCE': 1, 'LOWER': 2}
    for box in sorted(parts['boxes'], key=lambda b: order.get(b['kind'], 2)):
        out.stroke_color(draft.INK)
        if box['kind'] == 'UPPER':
            out.line_width(0.45)
            out.dash(5.0, 3.0)
        elif box['kind'] == 'APPLIANCE':
            out.line_width(0.45)
            out.dash(8.0, 2.0)
        else:
            out.line_width(0.8)
            out.dash()
        outline(box['poly'])
        out.dash()
    out.stroke_color(draft.GREY)
    out.line_width(0.3)
    for hinge, arc in parts['swings']:
        aa = [P(p) for p in arc]
        out.lines([(P(hinge), aa[-1])]
                  + [(aa[i], aa[i + 1]) for i in range(len(aa) - 1)])
    for box in parts['boxes']:
        if not box['label']:
            continue
        cx, cy = P(box['at'])
        if box['kind'] == 'APPLIANCE':
            draft.text_centered(out, cx, cy - 2.0, box['label'], 5.0)
            continue
        views.number_tag(out, cx, cy, box['label'])
    for a, b, outward, length in parts['dims']:
        pa, pb, po = P(a), P(b), P(outward)
        n = math.hypot(po[0] - pa[0], po[1] - pa[1]) or 1.0
        off = ((po[0] - pa[0]) / n * 24.0, (po[1] - pa[1]) / n * 24.0)
        draft.dim_aligned(out, pa, pb, off, em.format_length(scene, length))
    for name, (stand, toward) in parts['markers'].items():
        sx, sy = P(stand)
        out.anchors['marker:' + name] = (sx, sy, toward[0], toward[1])
    out.info = {'k': k, 'scale': label}
    return out
