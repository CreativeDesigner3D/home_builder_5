"""Personalização de módulos inseridos e biblioteca de módulos do usuário (feature 003, bloco A).

- `spec`, `manifest`: núcleos puros (testáveis fora do Blender)
- `props`: `Object.btm_custom`, gravado no vão ou na peça
- `adapters`: um adaptador por biblioteca (frameless, face frame, closets, `btm`)
- `reapply`: reaplica a personalização depois da reconstrução das frentes
- `library_io`, `ops_library`: salvar e inserir módulos
- `ops_customize`, `panels`: operadores e painel "Personalizar módulo"
"""


def _modules():
    # Import tardio: `spec` e `manifest` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import ops_customize, ops_library, panels, props
    return (props, ops_customize, ops_library, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
