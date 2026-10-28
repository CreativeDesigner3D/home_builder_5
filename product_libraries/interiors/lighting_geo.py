"""Light fixtures: a model and real Blender lights, so they light renders.

A fixture is a GeoNodeCage (types_lighting) whose kind, lumens and
colour temperature are on the cage. A ceiling fixture's cage hangs from
the ceiling: x and y centred on where it was placed, its top at the
ceiling. A wall fixture's cage stands against the wall like an
appliance's (its back at y = 0, the room at -y). Each build replaces the
model's parts and its lights, children of the cage.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from ...units import inch
from ..common import appliance_geo as AG

FIXTURE_KEY = 'IS_LIGHT_FIXTURE'
KIND_KEY = 'FIXTURE_KIND'
LUMENS_KEY = 'FIXTURE_LUMENS'
KELVIN_KEY = 'FIXTURE_KELVIN'
PART_KEY = 'IS_FIXTURE_PART'
LIGHT_KEY = 'IS_FIXTURE_LIGHT'
BASE_WATTS = 'HB_BASE_WATTS'
LUMENS_PER_WATT = 25.0              # tuned against Add Room Lights' watts in EEVEE

CEILING_KINDS = ('PENDANT', 'FLUSH', 'RECESSED', 'CHANDELIER', 'FAN')
WALL_KINDS = ('SCONCE', 'VANITY')


def kelvin_to_rgb(kelvin):
    """An approximation of a black body's colour at a temperature."""
    t = kelvin / 100.0
    r = 255.0 if t <= 66 else max(0.0, min(255.0, 329.698727446 * ((t - 60) ** -0.1332047592)))
    if t <= 66:
        g = 99.4708025861 * math.log(max(t, 1.0)) - 161.1195681661
    else:
        g = 288.1221695283 * ((t - 60) ** -0.0755148492)
    g = max(0.0, min(255.0, g))
    if t >= 66:
        b = 255.0
    elif t <= 19:
        b = 0.0
    else:
        b = max(0.0, min(255.0, 138.5177312231 * math.log(t - 10) - 305.0447927307))
    return (r / 255.0, g / 255.0, b / 255.0)


# ---- Parts --------------------------------------------------------------------------

def _metal():
    return AG._material('Fixture Metal', (0.35, 0.33, 0.30), 0.9, 0.3)


def _shade():
    return AG._material('Fixture Shade', (0.92, 0.90, 0.85), 0.0, 0.6)


def _blade():
    return AG._material('Fan Blade', (0.42, 0.30, 0.20), 0.0, 0.5)


def _glow(color):
    name = "Fixture Bulb %02x%02x%02x" % tuple(round(c * 255) for c in color)
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = color + (1.0,)
        em.inputs['Strength'].default_value = 8.0
        nt.links.new(em.outputs[0], out.inputs['Surface'])
        mat.diffuse_color = color + (1.0,)
    return mat


def _part(cage, name, bm, mat, smooth=True):
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


def _rev(profile, cx, cy, segments=32):
    """A solid of revolution round a vertical axis at (cx, cy) from (r, z)."""
    return AG._oval_solid(profile, cx, cy, 1.0, 1.0, segments)


def _rod(cx, cy, z0, z1, r=inch(0.25)):
    return _rev([(r, z0), (r, z1), (0.001, z1)], cx, cy, 12)


def _sphere(cx, cy, cz, r, segments=16):
    prof = [(0.001, cz - r)] + [(r * math.sin(math.pi * k / 8), cz - r * math.cos(math.pi * k / 8))
                                for k in range(1, 8)] + [(0.001, cz + r)]
    return _rev(prof, cx, cy, segments)


def _light(cage, name, kind, location, watts, color, size=0.05, rotation=(0.0, 0.0, 0.0),
           spot=None, shape=None, size_y=None):
    data = bpy.data.lights.new(name, kind)
    data.energy = watts
    data.color = color
    if kind in ('POINT', 'SPOT'):
        data.shadow_soft_size = size
    if kind == 'SPOT' and spot:
        data.spot_size = spot
        data.spot_blend = 0.6
    if kind == 'AREA':
        data.shape = shape or 'DISK'
        data.size = size
        if size_y is not None:
            data.size_y = size_y
    obj = bpy.data.objects.new(name, data)
    obj.parent = cage
    obj.location = location
    obj.rotation_euler = rotation
    obj[LIGHT_KEY] = True
    obj[BASE_WATTS] = watts
    for coll in list(cage.users_collection) or [bpy.context.scene.collection]:
        coll.objects.link(obj)
    return obj


# ---- Builders: ceiling fixtures (x, y from 0 to the cage's size, top at its top) --

def _canopy(cage, cx, cy, top, r=inch(2.75)):
    _part(cage, "Canopy", _rev([(r, top - inch(1.0)), (r * 0.9, top), (0.001, top)], cx, cy), _metal())


def _build_pendant(cage, w, d, h, watts, color):
    cx, cy = w / 2.0, d / 2.0
    _canopy(cage, cx, cy, h)
    shade_h = min(inch(8.0), h * 0.4)
    _part(cage, "Rod", _rod(cx, cy, shade_h, h - inch(1.0)), _metal())
    r = min(w, d) / 2.0
    _part(cage, "Shade", _rev([(r, 0.0), (r * 0.92, shade_h * 0.15), (r * 0.55, shade_h * 0.75),
                                (inch(1.2), shade_h), (0.001, shade_h)], cx, cy), _shade())
    _part(cage, "Bulb", _sphere(cx, cy, shade_h * 0.4, inch(1.4)), _glow(color))
    _light(cage, "Pendant Light", 'POINT', (cx, cy, shade_h * 0.3), watts, color, size=0.04)


def _build_flush(cage, w, d, h, watts, color):
    cx, cy = w / 2.0, d / 2.0
    r = min(w, d) / 2.0
    _part(cage, "Fixture Rim", _rev([(r, h - inch(0.75)), (r, h), (0.001, h)], cx, cy), _metal())
    _part(cage, "Dome", _rev([(r * 0.95, h - inch(0.75)), (r * 0.8, h * 0.45), (r * 0.45, h * 0.1),
                               (0.001, 0.0)], cx, cy), _glow(tuple(0.5 + c * 0.5 for c in color)))
    _light(cage, "Flush Light", 'POINT', (cx, cy, -inch(1.0)), watts, color, size=0.08)


def _build_recessed(cage, w, d, h, watts, color):
    cx, cy = w / 2.0, d / 2.0
    r = min(w, d) / 2.0
    _part(cage, "Trim Ring", _rev([(r, h - inch(0.25)), (r, h), (r * 0.72, h), (r * 0.72, h - inch(0.25))],
                                   cx, cy), _shade(), smooth=False)
    _part(cage, "Lamp", _rev([(r * 0.72, h - inch(0.2)), (0.001, h - inch(0.2))], cx, cy),
          _glow(color), smooth=False)
    _light(cage, "Can Light", 'AREA', (cx, cy, h - inch(0.3)), watts, color, size=r * 1.4)


def _build_chandelier(cage, w, d, h, watts, color):
    cx, cy = w / 2.0, d / 2.0
    _canopy(cage, cx, cy, h)
    body = h * 0.35
    _part(cage, "Stem", _rod(cx, cy, body, h - inch(1.0), inch(0.4)), _metal())
    _part(cage, "Body", _rev([(inch(0.6), 0.0), (inch(2.5), body * 0.3), (inch(1.2), body * 0.8),
                               (inch(0.8), body), (0.001, body)], cx, cy), _metal())
    arms = 6
    reach = min(w, d) / 2.0 - inch(1.5)
    bulbs = []
    for k in range(arms):
        a = 2.0 * math.pi * k / arms
        x, y = cx + math.cos(a) * reach, cy + math.sin(a) * reach
        bm = bmesh.new()
        n = 8
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            p0 = Vector((cx + math.cos(a) * reach * t0, cy + math.sin(a) * reach * t0, body * 0.35 + body * 0.4 * t0 ** 2))
            p1 = Vector((cx + math.cos(a) * reach * t1, cy + math.sin(a) * reach * t1, body * 0.35 + body * 0.4 * t1 ** 2))
            mid = (p0 + p1) / 2.0
            seg = AG._soft_box(mid.x - inch(0.25), mid.x + inch(0.25), mid.y - inch(0.25), mid.y + inch(0.25),
                               min(p0.z, p1.z) - inch(0.2), max(p0.z, p1.z) + inch(0.2), inch(0.1))
            tmp = bpy.data.meshes.new("tmp")
            seg.to_mesh(tmp)
            seg.free()
            bm.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        _part(cage, "Arm", bm, _metal())
        top = body * 0.75 + inch(0.5)
        _part(cage, "Cup", _rev([(inch(0.9), top - inch(1.2)), (inch(1.2), top), (0.001, top)], x, y), _metal())
        _part(cage, "Candle Bulb", _sphere(x, y, top + inch(1.4), inch(0.8)), _glow(color))
        bulbs.append((x, y, top + inch(1.4)))
    # A few real lights for many bulbs: renders stay quick
    for k in range(3):
        x, y, z = bulbs[k * 2]
        _light(cage, "Chandelier Light", 'POINT', (x, y, z), watts / 3.0, color, size=0.03)


def _build_fan(cage, w, d, h, watts, color):
    cx, cy = w / 2.0, d / 2.0
    _canopy(cage, cx, cy, h, inch(3.0))
    motor = inch(6.0)
    _part(cage, "Downrod", _rod(cx, cy, motor, h - inch(1.0), inch(0.4)), _metal())
    _part(cage, "Motor", _rev([(inch(3.5), inch(1.5)), (inch(4.0), inch(3.0)), (inch(3.6), motor),
                                (0.001, motor)], cx, cy), _metal())
    span = min(w, d) / 2.0
    for k in range(5):
        a = 2.0 * math.pi * k / 5
        bm = AG._soft_box(inch(4.0), span, -inch(2.75), inch(2.75), inch(3.0), inch(3.35), inch(0.1))
        for v in bm.verts:
            x, y = v.co.x, v.co.y
            v.co.x = cx + x * math.cos(a) - y * math.sin(a)
            v.co.y = cy + x * math.sin(a) + y * math.cos(a)
        _part(cage, "Blade", bm, _blade(), smooth=False)
    _part(cage, "Light Kit", _rev([(inch(3.0), inch(1.5)), (inch(2.6), inch(0.6)), (0.001, 0.0)], cx, cy),
          _glow(tuple(0.5 + c * 0.5 for c in color)))
    _light(cage, "Fan Light", 'POINT', (cx, cy, -inch(1.0)), watts, color, size=0.06)


# ---- Builders: wall fixtures (the wall at y = 0, the room at -y) --------------------

def _build_sconce(cage, w, d, h, watts, color):
    cx = w / 2.0
    _part(cage, "Backplate", AG._soft_box(cx - inch(2.25), cx + inch(2.25), -inch(0.75), 0.0,
                                          h * 0.25, h * 0.75, inch(0.25)), _metal())
    _part(cage, "Arm", AG._soft_box(cx - inch(0.3), cx + inch(0.3), -d * 0.55, -inch(0.75),
                                    h * 0.45, h * 0.52, inch(0.1)), _metal())
    sy = -d * 0.55
    _part(cage, "Shade", _rev([(inch(2.6), h * 0.35), (inch(2.2), h), (inch(1.8), h), (inch(2.3), h * 0.38)],
                               cx, sy), _shade())
    _part(cage, "Bulb", _sphere(cx, sy, h * 0.6, inch(1.1)), _glow(color))
    _light(cage, "Sconce Light", 'POINT', (cx, sy, h * 0.6), watts, color, size=0.04)


def _build_vanity(cage, w, d, h, watts, color):
    _part(cage, "Bar", AG._soft_box(0.0, w, -inch(1.0), 0.0, h * 0.4, h * 0.6, inch(0.3)), _metal())
    n = max(2, min(5, int(w / inch(8.0))))
    for k in range(n):
        x = w * (k + 0.5) / n
        _part(cage, "Globe", _sphere(x, -d * 0.55, h * 0.5, min(h, d) * 0.4), _glow(color))
    _light(cage, "Vanity Light", 'AREA', (w / 2.0, -d * 0.6, h * 0.5), watts, color, size=w * 0.9,
           shape='RECTANGLE', size_y=inch(3.0), rotation=(math.radians(90.0), 0.0, 0.0))


BUILDERS = {
    'PENDANT': _build_pendant,
    'FLUSH': _build_flush,
    'RECESSED': _build_recessed,
    'CHANDELIER': _build_chandelier,
    'FAN': _build_fan,
    'SCONCE': _build_sconce,
    'VANITY': _build_vanity,
}


# ---- Building ---------------------------------------------------------------------

def clear(cage):
    for child in list(cage.children):
        if child.get(PART_KEY) or child.get(LIGHT_KEY):
            data = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Light) and data.users == 0:
                bpy.data.lights.remove(data)


def watts_of(cage):
    return float(cage.get(LUMENS_KEY, 800.0)) / LUMENS_PER_WATT


def build(cage):
    """Make a fixture's model and lights from its kind and settings."""
    from ... import hb_types
    kind = cage.get(KIND_KEY)
    builder = BUILDERS.get(kind)
    if builder is None:
        return False
    clear(cage)
    c = hb_types.GeoNodeCage(cage)
    w, d, h = c.get_input('Dim X'), c.get_input('Dim Y'), c.get_input('Dim Z')
    color = kelvin_to_rgb(float(cage.get(KELVIN_KEY, 2700.0)))
    builder(cage, w, d, h, watts_of(cage), color)
    apply_house_switches(cage)
    return True


def apply_house_switches(cage=None):
    """The house's Lights in Renders switch and dimmer on one fixture's
    lights, or every fixture's."""
    scene = bpy.context.scene
    try:
        from ... import hb_house
        house_scene = hb_house.house_scene_of(scene) or scene
    except Exception:
        house_scene = scene
    house = getattr(house_scene, 'hb_house', None)
    on = getattr(house, 'fixture_lights', True)
    dim = getattr(house, 'fixture_dimmer', 1.0)
    objs = cage.children if cage is not None else house_scene.objects
    for obj in objs:
        if obj.get(LIGHT_KEY) and obj.type == 'LIGHT':
            obj.data.energy = float(obj.get(BASE_WATTS, obj.data.energy)) * dim
            obj.hide_render = not on
