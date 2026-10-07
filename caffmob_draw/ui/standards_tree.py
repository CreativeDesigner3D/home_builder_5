"""Árvore do Configurador de Dimensões (T031; D-16).

`UIList` sobre `WindowManager.btm_standards_draft.tree`: grupos (Medidas Máximas; linha → Dimensões Externas /
Chapas / Componentes) com abrir/fechar por clique e parâmetros com o valor do rascunho na unidade do usuário.
A busca por nome fica no campo `draft.search` (a árvore é refeita a cada tecla).
"""

import bpy  # type: ignore

from ..data import dimension_schema as schema


class BTM_UL_StandardsTree(bpy.types.UIList):
    bl_idname = "BTM_UL_StandardsTree"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0, flt_flag=0):
        from ..standards import api
        row = layout.row(align=True)
        for _ in range(item.depth):
            row.separator(factor=1.6)
        if item.node_type == 'GROUP':
            opened = bool(data.search.strip()) or item.path in api.expanded_paths(data)
            row.label(text=item.label, icon='DISCLOSURE_TRI_DOWN' if opened else 'DISCLOSURE_TRI_RIGHT')
            return
        param = schema.get_param(item.key)
        value_item = data.values.get(item.key)
        if param is None or value_item is None:
            row.label(text=item.label)
            return
        value = value_item.text if value_item.is_text else value_item.value
        text = api.format_param_value(param, value, api.user_unit(context.scene))
        row.label(text=item.label, icon='DOT' if item.key == data.selected_key else 'BLANK1')
        sub = row.row()
        sub.alignment = 'RIGHT'
        sub.label(text=text)

    def filter_items(self, context, data, propname):
        # Filtragem feita na reconstrução da árvore (draft.search); aqui mantém a ordem original.
        return [], []


classes = (BTM_UL_StandardsTree,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
