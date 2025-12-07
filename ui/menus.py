import bpy

class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.wall_prompts")
        layout.operator("home_builder_walls.add_floor")

classes = (
    HOME_BUILDER_MT_wall_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)        