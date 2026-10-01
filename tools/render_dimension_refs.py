"""Gera as imagens de referência do Configurador de Dimensões.

Uso:
    blender --background --factory-startup --python tools/render_dimension_refs.py

Saída: blendertomob/assets/dimension_refs/<chave>.png (chaves = `image_key` de data/dimension_schema.py).
- sheet_<componente>.png: placa com os lados da fita numerados (1 e 2 = bordas do comprimento,
  3 e 4 = bordas da largura — convenção C-1).
- ext_<campo>.png: módulo com a medida destacada em vermelho.
- max_measures.png: chapa com as medidas máximas.
"""

import importlib.util
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "blendertomob" / "assets" / "dimension_refs"

spec = importlib.util.spec_from_file_location("dimension_schema", ROOT / "blendertomob/data/dimension_schema.py")
schema = importlib.util.module_from_spec(spec)
sys.modules["dimension_schema"] = schema
spec.loader.exec_module(schema)

WOOD = (0.55, 0.33, 0.18, 1.0)
WHITE = (0.92, 0.92, 0.92, 1.0)
RED = (0.85, 0.08, 0.08, 1.0)
DARK = (0.1, 0.1, 0.1, 1.0)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'OBJECT'
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 480
    scene.render.resolution_y = 300
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.compression = 100
    scene.world = bpy.data.worlds.new("Fundo")
    scene.world.color = (1.0, 1.0, 1.0)
    scene.display.shading.background_type = 'WORLD'
    return scene


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


def box(name, size, location, color):
    mesh = bpy.data.meshes.new(name)
    x, y, z = (s / 2 for s in size)
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.color = color
    bpy.context.scene.collection.objects.link(obj)
    return obj


def text(body, location, size=0.12, color=DARK, rotation=(math.radians(90), 0, 0)):
    curve = bpy.data.curves.new(body, type='FONT')
    curve.body = body
    curve.size = size
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    obj = bpy.data.objects.new(body, curve)
    obj.location = location
    obj.rotation_euler = rotation
    obj.color = color
    bpy.context.scene.collection.objects.link(obj)
    return obj


def camera(location, target, ortho_scale):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def render(name):
    OUT.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)


def sheet_image(component):
    """Placa vista de frente (comprimento na vertical) com os 4 lados numerados e o nome do componente."""
    reset_scene()
    length, width = 1.1, 0.62
    box("Placa", (width, 0.03, length), (-0.45, 0, 0), WOOD)
    # Lados 1 e 2 = bordas do comprimento (esquerda/direita); 3 e 4 = bordas da largura (topo/base).
    text("1", (-0.45 - width / 2 - 0.1, -0.05, 0), 0.15, RED)
    text("2", (-0.45 + width / 2 + 0.1, -0.05, 0), 0.15, RED)
    text("3", (-0.45, -0.05, length / 2 + 0.1), 0.15, RED)
    text("4", (-0.45, -0.05, -length / 2 - 0.1), 0.15, RED)
    text(component.label_pt, (0.75, -0.05, 0.2), 0.1, DARK)
    text("1, 2 = comprimento", (0.75, -0.05, -0.05), 0.075, DARK)
    text("3, 4 = largura", (0.75, -0.05, -0.2), 0.075, DARK)
    camera((0, -6, 0), (0, 0, 0), 2.6)
    render(f"sheet_{component.code.lower()}")


def external_image(field_name):
    """Módulo inferior/aéreo/torre em perspectiva leve com a medida em destaque."""
    reset_scene()
    tall = field_name.startswith('tall')
    upper = field_name.startswith('upper') or field_name == 'install_height_upper'
    w, d, h = 0.6, 0.55, (2.2 if tall else 0.72)
    if upper:
        d, h = 0.35, 0.7
    z0 = 1.5 if field_name == 'install_height_upper' else 0.0
    kick = 0.1 if not upper else 0.0
    box("Caixa", (w, d, h - kick), (0, 0, z0 + kick + (h - kick) / 2), WOOD)
    box("Porta", (w - 0.004, 0.018, h - kick - 0.004), (0, -d / 2 - 0.01, z0 + kick + (h - kick) / 2), WHITE)
    if kick:
        box("Rodape", (w - 0.04, 0.015, kick), (0, -d / 2 + 0.05, kick / 2), DARK)
    box("Piso", (2.2, 2.0, 0.005), (0, 0, -0.003), (0.85, 0.85, 0.85, 1.0))
    if 'depth' in field_name:
        box("Cota", (0.01, d, 0.01), (w / 2 + 0.08, 0, z0 + h + 0.05), RED)
    elif field_name in ('toe_kick_height', 'toe_kick_setback'):
        box("Cota", (0.01, 0.01, kick), (w / 2 + 0.08, -d / 2, kick / 2), RED)
    elif field_name == 'install_height_upper':
        box("Cota", (0.01, 0.01, z0), (w / 2 + 0.08, -d / 2, z0 / 2), RED)
    elif field_name == 'top_overhang':
        box("Tampo", (w + 0.04, d + 0.04, 0.03), (0, -0.02, h + 0.015), (0.6, 0.6, 0.6, 1.0))
        box("Cota", (0.01, 0.04, 0.01), (w / 2 + 0.08, -d / 2 - 0.02, h + 0.05), RED)
    else:
        box("Cota", (0.01, 0.01, h), (w / 2 + 0.08, -d / 2, z0 + h / 2), RED)
    top = z0 + h
    camera((2.6, -3.6, top * 0.6 + 1.0), (0, 0, top / 2), max(2.4, (top + 0.5) * 1.6))
    render(f"ext_{field_name}")


def max_image():
    reset_scene()
    box("Chapa", (2.75, 0.02, 1.83), (0, 0, -0.1), WOOD)
    box("Util", (2.73, 0.021, 1.81), (0, -0.002, -0.1), (0.62, 0.4, 0.22, 1.0))
    text("Largura máxima", (0, -0.05, 1.0), 0.14, RED)
    text("Comprimento máximo", (0, -0.05, -0.1), 0.14, WHITE)
    camera((0, -6, 0), (0, 0, 0), 3.4)
    render("max_measures")


def main():
    for component in schema.COMPONENTS:
        sheet_image(component)
    seen = set()
    for param in schema.params_for(group=schema.GROUP_EXTERNAL):
        if param.field in seen:
            continue
        seen.add(param.field)
        external_image(param.field)
    max_image()
    print(f"DIMENSION_REFS_OK {len(list(OUT.glob('*.png')))} imagens em {OUT}")


if __name__ == "__main__":
    main()
