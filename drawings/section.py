"""SECTION view: a cut square to a wall at one place along it.

Everything standing at that place is in the view, so an upper over a
base comes out as one section with the wall line behind them. The
drawing is made from the parts' own boxes: a part the cut passes
through is drawn heavy, the far side of each cabinet light, with the
toe platform and the nearest pull.

Origin = the wall's face at the floor; the room is to the left.

First cut: the far side's holes are a pattern, not the cabinet's real
drilling, and countertops, reveals and typed notes are not drawn yet.
"""

from mathutils import Vector

from ..operators import elevation_mode as em
from . import draft
from .drawing import Drawing
from . import views

IN = draft.INCH
CUT_WIDTH, SEEN_WIDTH = 0.9, 0.35
FRONT_ROLES = ('FRONT', 'LEFT_DOOR', 'RIGHT_DOOR', 'DOOR', 'FALSE_FRONT',
               'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT')
SIDE_ROLES = ('LEFT_SIDE', 'RIGHT_SIDE')
SHELF_ROLES = ('SHELF', 'ADJUSTABLE_SHELF')
KICK_ROLES = ('LADDER_BASE',)


def _box(ev, Fi):
    pts = [Fi @ (ev.matrix_world @ Vector(c)) for c in ev.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


def _boards(ev, Fi, box):
    """One shelf mesh can hold several shelves: (z0, z1) of each."""
    if box[5] - box[4] < 1.5 * IN:
        return [(box[4], box[5])]
    zs = sorted({round((Fi @ (ev.matrix_world @ v.co)).z, 4)
                 for v in ev.data.vertices})
    return [(a, b) for a, b in zip(zs[::2], zs[1::2]) if b - a < 1.5 * IN]


def parts_at(context, wall, x_cut):
    """What a cut at `x_cut` metres along `wall` meets, in the wall's
    frame (y = 0 the wall's face, the room negative): 'items', 'cut'
    [(role, y0, y1, z0, z1)], 'seen' (far sides), 'pulls', 'kick'."""
    scene = context.scene
    Fi = em._frame(wall)[1]
    deps = context.evaluated_depsgraph_get()
    out = {'items': [], 'cut': [], 'seen': [], 'pulls': [], 'kick': []}
    pulls = []
    for it in views.wall_items(scene, wall):
        if it.kind == 'OPENING' or not (
                it.x0 - 1e-4 <= x_cut <= it.x1 + 1e-4):
            continue
        out['items'].append(it)
        if it.obj.get('IS_APPLIANCE'):
            out['seen'].append(
                ('APPLIANCE',) + _box(it.obj.evaluated_get(deps), Fi)[2:])
            continue
        for obj in it.obj.children_recursive:
            if obj.type != 'MESH':
                continue
            role = obj.get('hb_part_role')
            ev = obj.evaluated_get(deps)
            if role in KICK_ROLES:
                out['kick'].append(_box(ev, Fi)[2:])
                continue
            if (obj.get('IS_GEONODE_CAGE') or obj.hide_render
                    or ev.data is None or not len(ev.data.vertices)
                    or not obj.get('CABINET_PART') and role is None):
                continue
            box = _box(ev, Fi)
            hit = box[0] - 1e-4 <= x_cut <= box[1] + 1e-4
            if role == 'PULL':
                pulls.append(box)
            elif role in SIDE_ROLES and not hit:
                if role == 'RIGHT_SIDE':
                    out['seen'].append((role,) + box[2:])
            elif hit:
                if role in SHELF_ROLES:
                    for z0, z1 in _boards(ev, Fi, box):
                        out['cut'].append(('SHELF', box[2], box[3], z0, z1))
                else:
                    out['cut'].append((role or 'PART',) + box[2:])
    # One pull at each height: the one nearest the cut.
    best = {}
    for box in pulls:
        key = round((box[4] + box[5]) / 2.0, 2)
        d = abs((box[0] + box[1]) / 2.0 - x_cut)
        if key not in best or d < best[key][0]:
            best[key] = (d, box[2:])
    out['pulls'] = [v[1] for v in best.values()]
    return out


def wall_cuts(scene, wall):
    """Where a wall is worth cutting: once through each distinct set-up
    of fronts among what stands on its floor, a third of the way along
    the product, in metres along the wall."""
    seen, cuts = set(), []
    for it in sorted(views.wall_items(scene, wall), key=lambda it: it.x0):
        if (it.kind != 'LOWER' or it.obj.get('IS_APPLIANCE')
                or it.x1 - it.x0 < 12 * IN):
            continue
        fronts = tuple(sorted(
            (obj.get('hb_part_role'), round(obj.dimensions.z, 2))
            for obj in it.obj.children_recursive
            if obj.get('hb_part_role') in FRONT_ROLES))
        key = (fronts, round(it.z1 - it.z0, 3))
        if key in seen:
            continue
        seen.add(key)
        cuts.append(round(it.x0 + (it.x1 - it.x0) * 0.3, 4))
    return cuts


def resolve(context, view, _width, _height):
    wall = views.wall_of(view)
    if wall is None:
        return None
    scene = context.scene
    k = view.get('k') or views.INCH_SCALE
    wall_height = em._frame(wall)[3]
    parts = parts_at(context, wall, float(view.get('x') or 0.0))
    if not parts['items']:
        return None
    out = Drawing()

    def fmt(v):
        return em.format_length(scene, v)

    def R(y0, y1, z0, z1):
        return (y0 * k, z0 * k, (y1 - y0) * k, (z1 - z0) * k)

    front_y = min([c[1] for c in parts['cut']]
                  + [s[1] for s in parts['seen']] + [-12 * IN])
    # The wall and the floor.
    out.stroke_color(draft.INK)
    out.line_width(0.9)
    out.lines([((0.0, 0.0), (0.0, wall_height * k + 14.0)),
               ((front_y * k - 70.0, 0.0), (0.0, 0.0))])
    # The far side of each cabinet.
    for role, y0, y1, z0, z1 in parts['seen']:
        out.stroke_color(draft.INK)
        out.line_width(SEEN_WIDTH)
        out.rect(*R(y0, y1, z0, z1), stroke=True)
        if role == 'APPLIANCE':
            continue
        out.fill_color(draft.INK)
        z = z0 + 2.5 * IN
        while z < z1 - 2.0 * IN:
            for y in (y0 + 0.037, y1 - 0.75 * IN - 0.037):
                out.circle(y * k, z * k, 0.55, fill=True, stroke=False)
            z += 0.032
    # The toe platform: its front and back rails cut, the rest seen.
    for y0, y1, z0, z1 in parts['kick']:
        out.stroke_color(draft.INK)
        out.line_width(SEEN_WIDTH)
        out.rect(*R(y0, y1, z0, z1), stroke=True)
        for y in (y0, y1 - 0.75 * IN):
            out.fill_color((0.8, 0.8, 0.8))
            out.rect(*R(y, y + 0.75 * IN, z0, z1), fill=True, stroke=True)
    # What the cut goes through.
    for role, y0, y1, z0, z1 in parts['cut']:
        out.stroke_color(draft.INK)
        out.fill_color(draft.WHITE)
        if role == 'DRAWER_BOX':
            out.line_width(0.6)
            out.rect(*R(y0, y1, z0, z1), fill=True, stroke=True)
            t = 0.5 * IN
            if y1 - y0 > 3 * t and z1 - z0 > 2 * t:
                out.rect(*R(y0 + t, y1 - t, z0 + t, z1),
                         fill=True, stroke=True)
        else:
            out.line_width(CUT_WIDTH)
            out.rect(*R(y0, y1, z0, z1), fill=True, stroke=True)
        if role == 'SHELF':
            draft.text_centered(out, (y0 + y1) / 2.0 * k, z1 * k + 4.0,
                                'ADJ', 6.5)
    for y0, y1, z0, z1 in parts['pulls']:
        out.stroke_color(draft.INK)
        out.line_width(0.5)
        out.rect(*R(y0, y1, z0, z1), stroke=True)

    # ---- Dimensions, placed by rule.
    items = sorted(parts['items'], key=lambda it: it.z0)
    cabinets = [it for it in items if not it.obj.get('IS_APPLIANCE')]
    fronts = sorted((c for c in parts['cut'] if c[0] in FRONT_ROLES),
                    key=lambda c: c[3])

    def on_floor(it):
        return it.z0 < 0.3

    # Left: each cabinet's fronts as a chain, the kick with them.
    x_left = front_y * k - 26.0
    for it in cabinets:
        mine = [c for c in fronts
                if it.z0 - 1e-3 <= c[3] and c[4] <= it.z1 + 1e-3]
        levels = [0.0] if on_floor(it) and mine else []
        for c in mine:
            levels += [c[3], c[4]]
        levels = sorted(set(round(v, 4) for v in levels))
        for a, b in zip(levels, levels[1:]):
            if b - a < 0.02:            # a reveal between two fronts
                continue
            draft.dim_v(out, a * k, b * k, x_left, fmt(b - a),
                        ext_to=front_y * k)
    # Right, past the wall line: each cabinet, then the run off the floor.
    for it in cabinets:
        z0 = 0.0 if on_floor(it) else it.z0
        draft.dim_v(out, z0 * k, it.z1 * k, 14.0, fmt(it.z1 - z0),
                    ext_to=0.0, side=1)
    if len(cabinets) > 1:
        top = max(it.z1 for it in cabinets)
        draft.dim_v(out, 0.0, top * k, 54.0, fmt(top), ext_to=0.0, side=1)
    # Over each cabinet: the depth of its case.
    for it in cabinets:
        sides = [s for s in parts['seen'] if s[0] in SIDE_ROLES
                 and it.z0 - 1e-3 <= s[3] and s[4] <= it.z1 + 1e-3]
        if sides:
            _role, y0, y1, _z0, z1 = sides[0]
            draft.dim_h(out, y0 * k, y1 * k, z1 * k + 18.0, fmt(y1 - y0),
                        ext_to=z1 * k)
    # Under the floor: the platform, and how far it stands back.
    for y0, y1, _z0, _z1 in parts['kick']:
        draft.dim_h(out, y0 * k, y1 * k, -18.0, fmt(y1 - y0), ext_to=0.0)
        case_front = min([s[1] for s in parts['seen']
                          if s[0] in SIDE_ROLES and s[3] < 0.3] + [y0])
        if y0 - case_front > 0.01:
            draft.dim_h(out, case_front * k, y0 * k, -34.0,
                        fmt(y0 - case_front), ext_to=0.0)
    for it in items:
        if it.obj.get('IS_APPLIANCE'):
            draft.text_centered(out, (front_y / 2.0) * k,
                                (it.z0 + it.z1) / 2.0 * k,
                                it.name.upper(), 8.0)
    out.anchors['wall_floor'] = (0.0, 0.0)
    out.info = {'k': k, 'scale': "1\" = 1'-0\""}
    return out
