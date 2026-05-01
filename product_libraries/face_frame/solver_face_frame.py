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
import math

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

        # Side scribe + finish end condition. The pair determines how
        # far the side panel sits inboard of the face frame outer face
        # via left_scribe_offset / right_scribe_offset.
        self.l_scribe = cab.left_scribe
        self.r_scribe = cab.right_scribe
        self.l_fin_end = cab.left_finished_end_condition
        self.r_fin_end = cab.right_finished_end_condition
        self.top_scribe = cab.top_scribe

        # Rail width defaults (used when populating a fresh bay)
        self.default_top_rail_width = cab.top_rail_width
        self.default_bottom_rail_width = cab.bottom_rail_width
        # Stretcher dimensions for stretcher-based top construction
        self.stretcher_w = getattr(cab, 'stretcher_width', None) or 0.0889
        self.stretcher_t = getattr(cab, 'stretcher_thickness', None) or 0.0127

        # Bay-level mid rail / mid stile widths (face frame members
        # created by H/V splits inside a bay). Cabinet-level defaults
        # used as starting values; per-member overrides come later.
        self.bay_mid_rail_width = cab.bay_mid_rail_width
        self.bay_mid_stile_width = cab.bay_mid_stile_width

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
            'tree':               self._read_tree_root(bay_obj),
        }

    def _read_tree_root(self, bay_obj):
        """Find the bay's root tree node (single direct opening or split
        child) and recursively snapshot it. Returns None if the bay has
        no tree yet (during initial creation, before _build_carcass_parts
        adds the first opening)."""
        from . import types_face_frame
        candidates = [
            c for c in bay_obj.children
            if c.get(types_face_frame.TAG_OPENING_CAGE)
            or c.get(types_face_frame.TAG_SPLIT_NODE)
        ]
        if not candidates:
            return None
        # Prefer a child explicitly tagged as the bay's root if there's
        # ever ambiguity. With the current model there's exactly one
        # tree-node child of a bay; we just take the first.
        return self._read_tree_node(candidates[0])

    def _read_tree_node(self, obj):
        """Recursively snapshot a tree node. Leaves carry opening props;
        internal nodes carry axis + a list of child snapshots (sorted
        by hb_split_child_index for stable ordering)."""
        from . import types_face_frame
        if obj.get(types_face_frame.TAG_SPLIT_NODE):
            sp = obj.face_frame_split
            children = sorted(
                [c for c in obj.children
                 if c.get(types_face_frame.TAG_OPENING_CAGE)
                 or c.get(types_face_frame.TAG_SPLIT_NODE)],
                key=lambda c: c.get('hb_split_child_index', 0),
            )
            return {
                'kind':            'split',
                'obj_name':        obj.name,
                'axis':            sp.axis,
                'size':            sp.size,
                'unlock_size':     sp.unlock_size,
                'splitter_width':  sp.splitter_width,
                'add_backing':     sp.add_backing,
                'children':        [self._read_tree_node(c) for c in children],
            }
        # Leaf opening
        op = obj.face_frame_opening
        return {
            'kind':         'leaf',
            'obj_name':     obj.name,
            'size':         op.size,
            'unlock_size':  op.unlock_size,
            'opening_index': op.opening_index,
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
            'tree':               None,
        }


# ---------------------------------------------------------------------------
# Carcass dimensions
# ---------------------------------------------------------------------------
def carcass_inner_depth(layout):
    """Available depth from cabinet front to back, behind the face frame."""
    return layout.dim_y - layout.fft


# ---------------------------------------------------------------------------
# Side X offset (scribe / finish end condition)
# ---------------------------------------------------------------------------
# Face frame outer face stays at X=0 (left) and X=dim_x (right). Side
# panels can sit inboard of the face frame outer face by left/right
# scribe offsets. The offset comes from finish end condition first, then
# the user's typed scribe:
#   - THREE_QUARTER: side IS the outer face -> offset = 0
#   - PANELED: reserve 3/4" outboard for an applied panel
#   - everything else: use the typed scribe value (default 0)
def left_scribe_offset(layout):
    if layout.l_fin_end == 'THREE_QUARTER':
        return 0.0
    if layout.l_fin_end == 'PANELED':
        return inch(0.75)
    return layout.l_scribe


def right_scribe_offset(layout):
    if layout.r_fin_end == 'THREE_QUARTER':
        return 0.0
    if layout.r_fin_end == 'PANELED':
        return inch(0.75)
    return layout.r_scribe


def carcass_inner_left_x(layout):
    """X of the left side panel's inner face - the left bound of the
    cabinet's interior cavity. Sides are mt thick; outer face sits at
    left_scribe_offset."""
    return left_scribe_offset(layout) + layout.mt


def carcass_inner_right_x(layout):
    """X of the right side panel's inner face."""
    return layout.dim_x - right_scribe_offset(layout) - layout.mt


# ---------------------------------------------------------------------------
# Top Z: carcass top vs side top
# ---------------------------------------------------------------------------
# bay_top_z is the bay opening top (= bottom of top rail = top of side
# in the no-scribe case). With top_scribe, the carcass top (top panel
# for Upper/Tall, stretchers for Base/LapDrawer) drops by top_scribe.
# Sides that aren't the visible finished face drop with it; THREE_QUARTER
# finished sides stay at bay_top_z to keep their visible face full-height.
# Face frame members (stiles, top rail) are unaffected.
def carcass_top_z(layout, bay_index):
    """Z of the carcass top's top face. Held down by top_scribe."""
    return bay_top_z(layout, bay_index) - layout.top_scribe


def left_side_top_z(layout):
    if layout.l_fin_end == 'THREE_QUARTER':
        return bay_top_z(layout, 0)
    return carcass_top_z(layout, 0)


def right_side_top_z(layout):
    last = layout.bay_count - 1
    if layout.r_fin_end == 'THREE_QUARTER':
        return bay_top_z(layout, last)
    return carcass_top_z(layout, last)


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
    bay 0 -> shorter side; taller bay 0 -> longer side. X reflects the
    scribe offset so the side can sit inboard of the stile.
    """
    return (left_scribe_offset(layout), 0.0, bay_bottom_z(layout, 0))


def left_side_dims(layout):
    bottom_z = bay_bottom_z(layout, 0)
    top_z = left_side_top_z(layout)
    return (top_z - bottom_z, carcass_inner_depth(layout), layout.mt)


def right_side_position(layout):
    last = layout.bay_count - 1
    return (layout.dim_x - right_scribe_offset(layout),
            0.0, bay_bottom_z(layout, last))


def right_side_dims(layout):
    last = layout.bay_count - 1
    bottom_z = bay_bottom_z(layout, last)
    top_z = right_side_top_z(layout)
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
        left_x = carcass_inner_left_x(layout)
    else:
        left_x = _carcass_meeting_x(layout, start - 1)
    if end == layout.bay_count - 1:
        right_x = carcass_inner_right_x(layout)
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
        left_x = carcass_inner_left_x(layout)
    else:
        left_x = _mid_division_x(layout, start - 1) + layout.mt
    if end == layout.bay_count - 1:
        right_x = carcass_inner_right_x(layout)
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
            'vertical_length':   carcass_top_z(layout, start) - z_origin,
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
    mid divisions, dropping with each bay's carcass_top_z.

    Geometry:
      - origin x: segment left_x (symmetric meeting at mid div inside faces)
      - origin y: -mt  (just inside the face frame face)
      - origin z: carcass_top_z(start)  (= bay_top_z - top_scribe)
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
            'z':          carcass_top_z(layout, start),
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
      - origin z: carcass_top_z(start)  (held down by top_scribe)
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
            'z':          carcass_top_z(layout, start),
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
      - origin z: carcass_top_z(start)  (held down by top_scribe)
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
            'z':          carcass_top_z(layout, start),
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
    higher_top_z = max(carcass_top_z(layout, gap_index),
                       carcass_top_z(layout, gap_index + 1))
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
def _cage_x_bounds(layout, bay_index):
    """Carcass interior X bounds for a single bay - left face to right
    face of the cavity between sides / mid divisions.

    Differs from _segment_x_bounds in the stepped-cabinet case: the
    cage always stops at the mid division's near face from this bay's
    perspective, regardless of which neighbor's bottom panel passes
    under or over the division.
    """
    if bay_index == 0:
        left_x = carcass_inner_left_x(layout)
    else:
        left_x = _mid_division_x(layout, bay_index - 1) + layout.mt
    if bay_index == layout.bay_count - 1:
        right_x = carcass_inner_right_x(layout)
    else:
        right_x = _mid_division_x(layout, bay_index)
    return left_x, right_x


def bay_cage_position(layout, bay_index):
    """Origin of the bay cage in cabinet-local space.

    Anchored at the back-left-bottom corner of the carcass column for
    this bay: top of the bottom panel (= top of the bottom rail), back
    face of the face frame, and the inner face of either the left side
    panel (for bay 0) or the mid division to its left.
    """
    bay = layout.bays[bay_index]
    left_x, _ = _cage_x_bounds(layout, bay_index)
    y = -layout.dim_y + layout.fft
    z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']
    return (left_x, y, z)


def bay_cage_dims(layout, bay_index):
    """Dim X (width), Dim Y (depth back-to-front), Dim Z (height).

    Cage spans the full carcass column behind the face frame for this
    bay - it represents the interior cavity, not the door/drawer
    opening. Interior parts (shelves, dividers) span the full cage
    width; door/drawer fronts overlay the face frame opening and
    extend outward into the cage's margin between opening and side /
    mid division.

    - X: between cabinet sides / adjacent mid divisions (carcass
      interior, wider than the face frame opening by lsw/rsw - mt on
      end bays and msw/2 - mt/2 on shared mid div bays)
    - Y: from the back face of the face frame to the front face of the
      back panel (bay depth minus fft minus bt)
    - Z: top of the bay's bottom panel up to the underside of the
      cabinet top - stretcher underside for BASE / LAP_DRAWER, solid
      top underside for UPPER / TALL.
    """
    bay = layout.bays[bay_index]
    left_x, right_x = _cage_x_bounds(layout, bay_index)
    cage_dim_x = right_x - left_x
    cage_dim_y = bay['depth'] - layout.fft - layout.bt
    top_thickness = layout.stretcher_t if layout.uses_stretchers else layout.mt
    cage_top_z = carcass_top_z(layout, bay_index) - top_thickness
    cage_bottom_z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']
    cage_dim_z = cage_top_z - cage_bottom_z
    return (cage_dim_x, cage_dim_y, cage_dim_z)


# ---------------------------------------------------------------------------
# Opening cage (the face frame opening; child of a bay cage)
# ---------------------------------------------------------------------------
# Each bay starts with a single opening filling its face frame opening.
# Splitter operations subdivide a bay by adding more openings.
# ---------------------------------------------------------------------------
# Bay opening tree walk
#
# bay_openings(layout, bay_index) is the entry point: it walks the
# bay's tree of openings and split nodes (snapshotted into
# layout.bays[i]['tree']) and returns one rect per LEAF opening.
#
# Each rect carries the cage geometry (position + dimensions in
# bay-local coords), the four reveals (distance from cage edge to face
# frame opening edge on each side), and the leaf's identity
# (obj_name, opening_index) so the type-side reconciliation can match
# leaves back to live Blender objects.
#
# A reveal of 0 on a side means the cage edge is flush with the face
# frame opening edge on that side - which happens whenever a face
# frame member sits flush against a panel boundary (top of bottom rail
# = top of bottom panel; mid rail edges = sub-opening cage edges).
# Non-zero reveals come from members whose width exceeds the adjacent
# panel thickness (top rail wider than the carcass top thickness) or
# from stiles wider than the side panel thickness.
# ---------------------------------------------------------------------------
def _bay_root_reveals(layout, bay_index):
    """Reveals on each side of the bay's full cage rect, from the bay's
    perimeter face frame (top rail, bottom rail, end stile, mid div).
    These are inherited downward through the tree on edges that touch
    the bay's perimeter; internal split boundaries reset reveals to 0
    on the perpendicular side because a mid rail / mid stile edge is
    flush with its neighboring sub-cage's edge.
    """
    bay = layout.bays[bay_index]
    cage_left_x, cage_right_x = _cage_x_bounds(layout, bay_index)
    ff_opening_left_x = bay_x_position(layout, bay_index)
    ff_opening_right_x = ff_opening_left_x + bay['width']

    _, _, cage_dim_z = bay_cage_dims(layout, bay_index)
    ff_opening_height = (
        bay['height'] - bay['top_rail_width'] - bay['bottom_rail_width']
    )

    return {
        'top':    cage_dim_z - ff_opening_height,
        'bottom': 0.0,
        'left':   ff_opening_left_x - cage_left_x,
        'right':  cage_right_x - ff_opening_right_x,
    }


def _redistribute_sizes(children, available, splitter_count, splitter_width):
    """Distribute `available` along children; siblings with unlock_size
    hold their stored value, the rest evenly share the remainder. This
    is the same algorithm as _distribute_bay_widths, just running over
    a tree node's children instead of the cabinet's bays.
    """
    consumed_by_splitters = splitter_count * splitter_width
    locked_total = sum(
        c['size'] for c in children if c['unlock_size']
    )
    unlocked = [c for c in children if not c['unlock_size']]
    remainder = available - consumed_by_splitters - locked_total
    share = remainder / len(unlocked) if unlocked else 0.0
    return [c['size'] if c['unlock_size'] else share for c in children]


# Backing kind is implied by the split's axis: H-splits (mid rails)
# always get a shelf, V-splits (mid stiles) always get a division.
_AXIS_TO_BACKING_ROLE = {
    'H': 'BAY_SHELF',
    'V': 'BAY_DIVISION',
}


def _backing_thickness_for_role(layout, role):
    """Material thickness for a carcass backing. Divisions match the
    cabinet's standard carcass material thickness; shelves are fixed at
    3/4" per HB5 carcass conventions."""
    if role == 'BAY_DIVISION':
        return layout.mt
    if role == 'BAY_SHELF':
        return inch(0.75)
    return 0.0


def _emit_h_splitter(node, cage_x, cage_z, cage_dim_x, cage_dim_z,
                     reveals, splitter_top_z, splitter_bottom_z,
                     splitter_index, layout, splitters, backings):
    """Append the mid rail rect for an H-split between two consecutive
    children, plus the matching backing rect if backing_kind isn't
    NONE. All coords are BAY-local."""
    ff_left_x = cage_x + reveals['left']
    ff_width = cage_dim_x - reveals['left'] - reveals['right']
    splitter_w = node['splitter_width']
    splitters.append({
        'role':            'BAY_MID_RAIL',
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'x':               ff_left_x,
        'y':               -layout.fft,
        'z':               splitter_bottom_z,
        'length':          ff_width,
        'splitter_width':  splitter_w,
        'thickness':       layout.fft,
    })
    if not node.get('add_backing', False):
        return
    role = _AXIS_TO_BACKING_ROLE['H']
    bt_thickness = _backing_thickness_for_role(layout, role)
    cage_dim_y = layout.dim_y - layout.fft - layout.bt
    # Backing's TOP face flush with mid rail's TOP edge; backing
    # thickness extends downward from there. Length spans the full
    # carcass interior X (parent cage_dim_x), Width spans full carcass
    # depth, Thickness = backing_thickness on Z.
    backings.append({
        'role':            role,
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'axis':            'H',
        'x':               cage_x,
        'y':               0.0,
        'z':               splitter_top_z - bt_thickness,
        'length':          cage_dim_x,
        'width':           cage_dim_y,
        'thickness':       bt_thickness,
    })


def _emit_v_splitter(node, cage_x, cage_z, cage_dim_x, cage_dim_z,
                     reveals, splitter_left_x, splitter_index, layout,
                     splitters, backings):
    """Append the mid stile rect for a V-split between two consecutive
    children, plus the matching backing rect if backing_kind isn't
    NONE. All coords are BAY-local."""
    ff_bottom_z = cage_z + reveals['bottom']
    ff_height = cage_dim_z - reveals['top'] - reveals['bottom']
    splitter_w = node['splitter_width']
    splitters.append({
        'role':            'BAY_MID_STILE',
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'x':               splitter_left_x,
        'y':               -layout.fft,
        'z':               ff_bottom_z,
        'length':          ff_height,
        'splitter_width':  splitter_w,
        'thickness':       layout.fft,
    })
    if not node.get('add_backing', False):
        return
    role = _AXIS_TO_BACKING_ROLE['V']
    bt_thickness = _backing_thickness_for_role(layout, role)
    cage_dim_y = layout.dim_y - layout.fft - layout.bt
    # Vertical division centered on the mid stile (X-wise). Spans full
    # carcass interior Z (parent cage_dim_z) and full depth.
    stile_center_x = splitter_left_x + splitter_w / 2.0
    backing_left_x = stile_center_x - bt_thickness / 2.0
    backings.append({
        'role':            role,
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'axis':            'V',
        'x':               backing_left_x,
        'y':               0.0,
        'z':               cage_z,
        'length':          cage_dim_z,
        'width':           cage_dim_y,
        'thickness':       bt_thickness,
    })


def _walk_tree(node, layout, bay_index,
               cage_x, cage_z, cage_dim_x, cage_dim_z,
               reveals, leaves, splitters, backings):
    """Recursively descend a tree node. Emits leaf rects, splitter
    rects (mid rails / mid stiles), and backing rects (divisions /
    shelves) into the three lists provided by the caller."""
    if node['kind'] == 'leaf':
        leaves.append({
            'obj_name':       node['obj_name'],
            'opening_index':  node.get('opening_index', 0),
            'cage_x':         cage_x,
            'cage_z':         cage_z,
            'cage_dim_x':     cage_dim_x,
            'cage_dim_z':     cage_dim_z,
            'reveal_top':     reveals['top'],
            'reveal_bottom':  reveals['bottom'],
            'reveal_left':    reveals['left'],
            'reveal_right':   reveals['right'],
        })
        return

    children = node['children']
    if not children:
        return
    n_children = len(children)
    n_splitters = n_children - 1
    splitter_w = node['splitter_width']

    if node['axis'] == 'H':
        ff_avail_z = cage_dim_z - reveals['top'] - reveals['bottom']
        sizes = _redistribute_sizes(
            children, ff_avail_z, n_splitters, splitter_w
        )
        ff_opening_top_z = cage_z + cage_dim_z - reveals['top']
        cur_z_top = ff_opening_top_z
        for i, child in enumerate(children):
            child_size = sizes[i]
            child_ff_bottom_z = cur_z_top - child_size
            child_reveal_top = reveals['top'] if i == 0 else 0.0
            child_reveal_bottom = reveals['bottom'] if i == n_children - 1 else 0.0
            child_cage_top_z = cur_z_top + child_reveal_top
            child_cage_bottom_z = child_ff_bottom_z - child_reveal_bottom
            child_cage_dim_z = child_cage_top_z - child_cage_bottom_z

            child_reveals = {
                'top':    child_reveal_top,
                'bottom': child_reveal_bottom,
                'left':   reveals['left'],
                'right':  reveals['right'],
            }
            _walk_tree(
                child, layout, bay_index,
                cage_x=cage_x,
                cage_z=child_cage_bottom_z,
                cage_dim_x=cage_dim_x,
                cage_dim_z=child_cage_dim_z,
                reveals=child_reveals,
                leaves=leaves, splitters=splitters, backings=backings,
            )
            if i < n_children - 1:
                # Mid rail sits below this child's FF bottom edge.
                splitter_top_z = child_ff_bottom_z
                splitter_bottom_z = splitter_top_z - splitter_w
                _emit_h_splitter(
                    node, cage_x, cage_z, cage_dim_x, cage_dim_z,
                    reveals, splitter_top_z, splitter_bottom_z,
                    splitter_index=i, layout=layout,
                    splitters=splitters, backings=backings,
                )
            cur_z_top = child_ff_bottom_z - splitter_w
    else:
        ff_avail_x = cage_dim_x - reveals['left'] - reveals['right']
        sizes = _redistribute_sizes(
            children, ff_avail_x, n_splitters, splitter_w
        )
        ff_opening_left_x = cage_x + reveals['left']
        cur_x_left = ff_opening_left_x
        for i, child in enumerate(children):
            child_size = sizes[i]
            child_ff_right_x = cur_x_left + child_size
            child_reveal_left = reveals['left'] if i == 0 else 0.0
            child_reveal_right = reveals['right'] if i == n_children - 1 else 0.0
            child_cage_left_x = cur_x_left - child_reveal_left
            child_cage_right_x = child_ff_right_x + child_reveal_right
            child_cage_dim_x = child_cage_right_x - child_cage_left_x

            child_reveals = {
                'top':    reveals['top'],
                'bottom': reveals['bottom'],
                'left':   child_reveal_left,
                'right':  child_reveal_right,
            }
            _walk_tree(
                child, layout, bay_index,
                cage_x=child_cage_left_x,
                cage_z=cage_z,
                cage_dim_x=child_cage_dim_x,
                cage_dim_z=cage_dim_z,
                reveals=child_reveals,
                leaves=leaves, splitters=splitters, backings=backings,
            )
            if i < n_children - 1:
                splitter_left_x = child_ff_right_x
                _emit_v_splitter(
                    node, cage_x, cage_z, cage_dim_x, cage_dim_z,
                    reveals, splitter_left_x,
                    splitter_index=i, layout=layout,
                    splitters=splitters, backings=backings,
                )
            cur_x_left = child_ff_right_x + splitter_w


def bay_openings(layout, bay_index):
    """Walk one bay's tree and return its parts.

    Returns a dict with three lists in BAY-local coords:
      - 'leaves':    opening rects (cage geometry + reveals + identity)
      - 'splitters': mid rail / mid stile rects (face frame members
                     between consecutive children of each split node)
      - 'backings':  division / shelf rects (carcass-deep panels behind
                     each splitter, only present when the split's
                     backing_kind is SHELF or DIVISION)

    With no splits in the bay's tree the result is a single leaf and
    empty splitter / backing lists - same as the pre-tree behavior.
    """
    bay = layout.bays[bay_index]
    tree = bay.get('tree')
    empty = {'leaves': [], 'splitters': [], 'backings': []}
    if tree is None:
        return empty
    cage_dim_x_, _, cage_dim_z_ = bay_cage_dims(layout, bay_index)
    leaves, splitters, backings = [], [], []
    _walk_tree(
        tree, layout, bay_index,
        cage_x=0.0, cage_z=0.0,
        cage_dim_x=cage_dim_x_, cage_dim_z=cage_dim_z_,
        reveals=_bay_root_reveals(layout, bay_index),
        leaves=leaves, splitters=splitters, backings=backings,
    )
    return {'leaves': leaves, 'splitters': splitters, 'backings': backings}


# ---------------------------------------------------------------------------
# Compatibility wrappers - thin shims that route through bay_openings.
# Kept so existing callers (and any external tools) don't break; new
# code should consume bay_openings() directly.
# ---------------------------------------------------------------------------
def opening_count(layout, bay_index):
    return len(bay_openings(layout, bay_index)['leaves'])


def opening_position(layout, bay_index, opening_index):
    leaves = bay_openings(layout, bay_index)['leaves']
    if opening_index >= len(leaves):
        return (0.0, 0.0, 0.0)
    r = leaves[opening_index]
    return (r['cage_x'], 0.0, r['cage_z'])


def opening_dims(layout, bay_index, opening_index):
    leaves = bay_openings(layout, bay_index)['leaves']
    cage_dim_y = bay_cage_dims(layout, bay_index)[1]
    if opening_index >= len(leaves):
        return (0.0, cage_dim_y, 0.0)
    r = leaves[opening_index]
    return (r['cage_dim_x'], cage_dim_y, r['cage_dim_z'])


# ---------------------------------------------------------------------------
# Door / drawer front geometry (children of opening cage)
# ---------------------------------------------------------------------------
def resolved_overlay(cab_props, opening_props, side):
    """Return the effective overlay for one side of an opening.

    side is one of 'top', 'bottom', 'left', 'right'. If the opening
    unlocks that side, its own value wins; otherwise the cabinet-level
    default is used.
    """
    if getattr(opening_props, f'unlock_{side}_overlay'):
        return getattr(opening_props, f'{side}_overlay')
    return getattr(cab_props, f'default_{side}_overlay')


# Construction constants for visual open state. Cabinet-level
# customization can come later; for now the values match typical
# residential hinge / slide hardware.
DOOR_MAX_SWING_ANGLE = math.radians(100.0)
DOUBLE_DOOR_REVEAL = inch(0.125)
# Forward offset of door / drawer front from the face frame face.
# Mirrors the visible reveal between the back of an overlay door and
# the front of the frame on real cabinetry.
DOOR_TO_FRAME_GAP = inch(0.125)


def _door_panel_size(rect, cab_props, opening_props):
    """Width and height of the door panel covering this opening's face
    frame opening plus per-side overlay. For DOUBLE this is the
    combined width across both leaves; the per-leaf width is derived
    in the leaf builder by subtracting the reveal gap and halving.

    `rect` is one entry from bay_openings() - it carries the cage
    dimensions and the four reveals for this specific opening, which
    fully determines the face frame opening size on each axis.
    """
    opening_width = (
        rect['cage_dim_x'] - rect['reveal_left'] - rect['reveal_right']
    )
    opening_height = (
        rect['cage_dim_z'] - rect['reveal_top'] - rect['reveal_bottom']
    )
    width = (
        opening_width
        + resolved_overlay(cab_props, opening_props, 'left')
        + resolved_overlay(cab_props, opening_props, 'right')
    )
    height = (
        opening_height
        + resolved_overlay(cab_props, opening_props, 'top')
        + resolved_overlay(cab_props, opening_props, 'bottom')
    )
    return width, height


def _drawer_max_slide(layout, cab_props):
    """Maximum forward translation for a drawer/pullout front. Aimed at
    "near full extension": cabinet depth minus face frame thickness
    minus 1 inch of clearance. Becomes a cabinet prop later if
    customization is wanted.
    """
    return max(0.0, layout.dim_y - layout.fft - inch(1.0))


# ---------------------------------------------------------------------------
# Front leaves: per-opening descriptor of each front panel + its pivot.
#
# Most front configurations have a single leaf. DOUBLE doors have two
# (left + right half-width leaves meeting in the middle with a small
# reveal gap). The type code iterates this list and creates one
# (pivot, part) pair per leaf.
#
# Each leaf is a dict with keys:
#   'role'           PART_ROLE_DOOR / _DRAWER_FRONT / _PULLOUT_FRONT
#   'name'           Human-readable part name ("Door", "Door (Left)", ...)
#   'pivot_position' (x, y, z) in OPENING-local coords
#   'pivot_rotation' (rx, ry, rz)
#   'part_position'  (x, y, z) in PIVOT-local coords
#   'part_dims'      (length, width, thickness)
# ---------------------------------------------------------------------------
_FRONT_TYPE_TO_ROLE_NAME = {
    'DOOR':         ('DOOR',          'Door'),
    'DRAWER_FRONT': ('DRAWER_FRONT',  'Drawer Front'),
    'PULLOUT':      ('PULLOUT_FRONT', 'Pullout Front'),
    'FALSE_FRONT':  ('FALSE_FRONT',   'False Front'),
}


def _single_door_leaf_pivot(layout, rect, cab_props, opening_props):
    """Pivot position + rotation for a single-leaf door (LEFT / RIGHT /
    TOP / BOTTOM hinge), and the door's offset inside the pivot.
    Shared between DOOR and PULLOUT (PULLOUT in v1 uses door geometry
    but its pivot rotation is forced to identity by the caller).
    """
    door_thickness = cab_props.door_thickness
    width, height = _door_panel_size(rect, cab_props, opening_props)
    left_overlay = resolved_overlay(cab_props, opening_props, 'left')
    bottom_overlay = resolved_overlay(cab_props, opening_props, 'bottom')

    # Door pivot lives in OPENING-local coords. The opening cage origin
    # for this leaf is at (rect['cage_x'], 0, rect['cage_z']) in bay
    # local coords; in OPENING local that's (0, 0, 0). The face frame
    # opening's left edge is at opening-local X = reveal_left, bottom
    # at Z = reveal_bottom.
    base_x = rect['reveal_left'] - left_overlay
    base_y = -layout.fft - DOOR_TO_FRAME_GAP - door_thickness
    base_z = rect['reveal_bottom'] - bottom_overlay

    angle = opening_props.swing_percent * DOOR_MAX_SWING_ANGLE
    hinge = opening_props.hinge_side

    if hinge == 'RIGHT':
        return {
            'pivot_position': (base_x + width, base_y, base_z),
            'pivot_rotation': (0.0, 0.0, +angle),
            'part_position':  (-width, 0.0, 0.0),
        }
    if hinge == 'TOP':
        return {
            'pivot_position': (base_x, base_y, base_z + height),
            'pivot_rotation': (-angle, 0.0, 0.0),
            'part_position':  (0.0, 0.0, -height),
        }
    if hinge == 'BOTTOM':
        return {
            'pivot_position': (base_x, base_y, base_z),
            'pivot_rotation': (+angle, 0.0, 0.0),
            'part_position':  (0.0, 0.0, 0.0),
        }
    # LEFT (and DOUBLE doesn't reach here - handled separately)
    return {
        'pivot_position': (base_x, base_y, base_z),
        'pivot_rotation': (0.0, 0.0, -angle),
        'part_position':  (0.0, 0.0, 0.0),
    }


def _double_door_leaves(layout, rect, cab_props, opening_props, role):
    """Two leaves for a DOUBLE door: left half hinged on its outer-left
    edge, right half hinged on its outer-right edge, with a small
    DOUBLE_DOOR_REVEAL gap where they meet in the middle.
    """
    door_thickness = cab_props.door_thickness
    width, height = _door_panel_size(rect, cab_props, opening_props)
    leaf_width = (width - DOUBLE_DOOR_REVEAL) / 2.0
    left_overlay = resolved_overlay(cab_props, opening_props, 'left')
    bottom_overlay = resolved_overlay(cab_props, opening_props, 'bottom')

    base_x = rect['reveal_left'] - left_overlay
    base_y = -layout.fft - DOOR_TO_FRAME_GAP - door_thickness
    base_z = rect['reveal_bottom'] - bottom_overlay
    angle = opening_props.swing_percent * DOOR_MAX_SWING_ANGLE

    return [
        {
            'role': role, 'name': 'Door (Left)',
            'pivot_position': (base_x, base_y, base_z),
            'pivot_rotation': (0.0, 0.0, -angle),
            'part_position':  (0.0, 0.0, 0.0),
            'part_dims':      (height, leaf_width, door_thickness),
        },
        {
            'role': role, 'name': 'Door (Right)',
            'pivot_position': (base_x + width, base_y, base_z),
            'pivot_rotation': (0.0, 0.0, +angle),
            'part_position':  (-leaf_width, 0.0, 0.0),
            'part_dims':      (height, leaf_width, door_thickness),
        },
    ]


def _drawer_or_pullout_slide_leaf(layout, rect, cab_props,
                                  opening_props, role, name):
    """Single-leaf slide-out front. Pivot translates in -Y by
    swing_percent * max_slide; no rotation."""
    door_thickness = cab_props.door_thickness
    width, height = _door_panel_size(rect, cab_props, opening_props)
    left_overlay = resolved_overlay(cab_props, opening_props, 'left')
    bottom_overlay = resolved_overlay(cab_props, opening_props, 'bottom')

    base_x = rect['reveal_left'] - left_overlay
    base_y = -layout.fft - DOOR_TO_FRAME_GAP - door_thickness
    base_z = rect['reveal_bottom'] - bottom_overlay
    slide = opening_props.swing_percent * _drawer_max_slide(layout, cab_props)

    return {
        'role': role, 'name': name,
        'pivot_position': (base_x, base_y - slide, base_z),
        'pivot_rotation': (0.0, 0.0, 0.0),
        'part_position':  (0.0, 0.0, 0.0),
        'part_dims':      (height, width, door_thickness),
    }


class _ZeroSwingProxy:
    """Wraps an opening_props instance and reports swing_percent as 0.
    Used for FALSE_FRONT so the leaf builder can be reused without
    branching on slide behavior inside it.
    """
    __slots__ = ('_inner',)
    def __init__(self, inner):
        object.__setattr__(self, '_inner', inner)
    def __getattr__(self, name):
        if name == 'swing_percent':
            return 0.0
        return getattr(self._inner, name)


def front_leaves(layout, rect, cab_props, opening_props):
    """List of leaf descriptors for one opening's front parts.

    `rect` is the opening's entry from bay_openings() - it provides
    cage geometry and reveals so leaves don't need to be told which
    bay/opening_index they belong to.

    Empty list when front_type is NONE. Single-element for most
    configurations; two elements for DOUBLE doors (one per leaf).
    """
    front_type = opening_props.front_type
    if front_type == 'NONE':
        return []
    role, base_name = _FRONT_TYPE_TO_ROLE_NAME[front_type]

    if front_type in ('DRAWER_FRONT', 'PULLOUT', 'FALSE_FRONT'):
        # FALSE_FRONT shares drawer geometry but is fixed - we hand the
        # leaf builder a synthetic opening_props with swing_percent
        # zeroed so the panel never translates forward, regardless of
        # any stale value left on the real props.
        leaf_props = opening_props
        if front_type == 'FALSE_FRONT':
            leaf_props = _ZeroSwingProxy(opening_props)
        return [_drawer_or_pullout_slide_leaf(
            layout, rect, cab_props, leaf_props, role, base_name
        )]

    # DOOR
    if opening_props.hinge_side == 'DOUBLE':
        return _double_door_leaves(
            layout, rect, cab_props, opening_props, role
        )

    width, height = _door_panel_size(rect, cab_props, opening_props)
    leaf = _single_door_leaf_pivot(layout, rect, cab_props, opening_props)
    leaf['role'] = role
    leaf['name'] = base_name
    leaf['part_dims'] = (height, width, cab_props.door_thickness)
    return [leaf]


# ---------------------------------------------------------------------------
# Interior items (shelves, accessory labels, ...). Lives behind the face
# frame, inside the bay carcass cavity.
#
# Coordinate space for every descriptor is OPENING-LOCAL: x in [0, cage_dim_x],
# y in [0, cage_dim_y] (y = 0 at back face of face frame, growing into the
# cabinet), z in [0, cage_dim_z] (z = 0 at top of bay's bottom panel).
# ---------------------------------------------------------------------------
SHELF_THICKNESS = inch(0.75)
SHELF_X_CLEARANCE = inch(1.0 / 16.0)   # side gap for shelf-pin clearance
SHELF_FRONT_SETBACK = inch(0.25)       # tucked behind the face frame plane
SHELF_BACK_SETBACK = inch(0.25)        # finger gap to the back panel

ACCESSORY_TEXT_SIZE = inch(1.5)
ACCESSORY_Y_OFFSET = inch(1.0)         # nudge into the cavity so it reads
                                       # cleanly against the cabinet back


def auto_shelf_qty(opening_height):
    """Default count of adjustable shelves for an opening of `opening_height`
    interior height: one shelf per ~12 inches, with a one-shelf floor.
    Used for both initial seeding (when an interior item is added) and
    live recompute (when unlock_shelf_qty is False).
    """
    return max(1, int((opening_height or 0.0) / inch(12.0)))


def _adjustable_shelf_descriptors(rect, cage_dim_y, qty):
    """Build descriptors for `qty` evenly-spaced shelves in this opening.
    Returns an empty list if qty <= 0 or the cage is too short to hold
    a single shelf at the requested thickness.
    """
    if qty <= 0:
        return []
    cage_dim_x = rect['cage_dim_x']
    cage_dim_z = rect['cage_dim_z']

    interior_h = cage_dim_z - qty * SHELF_THICKNESS
    if interior_h <= 0:
        return []
    spacing = interior_h / (qty + 1)

    length = max(0.0, cage_dim_x - 2 * SHELF_X_CLEARANCE)
    width = max(0.0, cage_dim_y - SHELF_FRONT_SETBACK - SHELF_BACK_SETBACK)

    items = []
    for k in range(qty):
        # Shelf k bottom-face Z: stack from the bottom with one spacing
        # gap before the first shelf and one after the last.
        z = (k + 1) * spacing + k * SHELF_THICKNESS
        items.append({
            'kind':     'ADJUSTABLE_SHELF',
            'role':     'ADJUSTABLE_SHELF',
            'name':     f'Adjustable Shelf {k + 1}',
            'position': (SHELF_X_CLEARANCE, SHELF_FRONT_SETBACK, z),
            'dims':     (length, width, SHELF_THICKNESS),
        })
    return items


def _accessory_label_descriptor(rect, cage_dim_y, label):
    """Build a single text-label descriptor centered in the opening,
    facing -Y (readable from the front of the cabinet). Position is the
    text origin; the recalc applies rotation and font size from the
    descriptor.
    """
    cage_dim_x = rect['cage_dim_x']
    cage_dim_z = rect['cage_dim_z']
    return {
        'kind':     'ACCESSORY',
        'role':     'ACCESSORY_LABEL',
        'name':     f'Accessory Label - {label}' if label else 'Accessory Label',
        'position': (cage_dim_x / 2.0,
                     min(ACCESSORY_Y_OFFSET, max(0.0, cage_dim_y - inch(0.25))),
                     cage_dim_z / 2.0),
        # Rotation around X by +90 degrees turns a default text
        # object's front face (+Z) toward -Y so it's readable from the
        # cabinet front. Centering (align_x = CENTER, align_y = CENTER)
        # is applied in the recalc since it's font-data, not transform.
        'rotation': (math.radians(90.0), 0.0, 0.0),
        'text':     label or 'Accessory',
        'size':     ACCESSORY_TEXT_SIZE,
    }


def interior_item_descriptors(layout, rect, cab_props, opening_props):
    """Flatten one opening's interior_items collection into a list of
    geometry descriptors for the recalc to materialize. One InteriorItem
    can produce many descriptors (e.g., ADJUSTABLE_SHELF with qty=3 ->
    three shelf descriptors).

    Each descriptor carries a 'kind' field so the recalc can pick the
    right Blender object type (mesh part vs text object) without
    re-reading the source collection.
    """
    cage_dim_y = layout.dim_y - layout.fft - layout.bt
    out = []
    for item in opening_props.interior_items:
        if item.kind == 'ADJUSTABLE_SHELF':
            out.extend(_adjustable_shelf_descriptors(
                rect, cage_dim_y, item.shelf_qty
            ))
        elif item.kind == 'ACCESSORY':
            out.append(_accessory_label_descriptor(
                rect, cage_dim_y, item.accessory_label
            ))
    return out
