"""The plans of stairs that aren't straight runs and flat landings:
winders in an L's or U's turn, curved stairs and spiral stairs.

Everything is in the stair's own frame (hb_stairs): the first tread's
front edge from (0, 0) to (W, 0), climbing +y. A tread here is
(polygon, front edge, top): its outline counter-clockwise in plan, the
edge a person steps up over to reach it, and its top's height.

Winders: each quarter turn is the W x W square at the corner cut into
three kite treads by riser lines from the inside corner (where the
newel stands) at 30 and 60 degrees. A U's two quarter turns have a
plain tread between them when its flights stand apart.

Curved: treads between two arcs about a centre left (or right) of the
start, each as deep as the tread depth along the walk line (the middle
of the width). Spiral: the same about a centre pole, each tread a fixed
angle.
"""

import math

from mathutils import Matrix, Vector

from .units import inch

POLE_R = inch(2.0)              # a spiral's centre pole
WINDER_RISERS = 3               # risers in a quarter turn of winders
ARC_STEP = math.radians(6)      # the most an arc's edge turns between points


def is_shaped(v):
    """Whether the stair's treads are built from this module's plans."""
    return v['type'] in ('CURVED', 'SPIRAL') or (v['type'] in ('L_SHAPE', 'U_SHAPE') and v.get('winders'))


def is_arc(v):
    return v['type'] in ('CURVED', 'SPIRAL')


def _cross(u, p):
    return u.x * p.y - u.y * p.x


def clip(poly, f):
    """The part of a convex polygon where f(p) <= 0, f linear."""
    out = []
    k = len(poly)
    for i in range(k):
        p, q = poly[i], poly[(i + 1) % k]
        fp, fq = f(p), f(q)
        if fp <= 1e-12:
            out.append(p)
        if (fp < -1e-12 < fq) or (fq < -1e-12 < fp):
            t = fp / (fp - fq)
            out.append(p + (q - p) * t)
    return out


def _mirror_tread(tread, W):
    poly, front, z = tread
    poly = [Vector((W - p.x, p.y)) for p in reversed(poly)]
    if front is not None:
        front = (Vector((W - front[1].x, front[1].y)), Vector((W - front[0].x, front[0].y)))
    return poly, front, z


def corner(W):
    """A quarter turn of winders in the canonical square [0, W] x [0, W],
    entered over its bottom edge going +y and left over its left edge
    going -x, the newel at (0, 0): [(polygon, front edge)] in climbing
    order."""
    sq = [Vector((0.0, 0.0)), Vector((W, 0.0)), Vector((W, W)), Vector((0.0, W))]
    u30 = Vector((math.cos(math.radians(30)), math.sin(math.radians(30))))
    u60 = Vector((math.cos(math.radians(60)), math.sin(math.radians(60))))
    w1 = clip(sq, lambda p: _cross(u30, p))
    w2 = clip(clip(sq, lambda p: -_cross(u30, p)), lambda p: _cross(u60, p))
    w3 = clip(sq, lambda p: -_cross(u60, p))
    o = Vector((0.0, 0.0))
    return [(w1, (o, Vector((W, 0.0)))),
            (w2, (o, Vector((W, W * math.tan(math.radians(30)))))),
            (w3, (o, Vector((W / math.tan(math.radians(60)), W))))]


class Turn:
    """The treads of an L's or U's turn of winders: their plan, its rect
    (x0, y0, x1, y1), the newel corners, and the heights it climbs from
    and to."""

    def __init__(self, treads, rect, newels, z0, z1):
        self.treads, self.rect, self.newels, self.z0, self.z1 = treads, rect, newels, z0, z1


def winder_plan(v):
    """(flights, turn) of an L or U with winders: its two flights (from
    hb_stair_build.Flight) and its Turn."""
    from . import hb_stairs
    from .hb_stair_build import Flight
    W, T = v['width'], v['tread']
    u = v['type'] == 'U_SHAPE'
    gap = v['gap'] if u and v['gap'] >= inch(4) else 0.0
    corners = 2 if u else 1
    turn = WINDER_RISERS * corners + (1 if gap > 0.0 else 0)
    n = max(hb_stairs.riser_count(v['rise'], v['max_riser']), turn + 2)
    r = v['rise'] / n
    a = min(max(round(v['landing_height'] / r), 1), n - turn - 1)
    b = n - a - turn
    run1 = a * T
    z0 = a * r
    treads = []
    k = a
    for poly, front in corner(W):
        k += 1
        treads.append(([p + Vector((0.0, run1)) for p in poly],
                       (front[0] + Vector((0.0, run1)), front[1] + Vector((0.0, run1))), k * r))
    newels = [Vector((0.0, run1))]
    if u:
        if gap > 0.0:
            k += 1
            rect = [Vector((-gap, run1)), Vector((0.0, run1)), Vector((0.0, run1 + W)), Vector((-gap, run1 + W))]
            treads.append((rect, (Vector((0.0, run1)), Vector((0.0, run1 + W))), k * r))
        rot = Matrix.Rotation(math.radians(90), 2)
        off = Vector((-gap, run1))
        for poly, front in corner(W):
            k += 1
            treads.append(([rot @ p + off for p in poly], (rot @ front[0] + off, rot @ front[1] + off), k * r))
        newels.append(off.copy())
        rect = (-(W + gap), run1, W, run1 + W)
    else:
        rect = (0.0, run1, W, run1 + W)
    z2 = (a + turn) * r
    right = v['turn'] == 'RIGHT'
    if u:
        rot180 = Matrix.Rotation(math.radians(180), 4, 'Z')
        m2 = Matrix.Translation(((2 * W + gap) if right else -gap, run1, z2)) @ rot180
    elif right:
        m2 = Matrix.Translation((W, run1 + W, z2)) @ Matrix.Rotation(math.radians(-90), 4, 'Z')
    else:
        m2 = Matrix.Translation((0.0, run1, z2)) @ Matrix.Rotation(math.radians(90), 4, 'Z')
    if right:
        treads = [_mirror_tread(t, W) for t in treads]
        newels = [Vector((W - p.x, p.y)) for p in newels]
        rect = (W - rect[2], rect[1], W - rect[0], rect[3])
    flights = [Flight(a, r, T, W, Matrix.Identity(4), 0.0), Flight(b, r, T, W, m2, z2)]
    return flights, Turn(treads, rect, newels, z0, z2)


class Arc:
    """A curved or spiral stair's plan: its centre, inside and outside
    radii, the angle each tread turns, risers and riser height, and
    whether it is mirrored (turning right)."""

    def __init__(self, c, r_in, r_out, alpha, n, r, right, W):
        self.c, self.r_in, self.r_out, self.alpha = c, r_in, r_out, alpha
        self.n, self.r, self.right, self.W = n, r, right, W

    @property
    def r_walk(self):
        return (self.r_in + self.r_out) / 2.0

    def point(self, radius, phi):
        p = self.c + Vector((math.cos(phi), math.sin(phi))) * radius
        return Vector((self.W - p.x, p.y)) if self.right else p

    def tangent(self, phi):
        d = Vector((-math.sin(phi), math.cos(phi)))
        return Vector((-d.x, d.y)) if self.right else d

    def nosing_z(self, phi):
        """The line through the treads' front edges, at angle phi."""
        return self.r * phi / self.alpha + self.r


def arc_plan(v):
    """The Arc of a curved or spiral stair."""
    from . import hb_stairs
    n = hb_stairs.riser_count(v['rise'], v['max_riser'])
    if v['type'] == 'SPIRAL':
        r_in = POLE_R
        W = max(v['diameter'] / 2.0 - POLE_R, inch(12))
        alpha = math.radians(v['spiral_angle'])
    else:
        W = v['width']
        r_in = max(v['radius'], 0.0)
        alpha = v['tread'] / (r_in + W / 2.0)
    return Arc(Vector((-r_in, 0.0)), r_in, r_in + W, alpha, n, v['rise'] / n, v['turn'] == 'RIGHT', W)


def arc_treads(A):
    """[(polygon, front edge, top)] of an Arc's treads."""
    out = []
    steps = max(1, math.ceil(A.alpha / ARC_STEP))
    for i in range(A.n):
        p0, p1 = i * A.alpha, (i + 1) * A.alpha
        phis = [p0 + (p1 - p0) * j / steps for j in range(steps + 1)]
        outer = [A.point(A.r_out, ph) for ph in phis]
        inner = [A.point(A.r_in, ph) for ph in reversed(phis)]
        poly = outer + inner
        if A.right:
            poly.reverse()
        front = (A.point(A.r_in, p0), A.point(A.r_out, p0))
        if A.right:
            front = (front[1], front[0])
        out.append((poly, front, (i + 1) * A.r))
    return out


def ends(v):
    """The stair's start and end edges, each (middle, the way up there),
    for any type."""
    from .hb_stair_build import layout
    W = v['width']
    start = (Vector((W / 2.0, 0.0)), Vector((0.0, 1.0)))
    if is_arc(v):
        A = arc_plan(v)
        start = (A.point(A.r_walk, 0.0), A.tangent(0.0))
        phi = A.n * A.alpha
        return start, (A.point(A.r_walk, phi), A.tangent(phi))
    flights = layout(v)[0]
    f = flights[-1]
    mid = f.m @ Vector((f.W / 2.0, f.run, 0.0))
    up = f.m.to_3x3() @ Vector((0.0, 1.0, 0.0))
    return start, (mid.to_2d(), up.to_2d().normalized())


def walk_length(v):
    """How far a person walks up the stair along its middle."""
    from .hb_stair_build import layout
    if is_arc(v):
        A = arc_plan(v)
        return A.n * A.alpha * A.r_walk
    flights = layout(v)[0]
    run = sum(f.run for f in flights)
    if v.get('winders') and v['type'] in ('L_SHAPE', 'U_SHAPE'):
        corners = 2 if v['type'] == 'U_SHAPE' else 1
        run += corners * (math.pi / 2.0) * (v['width'] / 2.0)
        if v['type'] == 'U_SHAPE' and v['gap'] >= inch(4):
            run += v['gap']
    elif v['type'] == 'L_SHAPE':
        run += v['width']
    elif v['type'] == 'U_SHAPE':
        run += v['width'] + v['gap']
    return run
