import bpy
from . import props_obstacles
from . import ops_obstacles

def register():
    props_obstacles.register()
    ops_obstacles.register()

def unregister():
    ops_obstacles.unregister()
    props_obstacles.unregister()
