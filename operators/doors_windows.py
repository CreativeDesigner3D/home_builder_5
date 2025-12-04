import bpy
from .. import hb_types, hb_snap, units
import math
from mathutils import Vector
from bpy_extras import view3d_utils

class home_builder_doors_windows_OT_draw_doors_windows(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.draw_doors_windows"
    bl_label = "Draw Doors and Windows"
    bl_description = "Enter Draw Doors and Windows Mode. This will allow you to place a door or window on a wall"
    bl_options = {'UNDO'}

    geo_node = None
    selected_wall = None

    def create_door(self,context):
        props = bpy.context.scene.home_builder
        self.geo_node = hb_types.GeoNodeObject()
        self.geo_node.create("GeoNodeCage","Door")
        self.geo_node.set_input('Dim X', props.door_single_width)
        self.geo_node.set_input('Dim Y', props.wall_thickness)
        self.geo_node.set_input('Dim Z', props.door_height)
        self.geo_node.obj.display_type = 'WIRE'

    def execute(self, context):
        self.region = hb_snap.get_region(context)
        self.mouse_pos = Vector()
        self.hit_object = None  
        self.hit_location = ()    

        self.start_point = ()
        context.window_manager.modal_handler_add(self)

        self.create_door(context)
        return {'RUNNING_MODAL'}  

    def set_position(self):
        self.geo_node.obj.parent = None
        self.geo_node.obj.location = self.hit_location
        if self.hit_object:
            if 'IS_WALL_BP' in self.hit_object:
                self.selected_wall = hb_types.GeoNodeWall(self.hit_object)
                self.geo_node.obj.parent = self.selected_wall.obj
                self.geo_node.obj.matrix_world[0][3] = self.hit_location[0]
                self.geo_node.obj.matrix_world[1][3] = self.hit_location[1]
                self.geo_node.obj.rotation_euler.z = 0
                self.geo_node.obj.location.x = self.geo_node.obj.location.x
                self.geo_node.obj.location.y = 0
                self.geo_node.set_input("Dim Y",self.selected_wall.get_input('Thickness'))                
        else:
            pass
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}  

        # Hide objects to ignore then call snap.main
        # Sets self.hit_location and self.hit_object
        self.geo_node.obj.hide_set(True)
        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))
        hb_snap.main(self, event.ctrl, context)
        self.geo_node.obj.hide_set(False)

        self.set_position()
        
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            return {'FINISHED'}

        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            return {'FINISHED'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}

classes = (
    home_builder_doors_windows_OT_draw_doors_windows,
)

register, unregister = bpy.utils.register_classes_factory(classes)                  