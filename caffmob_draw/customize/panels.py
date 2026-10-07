"""Painel "Personalizar módulo" e biblioteca de módulos do usuário (feature 003, T031; RF-01, RF-07 a RF-10).

Subpainéis de "Propriedades" (`BTM_PT_object_properties`, feature 002).
"""

import bpy  # type: ignore

from . import adapters, library_io, spec


def _section(layout, caps, section):
    """Caixa da seção; desabilitada com o motivo quando a biblioteca não suporta (RF-01)."""
    box = layout.box()
    box.label(text=spec.SECTION_LABELS[section])
    reason = caps.get(section)
    if reason:
        row = box.row()
        row.enabled = False
        row.label(text=reason, icon='INFO')
        return None
    return box


def _opening_label(item):
    front = spec.FRONT_LABELS.get(item.front, "—")
    if item.front == 'DRAWERS' and item.drawer_count > 1:
        front = f"{item.drawer_count} gavetas"
    return front


def draw_customize(layout, context):
    root, adapter = adapters.for_object(context.active_object)
    if adapter is None:
        layout.label(text="Selecione um módulo", icon='INFO')
        return
    if not hasattr(adapter, 'read'):
        layout.label(text="Personalização desta biblioteca ainda não disponível", icon='INFO')
        return
    caps = adapter.capabilities(root)
    current = adapter.read(root)
    layout.label(text=f"Módulo: {root.name}", icon='OBJECT_DATA')
    for index, item in enumerate(current.openings):
        box = layout.box()
        header = box.row()
        header.label(text=f"Vão {index + 1}: {_opening_label(item)}", icon='MESH_PLANE')
        header.operator("caffmob.customize_clear", text="", icon='X').path = item.path
        col = box.column(align=True)
        row = col.row(align=True)
        row.enabled = caps.get('FRONTS') is None
        row.operator_menu_enum("caffmob.customize_set_front", "front", text="Frente").path = item.path
        if caps.get('FRONTS') is None and caps.get('STYLES') is None:
            row.operator_menu_enum("caffmob.customize_set_style", "style",
                                   text=item.door_style or "Estilo").path = item.path
        row = col.row(align=True)
        row.enabled = caps.get('PULLS') is None
        op = row.operator("caffmob.customize_set_pull", text=f"Puxador: {item.pull_model or 'do projeto'}",
                          icon='EMPTY_ARROWS')
        op.path = item.path
        row = col.row(align=True)
        row.enabled = caps.get('MATERIALS') is None
        op = row.operator("caffmob.customize_set_material",
                          text=f"Material das frentes: {item.front_material or 'do módulo'}", icon='MATERIAL')
        op.target, op.path = 'FRONTS', item.path
        row = col.row(align=True)
        row.enabled = caps.get('INTERIOR') is None
        inner = item.interior or spec.Interior()
        text = f"Interior: {inner.shelves} prat., {inner.dividers} div., {inner.drawers} gav."
        row.operator("caffmob.customize_set_interior", text=text, icon='ALIGN_JUSTIFY').path = item.path
    for section in ('FRONTS', 'PULLS', 'INTERIOR'):
        if caps.get(section):
            _section(layout, caps, section)
    box = _section(layout, caps, 'MATERIALS')
    if box is not None:
        col = box.column(align=True)
        for group in spec.GROUPS:
            op = col.operator("caffmob.customize_set_material",
                              text=f"{spec.GROUP_LABELS[group]}: {current.group_materials.get(group, 'do módulo')}")
            op.target, op.group = 'GROUP', group
        obj = context.active_object
        if obj is not root and obj.type == 'MESH':
            op = col.operator("caffmob.customize_set_material",
                              text=f"Peça {obj.name}: {obj.btm_custom.material or 'do grupo'}", icon='MESH_CUBE')
            op.target = 'PART'
    layout.operator("caffmob.module_save", icon='FILE_TICK')


def draw_library(layout, context):
    row = layout.row(align=True)
    row.operator("caffmob.module_open_folder", text="Abrir pasta", icon='FILE_FOLDER')
    try:
        entries = library_io.list_modules()
    except (OSError, ValueError) as exc:
        layout.label(text=f"Biblioteca indisponível: {exc}", icon='ERROR')
        return
    if not entries:
        layout.label(text="Nenhum módulo salvo ainda.", icon='INFO')
        return
    category = None
    col = layout.column(align=True)
    for entry in entries:
        if entry["category"] != category:
            category = entry["category"]
            col.label(text=category, icon='FILE_FOLDER')
        row = col.row(align=True)
        label = entry["name"] if entry["has_manifest"] else f"{entry['name']} (sem personalização)"
        row.operator("caffmob.module_insert", text=label, icon='IMPORT').filepath = entry["blend"]
        row.operator("caffmob.module_rename", text="", icon='GREASEPENCIL').filepath = entry["blend"]
        row.operator("caffmob.module_delete", text="", icon='TRASH').filepath = entry["blend"]


class BTM_PT_CustomizeModule(bpy.types.Panel):
    bl_label = "Modelos — Personalizar módulo"
    bl_idname = "BTM_PT_customize_module"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return adapters.for_object(context.active_object)[1] is not None

    def draw(self, context):
        draw_customize(self.layout, context)


class BTM_PT_ModuleLibrary(bpy.types.Panel):
    bl_label = "Biblioteca de módulos"
    bl_idname = "BTM_PT_module_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        draw_library(self.layout, context)


classes = (BTM_PT_CustomizeModule, BTM_PT_ModuleLibrary)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
