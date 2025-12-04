from . import props_face_frame

NAMESPACE = "hb_face_frame"
MENU_NAME = "Face Frame"

def register():
    props_face_frame.register()

def unregister():
    props_face_frame.unregister()