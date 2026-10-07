"""Adaptador de personalização do módulo paramétrico CAFFMob (`btm`) (feature 003, T040; D-05, D-07 a D-09).

O módulo é uma malha única (`geometry/mesh_gen.py`) com portas filhas (`geometry/door_controller.py`). Um só vão:
o próprio módulo. Gavetas, divisórias e estilos de porta não existem nessa linha e aparecem com o motivo.
"""

from ...geometry import door_controller
from ...geometry.mesh_gen import MAT_BACK, MAT_CARCASS, MAT_SHELF
from .. import spec
from . import common, frameless

LIBRARY = 'BTM'
SWING_TO_FRONT = {'LEFT': 'DOOR_LEFT', 'RIGHT': 'DOOR_RIGHT', 'DOUBLE': 'DOUBLE_DOORS', 'FLIP': 'FLIP_UP',
                  'NONE': 'OPEN'}
FRONT_TO_SWING = {v: k for k, v in SWING_TO_FRONT.items()}
NO_STYLES = "O módulo paramétrico não tem estilos de porta"


def capabilities(root):
    return {'FRONTS': None, 'PULLS': None, 'MATERIALS': None, 'INTERIOR': None, 'STYLES': NO_STYLES}


def front_types(root):
    return list(FRONT_TO_SWING)


def openings(root):
    return [("module", root)]


def front_type(root):
    return SWING_TO_FRONT.get(root.btm_cabinet.door_swing, 'OPEN'), 0


def read(root):
    result = spec.Spec(library=LIBRARY)
    item = result.ensure_opening("module")
    item.front, item.drawer_count = front_type(root)
    custom = root.btm_custom
    item.pull_model, item.pull_position, item.front_material = (custom.pull_model, custom.pull_position,
                                                                custom.front_material)
    item.interior = common.interior_of(root) or spec.Interior(shelves=int(root.btm_cabinet.shelves))
    result.group_materials = {i.group: i.material for i in custom.group_materials if i.material}
    return result


def set_front(context, root, opening, front, drawer_count=1):
    if front not in FRONT_TO_SWING:
        return [f"O módulo paramétrico não tem a frente '{spec.FRONT_LABELS.get(front, front)}'"]
    root.btm_cabinet.door_swing = FRONT_TO_SWING[front]      # o update refaz malha, portas e reaplica
    return []


def set_interior(context, root, opening, interior):
    messages = spec.validate_interior(interior)
    if messages:
        return messages
    root.btm_custom.interior = spec.interior_to_json(interior)
    root.btm_cabinet.shelves = int(interior.shelves)
    if interior.dividers or interior.drawers:
        messages.append("O módulo paramétrico só tem prateleiras; divisórias e gavetas internas foram ignoradas")
    if interior.heights:
        messages.append("O módulo paramétrico distribui as prateleiras por igual; as alturas foram ignoradas")
    return messages


def style_names():
    return []


def pull_items():
    return frameless.pull_items()       # mesmos arquivos de puxador da biblioteca frameless


def _carcass_materials(root, warnings):
    groups = {i.group: i.material for i in root.btm_custom.group_materials if i.material}
    if not groups:
        return
    carcass = common.material(groups.get('CAIXA'), warnings)
    slots = {MAT_CARCASS: carcass,
             MAT_SHELF: common.material(groups.get('INTERNO'), warnings) or carcass,
             MAT_BACK: common.material(groups.get('FUNDO'), warnings) or carcass}
    materials = root.data.materials
    while len(materials) < 3:
        materials.append(None)
    for index, mat in slots.items():
        if mat is not None:
            materials[index] = mat


def reapply(context, root):
    warnings = []
    custom = root.btm_custom
    _carcass_materials(root, warnings)
    groups = {i.group: i.material for i in custom.group_materials if i.material}
    front_mat = common.material(custom.front_material or groups.get('FRENTES', ""), warnings)
    pull_source = None
    if custom.pull_model and custom.pull_model != spec.NO_PULL:
        pull_source = frameless._pull_object(custom.pull_model, warnings)
    for door in door_controller.doors_of(root):
        if custom.pull_model == spec.NO_PULL or pull_source is not None:
            length = pull_source.dimensions.x if pull_source is not None else 0.1
            door_controller.set_door_pull(root, door, pull_source, custom.pull_position, length)
        door_controller.set_door_material(door, front_mat)
    return common.unique(warnings)
