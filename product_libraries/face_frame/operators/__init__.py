from . import ops_cabinet
from . import ops_defaults
from . import ops_finished_ends
from . import ops_placement


def register():
    ops_cabinet.register()
    ops_defaults.register()
    ops_finished_ends.register()
    ops_placement.register()


def unregister():
    ops_placement.unregister()
    ops_finished_ends.unregister()
    ops_defaults.unregister()
    ops_cabinet.unregister()
