"""The house's foundation: a slab, a crawlspace, or a basement.

Chosen on the Structure page (Foundation) and rebuilt from the ground
level's outline whenever its walls change.

* Slab: a concrete slab under the ground level's floor, its edge
  thickened down into a footing round the outline. No level of its own.
* Crawlspace and Basement: a Foundation level under the ground level.
  Its outside walls are generated round the ground level's outline - one
  concrete wall per edge, outside faces under the walls above, thickness
  inward - on a footing band. They are tagged, and replaced on every
  rebuild; walls drawn on the level by hand are kept, so a basement gets
  rooms, stairs and doors like any level. A crawlspace finds no rooms.
  The ground level's floor is framed over either (see hb_framing).

Generated parts follow the room floors' rule: tagged, rebuilt, never
edited; the choices live on the house (scene.hb_house).
"""

import bmesh
import bpy

from . import hb_house, hb_structure_geom as geom
from .units import inch

AUTO_KEY = 'HB_FOUNDATION_AUTO'         # a generated foundation wall
PART_KEY = 'HB_FOUNDATION_PART'         # the footing or slab mesh
WALL_TYPE = 'Foundation'
LEVEL_NAME = "Foundation"
PART = 'Structure'
MATERIAL = "HB Concrete"
CONCRETE = (0.62, 0.62, 0.60, 1.0)

MAX_JOIST_SPAN = inch(14 * 12)          # 2x10s at 16": wider gets a girder
GIRDER = (inch(4.5), inch(9.25), 3)     # (3) 2x10: width, depth, plies
PIER = inch(12)                         # a concrete pier, square
PIER_SPACING = inch(72)                 # at most, along a girder
SILL = inch(1.5)                        # the sill plate on the stem wall
SUBFLOOR = inch(0.75)
GROUND_JOIST = inch(9.25)               # 2x10s over a crawlspace or basement


def floor_zone():
    """From the top of a foundation wall to the ground level's floor: the
    sill, the joists and the subfloor."""
    return SILL + GROUND_JOIST + SUBFLOOR


def concrete_material():
    mat = bpy.data.materials.get(MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(MATERIAL)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = CONCRETE
            bsdf.inputs['Roughness'].default_value = 0.9
        mat.diffuse_color = CONCRETE
    return mat


def has_level(house):
    return house.foundation_type in ('CRAWL', 'BASEMENT')


def wall_height(house):
    return house.basement_height if house.foundation_type == 'BASEMENT' else house.crawl_height


# ---- Parts --------------------------------------------------------------------

def _collection(scene, level):
    hb_house.ensure_level_collections(scene, level)
    col = hb_house.level_subcollection(level, PART)
    if col is None:
        col = bpy.data.collections.new(f"{level.name} - {PART}")
        col['HB_LEVEL_PART'] = PART
        level.collection.children.link(col)
    return col


def parts(scene):
    return [o for o in scene.objects if o.get(PART_KEY)]


def auto_walls(scene, level=None):
    """The generated walls (on a level)."""
    return [o for o in auto_objects(scene, level) if o.get('IS_WALL_BP')]


def auto_objects(scene, level=None):
    """Everything generated on the foundation level: walls, girders, piers."""
    return [o for o in scene.objects if o.get(AUTO_KEY)
            and (level is None or o.get(hb_house.LEVEL_KEY) == level.uid)]


def _remove(obj):
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and data.users == 0 and isinstance(data, bpy.types.Mesh):
        bpy.data.meshes.remove(data)


def _remove_wall(obj):
    for child in list(obj.children_recursive):
        _remove(child)
    _remove(obj)


def _band_mesh(name, outer, inner, z0, z1):
    """A closed band between two rings of plan points (the same count,
    corresponding), from z0 to z1."""
    bm = bmesh.new()
    n = len(outer)
    ob = [bm.verts.new((p[0], p[1], z0)) for p in outer]
    ot = [bm.verts.new((p[0], p[1], z1)) for p in outer]
    ib = [bm.verts.new((p[0], p[1], z0)) for p in inner]
    it = [bm.verts.new((p[0], p[1], z1)) for p in inner]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ot[i], ot[j], it[j], it[i]))      # top
        bm.faces.new((ob[j], ob[i], ib[i], ib[j]))      # bottom
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))      # outside
        bm.faces.new((ib[j], ib[i], it[i], it[j]))      # inside
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _slab_mesh(name, outline, z0, z1, edge_ring=None, edge_z0=None):
    """A slab over an outline from z0 to z1; with `edge_ring` (an inner
    ring of the same count) its edge band reaches down to edge_z0."""
    bm = bmesh.new()
    top = [bm.verts.new((p[0], p[1], z1)) for p in outline]
    bm.faces.new(top)
    if edge_ring is None:
        bottom = [bm.verts.new((p[0], p[1], z0)) for p in outline]
        bm.faces.new(list(reversed(bottom)))
        for i in range(len(outline)):
            j = (i + 1) % len(outline)
            bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    else:
        n = len(outline)
        ob = [bm.verts.new((p[0], p[1], edge_z0)) for p in outline]
        ib = [bm.verts.new((p[0], p[1], edge_z0)) for p in edge_ring]
        iz = [bm.verts.new((p[0], p[1], z0)) for p in edge_ring]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ob[i], ob[j], top[j], top[i]))     # outside face
            bm.faces.new((ob[j], ob[i], ib[i], ib[j]))       # footing bottom
            bm.faces.new((ib[j], ib[i], iz[i], iz[j]))       # inside of the edge
        bm.faces.new(list(reversed(iz)))                     # slab underside
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _add_part(scene, level, name, mesh):
    obj = bpy.data.objects.new(name, mesh)
    _collection(scene, level).objects.link(obj)
    obj[PART_KEY] = True
    obj[hb_house.LEVEL_KEY] = level.uid
    mesh.materials.append(concrete_material())
    return obj


# ---- The level ----------------------------------------------------------------

def foundation_level(house):
    return next((l for l in house.levels if l.kind == 'FOUNDATION'), None)


def _ensure_level(scene, ground_vals):
    """The Foundation level, made under the ground level if missing, at the
    height the foundation's walls call for. Returns its uid.

    Reads the ground level's values first (ground_vals) and looks the new
    level up again by uid: nothing is held across the add()."""
    house = scene.hb_house
    g_elev = ground_vals
    h = wall_height(house)
    elevation = g_elev - floor_zone() - h
    level = foundation_level(house)
    if level is None:
        level = house.levels.add()
        uid = hb_house._new_uid()
        level.uid = uid
        level['name'] = LEVEL_NAME
        level['kind'] = 1                       # 'FOUNDATION'
        level['elevation'] = elevation
        level['applied_elevation'] = elevation
        level = hb_house.get_level(uid)
        hb_house.ensure_level_collections(scene, level)
    elif abs(level.elevation - elevation) > 1e-6:
        level.elevation = elevation             # moves what is on it
    level['ceiling_height'] = h
    level['floor_thickness'] = house.slab_thickness
    level['floor_to_floor'] = g_elev - elevation
    level['applied_floor_to_floor'] = g_elev - elevation
    return level.uid


def _remove_level(scene, uid):
    """Take the Foundation level away, unless walls drawn by hand are on
    it; then only its generated walls go. True if it went."""
    house = scene.hb_house
    hand = [o for o in scene.objects if o.get('IS_WALL_BP')
            and o.get(hb_house.LEVEL_KEY) == uid and not o.get(AUTO_KEY)]
    for obj in auto_objects(scene, hb_house.get_level(uid)):
        _remove_wall(obj)
    if hand:
        return False
    index = next(i for i, l in enumerate(house.levels) if l.uid == uid)
    level = house.levels[index]
    col = level.collection
    doomed = {o.name for o in scene.objects if o.get(hb_house.LEVEL_KEY) == uid}
    if col is not None:
        doomed |= {o.name for o in col.all_objects}
    for name in doomed:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            _remove(obj)
    if col is not None:
        for sub in list(col.children):
            bpy.data.collections.remove(sub)
        bpy.data.collections.remove(col)
    active = house.active_level_index
    house.levels.remove(index)
    house.active_level_index = max(0, min(active - (1 if active > index else 0),
                                          len(house.levels) - 1))
    return True


# ---- Rebuild --------------------------------------------------------------------

_building = False


def rebuild(scene):
    """Make the foundation the house's settings describe, round the ground
    level's outline as it is now."""
    global _building
    if _building:
        return
    scene = hb_house.house_scene_of(scene) or scene
    house = scene.hb_house
    ground = hb_house.ground_level(house)
    if ground is None:
        return
    _building = True
    try:
        _rebuild(scene, house, ground.uid)
    finally:
        _building = False


def _rebuild(scene, house, ground_uid):
    from .operators import walls
    for obj in parts(scene):
        _remove(obj)
    kind = house.foundation_type
    fl = foundation_level(house)
    if not has_level(house) and fl is not None:
        _remove_level(scene, fl.uid)
    ground = hb_house.get_level(ground_uid)
    if kind == 'NONE' or ground is None:
        return
    outlines = hb_house.level_outlines(scene, ground)
    # Under the outside of the sheathing, not the siding
    from . import hb_assemblies
    siding = max((hb_assemblies.siding_inset(o) for o in scene.objects
                  if o.get('IS_WALL_BP') and o.get(hb_house.LEVEL_KEY) == ground.uid), default=0.0)
    if siding > 0.0:
        outlines = [geom.offset_polygon(o, -siding) for o in outlines]
    if not outlines:
        return
    t = house.foundation_wall_thickness
    fw = max(house.footing_width, t)
    fd = house.footing_depth
    if kind == 'SLAB':
        # Under the room floors, its edge thickened into a footing
        top = ground.elevation - 0.012
        for k, poly in enumerate(outlines):
            inner = geom.offset_polygon(poly, -fw)
            mesh = _slab_mesh("Slab", poly, top - house.slab_thickness, top,
                              edge_ring=inner, edge_z0=top - house.slab_thickness - fd)
            _add_part(scene, ground, "Slab", mesh)
        return

    uid = _ensure_level(scene, ground.elevation)
    fl = hb_house.get_level(uid)
    h = wall_height(house)
    for obj in auto_objects(scene, fl):
        _remove_wall(obj)
    for poly in outlines:
        made = walls.build_wall_run(scene, poly, WALL_TYPE, level=hb_house.get_level(uid),
                                    thickness=t, height=h, closed=True)
        for obj in made:
            obj[AUTO_KEY] = True
            _concrete(obj)
        fl = hb_house.get_level(uid)
        # The footing band, centred under the wall
        out = (fw - t) / 2.0
        mesh = _band_mesh("Footing", geom.offset_polygon(poly, out),
                          geom.offset_polygon(poly, -(t + out)),
                          fl.elevation - fd, fl.elevation)
        _add_part(scene, fl, "Footing", mesh)
    if kind == 'CRAWL':
        _girders(scene, uid, hb_house.get_level(ground_uid), outlines, t)


def _girders(scene, uid, ground, outlines, t):
    """Girders on piers across a crawlspace too wide for the joists to
    span from wall to wall, square to them, splitting the span evenly;
    generated like the walls (AUTO_KEY), so a rebuild replaces them."""
    import math
    from mathutils import Vector
    from . import hb_framing, hb_members
    fl = hb_house.get_level(uid)
    # The stem walls' middles are what the joists bear on without girders
    bearings = []
    for poly in outlines:
        mid = geom.offset_polygon(poly, -t / 2.0)
        bearings += [(mid[i], mid[(i + 1) % len(mid)]) for i in range(len(mid))]
    axis = hb_framing.joist_axis(ground, outlines, bearings)
    ax = Vector(axis)
    run = Vector((-ax.y, ax.x))             # the way the joists run
    top = ground.elevation - SUBFLOOR - GROUND_JOIST
    w, d, plies = GIRDER
    for poly in outlines:
        inner = geom.offset_polygon(poly, -t)
        vals = [Vector(p).dot(run) for p in inner]
        lo, hi = min(vals), max(vals)
        n = math.ceil((hi - lo) / MAX_JOIST_SPAN)
        if n < 2:
            continue
        span = max(Vector(p).dot(ax) for p in inner) - min(Vector(p).dot(ax) for p in inner)
        for k in range(1, n):
            c = lo + (hi - lo) * k / n
            a = run * c + ax * (min(Vector(p).dot(ax) for p in inner) - 1.0)
            b = a + ax * (span + 2.0)
            for t0, t1 in geom.segment_in_polygon_spans(tuple(a), tuple(b), inner):
                p, q = a + (b - a) * t0, a + (b - a) * t1
                # Into the stem walls a little at each end, to bear on them
                p, q = p - ax * (t / 2.0), q + ax * (t / 2.0)
                length = (q - p).length
                if length < 0.5:
                    continue
                girder = hb_members._new(scene, fl, "Girder", 'GIRDER', 'LUMBER', w, d, plies, length)
                girder[AUTO_KEY] = True
                girder['MEMBER_POSITION'] = 'FLUSH'
                girder.location = (p.x, p.y, top)
                girder.rotation_euler = (0.0, 0.0, math.atan2(q.y - p.y, q.x - p.x))
                hb_members.rebuild(girder)
                inside = length - t
                count = max(1, math.ceil(inside / PIER_SPACING) - 1)
                for j in range(1, count + 1):
                    pt = p + (q - p) * ((t / 2.0 + inside * j / (count + 1)) / length)
                    pier = hb_members._new(scene, fl, "Pier", 'PIER', 'CONCRETE', PIER, PIER, 1,
                                           top - d - fl.elevation)
                    pier[AUTO_KEY] = True
                    pier.location = (pt.x, pt.y, fl.elevation)
                    hb_members.rebuild(pier)


def _concrete(obj):
    from . import hb_types
    wall = hb_types.GeoNodeWall(obj)
    mat = concrete_material()
    for name in ('Left Edge', 'Right Edge', 'Inside Face', 'Outside Face'):
        if wall.has_input(name):
            wall.set_input(name, mat)
    obj.update_tag()


def _settings_changed(self, context):
    scene = self.id_data
    rebuild(scene)
    # The ground level's floor framing changes with what is under it
    from . import hb_framing
    if scene.hb_house.show_framing:
        hb_framing.build(scene)


class HOME_BUILDER_OT_rebuild_foundation(bpy.types.Operator):
    """Build the foundation again round the ground level's walls"""
    bl_idname = "home_builder.rebuild_foundation"
    bl_label = "Rebuild Foundation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_house.is_house_project(context) and context.scene.get(hb_house.HOUSE_SCENE_KEY)

    def execute(self, context):
        rebuild(context.scene)
        return {'FINISHED'}


classes = (HOME_BUILDER_OT_rebuild_foundation,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
