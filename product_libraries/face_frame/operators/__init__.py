from . import ops_cabinet
from . import ops_defaults
from . import ops_finished_ends
from . import ops_placement
from . import op_modify_cabinet


def register():
    ops_cabinet.register()
    ops_defaults.register()
    ops_finished_ends.register()
    ops_placement.register()
    op_modify_cabinet.register()


def unregister():
    op_modify_cabinet.unregister()
    ops_placement.unregister()
    ops_finished_ends.unregister()
    ops_defaults.unregister()
    ops_cabinet.unregister()
