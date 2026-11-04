"""Roof surfaces with sloped ends - pure geometry, no Blender.

A mansard, a clipped gable or a Dutch gable is the lower of two
profiles: one across the roof, f(u), and one along it, g(v), each a
polyline of (position, height) carried on past its ends down its end
slopes. Where g is higher than `cut` it stops counting (a Dutch gable's
hips end there, and a small upright gable rises over them).

Within a cell of the grid made by both profiles' corners, f and g are
both straight, so where f = g is a straight line: each cell is one
facet, or two either side of that line. Facets that meet share their
points exactly, so the surface can be closed into solids.
"""

EPS = 1e-9


def at(points, x):
    """A polyline's height at x, carried straight on past its ends."""
    if len(points) == 1:
        return points[0][1]
    if x <= points[0][0]:
        (a, za), (b, zb) = points[0], points[1]
    elif x >= points[-1][0]:
        (a, za), (b, zb) = points[-2], points[-1]
    else:
        for (a, za), (b, zb) in zip(points, points[1:]):
            if a <= x <= b:
                break
    if abs(b - a) < EPS:
        return za
    return za + (zb - za) * (x - a) / (b - a)


def crossings(points, level, lo, hi):
    """Where a polyline passes through `level`, between lo and hi."""
    out = []
    xs = sorted({lo, hi} | {x for x, _z in points if lo < x < hi})
    for a, b in zip(xs, xs[1:]):
        za, zb = at(points, a) - level, at(points, b) - level
        if za * zb < 0:
            out.append(a + (b - a) * za / (za - zb))
    return out


def _grid(points, lo, hi, extra=()):
    xs = {lo, hi} | {x for x, _z in points if lo + EPS < x < hi - EPS} | set(extra)
    xs = sorted(xs)
    out = []
    for x in xs:
        if not out or x - out[-1] > 1e-7:
            out.append(x)
    return out


class Surface:
    """The lower of f(u) and g(v) over [u0, u1] x [v0, v1]: facets as
    lists of (u, v, z), counter-clockwise seen from above."""

    def __init__(self, f, g, u0, u1, v0, v1, cut=None):
        self.f, self.g, self.cut = f, g, cut
        self.u0, self.u1, self.v0, self.v1 = u0, u1, v0, v1
        extra_u = crossings(f, cut, u0, u1) if (g and cut is not None) else ()
        extra_v = crossings(g, cut, v0, v1) if (g and cut is not None) else ()
        self.us = _grid(f, u0, u1, extra_u)
        self.vs = _grid(g, v0, v1, extra_v) if g else [v0, v1]
        self.steps = list(extra_v)
        self.faces = []
        self._build()

    def g_on(self, v):
        """True where the end profile counts at v."""
        if not self.g:
            return False
        return self.cut is None or at(self.g, v) <= self.cut + 1e-9

    def z(self, u, v, g_on=None):
        zf = at(self.f, u)
        if g_on is None:
            g_on = self.g_on(v)
        return min(zf, at(self.g, v)) if g_on else zf

    def _build(self):
        for j in range(len(self.vs) - 1):
            va, vb = self.vs[j], self.vs[j + 1]
            g_on = self.g_on((va + vb) / 2.0)
            for i in range(len(self.us) - 1):
                ua, ub = self.us[i], self.us[i + 1]
                corners = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
                if not g_on:
                    self.faces.append([(u, v, at(self.f, u)) for u, v in corners])
                    continue
                h = [at(self.f, u) - at(self.g, v) for u, v in corners]
                if all(x >= -EPS for x in h) or all(x <= EPS for x in h):
                    self.faces.append([(u, v, self.z(u, v, True)) for u, v in corners])
                    continue
                f_side, g_side = [], []
                for k in range(4):
                    (u, v), hk = corners[k], h[k]
                    (u2, v2), h2 = corners[(k + 1) % 4], h[(k + 1) % 4]
                    p = (u, v, self.z(u, v, True))
                    if hk <= EPS:
                        f_side.append(p)
                    if hk >= -EPS:
                        g_side.append(p)
                    if (hk < -EPS and h2 > EPS) or (hk > EPS and h2 < -EPS):
                        q = self._cross(u, v, u2, v2)
                        f_side.append(q)
                        g_side.append(q)
                for poly in (f_side, g_side):
                    if len(poly) >= 3:
                        self.faces.append(poly)
        # A Dutch gable's upright gables, where the hips stop
        for vc in self.steps:
            for ua, ub in zip(self.us, self.us[1:]):
                za, zb = at(self.f, ua), at(self.f, ub)
                # Only where the roof across stands above the cut (the
                # grid has a corner wherever it passes through it)
                if min(za, zb) < self.cut - 1e-7 or max(za, zb) <= self.cut + 1e-7:
                    continue
                self.faces.append([(ua, vc, self.cut), (ub, vc, self.cut), (ub, vc, zb), (ua, vc, za)])

    def _cross(self, u, v, u2, v2):
        """Where f = g along a cell's edge (one of u or v is fixed on it)."""
        if abs(u - u2) < EPS:
            # Along v at u: g(v) = f(u)
            target = at(self.f, u)
            a, b = sorted((v, v2))
            za, zb = at(self.g, a) - target, at(self.g, b) - target
            vv = a + (b - a) * za / (za - zb)
            return (u, vv, target)
        target = at(self.g, v)
        a, b = sorted((u, u2))
        za, zb = at(self.f, a) - target, at(self.f, b) - target
        uu = a + (b - a) * za / (za - zb)
        return (uu, v, target)

    def side(self, name):
        """The surface's points along one side of its rectangle, in order
        round the rectangle counter-clockwise: 'v0' (u rising), 'u1',
        'v1' (u falling), 'u0'."""
        fixed, coord = {'v0': (self.v0, 1), 'v1': (self.v1, 1),
                        'u0': (self.u0, 0), 'u1': (self.u1, 0)}[name]
        seen = {}
        for face in self.faces:
            for p in face:
                if abs(p[coord] - fixed) < 1e-7:
                    seen[(round(p[0], 7), round(p[1], 7), round(p[2], 7))] = p
        pts = list(seen.values())
        other = 1 - coord
        reverse = name in ('v1', 'u0')
        pts.sort(key=lambda p: (p[other], p[2]), reverse=reverse)
        return pts


def slab_faces(bottom, top):
    """A closed slab between two surfaces over the same rectangle: the
    underside, the top and its four edges."""
    faces = [list(reversed(f)) for f in bottom.faces] + [list(f) for f in top.faces]
    for name in ('v0', 'u1', 'v1', 'u0'):
        b, t = bottom.side(name), top.side(name)
        faces.append(b + list(reversed(t)))
    return faces


def box_faces(surface, cap_z, above):
    """A closed solid between a surface and a flat cap at cap_z: the
    volume over it when `above` (what a roof trims away), under it
    otherwise."""
    faces = [list(f) if above else list(reversed(f)) for f in surface.faces]
    corners = [(surface.u0, surface.v0), (surface.u1, surface.v0),
               (surface.u1, surface.v1), (surface.u0, surface.v1)]
    cap = [(u, v, cap_z) for u, v in corners]
    faces.append(list(reversed(cap)) if above else cap)
    for k, name in enumerate(('v0', 'u1', 'v1', 'u0')):
        pts = surface.side(name)
        a, b = cap[k], cap[(k + 1) % 4]
        faces.append(pts + [b, a])
    return faces
