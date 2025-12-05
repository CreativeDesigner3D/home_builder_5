import bpy
from .units import inch

class home_builder_OT_to_do(bpy.types.Operator):
    bl_idname = "home_builder.to_do"
    bl_label = "To Do"
    bl_description = "This is a placeholder for a to do list"

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        pass


class home_builder_OT_set_recommended_settings(bpy.types.Operator):
    bl_idname = "home_builder.set_recommended_settings"
    bl_label = "Set Recommended Settings"
    bl_description = "This will set the recommended blender settings"

    turn_off_relationship_lines: bpy.props.BoolProperty(name="Turn Off Relationship Lines",
                                                        description="This setting culters the interface with unneeded relationship lines",
                                                        default=True)# type: ignore

    turn_on_object_color_type: bpy.props.BoolProperty(name="Turn On Object Color Type",
                                                        description="This setting turns on the object color type",
                                                        default=True)# type: ignore
    
    use_vertex_snapping: bpy.props.BoolProperty(name="Use Vertex Snapping",
                                                        description="This setting turns on vertex snapping",
                                                        default=True)# type: ignore

    turn_off_3d_cursor: bpy.props.BoolProperty(name="Turn Off 3D Cursor",
                                                        description="This setting turns off the 3D cursor",
                                                        default=True)# type: ignore

    show_wireframes: bpy.props.BoolProperty(name="Show Wireframes",
                                                        description="This setting shows the wireframes",
                                                        default=True)# type: ignore

    change_studio_lighting: bpy.props.BoolProperty(name="Change Studio Lighting",
                                                        description="This setting changes the studio lighting to the recommended lighting",
                                                        default=True)# type: ignore

    def check(self, context):
        return True

    def invoke(self,context,event):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.data:
                        self.space_data = region.data
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def execute(self, context):
        view = context.space_data
        overlay = view.overlay
        shading = view.shading        
        tool_settings = context.scene.tool_settings
        if self.turn_off_relationship_lines:
            overlay.show_relationship_lines = False
        if self.turn_on_object_color_type:
            shading.color_type = 'OBJECT'
        if self.turn_off_3d_cursor:
            overlay.show_cursor = False
        if self.show_wireframes:
            overlay.show_wireframes = True
            overlay.wireframe_threshold = 0.0
            overlay.wireframe_opacity = 0.8
        if self.change_studio_lighting:
            shading.studio_light = 'paint.sl'
        if self.use_vertex_snapping:
            tool_settings.snap_elements_base = {'VERTEX'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="These are the recommended Home Builder settings.")
        box.prop(self,'turn_off_relationship_lines')
        box.prop(self,'turn_on_object_color_type')
        box.prop(self,'turn_off_3d_cursor')
        box.prop(self,'show_wireframes')
        box.prop(self,'change_studio_lighting')
        box.prop(self,'use_vertex_snapping')

classes = (
    home_builder_OT_to_do,
    home_builder_OT_set_recommended_settings,
)

register, unregister = bpy.utils.register_classes_factory(classes)             