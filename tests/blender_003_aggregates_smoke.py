"""Teste de fumaça da feature 003, incrementos I3/I4 (T067): agregados e folhas de porta.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_003_aggregates_smoke.py

Cobre: importar OBJ, converter na lateral de um balcão, limite na borda, afundar até a espessura, Perfurar, furo real
no JSON 2.1 (`machining`), desconverter; folha de giro (180°) batendo na parede, voltar fechada, porta de correr,
"Abrir/Fechar Frentes" e salvar fechado com a folha aberta.
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import apply, convert, leaf, perforate  # noqa: E402
from caffmob_draw.cutting import json_exporter, machining, part_extractor  # noqa: E402
from caffmob_draw.inspection import fronts  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
scene = ctx.scene
env.clean_scene()


def max_diff(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


# 1. Importar um OBJ pelo plugin.
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = ctx.object
cube.scale = (0.2, 0.1, 0.05)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
path = os.path.join(tempfile.mkdtemp(), "nicho.obj")
assert bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, export_materials=False) == {'FINISHED'}
bpy.data.objects.remove(cube, do_unlink=True)
assert bpy.ops.caffmob.import_model(filepath=path) == {'FINISHED'}
nicho = ctx.view_layer.objects.active
assert nicho is not None and nicho.type == 'MESH'
try:
    bpy.ops.caffmob.import_model(filepath=path.replace(".obj", ".skp"))
    raise AssertionError(".skp deveria ser recusado")
except RuntimeError as exc:
    assert "Formato não suportado" in str(exc)

# 2. Converter em agregado da lateral de um balcão, pela face da chapa (+Z da peça).
base = tf.BaseCabinet()
base.create("Balcao")
hb_utils.run_calc_fix_until_stable(ctx, base.obj)
side = bpy.data.objects["Left Side"]
(lo, hi) = apply.local_box(side)
center_local = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] + 0.03))
nicho.matrix_world = side.matrix_world.normalized() @ __import__("mathutils").Matrix.Translation(center_local)
env.settle()
before = nicho.matrix_world.copy()
assert convert.convert(nicho, side, 'POS_Z') == 'POS_Z'
agg = nicho.btm_aggregate
assert agg.is_aggregate and nicho.parent == side
agg.u = 50.0
assert abs(agg.u - (hi[0] - lo[0] - agg.size[0])) < 1e-6, "parar na borda"
agg.offset = -0.030
assert abs(agg.offset + (hi[2] - lo[2])) < 1e-6, "afundar no máximo a espessura"
agg.offset = -0.010
agg.perforate = True
env.settle()
assert any(m.type == 'BOOLEAN' for m in side.modifiers) and agg.cutter is not None
assert perforate.real_hole_reason(nicho) is None
parts, _bad = part_extractor.extract_production_parts(ctx)
payload = json_exporter.build_global_payload(project={"name": "Smoke", "uid": "P", "rooms": []}, standard={},
                                             parts=parts, modules=part_extractor.module_entries(scene))
assert json_exporter.validate_global_json(payload) == []
assert payload["schema_version"] == "2.1.0"
assert not any(p["machining"] for p in payload["parts"]), "sem 'Furo real' a produção não muda"
agg.real_hole = True
env.settle()
assert side.modifiers.get(machining.AGGREGATE_PREFIX + nicho.name) is not None
parts, _bad = part_extractor.extract_production_parts(ctx)
payload = json_exporter.build_global_payload(project={"name": "Smoke", "uid": "P", "rooms": []}, standard={},
                                             parts=parts, modules=part_extractor.module_entries(scene))
cuts = [c for p in payload["parts"] for c in p["machining"]]
assert len(cuts) == 1 and cuts[0]["kind"] == "POCKET" and abs(cuts[0]["depth_mm"] - 10.0) < 0.2, cuts
assert json_exporter.validate_global_json(payload) == []
assert convert.unconvert(nicho)
assert not any(m.type == 'BOOLEAN' for m in side.modifiers)
assert side.modifiers.get(machining.AGGREGATE_PREFIX + nicho.name) is None
assert max_diff(nicho.matrix_world, before) < 1e-6 and nicho.parent is None

# 3. Folha de porta: giro de 180° batendo na parede a 30 cm da dobradiça.
env.clean_scene()
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.5, -0.3, 1.0))
frame = ctx.object
frame.name = "Batente"
frame.scale = (1.0, 0.6, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.5, -0.61, 1.0))
door = ctx.object
door.name = "Folha"
door.scale = (0.8, 0.02, 1.9)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.2, -1.0, 1.0))
wall = ctx.object
wall.name = "Parede"
wall.scale = (0.1, 1.0, 2.0)
env.settle()
closed = door.matrix_world.copy()
for obj in ctx.selected_objects:
    obj.select_set(False)
door.select_set(True)
frame.select_set(True)
ctx.view_layer.objects.active = frame
assert bpy.ops.caffmob.leaf_convert(motion='SWING', hinge='RIGHT', swing_sign='OUT', max_angle=180.0) == {'FINISHED'}
agg = door.btm_aggregate
agg.open_value = 1.0
env.settle()
assert agg.contact_name == "Parede" and 105.0 < agg.open_value * agg.max_angle < 110.0, agg.open_value
for _ in range(10):
    agg.open_value = 0.37
    agg.open_value = 0.0
env.settle()
assert max_diff(door.matrix_world, closed) < 1e-5

# 4. Abrir pela inspeção e salvar fechado com a folha aberta.
leaf_fronts = [f for f in fronts.iter_fronts(scene) if f.library == 'AGGREGATE']
assert len(leaf_fronts) == 1 and leaf_fronts[0].max_value == 180.0
leaf_fronts[0].commit(45.0)
env.settle()
assert abs(leaf_fronts[0].get() - 45.0) < 1e-6
blend = os.path.join(tempfile.mkdtemp(), "folha.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.wm.open_mainfile(filepath=blend)
env.settle()
leaf_fronts = [f for f in fronts.iter_fronts(bpy.context.scene) if f.library == 'AGGREGATE']
assert leaf_fronts and leaf_fronts[0].get() == 0.0, "salvar fechado vale para a folha convertida"

# 5. Porta de correr: 50% de 80 cm = 40 cm.
door = bpy.data.objects["Folha"]
assert convert.unconvert(door)
bpy.data.objects.remove(bpy.data.objects["Parede"], do_unlink=True)
leaf.make_leaf(door, bpy.data.objects["Batente"], 'SLIDE', slide_dir='POS_X', travel=0.8)
start = door.matrix_world.translation.x
door.btm_aggregate.open_value = 0.5
env.settle()
assert abs(door.matrix_world.translation.x - start - 0.4) < 1e-5
print("blender_003_aggregates_smoke: OK")
