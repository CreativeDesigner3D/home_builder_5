"""Picked miter joints between two boards.

Two boards meeting at a corner - end stiles of two cabinets, finished or
paneled backs wrapping an island half wall, two partitions - can be
mitred to each other from the part menu. The joint is stored on both
cabinets and re-applied after either one rebuilds:

- each board is grown out to the joint if it stops short of the corner
  (its growth is stamped on it and taken back off before the next
  application, so repeated rebuilds don't stack);
- each board is trimmed by a hidden prism cutter.

Modes:
- EVEN: both boards are cut on the line through the outside corner (where
  the outer faces meet) and the inside corner (where the inner faces
  meet).
- LONG_SELF / LONG_OTHER: a one-sided (butt) joint. The long board runs
  past the corner to where its inner face meets the short board's outer
  face, and ends square there. The short board is cut at the angle along
  the long board's inner face, so it sits flat against it.

Boards are vertical cutparts (Length along local X, Width along local Y,
Thickness along local Z with the Mirror Y / Mirror Z flags), seen in plan.
"""

import json

import bmesh
import bpy
from mathutils import Vector

from ... import units
from . import types_face_frame
from ...hb_types import GeoNodeCutpart

JOINTS_KEY = 'HB_MITER_JOINTS'
GROW_KEY = 'HB_MITER_GROW'
GROW_INPUT_KEY = 'HB_MITER_GROW_INPUT'
PART_ROLE_MITER_CUTTER = 'MITER_JOINT_CUTTER'
MOD_PREFIX = 'Miter Joint '

ALLOWED_ROLES = frozenset((
    types_face_frame.PART_ROLE_LEFT_STILE,
    types_face_frame.PART_ROLE_RIGHT_STILE,
    types_face_frame.PART_ROLE_MID_STILE,
    types_face_frame.PART_ROLE_BACK,
    types_face_frame.PART_ROLE_FINISHED_BACK,
    types_face_frame.PART_ROLE_LEFT_SIDE,
    types_face_frame.PART_ROLE_RIGHT_SIDE,
    types_face_frame.PART_ROLE_MID_DIVISION,
    types_face_frame.PART_ROLE_PARTITION_SKIN,
    'BEADBOARD', 'SHIPLAP', 'V_GROOVE',
))

_BIG = 2.0
_MARGIN = units.inch(1.0 / 32.0)
# Thinner stock leaves too little material for a clean miter.
MIN_THICKNESS = units.inch(0.5)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def part_key(part):
    """What re-finds a part after its cabinet rebuilds: role plus the
    segment / bay keys rebuilt parts carry, plus its name."""
    return {
        'name': part.name,
        'role': part.get('hb_part_role', ''),
        'seg': part.get('hb_segment_start_bay'),
        'bay': part.get('hb_bay_index'),
    }


def find_part(root, key):
    part = bpy.data.objects.get(key.get('name', ''))
    if part is not None and types_face_frame.find_cabinet_root(part) is root:
        return part
    for child in root.children_recursive:
        if child.get('hb_part_role') != key.get('role'):
            continue
        if (key.get('seg') is not None
                and child.get('hb_segment_start_bay') != key.get('seg')):
            continue
        if (key.get('bay') is not None
                and child.get('hb_bay_index') != key.get('bay')):
            continue
        return child
    return None


def joints(root):
    try:
        data = json.loads(root.get(JOINTS_KEY, '[]'))
    except (TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _store(root, data):
    if data:
        root[JOINTS_KEY] = json.dumps(data)
    elif JOINTS_KEY in root:
        del root[JOINTS_KEY]


def add_joint(part_a, part_b, mode='EVEN'):
    """Mitre part_a to part_b. mode: EVEN, LONG_A (part_a is the long
    board) or LONG_B. Replaces any joint either part already has."""
    remove_joints(part_a)
    remove_joints(part_b)
    root_a = types_face_frame.find_cabinet_root(part_a)
    root_b = types_face_frame.find_cabinet_root(part_b)
    if root_a is None or root_b is None:
        return False
    jid = f"{part_a.name}|{part_b.name}"
    mode_a = {'EVEN': 'EVEN', 'LONG_A': 'LONG_SELF',
              'LONG_B': 'LONG_OTHER'}[mode]
    mode_b = {'EVEN': 'EVEN', 'LONG_SELF': 'LONG_OTHER',
              'LONG_OTHER': 'LONG_SELF'}[mode_a]
    for root, me, other_root, other, m in (
            (root_a, part_a, root_b, part_b, mode_a),
            (root_b, part_b, root_a, part_a, mode_b)):
        data = joints(root)
        data.append({'id': jid, 'self': part_key(me),
                     'other_root': other_root.name,
                     'other': part_key(other), 'mode': m})
        _store(root, data)
    apply_root(root_a)
    if root_b is not root_a:
        apply_root(root_b)
    # The side behind a mitered end stile follows the joint.
    _rescribe(root_a)
    if root_b is not root_a:
        _rescribe(root_b)
    return True


def joint_for(part):
    root = types_face_frame.find_cabinet_root(part)
    if root is None:
        return None
    for j in joints(root):
        if find_part(root, j['self']) is part:
            return j
    return None


def remove_joints(part):
    """Drop the joint part takes part in, on both cabinets, and undo it."""
    j = joint_for(part)
    if j is None:
        return False
    root = types_face_frame.find_cabinet_root(part)
    other_root = bpy.data.objects.get(j['other_root'])
    for r in (root, other_root):
        if r is None:
            continue
        keep = [x for x in joints(r) if x.get('id') != j['id']]
        _store(r, keep)
    _undo(part)
    other = find_part(other_root, j['other']) if other_root else None
    if other is not None:
        _undo(other)
    return True


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def _evaluated_world(obj):
    """obj's world matrix as last evaluated. An object's own matrix_world
    is left at identity when undo reads the object back, until something
    moves it again; its evaluated copy keeps the real one."""
    try:
        ev = obj.evaluated_get(bpy.context.view_layer.depsgraph)
        if ev is not None and ev.is_evaluated:
            return ev.matrix_world.copy()
    except Exception:
        pass
    return obj.matrix_world.copy()


def _root_world(root):
    """A cabinet root's world matrix: its stored transform on its
    parent's evaluated matrix, so neither a move made a moment ago nor
    an undo leaves it stale."""
    if root.constraints or (root.parent is not None
                            and root.parent_type != 'OBJECT'):
        return _evaluated_world(root)
    local = root.matrix_parent_inverse @ root.matrix_basis
    if root.parent is None:
        return local
    return _evaluated_world(root.parent) @ local


def _world_matrix(part):
    """part's world matrix from stored transforms up to its cabinet root
    (matrix_world can lag within a rebuild)."""
    m = part.matrix_parent_inverse @ part.matrix_basis
    node = part.parent
    root = types_face_frame.find_cabinet_root(part)
    while node is not None and node is not root:
        m = node.matrix_parent_inverse @ node.matrix_basis @ m
        node = node.parent
    if root is None:
        return part.matrix_world.copy()
    return _root_world(root) @ m


class _Board:
    """A vertical board's plan footprint: along its plan axis from a0 to
    a1, across its thickness from its outer to inner face."""

    def __init__(self, part):
        self.part = part
        gn = GeoNodeCutpart(part)
        self.L = gn.get_input('Length')
        self.W = gn.get_input('Width')
        self.T = gn.get_input('Thickness')
        my = bool(gn.get_input('Mirror Y'))
        mz = bool(gn.get_input('Mirror Z'))
        self.mw = _world_matrix(part)
        r = self.mw.to_3x3()
        ax = {'x': r @ Vector((1, 0, 0)), 'y': r @ Vector((0, 1, 0)),
              'z': r @ Vector((0, 0, 1))}
        self.ranges = {'x': (0.0, self.L),
                       'y': (-self.W, 0.0) if my else (0.0, self.W),
                       'z': (-self.T, 0.0) if mz else (0.0, self.T)}
        # Plan length axis: the non-thickness axis lying flat.
        self.axis = 'x' if abs(ax['x'].z) < abs(ax['y'].z) else 'y'
        self.size_input = 'Length' if self.axis == 'x' else 'Width'
        o = self.mw.translation
        self.origin = Vector((o.x, o.y))
        d = ax[self.axis]
        self.u = Vector((d.x, d.y)).normalized()
        n = ax['z']
        self.n = Vector((n.x, n.y)).normalized()
        self.a0, self.a1 = self.ranges[self.axis]
        self.t0, self.t1 = self.ranges['z']
        self.mirror_axis = (self.axis == 'y' and my)

    def point(self, a, t):
        return self.origin + self.u * a + self.n * t

    def centre(self):
        return self.point((self.a0 + self.a1) / 2.0,
                          (self.t0 + self.t1) / 2.0)

    def faces(self, toward):
        """(outer_t, inner_t): thickness coordinates of the face away
        from / nearer to the point toward."""
        dt = (toward - self.origin).dot(self.n)
        mid = (self.t0 + self.t1) / 2.0
        if dt > mid:
            return self.t0, self.t1
        return self.t1, self.t0

    def line(self, t):
        """The face at thickness t as (point, direction)."""
        return self.point(0.0, t), self.u


def _cross(p1, d1, p2, d2):
    den = d1.x * d2.y - d1.y * d2.x
    if abs(den) < 1e-9:
        return None
    w = p2 - p1
    s = (w.x * d2.y - w.y * d2.x) / den
    return p1 + d1 * s


def _joint_points(a, b):
    """(O, I): outside corner (where the outer faces meet) and inside
    corner (where the inner faces meet)."""
    ca, cb = a.centre(), b.centre()
    a_out, a_in = a.faces(cb)
    b_out, b_in = b.faces(ca)
    O = _cross(*a.line(a_out), *b.line(b_out))
    I = _cross(*a.line(a_in), *b.line(b_in))
    return O, I


def _half_plane(p, q, toward):
    """Plan quad removing everything on toward's side of line p-q."""
    u = (q - p).normalized()
    n = Vector((-u.y, u.x))
    if (toward - p).dot(n) < 0:
        n = -n
    c = (p + q) / 2.0
    return [c - u * _BIG, c + u * _BIG, c + u * _BIG + n * _BIG,
            c - u * _BIG + n * _BIG]


def _toward_end(board, p):
    """A point past p along board's length, on the side away from its
    middle: the end of the board p lies at."""
    u = board.u if (p - board.centre()).dot(board.u) > 0 else -board.u
    return p + u


# ---------------------------------------------------------------------------
# Applying
# ---------------------------------------------------------------------------

def _undo_growth(part):
    stamp = part.get(GROW_KEY)
    if stamp is None:
        return
    key = part.get(GROW_INPUT_KEY, 'Length')
    try:
        grow, size, sx, sy, sz = stamp
    except (TypeError, ValueError):
        del part[GROW_KEY]
        return
    gn = GeoNodeCutpart(part)
    cur = gn.get_input(key)
    if cur is not None and abs(cur - size) < 1e-7:
        gn.set_input(key, size - grow)
        part.location = part.location - Vector((sx, sy, sz))
    del part[GROW_KEY]
    if GROW_INPUT_KEY in part:
        del part[GROW_INPUT_KEY]


def _grow_to(board, points):
    """Grow board along its plan axis so it reaches every point (plus a
    hair), at whichever end is nearer them. Stamped for _undo_growth."""
    need_hi = max((p - board.origin).dot(board.u) for p in points) + _MARGIN
    need_lo = min((p - board.origin).dot(board.u) for p in points) - _MARGIN
    mid = (board.a0 + board.a1) / 2.0
    target = sum((p - board.origin).dot(board.u) for p in points) / len(points)
    if target >= mid:
        grow = max(need_hi - board.a1, 0.0)
        at_size_end = (board.a1 != 0.0) or not board.mirror_axis
        shift_dir = 1.0
    else:
        grow = max(board.a0 - need_lo, 0.0)
        at_size_end = board.mirror_axis
        shift_dir = -1.0
    if grow <= 1e-7:
        return
    part = board.part
    gn = GeoNodeCutpart(part)
    size = gn.get_input(board.size_input)
    gn.set_input(board.size_input, size + grow)
    shift = Vector((0.0, 0.0, 0.0))
    if not at_size_end:
        local = Vector((1, 0, 0)) if board.axis == 'x' else Vector((0, 1, 0))
        shift = part.matrix_basis.to_3x3().normalized() @ (local * grow
                                                           * shift_dir)
        part.location = part.location + shift
    part[GROW_KEY] = [grow, size + grow, shift.x, shift.y, shift.z]
    part[GROW_INPUT_KEY] = board.size_input


def _ensure_cutter(part, idx):
    root = types_face_frame.find_cabinet_root(part)
    name = f"Miter Cutter {part.name} {idx}"
    cutter = next((c for c in root.children
                   if c.get('hb_part_role') == PART_ROLE_MITER_CUTTER
                   and c.get('hb_miter_part') == part.name
                   and c.get('hb_miter_idx') == idx), None)
    if cutter is None:
        cutter = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        cutter['hb_part_role'] = PART_ROLE_MITER_CUTTER
        cutter['hb_miter_part'] = part.name
        cutter['hb_miter_idx'] = idx
        cutter.parent = root
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in root.users_collection:
            coll.objects.link(cutter)
            break
    return cutter


def _write_prism(cutter, quad, z0, z1):
    root = cutter.parent
    inv = _root_world(root).inverted()
    bm = bmesh.new()
    lo = [bm.verts.new(inv @ Vector((p.x, p.y, z0))) for p in quad]
    hi = [bm.verts.new(inv @ Vector((p.x, p.y, z1))) for p in quad]
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(len(quad)):
        j = (i + 1) % len(quad)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(cutter.data)
    bm.free()
    cutter.location = (0.0, 0.0, 0.0)
    cutter.rotation_euler = (0.0, 0.0, 0.0)
    cutter.matrix_parent_inverse.identity()


def _set_cuts(part, quads, z0, z1):
    for idx in range(2):
        mod_name = f"{MOD_PREFIX}{idx + 1}"
        mod = part.modifiers.get(mod_name)
        if idx >= len(quads):
            if mod is not None:
                part.modifiers.remove(mod)
            _drop_cutter(part, idx)
            continue
        cutter = _ensure_cutter(part, idx)
        _write_prism(cutter, quads[idx], z0, z1)
        if mod is None:
            mod = part.modifiers.new(name=mod_name, type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.solver = 'EXACT'
        if mod.object is not cutter:
            mod.object = cutter


def _drop_cutter(part, idx):
    root = types_face_frame.find_cabinet_root(part)
    if root is None:
        return
    for c in list(root.children):
        if (c.get('hb_part_role') == PART_ROLE_MITER_CUTTER
                and c.get('hb_miter_part') == part.name
                and (idx is None or c.get('hb_miter_idx') == idx)):
            mesh = c.data
            bpy.data.objects.remove(c, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)


def _undo(part):
    _undo_growth(part)
    for idx in range(2):
        mod = part.modifiers.get(f"{MOD_PREFIX}{idx + 1}")
        if mod is not None:
            part.modifiers.remove(mod)
    _drop_cutter(part, None)


def _cut_line(a, b, mode):
    """(p, q): the plan line board a is cut on for its joint with b, from
    face to face across a's thickness, or None when the boards don't
    cross. It depends only on the boards' faces, so a's growth doesn't
    move it."""
    if mode == 'EVEN':
        O, I = _joint_points(a, b)
        if O is None or I is None:
            return None
        return O, I
    a_out, a_in = a.faces(b.centre())
    b_out, b_in = b.faces(a.centre())
    if mode == 'LONG_SELF':
        # Run past the corner to where my inner face meets the other
        # board's outer face, and end square there.
        p = _cross(*a.line(a_in), *b.line(b_out))
        if p is None:
            return None
        return p, p + a.n * (a_out - a_in)
    # LONG_OTHER: a is the short board, cut at the angle along the long
    # board's inner face.
    p = _cross(*a.line(a_out), *b.line(b_in))
    q = _cross(*a.line(a_in), *b.line(b_in))
    if p is None or q is None:
        return None
    return p, q


def _apply_pair(me, other, mode):
    """Grow + cut `me` for its joint with `other` (other is only read)."""
    _undo_growth(me)
    a = _Board(me)
    b = _Board(other)
    line = _cut_line(a, b, mode)
    if line is None:
        return
    p, q = line
    z_lo = min(a.mw.translation.z, b.mw.translation.z) - units.inch(2.0)
    z_hi = z_lo + units.inch(200.0)
    _grow_to(a, [p, q])
    a = _Board(me)
    if mode == 'LONG_SELF':
        quads = [_half_plane(p, q, _toward_end(a, p))]
    else:
        quads = [_half_plane(p, q, b.centre())]
    _set_cuts(me, quads, z_lo, z_hi)


def apply_root(root):
    """Re-apply every joint stored on root to root's own parts. Each
    cabinet applies its own side, so both run after either rebuilds
    (the partner is re-applied here too, its growth undone first)."""
    for j in joints(root):
        me = find_part(root, j['self'])
        other_root = bpy.data.objects.get(j.get('other_root', ''))
        other = find_part(other_root, j['other']) if other_root else None
        if me is None or other is None:
            continue
        try:
            _apply_pair(me, other, j.get('mode', 'EVEN'))
            oj = next((x for x in joints(other_root)
                       if x.get('id') == j.get('id')), None)
            if oj is not None and other_root is not root:
                _apply_pair(other, me, oj.get('mode', 'EVEN'))
        except Exception as exc:
            print(f"Home Builder: miter joint {j.get('id')} skipped ({exc})")


# ---------------------------------------------------------------------------
# Scribe behind a mitered end stile
# ---------------------------------------------------------------------------
#
# The carcass side behind an end stile sits in from the cabinet's edge by
# the scribe. Mitering the stile cuts its back face short of the edge
# (by the most on the short part of a one-sided joint), and a side left
# at its usual scribe would hang past the cut into the void behind the
# joint. While a side is unfinished - picked automatically or set by the
# user - its scribe is raised until the side lands on the stile with at
# least MIN_BEARING of stile beyond it, never so far that the side
# passes the stile's inner edge into the opening. A side already that
# far in is left where it is.
#
# The scribe the side had before is kept on the cabinet, next to the
# value written, under SCRIBE_KEY ({side: [base, written]}). Taking the
# miter off puts the base back. A scribe typed by hand after the joint
# moved it stands for as long as the joint does: the stamp is kept with
# a third, truthy entry so later rebuilds leave the side alone.

SCRIBE_KEY = 'HB_MITER_SCRIBE'
MIN_BEARING = units.inch(0.25)
_STILE_SIDES = {
    types_face_frame.PART_ROLE_LEFT_STILE: 'left',
    types_face_frame.PART_ROLE_RIGHT_STILE: 'right',
}
_SIDE_ROLES = {
    'left': types_face_frame.PART_ROLE_LEFT_SIDE,
    'right': types_face_frame.PART_ROLE_RIGHT_SIDE,
}
# Cabinets whose scribe-driven rebuild is running (by name).
_SCRIBING = set()


def _scribe_stamps(root):
    try:
        data = json.loads(root.get(SCRIBE_KEY, '{}'))
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _side_thickness(root, side):
    for child in root.children_recursive:
        if child.get('hb_part_role') == _SIDE_ROLES[side]:
            t = GeoNodeCutpart(child).get_input('Thickness')
            if t:
                return t
    return getattr(root.face_frame_cabinet, 'material_thickness',
                   units.inch(0.5))


def _scribe_needed(root, stile, other, mode, side):
    """Least scribe that puts the side behind `stile` on solid stile,
    capped where the side would pass the stile's inner edge. None when
    the joint doesn't cross."""
    a = _Board(stile)
    b = _Board(other)
    line = _cut_line(a, b, mode)
    if line is None:
        return None
    p, q = line
    inv = _root_world(root).inverted()
    z = a.mw.translation.z

    def local(pt):
        return inv @ Vector((pt.x, pt.y, z))

    # The back face is the one toward the carcass (greater local Y: the
    # frame is at the front, -Y).
    mid = (a.a0 + a.a1) / 2.0
    back_t = max((a.t0, a.t1), key=lambda t: local(a.point(mid, t)).y)
    end = _cross(*a.line(back_t), p, q - p)
    if end is None:
        return None
    ends = [local(a.point(a.a0, back_t)).x, local(a.point(a.a1, back_t)).x]
    width = root.face_frame_cabinet.width
    if side == 'left':
        reach = local(end).x
        inner = max(ends)
    else:
        reach = width - local(end).x
        inner = width - min(ends)
    need = reach + MIN_BEARING
    cap = inner - _side_thickness(root, side)
    return max(min(need, cap), 0.0)


def sync_scribes(root):
    """Set the scribe of each unfinished side whose end
    stile is mitered (see above). Returns True when a scribe changed, so
    the caller rebuilds the cabinet."""
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is None:
        return False
    wanted = {}
    for j in joints(root):
        me = find_part(root, j['self'])
        side = _STILE_SIDES.get(me.get('hb_part_role')) if me else None
        if side is None:
            continue
        other_root = bpy.data.objects.get(j.get('other_root', ''))
        other = find_part(other_root, j['other']) if other_root else None
        if other is None:
            continue
        need = _scribe_needed(root, me, other, j.get('mode', 'EVEN'), side)
        if need is not None:
            wanted[side] = need
    stamps = _scribe_stamps(root)
    if not wanted and not stamps:
        return False
    changed = False
    for side in ('left', 'right'):
        prop = f'{side}_scribe'
        cur = getattr(cab, prop)
        auto = getattr(cab, f'{side}_finish_end_auto')
        stamp = stamps.get(side)
        pinned = stamp is not None and len(stamp) > 2 and bool(stamp[2])
        if (stamp is not None and not pinned
                and abs(cur - stamp[1]) > 1e-6):
            if not auto:
                # Typed by hand since the joint moved it: that value
                # stands for as long as the joint does.
                stamp = stamps[side] = [cur, cur, 1]
                pinned = True
            else:
                # The exposure pass re-derived the scribe: that is the
                # new base.
                stamp = [cur, cur]
        unfinished = (getattr(cab, f'{side}_finished_end_condition')
                      == 'UNFINISHED')
        if pinned and side in wanted and unfinished:
            continue
        if side not in wanted or not unfinished:
            if stamp is not None:
                if not pinned and abs(cur - stamp[0]) > 1e-6:
                    cab[prop] = stamp[0]     # no update callback
                    changed = True
                del stamps[side]
            continue
        base = stamp[0] if stamp is not None else cur
        target = max(base, wanted[side])
        if abs(target - cur) > 1e-6:
            cab[prop] = target
            changed = True
        stamps[side] = [base, target]
    if stamps:
        root[SCRIBE_KEY] = json.dumps(stamps)
    elif SCRIBE_KEY in root:
        del root[SCRIBE_KEY]
    return changed


def held_scribe(root, side, scribe):
    """The scribe another pass should write for one side ('left' /
    'right') when it wants ``scribe`` there: no less than what a miter
    joint on that side's stile has raised it to. ``scribe`` becomes the
    value put back when the miter comes off."""
    stamps = _scribe_stamps(root)
    stamp = stamps.get(side)
    if stamp is None or (len(stamp) > 2 and stamp[2]):
        return scribe
    held = max(scribe, stamp[1])
    if abs(stamp[0] - scribe) > 1e-6 or abs(stamp[1] - held) > 1e-6:
        stamps[side] = [scribe, held]
        root[SCRIBE_KEY] = json.dumps(stamps)
    return held


def _rescribe(root):
    """sync_scribes, then rebuild root once if a scribe moved."""
    if root is None or root.name in _SCRIBING:
        return
    if not sync_scribes(root):
        return
    _SCRIBING.add(root.name)
    try:
        types_face_frame.recalculate_face_frame_cabinet(root)
    finally:
        _SCRIBING.discard(root.name)


def _on_recalc(root):
    if root is None:
        return
    if root.get(JOINTS_KEY):
        apply_root(root)
    if root.get(JOINTS_KEY) or root.get(SCRIBE_KEY):
        _rescribe(root)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

def _miterable(obj):
    return (obj is not None and obj.get('hb_part_role') in ALLOWED_ROLES
            and types_face_frame.find_cabinet_root(obj) is not None)


def _picked_pair(context):
    active = context.active_object
    others = [o for o in context.selected_objects
              if o is not active and _miterable(o)]
    if not _miterable(active) or len(others) != 1:
        return None
    return active, others[0]


def _too_thin(part):
    t = GeoNodeCutpart(part).get_input('Thickness')
    return t is not None and t < MIN_THICKNESS - units.inch(0.001)


class hb_face_frame_OT_miter_parts(bpy.types.Operator):
    """Mitre the active part to the other selected part (two end stiles,
    two backs or two partitions meeting at a corner)"""
    bl_idname = "hb_face_frame.miter_parts"
    bl_label = "Miter Joint"
    bl_description = ("Miter the two selected parts into each other "
                      "where they meet")
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Miter",
        items=[('EVEN', "Even", "Both parts cut on the corner's bisector"),
               ('LONG_A', "Active Part Long",
                "One-sided: the active part runs past the corner with a "
                "square end, the other is cut to sit flat against it"),
               ('LONG_B', "Other Part Long",
                "One-sided: the other part runs past the corner with a "
                "square end, the active part is cut to sit flat against it")],
        default='EVEN')  # type: ignore

    @classmethod
    def poll(cls, context):
        pair = _picked_pair(context)
        if pair is None:
            return False
        if all(_too_thin(p) for p in pair):
            cls.poll_message_set("Parts under 1/2\" thick can't be mitered")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        pair = _picked_pair(context)
        if pair is None:
            self.report({'WARNING'}, "Select exactly two parts to miter")
            return {'CANCELLED'}
        # Only a part that gets an angled cut needs 1/2" of material; a
        # thinner part can be the straight, long part of a one-sided joint.
        cut = {'EVEN': pair, 'LONG_A': pair[1:], 'LONG_B': pair[:1]}[self.mode]
        if any(_too_thin(p) for p in cut):
            self.report({'WARNING'},
                        "A part under 1/2\" thick can't take the angled cut. "
                        "Make it the long part, or use thicker stock")
            return {'CANCELLED'}
        if not add_joint(pair[0], pair[1], self.mode):
            return {'CANCELLED'}
        self.report({'INFO'}, f"Mitered {pair[0].name} and {pair[1].name}")
        return {'FINISHED'}


class hb_face_frame_OT_remove_miter(bpy.types.Operator):
    """Take the miter joint off the active part (and its partner)"""
    bl_idname = "hb_face_frame.remove_miter"
    bl_label = "Remove Miter"
    bl_description = "Put both parts of this miter joint back to square"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return _miterable(obj) and joint_for(obj) is not None

    def execute(self, context):
        obj = context.active_object
        root = types_face_frame.find_cabinet_root(obj)
        j = joint_for(obj)
        other_root = bpy.data.objects.get(j['other_root']) if j else None
        remove_joints(obj)
        for r in (root, other_root):
            if r is not None:
                types_face_frame.recalculate_face_frame_cabinet(r)
        return {'FINISHED'}


def _draw_menu_items(self, context):
    obj = context.active_object
    if not _miterable(obj):
        return
    layout = self.layout
    layout.separator()
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("hb_face_frame.miter_parts", icon='MOD_BEVEL')
    if joint_for(obj) is not None:
        layout.operator("hb_face_frame.remove_miter", icon='X')


_MENUS = ('HOME_BUILDER_MT_face_frame_part_commands',
          'HOME_BUILDER_MT_face_frame_interior_part_commands')
_classes = (hb_face_frame_OT_miter_parts, hb_face_frame_OT_remove_miter)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    for name in _MENUS:
        menu = getattr(bpy.types, name, None)
        if menu is not None:
            menu.append(_draw_menu_items)
    if _on_recalc not in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.append(_on_recalc)


def unregister():
    if _on_recalc in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.remove(_on_recalc)
    for name in _MENUS:
        menu = getattr(bpy.types, name, None)
        if menu is not None:
            try:
                menu.remove(_draw_menu_items)
            except Exception:
                pass
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
