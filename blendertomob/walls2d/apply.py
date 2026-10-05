"""Aplica o rascunho do Editor de Paredes às paredes do Home Builder 5 (T020; D-04, RN-12, RN-13, RN-16).

Para cada cadeia do modelo, na ordem dos trechos:
- trecho com origem: atualiza a parede existente; trecho novo: cria pelo mesmo caminho do construtor
  (`hb_types.GeoNodeWall.create`) com `Thickness`, `Height` e o tipo;
- a primeira parede fica solta na posição do primeiro nó; as seguintes são presas ao fim da anterior
  (`GeoNodeWall.connect_to_wall`, restrição `COPY_LOCATION`), como o construtor faz;
- comprimento, rotação, alturas e espessura vêm do modelo; tipo e orientação ficam em idprops.

Paredes que saíram do rascunho são removidas; os módulos e aberturas filhos delas ficam soltos na mesma posição (a
remoção junto com os módulos é opção do diálogo "Remover Parede"). Depois, as esquadrias de todas as paredes são
recalculadas (`operators/walls.update_all_wall_miters`) e pisos/tetos existentes são refeitos com o contorno novo.
Os filhos das paredes mantêm a posição relativa ao início.
"""

import math

import bpy  # type: ignore

from .. import hb_types
from ..operators import ops_wall_extras


def items_that_do_not_fit(plan):
    """[(parede, item)] — itens presos a uma parede que passariam do novo comprimento (RF-10)."""
    found = []
    for chain in plan.chains:
        for i, seg in enumerate(chain.segments):
            if not seg.source:
                continue
            wall = bpy.data.objects.get(seg.source)
            if wall is None:
                continue
            new_length = chain.length(i)
            for child in wall.children:
                if child.get('obj_x') or child.get('IS_2D_ANNOTATION'):
                    continue
                width = 0.0
                if getattr(child, 'home_builder', None) is not None and child.home_builder.mod_name:
                    try:
                        width = hb_types.GeoNodeObject(child).get_input('Dim X')
                    except Exception:
                        width = 0.0
                if child.location.x + width > new_length + 1e-4:
                    found.append((wall.name, child.name))
    return found


def modules_of_removed(plan):
    """[(parede, módulo)] — módulos (e outros itens soltos) presos a trechos apagados no editor (D-21, RF-10).

    Portas, janelas e cotas não contam: elas sempre saem com a parede.
    """
    found = []
    for name in plan.removed_sources:
        wall = bpy.data.objects.get(name)
        if wall is not None:
            found.extend((name, c.name) for c in wall.children
                         if not any(c.get(tag) for tag in ops_wall_extras.KEEP_WITH_WALL))
    return found


def _clear_chain_constraints(obj):
    for con in list(obj.constraints):
        if con.type == 'COPY_LOCATION':
            obj.constraints.remove(con)


def _norm(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi


def _legacy_type(seg):
    obj = bpy.data.objects.get(seg.source) if seg.source else None
    return obj.get('WALL_TYPE') if obj is not None else None


def height_mismatches(plan, project_height):
    """Paredes do rascunho de altura cheia com pé-direito diferente do projeto (D-37): ["nome (altura)"]."""
    from . import heights
    found = []
    for chain in plan.chains:
        for i, seg in enumerate(chain.segments):
            wall = {'name': seg.source or f"nova {i + 1}", 'height': seg.height, 'end_height': seg.end_height,
                    'btm_wall_type': seg.wall_type, 'legacy_wall_type': _legacy_type(seg)}
            if heights.walls_to_equalize([wall], project_height):
                found.append(f"{wall['name']} ({seg.height * 1000:.0f} mm)")
    return found


def apply_plan(context, plan, remove_modules=False, project_height=None):
    """Grava o rascunho. Devolve um relatório com as paredes criadas, atualizadas e removidas.

    `remove_modules`: os módulos dos trechos apagados saem junto (D-21); por padrão ficam soltos no lugar. Os objetos
    da camada nova convertidos (`plan.converted_sources`) são removidos (D-22). `project_height`: quando dado, as
    paredes de altura cheia passam a esse pé-direito (D-37). Contornos abertos com o fim no início são fechados (D-35).
    """
    from ..operators import walls as walls_ops
    from . import heights
    report = {'created': [], 'updated': [], 'removed': [], 'closed': 0}
    used = set()
    for chain in plan.chains:
        # Rede de segurança: contorno aberto com o fim no início é fechado antes de aplicar (D-35).
        if chain.close_if_touching():
            if not any(sg.source for sg in chain.segments):
                chain.side = chain.outward_side()
            report['closed'] += 1
        if project_height is not None:                 # "Igualar ao pé-direito do projeto" (D-37)
            for seg in chain.segments:
                if heights.follows_project_height(seg.wall_type, _legacy_type(seg)):
                    seg.height = seg.end_height = project_height
        # O Home Builder 5 põe a espessura à esquerda do sentido; Direção direita = cadeia invertida (D-25).
        nodes, segments = chain.hb_order()
        draft = type(chain)(nodes, segments, chain.closed, 'LEFT')
        previous = None
        for i, seg in enumerate(segments):
            obj = bpy.data.objects.get(seg.source) if seg.source else None
            if obj is None:
                wall = hb_types.GeoNodeWall()
                wall.create("Wall")
                obj = wall.obj
                report['created'].append(obj.name)
            else:
                wall = hb_types.GeoNodeWall(obj)
                report['updated'].append(obj.name)
            old_rotation = obj.matrix_world.to_euler().z
            kept = [(c, c.matrix_world.copy()) for c in obj.children if not c.get('obj_x')]
            used.add(obj.name)
            _clear_chain_constraints(obj)
            if previous is None:
                start = draft.nodes[0]
                obj.location = (start[0], start[1], obj.location.z)
            else:
                wall.connect_to_wall(previous)
            obj.rotation_euler = (0.0, 0.0, draft.direction(i))
            if kept and abs(_norm(draft.direction(i) - old_rotation)) > math.pi / 2:
                # A parede mudou de sentido (Direção trocada): os filhos ficam onde estavam no mundo.
                context.view_layer.update()
                for child, matrix in kept:
                    child.matrix_world = matrix
            wall.set_input('Length', draft.length(i))
            wall.set_input('Thickness', seg.thickness)
            wall.set_input('Height', seg.height)
            wall.set_input('End Height', seg.end_height)
            obj['btm_wall_type'] = seg.wall_type
            seg.source = obj.name
            previous = wall
    for name in plan.removed_sources:
        obj = bpy.data.objects.get(name)
        if obj is not None and name not in used:
            ops_wall_extras.remove_wall(obj, remove_modules=remove_modules)
            report['removed'].append(name)
    plan.removed_sources = []
    for name in plan.converted_sources:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.meshes.remove(data)
            report['removed'].append(name)
    plan.converted_sources = []
    context.view_layer.update()
    walls_ops.update_all_wall_miters()
    report['floors'], report['ceilings'] = refresh_floors_and_ceilings(context)
    return report


def _swap_mesh(obj, built):
    """Troca a malha de `obj` pela de `built` (objeto temporário), mantendo o objeto, os materiais e modificadores."""
    old = obj.data
    for material in old.materials:
        built.data.materials.append(material)
    obj.data = built.data
    bpy.data.objects.remove(built, do_unlink=True)
    if old.users == 0:
        bpy.data.meshes.remove(old)


def refresh_floors_and_ceilings(context):
    """Refaz pisos e tetos existentes (`IS_FLOOR_BP`/`IS_CEILING_BP`) com o contorno atual das salas fechadas.

    O legado não liga piso/teto às paredes: eles são gerados a partir do contorno (`add_floor`/`add_ceiling`). Aqui
    usamos as mesmas funções e trocamos só a malha, na ordem dos nomes, uma sala fechada para cada piso/teto. Pisos e
    tetos sem sala fechada correspondente ficam como estão. Devolve (pisos refeitos, tetos refeitos).
    """
    from ..operators import walls as walls_ops
    loops = []
    for chain in walls_ops.find_wall_chains():
        points = walls_ops.get_room_boundary_points(chain)
        if len(points) >= 3 and walls_ops.is_closed_loop(points):
            loops.append((chain, points))
    floors = sorted((o for o in context.scene.objects if o.get('IS_FLOOR_BP') and o.type == 'MESH'),
                    key=lambda o: o.name)
    ceilings = sorted((o for o in context.scene.objects if o.get('IS_CEILING_BP') and o.type == 'MESH'),
                      key=lambda o: o.name)
    floor_op, ceiling_op = walls_ops.home_builder_walls_OT_add_floor, walls_ops.home_builder_walls_OT_add_ceiling
    for obj, (_chain, points) in zip(floors, loops):
        _swap_mesh(obj, floor_op.create_floor_mesh(None, obj.name + "_tmp", points))
    for obj, (chain, points) in zip(ceilings, loops):
        height = hb_types.GeoNodeWall(chain[0]).get_input('Height') or context.scene.home_builder.ceiling_height
        _swap_mesh(obj, ceiling_op.create_ceiling_mesh(None, obj.name + "_tmp", points, height))
    return min(len(floors), len(loops)), min(len(ceilings), len(loops))


def sync_project_height(context, height):
    """Configurações → paredes (D-38, RF-43): grava `Height` e `End Height` = `height` em toda parede de altura cheia
    do projeto (todas as cenas; fora Mureta, meia-parede e parede falsa), recalcula as esquadrias e refaz piso e teto
    da cena atual. Devolve quantas paredes mudaram."""
    from ..operators import walls as walls_ops
    from . import heights
    changed = 0
    for obj in bpy.data.objects:
        if not obj.get('IS_WALL_BP'):
            continue
        if not heights.follows_project_height(obj.get('btm_wall_type'), obj.get('WALL_TYPE')):
            continue
        wall = hb_types.GeoNodeWall(obj)
        if not wall.has_modifier():
            continue
        if (abs(wall.get_input('Height') - height) <= heights.TOLERANCE
                and abs(wall.get_input('End Height') - height) <= heights.TOLERANCE):
            continue
        wall.set_input('Height', height)
        wall.set_input('End Height', height)
        changed += 1
    if changed:
        context.view_layer.update()
        walls_ops.update_all_wall_miters()
        refresh_floors_and_ceilings(context)
    return changed
