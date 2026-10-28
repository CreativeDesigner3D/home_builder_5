"""A stair built as a stair: treads, risers and landings (the stair
object's own mesh, what is walked on and what the floor above is opened
for), and its parts beside and under them - stringers, skirt boards,
railings (newels, balusters or panels, handrails), a handrail on a wall,
and walls and a closet door under it - in a child object, Stair Parts.

The stair's frame is hb_stairs': the first flight's foot at the origin,
as wide as +x, climbing +y. Each flight is built in its own frame (x
across 0..W, y along its run, z up from its foot) and moved into the
stair's by its matrix. A flight of n risers has n treads, its last level
with what it arrives on: the floor above, or a landing.

Which sides are open, and get a railing, is worked out from the walls of
the stair's level beside them; a side along a wall gets a skirt board
and a handrail on the wall instead.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import hb_house
from .units import inch

PARTS_KEY = 'IS_STAIR_PART'

RISER_T = inch(0.75)
STRINGER_T = inch(1.5)
STRINGER_ABOVE = inch(3)        # a closed stringer's top over the nosings
STRINGER_DEPTH = inch(10)       # its bottom under them
CUT_DEPTH = inch(9)             # a cut stringer's depth under the treads
SKIRT_T = inch(0.75)
NEWEL = inch(3.5)
NEWEL_ABOVE = inch(3)
RAIL_W, RAIL_H = inch(2.25), inch(2.5)
BALUSTER = inch(1.25)
BALUSTER_STEP = inch(5.25)      # centres, under a 4" sphere's clear gap
WALL_RAIL_R = inch(0.8)
WALL_RAIL_OFF = inch(3.25)      # its centre off the wall's face
GLASS_T = inch(0.5)
PONY_T = inch(4.5)
UNDER_T = inch(0.5)
DOOR_W, DOOR_H, DOOR_T = inch(24), inch(78), inch(1.375)
WALL_NEAR = 0.12                # a side this near a wall's face is against it

RISERS_ITEMS = [('CLOSED', "Closed", "A riser under every tread"),
                ('OPEN', "Open", "No risers: open between the treads")]
STRINGER_ITEMS = [('CLOSED', "Closed", "Boards each side, the treads housed between them"),
                  ('OPEN', "Open", "Cut stringers under the treads, their ends showing"),
                  ('CENTER', "Center", "One stringer down the middle")]
RAILING_ITEMS = [('AUTO', "Open Sides", "A railing on each side not along a wall"),
                 ('NONE', "None", "No railings")]
BALUSTER_ITEMS = [('SQUARE', "Square", "Square balusters"),
                  ('ROUND', "Round", "Turned (round) balusters"),
                  ('GLASS', "Glass", "Glass panels"),
                  ('SOLID', "Half Wall", "A half wall capped with a rail")]
UNDER_ITEMS = [('OPEN', "Open", "Nothing under the stair"),
               ('WALLED', "Walled", "Walls and a soffit close the space under it"),
               ('CLOSET', "Closet", "Walled, with a door into the space")]


def construction(obj):
    """The stair's construction settings, defaults filled in."""
    return {
        'risers': obj.get('STAIR_RISERS', 'CLOSED'),
        'stringer': obj.get('STAIR_STRINGER', 'CLOSED'),
        'nosing': float(obj.get('STAIR_NOSING', inch(1))),
        'skirt': bool(obj.get('STAIR_SKIRT', True)),
        'railing': obj.get('STAIR_RAILING', 'AUTO'),
        'baluster': obj.get('STAIR_BALUSTER', 'SQUARE'),
        'rail_height': float(obj.get('STAIR_RAIL_HEIGHT', inch(36))),
        'wall_rail': bool(obj.get('STAIR_WALL_RAIL', True)),
        'under': obj.get('STAIR_UNDER', 'OPEN'),
    }


# ---- The stair's layout -------------------------------------------------------------

class Flight:
    """One flight: n risers of r, treads T deep, W wide; `m` its frame in
    the stair's, `base` the height of its foot."""

    def __init__(self, n, r, T, W, m, base):
        self.n, self.r, self.T, self.W, self.m, self.base = n, r, T, W, m, base
        self.k = r / T

    def nosing_z(self, y):
        """The line through the treads' front edges, at y along the run."""
        return self.k * y + self.r

    @property
    def run(self):
        return self.n * self.T


def layout(v):
    """(flights, landings): the stair's flights and its landing rects
    (x0, y0, x1, y1, z) in its own frame - from hb_stairs.values."""
    from . import hb_stairs, hb_stair_shapes as shapes
    if shapes.is_arc(v):
        return [], []
    if shapes.is_shaped(v):
        return shapes.winder_plan(v)[0], []
    W, T = v['width'], v['tread']
    if v['type'] == 'STRAIGHT':
        n = hb_stairs.riser_count(v['rise'], v['max_riser'])
        return [Flight(n, v['rise'] / n, T, W, Matrix.Identity(4), 0.0)], []
    a, b, r = hb_stairs.split_flights(v['rise'], v['max_riser'], v['landing_height'])
    run1, z1 = a * T, a * r
    f1 = Flight(a, r, T, W, Matrix.Identity(4), 0.0)
    if v['type'] == 'L_SHAPE':
        if v['turn'] == 'LEFT':
            m2 = Matrix.Translation((0.0, run1, z1)) @ Matrix.Rotation(math.radians(90), 4, 'Z')
        else:
            m2 = Matrix.Translation((W, run1 + W, z1)) @ Matrix.Rotation(math.radians(-90), 4, 'Z')
        landing = (0.0, run1, W, run1 + W, z1)
    else:
        gap = v['gap']
        rot = Matrix.Rotation(math.radians(180), 4, 'Z')
        if v['turn'] == 'LEFT':
            m2 = Matrix.Translation((-gap, run1, z1)) @ rot
            landing = (-(W + gap), run1, W, run1 + v['landing_depth'], z1)
        else:
            m2 = Matrix.Translation((2 * W + gap, run1, z1)) @ rot
            landing = (0.0, run1, 2 * W + gap, run1 + v['landing_depth'], z1)
    return [f1, Flight(b, r, T, W, m2, z1)], [landing]


# ---- Little solids -------------------------------------------------------------------

class _B:
    """A bmesh being filled, each solid moved by a matrix and given a
    material slot."""

    def __init__(self):
        self.bm = bmesh.new()

    def _v(self, m, p):
        return self.bm.verts.new((m @ Vector(p)).to_tuple())

    def _f(self, vs, mat):
        try:
            self.bm.faces.new(vs).material_index = mat
        except ValueError:
            pass

    def box(self, m, x0, x1, y0, y1, z0, z1, mat, caps=True):
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
            return
        v = [self._v(m, p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                     (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
        faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        if caps:
            faces += [(0, 3, 2, 1), (4, 5, 6, 7)]
        for f in faces:
            self._f([v[i] for i in f], mat)

    def profile(self, m, x0, x1, pts, mat):
        """A solid from a (y, z) outline, counter-clockwise seen from +x,
        across x0..x1."""
        if len(pts) < 3 or x1 - x0 < 1e-6:
            return
        a = [self._v(m, (x0, y, z)) for y, z in pts]
        b = [self._v(m, (x1, y, z)) for y, z in pts]
        self._f(list(reversed(a)), mat)
        self._f(b, mat)
        k = len(pts)
        for i in range(k):
            j = (i + 1) % k
            self._f([a[i], a[j], b[j], b[i]], mat)

    def beam(self, m, p, q, w, h, mat, sides=4):
        """A bar from p to q: `sides` 4, w across (x) by h up (z); more,
        a round one w across."""
        p, q = Vector(p), Vector(q)
        d = q - p
        if d.length < 1e-6:
            return
        d.normalize()
        across = Vector((1.0, 0.0, 0.0)) if abs(d.x) < 0.9 else Vector((0.0, 1.0, 0.0))
        up = d.cross(across).normalized()
        across = up.cross(d).normalized()
        if sides == 4:
            ring = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        else:
            ring = [(w / 2 * math.cos(2 * math.pi * i / sides), w / 2 * math.sin(2 * math.pi * i / sides))
                    for i in range(sides)]
        a = [self._v(m, p + across * s + up * t) for s, t in ring]
        b = [self._v(m, q + across * s + up * t) for s, t in ring]
        self._f(list(reversed(a)), mat)
        self._f(b, mat)
        k = len(ring)
        for i in range(k):
            j = (i + 1) % k
            self._f([a[i], a[j], b[j], b[i]], mat)

    def post(self, m, x, y, z0, z1, w, mat, round_=False):
        if round_:
            self.beam(m, (x, y, z0), (x, y, z1), w, w, mat, sides=8)
        else:
            self.box(m, x - w / 2, x + w / 2, y - w / 2, y + w / 2, z0, z1, mat)

    def mesh(self, name):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        mesh.update()
        return mesh


# ---- The walked-on mesh ----------------------------------------------------------------

def shaped_treads(v, c):
    """[(polygon, front edge, top)] of every tread of a stair with winders,
    or a curved or spiral one, in its frame."""
    from . import hb_stair_shapes as shapes
    if shapes.is_arc(v):
        return shapes.arc_treads(shapes.arc_plan(v))
    flights, turn = shapes.winder_plan(v)
    out = []
    for fi, f in enumerate(flights):
        x0, x1 = (STRINGER_T, f.W - STRINGER_T) if c['stringer'] == 'CLOSED' else (0.0, f.W)
        for i in range(f.n):
            pts = [(x0, i * f.T), (x1, i * f.T), (x1, (i + 1) * f.T), (x0, (i + 1) * f.T)]
            poly = [(f.m @ Vector((x, y, 0.0))).to_2d() for x, y in pts]
            out.append((poly, (poly[0], poly[1]), f.base + (i + 1) * f.r))
        if fi == 0:
            out.extend(turn.treads)
    return out


def _shaped_mesh(v, c):
    """Treads from their outlines, each with its nosing over the front
    edge, and the risers under the front edges."""
    tt = v['tread_t']
    B = _B()
    I = Matrix.Identity(4)
    prev = 0.0
    for poly, front, z in shaped_treads(v, c):
        cen = sum(poly, Vector((0.0, 0.0))) / len(poly)
        pts = list(poly)
        n_in = None
        if front is not None:
            a, b = front
            d = b - a
            if d.length > 1e-6:
                n_in = Vector((-d.y, d.x)).normalized()
                if n_in.dot(cen - a) < 0:
                    n_in = -n_in
                # the front edge's points out over the step below
                pts = [p - n_in * c['nosing'] if abs((p - a).cross(d.normalized())) < 1e-5 else p for p in pts]
        bot = [B._v(I, (p.x, p.y, z - tt)) for p in pts]
        top = [B._v(I, (p.x, p.y, z)) for p in pts]
        B._f(list(reversed(bot)), 0)
        B._f(top, 0)
        k = len(pts)
        for i in range(k):
            j = (i + 1) % k
            B._f([bot[i], bot[j], top[j], top[i]], 0)
        if c['risers'] == 'CLOSED' and n_in is not None and z - tt > prev + 1e-4:
            a, b = front
            q = [a, b, b + n_in * RISER_T, a + n_in * RISER_T]
            lo = [B._v(I, (p.x, p.y, z - (z - prev))) for p in q]
            hi = [B._v(I, (p.x, p.y, z - tt)) for p in q]
            for i in range(4):
                j = (i + 1) % 4
                B._f([lo[i], lo[j], hi[j], hi[i]], 1)
        prev = z
    return B.mesh('Stairs')


def stair_mesh(v, c):
    """Treads (slot 0), risers (1) and landings (0) as a Mesh."""
    from . import hb_stair_shapes as shapes
    if shapes.is_shaped(v):
        return _shaped_mesh(v, c)
    flights, landings = layout(v)
    tt = v['tread_t']
    B = _B()
    for f in flights:
        x0, x1 = (STRINGER_T, f.W - STRINGER_T) if c['stringer'] == 'CLOSED' else (0.0, f.W)
        for i in range(f.n):
            top = (i + 1) * f.r
            B.box(f.m, x0, x1, i * f.T - c['nosing'], (i + 1) * f.T, top - tt, top, 0)
            if c['risers'] == 'CLOSED':
                B.box(f.m, x0, x1, i * f.T, i * f.T + RISER_T, i * f.r, top - tt, 1, caps=False)
    for lx0, ly0, lx1, ly1, z in landings:
        B.box(Matrix.Identity(4), lx0, lx1, ly0, ly1, z - tt, z, 0)
    return B.mesh('Stairs')


# ---- What is beside it --------------------------------------------------------------

def _against_wall(p, q, faces):
    """Whether the plan segment p-q (world) runs along a wall's face."""
    d = q - p
    if d.length < 1e-6:
        return False
    u = d.normalized()
    mid = (p + q) / 2.0
    for a, b in faces:
        f = b - a
        if f.length < 1e-6 or abs(f.normalized().cross(u)) > 0.05:
            continue
        fu = f.normalized()
        t = (mid - a).dot(fu)
        if t < -0.05 or t > f.length + 0.05:
            continue
        if abs((mid - a).cross(fu)) < WALL_NEAR:
            return True
    return False


def _world_seg(M, f_m, p, q):
    a = M @ f_m @ Vector((p[0], p[1], 0.0))
    b = M @ f_m @ Vector((q[0], q[1], 0.0))
    return a.to_2d(), b.to_2d()


def sides(obj, v=None):
    """For each flight, which of its sides (0: x = 0, 1: x = W) runs along a
    wall; and for each landing, its edges [(p, q, along a wall)] in the
    stair's frame that no flight comes onto."""
    from . import hb_stairs
    v = v or hb_stairs.values(obj)
    flights, landings = layout(v)
    M = obj.matrix_basis if obj.parent is None else obj.matrix_world
    faces = hb_stairs.wall_faces(bpy.context.scene, [obj.get(hb_house.LEVEL_KEY, '')])
    out = []
    for f in flights:
        walls = []
        for x in (0.0, f.W):
            p, q = _world_seg(M, f.m, (x, 0.0), (x, f.run))
            walls.append(_against_wall(p, q, faces))
        out.append(walls)
    edges = []
    for lx0, ly0, lx1, ly1, _z in landings:
        corners = [(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)]
        segs = []
        for i in range(4):
            p, q = corners[i], corners[(i + 1) % 4]
            for a, b in _open_parts(p, q, flights):
                wp, wq = (M @ Vector((a[0], a[1], 0))).to_2d(), (M @ Vector((b[0], b[1], 0))).to_2d()
                segs.append((a, b, _against_wall(wp, wq, faces)))
        edges.append(segs)
    return out, edges


def _open_parts(p, q, flights):
    """The parts of a landing's edge p-q that no flight's end or foot is on."""
    p, q = Vector(p), Vector(q)
    d = q - p
    L = d.length
    if L < 1e-6:
        return []
    u = d / L
    covered = []
    for f in flights:
        for y in (0.0, f.run):
            a = (f.m @ Vector((0.0, y, 0.0))).to_2d()
            b = (f.m @ Vector((f.W, y, 0.0))).to_2d()
            # on this edge's line?
            if abs((a - p).cross(u)) > 1e-3 or abs((b - p).cross(u)) > 1e-3:
                continue
            t0, t1 = sorted(((a - p).dot(u), (b - p).dot(u)))
            covered.append((max(t0, 0.0), min(t1, L)))
    covered.sort()
    out, t = [], 0.0
    for a, b in covered:
        if a > t + 1e-3:
            out.append((t, a))
        t = max(t, b)
    if t < L - 1e-3:
        out.append((t, L))
    return [((p + u * a).to_tuple(), (p + u * b).to_tuple()) for a, b in out if b - a > inch(4)]


def _railing_along(B, m, p, q, z0_at, z_rail_at, c, mats, posts=(True, True)):
    """A railing in frame m from plan point p to q: the rail at z_rail_at(t)
    over the walking line z0_at(t) (t from 0 at p to 1 at q), with posts
    at the ends asked for and balusters, panels or a half wall between."""
    p, q = Vector((p[0], p[1])), Vector((q[0], q[1]))
    L = (q - p).length
    if L < inch(4):
        return
    u = (q - p) / L
    style = c['baluster']
    rail_mat, bal_mat, glass_mat, wall_mat = mats
    at = lambda t: p + (q - p) * t
    if style == 'SOLID':
        n = max(1, int(L / inch(12)))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            a, b = at(t0), at(t1)
            # a short upright slab per piece, following the slope
            _slab(B, m, a, b, z0_at(t0), z0_at(t1), z_rail_at(t0), z_rail_at(t1), PONY_T, wall_mat)
        B.beam(m, (*at(0), z_rail_at(0) + RAIL_H / 2), (*at(1), z_rail_at(1) + RAIL_H / 2),
               PONY_T + inch(1), RAIL_H / 2, rail_mat)
        return
    for t, on in ((0.0, posts[0]), (1.0, posts[1])):
        if on:
            c0 = at(t)
            B.post(m, c0.x, c0.y, z0_at(t) - inch(0.5), z_rail_at(t) + NEWEL_ABOVE, NEWEL, rail_mat)
    B.beam(m, (*at(0), z_rail_at(0)), (*at(1), z_rail_at(1)), RAIL_W, RAIL_H, rail_mat)
    if style == 'GLASS':
        _slab(B, m, at(0.02), at(0.98), z0_at(0.02) + inch(2), z0_at(0.98) + inch(2),
              z_rail_at(0.02) - RAIL_H / 2, z_rail_at(0.98) - RAIL_H / 2, GLASS_T, glass_mat)
        return
    n = max(1, int(L / BALUSTER_STEP))
    for i in range(n):
        t = (i + 0.5) / n
        c0 = at(t)
        B.post(m, c0.x, c0.y, z0_at(t), z_rail_at(t) - RAIL_H / 2, BALUSTER, bal_mat,
               round_=style == 'ROUND')


def _slab(B, m, a, b, za0, zb0, za1, zb1, t, mat):
    """An upright slab t thick on the plan line a-b, its bottom from za0 to
    zb0 and its top from za1 to zb1."""
    d = b - a
    if d.length < 1e-6:
        return
    n = Vector((-d.y, d.x)).normalized() * (t / 2.0)
    pts = [(a - n, za0), (b - n, zb0), (b + n, zb0), (a + n, za0),
           (a - n, za1), (b - n, zb1), (b + n, zb1), (a + n, za1)]
    v = [B._v(m, (p.x, p.y, z)) for p, z in pts]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        B._f([v[i] for i in f], mat)


def parts_mesh(obj):
    """Everything beside and under the treads, as a Mesh: slots 0
    stringers and skirts, 1 rails and newels, 2 balusters, 3 glass, 4
    walls under, 5 the closet door."""
    from . import hb_stairs
    v = hb_stairs.values(obj)
    c = construction(obj)
    flights, landings = layout(v)
    side_walls, landing_edges = sides(obj, v)
    tt = v['tread_t']
    B = _B()
    mats = (1, 2, 3, 4)
    # A U's flights side by side with no gap share their inside: the upper
    # flight's railing serves both
    shared = (v['type'] == 'U_SHAPE' and v['gap'] < inch(4))
    shared_side = 0 if v['turn'] == 'LEFT' else 1
    for fi, f in enumerate(flights):
        walls = side_walls[fi]
        ye = (f.n - 1) * f.T            # the top nosing

        def board(x0, x1, f=f, ye=ye):
            """A board along the side, over and under the nosings."""
            yb = (STRINGER_DEPTH - f.r) / f.k
            pts = [(0.0, 0.0)]
            if 0.0 < yb < ye:
                pts += [(yb, 0.0), (ye, f.nosing_z(ye) - STRINGER_DEPTH)]
            else:
                pts += [(ye, 0.0)]
            pts += [(ye, f.nosing_z(ye) + STRINGER_ABOVE), (0.0, f.r + STRINGER_ABOVE)]
            B.profile(f.m, x0, x1, _clean(pts), 0)

        def cut(x0, x1, depth=CUT_DEPTH, f=f):
            """A stringer cut to the treads: a piece under each."""
            under = lambda y: max(0.0, f.k * y + f.r - tt - depth)
            for i in range(f.n - 1):
                y0, y1 = i * f.T, (i + 1) * f.T
                top = (i + 1) * f.r - tt
                B.profile(f.m, x0, x1, _clean([(y0, under(y0)), (y1, under(y1)), (y1, top), (y0, top)]), 0)

        if c['stringer'] == 'CLOSED':
            board(0.0, STRINGER_T)
            board(f.W - STRINGER_T, f.W)
        else:
            if c['stringer'] == 'OPEN':
                xs = [inch(1), f.W - inch(1) - STRINGER_T]
                if f.W > inch(40):
                    xs.append(f.W / 2 - STRINGER_T / 2)
                for x in xs:
                    cut(x, x + STRINGER_T)
            else:
                cut(f.W / 2 - inch(1.5), f.W / 2 + inch(1.5), CUT_DEPTH + inch(3))
            if c['skirt']:
                for s, against in enumerate(walls):
                    if against:
                        x0 = 0.0 if s == 0 else f.W - SKIRT_T
                        board(x0, x0 + SKIRT_T)
        if c['railing'] == 'NONE':
            continue
        # Railings on its open sides; a handrail on a wall
        h = c['rail_height']
        y0 = f.T * 0.5 - c['nosing'] / 2
        for s, against in enumerate(walls):
            if against:
                if c['wall_rail']:
                    xw = WALL_RAIL_OFF if s == 0 else f.W - WALL_RAIL_OFF
                    B.beam(f.m, (xw, 0.0, f.nosing_z(0.0) + h), (xw, ye, f.nosing_z(ye) + h),
                           2 * WALL_RAIL_R, 2 * WALL_RAIL_R, 1, sides=8)
                continue
            if shared and fi == 0 and s == shared_side:
                continue
            inner = STRINGER_T / 2 if c['stringer'] == 'CLOSED' else inch(2)
            x = inner if s == 0 else f.W - inner

            def walk(t, f=f, y0=y0, ye=ye):
                y = y0 + (ye - y0) * t
                if c['stringer'] == 'CLOSED':
                    return f.nosing_z(y) + STRINGER_ABOVE
                i = min(max(int((y + c['nosing']) // f.T), 0), f.n - 1)
                return (i + 1) * f.r

            def rail(t, f=f, y0=y0, ye=ye):
                return f.nosing_z(y0 + (ye - y0) * t) + h
            _railing_along(B, f.m, (x, y0), (x, ye), walk, rail, c, mats, posts=(True, False))
    # Landings: railings along their open edges
    if c['railing'] != 'NONE':
        for li, (lx0, ly0, lx1, ly1, z) in enumerate(landings):
            centre = Vector(((lx0 + lx1) / 2.0, (ly0 + ly1) / 2.0))
            for a, b, against in landing_edges[li]:
                if against:
                    continue
                a, b = Vector(a[:2]), Vector(b[:2])
                d = (b - a).normalized()
                n = Vector((-d.y, d.x))
                if n.dot(centre - (a + b) / 2.0) < 0:
                    n = -n
                _railing_along(B, Matrix.Identity(4), a + n * inch(2), b + n * inch(2),
                               lambda t, z=z: z, lambda t, z=z: z + c['rail_height'], c, mats)
    from . import hb_stair_shapes as shapes
    if shapes.is_arc(v):
        _arc_parts(B, v, c, shapes.arc_plan(v), mats)
    elif shapes.is_shaped(v):
        _turn_parts(B, obj, v, c, flights, shapes.winder_plan(v)[1], mats)
    if c['under'] in ('WALLED', 'CLOSET') and not shapes.is_arc(v):
        _under(B, obj, v, c, flights, landings, side_walls, landing_edges)
    return B.mesh('Stair Parts')


def _turn_edges(obj, v, flights, turn):
    """The open edges of a turn of winders: [(a, b, along a wall)]."""
    from . import hb_stairs
    M = obj.matrix_basis if obj.parent is None else obj.matrix_world
    faces = hb_stairs.wall_faces(bpy.context.scene, [obj.get(hb_house.LEVEL_KEY, '')])
    x0, y0, x1, y1 = turn.rect
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for i in range(4):
        for a, b in _open_parts(corners[i], corners[(i + 1) % 4], flights):
            wa, wb = (M @ Vector((a[0], a[1], 0))).to_2d(), (M @ Vector((b[0], b[1], 0))).to_2d()
            out.append((Vector(a[:2]), Vector(b[:2]), _against_wall(wa, wb, faces)))
    return out


def _seg_cross(a, b, p, q):
    """Where segment a-b crosses p-q, as a fraction along a-b, or None."""
    r, s = b - a, q - p
    den = r.cross(s)
    if abs(den) < 1e-9:
        return None
    t = (p - a).cross(s) / den
    u = (p - a).cross(r) / den
    if 1e-6 < t < 1 - 1e-6 and -1e-6 <= u <= 1 + 1e-6:
        return t
    return None


def _in_poly(p, poly):
    inside = False
    k = len(poly)
    for i in range(k):
        a, b = poly[i], poly[(i + 1) % k]
        if (a.y > p.y) != (b.y > p.y):
            x = a.x + (p.y - a.y) * (b.x - a.x) / (b.y - a.y)
            if x > p.x:
                inside = not inside
    return inside


def _over_treads(a, b, treads):
    """The edge a-b split where riser lines cross it: [(t0, t1, top of the
    tread under that piece)], and the height a rail follows at each
    break (between the two treads' tops)."""
    ts = sorted({0.0, 1.0} | {t for _p, fr, _z in treads if fr is not None
                              for t in [_seg_cross(a, b, fr[0], fr[1])] if t is not None})
    pieces = []
    for t0, t1 in zip(ts, ts[1:]):
        mid = a + (b - a) * ((t0 + t1) / 2.0)
        z = next((zt for poly, _f, zt in treads if _in_poly(mid, poly)), None)
        if z is None:
            z = min(treads, key=lambda tr: (sum(tr[0], Vector((0, 0))) / len(tr[0]) - mid).length)[2]
        pieces.append((t0, t1, z))
    return pieces


def _piece_heights(pieces):
    """The walking line's height at each piece's ends: halfway between the
    treads where they meet, each tread's own at the edge's ends."""
    out = []
    for i, (t0, t1, z) in enumerate(pieces):
        za = z if i == 0 else (pieces[i - 1][2] + z) / 2.0
        zb = z if i == len(pieces) - 1 else (pieces[i + 1][2] + z) / 2.0
        out.append((za, zb))
    return out


def _turn_parts(B, obj, v, c, flights, turn, mats):
    """A turn of winders: a newel at each inside corner, and along its open
    edges a stringer, a railing and (under) a wall."""
    I = Matrix.Identity(4)
    h = c['rail_height']
    cen = Vector(((turn.rect[0] + turn.rect[2]) / 2.0, (turn.rect[1] + turn.rect[3]) / 2.0))
    if c['railing'] != 'NONE':
        for p in turn.newels:
            B.post(I, p.x, p.y, 0.0, turn.z1 + h + NEWEL_ABOVE, NEWEL, 1)
    for a, b, against in _turn_edges(obj, v, flights, turn):
        d = (b - a).normalized()
        n = Vector((-d.y, d.x))
        if n.dot(cen - (a + b) / 2.0) < 0:
            n = -n
        pieces = _over_treads(a + n * inch(2), b + n * inch(2), turn.treads)
        heights = _piece_heights(pieces)
        last = len(pieces) - 1
        for i, ((t0, t1, z), (za, zb)) in enumerate(zip(pieces, heights)):
            pa, pb = a + (b - a) * t0, a + (b - a) * t1
            if c['stringer'] == 'CLOSED':
                _slab(B, I, pa + n * (STRINGER_T / 2), pb + n * (STRINGER_T / 2),
                      max(0.0, za - STRINGER_DEPTH), max(0.0, zb - STRINGER_DEPTH),
                      za + STRINGER_ABOVE, zb + STRINGER_ABOVE, STRINGER_T, 0)
            if c['under'] in ('WALLED', 'CLOSET') and not against:
                _slab(B, I, pa + n * (UNDER_T / 2), pb + n * (UNDER_T / 2), 0.0, 0.0,
                      max(0.0, za - STRINGER_DEPTH), max(0.0, zb - STRINGER_DEPTH), UNDER_T, 4)
            if against or c['railing'] == 'NONE':
                continue
            ra, rb = pa + n * inch(2), pb + n * inch(2)
            walk_z = (lambda t, z=z: z) if c['stringer'] != 'CLOSED' else \
                (lambda t, za=za, zb=zb: za + (zb - za) * t + STRINGER_ABOVE)
            _railing_along(B, I, ra, rb, walk_z, lambda t, za=za, zb=zb: za + (zb - za) * t + h,
                           c, mats, posts=(i == 0, i == last))


def _arc_parts(B, v, c, A, mats):
    """A curved or spiral stair: railings round its outside (and a curved
    one's inside), its stringers or a spiral's pole."""
    import math
    I = Matrix.Identity(4)
    h = c['rail_height']
    spiral = v['type'] == 'SPIRAL'
    end = (A.n - 1) * A.alpha
    if spiral:
        c0 = A.point(0.0, 0.0)
        B.post(I, c0.x, c0.y, 0.0, v['rise'] + h, 2 * A.r_in, 0, round_=True)
    steps = max(1, math.ceil(A.alpha / math.radians(10)))
    phis = [A.alpha * 0.5] + [A.alpha * (i + j / steps) for i in range(1, A.n - 1) for j in range(steps)] + [end]
    phis = sorted(set(round(p, 9) for p in phis if p <= end + 1e-9))
    sides_ = [A.r_out - inch(2)] if spiral else [A.r_in + inch(2), A.r_out - inch(2)]
    tread_top = lambda ph: (min(int(ph / A.alpha + 1e-9), A.n - 1) + 1) * A.r
    if c['railing'] != 'NONE':
        for radius in sides_:
            last = len(phis) - 2
            for i, (p0, p1) in enumerate(zip(phis, phis[1:])):
                a, b = A.point(radius, p0), A.point(radius, p1)
                pm = (p0 + p1) / 2.0
                walk = (lambda t, z=tread_top(pm): z)
                rail = (lambda t, p0=p0, p1=p1: A.nosing_z(p0 + (p1 - p0) * t) + h)
                _railing_along(B, I, a, b, walk, rail, c, mats, posts=(i == 0, i == last))
    if spiral:
        return
    # A curved stair's stringers: boards round both edges, or one under the middle
    allp = [A.alpha * i / steps for i in range(int(end / A.alpha * steps) + 1)] + [end]
    allp = sorted(set(round(p, 9) for p in allp))
    for p0, p1 in zip(allp, allp[1:]):
        if c['stringer'] == 'CLOSED':
            for radius in (A.r_in + STRINGER_T / 2, A.r_out - STRINGER_T / 2):
                a, b = A.point(radius, p0), A.point(radius, p1)
                _slab(B, I, a, b, max(0.0, A.nosing_z(p0) - STRINGER_DEPTH), max(0.0, A.nosing_z(p1) - STRINGER_DEPTH),
                      A.nosing_z(p0) + STRINGER_ABOVE, A.nosing_z(p1) + STRINGER_ABOVE, STRINGER_T, 0)
        else:
            a, b = A.point(A.r_walk, p0), A.point(A.r_walk, p1)
            top0 = tread_top(p0 + 1e-6) - v['tread_t']
            _slab(B, I, a, b, max(0.0, A.nosing_z(p0) - v['tread_t'] - CUT_DEPTH - A.r),
                  max(0.0, A.nosing_z(p1) - v['tread_t'] - CUT_DEPTH - A.r), top0, top0,
                  inch(3) if c['stringer'] == 'CENTER' else STRINGER_T, 0)


def _clean(pts):
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def _underside(f, y):
    """The underside of a flight at y along it, from its foot."""
    return max(0.0, f.nosing_z(y) - STRINGER_DEPTH)


def _under(B, obj, v, c, flights, landings, side_walls, landing_edges):
    """Walls round the space under the stair, a soffit under each flight,
    and for a closet a door in the tallest of the walls."""
    from . import hb_stairs
    M = obj.matrix_basis if obj.parent is None else obj.matrix_world
    faces = hb_stairs.wall_faces(bpy.context.scene, [obj.get(hb_house.LEVEL_KEY, '')])
    spots = []                  # (height free, flight, 'END' or the side, y of the door's middle)
    last = len(flights) - 1
    for fi, f in enumerate(flights):
        ye = (f.n - 1) * f.T
        B.beam(f.m, (f.W / 2, 0.0, _underside(f, 0.0) - UNDER_T / 2),
               (f.W / 2, ye, _underside(f, ye) - UNDER_T / 2), f.W, UNDER_T, 4)
        for s, against in enumerate(side_walls[fi]):
            if against:
                continue
            x0 = 0.0 if s == 0 else f.W - UNDER_T
            pts = [(0.0, -f.base), (ye, -f.base), (ye, _underside(f, ye)), (0.0, _underside(f, 0.0))]
            B.profile(f.m, x0, x0 + UNDER_T, _clean(pts), 4)
            yd = ye - DOOR_W / 2 - inch(4)
            if yd - DOOR_W / 2 > 0.0:
                spots.append((f.base + _underside(f, yd - DOOR_W / 2), 0, f, s, yd))
        if fi == last:
            p, q = _world_seg(M, f.m, (0.0, ye), (f.W, ye))
            if not _against_wall(p, q, faces):
                top = _underside(f, ye)
                B.box(f.m, 0.0, f.W, ye - UNDER_T, ye, -f.base, top, 4)
                # the tall end first, when a door fits there
                spots.append((f.base + top, 1 if f.base + top >= DOOR_H + inch(2) else 0, f, 'END', ye))
    tt = v['tread_t']
    for li, (_x0, _y0, _x1, _y1, z) in enumerate(landings):
        for a, b, against in landing_edges[li]:
            if not against:
                _slab(B, Matrix.Identity(4), Vector(a[:2]), Vector(b[:2]), 0.0, 0.0, z - tt, z - tt, UNDER_T, 4)
    if c['under'] != 'CLOSET' or not spots:
        return
    free, _first, f, where, y = max(spots, key=lambda sp: (sp[1], sp[0]))
    dh = min(DOOR_H, free - inch(2))
    if dh < inch(48):
        return
    z0 = -f.base
    if where == 'END':
        x = f.W / 2
        B.box(f.m, x - DOOR_W / 2, x + DOOR_W / 2, y, y + DOOR_T, z0 + inch(0.5), z0 + dh, 5)
        B.post(f.m, x + DOOR_W / 2 - inch(2.5), y + DOOR_T + inch(1), z0 + inch(36), z0 + inch(37.5),
               inch(1.5), 1, round_=True)
    else:
        x0, x1 = (-DOOR_T, 0.0) if where == 0 else (f.W, f.W + DOOR_T)
        B.box(f.m, x0, x1, y - DOOR_W / 2, y + DOOR_W / 2, z0 + inch(0.5), z0 + dh, 5)
        kx = x0 - inch(1) if where == 0 else x1 + inch(1)
        B.post(f.m, kx, y - DOOR_W / 2 + inch(2.5), z0 + inch(36), z0 + inch(37.5), inch(1.5), 1, round_=True)


# ---- Materials ---------------------------------------------------------------------------

def _mat(name, color, roughness=0.5, glass=False):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = color + (1.0,)
            bsdf.inputs['Roughness'].default_value = roughness
            if glass:
                for key in ('Transmission Weight', 'Transmission'):
                    if key in bsdf.inputs:
                        bsdf.inputs[key].default_value = 1.0
                        break
        mat.diffuse_color = color + ((0.3,) if glass else (1.0,))
        if glass and hasattr(mat, 'surface_render_method'):
            mat.surface_render_method = 'BLENDED'
    return mat


def materials(obj):
    """The stair's materials: (tread, riser, stringer, rail, baluster,
    glass, wall, door) - its own picks, or the defaults."""
    st = obj.hb_stair
    tread = st.tread_material or _mat("HB Stair Tread", (0.52, 0.34, 0.18), 0.45)
    paint = _mat("HB Stair Paint", (0.92, 0.91, 0.88), 0.5)
    riser = st.riser_material or paint
    stringer = st.stringer_material or paint
    rail = st.rail_material or _mat("HB Handrail", (0.36, 0.22, 0.11), 0.4)
    baluster = st.baluster_material or paint
    glass = _mat("HB Stair Glass", (0.85, 0.92, 0.95), 0.05, glass=True)
    wall = _mat("HB Stair Wall", (0.90, 0.89, 0.86), 0.8)
    door = _mat("HB Stair Door", (0.93, 0.92, 0.90), 0.45)
    return tread, riser, stringer, rail, baluster, glass, wall, door


# ---- Building -------------------------------------------------------------------------

def parts_of(obj):
    return next((c for c in obj.children if c.get(PARTS_KEY)), None)


def build(obj):
    """The stair's treads and risers, and its parts, from its settings."""
    from . import hb_stairs, hb_utils
    v = hb_stairs.values(obj)
    c = construction(obj)
    tread, riser, stringer, rail, baluster, glass, wall, door = materials(obj)
    old = obj.data
    mesh = stair_mesh(v, c)
    mesh.materials.append(tread)
    mesh.materials.append(riser)
    obj.data = mesh
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    pm = parts_mesh(obj)
    for m in (stringer, rail, baluster, glass, wall, door):
        pm.materials.append(m)
    parts = parts_of(obj)
    if parts is None:
        parts = hb_utils.new_object("Stair Parts", pm)
        for col in obj.users_collection or [bpy.context.scene.collection]:
            col.objects.link(parts)
        parts.parent = obj
        parts.matrix_parent_inverse.identity()
        parts[PARTS_KEY] = True
        if obj.get(hb_house.LEVEL_KEY):
            parts[hb_house.LEVEL_KEY] = obj[hb_house.LEVEL_KEY]
    else:
        oldp = parts.data
        parts.data = pm
        if oldp is not None and oldp.users == 0:
            bpy.data.meshes.remove(oldp)
    return parts
