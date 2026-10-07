"""Geometria livre (feature 002, bloco 4): placa e caixa por pontos, editáveis e opcionalmente peças de fabricação.

- `props`: `Object.btm_geometry`
- `mesh`: malha BMesh e chapas da lista de peças (`cutting/part_sources.geometry_records`)
- `ops_create`: criação por pontos de referência
- `ops_edit`: duplicar, espelhar e excluir
"""


def _modules():
    from . import ops_create, ops_edit, props
    return (props, ops_create, ops_edit)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
