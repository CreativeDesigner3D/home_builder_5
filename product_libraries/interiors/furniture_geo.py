"""Furniture: simple procedural models cut to their cages, each with a
flat plan symbol (outline and a few lines) for plan views.

A piece is a GeoNodeCage (types_furniture) standing like an appliance:
its back at y = 0, its front at y = -depth, the floor at z = 0. Its kind
and options are on the cage; each build replaces its parts and symbol,
children of the cage. A dining table's chairs, and a desk's, are its
own parts, laid out from its size round it.
"""

import math

import bmesh
import bpy

from ...units import inch
from ..common import appliance_geo as AG

FURNISHING_KEY = 'IS_FURNISHING'
KIND_KEY = 'FURNISHING_KIND'
PART_KEY = 'IS_FURNISHING_PART'
SYMBOL_KEY = 'IS_PLAN_SYMBOL'
BED_SIZES = {'TWIN': inch(39), 'FULL': inch(54), 'QUEEN': inch(60), 'KING': inch(76)}
SEAT_PER_SIDE = inch(30)            # a dining chair's share of a table's side
CHAIR_W, CHAIR_D, CHAIR_H = inch(18), inch(20), inch(34)
CHAIR_OUT = inch(4)                 # pulled out this far from the table's edge
LEG = inch(1.75)


# ---- Materials and parts -------------------------------------------------------------

def _wood():
    return AG._material('Furniture Wood', (0.42, 0.28, 0.17), 0.0, 0.45)


def _fabric():
    return AG._material('Furniture Fabric', (0.55, 0.53, 0.49), 0.0, 0.9)


def _bedding():
    return AG._material('Furniture Bedding', (0.93, 0.92, 0.89), 0.0, 0.9)


def _rug():
    return AG._material('Furniture Rug', (0.47, 0.36, 0.30), 0.0, 1.0)


def _dark():
    return AG._material('Furniture Metal', (0.12, 0.12, 0.12), 0.8, 0.35)


def _part(cage, name, bm, mat, smooth=False):
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    obj.parent = cage
    obj[PART_KEY] = True
    if cage.get('MENU_ID'):
        obj['MENU_ID'] = cage['MENU_ID']
    for coll in list(cage.users_collection) or [bpy.context.scene.collection]:
        coll.objects.link(obj)
    return obj


def _box(cage, name, x0, x1, y0, y1, z0, z1, mat, round_by=inch(0.25)):
    if x1 - x0 > 1e-4 and y1 - y0 > 1e-4 and z1 - z0 > 1e-4:
        _part(cage, name, AG._soft_box(x0, x1, y0, y1, z0, z1, round_by), mat, smooth=round_by > inch(0.5))


def _legs(cage, x0, x1, y0, y1, h, inset=inch(1.5), size=LEG, mat=None):
    for x in (x0 + inset, x1 - inset - size):
        for y in (y0 + inset, y1 - inset - size):
            _box(cage, "Leg", x, x + size, y, y + size, 0.0, h, mat or _wood(), inch(0.1))


class _Symbol:
    """Edges at the floor: the piece in plan."""

    def __init__(self):
        self.verts, self.edges = [], []

    def line(self, *pts):
        b = len(self.verts)
        self.verts.extend((x, y, inch(0.05)) for x, y in pts)
        self.edges.extend((b + i, b + i + 1) for i in range(len(pts) - 1))

    def rect(self, x0, y0, x1, y1):
        self.line((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))

    def circle(self, cx, cy, r, n=32):
        self.line(*[(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n))
                    for k in range(n + 1)])

    def make(self, cage):
        mesh = bpy.data.meshes.new("Plan Symbol")
        mesh.from_pydata(self.verts, self.edges, [])
        obj = bpy.data.objects.new("Plan Symbol", mesh)
        obj.parent = cage
        obj[PART_KEY] = True
        obj[SYMBOL_KEY] = True
        obj.hide_render = True
        for coll in list(cage.users_collection) or [bpy.context.scene.collection]:
            coll.objects.link(obj)
        return obj


# ---- Seating -----------------------------------------------------------------------

def _seating(cage, w, d, h, sym, seats, arms=True, x0=0.0, x1=None):
    """A sofa's or armchair's run from x0 to x1: a platform, arms, a back,
    seat and back cushions."""
    x1 = w if x1 is None else x1
    arm = inch(6) if arms else 0.0
    seat_z, back_d = inch(17), inch(9)
    fabric = _fabric()
    _box(cage, "Seat Base", x0, x1, -d, 0.0, inch(4), seat_z - inch(4), fabric, inch(1))
    if arms:
        for a, b in ((x0, x0 + arm), (x1 - arm, x1)):
            _box(cage, "Arm", a, b, -d, 0.0, inch(4), inch(25), fabric, inch(2))
    _box(cage, "Back", x0 + arm, x1 - arm, -back_d, 0.0, seat_z - inch(4), h, fabric, inch(2))
    run = (x1 - x0 - 2 * arm) / seats
    for k in range(seats):
        a = x0 + arm + k * run
        _box(cage, "Seat Cushion", a + inch(0.25), a + run - inch(0.25), -d + inch(1), -back_d,
             seat_z - inch(4), seat_z + inch(1), fabric, inch(2))
        _box(cage, "Back Cushion", a + inch(0.5), a + run - inch(0.5), -back_d - inch(5), -back_d,
             seat_z + inch(1), h - inch(3), fabric, inch(2.5))
        sym.line((a, -d), (a, -back_d))
    _legs(cage, x0, x1, -d, 0.0, inch(4), size=inch(1.5), mat=_dark())
    sym.rect(x0, -d, x1, 0.0)
    sym.line((x0 + arm, -back_d), (x1 - arm, -back_d))
    if arms:
        sym.line((x0 + arm, -d), (x0 + arm, 0.0))
        sym.line((x1 - arm, -d), (x1 - arm, 0.0))


def _build_sofa(cage, w, d, h, opts, sym):
    _seating(cage, w, d, h, sym, max(1, min(4, round(w / inch(28)))))


def _build_armchair(cage, w, d, h, opts, sym):
    _seating(cage, w, d, h, sym, 1)


def _build_sectional(cage, w, d, h, opts, sym):
    """A sofa along the back and a return coming forward at one end."""
    seat_d = inch(36)
    left = opts.get('side', 'LEFT') == 'LEFT'
    # The return, its back against the side
    rx0, rx1 = (0.0, seat_d) if left else (w - seat_d, w)
    main0, main1 = (seat_d, w) if left else (0.0, w - seat_d)
    _seating(cage, w, seat_d, h, sym, max(1, round((main1 - main0) / inch(30))), arms=False,
             x0=main0, x1=main1)
    fabric = _fabric()
    _box(cage, "Return Base", rx0, rx1, -d, 0.0, inch(4), inch(13), fabric, inch(1))
    _box(cage, "Return Cushion", rx0 + inch(0.5), rx1 - inch(0.5), -d + inch(1), -inch(9),
         inch(13), inch(18), fabric, inch(2))
    _box(cage, "Return Back", rx0, rx1, -inch(9), 0.0, inch(13), h, fabric, inch(2))
    back_x = (rx0, rx0 + inch(6)) if left else (rx1 - inch(6), rx1)
    _box(cage, "Return Arm", back_x[0], back_x[1], -d, -inch(9), inch(4), inch(25), fabric, inch(2))
    sym.rect(rx0, -d, rx1, 0.0)


# ---- Bedroom -----------------------------------------------------------------------

def _build_bed(cage, w, d, h, opts, sym):
    head_t = inch(2.5)
    wood, bedding = _wood(), _bedding()
    _box(cage, "Headboard", 0.0, w, -head_t, 0.0, 0.0, h, wood, inch(0.5))
    _box(cage, "Bed Base", inch(0.5), w - inch(0.5), -d, -head_t, inch(4), inch(14), wood, inch(0.5))
    _box(cage, "Mattress", inch(1), w - inch(1), -d + inch(0.5), -head_t, inch(14), inch(24), bedding, inch(2))
    _box(cage, "Duvet", inch(0.5), w - inch(0.5), -d, -head_t - inch(22), inch(20), inch(25),
         AG._material('Furniture Duvet', (0.58, 0.64, 0.70), 0.0, 0.95), inch(2))
    n = 2 if w > inch(45) else 1
    pw = (w - inch(6)) / n
    for k in range(n):
        a = inch(3) + k * pw
        _box(cage, "Pillow", a + inch(1), a + pw - inch(1), -head_t - inch(19), -head_t - inch(2),
             inch(24), inch(29), bedding, inch(2.5))
        sym.rect(a + inch(1), -head_t - inch(19), a + pw - inch(1), -head_t - inch(2))
    _legs(cage, inch(0.5), w - inch(0.5), -d, -head_t, inch(4), size=inch(2))
    sym.rect(0.0, -d, w, 0.0)
    sym.line((0.0, -head_t - inch(22)), (w, -head_t - inch(22)))


def _case(cage, w, d, h, sym, rows, cols, legs=inch(4)):
    """A case of drawers: carcass, top, drawer fronts in rows and columns."""
    wood = _wood()
    pull = inch(0.6)                # the pulls stand this far out: the fronts are set back by it
    face = -d + pull
    _box(cage, "Case", 0.0, w, face + inch(0.75), 0.0, legs, h - inch(1), wood, inch(0.2))
    _box(cage, "Top", -inch(0.5), w + inch(0.5), -d, 0.0, h - inch(1), h, wood, inch(0.25))
    fh = (h - inch(1) - legs) / rows
    fw = w / cols
    for r in range(rows):
        for c in range(cols):
            x0, z0 = c * fw, legs + r * fh
            _box(cage, "Drawer", x0 + inch(0.15), x0 + fw - inch(0.15), face, face + inch(0.75),
                 z0 + inch(0.15), z0 + fh - inch(0.15), wood, inch(0.15))
            cx, cz = x0 + fw / 2.0, z0 + fh / 2.0
            _box(cage, "Pull", cx - inch(1.5), cx + inch(1.5), -d, face,
                 cz - inch(0.25), cz + inch(0.25), _dark(), inch(0.1))
    _legs(cage, 0.0, w, face + inch(0.75), 0.0, legs, inset=inch(0.5))
    sym.rect(-inch(0.5), -d, w + inch(0.5), 0.0)


def _build_nightstand(cage, w, d, h, opts, sym):
    _case(cage, w, d, h, sym, 2, 1)


def _build_dresser(cage, w, d, h, opts, sym):
    _case(cage, w, d, h, sym, 3, 2 if w > inch(40) else 1)


def _build_tv_console(cage, w, d, h, opts, sym):
    _case(cage, w, d, h, sym, 1, max(2, round(w / inch(22))), legs=inch(6))


def _build_bookcase(cage, w, d, h, opts, sym):
    wood, t = _wood(), inch(0.75)
    for a, b in ((0.0, t), (w - t, w)):
        _box(cage, "Side", a, b, -d, 0.0, 0.0, h, wood, inch(0.1))
    _box(cage, "Back", t, w - t, -inch(0.5), 0.0, 0.0, h, wood, inch(0.05))
    shelves = max(2, round(h / inch(13)))
    for k in range(shelves + 1):
        z = inch(3) + k * (h - inch(3) - t) / shelves
        _box(cage, "Shelf", t, w - t, -d, -inch(0.5), z, z + t, wood, inch(0.05))
    _box(cage, "Toe", t, w - t, -d + inch(1), -inch(0.5), 0.0, inch(3), wood, inch(0.05))
    sym.rect(0.0, -d, w, 0.0)


# ---- Tables -------------------------------------------------------------------------

def _table(cage, w, d, h, sym, round_top=False):
    wood = _wood()
    top = inch(1.25)
    if round_top:
        r = min(w, d) / 2.0
        _part(cage, "Table Top", AG._oval_solid([(r, h - top), (r, h), (0.001, h)], w / 2.0, -d / 2.0,
                                                 1.0, (d / 2.0) / r if r else 1.0, 48), wood, smooth=True)
        _part(cage, "Pedestal", AG._oval_solid([(inch(9), 0.0), (inch(8), inch(1.5)), (inch(2.5), inch(4)),
                                                (inch(2.5), h - top), (0.001, h - top)], w / 2.0, -d / 2.0,
                                               1.0, 1.0, 24), wood, smooth=True)
        sym.circle(w / 2.0, -d / 2.0, r)
        return
    _box(cage, "Table Top", 0.0, w, -d, 0.0, h - top, h, wood, inch(0.25))
    _box(cage, "Apron", inch(2), w - inch(2), -d + inch(2), -inch(2), h - top - inch(3.5), h - top, wood, inch(0.1))
    _legs(cage, 0.0, w, -d, 0.0, h - top, inset=inch(2), size=inch(2.25))
    sym.rect(0.0, -d, w, 0.0)


def _chair(cage, cx, cy, facing, sym):
    """A dining chair at (cx, cy) facing `facing` (radians; 0 faces -y)."""
    wood = _wood()
    c, s = math.cos(facing), math.sin(facing)

    def place(bm):
        for v in bm.verts:
            x, y = v.co.x, v.co.y
            v.co.x = cx + x * c - y * s
            v.co.y = cy + x * s + y * c
        return bm
    hw, hd = CHAIR_W / 2.0, CHAIR_D / 2.0
    _part(cage, "Chair Seat", place(AG._soft_box(-hw, hw, -hd, hd, inch(16), inch(18), inch(0.3))), wood)
    _part(cage, "Chair Back", place(AG._soft_box(-hw, hw, hd - inch(1), hd, inch(18), CHAIR_H, inch(0.3))), wood)
    for x in (-hw + inch(0.5), hw - inch(2)):
        for y in (-hd + inch(0.5), hd - inch(2)):
            _part(cage, "Chair Leg", place(AG._soft_box(x, x + inch(1.5), y, y + inch(1.5), 0.0, inch(16),
                                                        inch(0.1))), wood)
    pts = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd), (-hw, -hd)]
    sym.line(*[(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts])


def chair_count(w, d, shape, asked=0):
    """How many chairs a dining table seats: as asked, or a chair per 30"
    of each long side and one at each end (round: one per 24" round)."""
    if asked > 0:
        return asked
    if shape == 'ROUND':
        return max(2, int(math.pi * min(w, d) / inch(24)))
    per_side = max(1, int(max(w, d) / SEAT_PER_SIDE))
    return per_side * 2 + (2 if max(w, d) >= inch(60) else 0)


def _build_dining_table(cage, w, d, h, opts, sym):
    shape = opts.get('shape', 'RECT')
    _table(cage, w, d, h, sym, round_top=shape == 'ROUND')
    n = chair_count(w, d, shape, int(opts.get('chairs', 0)))
    cx, cy = w / 2.0, -d / 2.0
    if shape == 'ROUND':
        r = min(w, d) / 2.0 + CHAIR_D / 2.0 - inch(4)
        for k in range(n):
            a = 2.0 * math.pi * k / n
            _chair(cage, cx + r * math.cos(a), cy + r * math.sin(a), a - math.pi / 2.0, sym)
        return
    ends = 2 if (n % 2 == 0 and n >= 6 and max(w, d) >= inch(60)) else 0
    per_side = (n - ends) // 2
    along = w
    for k in range(per_side):
        x = along * (k + 0.5) / per_side
        _chair(cage, x, -d - CHAIR_D / 2.0 + CHAIR_OUT, math.pi, sym)
        _chair(cage, x, CHAIR_D / 2.0 - CHAIR_OUT, 0.0, sym)
    if ends:
        _chair(cage, -CHAIR_D / 2.0 + CHAIR_OUT, cy, math.pi / 2.0, sym)
        _chair(cage, w + CHAIR_D / 2.0 - CHAIR_OUT, cy, -math.pi / 2.0, sym)


def _build_coffee_table(cage, w, d, h, opts, sym):
    _table(cage, w, d, h, sym)


def _build_end_table(cage, w, d, h, opts, sym):
    _table(cage, w, d, h, sym)


def _build_desk(cage, w, d, h, opts, sym):
    wood = _wood()
    _box(cage, "Desk Top", 0.0, w, -d, 0.0, h - inch(1.25), h, wood, inch(0.25))
    _case(cage, min(inch(16), w * 0.3), d - inch(1), h - inch(1.25), _Symbol(), 3, 1, legs=inch(2))
    _legs(cage, 0.0, w, -d, 0.0, h - inch(1.25), inset=inch(1), size=inch(2))
    _chair(cage, w / 2.0, -d - CHAIR_D / 2.0 + CHAIR_OUT * 2, math.pi, sym)
    sym.rect(0.0, -d, w, 0.0)


def _build_rug(cage, w, d, h, opts, sym):
    _box(cage, "Rug", 0.0, w, -d, 0.0, 0.0, max(h, inch(0.25)), _rug(), inch(0.1))
    _box(cage, "Rug Border", inch(4), w - inch(4), -d + inch(4), -inch(4), 0.0, max(h, inch(0.25)) + inch(0.02),
         AG._material('Furniture Rug Field', (0.62, 0.52, 0.42), 0.0, 1.0), inch(0.05))
    sym.rect(0.0, -d, w, 0.0)
    sym.rect(inch(4), -d + inch(4), w - inch(4), -inch(4))


BUILDERS = {
    'BED': _build_bed, 'NIGHTSTAND': _build_nightstand, 'DRESSER': _build_dresser,
    'SOFA': _build_sofa, 'LOVESEAT': _build_sofa, 'SECTIONAL': _build_sectional,
    'ARMCHAIR': _build_armchair, 'COFFEE_TABLE': _build_coffee_table, 'END_TABLE': _build_end_table,
    'TV_CONSOLE': _build_tv_console, 'RUG': _build_rug,
    'DINING_TABLE': _build_dining_table, 'DESK': _build_desk, 'BOOKCASE': _build_bookcase,
}


def options(cage):
    return {'side': cage.get('FURNISHING_SIDE', 'LEFT'), 'shape': cage.get('FURNISHING_SHAPE', 'RECT'),
            'chairs': int(cage.get('FURNISHING_CHAIRS', 0))}


def clear(cage):
    for child in list(cage.children):
        if child.get(PART_KEY):
            mesh = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)


def build(cage):
    """Make a piece's model and plan symbol from its kind and size."""
    from ... import hb_types
    builder = BUILDERS.get(cage.get(KIND_KEY))
    if builder is None:
        return False
    clear(cage)
    c = hb_types.GeoNodeCage(cage)
    w, d, h = c.get_input('Dim X'), c.get_input('Dim Y'), c.get_input('Dim Z')
    sym = _Symbol()
    builder(cage, w, d, h, options(cage), sym)
    sym.make(cage)
    return True
