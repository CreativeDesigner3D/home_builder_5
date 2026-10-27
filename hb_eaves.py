"""Eave trim and gutters: fascia, boxed soffits and rake boards round the
roofs, gutters along the eaves and downspouts to the ground.

Turned on in HOUSE > Roof > Eaves & Gutters; off in old files. Rebuilt
with the roofs, so it follows every roof edit.

The edges come from the roofs as built, not from their recipes, so one
rule serves gables, hips, gambrels, cross gables, dormers and porch roofs
and every cut between them. A roof is a slab; the outline of its top
surface is where trim can go. A level stretch of that outline is an eave,
a sloped one a rake. A stretch is trimmed only where it is free: just
outside it there is no roof a little below or above (where a cross gable
sits on the main roof, or a roof runs into another) and no wall overhead
(where an upper level rises through the roof).

Each level's trim is one object and its gutters another, in the level's
collection, tagged IS_EAVE_TRIM; Show Roofs hides them with the roofs.
"""

import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import hb_house
from .units import inch

TRIM_KEY = 'IS_EAVE_TRIM'
GUTTER_MATERIAL = "HB Gutter"
GUTTER_COLOR = (0.93, 0.93, 0.91, 1.0)

TOP_NZ = 0.15               # a face this upturned is part of a roof's top
LEVEL_DZ = 0.01             # an edge rising less than this per metre is level
PROBE_OUT = 0.05            # how far outside an edge it is probed
PROBE_STEP = 0.25           # along it
MIN_RUN = 0.15              # shorter kept stretches are dropped
ROOF_BELOW = 0.30           # a roof this close under the probe: not free
ROOF_ABOVE = 1.0            # or this close over it
WALL_ABOVE = 3.0            # a wall this close over it: an upper level
SOFFIT_T = inch(0.5)
SOFFIT_REACH = 1.5          # how far in a soffit looks for its wall
GUTTER_GAP = inch(0.5)      # its top under the roof's edge
DOWNSPOUT = (inch(3.0), inch(2.0))
DOWNSPOUT_MAX = 12.0        # most gutter between downspouts
STOP_ABOVE_ROOF = 0.10


# ---- What the roofs' edges are -------------------------------------------------

class Run:
    """A stretch of a roof's top edge to trim: from a to b (world), the
    roof's top on its left, `out` the horizontal outward direction."""
    __slots__ = ('kind', 'a', 'b', 'out', 'level', 'dormer')

    def __init__(self, kind, a, b, out, level, dormer):
        self.kind, self.a, self.b, self.out = kind, a, b, out
        self.level, self.dormer = level, dormer

    @property
    def length(self):
        return (self.b - self.a).length


def _roof_objects(scene):
    """(object, level uid, is a dormer roof) for every roof built."""
    out = []
    for level in scene.hb_house.levels:
        for obj, dormer in ((level.roof.roof_obj, False), (level.roof.dormer_obj, True)):
            if obj is not None and obj.type == 'MESH' and obj.name in scene.objects:
                out.append((obj, level.uid, dormer))
        for room in level.rooms:
            obj = room.porch_roof_obj
            if obj is not None and obj.type == 'MESH' and obj.name in scene.objects:
                out.append((obj, level.uid, False))
    return out


def _world_mesh(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    m = obj.matrix_world
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(m)
    ev.to_mesh_clear()
    bm.normal_update()
    return bm


def _trees(scene, depsgraph, roofs):
    verts, polys = [], []
    for obj, _uid, _d in roofs:
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        m = obj.matrix_world
        base = len(verts)
        verts.extend(m @ v.co for v in mesh.vertices)
        polys.extend([base + i for i in p.vertices] for p in mesh.polygons)
        ev.to_mesh_clear()
    roof_tree = BVHTree.FromPolygons(verts, polys) if polys else None
    verts, polys = [], []
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP') or obj.type != 'MESH':
            continue
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        m = obj.matrix_world
        base = len(verts)
        verts.extend(m @ v.co for v in mesh.vertices)
        polys.extend([base + i for i in p.vertices] for p in mesh.polygons)
        ev.to_mesh_clear()
    wall_tree = BVHTree.FromPolygons(verts, polys) if polys else None
    return roof_tree, wall_tree


def _free(p, roof_tree, wall_tree):
    """Whether a point just outside a roof's edge is open air."""
    down, up = Vector((0.0, 0.0, -1.0)), Vector((0.0, 0.0, 1.0))
    if roof_tree is not None:
        if roof_tree.ray_cast(p + up * 0.02, down, ROOF_BELOW)[0] is not None:
            return False
        if roof_tree.ray_cast(p - up * 0.02, up, ROOF_ABOVE)[0] is not None:
            return False
    if wall_tree is not None and wall_tree.ray_cast(p, up, WALL_ABOVE)[0] is not None:
        return False
    return True


def _top_outline(bm):
    """The top surface's outline edges: (a, b, outward) with the top on the
    edge's left looking from a to b."""
    top = {f for f in bm.faces if f.normal.z > TOP_NZ}
    out = []
    for e in bm.edges:
        tops = [f for f in e.link_faces if f in top]
        if len(tops) != 1:
            continue
        f = tops[0]
        a, b = e.verts[0].co.copy(), e.verts[1].co.copy()
        # Wind it so the face is on the left
        for loop in f.loops:
            if loop.edge == e:
                a, b = loop.vert.co.copy(), loop.link_loop_next.vert.co.copy()
                break
        d = (b - a)
        flat = Vector((d.x, d.y, 0.0))
        if flat.length < 1e-6:
            continue                    # a plumb edge: no trim along it
        outward = Vector((flat.y, -flat.x, 0.0)).normalized()
        out.append((a, b, outward))
    return out


def _merge(edges):
    """Join edges that carry on in a straight line into one."""
    edges = list(edges)
    merged = True
    while merged:
        merged = False
        for i in range(len(edges)):
            for j in range(len(edges)):
                if i == j:
                    continue
                a0, b0, o0 = edges[i]
                a1, b1, o1 = edges[j]
                if (b0 - a1).length < 1e-4 and (b0 - a0).normalized().dot((b1 - a1).normalized()) > 0.9999:
                    edges[i] = (a0, b1, o0)
                    del edges[j]
                    merged = True
                    break
            if merged:
                break
    return edges


def roof_runs(scene, depsgraph=None):
    """Every free stretch of every roof's top edge: [Run]."""
    depsgraph = depsgraph or bpy.context.evaluated_depsgraph_get()
    roofs = _roof_objects(scene)
    roof_tree, wall_tree = _trees(scene, depsgraph, roofs)
    runs = []
    for obj, uid, dormer in roofs:
        bm = _world_mesh(obj, depsgraph)
        edges = _merge(_top_outline(bm))
        bm.free()
        for a, b, outward in edges:
            d = b - a
            length = d.length
            if length < MIN_RUN:
                continue
            slope = abs(d.z) / max(Vector((d.x, d.y)).length, 1e-9)
            kind = 'EAVE' if slope < LEVEL_DZ else 'RAKE'
            n = max(2, int(length / PROBE_STEP) + 1)
            keep = []
            for k in range(n + 1):
                t = k / n
                keep.append(_free(a + d * t + outward * PROBE_OUT, roof_tree, wall_tree))
            # Kept stretches between probes
            start = None
            for k in range(n + 1):
                if keep[k] and start is None:
                    start = k
                if (not keep[k] or k == n) and start is not None:
                    end = k if keep[k] else k - 1
                    t0, t1 = start / n, end / n
                    if (t1 - t0) * length >= MIN_RUN:
                        runs.append(Run(kind, a + d * t0, a + d * t1, outward, uid, dormer))
                    start = None
    return runs


# ---- Parts ------------------------------------------------------------------------

def _quad_box(bm, corners):
    """A box from its 8 corners: bottom four then top four, each ring
    going round the same way."""
    v = [bm.verts.new(c) for c in corners]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])


def _fascia(bm, run, height, thick):
    a, b, o = run.a, run.b, run.out * thick
    down = Vector((0.0, 0.0, -height))
    _quad_box(bm, [a + down, b + down, b + down + o, a + down + o, a, b, b + o, a + o])


def _soffit(bm, run, height, wall_tree):
    """A level board under the overhang, from the fascia back to the wall."""
    z = -height
    reach = None
    if wall_tree is not None:
        for t in (0.25, 0.5, 0.75):
            p = run.a.lerp(run.b, t) + Vector((0.0, 0.0, z - SOFFIT_T * 0.5))
            hit = wall_tree.ray_cast(p, -run.out, SOFFIT_REACH)
            if hit[0] is not None:
                reach = hit[3] if reach is None else min(reach, hit[3])
    if reach is None or reach < 0.05:
        return
    a = run.a + Vector((0.0, 0.0, z))
    b = run.b + Vector((0.0, 0.0, z))
    i = -run.out * reach
    t = Vector((0.0, 0.0, -SOFFIT_T))
    _quad_box(bm, [a + i + t, b + i + t, b + t, a + t, a + i, b + i, b, a])


def _rake(bm, run, width, thick):
    """A board on the gable end along a rake: its top on the roof's edge,
    `width` down square to the slope, `thick` out from the end."""
    d = (run.b - run.a).normalized()
    down = d.cross(run.out)
    if down.z > 0:
        down = -down
    down = down.normalized() * width
    a, b, o = run.a, run.b, run.out * thick
    _quad_box(bm, [a + down, b + down, b + down + o, a + down + o, a, b, b + o, a + o])


def _profile(style, size):
    """A gutter's cross-section as (out, z) points round its shell, from
    its back top, open at the top: K-style or half round."""
    w = inch(size)
    d = w * 0.85
    t = inch(0.04) * 2.0
    if style == 'HALF_ROUND':
        pts = [(w / 2.0 - math.cos(math.pi * k / 10) * w / 2.0,
                -math.sin(math.pi * k / 10) * w / 2.0) for k in range(11)]
    else:
        pts = [(0.0, 0.0), (0.0, -d), (w * 0.70, -d), (w * 0.82, -d * 0.82),
               (w * 0.80, -d * 0.55), (w * 0.95, -d * 0.40), (w, -d * 0.12), (w * 0.94, 0.0)]
    inner = [(x + (t if 0 < i < len(pts) - 1 else 0.0) * (1 if x < w / 2 else -1),
              z + (t if z < -1e-6 else 0.0)) for i, (x, z) in enumerate(pts)]
    return pts + list(reversed(inner))


def _sweep(bm, run, offset_out, z_top, ring, caps=True):
    """Sweep a closed (out, z) ring along a run."""
    rings = []
    for p in (run.a, run.b):
        base = p + run.out * offset_out
        rings.append([bm.verts.new(base + run.out * x + Vector((0.0, 0.0, z_top - p.z + z)))
                      for x, z in ring])
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    if caps:
        for r in rings:
            try:
                bm.faces.new(r)
            except ValueError:
                pass


def _downspouts(bm, run, offset_out, z_gutter, roof_tree, wall_tree, ground_z):
    """Downspouts from a gutter run: one in from each end, and one more
    every DOWNSPOUT_MAX, each back to the wall then down."""
    length = run.length
    count = max(1, math.ceil(length / DOWNSPOUT_MAX))
    ts = [min(0.15 / length, 0.5)] if count == 1 else [
        0.15 / length + (1 - 0.3 / length) * k / (count - 1) for k in range(count)]
    w, dpt = DOWNSPOUT
    along = (run.b - run.a).normalized()
    for t in ts:
        top = run.a.lerp(run.b, t) + run.out * (offset_out + inch(2.5))
        top.z = z_gutter
        reach = 0.3
        if wall_tree is not None:
            hit = wall_tree.ray_cast(top - Vector((0.0, 0.0, 0.3)), -run.out, SOFFIT_REACH + 0.5)
            if hit[0] is not None:
                reach = hit[3] - dpt / 2.0 - inch(1.0)
        bottom = ground_z
        foot = top - run.out * reach
        if roof_tree is not None:
            hit = roof_tree.ray_cast(foot - Vector((0.0, 0.0, 0.4)), Vector((0.0, 0.0, -1.0)), 30.0)
            if hit[0] is not None and hit[0].z > ground_z:
                bottom = hit[0].z + STOP_ABOVE_ROOF
        # Back from the gutter to the wall, just under it
        ax, ao = along * (w / 2.0), run.out * (dpt / 2.0)
        z0, z1 = z_gutter - 0.30, z_gutter - 0.30 + dpt
        p0, p1 = top, foot
        _quad_box(bm, [p0 - ax + Vector((0, 0, z0 - p0.z)), p0 + ax + Vector((0, 0, z0 - p0.z)),
                       p1 + ax + Vector((0, 0, z0 - p1.z)), p1 - ax + Vector((0, 0, z0 - p1.z)),
                       p0 - ax + Vector((0, 0, z1 - p0.z)), p0 + ax + Vector((0, 0, z1 - p0.z)),
                       p1 + ax + Vector((0, 0, z1 - p1.z)), p1 - ax + Vector((0, 0, z1 - p1.z))])
        # From the gutter down to that run
        _quad_box(bm, [top - ax - ao + Vector((0, 0, z0 - top.z)), top + ax - ao + Vector((0, 0, z0 - top.z)),
                       top + ax + ao + Vector((0, 0, z0 - top.z)), top - ax + ao + Vector((0, 0, z0 - top.z)),
                       top - ax - ao, top + ax - ao, top + ax + ao, top - ax + ao])
        # Down the wall
        if z0 - bottom > 0.05:
            f = foot
            _quad_box(bm, [f - ax - ao + Vector((0, 0, bottom - f.z)), f + ax - ao + Vector((0, 0, bottom - f.z)),
                           f + ax + ao + Vector((0, 0, bottom - f.z)), f - ax + ao + Vector((0, 0, bottom - f.z)),
                           f - ax - ao + Vector((0, 0, z0 - f.z)), f + ax - ao + Vector((0, 0, z0 - f.z)),
                           f + ax + ao + Vector((0, 0, z0 - f.z)), f - ax + ao + Vector((0, 0, z0 - f.z))])


def _gutter_material():
    mat = bpy.data.materials.get(GUTTER_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(GUTTER_MATERIAL)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = GUTTER_COLOR
            bsdf.inputs['Roughness'].default_value = 0.35
            bsdf.inputs['Metallic'].default_value = 0.4
        mat.diffuse_color = GUTTER_COLOR
    return mat


# ---- Rebuild ----------------------------------------------------------------------

_held = 0


class held:
    """While inside, roof rebuilds leave the trim alone; one refresh after."""

    def __enter__(self):
        global _held
        _held += 1

    def __exit__(self, *exc):
        global _held
        _held -= 1


def trim_objects(scene):
    return [o for o in scene.objects if o.get(TRIM_KEY)]


def _clear(scene):
    for obj in trim_objects(scene):
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def refresh(scene):
    """Rebuild every level's eave trim and gutters (or remove them)."""
    if _held:
        return
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    _clear(scene)
    house = scene.hb_house
    if not house.eave_trim:
        return
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    roofs = _roof_objects(scene)
    if not roofs:
        return
    roof_tree, wall_tree = _trees(scene, depsgraph, roofs)
    runs = roof_runs(scene, depsgraph)
    from . import hb_exterior
    trim_mat = hb_exterior.trim_material()
    gutter_mat = _gutter_material()
    ground = hb_house.ground_level(house)
    ground_z = (ground.elevation if ground is not None else 0.0) - hb_exterior.BASE_BELOW
    by_level = {}
    for run in runs:
        by_level.setdefault(run.level, []).append(run)
    ring = _profile(house.gutter_style, float(house.gutter_size))
    for uid, level_runs in by_level.items():
        level = hb_house.get_level(uid)
        if level is None:
            continue
        hb_house.ensure_level_collections(scene, level)
        trim = bmesh.new()
        gut = bmesh.new()
        for run in level_runs:
            if run.kind == 'EAVE':
                _fascia(trim, run, house.fascia_height, house.fascia_thickness)
                if house.soffit_style == 'BOXED':
                    _soffit(trim, run, house.fascia_height, wall_tree)
                if house.gutters and (house.gutters_on_dormers or not run.dormer):
                    z_top = run.a.z - GUTTER_GAP
                    _sweep(gut, run, house.fascia_thickness, z_top, ring)
                    if house.downspouts:
                        z_bot = z_top - inch(float(house.gutter_size)) * 0.85
                        _downspouts(gut, run, house.fascia_thickness, z_bot, roof_tree, wall_tree, ground_z)
            elif house.rake_boards:
                _rake(trim, run, house.fascia_height, house.fascia_thickness)
        for bm, name, mat in ((trim, "Eave Trim", trim_mat), (gut, "Gutters", gutter_mat)):
            if not bm.faces:
                bm.free()
                continue
            bm.normal_update()
            mesh = bpy.data.meshes.new(f"{name} - {level.name}")
            bm.to_mesh(mesh)
            bm.free()
            mesh.materials.append(mat)
            obj = bpy.data.objects.new(f"{name} - {level.name}", mesh)
            level.collection.objects.link(obj)
            obj[TRIM_KEY] = True
            obj[hb_house.LEVEL_KEY] = uid
            obj.hide_viewport = not house.show_roofs
    apply_visibility(scene)


def apply_visibility(scene):
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    hide = not scene.hb_house.show_roofs
    for obj in trim_objects(scene):
        obj.hide_viewport = hide
        # And renders as its level's roof does
        level = hb_house.get_level(obj.get(hb_house.LEVEL_KEY, ''))
        roof = level.roof.roof_obj if level is not None else None
        obj.hide_render = roof.hide_render if roof is not None else False


def _settings_changed(self, context):
    refresh(self.id_data)
