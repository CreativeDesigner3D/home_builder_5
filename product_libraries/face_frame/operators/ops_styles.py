"""Face frame style management ops: add/remove for cabinet styles and door
styles. Assign / Update ops land in a follow-up alongside the per-part
material wiring.
"""
import bpy
from bpy.types import Operator

from ..props_hb_face_frame import (get_style_props,
                                   _reapply_materials_for_door_style)
from .. import style_options


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


def _copy_collection(src_coll, dst_coll):
    """Replace dst_coll's entries with copies of src_coll's (scalar props)."""
    dst_coll.clear()
    for src_item in src_coll:
        dst_item = dst_coll.add()
        for prop in src_item.bl_rna.properties:
            pid = prop.identifier
            if pid == 'rna_type' or prop.is_readonly:
                continue
            try:
                setattr(dst_item, pid, getattr(src_item, pid))
            except Exception:
                pass


def _copy_cabinet_style(src, dst):
    """Copy a cabinet style's settings from src to dst (everything except the
    name). The finish / overlay cascade is copied FIRST so its update
    callbacks settle (they rewrite the ff_* widths from the overlay table),
    then the remaining fields are copied so any customized widths / unlocks
    land last and aren't clobbered. Collection props (e.g. millwork_items)
    are cleared and re-added entry by entry."""
    cascade = ('finish_color', 'finish_overlay', 'door_overlay_type')
    for pid in cascade:
        try:
            setattr(dst, pid, getattr(src, pid))
        except Exception:
            pass
    # The per-style finish materials are lazily created and owned by each
    # style (get_finish_material names them "<style> Finish"). Copying the
    # pointer would make the new style share the source's material datablock,
    # so resolving the new style's finish recolors that shared material and
    # changes every cabinet using it. Leave these empty so the new style
    # builds its own; custom_material / custom_interior_material are the
    # user's explicit picks and stay shared.
    own_materials = ('material', 'material_rotated',
                     'interior_material', 'interior_material_rotated')
    for prop in src.bl_rna.properties:
        pid = prop.identifier
        if (pid in ('rna_type', 'name') or pid in cascade
                or pid in own_materials or prop.is_readonly):
            continue
        if prop.type == 'COLLECTION':
            _copy_collection(getattr(src, pid), getattr(dst, pid))
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
        # New style duplicates the currently-selected one so adding is
        # "copy + tweak" (matches the door / drawer-front style Add), which
        # is what dealers want for a second style in the same job.
        idx = ff.active_cabinet_style_index
        src = ff.cabinet_styles[idx] if 0 <= idx < len(ff.cabinet_styles) else None
        base = src.name if src is not None else "Style"
        new_style = ff.cabinet_styles.add()
        new_style.name = _next_unique_name(base, existing)
        if src is not None:
            _copy_cabinet_style(src, new_style)
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


class hb_face_frame_OT_move_cabinet_style(Operator):
    """Move the active cabinet style up or down in the list"""
    bl_idname = "hb_face_frame.move_cabinet_style"
    bl_label = "Move Cabinet Style"
    bl_description = ("Reorder the active cabinet style. 2D shop-drawing fill "
                      "colours follow list order -- the first style is white, "
                      "the rest take palette colours -- so moving a style "
                      "changes which one stays white")
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[('UP', "Up", "Move the style up"),
               ('DOWN', "Down", "Move the style down")],
        default='UP',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 1

    def execute(self, context):
        ff = get_style_props(context)
        count = len(ff.cabinet_styles)
        idx = ff.active_cabinet_style_index
        if idx < 0 or idx >= count:
            return {'CANCELLED'}
        new_idx = idx - 1 if self.direction == 'UP' else idx + 1
        if new_idx < 0 or new_idx >= count:
            return {'CANCELLED'}
        # Styles are referenced by name (STYLE_NAME on cabinets), so reordering
        # the pool is safe -- only the order-driven 2D colour assignment
        # (Spaces assign_style_colors, applied at page generation) changes.
        ff.cabinet_styles.move(idx, new_idx)
        ff.active_cabinet_style_index = new_idx
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
        else:
            # No style to copy: match the door-style seed default --
            # rail callouts are a drawer-rail concern.
            new_style.show_rail_annotation = False
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

        # Resolve every selected object up to its cabinet root OR wood-hood
        # cage; dedupe across both pools.
        from ...common import wood_hoods
        cab_roots = []
        hood_roots = []
        seen = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                if root.name not in seen:
                    seen.add(root.name)
                    cab_roots.append(root)
                continue
            hood = wood_hoods.find_hood_root(obj)
            if hood is not None and hood.name not in seen:
                seen.add(hood.name)
                hood_roots.append(hood)

        if not cab_roots and not hood_roots:
            self.report({'WARNING'}, "No face frame cabinets or wood hoods in selection")
            return {'CANCELLED'}

        for root in cab_roots:
            style.assign_style_to_cabinet(root)
        for hood in hood_roots:
            style.assign_style_to_hood(hood)
        n = len(cab_roots) + len(hood_roots)
        self.report({'INFO'}, f"Applied '{style.name}' to {n} item(s)")
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

        from ...common import wood_hoods
        # Walk the scene; match cabinets by cage marker and wood hoods by
        # APPLIANCE_TYPE, both gated on STYLE_NAME.
        cab_roots = []
        hood_roots = []
        for obj in context.scene.objects:
            if obj.get('STYLE_NAME') != target_name:
                continue
            if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
                cab_roots.append(obj)
            elif obj.get('APPLIANCE_TYPE') == 'HOOD':
                hood_roots.append(obj)
        if not cab_roots and not hood_roots:
            self.report({'INFO'}, f"No cabinets or hoods tagged with '{target_name}'")
            return {'FINISHED'}

        for root in cab_roots:
            style.assign_style_to_cabinet(root)
        for hood in hood_roots:
            style.assign_style_to_hood(hood)
        n = len(cab_roots) + len(hood_roots)
        self.report({'INFO'}, f"Updated {n} item(s) tagged '{target_name}'")
        return {'FINISHED'}


class hb_face_frame_OT_paint_assign_cabinet_style(bpy.types.Operator):
    """Modal paint-assign: click cabinets in the viewport to apply the active
    cabinet style. Each click resolves the part under the cursor up to its
    cabinet root and assigns the style to that one cabinet. Mirrors the
    front-style paint tool. Stays active until Esc / right-click."""
    bl_idname = "hb_face_frame.paint_assign_cabinet_style"
    bl_label = "Assign by Painting"
    bl_description = "Click cabinets in the viewport to assign the active cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 0

    def _active_style(self, ff):
        idx = ff.active_cabinet_style_index
        return ff.cabinet_styles[idx] if 0 <= idx < len(ff.cabinet_styles) else None

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

    def _cabinet_under_cursor(self, context, event):
        from bpy_extras import view3d_utils
        from .. import types_face_frame
        region, rv3d, coord = self._region_under_mouse(context, event)
        if region is None:
            return None
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        depsgraph = context.evaluated_depsgraph_get()
        hit, loc, nrm, fidx, obj, mat = context.scene.ray_cast(depsgraph, origin, direction)
        if not hit or obj is None:
            return None
        # The hit may be any cabinet or hood part -- resolve to the cabinet
        # root, else fall back to the wood-hood cage.
        root = types_face_frame.find_cabinet_root(obj)
        if root is not None:
            return root
        from ...common import wood_hoods
        return wood_hoods.find_hood_root(obj)

    def _paint(self, context, event):
        ff = get_style_props(context)
        style = self._active_style(ff)
        if style is None:
            return
        root = self._cabinet_under_cursor(context, event)
        if root is None:
            return
        if root.get('IS_FACE_FRAME_CABINET_CAGE'):
            style.assign_style_to_cabinet(root)
        elif root.get('APPLIANCE_TYPE') == 'HOOD':
            style.assign_style_to_hood(root)
        else:
            return
        if root.name not in self._painted:
            self._painted.add(root.name)
            self._count += 1
        context.workspace.status_text_set(
            f"Applied '{style.name}' to {self._count} item(s)  |  Esc / RMB to finish")

    def _set_hover(self, context, root):
        """Highlight the cabinet under the cursor by selecting its root, so it's
        clear which cabinet a click will assign. Only ONE hovered cabinet is
        highlighted at a time; passing None clears it. Selection is restored
        when the tool finishes."""
        if root is self._hovered:
            return
        prev = self._hovered
        if prev is not None:
            try:
                prev.select_set(False)
            except Exception:
                pass
        if root is not None:
            try:
                root.select_set(True)
                context.view_layer.objects.active = root
            except Exception:
                pass
        self._hovered = root
        if context.area is not None:
            context.area.tag_redraw()

    def _hover(self, context, event):
        self._set_hover(context, self._cabinet_under_cursor(context, event))

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
        self.report({'INFO'}, f"Assigned cabinet style to {self._count} cabinet(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from the 3D viewport")
            return {'CANCELLED'}
        if self._active_style(get_style_props(context)) is None:
            self.report({'WARNING'}, "No active cabinet style to assign")
            return {'CANCELLED'}
        self._count = 0
        self._painted = set()
        self._hovered = None
        # Capture selection so the hover highlight can be undone on finish.
        self._orig_sel = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        self._orig_active = active.name if active else None
        context.window.cursor_modal_set('PAINT_BRUSH')
        context.workspace.status_text_set(
            "Paint-assign: hover highlights a cabinet, click to assign  |  Esc / RMB to finish")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


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
            result = ds.assign_style_to_front(obj, record_override=True)
            if result is True:
                applied += 1
            elif isinstance(result, str):
                errors.append(f"{obj.name}: {result}")
            # False = not a styleable front, skip silently

        if applied == 0 and not errors:
            self.report({'WARNING'}, "No face frame fronts in selection")
            return {'CANCELLED'}
        # assign_style_to_front only builds the modifier + tags; surfaces
        # (grain rotation, Prep-for-Glass panel) come from the cabinet
        # material walk -- re-run it so an already-configured glass style
        # renders glass on assignment, not on the next unrelated recalc.
        if applied:
            _reapply_materials_for_door_style(ds, context)
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

        # Surfaces come from the cabinet material walk (see assign op).
        if applied:
            _reapply_materials_for_door_style(ds, context)
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

    _DOOR_ROLES = {'DOOR', 'PULLOUT_FRONT'}
    _DRAWER_ROLES = {'DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT'}

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
        result = style.assign_style_to_front(front, record_override=True)
        if result is True:
            self._count += 1
            # Surfaces come from the cabinet material walk (see assign
            # op) -- run it per click so a glass panel shows immediately.
            _reapply_materials_for_door_style(style, context)
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

    _DOOR_ROLES = {'DOOR', 'PULLOUT_FRONT'}
    _DRAWER_ROLES = {'DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT'}

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
        # Surfaces come from the cabinet material walk (see assign op).
        if applied:
            _reapply_materials_for_door_style(ds, context)
        self.report({'INFO'}, f"Updated {applied} front(s) tagged '{target}'")
        return {'FINISHED'}


class hb_face_frame_PG_temp_special_effect(bpy.types.PropertyGroup):
    """Scratch row for the Add Special Effects dialog checkboxes."""
    is_selected: bpy.props.BoolProperty(name="Is Selected")  # type: ignore


def _active_cabinet_style(context):
    """The cabinet style currently selected in the styles list, or None."""
    ff = get_style_props(context)
    if ff is None or not ff.cabinet_styles:
        return None
    idx = ff.active_cabinet_style_index
    if idx < 0 or idx >= len(ff.cabinet_styles):
        return None
    return ff.cabinet_styles[idx]


class hb_face_frame_OT_add_special_effects(Operator):
    """Add finish special effects to the active cabinet style. The offered
    list is the set compatible with the style's wood + color."""
    bl_idname = "hb_face_frame.add_special_effects"
    bl_label = "Add Special Effects"
    bl_description = ("Add finish special effects compatible with this style's "
                      "wood and color")
    bl_options = {'REGISTER', 'UNDO'}

    candidates: bpy.props.CollectionProperty(
        type=hb_face_frame_PG_temp_special_effect)  # type: ignore

    def invoke(self, context, event):
        self.candidates.clear()
        style = _active_cabinet_style(context)
        if style is None:
            self.report({'ERROR'}, "No active cabinet style.")
            return {'CANCELLED'}
        have = {e.name for e in style.special_effects}
        avail = [e for e in style_options.special_effects_for(
                    style.finish_wood, style.finish_color) if e not in have]
        if not avail:
            self.report({'INFO'},
                        "No more special effects available for this wood + color.")
            return {'CANCELLED'}
        for nm in avail:
            self.candidates.add().name = nm
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        col = self.layout.column(align=True)
        for c in self.candidates:
            col.prop(c, "is_selected", text=c.name)

    def execute(self, context):
        style = _active_cabinet_style(context)
        if style is None:
            return {'CANCELLED'}
        added = 0
        for c in self.candidates:
            if c.is_selected:
                style.special_effects.add().name = c.name
                added += 1
        self.report({'INFO'}, f"Added {added} special effect(s).")
        return {'FINISHED'}


class hb_face_frame_OT_remove_special_effect(Operator):
    """Remove a special effect from the active cabinet style."""
    bl_idname = "hb_face_frame.remove_special_effect"
    bl_label = "Remove Special Effect"
    bl_description = "Remove this special effect from the cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    effect_name: bpy.props.StringProperty(name="Name")  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context)
        if style is None:
            return {'CANCELLED'}
        for i, item in enumerate(style.special_effects):
            if item.name == self.effect_name:
                style.special_effects.remove(i)
                break
        return {'FINISHED'}


class hb_face_frame_OT_add_cabinet_extra_front_style(Operator):
    """Add an extra door- or drawer-front style row to the active cabinet
    style. The row is shown on the Style Section page (DOORS / DRAWERS); it
    documents an additional front style assigned to this style's cabinets in
    3D and has no geometric effect."""
    bl_idname = "hb_face_frame.add_cabinet_extra_front_style"
    bl_label = "Add Front Style"
    bl_description = ("Add an additional front style shown on the "
                      "Style Section page")
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", "Door style"),
               ('DRAWER', "Drawer", "Drawer front style")],
        default='DOOR')  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context)
        if style is None:
            self.report({'ERROR'}, "No active cabinet style.")
            return {'CANCELLED'}
        coll = (style.extra_drawer_front_styles if self.kind == 'DRAWER'
                else style.extra_door_styles)
        coll.add()
        return {'FINISHED'}


class hb_face_frame_OT_remove_cabinet_extra_front_style(Operator):
    """Remove an extra front-style row from the active cabinet style."""
    bl_idname = "hb_face_frame.remove_cabinet_extra_front_style"
    bl_label = "Remove Front Style"
    bl_description = "Remove this front style from the Style Section page"
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", "Door style"),
               ('DRAWER', "Drawer", "Drawer front style")],
        default='DOOR')  # type: ignore
    index: bpy.props.IntProperty(name="Index", default=-1)  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context)
        if style is None:
            return {'CANCELLED'}
        coll = (style.extra_drawer_front_styles if self.kind == 'DRAWER'
                else style.extra_door_styles)
        if 0 <= self.index < len(coll):
            coll.remove(self.index)
        return {'FINISHED'}


class hb_face_frame_OT_paint_part_material(bpy.types.Operator):
    """Modal part-paint: click parts (or any object) to paint the active
    cabinet style's Finish or Interior material onto them, or Reset a
    cabinet part to its automatic by-role material. For a cabinet part the
    choice is stored as a per-part override (hb_part_material_override) so it
    survives recalc; for any other object the material is assigned to its
    slots directly. 1 / 2 / 3 switch brush; Esc / RMB finishes."""
    bl_idname = "hb_face_frame.paint_part_material"
    bl_label = "Paint Part Material"
    bl_description = ("Click parts to paint the cabinet style's finish / "
                      "interior material onto them")
    bl_options = {'REGISTER', 'UNDO'}

    brush: bpy.props.EnumProperty(
        name="Brush",
        items=[
            ('FINISH',   "Finish",   "Paint the style's finish (exterior) material"),
            ('INTERIOR', "Interior", "Paint the style's interior material"),
            ('RESET',    "Reset",    "Return a cabinet part to its automatic material"),
        ],
        default='FINISH',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(ff.cabinet_styles) > 0

    def _active_style(self, ff):
        idx = ff.active_cabinet_style_index
        return ff.cabinet_styles[idx] if 0 <= idx < len(ff.cabinet_styles) else None

    def _region_under_mouse(self, context, event):
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

    def _object_under_cursor(self, context, event):
        from bpy_extras import view3d_utils
        region, rv3d, coord = self._region_under_mouse(context, event)
        if region is None:
            return None
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        depsgraph = context.evaluated_depsgraph_get()
        hit, loc, nrm, fidx, obj, mat = context.scene.ray_cast(
            depsgraph, origin, direction)
        if not hit or obj is None:
            return None
        # ray_cast returns the evaluated object; resolve to the original.
        return obj.original if hasattr(obj, 'original') else obj

    def _style_for(self, ff, obj):
        """A cabinet part follows its cabinet's STYLE_NAME so the immediate
        paint matches what recalc will re-apply; everything else uses the
        active style."""
        from .. import types_face_frame
        root = types_face_frame.find_cabinet_root(obj)
        if root is not None and root.get('STYLE_NAME'):
            name = root.get('STYLE_NAME')
            for cs in ff.cabinet_styles:
                if cs.name == name:
                    return cs
        return self._active_style(ff)

    @staticmethod
    def _assign_object_material(obj, mat):
        me = getattr(obj, 'data', None)
        if mat is None or me is None or not hasattr(me, 'materials'):
            return False
        if len(me.materials) == 0:
            me.materials.append(mat)
        else:
            for i in range(len(me.materials)):
                me.materials[i] = mat
        return True

    @staticmethod
    def _paint_manual_part_slots(obj, surface_mat, edge_mat):
        """Paint a part that was made editable (manual). Its GeoNode(s)
        were applied, so the cutpart surface inputs / Door Style modifier
        are gone and the materials live in the baked mesh's slots instead
        - writing GN inputs would silently no-op. Rewrite the slots: a
        slot holding a ROTATED (cross-grain) material takes the rotated
        edge material so grain direction is preserved, a glass panel slot
        is left alone, everything else takes the surface material."""
        me = getattr(obj, 'data', None)
        if surface_mat is None or me is None or not hasattr(me, 'materials'):
            return False
        if len(me.materials) == 0:
            me.materials.append(surface_mat)
            return True
        for i in range(len(me.materials)):
            cur = me.materials[i]
            name = cur.name if cur is not None else ''
            if name == 'Door Panel Glass':
                continue
            if edge_mat is not None and 'ROTATED' in name:
                me.materials[i] = edge_mat
            else:
                me.materials[i] = surface_mat
        return True

    _FRONT_ROLES = {'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT',
                    'FALSE_FRONT', 'TILT_OUT'}

    @staticmethod
    def _opening_for(obj):
        """Walk up to the front's stable opening cage (survives recalc)."""
        node = obj.parent
        while node is not None:
            if node.get('IS_FACE_FRAME_OPENING_CAGE'):
                return node
            node = node.parent
        return None

    def _paint(self, context, event):
        ff = get_style_props(context)
        obj = self._object_under_cursor(context, event)
        if obj is None:
            return
        from .. import types_face_frame
        # Always paint with the active (selected) style so a part picks up the
        # colour the user chose - consistent with painting a plain object.
        style = self._active_style(ff)
        if style is None:
            return
        is_part = bool(obj.get('CABINET_PART'))
        is_front = is_part and obj.get('hb_part_role') in self._FRONT_ROLES

        if self.brush == 'RESET':
            if is_front:
                opening = self._opening_for(obj)
                tgt = opening if opening is not None else obj
                for k in ('hb_front_material_override', 'hb_front_material_style'):
                    if k in tgt:
                        del tgt[k]
            elif is_part:
                for k in ('hb_part_material_override', 'hb_part_material_style'):
                    if k in obj:
                        del obj[k]
            if is_part:
                root = types_face_frame.find_cabinet_root(obj)
                if root is not None:
                    host = self._style_for(ff, obj)
                    if host is not None:
                        host._apply_materials_to_cabinet(root)
            # Non-cabinet objects have no automatic material; leave as-is.
        else:
            if self.brush == 'FINISH':
                mat, edge = style.get_finish_material()
            else:
                mat, edge = style.get_interior_material()
            if is_front:
                # Fronts are rebuilt each recalc, so the override is stored on
                # the stable opening cage; the material walk re-applies it to
                # the new front (incl. the 5-piece door modifier slots).
                opening = self._opening_for(obj)
                tgt = opening if opening is not None else obj
                tgt['hb_front_material_override'] = self.brush
                tgt['hb_front_material_style'] = style.name
                if obj.get('IS_MANUAL_PART'):
                    # Manual front: GN applied, paint the baked slots.
                    self._paint_manual_part_slots(obj, mat, edge)
                else:
                    style._set_part_surfaces(obj, mat, edge)
                    style._set_door_modifier_materials(obj, mat, edge)
            elif is_part:
                obj['hb_part_material_override'] = self.brush
                obj['hb_part_material_style'] = style.name
                if obj.get('IS_MANUAL_PART'):
                    # Manual part: GN applied, paint the baked slots.
                    self._paint_manual_part_slots(obj, mat, edge)
                else:
                    style._set_part_surfaces(obj, mat, edge)
            else:
                self._assign_object_material(obj, mat)

        if context.area is not None:
            context.area.tag_redraw()
        self._painted.add(obj.name)
        self._status(context, count=True)

    def _status(self, context, count=False):
        tail = (f" - {len(self._painted)} painted" if count else "")
        context.workspace.status_text_set(
            f"Paint Part [{self.brush.title()}]{tail}  |  "
            f"1 Finish  2 Interior  3 Reset  |  click parts  |  Esc / RMB to finish")

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._finish(context)
        if event.type in {'ONE', 'NUMPAD_1'} and event.value == 'PRESS':
            self.brush = 'FINISH'; self._status(context); return {'RUNNING_MODAL'}
        if event.type in {'TWO', 'NUMPAD_2'} and event.value == 'PRESS':
            self.brush = 'INTERIOR'; self._status(context); return {'RUNNING_MODAL'}
        if event.type in {'THREE', 'NUMPAD_3'} and event.value == 'PRESS':
            self.brush = 'RESET'; self._status(context); return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._paint(context, event)
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        if context.area is not None:
            context.area.tag_redraw()
        self.report({'INFO'}, f"Painted {len(self._painted)} part(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from the 3D viewport")
            return {'CANCELLED'}
        if self._active_style(get_style_props(context)) is None:
            self.report({'WARNING'}, "No active cabinet style")
            return {'CANCELLED'}
        self._painted = set()
        context.window.cursor_modal_set('PAINT_BRUSH')
        self._status(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


classes = (
    hb_face_frame_PG_temp_special_effect,
    hb_face_frame_OT_add_special_effects,
    hb_face_frame_OT_remove_special_effect,
    hb_face_frame_OT_add_cabinet_extra_front_style,
    hb_face_frame_OT_remove_cabinet_extra_front_style,
    hb_face_frame_OT_add_cabinet_style,
    hb_face_frame_OT_remove_cabinet_style,
    hb_face_frame_OT_move_cabinet_style,
    hb_face_frame_OT_add_door_style,
    hb_face_frame_OT_remove_door_style,
    hb_face_frame_OT_add_drawer_front_style,
    hb_face_frame_OT_remove_drawer_front_style,
    hb_face_frame_OT_assign_style_to_selected_cabinets,
    hb_face_frame_OT_update_cabinets_from_style,
    hb_face_frame_OT_paint_assign_cabinet_style,
    hb_face_frame_OT_paint_part_material,
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
