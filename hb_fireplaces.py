"""Fireplaces and their chimneys.

A fireplace is placed on a wall like a window: a GeoNodeCage parented to
the wall, tagged IS_FIREPLACE_BP, whose box IS the firebox's mouth - Dim
X its width, Dim Z its height, its z the hearth's height off the floor.
Its settings are Object.hb_fireplace. Everything else is built from those
as the cage's children and replaced on each rebuild:

- in the room: the firebox's lining (splayed sides), the hearth, the
  surround and the mantel;
- the masonry: an Inside chimney's breast standing in the room up to the
  ceiling, or an Outside chimney's mass standing outside the wall (the
  cage then cuts the wall for the mouth), with a shoulder and a stack;
- the stack rises through the floors above (an Inside one) and the roof,
  to the 3-2-10 rule: 3 ft above where it passes through the roof, and
  2 ft above any roof within 10 ft. The roofs are opened for it by their
  openings cutters (see hb_skylights), and floors and ceilings by a chase
  cutter.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import hb_house, hb_types, hb_utils
from .units import inch

FIREPLACE_KEY = 'IS_FIREPLACE_BP'
PART_KEY = 'IS_FIREPLACE_PART'
CHIMNEY_KEY = 'IS_CHIMNEY'
CHASE_KEY = 'IS_CHIMNEY_CHASE'
BOX_KEY = 'IS_FIREPLACE_BOX'        # the wire box round the whole fireplace
MENU_ID = "HOME_BUILDER_MT_fireplace_commands"
CHASE_CUT = "Chimney - "            # + the fireplace's name, on floors and ceilings

SIDE = inch(16)                     # masonry beside the mouth
BACK = inch(8)                      # and behind the firebox
LINER = inch(2)
SPLAY = inch(4)                     # each side of the firebox narrows this much to its back
SHOULDER_RISE = inch(24)            # an outside mass, above the mouth, before its shoulder
BASE_BELOW = 0.15                   # an outside mass starts this far under the floor
SURROUND_T = inch(1)
MANTEL_GAP = inch(6)                # the shelf, over the surround
CROWN_OVER = inch(2)
CROWN_T = inch(4)
FLUE = inch(8)
CAP_T = inch(1)
CLEARANCE = 0.05                    # the roof opened this much round the stack

CODE_ABOVE = 0.914                  # 3 ft above where it passes through
CODE_NEAR = 3.048                   # any roof within 10 ft
CODE_NEAR_ABOVE = 0.61              # 2 ft above that
SAMPLE = 0.25

FIREBRICK = (0.28, 0.13, 0.09)
HEARTH = (0.42, 0.41, 0.39)
CROWN = (0.62, 0.61, 0.58)
CAP = (0.30, 0.30, 0.31)

# The lists the tool shares with these settings (hb_house's)
CHIMNEY_ITEMS = hb_house.FIREPLACE_CHIMNEY_ITEMS
STYLE_ITEMS = hb_house.FIREPLACE_STYLE_ITEMS
MANTEL_ITEMS = hb_house.FIREPLACE_MANTEL_ITEMS
FINISH_ITEMS = [
    ('BRICK', "Brick", "Brick in running bond"),
    ('STONE', "Stone", "Rough stone"),
]


# ---- The 3-2-10 rule (pure) --------------------------------------------------------

def _rect_distance(rect, x, y):
    x0, y0, x1, y1 = rect
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def chimney_top(rect, samples, ring=0.3):
    """The height a stack over the plan rectangle `rect` (x0, y0, x1, y1)
    must reach, from roof heights `samples` [(x, y, z)] around it: 3 ft
    above the roof where it passes through (the samples just round it),
    and 2 ft above any roof within 10 ft. None with no roof near it."""
    through, near = None, None
    for x, y, z in samples:
        d = _rect_distance(rect, x, y)
        if d <= ring:
            through = z if through is None else max(through, z)
        if d <= CODE_NEAR:
            near = z if near is None else max(near, z)
    tops = []
    if through is not None:
        tops.append(through + CODE_ABOVE)
    if near is not None:
        tops.append(near + CODE_NEAR_ABOVE)
    return max(tops) if tops else None


def roof_samples(tree, rect, skip):
    """Roof heights on a grid round a plan rectangle, out to 10 ft, from
    rays down into `tree` - leaving out the `skip` rectangle (the stack's
    own opening)."""
    x0, y0, x1, y1 = rect
    out = []
    nx = int((x1 - x0 + 2 * CODE_NEAR) / SAMPLE) + 1
    ny = int((y1 - y0 + 2 * CODE_NEAR) / SAMPLE) + 1
    down = Vector((0.0, 0.0, -1.0))
    for i in range(nx + 1):
        x = x0 - CODE_NEAR + i * SAMPLE
        for j in range(ny + 1):
            y = y0 - CODE_NEAR + j * SAMPLE
            if _rect_distance(skip, x, y) <= 0.0:
                continue
            if _rect_distance(rect, x, y) > CODE_NEAR:
                continue
            hit = tree.ray_cast(Vector((x, y, 1000.0)), down)
            if hit[0] is not None:
                out.append((x, y, hit[0].z))
    return out


# ---- Where it is ---------------------------------------------------------------------

def is_fireplace(obj):
    return obj is not None and bool(obj.get(FIREPLACE_KEY))


def fireplace_of(obj):
    """The fireplace an object is, or is part of; None for anything else."""
    while obj is not None:
        if is_fireplace(obj):
            return obj
        obj = obj.parent
    return None


def _cage_matrix(cage):
    """The cage's world matrix, good on a cage made a moment ago."""
    if cage.parent is not None:
        return cage.parent.matrix_world @ cage.matrix_parent_inverse @ cage.matrix_basis
    return cage.matrix_basis.copy()


def room_side(cage):
    """+1 when the room is on the wall's thickness side (y = T), -1 when
    it is on its reference side (y = 0)."""
    from . import hb_exterior
    wall = cage.parent
    side = hb_exterior.outdoor_side(wall) if wall is not None else None
    if side == 'REF':
        return 1
    if side == 'FAR':
        return -1
    # An inside wall: the side with a room, if there is one
    scene = hb_house.house_scene_of(bpy.context.scene)
    if scene is not None and wall is not None:
        rooms = hb_exterior._indoor_polygons(scene).get(wall.get(hb_house.LEVEL_KEY, ''), [])
        from . import hb_wall_graph
        m = _cage_matrix(cage)
        t = hb_types.GeoNodeCage(cage).get_input('Dim Y')
        w = hb_types.GeoNodeCage(cage).get_input('Dim X')
        for s, y in ((1, t + 0.3), (-1, -0.3)):
            p = m @ Vector((w / 2.0, y, 0.0))
            if any(hb_wall_graph.point_in_polygon((p.x, p.y), r) for r in rooms):
                return s
    return -1


def _level(cage):
    wall = cage.parent
    uid = wall.get(hb_house.LEVEL_KEY, '') if wall is not None else ''
    return hb_house.get_level(uid) if uid else None


def chimney_kind(cage):
    """'OUTSIDE', 'INSIDE' or 'NONE' - an Outside chimney only on an
    outside wall of a house."""
    from . import hb_exterior
    kind = cage.hb_fireplace.chimney
    if kind == 'OUTSIDE' and (cage.parent is None or hb_exterior.outdoor_side(cage.parent) is None):
        return 'INSIDE' if hb_house.house_scene_of(bpy.context.scene) is not None else 'NONE'
    if hb_house.house_scene_of(bpy.context.scene) is None and kind == 'INSIDE':
        return 'NONE'
    return kind


# ---- Building ---------------------------------------------------------------------------

class _Parts:
    """Boxes and prisms in the fireplace's own terms: x along the wall
    from the mouth's left, d out from the wall's room face into the room
    (negative: into the wall and outside), z up from the hearth."""

    def __init__(self, face, s):
        self.bm = bmesh.new()
        self.face, self.s = face, s

    def _y(self, d):
        return self.face + self.s * d

    def box(self, x0, x1, d0, d1, z0, z1, mat=0):
        y0, y1 = sorted((self._y(d0), self._y(d1)))
        if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6 or z1 - z0 <= 1e-6:
            return
        vs = [self.bm.verts.new(p) for p in
              ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
               (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.bm.faces.new([vs[i] for i in f]).material_index = mat

    def solid(self, bottom, z0, top, z1, mat=0):
        """A solid from one plan polygon [(x, d)] at z0 to another with as
        many corners at z1: an upright prism, or a shoulder's taper."""
        if z1 - z0 <= 1e-6:
            return
        b = [self.bm.verts.new((x, self._y(d), z0)) for x, d in bottom]
        t = [self.bm.verts.new((x, self._y(d), z1)) for x, d in top]
        n = len(b)
        self.bm.faces.new(b).material_index = mat
        self.bm.faces.new(t).material_index = mat
        for i in range(n):
            j = (i + 1) % n
            self.bm.faces.new((b[i], b[j], t[j], t[i])).material_index = mat

    def mesh(self, name, materials):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for mat in materials:
            mesh.materials.append(mat)
        return mesh


def _rect(x0, x1, d0, d1):
    return [(x0, d0), (x1, d0), (x1, d1), (x0, d1)]


def _material(name, color, roughness=0.7):
    from .product_libraries.common import door_window_geo
    return door_window_geo._material(name, color, roughness)


def _masonry(cage):
    from . import hb_exterior
    fp = cage.hb_fireplace
    return hb_exterior.siding_material(fp.finish, tuple(fp.color), False)


def _chase_material(cage):
    from . import hb_exterior
    scene = hb_house.house_scene_of(bpy.context.scene)
    level = _level(cage)
    if scene is not None:
        style, color = hb_exterior.level_finish(scene, level)
        if style != 'NONE':
            return hb_exterior.siding_material(style, color, False)
    return hb_exterior.trim_material()


def _clear(cage):
    for child in list(cage.children):
        if child.get(PART_KEY):
            mesh = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)


def _child(cage, name, mesh, tag):
    obj = hb_utils.new_object(name, mesh)
    for coll in (cage.users_collection or [bpy.context.scene.collection]):
        coll.objects.link(obj)
    obj.parent = cage
    obj[PART_KEY] = True
    obj[tag] = True
    if cage.get('MENU_ID'):
        obj['MENU_ID'] = cage['MENU_ID']
    lv = cage.parent.get(hb_house.LEVEL_KEY) if cage.parent is not None else None
    if lv:
        obj[hb_house.LEVEL_KEY] = lv
    return obj


def layout(cage):
    """The numbers everything is built from (see _Parts for the terms)."""
    fp = cage.hb_fireplace
    c = hb_types.GeoNodeCage(cage)
    W, T, Hm = c.get_input('Dim X'), c.get_input('Dim Y'), c.get_input('Dim Z')
    s = room_side(cage)
    kind = chimney_kind(cage)
    hz = cage.location.z
    level = _level(cage)
    ceiling = (level.ceiling_height if level is not None else 2.44) - hz
    fd = fp.firebox_depth
    out = {'W': W, 'T': T, 'Hm': Hm, 's': s, 'face': T if s > 0 else 0.0, 'kind': kind,
           'hz': hz, 'ceiling': ceiling}
    if kind == 'OUTSIDE':
        fd = max(fd, T + inch(4))
        depth = fd + BACK
        out.update(front=0.0, back=-fd, mass=(-depth, -T), z_mass=(-hz - BASE_BELOW, Hm + SHOULDER_RISE))
        sd = min(fp.stack_depth, depth - T)
        out['stack'] = (-T - sd, -T)
    else:
        depth = fd + BACK
        out.update(front=depth, back=BACK, mass=(0.0, depth), z_mass=(-hz, ceiling))
        out['stack'] = (0.0, min(fp.stack_depth, depth))
    sw = min(fp.stack_width, W + 2 * SIDE)
    out['stack_x'] = (W / 2.0 - sw / 2.0, W / 2.0 + sw / 2.0)
    out['fd'] = fd
    return out


def stack_rect_world(cage, L=None, grow=0.0):
    """The stack's plan rectangle in world XY (x0, y0, x1, y1), grown by
    `grow`; None when it has no stack."""
    L = L or layout(cage)
    if L['kind'] == 'NONE':
        return None
    m = _cage_matrix(cage)
    (x0, x1), (d0, d1) = L['stack_x'], L['stack']
    pts = [m @ Vector((x, L['face'] + L['s'] * d, 0.0)) for x in (x0, x1) for d in (d0, d1)]
    return (min(p.x for p in pts) - grow, min(p.y for p in pts) - grow,
            max(p.x for p in pts) + grow, max(p.y for p in pts) + grow)


def chimney_height(scene, cage, L=None):
    """The stack's top in world z: by the 3-2-10 rule from the roofs
    round it, plus the fireplace's extra height."""
    from . import hb_roofs
    L = L or layout(cage)
    rect = stack_rect_world(cage, L)
    m = _cage_matrix(cage)
    base = m.translation.z
    floor_top = base + L['z_mass'][1]
    if rect is None:
        return None
    top = None
    tree = hb_roofs.roof_bvh(scene) if scene is not None else None
    if tree is not None:
        grow = CLEARANCE + 0.02
        skip = (rect[0] - grow, rect[1] - grow, rect[2] + grow, rect[3] + grow)
        top = chimney_top(rect, roof_samples(tree, rect, skip), ring=0.3)
    if top is None:
        # No roof near it: clear of the highest level's walls
        house = scene.hb_house if scene is not None else None
        tops = [l.elevation + hb_house.exterior_wall_height(l) for l in house.levels] if house else []
        top = max(tops + [floor_top]) + CODE_ABOVE
    return max(top, floor_top + 0.5) + cage.hb_fireplace.extra_height


def build(cage):
    """Rebuild a fireplace's parts and chimney from its settings."""
    if not is_fireplace(cage):
        return
    _clear(cage)
    c = hb_types.GeoNodeCage(cage)
    if not c.has_modifier():
        return
    fp = cage.hb_fireplace
    L = layout(cage)
    W, Hm, hz = L['W'], L['Hm'], L['hz']
    front, back = L['front'], L['back']
    sgn = 1.0 if back < front else -1.0     # from the back toward the front

    # The room's parts: lining, hearth, surround, mantel
    P = _Parts(L['face'], L['s'])
    P.box(SPLAY, W - SPLAY, back, back + sgn * LINER, 0.0, Hm, 1)
    P.solid([(0.0, front), (0.0, back), (SPLAY, back)], 0.0,
            [(0.0, front), (0.0, back), (SPLAY, back)], Hm, 1)
    P.solid([(W, front), (W, back), (W - SPLAY, back)], 0.0,
            [(W, front), (W, back), (W - SPLAY, back)], Hm, 1)
    P.box(0.0, W, back, front, 0.0, 0.01, 1)
    he = fp.hearth_extension
    z_top = max(0.0, 0.02 - hz)
    P.box(-he, W + he, front, front + fp.hearth_depth, -hz, z_top, 3)
    sw = fp.surround_width
    if sw > 0.0:
        P.box(-sw, 0.0, front, front + SURROUND_T, 0.0, Hm, 0)
        P.box(W, W + sw, front, front + SURROUND_T, 0.0, Hm, 0)
        P.box(-sw, W + sw, front, front + SURROUND_T, Hm, Hm + sw, 0)
    shelf = Hm + sw + MANTEL_GAP
    if fp.mantel in ('SHELF', 'FULL'):
        reach = sw + (inch(6) if fp.mantel == 'FULL' else inch(4))
        P.box(-reach, W + reach, front, front + inch(9), shelf, shelf + inch(2), 2)
    if fp.mantel == 'FULL':
        pw = inch(5)
        P.box(-sw - pw, -sw, front, front + inch(3), -hz, shelf, 2)
        P.box(W + sw, W + sw + pw, front, front + inch(3), -hz, shelf, 2)
        P.box(-sw - pw, W + sw + pw, front, front + inch(2), Hm + sw, shelf, 2)
    from .product_libraries.common import door_window_geo
    room = P.mesh("Fireplace", [_masonry(cage), _material("HB Firebrick", FIREBRICK),
                                door_window_geo._trim_material(), _material("HB Hearth", HEARTH)])
    room_obj = _child(cage, f"{cage.name} Parts", room, 'IS_FIREPLACE_ROOM')

    # The masonry: breast or outside mass, shoulder and stack
    scene = hb_house.house_scene_of(bpy.context.scene)
    mat = _chase_material(cage) if fp.style == 'CHASE' else _masonry(cage)
    C = _Parts(L['face'], L['s'])
    m0, m1 = L['mass']
    z0, z_s = L['z_mass']
    x0, x1 = -SIDE, W + SIDE
    for a, b in ((x0, 0.0), (W, x1)):
        C.box(a, b, m0, m1, z0, z_s)
    C.box(0.0, W, m0, m1, Hm, z_s)
    if L['kind'] == 'OUTSIDE':
        C.box(0.0, W, m0, -L['fd'], 0.0, Hm)
        C.box(0.0, W, m0, m1, z0, 0.0)
    else:
        C.box(0.0, W, m0, back, 0.0, Hm)
        if hz > 1e-3:
            C.box(0.0, W, m0, m1, z0, 0.0)
    top_world = None
    if L['kind'] != 'NONE' and scene is not None:
        sx0, sx1 = L['stack_x']
        sd0, sd1 = L['stack']
        if L['kind'] == 'OUTSIDE':
            rise = max(sx0 - x0, x1 - sx1, abs((m1 - m0) - (sd1 - sd0)), 0.0)
            C.solid(_rect(x0, x1, m0, m1), z_s, _rect(sx0, sx1, sd0, sd1), z_s + rise)
            z_stack = z_s + rise
        else:
            z_stack = z_s
        base = _cage_matrix(cage).translation.z
        top_world = chimney_height(scene, cage, L)
        z_top = top_world - base
        C.box(sx0, sx1, sd0, sd1, z_stack, z_top)
        # Crown and flue, or the chase's cap
        mats = [mat]
        if fp.style == 'MASONRY':
            C.box(sx0 - CROWN_OVER, sx1 + CROWN_OVER, sd0 - CROWN_OVER, sd1 + CROWN_OVER,
                  z_top, z_top + CROWN_T, 1)
            fx, fdd = (sx0 + sx1) / 2.0, (sd0 + sd1) / 2.0
            C.box(fx - FLUE / 2, fx + FLUE / 2, fdd - FLUE / 2, fdd + FLUE / 2,
                  z_top + CROWN_T, z_top + CROWN_T + inch(6), 2)
            mats += [_material("HB Chimney Crown", CROWN), _material("HB Flue", (0.45, 0.25, 0.18))]
        else:
            C.box(sx0 - CAP_T, sx1 + CAP_T, sd0 - CAP_T, sd1 + CAP_T, z_top, z_top + CAP_T, 1)
            mats += [_material("HB Chimney Cap", CAP, roughness=0.35)]
    else:
        mats = [mat]
    chimney = _child(cage, f"Chimney - {cage.name}", C.mesh("Chimney", mats), CHIMNEY_KEY)
    _box(cage, [room_obj, chimney], z_s)
    cage['HB_CHIMNEY_TOP'] = top_world if top_world is not None else 0.0
    _chase_cutter(cage, L, top_world)
    _wall_cut(cage, L['kind'] == 'OUTSIDE')


def _box(cage, parts, z_top):
    """A wire box round the whole fireplace below `z_top` (the stack
    above left out): what a click on any of it selects, so its outline is
    the fireplace's, where the cage is only the firebox's mouth."""
    pts = [v.co for obj in parts if obj is not None and obj.type == 'MESH'
           for v in obj.data.vertices if v.co.z <= z_top + 1e-4]
    if not pts:
        return None
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    corners = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    mesh = bpy.data.meshes.new("Fireplace Box")
    mesh.from_pydata(corners, edges, [])
    obj = _child(cage, f"{cage.name} Box", mesh, BOX_KEY)
    obj.display_type = 'WIRE'
    obj.hide_render = True
    obj.color = cage.color
    # Moved by itself it would leave the fireplace behind
    obj.lock_location = obj.lock_rotation = obj.lock_scale = (True, True, True)
    return obj


def box_of(obj):
    """The wire box of the fireplace an object is part of, or None."""
    cage = fireplace_of(obj)
    if cage is None:
        return None
    return next((c for c in cage.children if c.get(BOX_KEY)), None)


def _wall_cut(cage, on):
    """An Outside chimney's mouth goes through the wall; an Inside one
    stands in front of it."""
    from .operators import doors_windows
    wall = cage.parent
    if wall is None:
        return
    name = f"Boolean_{cage.name}"
    mod = wall.modifiers.get(name)
    if on and mod is None:
        doors_windows.cut_wall(wall, cage)
    elif not on and mod is not None:
        wall.modifiers.remove(mod)
    cage.hide_render = True


def _chase_cutter(cage, L, top_world):
    """An Inside chimney's stack opens the ceiling it rises from and the
    floors and ceilings above: a box over it, a child of the fireplace."""
    old = next((c for c in cage.children if c.get(CHASE_KEY)), None)
    if L['kind'] != 'INSIDE' or top_world is None:
        if old is not None:
            mesh = old.data
            bpy.data.objects.remove(old, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        return
    P = _Parts(L['face'], L['s'])
    sx0, sx1 = L['stack_x']
    d0, d1 = L['stack']
    g = 0.02
    base = _cage_matrix(cage).translation.z
    P.box(sx0 - g, sx1 + g, d0 - g, d1 + g, L['ceiling'] - 0.1, top_world - base + 0.1)
    mesh = P.mesh("Chimney Chase", [])
    if old is None:
        old = hb_utils.new_object(f"Chimney Chase - {cage.name}", mesh)
        for coll in (cage.users_collection or [bpy.context.scene.collection]):
            coll.objects.link(old)
        old.parent = cage
        old[CHASE_KEY] = True
        old['IS_CUTTING_OBJ'] = True
        old.display_type = 'WIRE'
        old.hide_render = True
    else:
        prev = old.data
        old.data = mesh
        if prev.users == 0:
            bpy.data.meshes.remove(prev)
    old.hide_viewport = True


def fireplaces(scene):
    return [o for o in scene.objects if o.get(FIREPLACE_KEY)]


def roof_cut_rects(scene):
    """The plan rectangles the roofs are opened by for chimneys, in world XY."""
    out = []
    for cage in fireplaces(scene):
        rect = stack_rect_world(cage, grow=CLEARANCE)
        if rect is not None:
            out.append(rect)
    return out


def apply_chase_cuts(scene):
    """Open the floors and ceilings an Inside chimney's stack rises
    through; take cuts off those it no longer does."""
    from . import hb_rooms, hb_roofs
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    wanted = {}
    for cage in fireplaces(scene):
        chase = next((c for c in cage.children if c.get(CHASE_KEY)), None)
        level = _level(cage)
        if chase is None or level is None:
            continue
        rect = stack_rect_world(cage)
        top = cage.get('HB_CHIMNEY_TOP', 0.0)
        for lv in scene.hb_house.levels:
            if lv.elevation < level.elevation - 1e-3 or lv.elevation > top:
                continue
            for room in lv.rooms:
                poly = hb_rooms.room_polygon(scene, lv, room) if not room.orphaned else None
                if not poly:
                    continue
                xs, ys = [p[0] for p in poly], [p[1] for p in poly]
                if max(xs) < rect[0] or min(xs) > rect[2] or max(ys) < rect[1] or min(ys) > rect[3]:
                    continue
                hosts = [room.ceiling_obj]
                if lv.uid != level.uid:
                    hosts.append(room.floor_obj)
                for host in hosts:
                    if host is not None:
                        wanted.setdefault(host, {})[CHASE_CUT + cage.name] = chase
    for level in scene.hb_house.levels:
        for room in level.rooms:
            for obj in (room.floor_obj, room.ceiling_obj):
                if obj is None:
                    continue
                keep = wanted.get(obj, {})
                for mod in list(obj.modifiers):
                    if mod.type == 'BOOLEAN' and mod.name.startswith(CHASE_CUT) and mod.name not in keep:
                        obj.modifiers.remove(mod)
                for name, cutter in keep.items():
                    hb_roofs._set_boolean(obj, name, cutter, True)


def refresh(scene):
    """Every fireplace built again - chimneys to the roofs as they are now."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    cages = fireplaces(scene)
    if not cages:
        apply_chase_cuts(scene)
        return
    bpy.context.view_layer.update()
    for cage in cages:
        build(cage)
    apply_chase_cuts(scene)


def changed(cage):
    """A fireplace's settings changed: rebuild it, open the roofs for it
    where its stack now is, and set its height to them."""
    scene = hb_house.house_scene_of(bpy.context.scene)
    build(cage)
    if scene is not None:
        from . import hb_skylights
        for level in scene.hb_house.levels:
            if level.roof.enabled and level.roof.roof_obj is not None:
                hb_skylights.rebuild(scene, level)
        refresh(scene)


def place(context, cage):
    """A fireplace just dropped on a wall: it takes the tool's settings."""
    house = context.scene.hb_house
    cage[FIREPLACE_KEY] = True
    cage['MENU_ID'] = MENU_ID
    fp = cage.hb_fireplace
    fp['chimney'] = [i[0] for i in CHIMNEY_ITEMS].index(house.fireplace_chimney)
    fp['style'] = [i[0] for i in STYLE_ITEMS].index(house.fireplace_style)
    fp['mantel'] = [i[0] for i in MANTEL_ITEMS].index(house.fireplace_mantel)
    changed(cage)


def delete(cage):
    """Take a fireplace out: its parts, its wall cut, its roof openings."""
    wall = cage.parent
    if wall is not None:
        mod = wall.modifiers.get(f"Boolean_{cage.name}")
        if mod is not None:
            wall.modifiers.remove(mod)
    for child in list(cage.children_recursive):
        mesh = child.data if child.type == 'MESH' else None
        bpy.data.objects.remove(child, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    mesh = cage.data
    bpy.data.objects.remove(cage, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    scene = hb_house.house_scene_of(bpy.context.scene)
    if scene is not None:
        from . import hb_skylights
        for level in scene.hb_house.levels:
            if level.roof.enabled and level.roof.roof_obj is not None:
                hb_skylights.rebuild(scene, level)
        apply_chase_cuts(scene)


# ---- Settings ------------------------------------------------------------------------

def _settings_changed(self, context):
    changed(self.id_data)


def _cage_input(name):
    def get(self):
        c = hb_types.GeoNodeCage(self.id_data)
        return c.get_input(name) if c.has_modifier() else 0.0

    def set(self, value):
        hb_types.GeoNodeCage(self.id_data).set_input(name, value)
        changed(self.id_data)
    return get, set


def _get_hearth(self):
    return self.id_data.location.z


def _set_hearth(self, value):
    self.id_data.location.z = value
    changed(self.id_data)


_width = _cage_input('Dim X')
_height = _cage_input('Dim Z')


class HB_Fireplace(bpy.types.PropertyGroup):
    """A fireplace's settings (see hb_fireplaces)."""
    opening_width: bpy.props.FloatProperty(
        name="Opening Width", min=inch(18), max=inch(96), subtype='DISTANCE', precision=4,
        get=_width[0], set=_width[1])  # type: ignore
    opening_height: bpy.props.FloatProperty(
        name="Opening Height", min=inch(16), max=inch(60), subtype='DISTANCE', precision=4,
        get=_height[0], set=_height[1])  # type: ignore
    hearth_height: bpy.props.FloatProperty(
        name="Hearth Height", description="The hearth's top, above the floor",
        min=0.0, max=inch(36), subtype='DISTANCE', precision=4,
        get=_get_hearth, set=_set_hearth)  # type: ignore
    chimney: bpy.props.EnumProperty(name="Chimney", items=CHIMNEY_ITEMS, default='OUTSIDE',
                                    update=_settings_changed)  # type: ignore
    style: bpy.props.EnumProperty(name="Chimney Style", items=STYLE_ITEMS, default='MASONRY',
                                  update=_settings_changed)  # type: ignore
    finish: bpy.props.EnumProperty(name="Masonry", items=FINISH_ITEMS, default='BRICK',
                                   update=_settings_changed)  # type: ignore
    color: bpy.props.FloatVectorProperty(
        name="Masonry Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.55, 0.27, 0.20), update=_settings_changed)  # type: ignore
    mantel: bpy.props.EnumProperty(name="Mantel", items=MANTEL_ITEMS, default='SHELF',
                                   update=_settings_changed)  # type: ignore
    firebox_depth: bpy.props.FloatProperty(
        name="Firebox Depth", default=inch(20), min=inch(12), max=inch(36),
        subtype='DISTANCE', precision=4, update=_settings_changed)  # type: ignore
    hearth_depth: bpy.props.FloatProperty(
        name="Hearth Depth", description="How far the hearth runs out into the room",
        default=inch(20), min=inch(8), max=inch(48), subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore
    hearth_extension: bpy.props.FloatProperty(
        name="Hearth Extension", description="How far the hearth runs past each side of the opening",
        default=inch(12), min=0.0, max=inch(36), subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore
    surround_width: bpy.props.FloatProperty(
        name="Surround Width", default=inch(8), min=0.0, max=inch(24),
        subtype='DISTANCE', precision=4, update=_settings_changed)  # type: ignore
    stack_width: bpy.props.FloatProperty(
        name="Stack Width", default=inch(24), min=inch(12), max=inch(72),
        subtype='DISTANCE', precision=4, update=_settings_changed)  # type: ignore
    stack_depth: bpy.props.FloatProperty(
        name="Stack Depth", default=inch(20), min=inch(12), max=inch(48),
        subtype='DISTANCE', precision=4, update=_settings_changed)  # type: ignore
    extra_height: bpy.props.FloatProperty(
        name="Extra Height", description="Above the height the 3-2-10 rule sets",
        default=0.0, min=0.0, max=3.0, subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore


# ---- Operators ------------------------------------------------------------------------

class HOME_BUILDER_OT_delete_fireplace(bpy.types.Operator):
    bl_idname = "home_builder.delete_fireplace"
    bl_label = "Delete Fireplace"
    bl_description = "Delete the fireplace and its chimney"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return fireplace_of(context.active_object) is not None

    def execute(self, context):
        delete(fireplace_of(context.active_object))
        return {'FINISHED'}


class HOME_BUILDER_MT_fireplace_commands(bpy.types.Menu):
    bl_label = "Fireplace"
    bl_idname = MENU_ID

    def draw(self, context):
        self.layout.operator("home_builder.delete_fireplace", icon='X')


classes = (
    HB_Fireplace,
    HOME_BUILDER_OT_delete_fireplace,
    HOME_BUILDER_MT_fireplace_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_fireplace = bpy.props.PointerProperty(type=HB_Fireplace)


def unregister():
    if hasattr(bpy.types.Object, 'hb_fireplace'):
        del bpy.types.Object.hb_fireplace
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
