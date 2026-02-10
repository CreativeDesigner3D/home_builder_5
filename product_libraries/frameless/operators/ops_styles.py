import bpy
import os
from bpy_extras import view3d_utils
from .. import types_frameless
from .. import props_hb_frameless
from ..props_hb_frameless import get_or_create_pull_finish_material
from .... import hb_utils, hb_project, hb_types, units

class hb_frameless_OT_add_door_style(bpy.types.Operator):
    """Add a new door style"""
    bl_idname = "hb_frameless.add_door_style"
    bl_label = "Add Door Style"
    bl_description = "Add a new door style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create new style
        style = props.door_styles.add()
        
        # Generate unique name
        base_name = "Door Style"
        existing_names = [s.name for s in props.door_styles]
        counter = len(props.door_styles)
        while f"{base_name} {counter}" in existing_names:
            counter += 1
        style.name = f"{base_name} {counter}"
        
        # Set as active
        props.active_door_style_index = len(props.door_styles) - 1
        
        self.report({'INFO'}, f"Added door style: {style.name}")
        return {'FINISHED'}


class hb_frameless_OT_remove_door_style(bpy.types.Operator):
    """Remove the selected door style"""
    bl_idname = "hb_frameless.remove_door_style"
    bl_label = "Remove Door Style"
    bl_description = "Remove the selected door style (at least one style must remain)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 1

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if len(props.door_styles) <= 1:
            self.report({'WARNING'}, "Cannot remove the last door style")
            return {'CANCELLED'}
        
        index = props.active_door_style_index
        style_name = props.door_styles[index].name
        
        # Remove the style
        props.door_styles.remove(index)
        
        # Adjust active index
        if props.active_door_style_index >= len(props.door_styles):
            props.active_door_style_index = len(props.door_styles) - 1
        
        # Update any fronts that referenced this style
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                    front_style_index = obj.get('DOOR_STYLE_INDEX', 0)
                    if front_style_index == index:
                        obj['DOOR_STYLE_INDEX'] = 0
                    elif front_style_index > index:
                        obj['DOOR_STYLE_INDEX'] = front_style_index - 1
        
        self.report({'INFO'}, f"Removed door style: {style_name}")
        return {'FINISHED'}


class hb_frameless_OT_duplicate_door_style(bpy.types.Operator):
    """Duplicate the selected door style"""
    bl_idname = "hb_frameless.duplicate_door_style"
    bl_label = "Duplicate Door Style"
    bl_description = "Create a copy of the selected door style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            return {'CANCELLED'}
        
        source = props.door_styles[props.active_door_style_index]
        
        # Create new style
        new_style = props.door_styles.add()
        new_style.name = f"{source.name} Copy"
        
        # Copy all properties
        new_style.door_type = source.door_type
        new_style.panel_material = source.panel_material
        new_style.stile_width = source.stile_width
        new_style.rail_width = source.rail_width
        new_style.add_mid_rail = source.add_mid_rail
        new_style.center_mid_rail = source.center_mid_rail
        new_style.mid_rail_width = source.mid_rail_width
        new_style.mid_rail_location = source.mid_rail_location
        new_style.panel_thickness = source.panel_thickness
        new_style.panel_inset = source.panel_inset
        new_style.edge_profile_type = source.edge_profile_type
        new_style.outside_profile = source.outside_profile
        new_style.inside_profile = source.inside_profile
        
        # Set as active
        props.active_door_style_index = len(props.door_styles) - 1
        
        self.report({'INFO'}, f"Duplicated door style: {new_style.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_door_style_to_selected_fronts(bpy.types.Operator):
    """Paint door style onto fronts - click doors/drawers to assign the active style"""
    bl_idname = "hb_frameless.assign_door_style_to_selected_fronts"
    bl_label = "Paint Door Style"
    bl_description = "Click on door or drawer fronts to assign the active door style. Right-click or ESC to finish"
    bl_options = {'REGISTER', 'UNDO'}

    # Track state
    hovered_front = None
    assigned_count: int = 0
    style_name: str = ""
    style_index: int = 0
    
    # Store original object state for restoration
    original_states = {}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def get_front_under_mouse(self, context, event):
        """Ray cast to find door/drawer front under mouse cursor."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        coord = (event.mouse_region_x, event.mouse_region_y)
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )
        
        if result and obj:
            current = obj
            while current:
                if current.get('IS_DOOR_FRONT') or current.get('IS_DRAWER_FRONT'):
                    return current
                current = current.parent
        
        return None

    def highlight_front(self, obj, highlight=True):
        """Highlight or unhighlight a front by selecting it."""
        if highlight:
            if obj.name not in self.original_states:
                self.original_states[obj.name] = {
                    'selected': obj.select_get(),
                }
            obj.select_set(True)
        else:
            if obj.name in self.original_states:
                state = self.original_states[obj.name]
                obj.select_set(state['selected'])

    def update_header(self, context):
        """Update header text with current status."""
        text = f"Door Style: '{self.style_name}' | LMB: Assign style | RMB/ESC: Finish | Assigned: {self.assigned_count}"
        context.area.header_text_set(text)

    def assign_style_to_front(self, context, front_obj):
        """Assign the active style to a front."""
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        style = props.door_styles[self.style_index]
        
        result = style.assign_style_to_front(front_obj)
        
        if result == True:
            front_obj['DOOR_STYLE_INDEX'] = self.style_index
            return True
        elif isinstance(result, str):
            # Validation error - show message
            self.report({'WARNING'}, result)
            return False
        else:
            return False

    def cleanup(self, context):
        """Clean up modal state."""
        for obj_name in list(self.original_states.keys()):
            obj = bpy.data.objects.get(obj_name)
            if obj:
                self.highlight_front(obj, highlight=False)
        
        self.original_states.clear()
        self.hovered_front = None
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')

    def invoke(self, context, event):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            self.report({'WARNING'}, "No door styles defined")
            return {'CANCELLED'}
        
        self.style_index = props.active_door_style_index
        self.style_name = props.door_styles[self.style_index].name
        self.assigned_count = 0
        self.hovered_front = None
        self.original_states = {}
        
        bpy.ops.object.select_all(action='DESELECT')
        context.window.cursor_set('PAINT_BRUSH')
        self.update_header(context)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.value == 'PRESS':
                self.cleanup(context)
                if self.assigned_count > 0:
                    self.report({'INFO'}, f"Assigned '{self.style_name}' to {self.assigned_count} front(s)")
                else:
                    self.report({'INFO'}, "Style painting cancelled")
                return {'FINISHED'}
        
        if event.type == 'MOUSEMOVE':
            front = self.get_front_under_mouse(context, event)
            
            if self.hovered_front and self.hovered_front != front:
                self.highlight_front(self.hovered_front, highlight=False)
            
            if front and front != self.hovered_front:
                self.highlight_front(front, highlight=True)
            
            self.hovered_front = front
        
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_front:
                if self.assign_style_to_front(context, self.hovered_front):
                    self.assigned_count += 1
                    self.update_header(context)
                return {'RUNNING_MODAL'}
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        if event.type in {'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 
                          'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0'}:
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class hb_frameless_OT_update_fronts_from_style(bpy.types.Operator):
    """Update all fronts that use the active door style"""
    bl_idname = "hb_frameless.update_fronts_from_style"
    bl_label = "Update Fronts from Style"
    bl_description = "Update all door and drawer fronts that use the active door style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            self.report({'WARNING'}, "No door styles defined")
            return {'CANCELLED'}
        
        style_index = props.active_door_style_index
        style = props.door_styles[style_index]
        
        success_count = 0
        skip_count = 0
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                    front_style_index = obj.get('DOOR_STYLE_INDEX', 0)
                    if front_style_index == style_index:
                        result = style.assign_style_to_front(obj)
                        if result == True:
                            success_count += 1
                        else:
                            skip_count += 1
        
        if skip_count > 0:
            self.report({'WARNING'}, f"Updated {success_count} front(s), skipped {skip_count} (too small for style)")
        else:
            self.report({'INFO'}, f"Updated {success_count} front(s) with style '{style.name}'")
        return {'FINISHED'}


class hb_frameless_OT_add_cabinet_style(bpy.types.Operator):
    """Add a new cabinet style"""
    bl_idname = "hb_frameless.add_cabinet_style"
    bl_label = "Add Cabinet Style"
    bl_description = "Add a new cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hb_frameless
        
        # Create new style
        style = props.cabinet_styles.add()
        
        # Generate unique name
        base_name = "Style"
        existing_names = [s.name for s in props.cabinet_styles]
        counter = len(props.cabinet_styles)
        while f"{base_name} {counter}" in existing_names:
            counter += 1
        style.name = f"{base_name} {counter}"
        
        # Set as active
        props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        self.report({'INFO'}, f"Added cabinet style: {style.name}")
        return {'FINISHED'}


class hb_frameless_OT_remove_cabinet_style(bpy.types.Operator):
    """Remove the selected cabinet style"""
    bl_idname = "hb_frameless.remove_cabinet_style"
    bl_label = "Remove Cabinet Style"
    bl_description = "Remove the selected cabinet style (at least one style must remain)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hb_frameless
        # Must have more than 1 style to remove
        return len(props.cabinet_styles) > 1

    def execute(self, context):
        props = context.scene.hb_frameless
        
        if len(props.cabinet_styles) <= 1:
            self.report({'WARNING'}, "Cannot remove the last cabinet style")
            return {'CANCELLED'}
        
        index = props.active_cabinet_style_index
        style_name = props.cabinet_styles[index].name
        
        # Remove the style
        props.cabinet_styles.remove(index)
        
        # Adjust active index
        if props.active_cabinet_style_index >= len(props.cabinet_styles):
            props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        # Update any cabinets that referenced this style
        # (shift indices for cabinets using styles after the removed one)
        for obj in context.scene.objects:
            if obj.get('IS_FRAMELESS_CABINET_CAGE'):
                cab_style_index = obj.get('CABINET_STYLE_INDEX', 0)
                if cab_style_index == index:
                    # Reset to default style
                    obj['CABINET_STYLE_INDEX'] = 0
                elif cab_style_index > index:
                    # Shift index down
                    obj['CABINET_STYLE_INDEX'] = cab_style_index - 1
        
        self.report({'INFO'}, f"Removed cabinet style: {style_name}")
        return {'FINISHED'}


class hb_frameless_OT_duplicate_cabinet_style(bpy.types.Operator):
    """Duplicate the selected cabinet style"""
    bl_idname = "hb_frameless.duplicate_cabinet_style"
    bl_label = "Duplicate Cabinet Style"
    bl_description = "Create a copy of the selected cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def execute(self, context):
        props = context.scene.hb_frameless
        
        if not props.cabinet_styles:
            return {'CANCELLED'}
        
        source = props.cabinet_styles[props.active_cabinet_style_index]
        
        # Create new style
        new_style = props.cabinet_styles.add()
        new_style.name = f"{source.name} Copy"
        
        # Copy all properties
        new_style.wood_species = source.wood_species
        new_style.stain_color = source.stain_color
        new_style.paint_color = source.paint_color
        new_style.door_overlay_type = source.door_overlay_type
        new_style.edge_banding = source.edge_banding
        
        # Set as active
        props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        self.report({'INFO'}, f"Duplicated cabinet style: {new_style.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_cabinet_style_to_selected_cabinets(bpy.types.Operator):
    """Paint cabinet style onto cabinets - click cabinets to assign the active style"""
    bl_idname = "hb_frameless.assign_cabinet_style_to_selected_cabinets"
    bl_label = "Paint Cabinet Style"
    bl_description = "Click on cabinets to assign the active cabinet style. Right-click or ESC to finish"
    bl_options = {'REGISTER', 'UNDO'}

    # Track state
    hovered_cabinet = None
    assigned_count: int = 0
    style_name: str = ""
    style_index: int = 0
    
    # Store original object state for restoration
    original_states = {}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def get_cabinet_under_mouse(self, context, event):
        """Ray cast to find cabinet under mouse cursor."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        # Get mouse coordinates
        coord = (event.mouse_region_x, event.mouse_region_y)
        
        # Get ray from mouse position
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        # Ray cast through scene
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )
        
        if result and obj:
            # Check if hit object or any of its parents is a cabinet cage or product cage
            current = obj
            while current:
                if current.get('IS_FRAMELESS_CABINET_CAGE') or current.get('IS_FRAMELESS_PRODUCT_CAGE'):
                    return current
                current = current.parent
        
        return None

    def highlight_cabinet(self, obj, highlight=True):
        """Highlight or unhighlight a cabinet cage by selecting it."""
        if highlight:
            # Store original state if not already stored
            if obj.name not in self.original_states:
                self.original_states[obj.name] = {
                    'selected': obj.select_get(),
                    'hide_viewport': obj.hide_viewport,
                }
            # Show cage as selected
            obj.hide_viewport = False
            obj.select_set(True)
        else:
            # Restore original state
            if obj.name in self.original_states:
                state = self.original_states[obj.name]
                obj.select_set(state['selected'])
                obj.hide_viewport = state['hide_viewport']

    def update_header(self, context):
        """Update header text with current status."""
        text = f"Cabinet Style: '{self.style_name}' | LMB: Assign style | RMB/ESC: Finish | Assigned: {self.assigned_count}"
        context.area.header_text_set(text)

    def assign_style_to_cabinet(self, context, cabinet_obj):
        """Assign the active style to a cabinet."""
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        style = props.cabinet_styles[self.style_index]
        
        cabinet_obj['CABINET_STYLE_INDEX'] = self.style_index
        cabinet_obj['CABINET_STYLE_NAME'] = style.name
        style.assign_style_to_cabinet(cabinet_obj)
        
        return True

    def cleanup(self, context):
        """Clean up modal state."""
        # Restore all highlighted objects
        for obj_name in list(self.original_states.keys()):
            obj = bpy.data.objects.get(obj_name)
            if obj:
                self.highlight_cabinet(obj, highlight=False)
        
        self.original_states.clear()
        self.hovered_cabinet = None
        
        # Clear header and restore cursor
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')

    def invoke(self, context, event):
        # Get style info for display
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.cabinet_styles:
            self.report({'WARNING'}, "No cabinet styles defined")
            return {'CANCELLED'}
        
        self.style_index = props.active_cabinet_style_index
        self.style_name = props.cabinet_styles[self.style_index].name
        self.assigned_count = 0
        self.hovered_cabinet = None
        self.original_states = {}
        
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Set cursor to paint brush
        context.window.cursor_set('PAINT_BRUSH')
        
        # Set up modal
        self.update_header(context)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # Always update the view
        context.area.tag_redraw()
        
        # Handle cancel
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.value == 'PRESS':
                self.cleanup(context)
                if self.assigned_count > 0:
                    self.report({'INFO'}, f"Assigned '{self.style_name}' to {self.assigned_count} cabinet(s)")
                else:
                    self.report({'INFO'}, "Style painting cancelled")
                return {'FINISHED'}
        
        # Handle mouse move - update hover highlight
        if event.type == 'MOUSEMOVE':
            cabinet = self.get_cabinet_under_mouse(context, event)
            
            # Unhighlight previous
            if self.hovered_cabinet and self.hovered_cabinet != cabinet:
                self.highlight_cabinet(self.hovered_cabinet, highlight=False)
            
            # Highlight new
            if cabinet and cabinet != self.hovered_cabinet:
                self.highlight_cabinet(cabinet, highlight=True)
            
            self.hovered_cabinet = cabinet
        
        # Handle click - assign style
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_cabinet:
                if self.assign_style_to_cabinet(context, self.hovered_cabinet):
                    self.assigned_count += 1
                    self.update_header(context)
                return {'RUNNING_MODAL'}
        
        # Pass through navigation events
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        # Pass through view manipulation
        if event.type in {'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 
                          'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0'}:
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class hb_frameless_OT_assign_cabinet_style(bpy.types.Operator):
    """Assign the active cabinet style to a cabinet"""
    bl_idname = "hb_frameless.assign_cabinet_style"
    bl_label = "Assign Style to Cabinet"
    bl_description = "Assign the active cabinet style to a cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        style_index = props.active_cabinet_style_index
        style = props.cabinet_styles[style_index]
        
        cabinet_obj = bpy.data.objects.get(self.cabinet_name)
        if cabinet_obj:
            cabinet_obj['CABINET_STYLE_INDEX'] = style_index
            cabinet_obj['CABINET_STYLE_NAME'] = style.name  # Store name for reference
            style.assign_style_to_cabinet(cabinet_obj)
        
        return {'FINISHED'}


class hb_frameless_OT_update_cabinets_from_style(bpy.types.Operator):
    """Update all cabinets in the scene that use the active cabinet style"""
    bl_idname = "hb_frameless.update_cabinets_from_style"
    bl_label = "Update Cabinets from Style"
    bl_description = "Update all cabinets in the scene that use the active cabinet style with current style settings"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _cabinets = []
    _current_index = 0
    _total_count = 0
    _style = None
    _style_name = ""

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def modal(self, context, event):
        wm = context.window_manager
        
        if event.type == 'ESC':
            self.finish(context)
            self.report({'WARNING'}, f"Cancelled. Updated {self._current_index} of {self._total_count} cabinets.")
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self._current_index < self._total_count:
                # Process one cabinet
                obj = self._cabinets[self._current_index]
                if obj and self._style:
                    self._style.assign_style_to_cabinet(obj)
                    hb_utils.run_calc_fix(context, obj)
                    obj['CABINET_STYLE_NAME'] = self._style_name
                
                self._current_index += 1
                
                # Update progress bar (keep below 1.0 to show progress bar)
                wm.home_builder.progress = min(0.99, self._current_index / self._total_count)
                
                # Force redraw to update progress bar
                for area in context.screen.areas:
                    area.tag_redraw()
            else:
                # Finished
                self.finish(context)
                self.report({'INFO'}, f"Updated {self._total_count} cabinet(s) with style '{self._style_name}'")
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def finish(self, context):
        wm = context.window_manager
        
        # Remove timer
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        # Reset progress to 1.0 (hides progress bar)
        wm.home_builder.progress = 1.0
        
        # Force immediate UI redraw
        for window in wm.windows:
            for area in window.screen.areas:
                area.tag_redraw()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        # Clear class variables
        self._cabinets = []
        self._current_index = 0
        self._total_count = 0
        self._style = None

    def invoke(self, context, event):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        wm = context.window_manager
        
        if not props.cabinet_styles:
            self.report({'WARNING'}, "No cabinet styles defined")
            return {'CANCELLED'}
        
        style_index = props.active_cabinet_style_index
        self._style = props.cabinet_styles[style_index]
        self._style_name = self._style.name
        
        # Collect all cabinets that need updating
        self._cabinets = []
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_FRAMELESS_CABINET_CAGE'):
                    cab_style_index = obj.get('CABINET_STYLE_INDEX', 0)
                    if cab_style_index == style_index:
                        self._cabinets.append(obj)
        
        self._total_count = len(self._cabinets)
        self._current_index = 0
        
        if self._total_count == 0:
            self.report({'INFO'}, f"No cabinets found using style '{self._style_name}'")
            return {'CANCELLED'}
        
        # Set initial progress to 0
        wm.home_builder.progress = 0.0
        
        # Add timer for modal operation
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Fallback for non-invoke calls
        return self.invoke(context, None)



# =============================================================================
# CROWN DETAIL OPERATORS
# =============================================================================


class hb_frameless_OT_update_cabinet_pulls(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_pulls"
    bl_label = "Update Cabinet Pulls"
    bl_description = "Update pulls on all cabinets to match current selection"
    bl_options = {'UNDO'}
    
    pull_type: bpy.props.EnumProperty(
        name="Pull Type",
        items=[
            ('DOOR', "Door Pulls", "Update door pulls"),
            ('DRAWER', "Drawer Pulls", "Update drawer pulls"),
            ('ALL', "All Pulls", "Update all pulls"),
        ],
        default='ALL'
    )# type: ignore

    def _get_pull_obj(self, props, pull_type):
        """Get pull object based on current selection. Returns (pull_obj, is_none).
        is_none=True means pulls should be cleared."""
        if pull_type == 'drawer':
            selection = props.drawer_pull_selection
        else:
            selection = props.door_pull_selection
        
        if selection == 'NONE':
            return None, True
        
        if selection == 'CUSTOM':
            if pull_type == 'drawer':
                return props.current_drawer_front_pull_object, False
            else:
                return props.current_door_pull_object, False
        
        # Bundled pull - load from file
        pull_obj = props_hb_frameless.load_pull_object(selection)
        if pull_obj:
            if pull_type == 'drawer':
                props.current_drawer_front_pull_object = pull_obj
            else:
                props.current_door_pull_object = pull_obj
        return pull_obj, False

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        door_pull_obj, door_is_none = None, False
        drawer_pull_obj, drawer_is_none = None, False
        
        if self.pull_type in ('DOOR', 'ALL'):
            door_pull_obj, door_is_none = self._get_pull_obj(props, 'door')
        if self.pull_type in ('DRAWER', 'ALL'):
            drawer_pull_obj, drawer_is_none = self._get_pull_obj(props, 'drawer')
        
        updated_count = 0
        cleared_count = 0
        updated_objs = []
        
        for obj in context.scene.objects:
            if not obj.get('IS_CABINET_PULL'):
                continue
            
            parent = obj.parent
            if not parent:
                continue
            
            try:
                pull_hw = hb_types.GeoNodeHardware(obj)
                
                if parent.get('IS_DOOR_FRONT') and self.pull_type in ('DOOR', 'ALL'):
                    if door_is_none:
                        pull_hw.set_input("Object", None)
                        cleared_count += 1
                    elif door_pull_obj:
                        pull_hw.set_input("Object", door_pull_obj)
                        parent['Pull Length'] = door_pull_obj.dimensions.x
                        updated_count += 1
                    updated_objs.append(obj)
                    updated_objs.append(parent)
                
                elif parent.get('IS_DRAWER_FRONT') and self.pull_type in ('DRAWER', 'ALL'):
                    if drawer_is_none:
                        pull_hw.set_input("Object", None)
                        cleared_count += 1
                    elif drawer_pull_obj:
                        pull_hw.set_input("Object", drawer_pull_obj)
                        parent['Pull Length'] = drawer_pull_obj.dimensions.x
                        updated_count += 1
                    updated_objs.append(obj)
                    updated_objs.append(parent)
            except:
                pass

        # Force driver recalculation
        for obj in updated_objs:
            obj.update_tag()

        hb_utils.run_calc_fix(context)

        if cleared_count:
            self.report({'INFO'}, f"Cleared {cleared_count} pull(s)")
        else:
            self.report({'INFO'}, f"Updated {updated_count} pull(s)")
        return {'FINISHED'}



class hb_frameless_OT_update_pull_locations(bpy.types.Operator):
    bl_idname = "hb_frameless.update_pull_locations"
    bl_label = "Update Pull Locations"
    bl_description = "Update pull locations on all fronts to match current global settings"
    bl_options = {'UNDO'}
    
    update_type: bpy.props.EnumProperty(
        name="Update Type",
        items=[
            ('DOOR', "Door Fronts", "Update door pull locations"),
            ('DRAWER', "Drawer Fronts", "Update drawer pull locations"),
            ('ALL', "All Fronts", "Update all pull locations"),
        ],
        default='ALL'
    )# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        door_count = 0
        drawer_count = 0
        updated_fronts = []
        
        # Only update objects in the current scene
        for obj in context.scene.objects:
            # Update door fronts
            if obj.get('IS_DOOR_FRONT') and self.update_type in ('DOOR', 'ALL'):
                try:
                    # Update properties using obj['Prop Name'] syntax
                    obj['Handle Horizontal Location'] = props.pull_dim_from_edge
                    obj['Base Pull Vertical Location'] = props.pull_vertical_location_base
                    obj['Tall Pull Vertical Location'] = props.pull_vertical_location_tall
                    obj['Upper Pull Vertical Location'] = props.pull_vertical_location_upper
                    updated_fronts.append(obj)
                    door_count += 1
                except Exception as e:
                    print(f"Error updating door front {obj.name}: {e}")
            
            # Update drawer fronts
            elif obj.get('IS_DRAWER_FRONT') and self.update_type in ('DRAWER', 'ALL'):
                try:
                    obj['Center Pull'] = 1 if props.center_pulls_on_drawer_front else 0
                    obj['Handle Horizontal Location'] = props.pull_vertical_location_drawers
                    updated_fronts.append(obj)
                    drawer_count += 1
                except Exception as e:
                    print(f"Error updating drawer front {obj.name}: {e}")
        
        # Force driver recalculation (workaround for Blender bug #133392)
        # Touch location on all pull objects to mark transforms dirty
        for obj in updated_fronts:
            hb_utils.run_calc_fix(context,obj)
        
        # Report results
        if self.update_type == 'DOOR':
            self.report({'INFO'}, f"Updated {door_count} door front(s)")
        elif self.update_type == 'DRAWER':
            self.report({'INFO'}, f"Updated {drawer_count} drawer front(s)")
        else:
            self.report({'INFO'}, f"Updated {door_count} door(s) and {drawer_count} drawer(s)")
        
        return {'FINISHED'}


class hb_frameless_OT_update_pull_finish(bpy.types.Operator):
    """Update finish on all cabinet pulls"""
    bl_idname = "hb_frameless.update_pull_finish"
    bl_label = "Update Pull Finish"
    bl_description = "Apply the selected finish to all cabinet pulls"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Get or create the finish material
        finish_mat = get_or_create_pull_finish_material(props.pull_finish)
        if not finish_mat:
            self.report({'ERROR'}, "Could not create finish material")
            return {'CANCELLED'}
        
        pull_count = 0
        updated_sources = set()
        
        # Find all pull objects and their source objects
        for obj in context.scene.objects:
            # Check for door/drawer fronts and get their pull children
            if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                for child in obj.children:
                    if 'Pull' in child.name:
                        # Find the geometry node modifier
                        for mod in child.modifiers:
                            if mod.type == 'NODES' and mod.node_group:
                                # Get the source object from the modifier
                                for key in mod.keys():
                                    val = mod[key]
                                    if hasattr(val, 'material_slots'):
                                        # This is the source pull object
                                        source_obj = val
                                        if source_obj.name not in updated_sources:
                                            # Apply material to source object
                                            if len(source_obj.material_slots) == 0:
                                                source_obj.data.materials.append(finish_mat)
                                            else:
                                                source_obj.material_slots[0].material = finish_mat
                                            updated_sources.add(source_obj.name)
                        pull_count += 1
        
        # Force viewport update
        context.view_layer.update()
        
        self.report({'INFO'}, f"Applied finish to {len(updated_sources)} pull type(s) ({pull_count} total pulls)")
        return {'FINISHED'}




# ============================================
# FINISH COLOR OPERATORS
# ============================================

class hb_frameless_OT_add_custom_finish_color(bpy.types.Operator):
    """Add a new custom finish color"""
    bl_idname = "hb_frameless.add_custom_finish_color"
    bl_label = "Add Custom Finish Color"
    bl_description = "Create a new custom color and save it to your user library"
    bl_options = {'REGISTER', 'UNDO'}
    
    color_name: bpy.props.StringProperty(name="Color Name", default="My Custom Color")  # type: ignore
    color_1: bpy.props.FloatVectorProperty(
        name="Color 1", subtype='COLOR', size=4, min=0, max=1,
        default=(0.5, 0.4, 0.3, 1.0)
    )  # type: ignore
    color_2: bpy.props.FloatVectorProperty(
        name="Color 2", subtype='COLOR', size=4, min=0, max=1,
        default=(0.4, 0.3, 0.2, 1.0)
    )  # type: ignore
    roughness: bpy.props.FloatProperty(name="Roughness", min=0, max=1, default=1.0)  # type: ignore
    noise_bump_strength: bpy.props.FloatProperty(name="Noise Bump Strength", min=0, max=1, default=0.1)  # type: ignore
    knots_bump_strength: bpy.props.FloatProperty(name="Knots Bump Strength", min=0, max=1, default=0.15)  # type: ignore
    wood_bump_strength: bpy.props.FloatProperty(name="Wood Bump Strength", min=0, max=1, default=0.2)  # type: ignore
    
    def invoke(self, context, event):
        from .. import finish_colors
        
        # Pre-fill from current selection
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[props.active_cabinet_style_index]
            color_type = 'paint' if style.wood_species == 'PAINT_GRADE' else 'stain'
            color_name = style.paint_color if style.wood_species == 'PAINT_GRADE' else style.stain_color
            data = finish_colors.get_color_data(color_name, color_type)
            self.color_1 = data.get('color_1', [0.5, 0.4, 0.3, 1.0])
            self.color_2 = data.get('color_2', [0.4, 0.3, 0.2, 1.0])
            self.roughness = data.get('roughness', 1.0)
            self.noise_bump_strength = data.get('noise_bump_strength', 0.1)
            self.knots_bump_strength = data.get('knots_bump_strength', 0.15)
            self.wood_bump_strength = data.get('wood_bump_strength', 0.2)
        
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "color_name")
        
        row = layout.row()
        col = row.column()
        col.label(text="Primary Color:")
        col.prop(self, "color_1", text="")
        col = row.column()
        col.label(text="Secondary Color:")
        col.prop(self, "color_2", text="")
        
        layout.separator()
        layout.label(text="Shader Parameters:")
        layout.prop(self, "roughness")
        layout.prop(self, "noise_bump_strength")
        layout.prop(self, "knots_bump_strength")
        layout.prop(self, "wood_bump_strength")
    
    def execute(self, context):
        from .. import finish_colors
        
        if not self.color_name.strip():
            self.report({'WARNING'}, "Color name cannot be empty")
            return {'CANCELLED'}
        
        # Determine which type based on active style
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        color_type = 'stain'
        if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[props.active_cabinet_style_index]
            if style.wood_species == 'PAINT_GRADE':
                color_type = 'paint'
        
        color_data = {
            'color_1': list(self.color_1),
            'color_2': list(self.color_2),
            'roughness': self.roughness,
            'noise_bump_strength': self.noise_bump_strength,
            'knots_bump_strength': self.knots_bump_strength,
            'wood_bump_strength': self.wood_bump_strength,
        }
        
        if finish_colors.save_custom_color(self.color_name, color_data, color_type):
            # Set the active style to use the new color
            if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
                style = props.cabinet_styles[props.active_cabinet_style_index]
                if color_type == 'paint':
                    style.paint_color = self.color_name
                else:
                    style.stain_color = self.color_name
            
            self.report({'INFO'}, f"Saved custom {color_type} color: {self.color_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save custom color")
            return {'CANCELLED'}


class hb_frameless_OT_delete_custom_finish_color(bpy.types.Operator):
    """Delete a custom finish color from the user library"""
    bl_idname = "hb_frameless.delete_custom_finish_color"
    bl_label = "Delete Custom Color"
    bl_description = "Delete this custom color from your user library"
    bl_options = {'REGISTER', 'UNDO'}
    
    color_name: bpy.props.StringProperty(name="Color Name")  # type: ignore
    color_type: bpy.props.StringProperty(name="Color Type", default='stain')  # type: ignore
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        from .. import finish_colors
        
        if finish_colors.delete_custom_color(self.color_name, self.color_type):
            self.report({'INFO'}, f"Deleted custom color: {self.color_name}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Cannot delete built-in color: {self.color_name}")
            return {'CANCELLED'}


class hb_frameless_OT_edit_finish_color(bpy.types.Operator):
    """Edit the shader parameters for the current finish color"""
    bl_idname = "hb_frameless.edit_finish_color"
    bl_label = "Edit Finish Color"
    bl_description = "Edit the color and shader parameters, then save as a new custom color"
    bl_options = {'REGISTER', 'UNDO'}
    
    color_type: bpy.props.StringProperty(name="Color Type", default='stain')  # type: ignore
    
    color_name: bpy.props.StringProperty(name="Color Name", default="")  # type: ignore
    color_1: bpy.props.FloatVectorProperty(
        name="Primary Color", subtype='COLOR', size=4, min=0, max=1,
        default=(0.5, 0.4, 0.3, 1.0)
    )  # type: ignore
    color_2: bpy.props.FloatVectorProperty(
        name="Secondary Color", subtype='COLOR', size=4, min=0, max=1,
        default=(0.4, 0.3, 0.2, 1.0)
    )  # type: ignore
    roughness: bpy.props.FloatProperty(name="Roughness", min=0, max=1, default=1.0)  # type: ignore
    noise_bump_strength: bpy.props.FloatProperty(name="Noise Bump Strength", min=0, max=1, default=0.1)  # type: ignore
    knots_bump_strength: bpy.props.FloatProperty(name="Knots Bump Strength", min=0, max=1, default=0.15)  # type: ignore
    wood_bump_strength: bpy.props.FloatProperty(name="Wood Bump Strength", min=0, max=1, default=0.2)  # type: ignore
    
    def invoke(self, context, event):
        from .. import finish_colors
        
        # Pre-fill from current selection
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[props.active_cabinet_style_index]
            color_name = style.paint_color if self.color_type == 'paint' else style.stain_color
            data = finish_colors.get_color_data(color_name, self.color_type)
            
            self.color_name = color_name
            self.color_1 = data.get('color_1', [0.5, 0.4, 0.3, 1.0])
            self.color_2 = data.get('color_2', [0.4, 0.3, 0.2, 1.0])
            self.roughness = data.get('roughness', 1.0)
            self.noise_bump_strength = data.get('noise_bump_strength', 0.1)
            self.knots_bump_strength = data.get('knots_bump_strength', 0.15)
            self.wood_bump_strength = data.get('wood_bump_strength', 0.2)
        
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        from .. import finish_colors
        layout = self.layout
        
        is_custom = finish_colors.is_custom_color(self.color_name, self.color_type)
        is_default = not is_custom and self.color_name in (
            finish_colors.DEFAULT_STAIN_COLORS if self.color_type == 'stain' 
            else finish_colors.DEFAULT_PAINT_COLORS
        )
        
        if is_default:
            layout.label(text="Editing a built-in color will save as a custom override", icon='INFO')
        
        layout.prop(self, "color_name")
        
        row = layout.row()
        col = row.column()
        col.label(text="Primary Color:")
        col.prop(self, "color_1", text="")
        col = row.column()
        col.label(text="Secondary Color:")
        col.prop(self, "color_2", text="")
        
        layout.separator()
        layout.label(text="Shader Parameters:")
        layout.prop(self, "roughness")
        layout.prop(self, "noise_bump_strength")
        layout.prop(self, "knots_bump_strength")
        layout.prop(self, "wood_bump_strength")
    
    def execute(self, context):
        from .. import finish_colors
        
        if not self.color_name.strip():
            self.report({'WARNING'}, "Color name cannot be empty")
            return {'CANCELLED'}
        
        color_data = {
            'color_1': list(self.color_1),
            'color_2': list(self.color_2),
            'roughness': self.roughness,
            'noise_bump_strength': self.noise_bump_strength,
            'knots_bump_strength': self.knots_bump_strength,
            'wood_bump_strength': self.wood_bump_strength,
        }
        
        if finish_colors.save_custom_color(self.color_name, color_data, self.color_type):
            # Update active style to use this color
            main_scene = hb_project.get_main_scene()
            props = main_scene.hb_frameless
            if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
                style = props.cabinet_styles[props.active_cabinet_style_index]
                if self.color_type == 'paint':
                    style.paint_color = self.color_name
                else:
                    style.stain_color = self.color_name
            
            self.report({'INFO'}, f"Saved color: {self.color_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save color")
            return {'CANCELLED'}


classes = (
    hb_frameless_OT_add_door_style,
    hb_frameless_OT_remove_door_style,
    hb_frameless_OT_duplicate_door_style,
    hb_frameless_OT_assign_door_style_to_selected_fronts,
    hb_frameless_OT_update_fronts_from_style,
    hb_frameless_OT_add_cabinet_style,
    hb_frameless_OT_remove_cabinet_style,
    hb_frameless_OT_duplicate_cabinet_style,
    hb_frameless_OT_assign_cabinet_style_to_selected_cabinets,
    hb_frameless_OT_assign_cabinet_style,
    hb_frameless_OT_update_cabinets_from_style,
    hb_frameless_OT_update_cabinet_pulls,
    hb_frameless_OT_update_pull_locations,
    hb_frameless_OT_update_pull_finish,
    hb_frameless_OT_add_custom_finish_color,
    hb_frameless_OT_delete_custom_finish_color,
    hb_frameless_OT_edit_finish_color,
)

register, unregister = bpy.utils.register_classes_factory(classes)
