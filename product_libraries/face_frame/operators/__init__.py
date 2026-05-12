from . import ops_cabinet
from . import ops_countertop
from . import ops_defaults
from . import ops_finished_ends
from . import ops_library
from . import ops_placement
from . import ops_styles
from . import op_modify_cabinet
from . import op_open_mode


def register():
    ops_cabinet.register()
    ops_countertop.register()
    ops_defaults.register()
    ops_finished_ends.register()
    ops_library.register()
    ops_placement.register()
    ops_styles.register()
    op_modify_cabinet.register()
    op_open_mode.register()


def unregister():
    op_open_mode.unregister()
    op_modify_cabinet.unregister()
    ops_styles.unregister()
    ops_placement.unregister()
    ops_library.unregister()
    ops_finished_ends.unregister()
    ops_defaults.unregister()
    ops_countertop.unregister()
    ops_cabinet.unregister()
