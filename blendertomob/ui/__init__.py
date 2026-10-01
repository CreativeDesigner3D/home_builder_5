from . import panels, standards_tree

# Ordem de registro: a UIList antes dos painéis que a usam.
_MODULES = (standards_tree, panels)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
