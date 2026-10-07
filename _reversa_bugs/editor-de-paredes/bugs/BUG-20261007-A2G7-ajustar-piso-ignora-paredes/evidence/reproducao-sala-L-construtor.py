import sys, bpy
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env
from caffmob_draw.walls2d import model, apply
from caffmob_draw.product_libraries.frameless import types_frameless as tf
from caffmob_draw import hb_utils
ctx=bpy.context; env.clean_scene()
segs=lambda n:[model.Segment(thickness=0.15,height=2.6) for _ in range(n)]
L=model.Chain([(0,0),(4,0),(4,2),(2,2),(2,4),(0,4)], segs(6), closed=True, side='LEFT')
L.side=L.outward_side()
apply.apply_plan(ctx, model.WallPlan([L])); env.settle()
walls=[o for o in ctx.scene.objects if o.get('IS_WALL_BP')]
print("walls", len(walls), "mesh verts", [len(w.data.vertices) for w in walls])
b=tf.BaseCabinet(); b.create("Balcao"); b.obj.location=(10,10,0); hb_utils.run_calc_fix_until_stable(ctx,b.obj)
print("cabinet kind", b.obj.btm_plane.object_kind, "IS_WALL_BP", b.obj.get('IS_WALL_BP'))
print(bpy.ops.caffmob.adjust_floor())
f=bpy.data.objects['BTM_Floor']; cs=[f.matrix_world@v.co for v in f.data.vertices]
print("floor verts", len(cs), [tuple(round(c[i],2) for i in range(2)) for c in cs][:10])
import bmesh
bm=bmesh.new(); bm.from_mesh(f.data); print("floor area", round(sum(fc.calc_area() for fc in bm.faces),3), "expected L inner area 12.0"); bm.free()
