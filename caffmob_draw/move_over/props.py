"""Estado do modo "Mover Sobre" (T006; data-delta §1). Fica em `WindowManager.btm_move_over` e não é salvo.

Feature 003 (T009): passo do teclado e posição relativa/absoluta; posições salvas na cena
(`Scene.btm_saved_positions`, salvas no arquivo) e plano de inserção da sessão (`WindowManager.btm_insertion_plane`).
"""

import bpy  # type: ignore


def _redraw(_self, context):
    screen = getattr(context, 'screen', None)
    for area in (screen.areas if screen else []):
        if area.type == 'VIEW_3D':
            area.tag_redraw()


class BTM_PG_MoveOverState(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Mover Sobre",
        description=("Com o modo ligado, arraste um objeto sobre outro com o botão direito para alinhá-los. "
                     "O botão direito deixa de abrir o menu de contexto enquanto o modo estiver ligado"),
        default=False, update=_redraw)  # type: ignore
    tolerance_px: bpy.props.IntProperty(
        name="Tolerância", description="Distância em pixels para considerar um clique perto de um alvo",
        default=12, min=4, max=40)  # type: ignore
    step: bpy.props.FloatProperty(
        name="Passo", description="Quanto as setas e Page Up/Down movem o objeto na janela Mover Sobre",
        default=0.01, min=0.0001, max=1.0, subtype='DISTANCE', unit='LENGTH')  # type: ignore
    show_relative: bpy.props.BoolProperty(
        name="Visualizar posição relativa",
        description="Ligado: os campos mostram a distância à referência. Desligado: a posição no projeto",
        default=True)  # type: ignore


class BTM_PG_SavedPosition(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Nome")  # type: ignore
    delta: bpy.props.FloatVectorProperty(size=3, subtype='TRANSLATION', unit='LENGTH')  # type: ignore
    rotation: bpy.props.FloatProperty(name="Rotação")  # type: ignore
    b_side: bpy.props.EnumProperty(items=[('LEFT', "Esquerda", ""), ('RIGHT', "Direita", "")])  # type: ignore


class BTM_PG_InsertionPlane(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(name="Plano de inserção ativo", default=False, update=_redraw)  # type: ignore
    matrix: bpy.props.FloatVectorProperty(size=16)  # type: ignore
    source_name: bpy.props.StringProperty(name="Origem")  # type: ignore


classes = (BTM_PG_MoveOverState, BTM_PG_SavedPosition, BTM_PG_InsertionPlane)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_move_over = bpy.props.PointerProperty(type=BTM_PG_MoveOverState)
    bpy.types.WindowManager.btm_insertion_plane = bpy.props.PointerProperty(type=BTM_PG_InsertionPlane)
    bpy.types.Scene.btm_saved_positions = bpy.props.CollectionProperty(type=BTM_PG_SavedPosition)
    bpy.types.Scene.btm_saved_positions_index = bpy.props.IntProperty(default=0)


def unregister():
    for owner, attr in ((bpy.types.Scene, 'btm_saved_positions_index'), (bpy.types.Scene, 'btm_saved_positions'),
                        (bpy.types.WindowManager, 'btm_insertion_plane')):
        if hasattr(owner, attr):
            delattr(owner, attr)
    if hasattr(bpy.types.WindowManager, 'btm_move_over'):
        del bpy.types.WindowManager.btm_move_over
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
