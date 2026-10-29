"""Obstacles as models: what an outlet, switch, vent, light or fan looks
like, made within the size the obstacle is given.

Most are built in the obstacle's own frame - u across its face, v up it,
n out from the surface it is on (0 against it) - then turned onto the
axes the obstacle mesh has always used for that surface: a wall item
faces +y with z up, a ceiling item faces down, a floor item faces up.
The mesh stays centred in the box that placement and editing size it
by, so a thin plate on a deep box (a recessed light's trim, a register)
sits against the surface with the rest of the depth left empty.

Pipes, columns, beams and the custom shapes are built straight on the
mesh's axes, as they were.
"""

import math

import bmesh
import bpy
from mathutils import Matrix

from .units import inch


# ---- Materials ------------------------------------------------------------------------

# key: (name, colour, metallic, roughness)
MATERIALS = {
    'plate': ("Obstacle Plastic", (0.92, 0.91, 0.88), 0.0, 0.35),
    'slot': ("Obstacle Slot", (0.03, 0.03, 0.03), 0.0, 0.6),
    'metal': ("Obstacle Metal", (0.72, 0.72, 0.72), 1.0, 0.3),
    'grille': ("Obstacle Grille", (0.88, 0.88, 0.86), 0.3, 0.4),
    'dark': ("Obstacle Dark Metal", (0.2, 0.19, 0.18), 0.8, 0.4),
    'brass': ("Obstacle Brass", (0.72, 0.55, 0.28), 1.0, 0.3),
    'red': ("Obstacle Red", (0.7, 0.06, 0.05), 0.0, 0.4),
    'wood': ("Obstacle Wood", (0.45, 0.31, 0.19), 0.0, 0.5),
    'pipe': ("Obstacle Pipe", (0.85, 0.84, 0.8), 0.0, 0.4),
    'screen': ("Obstacle Screen", (0.06, 0.08, 0.1), 0.0, 0.15),
    'custom': ("Obstacle", (0.8, 0.6, 0.4), 0.0, 0.5),
    'light': ("Obstacle Light", (1.0, 0.95, 0.85), 0.0, 0.3),
}
EMISSIVE = {'light': 3.0}


def material(key):
    from .product_libraries.common import appliance_geo as AG
    name, color, metallic, roughness = MATERIALS[key]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = AG._material(name, color, metallic, roughness)
    mat.diffuse_color = (*color, 1.0)
    if key in EMISSIVE:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = EMISSIVE[key]
    return mat


# ---- Building ---------------------------------------------------------------------------

class _B:
    """A bmesh of boxes and cylinders, each part painted with a material
    key."""

    def __init__(self):
        self.bm = bmesh.new()
        self.keys = []

    def _paint(self, verts, key):
        if key not in self.keys:
            self.keys.append(key)
        i = self.keys.index(key)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = i

    def box(self, u0, u1, v0, v1, n0, n1, key, turn=0.0):
        """An axis box; `turn` spins it about n through the origin."""
        if min(u1 - u0, v1 - v0, n1 - n0) <= 1e-6:
            return
        m = (Matrix.Translation(((u0 + u1) / 2, (v0 + v1) / 2, (n0 + n1) / 2))
             @ Matrix.Diagonal((u1 - u0, v1 - v0, n1 - n0, 1.0)))
        if turn:
            m = Matrix.Rotation(turn, 4, 'Z') @ m
        self._paint(bmesh.ops.create_cube(self.bm, size=1.0, matrix=m)['verts'], key)

    def cyl(self, cu, cv, r, n0, n1, key, r2=None, segments=24, rot=None):
        """A cylinder (or cone, to r2) along n, from n0 to n1; `rot`
        turns it about the origin after."""
        if n1 - n0 <= 1e-6 or r <= 1e-6:
            return
        m = Matrix.Translation((cu, cv, (n0 + n1) / 2))
        if rot is not None:
            m = rot @ m
        verts = bmesh.ops.create_cone(
            self.bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=r, radius2=r if r2 is None else max(r2, 1e-5),
            depth=n1 - n0, matrix=m)['verts']
        self._paint(verts, key)

    def finish(self, mesh, frame, depth):
        """Turn the frame onto the mesh's axes and write it out."""
        if frame == 'WALL':        # x = u, y = n - d/2, z = v
            m = Matrix(((1, 0, 0, 0), (0, 0, 1, -depth / 2), (0, 1, 0, 0), (0, 0, 0, 1)))
        elif frame == 'CEILING':   # z = d/2 - n
            m = Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, depth / 2), (0, 0, 0, 1)))
        elif frame == 'FLOOR':     # z = n - d/2
            m = Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, -depth / 2), (0, 0, 0, 1)))
        else:                      # already on the mesh's axes
            m = Matrix.Identity(4)
        bm = self.bm
        bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
        if m.determinant() < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.normal_update()
        # Slots first: clearing them after would put every face on slot 0
        mesh.materials.clear()
        for key in self.keys:
            mesh.materials.append(material(key))
        bm.to_mesh(mesh)
        bm.free()


def _frame(b, u0, u1, v0, v1, n0, n1, f, key):
    """A rectangular frame f wide, open in the middle."""
    b.box(u0, u1, v1 - f, v1, n0, n1, key)
    b.box(u0, u1, v0, v0 + f, n0, n1, key)
    b.box(u0, u0 + f, v0 + f, v1 - f, n0, n1, key)
    b.box(u1 - f, u1, v0 + f, v1 - f, n0, n1, key)


def _gangs(W, H, nominal_w=inch(2.75), nominal_h=inch(4.5)):
    """How many devices side by side, and the size of one nominal inch."""
    gangs = max(1, round(W / inch(2.25 if W > inch(3.5) else 2.75)))
    gangs = min(gangs, 4)
    s = inch(1) * min(W / gangs / nominal_w, H / nominal_h)
    return gangs, s


def _centres(W, gangs):
    step = W / gangs
    return [-W / 2 + step * (i + 0.5) for i in range(gangs)]


# ---- Wall items -------------------------------------------------------------------------

def _plate(b, W, H, D):
    t = min(D, inch(0.2))
    b.box(-W / 2, W / 2, -H / 2, H / 2, 0.0, t, 'plate')
    return t


def _receptacle(b, cu, cv, s, n):
    """One receptacle face: two slots and the ground hole."""
    b.box(cu - 0.68 * s, cu + 0.68 * s, cv - 0.55 * s, cv + 0.55 * s, n, n + 0.08 * s, 'plate')
    top = n + 0.085 * s
    for du, tall in ((-0.25, 0.30), (0.25, 0.24)):
        b.box(cu + (du - 0.035) * s, cu + (du + 0.035) * s,
              cv + (0.1 - tall / 2) * s, cv + (0.1 + tall / 2) * s, n + 0.05 * s, top, 'slot')
    b.cyl(cu, cv - 0.28 * s, 0.08 * s, n + 0.05 * s, top, 'slot', segments=12)


def _outlet(b, W, H, D, gfci=False):
    t = _plate(b, W, H, D)
    gangs, s = _gangs(W, H)
    for cu in _centres(W, gangs):
        if gfci:
            b.box(cu - 0.66 * s, cu + 0.66 * s, -1.3 * s, 1.3 * s, t, t + 0.06 * s, 'plate')
            n = t + 0.06 * s
            for cv in (0.78, -0.78):
                b.box(cu - 0.35 * s, cu + 0.35 * s, cv * s - 0.22 * s, cv * s + 0.22 * s, n - 0.01 * s, n + 0.04 * s, 'plate')
                for du in (-0.18, 0.18):
                    b.box(cu + (du - 0.03) * s, cu + (du + 0.03) * s, cv * s - 0.12 * s, cv * s + 0.12 * s,
                          n, n + 0.045 * s, 'slot')
            b.box(cu - 0.42 * s, cu - 0.06 * s, -0.12 * s, 0.12 * s, n, n + 0.08 * s, 'slot')
            b.box(cu + 0.06 * s, cu + 0.42 * s, -0.12 * s, 0.12 * s, n, n + 0.08 * s, 'red')
        else:
            for cv in (0.78, -0.78):
                _receptacle(b, cu, cv * s, s, t)


def _switch(b, W, H, D, dimmer=False):
    t = _plate(b, W, H, D)
    gangs, s = _gangs(W, H)
    for cu in _centres(W, gangs):
        if dimmer:
            b.box(cu - 0.66 * s, cu + 0.66 * s, -1.3 * s, 1.3 * s, t, t + 0.05 * s, 'plate')
            b.box(cu - 0.6 * s, cu + 0.3 * s, -1.2 * s, 1.2 * s, t + 0.05 * s, t + 0.16 * s, 'plate')
            b.box(cu + 0.42 * s, cu + 0.5 * s, -1.0 * s, 1.0 * s, t + 0.05 * s, t + 0.07 * s, 'slot')
            b.box(cu + 0.38 * s, cu + 0.54 * s, 0.1 * s, 0.4 * s, t + 0.05 * s, t + 0.2 * s, 'plate')
        else:
            b.box(cu - 0.17 * s, cu + 0.17 * s, -0.47 * s, 0.47 * s, t, t + 0.04 * s, 'plate')
            b.box(cu - 0.1 * s, cu + 0.1 * s, 0.0, 0.3 * s, t + 0.04 * s, t + 0.38 * s, 'plate')


def _thermostat(b, W, H, D):
    body = max(min(D, inch(1.25)), inch(0.3))
    b.box(-W / 2, W / 2, -H / 2, H / 2, 0.0, body, 'plate')
    b.box(-W * 0.36, W * 0.36, H * 0.0, H * 0.36, body, body + inch(0.03), 'screen')
    for i in range(3):
        cu = (i - 1) * W * 0.25
        b.box(cu - W * 0.08, cu + W * 0.08, -H * 0.3, -H * 0.2, body, body + inch(0.06), 'plate')


def _register(b, W, H, D, key='grille', across=False):
    """A louvered register: a frame and slats over a dark back. `across`
    runs the slats up and down, the long way of a floor register."""
    t = min(D, inch(0.35))
    f = min(inch(0.75), min(W, H) * 0.15)
    _frame(b, -W / 2, W / 2, -H / 2, H / 2, 0.0, t, f, key)
    b.box(-W / 2 + f, W / 2 - f, -H / 2 + f, H / 2 - f, 0.0, inch(0.03), 'slot')
    if across:
        span = W - 2 * f
        count = max(2, int(span / inch(0.5)))
        step = span / count
        for i in range(count - 1):
            u = -W / 2 + f + step * (i + 1)
            b.box(u - inch(0.06), u + inch(0.06), -H / 2 + f, H / 2 - f, 0.0, t * 0.85, key)
    else:
        span = H - 2 * f
        count = max(2, int(span / inch(0.6)))
        step = span / count
        for i in range(count - 1):
            v = -H / 2 + f + step * (i + 1)
            b.box(-W / 2 + f, W / 2 - f, v - inch(0.08), v + inch(0.08), 0.0, t * 0.85, key)


def _return_grille(b, W, H, D):
    """A return: a frame over a grid."""
    t = min(D, inch(0.35))
    f = min(inch(1), min(W, H) * 0.1)
    _frame(b, -W / 2, W / 2, -H / 2, H / 2, 0.0, t, f, 'grille')
    b.box(-W / 2 + f, W / 2 - f, -H / 2 + f, H / 2 - f, 0.0, inch(0.03), 'slot')
    cell = inch(0.75)
    nu = max(2, int((W - 2 * f) / cell))
    nv = max(2, int((H - 2 * f) / cell))
    for i in range(1, nu):
        u = -W / 2 + f + (W - 2 * f) * i / nu
        b.box(u - inch(0.05), u + inch(0.05), -H / 2 + f, H / 2 - f, 0.0, t * 0.8, 'grille')
    for j in range(1, nv):
        v = -H / 2 + f + (H - 2 * f) * j / nv
        b.box(-W / 2 + f, W / 2 - f, v - inch(0.05), v + inch(0.05), 0.0, t * 0.8, 'grille')


def _access_panel(b, W, H, D):
    t = min(D, inch(0.4))
    f = min(inch(0.75), min(W, H) * 0.08)
    _frame(b, -W / 2, W / 2, -H / 2, H / 2, 0.0, t, f, 'plate')
    b.box(-W / 2 + f, W / 2 - f, -H / 2 + f, H / 2 - f, 0.0, t * 0.6, 'plate')
    b.cyl(W / 2 - f - inch(1), 0.0, inch(0.3), t * 0.6, t * 0.6 + inch(0.12), 'metal', segments=16)


def _data_outlet(b, W, H, D):
    t = _plate(b, W, H, D)
    gangs, s = _gangs(W, H)
    for cu in _centres(W, gangs):
        b.cyl(cu, 0.75 * s, 0.22 * s, t, t + 0.15 * s, 'metal', segments=16)
        b.cyl(cu, 0.75 * s, 0.08 * s, t + 0.15 * s, t + 0.4 * s, 'metal', segments=12)
        b.box(cu - 0.3 * s, cu + 0.3 * s, -1.0 * s, -0.5 * s, t, t + 0.06 * s, 'slot')


def _intercom(b, W, H, D):
    body = max(min(D, inch(0.8)), inch(0.2))
    b.box(-W / 2, W / 2, -H / 2, H / 2, 0.0, body, 'plate')
    # Speaker holes over the top half
    r = min(W, H) * 0.025
    for i in range(5):
        for j in range(4):
            u = (i - 2) * W * 0.13
            v = H * 0.12 + j * H * 0.08
            b.cyl(u, v, r, body - inch(0.02), body + inch(0.01), 'slot', segments=8)
    for i in range(3):
        u = (i - 1) * W * 0.25
        b.box(u - W * 0.08, u + W * 0.08, -H * 0.3, -H * 0.2, body, body + inch(0.08), 'slot')


def _fire_pull(b, W, H, D):
    body = max(min(D, inch(2.5)), inch(0.3))
    b.box(-W / 2, W / 2, -H / 2, H / 2, 0.0, body, 'red')
    b.box(-W * 0.36, W * 0.36, H * 0.02, H * 0.14, body, min(D, body + inch(0.4)) + inch(0.01), 'plate')
    b.box(-W * 0.3, W * 0.3, -H * 0.35, -H * 0.12, body, body + inch(0.02), 'plate')


# ---- Floor items ------------------------------------------------------------------------

def _floor_drain(b, W, H, D):
    r = W / 2
    t = min(D, inch(0.2))
    b.cyl(0, 0, r, 0.0, t, 'metal', segments=32)
    b.cyl(0, 0, r * 0.78, t - inch(0.02), t + inch(0.005), 'slot', segments=32)
    bars = 5
    for i in range(bars):
        v = (i - (bars - 1) / 2) * r * 0.3
        half = max((r * 0.78) ** 2 - v * v, 0.0) ** 0.5
        b.box(-half, half, v - r * 0.05, v + r * 0.05, t - inch(0.02), t + inch(0.01), 'metal')


def _floor_outlet(b, W, H, D):
    t = min(D, inch(0.3))
    b.box(-W / 2, W / 2, -H / 2, H / 2, 0.0, t, 'brass')
    cols = 2 if W > inch(5) else 1
    rows = 2
    r = min(W / cols, H / rows) * 0.33
    for i in range(cols):
        for j in range(rows):
            u = -W / 2 + W * (i + 0.5) / cols
            v = -H / 2 + H * (j + 0.5) / rows
            b.cyl(u, v, r, t, t + inch(0.05), 'brass', segments=20)
            b.box(u - r * 0.5, u + r * 0.5, v - r * 0.08, v + r * 0.08, t + inch(0.05), t + inch(0.06), 'slot')


# ---- Ceiling items ----------------------------------------------------------------------

def _recessed_light(b, W, H, D):
    r = W / 2
    b.cyl(0, 0, r, 0.0, inch(0.35), 'plate', segments=32)
    b.cyl(0, 0, r * 0.74, inch(0.05), inch(0.36), 'light', segments=32)


def _surface_light(b, W, H, D):
    r = min(W, H) / 2
    base = min(inch(0.5), D * 0.25)
    b.cyl(0, 0, r * 0.95, 0.0, base, 'metal', segments=32)
    b.cyl(0, 0, r * 0.9, base, D * 0.92, 'light', r2=r * 0.6, segments=32)
    b.cyl(0, 0, inch(0.35), D * 0.92, D, 'metal', segments=12)


def _ceiling_fan(b, W, H, D):
    r = W / 2
    canopy = min(inch(1.6), D * 0.15)
    b.cyl(0, 0, inch(2.6), 0.0, canopy, 'metal', r2=inch(2.0), segments=24)
    motor0, motor1 = max(D - inch(4.5), canopy + inch(0.5)), D - inch(1.8)
    b.cyl(0, 0, inch(0.35), canopy, motor0, 'metal', segments=12)
    b.cyl(0, 0, inch(3.6), motor0, motor1, 'metal', r2=inch(3.2), segments=32)
    # Five blades, from the motor out to the fan's width
    blade_w = min(inch(5.5), r * 0.25)
    n0 = motor0 + (motor1 - motor0) * 0.35
    for i in range(5):
        a = math.radians(i * 72)
        b.box(inch(3.0), r, -blade_w / 2, blade_w / 2, n0, n0 + inch(0.2), 'wood', turn=a)
        b.box(inch(2.4), inch(5.0), -inch(0.5), inch(0.5), n0 - inch(0.05), n0 + inch(0.3), 'metal', turn=a)
    b.cyl(0, 0, inch(3.0), motor1, D, 'light', r2=inch(2.0), segments=24)


def _ceiling_diffuser(b, W, H, D):
    """A square diffuser: frames stepping down to a centre plate."""
    t = min(D, inch(1.0))
    rings = 4
    for i in range(rings):
        k = 1.0 - i * 0.18
        f = min(W, H) * 0.06
        _frame(b, -W / 2 * k, W / 2 * k, -H / 2 * k, H / 2 * k,
               0.0, t * (0.3 + 0.7 * i / rings), f, 'grille')
    k = 1.0 - rings * 0.18
    b.box(-W / 2 * k, W / 2 * k, -H / 2 * k, H / 2 * k, 0.0, t, 'grille')
    b.box(-W / 2 * 0.95, W / 2 * 0.95, -H / 2 * 0.95, H / 2 * 0.95, 0.0, inch(0.03), 'slot')


def _detector(b, W, H, D, co=False):
    r = W / 2
    base = D * 0.45
    b.cyl(0, 0, r, 0.0, base, 'plate', segments=32)
    b.cyl(0, 0, r * 0.88, base, D, 'plate', r2=r * 0.55, segments=32)
    if co:
        b.box(-r * 0.3, r * 0.3, -r * 0.15, r * 0.15, D - inch(0.02), D + inch(0.01), 'screen')
    else:
        b.cyl(r * 0.25, r * 0.25, r * 0.06, D - inch(0.1), D + inch(0.01), 'red', segments=12)
        for i in range(6):
            a = math.radians(i * 60)
            b.box(r * 0.62, r * 0.82, -r * 0.03, r * 0.03, base - inch(0.01), base + inch(0.1), 'slot', turn=a)


def _sprinkler(b, W, H, D):
    r = W / 2
    b.cyl(0, 0, r, 0.0, inch(0.3), 'metal', segments=24)
    b.cyl(0, 0, inch(0.3), inch(0.3), D * 0.6, 'metal', segments=16)
    b.box(-inch(0.3), -inch(0.18), -inch(0.08), inch(0.08), D * 0.45, D * 0.8, 'metal')
    b.box(inch(0.18), inch(0.3), -inch(0.08), inch(0.08), D * 0.45, D * 0.8, 'metal')
    b.cyl(0, 0, inch(0.08), D * 0.6, D * 0.78, 'red', segments=8)
    b.cyl(0, 0, r * 0.65, D * 0.8, D * 0.84, 'metal', segments=24)


# ---- On the mesh's own axes -------------------------------------------------------------

def _raw(b, width, height, depth, obstacle_type, surface):
    flat = surface in ('FLOOR', 'CEILING')
    if obstacle_type == 'CUSTOM_CIRCLE':
        b.cyl(0, 0, width / 2, -depth / 2, depth / 2, 'custom', segments=16)
    elif obstacle_type == 'PIPE_HORIZONTAL':
        b.cyl(0, 0, height / 2, -width / 2, width / 2, 'pipe', segments=16,
              rot=Matrix.Rotation(math.pi / 2, 4, 'Y'))
        for x in (-width / 2 + inch(0.75), width / 2 - inch(0.75)):
            b.cyl(0, 0, height / 2 * 1.15, x - inch(0.5), x + inch(0.5), 'pipe', segments=16,
                  rot=Matrix.Rotation(math.pi / 2, 4, 'Y'))
    elif obstacle_type == 'PIPE_VERTICAL':
        b.cyl(0, 0, width / 2, -height / 2, height / 2, 'pipe', segments=16)
    elif obstacle_type == 'COLUMN':
        plinth = min(height * 0.06, inch(6))
        b.box(-width / 2, width / 2, -width / 2, width / 2, -height / 2, -height / 2 + plinth, 'plate')
        b.box(-width / 2, width / 2, -width / 2, width / 2, height / 2 - plinth, height / 2, 'plate')
        b.cyl(0, 0, width / 2 * 0.82, -height / 2 + plinth, height / 2 - plinth, 'plate', segments=32)
    elif obstacle_type == 'BEAM':
        if flat:
            b.box(-width / 2, width / 2, -height / 2, height / 2, -depth / 2, depth / 2, 'wood')
        else:
            b.box(-width / 2, width / 2, -depth / 2, depth / 2, -height / 2, height / 2, 'wood')
    elif flat:
        b.box(-width / 2, width / 2, -height / 2, height / 2, -depth / 2, depth / 2, 'custom')
    else:
        b.box(-width / 2, width / 2, -depth / 2, depth / 2, -height / 2, height / 2, 'custom')


MODELS = {
    'OUTLET_STANDARD': _outlet,
    'OUTLET_DOUBLE': _outlet,
    'OUTLET_GFCI': lambda b, W, H, D: _outlet(b, W, H, D, gfci=True),
    'SWITCH_SINGLE': _switch,
    'SWITCH_DOUBLE': _switch,
    'SWITCH_DIMMER': lambda b, W, H, D: _switch(b, W, H, D, dimmer=True),
    'THERMOSTAT': _thermostat,
    'VENT_WALL': _register,
    'VENT_WALL_LARGE': _register,
    'VENT_RETURN': _return_grille,
    'ACCESS_PANEL': _access_panel,
    'ACCESS_PANEL_LARGE': _access_panel,
    'CABLE_OUTLET': _data_outlet,
    'INTERCOM': _intercom,
    'FIRE_ALARM': _fire_pull,
    'VENT_FLOOR': lambda b, W, H, D: _register(b, W, H, D, key='dark', across=True),
    'VENT_FLOOR_LARGE': lambda b, W, H, D: _register(b, W, H, D, key='dark', across=True),
    'FLOOR_DRAIN': _floor_drain,
    'FLOOR_OUTLET': _floor_outlet,
    'FLOOR_BOX': _floor_outlet,
    'LIGHT_RECESSED': _recessed_light,
    'LIGHT_RECESSED_SMALL': _recessed_light,
    'LIGHT_SURFACE': _surface_light,
    'CEILING_FAN': _ceiling_fan,
    'CEILING_FAN_SMALL': _ceiling_fan,
    'VENT_CEILING': _ceiling_diffuser,
    'EXHAUST_FAN': lambda b, W, H, D: _register(b, W, W, D),
    'SMOKE_DETECTOR': _detector,
    'CO_DETECTOR': lambda b, W, H, D: _detector(b, W, H, D, co=True),
    'SPRINKLER': _sprinkler,
}

# Round ones are as wide as they are long
ROUND = {'FLOOR_DRAIN', 'LIGHT_RECESSED', 'LIGHT_RECESSED_SMALL', 'CEILING_FAN',
         'CEILING_FAN_SMALL', 'EXHAUST_FAN', 'SMOKE_DETECTOR', 'CO_DETECTOR', 'SPRINKLER'}


def build(mesh, width, height, depth, obstacle_type, surface='WALL'):
    """Fill `mesh` with the obstacle's model, centred on the origin."""
    b = _B()
    model = MODELS.get(obstacle_type)
    if model is None:
        _raw(b, width, height, depth, obstacle_type, surface)
        b.finish(mesh, 'RAW', depth)
        return
    frame = surface if surface in ('FLOOR', 'CEILING') else 'WALL'
    model(b, width, width if obstacle_type in ROUND else height, depth)
    b.finish(mesh, frame, depth)
