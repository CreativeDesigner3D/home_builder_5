"""Teste de fumaça da feature 003, incrementos I1/I2 (T066): personalizar módulos das quatro bibliotecas e salvar
como módulo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_003_customize_smoke.py
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import adapters, library_io, reapply, spec  # noqa: E402
from caffmob_draw.customize.adapters import btm as ba  # noqa: E402
from caffmob_draw.customize.adapters import closets as ca  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.customize.adapters import face_frame as ffa  # noqa: E402
from caffmob_draw.customize.adapters import frameless as fa  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
scene = ctx.scene
env.clean_scene()
laca = bpy.data.materials.new("Laca branca")
mdf = bpy.data.materials.new("MDF carvalho")


def top_surface(obj):
    return common.compat.get_gn_input(common.gn_modifier(obj, 'GeoNodeCutpart'), 'Top Surface')


# 1. Frameless: frente, estilo, puxador, materiais, interior e reaplicação depois do estilo do projeto.
base = tf.BaseCabinet()
base.default_exterior = 'Doors'
base.create("Balcao")
hb_utils.run_calc_fix_until_stable(ctx, base.obj)
root = base.obj
assert adapters.for_root(root) is fa
assert fa.set_front(ctx, root, fa.openings(root)[0][1], 'DRAWERS', 3) == []
assert [fa.front_type(o)[0] for _p, o in fa.openings(root)] == ['DRAWERS'] * 3
assert fa.set_front(ctx, root, fa.openings(root)[0][1], 'DOOR_RIGHT') == []
style = scene.hb_frameless.door_styles.add()
style.name, style.door_type = "Vidro", '5_PIECE'
opening = fa.openings(root)[0][1]
opening.btm_custom.door_style = "Vidro"
opening.btm_custom.front_material = "Laca branca"
opening.btm_custom.pull_model = fa.pull_items()[0][0]
root.btm_custom.set_group_material('CAIXA', "MDF carvalho")
assert reapply.reapply(ctx, root) == []
doors = fa.fronts(opening)
assert doors and all(d.get('DOOR_STYLE_NAME') == "Vidro" and top_surface(d) == laca for d in doors)
side = bpy.data.objects["Left Side"]
assert top_surface(side) == mdf
bpy.ops.caffmob_frameless.update_cabinet_materials()
assert top_surface(side) == mdf, "o estilo do projeto apagou a personalização"
tall = tf.TallCabinet()
tall.create("Alto")
hb_utils.run_calc_fix_until_stable(ctx, tall.obj)
tall_opening = fa.openings(tall.obj)[0][1]
assert fa.set_interior(ctx, tall.obj, tall_opening, spec.Interior(shelves=1, heights=[5.0])) == ['altura fora do vão']
assert fa.set_interior(ctx, tall.obj, tall_opening, spec.Interior(shelves=2, heights=[0.2, 0.45])) == []
assert fa.set_interior(ctx, tall.obj, tall_opening, spec.Interior(drawers=2)) == []
assert len([o for o in fa.leaf_opening(tall_opening).children_recursive if o.name.startswith("Rollout")]) == 2

# 2. Salvar como módulo e inserir num arquivo novo.
ctx.view_layer.objects.active = root
with ctx.temp_override(active_object=root, object=root):
    assert bpy.ops.caffmob.module_save(module_name="Balcão vidro", category="Balcões", thumbnail=False) == {'FINISHED'}
    assert bpy.ops.caffmob.module_save(module_name="Balcão vidro", category="Balcões") == {'CANCELLED'}
entries = library_io.list_modules()
assert [(e['name'], e['category'], e['has_manifest']) for e in entries] == [("Balcão vidro", "Balcões", True)]

# 3. Face frame: troca de frente, estilo, puxador e material sobrevivem ao recálculo.
ff = tff.BaseFaceFrameCabinet()
ff.create("FaceFrame")
ff.obj.location.x = 3.0
env.settle()
ff_root = ff.obj
ff_opening = ffa.openings(ff_root)[0][1]
assert ffa.set_front(ctx, ff_root, ff_opening, 'DOUBLE_DOORS') == []
ff_style = scene.hb_face_frame.door_styles.add()
ff_style.name = "Shaker"
ff_opening.btm_custom.door_style = "Shaker"
ff_opening.btm_custom.front_material = "Laca branca"
assert reapply.reapply(ctx, ff_root) == []
ff_root.face_frame_cabinet.width = ff_root.face_frame_cabinet.width + 0.1
fronts_ff = ffa.fronts(ffa.openings(ff_root)[0][1])
assert fronts_ff and all(f.get('DOOR_STYLE_NAME') == "Shaker" and top_surface(f) == laca for f in fronts_ff)

# 4. Closets: frente e estilo por vão; o estilo volta depois do recálculo.
starter = tc.BaseClosetStarter()
starter.create_starter("Roupeiro", bay_qty=2)
starter.obj.location.x = 6.0
tc.recalculate_closet_starter(starter.obj)
cl_root = starter.obj
assert ca.set_front(ctx, cl_root, ca.openings(cl_root)[0][1], 'DOUBLE_DOORS') == []
assert ca.set_front(ctx, cl_root, ca.openings(cl_root)[1][1], 'FLIP_UP') != []
cl_opening = ca.openings(cl_root)[0][1]
cl_opening.btm_custom.door_style = 'WIDE_SHAKER'
tc.recalculate_closet_starter(cl_root)
assert all(f.get('DOOR_STYLE_NAME') == 'WIDE_SHAKER' for f in ca.fronts(cl_opening))

# 5. Módulo paramétrico (btm): prateleiras, materiais por grupo e puxador na borda livre.
assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
quick = ctx.object
assert ba.capabilities(quick)['STYLES']
assert ba.set_front(ctx, quick, quick, 'DOUBLE_DOORS') == []
assert ba.set_interior(ctx, quick, quick, spec.Interior(shelves=2)) == []
quick.btm_custom.set_group_material('CAIXA', "MDF carvalho")
quick.btm_custom.pull_model = ba.pull_items()[0][0]
assert reapply.reapply(ctx, quick) == []
assert quick.data.materials[0] == mdf
assert all(any(c.get('IS_CABINET_PULL') for c in d.children) for d in ba.door_controller.doors_of(quick))

# 6. Arquivo novo: o módulo salvo volta com a personalização.
bpy.ops.wm.read_homefile(use_empty=True)
env.addon.load_file_post(None)
ctx = bpy.context
assert bpy.ops.caffmob.module_insert(filepath=entries[0]['blend'], place=False) == {'FINISHED'}
inserted = ctx.view_layer.objects.active
read = fa.read(inserted).openings[0]
assert (read.door_style, read.front_material) == ("Vidro", "Laca branca"), read
print("blender_003_customize_smoke: OK")
