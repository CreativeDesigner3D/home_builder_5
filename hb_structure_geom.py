"""Plan geometry for the house's structure, in plain Python.

No bpy here: points are (x, y) tuples, so all of it can be tested without
Blender, as hb_wall_graph is. Stairwell openings use it now; foundations,
trusses and the floor deck will add their own pieces.
"""

# ---- A union of axis-aligned rectangles --------------------------------------
# A stairwell opening is the treads that need headroom, each a rectangle
# in the stair's own space. Their union is cut on a grid of every edge
# coordinate: a cell is in it when its middle is in some rectangle.

EPS = 1e-6
GRID_TOL = 1e-5                 # edges this close are one grid line


def _lines(vals):
    """Grid lines through the values, those closer than GRID_TOL merged:
    two treads' edges a float's noise apart are one line, not a sliver."""
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > GRID_TOL:
            out.append(v)
    return out


def _grid(rects):
    xs = _lines(v for r in rects for v in (r[0], r[2]))
    ys = _lines(v for r in rects for v in (r[1], r[3]))
    covered = set()
    for i in range(len(xs) - 1):
        cx = (xs[i] + xs[i + 1]) / 2.0
        for j in range(len(ys) - 1):
            cy = (ys[j] + ys[j + 1]) / 2.0
            if any(r[0] - EPS <= cx <= r[2] + EPS and r[1] - EPS <= cy <= r[3] + EPS
                   for r in rects):
                covered.add((i, j))
    return xs, ys, covered


def rect_union_cells(rects):
    """The union of rectangles (x0, y0, x1, y1) as non-overlapping cells
    on the grid of their edges, sharing whole edges with each other."""
    rects = [r for r in rects if r[2] - r[0] > EPS and r[3] - r[1] > EPS]
    if not rects:
        return []
    xs, ys, covered = _grid(rects)
    return [(xs[i], ys[j], xs[i + 1], ys[j + 1]) for i, j in sorted(covered)]


def rect_union_area(rects):
    return sum((c[2] - c[0]) * (c[3] - c[1]) for c in rect_union_cells(rects))


def rect_union_edges(rects, merge=True):
    """The outline of a union of rectangles as straight edges, each
    (start, end, outward normal), collinear pieces joined - or, without
    `merge`, one per grid cell side, so they meet the cells' corners."""
    rects = [r for r in rects if r[2] - r[0] > EPS and r[3] - r[1] > EPS]
    if not rects:
        return []
    xs, ys, covered = _grid(rects)
    runs = {}       # (normal, line coordinate) -> [(t0, t1)]
    for i, j in covered:
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
        if (i - 1, j) not in covered:
            runs.setdefault(((-1, 0), x0), []).append((y0, y1))
        if (i + 1, j) not in covered:
            runs.setdefault(((1, 0), x1), []).append((y0, y1))
        if (i, j - 1) not in covered:
            runs.setdefault(((0, -1), y0), []).append((x0, x1))
        if (i, j + 1) not in covered:
            runs.setdefault(((0, 1), y1), []).append((x0, x1))
    edges = []
    for (normal, c), spans in runs.items():
        spans.sort()
        if not merge:
            for a, b in spans:
                edges.append(((c, a), (c, b), normal) if normal[0] != 0
                             else ((a, c), (b, c), normal))
            continue
        merged = [list(spans[0])]
        for a, b in spans[1:]:
            if a <= merged[-1][1] + EPS:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        for a, b in merged:
            if normal[0] != 0:
                edges.append(((c, a), (c, b), normal))
            else:
                edges.append(((a, c), (b, c), normal))
    return edges


# ---- Intervals ---------------------------------------------------------------

def subtract_intervals(span, holes):
    """The parts of interval `span` (a, b) outside the `holes` intervals."""
    a, b = span
    out = [(a, b)]
    for h0, h1 in sorted(holes):
        nxt = []
        for s0, s1 in out:
            if h1 <= s0 + EPS or h0 >= s1 - EPS:
                nxt.append((s0, s1))
                continue
            if h0 > s0 + EPS:
                nxt.append((s0, h0))
            if h1 < s1 - EPS:
                nxt.append((h1, s1))
        out = nxt
    return out


def segment_in_polygon_spans(a, b, poly):
    """Where segment a-b crosses inside a polygon, as parameter intervals
    (t0, t1) along it, 0 at a and 1 at b."""
    ts = []
    n = len(poly)
    dx, dy = b[0] - a[0], b[1] - a[1]
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        ex, ey = q[0] - p[0], q[1] - p[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((p[0] - a[0]) * ey - (p[1] - a[1]) * ex) / den
        u = ((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / den
        if -EPS <= u <= 1 + EPS:
            ts.append(t)
    ts = sorted(t for t in ts if 0.0 - EPS <= t <= 1.0 + EPS)
    ts = [min(max(t, 0.0), 1.0) for t in ts]
    out = []
    pts = [0.0] + ts + [1.0]
    for t0, t1 in zip(pts, pts[1:]):
        if t1 - t0 < EPS:
            continue
        m = (t0 + t1) / 2.0
        if _inside((a[0] + dx * m, a[1] + dy * m), poly):
            if out and abs(out[-1][1] - t0) < EPS:
                out[-1] = (out[-1][0], t1)
            else:
                out.append((t0, t1))
    return out


def _inside(pt, poly):
    x, y = pt
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


# ---- Offsets -----------------------------------------------------------------

def offset_polygon(poly, d):
    """A polygon's edges moved out by `d` (in by a negative `d`), corners
    where the moved edges meet. Counter-clockwise in, counter-clockwise
    out, one point per point; for the footings and slab round a house's
    outline, whose corners are walls' corners, never needle-thin."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
               for i in range(n)) / 2.0
    sign = 1.0 if area > 0 else -1.0
    lines = []
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        length = (dx * dx + dy * dy) ** 0.5
        if length < EPS:
            lines.append(None)
            continue
        # The outward normal of a counter-clockwise edge is on its right
        nx, ny = dy / length * sign, -dx / length * sign
        lines.append(((ax + nx * d, ay + ny * d), (dx / length, dy / length)))
    out = []
    for i in range(n):
        l0, l1 = lines[i - 1], lines[i]
        if l0 is None or l1 is None:
            p = l1[0] if l1 else (l0[0] if l0 else poly[i])
            out.append(p)
            continue
        (p0, d0), (p1, d1) = l0, l1
        den = d0[0] * d1[1] - d0[1] * d1[0]
        if abs(den) < 1e-9:
            out.append(p1)          # straight on: the moved point itself
            continue
        t = ((p1[0] - p0[0]) * d1[1] - (p1[1] - p0[1]) * d1[0]) / den
        out.append((p0[0] + d0[0] * t, p0[1] + d0[1] * t))
    return out


def polygon_area(poly):
    n = len(poly)
    return sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
               for i in range(n)) / 2.0
