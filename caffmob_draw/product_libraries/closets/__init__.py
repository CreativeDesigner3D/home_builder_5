from . import props_closets
from . import menus_closets
from . import operators
from . import gpu_overlay_closets

NAMESPACE = "hb_closets"
MENU_NAME = "Closet"


def register():
    props_closets.register()
    menus_closets.register()
    operators.register()
    gpu_overlay_closets.register()


def unregister():
    gpu_overlay_closets.unregister()
    operators.unregister()
    menus_closets.unregister()
    props_closets.unregister()
