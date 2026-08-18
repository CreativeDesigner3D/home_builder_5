"""Light, code-built accessory models.

The accessory catalog names its models by file - "Rack Belt 14",
"Hook Coat" - and the prior library shipped those files as heavy
meshes: five thousand vertices for a belt rack, twelve thousand for
a hamper, and a separate file for every width. This module draws
the same items by code instead, from a parts census taken off those
files - every slide, rail, bracket and bag measured and put back at
its measured place - so they read the same on screen for a fraction
of the weight, and one builder covers every size.

The registry is keyed by the same model names the catalog uses, so
nothing above this file changes: a saved drawing still remembers
"Rack Belt 14", the catalog still offers it, and the loader simply
builds it rather than reading it off disk. A real installed model
file always wins - the builder only answers when no file is there.

Drawing conventions, the bought files' own:
  panel racks/hooks   origin on the panel face, reach running -X,
                      depth running back +Y, mounting line at z=0
  pull-outs           x centered on the opening, y=0 the front
                      running back, the chassis just under z=0 and
                      the wares hanging below or standing above
  boards and mirrors  standing up from z=0

BUILTIN_ITEMS is the catalog the library offers when no host add-on
is providing one: the same items in the same families with the same
clearances, under plain names, with no ordering data - size limits
and finishes belong to whoever sells the accessories.
"""

import math

import bmesh
import bpy
import mathutils

from . import accessory_shapes

_IN = 0.0254


# ---------------------------------------------------------------------------
# Materials: a small shared set, made once
# ---------------------------------------------------------------------------
def _mat(name, color, metallic, roughness):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes.get('Principled BSDF')
        if b is not None:
            b.inputs['Base Color'].default_value = (*color, 1.0)
            b.inputs['Metallic'].default_value = metallic
            b.inputs['Roughness'].default_value = roughness
        m.diffuse_color = (*color, 1.0)
    return m


def _metal():
    return _mat('Closet Accessory Metal', (0.42, 0.42, 0.43), 1.0, 0.35)


def _fabric():
    return _mat('Closet Accessory Fabric', (0.55, 0.53, 0.50), 0.0, 0.9)


def _board():
    return _mat('Closet Accessory Board', (0.82, 0.80, 0.77), 0.0, 0.6)


def _glass():
    return _mat('Closet Accessory Mirror', (0.75, 0.78, 0.80), 1.0, 0.05)


# The finishes an accessory is offered in, by the names the catalog
# uses. A built model starts in the shared neutral metal and fabric;
# apply_finish overrides them per instance, object-level, so every
# instance keeps sharing the one mesh.
_FINISH_SPECS = {
    'Chrome': ((0.80, 0.80, 0.82), 1.0, 0.08),
    'Black': ((0.03, 0.03, 0.03), 0.9, 0.45),
    'Slate': ((0.13, 0.14, 0.16), 0.9, 0.40),
    'Matte Nickel': ((0.44, 0.44, 0.42), 1.0, 0.45),
    'Matte Aluminum': ((0.55, 0.56, 0.58), 1.0, 0.45),
    'Matte Gold': ((0.60, 0.45, 0.18), 1.0, 0.40),
    'White': ((0.88, 0.88, 0.87), 0.2, 0.55),
}
_FABRIC_SPECS = {
    'Fabric Beach': ((0.72, 0.66, 0.55), 0.0, 0.9),
    'Fabric Slate': ((0.35, 0.37, 0.40), 0.0, 0.9),
    'Fabric Black': ((0.08, 0.08, 0.08), 0.0, 0.9),
}


def apply_finish(obj, color='', fabric=''):
    """Dress one instance in its chosen finish and fabric.

    The mesh keeps the shared neutral materials; the override rides
    the object's slots, so two instances of the one mesh can wear
    two finishes. Unknown or empty names leave the neutral in place."""
    if obj is None or obj.type != 'MESH' or obj.data is None:
        return
    fin = _FINISH_SPECS.get(color)
    fab = _FABRIC_SPECS.get(fabric)
    if fin is None and fab is None:
        return
    metal, fabric_mat = _metal(), _fabric()
    for i, mesh_mat in enumerate(obj.data.materials):
        if i >= len(obj.material_slots):
            break
        slot = obj.material_slots[i]
        if mesh_mat is metal and fin is not None:
            slot.link = 'OBJECT'
            slot.material = _mat('Closet Accessory ' + color, *fin)
        elif mesh_mat is fabric_mat and fab is not None:
            slot.link = 'OBJECT'
            slot.material = _mat('Closet Accessory ' + fabric, *fab)


# ---------------------------------------------------------------------------
# Mesh helpers. Every part is a box or a bar; the census says where.
# ---------------------------------------------------------------------------
class _Build:
    """One model under construction: geometry plus which of the
    shared materials each part wears."""

    def __init__(self):
        self.bm = bmesh.new()
        self.slots = []          # materials in slot order
        self.faces_by_slot = {}  # slot -> set of new faces

    def _slot(self, mat):
        if mat in self.slots:
            return self.slots.index(mat)
        self.slots.append(mat)
        return len(self.slots) - 1

    def _claim(self, slot, before):
        new = [f for f in self.bm.faces if f not in before]
        for f in new:
            f.material_index = slot

    def box(self, sx, sy, sz, x, y, z, mat=None):
        """An axis-aligned box with its MIN corner at (x, y, z)."""
        slot = self._slot(mat or _metal())
        before = set(self.bm.faces)
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        bmesh.ops.scale(self.bm, vec=(sx, sy, sz), verts=r['verts'])
        bmesh.ops.translate(self.bm, vec=(x + sx / 2.0, y + sy / 2.0,
                                          z + sz / 2.0),
                            verts=r['verts'])
        self._claim(slot, before)
        return r['verts']

    def bar(self, r, length, axis, x, y, z, segs=8, mat=None):
        """A round bar from (x, y, z) along one axis."""
        slot = self._slot(mat or _metal())
        before = set(self.bm.faces)
        res = bmesh.ops.create_cone(self.bm, cap_ends=True,
                                    segments=segs, radius1=r,
                                    radius2=r, depth=length)
        verts = res['verts']
        if axis == 'X':
            m = mathutils.Matrix.Rotation(math.radians(90), 4, 'Y')
            bmesh.ops.transform(self.bm, matrix=m, verts=verts)
        elif axis == 'Y':
            m = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
            bmesh.ops.transform(self.bm, matrix=m, verts=verts)
        off = {'X': (length / 2.0, 0, 0), 'Y': (0, length / 2.0, 0),
               'Z': (0, 0, length / 2.0)}[axis]
        bmesh.ops.translate(self.bm, vec=(x + off[0], y + off[1],
                                          z + off[2]), verts=verts)
        self._claim(slot, before)
        return verts

    def shape(self, name, x=0.0, y=0.0, z=0.0, mat=None):
        """One baked shape from the prior library's own meshes,
        placed at an offset - the cast curves code cannot fake."""
        slot = self._slot(mat or _metal())
        packed, faces = accessory_shapes.SHAPES[name]
        s = accessory_shapes.SCALE
        before = set(self.bm.faces)
        verts = []
        for i in range(0, len(packed), 3):
            verts.append(self.bm.verts.new(
                (packed[i] * s + x, packed[i + 1] * s + y,
                 packed[i + 2] * s + z)))
        for poly in faces:
            try:
                self.bm.faces.new([verts[i] for i in poly])
            except ValueError:
                pass
        self._claim(slot, before)
        return verts

    def open_box(self, sx, sy, sz, x, y, z, t, mat=None, bottom=True):
        """A thin-walled, open-topped box - a bin, a bag, a tray."""
        self.box(t, sy, sz, x, y, z, mat)
        self.box(t, sy, sz, x + sx - t, y, z, mat)
        self.box(sx - 2 * t, t, sz, x + t, y, z, mat)
        self.box(sx - 2 * t, t, sz, x + t, y + sy - t, z, mat)
        if bottom:
            self.box(sx - 2 * t, sy - 2 * t, t, x + t, y + t, z, mat)

    def done(self, name):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for m in self.slots:
            mesh.materials.append(m)
        obj = bpy.data.objects.new(name, mesh)
        return obj


# ---------------------------------------------------------------------------
# The shared pull-out chassis, measured off the bought files: slide
# housings tight to each side, an inner slide member, a cap at each
# front corner, and a cross rail at the front and the back.
# ---------------------------------------------------------------------------
def _chassis(b, w, d):
    hw = w / 2.0
    for sx in (-1, 1):
        # slide housing against the side
        x = -hw + 0.0048 if sx < 0 else hw - 0.0048 - 0.035
        b.box(0.035, d - 0.006, 0.068, x, 0.002, -0.055)
        # inner slide member
        x = -hw if sx < 0 else hw - 0.032
        b.box(0.032, 0.257, 0.060, x, 0.012, -0.049)
        # front cap
        x = -hw + 0.004 if sx < 0 else hw - 0.004 - 0.037
        b.box(0.037, 0.003, 0.071, x, 0.0, -0.057)
    rail_w = w - 0.08
    b.box(rail_w, 0.020, 0.036, -rail_w / 2.0, 0.004, -0.054)
    b.box(rail_w, 0.020, 0.036, -rail_w / 2.0, d - 0.030, -0.054)
    return rail_w


def _chassis_slim(b, w, d):
    """The slimmer frame the pants rack and its hamper cousin ride:
    thin side slides and a light round-cornered rail pair."""
    hw = w / 2.0
    for sx in (-1, 1):
        x = -hw if sx < 0 else hw - 0.013
        b.box(0.013, d - 0.006, 0.047, x, 0.005, -0.025)
        x = -hw + 0.003 if sx < 0 else hw - 0.003 - 0.021
        b.box(0.021, d - 0.001, 0.060, x, 0.0, -0.031)
    rail_w = w - 0.03
    b.box(rail_w, 0.022, 0.022, -rail_w / 2.0, 0.018, -0.011)
    b.box(rail_w, 0.022, 0.022, -rail_w / 2.0, d - 0.037, -0.011)
    return rail_w


def _dividers_for(w_in):
    """How many dividers a divided pull-out carries at a width: one
    at 18, two at 24, three at 30, four at 36."""
    return max(1, int(round((w_in - 12) / 6.0)))


# ---------------------------------------------------------------------------
# Opening pull-outs
# ---------------------------------------------------------------------------
def build_divided_drawer(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    # the deep box
    b.open_box(rail_w, d - 0.021, 0.190, -rail_w / 2.0, 0.010,
               -0.210, 0.009, _fabric())
    # dividers and their top clips
    n = _dividers_for(w_in)
    for i in range(n):
        x = -rail_w / 2.0 + rail_w * (i + 1) / (n + 1)
        b.box(0.009, d - 0.050, 0.170, x - 0.0045, 0.025, -0.203,
              _fabric())
        for y in (0.015, d - 0.031):
            b.box(0.041, 0.015, 0.050, x - 0.020, y, -0.105)
    return b.done('Divided Drawer %d' % w_in)


def build_folding_station(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    b.box(rail_w - 0.003, d - 0.052, 0.006, -(rail_w - 0.003) / 2.0,
          0.026, -0.033, _board())
    return b.done('Folding Station %d' % w_in)


def build_pullout_shelf(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    b.box(rail_w - 0.003, d - 0.052, 0.006, -(rail_w - 0.003) / 2.0,
          0.026, -0.053, _board())
    n = _dividers_for(w_in)
    for i in range(n):
        x = -rail_w / 2.0 + rail_w * (i + 1) / (n + 1)
        b.box(0.003, d - 0.051, 0.080, x - 0.0015, 0.025, -0.046)
        for y in (0.017, d - 0.038):
            b.box(0.041, 0.020, 0.025, x - 0.020, y, -0.045)
    return b.done('Pull Out Shelf %d' % w_in)


def build_jewelry_organizer(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    b.box(rail_w - 0.003, d - 0.052, 0.006, -(rail_w - 0.003) / 2.0,
          0.026, -0.053, _board())
    # the shallow felt tray, divided into small wells
    tw = rail_w - 0.001
    b.open_box(tw, d - 0.051, 0.024, -tw / 2.0, 0.025, -0.046,
               0.004, _fabric())
    cols = max(3, int(w_in / 5))
    for i in range(1, cols):
        x = -tw / 2.0 + tw * i / cols
        b.box(0.004, d - 0.059, 0.020, x - 0.002, 0.029, -0.046,
              _fabric())
    b.box(tw - 0.008, 0.004, 0.020, -tw / 2.0 + 0.004,
          (d - 0.051) / 2.0 + 0.025, -0.046, _fabric())
    return b.done('Jewelry Organizer %d' % w_in)


def build_lingerie_drawer(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    # the shallow open basket
    b.open_box(rail_w, d - 0.021, 0.130, -rail_w / 2.0, 0.010,
               -0.140, 0.004, _fabric())
    n = _dividers_for(w_in) + 1
    for i in range(n):
        x = -rail_w / 2.0 + rail_w * (i + 1) / (n + 1)
        b.box(0.009, d - 0.050, 0.071, x - 0.0045, 0.025, -0.106,
              _fabric())
        for y in (0.016, d - 0.031):
            b.box(0.041, 0.015, 0.050, x - 0.020, y, -0.105)
    return b.done('Lingerie Drawer %d' % w_in)


def build_hamper_engage(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    # the top rim rails the bags hang from
    b.box(rail_w, 0.013, 0.006, -rail_w / 2.0, 0.021, -0.020)
    b.box(rail_w, 0.013, 0.006, -rail_w / 2.0, d - 0.034, -0.020)
    # hanger rails across, and their brackets
    bag_w = (rail_w - 0.022) / 2.0
    xs = (-rail_w / 2.0 + 0.014, -0.019, 0.010,
          rail_w / 2.0 - 0.022)
    for x in xs[:4]:
        b.box(0.008, d - 0.013, 0.060, x, 0.007, -0.043)
    for x in (-rail_w / 2.0 + 0.011, -0.021, rail_w / 2.0 - 0.035):
        for y in (0.054, d - 0.111):
            b.box(0.014, 0.057, 0.085, x, y, -0.118)
    # two deep fabric bags
    for x0 in (-rail_w / 2.0 + 0.007, 0.004):
        b.open_box(bag_w, d - 0.077, 0.476, x0, 0.038, -0.511,
                   0.006, _fabric())
    return b.done('Pull Out Hamper %d' % w_in)


def build_hamper_synergy(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis_slim(b, w, d)
    bag_w = (rail_w - 0.024) / 2.0
    for x in (-rail_w / 2.0 + 0.018, 0.011, -0.020,
              rail_w / 2.0 - 0.026):
        b.box(0.008, d - 0.013, 0.061, x, 0.008, -0.021)
    for x0 in (-rail_w / 2.0 + 0.016, 0.009):
        b.open_box(bag_w, d - 0.073, 0.497, x0, 0.036, -0.507,
                   0.006, _fabric())
        # the stiff flat front the bag hangs behind
        b.box(bag_w, 0.004, 0.495, x0, d - 0.041, -0.507, _fabric())
    return b.done('Pull Out Hamper Synergy %d' % w_in)


def build_shoe_organizer(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis(b, w, d)
    # a third rail through the middle
    b.box(rail_w, 0.020, 0.036, -rail_w / 2.0, (d - 0.036) / 2.0,
          -0.054)
    # shoe cradles standing in two rows, an L of base and back
    per_row = max(5, int(round(rail_w / 0.0588)))
    pitch = rail_w / per_row
    for row_y in (0.012, d - 0.118):
        for i in range(per_row):
            x = -rail_w / 2.0 + pitch * (i + 0.5) - 0.0305
            b.box(0.061, 0.034, 0.020, x, row_y, -0.020)
            b.box(0.061, 0.008, 0.154, x, row_y + 0.026, -0.020)
    return b.done('Shoe Organizer %d' % w_in)


def build_pants_rack(w_in=24, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    rail_w = _chassis_slim(b, w, d)
    # the real blade profile, baked, repeated at the bought pitch
    blades = max(9, int(round((rail_w - 0.05) / 0.031)))
    pitch = (rail_w - 0.05) / blades
    for i in range(blades):
        x = -rail_w / 2.0 + 0.025 + pitch * (i + 0.5)
        b.shape('Pants Blade', x - 0.003, -0.094, -0.061)
    return b.done('Pull Out Pants Rack %d' % w_in)


def build_storage_box(w_in=18, d_in=14):
    w, d = w_in * _IN, d_in * _IN
    b = _Build()
    b.box(w - 0.024, d - 0.019, 0.184, -(w - 0.024) / 2.0,
          -(d - 0.019) / 2.0, 0.0, _fabric())
    b.box(w - 0.012, d - 0.012, 0.039, -(w - 0.012) / 2.0,
          -(d - 0.012) / 2.0, 0.150, _fabric())
    return b.done('Storage Box %d' % w_in)


def build_wire_basket(w=0.6096, h=0.2794, d=0.3556):
    """A vinyl-coated wire basket at the size it was made: a rim,
    corner posts, horizontal wire runs one to the inch down the
    sides, and floor wires one to the inch along the depth - the
    counts the prior library drove its rig by. Drawn from its own
    front-left-bottom corner, running back +Y."""
    b = _Build()
    t = 0.004
    # rim: a stouter frame around the mouth
    b.box(w, 0.006, 0.006, 0.0, 0.0, h - 0.006)
    b.box(w, 0.006, 0.006, 0.0, d - 0.006, h - 0.006)
    b.box(0.006, d - 0.012, 0.006, 0.0, 0.006, h - 0.006)
    b.box(0.006, d - 0.012, 0.006, w - 0.006, 0.006, h - 0.006)
    # corner posts
    for x in (0.001, w - 0.005):
        for y in (0.001, d - 0.005):
            b.box(t, t, h - 0.006, x, y, 0.0)
    # horizontal wire runs, one to the inch of height
    runs = max(2, int(round(h / _IN)) - 1)
    for i in range(runs):
        z = h * (i + 0.5) / (runs + 0.5) - 0.004
        b.box(w, t, t, 0.0, 0.0, z)
        b.box(w, t, t, 0.0, d - t, z)
        b.box(t, d - 2 * t, t, 0.0, t, z)
        b.box(t, d - 2 * t, t, w - t, t, z)
    # a few uprights steadying the long faces
    ups = max(3, int(round(w / (3 * _IN))))
    for i in range(ups):
        x = w * (i + 0.5) / ups - t / 2.0
        b.box(t, t, h - 0.008, x, 0.0, 0.0)
        b.box(t, t, h - 0.008, x, d - t, 0.0)
    # floor wires, one to the inch of depth
    floor = max(2, int(round(d / _IN)))
    for i in range(floor):
        y = d * (i + 0.5) / floor - t / 2.0
        b.box(w - 2 * t, t, t, t, y, 0.0)
    return b.done('Wire Basket')


def build_wardrobe_lift(w=0.65):
    """The pull-down rod on its spring arms, drawn at rest."""
    b = _Build()
    for x in (0.0, w - 0.058):
        b.box(0.043, 0.147, 0.256, x - w / 2.0, -0.074, 0.0)
        b.box(0.009, 0.038, 0.771, x - w / 2.0 + 0.019, -0.016,
              0.059)
        b.box(0.025, 0.018, 0.031, x - w / 2.0 + 0.022, -0.006,
              0.797)
    b.bar(0.008, w - 0.066, 'X', -w / 2.0 + 0.023, 0.003, 0.819)
    b.box(0.042, 0.042, 0.823, -0.021, -0.018, -0.008)
    b.box(0.019, 0.019, 0.037, -0.010, -0.007, 0.784)
    return b.done('Wardrobe Lift')


# ---------------------------------------------------------------------------
# Panel racks: a track on the panel, a sliding arm, the wares
# ---------------------------------------------------------------------------
def _rack_base(b, d):
    b.box(0.010, d - 0.014, 0.030, -0.010, 0.005, -0.015)
    b.box(0.026, d - 0.013, 0.045, -0.029, 0.004, -0.022)
    for y in (0.0, d - 0.009):
        b.box(0.031, 0.005, 0.048, -0.034, y, -0.025)


def build_belt_rack(depth_in=14):
    """The prior library's own rack, baked whole - the turned pegs
    are its character, and turning is not a thing boxes do."""
    b = _Build()
    b.shape('Rack Belt %d' % depth_in)
    return b.done('Belt Rack %d' % depth_in)


def build_tie_rack(depth_in=14):
    d = depth_in * _IN
    b = _Build()
    _rack_base(b, d)
    b.bar(0.005, d - 0.055, 'Y', -0.060, 0.024, -0.032)
    pegs = max(8, int(depth_in / 1.5))
    for i in range(pegs):
        y = 0.026 + (d - 0.058) * i / max(pegs - 1, 1)
        b.bar(0.0035, 0.030, 'X', -0.062, y, -0.037, segs=6)
    return b.done('Tie Rack %d' % depth_in)


def build_scarf_rack(depth_in=14):
    """Baked whole, like the belt rack - its hanging rings would
    read as anything but rings out of primitives."""
    b = _Build()
    b.shape('Rack Scarf %d' % depth_in)
    return b.done('Scarf Rack %d' % depth_in)


def build_valet_rod(depth_in=14):
    d = depth_in * _IN
    b = _Build()
    b.box(0.024, d - 0.012, 0.045, -0.023, 0.011, -0.022)
    b.box(0.028, 0.005, 0.048, -0.028, 0.010, -0.023)
    b.box(0.014, d - 0.007, 0.019, -0.021, 0.006, -0.009)
    b.box(0.017, 0.010, 0.044, -0.023, 0.0, -0.021)
    return b.done('Valet Rod %d' % depth_in)


def build_valet_pin():
    b = _Build()
    b.bar(0.0095, 0.008, 'Y', 0.0, -0.008, 0.0, segs=10)
    b.bar(0.006, 0.004, 'Y', 0.0, -0.010, 0.0, segs=8)
    return b.done('Valet Pin')


# ---------------------------------------------------------------------------
# Hooks: the prior library's own castings, baked and thinned. A
# hook's whole character is its curves; these keep them.
# ---------------------------------------------------------------------------
def _hook(name):
    b = _Build()
    b.shape(name)
    return b.done(name)


def build_hook_belt():
    return _hook('Hook Belt')


def build_hook_broom():
    return _hook('Hook Broom')


def build_hook_coat():
    return _hook('Hook Coat')


def build_hook_double():
    return _hook('Hook Double')


def build_hook_tie():
    return _hook('Hook Tie')


def build_hook_waterfall():
    return _hook('Hook Waterfall')


# ---------------------------------------------------------------------------
# Ironing boards and mirrors, standing up from their mount
# ---------------------------------------------------------------------------
def build_ironing_swivel():
    b = _Build()
    b.box(0.061, 0.349, 0.261, -0.061, 0.001, 0.118)
    b.box(0.020, 0.245, 0.654, -0.106, 0.027, 0.026)
    for z in (0.0, 0.481):
        b.box(0.028, 0.298, 0.481, -0.087, 0.001, z, _board())
    return b.done('Ironing Board Swivel')


def build_ironing_popup():
    b = _Build()
    b.box(0.058, 0.344, 0.398, -0.058, 0.007, 0.290)
    b.box(0.028, 0.298, 0.340, -0.095, 0.007, -0.032, _board())
    b.box(0.029, 0.254, 0.443, -0.090, 0.023, 0.267)
    b.box(0.028, 0.298, 0.622, -0.095, 0.007, 0.307, _board())
    b.box(0.020, 0.349, 0.402, -0.061, 0.001, 0.288)
    return b.done('Ironing Board Pop-Up')


def build_ironing_shelf_mount():
    b = _Build()
    b.box(0.261, 0.349, 0.061, -0.131, 0.001, 0.0)
    b.box(0.483, 0.298, 0.060, -0.248, 0.001, 0.067, _board())
    b.box(0.301, 0.254, 0.029, -0.151, 0.023, 0.061)
    return b.done('Ironing Board Shelf Mount')


def build_mirror(h_in=35, rotates=False):
    h = 0.889 if h_in == 35 else 1.194
    b = _Build()
    x0 = -0.031 if rotates else -0.015
    b.box(0.015, 0.333, h, x0, 0.0, 0.0)
    b.box(0.004, 0.330, h - 0.003, x0 + 0.002, 0.002, 0.002,
          _glass())
    if rotates:
        b.box(0.034, 0.019, h * 0.53, -0.038, 0.0, h * 0.24)
        for z in (h * 0.26, h * 0.69):
            b.box(0.013, 0.334, 0.046, -0.013, 0.005, z)
    return b.done('Mirror %d%s' % (h_in, ' Rotation' if rotates
                                   else ''))


# ---------------------------------------------------------------------------
# The registry: model name -> how to draw it
# ---------------------------------------------------------------------------
def _sized(fn, **kw):
    return lambda: fn(**kw)


MODELS = {}
for _w in (18, 24, 30, 36):
    MODELS['Divided Drawer %d.blend' % _w] = \
        _sized(build_divided_drawer, w_in=_w)
    MODELS['Folding Station - Flat - %d x 14.blend' % _w] = \
        _sized(build_folding_station, w_in=_w)
    MODELS['Divided Pull Out Shelf %d x 14.blend' % _w] = \
        _sized(build_pullout_shelf, w_in=_w)
    MODELS['Pull Out Jewelry Organizer %d x 14.blend' % _w] = \
        _sized(build_jewelry_organizer, w_in=_w)
    MODELS['Pull Out Jewelry Organizer %d X 14.blend' % _w] = \
        _sized(build_jewelry_organizer, w_in=_w)
    MODELS['Pull Out Lingerie Drawer %d x 14.blend' % _w] = \
        _sized(build_lingerie_drawer, w_in=_w)
    MODELS['Pull Out Hamper Engage %d x 14.blend' % _w] = \
        _sized(build_hamper_engage, w_in=_w)
    MODELS['Pull Out Hamper Synergy %d.blend' % _w] = \
        _sized(build_hamper_synergy, w_in=_w)
    MODELS['Shoe Organizer %d x 14.blend' % _w] = \
        _sized(build_shoe_organizer, w_in=_w)
    MODELS['Pull Out Pants Rack %d.blend' % _w] = \
        _sized(build_pants_rack, w_in=_w)
for _w in (15, 18, 24):
    MODELS['Storage Box %d x 14.blend' % _w] = \
        _sized(build_storage_box, w_in=_w)
for _d in (12, 14, 18):
    MODELS['Rack Belt %d.blend' % _d] = _sized(build_belt_rack,
                                               depth_in=_d)
    MODELS['Rack Tie %d.blend' % _d] = _sized(build_tie_rack,
                                              depth_in=_d)
    MODELS['Rack Scarf %d.blend' % _d] = _sized(build_scarf_rack,
                                                depth_in=_d)
for _d in (12, 14):
    MODELS['Rack Valet %d.blend' % _d] = _sized(build_valet_rod,
                                                depth_in=_d)
MODELS.update({
    'Valet Pin.blend': build_valet_pin,
    'Hook Belt.blend': build_hook_belt,
    'Hook Broom.blend': build_hook_broom,
    'Hook Coat.blend': build_hook_coat,
    'Hook Double.blend': build_hook_double,
    'Hook Tie.blend': build_hook_tie,
    'Hook Waterfall.blend': build_hook_waterfall,
    'Ironing Board Panel Deluxe Swivel.blend': build_ironing_swivel,
    'Ironing Board Panel Premier Pop-Up.blend': build_ironing_popup,
    'Ironing Board Shelf Mount Sidelines Elite.blend':
        build_ironing_shelf_mount,
    'Mirror Fixed 35.blend': _sized(build_mirror, h_in=35),
    'Mirror Fixed 47.blend': _sized(build_mirror, h_in=47),
    'Mirror Full Rotation 35.blend': _sized(build_mirror, h_in=35,
                                            rotates=True),
    'Mirror Full Rotation 47.blend': _sized(build_mirror, h_in=47,
                                            rotates=True),
    'Wardrobe Lift.blend': build_wardrobe_lift,
    'Wire Basket.blend': build_wire_basket,
})

# The two that are made to a size given at placement rather than
# picked from a band: the basket to three chosen measures, the lift
# pulled out to the opening.
SIZED = {'Wire Basket.blend': build_wire_basket}
STRETCH = {'Wardrobe Lift.blend': build_wardrobe_lift}


def build_sized(name, w, h, d):
    """A model built to given measures, or None."""
    fn = SIZED.get(name)
    return fn(w=w, h=h, d=d) if fn is not None else None


def build_stretch(name, width):
    """A model built out to a width, or None."""
    fn = STRETCH.get(name)
    return fn(w=width) if fn is not None else None


def offers(name):
    """Whether this module can draw a model of that name."""
    return name in MODELS


def build(name):
    """A fresh, unlinked source object for a model name, or None.
    The loader caches it; instances share its mesh."""
    fn = MODELS.get(name)
    if fn is None:
        return None
    return fn()


# ---------------------------------------------------------------------------
# The catalog offered when nothing else is offering one. Families,
# clearances and drawing facts only - size limits and finishes
# belong to whoever sells the accessories.
# ---------------------------------------------------------------------------
def _hook_sizes():
    return [
        {'name': "Belt Hook", 'size': 0.0, 'model': 'Hook Belt.blend'},
        {'name': "Broom Hook", 'size': 0.0,
         'model': 'Hook Broom.blend'},
        {'name': "Coat Hook", 'size': 0.0, 'model': 'Hook Coat.blend'},
        {'name': "Double Hook", 'size': 0.0,
         'model': 'Hook Double.blend'},
        {'name': "Tie Hook", 'size': 0.0, 'model': 'Hook Tie.blend'},
        {'name': "Waterfall Hook", 'size': 0.0,
         'model': 'Hook Waterfall.blend'},
    ]


def _depth_sizes(stem, depths=(12, 14, 18)):
    return [{'name': '%d" Deep' % d, 'size': d * _IN,
             'model': '%s %d.blend' % (stem, d)} for d in depths]


def _width_sizes(pattern, widths=(18, 24, 30)):
    return [{'name': '%d" Wide' % w, 'size': w * _IN,
             'model': pattern % w} for w in widths]


BUILTIN_ITEMS = [
    # -- in the opening ---------------------------------------------------
    {'code': 'DIVIDED_DRAWER', 'name': "Divided Drawer",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.032, 'space_below': 0.235, 'ready': True,
     'sizes': _width_sizes('Divided Drawer %d.blend'),
     'description': "A lined drawer on runners, divided into "
                    "compartments"},
    {'code': 'FOLDING_STATION', 'name': "Folding Station",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.023, 'space_below': 0.096, 'ready': True,
     'sizes': _width_sizes('Folding Station - Flat - %d x 14.blend'),
     'description': "A pull-out board to fold on"},
    {'code': 'PULLOUT_SHELF', 'name': "Pull Out Shelf",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.055, 'space_below': 0.073, 'ready': True,
     'sizes': _width_sizes('Divided Pull Out Shelf %d x 14.blend'),
     'description': "A divided shelf on runners"},
    {'code': 'JEWELRY_ORGANIZER', 'name': "Jewelry Organizer",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.023, 'space_below': 0.064, 'ready': True,
     'sizes': _width_sizes('Pull Out Jewelry Organizer %d x '
                           '14.blend'),
     'description': "A shallow felt tray on runners"},
    {'code': 'LINGERIE_DRAWER', 'name': "Lingerie Drawer",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.023, 'space_below': 0.138, 'ready': True,
     'sizes': _width_sizes('Pull Out Lingerie Drawer %d x 14.blend'),
     'description': "A shallow divided basket on runners"},
    {'code': 'PULLOUT_HAMPER', 'name': "Pull Out Hamper",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.023, 'space_below': 0.568, 'ready': True,
     'sizes': _width_sizes('Pull Out Hamper Engage %d x 14.blend'),
     'description': "Fabric hamper bags hanging from a pull-out "
                    "frame"},
    {'code': 'SHOE_ORGANIZER', 'name': "Shoe Organizer",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.216, 'space_below': 0.152, 'ready': True,
     'sizes': _width_sizes('Shoe Organizer %d x 14.blend'),
     'description': "Shoes standing in rows on a pull-out"},
    {'code': 'SLIDING_PANTS_RACK', 'name': "Sliding Pants Rack",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'depth': 0.3556,
     'space_above': 0.023, 'space_below': 0.663, 'ready': True,
     'sizes': _width_sizes('Pull Out Pants Rack %d.blend'),
     'description': "Blades for hanging pants on a slide"},
    {'code': 'STORAGE_BOX', 'name': "Storage Box",
     'family': 'OPENING', 'band_axis': 'WIDTH', 'height': 0.189,
     'depth': 0.344, 'ready': True,
     'sizes': _width_sizes('Storage Box %d x 14.blend',
                           (15, 18, 24)),
     'description': "A lidded fabric box for a shelf"},
    # -- on a panel -------------------------------------------------------
    {'code': 'BELT_RACK', 'name': "Belt Rack", 'family': 'PANEL',
     'band_axis': 'DEPTH', 'sizes': _depth_sizes('Rack Belt'),
     'ready': True,
     'description': "Pegs along a sliding arm on the panel"},
    {'code': 'TIE_RACK', 'name': "Tie Rack", 'family': 'PANEL',
     'band_axis': 'DEPTH', 'sizes': _depth_sizes('Rack Tie'),
     'ready': True,
     'description': "Close-set pegs along a sliding arm"},
    {'code': 'SCARF_RACK', 'name': "Scarf Rack", 'family': 'PANEL',
     'band_axis': 'DEPTH', 'sizes': _depth_sizes('Rack Scarf'),
     'ready': True,
     'description': "Hanging loops along a sliding arm"},
    {'code': 'VALET_ROD', 'name': "Valet Rod", 'family': 'PANEL',
     'band_axis': 'DEPTH',
     'sizes': _depth_sizes('Rack Valet', (12, 14)), 'ready': True,
     'description': "A pull-out rod for the next day's clothes"},
    {'code': 'VALET_PIN', 'name': "Valet Pin", 'family': 'PANEL',
     'model': 'Valet Pin.blend', 'depth': 0.009, 'ready': True,
     'description': "A knob on the panel to hang a hanger from"},
    {'code': 'HOOKS', 'name': "Hooks", 'family': 'PANEL',
     'band_axis': 'STYLE', 'sizes': _hook_sizes(), 'depth': 0.046,
     'ready': True, 'description': "A hook on the panel face"},
    {'code': 'IRONING_BOARD', 'name': "Ironing Board",
     'family': 'PANEL', 'band_axis': 'STYLE', 'depth': 0.351,
     'ready': True,
     'sizes': [
         {'name': "Swivel", 'size': 0.0,
          'model': 'Ironing Board Panel Deluxe Swivel.blend'},
         {'name': "Pop-Up", 'size': 0.0,
          'model': 'Ironing Board Panel Premier Pop-Up.blend'}],
     'description': "A fold-away ironing board on the panel"},
    {'code': 'MIRROR', 'name': "Mirror", 'family': 'PANEL',
     'band_axis': 'STYLE', 'depth': 0.340, 'ready': True,
     'sizes': [
         {'name': 'Fixed 35"', 'size': 0.0,
          'model': 'Mirror Fixed 35.blend'},
         {'name': 'Fixed 47"', 'size': 0.0,
          'model': 'Mirror Fixed 47.blend'},
         {'name': 'Full Rotation 35"', 'size': 0.0,
          'model': 'Mirror Full Rotation 35.blend'},
         {'name': 'Full Rotation 47"', 'size': 0.0,
          'model': 'Mirror Full Rotation 47.blend'}],
     'description': "A dressing mirror on the panel"},
    # -- on a cleat, and in an opening on a shelf -------------------------
    {'code': 'CLEAT_HOOKS', 'name': "Cleat Hooks", 'family': 'CLEAT',
     'band_axis': 'STYLE', 'sizes': _hook_sizes(), 'depth': 0.046,
     'ready': True,
     'description': "A board with a row of hooks along it"},
    {'code': 'IRONING_BOARD_DRAWER', 'name': "Ironing Board Drawer",
     'family': 'INSERT', 'width': 0.305, 'height': 0.127,
     'depth': 0.346, 'ready': True,
     'model': 'Ironing Board Shelf Mount Sidelines Elite.blend',
     'description': "An ironing board folding out of a drawer"},
]
