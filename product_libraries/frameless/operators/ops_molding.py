import bpy

from .. import molding_frameless


class hb_frameless_OT_add_molding(bpy.types.Operator):
    """Add crown molding along the top of every cabinet in the room tall
    enough to carry it, using the selected profile (re-run after moving
    cabinets; the room's previous run is cleared first)"""
    bl_idname = "hb_frameless.add_molding"
    bl_label = "Add Crown Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        profile = molding_frameless.load_profile(
            molding_frameless.current_profile_name(scene))
        if profile is None:
            self.report({'WARNING'}, "Crown profile not found")
            return {'CANCELLED'}
        made = molding_frameless.add_crown(scene, profile)
        if made == 0:
            self.report({'INFO'},
                        "No qualifying cabinets (tops under 60\" are skipped)")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Added crown to {made} cabinet(s)")
        return {'FINISHED'}


class hb_frameless_OT_delete_molding(bpy.types.Operator):
    """Remove all crown molding from the room"""
    bl_idname = "hb_frameless.delete_molding"
    bl_label = "Remove Crown Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        removed = molding_frameless.clear_molding(context.scene)
        self.report({'INFO'}, f"Removed {removed} crown run(s)")
        return {'FINISHED'}


classes = (
    hb_frameless_OT_add_molding,
    hb_frameless_OT_delete_molding,
)

register, unregister = bpy.utils.register_classes_factory(classes)
