import bpy
from ... import hb_utils

class HOME_BUILDER_MT_applied_ends(bpy.types.Menu):
    bl_label = "Applied Ends"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Slab Panels:")
        layout.operator("hb_frameless.add_applied_end", text="Add Left Slab").side = 'LEFT'
        layout.operator("hb_frameless.add_applied_end", text="Add Right Slab").side = 'RIGHT'
        layout.operator("hb_frameless.add_applied_end", text="Add Back Slab").side = 'BACK'
        layout.operator("hb_frameless.add_applied_end", text="Add Both Sides Slab").side = 'BOTH'
        layout.separator()
        layout.label(text="5-Piece Panels:")
        op = layout.operator("hb_frameless.update_finished_end", text="Left 5-Piece...")
        op.side = 'LEFT'
        op.finished_end_type = '5PIECE'
        op = layout.operator("hb_frameless.update_finished_end", text="Right 5-Piece...")
        op.side = 'RIGHT'
        op.finished_end_type = '5PIECE'
        op = layout.operator("hb_frameless.update_finished_end", text="Back 5-Piece...")
        op.side = 'BACK'
        op.finished_end_type = '5PIECE'
        layout.separator()
        layout.label(text="Remove:")
        layout.operator("hb_frameless.remove_applied_end", text="Remove Left").side = 'LEFT'
        layout.operator("hb_frameless.remove_applied_end", text="Remove Right").side = 'RIGHT'
        layout.operator("hb_frameless.remove_applied_end", text="Remove Back").side = 'BACK'
        layout.operator("hb_frameless.remove_applied_end", text="Remove Both Sides").side = 'BOTH'


class HOME_BUILDER_MT_applied_end_commands(bpy.types.Menu):
    bl_label = "Applied End Commands"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj and obj.get('IS_APPLIED_PANEL_5PIECE'):
            layout.operator("hb_frameless.applied_panel_prompts", text="Panel Prompts")
            layout.separator()
        
        layout.operator("hb_frameless.update_finished_end", text="Change Finished End Type")
        layout.separator()
        layout.operator("hb_frameless.remove_applied_end", text="Remove Applied End")


class HOME_BUILDER_MT_cabinet_commands(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.cabinet_prompts", text="Cabinet Prompts")
        layout.operator("hb_frameless.adjust_multiple_cabinet_widths", text="Adjust Cabinet Sizes")
        layout.separator()
        layout.operator("hb_frameless.drop_cabinet_to_countertop", text="Drop to Countertop")
        layout.operator("hb_frameless.drop_cabinet_height", text="Drop Height")
        layout.operator("hb_frameless.raise_cabinet_bottom", text="Raise Bottom")
        layout.separator()
        layout.menu("HOME_BUILDER_MT_applied_ends", text="Applied Ends")
        layout.operator("hb_frameless.finish_interior", text="Finish Interior")
        
        # Show "Create Cabinet Group" if multiple cabinets are selected
        selected_cabinets = set()
        for obj in context.selected_objects:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp:
                selected_cabinets.add(cabinet_bp)
        
        if len(selected_cabinets) > 1:
            layout.separator()
            layout.operator("hb_frameless.create_cabinet_group", text="Create Cabinet Group")
        
        layout.separator()
        layout.operator("hb_frameless.delete_cabinet", text="Delete Cabinet")


class HOME_BUILDER_MT_bay_commands(bpy.types.Menu):
    bl_label = "Bay Commands"

    def draw(self, context):
        layout = self.layout
        layout.menu("HOME_BUILDER_MT_bay_change_configuration", text="Change Configuration")
        layout.operator("hb_frameless.custom_vertical_splitter", text="Custom Vertical Openings")
        layout.operator("hb_frameless.custom_horizontal_splitter", text="Custom Horizontal Openings")
        layout.separator()
        layout.operator("hb_frameless.edit_splitter_openings", text="Edit Opening Sizes")


class HOME_BUILDER_MT_bay_change_configuration(bpy.types.Menu):
    bl_label = "Change Bay Configuration"

    def draw(self, context):
        from ... import hb_utils
        
        layout = self.layout
        
        # Detect cabinet type from selected object
        cabinet_type = 'BASE'  # Default
        obj = context.object
        if obj:
            bay_bp = obj if 'IS_FRAMELESS_BAY_CAGE' in obj else hb_utils.get_bay_bp(obj)
            if bay_bp:
                cabinet_bp = hb_utils.get_cabinet_bp(bay_bp)
                if cabinet_bp:
                    cabinet_type = cabinet_bp.get('CABINET_TYPE', 'BASE')
        
        if cabinet_type == 'BASE':
            self.draw_base_options(layout)
        elif cabinet_type == 'UPPER':
            self.draw_upper_options(layout)
        elif cabinet_type == 'TALL':
            self.draw_tall_options(layout)
        else:
            self.draw_base_options(layout)  # Fallback
        
        layout.separator()
        layout.operator("hb_frameless.custom_vertical_splitter", text="Custom Vertical...")
        layout.operator("hb_frameless.custom_horizontal_splitter", text="Custom Horizontal...")
    
    def draw_base_options(self, layout):
        """Draw options for base cabinets."""
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Door").opening_type = 'LEFT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Door").opening_type = 'RIGHT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Doors").opening_type = 'DOUBLE_DOORS'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="1 Drawer 1 Door").opening_type = 'DOOR_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="1 Drawer 2 Door").opening_type = '1_DRAWER_2_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="2 Drawer 2 Door").opening_type = '2_DRAWER_2_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="4 Drawers").opening_type = '4_DRAWER_STACK'
        layout.operator("hb_frameless.change_bay_opening", text="3 Drawers").opening_type = '3_DRAWER_STACK'
        layout.operator("hb_frameless.change_bay_opening", text="2 Drawers").opening_type = '2_DRAWER_STACK'
        layout.operator("hb_frameless.change_bay_opening", text="1 Drawer").opening_type = 'SINGLE_DRAWER'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="False Front").opening_type = 'FALSE_FRONT'
        layout.operator("hb_frameless.change_bay_opening", text="Pullout").opening_type = 'PULLOUT'
        layout.operator("hb_frameless.change_bay_opening", text="Pullout with Drawer").opening_type = 'PULLOUT_WITH_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="Microwave with Drawer").opening_type = 'MICROWAVE_DRAWER'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Open with Shelves").opening_type = 'OPEN_WITH_SHELVES'
        layout.operator("hb_frameless.change_bay_opening", text="Open").opening_type = 'OPEN'
    
    def draw_upper_options(self, layout):
        """Draw options for upper cabinets."""
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Door").opening_type = 'LEFT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Door").opening_type = 'RIGHT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Doors").opening_type = 'DOUBLE_DOORS'
        layout.operator("hb_frameless.change_bay_opening", text="Lift Up Door").opening_type = 'FLIP_UP_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Stacked Door").opening_type = 'LEFT_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Stacked Door").opening_type = 'RIGHT_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Stacked Door").opening_type = 'DOUBLE_STACKED_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Doors with 1 Drawer").opening_type = 'DOORS_WITH_1_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="Doors with 2 Drawers").opening_type = 'DOORS_WITH_2_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="Doors with 3 Drawers").opening_type = 'DOORS_WITH_3_DRAWER'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Doors with Pullout").opening_type = 'DOORS_WITH_PULLOUT'
        layout.operator("hb_frameless.change_bay_opening", text="Pullout").opening_type = 'PULLOUT'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="False Front").opening_type = 'FALSE_FRONT'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Open with Shelves").opening_type = 'OPEN_WITH_SHELVES'
        layout.operator("hb_frameless.change_bay_opening", text="Open").opening_type = 'OPEN'
    
    def draw_tall_options(self, layout):
        """Draw options for tall cabinets."""
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Door").opening_type = 'LEFT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Door").opening_type = 'RIGHT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Doors").opening_type = 'DOUBLE_DOORS'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Stacked Door").opening_type = 'LEFT_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Stacked Door").opening_type = 'RIGHT_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Stacked Door").opening_type = 'DOUBLE_STACKED_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing 3 Stacked Door").opening_type = 'LEFT_3_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing 3 Stacked Door").opening_type = 'RIGHT_3_STACKED_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double 3 Stacked Door").opening_type = 'DOUBLE_3_STACKED_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Built In Appliance").opening_type = 'APPLIANCE'
        layout.operator("hb_frameless.change_bay_opening", text="Built In Double Appliance").opening_type = 'DOUBLE_APPLIANCE'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Doors with Tall Pullout").opening_type = 'DOORS_WITH_TALL_PULLOUT'
        layout.operator("hb_frameless.change_bay_opening", text="Tall Pullout").opening_type = 'TALL_PULLOUT'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Open with Shelves").opening_type = 'OPEN_WITH_SHELVES'
        layout.operator("hb_frameless.change_bay_opening", text="Open").opening_type = 'OPEN'


class HOME_BUILDER_MT_opening_commands(bpy.types.Menu):
    bl_label = "Opening Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.opening_prompts", text="Opening Prompts")
        layout.separator()
        layout.menu("HOME_BUILDER_MT_opening_change", text="Change Opening")
        layout.separator()
        layout.operator("hb_frameless.edit_splitter_openings", text="Edit Opening Sizes")


class HOME_BUILDER_MT_opening_change(bpy.types.Menu):
    bl_label = "Change Opening"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.change_opening_type", text="Left Door").opening_type = 'LEFT_DOOR'
        layout.operator("hb_frameless.change_opening_type", text="Right Door").opening_type = 'RIGHT_DOOR'
        layout.operator("hb_frameless.change_opening_type", text="Double Doors").opening_type = 'DOUBLE_DOORS'
        layout.operator("hb_frameless.change_opening_type", text="Flip Up Door").opening_type = 'FLIP_UP_DOOR'
        layout.separator()
        layout.operator("hb_frameless.change_opening_type", text="Drawer").opening_type = 'SINGLE_DRAWER'
        layout.operator("hb_frameless.change_opening_type", text="Pullout").opening_type = 'PULLOUT'
        layout.operator("hb_frameless.change_opening_type", text="False Front").opening_type = 'FALSE_FRONT'
        layout.separator()
        layout.operator("hb_frameless.change_opening_type", text="Open (No Front)").opening_type = 'OPEN'
        layout.operator("hb_frameless.change_opening_type", text="Open with Shelves").opening_type = 'OPEN_WITH_SHELVES'
        layout.separator()
        layout.operator("hb_frameless.custom_vertical_splitter", text="Custom Vertical...")
        layout.operator("hb_frameless.custom_horizontal_splitter", text="Custom Horizontal...")


class HOME_BUILDER_MT_door_front_commands(bpy.types.Menu):
    bl_label = "Door/Drawer Front Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.door_front_prompts", text="Front Prompts")
        layout.separator()
        layout.operator("hb_frameless.assign_door_style_to_selected_fronts", text="Assign Door Style")
        layout.separator()
        layout.operator("hb_frameless.delete_front", text="Delete Front")


class HOME_BUILDER_MT_interior_commands(bpy.types.Menu):
    bl_label = "Interior Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.interior_prompts", text="Interior Prompts")
        layout.separator()
        layout.menu("HOME_BUILDER_MT_interior_change", text="Change Interior")


class HOME_BUILDER_MT_interior_change(bpy.types.Menu):
    bl_label = "Change Interior"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.change_interior_type", text="Shelves").interior_type = 'SHELVES'
        layout.operator("hb_frameless.change_interior_type", text="Empty (No Interior)").interior_type = 'EMPTY'
        layout.separator()
        layout.operator("hb_frameless.custom_interior_vertical", text="Custom Vertical Division...")
        layout.operator("hb_frameless.custom_interior_horizontal", text="Custom Horizontal Division...")


class HOME_BUILDER_MT_interior_part_commands(bpy.types.Menu):
    bl_label = "Interior Part Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.interior_part_prompts", text="Part Prompts")
        layout.separator()
        layout.operator("hb_frameless.interior_prompts", text="Edit Interior...")
        layout.menu("HOME_BUILDER_MT_interior_change", text="Change Interior Configuration")
        layout.separator()
        layout.operator("hb_frameless.delete_interior_part", text="Delete Part")


class HOME_BUILDER_MT_floating_shelf_commands(bpy.types.Menu):
    bl_label = "Floating Shelf Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Floating Shelf Prompts")
        layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Floating Shelf")


class HOME_BUILDER_MT_valance_commands(bpy.types.Menu):
    bl_label = "Valance Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Valance Prompts")
        layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Valance")


class HOME_BUILDER_MT_support_frame_commands(bpy.types.Menu):
    bl_label = "Support Frame Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Support Frame Prompts")
        layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Support Frame")


class HOME_BUILDER_MT_half_wall_commands(bpy.types.Menu):
    bl_label = "Half Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Half Wall Prompts")
        layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Half Wall")


class HOME_BUILDER_MT_leg_commands(bpy.types.Menu):
    bl_label = "Leg Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Leg Prompts")
        layout.separator()
        layout.menu("HOME_BUILDER_MT_applied_ends", text="Applied Ends")
        layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Leg")


class HOME_BUILDER_MT_part_commands(bpy.types.Menu):
    bl_label = "Part Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.product_prompts", text="Part Prompts")
        layout.separator()
        # Hide Applied Ends for misc parts (they have no cage with openings)
        obj = context.object
        is_misc = False
        if obj:
            current = obj
            while current:
                if current.get('IS_FRAMELESS_MISC_PART'):
                    is_misc = True
                    break
                current = current.parent
        if not is_misc:
            layout.menu("HOME_BUILDER_MT_applied_ends", text="Applied Ends")
            layout.separator()
        if is_misc:
            layout.operator("hb_frameless.convert_to_door_panel", text="Convert to Door Panel")
            layout.separator()
        layout.operator("hb_frameless.delete_product", text="Delete Part")


class HOME_BUILDER_MT_appliance_commands(bpy.types.Menu):
    bl_label = "Appliance Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.appliance_prompts", text="Appliance Prompts")
        layout.separator()
        layout.operator("hb_frameless.toggle_panel_ready", text="Toggle Panel Ready")
        layout.operator("hb_frameless.add_appliance_door_panel", text="Add Appliance Door Panel")
        layout.separator()
        layout.operator("hb_frameless.delete_appliance", text="Delete Appliance")


classes = (
    HOME_BUILDER_MT_applied_ends,
    HOME_BUILDER_MT_cabinet_commands,
    HOME_BUILDER_MT_bay_commands,
    HOME_BUILDER_MT_bay_change_configuration,
    HOME_BUILDER_MT_opening_commands,
    HOME_BUILDER_MT_opening_change,
    HOME_BUILDER_MT_door_front_commands,
    HOME_BUILDER_MT_interior_commands,
    HOME_BUILDER_MT_interior_change,
    HOME_BUILDER_MT_interior_part_commands,
    HOME_BUILDER_MT_floating_shelf_commands,
    HOME_BUILDER_MT_valance_commands,
    HOME_BUILDER_MT_support_frame_commands,
    HOME_BUILDER_MT_half_wall_commands,
    HOME_BUILDER_MT_leg_commands,
    HOME_BUILDER_MT_part_commands,
    HOME_BUILDER_MT_appliance_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
