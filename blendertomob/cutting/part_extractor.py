"""Extração da lista de peças de produção (T025; RN-16, RN-17, D-12).

Fluxo: adaptadores (`part_sources`) → classificação por componente → matéria-prima e espessura das fitas pelo
componente da definição de dimensões ativa → checagem do limite de chapa do componente → (peças, incompatíveis).
"""

from ..data import dimension_schema as schema
from . import part_sources
from .nesting import NestingPart

DEFAULT_MATERIAL = "MDF"


def _schema_values(market='BR'):
    return {key: param.default(market) for key, param in schema.PARAMS.items()}


def _value(values, key, default=0.0):
    value = values.get(key, default)
    return default if value is None else value


def limit_status(length, width, max_length, max_width):
    """Compara as medidas ordenadas: o lado maior com o maior limite e o menor com o menor. 0 = sem limite."""
    limits = [v for v in (float(max_length or 0.0), float(max_width or 0.0)) if v > 0.0]
    if not limits:
        return "OK"
    long_side, short_side = max(length, width), min(length, width)
    long_limit = max(limits)
    short_limit = min(limits) if len(limits) == 2 else long_limit
    if long_side > long_limit + 1e-6:
        return "EXCEEDS_LENGTH"
    if short_side > short_limit + 1e-6:
        return "EXCEEDS_WIDTH"
    return "OK"


def thickness_lookup(values, line):
    def thickness_for(component):
        return float(_value(values, schema.sheet_key(line, component, 'thickness'), 15.0))
    return thickness_for


def record_to_part(record, values):
    """Converte um `PartRecord` em `NestingPart` usando os valores (mm) da definição ativa."""
    component = record.component
    known = component in schema.COMPONENTS_BY_CODE and record.line in schema.LINE_CODES
    if known:
        material = str(_value(values, schema.sheet_key(record.line, component, 'material'), DEFAULT_MATERIAL))
        edges = []
        for side in range(1, 5):
            if record.edge_thickness is not None:
                edges.append(float(record.edge_thickness[side - 1]))
            elif record.edges_present[side - 1]:
                edges.append(float(_value(values, schema.sheet_key(record.line, component, f"edge_{side}"), 0.0)))
            else:
                edges.append(0.0)
        status = limit_status(
            record.length, record.width,
            _value(values, schema.sheet_key(record.line, component, 'max_length'), 0.0),
            _value(values, schema.sheet_key(record.line, component, 'max_width'), 0.0))
    else:
        material, edges, status = record.material or DEFAULT_MATERIAL, [0.0] * 4, "OK"
    return NestingPart(
        id=record.uid, uid=record.uid, name=record.name, width=record.width, height=record.length,
        thickness=record.thickness, quantity=record.quantity, material=material,
        grain_direction=record.grain, module_ref=record.module_name, module_uid=record.module_uid,
        component=component, edges=edges, finish=record.finish, source=record.source, limit_status=status)


def _active_values(scene):
    try:
        from ..standards import api
        definition = api.active_definition(scene)
        if definition is not None:
            return api.definition_values(definition)
    except Exception:
        pass
    return _schema_values('BR')


def extract_production_parts(context, scene=None):
    """Peças de produção da cena e a lista das incompatíveis com o limite de chapa (`limit_status` ≠ OK)."""
    scene = scene or context.scene
    values = _active_values(scene)
    parts = []
    for module in part_sources.iter_modules(scene):
        if module.library == "BTM":
            records = part_sources.synthetic_records(module, thickness_lookup(values, module.line))
        else:
            records = part_sources.cutpart_records(module)
        parts.extend(record_to_part(r, values) for r in records)
    parts.extend(record_to_part(r, values) for r in part_sources.geometry_records(scene))
    parts.sort(key=lambda p: (p.module_uid or "", p.uid))
    incompatible = [p for p in parts if p.limit_status != "OK"]
    return parts, incompatible


def module_entries(scene):
    """Módulos no formato `modules[]` do JSON v2."""
    entries = []
    for module in part_sources.iter_modules(scene):
        obj = module.obj
        dims = obj.dimensions
        entries.append({
            "uid": module.uid, "name": module.name, "room_uid": str(obj.get('btm_room_uid', '')),
            "line": module.line, "library": module.library, "type": module.type,
            "width_mm": round(dims.x * 1000.0, 1), "height_mm": round(dims.z * 1000.0, 1),
            "depth_mm": round(dims.y * 1000.0, 1),
            "location_mm": [round(v * 1000.0, 1) for v in obj.matrix_world.translation],
            "rotation_deg": [round(v * 57.29577951308232, 3) for v in obj.matrix_world.to_euler()],
            "finish": {},
        })
    return entries


def extract_parts_from_scene(context):
    """Compatibilidade: só a lista de peças."""
    return extract_production_parts(context)[0]

