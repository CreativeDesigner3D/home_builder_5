"""Estado do modo "Mover Sobre" (T006; data-delta §1). Fica em `WindowManager.btm_move_over` e não é salvo."""

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


classes = (BTM_PG_MoveOverState,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_move_over = bpy.props.PointerProperty(type=BTM_PG_MoveOverState)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_move_over'):
        del bpy.types.WindowManager.btm_move_over
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
