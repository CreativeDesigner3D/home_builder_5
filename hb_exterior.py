"""
Exterior finish: siding on the outside of the house and a masonry base.

The house has a siding finish and colour (hb_house): board and batten,
lap, shingles, stucco, brick or stone. A level can have its own, and so
can any outside wall (Object.hb_siding) - the wall's own wins, then its
level's, then the house's. The gable ends and the walls the roofs make
(dormer walls) can have theirs too. Each finish is a material on the
outdoor face of the wall: procedural, laid out in world space so boards
line up from wall to wall, shown in Material Preview and renders; in
solid view the walls take its colour.

With Real Geometry on, board and batten, lap and shingles are also
built: battens standing proud of the boards, lap boards and shingle rows
each thicker at the bottom. They are cut from the walls as built -
trimmed to the roof, stopping at windows and doors - one object per
level.

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

SIDING_MATERIAL = "HB Siding"     # every siding material's name starts with this
BASE_MATERIAL = "HB Masonry Base"
BASE_OBJECT = "Exterior Base"
BASE_KEY = 'IS_EXTERIOR_BASE'
BASE_PROUD = 0.03           # how far the base stands out from the wall (m)
BASE_BELOW = 0.15           # and how far it runs down past the floor
BATTEN_SPACING = 0.4064     # 16"
BATTEN_WIDTH = 0.038        # 1 1/2"
LAP_EXPOSURE = 0.152        # 6" lap boards
SHINGLE_EXPOSURE = 0.178    # 7" shingle rows
BATTEN_PROUD = 0.019        # real battens stand 3/4" off the boards
LAP_PROUD = 0.019           # a real lap board's bottom edge, off the wall
SHINGLE_PROUD = 0.013       # and a shingle row's
ROW_TOP = 0.003             # the top of a lap board or shingle row
GEO_KEY = 'IS_SIDING_GEOMETRY'
BUILT = ('BOARD_BATTEN', 'LAP', 'SHINGLE')     # finishes Real Geometry builds
CORNER_WIDTH = 0.089        # a corner board's face, 3 1/2"
CORNER_THICK = 0.025        # and its thickness, 1": proud of the siding
TRIM_MATERIAL = "HB Exterior Trim"
TRIM_COLOR = (0.93, 0.93, 0.91)


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


def _sawtooth(nt, z, spacing):
    """Rises from 0 at the top of each row to 1 at its bottom edge."""
    div = nt.nodes.new('ShaderNodeMath')
    div.operation = 'DIVIDE'
    nt.links.new(z, div.inputs[0])
    div.inputs[1].default_value = spacing
    frac = nt.nodes.new('ShaderNodeMath')
    frac.operation = 'FRACT'
    nt.links.new(div.outputs[0], frac.inputs[0])
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(frac.outputs[0], inv.inputs[1])
    return inv.outputs[0]


def _bump(nt, bsdf, height, strength, distance=0.01, invert=False):
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.invert = invert
    if 'Distance' in bump.inputs:
        bump.inputs['Distance'].default_value = distance
    nt.links.new(height, bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])


def _masonry(nt, bsdf, style, rgba, run, z):
    """Brick in running bond, or rough stone, on a world-space wall."""
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
        ramp.inputs['B'].default_value = (rgba[0] * 0.7, rgba[1] * 0.7, rgba[2] * 0.7, 1.0)
        nt.links.new(tex.outputs['Distance'], ramp.inputs['Factor'])
        nt.links.new(ramp.outputs['Result'], bsdf.inputs['Base Color'])
        _bump(nt, bsdf, tex.outputs['Distance'], 0.5)
    else:
        tex = nt.nodes.new('ShaderNodeTexBrick')
        tex.offset = 0.5
        tex.inputs['Color1'].default_value = rgba
        tex.inputs['Color2'].default_value = (rgba[0] * 0.8, rgba[1] * 0.75, rgba[2] * 0.75, 1.0)
        tex.inputs['Mortar'].default_value = (0.75, 0.73, 0.70, 1.0)
        tex.inputs['Scale'].default_value = 1.0
        tex.inputs['Mortar Size'].default_value = 0.01
        tex.inputs['Brick Width'].default_value = 0.2
        tex.inputs['Row Height'].default_value = 0.067
        nt.links.new(vec.outputs[0], tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        _bump(nt, bsdf, tex.outputs['Fac'], 0.3, invert=True)


def _finish_name(style, color, built):
    hexcode = "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in color[:3])
    return f"{style.title().replace('_', ' ')} #{hexcode}" + (" Built" if built else "")


def _finish_nodes(nt, style, color, built):
    """Lay one finish into a material's node tree: its own Principled BSDF,
    returned. With `built`, the shapes Real Geometry builds (battens, lap
    and shingle rows) are left out."""
    rgba = (color[0], color[1], color[2], 1.0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = 0.6
    run, z = _run_coordinate(nt)
    if style in ('BRICK', 'STONE'):
        bsdf.inputs['Roughness'].default_value = 0.85
        _masonry(nt, bsdf, style, rgba, run, z)
        return bsdf
    if style == 'STUCCO':
        bsdf.inputs['Roughness'].default_value = 0.9
        tex = nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 60.0
        tex.inputs['Detail'].default_value = 8.0
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        nt.links.new(geo.outputs['Position'], tex.inputs['Vector'])
        _bump(nt, bsdf, tex.outputs['Fac'], 0.25, distance=0.003)
        return bsdf
    if style == 'SHINGLE':
        # Rows of shingles of varied widths and shades, gaps between
        vec = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(run, vec.inputs['X'])
        nt.links.new(z, vec.inputs['Y'])
        tex = nt.nodes.new('ShaderNodeTexBrick')
        tex.offset = 0.5
        tex.squash = 0.6
        tex.squash_frequency = 3
        tex.inputs['Color1'].default_value = rgba
        tex.inputs['Color2'].default_value = (color[0] * 0.82, color[1] * 0.8, color[2] * 0.78, 1.0)
        tex.inputs['Mortar'].default_value = (color[0] * 0.35, color[1] * 0.33, color[2] * 0.3, 1.0)
        tex.inputs['Scale'].default_value = 1.0
        tex.inputs['Mortar Size'].default_value = 0.004
        tex.inputs['Brick Width'].default_value = 0.17
        tex.inputs['Row Height'].default_value = SHINGLE_EXPOSURE
        nt.links.new(vec.outputs[0], tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        if not built:
            _bump(nt, bsdf, _sawtooth(nt, z, SHINGLE_EXPOSURE), 0.35)
        return bsdf
    if built or style not in ('LAP', 'BOARD_BATTEN'):
        return bsdf             # plain boards: the battens or laps are real
    if style == 'LAP':
        # Each board's bottom edge stands proud: a sawtooth up its exposure
        _bump(nt, bsdf, _sawtooth(nt, z, LAP_EXPOSURE), 0.4)
        return bsdf
    height = _stripes(nt, run, BATTEN_SPACING, BATTEN_WIDTH)
    _bump(nt, bsdf, height, 0.6)
    # Battens a shade darker, so they read from a distance
    shade = nt.nodes.new('ShaderNodeMix')
    shade.data_type = 'RGBA'
    shade.inputs['A'].default_value = rgba
    shade.inputs['B'].default_value = (color[0] * 0.9, color[1] * 0.9, color[2] * 0.9, 1.0)
    nt.links.new(height, shade.inputs['Factor'])
    nt.links.new(shade.outputs['Result'], bsdf.inputs['Base Color'])
    return bsdf


def _material(name, color):
    """A siding material by name: (material, node tree or None). The tree
    comes back empty, but for an output, when the material needs making."""
    full = f"{SIDING_MATERIAL} {name}"
    mat = bpy.data.materials.get(full)
    if mat is not None and mat.get('hb_finish') == full:
        return mat, None
    mat = mat or bpy.data.materials.new(full)
    mat['hb_finish'] = full
    mat.diffuse_color = (color[0], color[1], color[2], 1.0)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    nt.nodes.new('ShaderNodeOutputMaterial')
    return mat, nt


def _output(nt):
    return next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')


def siding_material(style, color, built=False):
    """The material for a siding finish and colour - shared by every wall
    with that finish. With `built`, the shapes Real Geometry builds are
    left out of it."""
    built = built and style in BUILT
    mat, nt = _material(_finish_name(style, color, built), color)
    if nt is not None:
        bsdf = _finish_nodes(nt, style, color, built)
        nt.links.new(bsdf.outputs['BSDF'], _output(nt).inputs['Surface'])
    return mat


def split_material(below, above, split_z, built=False):
    """One wall's material with two finishes: `below` up to split_z (the
    eaves), `above` over it - a gable end's own siding above its walls'."""
    (s0, c0), (s1, c1) = below, above
    b0, b1 = built and s0 in BUILT, built and s1 in BUILT
    name = (f"{_finish_name(s0, c0, b0)} / {_finish_name(s1, c1, b1)} "
            f"at {round(split_z * 1000)}mm")
    mat, nt = _material(name, c0)
    if nt is None:
        return mat
    low = _finish_nodes(nt, s0, c0, b0)
    high = _finish_nodes(nt, s1, c1, b1)
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    over = nt.nodes.new('ShaderNodeMath')
    over.operation = 'GREATER_THAN'
    nt.links.new(sep.outputs['Z'], over.inputs[0])
    over.inputs[1].default_value = split_z
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(over.outputs[0], mix.inputs['Fac'])
    nt.links.new(low.outputs['BSDF'], mix.inputs[1])
    nt.links.new(high.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], _output(nt).inputs['Surface'])
    return mat


def base_material(style, color):
    """The base material: brick in running bond, or rough stone."""
    mat = bpy.data.materials.get(BASE_MATERIAL) or bpy.data.materials.new(BASE_MATERIAL)
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    nt, bsdf = _nodes_reset(mat)
    bsdf.inputs['Roughness'].default_value = 0.85
    run, z = _run_coordinate(nt)
    _masonry(nt, bsdf, style, rgba, run, z)
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
    rooms = _indoor_polygons(scene).get(level.uid, [])
    bm = bmesh.new()
    _objs, segs = walls.level_wall_segs(scene, level.uid)

    def indoors(p):
        return any(hb_wall_graph.point_in_polygon(p, poly) for poly in rooms)

    for seg in segs:
        if seg.wall_type != 'Exterior':
            continue
        obj = scene.objects[seg.id]
        n, d, t = seg.normal, seg.dir, seg.thickness
        # The base goes on the side with no room: a wall's thickness falls
        # outward or inward depending on how it was drawn (as the siding
        # finds). A wall with rooms both sides is inside the house,
        # whatever it is marked, and has none.
        mid = hb_wall_graph._mul(hb_wall_graph._add(seg.start, seg.end), 0.5)
        thick_probe = (mid[0] + n[0] * (t + 0.3), mid[1] + n[1] * (t + 0.3))
        ref_probe = (mid[0] - n[0] * 0.3, mid[1] - n[1] * 0.3)
        thick_in, ref_in = indoors(thick_probe), indoors(ref_probe)
        if thick_in and ref_in:
            continue
        if thick_in:
            face, sign, probe = 0.0, -1.0, ref_probe
        else:
            face, sign, probe = t, 1.0, thick_probe
        # Facing a porch: its floor is there instead
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
                for out in (face, face + sign * BASE_PROUD):
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


# ---- Real siding geometry -------------------------------------------------------------

def _clip(poly, axis, value, keep_above):
    """A polygon of (s, z) points cut by the line axis == value, keeping
    the side above it (or below)."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina = (a[axis] >= value) if keep_above else (a[axis] <= value)
        inb = (b[axis] >= value) if keep_above else (b[axis] <= value)
        if ina:
            out.append(a)
        if ina != inb:
            t = (value - a[axis]) / (b[axis] - a[axis])
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _strip(poly, axis, lo, hi):
    return _clip(_clip(poly, axis, lo, True), axis, hi, False)


def _area(poly):
    """A polygon's area (shoelace), unsigned."""
    n = len(poly)
    return abs(sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
                   for i in range(n))) / 2.0


MIN_FACE_AREA = 0.01        # m2: a wall face smaller is a sliver the boolean left
MIN_PIECE_AREA = 1e-5       # m2: a batten or row piece smaller is a line


def _outdoor_faces(obj, mesh, rooms, both_sides):
    """The upright faces of an evaluated wall that look outdoors, as
    triangles (normal, plane offset, [(s, z)] x 3): s along the face, z
    up. Triangles, because a cut leaves a face round an opening as one
    polygon that reaches round the hole along a slit - clipped whole it
    would fill the opening back in; its triangles never cover it. A face
    looks outdoors when a step out from it isn't in one of the level's
    rooms; the roof-made walls have no rooms beside them, so `both_sides`
    takes both of their faces."""
    from mathutils import Vector
    m = obj.matrix_world
    rot = m.to_3x3()
    mesh.calc_loop_triangles()
    tris = {}
    for tri in mesh.loop_triangles:
        tris.setdefault(tri.polygon_index, []).append(tri.vertices)
    out = []
    for f in mesh.polygons:
        n = rot @ f.normal
        if abs(n.z) > 0.05 or n.length < 1e-6:
            continue
        n = Vector((n.x, n.y, 0.0)).normalized()
        pts = [m @ mesh.vertices[i].co for i in f.vertices]
        a = Vector((-n.y, n.x, 0.0))
        poly = [(p.dot(a), p.z) for p in pts]
        ss = [p[0] for p in poly]
        zs = [p[1] for p in poly]
        if (max(ss) - min(ss) < 0.25 or max(zs) - min(zs) < 0.05
                or _area(poly) < MIN_FACE_AREA):
            continue                # a wall's end, or a sliver (a cut can leave them across an opening)
        if not both_sides:
            # Which way a face looks can't be read from its normal (a wall
            # drawn the other way round has its faces turned): a face just
            # off a room is an inside face; the outdoor side of the others
            # is the one whose step out isn't in a room
            c = sum(pts, Vector()) / len(pts)
            in_room = lambda d: any(hb_wall_graph.point_in_polygon(((c + n * d).x, (c + n * d).y), r)
                                    for r in rooms)
            if in_room(0.05) or in_room(-0.05):
                continue
            if in_room(0.25) and not in_room(-0.25):
                n = -n
                a = Vector((-n.y, n.x, 0.0))
        offset = pts[0].dot(n)
        for tri in tris.get(f.index, ()):
            corners = [m @ mesh.vertices[i].co for i in tri]
            out.append((n, offset, [(p.dot(a), p.z) for p in corners]))
    return out


def _add_prism(bm, n, offset, poly, depth_at):
    """A solid from a face polygon out to depth_at(z) off the face."""
    from mathutils import Vector
    if len(poly) < 3 or _area(poly) < MIN_PIECE_AREA:
        return
    a = Vector((-n.y, n.x, 0.0))
    up = Vector((0.0, 0.0, 1.0))

    def point(s, z, d):
        return n * (offset + d) + a * s + up * z
    back = [bm.verts.new(point(s, z, 0.0)) for s, z in poly]
    front = [bm.verts.new(point(s, z, depth_at(z))) for s, z in poly]
    try:
        bm.faces.new(back)
        bm.faces.new(front[::-1])
        k = len(poly)
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((back[i], back[j], front[j], front[i]))
    except ValueError:
        pass


def _simplify(poly, tol=1e-5):
    """A polygon without its in-line points (left where pieces met)."""
    out = list(poly)
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if abs(cross) < tol * max(1e-9, math.dist(a, c)):
                del out[i]
                changed = True
                break
    return out


def _merge(pieces):
    """Pieces of one board (from the triangles of a wall's faces) joined
    into whole outlines: the edges between them dissolved, the points
    left in line dropped."""
    bm = bmesh.new()
    for p in pieces:
        if len(p) < 3 or _area(p) < MIN_PIECE_AREA:
            continue
        try:
            bm.faces.new([bm.verts.new((x, z, 0.0)) for x, z in p])
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    inner = [e for e in bm.edges if len(e.link_faces) == 2]
    if inner:
        bmesh.ops.dissolve_edges(bm, edges=inner, use_verts=False)
    out = []
    for f in bm.faces:
        poly = _simplify([(v.co.x, v.co.y) for v in f.verts])
        if len(poly) >= 3 and _area(poly) >= MIN_PIECE_AREA:
            out.append(poly)
    bm.free()
    return out


def _build_plane(bm, style, n, offset, polys):
    """The battens, or the lap or shingle rows, over the parts of a wall's
    outside in one plane: each board one solid, whatever triangles the
    wall's faces came in."""
    ss = [p[0] for poly in polys for p in poly]
    zs = [p[1] for poly in polys for p in poly]
    if style == 'BOARD_BATTEN':
        half = BATTEN_WIDTH / 2.0
        for k in range(math.floor(min(ss) / BATTEN_SPACING), math.ceil(max(ss) / BATTEN_SPACING) + 1):
            c = k * BATTEN_SPACING
            for piece in _merge([_strip(poly, 0, c - half, c + half) for poly in polys]):
                _add_prism(bm, n, offset, piece, lambda z: BATTEN_PROUD)
        return
    exposure, proud = (LAP_EXPOSURE, LAP_PROUD) if style == 'LAP' else (SHINGLE_EXPOSURE, SHINGLE_PROUD)
    for k in range(math.floor(min(zs) / exposure), math.ceil(max(zs) / exposure)):
        bottom, top = k * exposure, (k + 1) * exposure
        for piece in _merge([_strip(poly, 1, bottom, top) for poly in polys]):
            # Thicker at the bottom edge, like a board lapped over the one below
            _add_prism(bm, n, offset, piece,
                       lambda z, top=top: ROW_TOP + (proud - ROW_TOP) * (top - z) / exposure)


def _plane_edges(n, offset, polys):
    """The upright edges of the outline of a wall's outside in one plane:
    (point in plan, z from, z to, the way along the plane the face lies)."""
    from mathutils import Vector
    a = Vector((-n.y, n.x, 0.0))
    out = []
    for poly in _merge(polys):
        ss = [p[0] for p in poly]
        lo, hi = min(ss), max(ss)
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            if abs(p[0] - q[0]) > 1e-4 or abs(p[1] - q[1]) < 0.05:
                continue
            s = p[0]
            if hi - lo < 1e-6:
                continue
            side = 1.0 if s - lo < hi - s else -1.0
            point = n * offset + a * s
            out.append((point.to_2d(), min(p[1], q[1]), max(p[1], q[1]), a * side, s, side))
    return out


def _corner_boards(bm, planes):
    """Corner boards where two walls' outsides meet at an outside corner:
    an L of two boards standing over the siding's ends, up the corner."""
    keys = list(planes)
    edges = {k: _plane_edges(*planes[k]) for k in keys}
    made = 0
    for i, ka in enumerate(keys):
        na = planes[ka][0]
        for kb in keys[i + 1:]:
            nb = planes[kb][0]
            if abs(na.dot(nb)) > 0.9:
                continue                    # in line, or facing each other
            for pa, za0, za1, exa, sa, sida in edges[ka]:
                for pb, zb0, zb1, exb, sb, sidb in edges[kb]:
                    if (pa - pb).length > 0.03:
                        continue
                    z0, z1 = max(za0, zb0), min(za1, zb1)
                    if z1 - z0 < 0.1:
                        continue
                    # Outside: each face runs away from the other's front
                    if nb.dot(exa) > -0.3 or na.dot(exb) > -0.3:
                        continue
                    # One board runs on past the corner by the other's thickness
                    a_lo, a_hi = sorted((sa - sida * CORNER_THICK, sa + sida * CORNER_WIDTH))
                    b_lo, b_hi = sorted((sb, sb + sidb * CORNER_WIDTH))
                    for (n, off), lo, hi in (((na, planes[ka][1]), a_lo, a_hi),
                                             ((nb, planes[kb][1]), b_lo, b_hi)):
                        _add_prism(bm, n, off, [(lo, z0), (hi, z0), (hi, z1), (lo, z1)],
                                   lambda z: CORNER_THICK)
                    made += 1
    return made


def trim_material():
    mat = bpy.data.materials.get(TRIM_MATERIAL) or bpy.data.materials.new(TRIM_MATERIAL)
    mat.diffuse_color = TRIM_COLOR + (1.0,)
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = next((nd for nd in mat.node_tree.nodes if nd.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = TRIM_COLOR + (1.0,)
        bsdf.inputs['Roughness'].default_value = 0.5
    return mat


def _geometry_object(scene, level):
    return next((o for o in scene.objects
                 if o.get(GEO_KEY) and o.get(hb_house.LEVEL_KEY) == level.uid), None)


def build_siding_geometry(scene, walls_done, roof_done, rooms):
    """Real battens, lap boards and shingle rows on the outside of the
    walls, one object per level - or none, with Real Geometry off."""
    house = scene.hb_house
    wanted = {}
    corners = {}                # level uid -> {plane: (normal, offset, polygons)}
    if house.siding_geometry:
        jobs = ([(o, f, g, z, False) for o, f, g, z in walls_done]
                + [(o, f, g, z, True) for o, f, g, z in roof_done])
        jobs = [j for j in jobs if j[1][0] in BUILT or (j[2] is not None and j[2][0] in BUILT)]
        if jobs:
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
        for obj, finish, gable, split, both in jobs:
            level = _level_of(scene, obj)
            if level is None:
                continue
            ev = obj.evaluated_get(dg)
            try:
                mesh = ev.to_mesh()
            except RuntimeError:
                continue
            faces = _outdoor_faces(obj, mesh, rooms.get(level.uid, []), both)
            ev.to_mesh_clear()
            if not faces:
                continue
            planes = wanted.setdefault(level.uid, {})
            for n, offset, poly in faces:
                if gable is None:
                    parts = [(finish, poly)]
                else:
                    parts = [(finish, _clip(poly, 1, split, False)), (gable, _clip(poly, 1, split, True))]
                for part_finish, part in parts:
                    if part_finish[0] not in BUILT or len(part) < 3:
                        continue
                    # Gathered by plane, so a board runs whole across the
                    # wall's faces (and on along walls in line with it)
                    key = (part_finish, round(n.x, 4), round(n.y, 4), round(offset, 4))
                    planes.setdefault(key, (n, offset, []))[2].append(part)
                    # And by plane alone, for finding the outside corners
                    whole = corners.setdefault(level.uid, {})
                    whole.setdefault(key[1:], (n, offset, []))[2].append(part)
    for level in house.levels:
        obj = _geometry_object(scene, level)
        if level.uid not in wanted:
            if obj is not None:
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            continue
        bm, mats = bmesh.new(), {}
        for (part_finish, *_key), (n, offset, polys) in wanted[level.uid].items():
            index = mats.setdefault(part_finish, len(mats))
            start = len(bm.faces)
            _build_plane(bm, part_finish[0], n, offset, polys)
            bm.faces.ensure_lookup_table()
            for f in bm.faces[start:]:
                f.material_index = index
        # Corner boards over the siding's ends
        start = len(bm.faces)
        if _corner_boards(bm, corners.get(level.uid, {})):
            index = mats.setdefault(('TRIM', TRIM_COLOR), len(mats))
            bm.faces.ensure_lookup_table()
            for f in bm.faces[start:]:
                f.material_index = index
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        mesh = bpy.data.meshes.new(f"Siding - {level.name}")
        bm.to_mesh(mesh)
        bm.free()
        for finish, _i in sorted(mats.items(), key=lambda kv: kv[1]):
            mesh.materials.append(trim_material() if finish[0] == 'TRIM'
                                  else siding_material(finish[0], finish[1], True))
        if obj is None:
            obj = bpy.data.objects.new(f"Siding - {level.name}", mesh)
            obj[GEO_KEY] = True
            obj[hb_house.LEVEL_KEY] = level.uid
            hb_house.ensure_level_collections(scene, level)
            hb_house.level_subcollection(level, 'Walls').objects.link(obj)
        else:
            old = obj.data
            obj.data = mesh
            if old is not None and old.users == 0:
                bpy.data.meshes.remove(old)
        obj.color = mesh.materials[0].diffuse_color if mesh.materials else obj.color


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
    """(level, object) for the walls the roofs make: filled-in gable ends
    and dormer walls."""
    for level in scene.hb_house.levels:
        for obj in (level.roof.gables_obj, level.roof.dormer_walls_obj):
            if obj is not None:
                yield level, obj


def _level_of(scene, obj):
    uid = obj.get(hb_house.LEVEL_KEY, '')
    return next((l for l in scene.hb_house.levels if l.uid == uid), None)


def level_finish(scene, level):
    """(style, colour) of a level's outside walls: its own, or the house's."""
    house = scene.hb_house
    if level is not None and level.siding_style != 'INHERIT':
        return level.siding_style, tuple(level.siding_color)
    return house.siding_style, tuple(house.siding_color)


def wall_finish(scene, obj):
    """(style, colour) of an outside wall: its own, its level's or the house's."""
    own = getattr(obj, 'hb_siding', None)
    if own is not None and own.style != 'INHERIT' and obj.get('WALL_TYPE') != 'Dormer':
        return own.style, tuple(own.color)
    return level_finish(scene, _level_of(scene, obj))


def gable_split(scene, level):
    """The height where a level's walls end and its gable ends begin."""
    return level.elevation + hb_house.exterior_wall_height(level)


def gable_finish(scene, level):
    """(style, colour) of the gable ends and roof-made walls over a level."""
    house = scene.hb_house
    if house.gable_siding_style != 'INHERIT':
        return house.gable_siding_style, tuple(house.gable_siding_color)
    return level_finish(scene, level)


def _material_for(finish, built):
    style, color = finish
    return siding_material(style, color, built) if style != 'NONE' else None


def _is_siding(mat):
    return mat is not None and mat.name.startswith(SIDING_MATERIAL)


def apply_exterior_finish(scene):
    """Put the house's siding and base on, or take them off."""
    from . import hb_types
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    house = scene.hb_house
    built = house.siding_geometry
    rooms = _indoor_polygons(scene)
    walls_done = []
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP'):
            continue
        if obj.get('WALL_TYPE', 'Exterior') not in ('Exterior', 'Dormer'):
            continue
        wall = hb_types.GeoNodeWall(obj)
        if not (wall.has_modifier() and wall.has_input(THICK_SIDE)):
            continue
        finish = wall_finish(scene, obj)
        siding = _material_for(finish, built)
        # A gable end: the gables' own siding above the eaves
        level = _level_of(scene, obj)
        gable, split = None, None
        if level is not None and house.gable_siding_style != 'INHERIT':
            split = gable_split(scene, level)
            top = obj.matrix_world.translation.z + (wall.get_input('Height') or 0.0)
            if top > split + 0.05 and gable_finish(scene, level) != finish:
                gable = gable_finish(scene, level)
                siding = split_material(finish, gable, split, built)
        outside = _outside_input(obj, wall, rooms.get(obj.get(hb_house.LEVEL_KEY, ''), []))
        for name in (THICK_SIDE, REF_SIDE, 'Inside Face', 'Outside Face'):
            if not wall.has_input(name):
                continue
            if name == outside:
                wall.set_input(name, siding)
            elif _is_siding(wall.get_input(name)):
                wall.set_input(name, None)
        obj.update_tag()
        walls_done.append((obj, finish, gable, split))
    roof_done = []
    for level, obj in _roof_walls(scene):
        finish = gable_finish(scene, level)
        siding = _material_for(finish, built)
        if siding is not None:
            obj.data.materials.clear()
            obj.data.materials.append(siding)
        roof_done.append((obj, finish, None, None))
    build_siding_geometry(scene, walls_done, roof_done, rooms)

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
