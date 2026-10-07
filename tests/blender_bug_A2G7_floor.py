"""Reprodução e regressão do BUG-20261007-A2G7: "Ajustar Piso" ignora as paredes.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_A2G7_floor.py
"""

import json
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.geometry.mesh_gen import generate_wall_from_segments  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context


def floor():
    return next(o for o in ctx.scene.objects if o.btm_plane.object_kind == 'FLOOR')


def floor_box_and_area():
    obj = floor()
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    area = sum(f.calc_area() for f in bm.faces)
    bm.free()
    lo = tuple(round(min(p[i] for p in pts), 3) for i in range(2))
    hi = tuple(round(max(p[i] for p in pts), 3) for i in range(2))
    return lo, hi, round(area, 3)


def l_chain():
    segs = [model.Segment(thickness=0.15, height=2.6) for _ in range(6)]
    chain = model.Chain([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)], segs, closed=True, side='LEFT')
    chain.side = chain.outward_side()
    return chain


# 1. Reprodução: sala 4 x 3 m pelo editor de paredes → piso na face interna (0..4 x 0..3), não 5 x 5 m na origem.
env.clean_scene()
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
env.settle()
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
lo, hi, area = floor_box_and_area()
assert (lo, hi) == ((0.0, 0.0), (4.0, 3.0)) and abs(area - 12.0) < 1e-3, (lo, hi, area)

# 2. Reprodução: sala em L do editor com um balcão na cena → área do L interno (12 m²); o balcão não é parede.
env.clean_scene()
apply.apply_plan(ctx, model.WallPlan([l_chain()]))
cab = tf.BaseCabinet()
cab.create("Balcao")
cab.obj.location = (10.0, 10.0, 0.0)
hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
env.settle()
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
lo, hi, area = floor_box_and_area()
assert abs(area - 12.0) < 1e-3 and hi == (4.0, 4.0), (lo, hi, area)

# 3. Regressão: sala em L da camada nova (linha de centro) → face interna, sem cobrir o recorte.
env.clean_scene()
pts = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4), (0, 0)]
mesh = bpy.data.meshes.new("Parede")
wall = bpy.data.objects.new("ParedeNova", mesh)
ctx.collection.objects.link(wall)
wall.btm_plane.object_kind = 'WALL'
wall["btm_wall_segments"] = json.dumps([{'start': list(a), 'end': list(b), 'thickness': 0.15, 'height': 2.6,
                                         'offset': 0.0} for a, b in zip(pts, pts[1:])])
generate_wall_from_segments(wall, [{'start': Vector(a), 'end': Vector(b), 'thickness': 0.15, 'height': 2.6,
                                    'offset': 0.0} for a, b in zip(pts, pts[1:])])
env.settle()
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
lo, hi, area = floor_box_and_area()
assert abs(area - (3.85 * 1.85 + 1.85 * 2.0)) < 1e-3 and lo == (0.075, 0.075), (lo, hi, area)

# 4. Regressão: mudar as paredes e ajustar de novo atualiza o mesmo piso, sem deslocamento.
env.clean_scene()
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
env.settle()
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
first = floor()
first.location = (1.0, 1.0, 0.0)          # piso deslocado por engano (ou por um ajuste antigo)
for obj in [o for o in ctx.scene.objects if o.get('IS_WALL_BP')]:
    bpy.data.objects.remove(obj, do_unlink=True)
apply.apply_plan(ctx, model.WallPlan([model.rectangle(5.0, 3.0)]))
env.settle()
assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
assert floor() == first and first.matrix_world == Matrix.Identity(4)
lo, hi, area = floor_box_and_area()
assert (lo, hi) == ((0.0, 0.0), (5.0, 3.0)), (lo, hi)
print("blender_bug_A2G7_floor: OK")
