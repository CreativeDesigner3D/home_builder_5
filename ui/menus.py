import bpy


class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.wall_prompts", text="Wall Prompts")


class HOME_BUILDER_MT_door_commands(bpy.types.Menu):
    bl_label = "Door Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_doors_windows.door_prompts", text="Door Prompts")
        layout.separator()
        layout.operator("home_builder_doors_windows.flip_door_swing", text="Flip Door Swing")
        layout.operator("home_builder_doors_windows.flip_door_hand", text="Flip Door Hand")
        layout.operator("home_builder_doors_windows.toggle_double_door", text="Toggle Double Door")
        layout.separator()
        layout.operator("home_builder_doors_windows.delete_door_window", text="Delete Door").object_type = 'DOOR'


class HOME_BUILDER_MT_window_commands(bpy.types.Menu):
    bl_label = "Window Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_doors_windows.window_prompts", text="Window Prompts")
        layout.separator()
        layout.operator("home_builder_doors_windows.delete_door_window", text="Delete Window").object_type = 'WINDOW'


classes = (
    HOME_BUILDER_MT_wall_commands,
    HOME_BUILDER_MT_door_commands,
    HOME_BUILDER_MT_window_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
