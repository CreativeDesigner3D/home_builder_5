from . import props_closets

NAMESPACE = "hb_closets"
MENU_NAME = "Frameless"

def register():
    props_closets.register()

def unregister():
    props_closets.unregister()