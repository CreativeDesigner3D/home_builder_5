"""Face frame sidebar UI + shared draw functions.

The draw_cabinet_properties() function is the single layout used by both
the sidebar panel (HB_FACE_FRAME_PT_active_cabinet) and the right-click
popup operator (hb_face_frame.cabinet_prompts). Property changes fire the
cabinet's update callbacks live - no apply step needed.

The HB_FACE_FRAME_PT_test_drop panel provides a development-time hook for
dropping cabinets with arbitrary bay counts so the multi-bay solver can
be exercised without waiting for the placement-driven defaults system.
"""
import bpy

from . import types_face_frame


# ---------------------------------------------------------------------------
# Shared draw function - used by sidebar panel AND cabinet_prompts popup
# ---------------------------------------------------------------------------
def draw_cabinet_properties(layout, root):
    """Draw the cabinet properties UI for the given cabinet root object.

    Both the sidebar panel and the right-click popup operator call this so
    they always show identical content.
    """
    cab_props = root.face_frame_cabinet

    # Identity header
    col = layout.column(align=True)
    row = col.row()
    row.label(text=root.name, icon='MESH_CUBE')
    row = col.row()
    row.label(text=f"Type: {cab_props.cabinet_type}")
    row.label(text=f"Class: {root.get('CLASS_NAME', '?')}")

    # Dimensions
    box = layout.box()
    box.label(text="Dimensions", icon='ARROW_LEFTRIGHT')
    col = box.column(align=True)
    col.prop(cab_props, 'width', text="Width")
    col.prop(cab_props, 'depth', text="Depth")
    col.prop(cab_props, 'height', text="Height")

    # Construction
    box = layout.box()
    box.label(text="Construction", icon='MODIFIER')
    col = box.column(align=True)
    col.prop(cab_props, 'material_thickness', text="Material Thickness")
    col.prop(cab_props, 'back_thickness', text="Back Thickness")

    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.separator()
        col.prop(cab_props, 'toe_kick_type', text="Toe Kick Type")
        col.prop(cab_props, 'toe_kick_height', text="Toe Kick Height")
        col.prop(cab_props, 'toe_kick_setback', text="Toe Kick Setback")

    # Face Frame
    box = layout.box()
    box.label(text="Face Frame", icon='MESH_GRID')
    col = box.column(align=True)
    col.prop(cab_props, 'face_frame_thickness', text="Thickness")
    col.separator()
    col.prop(cab_props, 'left_stile_width', text="Left Stile Width")
    col.prop(cab_props, 'right_stile_width', text="Right Stile Width")
    col.separator()
    col.prop(cab_props, 'top_rail_width', text="Top Rail Width (default)")
    col.prop(cab_props, 'bottom_rail_width', text="Bottom Rail Width (default)")

    # Bays - one collapsible row per bay child
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if bays:
        box = layout.box()
        box.label(text=f"Bays ({len(bays)})", icon='MESH_CUBE')
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            sub = box.box()
            sub.label(text=f"Bay {bp.bay_index + 1}")
            col = sub.column(align=True)

            # Width row: field is disabled when the value is auto-calculated.
            # The padlock toggle on the right switches to manual mode.
            #   unlock_width = False -> auto, field disabled, LOCKED icon
            #   unlock_width = True  -> manual, field editable, UNLOCKED icon
            width_row = col.row(align=True)
            field = width_row.row(align=True)
            field.enabled = bp.unlock_width
            field.prop(bp, 'width', text="Width")
            lock_icon = 'UNLOCKED' if bp.unlock_width else 'LOCKED'
            width_row.prop(bp, 'unlock_width', text="", icon=lock_icon)

            col.prop(bp, 'height', text="Height")
            col.prop(bp, 'depth', text="Depth")
            col.prop(bp, 'kick_height', text="Kick Height")
            col.prop(bp, 'top_offset', text="Top Offset")
            col.separator()
            col.prop(bp, 'top_rail_width', text="Top Rail Width")
            col.prop(bp, 'bottom_rail_width', text="Bottom Rail Width")
            col.separator()
            col.prop(bp, 'remove_bottom', text="Remove Bottom")

    # Mid stiles
    mid_stiles = cab_props.mid_stile_widths
    if len(mid_stiles) > 0:
        box = layout.box()
        box.label(text=f"Mid Stiles ({len(mid_stiles)})", icon='SNAP_EDGE')
        for i, ms in enumerate(mid_stiles):
            sub = box.box()
            sub.label(text=f"Mid Stile {i + 1}")
            col = sub.column(align=True)
            col.prop(ms, 'width', text="Width")
            col.prop(ms, 'extend_up_amount', text="Extend Up")
            col.prop(ms, 'extend_down_amount', text="Extend Down")

    # Recalc button - useful when properties were set via script
    layout.separator()
    layout.operator('hb_face_frame.recalculate_cabinet',
                    text="Recalculate", icon='FILE_REFRESH')


# ---------------------------------------------------------------------------
# Active-cabinet sidebar panel
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_active_cabinet(bpy.types.Panel):
    """Sidebar panel for the active face frame cabinet."""
    bl_label = "Face Frame Cabinet"
    bl_idname = "HB_FACE_FRAME_PT_active_cabinet"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_order = 11

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_cabinet_properties(self.layout, root)


# ---------------------------------------------------------------------------
# Test-drop panel (development-time bay_qty exercise)
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_test_drop(bpy.types.Panel):
    """Drop a face frame cabinet with a chosen bay count.

    Always-visible test panel. Drop buttons call the standard draw_cabinet
    operator with the bay_qty from scene-level test settings, so the
    multi-bay solver can be exercised independently of the placement
    machinery.
    """
    bl_label = "Test Drop"
    bl_idname = "HB_FACE_FRAME_PT_test_drop"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_order = 10

    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.hb_face_frame

        col = layout.column(align=True)
        col.prop(scene_props, 'test_bay_qty', text="Bay Qty")

        box = layout.box()
        box.label(text="Drop with N bays", icon='ADD')
        col = box.column(align=True)

        for cabinet_name in ('Base Door', 'Upper', 'Tall'):
            op = col.operator('hb_face_frame.draw_cabinet', text=cabinet_name)
            op.cabinet_name = cabinet_name
            op.bay_qty = scene_props.test_bay_qty


classes = (
    HB_FACE_FRAME_PT_test_drop,
    HB_FACE_FRAME_PT_active_cabinet,
)


register, unregister = bpy.utils.register_classes_factory(classes)
