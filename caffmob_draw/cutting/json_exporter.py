"""JSON global v2 do projeto: peças, módulos e plano de corte (T026; RF-110, RF-111, RF-113, D-14).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/json-global-v2.md`.
Python puro (stdlib). Valores sempre em mm no arquivo; a versão 1.x é aceita na leitura e convertida (M-04).

Convenção de medidas: `NestingPart.height` é o comprimento (`length_mm`) e `NestingPart.width` a largura
(`width_mm`). Na chapa, `length_mm` é o eixo X do plano de corte e `width_mm` o eixo Y.
"""

import datetime
import json
import os
import tempfile

from .nesting import NestingPart

FORMAT = "caffmob_draw.project"
# Arquivos exportados antes da identidade CAFFMob Draw continuam válidos na leitura (BUG-20261006-QAVK).
ACCEPTED_FORMATS = (FORMAT, "blendertomob.project")
SCHEMA_VERSION = "2.1.0"     # 2.1: `machining` por peça (feature 003); leitores 2.0 continuam válidos
SUPPORTED_MAJOR = 2
ALGORITHM = "guillotine-shelf-nfd"

GRAIN_TO_JSON = {'NONE': "NONE", 'VERTICAL': "LENGTH", 'HORIZONTAL': "WIDTH"}
GRAIN_FROM_JSON = {v: k for k, v in GRAIN_TO_JSON.items()}
SOURCES = ("CUTPART", "SYNTHETIC", "FREE_GEOMETRY")
LIMIT_STATUSES = ("OK", "EXCEEDS_WIDTH", "EXCEEDS_LENGTH", "MACHINING_CLIPPED")


class GlobalJsonError(Exception):
    """Arquivo JSON global inválido; `errors` traz as mensagens com o caminho do campo."""

    def __init__(self, message, errors=()):
        super().__init__(message)
        self.errors = list(errors)


# ----------------------------------------------------------------------------------------------------------------
# Montagem
# ----------------------------------------------------------------------------------------------------------------

def _round(value, precision):
    return round(float(value or 0.0), precision)


def sheet_material_id(material, thickness):
    return f"SHEET:{material}:{_round(thickness, 2):g}"


def _generator(version=None, blender_version=None):
    if blender_version is None:
        try:
            import bpy
            blender_version = bpy.app.version_string
        except Exception:
            blender_version = ""
    return {"name": "CAFFMob Draw", "version": version or "", "blender_version": blender_version}


def _project_section(project, include_client):
    project = dict(project or {})
    company = project.get("company") or {}
    return {
        "name": str(project.get("name") or "Projeto"),
        "uid": str(project.get("uid") or ""),
        "rooms": [{"uid": str(r.get("uid", "")), "name": str(r.get("name", ""))} for r in project.get("rooms") or []],
        "client": (project.get("client") or None) if include_client else None,
        "company": {"name": str(company.get("name", "")), "author": str(company.get("author", "")),
                    **{k: v for k, v in company.items() if k not in ("name", "author")}},
    }


def _materials(parts, nesting_result):
    trims = {}
    for sheet in (nesting_result or {}).get("sheets", []):
        key = sheet_material_id(sheet.get("material", ""), sheet.get("thickness", 0.0))
        trims.setdefault(key, {
            "width_mm": sheet["height"], "length_mm": sheet["width"],
            "trim_mm": dict(sheet.get("refilos") or {}),
        })
    materials = {}
    for part in parts:
        mid = sheet_material_id(part.material, part.thickness)
        if mid not in materials:
            entry = {"id": mid, "name": part.material, "kind": "SHEET", "thickness_mm": _round(part.thickness, 2)}
            if mid in trims:
                entry["sheet"] = trims[mid]
            materials[mid] = entry
    return [materials[k] for k in sorted(materials)]


def _part_entry(part, precision):
    edge_precision = max(2, precision)
    return {
        "uid": part.uid,
        "module_uid": part.module_uid,
        "name": part.name,
        "component": part.component,
        "length_mm": _round(part.height, precision),
        "width_mm": _round(part.width, precision),
        "thickness_mm": _round(part.thickness, precision),
        "quantity": int(part.quantity),
        "material_id": sheet_material_id(part.material, part.thickness),
        "grain": GRAIN_TO_JSON.get(part.grain_direction, "NONE"),
        "finish_id": part.finish or "",
        "edges": [{"side": i + 1, "material_id": None, "thickness_mm": _round(t, edge_precision)}
                  for i, t in enumerate(part.edges)],
        "source": part.source,
        "limit_status": ("MACHINING_CLIPPED" if getattr(part, 'machining_clipped', False)
                         and part.limit_status == "OK" else part.limit_status),
        "drilling": [],
        "machining": [dict(entry) for entry in getattr(part, 'machining', [])],
    }


def _offcuts(sheet, precision):
    """Sobras retangulares: à direita de cada faixa e acima da última faixa."""
    offcuts = []
    trims = sheet.get("refilos") or {}
    left, bottom = trims.get("left", 0.0), trims.get("bottom", 0.0)
    usable_w, usable_h = sheet["usable_width"], sheet["usable_height"]
    top = 0.0
    for shelf in sheet.get("shelves", []):
        used_x = shelf["current_x"]
        if usable_w - used_x > 1.0:
            offcuts.append({"x_mm": _round(left + used_x, precision), "y_mm": _round(bottom + shelf["y"], precision),
                            "width_mm": _round(shelf["height"], precision),
                            "length_mm": _round(usable_w - used_x, precision)})
        top = max(top, shelf["y"] + shelf["height"])
    if usable_h - top > 1.0:
        offcuts.append({"x_mm": _round(left, precision), "y_mm": _round(bottom + top, precision),
                        "width_mm": _round(usable_h - top, precision), "length_mm": _round(usable_w, precision)})
    return offcuts


def _cut_plan(nesting_result, settings, precision, stale):
    settings = settings or {}
    sheets = []
    placed = 0
    for sheet in nesting_result.get("sheets", []):
        placements = []
        for shelf in sheet.get("shelves", []):
            for item in shelf.get("parts", []):
                placements.append({"part_uid": item.get("part_uid") or item.get("part_id") or item["id"],
                                   "x_mm": _round(item["x"], precision), "y_mm": _round(item["y"], precision),
                                   "rotated": bool(item.get("rotated", False))})
        placed += len(placements)
        sheets.append({
            "id": int(sheet["id"]),
            "material_id": sheet_material_id(sheet.get("material", ""), sheet.get("thickness", 0.0)),
            "finish_id": sheet.get("finish", ""),
            "thickness_mm": _round(sheet.get("thickness", 0.0), precision),
            "width_mm": _round(sheet["height"], precision),
            "length_mm": _round(sheet["width"], precision),
            "usable": {"width_mm": _round(sheet["usable_height"], precision),
                       "length_mm": _round(sheet["usable_width"], precision)},
            "utilization_pct": sheet.get("utilization_percentage", 0.0),
            "placements": placements,
            "offcuts": _offcuts(sheet, precision),
        })
    stats = nesting_result.get("stats", {})
    return {
        "algorithm": ALGORITHM,
        "kerf_mm": float(settings.get("kerf_mm", 4.0)),
        "allow_rotation": bool(settings.get("allow_rotation", True)),
        "respect_grain": bool(settings.get("respect_grain", True)),
        "stale": bool(stale),
        "sheets": sheets,
        "unplaced": sorted({u.get("uid") or u["id"] for u in nesting_result.get("unplaced", [])}),
        "stats": {"sheets": len(sheets), "parts_placed": placed,
                  "utilization_pct": stats.get("utilization_percentage", 0.0),
                  "waste_m2": stats.get("waste_area_m2", 0.0)},
    }


def _warnings(parts, nesting_result):
    warnings = []
    for part in sorted(parts, key=lambda p: p.uid):
        if part.limit_status != "OK":
            warnings.append({"code": part.limit_status, "part_uid": part.uid,
                             "message": f"{part.name}: maior que o limite de chapa do componente {part.component}."})
        if part.component == "UNCLASSIFIED":
            warnings.append({"code": "UNCLASSIFIED", "part_uid": part.uid,
                             "message": f"{part.name}: peça sem componente do padrão de dimensões."})
    for item in (nesting_result or {}).get("unplaced", []):
        warnings.append({"code": "UNPLACED", "part_uid": item.get("uid") or item["id"],
                         "message": f"{item.get('name', '')}: {item.get('reason', 'não coube na chapa')}."})
    return warnings


def build_global_payload(project, standard, parts, modules=None, nesting_result=None, nesting_settings=None,
                         include_client=True, precision=1, stale=False, version=None, extra_warnings=()):
    """Monta o dicionário do JSON v2 (ordem estável: módulos e peças por `uid`)."""
    parts = sorted(parts, key=lambda p: p.uid)
    standard = dict(standard or {})
    payload = {
        "schema": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "generator": _generator(version),
        "exported_at": datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        "unit": "mm",
        "decimal_precision": int(precision),
        "project": _project_section(project, include_client),
        "standard": {"uid": str(standard.get("uid", "")), "name": str(standard.get("name", "")),
                     "version": int(standard.get("version") or 0), "market": str(standard.get("market", "BR"))},
        "materials": _materials(parts, nesting_result),
        "modules": sorted([dict(m) for m in modules or []], key=lambda m: str(m.get("uid", ""))),
        "parts": [_part_entry(p, precision) for p in parts],
        "warnings": list(extra_warnings) + _warnings(parts, nesting_result),
    }
    if nesting_result is not None:
        payload["cut_plan"] = _cut_plan(nesting_result, nesting_settings, precision, stale)
    return payload


# ----------------------------------------------------------------------------------------------------------------
# Validação
# ----------------------------------------------------------------------------------------------------------------

def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _major(version):
    try:
        return int(str(version).split('.')[0])
    except ValueError:
        return None


def validate_global_json(payload):
    """Lista de erros (vazia = válido). Cada mensagem começa pelo caminho do campo (`parts[3].thickness_mm`)."""
    errors = []

    def need(obj, path, key, kind, check=None):
        if not isinstance(obj, dict) or key not in obj:
            errors.append(f"{path}{key}: campo obrigatório ausente")
            return None
        value = obj[key]
        ok = _is_number(value) if kind == 'number' else isinstance(value, kind)
        if not ok:
            errors.append(f"{path}{key}: tipo inválido")
            return None
        if check is not None and not check(value):
            errors.append(f"{path}{key}: valor inválido ({value!r})")
        return value

    if not isinstance(payload, dict):
        return ["$: o documento deve ser um objeto JSON"]
    if payload.get("schema") not in ACCEPTED_FORMATS:
        errors.append(f"schema: esperado {FORMAT!r}")
    version = need(payload, "", "schema_version", str)
    if version is not None:
        major = _major(version)
        if major is None or major > SUPPORTED_MAJOR:
            errors.append(f"schema_version: versão {version} não suportada (máximo {SUPPORTED_MAJOR}.x)")
    need(payload, "", "generator", dict)
    need(payload, "", "exported_at", str)
    need(payload, "", "unit", str, lambda u: u == "mm")
    need(payload, "", "decimal_precision", int)
    project = need(payload, "", "project", dict)
    if project is not None:
        need(project, "project.", "name", str)
        need(project, "project.", "rooms", list)
    need(payload, "", "standard", dict)
    need(payload, "", "warnings", list)

    material_ids = set()
    for i, material in enumerate(need(payload, "", "materials", list) or []):
        mid = need(material, f"materials[{i}].", "id", str)
        need(material, f"materials[{i}].", "kind", str, lambda k: k in ("SHEET", "EDGE"))
        if mid is not None:
            material_ids.add(mid)

    for i, module in enumerate(need(payload, "", "modules", list) or []):
        need(module, f"modules[{i}].", "uid", str)
        need(module, f"modules[{i}].", "name", str)

    part_uids = set()
    for i, part in enumerate(need(payload, "", "parts", list) or []):
        p = f"parts[{i}]."
        uid = need(part, p, "uid", str)
        if uid is not None:
            if uid in part_uids:
                errors.append(f"{p}uid: duplicado ({uid})")
            part_uids.add(uid)
        need(part, p, "name", str)
        need(part, p, "component", str)
        for key in ("length_mm", "width_mm", "thickness_mm"):
            need(part, p, key, 'number', lambda v: v > 0)
        need(part, p, "quantity", int, lambda v: v >= 1)
        need(part, p, "material_id", str, lambda v: v in material_ids)
        need(part, p, "grain", str, lambda v: v in GRAIN_FROM_JSON)
        need(part, p, "finish_id", str)
        edges = need(part, p, "edges", list, lambda v: len(v) == 4)
        for j, edge in enumerate(edges or []):
            need(edge, f"{p}edges[{j}].", "side", int, lambda v: 1 <= v <= 4)
            need(edge, f"{p}edges[{j}].", "thickness_mm", 'number', lambda v: v >= 0)
        need(part, p, "source", str, lambda v: v in SOURCES)
        need(part, p, "limit_status", str, lambda v: v in LIMIT_STATUSES)
        if "machining" in part:          # 2.1 (feature 003); ausente em 2.0 = lista vazia
            for j, cut in enumerate(need(part, p, "machining", list) or []):
                m = f"{p}machining[{j}]."
                need(cut, m, "kind", str, lambda v: v in ("POCKET", "THROUGH_CUT"))
                for key in ("x_mm", "y_mm", "end_x_mm", "end_y_mm", "depth_mm"):
                    need(cut, m, key, 'number', lambda v: v >= 0)

    plan = payload.get("cut_plan")
    if plan is not None:
        if not isinstance(plan, dict):
            errors.append("cut_plan: tipo inválido")
        else:
            for i, sheet in enumerate(need(plan, "cut_plan.", "sheets", list) or []):
                s = f"cut_plan.sheets[{i}]."
                need(sheet, s, "material_id", str, lambda v: v in material_ids)
                for key in ("width_mm", "length_mm"):
                    need(sheet, s, key, 'number', lambda v: v > 0)
                for j, placement in enumerate(need(sheet, s, "placements", list) or []):
                    need(placement, f"{s}placements[{j}].", "part_uid", str, lambda v: v in part_uids)
    return errors


# ----------------------------------------------------------------------------------------------------------------
# Arquivo
# ----------------------------------------------------------------------------------------------------------------

def write_global_json(path, payload):
    """Escrita atômica, UTF-8 sem BOM. Levanta GlobalJsonError se o conteúdo não passar na validação."""
    errors = validate_global_json(payload)
    if errors:
        raise GlobalJsonError("JSON global inválido.", errors)
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path


def read_global_json(path):
    """Lê um JSON global (v2, ou v1 convertido). Levanta GlobalJsonError com os erros de validação."""
    try:
        with open(str(path), encoding='utf-8-sig') as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise GlobalJsonError(f"JSON inválido (linha {exc.lineno}, coluna {exc.colno}).") from None
    except OSError as exc:
        raise GlobalJsonError(f"Não foi possível ler o arquivo: {exc}") from None
    if isinstance(payload, dict) and _major(payload.get("schema_version", "")) == 1:
        payload = convert_v1(payload)
    errors = validate_global_json(payload)
    if errors:
        raise GlobalJsonError("O arquivo não é um JSON global válido do CAFFMob Draw.", errors)
    return payload


def payload_to_parts(payload):
    """Reconstrói os `NestingPart` a partir de um payload v2 válido."""
    materials = {m["id"]: m for m in payload.get("materials", [])}
    modules = {m["uid"]: m for m in payload.get("modules", [])}
    parts = []
    for entry in payload.get("parts", []):
        material = materials.get(entry["material_id"], {})
        module = modules.get(entry.get("module_uid") or "", {})
        parts.append(NestingPart(
            id=entry["uid"], uid=entry["uid"], name=entry["name"],
            width=entry["width_mm"], height=entry["length_mm"], thickness=entry["thickness_mm"],
            quantity=entry["quantity"], material=material.get("name", entry["material_id"]),
            grain_direction=GRAIN_FROM_JSON.get(entry["grain"], 'NONE'),
            module_ref=module.get("name", ""), module_uid=entry.get("module_uid"),
            component=entry["component"], edges=[e.get("thickness_mm", 0.0) for e in entry["edges"]],
            finish=entry.get("finish_id", ""), source=entry.get("source", "SYNTHETIC"),
            limit_status=entry.get("limit_status", "OK"),
        ))
    return parts


def convert_v1(document):
    """Converte o JSON v1 (`parts_catalog`) em v2. O plano de corte v1 não é convertido: gere-o de novo."""
    parts = []
    for entry in document.get("parts_catalog", []):
        edges = entry.get("edges") or {}
        parts.append(NestingPart(
            id=entry["id"], name=entry.get("name", entry["id"]), width=entry["width"], height=entry["height"],
            quantity=entry.get("quantity", 1), thickness=entry.get("thickness", 15.0),
            material=entry.get("material", "MDF"), grain_direction=entry.get("grain_direction", 'NONE'),
            module_ref=entry.get("module_ref", ""),
            edges=[edges.get("left", 0.0), edges.get("right", 0.0), edges.get("top", 0.0), edges.get("bottom", 0.0)],
            source="SYNTHETIC"))
    project = document.get("project") or {}
    warnings = []
    if document.get("sheets"):
        warnings.append({"code": "V1_CUT_PLAN_DROPPED", "part_uid": None,
                         "message": "Plano de corte do arquivo v1 não convertido: gere o plano novamente."})
    return build_global_payload(
        project={"name": project.get("name", "Projeto"), "uid": "", "rooms": []},
        standard={"uid": "", "name": "", "version": 0, "market": "BR"},
        parts=parts, extra_warnings=warnings)


def export_cut_plan_to_json(filepath, nesting_result, parts_list, project_name="Projeto Marcenaria", **kwargs):
    """Compatibilidade com o chamador antigo: grava agora o JSON v2."""
    payload = build_global_payload(project={"name": project_name}, standard=kwargs.pop("standard", None),
                                   parts=parts_list, nesting_result=nesting_result, **kwargs)
    write_global_json(filepath, payload)
    return filepath
