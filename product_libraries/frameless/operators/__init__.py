from . import ops_placement
from . import ops_cabinet
from . import ops_opening
from . import ops_interior
from . import ops_front
from . import ops_appliance
from . import ops_styles
from . import ops_crown
from . import ops_library
from . import ops_defaults
from . import ops_finished_ends


def register():
    ops_placement.register()
    ops_cabinet.register()
    ops_opening.register()
    ops_interior.register()
    ops_front.register()
    ops_appliance.register()
    ops_styles.register()
    ops_crown.register()
    ops_library.register()
    ops_defaults.register()
    ops_finished_ends.register()


def unregister():
    ops_placement.unregister()
    ops_cabinet.unregister()
    ops_opening.unregister()
    ops_interior.unregister()
    ops_front.unregister()
    ops_appliance.unregister()
    ops_styles.unregister()
    ops_crown.unregister()
    ops_library.unregister()
    ops_defaults.unregister()
    ops_finished_ends.unregister()
