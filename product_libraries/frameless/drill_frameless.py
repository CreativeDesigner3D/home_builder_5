"""Double-click to go into a frameless cabinet, Esc to come back out.

The frameless library's version of face_frame/drill.py: a double-click
goes one selection level deeper and picks what is under the cursor --
cabinet, then its bay, then the opening, then the part. Esc goes back up
a level and picks what holds the selection; a click on empty space goes
back to the level the mode bar was set to.

It moves the scene's frameless selection mode rather than keeping a
level of its own, so the cages, size labels and grab handles follow the
drill. The mode bar's pick is the base; the drill only ever goes below
it, and a pick on the bar sets a new base. Interiors is a mode-bar level
of its own: a double-click from it goes on to Parts, and Esc from it
goes back to Openings.
"""
import bpy

from ... import hb_utils

# Levels by depth; the drill steps through all but Interiors.
RANK = {'Cabinets': 0, 'Bays': 1, 'Openings': 2, 'Interiors': 3, 'Parts': 4}
DOWN = {'Cabinets': 'Bays', 'Bays': 'Openings', 'Openings': 'Parts',
        'Interiors': 'Parts'}
UP = {'Bays': 'Cabinets', 'Openings': 'Bays', 'Interiors': 'Openings',
      'Parts': 'Openings'}

_base = None            # the mode bar's pick while drilled below it, else None
_setting = False        # True while this module moves the mode itself
_addon_keymaps = []


def _props(context):
    return getattr(context.scene, 'hb_frameless', None)


def _mode(context):
    p = _props(context)
    return p.frameless_selection_mode if p is not None else None


def _frameless_tab(context):
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    hb = getattr(scene, 'home_builder', None)
    return getattr(hb, 'product_tab', '') == 'FRAMELESS'


def drilled(context):
    """True when the drill has taken the mode below the mode bar's pick."""
    mode = _mode(context)
    return (_base is not None and mode in RANK
            and RANK[mode] > RANK[_base])


def base_level():
    return _base


def note_mode_change(mode):
    """Called from the mode's update: a pick from anywhere but the drill
    is a new base, so the drill lets go."""
    global _base
    if not _setting:
        _base = None


def set_mode(context, mode):
    """Move the selection mode without letting go of the drill."""
    global _setting
    p = _props(context)
    if p.frameless_selection_mode == mode:
        return
    _setting = True
    try:
        p.frameless_selection_mode = mode
    finally:
        _setting = False


def set_base(base):
    global _base
    _base = base


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
    set_mode(context, mode)
    objects = context.view_layer.objects
    for name in names:
        obj = objects.get(name)
        if obj is not None:
            obj.select_set(True)
    if active_name and objects.get(active_name) is not None:
        objects.active = objects[active_name]


def _parent_with(obj, tag):
    o = obj.parent if obj is not None else None
    while o is not None:
        if o.get(tag):
            return o
        o = o.parent
    return None


def parent_at(obj, level):
    """The ancestor of `obj` a click at `level` would have picked."""
    if obj is None:
        return None
    if level == 'Cabinets':
        return hb_utils.get_cabinet_bp(obj)
    if level == 'Bays':
        return _parent_with(obj, 'IS_FRAMELESS_BAY_CAGE')
    if level == 'Openings':
        return _parent_with(obj, 'IS_FRAMELESS_OPENING_CAGE')
    return None


def _applies(context):
    return (_props(context) is not None and context.mode == 'OBJECT'
            and _frameless_tab(context) and _mode(context) in RANK)


class hb_frameless_OT_drill_in(bpy.types.Operator):
    """Go one level into what is under the cursor: cabinet, bay, opening, part"""
    bl_idname = "hb_frameless.drill_in"
    bl_label = "Select Inside"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _applies(context) and _mode(context) in DOWN

    def invoke(self, context, event):
        global _base
        if _on_hud(context, event):
            return {'PASS_THROUGH'}
        mode = _mode(context)
        names = [o.name for o in context.selected_objects]
        active = context.view_layer.objects.active
        active_name = active.name if active is not None else None
        base = _base if drilled(context) else mode
        set_mode(context, DOWN[mode])
        if not _select_at(context, event):
            # Nothing at the next level here: stay where it was.
            _restore(context, mode, names, active_name)
            return {'CANCELLED'}
        _base = base
        return {'FINISHED'}


class hb_frameless_OT_drill_out(bpy.types.Operator):
    """Go back up one level and pick what holds the selection"""
    bl_idname = "hb_frameless.drill_out"
    bl_label = "Select Parent"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _applies(context) and drilled(context)

    def execute(self, context):
        global _base
        up = UP[_mode(context)]
        active = context.view_layer.objects.active
        target = parent_at(active, up)
        base = _base
        set_mode(context, up)
        _base = None if RANK[up] <= RANK[base] else base
        if target is not None:
            bpy.ops.object.select_all(action='DESELECT')
            target.select_set(True)
            context.view_layer.objects.active = target
        return {'FINISHED'}


class hb_frameless_OT_drill_click(bpy.types.Operator):
    """Pick under the cursor; a click on nothing goes back to the mode
    bar's level"""
    bl_idname = "hb_frameless.drill_click"
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
            set_mode(context, base)
        return {'FINISHED'}


classes = (
    hb_frameless_OT_drill_in,
    hb_frameless_OT_drill_out,
    hb_frameless_OT_drill_click,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, key, value in (
            (hb_frameless_OT_drill_in.bl_idname, 'LEFTMOUSE', 'DOUBLE_CLICK'),
            (hb_frameless_OT_drill_click.bl_idname, 'LEFTMOUSE', 'CLICK'),
            (hb_frameless_OT_drill_out.bl_idname, 'ESC', 'PRESS')):
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
