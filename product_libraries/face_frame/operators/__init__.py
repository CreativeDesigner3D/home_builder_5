from . import ops_cabinet
from . import ops_defaults
from . import ops_placement


def register():
    ops_cabinet.register()
    ops_defaults.register()
    ops_placement.register()


def unregister():
    ops_placement.unregister()
    ops_defaults.unregister()
    ops_cabinet.unregister()
