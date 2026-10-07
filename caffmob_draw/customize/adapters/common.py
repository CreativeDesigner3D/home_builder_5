"""Utilidades comuns aos adaptadores de personalização (feature 003, T019-T040)."""

import bpy  # type: ignore

from ... import compat
from ...cutting import part_roles
from .. import spec

NO_STYLE_REASON = "A biblioteca não tem estilos de porta"


def ordered(objs):
    """Ordem estável: da esquerda para a direita, de cima para baixo (posição no mundo)."""
    return sorted(objs, key=lambda o: (round(o.matrix_world.translation.x, 4), -round(o.matrix_world.translation.z, 4),
                                       o.name))


def material(name, warnings):
    """Material por nome (RN-06); ausente → aviso e None."""
    if not name:
        return None
    mat = bpy.data.materials.get(name)
    if mat is None:
        warnings.append(f"Material '{name}' não existe neste arquivo")
    return mat


def rotated(mat):
    """Variante com o veio girado (convenção do legado: '<nome> ROTATED'), ou o próprio material."""
    if mat is None:
        return None
    return bpy.data.materials.get(mat.name + " ROTATED") or mat


def gn_modifier(obj, base_name):
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and mod.node_group.name.split(".")[0] == base_name:
            return mod
    return None


def set_cutpart_material(obj, mat):
    """Material de uma peça `GeoNodeCutpart` (as duas faces e os materiais de porta 5 peças); outras malhas: slots."""
    if mat is None:
        return False
    mod = gn_modifier(obj, 'GeoNodeCutpart')
    if mod is None:
        if obj.type != 'MESH':
            return False
        if not obj.data.materials:
            obj.data.materials.append(mat)
        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = mat
        return True
    compat.try_set_gn_input(mod, 'Top Surface', mat)
    compat.try_set_gn_input(mod, 'Bottom Surface', mat)
    if not mod.show_viewport and obj.type == 'MESH' and obj.data.materials:
        # porta 5 peças do face frame: malha estática, com o modificador da peça desligado
        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = mat
    for other in obj.modifiers:
        if other.type != 'NODES' or other is mod or other.node_group is None:
            continue
        items = other.node_group.interface.items_tree
        for socket, value in (('Material', mat), ('Stile Material', mat), ('Panel Material', mat),
                              ('Rail Material', rotated(mat))):
            if socket in items:
                compat.try_set_gn_input(other, socket, value)
    return True


def part_group(obj, cabinet_type=None):
    """Grupo de material da peça pelo componente (`part_roles.classify`)."""
    if obj.get('IS_CABINET_FRONT') or obj.get('hb_part_role') in ('DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT'):
        return 'FRENTES'
    component = part_roles.classify(obj.name, obj.get('hb_part_role'), cabinet_type)
    return spec.group_of_component(component)


def is_cutpart(obj):
    return obj.type == 'MESH' and gn_modifier(obj, 'GeoNodeCutpart') is not None


def apply_group_materials(root, warnings, cabinet_type=None, parts=None):
    """Materiais por grupo (no `btm_custom` da raiz) e por peça (no `btm_custom` da peça; vence o grupo)."""
    custom = root.btm_custom
    groups = {item.group: item.material for item in custom.group_materials if item.material}
    for obj in (parts if parts is not None else [o for o in root.children_recursive if is_cutpart(o)]):
        name = obj.btm_custom.material or groups.get(part_group(obj, cabinet_type), "")
        if name:
            set_cutpart_material(obj, material(name, warnings))


def read_materials(root, target, parts):
    target.group_materials = {item.group: item.material for item in root.btm_custom.group_materials if item.material}
    target.part_materials = {obj.name: obj.btm_custom.material for obj in parts if obj.btm_custom.material}


def interior_of(opening):
    return spec.interior_from_json(opening.btm_custom.interior)


def unique(messages):
    """Mensagens sem repetição, na ordem em que apareceram."""
    return list(dict.fromkeys(messages))


def run_operator(context, op, obj, **kwargs):
    """Chama um operador da biblioteca com `obj` como objeto ativo; devolve o conjunto de retorno."""
    with context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        return op(**kwargs)
