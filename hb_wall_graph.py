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
    __slots__ = ('point', 'ends', 'host', 'kind')

    def __init__(self, point, ends):
        self.point = point
        self.ends = ends          # [(seg_id, START|END), ...]
        self.host = None          # Host for a T node
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
    return nodes


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
