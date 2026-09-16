"""
Countertop pieces both product libraries share: how an island is grouped
into one slab, and the finishing every new top needs.

An island is rarely a single cabinet. It is a row of them, usually with a
second row back to back behind it, and often with a dishwasher or a
beverage centre standing between two of them. Sizing a top to each
cabinet in turn gives an island as many separate slabs as it has boxes,
with a hole wherever an appliance sits -- an appliance is not a cabinet,
so nothing claimed that stretch.

So members are grouped first. Two members belong to the same island when
their footprints touch, and grouping is transitive, which is what lets a
back row bridge a gap the front row has: a dishwasher between two base
cabinets is spanned even if the dishwasher itself were left out, because
the run behind touches both sides of it.

The group's top is one slab over the union of the footprints, measured in
the frame of one member so a rotated island stays square to itself
rather than to the world.

A range is deliberately not an island member. It gets no countertop --
the same rule the wall runs follow -- so it does not join a group, and an
island split by one comes out as two tops, which is correct.

The library's own countertop module owns the overhang and thickness
settings and passes them in; nothing here reads a property group.

A top is not stuck with the rectangle it was measured into. The outline
it was built from is kept on the object, and the slab is rebuilt from
that outline whenever it changes -- which is what lets an island top be
pushed out over a seating overhang, or cut back around a corner, without
the cabinets underneath having to pretend to be that shape.

Every top also goes through finish(), which stamps the right-click menu
and lays down UVs. The UVs matter more than they look: a procedural
material reads the UV output of a Texture Coordinate node, and a mesh
with NO uv layer hands that node (0, 0) at every point -- so the whole
slab samples a single spot of the texture and renders as one flat
colour. That is why a countertop used to need unwrapping by hand
before its material would show.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from ... import hb_types
from ... import hb_utils

MENU_ID = 'HOME_BUILDER_MT_countertop_commands'

# Footprints closer than this count as touching. Wide enough for a
# filler or a scribe gap, far short of any real separation between two
# islands.
JOIN_GAP = 0.0254          # 1 inch

# Appliances that stand under a countertop and so belong to the island.
# A range is excluded on purpose (see the module docstring); anything
# taller than the cabinets, a refrigerator, is excluded by height.
UNDER_COUNTER_MARGIN = 4 * 0.0254

# The top's shape, held on the object so it survives a rebuild and a
# file round trip. OUTLINE is a flat list of local XY pairs going round
# the slab; TOP is the local Z of its underside and THICKNESS its depth.
# An ID property can hold a flat list of floats and not much else, which
# is why the outline is stored the way it is.
OUTLINE_KEY = 'ct_outline'
TOP_KEY = 'ct_top_z'
THICKNESS_KEY = 'ct_thickness'

# How each outline corner is finished, three floats per corner in outline
# order: (kind, size back along the edge before it, size on along the
# edge after it). A radius uses the first size as its radius. The corner
# the user drags stays the sharp one; the slab is built from the outline
# with these applied, so moving an edge carries its clipped or rounded
# corners along instead of flattening them into plain points.
CORNERS_KEY = 'ct_corners'
CORNER_SHARP = 0
CORNER_CLIP = 1
CORNER_RADIUS = 2

# Optional per-edge data, one float per corner for the edge leaving it
# (corner i -> corner i + 1). A top that uses it -- a wood top marks which
# edges are finished -- carries it as a fourth field on each corner
# tuple, and every shape edit hands it on: an edge split in two, or a
# step put into one, gives the new edges the value of the edge they came
# from. Tops without the key get plain three-field corners.
EDGES_KEY = 'ct_edges'

# Degrees of arc per segment of a rounded corner.
ARC_STEP_DEG = 7.5

# Two outline points closer than this are the same corner.
POINT_TOL = 1e-6


def footprint(obj):
    """World-space XY corners of an object's cage.

    The cage runs local X 0..dim_x and local Y 0..-dim_y -- the body
    hangs off the origin line towards the front, which is the same
    convention the wall runs use.
    """
    cage = hb_types.GeoNodeCage(obj)
    dim_x = cage.get_input('Dim X')
    dim_y = cage.get_input('Dim Y')
    corners = [(0.0, 0.0), (dim_x, 0.0), (dim_x, -dim_y), (0.0, -dim_y)]
    return [obj.matrix_world @ Vector((x, y, 0.0)) for x, y in corners]


def _bounds(points):
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def _touching(a_pts, b_pts, gap):
    """Do two footprints touch or overlap, within gap?

    Compared as world-axis boxes. Two islands at an angle to each other
    could in principle be called touching when they only pass close by,
    but they would have to be within an inch to do it.
    """
    ax0, ax1, ay0, ay1 = _bounds(a_pts)
    bx0, bx1, by0, by1 = _bounds(b_pts)
    return (ax0 - gap <= bx1 and bx0 - gap <= ax1
            and ay0 - gap <= by1 and by0 - gap <= ay1)


def group_members(members, gap=JOIN_GAP):
    """Split island members into connected groups by touching footprint.

    Returns a list of lists, each in the order the members came in.
    """
    prints = [footprint(m) for m in members]
    groups = []
    unassigned = set(range(len(members)))
    while unassigned:
        seed = min(unassigned)
        unassigned.discard(seed)
        group = [seed]
        frontier = [seed]
        while frontier:
            i = frontier.pop()
            for j in sorted(unassigned):
                if _touching(prints[i], prints[j], gap):
                    unassigned.discard(j)
                    group.append(j)
                    frontier.append(j)
        groups.append([members[i] for i in sorted(group)])
    return groups


def _faces_opposite(a, b):
    """True when b is turned roughly 180 degrees from a -- the back-to-
    back island, whose far side is another front rather than a back."""
    delta = abs((a.matrix_world.to_euler().z - b.matrix_world.to_euler().z))
    delta = delta % (2.0 * math.pi)
    return abs(delta - math.pi) < 0.2


def create_group_countertop(context, members, overhang_front, overhang_sides,
                            overhang_back, thickness, library,
                            cabinets=None):
    """One slab over a whole island. Returns the new object, or None.

    ``members`` are the cabinets and under-counter appliances of one
    island; ``cabinets`` are just the cabinets, which is what sets the
    height -- a dishwasher is shorter than the boxes beside it and must
    not pull the top down.
    """
    if not members:
        return None
    cabinets = cabinets or members
    anchor = cabinets[0]
    to_local = anchor.matrix_world.inverted()

    # Every footprint in the anchor's frame, so a rotated island is
    # measured square to itself.
    local = []
    for member in members:
        local.extend(to_local @ p for p in footprint(member))
    x0, x1, y0, y1 = _bounds(local)

    # The anchor's own body runs to -Y, so local -Y is a front. The
    # far side is a front too when anything faces the other way.
    back_overhang = (overhang_front
                     if any(_faces_opposite(anchor, m) for m in members)
                     else overhang_back)
    x0 -= overhang_sides
    x1 += overhang_sides
    y0 -= overhang_front
    y1 += back_overhang

    top = None
    for cab in cabinets:
        cage = hb_types.GeoNodeCage(cab)
        corner = cab.matrix_world @ Vector((0.0, 0.0, cage.get_input('Dim Z')))
        z = (to_local @ corner).z
        top = z if top is None else max(top, z)
    if top is None:
        return None

    obj = hb_utils.new_object('Countertop',
                               bpy.data.meshes.new('Countertop'))
    obj.parent = anchor
    obj.matrix_parent_inverse.identity()
    obj['IS_COUNTERTOP'] = True
    context.scene.collection.objects.link(obj)
    # The measured rectangle is only where the top STARTS. It is stored
    # as an outline and the slab built from that, so reshaping it later
    # is the same operation as building it now.
    obj[TOP_KEY] = float(top)
    obj[THICKNESS_KEY] = float(thickness)
    set_outline(obj, ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
    obj['MENU_ID'] = MENU_ID
    obj['HB_COUNTERTOP_LIB'] = library
    rebuild(obj)
    return obj


def outline_of(obj):
    """The top's outline as a list of local (x, y) corners."""
    flat = obj.get(OUTLINE_KEY) or []
    return [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]


def corners_of(obj):
    """One (kind, size_before, size_after) per outline corner, plus the
    edge value leaving it when the top keeps per-edge data."""
    count = len(outline_of(obj))
    flat = list(obj.get(CORNERS_KEY) or [])
    edges = obj.get(EDGES_KEY)
    edges = list(edges) if edges is not None else None
    out = []
    for i in range(count):
        j = i * 3
        if j + 2 < len(flat):
            c = (int(round(flat[j])), float(flat[j + 1]), float(flat[j + 2]))
        else:
            c = (CORNER_SHARP, 0.0, 0.0)
        if edges is not None:
            c = c + (float(edges[i]) if i < len(edges) else 0.0,)
        out.append(c)
    return out


def _extras(corner):
    """The per-edge fields of a corner tuple, if any."""
    return tuple(corner[3:]) if corner is not None else ()


def sharp_like(corner):
    """A sharp corner that keeps ``corner``'s edge data -- what a point
    inserted along that corner's edge gets."""
    return (CORNER_SHARP, 0.0, 0.0) + _extras(corner)


def dedupe_shape(points, corners=None):
    """Drop corners that repeat the one before, wrapping round the end.

    A drag that pushes one edge onto its neighbour would otherwise leave
    a zero-length edge behind, and a face built on one of those is a
    face with no area. A dropped corner takes its finish with it -- the
    survivor keeps whichever finish it already had -- and the survivor
    takes over the dropped corner's edge, and with it that edge's data.
    """
    corners = list(corners) if corners is not None else None
    pts, cns = [], []
    for i, (x, y) in enumerate(points):
        if pts and (abs(pts[-1][0] - x) < POINT_TOL
                    and abs(pts[-1][1] - y) < POINT_TOL):
            if corners is not None and i < len(corners):
                head = (cns[-1] if cns[-1][0] != CORNER_SHARP
                        else corners[i])
                cns[-1] = tuple(head[:3]) + _extras(corners[i])
            continue
        pts.append((float(x), float(y)))
        cns.append(corners[i] if corners is not None and i < len(corners)
                   else (CORNER_SHARP, 0.0, 0.0))
    while len(pts) > 1 and (abs(pts[0][0] - pts[-1][0]) < POINT_TOL
                            and abs(pts[0][1] - pts[-1][1]) < POINT_TOL):
        pts.pop()
        cns.pop()
    return pts, cns


def set_outline(obj, points, corners=None):
    """Store an outline and, optionally, how each corner is finished.

    Without ``corners`` every corner is left sharp.
    """
    pts, cns = dedupe_shape(points, corners)
    flat = []
    for x, y in pts:
        flat.extend((x, y))
    obj[OUTLINE_KEY] = flat
    if corners is not None and cns and len(cns[0]) > 3:
        obj[EDGES_KEY] = [float(c[3]) for c in cns]
    if corners is None or all(c[0] == CORNER_SHARP for c in cns):
        if CORNERS_KEY in obj:
            del obj[CORNERS_KEY]
        return
    flat = []
    for c in cns:
        flat.extend((float(c[0]), float(c[1]), float(c[2])))
    obj[CORNERS_KEY] = flat


def signed_area(points):
    """Twice the signed area: positive when the outline runs
    anticlockwise."""
    total = 0.0
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        total += a[0] * b[1] - b[0] * a[1]
    return total


def _segments_cross(p1, p2, p3, p4):
    """Do segments p1p2 and p3p4 properly cross (touching ends aside)?"""
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1 = orient(p3, p4, p1)
    d2 = orient(p3, p4, p2)
    d3 = orient(p1, p2, p3)
    d4 = orient(p1, p2, p4)
    eps = 1e-12
    return ((d1 > eps and d2 < -eps) or (d1 < -eps and d2 > eps)) and \
           ((d3 > eps and d4 < -eps) or (d3 < -eps and d4 > eps))


def is_simple(points, min_area=1e-6):
    """Is the outline one solid piece: no edge crossing another, and
    some area to it? A drag that folds the slab over itself is refused
    rather than built."""
    count = len(points)
    if count < 3 or abs(signed_area(points)) / 2.0 < min_area:
        return False
    for i in range(count):
        a, b = points[i], points[(i + 1) % count]
        for j in range(i + 2, count):
            if i == 0 and j == count - 1:
                continue
            c, d = points[j], points[(j + 1) % count]
            if _segments_cross(a, b, c, d):
                return False
    return True


def _unit(dx, dy):
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return None, 0.0
    return (dx / length, dy / length), length


def corner_tangents(points, corners):
    """How far each corner's finish reaches along its two edges, clamped
    so neighbouring finishes on one edge never run past each other.

    Returns one (reach_before, reach_after) per corner. A radius is
    turned into its tangent length here, which is what the edges see.
    """
    count = len(points)
    want = []
    for i in range(count):
        kind, s0, s1 = (corners[i] if i < len(corners)
                        else (CORNER_SHARP, 0, 0))[:3]
        if kind == CORNER_CLIP:
            want.append([max(0.0, s0), max(0.0, s1)])
        elif kind == CORNER_RADIUS:
            c = points[i]
            u0, _ = _unit(points[i - 1][0] - c[0], points[i - 1][1] - c[1])
            u1, _ = _unit(points[(i + 1) % count][0] - c[0],
                          points[(i + 1) % count][1] - c[1])
            if u0 is None or u1 is None:
                want.append([0.0, 0.0])
                continue
            cos_t = max(-1.0, min(1.0, u0[0] * u1[0] + u0[1] * u1[1]))
            theta = math.acos(cos_t)
            if theta < 1e-3 or theta > math.pi - 1e-3:
                want.append([0.0, 0.0])      # straight or folded: nothing to round
                continue
            t = max(0.0, s0) / math.tan(theta / 2.0)
            want.append([t, t])
        else:
            want.append([0.0, 0.0])

    # Each edge i -> i+1 is shared by corner i's "after" reach and corner
    # i+1's "before" reach. Keep a sliver of straight edge between them.
    for i in range(count):
        j = (i + 1) % count
        _, length = _unit(points[j][0] - points[i][0],
                          points[j][1] - points[i][1])
        total = want[i][1] + want[j][0]
        limit = length * 0.999
        if total > limit and total > 0.0:
            k = limit / total
            want[i][1] *= k
            want[j][0] *= k
    # A radius needs the same tangent on both sides; take the smaller.
    for i in range(count):
        kind = corners[i][0] if i < len(corners) else CORNER_SHARP
        if kind == CORNER_RADIUS:
            t = min(want[i])
            want[i] = [t, t]
    return [tuple(w) for w in want]


def expand_outline(points, corners):
    """The slab's real outline: the dragged corners with each finish cut
    in -- a clip becomes two points, a radius a run of arc points."""
    return expand_outline_edges(points, corners)[0]


def expand_outline_edges(points, corners):
    """expand_outline, plus the edge value of every edge of the result.

    An edge that is part of a design edge keeps that edge's value; the
    short edges a clip or a radius adds take the larger of the two edges
    they join, so a clipped corner between a finished edge and an
    unfinished one is finished. Without per-edge data every value is 0.
    """
    count = len(points)

    def value(i):
        c = corners[i % count] if (i % count) < len(corners) else None
        extra = _extras(c)
        return float(extra[0]) if extra else 0.0

    if count < 3:
        return list(points), [value(i) for i in range(count)]
    reach = corner_tangents(points, corners)
    out, vals = [], []
    for i in range(count):
        c = points[i]
        kind = corners[i][0] if i < len(corners) else CORNER_SHARP
        joint = max(value(i - 1), value(i))
        r0, r1 = reach[i]
        if kind == CORNER_SHARP or (r0 < POINT_TOL and r1 < POINT_TOL):
            out.append(c)
            vals.append(value(i))
            continue
        u0, _ = _unit(points[i - 1][0] - c[0], points[i - 1][1] - c[1])
        u1, _ = _unit(points[(i + 1) % count][0] - c[0],
                      points[(i + 1) % count][1] - c[1])
        if u0 is None or u1 is None:
            out.append(c)
            vals.append(value(i))
            continue
        p0 = (c[0] + u0[0] * r0, c[1] + u0[1] * r0)
        p1 = (c[0] + u1[0] * r1, c[1] + u1[1] * r1)
        if kind == CORNER_CLIP:
            out.extend((p0, p1))
            vals.extend((joint, value(i)))
            continue
        # Radius: the arc centre sits on the bisector, square to both
        # tangent points.
        bis, _ = _unit(u0[0] + u1[0], u0[1] + u1[1])
        cos_t = max(-1.0, min(1.0, u0[0] * u1[0] + u0[1] * u1[1]))
        theta = math.acos(cos_t)
        if bis is None or theta < 1e-3:
            out.extend((p0, p1))
            vals.extend((joint, value(i)))
            continue
        radius = r0 * math.tan(theta / 2.0)
        dist = radius / math.sin(theta / 2.0)
        centre = (c[0] + bis[0] * dist, c[1] + bis[1] * dist)
        a0 = math.atan2(p0[1] - centre[1], p0[0] - centre[0])
        a1 = math.atan2(p1[1] - centre[1], p1[0] - centre[0])
        sweep = a1 - a0
        while sweep > math.pi:
            sweep -= 2.0 * math.pi
        while sweep < -math.pi:
            sweep += 2.0 * math.pi
        steps = max(2, int(math.ceil(abs(math.degrees(sweep)) / ARC_STEP_DEG)))
        for s in range(steps + 1):
            a = a0 + sweep * s / steps
            out.append((centre[0] + math.cos(a) * radius,
                        centre[1] + math.sin(a) * radius))
            vals.append(joint if s < steps else value(i))
    pts, cns = dedupe_shape(out, [(CORNER_SHARP, 0.0, 0.0, v) for v in vals])
    return pts, [c[3] for c in cns]


def built_outline(obj):
    """The outline the slab is actually built on, finishes applied."""
    return expand_outline(outline_of(obj), corners_of(obj))


# ---------------------------------------------------------------------------
# Shape edits
#
# Each takes an outline and its corner finishes and returns new ones,
# leaving the inputs alone, so an interactive drag can recompute from the
# shape it started with on every mouse move rather than compounding.
# ---------------------------------------------------------------------------

SHARP = (CORNER_SHARP, 0.0, 0.0)


def set_edge_value(corners, index, value):
    """Set the edge data on the edge leaving corner ``index``."""
    cns = list(corners)
    i = index % len(cns)
    cns[i] = tuple(cns[i][:3]) + (float(value),)
    return cns


def edge_normal(points, index):
    """Outward unit normal of edge ``index`` (index -> index + 1)."""
    a = points[index % len(points)]
    b = points[(index + 1) % len(points)]
    u, length = _unit(b[0] - a[0], b[1] - a[1])
    if u is None:
        return None
    n = (u[1], -u[0])
    return n if signed_area(points) > 0.0 else (-n[0], -n[1])


def _cross(d0, d1):
    return d0[0] * d1[1] - d0[1] * d1[0]


def _line_hit(a0, da, b0, db):
    """Where two 2D lines cross, or None when they run parallel."""
    ua, _ = _unit(*da)
    ub, _ = _unit(*db)
    if ua is None or ub is None or abs(_cross(ua, ub)) < 1e-6:
        return None
    cross = _cross(da, db)
    dx, dy = b0[0] - a0[0], b0[1] - a0[1]
    t = (dx * db[1] - dy * db[0]) / cross
    return (a0[0] + da[0] * t, a0[1] + da[1] * t)


def slide_edge(points, corners, index, delta):
    """Push edge ``index`` out (delta > 0) or in along its normal.

    A neighbour meeting the edge at an angle keeps its line and the
    shared corner lands where the lines now cross -- a rectangle stays a
    rectangle, an angled end keeps its angle. A neighbour running
    straight on from the edge (the two halves of a split edge) has no
    crossing, so a square step is put in there instead: that is what
    turns part of a front edge into an offset, a bump-out or, pulled
    from an end, the leg of an L.

    Returns (points, corners, new index of the edge).
    """
    count = len(points)
    index %= count
    n = edge_normal(points, index)
    if n is None or abs(delta) < 1e-12:
        return list(points), list(corners), index
    nxt = (index + 1) % count
    prev = (index - 1) % count
    after = (nxt + 1) % count
    a, b = points[index], points[nxt]
    ma = (a[0] + n[0] * delta, a[1] + n[1] * delta)
    mb = (b[0] + n[0] * delta, b[1] + n[1] * delta)
    edge_dir = (b[0] - a[0], b[1] - a[1])
    prev_dir = (a[0] - points[prev][0], a[1] - points[prev][1])
    next_dir = (points[after][0] - b[0], points[after][1] - b[1])
    hit_a = _line_hit(ma, edge_dir, points[prev], prev_dir)
    hit_b = _line_hit(ma, edge_dir, points[after], next_dir)

    # What stands in for a, and for b.
    if hit_a is None:
        a_pts, a_cns = [a, ma], [corners[index], sharp_like(corners[index])]
    else:
        a_pts, a_cns = [hit_a], [corners[index]]
    if hit_b is None:
        b_pts, b_cns = [mb, b], [sharp_like(corners[index]), corners[nxt]]
    else:
        b_pts, b_cns = [hit_b], [corners[nxt]]

    new_pts, new_cns = [], []
    edge_at = None
    for i in range(count):
        if i == index:
            new_pts += a_pts
            new_cns += a_cns
            edge_at = len(new_pts) - 1
            if nxt != 0:
                new_pts += b_pts
                new_cns += b_cns
        elif i == nxt:
            if nxt == 0:
                # The closing edge: b's stand-ins lead the list so point
                # 0 stays where it was in the order.
                new_pts += b_pts
                new_cns += b_cns
        else:
            new_pts.append(points[i])
            new_cns.append(corners[i])
    return new_pts, new_cns, edge_at


def split_edge(points, corners, index, point):
    """Put a new sharp corner on edge ``index`` at the spot nearest
    ``point``. Returns (points, corners, index of the new corner), or
    the inputs and None when the spot is on top of an existing end."""
    count = len(points)
    index %= count
    a, b = points[index], points[(index + 1) % count]
    u, length = _unit(b[0] - a[0], b[1] - a[1])
    if u is None:
        return list(points), list(corners), None
    t = (point[0] - a[0]) * u[0] + (point[1] - a[1]) * u[1]
    if t <= POINT_TOL * 10 or t >= length - POINT_TOL * 10:
        return list(points), list(corners), None
    p = (a[0] + u[0] * t, a[1] + u[1] * t)
    pts = list(points[:index + 1]) + [p] + list(points[index + 1:])
    cns = (list(corners[:index + 1]) + [sharp_like(corners[index])]
           + list(corners[index + 1:]))
    return pts, cns, index + 1


def is_straight_through(points, index):
    """Does the outline run straight on through corner ``index``? True
    for a corner that only splits an edge."""
    count = len(points)
    c = points[index % count]
    p = points[(index - 1) % count]
    q = points[(index + 1) % count]
    u0, _ = _unit(c[0] - p[0], c[1] - p[1])
    u1, _ = _unit(q[0] - c[0], q[1] - c[1])
    if u0 is None or u1 is None:
        return False
    return abs(_cross(u0, u1)) < 1e-6 and (u0[0] * u1[0] + u0[1] * u1[1]) > 0.0


def move_corner(points, corners, index, point):
    """Move one corner, angling the two edges that meet there."""
    pts = list(points)
    pts[index % len(pts)] = (float(point[0]), float(point[1]))
    return pts, list(corners)


def remove_corner(points, corners, index):
    """Take a corner out; its two edges join straight across. None when
    that would leave fewer than three."""
    if len(points) <= 3:
        return None
    index %= len(points)
    pts = list(points[:index]) + list(points[index + 1:])
    cns = list(corners[:index]) + list(corners[index + 1:])
    return pts, cns


def set_corner_finish(corners, index, kind, size_before, size_after=None):
    cns = list(corners)
    if size_after is None:
        size_after = size_before
    i = index % len(cns)
    cns[i] = ((kind, float(size_before), float(size_after))
              if kind != CORNER_SHARP else SHARP) + _extras(cns[i])
    return cns


def finish_point(points, corners, index):
    """Where to draw the grip for a corner's finish: the middle of its
    clip line or arc. None for a sharp corner."""
    count = len(points)
    kind = corners[index][0]
    if kind == CORNER_SHARP:
        return None
    reach = corner_tangents(points, corners)[index]
    c = points[index]
    u0, _ = _unit(points[index - 1][0] - c[0], points[index - 1][1] - c[1])
    u1, _ = _unit(points[(index + 1) % count][0] - c[0],
                  points[(index + 1) % count][1] - c[1])
    if u0 is None or u1 is None:
        return None
    p0 = (c[0] + u0[0] * reach[0], c[1] + u0[1] * reach[0])
    p1 = (c[0] + u1[0] * reach[1], c[1] + u1[1] * reach[1])
    mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
    if kind == CORNER_RADIUS:
        bis, _ = _unit(u0[0] + u1[0], u0[1] + u1[1])
        cos_t = max(-1.0, min(1.0, u0[0] * u1[0] + u0[1] * u1[1]))
        theta = math.acos(cos_t)
        if bis is not None and theta > 1e-3:
            radius = reach[0] * math.tan(theta / 2.0)
            dist = radius / math.sin(theta / 2.0)
            return (c[0] + bis[0] * (dist - radius),
                    c[1] + bis[1] * (dist - radius))
    return mid


def has_outline(obj):
    return len(outline_of(obj)) >= 3


def ensure_outline(obj):
    """Give a top an outline if it has none. True when one is there.

    Tops built before the outline existed are boxes, and a box is fully
    described by the mesh it already carries: its footprint is the
    rectangle, and its Z range the underside and the thickness. Seeding
    from that means an old job can be reshaped without being rebuilt,
    and the seeded shape is exactly the slab that was already there.
    """
    if has_outline(obj):
        return True
    mesh = getattr(obj, 'data', None)
    if mesh is None or len(mesh.vertices) < 8:
        return False
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    thickness = max(zs) - min(zs)
    if thickness <= 0.0:
        return False
    obj[TOP_KEY] = float(min(zs))
    obj[THICKNESS_KEY] = float(thickness)
    set_outline(obj, ((min(xs), min(ys)), (max(xs), min(ys)),
                      (max(xs), max(ys)), (min(xs), max(ys))))
    return True


def rebuild(obj):
    """Rewrite the slab's mesh from its stored outline. True if built.

    Writes into the existing mesh datablock, so the material the top is
    already wearing survives being reshaped.
    """
    points = built_outline(obj)
    if len(points) < 3:
        return False
    top = float(obj.get(TOP_KEY, 0.0))
    thickness = float(obj.get(THICKNESS_KEY, 0.0))
    if thickness <= 0.0:
        return False

    bm = bmesh.new()
    lower = [bm.verts.new((x, y, top)) for x, y in points]
    upper = [bm.verts.new((x, y, top + thickness)) for x, y in points]
    bm.faces.new(list(reversed(lower)))
    bm.faces.new(upper)
    count = len(points)
    for i in range(count):
        j = (i + 1) % count
        bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    cut_for_sinks(obj)
    apply_world_uvs(obj)
    return True


def cut_for_sinks(obj):
    """The sinks under a top cut their openings through it."""
    try:
        from . import appliance_geo
    except Exception:
        return 0
    return appliance_geo.cut_sink_openings(obj, world_matrix(obj))


def world_matrix(obj):
    """obj.matrix_world, computed rather than read.

    The cached value is stale for an object parented moments ago, and
    every top here is exactly that.
    """
    if obj.parent is None:
        return obj.matrix_basis.copy()
    return obj.parent.matrix_world @ obj.matrix_parent_inverse @ obj.matrix_basis


def apply_world_uvs(obj):
    """Box-project the mesh in world space, 1 UV unit = 1 metre.

    World rather than object space so neighbouring tops share one
    continuous run of stone or tile instead of each restarting the
    pattern at its own corner. Each face takes the plane its normal
    points along, which keeps the top's projection from smearing down
    the edge band.
    """
    mesh = obj.data
    mw = world_matrix(obj)
    rot = mw.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        normal = rot @ face.normal
        axis = max(range(3), key=lambda i: abs(normal[i]))
        for loop in face.loops:
            co = mw @ loop.vert.co
            if axis == 2:
                loop[uv_layer].uv = (co.x, co.y)
            elif axis == 0:
                loop[uv_layer].uv = (co.y, co.z)
            else:
                loop[uv_layer].uv = (co.x, co.z)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def finish(obj, library):
    """Everything a freshly built countertop still needs: its own
    right-click menu, the library that built it (so the menu can offer
    that library's cut command), and UVs."""
    obj['MENU_ID'] = MENU_ID
    obj['HB_COUNTERTOP_LIB'] = library
    cut_for_sinks(obj)
    apply_world_uvs(obj)
    return obj


def is_under_counter(obj, cabinet_top):
    """Does this appliance belong under an island's countertop?

    Anything reaching no higher than the cabinets beside it, except a
    range, which carries its own top.
    """
    if not obj.get('IS_APPLIANCE') or obj.get('APPLIANCE_TYPE') == 'RANGE':
        return False
    try:
        cage = hb_types.GeoNodeCage(obj)
        top = obj.matrix_world.translation.z + cage.get_input('Dim Z')
    except Exception:
        return False
    return top <= cabinet_top + UNDER_COUNTER_MARGIN
