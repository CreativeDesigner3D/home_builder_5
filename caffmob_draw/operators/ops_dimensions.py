"""Operadores antigos de dimensões (T043): mantidos por compatibilidade com menus e atalhos existentes.

Os dois passam a abrir o Configurador de Dimensões (`caffmob.standards_configurator`), que substitui
`btm_settings.dimension_settings` e os presets de `data/dimensions_preset.py`.
"""

import bpy  # type: ignore


def _open_configurator(operator, context):
    if bpy.app.background or context.window is None:
        operator.report({'INFO'}, "Use o Configurador de Dimensões (caffmob.standards_configurator).")
        return {'CANCELLED'}
    bpy.ops.caffmob.standards_configurator('INVOKE_DEFAULT')
    return {'FINISHED'}


class BTM_OT_DimensionSettingsDialog(bpy.types.Operator):
    """Abre o Configurador de Dimensões (padrão de medidas, chapas, fitas e limites)"""
    bl_idname = "caffmob.dimension_settings_dialog"
    bl_label = "Configurações de Dimensões"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return _open_configurator(self, context)

    def execute(self, context):
        return _open_configurator(self, context)


class BTM_OT_ApplyDimensionPreset(bpy.types.Operator):
    """Abre o Configurador de Dimensões (os presets antigos foram substituídos pelas definições do padrão)"""
    bl_idname = "caffmob.apply_dimension_preset"
    bl_label = "Aplicar Preset de Dimensão"
    bl_options = {'REGISTER'}

    preset_key: bpy.props.StringProperty(name="Chave do Preset", default="COZINHA_INFERIOR")  # type: ignore

    def invoke(self, context, event):
        return _open_configurator(self, context)

    def execute(self, context):
        return _open_configurator(self, context)


classes = (
    BTM_OT_DimensionSettingsDialog,
    BTM_OT_ApplyDimensionPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
