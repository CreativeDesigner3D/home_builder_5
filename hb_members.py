"""Structural members placed by hand: beams and the posts under them.

A member is a mesh object rebuilt from its custom properties, the way
stairs are: what it is (beam or post), what it is made of (sawn lumber,
LVL, glulam, steel), its size and plies, and where it sits. Its level's
Structure collection holds it, so it shows and hides with the level, and
it stays solid while the framing shows.

A beam runs along its object's local +X from its origin, centred across
it, its top at the origin's height. Dropped, it hangs under the ceiling
(its top at the ceiling); Flush, it sits in the ceiling framing (its
bottom at the ceiling). A post stands on the level's floor, centred on
its origin, up to the underside of the beam over it or to the ceiling.

No engineering is done: sizes are what the designer picks. A rough span
guide says when a sawn-lumber beam is long for its depth.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from . import hb_house
from .units import inch

MEMBER_KEY = 'IS_MEMBER'
PART = 'Structure'              # the level sub-collection
MENU_ID = 'HOME_BUILDER_MT_member_commands'

LUMBER_PLY = inch(1.5)          # a sawn board's thickness
LVL_PLY = inch(1.75)
PLY_SEAM = inch(0.03)           # the line between plies
# Nominal lumber: identifier -> actual depth
LUMBER_DEPTHS = {'2X6': inch(5.5), '2X8': inch(7.25), '2X10': inch(9.25),
                 '2X12': inch(11.25)}
# Posts: identifier -> (width, depth)
POST_SIZES = {'4X4': (inch(3.5), inch(3.5)), '4X6': (inch(3.5), inch(5.5)),
              '6X6': (inch(5.5), inch(5.5)), '8X8': (inch(7.25), inch(7.25))}
# A sawn beam much longer than this many times its depth wants a check
SPAN_GUIDE = 18.0

MATERIAL_COLORS = {
    'CONCRETE': ((0.62, 0.62, 0.60), 0.9, 0.0),
    'LUMBER': ((0.78, 0.62, 0.42), 0.85, 0.0),
    'LVL': ((0.83, 0.68, 0.47), 0.6, 0.0),
    'GLULAM': ((0.86, 0.72, 0.52), 0.5, 0.0),
    'STEEL': ((0.35, 0.36, 0.38), 0.45, 0.9),
}


def _material(kind):
    color, rough, metal = MATERIAL_COLORS.get(kind, MATERIAL_COLORS['LUMBER'])
    name = f"Member {kind.title()}"
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (*color, 1.0)
            bsdf.inputs['Roughness'].default_value = rough
            bsdf.inputs['Metallic'].default_value = metal
        mat.diffuse_color = (*color, 1.0)
    return mat


# ---- Sizes ------------------------------------------------------------------

def beam_section(house):
    """(width, depth, plies, label) of the beam the house's member
    settings describe."""
    m = house.member_material
    if m == 'LUMBER':
        plies = max(1, house.member_plies)
        d = LUMBER_DEPTHS.get(house.member_lumber, inch(9.25))
        return plies * LUMBER_PLY, d, plies, f"({plies}) {house.member_lumber.lower()}"
    if m == 'LVL':
        plies = max(1, house.member_plies)
        d = house.member_depth
        return plies * LVL_PLY, d, plies, f"({plies}) 1-3/4\" LVL"
    return house.member_width, house.member_depth, 1, m.title()


def post_section(house):
    """(width, depth) of the post the house's member settings describe."""
    if house.member_material == 'STEEL':
        return house.member_width, house.member_width
    return POST_SIZES.get(house.post_size, POST_SIZES['4X4'])


def span_warning(obj):
    """A note when a sawn-lumber beam is long for its depth, or None."""
    if obj.get('MEMBER_KIND') != 'BEAM' or obj.get('MEMBER_MATERIAL') != 'LUMBER':
        return None
    length, depth = float(obj['MEMBER_LENGTH']), float(obj['MEMBER_D'])
    if length > depth * SPAN_GUIDE:
        return (f"Long for a sawn beam this deep (a rough guide, not a "
                f"calculation): check it or use LVL")
    return None


# ---- The mesh ---------------------------------------------------------------

def _box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])


def rebuild(obj):
    """Remake a member's mesh from its properties."""
    kind = obj.get('MEMBER_KIND', 'BEAM')
    w, d = float(obj['MEMBER_W']), float(obj['MEMBER_D'])
    plies = max(1, int(obj.get('MEMBER_PLIES', 1)))
    bm = bmesh.new()
    if kind in ('POST', 'PIER'):
        h = float(obj['MEMBER_LENGTH'])
        _box(bm, -w / 2.0, w / 2.0, -d / 2.0, d / 2.0, 0.0, h)
    else:
        length = float(obj['MEMBER_LENGTH'])
        ply = w / plies
        for k in range(plies):
            y0 = -w / 2.0 + k * ply
            y1 = y0 + ply - (PLY_SEAM if k < plies - 1 else 0.0)
            _box(bm, 0.0, length, y0, y1, -d, 0.0)
    old = obj.data
    mesh = bpy.data.meshes.new(obj.name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(_material(obj.get('MEMBER_MATERIAL', 'LUMBER')))
    obj.data = mesh
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)


# ---- Members on a level -----------------------------------------------------

def _collection(scene, level):
    hb_house.ensure_level_collections(scene, level)
    col = hb_house.level_subcollection(level, PART)
    if col is None:
        col = bpy.data.collections.new(f"{level.name} - {PART}")
        col['HB_LEVEL_PART'] = PART
        level.collection.children.link(col)
    return col


def members_of(scene, level=None, kind=None):
    return [o for o in scene.objects if o.get(MEMBER_KEY)
            and (level is None or o.get(hb_house.LEVEL_KEY) == level.uid)
            and (kind is None or o.get('MEMBER_KIND') == kind)]


def _new(scene, level, name, kind, material, w, d, plies, length):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    _collection(scene, level).objects.link(obj)
    obj[MEMBER_KEY] = True
    obj[hb_house.LEVEL_KEY] = level.uid
    obj['MENU_ID'] = MENU_ID
    obj['MEMBER_KIND'] = kind
    obj['MEMBER_MATERIAL'] = material
    obj['MEMBER_W'] = float(w)
    obj['MEMBER_D'] = float(d)
    obj['MEMBER_PLIES'] = int(plies)
    obj['MEMBER_LENGTH'] = float(length)
    return obj


def ceiling_at(level, x, y):
    from . import hb_rooms
    return hb_rooms.ceiling_z_at(level, x, y)


def beam_top(level, a, b, position, depth):
    """Height of a beam's top between plan points a and b: at the ceiling
    for a dropped beam, a depth above it for a flush one."""
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    ceiling = ceiling_at(level, *mid)
    return ceiling + depth if position == 'FLUSH' else ceiling


def add_beam(scene, level, a, b, house=None, position=None):
    """A beam from plan point a to b on a level, sized from the house's
    member settings. Returns the object."""
    house = house or scene.hb_house
    position = position or house.beam_position
    w, d, plies, label = beam_section(house)
    a, b = Vector((a[0], a[1], 0.0)), Vector((b[0], b[1], 0.0))
    length = (b - a).length
    if length < 0.01:
        return None
    obj = _new(scene, level, "Beam", 'BEAM', house.member_material, w, d, plies, length)
    obj['MEMBER_POSITION'] = position
    obj['MEMBER_LABEL'] = label
    obj.location = (a.x, a.y, beam_top(level, a, b, position, d))
    obj.rotation_euler = (0.0, 0.0, math.atan2(b.y - a.y, b.x - a.x))
    rebuild(obj)
    refresh_posts(scene, level)
    return obj


def beam_over(scene, level, x, y):
    """The lowest beam over plan point (x, y) on a level, or None."""
    best = None
    for beam in members_of(scene, level, 'BEAM'):
        p = beam.matrix_world.inverted() @ Vector((x, y, beam.location.z))
        w, length = float(beam['MEMBER_W']), float(beam['MEMBER_LENGTH'])
        if -0.01 <= p.x <= length + 0.01 and abs(p.y) <= w / 2.0 + 0.01:
            bottom = beam.location.z - float(beam['MEMBER_D'])
            if best is None or bottom < best[0]:
                best = (bottom, beam)
    return best[1] if best else None


def post_height(scene, level, x, y):
    """From the level's floor to the underside of the beam over (x, y),
    or to the ceiling."""
    beam = beam_over(scene, level, x, y)
    top = (beam.location.z - float(beam['MEMBER_D']) if beam is not None
           else ceiling_at(level, x, y))
    return max(top - level.elevation, 0.1)


def add_post(scene, level, p, house=None):
    """A post at plan point p on a level, up to the beam over it or the
    ceiling. Returns the object."""
    house = house or scene.hb_house
    w, d = post_section(house)
    material = 'STEEL' if house.member_material == 'STEEL' else 'LUMBER'
    obj = _new(scene, level, "Post", 'POST', material, w, d, 1,
               post_height(scene, level, p[0], p[1]))
    obj['MEMBER_LABEL'] = (house.post_size.lower() if material == 'LUMBER'
                           else "Steel column")
    obj.location = (p[0], p[1], level.elevation)
    rebuild(obj)
    return obj


def refresh_posts(scene, level):
    """Posts follow the beams over them."""
    bpy.context.view_layer.update()
    for post in members_of(scene, level, 'POST'):
        h = post_height(scene, level, post.location.x, post.location.y)
        if abs(h - float(post['MEMBER_LENGTH'])) > 1e-5:
            post['MEMBER_LENGTH'] = h
            rebuild(post)


def on_wall(scene, level, p, margin=0.02):
    """Whether plan point p lies within a wall's thickness on a level."""
    from .operators import walls
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    for seg in segs:
        if seg.thickness <= 0.0:
            continue
        rel = (p[0] - seg.start[0], p[1] - seg.start[1])
        along = rel[0] * seg.dir[0] + rel[1] * seg.dir[1]
        off = rel[0] * seg.normal[0] + rel[1] * seg.normal[1]
        if -margin <= along <= seg.length + margin and -margin <= off <= seg.thickness + margin:
            return True
    return False


def add_end_posts(scene, level, beam, house=None):
    """Posts under a beam's ends that don't rest on a wall."""
    house = house or scene.hb_house
    w, _d = post_section(house)
    m = beam.matrix_world
    length = float(beam['MEMBER_LENGTH'])
    posts = []
    for t in (w / 2.0, length - w / 2.0):
        p = (m @ Vector((t, 0.0, 0.0))).to_2d()
        end = (m @ Vector((0.0 if t < length / 2 else length, 0.0, 0.0))).to_2d()
        if on_wall(scene, level, end):
            continue
        posts.append(add_post(scene, level, p, house))
    return posts
