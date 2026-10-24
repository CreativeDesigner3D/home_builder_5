"""
Exterior finish: siding on the outside of the house and a masonry base.

House-wide settings on hb_house (siding style and colour, base style,
colour and height). The siding is a material on the Outside Face of every
exterior wall and on the walls the roofs make (filled-in gable ends,
dormer walls). It is procedural, laid out in world space so boards line
up from wall to wall: board and batten (vertical battens every 16") or lap
(horizontal boards), shown in Material Preview and renders; in solid view
the walls take its colour.

The base is a band of brick (or stone) standing just proud of the outside
of the ground level's exterior walls, from a little below the floor up to
the base height. It stops at doors, at any window that comes down into
it, and where the wall faces a porch (the porch's floor is there).
One object per house, rebuilt with the walls.
"""

import math

import bmesh
import bpy

from . import hb_house, hb_wall_graph

SIDING_MATERIAL = "HB Siding"
BASE_MATERIAL = "HB Masonry Base"
BASE_OBJECT = "Exterior Base"
BASE_KEY = 'IS_EXTERIOR_BASE'
BASE_PROUD = 0.03           # how far the base stands out from the wall (m)
BASE_BELOW = 0.15           # and how far it runs down past the floor
BATTEN_SPACING = 0.4064     # 16"
BATTEN_WIDTH = 0.038        # 1 1/2"
LAP_EXPOSURE = 0.152        # 6" lap boards


# ---- Materials ------------------------------------------------------------------

def _nodes_reset(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return nt, bsdf


def _run_coordinate(nt):
    """A world-space coordinate that runs along any wall: x + y. Walls
    square to the axes see it advance along their length."""
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    nt.links.new(sep.outputs['X'], add.inputs[0])
    nt.links.new(sep.outputs['Y'], add.inputs[1])
    return add.outputs[0], sep.outputs['Z']


def _stripes(nt, coord, spacing, width, soft=0.006):
    """1 on a stripe `width` wide every `spacing` along coord, else 0,
    with edges eased over `soft` metres - a hard step gives a bump
    nothing to show."""
    div = nt.nodes.new('ShaderNodeMath')
    div.operation = 'DIVIDE'
    nt.links.new(coord, div.inputs[0])
    div.inputs[1].default_value = spacing
    frac = nt.nodes.new('ShaderNodeMath')
    frac.operation = 'FRACT'
    nt.links.new(div.outputs[0], frac.inputs[0])
    # Distance from the stripe's middle, in metres
    centre = nt.nodes.new('ShaderNodeMath')
    centre.operation = 'MULTIPLY_ADD'
    nt.links.new(frac.outputs[0], centre.inputs[0])
    centre.inputs[1].default_value = spacing
    centre.inputs[2].default_value = -width / 2.0
    dist = nt.nodes.new('ShaderNodeMath')
    dist.operation = 'ABSOLUTE'
    nt.links.new(centre.outputs[0], dist.inputs[0])
    edge = nt.nodes.new('ShaderNodeMapRange')
    edge.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(dist.outputs[0], edge.inputs['Value'])
    edge.inputs['From Min'].default_value = width / 2.0 + soft
    edge.inputs['From Max'].default_value = width / 2.0 - soft
    edge.inputs['To Min'].default_value = 0.0
    edge.inputs['To Max'].default_value = 1.0
    return edge.outputs['Result']


def siding_material(style, color):
    """The siding material, (re)built for a style and colour."""
    mat = bpy.data.materials.get(SIDING_MATERIAL) or bpy.data.materials.new(SIDING_MATERIAL)
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    nt, bsdf = _nodes_reset(mat)
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = 0.6
    run, z = _run_coordinate(nt)
    if style == 'LAP':
        # Each board's bottom edge stands proud: a sawtooth up its exposure
        div = nt.nodes.new('ShaderNodeMath')
        div.operation = 'DIVIDE'
        nt.links.new(z, div.inputs[0])
        div.inputs[1].default_value = LAP_EXPOSURE
        frac = nt.nodes.new('ShaderNodeMath')
        frac.operation = 'FRACT'
        nt.links.new(div.outputs[0], frac.inputs[0])
        inv = nt.nodes.new('ShaderNodeMath')
        inv.operation = 'SUBTRACT'
        inv.inputs[0].default_value = 1.0
        nt.links.new(frac.outputs[0], inv.inputs[1])
        height = inv.outputs[0]
        strength = 0.4
    else:
        height = _stripes(nt, run, BATTEN_SPACING, BATTEN_WIDTH)
        strength = 0.6
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    if 'Distance' in bump.inputs:
        bump.inputs['Distance'].default_value = 0.01
    nt.links.new(height, bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    if style != 'LAP':
        # Battens a shade darker, so they read from a distance
        shade = nt.nodes.new('ShaderNodeMix')
        shade.data_type = 'RGBA'
        shade.inputs['A'].default_value = rgba
        shade.inputs['B'].default_value = (color[0] * 0.9, color[1] * 0.9, color[2] * 0.9, 1.0)
        nt.links.new(height, shade.inputs['Factor'])
        nt.links.new(shade.outputs['Result'], bsdf.inputs['Base Color'])
    return mat


def base_material(style, color):
    """The base material: brick in running bond, or rough stone."""
    mat = bpy.data.materials.get(BASE_MATERIAL) or bpy.data.materials.new(BASE_MATERIAL)
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    nt, bsdf = _nodes_reset(mat)
    bsdf.inputs['Roughness'].default_value = 0.85
    run, z = _run_coordinate(nt)
    vec = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(run, vec.inputs['X'])
    nt.links.new(z, vec.inputs['Y'])
    if style == 'STONE':
        tex = nt.nodes.new('ShaderNodeTexVoronoi')
        tex.inputs['Scale'].default_value = 6.0
        nt.links.new(vec.outputs[0], tex.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeMix')
        ramp.data_type = 'RGBA'
        ramp.inputs['A'].default_value = rgba
        ramp.inputs['B'].default_value = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1.0)
        nt.links.new(tex.outputs['Distance'], ramp.inputs['Factor'])
        nt.links.new(ramp.outputs['Result'], bsdf.inputs['Base Color'])
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.5
        nt.links.new(tex.outputs['Distance'], bump.inputs['Height'])
    else:
        tex = nt.nodes.new('ShaderNodeTexBrick')
        tex.offset = 0.5
        tex.inputs['Color1'].default_value = rgba
        tex.inputs['Color2'].default_value = (color[0] * 0.8, color[1] * 0.75, color[2] * 0.75, 1.0)
        tex.inputs['Mortar'].default_value = (0.75, 0.73, 0.70, 1.0)
        tex.inputs['Scale'].default_value = 1.0
        tex.inputs['Mortar Size'].default_value = 0.01
        tex.inputs['Brick Width'].default_value = 0.2
        tex.inputs['Row Height'].default_value = 0.067
        nt.links.new(vec.outputs[0], tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.3
        bump.invert = True
        nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


# ---- The base band -------------------------------------------------------------------

def _gaps(wall_obj, base_top):
    """Spans along a wall (local x) its openings take out of the base:
    doors, and windows that come down into it."""
    from . import hb_types
    out = []
    for child in wall_obj.children:
        if not (child.get('IS_ENTRY_DOOR_BP') or child.get('IS_WINDOW_BP')):
            continue
        cage = hb_types.GeoNodeCage(child)
        if not cage.has_modifier():
            continue
        if child.location.z >= base_top - 1e-4:
            continue
        x0 = child.location.x
        out.append((x0, x0 + cage.get_input('Dim X')))
    return sorted(out)


def _porch_polygons(scene, level):
    from . import hb_porches
    from .operators import walls
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    return [a.polygon for a in hb_wall_graph.find_rooms(segs) if hb_porches.is_porch_area(a)]


def base_mesh(scene, level, height):
    """The base band along the outside of a level's exterior walls."""
    from . import hb_types
    from .operators import walls
    porches = _porch_polygons(scene, level)
    bm = bmesh.new()
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    for seg in segs:
        if seg.wall_type != 'Exterior':
            continue
        obj = scene.objects[seg.id]
        n, d, t = seg.normal, seg.dir, seg.thickness
        # Facing a porch: its floor is there instead
        mid = hb_wall_graph._mul(hb_wall_graph._add(seg.start, seg.end), 0.5)
        probe = (mid[0] + n[0] * (t + 0.3), mid[1] + n[1] * (t + 0.3))
        if any(hb_wall_graph.point_in_polygon(probe, poly) for poly in porches):
            continue
        # Each end runs on past the corner, round the wall it meets
        reach = t + BASE_PROUD
        spans = [(-reach, seg.length + reach)]
        for g0, g1 in _gaps(obj, height):
            cut = []
            for a, b in spans:
                if g1 <= a or g0 >= b:
                    cut.append((a, b))
                    continue
                if g0 > a:
                    cut.append((a, g0))
                if g1 < b:
                    cut.append((g1, b))
            spans = cut
        z0, z1 = level.elevation - BASE_BELOW, level.elevation + height
        for a, b in spans:
            if b - a < 0.02:
                continue
            corners = []
            for along in (a, b):
                for out in (t, t + BASE_PROUD):
                    corners.append((seg.start[0] + d[0] * along + n[0] * out,
                                    seg.start[1] + d[1] * along + n[1] * out))
            p = [corners[0], corners[2], corners[3], corners[1]]
            low = [bm.verts.new((x, y, z0)) for x, y in p]
            high = [bm.verts.new((x, y, z1)) for x, y in p]
            bm.faces.new(low)
            bm.faces.new(high[::-1])
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((low[i], low[j], high[j], high[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(BASE_OBJECT)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _base_object(scene):
    return next((o for o in scene.objects if o.get(BASE_KEY)), None)


# ---- Applying ----------------------------------------------------------------------

# A GeoNodeWall's two big faces, whatever its inputs are called: the
# reference side and the side its thickness is on. ('Inside Face' and
# 'Outside Face' are its ends.)
REF_SIDE = 'Left Edge'
THICK_SIDE = 'Right Edge'


def _indoor_polygons(scene):
    """{level uid: [room outlines]} - the rooms, porches left out."""
    from . import hb_porches
    from .operators import walls
    out = {}
    for level in scene.hb_house.levels:
        _objs, segs = walls.level_wall_segs(scene, level.uid)
        out[level.uid] = [a.polygon for a in hb_wall_graph.find_rooms(segs)
                          if not hb_porches.is_porch_area(a)]
    return out


def _outside_input(obj, wall, rooms):
    """Which of a wall's big faces is outdoors. A wall's thickness falls
    to one side of its reference line - outward or inward depending on
    how it was drawn - so look which side has the house's rooms. A
    dormer front's thickness is always inward."""
    if obj.get('WALL_TYPE') == 'Dormer':
        return REF_SIDE
    from mathutils import Vector
    m = obj.matrix_world
    t = wall.get_input('Thickness')
    mid = wall.get_input('Length') / 2.0
    thick_side = m @ Vector((mid, t + 0.3, 0.0))
    if any(hb_wall_graph.point_in_polygon((thick_side.x, thick_side.y), poly) for poly in rooms):
        return REF_SIDE
    return THICK_SIDE

def _roof_walls(scene):
    for level in scene.hb_house.levels:
        for obj in (level.roof.gables_obj, level.roof.dormer_walls_obj):
            if obj is not None:
                yield obj


def apply_exterior_finish(scene):
    """Put the house's siding and base on, or take them off."""
    from . import hb_types
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    house = scene.hb_house
    siding = (siding_material(house.siding_style, house.siding_color)
              if house.siding_style != 'NONE' else None)
    rooms = _indoor_polygons(scene)
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP'):
            continue
        if obj.get('WALL_TYPE', 'Exterior') not in ('Exterior', 'Dormer'):
            continue
        wall = hb_types.GeoNodeWall(obj)
        if not (wall.has_modifier() and wall.has_input(THICK_SIDE)):
            continue
        outside = _outside_input(obj, wall, rooms.get(obj.get(hb_house.LEVEL_KEY, ''), []))
        for name in (THICK_SIDE, REF_SIDE, 'Inside Face', 'Outside Face'):
            if not wall.has_input(name):
                continue
            if name == outside:
                wall.set_input(name, siding)
            elif wall.get_input(name) is not None and wall.get_input(name).name == SIDING_MATERIAL:
                wall.set_input(name, None)
        obj.update_tag()
    for obj in _roof_walls(scene):
        if siding is not None:
            obj.data.materials.clear()
            obj.data.materials.append(siding)

    old = _base_object(scene)
    ground = min(house.levels, key=lambda l: l.elevation) if len(house.levels) else None
    if house.base_style == 'NONE' or ground is None or house.base_height <= 0:
        if old is not None:
            mesh = old.data
            bpy.data.objects.remove(old, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        return
    mesh = base_mesh(scene, ground, house.base_height)
    mesh.materials.append(base_material(house.base_style, house.base_color))
    if old is None:
        obj = bpy.data.objects.new(BASE_OBJECT, mesh)
        obj[BASE_KEY] = True
        obj[hb_house.LEVEL_KEY] = ground.uid
        hb_house.ensure_level_collections(scene, ground)
        hb_house.level_subcollection(ground, 'Walls').objects.link(obj)
    else:
        prev = old.data
        old.data = mesh
        if prev.users == 0:
            bpy.data.meshes.remove(prev)
        obj = old
    obj.color = mesh.materials[0].diffuse_color
