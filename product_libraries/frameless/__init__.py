from . import props_hb_frameless
from . import ops_hb_frameless
from . import menus_frameless
from . import types_frameless

NAMESPACE = "hb_frameless"
MENU_NAME = "Frameless"

def register():
    props_hb_frameless.register()
    ops_hb_frameless.register()
    menus_frameless.register()

def unregister():
    props_hb_frameless.unregister()
    ops_hb_frameless.unregister()
    menus_frameless.unregister()
