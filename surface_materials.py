"""
Procedural surface materials for the surfaces a room is rendered with:
floors, wall backsplashes and countertops.

Every look is built from shader nodes in code, so no texture files or
.blend assets ship with the addon and a usable surface is one click away.
The four builders are wood planks, tile, veined stone and a flat color.
They live in one module so the floor, the backsplash and the countertops
share the same shaders rather than keeping copies that drift.

Anyone who wants a real photographed tile instead picks a material
already in the file -- a material asset library registers with Blender,
so dragging one in makes it available here. That is the 'EXISTING'
style; see operators/ops_surfaces.py.

World-scale UVs are assumed: 1 UV unit = 1 metre, which is what Add
Floor generates and what backsplash.py writes onto its slabs. Tile and
plank sizes are therefore real lengths in metres.
"""

import bpy

INCH = 0.0254


# ---------------------------------------------------------------------------
# Looks
# ---------------------------------------------------------------------------
# Every look is (label, base color, accent color) in sRGB 0-1. The accent
# is the grout for tile, the vein for stone, and the darker plank tone for
# wood. CUSTOM keeps whatever colors the dialog is holding.

TILE_LOOKS = {
    'WHITE_GLOSS': ("White Gloss",  (0.94, 0.94, 0.92), (0.80, 0.79, 0.76)),
    'ALABASTER':   ("Alabaster",    (0.90, 0.87, 0.81), (0.74, 0.71, 0.66)),
    'CARRARA':     ("Carrara",      (0.90, 0.90, 0.88), (0.74, 0.74, 0.73)),
    'LIGHT_GRAY':  ("Light Gray",   (0.70, 0.70, 0.68), (0.52, 0.52, 0.50)),
    'CHARCOAL':    ("Charcoal",     (0.24, 0.24, 0.25), (0.17, 0.17, 0.18)),
    'SAGE':        ("Sage",         (0.62, 0.67, 0.58), (0.48, 0.52, 0.45)),
    'NAVY':        ("Navy",         (0.16, 0.24, 0.36), (0.30, 0.32, 0.34)),
    'TERRACOTTA':  ("Terracotta",   (0.68, 0.38, 0.24), (0.55, 0.47, 0.40)),
    'TRAVERTINE':  ("Travertine",   (0.82, 0.74, 0.60), (0.64, 0.57, 0.46)),
    'CUSTOM':      ("Custom", None, None),
}

STONE_LOOKS = {
    'WHITE_QUARTZ':  ("White Quartz",   (0.92, 0.91, 0.89), (0.78, 0.77, 0.75)),
    'CARRARA':       ("Carrara Marble", (0.90, 0.90, 0.89), (0.60, 0.61, 0.63)),
    'CALACATTA':     ("Calacatta",      (0.94, 0.93, 0.90), (0.70, 0.63, 0.50)),
    'GRAY_QUARTZ':   ("Gray Quartz",    (0.55, 0.55, 0.54), (0.42, 0.42, 0.42)),
    'BLACK_GRANITE': ("Black Granite",  (0.09, 0.09, 0.10), (0.30, 0.30, 0.32)),
    'SOAPSTONE':     ("Soapstone",      (0.22, 0.24, 0.24), (0.38, 0.40, 0.40)),
    'CUSTOM':        ("Custom", None, None),
}

WOOD_LOOKS = {
    'LIGHT_OAK':  ("Light Oak",   (0.80, 0.68, 0.50), (0.66, 0.53, 0.37)),
    'NATURAL':    ("Natural Oak", (0.64, 0.45, 0.27), (0.48, 0.32, 0.18)),
    'HONEY':      ("Honey Maple", (0.78, 0.56, 0.32), (0.64, 0.42, 0.22)),
    'WALNUT':     ("Walnut",      (0.34, 0.22, 0.13), (0.22, 0.13, 0.08)),
    'GRAY_WASH':  ("Gray Wash",   (0.58, 0.55, 0.51), (0.44, 0.41, 0.38)),
    'CUSTOM':     ("Custom", None, None),
}

SOLID_LOOKS = {
    'WHITE':      ("White",        (0.92, 0.92, 0.91), None),
    'CONCRETE':   ("Concrete",     (0.60, 0.60, 0.58), None),
    'WARM_GRAY':  ("Warm Gray",    (0.72, 0.69, 0.64), None),
    'GREIGE':     ("Greige",       (0.66, 0.63, 0.58), None),
    'BLACK':      ("Black",        (0.08, 0.08, 0.08), None),
    'CUSTOM':     ("Custom", None, None),
}

SURFACE_LOOKS = {
    'TILE': TILE_LOOKS,
    'STONE': STONE_LOOKS,
    'WOOD': WOOD_LOOKS,
    'SOLID': SOLID_LOOKS,
}

# Tile formats: (label, brick width, row height, running bond). Width is
# the long dimension as laid, so subway reads 6 wide by 3 tall. CUSTOM
# leaves the size fields alone for a format nobody stocks.
TILE_FORMATS = {
    'SUBWAY': ("Subway 3 x 6",   6 * INCH,  3 * INCH,  True),
    'MOSAIC': ("Mosaic 2 in",    2 * INCH,  2 * INCH,  False),
    'SQ4':    ("Square 4 in",    4 * INCH,  4 * INCH,  False),
    'SQ6':    ("Square 6 in",    6 * INCH,  6 * INCH,  False),
    'SQ12':   ("Square 12 in",  12 * INCH, 12 * INCH,  False),
    'PLANK':  ("Plank 4 x 12",  12 * INCH,  4 * INCH,  True),
    'LARGE':  ("Large 12 x 24", 24 * INCH, 12 * INCH,  True),
    'CUSTOM': ("Custom", None, None, False),
}

SURFACE_STYLE_ITEMS = [
    ('TILE',  "Tile",  "Tile with grout, in a grid or running bond", 'MESH_GRID', 0),
    ('STONE', "Stone", "Veined stone -- quartz, marble or granite", 'MATSHADERBALL', 1),
    ('WOOD',  "Wood",  "Wood boards with grain (butcher block)", 'MOD_WAVE', 2),
    ('SOLID', "Solid Color", "Flat color", 'MATERIAL', 3),
    ('EXISTING', "Pick Material",
     "Use a material already in this file -- a textured one dragged in "
     "from the Materials library", 'MATERIAL_DATA', 4),
]

# How each stone carries itself: (vein scale, vein width, speckle).
# Scale is veins per metre, so a bigger number means finer, busier
# veining; width is the half-thickness of a vein in that field; speckle
# is the grain that separates a granite from a marble. Marble is a few
# bold veins over a clean ground, quartz is the reverse.
STONE_CHARACTER = {
    'WHITE_QUARTZ':  (3.0, 0.020, 0.055),
    'CARRARA':       (2.2, 0.035, 0.020),
    'CALACATTA':     (1.4, 0.050, 0.015),
    'GRAY_QUARTZ':   (3.5, 0.015, 0.075),
    'BLACK_GRANITE': (4.2, 0.010, 0.130),
    'SOAPSTONE':     (2.0, 0.030, 0.030),
    'CUSTOM':        (2.4, 0.030, 0.035),
}


def stone_character(look):
    """Vein and speckle settings for one stone look, as keyword
    arguments for build_surface_material."""
    scale, width, speckle = STONE_CHARACTER.get(
        look, STONE_CHARACTER['CUSTOM'])
    return {'vein_scale': scale, 'vein_width': width, 'speckle': speckle}


DEFAULT_LOOK = {'TILE': 'WHITE_GLOSS', 'STONE': 'WHITE_QUARTZ',
                'WOOD': 'NATURAL', 'SOLID': 'WHITE'}
DEFAULT_ROUGHNESS = {'TILE': 0.15, 'STONE': 0.18, 'WOOD': 0.45, 'SOLID': 0.6}


def look_items(style):
    """Enum items for the look dropdown of one style."""
    looks = SURFACE_LOOKS.get(style)
    if not looks:
        return [('CUSTOM', "Custom", "")]
    return [(k, v[0], "") for k, v in looks.items()]


def format_items():
    return [(k, v[0], "") for k, v in TILE_FORMATS.items()]


def srgb_to_linear(c):
    out = []
    for v in c:
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


# ---------------------------------------------------------------------------
# Node graphs
# ---------------------------------------------------------------------------

def clear_nodes(mat):
    """Wipe a material back to Principled -> Output and hand back the node
    tree, the BSDF, and a texture-coordinate node to drive textures from."""
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (700, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    uv = nt.nodes.new('ShaderNodeTexCoord')
    uv.location = (-1100, 0)
    return nt, bsdf, uv


def build_wood_nodes(mat, base, accent, plank_w, roughness):
    nt, bsdf, uv = clear_nodes(mat)
    n = nt.nodes
    L = nt.links
    base = (*base, 1.0)
    accent = (*accent, 1.0)

    # Planks: bricks the size of boards, staggered end joints, hairline gap.
    planks = n.new('ShaderNodeTexBrick')
    planks.location = (-800, 200)
    planks.offset = 0.37
    planks.offset_frequency = 3
    planks.squash = 1.0
    planks.squash_frequency = 1
    planks.inputs['Scale'].default_value = 1.0
    planks.inputs['Color1'].default_value = base
    planks.inputs['Color2'].default_value = accent
    planks.inputs['Mortar'].default_value = (0.02, 0.015, 0.01, 1.0)
    planks.inputs['Mortar Size'].default_value = 0.0015
    planks.inputs['Mortar Smooth'].default_value = 0.2
    planks.inputs['Bias'].default_value = 0.0
    planks.inputs['Brick Width'].default_value = plank_w * 9.0
    planks.inputs['Row Height'].default_value = plank_w
    L.new(uv.outputs['UV'], planks.inputs['Vector'])

    # Per-plank grain phase: nudge the grain coordinates by the plank's
    # random tint so neighbours don't share a grain pattern.
    phase = n.new('ShaderNodeVectorMath')
    phase.location = (-800, -150)
    phase.operation = 'MULTIPLY_ADD'
    phase.inputs[1].default_value = (0.0, 7.0, 0.0)
    L.new(planks.outputs['Color'], phase.inputs[0])
    L.new(uv.outputs['UV'], phase.inputs[2])

    grain = n.new('ShaderNodeTexWave')
    grain.location = (-550, -150)
    grain.wave_type = 'BANDS'
    grain.bands_direction = 'Y'
    grain.inputs['Scale'].default_value = 60.0 / max(plank_w / 0.127, 0.25)
    grain.inputs['Distortion'].default_value = 6.0
    grain.inputs['Detail'].default_value = 3.0
    grain.inputs['Detail Scale'].default_value = 1.5
    grain.inputs['Detail Roughness'].default_value = 0.6
    L.new(phase.outputs['Vector'], grain.inputs['Vector'])

    fine = n.new('ShaderNodeTexNoise')
    fine.location = (-550, -420)
    fine.inputs['Scale'].default_value = 180.0
    fine.inputs['Detail'].default_value = 3.0
    fine.inputs['Roughness'].default_value = 0.6
    L.new(uv.outputs['UV'], fine.inputs['Vector'])

    # Grain darkens the plank tint a little (multiply by 0.78..1).
    grain_map = n.new('ShaderNodeMapRange')
    grain_map.location = (-300, -150)
    grain_map.inputs['To Min'].default_value = 0.78
    grain_map.inputs['To Max'].default_value = 1.0
    L.new(grain.outputs['Fac'], grain_map.inputs['Value'])

    fine_map = n.new('ShaderNodeMapRange')
    fine_map.location = (-300, -420)
    fine_map.inputs['To Min'].default_value = 0.9
    fine_map.inputs['To Max'].default_value = 1.05
    L.new(fine.outputs['Fac'], fine_map.inputs['Value'])

    tone = n.new('ShaderNodeMix')
    tone.location = (-50, 100)
    tone.data_type = 'RGBA'
    tone.blend_type = 'MULTIPLY'
    tone.inputs['Factor'].default_value = 1.0
    L.new(planks.outputs['Color'], tone.inputs[6])
    L.new(grain_map.outputs['Result'], tone.inputs[7])

    tone2 = n.new('ShaderNodeMix')
    tone2.location = (150, 100)
    tone2.data_type = 'RGBA'
    tone2.blend_type = 'MULTIPLY'
    tone2.inputs['Factor'].default_value = 1.0
    L.new(tone.outputs[2], tone2.inputs[6])
    L.new(fine_map.outputs['Result'], tone2.inputs[7])
    L.new(tone2.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = roughness

    # Grain + plank gaps as bump.
    bump_mix = n.new('ShaderNodeMath')
    bump_mix.location = (0, -350)
    bump_mix.operation = 'MULTIPLY_ADD'
    bump_mix.inputs[1].default_value = 0.35
    L.new(grain.outputs['Fac'], bump_mix.inputs[0])
    L.new(planks.outputs['Fac'], bump_mix.inputs[2])
    bump = n.new('ShaderNodeBump')
    bump.location = (200, -350)
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.002
    L.new(bump_mix.outputs['Value'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])


def build_tile_nodes(mat, base, grout, tile_w, tile_h, roughness,
                     running_bond, grout_size=0.004):
    """Tile with grout. Separate width and height so a 3 x 6 subway lays
    the way it is sold; square formats pass the same number twice."""
    nt, bsdf, uv = clear_nodes(mat)
    n = nt.nodes
    L = nt.links
    base = (*base, 1.0)
    grout = (*grout, 1.0)
    # Slight second tone so tiles are not perfectly uniform.
    varied = tuple(min(1.0, c * 0.94) for c in base[:3]) + (1.0,)

    tiles = n.new('ShaderNodeTexBrick')
    tiles.location = (-800, 200)
    tiles.offset = 0.5 if running_bond else 0.0
    tiles.offset_frequency = 2
    tiles.inputs['Scale'].default_value = 1.0
    tiles.inputs['Color1'].default_value = base
    tiles.inputs['Color2'].default_value = varied
    tiles.inputs['Mortar'].default_value = grout
    tiles.inputs['Mortar Size'].default_value = _mortar_size(
        grout_size, tile_w, tile_h)
    tiles.inputs['Mortar Smooth'].default_value = 0.15
    tiles.inputs['Bias'].default_value = 0.4
    tiles.inputs['Brick Width'].default_value = tile_w
    tiles.inputs['Row Height'].default_value = tile_h
    L.new(uv.outputs['UV'], tiles.inputs['Vector'])

    # Soft mottling within each tile.
    mottle = n.new('ShaderNodeTexNoise')
    mottle.location = (-800, -200)
    mottle.inputs['Scale'].default_value = 6.0
    mottle.inputs['Detail'].default_value = 4.0
    mottle.inputs['Roughness'].default_value = 0.55
    L.new(uv.outputs['UV'], mottle.inputs['Vector'])
    mottle_map = n.new('ShaderNodeMapRange')
    mottle_map.location = (-550, -200)
    mottle_map.inputs['To Min'].default_value = 0.92
    mottle_map.inputs['To Max'].default_value = 1.04
    L.new(mottle.outputs['Fac'], mottle_map.inputs['Value'])

    tone = n.new('ShaderNodeMix')
    tone.location = (-250, 100)
    tone.data_type = 'RGBA'
    tone.blend_type = 'MULTIPLY'
    tone.inputs['Factor'].default_value = 1.0
    L.new(tiles.outputs['Color'], tone.inputs[6])
    L.new(mottle_map.outputs['Result'], tone.inputs[7])
    L.new(tone.outputs[2], bsdf.inputs['Base Color'])

    # Glossy tile, matte grout.
    rough = n.new('ShaderNodeMapRange')
    rough.location = (-250, -200)
    rough.inputs['To Min'].default_value = roughness
    rough.inputs['To Max'].default_value = 0.9
    L.new(tiles.outputs['Fac'], rough.inputs['Value'])
    L.new(rough.outputs['Result'], bsdf.inputs['Roughness'])

    # Grout lines recessed.
    bump = n.new('ShaderNodeBump')
    bump.location = (0, -400)
    bump.invert = True
    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.003
    L.new(tiles.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])


def _mortar_size(grout_size, tile_w, tile_h):
    """Brick node Mortar Size from a real joint width, in metres.

    Mortar Size reads as a fraction of the tile and is not one: it is a
    HALF-width in the texture's own coordinate units, the same units as
    Brick Width and Row Height. Since the UVs are world scale and Scale
    is 1, that unit is the metre, and the joint comes out
    2 * Mortar Size wide.

    Getting this wrong is not subtle. Treating it as a fraction put
    0.05 on a 3 x 6 subway, which is a 100 mm joint around a 76 mm
    tile -- the grout swallowed the tile and the wall rendered as one
    flat colour with no pattern at all.

    Clamped so a request for a fat joint on a mosaic still leaves tile
    to look at.
    """
    half = grout_size / 2.0
    return max(0.0002, min(half, min(tile_w, tile_h) * 0.2))


def build_stone_nodes(mat, base, vein, roughness, vein_scale=2.4,
                      vein_width=0.030, speckle=0.035):
    """Veined stone: marble, quartz or granite.

    A vein is drawn as a narrow band either side of one contour of a
    distorted wave, not as the wave itself. Taking the wave straight is
    what made the first version read as camouflage: the field spends
    most of its range far from any contour, so most of the slab came out
    part-veined and the ground was never clean. Measuring DISTANCE to
    the contour instead leaves the ground alone and puts colour only
    where a vein actually runs.

    Two passes -- a bold one and a finer one about a third its width --
    combined with MAXIMUM, so hairlines branch off the main veins rather
    than washing over them. The coordinates are squashed on one axis
    first, which is what makes veins run in a direction instead of
    pooling.
    """
    nt, bsdf, uv = clear_nodes(mat)
    n = nt.nodes
    L = nt.links

    # Anisotropy: features stretch along V, so veins run rather than pool.
    stretch = n.new('ShaderNodeVectorMath')
    stretch.location = (-1000, 200)
    stretch.operation = 'MULTIPLY'
    stretch.inputs[1].default_value = (1.0, 0.26, 1.0)
    L.new(uv.outputs['UV'], stretch.inputs[0])

    def vein_pass(scale, width, distortion, detail, strength, y):
        """One vein layer: distance from the wave's mid contour, mapped
        so 0 sits on the vein and `width` is clear of it."""
        wave = n.new('ShaderNodeTexWave')
        wave.location = (-800, y)
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'DIAGONAL'
        wave.inputs['Scale'].default_value = scale
        wave.inputs['Distortion'].default_value = distortion
        wave.inputs['Detail'].default_value = detail
        wave.inputs['Detail Scale'].default_value = 2.0
        wave.inputs['Detail Roughness'].default_value = 0.6
        L.new(stretch.outputs['Vector'], wave.inputs['Vector'])

        centre = n.new('ShaderNodeMath')
        centre.location = (-600, y)
        centre.operation = 'SUBTRACT'
        centre.inputs[1].default_value = 0.5
        L.new(wave.outputs['Fac'], centre.inputs[0])

        away = n.new('ShaderNodeMath')
        away.location = (-450, y)
        away.operation = 'ABSOLUTE'
        L.new(centre.outputs['Value'], away.inputs[0])

        mask = n.new('ShaderNodeMapRange')
        mask.location = (-300, y)
        mask.inputs['From Min'].default_value = 0.0
        mask.inputs['From Max'].default_value = max(width, 1e-4)
        mask.inputs['To Min'].default_value = strength
        mask.inputs['To Max'].default_value = 0.0
        mask.clamp = True
        L.new(away.outputs['Value'], mask.inputs['Value'])
        return mask

    # Distortion kept modest on purpose: crank it and the veins curl
    # into little loops, which reads as marbled paper rather than
    # stone. Long and wandering is what a slab actually looks like.
    bold = vein_pass(vein_scale, vein_width, 9.0, 3.0, 1.0, 320)
    fine = vein_pass(vein_scale * 2.7, vein_width * 0.35, 12.0, 2.0, 0.55, 40)

    veins = n.new('ShaderNodeMath')
    veins.location = (-120, 200)
    veins.operation = 'MAXIMUM'
    L.new(bold.outputs['Result'], veins.inputs[0])
    L.new(fine.outputs['Result'], veins.inputs[1])

    mix = n.new('ShaderNodeMix')
    mix.location = (60, 200)
    mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*base, 1.0)
    mix.inputs[7].default_value = (*vein, 1.0)
    L.new(veins.outputs['Value'], mix.inputs['Factor'])

    # Speckle -- the grain that separates quartz and granite from marble.
    speck = n.new('ShaderNodeTexNoise')
    speck.location = (-800, -320)
    speck.inputs['Scale'].default_value = 380.0
    speck.inputs['Detail'].default_value = 2.0
    speck.inputs['Roughness'].default_value = 0.8
    L.new(uv.outputs['UV'], speck.inputs['Vector'])
    speck_map = n.new('ShaderNodeMapRange')
    speck_map.location = (-550, -320)
    speck_map.inputs['To Min'].default_value = 1.0 - speckle
    speck_map.inputs['To Max'].default_value = 1.0 + speckle
    L.new(speck.outputs['Fac'], speck_map.inputs['Value'])

    # A slow, very shallow cloud so a big slab is not perfectly even.
    cloud = n.new('ShaderNodeTexNoise')
    cloud.location = (-800, -560)
    cloud.inputs['Scale'].default_value = 2.5
    cloud.inputs['Detail'].default_value = 3.0
    L.new(uv.outputs['UV'], cloud.inputs['Vector'])
    cloud_map = n.new('ShaderNodeMapRange')
    cloud_map.location = (-550, -560)
    cloud_map.inputs['To Min'].default_value = 0.97
    cloud_map.inputs['To Max'].default_value = 1.03
    L.new(cloud.outputs['Fac'], cloud_map.inputs['Value'])

    grain = n.new('ShaderNodeMath')
    grain.location = (-350, -440)
    grain.operation = 'MULTIPLY'
    L.new(speck_map.outputs['Result'], grain.inputs[0])
    L.new(cloud_map.outputs['Result'], grain.inputs[1])

    tone = n.new('ShaderNodeMix')
    tone.location = (240, 120)
    tone.data_type = 'RGBA'
    tone.blend_type = 'MULTIPLY'
    tone.inputs['Factor'].default_value = 1.0
    L.new(mix.outputs[2], tone.inputs[6])
    L.new(grain.outputs['Value'], tone.inputs[7])
    L.new(tone.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = roughness
    _set_if_present(bsdf, 'Coat Weight', 0.25)
    _set_if_present(bsdf, 'Coat Roughness', 0.05)


def build_solid_nodes(mat, base, roughness):
    nt, bsdf, uv = clear_nodes(mat)
    n = nt.nodes
    L = nt.links
    # A whisper of noise keeps flat surfaces from banding under lights.
    noise = n.new('ShaderNodeTexNoise')
    noise.location = (-800, 0)
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 5.0
    L.new(uv.outputs['UV'], noise.inputs['Vector'])
    nmap = n.new('ShaderNodeMapRange')
    nmap.location = (-550, 0)
    nmap.inputs['To Min'].default_value = 0.96
    nmap.inputs['To Max'].default_value = 1.03
    L.new(noise.outputs['Fac'], nmap.inputs['Value'])
    tone = n.new('ShaderNodeMix')
    tone.location = (-250, 0)
    tone.data_type = 'RGBA'
    tone.blend_type = 'MULTIPLY'
    tone.inputs['Factor'].default_value = 1.0
    tone.inputs[6].default_value = (*base, 1.0)
    L.new(nmap.outputs['Result'], tone.inputs[7])
    L.new(tone.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = roughness


def _set_if_present(node, name, value):
    """Principled input names move between Blender versions -- Coat was
    Clearcoat before 4.0 -- so a missing socket is a skip, not a crash."""
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


# ---------------------------------------------------------------------------
# Building a named surface material
# ---------------------------------------------------------------------------

def build_surface_material(name, style, base_srgb, accent_srgb, roughness,
                           tile_w=0.1524, tile_h=0.0762, running_bond=True,
                           grout_size=0.004, vein_scale=2.4,
                           vein_width=0.030, speckle=0.035):
    """Create or rebuild the named material in this style and return it.

    Rebuilding in place is what lets a backsplash be restyled from the
    same dialog without collecting one material per attempt.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    base = srgb_to_linear(base_srgb)
    accent = srgb_to_linear(accent_srgb) if accent_srgb else base
    if style == 'TILE':
        build_tile_nodes(mat, base, accent, tile_w, tile_h, roughness,
                         running_bond, grout_size)
    elif style == 'STONE':
        build_stone_nodes(mat, base, accent, roughness, vein_scale,
                          vein_width, speckle)
    elif style == 'WOOD':
        build_wood_nodes(mat, base, accent, tile_h, roughness)
    else:
        build_solid_nodes(mat, base, roughness)
    mat["HB_SURFACE_STYLE"] = style
    return mat


def assign(obj, mat):
    """Put mat in the object's first material slot."""
    if obj is None or obj.type != 'MESH' or mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
