import bpy


class hb_face_frame_OT_draw_cabinet(bpy.types.Operator):
    """Draw a face frame cabinet of the given type.

    Phase 2 placeholder: reports the requested cabinet name without building
    geometry. Full construction logic is wired up in Phase 3 once
    types_face_frame.py is ported.
    """
    bl_idname = "hb_face_frame.draw_cabinet"
    bl_label = "Draw Face Frame Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(
        name="Cabinet Name",
        description="The face frame cabinet type to draw",
        default="",
    )  # type: ignore

    def execute(self, context):
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}

        msg = f"Face Frame: would draw '{self.cabinet_name}' (Phase 3 not yet implemented)"
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_draw_cabinet,
)


register, unregister = bpy.utils.register_classes_factory(classes)
