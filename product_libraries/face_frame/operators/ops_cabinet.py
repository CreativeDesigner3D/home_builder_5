import bpy

from .. import types_face_frame
from ...frameless.operators.ops_placement import toggle_cabinet_color


# ---------------------------------------------------------------------------
# Operator: drop a cabinet from the library
# ---------------------------------------------------------------------------
class hb_face_frame_OT_draw_cabinet(bpy.types.Operator):
    """Drop a face frame cabinet at the 3D cursor."""
    bl_idname = "hb_face_frame.draw_cabinet"
    bl_label = "Draw Face Frame Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(
        name="Cabinet Name",
        description="The face frame cabinet type to draw",
        default="",
    )  # type: ignore

    bay_qty: bpy.props.IntProperty(
        name="Bay Quantity",
        description="Number of bays to create on the cabinet (1-10)",
        default=1, min=1, max=10,
    )  # type: ignore

    def execute(self, context):
        # Thin wrapper over the modal placement operator. Lets the
        # catalog browser keep calling hb_face_frame.draw_cabinet while
        # the actual placement (cursor follow, wall snap, click-to-
        # commit) lives in hb_face_frame.place_cabinet. Same pattern
        # frameless uses (see ops_placement.py in that library).
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}
        bpy.ops.hb_face_frame.place_cabinet(
            'INVOKE_DEFAULT',
            cabinet_name=self.cabinet_name,
            bay_qty=self.bay_qty,
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: force a recalc on the active cabinet
# ---------------------------------------------------------------------------
class hb_face_frame_OT_recalculate_cabinet(bpy.types.Operator):
    """Force-recalculate the active face frame cabinet."""
    bl_idname = "hb_face_frame.recalculate_cabinet"
    bl_label = "Recalculate Face Frame Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def execute(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.report({'WARNING'}, "No face frame cabinet selected")
            return {'CANCELLED'}
        types_face_frame.recalculate_face_frame_cabinet(root)
        self.report({'INFO'}, f"Recalculated {root.name}")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: selection mode toggle (highlights matching objects, dims others)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_toggle_mode(bpy.types.Operator):
    """Apply visibility/highlighting for the current face frame selection mode.

    Mirrors the frameless toggle_mode operator but scoped to face-frame-tagged
    objects. Iterates scene objects (or the children of search_obj_name), and
    for each object decides whether it matches the active mode. Matching
    objects become solid + selectable; non-matching objects get hidden/dimmed.
    """
    bl_idname = "hb_face_frame.toggle_mode"
    bl_label = "Toggle Face Frame Selection Mode"
    bl_description = "Highlight objects matching the current face frame selection mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name", default="")  # type: ignore

    # Object-marker tags for cage-level modes
    MODE_TAGS = {
        'Cabinets':  types_face_frame.TAG_CABINET_CAGE,
        'Bays':      types_face_frame.TAG_BAY_CAGE,
        'Openings':  'IS_FACE_FRAME_OPENING_CAGE',     # Phase 3c
        'Interiors': 'IS_FACE_FRAME_INTERIOR_PART',    # Phase 3d
    }

    def _matches_mode(self, obj, mode):
        """Return True if obj should be highlighted in the given mode."""
        if mode == 'Face Frame':
            return obj.get('hb_part_role') in types_face_frame.FACE_FRAME_PART_ROLES
        if mode == 'Parts':
            return bool(obj.get('CABINET_PART'))
        tag = self.MODE_TAGS.get(mode)
        if tag is None:
            return False
        return tag in obj

    def _toggle_one(self, obj, mode):
        """Apply highlight/dim to a single object."""
        # Skip walls, doors, windows, cutting objects - they are not part of
        # the face frame hierarchy and shouldn't be touched by mode toggling.
        if any(t in obj for t in ('IS_WALL_BP', 'IS_ENTRY_DOOR_BP',
                                  'IS_WINDOW_BP', 'IS_CUTTING_OBJ')):
            return
        # Only touch objects that are part of a face frame cabinet, or are
        # generic cabinet parts/cages we know about. Avoids dimming arbitrary
        # scene geometry.
        if types_face_frame.find_cabinet_root(obj) is None:
            return

        if self._matches_mode(obj, mode):
            toggle_cabinet_color(obj, True, type_name=self.MODE_TAGS.get(mode, ''))
        else:
            toggle_cabinet_color(obj, False, type_name=self.MODE_TAGS.get(mode, ''))

    def execute(self, context):
        mode = context.scene.hb_face_frame.face_frame_selection_mode

        if self.search_obj_name and self.search_obj_name in bpy.data.objects:
            root_obj = bpy.data.objects[self.search_obj_name]
            self._toggle_one(root_obj, mode)
            for child in root_obj.children_recursive:
                self._toggle_one(child, mode)
        else:
            for obj in context.scene.objects:
                self._toggle_one(obj, mode)

        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: cabinet prompts popup (right-click -> Cabinet Prompts)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_cabinet_prompts(bpy.types.Operator):
    """Open the cabinet-wide properties dialog.

    Shows ONLY cabinet-wide settings (dimensions, construction, face
    frame defaults) - not per-bay properties. Per-bay editing goes
    through hb_face_frame.bay_prompts; per-mid-stile editing goes
    through hb_face_frame.mid_stile_prompts.
    """
    bl_idname = "hb_face_frame.cabinet_prompts"
    bl_label = "Cabinet Properties"
    bl_description = "Edit cabinet-wide properties (dimensions, construction, face frame defaults)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=320)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.layout.label(text="No face frame cabinet selected", icon='INFO')
            return
        ui_face_frame.draw_cabinet_wide(self.layout, root)


class hb_face_frame_OT_bay_prompts(bpy.types.Operator):
    """Open a focused properties dialog for a single bay.

    Operates on the active object - which must be a bay cage (i.e., the
    user right-clicked on a bay or has it selected). Shows only that
    bay's properties: width, height, depth, kick height, top offset,
    rail width overrides, remove_bottom, delete_bay.
    """
    bl_idname = "hb_face_frame.bay_prompts"
    bl_label = "Bay Properties"
    bl_description = "Edit a single bay's properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_BAY_CAGE))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        bay_obj = context.active_object
        if bay_obj is None or not bay_obj.get(types_face_frame.TAG_BAY_CAGE):
            self.layout.label(text="No bay selected", icon='INFO')
            return
        ui_face_frame.draw_bay_properties(self.layout, bay_obj)


class hb_face_frame_OT_mid_stile_prompts(bpy.types.Operator):
    """Open a focused properties dialog for a single mid stile.

    Operates on the active object - which must be a mid stile face frame
    part (hb_part_role == PART_ROLE_MID_STILE). Shows just that mid
    stile's width, extend up, and extend down.
    """
    bl_idname = "hb_face_frame.mid_stile_prompts"
    bl_label = "Mid Stile Properties"
    bl_description = "Edit a single mid stile's properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') == types_face_frame.PART_ROLE_MID_STILE

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=260)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        obj = context.active_object
        if obj is None or obj.get('hb_part_role') != types_face_frame.PART_ROLE_MID_STILE:
            self.layout.label(text="No mid stile selected", icon='INFO')
            return
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            self.layout.label(text="No cabinet root found", icon='ERROR')
            return
        msi = obj.get('hb_mid_stile_index', 0)
        ui_face_frame.draw_mid_stile_properties(self.layout, root, msi)


classes = (
    hb_face_frame_OT_draw_cabinet,
    hb_face_frame_OT_recalculate_cabinet,
    hb_face_frame_OT_toggle_mode,
    hb_face_frame_OT_cabinet_prompts,
    hb_face_frame_OT_bay_prompts,
    hb_face_frame_OT_mid_stile_prompts,
)


register, unregister = bpy.utils.register_classes_factory(classes)
