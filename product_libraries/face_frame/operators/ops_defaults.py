import bpy


class hb_face_frame_OT_update_cabinet_sizes(bpy.types.Operator):
    """Refresh sizes of existing face frame cabinets to match scene defaults.

    Phase 2 placeholder. Full implementation comes in Phase 3.
    """
    bl_idname = "hb_face_frame.update_cabinet_sizes"
    bl_label = "Update Face Frame Cabinet Sizes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Face Frame: update_cabinet_sizes is a Phase 2 placeholder")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_update_cabinet_sizes,
)


register, unregister = bpy.utils.register_classes_factory(classes)
