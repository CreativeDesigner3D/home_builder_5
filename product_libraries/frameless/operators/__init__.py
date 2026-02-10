from . import ops_placement
from . import ops_cabinet
from . import ops_opening
from . import ops_interior
from . import ops_front
from . import ops_appliance
from . import ops_styles
from . import ops_crown
from . import ops_toe_kick
from . import ops_upper_bottom
from . import ops_library
from . import ops_defaults
from . import ops_finished_ends
from . import ops_products
from . import ops_countertop
from . import ops_cleanup


def register():
    ops_placement.register()
    ops_cabinet.register()
    ops_opening.register()
    ops_interior.register()
    ops_front.register()
    ops_appliance.register()
    ops_styles.register()
    ops_crown.register()
    ops_toe_kick.register()
    ops_upper_bottom.register()
    ops_library.register()
    ops_defaults.register()
    ops_finished_ends.register()
    ops_products.register()
    ops_countertop.register()
    ops_cleanup.register()


def unregister():
    ops_placement.unregister()
    ops_cabinet.unregister()
    ops_opening.unregister()
    ops_interior.unregister()
    ops_front.unregister()
    ops_appliance.unregister()
    ops_styles.unregister()
    ops_crown.unregister()
    ops_toe_kick.unregister()
    ops_upper_bottom.unregister()
    ops_library.unregister()
    ops_defaults.unregister()
    ops_finished_ends.unregister()
    ops_products.unregister()
    ops_countertop.unregister()
    ops_cleanup.unregister()
