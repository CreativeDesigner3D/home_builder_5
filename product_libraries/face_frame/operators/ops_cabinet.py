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
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}

        cls = types_face_frame.get_cabinet_class(self.cabinet_name)
        if cls is None:
            self.report({'WARNING'}, f"Unknown cabinet name: {self.cabinet_name}")
            return {'CANCELLED'}

        cabinet = cls()
        cabinet.create(self.cabinet_name, bay_qty=self.bay_qty)

        cursor_loc = context.scene.cursor.location
        cabinet.obj.location.x = cursor_loc.x
        cabinet.obj.location.y = cursor_loc.y
        cab_props = cabinet.obj.face_frame_cabinet
        if cab_props.cabinet_type != 'UPPER':
            cabinet.obj.location.z = cursor_loc.z

        for obj in context.selected_objects:
            obj.select_set(False)
        cabinet.obj.select_set(True)
        context.view_layer.objects.active = cabinet.obj

        # Apply the active selection mode so the new cabinet's parts/cages
        # have the right visibility (cages hidden, cabinet root selectable
        # by default in 'Cabinets' mode).
        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=cabinet.obj.name)
            # toggle_mode deselects everything; re-select just the new cabinet
            cabinet.obj.select_set(True)
            context.view_layer.objects.active = cabinet.obj
        except RuntimeError:
            pass  # poll/context issue - safe to skip

        self.report({'INFO'}, f"Created {self.cabinet_name} ({cls.__name__})")
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
    """Open the face frame cabinet properties dialog.

    Same draw layout as the sidebar panel (HB_FACE_FRAME_PT_active_cabinet),
    just rendered as a popup. Property changes fire the cabinet's update
    callbacks live - no separate apply step needed.
    """
    bl_idname = "hb_face_frame.cabinet_prompts"
    bl_label = "Cabinet Properties"
    bl_description = "Edit face frame cabinet properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        # Lazy import to avoid circular import at module load
        from .. import ui_face_frame
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.layout.label(text="No face frame cabinet selected", icon='INFO')
            return
        ui_face_frame.draw_cabinet_properties(self.layout, root)


classes = (
    hb_face_frame_OT_draw_cabinet,
    hb_face_frame_OT_recalculate_cabinet,
    hb_face_frame_OT_toggle_mode,
    hb_face_frame_OT_cabinet_prompts,
)


register, unregister = bpy.utils.register_classes_factory(classes)
