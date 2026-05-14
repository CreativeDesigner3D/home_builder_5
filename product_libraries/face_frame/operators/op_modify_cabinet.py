"""Modal operator: drag bay/opening boundaries on face frame cabinets.

Slice 1: bay edges only. Hover to highlight a mid-stile centerline,
LMB-drag to resize the two adjacent bays, LMB-release commits and
auto-locks the new widths via the bay-width property setter.

Visual overlay (POST_PIXEL):
- All editable boundary candidates drawn as faint vertical lines.
- The hovered or active boundary drawn brighter and thicker.
- Locked bays get a subtle tint over their FF rectangle plus a small
  padlock glyph at the top-right corner.
- During a drag, dimension text is drawn over the two affected bays
  showing the current width, plus the offset near the cursor.
- Snap markers appear when the cursor is near a fractional inch
  increment or aligns with another boundary's FF X across the scene.

Numeric input (typed digits / fraction / inches mark) overrides the
cursor-driven offset until cleared. Tab cycles snap modes (off / coarse
/ fine). Shift disables snap. Enter commits the modal session; Esc /
RMB cancels the active drag if there is one, otherwise the session.
"""
import bpy
import gpu
import blf
import math
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

from .. import solver_face_frame as solver
from .. import types_face_frame
from .... import hb_types
from ....units import inch


# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
HIT_TOLERANCE_PX = 12.0
SNAP_PX = 8.0
SNAP_FRACTIONS = (inch(1.0), inch(0.5), inch(0.25), inch(0.125))
MIN_BAY_WIDTH = inch(2.0)
MIN_OPENING_SIZE = inch(1.0)
LOCK_TINT = (0.95, 0.55, 0.10, 0.10)        # warm tint for locked bays
HOVER_LINE = (1.00, 0.85, 0.20, 1.00)
ACTIVE_LINE = (1.00, 0.65, 0.10, 1.00)
GHOST_LINE = (0.85, 0.85, 0.85, 0.35)
DIM_TEXT = (1.00, 1.00, 1.00, 1.00)
SNAP_MARKER = (0.40, 0.85, 1.00, 1.00)
LOCK_GLYPH = (1.00, 0.85, 0.20, 1.00)


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------
def _member_is_cabinet(obj):
    return bool(obj.get(types_face_frame.TAG_CABINET_CAGE))


def _member_width(obj):
    """Member width — cabinet width prop for cages, Dim X for appliances."""
    if _member_is_cabinet(obj):
        return obj.face_frame_cabinet.width
    return hb_types.GeoNodeObject(obj).get_input('Dim X')


def _member_is_locked(obj):
    """Locked members hold their width during a group resize. Appliances
    are always locked (their physical width doesn't flex)."""
    if _member_is_cabinet(obj):
        return bool(obj.face_frame_cabinet.lock_width)
    return True


def _member_set_width(obj, w):
    """Write a new width. No-op for appliances (they're locked)."""
    if _member_is_cabinet(obj):
        obj.face_frame_cabinet.width = w


def _row_key(obj):
    """Bucket members into rows by rotation around Z. 0 and pi are the
    two cases that matter for islands (front row vs back row); anything
    else rounds to the nearest pi/4 step so an angled run also groups
    cleanly with itself.
    """
    rot_z = obj.rotation_euler.z
    quantum = math.pi / 4
    key = round(rot_z / quantum) * quantum
    # Normalize to [-pi, pi] so e.g. 2pi and 0 share a key.
    while key > math.pi:
        key -= 2 * math.pi
    while key <= -math.pi:
        key += 2 * math.pi
    return round(key, 4)


class GroupLayout:
    """Minimal layout adapter so the solver's FF-plane helpers (which
    expect a FaceFrameLayout) can be reused for a cabinet group.

    The group cage stands in for a cabinet: its local +X is the run
    direction, its local +Z is up, its outer face is at local y =
    -dim_y (matching the Mirror-Y cage convention). The basis-building
    helpers in solver_face_frame only read dim_x, dim_y, is_angled,
    and the blind offsets — keeping this class to that subset is
    enough to make ff_local_to_world / mouse_to_ff_local /
    face_frame_world_basis behave correctly for groups.

    dim_x is computed live from the sum of member cabinet widths
    rather than re-read from the cage's Dim X input, so the FF basis
    tracks edits made during a drag even if the cage modifier hasn't
    been refreshed yet.
    """

    def __init__(self, group_obj):
        geo = hb_types.GeoNodeObject(group_obj)
        # dim_x = widest row's total width, summing cabinets AND
        # appliances. Earlier version summed cabinets only, which made
        # the GROUP_OUTER_RIGHT drag line land short by the appliance's
        # width. Bucketing by rotation handles front-back island runs:
        # each row sums independently, and the widest wins.
        members = [c for c in group_obj.children
                   if c.get(types_face_frame.TAG_CABINET_CAGE)
                   or c.get('IS_APPLIANCE')]
        row_totals = {}
        for m in members:
            key = _row_key(m)
            row_totals[key] = row_totals.get(key, 0.0) + _member_width(m)
        if row_totals:
            self.dim_x = max(row_totals.values())
        else:
            self.dim_x = geo.get_input('Dim X')
        self.dim_y = geo.get_input('Dim Y')
        self.dim_z = geo.get_input('Dim Z')
        self.is_angled = False
        self.blind_offset_left = 0.0
        self.blind_offset_right = 0.0
        # Cabinets only (no appliances) for CABINET_BOUNDARY records -
        # those record adjacent face-frame cabinet pairs the user can
        # drag between. Appliances are locked and don't participate.
        self.cabinets = sorted(
            [c for c in group_obj.children
             if c.get(types_face_frame.TAG_CABINET_CAGE)],
            key=lambda c: c.location.x,
        )


def group_boundary_records(group_obj, layout):
    """Boundary records for a Grab Cabinet Group session.

    Phase A: only CABINET_BOUNDARY records (between adjacent member
    cabinets). Group outer-edge drags (which would distribute a
    delta across unlocked members based on face_frame_cabinet.lock_
    width) land in a follow-up edit.

    cabinet_obj on each record is the group itself — the FF basis used
    for screen projection is the group's frame, not any one member's.
    """
    # Bucket every member by row using rotation around Z. CABINET_
    # BOUNDARY records only make sense within a single row (a "boundary"
    # between a front-row and back-row cabinet isn't a thing — they're
    # not spatially adjacent along either row's run). Walking each row
    # left-to-right in group-local X, the running_x accumulates over
    # ALL members (cabinets AND appliances) so the boundary ff_x lands
    # at the actual cabinet-cabinet abutment. Boundaries are only
    # emitted between consecutive face-frame cabinets within a row;
    # appliance-adjacent edges are skipped because appliances can't
    # absorb a width shift.
    rows_by_key = {}
    for m in group_obj.children:
        if not (m.get(types_face_frame.TAG_CABINET_CAGE)
                or m.get('IS_APPLIANCE')):
            continue
        w = _member_width(m)
        rot = m.rotation_euler.z
        is_back = abs(abs(rot) - math.pi) < 0.1
        leading_offset = w if is_back else 0.0
        left_gx = m.location.x - leading_offset
        rows_by_key.setdefault(_row_key(m), []).append({
            'obj': m,
            'width': w,
            'left_gx': left_gx,
        })

    edge_index = 0
    for row_entries in rows_by_key.values():
        row_entries.sort(key=lambda e: e['left_gx'])
        # running_x advances by every member's width so cabinet
        # boundaries land at the right group-local X even when an
        # appliance sits between two cabinets.
        running_x = row_entries[0]['left_gx']
        for i in range(len(row_entries) - 1):
            running_x += row_entries[i]['width']
            left = row_entries[i]['obj']
            right = row_entries[i + 1]['obj']
            if not (_member_is_cabinet(left) and _member_is_cabinet(right)):
                continue
            ff_z_high = min(left.face_frame_cabinet.height,
                            right.face_frame_cabinet.height)
            yield {
                'kind': 'CABINET_BOUNDARY',
                'axis': 'X',
                'primary_sign': 1.0,
                'cabinet_obj': group_obj,
                'edge_index': edge_index,
                'left_cab_name': left.name,
                'right_cab_name': right.name,
                'ff_x': running_x,
                'ff_z_low': 0.0,
                'ff_z_high': ff_z_high,
                'locked_left': bool(left.face_frame_cabinet.lock_width),
                'locked_right': bool(right.face_frame_cabinet.lock_width),
            }
            edge_index += 1

    # Outer right edge of the group. Dragging grows / shrinks the
    # group; unlocked member cabinets absorb the delta proportionally
    # by their current width, locked ones hold.
    yield {
        'kind': 'GROUP_OUTER_RIGHT',
        'axis': 'X',
        'primary_sign': 1.0,
        'cabinet_obj': group_obj,
        'ff_x': layout.dim_x,
        'ff_z_low': 0.0,
        'ff_z_high': layout.dim_z,
    }
    # Outer left edge. Same distribution math, plus a group translation
    # so the right edge stays put while the left moves.
    yield {
        'kind': 'GROUP_OUTER_LEFT',
        'axis': 'X',
        'primary_sign': -1.0,
        'translate': True,
        'translate_axis': 'X',
        'cabinet_obj': group_obj,
        'ff_x': 0.0,
        'ff_z_low': 0.0,
        'ff_z_high': layout.dim_z,
    }


def _collect_group_boundaries(group_obj):
    """Build the (boundary, layout) list for a single cabinet group.

    Mirrors _collect_boundaries' shape but scoped to one group, using
    GroupLayout instead of FaceFrameLayout.
    """
    if group_obj is None or not group_obj.get('IS_CAGE_GROUP'):
        return []
    layout = GroupLayout(group_obj)
    return [(b, layout) for b in group_boundary_records(group_obj, layout)]


def _iter_face_frame_cabinets(scene):
    for obj in scene.objects:
        if obj.get(types_face_frame.TAG_CABINET_CAGE):
            yield obj


def _snapshot_session(scene):
    """Capture per-bay widths, cabinet widths, and the matching lock
    flags for every face-frame cabinet in the scene. Used to roll back
    on Esc - covers any grab variant's edits without per-variant
    bookkeeping.
    """
    snap = {'bays': {}, 'cabinets': {}}
    for cab in _iter_face_frame_cabinets(scene):
        bays = sorted(
            [c for c in cab.children if c.get(types_face_frame.TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        snap['bays'][cab.name] = [
            {
                'bay_name': b.name,
                'width': b.face_frame_bay.width,
                'unlock_width': b.face_frame_bay.unlock_width,
            }
            for b in bays
        ]
        snap['cabinets'][cab.name] = {
            'width': cab.face_frame_cabinet.width,
            'lock_width': cab.face_frame_cabinet.lock_width,
        }
    return snap


def _restore_session(snap):
    """Restore per-bay widths, cabinet widths, and the matching lock
    flags from a snapshot. Cabinets restored before bays so the
    cabinet-level recalc fires once with the correct outer width,
    rather than running per-bay and triggering a redistribution
    against a still-stale cabinet width.
    """
    for cab_name, state in snap.get('cabinets', {}).items():
        cab = bpy.data.objects.get(cab_name)
        if cab is None:
            continue
        cp = cab.face_frame_cabinet
        # Restore lock_width first so the width setter doesn't see
        # an inconsistent intermediate state.
        cp.lock_width = state['lock_width']
        cp.width = state['width']
    for cab_name, bay_states in snap.get('bays', {}).items():
        for state in bay_states:
            bay = bpy.data.objects.get(state['bay_name'])
            if bay is None:
                continue
            bp = bay.face_frame_bay
            bp.unlock_width = state['unlock_width']
            bp.width = state['width']


# ---------------------------------------------------------------------------
# Boundary collection
# ---------------------------------------------------------------------------
def _collect_boundaries(scene, collector):
    """Walk every face-frame cabinet and gather boundary records using
    the supplied collector function (one per grab-operator variant).
    Returns list of (boundary, layout) tuples."""
    out = []
    for cab in _iter_face_frame_cabinets(scene):
        layout = solver.FaceFrameLayout(cab)
        for b in collector(cab, layout):
            out.append((b, layout))
    return out


# ---------------------------------------------------------------------------
# Screen-space projection helpers
# ---------------------------------------------------------------------------
def _ff_to_screen(region, rv3d, cabinet_obj, layout, ff_x, ff_z):
    """Project an FF-local point to 2D screen coords. Returns Vector or
    None if the point is behind the camera or off-region."""
    world = solver.ff_local_to_world(cabinet_obj, layout, ff_x, ff_z)
    co2d = view3d_utils.location_3d_to_region_2d(region, rv3d, world)
    return co2d


def _boundary_endpoints_ff(b):
    """Return the two FF-local endpoints of a boundary's drawn line as
    pairs (ff_x, ff_z). Vertical lines (axis 'X') span ff_z; horizontal
    lines (axis 'Z') span ff_x."""
    if b['axis'] == 'X':
        return (b['ff_x'], b['ff_z_low']), (b['ff_x'], b['ff_z_high'])
    return (b['ff_x_low'], b['ff_z']), (b['ff_x_high'], b['ff_z'])


def _boundary_screen_distance(region, rv3d, b, layout, mouse_xy):
    """Distance in pixels from mouse_xy to the boundary's drawn line
    segment, axis-aware. Returns +inf if not projectable."""
    p1_ff, p2_ff = _boundary_endpoints_ff(b)
    a = _ff_to_screen(region, rv3d, b['cabinet_obj'], layout,
                      p1_ff[0], p1_ff[1])
    z = _ff_to_screen(region, rv3d, b['cabinet_obj'], layout,
                      p2_ff[0], p2_ff[1])
    if a is None or z is None:
        return float('inf')
    p = Vector((mouse_xy[0], mouse_xy[1]))
    seg = z - a
    seg_len2 = seg.length_squared
    if seg_len2 < 1e-6:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(seg) / seg_len2))
    proj = a + seg * t
    return (p - proj).length


# ---------------------------------------------------------------------------
# Snap math
# ---------------------------------------------------------------------------
def _proposed_point_for_snap(b, proposed):
    """FF-local point at which to evaluate snapping. For axis 'X' the
    proposed value is the new ff_x and we evaluate at ff_z_low; for
    axis 'Z' the proposed value is the new ff_z and we evaluate at
    ff_x_low. Returns (ff_x, ff_z)."""
    if b['axis'] == 'X':
        return (proposed, b['ff_z_low'])
    return (b['ff_x_low'], proposed)


def _other_anchor_point_ff(other_b):
    """A reference (ff_x, ff_z) on `other_b` to align against. For
    axis 'X' boundaries we use (ff_x, ff_z_low); for axis 'Z' we use
    (ff_x_low, ff_z)."""
    if other_b['axis'] == 'X':
        return (other_b['ff_x'], other_b['ff_z_low'])
    return (other_b['ff_x_low'], other_b['ff_z'])


def _snap_offset(proposed, region, rv3d, b, layout,
                 all_boundaries, snap_mode):
    """Axis-aware snap. `proposed` is on b's drag axis (ff_x or ff_z).
    Returns (snapped, snap_kind | None).

    Alignment snap uses the screen-axis matching the drag axis: vertical
    boundaries align by screen X, horizontal boundaries by screen Y.
    """
    if snap_mode == 'OFF':
        return proposed, None
    cabinet_obj = b['cabinet_obj']
    self_pt = _proposed_point_for_snap(b, proposed)
    proj_self = _ff_to_screen(region, rv3d, cabinet_obj, layout,
                              self_pt[0], self_pt[1])
    drag_screen_axis = 'x' if b['axis'] == 'X' else 'y'
    # 1. Alignment to other boundaries on the SAME drag axis. Same-axis
    # only because cross-axis alignment isn't meaningful (aligning a
    # vertical line's screen.y to a horizontal line's anchor projects
    # to whatever the horizontal line's left endpoint happens to be —
    # not a target the user could reason about). It also caused visible
    # flicker on vertical drags: every BAY_EDGE / MID_STILE in the
    # scene has its alignment anchor at its ff_z_low, all clustered at
    # bay-bottom level, so dragging through that band rapidly switches
    # between dozens of near-identical targets.
    if proj_self is not None:
        best = None
        best_dist = SNAP_PX
        for other_b, other_layout in all_boundaries:
            if other_b is b:
                continue
            if other_b['axis'] != b['axis']:
                continue
            opt = _other_anchor_point_ff(other_b)
            other_screen = _ff_to_screen(
                region, rv3d, other_b['cabinet_obj'], other_layout,
                opt[0], opt[1])
            if other_screen is None:
                continue
            d = abs(getattr(other_screen, drag_screen_axis)
                    - getattr(proj_self, drag_screen_axis))
            if d < best_dist:
                best_dist = d
                best = (other_b, other_layout, opt)
        if best is not None:
            other_b, other_layout, opt = best
            other_world = solver.ff_local_to_world(
                other_b['cabinet_obj'], other_layout, opt[0], opt[1])
            origin_w, x_axis_w, z_axis_w, _n = solver.face_frame_world_basis(
                cabinet_obj, layout)
            if b['axis'] == 'X':
                snapped = (other_world - origin_w).dot(x_axis_w)
            else:
                snapped = (other_world - origin_w).dot(z_axis_w)
            return snapped, ('ALIGN', other_b)
    # 2. Fractional inch snap
    fractions = SNAP_FRACTIONS if snap_mode == 'FINE' else SNAP_FRACTIONS[:2]
    best_frac = None
    best_frac_dist = float('inf')
    for f in fractions:
        snapped = round(proposed / f) * f
        d = abs(proposed - snapped)
        if d < best_frac_dist:
            best_frac_dist = d
            best_frac = snapped
    if best_frac is not None and proj_self is not None:
        snap_pt = _proposed_point_for_snap(b, best_frac)
        proj_snap = _ff_to_screen(region, rv3d, cabinet_obj, layout,
                                  snap_pt[0], snap_pt[1])
        if proj_snap is not None and (proj_snap - proj_self).length < SNAP_PX:
            return best_frac, ('FRACTION', best_frac)
    return proposed, None


# ---------------------------------------------------------------------------
# GPU draw
# ---------------------------------------------------------------------------
def _draw_line_2d(shader, p1, p2, color, width=1.0):
    if p1 is None or p2 is None:
        return
    gpu.state.line_width_set(width)
    shader.uniform_float("color", color)
    batch = batch_for_shader(shader, 'LINES',
                             {"pos": [(p1.x, p1.y), (p2.x, p2.y)]})
    batch.draw(shader)


def _draw_quad_2d(shader, corners, color):
    """corners: 4 Vector2 in CCW order. Filled quad."""
    if any(c is None for c in corners):
        return
    shader.uniform_float("color", color)
    verts = [(c.x, c.y) for c in corners]
    indices = [(0, 1, 2), (0, 2, 3)]
    batch = batch_for_shader(
        shader, 'TRIS', {"pos": verts}, indices=indices)
    batch.draw(shader)


def _draw_padlock(shader, x, y, color, size=10.0):
    """Tiny GPU padlock anchored at top-right corner of a rect.
    Body is a rect; shackle is a half-arc above the body."""
    bw = size
    bh = size * 0.7
    bx = x - bw
    by = y - bh
    body = [
        Vector((bx, by)),
        Vector((bx + bw, by)),
        Vector((bx + bw, by + bh)),
        Vector((bx, by + bh)),
    ]
    _draw_quad_2d(shader, body, color)
    # Shackle: half-circle above the body
    shader.uniform_float("color", color)
    cx = bx + bw * 0.5
    cy = by + bh
    r = bw * 0.32
    segs = 10
    pts = []
    for i in range(segs + 1):
        a = math.pi * (i / segs)  # 0..pi (left-to-right over the top)
        pts.append((cx + r * math.cos(math.pi - a), cy + r * math.sin(a)))
    gpu.state.line_width_set(1.5)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": pts})
    batch.draw(shader)


def _bay_rect_screen(region, rv3d, cabinet_obj, layout, bay_idx):
    """Four-corner FF rect of a bay in screen space (CCW from bottom-
    left). Returns list of Vector2 or None if any corner fails to
    project."""
    x0 = solver.bay_x_position(layout, bay_idx)
    x1 = x0 + layout.bays[bay_idx]['width']
    z0 = solver.bay_bottom_z(layout, bay_idx)
    z1 = solver.bay_top_z(layout, bay_idx)
    corners = []
    for ff_x, ff_z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        c = _ff_to_screen(region, rv3d, cabinet_obj, layout, ff_x, ff_z)
        if c is None:
            return None
        corners.append(c)
    return corners


def _draw_text(x, y, text, color, size=12):
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    w, h = blf.dimensions(font_id, text)
    blf.position(font_id, x - w / 2, y - h / 2, 0)
    blf.draw(font_id, text)


def _format_inches(meters):
    """Display helper: convert meters back to a fractional-inch string
    for dimension labels."""
    inches = meters / 0.0254
    whole = int(inches)
    frac = inches - whole
    sixteenths = round(frac * 16)
    if sixteenths == 16:
        whole += 1
        sixteenths = 0
    if sixteenths == 0:
        return f"{whole}\""
    # reduce
    g = math.gcd(sixteenths, 16)
    return f"{whole} {sixteenths // g}/{16 // g}\""


def _opening_rect_screen(region, rv3d, cabinet_obj, layout, leaf_rect, bay_index):
    """Four-corner FF rect of an opening leaf in screen space (CCW from
    bottom-left). leaf_rect is one entry from bay_openings()['leaves'].
    Coords come back in BAY-local; convert to FF-local via the bay's
    cage origin."""
    cage_left_x, _ = solver._cage_x_bounds(layout, bay_index)
    cage_bottom_z = (solver.bay_bottom_z(layout, bay_index)
                     + layout.bays[bay_index]['bottom_rail_width'])
    x0 = cage_left_x + leaf_rect['cage_x']
    x1 = x0 + leaf_rect['cage_dim_x']
    z0 = cage_bottom_z + leaf_rect['cage_z']
    z1 = z0 + leaf_rect['cage_dim_z']
    corners = []
    for ff_x, ff_z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        c = _ff_to_screen(region, rv3d, cabinet_obj, layout, ff_x, ff_z)
        if c is None:
            return None
        corners.append(c)
    return corners


def _draw_callback(op, context):
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    # Reset clickable-lock targets for this draw pass. Modal LMB-press
    # scans this list before falling through to boundary picking.
    op._lock_targets = []
    # 1. Locked-bay tints + padlock glyphs
    for cab in _iter_face_frame_cabinets(context.scene):
        layout = solver.FaceFrameLayout(cab)
        bay_objs = sorted(
            [c for c in cab.children if c.get(types_face_frame.TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        for i, bay in enumerate(bay_objs):
            if bay.face_frame_bay.unlock_width:
                corners = _bay_rect_screen(region, rv3d, cab, layout, i)
                if corners is not None:
                    _draw_quad_2d(shader, corners, LOCK_TINT)
                    # Bay locks sit centered on the bay's top edge so
                    # they're spatially distinct from opening locks
                    # (which hug the right edge). Average both top
                    # corners to stay correct under perspective skew.
                    top_left = corners[3]
                    top_right = corners[2]
                    top_center_x = 0.5 * (top_left.x + top_right.x)
                    top_center_y = 0.5 * (top_left.y + top_right.y)
                    # _draw_padlock's (x, y) is the body's top-right.
                    # Shift right by bw/2 (=5) so body centers on the
                    # top edge; inset 4 below so shackle clears rail.
                    icon_anchor_x = top_center_x + 5.0
                    icon_anchor_y = top_center_y - 4
                    _draw_padlock(shader, icon_anchor_x, icon_anchor_y,
                                  LOCK_GLYPH, size=10.0)
                    op._lock_targets.append({
                        'kind': 'BAY',
                        'target_name': bay.name,
                        'cx': icon_anchor_x - 5,
                        'cy': icon_anchor_y - 3.5,
                    })
            # Locked-opening tints + padlock glyphs (per-leaf)
            leaves = solver.bay_openings(layout, i).get('leaves', [])
            for leaf in leaves:
                leaf_obj = bpy.data.objects.get(leaf['obj_name'])
                if leaf_obj is None:
                    continue
                if not leaf_obj.face_frame_opening.unlock_size:
                    continue
                corners = _opening_rect_screen(
                    region, rv3d, cab, layout, leaf, i)
                if corners is None:
                    continue
                _draw_quad_2d(shader, corners, LOCK_TINT)
                # Opening locks hang on the right edge, vertically
                # centered on the opening. Pairs with bay locks
                # (top-center) so the two kinds never collide.
                bottom_right = corners[1]
                top_right = corners[2]
                right_edge_x = 0.5 * (bottom_right.x + top_right.x)
                right_mid_y = 0.5 * (bottom_right.y + top_right.y)
                # _draw_padlock's (x, y) is the body's top-right.
                # Inset 4 inboard from the right edge; shift up by
                # bh/2 (=3.5) so body centers on right_mid_y.
                icon_anchor_x = right_edge_x - 4
                icon_anchor_y = right_mid_y + 3.5
                _draw_padlock(shader, icon_anchor_x, icon_anchor_y,
                              LOCK_GLYPH, size=10.0)
                op._lock_targets.append({
                    'kind': 'OPENING',
                    'target_name': leaf['obj_name'],
                    'cx': icon_anchor_x - 5,
                    'cy': icon_anchor_y - 3.5,
                })
    # 2. Boundary lines
    for b, layout in op._boundaries:
        p1_ff, p2_ff = _boundary_endpoints_ff(b)
        a = _ff_to_screen(region, rv3d, b['cabinet_obj'], layout,
                          p1_ff[0], p1_ff[1])
        z = _ff_to_screen(region, rv3d, b['cabinet_obj'], layout,
                          p2_ff[0], p2_ff[1])
        is_active = (op._drag_boundary is b) or (op._hover_boundary is b)
        color = ACTIVE_LINE if is_active else GHOST_LINE
        width = 2.5 if is_active else 1.0
        _draw_line_2d(shader, a, z, color, width)
    # 3. Drag dimensions + snap marker
    if op._drag_active and op._drag_boundary is not None:
        b = op._drag_boundary
        layout = op._drag_layout
        cab = b['cabinet_obj']
        snap = op._drag_snapshot or []
        if b['kind'] in ('OUTER_RIGHT', 'OUTER_LEFT',
                         'OUTER_TOP', 'OUTER_BOTTOM',
                         'TOE_KICK'):
            # Single-neighbor drag: one label at the boundary's
            # midpoint showing the current cabinet dim.
            cur = getattr(cab.face_frame_cabinet, b['dim_attr'])
            if b['axis'] == 'X':
                mid_pt = (b['ff_x'], 0.5 * (b['ff_z_low'] + b['ff_z_high']))
            else:
                mid_pt = (0.5 * (b['ff_x_low'] + b['ff_x_high']), b['ff_z'])
            scr = _ff_to_screen(region, rv3d, cab, layout,
                                mid_pt[0], mid_pt[1])
            if scr is not None:
                _draw_text(scr.x, scr.y, _format_inches(cur),
                           DIM_TEXT, size=14)
        elif b['kind'] == 'BAY_HANDLE':
            # Per-bay handle: label the bay's current attr value at the
            # boundary midpoint.
            bay_obj = bpy.data.objects.get(b['bay_obj_name'])
            if bay_obj is not None:
                cur = getattr(bay_obj.face_frame_bay, b['attr'])
                mid_pt = (0.5 * (b['ff_x_low'] + b['ff_x_high']), b['ff_z'])
                scr = _ff_to_screen(region, rv3d, cab, layout,
                                    mid_pt[0], mid_pt[1])
                if scr is not None:
                    _draw_text(scr.x, scr.y, _format_inches(cur),
                               DIM_TEXT, size=14)
        elif b['kind'] == 'BAY_EDGE':
            for bay_idx in (b['left_bay_idx'], b['right_bay_idx']):
                x0 = solver.bay_x_position(layout, bay_idx)
                x1 = x0 + layout.bays[bay_idx]['width']
                zmid = 0.5 * (solver.bay_bottom_z(layout, bay_idx)
                              + solver.bay_top_z(layout, bay_idx))
                cx_ff = 0.5 * (x0 + x1)
                scr = _ff_to_screen(region, rv3d, cab, layout, cx_ff, zmid)
                if scr is not None:
                    _draw_text(scr.x, scr.y,
                               _format_inches(layout.bays[bay_idx]['width']),
                               DIM_TEXT, size=14)
        else:
            # MID_STILE / MID_RAIL: label the two affected children's
            # current size at their rect centers.
            for state in snap:
                obj = bpy.data.objects.get(state['name'])
                if obj is None:
                    continue
                pg = (obj.face_frame_opening
                      if obj.get(types_face_frame.TAG_OPENING_CAGE)
                      else obj.face_frame_split)
                # For label placement: project a point near the
                # boundary's centerline biased toward each child. Use
                # the matrix_world of the child's cage if it has one,
                # otherwise fall back to a midpoint along the boundary.
                if obj.get(types_face_frame.TAG_OPENING_CAGE):
                    # Find this leaf in any bay - bay_index is on the
                    # boundary record.
                    bi = b['bay_index']
                    leaves = solver.bay_openings(layout, bi).get('leaves', [])
                    leaf_match = next(
                        (lf for lf in leaves
                         if lf['obj_name'] == state['name']), None)
                    if leaf_match is None:
                        continue
                    cage_left_x, _ = solver._cage_x_bounds(layout, bi)
                    cage_bottom_z = (
                        solver.bay_bottom_z(layout, bi)
                        + layout.bays[bi]['bottom_rail_width'])
                    cx_ff = (cage_left_x + leaf_match['cage_x']
                             + leaf_match['cage_dim_x'] * 0.5)
                    cz_ff = (cage_bottom_z + leaf_match['cage_z']
                             + leaf_match['cage_dim_z'] * 0.5)
                    scr = _ff_to_screen(region, rv3d, cab, layout,
                                        cx_ff, cz_ff)
                    if scr is not None:
                        _draw_text(scr.x, scr.y,
                                   _format_inches(pg.size),
                                   DIM_TEXT, size=14)
        # Snap marker
        if op._snap_kind is not None:
            if b['axis'] == 'X':
                marker_pt = (b['ff_x'], b['ff_z_high'])
            else:
                marker_pt = (b['ff_x_high'], b['ff_z'])
            scr = _ff_to_screen(region, rv3d, cab, layout,
                                marker_pt[0], marker_pt[1])
            if scr is not None:
                r = 6
                pts = [(scr.x, scr.y + r), (scr.x + r, scr.y),
                       (scr.x, scr.y - r), (scr.x - r, scr.y),
                       (scr.x, scr.y + r)]
                gpu.state.line_width_set(2.0)
                shader.uniform_float("color", SNAP_MARKER)
                batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": pts})
                batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


# ---------------------------------------------------------------------------
# Modal operator: shared mixin + per-scope subclasses
# ---------------------------------------------------------------------------
# The grab UX — hover-pick a boundary, drag with snap, auto-lock,
# click-to-unlock — is identical regardless of which boundaries the
# operator exposes. Subclasses set BOUNDARY_COLLECTOR to a function
# that yields the relevant boundary records for that scope (face frame
# internals, cabinet outer dims, walls, etc. as the pattern grows).
class _GrabBaseMixin:
    """Shared modal lifecycle, GPU draw, snap, drag, commit, and
    click-to-unlock machinery for grab-style operators.

    Subclasses must set:
      BOUNDARY_COLLECTOR — callable(cabinet_obj, layout) -> iterable of
                           boundary records.
    Subclasses must also set bl_idname / bl_label / bl_description /
    bl_options on themselves.
    """
    BOUNDARY_COLLECTOR = None

    # Subclasses can override _collect to scope boundary collection to
    # a specific object (e.g. a cabinet group) instead of iterating
    # every face-frame cabinet in the scene. Default returns the
    # scene-wide list via the existing per-cabinet collector.
    def _collect(self):
        return _collect_boundaries(bpy.context.scene, self.BOUNDARY_COLLECTOR)


    # Session state
    _session_snapshot = None
    _draw_handle = None
    _boundaries = None
    _hover_boundary = None
    _drag_boundary = None
    _drag_layout = None
    _drag_snapshot = None       # bay_widths list at drag start
    _drag_active = False
    _drag_origin_ff = 0.0          # cursor pos on drag axis at click
    _drag_origin_boundary = 0.0    # boundary's drag-axis value at click
    _drag_basis = None             # cached FF basis (origin, x, z, normal)
    _snap_mode = 'COARSE'       # OFF | COARSE | FINE
    _snap_disabled_temp = False # Shift held
    _snap_kind = None
    _typed = ''
    _typing = False
    _lock_targets = None        # list[dict] populated by draw, consumed by LMB

    @classmethod
    def poll(cls, context):
        return any(
            o.get(types_face_frame.TAG_CABINET_CAGE)
            for o in context.scene.objects
        )

    # ---- Lifecycle ----

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from a 3D Viewport")
            return {'CANCELLED'}
        self._session_snapshot = _snapshot_session(context.scene)
        self._boundaries = self._collect()
        if not self._boundaries:
            self.report({'INFO'}, "No editable boundaries found")
            return {'CANCELLED'}
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        # bl_label leads so the mode is identified up front. Area
        # header (top of viewport) is more visible than the workspace
        # status bar; matches the draw_walls / change_room_size
        # convention. Mention click-to-unlock since the lock-icon
        # affordance is otherwise only discoverable by experiment.
        context.area.header_text_set(
            f"{self.bl_label}  |  LMB: drag boundary or click lock"
            f" to unlock  |  Type: numeric  |  Tab: cycle snap"
            f"  |  Shift: hold to disable snap  |  Enter: confirm"
            f"  |  Esc / RMB: cancel"
        )
        context.window.cursor_modal_set('SCROLL_XY')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _cleanup(self, context):
        if self._draw_handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    self._draw_handle, 'WINDOW')
            except Exception:
                pass
            self._draw_handle = None
        try:
            if context.area is not None:
                context.area.header_text_set(None)
        except Exception:
            pass
        try:
            if context.window is not None:
                context.window.cursor_modal_restore()
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    # ---- Boundary picking ----

    LOCK_ICON_HIT_TOL = 14.0

    def _handle_lock_click(self, context, event):
        """Scan the lock-icon screen positions recorded by the most
        recent draw pass. If the click lands within tolerance, unset the
        corresponding unlock flag (which fires the prop's update callback
        and triggers a recalc), refresh boundaries, and report True.

        Returns False if no icon was hit (caller should fall through to
        boundary picking).
        """
        targets = self._lock_targets or []
        if not targets:
            return False
        mx, my = event.mouse_region_x, event.mouse_region_y
        best = None
        best_d2 = self.LOCK_ICON_HIT_TOL ** 2
        for t in targets:
            dx = mx - t['cx']
            dy = my - t['cy']
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = t
        if best is None:
            return False
        obj = bpy.data.objects.get(best['target_name'])
        if obj is None:
            return True  # consumed; nothing to do
        if best['kind'] == 'BAY':
            obj.face_frame_bay.unlock_width = False
        else:
            obj.face_frame_opening.unlock_size = False
        # Boundaries change because freshly-unlocked children re-share
        # their sibling space; the icon also disappears.
        self._boundaries = self._collect()
        return True

    def _pick_boundary(self, context, event):
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return None
        mxy = (event.mouse_region_x, event.mouse_region_y)
        best = None
        best_d = HIT_TOLERANCE_PX
        for b, layout in self._boundaries:
            d = _boundary_screen_distance(region, rv3d, b, layout, mxy)
            if d < best_d:
                best_d = d
                best = (b, layout)
        return best

    # ---- Drag mechanics ----

    # ---- Snapshot helpers (axis-aware, kind-dispatched) ----

    @staticmethod
    def _snapshot_neighbors(b):
        """Snapshot the affected neighbor(s) for a drag, keyed by kind.

        Returns a list of dicts. Length 2 for paired-neighbor kinds
        (BAY_EDGE, MID_STILE, MID_RAIL). Length 1 for single-neighbor
        kinds (OUTER_RIGHT, OUTER_LEFT, OUTER_TOP, TOE_KICK,
        BAY_HANDLE) where only one value changes — no paired sibling
        to compensate.
        """
        cab = b['cabinet_obj']

        if b['kind'] == 'CABINET_BOUNDARY':
            out = []
            for nm in (b['left_cab_name'], b['right_cab_name']):
                obj = bpy.data.objects.get(nm)
                if obj is None:
                    continue
                cp = obj.face_frame_cabinet
                out.append({
                    'kind': 'CABINET_WIDTH',
                    'name': obj.name,
                    'attr': 'width',
                    'unlock_attr': 'lock_width',
                    'value': cp.width,
                    'unlock': cp.lock_width,
                })
            return out

        if b['kind'] in ('GROUP_OUTER_RIGHT', 'GROUP_OUTER_LEFT'):
            group = cab  # 'cabinet_obj' on group records is the group itself
            # Collect every group member - face frame cabinets AND
            # appliances - and bucket by row using rotation around Z.
            # Within each row, sort spatially left-to-right in group-local
            # X (which depends on rotation: front-row location.x is the
            # cab's left edge, back-row location.x is the right edge).
            members = [c for c in group.children
                       if c.get(types_face_frame.TAG_CABINET_CAGE)
                       or c.get('IS_APPLIANCE')]
            rows_by_key = {}
            for m in members:
                w = _member_width(m)
                rot = m.rotation_euler.z
                # leading_offset: distance from spatial-left-edge-in-
                # group-local to the cab's location.x. 0 for front
                # (location.x sits at left edge), width for back
                # (location.x sits at right edge because rotated 180).
                is_back = abs(abs(rot) - math.pi) < 0.1
                leading_offset = w if is_back else 0.0
                left_gx = m.location.x - leading_offset
                rows_by_key.setdefault(_row_key(m), []).append({
                    'obj': m,
                    'width': w,
                    'left_gx': left_gx,
                    'is_back': is_back,
                })
            rows = []
            for key in sorted(rows_by_key.keys()):
                entries = sorted(rows_by_key[key], key=lambda e: e['left_gx'])
                rows.append({
                    'rotation_key': key,
                    'is_back_row': entries[0]['is_back'],
                    'start_gx': entries[0]['left_gx'],
                    'member_names': [e['obj'].name for e in entries],
                    'orig_widths': [e['width'] for e in entries],
                    'orig_locations':
                        [e['obj'].location.copy() for e in entries],
                    'orig_locks': [_member_is_locked(e['obj']) for e in entries],
                    'is_appliance': [not _member_is_cabinet(e['obj'])
                                     for e in entries],
                })
            state = {
                'kind': 'GROUP_DISTRIBUTE',
                'name': group.name,
                'rows': rows,
                'orig_group_world_loc':
                    group.matrix_world.translation.copy(),
                'orig_group_location': group.location.copy(),
            }
            if b.get('translate'):
                state['translate'] = True
                state['grow_sign'] = b.get('primary_sign', 1.0)
            return [state]

        if b['kind'] == 'BAY_EDGE':
            bay_objs = sorted(
                [c for c in cab.children
                 if c.get(types_face_frame.TAG_BAY_CAGE)],
                key=lambda c: c.get('hb_bay_index', 0),
            )
            out = []
            for idx in (b['left_bay_idx'], b['right_bay_idx']):
                if idx < len(bay_objs):
                    bp = bay_objs[idx].face_frame_bay
                    out.append({
                        'kind': 'BAY',
                        'name': bay_objs[idx].name,
                        'attr': 'width',
                        'unlock_attr': 'unlock_width',
                        'value': bp.width,
                        'unlock': bp.unlock_width,
                    })
            return out

        if b['kind'] == 'BAY_HANDLE':
            bay_obj = bpy.data.objects.get(b['bay_obj_name'])
            if bay_obj is None:
                return []
            bp = bay_obj.face_frame_bay
            state = {
                'kind': 'BAY',
                'name': bay_obj.name,
                'attr': b['attr'],
                'unlock_attr': b['unlock_attr'],
                'value': getattr(bp, b['attr']),
                'unlock': getattr(bp, b['unlock_attr']),
                'min_value': b.get('min_value'),
            }
            # Compensate: a paired attribute on the same bay that
            # absorbs the drag so a constraint stays satisfied (e.g.
            # upper bay top edge: top_offset shrinks while height
            # grows so bay_bottom_z stays put).
            if 'compensate_attr' in b:
                state['compensate_attr'] = b['compensate_attr']
                state['compensate_unlock_attr'] = b['compensate_unlock_attr']
                state['compensate_sign'] = b['compensate_sign']
                state['compensate_min_value'] = b['compensate_min_value']
                state['compensate_value'] = getattr(bp, b['compensate_attr'])
                state['compensate_unlock'] = getattr(
                    bp, b['compensate_unlock_attr'])
            return [state]

        if b['kind'] in ('OUTER_RIGHT', 'OUTER_LEFT',
                         'OUTER_TOP', 'OUTER_BOTTOM',
                         'TOE_KICK'):
            dim_attr = b['dim_attr']
            state = {
                'kind': 'CABINET_DIM',
                'name': cab.name,
                'dim': dim_attr,
                'value': getattr(cab.face_frame_cabinet, dim_attr),
                'unlock': None,
            }
            # Translate companion: dragging the LEFT or BOTTOM edge
            # also moves the cabinet's location so the opposite edge
            # stays put. translate_axis selects which FF basis axis to
            # translate along (matched against the cached drag basis
            # at write time).
            if b.get('translate'):
                state['translate'] = True
                state['translate_axis'] = b['translate_axis']
                state['grow_sign'] = b.get('primary_sign', 1.0)
                state['orig_world_loc'] = cab.matrix_world.translation.copy()
                state['orig_location'] = cab.location.copy()
            return [state]

        # MID_STILE / MID_RAIL: tree children
        if b['kind'] == 'MID_STILE':
            primary = b['left_child_name']
            secondary = b['right_child_name']
        else:
            primary = b['top_child_name']
            secondary = b['bottom_child_name']
        out = []
        for nm in (primary, secondary):
            obj = bpy.data.objects.get(nm)
            if obj is None:
                continue
            pg = (obj.face_frame_opening
                  if obj.get(types_face_frame.TAG_OPENING_CAGE)
                  else obj.face_frame_split)
            out.append({
                'kind': 'TREE_CHILD',
                'name': nm,
                'value': pg.size,
                'unlock': pg.unlock_size,
            })
        return out

    def _write_neighbor(self, state, new_value, write_unlock, delta=None):
        """Apply a new value to one snapshot record. Auto-lock semantics
        vary by kind:
          BAY        - explicitly set the unlock flag named by the
                       state, then write the attribute. If the state
                       carries a compensate_attr, compute the
                       compensating value from delta and write it too
                       (with its own auto-lock).
          CABINET_DIM- write the named dim. If translate is set, also
                       shift cab.location along the cached drag basis
                       so the opposite edge stays put.
          TREE_CHILD - explicit unlock_size = True alongside size write
        """
        obj = bpy.data.objects.get(state['name'])
        if obj is None:
            return
        if state['kind'] == 'BAY':
            bp = obj.face_frame_bay
            unlock_attr = state['unlock_attr']
            if write_unlock and not getattr(bp, unlock_attr):
                setattr(bp, unlock_attr, True)
            setattr(bp, state['attr'], new_value)
            # Compensate write: derive new value from the same delta
            # that drove the primary so the constraint stays satisfied.
            if 'compensate_attr' in state and delta is not None:
                c_attr = state['compensate_attr']
                c_unlock_attr = state['compensate_unlock_attr']
                c_sign = state['compensate_sign']
                c_orig = state['compensate_value']
                c_new = c_orig + c_sign * delta
                if write_unlock and not getattr(bp, c_unlock_attr):
                    setattr(bp, c_unlock_attr, True)
                setattr(bp, c_attr, c_new)
            return
        if state['kind'] == 'CABINET_DIM':
            cab_props = obj.face_frame_cabinet
            setattr(cab_props, state['dim'], new_value)
            if state.get('translate') and self._drag_basis is not None:
                # delta along the drag axis = (new - orig) / grow_sign
                grow_sign = state['grow_sign']
                if abs(grow_sign) < 1e-9:
                    return
                delta_axis = (new_value - state['value']) / grow_sign
                origin_w, x_axis_w, z_axis_w, _n = self._drag_basis
                axis_w = x_axis_w if state['translate_axis'] == 'X' \
                    else z_axis_w
                world_delta = axis_w * delta_axis
                new_world_loc = state['orig_world_loc'] + world_delta
                if obj.parent is not None:
                    parent_inv = obj.parent.matrix_world.inverted_safe()
                    obj.location = parent_inv @ new_world_loc
                else:
                    obj.location = new_world_loc
            return
        if state['kind'] == 'CABINET_WIDTH':
            cp = obj.face_frame_cabinet
            unlock_attr = state['unlock_attr']
            if write_unlock and not getattr(cp, unlock_attr):
                setattr(cp, unlock_attr, True)
            setattr(cp, state['attr'], new_value)
            return
        # Tree child
        pg = (obj.face_frame_opening
              if obj.get(types_face_frame.TAG_OPENING_CAGE)
              else obj.face_frame_split)
        if write_unlock and not pg.unlock_size:
            pg.unlock_size = True
        pg.size = new_value

    @staticmethod
    def _restore_neighbor(state):
        """Restore one snapshot record to its pre-drag value."""
        obj = bpy.data.objects.get(state['name'])
        if obj is None:
            return
        if state['kind'] == 'BAY':
            bp = obj.face_frame_bay
            unlock_attr = state['unlock_attr']
            setattr(bp, unlock_attr, state['unlock'])
            setattr(bp, state['attr'], state['value'])
            if 'compensate_attr' in state:
                setattr(bp, state['compensate_unlock_attr'],
                        state['compensate_unlock'])
                setattr(bp, state['compensate_attr'],
                        state['compensate_value'])
            return
        if state['kind'] == 'CABINET_DIM':
            setattr(obj.face_frame_cabinet, state['dim'], state['value'])
            if state.get('translate') and 'orig_location' in state:
                obj.location = state['orig_location']
            return
        if state['kind'] == 'CABINET_WIDTH':
            cp = obj.face_frame_cabinet
            setattr(cp, state['unlock_attr'], state['unlock'])
            setattr(cp, state['attr'], state['value'])
            return
        if state['kind'] == 'GROUP_DISTRIBUTE':
            # Restore every row's member widths and locations, then the
            # group's translation and the cage's Dim X.
            orig_totals = []
            for row in state['rows']:
                for name, w, loc in zip(row['member_names'],
                                        row['orig_widths'],
                                        row['orig_locations']):
                    m = bpy.data.objects.get(name)
                    if m is None:
                        continue
                    _member_set_width(m, w)
                    m.location = loc.copy()
                orig_totals.append(sum(row['orig_widths']))
            group = obj  # obj was looked up from state['name'] above
            if state.get('translate'):
                group.location = state['orig_group_location'].copy()
            try:
                hb_types.GeoNodeObject(group).set_input(
                    'Dim X', max(orig_totals) if orig_totals else 0.0)
            except Exception:
                pass
            return
        pg = (obj.face_frame_opening
              if obj.get(types_face_frame.TAG_OPENING_CAGE)
              else obj.face_frame_split)
        pg.unlock_size = state['unlock']
        pg.size = state['value']

    # ---- Drag lifecycle ----

    def _drag_axis_value(self, b, ff_x, ff_z):
        """Project the FF-local point onto the boundary's drag axis."""
        return ff_x if b['axis'] == 'X' else ff_z

    def _boundary_axis_value(self, b):
        """Current value of the boundary along its drag axis."""
        return b['ff_x'] if b['axis'] == 'X' else b['ff_z']

    def _apply_group_distribute(self, state, width_delta):
        """Distribute a total-group-width delta across each row's
        unlocked members, reposition every member spatially left-to-
        right in group-local X, and (for LEFT-edge drags) translate
        the group so its world-space right edge stays put.

        Each row (front cabinets, back cabinets) distributes the SAME
        width_delta independently. Within a row, unlocked face-frame
        cabinets absorb proportionally to their original width;
        appliances and lock_width=True cabinets hold their width but
        still get repositioned so they remain abutting their neighbors.

        Row geometry depends on rotation: front-row cabinets have
        location.x at their spatial-left edge in group-local, back-row
        cabinets have location.x at their spatial-right edge
        (rotated 180 around Z, so cab-local origin maps to the right
        end in group-local). leading_offset captures that.
        """
        max_new_total = 0.0
        for row in state['rows']:
            orig_widths = row['orig_widths']
            orig_locks = row['orig_locks']
            unlocked = [i for i, lk in enumerate(orig_locks) if not lk]

            if unlocked:
                weights = [orig_widths[i] for i in unlocked]
                total_weight = sum(weights)
                row_delta = width_delta
                if total_weight > 1e-9:
                    # Clamp so no unlocked drops below MIN_BAY_WIDTH.
                    floor = None
                    for i, w in zip(unlocked, weights):
                        if w > 1e-9:
                            f = ((MIN_BAY_WIDTH - orig_widths[i])
                                 * total_weight / w)
                            floor = f if floor is None else max(floor, f)
                    if floor is not None and row_delta < floor:
                        row_delta = floor
                    new_widths = list(orig_widths)
                    for i, w in zip(unlocked, weights):
                        share = (w / total_weight) * row_delta
                        new_widths[i] = orig_widths[i] + share
                else:
                    new_widths = list(orig_widths)
            else:
                # All locked: row width is fixed. Members still need
                # repositioning if their relative order shifts, but in
                # practice their absolute positions don't move.
                new_widths = list(orig_widths)

            is_back_row = row['is_back_row']
            running_gx = row['start_gx']
            for i, name in enumerate(row['member_names']):
                m = bpy.data.objects.get(name)
                if m is None:
                    continue
                if new_widths[i] != orig_widths[i]:
                    _member_set_width(m, new_widths[i])
                leading_offset = new_widths[i] if is_back_row else 0.0
                new_loc = row['orig_locations'][i].copy()
                new_loc.x = running_gx + leading_offset
                m.location = new_loc
                running_gx += new_widths[i]
            max_new_total = max(max_new_total, running_gx - row['start_gx'])

        group = bpy.data.objects.get(state['name'])
        if group is None:
            return

        if state.get('translate') and self._drag_basis is not None:
            # World-space right edge stays put; group shifts along its
            # frozen +X axis by the shrinkage amount (max across rows).
            # Use the front row's shrinkage by default - typical islands
            # have aligned front+back so row deltas match.
            orig_total = max(
                (sum(r['orig_widths']) for r in state['rows']),
                default=0.0,
            )
            shift = orig_total - max_new_total
            origin_w, x_axis_w, _z, _n = self._drag_basis
            new_world_loc = state['orig_group_world_loc'] + x_axis_w * shift
            if group.parent is not None:
                parent_inv = group.parent.matrix_world.inverted_safe()
                group.location = parent_inv @ new_world_loc
            else:
                group.location = new_world_loc

        # Sync cage Dim X to the widest row's total. For aligned
        # islands all rows match; for misaligned the cage tracks the
        # outermost extent.
        try:
            hb_types.GeoNodeObject(group).set_input('Dim X', max_new_total)
        except Exception:
            pass


    def _start_drag(self, context, event, b, layout):
        region = context.region
        rv3d = context.region_data
        hit = solver.mouse_to_ff_local(
            b['cabinet_obj'], layout, region, rv3d,
            (event.mouse_region_x, event.mouse_region_y))
        if hit is None:
            return False
        ff_x, ff_z, _w = hit
        self._drag_boundary = b
        self._drag_layout = layout
        self._drag_origin_ff = self._drag_axis_value(b, ff_x, ff_z)
        self._drag_origin_boundary = self._boundary_axis_value(b)
        # Freeze the FF basis for the duration of the drag. For drags
        # that translate the cabinet (OUTER_LEFT) this keeps cursor
        # projection in a stable reference frame; otherwise the
        # cabinet would move underneath the cursor and cursor_delta
        # would compound.
        self._drag_basis = solver.face_frame_world_basis(
            b['cabinet_obj'], layout)
        self._drag_active = True
        self._drag_snapshot = self._snapshot_neighbors(b)
        return True

    def _apply_drag(self, context, event):
        if not self._drag_active:
            return
        region = context.region
        rv3d = context.region_data
        b = self._drag_boundary
        layout = self._drag_layout
        cab = b['cabinet_obj']
        # Use the frozen drag basis. mouse_to_ff_local would re-derive
        # the basis from the cabinet's current matrix_world, which is
        # mid-update for translate-style drags.
        hit = solver.mouse_to_ff_local_with_basis(
            region, rv3d,
            (event.mouse_region_x, event.mouse_region_y),
            self._drag_basis)
        if hit is None:
            return
        ff_x_now, ff_z_now, _w = hit
        cursor_axis_now = self._drag_axis_value(b, ff_x_now, ff_z_now)
        cursor_delta = cursor_axis_now - self._drag_origin_ff
        # Anchor proposed position on the boundary's drag-start value,
        # not its live value. Reading the live value compounds movement
        # across mousemoves: each pass would add cursor_delta on top of
        # the previously applied delta, producing visible jitter when
        # snap is engaged.
        proposed_axis = self._drag_origin_boundary + cursor_delta
        # Numeric override (typed): treat the typed value as the absolute
        # new size of the primary neighbor. Convert to a proposed axis
        # value via the sign convention used below.
        if self._typing and self._typed:
            try:
                primary_orig = (self._drag_snapshot[0]['value']
                                if self._drag_snapshot else 0.0)
                sign = b.get('primary_sign', 1.0)
                typed_size = self._parse_typed(self._typed)
                # Positive primary-growth delta = sign * (new - orig)
                # along the drag axis, so:
                proposed_axis = (self._drag_origin_boundary
                                 + sign * (typed_size - primary_orig))
            except ValueError:
                return
        snap_mode = 'OFF' if (self._snap_disabled_temp or self._typing) \
            else self._snap_mode
        snapped_axis, snap_kind = _snap_offset(
            proposed_axis, region, rv3d, b, layout,
            self._boundaries, snap_mode)
        delta = snapped_axis - self._drag_origin_boundary
        self._snap_kind = snap_kind

        # Group outer-edge drags use N-way distribution across member
        # cabinets, gated by face_frame_cabinet.lock_width. State on
        # the snapshot is a single GROUP_DISTRIBUTE record carrying
        # original widths and locations, so the math is anchored on
        # drag-start values and stays drift-free across refreshes.
        if b['kind'] in ('GROUP_OUTER_RIGHT', 'GROUP_OUTER_LEFT'):
            if not self._drag_snapshot:
                return
            state = self._drag_snapshot[0]
            primary_sign = b.get('primary_sign', 1.0)
            # width_delta = total change to group width. RIGHT: +cursor
            # delta = +growth. LEFT: +cursor delta = -growth (right edge
            # stays put, left moves in).
            self._apply_group_distribute(state, primary_sign * delta)
            self._boundaries = self._collect()
            for nb, nl in self._boundaries:
                if (nb['cabinet_obj'] is b['cabinet_obj']
                        and nb['kind'] == b['kind']):
                    self._drag_boundary = nb
                    self._drag_layout = nl
                    break
            return

        # Apply with clamp. Sign convention: positive delta along the
        # drag axis grows the PRIMARY neighbor and shrinks the SECONDARY.
        # For MID_RAIL the primary is the TOP child and the drag axis
        # is +ff_z. Moving the boundary up (positive delta) should
        # SHRINK the top child, not grow it. Flip primary growth sign
        # for MID_RAIL so the math stays consistent.
        primary_sign = b.get('primary_sign', 1.0)
        if not self._drag_snapshot:
            return
        state0 = self._drag_snapshot[0]
        primary_orig = state0['value']
        single_neighbor = (len(self._drag_snapshot) == 1)
        # Default minimum if the boundary record didn't supply its own.
        if b['kind'] in ('BAY_EDGE', 'OUTER_RIGHT', 'OUTER_LEFT',
                         'OUTER_TOP', 'OUTER_BOTTOM', 'BAY_HANDLE',
                         'CABINET_BOUNDARY'):
            default_min = MIN_BAY_WIDTH
        elif b['kind'] == 'TOE_KICK':
            default_min = 0.0
        else:
            default_min = MIN_OPENING_SIZE
        primary_min = state0.get('min_value')
        if primary_min is None:
            primary_min = default_min

        if single_neighbor:
            # Possibly-compound clamp: enforce primary_min, and (if
            # present) the compensate attr's own min, by clamping
            # delta to the most restrictive feasible range.
            has_compensate = ('compensate_attr' in state0)
            # primary_sign * delta >= primary_min - primary_orig
            if primary_sign > 0:
                lower = (primary_min - primary_orig) / primary_sign
                if delta < lower:
                    delta = lower
            elif primary_sign < 0:
                upper = (primary_min - primary_orig) / primary_sign
                if delta > upper:
                    delta = upper
            if has_compensate:
                c_orig = state0['compensate_value']
                c_sign = state0['compensate_sign']
                c_min = state0['compensate_min_value']
                if c_sign > 0:
                    lower = (c_min - c_orig) / c_sign
                    if delta < lower:
                        delta = lower
                elif c_sign < 0:
                    upper = (c_min - c_orig) / c_sign
                    if delta > upper:
                        delta = upper
            new_primary = primary_orig + primary_sign * delta
            new_secondary = None
        else:
            # Paired-neighbor (BAY_EDGE, MID_STILE, MID_RAIL).
            secondary_orig = self._drag_snapshot[1]['value']
            sec_min = self._drag_snapshot[1].get('min_value')
            if sec_min is None:
                sec_min = default_min
            new_primary = primary_orig + primary_sign * delta
            new_secondary = secondary_orig - primary_sign * delta
            if new_primary < primary_min:
                shortfall = primary_min - new_primary
                new_primary = primary_min
                new_secondary -= shortfall
            if new_secondary < sec_min:
                shortfall = sec_min - new_secondary
                new_secondary = sec_min
                new_primary -= shortfall
                if new_primary < primary_min:
                    new_primary = primary_min
        # Write. write_unlock = True so each affected child auto-locks
        # (no-op for CABINET_DIM kind).
        self._write_neighbor(state0, new_primary, True, delta=delta)
        if not single_neighbor:
            self._write_neighbor(
                self._drag_snapshot[1], new_secondary, True)
        # Refresh boundaries — splitter centerlines shift as sizes
        # change. Re-link the drag boundary to the freshly collected
        # record matching the same edge / split / gap.
        self._boundaries = self._collect()
        for nb, nl in self._boundaries:
            if nb['cabinet_obj'] is not cab or nb['kind'] != b['kind']:
                continue
            same = False
            if b['kind'] == 'BAY_EDGE':
                same = nb.get('edge_index') == b.get('edge_index')
            elif b['kind'] == 'CABINET_BOUNDARY':
                same = nb.get('edge_index') == b.get('edge_index')
            elif b['kind'] in ('OUTER_RIGHT', 'OUTER_LEFT',
                               'OUTER_TOP', 'OUTER_BOTTOM',
                               'TOE_KICK'):
                # One of each kind per cabinet (matching kind + cabinet
                # already checked above is sufficient).
                same = True
            elif b['kind'] == 'BAY_HANDLE':
                same = (
                    nb.get('bay_obj_name') == b.get('bay_obj_name')
                    and nb.get('attr') == b.get('attr')
                )
            else:
                same = (
                    nb.get('split_node_name') == b.get('split_node_name')
                    and nb.get('splitter_index') == b.get('splitter_index')
                )
            if same:
                self._drag_boundary = nb
                self._drag_layout = nl
                break

    def _end_drag(self, commit):
        if not self._drag_active:
            return
        if not commit:
            for state in (self._drag_snapshot or []):
                self._restore_neighbor(state)
            self._boundaries = self._collect()
        self._drag_active = False
        self._drag_boundary = None
        self._drag_layout = None
        self._drag_snapshot = None
        self._drag_basis = None
        self._snap_kind = None
        self._typing = False
        self._typed = ''

    @staticmethod
    def _parse_typed(s):
        """Parse a numeric string in inches: '12', '12.5', '12 1/2',
        '12-1/2'. Returns meters."""
        s = s.strip().replace('-', ' ')
        if not s:
            raise ValueError("empty")
        parts = s.split()
        total = 0.0
        for part in parts:
            if '/' in part:
                num, den = part.split('/')
                total += float(num) / float(den)
            else:
                total += float(part)
        return inch(total)

    # ---- Modal event router ----

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self._snap_disabled_temp = event.shift
            if self._drag_active:
                self._apply_drag(context, event)
            else:
                pick = self._pick_boundary(context, event)
                self._hover_boundary = pick[0] if pick else None
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Lock-icon click takes priority over boundary picking. The
            # icons are tiny so we use a generous square tolerance.
            if self._handle_lock_click(context, event):
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            pick = self._pick_boundary(context, event)
            if pick is not None:
                b, layout = pick
                self._start_drag(context, event, b, layout)
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self._drag_active:
                self._end_drag(commit=True)
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'TAB' and event.value == 'PRESS':
            self._snap_mode = {
                'OFF': 'COARSE',
                'COARSE': 'FINE',
                'FINE': 'OFF',
            }[self._snap_mode]
            self.report({'INFO'}, f"Snap: {self._snap_mode}")
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Numeric input during a drag
        if self._drag_active and event.value == 'PRESS':
            if event.type in ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR',
                              'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'):
                digit = event.type[-1] if event.type[-1].isdigit() \
                    else {'ZERO': '0', 'ONE': '1', 'TWO': '2',
                          'THREE': '3', 'FOUR': '4', 'FIVE': '5',
                          'SIX': '6', 'SEVEN': '7', 'EIGHT': '8',
                          'NINE': '9'}[event.type]
                self._typed += digit
                self._typing = True
                self._apply_drag(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type == 'PERIOD':
                self._typed += '.'
                self._typing = True
                return {'RUNNING_MODAL'}
            if event.type == 'SLASH':
                self._typed += '/'
                self._typing = True
                return {'RUNNING_MODAL'}
            if event.type == 'SPACE':
                self._typed += ' '
                self._typing = True
                return {'RUNNING_MODAL'}
            if event.type == 'BACK_SPACE':
                self._typed = self._typed[:-1]
                if not self._typed:
                    self._typing = False
                self._apply_drag(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

        if event.type in ('RET', 'NUMPAD_ENTER') and event.value == 'PRESS':
            if self._drag_active:
                self._end_drag(commit=True)
            self._cleanup(context)
            return {'FINISHED'}

        if event.type in ('ESC', 'RIGHTMOUSE') and event.value == 'PRESS':
            if self._drag_active:
                # Cancel just this drag, stay in session
                self._end_drag(commit=False)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            # Otherwise cancel session: roll back everything
            _restore_session(self._session_snapshot)
            self._cleanup(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
class hb_face_frame_OT_grab_face_frame(_GrabBaseMixin, bpy.types.Operator):
    """Modal: grab face frame internals — bay edges, mid stiles, and
    mid rails — to resize bays and openings."""
    bl_idname = "hb_face_frame.grab_face_frame"
    bl_label = "Grab Face Frame"
    bl_description = (
        "Click and drag face-frame boundaries (bay edges, mid stiles, "
        "mid rails) to resize bays and openings. Click a lock icon to "
        "unlock. Enter to confirm, Esc to cancel"
    )
    bl_options = {'REGISTER', 'UNDO'}
    BOUNDARY_COLLECTOR = staticmethod(solver.editable_boundaries_v1)


class hb_face_frame_OT_grab_cabinet(_GrabBaseMixin, bpy.types.Operator):
    """Modal: grab cabinet-level dims — outer right edge (width), outer
    top edge (height), and bay edges."""
    bl_idname = "hb_face_frame.grab_cabinet"
    bl_label = "Grab Cabinet"
    bl_description = (
        "Click and drag the cabinet's outer edges to resize overall "
        "width / height, or drag bay edges to redistribute width "
        "between bays. Enter to confirm, Esc to cancel"
    )
    bl_options = {'REGISTER', 'UNDO'}
    BOUNDARY_COLLECTOR = staticmethod(solver.editable_boundaries_cabinet)


class hb_face_frame_OT_grab_cabinet_group(_GrabBaseMixin, bpy.types.Operator):
    """Modal: grab boundaries between member cabinets in a cabinet
    group. Drag a boundary to shift width between the two adjacent
    cabinets. Same modal mechanics as Grab Cabinet (snap, type-to-set,
    Esc to cancel, click-to-unlock) — scope is just the active group
    instead of the whole scene.

    Phase A: only inter-cabinet boundaries (CABINET_BOUNDARY). Group
    outer-edge drags with lock_width-aware distribution land in a
    follow-up.
    """
    bl_idname = "hb_face_frame.grab_cabinet_group"
    bl_label = "Grab Cabinet Group"
    bl_description = (
        "Click and drag boundaries between cabinets in the group to "
        "shift width between them. Locked cabinets hold their width. "
        "Enter to confirm, Esc to cancel"
    )
    bl_options = {'REGISTER', 'UNDO'}
    # Group scope is resolved via _collect; BOUNDARY_COLLECTOR is
    # unused in this subclass but the mixin tolerates None.

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_CAGE_GROUP'))

    def invoke(self, context, event):
        # Capture the active group up front so _collect doesn't depend
        # on the active object staying selected across modal events.
        self._scope_group = context.active_object
        if (self._scope_group is None
                or not self._scope_group.get('IS_CAGE_GROUP')):
            self.report({'WARNING'}, "Active object isn't a cabinet group")
            return {'CANCELLED'}
        return super().invoke(context, event)

    def _collect(self):
        return _collect_group_boundaries(self._scope_group)


classes = (
    hb_face_frame_OT_grab_face_frame,
    hb_face_frame_OT_grab_cabinet,
    hb_face_frame_OT_grab_cabinet_group,
)
register, unregister = bpy.utils.register_classes_factory(classes)
