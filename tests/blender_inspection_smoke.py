"""Teste de fumaça da inspeção e movimento (T053; incremento 3, bloco 1).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_inspection_smoke.py

Cobre as quatro origens de frente (frameless, face frame, closets e módulo rápido): abrir a 45° e 90°, conversão
para o estado de cada linha, salvar fechado com a tela aberta (RN-14), plano de corte não marcado ao abrir portas
(D-31), interferência com um obstáculo à frente da porta (RF-091) e "Evitar Sobreposição" no posicionamento (RN-13).
O controle giratório e o modo de clique precisam de janela e ficam fora deste teste.
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import blendertomob as addon  # noqa: E402

addon.register()
addon.load_file_post(None)

from blendertomob import hb_placement, hb_types, hb_utils  # noqa: E402
from blendertomob.inspection import fronts  # noqa: E402
from blendertomob.product_libraries.closets import types_closets as tc  # noqa: E402
from blendertomob.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from blendertomob.product_libraries.frameless import types_frameless as tf  # noqa: E402


def settle():
    for _ in range(3):
        bpy.context.view_layer.update()


def values(scene):
    return {(f.library, f.kind): round(f.get(), 3) for f in fronts.iter_fronts(scene)}


scene = bpy.context.scene
for obj in list(scene.objects):            # cena limpa: o cubo de fábrica atrapalharia a interferência
    bpy.data.objects.remove(obj, do_unlink=True)

# 1. Quatro origens de frente.
base = tf.BaseCabinet()
base.default_exterior = 'Door Drawer'
base.create("Balcao")
# Contorna o bug do Blender #133392 (drivers de netos não atualizam), como fazem os operadores do frameless.
hb_utils.run_calc_fix_until_stable(bpy.context, base.obj)
face_frame = tff.BaseFaceFrameCabinet()
face_frame.create("FaceFrame")
face_frame.obj.location.x = 3.0
settle()
opening = next(o for o in scene.objects if o.get(tff.TAG_OPENING_CAGE))
opening.face_frame_opening.front_type = 'DOOR'
opening.face_frame_opening.hinge_side = 'LEFT'
starter = tc.BaseClosetStarter()
starter.create_starter("Roupeiro", bay_qty=1)
starter.obj.location.x = 6.0
for obj in [o for o in scene.objects if o.get(tc.TAG_OPENING_CAGE)]:
    obj[tc.PROP_DOOR_SWING] = 'DOUBLE'
tc.recalculate_closet_starter(starter.obj)
assert bpy.ops.btm.cabinet_builder(width=0.6) == {'FINISHED'}
quick = bpy.context.object
quick.location.x = 9.5
quick.btm_cabinet.door_swing = 'LEFT'
settle()

kinds = {(f.library, f.kind) for f in fronts.iter_fronts(scene)}
for expected in [('FRAMELESS', 'DOOR'), ('FRAMELESS', 'DRAWER'), ('FACE_FRAME', 'DOOR'), ('CLOSETS', 'DOOR'),
                 ('BTM', 'DOOR')]:
    assert expected in kinds, (expected, kinds)

# 2. Plano de corte calculado; abrir portas não deve marcá-lo como desatualizado.
assert bpy.ops.btm.calculate_nesting() == {'FINISHED'}
settle()
assert not scene.btm_settings.cut_plan_stale

# 3. Abrir a 45° e 90° e conferir a conversão para cada linha.
assert bpy.ops.btm.fronts_set_open(scope='ALL', mode='OPEN_45') == {'FINISHED'}
settle()
assert all(v == 45.0 for (lib, kind), v in values(scene).items() if kind == 'DOOR'), values(scene)
assert bpy.ops.btm.fronts_set_open(scope='ALL', mode='OPEN_90') == {'FINISHED'}
settle()
opened = values(scene)
assert all(v == 90.0 for (lib, kind), v in opened.items() if kind == 'DOOR'), opened
assert opened[('FRAMELESS', 'DRAWER')] == 1.0, opened
assert abs(opening.face_frame_opening.swing_percent - 0.9) < 1e-6
closet_doors = [o for o in scene.objects if o.get('hb_part_role') == tc.PART_ROLE_DOOR]
assert closet_doors and all(abs(o['hb_door_open'] - 90 / 110) < 1e-6 for o in closet_doors)
controller = next(c for c in quick.children if c.name.endswith('_Controller'))
assert abs(controller.location.y - 0.2) < 1e-6
assert not scene.btm_settings.cut_plan_stale, "abrir portas marcou o plano de corte como desatualizado"

# 4. Interferência: obstáculo à frente da porta do balcão.
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.3, -0.9, 0.5))
bpy.context.object.name = "Obstaculo"
assert bpy.ops.btm.fronts_set_open(scope='ALL', mode='CLOSE') == {'FINISHED'}
settle()
assert bpy.ops.btm.check_front_interference(scope='ALL') == {'FINISHED'}
state = bpy.context.window_manager.btm_inspection
hits = {(i.module_name, i.hit_name) for i in state.interferences}
assert ('Balcao', 'Obstaculo') in hits, hits
assert state.checked_fronts >= 5
assert all(f.get() == 0 for f in fronts.iter_fronts(scene)), "a verificação deve restaurar a pose"
bpy.data.objects.remove(bpy.data.objects["Obstaculo"], do_unlink=True)

# 5. Salvar fechado, tela aberta; reabrir fechado (RN-14).
assert bpy.ops.btm.fronts_set_open(scope='ALL', mode='OPEN_90') == {'FINISHED'}
settle()
path = os.path.join(tempfile.mkdtemp(), "inspecao.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
assert all(v > 0 for v in values(bpy.context.scene).values()), "a tela deve continuar aberta depois de salvar"
bpy.ops.wm.open_mainfile(filepath=path)
settle()
scene = bpy.context.scene
assert all(v == 0 for v in values(scene).values()), values(scene)

# 6. "Evitar Sobreposição" (RN-13): um módulo na parede bloqueia o vão só com a opção ligada.
wall = hb_types.GeoNodeWall()
# Sem a extensão instalada não há preferências do add-on; cria a parede pelo objeto GN genérico (sem a cor).
hb_types.GeoNodeObject.create(wall, 'GeoNodeWall', "Parede")
wall.set_input('Length', 4.0)
blocker = tf.BaseCabinet()
blocker.default_exterior = 'Open'
blocker.create("Vizinho")
blocker.obj.parent = wall.obj
blocker.obj.location = (1.0, 0.0, 0.0)
settle()
mixin = hb_placement.PlacementMixin()
scene.btm_settings.collision_global = True
gap_on = mixin.find_placement_gap_by_side(wall.obj, 2.5, 0.6, True, 0.1)
scene.btm_settings.collision_global = False
gap_off = mixin.find_placement_gap_by_side(wall.obj, 2.5, 0.6, True, 0.1)
assert gap_on[0] > 1.0, gap_on            # o vão começa depois do vizinho
assert gap_off[0] == 0 and abs(gap_off[1] - 4.0) < 1e-6, gap_off   # parede inteira livre

# 7. Registro limpo.
addon.unregister()
assert not hasattr(bpy.types.WindowManager, 'btm_inspection')
assert bpy.types.GizmoGroup.bl_rna_get_subclass_py('BTM_GGT_front_open') is None
print('BLENDER_INSPECTION_SMOKE_OK', flush=True)
