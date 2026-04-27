from . import ops_cabinet
from . import ops_defaults


def register():
    ops_cabinet.register()
    ops_defaults.register()


def unregister():
    ops_cabinet.unregister()
    ops_defaults.unregister()
