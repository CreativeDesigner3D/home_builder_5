"""Painéis da região lateral do Editor de Paredes (T030; RF-05, RF-08 a RF-10, D-07).

Só aparecem na área do Image Editor marcada como editor (`window.is_editor_area`):
- Ferramentas: Selecionar/Mover, Construir Parede, Inverter Sentido, Adicionar/Remover Vértice, Enquadrar;
- Painel: campos do trecho selecionado (comprimento na linha escolhida, ângulos, espessura, pés-direitos, orientação,
  tipo); ângulo do arco desabilitado, porque as paredes do Home Builder 5 são retas;
- Grid: tamanho e linhas magnéticas; padrões do lápis;
- OK / Cancelar, com o erro do último campo e a lista de itens que não cabem.
"""

import bpy  # type: ignore

from . import props, window


class _EditorPanel:
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Editor de Paredes"

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context)


class BTM_PT_WallEditorTools(_EditorPanel, bpy.types.Panel):
    bl_label = "Ferramentas"
    bl_idname = "BTM_PT_wall_editor_tools"
    bl_order = 0

    def draw(self, context):
        state = context.window_manager.btm_wall_editor
        col = self.layout.column(align=True)
        col.prop(state, "tool", expand=True)
        self.layout.operator("caffmob.wall_editor_fit", icon='ZOOM_ALL')


class BTM_PT_WallEditorSegment(_EditorPanel, bpy.types.Panel):
    bl_label = "Painel"
    bl_idname = "BTM_PT_wall_editor_segment"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        state = context.window_manager.btm_wall_editor
        s = props.session()
        chain, _i = s.segment() if s else (None, None)
        if chain is None:
            layout.label(text="Selecione um trecho na planta.", icon='INFO')
            return
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(state, "line")
        layout.prop(state, "length")
        layout.prop(state, "angle_abs")
        layout.prop(state, "angle_rel")
        row = layout.row()
        row.enabled = False
        row.label(text="Ângulo do Arco: paredes curvas não são suportadas")
        layout.prop(state, "lock_angle")
        layout.prop(state, "thickness")
        layout.prop(state, "height")
        layout.prop(state, "end_height")
        layout.prop(state, "direction", expand=True)
        layout.prop(state, "wall_type")


class BTM_PT_WallEditorGrid(_EditorPanel, bpy.types.Panel):
    bl_label = "Grid"
    bl_idname = "BTM_PT_wall_editor_grid"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        state = context.window_manager.btm_wall_editor
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(state, "grid_size")
        layout.prop(state, "magnetic")
        layout.separator()
        layout.label(text="Novas paredes")
        layout.prop(state, "new_direction")
        layout.prop(state, "new_thickness")
        layout.prop(state, "new_height")


class BTM_PT_WallEditorConfirm(_EditorPanel, bpy.types.Panel):
    bl_label = "Confirmar"
    bl_idname = "BTM_PT_wall_editor_confirm"
    bl_order = 99      # OK/Cancelar no fim do painel (D-30); com HIDE_HEADER o Blender ignora bl_order e põe no topo

    def draw(self, context):
        layout = self.layout
        s = props.session()
        if s is not None and s.error:
            layout.label(text=s.error, icon='ERROR')
        if s is not None and s.warnings:
            box = layout.box()
            box.label(text="Itens que não cabem:", icon='ERROR')
            for text in s.warnings[:8]:
                box.label(text=text)
            if len(s.warnings) > 8:
                box.label(text=f"… e mais {len(s.warnings) - 8}")
        if s is not None and s.removed_modules:
            box = layout.box()
            box.label(text="Módulos em trechos apagados:", icon='QUESTION')
            for text in s.removed_modules[:8]:
                box.label(text=text)
            if len(s.removed_modules) > 8:
                box.label(text=f"… e mais {len(s.removed_modules) - 8}")
            box.prop(context.window_manager.btm_wall_editor, "remove_modules")
            box.label(text="Desmarcado, os módulos ficam soltos no lugar.")
        if s is not None and s.height_mismatches:
            box = layout.box()
            from ..data import units
            box.label(text=f"Pé-direito do projeto: {units.format_value(s.project_height)}", icon='INFO')
            box.label(text="Paredes com outra altura:")
            for text in s.height_mismatches[:8]:
                box.label(text=text)
            if len(s.height_mismatches) > 8:
                box.label(text=f"… e mais {len(s.height_mismatches) - 8}")
            box.prop(context.window_manager.btm_wall_editor, "equalize_height")
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("caffmob.wall_editor_ok", text="OK", icon='CHECKMARK')
        row.operator("caffmob.wall_editor_cancel", text="Cancelar", icon='CANCEL')


classes = (BTM_PT_WallEditorTools, BTM_PT_WallEditorSegment, BTM_PT_WallEditorGrid, BTM_PT_WallEditorConfirm)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
