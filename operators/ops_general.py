"""General-purpose operators for the addon (cross-library utilities)."""

import bpy

# The claim marker the hide / isolate commands stamp is shared with
# the wall ones, so either Show All restores what the other hid.
from .walls import ISOLATE_HIDDEN_TAG


class HB_MT_call_menu_wrapper(bpy.types.Menu):
    """Wrapper menu that forces INVOKE_DEFAULT on its contents.

    Blender popup menus invoked via wm.call_menu run their items under an
    EXEC_* operator context by default. Operators that rely on invoke()
    (props dialogs, modal placement, search popups) silently no-op in that
    context - execute() returns {'FINISHED'} without ever popping the UI.

    Inlining the target menu via layout.menu_contents() lets us set the
    layout's operator_context once on the wrapper. The inner menu's draw()
    runs against our layout, so every layout.operator(...) call inside
    inherits INVOKE_DEFAULT - no per-menu patching required.
    """
    bl_idname = "HB_MT_call_menu_wrapper"
    bl_label = "HB Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        obj = context.object
        if (obj and "MENU_ID" in obj and obj["MENU_ID"]
                and hasattr(bpy.types, obj["MENU_ID"])):
            layout.menu_contents(obj["MENU_ID"])


class HB_GENERAL_OT_menu(bpy.types.Operator):
    """Pops the context menu for the active HB5 asset.

    Reads the ``MENU_ID`` custom property off the active object and pops a
    wrapper menu that inlines that target. The wrapper exists to force an
    INVOKE_DEFAULT operator context on the inner menu's items.

    Falls back to Blender's default object context menu when no HB5 asset
    is active so right-click is never dead.

    Intended to be bound to RIGHTMOUSE (3D View > Object Mode) in the
    user's keymap preferences.
    """
    bl_idname = "hb_general.menu"
    bl_label = "HB Menu"
    bl_description = "Open the context menu for the selected HB5 asset"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        obj = context.object
        menu_id = ""
        if obj and obj.get('IS_OBSTACLE') and not obj.get("MENU_ID"):
            # Obstacles placed before they carried a menu.
            obj["MENU_ID"] = 'HOME_BUILDER_MT_obstacle_commands'
        if obj and "MENU_ID" in obj and obj["MENU_ID"]:
            menu_id = obj["MENU_ID"]

        if menu_id and hasattr(bpy.types, menu_id):
            bpy.ops.wm.call_menu('INVOKE_DEFAULT',
                                 name="HB_MT_call_menu_wrapper")
        else:
            # No HB5 menu on the active object - fall through to the
            # native context menu so RMB still works on stock Blender
            # objects, empties, etc.
            bpy.ops.wm.call_menu('INVOKE_DEFAULT',
                                 name="VIEW3D_MT_object_context_menu")

        return {'FINISHED'}


def _delete_selection(context):
    """The objects a plain delete acts on: the selection, falling back to
    the active object (a right-click makes an object active without
    necessarily selecting it)."""
    objs = list(context.selected_objects)
    if not objs and context.object is not None:
        objs = [context.object]
    return objs


def _remove_objects(objs):
    """Delete objects outright rather than out of the current scene only.

    ``bpy.ops.object.delete`` unlinks an object from the collections of the
    ACTIVE SCENE and frees the datablock only when nothing else still
    references it. A layout view links the real part objects into its own
    content collections, and those hang off a collection instance rather
    than sitting in a scene's tree, so that sweep never reaches them: the
    part leaves the model, survives in bpy.data, and keeps drawing on the
    sheet. It also keeps its parent, so the next content rebuild walks
    ``children``, finds it, and links it straight back.

    Removing the datablock takes it out of every collection at once --
    what the cabinet, wall and sub-assembly deletes already do.
    """
    removed = 0
    for obj in objs:
        try:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
        except ReferenceError:
            pass
    return removed


def _delete_object_subtree(obj):
    """Remove ``obj`` and every descendant from bpy.data.

    Used when deleting a face frame sub-assembly cage that has no dedicated
    delete operator (an opening cage). Stock ``object.delete`` removes only the
    selected objects, which orphans the cage's parts; removing the whole subtree
    takes them with it.
    """
    for descendant in list(obj.children_recursive):
        bpy.data.objects.remove(descendant, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


class HB_GENERAL_OT_delete(bpy.types.Operator):
    """HB5-aware delete: routes to the correct delete operator for the
    selected asset, falling back to Blender's object delete otherwise.

    Stock ``object.delete`` removes only the selected objects, which leaves
    orphaned children behind when the selection is an HB5 cage or part, and
    never runs the cleanup an HB5 asset needs (wall miter recompute,
    neighbor constraint removal, etc.). This operator classifies the active
    object and dispatches:

    - face frame cabinet  -> hb_face_frame.delete_cabinet
    - closet starter      -> hb_closets.delete_starter
    - closet bay cage     -> hb_closets.delete_bay
    - closet opening cage -> hb_closets.clear_opening (openings are
      structural in closets; the reconciler owns their lifecycle)
    - closet part         -> hb_closets.delete_part (config-aware)
    - frameless cabinet   -> hb_frameless.delete_cabinet
    - frameless appliance -> hb_frameless.delete_appliance
    - door / window       -> home_builder_doors_windows.delete_door_window
    - wall                -> home_builder_walls.delete_wall
    - anything else       -> object.delete

    Each HB5 delete operator already sweeps ``selected_objects`` for its own
    kind, so multi-select delete (several cabinets, several walls) works
    without extra handling here - the active object only decides which kind
    is targeted. Mixed selections delete the active object's kind only.

    The cabinet, appliance, and door/window checks all run before the wall
    check on purpose: those assets sit in the wall's parent chain (a door
    or window BP is a direct child of the wall BP), so the wall test would
    otherwise misfire and delete the whole wall instead of the asset on it.

    Intended to be bound to the DEL key (3D View > Object Mode) in the
    user's keymap preferences.
    """
    bl_idname = "hb_general.delete"
    bl_label = "HB Delete"
    bl_description = "Delete the selected HB5 asset and all of its parts"
    bl_options = {'UNDO'}

    def execute(self, context):
        # Deferred imports: ops_general is imported before the product
        # libraries during addon registration, so importing these at module
        # scope would risk an early/circular import.
        from .. import hb_utils
        from ..product_libraries.face_frame import types_face_frame

        obj = context.active_object

        # A loose part attached to a cabinet is still just that part:
        # deleting it must never reach the cabinet it hangs on.
        if obj is not None and obj.get(ATTACHED_TAG):
            _remove_objects([o for o in _delete_selection(context)
                             if o.get(ATTACHED_TAG)])
            return {'FINISHED'}

        # A dimension / label (IS_2D_ANNOTATION) or an individual cabinet part
        # (CABINET_PART / hb_part_role) is a SUB-object of a product, not the
        # product itself. Deleting one must remove ONLY that object, never the
        # cabinet it annotates or belongs to: find_cabinet_root() below walks
        # up to the cage and would otherwise take the whole product down. The
        # cabinet CAGE must be the active object to delete the entire product.
        if obj is not None and (obj.get('IS_2D_ANNOTATION')
                                or obj.get('CABINET_PART')
                                or obj.get('hb_part_role')):
            # Closet parts route through their config-aware delete
            # (drawer/door/cubby counts decrement; rods take their
            # hangers along). Parts it doesn't cover remove their
            # subtree so children never orphan.
            from ..product_libraries.closets import types_closets
            if (obj.get('hb_part_role')
                    and types_closets.find_starter_root(obj) is not None):
                if bpy.ops.hb_closets.delete_part.poll():
                    bpy.ops.hb_closets.delete_part()
                else:
                    _delete_object_subtree(obj)
                return {'FINISHED'}
            # Only the part-like objects in the selection: a cage caught
            # up in a multi-select must not come down with them, which is
            # the "mixed selections delete the active object's kind only"
            # contract above -- and removing a cage object on its own
            # would orphan its parts.
            _remove_objects([o for o in _delete_selection(context)
                             if (o.get('IS_2D_ANNOTATION')
                                 or o.get('CABINET_PART')
                                 or o.get('hb_part_role'))])
            return {'FINISHED'}

        # Face frame cabinet: ONLY the cage (the cabinet root) deletes the
        # whole product. A descendant that resolves to a cabinet root but is not
        # the root itself (an opening cage, a bay, ...) deletes only the selected
        # object -- the cage must be the active object to take the product down.
        ff_root = types_face_frame.find_cabinet_root(obj)
        if ff_root is not None and ff_root is obj:
            bpy.ops.hb_face_frame.delete_cabinet()
            return {'FINISHED'}
        if ff_root is not None:
            # A sub-assembly of the cabinet (not the cage). Delete it AND its
            # parts: a bare object.delete would orphan the children.
            if obj.get('IS_FACE_FRAME_BAY_CAGE'):
                # Proper bay removal: wipes the bay subtree (openings, fronts,
                # pulls, interior) plus its mid-stile / mid-div pair and
                # reindexes the rest. Refuses on the last remaining bay.
                bpy.ops.hb_face_frame.delete_bay(
                    bay_index=obj.get('hb_bay_index', 0))
            else:
                # Opening cage (or other sub-cage): no dedicated operator, so
                # remove the cage and everything under it.
                _delete_object_subtree(obj)
            return {'FINISHED'}

        # Closet hierarchy: the starter CAGE deletes the whole product;
        # a bay cage deletes the bay; an opening cage clears its
        # contents (opening cages are structural - the reconciler owns
        # them); any other closet sub-object (hangers, molding) removes
        # its own subtree. Must run BEFORE the wall check: a starter is
        # a direct child of its wall, so the wall test would otherwise
        # delete the whole wall.
        from ..product_libraries.closets import types_closets
        cl_root = types_closets.find_starter_root(obj)
        if cl_root is not None:
            if cl_root is obj:
                bpy.ops.hb_closets.delete_starter()
            elif obj.get(types_closets.TAG_BAY_CAGE):
                bpy.ops.hb_closets.delete_bay()
            elif obj.get(types_closets.TAG_OPENING_CAGE):
                bpy.ops.hb_closets.clear_opening()
            else:
                _delete_object_subtree(obj)
            return {'FINISHED'}

        if hb_utils.get_cabinet_bp(obj) is not None:
            bpy.ops.hb_frameless.delete_cabinet()
        elif hb_utils.get_appliance_bp(obj) is not None:
            bpy.ops.hb_frameless.delete_appliance()
        elif obj and obj.get('IS_WINDOW_BP'):
            bpy.ops.home_builder_doors_windows.delete_door_window(
                object_type='WINDOW')
        elif obj and obj.get('IS_ENTRY_DOOR_BP'):
            bpy.ops.home_builder_doors_windows.delete_door_window(
                object_type='DOOR')
        elif obj and (obj.get('IS_WALL_BP')
                      or (obj.parent and obj.parent.get('IS_WALL_BP'))):
            bpy.ops.home_builder_walls.delete_wall()
        else:
            # Not an HB5 asset - delete with no confirm popup, matching
            # DEL's default behavior (X keeps its own stock confirm binding).
            _remove_objects(_delete_selection(context))

        return {'FINISHED'}


def _product_root(obj):
    """The whole product the object belongs to, or the object itself.

    Every library hangs its parts off a root, so hiding "the cabinet"
    has to start there: a part's own hide leaves its siblings on screen,
    which is what makes a half-hidden product look broken. Deliberately
    generous -- an object that belongs to no library comes back
    unchanged, so the caller can treat everything the same way.
    """
    if obj is None:
        return None
    from .. import hb_utils
    from ..product_libraries.face_frame import types_face_frame
    from ..product_libraries.closets import types_closets

    # An applied / standalone panel is its own root, and find_cabinet_root
    # already stops there rather than climbing into its host cabinet.
    root = types_face_frame.find_cabinet_root(obj)
    if root is not None:
        return root
    root = types_closets.find_starter_root(obj)
    if root is not None:
        return root
    root = hb_utils.get_cabinet_bp(obj) or hb_utils.get_appliance_bp(obj)
    if root is not None:
        return root
    cur = obj
    while cur is not None:
        if cur.get('IS_APPLIANCE') or cur.get('IS_WALL_BP'):
            return cur
        cur = cur.parent
    return obj


def _product_members(root):
    """Every object under ``root`` that belongs to that product.

    Products placed against a wall are parented to it, so a wall's
    children include whole cabinets and appliances. Hiding the wall
    should hide the wall, not the room: any child that resolves to a
    product root of its own is left out together with its subtree.
    Other roots keep everything under them.
    """
    if not root.get('IS_WALL_BP'):
        return list(root.children_recursive)
    members = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        if _is_library_root(obj) or _product_root(obj) is not root:
            continue
        members.append(obj)
        stack.extend(obj.children)
    return members


def _is_library_root(obj):
    """True when ``obj`` is the root of a library product (cabinet,
    closet starter, appliance) rather than plain wall geometry."""
    from .. import hb_utils
    from ..product_libraries.face_frame import types_face_frame
    from ..product_libraries.closets import types_closets
    return (types_face_frame.find_cabinet_root(obj) is obj
            or types_closets.find_starter_root(obj) is obj
            or hb_utils.get_cabinet_bp(obj) is obj
            or hb_utils.get_appliance_bp(obj) is obj
            or bool(obj.get('IS_APPLIANCE')))


# Marks a selection cage claimed through hide_set alone (see _hide_object).
ISOLATE_CAGE_TAG = 'HB_ISOLATED_CAGE'


def _hide_object(obj):
    """Hide one object and claim it, unless something already hid it.

    Anything already out of sight is left alone and unclaimed: the
    product logic keeps cutters, disabled partitions and construction
    helpers hidden, and the user may have hidden things by hand. Show
    All Hidden only restores what carries the claim.

    Selection cages are the exception. Switching selection modes shows
    and hides them through hide_viewport, so a cage that was out of
    sight for the current mode would come back on the next mode change.
    Every cage is claimed through hide_set alone instead, which the mode
    switch never touches, and hide_viewport stays with the mode.
    """
    if 'IS_GEONODE_CAGE' in obj:
        try:
            visible = not obj.hide_get() and not obj.hide_viewport
            if not obj.hide_get():
                obj.hide_set(True)
                obj[ISOLATE_HIDDEN_TAG] = True
                obj[ISOLATE_CAGE_TAG] = True
            return visible
        except RuntimeError:
            pass  # not in the active view layer: fall through
    try:
        if obj.hide_get():
            return False
    except RuntimeError:
        pass  # excluded from the view layer: the monitor flag decides
    if obj.hide_viewport:
        return False
    _set_hidden(obj, True)
    obj[ISOLATE_HIDDEN_TAG] = True
    return True


def _set_hidden(obj, hide):
    obj.hide_viewport = hide
    try:
        obj.hide_set(hide)
    except RuntimeError:
        pass  # not in the active view layer


class HB_GENERAL_OT_hide(bpy.types.Operator):
    """Hide a whole product, or a single part of one, with Show All
    Hidden to bring it back.

    Blender's own hide takes the selected objects and nothing else,
    which on an asset built from dozens of parented objects hides the
    cage and leaves the doors, drawers and carcass standing. ``scope``
    picks what a hide means:

    - PRODUCT -> the product root each selection resolves to, plus
      every object under it.
    - OBJECT  -> exactly the selected objects, for studying one part.

    With ``isolate`` the sense is inverted: everything else in the room
    is hidden instead, leaving the chosen product or part on its own.
    """
    bl_idname = "hb_general.hide"
    bl_label = "Hide"
    bl_options = {'UNDO'}

    scope: bpy.props.EnumProperty(
        name="Scope",
        items=[('PRODUCT', "Product",
                "The whole product and all of its parts"),
               ('OBJECT', "Object", "Only the selected objects")],
        default='PRODUCT')  # type: ignore

    isolate: bpy.props.BoolProperty(
        name="Isolate",
        description="Hide everything else instead",
        default=False)  # type: ignore

    @classmethod
    def description(cls, context, properties):
        noun = "product" if properties.scope == 'PRODUCT' else "part"
        if properties.isolate:
            return f"Hide everything except the selected {noun}"
        if properties.scope == 'PRODUCT':
            return "Hide the selected product and all of its parts"
        return "Hide the selected part"

    def _targets(self, context):
        """The objects this run is about: the selection itself, or every
        object under the products it belongs to."""
        selected = list(context.selected_objects)
        if not selected and context.active_object is not None:
            selected = [context.active_object]
        if self.scope == 'OBJECT':
            return selected
        roots = []
        for obj in selected:
            root = _product_root(obj)
            if root is not None and root not in roots:
                roots.append(root)
        # Children that live only in other scenes (drawing annotations
        # parented to a cabinet) stay out: hide_viewport is per object,
        # so hiding them here would blank them in those drawings too.
        scene_objects = context.scene.objects
        targets = []
        for root in roots:
            for obj in [root] + _product_members(root):
                if obj not in targets and scene_objects.get(obj.name) is obj:
                    targets.append(obj)
        return targets

    def execute(self, context):
        targets = self._targets(context)
        if not targets:
            self.report({'WARNING'}, "Nothing selected")
            return {'CANCELLED'}

        count = 0
        if self.isolate:
            keep = set(targets)
            for obj in context.scene.objects:
                # Cameras and lights are not room content, and hiding
                # them would blank the viewport.
                if obj in keep or obj.type in {'CAMERA', 'LIGHT'}:
                    continue
                count += bool(_hide_object(obj))
            self.report({'INFO'}, f"Isolated, hid {count} object(s)")
            return {'FINISHED'}

        for obj in targets:
            count += bool(_hide_object(obj))
        self.report({'INFO'}, f"{count} object(s) hidden")
        return {'FINISHED'}


class HB_GENERAL_OT_show_all_hidden(bpy.types.Operator):
    """Show everything the hide and isolate commands hid.

    Only claimed objects come back, so the parts the product logic keeps
    hidden stay hidden and no rebuild is needed afterwards.
    """
    bl_idname = "hb_general.show_all_hidden"
    bl_label = "Show All Hidden"
    bl_description = ("Unhide everything hidden by the hide and isolate "
                      "commands")
    bl_options = {'UNDO'}

    stock_fallback: bpy.props.BoolProperty(
        name="Stock Fallback",
        description=("When nothing was hidden by the hide commands, fall "
                     "back to Blender's own Reveal Hidden"),
        default=False,
        options={'SKIP_SAVE'})  # type: ignore

    @staticmethod
    def _claimed(context):
        """Claimed objects in this scene, plus claimed children of them
        that live only in other scenes. Hide used to reach those
        (drawing annotations parented to a cabinet), and they could
        never be restored from the scene they were hidden in."""
        scene_objects = context.scene.objects
        found = []
        for obj in scene_objects:
            if obj.get(ISOLATE_HIDDEN_TAG):
                found.append(obj)
        for obj in bpy.data.objects:
            if (obj.get(ISOLATE_HIDDEN_TAG)
                    and scene_objects.get(obj.name) is not obj
                    and obj.parent is not None
                    and scene_objects.get(obj.parent.name) is obj.parent):
                found.append(obj)
        return found

    def execute(self, context):
        count = 0
        for obj in self._claimed(context):
            if obj.get(ISOLATE_CAGE_TAG):
                # hide_viewport belongs to the selection mode.
                try:
                    obj.hide_set(False)
                except RuntimeError:
                    pass
                del obj[ISOLATE_CAGE_TAG]
            else:
                _set_hidden(obj, False)
            del obj[ISOLATE_HIDDEN_TAG]
            count += 1
        if count:
            self.report({'INFO'}, f"Restored {count} hidden object(s)")
        elif self.stock_fallback:
            # Bound to Alt+H: keep revealing what a plain hide took away.
            return bpy.ops.object.hide_view_clear('EXEC_DEFAULT')
        else:
            self.report({'INFO'}, "No hidden objects found")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Attaching loose parts to a cabinet
# ---------------------------------------------------------------------------
# A part modelled on its own - a plain mesh, or a Misc Part - can be
# made part of a cabinet: parented to the cabinet root where it stands,
# so it moves, copies and deletes with the cabinet and is drawn with it
# (the layout views walk a cabinet's whole child tree). Nothing about
# the part changes but its parent.
ATTACHED_TAG = 'hb_attached_part'
_CABINET_TAGS = ('IS_FACE_FRAME_CABINET_CAGE', 'IS_FRAMELESS_CABINET_CAGE')
# Objects that are themselves products or room pieces, never loose parts.
_NOT_A_PART_TAGS = _CABINET_TAGS + (
    'IS_WALL_BP', 'IS_FLOOR_BP', 'IS_CEILING_BP', 'IS_OBSTACLE',
    'IS_ENTRY_DOOR_BP', 'IS_WINDOW_BP', 'IS_APPLIANCE')


def find_attach_cabinet(obj):
    """The cabinet root at or above ``obj``, or None."""
    while obj is not None:
        if any(obj.get(t) for t in _CABINET_TAGS):
            return obj
        obj = obj.parent
    return None


def is_attachable(obj):
    """A loose part that can go on a cabinet: a mesh (or curve) that is
    not a product or room piece and not already one of a cabinet's own
    parts. One attached before can be moved to another cabinet."""
    if obj is None or obj.type not in {'MESH', 'CURVE'}:
        return False
    if any(obj.get(t) for t in _NOT_A_PART_TAGS):
        return False
    if obj.get(ATTACHED_TAG):
        return True
    return find_attach_cabinet(obj.parent) is None


def _attachable_selection(context):
    objs = list(context.selected_objects)
    if context.object is not None and context.object not in objs:
        objs.append(context.object)
    return [o for o in objs if is_attachable(o)]


def attach_to_cabinet(objs, cabinet):
    """Parent ``objs`` to ``cabinet`` without moving them."""
    for obj in objs:
        mw = obj.matrix_world.copy()
        obj.parent = cabinet
        obj.matrix_parent_inverse.identity()
        obj.matrix_world = mw
        obj[ATTACHED_TAG] = True


def detach_from_cabinet(objs):
    """Let attached parts go of their cabinet, where they stand."""
    for obj in objs:
        mw = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = mw
        if ATTACHED_TAG in obj:
            del obj[ATTACHED_TAG]


class HB_GENERAL_OT_attach_to_cabinet(bpy.types.Operator):
    """Make the selected parts part of a cabinet: click the cabinet and
    they move, copy and delete with it and are drawn with it"""
    bl_idname = "hb_general.attach_to_cabinet"
    bl_label = "Attach to Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(_attachable_selection(context))

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Use this from the 3D viewport")
            return {'CANCELLED'}
        self._names = [o.name for o in _attachable_selection(context)]
        self._cabinet = None
        self._header(context)
        context.window.cursor_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _parts(self):
        return [o for o in (bpy.data.objects.get(n) for n in self._names)
                if o is not None]

    def _header(self, context):
        n = len(self._names)
        what = f"{n} part{'s' if n != 1 else ''}"
        if self._cabinet is None:
            text = f"Attach {what}: click a cabinet   Esc: cancel"
        else:
            text = (f"Attach {what} to {self._cabinet.name}   "
                    "Click: attach   Esc: cancel")
        context.area.header_text_set(text)

    def _cabinet_under_mouse(self, context, event):
        from bpy_extras import view3d_utils
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return None
        coord = (event.mouse_region_x, event.mouse_region_y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        depsgraph = context.evaluated_depsgraph_get()
        skip = set(self._names)
        # Step past the parts being attached (and anything else that is
        # not a cabinet) until a cabinet is hit.
        for _ in range(32):
            hit, loc, _n, _i, obj, _m = context.scene.ray_cast(
                depsgraph, origin, direction)
            if not hit:
                return None
            if obj.name not in skip:
                cabinet = find_attach_cabinet(obj)
                if cabinet is not None:
                    return cabinet
            origin = loc + direction * 1e-4
        return None

    def _finish(self, context):
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type == 'MOUSEMOVE':
            cabinet = self._cabinet_under_mouse(context, event)
            if cabinet is not self._cabinet:
                self._cabinet = cabinet
                self._header(context)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._finish(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            cabinet = self._cabinet_under_mouse(context, event)
            if cabinet is None:
                return {'RUNNING_MODAL'}
            parts = self._parts()
            attach_to_cabinet(parts, cabinet)
            self._finish(context)
            self.report({'INFO'}, "Attached %d part%s to %s" % (
                len(parts), "" if len(parts) == 1 else "s", cabinet.name))
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


class HB_GENERAL_OT_detach_from_cabinet(bpy.types.Operator):
    """Take the selected parts off the cabinet they were attached to,
    leaving them where they are"""
    bl_idname = "hb_general.detach_from_cabinet"
    bl_label = "Detach from Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(o.get(ATTACHED_TAG) for o in _attachable_selection(context))

    def execute(self, context):
        parts = [o for o in _attachable_selection(context)
                 if o.get(ATTACHED_TAG)]
        detach_from_cabinet(parts)
        self.report({'INFO'}, "Detached %d part%s" % (
            len(parts), "" if len(parts) == 1 else "s"))
        return {'FINISHED'}


def draw_attach_items(layout, context):
    """The attach / detach commands, for any right-click menu a loose
    part can land in. Draws nothing when they don't apply."""
    parts = _attachable_selection(context)
    if not parts:
        return False
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("hb_general.attach_to_cabinet", icon='LINKED')
    if any(o.get(ATTACHED_TAG) for o in parts):
        layout.operator("hb_general.detach_from_cabinet", icon='UNLINKED')
    return True


classes = (
    HB_MT_call_menu_wrapper,
    HB_GENERAL_OT_menu,
    HB_GENERAL_OT_delete,
    HB_GENERAL_OT_hide,
    HB_GENERAL_OT_show_all_hidden,
    HB_GENERAL_OT_attach_to_cabinet,
    HB_GENERAL_OT_detach_from_cabinet,
)


# H / Alt+H in Object Mode run the product-aware hide and Show All
# Hidden, so the keyboard hides a whole product the way the context menu
# does. Shift+H (hide unselected) keeps its stock binding.
_addon_keymaps = []


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(HB_GENERAL_OT_hide.bl_idname, 'H', 'PRESS')
    kmi.properties.scope = 'PRODUCT'
    kmi.properties.isolate = False
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(HB_GENERAL_OT_show_all_hidden.bl_idname,
                              'H', 'PRESS', alt=True)
    kmi.properties.stock_fallback = True
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _register_keymaps()


def unregister():
    _unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
