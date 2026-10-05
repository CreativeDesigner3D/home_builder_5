from . import draw_handlers, selection_cotas

_MODULES = (draw_handlers, selection_cotas)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
