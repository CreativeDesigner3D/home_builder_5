"""Verificar interferência do envelope de abertura (T074; D-29, RF-091, RN-14).

Roda só sob demanda. Ausência de aviso só vale para as frentes verificadas: o relatório diz quantas foram.
"""

import bpy  # type: ignore

from . import interference
from .ops_inspect import scope_fronts


class BTM_OT_CheckFrontInterference(bpy.types.Operator):
    """Verifica se portas, basculantes e gavetas batem em outros objetos ao abrir (paredes, sancas, módulos)"""
    bl_idname = "caffmob.check_front_interference"
    bl_label = "Verificar Interferência"
    bl_options = {'REGISTER'}

    scope: bpy.props.EnumProperty(
        name="Escopo",
        items=[('ALL', "Projeto", "Todas as frentes do projeto"),
               ('SELECTED', "Selecionados", "Frentes dos módulos e peças selecionados")],
        default='ALL')  # type: ignore

    def execute(self, context):
        targets = scope_fronts(context, self.scope)
        results, checked = interference.check_fronts(context, targets)
        interference.store_results(context.window_manager, results, checked)
        for area in (context.screen.areas if context.screen else []):
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        if checked == 0:
            self.report({'WARNING'}, "Nenhuma frente foi verificada: não há portas ou gavetas no escopo.")
        elif results:
            self.report({'WARNING'}, f"{len(results)} interferência(s) em {checked} frente(s) verificada(s).")
        else:
            self.report({'INFO'}, f"Nenhuma interferência nas {checked} frente(s) verificada(s).")
        return {'FINISHED'}


class BTM_OT_InterferenceGoto(bpy.types.Operator):
    """Centraliza a vista no ponto da interferência e seleciona a frente e o objeto atingido"""
    bl_idname = "caffmob.interference_goto"
    bl_label = "Ir para a Interferência"
    bl_options = {'REGISTER'}

    index: bpy.props.IntProperty(name="Item", default=0, min=0)  # type: ignore

    def execute(self, context):
        state = context.window_manager.btm_inspection
        if not (0 <= self.index < len(state.interferences)):
            return {'CANCELLED'}
        item = state.interferences[self.index]
        state.interference_index = self.index
        for obj in context.selected_objects:
            obj.select_set(False)
        for name in (item.front_name, item.hit_name):
            obj = context.scene.objects.get(name)
            if obj is not None and obj.visible_get():
                obj.select_set(True)
        front = context.scene.objects.get(item.front_name)
        if front is not None and front.visible_get():
            context.view_layer.objects.active = front
        for area in (context.screen.areas if context.screen else []):
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_location = item.location
                area.tag_redraw()
        return {'FINISHED'}


classes = (BTM_OT_CheckFrontInterference, BTM_OT_InterferenceGoto)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
