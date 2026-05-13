"""Finished-ends bulk operations.

Two operators:
- apply_finished_ends_to_exposed: writes scene.default_finished_end_type
  to every cabinet side whose exposure is not UNEXPOSED (skips sides
  the user has manually pinned by leaving auto on).
- recalculate_side_exposure: re-arms auto on every side and re-runs
  exposure detection scene-wide. Drives the matching button in the
  Finished Ends and Backs panel.
"""
import bpy

from .. import exposure
from .. import types_face_frame
from ..exposure import _is_face_frame_carcass


SIDES = ('left', 'right', 'back')


class HB_FACE_FRAME_OT_apply_finished_ends_to_exposed(bpy.types.Operator):
    """Write a finished-end type to every cabinet side that is currently
    exposed (PARTIAL or EXPOSED), routed through the same priority rule
    detection uses: dishwasher beats partial beats fully-exposed.
    PARTIAL always resolves to FINISHED - paneled / working-FF / etc.
    are visual treatments for a fully exposed side, not a height-banded
    partial side, so the scene's default_finished_end_type only applies
    to EXPOSED sides. UNEXPOSED sides are left alone. Honors the
    per-side auto flag so manually-pinned sides keep their user choice.
    """
    bl_idname = "hb_face_frame.apply_finished_ends_to_exposed"
    bl_label = "Apply Finished Ends to All Exposed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_props = context.scene.hb_face_frame

        updated = 0
        with types_face_frame.suspend_recalc():
            for obj in context.scene.objects:
                # Carcass roots only - skip PANEL applied panels and
                # any non-cabinet objects.
                if not _is_face_frame_carcass(obj):
                    continue
                cab = obj.face_frame_cabinet
                for side in SIDES:
                    state = getattr(cab, f'{side}_exposure')
                    if state == 'UNEXPOSED':
                        continue
                    if not getattr(cab, f'{side}_finish_end_auto'):
                        continue
                    # Back has no dishwasher concept; only L/R carry the flag.
                    dishwasher = (
                        side != 'back'
                        and getattr(cab, f'{side}_dishwasher_adjacent')
                    )
                    finish = exposure._resolve_finish_type(
                        scene_props, state, dishwasher,
                    )
                    setattr(cab, f'{side}_finished_end_condition', finish)
                    # Re-arm: the user-edit callback flips auto off on any
                    # finish-condition write, including ours.
                    setattr(cab, f'{side}_finish_end_auto', True)
                    updated += 1

        target_type = scene_props.default_finished_end_type
        self.report(
            {'INFO'},
            f"Updated {updated} exposed side(s); EXPOSED -> {target_type}, "
            f"PARTIAL -> FINISHED",
        )
        return {'FINISHED'}


class HB_FACE_FRAME_OT_show_applied_panels(bpy.types.Operator):
    """Switch face frame selection mode to Applied Panels, highlighting
    every applied finished-end panel in the scene so they can be clicked
    directly. Host cabinet cages dim out for the duration.

    Reachable from the Finished Ends and Backs panel only - intentionally
    absent from the main mode picker. Clicking any standard mode (Cabinets,
    Bays, etc.) leaves Applied Panels via the normal selection-mode update
    path, since 'Applied Panels' is just another enum value on
    face_frame_selection_mode.

    Reports "No applied panels in scene" and cancels if nothing is there to
    highlight, so the user isn't dropped into an empty viewport state.
    """
    bl_idname = "hb_face_frame.show_applied_panels"
    bl_label = "Show Applied Panels"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ff_scene = context.scene.hb_face_frame
        has_panels = any(
            obj.get(types_face_frame.TAG_APPLIED_PANEL_SIDE)
            for obj in context.scene.objects
        )
        if not has_panels:
            self.report({'INFO'}, "No applied panels in scene")
            return {'CANCELLED'}
        # Order matters: enable the master toggle first so the mode write
        # below produces a visible highlight pass rather than landing in
        # the off-path branch of toggle_mode.
        ff_scene.face_frame_selection_mode_enabled = True
        ff_scene.face_frame_selection_mode = 'Applied Panels'
        return {'FINISHED'}


class HB_FACE_FRAME_OT_recalculate_side_exposure(bpy.types.Operator):
    """Sweep every face-frame cabinet, re-arm the per-side auto flags,
    and recompute exposure + finish type from current neighbor and
    wall geometry. Use this after a layout change to push manual side
    settings back to auto-pick.
    """
    bl_idname = "hb_face_frame.recalculate_side_exposure"
    bl_label = "Recalculate Side Exposure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        exposure.recalc_all_cabinet_exposure(context)
        self.report({'INFO'}, "Recalculated side exposure")
        return {'FINISHED'}


classes = (
    HB_FACE_FRAME_OT_apply_finished_ends_to_exposed,
    HB_FACE_FRAME_OT_show_applied_panels,
    HB_FACE_FRAME_OT_recalculate_side_exposure,
)


register, unregister = bpy.utils.register_classes_factory(classes)
