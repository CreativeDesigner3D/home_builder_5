"""Wall coverings by room: paint and tile on the walls, and paint on the
ceilings, chosen per room with house defaults by the kind of room.

A wall's face takes one material for its whole length, but in a house
one face can look into two rooms (a T wall lands on it). So each face
gets one composed material: the finish of each room along it, chosen by
where the shading point is along the wall (the wall's own x), and below
a height the room's lower band (a tile wainscot). The material is named
from what it holds, so faces that look the same share one.

Outdoor faces are left alone: the siding owns them (hb_exterior).
"""

import hashlib

import bpy

from . import hb_house, hb_types

MATERIAL_PREFIX = "HB Walls "
CEILING_PREFIX = "HB Ceiling "
FACES_KEY = 'HB_WALL_FACES'         # the faces a wall had covered, to undo
SIDE_INPUT = {'REF': 'Left Edge', 'FAR': 'Right Edge'}
TILE_W, TILE_H = 0.1524, 0.0762    # subway tile, 6" x 3"
GROUT = (0.62, 0.62, 0.60)
TILE_ROUGHNESS = 0.18
PAINT_ROUGHNESS = 0.7

FINISH_ITEMS = hb_house.WALL_FINISH_ITEMS
BAND_ITEMS = hb_house.WALL_BAND_ITEMS


# ---- What a room's walls are ------------------------------------------------------

def _rgb(c):
    return tuple(round(float(v), 3) for v in c[:3])


def room_spec(house, room):
    """(finish, colour, band, band colour, band height) of a room's walls:
    its own, or the house's for its kind of room."""
    if room.walls_auto:
        kind = hb_house.floor_kind(room)
        if kind == 'wet':
            return ('PAINT', _rgb(house.walls_wet_color), house.walls_wet_band,
                    _rgb(house.walls_band_color), round(house.walls_band_height, 4))
        color = house.walls_garage_color if kind == 'garage' else house.walls_room_color
        return ('PAINT', _rgb(color), 'NONE', (1.0, 1.0, 1.0), 0.0)
    band = room.walls_band if room.walls_band_height > 0.0 else 'NONE'
    return (room.walls_finish, _rgb(room.walls_color), band,
            _rgb(room.walls_band_color), round(room.walls_band_height, 4))


def _covered(room):
    return not (room.orphaned or room.is_porch or room.outdoor)


# ---- Materials -------------------------------------------------------------------

def _layers(spans):
    """The spans as [(from x, spec)]: each room's finish from halfway
    between it and the room before, the first from the wall's start."""
    runs = []
    for t0, t1, spec in sorted(spans):
        if runs and runs[-1][2] == spec:
            runs[-1][1] = max(runs[-1][1], t1)
            continue
        runs.append([t0, t1, spec])
    return [(None if i == 0 else round((runs[i - 1][1] + r[0]) / 2.0, 4), r[2])
            for i, r in enumerate(runs)]


def _finish_sockets(nt, spec_part, color, coord):
    """(colour socket, roughness value) of a paint or tile finish."""
    if spec_part == 'TILE':
        brick = nt.nodes.new('ShaderNodeTexBrick')
        brick.offset = 0.5
        brick.inputs['Color1'].default_value = color + (1.0,)
        brick.inputs['Color2'].default_value = tuple(min(c * 0.97, 1.0) for c in color) + (1.0,)
        brick.inputs['Mortar'].default_value = GROUT + (1.0,)
        brick.inputs['Scale'].default_value = 1.0
        brick.inputs['Mortar Size'].default_value = 0.0025
        brick.inputs['Brick Width'].default_value = TILE_W
        brick.inputs['Row Height'].default_value = TILE_H
        nt.links.new(coord, brick.inputs['Vector'])
        return brick.outputs['Color'], TILE_ROUGHNESS
    rgb = nt.nodes.new('ShaderNodeRGB')
    rgb.outputs[0].default_value = color + (1.0,)
    return rgb.outputs[0], PAINT_ROUGHNESS


def _mix(nt, a, b, fac):
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(fac, mix.inputs['Factor'])
    nt.links.new(a, mix.inputs[6])
    nt.links.new(b, mix.inputs[7])
    return mix.outputs[2]


def _mix_value(nt, a, b, fac):
    """a + fac * (b - a), a and b plain numbers or sockets."""
    m = nt.nodes.new('ShaderNodeMix')
    m.data_type = 'FLOAT'
    nt.links.new(fac, m.inputs['Factor'])
    for socket, value in ((m.inputs[2], a), (m.inputs[3], b)):
        if isinstance(value, (int, float)):
            socket.default_value = value
        else:
            nt.links.new(value, socket)
    return m.outputs[0]


def _compare(nt, value, threshold, op):
    node = nt.nodes.new('ShaderNodeMath')
    node.operation = op
    nt.links.new(value, node.inputs[0])
    node.inputs[1].default_value = threshold
    return node.outputs[0]


def face_material(layers):
    """The composed material for a face's layers [(from x, spec)]."""
    key = repr(layers)
    name = MATERIAL_PREFIX + hashlib.md5(key.encode()).hexdigest()[:10]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    face = nt.nodes.new('ShaderNodeCombineXYZ')        # along the wall, and up it
    nt.links.new(sep.outputs['X'], face.inputs['X'])
    nt.links.new(sep.outputs['Z'], face.inputs['Y'])
    x, z, coord = sep.outputs['X'], sep.outputs['Z'], face.outputs[0]
    color = rough = None
    for start, (finish, c, band, band_c, band_h) in layers:
        col, r = _finish_sockets(nt, finish, c, coord)
        if band != 'NONE' and band_h > 0.0:
            bcol, br = _finish_sockets(nt, band, band_c, coord)
            below = _compare(nt, z, band_h, 'LESS_THAN')
            col = _mix(nt, col, bcol, below)
            r = _mix_value(nt, r, br, below)
        if color is None:
            color, rough = col, r
            continue
        past = _compare(nt, x, start, 'GREATER_THAN')
        color = _mix(nt, color, col, past)
        rough = _mix_value(nt, rough, r, past)
    nt.links.new(color, bsdf.inputs['Base Color'])
    if isinstance(rough, (int, float)):
        bsdf.inputs['Roughness'].default_value = rough
    else:
        nt.links.new(rough, bsdf.inputs['Roughness'])
    # Solid view shows the first room's colour
    mat.diffuse_color = layers[0][1][1] + (1.0,)
    return mat


def ceiling_material(color):
    c = _rgb(color)
    name = CEILING_PREFIX + "%02x%02x%02x" % tuple(round(v * 255) for v in c)
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = c + (1.0,)
            bsdf.inputs['Roughness'].default_value = 0.85
        mat.diffuse_color = c + (1.0,)
    return mat


# ---- Applying ----------------------------------------------------------------------

def _plain(scene):
    """What an uncovered face goes back to: the scene's wall material."""
    hb = getattr(scene, 'home_builder', None)
    return getattr(hb, 'wall_material', None) if hb is not None else None


def face_spans(scene):
    """{(wall name, side): [(t0, t1, spec)]} - every room's stretch of
    every wall face it looks into."""
    from . import hb_rooms
    house = scene.hb_house
    out = {}
    for level in house.levels:
        for i in range(len(level.rooms)):
            room = level.rooms[i]
            if not _covered(room):
                continue
            spec = room_spec(house, room)
            for wall, side, t0, t1 in hb_rooms.room_faces(scene, level, room):
                out.setdefault((wall.name, side), []).append((round(t0, 4), round(t1, 4), spec))
    return out


def apply_wall_coverings(scene):
    """Cover every room's walls and ceiling as its settings say - or, with
    the house's Wall Finishes off, put back what they had."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    house = scene.hb_house
    on = house.walls_by_room
    spans = face_spans(scene) if on else {}
    plain = _plain(scene)
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP'):
            continue
        wall = hb_types.GeoNodeWall(obj)
        if not wall.has_modifier():
            continue
        had = set(obj.get(FACES_KEY, []))
        now = set()
        for side, input_name in SIDE_INPUT.items():
            mine = spans.get((obj.name, side))
            if mine:
                wall.set_input(input_name, face_material(_layers(mine)))
                now.add(side)
            elif side in had:
                current = wall.get_input(input_name)
                if current is None or current.name.startswith(MATERIAL_PREFIX):
                    wall.set_input(input_name, plain)
        if now or had:
            obj[FACES_KEY] = sorted(now)
            obj.update_tag()
    # Ceilings: painted, unless a room has its own material
    for level in house.levels:
        for room in level.rooms:
            obj = room.ceiling_obj
            if obj is None or obj.data is None or room.ceiling_material is not None:
                continue
            mats = obj.data.materials
            current = mats[0] if len(mats) else None
            if on and _covered(room):
                color = house.ceiling_color if room.walls_auto else room.ceiling_color
                mat = ceiling_material(color)
                if len(mats):
                    mats[0] = mat
                else:
                    mats.append(mat)
            elif current is not None and current.name.startswith(CEILING_PREFIX):
                mats.clear()


def changed(self, context):
    """A wall finish setting changed, on the house or a room."""
    scene = hb_house.house_scene_of(context.scene if context else bpy.context.scene)
    if scene is not None:
        apply_wall_coverings(scene)
