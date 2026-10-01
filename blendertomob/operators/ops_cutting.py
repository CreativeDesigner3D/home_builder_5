"""Operadores de produção: lista de peças, plano de corte, JSON global v2 e CSV (T035, T036; RF-110–RF-113a).

A lista de peças vem da extração real (`cutting.part_extractor`), com a definição ativa do Padrão de Dimensões.
O resultado do plano fica em cache na cena (`btm_nesting_json_cache`) e `btm_settings.cut_plan_stale` indica
que o projeto mudou depois do cálculo.
"""

import json

import bpy  # type: ignore
from bpy_extras.io_utils import ExportHelper, ImportHelper  # type: ignore

from ..cutting import csv_exporter, json_exporter
from ..cutting.nesting import optimize_nesting
from ..cutting.part_extractor import extract_production_parts, module_entries

CACHE_PROP = "btm_nesting_json_cache"
INCOMPATIBLE_PROP = "btm_cut_incompatible"


def nesting_settings(scene):
    """Parâmetros do otimizador (mm) a partir de `btm_settings.mdf_config`."""
    cfg = getattr(getattr(scene, 'btm_settings', None), 'mdf_config', None)
    if cfg is None:
        return {"sheet_width": 2750.0, "sheet_height": 1830.0, "refilo_top": 10.0, "refilo_bottom": 10.0,
                "refilo_left": 10.0, "refilo_right": 10.0, "kerf": 4.0, "allow_rotation": True,
                "respect_grain": True}
    return {
        "sheet_width": cfg.sheet_width * 1000.0, "sheet_height": cfg.sheet_height * 1000.0,
        "refilo_top": cfg.refilo_top * 1000.0, "refilo_bottom": cfg.refilo_bottom * 1000.0,
        "refilo_left": cfg.refilo_left * 1000.0, "refilo_right": cfg.refilo_right * 1000.0,
        "kerf": cfg.kerf * 1000.0, "allow_rotation": cfg.allow_rotation, "respect_grain": cfg.respect_grain,
    }


def project_info(scene):
    """Seção `project` do JSON v2 a partir de `Scene.hb_project` (cena principal)."""
    from .. import hb_project
    from ..standards import api
    main = api.main_scene(scene)
    props = getattr(main, 'hb_project', None)
    if props is None:
        return {"name": scene.name, "uid": "", "rooms": []}
    client = {
        "name": props.client_name, "phone": props.client_phone, "email": props.client_email,
        "address": ", ".join(v for v in (props.client_address, props.client_city, props.client_state,
                                         props.client_zip) if v),
    }
    return {
        "name": props.project_name or scene.name,
        "uid": props.project_number or "",
        "rooms": [{"uid": s.name, "name": s.name} for s in hb_project.get_room_scenes()],
        "client": client if props.client_name else None,
        "company": {"name": "", "author": props.designer_name, "phone": props.designer_phone,
                    "email": props.designer_email},
    }


def standard_info(scene):
    from ..standards import api
    definition = api.active_definition(scene)
    if definition is None:
        return {"uid": "", "name": "", "version": 0, "market": "BR"}
    return {"uid": definition.uid, "name": definition.name, "version": definition.version,
            "market": definition.market}


def calculate(context):
    """Extrai as peças, calcula o plano e grava o cache. Devolve (peças, incompatíveis, resultado)."""
    scene = context.scene
    parts, incompatible = extract_production_parts(context)
    # A extração grava `btm_uid` nos módulos novos; processa essa atualização agora para que o handler de
    # plano desatualizado (cutting/stale.py) não a confunda com uma mudança feita depois do cálculo.
    context.view_layer.update()
    settings = nesting_settings(scene)
    result = optimize_nesting(parts=parts, **settings)
    scene[CACHE_PROP] = json.dumps({"stats": result["stats"], "sheets": result["sheets"],
                                    "unplaced": result["unplaced"], "settings": settings})
    scene[INCOMPATIBLE_PROP] = json.dumps(
        [{"uid": p.uid, "name": p.name, "module": p.module_ref, "status": p.limit_status,
          "length": p.height, "width": p.width} for p in incompatible], ensure_ascii=False)
    stats = result["stats"]
    scene["btm_nesting_result"] = (
        f"{stats['sheets_count']} chapa(s), {stats['total_placed_parts']} peça(s) posicionada(s), "
        f"aproveitamento {stats['utilization_percentage']}%")
    scene["btm_nesting_parts_count"] = len(parts)
    scene["btm_nesting_sheets_count"] = stats["sheets_count"]
    scene["btm_nesting_utilization"] = stats["utilization_percentage"]
    settings_pg = getattr(scene, 'btm_settings', None)
    if settings_pg is not None:
        settings_pg.cut_plan_stale = False
    return parts, incompatible, result


def cached_result(scene):
    raw = scene.get(CACHE_PROP, "")
    return json.loads(raw) if raw else None


def incompatible_parts(scene):
    raw = scene.get(INCOMPATIBLE_PROP, "")
    return json.loads(raw) if raw else []


class BTM_OT_CalculateNesting(bpy.types.Operator):
    """Gera a lista de peças dos módulos do projeto e calcula o plano de corte por chapa e acabamento"""
    bl_idname = "btm.calculate_nesting"
    bl_label = "Calcular Plano de Corte"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        parts, incompatible, result = calculate(context)
        if not parts:
            self.report({'WARNING'}, "Nenhum módulo com peças de marcenaria encontrado no projeto.")
            return {'CANCELLED'}
        stats = result["stats"]
        message = (f"Plano de corte: {stats['sheets_count']} chapa(s), {stats['total_placed_parts']} peça(s), "
                   f"aproveitamento {stats['utilization_percentage']}%.")
        if incompatible:
            message += f" {len(incompatible)} peça(s) maior(es) que o limite de chapa do componente."
        if result["unplaced"]:
            message += f" {len(result['unplaced'])} peça(s) não couberam na chapa."
        self.report({'WARNING'} if incompatible or result["unplaced"] else {'INFO'}, message)
        return {'FINISHED'}


class BTM_OT_ExportCutPlanJSON(bpy.types.Operator, ExportHelper):
    """Exporta projeto, peças e plano de corte no JSON global v2 do BlenderToMob"""
    bl_idname = "btm.export_cut_plan_json"
    bl_label = "Exportar JSON Global"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'}, maxlen=255)  # type: ignore
    include_client: bpy.props.BoolProperty(
        name="Incluir dados do cliente", description="Grava nome e contato do cliente no arquivo (RN-21)",
        default=True)  # type: ignore
    include_plan: bpy.props.BoolProperty(name="Incluir plano de corte", default=True)  # type: ignore

    def invoke(self, context, event):
        settings = getattr(context.scene, 'btm_settings', None)
        if settings is not None:
            self.include_client = settings.cut_include_client
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        scene = context.scene
        settings = getattr(scene, 'btm_settings', None)
        stale = bool(settings.cut_plan_stale) if settings is not None else False
        parts, _incompatible = extract_production_parts(context)
        result = None
        if self.include_plan:
            result = cached_result(scene)
            if result is None or stale:
                _parts, _inc, result = calculate(context)
                stale = False
        payload = json_exporter.build_global_payload(
            project=project_info(scene), standard=standard_info(scene), parts=parts,
            modules=module_entries(scene), nesting_result=result,
            nesting_settings={"kerf_mm": (result or {}).get("settings", {}).get("kerf", 4.0),
                              "allow_rotation": (result or {}).get("settings", {}).get("allow_rotation", True),
                              "respect_grain": (result or {}).get("settings", {}).get("respect_grain", True)},
            include_client=self.include_client, stale=stale)
        try:
            json_exporter.write_global_json(self.filepath, payload)
        except json_exporter.GlobalJsonError as exc:
            self.report({'ERROR'}, f"{exc} {'; '.join(exc.errors[:3])}")
            return {'CANCELLED'}
        except OSError as exc:
            self.report({'ERROR'}, f"Não foi possível gravar: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"JSON global exportado: {len(payload['parts'])} peça(s) em {self.filepath}")
        return {'FINISHED'}


class BTM_OT_ImportCutPlanJSON(bpy.types.Operator, ImportHelper):
    """Lê um JSON global (v2 ou v1) e mostra o resumo das peças e do plano de corte"""
    bl_idname = "btm.import_cut_plan_json"
    bl_label = "Importar JSON Global"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'}, maxlen=255)  # type: ignore

    def execute(self, context):
        try:
            payload = json_exporter.read_global_json(self.filepath)
        except json_exporter.GlobalJsonError as exc:
            detail = "; ".join(exc.errors[:3])
            self.report({'ERROR'}, f"{exc} {detail}".strip())
            return {'CANCELLED'}
        parts = json_exporter.payload_to_parts(payload)
        plan = payload.get("cut_plan")
        scene = context.scene
        if plan is not None:
            scene["btm_imported_cut_plan"] = json.dumps(plan, ensure_ascii=False)
        sheets = len(plan["sheets"]) if plan else 0
        self.report({'INFO'}, f"\"{payload['project']['name']}\": {len(parts)} peça(s), {sheets} chapa(s) no plano.")
        return {'FINISHED'}


class BTM_OT_ExportPartsCSV(bpy.types.Operator, ExportHelper):
    """Exporta a lista de peças em CSV (separador ;, vírgula decimal) para planilhas e otimizadores"""
    bl_idname = "btm.export_parts_csv"
    bl_label = "Exportar Peças (CSV)"
    bl_options = {'REGISTER'}

    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={'HIDDEN'}, maxlen=255)  # type: ignore

    def execute(self, context):
        parts, _incompatible = extract_production_parts(context)
        if not parts:
            self.report({'WARNING'}, "Nenhuma peça para exportar.")
            return {'CANCELLED'}
        try:
            count = csv_exporter.write_parts_csv(self.filepath, parts)
        except OSError as exc:
            self.report({'ERROR'}, f"Não foi possível gravar: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"CSV exportado: {count} peça(s) em {self.filepath}")
        return {'FINISHED'}


classes = (
    BTM_OT_CalculateNesting,
    BTM_OT_ExportCutPlanJSON,
    BTM_OT_ImportCutPlanJSON,
    BTM_OT_ExportPartsCSV,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
