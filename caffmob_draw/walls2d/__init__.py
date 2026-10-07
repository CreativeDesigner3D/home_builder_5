"""Editor de Paredes 2D (feature 002, bloco 3): planta a lápis das paredes do Home Builder 5.

- `model`: nós, trechos, linhas interna/externa/referência e edição (Python puro, testável fora do Blender)
- `scene_io` / `apply`: leitura das paredes da cena e aplicação do rascunho no OK
- `props`: sessão do editor e campos do trecho (`WindowManager.btm_wall_editor`)
- `window`: janela própria (Image Editor) e desenho da planta
- `ops_editor`: abrir, modal de interação, OK/Cancelar
- `panels`: região lateral do editor
"""


def _modules():
    # Import tardio: `model` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import ops_editor, panels, props, window
    return (props, window, ops_editor, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
