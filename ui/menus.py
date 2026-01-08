import bpy


class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.wall_prompts", text="Wall Prompts")


class HOME_BUILDER_MT_cabinet_commands(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.cabinet_prompts", text="Cabinet Prompts")
        layout.separator()
        layout.operator("hb_frameless.drop_cabinet_to_countertop", text="Drop to Countertop")
        layout.operator("hb_frameless.drop_cabinet_height", text="Drop Height")
        layout.operator("hb_frameless.raise_cabinet_bottom", text="Raise Bottom")
        layout.separator()
        layout.operator("hb_frameless.add_applied_end", text="Add Applied End")
        layout.separator()
        layout.operator("hb_frameless.delete_cabinet", text="Delete Cabinet")


class HOME_BUILDER_MT_bay_commands(bpy.types.Menu):
    bl_label = "Bay Commands"

    def draw(self, context):
        layout = self.layout
        layout.menu("HOME_BUILDER_MT_bay_change_configuration", text="Change Configuration")


class HOME_BUILDER_MT_bay_change_configuration(bpy.types.Menu):
    bl_label = "Change Bay Configuration"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.change_bay_opening", text="Door/Drawer").opening_type = 'DOOR_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="Left Swing Door").opening_type = 'LEFT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Right Swing Door").opening_type = 'RIGHT_DOOR'
        layout.operator("hb_frameless.change_bay_opening", text="Double Doors").opening_type = 'DOUBLE_DOORS'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Single Drawer").opening_type = 'SINGLE_DRAWER'
        layout.operator("hb_frameless.change_bay_opening", text="2 Drawer Stack").opening_type = '2_DRAWER_STACK'
        layout.operator("hb_frameless.change_bay_opening", text="3 Drawer Stack").opening_type = '3_DRAWER_STACK'
        layout.operator("hb_frameless.change_bay_opening", text="4 Drawer Stack").opening_type = '4_DRAWER_STACK'
        layout.separator()
        layout.operator("hb_frameless.change_bay_opening", text="Open (No Front)").opening_type = 'OPEN'
        layout.separator()
        layout.operator("hb_frameless.custom_vertical_splitter", text="Custom Vertical...")
        layout.operator("hb_frameless.custom_horizontal_splitter", text="Custom Horizontal...")


class HOME_BUILDER_MT_opening_commands(bpy.types.Menu):
    bl_label = "Opening Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.opening_prompts", text="Opening Prompts")
        layout.separator()
        layout.menu("HOME_BUILDER_MT_opening_change", text="Change Opening")


class HOME_BUILDER_MT_opening_change(bpy.types.Menu):
    bl_label = "Change Opening"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_frameless.change_opening_type", text="Doors").opening_type = 'DOORS'
        layout.operator("hb_frameless.change_opening_type", text="Drawer").opening_type = 'DRAWER'
        layout.operator("hb_frameless.change_opening_type", text="Open (No Front)").opening_type = 'OPEN'
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
        layout.operator("hb_frameless.change_interior_type", text="Rollouts").interior_type = 'ROLLOUTS'
        layout.operator("hb_frameless.change_interior_type", text="Tray Dividers").interior_type = 'TRAY_DIVIDERS'
        layout.operator("hb_frameless.change_interior_type", text="Empty (No Interior)").interior_type = 'EMPTY'
        layout.separator()
        layout.operator("hb_frameless.custom_interior_vertical", text="Custom Vertical Division...")
        layout.operator("hb_frameless.custom_interior_horizontal", text="Custom Horizontal Division...")


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


classes = (
    HOME_BUILDER_MT_wall_commands,
    HOME_BUILDER_MT_cabinet_commands,
    HOME_BUILDER_MT_bay_commands,
    HOME_BUILDER_MT_bay_change_configuration,
    HOME_BUILDER_MT_opening_commands,
    HOME_BUILDER_MT_opening_change,
    HOME_BUILDER_MT_door_front_commands,
    HOME_BUILDER_MT_interior_commands,
    HOME_BUILDER_MT_interior_change,
    HOME_BUILDER_MT_interior_part_commands,
    HOME_BUILDER_MT_appliance_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
