"""A stair through a wall: the wall is cut open where people walk.

Each straight flight and landing gets a hidden cutter, a child of the
stair, shaped to the space walked through: from under its treads up to
the treads plus the stair's Headroom, the flight's slope followed. A
wall on the stair's level, or the level above, that one of them passes
through gets a Boolean against it, so the wall stays under the stair (it
holds it up) and over the headroom (a header), and is open between. Only
a wall the stair crosses - right through its thickness - is cut; one it
runs along beside, even one drawn a little into its edge, is not. The
opening is a little wider than the stair, so its sides do not lie on the
stair's own.

The cutters and their Booleans are made again whenever the stair is
built - placed, changed, moved, edited - so a wall the stair leaves
closes up. The stair's Cut Walls switch turns it off. Curved and spiral
stairs, and winders, are not cut for (yet).
"""

import bmesh
import bpy
from mathutils import Vector

from . import hb_house
from .units import inch

CUTTER_KEY = 'IS_STAIR_WALL_CUTTER'
UNDER = inch(1)             # how far under the line of the treads the cut starts
SIDE_IN = 0.002             # what a wall is tested against: the walking space
                            # this much inside the stair's sides
SIDE_OUT = inch(0.25)       # the opening: this much wider each side than the stair
CROSSES = 0.9               # a wall is crossed when the walking space takes in
                            # this much of its thickness
MOD_PREFIX = "Stair Cut - "


def cuts_walls(obj):
    return bool(obj.get('STAIR_CUT_WALLS', True))


def cutters_of(obj):
    return [c for c in obj.children if c.get(CUTTER_KEY)]


def _pieces(obj, side=SIDE_IN):
    """[(name, bmesh, span)]: the walking space over each flight and landing, in
    the stair's own frame, `side` inside the stair's sides (less than 0:
    outside them)."""
    from . import hb_stairs, hb_stair_build, hb_stair_shapes as shapes
    v = hb_stairs.values(obj)
    if shapes.is_arc(v) or shapes.is_shaped(v):
        return []
    head = v['headroom']
    flights, landings = hb_stair_build.layout(v)
    out = []
    for i, f in enumerate(flights):
        x0, x1 = side, f.W - side
        y0, y1 = -0.01, f.run + 0.01
        # Under the line through the tread backs, up to the nosings plus
        # the headroom
        zb = lambda y: f.k * y - UNDER
        zt = lambda y: f.k * y + f.r + head
        pts = [(y0, zb(y0)), (y1, zb(y1)), (y1, zt(y1)), (y0, zt(y0))]
        bm = bmesh.new()
        left = [bm.verts.new(f.m @ Vector((x0, y, z))) for y, z in pts]
        right = [bm.verts.new(f.m @ Vector((x1, y, z))) for y, z in pts]
        bm.faces.new(list(reversed(left)))
        bm.faces.new(right)
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([left[k], left[j], right[j], right[k]])
        out.append((f"Flight {i + 1}", bm, _flight_span(f, head)))
    for i, (lx0, ly0, lx1, ly1, z) in enumerate(landings):
        bm = bmesh.new()
        m = bmesh.ops.create_cube(bm, size=1.0)['verts']
        sx, sy, sz = lx1 - lx0 - 2 * side, ly1 - ly0 - 2 * side, head + UNDER
        for vert in m:
            vert.co = Vector(((lx0 + lx1) / 2 + vert.co.x * sx, (ly0 + ly1) / 2 + vert.co.y * sy,
                              z - UNDER + (vert.co.z + 0.5) * sz))
        out.append((f"Landing {i + 1}", bm, lambda pts, z=z: (z - UNDER, z + head)))
    for _name, bm, _span in out:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return out


def _flight_span(f, head):
    """For a flight, the walking space's height (stair frame) over the
    stretch of its run that some plan points (stair frame) lie across."""
    inv = f.m.inverted()

    def span(pts):
        ys = [(inv @ Vector((p.x, p.y, 0.0))).y for p in pts]
        y0, y1 = max(min(ys), 0.0), min(max(ys), f.run)
        if y1 < y0:
            y0 = y1 = min(max(min(ys), 0.0), f.run)
        z0 = (f.m @ Vector((0.0, y0, f.k * y0 - UNDER))).z
        z1 = (f.m @ Vector((0.0, y1, f.k * y1 + f.r + head))).z
        return z0, z1
    return span


def _height_at(obj, span, wpoly):
    """The walking space's z range (world) where a wall stands."""
    M = obj.matrix_basis if obj.parent is None else obj.matrix_world
    Mi = M.inverted()
    pts = [(Mi @ Vector((p.x, p.y, M.translation.z))).to_2d() for p in wpoly]
    z0, z1 = span(pts)
    return z0 + M.translation.z, z1 + M.translation.z


def _footprint(obj, bm):
    """A piece's plan outline in the world, as a convex polygon, and its z
    range."""
    M = obj.matrix_basis if obj.parent is None else obj.matrix_world
    pts = [M @ v.co for v in bm.verts]
    return _hull([p.to_2d() for p in pts]), min(p.z for p in pts), max(p.z for p in pts)


def _hull(points):
    pts = sorted(set((round(p.x, 6), round(p.y, 6)) for p in points))
    if len(pts) <= 2:
        return [Vector(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [Vector(p) for p in lower[:-1] + upper[:-1]]


def _overlap(a, b):
    """How deep two convex polygons overlap (separating axes), 0 if apart."""
    depth = None
    for poly in (a, b):
        for i in range(len(poly)):
            e = poly[(i + 1) % len(poly)] - poly[i]
            if e.length < 1e-9:
                continue
            n = Vector((-e.y, e.x)).normalized()
            pa = [n.dot(p) for p in a]
            pb = [n.dot(p) for p in b]
            d = min(max(pa), max(pb)) - max(min(pa), min(pb))
            if d <= 0:
                return 0.0
            depth = d if depth is None else min(depth, d)
    return depth or 0.0


def _wall_box(wall):
    """A wall's plan outline, z range and thickness."""
    from . import hb_types
    w = hb_types.GeoNodeWall(wall)
    try:
        L, t, h = w.get_input('Length'), w.get_input('Thickness'), w.get_input('Height')
    except Exception:
        return None
    M = wall.matrix_world
    poly = [(M @ Vector((x, y, 0.0))).to_2d() for x, y in ((0, 0), (L, 0), (L, t), (0, t))]
    z = M.translation.z
    return poly, z, z + h, t


def _walls_near(obj):
    scene = obj.users_scene[0] if obj.users_scene else bpy.context.scene
    level = hb_house.get_level(obj.get(hb_house.LEVEL_KEY, '')) if obj.get(hb_house.LEVEL_KEY) else None
    uids = set()
    if level is not None:
        uids.add(level.uid)
        above = hb_house.level_above(scene.hb_house, level)
        if above is not None:
            uids.add(above.uid)
    return [w for w in scene.objects if w.get('IS_WALL_BP')
            and (not uids or w.get(hb_house.LEVEL_KEY, '') in uids)]


def clear(obj):
    """Take a stair's cutters away, and the cuts they made."""
    from . import cutters
    for c in cutters_of(obj):
        cutters.remove(c)


def cut(obj):
    """Make the stair's cutters, and cut the walls they pass through."""
    from . import cutters
    old = {c.name: c for c in cutters_of(obj)}
    if not cuts_walls(obj):
        clear(obj)
        return []
    tests = {name: (bm, span) for name, bm, span in _pieces(obj)}
    pieces = _pieces(obj, -SIDE_OUT)
    kept, cut_walls = [], []
    for name, bm, _span in pieces:
        test = tests.get(name)
        poly, z0, z1 = _footprint(obj, test[0]) if test is not None else ([], 0.0, 0.0)
        full = f"{obj.name} {name} Cut"
        cutter = next((c for c in old.values() if c.get('HB_PIECE') == name), None)
        mesh = bpy.data.meshes.new(full)
        bm.to_mesh(mesh)
        bm.free()
        if cutter is None:
            cutter = bpy.data.objects.new(full, mesh)
            for col in obj.users_collection or [bpy.context.scene.collection]:
                col.objects.link(cutter)
            cutter.parent = obj
            cutter.matrix_parent_inverse.identity()
            cutter[CUTTER_KEY] = True
            cutter['IS_CUTTING_OBJ'] = True
            cutter['HB_PIECE'] = name
            if obj.get(hb_house.LEVEL_KEY):
                cutter[hb_house.LEVEL_KEY] = obj[hb_house.LEVEL_KEY]
            cutter.display_type = 'WIRE'
            cutter.hide_render = True
            cutter.hide_viewport = True
        else:
            prev = cutter.data
            cutter.data = mesh
            if prev is not None and prev.users == 0:
                bpy.data.meshes.remove(prev)
        kept.append(cutter)
        crossed = set()
        for wall in _walls_near(obj) if poly else []:
            box = _wall_box(wall)
            if box is None:
                continue
            wpoly, wz0, wz1, t = box
            # Through its thickness, not along its face
            if wz1 <= z0 or wz0 >= z1 or _overlap(poly, wpoly) < t * CROSSES:
                continue
            # Over the stretch of the stair the wall stands across
            hz0, hz1 = _height_at(obj, test[1], wpoly)
            if wz1 <= hz0 or wz0 >= hz1:
                continue
            crossed.add(wall.name)
            if not any(m.type == 'BOOLEAN' and m.object == cutter for m in wall.modifiers):
                mod = wall.modifiers.new(name=MOD_PREFIX + cutter.name, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.object = cutter
                mod.solver = 'EXACT'
            cut_walls.append(wall)
        # Walls this piece no longer passes through close up again
        for host, mod in cutters.hosts_of(cutter):
            if host.name not in crossed:
                host.modifiers.remove(mod)
    for c in old.values():
        if c not in kept:
            cutters.remove(c)
    for bm, _span in tests.values():
        bm.free()
    return cut_walls
