"""Finished-ends bulk operations.

Today: a single operator that walks the scene and writes the chosen
finished-end type to every side flagged exposed. Future passes add
scene-wide exposure detection (from neighbor / wall geometry) and
sweep operators that re-evaluate exposure before assigning.
"""
import bpy

from .. import types_face_frame


SIDES = ('left', 'right', 'back')


class HB_FACE_FRAME_OT_apply_finished_ends_to_exposed(bpy.types.Operator):
    """Write the scene's default finished-end type to every cabinet side
    flagged exposed. Non-exposed sides are left alone so prior decisions
    aren't clobbered.
    """
    bl_idname = "hb_face_frame.apply_finished_ends_to_exposed"
    bl_label = "Apply Finished Ends to All Exposed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_props = context.scene.hb_face_frame
        target_type = scene_props.default_finished_end_type

        updated = 0
        for obj in context.scene.objects:
            if not obj.get(types_face_frame.TAG_CABINET_CAGE):
                continue
            cab = obj.face_frame_cabinet
            for side in SIDES:
                if not getattr(cab, f'{side}_exposed'):
                    continue
                setattr(cab, f'{side}_finished_end_condition', target_type)
                updated += 1

        self.report({'INFO'}, f"Updated {updated} exposed side(s) to {target_type}")
        return {'FINISHED'}


classes = (
    HB_FACE_FRAME_OT_apply_finished_ends_to_exposed,
)


register, unregister = bpy.utils.register_classes_factory(classes)
