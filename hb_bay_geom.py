"""Bay, bow and box windows' plan geometry - pure, no Blender.

Coordinates are a bay's own: x along the host wall from the bay's left
end, o out from the host wall's outdoor face. A bay's outline runs from
(0, 0) out and round to (width, 0), clockwise; the host wall closes it.
"""

import math


def bay_plan(kind, width, depth, angle=math.radians(45), segments=5):
    """The outline's corners [(x, o)] from (0, 0) to (width, 0).
    'BAY': angled sides at `angle` to the wall, a front parallel to it;
    'BOX': square sides; 'BOW': `segments` chords of the arc through both
    ends that stands `depth` out at its middle."""
    if kind == 'BOX':
        return [(0.0, 0.0), (0.0, depth), (width, depth), (width, 0.0)]
    if kind == 'BOW':
        n = max(int(segments), 2)
        half = width / 2.0
        r = (half * half + depth * depth) / (2.0 * depth)
        cx, co = half, depth - r
        a0 = math.atan2(0.0 - co, 0.0 - cx)
        a1 = math.atan2(0.0 - co, width - cx)
        pts = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((cx + r * math.cos(a), co + r * math.sin(a)))
        pts[0], pts[-1] = (0.0, 0.0), (width, 0.0)
        return pts
    run = depth / math.tan(angle)
    run = min(run, width / 2.0 - 1e-3)
    return [(0.0, 0.0), (run, depth), (width - run, depth), (width, 0.0)]


def _inward(a, b):
    """The unit normal of segment a-b toward the outline's inside (to its
    right: the outline runs clockwise)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    return (dy / length, -dx / length)


def _meet(p, d, q, e):
    """Where the line through p along d meets the one through q along e."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-12:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


def offset(points, dist):
    """The outline moved `dist` inward (outward when negative), each side
    square to itself: its corners where the moved sides meet, its ends
    where the first and last meet the host wall (o = 0)."""
    lines = []
    for a, b in zip(points, points[1:]):
        n = _inward(a, b)
        lines.append(((a[0] + n[0] * dist, a[1] + n[1] * dist), (b[0] - a[0], b[1] - a[1])))
    out = [_meet(lines[0][0], lines[0][1], (0.0, 0.0), (1.0, 0.0)) or lines[0][0]]
    for (p, d), (q, e) in zip(lines, lines[1:]):
        out.append(_meet(p, d, q, e) or q)
    p, d = lines[-1]
    out.append(_meet(p, d, (0.0, 0.0), (1.0, 0.0)) or (p[0] + d[0], p[1] + d[1]))
    return out


def area(poly):
    a = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        a += x0 * y1 - x1 * y0
    return a / 2.0


def _clip(poly, f):
    """Sutherland-Hodgman: the part of a convex polygon where f(p) <= 0,
    f linear."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = f(p), f(q)
        if fp <= 1e-12:
            out.append(p)
        if (fp < -1e-12 < fq) or (fq < -1e-12 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def hip_facets(points, roof_poly, pitch):
    """A hip over the bay, its host side not sloping: for each side of
    the outline, the part of `roof_poly` where that side's slope is the
    lowest. Heights are pitch x the distance in from the side, so add the
    plate. Returns [(polygon, side index)], each counter-clockwise."""
    sides = []
    for a, b in zip(points, points[1:]):
        sides.append((a, _inward(a, b)))

    def rise(i, p):
        a, n = sides[i]
        return pitch * ((p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1])

    poly = list(roof_poly)
    if area(poly) < 0:
        poly.reverse()
    out = []
    for i in range(len(sides)):
        facet = poly
        for j in range(len(sides)):
            if j != i and facet:
                facet = _clip(facet, lambda p, i=i, j=j: rise(i, p) - rise(j, p))
        if len(facet) >= 3 and abs(area(facet)) > 1e-9:
            out.append((facet, i))
    return out


def hip_height(points, pitch, p):
    """The hip's rise over the plate at p: the lowest of the sides' slopes."""
    best = None
    for a, b in zip(points, points[1:]):
        n = _inward(a, b)
        z = pitch * ((p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1])
        best = z if best is None else min(best, z)
    return best
