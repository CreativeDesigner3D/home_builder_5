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
import bpy

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
        self.corner_type = cab.corner_type

        # Cabinet dimensions
        self.dim_x = cab.width
        self.dim_y = cab.depth
        self.dim_z = cab.height

        # Angled standard cabinet (single-bay only): per-side depths drive
        # the front face frame plane, leaving the back at dim_y. Captured
        # here so the side / face frame solvers branch on a single flag
        # without re-reading cab props. is_angled gates the branch and is
        # finalized below once bay_count is known.
        self.unlock_left_depth = cab.unlock_left_depth
        self.unlock_right_depth = cab.unlock_right_depth
        self.cab_left_depth = cab.left_depth
        self.cab_right_depth = cab.right_depth

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
        self.toe_kick_type = (cab.toe_kick_type
                              if self.has_toe_kick else 'FLOATING')
        self.extend_left_stile_to_floor = cab.extend_left_stile_to_floor
        self.extend_right_stile_to_floor = cab.extend_right_stile_to_floor
        self.kick_inset_left = (cab.inset_toe_kick_left
                                if self.has_toe_kick else 0.0)
        self.kick_inset_right = (cab.inset_toe_kick_right
                                 if self.has_toe_kick else 0.0)
        self.back_bottom_inset = cab.back_bottom_inset
        self.finish_kick_thickness = cab.finish_toe_kick_thickness
        self.include_finish_kick = cab.include_finish_toe_kick

        # End stile widths
        self.lsw = cab.left_stile_width
        self.rsw = cab.right_stile_width

        # Blind corner offsets - amount the FF plane is shrunk on each
        # side when the corresponding end is configured as blind. Zero
        # otherwise. Used by face_frame_length and ff_outer_world_pos
        # so end stiles, rails, and bays all naturally fit inside the
        # remaining FF area; the blind panels themselves still anchor
        # to the cabinet's outer edges (x=0 / x=dim_x).
        is_blind_left = (cab.left_stile_type == 'BLIND'
                         and cab.blind_left
                         and cab.blind_amount_left > 0)
        is_blind_right = (cab.right_stile_type == 'BLIND'
                          and cab.blind_right
                          and cab.blind_amount_right > 0)
        self.blind_offset_left = cab.blind_amount_left if is_blind_left else 0.0
        self.blind_offset_right = cab.blind_amount_right if is_blind_right else 0.0

        # Side scribe + finish end condition. The pair determines how
        # far the side panel sits inboard of the face frame outer face
        # via left_scribe_offset / right_scribe_offset.
        self.l_scribe = cab.left_scribe
        self.r_scribe = cab.right_scribe
        self.l_fin_end = cab.left_finished_end_condition
        self.r_fin_end = cab.right_finished_end_condition
        self.b_fin_end = cab.back_finished_end_condition
        self.top_scribe = cab.top_scribe
        self.division_thickness = cab.division_thickness

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

        # Angled mode is exclusive with corner cabinets and only valid on
        # single-bay carcasses (UI hides the unlocks otherwise).
        self.is_angled = (
            self.corner_type == 'NONE'
            and self.bay_count == 1
            and (self.unlock_left_depth or self.unlock_right_depth)
        )

        # Angled cabinets always use a solid top regardless of cabinet
        # type. The boolean cutter that produces the trapezoidal top /
        # bottom / shelves operates on full panels; stretchers would
        # need separate per-strip trimming and would defeat the point
        # of a single uniform cutter.
        if self.is_angled:
            self.uses_stretchers = False

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
            'remove_carcass':     bp.remove_carcass,
            'floating_bay':       bp.floating_bay,
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
            'height':             self.dim_z,
            'depth':              self.dim_y,
            'kick_height':        self.tkh,
            'top_offset':         0.0,
            'top_rail_width':     self.default_top_rail_width,
            'bottom_rail_width':  self.default_bottom_rail_width,
            'remove_bottom':      False,
            'remove_carcass':     False,
            'floating_bay':       False,
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
    if layout.l_fin_end == 'FINISHED':
        return 0.0
    if layout.l_fin_end == 'PANELED':
        return inch(0.75)
    # 1/4 applied panels (FLUSH_X strip + textured beadboard / shiplap)
    # all sit in a 1/4 scribe gap so they tuck flush against the side.
    if layout.l_fin_end in ('FLUSH_X', 'BEADBOARD', 'SHIPLAP'):
        return inch(0.25)
    return layout.l_scribe


def left_side_thickness(layout):
    """Left side panel thickness. FINISHED sides are 3/4 stock (the
    side IS the visible outer face); other conditions use the cabinet's
    material_thickness (typically 1/2). Tops, bottoms, and dividers
    stay at material_thickness in all cases.
    """
    if layout.l_fin_end == 'FINISHED':
        return inch(0.75)
    return layout.mt


def right_scribe_offset(layout):
    if layout.r_fin_end == 'FINISHED':
        return 0.0
    if layout.r_fin_end == 'PANELED':
        return inch(0.75)
    if layout.r_fin_end in ('FLUSH_X', 'BEADBOARD', 'SHIPLAP'):
        return inch(0.25)
    return layout.r_scribe


def right_side_thickness(layout):
    """See left_side_thickness."""
    if layout.r_fin_end == 'FINISHED':
        return inch(0.75)
    return layout.mt


def back_thickness(layout):
    """Carcass back panel thickness. Always the cabinet's back_thickness
    prop (typically 1/4) regardless of finish condition - the FINISHED
    back is rendered as a SEPARATE 3/4 applied panel layered on top of
    the carcass back, not by thickening the carcass back itself. See
    _reconcile_finished_back for the applied piece.
    """
    return layout.bt


def carcass_inner_left_x(layout):
    """X of the left side panel's inner face - the left bound of the
    cabinet's interior cavity. Outer face sits at left_scribe_offset;
    thickness depends on the finish condition (3/4 for FINISHED,
    material_thickness otherwise)."""
    return left_scribe_offset(layout) + left_side_thickness(layout)


def carcass_inner_right_x(layout):
    """X of the right side panel's inner face."""
    return layout.dim_x - right_scribe_offset(layout) - right_side_thickness(layout)


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
    if layout.l_fin_end == 'FINISHED':
        return bay_top_z(layout, 0)
    return carcass_top_z(layout, 0)


def right_side_top_z(layout):
    last = layout.bay_count - 1
    if layout.r_fin_end == 'FINISHED':
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
# Bases / talls anchor at the floor. bay.height is floor to top of top rail;
# bay.kick_height is floor to bottom of bottom rail (the toe kick recess
# height). bay_bottom_z / bay_top_z map directly to these.
# Uppers anchor at the cabinet top: bay_top_z is fixed by dim_z - top_offset,
# and bay_height extends downward from there. Uppers carry kick_height = 0.
#
# All Z positions for bottom rails, bay cages, mid stile bottoms, and the
# bottom-rail passthrough check go through these helpers.
def bay_bottom_z(layout, bay_index):
    """Z of the bay's bottom edge (bottom of the bottom rail / top of
    toe kick recess for base / tall)."""
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'UPPER':
        return layout.dim_z - bay['top_offset'] - bay['height']
    return bay['kick_height']


def bay_top_z(layout, bay_index):
    """Z of the bay's top edge (top of the top rail)."""
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'UPPER':
        return layout.dim_z - bay['top_offset']
    return bay['height']


def side_bottom_z(layout, bay_index, side='LEFT'):
    """Z of the carcass side panel's bottom edge.

    NOTCH and FLUSH run sides to the floor (a corner notch handles the
    recess for NOTCH; the wide bottom rail handles it for FLUSH).
    FLOATING and uppers anchor the side at the bay bottom.

    Per-bay override: floating_bay forces this bay's side to anchor at
    the bay bottom regardless of cabinet toe_kick_type.

    Inset exception: kick_inset_left / kick_inset_right > 0 means a
    return part is wrapping the kick at that end and the side floats
    by kick_height on that side, so the inset region is open from
    the floor up to the cabinet bottom panel.
    """
    if not layout.has_toe_kick:
        return bay_bottom_z(layout, bay_index)
    if layout.toe_kick_type == 'FLOATING':
        return bay_bottom_z(layout, bay_index)
    if layout.bays[bay_index].get('floating_bay'):
        return bay_bottom_z(layout, bay_index)
    # NOTCH / FLUSH default to floor unless this side has a kick inset.
    if side == 'LEFT' and layout.kick_inset_left > 0:
        return bay_bottom_z(layout, bay_index)
    if side == 'RIGHT' and layout.kick_inset_right > 0:
        return bay_bottom_z(layout, bay_index)
    return 0.0


def left_stile_to_floor(layout):
    """End stile extends past the bay bottom down to the floor when the
    user enables it explicitly, or when FLUSH is on (a wide bottom rail
    butts into a full-height stile rather than the other way around).
    Uppers don't have a kick to fill, so the option no-ops there.
    """
    if not layout.has_toe_kick:
        return False
    if layout.toe_kick_type == 'FLUSH':
        return True
    return layout.extend_left_stile_to_floor


def right_stile_to_floor(layout):
    if not layout.has_toe_kick:
        return False
    if layout.toe_kick_type == 'FLUSH':
        return True
    return layout.extend_right_stile_to_floor


# ---------------------------------------------------------------------------
# Toe kick subfront - the visible front face of the recess
# ---------------------------------------------------------------------------
def has_kick_subfront(layout):
    """Subfront only exists for NOTCH (recessed kick). FLUSH replaces
    it with the wide bottom rail; FLOATING leaves the kick to a separate
    base assembly; uppers have no kick.
    """
    return layout.has_toe_kick and layout.toe_kick_type == 'NOTCH'


def _kick_subfront_passthrough(layout, gap_index):
    """True if a single kick subfront spans gap_index uninterrupted.
    Breaks where adjacent bays have different kick_heights, where
    either bay has remove_bottom or remove_carcass set, or where either
    bay is flagged floating_bay (no kick parts emitted at that bay).
    """
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_a['kick_height'], bay_b['kick_height']):
        return False
    if (bay_a.get('remove_bottom') or bay_b.get('remove_bottom')
            or bay_a.get('remove_carcass') or bay_b.get('remove_carcass')):
        return False
    if bay_a.get('floating_bay') or bay_b.get('floating_bay'):
        return False
    return True


def kick_subfront_segments(layout):
    """Toe kick subfront segments. Captured between the carcass sides
    (and between mid divisions at interior breaks via _segment_x_bounds).
    Breaks where adjacent bays have different kick_heights so each
    segment can take its bay's kick_height as its Width. Insets are
    only honored at the cabinet ends - interior breaks butt against
    the meeting plane.
    """
    if not has_kick_subfront(layout):
        return []
    segments = []
    last_bay = layout.bay_count - 1
    for start, end in _compute_segments(layout, _kick_subfront_passthrough):
        first_bay = layout.bays[start]
        if first_bay.get('remove_bottom') or first_bay.get('remove_carcass'):
            continue
        if first_bay.get('floating_bay'):
            continue
        left_x, right_x = _segment_x_bounds(layout, start, end)
        if start == 0:
            if layout.kick_inset_left > 0:
                # Inset with return: main kick butts against the return's
                # inboard face at (inset + tkt).
                left_x = layout.kick_inset_left + layout.tkt
            # else: kick captured between sides at carcass_inner_left_x
        if end == last_bay:
            if layout.kick_inset_right > 0:
                right_x = (layout.dim_x - layout.kick_inset_right
                           - layout.tkt)
        wx, wy, wz = ff_perpendicular_offset_at_world_x(
            layout, left_x, layout.tks + layout.tkt, 0.0
        )
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          wx,
            # Y sits at the notch's back wall: tks back from the cabinet
            # front, plus tkt so the kick's FRONT face is flush with the
            # notch back. The kick is captured between the side panels
            # at world X = left_x and right_x, so we anchor at world X
            # (not FF-x). Length is along the kick's own +X axis (FF-
            # aligned after rotation), which spans 1/cos farther than
            # the world X delta in angled mode.
            'y':          wy,
            'z':          wz,
            'length':     ff_world_x_span_to_length(layout, right_x - left_x),
            'width':      first_bay['kick_height'],
            'thickness':  layout.tkt,
        })
    return segments


def has_finish_kick(layout):
    """Finish toe kick is the visible 1/4 face board applied to the
    front of the kick subfront. Requires include_finish_kick on
    cab_props plus a subfront to apply to.
    """
    return has_kick_subfront(layout) and layout.include_finish_kick


def finish_kick_segments(layout):
    """Finish toe kick segments. Same passthrough as the subfront so a
    segmented subfront gets a matching segmented finish, but X spans
    the FULL cabinet width at the ends (not captured between sides) -
    interior breaks still meet at the carcass meeting plane to line up
    with the subfront break behind them. Y sits in front of the
    subfront so its back face is flush with the subfront's front.

    Stile-to-floor exception: that side's carcass panel has no notch
    and is solid through the kick Y range, so a full-width finish kick
    would intersect it. Inset the cabinet-end X by the side's thickness
    on that side; the corner finish kick part fills the X stretch
    behind the stile separately.
    """
    if not has_finish_kick(layout):
        return []
    segments = []
    last_bay = layout.bay_count - 1
    finish_t = layout.finish_kick_thickness
    for start, end in _compute_segments(layout, _kick_subfront_passthrough):
        first_bay = layout.bays[start]
        if first_bay.get('remove_bottom') or first_bay.get('remove_carcass'):
            continue
        if first_bay.get('floating_bay'):
            continue
        if start == 0:
            if layout.kick_inset_left > 0:
                # Inset with return: finish kick covers the return's
                # front face, so it starts at the return's outer X.
                left_x = layout.kick_inset_left
            elif left_stile_to_floor(layout):
                left_x = carcass_inner_left_x(layout)
            else:
                left_x = 0.0
        else:
            left_x = _carcass_meeting_x(layout, start - 1)
        if end == last_bay:
            if layout.kick_inset_right > 0:
                right_x = layout.dim_x - layout.kick_inset_right
            elif right_stile_to_floor(layout):
                right_x = carcass_inner_right_x(layout)
            else:
                right_x = layout.dim_x
        else:
            right_x = _carcass_meeting_x(layout, end)
        # Finish kick lives just IN FRONT of the subfront (its back face
        # flush with the subfront's front face), so its perpendicular
        # offset from the FF outer plane is (tks + tkt - finish_t).
        # Like the subfront, it spans world-X between the side panels,
        # so we use the world-X helper and convert to FF-aligned length.
        wx, wy, wz = ff_perpendicular_offset_at_world_x(
            layout, left_x,
            layout.tks + layout.tkt - finish_t,
            0.0,
        )
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          wx,
            'y':          wy,
            'z':          wz,
            'length':     ff_world_x_span_to_length(layout, right_x - left_x),
            'width':      first_bay['kick_height'],
            'thickness':  finish_t,
        })
    return segments


def _end_bay_drops_kick(layout, bay_index):
    """End-bay convenience: True if that bay omits its kick parts via
    remove_bottom, remove_carcass, or floating_bay. Used to suppress
    corner finish kicks and kick returns at a cabinet end whose bay
    has no kick.
    """
    bay = layout.bays[bay_index]
    return bool(bay.get('remove_bottom')
                or bay.get('remove_carcass')
                or bay.get('floating_bay'))


def has_left_corner_finish_kick(layout):
    """Filler at the left corner behind the stile - only when stile-to-
    floor is on for that side AND the user hasn't disabled the finish.
    Suppressed when bay 0 omits its kick parts.
    """
    if _end_bay_drops_kick(layout, 0):
        return False
    return has_finish_kick(layout) and left_stile_to_floor(layout)


def has_right_corner_finish_kick(layout):
    if _end_bay_drops_kick(layout, layout.bay_count - 1):
        return False
    return has_finish_kick(layout) and right_stile_to_floor(layout)


def left_corner_finish_kick_position(layout):
    """Origin at the inside face of the left side panel (carcass_inner_
    left_x already folds in scribe + side_thickness), at the back of
    the stile, on the floor. Starting here keeps the corner kick from
    intersecting the side and from overlapping the main finish kick,
    which begins at the same X.
    """
    return (carcass_inner_left_x(layout),
            -layout.dim_y + layout.fft, 0.0)


def left_corner_finish_kick_dims(layout):
    """Length spans from inside-of-side to inside-of-stile, so it adjusts
    automatically with scribe and side_thickness (both folded into
    carcass_inner_left_x). Width is bay 0's kick height. Thickness fills
    the gap from stile back to main finish kick front.
    """
    length = layout.lsw - carcass_inner_left_x(layout)
    width = layout.bays[0]['kick_height']
    thickness = (layout.tks + layout.tkt
                 - layout.finish_kick_thickness - layout.fft)
    return (length, width, thickness)


def right_corner_finish_kick_position(layout):
    """Origin at the inside face of the right stile (X = dim_x - rsw),
    extending +X toward the side's inner face.
    """
    return (layout.dim_x - layout.rsw,
            -layout.dim_y + layout.fft, 0.0)


def right_corner_finish_kick_dims(layout):
    """Mirror of the left corner: length runs from inside-of-stile to
    inside-of-side. Uses the LAST bay's kick height since this corner
    abuts the rightmost main-finish segment.
    """
    length = carcass_inner_right_x(layout) - (layout.dim_x - layout.rsw)
    width = layout.bays[layout.bay_count - 1]['kick_height']
    thickness = (layout.tks + layout.tkt
                 - layout.finish_kick_thickness - layout.fft)
    return (length, width, thickness)


# ---------------------------------------------------------------------------
# Kick returns - vertical closeout panels at the inset ends
# ---------------------------------------------------------------------------
# When kick_inset_left / right > 0, the side floats up by kick_height
# and the kick is "wrapped" at that end by a return panel running the
# full carcass depth, sitting tkt-thick at the inset X position. The
# main kick subfront butts against the return's inboard face.
# ---------------------------------------------------------------------------
def has_left_kick_return(layout):
    if _end_bay_drops_kick(layout, 0):
        return False
    return (has_kick_subfront(layout)
            and layout.kick_inset_left > 0)


def has_right_kick_return(layout):
    if _end_bay_drops_kick(layout, layout.bay_count - 1):
        return False
    return (has_kick_subfront(layout)
            and layout.kick_inset_right > 0)


def left_kick_return_position(layout):
    """Origin at the cabinet back, X at the inset distance from the
    cabinet outer, on the floor. Length runs -Y toward the front,
    Thickness extends +X toward the cabinet interior.
    """
    return (layout.kick_inset_left, 0.0, 0.0)


def left_kick_return_dims(layout):
    """Length spans from cabinet back to main kick front. Width is bay
    0's kick height. Thickness is the toe kick board thickness.
    """
    length = layout.dim_y - layout.tks - layout.tkt
    width = layout.bays[0]['kick_height']
    thickness = layout.tkt
    return (length, width, thickness)


def right_kick_return_position(layout):
    """Origin at the right end at X = dim_x - kick_inset_right; Thickness
    extends -X toward the cabinet interior (Mirror Z = False on the
    part flips the Thickness direction relative to the left return).
    """
    return (layout.dim_x - layout.kick_inset_right, 0.0, 0.0)


def right_kick_return_dims(layout):
    """Mirror of left_kick_return_dims; uses the LAST bay's kick height."""
    length = layout.dim_y - layout.tks - layout.tkt
    width = layout.bays[layout.bay_count - 1]['kick_height']
    thickness = layout.tkt
    return (length, width, thickness)


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
    - either bay has remove_bottom set (the flagged bay omits its rail)
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
    if bay_a.get('remove_bottom') or bay_b.get('remove_bottom'):
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
        ff_x = bay_x_position(layout, start)
        # Length: sum of bay widths within segment + intermediate mid stile widths
        length = first_bay['width']
        for k in range(start, end):
            length += layout.mid_stiles[k]['width']
            length += layout.bays[k + 1]['width']
        wx, wy, wz = ff_outer_world_pos(
            layout, ff_x, bay_top_z(layout, start)
        )
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          wx,
            'y':          wy,
            'z':          wz,
            'length':     length,
            'width':      first_bay['top_rail_width'],
            'thickness':  layout.fft,
        })
    return segments


def bottom_rail_segments(layout):
    """Compute bottom rail segments. FLUSH extends the rail down to the
    floor and grows its width by kick_height so a single wide rail fills
    the space the recess would otherwise occupy.
    """
    segments = []
    flush = (layout.has_toe_kick and layout.toe_kick_type == 'FLUSH')
    for start, end in _compute_segments(layout, bottom_rail_passthrough):
        first_bay = layout.bays[start]
        # Passthrough breaks at bays with remove_bottom, so any flagged
        # bay arrives here as a (i, i) segment we drop. remove_carcass
        # is intentionally not gated here - the face frame stays.
        if first_bay.get('remove_bottom'):
            continue
        ff_x = bay_x_position(layout, start)
        length = first_bay['width']
        for k in range(start, end):
            length += layout.mid_stiles[k]['width']
            length += layout.bays[k + 1]['width']
        if flush:
            z = 0.0
            width = first_bay['kick_height'] + first_bay['bottom_rail_width']
        else:
            z = bay_bottom_z(layout, start)
            width = first_bay['bottom_rail_width']
        wx, wy, wz = ff_outer_world_pos(layout, ff_x, z)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          wx,
            'y':          wy,
            'z':          wz,
            'length':     length,
            'width':      width,
            'thickness':  layout.fft,
        })
    return segments


# ---------------------------------------------------------------------------
# End stiles (left and right) - always exist
# ---------------------------------------------------------------------------
def left_end_stile_position(layout):
    """Left end stile follows bay 0's vertical extent unless the user
    has asked for a stile-to-floor or FLUSH forces it - in those cases
    the stile drops to Z = 0 and gets longer. Anchored at the LEFT
    endpoint of the FF outer plane (FF-x = 0); in angled mode that
    sits at world (0, -effective_left_depth) instead of (0, -dim_y).
    """
    bottom_z = 0.0 if left_stile_to_floor(layout) else bay_bottom_z(layout, 0)
    return ff_outer_world_pos(layout, 0.0, bottom_z)


def left_end_stile_dims(layout):
    bottom_z = 0.0 if left_stile_to_floor(layout) else bay_bottom_z(layout, 0)
    top_z = bay_top_z(layout, 0)
    return (top_z - bottom_z, layout.lsw, layout.fft)


def right_end_stile_position(layout):
    """Right end stile follows the LAST bay's vertical extent unless the
    user has asked for a stile-to-floor or FLUSH forces it. Anchored
    at the RIGHT endpoint of the FF outer plane (FF-x = ff_length);
    in angled mode that sits at world (dim_x, -effective_right_depth).
    """
    last = layout.bay_count - 1
    bottom_z = (0.0 if right_stile_to_floor(layout)
                else bay_bottom_z(layout, last))
    return ff_outer_world_pos(layout, face_frame_length(layout), bottom_z)


def right_end_stile_dims(layout):
    last = layout.bay_count - 1
    bottom_z = (0.0 if right_stile_to_floor(layout)
                else bay_bottom_z(layout, last))
    top_z = bay_top_z(layout, last)
    return (top_z - bottom_z, layout.rsw, layout.fft)


# ---------------------------------------------------------------------------
# Carcass side panels - extend with first/last bay's vertical range
# ---------------------------------------------------------------------------
def effective_left_depth(layout):
    """Left side's front-to-back length budget. In angled mode the
    unlocked side reads cab.left_depth; otherwise it falls back to the
    first bay's depth (which equals dim_y on single-bay carcasses)."""
    if layout.is_angled and layout.unlock_left_depth:
        return layout.cab_left_depth
    return layout.bays[0]['depth']


def effective_right_depth(layout):
    """Mirror of effective_left_depth for the right side."""
    if layout.is_angled and layout.unlock_right_depth:
        return layout.cab_right_depth
    last = layout.bay_count - 1
    return layout.bays[last]['depth']


def face_frame_angle(layout):
    """Z rotation (radians) that maps the original square face frame
    direction (+X) to the angled FF plane's direction, going from the
    left endpoint to the right endpoint of the FF inner plane.

    Negative when the left side is shallower than the right: the right
    endpoint sits at more-negative Y, so rotating +X clockwise (negative
    Z in right-handed coords) is needed to align with the FF line.
    Returns 0.0 when not angled.

    Used directly as rotation_euler.z on FF parts that lie in the FF
    plane (stiles, rails, kick subfront, opening front pivots) and on
    the angled cutter.
    """
    if not layout.is_angled:
        return 0.0
    dy = effective_left_depth(layout) - effective_right_depth(layout)
    return math.atan2(dy, layout.dim_x)


def face_frame_length(layout):
    """Length of the face frame plane along its own X axis. In the
    square case the FF plane shrinks by any active blind offsets so
    end stiles, rails, and bays all fit within the non-blind portion
    of the cabinet width. The angled case keeps the hypotenuse math
    untouched - blind plus angled isn't supported yet.
    """
    if not layout.is_angled:
        return (layout.dim_x
                - layout.blind_offset_left
                - layout.blind_offset_right)
    dy = effective_right_depth(layout) - effective_left_depth(layout)
    return math.hypot(layout.dim_x, dy)


def ff_outer_world_pos(layout, ff_x, world_z):
    """World (x, y, z) on the FF outer plane at FF-distance ff_x from
    the left endpoint of the (potentially shrunken) face frame, at
    height world_z.

    For non-angled cabinets ff_x maps to world X via the blind offset:
    the FF plane's left endpoint sits at world x = blind_offset_left,
    so the function returns (ff_x + blind_offset_left, -dim_y, z).
    Callers pass FF-local coordinates from bay_x_position /
    face_frame_length so the offset is added once at the world
    boundary.

    For angled cabinets the FF outer plane is rotated around Z by
    face_frame_angle, with its left endpoint at (0, -effective_left_
    depth) and its right endpoint at (dim_x, -effective_right_depth).
    Blind+angled isn't supported, so the angled branch ignores the
    blind offsets.
    """
    if not layout.is_angled:
        return (ff_x + layout.blind_offset_left, -layout.dim_y, world_z)
    theta = face_frame_angle(layout)
    return (
        ff_x * math.cos(theta),
        -effective_left_depth(layout) + ff_x * math.sin(theta),
        world_z,
    )


def ff_inner_world_pos(layout, ff_x, world_z):
    """World (x, y, z) on the FF inner plane (the back face of the
    face frame, where carcass tops / bottoms / sides butt) at FF-
    distance ff_x from the left endpoint, at height world_z.

    Equivalent to ff_outer_world_pos shifted by fft in the
    perpendicular-into-cabinet direction.
    """
    return ff_perpendicular_offset(layout, ff_x, layout.fft, world_z)


def ff_perpendicular_offset(layout, ff_x, perp_offset, world_z):
    """World (x, y, z) on a FF-parallel plane shifted inward from the
    FF outer plane by perp_offset along the perpendicular-into-cabinet
    direction, parameterized by FF-distance ff_x from the left FF
    endpoint. For parts whose endpoints are already in FF coordinates
    (rails, stiles).
    """
    if not layout.is_angled:
        return (ff_x, -layout.dim_y + perp_offset, world_z)
    theta = face_frame_angle(layout)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return (
        ff_x * cos_t - perp_offset * sin_t,
        -effective_left_depth(layout) + ff_x * sin_t + perp_offset * cos_t,
        world_z,
    )


def ff_perpendicular_offset_at_world_x(layout, world_x, perp_offset, world_z):
    """World (x, y, z) on the same FF-parallel plane as
    ff_perpendicular_offset, but parameterized by WORLD X instead of
    FF-distance. For the toe kick subfront and finish kick whose
    endpoints must align with the side panels' world-X-aligned inner
    faces (so the kick is captured between the sides), not with the
    FF stile inboard edges.
    """
    if not layout.is_angled:
        return (world_x, -layout.dim_y + perp_offset, world_z)
    theta = face_frame_angle(layout)
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    # Kick plane equation: y(x) = -ld + tan*x + perp/cos. Derived from
    # parameterizing the plane by FF-x (y = -ld + ff_x*sin + perp*cos,
    # x = ff_x*cos - perp*sin) and eliminating ff_x.
    return (
        world_x,
        (-effective_left_depth(layout)
         + (sin_t / cos_t) * world_x
         + perp_offset / cos_t),
        world_z,
    )


def ff_world_x_span_to_length(layout, world_x_span):
    """Given a span between two world X coordinates that lie on a FF-
    parallel plane (e.g. the subfront kick stretching between the side
    panels' inner faces), return the length the part should be along
    its own +X axis (which after rotation is FF-aligned). For square
    cabinets this is the same number; for angled it's longer by 1/cos.
    """
    if not layout.is_angled:
        return world_x_span
    return world_x_span / math.cos(face_frame_angle(layout))


def left_side_position(layout):
    """Left carcass side. Two anchoring modes:

      Square (default): side back edge sits at -dim_y + bay 0 depth,
        so a shallower bay shifts BOTH ends forward equally and the
        back panel moves with it.
      Angled (single-bay, unlock on): side back edge anchors at the
        cabinet back (Y = 0). Only the front edge moves, producing
        the asymmetric front geometry that drives the angled face
        frame plane while the back stays put.

    X reflects the scribe offset so the side can sit inboard of the
    stile. Z anchor depends on toe_kick_type via side_bottom_z.
    """
    if layout.is_angled:
        y = 0.0
    else:
        y = -layout.dim_y + layout.bays[0]['depth']
    return (left_scribe_offset(layout), y,
            side_bottom_z(layout, 0, 'LEFT'))


def left_side_dims(layout):
    bottom_z = side_bottom_z(layout, 0, 'LEFT')
    top_z = left_side_top_z(layout)
    return (top_z - bottom_z,
            effective_left_depth(layout) - layout.fft,
            left_side_thickness(layout))


def right_side_position(layout):
    """Mirror of left_side_position. See its docstring for the two
    anchoring modes."""
    if layout.is_angled:
        y = 0.0
    else:
        last = layout.bay_count - 1
        y = -layout.dim_y + layout.bays[last]['depth']
    last = layout.bay_count - 1
    return (layout.dim_x - right_scribe_offset(layout), y,
            side_bottom_z(layout, last, 'RIGHT'))


def right_side_dims(layout):
    last = layout.bay_count - 1
    bottom_z = side_bottom_z(layout, last, 'RIGHT')
    top_z = right_side_top_z(layout)
    return (top_z - bottom_z,
            effective_right_depth(layout) - layout.fft,
            right_side_thickness(layout))


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

    x = (bay_x_position(layout, gap_index)
         + bay_a['width']
         + layout.blind_offset_left)
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
    - either bay has remove_bottom or remove_carcass set
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
    if (bay_a.get('remove_bottom') or bay_b.get('remove_bottom')
            or bay_a.get('remove_carcass') or bay_b.get('remove_carcass')):
        return False
    return True


def _mid_stile_center_x(layout, gap_index):
    """World-X of the mid-stile centerline at this gap. The mid-div
    setup is mirrored about this line: same-depth = single panel
    centered here; diff-depth = two panels meeting face-to-face here.

    bay_x_position returns FF-local; add blind_offset_left so this
    function honors its world-X contract regardless of blind state.
    """
    bay_a = layout.bays[gap_index]
    ms = layout.mid_stiles[gap_index]
    msw = ms['width']
    base_x = (bay_x_position(layout, gap_index)
              + bay_a['width']
              + layout.blind_offset_left)
    return base_x + msw / 2.0


def _mid_div_left_outer_x(layout, gap_index):
    """X of the LEFT-facing outer face of the mid-div setup. For
    matching bay depths this is the single centered panel's left face;
    for differing depths this is panel A's (bay A's right wall) left
    face.
    """
    center = _mid_stile_center_x(layout, gap_index)
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    dt = layout.division_thickness
    if _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return center - dt / 2.0
    return center - dt


def _mid_div_right_outer_x(layout, gap_index):
    """X of the RIGHT-facing outer face of the mid-div setup. Mirror
    of _mid_div_left_outer_x."""
    center = _mid_stile_center_x(layout, gap_index)
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    dt = layout.division_thickness
    if _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return center + dt / 2.0
    return center + dt


def _carcass_meeting_x(layout, gap_index):
    """X coordinate where two adjacent carcass bottom (or back)
    segments meet at gap_index.

    Same-depth gap (one panel): the HIGHER bay's panel abuts the mid div
    at its near face; the LOWER bay's panel passes UNDER the mid div to
    the far face. Both segments meet at that single X.

    Diff-depth gap (two panels): segments cannot pass under since each
    bay has its own wall at its own depth. Both terminate at the
    touching face between panel A and panel B (= mid-stile center).
    """
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return _mid_stile_center_x(layout, gap_index)
    if bay_bottom_z(layout, gap_index) > bay_bottom_z(layout, gap_index + 1):
        return _mid_div_left_outer_x(layout, gap_index)
    return _mid_div_right_outer_x(layout, gap_index)


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
        left_x = _mid_div_right_outer_x(layout, start - 1)
    if end == layout.bay_count - 1:
        right_x = carcass_inner_right_x(layout)
    else:
        right_x = _mid_div_left_outer_x(layout, end)
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
        # Passthrough breaks at bays with remove_bottom or remove_carcass,
        # so any flagged bay arrives here as a (i, i) segment we drop.
        if first_bay.get('remove_bottom') or first_bay.get('remove_carcass'):
            continue
        left_x, right_x = _segment_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.dim_y + first_bay['depth'] - back_thickness(layout),
            'z':          bay_bottom_z(layout, start) + first_bay['bottom_rail_width'] - layout.mt,
            'length':     right_x - left_x,
            'panel_dim_y': first_bay['depth'] - back_thickness(layout) - layout.fft,
            'thickness':  layout.mt,
        })
    return segments


def _carcass_back_passthrough(layout, gap_index):
    """Back panel breaks when bay floors, ceilings, or depths differ,
    when either bay has remove_carcass set, or when either bay has
    remove_bottom set (the flagged bay's back drops to the cabinet
    floor and so can't share a Z origin with its neighbours)."""
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
    if bay_a.get('remove_carcass') or bay_b.get('remove_carcass'):
        return False
    if bay_a.get('remove_bottom') or bay_b.get('remove_bottom'):
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
        # Passthrough breaks at bays with remove_carcass, so flagged bays
        # arrive as (i, i) segments we drop.
        if first_bay.get('remove_carcass'):
            continue
        left_x, right_x = _segment_x_bounds(layout, start, end)
        if first_bay.get('remove_bottom'):
            # No bottom panel here, so the back wraps the missing
            # bottom and toe-kick area by dropping to the cabinet floor.
            z_origin = 0.0
        else:
            z_origin = bay_bottom_z(layout, start) + first_bay['bottom_rail_width'] - layout.mt
        # Cabinet-level override: raise the back's bottom edge above
        # the default origin (refrigerator cabinet, etc.). Honored
        # only when it raises the panel - never lowers it.
        if layout.back_bottom_inset > z_origin:
            z_origin = layout.back_bottom_inset
        # Per-bay back: segments break at depth changes (passthrough returns
        # False), so each segment's bays share a single depth -> use start
        # bay's depth to position the back at this bay group's back edge.
        back_y = -layout.dim_y + first_bay['depth']
        segments.append({
            'start_bay':       start,
            'end_bay':         end,
            'x':               left_x,
            'y':               back_y,
            'z':               z_origin,
            'horizontal_length': right_x - left_x,
            'vertical_length':   carcass_top_z(layout, start) - z_origin,
            'thickness':       back_thickness(layout),
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
    - either bay has remove_carcass set
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
    if bay_a.get('remove_carcass') or bay_b.get('remove_carcass'):
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
      - origin y: -dim_y + bay.depth - bt  (front face of this bay's back panel)
      - origin z: carcass_top_z(start)  (= bay_top_z - top_scribe)
      - Length:  segment X span
      - Width:   bay.depth - bt - fft   (back-panel front face to
        face-frame back face; Mirror Y = True so width extends in -Y)
      - Thickness: mt   (Mirror Z = True so panel extends down by mt)
    """
    segments = []
    for start, end in _compute_segments(layout, _top_stretcher_passthrough):
        first_bay = layout.bays[start]
        if first_bay.get('remove_carcass'):
            continue
        left_x, right_x = _stretcher_x_bounds(layout, start, end)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          -layout.dim_y + first_bay['depth'] - back_thickness(layout),
            'z':          carcass_top_z(layout, start),
            'length':     right_x - left_x,
            'panel_dim_y': first_bay['depth'] - back_thickness(layout) - layout.fft,
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
        if layout.bays[start].get('remove_carcass'):
            continue
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
        first_bay = layout.bays[start]
        if first_bay.get('remove_carcass'):
            continue
        left_x, right_x = _stretcher_x_bounds(layout, start, end)
        # Rear stretcher sits just inside the bay's back panel, so its Y
        # tracks the bay's back panel front face: -dim_y + bay_depth - bt.
        # Segment passthrough already breaks on depth change, so all bays
        # in a segment share a depth and the start bay drives Y.
        rear_y = -layout.dim_y + first_bay['depth'] - back_thickness(layout)
        segments.append({
            'start_bay':  start,
            'end_bay':    end,
            'x':          left_x,
            'y':          rear_y,
            'z':          carcass_top_z(layout, start),
            'length':     right_x - left_x,
            'width':      layout.stretcher_w,
            'thickness':  layout.stretcher_t,
        })
    return segments


# ---------------------------------------------------------------------------
# Mid division - the carcass partition behind each mid stile
# ---------------------------------------------------------------------------
def mid_division_notch_active(layout, gap_index):
    """Whether the slot-0 mid-div panel at this gap needs stretcher
    notches at its top-front and top-back corners. Only the same-depth
    single panel ever gets notches: differing depths produce two panels
    each ending under its own bay's stretcher segment, so nothing
    crosses the panel.

    True iff:
      - cabinet uses stretchers (Base / LapDrawer), and
      - bay depths match (single panel at this gap), and
      - the stretcher segment actually passes through this gap
        (matching heights, depths, rail widths)
    """
    if not layout.uses_stretchers:
        return False
    if gap_index >= len(layout.mid_stiles):
        return False
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    if not _epsilon_eq(bay_a['depth'], bay_b['depth']):
        return False
    return _top_stretcher_passthrough(layout, gap_index)


def mid_division_panels(layout, gap_index):
    """Per-gap mid-division panel data.

    Returns a list of one or two panel dicts. Bay depths matching ->
    a single panel centered on the mid-stile. Bay depths differing ->
    two panels face-to-face at the mid-stile center, each sized to
    its own bay's depth.

    Each dict has:
      slot      - 0 (always present) or 1 (only when depths differ)
      bay_side  - 'CENTER', 'A' (bay_a's right wall), 'B' (bay_b's left wall)
      x, y, z   - origin position
      length    - vertical extent (top_z - bottom_z)
      width     - depth into cabinet (front-to-back), per its bay
      thickness - panel thickness (= layout.mt)
    """
    if gap_index >= len(layout.mid_stiles):
        return []
    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    ms = layout.mid_stiles[gap_index]

    center_x = _mid_stile_center_x(layout, gap_index)
    dt = layout.division_thickness
    # When adjacent bay tops differ (top_offset change at this gap),
    # the partition extends an extra mt past the carcass top so it
    # sits flush with the top panel's top face instead of stopping at
    # its underside. Mirrors how the partition skin reaches the top
    # face of the shallower bay's top panel.
    tops_differ = not _epsilon_eq(
        bay_top_z(layout, gap_index),
        bay_top_z(layout, gap_index + 1),
    )

    def _panel_y(depth):
        # Mirror Y=True extends width in -Y; origin sits at the panel's
        # back face (= front face of carcass back panel). Width spans
        # forward to the face frame's back face.
        return -layout.dim_y + depth - back_thickness(layout)

    def _panel_width(depth):
        return depth - back_thickness(layout) - layout.fft

    def _bay_z_range(bay_idx):
        """Bottom and top Z of a single-bay mid-div panel: from this
        bay's bottom rail top to this bay's carcass top (with the
        construction-style adjustment + per-mid-stile extend amounts).

        remove_bottom on this bay drops the brw term so the panel's
        bottom matches the mid-stile's bottom (which itself drops by
        brw via bottom_rail_passthrough returning False)."""
        bay = layout.bays[bay_idx]
        brw_term = 0.0 if bay.get('remove_bottom') else bay['bottom_rail_width']
        bottom_z = (bay_bottom_z(layout, bay_idx)
                    + brw_term
                    - ms['extend_down_amount'])
        top = carcass_top_z(layout, bay_idx)
        # Stretchers: division flush with stretcher tops for structural
        # attachment. Solid top: division stops mt below carcass top to
        # butt against the underside of the top panel.
        if layout.uses_stretchers or tops_differ:
            top_z = top + ms['extend_up_amount']
        else:
            top_z = top - layout.mt + ms['extend_up_amount']
        return bottom_z, top_z

    if _epsilon_eq(bay_a['depth'], bay_b['depth']):
        # One shared panel. Spans the union of the two bays' vertical
        # ranges - bottom = lower bay's floor (rail top), top = higher
        # carcass top - so the single wall covers both bays whatever
        # their heights.
        if bay_bottom_z(layout, gap_index) <= bay_bottom_z(layout, gap_index + 1):
            lower_idx = gap_index
        else:
            lower_idx = gap_index + 1
        # If either adjacent bay has remove_bottom, the mid-stile drops
        # by brw (rail-passthrough returns False); the shared division
        # panel follows so its bottom aligns with the mid-stile.
        either_remove_bottom = (bay_a.get('remove_bottom')
                                or bay_b.get('remove_bottom'))
        if either_remove_bottom:
            lower_brw = 0.0
        else:
            lower_brw = layout.bays[lower_idx]['bottom_rail_width']
        bottom_z = (bay_bottom_z(layout, lower_idx) + lower_brw
                    - ms['extend_down_amount'])
        higher_top_z = max(carcass_top_z(layout, gap_index),
                           carcass_top_z(layout, gap_index + 1))
        if layout.uses_stretchers or tops_differ:
            top_z = higher_top_z + ms['extend_up_amount']
        else:
            top_z = higher_top_z - layout.mt + ms['extend_up_amount']
        # Mirror Z=True extends in +X from origin, so origin x = panel's
        # left face = center - dt/2.
        return [{
            'slot':      0,
            'bay_side':  'CENTER',
            'x':         center_x - dt / 2.0,
            'y':         _panel_y(bay_a['depth']),
            'z':         bottom_z,
            'length':    top_z - bottom_z,
            'width':     _panel_width(bay_a['depth']),
            'thickness': dt,
            # Stretcher notches at top-front + top-back of the panel.
            # Active when stretchers actually cross this gap; sized to
            # the stretcher's own width and thickness for a flush fit.
            'notch_active':       mid_division_notch_active(layout, gap_index),
            'notch_x':            layout.stretcher_t,
            'notch_y':            layout.stretcher_w,
            'notch_route_depth':  dt,
        }]

    # Two panels, face-to-face at center_x. Each is its own bay's
    # interior wall - sized to its own bay's depth AND height. Panel A
    # is bay A's right wall (left face at center_x - dt, right face at
    # center_x). Panel B is bay B's left wall (left face at center_x,
    # right face at center_x + dt).
    a_bottom_z, a_top_z = _bay_z_range(gap_index)
    b_bottom_z, b_top_z = _bay_z_range(gap_index + 1)
    return [
        {
            'slot':      0,
            'bay_side':  'A',
            'x':         center_x - dt,
            'y':         _panel_y(bay_a['depth']),
            'z':         a_bottom_z,
            'length':    a_top_z - a_bottom_z,
            'width':     _panel_width(bay_a['depth']),
            'thickness': dt,
            # Diff-depth: each bay's stretcher segment terminates at its
            # own panel face, so nothing crosses - notches never apply.
            'notch_active':       False,
            'notch_x':            layout.stretcher_t,
            'notch_y':            layout.stretcher_w,
            'notch_route_depth':  dt,
        },
        {
            'slot':      1,
            'bay_side':  'B',
            'x':         center_x,
            'y':         _panel_y(bay_b['depth']),
            'z':         b_bottom_z,
            'length':    b_top_z - b_bottom_z,
            'width':     _panel_width(bay_b['depth']),
            'thickness': dt,
            'notch_active':       False,
            'notch_x':            layout.stretcher_t,
            'notch_y':            layout.stretcher_w,
            'notch_route_depth':  dt,
        },
    ]


# ---------------------------------------------------------------------------
# Partition skin - filler at the bottom of the mid-division covering the
# mid-stile back-face overhang on the shallower bay's side when adjacent
# bays have different floors.
# ---------------------------------------------------------------------------
def partition_skin_panels(layout, gap_index):
    """Per-gap partition skins. Returns 0, 1, or 2 panel dicts.

    A skin is a filler attached to the partition on the shallower
    bay's side, covering the mid-stile back-face overhang where one
    bay's interior doesn't extend as far as the other's. Up to two
    skins emit per gap:

      slot 0 - bottom step: floors differ. Skin fills the X overhang
        in Z range from the deeper bay's floor up to the shallower
        bay's bottom panel underside (= floor + brw - mt).

      slot 1 - top step: tops differ. Only meaningful for cabinets
        with a solid top panel (Upper / Tall). Skin fills the X
        overhang in Z range from the shallower bay's top panel top
        face (= bay_top_z - top_scribe) up to the deeper bay's top.

    Same-depth gap thickness is (msw - dt) / 2; diff-depth (two-panel
    partition meeting face-to-face at center) is msw / 2 - dt. Y wraps
    the back panel so origin sits at the bay's back-panel back face
    and width spans forward to the face frame's back face.
    """
    skins = []
    if gap_index >= len(layout.mid_stiles):
        return skins

    bay_a = layout.bays[gap_index]
    bay_b = layout.bays[gap_index + 1]
    msw = layout.mid_stiles[gap_index]['width']
    dt = layout.division_thickness
    same_depth = _epsilon_eq(bay_a['depth'], bay_b['depth'])
    if same_depth:
        thickness = (msw - dt) / 2.0
    else:
        thickness = msw / 2.0 - dt
    if thickness <= 0.0:
        return skins

    center_x = _mid_stile_center_x(layout, gap_index)

    def _x_origin(side):
        if side == 'LEFT':
            return center_x - msw / 2.0
        return center_x + (dt / 2.0 if same_depth else dt)

    def _y_and_width(skin_bay):
        d = skin_bay['depth']
        return (-layout.dim_y + d, d - layout.fft)

    # ----- Slot 0: bottom step -----
    floor_a = bay_bottom_z(layout, gap_index)
    floor_b = bay_bottom_z(layout, gap_index + 1)
    if not _epsilon_eq(floor_a, floor_b):
        if floor_a > floor_b:
            side = 'LEFT'
            skin_bay_idx = gap_index
            bottom_z, top_z = floor_b, floor_a
        else:
            side = 'RIGHT'
            skin_bay_idx = gap_index + 1
            bottom_z, top_z = floor_a, floor_b
        skin_bay = layout.bays[skin_bay_idx]
        top_z += skin_bay['bottom_rail_width'] - layout.mt
        y, width = _y_and_width(skin_bay)
        skins.append({
            'slot':      0,
            'side':      side,
            'x':         _x_origin(side),
            'y':         y,
            'z':         bottom_z,
            'length':    top_z - bottom_z,
            'width':     width,
            'thickness': thickness,
        })

    # ----- Slot 1: top step (Upper / Tall only - solid top panel) -----
    if layout.cabinet_type in {'UPPER', 'TALL'}:
        top_a = bay_top_z(layout, gap_index)
        top_b = bay_top_z(layout, gap_index + 1)
        if not _epsilon_eq(top_a, top_b):
            # Bay with the LOWER top is the shallower-at-top one.
            if top_a < top_b:
                side = 'LEFT'
                skin_bay_idx = gap_index
                lower_top, upper_top = top_a, top_b
            else:
                side = 'RIGHT'
                skin_bay_idx = gap_index + 1
                lower_top, upper_top = top_b, top_a
            skin_bay = layout.bays[skin_bay_idx]
            bottom_z = lower_top - layout.top_scribe
            top_z = upper_top
            y, width = _y_and_width(skin_bay)
            skins.append({
                'slot':      1,
                'side':      side,
                'x':         _x_origin(side),
                'y':         y,
                'z':         bottom_z,
                'length':    top_z - bottom_z,
                'width':     width,
                'thickness': thickness,
            })

    return skins


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
        left_x = _mid_div_right_outer_x(layout, bay_index - 1)
    if bay_index == layout.bay_count - 1:
        right_x = carcass_inner_right_x(layout)
    else:
        right_x = _mid_div_left_outer_x(layout, bay_index)
    return left_x, right_x


def bay_cage_position(layout, bay_index):
    """Origin of the bay cage in cabinet-local space.

    Cabinet mode: back-left-bottom corner of the carcass column for
    this bay - top of bottom panel, back face of face frame, inner
    face of left side / mid division.

    Panel mode: back-left-bottom corner of the face frame opening for
    this bay. X = bay's left FF edge. Y = back face of panel. Z = top
    of bottom rail.
    """
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'PANEL':
        x = bay_x_position(layout, bay_index)
        y = -layout.dim_y
        z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']
        return (x, y, z)

    left_x, _ = _cage_x_bounds(layout, bay_index)
    z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']
    # In angled mode the cage rotates around Z by face_frame_angle so
    # bay-local +X aligns with the FF direction. The anchor sits at
    # FF-distance left_x from the left endpoint on the FF inner plane;
    # opening cages stay at bay-local Y=0 and inherit the rotation, so
    # they land on the FF inner plane in world. ff_inner_world_pos
    # collapses to (left_x, -dim_y + fft, z) when not angled.
    return ff_inner_world_pos(layout, left_x, z)


def bay_cage_dims(layout, bay_index):
    """Dim X (width), Dim Y (depth back-to-front), Dim Z (height).

    Cabinet mode: cage spans the full carcass column behind the face
    frame for this bay - interior cavity, wider than the face frame
    opening on every axis to capture overlay door/drawer extents.

    Panel mode (cabinet_type == 'PANEL'): cage exactly matches the
    face frame opening rectangle. No carcass behind the frame, so no
    interior cavity to enclose. Y collapses to the panel's own depth.

    - X: between cabinet sides / adjacent mid divisions (cabinet) or
      between this bay's stiles (panel)
    - Y: bay depth minus fft minus bt (cabinet) or full panel depth
      (panel)
    - Z: top of bottom panel to underside of top construction
      (cabinet) or face frame opening height (panel)
    """
    bay = layout.bays[bay_index]
    if layout.cabinet_type == 'PANEL':
        ff_opening_height = (
            bay['height'] - bay['top_rail_width'] - bay['bottom_rail_width']
        )
        return (bay['width'], layout.dim_y, ff_opening_height)

    left_x, right_x = _cage_x_bounds(layout, bay_index)
    cage_dim_x = right_x - left_x
    cage_dim_y = bay['depth'] - layout.fft - back_thickness(layout)
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

    Panel mode: cage already matches the face frame opening, so all
    perimeter reveals are zero.
    """
    if layout.cabinet_type == 'PANEL':
        return {'top': 0.0, 'bottom': 0.0, 'left': 0.0, 'right': 0.0}

    bay = layout.bays[bay_index]
    cage_left_x, cage_right_x = _cage_x_bounds(layout, bay_index)
    # Cage bounds are world; bay_x_position is FF-local. Convert to
    # world so the reveal subtractions don't mix coordinate systems.
    ff_opening_left_x = (bay_x_position(layout, bay_index)
                         + layout.blind_offset_left)
    ff_opening_right_x = ff_opening_left_x + bay['width']

    _, _, cage_dim_z = bay_cage_dims(layout, bay_index)
    # bay.height now spans floor to top of top rail, so subtracting just
    # the rails leaves both the FF opening AND the kick recess. Subtract
    # kick_height too so the result is the FF opening only. Uppers carry
    # kick_height = 0 so this is a no-op there.
    ff_opening_height = (
        bay['height']
        - bay['top_rail_width']
        - bay['bottom_rail_width']
        - bay['kick_height']
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


def _emit_h_splitter(node, cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z,
                     reveals, splitter_top_z, splitter_bottom_z,
                     splitter_index, layout, splitters, backings):
    """Append the mid rail rect for an H-split between two consecutive
    children, plus the matching backing rect if backing_kind isn't
    NONE. All coords are BAY-local."""
    ff_left_x = cage_x + reveals['left']
    ff_width = cage_dim_x - reveals['left'] - reveals['right']
    splitter_w = node['splitter_width']
    # Cabinet: bay cage origin sits at the back of the face frame, so a
    # mid splitter (a face-frame member) lives one fft in -Y from the
    # origin to land in the FF plane. Panel: bay cage origin sits at
    # the panel's front face and the cage spans the full panel depth,
    # so the splitter sits at bay-local y=0 to land flush with the
    # panel's front face.
    splitter_y = _ff_front_y_bay_local(layout)
    splitters.append({
        'role':            'BAY_MID_RAIL',
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'x':               ff_left_x,
        'y':               splitter_y,
        'z':               splitter_bottom_z,
        'length':          ff_width,
        'splitter_width':  splitter_w,
        'thickness':       layout.fft,
    })
    if not node.get('add_backing', False):
        return
    role = _AXIS_TO_BACKING_ROLE['H']
    bt_thickness = _backing_thickness_for_role(layout, role)
    # cage_dim_y comes in as a parameter (bay-uniform); was previously
    # recomputed from layout.dim_y, which broke for varying bay depths.
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


def _emit_v_splitter(node, cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z,
                     reveals, splitter_left_x, splitter_index, layout,
                     splitters, backings):
    """Append the mid stile rect for a V-split between two consecutive
    children, plus the matching backing rect if backing_kind isn't
    NONE. All coords are BAY-local."""
    ff_bottom_z = cage_z + reveals['bottom']
    ff_height = cage_dim_z - reveals['top'] - reveals['bottom']
    splitter_w = node['splitter_width']
    # See _emit_h_splitter for the cabinet vs panel y rationale.
    splitter_y = _ff_front_y_bay_local(layout)
    splitters.append({
        'role':            'BAY_MID_STILE',
        'split_node_name': node['obj_name'],
        'splitter_index':  splitter_index,
        'x':               splitter_left_x,
        'y':               splitter_y,
        'z':               ff_bottom_z,
        'length':          ff_height,
        'splitter_width':  splitter_w,
        'thickness':       layout.fft,
    })
    if not node.get('add_backing', False):
        return
    role = _AXIS_TO_BACKING_ROLE['V']
    bt_thickness = _backing_thickness_for_role(layout, role)
    # cage_dim_y comes in as a parameter (bay-uniform); was previously
    # recomputed from layout.dim_y, which broke for varying bay depths.
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
               cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z,
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
            # cage_dim_y is bay-uniform; threaded down from bay_openings
            # so interior items size to the bay's depth, not the
            # cabinet's overall dim_y.
            'cage_dim_y':     cage_dim_y,
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
                cage_dim_y=cage_dim_y,
                cage_dim_z=child_cage_dim_z,
                reveals=child_reveals,
                leaves=leaves, splitters=splitters, backings=backings,
            )
            if i < n_children - 1:
                # Mid rail sits below this child's FF bottom edge.
                splitter_top_z = child_ff_bottom_z
                splitter_bottom_z = splitter_top_z - splitter_w
                _emit_h_splitter(
                    node, cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z,
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
                cage_dim_y=cage_dim_y,
                cage_dim_z=cage_dim_z,
                reveals=child_reveals,
                leaves=leaves, splitters=splitters, backings=backings,
            )
            if i < n_children - 1:
                splitter_left_x = child_ff_right_x
                _emit_v_splitter(
                    node, cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z,
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
    cage_dim_x_, cage_dim_y_, cage_dim_z_ = bay_cage_dims(layout, bay_index)
    leaves, splitters, backings = [], [], []
    _walk_tree(
        tree, layout, bay_index,
        cage_x=0.0, cage_z=0.0,
        cage_dim_x=cage_dim_x_, cage_dim_y=cage_dim_y_, cage_dim_z=cage_dim_z_,
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


def _ff_front_y_bay_local(layout):
    """Bay-local Y of the face frame's front (outer) face.

    Cabinet mode: bay cage origin sits at the BACK of the face frame,
    so the front face is one fft in -Y. Panel mode: cage origin sits
    at the panel's front face (which is the FF front), so it's 0.
    Used by every front leaf and splitter to anchor against the FF
    plane regardless of cabinet vs panel context.
    """
    return 0.0 if layout.cabinet_type == 'PANEL' else -layout.fft


def _ff_back_y_bay_local(layout):
    """Bay-local Y of the face frame's back (inner) face.

    Cabinet mode: 0 (bay cage origin = FF back). Panel mode: layout.dim_y
    (cage spans panel front -> back).
    """
    return layout.dim_y if layout.cabinet_type == 'PANEL' else 0.0


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


def _drawer_max_slide(layout, rect):
    """Maximum forward translation for a drawer/pullout front. Aimed at
    "near full extension": bay depth minus face frame thickness minus
    1 inch of clearance. Sourced from the leaf rect's cage_dim_y so the
    slide tracks per-bay depth, not the cabinet's overall dim_y.
    """
    # cage_dim_y = bay_depth - fft - bt; bay_depth - fft = cage_dim_y + bt.
    return max(0.0, rect['cage_dim_y'] + back_thickness(layout) - inch(1.0))


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
    'INSET_PANEL':  ('INSET_PANEL',   'Inset Panel'),
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
    base_y = _ff_front_y_bay_local(layout) - DOOR_TO_FRAME_GAP - door_thickness
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
    base_y = _ff_front_y_bay_local(layout) - DOOR_TO_FRAME_GAP - door_thickness
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
    base_y = _ff_front_y_bay_local(layout) - DOOR_TO_FRAME_GAP - door_thickness
    base_z = rect['reveal_bottom'] - bottom_overlay
    slide = opening_props.swing_percent * _drawer_max_slide(layout, rect)

    return {
        'role': role, 'name': name,
        'pivot_position': (base_x, base_y - slide, base_z),
        # Swing-zero pivot corner. The drawer box anchors against this so it
        # can be placed once in pivot-local space and ride the slide via the
        # pivot's animated Y - if it anchored to pivot_position instead, the
        # box would sit at a fixed world Y and stay behind while the front
        # slides out.
        'pivot_anchor_position': (base_x, base_y, base_z),
        'pivot_rotation': (0.0, 0.0, 0.0),
        'part_position':  (0.0, 0.0, 0.0),
        'part_dims':      (height, width, door_thickness),
    }


def _inset_panel_leaf(layout, rect, role, name):
    """Single-leaf inset panel that fills the face frame opening.
    Sits IN the opening (not in front of it like an overlay door),
    with its back face flush with the back of the face frame plane.
    Thickness fixed at 1/4".

    The pivot is the part's front face; the part extends +Y by
    thickness from there. To place the back face on the FF back plane:
    pivot_y = ff_back_y_bay_local - thickness. In bay-local Y the FF
    back is at 0 for cabinets (cage origin = back of FF) and at
    layout.dim_y for panels (cage spans panel front -> back).
    """
    panel_thickness = inch(0.25)
    width = (
        rect['cage_dim_x'] - rect['reveal_left'] - rect['reveal_right']
    )
    height = (
        rect['cage_dim_z'] - rect['reveal_top'] - rect['reveal_bottom']
    )
    base_x = rect['reveal_left']
    base_y = _ff_back_y_bay_local(layout) - panel_thickness
    base_z = rect['reveal_bottom']
    return {
        'role': role,
        'name': name,
        'pivot_position': (base_x, base_y, base_z),
        'pivot_rotation': (0.0, 0.0, 0.0),
        'part_position':  (0.0, 0.0, 0.0),
        'part_dims':      (height, width, panel_thickness),
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

    if front_type == 'INSET_PANEL':
        return [_inset_panel_leaf(layout, rect, role, base_name)]

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
    # Per-bay depth - threaded onto each leaf rect by bay_openings.
    # Used to be computed here from layout.dim_y, which broke when bay
    # depths diverged from the cabinet's overall depth.
    cage_dim_y = rect['cage_dim_y']
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


# ---------------------------------------------------------------------------
# Modify-cabinet support: world-space FF basis + boundary enumeration
# ---------------------------------------------------------------------------
# These helpers exist for the modify_cabinet modal operator. They convert
# between the FF-local (ff_x, ff_z) coordinate system used by every other
# solver function and Blender world space, accounting for the cabinet's
# location, Z rotation, and (for angled cabinets) face_frame_angle.

def face_frame_world_basis(cabinet_obj, layout):
    """Return (origin_w, x_axis_w, z_axis_w, normal_w) for the cabinet's
    FF outer plane, all in world space.

    - origin_w: world position of (ff_x=0, ff_z=0). This is the FF outer
      face's left endpoint at floor level.
    - x_axis_w: unit vector along the FF, in the direction of increasing
      ff_x (left endpoint to right endpoint).
    - z_axis_w: world +Z (cabinets stand vertical; FF is always plumb).
    - normal_w: unit vector pointing outward (away from the cabinet
      interior, into the room).

    Used by the modify-cabinet operator both to project mouse rays onto
    the FF plane and to project FF-local boundary positions back to
    screen space for GPU drawing.
    """
    from mathutils import Vector
    # ff_outer_world_pos returns cabinet-local coords. Two endpoints
    # define the FF line: ff_x=0 (left) and ff_x=face_frame_length (right),
    # both at world_z=0. Transform through the cabinet's matrix_world to
    # get world-space anchors.
    ff_len = face_frame_length(layout)
    p_left_local = Vector(ff_outer_world_pos(layout, 0.0, 0.0))
    p_right_local = Vector(ff_outer_world_pos(layout, ff_len, 0.0))
    mw = cabinet_obj.matrix_world
    origin_w = mw @ p_left_local
    p_right_w = mw @ p_right_local
    x_axis_w = (p_right_w - origin_w)
    if x_axis_w.length < 1e-8:
        x_axis_w = Vector((1.0, 0.0, 0.0))
    else:
        x_axis_w.normalize()
    z_axis_w = Vector((0.0, 0.0, 1.0))
    # Outward normal: cross of x_axis and z_axis, pointing away from
    # cabinet interior. The FF inner plane sits at +Y in cabinet-local
    # (carcass side); outer plane is at -Y. So outward in cabinet-local
    # is -Y, which under matrix_world rotation becomes -mw.col[1].xyz.
    # Easier: take the cross of x_axis_w and z_axis_w, then flip if it
    # points the wrong way (toward cabinet interior).
    normal_w = x_axis_w.cross(z_axis_w)
    if normal_w.length < 1e-8:
        normal_w = Vector((0.0, -1.0, 0.0))
    else:
        normal_w.normalize()
    # Test orientation: the cabinet's local +Y points into the carcass
    # interior. Outward should be opposite. mw.col[1].xyz is local +Y in
    # world space; if normal_w dots positive with it, flip.
    local_y_in_world = Vector((mw[0][1], mw[1][1], mw[2][1]))
    if normal_w.dot(local_y_in_world) > 0.0:
        normal_w = -normal_w
    return origin_w, x_axis_w, z_axis_w, normal_w


def ff_local_to_world(cabinet_obj, layout, ff_x, ff_z):
    """Map (ff_x, ff_z) on the FF outer plane to a world-space Vector.

    Wraps face_frame_world_basis for callers that just want a point.
    """
    origin_w, x_axis_w, z_axis_w, _normal_w = face_frame_world_basis(
        cabinet_obj, layout)
    return origin_w + x_axis_w * ff_x + z_axis_w * ff_z


def mouse_to_ff_local(cabinet_obj, layout, region, rv3d, mouse_xy):
    """Project a mouse position onto the cabinet's FF outer plane and
    return (ff_x, ff_z) plus the world-space hit point.

    Returns (ff_x, ff_z, world_hit) on success, None on failure (parallel
    ray, projection failed, or behind viewer).

    ff_x is along the FF (0 at left endpoint, face_frame_length at right);
    ff_z is vertical (matches world Z relative to cabinet's floor).
    """
    from bpy_extras import view3d_utils
    from mathutils import Vector
    from mathutils.geometry import intersect_line_plane
    if region is None or rv3d is None:
        return None
    co2d = (mouse_xy[0], mouse_xy[1])
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d)
    ray_dir = view3d_utils.region_2d_to_vector_3d(region, rv3d, co2d)
    if ray_origin is None or ray_dir is None:
        return None
    origin_w, x_axis_w, z_axis_w, normal_w = face_frame_world_basis(
        cabinet_obj, layout)
    hit = intersect_line_plane(
        ray_origin, ray_origin + ray_dir, origin_w, normal_w,
    )
    if hit is None:
        return None
    rel = hit - origin_w
    ff_x = rel.dot(x_axis_w)
    ff_z = rel.dot(z_axis_w)
    return (ff_x, ff_z, hit)


def bay_edge_ff_x(layout, edge_index):
    """FF-local X of the centerline of the mid-stile separating bays
    edge_index and edge_index+1.

    Valid edge_index range: 0 .. bay_count - 2. The drag handle for
    resizing two adjacent bays sits on this centerline.
    """
    if edge_index < 0 or edge_index >= layout.bay_count - 1:
        raise IndexError(f"bay edge {edge_index} out of range")
    x = layout.lsw
    for i in range(edge_index):
        x += layout.bays[i]['width']
        x += layout.mid_stiles[i]['width']
    x += layout.bays[edge_index]['width']
    x += layout.mid_stiles[edge_index]['width'] * 0.5
    return x


def editable_boundaries_v1(cabinet_obj, layout):
    """Yield boundary records for the modify-cabinet operator.

    Three kinds, all carrying axis = 'X' or 'Z' so the operator can
    branch on drag direction without re-inspecting kind:
      BAY_EDGE   - axis 'X', vertical line, drag horizontal,
                   commits via Face_Frame_Bay_Props.width
      MID_STILE  - axis 'X', vertical line, drag horizontal,
                   commits via the two child nodes' size + unlock_size
      MID_RAIL   - axis 'Z', horizontal line, drag vertical,
                   commits via the two child nodes' size + unlock_size
    """
    from . import types_face_frame
    bay_objs = sorted(
        [c for c in cabinet_obj.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    # BAY_EDGE pass
    if layout.bay_count >= 2:
        for i in range(layout.bay_count - 1):
            ff_x = bay_edge_ff_x(layout, i)
            zl_left = bay_bottom_z(layout, i)
            zh_left = bay_top_z(layout, i)
            zl_right = bay_bottom_z(layout, i + 1)
            zh_right = bay_top_z(layout, i + 1)
            ff_z_low = min(zl_left, zl_right)
            ff_z_high = max(zh_left, zh_right)
            locked_left = False
            locked_right = False
            if i < len(bay_objs):
                locked_left = bool(bay_objs[i].face_frame_bay.unlock_width)
            if i + 1 < len(bay_objs):
                locked_right = bool(bay_objs[i + 1].face_frame_bay.unlock_width)
            yield {
                'kind': 'BAY_EDGE',
                'axis': 'X',
                'primary_sign': 1.0,
                'cabinet_obj': cabinet_obj,
                'edge_index': i,
                'ff_x': ff_x,
                'ff_z_low': ff_z_low,
                'ff_z_high': ff_z_high,
                'left_bay_idx': i,
                'right_bay_idx': i + 1,
                'locked_left': locked_left,
                'locked_right': locked_right,
            }
    # Per-bay vertical-anchor handles. Top edge and bottom edge of each
    # bay map to different bay properties depending on cabinet type:
    #   base / tall: top -> bay.height            (drag up => grow)
    #                bottom -> bay.kick_height    (drag up => grow)
    #   upper:       top -> bay.top_offset        (drag up => shrink)
    #                bottom -> bay.height         (drag up => shrink)
    # Live in Grab Face Frame; outer cabinet edges live in Grab Cabinet.
    is_upper = (layout.cabinet_type == 'UPPER')
    for bi, bay_obj in enumerate(bay_objs):
        bp = bay_obj.face_frame_bay
        x0 = bay_x_position(layout, bi)
        x1 = x0 + layout.bays[bi]['width']
        z_top = bay_top_z(layout, bi)
        z_bottom = bay_bottom_z(layout, bi)
        if is_upper:
            # Top edge drives top_offset AND height: dragging up shrinks
            # top_offset (bay top rises) while growing height by the
            # same amount (bay bottom stays put). bay_bottom_z =
            # dim_z - top_offset - height; preserving it requires
            # d(top_offset) + d(height) = 0, i.e. compensate_sign is
            # the negative of primary's effect on top_offset.
            yield {
                'kind': 'BAY_HANDLE',
                'axis': 'Z',
                'primary_sign': -1.0,
                'cabinet_obj': cabinet_obj,
                'bay_obj_name': bay_obj.name,
                'attr': 'top_offset',
                'unlock_attr': 'unlock_top_offset',
                # top_offset is signed: positive drops the bay below
                # the cabinet ceiling, negative pushes it above. No
                # lower bound — the user's design intent rules.
                'min_value': float('-inf'),
                'compensate_attr': 'height',
                'compensate_unlock_attr': 'unlock_height',
                'compensate_sign': 1.0,
                'compensate_min_value': inch(2.0),
                'locked': bool(bp.unlock_top_offset),
                'ff_z': z_top,
                'ff_x_low': x0,
                'ff_x_high': x1,
            }
            # Bottom edge drives height (drag up shrinks height).
            # No compensate: dragging the bottom moves only the bottom
            # edge; top stays put because top_offset isn't touched.
            yield {
                'kind': 'BAY_HANDLE',
                'axis': 'Z',
                'primary_sign': -1.0,
                'cabinet_obj': cabinet_obj,
                'bay_obj_name': bay_obj.name,
                'attr': 'height',
                'unlock_attr': 'unlock_height',
                'min_value': inch(2.0),
                'locked': bool(bp.unlock_height),
                'ff_z': z_bottom,
                'ff_x_low': x0,
                'ff_x_high': x1,
            }
        else:
            # Top edge drives height (drag up grows height)
            yield {
                'kind': 'BAY_HANDLE',
                'axis': 'Z',
                'primary_sign': 1.0,
                'cabinet_obj': cabinet_obj,
                'bay_obj_name': bay_obj.name,
                'attr': 'height',
                'unlock_attr': 'unlock_height',
                'locked': bool(bp.unlock_height),
                'ff_z': z_top,
                'ff_x_low': x0,
                'ff_x_high': x1,
            }
            # Kick top drives kick_height (drag up grows kick_height).
            # Only emit when the cabinet has a toe kick at all.
            if layout.has_toe_kick:
                yield {
                    'kind': 'BAY_HANDLE',
                    'axis': 'Z',
                    'primary_sign': 1.0,
                    'cabinet_obj': cabinet_obj,
                    'bay_obj_name': bay_obj.name,
                    'attr': 'kick_height',
                    'unlock_attr': 'unlock_kick_height',
                    'min_value': 0.0,
                    'locked': bool(bp.unlock_kick_height),
                    'ff_z': z_bottom,
                    'ff_x_low': x0,
                    'ff_x_high': x1,
                }
    # MID_STILE / MID_RAIL pass per bay
    for bi in range(layout.bay_count):
        for b in intra_bay_boundaries(cabinet_obj, layout, bi):
            yield b

def intra_bay_boundaries(cabinet_obj, layout, bay_index):
    """Yield MID_STILE and MID_RAIL boundary records for one bay.

    Walks the splitter rects emitted by bay_openings() and converts them
    from bay-local coords to FF-local coords. For non-angled cabinets the
    bay's cage X origin in cabinet-local equals its FF-local X origin, so
    the conversion is an additive offset. Angled cabinets use the same
    relation since bay-local X aligns with the FF direction (see
    bay_cage_position).

    Each yielded record carries enough context for the modify-cabinet
    operator to commit a drag without re-deriving geometry: the parent
    split node's name, the splitter's gap index, and the two adjacent
    children's object names plus current lock state.
    """
    from . import types_face_frame
    bo = bay_openings(layout, bay_index)
    splitters = bo.get('splitters', [])
    if not splitters:
        return
    bay = layout.bays[bay_index]
    cage_left_x, _ = _cage_x_bounds(layout, bay_index)
    cage_bottom_z = bay_bottom_z(layout, bay_index) + bay['bottom_rail_width']

    for s in splitters:
        node_name = s.get('split_node_name')
        node_obj = bpy.data.objects.get(node_name) if node_name else None
        if node_obj is None:
            continue
        # Children of the split node, sorted to match the tree's
        # iteration order so splitter_index lines up with the gap.
        kids = sorted(
            [c for c in node_obj.children
             if c.get(types_face_frame.TAG_OPENING_CAGE)
             or c.get(types_face_frame.TAG_SPLIT_NODE)],
            key=lambda c: c.get('hb_split_child_index', 0),
        )
        gi = s['splitter_index']
        if gi < 0 or gi + 1 >= len(kids):
            continue
        left_kid = kids[gi]
        right_kid = kids[gi + 1]
        locked_left = _kid_unlock_size(left_kid)
        locked_right = _kid_unlock_size(right_kid)
        if s['role'] == 'BAY_MID_STILE':
            # Vertical line on the FF outer plane. Drag axis: FF-X.
            ff_x = cage_left_x + s['x'] + s['splitter_width'] * 0.5
            ff_z_low = cage_bottom_z + s['z']
            ff_z_high = ff_z_low + s['length']
            yield {
                'kind': 'MID_STILE',
                'axis': 'X',
                'primary_sign': 1.0,
                'cabinet_obj': cabinet_obj,
                'bay_index': bay_index,
                'split_node_name': node_name,
                'splitter_index': gi,
                'left_child_name': left_kid.name,
                'right_child_name': right_kid.name,
                'ff_x': ff_x,
                'ff_z_low': ff_z_low,
                'ff_z_high': ff_z_high,
                'locked_left': locked_left,
                'locked_right': locked_right,
            }
        elif s['role'] == 'BAY_MID_RAIL':
            # Horizontal line on the FF outer plane. Drag axis: FF-Z.
            # 'top' / 'bottom' wording mirrors how the user sees them:
            # left_kid (lower hb_split_child_index) sits at the TOP of
            # the rail because _walk_tree allocates H-split children
            # top-down (cur_z_top decreases each iteration).
            ff_z = cage_bottom_z + s['z'] + s['splitter_width'] * 0.5
            ff_x_low = cage_left_x + s['x']
            ff_x_high = ff_x_low + s['length']
            yield {
                'kind': 'MID_RAIL',
                'axis': 'Z',
                'primary_sign': -1.0,
                'cabinet_obj': cabinet_obj,
                'bay_index': bay_index,
                'split_node_name': node_name,
                'splitter_index': gi,
                'top_child_name': left_kid.name,
                'bottom_child_name': right_kid.name,
                'ff_z': ff_z,
                'ff_x_low': ff_x_low,
                'ff_x_high': ff_x_high,
                'locked_top': locked_left,
                'locked_bottom': locked_right,
            }


def _kid_unlock_size(kid_obj):
    """Read unlock_size from a tree-child object (opening leaf or split
    node). Both PropertyGroups expose unlock_size with the same name."""
    if hasattr(kid_obj, 'face_frame_opening') and kid_obj.face_frame_opening is not None:
        try:
            return bool(kid_obj.face_frame_opening.unlock_size)
        except AttributeError:
            pass
    if hasattr(kid_obj, 'face_frame_split') and kid_obj.face_frame_split is not None:
        try:
            return bool(kid_obj.face_frame_split.unlock_size)
        except AttributeError:
            pass
    return False


def editable_boundaries_cabinet(cabinet_obj, layout):
    """Boundary records for the cabinet-level grab operator.

    Exposes only the four outer edges of the cabinet — left, right,
    top, bottom. Bay-level and intra-bay edits live in
    editable_boundaries_v1 (Grab Face Frame). This separation keeps
    each operator's overlay unambiguous: at any FF position there's
    exactly one drag handle per Grab variant, no flicker between
    overlapping per-bay and cabinet-level lines.

    LEFT and BOTTOM dragging translate the cabinet's location (so the
    opposite edge stays put) in addition to writing the dimension.
    Depth is omitted; face-on UX doesn't render a depth handle cleanly.
    """
    ff_len = face_frame_length(layout)
    # OUTER_RIGHT — vertical line at the FF's right end
    yield {
        'kind': 'OUTER_RIGHT',
        'axis': 'X',
        'primary_sign': 1.0,
        'cabinet_obj': cabinet_obj,
        'dim_attr': 'width',
        'ff_x': ff_len,
        'ff_z_low': 0.0,
        'ff_z_high': layout.dim_z,
    }
    # OUTER_LEFT — vertical line at the FF's left end. Translates the
    # cabinet location along +ff_x_world so the right edge stays put.
    yield {
        'kind': 'OUTER_LEFT',
        'axis': 'X',
        'primary_sign': -1.0,
        'translate': True,
        'translate_axis': 'X',
        'cabinet_obj': cabinet_obj,
        'dim_attr': 'width',
        'ff_x': 0.0,
        'ff_z_low': 0.0,
        'ff_z_high': layout.dim_z,
    }
    # OUTER_TOP — horizontal line at the cabinet's top
    yield {
        'kind': 'OUTER_TOP',
        'axis': 'Z',
        'primary_sign': 1.0,
        'cabinet_obj': cabinet_obj,
        'dim_attr': 'height',
        'ff_z': layout.dim_z,
        'ff_x_low': 0.0,
        'ff_x_high': ff_len,
    }
    # OUTER_BOTTOM — horizontal line at the cabinet's floor. Translates
    # cabinet location along +ff_z_world so the top stays put. For
    # floor-anchored types (base, tall) this lifts the cabinet off the
    # floor; the user is responsible for re-seating it if needed.
    yield {
        'kind': 'OUTER_BOTTOM',
        'axis': 'Z',
        'primary_sign': -1.0,
        'translate': True,
        'translate_axis': 'Z',
        'cabinet_obj': cabinet_obj,
        'dim_attr': 'height',
        'ff_z': 0.0,
        'ff_x_low': 0.0,
        'ff_x_high': ff_len,
    }

def mouse_to_ff_local_with_basis(region, rv3d, mouse_xy, basis):
    """Project a mouse position onto an FF outer plane defined by the
    given basis tuple (origin_w, x_axis_w, z_axis_w, normal_w). Returns
    (ff_x, ff_z, world_hit) or None.

    Companion to mouse_to_ff_local. Used by the modify-cabinet operator
    during drags that translate the cabinet's location: a frozen basis
    captured at drag start gives cursor_delta a stable reference frame,
    avoiding compounding drift as the cabinet moves under the cursor.
    """
    from bpy_extras import view3d_utils
    from mathutils.geometry import intersect_line_plane
    if region is None or rv3d is None:
        return None
    co2d = (mouse_xy[0], mouse_xy[1])
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d)
    ray_dir = view3d_utils.region_2d_to_vector_3d(region, rv3d, co2d)
    if ray_origin is None or ray_dir is None:
        return None
    origin_w, x_axis_w, z_axis_w, normal_w = basis
    hit = intersect_line_plane(
        ray_origin, ray_origin + ray_dir, origin_w, normal_w,
    )
    if hit is None:
        return None
    rel = hit - origin_w
    return (rel.dot(x_axis_w), rel.dot(z_axis_w), hit)

