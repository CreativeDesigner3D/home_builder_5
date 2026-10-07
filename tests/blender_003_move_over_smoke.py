"""Teste de fumaça da feature 003, incremento I5 (T068): Mover Sobre ampliado.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_003_move_over_smoke.py

Cobre a camada de cena da janela (o modal precisa de janela e fica no roteiro manual do onboarding): X digitado,
rotação 90° pelo centro da base, cancelar devolvendo posição e rotação, relativa/absoluta sem mover, posição salva
aplicada a outro par, Substituir por módulo da biblioteca e o plano de inserção gravado.
"""

import sys
import types
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import library_io  # noqa: E402
from caffmob_draw.move_over import insertion_plane, ops_substitute  # noqa: E402
from caffmob_draw.move_over.scene import MoveOver  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
scene = ctx.scene
env.clean_scene()


def cabinet(cls, name, x):
    item = cls()
    item.create(name)
    item.obj.location.x = x
    hb_utils.run_calc_fix_until_stable(ctx, item.obj)
    return item.obj


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


b1 = cabinet(tf.BaseCabinet, "Balcao", 0.0)
a1 = cabinet(tf.BaseCabinet, "Nicho", 2.0)
env.settle()
original = a1.matrix_world.copy()

# 1. X digitado, rotação de 90° (centro da base parado), cancelar devolve tudo.
mo = MoveOver(ctx, a1, b1)
mo.set_gap(0, 0.15)
env.settle()
assert close(mo.gaps()[0], 0.15)
center_before = (Vector(mo.box_a()[0]) + Vector(mo.box_a()[1])) / 2
mo.set_rotation(90.0)
env.settle()
center_after = (Vector(mo.box_a()[0]) + Vector(mo.box_a()[1])) / 2
assert close(center_before.x, center_after.x) and close(center_before.y, center_after.y)
assert close(a1.matrix_world.to_euler().z, b1.matrix_world.to_euler().z + 1.5707963, 1e-4)
before_abs = mo.world_min()
moved = a1.matrix_world.copy()
assert before_abs == mo.world_min() and a1.matrix_world == moved, "trocar relativa/absoluta não move"
mo.restore()
env.settle()
assert all(close(x, y) for ra, rb in zip(a1.matrix_world, original) for x, y in zip(ra, rb))

# 2. Passo do teclado e modo absoluto.
mo = MoveOver(ctx, a1, b1)
x0 = mo.world_min()[0]
mo.nudge((0.01, 0.0, 0.0))
assert close(mo.world_min()[0] - x0, 0.01)
mo.set_world(2, 0.5)
env.settle()
assert close(mo.world_min()[2], 0.5)

# 3. Posição salva aplicada a outro par.
mo.set_gap(0, 0.15)
saved = mo.saved()
b2 = cabinet(tf.BaseCabinet, "Balcao 2", 5.0)
a2 = cabinet(tf.BaseCabinet, "Nicho 2", 8.0)
env.settle()
mo2 = MoveOver(ctx, a2, b2)
mo2.apply_saved(saved)
env.settle()
assert close(mo2.gaps()[0], mo.gaps()[0]) and close(mo2.gaps()[2], mo.gaps()[2]), (mo.gaps(), mo2.gaps())

# 4. Substituir por módulo da biblioteca: mesmo canto de referência, o antigo some.
upper = cabinet(tf.UpperCabinet, "Aereo", 12.0)
ctx.view_layer.objects.active = upper
with ctx.temp_override(active_object=upper, object=upper):
    assert bpy.ops.caffmob.module_save(module_name="Aéreo base", category="Testes", thumbnail=False) == {'FINISHED'}
entry = library_io.list_modules()[0]
right_of_b = mo2.box_a()[0][0]
new, warnings = ops_substitute.substitute(ctx, a2, b2, entry)
env.settle()
assert new is not None and "Nicho 2" not in bpy.data.objects
check = MoveOver(ctx, new, b2)
assert close(check.box_a()[0][0], right_of_b, 1e-3), (check.box_a()[0][0], right_of_b)

# 5. Plano de inserção gravado (a escolha pelo clique precisa de janela).
fake = types.SimpleNamespace(report=lambda *args: None)
insertion_plane.BTM_OT_SetInsertionPlane.set_plane(fake, ctx, Vector((0, 0, 0.9)), Vector((0, 0, 1)), "Balcao")
plane = ctx.window_manager.btm_insertion_plane
assert plane.active and close(plane.matrix[11], 0.9) and plane.source_name == "Balcao"
with ctx.temp_override():
    assert bpy.ops.caffmob.clear_insertion_plane() == {'FINISHED'}
assert not plane.active
print("blender_003_move_over_smoke: OK")
