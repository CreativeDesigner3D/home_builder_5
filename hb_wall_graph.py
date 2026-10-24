"""
Wall junction graph.

Works out how walls meet - free ends, straight runs, L corners, T
junctions and 3+ way junctions - from wall positions alone, and how each
wall end has to be cut so the walls close cleanly against each other.

Pure Python on plain tuples (no bpy, no mathutils) so it can be tested
outside Blender. walls.py turns GeoNodeWall objects into Segs and writes
the answers back onto the walls' geometry-node inputs.

Wall convention (same as GeoNodeWall): a wall runs from `start` to `end`
along its reference line, and its thickness is extruded to the LEFT of
that direction. So the reference line is one face of the wall (w = 0)
and the far face is offset by the thickness (w = t).

An end cut is described by two offsets along the wall's own direction,
measured from the reference endpoint: `a` where the cut meets the
reference face and `b` where it meets the far face. (0, 0) is a square
end. to_inputs() turns them into the wall's Extension and Angle inputs.
"""

import math
from collections import namedtuple

JOIN_TOL = 0.01                 # endpoints closer than this meet (m)
COLLINEAR_EPS = 1e-6            # |cross| of unit vectors below this is parallel
MAX_CUT_RATIO = 8.0             # a cut longer than this many thicknesses is a spike

FREE, STRAIGHT, L_CORNER, TEE, MULTI = 'FREE', 'STRAIGHT', 'L', 'T', 'MULTI'
START, END = 'start', 'end'


# ---- Small vector helpers ----------------------------------------------------

def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _add(a, b): return (a[0] + b[0], a[1] + b[1])
def _mul(a, k): return (a[0] * k, a[1] * k)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1]
def _cross(a, b): return a[0] * b[1] - a[1] * b[0]
def _len(a): return math.hypot(a[0], a[1])
def _left(a): return (-a[1], a[0])


def intersect(p, d, q, e):
    """Intersection of lines p + s*d and q + r*e, or None if parallel."""
    den = _cross(d, e)
    if abs(den) < 1e-12:
        return None
    s = _cross(_sub(q, p), e) / den
    return _add(p, _mul(d, s))


# ---- Input -------------------------------------------------------------------

class Seg:
    """One wall's reference line."""

    __slots__ = ('id', 'start', 'end', 'thickness', 'level', 'wall_type',
                 'length', 'dir', 'normal')

    def __init__(self, id, start, end, thickness, level='', wall_type=''):
        self.id = id
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))
        self.thickness = float(thickness)
        self.level = level
        self.wall_type = wall_type
        v = _sub(self.end, self.start)
        self.length = _len(v)
        self.dir = _mul(v, 1.0 / self.length) if self.length > 1e-12 else (1.0, 0.0)
        self.normal = _left(self.dir)     # thickness side

    def point(self, which):
        return self.start if which == START else self.end

    def away(self, which):
        """Unit vector from this end INTO the wall."""
        return self.dir if which == START else _mul(self.dir, -1.0)

    def face_point(self, w):
        """A point on the face line offset `w` from the reference line."""
        return _add(self.start, _mul(self.normal, w))


Host = namedtuple('Host', 'seg_id t side')   # side: 'REF' or 'FAR'


class Node:
    __slots__ = ('point', 'ends', 'host', 'corner', 'kind')

    def __init__(self, point, ends):
        self.point = point
        self.ends = ends          # [(seg_id, START|END), ...]
        self.host = None          # Host for a T node
        self.corner = None        # Node whose corner a lone end sits in
        self.kind = FREE


class Graph:
    def __init__(self, segs, nodes):
        self.segs = segs                          # id -> Seg
        self.nodes = nodes
        self.node_of = {}                         # (seg_id, which) -> Node
        for node in nodes:
            for end in node.ends:
                self.node_of[end] = node

    def tees(self):
        return [n for n in self.nodes if n.kind == TEE]


# ---- Building the graph ------------------------------------------------------

def build_graph(segs, tol=JOIN_TOL):
    """Nodes for every wall end. Walls only meet walls on the same level."""
    by_id = {s.id: s for s in segs if s.length > 1e-9}
    nodes = []
    by_level = {}
    for s in by_id.values():
        by_level.setdefault(s.level, []).append(s)
    for level_segs in by_level.values():
        nodes.extend(_level_nodes(level_segs, tol))
    return Graph(by_id, nodes)


def _level_nodes(segs, tol):
    ends = [(s.id, which, s.point(which)) for s in segs for which in (START, END)]

    # Cluster coincident endpoints (union-find)
    parent = list(range(len(ends)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            if _len(_sub(ends[i][2], ends[j][2])) < tol:
                parent[find(i)] = find(j)
    clusters = {}
    for i in range(len(ends)):
        clusters.setdefault(find(i), []).append(i)

    by_id = {s.id: s for s in segs}
    nodes = []
    for members in clusters.values():
        pts = [ends[i][2] for i in members]
        point = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        node = Node(point, [(ends[i][0], ends[i][1]) for i in members])
        if len(node.ends) == 1:
            node.host = _find_host(by_id[node.ends[0][0]], node.ends[0][1],
                                   point, segs, tol)
        node.kind = _kind(node, by_id)
        nodes.append(node)

    # A lone end that lands in the corner of another junction - on its
    # outside corner, or inside the square where two walls overlap - is
    # joined to that junction, though it touches no wall's span. Its cut
    # stays square; this only joins it up for finding rooms.
    node_of = {end: node for node in nodes for end in node.ends}
    for node in nodes:
        if node.kind == FREE:
            seg_id, which = node.ends[0]
            node.corner = _find_corner(by_id[seg_id], node.point, segs,
                                       node_of, tol)
    return nodes


def _find_corner(seg, point, segs, node_of, tol):
    best, best_d = None, None
    for host in segs:
        if host.id == seg.id:
            continue
        rel = _sub(point, host.start)
        w = _dot(rel, host.normal)
        if not (-tol <= w <= host.thickness + tol):
            continue
        t = _dot(rel, host.dir)
        if t <= tol:
            which = START
        elif t >= host.length - tol:
            which = END
        else:
            continue            # partway along: that would be a T
        other = node_of.get((host.id, which))
        if other is None or len(other.ends) < 2:
            continue            # a junction's corner, not a free end's
        d = _len(_sub(point, other.point))
        if d > 1.5 * (host.thickness + seg.thickness):
            continue
        if best_d is None or d < best_d:
            best, best_d = other, d
    return best


def _find_host(seg, which, point, segs, tol):
    """The wall a lone end lands on partway along: its endpoint lies inside
    the host's span, on or between the host's two faces."""
    best = None
    best_d = None
    for host in segs:
        if host.id == seg.id:
            continue
        if abs(_cross(seg.dir, host.dir)) < 1e-3:
            continue                    # parallel walls don't tee
        rel = _sub(point, host.start)
        t = _dot(rel, host.dir)
        if not (tol < t < host.length - tol):
            continue
        w = _dot(rel, host.normal)
        if not (-tol <= w <= host.thickness + tol):
            continue
        d_ref, d_far = abs(w), abs(w - host.thickness)
        d = min(d_ref, d_far)
        if best_d is None or d < best_d:
            best_d = d
            best = Host(host.id, t, 'REF' if d_ref <= d_far else 'FAR')
    return best


def _kind(node, by_id):
    n = len(node.ends)
    if n == 1:
        return TEE if node.host is not None else FREE
    if n == 2:
        (ia, wa), (ib, wb) = node.ends
        ua, ub = by_id[ia].away(wa), by_id[ib].away(wb)
        if abs(_cross(ua, ub)) < COLLINEAR_EPS and _dot(ua, ub) < 0:
            return STRAIGHT
        return L_CORNER
    return MULTI


# ---- Solving the cuts ---------------------------------------------------------

def solve(graph):
    """{(seg_id, which): (a, b)} for every wall end in the graph."""
    cuts = {}
    for node in graph.nodes:
        if node.kind in (FREE, STRAIGHT):
            for end in node.ends:
                cuts[end] = (0.0, 0.0)
        elif node.kind == L_CORNER:
            ea, eb = node.ends
            cuts[ea], cuts[eb] = _corner_cut(graph, ea, eb, node.point)
        elif node.kind == TEE:
            end = node.ends[0]
            cuts[end] = _tee_cut(graph.segs[end[0]], end[1],
                                 graph.segs[node.host.seg_id])
        else:
            cuts.update(_multi_cuts(graph, node))
    return cuts


def _offsets(seg, which, ref_pt, far_pt):
    p = seg.point(which)
    return (_dot(_sub(ref_pt, p), seg.dir), _dot(_sub(far_pt, p), seg.dir))


def _too_long(seg, cut):
    limit = MAX_CUT_RATIO * max(seg.thickness, 1e-6)
    return abs(cut[0]) > limit or abs(cut[1]) > limit


def _bisector_cut(seg, which, other, other_which, point):
    """Cut both walls on the bisector through the node: the fallback when
    the face intersections run away (walls that barely turn but differ in
    thickness)."""
    ux, uy = seg.away(which), other.away(other_which)
    m = _sub(ux, uy)
    if _len(m) < 1e-12:
        return (0.0, 0.0)
    line_dir = _left(_mul(m, 1.0 / _len(m)))
    far = intersect(seg.face_point(seg.thickness), seg.dir, point, line_dir)
    if far is None:
        return (0.0, 0.0)
    return (0.0, _dot(_sub(far, seg.point(which)), seg.dir))


def _corner_cut(graph, ea, eb, point):
    """Two wall ends meeting at one point. The cut joins where their inner
    faces cross to where their outer faces cross; 'inner' is the face of
    each wall on the side the other wall turns towards."""
    x, y = graph.segs[ea[0]], graph.segs[eb[0]]
    ux, uy = x.away(ea[1]), y.away(eb[1])
    if abs(_cross(ux, uy)) < COLLINEAR_EPS:
        return (0.0, 0.0), (0.0, 0.0)

    def faces(seg, toward):
        # (inner w, outer w) for this wall
        if _dot(toward, seg.normal) > 0:
            return seg.thickness, 0.0
        return 0.0, seg.thickness

    xi, xo = faces(x, uy)
    yi, yo = faces(y, ux)
    inner = intersect(x.face_point(xi), x.dir, y.face_point(yi), y.dir)
    outer = intersect(x.face_point(xo), x.dir, y.face_point(yo), y.dir)
    if inner is None or outer is None:
        return (0.0, 0.0), (0.0, 0.0)

    def cut(seg, which, inner_w):
        # The reference face takes whichever crossing lies on it
        if inner_w == 0.0:
            return _offsets(seg, which, inner, outer)
        return _offsets(seg, which, outer, inner)

    cx = cut(x, ea[1], xi)
    cy = cut(y, eb[1], yi)
    if _too_long(x, cx) or _too_long(y, cy):
        return (_bisector_cut(x, ea[1], y, eb[1], point),
                _bisector_cut(y, eb[1], x, ea[1], point))
    return cx, cy


def _tee_cut(seg, which, host):
    """A wall end landing on another wall: cut it along the host's face on
    the side this wall is on."""
    u = seg.away(which)
    w = host.thickness if _dot(u, host.normal) > 0 else 0.0
    q = host.face_point(w)
    ref = intersect(seg.start, seg.dir, q, host.dir)
    far = intersect(seg.face_point(seg.thickness), seg.dir, q, host.dir)
    if ref is None or far is None:
        return (0.0, 0.0)
    cut = _offsets(seg, which, ref, far)
    return (0.0, 0.0) if _too_long(seg, cut) else cut


def _multi_cuts(graph, node):
    """Three or more ends at one point: the two that run most nearly
    straight through (exterior walls first) join as a corner or a straight
    run, and every other end butts into whichever of those two it meets
    on the side its thickness lies."""
    ends = node.ends
    segs = graph.segs
    best, best_score = None, None
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            si, sj = segs[ends[i][0]], segs[ends[j][0]]
            score = -_dot(si.away(ends[i][1]), sj.away(ends[j][1]))
            if si.wall_type == 'Exterior' and sj.wall_type == 'Exterior':
                score += 0.5
            if best_score is None or score > best_score:
                best, best_score = (i, j), score
    ea, eb = ends[best[0]], ends[best[1]]
    cuts = {}
    sa, sb = segs[ea[0]], segs[eb[0]]
    if abs(_cross(sa.away(ea[1]), sb.away(eb[1]))) < COLLINEAR_EPS:
        cuts[ea] = cuts[eb] = (0.0, 0.0)
    else:
        cuts[ea], cuts[eb] = _corner_cut(graph, ea, eb, node.point)
    for k, end in enumerate(ends):
        if k in best:
            continue
        seg = segs[end[0]]
        # The through wall that runs out from the node towards this
        # wall's body is the one it sits against.
        host_end = max((ea, eb), key=lambda e: _dot(segs[e[0]].away(e[1]), seg.normal))
        cuts[end] = _tee_cut(seg, end[1], segs[host_end[0]])
    return cuts


# ---- Output --------------------------------------------------------------------

def to_inputs(seg, which, cut, has_extension=True):
    """(extension, angle) for the wall's Left (start) or Right (end) inputs.

    The geometry node moves the end's vertices by the extension along the
    wall (start: backwards, end: forwards), then shears the far-face
    corner by tan(angle) * thickness. Without the extension inputs (a
    file whose wall node predates them) the reference corner can't move,
    so the far corner alone is placed."""
    a, b = cut
    t = seg.thickness
    if not has_extension:
        return 0.0, math.atan2(b, t) if t else 0.0
    angle = math.atan2(b - a, t) if t else 0.0
    ext = -a if which == START else a
    return ext, angle


# ---- Rooms ---------------------------------------------------------------------
# A room is a closed area of walls on one level. The walls' reference lines
# are joined into a planar graph - a wall that tees into another is carried
# on to that wall's reference line, and the host is split there - and every
# bounded face of that graph is a room. Its outline is then moved off the
# reference lines onto the wall face that looks into the room, so a room's
# polygon is its inside: what the floor, ceiling and area are made from.

# polygon: the room's inside (its area, its ceiling). floor: the same room
# carried to the middle of its walls, so the floors of two rooms meet
# under the wall between them and an opening in it has floor beneath.
# wall_types: the kinds of wall around the room ('Railing' marks a deck).
RoomArea = namedtuple('RoomArea', 'level polygon area floor wall_types')

ROOM_MIN_AREA = 0.05            # m2; smaller faces are slivers between walls
NOT_ROOM_WALLS = ('Half', 'Fake')


def polygon_area(poly):
    """Signed area; positive when the points run counter-clockwise."""
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def point_in_polygon(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _dist_to_edges(pt, poly):
    best = None
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ab = _sub(b, a)
        L2 = _dot(ab, ab)
        t = 0.0 if L2 < 1e-18 else max(0.0, min(1.0, _dot(_sub(pt, a), ab) / L2))
        d = _len(_sub(pt, _add(a, _mul(ab, t))))
        best = d if best is None else min(best, d)
    return best or 0.0


def interior_point(poly):
    """A point well inside the polygon: its centroid when that is inside,
    otherwise the sampled point farthest from every edge (an L-shaped
    room's centroid can fall outside it)."""
    area = polygon_area(poly)
    if abs(area) > 1e-12:
        cx = cy = 0.0
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            f = x1 * y2 - x2 * y1
            cx += (x1 + x2) * f
            cy += (y1 + y2) * f
        c = (cx / (6.0 * area), cy / (6.0 * area))
        if point_in_polygon(c, poly) and _dist_to_edges(c, poly) > 0.15:
            return c
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    best, best_d = None, -1.0
    steps = 24
    for i in range(1, steps):
        for j in range(1, steps):
            p = (min(xs) + (max(xs) - min(xs)) * i / steps,
                 min(ys) + (max(ys) - min(ys)) * j / steps)
            if not point_in_polygon(p, poly):
                continue
            d = _dist_to_edges(p, poly)
            if d > best_d:
                best, best_d = p, d
    return best if best is not None else poly[0]


def find_rooms(segs, tol=JOIN_TOL):
    """Every room on every level: [RoomArea]. Half and fake walls don't
    divide rooms."""
    walls = [s for s in segs if s.length > 1e-9 and s.wall_type not in NOT_ROOM_WALLS]
    by_level = {}
    for s in walls:
        by_level.setdefault(s.level, []).append(s)
    rooms = []
    for level, level_segs in by_level.items():
        for poly, floor, types in _level_room_polygons(level_segs, tol):
            rooms.append(RoomArea(level, poly, polygon_area(poly), floor, types))
    return rooms


def _level_room_polygons(segs, tol):
    graph = build_graph(segs, tol)
    by_id = graph.segs

    # Vertices, merged within tol
    verts = []

    def vid(p):
        for i, q in enumerate(verts):
            if _len(_sub(p, q)) < tol:
                return i
        verts.append(p)
        return len(verts) - 1

    # Stations along each wall's reference line: its two ends, carried on
    # to the host's reference line at a T, plus every T landing on it.
    stations = {s.id: [] for s in by_id.values()}
    node_vid = {}
    for s in by_id.values():
        for which in (START, END):
            node = graph.node_of.get((s.id, which))
            if node is None:
                continue
            p = node.point
            if node.kind == TEE:
                host = by_id[node.host.seg_id]
                q = intersect(s.start, s.dir, host.start, host.dir)
                if q is not None:
                    p = q
                    t = _dot(_sub(q, host.start), host.dir)
                    stations[host.id].append((t, vid(q)))
            node_vid[id(node)] = vid(p)
            stations[s.id].append((_dot(_sub(p, s.start), s.dir), vid(p)))

    edges = []                  # (u, v, seg)
    seen = set()
    for sid, sts in stations.items():
        sts.sort()
        for (t0, a), (t1, b) in zip(sts, sts[1:]):
            if a == b or t1 - t0 < tol:
                continue
            key = (min(a, b), max(a, b))
            if key in seen:
                continue        # two walls on the same line: count once
            seen.add(key)
            edges.append((a, b, by_id[sid]))

    # A lone end in another junction's corner is joined to it by a short
    # link that carries no wall face of its own
    for node in graph.nodes:
        if node.corner is None:
            continue
        a, b = node_vid.get(id(node)), node_vid.get(id(node.corner))
        if a is None or b is None or a == b:
            continue
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            edges.append((a, b, None))

    # Drop dead ends: a wall end touching nothing can't bound a room
    while True:
        degree = {}
        for a, b, _s in edges:
            degree[a] = degree.get(a, 0) + 1
            degree[b] = degree.get(b, 0) + 1
        kept = [e for e in edges if degree[e[0]] > 1 and degree[e[1]] > 1]
        if len(kept) == len(edges):
            break
        edges = kept
    if not edges:
        return []

    # Half-edges and the faces they bound (each face on its half-edges' left)
    out = {}
    for i, (a, b, _s) in enumerate(edges):
        out.setdefault(a, []).append((i, a, b))
        out.setdefault(b, []).append((i, b, a))
    for v, hs in out.items():
        hs.sort(key=lambda h: math.atan2(verts[h[2]][1] - verts[v][1],
                                         verts[h[2]][0] - verts[v][0]))

    def next_half(h):
        i, a, b = h
        around = out[b]
        k = next(k for k, g in enumerate(around) if g[0] == i and g[2] == a)
        return around[(k - 1) % len(around)]

    used = set()
    polys = []
    for start in [h for hs in out.values() for h in hs]:
        if start in used:
            continue
        face = []
        h = start
        while h not in used:
            used.add(h)
            face.append(h)
            h = next_half(h)
        pts = [verts[h[1]] for h in face]
        if polygon_area(pts) <= ROOM_MIN_AREA:
            continue            # the outside of the building, or a sliver
        inside = _inside_polygon(face, edges, verts)
        if inside and polygon_area(inside) > ROOM_MIN_AREA:
            floor = _inside_polygon(face, edges, verts, mid_wall=True)
            types = frozenset(edges[i][2].wall_type for i, _a, _b in face
                              if edges[i][2] is not None)
            polys.append((inside, floor or inside, types))
    return polys


def _inside_polygon(face, edges, verts, mid_wall=False):
    """The face moved off the reference lines onto the faces of the walls
    that look into it - or, with mid_wall, onto the middle of each wall."""
    lines = []
    for i, a, b in face:
        seg = edges[i][2]
        if seg is None:
            continue            # a corner link: the faces either side meet
        into_room = _left(_sub(verts[b], verts[a]))
        if mid_wall:
            w = seg.thickness / 2.0
        else:
            w = seg.thickness if _dot(into_room, seg.normal) > 0 else 0.0
        lines.append((seg.face_point(w), seg.dir, verts[a]))
    pts = []
    n = len(lines)
    for k in range(n):
        p1, d1, _v1 = lines[k - 1]
        p2, d2, v2 = lines[k]
        if abs(_cross(d1, d2)) < 1e-9:
            # Parallel neighbours: the same line carries on (nothing to
            # add), or a step where two walls of different thickness meet
            if abs(_cross(d1, _sub(p2, p1))) < 1e-6:
                continue
            for p, d in ((p1, d1), (p2, d2)):
                pts.append(_add(p, _mul(d, _dot(_sub(v2, p), d))))
            continue
        q = intersect(p1, d1, p2, d2)
        if q is not None:
            pts.append(q)
    clean = []
    for p in pts:
        if not clean or _len(_sub(p, clean[-1])) > 1e-6:
            clean.append(p)
    if len(clean) > 1 and _len(_sub(clean[0], clean[-1])) < 1e-6:
        clean.pop()
    # Points partway along a straight edge (a T on the far side, a corner
    # link) add nothing to the outline
    changed = True
    while changed and len(clean) > 3:
        changed = False
        for k in range(len(clean)):
            a, p, b = clean[k - 1], clean[k], clean[(k + 1) % len(clean)]
            if abs(_cross(_sub(p, a), _sub(b, p))) < 1e-9:
                del clean[k]
                changed = True
                break
    return clean if len(clean) >= 3 else None
