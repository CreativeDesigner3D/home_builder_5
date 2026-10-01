"""Adaptadores de peças da cena (T024; D-08, D-10).

- `CUTPART`: lê os `GeoNodeCutpart` visíveis dos módulos frameless e closets (Length, Width, Thickness, material de
  `Top Surface`, fitas por `Edge *`) via `compat`.
- `SYNTHETIC`: módulos `btm_*` sem peças reais; as peças são deduzidas das medidas do módulo (comportamento antigo).

Cada módulo raiz recebe um `btm_uid` persistente; a peça recebe `uid = <btm_uid>/<componente>/<índice>`, com o índice
contado por componente na ordem dos nomes, para continuar estável entre recálculos (RN-18).
"""

import uuid
from dataclasses import dataclass, field

from .. import compat
from . import part_roles

FRAMELESS_TAG = 'IS_FRAMELESS_CABINET_CAGE'
CLOSET_TAG = 'IS_CLOSET_STARTER_CAGE'
UID_PROP = 'btm_uid'
LINE_PROP = 'btm_line'
CUTPART_GROUP = 'GeoNodeCutpart'


@dataclass
class PartRecord:
    """Peça lida da cena, antes de aplicar o padrão de dimensões (medidas em mm)."""
    uid: str
    module_uid: str
    module_name: str
    line: str
    name: str
    component: str
    length: float
    width: float
    thickness: float
    finish: str = ""
    edges_present: list = field(default_factory=lambda: [False, False, False, False])
    edge_thickness: list = None     # espessuras explícitas (só no adaptador sintético)
    grain: str = 'NONE'
    source: str = "CUTPART"
    quantity: int = 1
    material: str = ""


@dataclass
class ModuleRecord:
    uid: str
    name: str
    line: str
    library: str
    type: str
    obj: object = None


# ----------------------------------------------------------------------------------------------------------------
# Módulos
# ----------------------------------------------------------------------------------------------------------------

def ensure_module_uid(obj):
    uid = obj.get(UID_PROP)
    if not uid:
        uid = uuid.uuid4().hex[:12]
        obj[UID_PROP] = uid
    return str(uid)


def _is_btm_module(obj):
    plane = getattr(obj, 'btm_plane', None)
    return plane is not None and getattr(plane, 'object_kind', '') == 'MODULE'


def iter_modules(scene):
    """Módulos do projeto: gabinetes frameless, starters do closets e módulos `btm_*`."""
    modules = []
    for obj in scene.objects:
        if obj.get(FRAMELESS_TAG):
            library, line, kind = "FRAMELESS", obj.get(LINE_PROP) or "COZ", obj.get('CABINET_TYPE', '')
        elif obj.get(CLOSET_TAG):
            starter = getattr(obj, 'hb_closet_starter', None)
            library, line = "CLOSETS", obj.get(LINE_PROP) or "DOR"
            kind = starter.closet_type if starter is not None else ''
        elif obj.type == 'MESH' and _is_btm_module(obj):
            library, line, kind = "BTM", obj.get(LINE_PROP) or "COZ", "MODULE"
        else:
            continue
        modules.append(ModuleRecord(ensure_module_uid(obj), obj.name, str(line), library, str(kind), obj))
    modules.sort(key=lambda m: m.uid)
    return modules


# ----------------------------------------------------------------------------------------------------------------
# Adaptador CUTPART
# ----------------------------------------------------------------------------------------------------------------

def _cutpart_modifier(obj):
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and mod.node_group.name.split('.')[0] == CUTPART_GROUP:
            return mod
    return None


def _visible(obj):
    try:
        return not obj.hide_viewport and not obj.hide_get()
    except RuntimeError:
        return not obj.hide_viewport


def _material_name(value):
    return value.name if value is not None and hasattr(value, 'name') else ""


def cutpart_records(module):
    """Peças reais (GeoNodeCutpart visíveis) de um módulo frameless/closets."""
    found = []
    for obj in module.obj.children_recursive:
        if obj.type != 'MESH' or not _visible(obj):
            continue
        mod = _cutpart_modifier(obj)
        if mod is None:
            continue
        component = part_roles.classify(obj.name, obj.get('hb_part_role'), module.type)
        if component is part_roles.SKIP:
            continue
        length = abs(float(compat.try_get_gn_input(mod, 'Length', 0.0) or 0.0)) * 1000.0
        width = abs(float(compat.try_get_gn_input(mod, 'Width', 0.0) or 0.0)) * 1000.0
        thickness = abs(float(compat.try_get_gn_input(mod, 'Thickness', 0.0) or 0.0)) * 1000.0
        if length <= 0.0 or width <= 0.0:
            continue
        edges = [False] * 4
        for input_name, side in part_roles.EDGE_INPUTS:
            edges[side - 1] = compat.try_get_gn_input(mod, input_name, None) is not None
        finish = _material_name(compat.try_get_gn_input(mod, 'Top Surface', None))
        found.append((component, obj.name, PartRecord(
            uid="", module_uid=module.uid, module_name=module.name, line=module.line,
            name=part_roles.base_name(obj.name), component=component,
            length=length, width=width, thickness=thickness, finish=finish, edges_present=edges)))
    return _assign_uids(module, found)


def _assign_uids(module, found):
    found.sort(key=lambda item: (item[0], item[1]))
    counters = {}
    records = []
    for component, _name, record in found:
        index = counters.get(component, 0)
        counters[component] = index + 1
        record.uid = f"{module.uid}/{component}/{index}"
        records.append(record)
    return records


# ----------------------------------------------------------------------------------------------------------------
# Adaptador sintético (módulos btm_* sem peças reais)
# ----------------------------------------------------------------------------------------------------------------

def synthetic_records(module, thickness_for):
    """Peças deduzidas das medidas do módulo. `thickness_for(componente)` dá a espessura em mm."""
    obj = module.obj
    cab = getattr(obj, 'btm_cabinet', None)
    if cab is not None and cab.width > 0:
        width, height, depth = cab.width * 1000.0, cab.height * 1000.0, cab.depth * 1000.0
        door_swing = cab.door_swing
        carcass = cab.thickness * 1000.0 if cab.thickness > 0 else thickness_for("LAT")
    else:
        dims = obj.dimensions
        width, height, depth = dims.x * 1000.0, dims.z * 1000.0, dims.y * 1000.0
        door_swing = 'LEFT'
        carcass = thickness_for("LAT")
    inner = max(50.0, width - 2.0 * carcass)
    back = thickness_for("FUN_INF")
    spec = [
        ("LAT", "Lateral esquerda", height, depth, carcass, [True, False, False, False]),
        ("LAT", "Lateral direita", height, depth, carcass, [True, False, False, False]),
        ("BAS", "Base inferior", inner, depth, carcass, [True, False, False, False]),
        ("BAS", "Base superior", inner, depth, carcass, [True, False, False, False]),
        ("FUN_INF", "Fundo", max(50.0, height - 2.0 * carcass + 16.0), max(50.0, inner + 16.0), back,
         [False, False, False, False]),
        ("PRAT", "Prateleira", max(50.0, inner - 2.0), max(50.0, depth - 20.0), thickness_for("PRAT"),
         [True, False, False, False]),
    ]
    door = thickness_for("POR")
    if door_swing == 'DOUBLE':
        for side in ("esquerda", "direita"):
            spec.append(("POR", f"Porta {side}", max(50.0, height - 4.0), max(50.0, width / 2.0 - 3.0), door,
                         [True, True, True, True]))
    elif door_swing != 'NONE':
        spec.append(("POR", "Porta", max(50.0, height - 4.0), max(50.0, width - 4.0), door, [True, True, True, True]))
    found = []
    for i, (component, name, length, part_width, thickness, edges) in enumerate(spec):
        found.append((component, f"{i:02d}", PartRecord(
            uid="", module_uid=module.uid, module_name=module.name, line=module.line, name=name,
            component=component, length=length, width=part_width, thickness=thickness,
            edges_present=edges, source="SYNTHETIC")))
    return _assign_uids(module, found)


def module_has_cutparts(module):
    return any(_cutpart_modifier(o) is not None for o in module.obj.children_recursive if o.type == 'MESH')
