"""Operadores do Padrão de Dimensões (T032–T034, T045; D-16, D-16a, RN-23, RF-057, RF-058).

- `btm.standards_configurator`: Configurador de Dimensões (rascunho → aplicar com confirmação de N módulos).
- `btm.standards_apply`: aplica o rascunho atual (uso em painéis e scripts).
- Gestão: definir ativa, duplicar, renomear, excluir (embutidas protegidas).
- Arquivos: exportar/importar `.btmdim.json` e `DIMENSIONEXPORT` do Promob.
- `btm.standards_report`: janela com o relatório da última aplicação/importação.
"""

import os

import bpy  # type: ignore
from bpy_extras.io_utils import ExportHelper, ImportHelper  # type: ignore

from ..data import dimension_schema as schema
from ..standards import api, io_json, io_promob, sync

# Relatório da última aplicação/importação (mostrado por btm.standards_report).
_LAST_REPORT = {'title': "", 'lines': []}
PENDING_ROWS = 8


def _set_report(title, lines):
    _LAST_REPORT['title'] = title
    _LAST_REPORT['lines'] = list(lines)


def _show_report(context):
    if bpy.app.background or context.window is None:
        return
    bpy.ops.btm.standards_report('INVOKE_DEFAULT')


def _apply_report_lines(report):
    lines = [f"Definição: {report.get('definition', '')}",
             f"Módulos atualizados: {report.get('modules_updated', 0)} "
             f"(cozinha {report.get('frameless', 0)}, dormitório {report.get('closets', 0)})"]
    changes = report.get('changes') or []
    if changes:
        lines.append(f"Parâmetros alterados: {len(changes)}")
        lines += [f"  {c['label']}: {c['old']} → {c['new']}" for c in changes[:20]]
        if len(changes) > 20:
            lines.append(f"  … e mais {len(changes) - 20}")
    skipped = report.get('skipped_manual') or []
    if skipped:
        lines.append(f"Medidas manuais preservadas: {len(skipped)}")
        lines += [f"  {module}: {name}" for module, name in skipped[:10]]
    without = report.get('without_target') or []
    if without:
        lines.append(f"Sem destino nas bibliotecas atuais (valem para a lista de peças): {len(without)}")
        lines += [f"  {schema.label(k)}" for k in without[:10]]
    return lines


def _sync_report_message(report):
    return (f"Padrão aplicado: {report.get('modules_updated', 0)} módulo(s) atualizado(s); "
            f"{len(report.get('skipped_manual') or [])} medida(s) manual(is) preservada(s).")


# ----------------------------------------------------------------------------------------------------------------
# Configurador
# ----------------------------------------------------------------------------------------------------------------

def draw_pending(layout, scene, draft):
    changes = api.pending_changes(scene, draft)
    box = layout.box()
    if not changes:
        box.label(text="Nenhuma alteração pendente.", icon='CHECKMARK')
        return changes
    box.label(text=f"Alterações pendentes: {len(changes)}", icon='MODIFIER')
    col = box.column(align=True)
    for change in changes[:PENDING_ROWS]:
        col.label(text=f"{change['label']}: {change['old']} → {change['new']}")
    if len(changes) > PENDING_ROWS:
        col.label(text=f"… e mais {len(changes) - PENDING_ROWS}")
    return changes


def draw_editor(layout, context, draft):
    """Painel direito do Configurador: imagem de referência, campo do valor, faixa e erro."""
    from ..standards import previews
    param = schema.get_param(draft.selected_key)
    col = layout.column()
    icon = previews.icon_id(param.image_key if param else 'max_measures')
    if icon:
        col.template_icon(icon_value=icon, scale=12.0)
    else:
        col.label(text="Imagem de referência indisponível.", icon='IMAGE_DATA')
    if param is None:
        col.label(text="Selecione um parâmetro na árvore.", icon='INFO')
        return
    title = schema.line_label(param.line) if param.line != 'GLOBAL' else "Medidas Máximas"
    if param.component:
        title += f" › {schema.COMPONENTS_BY_CODE[param.component].label_pt}"
    col.label(text=title)
    col.label(text=param.label_pt, icon='DRIVER_DISTANCE')
    if param.type == 'ENUM':
        col.prop(draft, "edit_enum", text="")
    else:
        col.prop(draft, "edit_text", text="")
        unit = api.user_unit(context.scene)
        low = api.format_param_value(param, param.min, unit) if param.min is not None else "—"
        high = api.format_param_value(param, param.max, unit) if param.max is not None else "—"
        col.label(text=f"Faixa: {low} a {high}", icon='INFO')
    if draft.error:
        row = col.row()
        row.alert = True
        row.label(text=draft.error, icon='ERROR')


class BTM_OT_StandardsConfigurator(bpy.types.Operator):
    """Abre o Configurador de Dimensões: padrão de medidas, chapas, fitas e limites de todas as linhas"""
    bl_idname = "btm.standards_configurator"
    bl_label = "Configurador de Dimensões"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        try:
            api.begin_draft(context.scene, context.window_manager)
        except api.StandardsError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        definition = api.active_definition(context.scene)
        confirm = "Fechar" if definition.builtin else "Aplicar"
        return context.window_manager.invoke_props_dialog(self, width=980, title="Configurador de Dimensões",
                                                          confirm_text=confirm)

    def draw(self, context):
        scene = context.scene
        draft = context.window_manager.btm_standards_draft
        definition = api.draft_definition(scene, draft)
        layout = self.layout
        row = layout.row()
        if definition is not None and definition.builtin:
            row.label(text=f"{definition.name} (somente leitura)", icon='LOCKED')
            row.operator("btm.standards_duplicate", text="Duplicar para editar", icon='DUPLICATE')
        else:
            row.prop(draft, "definition_name", text="Definição")
        split = layout.split(factor=0.55)
        left = split.column()
        left.prop(draft, "search", text="", icon='VIEWZOOM')
        left.template_list("BTM_UL_StandardsTree", "", draft, "tree", draft, "tree_index", rows=20, maxrows=20)
        right = split.column()
        draw_editor(right, context, draft)
        changes = draw_pending(layout, scene, draft)
        if changes and definition is not None and not definition.builtin:
            count = len(sync.affected_modules(scene))
            row = layout.row()
            row.label(text=f"Ao aplicar, {count} módulo(s) do projeto serão atualizados.", icon='MOD_BUILD')
            row.prop(draft, "include_manual")

    def execute(self, context):
        scene = context.scene
        draft = context.window_manager.btm_standards_draft
        definition = api.draft_definition(scene, draft)
        if definition is None:
            self.report({'ERROR'}, "A definição em edição não existe mais.")
            return {'CANCELLED'}
        if definition.builtin:
            return {'FINISHED'}
        try:
            report = api.apply_draft(scene, draft, include_manual=draft.include_manual)
        except api.StandardsError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        _set_report("Padrão de Dimensões aplicado", _apply_report_lines(report))
        self.report({'INFO'}, _sync_report_message(report))
        _show_report(context)
        return {'FINISHED'}


class BTM_OT_StandardsApply(bpy.types.Operator):
    """Aplica o rascunho do Configurador à definição e atualiza os módulos do projeto"""
    bl_idname = "btm.standards_apply"
    bl_label = "Aplicar Padrão de Dimensões"
    bl_options = {'REGISTER', 'UNDO'}

    include_manual: bpy.props.BoolProperty(
        name="Incluir medidas manuais",
        description="Também substitui medidas editadas à mão nos módulos (RN-23)",
        default=False)  # type: ignore

    def invoke(self, context, event):
        count = len(sync.affected_modules(context.scene))
        return context.window_manager.invoke_confirm(
            self, event, title="Aplicar Padrão de Dimensões",
            message=f"{count} módulo(s) serão atualizados.", confirm_text="Aplicar")

    def execute(self, context):
        draft = context.window_manager.btm_standards_draft
        try:
            report = api.apply_draft(context.scene, draft, include_manual=self.include_manual)
        except api.StandardsError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        _set_report("Padrão de Dimensões aplicado", _apply_report_lines(report))
        self.report({'INFO'}, _sync_report_message(report))
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------
# Gestão das definições
# ----------------------------------------------------------------------------------------------------------------

def _definition_items(self, context):
    data = api.standards(context.scene)
    items = []
    if data is not None:
        for index, definition in enumerate(data.definitions):
            icon = 'LOCKED' if definition.builtin else 'PRESET'
            items.append((definition.uid, definition.name, definition.source, icon, index))
    _definition_items.cache = items   # mantém as strings vivas (EnumProperty dinâmico)
    return items or [('NONE', "Nenhuma", "", 'NONE', 0)]


class BTM_OT_StandardsSetActive(bpy.types.Operator):
    """Define a definição ativa do projeto e atualiza os módulos existentes"""
    bl_idname = "btm.standards_set_active"
    bl_label = "Definir Definição Ativa"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "definition"

    definition: bpy.props.EnumProperty(name="Definição", items=_definition_items)  # type: ignore
    include_manual: bpy.props.BoolProperty(name="Incluir medidas manuais", default=False)  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Definir Definição Ativa",
                                                          confirm_text="Definir e aplicar")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "definition")
        layout.label(text=f"{len(sync.affected_modules(context.scene))} módulo(s) serão atualizados.",
                     icon='MOD_BUILD')
        layout.prop(self, "include_manual")

    def execute(self, context):
        scene = context.scene
        definition = api.find_definition(scene, uid=self.definition)
        if definition is None:
            self.report({'ERROR'}, "Definição não encontrada.")
            return {'CANCELLED'}
        api.set_active(scene, definition)
        report = sync.apply_definition(scene, definition, include_manual=self.include_manual)
        _set_report("Definição ativa alterada", _apply_report_lines(report))
        self.report({'INFO'}, _sync_report_message(report))
        return {'FINISHED'}


class BTM_OT_StandardsDuplicate(bpy.types.Operator):
    """Duplica a definição ativa como cópia editável (a cópia passa a ser a ativa)"""
    bl_idname = "btm.standards_duplicate"
    bl_label = "Duplicar Definição"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        try:
            api.ensure_ready(scene)
            new = api.duplicate_definition(scene, api.active_definition(scene))
        except api.StandardsError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        draft = context.window_manager.btm_standards_draft
        if draft.definition_uid:
            # Configurador aberto sobre a embutida: o rascunho passa a editar a cópia.
            draft.definition_uid = new.uid
            draft.definition_name = new.name
        self.report({'INFO'}, f"Definição \"{new.name}\" criada e ativa.")
        return {'FINISHED'}


class BTM_OT_StandardsRename(bpy.types.Operator):
    """Renomeia a definição ativa"""
    bl_idname = "btm.standards_rename"
    bl_label = "Renomear Definição"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Nome")  # type: ignore

    @classmethod
    def poll(cls, context):
        definition = api.active_definition(context.scene)
        return definition is not None and not definition.builtin

    def invoke(self, context, event):
        self.name = api.active_definition(context.scene).name
        return context.window_manager.invoke_props_dialog(self, title="Renomear Definição")

    def execute(self, context):
        name = self.name.strip()
        if not name:
            self.report({'ERROR'}, "Informe um nome.")
            return {'CANCELLED'}
        definition = api.active_definition(context.scene)
        if name != definition.name:
            definition.name = api.unique_name(context.scene, name)
        return {'FINISHED'}


class BTM_OT_StandardsDelete(bpy.types.Operator):
    """Exclui a definição ativa (as embutidas não podem ser excluídas)"""
    bl_idname = "btm.standards_delete"
    bl_label = "Excluir Definição"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        definition = api.active_definition(context.scene)
        return definition is not None and not definition.builtin

    def invoke(self, context, event):
        definition = api.active_definition(context.scene)
        return context.window_manager.invoke_confirm(
            self, event, title="Excluir Definição", message=f"Excluir \"{definition.name}\"?",
            confirm_text="Excluir", icon='WARNING')

    def execute(self, context):
        try:
            api.remove_definition(context.scene, api.active_definition(context.scene))
        except api.StandardsError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------
# Arquivos
# ----------------------------------------------------------------------------------------------------------------

def _default_filename(context, extension):
    definition = api.active_definition(context.scene)
    base = definition.name if definition else "padrao"
    safe = "".join(ch if ch.isalnum() or ch in " -_." else "_" for ch in base).strip() or "padrao"
    return safe + extension


class BTM_OT_StandardsExportJSON(bpy.types.Operator, ExportHelper):
    """Exporta a definição ativa para um arquivo .btmdim.json"""
    bl_idname = "btm.standards_export_json"
    bl_label = "Exportar Definição (JSON)"
    bl_options = {'REGISTER'}

    filename_ext = ".btmdim.json"
    filter_glob: bpy.props.StringProperty(default="*.btmdim.json;*.json", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = os.path.join(io_json.user_folder(), _default_filename(context, self.filename_ext))
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        definition = api.active_definition(context.scene)
        if definition is None:
            self.report({'ERROR'}, "Nenhuma definição ativa.")
            return {'CANCELLED'}
        try:
            io_json.export_definition(self.filepath, definition)
        except OSError as exc:
            self.report({'ERROR'}, f"Não foi possível gravar: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Definição exportada: {self.filepath}")
        return {'FINISHED'}


class BTM_OT_StandardsImportJSON(bpy.types.Operator, ImportHelper):
    """Importa uma definição de um arquivo .btmdim.json"""
    bl_idname = "btm.standards_import_json"
    bl_label = "Importar Definição (JSON)"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".btmdim.json"
    filter_glob: bpy.props.StringProperty(default="*.btmdim.json;*.json", options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        try:
            definition, warnings = io_json.import_definition(context.scene, self.filepath)
        except (io_json.StandardFileError, api.StandardsError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        _set_report("Definição importada", [f"Definição: {definition.name}"] + [f"  {w}" for w in warnings])
        self.report({'INFO'}, f"Definição \"{definition.name}\" importada ({len(warnings)} aviso(s)).")
        _show_report(context)
        return {'FINISHED'}


class BTM_OT_StandardsImportPromob(bpy.types.Operator, ImportHelper):
    """Importa uma configuração de dimensões exportada pelo Promob (DIMENSIONEXPORT)"""
    bl_idname = "btm.standards_import_promob"
    bl_label = "Importar do Promob"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml;*.dimensionExport", options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        scene = context.scene
        try:
            doc = io_promob.read_dimensionexport(self.filepath)
            data = io_promob.to_definition_data(doc)
            standards = api.ensure_ready(scene)
        except (io_promob.PromobFormatError, api.StandardsError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        from ..standards import builtin
        name = api.unique_name(scene, data['name'])
        definition = standards.definitions.add()
        definition.uid = api.new_uid()
        definition.name = name
        definition.market = 'BR'
        definition.source = 'PROMOB_IMPORT'
        definition.updated_at = builtin.now_iso()
        builtin.fill_from_schema(definition, 'BR')
        for key, value in data['values'].items():
            api.set_value(definition, key, value)
        for raw in data['raw_attributes']:
            item = definition.raw_attributes.add()
            item.attr_id, item.value, item.key = raw['id'], raw['value'], raw['key']
        rep = data['report']
        lines = [f"Definição: {name}",
                 f"Atributos no arquivo: {rep['total']}; reconhecidos: {rep['mapped']}",
                 f"Não reconhecidos (mantidos para reexportação): {len(rep['unrecognized'])}",
                 f"  dos quais de família conhecida sem componente equivalente: "
                 f"{len(rep['confirmed_without_equivalent'])}"]
        if rep['invalid']:
            lines.append(f"Valores inválidos ignorados: {', '.join(rep['invalid'][:10])}")
        if rep['duplicates']:
            lines.append(f"IDs duplicados (vale o último): {', '.join(rep['duplicates'][:10])}")
        lines.append("Use \"Definir ativa\" para aplicar esta definição ao projeto.")
        _set_report("Importação do Promob", lines)
        self.report({'INFO'}, f"\"{name}\": {rep['mapped']} de {rep['total']} atributos reconhecidos.")
        _show_report(context)
        return {'FINISHED'}


class BTM_OT_StandardsExportPromob(bpy.types.Operator, ExportHelper):
    """Exporta a definição ativa no formato DIMENSIONEXPORT do Promob"""
    bl_idname = "btm.standards_export_promob"
    bl_label = "Exportar para o Promob"
    bl_options = {'REGISTER'}

    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        definition = api.active_definition(context.scene)
        if definition is None:
            self.report({'ERROR'}, "Nenhuma definição ativa.")
            return {'CANCELLED'}
        values = api.definition_values(definition)
        raw = [{'id': r.attr_id, 'value': r.value, 'key': r.key} for r in definition.raw_attributes]
        if not raw:
            raw = io_promob.attributes_from_values(values)
        try:
            io_promob.write_dimensionexport(self.filepath, definition.name, values, raw)
        except OSError as exc:
            self.report({'ERROR'}, f"Não foi possível gravar: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Exportado para o Promob: {self.filepath}")
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------
# Relatório (T045)
# ----------------------------------------------------------------------------------------------------------------

class BTM_OT_StandardsReport(bpy.types.Operator):
    """Mostra o relatório da última aplicação ou importação do Padrão de Dimensões"""
    bl_idname = "btm.standards_report"
    bl_label = "Relatório do Padrão de Dimensões"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=620)

    def draw(self, context):
        layout = self.layout
        layout.label(text=_LAST_REPORT['title'] or "Sem relatório.", icon='INFO')
        col = layout.column(align=True)
        for line in _LAST_REPORT['lines']:
            col.label(text=line)

    def execute(self, context):
        return {'FINISHED'}


classes = (
    BTM_OT_StandardsConfigurator,
    BTM_OT_StandardsApply,
    BTM_OT_StandardsSetActive,
    BTM_OT_StandardsDuplicate,
    BTM_OT_StandardsRename,
    BTM_OT_StandardsDelete,
    BTM_OT_StandardsExportJSON,
    BTM_OT_StandardsImportJSON,
    BTM_OT_StandardsImportPromob,
    BTM_OT_StandardsExportPromob,
    BTM_OT_StandardsReport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
