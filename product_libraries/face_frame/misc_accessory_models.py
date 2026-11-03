"""3D models for drawer, board, door-mounted and roll-out accessories.

Three families, all procedural (one derived mesh per unit, role
ACCESSORY_MODEL, never a CABINET_PART, so cut lists and machining
leave them alone; each unit keeps its own materials):

Drawer accessories, built inside the drawer box from a render hint on
the product entry (see types_face_frame.DRAWER_INSERT_BUILDERS, which
this module extends through DRAWER_INSERT_KINDS). A kind that takes
drawer floor is packed left to right like the other inserts at its own
published size; the rest span the box (a mat on the floor, a peg board,
an upper sliding tray, file rails ...) and can be combined freely:
dish pegs and racks stand on a peg board when the drawer has one.

Opening units, named by an entry's ``model`` (registered with
accessory_models, which hands these models to this module):

    pullout_board       bread / writing board in the top rail slot
    butcher_block       roll-out butcher block under the top rail
    keyboard_rollout    keyboard platform (``deluxe`` for the black unit)
    tv_swivel           swivel deck on its mechanism at the opening floor
    swing_rack          double-sided spice rack hinged at the opening
                        edge opposite the door hinge
    swinger_pantry      two swing-out racks behind a pair of doors (the
                        door racks are built on the doors, see below)

Front-mounted units ride the front so they swing with it: door racks
(``door_rack``) on the back of each door leaf and the swinger pantry's
door racks, and the tray on the back of a tilt-out front
(``tilt_tray``). attach_front_models builds them under the front pivot;
in the opening itself they build nothing.

Every unit keeps its catalog size and is centered in the face frame
opening, never stretched to fill it; anything larger than the opening
is clipped.
"""

import math
from functools import partial

import bpy
import bmesh

from ... import hb_utils
from . import accessory_materials
from ...units import inch

ROLE = 'ACCESSORY_MODEL'
FINISH_MATCH_KEY = 'hb_accessory_finish_match'
TAG_OPENING_CAGE = 'IS_FACE_FRAME_OPENING_CAGE'
I = inch(1.0)

# ---------------------------------------------------------------------------
# Materials: slot keys. FINISH is the cabinet's exterior finish (the
# material walk swaps it in when the object is stamped FINISH_MATCH_KEY).
# ---------------------------------------------------------------------------
FINISH, MAPLE, BIRCH, CHROME, STEEL, CLEAR, BLACK, GRAY, RUBBER, \
    POLYMER, WHITE, SMOKED = range(12)

_SHARED = {MAPLE: 'MAPLE', BIRCH: 'BIRCH', CHROME: 'CHROME', STEEL: 'STEEL',
           CLEAR: 'CLEAR_PLASTIC', POLYMER: 'POLYMER', FINISH: 'MAPLE'}
_PLAIN = {
    BLACK:  ("Accessory Black", (0.03, 0.03, 0.035, 1.0), 0.0, 0.5, 0.0),
    GRAY:   ("Accessory Gray Vinyl", (0.42, 0.43, 0.44, 1.0), 0.0, 0.6, 0.0),
    RUBBER: ("Accessory Non-Slip Mat", (0.16, 0.16, 0.17, 1.0), 0.0, 0.9,
             0.0),
    WHITE:  ("Accessory White Plastic", (0.92, 0.92, 0.90, 1.0), 0.0, 0.4,
             0.0),
    SMOKED: ("Accessory Smoked Acrylic", (0.30, 0.28, 0.26, 1.0), 0.0, 0.1,
             0.6),
}


def _material(key):
    shared = _SHARED.get(key)
    if shared is not None:
        mat = accessory_materials.get(shared)
        if mat is not None:
            return mat
    name, color, metallic, rough, trans = _PLAIN.get(
        key, ("Accessory Plain", (0.8, 0.8, 0.8, 1.0), 0.0, 0.5, 0.0))
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = accessory_materials._plain(name, color, metallic, rough, trans)
    return mat


# ---------------------------------------------------------------------------
# Mesh collector
# ---------------------------------------------------------------------------

class _Mesh:
    """bmesh with axis-aligned boxes, prisms and cylinders, each face
    tagged with a material key (remapped to slots on output)."""

    def __init__(self):
        self.bm = bmesh.new()

    def box(self, x0, x1, y0, y1, z0, z1, mi):
        if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6 or z1 - z0 <= 1e-6:
            return
        bm = self.bm
        v = [bm.verts.new((x, y, z)) for z in (z0, z1)
             for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                  (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            bm.faces.new([v[i] for i in f]).material_index = mi

    def prism(self, poly, axis, a0, a1, mi):
        """Closed outline extruded along axis: (y, z) for 'X', (x, z)
        for 'Y', (x, y) for 'Z'."""
        if a1 - a0 <= 1e-6 or len(poly) < 3:
            return

        def pt(u, v, a):
            if axis == 'X':
                return (a, u, v)
            if axis == 'Y':
                return (u, a, v)
            return (u, v, a)
        bm = self.bm
        lo = [bm.verts.new(pt(u, v, a0)) for u, v in poly]
        hi = [bm.verts.new(pt(u, v, a1)) for u, v in poly]
        n = len(poly)
        bm.faces.new(list(reversed(lo))).material_index = mi
        bm.faces.new(hi).material_index = mi
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i])).material_index = mi

    def cyl(self, cx, cy, r, z0, z1, mi, seg=12, axis='Z'):
        """Cylinder; for axis 'X' / 'Y', (cx, cy) is the section center
        in that axis's prism plane and z0..z1 the run along the axis."""
        poly = [(cx + r * math.cos(2 * math.pi * i / seg),
                 cy + r * math.sin(2 * math.pi * i / seg))
                for i in range(seg)]
        self.prism(poly, axis, z0, z1, mi)

    def rod(self, x0, x1, y0, y1, z0, z1, t, mi=CHROME):
        """Square rod between two points that differ along one axis."""
        h = t / 2.0
        if abs(x1 - x0) > 1e-6:
            self.box(min(x0, x1), max(x0, x1), y0 - h, y0 + h, z0 - h,
                     z0 + h, mi)
        elif abs(y1 - y0) > 1e-6:
            self.box(x0 - h, x0 + h, min(y0, y1), max(y0, y1), z0 - h,
                     z0 + h, mi)
        else:
            self.box(x0 - h, x0 + h, y0 - h, y0 + h, min(z0, z1),
                     max(z0, z1), mi)

    def rotate_z(self, angle, cx, cy):
        if abs(angle) < 1e-9:
            return
        from mathutils import Matrix, Vector
        bmesh.ops.rotate(self.bm, verts=self.bm.verts[:],
                         cent=Vector((cx, cy, 0.0)),
                         matrix=Matrix.Rotation(angle, 3, 'Z'))

    def to_object(self, name, finish_match=False):
        bm = self.bm
        if not bm.faces:
            bm.free()
            return None
        used = sorted({f.material_index for f in bm.faces})
        remap = {k: i for i, k in enumerate(used)}
        for f in bm.faces:
            f.material_index = remap[f.material_index]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        for k in used:
            mesh.materials.append(_material(k))
        obj = hb_utils.new_object(name, mesh)
        if finish_match and used and used[0] == FINISH:
            obj[FINISH_MATCH_KEY] = True
        return obj


def _spread(a, b, n):
    if n <= 0:
        return []
    step = (b - a) / n
    return [a + step * (i + 0.5) for i in range(n)]


def _levels(z0, z1, pitch):
    out = []
    z = z0 + pitch
    while z < z1 - inch(1.5):
        out.append(z)
        z += pitch
    return out


# ---------------------------------------------------------------------------
# Drawer accessories
# ---------------------------------------------------------------------------
# kind -> (builder name, default height in inches, takes drawer floor).
# Merged into types_face_frame.DRAWER_INSERT_BUILDERS; the builder name
# carries the 'misc:' prefix so the drawer code resolves it here.
DRAWER_INSERT_KINDS = {
    'BREAD_BOARD_DRAWER': ('misc:bread_board_drawer', 0.0, False),
    'BREAD_LID':          ('misc:bread_lid', 0.0, False),
    'PASTA_DIVIDER':      ('misc:pasta_divider', 0.0, False),
    'FILE_RAILS':         ('misc:file_rails', 0.0, False),
    'DRYING_RACK':        ('misc:drying_rack', 0.0, False),
    'DOCKING':            ('misc:docking', 0.0, False),
    'GROOMING':           ('misc:grooming', 0.0, False),
    'IRONING_BOARD':      ('misc:ironing_board', 0.0, False),
    'PEG_BOARD':          ('misc:peg_board', 0.0, False),
    'DISH_PEGS':          ('misc:dish_pegs', 0.0, False),
    'TRAY_DIVIDERS':      ('misc:tray_dividers', 0.0, False),
    'PENCIL_SCOOP':       ('misc:pencil_scoop', 0.0, False),
    'DOUBLE_TIER':        ('misc:double_tier', 0.0, False),
    'MAT':                ('misc:mat', 0.0, False),
    'ROLL_DISPENSER':     ('misc:roll_dispenser', 2.25, True),
    'CONTAINER_HOLDER':   ('misc:container_holder', 1.9375, True),
    'LID_RACK':           ('misc:lid_rack', 5.5, True),
    'POT_RACK':           ('misc:pot_rack', 7.0, True),
    'CANISTER_RACK':      ('misc:canister_rack', 7.0, True),
}

PEG_BOARD_T = inch(0.5)
MAT_T = inch(0.125)


def _kind_of(item):
    hint = (getattr(item, 'accessory_render', '') or '').split()
    return hint[0].upper() if hint else ''


def _drawer_items(box_obj):
    """ACCESSORY items of the drawer the box belongs to."""
    node = box_obj.parent
    while node is not None and not node.get(TAG_OPENING_CAGE):
        node = node.parent
    if node is None:
        return []
    return [it for it in node.face_frame_opening.interior_items
            if it.kind == 'ACCESSORY']


def _floor_z(box_obj, z0):
    """Top of what lies on the drawer bottom: a peg board lifts the
    things that stand on it."""
    kinds = {_kind_of(it) for it in _drawer_items(box_obj)}
    if 'PEG_BOARD' in kinds:
        return z0 + PEG_BOARD_T
    return z0


def _emit(host, box_obj, item, mesh, fallback):
    name = host._insert_name(item, fallback)
    obj = mesh.to_object(name)
    if obj is None:
        return None
    for coll in box_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = box_obj
    obj['hb_part_role'] = ROLE
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_drawer_box_commands'
    obj['IS_FINISHED'] = True
    return obj


def _box_top(host, inner):
    return inner.z0 + inner.h + host.DRAWER_INSERT_RIM_GAP


def _tray(m, x0, x1, y0, y1, z0, z1, wall, mi=MAPLE, bottom=inch(0.25)):
    """Open tray: bottom panel and four walls."""
    m.box(x0, x1, y0, y1, z0, z0 + bottom, mi)
    zb = z0 + bottom
    m.box(x0, x0 + wall, y0, y1, zb, z1, mi)
    m.box(x1 - wall, x1, y0, y1, zb, z1, mi)
    m.box(x0 + wall, x1 - wall, y0, y0 + wall, zb, z1, mi)
    m.box(x0 + wall, x1 - wall, y1 - wall, y1, zb, z1, mi)
    return x0 + wall, x1 - wall, y0 + wall, y1 - wall, zb


def _partitions(m, x0, x1, y0, y1, z0, z1, count, t, mi=MAPLE):
    if count < 2:
        return
    clear = (x1 - x0) - t * (count - 1)
    if clear <= t:
        return
    comp = clear / count
    for i in range(count - 1):
        p = x0 + comp * (i + 1) + t * i
        m.box(p, p + t, y0, y1, z0, z1, mi)


def _side_slides(m, inner, z0, z1, y0, y1):
    """Side-mount slide members on the drawer box walls."""
    for x0, x1 in ((inner.x0, inner.x0 + inch(0.5)),
                   (inner.x1 - inch(0.5), inner.x1)):
        m.box(x0, x1, y0, y1, z0, z1, STEEL)


def _upper_tray(host, m, inner, depth_frac, height, slots):
    """Sliding upper tray riding at the rim on side-mount slides.
    Returns the tray rect (x0, x1, y0, y1, z0, z1)."""
    top = _box_top(host, inner) - inch(0.125)
    z0 = max(inner.z0 + inch(1.0), top - height)
    x0, x1 = inner.x0 + inch(0.5), inner.x1 - inch(0.5)
    d = (inner.y1 - inner.y0) * depth_frac
    y0, y1 = inner.y0, inner.y0 + d
    _side_slides(m, inner, z0 + inch(0.25), z0 + inch(0.75), inner.y0,
                 inner.y1)
    ix0, ix1, iy0, iy1, zb = _tray(m, x0, x1, y0, y1, z0, top,
                                   inch(0.375))
    _partitions(m, ix0, ix1, iy0, iy1, zb, top - inch(0.25), slots,
                inch(0.25))
    return x0, x1, y0, y1, z0, top


def _bread_board_drawer(host, box_obj, inner, item, params, cursor=None):
    """Cutlery / bread board drawer: cutlery slots on the drawer floor,
    a top tray at the rim holding a removable bread board beside a
    six-slot knife holder."""
    m = _Mesh()
    top = _box_top(host, inner) - inch(0.125)
    tray_h = inch(1.5)
    low_top = max(inner.z0 + inch(1.0), top - tray_h - inch(0.25))
    # Lower cutlery partitions running front to back.
    _partitions(m, inner.x0, inner.x1, inner.y0 + inch(0.5),
                inner.y1 - inch(0.5), inner.z0, low_top,
                int(params.get('SLOTS', 5)), inch(0.375))
    x0, x1, y0, y1, z0, z1 = _upper_tray(host, m, inner, 0.72, tray_h, 0)
    ix0, ix1, iy0, iy1 = (x0 + inch(0.375), x1 - inch(0.375),
                          y0 + inch(0.375), y1 - inch(0.375))
    knife_w = min(inch(4.0), (ix1 - ix0) * 0.3)
    # Knife holder: six slotted ribs at the right of the tray.
    kx0 = ix1 - knife_w
    m.box(kx0 - inch(0.25), kx0, iy0, iy1, z0 + inch(0.25), z1, MAPLE)
    for x in _spread(kx0, ix1, 6):
        m.box(x - inch(0.2), x + inch(0.2), iy0, iy1, z0 + inch(0.25),
              z1 - inch(0.125), MAPLE)
    # Bread board: 3/4" hardwood lying in the rest of the tray.
    m.box(ix0 + inch(0.0625), kx0 - inch(0.3125), iy0 + inch(0.0625),
          iy1 - inch(0.0625), z1 - inch(0.75) - inch(0.0625),
          z1 - inch(0.0625), BIRCH)
    _emit(host, box_obj, item, m, 'Cutlery / Bread Board')


def _bread_lid(host, box_obj, inner, item, params, cursor=None):
    """Bread drawer: smoked acrylic lid sliding in slots under the rim,
    with a small chrome knob at the front."""
    m = _Mesh()
    z = _box_top(host, inner) - inch(0.625)
    y0, y1 = inner.y0 + inch(0.25), inner.y1 - inch(0.25)
    m.box(inner.x0 - inch(0.1875), inner.x1 + inch(0.1875), y0, y1, z,
          z + inch(0.1875), SMOKED)
    cx = (inner.x0 + inner.x1) / 2.0
    m.cyl(cx, y0 + inch(1.5), inch(0.375), z + inch(0.1875),
          z + inch(0.9375), CHROME, seg=12)
    _emit(host, box_obj, item, m, 'Bread Drawer Lid')


def _pasta_divider(host, box_obj, inner, item, params, cursor=None):
    """Pasta / grain drawer: removable wood divider set back 2" from
    the drawer face."""
    m = _Mesh()
    y = inner.y0 + inch(float(params.get('SETBACK', 2.0))) - inch(0.75)
    y = max(y, inner.y0)
    m.box(inner.x0, inner.x1, y, y + inch(0.5), inner.z0,
          inner.z0 + inner.h, MAPLE)
    _emit(host, box_obj, item, m, 'Pasta Divider')


def _file_rails(host, box_obj, inner, item, params, cursor=None):
    """File drawer: aluminum hanging-file bars slotted into the drawer
    sides, one pair at letter spacing (files slide side to side)."""
    m = _Mesh()
    z = _box_top(host, inner) - inch(1.0)
    pitch = inch(float(params.get('SPACING', 12.25)))
    d = inner.y1 - inner.y0
    ys = ([inner.y0 + (d - pitch) / 2.0, inner.y0 + (d + pitch) / 2.0]
          if d > pitch + inch(1.0) else [inner.y0 + inch(1.0),
                                          inner.y1 - inch(1.0)])
    for y in ys:
        m.box(inner.x0 - inch(0.25), inner.x1 + inch(0.25),
              y - inch(0.0625), y + inch(0.0625), z - inch(0.75), z, STEEL)
    _emit(host, box_obj, item, m, 'File Rails')


def _drying_rack(host, box_obj, inner, item, params, cursor=None):
    """Drying rack drawer: a maple frame with stainless rods across it,
    folded in two layers inside the drawer."""
    m = _Mesh()
    rods = int(params.get('RODS', 15))
    x0, x1 = inner.x0 + inch(0.25), inner.x1 - inch(0.25)
    y0, y1 = inner.y0 + inch(0.25), inner.y1 - inch(0.25)
    rail_w, rail_h = inch(1.0), inch(0.75)
    half = max(1, rods // 2)
    for layer, (z, n) in enumerate(((inner.z0 + inch(0.25), rods - half),
                                    (inner.z0 + inch(1.25), half))):
        if z + rail_h > _box_top(host, inner):
            break
        for xa, xb in ((x0, x0 + rail_w), (x1 - rail_w, x1)):
            m.box(xa, xb, y0, y1, z, z + rail_h, MAPLE)
        for ya, yb in ((y0, y0 + rail_w), (y1 - rail_w, y1)):
            m.box(x0 + rail_w, x1 - rail_w, ya, yb, z, z + rail_h, MAPLE)
        for y in _spread(y0 + rail_w, y1 - rail_w, n):
            m.cyl(y, z + rail_h / 2.0, inch(0.1875), x0 + rail_w,
                  x1 - rail_w, STEEL, seg=8, axis='X')
    _emit(host, box_obj, item, m, 'Drying Rack')


def _docking(host, box_obj, inner, item, params, cursor=None):
    """Docking drawer station: slim box against the back of the drawer,
    face plate up, with its USB / AC ports."""
    m = _Mesh()
    w = min(inch(float(params.get('W', 12.375))), inner.x1 - inner.x0)
    d = min(inch(float(params.get('D', 2.75))), inner.y1 - inner.y0)
    h = min(inch(float(params.get('H', 3.25))), inner.h)
    cx = (inner.x0 + inner.x1) / 2.0
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y1 = inner.y1
    y0 = y1 - d
    z0 = inner.z0
    m.box(x0, x1, y0, y1, z0, z0 + h - inch(0.125), STEEL)
    m.box(x0 - inch(0.125), x1 + inch(0.125), y0 - inch(0.125), y1,
          z0 + h - inch(0.125), z0 + h, BLACK)
    usb = int(params.get('USB', 2))
    ac = int(params.get('AC', 2))
    ports = [('AC', i) for i in range(ac)] + [('USB', i) for i in range(usb)]
    zt = z0 + h
    for (kind, _i), x in zip(ports, _spread(x0 + inch(1.0), x1 - inch(1.0),
                                            len(ports))):
        if kind == 'AC':
            m.box(x - inch(0.5), x + inch(0.5), y0 + inch(0.5),
                  y1 - inch(0.5), zt, zt + inch(0.06), WHITE)
        else:
            m.box(x - inch(0.25), x + inch(0.25), y0 + inch(1.0),
                  y0 + inch(1.4), zt, zt + inch(0.06), WHITE)
    _emit(host, box_obj, item, m, 'Docking Station')


def _grooming(host, box_obj, inner, item, params, cursor=None):
    """Grooming drawer: two removable stainless bins at the front left,
    non-skid compartments, and a tamper-resistant outlet on the back
    compartment wall."""
    m = _Mesh()
    top = inner.z0 + inner.h
    w = inner.x1 - inner.x0
    d = inner.y1 - inner.y0
    t = inch(0.5)
    mid_y = inner.y0 + d * 0.55
    m.box(inner.x0, inner.x1, mid_y, mid_y + t, inner.z0, top, MAPLE)
    split_x = inner.x0 + w * 0.5
    m.box(split_x, split_x + t, inner.y0, mid_y, inner.z0, top, MAPLE)
    # Bins stand in a shelf with two round cut-outs (shelf drawn as a
    # frame around them).
    shelf_z = top - inch(0.5)
    r = min(inch(2.0), (split_x - inner.x0) / 4.0 - inch(0.1),
            (mid_y - inner.y0) / 2.0 - inch(0.25))
    if r > inch(0.75):
        m.box(inner.x0, split_x, inner.y0, mid_y, shelf_z, shelf_z + t, MAPLE)
        for cx in _spread(inner.x0, split_x, 2):
            cy = (inner.y0 + mid_y) / 2.0
            m.cyl(cx, cy, r, inner.z0 + inch(0.25), shelf_z + t + inch(0.05),
                  STEEL, seg=16)
    # Non-skid linings.
    m.box(split_x + t, inner.x1, inner.y0, mid_y, inner.z0,
          inner.z0 + MAT_T, RUBBER)
    m.box(inner.x0, inner.x1, mid_y + t, inner.y1, inner.z0,
          inner.z0 + MAT_T, RUBBER)
    # Outlet plate on the back compartment's front wall.
    ox = (inner.x0 + inner.x1) / 2.0
    oz = inner.z0 + min(inner.h * 0.5, inch(3.0))
    m.box(ox - inch(1.4), ox + inch(1.4), mid_y + t, mid_y + t + inch(0.1),
          oz - inch(1.0), oz + inch(1.0), WHITE)
    _emit(host, box_obj, item, m, 'Grooming Drawer')


def _ironing_board(host, box_obj, inner, item, params, cursor=None):
    """Ironing board drawer: the board folded flat on its steel frame,
    stored behind the drawer face."""
    m = _Mesh()
    bw = min(inch(11.75), inner.x1 - inner.x0 - inch(1.0))
    cx = (inner.x0 + inner.x1) / 2.0
    x0, x1 = cx - bw / 2.0, cx + bw / 2.0
    y0, y1 = inner.y0 + inch(0.5), inner.y1 - inch(0.5)
    z = inner.z0
    # Frame: two steel channels along the sides, cross bars.
    for xa in (inner.x0 + inch(0.25), inner.x1 - inch(1.25)):
        m.box(xa, xa + inch(1.0), inner.y0, inner.y1, z, z + inch(1.0),
              STEEL)
    for y in (y0 + inch(1.0), y1 - inch(1.0)):
        m.box(inner.x0 + inch(1.25), inner.x1 - inch(1.25),
              y - inch(0.375), y + inch(0.375), z + inch(0.25), z + inch(0.75),
              STEEL)
    # Folded board: two layers, the nose rounded.
    r = bw / 2.0
    zb = z + inch(1.0)
    for k in range(2):
        za = zb + k * inch(1.0)
        if za + inch(0.875) > _box_top(host, inner):
            break
        poly = [(x0, y0), (x1, y0), (x1, y1 - r)]
        for i in range(1, 12):
            a = math.pi * i / 12.0
            poly.append((cx + r * math.cos(a), y1 - r + r * math.sin(a)))
        poly.append((x0, y1 - r))
        m.prism(poly, 'Z', za, za + inch(0.625), STEEL)
        m.prism(poly, 'Z', za + inch(0.625), za + inch(0.875), WHITE)
    _emit(host, box_obj, item, m, 'Ironing Board')


def _peg_board(host, box_obj, inner, item, params, cursor=None):
    """Dish drawer peg board floor (maple, or gray vinyl), with the peg
    hole grid marked on its top."""
    m = _Mesh()
    gray = float(params.get('GRAY', 0.0)) >= 0.5
    w = min(inner.x1 - inner.x0, inch(39.25))
    d = min(inner.y1 - inner.y0, inch(21.25))
    x0 = (inner.x0 + inner.x1) / 2.0 - w / 2.0
    y0 = inner.y0
    z1 = inner.z0 + PEG_BOARD_T
    m.box(x0, x0 + w, y0, y0 + d, inner.z0, z1, GRAY if gray else MAPLE)
    pitch = inch(2.0)
    hr = inch(0.2)
    nx = int((w - inch(1.0)) / pitch)
    ny = int((d - inch(1.0)) / pitch)
    sx = x0 + (w - (nx - 1) * pitch) / 2.0
    sy = y0 + (d - (ny - 1) * pitch) / 2.0
    for i in range(max(nx, 0)):
        for j in range(max(ny, 0)):
            x, y = sx + i * pitch, sy + j * pitch
            m.box(x - hr, x + hr, y - hr, y + hr, z1, z1 + inch(0.01), BLACK)
    _emit(host, box_obj, item, m, 'Peg Board')


def _floor_users_width(box_obj, host):
    """Width the floor-taking inserts of this drawer claim at their
    published sizes, so loose pegs stand clear of them."""
    from . import types_face_frame as tff
    total = 0.0
    for it in _drawer_items(box_obj):
        kind, p = tff.parse_render_hint(it.accessory_render)
        spec = tff.DRAWER_INSERT_BUILDERS.get(kind)
        if spec is None or not spec[2]:
            continue
        w = getattr(it, 'insert_width', 0.0) or inch(p.get('W', 0.0))
        total += w * max(getattr(it, 'accessory_qty', 1), 1)
    return total


def _dish_pegs(host, box_obj, inner, item, params, cursor=None):
    """Dish pegs, sets of four: each set rings one stack of plates,
    standing on the peg board (or the drawer floor), clear of the racks
    and inserts packed from the left."""
    m = _Mesh()
    metal = float(params.get('METAL', 0.0)) >= 0.5
    sets = max(getattr(item, 'accessory_qty', 1), 1)
    z0 = _floor_z(box_obj, inner.z0)
    h = min(inch(float(params.get('H', 6.0))), _box_top(host, inner) - z0
            - inch(0.25))
    r = inch(0.375) if not metal else inch(0.25)
    side = inch(float(params.get('RING', 9.0)))
    x_start = max(cursor or inner.x0,
                  inner.x0 + _floor_users_width(box_obj, host))
    span = inner.x1 - x_start
    if span < side:
        x_start, span = inner.x0, inner.x1 - inner.x0
    d = inner.y1 - inner.y0
    for k, cx in enumerate(_spread(x_start, x_start + span, sets)):
        cy = inner.y0 + d / 2.0
        s = min(side, span / sets - inch(1.0), d - inch(2.0)) / 2.0
        for dx, dy in ((-s, -s), (s, -s), (s, s), (-s, s)):
            m.cyl(cx + dx, cy + dy, r, z0, z0 + h,
                  CHROME if metal else MAPLE, seg=10)
    _emit(host, box_obj, item, m, 'Dish Pegs')


def _tray_dividers(host, box_obj, inner, item, params, cursor=None):
    """Upright 1/4" birch tray dividers running front to back, standing
    in hardwood channels, spaced equally across the drawer."""
    m = _Mesh()
    n = max(getattr(item, 'accessory_qty', 1), 1)
    x0 = cursor if cursor and cursor > inner.x0 else inner.x0
    top = inner.z0 + inner.h
    for x in [x0 + (inner.x1 - x0) * (i + 1) / (n + 1) for i in range(n)]:
        m.box(x - inch(0.125), x + inch(0.125), inner.y0, inner.y1,
              inner.z0 + inch(0.25), top, BIRCH)
        m.box(x - inch(0.375), x + inch(0.375), inner.y0, inner.y1,
              inner.z0, inner.z0 + inch(0.5), MAPLE)
    _emit(host, box_obj, item, m, 'Tray Dividers')


def _pencil_scoop(host, box_obj, inner, item, params, cursor=None):
    """Pencil scoop: a maple trough across the front of the drawer with a
    coved inside."""
    m = _Mesh()
    d = inch(float(params.get('D', 2.5)))
    h = min(inch(float(params.get('H', 1.375))), inner.h)
    y0 = inner.y0
    r = min(d / 2.0 - inch(0.125), h - inch(0.25))
    prof = [(y0, inner.z0), (y0 + d, inner.z0), (y0 + d, inner.z0 + h),
            (y0 + d - inch(0.125), inner.z0 + h)]
    cy = y0 + d / 2.0
    for i in range(1, 12):
        a = math.pi * i / 12.0
        prof.append((cy + r * math.cos(a),
                     inner.z0 + h - r * math.sin(a)))
    prof.append((y0 + inch(0.125), inner.z0 + h))
    prof.append((y0, inner.z0 + h))
    m.prism(prof, 'X', inner.x0, inner.x1, MAPLE)
    _emit(host, box_obj, item, m, 'Pencil Scoop')


def _double_tier(host, box_obj, inner, item, params, cursor=None):
    """Double tier drawer: an upper sliding tray on side-mount slides at
    the rim (pushes back into the cabinet). The organizer drawers add
    cutlery compartments in the tray and in the main drawer below it,
    the large ones a knife section."""
    m = _Mesh()
    organizer = float(params.get('ORGANIZER', 0.0)) >= 0.5
    knife = float(params.get('KNIFE', 0.0)) >= 0.5
    w = inner.x1 - inner.x0
    slots = (max(3, min(6, int(w / inch(3.0)))) if organizer else 0)
    x0, x1, y0, y1, z0, z1 = _upper_tray(host, m, inner, 0.58,
                                         inch(2.0), slots)
    if organizer:
        low_top = max(inner.z0 + inch(1.0), z0 - inch(0.25))
        ly0 = inner.y0 + inch(0.5)
        lx1 = inner.x1
        if knife:
            # Knife section at the right: slotted ribs.
            kw = min(inch(5.0), w * 0.25)
            lx1 = inner.x1 - kw
            for x in _spread(lx1, inner.x1, 7):
                m.box(x - inch(0.25), x + inch(0.25), ly0,
                      inner.y1 - inch(0.5), inner.z0,
                      inner.z0 + min(inch(2.0), low_top - inner.z0), MAPLE)
        _partitions(m, inner.x0, lx1, ly0, inner.y1 - inch(0.5),
                    inner.z0, low_top, max(3, slots - 1), inch(0.375))
        # Cross rail at the back of the lower compartments.
        m.box(inner.x0, lx1, inner.y1 - inch(4.5), inner.y1 - inch(4.125),
              inner.z0, low_top, MAPLE)
    _emit(host, box_obj, item, m, 'Double Tier Tray')


def _mat(host, box_obj, inner, item, params, cursor=None):
    """Non-slip mat cut to the drawer bottom."""
    m = _Mesh()
    m.box(inner.x0, inner.x1, inner.y0, inner.y1, inner.z0,
          inner.z0 + MAT_T, RUBBER)
    _emit(host, box_obj, item, m, 'Non-Slip Mat')


# -- floor-taking drawer inserts (packed at their own size) -----------------

def _roll_dispenser(host, box_obj, rect, item, params):
    """Double roll dispenser: a birch box with two rolls side by side
    under rounded lids running front to back."""
    m = _Mesh()
    x0, x1, y0, y1, z0 = rect.x0, rect.x1, rect.y0, rect.y1, rect.z0
    h = rect.h
    base = min(h * 0.45, inch(1.0))
    m.box(x0, x1, y0, y1, z0, z0 + base, BIRCH)
    w = x1 - x0
    r = min(w / 4.0, h - base)
    for cx in (x0 + w * 0.25, x0 + w * 0.75):
        poly = [(cx - r, z0 + base)]
        for i in range(1, 12):
            a = math.pi - math.pi * i / 12.0
            poly.append((cx + r * math.cos(a), z0 + base + r * math.sin(a)))
        poly.append((cx + r, z0 + base))
        m.prism(poly, 'Y', y0 + inch(0.25), y1 - inch(0.25), BIRCH)
    # Cutter strip across the front.
    m.box(x0, x1, y0, y0 + inch(0.25), z0, z0 + base + r * 0.6, BIRCH)
    _emit(host, box_obj, item, m, 'Roll Dispenser')


def _container_holder(host, box_obj, rect, item, params):
    """Insert container holder: a low birch frame holding two clear
    containers."""
    m = _Mesh()
    ix0, ix1, iy0, iy1, zb = _tray(m, rect.x0, rect.x1, rect.y0, rect.y1,
                                   rect.z0, rect.z0 + rect.h * 0.6,
                                   inch(0.25), BIRCH)
    n = 2
    pitch = (iy1 - iy0) / n
    for k in range(n):
        cy0 = iy0 + pitch * k + inch(0.125)
        m.box(ix0 + inch(0.125), ix1 - inch(0.125), cy0, cy0 + pitch
              - inch(0.25), zb, rect.z0 + rect.h, CLEAR)
    _emit(host, box_obj, item, m, 'Container Holder')


def _wire_frames(m, x0, x1, y0, y1, z0, h, loops, across):
    """Chrome rack: base rails and upright loops. across=True: loops run
    side to side (things stand front to back between them)."""
    t = inch(0.1875)
    if across:
        for x in (x0, x1):
            m.rod(x, x, y0, y1, z0 + t / 2, z0 + t / 2, t)
        for y in _spread(y0, y1, loops):
            m.rod(x0, x0, y, y, z0, z0 + h, t)
            m.rod(x1, x1, y, y, z0, z0 + h, t)
            m.rod(x0, x1, y, y, z0 + h, z0 + h, t)
    else:
        for y in (y0, y1):
            m.rod(x0, x1, y, y, z0 + t / 2, z0 + t / 2, t)
        for x in _spread(x0, x1, loops):
            m.rod(x, x, y0, y0, z0, z0 + h, t)
            m.rod(x, x, y1, y1, z0, z0 + h, t)
            m.rod(x, x, y0, y1, z0 + h, z0 + h, t)


def _rack_z(box_obj, rect):
    z0 = _floor_z(box_obj, rect.z0)
    return z0, rect.h - (z0 - rect.z0)


def _lid_rack(host, box_obj, rect, item, params):
    """Lid organizer: chrome rack with upright loops for six lids."""
    m = _Mesh()
    z0, h = _rack_z(box_obj, rect)
    _wire_frames(m, rect.x0 + inch(0.25), rect.x1 - inch(0.25),
                 rect.y0 + inch(0.25), rect.y1 - inch(0.25), z0, h,
                 int(params.get('SLOTS', 7)), True)
    _emit(host, box_obj, item, m, 'Lid Organizer')


def _pot_rack(host, box_obj, rect, item, params):
    """Pot & pan / cookware organizer: adjustable chrome rack with a
    handle rest along the front."""
    m = _Mesh()
    z0, h = _rack_z(box_obj, rect)
    x0, x1 = rect.x0 + inch(0.25), rect.x1 - inch(0.25)
    y0, y1 = rect.y0 + inch(0.25), rect.y1 - inch(0.25)
    _wire_frames(m, x0, x1, y0, y1, z0, h,
                 int(params.get('SLOTS', 5)), True)
    t = inch(0.1875)
    m.rod(x0, x1, y0, y0, z0 + h * 0.5, z0 + h * 0.5, t)
    m.rod(x0, x1, y1, y1, z0 + h * 0.5, z0 + h * 0.5, t)
    _emit(host, box_obj, item, m, 'Cookware Organizer')


def _canister_rack(host, box_obj, rect, item, params):
    """Canister set: two stainless containers with see-through lids in a
    chrome rack."""
    m = _Mesh()
    z0, h = _rack_z(box_obj, rect)
    x0, x1, y0, y1 = rect.x0, rect.x1, rect.y0, rect.y1
    t = inch(0.1875)
    for y in (y0 + t, y1 - t):
        m.rod(x0, x1, y, y, z0 + t / 2, z0 + t / 2, t)
        m.rod(x0, x1, y, y, z0 + h * 0.6, z0 + h * 0.6, t)
    w = x1 - x0
    r = min(w / 4.0, (y1 - y0) / 2.0) - inch(0.125)
    for cx in (x0 + w * 0.25, x0 + w * 0.75):
        cy = (y0 + y1) / 2.0
        m.cyl(cx, cy, r, z0 + t, z0 + h - inch(0.5), STEEL, seg=16)
        m.cyl(cx, cy, r + inch(0.0625), z0 + h - inch(0.5), z0 + h, CLEAR,
              seg=16)
        for x in (cx - r, cx + r):
            m.rod(x, x, y0 + t, y0 + t, z0, z0 + h * 0.6, t)
            m.rod(x, x, y1 - t, y1 - t, z0, z0 + h * 0.6, t)
    _emit(host, box_obj, item, m, 'Canister Set')


_DRAWER_FNS = {
    'bread_board_drawer': _bread_board_drawer,
    'bread_lid': _bread_lid,
    'pasta_divider': _pasta_divider,
    'file_rails': _file_rails,
    'drying_rack': _drying_rack,
    'docking': _docking,
    'grooming': _grooming,
    'ironing_board': _ironing_board,
    'peg_board': _peg_board,
    'dish_pegs': _dish_pegs,
    'tray_dividers': _tray_dividers,
    'pencil_scoop': _pencil_scoop,
    'double_tier': _double_tier,
    'mat': _mat,
    'roll_dispenser': _roll_dispenser,
    'container_holder': _container_holder,
    'lid_rack': _lid_rack,
    'pot_rack': _pot_rack,
    'canister_rack': _canister_rack,
}


def drawer_builder(host, name):
    """Bound builder for a 'misc:' drawer insert builder name, or None.
    Called with the same arguments as the drawer code's own builders."""
    if not name.startswith('misc:'):
        return None
    fn = _DRAWER_FNS.get(name[5:])
    return partial(fn, host) if fn is not None else None


# ---------------------------------------------------------------------------
# Opening units
# ---------------------------------------------------------------------------
FRONT_MODELS = frozenset({'door_rack', 'tilt_tray'})
OPENING_MODELS = frozenset({
    'pullout_board', 'butcher_block', 'keyboard_rollout', 'tv_swivel',
    'swing_rack', 'swinger_pantry'})
MODELS = FRONT_MODELS | OPENING_MODELS
# Slide out of the opening as its front opens.
ROLLING_MODELS = frozenset({'pullout_board', 'butcher_block',
                            'keyboard_rollout', 'tv_swivel'})
# Builds racks on the doors as well as its units in the opening.
DOOR_RACK_MODELS = frozenset({'door_rack', 'swinger_pantry'})


def _f(params, key, default):
    try:
        return float(params.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def _opening_of(item):
    """The opening cage owning an interior item, or None."""
    node = getattr(item, 'id_data', None)
    while node is not None and not node.get(TAG_OPENING_CAGE):
        node = node.parent
    return node


def _swing(item):
    """(door angle, hinge side) of the opening the item stands in."""
    op = _opening_of(item)
    if op is None:
        return 0.0, 'RIGHT'
    props = op.face_frame_opening
    return (props.swing_percent * math.radians(90.0),
            getattr(props, 'hinge_side', 'RIGHT'))


def descriptor(rect, cage_dim_y, item, front_y, back_setback, model, params):
    """Placement for one of this module's opening models (see
    accessory_models.descriptor). Front-mounted models return a
    descriptor that builds nothing in the opening, so no label is shown:
    their units are built on the front (attach_front_models)."""
    rev_l = max(0.0, rect.get('reveal_left', 0.0))
    rev_r = max(0.0, rect.get('reveal_right', 0.0))
    rev_b = max(0.0, rect.get('reveal_bottom', 0.0))
    rev_t = max(0.0, rect.get('reveal_top', 0.0))
    open_w = rect['cage_dim_x'] - rev_l - rev_r
    open_h = rect['cage_dim_z'] - rev_b - rev_t
    room_y = cage_dim_y - front_y - back_setback
    if open_w <= inch(2.0) or open_h <= inch(1.0) or room_y <= inch(2.0):
        return None
    params = dict(params)
    top = rev_b + open_h
    if model in FRONT_MODELS:
        params['_front_mounted'] = True
        pos, dims = (rev_l, front_y, rev_b), (open_w, room_y, open_h)
    elif model == 'pullout_board':
        w = min(open_w - inch(0.5), inch(_f(params, 'max_width', 24.0)))
        d = min(room_y + front_y, inch(_f(params, 'depth', 20.0)))
        t = inch(0.75)
        # Rides in the slot cut in a top rail deep enough to take it,
        # else just under the rail; the nosing is flush with the frame.
        z = (top + (rev_t - t) / 2.0 if rev_t >= inch(1.5)
             else top - t - inch(0.125))
        ff = inch(0.75)
        pos, dims = (rev_l + (open_w - w) / 2.0, -ff, z), (w, d + ff, t)
    elif model == 'butcher_block':
        w = min(open_w - inch(0.5), inch(_f(params, 'max_width', 24.0)) +
                inch(1.0))
        d = min(room_y, inch(_f(params, 'depth', 21.0)))
        h = min(inch(1.75), open_h)
        pos, dims = (rev_l + (open_w - w) / 2.0, front_y,
                     top - inch(0.25) - h), (w, d, h)
    elif model == 'keyboard_rollout':
        deluxe = bool(params.get('deluxe'))
        w = min(open_w - inch(1.0),
                inch(_f(params, 'unit_width', 28.0 if deluxe else 26.0)))
        d = min(room_y + front_y, inch(_f(params, 'depth',
                                          18.0 if deluxe else 12.0)))
        h = min(inch(3.625), open_h)
        pos, dims = (rev_l + (open_w - w) / 2.0, 0.0, top - h), (w, d, h)
    elif model == 'tv_swivel':
        w = max(open_w - inch(_f(params, 'clearance', 8.0)), inch(6.0))
        w = min(w, open_w)
        d = min(room_y + front_y, inch(_f(params, 'depth', 22.0)))
        h = min(inch(3.25), open_h)
        pos, dims = (rev_l + (open_w - w) / 2.0, 0.0, rev_b), (w, d, h)
    else:   # swing_rack / swinger_pantry: the whole opening hole
        angle, hinge = _swing(item)
        params['_swing'] = angle
        params['_hinge'] = hinge
        pos, dims = (rev_l, front_y, rev_b), (open_w, room_y, open_h)
    if model in ROLLING_MODELS:
        # Opening the front shows the unit pulled part way out.
        angle, _hinge = _swing(item)
        pull = (angle / math.radians(90.0)) * dims[1] * 0.6
        pos = (pos[0], pos[1] - pull, pos[2])
    label = getattr(item, 'accessory_label', '') or item.accessory_code
    return {
        'kind':     'ACCESSORY_MODEL',
        'role':     ROLE,
        'name':     '%s Model' % label,
        'model':    model,
        'params':   params,
        'position': pos,
        'dims':     dims,
    }


def _rack(m, x0, x1, y0, y1, z0, z1, spacing, rails, first=None,
          double=False, mi=MAPLE):
    """Open-backed rack: sides, top, bottom, shelves at ``spacing`` and a
    rail in front of each shelf on the open face (y1; both faces when
    ``double``, with a center panel)."""
    t = inch(0.5)
    if x1 - x0 < 3 * t or z1 - z0 < 3 * t or y1 - y0 < inch(1.0):
        m.box(x0, x1, y0, y1, z0, z1, mi)
        return
    m.box(x0, x0 + t, y0, y1, z0, z1, mi)
    m.box(x1 - t, x1, y0, y1, z0, z1, mi)
    m.box(x0 + t, x1 - t, y0, y1, z0, z0 + t, mi)
    m.box(x0 + t, x1 - t, y0, y1, z1 - t, z1, mi)
    if double:
        cy = (y0 + y1) / 2.0
        m.box(x0 + t, x1 - t, cy - inch(0.125), cy + inch(0.125), z0 + t,
              z1 - t, mi)
    else:
        m.box(x0 + t, x1 - t, y0, y0 + inch(0.25), z0 + t, z1 - t, mi)
    shelves = [z0]
    z = z0 + (inch(first) if first else spacing)
    while z < z1 - t - inch(2.0):
        m.box(x0 + t, x1 - t, y0, y1, z, z + t, mi)
        shelves.append(z)
        z += spacing
    faces = (y0, y1) if double else (y1,)
    for zs in shelves:
        rz = zs + t + inch(1.3)
        if rz > z1 - t:
            continue
        for yf in faces:
            yr = yf - inch(0.3) if yf == y1 else yf + inch(0.3)
            if rails == 'chrome':
                m.rod(x0 + t, x1 - t, yr, yr, rz, rz, inch(0.15), CHROME)
            else:
                m.cyl(yr, rz, inch(0.1875), x0 + t, x1 - t, mi, seg=8,
                      axis='X')


def _build_door_rack(m, w, d, h, params):
    rd = min(inch(_f(params, 'rack_depth', 3.75)), d)
    _rack(m, 0.0, w, 0.0, rd, 0.0, h,
          inch(_f(params, 'spacing', 5.5)),
          params.get('rails', 'wood'), first=params.get('first'))


def _build_tilt_tray(m, w, d, h, params):
    """Stainless tray on concealed hinges."""
    td = min(inch(_f(params, 'tray_depth', 2.125)), d)
    th = min(inch(_f(params, 'tray_height', 3.0)), h)
    t = inch(0.04)
    m.box(0.0, w, 0.0, td, 0.0, t, STEEL)
    m.box(0.0, w, td - t, td, 0.0, th, STEEL)
    m.box(0.0, w, 0.0, t, 0.0, th * 0.6, STEEL)
    m.box(0.0, t, 0.0, td, 0.0, th, STEEL)
    m.box(w - t, w, 0.0, td, 0.0, th, STEEL)
    for x in (inch(0.75), w - inch(1.75)):
        m.box(x, x + inch(1.0), 0.0, inch(0.5), th * 0.4, th, STEEL)


def _build_pullout_board(m, w, d, h, params):
    """Board with a hardwood nosing at the front (y = 0)."""
    ff = min(inch(0.75), d * 0.2)
    whole_finish = bool(params.get('finish_board'))
    board = FINISH if whole_finish else MAPLE
    m.box(0.0, w, 0.0, ff, 0.0, h, FINISH)
    m.box(0.0, w, ff, d, 0.0, h, board)
    # Finger pull groove under the nosing.
    m.box(w * 0.35, w * 0.65, 0.0, ff, -inch(0.01), inch(0.05), BLACK)


def _build_butcher_block(m, w, d, h, params):
    """1-1/2" maple butcher block on side-mount slides."""
    sw = inch(0.5)
    bt = min(inch(1.5), h)
    x0, x1 = sw, w - sw
    strips = max(1, int((x1 - x0) / inch(1.5)))
    pitch = (x1 - x0) / strips
    for i in range(strips):
        m.box(x0 + pitch * i, x0 + pitch * (i + 1), 0.0, d, h - bt, h,
              MAPLE if i % 2 == 0 else BIRCH)
    for xa in (0.0, w - sw):
        m.box(xa, xa + sw, inch(0.5), d, h - bt + inch(0.25),
              h - inch(0.25), STEEL)


def _build_keyboard_rollout(m, w, d, h, params):
    deluxe = bool(params.get('deluxe'))
    if deluxe:
        body = BLACK
        deck_t = inch(0.75)
        m.box(0.0, w, 0.0, d, 0.0, deck_t, body)
        # Gel palm rest along the front, mouse pad at the right, storage
        # compartments across the back.
        m.box(inch(0.5), w - inch(0.5), 0.0, inch(2.5), deck_t,
              deck_t + inch(0.75), body)
        m.box(w - inch(8.5), w - inch(0.5), inch(3.0), inch(11.0), deck_t,
              deck_t + inch(0.06), GRAY)
        by = d - inch(4.0)
        m.box(0.0, w, by, by + inch(0.25), deck_t, deck_t + inch(1.0), body)
        for x in (w / 3.0, 2.0 * w / 3.0):
            m.box(x - inch(0.125), x + inch(0.125), by, d, deck_t,
                  deck_t + inch(1.0), body)
        m.box(0.0, w, d - inch(0.25), d, deck_t, deck_t + inch(1.0), body)
    else:
        deck_t = inch(0.75)
        m.box(0.0, w, inch(0.75), d, 0.0, deck_t, BIRCH)
        m.box(0.0, w, 0.0, inch(0.75), 0.0, deck_t, MAPLE)
    # Hanging brackets and slides up to the top of the unit.
    for xa in (inch(1.0), w - inch(1.5)):
        m.box(xa, xa + inch(0.5), inch(1.0), inch(1.5), deck_t, h, STEEL)
        m.box(xa, xa + inch(0.5), d - inch(2.0), d - inch(1.5), deck_t, h,
              STEEL)
        m.box(xa - inch(0.25), xa + inch(0.75), inch(0.5), d - inch(0.5),
              h - inch(0.5), h, STEEL)


def _build_tv_swivel(m, w, d, h, params):
    """Steel mechanism (base, slides, turntable) under a 3/4" deck with a
    2-1/2" hardwood nosing."""
    deck_t = inch(0.75)
    nose_h = min(inch(2.5), h)
    zt = h
    zd = zt - deck_t
    m.box(inch(1.0), w - inch(1.0), inch(1.0), d - inch(0.5), 0.0,
          inch(0.25), STEEL)
    for xa in (inch(1.0), w - inch(2.0)):
        m.box(xa, xa + inch(1.0), inch(1.0), d - inch(0.5), inch(0.25),
              inch(1.25), STEEL)
    r = min(w, d) * 0.3
    m.cyl(w / 2.0, d / 2.0, r, inch(1.25), zd, STEEL, seg=24)
    m.box(0.0, w, deck_t, d, zd, zt, BIRCH)
    m.box(0.0, w, 0.0, deck_t, zt - nose_h, zt, MAPLE)


def _build_swing_unit(m, x_hinge, y0, w, depth, h, left, angle, spacing,
                      rails, mi=MAPLE):
    """Double-sided rack hinged at its front corner on x_hinge, swung by
    ``angle`` (free end toward the room)."""
    sub = _Mesh()
    x0 = x_hinge if left else x_hinge - w
    _rack(sub, x0, x0 + w, y0, y0 + depth, 0.0, h, spacing, rails,
          double=True, mi=mi)
    sub.rotate_z(-angle if left else angle, x_hinge, y0)
    sub.bm.verts.ensure_lookup_table()
    # Merge into the target mesh.
    bm = m.bm
    vmap = {}
    for v in sub.bm.verts:
        vmap[v] = bm.verts.new(v.co)
    for f in sub.bm.faces:
        bm.faces.new([vmap[v] for v in f.verts]).material_index = \
            f.material_index
    sub.bm.free()


def _swing_rack_width(open_w_in):
    """Swing-out spice rack width for an opening: 12" -> 7", 15" -> 11",
    19" -> 16" (interpolated, held at the ends)."""
    pts = ((12.0, 7.0), (15.0, 11.0), (19.0, 16.0))
    if open_w_in <= pts[0][0]:
        return pts[0][1] - (pts[0][0] - open_w_in)
    for (a, wa), (b, wb) in zip(pts, pts[1:]):
        if open_w_in <= b:
            return wa + (wb - wa) * (open_w_in - a) / (b - a)
    return open_w_in - 3.0


def _build_swing_rack(m, w, d, h, params):
    hinge = params.get('_hinge', 'RIGHT')
    left = hinge != 'LEFT'          # rack on the side opposite the hinge
    rw = min(inch(_swing_rack_width(w / I)), w - inch(1.0))
    depth = min(inch(_f(params, 'rack_depth', 6.0)), d)
    rh = h - inch(0.5)
    _build_swing_unit(m, 0.0 if left else w, inch(0.25), rw, depth, rh,
                      left, _f(params, '_swing', 0.0),
                      inch(_f(params, 'spacing', 5.5)), 'wood')


def _build_swinger_pantry(m, w, d, h, params):
    if params.get('_front_mounted'):
        return
    sw = min(inch(_f(params, 'swinger_width', 12.0)), (w - inch(1.0)) / 2.0)
    depth = min(inch(_f(params, 'swinger_depth', 4.0)), d * 0.4)
    y0 = min(inch(_f(params, 'swinger_setback', 4.5)), d - depth)
    angle = _f(params, '_swing', 0.0)
    for left, xh in ((True, 0.0), (False, w)):
        _build_swing_unit(m, xh, y0, sw, depth, h - inch(0.5), left, angle,
                          inch(12.0), 'chrome')


_BUILDERS = {
    'door_rack': _build_door_rack,
    'tilt_tray': _build_tilt_tray,
    'pullout_board': _build_pullout_board,
    'butcher_block': _build_butcher_block,
    'keyboard_rollout': _build_keyboard_rollout,
    'tv_swivel': _build_tv_swivel,
    'swing_rack': _build_swing_rack,
    'swinger_pantry': _build_swinger_pantry,
}


def build_object(model, name, w, depth, h, params=None):
    """Unlinked mesh object for an opening model, or None. A
    front-mounted model builds nothing in the opening."""
    params = params or {}
    builder = _BUILDERS.get(model)
    if builder is None or w <= 0.0 or h <= 0.0 or depth <= 0.0:
        return None
    if params.get('_front_mounted') and model in FRONT_MODELS:
        return None
    m = _Mesh()
    builder(m, w, depth, h, params)
    finish = model == 'pullout_board'
    return m.to_object(name, finish_match=finish)


# ---------------------------------------------------------------------------
# Front-mounted units
# ---------------------------------------------------------------------------

def _front_spec(code):
    from ... import accessory_registry
    entry = accessory_registry.find(code) if code else None
    if not entry or entry.get('model') not in MODELS:
        return None
    params = entry.get('model_params') or {}
    return entry, entry['model'], (params if isinstance(params, dict) else {})


def attach_front_models(opening_obj, op_props, rect, leaves):
    """Build the racks / trays the opening's accessories mount on its
    fronts. ``leaves`` is [(pivot, leaf)] as just built; each unit is
    parented to its front's pivot so it swings with the front."""
    if not leaves:
        return
    items = [it for it in getattr(op_props, 'interior_items', ())
             if it.kind == 'ACCESSORY']
    rl = max(0.0, rect.get('reveal_left', 0.0))
    rr = max(0.0, rect.get('reveal_right', 0.0))
    rb = max(0.0, rect.get('reveal_bottom', 0.0))
    rt = max(0.0, rect.get('reveal_top', 0.0))
    hx0, hx1 = rl, rect['cage_dim_x'] - rr
    hz0, hz1 = rb, rect['cage_dim_z'] - rt
    for item in items:
        spec = _front_spec(getattr(item, 'accessory_code', ''))
        if spec is None:
            continue
        entry, model, params = spec
        if model in DOOR_RACK_MODELS:
            targets = [pl for pl in leaves if pl[1].get('role') == 'DOOR']
            if model == 'door_rack':
                # Leaves come left to right; racks fill from the door
                # picked for them.
                if getattr(item, 'accessory_door', 'LEFT') == 'RIGHT':
                    targets.reverse()
                targets = targets[:max(getattr(item, 'accessory_qty', 1), 1)]
            rparams = dict(params)
            if model == 'swinger_pantry':
                rparams = {'rack_depth': params.get('door_rack_depth', 4.0),
                           'spacing': params.get('door_rack_spacing', 12.0),
                           'rails': 'chrome'}
            margin = inch(_f(params, 'side_margin', 1.5))
            for pivot, leaf in targets:
                _attach_on_front(pivot, leaf, entry, 'door_rack', rparams,
                                 hx0, hx1, hz0 + inch(0.5),
                                 hz1 - inch(0.5), margin)
        elif model == 'tilt_tray':
            targets = [pl for pl in leaves if pl[1].get('role') in
                       ('TILT_OUT', 'FALSE_FRONT', 'DOOR')][:1]
            th = inch(_f(params, 'tray_height', 3.0))
            for pivot, leaf in targets:
                _attach_on_front(pivot, leaf, entry, 'tilt_tray', params,
                                 hx0, hx1, max(hz0, hz1 - inch(0.5) - th),
                                 hz1 - inch(0.5),
                                 inch(_f(params, 'side_margin', 1.0)),
                                 max_w=inch(_f(params, 'max_width', 33.0)))


def _attach_on_front(pivot, leaf, entry, model, params, hx0, hx1, hz0, hz1,
                     margin, max_w=None):
    """Place one unit on the back of a front, inside the face frame
    hole (it passes through the hole as the front closes)."""
    px, py, pz = leaf['pivot_position']
    ox, oy, oz = leaf.get('part_position', (0.0, 0.0, 0.0))
    dims = leaf.get('part_dims')
    x0, x1 = hx0 - px, hx1 - px
    if dims is not None:
        length, width = dims[0], dims[1]
        x0 = max(x0, ox)
        x1 = min(x1, ox + width)
    x0 += margin
    x1 -= margin
    if max_w is not None and x1 - x0 > max_w:
        c = (x0 + x1) / 2.0
        x0, x1 = c - max_w / 2.0, c + max_w / 2.0
    z0, z1 = hz0 - pz, hz1 - pz
    w, h = x1 - x0, z1 - z0
    if w < inch(2.0) or h < inch(1.0):
        return None
    # The back face of the front, pivot local.
    back = oy + inch(0.0625)
    d = inch(_f(params, 'rack_depth', _f(params, 'tray_depth', 4.0)))
    m = _Mesh()
    _BUILDERS[model](m, w, d, h, params)
    obj = m.to_object('%s Model' % (entry.get('name') or entry.get('code')))
    if obj is None:
        return None
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = pivot
    obj.location = (x0, back, z0)
    obj['hb_part_role'] = ROLE
    obj['IS_FACE_FRAME_INTERIOR_PART'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
    return obj
