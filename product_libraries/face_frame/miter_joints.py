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
- LONG_SELF / LONG_OTHER: an offset miter. The long board shows the full
  miter face: it is cut from the outside corner to where its inner face
  crosses the middle of the short board's thickness. The short board takes
  the same cut over its outer half and is notched square against the long
  board's inner face over its inner half.

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
    return root.matrix_world @ m


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
    """(O, I, X_a, X_b): outside corner, inside corner, and for an offset
    miter with a (or b) long, where that board's inner face crosses the
    middle of the other's thickness."""
    ca, cb = a.centre(), b.centre()
    a_out, a_in = a.faces(cb)
    b_out, b_in = b.faces(ca)
    O = _cross(*a.line(a_out), *b.line(b_out))
    I = _cross(*a.line(a_in), *b.line(b_in))
    xa = _cross(*a.line(a_in), *b.line((b_out + b_in) / 2.0))
    xb = _cross(*b.line(b_in), *a.line((a_out + a_in) / 2.0))
    return O, I, xa, xb


def _half_plane(p, q, toward):
    """Plan quad removing everything on toward's side of line p-q."""
    u = (q - p).normalized()
    n = Vector((-u.y, u.x))
    if (toward - p).dot(n) < 0:
        n = -n
    c = (p + q) / 2.0
    return [c - u * _BIG, c + u * _BIG, c + u * _BIG + n * _BIG,
            c - u * _BIG + n * _BIG]


def _outer_miter(b_short, a_long, o_pt, x_pt):
    """Plan cone at x_pt: the short board's outer half beyond the miter
    line x_pt-o_pt (its inner half is the notch's)."""
    r1 = (o_pt - x_pt).normalized()
    n_line = Vector((-r1.y, r1.x))
    if (a_long.centre() - x_pt).dot(n_line) < 0:
        n_line = -n_line
    r2 = b_short.u if b_short.u.dot(n_line) > 0 else -b_short.u
    return [x_pt, x_pt + r1 * _BIG, x_pt + (r1 + r2) * _BIG,
            x_pt + r2 * _BIG]


def _notch(b_short, a_long, x_pt):
    """Plan cone at x_pt covering the short board's inner half beyond the
    long board's inner face (the square notch of an offset miter)."""
    ca = a_long.centre()
    cb = b_short.centre()
    a_out, a_in = a_long.faces(cb)
    b_out, b_in = b_short.faces(ca)
    # Side of the long board's inner face its outer face lies on, and
    # side of the short board's mid-plane its inner face lies on.
    n_a = a_long.n if a_out > a_in else -a_long.n
    n_b = b_short.n if b_in > b_out else -b_short.n
    v1 = a_long.u if a_long.u.dot(n_b) > 0 else -a_long.u
    v2 = b_short.u if b_short.u.dot(n_a) > 0 else -b_short.u
    return [x_pt, x_pt + v1 * _BIG, x_pt + (v1 + v2) * _BIG, x_pt + v2 * _BIG]


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
    inv = root.matrix_world.inverted()
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


def _apply_pair(me, other, mode):
    """Grow + cut `me` for its joint with `other` (other is only read)."""
    _undo_growth(me)
    a = _Board(me)
    b = _Board(other)
    O, I, x_me, x_other = _joint_points(a, b)
    if O is None or I is None:
        return
    z_lo = min(a.mw.translation.z, b.mw.translation.z) - units.inch(2.0)
    z_hi = z_lo + units.inch(200.0)
    if mode == 'EVEN':
        _grow_to(a, [O, I])
        a = _Board(me)
        quads = [_half_plane(O, I, b.centre())]
    elif mode == 'LONG_SELF':
        if x_me is None:
            return
        _grow_to(a, [O, x_me])
        a = _Board(me)
        quads = [_half_plane(O, x_me, b.centre())]
    else:   # LONG_OTHER: me is the short board
        if x_other is None:
            return
        _grow_to(a, [O, x_other])
        a = _Board(me)
        quads = [_outer_miter(a, b, O, x_other),
                 _notch(a, b, x_other)]
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


def _on_recalc(root):
    if root is not None and root.get(JOINTS_KEY):
        apply_root(root)


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
                "Offset miter: the active part shows the full miter face, "
                "the other is mitred over half its thickness and notched"),
               ('LONG_B', "Other Part Long",
                "Offset miter: the other part shows the full miter face")],
        default='EVEN')  # type: ignore

    @classmethod
    def poll(cls, context):
        pair = _picked_pair(context)
        if pair is None:
            return False
        if any(_too_thin(p) for p in pair):
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
        if any(_too_thin(p) for p in pair):
            self.report({'WARNING'},
                        "Parts under 1/2\" thick can't be mitered")
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
