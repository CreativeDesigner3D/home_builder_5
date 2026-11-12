"""Cutaway: the walls between the view and the room hide by themselves.

Switched on (the Cutaway button on the tool strip), each wall whose
outside faces the view is hidden with what hangs on it, the way Hide
Wall hides it, and comes back when the view swings round. So is a wall
standing between the view and a good part of a room's floor - the
inside corner of an L, seen from its inside. A ceiling
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
_walls = {}             # scene name -> (gen, the walls: see _wall_info)
_last = {}              # scene name -> the view and gen last applied


def is_on(scene):
    return scene is not None and bool(getattr(scene, 'hb_cutaway', False))


# ---- The walls ---------------------------------------------------------------------

def _wall_frame(obj):
    """A wall's middle, its local +Y (its thickness side), its two ends
    in plan, its top and its foot, in the world."""
    from . import hb_types
    w = hb_types.GeoNodeWall(obj)
    try:
        length = w.get_input('Length')
        t = w.get_input('Thickness')
        h = w.get_input('Height')
    except Exception:
        return None
    m = obj.matrix_world
    # The middle of a curved wall is on its arc, facing square to it there
    mid = hb_types.wall_point(obj, length / 2.0, t / 2.0, h / 2.0)
    y = (hb_types.wall_point(obj, length / 2.0, t) - hb_types.wall_point(obj, length / 2.0, 0.0)).normalized()
    a = m @ Vector((0.0, t / 2.0, 0.0))
    b = m @ Vector((length, t / 2.0, 0.0))
    return mid, y, (a.x, a.y), (b.x, b.y), (m @ Vector((0.0, 0.0, h))).z, a.z


# Where a room is looked at: this high over its floor
EYE_LINE = 1.0
GRID = 7                # points across a room's floor each way
BLOCKING = 0.1          # the share of them a wall must hide to go


def _floor_points(poly, z):
    """Points spread over a room's floor, EYE_LINE over it."""
    from . import hb_wall_graph
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    out = []
    for i in range(GRID):
        for j in range(GRID):
            x = min(xs) + (max(xs) - min(xs)) * (i + 0.5) / GRID
            y = min(ys) + (max(ys) - min(ys)) * (j + 0.5) / GRID
            if hb_wall_graph.point_in_polygon((x, y), poly):
                out.append(Vector((x, y, z)))
    if not out:
        p = hb_wall_graph.interior_point(poly)
        if p is not None:
            out.append(Vector((p[0], p[1], z)))
    return out


SIDE_REACH = 0.3        # how far off a wall's middle its two sides are tried
JOINED = 0.35           # walls whose ends come this near belong together


def _near(p, a, b):
    """How far plan point p is from segment a-b."""
    ax, ay = b[0] - a[0], b[1] - a[1]
    d = ax * ax + ay * ay
    t = 0.0 if d < 1e-12 else max(0.0, min(1.0, (
        (p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / d))
    return ((p[0] - a[0] - ax * t) ** 2 + (p[1] - a[1] - ay * t) ** 2) ** 0.5


def _groups(frames):
    """The walls that touch, end to end or end to side, as lists: each
    is one room's walls where the walls do not close a room."""
    objs = list(frames)
    group = list(range(len(objs)))

    def find(i):
        while group[i] != i:
            group[i] = group[group[i]]
            i = group[i]
        return i

    for i, oi in enumerate(objs):
        ai, bi = frames[oi][2], frames[oi][3]
        for j in range(i + 1, len(objs)):
            aj, bj = frames[objs[j]][2], frames[objs[j]][3]
            if (min(_near(ai, aj, bj), _near(bi, aj, bj),
                    _near(aj, ai, bi), _near(bj, ai, bi)) < JOINED):
                group[find(i)] = find(j)
    # A room's walls stop at its doorways, so runs that do not touch can
    # still be one room: runs whose plan extents overlap are taken
    # together. Rooms standing clear of each other stay apart.
    def extent(members):
        pts = [p for i in members for p in (frames[objs[i]][2], frames[objs[i]][3])]
        return (min(p[0] for p in pts), min(p[1] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts))

    merged = True
    while merged:
        merged = False
        runs = {}
        for i in range(len(objs)):
            runs.setdefault(find(i), []).append(i)
        boxes = [(root, extent(members)) for root, members in runs.items()]
        for n, (ra, ea) in enumerate(boxes):
            for rb, eb in boxes[n + 1:]:
                if (ea[0] < eb[2] and eb[0] < ea[2]
                        and ea[1] < eb[3] and eb[1] < ea[3]):
                    group[find(ra)] = find(rb)
                    merged = True
            if merged:
                break
    out = {}
    for i, obj in enumerate(objs):
        out.setdefault(find(i), []).append(obj)
    return list(out.values())


def _room_polygons(scene):
    """The outlines of the rooms the scene's walls close."""
    try:
        from . import hb_wall_graph
        from .operators import walls
        _objs, segs = walls.level_wall_segs(scene, None)
        return [a.polygon for a in hb_wall_graph.find_rooms(segs)]
    except Exception:
        return []


def _room_walls(scene, frames, floors):
    """The walls of a scene that is not a house, each with its outside
    and the floor it is looked across to. A wall with a room on one side
    faces out the other; a wall between two rooms stays. Walls that do
    not close a room (an L, a galley, one run) take the side away from
    the middle of the walls they touch -- not of every wall in the
    scene, which sits between two rooms and turned their near walls
    inside out."""
    from . import hb_wall_graph
    polys = _room_polygons(scene)
    floor_points = {}

    def inside(point):
        return [i for i, poly in enumerate(polys)
                if hb_wall_graph.point_in_polygon((point.x, point.y), poly)]

    out, loose = [], []
    for obj, (mid, y, a, b, top, _foot) in frames.items():
        uid = obj.get(hb_house.LEVEL_KEY, '')
        flat = Vector((y.x, y.y, 0.0))
        if flat.length < 1e-6:
            continue
        flat.normalize()
        plus = inside(mid + flat * SIDE_REACH)
        minus = inside(mid - flat * SIDE_REACH)
        if plus and minus:
            continue            # between two rooms: an inside wall
        if not plus and not minus:
            loose.append(obj)
            continue
        points = []
        for i in plus or minus:
            if i not in floor_points:
                floor_points[i] = _floor_points(polys[i], floors[uid] + EYE_LINE)
            points.extend(floor_points[i])
        out.append((obj, mid, -y if plus else y, uid, a, b, top, points))
    for members in _groups({obj: frames[obj] for obj in loose}):
        centre = sum((frames[o][0] for o in members), Vector()) / len(members)
        for obj in members:
            mid, y, a, b, top, _foot = frames[obj]
            uid = obj.get(hb_house.LEVEL_KEY, '')
            away = Vector((mid.x - centre.x, mid.y - centre.y, 0.0))
            s = away.dot(y)
            if abs(s) < 1e-4:
                continue        # a lone wall: no inside to look into
            points = [Vector((centre.x, centre.y, floors[uid] + EYE_LINE))]
            out.append((obj, mid, y if s > 0 else -y, uid, a, b, top, points))
    return out


def _wall_info(scene):
    """[(wall, middle, outward normal, level uid, plan end, plan end,
    top, [points on the floor it is looked across to])] for the walls
    that can be cut. In a house, its outside walls (inside walls stay)
    and points over each of the level's rooms; elsewhere see
    _room_walls."""
    walls = [o for o in scene.objects if o.get('IS_WALL_BP') and o.type in ('MESH', 'EMPTY')]
    frames = {}
    for obj in walls:
        f = _wall_frame(obj)
        if f is not None:
            frames[obj] = f
    out, middles = [], {}
    if not frames:
        return out
    floors = {}
    for obj, f in frames.items():
        uid = obj.get(hb_house.LEVEL_KEY, '')
        floors[uid] = min(floors.get(uid, f[5]), f[5])
    if scene.get(hb_house.HOUSE_SCENE_KEY):
        from . import hb_exterior, hb_types, hb_wall_graph
        rooms = hb_exterior._indoor_polygons(scene)
        kinds = ('Exterior',) + hb_wall_graph.MODULE_WALL_TYPES
        for obj, (mid, y, a, b, top, _foot) in frames.items():
            if obj.get('WALL_TYPE', 'Exterior') not in kinds:
                continue
            uid = obj.get(hb_house.LEVEL_KEY, '')
            side = hb_exterior._outside_input(obj, hb_types.GeoNodeWall(obj), rooms.get(uid, []))
            out.append((obj, mid, -y if side == hb_exterior.REF_SIDE else y, uid, a, b, top))
        for uid, polys in rooms.items():
            if uid in floors:
                z = floors[uid] + EYE_LINE
                for poly in polys:
                    middles.setdefault(uid, []).extend(_floor_points(poly, z))
        return [w + (middles.get(w[3], ()),) for w in out]
    return _room_walls(scene, frames, floors)


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


def _cross(p, q, a, b):
    """Where plan segment p-q crosses a-b, as a fraction along p-q, or
    None."""
    rx, ry = q[0] - p[0], q[1] - p[1]
    sx, sy = b[0] - a[0], b[1] - a[1]
    den = rx * sy - ry * sx
    if abs(den) < 1e-9:
        return None
    ax, ay = a[0] - p[0], a[1] - p[1]
    t = (ax * sy - ay * sx) / den
    u = (ax * ry - ay * rx) / den
    if 0.0 < t < 1.0 and 0.0 <= u <= 1.0:
        return t
    return None


def _blocks(view, points, a, b, top):
    """Whether a wall stands between the view and a good part of a
    room's floor, tall enough to hide it."""
    if not points:
        return False
    eye, toward = view
    hidden = 0
    for m in points:
        e = eye if eye is not None else m + toward * 1000.0
        t = _cross(e, m, a, b)
        if t is not None and e.z + (m.z - e.z) * t < top:
            hidden += 1
    return hidden >= max(1, BLOCKING * len(points))


def _from_above(view, z):
    eye, toward = view
    if eye is not None:
        return eye.z > z + 0.01
    return toward.z > 0.2


def wanted(scene, view):
    """The objects the view hides: the cut walls (facing the view, or
    standing between it and a good part of a room) and what hangs on them,
    ceilings seen from above, and a house level's siding while any of its
    walls is cut."""
    hide = set()
    cut_levels = set()
    for obj, mid, outward, uid, a, b, top, points in _walls_of(scene):
        try:
            if obj.name not in scene.objects:
                continue
        except ReferenceError:
            continue
        if _facing(view, mid, outward) > FACING or _blocks(view, points, a, b, top):
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
