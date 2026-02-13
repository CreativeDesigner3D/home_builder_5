import bpy


class HOME_BUILDER_MT_main_menu(bpy.types.Menu):
    bl_label = "Home Builder"
    bl_idname = "HOME_BUILDER_MT_main_menu"

    def draw(self, context):
        layout = self.layout
        
        # Room operations
        layout.operator("home_builder.create_room", text="New Room", icon='ADD')
        layout.menu("HOME_BUILDER_MT_room_list", text="Switch Room", icon='LOOP_BACK')
        
        layout.separator()
        
        # Layout views submenu
        layout.menu("HOME_BUILDER_MT_layout_views_create", text="Create View", icon='VIEW_ORTHO')
        
        layout.separator()
        
        # Camera
        layout.operator("home_builder.create_camera", text="Create Camera", icon='CAMERA_DATA')
        
        layout.separator()
        
        # Settings
        layout.operator("home_builder.set_recommended_settings", 
                       text="Recommended Settings", icon='PREFERENCES')
        layout.operator("home_builder.rendering_settings",
                       text="Rendering Settings", icon='RENDER_STILL')
        
        layout.separator()
        
        # Developer
        layout.operator("home_builder.reload_addon", text="Reload Add-on", icon='FILE_REFRESH')


class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.wall_prompts", text="Wall Prompts")
        layout.separator()
        layout.operator("home_builder_walls.hide_wall", text="Hide Wall", icon='HIDE_ON')
        layout.operator("home_builder_walls.show_all_walls", text="Show All Walls", icon='HIDE_OFF')
        layout.separator()
        layout.operator("home_builder_walls.delete_wall", text="Delete Wall", icon='X')


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


def draw_home_builder_menu(self, context):
    self.layout.menu("HOME_BUILDER_MT_main_menu")


classes = (
    HOME_BUILDER_MT_main_menu,
    HOME_BUILDER_MT_wall_commands,
    HOME_BUILDER_MT_door_commands,
    HOME_BUILDER_MT_window_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder_menu)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_home_builder_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
