from . import props_hb_face_frame
from . import types_face_frame
from . import menus_face_frame
from . import operators
from . import ui_face_frame

NAMESPACE = "hb_face_frame"
MENU_NAME = "Face Frame"


def register():
    props_hb_face_frame.register()
    menus_face_frame.register()
    operators.register()
    ui_face_frame.register()


def unregister():
    ui_face_frame.unregister()
    operators.unregister()
    menus_face_frame.unregister()
    props_hb_face_frame.unregister()
