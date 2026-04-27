from . import props_hb_face_frame
from . import operators

NAMESPACE = "hb_face_frame"
MENU_NAME = "Face Frame"


def register():
    props_hb_face_frame.register()
    operators.register()


def unregister():
    operators.unregister()
    props_hb_face_frame.unregister()
