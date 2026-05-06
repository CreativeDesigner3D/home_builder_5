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
def _iter_face_frame_cabinets(scene):
    for obj in scene.objects:
        if obj.get(types_face_frame.TAG_CABINET_CAGE):
            yield obj


def _snapshot_session(scene):
    """Capture per-bay widths and unlock flags for every face-frame cabinet
    in the scene. Used to roll back on Esc."""
    snap = {}
    for cab in _iter_face_frame_cabinets(scene):
        bays = sorted(
            [c for c in cab.children if c.get(types_face_frame.TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        snap[cab.name] = [
            {
                'bay_name': b.name,
                'width': b.face_frame_bay.width,
                'unlock_width': b.face_frame_bay.unlock_width,
            }
            for b in bays
        ]
    return snap


def _restore_session(snap):
    """Restore per-bay widths and unlock flags from a snapshot."""
    for cab_name, bay_states in snap.items():
        for state in bay_states:
            bay = bpy.data.objects.get(state['bay_name'])
            if bay is None:
                continue
            bp = bay.face_frame_bay
            # Write unlock_width first to prevent the width setter's
            # auto-lock from re-flipping during restore.
            bp.unlock_width = state['unlock_width']
            bp.width = state['width']


# ---------------------------------------------------------------------------
# Boundary collection
# ---------------------------------------------------------------------------
def _collect_boundaries(scene):
    """Walk every face-frame cabinet and gather BAY_EDGE boundary
    records, plus the per-cabinet layout cached for hit-testing and
    drawing. Returns list of (boundary, layout) tuples."""
    out = []
    for cab in _iter_face_frame_cabinets(scene):
        layout = solver.FaceFrameLayout(cab)
        for b in solver.editable_boundaries_v1(cab, layout):
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
    # 1. Alignment to any other boundary (regardless of its axis), as
    # long as projecting it lines up on the drag screen axis.
    if proj_self is not None:
        best = None
        best_dist = SNAP_PX
        for other_b, other_layout in all_boundaries:
            if other_b is b:
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
                    top_right = corners[2]
                    icon_anchor_x = top_right.x - 4
                    icon_anchor_y = top_right.y - 4
                    _draw_padlock(shader, icon_anchor_x, icon_anchor_y,
                                  LOCK_GLYPH, size=10.0)
                    # Anchor (x, y) is the top-right corner of the lock
                    # body; center sits 5px left and 3.5px down. Record
                    # for click-to-unlock hit-testing.
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
                top_right = corners[2]
                icon_anchor_x = top_right.x - 4
                icon_anchor_y = top_right.y - 4
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
        if b['kind'] == 'BAY_EDGE':
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
# Modal operator
# ---------------------------------------------------------------------------
class hb_face_frame_OT_modify_cabinet(bpy.types.Operator):
    """Modal: drag bay boundaries on face frame cabinets to resize bays.

    Slice 1 supports bay-edge edits. Mid-stile (intra-bay opening) and
    mid-rail edits land in subsequent slices."""

    bl_idname = "hb_face_frame.modify_cabinet"
    bl_label = "Modify Face Frame Cabinet"
    bl_description = (
        "Click and drag bay boundaries to resize bays. Auto-locks edited "
        "bays. Enter to confirm, Esc to cancel"
    )
    bl_options = {'REGISTER', 'UNDO'}

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
        self._boundaries = _collect_boundaries(context.scene)
        if not self._boundaries:
            self.report({'INFO'}, "No editable boundaries found")
            return {'CANCELLED'}
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "LMB: drag boundary  |  Tab: snap mode  |  Shift: no snap  "
            "|  Type: numeric  |  Enter: confirm  |  Esc: cancel"
        )
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
            context.workspace.status_text_set(None)
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
        self._boundaries = _collect_boundaries(context.scene)
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
        """Snapshot the two children affected by a drag, keyed by kind.
        For BAY_EDGE: bay objects (width + unlock_width).
        For MID_STILE / MID_RAIL: opening or split tree-children
        (size + unlock_size). Returned as a list of dicts in
        [primary, secondary] order so delta arithmetic is consistent
        (primary grows, secondary shrinks)."""
        if b['kind'] == 'BAY_EDGE':
            cab = b['cabinet_obj']
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
                        'value': bp.width,
                        'unlock': bp.unlock_width,
                    })
            return out
        # Mid stile / mid rail: tree children
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

    @staticmethod
    def _write_neighbor(state, new_value, write_unlock):
        """Apply a new value to one snapshot record. Auto-lock semantics
        differ by kind: bay widths auto-lock through the setter; tree
        children need an explicit unlock_size = True alongside the size
        write."""
        obj = bpy.data.objects.get(state['name'])
        if obj is None:
            return
        if state['kind'] == 'BAY':
            bp = obj.face_frame_bay
            if write_unlock and not bp.unlock_width:
                bp.unlock_width = True
            bp.width = new_value
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
            bp.unlock_width = state['unlock']
            bp.width = state['value']
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
        hit = solver.mouse_to_ff_local(
            cab, layout, region, rv3d,
            (event.mouse_region_x, event.mouse_region_y))
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
                sign = -1.0 if b['kind'] == 'MID_RAIL' else 1.0
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
        # Apply with clamp. Sign convention: positive delta along the
        # drag axis grows the PRIMARY neighbor and shrinks the SECONDARY.
        # For MID_RAIL the primary is the TOP child and the drag axis
        # is +ff_z. Moving the boundary up (positive delta) should
        # SHRINK the top child, not grow it. Flip primary growth sign
        # for MID_RAIL so the math stays consistent.
        primary_sign = -1.0 if b['kind'] == 'MID_RAIL' else 1.0
        if not self._drag_snapshot:
            return
        primary_orig = self._drag_snapshot[0]['value']
        secondary_orig = (self._drag_snapshot[1]['value']
                          if len(self._drag_snapshot) > 1
                          else primary_orig)
        new_primary = primary_orig + primary_sign * delta
        new_secondary = secondary_orig - primary_sign * delta
        min_size = (MIN_BAY_WIDTH if b['kind'] == 'BAY_EDGE'
                    else MIN_OPENING_SIZE)
        if new_primary < min_size:
            shortfall = min_size - new_primary
            new_primary = min_size
            new_secondary -= shortfall
        if new_secondary < min_size:
            shortfall = min_size - new_secondary
            new_secondary = min_size
            new_primary -= shortfall
            if new_primary < min_size:
                new_primary = min_size
        # Write. write_unlock = True so each affected child auto-locks.
        self._write_neighbor(self._drag_snapshot[0], new_primary, True)
        if len(self._drag_snapshot) > 1:
            self._write_neighbor(self._drag_snapshot[1], new_secondary, True)
        # Refresh boundaries — splitter centerlines shift as sizes
        # change. Re-link the drag boundary to the freshly collected
        # record matching the same edge / split / gap.
        self._boundaries = _collect_boundaries(context.scene)
        for nb, nl in self._boundaries:
            if nb['cabinet_obj'] is not cab or nb['kind'] != b['kind']:
                continue
            same = False
            if b['kind'] == 'BAY_EDGE':
                same = nb.get('edge_index') == b.get('edge_index')
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
            self._boundaries = _collect_boundaries(bpy.context.scene)
        self._drag_active = False
        self._drag_boundary = None
        self._drag_layout = None
        self._drag_snapshot = None
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
classes = (hb_face_frame_OT_modify_cabinet,)
register, unregister = bpy.utils.register_classes_factory(classes)
