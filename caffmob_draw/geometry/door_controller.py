import bpy  # type: ignore
from .mesh_gen import generate_door_mesh


def delete_object(obj):
    """Remove um objeto e sua malha da cena de forma limpa."""
    if not obj:
        return
    # Desvincula de todas as coleções
    for col in obj.users_collection:
        col.objects.unlink(obj)
    # Remove dados associados
    if obj.type == 'MESH':
        bpy.data.meshes.remove(obj.data, do_unlink=True)
    elif obj.type == 'EMPTY':
        bpy.data.objects.remove(obj, do_unlink=True)


def get_child_by_name(parent, suffix):
    """Encontra um objeto filho que termina com o sufixo fornecido."""
    for child in parent.children:
        if child.name.endswith(suffix):
            return child
    return None


def setup_limit_constraint(empty_obj):
    """Configura restrição Limit Location para limitar o movimento do Empty no eixo Y local de 0.0 a 0.2m."""
    # Remove restrições antigas se existirem
    for con in empty_obj.constraints:
        if con.type == 'LIMIT_LOCATION':
            empty_obj.constraints.remove(con)

    con = empty_obj.constraints.new(type='LIMIT_LOCATION')
    con.use_min_x = True
    con.min_x = 0.0
    con.use_max_x = True
    con.max_x = 0.0

    con.use_min_y = True
    con.min_y = 0.0
    con.use_max_y = True
    con.max_y = 0.2

    con.use_min_z = True
    con.min_z = 0.0
    con.use_max_z = True
    con.max_z = 0.0

    con.owner_space = 'LOCAL'


def add_rotation_driver(door_obj, controller_obj, axis, factor):
    """Adiciona um Driver de rotação na folha da porta controlado pelo eixo Y local do Empty."""
    # Remove driver de rotação anterior se houver
    door_obj.driver_remove("rotation_euler", axis)

    driver_target = door_obj.driver_add("rotation_euler", axis)
    driver = driver_target.driver
    driver.type = 'SCRIPTED'

    var = driver.variables.new()
    var.name = "y"
    var.type = 'TRANSFORMS'

    target = var.targets[0]
    target.id = controller_obj
    target.data_path = 'location.y'
    target.transform_type = 'LOC_Y'
    target.transform_space = 'LOCAL_SPACE'

    # y vai de 0.0 a 0.2. Queremos que a rotação vá de 0 a factor * (pi / 2)
    # Relação: rotação = y * (factor * 1.570796 / 0.2) = y * factor * 7.85398
    driver.expression = f"y * ({factor} * 7.85398)"


def add_ui_sync_driver(cabinet_obj, controller_obj):
    """Adiciona driver na propriedade cabinet_obj.btm_cabinet.door_open baseada no movimento do Empty."""
    cabinet_obj.driver_remove("btm_cabinet.door_open")

    driver_target = cabinet_obj.driver_add("btm_cabinet.door_open")
    driver = driver_target.driver
    driver.type = 'SCRIPTED'

    var = driver.variables.new()
    var.name = "y"
    var.type = 'TRANSFORMS'

    target = var.targets[0]
    target.id = controller_obj
    target.data_path = 'location.y'
    target.transform_type = 'LOC_Y'
    target.transform_space = 'LOCAL_SPACE'

    # 0.2m no Empty = 1.0 (100% aberto) no slider
    driver.expression = "y / 0.2"


def update_door_geometry_and_controller(cabinet_obj):
    """Cria/atualiza as portas e o Empty controlador conforme as propriedades do armário."""
    cabinet = cabinet_obj.btm_cabinet
    swing = cabinet.door_swing

    # Nomes dos filhos esperados
    door_l_suffix = "_Door_L"
    door_r_suffix = "_Door_R"
    door_flip_suffix = "_Door_Flip"
    controller_suffix = "_Controller"

    # Se 'NONE', exclui filhos geométricos de portas e controladores
    if swing == 'NONE':
        delete_object(get_child_by_name(cabinet_obj, door_l_suffix))
        delete_object(get_child_by_name(cabinet_obj, door_r_suffix))
        delete_object(get_child_by_name(cabinet_obj, door_flip_suffix))
        delete_object(get_child_by_name(cabinet_obj, controller_suffix))
        # Limpa drivers da propriedade customizada
        cabinet_obj.driver_remove("btm_cabinet.door_open")
        return

    # Garante a existência do Empty controlador
    controller_obj = get_child_by_name(cabinet_obj, controller_suffix)
    if not controller_obj:
        controller_obj = bpy.data.objects.new(f"{cabinet_obj.name}{controller_suffix}", None)
        controller_obj.empty_display_size = 0.08
        controller_obj.empty_display_type = 'CUBE'
        cabinet_obj.users_collection[0].objects.link(controller_obj)
        controller_obj.parent = cabinet_obj

    setup_limit_constraint(controller_obj)

    # Reposiciona o Empty no local fechado (canto frontal direito/puxador padrão)
    # Y local do armário corre para trás (-Y), então a frente é em Y: 0.0
    # O Empty se move localmente no eixo Y dele próprio (que alinhamos com o Y global para frente).
    # Vamos posicionar o Empty na extremidade direita do armário para portas comuns
    controller_obj.location.x = cabinet.width / 2.0 - 0.03
    # Fechado = Y local 0: a restrição limita o curso a 0–0,2 m e o driver das portas usa y·(π/2)/0,2 (T059).
    controller_obj.location.y = 0.0
    controller_obj.location.z = cabinet.height / 2.0

    # Determina espessura e folga
    t = cabinet.thickness
    margin = 0.002

    # Deleta portas antigas incompatíveis com o swing atual
    if swing != 'DOUBLE':
        delete_object(get_child_by_name(cabinet_obj, door_l_suffix))
        delete_object(get_child_by_name(cabinet_obj, door_r_suffix))
    if swing != 'LEFT':
        if swing != 'DOUBLE': # DOUBLE usa LEFT e RIGHT
            delete_object(get_child_by_name(cabinet_obj, door_l_suffix))
    if swing != 'RIGHT':
        if swing != 'DOUBLE':
            delete_object(get_child_by_name(cabinet_obj, door_r_suffix))
    if swing != 'FLIP':
        delete_object(get_child_by_name(cabinet_obj, door_flip_suffix))

    # --- GERAR PORTA ESQUERDA ---
    if swing in ('LEFT', 'DOUBLE'):
        door_obj = get_child_by_name(cabinet_obj, door_l_suffix)
        w_door = (cabinet.width / 2.0 - margin * 1.5) if swing == 'DOUBLE' else (cabinet.width - margin * 2.0)
        h_door = cabinet.height - margin * 2.0

        if not door_obj:
            mesh = bpy.data.meshes.new(f"{cabinet_obj.name}{door_l_suffix}_Mesh")
            door_obj = bpy.data.objects.new(f"{cabinet_obj.name}{door_l_suffix}", mesh)
            cabinet_obj.users_collection[0].objects.link(door_obj)
            door_obj.parent = cabinet_obj

        generate_door_mesh(door_obj, w_door, h_door, t)

        # Pivô no lado esquerdo da abertura
        door_obj.location.x = -cabinet.width / 2.0 + margin
        door_obj.location.y = t  # alinha na face frontal
        door_obj.location.z = margin
        door_obj.rotation_euler.zero()

        # Adiciona o driver de rotação no eixo Z (positivo para abrir para fora/esquerda)
        add_rotation_driver(door_obj, controller_obj, 2, 1.0)

    # --- GERAR PORTA DIREITA ---
    if swing in ('RIGHT', 'DOUBLE'):
        door_obj = get_child_by_name(cabinet_obj, door_r_suffix)
        w_door = (cabinet.width / 2.0 - margin * 1.5) if swing == 'DOUBLE' else (cabinet.width - margin * 2.0)
        h_door = cabinet.height - margin * 2.0

        if not door_obj:
            mesh = bpy.data.meshes.new(f"{cabinet_obj.name}{door_r_suffix}_Mesh")
            door_obj = bpy.data.objects.new(f"{cabinet_obj.name}{door_r_suffix}", mesh)
            cabinet_obj.users_collection[0].objects.link(door_obj)
            door_obj.parent = cabinet_obj

        # Para rotacionar do lado direito, geramos a folha com largura negativa
        generate_door_mesh(door_obj, -w_door, h_door, t)

        # Pivô no lado direito da abertura
        door_obj.location.x = cabinet.width / 2.0 - margin
        door_obj.location.y = t
        door_obj.location.z = margin
        door_obj.rotation_euler.zero()

        # Adiciona o driver de rotação no eixo Z (negativo para abrir para fora/direita)
        add_rotation_driver(door_obj, controller_obj, 2, -1.0)

    # --- GERAR PORTA BASCULANTE (FLIP UP) ---
    if swing == 'FLIP':
        door_obj = get_child_by_name(cabinet_obj, door_flip_suffix)
        w_door = cabinet.width - margin * 2.0
        h_door = cabinet.height - margin * 2.0

        if not door_obj:
            mesh = bpy.data.meshes.new(f"{cabinet_obj.name}{door_flip_suffix}_Mesh")
            door_obj = bpy.data.objects.new(f"{cabinet_obj.name}{door_flip_suffix}", mesh)
            cabinet_obj.users_collection[0].objects.link(door_obj)
            door_obj.parent = cabinet_obj

        # Basculante rotaciona no eixo X.
        # Geramos a malha de modo que a dobradiça fique no topo (Z=0 local e abre subindo)
        # É mais fácil gerar w_door por h_door e reposicionar
        generate_door_mesh(door_obj, w_door, -h_door, t)

        # Pivô na parte superior (topo)
        door_obj.location.x = -cabinet.width / 2.0 + margin
        door_obj.location.y = t
        door_obj.location.z = cabinet.height - margin
        door_obj.rotation_euler.zero()

        # Rotação em X (negativa abre para cima/fora)
        add_rotation_driver(door_obj, controller_obj, 0, -1.0)

    # Adiciona driver de sincronização de UI no cabinet_obj.btm_cabinet.door_open
    add_ui_sync_driver(cabinet_obj, controller_obj)

    # Atualiza a posição do controlador baseando-se no valor inicial da propriedade
    controller_obj.location.y = cabinet.door_open * 0.2


def update_door_rotation_from_property(cabinet_obj):
    """
    Atualiza a posição do controlador Empty quando o usuário altera a propriedade
    'door_open' pelo slider na UI. Isso evita recursão cíclica de drivers.
    """
    cabinet = cabinet_obj.btm_cabinet
    controller_obj = get_child_by_name(cabinet_obj, "_Controller")
    if controller_obj:
        # Move o Empty. Os drivers das portas lerão a nova posição e rotacionarão!
        controller_obj.location.y = cabinet.door_open * 0.2
        # Força atualização da Viewport
        cabinet_obj.update_tag()


# ---------------------------------------------------------------------------
# Puxadores e materiais das portas (feature 003, D-07, D-08)
# ---------------------------------------------------------------------------

DOOR_SUFFIXES = ("_Door_L", "_Door_R", "_Door_Flip")
PULL_SUFFIX = "_Puxador"
PULL_EDGE = 0.05     # distância do puxador às bordas (m)


def doors_of(cabinet_obj):
    return [c for c in cabinet_obj.children if c.type == 'MESH' and c.name.endswith(DOOR_SUFFIXES)]


def _door_extent(door_obj):
    xs = [v.co.x for v in door_obj.data.vertices] or [0.0]
    zs = [v.co.z for v in door_obj.data.vertices] or [0.0]
    return min(xs), max(xs), min(zs), max(zs)


def set_door_pull(cabinet_obj, door_obj, pull_source, position='DEFAULT', pull_length=0.1):
    """Puxador como filho da porta: `pull_source` (objeto de malha) ou None para retirar.

    A folha é gerada de X 0→±largura, Z 0→±altura e Y 0→espessura; o puxador vai na borda livre (oposta à
    dobradiça), com a barra na vertical (na horizontal no basculante) e o corpo para fora do módulo.
    """
    from mathutils import Matrix, Vector  # type: ignore
    existing = [c for c in door_obj.children if c.get('IS_CABINET_PULL')]
    if pull_source is None:
        for pull in existing:
            bpy.data.objects.remove(pull, do_unlink=True)
        return None
    pull = existing[0] if existing else None
    if pull is None:
        pull = bpy.data.objects.new(door_obj.name + PULL_SUFFIX, pull_source.data)
        door_obj.users_collection[0].objects.link(pull)
        pull.parent = door_obj
        pull['IS_CABINET_PULL'] = True
    pull.data = pull_source.data
    x0, x1, z0, z1 = _door_extent(door_obj)
    thickness = cabinet_obj.btm_cabinet.thickness
    flip = door_obj.name.endswith("_Door_Flip")
    # Lado de fora: oposto ao centro da caixa, no eixo Y da porta.
    outward = 1.0 if door_obj.location.y >= 0.0 else -1.0
    y = thickness if outward > 0 else 0.0
    half = pull_length / 2.0
    if flip:
        x = (x0 + x1) / 2.0
        z = z0 + PULL_EDGE if z0 < 0 else z1 - PULL_EDGE
        axis_x = Vector((1.0, 0.0, 0.0))
    else:
        free_x = x1 if abs(x1) >= abs(x0) else x0
        x = free_x - PULL_EDGE if free_x > 0 else free_x + PULL_EDGE
        height = z1 - z0
        z = {'TOP': z1 - PULL_EDGE - half, 'BOTTOM': z0 + PULL_EDGE + half}.get(position, z0 + height / 2.0)
        axis_x = Vector((0.0, 0.0, 1.0))
    axis_y = Vector((0.0, -outward, 0.0))
    axis_z = axis_x.cross(axis_y)
    rotation = Matrix((axis_x, axis_y, axis_z)).transposed()
    pull.matrix_basis = Matrix.Translation((x, y, z)) @ rotation.to_4x4()
    return pull


def set_door_material(door_obj, material):
    if material is None or door_obj.type != 'MESH':
        return
    if door_obj.data.materials:
        door_obj.data.materials[0] = material
    else:
        door_obj.data.materials.append(material)
