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
        self.tkh = cab.toe_kick_height if self.has_toe_kick else 0.0
        self.tks = cab.toe_kick_setback if self.has_toe_kick else 0.0
        self.tkt = cab.toe_kick_thickness if self.has_toe_kick else 0.0

        # End stile widths
        self.lsw = cab.left_stile_width
        self.rsw = cab.right_stile_width

        # Rail width defaults (used when populating a fresh bay)
        self.default_top_rail_width = cab.top_rail_width
        self.default_bottom_rail_width = cab.bottom_rail_width

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
    return (0.0, -layout.dim_y, layout.tkh)


def left_end_stile_dims(layout):
    return (layout.dim_z - layout.tkh, layout.lsw, layout.fft)


def right_end_stile_position(layout):
    """Right end stile sits at x=dim_x. With z rotation 90 and the part's
    Mirror settings, the geometry extends in -X by rsw amount.
    """
    return (layout.dim_x, -layout.dim_y, layout.tkh)


def right_end_stile_dims(layout):
    return (layout.dim_z - layout.tkh, layout.rsw, layout.fft)


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


def carcass_bottom_segments(layout):
    """Per-segment bay floor panels.

    Each segment becomes one carcass-bottom object positioned to support
    the bay or run of bays. Position matches the bay's bottom_z + bottom
    rail width offset so the panel TOP aligns with where the bay cage sits.
    """
    segments = []
    for start, end in _compute_segments(layout, _carcass_bottom_passthrough):
        first_bay = layout.bays[start]
        x = bay_x_position(layout, start)
        length = first_bay['width']
        for k in range(start, end):
            length += layout.mid_stiles[k]['width']
            length += layout.bays[k + 1]['width']
        # Origin Y is at the front face of the back panel; Mirror Y on the
        # part extends the panel in -Y toward the face frame. Z origin is
        # one panel-thickness below the bay's floor (so the panel's TOP
        # surface lands at bay_bottom_z + bottom_rail_width).
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          x,
            'y':          -layout.dim_y + first_bay['depth'] - layout.bt,
            'z':          bay_bottom_z(layout, start) + first_bay['bottom_rail_width'] - layout.mt,
            'length':     length,
            'panel_dim_y': first_bay['depth'] - layout.bt - layout.fft,
            'thickness':  layout.mt,
        })
    return segments


# ---------------------------------------------------------------------------
# Mid division - the carcass partition behind each mid stile
# ---------------------------------------------------------------------------
def mid_division_position(layout, gap_index):
    """X, Y, Z position for the partition behind mid stile N.

    Sits centered on the mid stile (X), at the back-panel front face (Y),
    and at the same Z as the mid stile bottom (so length matches).
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
        # Asymmetric depths - sit on the deeper-bay side
        x = base_x + msw / 2.0

    # Y at the back panel front face of the deeper bay (max depth)
    use_depth = max(bay_a['depth'], bay_b['depth'])
    y = -layout.dim_y + use_depth - layout.bt

    # Z matches the mid stile's bottom
    z = min(bay_bottom_z(layout, gap_index),
            bay_bottom_z(layout, gap_index + 1))
    if bottom_rail_passthrough(layout, gap_index):
        z += bay_a['bottom_rail_width']
    z -= ms['extend_down_amount']

    return (x, y, z)


def mid_division_dims(layout, gap_index):
    """Length (vertical), Width (depth into cabinet), Thickness."""
    if gap_index >= len(layout.mid_stiles):
        return (0.0, 0.0, layout.mt)
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]

    # Length matches mid stile length (same logic as mid_stile_dims)
    bottom_z = min(bay_bottom_z(layout, gap_index),
                   bay_bottom_z(layout, gap_index + 1))
    if bottom_rail_passthrough(layout, gap_index):
        bottom_z += bay_a['bottom_rail_width']
    bottom_z -= ms['extend_down_amount']

    top_z = max(bay_top_z(layout, gap_index),
                bay_top_z(layout, gap_index + 1))
    if top_rail_passthrough(layout, gap_index):
        top_z -= bay_a['top_rail_width']
    top_z += ms['extend_up_amount']

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
