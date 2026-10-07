"""Teste de fumaça da feature 002 (T040): editor de paredes, geometria, operações de parede e movimento.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_002_smoke.py

Cobre: registro e remoção de tudo o que a 002 adiciona; Editor de Paredes (desenho a lápis com digitação, fechamento,
seleção da linha externa, remoção de trecho, aplicação e releitura; sala 3,9 × 2,7 com medida interna); geometria
livre (placa e caixa, espessura sem mover a face de apoio, peças `FREE_GEOMETRY` no JSON v2, duplicar, espelhar e
excluir); remover parede (Segmento / Manter o selecionado), rebaixar e invisível; "Mover na Parede" parando no
vizinho. A janela do editor, o modal do "Mover Sobre" e a criação por pontos precisam de janela e ficam fora.
"""

import sys
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
addon.load_file_post(None)

from caffmob_draw import hb_types, hb_utils  # noqa: E402
from caffmob_draw.canvas2d.view import View2D  # noqa: E402
from caffmob_draw.cutting import json_exporter, part_extractor  # noqa: E402
from caffmob_draw.geometry_free import mesh  # noqa: E402
from caffmob_draw.measure import scene_cotas  # noqa: E402
from caffmob_draw.move_over import align, ops_move_on_wall  # noqa: E402
from caffmob_draw.move_over import scene as move_scene  # noqa: E402
from caffmob_draw.operators import ops_wall_extras  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402
from caffmob_draw.walls2d import apply, model, ops_editor, props, scene_io, window  # noqa: E402

ctx = bpy.context
scene = ctx.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
# Sem a extensão instalada não há preferências do add-on (cor da parede); o construtor de paredes precisa delas.
type(ctx.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0))


def walls():
    return [o for o in scene.objects if o.get('IS_WALL_BP')]


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


# 1. Registro.
for idname in ('CAFFMOB_OT_wall_editor', 'CAFFMOB_OT_wall_editor_modal', 'CAFFMOB_OT_wall_editor_ok', 'CAFFMOB_OT_wall_remove',
               'CAFFMOB_OT_wall_lower', 'CAFFMOB_OT_wall_visibility', 'CAFFMOB_OT_geometry_create', 'CAFFMOB_OT_geometry_duplicate',
               'CAFFMOB_OT_move_on_wall', 'CAFFMOB_OT_move_over_drag'):
    assert bpy.types.Operator.bl_rna_get_subclass_py(idname) is not None, idname
for idname in ('BTM_PT_wall_editor_tools', 'BTM_PT_wall_editor_segment', 'BTM_PT_wall_editor_grid',
               'BTM_PT_object_properties'):
    assert bpy.types.Panel.bl_rna_get_subclass_py(idname) is not None, idname
assert hasattr(ctx.window_manager, 'btm_wall_editor') and hasattr(bpy.types.Object, 'btm_geometry')

# 2. Editor de Paredes: campos do trecho sobre o rascunho (sala interna 3,6 × 2,4, 150 mm; externa 3,9 × 2,7).
s = props.start(model.WallPlan([model.rectangle(3.6, 2.4)]), scene.name)
state = ctx.window_manager.btm_wall_editor
s.selected = (0, 0)
state.line = 'INNER'
assert close(state.length, 3.6), state.length
state.line = 'OUTER'
assert close(state.length, 3.9), state.length
assert state.direction == 'RIGHT'                         # espessura para fora
state.line = 'INNER'
state.thickness = 50.0
assert s.error.startswith("Valor Inválido"), s.error
state.wall_type = 'DIVISORIA'
assert close(s.plan.chains[0].segments[0].thickness, 0.1)
props.end()

# 3. Editor de Paredes: lápis (digitação + cliques), fechar, selecionar, remover trecho (modal com eventos simulados).
s = props.start(model.WallPlan([]), scene.name)
s.view = View2D((0, 0, 1000, 800))
s.view.fit(((-1, -1), (5, 4)), margin=0.1)
window.editor_area = lambda c: (None, None, types.SimpleNamespace(width=1000, height=800, x=0, y=0))
op = types.SimpleNamespace(dragging=None, panning=None)
for name in ('_handle', '_handle_click', '_handle_draw', '_append', '_finish_drawing', '_handle_prompt',
             '_handle_typing', '_answer_no'):
    setattr(op, name, getattr(ops_editor.BTM_OT_WallEditorModal, name).__get__(op))


def event(kind, value='PRESS', char=''):
    return types.SimpleNamespace(type=kind, value=value, unicode=char)


def at(world, ev):
    s.cursor = world
    return op._handle(ctx, ev, s, s.view, s.view.to_screen(world))


state.tool = 'DRAW'
at((0.0, 0.0), event('LEFTMOUSE'))
s.cursor = (1.0, 0.01)                     # quase horizontal: trava ortogonal
for char in "3000":
    op._handle(ctx, event('ONE', char=char), s, s.view, s.view.to_screen(s.cursor))
op._handle(ctx, event('RET'), s, s.view, s.view.to_screen(s.cursor))
assert s.drawing.nodes[-1] == (3.0, 0.0), s.drawing.nodes
at((3.0, 2.0), event('LEFTMOUSE'))
at((0.0, 2.0), event('LEFTMOUSE'))
at((0.0, 0.0), event('LEFTMOUSE'))
assert s.prompt == 'close'
_box, yes, _no = ops_editor._prompt_rects(types.SimpleNamespace(width=1000, height=800))
op._handle(ctx, event('LEFTMOUSE'), s, s.view, (yes[0] + 5, yes[1] + 5))
chain = s.plan.chains[0]
assert chain.closed and chain.segment_count() == 4 and state.tool == 'SELECT'
at((1.5, 0.0), event('LEFTMOUSE'))
at((1.5, 0.0), event('LEFTMOUSE', 'RELEASE'))
assert s.selected == (0, 0) and s.line == model.INNER     # a linha dos vértices é a face interna (D-25)
assert chain.side == 'RIGHT'                              # desenhada no anti-horário: espessura para fora
op._handle(ctx, event('DEL'), s, s.view, (0, 0))
assert [(c.closed, c.segment_count()) for c in s.plan.chains] == [(False, 3)]
report = apply.apply_plan(ctx, s.plan)
props.end()
assert len(report['created']) == 3 and len(walls()) == 3, report
reread = scene_io.read_plan(scene)
assert [(c.closed, c.segment_count()) for c in reread.chains] == [(False, 3)]
for obj in walls():
    ops_wall_extras.remove_wall(obj)
assert not walls()

# 3b. Sala de 4 paredes: dividir um trecho e editar o comprimento; cancelar não muda a cena.
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
before = sorted(round(hb_types.GeoNodeWall(o).get_input('Length'), 4) for o in walls())
plan = scene_io.read_plan(scene)
plan.chains[0].split(0, (2.0, 0.0))
plan.chains[0].set_length(1, 2.5)
assert sorted(round(hb_types.GeoNodeWall(o).get_input('Length'), 4) for o in walls()) == before   # rascunho
report = apply.apply_plan(ctx, plan)
assert len(report['created']) == 1 and len(walls()) == 5, report
assert scene_io.read_plan(scene).chains[0].closed
for obj in walls():
    ops_wall_extras.remove_wall(obj)

# 3c. Pisos e tetos existentes acompanham o contorno no OK (A005); paredes da camada nova aparecem como referência
#     na planta (A004).
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
assert bpy.ops.caffmob_walls.add_floor() == {'FINISHED'}
floor = next(o for o in scene.objects if o.get('IS_FLOOR_BP'))
floor_width = floor.dimensions.x + floor.dimensions.y
plan = scene_io.read_plan(scene)
plan.chains[0].set_length(0, 5.0)
report = apply.apply_plan(ctx, plan)
ctx.view_layer.update()
assert report['floors'] == 1 and floor.name in scene.objects, report
assert floor.dimensions.x + floor.dimensions.y > floor_width + 0.5, (floor_width, tuple(floor.dimensions))
for obj in walls():
    ops_wall_extras.remove_wall(obj)
bpy.data.objects.remove(floor, do_unlink=True)
from caffmob_draw.geometry import mesh_gen  # noqa: E402
btm_wall = bpy.data.objects.new("ParedeNova", bpy.data.meshes.new("ParedeNova"))
scene.collection.objects.link(btm_wall)
btm_wall.btm_plane.object_kind = 'WALL'
mesh_gen.generate_wall_mesh(btm_wall, 3.0, 0.15, 2.6)
refs = scene_io.read_plan(scene).references
assert len(refs) == 4 and not scene_io.read_plan(scene).chains, refs
bpy.data.objects.remove(btm_wall, do_unlink=True)

# 3d. Cliques sobre o painel lateral do editor não vão para a planta (A001).
fake_ui = types.SimpleNamespace(type='UI', x=834, y=5, width=280, height=552)
fake_win = types.SimpleNamespace(type='WINDOW', x=5, y=5, width=1109, height=552)
fake_area = types.SimpleNamespace(regions=[fake_win, fake_ui])
assert window.over_side_panel(fake_area, 900, 300) and not window.over_side_panel(fake_area, 400, 300)
assert window.visible_width(fake_area, fake_win) == 829
s = props.start(model.WallPlan([]), scene.name)
window.editor_area = lambda c: (None, fake_area, fake_win)
local = types.SimpleNamespace(dragging=None, panning=None)
local_fn = ops_editor.BTM_OT_WallEditorModal._local.__get__(local)
assert local_fn(ctx, types.SimpleNamespace(mouse_x=900, mouse_y=300)) == (None, None)
assert local_fn(ctx, types.SimpleNamespace(mouse_x=400, mouse_y=300))[1] == (395, 295)
props.end()

# 3e. Todo operador citado nos painéis, menus e HUD do add-on existe (A002).
import re  # noqa: E402
missing = set()
for path in (ROOT / "caffmob_draw").rglob("*.py"):
    for idname in re.findall(r'\.operator(?:_menu_enum)?\(\s*"([a-z0-9_]+\.[a-z0-9_]+)"', path.read_text()):
        module, name = idname.split(".")
        try:
            getattr(getattr(bpy.ops, module), name).get_rna_type()
        except (AttributeError, KeyError):
            missing.add(f"{path.relative_to(ROOT)}: {idname}")
assert not missing, sorted(missing)

# 4. Geometria livre.
placa = mesh.create_object(ctx, 'PLACA')
g = placa.btm_geometry
g.width, g.depth, g.thickness = 0.8, 0.5, 0.018
assert close(placa.dimensions.z, 0.018)
g.thickness = 0.025
assert close(placa.dimensions.z, 0.025) and close(min(v.co.z for v in placa.data.vertices), 0.0)
g.fabrication, g.material = True, "MDF 25"
caixa = mesh.create_object(ctx, 'CAIXA')
cg = caixa.btm_geometry
cg.width, cg.depth, cg.height, cg.thickness, cg.fabrication = 0.6, 0.5, 0.7, 0.018, True
parts, _bad = part_extractor.extract_production_parts(ctx)
free = [p for p in parts if p.source == "FREE_GEOMETRY"]
assert len(free) == 7 and all(p.module_uid is None for p in free), [(p.name, p.module_uid) for p in free]
assert any(p.material == "MDF 25" and close(p.thickness, 25.0) for p in free)
payload = json_exporter.build_global_payload(project={"name": "Smoke", "uid": "P", "rooms": []},
                                             standard={"uid": "S", "name": "S"}, parts=parts,
                                             modules=part_extractor.module_entries(scene))
assert json_exporter.validate_global_json(payload) == [], json_exporter.validate_global_json(payload)
with ctx.temp_override(active_object=placa, selected_objects=[placa]):
    assert bpy.ops.caffmob.geometry_duplicate() == {'FINISHED'}
copy = ctx.view_layer.objects.active
assert copy != placa and close(copy.location.x, 0.8) and close(copy.btm_geometry.thickness, 0.025)
with ctx.temp_override(active_object=copy):
    bpy.ops.caffmob.geometry_mirror()
assert close(copy.location.x, 0.0)
name = copy.name
with ctx.temp_override(active_object=copy):
    bpy.ops.caffmob.geometry_delete()
assert name not in bpy.data.objects
for obj in (placa, caixa):
    bpy.data.objects.remove(obj, do_unlink=True)

# 5. Operações de parede: rebaixar, invisível, remover Segmento (módulo fica solto) e Manter o selecionado.
apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
first = walls()[0]
assert len(ops_wall_extras.chain_of(first)) == 4
loose = mesh.create_object(ctx, 'CAIXA', "Solto")
loose.parent = first
with ctx.temp_override(active_object=first, selected_objects=[first]):
    bpy.ops.caffmob.wall_lower()
assert first.get('btm_wall_lowered') and first.hide_viewport
assert any(c.get('btm_lowered_proxy') for c in first.children)
with ctx.temp_override(active_object=first, selected_objects=[first]):
    bpy.ops.caffmob.wall_lower()
assert not first.get('btm_wall_lowered') and not first.hide_viewport
assert not any(c.get('btm_lowered_proxy') for c in first.children)
with ctx.temp_override(active_object=first, selected_objects=[first]):
    bpy.ops.caffmob.wall_visibility(mode='WIRE')
assert first.display_type == 'WIRE'
with ctx.temp_override(active_object=first, selected_objects=[first]):
    bpy.ops.caffmob.wall_visibility(mode='VISIBLE')
assert first.display_type == 'TEXTURED'
with ctx.temp_override(active_object=first, selected_objects=[first]):
    bpy.ops.caffmob.wall_remove(mode='SEGMENT', remove_modules=False)
assert len(walls()) == 3 and bpy.data.objects["Solto"].parent is None
assert [(c.closed, c.segment_count()) for c in scene_io.read_plan(scene).chains] == [(False, 3)]
keep = walls()[0]
with ctx.temp_override(active_object=keep, selected_objects=[keep]):
    bpy.ops.caffmob.wall_remove(mode='KEEP')
assert walls() == [keep]

# 6. "Mover na Parede": o balcão desliza ao longo da parede e para no vizinho.
wall = hb_types.GeoNodeWall(keep)
wall.set_input('Length', 4.0)
neighbor = tf.BaseCabinet()
neighbor.default_exterior = 'Open'
neighbor.create("Vizinho")
neighbor.obj.parent = keep
neighbor.obj.location = (0.5, 0.0, 0.0)
moving = tf.BaseCabinet()
moving.default_exterior = 'Open'
moving.create("Balcao")
moving.obj.parent = keep
moving.obj.location = (2.0, 0.0, 0.0)
hb_utils.run_calc_fix_until_stable(ctx, moving.obj)
ctx.view_layer.update()
scene.btm_settings.collision_global = True
mc = scene_cotas.for_object(moving.obj, scene)
assert mc is not None and mc.on_wall
drag = types.SimpleNamespace(mc=mc, start=mc.placement, grab=types.SimpleNamespace(x=2.0, z=0.0))
drag._header = lambda c: None
move = ops_move_on_wall.BTM_OT_MoveOnWall._move.__get__(drag)
move(ctx, types.SimpleNamespace(x=2.5, z=0.0), False)
assert close(moving.obj.location.x, 2.5)
move(ctx, types.SimpleNamespace(x=-5.0, z=0.0), False)
neighbor_end = 0.5 + hb_types.GeoNodeObject(neighbor.obj).get_input('Dim X')
assert close(moving.obj.location.x, neighbor_end), (moving.obj.location.x, neighbor_end)
assert close(moving.obj.location.y, 0.0)                    # não se afasta da parede

# 6b. Classificador (frente → módulo) e "Mover Sobre" pela camada de cena: encostar à direita e cancelar.
info = classify.classify(moving.obj)
assert info.kind == classify.MODULE and info.library == 'FRAMELESS', info
part = next(o for o in moving.obj.children_recursive if o.type == 'MESH')
assert classify.classify(part).root == moving.obj
starter = tc.BaseClosetStarter()
starter.create_starter("Roupeiro", bay_qty=1)
assert classify.classify(starter.obj).library == 'CLOSETS'
ctx.view_layer.update()
original = moving.obj.matrix_world.copy()
mo = move_scene.MoveOver(ctx, moving.obj, neighbor.obj)
mo.align_to([align.Target(align.RIGHT, None)])
box_a, box_b = mo.box_a(), mo.box_b
assert close(box_a[0][0], box_b[1][0]), (box_a, box_b)
mo.restore()
assert (moving.obj.matrix_world.translation - original.translation).length < 1e-6

# 6c. Revisão de 2026-10-05: módulos de trecho apagado (D-21) e conversão de paredes da camada nova (D-22).
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for remove_modules in (False, True):
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    wall0 = walls()[0]
    module = mesh.create_object(ctx, 'CAIXA', "ModuloNaParede")
    module.parent = wall0
    plan = scene_io.read_plan(scene)
    ci, si = next((ci, si) for ci, c in enumerate(plan.chains) for si, sg in enumerate(c.segments)
                  if sg.source == wall0.name)
    s = types.SimpleNamespace(plan=plan, selected=(ci, si))
    ops_editor.remove_segment(s, ci, si)
    assert apply.modules_of_removed(plan) == [(wall0.name, "ModuloNaParede")], apply.modules_of_removed(plan)
    apply.apply_plan(ctx, plan, remove_modules=remove_modules)
    if remove_modules:
        assert "ModuloNaParede" not in bpy.data.objects
    else:
        assert bpy.data.objects["ModuloNaParede"].parent is None
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

import json  # noqa: E402
old_wall = bpy.data.objects.new("ParedeAntiga", bpy.data.meshes.new("ParedeAntiga"))
scene.collection.objects.link(old_wall)
old_wall.btm_plane.object_kind = 'WALL'
square = [((0, 0), (4, 0)), ((4, 0), (4, 3)), ((4, 3), (0, 3)), ((0, 3), (0, 0))]
old_wall["btm_wall_segments"] = json.dumps([{'start': a, 'end': b, 'thickness': 0.2, 'height': 2.7, 'offset': 0.0}
                                            for a, b in square])
mesh_gen.generate_wall_from_segments(old_wall, [{'start': a, 'end': b, 'thickness': 0.2, 'height': 2.7}
                                                for a, b in square])
old_wall.location = (1.0, 0.0, 0.0)
ctx.view_layer.update()
assert scene_io.is_other_layer_wall(old_wall)
plan = scene_io.read_plan(scene)
assert plan.references and not plan.chains
assert scene_io.convert_into(plan, [old_wall], scene) == []
assert not plan.references and plan.chains[0].closed and plan.chains[0].side == 'RIGHT'
apply.apply_plan(ctx, plan)
assert "ParedeAntiga" not in bpy.data.objects and len(walls()) == 4
assert all(close(hb_types.GeoNodeWall(w).get_input('Thickness'), 0.2) for w in walls())
assert all(close(hb_types.GeoNodeWall(w).get_input('Height'), 2.7) for w in walls())
reread = scene_io.read_plan(scene).chains[0]
xs = [n[0] for n in reread.nodes]
# vértices = face interna: linha de centro (1..5) menos meia espessura (0,1) de cada lado
assert reread.closed and close(min(xs), 1.1, 1e-3) and close(max(xs), 4.9, 1e-3), reread.nodes
outer_x = [p[0] for i in range(reread.segment_count()) for p in reread.outer_line(i)]
assert close(min(outer_x), 0.9, 1e-3) and close(max(outer_x), 5.1, 1e-3), outer_x     # mesmo corpo de parede
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# 6e. Direção (D-25): salas nos dois sentidos com a espessura para fora e o lado −Y (frente dos módulos) para dentro;
#     trocar a Direção mantém a medida interna e os módulos no lugar; digitação direta (D-27); Cancelar pergunta (D-30).
from mathutils import Vector as _V  # noqa: E402


def interior_ok(points, lo=(0.0, 0.0), hi=(3.0, 2.0), tol=1e-3):
    return all(lo[0] - tol <= p.x <= hi[0] + tol and lo[1] - tol <= p.y <= hi[1] + tol for p in points)


ccw = model.rectangle(3.0, 2.0, thickness=0.15)                                   # anti-horário, Direção direita
cw = model.Chain(list(reversed(ccw.nodes)), [model.Segment(0.15) for _ in range(4)], closed=True, side='LEFT')
for label, room in (("anti-horário", ccw), ("horário", cw)):
    apply.apply_plan(ctx, model.WallPlan([room]))
    ctx.view_layer.update()
    for w in walls():
        dg = ctx.evaluated_depsgraph_get()
        corners = [w.matrix_world @ _V(c) for c in w.evaluated_get(dg).bound_box]
        assert not all(0.01 < p.x < 2.99 and 0.01 < p.y < 1.99 for p in corners), (label, w.name, "parede dentro")
        probe = w.matrix_world @ _V((0.5, -0.3, 0.0))                             # frente de um módulo (−Y local)
        assert interior_ok([probe]), (label, w.name, tuple(probe))
    reread = scene_io.read_plan(scene).chains[0]
    assert sorted(round(reread.length(i), 4) for i in range(4)) == [2.0, 2.0, 3.0, 3.0], (label, reread.nodes)
    for w in walls():
        ops_wall_extras.remove_wall(w)

apply.apply_plan(ctx, model.WallPlan([model.rectangle(3.0, 2.0)]))
wall_a = walls()[0]
box = mesh.create_object(ctx, 'CAIXA', "PresoNaParede")
box.parent = wall_a
box.location = (0.5, -0.5, 0.0)
ctx.view_layer.update()
world_before = box.matrix_world.translation.copy()
plan = scene_io.read_plan(scene)
inner_before = sorted(round(plan.chains[0].length(i), 4) for i in range(4))
plan.chains[0].side = 'RIGHT' if plan.chains[0].side == 'LEFT' else 'LEFT'        # troca a Direção
apply.apply_plan(ctx, plan)
ctx.view_layer.update()
plan = scene_io.read_plan(scene)
assert sorted(round(plan.chains[0].length(i), 4) for i in range(4)) == inner_before
assert (box.matrix_world.translation - world_before).length < 1e-4, "o item preso fica no lugar"
for w in walls():
    ops_wall_extras.remove_wall(w)
bpy.data.objects.remove(box, do_unlink=True)

s = props.start(model.WallPlan([model.rectangle(3.0, 2.0)]), scene.name)
s.view = View2D((0, 0, 1000, 800))
s.view.fit(((-1, -1), (4, 3)), margin=0.1)
window.editor_area = lambda c: (None, None, types.SimpleNamespace(width=1000, height=800, x=0, y=0))
state.tool = 'SELECT'
at((1.5, 0.0), event('LEFTMOUSE'))
at((1.5, 0.0), event('LEFTMOUSE', 'RELEASE'))
assert s.selected == (0, 0) and s.line == model.INNER
for char in "3500":
    op._handle(ctx, event('ONE', char=char), s, s.view, s.view.to_screen((1.5, 0.0)))
op._handle(ctx, event('RET'), s, s.view, s.view.to_screen((1.5, 0.0)))
assert close(s.plan.chains[0].length(0), 3.5), s.plan.chains[0].length(0)
at((3.0, 2.0), event('LEFTMOUSE'))                                    # vértice 2: trecho 1 termina nele
at((3.0, 2.0), event('LEFTMOUSE', 'RELEASE'))
assert s.selected_node == (0, 2), s.selected_node
for char in "2500":
    op._handle(ctx, event('ONE', char=char), s, s.view, s.view.to_screen((3.0, 2.0)))
op._handle(ctx, event('RET'), s, s.view, s.view.to_screen((3.0, 2.0)))
assert close(s.plan.chains[0].length(1), 2.5), s.plan.chains[0].length(1)
assert s.dirty()
op._handle(ctx, event('ESC'), s, s.view, (10, 10))
assert s.prompt == 'discard' and s.request is None, "Cancelar com alterações pergunta"
op._handle(ctx, event('ESC'), s, s.view, (10, 10))
assert s.prompt is None and s.request is None, "Esc na pergunta = Não"
props.end()

# 6f. Fechamento e pé-direito (D-33 a D-38).
s = props.start(model.WallPlan([]), scene.name)
s.view = View2D((0, 0, 1000, 800))
s.view.fit(((-1, -1), (4, 3)), margin=0.1)
state.tool = 'DRAW'
at((0.0, 0.0), event('LEFTMOUSE'))
for target, text in (((1.0, 0.0), "3000"), ((3.0, 1.0), "2000"), ((2.0, 2.0), "3000"), ((0.0, 1.0), "2000")):
    s.cursor = target
    for char in text:
        op._handle(ctx, event('ONE', char=char), s, s.view, s.view.to_screen(target))
    op._handle(ctx, event('RET'), s, s.view, s.view.to_screen(target))
assert s.prompt == 'close' and len(s.drawing.nodes) == 4, (s.prompt, s.drawing.nodes)   # pelo teclado pergunta
op._handle(ctx, event('ESC'), s, s.view, (10, 10))                                       # "Não": mantém o trecho
assert s.prompt is None and len(s.drawing.nodes) == 5 and not s.drawing.closed
s.drawing.nodes.pop()
s.drawing.segments.pop()
s.prompt, s.pending_point = 'close', None
_box, yes, _no = ops_editor._prompt_rects(types.SimpleNamespace(width=1000, height=800))
op._handle(ctx, event('LEFTMOUSE'), s, s.view, (yes[0] + 5, yes[1] + 5))               # "Sim": fecha
chain = s.plan.chains[-1]
assert chain.closed and chain.segment_count() == 4 and chain.side == 'RIGHT'
props.end()
# ímã: 10 px gruda e pergunta; 20 px não
s = props.start(model.WallPlan([]), scene.name)
s.view = View2D((0, 0, 1000, 800))
s.view.fit(((-1, -1), (4, 3)), margin=0.1)
state.tool = 'DRAW'
for p in ((0.0, 0.0), (3.0, 0.0), (3.0, 2.0)):
    at(p, event('LEFTMOUSE'))
p0 = s.view.to_screen((0.0, 0.0))
assert ops_editor.close_snap(s, s.view, (p0[0] + 10, p0[1])) and not ops_editor.close_snap(s, s.view, (p0[0] + 20, p0[1]))
op._handle(ctx, event('LEFTMOUSE'), s, s.view, (p0[0] + 20, p0[1] + 1))
assert s.prompt is None and len(s.drawing.nodes) == 4                                   # longe: vértice normal
op._handle(ctx, event('LEFTMOUSE'), s, s.view, (p0[0] + 10, p0[1]))
assert s.prompt == 'close'
props.end()
# rede de segurança no OK e pé-direito do projeto
open_room = model.Chain([(0, 0), (3, 0), (3, 2), (0, 2), (0, 0.003)], [model.Segment(0.15, 2.5) for _ in range(4)])
report = apply.apply_plan(ctx, model.WallPlan([open_room]), project_height=2.7)
assert report['closed'] == 1 and len(walls()) == 4
reread = scene_io.read_plan(scene).chains[0]
assert reread.closed, "o OK fecha a sala com o fim no início"
assert all(close(hb_types.GeoNodeWall(w).get_input('Height'), 2.7) for w in walls()), "igualar ao projeto"
mureta = walls()[0]
mureta['btm_wall_type'] = 'MURETA'
hb_types.GeoNodeWall(mureta).set_input('Height', 1.1)
hb_types.GeoNodeWall(mureta).set_input('End Height', 1.1)
plan = scene_io.read_plan(scene)
assert apply.height_mismatches(plan, 2.8) and not any("1100" in t for t in apply.height_mismatches(plan, 2.8))
from caffmob_draw.walls2d import apply as _ap  # noqa: E402
changed = _ap.sync_project_height(ctx, 2.8)                                              # Configurações (D-38)
assert changed == 3, changed
assert close(hb_types.GeoNodeWall(mureta).get_input('Height'), 1.1)
assert all(close(hb_types.GeoNodeWall(w).get_input('Height'), 2.8) for w in walls() if w != mureta)
scene.home_builder.ceiling_height = 2.9                                                  # pelo callback do legado
assert all(close(hb_types.GeoNodeWall(w).get_input('End Height'), 2.9) for w in walls() if w != mureta)
for w in walls():
    ops_wall_extras.remove_wall(w)

# Seta do gizmo com porta (D-31): devolve 0 em vez de erro.
from caffmob_draw.inspection import gizmo as _gizmo  # noqa: E402
_gizmo._state['front'] = types.SimpleNamespace(hinged=True, get=lambda: 45.0)
assert _gizmo.BTM_GGT_front_open._arrow_get(None) == 0.0
_gizmo._state['front'] = None

# 6d. Porta de ambiente (D-20): as 6 combinações abrem para o lado do símbolo 2D e o arquivo é salvo fechado.
import math  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
from mathutils import Vector  # noqa: E402
from caffmob_draw.inspection import fronts  # noqa: E402
from caffmob_draw.inspection import room_door_math as rd  # noqa: E402


def room_door(name, inside, left, double, x):
    cage = hb_types.GeoNodeCage()
    cage.create(name)
    cage.obj['IS_ENTRY_DOOR_BP'] = True
    for key, value in (('Dim X', 0.9), ('Dim Y', 0.15), ('Dim Z', 2.1)):
        cage.set_input(key, value)
    swing = hb_types.GeoNodeDoorSwing()
    swing.create('Door Swing Annotation')
    swing.obj.parent = cage.obj
    for key, value in (('Dim X', 0.9), ('Dim Y', 0.15), ('Swing Inside', inside), ('Is Left', left),
                       ('Is Double', double)):
        swing.set_input(key, value)
    cage.obj.location = (x, 0.0, 0.0)
    cage.obj.rotation_euler.z = math.radians(30)
    return cage.obj


combos = [(True, True, False), (True, False, False), (False, True, False), (False, False, False),
          (True, False, True), (False, False, True)]
doors = [room_door(f"Porta{i}", *c, x=3.0 * i) for i, c in enumerate(combos)]
ctx.view_layer.update()
for door, (inside, left, double) in zip(doors, combos):
    front = fronts.front_for_object(door, scene)
    assert front is not None and front.get() == 0.0 and not front.can_sweep()
    assert fronts.fronts_of(door, scene), "a janela de propriedades acha a frente pela porta"
    front.commit(90.0)
    ctx.view_layer.update()
    pivots = [c for c in door.children if c.get('btm_room_door_pivot')]
    assert len(pivots) == (2 if double else 1)
    for spec, pivot in zip(rd.leaves(0.9, 0.15, 2.1, left, double, inside, 0.0381), sorted(
            pivots, key=lambda p: str(p['btm_room_door_pivot']))):
        leaf = pivot.children[0]
        tip = door.matrix_world @ Vector((*rd.open_tip(spec, 90.0), 0.0))
        nearest = min((leaf.matrix_world @ v.co - tip).length for v in leaf.data.vertices)
        assert nearest < 1e-4, (door.name, nearest)
    assert close(front.get(), 90.0)
path = os.path.join(tempfile.mkdtemp(), "portas.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
assert all(close(fronts.front_for_object(d, ctx.scene).get(), 90.0) for d in doors), "a tela continua aberta"
bpy.ops.wm.open_mainfile(filepath=path)
scene = bpy.context.scene
reopened = [fronts.front_for_object(scene.objects[f"Porta{i}"], scene) for i in range(len(combos))]
assert all(f.get() == 0.0 for f in reopened), [f.get() for f in reopened]

# 7. Registro limpo (duas vezes, sem resíduo).
addon.unregister()
addon.register()
addon.unregister()
assert not hasattr(bpy.types.Object, 'btm_geometry') and not hasattr(bpy.types.WindowManager, 'btm_wall_editor')
leftover = []                                    # D-32: nenhum operador do pacote sobra (pelo bl_idname)
for path in (ROOT / "caffmob_draw").rglob("*.py"):
    for idname in re.findall(r'bl_idname\s*=\s*["\']([a-z0-9_]+\.[a-z0-9_]+)["\']', path.read_text()):
        module, name = idname.split(".")
        try:
            getattr(getattr(bpy.ops, module), name).get_rna_type()
            leftover.append(idname)
        except (AttributeError, KeyError):
            pass
assert not leftover, (len(leftover), leftover[:10])
print("blender_002_smoke: OK")
