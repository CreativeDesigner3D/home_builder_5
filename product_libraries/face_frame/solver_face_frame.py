"""Layout solver for face frame cabinets.

Pure-Python; no drivers. The cabinet's recalculate() method builds a
FaceFrameLayout snapshot from PropertyGroups, asks this module for
segments and per-part geometry, then writes resolved values to the
existing part objects.

Coordinate convention (matches frameless and the carcass):
- Cabinet origin at back-left, floor level
- +X is right, -Y is forward (cabinet front at y = -dim_y)
- Face frame outside face flush with cabinet front (at y = -dim_y)
- Carcass front edge sits behind the face frame (at y = -dim_y + fft)

Multi-bay strategy (option B - lazy per-segment rails):
A "segment" is a run of consecutive bays whose top (or bottom) rail can
be a single physical part - same height, no extended mid stile breaking
the run, etc. The solver returns one segment record per physical rail
needed; the cabinet's recalculate() reconciles those segments against
existing rail objects, creating/destroying as needed. No hidden parts.

Mid stiles are always one-per-gap and never destroyed. Their length and Z
position adapt based on whether adjacent rails pass through the gap.
"""
from ...units import inch


# ---------------------------------------------------------------------------
# Layout snapshot
# ---------------------------------------------------------------------------
class FaceFrameLayout:
    """Snapshot of a cabinet's solved state.

    Reads cabinet props, walks bay child objects (sorted by hb_bay_index),
    reads the cabinet's mid_stile_widths collection. Used by every solver
    function so positions and lengths come from one consistent input.
    """

    def __init__(self, cabinet_obj):
        # Lazy import avoids any circular at module load
        from . import types_face_frame
        self._cabinet_tag = types_face_frame.TAG_BAY_CAGE

        cab = cabinet_obj.face_frame_cabinet
        self.cabinet_type = cab.cabinet_type

        # Cabinet dimensions
        self.dim_x = cab.width
        self.dim_y = cab.depth
        self.dim_z = cab.height

        # Material thicknesses
        self.mt = cab.material_thickness
        self.bt = cab.back_thickness
        self.fft = cab.face_frame_thickness

        # Toe kick (cabinet baseline; bay kick_height adds on top)
        self.has_toe_kick = self.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER')
        # Top construction style: bases and lap drawers use front + rear
        # stretchers; uppers and talls use a solid top panel.
        self.uses_stretchers = self.cabinet_type in ('BASE', 'LAP_DRAWER')
        self.tkh = cab.toe_kick_height if self.has_toe_kick else 0.0
        self.tks = cab.toe_kick_setback if self.has_toe_kick else 0.0
        self.tkt = cab.toe_kick_thickness if self.has_toe_kick else 0.0

        # End stile widths
        self.lsw = cab.left_stile_width
        self.rsw = cab.right_stile_width

        # Rail width defaults (used when populating a fresh bay)
        self.default_top_rail_width = cab.top_rail_width
        self.default_bottom_rail_width = cab.bottom_rail_width
        # Stretcher dimensions for stretcher-based top construction
        self.stretcher_w = getattr(cab, 'stretcher_width', None) or 0.0889
        self.stretcher_t = getattr(cab, 'stretcher_thickness', None) or 0.0127

        # Walk bay children
        bay_children = sorted(
            [c for c in cabinet_obj.children if c.get(self._cabinet_tag)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if bay_children:
            self.bay_count = len(bay_children)
            self.bays = [self._read_bay(c) for c in bay_children]
        else:
            # Fallback - cabinet hasn't built its bay objects yet (during
            # the initial create_carcass call before bays are added).
            self.bay_count = 1
            self.bays = [self._make_default_bay()]

        # Mid stile widths from the cabinet's collection (one per gap)
        ms_coll = cab.mid_stile_widths
        n_gaps = max(0, self.bay_count - 1)
        default_ms = inch(2.0)
        self.mid_stiles = []
        for i in range(n_gaps):
            if i < len(ms_coll):
                ms = ms_coll[i]
                self.mid_stiles.append({
                    'width': ms.width,
                    'extend_up_amount': ms.extend_up_amount,
                    'extend_down_amount': ms.extend_down_amount,
                })
            else:
                self.mid_stiles.append({
                    'width': default_ms,
                    'extend_up_amount': 0.0,
                    'extend_down_amount': 0.0,
                })

    def _read_bay(self, bay_obj):
        bp = bay_obj.face_frame_bay
        return {
            'width':              bp.width,
            'height':             bp.height,
            'depth':              bp.depth,
            'kick_height':        bp.kick_height,
            'top_offset':         bp.top_offset,
            'top_rail_width':     bp.top_rail_width,
            'bottom_rail_width':  bp.bottom_rail_width,
            'remove_bottom':      bp.remove_bottom,
            'delete_bay':         bp.delete_bay,
        }

    def _make_default_bay(self):
        return {
            'width':              self.dim_x - self.lsw - self.rsw,
            'height':             self.dim_z - self.tkh,
            'depth':              self.dim_y,
            'kick_height':        0.0,
            'top_offset':         0.0,
            'top_rail_width':     self.default_top_rail_width,
            'bottom_rail_width':  self.default_bottom_rail_width,
            'remove_bottom':      False,
            'delete_bay':         False,
        }


# ---------------------------------------------------------------------------
# Carcass dimensions
# ---------------------------------------------------------------------------
def carcass_inner_depth(layout):
    """Available depth from cabinet front to back, behind the face frame."""
    return layout.dim_y - layout.fft


# ---------------------------------------------------------------------------
# Bay X position (cumulative across stiles + previous bays)
# ---------------------------------------------------------------------------
def bay_x_position(layout, bay_index):
    """X coordinate of the left edge of bay N's opening."""
    x = layout.lsw
    for i in range(bay_index):
        x += layout.bays[i]['width']
        if i < len(layout.mid_stiles):
            x += layout.mid_stiles[i]['width']
    return x


# ---------------------------------------------------------------------------
# Per-bay vertical anchors - the key abstraction for base vs upper cabinets
# ---------------------------------------------------------------------------
# Bases anchor at the floor: bay_bottom_z is fixed by toe kick + bay kick,
# and a taller bay_height extends UPWARD past the cabinet ceiling.
# Uppers anchor at the cabinet top: bay_top_z is fixed by dim_z - top_offset,
# and a taller bay_height extends DOWNWARD past the cabinet floor.
#
# All Z positions for bottom rails, bay cages, mid stile bottoms, and the
# bottom-rail passthrough check go through these helpers. Top rails and the
# top-rail passthrough always anchor at dim_z - top_offset for now (matches
# both cabinet types in the common case).
def bay_bottom_z(layout, bay_index):
    """Z of the bay's bottom edge (top surface of the bay's bottom rail)."""
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'UPPER':
        return layout.dim_z - bay['top_offset'] - bay['height']
    return layout.tkh + bay['kick_height']


def bay_top_z(layout, bay_index):
    """Z of the bay's top edge (bottom surface of the bay's top rail)."""
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'UPPER':
        return layout.dim_z - bay['top_offset']
    return layout.tkh + bay['kick_height'] + bay['height']


# ---------------------------------------------------------------------------
# Pass-through predicates - "does the rail/something cross gap N?"
# ---------------------------------------------------------------------------
def _epsilon_eq(a, b, places=4):
    return round(a, places) == round(b, places)


def top_rail_passthrough(layout, gap_index):
    """True if a single top rail spans uninterrupted across gap_index.

    Break conditions:
    - extend_up_amount > 0 on the mid stile (it pokes through the rail)
    - bay top Z's differ (top_offset for uppers; kick/height for bases)
    - bay top rail widths differ
    """
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]
    if ms['extend_up_amount'] > 0:
        return False
    if not _epsilon_eq(bay_top_z(layout, gap_index),
                       bay_top_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_a['top_rail_width'], bay_b['top_rail_width']):
        return False
    return True


def bottom_rail_passthrough(layout, gap_index):
    """True if a single bottom rail spans uninterrupted across gap_index.

    Break conditions:
    - extend_down_amount > 0 on the mid stile
    - bay bottom Z's differ (caused by kick height differences for bases,
      or bay height differences for uppers)
    - bay bottom rail widths differ
    - the right-side bay has remove_bottom set
    """
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]
    if ms['extend_down_amount'] > 0:
        return False
    if not _epsilon_eq(bay_bottom_z(layout, gap_index),
                       bay_bottom_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_a['bottom_rail_width'], bay_b['bottom_rail_width']):
        return False
    if bay_b.get('remove_bottom', False):
        return False
    return True


# ---------------------------------------------------------------------------
# Segment computation
# ---------------------------------------------------------------------------
def _compute_segments(layout, passthrough_fn):
    """Generic segment builder. passthrough_fn(layout, gap_index) -> bool.

    Returns list of (start_bay, end_bay) tuples (inclusive on both ends).
    """
    n = layout.bay_count
    if n == 0:
        return []

    segments = []
    seg_start = 0
    for gap in range(n - 1):
        if not passthrough_fn(layout, gap):
            segments.append((seg_start, gap))
            seg_start = gap + 1
    segments.append((seg_start, n - 1))
    return segments


def top_rail_segments(layout):
    """Compute top rail segments. Each segment becomes one rail object.

    Returns list of dicts with keys: start_bay, end_bay, x, y, z,
    length, width, thickness.
    """
    segments = []
    for start, end in _compute_segments(layout, top_rail_passthrough):
        first_bay = layout.bays[start]
        x = bay_x_position(layout, start)
        # Length: sum of bay widths within segment + intermediate mid stile widths
        length = first_bay['width']
        for k in range(start, end):
            length += layout.mid_stiles[k]['width']
            length += layout.bays[k + 1]['width']
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          x,
            'y':          -layout.dim_y,
            'z':          bay_top_z(layout, start),
            'length':     length,
            'width':      first_bay['top_rail_width'],
            'thickness':  layout.fft,
        })
    return segments


def bottom_rail_segments(layout):
    """Compute bottom rail segments."""
    segments = []
    for start, end in _compute_segments(layout, bottom_rail_passthrough):
        first_bay = layout.bays[start]
        x = bay_x_position(layout, start)
        length = first_bay['width']
        for k in range(start, end):
            length += layout.mid_stiles[k]['width']
            length += layout.bays[k + 1]['width']
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          x,
            'y':          -layout.dim_y,
            'z':          bay_bottom_z(layout, start),
            'length':     length,
            'width':      first_bay['bottom_rail_width'],
            'thickness':  layout.fft,
        })
    return segments


# ---------------------------------------------------------------------------
# End stiles (left and right) - always exist
# ---------------------------------------------------------------------------
def left_end_stile_position(layout):
    """Left end stile follows bay 0's vertical extent. If bay 0 drops below
    the cabinet's nominal floor (taller upper bay) or rises above (different
    kick on a base), the stile origin moves with it so it covers the
    bay's full height face.
    """
    return (0.0, -layout.dim_y, bay_bottom_z(layout, 0))


def left_end_stile_dims(layout):
    bottom_z = bay_bottom_z(layout, 0)
    top_z = bay_top_z(layout, 0)
    return (top_z - bottom_z, layout.lsw, layout.fft)


def right_end_stile_position(layout):
    """Right end stile follows the LAST bay's vertical extent."""
    last = layout.bay_count - 1
    return (layout.dim_x, -layout.dim_y, bay_bottom_z(layout, last))


def right_end_stile_dims(layout):
    last = layout.bay_count - 1
    bottom_z = bay_bottom_z(layout, last)
    top_z = bay_top_z(layout, last)
    return (top_z - bottom_z, layout.rsw, layout.fft)


# ---------------------------------------------------------------------------
# Carcass side panels - extend with first/last bay's vertical range
# ---------------------------------------------------------------------------
def left_side_position(layout):
    """Left carcass side matches bay 0's vertical range exactly. Shorter
    bay 0 -> shorter side; taller bay 0 -> longer side.
    """
    return (0.0, 0.0, bay_bottom_z(layout, 0))


def left_side_dims(layout):
    bottom_z = bay_bottom_z(layout, 0)
    top_z = bay_top_z(layout, 0)
    return (top_z - bottom_z, carcass_inner_depth(layout), layout.mt)


def right_side_position(layout):
    last = layout.bay_count - 1
    return (layout.dim_x, 0.0, bay_bottom_z(layout, last))


def right_side_dims(layout):
    last = layout.bay_count - 1
    bottom_z = bay_bottom_z(layout, last)
    top_z = bay_top_z(layout, last)
    return (top_z - bottom_z, carcass_inner_depth(layout), layout.mt)


# ---------------------------------------------------------------------------
# Mid stile (one per gap) - position and length depend on adjacent rails
# ---------------------------------------------------------------------------
def mid_stile_position(layout, gap_index):
    """X, Y, Z position for the mid stile at gap_index (between bay
    gap_index and bay gap_index + 1).

    Z = lower of the two adjacent bay bottoms (so the stile reaches down
    to the deeper bay), plus the bottom rail width if a rail passes
    through this gap, minus the mid stile's extend_down_amount.
    """
    if gap_index >= len(layout.mid_stiles):
        return (0.0, 0.0, 0.0)

    bay_a = layout.bays[gap_index]
    ms = layout.mid_stiles[gap_index]

    base_z = min(bay_bottom_z(layout, gap_index),
                 bay_bottom_z(layout, gap_index + 1))
    if bottom_rail_passthrough(layout, gap_index):
        base_z += bay_a['bottom_rail_width']
    base_z -= ms['extend_down_amount']

    x = bay_x_position(layout, gap_index) + bay_a['width']
    y = -layout.dim_y
    return (x, y, base_z)


def mid_stile_dims(layout, gap_index):
    """Length, Width, Thickness for the mid stile at gap_index.

    Length runs from the mid stile's bottom Z up to the bottom edge of
    the top rail covering this gap (or cabinet ceiling if rails are split).
    extend_up_amount adds to the length.
    """
    if gap_index >= len(layout.mid_stiles):
        return (0.0, 0.0, layout.fft)

    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]

    # Bottom Z (matches mid_stile_position)
    bottom_z = min(bay_bottom_z(layout, gap_index),
                   bay_bottom_z(layout, gap_index + 1))
    if bottom_rail_passthrough(layout, gap_index):
        bottom_z += bay_a['bottom_rail_width']
    bottom_z -= ms['extend_down_amount']

    # Top Z: higher of the two adjacent bay tops, minus top rail width
    # if a rail passes through, plus extend_up_amount.
    top_z = max(bay_top_z(layout, gap_index),
                bay_top_z(layout, gap_index + 1))
    if top_rail_passthrough(layout, gap_index):
        top_z -= bay_a['top_rail_width']
    top_z += ms['extend_up_amount']

    length = top_z - bottom_z
    return (length, ms['width'], layout.fft)


# ---------------------------------------------------------------------------
# Per-segment carcass bottom panels - the bay floors
# ---------------------------------------------------------------------------
def _carcass_bottom_passthrough(layout, gap_index):
    """True if the bay-floor (carcass bottom) panel spans gap_index uninterrupted.

    Break conditions:
    - bay bottom Z's differ (different floor heights)
    - bay depths differ (each panel sized to its bay's depth)
    - bottom rail widths differ (panel Z computed from bay_bottom_z + brw)
    - either bay has remove_bottom set
    - either bay has delete_bay set
    """
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_bottom_z(layout, gap_index),
                       bay_bottom_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return False
    if not _epsilon_eq(bay_a['bottom_rail_width'], bay_b['bottom_rail_width']):
        return False
    if bay_a.get('remove_bottom') or bay_b.get('remove_bottom'):
        return False
    if bay_a.get('delete_bay') or bay_b.get('delete_bay'):
        return False
    return True


def _mid_division_x(layout, gap_index):
    """X position of the mid division panel at gap_index. Matches the
    placement logic in mid_division_position so bottoms/backs can align
    their edges to it.
    """
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]
    msw = ms['width']
    base_x = bay_x_position(layout, gap_index) + bay_a['width']
    if _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return base_x + msw / 2.0 - layout.mt / 2.0
    return base_x + msw / 2.0


def _carcass_meeting_x(layout, gap_index):
    """X coordinate where two adjacent carcass bottom (or back) segments
    meet at gap_index. The HIGHER bay's panel abuts the mid division at
    its near face; the LOWER bay's panel passes UNDER the mid division to
    its far face. Both meet at the same X - the higher bay's near face.
    """
    mid_div_x = _mid_division_x(layout, gap_index)
    if bay_bottom_z(layout, gap_index) > bay_bottom_z(layout, gap_index + 1):
        # Higher bay is on the LEFT - meet at mid div left face
        return mid_div_x
    else:
        # Higher bay is on the RIGHT (or same Z) - meet at mid div right face
        return mid_div_x + layout.mt


def _segment_x_bounds(layout, start, end):
    """Left and right X for a segment that should fill from cabinet inner
    side wall to cabinet inner side wall, meeting adjacent segments at
    the mid division on internal gaps.
    """
    if start == 0:
        left_x = layout.mt
    else:
        left_x = _carcass_meeting_x(layout, start - 1)
    if end == layout.bay_count - 1:
        right_x = layout.dim_x - layout.mt
    else:
        right_x = _carcass_meeting_x(layout, end)
    return left_x, right_x


def _stretcher_x_bounds(layout, start, end):
    """X bounds for stretchers (and any panel that meets adjacent
    segments SYMMETRICALLY at the mid division's inside faces, rather
    than asymmetrically like carcass bottoms which have a higher/lower
    bay relationship).

    For an internal boundary at gap_index:
      - segment on the LEFT  (right edge): meets at mid_div left face = mid_div_x
      - segment on the RIGHT (left edge):  meets at mid_div right face = mid_div_x + mt
    """
    if start == 0:
        left_x = layout.mt
    else:
        left_x = _mid_division_x(layout, start - 1) + layout.mt
    if end == layout.bay_count - 1:
        right_x = layout.dim_x - layout.mt
    else:
        right_x = _mid_division_x(layout, end)
    return left_x, right_x


def carcass_bottom_segments(layout):
    """Per-segment bay floor panels.

    Length spans from carcass inner side (or previous mid division) to
    next mid division (or carcass inner side). The HIGHER neighbor's
    panel abuts the mid division; the LOWER neighbor passes underneath
    so the mid division can rest on top of it.
    """
    segments = []
    for start, end in _compute_segments(layout, _carcass_bottom_passthrough):
        first_bay = layout.bays[start]
        left_x, right_x = _segment_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.dim_y + first_bay['depth'] - layout.bt,
            'z':          bay_bottom_z(layout, start) + first_bay['bottom_rail_width'] - layout.mt,
            'length':     right_x - left_x,
            'panel_dim_y': first_bay['depth'] - layout.bt - layout.fft,
            'thickness':  layout.mt,
        })
    return segments


def _carcass_back_passthrough(layout, gap_index):
    """Back panel breaks when bay floors, ceilings, or depths differ."""
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_bottom_z(layout, gap_index),
                       bay_bottom_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_top_z(layout, gap_index),
                       bay_top_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return False
    if not _epsilon_eq(bay_a['bottom_rail_width'], bay_b['bottom_rail_width']):
        return False
    if bay_a.get('delete_bay') or bay_b.get('delete_bay'):
        return False
    return True


def carcass_back_segments(layout):
    """Per-segment back panels.

    Same X span as the bottom segments (from mid division to mid division
    or carcass side). Z origin matches the bay's floor (top of bottom
    panel); vertical extent reaches up to the cabinet ceiling.
    """
    segments = []
    for start, end in _compute_segments(layout, _carcass_back_passthrough):
        first_bay = layout.bays[start]
        left_x, right_x = _segment_x_bounds(layout, start, end)
        z_origin = bay_bottom_z(layout, start) + first_bay['bottom_rail_width'] - layout.mt
        segments.append({
            'start_bay':       start,
            'end_bay':         end,
            'x':               left_x,
            'y':               0.0,
            'z':               z_origin,
            'horizontal_length': right_x - left_x,
            'vertical_length':   bay_top_z(layout, start) - z_origin,
            'thickness':       layout.bt,
        })
    return segments


def _top_stretcher_passthrough(layout, gap_index):
    """True if a top stretcher spans uninterrupted across gap_index.

    Stretchers (front and rear) are placed per-bay at each bay's top
    edge. They merge across adjacent bays only when nothing about the
    geometry differs between the two bays.

    Break conditions:
    - bay top Z's differ (top_offset for uppers; kick + height for bases)
    - bay depths differ (front stretcher Y position depends on depth)
    - either bay has delete_bay set
    """
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_top_z(layout, gap_index),
                       bay_top_z(layout, gap_index + 1)):
        return False
    if not _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return False
    if bay_a.get('delete_bay') or bay_b.get('delete_bay'):
        return False
    return True


def carcass_top_segments(layout):
    """Per-segment SOLID carcass top panels for Upper / Tall cabinets.

    Bases and lap drawers use front + rear stretchers instead — see
    front_stretcher_segments / rear_stretcher_segments. This function
    produces a closed top panel sitting between the carcass sides /
    mid divisions, dropping with each bay's bay_top_z.

    Geometry:
      - origin x: segment left_x (symmetric meeting at mid div inside faces)
      - origin y: -mt  (just inside the face frame face)
      - origin z: bay_top_z(start)
      - Length:  segment X span
      - Width:   bay.depth - bt - fft - mt   (front to back interior)
      - Thickness: mt   (Mirror Z = True so panel extends down by mt)
    """
    segments = []
    for start, end in _compute_segments(layout, _top_stretcher_passthrough):
        first_bay = layout.bays[start]
        left_x, right_x = _stretcher_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.mt,
            'z':          bay_top_z(layout, start),
            'length':     right_x - left_x,
            'panel_dim_y': first_bay['depth'] - layout.bt - layout.fft - layout.mt,
            'thickness':  layout.mt,
        })
    return segments


def front_stretcher_segments(layout):
    """Per-segment front-of-cabinet top stretchers.

    Sits just behind the face frame at each bay's top edge. Replaces
    the older solid carcass top with stretcher-based face frame
    construction (no closed top panel, just front + rear stretchers).

    Geometry:
      - rotation: none (Cutpart with default axes)
      - origin x: segment left_x (= mt for the leftmost bay segment)
      - origin y: -dim_y + fft  (just behind the face frame)
      - origin z: bay_top_z(start)
      - Length:  segment X span (right_x - left_x)
      - Width:   stretcher depth (Y axis, extends in +Y; Mirror Y = False)
      - Thickness: stretcher thickness (Z axis, extends in -Z; Mirror Z = True)
    """
    segments = []
    for start, end in _compute_segments(layout, _top_stretcher_passthrough):
        left_x, right_x = _stretcher_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.dim_y + layout.fft,
            'z':          bay_top_z(layout, start),
            'length':     right_x - left_x,
            'width':      layout.stretcher_w,
            'thickness':  layout.stretcher_t,
        })
    return segments


def rear_stretcher_segments(layout):
    """Per-segment back-of-cabinet top stretchers.

    Sits just inside the carcass back panel, mirrored from the front
    stretcher. Same X bounds and Z origin as the front; differs only
    in Y position and Mirror Y direction.

    Geometry:
      - rotation: none
      - origin x: segment left_x
      - origin y: -bt  (just inside back panel)
      - origin z: bay_top_z(start)
      - Length:  segment X span
      - Width:   stretcher depth (Mirror Y = True so it extends in -Y)
      - Thickness: stretcher thickness (Mirror Z = True)
    """
    segments = []
    for start, end in _compute_segments(layout, _top_stretcher_passthrough):
        left_x, right_x = _stretcher_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.bt,
            'z':          bay_top_z(layout, start),
            'length':     right_x - left_x,
            'width':      layout.stretcher_w,
            'thickness':  layout.stretcher_t,
        })
    return segments


# ---------------------------------------------------------------------------
# Mid division - the carcass partition behind each mid stile
# ---------------------------------------------------------------------------
def mid_division_position(layout, gap_index):
    """X, Y, Z position for the partition behind mid stile N.

    Z = top of the LOWER bay's bottom rail, regardless of whether the
    rail breaks at this gap. The mid div sits on the lower bay's bottom
    rail and extends up behind the top rail to the cabinet top.
    """
    if gap_index >= len(layout.mid_stiles):
        return (0.0, 0.0, 0.0)
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]

    msw = ms['width']
    base_x = bay_x_position(layout, gap_index) + bay_a['width']
    if _epsilon_eq(bay_a['depth'], bay_b['depth']):
        x = base_x + msw / 2.0 - layout.mt / 2.0
    else:
        x = base_x + msw / 2.0

    use_depth = max(bay_a['depth'], bay_b['depth'])
    y = -layout.dim_y + use_depth - layout.bt

    # Z: top of LOWER bay's bottom rail
    if bay_bottom_z(layout, gap_index) <= bay_bottom_z(layout, gap_index + 1):
        lower_idx = gap_index
    else:
        lower_idx = gap_index + 1
    lower_brw = layout.bays[lower_idx]['bottom_rail_width']
    z = bay_bottom_z(layout, lower_idx) + lower_brw
    z -= ms['extend_down_amount']

    return (x, y, z)


def mid_division_dims(layout, gap_index):
    """Length (vertical), Width (depth into cabinet), Thickness.

    The mid div extends from the top of the lower bay's bottom rail up
    to the underside of the cabinet's carcass top (dim_z - mt). It runs
    BEHIND the top rail rather than stopping under it.
    """
    if gap_index >= len(layout.mid_stiles):
        return (0.0, 0.0, layout.mt)
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]

    # Bottom Z: top of LOWER bay's bottom rail (matches mid_division_position)
    if bay_bottom_z(layout, gap_index) <= bay_bottom_z(layout, gap_index + 1):
        lower_idx = gap_index
    else:
        lower_idx = gap_index + 1
    lower_brw = layout.bays[lower_idx]['bottom_rail_width']
    bottom_z = bay_bottom_z(layout, lower_idx) + lower_brw - ms['extend_down_amount']

    # Top Z: depends on top construction style.
    #   Stretchers (Base / Lap Drawer) - division extends fully to the
    #     taller neighbor's bay_top_z. Top edge flush with top rails and
    #     stretchers, providing structural attachment.
    #   Solid top  (Upper / Tall) - division stops mt below the taller
    #     neighbor's bay_top_z to butt against the underside of the
    #     carcass top panel.
    higher_top_z = max(bay_top_z(layout, gap_index),
                       bay_top_z(layout, gap_index + 1))
    if layout.uses_stretchers:
        top_z = higher_top_z + ms['extend_up_amount']
    else:
        top_z = higher_top_z - layout.mt + ms['extend_up_amount']

    length = top_z - bottom_z
    width = max(bay_a['depth'], bay_b['depth']) - layout.bt - layout.fft
    return (length, width, layout.mt)


# ---------------------------------------------------------------------------
# Bay cage (the opening behind the face frame)
# ---------------------------------------------------------------------------
def bay_cage_position(layout, bay_index):
    bay = layout.bays[bay_index]
    x = bay_x_position(layout, bay_index)
    y = -layout.dim_y + layout.fft
    z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']
    return (x, y, z)


def bay_cage_dims(layout, bay_index):
    """Dim X (width), Dim Y (depth back-to-front), Dim Z (height).

    Bay's depth field is independent: the cage Y dim is bay depth minus
    face frame thickness (since the cage starts behind the face frame).
    """
    bay = layout.bays[bay_index]
    cage_dim_x = bay['width']
    cage_dim_y = bay['depth'] - layout.fft
    cage_dim_z = (bay['height']
                  - bay['top_rail_width']
                  - bay['bottom_rail_width']
                  - bay['top_offset'])
    return (cage_dim_x, cage_dim_y, cage_dim_z)
