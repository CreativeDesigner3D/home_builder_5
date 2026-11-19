import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_types, units

class hb_frameless_OT_update_toe_kick_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_toe_kick_prompts"
    bl_label = "Update Toe Kick Prompts"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        # Map enum string to COMBOBOX index
        type_map = {
            'Notch Ends to Floor': 0,
            'Ladder Style': 1,
            'Floating': 2,
            'Leg Levelers': 3,
        }
        new_type_index = type_map.get(frameless_props.default_toe_kick_type, 0)

        # Snapshot first: switching the type adds and removes parts, which
        # must not happen under a live scene.objects iterator.
        for obj in list(context.scene.objects):
            try:
                obj.name
            except ReferenceError:
                continue  # a part of the old type, already taken off
            # A filler, panel or corner standing off the floor (beside an
            # upper) is built with no toe kick: it keeps none.
            no_kick = (not obj.get('IS_FRAMELESS_CABINET_CAGE')
                       and 'Toe Kick Height' in obj
                       and float(obj['Toe Kick Height']) <= 0.0)
            if 'Toe Kick Height' in obj and not no_kick:
                obj['Toe Kick Height'] = frameless_props.default_toe_kick_height
            if 'Toe Kick Setback' in obj and not no_kick:
                obj['Toe Kick Setback'] = frameless_props.default_toe_kick_setback
            if 'Toe Kick Type' in obj:
                # A cabinet trades the old type's parts for the new one's
                # (kick board, ladder base, levelers, the notch in the
                # sides); anything else just carries the number.
                if not (obj.get('IS_FRAMELESS_CABINET_CAGE')
                        and int(obj['Toe Kick Type']) != new_type_index
                        and types_frameless.set_toe_kick_type(
                            obj, new_type_index)):
                    obj['Toe Kick Type'] = new_type_index
            if 'Leg Leveler Inset' in obj:
                obj['Leg Leveler Inset'] = frameless_props.default_leg_leveler_inset
            hb_utils.run_calc_fix(context,obj)              
        return {'FINISHED'}



class hb_frameless_OT_update_material_thickness_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_material_thickness_prompts"
    bl_label = "Update Material Thickness Prompts"
    bl_description = "Update all cabinets in the project with the current material thickness"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        thickness = frameless_props.default_carcass_part_thickness
        updated_count = 0

        for obj in context.scene.objects:
            changed = False
            if 'Material Thickness' in obj:
                obj['Material Thickness'] = thickness
                changed = True
            for key in ('Left Thickness', 'Right Thickness', 'Top Thickness', 'Bottom Thickness'):
                if key in obj:
                    obj[key] = thickness
                    changed = True
            if changed:
                hb_utils.run_calc_fix(context, obj)
                updated_count += 1

        self.report({'INFO'}, f"Updated material thickness on {updated_count} object(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_front_thickness_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_front_thickness_prompts"
    bl_label = "Update Front Thickness Prompts"
    bl_description = "Update every door and drawer front in the project to the current front thickness"

    def execute(self, context):
        thickness = context.scene.hb_frameless.default_front_thickness
        updated_count = 0
        for obj in context.scene.objects:
            if 'Front Thickness' in obj:
                if abs(float(obj['Front Thickness']) - thickness) > 1e-7:
                    obj['Front Thickness'] = thickness
                    hb_utils.run_calc_fix(context, obj)
                    updated_count += 1
        self.report({'INFO'}, f"Updated front thickness on {updated_count} object(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_base_top_construction_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_base_top_construction_prompts"
    bl_label = "Update Base Top Construction Prompts"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        # The cabinet prompt is a combobox: Full Top, Stretchers, Sink.
        index = {'Full Top': 0, 'Stretchers': 1}.get(
            frameless_props.base_top_construction, 1)
        for obj in context.scene.objects:
            # A sink base keeps its sink top whatever the room default.
            if 'Base Top Construction' in obj and not obj.get('IS_SINK_CABINET'):
                obj['Base Top Construction'] = index
                hb_utils.run_calc_fix(context, obj)
        return {'FINISHED'}


def _opening_front_kind(opening_obj):
    """'DRAWER' (a drawer or false front), 'DOOR', 'PULLOUT' or None for
    what closes an opening of a vertical splitter."""
    from .. import solver_frameless
    insert = solver_frameless.opening_front_insert(opening_obj) if opening_obj else None
    if insert is None:
        return None
    for child in insert.children:
        if child.get('IS_PULLOUT_FRONT'):
            return 'PULLOUT'
        if child.get('IS_DRAWER_FRONT'):
            return 'DRAWER'
        if child.get('IS_DOOR_FRONT'):
            return 'DOOR'
    return None


def top_front_splitters(scene, equal_stacks):
    """The outermost vertical splitters of the scene's frameless cabinets
    whose top opening holds a drawer or false front, by the rules new
    cabinets are built with: a drawer over doors or other fronts always,
    an all-drawer stack only with three or more drawers and equal stack
    heights off."""
    from .. import solver_frameless
    tag = solver_frameless.SPLITTER_VERTICAL_TAG
    found = []
    for obj in list(scene.objects):
        if not obj.get(tag):
            continue
        parent = obj.parent
        nested = False
        while parent is not None:
            if parent.get(tag):
                nested = True
                break
            parent = parent.parent
        if nested:
            continue
        calc = solver_frameless.splitter_calculator(obj)
        if calc is None or len(calc.prompts) < 2:
            continue
        parts = solver_frameless.split_parts(obj)
        kinds = [_opening_front_kind(parts.get(('OPENING', i)))
                 for i in range(1, len(calc.prompts) + 1)]
        if kinds[0] != 'DRAWER':
            continue
        if all(k == 'DRAWER' for k in kinds) and (len(kinds) < 3 or equal_stacks):
            continue
        found.append(obj)
    return found


class hb_frameless_OT_update_drawer_front_height_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_drawer_front_height_prompts"
    bl_label = "Update Drawer Front Height Prompts"
    bl_description = ("Give the top drawer and sink false front of every frameless "
                      "cabinet in the room the Top Drawer Front Height; the openings "
                      "below share the rest as before")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from . import ops_opening
        props = context.scene.hb_frameless
        height = props.top_drawer_front_height
        splitters = top_front_splitters(context.scene, props.equal_drawer_stack_heights)
        for splitter_obj in splitters:
            rows = ops_opening.front_height_rows(splitter_obj)
            # The top front takes the option; fronts below keep what is
            # held on them, and the rest share what is left.
            heights = [height] + [h if held else None
                                  for _i, _label, h, held, _f in rows[1:]]
            ops_opening.set_front_heights(context, splitter_obj, heights)
        self.report({'INFO'}, "Set the top front of %d cabinet bay(s) to %s"
                    % (len(splitters), units.unit_to_string(context.scene.unit_settings, height)))
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

        # Sizes are per room -- the tall and upper heights are this
        # room's ceiling height less its clearances, so they have to
        # come from the scene holding the cabinets being updated, not
        # from the main scene (see hb_project.get_settings_scene).
        settings_scene = hb_project.get_settings_scene(context)
        props = settings_scene.hb_frameless

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
                hb_utils.run_calc_fix(context, cabinet.obj)
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
    hb_frameless_OT_update_material_thickness_prompts,
    hb_frameless_OT_update_front_thickness_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_update_cabinet_sizes,
)

register, unregister = bpy.utils.register_classes_factory(classes)
