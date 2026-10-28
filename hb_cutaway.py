"""Cutaway: the walls between the view and the room hide by themselves.

Switched on (the Cutaway button on the tool strip), each wall whose
outside faces the view is hidden with what hangs on it, the way Hide
Wall hides it, and comes back when the view swings round. A ceiling
seen from above hides too, and in a house a level's siding goes while
any of its walls is cut. Only what this hid is ever shown again:
anything already hidden stays as it was.

A timer watches the largest 3D view of each window whose scene has it
on. The walls' outsides are worked out again only when something in
the scene moves or changes; turning the view only compares them with
where it looks from.
"""

import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

from . import hb_house

CUT_KEY = 'HB_CUTAWAY_HIDDEN'
FACING = 0.15           # how square a wall must face the view to hide
INTERVAL = 0.1

_gen = 0                # bumped when the scene's objects move or change
_walls = {}             # scene name -> (gen, [(wall, mid, outward, level uid)])
_last = {}              # scene name -> the view and gen last applied


def is_on(scene):
    return scene is not None and bool(getattr(scene, 'hb_cutaway', False))


# ---- The walls ---------------------------------------------------------------------

def _wall_frame(obj):
    """A wall's middle and its local +Y (its thickness side), in the
    world."""
    from . import hb_types
    w = hb_types.GeoNodeWall(obj)
    try:
        length = w.get_input('Length')
        t = w.get_input('Thickness')
        h = w.get_input('Height')
    except Exception:
        return None
    m = obj.matrix_world
    mid = m @ Vector((length / 2.0, t / 2.0, h / 2.0))
    y = (m.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    return mid, y


def _wall_info(scene):
    """[(wall, middle, outward normal, level uid)] for the walls that can
    be cut. In a house, its outside walls (inside walls stay); elsewhere
    every wall, its outside the side away from the middle of them all."""
    walls = [o for o in scene.objects if o.get('IS_WALL_BP') and o.type in ('MESH', 'EMPTY')]
    frames = {}
    for obj in walls:
        f = _wall_frame(obj)
        if f is not None:
            frames[obj] = f
    out = []
    if scene.get(hb_house.HOUSE_SCENE_KEY):
        from . import hb_exterior, hb_types, hb_wall_graph
        rooms = hb_exterior._indoor_polygons(scene)
        kinds = ('Exterior',) + hb_wall_graph.MODULE_WALL_TYPES
        for obj, (mid, y) in frames.items():
            if obj.get('WALL_TYPE', 'Exterior') not in kinds:
                continue
            uid = obj.get(hb_house.LEVEL_KEY, '')
            side = hb_exterior._outside_input(obj, hb_types.GeoNodeWall(obj), rooms.get(uid, []))
            out.append((obj, mid, -y if side == hb_exterior.REF_SIDE else y, uid))
        return out
    if not frames:
        return out
    centre = sum((mid for mid, _y in frames.values()), Vector()) / len(frames)
    for obj, (mid, y) in frames.items():
        away = Vector((mid.x - centre.x, mid.y - centre.y, 0.0))
        s = away.dot(y)
        if abs(s) < 1e-4:
            continue        # a lone wall: no inside to look into
        out.append((obj, mid, y if s > 0 else -y, obj.get(hb_house.LEVEL_KEY, '')))
    return out


def _walls_of(scene):
    cached = _walls.get(scene.name)
    if cached is None or cached[0] != _gen:
        cached = (_gen, _wall_info(scene))
        _walls[scene.name] = cached
    return cached[1]


# ---- What the view hides -----------------------------------------------------------

def _facing(view, point, normal):
    """How square a face at `point` facing `normal` is to the view: over
    zero, its front is seen."""
    eye, toward = view
    d = (eye - point) if eye is not None else toward
    if d.length < 1e-6:
        return 0.0
    return normal.dot(d.normalized())


def _from_above(view, z):
    eye, toward = view
    if eye is not None:
        return eye.z > z + 0.01
    return toward.z > 0.2


def wanted(scene, view):
    """The objects the view hides: the cut walls and what hangs on them,
    ceilings seen from above, and a house level's siding while any of its
    walls is cut."""
    hide = set()
    cut_levels = set()
    for obj, mid, outward, uid in _walls_of(scene):
        try:
            if obj.name not in scene.objects:
                continue
        except ReferenceError:
            continue
        if _facing(view, mid, outward) > FACING:
            hide.add(obj)
            hide.update(obj.children_recursive)
            cut_levels.add(uid)
    for obj in scene.objects:
        if obj.get('IS_CEILING_BP'):
            top = max((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
            if _from_above(view, top):
                hide.add(obj)
                hide.update(obj.children_recursive)
    if cut_levels and scene.get(hb_house.HOUSE_SCENE_KEY):
        from . import hb_exterior
        for obj in scene.objects:
            if obj.get(hb_exterior.GEO_KEY) and obj.get(hb_house.LEVEL_KEY, '') in cut_levels:
                hide.add(obj)
    return hide


def apply(scene, view_layer, view):
    """Hide what the view hides, and show again what it no longer does
    (only what this hid)."""
    want = wanted(scene, view) if view is not None else set()
    objects = view_layer.objects
    for obj in scene.objects:
        if objects.get(obj.name) is not obj:
            continue
        mine = bool(obj.get(CUT_KEY))
        if obj in want:
            if not mine and not obj.hide_get(view_layer=view_layer):
                obj.hide_set(True, view_layer=view_layer)
                obj[CUT_KEY] = True
        elif mine:
            obj.hide_set(False, view_layer=view_layer)
            del obj[CUT_KEY]


def restore(scene, view_layer=None):
    """Show everything Cutaway hid."""
    view_layers = [view_layer] if view_layer is not None else list(scene.view_layers)
    for obj in scene.objects:
        if obj.get(CUT_KEY):
            for vl in view_layers:
                if vl.objects.get(obj.name) is obj:
                    obj.hide_set(False, view_layer=vl)
            del obj[CUT_KEY]
    _last.pop(scene.name, None)


# ---- Watching the view -------------------------------------------------------------

def _view_of(window):
    """(eye, toward) of the window's largest 3D view: the eye's place in
    perspective, else None and the direction back toward the viewer."""
    best = None
    for area in window.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        if best is None or area.width * area.height > best.width * best.height:
            best = area
    if best is None:
        return None
    r3d = best.spaces.active.region_3d
    if r3d is None:
        return None
    inv = r3d.view_matrix.inverted()
    toward = (inv.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    if r3d.is_perspective:
        return inv.translation.copy(), toward
    return None, toward


def _key(view):
    eye, toward = view
    return (tuple(round(v, 3) for v in eye) if eye is not None else None,
            tuple(round(v, 3) for v in toward), _gen)


def _tick():
    if not any(is_on(s) for s in bpy.data.scenes):
        return None
    try:
        wm = bpy.context.window_manager
        for window in wm.windows:
            scene = window.scene
            if not is_on(scene):
                continue
            view = _view_of(window)
            if view is None:
                continue
            key = _key(view)
            if _last.get(scene.name) == key:
                continue
            _last[scene.name] = key
            apply(scene, window.view_layer, view)
    except Exception:
        import traceback
        traceback.print_exc()
    return INTERVAL


def _start():
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=INTERVAL, persistent=True)


def _changed(self, context):
    if self.hb_cutaway:
        _last.pop(self.name, None)
        _start()
    else:
        restore(self)


@persistent
def _depsgraph_post(_scene, depsgraph):
    global _gen
    for u in depsgraph.updates:
        if isinstance(u.id, bpy.types.Object) and (u.is_updated_transform or u.is_updated_geometry):
            _gen += 1
            return


@persistent
def _load_post(_dummy):
    _walls.clear()
    _last.clear()
    if any(is_on(s) for s in bpy.data.scenes):
        _start()


class HOME_BUILDER_OT_toggle_cutaway(bpy.types.Operator):
    bl_idname = "home_builder.toggle_cutaway"
    bl_label = "Cutaway"
    bl_description = ("Hide the walls between the view and the room as you look around, "
                      "and the ceilings you look down on")

    def execute(self, context):
        context.scene.hb_cutaway = not context.scene.hb_cutaway
        for area in context.screen.areas if context.screen else ():
            area.tag_redraw()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(HOME_BUILDER_OT_toggle_cutaway)
    bpy.types.Scene.hb_cutaway = bpy.props.BoolProperty(
        name="Cutaway", default=False, update=_changed,
        description="Hide the walls between the view and the room as you look around")
    for handlers, fn in ((bpy.app.handlers.depsgraph_update_post, _depsgraph_post),
                         (bpy.app.handlers.load_post, _load_post)):
        if fn not in handlers:
            handlers.append(fn)
    try:
        if any(is_on(s) for s in bpy.data.scenes):
            _start()
    except Exception:
        pass                # bpy.data is closed while the add-on starts: load_post starts it


def unregister():
    for handlers, fn in ((bpy.app.handlers.depsgraph_update_post, _depsgraph_post),
                         (bpy.app.handlers.load_post, _load_post)):
        if fn in handlers:
            handlers.remove(fn)
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    if hasattr(bpy.types.Scene, 'hb_cutaway'):
        del bpy.types.Scene.hb_cutaway
    bpy.utils.unregister_class(HOME_BUILDER_OT_toggle_cutaway)
