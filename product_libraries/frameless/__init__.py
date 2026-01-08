from . import props_hb_frameless
from . import operators
from . import menus_frameless
from . import types_frameless

NAMESPACE = "hb_frameless"
MENU_NAME = "Frameless"

def register():
    props_hb_frameless.register()
    operators.register()
    menus_frameless.register()

def unregister():
    props_hb_frameless.unregister()
    operators.unregister()
    menus_frameless.unregister()
