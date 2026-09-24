"""Face frame style management ops: add/remove for cabinet styles and door
styles. Assign / Update ops land in a follow-up alongside the per-part
material wiring.
"""
import bpy
from bpy.types import Operator

from ..props_hb_face_frame import (get_style_props,
                                   _reapply_materials_for_door_style)
from .. import props_hb_face_frame
from .. import style_options


def _refresh_style_colors(context):
    """Repaint the viewport when style colours are showing.

    A cabinet's colour comes from its style's place in the pool, so
    adding, removing, reordering or reassigning a style changes what the
    scene should look like. No-op while the option is off.
    """
    try:
        if get_style_props(context).show_style_colors:
            props_hb_face_frame.apply_style_colors(context)
    except Exception:
        pass


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
    # rename_anchor is the style's OWN previous name (see the cabinet-style
    # copy above): copying it would make the copy's first rename re-tag
    # every front of the SOURCE style.
    for prop in src.bl_rna.properties:
        pid = prop.identifier
        if (pid in ('rna_type', 'name', 'rename_anchor') or pid in cascade
                or prop.is_readonly):
            continue
        try:
            setattr(dst, pid, getattr(src, pid))
        except Exception:
            pass
    dst.rename_anchor = dst.name


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
    # rename_anchor is the style's OWN previous name, used to re-tag
    # assigned cabinets when it is renamed. Copying it would point the
    # new style back at the source's name, so the first rename of the
    # copy would silently re-stamp every cabinet assigned to the SOURCE
    # style -- invisible until the next rebuild repainted them.
    for prop in src.bl_rna.properties:
        pid = prop.identifier
        if (pid in ('rna_type', 'name', 'rename_anchor') or pid in cascade
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
        # is what users want for a second style in the same job.
        idx = ff.active_cabinet_style_index
        src = ff.cabinet_styles[idx] if 0 <= idx < len(ff.cabinet_styles) else None
        base = src.name if src is not None else "Style"
        new_style = ff.cabinet_styles.add()
        new_style.name = _next_unique_name(base, existing)
        if src is not None:
            _copy_cabinet_style(src, new_style)
        # Anchor the copy to its OWN name so its first rename only
        # re-tags cabinets assigned to IT, never the style it came from.
        new_style.rename_anchor = new_style.name
        ff.active_cabinet_style_index = len(ff.cabinet_styles) - 1
        _refresh_style_colors(context)
        self.report({'INFO'}, f"Added cabinet style: {new_style.name}")
        return {'FINISHED'}


class hb_face_frame_OT_remove_cabinet_style(Operator):
    """Remove the active face frame cabinet style"""
    bl_idname = "hb_face_frame.remove_cabinet_style"
    bl_label = "Remove Cabinet Style"
    bl_description = "Remove the active cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    # Callers that show a style other than the active one (the settings
    # dialog opens on the row whose gear was clicked) pass the index they
    # are showing; -1 keeps the old behaviour of removing the active one.
    index: bpy.props.IntProperty(default=-1)  # type: ignore

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
        idx = self.index if self.index >= 0 else ff.active_cabinet_style_index
        if idx < 0 or idx >= len(ff.cabinet_styles):
            return {'CANCELLED'}
        name = ff.cabinet_styles[idx].name
        ff.cabinet_styles.remove(idx)
        # Removing a row above the active one slides the rest up, so the
        # stored index would land on the wrong style.
        if idx < ff.active_cabinet_style_index:
            ff.active_cabinet_style_index -= 1
        if ff.active_cabinet_style_index >= len(ff.cabinet_styles):
            ff.active_cabinet_style_index = max(0, len(ff.cabinet_styles) - 1)
        _refresh_style_colors(context)
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
        # (the host add-on's style colors, applied at page generation) changes.
        ff.cabinet_styles.move(idx, new_idx)
        ff.active_cabinet_style_index = new_idx
        _refresh_style_colors(context)
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


# ---------------------------------------------------------------------------
# Front styles in use
# ---------------------------------------------------------------------------
# A cabinet style names its door and drawer front styles; a front can
# carry one of its own (painted on, kept on its opening or its appliance
# panel section). Removing a style that is still named anywhere asks for
# the one to use instead, so nothing is left pointing at a name that is
# gone.

_FRONT_POOLS = {
    'DOOR': ('door_styles', 'active_door_style_index', 'door_style',
             'extra_door_styles', 'hb_front_door_style'),
    'DRAWER': ('drawer_front_styles', 'active_drawer_front_style_index',
               'drawer_front_style', 'extra_drawer_front_styles',
               'hb_front_drawer_style'),
}


def _front_roles(kind):
    ds = props_hb_face_frame.Face_Frame_Door_Style
    return (ds._DOOR_FRONT_ROLES if kind == 'DOOR'
            else ds._DRAWER_FRONT_ROLES)


def front_style_usage(ff, kind, name):
    """(cabinet style names, count of fronts) using front style `name`."""
    _pool, _idx, prop, extras, _ovr = _FRONT_POOLS[kind]
    styles = [cs.name for cs in ff.cabinet_styles
              if getattr(cs, prop, None) == name
              or any(e.style == name for e in getattr(cs, extras, ()))]
    roles = _front_roles(kind)
    fronts = sum(1 for obj in bpy.data.objects
                 if obj.users_scene
                 and obj.get('DOOR_STYLE_NAME') == name
                 and obj.get('hb_part_role') in roles)
    return styles, fronts


def _replace_front_style(ff, kind, old, new):
    """Point everything that names front style `old` at `new`."""
    _pool, _idx, prop, extras, ovr = _FRONT_POOLS[kind]
    for cs in ff.cabinet_styles:
        for e in getattr(cs, extras, ()):
            if e.style == old:
                e.style = new
        if getattr(cs, prop, None) == old:
            setattr(cs, prop, new)      # restyles its cabinets
    new_style = next((ds for ds in getattr(ff, _pool) if ds.name == new),
                     None)
    roles = _front_roles(kind)
    for obj in list(bpy.data.objects):
        if obj.get(ovr) == old:
            obj[ovr] = new              # an opening's own pick
        props = getattr(obj, 'appliance_panels', None)
        for sec in (getattr(props, 'sections', ()) or ()):
            if sec.get(ovr) == old:
                sec[ovr] = new          # an appliance panel's own pick
        if (new_style is not None and obj.users_scene
                and obj.get('DOOR_STYLE_NAME') == old
                and obj.get('hb_part_role') in roles):
            new_style.assign_style_to_front(obj)


def _replacement_items(self, context):
    ff = get_style_props(context)
    pool = getattr(ff, _FRONT_POOLS[self.kind][0])
    idx = getattr(ff, _FRONT_POOLS[self.kind][1])
    doomed = pool[idx].name if 0 <= idx < len(pool) else None
    items = [(ds.name, ds.name, "") for ds in pool if ds.name != doomed]
    return items or [('NONE', "(none)", "")]


class _RemoveFrontStyle:
    """Remove the active front style. One still in use asks which style
    takes its place first."""
    bl_options = {'REGISTER', 'UNDO'}
    KIND = 'DOOR'

    replacement: bpy.props.EnumProperty(
        name="Use Instead", items=_replacement_items)  # type: ignore

    @property
    def kind(self):
        return self.KIND

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return len(getattr(ff, _FRONT_POOLS[cls.KIND][0])) > 1

    def _doomed(self, context):
        ff = get_style_props(context)
        pool = getattr(ff, _FRONT_POOLS[self.KIND][0])
        idx = getattr(ff, _FRONT_POOLS[self.KIND][1])
        return ff, pool, idx, (pool[idx] if 0 <= idx < len(pool) else None)

    def invoke(self, context, event):
        ff, _pool, _idx, doomed = self._doomed(context)
        if doomed is None:
            return {'CANCELLED'}
        styles, fronts = front_style_usage(ff, self.KIND, doomed.name)
        if not styles and not fronts:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        ff, _pool, _idx, doomed = self._doomed(context)
        if doomed is None:
            return
        styles, fronts = front_style_usage(ff, self.KIND, doomed.name)
        col = self.layout.column()
        col.label(text="%s is still in use:" % doomed.name, icon='ERROR')
        for name in styles[:6]:
            col.label(text="    Cabinet style %s" % name)
        if len(styles) > 6:
            col.label(text="    and %d more" % (len(styles) - 6))
        if fronts:
            col.label(text="    %d front%s given it by hand"
                      % (fronts, "" if fronts == 1 else "s"))
        col.separator()
        col.prop(self, 'replacement')

    def execute(self, context):
        ff, pool, idx, doomed = self._doomed(context)
        if doomed is None or len(pool) <= 1:
            self.report({'WARNING'}, "At least one style must remain")
            return {'CANCELLED'}
        name = doomed.name
        styles, fronts = front_style_usage(ff, self.KIND, name)
        if styles or fronts:
            new = self.replacement
            if new in ('', 'NONE', name) or not any(ds.name == new
                                                    for ds in pool):
                self.report({'WARNING'}, "Pick the style to use instead")
                return {'CANCELLED'}
            _replace_front_style(ff, self.KIND, name, new)
        # The replacement may have shifted what idx points at.
        idx = next((i for i, ds in enumerate(pool) if ds.name == name), -1)
        if idx < 0:
            return {'CANCELLED'}
        pool.remove(idx)
        index_prop = _FRONT_POOLS[self.KIND][1]
        if getattr(ff, index_prop) >= len(pool):
            setattr(ff, index_prop, max(0, len(pool) - 1))
        self.report({'INFO'}, "Removed %s" % name)
        return {'FINISHED'}


class hb_face_frame_OT_remove_door_style(_RemoveFrontStyle, Operator):
    """Remove the active door style. One still in use asks which style
    takes its place"""
    bl_idname = "hb_face_frame.remove_door_style"
    bl_label = "Remove Door Style"
    bl_description = "Remove the active door style"
    KIND = 'DOOR'


class hb_face_frame_OT_remove_drawer_front_style(_RemoveFrontStyle, Operator):
    """Remove the active drawer front style. One still in use asks which
    style takes its place"""
    bl_idname = "hb_face_frame.remove_drawer_front_style"
    bl_label = "Remove Drawer Front Style"
    bl_description = "Remove the active drawer front style"
    KIND = 'DRAWER'


# ---------------------------------------------------------------------------
# New from the catalog, and the matching drawer front
# ---------------------------------------------------------------------------

def new_front_style(context, kind, series, shape=None, panel=None):
    """Add a front style built from a catalog pick and make it the
    pick. Other settings (profiles, material) come from the style that
    was picked, as NEW does. Returns the new style."""
    ff = get_style_props(context)
    pool_name, index_prop = _FRONT_POOLS[kind][0], _FRONT_POOLS[kind][1]
    pool = getattr(ff, pool_name)
    src_idx = getattr(ff, index_prop)
    src = pool[src_idx] if 0 <= src_idx < len(pool) else None
    existing = [ds.name for ds in pool]
    style = pool.add()
    style.name = _next_unique_name(
        " ".join(x for x in (series, shape, panel) if x) or "Style",
        existing)
    if src is not None:
        _copy_door_style(src, style)
    # The cascade settles each level before the next is set.
    for prop, value in (('front_series', series), ('front_shape', shape),
                        ('front_panel', panel)):
        if value:
            try:
                setattr(style, prop, value)
            except Exception:
                pass
    setattr(ff, index_prop, len(pool) - 1)
    return style


class hb_face_frame_OT_new_front_style(Operator):
    """Make a front style from a catalog series, shape and panel"""
    bl_idname = "hb_face_frame.new_front_style"
    bl_label = "New Front Style"
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", ""), ('DRAWER', "Drawer Front", "")])  # type: ignore
    series: bpy.props.StringProperty()  # type: ignore
    shape: bpy.props.StringProperty()  # type: ignore
    panel: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        if not self.series:
            return {'CANCELLED'}
        style = new_front_style(context, self.kind, self.series,
                                self.shape or None, self.panel or None)
        self.report({'INFO'}, "Added %s" % style.name)
        return {'FINISHED'}


class hb_face_frame_OT_matching_drawer_front(Operator):
    """Make the drawer front style that goes with the picked door style:
    the same series, shape and panel from the drawer catalog, following
    the door's rail width where the front is tall enough"""
    bl_idname = "hb_face_frame.matching_drawer_front"
    bl_label = "Make Matching Drawer Front"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return 0 <= ff.active_door_style_index < len(ff.door_styles)

    def execute(self, context):
        ff = get_style_props(context)
        door = ff.door_styles[ff.active_door_style_index]
        from .. import style_options
        series = door.front_series
        if series not in style_options.DRAWER_SERIES:
            self.report({'WARNING'}, "%s has no drawer fronts in the catalog"
                        % series)
            return {'CANCELLED'}
        shapes = style_options.door_shapes(series, drawer=True)
        shape = door.front_shape if door.front_shape in shapes else (
            shapes[0] if shapes else None)
        panels = (style_options.door_panels(series, shape, drawer=True)
                  if shape else [])
        panel = door.front_panel if door.front_panel in panels else (
            panels[0] if panels else None)
        style = new_front_style(context, 'DRAWER', series, shape, panel)
        try:
            style.match_door_rail_width = True
        except Exception:
            pass
        self.report({'INFO'}, "Added drawer front %s" % style.name)
        return {'FINISHED'}


# The New from Catalog steps, kept here for the manager page to draw:
# {'kind': 'DOOR' | 'DRAWER', 'series': str | None, 'shape': str | None}
# while a pick is under way, else None.
front_wizard = None


class hb_face_frame_OT_front_style_wizard(Operator):
    """One step of making a front style from the catalog"""
    bl_idname = "hb_face_frame.front_style_wizard"
    bl_label = "New from Catalog"
    bl_options = {'INTERNAL'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", ""), ('DRAWER', "Drawer Front", "")])  # type: ignore
    step: bpy.props.EnumProperty(items=[
        ('START', "Start", ""), ('SERIES', "Series", ""),
        ('SHAPE', "Shape", ""), ('PANEL', "Panel", ""),
        ('BACK', "Back", ""), ('CANCEL', "Cancel", "")])  # type: ignore
    value: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        global front_wizard
        from .. import style_options
        drawer = self.kind == 'DRAWER'
        w = front_wizard
        if self.step == 'START':
            front_wizard = {'kind': self.kind, 'series': None, 'shape': None}
        elif self.step == 'CANCEL' or w is None:
            front_wizard = None
        elif self.step == 'BACK':
            if w['shape'] is not None:
                w['shape'] = None
            elif w['series'] is not None:
                w['series'] = None
            else:
                front_wizard = None
        elif self.step == 'SERIES':
            w['series'] = self.value
            shapes = style_options.door_shapes(self.value, drawer=drawer)
            if len(shapes) <= 1:
                # One shape: nothing to choose.
                w['shape'] = shapes[0] if shapes else ""
        elif self.step == 'SHAPE':
            w['shape'] = self.value
        elif self.step == 'PANEL':
            new_front_style(context, self.kind, w['series'],
                            w['shape'] or None, self.value or None)
            front_wizard = None
        # One panel left to pick: take it.
        w = front_wizard
        if w is not None and w['series'] and w['shape'] is not None:
            panels = style_options.door_panels(w['series'], w['shape'],
                                               drawer=drawer)
            if len(panels) <= 1:
                new_front_style(context, self.kind, w['series'],
                                w['shape'] or None,
                                panels[0] if panels else None)
                front_wizard = None
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
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
        bare_parts = []
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
                continue
            part = _bare_part_for(obj)
            if part is not None and part.name not in seen:
                seen.add(part.name)
                bare_parts.append(part)

        if not cab_roots and not hood_roots and not bare_parts:
            self.report({'WARNING'}, "No face frame cabinets or wood hoods in selection")
            return {'CANCELLED'}

        for root in cab_roots:
            style.assign_style_to_cabinet(root)
        for hood in hood_roots:
            # Stamp the style first, then rebuild a built wood hood so its
            # static doors pick up the new style's door construction.
            style.assign_style_to_hood(hood)
            wood_hoods.rebuild_built_hood(hood)
        for part in bare_parts:
            _apply_style_finish_to_bare_part(style, part)
        n = len(cab_roots) + len(hood_roots) + len(bare_parts)
        _refresh_style_colors(context)
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
            # Built wood hoods rebuild so their static doors pick up the
            # style's door construction (the rebuild re-pushes the
            # finish); unbuilt hoods just take the finish.
            if not wood_hoods.rebuild_built_hood(hood):
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
        # root, else fall back to the wood-hood cage, else a bare part
        # (Wood Top / Misc Part) standing on its own.
        root = types_face_frame.find_cabinet_root(obj)
        if root is not None:
            return root
        from ...common import wood_hoods
        hood = wood_hoods.find_hood_root(obj)
        if hood is not None:
            return hood
        return _bare_part_for(obj)

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
            _refresh_style_colors(context)
        elif root.get('APPLIANCE_TYPE') == 'HOOD':
            # Stamp the style, then rebuild a built wood hood so its
            # static doors pick up the new style's door construction.
            style.assign_style_to_hood(root)
            from ...common import wood_hoods
            wood_hoods.rebuild_built_hood(root)
        elif root.get('CABINET_PART'):
            # Bare part (Wood Top / Misc Part) with no cabinet above it.
            if not _apply_style_finish_to_bare_part(style, root):
                return
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


def _front_kind(front, door_roles, drawer_roles):
    """'DOOR' / 'DRAWER' / None for a front object. Role-based, except that
    a false face frame end's fixed fronts stand in for door panels and so
    count as door fronts (types_face_frame.front_reads_door_pool)."""
    from .. import types_face_frame
    role = front.get('hb_part_role')
    if role in door_roles:
        return 'DOOR'
    if role in drawer_roles:
        return ('DOOR' if types_face_frame.front_reads_door_pool(front)
                else 'DRAWER')
    return None


class _paint_front_brush:
    """Shared machinery for the viewport paint brushes (front-style assign
    and per-door hardware callouts): region/ray resolution, hover
    highlight, the modal loop, and selection restore. Deliberately a
    plain mixin, NOT an Operator subclass -- registering an Operator
    that subclasses an already-registered Operator corrupts the parent's
    RNA callbacks (its invoke/execute silently stop being called), so
    both paint operators derive from this plus bpy.types.Operator."""

    _DOOR_ROLES = {'DOOR', 'PULLOUT_FRONT'}
    _DRAWER_ROLES = {'DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT'}

    def _front_kind(self, front):
        """'DOOR' / 'DRAWER' / None for a front object. Role-based, except
        that a false face frame end's fixed fronts count as door fronts so
        they take the Door Style (types_face_frame.front_reads_door_pool)."""
        return _front_kind(front, self._DOOR_ROLES, self._DRAWER_ROLES)

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

    def _paints(self, front):
        """True when this brush would paint the given front. Role-based by
        default; the front-style brush overrides it to match on front KIND
        so a false face frame end's fronts take the door brush."""
        return front.get('hb_part_role') in self._allowed_roles()

    def _hover(self, context, event):
        """Resolve + highlight the matching front under the cursor."""
        front = self._front_under_cursor(context, event)
        if front is not None and not self._paints(front):
            front = None  # a front this brush skips -> don't highlight
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


class hb_face_frame_OT_paint_assign_front_style(_paint_front_brush, bpy.types.Operator):
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


    def _paints(self, front):
        return self._front_kind(front) == self.kind

    def _active_style(self, ff):
        if self.kind == 'DRAWER':
            pool, idx = ff.drawer_front_styles, ff.active_drawer_front_style_index
        else:
            pool, idx = ff.door_styles, ff.active_door_style_index
        return pool[idx] if 0 <= idx < len(pool) else None

    def _paint(self, context, event):
        ff = get_style_props(context)
        style = self._active_style(ff)
        if style is None:
            return
        front = self._front_under_cursor(context, event)
        if front is None:
            return
        if not self._paints(front):
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


class hb_face_frame_OT_paint_door_hardware(_paint_front_brush, bpy.types.Operator):
    """Modal paint for hardware callouts: click DOOR fronts to add one
    callout (RC / TL / FR) to that door's opening, Ctrl+Click to remove
    it. The door style's checkboxes only DECLARE the callout for the
    job (the style-page legend line); which doors actually carry the
    letter mark on the drawings is painted here -- hardware lives on
    specific doors, not every door of a style. Esc / right-click
    finishes. Stamps persist on the opening cage (fronts are rebuilt
    every recalc) keyed per leaf, so clicking one door of a pair leaves
    its partner alone, and are read by downstream 2D consumers."""
    bl_idname = "hb_face_frame.paint_door_hardware"
    bl_label = "Assign Doors"
    bl_description = ("Click doors in the viewport to add this hardware "
                      "callout per door; Ctrl+Click removes it")
    bl_options = {'REGISTER', 'UNDO'}

    callout: bpy.props.EnumProperty(
        items=[('RC', "Restrictor Clips", ""),
               ('TL', "Touch Latches", ""),
               ('FR', "Finger Route", "")],
        default='TL', options={'HIDDEN'},
    )  # type: ignore

    def _allowed_roles(self):
        return {'DOOR'}

    def _paint(self, context, event):
        front = self._front_under_cursor(context, event)
        if front is None:
            return
        if front.get('hb_part_role') != 'DOOR':
            context.workspace.status_text_set(
                "Skipped: not a door  |  Esc / RMB to finish")
            return
        from . import ops_part_commands
        from .. import props_hb_face_frame as _props
        store = ops_part_commands._frame_store(front)
        # Click APPLIES, Ctrl+Click removes -- never a blind toggle, so
        # painting a run of doors that are already marked is a no-op
        # rather than a switch-off.
        state = not event.ctrl
        hw = _props.front_door_hw(front, store)
        if hw[self.callout] == state:
            context.workspace.status_text_set(
                f"{self.callout} already {'ON' if state else 'OFF'}: "
                f"{front.name}  |  Esc / RMB to finish")
            return
        hw[self.callout] = state
        _props.set_front_door_hw(front, hw, store)
        self._count += 1
        context.workspace.status_text_set(
            f"{self.callout} {'ON' if state else 'OFF'}: {front.name}  |  "
            f"{self._count} change(s)  |  Click = add, Ctrl+Click = "
            "remove, Esc / RMB to finish")

    def _finish(self, context):
        self._set_hover(context, None)
        self._restore_selection(context)
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        if context.area is not None:
            context.area.tag_redraw()
        self.report({'INFO'},
                    f"Toggled {self.callout} on {self._count} door(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from the 3D viewport")
            return {'CANCELLED'}
        self._count = 0
        self._hovered = None
        self._orig_sel = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        self._orig_active = active.name if active else None
        context.window.cursor_modal_set('PAINT_BRUSH')
        context.workspace.status_text_set(
            f"Paint {self.callout} callouts: Click a door = add, "
            "Ctrl+Click = remove  |  Esc / RMB to finish")
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
        else:
            pool, idx = ff.door_styles, ff.active_door_style_index
        if idx < 0 or idx >= len(pool):
            self.report({'WARNING'}, "No active style")
            return {'CANCELLED'}
        ds = pool[idx]
        target = ds.name
        applied = 0
        for obj in context.scene.objects:
            if obj.get('DOOR_STYLE_NAME') != target:
                continue
            if _front_kind(obj, self._DOOR_ROLES,
                           self._DRAWER_ROLES) != self.kind:
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


def _active_cabinet_style(context, style_index=-1):
    """The cabinet style the user is editing, or None.

    ``style_index`` names a row outright -- the per-style form is also
    drawn in a settings dialog opened on a row that is not the
    highlighted one, and its buttons pass the row they belong to. With
    no index (or one that no longer exists) this falls back to the
    highlighted row, which is what the sidebar form shows.
    """
    ff = get_style_props(context)
    if ff is None or not ff.cabinet_styles:
        return None
    if 0 <= style_index < len(ff.cabinet_styles):
        return ff.cabinet_styles[style_index]
    idx = ff.active_cabinet_style_index
    if idx < 0 or idx >= len(ff.cabinet_styles):
        return None
    return ff.cabinet_styles[idx]


def _style_index_prop():
    """Row this button belongs to; -1 means "the highlighted style"."""
    return bpy.props.IntProperty(name="Style Index", default=-1,
                                 options={'HIDDEN'})


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
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        self.candidates.clear()
        style = _active_cabinet_style(context, self.style_index)
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
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            return {'CANCELLED'}
        added = 0
        for c in self.candidates:
            if c.is_selected:
                style.special_effects.add().name = c.name
                added += 1
        self.report({'INFO'}, f"Added {added} special effect(s).")
        return {'FINISHED'}


class hb_face_frame_OT_add_special_effect(Operator):
    """Add one finish special effect to the active cabinet style -- the
    viewport panel's menu lists the compatible ones and adds the one
    picked, where the sidebar's dialog ticks several at once."""
    bl_idname = "hb_face_frame.add_special_effect"
    bl_label = "Add Special Effect"
    bl_description = "Add this special effect to the cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    effect_name: bpy.props.StringProperty(name="Name")  # type: ignore
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None or not self.effect_name:
            return {'CANCELLED'}
        if self.effect_name not in {e.name for e in style.special_effects}:
            style.special_effects.add().name = self.effect_name
        return {'FINISHED'}


class hb_face_frame_OT_remove_special_effect(Operator):
    """Remove a special effect from the active cabinet style."""
    bl_idname = "hb_face_frame.remove_special_effect"
    bl_label = "Remove Special Effect"
    bl_description = "Remove this special effect from the cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    effect_name: bpy.props.StringProperty(name="Name")  # type: ignore
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            return {'CANCELLED'}
        for i, item in enumerate(style.special_effects):
            if item.name == self.effect_name:
                style.special_effects.remove(i)
                break
        return {'FINISHED'}


def _repropagate_tall_drawer(context, style, kind):
    """The first extra drawer-front style is the tall-drawer style when the
    cabinet style's extra_drawer_front_height is set, so a row add / remove
    can restyle fronts. Door rows are documentation only."""
    if kind != 'DRAWER':
        return
    # A first drawer row is the new alternate style: start its height
    # at that style's minimum (the write re-propagates).
    if (len(style.extra_drawer_front_styles) == 1
            and style.extra_drawer_front_height <= 0.0
            and props_hb_face_frame.fill_alternate_drawer_height(
                style, context)):
        return
    if style.extra_drawer_front_height > 0.0:
        props_hb_face_frame._propagate_cabinet_style(style, context)


class hb_face_frame_OT_use_front_style(Operator):
    """Make the picked door (or drawer front) style the one the active
    cabinet style builds its fronts with -- the door style manager's
    way of assigning without going back to the dropdown."""
    bl_idname = "hb_face_frame.use_front_style"
    bl_label = "Use for This Cabinet Style"
    bl_description = ("Build the active cabinet style's fronts with the "
                      "picked style")
    bl_options = {'UNDO'}

    kind: bpy.props.EnumProperty(
        items=[('DOOR', "Door", ""), ('DRAWER', "Drawer Front", "")],
        default='DOOR')  # type: ignore

    @staticmethod
    def _picked(sp, kind):
        pool, idx = ((sp.door_styles, sp.active_door_style_index)
                     if kind == 'DOOR'
                     else (sp.drawer_front_styles,
                           sp.active_drawer_front_style_index))
        return pool[idx] if 0 <= idx < len(pool) else None

    @classmethod
    def poll(cls, context):
        sp = get_style_props(context)
        return (sp is not None
                and 0 <= sp.active_cabinet_style_index < len(sp.cabinet_styles))

    def execute(self, context):
        sp = get_style_props(context)
        cs = sp.cabinet_styles[sp.active_cabinet_style_index]
        style = self._picked(sp, self.kind)
        if style is None:
            self.report({'WARNING'}, "Pick a style first")
            return {'CANCELLED'}
        prop = 'door_style' if self.kind == 'DOOR' else 'drawer_front_style'
        if getattr(cs, prop) != style.name:
            setattr(cs, prop, style.name)
        self.report({'INFO'}, "%s now uses %s" % (cs.name, style.name))
        return {'FINISHED'}


class hb_face_frame_OT_face_frame_sizes(Operator):
    """Show the active cabinet style's face frame sizes as one grid:
    every rail and stile for base, tall and upper, the rails editable
    behind their padlocks. The Options panel lists the same numbers a
    row at a time, greyed while they follow the overlay, which is hard
    to read across."""
    bl_idname = "hb_face_frame.face_frame_sizes"
    bl_label = "Face Frame Sizes"
    bl_description = ("Show every rail and stile size for base, tall and "
                      "upper cabinets in one grid")
    bl_options = {'UNDO'}

    @staticmethod
    def _style(context):
        sp = get_style_props(context)
        if sp is None:
            return None
        i = sp.active_cabinet_style_index
        return sp.cabinet_styles[i] if 0 <= i < len(sp.cabinet_styles) else None

    @classmethod
    def poll(cls, context):
        return cls._style(context) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        style = self._style(context)
        if style is None:
            self.layout.label(text="No cabinet style", icon='INFO')
            return
        self.layout.label(text=style.name, icon='MATERIAL')
        style._draw_face_frame_sizes(self.layout, context)

    def execute(self, context):
        # The grid edits the style directly; OK just closes it.
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
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            self.report({'ERROR'}, "No active cabinet style.")
            return {'CANCELLED'}
        coll = (style.extra_drawer_front_styles if self.kind == 'DRAWER'
                else style.extra_door_styles)
        coll.add()
        _repropagate_tall_drawer(context, style, self.kind)
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
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore
    index: bpy.props.IntProperty(name="Index", default=-1)  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            return {'CANCELLED'}
        coll = (style.extra_drawer_front_styles if self.kind == 'DRAWER'
                else style.extra_door_styles)
        if 0 <= self.index < len(coll):
            coll.remove(self.index)
            _repropagate_tall_drawer(context, style, self.kind)
        return {'FINISHED'}


class hb_face_frame_OT_add_style_note(Operator):
    """Add a free-text note row to the active cabinet style. Notes print
    in a NOTES section at the end of the style's Style Section block
    (e.g. 'TOUCH LATCH = TL'). No geometric effect."""
    bl_idname = "hb_face_frame.add_style_note"
    bl_label = "Add Note"
    bl_description = "Add a note line printed on the Style Section page"
    bl_options = {'REGISTER', 'UNDO'}

    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            self.report({'ERROR'}, "No active cabinet style.")
            return {'CANCELLED'}
        style.ss_notes.add()
        return {'FINISHED'}


class hb_face_frame_OT_remove_style_note(Operator):
    """Remove a note row from the active cabinet style."""
    bl_idname = "hb_face_frame.remove_style_note"
    bl_label = "Remove Note"
    bl_description = "Remove this note from the Style Section page"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(name="Index", default=-1)  # type: ignore
    style_index: bpy.props.IntProperty(
        name="Style Index", default=-1, options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        style = _active_cabinet_style(context, self.style_index)
        if style is None:
            return {'CANCELLED'}
        if 0 <= self.index < len(style.ss_notes):
            style.ss_notes.remove(self.index)
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
    # Shelf roles are wiped + rebuilt every recalc (like fronts), so
    # their paint stamp also lives on a stable cage, not the part.
    _SHELF_ROLES = {'ADJUSTABLE_SHELF', 'INTERIOR_FIXED_SHELF', 'BAY_SHELF',
                    'VANITY_SHELF', 'CORNER_SHELF', 'CORNER_FIXED_SHELF'}

    @staticmethod
    def _opening_for(obj):
        """Walk up to the front's stable opening cage (survives recalc)."""
        node = obj.parent
        while node is not None:
            if node.get('IS_FACE_FRAME_OPENING_CAGE'):
                return node
            node = node.parent
        return None

    @staticmethod
    def _shelf_cage_for(obj):
        """Walk up to the stable cage a shelf stamp lives on: the opening
        cage when the shelf sits under one, else the bay cage. None for
        shelves outside both (the stamp then falls back to the part and
        lasts until the next recalc)."""
        node = obj.parent
        bay = None
        while node is not None:
            if node.get('IS_FACE_FRAME_OPENING_CAGE'):
                return node
            if bay is None and node.get('IS_FACE_FRAME_BAY_CAGE'):
                bay = node
            node = node.parent
        return bay

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
        is_shelf = is_part and obj.get('hb_part_role') in self._SHELF_ROLES

        if self.brush == 'RESET':
            if is_front:
                opening = self._opening_for(obj)
                tgt = opening if opening is not None else obj
                for k in ('hb_front_material_override', 'hb_front_material_style'):
                    if k in tgt:
                        del tgt[k]
            elif is_shelf:
                tgt = self._shelf_cage_for(obj)
                for t in (tgt, obj):
                    if t is None:
                        continue
                    for k in ('hb_shelf_material_override',
                              'hb_shelf_material_style',
                              'hb_part_material_override',
                              'hb_part_material_style'):
                        if k in t:
                            del t[k]
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
            elif is_shelf:
                # Shelves are wiped + rebuilt each recalc, so the stamp
                # lives on the stable opening / bay cage; the material
                # walk re-applies it to the respawned shelves.
                cage = self._shelf_cage_for(obj)
                tgt = cage if cage is not None else obj
                key = ('hb_shelf_material' if cage is not None
                       else 'hb_part_material')
                tgt[key + '_override'] = self.brush
                tgt[key + '_style'] = style.name
                style._set_part_surfaces(obj, mat, edge)
            elif is_part:
                obj['hb_part_material_override'] = self.brush
                obj['hb_part_material_style'] = style.name
                if obj.get('IS_MANUAL_PART'):
                    # Manual part: GN applied, paint the baked slots.
                    self._paint_manual_part_slots(obj, mat, edge)
                elif obj.get('HB_STATIC_TEXTURED'):
                    # Static carved mesh (nosed wood top / textured
                    # panel): the mesh slots render, the GN inputs are
                    # inert -- write both so the paint survives the part
                    # flipping back to live cutpart display.
                    style._set_part_surfaces(obj, mat, edge)
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
    hb_face_frame_OT_add_special_effect,
    hb_face_frame_OT_remove_special_effect,
    hb_face_frame_OT_face_frame_sizes,
    hb_face_frame_OT_use_front_style,
    hb_face_frame_OT_add_cabinet_extra_front_style,
    hb_face_frame_OT_remove_cabinet_extra_front_style,
    hb_face_frame_OT_add_style_note,
    hb_face_frame_OT_remove_style_note,
    hb_face_frame_OT_add_cabinet_style,
    hb_face_frame_OT_remove_cabinet_style,
    hb_face_frame_OT_move_cabinet_style,
    hb_face_frame_OT_add_door_style,
    hb_face_frame_OT_remove_door_style,
    hb_face_frame_OT_add_drawer_front_style,
    hb_face_frame_OT_remove_drawer_front_style,
    hb_face_frame_OT_new_front_style,
    hb_face_frame_OT_matching_drawer_front,
    hb_face_frame_OT_front_style_wizard,
    hb_face_frame_OT_assign_style_to_selected_cabinets,
    hb_face_frame_OT_update_cabinets_from_style,
    hb_face_frame_OT_paint_assign_cabinet_style,
    hb_face_frame_OT_paint_part_material,
    hb_face_frame_OT_assign_door_style_to_selected_fronts,
    hb_face_frame_OT_update_fronts_from_door_style,
    hb_face_frame_OT_paint_assign_front_style,
    hb_face_frame_OT_paint_door_hardware,
    hb_face_frame_OT_update_fronts_from_style,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()


def unregister():
    _unregister_classes()
