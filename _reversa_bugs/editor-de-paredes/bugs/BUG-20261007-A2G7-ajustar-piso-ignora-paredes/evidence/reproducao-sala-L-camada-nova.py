import sys, bpy, json, bmesh
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env
from caffmob_draw.geometry.mesh_gen import generate_wall_from_segments
ctx=bpy.context; env.clean_scene()
pts=[(0,0),(4,0),(4,2),(2,2),(2,4),(0,4),(0,0)]
segs=[{'start':list(a),'end':list(b),'thickness':0.15,'height':2.6,'offset':0.0} for a,b in zip(pts,pts[1:])]
me=bpy.data.meshes.new("W"); w=bpy.data.objects.new("ParedeNova", me); ctx.collection.objects.link(w)
w["btm_wall_segments"]=json.dumps(segs); w.btm_plane.object_kind='WALL'
from mathutils import Vector
generate_wall_from_segments(w, [{'start':Vector(a),'end':Vector(b),'thickness':0.15,'height':2.6,'offset':0.0} for a,b in zip(pts,pts[1:])])
print("verts", len(w.data.vertices))
print(bpy.ops.caffmob.adjust_floor())
f=bpy.data.objects['BTM_Floor']; bm=bmesh.new(); bm.from_mesh(f.data)
xs=[ (f.matrix_world@v.co) for v in f.data.vertices]
print("floor area", round(sum(fc.calc_area() for fc in bm.faces),3), "bbox", [round(min(c[i] for c in xs),3) for i in range(2)], [round(max(c[i] for c in xs),3) for i in range(2)], "L inner area ~", round((4-0.15)*(2-0.15)+(2-0.15)*(2)  ,2))
