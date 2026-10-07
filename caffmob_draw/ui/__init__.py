from . import object_properties, panels, save_feedback, standards_tree

# Ordem de registro: a UIList antes dos painéis que a usam.
_MODULES = (standards_tree, panels, object_properties, save_feedback)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
