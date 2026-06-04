"""Face frame style management ops: add/remove for cabinet styles and door
styles. Assign / Update ops land in a follow-up alongside the per-part
material wiring.
"""
import bpy
from bpy.types import Operator

from ..props_hb_face_frame import get_style_props


def _next_unique_name(base, existing):
    """Return base, or base.001 / base.002 / ... if base is taken."""
    if base not in existing:
        return base
    i = 1
    while f"{base}.{i:03d}" in existing:
        i += 1
    return f"{base}.{i:03d}"


def _copy_door_style(src, dst):
    """Copy a door / drawer-front style's settings from src to dst (everything
    except the name). The catalog cascade (series -> shape -> panel) is copied
    FIRST so its update callbacks settle, then the remaining fields are copied
    so any unlocked / overridden widths land last and aren't clobbered by the
    cascade's re-derive."""
    cascade = ('front_series', 'front_shape', 'front_panel')
    for pid in cascade:
        try:
            setattr(dst, pid, getattr(src, pid))
        except Exception:
            pass
    for prop in src.bl_rna.properties:
        pid = prop.identifier
        if pid in ('rna_type', 'name') or pid in cascade or prop.is_readonly:
            continue
        try:
            setattr(dst, pid, getattr(src, pid))
        except Exception:
            pass


class hb_face_frame_OT_add_cabinet_style(Operator):
    """Add a new face frame cabinet style"""
    bl_idname = "hb_face_frame.add_cabinet_style"
    bl_label = "Add Cabinet Style"
    bl_description = "Add a new face frame cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ff = get_style_props(context)
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
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 1

    def execute(self, context):
        ff = get_style_props(context)
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
        ff = get_style_props(context)
        existing = [s.name for s in ff.door_styles]
        # New style duplicates the currently-selected one (its settings),
        # so adding is "copy + tweak"; the name gets a unique .NNN suffix.
        idx = ff.active_door_style_index
        src = ff.door_styles[idx] if 0 <= idx < len(ff.door_styles) else None
        base = src.name if src is not None else "Door Style"
        new_style = ff.door_styles.add()
        new_style.name = _next_unique_name(base, existing)
        if src is not None:
            _copy_door_style(src, new_style)
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
        ff = get_style_props(context)
        return len(ff.door_styles) > 1

    def execute(self, context):
        ff = get_style_props(context)
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


class hb_face_frame_OT_add_drawer_front_style(Operator):
    """Add a new face frame drawer front style"""
    bl_idname = "hb_face_frame.add_drawer_front_style"
    bl_label = "Add Drawer Front Style"
    bl_description = "Add a new face frame drawer front style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ff = get_style_props(context)
        existing = [s.name for s in ff.drawer_front_styles]
        # New style duplicates the currently-selected drawer front style.
        idx = ff.active_drawer_front_style_index
        src = ff.drawer_front_styles[idx] if 0 <= idx < len(ff.drawer_front_styles) else None
        base = src.name if src is not None else "Drawer Front Style"
        new_style = ff.drawer_front_styles.add()
        new_style.name = _next_unique_name(base, existing)
        if src is not None:
            _copy_door_style(src, new_style)
        ff.active_drawer_front_style_index = len(ff.drawer_front_styles) - 1
        self.report({'INFO'}, f"Added drawer front style: {new_style.name}")
        return {'FINISHED'}


class hb_face_frame_OT_remove_drawer_front_style(Operator):
    """Remove the active face frame drawer front style"""
    bl_idname = "hb_face_frame.remove_drawer_front_style"
    bl_label = "Remove Drawer Front Style"
    bl_description = "Remove the active drawer front style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(ff.drawer_front_styles) > 1

    def execute(self, context):
        ff = get_style_props(context)
        if len(ff.drawer_front_styles) <= 1:
            self.report({'WARNING'}, "At least one drawer front style must remain")
            return {'CANCELLED'}
        idx = ff.active_drawer_front_style_index
        if idx < 0 or idx >= len(ff.drawer_front_styles):
            return {'CANCELLED'}
        name = ff.drawer_front_styles[idx].name
        ff.drawer_front_styles.remove(idx)
        if ff.active_drawer_front_style_index >= len(ff.drawer_front_styles):
            ff.active_drawer_front_style_index = max(0, len(ff.drawer_front_styles) - 1)
        self.report({'INFO'}, f"Removed drawer front style: {name}")
        return {'FINISHED'}


class hb_face_frame_OT_assign_style_to_selected_cabinets(Operator):
    """Apply the active cabinet style to every selected face frame cabinet"""
    bl_idname = "hb_face_frame.assign_style_to_selected_cabinets"
    bl_label = "Assign Style"
    bl_description = "Apply the active cabinet style to every selected face frame cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 0 and len(context.selected_objects) > 0

    def execute(self, context):
        from .. import types_face_frame
        ff = get_style_props(context)
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
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 0

    def execute(self, context):
        ff = get_style_props(context)
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
        ff = get_style_props(context)
        return len(ff.door_styles) > 0 and len(context.selected_objects) > 0

    def execute(self, context):
        ff = get_style_props(context)
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
        ff = get_style_props(context)
        return len(ff.door_styles) > 0

    def execute(self, context):
        ff = get_style_props(context)
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


class hb_face_frame_OT_paint_assign_front_style(bpy.types.Operator):
    """Modal paint-assign: click fronts in the viewport to apply the active
    door / drawer-front style. The brush only paints MATCHING fronts -- a
    DOOR brush paints door fronts, a DRAWER brush paints drawer fronts; a
    wrong-role click is skipped. Stays active until Esc / right-click."""
    bl_idname = "hb_face_frame.paint_assign_front_style"
    bl_label = "Assign by Painting"
    bl_description = "Click fronts in the viewport to assign the active style"
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", "Paint door fronts with the active door style"),
               ('DRAWER', "Drawer", "Paint drawer fronts with the active drawer front style")],
        default='DOOR',
        options={'HIDDEN'},
    )  # type: ignore

    _DOOR_ROLES = {'DOOR'}
    _DRAWER_ROLES = {'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'}

    def _allowed_roles(self):
        return self._DRAWER_ROLES if self.kind == 'DRAWER' else self._DOOR_ROLES

    def _active_style(self, ff):
        if self.kind == 'DRAWER':
            pool, idx = ff.drawer_front_styles, ff.active_drawer_front_style_index
        else:
            pool, idx = ff.door_styles, ff.active_door_style_index
        return pool[idx] if 0 <= idx < len(pool) else None

    def _region_under_mouse(self, context, event):
        """The VIEW_3D WINDOW region + rv3d under the cursor, with region-
        relative coords. Window-absolute mouse coords are used so painting
        works regardless of which region the modal was started in (the
        operator is launched from the N-panel)."""
        x, y = event.mouse_x, event.mouse_y
        for area in context.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for region in area.regions:
                if (region.type == 'WINDOW'
                        and region.x <= x < region.x + region.width
                        and region.y <= y < region.y + region.height):
                    rv3d = area.spaces.active.region_3d
                    return region, rv3d, (x - region.x, y - region.y)
        return None, None, None

    def _front_under_cursor(self, context, event):
        from bpy_extras import view3d_utils
        region, rv3d, coord = self._region_under_mouse(context, event)
        if region is None:
            return None
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        depsgraph = context.evaluated_depsgraph_get()
        hit, loc, nrm, fidx, obj, mat = context.scene.ray_cast(depsgraph, origin, direction)
        if not hit or obj is None:
            return None
        # The hit may be the front itself or a child (e.g. a pull) -- walk up
        # to the nearest object carrying a front role.
        cur = obj
        while cur is not None:
            role = cur.get('hb_part_role')
            if role in self._DOOR_ROLES or role in self._DRAWER_ROLES:
                return cur
            cur = cur.parent
        return None

    def _paint(self, context, event):
        ff = get_style_props(context)
        style = self._active_style(ff)
        if style is None:
            return
        front = self._front_under_cursor(context, event)
        if front is None:
            return
        if front.get('hb_part_role') not in self._allowed_roles():
            context.workspace.status_text_set(
                f"Skipped: not a {self.kind.lower()} front  |  Esc / RMB to finish")
            return
        result = style.assign_style_to_front(front)
        if result is True:
            self._count += 1
            context.workspace.status_text_set(
                f"Applied '{style.name}' to {self._count} front(s)  |  Esc / RMB to finish")
        elif isinstance(result, str):
            context.workspace.status_text_set(result + "  |  Esc / RMB to finish")

    def _set_hover(self, context, front):
        """Highlight the assignable front under the cursor by selecting it (and
        making it active), so it's clear which part a click will assign. Only
        ONE hovered front is highlighted at a time; passing None clears it.
        Selection is restored when the tool finishes."""
        if front is self._hovered:
            return
        prev = self._hovered
        if prev is not None:
            try:
                prev.select_set(False)
            except Exception:
                pass
        if front is not None:
            try:
                front.select_set(True)
                context.view_layer.objects.active = front
            except Exception:
                pass
        self._hovered = front
        if context.area is not None:
            context.area.tag_redraw()

    def _hover(self, context, event):
        """Resolve + highlight the matching-role front under the cursor."""
        front = self._front_under_cursor(context, event)
        if front is not None and front.get('hb_part_role') not in self._allowed_roles():
            front = None  # wrong-role front won't be painted -> don't highlight
        self._set_hover(context, front)

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._finish(context)
        if event.type == 'MOUSEMOVE':
            self._hover(context, event)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._paint(context, event)
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def _restore_selection(self, context):
        """Restore the selection captured at invoke (the paint hover mutated it)."""
        for ob in list(context.selected_objects):
            try:
                ob.select_set(False)
            except Exception:
                pass
        for name in self._orig_sel:
            ob = bpy.data.objects.get(name)
            if ob is not None:
                try:
                    ob.select_set(True)
                except Exception:
                    pass
        context.view_layer.objects.active = (
            bpy.data.objects.get(self._orig_active) if self._orig_active else None)

    def _finish(self, context):
        self._set_hover(context, None)
        self._restore_selection(context)
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        if context.area is not None:
            context.area.tag_redraw()
        self.report({'INFO'}, f"Assigned {self.kind.lower()} style to {self._count} front(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from the 3D viewport")
            return {'CANCELLED'}
        if self._active_style(get_style_props(context)) is None:
            self.report({'WARNING'}, "No active style to assign")
            return {'CANCELLED'}
        self._count = 0
        self._hovered = None
        # Capture selection so the hover highlight can be undone on finish.
        self._orig_sel = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        self._orig_active = active.name if active else None
        context.window.cursor_modal_set('PAINT_BRUSH')
        context.workspace.status_text_set(
            "Paint-assign: hover highlights a front, click to assign  |  Esc / RMB to finish")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class hb_face_frame_OT_update_fronts_from_style(bpy.types.Operator):
    """Re-apply the active door OR drawer-front style (per kind) to every
    matching-role front already tagged with that style name. Pool-aware
    companion to the paint tool; role-scoped so a same-named style in the
    other pool is never touched."""
    bl_idname = "hb_face_frame.update_fronts_from_style"
    bl_label = "Update Fronts"
    bl_description = "Re-apply the active style to every front already tagged with that style name"
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", ""), ('DRAWER', "Drawer", "")],
        default='DOOR', options={'HIDDEN'},
    )  # type: ignore

    _DOOR_ROLES = {'DOOR'}
    _DRAWER_ROLES = {'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'}

    def execute(self, context):
        ff = get_style_props(context)
        if self.kind == 'DRAWER':
            pool, idx = ff.drawer_front_styles, ff.active_drawer_front_style_index
            roles = self._DRAWER_ROLES
        else:
            pool, idx = ff.door_styles, ff.active_door_style_index
            roles = self._DOOR_ROLES
        if idx < 0 or idx >= len(pool):
            self.report({'WARNING'}, "No active style")
            return {'CANCELLED'}
        ds = pool[idx]
        target = ds.name
        applied = 0
        for obj in context.scene.objects:
            if obj.get('DOOR_STYLE_NAME') != target:
                continue
            if obj.get('hb_part_role') not in roles:
                continue
            if ds.assign_style_to_front(obj) is True:
                applied += 1
        self.report({'INFO'}, f"Updated {applied} front(s) tagged '{target}'")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_add_cabinet_style,
    hb_face_frame_OT_remove_cabinet_style,
    hb_face_frame_OT_add_door_style,
    hb_face_frame_OT_remove_door_style,
    hb_face_frame_OT_add_drawer_front_style,
    hb_face_frame_OT_remove_drawer_front_style,
    hb_face_frame_OT_assign_style_to_selected_cabinets,
    hb_face_frame_OT_update_cabinets_from_style,
    hb_face_frame_OT_assign_door_style_to_selected_fronts,
    hb_face_frame_OT_update_fronts_from_door_style,
    hb_face_frame_OT_paint_assign_front_style,
    hb_face_frame_OT_update_fronts_from_style,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()


def unregister():
    _unregister_classes()
