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
