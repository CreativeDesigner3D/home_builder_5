"""Face frame cabinet construction classes.

Phase 3a deliverable: class hierarchy and a minimal carcass build.
- FaceFrameCabinet: base class for all face frame cabinets. No drivers.
  All dimension propagation runs through cabinet.recalculate().
- BaseFaceFrameCabinet, UpperFaceFrameCabinet, TallFaceFrameCabinet,
  LapDrawerFaceFrameCabinet: subclasses with type-specific defaults.
- FaceFrameBay: bay cage object (Phase 3b will populate bay contents).

Carcass conventions match frameless (same CabinetPart GeoNode setup):
- Cabinet origin at back-left, floor level
- +X is right, -Y is forward (depth runs in -Y), +Z is up
- Back panel sits at y=0; front of cabinet is at y=-depth
- Mirror Y=True on a part means it extrudes in -Y from its origin
- Mirror Z=True means it extrudes in -Z from its origin
"""
import bpy
import bmesh
import math
from types import SimpleNamespace
import os
from contextlib import contextmanager

from mathutils import Vector, Matrix, Euler

from ... import hb_utils
from ...hb_types import GeoNodeCage, GeoNodeCutpart, GeoNodeDrawerBox, GeoNodeRectangle
from ...units import inch
from ...hb_details import apply_label_style
from ..common import types_appliances
from ..frameless.types_frameless import CabinetPart
from ..frameless.types_products import HalfWall as _FramelessHalfWall
from ..frameless.types_products import SupportFrame as _FramelessSupportFrame
from . import solver_face_frame as solver
from . import pulls


# ---------------------------------------------------------------------------
# Identity tags
# ---------------------------------------------------------------------------
TAG_CABINET_CAGE = 'IS_FACE_FRAME_CABINET_CAGE'
TAG_BAY_CAGE = 'IS_FACE_FRAME_BAY_CAGE'
TAG_OPENING_CAGE = 'IS_FACE_FRAME_OPENING_CAGE'
TAG_SPLIT_NODE = 'IS_FACE_FRAME_SPLIT_NODE'
# Non-cabinet face-frame PRODUCTS (e.g. the Half Wall) that should still
# behave like a cabinet for selection purposes: their cage shows + is the
# selection target in 'Cabinets' selection mode. They are NOT TAG_CABINET_CAGE
# (that would route them through the cabinet recalc / modify / carcass
# machinery, which would wreck their custom geometry) - the selection mode
# operator special-cases this tag the same way it does IS_APPLIANCE.
TAG_PRODUCT_CAGE = 'IS_FACE_FRAME_PRODUCT_CAGE'
# Interior tree tags. Internal nodes carry TAG_INTERIOR_SPLIT_NODE; leaves
# carry TAG_INTERIOR_REGION. Both live as cage children of an opening.
TAG_INTERIOR_SPLIT_NODE = 'IS_INTERIOR_SPLIT_NODE'
TAG_INTERIOR_REGION = 'IS_INTERIOR_REGION'

# Reentrance guards. Bay-level prop writes inside recalculate() (such as
# the width redistribution in _distribute_bay_widths) fire those props'
# update callbacks, which would normally call back into recalculate. The
# guards short-circuit that cycle.
#
# _RECALCULATING: cabinet root IDs currently inside recalculate(). Update
#     callbacks consult this and exit early if the cabinet is already in
#     the middle of a recalc.
# _DISTRIBUTING_WIDTHS: cabinet root IDs whose bay widths are currently
#     being written by _distribute_bay_widths. The bay width update callback
#     consults this to distinguish system writes (no auto-lock) from user
#     edits (auto-lock so the value holds during future redistributions).
# _RECALC_SUSPEND_DEPTH: refcounted suspend of recalculate_face_frame_cabinet.
#     While > 0, recalcs are coalesced by cabinet name into _PENDING_RECALC_NAMES
#     instead of executing. The outermost resume drains the pending set and
#     runs each cabinet's recalc exactly once. Use the suspend_recalc() context
#     manager - inner suspends stack and only the outermost exit drains.
_RECALCULATING = set()
_DISTRIBUTING_WIDTHS = set()
_RECALC_SUSPEND_DEPTH = 0
_PENDING_RECALC_NAMES = set()


@contextmanager
def suspend_recalc():
    """Suspend cabinet recalcs across a block of property writes.

    Pending recalcs (whether from update callbacks or explicit calls) are
    coalesced and run once when the outermost suspend exits. Use this
    around any operation that performs many property writes that would
    each trigger a full cabinet recalc - the actual layout work happens
    once at the end instead of N times during.
    """
    global _RECALC_SUSPEND_DEPTH
    _RECALC_SUSPEND_DEPTH += 1
    try:
        yield
    finally:
        _RECALC_SUSPEND_DEPTH -= 1
        if _RECALC_SUSPEND_DEPTH == 0:
            pending = list(_PENDING_RECALC_NAMES)
            _PENDING_RECALC_NAMES.clear()
            for cab_name in pending:
                cab = bpy.data.objects.get(cab_name)
                if cab is None:
                    continue
                # Don't let one cabinet's recalc failure block the rest.
                try:
                    recalculate_face_frame_cabinet(cab)
                except Exception:
                    pass


# Single string-enum role for parts.
PART_ROLE_LEFT_SIDE = 'LEFT_SIDE'
PART_ROLE_RIGHT_SIDE = 'RIGHT_SIDE'
PART_ROLE_TOP = 'TOP'  # solid top panel for Upper / Tall (Base / Lap use stretchers)
PART_ROLE_FRONT_STRETCHER = 'FRONT_STRETCHER'
PART_ROLE_REAR_STRETCHER = 'REAR_STRETCHER'
PART_ROLE_BOTTOM = 'BOTTOM'
PART_ROLE_BACK = 'BACK'
PART_ROLE_TOE_KICK_SUBFRONT = 'TOE_KICK_SUBFRONT'
PART_ROLE_FINISH_TOE_KICK = 'FINISH_TOE_KICK'
PART_ROLE_LEFT_CORNER_FINISH_KICK = 'LEFT_CORNER_FINISH_KICK'
PART_ROLE_RIGHT_CORNER_FINISH_KICK = 'RIGHT_CORNER_FINISH_KICK'
PART_ROLE_MID_FINISH_KICK = 'MID_FINISH_KICK'
PART_ROLE_LEFT_KICK_RETURN = 'LEFT_KICK_RETURN'
PART_ROLE_RIGHT_KICK_RETURN = 'RIGHT_KICK_RETURN'
# Loose toe kick ladder sub-base (toe_kick_type == 'LOOSE'): a freestanding
# frame the floated carcass sits on - front + rear rail spanning between two
# front-to-back end boards. All four are finished-material parts.
PART_ROLE_LOOSE_KICK_FRONT = 'LOOSE_KICK_FRONT'
PART_ROLE_LOOSE_KICK_REAR = 'LOOSE_KICK_REAR'
PART_ROLE_LOOSE_KICK_END_LEFT = 'LOOSE_KICK_END_LEFT'
PART_ROLE_LOOSE_KICK_END_RIGHT = 'LOOSE_KICK_END_RIGHT'

# Leg product (slim face-frame post / filler). Built by a dedicated
# product class that bypasses the bay/solver pipeline; all parts are
# finished-material.
LEG_PRODUCT_TAG = 'IS_LEG_PRODUCT'
PART_ROLE_LEG_PANEL_LEFT = 'LEG_PANEL_LEFT'
PART_ROLE_LEG_PANEL_RIGHT = 'LEG_PANEL_RIGHT'
PART_ROLE_LEG_STILE = 'LEG_STILE'
PART_ROLE_LEG_TK_STILE = 'LEG_TK_STILE'
PART_ROLE_LEG_TK_FILLER = 'LEG_TK_FILLER'
# Leg product v2: finished front bands + interior back / nailers.
PART_ROLE_LEG_FINISH_X_LEFT = 'LEG_FINISH_X_LEFT'
PART_ROLE_LEG_FINISH_X_RIGHT = 'LEG_FINISH_X_RIGHT'
PART_ROLE_LEG_BACK = 'LEG_BACK'
PART_ROLE_LEG_NAILER_LEFT = 'LEG_NAILER_LEFT'
PART_ROLE_LEG_NAILER_RIGHT = 'LEG_NAILER_RIGHT'

# Floating shelf (wall-mounted hollow slab). Built by a dedicated
# product class that bypasses the bay/solver pipeline; finished boards.
FLOATING_SHELF_TAG = 'IS_FLOATING_SHELF'
PART_ROLE_SHELF_FRONT = 'SHELF_FRONT'
PART_ROLE_SHELF_TOP = 'SHELF_TOP'
PART_ROLE_SHELF_BOTTOM = 'SHELF_BOTTOM'
PART_ROLE_SHELF_PANEL_LEFT = 'SHELF_PANEL_LEFT'
PART_ROLE_SHELF_PANEL_RIGHT = 'SHELF_PANEL_RIGHT'

# Valance product (a decorative board spanning the gap between two
# upper cabinets). Same non-bay pattern as the floating shelf.
VALANCE_TAG = 'IS_VALANCE_PRODUCT'
PART_ROLE_VALANCE_BOARD = 'VALANCE_BOARD'
PART_ROLE_VALANCE_COVER = 'VALANCE_COVER'
PART_ROLE_VALANCE_PANEL_LEFT = 'VALANCE_PANEL_LEFT'
PART_ROLE_VALANCE_PANEL_RIGHT = 'VALANCE_PANEL_RIGHT'
PART_ROLE_BLIND_PANEL_LEFT = 'BLIND_PANEL_LEFT'
PART_ROLE_BLIND_PANEL_RIGHT = 'BLIND_PANEL_RIGHT'

# 1/4" thick decorative panel that closes off the dead corner space when
# the cabinet sits next to a perpendicular cabinet on an adjacent wall.
BLIND_PANEL_THICKNESS = inch(0.25)

# Face frame member roles (rails and stiles). Phase 3a doesn't create any
# of these yet; defined here so the "Face Frame" selection mode has a known
# set of roles to filter on once Phase 3b builds them.
PART_ROLE_TOP_RAIL = 'TOP_RAIL'
PART_ROLE_BOTTOM_RAIL = 'BOTTOM_RAIL'
PART_ROLE_LEFT_STILE = 'LEFT_STILE'
PART_ROLE_RIGHT_STILE = 'RIGHT_STILE'
# Optional 'stile in lieu of leg' lower stiles on a refrigerator cabinet
# (floor -> top of fridge opening). Built only on RefrigeratorCabinet.
PART_ROLE_LEFT_REFRIG_STILE = 'LEFT_REFRIG_STILE'
PART_ROLE_RIGHT_REFRIG_STILE = 'RIGHT_REFRIG_STILE'
PART_ROLE_MID_STILE = 'MID_STILE'
PART_ROLE_MID_RAIL = 'MID_RAIL'
# Filler stiles in a front-dropped bay's open band (above the dropped
# top rail), fitting a farm sink / cooktop to the drop. Keyed per bay +
# side and reconciled from solver.front_drop_filler_segments.
PART_ROLE_FRONT_DROP_FILLER = 'FRONT_DROP_FILLER'

# Splitter members and backings created by H/V splits inside a single
# bay. Mid rail / mid stile sit in the face frame plane; division /
# shelf are carcass-deep panels behind them. Defined here (above the
# FACE_FRAME_PART_ROLES set) so they're in scope when the set is built.
PART_ROLE_BAY_MID_RAIL = 'BAY_MID_RAIL'
PART_ROLE_BAY_MID_STILE = 'BAY_MID_STILE'
PART_ROLE_BAY_DIVISION = 'BAY_DIVISION'
PART_ROLE_BAY_SHELF = 'BAY_SHELF'

FACE_FRAME_PART_ROLES = frozenset({
    PART_ROLE_TOP_RAIL, PART_ROLE_BOTTOM_RAIL,
    PART_ROLE_LEFT_STILE, PART_ROLE_RIGHT_STILE,
    PART_ROLE_MID_STILE, PART_ROLE_MID_RAIL,
    PART_ROLE_BAY_MID_RAIL, PART_ROLE_BAY_MID_STILE,
    PART_ROLE_FRONT_DROP_FILLER,
})

BAY_SPLITTER_ROLES = frozenset({
    PART_ROLE_BAY_MID_RAIL, PART_ROLE_BAY_MID_STILE,
})
BAY_BACKING_ROLES = frozenset({
    PART_ROLE_BAY_DIVISION, PART_ROLE_BAY_SHELF,
})


# Highlight colour for a face frame part the user has UNLOCKED (manually
# overridden). Shown in Face Frame selection mode -- amber, slightly
# transparent -- so changed-from-default parts stand out from the default
# light-blue highlight. Used by the toggle_mode operator AND the post-recalc
# highlight reapply below, so both colouring paths agree.
FACE_FRAME_UNLOCKED_COLOR = (0.95, 0.55, 0.10, 0.6)


def part_width_is_unlocked(obj):
    """True when this face frame part carries a manual width override (its
    unlock flag is set), so Face Frame selection mode can flag it as
    changed-from-default. Only the width-overridable roles can be unlocked;
    every other part returns False.
    """
    role = obj.get('hb_part_role')
    if role not in FACE_FRAME_PART_ROLES:
        return False
    root = find_cabinet_root(obj)
    if root is None:
        return False
    cab = root.face_frame_cabinet
    if role == PART_ROLE_LEFT_STILE:
        return bool(cab.unlock_left_stile)
    if role == PART_ROLE_RIGHT_STILE:
        return bool(cab.unlock_right_stile)
    if role == PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            return bool(cab.mid_stile_widths[msi].unlock)
        return False
    if role in (PART_ROLE_TOP_RAIL, PART_ROLE_BOTTOM_RAIL):
        attr = ('unlock_top_rail' if role == PART_ROLE_TOP_RAIL
                else 'unlock_bottom_rail')
        # Cabinet-level rail unlock (the lock toggle in the cabinet prompts,
        # draw_face_frame_defaults) overrides every bay's rail, so flag the
        # part when it is set -- the same name lives on the bay, which the
        # right-click set_part_width path flips. Either one means overridden.
        if getattr(cab, attr):
            return True
        start = obj.get('hb_segment_start_bay', 0)
        bay = None
        for child in root.children:
            if child.get(TAG_BAY_CAGE) and child.get('hb_bay_index') == start:
                bay = child
                break
        if bay is None:
            return False
        return bool(getattr(bay.face_frame_bay, attr))
    if role in (PART_ROLE_BAY_MID_RAIL, PART_ROLE_BAY_MID_STILE):
        split_name = obj.get('hb_split_node_name')
        split = bpy.data.objects.get(split_name) if split_name else None
        if split is None:
            return False
        sp = split.face_frame_split
        if sp.unlock_splitter_width:
            return True
        idx = obj.get('hb_splitter_index', 0)
        coll = sp.splitter_widths
        return 0 <= idx < len(coll) and bool(coll[idx].active)
    return False

# Carcass interior partition behind each mid stile (one per gap).
PART_ROLE_MID_DIVISION = 'MID_DIVISION'

# Filler attached to a mid-div on the shallower bay's side, covering
# the mid-stile back-face overhang in the Z range between adjacent
# bays' floors when those floors differ.
PART_ROLE_PARTITION_SKIN = 'PARTITION_SKIN'

# Front parts (children of opening cages). Roles are reserved here so
# selection-mode filtering can pick them up; only DOOR is implemented in
# this pass. Drawer fronts and pullouts will use their own roles when
# they land.
PART_ROLE_DOOR = 'DOOR'
PART_ROLE_DRAWER_FRONT = 'DRAWER_FRONT'
PART_ROLE_PULLOUT_FRONT = 'PULLOUT_FRONT'
PART_ROLE_FALSE_FRONT = 'FALSE_FRONT'
PART_ROLE_INSET_PANEL = 'INSET_PANEL'
# Tilt-out: a drawer-styled front that tilts down on a BOTTOM hinge.
# Own role (not FALSE_FRONT) so it's drawer-styled but carries a pull and
# a swing; not in the drawer-box role set, so it gets no slide box.
PART_ROLE_TILT_OUT = 'TILT_OUT'
PART_ROLE_APRON = 'APRON'
# Drawer-look door: a working DOOR leaf wearing N applied drawer-front
# panels (proud of the leaf, with reveal gaps that read as faux mid
# rails) so it looks like a drawer stack but opens as one door. Built in
# _update_fronts_in_opening as children of the door part (inherit swing);
# carry no DOOR_STYLE_NAME, so pricing / machining see one door.
PART_ROLE_DRAWER_LOOK_FRONT = 'DRAWER_LOOK_FRONT'
# Faux mid-rail strip between drawer-look fronts, added only for FULL
# INSET (proud of the inset fronts, like a real inset face frame).
PART_ROLE_DRAWER_LOOK_RAIL = 'DRAWER_LOOK_RAIL'
DRAWER_LOOK_REVEAL = inch(0.125)            # gap between applied fronts
DRAWER_LOOK_TALLER_TOP_FACTOR = 1.5         # top front height vs each other

# Applied finished-back part: a 3/4 panel layered on top of the carcass
# back when back_finished_end_condition is FINISHED. Carcass back stays
# at its normal back_thickness (1/4 typically); this part adds the
# visible finish surface behind it.
PART_ROLE_FINISHED_BACK = 'FINISHED_BACK'

# Finished-side return closeout. When a FINISHED side is extended back past
# a FINISHED back and the user sets a return width, the exposed back corner
# is wrapped by two 3/4 parts: a RETURN panel parallel to the side (its
# depth = the side's extend-back amount) that dies into the finished back,
# and a rear STILE (the outermost/rearmost member) whose width IS the return
# width, running full height to the floor. Managed by
# _reconcile_finished_side_returns; both roles are in _FINISH_EXTERIOR_ROLES.
PART_ROLE_LEFT_SIDE_RETURN = 'LEFT_SIDE_RETURN'
PART_ROLE_RIGHT_SIDE_RETURN = 'RIGHT_SIDE_RETURN'
PART_ROLE_LEFT_SIDE_RETURN_STILE = 'LEFT_SIDE_RETURN_STILE'
PART_ROLE_RIGHT_SIDE_RETURN_STILE = 'RIGHT_SIDE_RETURN_STILE'

# Tag carried by either kind of return member (the flat FINISHED cutpart or
# the PANELED applied-panel root) so the reconciler can find and kind-swap it
# regardless of type. `hb_return_member_kind` ('FINISHED'/'PANELED') records
# which kind is currently built.
TAG_RETURN_MEMBER = 'hb_return_member'

# Applied flush-X strip: a 1/4 part covering the front portion of a
# cabinet side when LEFT/RIGHT_finished_end_condition is FLUSH_X. The
# strip's outer face is flush with the FF outer face; its width along
# the cabinet depth is the user's *_flush_x_amount value (typically
# 4"). Used for sides that abut a dishwasher / appliance where a full
# applied panel isn't wanted.
PART_ROLE_FLUSH_X = 'FLUSH_X'
TAG_FLUSH_X_SIDE = 'hb_flush_x_side'
PART_ROLE_FULL_OVERLAY_STILE = 'FULL_OVERLAY_STILE'
TAG_FO_STILE_SIDE = 'hb_fo_stile_side'

# Per-bay finish liner: 1/4 finish-material panels added to the inner
# faces of a bay's opening (left / right / top / back) when the bay's
# finish_bay flag is set, so the exterior finish reads inside the
# opening. Keyed by bay index + face so they reuse-in-place / sweep
# cleanly across recalcs. See _reconcile_bay_finish_panels.
PART_ROLE_BAY_FINISH = 'BAY_FINISH'
TAG_BAY_FINISH_BAY = 'hb_bay_finish_bay'
TAG_BAY_FINISH_FACE = 'hb_bay_finish_face'
# Which opening within the bay a finish liner belongs to: an opening
# leaf index for a per-opening finish, or -1 for a whole-bay finish.
TAG_BAY_FINISH_OPENING = 'hb_bay_finish_opening'

# Textured-finish applied panels: 1/4 flat parts representing beadboard
# or shiplap finishes on a side (LEFT / RIGHT / BACK). Distinct roles
# so a future material pass can shade them differently; geometry is
# identical between the two for now (later: a modifier could carve
# bead profiles / plank reveals into the part).
PART_ROLE_BEADBOARD = 'BEADBOARD'
PART_ROLE_SHIPLAP = 'SHIPLAP'
TAG_TEXTURED_PANEL_SIDE = 'hb_textured_panel_side'
TEXTURED_PANEL_ROLES = {
    'BEADBOARD': PART_ROLE_BEADBOARD,
    'SHIPLAP':   PART_ROLE_SHIPLAP,
}

# Applied panel side tag - written on a panel root that's been spawned
# by a cabinet to serve as its left/right/back finished end. Drives
# reconciliation (find / resize / remove on cabinet recalc).
TAG_APPLIED_PANEL_SIDE = 'hb_applied_to_cabinet_side'

# Cabinet-side finished_end_condition values that spawn an applied panel
# child. PANELED is the simplest case (just an inset-panel face frame);
# FALSE_FF and WORKING_FF will eventually drive the panel's openings to
# carry false / working drawer fronts (deferred to a later pass).
APPLIED_PANEL_END_TYPES = frozenset({'PANELED', 'FALSE_FF', 'WORKING_FF'})

# Pivot empty parent of every front part. Holds the swing rotation
# (door / pullout) or the slide translation (drawer front) so the front
# part itself stays at a fixed local transform relative to the pivot.
PART_ROLE_FRONT_PIVOT = 'FRONT_PIVOT'

# Drawer box behind a drawer or pullout front. Parented to the front pivot
# (not the front part) so the box rides the slide animation but is sized
# from the opening cage's interior dimensions, independent of the front's
# overlay-inflated size. Not a member of FRONT_PART_ROLES; it's an interior
# part by structure even though it's spawned alongside the front.
PART_ROLE_DRAWER_BOX = 'DRAWER_BOX'

# Front roles that share the same panel geometry today. Keeping them
# grouped here so reconciliation can iterate the set instead of
# spelling each role out.
# Left/right filler stiles built inside an APPLIANCE opening (no door/drawer).
# Sits in the face-frame plane like a stile but is wiped + rebuilt per recalc
# like a front part, so it's grouped with FRONT_PART_ROLES rather than the
# cabinet-level FACE_FRAME_PART_ROLES (it has no per-part unlock width; its
# width comes from the opening's appliance/filler props).
PART_ROLE_APPLIANCE_FILLER = 'APPLIANCE_FILLER'

FRONT_PART_ROLES = frozenset({
    PART_ROLE_DOOR,
    PART_ROLE_DRAWER_FRONT,
    PART_ROLE_PULLOUT_FRONT,
    PART_ROLE_FALSE_FRONT,
    PART_ROLE_TILT_OUT,
    PART_ROLE_INSET_PANEL,
    PART_ROLE_APRON,
    PART_ROLE_APPLIANCE_FILLER,
})

FRONT_TYPE_TO_ROLE = {
    'DOOR':         PART_ROLE_DOOR,
    'DRAWER_FRONT': PART_ROLE_DRAWER_FRONT,
    'PULLOUT':      PART_ROLE_PULLOUT_FRONT,
    'FALSE_FRONT':  PART_ROLE_FALSE_FRONT,
    'TILT_OUT':     PART_ROLE_TILT_OUT,
}

# ---------------------------------------------------------------------------
# Interior parts (children of opening cages; sit behind the face frame).
# Orthogonal to front_type - any front_type can carry interior items, and
# 'open' openings (front_type = NONE) get all of their visual content from
# this list.
# ---------------------------------------------------------------------------
PART_ROLE_ADJUSTABLE_SHELF = 'ADJUSTABLE_SHELF'
PART_ROLE_GLASS_SHELF = 'GLASS_SHELF'
PART_ROLE_PULLOUT_SHELF = 'PULLOUT_SHELF'
PART_ROLE_PULLOUT_SPACER = 'PULLOUT_SPACER'
PART_ROLE_ROLLOUT_BOX = 'ROLLOUT_BOX'
PART_ROLE_ROLLOUT_SPACER = 'ROLLOUT_SPACER'
PART_ROLE_TRAY_DIVIDER = 'TRAY_DIVIDER'
PART_ROLE_TRAY_LOCKED_SHELF = 'TRAY_LOCKED_SHELF'
PART_ROLE_VANITY_SHELF = 'VANITY_SHELF'
PART_ROLE_VANITY_SUPPORT = 'VANITY_SUPPORT'
PART_ROLE_ACCESSORY_LABEL = 'ACCESSORY_LABEL'
# Appliance-bay annotation: the square + word (SINK / COOKTOP) drawn on
# top of an appliance bay so plan views read like a dealer drawing.
# Wiped + recreated every recalc (sized from the live bay cage); the
# durable signal is the APPLIANCE_BAY custom prop on the bay cage.
PART_ROLE_APPLIANCE_ANNOTATION = 'APPLIANCE_ANNOTATION'
APPLIANCE_ANNO_SIDE_MARGIN = inch(2.0)     # square inset from each bay side
APPLIANCE_ANNO_Z_LIFT = inch(0.5)          # square sits this far above the bay top
APPLIANCE_ANNO_TEXT_SIZE = inch(2.0)
APPLIANCE_ANNO_LINE_THICKNESS = inch(0.05)
# Word pulled toward the bay FRONT (-Y) so it stays readable in
# elevations when an upper cabinet hangs over the sink / cooktop.
APPLIANCE_ANNO_TEXT_Y_OFFSET = inch(-4.0)
# Interior tree dividers: physical parts at split-node boundaries.
PART_ROLE_INTERIOR_DIVISION = 'INTERIOR_DIVISION'
PART_ROLE_INTERIOR_FIXED_SHELF = 'INTERIOR_FIXED_SHELF'
# Optional face frame member (rail / stile) inline with the
# cabinet face frame at an interior split node.
PART_ROLE_INTERIOR_FF_RAIL = 'INTERIOR_FF_RAIL'
PART_ROLE_INTERIOR_FF_STILE = 'INTERIOR_FF_STILE'

INTERIOR_PART_ROLES = frozenset({
    PART_ROLE_ADJUSTABLE_SHELF,
    PART_ROLE_GLASS_SHELF,
    PART_ROLE_PULLOUT_SHELF,
    PART_ROLE_PULLOUT_SPACER,
    PART_ROLE_ROLLOUT_BOX,
    PART_ROLE_ROLLOUT_SPACER,
    PART_ROLE_TRAY_DIVIDER,
    PART_ROLE_TRAY_LOCKED_SHELF,
    PART_ROLE_VANITY_SHELF,
    PART_ROLE_VANITY_SUPPORT,
    PART_ROLE_ACCESSORY_LABEL,
    PART_ROLE_INTERIOR_DIVISION,
    PART_ROLE_INTERIOR_FIXED_SHELF,
    PART_ROLE_INTERIOR_FF_RAIL,
    PART_ROLE_INTERIOR_FF_STILE,
})

# Maps a Face_Frame_Interior_Item.kind to the *primary* part role its
# descriptors carry. Multi-part assemblies (PULLOUT_SHELF, ROLLOUT,
# TRAY_DIVIDERS, VANITY_SHELVES) emit multiple part roles; this map
# only names the headline role used for tagging the wipe set.
INTERIOR_KIND_TO_ROLE = {
    'ADJUSTABLE_SHELF':      PART_ROLE_ADJUSTABLE_SHELF,
    'GLASS_SHELF':           PART_ROLE_GLASS_SHELF,
    'PULLOUT_SHELF':         PART_ROLE_PULLOUT_SHELF,
    'ROLLOUT':               PART_ROLE_ROLLOUT_BOX,
    'TRAY_DIVIDERS':         PART_ROLE_TRAY_DIVIDER,
    'VANITY_SHELVES':        PART_ROLE_VANITY_SHELF,
    'ACCESSORY':             PART_ROLE_ACCESSORY_LABEL,
    'INTERIOR_DIVISION':     PART_ROLE_INTERIOR_DIVISION,
    'INTERIOR_FIXED_SHELF':  PART_ROLE_INTERIOR_FIXED_SHELF,
}

# Angled standard cabinet machinery. The cutter is a hidden GeoNodeCage
# whose cage volume covers everything forward of the angled face frame
# inner plane; carcass parts that need a trapezoidal silhouette carry a
# 'Angled Cut' boolean DIFFERENCE modifier referencing it. Defined down
# here so the role frozenset can reference PART_ROLE_ADJUSTABLE_SHELF
# (declared just above).
PART_ROLE_ANGLED_CUTTER = 'ANGLED_CUTTER'
ANGLED_CUT_MOD_NAME = 'Angled Cut'
ANGLED_CUT_PART_ROLES = frozenset({
    PART_ROLE_TOP, PART_ROLE_BOTTOM,
    PART_ROLE_BAY_SHELF,
    PART_ROLE_ADJUSTABLE_SHELF, PART_ROLE_GLASS_SHELF,
    PART_ROLE_TRAY_LOCKED_SHELF,
    PART_ROLE_INTERIOR_FIXED_SHELF,
})

# Tip-up wedge cutter (back-bottom chamfer). Same lazy-cutter + boolean
# pattern as the angled cutter, but the cutter is a triangular-prism MESH
# and it's driven by the wedge_* cabinet props (see solver.wedge_geometry).
PART_ROLE_WEDGE_CUTTER = 'WEDGE_CUTTER'
WEDGE_CUT_MOD_NAME = 'Tip-Up Wedge'
WEDGE_CUT_PART_ROLES = frozenset({
    PART_ROLE_LEFT_SIDE, PART_ROLE_RIGHT_SIDE,
    PART_ROLE_BACK, PART_ROLE_FINISHED_BACK, PART_ROLE_BOTTOM,
    PART_ROLE_LEFT_KICK_RETURN, PART_ROLE_RIGHT_KICK_RETURN,
})

# Angled back-extension trim cutter. The full-depth TOP / BOTTOM (and
# shelves) can't be a trapezoid natively (they are rectangular cutparts),
# so they are first extended rectangularly to reach the extended back
# corner, then a boolean DIFFERENCE trims the front overhang along the
# angled side line - leaving the trapezoid. Same lazy mesh-cutter pattern
# as the tip-up wedge; driven by extend_back_left / extend_back_right.
# Furniture / veneer wood top: an overhanging slab sitting proud on the
# carcass top, used by dresser products. Managed by _apply_furniture_top
# (ensure / position / cleanup), gated on the furniture_top cabinet prop;
# in _FINISH_EXTERIOR_ROLES so the material walk gives it the cabinet's
# exterior wood finish.
PART_ROLE_FURNITURE_TOP = 'FURNITURE_TOP'
# Furniture-top plan shapes (furniture_top_shape). BOW_BACK and RADIUS
# trim the rectangular top cutpart with a hidden boolean cutter (same
# lazy mesh-cutter pattern as the back-extension trim); WATERFALL adds a
# drop panel at each end of the top running from its underside to the
# floor (in _FINISH_EXTERIOR_ROLES like the top itself). All managed by
# _apply_furniture_top.
PART_ROLE_FURNITURE_TOP_CUTTER = 'FURNITURE_TOP_CUTTER'
PART_ROLE_FURNITURE_TOP_LEG = 'FURNITURE_TOP_LEG'
FURNITURE_TOP_CUT_MOD_NAME = 'Furniture Top Shape Cut'
# Arc tessellation for the bow-back / radius-corner cutter meshes.
FURNITURE_TOP_BOW_SEGMENTS = 48
FURNITURE_TOP_RADIUS_SEGMENTS = 16
# Finished back panel closing the open recess below an upper whose
# ends are extended down (hutch). Managed by _apply_hutch_back; in
# _FINISH_EXTERIOR_ROLES so it gets the cabinet's finish material.
PART_ROLE_HUTCH_BACK = 'HUTCH_BACK'
# Attached wing: an angled return panel on an end, built from that end's
# extend_back value when its "Attach as Wing" option is on (carcass stays
# square). Managed by _apply_wing; finished on its outer face only.
PART_ROLE_WING = 'WING'
PART_ROLE_BACK_EXT_CUTTER = 'BACK_EXT_CUTTER'
BACK_EXT_CUT_MOD_NAME = 'Back Extension Trim'
BACK_EXT_CUT_PART_ROLES = frozenset({
    PART_ROLE_TOP, PART_ROLE_BOTTOM,
    PART_ROLE_FRONT_STRETCHER, PART_ROLE_REAR_STRETCHER,
    PART_ROLE_FINISH_TOE_KICK, PART_ROLE_TOE_KICK_SUBFRONT,
    PART_ROLE_BAY_SHELF,
    PART_ROLE_ADJUSTABLE_SHELF, PART_ROLE_GLASS_SHELF,
})

# Over-stool side-front profile cut: a decorative silhouette (authored as a
# closed curve in face_frame_assets/profiles) boolean-subtracted from the
# bottom-front corner of each extended side panel. See _apply_overstool_profile.
PART_ROLE_SIDE_PROFILE_CUTTER = 'SIDE_PROFILE_CUTTER'
SIDE_PROFILE_CUT_MOD_NAME = 'Side Profile Cut'
PART_ROLE_OVERSTOOL_SHELF = 'OVERSTOOL_SHELF'
PART_ROLE_OVERSTOOL_TOWEL_BAR = 'OVERSTOOL_TOWEL_BAR'
# Leg-accessory sizing (effective real-world). Shelf is front-aligned (front
# edge flush with the leg front, extending back); towel bar is a round rod.
# Z positions are measured UP from the dropped leg bottom.
OVERSTOOL_SHELF_DEPTH = inch(6.0)
OVERSTOOL_SHELF_THICKNESS = inch(0.75)
OVERSTOOL_SHELF_Z_ABOVE_LEG_BOTTOM = inch(0.0)  # flush with leg bottom
OVERSTOOL_TOWEL_BAR_DIAMETER = inch(0.75)
OVERSTOOL_TOWEL_BAR_Z_ABOVE_LEG_BOTTOM = inch(4.0)
OVERSTOOL_TOWEL_BAR_Y_FROM_FRONT = inch(1.0)
OVERSTOOL_TOWEL_BAR_SEGMENTS = 16
# When BOTH accessories are present they rearrange: the shelf raises and the
# towel bar drops below it + moves back, so the bar tucks under the raised shelf.
OVERSTOOL_SHELF_Z_COMBO_RAISE = inch(3.0)
OVERSTOOL_TOWEL_BAR_COMBO_Z_DROP = inch(3.5)
OVERSTOOL_TOWEL_BAR_COMBO_Y_BACK = inch(2.0)
_OVERSTOOL_PROFILE_BLEND = ('face_frame_assets', 'profiles', 'Over Stool Profile.blend')
_OVERSTOOL_PROFILE_CURVE_NAME = 'BézierCurve'
_OVERSTOOL_PROFILE_POLY_CACHE = None  # list[(x, y)] meters, ordered closed loop


def _overstool_profile_poly():
    """Return the over-stool profile outline as an ordered closed loop of
    (x, y) points in the profile's LOCAL XY (meters), sampled from the
    authored Bezier in the profile blend. Cached after the first load.

    Sampled with interpolate_bezier (no depsgraph / scene-link needed) so it
    is safe to call from a recalc. The loop is the profile silhouette; the
    cutter prism (in _position_side_profile_cutter) extrudes it through the
    panel thickness for a boolean DIFFERENCE.
    """
    global _OVERSTOOL_PROFILE_POLY_CACHE
    if _OVERSTOOL_PROFILE_POLY_CACHE is not None:
        return _OVERSTOOL_PROFILE_POLY_CACHE
    from mathutils.geometry import interpolate_bezier
    blend = os.path.join(os.path.dirname(__file__), *_OVERSTOOL_PROFILE_BLEND)
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.objects = [_OVERSTOOL_PROFILE_CURVE_NAME]
    obj = next((o for o in bpy.data.objects if o not in before), None)
    pts = []
    try:
        sp = obj.data.splines[0]
        bp = sp.bezier_points
        n = len(bp)
        res = max(8, obj.data.resolution_u)
        last = n if sp.use_cyclic_u else n - 1
        for i in range(last):
            a = bp[i]
            b = bp[(i + 1) % n]
            seg = interpolate_bezier(a.co, a.handle_right, b.handle_left, b.co, res)
            pts.extend((v.x, v.y) for v in seg[:-1])  # drop shared endpoint
    finally:
        cu = obj.data if obj else None
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        if cu and cu.users == 0:
            bpy.data.curves.remove(cu)
    _OVERSTOOL_PROFILE_POLY_CACHE = pts
    return pts


# ---------------------------------------------------------------------------
# Bottom-rail decorative profile cut (Beckony / Heritage / ... valance).
# A closed 2D Bezier authored with the decorative detail confined to the two
# ENDS and a flat horizontal middle. At apply time the ends stay FIXED and only
# the flat middle stretches to the rail length (3-slice), so the same profile
# fits any width with identical end details. Profiles are the '* Cutter.blend'
# curves in face_frame_assets/profiles. See _apply_bottom_rail_profile.
# ---------------------------------------------------------------------------
PART_ROLE_BOTTOM_RAIL_PROFILE_CUTTER = 'BOTTOM_RAIL_PROFILE_CUTTER'
BOTTOM_RAIL_PROFILE_CUT_MOD_NAME = 'Bottom Rail Profile Cut'
BOTTOM_RAIL_PROFILE_END_MARGIN = inch(2.0)  # flat, uncut rail left at each end
_BOTTOM_RAIL_PROFILE_ARCH = 'ARCH'          # procedural smooth-arch option (no blend)
BOTTOM_RAIL_PROFILE_ARCH_RISE = inch(2.0)   # arch height at the centre
_BOTTOM_RAIL_PROFILE_SUFFIX = ' Cutter.blend'
_BOTTOM_RAIL_PROFILE_POLY_CACHE = {}   # profile_id -> list[(x, y)] meters


def bottom_rail_profile_dir():
    return os.path.join(os.path.dirname(__file__), 'face_frame_assets', 'profiles')


def _bottom_rail_profile_poly(profile_id):
    """Sampled closed-loop (x, y) outline (meters) for a profile id, cached.
    Same depsgraph-free Bezier sampling as _overstool_profile_poly."""
    if profile_id in _BOTTOM_RAIL_PROFILE_POLY_CACHE:
        return _BOTTOM_RAIL_PROFILE_POLY_CACHE[profile_id]
    from mathutils.geometry import interpolate_bezier
    blend = os.path.join(bottom_rail_profile_dir(), profile_id + '.blend')
    if not os.path.exists(blend):
        return []
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.objects = [profile_id] if profile_id in src.objects else list(src.objects)
    obj = next((o for o in bpy.data.objects if o not in before), None)
    pts = []
    try:
        sp = obj.data.splines[0]
        bp = sp.bezier_points
        n = len(bp)
        res = max(12, obj.data.resolution_u)
        last = n if sp.use_cyclic_u else n - 1
        for i in range(last):
            a = bp[i]
            b = bp[(i + 1) % n]
            seg = interpolate_bezier(a.co, a.handle_right, b.handle_left, b.co, res)
            pts.extend((v.x, v.y) for v in seg[:-1])
    finally:
        cu = obj.data if obj else None
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        if cu and cu.users == 0:
            bpy.data.curves.remove(cu)
    _BOTTOM_RAIL_PROFILE_POLY_CACHE[profile_id] = pts
    return pts


def _bottom_rail_profile_stretched(poly, target_len):
    """3-slice the profile to target_len. Seams are the x-range of the flat top
    edge (points at max Y): keep the LEFT detail (x <= left_seam) fixed,
    translate the RIGHT detail (x >= right_seam) by (target_len - ref_len), and
    stretch the flat middle between them. Returns the remapped [(x, y)], or None
    when the rail is too short to hold both end details."""
    if not poly:
        return None
    max_y = max(y for _, y in poly)
    ref_len = max(x for x, _ in poly)
    top_x = [x for x, y in poly if abs(y - max_y) < 1e-4]
    if not top_x:
        return None
    left_seam, right_seam = min(top_x), max(top_x)
    right_detail = ref_len - right_seam
    if target_len <= left_seam + right_detail:
        return None
    delta = target_len - ref_len
    mid_old = right_seam - left_seam
    mid_new = mid_old + delta
    out = []
    for x, y in poly:
        if x <= left_seam:
            nx = x
        elif x >= right_seam:
            nx = x + delta
        elif mid_old > 1e-9:
            nx = left_seam + (x - left_seam) * (mid_new / mid_old)
        else:
            nx = x
        out.append((nx, y))
    return out


def _bottom_rail_arch_poly(chord, rise=None, segments=48):
    """Closed (x, y) loop for a smooth arched bottom-rail cut spanning x in
    [0, chord]: the TOP edge is a circular arc rising `rise` at the centre from
    y=0 at both ends; the bottom edge is flat just below y=0 so the cut clears
    the rail's bottom edge. Chord = the arch's span; a wider rail flattens the
    arc (fixed rise, larger radius). Returns None for a non-positive span."""
    if rise is None:
        rise = BOTTOM_RAIL_PROFILE_ARCH_RISE
    if chord <= 0.0 or rise <= 0.0:
        return None
    half = chord / 2.0
    radius = (half * half + rise * rise) / (2.0 * rise)
    cx, cy = half, rise - radius
    below = -inch(0.25)
    top = []
    for i in range(segments + 1):
        x = chord * i / segments
        dx = x - cx
        top.append((x, cy + math.sqrt(max(0.0, radius * radius - dx * dx))))
    return top + [(chord, below), (0.0, below)]


# Baseline rotation_euler.z for parts that live in the face frame plane.
# Recalc adds face_frame_angle on top so they rotate with the angled
# FF plane in angled mode; with theta = 0 the values match the build-
# time rotations and there's no behavior change for square cabinets.
# Bay cages are handled separately in _update_bay_cage (no baseline; the
# FF angle IS the rotation).
FF_ROTATION_BASELINE_Z = {
    PART_ROLE_LEFT_STILE:        math.pi / 2,
    PART_ROLE_RIGHT_STILE:       math.pi / 2,
    PART_ROLE_LEFT_REFRIG_STILE:  math.pi / 2,
    PART_ROLE_RIGHT_REFRIG_STILE: math.pi / 2,
    PART_ROLE_FRONT_DROP_FILLER: math.pi / 2,
    PART_ROLE_TOP_RAIL:          0.0,
    PART_ROLE_BOTTOM_RAIL:       0.0,
    PART_ROLE_TOE_KICK_SUBFRONT: 0.0,
    PART_ROLE_FINISH_TOE_KICK:   0.0,
    PART_ROLE_BLIND_PANEL_LEFT:  math.pi / 2,
    PART_ROLE_BLIND_PANEL_RIGHT: math.pi / 2,
}


# ---------------------------------------------------------------------------
# Bay cage
# ---------------------------------------------------------------------------
class FaceFrameBay(GeoNodeCage):
    """Bay cage: a child of a FaceFrameCabinet that defines one bay's volume.
    Phase 3b populates bay contents (face frame members, openings)."""

    def create(self, name="Bay"):
        super().create(name)
        self.obj[TAG_BAY_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_bay_commands'
        self.obj.display_type = 'WIRE'


# ---------------------------------------------------------------------------
# Opening cage
# ---------------------------------------------------------------------------
class FaceFrameOpening(GeoNodeCage):
    """Opening cage: a child of a FaceFrameBay that defines one face frame
    opening's volume. Each bay starts with a single opening filling its
    face frame opening; splitter operations subdivide a bay by adding
    more openings.

    The cage is positioned in the face frame plane (Y depth = fft) and
    spans the opening width / height between the bay's bounding stiles
    and rails. Doors, drawer fronts, and pullouts attach to the opening
    and overlay it by the opening's per-side overlay values (or the
    cabinet defaults when an overlay side is locked).
    """

    def create(self, name="Opening"):
        super().create(name)
        self.obj[TAG_OPENING_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_opening_commands'
        self.obj.display_type = 'WIRE'


class FaceFrameInteriorRegion(GeoNodeCage):
    """Interior tree leaf cage. A wireframe box inside an opening that
    represents one region of the interior split tree. Selectable in the
    viewport; the panel uses the active region to drive which leaf's
    interior_items are shown / edited.
    """

    def create(self, name="Region"):
        super().create(name)
        self.obj[TAG_INTERIOR_REGION] = True
        self.obj.display_type = 'WIRE'


# ---------------------------------------------------------------------------
# Tree cloning (used by insert_bay to copy a bay's contents)
# ---------------------------------------------------------------------------
def _copy_property_group(src, dst, skip=()):
    """Copy every writable, non-pointer field from one PropertyGroup to
    another, recursing into nested CollectionProperty members. `skip` is
    a set of identifiers to leave untouched on dst. Pointer props are
    skipped (none of the face frame PGs carry them today; the guard is
    defensive against future additions)."""
    for prop in src.bl_rna.properties:
        ident = prop.identifier
        if ident == 'rna_type' or ident in skip or prop.is_readonly:
            continue
        if prop.type == 'POINTER':
            continue
        if prop.type == 'COLLECTION':
            dst_coll = getattr(dst, ident)
            dst_coll.clear()
            for src_item in getattr(src, ident):
                _copy_property_group(src_item, dst_coll.add())
            continue
        try:
            setattr(dst, ident, getattr(src, ident))
        except (AttributeError, TypeError):
            pass


def _clone_interior_tree_node(src_node, new_parent):
    """Recursively clone an opening's interior tree node - a region leaf
    cage or an interior-split Empty - under new_parent. Carcass interior
    parts are not cloned; the recalc rebuilds those from the copied
    PropertyGroups."""
    if src_node.get(TAG_INTERIOR_REGION):
        new_leaf = FaceFrameInteriorRegion()
        new_leaf.create('Region')
        new_leaf.obj.parent = new_parent
        ici = src_node.get('hb_interior_child_index')
        if ici is not None:
            new_leaf.obj['hb_interior_child_index'] = ici
        _copy_property_group(
            src_node.face_frame_interior_region,
            new_leaf.obj.face_frame_interior_region,
        )
        return new_leaf.obj

    if src_node.get(TAG_INTERIOR_SPLIT_NODE):
        split_obj = bpy.data.objects.new('Interior Split', None)
        bpy.context.scene.collection.objects.link(split_obj)
        split_obj.empty_display_type = 'PLAIN_AXES'
        split_obj.empty_display_size = 0.001
        split_obj[TAG_INTERIOR_SPLIT_NODE] = True
        split_obj.parent = new_parent
        ici = src_node.get('hb_interior_child_index')
        if ici is not None:
            split_obj['hb_interior_child_index'] = ici
        _copy_property_group(
            src_node.face_frame_interior_split,
            split_obj.face_frame_interior_split,
        )
        children = sorted(
            [c for c in src_node.children
             if c.get(TAG_INTERIOR_REGION)
             or c.get(TAG_INTERIOR_SPLIT_NODE)],
            key=lambda c: c.get('hb_interior_child_index', 0),
        )
        for c in children:
            _clone_interior_tree_node(c, split_obj)
        return split_obj
    return None


def _clone_bay_tree_node(src_node, new_parent, opening_counter):
    """Recursively clone a bay's interior tree node - an opening cage or
    a split-node Empty - under new_parent. opening_counter is a one-item
    list used as a mutable per-bay counter so cloned openings get fresh
    sequential opening_index values. Fronts, pulls, and carcass parts
    are not cloned: the recalc rebuilds those from the copied front_type
    plus the cabinet style."""
    if src_node.get(TAG_OPENING_CAGE):
        new_op = FaceFrameOpening()
        new_op.create('Opening')
        new_op.obj.parent = new_parent
        idx = opening_counter[0]
        opening_counter[0] += 1
        new_op.obj['hb_opening_index'] = idx
        # opening_index is the within-bay counter, reassigned here; every
        # other opening field (front_type, overlays, interior_items, ...)
        # is copied verbatim so the new bay matches the anchor.
        _copy_property_group(
            src_node.face_frame_opening,
            new_op.obj.face_frame_opening,
            skip=('opening_index',),
        )
        new_op.obj.face_frame_opening.opening_index = idx
        sci = src_node.get('hb_split_child_index')
        if sci is not None:
            new_op.obj['hb_split_child_index'] = sci
        interior_root = solver._interior_tree_root(src_node)
        if interior_root is not None:
            _clone_interior_tree_node(interior_root, new_op.obj)
        return new_op.obj

    if src_node.get(TAG_SPLIT_NODE):
        split_obj = bpy.data.objects.new('Split Node', None)
        bpy.context.scene.collection.objects.link(split_obj)
        split_obj.empty_display_type = 'PLAIN_AXES'
        split_obj.empty_display_size = 0.001
        split_obj[TAG_SPLIT_NODE] = True
        split_obj.parent = new_parent
        sci = src_node.get('hb_split_child_index')
        if sci is not None:
            split_obj['hb_split_child_index'] = sci
        _copy_property_group(
            src_node.face_frame_split, split_obj.face_frame_split)
        children = sorted(
            [c for c in src_node.children
             if c.get(TAG_OPENING_CAGE) or c.get(TAG_SPLIT_NODE)],
            key=lambda c: c.get('hb_split_child_index', 0),
        )
        for c in children:
            _clone_bay_tree_node(c, split_obj, opening_counter)
        return split_obj
    return None


# ---------------------------------------------------------------------------
# Base cabinet class
# ---------------------------------------------------------------------------
class FaceFrameCabinet(GeoNodeCage):
    # When True, the place_cabinet modal pins bay_qty=1 and disables
    # fill-to-gap behavior. Used for single-unit products like sinks
    # where tiling across a wall doesn't make sense.
    single_placement = False

    """Base class for all face frame cabinets.

    No drivers. All dimensions flow through the recalculate() method which
    reads from the cabinet's face_frame_cabinet PropertyGroup and writes
    dimensions/positions to all child parts.
    """

    default_width = inch(36)
    default_height = inch(34.5)
    default_depth = inch(24)
    default_cabinet_type = 'BASE'
    # Optional floor->bottom mount height for uppers at placement. None =
    # use the scene wall-cabinet location; a subclass may pin a value
    # (read by ops_placement._upper_mount_z).
    default_z_location = None

    # =====================================================================
    # Construction
    # =====================================================================
    def create_cabinet_root(self, name):
        """Create the cabinet's top-level cage object."""
        super().create(name)

        self.obj[TAG_CABINET_CAGE] = True
        self.obj['CABINET_TYPE'] = self.default_cabinet_type
        self.obj['CLASS_NAME'] = self.__class__.__name__
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_cabinet_commands'
        self.obj.display_type = 'WIRE'

        # Mirror Y on the cabinet cage so the wireframe extrudes in -Y from
        # origin, matching the convention used by all child parts.
        self.set_input('Mirror Y', True)

        # Initialize the object-level PropertyGroup. Note: setting the
        # width/height/depth here will fire their update callbacks, which
        # call recalculate(). At this point parts don't exist yet, so the
        # recalc just sets the cage Dim X/Y/Z and returns - safe.
        scene = bpy.context.scene
        cab_props = self.obj.face_frame_cabinet
        cab_props.cabinet_type = self.default_cabinet_type

        # Type-specific top scribe defaults: amount the carcass top is
        # held down from bay_top_z. Uppers get a small cosmetic gap;
        # talls get a larger one for ceiling scribing on the side.
        # Sides drop with the carcass top unless flagged finished.
        cab_props.top_scribe = {
            'UPPER': inch(0.125),
            'TALL':  inch(0.5),
        }.get(self.default_cabinet_type, 0.0)

        # Uppers sit at the back of a corner with shallower carcasses, so
        # the blind amount default tracks Upper depth conventions (12") vs
        # the standard 24" Base/Tall default seeded by the property declaration.
        if self.default_cabinet_type == 'UPPER':
            cab_props.blind_amount_left = inch(12.0)
            cab_props.blind_amount_right = inch(12.0)

        if hasattr(scene, 'hb_face_frame'):
            ff_scene = scene.hb_face_frame
            cab_props.left_stile_width = ff_scene.ff_end_stile_width
            cab_props.right_stile_width = ff_scene.ff_end_stile_width
            cab_props.top_rail_width = ff_scene.ff_top_rail_width
            cab_props.bottom_rail_width = ff_scene.ff_bottom_rail_width
            cab_props.face_frame_thickness = ff_scene.ff_face_frame_thickness

        # Set dimensions last; this fires the update path
        cab_props.width = self.default_width
        cab_props.height = self.default_height
        cab_props.depth = self.default_depth

    def create_carcass(self, has_toe_kick, bay_qty=1):
        """Create the 5-part carcass + face frame end stiles + N bay cages
        + N-1 mid stiles. Initial rail segments are computed and created
        in the trailing recalculate() call.

        The whole body runs under _RECALCULATING + _DISTRIBUTING_WIDTHS so
        that prop assignments during initialization don't trigger nested
        recalcs or auto-lock the bay widths. The single recalculate() after
        the guard release does the layout once with all props in place.
        """
        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            self._build_carcass_parts(bay_qty)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        # All parts and props in place - run the layout once.
        self.recalculate()

    # =====================================================================
    # Insert / Delete bay (structural mutation)
    # =====================================================================
    def insert_bay(self, anchor_index, direction):
        """Insert a new bay relative to an existing one.

        anchor_index: index of the existing bay we're inserting next to.
        direction: 'BEFORE' (new bay takes anchor's slot, anchor shifts
        right) or 'AFTER' (new bay goes one past anchor, everything
        beyond shifts right).

        Adds one bay object (with a single fresh opening), one
        mid_stile_widths entry, one mid stile part, and a slot-0 / slot-1
        mid div pair. Existing bay / mid stile / mid div parts whose
        index sits at or past the insertion point have their hb_*_index
        bumped by one. width=0 + unlock_width=False on the new bay so
        the redistributor immediately gives it an equal share.
        """
        bays = self._sorted_bays()
        if not bays:
            return
        anchor_index = max(0, min(anchor_index, len(bays) - 1))
        # Hold the anchor bay's object ref before the reindex pass. The
        # ref is stable across reindexing (only its hb_bay_index prop
        # changes), so the new bay can clone its tree afterwards.
        anchor_bay = bays[anchor_index]
        new_bay_index = anchor_index if direction == 'BEFORE' else anchor_index + 1
        # Inserting AT new_bay_index means existing bays at new_bay_index
        # and beyond shift up by one. The new mid-stile sits at gap
        # new_bay_index - 1 if inserting at position > 0, else at gap 0.
        # Concretely: if new_bay_index < new_bay_count - 1 there's a gap
        # to the right of the new bay; else gap to the left.
        new_gap_index = new_bay_index - 1 if new_bay_index > 0 else 0
        # When inserting at position > 0 the new gap sits BETWEEN the
        # bay-to-the-left and the new bay. When inserting at position 0
        # (BEFORE bay 0) the new gap sits between the new bay and old
        # bay 0, which is gap 0 in the new numbering. Either way, gap
        # ranges shift up by one for any old gap whose index >= new_gap_index.

        cab_props = self.obj.face_frame_cabinet
        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            # 1) Reindex existing bays at/after new_bay_index.
            for bay_obj in self._sorted_bays():
                idx = bay_obj.get('hb_bay_index', 0)
                if idx >= new_bay_index:
                    bay_obj['hb_bay_index'] = idx + 1
                    bay_obj.face_frame_bay.bay_index = idx + 1

            # 2) Reindex existing mid-stile / mid-div parts at/after new_gap_index.
            for child in self._sorted_mid_parts():
                idx = child.get('hb_mid_stile_index', 0)
                if idx >= new_gap_index:
                    child['hb_mid_stile_index'] = idx + 1

            # 3) Insert mid_stile_widths entry at new_gap_index by
            #    add()-then-shuffle, since CollectionProperty has no
            #    insert(at). Shift values from new_gap_index forward.
            self._insert_mid_stile_width_entry(new_gap_index, inch(2.0))

            # 4) Build the new bay object + opening.
            new_bay = self._create_bay_at(new_bay_index)

            # 4b) Replace the new bay's placeholder opening with a deep
            #     copy of the anchor bay's tree (openings, splits, front
            #     types, overlays, interior items / interior tree). Bay-
            #     level physical props stay at _create_bay_at defaults so
            #     the redistributor still gives the new bay an equal
            #     width share. Fronts / pulls are rebuilt by the recalc.
            anchor_roots = [c for c in anchor_bay.children
                            if c.get(TAG_OPENING_CAGE)
                            or c.get(TAG_SPLIT_NODE)]
            if anchor_roots:
                for placeholder in [c for c in new_bay.children
                                    if c.get(TAG_OPENING_CAGE)
                                    or c.get(TAG_SPLIT_NODE)]:
                    for d in list(placeholder.children_recursive):
                        bpy.data.objects.remove(d, do_unlink=True)
                    bpy.data.objects.remove(placeholder, do_unlink=True)
                _clone_bay_tree_node(anchor_roots[0], new_bay, [0])

            # 5) Build the new mid-stile + mid-div pair at new_gap_index.
            self._create_mid_parts_at(new_gap_index)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        # Route through the module-level wrapper, not the bare
        # recalculate(): the wrapper also runs _reapply_cabinet_style,
        # which re-adds the per-front door-style modifier the wipe-and-
        # rebuild recalc strips. Calling self.recalculate() directly
        # would leave every front rendering as a slab.
        recalculate_face_frame_cabinet(self.obj)
        return new_bay

    def delete_bay(self, bay_index):
        """Delete the bay at bay_index. Refuses if it would leave zero
        bays. Cleans up the bay's subtree (openings, fronts, pulls,
        interior items), removes one gap (mid_stile_widths entry plus
        the matching mid-stile and mid-div pair), and reindexes the
        rest. When deleting bay i:
          - if i < n_bays - 1: gap i is removed (right-of-bay)
          - else (last bay): gap n_gaps - 1 is removed (left-of-bay)
        """
        bays = self._sorted_bays()
        if len(bays) <= 1:
            return False
        bay_index = max(0, min(bay_index, len(bays) - 1))
        target_bay = bays[bay_index]

        n_bays_before = len(bays)
        n_gaps_before = max(0, n_bays_before - 1)
        if bay_index < n_bays_before - 1:
            removed_gap_index = bay_index
        else:
            removed_gap_index = n_gaps_before - 1

        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            # 1) Wipe the bay's entire subtree (openings -> fronts ->
            #    pulls -> interior items, plus the bay cage itself).
            for descendant in list(target_bay.children_recursive):
                bpy.data.objects.remove(descendant, do_unlink=True)
            bpy.data.objects.remove(target_bay, do_unlink=True)

            # 2) Remove mid-stile + mid-div pair at removed_gap_index.
            for child in list(self._sorted_mid_parts()):
                if child.get('hb_mid_stile_index', 0) == removed_gap_index:
                    bpy.data.objects.remove(child, do_unlink=True)

            # 3) Remove the mid_stile_widths entry at removed_gap_index.
            self._remove_mid_stile_width_entry(removed_gap_index)

            # 4) Reindex remaining bays past bay_index down by one.
            for bay_obj in self._sorted_bays():
                idx = bay_obj.get('hb_bay_index', 0)
                if idx > bay_index:
                    bay_obj['hb_bay_index'] = idx - 1
                    bay_obj.face_frame_bay.bay_index = idx - 1

            # 5) Reindex remaining mid parts past removed_gap_index down
            #    by one.
            for child in self._sorted_mid_parts():
                idx = child.get('hb_mid_stile_index', 0)
                if idx > removed_gap_index:
                    child['hb_mid_stile_index'] = idx - 1
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        # Route through the wrapper so _reapply_cabinet_style re-adds
        # the per-front door-style modifiers the rebuild strips.
        recalculate_face_frame_cabinet(self.obj)
        return True

    # ----- Helpers used by insert_bay / delete_bay -----------------------
    def _sorted_bays(self):
        return sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )

    def _sorted_mid_parts(self):
        """Cabinet children that participate in gap indexing: mid-stile
        plus the slot-0 / slot-1 mid-div pair per gap."""
        roles = (PART_ROLE_MID_STILE, PART_ROLE_MID_DIVISION)
        return sorted(
            [c for c in self.obj.children if c.get('hb_part_role') in roles],
            key=lambda c: (c.get('hb_mid_stile_index', 0),
                           0 if c.get('hb_part_role') == PART_ROLE_MID_STILE else 1,
                           c.get('hb_mid_div_slot', 0)),
        )

    def _insert_mid_stile_width_entry(self, index, width_value):
        """Insert a mid_stile_widths entry by add()+ripple-shift, since
        CollectionProperty doesn't expose insert-at. After this the
        entry at `index` carries width_value (and zeroed extends)."""
        coll = self.obj.face_frame_cabinet.mid_stile_widths
        coll.add()
        n = len(coll)
        for i in range(n - 2, index - 1, -1):
            coll[i + 1].width = coll[i].width
            coll[i + 1].extend_up_amount = coll[i].extend_up_amount
            coll[i + 1].extend_down_amount = coll[i].extend_down_amount
        coll[index].width = width_value
        coll[index].extend_up_amount = 0.0
        coll[index].extend_down_amount = 0.0

    def _remove_mid_stile_width_entry(self, index):
        coll = self.obj.face_frame_cabinet.mid_stile_widths
        n = len(coll)
        for i in range(index, n - 1):
            coll[i].width = coll[i + 1].width
            coll[i].extend_up_amount = coll[i + 1].extend_up_amount
            coll[i].extend_down_amount = coll[i + 1].extend_down_amount
        coll.remove(n - 1)

    def _create_bay_at(self, bay_index):
        """Build a fresh bay + single opening with hb_bay_index set.
        Width=0 + unlock_width=False -> recalc redistributor gives it an
        equal share among unlocked bays. Other defaults pulled from
        cabinet props (matching the initial _build_carcass_parts path).
        """
        cab_props = self.obj.face_frame_cabinet
        bay = FaceFrameBay()
        bay.create(f'Bay {bay_index + 1}')
        bay.obj.parent = self.obj
        bay.obj['hb_bay_index'] = bay_index
        bp = bay.obj.face_frame_bay
        bp.bay_index = bay_index
        bp.width = 0.0   # redistributor fills it
        # See _build_carcass_parts for bay.height / kick_height semantics.
        bp.height = cab_props.height
        bp.depth = cab_props.depth
        bp.kick_height = (cab_props.toe_kick_height
                          if self._has_toe_kick() else 0.0)
        bp.top_offset = 0.0
        bp.top_rail_width = cab_props.top_rail_width
        bp.bottom_rail_width = cab_props.bottom_rail_width

        opening = FaceFrameOpening()
        opening.create('Opening 1')
        opening.obj.parent = bay.obj
        opening.obj['hb_opening_index'] = 0
        opening.obj.face_frame_opening.opening_index = 0
        opening.obj.face_frame_opening.front_type = (
            default_front_type_for_root(self.obj)
        )
        return bay.obj

    def _create_mid_parts_at(self, gap_index):
        """Build a mid stile and a slot-0 / slot-1 mid div pair at
        gap_index. Mirrors the initial loop in _build_carcass_parts."""
        mid_stile = CabinetPart()
        mid_stile.create(f'Mid Stile {gap_index + 1}')
        mid_stile.obj.parent = self.obj
        mid_stile.obj['hb_part_role'] = PART_ROLE_MID_STILE
        mid_stile.obj['CABINET_PART'] = True
        mid_stile.obj['hb_mid_stile_index'] = gap_index
        mid_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        mid_stile.obj.rotation_euler.y = math.radians(-90)
        mid_stile.obj.rotation_euler.z = math.radians(90)
        mid_stile.set_input('Mirror Y', True)
        mid_stile.set_input('Mirror Z', True)

        # Face-frame-only roots (panels / applied panels) have no carcass,
        # so they get the mid stile but never mid-division partitions or
        # partition skins. Mirrors the guard in _build_carcass_parts;
        # without it insert_bay (used by the applied-panel split) seeds
        # carcass parts onto panels that shouldn't have them.
        if not self._has_carcass():
            return

        for slot in (0, 1):
            mid_div = CabinetPart()
            mid_div.create(f'Mid Division {gap_index + 1}.{slot}')
            mid_div.obj.parent = self.obj
            mid_div.obj['hb_part_role'] = PART_ROLE_MID_DIVISION
            mid_div.obj['CABINET_PART'] = True
            mid_div.obj['hb_mid_stile_index'] = gap_index
            mid_div.obj['hb_mid_div_slot'] = slot
            mid_div.obj.rotation_euler.y = math.radians(-90)
            mid_div.set_input('Mirror Y', True)
            mid_div.set_input('Mirror Z', True)
            if slot == 1:
                mid_div.obj.hide_viewport = True
                mid_div.obj.hide_render = True
            else:
                notch_front = mid_div.add_part_modifier(
                    'CPM_CORNERNOTCH', 'Notch Top Front')
                notch_front.set_input('Flip X', True)
                notch_front.set_input('Flip Y', True)
                notch_front.mod.show_viewport = False
                notch_front.mod.show_render = False
                notch_back = mid_div.add_part_modifier(
                    'CPM_CORNERNOTCH', 'Notch Top Back')
                notch_back.set_input('Flip X', True)
                notch_back.set_input('Flip Y', False)
                notch_back.mod.show_viewport = False
                notch_back.mod.show_render = False

        # Partition skins: two slots per gap (slot 0 = bottom step,
        # slot 1 = top step, Upper/Tall only). Both start hidden;
        # recalc reveals + sizes them based on partition_skin_panels.
        for slot in (0, 1):
            skin = CabinetPart()
            skin.create(f'Partition Skin {gap_index + 1}.{slot}')
            skin.obj.parent = self.obj
            skin.obj['hb_part_role'] = PART_ROLE_PARTITION_SKIN
            skin.obj['CABINET_PART'] = True
            skin.obj['hb_mid_stile_index'] = gap_index
            skin.obj['hb_partition_skin_slot'] = slot
            skin.obj.rotation_euler.y = math.radians(-90)
            skin.set_input('Mirror Y', True)
            skin.set_input('Mirror Z', True)
            skin.obj.hide_viewport = True
            skin.obj.hide_render = True

    def _build_carcass_parts(self, bay_qty):
        """Body of create_carcass, factored out so the guard wrapping above
        is easy to read. Creates carcass parts, end stiles, bay cages, and
        mid stile parts. Initializes per-bay PropertyGroups.
        """
        # ----- Carcass -----
        # Skipped for face-frame-only roots (panels). Bottom / top / back
        # are already segment-keyed and lazy; only the side panels are
        # created up-front and need the explicit gate.
        if self._has_carcass():
            left = CabinetPart()
            left.create('Left Side')
            left.obj.parent = self.obj
            left.obj['hb_part_role'] = PART_ROLE_LEFT_SIDE
            left.obj['CABINET_PART'] = True
            left.obj.rotation_euler.y = math.radians(-90)
            left.set_input('Mirror Y', True)
            left.set_input('Mirror Z', True)
            # Front-bottom corner notch for NOTCH toe kick type. Both
            # sides have Mirror Y = True so Flip Y = True targets the
            # front face. Flip X = False targets the bottom (origin end
            # of Length axis). Driven and toggled per recalc; defaults
            # off so FLUSH / FLOATING / uppers see no cut.
            l_notch = left.add_part_modifier('CPM_CORNERNOTCH', 'Notch Front Bottom')
            l_notch.set_input('Flip X', False)
            l_notch.set_input('Flip Y', True)
            l_notch.mod.show_viewport = False
            l_notch.mod.show_render = False

            right = CabinetPart()
            right.create('Right Side')
            right.obj.parent = self.obj
            right.obj['hb_part_role'] = PART_ROLE_RIGHT_SIDE
            right.obj['CABINET_PART'] = True
            right.obj.rotation_euler.y = math.radians(-90)
            right.set_input('Mirror Y', True)
            right.set_input('Mirror Z', False)
            r_notch = right.add_part_modifier('CPM_CORNERNOTCH', 'Notch Front Bottom')
            r_notch.set_input('Flip X', False)
            r_notch.set_input('Flip Y', True)
            r_notch.mod.show_viewport = False
            r_notch.mod.show_render = False

        # Bottom is segment-keyed; created lazily by _reconcile_carcass_bottoms.

        # Top is segment-keyed; created lazily by _reconcile_carcass_tops.

        # Back is segment-keyed; created lazily by _reconcile_carcass_backs.

        # ----- End stiles -----
        left_stile = CabinetPart()
        left_stile.create('Left End Stile')
        left_stile.obj.parent = self.obj
        left_stile.obj['hb_part_role'] = PART_ROLE_LEFT_STILE
        left_stile.obj['CABINET_PART'] = True
        left_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        left_stile.obj.rotation_euler.y = math.radians(-90)
        left_stile.obj.rotation_euler.z = math.radians(90)
        left_stile.set_input('Mirror Y', True)
        left_stile.set_input('Mirror Z', True)

        right_stile = CabinetPart()
        right_stile.create('Right End Stile')
        right_stile.obj.parent = self.obj
        right_stile.obj['hb_part_role'] = PART_ROLE_RIGHT_STILE
        right_stile.obj['CABINET_PART'] = True
        right_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        right_stile.obj.rotation_euler.y = math.radians(-90)
        right_stile.obj.rotation_euler.z = math.radians(90)
        right_stile.set_input('Mirror Y', False)
        right_stile.set_input('Mirror Z', True)

        # ----- Bay cages + bay-level prop initialization -----
        cab_props = self.obj.face_frame_cabinet
        bay_qty = max(1, int(bay_qty))
        equal_bay_width = (
            cab_props.width
            - cab_props.left_stile_width
            - cab_props.right_stile_width
            - (bay_qty - 1) * inch(2.0)
        ) / bay_qty

        for i in range(bay_qty):
            bay = FaceFrameBay()
            bay.create(f'Bay {i + 1}')
            bay.obj.parent = self.obj
            bay.obj['hb_bay_index'] = i
            bp = bay.obj.face_frame_bay
            bp.bay_index = i
            bp.width = equal_bay_width
            # bay.height runs floor to top of top rail. For base / tall
            # the kick lives inside this envelope at bay-local
            # [0, kick_height]; bay.kick_height is the floor-to-bottom-
            # rail distance, seeded from the cabinet default and held in
            # sync by _distribute_bay_kick_heights when locked.
            bp.height = cab_props.height
            bp.depth = cab_props.depth
            bp.kick_height = (cab_props.toe_kick_height
                              if self._has_toe_kick() else 0.0)
            bp.top_offset = 0.0
            bp.top_rail_width = cab_props.top_rail_width
            bp.bottom_rail_width = cab_props.bottom_rail_width

            # One opening per bay at create time - fills the bay's face
            # frame opening. Splitter operations subdivide a bay later by
            # adding more opening children.
            opening = FaceFrameOpening()
            opening.create('Opening 1')
            opening.obj.parent = bay.obj
            opening.obj['hb_opening_index'] = 0
            opening.obj.face_frame_opening.opening_index = 0
            opening.obj.face_frame_opening.front_type = (
                default_front_type_for_root(self.obj)
            )

        # ----- Mid stile parts + width collection (one per gap) -----
        cab_props.mid_stile_widths.clear()
        for i in range(bay_qty - 1):
            ms_entry = cab_props.mid_stile_widths.add()
            ms_entry.width = inch(2.0)

            mid_stile = CabinetPart()
            mid_stile.create(f'Mid Stile {i + 1}')
            mid_stile.obj.parent = self.obj
            mid_stile.obj['hb_part_role'] = PART_ROLE_MID_STILE
            mid_stile.obj['CABINET_PART'] = True
            mid_stile.obj['hb_mid_stile_index'] = i
            mid_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
            mid_stile.obj.rotation_euler.y = math.radians(-90)
            mid_stile.obj.rotation_euler.z = math.radians(90)
            mid_stile.set_input('Mirror Y', True)
            mid_stile.set_input('Mirror Z', True)

            # Mid Division panels: carcass partition behind this mid
            # stile. Skipped for face-frame-only roots (panels). Two
            # slots per gap so we can show one centered panel for
            # matching bay depths or two face-to-face panels for
            # differing depths without create/delete during recalc. Slot
            # 1 starts hidden; recalc toggles it based on the panel list
            # returned by solver.mid_division_panels.
            if not self._has_carcass():
                continue
            for slot in (0, 1):
                mid_div = CabinetPart()
                mid_div.create(f'Mid Division {i + 1}.{slot}')
                mid_div.obj.parent = self.obj
                mid_div.obj['hb_part_role'] = PART_ROLE_MID_DIVISION
                mid_div.obj['CABINET_PART'] = True
                mid_div.obj['hb_mid_stile_index'] = i
                mid_div.obj['hb_mid_div_slot'] = slot
                mid_div.obj.rotation_euler.y = math.radians(-90)
                mid_div.set_input('Mirror Y', True)
                mid_div.set_input('Mirror Z', True)
                if slot == 1:
                    mid_div.obj.hide_viewport = True
                    mid_div.obj.hide_render = True
                else:
                    # Slot 0 may need stretcher notches at top-front and
                    # top-back when this gap has a single shared panel
                    # AND the stretcher segment passes through. Two
                    # CPM_CORNERNOTCH modifiers are added once at build
                    # time; recalc drives their X / Y / Route Depth and
                    # toggles show_viewport based on solver flags.
                    #
                    # Local-axis mapping after rot Y=-90, Mirror Y=True,
                    # Mirror Z=True:
                    #   local +X (Length) -> world +Z  (panel vertical)
                    #   local +Y (Width)  -> world +Y  (back is local +Y end)
                    #   local +Z (Thick)  -> world +X
                    # CPM_CORNERNOTCH operates in local space with X
                    # cutting along Length (vertical depth from one X
                    # end), Y cutting along Width (horizontal depth from
                    # one Y end), Route Depth cutting along Thickness.
                    # Top corner -> Flip X = True (X-far end = top).
                    # Front corner (world -Y) -> Flip Y = True (the
                    # Mirror-Y-driven far end = front face).
                    # Back corner (world +Y, the local-Y origin face)
                    # -> Flip Y = False (default end).
                    notch_front = mid_div.add_part_modifier(
                        'CPM_CORNERNOTCH', 'Notch Top Front')
                    notch_front.set_input('Flip X', True)
                    notch_front.set_input('Flip Y', True)
                    notch_front.mod.show_viewport = False
                    notch_front.mod.show_render = False
                    notch_back = mid_div.add_part_modifier(
                        'CPM_CORNERNOTCH', 'Notch Top Back')
                    notch_back.set_input('Flip X', True)
                    notch_back.set_input('Flip Y', False)
                    notch_back.mod.show_viewport = False
                    notch_back.mod.show_render = False

            # Partition skins: two slots per gap (slot 0 = bottom step,
            # slot 1 = top step, Upper/Tall only). Both start hidden;
            # recalc reveals + sizes them based on partition_skin_panels.
            for slot in (0, 1):
                skin = CabinetPart()
                skin.create(f'Partition Skin {i + 1}.{slot}')
                skin.obj.parent = self.obj
                skin.obj['hb_part_role'] = PART_ROLE_PARTITION_SKIN
                skin.obj['CABINET_PART'] = True
                skin.obj['hb_mid_stile_index'] = i
                skin.obj['hb_partition_skin_slot'] = slot
                skin.obj.rotation_euler.y = math.radians(-90)
                skin.set_input('Mirror Y', True)
                skin.set_input('Mirror Z', True)
                skin.obj.hide_viewport = True
                skin.obj.hide_render = True

        # Rails and per-bay carcass bottoms get created lazily by the segment reconciliation step inside
        # recalculate(). No initial rail objects needed here.

    # =====================================================================
    # Calculators - dimension distribution among peers (bay widths)
    # =====================================================================
    def _distribute_bay_depths(self):
        """For each bay where unlock_depth is False, sync the bay's
        depth to the cabinet depth. Bays with unlock_depth=True keep
        their stored value, allowing per-bay overrides.
        """
        cab_props = self.obj.face_frame_cabinet
        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            if bp.unlock_depth:
                continue
            if abs(bp.depth - cab_props.depth) > 1e-6:
                bp.depth = cab_props.depth

    def _distribute_bay_heights(self):
        """Sync each bay's height to cabinet height when unlock_height
        is False. bay.height is the full vertical extent floor to top of
        top rail; the toe kick lives inside it for base / tall bays via
        bay.kick_height (handled by _distribute_bay_kick_heights).
        """
        cab_props = self.obj.face_frame_cabinet
        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if not bays:
            return
        target = cab_props.height
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            if bp.unlock_height:
                continue
            if abs(bp.height - target) > 1e-6:
                bp.height = target

    def _distribute_bay_kick_heights(self):
        """Sync each bay's kick_height to cabinet toe_kick_height when
        unlock_kick_height is False. Mirrors _distribute_bay_widths.
        Uppers (no toe kick) get 0.

        System writes are bracketed by _DISTRIBUTING_WIDTHS so the bay's
        kick_height update callback knows not to treat them as user edits
        and auto-lock the bay.
        """
        cab_props = self.obj.face_frame_cabinet
        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if not bays:
            return
        target = (cab_props.toe_kick_height
                  if self._has_toe_kick() else 0.0)
        _DISTRIBUTING_WIDTHS.add(id(self.obj))
        try:
            for bay_obj in bays:
                bp = bay_obj.face_frame_bay
                if bp.unlock_kick_height:
                    continue
                if abs(bp.kick_height - target) > 1e-6:
                    bp.kick_height = target
        finally:
            _DISTRIBUTING_WIDTHS.discard(id(self.obj))

    def _distribute_bay_rails(self):
        """Sync each bay's top / bottom rail width to the cabinet defaults
        unless the bay has the matching unlock_*_rail flag set. Mirrors
        _distribute_bay_depths: a locked bay follows the cabinet default,
        an unlocked bay holds its own per-bay rail override.
        """
        cab_props = self.obj.face_frame_cabinet
        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            if not bp.unlock_top_rail:
                if abs(bp.top_rail_width - cab_props.top_rail_width) > 1e-6:
                    bp.top_rail_width = cab_props.top_rail_width
            if not bp.unlock_bottom_rail:
                if abs(bp.bottom_rail_width - cab_props.bottom_rail_width) > 1e-6:
                    bp.bottom_rail_width = cab_props.bottom_rail_width

    def _distribute_bay_widths(self):
        """Redistribute available width among bays whose unlock_width is False.

        Runs at the top of recalculate() so that bay-width fields are up to
        date before the layout solver reads them. Bays with unlock_width=True
        hold their current width; bays with unlock_width=False each get an
        equal share of whatever width is left.

        System writes during this method are bracketed by _DISTRIBUTING_WIDTHS
        so the bay-width update callback knows not to auto-lock.
        """
        cab_props = self.obj.face_frame_cabinet

        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if not bays:
            return

        # Space taken by stiles
        consumed = cab_props.left_stile_width + cab_props.right_stile_width
        for i in range(min(len(bays) - 1, len(cab_props.mid_stile_widths))):
            consumed += cab_props.mid_stile_widths[i].width

        # Sum of locked bay widths
        locked_total = 0.0
        unlocked_bays = []
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            if bp.unlock_width:
                locked_total += bp.width
            else:
                unlocked_bays.append(bay_obj)

        if not unlocked_bays:
            return  # all bays locked, nothing to redistribute

        # In angled mode the face frame becomes the hypotenuse, so rails
        # and openings need to size against that length, not the cabinet's
        # world X width. Layout's face_frame_length helper would do this
        # but isn't built yet at this point in recalc, so reproduce the
        # same condition + math directly from cab_props.
        is_angled_single_bay = (
            cab_props.corner_type == 'NONE'
            and len(bays) == 1
            and (cab_props.unlock_left_depth or cab_props.unlock_right_depth)
        )
        if is_angled_single_bay:
            ld = (cab_props.left_depth if cab_props.unlock_left_depth
                  else cab_props.depth)
            rd = (cab_props.right_depth if cab_props.unlock_right_depth
                  else cab_props.depth)
            available_width = math.hypot(cab_props.width, ld - rd)
        else:
            # Mirror FaceFrameLayout.blind_offset_* coupling so the bay
            # share matches the FF area the solver will actually use.
            blind_left = (cab_props.blind_amount_left
                          if (cab_props.left_stile_type == 'BLIND'
                              and cab_props.blind_left
                              and cab_props.blind_amount_left > 0)
                          else 0.0)
            blind_right = (cab_props.blind_amount_right
                           if (cab_props.right_stile_type == 'BLIND'
                               and cab_props.blind_right
                               and cab_props.blind_amount_right > 0)
                           else 0.0)
            available_width = cab_props.width - blind_left - blind_right

        remainder = available_width - consumed - locked_total
        share = remainder / len(unlocked_bays)

        # Write shares to unlocked bays under the distribution guard so
        # callbacks from these writes don't trigger auto-lock.
        _DISTRIBUTING_WIDTHS.add(id(self.obj))
        try:
            for bay_obj in unlocked_bays:
                bp = bay_obj.face_frame_bay
                if abs(bp.width - share) > 1e-6:
                    bp.width = share
        finally:
            _DISTRIBUTING_WIDTHS.discard(id(self.obj))

    # =====================================================================
    # Layout / dimension propagation - source of truth is the prop group.
    # No drivers; the solver writes resolved values directly to parts.
    # =====================================================================
    def _distribute_split_sizes(self):
        """Redistribute sizes among siblings inside every split node in
        every bay's tree. Walks the tree top-down: at each split node,
        the parent FF opening dim along the split's axis is divided
        into (n - 1) splitter widths plus n child sizes; locked
        children hold their stored value, unlocked share the rest.

        Mirrors _distribute_bay_widths but operates per-bay-tree
        instead of per-cabinet. System writes go through the
        _DISTRIBUTING_WIDTHS guard so update callbacks know not to
        auto-lock.
        """
        cab_props = self.obj.face_frame_cabinet
        for bay_obj in [c for c in self.obj.children
                        if c.get(TAG_BAY_CAGE)]:
            bp = bay_obj.face_frame_bay
            roots = [c for c in bay_obj.children
                     if c.get(TAG_OPENING_CAGE)
                     or c.get(TAG_SPLIT_NODE)]
            if not roots:
                continue
            root = roots[0]
            # Bay's tree root has no size of its own; it fills the bay's
            # face frame opening rect. bp.height spans floor to top of
            # top rail, so subtract both rails AND kick_height to leave
            # the FF opening only (uppers carry kick_height = 0 so this
            # is a no-op there). Same correction applied in
            # _bay_root_reveals; without it the children sum to a total
            # that's too large by kick_height and the bottom child
            # overflows when laid out against cage_dim_z.
            ff_height = (bp.height - bp.top_rail_width
                         - bp.bottom_rail_width - bp.kick_height)
            ff_width = bp.width
            self._redistribute_split_node(root, ff_width, ff_height, cab_props)

    def _redistribute_split_node(self, node, parent_ff_width,
                                 parent_ff_height, cab_props):
        """If `node` is a split, redistribute among its children and
        recurse into each child. The parent_ff_* args describe the FF
        opening dim of the rect this node occupies (which is what its
        children share). Leaves end the recursion.
        """
        if not node.get(TAG_SPLIT_NODE):
            return
        sp = node.face_frame_split
        children = sorted(
            [c for c in node.children
             if c.get(TAG_OPENING_CAGE) or c.get(TAG_SPLIT_NODE)],
            key=lambda c: c.get('hb_split_child_index', 0),
        )
        if not children:
            return

        is_h = (sp.axis == 'H')
        parent_dim = parent_ff_height if is_h else parent_ff_width
        splitter_w = sp.splitter_width
        n_splitters = len(children) - 1

        locked_total = 0.0
        unlocked = []
        for c in children:
            size_val, unlock = self._read_node_size(c)
            if unlock:
                locked_total += size_val
            else:
                unlocked.append(c)

        # Vanity door rule: an unlocked child stamped SIZE_ROLE
        # 'VANITY_DOOR' takes its share plus VANITY_DOOR_EXTRA_WIDTH,
        # deducted from the pool first. Mirrors the geometry rule in
        # solver_face_frame._redistribute_sizes; both must agree or the
        # stored sizes drift from the built fronts.
        extra_total = sum(
            solver.VANITY_DOOR_EXTRA_WIDTH for c in unlocked
            if c.get('SIZE_ROLE') == 'VANITY_DOOR'
        )
        remainder = parent_dim - n_splitters * splitter_w - locked_total
        share = ((remainder - extra_total) / len(unlocked)) if unlocked else 0.0

        _DISTRIBUTING_WIDTHS.add(id(self.obj))
        try:
            for c in unlocked:
                extra = (solver.VANITY_DOOR_EXTRA_WIDTH
                         if c.get('SIZE_ROLE') == 'VANITY_DOOR' else 0.0)
                self._write_node_size(c, share + extra)
        finally:
            _DISTRIBUTING_WIDTHS.discard(id(self.obj))

        for c in children:
            size_val, _ = self._read_node_size(c)
            if is_h:
                child_w, child_h = parent_ff_width, size_val
            else:
                child_w, child_h = size_val, parent_ff_height
            self._redistribute_split_node(c, child_w, child_h, cab_props)

    def _read_node_size(self, obj):
        """Return (size, unlock_size) for any tree node (leaf opening
        or internal split node)."""
        if obj.get(TAG_OPENING_CAGE):
            op = obj.face_frame_opening
            return op.size, op.unlock_size
        if obj.get(TAG_SPLIT_NODE):
            sp = obj.face_frame_split
            return sp.size, sp.unlock_size
        return 0.0, False

    def _write_node_size(self, obj, value):
        """Write redistributed size to a tree node."""
        if obj.get(TAG_OPENING_CAGE):
            obj.face_frame_opening.size = value
        elif obj.get(TAG_SPLIT_NODE):
            obj.face_frame_split.size = value

    def recalculate(self):
        """Recompute all part dimensions and positions from props.

        Order:
        1. Sync cage Dim X/Y/Z (so the wireframe matches even if no parts)
        2. Build a FaceFrameLayout snapshot
        3. Compute top/bottom rail segments
        4. Reconcile rail objects against segments (create missing, delete obsolete)
        5. Walk all children and dispatch by role - write resolved geometry
        """
        cab_props = self.obj.face_frame_cabinet
        self.set_input('Dim X', cab_props.width)
        self.set_input('Dim Y', cab_props.depth)
        self.set_input('Dim Z', cab_props.height)

        # Depths and heights first - each bay's tree redistribution
        # reads bp.height to compute the available FF rect, and the
        # solver reads bp.depth for carcass parts.
        self._distribute_bay_depths()
        self._distribute_bay_heights()
        self._distribute_bay_kick_heights()
        # Rail widths follow the cabinet default unless a bay is unlocked.
        self._distribute_bay_rails()
        # Then the width calculator before the solver reads bay widths.
        self._distribute_bay_widths()
        # Then redistribute sizes inside each bay's tree of openings /
        # splits. Order matters: bay widths need to be settled first
        # because each bay's tree's available width comes from bp.width.
        self._distribute_split_sizes()

        layout = solver.FaceFrameLayout(self.obj)
        carcass_depth = solver.carcass_inner_depth(layout)
        # face_frame_angle is 0 for square cabinets, so the rotation
        # additions below are idempotent in the non-angled case.
        ff_theta = solver.face_frame_angle(layout)

        # Compute and reconcile rail segments before the dispatch loop
        top_segments = solver.top_rail_segments(layout)
        bottom_segments = solver.bottom_rail_segments(layout)
        self._reconcile_rails(PART_ROLE_TOP_RAIL, top_segments)
        self._reconcile_rails(PART_ROLE_BOTTOM_RAIL, bottom_segments)
        # Drop fillers: filler stiles in each front-dropped bay's open
        # band, fitting a farm sink / cooktop (keyed per bay + side).
        drop_filler_segs = solver.front_drop_filler_segments(layout)
        self._reconcile_front_drop_fillers(drop_filler_segs)

        # Carcass branch - skipped for face-frame-only roots (panels).
        # Empty segment lists make the dispatch loop's carcass branches
        # no-ops, since _build_carcass_parts also skipped creating those
        # children.
        if self._has_carcass():
            carcass_bottom_segs = solver.carcass_bottom_segments(layout)
            carcass_back_segs = solver.carcass_back_segments(layout)
            self._reconcile_carcass_bottoms(carcass_bottom_segs)
            self._reconcile_carcass_backs(carcass_back_segs)
            if self._has_toe_kick():
                kick_subfront_segs = solver.kick_subfront_segments(layout)
                self._reconcile_kick_subfronts(kick_subfront_segs)
                finish_kick_segs = solver.finish_kick_segments(layout)
                self._reconcile_finish_kicks(finish_kick_segs)
                self._ensure_corner_finish_kick(
                    PART_ROLE_LEFT_CORNER_FINISH_KICK, 'Finish Toe Kick Left')
                self._ensure_corner_finish_kick(
                    PART_ROLE_RIGHT_CORNER_FINISH_KICK, 'Finish Toe Kick Right')
                self._reconcile_mid_finish_kicks(layout)
                self._ensure_partition_skin_slot2(layout)
                self._ensure_kick_return(
                    PART_ROLE_LEFT_KICK_RETURN, 'Toe Kick Return Left',
                    mirror_z=True)
                self._ensure_kick_return(
                    PART_ROLE_RIGHT_KICK_RETURN, 'Toe Kick Return Right',
                    mirror_z=False)
                # Loose ladder sub-base. Always ensured (hidden in the
                # dispatch loop unless toe_kick_type == 'LOOSE'), so a
                # toe-kick-type change toggles visibility without
                # creating / destroying parts.
                self._ensure_loose_kick_part(
                    PART_ROLE_LOOSE_KICK_FRONT, 'Loose Kick Front',
                    kind='RAIL', mirror_z=True)
                self._ensure_loose_kick_part(
                    PART_ROLE_LOOSE_KICK_REAR, 'Loose Kick Rear',
                    kind='RAIL', mirror_z=True)
                self._ensure_loose_kick_part(
                    PART_ROLE_LOOSE_KICK_END_LEFT, 'Loose Kick End Left',
                    kind='END', mirror_z=True)
                self._ensure_loose_kick_part(
                    PART_ROLE_LOOSE_KICK_END_RIGHT, 'Loose Kick End Right',
                    kind='END', mirror_z=False)
            else:
                kick_subfront_segs = []
                finish_kick_segs = []
                self._reconcile_kick_subfronts([])
                self._reconcile_finish_kicks([])

            # Blind panels exist on every carcass-bearing cabinet (Base /
            # Tall / Upper / Lap Drawer). Hidden when stile type isn't
            # BLIND or the side's blind flag is False - the dispatch loop
            # toggles visibility per side.
            self._ensure_blind_panel(
                PART_ROLE_BLIND_PANEL_LEFT, 'Blind Panel Left', mirror_y=True)
            self._ensure_blind_panel(
                PART_ROLE_BLIND_PANEL_RIGHT, 'Blind Panel Right', mirror_y=False)

            # Top construction branches on cabinet type:
            #   BASE / LAP_DRAWER -> Front + Rear stretchers
            #   UPPER / TALL      -> Solid top panel
            # Cleanup the other style's parts in case of cabinet-type
            # change or migration from a previous architecture.
            if layout.uses_stretchers:
                front_stretcher_segs = solver.front_stretcher_segments(layout)
                rear_stretcher_segs = solver.rear_stretcher_segments(layout)
                self._cleanup_role(PART_ROLE_TOP)
                self._reconcile_stretchers(PART_ROLE_FRONT_STRETCHER, front_stretcher_segs)
                self._reconcile_stretchers(PART_ROLE_REAR_STRETCHER, rear_stretcher_segs)
                carcass_top_segs = []
            else:
                carcass_top_segs = solver.carcass_top_segments(layout)
                self._cleanup_role(PART_ROLE_FRONT_STRETCHER)
                self._cleanup_role(PART_ROLE_REAR_STRETCHER)
                self._reconcile_carcass_tops(carcass_top_segs)
                front_stretcher_segs = []
                rear_stretcher_segs = []
        else:
            carcass_bottom_segs = []
            carcass_back_segs = []
            carcass_top_segs = []
            front_stretcher_segs = []
            rear_stretcher_segs = []
            kick_subfront_segs = []
            finish_kick_segs = []

        top_seg_by_start = {s['start_bay']: s for s in top_segments}
        bot_seg_by_start = {s['start_bay']: s for s in bottom_segments}
        drop_filler_by_key = {(s['bay'], s['side']): s for s in drop_filler_segs}
        kick_seg_by_start = {s['start_bay']: s for s in kick_subfront_segs}
        finish_kick_seg_by_start = {s['start_bay']: s for s in finish_kick_segs}
        carc_bot_by_start = {s['start_bay']: s for s in carcass_bottom_segs}
        carc_back_by_start = {s['start_bay']: s for s in carcass_back_segs}
        front_str_by_start = {s['start_bay']: s for s in front_stretcher_segs}
        rear_str_by_start = {s['start_bay']: s for s in rear_stretcher_segs}
        carc_top_by_start = {s['start_bay']: s for s in carcass_top_segs}

        # Ensure every part in this cabinet carries a right-click menu.
        # Fronts (nested under openings, not direct children) and parts
        # built before the part menu existed get the shared part-commands
        # menu - without clobbering parts that already have a more
        # specific one (interior parts, etc.).
        for _part_obj in self.obj.children_recursive:
            if _part_obj.get('hb_part_role') and not _part_obj.get('MENU_ID'):
                _part_obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'

        for child in self.obj.children:
            role = child.get('hb_part_role')
            bay_index = child.get('hb_bay_index', 0)

            # Bay cage handling (no hb_part_role; identified by tag)
            if child.get(TAG_BAY_CAGE):
                self._update_bay_cage(child, layout, bay_index)
                continue

            if not role:
                continue

            # Manual / frozen parts opt out of the parametric rewrite.
            # IS_MANUAL_PART is set by hb_face_frame.make_part_editable
            # once the cutpart GN has been applied to real mesh: the user
            # has hand-edited this board, so its location / dims / rotation
            # / visibility are left exactly as they are. Skipped BEFORE the
            # FF rotation block so a frozen stile / rail isn't re-rotated.
            #
            # Self-heal: a part whose cutpart GN modifier is gone has been
            # applied (by make_part_editable, or by hand in the modifier
            # stack) and has no inputs to push - set_input would raise. It
            # is manual by construction, so stamp the flag and skip. This
            # keeps recalc crash-proof regardless of how a part was applied.
            if child.type == 'MESH':
                _mn = child.home_builder.mod_name
                if _mn and _mn not in child.modifiers:
                    child['IS_MANUAL_PART'] = True
            if child.get('IS_MANUAL_PART'):
                continue

            # FF plane rotation. Hits stiles, rails, and kick subfronts;
            # leaves other parts (sides, back, panels) at their built-in
            # rotation_euler. Idempotent in square mode (theta = 0).
            ff_baseline = FF_ROTATION_BASELINE_Z.get(role)
            if ff_baseline is not None:
                child.rotation_euler.z = ff_baseline + ff_theta

            part = GeoNodeCutpart(child)

            # ---- Carcass (sides shrink to leave room for the face frame at front) ----
            # End-side suppression: when the adjacent end bay has
            # remove_carcass set, the side panel becomes an orphan
            # (no back / bottom / top to attach to at that bay), so
            # hide it. The neighbouring bay's enclosure is provided by
            # the gap mid-division. remove_bottom is not enough to
            # warrant suppression - the carcass shell remains.
            if role == PART_ROLE_LEFT_SIDE:
                visible = not layout.bays[0].get('remove_carcass')
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.left_side_position(layout)
                length, width, thickness = solver.left_side_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)
                self._update_side_corner_notch(child, layout, 0)

            elif role == PART_ROLE_RIGHT_SIDE:
                last = layout.bay_count - 1
                visible = not layout.bays[last].get('remove_carcass')
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.right_side_position(layout)
                length, width, thickness = solver.right_side_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)
                self._update_side_corner_notch(child, layout, last)

            elif role == PART_ROLE_BOTTOM:
                seg = carc_bot_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['panel_dim_y'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_FRONT_STRETCHER:
                seg = front_str_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_REAR_STRETCHER:
                seg = rear_str_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_TOP:
                seg = carc_top_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['panel_dim_y'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_BACK:
                seg = carc_back_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['vertical_length'])
                part.set_input('Width', seg['horizontal_length'])
                part.set_input('Thickness', seg['thickness'])

            # ---- End stiles ----
            elif role == PART_ROLE_LEFT_STILE:
                pos = solver.left_end_stile_position(layout)
                length, width, thickness = solver.left_end_stile_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_RIGHT_STILE:
                pos = solver.right_end_stile_position(layout)
                length, width, thickness = solver.right_end_stile_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            # ---- Refrigerator 'stile in lieu of leg' (floor -> opening top) ----
            elif role == PART_ROLE_LEFT_REFRIG_STILE:
                visible = solver.has_refrig_stile(layout, 'LEFT')
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.left_refrig_stile_position(layout)
                length, width, thickness = solver.left_refrig_stile_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_RIGHT_REFRIG_STILE:
                visible = solver.has_refrig_stile(layout, 'RIGHT')
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.right_refrig_stile_position(layout)
                length, width, thickness = solver.right_refrig_stile_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            # ---- Rails (segment-keyed) ----
            elif role == PART_ROLE_TOP_RAIL:
                seg = top_seg_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_BOTTOM_RAIL:
                seg = bot_seg_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            # ---- Drop fillers (front-dropped sink / cooktop band) ----
            elif role == PART_ROLE_FRONT_DROP_FILLER:
                seg = drop_filler_by_key.get(
                    (child.get('hb_segment_start_bay'),
                     child.get('hb_drop_filler_side')))
                if seg is None:
                    continue
                child.location = seg['pos']
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_TOE_KICK_SUBFRONT:
                seg = kick_seg_by_start.get(child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_FINISH_TOE_KICK:
                seg = finish_kick_seg_by_start.get(
                    child.get('hb_segment_start_bay'))
                if seg is None:
                    continue
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_LEFT_CORNER_FINISH_KICK:
                visible = solver.has_left_corner_finish_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.left_corner_finish_kick_position(layout)
                length, width, thickness = solver.left_corner_finish_kick_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_RIGHT_CORNER_FINISH_KICK:
                visible = solver.has_right_corner_finish_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.right_corner_finish_kick_position(layout)
                length, width, thickness = solver.right_corner_finish_kick_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_MID_FINISH_KICK:
                gi = child.get('hb_mid_stile_index', 0)
                side = child.get('hb_mid_kick_side', 'LEFT')
                pos = solver.mid_finish_kick_position(layout, gi, side)
                dims = solver.mid_finish_kick_dims(layout, gi, side)
                if pos is None or dims is None:
                    child.hide_viewport = True
                    child.hide_render = True
                    continue
                child.hide_viewport = False
                child.hide_render = False
                child.location = pos
                length, width, thickness = dims
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_LEFT_KICK_RETURN:
                visible = solver.has_left_kick_return(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.left_kick_return_position(layout)
                length, width, thickness = solver.left_kick_return_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_RIGHT_KICK_RETURN:
                visible = solver.has_right_kick_return(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                pos = solver.right_kick_return_position(layout)
                length, width, thickness = solver.right_kick_return_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            # ---- Loose toe kick ladder (visible only for LOOSE) ----
            elif role == PART_ROLE_LOOSE_KICK_FRONT:
                visible = solver.has_loose_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                seg = solver.loose_kick_front_rail(layout)
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_LOOSE_KICK_REAR:
                visible = solver.has_loose_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                seg = solver.loose_kick_rear_rail(layout)
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_LOOSE_KICK_END_LEFT:
                visible = solver.has_loose_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                seg = solver.loose_kick_end(layout, 'LEFT')
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_LOOSE_KICK_END_RIGHT:
                visible = solver.has_loose_kick(layout)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                seg = solver.loose_kick_end(layout, 'RIGHT')
                child.location = (seg['x'], seg['y'], seg['z'])
                part.set_input('Length', seg['length'])
                part.set_input('Width', seg['width'])
                part.set_input('Thickness', seg['thickness'])

            elif role == PART_ROLE_BLIND_PANEL_LEFT:
                # Visible when the left end is a blind corner stile AND
                # the side's blind flag is on (an adjacent cabinet is
                # actually butted against this stile). Either condition
                # off and the panel hides without being deleted.
                visible = (cab_props.left_stile_type == 'BLIND'
                           and cab_props.blind_left
                           and cab_props.blind_amount_left > 0)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                z_origin, z_height = self._blind_panel_z_range()
                # Anchored at the LEFT endpoint of the FF outer plane,
                # offset back by face_frame_thickness so the panel sits
                # just behind the face frame. Length runs vertically
                # (cabinet interior height); Width runs +X by
                # blind_amount via Mirror Y=True (matches left stile);
                # Thickness extends +Y deeper into the cabinet body.
                child.location = (0.0,
                                  -cab_props.depth + cab_props.face_frame_thickness,
                                  z_origin)
                part.set_input('Length', z_height)
                part.set_input('Width', cab_props.blind_amount_left)
                part.set_input('Thickness', BLIND_PANEL_THICKNESS)

            elif role == PART_ROLE_BLIND_PANEL_RIGHT:
                visible = (cab_props.right_stile_type == 'BLIND'
                           and cab_props.blind_right
                           and cab_props.blind_amount_right > 0)
                child.hide_viewport = not visible
                child.hide_render = not visible
                if not visible:
                    continue
                z_origin, z_height = self._blind_panel_z_range()
                # Anchored at the RIGHT endpoint of the FF outer plane.
                # Mirror Y=False makes Width grow -X from this anchor
                # (matches right stile), so the panel reaches inboard
                # by blind_amount.
                child.location = (cab_props.width,
                                  -cab_props.depth + cab_props.face_frame_thickness,
                                  z_origin)
                part.set_input('Length', z_height)
                part.set_input('Width', cab_props.blind_amount_right)
                part.set_input('Thickness', BLIND_PANEL_THICKNESS)

            # ---- Mid stiles (gap-keyed) ----
            elif role == PART_ROLE_MID_STILE:
                # Backfill MENU_ID for cabinets created before right-click was added
                if not child.get('MENU_ID'):
                    child['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
                msi = child.get('hb_mid_stile_index', 0)
                if msi >= len(layout.mid_stiles):
                    child.hide_viewport = True
                    continue
                child.hide_viewport = False
                pos = solver.mid_stile_position(layout, msi)
                length, width, thickness = solver.mid_stile_dims(layout, msi)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_MID_DIVISION:
                msi = child.get('hb_mid_stile_index', 0)
                slot = child.get('hb_mid_div_slot', 0)
                panels = solver.mid_division_panels(layout, msi)
                # Pick the panel whose slot matches this child. Slot 0
                # is always present when the gap exists; slot 1 only
                # when bay depths differ (2-panel diff-depth case).
                panel = next((p for p in panels if p['slot'] == slot), None)
                if panel is None:
                    child.hide_viewport = True
                    child.hide_render = True
                    continue
                child.hide_viewport = False
                child.hide_render = False
                child.location = (panel['x'], panel['y'], panel['z'])
                part.set_input('Length',    panel['length'])
                part.set_input('Width',     panel['width'])
                part.set_input('Thickness', panel['thickness'])
                # Drive top stretcher notches (slot 0 only - slot 1 has
                # no notch modifiers and panel['notch_active'] is False
                # there anyway).
                self._update_mid_div_notches(child, panel)

            elif role == PART_ROLE_PARTITION_SKIN:
                msi = child.get('hb_mid_stile_index', 0)
                slot = child.get('hb_partition_skin_slot', 0)
                skins = solver.partition_skin_panels(layout, msi)
                skin = next((s for s in skins if s['slot'] == slot), None)
                if slot == 2:
                    # Slot 2 (floating finish) drops to the floor; notch its
                    # front-bottom to clear the toe-kick recess (off when the
                    # gap's mid stile is itself stile-to-floor).
                    self._drive_partition_skin_floor_notch(
                        child, layout, msi, skin)
                if skin is None:
                    child.hide_viewport = True
                    child.hide_render = True
                    continue
                child.hide_viewport = False
                child.hide_render = False
                child.location = (skin['x'], skin['y'], skin['z'])
                part.set_input('Length',    skin['length'])
                part.set_input('Width',     skin['width'])
                part.set_input('Thickness', skin['thickness'])

        # Spawn / resize / remove applied finished-end panels last so
        # they pick up the most recent cabinet dimensions. Skipped for
        # panel roots (a panel never carries another panel as its end).
        if self._has_carcass():
            self._reconcile_applied_panels(layout)
            self._reconcile_finished_back(layout)
            self._reconcile_flush_x_strips(layout)
            self._reconcile_full_overlay_stiles(layout)
            self._reconcile_textured_panels(layout)
            self._reconcile_bay_finish_panels(layout)
            # Run a FINISHED carcass side past the cabinet back by its
            # per-side extend. The applied / textured side families carry
            # their own overhang above; the FINISHED side has no applied
            # part, so the carcass side itself is grown here.
            self._extend_finished_side_panels(layout)
            # Close the exposed corner of an extended finished side with a
            # return panel + rear stile when a return width is set (needs a
            # FINISHED back to return into). Runs after the extend so it can
            # read the grown side's rear edge.
            self._reconcile_finished_side_returns(layout)

        # Angled cabinet cutter: drives the trapezoidal silhouette on
        # the root cage, top, bottom, and any shelves. Lazy: created
        # on transition into angled mode, removed on transition out.
        if layout.is_angled and self._has_carcass():
            cutter_obj = self._ensure_angled_cutter()
            self._position_angled_cutter(cutter_obj, layout)
            self._apply_angled_cuts(cutter_obj)
        else:
            self._cleanup_angled_cutter_and_cuts()

        # Angled back extension: splay one/both side panels outward at the
        # back and widen the carcass panels, so the back is wider than the
        # square front (access into an angled wall corner). Runs after the
        # part loop so it reshapes the already-positioned sides / back /
        # top / bottom in place; a no-op when both extends are 0.
        if self._has_carcass():
            self._apply_back_extension(layout)

        # Extend Bottom (uppers): overhang the carcass bottom past a side to
        # cover the corner void where two uppers meet. Runs after the part
        # loop / back extension so it reshapes the positioned bottom in place.
        if self._has_carcass() and layout.cabinet_type == 'UPPER':
            self._apply_bottom_extension(layout)

        # Appliance bay annotation (square + SINK / COOKTOP word) on top
        # of stamped bays and the dedicated sink cabinet's basin bay.
        # Unconditional so stale annotations are wiped even when the
        # trigger goes away.
        self._apply_appliance_annotations(layout)

        # Furniture / veneer wood top: an overhanging slab sitting proud
        # on the carcass top (dresser / furniture products). Managed like
        # the cutters so it tracks width / depth / height; a no-op when
        # furniture_top is off.
        self._apply_furniture_top(layout)

        # Hutch finished back: close the open recess below an upper
        # whose ends are extended down. No-op when off / no drop.
        self._apply_hutch_back(layout)

        # Over-stool side-front profile: cut the decorative leg profile into
        # the bottom-front of each extended side. No-op + cleanup when off.
        self._apply_overstool_profile(layout)

        # Bottom-rail decorative profile (valance): cut the chosen profile
        # into the bottom rail(s). No-op + cleanup when off.
        self._apply_bottom_rail_profile(layout)

        # Over-stool leg accessories: shelf and/or towel bar between the legs
        # per the overstool_accessory dropdown. No-op + cleanup when off.
        self._apply_overstool_accessories(layout)

        # Tip-up wedge: chamfer the back-bottom corner when enabled and the
        # cabinet's tip-up diagonal exceeds the ceiling. Re-applied here so
        # it survives part reconciliation, exactly like the angled cutter.
        wedge = solver.wedge_geometry(layout) if self._has_carcass() else None
        if wedge is not None:
            length, height, _clamped = wedge
            cutter_obj = self._ensure_wedge_cutter()
            self._position_wedge_cutter(cutter_obj, length, height)
            self._apply_wedge_cuts(cutter_obj)
            # Publish the computed dims on the cabinet root (meters) as
            # id props so downstream consumers (e.g. drawing / annotation
            # layers) can read them without recomputing. Cleared when the
            # wedge is removed.
            self.obj['WEDGE_LENGTH'] = length
            self.obj['WEDGE_HEIGHT'] = height
        else:
            self._cleanup_wedge_cutter_and_cuts()
            for _k in ('WEDGE_LENGTH', 'WEDGE_HEIGHT'):
                if _k in self.obj:
                    del self.obj[_k]

    # =====================================================================
    # Angled cabinet cutter (single-bay, unlock_left/right_depth on)
    # =====================================================================
    def _ensure_angled_cutter(self):
        """Find the cabinet's angled cutter or build it. Lazy: only
        called when entering angled mode, so non-angled cabinets carry
        no extra child."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_ANGLED_CUTTER:
                return child
        cutter = GeoNodeCage()
        cutter.create('Angled Cutter')
        cutter.obj.parent = self.obj
        cutter.obj['hb_part_role'] = PART_ROLE_ANGLED_CUTTER
        # Show Cage emits the cage geometry the boolean reads from;
        # hide_viewport keeps the wireframe out of the artist's way.
        cutter.set_input('Show Cage', True)
        cutter.obj.hide_viewport = True
        return cutter.obj

    def _position_angled_cutter(self, cutter_obj, layout):
        """Place / size the cutter so its cage covers the wedge of
        space forward of the angled FF inner plane.

        Origin sits at the LEFT endpoint of the FF inner plane shifted
        backward along the FF direction by `margin`, with rotation_
        euler.z = face_frame_angle so cutter-local +X runs from left
        to right along the FF line. Cage extends in cutter-local +X
        for ff_length + 2 * margin (past both endpoints), in cutter-
        local -Y for dim_y + margin (toward the cabinet front, far
        enough to clear it from any point on the FF inner plane), and
        in +Z for dim_z + 2 * margin (covering top and bottom panels
        plus margin in either direction).
        """
        margin = inch(2.0)
        fft = layout.fft
        ld = solver.effective_left_depth(layout)
        theta = solver.face_frame_angle(layout)
        ff_len = solver.face_frame_length(layout)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        cutter_obj.location = (
            -margin * cos_t,
            -ld + fft - margin * sin_t,
            -margin,
        )
        cutter_obj.rotation_euler = (0.0, 0.0, theta)

        cage = GeoNodeCage(cutter_obj)
        cage.set_input('Dim X', ff_len + 2.0 * margin)
        cage.set_input('Dim Y', layout.dim_y + margin)
        cage.set_input('Dim Z', layout.dim_z + 2.0 * margin)
        cage.set_input('Mirror X', False)
        cage.set_input('Mirror Y', True)
        cage.set_input('Mirror Z', False)
        cage.set_input('Show Cage', True)

    def _iter_angled_cut_targets(self):
        """Yield every object that should carry the 'Angled Cut'
        modifier: cabinet root cage (so its silhouette matches the
        carved carcass), cabinet-level top / bottom panels, and any
        bay shelf / adjustable shelf living deeper in the bay tree.
        """
        yield self.obj
        stack = list(self.obj.children)
        while stack:
            obj = stack.pop()
            role = obj.get('hb_part_role')
            if role == PART_ROLE_ANGLED_CUTTER:
                continue
            if role in ANGLED_CUT_PART_ROLES:
                yield obj
            stack.extend(obj.children)

    def _apply_angled_cuts(self, cutter_obj):
        """Ensure every cuttable target carries a boolean DIFFERENCE
        modifier named ANGLED_CUT_MOD_NAME pointing at the cutter.
        Idempotent; safe to call every recalc."""
        for part in self._iter_angled_cut_targets():
            mod = part.modifiers.get(ANGLED_CUT_MOD_NAME)
            if mod is None:
                mod = part.modifiers.new(name=ANGLED_CUT_MOD_NAME, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
            if mod.object is not cutter_obj:
                mod.object = cutter_obj

    def _cleanup_angled_cutter_and_cuts(self):
        """Reverse of _apply_angled_cuts + _ensure_angled_cutter. Pulls
        the modifier off every target it might be attached to, then
        removes the cutter object. No-op when there's nothing to undo.
        """
        for part in self._iter_angled_cut_targets():
            mod = part.modifiers.get(ANGLED_CUT_MOD_NAME)
            if mod is not None:
                part.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_ANGLED_CUTTER:
                bpy.data.objects.remove(child, do_unlink=True)

    # =====================================================================
    # Angled back extension (trapezoidal back; extend_back_left / _right)
    # =====================================================================
    def _part_input(self, child, name):
        for m in child.modifiers:
            if m.type == 'NODES' and m.node_group:
                for it in m.node_group.interface.items_tree:
                    if getattr(it, 'in_out', '') == 'INPUT' and it.name == name:
                        try:
                            return hb_utils.get_gn_input(m, it.identifier)
                        except Exception:
                            return None
        return None

    def _set_part_input(self, child, name, value):
        for m in child.modifiers:
            if m.type == 'NODES' and m.node_group:
                for it in m.node_group.interface.items_tree:
                    if getattr(it, 'in_out', '') == 'INPUT' and it.name == name:
                        hb_utils.set_gn_input(m, it.identifier, value)
                        return

    def _back_ext_line(self, side, extend, depth):
        """The outer line of a back-extended / wing end, in cabinet-local XY.

        Returns (front_target, back_target, phi, w_new): front_target is the
        fixed front-outer corner; back_target is the back-outer corner moved
        out (signed) by `extend`; phi orients a part's local -Y axis from the
        new back toward the fixed front; w_new is the hypotenuse length.
        Shared by _angle_side_panel (carcass splay) and the attached wing so
        both sit on the exact same edge.
        """
        from mathutils import Vector
        dim_x = self.obj.face_frame_cabinet.width
        if side == 'RIGHT':
            outer_x = dim_x
            back_target = Vector((outer_x + extend, 0.0))
        else:  # LEFT
            outer_x = 0.0
            back_target = Vector((outer_x - extend, 0.0))
        front_target = Vector((outer_x, -depth))
        d = front_target - back_target
        w_new = d.length
        dn = d.normalized()
        # part-local front offset is (0, -W): R(phi)*(0,-1) must equal dn.
        # R(phi)*(0,-1) = (sin phi, -cos phi)  =>  phi = atan2(dn.x, -dn.y)
        phi = math.atan2(dn.x, -dn.y)
        return front_target, back_target, phi, w_new

    def _angle_side_panel(self, child, side, extend):
        """Splay one carcass side panel outward at the back by `extend`
        (meters), pivoting about its FRONT-OUTER corner so the front edge
        stays put. Analytic transform (no bound-box sampling):

        The side part's origin is its BACK-OUTER corner; its outer edge
        runs along part-local -Y by Width (= depth). For a RIGHT side the
        outer x is dim_x; the back-outer corner moves dim_x -> dim_x +
        extend, the front-outer corner stays at (dim_x, -depth). LEFT
        mirrors (outer x = 0, back moves to -extend).

        Sets: location = back-corner target, rotation_euler.z = phi so the
        part-local -Y axis points from the new back toward the fixed
        front, and Width = the new (hypotenuse) depth.
        """
        import math
        from mathutils import Vector
        # `extend` may be NEGATIVE: positive splays the back corner outward
        # (back wider than front), negative pulls it inward (back narrower).
        # The analytic transform below handles either sign -- back_target moves
        # the corner the signed amount and w_new / phi follow. Only exactly 0
        # is a no-op (the caller resets rotation in that case).
        depth = self._part_input(child, 'Width')
        if depth is None or extend == 0.0:
            return None
        front_target, back_target, phi, w_new = self._back_ext_line(
            side, extend, depth)
        child.rotation_euler.z = phi
        child.location.x = back_target.x
        child.location.y = back_target.y
        self._set_part_input(child, 'Width', w_new)
        # Return the side's OUTER line (front-outer, back-outer) so the
        # trapezoid trim cutter can align its cut to this exact edge.
        return (front_target, back_target)

    # =====================================================================
    # Furniture / veneer wood top (dresser products)
    # =====================================================================
    def _ensure_furniture_top(self):
        """Find or lazily create the furniture-top CabinetPart - a flat
        slab parented to the cabinet root, tagged PART_ROLE_FURNITURE_TOP
        and CABINET_PART so the material walk picks it up. Reused across
        recalcs; sizing / placement is done by _position_furniture_top."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP:
                return child
        top = CabinetPart()
        top.create('Wood Top')
        top.obj.parent = self.obj
        top.obj['hb_part_role'] = PART_ROLE_FURNITURE_TOP
        top.obj['CABINET_PART'] = True
        # Flat slab orientation: Length -> +X, Width -> -Y (Mirror Y),
        # Thickness -> +Z (Mirror Z False) so it sits proud ON the carcass
        # top rather than extending down into the case.
        top.set_input('Mirror Y', True)
        top.set_input('Mirror Z', False)
        return top.obj

    def _position_furniture_top(self, top_obj):
        """Size + place the furniture top from the cabinet width / depth /
        height and the per-side furniture_top_overhang_* / _thickness props.
        Each edge (front / back / left / right) overhangs the carcass
        independently. Falls back to the legacy uniform furniture_top_overhang
        (and a flush back) for data saved before the per-side props.

        BOW_BACK shape: the slab is first extended straight back by the
        bow altitude so it covers the arc's bulge; the shape cutter then
        trims it back to the arc (the arc's corners stay on the straight
        back-overhang line)."""
        cab = self.obj.face_frame_cabinet
        dim_x = cab.width
        dim_y = cab.depth
        dim_z = cab.height
        legacy = cab.furniture_top_overhang
        ohl = getattr(cab, 'furniture_top_overhang_left', legacy)
        ohr = getattr(cab, 'furniture_top_overhang_right', legacy)
        ohf = getattr(cab, 'furniture_top_overhang_front', legacy)
        ohb = getattr(cab, 'furniture_top_overhang_back', 0.0)
        th = cab.furniture_top_thickness
        bow = 0.0
        if getattr(cab, 'furniture_top_shape', 'RECTANGLE') == 'BOW_BACK':
            bow = max(getattr(cab, 'furniture_top_bow_altitude', 0.0), 0.0)
        part = GeoNodeCutpart(top_obj)
        part.set_input('Length', dim_x + ohl + ohr)   # left + right overhang
        part.set_input('Width', dim_y + ohf + ohb + bow)  # front/back + bow
        part.set_input('Thickness', th)
        # Origin at the case top back-left corner, shifted -X by the left
        # overhang and +Y by the back overhang (plus the bow bulge). Width
        # runs -Y from the back edge past the front (y = -(dim_y + ohf)).
        # Thickness +Z.
        top_obj.location = Vector((-ohl, ohb + bow, dim_z))
        top_obj.rotation_euler = (0.0, 0.0, 0.0)

    def _cleanup_furniture_top(self):
        """Remove the furniture-top part (furniture_top toggled off, or a
        non-carcass / non-furniture cabinet) plus its shape cutter and
        any waterfall drop panels."""
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP:
                bpy.data.objects.remove(child, do_unlink=True)
        self._cleanup_furniture_top_cutter()
        self._cleanup_furniture_top_legs()

    # ---- Furniture top shape (bow back / radius corners / waterfall) ----
    def _furniture_top_extents(self):
        """Plan-space extents of the furniture top in cabinet-local XY:
        (x_left, x_right, y_front, y_back) EXCLUDING any bow bulge - the
        bow arc's corners sit on y_back. Mirrors the sizing math in
        _position_furniture_top."""
        cab = self.obj.face_frame_cabinet
        legacy = cab.furniture_top_overhang
        ohl = getattr(cab, 'furniture_top_overhang_left', legacy)
        ohr = getattr(cab, 'furniture_top_overhang_right', legacy)
        ohf = getattr(cab, 'furniture_top_overhang_front', legacy)
        ohb = getattr(cab, 'furniture_top_overhang_back', 0.0)
        return (-ohl, cab.width + ohr, -(cab.depth + ohf), ohb)

    def _ensure_furniture_top_cutter(self):
        """Find or lazily create the furniture-top shape cutter MESH.
        Hidden in the viewport; the boolean reads its mesh regardless.
        Mirrors _ensure_back_ext_cutter."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP_CUTTER:
                return child
        mesh = bpy.data.meshes.new('Wood Top Shape Cutter')
        cutter = bpy.data.objects.new('Wood Top Shape Cutter', mesh)
        cutter['hb_part_role'] = PART_ROLE_FURNITURE_TOP_CUTTER
        cutter.parent = self.obj
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in self.obj.users_collection:
            coll.objects.link(cutter)
            break
        return cutter

    def _position_furniture_top_cutter(self, cutter_obj):
        """Rebuild the shape-cutter mesh for the current shape props.

        BOW_BACK: one prism removing everything behind the circular arc
        through the two back corners and the apex (bow altitude past the
        straight back edge). The slab was pre-extended by the altitude in
        _position_furniture_top, so the DIFFERENCE leaves the bowed edge.

        RADIUS: one prism per corner with a non-zero radius, removing the
        corner material outside a quarter-circle of that radius. Radii are
        clamped so opposite corners cannot overlap.

        Prisms span only the top's Z range (plus a margin) so nothing else
        is affected, and their outer walls sit a margin outside the slab so
        no cutter face is coplanar with a slab face."""
        cab = self.obj.face_frame_cabinet
        shape = getattr(cab, 'furniture_top_shape', 'RECTANGLE')
        x_l, x_r, y_f, y_b = self._furniture_top_extents()
        th = cab.furniture_top_thickness
        margin = inch(1.0)
        z0 = cab.height - margin
        z1 = cab.height + th + margin

        def prism(bm, pts):
            # Extrude a closed plan polygon from z0 to z1; winding is
            # unified by the recalc_face_normals below.
            bot = [bm.verts.new((p[0], p[1], z0)) for p in pts]
            top = [bm.verts.new((p[0], p[1], z1)) for p in pts]
            bm.faces.new(bot)
            bm.faces.new(list(reversed(top)))
            n = len(pts)
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((bot[i], bot[j], top[j], top[i]))

        bm = bmesh.new()
        if shape == 'BOW_BACK':
            alt = max(getattr(cab, 'furniture_top_bow_altitude', 0.0), 0.0)
            if alt > 1e-6:
                # Circle through (x_l, y_b), (x_r, y_b) and the apex
                # ((x_l + x_r) / 2, y_b + alt): R = (c^2 + a^2) / 2a with
                # c the half-chord, centered a - R below the apex.
                half = (x_r - x_l) * 0.5
                rad = (half * half + alt * alt) / (2.0 * alt)
                cx = (x_l + x_r) * 0.5
                cy = y_b + alt - rad
                a0 = math.atan2(y_b - cy, x_l - cx)
                a1 = math.atan2(y_b - cy, x_r - cx)
                y_out = y_b + alt + margin
                segs = FURNITURE_TOP_BOW_SEGMENTS
                pts = []
                for i in range(segs + 1):
                    ang = a0 + (a1 - a0) * i / segs
                    pts.append((cx + rad * math.cos(ang),
                                cy + rad * math.sin(ang)))
                # Close around the outside: past the right corner, back
                # behind the extended slab, past the left corner. The end
                # walls sit outside the slab ends so the only cut faces
                # are along the arc itself.
                pts.extend([(x_r + margin, y_b), (x_r + margin, y_out),
                            (x_l - margin, y_out), (x_l - margin, y_b)])
                prism(bm, pts)
        elif shape == 'RADIUS':
            segs = FURNITURE_TOP_RADIUS_SEGMENTS
            rmax = max(min(x_r - x_l, y_b - y_f) * 0.5 - inch(0.01), 0.0)
            corners = (
                # (corner, x/y direction into the slab, radius prop)
                (x_l, y_f, 1.0, 1.0,
                 getattr(cab, 'furniture_top_radius_front_left', 0.0)),
                (x_r, y_f, -1.0, 1.0,
                 getattr(cab, 'furniture_top_radius_front_right', 0.0)),
                (x_l, y_b, 1.0, -1.0,
                 getattr(cab, 'furniture_top_radius_back_left', 0.0)),
                (x_r, y_b, -1.0, -1.0,
                 getattr(cab, 'furniture_top_radius_back_right', 0.0)),
            )
            for px, py, sx, sy, r in corners:
                r = min(max(r, 0.0), rmax)
                if r <= 1e-6:
                    continue
                # Quarter-circle centered r in from both edges; removal
                # region = the corner block outside the arc, extended a
                # margin past both slab edges.
                ccx, ccy = px + sx * r, py + sy * r
                pts = [(px + sx * r, py)]      # tangent point on the X edge
                for i in range(1, segs):
                    ang = (math.pi * 0.5) * i / segs
                    pts.append((ccx - sx * r * math.sin(ang),
                                ccy - sy * r * math.cos(ang)))
                pts.append((px, py + sy * r))  # tangent point on the Y edge
                pts.extend([(px - sx * margin, py + sy * r),
                            (px - sx * margin, py - sy * margin),
                            (px + sx * r, py - sy * margin)])
                prism(bm, pts)
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(cutter_obj.data)
        bm.free()
        cutter_obj.location = (0.0, 0.0, 0.0)
        cutter_obj.rotation_euler = (0.0, 0.0, 0.0)

    def _cleanup_furniture_top_cutter(self):
        """Remove the shape cutter and its boolean modifier on the top.
        No-op when there is nothing to undo."""
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP:
                mod = child.modifiers.get(FURNITURE_TOP_CUT_MOD_NAME)
                if mod is not None:
                    child.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP_CUTTER:
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    def _ensure_furniture_top_leg(self, side):
        """Find or lazily create one waterfall drop panel ('LEFT' /
        'RIGHT'), tagged like the top so the material walk finishes it.
        Same vertical-panel orientation as the carcass sides: Length up,
        Width along -Y, thickness across X - mirrored so each leg's
        origin X is its OUTER face."""
        for child in self.obj.children:
            if (child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP_LEG
                    and child.get('hb_leg_side') == side):
                return child
        leg = CabinetPart()
        leg.create(f'Wood Top Waterfall {side.title()}')
        leg.obj.parent = self.obj
        leg.obj['hb_part_role'] = PART_ROLE_FURNITURE_TOP_LEG
        leg.obj['hb_leg_side'] = side
        leg.obj['CABINET_PART'] = True
        leg.obj.rotation_euler.y = math.radians(-90)
        leg.set_input('Mirror Y', True)
        # LEFT grows thickness +X (inward from the outer face at the
        # top's left edge); RIGHT grows -X from the top's right edge.
        leg.set_input('Mirror Z', side == 'LEFT')
        return leg.obj

    def _position_furniture_top_legs(self):
        """Size + place both waterfall drop panels: outer face flush with
        the top's end, running from the floor to the underside of the top,
        spanning the top's full plan depth, same thickness as the top."""
        cab = self.obj.face_frame_cabinet
        x_l, x_r, y_f, y_b = self._furniture_top_extents()
        th = cab.furniture_top_thickness
        dim_z = cab.height
        for side, outer_x in (('LEFT', x_l), ('RIGHT', x_r)):
            leg_obj = self._ensure_furniture_top_leg(side)
            if leg_obj.get('IS_MANUAL_PART'):
                continue
            part = GeoNodeCutpart(leg_obj)
            part.set_input('Length', dim_z)      # floor -> underside of top
            part.set_input('Width', y_b - y_f)   # full top plan depth
            part.set_input('Thickness', th)
            leg_obj.location = Vector((outer_x, y_b, 0.0))
            leg_obj.rotation_euler = (0.0, math.radians(-90), 0.0)

    def _cleanup_furniture_top_legs(self):
        """Remove the waterfall drop panels (shape changed / top gone)."""
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_FURNITURE_TOP_LEG:
                bpy.data.objects.remove(child, do_unlink=True)

    def _apply_furniture_top(self, layout):
        """Build / position the veneer wood top when furniture_top is on and
        the cabinet has a carcass; otherwise ensure it is gone. Called once
        per recalc (after _apply_back_extension) so it tracks width / depth /
        height changes - the managed-part lifecycle mirrors the cutters.
        Also manages the shape extras from furniture_top_shape: the
        bow-back / radius-corner boolean cutter and the waterfall drop
        panels."""
        cab = self.obj.face_frame_cabinet
        if getattr(cab, 'furniture_top', False) and self._has_carcass():
            top_obj = self._ensure_furniture_top()
            # A made-editable (manual) top is hand-controlled: its cutpart
            # GeoNode has been applied off, so re-driving it would raise
            # (no modifier to set inputs on). Leave it exactly as the user
            # edited it - including any shape cutter / waterfall panels.
            if top_obj.get('IS_MANUAL_PART'):
                return
            self._position_furniture_top(top_obj)
            shape = getattr(cab, 'furniture_top_shape', 'RECTANGLE')
            wants_cut = (
                (shape == 'BOW_BACK'
                 and getattr(cab, 'furniture_top_bow_altitude', 0.0) > 1e-6)
                or (shape == 'RADIUS' and any(
                    getattr(cab, f'furniture_top_radius_{c}', 0.0) > 1e-6
                    for c in ('front_left', 'front_right',
                              'back_left', 'back_right'))))
            if wants_cut:
                cutter = self._ensure_furniture_top_cutter()
                self._position_furniture_top_cutter(cutter)
                mod = top_obj.modifiers.get(FURNITURE_TOP_CUT_MOD_NAME)
                if mod is None:
                    mod = top_obj.modifiers.new(
                        name=FURNITURE_TOP_CUT_MOD_NAME, type='BOOLEAN')
                    mod.operation = 'DIFFERENCE'
                    mod.solver = 'EXACT'
                if mod.object is not cutter:
                    mod.object = cutter
            else:
                self._cleanup_furniture_top_cutter()
            if shape == 'WATERFALL':
                self._position_furniture_top_legs()
            else:
                self._cleanup_furniture_top_legs()
        else:
            self._cleanup_furniture_top()

    # =====================================================================
    # Hutch finished back (uppers with ends extended down)
    # =====================================================================
    def _ensure_hutch_back(self):
        """Find or lazily create the hutch recess back CabinetPart - a
        panel mirroring the carcass back's orientation, tagged
        PART_ROLE_HUTCH_BACK (+ CABINET_PART so the material walk gives it
        the finish material). Sized / placed by _position_hutch_back."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_HUTCH_BACK:
                return child
        back = CabinetPart()
        back.create('Hutch Back')
        back.obj.parent = self.obj
        back.obj['hb_part_role'] = PART_ROLE_HUTCH_BACK
        back.obj['CABINET_PART'] = True
        # Same orientation as the carcass back (Length up, Width across X).
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.set_input('Mirror Y', True)
        return back.obj

    def _position_hutch_back(self, back_obj, layout):
        """Span the back of the dropped-end recess: same X / Y / thickness
        as the carcass back, from the box bottom DOWN by the drop (the
        deeper of the two ends when they differ)."""
        segs = solver.carcass_back_segments(layout)
        if not segs:
            self._cleanup_hutch_back()
            return
        left_x = min(s['x'] for s in segs)
        right_x = max(s['x'] + s['horizontal_length'] for s in segs)
        drop = max(solver.ends_down_drop(layout, 'LEFT'),
                   solver.ends_down_drop(layout, 'RIGHT'))
        box_bottom = solver.bay_bottom_z(layout, 0)
        bottom_z = box_bottom - drop
        # Top out at the carcass back's bottom edge (seg z) so the recess
        # back is continuous with it and reaches the actual underside of
        # the upper box - bay_bottom_z is only the bottom-rail line, which
        # sits ~a rail below the bottom panel, leaving a gap.
        top_z = segs[0]['z']
        part = GeoNodeCutpart(back_obj)
        part.set_input('Length', top_z - bottom_z)
        part.set_input('Width', right_x - left_x)
        part.set_input('Thickness', segs[0]['thickness'])
        back_obj.location = (left_x, segs[0]['y'], bottom_z)

    def _cleanup_hutch_back(self):
        """Remove the hutch recess back (option off / no end dropped)."""
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_HUTCH_BACK:
                bpy.data.objects.remove(child, do_unlink=True)

    def _apply_hutch_back(self, layout):
        """Close the open recess below an upper whose ends are extended
        down with a finished back, when hutch_finished_back is on and at
        least one end is dropped. Called once per recalc; managed like the
        other extras."""
        cab = self.obj.face_frame_cabinet
        drop = max(solver.ends_down_drop(layout, 'LEFT'),
                   solver.ends_down_drop(layout, 'RIGHT'))
        if getattr(cab, 'hutch_finished_back', False) and drop > 0:
            back_obj = self._ensure_hutch_back()
            self._position_hutch_back(back_obj, layout)
        else:
            self._cleanup_hutch_back()

    def _apply_back_extension(self, layout):
        """Reshape the carcass into a trapezoid wider at the back when
        extend_back_left / extend_back_right are set. v1 step 1: angle the
        side panel(s). Back / top / bottom widening follows. No-op (and
        resets any prior angle) when an end's extend is 0.
        """
        cab = self.obj.face_frame_cabinet
        raw_l = getattr(cab, 'extend_back_left', 0.0) or 0.0
        raw_r = getattr(cab, 'extend_back_right', 0.0) or 0.0
        # "Attach as Wing" converts an end's back extension into a separate
        # angled return panel: the carcass stays SQUARE for that end and the
        # extension is built as a wing below instead. Only active when the
        # end's extend is non-zero.
        wing_l = bool(getattr(cab, 'wing_attached_left', False)) and raw_l != 0.0
        wing_r = bool(getattr(cab, 'wing_attached_right', False)) and raw_r != 0.0
        # Carcass-effective extends: zero on a wing end so the splay / widen /
        # trim below leave it square; the raw value drives the wing instead.
        ext_l = 0.0 if wing_l else raw_l
        ext_r = 0.0 if wing_r else raw_r
        # Either end may be POSITIVE (outward, back wider) or NEGATIVE
        # (inward, back narrower); only exactly 0 is a no-op for that end.
        active = ext_l != 0.0 or ext_r != 0.0
        line_l = None   # (front_outer, back_outer) of the angled left side
        line_r = None   # ... right side; feed the trim cutter
        side_thickness = 0.0
        for child in self.obj.children:
            role = child.get('hb_part_role')
            if role == PART_ROLE_LEFT_SIDE:
                side_thickness = self._part_input(child, 'Thickness') or 0.0
                if ext_l != 0.0:
                    line_l = self._angle_side_panel(child, 'LEFT', ext_l)
                else:
                    child.rotation_euler.z = 0.0
            elif role == PART_ROLE_RIGHT_SIDE:
                side_thickness = self._part_input(child, 'Thickness') or 0.0
                if ext_r != 0.0:
                    line_r = self._angle_side_panel(child, 'RIGHT', ext_r)
                else:
                    child.rotation_euler.z = 0.0
            elif role in (PART_ROLE_BACK, PART_ROLE_FINISHED_BACK):
                # Back panel: X-span is the 'Width' input. Not a trim-cutter
                # target, so it follows the corner directly in BOTH directions
                # (grows outward / shrinks inward).
                self._widen_back_panel(child, ext_l, ext_r, 'Width')
            elif role in (PART_ROLE_REAR_STRETCHER, PART_ROLE_FRONT_STRETCHER,
                          PART_ROLE_FINISH_TOE_KICK,
                          PART_ROLE_TOE_KICK_SUBFRONT):
                # Stretchers AND the toe-kick front members (finish kick + sub
                # kick) all span left-right (X-span is 'Length') and have depth
                # in Y, so the angled side crosses them. Treated like top/bottom:
                # outward grows rectangularly then the cutter trims the overhang;
                # inward stays square and the cutter trims the corner
                # (allow_shrink=False). The toe-kick fronts are RECESSED in Y, so
                # at their setback the angled side has already moved off the
                # square width -- widening + the cutter lands their end on the
                # side line at that depth, closing the gap the recess opened.
                # Front-most edges trim back to the square front-outer corner, so
                # the square front face is unaffected.
                self._widen_back_panel(child, ext_l, ext_r, 'Length',
                                       allow_shrink=False)
            elif role in (PART_ROLE_TOP, PART_ROLE_BOTTOM):
                # Full-depth panels ARE trim-cutter targets. Outward: extend
                # rectangularly to the corner, the cutter trims the FRONT
                # overhang -> trapezoid. Inward: leave the panel SQUARE
                # (allow_shrink=False ignores a negative end) and let the cutter
                # remove the BACK corner instead. The cutter's cut line is the
                # angled side either way, so a square panel trims correctly.
                self._widen_back_panel(child, ext_l, ext_r, 'Length',
                                       allow_shrink=False)

        # Trapezoid trim for the full-depth panels (top / bottom / shelves):
        # boolean-difference the front overhang along the angled side
        # line(s). Built only when an end is extended; removed otherwise.
        if active and (line_l is not None or line_r is not None):
            cutter = self._ensure_back_ext_cutter()
            self._position_back_ext_cutter(cutter, line_l, line_r, side_thickness)
            self._apply_back_ext_cuts(cutter)
        else:
            self._cleanup_back_ext_cutter_and_cuts()

        # Wing attached: for an end whose "Attach as Wing" is on (and its
        # extend is non-zero), the carcass above stayed square (wing ends were
        # zeroed out of ext_l / ext_r); add the angled return panel along the
        # line the raw extend defines. Off / 0 -> removed.
        self._apply_wing(layout, 'LEFT', raw_l if wing_l else 0.0)
        self._apply_wing(layout, 'RIGHT', raw_r if wing_r else 0.0)

    def _apply_wing(self, layout, side, extend):
        """Build / remove the attached wing on one end. `extend` is the raw
        extend_back value (already gated on the wing checkbox by the caller);
        0 removes the wing. The wing is a flat angled return panel standing on
        the same (front-outer, back-outer) line the back extension would have
        used, with the carcass kept square."""
        if extend != 0.0 and self._has_carcass():
            wing_obj = self._ensure_wing(side)
            self._position_wing(wing_obj, layout, side, extend)
        else:
            self._cleanup_wing(side)

    def _ensure_wing(self, side):
        """Find or lazily create one end's wing CabinetPart - a bare finished
        panel tagged PART_ROLE_WING (+ CABINET_PART so the material walk
        finishes its outer face) and WING_SIDE so the two ends stay distinct.
        Same base orientation as a carcass side (Length up, Width across);
        Mirror Z matches the side so the finished outer face is Bottom."""
        for child in self.obj.children:
            if (child.get('hb_part_role') == PART_ROLE_WING
                    and child.get('WING_SIDE') == side):
                return child
        wing = CabinetPart()
        wing.create('Wing')
        wing.obj.parent = self.obj
        wing.obj['hb_part_role'] = PART_ROLE_WING
        wing.obj['CABINET_PART'] = True
        wing.obj['WING_SIDE'] = side
        wing.obj.rotation_euler.y = math.radians(-90)
        wing.set_input('Mirror Y', True)
        wing.set_input('Mirror Z', side == 'LEFT')
        return wing.obj

    def _position_wing(self, wing_obj, layout, side, extend):
        """Stand the wing on the angled end line: full side height, the
        hypotenuse as its Width, pivoted to phi at the back-outer corner.
        Reuses _back_ext_line (shared with the carcass splay) and the solver's
        square side position / dims, so the wing tracks height / depth and
        sits at the side's base Z."""
        if side == 'LEFT':
            pos = solver.left_side_position(layout)
            length, width, thickness = solver.left_side_dims(layout)
        else:
            pos = solver.right_side_position(layout)
            length, width, thickness = solver.right_side_dims(layout)
        _front, back_target, phi, w_new = self._back_ext_line(side, extend, width)
        part = GeoNodeCutpart(wing_obj)
        part.set_input('Length', length)       # full cabinet (side) height
        part.set_input('Width', w_new)         # hypotenuse along the end line
        part.set_input('Thickness', thickness)
        wing_obj.rotation_euler.z = phi
        wing_obj.location = (back_target.x, back_target.y, pos[2])

    def _cleanup_wing(self, side):
        """Remove one end's wing (checkbox off or extend back to 0)."""
        for child in list(self.obj.children):
            if (child.get('hb_part_role') == PART_ROLE_WING
                    and child.get('WING_SIDE') == side):
                bpy.data.objects.remove(child, do_unlink=True)

    def _apply_bottom_extension(self, layout):
        """Overhang the carcass bottom panel(s) laterally past the side(s) to
        cover the void where two upper cabinets meet in a corner. Uppers only.

        Outward only (extend_bottom_left / _right are min 0). Reuses
        _widen_back_panel on the BOTTOM children with the 'Length' span input:
        that helper already grows only the end(s) that reach a cabinet end
        (so on a multi-bay upper just the outermost bottom segment overhangs,
        interior bay divisions are left alone) and derives the span
        analytically (recalc-stale-safe). Nothing else moves - the face frame,
        sides, and doors stay square, so only the bottom sticks out under the
        void. No-op (square) when both extends are 0; the part loop has already
        reset each bottom to its square span this recalc, so this is applied on
        top each time and self-corrects when the values drop back to 0.
        """
        cab = self.obj.face_frame_cabinet
        ext_l = getattr(cab, 'extend_bottom_left', 0.0) or 0.0
        ext_r = getattr(cab, 'extend_bottom_right', 0.0) or 0.0
        if ext_l == 0.0 and ext_r == 0.0:
            return
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_BOTTOM:
                self._widen_back_panel(child, ext_l, ext_r, 'Length',
                                       allow_shrink=True)

    def _widen_back_panel(self, child, ext_l, ext_r, span_input,
                          allow_shrink=True):
        """Move a back-row panel's X-span end(s) to follow the angled back
        corner(s). Signed: a POSITIVE end extends the span outward, a NEGATIVE
        end shrinks it inward. Only the end(s) reaching a cabinet end move; a
        segment ending at an interior bay division is left alone. The right
        end moves by ext_r; the left end by ext_l (and the origin follows so
        the right end stays put). `span_input` is the X-span geometry-node
        input ('Width' for the back panel, 'Length' for stretchers / top /
        bottom).

        `allow_shrink`: False for full-depth TOP / BOTTOM, which the trim
        cutter re-shapes -- a NEGATIVE (inward) end is ignored here so the
        panel stays SQUARE and the cutter removes the back corner instead.
        True (back panel / rear stretcher, not cutter targets) follows the
        corner directly in both directions.

        The part loop has just reset this panel's square span/location, so the
        deltas are applied on top each recalc (self-correcting).
        """
        if not allow_shrink:
            # Trim-cutter targets: ignore inward (negative) ends -- the cutter
            # trims the back corner off the square panel.
            ext_l = max(ext_l, 0.0)
            ext_r = max(ext_r, 0.0)
        if ext_l == 0.0 and ext_r == 0.0:
            return
        width = self._part_input(child, span_input)
        if width is None:
            return
        dim_x = self.obj.face_frame_cabinet.width
        # X extent of this panel in cabinet-local, derived ANALYTICALLY from the
        # part's fresh origin + span -- NOT from bound_box. The part loop just
        # set this panel's location + span this recalc, but bound_box is the
        # depsgraph-EVALUATED extent and can still report the PREVIOUS extend
        # within the same pass (stale). Reading it made the "reaches the end"
        # test flip between recalcs, so the part length flickered as the extend
        # value changed. The part's origin is its left (-X) edge and the span
        # runs +X by `width` (the same convention the grow/origin math below
        # relies on), so the extent is [location.x, location.x + width]. The
        # back is inset from each cabinet end by the side thickness, so "reaches
        # the end" uses a 1" tolerance rather than touching 0 / dim_x exactly.
        x_lo = child.location.x
        x_hi = child.location.x + width
        end_tol = inch(1.0)
        grow_left = ext_l if x_lo <= end_tol else 0.0
        grow_right = ext_r if x_hi >= dim_x - end_tol else 0.0
        if grow_left == 0.0 and grow_right == 0.0:
            return
        # Floor the result so a large inward value can't invert the panel.
        new_width = max(width + grow_left + grow_right, inch(0.125))
        self._set_part_input(child, span_input, new_width)
        # The right end moves with the span from the fixed left origin (no
        # origin move). Moving the left end shifts the origin by -grow_left:
        # +grow_left (outward) moves the origin -X; a negative grow_left
        # (inward) moves it +X. Right end stays put either way.
        if grow_left != 0.0:
            child.location.x -= grow_left

    # =====================================================================
    # Tip-up wedge cutter (back-bottom chamfer; driven by wedge_* props)
    # =====================================================================
    def _ensure_back_ext_cutter(self):
        """Find or lazily create the back-extension trim cutter MESH.
        Hidden in the viewport; the boolean reads its mesh regardless.
        Mirrors _ensure_wedge_cutter."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_BACK_EXT_CUTTER:
                return child
        mesh = bpy.data.meshes.new('Back Extension Cutter')
        cutter = bpy.data.objects.new('Back Extension Cutter', mesh)
        cutter['hb_part_role'] = PART_ROLE_BACK_EXT_CUTTER
        cutter.parent = self.obj
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in self.obj.users_collection:
            coll.objects.link(cutter)
            break
        return cutter

    def _position_back_ext_cutter(self, cutter_obj, line_l, line_r,
                                  side_thickness):
        """Rebuild the cutter mesh as one half-space box per angled side,
        each removing the front overhang outside that side's INNER face -
        so the rectangularly-extended top / bottom become trapezoids that
        match the angled sides.

        Each `line` is (front_outer, back_outer) Vector2 in cabinet-local
        X-Y, as used to place the angled side. The inner face is that line
        offset toward the cabinet body by `side_thickness`; the box keeps
        the body side and removes the rest.
        """
        import math
        from mathutils import Vector
        margin = inch(2.0)
        dim_x = self.obj.face_frame_cabinet.width
        dim_y = self.obj.face_frame_cabinet.depth
        dim_z = self.obj.face_frame_cabinet.height
        big = (dim_x + dim_y) * 2.0 + inch(12.0)
        body_center = Vector((dim_x * 0.5, -dim_y * 0.5))
        z0, z1 = -margin, dim_z + margin

        bm = bmesh.new()

        def add_box(front_outer, back_outer):
            d = (back_outer - front_outer)
            if d.length < 1e-6:
                return
            dirn = d.normalized()
            # inward normal candidates; pick the one pointing toward the
            # body center (that side is kept).
            n = Vector((-dirn.y, dirn.x))
            if n.dot(body_center - front_outer) < 0:
                n = -n
            # inner face line, offset toward the body by the side thickness
            f_in = front_outer + n * side_thickness
            # remove side is away from the body: -n
            rem = -n
            # box: u along dirn (both ways), v along rem (0..big = remove),
            # extruded in z.
            def P(u, v, z):
                p = f_in + dirn * u + rem * v
                return (p.x, p.y, z)
            us = (-big, big)
            vs = (-inch(0.05), big)   # tiny bite into the body to avoid a sliver
            verts = {}
            for iu, u in enumerate(us):
                for iv, v in enumerate(vs):
                    for iz, z in enumerate((z0, z1)):
                        verts[(iu, iv, iz)] = bm.verts.new(P(u, v, z))
            bm.verts.ensure_lookup_table()

            def face(a, bb, c, dd):
                bm.faces.new((verts[a], verts[bb], verts[c], verts[dd]))
            face((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))
            face((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))
            face((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))
            face((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))
            face((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))
            face((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))

        if line_l is not None:
            add_box(line_l[0], line_l[1])
        if line_r is not None:
            add_box(line_r[0], line_r[1])
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(cutter_obj.data)
        bm.free()
        cutter_obj.location = (0.0, 0.0, 0.0)
        cutter_obj.rotation_euler = (0.0, 0.0, 0.0)

    def _iter_back_ext_cut_targets(self):
        """Full-depth panels the trapezoid trim applies to. Mirrors
        _iter_wedge_cut_targets."""
        stack = list(self.obj.children)
        while stack:
            obj = stack.pop()
            role = obj.get('hb_part_role')
            if role == PART_ROLE_BACK_EXT_CUTTER:
                continue
            if role in BACK_EXT_CUT_PART_ROLES:
                yield obj
            stack.extend(obj.children)

    def _apply_back_ext_cuts(self, cutter_obj):
        """Ensure every target carries a boolean DIFFERENCE modifier named
        BACK_EXT_CUT_MOD_NAME pointing at the cutter. Idempotent."""
        for part in self._iter_back_ext_cut_targets():
            mod = part.modifiers.get(BACK_EXT_CUT_MOD_NAME)
            if mod is None:
                mod = part.modifiers.new(
                    name=BACK_EXT_CUT_MOD_NAME, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
            if mod.object is not cutter_obj:
                mod.object = cutter_obj

    def _cleanup_back_ext_cutter_and_cuts(self):
        """Reverse of _apply_back_ext_cuts + _ensure_back_ext_cutter.
        No-op when there's nothing to undo."""
        for part in self._iter_back_ext_cut_targets():
            mod = part.modifiers.get(BACK_EXT_CUT_MOD_NAME)
            if mod is not None:
                part.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_BACK_EXT_CUTTER:
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    # =====================================================================
    # Over-stool side-front profile cut (decorative leg foot)
    # =====================================================================
    def _side_part_by_role(self, role):
        """The carcass side panel (LEFT_SIDE / RIGHT_SIDE) - a direct child
        of the cabinet root. None if absent (panels / suppressed bays)."""
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        return None

    def _ensure_side_profile_cutter(self, side):
        """Find or lazily create the per-side profile cutter MESH (one per
        side, distinguished by hb_profile_side). Hidden; the boolean reads
        its mesh regardless. Mirrors _ensure_back_ext_cutter."""
        for child in self.obj.children:
            if (child.get('hb_part_role') == PART_ROLE_SIDE_PROFILE_CUTTER
                    and child.get('hb_profile_side') == side):
                return child
        name = 'Side Profile Cutter ' + side.title()
        mesh = bpy.data.meshes.new(name)
        cutter = bpy.data.objects.new(name, mesh)
        cutter['hb_part_role'] = PART_ROLE_SIDE_PROFILE_CUTTER
        cutter['hb_profile_side'] = side
        cutter.parent = self.obj
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in self.obj.users_collection:
            coll.objects.link(cutter)
            break
        return cutter

    def _position_side_profile_cutter(self, cutter, side, layout):
        """Rebuild the cutter mesh as a prism: the profile silhouette placed
        with its LOCAL ORIGIN at the side's bottom-front corner (profile X ->
        cabinet depth/Y, profile Y -> vertical/Z), extruded through the full
        panel thickness in X. Built in CABINET-LOCAL coords (cutter at
        identity), the same frame the side position is expressed in.

        Orientation knobs (eyeball / flip if the cut faces the wrong way):
          DEPTH_SIGN  profile +X -> +Y (toward the back) when +1.
          UP_SIGN     profile +Y -> +Z (upward) when +1.
        """
        poly = _overstool_profile_poly()
        if not poly:
            return
        if side == 'RIGHT':
            pos = solver.right_side_position(layout)
            dims = solver.right_side_dims(layout)
        else:
            pos = solver.left_side_position(layout)
            dims = solver.left_side_dims(layout)
        depth, thickness = dims[1], dims[2]
        corner_y = pos[1] - depth          # front edge (front = -Y)
        corner_z = pos[2]                  # dropped side bottom
        margin = inch(2.0)
        x0 = pos[0] - thickness - margin   # span the full panel thickness
        x1 = pos[0] + thickness + margin   # (both directions; panel is thin)
        DEPTH_SIGN, UP_SIGN = 1.0, 1.0
        bm = bmesh.new()
        loop0, loop1 = [], []
        for (px, py) in poly:
            y = corner_y + DEPTH_SIGN * px
            z = corner_z + UP_SIGN * py
            loop0.append(bm.verts.new((x0, y, z)))
            loop1.append(bm.verts.new((x1, y, z)))
        bm.faces.new(loop0)
        bm.faces.new(list(reversed(loop1)))
        n = len(poly)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((loop0[i], loop0[j], loop1[j], loop1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(cutter.data)
        bm.free()
        cutter.location = (0.0, 0.0, 0.0)
        cutter.rotation_euler = (0.0, 0.0, 0.0)

    def _cleanup_side_profile_cutters(self):
        """Reverse of _apply_overstool_profile. No-op when nothing to undo."""
        for role in (PART_ROLE_LEFT_SIDE, PART_ROLE_RIGHT_SIDE):
            part = self._side_part_by_role(role)
            if part is None:
                continue
            mod = part.modifiers.get(SIDE_PROFILE_CUT_MOD_NAME)
            if mod is not None:
                part.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_SIDE_PROFILE_CUTTER:
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    def _apply_overstool_profile(self, layout):
        """Cut the over-stool decorative profile into the bottom-front corner
        of each extended side panel. Gated on an UPPER with side_front_profile
        on AND the sides actually dropped (extend_sides_down > 0). A no-op +
        full cleanup otherwise, so toggling off restores the square legs."""
        on = (layout.cabinet_type == 'UPPER'
              and getattr(layout, 'side_front_profile', False)
              and getattr(layout, 'extend_sides_down', False)
              and getattr(layout, 'extend_sides_down_amount', 0.0) > 0.0)
        if not on:
            self._cleanup_side_profile_cutters()
            return
        for side, role in (('LEFT', PART_ROLE_LEFT_SIDE),
                           ('RIGHT', PART_ROLE_RIGHT_SIDE)):
            part = self._side_part_by_role(role)
            if part is None:
                continue
            cutter = self._ensure_side_profile_cutter(side)
            self._position_side_profile_cutter(cutter, side, layout)
            mod = part.modifiers.get(SIDE_PROFILE_CUT_MOD_NAME)
            if mod is None:
                mod = part.modifiers.new(
                    name=SIDE_PROFILE_CUT_MOD_NAME, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
            if mod.object is not cutter:
                mod.object = cutter

    # =====================================================================
    # Bottom-rail decorative profile cut (valance)
    # =====================================================================
    def _bottom_rail_parts(self):
        return [c for c in self.obj.children_recursive
                if c.get('hb_part_role') == PART_ROLE_BOTTOM_RAIL]

    def _ensure_bottom_rail_profile_cutter(self, seg_key):
        for child in self.obj.children:
            if (child.get('hb_part_role') == PART_ROLE_BOTTOM_RAIL_PROFILE_CUTTER
                    and child.get('hb_profile_seg') == seg_key):
                return child
        name = 'Bottom Rail Profile Cutter ' + str(seg_key)
        mesh = bpy.data.meshes.new(name)
        cutter = bpy.data.objects.new(name, mesh)
        cutter['hb_part_role'] = PART_ROLE_BOTTOM_RAIL_PROFILE_CUTTER
        cutter['hb_profile_seg'] = seg_key
        cutter.parent = self.obj
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in self.obj.users_collection:
            coll.objects.link(cutter)
            break
        return cutter

    def _position_bottom_rail_profile_cutter(self, cutter, rail, profile_id, poly):
        """Rebuild the cutter prism aligned to the rail: profile X -> rail
        Length, profile Y -> up from the rail's bottom edge (rail local Y=0),
        extruded through the rail Thickness. Built in cabinet-local coords via
        the rail's matrix_local (rails are direct children of the root). ARCH
        generates a smooth circular arc; every other profile 3-slices its
        authored curve. Returns False (and clears the mesh) when too short."""
        part = GeoNodeCutpart(rail)
        try:
            length = part.get_input('Length')
            thickness = part.get_input('Thickness')
        except Exception:
            return False
        # Inset the cut from each rail end by a flat margin: it spans
        # [margin, length - margin], leaving uncut rail at each end.
        margin = BOTTOM_RAIL_PROFILE_END_MARGIN
        inner_len = length - 2.0 * margin
        if profile_id == _BOTTOM_RAIL_PROFILE_ARCH:
            rpoly = _bottom_rail_arch_poly(inner_len)
        else:
            rpoly = _bottom_rail_profile_stretched(poly, inner_len)
        if not rpoly:
            cutter.data.clear_geometry()
            return False
        rpoly = [(px + margin, py) for (px, py) in rpoly]
        # Extrude symmetrically past BOTH faces so the cut passes fully through
        # the rail regardless of which way its local thickness axis points (the
        # rail mesh runs 0..-Thickness in local Z, not 0..+Thickness).
        eps = inch(0.1)
        zt = thickness + eps
        ml = rail.matrix_local
        bm = bmesh.new()
        loop0, loop1 = [], []
        for (px, py) in rpoly:
            loop0.append(bm.verts.new(ml @ Vector((px, py, -zt))))
            loop1.append(bm.verts.new(ml @ Vector((px, py, zt))))
        bm.faces.new(loop0)
        bm.faces.new(list(reversed(loop1)))
        n = len(rpoly)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((loop0[i], loop0[j], loop1[j], loop1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(cutter.data)
        bm.free()
        cutter.location = (0.0, 0.0, 0.0)
        cutter.rotation_euler = (0.0, 0.0, 0.0)
        return True

    def _cleanup_bottom_rail_profile_cutters(self):
        """Reverse of _apply_bottom_rail_profile. No-op when nothing to undo."""
        for rail in self._bottom_rail_parts():
            mod = rail.modifiers.get(BOTTOM_RAIL_PROFILE_CUT_MOD_NAME)
            if mod is not None:
                rail.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_BOTTOM_RAIL_PROFILE_CUTTER:
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    def _apply_bottom_rail_profile(self, layout):
        """Cut the chosen decorative profile into the bottom rail(s). Gated on a
        BASE / UPPER with bottom_rail_profile set; a no-op + full cleanup
        otherwise. One cutter per bottom-rail segment; the profile's end details
        stay fixed while its flat middle stretches to each rail's length."""
        cab_props = self.obj.face_frame_cabinet
        profile_id = getattr(cab_props, 'bottom_rail_profile', 'NONE')
        on = (layout.cabinet_type in ('BASE', 'UPPER')
              and profile_id not in ('NONE', ''))
        is_arch = profile_id == _BOTTOM_RAIL_PROFILE_ARCH
        poly = None if (not on or is_arch) else _bottom_rail_profile_poly(profile_id)
        if not on or (not is_arch and not poly):
            self._cleanup_bottom_rail_profile_cutters()
            return
        live_keys = set()
        for rail in self._bottom_rail_parts():
            seg_key = rail.get('hb_segment_start_bay')
            if seg_key is None:
                seg_key = rail.name
            live_keys.add(seg_key)
            cutter = self._ensure_bottom_rail_profile_cutter(seg_key)
            ok = self._position_bottom_rail_profile_cutter(cutter, rail, profile_id, poly)
            mod = rail.modifiers.get(BOTTOM_RAIL_PROFILE_CUT_MOD_NAME)
            if not ok:
                if mod is not None:
                    rail.modifiers.remove(mod)
                continue
            if mod is None:
                mod = rail.modifiers.new(
                    name=BOTTOM_RAIL_PROFILE_CUT_MOD_NAME, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
            if mod.object is not cutter:
                mod.object = cutter
        # Drop cutters whose rail segment no longer exists.
        for child in list(self.obj.children):
            if (child.get('hb_part_role') == PART_ROLE_BOTTOM_RAIL_PROFILE_CUTTER
                    and child.get('hb_profile_seg') not in live_keys):
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    # =====================================================================
    # Over-stool leg accessories (shelf / towel bar between the legs)
    # =====================================================================
    def _overstool_interior(self, layout):
        """(left_inner_x, right_inner_x, front_y, leg_bottom_z) for the gap
        between the two extended legs - shared by the shelf and towel bar.
        left/right inner = side outer x +/- its thickness; front = leg front
        edge (y = -depth); leg_bottom = the dropped side bottom z."""
        lp = solver.left_side_position(layout); ld = solver.left_side_dims(layout)
        rp = solver.right_side_position(layout); rd = solver.right_side_dims(layout)
        left_inner = lp[0] + ld[2]
        right_inner = rp[0] - rd[2]
        front_y = lp[1] - ld[1]
        return left_inner, right_inner, front_y, lp[2]

    def _ensure_overstool_shelf(self):
        """Find or lazily create the leg shelf CabinetPart - a flat slab
        tagged PART_ROLE_OVERSTOOL_SHELF + CABINET_PART so the material walk
        gives it the exterior finish. Reused across recalcs."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_OVERSTOOL_SHELF:
                return child
        shelf = CabinetPart()
        shelf.create('Leg Shelf')
        shelf.obj.parent = self.obj
        shelf.obj['hb_part_role'] = PART_ROLE_OVERSTOOL_SHELF
        shelf.obj['CABINET_PART'] = True
        # Length -> +X (between legs), Width -> -Y (Mirror Y) so the shelf
        # runs from the back (y=0) forward, Thickness -> +Z (up).
        shelf.set_input('Mirror Y', True)
        shelf.set_input('Mirror Z', False)
        return shelf.obj

    def _position_overstool_shelf(self, shelf_obj, layout):
        """Span the shelf between the leg inner faces, back-aligned (origin at
        y=0, Mirror Y runs it forward), 6" deep, its bottom flush with the
        leg bottom (OVERSTOOL_SHELF_Z_ABOVE_LEG_BOTTOM up from it)."""
        left_inner, right_inner, _front_y, leg_bottom = self._overstool_interior(layout)
        part = GeoNodeCutpart(shelf_obj)
        part.set_input('Length', right_inner - left_inner)
        part.set_input('Width', OVERSTOOL_SHELF_DEPTH)
        part.set_input('Thickness', OVERSTOOL_SHELF_THICKNESS)
        z = leg_bottom + OVERSTOOL_SHELF_Z_ABOVE_LEG_BOTTOM
        if layout.overstool_accessory == 'SHELF_AND_TOWEL_BAR':
            z += OVERSTOOL_SHELF_Z_COMBO_RAISE   # tuck the bar below the shelf
        shelf_obj.location = Vector((left_inner, 0.0, z))
        shelf_obj.rotation_euler = (0.0, 0.0, 0.0)

    def _ensure_overstool_towel_bar(self):
        """Find or lazily create the towel-bar MESH object (a round rod).
        Rebuilt each recalc by _position_overstool_towel_bar."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_OVERSTOOL_TOWEL_BAR:
                return child
        mesh = bpy.data.meshes.new('Towel Bar')
        bar = bpy.data.objects.new('Towel Bar', mesh)
        bar['hb_part_role'] = PART_ROLE_OVERSTOOL_TOWEL_BAR
        bar['CABINET_PART'] = True
        bar.parent = self.obj
        for coll in self.obj.users_collection:
            coll.objects.link(bar)
            break
        return bar

    def _position_overstool_towel_bar(self, bar_obj, layout):
        """Rebuild the towel bar as a cylinder spanning the leg inner faces,
        axis along X, OVERSTOOL_TOWEL_BAR_Y_FROM_FRONT back from the leg front
        and OVERSTOOL_TOWEL_BAR_Z_ABOVE_LEG_BOTTOM up from the leg bottom."""
        from mathutils import Matrix
        left_inner, right_inner, front_y, leg_bottom = self._overstool_interior(layout)
        length = right_inner - left_inner
        r = OVERSTOOL_TOWEL_BAR_DIAMETER * 0.5
        bm = bmesh.new()
        # create_cone builds along local Z; rotate 90 about Y so the axis is X.
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False,
            segments=OVERSTOOL_TOWEL_BAR_SEGMENTS,
            radius1=r, radius2=r, depth=length,
            matrix=Matrix.Rotation(math.radians(90.0), 4, 'Y'))
        bm.to_mesh(bar_obj.data)
        bm.free()
        # The towel bar always sits low + back (the same spot it takes in the
        # combo layout), whether or not a shelf is also present.
        z_above = OVERSTOOL_TOWEL_BAR_Z_ABOVE_LEG_BOTTOM - OVERSTOOL_TOWEL_BAR_COMBO_Z_DROP
        y_back = OVERSTOOL_TOWEL_BAR_Y_FROM_FRONT + OVERSTOOL_TOWEL_BAR_COMBO_Y_BACK
        bar_obj.location = Vector(((left_inner + right_inner) * 0.5,
                                   front_y + y_back,
                                   leg_bottom + z_above))
        bar_obj.rotation_euler = (0.0, 0.0, 0.0)

    def _cleanup_overstool_part(self, role):
        """Remove the shelf or towel bar (accessory not wanted / no legs)."""
        for child in list(self.obj.children):
            if child.get('hb_part_role') == role:
                mesh = child.data if child.type == 'MESH' else None
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    def _apply_overstool_accessories(self, layout):
        """Build / remove the leg shelf and towel bar per overstool_accessory.
        Only when the cabinet is an upper with the sides actually extended
        (the accessories hang between the legs). Idempotent + self-cleaning so
        switching the dropdown adds / removes the right parts."""
        legs = (layout.cabinet_type == 'UPPER'
                and getattr(layout, 'extend_sides_down', False)
                and getattr(layout, 'extend_sides_down_amount', 0.0) > 0.0
                and self._has_carcass())
        acc = getattr(layout, 'overstool_accessory', 'SHELF') if legs else None
        if legs and acc in ('SHELF', 'SHELF_AND_TOWEL_BAR'):
            self._position_overstool_shelf(self._ensure_overstool_shelf(), layout)
        else:
            self._cleanup_overstool_part(PART_ROLE_OVERSTOOL_SHELF)
        if legs and acc in ('TOWEL_BAR', 'SHELF_AND_TOWEL_BAR'):
            self._position_overstool_towel_bar(self._ensure_overstool_towel_bar(), layout)
        else:
            self._cleanup_overstool_part(PART_ROLE_OVERSTOOL_TOWEL_BAR)

    def _ensure_wedge_cutter(self):
        """Find or lazily create the wedge cutter MESH object. Hidden in
        the viewport; a boolean still reads its mesh regardless."""
        for child in self.obj.children:
            if child.get('hb_part_role') == PART_ROLE_WEDGE_CUTTER:
                return child
        mesh = bpy.data.meshes.new('Wedge Cutter')
        cutter = bpy.data.objects.new('Wedge Cutter', mesh)
        cutter['hb_part_role'] = PART_ROLE_WEDGE_CUTTER
        cutter.parent = self.obj
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True
        for coll in self.obj.users_collection:
            coll.objects.link(cutter)
            break
        return cutter

    def _position_wedge_cutter(self, cutter_obj, length, height):
        """Rebuild the cutter's triangular-prism mesh from the live wedge
        dims. Cross-section in the Y-Z plane (cabinet back at y=0, front
        at y=-dim_y, floor z=0):
          P1 = (-length, 0)       forward point where the cut meets the bottom
          P2 = (0, height)        upper point where the cut meets the back
          P3 = (+margin, -margin) back-bottom corner pushed past the faces
        Extruded along X from -margin to dim_x + margin so it spans both
        side panels. Differencing the prism chamfers the back-bottom corner.
        """
        margin = inch(0.5)
        dim_x = self.obj.face_frame_cabinet.width
        p1 = (-length, 0.0)
        p2 = (0.0, height)
        p3 = (margin, -margin)
        x_min, x_max = -margin, dim_x + margin
        bm = bmesh.new()
        v1L = bm.verts.new((x_min, p1[0], p1[1]))
        v2L = bm.verts.new((x_min, p2[0], p2[1]))
        v3L = bm.verts.new((x_min, p3[0], p3[1]))
        v1R = bm.verts.new((x_max, p1[0], p1[1]))
        v2R = bm.verts.new((x_max, p2[0], p2[1]))
        v3R = bm.verts.new((x_max, p3[0], p3[1]))
        bm.verts.ensure_lookup_table()
        bm.faces.new((v1L, v2L, v3L))
        bm.faces.new((v1R, v3R, v2R))
        bm.faces.new((v1L, v1R, v2R, v2L))
        bm.faces.new((v2L, v2R, v3R, v3L))
        bm.faces.new((v3L, v3R, v1R, v1L))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(cutter_obj.data)
        bm.free()
        cutter_obj.location = (0.0, 0.0, 0.0)

    def _iter_wedge_cut_targets(self):
        """Root cage + carcass parts whose back-bottom corner the wedge
        chamfers. Mirrors _iter_angled_cut_targets."""
        yield self.obj
        stack = list(self.obj.children)
        while stack:
            obj = stack.pop()
            role = obj.get('hb_part_role')
            if role == PART_ROLE_WEDGE_CUTTER:
                continue
            if role in WEDGE_CUT_PART_ROLES:
                yield obj
            stack.extend(obj.children)

    def _apply_wedge_cuts(self, cutter_obj):
        """Ensure every target carries a boolean DIFFERENCE modifier named
        WEDGE_CUT_MOD_NAME pointing at the cutter. Idempotent; safe every
        recalc."""
        for part in self._iter_wedge_cut_targets():
            mod = part.modifiers.get(WEDGE_CUT_MOD_NAME)
            if mod is None:
                mod = part.modifiers.new(name=WEDGE_CUT_MOD_NAME, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
            if mod.object is not cutter_obj:
                mod.object = cutter_obj

    def _cleanup_wedge_cutter_and_cuts(self):
        """Reverse of _apply_wedge_cuts + _ensure_wedge_cutter. No-op when
        there's nothing to undo."""
        for part in self._iter_wedge_cut_targets():
            mod = part.modifiers.get(WEDGE_CUT_MOD_NAME)
            if mod is not None:
                part.modifiers.remove(mod)
        for child in list(self.obj.children):
            if child.get('hb_part_role') == PART_ROLE_WEDGE_CUTTER:
                mesh = child.data
                bpy.data.objects.remove(child, do_unlink=True)
                if mesh is not None and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    # =====================================================================
    # Applied finished-end panels (parented panel roots covering a side)
    # =====================================================================
    def _reconcile_applied_panels(self, layout):
        """Sync applied panel children to the cabinet's three side
        finished-end conditions. For each side whose condition is in
        APPLIED_PANEL_END_TYPES, ensure a panel root exists, parented
        and tagged with the side. Resize / reposition existing panels
        without rebuilding their bay/opening structure - so user edits
        (splits, front-type changes, mid-stile widths) survive.
        """
        cab = self.obj.face_frame_cabinet
        side_conditions = {
            'LEFT':  cab.left_finished_end_condition,
            'RIGHT': cab.right_finished_end_condition,
            'BACK':  cab.back_finished_end_condition,
        }

        # Index existing applied panels by side. Multiple per side
        # shouldn't happen, but if it does we keep the first and remove
        # extras to converge on a clean state.
        existing = {}
        extras = []
        for child in self.obj.children:
            side = child.get(TAG_APPLIED_PANEL_SIDE)
            if not side:
                continue
            if side in existing:
                extras.append(child)
            else:
                existing[side] = child
        for child in extras:
            _remove_root_with_children(child)

        for side, condition in side_conditions.items():
            wants_panel = condition in APPLIED_PANEL_END_TYPES
            panel_obj = existing.get(side)

            if not wants_panel:
                if panel_obj is not None:
                    _remove_root_with_children(panel_obj)
                continue

            if panel_obj is None:
                panel = PanelFaceFrameCabinet()
                panel.create(f'Applied Panel {side[0]}', bay_qty=1)
                panel_obj = panel.obj
                panel_obj.parent = self.obj
                panel_obj[TAG_APPLIED_PANEL_SIDE] = side

            # Stamp the parent cabinet's style onto the panel root so the
            # panel's own recalc tail (_reapply_cabinet_style) materials its
            # parts. The inset-panel fronts and the auto split mid-rails /
            # mid-stiles are torn down and rebuilt every recalc; with no
            # STYLE_NAME the panel's own recalc leaves the rebuilt parts
            # unmaterialed (rendered white). A parent recalc would walk
            # them, but a panel-scoped recalc (e.g. the panel dim writes
            # below) has no following parent walk. _apply_door_styles_to_
            # fronts is a no-op on INSET_PANEL roles, so this only adds the
            # finish. Re-stamped each reconcile to track a parent restyle.
            parent_style = self.obj.get('STYLE_NAME')
            if parent_style:
                panel_obj['STYLE_NAME'] = parent_style

            location, rotation_z, width, height, depth = (
                applied_panel_geometry(layout, side)
            )
            # Finished-end overhang (applied panel). BACK is rotated 180
            # so panel +X runs cabinet -X from origin x=dim_x: extend_left
            # widens the far end past x=0, extend_right shifts the origin
            # +X and widens. LEFT (rotZ=-90, +X->-Y) has its back edge at
            # the origin, so a back overhang shifts origin +Y and widens.
            # RIGHT (rotZ=+90, +X->+Y) has its back edge at the FAR end,
            # so a back overhang only widens.
            if side == 'BACK':
                # Trim the paneled back at each end that carries a return
                # closeout so it butts the return post instead of running
                # behind it. Rotated 180, the origin is the RIGHT end, so a
                # right return shifts the origin -X and narrows; a left return
                # (far end) only narrows - mirroring the extend_r / extend_l
                # grows below.
                ret_l = self._finished_side_return_width(cab, layout, 'LEFT')
                ret_r = self._finished_side_return_width(cab, layout, 'RIGHT')
                location = (location[0] + cab.back_finished_extend_right - ret_r,
                            location[1], location[2])
                width = (width + cab.back_finished_extend_left
                         + cab.back_finished_extend_right - ret_l - ret_r)
            elif side == 'LEFT':
                eb = cab.left_side_finished_extend_back
                location = (location[0], location[1] + eb, location[2])
                width = width + eb
            else:  # RIGHT
                width = width + cab.right_side_finished_extend_back
            panel_obj.location = location
            panel_obj.rotation_euler = (0.0, 0.0, rotation_z)
            panel_props = panel_obj.face_frame_cabinet
            # Writing width / height / depth fires _update_cabinet_dim
            # on the panel root which calls recalculate_face_frame_cabinet
            # on IT. The _RECALCULATING guard is keyed by id(root), so
            # the cabinet's outer recalc isn't blocked - the panel runs
            # its own recalc. Three writes -> three panel recalcs; cheap,
            # panels are small.
            panel_props.width = width
            panel_props.height = height
            panel_props.depth = depth

            # Sizing first - apply_panel_split_structure reads the
            # panel's bay.location.z to compute the mid rail position,
            # and bay.location.z is downstream of the panel's
            # bottom_rail_width, which apply_panel_sizing sets. If
            # sizing runs second, the split rebuild reads the panel's
            # DEFAULT bot_rail (1.5") instead of the correct value
            # (door rail + bay bottom rail + ...) and the mid rail
            # lands too high. The split rebuild does NOT modify the
            # panel's only bay - only its descendants - so it's safe
            # for sizing to run first.
            from . import applied_panel_sizing
            applied_panel_sizing.apply_panel_sizing(
                self.obj, panel_obj, side, condition,
            )
            applied_panel_sizing.apply_panel_split_structure(
                self.obj, panel_obj, side,
            )
            # Toe-kick corner notch on bottom rail + facing stile.
            # No-op for BACK panels and non-NOTCH toe kicks.
            applied_panel_sizing.apply_panel_toe_kick_notch(
                self.obj, panel_obj, side,
            )

            # Stamp a right-click menu onto the panel's menu-less parts
            # (inset panel fronts, pivots) so clicking any part of the
            # applied panel surfaces the panel's own prompts via the
            # part-commands menu. Face-frame parts already carry that
            # MENU_ID; cabinet_prompts resolves to the panel root.
            for part in panel_obj.children_recursive:
                if part.get('hb_part_role') and not part.get('MENU_ID'):
                    part['MENU_ID'] = (
                        'HOME_BUILDER_MT_face_frame_part_commands')

    # =====================================================================
    # Applied finished back (single 3/4 part layered on the carcass back)
    # =====================================================================
    def _reconcile_finished_back(self, layout):
        """Spawn / resize / remove the FINISHED back applied panel.

        Triggered only when back_finished_end_condition == 'FINISHED'.
        The carcass back itself stays at its normal back_thickness;
        this method just adds (or removes) a single 3/4 panel sitting
        directly behind it. Same delete-on-condition-change /
        resize-in-place pattern as the applied panels - the part holds
        no user state, so reuse-when-present keeps it stable across
        recalcs without rebuilding.

        Spans the full cabinet width (less any per-side return closeout,
        which trims that end so the back butts the return post) and full
        cabinet height. Refining for stepped cabinets or excluding the toe
        kick is deferred.
        """
        cab = self.obj.face_frame_cabinet
        wants = cab.back_finished_end_condition == 'FINISHED'
        existing = next(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_FINISHED_BACK),
            None,
        )

        if not wants:
            if existing is not None:
                bpy.data.objects.remove(existing, do_unlink=True)
            return

        thickness = inch(0.75)
        if existing is None:
            part = CabinetPart()
            part.create('Finished Back')
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_FINISHED_BACK
            part.obj['CABINET_PART'] = True
            # Same orientation as the carcass back: rotation x=90 / y=-90
            # with Mirror Y=True extrudes Thickness in -Y from origin.
            # Origin sits at Y=+thickness so the part fills [0, thickness]
            # in cabinet Y - flush against the carcass back's outer face,
            # extending behind the cabinet by 3/4.
            part.obj.rotation_euler.x = math.radians(90)
            part.obj.rotation_euler.y = math.radians(-90)
            part.set_input('Mirror Y', True)
            existing = part.obj
        else:
            part = GeoNodeCutpart(existing)

        # Finished-end overhang: grow the panel past the cabinet's left
        # (-X) / right (+X) end. Width spans +X from origin x=0, so
        # extending the left end shifts the origin -X and widens; the
        # right end just widens. Negative values inset that edge.
        ext_l = cab.back_finished_extend_left
        ext_r = cab.back_finished_extend_right
        # Shorten the back at each end that carries a return closeout so it
        # butts the return post's outer face instead of running behind it.
        # The return panel's outer face sits `return width` in from that
        # side's outer face, so trimming the back by the same amount (and
        # shifting the origin +X for a left return) lands them flush.
        ret_l = self._finished_side_return_width(cab, layout, 'LEFT')
        ret_r = self._finished_side_return_width(cab, layout, 'RIGHT')
        existing.location = (-ext_l + ret_l, thickness, 0.0)
        part.set_input('Length',    layout.dim_z)
        part.set_input('Width',     layout.dim_x + ext_l + ext_r - ret_l - ret_r)
        part.set_input('Thickness', thickness)

    def _extend_finished_side_panels(self, layout):
        """Run a FINISHED carcass side panel past the cabinet back by the
        per-side extend amount.

        Only the carcass-side FINISHED case lives here. An applied /
        beadboard / shiplap side carries its overhang on its own applied
        part (handled in that reconciler); a FINISHED side has no applied
        part - the carcass side IS the finished face - so it is grown
        directly.

        The side panel's origin sits at its back edge (cabinet Y=0) with
        Width (depth) extruding -Y, so a positive extend shifts the origin
        +Y and widens, pushing the back out while the square front edge
        stays put (verified empirically). The Width base is recomputed from
        the solver rather than read back, so the extend never accumulates;
        the part loop has already written the square location/Width this
        recalc, so a zero extend needs no reset (self-correcting).

        Skipped in angled mode, where the side geometry is reshaped by the
        angled cutter / trapezoidal back (§18) and a naive +Y grow would
        fight those passes - left as a v1 limit.
        """
        if layout.is_angled:
            return
        cab = self.obj.face_frame_cabinet
        specs = (
            (PART_ROLE_LEFT_SIDE, cab.left_finished_end_condition,
             cab.left_side_finished_extend_back, solver.left_side_dims),
            (PART_ROLE_RIGHT_SIDE, cab.right_finished_end_condition,
             cab.right_side_finished_extend_back, solver.right_side_dims),
        )
        for role, condition, extend, dims_fn in specs:
            if condition != 'FINISHED' or extend == 0.0:
                continue
            child = next((c for c in self.obj.children
                          if c.get('hb_part_role') == role), None)
            if child is None or child.hide_viewport:
                continue
            base_width = dims_fn(layout)[1]  # (length, width=depth, thickness)
            child.location.y += extend
            GeoNodeCutpart(child).set_input('Width', base_width + extend)

    def _finished_side_return_width(self, cab, layout, side):
        """Effective return-closeout width on `side` ('LEFT' / 'RIGHT'), or
        0.0 when the return isn't active. Active requires a non-angled
        cabinet, a FINISHED or PANELED back to return into, and that side
        being FINISHED or PANELED, extended back (extend > 0), with a
        positive return width.
        Single source of truth shared by the return-part builder and the
        back sizing (the finished-back cutpart or the paneled applied-back
        panel is shortened by this width so it butts the return post
        instead of running behind it).
        """
        if layout.is_angled:
            return 0.0
        if cab.back_finished_end_condition not in ('FINISHED', 'PANELED'):
            return 0.0
        if side == 'LEFT':
            condition = cab.left_finished_end_condition
            extend = cab.left_side_finished_extend_back
            width = cab.left_side_return_width
        else:
            condition = cab.right_finished_end_condition
            extend = cab.right_side_finished_extend_back
            width = cab.right_side_return_width
        if condition not in ('FINISHED', 'PANELED') or extend <= 0.0 or width <= 0.0:
            return 0.0
        return width

    def _reconcile_finished_side_returns(self, layout):
        """Spawn / resize / remove the return closeout on a FINISHED or
        PANELED side that is extended back past a FINISHED or PANELED back.

        Coordinate frame: cabinet back plane at Y=0, body toward -Y, and an
        extended side grows in +Y to its rear edge at Y=extend. The closeout
        wraps that exposed back corner with two 3/4-deep members:

          * RETURN panel - parallel to the side, depth = the side's extend-back
            amount, running Y[0, extend] so its front edge dies into the
            (shortened) back. Sits inboard of the side outer face by the return
            width (behind the stile).
          * STILE - the rearmost / outermost member, X-span = the return width,
            capping the rear at Y[extend, extend+3/4]. Runs full height to the
            floor.

        Each member is a flat FINISHED cutpart (default) or a PANELED applied
        panel (PanelFaceFrameCabinet) per its *_return_panel_type /
        *_return_stile_type prop; both kinds occupy the same footprint, so the
        inner_x-keyed back shortening is unaffected by the choice.

        Gated (via _finished_side_return_width) on the side being FINISHED or
        PANELED, extended back (extend>0), a nonzero return width, and a
        FINISHED or PANELED back to return into. Anything failing the gate
        removes both parts (idempotent). Skipped in angled mode, matching
        _extend_finished_side_panels.
        """
        cab = self.obj.face_frame_cabinet
        thk = inch(0.75)  # 3/4 finished stock / applied-panel depth
        # outer_x = the side's visible outer face = the face-frame outer face
        # (X=0 left, dim_x right); correct for FINISHED and PANELED sides (do
        # NOT use the scribe offset, which is 0.75 for PANELED). mirror_z sets
        # the finished return panel's Thickness direction: OFF left / ON right,
        # so its body runs toward the side and its inboard face lands at
        # inner_x, where the shortened back butts it.
        specs = (
            ('LEFT', PART_ROLE_LEFT_SIDE_RETURN,
             PART_ROLE_LEFT_SIDE_RETURN_STILE,
             cab.left_side_finished_extend_back, cab.left_side_return_width,
             0.0, False, cab.left_side_return_panel_type,
             cab.left_side_return_stile_type),
            ('RIGHT', PART_ROLE_RIGHT_SIDE_RETURN,
             PART_ROLE_RIGHT_SIDE_RETURN_STILE,
             cab.right_side_finished_extend_back, cab.right_side_return_width,
             layout.dim_x, True, cab.right_side_return_panel_type,
             cab.right_side_return_stile_type),
        )
        for (side, return_role, stile_role, extend, return_width, outer_x,
             mirror_z, panel_type, stile_type) in specs:
            wants = self._finished_side_return_width(cab, layout, side) > 0.0
            # inner_x = the return panel's inboard face (where the shortened
            # back butts) = return width in from the outer face.
            inboard = 1.0 if side == 'LEFT' else -1.0
            inner_x = outer_x + inboard * return_width

            # ---- Return panel ----
            # Finished: side-oriented cutpart (rot Y=-90), Width=depth=extend,
            # Thickness toward the outer face (mirror_z). Paneled: applied
            # panel, width=extend along +Y (rot Z=+90), body on the same side
            # of inner_x as the finished part.
            rp_origin_x = inner_x if side == 'RIGHT' else inner_x - thk
            self._reconcile_return_member(
                return_role, wants, panel_type, 'Side Return ' + side[0],
                finished=dict(loc=(inner_x, extend, 0.0), rot_x=0.0,
                              mirror_z=mirror_z, length=layout.dim_z,
                              width=extend, thickness=thk),
                paneled=dict(loc=(rp_origin_x, 0.0, 0.0),
                             rot_z=math.radians(90), width=extend,
                             height=layout.dim_z, depth=thk, side=side))

            # ---- Rear stile ----
            # Finished: back-oriented cutpart (rot X=90, Y=-90), Width=return
            # width in +X from the lower-X end, 3/4 cap at Y=extend..+3/4.
            # Paneled: applied panel facing rear (rot Z=180), same rear cap.
            self._reconcile_return_member(
                stile_role, wants, stile_type, 'Side Return Stile ' + side[0],
                finished=dict(loc=(min(outer_x, inner_x), extend + thk, 0.0),
                              rot_x=math.radians(90), mirror_z=False,
                              length=layout.dim_z, width=return_width,
                              thickness=thk),
                paneled=dict(loc=(max(outer_x, inner_x), extend, 0.0),
                             rot_z=math.radians(180), width=return_width,
                             height=layout.dim_z, depth=thk, side=side))

    def _reconcile_return_member(self, role, wants, kind, name,
                                 finished, paneled):
        """Build / resize / remove one return member (the return panel or the
        rear stile) as a flat FINISHED cutpart or a PANELED applied panel.
        Found by TAG_RETURN_MEMBER (falling back to the legacy hb_part_role
        tag on pre-type parts); a kind change or a failed gate removes the
        existing member the right way and rebuilds. `finished` / `paneled` are
        geometry dicts built by the caller.
        """
        existing = next((c for c in self.obj.children
                         if c.get(TAG_RETURN_MEMBER) == role
                         or c.get('hb_part_role') == role), None)
        if not wants:
            if existing is not None:
                self._remove_return_member(existing)
            return
        current_kind = (existing.get('hb_return_member_kind', 'FINISHED')
                        if existing is not None else None)
        if existing is not None and current_kind != kind:
            self._remove_return_member(existing)
            existing = None
        if kind == 'PANELED':
            self._build_return_paneled(role, name, existing, paneled)
        else:
            self._build_return_finished(role, name, existing, finished)

    def _build_return_finished(self, role, name, existing, geo):
        """Flat 3/4 finished cutpart. rot_x distinguishes the side-oriented
        return panel (0) from the back-oriented stile (90); both add Y=-90.
        """
        if existing is None:
            part = CabinetPart()
            part.create(name)
            part.obj.parent = self.obj
            part.obj['CABINET_PART'] = True
            part.obj.rotation_euler.x = geo['rot_x']
            part.obj.rotation_euler.y = math.radians(-90)
            part.set_input('Mirror Y', True)
            part.set_input('Mirror Z', geo['mirror_z'])
            existing = part.obj
        else:
            part = GeoNodeCutpart(existing)
        existing['hb_part_role'] = role
        existing[TAG_RETURN_MEMBER] = role
        existing['hb_return_member_kind'] = 'FINISHED'
        existing.location = geo['loc']
        part.set_input('Length', geo['length'])
        part.set_input('Width', geo['width'])
        part.set_input('Thickness', geo['thickness'])

    def _build_return_paneled(self, role, name, existing, geo):
        """PANELED applied panel (PanelFaceFrameCabinet) filling the member's
        footprint (width along its long axis, 3/4 depth, frame face outward),
        stamped with the parent style so its rebuilt parts get the finish.
        """
        if existing is None:
            panel = PanelFaceFrameCabinet()
            panel.create(name, bay_qty=1)
            existing = panel.obj
            existing.parent = self.obj
        existing[TAG_RETURN_MEMBER] = role
        existing['hb_return_member_kind'] = 'PANELED'
        parent_style = self.obj.get('STYLE_NAME')
        if parent_style:
            existing['STYLE_NAME'] = parent_style
        existing.location = geo['loc']
        existing.rotation_euler = (0.0, 0.0, geo['rot_z'])
        pp = existing.face_frame_cabinet
        pp.width = geo['width']
        pp.height = geo['height']
        pp.depth = geo['depth']
        # Match the top / bottom rail widths to the cabinet's side panels.
        self._match_return_member_rails(existing, geo['side'])

    def _match_return_member_rails(self, panel_obj, side):
        """Set a paneled return member's top / bottom rail widths to match the
        cabinet's PANELED side panels, so the rails read consistently with the
        sides. Uses the same auto-size resolver against that side's condition
        (falling back to PANELED when the side itself isn't an applied-panel
        type); skipped when auto sizing is off, exactly like the side panels.
        Only the rails are matched - stiles stay the member's own. Rails render
        per-bay as well as at panel level, so both are written; per-part unlock
        overrides are respected.
        """
        from . import applied_panel_sizing
        cab = self.obj.face_frame_cabinet
        side_cond = (cab.left_finished_end_condition if side == 'LEFT'
                     else cab.right_finished_end_condition)
        cond = side_cond if side_cond in APPLIED_PANEL_END_TYPES else 'PANELED'
        sizes = applied_panel_sizing.resolve_panel_sizing(self.obj, side, cond)
        if sizes is None:
            return
        top_rw = sizes['top_rail_width']
        bot_rw = sizes['bottom_rail_width']
        pp = panel_obj.face_frame_cabinet
        with suspend_recalc():
            if not pp.unlock_top_rail:
                pp.top_rail_width = top_rw
            if not pp.unlock_bottom_rail:
                pp.bottom_rail_width = bot_rw
            for child in panel_obj.children_recursive:
                if not child.get(TAG_BAY_CAGE):
                    continue
                bay = child.face_frame_bay
                if not bay.unlock_top_rail:
                    bay.top_rail_width = top_rw
                if not bay.unlock_bottom_rail:
                    bay.bottom_rail_width = bot_rw

    def _remove_return_member(self, obj):
        """Remove a return member; paneled members are roots with children."""
        if obj.get('hb_return_member_kind') == 'PANELED':
            _remove_root_with_children(obj)
        else:
            bpy.data.objects.remove(obj, do_unlink=True)

    # =====================================================================
    # Applied flush-X strips (single 1/4 part on the front of a side)
    # =====================================================================
    def _reconcile_full_overlay_stiles(self, layout):
        """Full-overlay cabinets with a WALL end stile get an extra
        1.25\"-wide face-frame part doubled in FRONT of that stile, the
        height of the door front, flush to the cabinet side. Spawn / resize
        / remove per side. Mirrors the end-stile build (rotation + mirror
        flags) shifted one face-frame thickness forward.
        """
        cab = self.obj.face_frame_cabinet
        is_full = _resolve_style_overlay(self.obj) == 'FULL'
        last = layout.bay_count - 1
        side_specs = (
            ('LEFT',  cab.left_stile_type,  0,    0.0),
            ('RIGHT', cab.right_stile_type, last, solver.face_frame_length(layout)),
        )
        existing = {
            child.get(TAG_FO_STILE_SIDE): child
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_FULL_OVERLAY_STILE
            and child.get(TAG_FO_STILE_SIDE) in ('LEFT', 'RIGHT')
        }
        width = inch(1.25)
        for side, stile_type, bi, ff_x in side_specs:
            wants = is_full and stile_type == 'WALL'
            part_obj = existing.get(side)
            if not wants:
                if part_obj is not None:
                    bpy.data.objects.remove(part_obj, do_unlink=True)
                continue
            bay = layout.bays[bi]
            bottom_rail = solver.effective_bottom_rail_width(layout, bi)
            # Door front = clear opening + the top/bottom overlay it laps.
            opening_h = (bay['height'] - bay['top_rail_width']
                         - bottom_rail - bay['kick_height'])
            door_h = (opening_h + layout.default_top_overlay
                      + layout.default_bottom_overlay)
            door_bottom_z = (solver.bay_bottom_z(layout, bi) + bottom_rail
                             - layout.default_bottom_overlay)
            # One fft FORWARD of the FF outer plane -> right in front of
            # the stile (perp_offset positive is INTO the cabinet).
            pos = solver.ff_perpendicular_offset(
                layout, ff_x, -layout.fft, door_bottom_z)
            if part_obj is None:
                part = CabinetPart()
                part.create(f'FO Stile {side[0]}')
                part.obj.parent = self.obj
                part.obj['hb_part_role'] = PART_ROLE_FULL_OVERLAY_STILE
                part.obj['CABINET_PART'] = True
                part.obj[TAG_FO_STILE_SIDE] = side
                part.obj.rotation_euler.y = math.radians(-90)
                part.obj.rotation_euler.z = math.radians(90)
                part.set_input('Mirror Y', side == 'LEFT')
                part.set_input('Mirror Z', True)
                part_obj = part.obj
            else:
                part = GeoNodeCutpart(part_obj)
            part_obj.location = pos
            part.set_input('Length', door_h)
            part.set_input('Width', width)
            part.set_input('Thickness', layout.fft)

    def _reconcile_flush_x_strips(self, layout):
        """Spawn / resize / remove the FLUSH_X applied strip on each
        side. Triggered when *_finished_end_condition == 'FLUSH_X'.

        The strip is a single 1/4 thick part. Outer face flush with
        the cabinet's exterior side plane (X=0 on left, dim_x on
        right); inner face touches the side panel since FLUSH_X auto-
        scribes to 1/4 in the solver. Y starts at the back of the
        face frame (lined up with the side panel) and extends back
        into the cabinet by *_flush_x_amount. Z span matches the side
        panel.
        """
        cab = self.obj.face_frame_cabinet
        side_specs = (
            ('LEFT',  cab.left_finished_end_condition,
             cab.left_flush_x_amount, 0),
            ('RIGHT', cab.right_finished_end_condition,
             cab.right_flush_x_amount, layout.bay_count - 1),
        )

        existing = {
            child.get(TAG_FLUSH_X_SIDE): child
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_FLUSH_X
            and child.get(TAG_FLUSH_X_SIDE) in ('LEFT', 'RIGHT')
        }

        for side, condition, amount, bay_index in side_specs:
            wants = condition == 'FLUSH_X'
            strip = existing.get(side)

            if not wants:
                if strip is not None:
                    bpy.data.objects.remove(strip, do_unlink=True)
                continue

            thickness = inch(0.25)
            # Run the strip the full height of the cabinet side. For
            # NOTCH / FLUSH toe kicks side_bottom_z is the floor (0.0),
            # so the strip drops to the floor like the carcass side it
            # covers instead of stopping at the top of the kick. FLOATING
            # / uppers keep it at the bay bottom (side_bottom_z ==
            # bay_bottom_z there), preserving the old behavior.
            bottom_z = solver.side_bottom_z(layout, bay_index, side)
            top_z = (solver.left_side_top_z(layout)
                     if side == 'LEFT'
                     else solver.right_side_top_z(layout))
            length = top_z - bottom_z
            # Width along cabinet -Y from origin (Mirror Y=True flips
            # +Y to -Y). Strip's front edge sits at the back of the
            # face frame (-dim_y + fft) so it aligns with the side
            # panel; from there it extends back into the cabinet by
            # `amount`. Origin Y is the strip's back edge:
            #   origin_y - amount = -dim_y + fft   (front edge)
            #   origin_y         = -dim_y + fft + amount (back edge)
            origin_y = -layout.dim_y + layout.fft + amount
            origin_x = 0.0 if side == 'LEFT' else layout.dim_x

            if strip is None:
                part = CabinetPart()
                part.create(f'Flush X {side[0]}')
                part.obj.parent = self.obj
                part.obj['hb_part_role'] = PART_ROLE_FLUSH_X
                part.obj['CABINET_PART'] = True
                part.obj[TAG_FLUSH_X_SIDE] = side
                # Match the carcass side rotation/mirror flags so the
                # strip's Length axis goes +Z, Width goes -Y, Thickness
                # goes +X (left) or -X (right). Mirror Z differs between
                # sides exactly as the carcass sides do.
                part.obj.rotation_euler.y = math.radians(-90)
                part.set_input('Mirror Y', True)
                part.set_input('Mirror Z', side == 'LEFT')
                strip = part.obj
            else:
                part = GeoNodeCutpart(strip)

            strip.location = (origin_x, origin_y, bottom_z)
            part.set_input('Length',    length)
            part.set_input('Width',     amount)
            part.set_input('Thickness', thickness)
            self._drive_flush_x_notch(strip, layout, side, bay_index, thickness)

    def _drive_flush_x_notch(self, strip, layout, side, bay_index, thickness):
        """Drive a FLUSH_X strip's 'Notch Front Bottom' modifier so a
        full-height strip clears the toe-kick recess on base / tall
        cabinets, mirroring _update_side_corner_notch for the carcass
        side it covers. Active only for a NOTCH toe kick when the strip
        actually reaches the floor - not when that side is stile-to-floor,
        kick-inset, a floating bay, or FLUSH / FLOATING / uppers. The
        modifier is added lazily so strips built before notch support are
        upgraded in place on the next recalc. Route Depth cuts the full
        1/4\" strip thickness; the strip shares the side's Mirror Y so
        Flip Y = True targets the front face and Flip X = False the bottom.
        """
        mod = strip.modifiers.get('Notch Front Bottom')
        if mod is None:
            cpm = GeoNodeCutpart(strip).add_part_modifier(
                'CPM_CORNERNOTCH', 'Notch Front Bottom')
            cpm.set_input('Flip X', False)
            cpm.set_input('Flip Y', True)
            mod = cpm.mod
        if mod.node_group is None:
            return
        if side == 'LEFT':
            stile_to_floor = solver.left_stile_to_floor(layout)
            has_inset = layout.kick_inset_left > 0
        else:
            stile_to_floor = solver.right_stile_to_floor(layout)
            has_inset = layout.kick_inset_right > 0
        bay_floating = (
            0 <= bay_index < len(layout.bays)
            and bool(layout.bays[bay_index].get('floating_bay'))
        )
        active = (layout.has_toe_kick
                  and layout.toe_kick_type == 'NOTCH'
                  and not stile_to_floor
                  and not has_inset
                  and not bay_floating
                  and 0 <= bay_index < len(layout.bays))
        if active:
            kick = layout.bays[bay_index]['kick_height']
            setback = self.obj.face_frame_cabinet.toe_kick_setback
            route = thickness
        else:
            kick = setback = route = 0.0
        ng = mod.node_group
        for input_name, value in (
            ('X', kick),
            ('Y', setback),
            ('Route Depth', route),
        ):
            node_input = ng.interface.items_tree.get(input_name)
            if node_input is not None:
                hb_utils.set_gn_input(mod, node_input.identifier, value)
        mod.show_viewport = active
        mod.show_render = active

    # =====================================================================
    # Per-bay finish liner panels (left / right / top / back)
    # =====================================================================
    def _reconcile_bay_finish_panels(self, layout):
        """Spawn / resize / remove finish liner panels for finished bays
        and finished openings.

        A finished region (a whole bay via finish_bay, or a single opening
        via finish_opening) gets 1/4 finish-material liner panels on its
        inner faces so the exterior finish reads inside it. FULL finish
        lines the full cavity depth on five faces (LEFT / RIGHT / TOP /
        BACK / BOTTOM); FLUSH finish lines the FF opening with a band flush
        to the FF front face, running finish_*_flush_depth back (0 = full
        depth) with no BACK panel (open behind for an appliance). A removed
        bay bottom drops the BOTTOM panel and runs the verticals to the
        floor. The geometry is identical for bays and openings - only the
        region bounds differ - so both route through _finish_region_specs.

        A bay-level finish supersedes per-opening finishes within that bay
        (the bay liner already covers everything). Liners are keyed by
        (bay_index, opening_index, face) - opening_index -1 for a bay-level
        liner - so they reuse in place and sweep cleanly. Angled cabinets
        are deferred (bay-local Y here assumes square).
        """
        existing = {}
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_BAY_FINISH:
                continue
            key = (child.get(TAG_BAY_FINISH_BAY),
                   child.get(TAG_BAY_FINISH_OPENING, -1),
                   child.get(TAG_BAY_FINISH_FACE))
            existing[key] = child

        wanted = set()
        if not layout.is_angled:
            t = inch(0.25)
            for bi, bay in enumerate(layout.bays):
                bay_left_x, bay_right_x = solver._cage_x_bounds(layout, bi)
                _, bay_dim_y, bay_dim_z = solver.bay_cage_dims(layout, bi)
                bay_bottom = (solver.bay_bottom_z(layout, bi)
                              + solver.effective_bottom_rail_width(layout, bi))
                bay_top = bay_bottom + bay_dim_z
                bay_to_floor = bool(bay.get('remove_bottom'))

                if bay.get('finish_bay'):
                    region = dict(
                        left_x=bay_left_x, right_x=bay_right_x,
                        bottom_z=bay_bottom, top_z=bay_top,
                        cage_dim_y=bay_dim_y,
                        reveals=solver._bay_root_reveals(layout, bi),
                    )
                    specs = self._finish_region_specs(
                        layout, region, bool(bay.get('finish_bay_flush')),
                        bay.get('finish_bay_flush_depth', 0.0), bay_to_floor, t)
                    for face, spec in specs:
                        self._emit_bay_finish_panel(bi, -1, face, spec, t, existing)
                        wanted.add((bi, -1, face))
                    continue

                # No bay-level finish -> check each opening leaf. The leaf
                # rects are bay-local; the bay cage origin (bay_left_x,
                # bay_bottom) maps them to cabinet-local. An opening only
                # reaches the floor when the bay bottom is removed AND it's
                # the bottom-most leaf (cage_z == 0).
                for leaf in solver.bay_openings(layout, bi)['leaves']:
                    op_obj = bpy.data.objects.get(leaf['obj_name'])
                    if op_obj is None:
                        continue
                    op = op_obj.face_frame_opening
                    if not op.finish_opening:
                        continue
                    oi = leaf['opening_index']
                    op_left_x = bay_left_x + leaf['cage_x']
                    op_bottom = bay_bottom + leaf['cage_z']
                    region = dict(
                        left_x=op_left_x,
                        right_x=op_left_x + leaf['cage_dim_x'],
                        bottom_z=op_bottom,
                        top_z=op_bottom + leaf['cage_dim_z'],
                        cage_dim_y=leaf['cage_dim_y'],
                        reveals={'left':   leaf['reveal_left'],
                                 'right':  leaf['reveal_right'],
                                 'top':    leaf['reveal_top'],
                                 'bottom': leaf['reveal_bottom']},
                    )
                    op_to_floor = bay_to_floor and abs(leaf['cage_z']) < 1e-6
                    specs = self._finish_region_specs(
                        layout, region, bool(op.finish_opening_flush),
                        op.finish_opening_flush_depth, op_to_floor, t)
                    for face, spec in specs:
                        self._emit_bay_finish_panel(bi, oi, face, spec, t, existing)
                        wanted.add((bi, oi, face))

        for key, child in existing.items():
            if key not in wanted:
                bpy.data.objects.remove(child, do_unlink=True)

    def _finish_region_specs(self, layout, region, flush, raw_depth, to_floor, t):
        """Build the (face, spec) list for one finished region.

        `region` is cabinet-local: left_x / right_x / bottom_z / top_z, the
        cavity depth cage_dim_y, and the four reveals (cage edge -> FF
        opening edge). See _reconcile_bay_finish_panels for the FULL vs
        FLUSH and to_floor semantics; the math here is shared by bays and
        openings.
        """
        left_x = region['left_x']; right_x = region['right_x']
        bottom_z = region['bottom_z']; top_z = region['top_z']
        cage_dim_x = right_x - left_x
        cage_dim_y = region['cage_dim_y']
        rev = region['reveals']
        ff_back_y = -layout.dim_y + layout.fft
        cavity_back_y = ff_back_y + cage_dim_y

        if flush:
            # FLUSH band lining the FF opening, flush with the FF front
            # face. Visible faces sit at the FF opening edges (no reveal)
            # with thickness OUTBOARD (LEFT -X, RIGHT +X, TOP +Z, BOTTOM
            # -Z). No BACK panel - open behind for an appliance.
            op_left_x   = left_x + rev['left']
            op_right_x  = right_x - rev['right']
            op_bottom_z = 0.0 if to_floor else bottom_z + rev['bottom']
            op_top_z    = top_z - rev['top']
            op_height   = op_top_z - op_bottom_z
            op_width    = op_right_x - op_left_x
            ff_front_y  = -layout.dim_y
            max_depth   = layout.fft + cage_dim_y
            depth = max_depth if raw_depth <= 0.0 else min(raw_depth, max_depth)
            band_back_y = ff_front_y + depth   # Mirror-Y anchor edge
            specs = [
                ('LEFT',  dict(rot=(0.0, math.radians(-90), 0.0),
                               mirror_y=True, mirror_z=False,
                               loc=(op_left_x, band_back_y, op_bottom_z),
                               length=op_height, width=depth)),
                ('RIGHT', dict(rot=(0.0, math.radians(-90), 0.0),
                               mirror_y=True, mirror_z=True,
                               loc=(op_right_x, band_back_y, op_bottom_z),
                               length=op_height, width=depth)),
                ('TOP',   dict(rot=(0.0, 0.0, 0.0),
                               mirror_y=True, mirror_z=False,
                               loc=(op_left_x, band_back_y, op_top_z),
                               length=op_width, width=depth)),
            ]
            if not to_floor:
                specs.append(
                    ('BOTTOM', dict(rot=(0.0, 0.0, 0.0),
                                    mirror_y=True, mirror_z=True,
                                    loc=(op_left_x, band_back_y, op_bottom_z),
                                    length=op_width, width=depth)))
        else:
            # FULL finish lining the full cavity depth on the cavity walls.
            vert_bottom_z = 0.0 if to_floor else bottom_z
            vert_height   = top_z - vert_bottom_z
            specs = [
                ('LEFT',  dict(rot=(0.0, math.radians(-90), 0.0),
                               mirror_y=True, mirror_z=True,
                               loc=(left_x, cavity_back_y, vert_bottom_z),
                               length=vert_height, width=cage_dim_y)),
                ('RIGHT', dict(rot=(0.0, math.radians(-90), 0.0),
                               mirror_y=True, mirror_z=False,
                               loc=(right_x, cavity_back_y, vert_bottom_z),
                               length=vert_height, width=cage_dim_y)),
                ('TOP',   dict(rot=(0.0, 0.0, 0.0),
                               mirror_y=True, mirror_z=True,
                               loc=(left_x + t, cavity_back_y, top_z),
                               length=max(cage_dim_x - 2 * t, 0.0),
                               width=cage_dim_y)),
                ('BACK',  dict(rot=(math.radians(90), math.radians(-90), 0.0),
                               mirror_y=True, mirror_z=False,
                               loc=(left_x, cavity_back_y, vert_bottom_z),
                               length=vert_height, width=cage_dim_x)),
            ]
            if not to_floor:
                specs.append(
                    ('BOTTOM', dict(rot=(0.0, 0.0, 0.0),
                                    mirror_y=True, mirror_z=False,
                                    loc=(left_x + t, cavity_back_y, bottom_z),
                                    length=max(cage_dim_x - 2 * t, 0.0),
                                    width=cage_dim_y)))
        return specs

    def _emit_bay_finish_panel(self, bay_index, opening_index, face, spec,
                               thickness, existing):
        """Create or reuse one (bay_index, opening_index, face) finish liner
        and write its transform + cutpart dims from `spec`. opening_index
        is -1 for a whole-bay liner. Reuse-by-key keeps object identity
        stable so downstream view instances don't break.
        """
        key = (bay_index, opening_index, face)
        strip = existing.get(key)
        if strip is None:
            if opening_index < 0:
                name = f'Bay Finish {bay_index + 1} {face.title()}'
            else:
                name = f'Opening Finish {bay_index + 1}.{opening_index} {face.title()}'
            part = CabinetPart()
            part.create(name)
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_BAY_FINISH
            part.obj['CABINET_PART'] = True
            part.obj[TAG_BAY_FINISH_BAY] = bay_index
            part.obj[TAG_BAY_FINISH_OPENING] = opening_index
            part.obj[TAG_BAY_FINISH_FACE] = face
            strip = part.obj
        else:
            part = GeoNodeCutpart(strip)
        rx, ry, rz = spec['rot']
        strip.rotation_euler = (rx, ry, rz)
        part.set_input('Mirror Y', spec['mirror_y'])
        part.set_input('Mirror Z', spec['mirror_z'])
        strip.location = spec['loc']
        part.set_input('Length',    spec['length'])
        part.set_input('Width',     spec['width'])
        part.set_input('Thickness', thickness)

    # =====================================================================
    # Applied textured panels (BEADBOARD / SHIPLAP, 1/4 flat parts)
    # =====================================================================
    def _reconcile_textured_panels(self, layout):
        """Spawn / resize / remove BEADBOARD or SHIPLAP applied panels.

        One reconciler covers all three sides. Geometry is a single
        1/4 flat part per side - same overall position as a PANELED
        applied panel (LEFT / RIGHT) or FINISHED back (BACK), without
        the face frame structure. Distinct roles per condition so a
        future material pass can shade beadboard and shiplap
        differently; a future modifier pass can carve bead profiles /
        plank reveals into the geometry.

        Resize-in-place when the role is unchanged. Condition flips
        between BEADBOARD <-> SHIPLAP rebuild the part since the role
        changes.
        """
        cab = self.obj.face_frame_cabinet
        side_specs = (
            ('LEFT',  cab.left_finished_end_condition),
            ('RIGHT', cab.right_finished_end_condition),
            ('BACK',  cab.back_finished_end_condition),
        )

        existing = {
            child.get(TAG_TEXTURED_PANEL_SIDE): child
            for child in self.obj.children
            if child.get(TAG_TEXTURED_PANEL_SIDE) in ('LEFT', 'RIGHT', 'BACK')
        }

        for side, condition in side_specs:
            desired_role = TEXTURED_PANEL_ROLES.get(condition)
            part_obj = existing.get(side)

            if desired_role is None:
                if part_obj is not None:
                    bpy.data.objects.remove(part_obj, do_unlink=True)
                continue

            # Role mismatch -> drop and recreate so material assignment
            # tracks the chosen condition cleanly.
            if (part_obj is not None
                    and part_obj.get('hb_part_role') != desired_role):
                bpy.data.objects.remove(part_obj, do_unlink=True)
                part_obj = None

            thickness = inch(0.25)

            if side == 'LEFT':
                bottom_z = solver.bay_bottom_z(layout, 0)
                location = (0.0, 0.0, bottom_z)
                length = solver.left_side_top_z(layout) - bottom_z
                width = layout.dim_y - layout.fft
                rot_x, rot_y = 0.0, math.radians(-90)
                mirror_y, mirror_z = True, True
            elif side == 'RIGHT':
                last = layout.bay_count - 1
                bottom_z = solver.bay_bottom_z(layout, last)
                location = (layout.dim_x, 0.0, bottom_z)
                length = solver.right_side_top_z(layout) - bottom_z
                width = layout.dim_y - layout.fft
                rot_x, rot_y = 0.0, math.radians(-90)
                mirror_y, mirror_z = True, False
            else:  # BACK
                # Origin sits at Y=+thickness so the part fills [0, thickness]
                # in cabinet Y - directly behind the carcass back, same as
                # FINISHED_BACK but 1/4 thick.
                location = (0.0, thickness, 0.0)
                length = layout.dim_z
                width = layout.dim_x
                rot_x, rot_y = math.radians(90), math.radians(-90)
                mirror_y, mirror_z = True, False  # no z-mirror needed

            # Finished-end overhang. BACK grows past the L/-X and R/+X
            # ends (Width spans +X from origin x=0, same as the finished
            # back). LEFT / RIGHT have their back edge at the origin with
            # Width extruding -Y, so a back overhang shifts origin +Y and
            # widens; the square front stays put.
            if side == 'BACK':
                el = cab.back_finished_extend_left
                er = cab.back_finished_extend_right
                location = (location[0] - el, location[1], location[2])
                width = width + el + er
            else:
                eb = (cab.left_side_finished_extend_back if side == 'LEFT'
                      else cab.right_side_finished_extend_back)
                location = (location[0], location[1] + eb, location[2])
                width = width + eb

            if part_obj is None:
                part = CabinetPart()
                label = 'Beadboard' if condition == 'BEADBOARD' else 'Shiplap'
                part.create(f'{label} {side[0]}')
                part.obj.parent = self.obj
                part.obj['hb_part_role'] = desired_role
                part.obj['CABINET_PART'] = True
                part.obj[TAG_TEXTURED_PANEL_SIDE] = side
                part.obj.rotation_euler.x = rot_x
                part.obj.rotation_euler.y = rot_y
                part.set_input('Mirror Y', mirror_y)
                part.set_input('Mirror Z', mirror_z)
                part_obj = part.obj
            else:
                part = GeoNodeCutpart(part_obj)

            part_obj.location = location
            part.set_input('Length',    length)
            part.set_input('Width',     width)
            part.set_input('Thickness', thickness)

    # =====================================================================
    # Helpers - rail reconciliation + bay cage update
    # =====================================================================
    def _reconcile_rails(self, role, segments):
        """Match existing rail children of the given role against the desired
        segment list. Delete rails whose start_bay isn't in the segment set;
        create rails for segments that don't have a matching object yet.

        Identity key is hb_segment_start_bay. After this call every segment
        has exactly one rail object with the matching key; the dispatch loop
        in recalculate() then writes geometry to each.
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        # Pass 1: delete obsolete rails
        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != role:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        # Pass 2: figure out which starts already exist
        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == role
        }

        # Pass 3: create rails for segments that don't have an object yet
        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_rail_part(role, seg['start_bay'])

    def _reconcile_front_drop_fillers(self, segments):
        """Match drop-filler children against solver.front_drop_filler_
        segments. Three-pass delete/match/create like _reconcile_rails,
        keyed by (hb_segment_start_bay, hb_drop_filler_side) since a bay
        can carry one filler per side.
        """
        wanted = {(seg['bay'], seg['side']) for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_FRONT_DROP_FILLER:
                continue
            key = (child.get('hb_segment_start_bay'),
                   child.get('hb_drop_filler_side'))
            if key not in wanted:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing = {
            (child.get('hb_segment_start_bay'),
             child.get('hb_drop_filler_side'))
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_FRONT_DROP_FILLER
        }

        for seg in segments:
            if (seg['bay'], seg['side']) in existing:
                continue
            self._create_front_drop_filler(seg['bay'], seg['side'])

    def _create_front_drop_filler(self, bay_index, side):
        """Create one drop-filler stile keyed to its bay + side. Oriented
        like an end stile (Length vertical); the LEFT filler mirrors the
        left stile's Mirror Y so width extends into the band, the RIGHT
        filler mirrors the right stile's."""
        side_label = 'Left' if side == 'LEFT' else 'Right'
        filler = CabinetPart()
        filler.create(f'{side_label} Drop Filler {bay_index + 1}')
        filler.obj.parent = self.obj
        filler.obj['hb_part_role'] = PART_ROLE_FRONT_DROP_FILLER
        filler.obj['CABINET_PART'] = True
        filler.obj['hb_segment_start_bay'] = bay_index
        filler.obj['hb_drop_filler_side'] = side
        filler.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        filler.obj.rotation_euler.y = math.radians(-90)
        filler.obj.rotation_euler.z = math.radians(90)
        filler.set_input('Mirror Y', side == 'LEFT')
        filler.set_input('Mirror Z', True)
        return filler

    def _reconcile_carcass_bottoms(self, segments):
        """Match Bottom carcass children against segments. Three-pass
        delete/match/create keyed by hb_segment_start_bay - same shape
        as _reconcile_rails. Also cleans up any legacy non-segment Bottom
        (its hb_segment_start_bay is None which is never in wanted_starts).
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_BOTTOM:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_BOTTOM
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_carcass_bottom_part(seg['start_bay'])

    def _create_carcass_bottom_part(self, start_bay_index):
        """Create one carcass bottom part (bay floor) keyed to its segment."""
        bottom = CabinetPart()
        bottom.create(f'Bottom {start_bay_index + 1}')
        bottom.obj.parent = self.obj
        bottom.obj['hb_part_role'] = PART_ROLE_BOTTOM
        bottom.obj['CABINET_PART'] = True
        bottom.obj['hb_segment_start_bay'] = start_bay_index
        bottom.set_input('Mirror Y', True)
        bottom.set_input('Mirror Z', False)
        return bottom

    def _reconcile_kick_subfronts(self, segments):
        """Match Toe Kick Subfront children against segments. Three-pass
        delete/match/create keyed by hb_segment_start_bay - same shape
        as _reconcile_carcass_bottoms. Also deletes any legacy single-
        piece kick subfront (no hb_segment_start_bay marker).
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_TOE_KICK_SUBFRONT:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_TOE_KICK_SUBFRONT
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_kick_subfront_part(seg['start_bay'])

    def _create_kick_subfront_part(self, start_bay_index):
        """Create one toe kick subfront part keyed to its segment.
        Same orientation as the bottom rail: rotation X=90 + Mirror Z
        so Length=X, Width=Z, Thickness extends +Y into the cabinet.
        """
        kick = CabinetPart()
        kick.create(f'Toe Kick Subfront {start_bay_index + 1}')
        kick.obj.parent = self.obj
        kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK_SUBFRONT
        kick.obj['CABINET_PART'] = True
        kick.obj['hb_segment_start_bay'] = start_bay_index
        kick.obj.rotation_euler.x = math.radians(90)
        kick.set_input('Mirror Z', True)
        return kick

    def _reconcile_finish_kicks(self, segments):
        """Match Finish Toe Kick children against segments. Three-pass
        delete/match/create keyed by hb_segment_start_bay - same shape
        as _reconcile_kick_subfronts.
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_FINISH_TOE_KICK:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_FINISH_TOE_KICK
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_finish_kick_part(seg['start_bay'])

    def _create_finish_kick_part(self, start_bay_index):
        """Create one finish toe kick part keyed to its segment. Same
        orientation as the kick subfront.
        """
        fk = CabinetPart()
        fk.create(f'Finish Toe Kick {start_bay_index + 1}')
        fk.obj.parent = self.obj
        fk.obj['hb_part_role'] = PART_ROLE_FINISH_TOE_KICK
        fk.obj['CABINET_PART'] = True
        fk.obj['hb_segment_start_bay'] = start_bay_index
        fk.obj.rotation_euler.x = math.radians(90)
        fk.set_input('Mirror Z', True)
        return fk

    def _ensure_corner_finish_kick(self, role, name):
        """Lazy-create a corner finish kick (left or right) if absent.
        Single piece per corner - filler that varies in Thickness to
        bridge the stile back to the main finish kick front when stile-
        to-floor is on. Same orientation as the main finish kick.
        """
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        fk = CabinetPart()
        fk.create(name)
        fk.obj.parent = self.obj
        fk.obj['hb_part_role'] = role
        fk.obj['CABINET_PART'] = True
        fk.obj.rotation_euler.x = math.radians(90)
        fk.set_input('Mirror Z', True)
        return fk.obj

    def _create_mid_finish_kick(self, gap_index, side):
        """Create one mid-stile finish toe kick filler, keyed by gap +
        side. Same orientation as the end-stile corner finish kick."""
        label = 'Left' if side == 'LEFT' else 'Right'
        fk = CabinetPart()
        fk.create(f'Finish Toe Kick {label} (Mid {gap_index + 1})')
        fk.obj.parent = self.obj
        fk.obj['hb_part_role'] = PART_ROLE_MID_FINISH_KICK
        fk.obj['CABINET_PART'] = True
        fk.obj['hb_mid_stile_index'] = gap_index
        fk.obj['hb_mid_kick_side'] = side
        fk.obj.rotation_euler.x = math.radians(90)
        fk.set_input('Mirror Z', True)
        return fk.obj

    def _reconcile_mid_finish_kicks(self, layout):
        """Match mid-stile finish toe kick fillers against to-floor gaps.

        Two per to-floor mid stile (LEFT + RIGHT of the dropped division),
        keyed by (hb_mid_stile_index, hb_mid_kick_side). Creates the
        missing ones and removes any whose gap is no longer to-floor (or
        out of range / finish kick disabled). Positioned + sized in the
        main part loop (PART_ROLE_MID_FINISH_KICK branch)."""
        n_gaps = max(0, layout.bay_count - 1)
        wanted = set()
        for gi in range(n_gaps):
            if solver.has_mid_finish_kick(layout, gi):
                wanted.add((gi, 'LEFT'))
                wanted.add((gi, 'RIGHT'))
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_MID_FINISH_KICK:
                continue
            key = (child.get('hb_mid_stile_index'),
                   child.get('hb_mid_kick_side'))
            if key not in wanted:
                bpy.data.objects.remove(child, do_unlink=True)
        existing = {(c.get('hb_mid_stile_index'), c.get('hb_mid_kick_side'))
                    for c in self.obj.children
                    if c.get('hb_part_role') == PART_ROLE_MID_FINISH_KICK}
        for gi, side in wanted:
            if (gi, side) not in existing:
                self._create_mid_finish_kick(gi, side)

    def _ensure_partition_skin_slot2(self, layout):
        """Lazy-create the slot-2 partition skin (floating-bay finish) per
        gap if absent. Slots 0/1 are created up front at gap creation; slot
        2 was added later, so this backfills existing cabinets. Sized + hidden
        by the PARTITION_SKIN part-loop branch from partition_skin_panels."""
        n_gaps = max(0, layout.bay_count - 1)
        existing = {
            (c.get('hb_mid_stile_index'), c.get('hb_partition_skin_slot'))
            for c in self.obj.children
            if c.get('hb_part_role') == PART_ROLE_PARTITION_SKIN
        }
        for gi in range(n_gaps):
            if (gi, 2) in existing:
                continue
            skin = CabinetPart()
            skin.create(f'Partition Skin {gi + 1}.2')
            skin.obj.parent = self.obj
            skin.obj['hb_part_role'] = PART_ROLE_PARTITION_SKIN
            skin.obj['CABINET_PART'] = True
            skin.obj['hb_mid_stile_index'] = gi
            skin.obj['hb_partition_skin_slot'] = 2
            skin.obj.rotation_euler.y = math.radians(-90)
            skin.set_input('Mirror Y', True)
            skin.set_input('Mirror Z', True)
            skin.obj.hide_viewport = True
            skin.obj.hide_render = True

    def _drive_partition_skin_floor_notch(self, skin_obj, layout, gap_index, skin):
        """Drive the slot-2 (floating-finish) partition skin's 'Notch Front
        Bottom' modifier so the floor-dropped skin clears the toe-kick recess
        at the cabinet front.

        Active for a NOTCH toe kick when the slot-2 skin is present, UNLESS the
        gap's mid stile is itself dropped to the floor (the stile-to-floor
        construction already finishes the front, so no notch). Added lazily so
        skins built before notch support upgrade in place. Flip X=False (bottom)
        / Flip Y=True (front) match the mid-division's bottom-front corner (the
        skin shares the mid-division orientation)."""
        mod = skin_obj.modifiers.get('Notch Front Bottom')
        if mod is None:
            cpm = GeoNodeCutpart(skin_obj).add_part_modifier(
                'CPM_CORNERNOTCH', 'Notch Front Bottom')
            cpm.set_input('Flip X', False)
            cpm.set_input('Flip Y', True)
            mod = cpm.mod
        if mod.node_group is None:
            return
        active = (skin is not None
                  and layout.has_toe_kick
                  and layout.toe_kick_type == 'NOTCH'
                  and gap_index < len(layout.mid_stiles)
                  and not bool(layout.mid_stiles[gap_index].get('to_floor')))
        if active:
            # The floating bay carries the lift in its kick_height, so read the
            # NON-floating neighbour's kick for the real toe-kick height.
            bay_a = layout.bays[gap_index]
            neighbor_idx = (gap_index + 1
                            if bool(bay_a.get('floating_bay')) else gap_index)
            kick = layout.bays[neighbor_idx]['kick_height']
            setback = self.obj.face_frame_cabinet.toe_kick_setback
            route = skin['thickness']
        else:
            kick = setback = route = 0.0
        ng = mod.node_group
        for input_name, value in (('X', kick), ('Y', setback),
                                  ('Route Depth', route)):
            node_input = ng.interface.items_tree.get(input_name)
            if node_input is not None:
                hb_utils.set_gn_input(mod, node_input.identifier, value)
        mod.show_viewport = active
        mod.show_render = active

    def _ensure_kick_return(self, role, name, mirror_z):
        """Lazy-create a left or right kick return - a vertical
        closeout panel at the inset X position running full carcass
        depth from cabinet back to main kick front. Rotation X=90 +
        Z=-90 so Length runs -Y; mirror_z flips Thickness direction
        (+X for left, -X for right).
        """
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        ret = CabinetPart()
        ret.create(name)
        ret.obj.parent = self.obj
        ret.obj['hb_part_role'] = role
        ret.obj['CABINET_PART'] = True
        ret.obj.rotation_euler.x = math.radians(90)
        ret.obj.rotation_euler.z = math.radians(-90)
        ret.set_input('Mirror Z', mirror_z)
        return ret.obj

    def _ensure_loose_kick_part(self, role, name, kind, mirror_z):
        """Lazy-create one board of the loose toe-kick ladder.

        kind 'RAIL' (front / rear): subfront orientation - rotation X=90
        + Mirror Z, so Length runs along X, Width up in Z, Thickness +Y.
        kind 'END' (left / right): kick-return orientation - rotation
        X=90 + Z=-90, so Length runs -Y front-to-back, Width up in Z,
        Thickness along X (mirror_z flips it +X / -X). Position + dims
        are written by the dispatch loop from the solver each recalc;
        the part is hidden when the cabinet isn't a LOOSE kick.
        """
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj.rotation_euler.x = math.radians(90)
        if kind == 'END':
            part.obj.rotation_euler.z = math.radians(-90)
        part.set_input('Mirror Z', mirror_z)
        return part.obj

    def _ensure_blind_panel(self, role, name, mirror_y):
        """Lazy-create a left or right blind panel - a 1/4" vertical
        partition that sits just behind the face frame, parallel to it,
        extending inboard from the cabinet end by blind_amount. Closes
        off the dead corner space when an adjacent perpendicular cabinet
        butts against this end. Same rotation convention as the end
        stiles (Y=-90 + Z=90); mirror_y flips Width direction so the
        panel grows inboard from each respective end (True for LEFT,
        False for RIGHT, matching left/right stile setup).
        """
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        panel = CabinetPart()
        panel.create(name)
        panel.obj.parent = self.obj
        panel.obj['hb_part_role'] = role
        panel.obj['CABINET_PART'] = True
        panel.obj.rotation_euler.y = math.radians(-90)
        panel.obj.rotation_euler.z = math.radians(90)
        panel.set_input('Mirror Y', mirror_y)
        panel.set_input('Mirror Z', False)
        return panel.obj

    def _blind_panel_z_range(self):
        """Return (z_origin, z_height) for blind panel placement.
        Sits above the toe kick recess (or directly on the floor for
        upper / panel cabinets) and runs to the top of the cabinet.
        Subclasses can override if a class needs a different baseline
        (e.g. lap drawer wanting to sit above the lap reveal).
        """
        cab_props = self.obj.face_frame_cabinet
        z_origin = cab_props.toe_kick_height if self._has_toe_kick() else 0.0
        z_height = max(cab_props.height - z_origin, 0.0)
        return (z_origin, z_height)

    def _reconcile_carcass_backs(self, segments):
        """Match Back carcass children against segments. Same three-pass
        delete/match/create as _reconcile_carcass_bottoms.
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_BACK:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_BACK
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_carcass_back_part(seg['start_bay'])

    def _create_carcass_back_part(self, start_bay_index):
        """Create one carcass back panel keyed to its segment."""
        back = CabinetPart()
        back.create(f'Back {start_bay_index + 1}')
        back.obj.parent = self.obj
        back.obj['hb_part_role'] = PART_ROLE_BACK
        back.obj['CABINET_PART'] = True
        back.obj['hb_segment_start_bay'] = start_bay_index
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.set_input('Mirror Y', True)
        return back


    def _cleanup_role(self, role):
        """Remove all children with the given hb_part_role.

        Used when the cabinet's top-construction style differs from what
        was previously built (e.g., a base cabinet that has leftover
        solid TOP parts from the old architecture, or a tall cabinet
        with stretcher leftovers from a type change).
        """
        to_delete = [
            child for child in list(self.obj.children)
            if child.get('hb_part_role') == role
        ]
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

    def _reconcile_carcass_tops(self, segments):
        """Match solid Top carcass children against segments. Same
        three-pass delete/match/create as _reconcile_carcass_bottoms /
        _backs. Used for Upper / Tall cabinets only.
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != PART_ROLE_TOP:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == PART_ROLE_TOP
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_carcass_top_part(seg['start_bay'])

    def _create_carcass_top_part(self, start_bay_index):
        """Create one solid carcass top part keyed to its segment.

        Mirror Y = True so the panel extends from y=-mt back into the
        cabinet by panel_dim_y. Mirror Z = True so it extends down by
        thickness from its z=bay_top_z origin.
        """
        top = CabinetPart()
        top.create(f'Top {start_bay_index + 1}')
        top.obj.parent = self.obj
        top.obj['hb_part_role'] = PART_ROLE_TOP
        top.obj['CABINET_PART'] = True
        top.obj['hb_segment_start_bay'] = start_bay_index
        top.set_input('Mirror Y', True)
        top.set_input('Mirror Z', True)
        return top

    def _reconcile_stretchers(self, role, segments):
        """Match stretcher children against segments. Generic over front
        vs rear: caller passes PART_ROLE_FRONT_STRETCHER or
        PART_ROLE_REAR_STRETCHER. Same three-pass delete/match/create
        shape as _reconcile_carcass_bottoms / _backs.
        """
        wanted_starts = {seg['start_bay'] for seg in segments}

        to_delete = []
        for child in list(self.obj.children):
            if child.get('hb_part_role') != role:
                continue
            if child.get('hb_segment_start_bay') not in wanted_starts:
                to_delete.append(child)
        for child in to_delete:
            bpy.data.objects.remove(child, do_unlink=True)

        existing_starts = {
            child.get('hb_segment_start_bay')
            for child in self.obj.children
            if child.get('hb_part_role') == role
        }

        for seg in segments:
            if seg['start_bay'] in existing_starts:
                continue
            self._create_stretcher_part(role, seg['start_bay'])

    def _create_stretcher_part(self, role, start_bay_index):
        """Create one stretcher part keyed to its segment.

        Front and rear differ only in name prefix and Mirror Y. Both
        sit at z = bay_top_z(start) and extend down (-Z) by thickness.
          - Front: Mirror Y = False (depth extends back into cabinet)
          - Rear:  Mirror Y = True  (depth extends forward into cabinet)
        """
        if role == PART_ROLE_FRONT_STRETCHER:
            name = f'Front Stretcher {start_bay_index + 1}'
            mirror_y = False
        else:
            name = f'Rear Stretcher {start_bay_index + 1}'
            mirror_y = True
        s = CabinetPart()
        s.create(name)
        s.obj.parent = self.obj
        s.obj['hb_part_role'] = role
        s.obj['CABINET_PART'] = True
        s.obj['hb_segment_start_bay'] = start_bay_index
        s.set_input('Mirror Y', mirror_y)
        s.set_input('Mirror Z', True)
        return s

    def _create_rail_part(self, role, start_bay_index):
        """Create a single rail part with the given role and start_bay key."""
        if role == PART_ROLE_TOP_RAIL:
            name = f'Top Rail {start_bay_index + 1}'
        else:
            name = f'Bottom Rail {start_bay_index + 1}'

        rail = CabinetPart()
        rail.create(name)
        rail.obj.parent = self.obj
        rail.obj['hb_part_role'] = role
        rail.obj['CABINET_PART'] = True
        rail.obj['hb_segment_start_bay'] = start_bay_index
        rail.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        rail.obj.rotation_euler.x = math.radians(90)
        if role == PART_ROLE_TOP_RAIL:
            rail.set_input('Mirror Y', True)
            rail.set_input('Mirror Z', True)
        else:
            rail.set_input('Mirror Z', True)
        return rail

    def _update_side_corner_notch(self, side_obj, layout, bay_index):
        """Drive the side's 'Notch Front Bottom' modifier from the
        cabinet's toe kick type. Active only for NOTCH and only when
        that side's stile is NOT extending to the floor - a stile-to-
        floor stile already encloses the kick corner from the front,
        so a notched side would leave an exposed gap behind it. FLUSH
        / FLOATING / uppers also leave the notch inactive. Adds the
        modifier lazily so cabinets built before NOTCH support are
        upgraded in place on the next recalc.
        """
        cab_props = self.obj.face_frame_cabinet
        mod = side_obj.modifiers.get('Notch Front Bottom')
        if mod is None:
            wrapper = GeoNodeCutpart(side_obj)
            cpm = wrapper.add_part_modifier(
                'CPM_CORNERNOTCH', 'Notch Front Bottom')
            cpm.set_input('Flip X', False)
            cpm.set_input('Flip Y', True)
            mod = cpm.mod
        if mod.node_group is None:
            return
        role = side_obj.get('hb_part_role')
        if role == PART_ROLE_LEFT_SIDE:
            stile_to_floor = solver.left_stile_to_floor(layout)
            has_inset = layout.kick_inset_left > 0
            side_thickness = solver.left_side_thickness(layout)
        else:
            stile_to_floor = solver.right_stile_to_floor(layout)
            has_inset = layout.kick_inset_right > 0
            side_thickness = solver.right_side_thickness(layout)
        # End bay flagged floating_bay forces the side to anchor at the
        # bay bottom (see solver.side_bottom_z), so the notch becomes
        # redundant just like the has_inset case.
        bay_floating = (
            0 <= bay_index < len(layout.bays)
            and bool(layout.bays[bay_index].get('floating_bay'))
        )
        # Side already floats by kick_height when there's an inset on
        # this side, so the notch (which only existed to clear the
        # recess in a floor-anchored side) becomes redundant.
        active = (layout.has_toe_kick
                  and layout.toe_kick_type == 'NOTCH'
                  and not stile_to_floor
                  and not has_inset
                  and not bay_floating
                  and 0 <= bay_index < len(layout.bays))
        if active:
            bay = layout.bays[bay_index]
            kick = bay['kick_height']
            setback = cab_props.toe_kick_setback
            # Route Depth must cut through the FULL side thickness, not
            # just the cabinet's material_thickness default. FINISHED
            # sides are 3/4" thick (vs 1/2" default), and a notch that
            # only cuts 1/2" would leave 1/4" of material in the kick
            # recess.
            thickness = side_thickness
        else:
            kick = setback = thickness = 0.0
        ng = mod.node_group
        for input_name, value in (
            ('X', kick),
            ('Y', setback),
            ('Route Depth', thickness),
        ):
            node_input = ng.interface.items_tree.get(input_name)
            if node_input is not None:
                hb_utils.set_gn_input(mod, node_input.identifier, value)
        mod.show_viewport = active
        mod.show_render = active

    def _update_mid_div_notches(self, mid_div_obj, panel):
        """Drive the two CPM_CORNERNOTCH modifiers on a slot-0 mid-div.

        The build path adds 'Notch Top Front' and 'Notch Top Back' with
        their Flip flags pre-set. Each recalc updates X / Y / Route Depth
        and toggles show_viewport / show_render based on the solver's
        notch flags. The two gate independently: a front-dropped (sink /
        cooktop) bay's front stretcher terminates at the division face
        instead of crossing, so only the rear notch is cut there. Slot-1
        mid-divs (diff-depth case) have no notch modifiers and silently
        no-op here.
        """
        back_active = panel.get('notch_active', False)
        front_active = panel.get('notch_front_active', back_active)
        size_x = panel.get('notch_x', 0.0)
        size_y = panel.get('notch_y', 0.0)
        route = panel.get('notch_route_depth', 0.0)
        for name, active in (('Notch Top Front', front_active),
                             ('Notch Top Back', back_active)):
            mod = mid_div_obj.modifiers.get(name)
            if mod is None:
                continue  # slot 1 lacks these modifiers
            ng = mod.node_group
            if ng is None:
                continue
            for input_name, value in (
                ('X', size_x),
                ('Y', size_y),
                ('Route Depth', route),
            ):
                node_input = ng.interface.items_tree.get(input_name)
                if node_input is not None:
                    hb_utils.set_gn_input(mod, node_input.identifier, value)
            mod.show_viewport = active
            mod.show_render = active

    def _bay_has_false_front(self, bay_obj):
        """True when any opening in the bay is a FALSE_FRONT -- the
        cleanest signal that the bay houses a sink basin (a working
        drawer can't sit in front of one)."""
        for child in bay_obj.children_recursive:
            if not child.get(TAG_OPENING_CAGE):
                continue
            if child.face_frame_opening.front_type == 'FALSE_FRONT':
                return True
        return False

    def _create_appliance_annotation(self, bay_obj, kind):
        """One GeoNodeRectangle (square outline + centered word) flat on
        top of the bay, parented to the bay cage so it rides the cabinet
        into every 2D view. Bay-local frame: origin front-left-bottom,
        +Y toward the back, top at Dim Z."""
        cage = GeoNodeCage(bay_obj)
        dim_x = cage.get_input('Dim X')
        dim_y = cage.get_input('Dim Y')
        dim_z = cage.get_input('Dim Z')
        margin = min(APPLIANCE_ANNO_SIDE_MARGIN, dim_x * 0.25)
        rect = GeoNodeRectangle()
        rect.create(f"{kind.title()} Annotation")
        rect.obj.parent = bay_obj
        rect.obj.location = (margin, dim_y / 4.0, dim_z + APPLIANCE_ANNO_Z_LIFT)
        rect.set_input('Dim X', dim_x - margin * 2.0)
        rect.set_input('Dim Y', dim_y / 2.0)
        rect.set_input('Line Thickness', APPLIANCE_ANNO_LINE_THICKNESS)
        rect.set_input('Text', kind)
        rect.set_input('Text Size', APPLIANCE_ANNO_TEXT_SIZE)
        rect.set_input('Text Y Offset', APPLIANCE_ANNO_TEXT_Y_OFFSET)
        rect.obj['hb_part_role'] = PART_ROLE_APPLIANCE_ANNOTATION
        rect.obj['IS_2D_ANNOTATION'] = True
        rect.obj['APPLIANCE_ANNOTATION'] = True
        rect.obj['IS_SINK_ANNOTATION' if kind == 'SINK'
                 else 'IS_COOKTOP_ANNOTATION'] = True
        return rect

    def _apply_appliance_annotations(self, layout):
        """Wipe-and-recreate the square + word annotation on every
        appliance bay (same lifecycle as accessory labels, so it tracks
        bay size/drop). Triggers: an APPLIANCE_BAY stamp on the bay cage
        (set by hb_face_frame.add_appliance_to_bay), or -- for the
        dedicated SinkFaceFrameCabinet -- the bay holding the false
        front (the basin bay), no stamp required."""
        for child in list(self.obj.children_recursive):
            if child.get('hb_part_role') == PART_ROLE_APPLIANCE_ANNOTATION:
                bpy.data.objects.remove(child, do_unlink=True)

        is_sink_cabinet = self.obj.get('CLASS_NAME') == 'SinkFaceFrameCabinet'
        for bay_obj in [c for c in self.obj.children if c.get(TAG_BAY_CAGE)]:
            if bay_obj.hide_viewport:
                continue
            kind = bay_obj.get('APPLIANCE_BAY')
            if not kind and is_sink_cabinet and self._bay_has_false_front(bay_obj):
                kind = 'SINK'
            if kind not in ('SINK', 'COOKTOP'):
                continue
            self._create_appliance_annotation(bay_obj, kind)

    def _update_bay_cage(self, bay_obj, layout, bay_index):
        """Position and size a single bay cage from the solver. Cascades
        to the bay's opening cage children so they stay in sync with the
        bay's face frame opening dimensions.
        """
        if bay_index >= layout.bay_count:
            bay_obj.hide_viewport = True
            for child in bay_obj.children:
                if child.get(TAG_OPENING_CAGE):
                    child.hide_viewport = True
            return
        bay_obj.hide_viewport = False
        bay = FaceFrameBay(bay_obj)
        pos = solver.bay_cage_position(layout, bay_index)
        dim_x, dim_y, dim_z = solver.bay_cage_dims(layout, bay_index)
        bay_obj.location = pos
        # Rotate the bay around Z so its local +X aligns with the FF
        # direction; opening cages, front pivots, fronts, and any
        # interior items inherit the angle automatically through the
        # parent transform. Zero in square cabinets.
        bay_obj.rotation_euler.z = solver.face_frame_angle(layout)
        bay.set_input('Dim X', dim_x)
        bay.set_input('Dim Y', dim_y)
        bay.set_input('Dim Z', dim_z)
        bay.set_input('Mirror Y', False)
        self._update_openings_in_bay(bay_obj, layout, bay_index)

    def _update_openings_in_bay(self, bay_obj, layout, bay_index):
        """Reconcile a bay's tree against the solver's parts list.

        bay_openings() returns three lists:
          - leaves: each maps to an opening cage object (matched by name)
          - splitters: each maps to a bay mid rail or mid stile part
          - backings: each maps to a bay division or shelf part

        Opening cages are matched in place (by obj.name) so their props
        survive across recalcs. Splitters and backings are deleted and
        recreated each pass since they hold no user state - all of
        their parameters are derived from the split node's props.

        Split-node empties are forced to local origin so opening cage
        bay-local coords stay accurate at any tree depth.
        """
        parts = solver.bay_openings(layout, bay_index)
        leaves_by_name = {r['obj_name']: r for r in parts['leaves']}
        cage_dim_y = solver.bay_cage_dims(layout, bay_index)[1]

        # Snapshot descendants by tag UP FRONT. The opening loop below
        # calls _update_fronts_in_opening, which removes pivot and
        # front-part children of each cage; if we walked
        # children_recursive directly, those removed refs would still
        # be in our iteration and the next .get() would raise
        # "StructRNA of type Object has been removed". Filtering down
        # to cages and split nodes (neither of which is touched by the
        # inner deletions) keeps every ref live across the loop.
        all_descendants = list(bay_obj.children_recursive)
        split_nodes = [d for d in all_descendants
                       if d.get(TAG_SPLIT_NODE)]
        opening_cages = [d for d in all_descendants
                         if d.get(TAG_OPENING_CAGE)]

        # Pass 1a: pin split-node empties to local origin
        for sn in split_nodes:
            sn.location = (0.0, 0.0, 0.0)

        # Pass 1b: opening cages - in-place match by obj.name
        for cage in opening_cages:
            rect = leaves_by_name.get(cage.name)
            if rect is None:
                cage.hide_viewport = True
                continue
            cage.hide_viewport = False
            op = FaceFrameOpening(cage)
            cage.location = (rect['cage_x'], 0.0, rect['cage_z'])
            op.set_input('Dim X', rect['cage_dim_x'])
            op.set_input('Dim Y', cage_dim_y)
            op.set_input('Dim Z', rect['cage_dim_z'])
            op.set_input('Mirror Y', False)
            self._update_fronts_in_opening(cage, layout, rect)
            self._update_interior_items_in_opening(cage, layout, rect)

        # Pass 2: splitters (mid rails / mid stiles) - delete & recreate
        self._reconcile_bay_splitters(bay_obj, parts['splitters'])
        # Pass 3: backings (divisions / shelves) - delete & recreate.
        # Backings are carcass-deep partitions; for face-frame only
        # roots (panels) we still call the reconcile with an empty
        # rect list so its internal wipe cleans up any stale backings
        # (e.g. on a panel that had splits before this gate landed).
        # remove_carcass on this bay also drops backings - same wipe
        # path so existing ones are cleaned up when the flag is set.
        bay_drops_carcass = bay_obj.face_frame_bay.remove_carcass
        if not self._has_carcass() or bay_drops_carcass:
            backing_rects = []
        else:
            backing_rects = parts['backings']
        self._reconcile_bay_backings(bay_obj, backing_rects)

    def _reconcile_bay_splitters(self, bay_obj, splitter_rects):
        """Delete every existing bay splitter (mid rail / mid stile)
        anywhere under the bay, then rebuild from `splitter_rects`.

        Each rect carries the parent split-node name; the new part is
        parented to that split node so cleanup cascades when the split
        is removed. Coords from the rect are bay-local; with the split
        node defensively pinned at (0,0,0), bay-local equals
        split-node-local for these parts.
        """
        for descendant in list(bay_obj.children_recursive):
            # BAY_SPLITTER_ROLES catches mid rails / mid stiles. The
            # IS_BAY_SPLITTER_RAIL marker also catches a bay splitter that
            # was retagged BOTTOM_RAIL (remove_bottom open-bottom bays) so
            # the rebuild stays idempotent -- real cabinet bottom rails are
            # parented to the cabinet, never under the bay, so they are out
            # of this sweep's reach.
            if (descendant.get('hb_part_role') in BAY_SPLITTER_ROLES
                    or descendant.get('IS_BAY_SPLITTER_RAIL')):
                bpy.data.objects.remove(descendant, do_unlink=True)

        for rect in splitter_rects:
            split_obj = bpy.data.objects.get(rect['split_node_name'])
            if split_obj is None:
                continue
            if rect['role'] == 'BAY_MID_RAIL':
                self._create_bay_mid_rail(split_obj, rect)
            else:
                self._create_bay_mid_stile(split_obj, rect)

    def _reconcile_bay_backings(self, bay_obj, backing_rects):
        """Delete every existing bay backing part anywhere under the
        bay, then rebuild from `backing_rects`. Same pattern as
        _reconcile_bay_splitters; backings are parented to their split
        node so cleanup cascades naturally."""
        for descendant in list(bay_obj.children_recursive):
            if descendant.get('hb_part_role') in BAY_BACKING_ROLES:
                bpy.data.objects.remove(descendant, do_unlink=True)

        for rect in backing_rects:
            split_obj = bpy.data.objects.get(rect['split_node_name'])
            if split_obj is None:
                continue
            self._create_bay_backing(split_obj, rect)

    def _create_bay_mid_rail(self, split_obj, rect):
        """Mid rail orientation matches the bay's bottom rail (rotation
        X=90, Mirror Z=True): Length goes +X, Width goes +Z, Thickness
        goes +Y from the part origin. Origin sits at the rail's
        bottom-front-left corner in bay-local coords."""
        rail = CabinetPart()
        idx = rect['splitter_index'] + 1
        # A remove_bottom bay's lowest framed splitter is the section's
        # bottom rail, not a mid rail (e.g. refrigerator cabinet). Tag it
        # BOTTOM_RAIL so pricing / manufacturing / the toe-kick detail
        # reader classify it correctly; IS_BAY_SPLITTER_RAIL keeps the
        # reconcile sweep able to clean it on rebuild.
        as_bottom = bool(rect.get('as_bottom_rail'))
        rail.create(f'Bottom Rail {idx}' if as_bottom
                    else f'Bay Mid Rail {idx}')
        rail.obj.parent = split_obj
        rail.obj['hb_part_role'] = (PART_ROLE_BOTTOM_RAIL if as_bottom
                                    else PART_ROLE_BAY_MID_RAIL)
        rail.obj['IS_BAY_SPLITTER_RAIL'] = True
        rail.obj['CABINET_PART'] = True
        rail.obj['hb_split_node_name'] = rect['split_node_name']
        rail.obj['hb_splitter_index'] = rect['splitter_index']
        rail.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        rail.obj.rotation_euler.x = math.radians(90)
        rail.set_input('Mirror Z', True)
        rail.obj.location = (rect['x'], rect['y'], rect['z'])
        rail.set_input('Length', rect['length'])
        rail.set_input('Width', rect['splitter_width'])
        rail.set_input('Thickness', rect['thickness'])
        return rail

    def _create_bay_mid_stile(self, split_obj, rect):
        """Mid stile orientation matches the cabinet-level left end
        stile (rotation y=-90, z=90, Mirror Y=True, Mirror Z=True):
        Length goes +Z, Width goes +X, Thickness goes +Y. Origin at
        the stile's bottom-front-left corner in bay-local coords."""
        stile = CabinetPart()
        idx = rect['splitter_index'] + 1
        stile.create(f'Bay Mid Stile {idx}')
        stile.obj.parent = split_obj
        stile.obj['hb_part_role'] = PART_ROLE_BAY_MID_STILE
        stile.obj['CABINET_PART'] = True
        stile.obj['hb_split_node_name'] = rect['split_node_name']
        stile.obj['hb_splitter_index'] = rect['splitter_index']
        stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        stile.obj.rotation_euler.y = math.radians(-90)
        stile.obj.rotation_euler.z = math.radians(90)
        stile.set_input('Mirror Y', True)
        stile.set_input('Mirror Z', True)
        stile.obj.location = (rect['x'], rect['y'], rect['z'])
        stile.set_input('Length', rect['length'])
        stile.set_input('Width', rect['splitter_width'])
        stile.set_input('Thickness', rect['thickness'])
        return stile

    def _create_bay_backing(self, split_obj, rect):
        """Backing (division / shelf) - carcass-deep panel behind a
        splitter. For H-splits (rect['axis'] == 'H') the backing is a
        horizontal panel: no rotation, Length+X, Width+Y, Thickness+Z.
        For V-splits the backing is a vertical panel: rotation y=-90
        with Mirror Y=True and Mirror Z=True (matches cabinet-level
        mid division), Length+Z, Width+Y, Thickness+X.
        """
        part = CabinetPart()
        kind_label = 'Division' if rect['role'] == 'BAY_DIVISION' else 'Shelf'
        idx = rect['splitter_index'] + 1
        part.create(f'Bay {kind_label} {idx}')
        part.obj.parent = split_obj
        role = (PART_ROLE_BAY_DIVISION if rect['role'] == 'BAY_DIVISION'
                else PART_ROLE_BAY_SHELF)
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj['hb_split_node_name'] = rect['split_node_name']
        part.obj['hb_splitter_index'] = rect['splitter_index']
        if rect['axis'] == 'H':
            # Horizontal panel - no rotation, default mirror flags
            part.obj.location = (rect['x'], rect['y'], rect['z'])
            part.set_input('Length', rect['length'])
            part.set_input('Width', rect['width'])
            part.set_input('Thickness', rect['thickness'])
        else:
            # Vertical division panel: rotation Y=-90 with Mirror Z=True
            # gives Length+Z, Width+Y, Thickness+X. Mirror Y is left
            # off so Width extends +Y from the origin (back of face
            # frame in bay-local toward the back panel) - the cabinet-
            # level mid division uses Mirror Y=True, but in a bay-
            # internal context that flips depth backward and lands the
            # division outside the carcass.
            part.obj.rotation_euler.y = math.radians(-90)
            part.set_input('Mirror Y', False)
            part.set_input('Mirror Z', True)
            part.obj.location = (rect['x'], rect['y'], rect['z'])
            part.set_input('Length', rect['length'])
            part.set_input('Width', rect['width'])
            part.set_input('Thickness', rect['thickness'])
        return part

    def _update_fronts_in_opening(self, opening_obj, layout, rect):
        """Reconcile front parts under an opening cage.

        Structure: opening cage -> front pivot empty -> front part.
        The pivot holds the swing rotation (DOOR / PULLOUT-as-door) or
        slide translation (DRAWER_FRONT / PULLOUT slide) so the front
        part itself sits at a fixed local transform inside the pivot.
        Pulling the visual open state out of the part keeps the part's
        geometry math independent of swing_percent.

        `rect` is the opening's solver rect (from bay_openings) - it
        provides cage size and reveals so the solver can size the
        front without re-walking the bay tree.

        v1 strategy: delete-and-recreate the pivot + part on every
        recalc. Front parts hold no user state, so identity loss is
        cheap. Once front parts grow editable per-part props (style,
        material override) this can switch to in-place reconciliation.
        Also handles legacy doors that were direct children of the
        opening (pre-pivot) by deleting them.
        """
        # Manual fronts: the user applied + hand-edited the front(s) under
        # this opening via hb_face_frame.make_part_editable. The flag lives on
        # the OPENING cage (not the front) because front objects are torn down
        # and rebuilt here on every recalc - the opening survives. Skip the
        # wipe + rebuild so the applied front persists; Revert clears the flag
        # to resume normal rebuilding.
        if opening_obj.get('IS_MANUAL_FRONT'):
            return
        op_props = opening_obj.face_frame_opening
        front_type = op_props.front_type
        cab_props = self.obj.face_frame_cabinet

        # Wipe existing pivots, parts, and any legacy direct-child fronts.
        # Use children_recursive so pull instances parented under the door
        # part (grandchildren of the pivot) also get cleaned.
        for child in list(opening_obj.children):
            role = child.get('hb_part_role')
            if role == PART_ROLE_FRONT_PIVOT:
                # Reverse so deeper descendants unparent before ancestors.
                for sub in reversed(list(child.children_recursive)):
                    if sub.name in bpy.data.objects:
                        bpy.data.objects.remove(sub, do_unlink=True)
                bpy.data.objects.remove(child, do_unlink=True)
            elif role in FRONT_PART_ROLES:
                bpy.data.objects.remove(child, do_unlink=True)

        if front_type == 'NONE':
            return

        for leaf in solver.front_leaves(
            layout, rect, cab_props, op_props
        ):
            pivot = self._create_front_pivot(opening_obj)
            pivot.location = leaf['pivot_position']
            pivot.rotation_euler = leaf['pivot_rotation']

            front = self._create_front_part(
                pivot, leaf['role'], leaf['name']
            )
            front.obj.location = leaf['part_position']
            length, width, thickness = leaf['part_dims']
            front.set_input('Length', length)
            front.set_input('Width', width)
            front.set_input('Thickness', thickness)

            # Per-leaf frame-width override (tri-view mirror doors zero the
            # interior stiles where mirrors meet). Stamped onto the door
            # object so assign_style_to_front sets these per-side widths
            # instead of the uniform door-style stile/rail width. Cleared
            # when the leaf carries no override so a normal door reverts.
            _ovr = leaf.get('frame_override')
            _OVR_KEYS = {
                'left_stile':  'HB_FRAME_OVR_LEFT_STILE',
                'right_stile': 'HB_FRAME_OVR_RIGHT_STILE',
                'top_rail':    'HB_FRAME_OVR_TOP_RAIL',
                'bottom_rail': 'HB_FRAME_OVR_BOTTOM_RAIL',
            }
            for _k, _prop in _OVR_KEYS.items():
                if _ovr is not None and _k in _ovr:
                    front.obj[_prop] = _ovr[_k]
                elif _prop in front.obj:
                    del front.obj[_prop]

            # Drawer-look doors swap the single door pull for one pull
            # per applied drawer front; the panels are added below and
            # inherit the leaf swing. v1: single-leaf LEFT / RIGHT only.
            drawer_look = (
                leaf['role'] == PART_ROLE_DOOR
                and getattr(op_props, 'drawer_look_divisions', 'NONE') != 'NONE'
                and op_props.hinge_side in ('LEFT', 'RIGHT')
            )
            # Tri-view mirror doors carry no pulls (touch-open per the
            # production spec) -- both the three-bay build and legacy
            # single-opening builds.
            no_pulls = (self.obj.get('HB_NO_DOOR_PULLS')
                        or self.obj.get('HB_TRIVIEW_DOORS'))
            if not drawer_look and not no_pulls:
                self._create_pull_for_front(front, leaf['role'], leaf)
            self._create_drawer_box_for_front(pivot, leaf, rect)
            if drawer_look:
                self._build_drawer_look_fronts(front, leaf, op_props)

        # Sink apron: a fixed face-frame-depth panel across the top of a
        # DOOR opening (apron / farmhouse sink). The door(s) stay full
        # height; the apron sits behind them in the face-frame band
        # (y from the FF front face back by fft). Built directly here -
        # not via the leaf/pivot path - so it carries no door style or
        # pull; PART_ROLE_APRON is in FRONT_PART_ROLES so it's wiped on
        # the next rebuild. Same orientation as a front part (Length ->
        # vertical, Width -> horizontal, Thickness -> depth).
        if op_props.add_apron and front_type == 'DOOR':
            # Full interior width (the whole opening cage, x from 0), and
            # set BEHIND the face frame: the FF back plane is bay-local
            # y = 0, and a front part's Thickness extends -Y from its
            # origin, so an origin at y = +fft puts the apron body in
            # y[0, fft] - just behind the frame, in the interior.
            full_w = rect['cage_dim_x']
            top_z = rect['cage_dim_z'] - rect['reveal_top']
            apron_h = min(op_props.apron_height,
                          top_z - rect['reveal_bottom'])
            if full_w > 0.0 and apron_h > 0.0:
                fft = cab_props.face_frame_thickness
                apron = CabinetPart()
                apron.create('Apron')
                apron.obj.parent = opening_obj
                apron.obj['hb_part_role'] = PART_ROLE_APRON
                apron.obj['CABINET_PART'] = True
                # Interior part: shows up in 'Interiors' selection mode and is
                # routed into the Dashed freestyle collection on 2D layout
                # views (both keyed off this tag in hb_layouts).
                apron.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
                apron.obj.rotation_euler.y = math.radians(-90)
                apron.obj.rotation_euler.z = math.radians(90)
                apron.set_input('Mirror Y', True)
                apron.obj.location = (0.0, fft, top_z - apron_h)
                apron.set_input('Length', apron_h)
                apron.set_input('Width', full_w)
                apron.set_input('Thickness', fft)

        # APPLIANCE openings: filler stiles at the left/right inboard edges so
        # the clear opening matches the appliance width. Built directly here
        # (no front pivot); PART_ROLE_APPLIANCE_FILLER is in FRONT_PART_ROLES so
        # they wipe + rebuild on every recalc. Oriented like a stile (Length ->
        # vertical, Width -> horizontal, Thickness -> face-frame depth) and
        # parented to the opening cage so they ride the angled-FF rotation the
        # same way the apron does.
        if front_type == 'APPLIANCE':
            left_w, right_w = solver.appliance_filler_widths(rect, op_props)
            clear_h = (rect['cage_dim_z'] - rect['reveal_top']
                       - rect['reveal_bottom'])
            fft = cab_props.face_frame_thickness
            z0 = rect['reveal_bottom']
            filler_specs = []
            if left_w > 0.0:
                filler_specs.append(
                    ('Left Appliance Filler', rect['reveal_left'], left_w))
            if right_w > 0.0:
                x_right = rect['cage_dim_x'] - rect['reveal_right'] - right_w
                filler_specs.append(
                    ('Right Appliance Filler', x_right, right_w))
            for fname, x0, fw in filler_specs:
                if clear_h <= 0.0 or fw <= 0.0:
                    continue
                filler = CabinetPart()
                filler.create(fname)
                filler.obj.parent = opening_obj
                filler.obj['hb_part_role'] = PART_ROLE_APPLIANCE_FILLER
                filler.obj['CABINET_PART'] = True
                filler.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
                filler.obj.rotation_euler.y = math.radians(-90)
                filler.obj.rotation_euler.z = math.radians(90)
                filler.set_input('Mirror Y', True)
                # Mirror Z False so the filler's thickness sits in the
                # face-frame plane (proud), not behind it.
                filler.set_input('Mirror Z', False)
                filler.obj.location = (x0, 0.0, z0)
                filler.set_input('Length', clear_h)
                filler.set_input('Width', fw)
                filler.set_input('Thickness', fft)

    def _build_drawer_look_fronts(self, front, leaf, op_props):
        """Lay N applied drawer fronts on a DOOR leaf so it reads exactly
        like a real N-drawer stack but opens as one door.

        Heights, reveals and the drawer-front style mirror a real stack:
        a short top front (the scene Top Drawer Opening Height) with the
        rest equal, reveals = the cabinet mid-rail width less the two
        overlapping overlays, and the panels picked up by
        _apply_door_styles_to_fronts as DRAWER_LOOK_FRONT (drawer-front
        style). The carrier leaf is rendered as a flat slab (skipped by
        that styling pass) and recessed one front thickness along its
        outward normal, so the proud fronts sit at the normal front plane
        and the slab shows through the reveals as the faux mid rails. Each
        front gets its own drawer pull. The panels live under the front
        pivot, so the per-recalc pivot wipe clears them.

        v1 scope: single-leaf LEFT / RIGHT swing doors.
        """
        divisions = getattr(op_props, 'drawer_look_divisions', 'NONE')
        if leaf['role'] != PART_ROLE_DOOR or divisions == 'NONE':
            return
        if op_props.hinge_side not in ('LEFT', 'RIGHT'):
            return
        n = int(divisions)
        length, width, thickness = leaf['part_dims']
        cab_props = self.obj.face_frame_cabinet
        overlays = (solver.resolved_overlay(cab_props, op_props, 'top')
                    + solver.resolved_overlay(cab_props, op_props, 'bottom'))
        # Reveal between fronts = mid-rail width less the two overlapping
        # front overlays, matching a real drawer stack.
        reveal = max(0.0, cab_props.bay_mid_rail_width - overlays)
        # FULL INSET (negative overlay): the fronts sit flush in the
        # frame, so the reveals can't read as rails - add real proud
        # mid-rail strips between the fronts instead.
        inset = overlays < 0.0
        # Front heights come from per-drawer OPENING heights, exactly like a
        # standard drawer stack: the available run (leaf less the two outer
        # overlays and the n-1 mid rails) is shared among the openings -
        # user-held (unlock_size) heights kept, the rest splitting the
        # remainder equally - then front height = opening height + overlays.
        # spec is bottom -> top; the top opening defaults to the scene Top
        # Drawer Opening Height (seeded by _update_drawer_look_divisions).
        rail_w = cab_props.bay_mid_rail_width
        available = length - overlays - (n - 1) * rail_w
        openings = getattr(op_props, 'drawer_look_openings', None)
        if openings is not None and len(openings) == n:
            spec = [(o.size, bool(o.unlock_size)) for o in openings]
        else:
            top_oh = bpy.context.scene.hb_face_frame.top_drawer_opening_height
            spec = [(0.0, False)] * (n - 1) + [(top_oh, True)]
        held_total = sum(s for s, held in spec if held)
        auto = [k for k, (s, held) in enumerate(spec) if not held]
        share = (available - held_total) / len(auto) if auto else 0.0
        # Write the auto-computed opening height back into the locked
        # (not unlock_size) rows so their disabled UI field shows the
        # real height. Safe mid-recalc: the size update callback bails
        # on the _RECALCULATING guard, so this can't loop.
        if openings is not None and len(openings) == n:
            for k, (s, held) in enumerate(spec):
                if not held and abs(openings[k].size - share) > 1e-6:
                    openings[k].size = share
        heights = [(s if held else share) + overlays for (s, held) in spec]
        if any(h <= 0.0 for h in heights):
            return

        # The carrier leaf is the swinging "door": flat slab, recessed by
        # one front thickness along its outward normal so the proud fronts
        # land at the normal front plane.
        carrier = front.obj
        carrier['HB_DRAWER_LOOK_CARRIER'] = True
        outward = carrier.rotation_euler.to_matrix() @ Vector((0.0, 0.0, 1.0))
        carrier.location = carrier.location - outward * thickness

        scene_props = bpy.context.scene.hb_face_frame
        z = 0.0
        for i, h in enumerate(heights):
            panel = CabinetPart()
            panel.create("Drawer-Look Front " + str(i + 1))
            panel.obj.parent = carrier
            panel.obj['hb_part_role'] = PART_ROLE_DRAWER_LOOK_FRONT
            panel.obj['CABINET_PART'] = True
            # Identity local rotation: the panel shares the carrier's local
            # frame (X = vertical, -Y = horizontal, +Z = outward). Full
            # width + tiled height cover the slab except the reveals; z =
            # thickness mounts the panel proud of the recessed slab.
            panel.obj.rotation_euler = (0.0, 0.0, 0.0)
            panel.set_input('Mirror Y', True)
            panel.obj.location = (z, 0.0, thickness)
            panel.set_input('Length', h)
            panel.set_input('Width', width)
            panel.set_input('Thickness', thickness)
            self._add_drawer_look_pull(panel.obj, h, width, thickness,
                                       scene_props)
            if inset and i < n - 1:
                rail_h = cab_props.bay_mid_rail_width
                rail = CabinetPart()
                rail.create("Drawer-Look Rail " + str(i + 1))
                rail.obj.parent = carrier
                rail.obj['hb_part_role'] = PART_ROLE_DRAWER_LOOK_RAIL
                rail.obj['CABINET_PART'] = True
                rail.obj.rotation_euler = (0.0, 0.0, 0.0)
                rail.set_input('Mirror Y', True)
                # Mirror Z flips the cutpart's thickness axis so the rail
                # builds back into the frame rather than proud-outward.
                rail.set_input('Mirror Z', True)
                # Centered in the gap, full width, proud of the fronts by
                # one thickness (matches a real inset stack's mid rail).
                rail.obj.location = (z + h + (reveal - rail_h) / 2.0,
                                     0.0, thickness * 2.0)
                rail.set_input('Length', rail_h)
                rail.set_input('Width', width)
                rail.set_input('Thickness', thickness)
            z += h + reveal

    def _add_drawer_look_pull(self, panel_obj, length, width, thickness,
                              scene_props):
        """A centered horizontal drawer pull on one drawer-look panel,
        mounted on its proud front face (same orientation the drawer-pull
        branch of _create_pull_for_front uses)."""
        pull_obj = pulls.resolve_pull_object(scene_props, 'drawer')
        if pull_obj is None:
            return
        instance = bpy.data.objects.new("Pull - " + panel_obj.name,
                                        pull_obj.data)
        bpy.context.scene.collection.objects.link(instance)
        instance.parent = panel_obj
        instance.location = (length / 2.0, -width / 2.0, thickness)
        instance.rotation_euler = (math.radians(-90.0), 0.0,
                                   math.radians(90.0))
        instance['hb_part_role'] = 'PULL'
        instance['IS_CABINET_PULL'] = True

    def _create_front_pivot(self, opening_obj):
        """Create an Empty parented to the opening cage, used as the
        rotation/translation pivot for one front leaf. The empty is
        kept very small in the viewport - the user drives the swing
        through the opening's swing_percent slider, not by grabbing the
        empty directly, so the gizmo doesn't need to be prominent.
        """
        pivot = bpy.data.objects.new('Front Pivot', None)
        bpy.context.scene.collection.objects.link(pivot)
        pivot.empty_display_type = 'PLAIN_AXES'
        pivot.empty_display_size = 0.001
        pivot.parent = opening_obj
        pivot['hb_part_role'] = PART_ROLE_FRONT_PIVOT
        return pivot

    def _create_front_part(self, pivot_obj, role, name):
        """Create a front CabinetPart parented to the given pivot empty.

        Orientation: rotation y=-90, z=90 with Mirror Y=True. Mirror Z
        is intentionally NOT set so the CPM_5PIECEDOOR modifier renders
        its panel / rails on the correct face - Mirror Z flips the
        thickness axis inside the cutpart, which inverts the asymmetric
        5-piece geometry. The leaf's part_position picks the X / Z
        offsets so the panel anchors against the pivot's hinge corner;
        compensation for the dropped Mirror Z (if any visible shift on
        slab fronts) lives in solver.front_leaves.
        """
        part = CabinetPart()
        part.create(name)
        part.obj.parent = pivot_obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj.rotation_euler.y = math.radians(-90)
        part.obj.rotation_euler.z = math.radians(90)
        part.set_input('Mirror Y', True)
        return part

    def _z_in_cabinet(self, obj):
        """Walk obj's parent chain up to (but not including) the cabinet
        root, summing each parent's local Z. Returns the Z position of
        obj's local origin in cabinet-local space.

        Reads obj.location directly rather than matrix_world so the
        result is correct mid-recalc, before the depsgraph evaluates
        any newly-set transforms. Valid because none of the ancestors
        on this chain (pivot, opening, split, bay) carry rotations
        that translate Z at recalc-time (pivots are at swing 0).
        """
        z = 0.0
        cur = obj
        while cur is not None and cur is not self.obj:
            z += cur.location.z
            cur = cur.parent
        return z

    def _create_pull_for_front(self, front_part, role, leaf):
        """Attach a pull instance to `front_part` based on the cabinet's
        type and the front's role (DOOR / DRAWER_FRONT / PULLOUT_FRONT).
        FALSE_FRONT and INSET_PANEL skip - both are decorative
        and don't carry a pull. Returns the pull Object (or None if no
        pull is selected or the asset can't be loaded).

        The pull is parented to `front_part` so it inherits the swing /
        slide animation. Position is computed in front-part local space
        (X = Length axis, -Y = Width axis, -Z = out of cabinet). Pull
        rotation_euler.x = +90 deg maps the asset's bar axis along
        the door's vertical and orients its body in -Z (outward).
        """
        if role in (PART_ROLE_FALSE_FRONT, PART_ROLE_INSET_PANEL):
            return None
        scene_props = bpy.context.scene.hb_face_frame
        kind = 'drawer' if role in (PART_ROLE_DRAWER_FRONT, PART_ROLE_PULLOUT_FRONT, PART_ROLE_TILT_OUT) else 'door'
        # A pullout front carries a drawer-style pull - drawer pull
        # asset, horizontal bar - but it's a full door-height front, so
        # its vertical placement follows the door / cabinet-type formula
        # (top-of-door on a base cabinet), not the drawer formula.
        is_pullout = role == PART_ROLE_PULLOUT_FRONT
        # A flip door (TOP / BOTTOM hinge) has its hinge along a horizontal
        # edge, so the pull sits centered on the OPPOSITE edge with a
        # horizontal bar (like a drawer pull), not on the left/right edge
        # like a swing door. hinge is threaded in via the leaf descriptor.
        hinge = leaf.get('hinge')
        is_flip = (kind == 'door' and hinge in ('TOP', 'BOTTOM'))
        pull_obj = pulls.resolve_pull_object(scene_props, kind)
        if pull_obj is None:
            return None

        cabinet_type = self.obj.face_frame_cabinet.cabinet_type
        length, width, thickness = leaf['part_dims']
        h_offset = scene_props.pull_horizontal_offset

        # The pull asset's origin sits at the bar's center, so naive
        # placement at "X from edge" puts the pull's CENTER at that
        # distance and the pull spills half-its-length past the edge.
        # User-facing offsets are edge-to-nearest-pull-edge, so subtract
        # half the bar length on edge-anchored vertical formulas.
        # Centered placements (length/2 etc) keep their middle anchor
        # and don't shift. Bar axis maps to part-X on doors and part-Y
        # on drawers; the asset's X span is the right dim either way.
        half_pull_len = pulls.pull_length(pull_obj) / 2.0

        # Vertical (X axis on door): zone-dependent. Pullout fronts are
        # excluded from the drawer branch so they fall through to the
        # cabinet-type branch below and sit at the top of the door like
        # a door pull. Their pull is rotated flat, though, so the bar's
        # vertical extent is ~0 - the half-bar-length edge correction
        # that vertical door-pull bars need doesn't apply, so vert_half
        # is 0 for pullouts.
        vert_half = 0.0 if is_pullout else half_pull_len
        if is_flip:
            # Flip door: pull centered on the UNHINGED edge. TOP hinge
            # (flip up) -> unhinged edge is the bottom, so the pull sits
            # near the door bottom; BOTTOM hinge (flip / tilt down) ->
            # unhinged edge is the top, near the door top. The bar is
            # rotated flat below (no vertical extent), so no half-bar edge
            # correction is needed here.
            if hinge == 'TOP':
                x = scene_props.pull_vertical_location_upper
            else:  # BOTTOM
                x = length - scene_props.pull_vertical_location_base
        elif kind == 'drawer' and not is_pullout:
            if scene_props.center_pulls_on_drawer_front:
                x = length / 2.0
            else:
                # Off-center moves the pull toward the top of the
                # drawer. Reuse the base vertical offset so the user
                # only has one offset to tune.
                x = length - scene_props.pull_vertical_location_base - half_pull_len
        elif cabinet_type == 'UPPER':
            x = scene_props.pull_vertical_location_upper + vert_half
        elif cabinet_type == 'TALL':
            # Three-way decision based on the door's vertical position
            # AND its length:
            #   - High door (bottom above the tall threshold) -> UPPER:
            #     small offset from door bottom, like an upper cabinet.
            #   - Door long enough to fit the tall offset -> TALL:
            #     offset from door bottom (~36" reach height).
            #   - Short door (offset would land past the door top) ->
            #     BASE: offset from door TOP, so the pull stays on the
            #     door regardless of how short it is.
            door_bottom_z = self._z_in_cabinet(front_part.obj)
            tall_offset = scene_props.pull_vertical_location_tall
            if door_bottom_z >= tall_offset:
                x = scene_props.pull_vertical_location_upper + vert_half
            elif length >= tall_offset:
                x = tall_offset + vert_half
            else:
                x = length - scene_props.pull_vertical_location_base - vert_half
        else:
            # BASE / LAP_DRAWER: measure DOWN from top of door.
            x = length - scene_props.pull_vertical_location_base - vert_half

        # Horizontal (Y axis on door): the leaf builder positions a
        # right-hinged door's local origin at the UNHINGED corner
        # (door.location.x is offset by -width so the door extends
        # back across the cabinet). Detecting that lets us flip the
        # pull to the correct edge without needing to thread
        # hinge_side through the leaf descriptor.
        if kind == 'drawer' or is_flip:
            # Drawers and flip doors: pull horizontally centered.
            # (center_pulls_on_drawer_front controls the drawer pull's
            # vertical position, not horizontal.)
            y = -width / 2.0
        elif front_part.obj.location.x < 0.0:
            # Right-hinged door: hinge at Y = -width, unhinged at Y = 0.
            y = -h_offset
        else:
            # Left-hinged door (incl. DOUBLE Left leaf): hinge at Y = 0,
            # unhinged at Y = -width.
            y = -(width - h_offset)

        # Mounting plane: pull sits flush against the door front face.
        # Without Mirror Z, the cutpart's geometry extends +Z from
        # part-local origin, so part-local z=0 is the BACK face
        # (against the cabinet) and z=+thickness is the FRONT face
        # (toward the viewer). The pull mounts on the front face.
        z = thickness

        instance = bpy.data.objects.new(f"Pull - {front_part.obj.name}", pull_obj.data)
        bpy.context.scene.collection.objects.link(instance)
        instance.parent = front_part.obj
        instance.location = (x, y, z)
        # rotation_x = -90 deg: pull body (modeled in -Y) ends up extending
        # in door-local +Z, which is away from the cabinet (beyond the
        # door front). Bar axis stays along door-local +X = vertical for
        # doors. For drawers (and pullouts) we add rotation_z = 90 deg
        # so the bar runs horizontal across the drawer front. Flip doors
        # (TOP / BOTTOM hinge) use the same horizontal-bar orientation.
        rot_z = math.radians(90.0) if (kind == 'drawer' or is_flip) else 0.0
        instance.rotation_euler = (math.radians(-90.0), 0.0, rot_z)
        instance['hb_part_role'] = 'PULL'
        instance['IS_CABINET_PULL'] = True
        return instance


    def _create_drawer_box_for_front(self, pivot_obj, leaf, rect):
        """Spawn a drawer box behind a drawer or pullout front.

        Skips quietly if the role isn't drawer/pullout, if the scene-level
        toggle is off, or if any computed dimension goes nonpositive (very
        narrow openings with large clearances). The box is parented to the
        front pivot rather than the front part: the pivot's local axes
        match the opening cage's (no rotation for slide leaves), so the
        box can be placed and sized in opening-local terms without
        composing through the front's rotated frame. Anchoring to
        pivot_anchor_position (swing=0) instead of pivot_position lets
        the box ride the slide animation - the pivot's animated Y carries
        the box forward; if we used pivot_position the box would stay at
        a fixed world Y and the front would slide out without it.

        Box dimensions fit inside the face frame opening hole minus
        per-side clearances. Box depth is the full bay cavity depth
        (cage_dim_y) minus rear clearance, so its front face sits flush
        with the back of the face frame.
        """
        if leaf['role'] not in (PART_ROLE_DRAWER_FRONT, PART_ROLE_PULLOUT_FRONT):
            return None
        scene_props = bpy.context.scene.hb_face_frame
        if not scene_props.include_drawer_boxes:
            return None

        side_clr = scene_props.drawer_box_side_clearance
        top_clr = scene_props.drawer_box_top_clearance
        rear_clr = scene_props.drawer_box_rear_clearance
        bottom_clr = scene_props.drawer_box_bottom_clearance

        cage_x = rect['cage_dim_x']
        cage_y = rect['cage_dim_y']
        cage_z = rect['cage_dim_z']
        rl = rect['reveal_left']
        rr = rect['reveal_right']
        rt = rect['reveal_top']
        rb = rect['reveal_bottom']

        # Anchor the box's front face against the back of the drawer
        # front so the two read as connected. The pivot's swing=0 Y now
        # sits AT the drawer front's back face (the front part extends
        # -Y from the pivot by door_thickness to its outer face), so the
        # back of the front lives at anchor_y. The box passes through
        # the FF opening from there and extends back to cage_dim_y -
        # rear_clr; box_dx already sits within the opening reveals, so
        # it clears the rails and stiles.
        anchor = leaf.get('pivot_anchor_position', leaf['pivot_position'])
        a_x, a_y, a_z = anchor
        front_back_y = a_y

        box_dx = cage_x - rl - rr - 2.0 * side_clr
        box_dy = (cage_y - rear_clr) - front_back_y
        box_dz = cage_z - rt - rb - top_clr - bottom_clr
        if box_dx <= 0.0 or box_dy <= 0.0 or box_dz <= 0.0:
            return None

        # Box origin (front-left-bottom corner) in opening-local coords.
        op_x = rl + side_clr
        op_y = front_back_y
        op_z = rb + bottom_clr

        box = GeoNodeDrawerBox()
        box.create('Drawer Box')
        box.obj.parent = pivot_obj
        box.obj.location = (op_x - a_x, op_y - a_y, op_z - a_z)
        box.set_input('Dim X', box_dx)
        box.set_input('Dim Y', box_dy)
        box.set_input('Dim Z', box_dz)
        box.obj['hb_part_role'] = PART_ROLE_DRAWER_BOX
        box.obj['CABINET_PART'] = True
        return box

    def _update_interior_items_in_opening(self, opening_obj, layout, rect):
        """Rebuild the opening's interior parts (shelves, accessory
        labels, ...). Same wipe-and-recreate strategy as fronts:
        interior parts hold no user state worth preserving across
        recalcs - their geometry is fully derived from the InteriorItem
        collection on the opening props.

        Panel roots (face-frame only) never have interior parts; we
        still run the wipe to clean up anything stale, then clear the
        collection and return before the spawn loop.
        """
        op_props = opening_obj.face_frame_opening

        # Wipe existing interior children. Match either by role tag or
        # by the explicit ACCESSORY marker we set on text objects, since
        # text-data objects can't carry the same custom prop conventions
        # quite as cleanly as mesh parts.
        for child in list(opening_obj.children):
            if child.get('hb_part_role') in INTERIOR_PART_ROLES:
                bpy.data.objects.remove(child, do_unlink=True)

        if not self._has_carcass():
            if len(op_props.interior_items) > 0:
                op_props.interior_items.clear()
            return

        # Share remainder between unlocked siblings of every split
        # node so users can edit either side of a divider and have
        # the other yield. No-op when the opening uses the flat path.
        # Runs before cage sizing so the leaf wireframes pick up the
        # redistributed sizes.
        self._redistribute_interior_split_tree(opening_obj, rect)

        # Bring leaf cage dims + child locations into sync with the
        # tree props before reading any rects from the tree (no-op
        # when the opening uses the flat path).
        self._update_interior_tree_cages(opening_obj, rect)

        # Sync auto-computed shelf counts for any unlocked items before
        # the solver reads them. Writing shelf_qty fires its update
        # callback which would re-enter recalculate_face_frame_cabinet,
        # but the _RECALCULATING guard short-circuits that. When a tree
        # exists, every leaf's items get the same auto rule applied
        # against the leaf's own height (so a fixed shelf splitting an
        # opening into halves seeds each half independently).
        for region_props, region_z in self._walk_interior_regions(
            opening_obj, rect,
        ):
            auto_qty = solver.auto_shelf_qty(region_z, layout.dim_y)
            for item in region_props.interior_items:
                if item.kind == 'ADJUSTABLE_SHELF' and not item.unlock_shelf_qty:
                    if item.shelf_qty != auto_qty:
                        item.shelf_qty = auto_qty
                elif (item.kind == 'ROLLOUT'
                      and len(item.rollout_boxes) == 0 and item.qty > 0):
                    # One-time migration of rollouts saved before per-box
                    # heights: seed one box per qty at the old uniform
                    # height. Guarded on an empty collection so it runs once;
                    # the writes re-enter recalc but the _RECALCULATING guard
                    # absorbs that.
                    for _ in range(item.qty):
                        box = item.rollout_boxes.add()
                        box.height_preset = 'CUSTOM'
                        box.height = item.rollout_height

        for desc in solver.interior_descriptors_for_opening(
            opening_obj, layout, rect, self.obj.face_frame_cabinet,
        ):
            kind = desc['kind']
            if kind == 'ADJUSTABLE_SHELF':
                self._create_shelf_part(opening_obj, desc)
            elif kind == 'ACCESSORY':
                self._create_accessory_label(opening_obj, desc)
            elif kind == 'ROLLOUT_BOX':
                self._create_rollout_box(opening_obj, desc)
            elif kind in ('INTERIOR_FF_RAIL', 'INTERIOR_FF_STILE'):
                self._create_interior_face_frame_part(
                    opening_obj, desc,
                )
            else:
                # All remaining mesh-based interior parts route through
                # the generic factory; orientation in the descriptor
                # drives rotation / mirror flags. Covers GLASS_SHELF,
                # PULLOUT_SHELF, PULLOUT_SPACER, ROLLOUT_SPACER,
                # TRAY_DIVIDER, TRAY_LOCKED_SHELF, VANITY_SHELF,
                # VANITY_SUPPORT.
                self._create_interior_mesh_part(opening_obj, desc)

    def _create_shelf_part(self, opening_obj, desc):
        """Horizontal panel oriented as Length+X, Width+Y, Thickness+Z
        (matches the carcass bottom panel and H-axis bay backings - no
        rotation, no mirror flags beyond the GeoNodeCage default).

        Tagged IS_FACE_FRAME_INTERIOR_PART so the 'Interiors' selection
        mode picks shelves up alongside any future interior parts.
        """
        part = CabinetPart()
        part.create(desc['name'])
        part.obj.parent = opening_obj
        part.obj['hb_part_role'] = desc['role']
        part.obj['CABINET_PART'] = True
        part.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
        part.obj.location = desc['position']
        length, width, thickness = desc['dims']
        part.set_input('Length', length)
        part.set_input('Width', width)
        part.set_input('Thickness', thickness)
        return part

    def _create_accessory_label(self, opening_obj, desc):
        """Blender text object centered in the opening, rotated to face
        the front of the cabinet. The hb_part_role tag lets the wipe
        pass find and remove it on the next recalc, same way it finds
        shelves.
        """
        font_curve = bpy.data.curves.new(type='FONT', name=desc['name'])
        font_curve.body = desc['text']
        font_curve.size = desc['size']
        font_curve.align_x = 'CENTER'
        font_curve.align_y = 'CENTER'
        text_obj = bpy.data.objects.new(desc['name'], font_curve)
        bpy.context.scene.collection.objects.link(text_obj)
        # Resolved annotation font + color (Calibri by default).
        apply_label_style(text_obj, bpy.context.scene)
        text_obj.parent = opening_obj
        text_obj.location = desc['position']
        text_obj.rotation_euler = desc['rotation']
        text_obj['hb_part_role'] = desc['role']
        # Annotation tag so the end-of-recalc cabinet-style pass
        # (toggle_cabinet_color) colors it as annotation text rather
        # than repainting it the default white.
        text_obj['IS_2D_ANNOTATION'] = True
        return text_obj

    def _redistribute_interior_split_tree(self, opening_obj, rect):
        """Top-level entry: walk the opening's interior tree and share
        the remainder among unlocked siblings of every split node. No-op
        when the opening uses the flat path. Mirrors the front-frame
        _redistribute_split_node convention so editing either child of
        a divider feels the same as editing either child of a bay split.
        """
        root = solver._interior_tree_root(opening_obj)
        if root is None:
            return
        self._redistribute_interior_node(root, rect)

    def _redistribute_interior_node(self, node, rect):
        """If node is a split, share remainder among its unlocked
        children and recurse. Leaves end the recursion. Writes happen
        inside the cabinet's _RECALCULATING guard so per-prop update
        callbacks short-circuit and don't re-enter recalc.
        """
        if not node.get(TAG_INTERIOR_SPLIT_NODE):
            return
        sp = node.face_frame_interior_split
        children = sorted(
            [c for c in node.children
             if c.get(TAG_INTERIOR_REGION)
             or c.get(TAG_INTERIOR_SPLIT_NODE)],
            key=lambda c: c.get('hb_interior_child_index', 0),
        )
        if len(children) != 2:
            return

        is_h = (sp.axis == 'H')
        parent_dim = rect['cage_dim_z'] if is_h else rect['cage_dim_x']
        div_t = sp.divider_thickness

        locked_total = 0.0
        unlocked = []
        for c in children:
            size_val, unlock = solver._read_interior_node_size(c)
            # unlock=True means hold the stored size (matches the
            # naming convention from front-frame's split tree).
            if unlock:
                locked_total += size_val
            else:
                unlocked.append(c)

        remainder = max(0.0, parent_dim - div_t - locked_total)
        share = remainder / len(unlocked) if unlocked else 0.0

        # Reuse _DISTRIBUTING_WIDTHS as the system-write guard so the
        # interior-size update callback knows these writes are not
        # user edits and skips the auto-lock.
        _DISTRIBUTING_WIDTHS.add(id(self.obj))
        try:
            for c in unlocked:
                if c.get(TAG_INTERIOR_REGION):
                    c.face_frame_interior_region.size = share
                else:
                    c.face_frame_interior_split.size = share
        finally:
            _DISTRIBUTING_WIDTHS.discard(id(self.obj))

        # Recurse with each child's resolved sub-rect
        for c in children:
            size_val, _ = solver._read_interior_node_size(c)
            if is_h:
                child_rect = {
                    'cage_dim_x': rect['cage_dim_x'],
                    'cage_dim_y': rect['cage_dim_y'],
                    'cage_dim_z': size_val,
                }
            else:
                child_rect = {
                    'cage_dim_x': size_val,
                    'cage_dim_y': rect['cage_dim_y'],
                    'cage_dim_z': rect['cage_dim_z'],
                }
            self._redistribute_interior_node(c, child_rect)

    def _update_interior_tree_cages(self, opening_obj, rect):
        """Walk the opening's interior tree and bring each cage's
        Dim X/Y/Z + each child's location into sync with the current
        tree props (axis, divider_thickness, child sizes). No-op when
        the opening has no tree.

        Mirrors the layout math in solver._walk_interior_node so the
        wireframe leaf cages render in the same positions the
        descriptor walker computes for items.
        """
        root = solver._interior_tree_root(opening_obj)
        if root is None:
            return
        # The root sits at the opening's origin and inherits the full
        # rect; downstream relative offsets accumulate via parent-child.
        root.location = (0.0, 0.0, 0.0)
        self._size_interior_node(root, rect)

    def _size_interior_node(self, node, rect):
        """Recurse: at leaves, write Dim X/Y/Z on the cage; at split
        nodes, compute child rects + relative offsets, update child
        locations, and recurse.
        """
        if node.get(TAG_INTERIOR_REGION):
            region = FaceFrameInteriorRegion(node)
            region.set_input('Dim X', rect['cage_dim_x'])
            region.set_input('Dim Y', rect['cage_dim_y'])
            region.set_input('Dim Z', rect['cage_dim_z'])
            return

        if not node.get(TAG_INTERIOR_SPLIT_NODE):
            return

        sp = node.face_frame_interior_split
        children = sorted(
            [c for c in node.children
             if c.get(TAG_INTERIOR_REGION)
             or c.get(TAG_INTERIOR_SPLIT_NODE)],
            key=lambda c: c.get('hb_interior_child_index', 0),
        )
        if len(children) != 2:
            return

        div_t = sp.divider_thickness
        cage_x = rect['cage_dim_x']
        cage_y = rect['cage_dim_y']
        cage_z = rect['cage_dim_z']
        size_a, _ = solver._read_interior_node_size(children[0])
        size_b, _ = solver._read_interior_node_size(children[1])

        if sp.axis == 'H':
            children[0].location = (0.0, 0.0, 0.0)
            children[1].location = (0.0, 0.0, size_a + div_t)
            self._size_interior_node(children[0], {
                'cage_dim_x': cage_x, 'cage_dim_y': cage_y,
                'cage_dim_z': size_a,
            })
            self._size_interior_node(children[1], {
                'cage_dim_x': cage_x, 'cage_dim_y': cage_y,
                'cage_dim_z': size_b,
            })
        else:
            children[0].location = (0.0, 0.0, 0.0)
            children[1].location = (size_a + div_t, 0.0, 0.0)
            self._size_interior_node(children[0], {
                'cage_dim_x': size_a, 'cage_dim_y': cage_y,
                'cage_dim_z': cage_z,
            })
            self._size_interior_node(children[1], {
                'cage_dim_x': size_b, 'cage_dim_y': cage_y,
                'cage_dim_z': cage_z,
            })

    def _walk_interior_regions(self, opening_obj, opening_rect):
        """Yield (region_props, region_height) pairs covering every
        leaf in the opening's interior tree. When the opening has no
        tree, yields exactly one pair: the opening's own props + the
        face frame opening height. Used by the auto-shelf-qty pass so
        each leaf seeds its shelf count from its own height, not the
        whole opening's. The catalog shelf table is keyed on the FACE
        FRAME opening height, not the carcass cage height -- the cage
        runs top rail to top panel and can sit a bracket above the
        opening the dealer measures (e.g. a 13 7/8" opening in an 18"
        upper has a ~15 3/4" cage, which wrongly earned 1 shelf).
        """
        ff_opening_h = (opening_rect['cage_dim_z']
                        - opening_rect['reveal_top']
                        - opening_rect['reveal_bottom'])
        root = solver._interior_tree_root(opening_obj)
        if root is None:
            yield (opening_obj.face_frame_opening, ff_opening_h)
            return

        def _recurse(node, dim_z):
            if node.get(TAG_INTERIOR_REGION):
                yield (node.face_frame_interior_region, dim_z)
                return
            if not node.get(TAG_INTERIOR_SPLIT_NODE):
                return
            sp = node.face_frame_interior_split
            children = sorted(
                [c for c in node.children
                 if c.get(TAG_INTERIOR_REGION)
                 or c.get(TAG_INTERIOR_SPLIT_NODE)],
                key=lambda c: c.get('hb_interior_child_index', 0),
            )
            if len(children) != 2:
                return
            size_a, _ = solver._read_interior_node_size(children[0])
            size_b, _ = solver._read_interior_node_size(children[1])
            if sp.axis == 'H':
                yield from _recurse(children[0], size_a)
                yield from _recurse(children[1], size_b)
            else:
                # V-split doesn't change Z extent for either child.
                yield from _recurse(children[0], dim_z)
                yield from _recurse(children[1], dim_z)

        yield from _recurse(root, ff_opening_h)

    def _create_interior_mesh_part(self, opening_obj, desc):
        """Generic interior mesh-part factory. Reads desc['orientation']
        for rotation / mirror conventions:

          HORIZONTAL  - no rotation, no mirror; origin = front-left-bottom.
                        Length+X, Width+Y, Thickness+Z.
          VERTICAL    - rotation_euler.y = -90 deg, Mirror Y, Mirror Z.
                        Origin = back-bottom; length runs +Z (up), width
                        runs -Y (forward). Matches Mid Division /
                        Partition Skin convention.

        Tagged IS_FACE_FRAME_INTERIOR_PART so the wipe pass picks it up
        on every recalc.
        """
        part = CabinetPart()
        part.create(desc['name'])
        part.obj.parent = opening_obj
        part.obj['hb_part_role'] = desc['role']
        part.obj['CABINET_PART'] = True
        part.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
        part.obj.location = desc['position']

        orientation = desc.get('orientation', 'HORIZONTAL')
        if orientation == 'VERTICAL':
            part.obj.rotation_euler.y = math.radians(-90)
            part.set_input('Mirror Y', True)
            part.set_input('Mirror Z', True)
        # HORIZONTAL falls through with default rotation/mirror.

        length, width, thickness = desc['dims']
        part.set_input('Length', length)
        part.set_input('Width', width)
        part.set_input('Thickness', thickness)
        return part

    def _create_interior_face_frame_part(self, opening_obj, desc):
        """Optional face frame member at an interior split node - a rail
        for a fixed shelf (kind INTERIOR_FF_RAIL) or a stile for a
        division (kind INTERIOR_FF_STILE). Rotation / mirror conventions
        match the bay mid rail and mid stile so the part lands inline
        with the cabinet face frame plane. Parented to the opening cage
        in opening-local coords and tagged IS_FACE_FRAME_INTERIOR_PART
        so the interior wipe pass rebuilds it each recalc.
        """
        part = CabinetPart()
        part.create(desc['name'])
        part.obj.parent = opening_obj
        part.obj['hb_part_role'] = desc['role']
        part.obj['CABINET_PART'] = True
        part.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
        part.obj.location = desc['position']

        if desc['kind'] == 'INTERIOR_FF_STILE':
            # Mid-stile orientation: Length+Z, Width+X, Thickness+Y.
            part.obj.rotation_euler.y = math.radians(-90)
            part.obj.rotation_euler.z = math.radians(90)
            part.set_input('Mirror Y', True)
            part.set_input('Mirror Z', True)
        else:
            # Mid-rail orientation: Length+X, Width+Z, Thickness+Y.
            part.obj.rotation_euler.x = math.radians(90)
            part.set_input('Mirror Z', True)

        length, width, thickness = desc['dims']
        part.set_input('Length', length)
        part.set_input('Width', width)
        part.set_input('Thickness', thickness)
        return part

    def _create_rollout_box(self, opening_obj, desc):
        """Drawer box for ROLLOUT items. Uses GeoNodeDrawerBox parented
        to the opening cage in opening-local coords; origin sits at the
        box's front-left-bottom corner.
        """
        box = GeoNodeDrawerBox()
        box.create(desc['name'])
        box.obj.parent = opening_obj
        box.obj['hb_part_role'] = desc['role']
        box.obj['CABINET_PART'] = True
        box.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        box.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
        box.obj.location = desc['position']
        dx, dy, dz = desc['dims']
        box.set_input('Dim X', dx)
        box.set_input('Dim Y', dy)
        box.set_input('Dim Z', dz)
        return box

    def _has_toe_kick(self):
        """Whether this cabinet sits on a toe kick. Subclasses override."""
        return False

    def _has_carcass(self):
        """Whether this root has carcass parts (sides, top, bottom, back,
        stretchers, mid divisions). False for panel-only roots that are
        just a face frame. Subclasses override.
        """
        return True

    def add_temporary_parts(self):
        """Phase 3a stub. Phase 3d implements lazy add/remove of optional
        parts (blind panels, inset toe kicks, nailers, blocking, LED notches).
        """
        pass


# ---------------------------------------------------------------------------
# Cabinet subclasses
# ---------------------------------------------------------------------------
class BaseFaceFrameCabinet(FaceFrameCabinet):
    """Standard base cabinet with toe kick. Sits on the floor."""
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.default_cabinet_width
            self.default_height = props.base_cabinet_height
            self.default_depth = props.base_cabinet_depth

    def _has_toe_kick(self):
        return True

    def create(self, name="Base Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


class FloatingBaseFaceFrameCabinet(BaseFaceFrameCabinet):
    """Base cabinet whose body is lifted off the floor on a separate
    base assembly. Same construction as BASE; toe kick type forced to
    FLOATING at create-time so the carcass sides anchor at the bay
    bottom and no recessed kick subfront is emitted.
    """

    def create(self, name="Floating Base Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        # Toe kick type override: kick_height keeps its default (the
        # gap between floor and body); change it from the cabinet
        # prompts if a taller reveal is wanted.
        cab_props = self.obj.face_frame_cabinet
        cab_props.toe_kick_type = 'FLOATING'
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


class FurnitureFaceFrameCabinet(BaseFaceFrameCabinet):
    """Shared base for freestanding furniture products (dressers, night
    stands): a base cabinet with a flush (wide-bottom-rail) kick instead
    of a recessed toe kick. The drawer / door layout is applied by the
    placement operator via default_bay_config; the flush kick is forced
    here at create time so it holds regardless of the scene toe-kick
    default. Subclasses set the default height, the bay layout (by name),
    and whether a veneer wood top is added.
    """

    def create(self, name="Furniture Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        # Furniture base: the face frame's bottom rail runs to the floor
        # (no recess), rather than the NOTCH default.
        self.obj.face_frame_cabinet.toe_kick_type = 'FLUSH'
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


class FiveDrawerDresserCabinet(FurnitureFaceFrameCabinet):
    """48"-tall dresser: split top row (two drawers) over three single
    drawers - five fronts. Gets a veneer wood top (added in a later pass)."""

    def __init__(self):
        super().__init__()
        # Spec height; overrides the inherited base_cabinet_height.
        self.default_height = inch(48.0)

    def create(self, name="5 Drawer Dresser", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        # Veneer wood top - an overhanging slab on the case. Setting the
        # prop fires the recalc callback, which builds it via
        # _apply_furniture_top now that the carcass exists.
        self.obj.face_frame_cabinet.furniture_top = True


class SixDrawerDresserCabinet(FurnitureFaceFrameCabinet):
    """60"-tall dresser: five equal rows, the top row split into two
    side-by-side drawers (six fronts). Carries a veneer wood top like the
    five-drawer."""

    def __init__(self):
        super().__init__()
        # Spec height; overrides the inherited base_cabinet_height.
        self.default_height = inch(60.0)

    def create(self, name="6 Drawer Dresser", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        # Veneer wood top - same overhanging slab as the five-drawer.
        self.obj.face_frame_cabinet.furniture_top = True


class NightStandFaceFrameCabinet(FurnitureFaceFrameCabinet):
    """24"-tall night stand: double doors, flush kick, veneer wood top.
    The double-door layout is applied by the placement operator via
    default_bay_config."""

    def __init__(self):
        super().__init__()
        self.default_height = inch(24.0)

    def create(self, name="Night Stand", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        self.obj.face_frame_cabinet.furniture_top = True


class ThreeDrawerNightStandCabinet(FurnitureFaceFrameCabinet):
    """24"-tall night stand: a single column of three equal drawers,
    flush kick, veneer wood top."""

    def __init__(self):
        super().__init__()
        self.default_height = inch(24.0)

    def create(self, name="3 Drawer Night Stand", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        self.obj.face_frame_cabinet.furniture_top = True


class WindowSeatFaceFrameCabinet(FurnitureFaceFrameCabinet):
    """18"-tall window seat: a standard BASE cabinet with a flush
    (wide-bottom-rail) kick. The flush kick comes from
    FurnitureFaceFrameCabinet (its sole behavior); unlike the dresser /
    night stand products this one gets NO furniture wood top. Each bay
    defaults to a recessed inset panel filling the opening - applied by
    the placement operator via default_bay_config ('INSET_PANEL')."""

    def __init__(self):
        super().__init__()
        # Spec height; overrides the inherited base_cabinet_height.
        self.default_height = inch(18.0)

    def create(self, name="Window Seat", bay_qty=1):
        # Flush kick is forced by the FurnitureFaceFrameCabinet create;
        # no furniture_top write here keeps the top open (no veneer slab).
        super().create(name, bay_qty=bay_qty)


class SinkFaceFrameCabinet(BaseFaceFrameCabinet):
    """Standard base cabinet sized for a sink. Default width is pulled
    from sink_cabinet_width; the bay defaults to false-front-over-doors
    via default_bay_config so the sink basin clears the upper drawer
    position with its own apron. Otherwise a plain BASE construction.
    """

    single_placement = True

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            self.default_width = scene.hb_face_frame.sink_cabinet_width


class UpperFaceFrameCabinet(FaceFrameCabinet):
    """Upper (wall) cabinet. No toe kick; mounts above the counter."""
    default_cabinet_type = 'UPPER'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.default_cabinet_width
            self.default_height = props.upper_cabinet_height
            self.default_depth = props.upper_cabinet_depth

    def _has_toe_kick(self):
        return False

    def create(self, name="Upper Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        self.create_carcass(has_toe_kick=False, bay_qty=bay_qty)
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            self.obj.location.z = scene.hb_face_frame.default_wall_cabinet_location


class BookcaseUpperFaceFrameCabinet(UpperFaceFrameCabinet):
    """Open-shelf upper bookcase meant to sit on top of base cabinets.
    Same upper construction (no toe kick), but each bay has its bottom
    panel removed (open underneath) and the default mount height is 36"
    off the floor (default_z_location) instead of the over-counter wall
    location. The open-with-shelves layout is applied by the placement
    operator via default_bay_config ('OPEN_WITH_SHELVES')."""

    # Placement reads this for the floor->bottom mount height (see
    # ops_placement._upper_mount_z); 36" sits it on a base-cabinet run.
    default_z_location = inch(36.0)

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            # Keep the same top-of-cabinet clearance from the ceiling as a
            # standard upper (top sits at ceiling - top_clearance), but
            # start at the lower 36" mount instead of the 54" wall location
            # -> taller by the difference. upper_cabinet_height already
            # bakes in (ceiling - top_clearance - wall_location), so adding
            # back (wall_location - our mount Z) re-tops it at the ceiling
            # clearance from the lower start.
            self.default_height = (
                props.upper_cabinet_height
                + (props.default_wall_cabinet_location - self.default_z_location))

    def create(self, name="Bookcase Upper", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        # Mount height for the direct-create / thumbnail path (placement
        # applies the same value via default_z_location).
        self.obj.location.z = self.default_z_location
        # Open underneath: drop each bay's bottom panel. Snapshot the bay
        # refs first - each remove_bottom write triggers a recalc that
        # reconciles carcass parts; suspend_recalc batches them.
        bay_objs = [c for c in self.obj.children if c.get(TAG_BAY_CAGE)]
        with suspend_recalc():
            for bay_obj in bay_objs:
                bay_obj.face_frame_bay.remove_bottom = True


class HutchUpperFaceFrameCabinet(UpperFaceFrameCabinet):
    """Upper cabinet whose left/right sides and end stiles drop down to the
    countertop, leaving an open recess below the box (a hutch). Standard
    upper body, mount, and height; the 'extend ends down' construction
    option is turned on at create with the drop defaulted to the gap
    between the wall-cabinet mount and the base-cabinet top."""

    def create(self, name="Hutch Upper", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        cab = self.obj.face_frame_cabinet
        cab.extend_left_end_down = True
        cab.extend_right_end_down = True
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            # Drop both ends to the counter: the wall-cabinet mount minus the
            # base-cabinet height. Editable per-side per-cabinet afterward.
            drop = (props.default_wall_cabinet_location
                    - props.base_cabinet_height)
            cab.extend_left_end_down_amount = drop
            cab.extend_right_end_down_amount = drop


class StandardRecessedMedicineCabinet(UpperFaceFrameCabinet):
    """Recessed medicine cabinet - a shallow wall-mounted upper box
    (3.75" deep x 16.25" wide x 22.75" tall). No finished ends: it sits
    recessed in the wall, so the ends aren't exposed (finish-end auto is
    turned off both sides). Front comes from default_bay_config; a single
    door at this width."""

    # Placement sinks this product into the wall so the face frame sits
    # flush with the wall face (read by the wall-placement operator).
    recess_into_wall = True

    def __init__(self):
        super().__init__()
        self.default_width = inch(16.25)
        self.default_height = inch(22.75)
        self.default_depth = inch(3.75)

    def create(self, name="Standard Recessed Medicine Cabinet", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        cab = self.obj.face_frame_cabinet
        # No finished ends - recessed in the wall, ends not exposed.
        cab.left_finish_end_auto = False
        cab.right_finish_end_auto = False
        cab.left_finished_end_condition = 'UNFINISHED'
        cab.right_finished_end_condition = 'UNFINISHED'


class MedicineCabinetFaceFrameCabinet(UpperFaceFrameCabinet):
    """Surface-mounted medicine cabinet - a standard upper cabinet (same
    default width / height / mount) at a shallow 6" depth. Ends finish
    normally (it projects from the wall), unlike the recessed variant."""

    def __init__(self):
        super().__init__()
        self.default_depth = inch(6.0)

    def create(self, name="Medicine Cabinet", bay_qty=1):
        super().create(name, bay_qty=bay_qty)


class OverstoolCabinetFaceFrameCabinet(MedicineCabinetFaceFrameCabinet):
    """Over-the-toilet cabinet: standard upper width / height at a 9" depth,
    but BOTH carcass side panels extend 7" below the box as furniture legs,
    with a decorative profile cut into the bottom-front corner of each side.
    Only the sides drop - the face frame, end stiles, doors and box stay at
    box bottom."""

    def __init__(self):
        # Deeper than the medicine cabinet it derives from (6") - over a
        # toilet it needs room for the tank/lid clearance.
        super().__init__()
        self.default_depth = inch(9.0)

    def create(self, name="Overstool Cabinet", bay_qty=1):
        super().create(name, bay_qty=bay_qty)
        cab = self.obj.face_frame_cabinet
        cab.extend_sides_down = True
        cab.extend_sides_down_amount = inch(7.0)
        cab.side_front_profile = True


class TriViewMedicineCabinetFaceFrameCabinet(MedicineCabinetFaceFrameCabinet):
    """Tri-view medicine cabinet, built per the production spec: a
    surface-mount upper (6" deep) with THREE REAL BAYS.

    - Face frame: 1-5/16" stiles -- ends AND both mid stiles -- pinned
      via the unlock flags so a style re-apply keeps them.
    - One mirror door per bay, hinged R / R / L. Every door edge takes a
      5/8" overlay (CLIPtop Blumotion 5/8"-overlay hinges), so two
      adjacent doors overlay 5/8 + 5/8 = 1-1/4" of each 1-5/16" mid
      stile and read a 1/16" reveal between the mirrors.
    - Door trim: 1-1/4" wood frame with the MEETING edges left open (no
      trim member) so the mirrors run visually edge-to-edge; only the
      two outer doors keep their outer stile. Stamped as LOCKED
      Set-Door-Frame overrides on each opening cage (the durable store),
      so cabinet edits and style re-applies keep the per-side widths.

    Earlier builds were a SINGLE opening carrying three butting leaves
    driven by the HB_TRIVIEW_DOORS flag (see solver.front_leaves); that
    solver path remains for files placed before this construction, but
    new placements use the standard three-bay machinery -- which is also
    what gives the product its mid stiles, per production."""

    TRIVIEW_STILE_W = inch(1.3125)   # 1-5/16" end + mid stiles
    TRIVIEW_OVERLAY = inch(0.625)    # 5/8" overlay hinges
    TRIVIEW_TRIM_W = inch(1.25)      # 1-1/4" wood door trim

    def create(self, name="Tri-View Medicine Cabinet", bay_qty=3):
        super().create(name, bay_qty=3)
        cab = self.obj.face_frame_cabinet
        # Mirror doors are touch-open: no pulls on any front.
        self.obj['HB_NO_DOOR_PULLS'] = True

        with suspend_recalc():
            # 1-5/16" stiles on the ends and both gaps. Unlock BEFORE
            # width so the write isn't treated as a style-cascade value.
            cab.unlock_left_stile = True
            cab.unlock_right_stile = True
            cab.left_stile_width = self.TRIVIEW_STILE_W
            cab.right_stile_width = self.TRIVIEW_STILE_W
            for entry in cab.mid_stile_widths:
                entry.unlock = True
                entry.width = self.TRIVIEW_STILE_W

            # Openings in bay order: one per bay (default upper config).
            bays = sorted(
                [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
                key=lambda b: b.face_frame_bay.bay_index)
            openings = []
            for bay in bays:
                for c in bay.children:
                    if c.get(TAG_OPENING_CAGE):
                        openings.append(c)
                        break

            hinges = ('RIGHT', 'RIGHT', 'LEFT')
            trims = (
                (self.TRIVIEW_TRIM_W, 0.0),   # left door: outer stile only
                (0.0, 0.0),                   # center door: no stiles
                (0.0, self.TRIVIEW_TRIM_W),   # right door: outer stile only
            )
            for op_obj, hinge, (left_trim, right_trim) in zip(
                    openings, hinges, trims):
                fop = op_obj.face_frame_opening
                for side in ('left', 'right', 'top', 'bottom'):
                    setattr(fop, f'unlock_{side}_overlay', True)
                    setattr(fop, f'{side}_overlay', self.TRIVIEW_OVERLAY)
                fop.hinge_side = hinge
                fop.front_type = 'DOOR'
                # Locked door-frame override on the opening cage: the
                # same durable store the Set Door Frame dialog writes.
                op_obj['HB_FRAME_OVR_LEFT_STILE'] = left_trim
                op_obj['HB_FRAME_OVR_RIGHT_STILE'] = right_trim
                op_obj['HB_FRAME_OVR_TOP_RAIL'] = self.TRIVIEW_TRIM_W
                op_obj['HB_FRAME_OVR_BOTTOM_RAIL'] = self.TRIVIEW_TRIM_W
                op_obj['HB_FRAME_OVR_MID_RAIL_MODE'] = 'NONE'
                op_obj['HB_FRAME_OVR_MID_RAIL_LOCATION'] = 0.0
                op_obj['HB_FRAME_FRAME_LOCKED'] = True
                # Fixed door look: plain square wood frame + flat mirror
                # panel, regardless of the assigned door style (see
                # _apply_mirror_door_front in props_hb_face_frame).
                op_obj['HB_MIRROR_DOOR'] = True


class TallFaceFrameCabinet(FaceFrameCabinet):
    """Tall cabinet (pantry, oven, broom). Toe kick present, full-tall."""
    default_cabinet_type = 'TALL'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.default_cabinet_width
            self.default_height = props.tall_cabinet_height
            self.default_depth = props.tall_cabinet_depth

    def _has_toe_kick(self):
        return True

    def create(self, name="Tall Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


class RefrigeratorCabinet(TallFaceFrameCabinet):
    """Tall cabinet configured to house a refrigerator: doors above,
    open zone below for the fridge.

    Construction differences from a standard tall cabinet:
    - Bay's bottom panel removed (refrigerator zone is open underneath).
    - Both end stiles extend to the floor since there's no kick recess
      to clear behind them.
    - Toe kick height is 0 (no kick recess); the open fridge zone runs
      to the floor.
    - Carcass back is raised by refrigerator_height so it spans only
      the door zone, leaving the lower zone open at the back as well.
    - Bay tree is preset to doors-on-top + appliance-on-bottom, with
      the appliance opening pinned to the scene refrigerator_height.
    """

    single_placement = True

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.refrigerator_cabinet_width

    def create(self, name="Refrigerator Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        cab_props = self.obj.face_frame_cabinet
        cab_props.extend_left_stile_to_floor = True
        cab_props.extend_right_stile_to_floor = True
        # No toe kick: the open fridge zone runs to the floor and the end
        # stiles already extend down, so there's no kick recess. Set
        # BEFORE the back_bottom_inset formula below (and create_carcass)
        # so both the single build recalc and that formula read 0.
        cab_props.toe_kick_height = 0.0
        # Raise the back so it only spans the door zone above the
        # refrigerator. Mirrors the standard back z_origin formula
        # (top of rail - mt) anchored at the top of the mid rail above
        # the appliance opening: kick + appliance + mid rail - mt. No
        # bottom_rail term: the bays carry remove_bottom (set below),
        # so the appliance opening starts at the kick top with no rail
        # below it. Captured at create-time; the user can tweak from
        # the cabinet prompts after (same formula in
        # _update_refrigerator_opening_height).
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            # Seed the per-cabinet opening height from the scene default
            # via dict-set so its update callback (which would walk for a
            # not-yet-built opening node) doesn't fire mid-create.
            cab_props['refrigerator_opening_height'] = (
                scene.hb_face_frame.refrigerator_height)
            cab_props.back_bottom_inset = (
                cab_props.toe_kick_height
                + scene.hb_face_frame.refrigerator_height
                + cab_props.bay_mid_rail_width
                - cab_props.material_thickness
            )
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)
        # Drop the bottom panel on each bay so the carcass is open
        # underneath the refrigerator zone. Snapshot the bay refs
        # first because the recalc that fires from each remove_bottom
        # write reconciles back / bottom / kick parts and would
        # invalidate sibling references mid-iteration over
        # self.obj.children. suspend_recalc batches the writes into
        # a single recalc on exit.
        bay_objs = [c for c in self.obj.children if c.get(TAG_BAY_CAGE)]
        with suspend_recalc():
            for bay_obj in bay_objs:
                bay_obj.face_frame_bay.remove_bottom = True

        # ----- Refrigerator stiles (in lieu of leg) -----
        # Two optional lower stiles (floor -> top of fridge opening), one per
        # end, hidden unless refrigerator_stile_left/right is on. Built here (not
        # in create_carcass) so only refrigerator cabinets carry them; the
        # generic recalc positions/hides them by role. Mirror the End Stile setup
        # so a lower stile lines up exactly beneath its (raised) end stile.
        left_refrig = CabinetPart()
        left_refrig.create('Left Refrigerator Stile')
        left_refrig.obj.parent = self.obj
        left_refrig.obj['hb_part_role'] = PART_ROLE_LEFT_REFRIG_STILE
        left_refrig.obj['CABINET_PART'] = True
        left_refrig.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        left_refrig.obj.rotation_euler.y = math.radians(-90)
        left_refrig.obj.rotation_euler.z = math.radians(90)
        left_refrig.set_input('Mirror Y', True)
        left_refrig.set_input('Mirror Z', True)

        right_refrig = CabinetPart()
        right_refrig.create('Right Refrigerator Stile')
        right_refrig.obj.parent = self.obj
        right_refrig.obj['hb_part_role'] = PART_ROLE_RIGHT_REFRIG_STILE
        right_refrig.obj['CABINET_PART'] = True
        right_refrig.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        right_refrig.obj.rotation_euler.y = math.radians(-90)
        right_refrig.obj.rotation_euler.z = math.radians(90)
        right_refrig.set_input('Mirror Y', False)
        right_refrig.set_input('Mirror Z', True)


class BuiltInTallFaceFrameCabinet(TallFaceFrameCabinet):
    """Tall cabinet for a built-in range / oven. Placed like a
    refrigerator: dropped at a fixed width instead of filling the wall
    gap (single_placement). Width is seeded from the scene range_width
    and stays editable during placement (type a width) and from the
    cabinet prompts afterward. The built-in appliance bay layout is
    applied by name via bay_presets.default_bay_config.
    """

    single_placement = True

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            self.default_width = scene.hb_face_frame.range_width


class BookcaseFaceFrameCabinet(TallFaceFrameCabinet):
    """Bookcase: a tall cabinet at a fixed 12" depth with a single open
    bay of adjustable shelves. Depth is locked here rather than pulled
    from tall_cabinet_depth so the bookcase stays shallow regardless of
    the tall-cabinet default; the open-with-shelves bay is applied by
    the placement operator via default_bay_config.
    """

    def __init__(self):
        super().__init__()
        self.default_depth = inch(12.0)

    def create(self, name="Bookcase", bay_qty=1):
        super().create(name, bay_qty=bay_qty)


class BookcaseStorageUnitFaceFrameCabinet(BookcaseFaceFrameCabinet):
    """Bookcase with a storage base: open adjustable shelves on top over a
    double-door cabinet below. Same 12" deep tall body as the plain
    bookcase; the split layout is applied by the placement operator via
    default_bay_config ('BOOKCASE_STORAGE')."""

    def create(self, name="Bookcase Storage Unit", bay_qty=1):
        super().create(name, bay_qty=bay_qty)


class LapDrawerFaceFrameCabinet(FaceFrameCabinet):
    """Lap drawer cabinet: a base cabinet configured to float above the
    counter with a single drawer bay. Built on the BASE construction
    (stretchers + toe kick) and overridden at create-time to FLOATING
    with a 27" lift, so the carcass sits at the lap-drawer reveal.
    """
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.default_cabinet_width
            self.default_height = props.base_cabinet_height
            self.default_depth = props.base_cabinet_depth

    def _has_toe_kick(self):
        return True

    def create(self, name="Lap Drawer Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        # Lap-drawer-specific toe kick: floating construction with the
        # cabinet body lifted to counter height. Set before create_carcass
        # so the single recalc that builds the parts uses these values.
        cab_props = self.obj.face_frame_cabinet
        cab_props.toe_kick_type = 'FLOATING'
        cab_props.toe_kick_height = inch(27.0)
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


# ---------------------------------------------------------------------------
# Helpers - cabinet lookup and recalc-from-prop-update
# ---------------------------------------------------------------------------
class PanelFaceFrameCabinet(FaceFrameCabinet):
    """Standalone face frame panel: no carcass, just rails / stiles /
    bays / openings. Same machinery as a cabinet, with carcass parts
    gated off. Default 24" x 30" x 0.75" matches a typical applied
    panel size.
    """
    default_cabinet_type = 'PANEL'

    def __init__(self):
        super().__init__()
        self.default_width = inch(24.0)
        self.default_height = inch(30.0)
        self.default_depth = inch(0.75)

    def _has_toe_kick(self):
        return False

    def _has_carcass(self):
        return False

    def create(self, name="Panel", bay_qty=1):
        self.create_cabinet_root(name)
        self.create_carcass(has_toe_kick=False, bay_qty=bay_qty)


class FaceFrameAndDoorsCabinet(PanelFaceFrameCabinet):
    """Standalone face frame + doors: a carcass-less panel (identical to the
    Panel product) whose openings default to working DOORS instead of inset
    panels. Split / change openings afterward exactly like a Panel.

    `default_opening_front_type` is read by default_front_type_for_root when
    each opening is first built. Panel-derived, so it MUST be registered in
    WRAP_CLASS_REGISTRY or recalc re-wraps it as the base carcass cabinet
    (it would gain a carcass) - see Panel / Mirror Frame.

    Openings are pinned to the placed bay count (panel_split_auto off):
    the applied-panel width ladder re-splits a standalone panel to ~18"
    openings on every recalc, which turned a 1-bay placement preview
    into a 2-bay product for anything over 20" wide. Doors follow door
    conventions, not panel aesthetics - the user splits bays manually
    (or re-enables Auto Openings) when they want more.
    """
    default_opening_front_type = 'DOOR'

    def create(self, name="Face Frame and Doors", bay_qty=1):
        self.create_cabinet_root(name)
        # Raw ID-prop write: set BEFORE the carcass builds so no
        # create-time recalc can apply the ladder, and without firing
        # the prop's update callback (which would recalc mid-create).
        self.obj.face_frame_cabinet["panel_split_auto"] = False
        self.create_carcass(has_toe_kick=False, bay_qty=bay_qty)


class MirrorFrameFaceFrameCabinet(PanelFaceFrameCabinet):
    """Mirror frame: the same flat face-frame panel as the 'Panel' product
    (no carcass - just rails / stiles), 38" wide x 28" tall x 0.75", hung on
    the wall and PLACED like an upper cabinet (mounts_as_upper).

    Built at the Panel DEFAULT size then resized - NOT created straight at
    38x28. A panel created directly at a wide width picks up stray carcass /
    blind parts (a latent quirk in the wide-bay create path); the normal
    draw-a-panel flow creates at default then resizes, which stays clean. We
    reproduce that clean path here."""

    mounts_as_upper = True

    def create(self, name="Mirror Frame", bay_qty=1):
        super().create(name, bay_qty=bay_qty)   # clean Panel at default size
        cab = self.obj.face_frame_cabinet
        cab.width = inch(38.0)
        cab.height = inch(28.0)
        # The inset panel filling the frame is the mirror: the material
        # walk paints INSET_PANEL parts of a cabinet carrying this flag
        # with the shared 'Door Panel Mirror' material (see
        # _apply_materials_to_cabinet).
        self.obj['HB_MIRROR_PANEL_FRONTS'] = True


class TubSkirtFaceFrameCabinet(PanelFaceFrameCabinet):
    """Tub skirt: the exact same flat face-frame panel as the 'Panel' product,
    just 24" tall by default instead of 30". Sits on the floor in front of a
    tub and is placed like a panel (NOT wall-mounted). Like any panel-derived
    class it MUST be registered in WRAP_CLASS_REGISTRY so recalc wraps it as a
    Panel (no carcass); an unregistered panel-derived class falls back to the
    base carcass cabinet (see Mirror Frame)."""

    def __init__(self):
        super().__init__()
        self.default_height = inch(24.0)

    def create(self, name="Tub Skirt", bay_qty=1):
        super().create(name, bay_qty=bay_qty)


class LegProductFaceFrameCabinet(FaceFrameCabinet):
    """Slim face-frame post / filler ("leg product").

    NOT a bay/opening product: a fixed parameterized assembly built from
    its own parts, parameterized by the cage width/height/depth plus the
    ``leg_product`` propgroup. Overrides ``recalculate()`` to build and
    lay out its parts directly instead of running bay reconciliation, so
    none of the carcass / solver machinery applies.

    Parts: left + right side panels (finished, with a front-bottom
    toe-kick notch), finished front Finish-X bands, an interior back +
    left/right nailers, a full-width face-frame stile, and a toe-kick
    stile + filler. ``finish_type`` drives which panels show / are
    finished; ``only_stile`` keeps just the stile; ``is_column`` drops
    the toe kick; the per-panel depth overrides and nailer toggles size
    the back. ``is_appliance_leg`` / ``is_island_leg`` are placement
    metadata only (no geometry effect yet).
    """
    single_placement = True
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        self.default_width = inch(2.0)
        # Height / depth follow the scene's base-cabinet defaults so a
        # leg matches the base cabinets beside it (width stays a slim 2").
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_height = props.base_cabinet_height
            self.default_depth = props.base_cabinet_depth

    def _has_toe_kick(self):
        return False

    def _has_carcass(self):
        return False

    def create(self, name="Leg", bay_qty=1):
        # create_cabinet_root writes width/height/depth, which fire the
        # update callback -> recalculate(); CLASS_NAME is already set by
        # then, so the obj wraps as this class and our recalculate() runs
        # (ensuring + laying out parts). The explicit recalculate() below
        # is a harmless belt-and-suspenders for the LEG_PRODUCT_TAG write.
        self.create_cabinet_root(name)
        self.obj[LEG_PRODUCT_TAG] = True
        # Use the leg-specific right-click menu rather than the default
        # cabinet command menu (no bays / joins / wedge for a leg).
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_leg_product_commands'
        self.recalculate()

    # ------------------------------------------------------------------
    # Part lifecycle
    # ------------------------------------------------------------------
    def _ensure_leg_part(self, role, name, add_notch=False):
        """Lazily create one leg CabinetPart keyed by role. Side panels
        get a front-bottom corner-notch modifier for the toe-kick recess."""
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                return child
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        if add_notch:
            # Front-bottom toe-kick notch. Flip orientation matches the
            # carcass side's "Notch Front Bottom"; verify against the
            # rendered panel and flip if the notch lands on the wrong
            # corner (the panels are rotated Ry=-90).
            cpm = part.add_part_modifier('CPM_CORNERNOTCH', 'Front Notch')
            cpm.set_input('Flip X', False)
            cpm.set_input('Flip Y', True)
        return part.obj

    def _ensure_leg_parts(self):
        """Ensure all leg parts exist. Returns a role -> object map. The
        finished front bands (Finish-X) carry a toe-kick notch like the
        side panels; the interior back / nailers do not."""
        spec = (
            (PART_ROLE_LEG_PANEL_LEFT, 'Leg Panel Left', True),
            (PART_ROLE_LEG_PANEL_RIGHT, 'Leg Panel Right', True),
            (PART_ROLE_LEG_FINISH_X_LEFT, 'Leg Finish Left X', True),
            (PART_ROLE_LEG_FINISH_X_RIGHT, 'Leg Finish Right X', True),
            (PART_ROLE_LEG_BACK, 'Leg Back', False),
            (PART_ROLE_LEG_NAILER_LEFT, 'Leg Nailer Left', False),
            (PART_ROLE_LEG_NAILER_RIGHT, 'Leg Nailer Right', False),
            (PART_ROLE_LEG_STILE, 'Leg Stile', False),
            (PART_ROLE_LEG_TK_STILE, 'Leg Toe Kick Stile', False),
            (PART_ROLE_LEG_TK_FILLER, 'Leg Toe Kick Filler', False),
        )
        return {role: self._ensure_leg_part(role, name, add_notch)
                for role, name, add_notch in spec}

    @staticmethod
    def _set_notch(panel_obj, active, x, y, route_depth):
        """Drive a side panel's 'Front Notch' CPM_CORNERNOTCH inputs +
        visibility. No-op if the modifier is missing."""
        mod = panel_obj.modifiers.get('Front Notch')
        if mod is None or mod.node_group is None:
            return
        ng = mod.node_group
        for input_name, value in (('X', x), ('Y', y), ('Route Depth', route_depth)):
            node_input = ng.interface.items_tree.get(input_name)
            if node_input is not None:
                hb_utils.set_gn_input(mod, node_input.identifier, value)
        mod.show_viewport = active
        mod.show_render = active

    # ------------------------------------------------------------------
    # Recalc (bespoke; bypasses the bay solver)
    # ------------------------------------------------------------------
    def recalculate(self):
        cab = self.obj.face_frame_cabinet
        leg = self.obj.leg_product

        width = cab.width
        height = cab.height
        depth = cab.depth
        # Keep the wireframe cage in sync, same as the base recalc.
        self.set_input('Dim X', width)
        self.set_input('Dim Y', depth)
        self.set_input('Dim Z', height)

        mt = leg.material_thickness
        fft = leg.face_frame_thickness
        tks = leg.toe_kick_setback
        tkh = 0.0 if leg.is_column else leg.toe_kick_height
        finish = leg.finish_type
        only_stile = leg.only_stile
        # A side carrying an applied paneled end (Paneled / False FF /
        # Working FF) hands its finished face to the applied panel, so
        # the leg's own side panel + Finish-X band on that side drop out.
        left_paneled = (cab.left_finished_end_condition
                        in APPLIED_PANEL_END_TYPES)
        right_paneled = (cab.right_finished_end_condition
                         in APPLIED_PANEL_END_TYPES)
        # v2 reads
        olp = leg.override_left_panel_depth
        orp = leg.override_right_panel_depth
        ibln = leg.include_back_left_nailer
        ibrn = leg.include_back_right_nailer
        has_back = ibln or ibrn
        b_width = leg.back_width
        bt = leg.back_thickness
        nt = leg.nailer_thickness
        nw = leg.nailer_width
        fx_width = leg.flush_x_panel_width

        parts = self._ensure_leg_parts()
        L = parts[PART_ROLE_LEG_PANEL_LEFT]
        R = parts[PART_ROLE_LEG_PANEL_RIGHT]
        FXL = parts[PART_ROLE_LEG_FINISH_X_LEFT]
        FXR = parts[PART_ROLE_LEG_FINISH_X_RIGHT]
        BACK = parts[PART_ROLE_LEG_BACK]
        NL = parts[PART_ROLE_LEG_NAILER_LEFT]
        NR = parts[PART_ROLE_LEG_NAILER_RIGHT]
        STILE = parts[PART_ROLE_LEG_STILE]
        TKS = parts[PART_ROLE_LEG_TK_STILE]
        TKF = parts[PART_ROLE_LEG_TK_FILLER]

        # Back shifts the side panels forward by its thickness.
        back_off = bt if has_back else 0.0

        def place(obj, length, w, thickness, loc, rot, mirror):
            gn = GeoNodeCutpart(obj)
            gn.set_input('Length', length)
            gn.set_input('Width', w)
            gn.set_input('Thickness', thickness)
            obj.location = loc
            obj.rotation_euler = rot
            for k, v in mirror.items():
                gn.set_input(k, v)

        # --- Left side panel ---
        if finish == 'INTERMEDIATE':
            l_x = width / 2.0 - mt / 2.0
        elif finish == 'FINISH_RIGHT':
            l_x = width - mt
        else:  # FINISH_LEFT / FINISH_BOTH
            l_x = 0.0
        l_depth = olp if olp > 0.0 else depth - fft
        l_y = (0.0 if olp <= 0.0 else -depth + olp + fft) - back_off
        place(L, height, l_depth, mt, (l_x, l_y, 0.0),
              (0.0, math.radians(-90), 0.0),
              {'Mirror Y': True, 'Mirror Z': True})
        l_visible = not (finish == 'FINISH_RIGHT' or only_stile) and not left_paneled
        L.hide_viewport = not l_visible
        L.hide_render = not l_visible
        L['IS_FINISHED'] = (finish != 'INTERMEDIATE')

        # --- Right side panel ---
        r_depth = orp if orp > 0.0 else depth - fft
        r_y = (0.0 if orp <= 0.0 else -depth + orp + fft) - back_off
        place(R, height, r_depth, mt, (width, r_y, 0.0),
              (0.0, math.radians(-90), 0.0),
              {'Mirror Y': True, 'Mirror Z': False})
        r_visible = finish in ('FINISH_RIGHT', 'FINISH_BOTH') and not only_stile and not right_paneled
        R.hide_viewport = not r_visible
        R.hide_render = not r_visible
        R['IS_FINISHED'] = True

        # --- Toe-kick notch on the visible panels ---
        notch_on = (not leg.is_column) and (not only_stile) and tkh > 0.0
        self._set_notch(L, notch_on and l_visible, tkh, tks - fft, mt)
        self._set_notch(R, notch_on and r_visible, tkh, tks - fft, mt)

        # --- Face-frame stile (full width across the front) ---
        place(STILE, height - tkh, width, fft, (0.0, -depth, tkh),
              (0.0, math.radians(-90), math.radians(90)),
              {'Mirror Y': True, 'Mirror Z': True})
        STILE['IS_FINISHED'] = True

        # --- Toe-kick stile + filler (between the side panels) ---
        tk_width = width - (0.0 if only_stile else mt * 2.0)
        tk_x = 0.0 if only_stile else mt
        tk_visible = (not leg.is_column) and (only_stile or finish == 'FINISH_BOTH')

        place(TKS, tkh, tk_width, fft, (tk_x, -depth + tks, 0.0),
              (0.0, math.radians(-90), math.radians(90)),
              {'Mirror Y': True, 'Mirror Z': True})
        TKS.hide_viewport = not tk_visible
        TKS.hide_render = not tk_visible
        TKS['IS_FINISHED'] = True

        place(TKF, tks, tk_width, fft, (tk_x, -depth + tks + fft, tkh),
              (0.0, 0.0, math.radians(90)),
              {'Mirror Y': True, 'Mirror X': True})
        TKF.hide_viewport = not tk_visible
        TKF.hide_render = not tk_visible
        TKF['IS_FINISHED'] = True

        # --- Finished front bands (Finish-X) -------------------------
        # A finished band covering the front fx_width inches on the
        # side whose panel is NOT the primary finished face. Its
        # "thickness" (set_input Thickness) is the band's X extent.
        notch_route_ext = inch(0.1)

        # Left band: shown for INTERMEDIATE / FINISH_RIGHT.
        fxl_t = (width - mt) if finish == 'FINISH_RIGHT' else (width / 2.0 - mt / 2.0)
        place(FXL, height, fx_width, fxl_t, (0.0, -depth + fft + fx_width, 0.0),
              (0.0, math.radians(-90), 0.0),
              {'Mirror Y': True, 'Mirror Z': True})
        fxl_vis = finish in ('INTERMEDIATE', 'FINISH_RIGHT') and not only_stile and not left_paneled
        FXL.hide_viewport = not fxl_vis
        FXL.hide_render = not fxl_vis
        FXL['IS_FINISHED'] = True
        self._set_notch(FXL, notch_on and fxl_vis, tkh, tks - fft, fxl_t + notch_route_ext)

        # Right band: shown for FINISH_LEFT / INTERMEDIATE.
        fxr_t = (width - mt) if finish == 'FINISH_LEFT' else (width / 2.0 - mt / 2.0)
        place(FXR, height, fx_width, fxr_t, (width, -depth + fft + fx_width, 0.0),
              (0.0, math.radians(-90), 0.0),
              {'Mirror Y': True, 'Mirror Z': False})
        fxr_vis = finish in ('FINISH_LEFT', 'INTERMEDIATE') and not only_stile and not right_paneled
        FXR.hide_viewport = not fxr_vis
        FXR.hide_render = not fxr_vis
        FXR['IS_FINISHED'] = True
        self._set_notch(FXR, notch_on and fxr_vis, tkh, tks - fft, fxr_t + notch_route_ext)

        # --- Interior back + nailers ---------------------------------
        # Back spans only the included nailer side(s); it sits at y=0
        # (the very back) and the side panels were shifted forward to
        # clear it.
        back_w = (b_width if ibln else 0.0) + (b_width if ibrn else 0.0)
        back_x = width / 2.0 + (b_width if ibrn else 0.0)
        place(BACK, height, back_w, bt, (back_x, 0.0, 0.0),
              (0.0, math.radians(-90), math.radians(-90)),
              {'Mirror Y': True, 'Mirror Z': True})
        BACK.hide_viewport = not has_back
        BACK.hide_render = not has_back

        # Horizontal nailers at the top back, one per included side.
        place(NL, b_width, nw, nt, (width / 2.0, 0.0, height),
              (math.radians(90), 0.0, 0.0),
              {'Mirror X': True, 'Mirror Y': True})
        NL.hide_viewport = not ibln
        NL.hide_render = not ibln

        place(NR, b_width, nw, nt, (width / 2.0, 0.0, height),
              (math.radians(90), 0.0, 0.0),
              {'Mirror X': False, 'Mirror Y': True})
        NR.hide_viewport = not ibrn
        NR.hide_render = not ibrn

        # --- Applied finished-end panels (Left / Right) --------------
        # The leg recalc bypasses the bay solver, so the shared
        # _reconcile_applied_panels needs a minimal layout snapshot: just
        # the fields applied_panel_geometry and the scribe-offset helpers
        # read (overall dims, face-frame thickness, each side's finish
        # condition + scribe). Only Left / Right are offered in the leg
        # UI; Back stays UNFINISHED so no back panel is built. A side left
        # UNFINISHED produces no panel, so this is opt-in and cheap.
        leg_layout = SimpleNamespace(
            dim_x=width,
            dim_y=depth,
            dim_z=height,
            fft=fft,
            l_fin_end=cab.left_finished_end_condition,
            r_fin_end=cab.right_finished_end_condition,
            l_scribe=cab.left_scribe,
            r_scribe=cab.right_scribe,
        )
        self._reconcile_applied_panels(leg_layout)


class FloatingShelfFaceFrameCabinet(FaceFrameCabinet):
    """Wall-mounted floating shelf (a hollow finished slab).

    NOT a bay/opening product: a fixed parameterized box built directly,
    parameterized by the cage width / depth + height (height = the
    shelf's overall thickness) and the ``floating_shelf`` propgroup.
    Overrides ``recalculate()`` to build its parts (front board, inset
    top + bottom, and finish-gated left/right end panels) instead of the
    carcass / solver machinery. No back - it mounts open against a wall.

    ``follow_cursor_z`` makes placement track the cursor's height on the
    wall instead of dropping to floor / a fixed upper height. LED routes
    (top / bottom cutouts) are a later pass.
    """
    single_placement = False
    fill_no_bays = True       # fill the wall gap, but always one piece
    follow_cursor_z = True    # mount at the cursor's height on the wall
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = getattr(bpy.context, 'scene', None)
        ff_scene = getattr(scene, 'hb_face_frame', None) if scene else None
        self.default_width = getattr(ff_scene, 'default_cabinet_width', inch(36.0))
        self.default_depth = inch(12.0)
        self.default_height = inch(2.5)   # shelf overall thickness

    def _has_toe_kick(self):
        return False

    def _has_carcass(self):
        return False

    def create(self, name="Floating Shelf", bay_qty=1):
        self.create_cabinet_root(name)
        self.obj[FLOATING_SHELF_TAG] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_floating_shelf_commands'
        self.recalculate()

    def _ensure_shelf_part(self, role, name, add_groove=False):
        # MENU_ID is (re)stamped on existing parts too so shelves built
        # before the parts had their own right-click menu pick it up on
        # their next recalc. The shared part menu carries Add Cutout and
        # Make Editable.
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                child['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
                return child
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        if add_groove:
            # Light groove (LED channel) for Heavy Duty shelves; driven
            # + toggled in recalculate().
            part.add_part_modifier('CPM_CUTOUT', 'Groove')
        return part.obj

    def _ensure_shelf_parts(self):
        spec = (
            (PART_ROLE_SHELF_FRONT, 'Shelf Front', False),
            (PART_ROLE_SHELF_TOP, 'Shelf Top', True),
            (PART_ROLE_SHELF_BOTTOM, 'Shelf Bottom', True),
            (PART_ROLE_SHELF_PANEL_LEFT, 'Shelf Panel Left', False),
            (PART_ROLE_SHELF_PANEL_RIGHT, 'Shelf Panel Right', False),
        )
        return {role: self._ensure_shelf_part(role, name, g)
                for role, name, g in spec}

    @staticmethod
    def _set_groove(panel_obj, active, x0, y0, x1, y1, depth, flip_z):
        """Drive a shelf panel's 'Groove' CPM_CUTOUT (X/Y/End X/End Y/
        Route Depth/Flip Z) + visibility. No-op if missing."""
        mod = panel_obj.modifiers.get('Groove')
        if mod is None or mod.node_group is None:
            return
        ng = mod.node_group
        for name, val in (('X', x0), ('Y', y0), ('End X', x1),
                          ('End Y', y1), ('Route Depth', depth)):
            ni = ng.interface.items_tree.get(name)
            if ni is not None:
                hb_utils.set_gn_input(mod, ni.identifier, val)
        fz = ng.interface.items_tree.get('Flip Z')
        if fz is not None:
            hb_utils.set_gn_input(mod, fz.identifier, flip_z)
        mod.show_viewport = active
        mod.show_render = active

    def recalculate(self):
        cab = self.obj.face_frame_cabinet
        shelf = self.obj.floating_shelf

        width = cab.width
        thickness = cab.height   # Dim Z = shelf overall thickness
        depth = cab.depth
        self.set_input('Dim X', width)
        self.set_input('Dim Y', depth)
        self.set_input('Dim Z', thickness)

        mt = shelf.material_thickness
        fl = shelf.finish_left
        fr = shelf.finish_right

        parts = self._ensure_shelf_parts()
        FRONT = parts[PART_ROLE_SHELF_FRONT]
        TOP = parts[PART_ROLE_SHELF_TOP]
        BOTTOM = parts[PART_ROLE_SHELF_BOTTOM]
        LP = parts[PART_ROLE_SHELF_PANEL_LEFT]
        RP = parts[PART_ROLE_SHELF_PANEL_RIGHT]

        def place(obj, length, w, th, loc, rot, mirror):
            # A Make Editable part owns its mesh and transform (its GN
            # was applied, so set_input would fail anyway) - leave it
            # alone; Revert to Parametric re-adds the GN and the next
            # recalc re-drives it here.
            if obj.get('IS_MANUAL_PART'):
                return
            gn = GeoNodeCutpart(obj)
            gn.set_input('Length', length)
            gn.set_input('Width', w)
            gn.set_input('Thickness', th)
            obj.location = loc
            obj.rotation_euler = rot
            for k, v in mirror.items():
                gn.set_input(k, v)

        inset_l = mt if fl else 0.0
        inset_r = mt if fr else 0.0
        inner_len = width - inset_l - inset_r
        inner_depth = depth - mt

        # Front board: full width, stands `thickness` tall at the front.
        place(FRONT, width, thickness, mt, (0.0, -depth, 0.0),
              (math.radians(-90), 0.0, 0.0), {'Mirror Y': True})
        FRONT['IS_FINISHED'] = True

        # Top + bottom: horizontal panels between the end panels, behind
        # the front board, spanning the remaining depth.
        place(TOP, inner_len, inner_depth, mt, (inset_l, -depth + mt, thickness),
              (0.0, 0.0, 0.0), {'Mirror Z': True})
        TOP['IS_FINISHED'] = True
        place(BOTTOM, inner_len, inner_depth, mt, (inset_l, -depth + mt, 0.0),
              (0.0, 0.0, 0.0), {})
        BOTTOM['IS_FINISHED'] = True

        # End panels: close each end when finished.
        place(LP, inner_depth, thickness, mt, (0.0, 0.0, 0.0),
              (math.radians(-90), 0.0, math.radians(90)),
              {'Mirror X': True, 'Mirror Y': True, 'Mirror Z': True})
        if not LP.get('IS_MANUAL_PART'):
            LP.hide_viewport = not fl
            LP.hide_render = not fl
        LP['IS_FINISHED'] = True

        place(RP, inner_depth, thickness, mt, (width, 0.0, 0.0),
              (math.radians(-90), 0.0, math.radians(90)),
              {'Mirror X': True, 'Mirror Y': True})
        if not RP.get('IS_MANUAL_PART'):
            RP.hide_viewport = not fr
            RP.hide_render = not fr
        RP['IS_FINISHED'] = True

        # --- Light groove (Heavy Duty shelves only) ---
        # A routed LED channel on the top and/or bottom face, set a
        # distance in from the rear edge. Panel-local Y runs front (0)
        # -> rear (inner_depth), so measure in from inner_depth.
        hd = shelf.shelf_type == 'HEAVY_DUTY'
        g_w = shelf.groove_width
        g_depth = shelf.groove_depth
        y_far = inner_depth - shelf.groove_distance_from_rear  # rear edge of groove
        y_near = y_far - g_w                                   # front edge of groove
        gx0, gx1 = -0.005, inner_len + 0.005                   # span full length
        # Flip Z picks the cut face; top cuts its top face, bottom its
        # bottom. Verify against the render and flip if reversed.
        # A manual part's Groove modifier stays live on the applied mesh
        # (Make Editable only applies the cutpart) - leave it alone too.
        if not TOP.get('IS_MANUAL_PART'):
            self._set_groove(TOP, hd and shelf.include_groove_top,
                             gx0, y_near, gx1, y_far, g_depth, True)
        if not BOTTOM.get('IS_MANUAL_PART'):
            self._set_groove(BOTTOM, hd and shelf.include_groove_bottom,
                             gx0, y_near, gx1, y_far, g_depth, False)


class ValanceFaceFrameProduct(FaceFrameCabinet):
    """Wall-mounted valance - a decorative board spanning the gap
    between two upper cabinets (e.g. over a sink or a window).

    NOT a bay/opening product: like the floating shelf it is a fixed
    parameterized assembly built directly from the cage width / depth /
    height (height = the board's vertical drop) and the
    ``valance_product`` propgroup. Parts: the valance board across the
    front, finish-gated left/right return panels back to the wall, and
    an optional top cover recessed below the top edge by a scribe
    amount (or resting at the bottom when flush_bottom).

    ``fill_no_bays`` spans the wall gap as one piece in placement;
    ``follow_cursor_z`` mounts it at the cursor's height on the wall
    (typically flush with the bottom of the adjacent uppers).
    """
    single_placement = False
    fill_no_bays = True       # span the gap, but always one piece
    follow_cursor_z = True    # mount at the cursor's height on the wall
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = getattr(bpy.context, 'scene', None)
        ff_scene = getattr(scene, 'hb_face_frame', None) if scene else None
        self.default_width = inch(30.0)
        self.default_depth = getattr(ff_scene, 'upper_cabinet_depth', inch(12.0))
        self.default_height = inch(4.0)   # board vertical drop

    def _has_toe_kick(self):
        return False

    def _has_carcass(self):
        return False

    def create(self, name="Valance", bay_qty=1):
        # bay_qty is accepted (the modal always passes it) but ignored -
        # a valance has no bays.
        self.create_cabinet_root(name)
        self.obj[VALANCE_TAG] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_valance_commands'
        self.recalculate()

    def _ensure_valance_part(self, role, name):
        # MENU_ID is (re)stamped on existing parts too so valances built
        # before the parts had their own right-click menu pick it up on
        # their next recalc. The shared part menu carries Add Cutout and
        # Make Editable (an arched valance board is cut that way).
        for child in self.obj.children:
            if child.get('hb_part_role') == role:
                child['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
                return child
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        return part.obj

    def recalculate(self):
        cab = self.obj.face_frame_cabinet
        val = self.obj.valance_product

        width = cab.width
        height = cab.height   # Dim Z = the board's vertical drop
        depth = cab.depth
        self.set_input('Dim X', width)
        self.set_input('Dim Y', depth)
        self.set_input('Dim Z', height)

        ft = val.frame_thickness   # board + return panel stock
        ct = val.cover_thickness   # top cover stock
        fl = val.finish_left
        fr = val.finish_right

        BOARD = self._ensure_valance_part(PART_ROLE_VALANCE_BOARD, 'Valance Board')
        COVER = self._ensure_valance_part(PART_ROLE_VALANCE_COVER, 'Valance Cover')
        LP = self._ensure_valance_part(PART_ROLE_VALANCE_PANEL_LEFT, 'Valance Panel Left')
        RP = self._ensure_valance_part(PART_ROLE_VALANCE_PANEL_RIGHT, 'Valance Panel Right')

        def place(obj, length, w, th, loc, rot, mirror):
            # A Make Editable part owns its mesh and transform (its GN
            # was applied, so set_input would fail anyway) - leave it
            # alone; Revert to Parametric re-adds the GN and the next
            # recalc re-drives it here.
            if obj.get('IS_MANUAL_PART'):
                return
            gn = GeoNodeCutpart(obj)
            gn.set_input('Length', length)
            gn.set_input('Width', w)
            gn.set_input('Thickness', th)
            obj.location = loc
            obj.rotation_euler = rot
            for k, v in mirror.items():
                gn.set_input(k, v)

        inset_l = ft if fl else 0.0
        inset_r = ft if fr else 0.0
        inner_len = width - inset_l - inset_r
        inner_depth = depth - ft   # behind the board, back to the wall

        # Valance board: full width across the front, `height` tall.
        # Same transform convention as a cabinet bottom rail (+90 X,
        # Mirror Z) - identical world geometry to the old -90/Mirror Y
        # placement, but it lets _position_bottom_rail_profile_cutter
        # cut the decorative bottom profile in the board's local space
        # exactly as it does on a bottom rail. Mirror Y is written
        # False explicitly so valances placed before this change
        # migrate on their next recalc.
        place(BOARD, width, height, ft, (0.0, -depth, 0.0),
              (math.radians(90), 0.0, 0.0),
              {'Mirror Y': False, 'Mirror Z': True})
        BOARD['IS_FINISHED'] = True

        # Return panels: close each end back to the wall when finished.
        place(LP, inner_depth, height, ft, (0.0, 0.0, 0.0),
              (math.radians(-90), 0.0, math.radians(90)),
              {'Mirror X': True, 'Mirror Y': True, 'Mirror Z': True})
        if not LP.get('IS_MANUAL_PART'):
            LP.hide_viewport = not fl
            LP.hide_render = not fl
        LP['IS_FINISHED'] = True

        place(RP, inner_depth, height, ft, (width, 0.0, 0.0),
              (math.radians(-90), 0.0, math.radians(90)),
              {'Mirror X': True, 'Mirror Y': True})
        if not RP.get('IS_MANUAL_PART'):
            RP.hide_viewport = not fr
            RP.hide_render = not fr
        RP['IS_FINISHED'] = True

        # Top cover: Mirror Z makes the given Z the panel's TOP face -
        # recessed below the top edge by the scribe amount, or occupying
        # 0..thickness at the floor of the valance when flush_bottom.
        cover_z = ct if val.flush_bottom else height - val.top_scribe
        place(COVER, inner_len, inner_depth, ct,
              (inset_l, -depth + ft, cover_z), (0.0, 0.0, 0.0),
              {'Mirror Z': True})
        if not COVER.get('IS_MANUAL_PART'):
            COVER.hide_viewport = not val.include_cover
            COVER.hide_render = not val.include_cover
        COVER['IS_FINISHED'] = True

        # Decorative bottom profile on the front board - the cabinet
        # bottom_rail_profile option applied to the valance. Reuses the
        # bottom-rail cutter machinery verbatim (the board shares the
        # rail transform convention above). A manual board is left
        # entirely alone: its cut, if any, is baked or riding the
        # existing boolean, and the cutter can't be rebuilt from an
        # applied GN anyway.
        if not BOARD.get('IS_MANUAL_PART'):
            profile_id = getattr(cab, 'bottom_rail_profile', 'NONE')
            is_arch = profile_id == _BOTTOM_RAIL_PROFILE_ARCH
            poly = (None if (is_arch or profile_id in ('NONE', ''))
                    else _bottom_rail_profile_poly(profile_id))
            if profile_id in ('NONE', '') or (not is_arch and not poly):
                mod = BOARD.modifiers.get(BOTTOM_RAIL_PROFILE_CUT_MOD_NAME)
                if mod is not None:
                    BOARD.modifiers.remove(mod)
                self._cleanup_bottom_rail_profile_cutters()
            else:
                cutter = self._ensure_bottom_rail_profile_cutter('VALANCE_BOARD')
                ok = self._position_bottom_rail_profile_cutter(
                    cutter, BOARD, profile_id, poly)
                mod = BOARD.modifiers.get(BOTTOM_RAIL_PROFILE_CUT_MOD_NAME)
                if not ok:
                    if mod is not None:
                        BOARD.modifiers.remove(mod)
                else:
                    if mod is None:
                        mod = BOARD.modifiers.new(
                            name=BOTTOM_RAIL_PROFILE_CUT_MOD_NAME,
                            type='BOOLEAN')
                        mod.operation = 'DIFFERENCE'
                        mod.solver = 'EXACT'
                    if mod.object is not cutter:
                        mod.object = cutter


class MiscPart(CabinetPart):
    """A single freely-resizable face frame part - a lone GeoNodeCutpart
    with NO cabinet cage.

    Unlike Panel / Leg / Floating Shelf (which are FaceFrameCabinet
    subclasses carrying a cage), a Misc Part is just a board: it stays out
    of Cabinets selection mode and carries none of the carcass / bay /
    opening machinery. It rides the standard place_cabinet modal, which
    special-cases cage-less products in _finalize (see
    operators/ops_placement.py) - it has no face_frame_cabinet propgroup
    for the cabinet path to write to. The default_* attrs feed that modal's
    preview cage; single_placement keeps it one fixed-width piece.
    """
    single_placement = True
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        # Dim X = width, Dim Y = depth, Dim Z = height (thickness). A flat
        # 24 x 12 x 3/4 board out of the box; resize after placement.
        self.default_width = inch(24.0)
        self.default_depth = inch(12.0)
        self.default_height = inch(0.75)

    def create(self, name="Misc Part", bay_qty=1):
        # bay_qty is accepted (the modal always passes it) but ignored - a
        # Misc Part has no bays. CabinetPart.create lays down the
        # GeoNodeCutpart + default inputs; we then size it, mark it a Misc
        # Part, and finish both faces.
        super().create(name)
        self.obj['IS_FACE_FRAME_MISC_PART'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_misc_part_commands'
        self.set_input('Length', self.default_width)
        self.set_input('Width', self.default_depth)
        self.set_input('Thickness', self.default_height)
        self.set_input('Mirror Y', True)
        self.obj['Finish Top'] = True
        self.obj['Finish Bottom'] = True

    # --- placement hooks (read by place_cabinet._finalize for bare parts) ---
    placement_stand_rotation = None  # Misc Part lies flat; no reorient.

    def apply_placement_width(self, width):
        """The cage width maps to the board's X span = its 'Length' input."""
        self.set_input('Length', width)


# Door Part: stand-up rotation so a standalone door reads vertical with
# its front face toward the room. Euler X=90 (the configured
# default), Y=-90: localX(Length=height)->world Z (up), localY(Width)->
# world X (across), and the front face (local +Z = thickness) points
# world -Y (toward the viewer). place_cabinet._finalize composes this
# onto the placement transform. Flip the X sign to face the door the
# other way.
_DOOR_PART_STAND = Euler((math.radians(90.0), math.radians(-90.0), 0.0),
                         'XYZ').to_matrix().to_4x4()


def _active_door_style():
    """The Face_Frame_Door_Style of the project's ACTIVE cabinet style, or
    None. Mirrors _apply_door_styles_to_fronts' resolution: active cabinet
    style -> its door_style name -> ff.door_styles lookup."""
    from . import props_hb_face_frame as props
    ff = props.get_style_props()
    if ff is None:
        return None
    idx = ff.active_cabinet_style_index
    if not (0 <= idx < len(ff.cabinet_styles)):
        return None
    name = ff.cabinet_styles[idx].door_style
    if not name or name == 'NONE':
        return None
    for ds in ff.door_styles:
        if ds.name == name:
            return ds
    return None


def apply_active_door_style_to_part(door_obj):
    """Apply the active cabinet style's door style to a Door Part front
    (assign_style_to_front adds / strips the CPM_5PIECEDOOR 'Door Style'
    modifier and stamps DOOR_STYLE_NAME). Also records the source cabinet
    style as STYLE_NAME so a later style-update pass can find it. No-op if
    nothing resolves."""
    from . import props_hb_face_frame as props
    ds = _active_door_style()
    if ds is None:
        return
    ds.assign_style_to_front(door_obj)
    ff = props.get_style_props()
    if ff is not None and 0 <= ff.active_cabinet_style_index < len(ff.cabinet_styles):
        door_obj['STYLE_NAME'] = ff.cabinet_styles[ff.active_cabinet_style_index].name


def apply_active_finish_to_product(product_obj):
    """Assign the project's ACTIVE cabinet style's exterior FINISH material
    to every cutpart under a non-cabinet face-frame PRODUCT (e.g. a Half
    Wall) and record the source style as STYLE_NAME.

    A product built from the frameless part primitives carries no
    hb_part_role, so the cabinet material walk (_apply_materials_to_cabinet,
    which dispatches by role and reads face_frame_cabinet side conditions)
    skips it entirely. A half wall is a single finished element, so the
    faithful behavior is the style's finish on every surface - surface =
    finish, edges = the rotated variant, mirroring the cabinet exterior-role
    branch. No-op if no style resolves or the finish is unresolved (e.g.
    CUSTOM species with no custom_material picked yet)."""
    from . import props_hb_face_frame as props
    ff = props.get_style_props()
    if ff is None:
        return
    idx = ff.active_cabinet_style_index
    if not (0 <= idx < len(ff.cabinet_styles)):
        return
    cs = ff.cabinet_styles[idx]
    finish_mat, finish_mat_rotated = cs.get_finish_material()
    if finish_mat is None:
        return
    for child in product_obj.children_recursive:
        if child.type != 'MESH':
            continue
        # _set_part_surfaces wraps the obj as a GeoNodeCutpart and plugs the
        # Top/Bottom Surface + edge inputs; it silently no-ops on any object
        # that isn't a cutpart, so the MESH guard is enough.
        cs._set_part_surfaces(child, finish_mat, finish_mat_rotated)
    product_obj['STYLE_NAME'] = cs.name


def position_door_part_pull(door_obj):
    """Create or reposition a scene-settings door pull on a Door Part.

    Mirrors _create_pull_for_front's DOOR / BASE / left-hinged branch but
    reads the part's own GeoNode dims (not a cabinet leaf) so it works
    standalone. The pull is parented to the door in front-local space
    (X = Length up, -Y = Width across, +Z = front face). Reused on resize
    so the pull tracks the door. Returns the pull Object or None."""
    scene_props = bpy.context.scene.hb_face_frame
    existing = next((c for c in door_obj.children if c.get('IS_CABINET_PULL')), None)

    # Per-door toggles stored as ID props (default on / left-hinged):
    # DOOR_PART_SHOW_PULL and DOOR_PART_PULL_SIDE ('LEFT' / 'RIGHT'),
    # driven by the right-click menu. Pull hidden -> drop any existing
    # instance and bail.
    if not door_obj.get('DOOR_PART_SHOW_PULL', True):
        if existing is not None:
            bpy.data.objects.remove(existing, do_unlink=True)
        return None
    # Front kind ('DOOR' default / 'DRAWER') picks the pull asset +
    # placement convention. A DRAWER front borrows the drawer-pull asset
    # and the in-cabinet drawer formula (horizontal bar, centered).
    front_kind = door_obj.get('DOOR_PART_FRONT_KIND', 'DOOR')
    pull_kind = 'drawer' if front_kind == 'DRAWER' else 'door'
    pull_obj = pulls.resolve_pull_object(scene_props, pull_kind)
    if pull_obj is None:
        if existing is not None:
            bpy.data.objects.remove(existing, do_unlink=True)
        return None
    part = GeoNodeCutpart(door_obj)
    length = part.get_input('Length')      # front height
    width = part.get_input('Width')        # front width
    thickness = part.get_input('Thickness')
    half = pulls.pull_length(pull_obj) / 2.0
    z = thickness                                                 # front face

    if pull_kind == 'drawer':
        # Drawer convention: horizontal bar centered across the width;
        # vertically centered or near the top per center_pulls_on_drawer_
        # front. Mirrors _create_pull_for_front's drawer branch (rot_z=90
        # runs the bar horizontal). PULL_SIDE is ignored (centered).
        if scene_props.center_pulls_on_drawer_front:
            x = length / 2.0
        else:
            x = length - scene_props.pull_vertical_location_base - half
        y = -width / 2.0
        rot = (math.radians(-90.0), 0.0, math.radians(90.0))
    else:
        # Door convention: vertical bar near the top, on the edge opposite
        # the hinge (DOOR_PART_PULL_SIDE).
        x = length - scene_props.pull_vertical_location_base - half
        if door_obj.get('DOOR_PART_PULL_SIDE', 'LEFT') == 'RIGHT':
            y = -scene_props.pull_horizontal_offset
        else:
            y = -(width - scene_props.pull_horizontal_offset)
        rot = (math.radians(-90.0), 0.0, 0.0)

    if existing is not None:
        inst = existing
        if inst.data is not pull_obj.data:
            inst.data = pull_obj.data
    else:
        inst = bpy.data.objects.new(f"Pull - {door_obj.name}", pull_obj.data)
        bpy.context.scene.collection.objects.link(inst)
        inst.parent = door_obj
        inst['hb_part_role'] = 'PULL'
        inst['IS_CABINET_PULL'] = True
    inst.location = (x, y, z)
    inst.rotation_euler = rot
    return inst


class DoorPart(CabinetPart):
    """A standalone door: the same bare GeoNodeCutpart as a Misc Part, but
    carrying a door style + pull.

    It is a DOOR-role front (so Face_Frame_Door_Style.assign_style_to_front
    renders it slab / 5-piece) plus a scene-settings pull, with NO cabinet
    cage / opening. On create it picks up the project's ACTIVE cabinet
    style's door style and the scene's current pull settings; both are
    re-applicable from the right-click menu. Rides the place_cabinet modal
    like the Misc Part; _finalize composes placement_stand_rotation so the
    door stands vertical wherever it lands. The 'Length' input is the door
    HEIGHT and 'Width' the door WIDTH (assign_style_to_front's convention).
    """
    single_placement = True
    default_cabinet_type = 'BASE'
    placement_stand_rotation = _DOOR_PART_STAND

    def __init__(self):
        super().__init__()
        # Preview cage: Dim X = width, Dim Y = depth (door thickness),
        # Dim Z = height -> a thin tall slab that reads as a door.
        self.default_width = inch(18.0)
        self.default_depth = inch(0.75)
        self.default_height = inch(30.0)

    def apply_placement_width(self, width):
        """The cage width is the door's WIDTH = its 'Width' input (its
        'Length' input is the door HEIGHT - see assign_style_to_front)."""
        self.set_input('Width', width)

    def create(self, name="Door", bay_qty=1):
        # bay_qty accepted but ignored. CabinetPart.create lays the cutpart;
        # we set it up as a DOOR front, stand it up, then apply the active
        # door style + a scene pull.
        super().create(name)
        self.obj['IS_FACE_FRAME_DOOR_PART'] = True
        self.obj['hb_part_role'] = PART_ROLE_DOOR
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_door_part_commands'
        self.set_input('Length', self.default_height)    # door height
        self.set_input('Width', self.default_width)      # door width
        self.set_input('Thickness', self.default_depth)  # door thickness
        self.set_input('Mirror Y', True)
        self.obj['Finish Top'] = True
        self.obj['Finish Bottom'] = True
        # Stand vertical for direct creation; _finalize re-composes this
        # onto the placement transform when placed via the modal.
        self.obj.matrix_basis = self.obj.matrix_basis @ _DOOR_PART_STAND
        apply_active_door_style_to_part(self.obj)
        position_door_part_pull(self.obj)


class HalfWallFaceFrameProduct(_FramelessHalfWall):
    """Half wall (pony / knee wall) for the Face Frame catalog's Misc
    section. Migrated by REUSING the frameless HalfWall geometry verbatim
    (studs + skins + finished end caps) - the face frame library already
    depends on the frameless part primitives (see the CabinetPart import
    above), so this thin subclass only routes the product through the face
    frame placement modal.

    It is NOT a face frame cabinet (no bays / openings / face frame), so it
    rides place_cabinet's bare-product branch in _finalize - the same path
    Misc Part / Door use. The frameless IS_FRAMELESS_PRODUCT_CAGE tag and
    PART_TYPE='HALF_WALL' set by the inherited create() are deliberately
    KEPT: the existing frameless right-click prompts (stud spacing, end
    caps, size) and delete key off those, so editing works unchanged.
    """
    single_placement = True          # one fixed-size piece, like Misc Part
    placement_stand_rotation = None  # built standing (Dim Z = height); no reorient

    def __init__(self):
        super().__init__()
        # Feed the placement modal's preview cage. The frameless HalfWall
        # seeds width / height / depth as instance attrs in its __init__;
        # mirror them onto the default_* names the face frame modal reads.
        self.default_width = self.width
        self.default_height = self.height
        self.default_depth = self.depth

    def create(self, name="Half Wall", bay_qty=1):
        # bay_qty is accepted (place_cabinet._finalize always passes it) but
        # ignored - a half wall has no bays. The inherited create builds the
        # full stud / skin geometry and tags the product cage.
        super().create(name)
        # Mark it a face-frame product cage so the Cabinets selection mode
        # shows its cage + makes it the selection target (see TAG_PRODUCT_CAGE
        # and hb_face_frame_OT_toggle_mode). NOT a cabinet cage by design.
        self.obj[TAG_PRODUCT_CAGE] = True
        # Pick up the project's active face-frame cabinet style's finish
        # material (the frameless geometry otherwise carries no face-frame
        # finish). Stamps STYLE_NAME so the source style is recorded.
        apply_active_finish_to_product(self.obj)

    def apply_placement_width(self, width):
        """The cage width maps to the product's X span = its 'Dim X' input
        (the studs / skins / top / bottom are all driver-bound to Dim X)."""
        self.set_input('Dim X', width)


class SupportFrameFaceFrameProduct(_FramelessSupportFrame):
    """Support frame (open rectangular frame + corner legs) for the Face
    Frame catalog's Misc section. Same migration shape as the Half Wall:
    REUSE the frameless SupportFrame geometry verbatim and add only the
    face frame placement + integration hooks.

    Not a face frame cabinet (no bays / openings), so it rides
    place_cabinet's bare-product branch in _finalize. The frameless
    IS_FRAMELESS_PRODUCT_CAGE tag + PART_TYPE='SUPPORT_FRAME' set by the
    inherited create() are KEPT so the existing frameless right-click
    prompts (support spacing, per-corner legs + types, leg sizes) and
    delete operate on it unchanged. TAG_PRODUCT_CAGE is added so it shows
    its cage / is the selection target in Cabinets selection mode, and the
    active style's finish material is applied to its parts.
    """
    single_placement = True          # one fixed-size piece, like the Half Wall
    placement_stand_rotation = None  # built in real orientation; no reorient

    def __init__(self):
        super().__init__()
        # Feed the placement modal's preview cage. The frameless SupportFrame
        # seeds width / height / depth in its __init__; mirror them onto the
        # default_* names the face frame modal reads.
        self.default_width = self.width
        self.default_height = self.height
        self.default_depth = self.depth

    def create(self, name="Support Frame", bay_qty=1):
        # bay_qty accepted (the modal always passes it) but ignored. The
        # inherited create builds the full frame + legs and tags the cage.
        super().create(name)
        # Face frame product cage -> shows in Cabinets selection mode.
        self.obj[TAG_PRODUCT_CAGE] = True
        # Active cabinet style's finish material (+ STYLE_NAME stamp).
        apply_active_finish_to_product(self.obj)

    def apply_placement_width(self, width):
        """The cage width maps to the product's X span = its 'Dim X' input
        (panels / supports / legs are all driver-bound to Dim X)."""
        self.set_input('Dim X', width)


CABINET_NAME_DISPATCH = {
    "Base Door": BaseFaceFrameCabinet,
    "Base Door Drw": BaseFaceFrameCabinet,
    "Base Drawer": BaseFaceFrameCabinet,
    "Floating Base Cabinet": FloatingBaseFaceFrameCabinet,
    "5 Drawer Dresser": FiveDrawerDresserCabinet,
    "6 Drawer Dresser": SixDrawerDresserCabinet,
    "Night Stand": NightStandFaceFrameCabinet,
    "3 Drawer Night Stand": ThreeDrawerNightStandCabinet,
    "Window Seat": WindowSeatFaceFrameCabinet,
    "Sink": SinkFaceFrameCabinet,
    "Lap Drawer": LapDrawerFaceFrameCabinet,
    "Upper": UpperFaceFrameCabinet,
    "Upper Stacked": UpperFaceFrameCabinet,
    "Bookcase Upper": BookcaseUpperFaceFrameCabinet,
    "Hutch Upper": HutchUpperFaceFrameCabinet,
    "Standard Recessed Medicine Cabinet": StandardRecessedMedicineCabinet,
    "Medicine Cabinet": MedicineCabinetFaceFrameCabinet,
    "Overstool Cabinet": OverstoolCabinetFaceFrameCabinet,
    "Mirror Frame": MirrorFrameFaceFrameCabinet,
    "Tri-View Medicine Cabinet": TriViewMedicineCabinetFaceFrameCabinet,
    "Tub Skirt": TubSkirtFaceFrameCabinet,
    "Tall": TallFaceFrameCabinet,
    "Tall Stacked": TallFaceFrameCabinet,
    "Refrigerator Cabinet": RefrigeratorCabinet,
    "Built in Tall": BuiltInTallFaceFrameCabinet,
    "Panel": PanelFaceFrameCabinet,
    "Face Frame and Doors": FaceFrameAndDoorsCabinet,
    "Bookcase": BookcaseFaceFrameCabinet,
    "Bookcase Storage Unit": BookcaseStorageUnitFaceFrameCabinet,
    "Leg Product": LegProductFaceFrameCabinet,
    "Floating Shelves": FloatingShelfFaceFrameCabinet,
    "Valance": ValanceFaceFrameProduct,
    "Misc Part": MiscPart,
    "Door": DoorPart,
    "Half Wall": HalfWallFaceFrameProduct,
    "Support Frame": SupportFrameFaceFrameProduct,
}


# Catalog names in the Appliance Products section map to classes in
# the shared common.types_appliances module. These produce a wireframe
# cage with a text label and no carcass / bays / face frame; the
# draw_cabinet operator drops them at the 3D cursor rather than
# routing through the cabinet placement modal.
APPLIANCE_NAME_DISPATCH = {
    "Dishwasher": types_appliances.Dishwasher,
    "Range": types_appliances.Range,
    "Range Hood": types_appliances.Hood,
    "Standalone Refrigerator": types_appliances.Refrigerator,
}


def get_cabinet_class(cabinet_name):
    """Return the FaceFrameCabinet subclass for the given library name."""
    if cabinet_name in CABINET_NAME_DISPATCH:
        return CABINET_NAME_DISPATCH[cabinet_name]
    if not cabinet_name:
        return None
    if 'Upper' in cabinet_name:
        return UpperFaceFrameCabinet
    if 'Tall' in cabinet_name or 'Refrigerator Cabinet' in cabinet_name:
        return TallFaceFrameCabinet
    return BaseFaceFrameCabinet


def find_cabinet_root(obj):
    """Walk up parents from obj to find the face frame cabinet root.

    Returns the cage Object (the one with IS_FACE_FRAME_CABINET_CAGE) or
    None if obj is not part of a face frame cabinet.
    """
    if obj is None:
        return None
    cur = obj
    while cur is not None:
        if cur.get(TAG_CABINET_CAGE):
            return cur
        cur = cur.parent
    return None


def default_front_type_for_root(root):
    """Default front_type for a freshly created opening under `root`.

    Panels default to INSET_PANEL so a new panel reads as a paneled
    door out of the box - the user can change individual openings
    afterward via the Change Opening menu or the Selection sub-panel.
    Cabinets stay NONE (open shelving) and let the user pick.
    """
    if root is None:
        return 'NONE'
    # A product class can override the default via default_opening_front_type
    # (e.g. FF & Doors defaults its openings to DOOR). Resolve the wrapper
    # class by CLASS_NAME the same way recalc does.
    cls = WRAP_CLASS_REGISTRY.get(root.get('CLASS_NAME'), FaceFrameCabinet)
    override = getattr(cls, 'default_opening_front_type', None)
    if override:
        return override
    if root.face_frame_cabinet.cabinet_type == 'PANEL':
        return 'INSET_PANEL'
    return 'NONE'


def applied_panel_geometry(layout, side):
    """Transform + dimensions for an applied panel covering one side of
    a cabinet. Returns (location, rotation_z, width, height, depth).

    Cabinet conventions: X=0 is the left exterior face, X=dim_x is the
    right exterior face; Y=0 is the back, Y=-dim_y is the front; Z=0
    is the floor, Z=dim_z is the cabinet top.

    LEFT and RIGHT panels sit in the scribe gap between the cabinet's
    exterior face and the side panel's outer face. The panel's outer
    (visible) face is flush with the face frame's outer face; its inner
    face touches the side panel. Z range is the FULL cabinet height -
    floor to cabinet top - so the panel covers the toe-kick band at
    the bottom and ignores top_scribe at the top. The panel's bottom
    rail width grows by toe_kick_height (handled in
    applied_panel_sizing) to keep that bottom band reading as frame
    rather than opening.

    BACK uses simple full-extent positioning for now; refining is
    deferred until applied-back behavior is settled.

    The standalone panel's local axes are: +X = width, +Y points INTO
    the panel (back face Y=0, front Y=-depth), +Z = up. Each side's
    rotation around Z aims the front face outward from the cabinet.
    """
    if side == 'LEFT':
        scribe = solver.left_scribe_offset(layout)
        # Rz(-pi/2): panel +X -> cabinet -Y, panel +Y -> cabinet +X.
        # Origin x = scribe (panel back face touches side outer face);
        # panel front face lands at cabinet x = 0 (flush with FF outer
        # face) when depth = scribe.
        location = (scribe, 0.0, 0.0)
        rotation_z = -math.pi / 2.0
        width = layout.dim_y - layout.fft
        height = layout.dim_z
        return (location, rotation_z, width, height, scribe)
    if side == 'RIGHT':
        scribe = solver.right_scribe_offset(layout)
        # Rz(+pi/2): panel +X -> cabinet +Y, panel +Y -> cabinet -X.
        # Origin x = dim_x - scribe; front face lands at dim_x (flush
        # with FF outer face) when depth = scribe.
        location = (layout.dim_x - scribe,
                    -layout.dim_y + layout.fft, 0.0)
        rotation_z = math.pi / 2.0
        width = layout.dim_y - layout.fft
        height = layout.dim_z
        return (location, rotation_z, width, height, scribe)
    # BACK: rotate +pi around Z. Front face -> +Y. Origin at
    # back-right-bottom; width spans cabinet x from dim_x down to 0.
    # Full cabinet height for now - refine when applied-back behavior
    # is settled.
    return ((layout.dim_x, 0.0, 0.0), math.pi,
            layout.dim_x, layout.dim_z, inch(0.75))


# Registry of CLASS_NAME -> FaceFrameCabinet subclass for _wrap_cabinet.
# Modules that introduce new cabinet subclasses (e.g. corner cabinets)
# register their classes into this dict at import time so the prop
# update callback dispatches to the right recalculate() override.
WRAP_CLASS_REGISTRY = {}


def _wrap_cabinet(obj):
    """Wrap a cabinet root Object as the appropriate FaceFrameCabinet subclass."""
    class_name = obj.get('CLASS_NAME', 'FaceFrameCabinet')
    cls = WRAP_CLASS_REGISTRY.get(class_name, FaceFrameCabinet)
    instance = cls.__new__(cls)
    GeoNodeCage.__init__(instance, obj)
    return instance


WRAP_CLASS_REGISTRY.update({
    'BaseFaceFrameCabinet': BaseFaceFrameCabinet,
    'FloatingBaseFaceFrameCabinet': FloatingBaseFaceFrameCabinet,
    'SinkFaceFrameCabinet': SinkFaceFrameCabinet,
    'UpperFaceFrameCabinet': UpperFaceFrameCabinet,
    'TallFaceFrameCabinet': TallFaceFrameCabinet,
    'RefrigeratorCabinet': RefrigeratorCabinet,
    'BuiltInTallFaceFrameCabinet': BuiltInTallFaceFrameCabinet,
    'BookcaseFaceFrameCabinet': BookcaseFaceFrameCabinet,
    'LapDrawerFaceFrameCabinet': LapDrawerFaceFrameCabinet,
    'PanelFaceFrameCabinet': PanelFaceFrameCabinet,
    'FaceFrameAndDoorsCabinet': FaceFrameAndDoorsCabinet,
    'LegProductFaceFrameCabinet': LegProductFaceFrameCabinet,
    'FloatingShelfFaceFrameCabinet': FloatingShelfFaceFrameCabinet,
    'ValanceFaceFrameProduct': ValanceFaceFrameProduct,
})


# Specialty Bath leaf classes. _wrap_cabinet() (run on every recalc) falls back
# to the base FaceFrameCabinet for any CLASS_NAME not registered here, and the
# base reports _has_carcass() == True - so an unregistered PANEL-derived class
# (Mirror Frame) wrongly rebuilds carcass / blind / top / bottom parts at
# recalc. Registering it makes recalc wrap it as a Panel (no carcass). The
# upper-derived bath products wrap to a carcass either way (and resolve
# _has_toe_kick to Upper's False == the base-wrap value), so listing them here
# is behavior-neutral - it just makes recalc use their real class.
WRAP_CLASS_REGISTRY.update({
    'StandardRecessedMedicineCabinet': StandardRecessedMedicineCabinet,
    'MedicineCabinetFaceFrameCabinet': MedicineCabinetFaceFrameCabinet,
    'OverstoolCabinetFaceFrameCabinet': OverstoolCabinetFaceFrameCabinet,
    'MirrorFrameFaceFrameCabinet': MirrorFrameFaceFrameCabinet,
    'TubSkirtFaceFrameCabinet': TubSkirtFaceFrameCabinet,
    'TriViewMedicineCabinetFaceFrameCabinet': TriViewMedicineCabinetFaceFrameCabinet,
})


def _remove_root_with_children(root_obj):
    """Delete a cabinet/panel root and every descendant. Iterates the
    descendant list in reverse so deeper objects unparent before their
    ancestors, avoiding "StructRNA has been removed" errors when a
    later iteration would try to read a freed Object.
    """
    for desc in reversed(list(root_obj.children_recursive)):
        if desc.name in bpy.data.objects:
            bpy.data.objects.remove(desc, do_unlink=True)
    bpy.data.objects.remove(root_obj, do_unlink=True)


# Standalone panel products (placed from the library) that should get the
# applied-back-panel behaviour: auto face frame sizes, the mid-stile width
# ladder, and auto openings. Applied panels are PanelFaceFrameCabinet too but
# carry TAG_APPLIED_PANEL_SIDE and are reconciled by their host, so excluded.
PANEL_PRODUCT_CLASS_NAMES = frozenset({
    'PanelFaceFrameCabinet', 'FaceFrameAndDoorsCabinet',
})


def _is_standalone_panel(root):
    return (root is not None
            and root.get('CLASS_NAME') in PANEL_PRODUCT_CLASS_NAMES
            and not root.get(TAG_APPLIED_PANEL_SIDE))


# Guard so the bay insert/delete inside the standalone-panel reconcile (each of
# which recalcs the panel) doesn't recurse back into the reconcile.
_RECONCILING_STANDALONE = set()


def _reconcile_standalone_panel(root):
    """Give a standalone Panel the same treatment an applied back panel gets:
    auto face frame sizes, the mid-stile width ladder, and auto openings - with
    the panel acting as its own host. Runs OUTSIDE the recalc reentrance guard
    (so the bay insert/delete it performs can recalc the panel) but under its
    own guard (so that recalc doesn't recurse here)."""
    if id(root) in _RECONCILING_STANDALONE:
        return
    if not _is_standalone_panel(root):
        return
    _RECONCILING_STANDALONE.add(id(root))
    try:
        from . import applied_panel_sizing as aps
        # NOTE: do NOT call apply_panel_sizing here. Its 5-piece path
        # reconstructs the rail as `cab.top_rail_width - overlay + door_rail`,
        # reading and writing the SAME field when the panel is its own host -
        # so the rail grows without bound every recalc. A standalone panel
        # keeps its own style-driven face-frame widths; only the split
        # structure (ladder + auto openings + mid-stile widths) is applied.
        aps.apply_panel_split_structure(root, root, 'BACK')
        # Surface the panel's properties from any of its parts: stamp the
        # part-commands menu onto menu-less parts (inset panels / pivots).
        for part in root.children_recursive:
            if part.get('hb_part_role') and not part.get('MENU_ID'):
                part['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
    finally:
        _RECONCILING_STANDALONE.discard(id(root))


def recalculate_face_frame_cabinet(obj):
    """Push current property values to all carcass parts. Safe entry point
    for property update callbacks. Walks up to find the cabinet root if obj
    is a child or descendant.

    Guarded against reentrance: if a recalc is already in progress for this
    cabinet (because a bay/cabinet prop write inside recalculate fired its
    update callback), this call exits immediately. The outer recalc will
    pick up the new value when it reads from props.

    Also honors suspend_recalc(): when active, the request is queued by name
    and drained once at the outermost resume.
    """
    root = find_cabinet_root(obj)
    if root is None:
        return
    if _RECALC_SUSPEND_DEPTH > 0:
        _PENDING_RECALC_NAMES.add(root.name)
        return
    if id(root) in _RECALCULATING:
        return
    _RECALCULATING.add(id(root))
    try:
        cabinet = _wrap_cabinet(root)
        cabinet.recalculate()
        _reapply_cabinet_style(root)
        _reapply_selection_mode_highlights(root)
    finally:
        _RECALCULATING.discard(id(root))

    # Standalone panels get the applied-back behaviour after the core
    # recalc (own guard prevents recursion via its bay insert/delete).
    _reconcile_standalone_panel(root)


def _reapply_selection_mode_highlights(root):
    """Re-apply face frame selection mode highlight to root and all its
    descendants. Called at the end of every recalc so newly created
    parts pick up the highlight without forcing the user to toggle the
    mode off and on.

    Mirrors HB_FACE_FRAME_OT_toggle_mode's per-object dispatch but does
    NOT clear scene selection - recalc fires from prop update callbacks
    during live-bound popup edits, not from an explicit user action, so
    messing with selection would close popups and break drag flow.
    """
    # Lazy import: toggle_cabinet_color lives in a sibling product library
    # and pulling it at module top would couple type-level recalc to the
    # frameless package import order during addon load.
    from ..frameless.operators.ops_placement import toggle_cabinet_color

    scene_props = getattr(bpy.context.scene, 'hb_face_frame', None)
    if scene_props is None:
        return

    mode = scene_props.face_frame_selection_mode
    # Master toggle off and Parts mode both route through the "not
    # highlighted" path - matches the operator's behavior at execute().
    if not scene_props.face_frame_selection_mode_enabled or mode == 'Parts':
        mode = '__off__'

    # Same tag dict as HB_FACE_FRAME_OT_toggle_mode.MODE_TAGS. Kept in
    # sync by convention; if the operator's MODE_TAGS gain entries, add
    # them here too.
    mode_tags = {
        'Cabinets':       TAG_CABINET_CAGE,
        'Bays':           TAG_BAY_CAGE,
        'Openings':       'IS_FACE_FRAME_OPENING_CAGE',
        'Interiors':      'IS_FACE_FRAME_INTERIOR_PART',
        'Applied Panels': TAG_APPLIED_PANEL_SIDE,
    }

    skip_markers = ('IS_WALL_BP', 'IS_ENTRY_DOOR_BP',
                    'IS_WINDOW_BP', 'IS_CUTTING_OBJ')

    def matches(obj):
        if mode == 'Face Frame':
            return obj.get('hb_part_role') in FACE_FRAME_PART_ROLES
        if mode == 'Cabinets':
            if obj.get('IS_APPLIANCE'):
                return True
            if obj.get(TAG_APPLIED_PANEL_SIDE):
                return False
        tag = mode_tags.get(mode)
        if tag is None:
            return False
        return tag in obj

    def apply(obj):
        if any(t in obj for t in skip_markers):
            return
        if matches(obj):
            toggle_cabinet_color(
                obj, True,
                type_name=mode_tags.get(mode, ''),
                dont_show_parent=False,
            )
            # Unlocked (overridden) parts read a distinct colour so the
            # user can see what they've changed from default. Same rule as
            # the toggle_mode operator; this path runs after every recalc.
            if mode == 'Face Frame' and part_width_is_unlocked(obj):
                obj.color = FACE_FRAME_UNLOCKED_COLOR
        else:
            toggle_cabinet_color(
                obj, False,
                type_name=mode_tags.get(mode, ''),
            )

    apply(root)
    for child in root.children_recursive:
        apply(child)


def _reapply_cabinet_style(root):
    """Re-attach door / drawer-front styles AND materials to a cabinet's
    parts after a recalc. The face frame solver wipes and rebuilds all
    bays, carcass parts, and fronts on every recalc, so per-part
    material slots and the per-front CPM_5PIECEDOOR modifier vanish
    each cycle. STYLE_NAME on the cabinet root survives (it lives on
    the root, not on parts), so we look up the cabinet style and re-
    run both walks. No-op if the cabinet has no STYLE_NAME or the
    named style is missing from the scene's collection.

    Order matters: door styles add the 5-piece modifier (which has its
    own material slots), and the material walk then wires those slots
    along with the cutpart surface inputs.
    """
    style_name = root.get('STYLE_NAME')
    if not style_name:
        return
    from .props_hb_face_frame import get_style_props
    ff = get_style_props()
    for cs in ff.cabinet_styles:
        if cs.name == style_name:
            cs._apply_door_styles_to_fronts(root)
            cs._apply_materials_to_cabinet(root)
            # FF sizes intentionally NOT re-applied here - widths are
            # cabinet props the user can edit between recalcs; pushing
            # them every recalc would clobber per-cabinet adjustments.
            # The Assign Style op runs the push explicitly.
            return


# ---------------------------------------------------------------------------
# Cabinet merge
# ---------------------------------------------------------------------------

_SIDE_PROP_NAMES_LEFT = (
    'left_finished_end_condition', 'left_exposure',
    'left_dishwasher_adjacent', 'left_finish_end_auto', 'left_scribe',
    'left_flush_x_amount', 'blind_left', 'blind_amount_left',
    'extend_left', 'left_offset', 'inset_toe_kick_left',
    'left_stile_width', 'left_stile_type', 'unlock_left_stile',
    'turn_off_left_stile', 'extend_left_stile_to_floor',
    'extend_left_stile_up', 'extend_left_stile_down',
    'extend_left_stile_up_amount', 'extend_left_stile_down_amount',
    'left_depth', 'unlock_left_depth',
)
_SIDE_PROP_NAMES_RIGHT = (
    'right_finished_end_condition', 'right_exposure',
    'right_dishwasher_adjacent', 'right_finish_end_auto', 'right_scribe',
    'right_flush_x_amount', 'blind_right', 'blind_amount_right',
    'extend_right', 'right_offset', 'inset_toe_kick_right',
    'right_stile_width', 'right_stile_type', 'unlock_right_stile',
    'turn_off_right_stile', 'extend_right_stile_to_floor',
    'extend_right_stile_up', 'extend_right_stile_down',
    'extend_right_stile_up_amount', 'extend_right_stile_down_amount',
    'right_depth', 'unlock_right_depth',
)


def _side_prop_names(side):
    return _SIDE_PROP_NAMES_RIGHT if side == 'RIGHT' else _SIDE_PROP_NAMES_LEFT


def _capture_side_props(props, side):
    """Snapshot all side-specific cabinet props for the given side."""
    return {name: getattr(props, name) for name in _side_prop_names(side)}


def _apply_side_props(props, side, captured):
    """Write a captured side-prop snapshot onto props. The dict's keys
    are expected to match the prop names for that side."""
    for name in _side_prop_names(side):
        if name in captured:
            setattr(props, name, captured[name])


def _default_side_props(side, stile_width, depth):
    """Return a dict of side-specific cabinet prop values representing
    a freshly-exterior side - what a new cabinet edge looks like at
    creation time. Used during break to reset both halves' new
    boundary edges to a clean default state.
    """
    pre = 'right_' if side == 'RIGHT' else 'left_'
    suf = '_right' if side == 'RIGHT' else '_left'
    return {
        f'{pre}finished_end_condition': 'UNFINISHED',
        f'{pre}exposed': True,
        f'{pre}scribe': 0.0,
        f'{pre}flush_x_amount': inch(4.0),
        f'blind{suf}': False,
        f'blind_amount{suf}': inch(24.0),
        f'extend{suf}': 0.0,
        f'{pre}offset': 0.0,
        f'inset_toe_kick{suf}': 0.0,
        f'{pre}stile_width': stile_width,
        f'{pre}stile_type': 'STANDARD',
        f'unlock_{pre}stile': False,
        f'turn_off_{pre}stile': False,
        f'extend_{pre}stile_to_floor': False,
        f'extend_{pre}stile_up': False,
        f'extend_{pre}stile_down': False,
        f'extend_{pre}stile_up_amount': 0.0,
        f'extend_{pre}stile_down_amount': 0.0,
        f'{pre}depth': depth,
        f'unlock_{pre}depth': False,
    }


def _propagate_far_side_props(absorbed_props, anchor_props, side):
    """When `absorbed` is merged onto `anchor` on the given `side`,
    `absorbed`'s far-side exterior props (the side opposite the merge
    boundary) become `anchor`'s same-side exterior props. The anchor's
    OTHER side stays untouched. The merge boundary itself - what was
    anchor's <side> exterior and absorbed's <opposite> exterior - just
    disappears (becomes interior bay structure), so neither gets read
    after the merge.
    """
    if side == 'RIGHT':
        anchor_props.right_finished_end_condition = absorbed_props.right_finished_end_condition
        anchor_props.right_exposure             = absorbed_props.right_exposure
        anchor_props.right_dishwasher_adjacent  = absorbed_props.right_dishwasher_adjacent
        anchor_props.right_finish_end_auto      = absorbed_props.right_finish_end_auto
        anchor_props.right_scribe                 = absorbed_props.right_scribe
        anchor_props.right_flush_x_amount         = absorbed_props.right_flush_x_amount
        anchor_props.blind_right                  = absorbed_props.blind_right
        anchor_props.blind_amount_right           = absorbed_props.blind_amount_right
        anchor_props.extend_right                 = absorbed_props.extend_right
        anchor_props.right_offset                 = absorbed_props.right_offset
        anchor_props.inset_toe_kick_right         = absorbed_props.inset_toe_kick_right
        anchor_props.right_stile_width            = absorbed_props.right_stile_width
        anchor_props.right_stile_type             = absorbed_props.right_stile_type
        anchor_props.unlock_right_stile           = absorbed_props.unlock_right_stile
        anchor_props.turn_off_right_stile         = absorbed_props.turn_off_right_stile
        anchor_props.extend_right_stile_to_floor  = absorbed_props.extend_right_stile_to_floor
        anchor_props.extend_right_stile_up        = absorbed_props.extend_right_stile_up
        anchor_props.extend_right_stile_down      = absorbed_props.extend_right_stile_down
        anchor_props.extend_right_stile_up_amount   = absorbed_props.extend_right_stile_up_amount
        anchor_props.extend_right_stile_down_amount = absorbed_props.extend_right_stile_down_amount
        # Per-side depth / unlock - pre-flight requires square cabinets so
        # these are defensive copies (would matter only if angled-cabinet
        # merge support is added later).
        anchor_props.right_depth                  = absorbed_props.right_depth
        anchor_props.unlock_right_depth           = absorbed_props.unlock_right_depth
    else:  # LEFT
        anchor_props.left_finished_end_condition = absorbed_props.left_finished_end_condition
        anchor_props.left_exposure              = absorbed_props.left_exposure
        anchor_props.left_dishwasher_adjacent   = absorbed_props.left_dishwasher_adjacent
        anchor_props.left_finish_end_auto       = absorbed_props.left_finish_end_auto
        anchor_props.left_scribe                 = absorbed_props.left_scribe
        anchor_props.left_flush_x_amount         = absorbed_props.left_flush_x_amount
        anchor_props.blind_left                  = absorbed_props.blind_left
        anchor_props.blind_amount_left           = absorbed_props.blind_amount_left
        anchor_props.extend_left                 = absorbed_props.extend_left
        anchor_props.left_offset                 = absorbed_props.left_offset
        anchor_props.inset_toe_kick_left         = absorbed_props.inset_toe_kick_left
        anchor_props.left_stile_width            = absorbed_props.left_stile_width
        anchor_props.left_stile_type             = absorbed_props.left_stile_type
        anchor_props.unlock_left_stile           = absorbed_props.unlock_left_stile
        anchor_props.turn_off_left_stile         = absorbed_props.turn_off_left_stile
        anchor_props.extend_left_stile_to_floor  = absorbed_props.extend_left_stile_to_floor
        anchor_props.extend_left_stile_up        = absorbed_props.extend_left_stile_up
        anchor_props.extend_left_stile_down      = absorbed_props.extend_left_stile_down
        anchor_props.extend_left_stile_up_amount   = absorbed_props.extend_left_stile_up_amount
        anchor_props.extend_left_stile_down_amount = absorbed_props.extend_left_stile_down_amount
        anchor_props.left_depth                  = absorbed_props.left_depth
        anchor_props.unlock_left_depth           = absorbed_props.unlock_left_depth


def merge_cabinets(anchor, absorbed, side):
    """Merge `absorbed` cabinet into `anchor` on the given `side`
    ('LEFT' or 'RIGHT' relative to anchor).

    Reparents absorbed's bays under anchor (preserving opening cage
    object identity, which the solver matches by obj.name across
    recalcs), copies absorbed's far-side exterior props onto anchor's
    same-side exterior, deletes absorbed, then triggers a single recalc
    of anchor.

    Pre-flight requires matching height, depth, world Z, and parent;
    abutting within 1 inch in parent-local X; and both cabinets square
    (no corner / angled merge in this pass).

    Returns True on success, False on failed pre-flight.
    """
    if side not in ('LEFT', 'RIGHT'):
        return False
    if anchor is None or absorbed is None or anchor is absorbed:
        return False
    if not anchor.get(TAG_CABINET_CAGE) or not absorbed.get(TAG_CABINET_CAGE):
        return False

    a_props = anchor.face_frame_cabinet
    b_props = absorbed.face_frame_cabinet

    eps = 1e-4
    if abs(a_props.height - b_props.height) > eps:
        return False
    if abs(a_props.depth - b_props.depth) > eps:
        return False
    if abs(anchor.matrix_world.translation.z - absorbed.matrix_world.translation.z) > eps:
        return False
    if anchor.parent is not absorbed.parent:
        return False
    if a_props.corner_type != 'NONE' or b_props.corner_type != 'NONE':
        return False

    tolerance = inch(1.0)
    a_w = a_props.width
    b_w = b_props.width

    # Abutment is checked along the anchor's run direction, defined as
    # its local +X axis projected into the world XY plane. For wall-
    # parented cabinets both anchor and absorbed sit with no local Z
    # rotation, so the run axis equals the wall's length direction and
    # the projected gap collapses to (absorbed.location.x -
    # anchor.location.x) - same number the old code computed. For
    # island / off-wall placement the cabinets can sit at any Z
    # rotation; the projection handles both cases.
    a_run = anchor.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    a_run.z = 0.0
    b_run = absorbed.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    b_run.z = 0.0
    if a_run.length < 1e-8 or b_run.length < 1e-8:
        return False
    a_run.normalize()
    b_run.normalize()
    # Cabinets in the same run must share orientation. Half-degree
    # tolerance keeps two parallel island runs offset depth-wise from
    # ever being treated as a single run.
    if a_run.dot(b_run) < math.cos(math.radians(0.5)):
        return False

    disp = absorbed.matrix_world.translation - anchor.matrix_world.translation
    signed = disp.x * a_run.x + disp.y * a_run.y
    perp_x = disp.x - signed * a_run.x
    perp_y = disp.y - signed * a_run.y
    perp = math.sqrt(perp_x * perp_x + perp_y * perp_y)
    if perp > tolerance:
        return False
    if side == 'RIGHT':
        gap = signed - a_w
    else:
        gap = -signed - b_w
    if abs(gap) > tolerance:
        return False

    with suspend_recalc():
        anchor_bays = sorted(
            [c for c in anchor.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        absorbed_bays = sorted(
            [c for c in absorbed.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        M = len(anchor_bays)
        N = len(absorbed_bays)

        # Snapshot original unlock_width on every bay. After merge each
        # bay's lock state is one of: original (multi-bay source) or
        # forced-True (single-bay source - the sink / appliance case
        # where the bay must hold its captured width).
        original_unlock = {
            bay.name: bay.face_frame_bay.unlock_width
            for bay in (anchor_bays + absorbed_bays)
        }

        # Capture mid_stile_widths from both cabinets as plain data
        # before mutating anything. Boundary width is the sum of the
        # two end stiles meeting at the merge - the wood that was
        # anchor's right end stile + absorbed's left end stile becomes
        # the boundary mid stile, preserving bay positions exactly.
        # Captured BEFORE _propagate_far_side_props because propagation
        # overwrites anchor's end stile widths.
        def _snapshot_mids(props):
            return [(e.width, e.unlock, e.extend_up_amount, e.extend_down_amount)
                    for e in props.mid_stile_widths]
        anchor_mids = _snapshot_mids(a_props)
        absorbed_mids = _snapshot_mids(b_props)

        # Boundary mid stile uses the cabinet's default mid-stile
        # width (typically narrower than the two abutting end stiles).
        # Total cabinet width is held at (a_w + b_w); the bay
        # redistributor absorbs the saved-stile-width delta into
        # whichever bays remain unlocked at recalc time.
        boundary_width = a_props.bay_mid_stile_width
        boundary_gap_index = M - 1 if side == 'RIGHT' else N - 1

        # Capture mid-stile / mid-div parts. Absorbed's move to anchor
        # with new indices; anchor's existing parts shift only on LEFT
        # merges (when absorbed prepends).
        mid_part_roles = (PART_ROLE_MID_STILE, PART_ROLE_MID_DIVISION)
        anchor_mid_parts = [c for c in anchor.children
                            if c.get('hb_part_role') in mid_part_roles]
        absorbed_mid_parts = [c for c in absorbed.children
                              if c.get('hb_part_role') in mid_part_roles]

        # Reparent absorbed's bays under anchor.
        for bay in absorbed_bays:
            bay.parent = anchor
            bay.matrix_parent_inverse.identity()

        if side == 'RIGHT':
            final_bays = anchor_bays + absorbed_bays
        else:
            final_bays = absorbed_bays + anchor_bays
        for new_idx, bay in enumerate(final_bays):
            bay['hb_bay_index'] = new_idx
            bay.face_frame_bay.bay_index = new_idx

        # A single-bay source's bay gets force-locked when it merges
        # into a multi-bay cabinet - the lock keeps a sink / appliance
        # bay from being resized by the neighbor's redistribution.
        # Multi-bay sources always keep their original unlock_width so
        # their auto-calculated bays absorb the boundary-stile
        # consolidation delta at recalc time.
        #
        # When two single-bay cabinets merge, the anchor is the cabinet
        # already in place and holds its width; only the absorbed bay -
        # the one just placed - stays unlocked, so _distribute_bay_widths
        # grows it to fill the merged run (the two abutting end stiles
        # collapse to one narrower boundary mid stile, freeing width
        # that needs an unlocked bay to land in).
        anchor_was_single = (M == 1)
        absorbed_was_single = (N == 1)
        both_single = anchor_was_single and absorbed_was_single
        for bay in anchor_bays:
            bay.face_frame_bay.unlock_width = (
                True if anchor_was_single else original_unlock[bay.name]
            )
        for bay in absorbed_bays:
            if both_single:
                bay.face_frame_bay.unlock_width = False
            else:
                bay.face_frame_bay.unlock_width = (
                    True if absorbed_was_single else original_unlock[bay.name]
                )

        # Toe-kick construction reconciliation. toe_kick_type and
        # toe_kick_height are cabinet-level, so the merge - which keeps
        # the anchor's cabinet props and deletes absorbed - would render
        # absorbed's bays with the anchor's kick. Express any difference
        # per bay instead: a bay built FLOATING (lap drawer, floating
        # base) carries floating_bay so the solver lifts it regardless
        # of the merged cabinet type, and any bay whose recess differs
        # from the merged default is unlocked so _distribute_bay_kick_
        # heights leaves it alone (e.g. a 27\" lap-drawer lift would
        # otherwise snap to the anchor's 4\").
        a_tk, b_tk = a_props.toe_kick_type, b_props.toe_kick_type
        if a_tk != b_tk:
            # Grounded type wins as the cabinet-level default for
            # unflagged bays: NOTCH over FLUSH over FLOATING.
            if 'NOTCH' in (a_tk, b_tk):
                merged_tk = 'NOTCH'
            elif 'FLUSH' in (a_tk, b_tk):
                merged_tk = 'FLUSH'
            else:
                merged_tk = 'FLOATING'
            if merged_tk != 'FLOATING':
                if a_tk == 'FLOATING':
                    for bay in anchor_bays:
                        bay.face_frame_bay.floating_bay = True
                if b_tk == 'FLOATING':
                    for bay in absorbed_bays:
                        bay.face_frame_bay.floating_bay = True
            a_props.toe_kick_type = merged_tk

        # Bays seed kick_height from their origin cabinet's
        # toe_kick_height; after the merge the cabinet-level default is
        # the anchor's. Unlock any bay that differs so it holds its own
        # recess / lift rather than being resynced to that default.
        merged_kh = a_props.toe_kick_height
        for bay in final_bays:
            bp = bay.face_frame_bay
            if abs(bp.kick_height - merged_kh) > eps:
                bp.unlock_kick_height = True

        _propagate_far_side_props(b_props, a_props, side)

        # Reparent absorbed's mid parts under anchor with new indices.
        # Anchor's existing mid parts shift only on LEFT merges.
        if side == 'RIGHT':
            for part in absorbed_mid_parts:
                old_idx = part.get('hb_mid_stile_index', 0)
                part['hb_mid_stile_index'] = old_idx + M
                part.parent = anchor
                part.matrix_parent_inverse.identity()
        else:
            for part in anchor_mid_parts:
                old_idx = part.get('hb_mid_stile_index', 0)
                part['hb_mid_stile_index'] = old_idx + N
            for part in absorbed_mid_parts:
                part.parent = anchor
                part.matrix_parent_inverse.identity()

        # Build the boundary mid stile + slot-0 / slot-1 mid div pair.
        # _create_mid_parts_at parents to anchor and sets defaults; the
        # recalc positions and sizes everything from layout.
        _wrap_cabinet(anchor)._create_mid_parts_at(boundary_gap_index)

        # Rebuild anchor's mid_stile_widths in merged order.
        if side == 'RIGHT':
            merged_mids = (anchor_mids
                           + [(boundary_width, False, 0.0, 0.0)]
                           + absorbed_mids)
        else:
            merged_mids = (absorbed_mids
                           + [(boundary_width, False, 0.0, 0.0)]
                           + anchor_mids)
        a_props.mid_stile_widths.clear()
        for w, ulk, ext_up, ext_dn in merged_mids:
            entry = a_props.mid_stile_widths.add()
            entry.width = w
            entry.unlock = ulk
            entry.extend_up_amount = ext_up
            entry.extend_down_amount = ext_dn

        # LEFT merge: anchor's origin moves to absorbed's old location.
        # The merged cabinet then spans exactly the same range as the
        # two originals combined; the bay redistributor handles the
        # (anchor.right + absorbed.left - boundary_default) delta by
        # growing whichever bays are still unlocked. Shifting via the
        # rotation-applied run vector lets this work for island
        # placement at any orientation, while collapsing to a plain
        # location.x assignment when rotation_euler is zero.
        if side == 'LEFT':
            run_in_parent = (
                anchor.rotation_euler.to_matrix() @ Vector((1.0, 0.0, 0.0))
            )
            anchor.location -= b_w * run_in_parent

        # Total cabinet width preserved at sum of original widths.
        a_props.width = a_w + b_w

        # Bays and mid parts have been reparented; what's left under
        # absorbed is its carcass + end stiles + rails + pulls.
        _remove_root_with_children(absorbed)

    return True


def _resolve_style_overlay(root):
    """door_overlay_type of the cabinet's assigned style, or None."""
    style_name = root.get('STYLE_NAME')
    if not style_name:
        return None
    try:
        from .props_hb_face_frame import get_style_props
        ff = get_style_props()
        style = next((cs for cs in ff.cabinet_styles if cs.name == style_name), None)
        return style.door_overlay_type if style is not None else None
    except Exception:
        return None


def _resolve_style_stile_width(root, cab_props, row):
    """Style's ff_<row>_width_<col> for this cabinet (column from
    cabinet_type), or None if it can't be resolved. Lets the break op size
    new butt-stile edges from the assigned style."""
    style_name = root.get('STYLE_NAME')
    if not style_name:
        return None
    try:
        from .props_hb_face_frame import get_style_props
        ff = get_style_props()
        style = next((cs for cs in ff.cabinet_styles if cs.name == style_name), None)
        if style is None:
            return None
        col = style._CABINET_TYPE_COLUMN.get(cab_props.cabinet_type, 'base')
        return getattr(style, f"ff_{row}_width_{col}", None)
    except Exception:
        return None


def break_cabinet_at_gap(cabinet, gap_index, shrink_side='AUTO'):
    """Break `cabinet` into two cabinets at the gap between bays
    `gap_index` and `gap_index+1`. Returns the new (right-half)
    cabinet root, or None on invalid input.

    `shrink_side` directs which half absorbs the extra width the break
    creates (replacing the boundary mid stile with two butt end stiles
    widens the pair; see the width math below): 'AUTO' splits it between
    halves that have unlocked bays; 'LEFT' / 'RIGHT' force it onto one
    half (Break Both uses this so each outer cabinet absorbs exactly one
    boundary's worth and the outer halves come out equal). A forced side
    with no unlocked bays falls back to AUTO.

    The original keeps bays [0..gap_index]; the new cabinet receives
    bays [gap_index+1..end] reindexed from 0. The boundary mid stile
    + mid div pair is deleted. New end stiles at the break edge use
    the cabinet's bay_mid_stile_width default; side props on the
    break edges reset to default-exterior state. The original's
    far-side (right) props propagate onto the new cabinet's right
    side, since that's the new cabinet's exterior on that side.

    Caller sets unlock_width on bays it wants preserved before
    calling.
    """
    if cabinet is None or not cabinet.get(TAG_CABINET_CAGE):
        return None
    cab_props = cabinet.face_frame_cabinet
    if cab_props.corner_type != 'NONE':
        return None
    bays = sorted(
        [c for c in cabinet.children if c.get(TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if not (0 <= gap_index < len(bays) - 1):
        return None

    class_name = cabinet.get('CLASS_NAME', 'FaceFrameCabinet')
    cls = WRAP_CLASS_REGISTRY.get(class_name, FaceFrameCabinet)

    with suspend_recalc():
        captured_right = _capture_side_props(cab_props, 'RIGHT')
        mids_data = [(e.width, e.unlock, e.extend_up_amount, e.extend_down_amount)
                     for e in cab_props.mid_stile_widths]
        right_mids = mids_data[gap_index + 1:]

        mid_part_roles = (PART_ROLE_MID_STILE, PART_ROLE_MID_DIVISION)
        all_mid_parts = [c for c in cabinet.children
                         if c.get('hb_part_role') in mid_part_roles]
        boundary_parts = [p for p in all_mid_parts
                          if p.get('hb_mid_stile_index', 0) == gap_index]
        right_mid_parts = [p for p in all_mid_parts
                           if p.get('hb_mid_stile_index', 0) > gap_index]
        right_bays = bays[gap_index + 1:]
        # Break edges become an interior butt joint -> size them from the
        # style's butt-stile width (keeps the width-conservation math below
        # consistent); fall back to the mid-stile default if no style.
        butt_w = _resolve_style_stile_width(cabinet, cab_props, 'butt_stile')
        boundary_default = butt_w if butt_w else cab_props.bay_mid_stile_width

        # Create new cabinet (1 default bay; we replace it below)
        new_inst = cls()
        new_inst.create(cabinet.name.split('.')[0], bay_qty=1)
        new_root = new_inst.obj
        new_props = new_root.face_frame_cabinet

        # Carry over root-level custom prop tags. STYLE_NAME drives
        # _reapply_cabinet_style at recalc end (door style + materials);
        # without it, the new cabinet's fronts render slab.
        for key in ('STYLE_NAME',):
            val = cabinet.get(key)
            if val is not None:
                new_root[key] = val

        if cabinet.parent is not None:
            new_root.parent = cabinet.parent
            new_root.matrix_parent_inverse.identity()
        new_root.rotation_euler = cabinet.rotation_euler.copy()
        new_root.location.y = cabinet.location.y
        new_root.location.z = cabinet.location.z

        # Copy cabinet-wide (non-side) props from original to new
        for name in (
            'cabinet_type', 'height', 'depth',
            'is_sink', 'is_built_in_appliance', 'is_double',
            'top_scribe', 'top_rail_width', 'bottom_rail_width',
            'unlock_top_rail', 'unlock_bottom_rail',
            'bay_mid_rail_width', 'bay_mid_stile_width',
            'panel_frame_auto', 'panel_top_rail_width',
            'panel_bottom_rail_width', 'panel_stile_width',
            'default_top_overlay', 'default_bottom_overlay',
            'default_left_overlay', 'default_right_overlay',
            'material_thickness', 'face_frame_thickness',
            'door_thickness', 'back_thickness', 'division_thickness',
            'finish_toe_kick_thickness',
            'toe_kick_type', 'toe_kick_height', 'toe_kick_setback',
            'toe_kick_thickness', 'back_bottom_inset',
            'include_finish_toe_kick',
            'include_external_nailer', 'include_internal_nailer',
            'include_thin_finished_bottom',
            'include_thick_finished_bottom', 'include_blocking',
            'back_finished_end_condition', 'back_exposure', 'back_finish_end_auto',
            'corner_type', 'exterior_option', 'interior_option',
            'tray_compartment',
        ):
            try:
                setattr(new_props, name, getattr(cab_props, name))
            except (AttributeError, TypeError):
                pass

        # Side props
        _apply_side_props(new_props, 'RIGHT', captured_right)
        _apply_side_props(new_props, 'LEFT',
                          _default_side_props('LEFT', boundary_default, cab_props.depth))
        _apply_side_props(cab_props, 'RIGHT',
                          _default_side_props('RIGHT', boundary_default, cab_props.depth))

        # The two edges the break just created are an interior butt joint.
        # Setting the type re-derives the stile width from the style's butt
        # row (== boundary_default), before the width math reads it below.
        new_props.left_stile_type = 'BUTT'
        cab_props.right_stile_type = 'BUTT'

        # Delete the new cabinet's default bay (created by cls.create())
        for child in list(new_root.children):
            if child.get(TAG_BAY_CAGE):
                _remove_root_with_children(child)

        # Reparent right bays from original to new, reindex from 0
        for new_idx, bay in enumerate(right_bays):
            bay.parent = new_root
            bay.matrix_parent_inverse.identity()
            bay['hb_bay_index'] = new_idx
            bay.face_frame_bay.bay_index = new_idx

        # Delete boundary mid stile + mid div pair
        for p in boundary_parts:
            if p.name in bpy.data.objects:
                bpy.data.objects.remove(p, do_unlink=True)

        # Reparent right mid parts; subtract (gap_index + 1) from index
        for p in right_mid_parts:
            old_idx = p.get('hb_mid_stile_index', 0)
            p['hb_mid_stile_index'] = old_idx - (gap_index + 1)
            p.parent = new_root
            p.matrix_parent_inverse.identity()

        # Strip original's mid_stile_widths down to first gap_index entries
        coll_a = cab_props.mid_stile_widths
        while len(coll_a) > gap_index:
            coll_a.remove(len(coll_a) - 1)

        # Build new cabinet's mid_stile_widths
        coll_b = new_props.mid_stile_widths
        coll_b.clear()
        for w, ulk, ext_up, ext_dn in right_mids:
            entry = coll_b.add()
            entry.width = w
            entry.unlock = ulk
            entry.extend_up_amount = ext_up
            entry.extend_down_amount = ext_dn

        # Set widths so combined width preserves the original cabinet's
        # total. Replacing the boundary mid stile (width B) with two
        # new end stiles (each at default D) adds (2D - B) of extra
        # width. That extra has to be absorbed by shrinking unlocked
        # bays - same redistribution principle as merge but in
        # reverse. Locked bays (including the active one the operator
        # just locked) hold; unlocked bays in each half receive a
        # share of the shrinkage.
        left_bay_total = sum(b.face_frame_bay.width for b in bays[:gap_index + 1])
        left_mid_total = sum(w for (w, _, _, _) in mids_data[:gap_index])
        right_bay_total = sum(b.face_frame_bay.width for b in right_bays)
        right_mid_total = sum(w for (w, _, _, _) in right_mids)

        boundary_actual = mids_data[gap_index][0]
        extra = 2 * boundary_default - boundary_actual

        left_has_unlocked = any(not b.face_frame_bay.unlock_width
                                for b in bays[:gap_index + 1])
        right_has_unlocked = any(not b.face_frame_bay.unlock_width
                                 for b in right_bays)
        if shrink_side == 'LEFT' and left_has_unlocked:
            left_shrink, right_shrink = extra, 0.0
        elif shrink_side == 'RIGHT' and right_has_unlocked:
            left_shrink, right_shrink = 0.0, extra
        elif left_has_unlocked and right_has_unlocked:
            left_shrink, right_shrink = extra / 2.0, extra / 2.0
        elif left_has_unlocked:
            left_shrink, right_shrink = extra, 0.0
        elif right_has_unlocked:
            left_shrink, right_shrink = 0.0, extra
        else:
            # No unlocked bays anywhere. Distribute symmetrically; the
            # halves will be slightly oversized but the user can
            # adjust manually.
            left_shrink, right_shrink = extra / 2.0, extra / 2.0

        cab_props.width = (cab_props.left_stile_width
                           + left_bay_total + left_mid_total
                           + cab_props.right_stile_width
                           - left_shrink)
        new_props.width = (new_props.left_stile_width
                           + right_bay_total + right_mid_total
                           + new_props.right_stile_width
                           - right_shrink)

        # Position new cabinet abutting original (using the now-final
        # original width).
        new_root.location.x = cabinet.location.x + cab_props.width

    return new_root
