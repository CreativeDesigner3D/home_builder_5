"""Estado da inspeção (T049; data-delta I3-1). Fica em `WindowManager.btm_inspection` e não é salvo no arquivo."""

import bpy  # type: ignore


class BTM_PG_Interference(bpy.types.PropertyGroup):
    front_name: bpy.props.StringProperty(name="Frente")  # type: ignore
    module_name: bpy.props.StringProperty(name="Módulo")  # type: ignore
    hit_name: bpy.props.StringProperty(name="Objeto atingido")  # type: ignore
    location: bpy.props.FloatVectorProperty(name="Ponto", size=3, subtype='TRANSLATION')  # type: ignore
    kind: bpy.props.EnumProperty(
        name="Tipo",
        items=[('DOOR', "Porta", ""), ('FLIP_UP', "Basculante", ""), ('FLIP_DOWN', "Basculante p/ baixo", ""),
               ('DRAWER', "Gaveta", ""), ('PULLOUT', "Pullout", "")],
        default='DOOR')  # type: ignore


class BTM_PG_InspectionState(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(name="Inspeção ativa", default=False)  # type: ignore
    snap_stops: bpy.props.BoolProperty(
        name="Encaixar em 0°, 45° e 90°",
        description="O controle giratório encaixa nas paradas de 0°, 45° e 90° quando chega perto delas",
        default=True)  # type: ignore
    default_angle: bpy.props.EnumProperty(
        name="Ângulo de abertura",
        description="Ângulo usado pelo clique no modo de inspeção e por \"Abrir tudo\"",
        items=[('90', "90°", "Abre as portas até 90°"), ('45', "45°", "Abre as portas até 45°")],
        default='90')  # type: ignore
    interferences: bpy.props.CollectionProperty(type=BTM_PG_Interference)  # type: ignore
    interference_index: bpy.props.IntProperty(default=0)  # type: ignore
    checked_fronts: bpy.props.IntProperty(
        name="Frentes verificadas", description="Frentes verificadas na última checagem (-1 = nunca)",
        default=-1)  # type: ignore


classes = (BTM_PG_Interference, BTM_PG_InspectionState)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_inspection = bpy.props.PointerProperty(type=BTM_PG_InspectionState)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_inspection'):
        del bpy.types.WindowManager.btm_inspection
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
