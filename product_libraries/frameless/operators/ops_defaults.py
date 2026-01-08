import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_types, units

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
    """Update all door and drawer fronts with the selected door style"""
    bl_idname = "hb_frameless.update_door_and_drawer_front_style"
    bl_label = "Update Door and Drawer Front Style"
    bl_options = {'REGISTER', 'UNDO'}

    selected_index: bpy.props.IntProperty(name="Selected Index", default=-1)# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        frameless_props = main_scene.hb_frameless

        if self.selected_index < 0 or self.selected_index >= len(frameless_props.door_styles):
            self.report({'WARNING'}, "Invalid door style index")
            return {'CANCELLED'}

        selected_door_style = frameless_props.door_styles[self.selected_index]
        success_count = 0
        skip_count = 0

        for obj in context.scene.objects:
            if 'IS_DOOR_FRONT' in obj or 'IS_DRAWER_FRONT' in obj:
                result = selected_door_style.assign_style_to_front(obj)
                if result == True:
                    success_count += 1
                else:
                    skip_count += 1

        if skip_count > 0:
            self.report({'WARNING'}, f"Updated {success_count} front(s), skipped {skip_count} (too small for style)")
        else:
            self.report({'INFO'}, f"Updated {success_count} front(s) with style '{selected_door_style.name}'")
        return {'FINISHED'}


class hb_frameless_OT_update_cabinet_sizes(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_sizes"
    bl_label = "Update Cabinet Sizes"
    bl_description = "Update all cabinet depths and heights to match the current size settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        # Get props from main scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        updated_count = 0
        
        # Find all cabinets in the current scene
        for obj in context.scene.objects:
            if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
                continue
            
            cabinet_type = obj.get('CABINET_TYPE', '')
            cabinet = hb_types.GeoNodeObject(obj)
            
            # Get the appropriate depth and height based on cabinet type
            if cabinet_type == 'BASE':
                new_depth = props.base_cabinet_depth
                new_height = props.base_cabinet_height
            elif cabinet_type == 'TALL':
                new_depth = props.tall_cabinet_depth
                new_height = props.tall_cabinet_height
            elif cabinet_type == 'UPPER':
                new_depth = props.upper_cabinet_depth
                new_height = props.upper_cabinet_height
            else:
                # Unknown type, skip
                continue
            
            # Update depth (Dim Y) and height (Dim Z)
            try:
                cabinet.set_input('Dim Y', new_depth)
                cabinet.set_input('Dim Z', new_height)
                updated_count += 1
            except Exception as e:
                self.report({'WARNING'}, f"Could not update cabinet {obj.name}: {str(e)}")
        
        if updated_count > 0:
            self.report({'INFO'}, f"Updated {updated_count} cabinet(s)")
        else:
            self.report({'INFO'}, "No cabinets found to update")
        
        return {'FINISHED'}


classes = (
    hb_frameless_OT_update_toe_kick_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_update_cabinet_sizes,
)

register, unregister = bpy.utils.register_classes_factory(classes)
