import sys, bpy
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env
from caffmob_draw.walls2d import model, apply
from mathutils import Vector
ctx=bpy.context; env.clean_scene()
plan=model.WallPlan([model.rectangle(4.0, 3.0)])
apply.apply_plan(ctx, plan)
env.settle()
walls=[o for o in ctx.scene.objects if o.get('IS_WALL_BP')]
print("HB walls", len(walls), "kinds", sorted({o.btm_plane.object_kind for o in ctx.scene.objects}))
print("adjust_floor", bpy.ops.caffmob.adjust_floor())
f=[o for o in ctx.scene.objects if o.name.startswith('BTM_Floor')][0]
cs=[f.matrix_world@v.co for v in f.data.vertices]
print("floor bbox", [round(min(c[i] for c in cs),3) for i in range(2)], [round(max(c[i] for c in cs),3) for i in range(2)], "verts", len(cs))
ws=[]
for w in walls:
    ev=w.evaluated_get(ctx.evaluated_depsgraph_get()); ws+= [w.matrix_world@Vector(c) for c in ev.bound_box]
print("walls bbox", [round(min(c[i] for c in ws),3) for i in range(2)], [round(max(c[i] for c in ws),3) for i in range(2)])
