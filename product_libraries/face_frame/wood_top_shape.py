"""
Shaped wood tops: the geometry for a top that is not a rectangle.

A wood top starts as one rectangular board sized from its cabinet. Once
it is reshaped (Edit Shape) it keeps an outline the same way a
countertop does -- countertop_common's keys and shape edits, plus one
value per edge saying whether that edge is finished. The finished edges
take the edge treatment the top is set to: the milled profile, or the
applied band. Everything here is plain math on 2D points so it can be
checked without Blender; types_face_frame turns the results into mesh.

Frame: the board's local space, X to the right, Y from 0 at the back
toward -depth at the front, Z up from the underside. The rectangle a
shape was drawn against is kept beside it, so when the cabinet under a
seated top changes size the shape stretches with it: points in the
right half move with the right edge, points in the front half with the
front. A notch or a bump keeps its size and its distance from the edge
it was cut into.

Edges meet the way the square top's edges already did. Where two
finished edges meet the treatment mitres on the line through the outer
corner and the inner one; where a finished edge meets a plain one it
stops square on the plain edge's face. The core board is the outline
with each finished edge pulled in by the treatment's depth.
"""

import math

from ..common import countertop_common as cc

# The rectangle the stored outline was drawn against, (width, depth).
BASE_KEY = 'wt_shape_base'

# Consecutive finished edges turning less than this belong to one run
# -- one band part -- so a rounded corner is one piece of edge, not
# twelve.
RUN_BREAK_DEG = 20.0


def is_shaped(obj):
    return cc.has_outline(obj)


def rectangle(width, depth):
    """The square top as an outline, anticlockwise: front, right, back,
    left edges, in that order."""
    return [(0.0, -depth), (width, -depth), (width, 0.0), (0.0, 0.0)]


def seed_corners(front, right, back, left):
    """Sharp corners carrying the four sides' finished flags, matching
    rectangle()'s edge order."""
    return [(cc.CORNER_SHARP, 0.0, 0.0, 1.0 if flag else 0.0)
            for flag in (front, right, back, left)]


def restretch(points, old_base, new_base, tol=1e-9):
    """Carry a shape onto a resized rectangle. Returns new points."""
    ow, od = old_base
    nw, nd = new_base
    dw, dd = nw - ow, nd - od
    if abs(dw) < tol and abs(dd) < tol:
        return list(points)
    out = []
    for x, y in points:
        nx = x + dw if x > ow / 2.0 else x
        ny = y - dd if y < -od / 2.0 else y
        out.append((nx, ny))
    return out


def anticlockwise(points, values):
    """The outline and edge values running anticlockwise. Reversing an
    outline moves each edge's value to the corner at its other end."""
    if cc.signed_area(points) >= 0.0:
        return list(points), list(values)
    count = len(points)
    pts = list(reversed(points))
    # Edge i of the reversed list runs from pts[i] to pts[i+1], which is
    # original edge (count - 2 - i) mod count.
    vals = [values[(count - 2 - i) % count] for i in range(count)]
    return pts, vals


def _dir(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return None, 0.0
    return (dx / length, dy / length), length


def _inward(u):
    """Inward normal of an anticlockwise outline's edge."""
    return (-u[1], u[0])


def _line(points, i, w):
    """Edge i's line pulled in by w: (point, direction)."""
    count = len(points)
    a, b = points[i % count], points[(i + 1) % count]
    u, _ = _dir(a, b)
    if u is None:
        return None
    n = _inward(u)
    return (a[0] + n[0] * w, a[1] + n[1] * w), u


def _meet(l0, l1, fallback):
    """Where two lines cross; ``fallback`` when they run parallel."""
    if l0 is None or l1 is None:
        return fallback
    (p, u), (q, v) = l0, l1
    cross = u[0] * v[1] - u[1] * v[0]
    if abs(cross) < 1e-9:
        return fallback
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = (dx * v[1] - dy * v[0]) / cross
    return (p[0] + u[0] * t, p[1] + u[1] * t)


def _shift(point, points, i, w):
    """``point`` moved in by w off edge i -- used where an edge runs
    straight on into the next and there is no corner to meet at."""
    count = len(points)
    u, _ = _dir(points[i % count], points[(i + 1) % count])
    if u is None:
        return point
    n = _inward(u)
    return (point[0] + n[0] * w, point[1] + n[1] * w)


def core_outline(points, finished, depth):
    """The core board: every finished edge pulled in by ``depth``."""
    count = len(points)
    out = []
    for i in range(count):
        wp = depth if finished[i - 1] else 0.0
        wi = depth if finished[i] else 0.0
        fallback = _shift(points[i], points, i, wi)
        out.append(_meet(_line(points, i - 1, wp), _line(points, i, wi),
                         fallback))
    return out


def edge_ends(points, finished, i, w):
    """Start and end of edge i's treatment at inward offset w: mitred on
    a finished neighbour, stopped on the face of a plain one."""
    count = len(points)
    prev, nxt = (i - 1) % count, (i + 1) % count
    here = _line(points, i, w)
    start = _meet(_line(points, prev, w if finished[prev] else 0.0), here,
                  _shift(points[i], points, i, w))
    end = _meet(here, _line(points, nxt, w if finished[nxt] else 0.0),
                _shift(points[nxt], points, i, w))
    return start, end


def sweep_rings(points, finished, section, i):
    """The two end rings of edge i's treatment prism.

    ``section`` is the profile as (w, z) pairs: w how far in from the
    top's outer face, z the height. Returns (ring_start, ring_end) as
    lists of (x, y, z)."""
    ring0, ring1 = [], []
    for w, z in section:
        s, e = edge_ends(points, finished, i, w)
        ring0.append((s[0], s[1], z))
        ring1.append((e[0], e[1], z))
    return ring0, ring1


def runs(points, finished):
    """Finished edges grouped into runs of near-straight turns. Returns
    lists of edge indices, each in outline order."""
    count = len(points)
    fin = [i for i in range(count) if finished[i]]
    if not fin:
        return []

    def joined(i):
        """Does edge i carry straight on into edge i + 1?"""
        j = (i + 1) % count
        if not (finished[i] and finished[j]):
            return False
        u, _ = _dir(points[i], points[j])
        v, _ = _dir(points[j], points[(j + 1) % count])
        if u is None or v is None:
            return True
        cos_t = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))
        return math.degrees(math.acos(cos_t)) < RUN_BREAK_DEG

    if len(fin) == count and all(joined(i) for i in range(count)):
        return [list(range(count))]
    # Start each run at an edge the one before it does not flow into.
    starts = [i for i in fin if not joined((i - 1) % count)]
    out = []
    for s in starts:
        run = [s]
        i = s
        while joined(i):
            i = (i + 1) % count
            run.append(i)
        out.append(run)
    return out


def run_length(points, run):
    total = 0.0
    count = len(points)
    for i in run:
        _, length = _dir(points[i], points[(i + 1) % count])
        total += length
    return total


def bounds(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


# ---------------------------------------------------------------------------
# Joints
#
# A top too big for one piece of stock is built from several, and the
# line where two meet is part of the design: a miter where an L turns, a
# seam across a long run. Each joint is a chord across the top, stored as
# (kind, ax, ay, bx, by) in the outline's frame. A miter starts at an
# inside corner and runs to the outer corner across from it; a seam runs
# straight across from a point on an edge. Both are found again on the
# shape after every change, so they stay on the corners and edges they
# were put on while the shape is edited.
# ---------------------------------------------------------------------------

JOINTS_KEY = 'wt_joints'
# Longest measurement of each piece the joints cut the top into, for
# anything checking pieces against stock size.
PIECE_LENGTHS_KEY = 'wt_piece_lengths'
JOINT_MITER = 1
JOINT_SEAM = 2

# How far a miter's inside corner may have moved and still be the same
# corner.
MITER_SNAP = 0.3048            # 12 inches


def joints_of(obj):
    flat = list(obj.get(JOINTS_KEY) or [])
    return [(int(round(flat[i])), (flat[i + 1], flat[i + 2]),
             (flat[i + 3], flat[i + 4]))
            for i in range(0, len(flat) - 4, 5)]


def set_joints(obj, joints):
    if not joints:
        if JOINTS_KEY in obj:
            del obj[JOINTS_KEY]
        return
    flat = []
    for kind, a, b in joints:
        flat.extend((float(kind), float(a[0]), float(a[1]),
                     float(b[0]), float(b[1])))
    obj[JOINTS_KEY] = flat


def restretch_joints(joints, old_base, new_base):
    out = []
    for kind, a, b in joints:
        a2, b2 = restretch([a, b], old_base, new_base)
        out.append((kind, a2, b2))
    return out


def _cross2(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def contains(poly, p):
    """Is p inside the outline (even-odd)?"""
    inside = False
    count = len(poly)
    for i in range(count):
        a, b = poly[i], poly[(i + 1) % count]
        if (a[1] > p[1]) != (b[1] > p[1]):
            x = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x > p[0]:
                inside = not inside
    return inside


def _seg_hit(p, d, a, b):
    """Ray p + t*d against segment ab: (t, s) or None."""
    e = (b[0] - a[0], b[1] - a[1])
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-12:
        return None
    w = (a[0] - p[0], a[1] - p[1])
    t = (w[0] * e[1] - w[1] * e[0]) / den
    s = (w[0] * d[1] - w[1] * d[0]) / den
    if -1e-9 <= s <= 1.0 + 1e-9:
        return t, s
    return None


def nearest_on_boundary(poly, p):
    """(point, edge index) on the outline nearest p."""
    best, best_d, best_i = None, None, None
    count = len(poly)
    for i in range(count):
        a, b = poly[i], poly[(i + 1) % count]
        u, length = _dir(a, b)
        if u is None:
            continue
        t = max(0.0, min(length,
                         (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]))
        q = (a[0] + u[0] * t, a[1] + u[1] * t)
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        if best_d is None or d < best_d:
            best, best_d, best_i = q, d, i
    return best, best_i


def ray_to_boundary(poly, p, d, skip_edge=None):
    """First point where a ray from p (on the outline) along d meets the
    outline again."""
    best = None
    count = len(poly)
    for i in range(count):
        if i == skip_edge:
            continue
        hit = _seg_hit(p, d, poly[i], poly[(i + 1) % count])
        if hit is None or hit[0] <= 1e-6:
            continue
        if best is None or hit[0] < best[0]:
            best = hit
    if best is None:
        return None
    return (p[0] + d[0] * best[0], p[1] + d[1] * best[0])


def chord_inside(poly, a, b):
    """Does the chord ab run through the top, not out across a notch?"""
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    if not contains(poly, mid):
        return False
    u, length = _dir(a, b)
    if u is None or length < 1e-4:
        return False
    count = len(poly)
    for i in range(count):
        hit = _seg_hit(a, u, poly[i], poly[(i + 1) % count])
        if hit is None:
            continue
        t, s = hit
        if 1e-5 < t < length - 1e-5 and 1e-6 < s < 1.0 - 1e-6:
            return False
    return True


def is_inside_corner(poly, i):
    """Is corner i of an anticlockwise outline a reflex (inside) one?"""
    count = len(poly)
    return _cross2(poly[i - 1], poly[i], poly[(i + 1) % count]) < -1e-12


def miter_target(poly, i):
    """The outer corner a miter from inside corner i runs to: the corner
    most nearly straight along the inside corner's bisector that a chord
    can reach through the top. None if there is none."""
    count = len(poly)
    c = poly[i]
    u0, _ = _dir(c, poly[i - 1])
    u1, _ = _dir(c, poly[(i + 1) % count])
    if u0 is None or u1 is None:
        return None
    inward, _ = _dir((0.0, 0.0), (-(u0[0] + u1[0]), -(u0[1] + u1[1])))
    if inward is None:
        return None
    best, best_cos = None, 0.0
    for k in range(count):
        if k == i or is_inside_corner(poly, k):
            continue
        v, _ = _dir(c, poly[k])
        if v is None:
            continue
        cos_a = v[0] * inward[0] + v[1] * inward[1]
        if cos_a <= best_cos or not chord_inside(poly, c, poly[k]):
            continue
        best, best_cos = poly[k], cos_a
    return best


def miter_from(poly, point):
    """A miter from the inside corner nearest ``point``, or None."""
    inside = [k for k in range(len(poly)) if is_inside_corner(poly, k)]
    if not inside:
        return None
    k = min(inside, key=lambda k: math.hypot(poly[k][0] - point[0],
                                             poly[k][1] - point[1]))
    if math.hypot(poly[k][0] - point[0], poly[k][1] - point[1]) > MITER_SNAP:
        return None
    target = miter_target(poly, k)
    if target is None:
        return None
    return (JOINT_MITER, poly[k], target)


def seam_from(poly, point, direction=None):
    """A seam across the top from the edge point nearest ``point``:
    square to that edge, or along ``direction`` when given."""
    a, i = nearest_on_boundary(poly, point)
    if a is None:
        return None
    count = len(poly)
    if direction is None:
        u, _ = _dir(poly[i], poly[(i + 1) % count])
        if u is None:
            return None
        direction = _inward(u)
    b = ray_to_boundary(poly, a, direction, skip_edge=i)
    if b is None or not chord_inside(poly, a, b):
        return None
    return (JOINT_SEAM, a, b)


def resolve_joints(poly, joints):
    """Put each joint back onto the shape as it is now. A miter finds its
    inside corner again (the nearest one) and its outer corner; a seam
    keeps its direction from the edge point nearest where it started.
    Joints that no longer fit are dropped."""
    out = []
    for kind, a, b in joints:
        if kind == JOINT_MITER:
            joint = miter_from(poly, a)
        else:
            d, _ = _dir(a, b)
            joint = seam_from(poly, a, d) if d is not None else None
        if joint is not None:
            out.append(joint)
    return out


def _area(poly):
    total = 0.0
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        total += a[0] * b[1] - b[0] * a[1]
    return total / 2.0


def split_polygon(poly, a, b):
    """Cut an outline along the line through a and b where it crosses
    the outline. Returns the two pieces, or [poly] when the line does not
    cross it exactly twice."""
    u, length = _dir(a, b)
    if u is None:
        return [poly]
    start = (a[0] - u[0] * 0.5, a[1] - u[1] * 0.5)
    reach = length + 1.0
    count = len(poly)
    hits = []
    for i in range(count):
        hit = _seg_hit(start, u, poly[i], poly[(i + 1) % count])
        if hit is None:
            continue
        t, s = hit
        if 0.0 <= t <= reach and s < 1.0 - 1e-9:
            hits.append((t, i))
    # A line through a corner meets both edges there; keep one.
    hits.sort()
    uniq = []
    for h in hits:
        if uniq and abs(h[0] - uniq[-1][0]) < 1e-7:
            continue
        uniq.append(h)
    if len(uniq) != 2:
        return [poly]
    ends = [((start[0] + u[0] * t, start[1] + u[1] * t), i) for t, i in uniq]
    ends.sort(key=lambda e: e[1])
    (pa, ia), (pb, ib) = ends
    piece1 = [pa] + [poly[k] for k in range(ia + 1, ib + 1)] + [pb]
    piece2 = ([pb] + [poly[k % count] for k in range(ib + 1, ia + count + 1)]
              + [pa])
    pieces = []
    for piece in (piece1, piece2):
        clean = []
        for p in piece:
            if clean and math.hypot(p[0] - clean[-1][0],
                                    p[1] - clean[-1][1]) < 1e-7:
                continue
            clean.append(p)
        if len(clean) > 2 and math.hypot(clean[0][0] - clean[-1][0],
                                         clean[0][1] - clean[-1][1]) < 1e-7:
            clean.pop()
        if len(clean) >= 3 and abs(_area(clean)) > 1e-8:
            pieces.append(clean)
    return pieces if len(pieces) == 2 else [poly]


def split_all(poly, joints):
    """Cut an outline by every joint in turn; each joint cuts the piece
    its midpoint falls in."""
    pieces = [poly]
    for _kind, a, b in joints:
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        for n, piece in enumerate(pieces):
            if contains(piece, mid):
                cut = split_polygon(piece, a, b)
                if len(cut) == 2:
                    pieces[n:n + 1] = cut
                break
    return pieces


def piece_length(poly):
    """A piece's length: the long side of the smallest rectangle of stock
    it can be cut from, squared to one of its own edges. A mitred leg
    measures along the leg, not along its miter."""
    best_area, best_len = None, 0.0
    count = len(poly)
    for i in range(count):
        u, _ = _dir(poly[i], poly[(i + 1) % count])
        if u is None:
            continue
        along = [p[0] * u[0] + p[1] * u[1] for p in poly]
        across = [-p[0] * u[1] + p[1] * u[0] for p in poly]
        la = max(along) - min(along)
        lc = max(across) - min(across)
        if best_area is None or la * lc < best_area - 1e-12:
            best_area, best_len = la * lc, max(la, lc)
    return best_len
