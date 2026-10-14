"""Keep cabinet group cages (IS_CAGE_GROUP) wrapped around their members.

A cabinet group is a GeoNodeCage whose children are the cabinets,
products and appliances it groups. The cage's location and Dim X/Y/Z are
fitted to those members when the group is created, but nothing kept them
in step afterwards: moving or resizing one member cabinet left the cage
where it was, so anything that reads the group's extent (plan dims,
island views, the group's own selection box) saw the old footprint.

``refit_cabinet_group`` re-fits a cage to its members in the cage's own
frame - its rotation is kept - and shifts every member back by the same
amount so nothing moves in world space. It writes nothing when the cage
already fits, so it is cheap to call after any edit.

``register`` adds a depsgraph handler that queues a refit whenever a
direct member of a group changes transform or geometry, and runs the
queued refits from a timer once no transform is in progress. Face frame
and frameless groups share the IS_CAGE_GROUP marker, so this covers both.
"""

import traceback

import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

GROUP_TAG = 'IS_CAGE_GROUP'

# Direct children carrying one of these are group members whose box the
# cage must cover - the same roots the Group commands collect.
FACE_FRAME_CABINET_TAG = 'IS_FACE_FRAME_CABINET_CAGE'
MEMBER_TAGS = (
    FACE_FRAME_CABINET_TAG,
    'IS_FACE_FRAME_PRODUCT_CAGE',
    'IS_FRAMELESS_CABINET_CAGE',
    'IS_FRAMELESS_PRODUCT_CAGE',
    'IS_FACE_FRAME_MISC_PART',
    'IS_APPLIANCE',
    GROUP_TAG,
)

# Annotations (dimensions, labels) hang off the group in its own frame;
# they ride along with the cage rather than being pinned in world space.
ANNOTATION_TAGS = ('IS_2D_ANNOTATION', 'IS_DIMENSION')

TOLERANCE = 1e-5


def is_group(obj):
    return obj is not None and bool(obj.get(GROUP_TAG))


def is_group_member(obj):
    """True for a direct child of a cabinet group that the cage bounds."""
    if obj is None or not is_group(obj.parent):
        return False
    return any(obj.get(tag) for tag in MEMBER_TAGS)


def group_of(obj):
    """The innermost cabinet group obj belongs to (obj itself when it is
    a group), or None."""
    cur = obj
    while cur is not None:
        if is_group(cur):
            return cur
        cur = cur.parent
    return None


def _modifier(obj):
    hb = getattr(obj, 'home_builder', None)
    name = getattr(hb, 'mod_name', '') if hb is not None else ''
    if not name:
        return None
    mod = obj.modifiers.get(name)
    if mod is None or mod.node_group is None:
        return None
    return mod


def _geo(obj):
    from ... import hb_types
    return hb_types.GeoNodeObject(obj)


def _read_input(geo, name, default=None):
    try:
        if geo.has_input(name):
            return geo.get_input(name)
    except (ValueError, KeyError, AttributeError):
        pass
    return default


def member_extent(obj):
    """(x0, x1, y0, y1, z0, z1) of obj's box in its own frame, or None
    when its size can't be read (an applied modifier, a bare empty)."""
    if obj.get(FACE_FRAME_CABINET_TAG) and hasattr(obj, 'face_frame_cabinet'):
        props = obj.face_frame_cabinet
        w, d, h = props.width, props.depth, props.height
        mirror = (False, True, False)
    else:
        if _modifier(obj) is None:
            return None
        geo = _geo(obj)
        if obj.get('IS_FACE_FRAME_MISC_PART'):
            # A lone board: Length/Width/Thickness, cabinet frame.
            w = _read_input(geo, 'Length')
            d = _read_input(geo, 'Width')
            h = _read_input(geo, 'Thickness')
            mirror = (False, True, False)
        else:
            w = _read_input(geo, 'Dim X')
            d = _read_input(geo, 'Dim Y')
            h = _read_input(geo, 'Dim Z')
            mirror = (bool(_read_input(geo, 'Mirror X', False)),
                      bool(_read_input(geo, 'Mirror Y', True)),
                      bool(_read_input(geo, 'Mirror Z', False)))
        if w is None or d is None or h is None:
            return None
    out = []
    for size, flip in zip((w, d, h), mirror):
        size = float(size)
        out.extend((-size, 0.0) if flip else (0.0, size))
    return tuple(out)


def _members(group_obj):
    return [c for c in group_obj.children
            if any(c.get(tag) for tag in MEMBER_TAGS)]


def member_bounds(group_obj):
    """Box around the group's members in the group's local frame, as
    (min Vector, max Vector), or None when there is nothing to bound.

    Member placement is read from their stored transforms (parent
    inverse @ basis), never from matrix_world, so it is right even for a
    scene the depsgraph has not evaluated yet.
    """
    lo = Vector((float('inf'),) * 3)
    hi = Vector((float('-inf'),) * 3)
    found = False
    for member in _members(group_obj):
        ext = member_extent(member)
        if ext is None:
            continue
        local = member.matrix_parent_inverse @ member.matrix_basis
        x0, x1, y0, y1, z0, z1 = ext
        for x in (x0, x1):
            for y in (y0, y1):
                for z in (z0, z1):
                    p = local @ Vector((x, y, z))
                    for i in range(3):
                        if p[i] < lo[i]:
                            lo[i] = p[i]
                        if p[i] > hi[i]:
                            hi[i] = p[i]
        found = True
    if not found:
        return None
    return lo, hi


def refit_cabinet_group(group_obj):
    """Fit group_obj's cage tightly around its members without moving
    anything in world space. Returns True when the cage changed.

    The cage keeps its rotation; only its origin and Dim X/Y/Z move.
    Members (and any other non-annotation children) get the opposite
    shift in the group frame, so their world transforms are unchanged.
    Annotation children keep their group-local placement. Writes nothing
    when the cage already fits within TOLERANCE.
    """
    if not is_group(group_obj) or _modifier(group_obj) is None:
        return False
    bounds = member_bounds(group_obj)
    if bounds is None:
        return False
    lo, hi = bounds
    geo = _geo(group_obj)
    flips = (bool(_read_input(geo, 'Mirror X', False)),
             bool(_read_input(geo, 'Mirror Y', False)),
             bool(_read_input(geo, 'Mirror Z', False)))
    # The cage origin sits on the min side of each axis, or the max side
    # when that axis is mirrored (Mirror Y: origin at the back).
    offset = Vector([hi[i] if flips[i] else lo[i] for i in range(3)])
    size = hi - lo
    names = ('Dim X', 'Dim Y', 'Dim Z')
    current = [_read_input(geo, n) for n in names]
    if any(v is None for v in current):
        return False
    if (offset.length <= TOLERANCE
            and all(abs(float(c) - s) <= TOLERANCE
                    for c, s in zip(current, size))):
        return False

    children = list(group_obj.children)
    # Move the cage origin by offset in its own frame. Only location is
    # written so the stored rotation is kept exactly.
    basis = group_obj.matrix_basis
    group_obj.location = (group_obj.location
                          + basis.to_3x3() @ offset)
    for child in children:
        if any(child.get(tag) for tag in ANNOTATION_TAGS):
            continue
        # basis' = mpi^-1 @ T(-offset) @ mpi @ basis, which is a pure
        # translation of basis by -(mpi rotation)^-1 @ offset.
        mpi3 = child.matrix_parent_inverse.to_3x3()
        child.location = (child.location
                          - mpi3.inverted_safe() @ offset)
    for name, value, cur in zip(names, size, current):
        if abs(float(cur) - value) > TOLERANCE:
            geo.set_input(name, value)
    return True


def refit_group_of(obj):
    """Refit the group obj belongs to (obj may be the group itself).
    Returns True when a cage changed. Never raises."""
    try:
        group = group_of(obj)
        if group is None:
            return False
        return refit_cabinet_group(group)
    except ReferenceError:
        return False
    except Exception:
        traceback.print_exc()
        return False


def refit_all_groups(scene):
    """Refit every cabinet group in scene, inner groups first. Returns
    the number of cages that changed."""
    groups = [o for o in scene.objects if is_group(o)]

    def depth(o):
        n = 0
        cur = o.parent
        while cur is not None:
            n += 1
            cur = cur.parent
        return n

    groups.sort(key=depth, reverse=True)
    changed = 0
    for group in groups:
        try:
            if refit_cabinet_group(group):
                changed += 1
        except Exception:
            traceback.print_exc()
    return changed


# ---------------------------------------------------------------------------
# Automatic refit after member edits
# ---------------------------------------------------------------------------
_pending = set()
_timer_armed = False
_running = False
RETRY_INTERVAL = 0.2


def _transform_in_progress():
    """True while the user is mid-drag: a Blender transform (G / R / S)
    or a face frame grab drag. Refitting then would shift the parent
    frame under an operator that is still writing member transforms."""
    wm = getattr(bpy.context, 'window_manager', None)
    for window in getattr(wm, 'windows', ()):
        for op in getattr(window, 'modal_operators', ()):
            if op.bl_idname.startswith('TRANSFORM_OT_'):
                return True
    try:
        from ..face_frame.operators import op_modify_cabinet
        for op in list(op_modify_cabinet._live_grabs):
            if getattr(op, '_drag_active', False):
                return True
    except Exception:
        pass
    return False


def flush_pending():
    """Refit every queued group now. Returns the number changed."""
    global _running
    names = list(_pending)
    _pending.clear()
    if not names:
        return 0
    changed = 0
    _running = True
    try:
        for name in names:
            group = bpy.data.objects.get(name)
            if group is None or not is_group(group):
                continue
            try:
                if refit_cabinet_group(group):
                    changed += 1
            except Exception:
                traceback.print_exc()
    finally:
        _running = False
    return changed


def _timer():
    global _timer_armed
    if _pending and _transform_in_progress():
        return RETRY_INTERVAL
    _timer_armed = False
    flush_pending()
    return None


@persistent
def _on_depsgraph_update(scene, depsgraph):
    global _timer_armed
    if _running:
        return
    for update in depsgraph.updates:
        if not (update.is_updated_transform or update.is_updated_geometry):
            continue
        obj = update.id
        if not isinstance(obj, bpy.types.Object):
            continue
        obj = obj.original
        parent = obj.parent
        if parent is None or not parent.get(GROUP_TAG):
            continue
        if not any(obj.get(tag) for tag in MEMBER_TAGS):
            continue
        _pending.add(parent.name)
    if _pending and not _timer_armed:
        _timer_armed = True
        bpy.app.timers.register(_timer, first_interval=0.0)


@persistent
def _on_load_pre(*_args):
    global _timer_armed
    _pending.clear()
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
    _pending.clear()
