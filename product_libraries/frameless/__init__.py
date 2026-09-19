from . import props_hb_frameless
from . import props_elevation_templates
from . import operators
from . import menus_frameless
from . import types_frameless
from . import types_products
from . import dim_edit_overlay
from . import quiet_cages

NAMESPACE = "hb_frameless"
MENU_NAME = "Frameless"

def register():
    props_hb_frameless.register()
    props_elevation_templates.register()
    operators.register()
    menus_frameless.register()
    dim_edit_overlay.register()
    quiet_cages.register()

def unregister():
    quiet_cages.unregister()
    dim_edit_overlay.unregister()
    props_hb_frameless.unregister()
    props_elevation_templates.unregister()
    operators.unregister()
    menus_frameless.unregister()
