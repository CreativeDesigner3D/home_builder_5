"""Double-click to go into a closet, Esc to come back out.

The closet library's version of face_frame/drill.py: a double-click goes
one selection level deeper and picks what is under the cursor --
starter, then its bay, then the opening, then the part. Esc goes back
up a level and picks the parent; a click on empty space goes back to the
level the mode bar was set to.

It moves the scene's closet selection mode rather than keeping a level
of its own, so the cages, labels and grab handles follow the drill. The
mode bar's pick is the base; the drill only ever goes below it, and a
pick on the bar sets a new base.
"""
import bpy

from . import types_closets

# Levels a double-click steps through, top to bottom.
LEVELS = ('Starters', 'Bays', 'Openings', 'Parts')

_base = None            # the mode bar's pick while drilled below it, else None
_setting = False        # True while this module moves the mode itself
_addon_keymaps = []


def _props(context):
    return getattr(context.scene, 'hb_closets', None)


def _closet_tab(context):
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    hb = getattr(scene, 'home_builder', None)
    return getattr(hb, 'product_tab', '') == 'CLOSET'


def drilled(context):
    """True when the drill has taken the mode below the mode bar's pick."""
    p = _props(context)
    return (_base is not None and p is not None
            and p.closet_selection_mode_enabled
            and p.closet_selection_mode in LEVELS
            and LEVELS.index(p.closet_selection_mode) > LEVELS.index(_base))


def note_mode_change(mode):
    """Called from the mode's update: a pick from anywhere but the drill
    is a new base, so the drill lets go."""
    global _base
    if not _setting:
        _base = None


def _set_mode(context, mode):
    global _setting
    p = _props(context)
    _setting = True
    try:
        if not p.closet_selection_mode_enabled:
            p.closet_selection_mode_enabled = True
        p.closet_selection_mode = mode
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


def _parent_with(obj, tags):
    o = obj.parent if obj is not None else None
    while o is not None:
        if any(o.get(t) for t in tags):
            return o
        o = o.parent
    return None


def parent_at(obj, level):
    """The ancestor of `obj` a click at `level` would have picked."""
    if level == 'Starters':
        return types_closets.find_starter_root(obj)
    if level == 'Bays':
        return _parent_with(obj, (types_closets.TAG_BAY_CAGE,
                                  types_closets.TAG_CORNER_BAY_CAGE))
    if level == 'Openings':
        return _parent_with(obj, (types_closets.TAG_OPENING_CAGE,
                                  types_closets.TAG_CORNER_OPENING_CAGE))
    return None


def _applies(context):
    p = _props(context)
    return (p is not None and context.mode == 'OBJECT'
            and _closet_tab(context)
            and p.closet_selection_mode in LEVELS)


class hb_closets_OT_drill_in(bpy.types.Operator):
    """Go one level into what is under the cursor: starter, bay, opening, part"""
    bl_idname = "hb_closets.drill_in"
    bl_label = "Select Inside"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        p = _props(context)
        return (_applies(context) and p.closet_selection_mode_enabled
                and p.closet_selection_mode != LEVELS[-1])

    def invoke(self, context, event):
        global _base
        if _on_hud(context, event):
            return {'PASS_THROUGH'}
        mode = _props(context).closet_selection_mode
        names = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        active_name = active.name if active is not None else None
        base = _base if drilled(context) else mode
        _set_mode(context, LEVELS[LEVELS.index(mode) + 1])
        if not _select_at(context, event):
            # Nothing at the next level here: stay where it was.
            _restore(context, mode, names, active_name)
            return {'CANCELLED'}
        _base = base
        return {'FINISHED'}


class hb_closets_OT_drill_out(bpy.types.Operator):
    """Go back up one level and pick what holds the selection"""
    bl_idname = "hb_closets.drill_out"
    bl_label = "Select Parent"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _applies(context) and drilled(context)

    def execute(self, context):
        global _base
        mode = _props(context).closet_selection_mode
        up = LEVELS[LEVELS.index(mode) - 1]
        active = context.view_layer.objects.active
        target = parent_at(active, up) if active is not None else None
        base = _base
        _set_mode(context, up)
        _base = None if up == base else base
        if target is not None:
            target.select_set(True)
            context.view_layer.objects.active = target
        return {'FINISHED'}


class hb_closets_OT_drill_click(bpy.types.Operator):
    """Pick under the cursor; a click on nothing goes back to the mode
    bar's level"""
    bl_idname = "hb_closets.drill_click"
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


classes = (
    hb_closets_OT_drill_in,
    hb_closets_OT_drill_out,
    hb_closets_OT_drill_click,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, key, value in (
            (hb_closets_OT_drill_in.bl_idname, 'LEFTMOUSE', 'DOUBLE_CLICK'),
            (hb_closets_OT_drill_click.bl_idname, 'LEFTMOUSE', 'CLICK'),
            (hb_closets_OT_drill_out.bl_idname, 'ESC', 'PRESS')):
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
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    _base = None
