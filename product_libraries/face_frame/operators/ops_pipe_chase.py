"""Pipe chase for carcass cabinets.

The operator is a sizing dialog: pick the chase location (left back
corner, back middle, right back corner), type the notch size, and on OK
write the chase_* props onto the cabinet. The geometry itself is built
by the cabinet's recalculate() (the chase_* props have an update
callback), so the notch + cover panels survive part reconciliation. See
types_face_frame._apply_pipe_chase.
"""
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty

from .. import types_face_frame
from ....units import inch


def chase_cabinet_root(obj):
    """The cabinet root, or None when obj isn't part of a carcass
    cabinet a chase can cut (panel-only roots have no carcass parts)."""
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return None
    carcass_roles = {
        types_face_frame.PART_ROLE_LEFT_SIDE,
        types_face_frame.PART_ROLE_RIGHT_SIDE,
        types_face_frame.PART_ROLE_BOTTOM,
        types_face_frame.PART_ROLE_BACK,
    }
    for child in root.children:
        if child.get('hb_part_role') in carcass_roles:
            return root
    return None


class HB_FACE_FRAME_OT_add_pipe_chase(bpy.types.Operator):
    bl_idname = "hb_face_frame.add_pipe_chase"
    bl_label = "Pipe Chase"
    bl_description = (
        "Notch the cabinet's back corner (or back middle) for a pipe "
        "chase and cover the opening with panels"
    )
    bl_options = {'REGISTER', 'UNDO'}

    location: EnumProperty(
        name="Location",
        items=[
            ('LEFT_BACK', "Left Back Corner",
             "Notch the back-left corner of the cabinet"),
            ('BACK_MIDDLE', "Back Middle",
             "Notch the middle of the cabinet back"),
            ('RIGHT_BACK', "Right Back Corner",
             "Notch the back-right corner of the cabinet"),
        ],
        default='LEFT_BACK',
    )  # type: ignore
    chase_width: FloatProperty(
        name="Width",
        description="Size of the notch along the cabinet back",
        default=inch(6.0), unit='LENGTH', subtype='DISTANCE', precision=4,
        min=0.0,
    )  # type: ignore
    chase_depth: FloatProperty(
        name="Depth",
        description="Size of the notch into the cabinet, measured from "
                    "the back",
        default=inch(4.0), unit='LENGTH', subtype='DISTANCE', precision=4,
        min=0.0,
    )  # type: ignore
    chase_offset: FloatProperty(
        name="Offset From Left",
        description="Back Middle only: distance from the cabinet's left "
                    "edge to the left edge of the notch",
        default=0.0, unit='LENGTH', subtype='DISTANCE', precision=4,
        min=0.0,
    )  # type: ignore
    notch_side: BoolProperty(
        name="Notch Side Panel",
        description="Corner chases only: also notch the adjacent side "
                    "panel (pipe intrudes past the cabinet side)",
        default=False,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return chase_cabinet_root(context.active_object) is not None

    def invoke(self, context, event):
        root = chase_cabinet_root(context.active_object)
        cab = root.face_frame_cabinet
        if cab.chase_enabled:
            # Editing an existing chase: seed from the stored spec.
            self.location = cab.chase_location
            self.chase_width = cab.chase_width
            self.chase_depth = cab.chase_depth
            self.chase_offset = cab.chase_offset
            self.notch_side = cab.chase_notch_side
        else:
            # Seed the middle offset centered for the current sizes.
            self.chase_offset = max(0.0, (cab.width - self.chase_width) / 2.0)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'location')
        layout.prop(self, 'chase_width')
        layout.prop(self, 'chase_depth')
        if self.location == 'BACK_MIDDLE':
            layout.prop(self, 'chase_offset')
        else:
            layout.prop(self, 'notch_side')

    def execute(self, context):
        root = chase_cabinet_root(context.active_object)
        cab = root.face_frame_cabinet
        cab.chase_location = self.location
        cab.chase_width = self.chase_width
        cab.chase_depth = self.chase_depth
        cab.chase_offset = self.chase_offset
        cab.chase_notch_side = (self.notch_side
                                and self.location != 'BACK_MIDDLE')
        # Setting chase_enabled fires the update callback -> recalc.
        cab.chase_enabled = True
        return {'FINISHED'}


class HB_FACE_FRAME_OT_remove_pipe_chase(bpy.types.Operator):
    bl_idname = "hb_face_frame.remove_pipe_chase"
    bl_label = "Remove Pipe Chase"
    bl_description = "Remove the pipe chase notch and cover panels"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        root = chase_cabinet_root(context.active_object)
        return root is not None and root.face_frame_cabinet.chase_enabled

    def execute(self, context):
        root = chase_cabinet_root(context.active_object)
        # Clearing the flag fires the update callback -> recalc cleans up
        # the cutter, booleans, and cover panels.
        root.face_frame_cabinet.chase_enabled = False
        return {'FINISHED'}


classes = (
    HB_FACE_FRAME_OT_add_pipe_chase,
    HB_FACE_FRAME_OT_remove_pipe_chase,
)

register, unregister = bpy.utils.register_classes_factory(classes)
