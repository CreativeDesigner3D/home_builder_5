from . import props_hb_face_frame
from . import appliance_panels
from . import types_face_frame
from . import types_face_frame_corner
from . import menus_face_frame
from . import operators
from . import ui_face_frame
from . import dim_edit_overlay

NAMESPACE = "hb_face_frame"
MENU_NAME = "Face Frame"


def register():
    props_hb_face_frame.register()
    appliance_panels.register()
    menus_face_frame.register()
    operators.register()
    ui_face_frame.register()
    dim_edit_overlay.register()


def unregister():
    dim_edit_overlay.unregister()
    ui_face_frame.unregister()
    operators.unregister()
    menus_face_frame.unregister()
    appliance_panels.unregister()
    props_hb_face_frame.unregister()
