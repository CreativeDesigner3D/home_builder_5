""""Mover Sobre" (feature 002, bloco 2): arrastar um objeto sobre outro com o botão direito e alinhá-los pelas vistas
superior e frontal.

- `align`: matemática pura dos alvos e deslocamentos (testável fora do Blender)
- `scene`: caixas no referencial de B, prévia, restauração e sobreposição
- `props`: estado do modo (`WindowManager.btm_move_over`)
- `ops_drag`: botão, atalho do botão direito e arraste
- `ops_dialog`: janela com as duas vistas
- `ops_move_on_wall`: arrastar o módulo só no plano da parede
"""


def _modules():
    # Import tardio: `align` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import ops_dialog, ops_drag, ops_move_on_wall, props
    return (props, ops_dialog, ops_drag, ops_move_on_wall)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
