import bpy
from . import types_frameless
from ... import hb_utils
from ...units import inch

class hb_frameless_OT_toggle_mode(bpy.types.Operator):
    """Toggle Cabinet Openings"""
    bl_idname = "hb_frameless.toggle_mode"
    bl_label = 'Toggle Mode'
    bl_description = "This will toggle the cabinet mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name",default="")# type: ignore
    toggle_type: bpy.props.StringProperty(name="Toggle Type",default="")# type: ignore
    toggle_on: bpy.props.BoolProperty(name="Toggle On",default=False)# type: ignore

    def has_child_item_type(self,obj,item_type):
        for child in obj.children_recursive:
            if item_type in child:
                return True
        return False

    def toggle_cabinet_color(self,obj,toggle,type_name="",dont_show_parent=True):
        hb_props = bpy.context.window_manager.home_builder
        add_on_prefs = hb_props.get_user_preferences(bpy.context)         

        if toggle:
            if dont_show_parent:
                if self.has_child_item_type(obj,type_name):
                    return
            obj.color = add_on_prefs.cabinet_color
            obj.show_in_front = True
            obj.hide_viewport = False
            obj.display_type = 'SOLID'
            obj.select_set(True)

        else:
            obj.show_name = False
            obj.show_in_front = False
            if 'IS_GEONODE_CAGE' in obj:
                obj.color = [0.000000, 0.000000, 0.000000, 0.100000]
                obj.display_type = 'WIRE'
                obj.hide_viewport = True
            elif 'IS_2D_ANNOTATION' in obj:
                obj.color = add_on_prefs.annotation_color
                obj.display_type = 'SOLID'
            else:
                obj.color = [1.000000, 1.000000, 1.000000, 1.000000]
                obj.display_type = 'SOLID'
            obj.select_set(False)

    def toggle_obj(self,obj):
        if 'IS_WALL_BP' in obj or 'IS_ENTRY_DOOR_BP' in obj or 'IS_WINDOW_BP' in obj:
            return        
        if self.toggle_type in obj:
            self.toggle_cabinet_color(obj,True,type_name=self.toggle_type)
        else:
            self.toggle_cabinet_color(obj,False,type_name=self.toggle_type)

    def execute(self, context):
        props = context.scene.hb_frameless
        if props.frameless_selection_mode == 'Cabinets':
            self.toggle_type="IS_FRAMELESS_CABINET_CAGE"
        elif props.frameless_selection_mode == 'Bays':
            self.toggle_type="IS_FRAMELESS_BAY_CAGE"            
        elif props.frameless_selection_mode == 'Openings':
            self.toggle_type="IS_FRAMELESS_OPENING_CAGE"
        elif props.frameless_selection_mode == 'Interiors':
            self.toggle_type="IS_FRAMELESS_INTERIOR_PART"
        elif props.frameless_selection_mode == 'Parts':
            self.toggle_type="NO_TYPE"      

        if self.search_obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.search_obj_name]
            self.toggle_obj(obj)
            for child in obj.children_recursive:
                self.toggle_obj(child)
        else:
            for obj in context.scene.objects:
                self.toggle_obj(obj)
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class hb_frameless_OT_update_cabinet_sizes(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_sizes"
    bl_label = "Update Cabinet Sizes"

    def execute(self, context):
        props = context.scene.hb_frameless

        # cabinets = types_frameless.get_all_cabinets(context)

        # for cabinet in cabinets:
        #     cab_type = cabinet.get_prompt("Cabinet Type")
        #     is_corner = cabinet.get_prompt("Corner Type")
        #     top_cab_height = cabinet.get_prompt("Top Cabinet Height")
        #     if top_cab_height:
        #         cabinet.get_prompt("Top Cabinet Height").set_value(props.top_stacked_cabinet_height)
        #     if cab_type.get_value() == 'Tall':
        #         cabinet.set_input("Dim Z",props.tall_cabinet_height)
        #         cabinet.set_input("Dim Y",props.tall_cabinet_depth)

        #     if cab_type.get_value() == 'Upper':
        #         cabinet.set_input("Dim Z",props.upper_cabinet_height)
        #         cabinet.obj.location.z = props.default_wall_cabinet_location
        #         if is_corner.get_value() == 'Pie Cut':
        #             pass
        #         else:
        #             cabinet.set_input("Dim Y",props.upper_cabinet_depth)

        #     if cab_type.get_value() == 'Base':
        #         cabinet.set_input("Dim Z",props.base_cabinet_height)
        #         if is_corner.get_value() == 'Pie Cut':
        #             pass
        #         else:
        #             cabinet.set_input("Dim Y",props.base_cabinet_depth)

        # pc_utils.run_calc_fix(context)
        # pc_utils.run_calc_fix(context)
        return {'FINISHED'}


class hb_frameless_OT_draw_cabinet(bpy.types.Operator):
    bl_idname = "hb_frameless.draw_cabinet"
    bl_label = "Draw Cabinet"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name")#type: ignore

    def execute(self, context):
        print('TODO: MODAL DRAW CABINET',self.cabinet_name)
        cabinet = types_frameless.Cabinet()
        cabinet.create('Cabinet') 

        doors = types_frameless.Doors()
        cabinet.add_cage_to_bay(doors)

        bpy.ops.hb_frameless.toggle_mode(search_obj_name=cabinet.obj.name)      
        return {'FINISHED'}


class hb_frameless_OT_update_toe_kick_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_toe_kick_prompts"
    bl_label = "Update Toe Kick Prompts"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        for obj in context.scene.objects:
            if 'Toe Kick Height' in obj:
                obj['Toe Kick Height'] = frameless_props.default_toe_kick_height
            if 'Toe Kick Setback' in obj:
                obj['Toe Kick Setback'] = frameless_props.default_toe_kick_setback  
            hb_utils.run_calc_fix(context,obj)              
        return {'FINISHED'}


class hb_frameless_OT_update_base_top_construction_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_base_top_construction_prompts"
    bl_label = "Update Base Top Construction Prompts"

    def execute(self, context):
        print('TODO: Update Base Top Construction Prompts')
        return {'FINISHED'}


class hb_frameless_OT_update_drawer_front_height_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_drawer_front_height_prompts"
    bl_label = "Update Drawer Front Height Prompts"

    def execute(self, context):
        print('TODO: Update Drawer Front Height Prompts')
        return {'FINISHED'}


class hb_frameless_OT_update_door_and_drawer_front_style(bpy.types.Operator):
    bl_idname = "hb_frameless.update_door_and_drawer_front_style"
    bl_label = "Update Door and Drawer Front Style"

    selected_index: bpy.props.IntProperty(name="Selected Index",default=-1)# type: ignore

    def execute(self, context):
        door_fronts = []
        drawer_fronts = []
        frameless_props = context.scene.hb_frameless

        selected_door_style = frameless_props.door_styles[self.selected_index]

        for obj in context.scene.objects:
            if 'IS_DOOR_FRONT' in obj:
                door_fronts.append(obj)
            if 'IS_DRAWER_FRONT' in obj:
                drawer_fronts.append(obj)

        for door_front_obj in door_fronts:
            door_front = types_frameless.CabinetDoor(door_front_obj)
            door_style = door_front.add_part_modifier('CPM_5PIECEDOOR','Door Style')
            door_style.set_input("Left Stile Width",selected_door_style.stile_width)
            door_style.set_input("Right Stile Width",selected_door_style.stile_width)
            door_style.set_input("Top Rail Width",selected_door_style.rail_width)
            door_style.set_input("Bottom Rail Width",selected_door_style.rail_width)
            door_style.set_input("Panel Thickness",selected_door_style.panel_thickness)
            door_style.set_input("Panel Inset",selected_door_style.panel_inset)

        return {'FINISHED'}


class hb_frameless_OT_add_door_style(bpy.types.Operator):
    bl_idname = "hb_frameless.add_door_style"
    bl_label = "Add Door Style"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        door_style = frameless_props.door_styles.add()
        door_style.name = "New Door Style"
        return {'FINISHED'}


classes = (
    hb_frameless_OT_toggle_mode,
    hb_frameless_OT_update_cabinet_sizes,
    hb_frameless_OT_draw_cabinet,
    hb_frameless_OT_update_toe_kick_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_add_door_style,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    