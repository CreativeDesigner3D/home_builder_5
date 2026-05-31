"""Tip-up wedge calculator for refrigerator / tall cabinets.

The operator is a calculator dialog: it reads the cabinet's leg depth /
height, takes ceiling / fudge / max-height inputs, previews the computed
wedge, and on OK writes the wedge_* props onto the cabinet. The geometry
itself is built by the cabinet's recalculate() (the wedge_* props have an
update callback), so the chamfer survives part reconciliation. See
solver_face_frame.compute_wedge / wedge_geometry and
types_face_frame._apply_wedge_cuts.
"""
import bpy
from bpy.props import FloatProperty

from .. import solver_face_frame as solver
from ....units import inch, meter_to_inch


def is_refrigerator_cabinet(obj):
    """True for a face-frame refrigerator cabinet root."""
    return obj is not None and obj.get('CLASS_NAME') == 'RefrigeratorCabinet'


def _fmt(meters):
    return '{:.3f}"'.format(meter_to_inch(meters))


class HB_FACE_FRAME_OT_add_refrigerator_wedge(bpy.types.Operator):
    bl_idname = "hb_face_frame.add_refrigerator_wedge"
    bl_label = "Wedge Calculator"
    bl_description = (
        "Chamfer the back-bottom corner of the cabinet so it clears the "
        "ceiling when tipped upright into place"
    )
    bl_options = {'REGISTER', 'UNDO'}

    ceiling_height: FloatProperty(
        name="Ceiling Height",
        description="Room ceiling height (pre-filled from the scene)",
        default=inch(96.0), unit='LENGTH', subtype='DISTANCE', precision=4,
    )  # type: ignore
    fudge_allowance: FloatProperty(
        name="Fudge Allowance",
        description="Extra clearance subtracted from the ceiling for safety",
        default=inch(0.5), unit='LENGTH', subtype='DISTANCE', precision=4,
        min=0.0,
    )  # type: ignore
    max_wedge_height: FloatProperty(
        name="Max Wedge Height",
        description="Wedge cannot exceed the base molding that covers it; "
                    "taller computed values are capped. 0 disables the cap.",
        default=inch(3.0), unit='LENGTH', subtype='DISTANCE', precision=4,
        min=0.0,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return is_refrigerator_cabinet(context.active_object)

    def invoke(self, context, event):
        cab = context.active_object.face_frame_cabinet
        # Seed from the cabinet's stored inputs if it already has a wedge,
        # else from the scene ceiling.
        if cab.wedge_enabled and cab.wedge_ceiling_height > 0.0:
            self.ceiling_height = cab.wedge_ceiling_height
            self.fudge_allowance = cab.wedge_fudge
            self.max_wedge_height = cab.wedge_max_height
        else:
            hb = getattr(context.scene, 'home_builder', None)
            if hb is not None:
                self.ceiling_height = getattr(hb, 'ceiling_height',
                                              self.ceiling_height)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        cab = context.active_object.face_frame_cabinet
        leg_depth, leg_height = cab.depth, cab.height

        box = layout.box()
        box.label(text="Cabinet", icon='MESH_CUBE')
        row = box.row()
        row.label(text="Leg Height:  " + _fmt(leg_height))
        row.label(text="Leg Depth:  " + _fmt(leg_depth))

        box = layout.box()
        box.label(text="Room & Settings", icon='SETTINGS')
        box.prop(self, 'ceiling_height')
        box.prop(self, 'fudge_allowance')
        box.prop(self, 'max_wedge_height')

        length, height, clamped, needed = solver.compute_wedge(
            leg_depth, leg_height,
            self.ceiling_height, self.fudge_allowance, self.max_wedge_height,
        )
        box = layout.box()
        if needed:
            box.label(text="Computed Wedge", icon='MOD_BEVEL')
            row = box.row()
            row.label(text="Wedge Length:  " + _fmt(length))
            row.label(text="Wedge Height:  " + _fmt(height))
            if clamped:
                row = box.row()
                row.alert = True
                row.label(text="Capped by Max Wedge Height; may not fully "
                               "clear the ceiling.", icon='ERROR')
        else:
            box.label(text="No Wedge Needed", icon='INFO')
            box.label(text="The cabinet's diagonal fits the effective ceiling.")

    def execute(self, context):
        cab = context.active_object.face_frame_cabinet
        length, height, clamped, needed = solver.compute_wedge(
            cab.depth, cab.height,
            self.ceiling_height, self.fudge_allowance, self.max_wedge_height,
        )
        # Persist the inputs; recalc derives + builds the wedge from them.
        cab.wedge_ceiling_height = self.ceiling_height
        cab.wedge_fudge = self.fudge_allowance
        cab.wedge_max_height = self.max_wedge_height
        # Setting wedge_enabled fires the update callback -> recalc.
        cab.wedge_enabled = True

        if not needed:
            self.report({'INFO'},
                "No wedge needed - diagonal fits the effective ceiling")
        else:
            self.report({'INFO'},
                "Wedge: length={}, height={}".format(_fmt(length), _fmt(height)))
        return {'FINISHED'}


class HB_FACE_FRAME_OT_remove_refrigerator_wedge(bpy.types.Operator):
    bl_idname = "hb_face_frame.remove_refrigerator_wedge"
    bl_label = "Remove Wedge"
    bl_description = "Remove the tip-up wedge chamfer from this cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (is_refrigerator_cabinet(obj)
                and obj.face_frame_cabinet.wedge_enabled)

    def execute(self, context):
        # Clearing the flag fires the update callback -> recalc cleans up
        # the cutter + booleans.
        context.active_object.face_frame_cabinet.wedge_enabled = False
        return {'FINISHED'}


classes = (
    HB_FACE_FRAME_OT_add_refrigerator_wedge,
    HB_FACE_FRAME_OT_remove_refrigerator_wedge,
)

register, unregister = bpy.utils.register_classes_factory(classes)
