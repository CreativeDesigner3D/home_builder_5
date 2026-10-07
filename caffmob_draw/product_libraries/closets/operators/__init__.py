from . import ops_closet
from . import op_grab_closet
from . import op_open_door_closet


def register():
    ops_closet.register()
    op_grab_closet.register()
    op_open_door_closet.register()


def unregister():
    op_open_door_closet.unregister()
    op_grab_closet.unregister()
    ops_closet.unregister()
