import bpy

from .. import types_face_frame
from .... import hb_project

# An upper whose bottom is further than this from the wall cabinet
# location was hung by hand.
_HUNG_BY_HAND_TOL = 0.0254 / 16.0


class hb_face_frame_OT_update_cabinet_sizes(bpy.types.Operator):
    """Push this room's tall_cabinet_height and upper_cabinet_height
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
        # Source values come from the room being updated, not from the
        # main scene: the derived heights are the room's own ceiling
        # height less its clearances, so reading them off another room
        # sizes these cabinets for that room's walls. Layout and detail
        # scenes fall back to the main scene (see get_settings_scene).
        settings_scene = hb_project.get_settings_scene(context)
        if not hasattr(settings_scene, 'hb_face_frame'):
            self.report({'WARNING'}, "Face frame scene props not registered")
            return {'CANCELLED'}
        ff_props = settings_scene.hb_face_frame

        updated = 0
        kept = 0
        wall_location = ff_props.default_wall_cabinet_location
        for obj in context.scene.objects:
            if not obj.get(types_face_frame.TAG_CABINET_CAGE):
                continue
            cabinet_type = obj.face_frame_cabinet.cabinet_type
            if cabinet_type == 'TALL':
                obj.face_frame_cabinet.height = ff_props.tall_cabinet_height
            elif cabinet_type == 'UPPER':
                # Height is pushed from the cabinet's bottom, which stays
                # put. An upper hung anywhere but the wall cabinet
                # location was sized by hand (stretched down to a
                # counter, stacked, set over an appliance): the derived
                # height is meant for the standard hang, so giving it to
                # this cabinet would pull its top down. Leave it alone.
                if abs(obj.location.z - wall_location) > _HUNG_BY_HAND_TOL:
                    kept += 1
                    continue
                obj.face_frame_cabinet.height = ff_props.upper_cabinet_height
            else:
                continue
            updated += 1

        msg = f"Updated {updated} cabinet(s)"
        if kept:
            msg += (f"; kept {kept} upper(s) hung by hand at their own "
                    "size")
        self.report({'INFO'}, msg)
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


class hb_face_frame_OT_update_finish_toe_kicks(bpy.types.Operator):
    """Push the project finish toe kick setting (on / off and stock)
    onto every face frame cabinet in this scene - one step to add or
    remove the finish toe kick everywhere instead of cabinet by cabinet.
    Cabinets whose kick can't carry one ignore the flag when they build,
    so writing every cabinet is harmless."""
    bl_idname = "hb_face_frame.update_finish_toe_kicks"
    bl_label = "Update Finish Toe Kicks"
    bl_description = ("Apply the project finish toe kick setting to "
                      "every cabinet in this room")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        if not hasattr(main_scene, 'hb_face_frame'):
            self.report({'WARNING'}, "Face frame scene props not registered")
            return {'CANCELLED'}
        ff_props = main_scene.hb_face_frame
        include = ff_props.default_include_finish_toe_kick
        kick_type = ff_props.default_finish_toe_kick_type

        # Snapshot first: each write recalcs the cabinet, and recalcs
        # can add / remove scene objects under a live iteration.
        cages = [obj for obj in context.scene.objects
                 if obj.get(types_face_frame.TAG_CABINET_CAGE)]
        updated = 0
        with types_face_frame.suspend_recalc():
            for obj in cages:
                cab = obj.face_frame_cabinet
                if cab.cabinet_type == 'PANEL':
                    continue
                changed = False
                # A flush kick only takes a finish kick when it is
                # turned on by hand, so the push never adds one there.
                flush_on = include and cab.toe_kick_type == 'FLUSH'
                if not flush_on and cab.include_finish_toe_kick != include:
                    cab.include_finish_toe_kick = include
                    changed = True
                if include and cab.finish_toe_kick_type != kick_type:
                    cab.finish_toe_kick_type = kick_type
                    changed = True
                updated += changed

        self.report({'INFO'},
                    f"Updated finish toe kick on {updated} cabinet(s)")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_update_cabinet_sizes,
    hb_face_frame_OT_update_toe_kicks,
    hb_face_frame_OT_update_finish_toe_kicks,
)


register, unregister = bpy.utils.register_classes_factory(classes)
