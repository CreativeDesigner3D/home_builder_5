import bpy

from .. import types_face_frame
from .... import hb_project


class hb_face_frame_OT_update_cabinet_sizes(bpy.types.Operator):
    """Push the current scene tall_cabinet_height and upper_cabinet_height
    onto every face frame cabinet in this scene. Resyncs cabinet sizes
    after a top cabinet clearance / wall cabinet location / ceiling
    height change.

    BASE cabinet height is user-editable and is not derived, so BASE
    cabinets are skipped. LAP_DRAWER has no derived size and is skipped.
    Writing cab_props.height triggers the per-cabinet recalc via the
    existing prop update callback, so each cabinet rebuilds itself.
    """
    bl_idname = "hb_face_frame.update_cabinet_sizes"
    bl_label = "Update Face Frame Cabinet Sizes"
    bl_description = "Update tall and upper cabinet heights to match the current scene defaults"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Source values come from the main scene (matches frameless's
        # pattern - handles cases where the user is in a viewport scene
        # different from the data scene).
        main_scene = hb_project.get_main_scene()
        if not hasattr(main_scene, 'hb_face_frame'):
            self.report({'WARNING'}, "Face frame scene props not registered")
            return {'CANCELLED'}
        ff_props = main_scene.hb_face_frame

        updated = 0
        for obj in context.scene.objects:
            if not obj.get(types_face_frame.TAG_CABINET_CAGE):
                continue
            cabinet_type = obj.face_frame_cabinet.cabinet_type
            if cabinet_type == 'TALL':
                obj.face_frame_cabinet.height = ff_props.tall_cabinet_height
            elif cabinet_type == 'UPPER':
                obj.face_frame_cabinet.height = ff_props.upper_cabinet_height
            else:
                continue
            updated += 1

        self.report({'INFO'}, f"Updated {updated} cabinet(s)")
        return {'FINISHED'}


class hb_face_frame_OT_update_toe_kicks(bpy.types.Operator):
    """Push the project toe kick height / setback onto every face frame
    cabinet in this scene. Cabinets without a real kick are left alone:
    refrigerator-style zero-height kicks, and FLOATING kicks (the height
    there is the float-off-floor amount, e.g. a lap drawer). Uppers carry
    the props but never build a kick, so writing them is harmless."""
    bl_idname = "hb_face_frame.update_toe_kicks"
    bl_label = "Update Toe Kicks"
    bl_description = ("Apply the project toe kick height and depth to "
                      "every cabinet in this room")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        if not hasattr(main_scene, 'hb_face_frame'):
            self.report({'WARNING'}, "Face frame scene props not registered")
            return {'CANCELLED'}
        ff_props = main_scene.hb_face_frame
        height = ff_props.default_toe_kick_height
        setback = ff_props.default_toe_kick_setback

        # Snapshot first: each write recalcs the cabinet, and recalcs
        # can add / remove scene objects under a live iteration.
        cages = [obj for obj in context.scene.objects
                 if obj.get(types_face_frame.TAG_CABINET_CAGE)]
        updated = 0
        with types_face_frame.suspend_recalc():
            for obj in cages:
                cab = obj.face_frame_cabinet
                if cab.toe_kick_height <= 0.0 or cab.toe_kick_type == 'FLOATING':
                    continue
                if (abs(cab.toe_kick_height - height) < 1e-9
                        and abs(cab.toe_kick_setback - setback) < 1e-9):
                    continue
                cab.toe_kick_height = height
                cab.toe_kick_setback = setback
                updated += 1

        self.report({'INFO'}, f"Updated toe kick on {updated} cabinet(s)")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_update_cabinet_sizes,
    hb_face_frame_OT_update_toe_kicks,
)


register, unregister = bpy.utils.register_classes_factory(classes)
