"""Face frame style management ops: add/remove for cabinet styles and door
styles. Assign / Update ops land in a follow-up alongside the per-part
material wiring.
"""
import bpy
from bpy.types import Operator


def _next_unique_name(base, existing):
    """Return base, or base.001 / base.002 / ... if base is taken."""
    if base not in existing:
        return base
    i = 1
    while f"{base}.{i:03d}" in existing:
        i += 1
    return f"{base}.{i:03d}"


class hb_face_frame_OT_add_cabinet_style(Operator):
    """Add a new face frame cabinet style"""
    bl_idname = "hb_face_frame.add_cabinet_style"
    bl_label = "Add Cabinet Style"
    bl_description = "Add a new face frame cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ff = context.scene.hb_face_frame
        existing = [s.name for s in ff.cabinet_styles]
        new_style = ff.cabinet_styles.add()
        new_style.name = _next_unique_name("Style", existing)
        ff.active_cabinet_style_index = len(ff.cabinet_styles) - 1
        self.report({'INFO'}, f"Added cabinet style: {new_style.name}")
        return {'FINISHED'}


class hb_face_frame_OT_remove_cabinet_style(Operator):
    """Remove the active face frame cabinet style"""
    bl_idname = "hb_face_frame.remove_cabinet_style"
    bl_label = "Remove Cabinet Style"
    bl_description = "Remove the active cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Always keep at least one style around so placement / assign
        # paths have something to apply.
        ff = context.scene.hb_face_frame
        return len(ff.cabinet_styles) > 1

    def execute(self, context):
        ff = context.scene.hb_face_frame
        if len(ff.cabinet_styles) <= 1:
            self.report({'WARNING'}, "At least one cabinet style must remain")
            return {'CANCELLED'}
        idx = ff.active_cabinet_style_index
        if idx < 0 or idx >= len(ff.cabinet_styles):
            return {'CANCELLED'}
        name = ff.cabinet_styles[idx].name
        ff.cabinet_styles.remove(idx)
        if ff.active_cabinet_style_index >= len(ff.cabinet_styles):
            ff.active_cabinet_style_index = max(0, len(ff.cabinet_styles) - 1)
        self.report({'INFO'}, f"Removed cabinet style: {name}")
        return {'FINISHED'}


class hb_face_frame_OT_add_door_style(Operator):
    """Add a new face frame door style"""
    bl_idname = "hb_face_frame.add_door_style"
    bl_label = "Add Door Style"
    bl_description = "Add a new face frame door / drawer-front style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ff = context.scene.hb_face_frame
        existing = [s.name for s in ff.door_styles]
        new_style = ff.door_styles.add()
        new_style.name = _next_unique_name("Door Style", existing)
        ff.active_door_style_index = len(ff.door_styles) - 1
        self.report({'INFO'}, f"Added door style: {new_style.name}")
        return {'FINISHED'}


class hb_face_frame_OT_remove_door_style(Operator):
    """Remove the active face frame door style"""
    bl_idname = "hb_face_frame.remove_door_style"
    bl_label = "Remove Door Style"
    bl_description = "Remove the active door style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = context.scene.hb_face_frame
        return len(ff.door_styles) > 1

    def execute(self, context):
        ff = context.scene.hb_face_frame
        if len(ff.door_styles) <= 1:
            self.report({'WARNING'}, "At least one door style must remain")
            return {'CANCELLED'}
        idx = ff.active_door_style_index
        if idx < 0 or idx >= len(ff.door_styles):
            return {'CANCELLED'}
        name = ff.door_styles[idx].name
        ff.door_styles.remove(idx)
        if ff.active_door_style_index >= len(ff.door_styles):
            ff.active_door_style_index = max(0, len(ff.door_styles) - 1)
        self.report({'INFO'}, f"Removed door style: {name}")
        return {'FINISHED'}


class hb_face_frame_OT_assign_style_to_selected_cabinets(Operator):
    """Apply the active cabinet style to every selected face frame cabinet"""
    bl_idname = "hb_face_frame.assign_style_to_selected_cabinets"
    bl_label = "Assign Style"
    bl_description = "Apply the active cabinet style to every selected face frame cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = context.scene.hb_face_frame
        return len(ff.cabinet_styles) > 0 and len(context.selected_objects) > 0

    def execute(self, context):
        from .. import types_face_frame
        ff = context.scene.hb_face_frame
        idx = ff.active_cabinet_style_index
        if idx < 0 or idx >= len(ff.cabinet_styles):
            self.report({'WARNING'}, "No active cabinet style")
            return {'CANCELLED'}
        style = ff.cabinet_styles[idx]

        # Resolve every selected object up to its cabinet root, dedupe
        roots = []
        seen = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is None or root.name in seen:
                continue
            seen.add(root.name)
            roots.append(root)

        if not roots:
            self.report({'WARNING'}, "No face frame cabinets in selection")
            return {'CANCELLED'}

        for root in roots:
            style.assign_style_to_cabinet(root)
        self.report({'INFO'}, f"Applied '{style.name}' to {len(roots)} cabinet(s)")
        return {'FINISHED'}


class hb_face_frame_OT_update_cabinets_from_style(Operator):
    """Re-apply the active cabinet style to every cabinet already tagged with it"""
    bl_idname = "hb_face_frame.update_cabinets_from_style"
    bl_label = "Update Cabinets"
    bl_description = "Re-apply the active cabinet style to every cabinet already tagged with that style name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = context.scene.hb_face_frame
        return len(ff.cabinet_styles) > 0

    def execute(self, context):
        ff = context.scene.hb_face_frame
        idx = ff.active_cabinet_style_index
        if idx < 0 or idx >= len(ff.cabinet_styles):
            self.report({'WARNING'}, "No active cabinet style")
            return {'CANCELLED'}
        style = ff.cabinet_styles[idx]
        target_name = style.name

        # Walk every object in the scene; match by cage marker + STYLE_NAME
        roots = [
            obj for obj in context.scene.objects
            if obj.get('IS_FACE_FRAME_CABINET_CAGE') and obj.get('STYLE_NAME') == target_name
        ]
        if not roots:
            self.report({'INFO'}, f"No cabinets tagged with '{target_name}'")
            return {'FINISHED'}

        for root in roots:
            style.assign_style_to_cabinet(root)
        self.report({'INFO'}, f"Updated {len(roots)} cabinet(s) tagged '{target_name}'")
        return {'FINISHED'}


class hb_face_frame_OT_assign_door_style_to_selected_fronts(Operator):
    """Apply the active door style to every selected face frame front"""
    bl_idname = "hb_face_frame.assign_door_style_to_selected_fronts"
    bl_label = "Assign Door Style"
    bl_description = "Apply the active door style to every selected face frame front"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = context.scene.hb_face_frame
        return len(ff.door_styles) > 0 and len(context.selected_objects) > 0

    def execute(self, context):
        ff = context.scene.hb_face_frame
        idx = ff.active_door_style_index
        if idx < 0 or idx >= len(ff.door_styles):
            self.report({'WARNING'}, "No active door style")
            return {'CANCELLED'}
        ds = ff.door_styles[idx]

        applied = 0
        errors = []
        for obj in context.selected_objects:
            result = ds.assign_style_to_front(obj)
            if result is True:
                applied += 1
            elif isinstance(result, str):
                errors.append(f"{obj.name}: {result}")
            # False = not a styleable front, skip silently

        if applied == 0 and not errors:
            self.report({'WARNING'}, "No face frame fronts in selection")
            return {'CANCELLED'}
        for err in errors:
            self.report({'WARNING'}, err)
        self.report({'INFO'}, f"Applied '{ds.name}' to {applied} front(s)")
        return {'FINISHED'}


class hb_face_frame_OT_update_fronts_from_door_style(Operator):
    """Re-apply the active door style to every front tagged with it"""
    bl_idname = "hb_face_frame.update_fronts_from_door_style"
    bl_label = "Update Fronts"
    bl_description = "Re-apply the active door style to every front already tagged with that style name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = context.scene.hb_face_frame
        return len(ff.door_styles) > 0

    def execute(self, context):
        ff = context.scene.hb_face_frame
        idx = ff.active_door_style_index
        if idx < 0 or idx >= len(ff.door_styles):
            self.report({'WARNING'}, "No active door style")
            return {'CANCELLED'}
        ds = ff.door_styles[idx]
        target = ds.name

        applied = 0
        errors = []
        for obj in context.scene.objects:
            if obj.get('DOOR_STYLE_NAME') != target:
                continue
            result = ds.assign_style_to_front(obj)
            if result is True:
                applied += 1
            elif isinstance(result, str):
                errors.append(f"{obj.name}: {result}")

        for err in errors:
            self.report({'WARNING'}, err)
        self.report({'INFO'}, f"Updated {applied} front(s) tagged '{target}'")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_add_cabinet_style,
    hb_face_frame_OT_remove_cabinet_style,
    hb_face_frame_OT_add_door_style,
    hb_face_frame_OT_remove_door_style,
    hb_face_frame_OT_assign_style_to_selected_cabinets,
    hb_face_frame_OT_update_cabinets_from_style,
    hb_face_frame_OT_assign_door_style_to_selected_fronts,
    hb_face_frame_OT_update_fronts_from_door_style,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()


def unregister():
    _unregister_classes()
