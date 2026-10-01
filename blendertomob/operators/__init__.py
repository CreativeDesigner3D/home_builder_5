import bpy  # type: ignore
from .wall_builder import BTM_OT_WallBuilder
from .floor_builder import BTM_OT_FloorBuilder, BTM_OT_AdjustFloor
from .cabinet_builder import BTM_OT_CabinetBuilder
from .opening_builder import BTM_OT_InsertOpening, BTM_OT_RemoveOpening
from . import ops_cutting, ops_standards
from .ops_dimensions import BTM_OT_DimensionSettingsDialog, BTM_OT_ApplyDimensionPreset

classes = (
    BTM_OT_WallBuilder,
    BTM_OT_FloorBuilder,
    BTM_OT_AdjustFloor,
    BTM_OT_CabinetBuilder,
    BTM_OT_InsertOpening,
    BTM_OT_RemoveOpening,
    BTM_OT_DimensionSettingsDialog,
    BTM_OT_ApplyDimensionPreset,
)

# Módulos com registro próprio (produção e Padrão de Dimensões).
_MODULES = (ops_cutting, ops_standards)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
