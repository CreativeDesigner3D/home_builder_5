"""Inspeção e movimento (incremento 3, bloco 1): abrir portas e gavetas de todas as linhas, controle no 3D,
salvar fechado e interferência do envelope de abertura (RF-090, RF-091; RN-14).

- `pivot_math`: matemática pura das poses (testável fora do Blender)
- `fronts` + `adapters/*`: frentes de cada linha com um valor de abertura comum
- `ops_inspect`: abrir/fechar tudo e o modo de inspeção (modal)
- `gizmo`: controle giratório/seta com paradas em 0°, 45° e 90°
- `save_guard`: salva fechado e reabre a vista (save_pre/save_post)
- `interference`, `ops_interference`, `overlay`: detector, operador e destaque no viewport
"""



def _modules():
    # Import tardio: `pivot_math` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import gizmo, ops_inspect, ops_interference, overlay, props, save_guard
    # Ordem de registro: dados, operadores, gizmo, handlers.
    return (props, ops_inspect, ops_interference, gizmo, overlay, save_guard)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
