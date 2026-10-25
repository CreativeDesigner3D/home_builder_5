"""Materials for purchased accessory models (pull-outs, roll-outs,
organizers, corner units).

The models share the materials the rest of the cabinet uses rather than
flat colours of their own: solid wood parts take the procedural wood
shader the cabinet finishes are built from (set to a species and stain),
and metal parts take the same metal finishes the pulls offer. Plastic
and polymer parts, which nothing else in the cabinet has, get small
node materials here.

Every material is created once per file and reused by name.
"""

import os
from types import SimpleNamespace

import bpy

# Accessory material key -> how to build it.
#   ('WOOD', species, stain)   procedural wood shader
#   ('METAL', finish name)     a pull finish from the finishes library
#   ('PLAIN', color, metallic, roughness, transmission)
SPECS = {
    'MAPLE':   ('WOOD', 'MAPLE', 'Natural'),
    'PLYWOOD': ('WOOD', 'BIRCH', 'Natural'),
    'BIRCH':   ('WOOD', 'BIRCH', 'Natural'),
    'CHROME':  ('METAL', 'Polished Chrome'),
    'STEEL':   ('METAL', 'Matte Aluminum'),
    'POLYMER': ('PLAIN', (0.90, 0.86, 0.76, 1.0), 0.0, 0.45, 0.0),
    'CLEAR_PLASTIC': ('PLAIN', (0.82, 0.88, 0.92, 1.0), 0.0, 0.1, 0.9),
}

# Solid-view colours: metal finishes read almost black in Solid shading
# at their real colour, so accessory copies get a lighter display colour.
_DISPLAY = {
    'MAPLE':   (0.86, 0.72, 0.52, 1.0),
    'PLYWOOD': (0.80, 0.66, 0.47, 1.0),
    'BIRCH':   (0.84, 0.74, 0.58, 1.0),
    'CHROME':  (0.72, 0.74, 0.77, 1.0),
    'STEEL':   (0.60, 0.61, 0.63, 1.0),
}

_NAMES = {
    'MAPLE': "Accessory Maple Wood",
    'PLYWOOD': "Accessory Plywood Wood",
    'BIRCH': "Accessory Birch Wood",
    'CHROME': "Accessory Polished Chrome",
    'STEEL': "Accessory Satin Steel",
    'POLYMER': "Accessory Almond Polymer",
    'CLEAR_PLASTIC': "Accessory Clear Plastic",
}


def _wood_blend_path():
    return os.path.join(os.path.dirname(__file__), 'face_frame_assets',
                        'materials', 'cabinet_material.blend')


def _wood(name, species, stain):
    """The cabinet wood shader set to one species and stain."""
    from . import wood_materials
    try:
        with bpy.data.libraries.load(_wood_blend_path()) as (src, dst):
            if 'Wood' not in src.materials:
                return None
            dst.materials = ['Wood']
    except Exception:
        return None
    mat = dst.materials[0]
    if mat is None:
        return None
    mat.name = name
    rotated = mat.copy()
    # update_finish_material reads a style; a stand-in carries just the
    # fields it uses. The rotated copy only exists to satisfy it.
    style = SimpleNamespace(
        material=mat, material_rotated=rotated, wood_species=species,
        stain_color=stain, paint_color='', finish_color='',
        custom_finish_color=(1.0, 1.0, 1.0, 1.0))
    try:
        wood_materials.update_finish_material(style)
    finally:
        bpy.data.materials.remove(rotated)
    return mat


def _metal(name, finish):
    """A private copy of a pull finish, so the display colour can be
    lightened without touching the pulls that share the original."""
    from . import pulls
    src = pulls.load_finish_material(finish)
    if src is None:
        return None
    mat = src.copy()
    mat.name = name
    return mat


def _plain(name, color, metallic, roughness, transmission):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        for key in ('Transmission Weight', 'Transmission'):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = transmission
                break
    mat.diffuse_color = color
    mat.metallic = metallic
    mat.roughness = roughness
    return mat


def get(key):
    """The material for an accessory material key, created on first use.
    Falls back to a plain material in the display colour when a library
    file or finish is missing, so a model is never left unshaded."""
    name = _NAMES.get(key)
    if name is None:
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    spec = SPECS[key]
    if spec[0] == 'WOOD':
        mat = _wood(name, spec[1], spec[2])
    elif spec[0] == 'METAL':
        mat = _metal(name, spec[1])
    else:
        mat = _plain(name, *spec[1:])
    if mat is None:
        color = _DISPLAY.get(key, (0.8, 0.8, 0.8, 1.0))
        mat = _plain(name, color, 0.9 if spec[0] == 'METAL' else 0.0,
                     0.3, 0.0)
    if key in _DISPLAY:
        mat.diffuse_color = _DISPLAY[key]
    return mat
