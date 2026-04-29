"""Face frame sidebar UI + shared draw helpers + selection awareness.

The sidebar is a parent panel with collapsible sub-panels:
    - Dimensions                (open by default)
    - Construction              (collapsed by default)
    - Face Frame Defaults       (collapsed by default)
    - Selection                 (dynamic - shows the active bay / stile / rail)
    - All Bays                  (collapsed by default)

Three popup operators provide focused editors that share these helpers:
    - hb_face_frame.cabinet_prompts    -> cabinet-wide only
    - hb_face_frame.bay_prompts        -> single bay
    - hb_face_frame.mid_stile_prompts  -> single mid stile

Adding a property to a section adds it everywhere because both the
sidebar sub-panels and the popups call the same draw_* helper.
"""
import bpy

from . import types_face_frame


# ---------------------------------------------------------------------------
# Selection helper
# ---------------------------------------------------------------------------
def find_active_selection(context):
    """Identify what the user is editing based on the active object.

    Returns a tuple keyed by kind:
        ('none',)
        ('cabinet',   root)
        ('bay',       bay_obj, root)
        ('mid_stile', stile_obj, msi, root)
        ('end_stile', stile_obj, role, root)
        ('rail',      rail_obj, role, root)
        ('other',     obj, root)
    """
    obj = context.active_object
    if obj is None:
        return ('none',)
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return ('none',)
    if obj == root:
        return ('cabinet', root)
    if obj.get(types_face_frame.TAG_BAY_CAGE):
        return ('bay', obj, root)
    role = obj.get('hb_part_role')
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        return ('mid_stile', obj, msi, root)
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        return ('rail', obj, role, root)
    if role in (types_face_frame.PART_ROLE_LEFT_STILE,
                types_face_frame.PART_ROLE_RIGHT_STILE):
        return ('end_stile', obj, role, root)
    return ('other', obj, root)


# ---------------------------------------------------------------------------
# Focused draw helpers - reused by sidebar sub-panels AND popup operators
# ---------------------------------------------------------------------------
def draw_identity(layout, root):
    """Cabinet name + type. Compact."""
    cab_props = root.face_frame_cabinet
    row = layout.row()
    row.label(text=root.name, icon='MESH_CUBE')
    row.label(text=cab_props.cabinet_type)


def draw_dimensions(layout, cab_props):
    col = layout.column(align=True)
    col.prop(cab_props, 'width', text="Width")
    col.prop(cab_props, 'depth', text="Depth")
    col.prop(cab_props, 'height', text="Height")


def draw_construction(layout, cab_props):
    """Material thickness, back thickness, toe kick (if applicable),
    stretchers (if applicable)."""
    col = layout.column(align=True)
    col.prop(cab_props, 'material_thickness', text="Material")
    col.prop(cab_props, 'back_thickness', text="Back")

    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.separator()
        col.label(text="Toe Kick")
        col.prop(cab_props, 'toe_kick_type', text="Type")
        col.prop(cab_props, 'toe_kick_height', text="Height")
        col.prop(cab_props, 'toe_kick_setback', text="Setback")

    if cab_props.cabinet_type in ('BASE', 'LAP_DRAWER'):
        col.separator()
        col.label(text="Top Stretchers")
        col.prop(cab_props, 'stretcher_width', text="Width")
        col.prop(cab_props, 'stretcher_thickness', text="Thickness")


def draw_face_frame_defaults(layout, cab_props):
    """Frame thickness + default stile and rail widths."""
    col = layout.column(align=True)
    col.prop(cab_props, 'face_frame_thickness', text="Frame Thickness")
    col.separator()
    col.prop(cab_props, 'left_stile_width', text="Left Stile")
    col.prop(cab_props, 'right_stile_width', text="Right Stile")
    col.separator()
    col.prop(cab_props, 'top_rail_width', text="Top Rail")
    col.prop(cab_props, 'bottom_rail_width', text="Bottom Rail")


def draw_bay_properties(layout, bay_obj):
    """All editable properties of a single bay. Used by both the
    sidebar Selection sub-panel and the bay_prompts popup."""
    bp = bay_obj.face_frame_bay
    layout.label(text=f"Bay {bp.bay_index + 1}", icon='MESH_CUBE')
    col = layout.column(align=True)

    # Width with unlock toggle - field disabled when auto, unlocked when manual
    width_row = col.row(align=True)
    field = width_row.row(align=True)
    field.enabled = bp.unlock_width
    field.prop(bp, 'width', text="Width")
    lock_icon = 'UNLOCKED' if bp.unlock_width else 'LOCKED'
    width_row.prop(bp, 'unlock_width', text="", icon=lock_icon)

    col.prop(bp, 'height', text="Height")
    col.prop(bp, 'depth', text="Depth")
    col.separator()
    col.prop(bp, 'kick_height', text="Kick Height")
    col.prop(bp, 'top_offset', text="Top Offset")
    col.separator()
    col.prop(bp, 'top_rail_width', text="Top Rail Width")
    col.prop(bp, 'bottom_rail_width', text="Bottom Rail Width")
    col.separator()
    col.prop(bp, 'remove_bottom', text="Remove Bottom")
    col.prop(bp, 'delete_bay', text="Delete Bay (cutout)")


def draw_mid_stile_properties(layout, root, msi):
    """All editable properties of a single mid stile."""
    cab_props = root.face_frame_cabinet
    if msi >= len(cab_props.mid_stile_widths):
        layout.label(text="Mid stile not found", icon='ERROR')
        return
    ms = cab_props.mid_stile_widths[msi]
    layout.label(text=f"Mid Stile {msi + 1}", icon='SNAP_EDGE')
    col = layout.column(align=True)
    col.prop(ms, 'width', text="Width")
    col.prop(ms, 'extend_up_amount', text="Extend Up")
    col.prop(ms, 'extend_down_amount', text="Extend Down")


def draw_end_stile_properties(layout, root, role):
    cab_props = root.face_frame_cabinet
    is_left = role == types_face_frame.PART_ROLE_LEFT_STILE
    side = "Left" if is_left else "Right"
    attr = 'left_stile_width' if is_left else 'right_stile_width'
    layout.label(text=f"{side} End Stile", icon='SNAP_EDGE')
    layout.prop(cab_props, attr, text="Width")


def draw_rail_properties(layout, root, rail_obj, role):
    """Rails are segment-keyed; the editable property is the bay's rail
    width override at the segment's start bay."""
    cab_props = root.face_frame_cabinet
    seg_start = rail_obj.get('hb_segment_start_bay', 0)
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if seg_start >= len(bays):
        layout.label(text="Rail's bay not found", icon='ERROR')
        return
    bp = bays[seg_start].face_frame_bay
    is_top = role == types_face_frame.PART_ROLE_TOP_RAIL
    label = "Top Rail" if is_top else "Bottom Rail"
    attr = 'top_rail_width' if is_top else 'bottom_rail_width'
    layout.label(text=f"{label} (Bay {seg_start + 1})", icon='SNAP_EDGE')
    layout.prop(bp, attr, text="Width")


def draw_all_bays_summary(layout, root):
    """Compact list of all bays with index and dims."""
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if not bays:
        layout.label(text="No bays", icon='INFO')
        return
    M_TO_IN = 39.3700787
    col = layout.column(align=True)
    for bay_obj in bays:
        bp = bay_obj.face_frame_bay
        row = col.row()
        w = bp.width * M_TO_IN
        h = bp.height * M_TO_IN
        d = bp.depth * M_TO_IN
        row.label(text=f"Bay {bp.bay_index + 1}")
        row.label(text=f"{w:.0f} x {h:.0f} x {d:.0f} in")


# ---------------------------------------------------------------------------
# Cabinet-wide content (used by both sidebar parent and cabinet_prompts popup)
# ---------------------------------------------------------------------------
def draw_cabinet_wide(layout, root):
    """Cabinet-level content only - identity, dimensions, construction,
    face frame defaults. Used by the cabinet_prompts popup. The sidebar
    splits these across sub-panels for collapsible browsing.
    """
    cab_props = root.face_frame_cabinet
    draw_identity(layout, root)
    layout.separator()
    box = layout.box()
    box.label(text="Dimensions", icon='ARROW_LEFTRIGHT')
    draw_dimensions(box, cab_props)
    box = layout.box()
    box.label(text="Construction", icon='MODIFIER')
    draw_construction(box, cab_props)
    box = layout.box()
    box.label(text="Face Frame Defaults", icon='MESH_GRID')
    draw_face_frame_defaults(box, cab_props)


# ---------------------------------------------------------------------------
# Parent panel - identity + recalc
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_active_cabinet(bpy.types.Panel):
    """Top-level face frame cabinet panel. Sub-panels register as children."""
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
        layout = self.layout
        draw_identity(layout, root)
        layout.operator('hb_face_frame.recalculate_cabinet',
                        text="Recalculate", icon='FILE_REFRESH')


# ---------------------------------------------------------------------------
# Sub-panels
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_dimensions(bpy.types.Panel):
    bl_label = "Dimensions"
    bl_idname = "HB_FACE_FRAME_PT_dimensions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_dimensions(self.layout, root.face_frame_cabinet)


class HB_FACE_FRAME_PT_construction(bpy.types.Panel):
    bl_label = "Construction"
    bl_idname = "HB_FACE_FRAME_PT_construction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_construction(self.layout, root.face_frame_cabinet)


class HB_FACE_FRAME_PT_face_frame_defaults(bpy.types.Panel):
    bl_label = "Face Frame Defaults"
    bl_idname = "HB_FACE_FRAME_PT_face_frame_defaults"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_face_frame_defaults(self.layout, root.face_frame_cabinet)


class HB_FACE_FRAME_PT_selection(bpy.types.Panel):
    """Dynamic content based on active object - shown only when something
    specific is selected (a bay, mid stile, end stile, or rail)."""
    bl_label = "Selection"
    bl_idname = "HB_FACE_FRAME_PT_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    @classmethod
    def poll(cls, context):
        kind = find_active_selection(context)[0]
        return kind in ('bay', 'mid_stile', 'end_stile', 'rail')

    def draw(self, context):
        sel = find_active_selection(context)
        kind = sel[0]
        if kind == 'bay':
            draw_bay_properties(self.layout, sel[1])
        elif kind == 'mid_stile':
            draw_mid_stile_properties(self.layout, sel[3], sel[2])
        elif kind == 'end_stile':
            draw_end_stile_properties(self.layout, sel[3], sel[2])
        elif kind == 'rail':
            draw_rail_properties(self.layout, sel[3], sel[1], sel[2])


class HB_FACE_FRAME_PT_all_bays(bpy.types.Panel):
    bl_label = "All Bays"
    bl_idname = "HB_FACE_FRAME_PT_all_bays"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_all_bays_summary(self.layout, root)


classes = (
    HB_FACE_FRAME_PT_active_cabinet,
    HB_FACE_FRAME_PT_dimensions,
    HB_FACE_FRAME_PT_construction,
    HB_FACE_FRAME_PT_face_frame_defaults,
    HB_FACE_FRAME_PT_selection,
    HB_FACE_FRAME_PT_all_bays,
)


register, unregister = bpy.utils.register_classes_factory(classes)
