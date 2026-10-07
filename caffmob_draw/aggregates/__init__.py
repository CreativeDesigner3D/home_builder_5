"""Agregados e folhas de porta convertidas (feature 003, blocos B e folha de porta).

- `limits`, `sweep`: núcleos puros (testáveis fora do Blender)
- `props`: `Object.btm_aggregate`
- `convert`, `apply`: converter, desconverter e posicionar no espaço do pai
- `perforate`, `production`: recorte 3D, furo real e peça de produção
- `leaf`, `collision`, `overlay`: folha de porta, parada na batida e simulação gráfica
- `ops_import`, `ops_aggregate`, `panels`: importação, operadores e painel
"""


def _modules():
    # Import tardio: `limits` e `sweep` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import apply, collision, ops_aggregate, ops_import, overlay, panels, props
    return (props, apply, collision, ops_import, ops_aggregate, overlay, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
