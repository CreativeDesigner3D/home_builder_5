"""The parts a laminate countertop is made from.

Read from the top as it is built (its outline, field joints, build-up
and splash), so the list always matches the model:

- a laminate slab top is one slab part per piece between field joints,
  banded 3mm on its front and finished ends;
- a built-up top is a 3/4" deck and its build-up strips per piece,
  plus the loose laminate that goes over them after: the deck face and,
  with a self edge, the front edge and each finished end. Laminate
  pieces are cut over in length and width for flush trimming. They are
  not in the room; they are listed so the laminate can be nested and
  ordered;
- the splash: slab splash stock banded 1mm on its top and exposed ends,
  or on a built-up top a 3/4" core with laminate on its face, top edge
  and exposed ends (1mm banding instead when the top is banded).

Lengths are cut lengths: a top butting a banded front edge is cut over
to reach under the banding.
"""

from fractions import Fraction

from ..common import countertop_common as cc

IN = 0.0254
LAMINATE_OVERSIZE = 0.5 * IN

CORE = "Particle Board 3/4\""
SLAB = "Laminate Slab 1-1/4\""
SPLASH = "Laminate Splash 3/4\""
LAMINATE = "Laminate"


def inches(value):
    """A length in meters as inches to the nearest 1/16."""
    sixteenths = round(value / IN * 16)
    whole, rem = divmod(abs(sixteenths), 16)
    sign = "-" if sixteenths < 0 else ""
    if not rem:
        return f"{sign}{whole}\""
    frac = Fraction(rem, 16)
    if not whole:
        return f"{sign}{frac.numerator}/{frac.denominator}\""
    return f"{sign}{whole}-{frac.numerator}/{frac.denominator}\""


def laminate_parts(obj):
    """The parts of one laminate top, identical ones counted together:
    dicts of qty, name, material, length, width, thickness, edges and
    laminate (True for a loose laminate piece)."""
    lam = cc._dict(obj.get(cc.LAMINATE_KEY))
    points = cc.built_outline(obj)
    if not lam or len(points) < 3:
        return []
    rect = cc.design_rect(obj)
    thickness = float(obj.get(cc.THICKNESS_KEY, 0.0))
    built = lam.get('construction') == 'BUILT_UP'
    self_edge = built and lam.get('edge') == 'SELF'
    buildup = cc._dict(obj.get(cc.BUILDUP_KEY))
    splash = cc._dict(obj.get(cc.SPLASH_KEY))
    deck = float(buildup.get('deck', 0.0)) if buildup else 0.0
    xs = [x for x, _y in points]
    ranges = cc.piece_ranges(obj, min(xs), max(xs))
    last = len(ranges) - 1
    over = LAMINATE_OVERSIZE
    parts = []

    def add(name, material, length, width, thick=0.0, edges="", laminate=False):
        parts.append({'name': name, 'material': material, 'length': length,
                      'width': width, 'thickness': thick, 'edges': edges,
                      'laminate': laminate})

    for i, (a, b) in enumerate(ranges):
        poly = cc.clip_x(points, a, b) if last else points
        ys = [y for _x, y in poly]
        depth = max(ys) - min(ys)
        length = b - a
        if i == 0:
            length += float(lam.get('extra_left', 0.0))
        if i == last:
            length += float(lam.get('extra_right', 0.0))
        left = lam.get('left') if i == 0 else 'JOINT'
        right = lam.get('right') if i == last else 'JOINT'
        finished = [k for k in (left, right) if k in ('FINISHED', 'FRIDGE')]
        tag = f"Top {i + 1}" if last else "Top"
        if not built:
            edges = "3mm front" + (f", 3mm {len(finished)} end" if finished else "")
            add(tag, SLAB, length, depth, thickness, edges + ", finished face up")
        else:
            if self_edge:
                band = ""
            else:
                band = "3mm front" + (f", 3mm {len(finished)} end" if finished else "")
            add(tag + " Deck", CORE, length, depth, deck, band)
            if rect:
                piece = (max(rect[0], a), min(rect[1], b), rect[2], rect[3])
                spec = cc.piece_spec(buildup, i, last, 0.0)
                for role, x0, x1, y0, y1 in cc.buildup_boxes(piece, spec):
                    run, wide = sorted((x1 - x0, y1 - y0), reverse=True)
                    add(f"{tag} Build-Up {role.title()}", CORE, run, wide,
                        thickness - deck)
            add(tag + " Laminate Deck", LAMINATE, length + over, depth + over,
                laminate=True)
            if self_edge:
                add(tag + " Laminate Front Edge", LAMINATE, length + over,
                    thickness + over, laminate=True)
                for _k in finished:
                    add(tag + " Laminate End Edge", LAMINATE, depth + over,
                        thickness + over, laminate=True)
        if not (splash and rect):
            continue
        piece = (max(rect[0], a), min(rect[1], b), rect[2], rect[3])
        spec = cc.piece_spec(splash, i, last, -1.0)
        height = float(spec.get('height', 0.0))
        th = float(spec.get('thickness', 0.0))
        for role, x0, x1, y0, y1 in cc.splash_boxes(piece, spec):
            if role == 'BACK':
                run = x1 - x0
                exposed = len(finished)
                name = "Splash" if not last else f"Splash {i + 1}"
            else:
                run = y1 - y0
                exposed = 1
                name = "End Splash"
            if not built:
                edges = "1mm top" + (f", 1mm {exposed} end" if exposed else "")
                add(name, SPLASH, run, height, th, edges)
                continue
            add(name, CORE, run, height, th,
                "" if self_edge else
                "1mm top" + (f", 1mm {exposed} end" if exposed else ""))
            add(name + " Laminate Face", LAMINATE, run + over, height + over,
                laminate=True)
            if self_edge:
                add(name + " Laminate Top Edge", LAMINATE, run + over,
                    th + over, laminate=True)
                for _e in range(exposed):
                    add(name + " Laminate End", LAMINATE, height + over,
                        th + over, laminate=True)
    return _combine(parts)


def _combine(parts):
    out = []
    index = {}
    for p in parts:
        key = (p['name'], p['material'], round(p['length'], 5), round(p['width'], 5),
               round(p['thickness'], 5), p['edges'], p['laminate'])
        if key in index:
            out[index[key]]['qty'] += 1
        else:
            index[key] = len(out)
            out.append(dict(p, qty=1))
    # Core parts first, then the loose laminate.
    out.sort(key=lambda p: p['laminate'])
    return out


def notes(obj):
    """Lines that go with the parts list: joints, drawbolts and cut-over."""
    lam = cc._dict(obj.get(cc.LAMINATE_KEY))
    lines = []
    joints = cc.joints_of(obj)
    bolts = len(obj.get(cc.DRAWBOLTS_KEY) or []) // 2
    if joints:
        lines.append(f"{len(joints)} field joint(s), {bolts} drawbolt(s)")
    extra = [inches(float(lam.get(k, 0.0))) for k in ('extra_left', 'extra_right')
             if float(lam.get(k, 0.0)) > 0.0]
    if extra:
        lines.append("Cut over " + " / ".join(extra)
                     + " where it butts a banded front edge")
    if lam.get('construction') == 'BUILT_UP':
        lines.append("Laminate pieces are cut " + inches(LAMINATE_OVERSIZE)
                     + " over in length and width for flush trimming")
    return lines
