"""Which ends of a frameless cabinet show, and the finish they get.

Each end of a straight cabinet is one of three things: open to the room
(EXPOSED), partly covered (PARTIAL: a shallower or shorter neighbour
leaves some of it showing) or covered (UNEXPOSED: a wall, an appliance
or other cabinets hide all of it). An open end takes the room's default
finished end, a partly covered one a finished side, a covered one goes
back to unfinished.

Everything is measured in world space, as boxes: an end is covered by
whatever box has a face lying on it, over the part of the end that face
overlaps. That reads the same for a neighbour on the same wall, a run
turning the corner on the next wall, an island and a peninsula.

An end set by hand is left alone until it is handed back to automatic.
"""
import bpy
import traceback
from bpy.app.handlers import persistent
from mathutils import Vector

from ... import hb_types, hb_utils, units
from . import solver_frameless

# Faces closer than this lie on each other.
TOUCH = units.inch(1.0 / 16.0)
# A wall this close to an end covers it: the gap is a scribe or a filler.
WALL_GAP = units.inch(3.0)
# A neighbour this much shorter or shallower still covers the whole end.
SLACK = units.inch(0.25)
# Walls meeting at an angle the box test can't read: how close the next
# wall has to start to the end of this one to close it.
WALL_JOIN = units.inch(6.0)

SIDES = ('LEFT', 'RIGHT')
AUTO_KEY = 'hb_end_auto_'      # + side.lower(): the condition set here last
MANUAL_KEY = 'hb_end_manual_'  # + side.lower(): set by hand, leave alone

COVER_TAGS = ('IS_FRAMELESS_CABINET_CAGE', 'IS_FRAMELESS_PRODUCT_CAGE',
              'IS_FACE_FRAME_CABINET_CAGE', 'IS_APPLIANCE')
WATCH_TAGS = COVER_TAGS + ('IS_WALL_BP',)


# ---------------------------------------------------------------------------
# Boxes
# ---------------------------------------------------------------------------

def _cage_box(obj):
    """((x0, x1), (y0, y1), (z0, z1)) of a cage in its own space."""
    cage = hb_types.GeoNodeObject(obj)
    spans = []
    for axis in 'XYZ':
        size = cage.get_input('Dim ' + axis)
        try:
            mirrored = bool(cage.get_input('Mirror ' + axis))
        except Exception:
            mirrored = False
        spans.append((-size, 0.0) if mirrored else (0.0, size))
    return tuple(spans)


def _wall_box(obj):
    wall = hb_types.GeoNodeWall(obj)
    return ((0.0, wall.get_input('Length')),
            (0.0, wall.get_input('Thickness')),
            (0.0, wall.get_input('Height')))


def _is_cover(obj):
    if not any(obj.get(tag) for tag in COVER_TAGS):
        return False
    if (obj.get('IS_BASE_ASSEMBLY') or obj.get('IS_L_CROWN')
            or obj.get('IS_CAGE_GROUP')):
        return False
    # A hood's cage runs to the ceiling; the hood itself hides nothing.
    if obj.get('IS_APPLIANCE') and obj.get('APPLIANCE_TYPE') == 'HOOD':
        return False
    return True


def is_auto_cabinet(obj):
    """A straight frameless cabinet: the ends this module settles."""
    return (bool(obj.get('IS_FRAMELESS_CABINET_CAGE'))
            and not obj.get('IS_CAGE_GROUP')
            and solver_frameless.carcass_kind(obj) in solver_frameless.STRAIGHT_KINDS)


class Scan:
    """The boxes of one scene, read once."""

    def __init__(self, scene):
        self.covers = []   # (obj, world matrix, box)
        self.walls = []
        self.cabinets = []
        for obj in scene.objects:
            try:
                if 'IS_WALL_BP' in obj:
                    self.walls.append((obj, obj.matrix_world.copy(), _wall_box(obj)))
                elif _is_cover(obj):
                    entry = (obj, hb_utils.world_matrix(obj), _cage_box(obj))
                    self.covers.append(entry)
                    if is_auto_cabinet(obj):
                        self.cabinets.append(entry)
            except Exception:
                continue

    def signature(self):
        """Changes whenever anything that decides an end moves or resizes."""
        rows = []
        for obj, mw, box in self.covers + self.walls:
            rows.append((obj.name,
                         tuple(round(v, 5) for row in mw for v in row),
                         tuple(round(v, 5) for span in box for v in span)))
        rows.sort()
        return tuple(rows)


def _box_in(frame_inv, mw, box):
    """The box seen from another object's space, as spans, when it stands
    square to that object. None when it is turned at an angle."""
    m = frame_inv @ mw
    rot = m.to_3x3()
    for col in range(3):
        axis = rot.col[col]
        if axis.length < 1e-6:
            return None
        axis = axis / axis.length
        if max(abs(axis.x), abs(axis.y), abs(axis.z)) < 0.9995:
            return None
    xs, ys, zs = [], [], []
    for x in box[0]:
        for y in box[1]:
            for z in box[2]:
                p = m @ Vector((x, y, z))
                xs.append(p.x)
                ys.append(p.y)
                zs.append(p.z)
    return ((min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs)))


def _union_area(rects):
    """Area covered by axis-aligned (a0, a1, b0, b1) rectangles."""
    if not rects:
        return 0.0
    cuts_a = sorted({v for r in rects for v in r[:2]})
    cuts_b = sorted({v for r in rects for v in r[2:]})
    area = 0.0
    for i in range(len(cuts_a) - 1):
        a = (cuts_a[i] + cuts_a[i + 1]) / 2.0
        for j in range(len(cuts_b) - 1):
            b = (cuts_b[j] + cuts_b[j + 1]) / 2.0
            if any(r[0] <= a <= r[1] and r[2] <= b <= r[3] for r in rects):
                area += (cuts_a[i + 1] - cuts_a[i]) * (cuts_b[j + 1] - cuts_b[j])
    return area


def _wall_end_closed(cab_obj, side, box, scan):
    """A cabinet at the end of its own wall, where the next wall starts
    at an angle: the corner closes the end."""
    parent = cab_obj.parent
    if parent is None or 'IS_WALL_BP' not in parent:
        return False
    try:
        length = hb_types.GeoNodeWall(parent).get_input('Length')
    except Exception:
        return False
    x0 = cab_obj.location.x + box[0][0]
    x1 = cab_obj.location.x + box[0][1]
    if side == 'LEFT' and x0 <= WALL_GAP:
        end = parent.matrix_world @ Vector((0.0, 0.0, 0.0))
    elif side == 'RIGHT' and x1 >= length - WALL_GAP:
        end = parent.matrix_world @ Vector((length, 0.0, 0.0))
    else:
        return False
    for wall_obj, mw, wbox in scan.walls:
        if wall_obj is parent:
            continue
        for x in wbox[0]:
            p = mw @ Vector((x, 0.0, 0.0))
            if (Vector((p.x, p.y)) - Vector((end.x, end.y))).length <= WALL_JOIN:
                return True
    return False


def side_exposure(cab_obj, side, scan):
    """'EXPOSED', 'PARTIAL' or 'UNEXPOSED' for one end of a cabinet."""
    entry = next((e for e in scan.cabinets if e[0] is cab_obj), None)
    if entry is None:
        entry = (cab_obj, hb_utils.world_matrix(cab_obj), _cage_box(cab_obj))
    _obj, mw, box = entry
    inv = mw.inverted_safe()
    (x0, x1), (y0, y1), (z0, z1) = box
    plane = x0 if side == 'LEFT' else x1
    out = -1.0 if side == 'LEFT' else 1.0
    full = (y1 - y0) * (z1 - z0)
    if full <= 0.0:
        return 'EXPOSED'

    rects = []

    def cover(spans, gap):
        near = spans[0][1] if side == 'LEFT' else spans[0][0]
        far = spans[0][0] if side == 'LEFT' else spans[0][1]
        # The face toward this end lies on it (or within the gap, for a
        # wall), and the box stands outside the cabinet.
        dist = (near - plane) * out
        if dist < -TOUCH or dist > gap:
            return
        if (far - plane) * out <= dist:
            return
        a0, a1 = max(spans[1][0] - SLACK, y0), min(spans[1][1] + SLACK, y1)
        b0, b1 = max(spans[2][0] - SLACK, z0), min(spans[2][1] + SLACK, z1)
        if a1 - a0 > SLACK * 2 and b1 - b0 > SLACK * 2:
            rects.append((a0, a1, b0, b1))

    for obj, omw, obox in scan.covers:
        if obj is cab_obj:
            continue
        spans = _box_in(inv, omw, obox)
        if spans is not None:
            cover(spans, TOUCH)
    for obj, omw, obox in scan.walls:
        spans = _box_in(inv, omw, obox)
        if spans is not None:
            cover(spans, WALL_GAP)

    covered = _union_area(rects)
    if covered >= full - 1e-7:
        return 'UNEXPOSED'
    if _wall_end_closed(cab_obj, side, box, scan):
        return 'UNEXPOSED'
    if covered > 1e-7:
        return 'PARTIAL'
    return 'EXPOSED'


# ---------------------------------------------------------------------------
# Applying
# ---------------------------------------------------------------------------

def _settings(scene):
    props = scene.hb_frameless
    return (bool(getattr(props, 'auto_finished_ends', True)),
            getattr(props, 'default_finished_end', 'FINISHED'))


def target_condition(state, default):
    if state == 'UNEXPOSED':
        return 'UNFINISHED'
    if state == 'PARTIAL':
        # A panel would run into the neighbour that covers part of it.
        return 'FINISHED'
    return default


def is_manual(cab_obj, side):
    return bool(cab_obj.get(MANUAL_KEY + side.lower(), False))


def set_manual(cab_obj, side, manual=True):
    key = MANUAL_KEY + side.lower()
    if manual:
        cab_obj[key] = True
    elif key in cab_obj:
        del cab_obj[key]


def _apply(context, cab_obj, side, target):
    """Put the end in ``target``. Returns True when it changed."""
    from .operators import ops_finished_ends
    current = ops_finished_ends.finish_condition(cab_obj, side)
    if current is None:
        return False
    key = AUTO_KEY + side.lower()
    # An end that is not the way this left it was set by hand, here or
    # before ends looked after themselves: it stays as it is.
    last = cab_obj.get(key, 'FINISHED')
    if current != last:
        set_manual(cab_obj, side)
        return False
    if cab_obj.get(key) != target:
        cab_obj[key] = target
    if current == target:
        return False
    panels = ('SLAB', '5PIECE')
    if current in panels or target in panels:
        ops_finished_ends.set_finish_condition(context, cab_obj, side, target)
    else:
        part = solver_frameless.carcass_parts(cab_obj).get(
            ops_finished_ends.FINISH_SIDE_ROLES[side])
        if part is None:
            return False
        part['Finish Top'] = False
        part['Finish Bottom'] = target == 'FINISHED'
    return True


def recalc_scene(scene=None, context=None):
    """Settle every automatic end in the scene. Returns the cabinets
    that changed."""
    global _running
    context = context or bpy.context
    scene = scene or context.scene
    auto, default = _settings(scene)
    if not auto:
        return []
    from .operators import ops_finished_ends
    scan = Scan(scene)
    wanted = []
    for cab_obj, _mw, _box in scan.cabinets:
        for side in SIDES:
            if is_manual(cab_obj, side):
                continue
            wanted.append((cab_obj, side,
                           target_condition(side_exposure(cab_obj, side, scan),
                                            default)))
    changed = []
    was_running = _running
    _running = True
    try:
        for cab_obj, side, target in wanted:
            try:
                if _apply(context, cab_obj, side, target) and cab_obj not in changed:
                    changed.append(cab_obj)
            except Exception:
                traceback.print_exc()
        for cab_obj in changed:
            try:
                ops_finished_ends._paint(cab_obj)
            except Exception:
                traceback.print_exc()
    finally:
        _running = was_running
    _signatures[scene.name] = (Scan(scene).signature() if changed
                               else scan.signature(), auto, default)
    return changed


def hand_back(cab_obj, side):
    """Make a hand-set end automatic again."""
    from .operators import ops_finished_ends
    set_manual(cab_obj, side, False)
    current = ops_finished_ends.finish_condition(cab_obj, side)
    if current is not None:
        cab_obj[AUTO_KEY + side.lower()] = current


# ---------------------------------------------------------------------------
# Keeping up with edits
# ---------------------------------------------------------------------------

RETRY_INTERVAL = 0.5
SETTLE_INTERVAL = 0.3

_pending = set()      # scene names
_signatures = {}      # scene name -> (signature, auto, default) last settled
_timer_armed = False
_running = False

PLACING = ('HB_FRAMELESS_OT_place', 'HB_FRAMELESS_OT_duplicate',
           'HB_FRAMELESS_OT_draw', 'TRANSFORM_OT_')


def _busy():
    """True while something is being dragged or placed."""
    wm = getattr(bpy.context, 'window_manager', None)
    for window in getattr(wm, 'windows', ()):
        for op in getattr(window, 'modal_operators', ()):
            idname = op.bl_idname
            if idname.startswith(PLACING):
                return True
            if (idname == 'HB_FRAMELESS_OT_grab'
                    and getattr(op, '_drag', None) is not None):
                return True
    return False


def request(scene=None):
    """Ask for the scene's ends to be settled once things are still."""
    global _timer_armed
    scene = scene or bpy.context.scene
    if scene is None:
        return
    _pending.add(scene.name)
    if not _timer_armed and not bpy.app.background:
        _timer_armed = True
        bpy.app.timers.register(_timer, first_interval=SETTLE_INTERVAL)


def flush_pending():
    """Settle every scene that asked. Returns the cabinets changed."""
    names = list(_pending)
    _pending.clear()
    changed = []
    for name in names:
        scene = bpy.data.scenes.get(name)
        if scene is None:
            continue
        try:
            # Fillers first, so the ends are read against where they
            # finish up.
            from . import scribe_fit
            scribe_fit.refit_scene(scene)
        except Exception:
            traceback.print_exc()
        try:
            auto, default = _settings(scene)
            if not auto:
                continue
            last = _signatures.get(name)
            if last is not None and last == (Scan(scene).signature(), auto, default):
                continue
            changed.extend(recalc_scene(scene))
        except Exception:
            traceback.print_exc()
    return changed


def _timer():
    global _timer_armed
    if _pending and _busy():
        return RETRY_INTERVAL
    _timer_armed = False
    flush_pending()
    return None


@persistent
def _on_depsgraph_update(scene, depsgraph):
    if _running:
        return
    for update in depsgraph.updates:
        if not (update.is_updated_transform or update.is_updated_geometry):
            continue
        obj = update.id
        if not isinstance(obj, bpy.types.Object):
            continue
        obj = obj.original
        if any(tag in obj for tag in WATCH_TAGS):
            request(scene)
            return


@persistent
def _on_load_pre(*_args):
    global _timer_armed
    _pending.clear()
    _signatures.clear()
    if _timer_armed and bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)
    _timer_armed = False


def register():
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)
    if _on_load_pre not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(_on_load_pre)


def unregister():
    global _timer_armed
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    if _on_load_pre in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(_on_load_pre)
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)
    _timer_armed = False
