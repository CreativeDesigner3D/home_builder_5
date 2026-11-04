"""Double-click to go into a cabinet, Esc to come back out.

The selection modes say what a click picks: a cabinet, a bay, an
opening, a part. Switching mode to reach one level down meant a trip to
the mode bar and back for every bay. Here a double-click goes one level
deeper and picks what is under the cursor -- cabinet, then its bay, then
the opening, then the part -- the way nested groups open in a drawing
program. Esc goes back up a level and picks the parent; a click on empty
space goes back to the level the mode bar was set to.

It moves the scene's selection mode rather than keeping a level of its
own, so everything that follows the mode (the cages, quiet cages in
Material Preview, the size labels, the inspector) follows the drill too.
The level the user picked on the mode bar is the base; the drill only
ever goes below it, and picking a mode on the bar sets a new base.
"""
import bpy

from . import types_face_frame

# Levels a double-click steps through, top to bottom.
LEVELS = ('Cabinets', 'Bays', 'Openings', 'Parts')

_base = None            # the mode bar's pick while drilled below it, else None
_setting = False        # True while this module moves the mode itself
_addon_keymaps = []


def _ff(context):
    return getattr(context.scene, 'hb_face_frame', None)


def drilled(context):
    """True when the drill has taken the mode below the mode bar's pick."""
    ff = _ff(context)
    return (_base is not None and ff is not None
            and ff.face_frame_selection_mode_enabled
            and ff.face_frame_selection_mode in LEVELS
            and LEVELS.index(ff.face_frame_selection_mode) > LEVELS.index(_base))


def note_mode_change(mode):
    """Called from the mode's update: a pick from anywhere but the drill
    is a new base, so the drill lets go."""
    global _base
    if not _setting:
        _base = None


def _set_mode(context, mode):
    global _setting
    ff = _ff(context)
    _setting = True
    try:
        if not ff.face_frame_selection_mode_enabled:
            ff.face_frame_selection_mode_enabled = True
        ff.face_frame_selection_mode = mode
    finally:
        _setting = False


def _on_hud(context, event):
    from ...operators import viewport_hud
    try:
        return viewport_hud.click_hits_widget(
            context, context.area, event.mouse_region_x, event.mouse_region_y)
    except Exception:
        return False


def _select_at(context, event):
    """Blender's own click select at the cursor. True if it picked."""
    bpy.ops.view3d.select(location=(event.mouse_region_x, event.mouse_region_y),
                          deselect_all=True)
    return bool(context.selected_objects)


def _restore(context, mode, names, active_name):
    """Back to `mode` with the selection it had."""
    _set_mode(context, mode)
    objects = context.view_layer.objects
    for name in names:
        obj = objects.get(name)
        if obj is not None:
            obj.select_set(True)
    if active_name and objects.get(active_name) is not None:
        objects.active = objects[active_name]


def _parent_with(obj, test):
    o = obj.parent if obj is not None else None
    while o is not None:
        if test(o):
            return o
        o = o.parent
    return None


def _parent_at(obj, level):
    """The ancestor of `obj` a click at `level` would have picked."""
    if level == 'Cabinets':
        return types_face_frame.find_cabinet_root(obj)
    if level == 'Bays':
        return _parent_with(obj, lambda o: o.get(types_face_frame.TAG_BAY_CAGE))
    if level == 'Openings':
        return _parent_with(obj,
                            lambda o: o.get(types_face_frame.TAG_OPENING_CAGE))
    return None


def _applies(context):
    ff = _ff(context)
    return (ff is not None and context.mode == 'OBJECT'
            and ff.face_frame_selection_mode in LEVELS)


class hb_face_frame_OT_drill_in(bpy.types.Operator):
    """Go one level into what is under the cursor: cabinet, bay, opening, part"""
    bl_idname = "hb_face_frame.drill_in"
    bl_label = "Select Inside"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        ff = _ff(context)
        return (_applies(context) and ff.face_frame_selection_mode_enabled
                and ff.face_frame_selection_mode != LEVELS[-1])

    def invoke(self, context, event):
        global _base
        if _on_hud(context, event):
            return {'PASS_THROUGH'}
        ff = _ff(context)
        mode = ff.face_frame_selection_mode
        names = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        active_name = active.name if active is not None else None
        base = _base if drilled(context) else mode
        _set_mode(context, LEVELS[LEVELS.index(mode) + 1])
        if not _select_at(context, event):
            # Nothing at the next level here (a corner has no openings):
            # stay where it was.
            _restore(context, mode, names, active_name)
            return {'CANCELLED'}
        _base = base
        return {'FINISHED'}


class hb_face_frame_OT_drill_out(bpy.types.Operator):
    """Go back up one level and pick what holds the selection"""
    bl_idname = "hb_face_frame.drill_out"
    bl_label = "Select Parent"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _applies(context) and drilled(context)

    def execute(self, context):
        global _base
        mode = _ff(context).face_frame_selection_mode
        up = LEVELS[LEVELS.index(mode) - 1]
        active = context.view_layer.objects.active
        target = _parent_at(active, up) if active is not None else None
        base = _base
        _set_mode(context, up)
        _base = None if up == base else base
        if target is not None:
            target.select_set(True)
            context.view_layer.objects.active = target
        return {'FINISHED'}


class hb_face_frame_OT_drill_click(bpy.types.Operator):
    """Pick under the cursor; a click on nothing goes back to the mode
    bar's level"""
    bl_idname = "hb_face_frame.drill_click"
    bl_label = "Select"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only while drilled: otherwise a click is Blender's own.
        return _applies(context) and drilled(context)

    def invoke(self, context, event):
        global _base
        if _on_hud(context, event):
            return {'PASS_THROUGH'}
        if not _select_at(context, event):
            base, _base = _base, None
            _set_mode(context, base)
        return {'FINISHED'}


class hb_face_frame_OT_select_level(bpy.types.Operator):
    """Pick this cabinet or bay, moving the selection mode to its level"""
    bl_idname = "hb_face_frame.select_level"
    bl_label = "Select"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()  # type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        global _base
        obj = context.view_layer.objects.get(self.name)
        if obj is None or self.level not in LEVELS or _ff(context) is None:
            return {'CANCELLED'}
        # Still below the mode bar's level: the drill holds. At or above
        # it, the drill has come all the way back out.
        base = _base
        if base is None or LEVELS.index(self.level) <= LEVELS.index(base):
            base = None
        if _ff(context).face_frame_selection_mode != self.level:
            _set_mode(context, self.level)
        else:
            bpy.ops.object.select_all(action='DESELECT')
        _base = base
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_select_level,
    hb_face_frame_OT_drill_in,
    hb_face_frame_OT_drill_out,
    hb_face_frame_OT_drill_click,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, key, value in (
            (hb_face_frame_OT_drill_in.bl_idname, 'LEFTMOUSE', 'DOUBLE_CLICK'),
            (hb_face_frame_OT_drill_click.bl_idname, 'LEFTMOUSE', 'CLICK'),
            (hb_face_frame_OT_drill_out.bl_idname, 'ESC', 'PRESS')):
        _addon_keymaps.append((km, km.keymap_items.new(idname, key, value)))


def unregister():
    global _base
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    _base = None
