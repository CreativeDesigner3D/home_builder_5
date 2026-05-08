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
import math
from contextlib import contextmanager

from ...hb_types import GeoNodeCage, GeoNodeCutpart
from ...units import inch
from ..frameless.types_frameless import CabinetPart
from . import solver_face_frame as solver
from . import pulls


# ---------------------------------------------------------------------------
# Identity tags
# ---------------------------------------------------------------------------
TAG_CABINET_CAGE = 'IS_FACE_FRAME_CABINET_CAGE'
TAG_BAY_CAGE = 'IS_FACE_FRAME_BAY_CAGE'
TAG_OPENING_CAGE = 'IS_FACE_FRAME_OPENING_CAGE'
TAG_SPLIT_NODE = 'IS_FACE_FRAME_SPLIT_NODE'

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
PART_ROLE_LEFT_KICK_RETURN = 'LEFT_KICK_RETURN'
PART_ROLE_RIGHT_KICK_RETURN = 'RIGHT_KICK_RETURN'

# Face frame member roles (rails and stiles). Phase 3a doesn't create any
# of these yet; defined here so the "Face Frame" selection mode has a known
# set of roles to filter on once Phase 3b builds them.
PART_ROLE_TOP_RAIL = 'TOP_RAIL'
PART_ROLE_BOTTOM_RAIL = 'BOTTOM_RAIL'
PART_ROLE_LEFT_STILE = 'LEFT_STILE'
PART_ROLE_RIGHT_STILE = 'RIGHT_STILE'
PART_ROLE_MID_STILE = 'MID_STILE'
PART_ROLE_MID_RAIL = 'MID_RAIL'

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
})

BAY_SPLITTER_ROLES = frozenset({
    PART_ROLE_BAY_MID_RAIL, PART_ROLE_BAY_MID_STILE,
})
BAY_BACKING_ROLES = frozenset({
    PART_ROLE_BAY_DIVISION, PART_ROLE_BAY_SHELF,
})

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

# Applied finished-back part: a 3/4 panel layered on top of the carcass
# back when back_finished_end_condition is FINISHED. Carcass back stays
# at its normal back_thickness (1/4 typically); this part adds the
# visible finish surface behind it.
PART_ROLE_FINISHED_BACK = 'FINISHED_BACK'

# Applied flush-X strip: a 1/4 part covering the front portion of a
# cabinet side when LEFT/RIGHT_finished_end_condition is FLUSH_X. The
# strip's outer face is flush with the FF outer face; its width along
# the cabinet depth is the user's *_flush_x_amount value (typically
# 4"). Used for sides that abut a dishwasher / appliance where a full
# applied panel isn't wanted.
PART_ROLE_FLUSH_X = 'FLUSH_X'
TAG_FLUSH_X_SIDE = 'hb_flush_x_side'

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

# Front roles that share the same panel geometry today. Keeping them
# grouped here so reconciliation can iterate the set instead of
# spelling each role out.
FRONT_PART_ROLES = frozenset({
    PART_ROLE_DOOR,
    PART_ROLE_DRAWER_FRONT,
    PART_ROLE_PULLOUT_FRONT,
    PART_ROLE_FALSE_FRONT,
    PART_ROLE_INSET_PANEL,
})

FRONT_TYPE_TO_ROLE = {
    'DOOR':         PART_ROLE_DOOR,
    'DRAWER_FRONT': PART_ROLE_DRAWER_FRONT,
    'PULLOUT':      PART_ROLE_PULLOUT_FRONT,
    'FALSE_FRONT':  PART_ROLE_FALSE_FRONT,
}

# ---------------------------------------------------------------------------
# Interior parts (children of opening cages; sit behind the face frame).
# Orthogonal to front_type - any front_type can carry interior items, and
# 'open' openings (front_type = NONE) get all of their visual content from
# this list.
# ---------------------------------------------------------------------------
PART_ROLE_ADJUSTABLE_SHELF = 'ADJUSTABLE_SHELF'
PART_ROLE_ACCESSORY_LABEL = 'ACCESSORY_LABEL'

INTERIOR_PART_ROLES = frozenset({
    PART_ROLE_ADJUSTABLE_SHELF,
    PART_ROLE_ACCESSORY_LABEL,
})

INTERIOR_KIND_TO_ROLE = {
    'ADJUSTABLE_SHELF': PART_ROLE_ADJUSTABLE_SHELF,
    'ACCESSORY':        PART_ROLE_ACCESSORY_LABEL,
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
    PART_ROLE_BAY_SHELF, PART_ROLE_ADJUSTABLE_SHELF,
})

# Baseline rotation_euler.z for parts that live in the face frame plane.
# Recalc adds face_frame_angle on top so they rotate with the angled
# FF plane in angled mode; with theta = 0 the values match the build-
# time rotations and there's no behavior change for square cabinets.
# Bay cages are handled separately in _update_bay_cage (no baseline; the
# FF angle IS the rotation).
FF_ROTATION_BASELINE_Z = {
    PART_ROLE_LEFT_STILE:        math.pi / 2,
    PART_ROLE_RIGHT_STILE:       math.pi / 2,
    PART_ROLE_TOP_RAIL:          0.0,
    PART_ROLE_BOTTOM_RAIL:       0.0,
    PART_ROLE_TOE_KICK_SUBFRONT: 0.0,
    PART_ROLE_FINISH_TOE_KICK:   0.0,
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


# ---------------------------------------------------------------------------
# Base cabinet class
# ---------------------------------------------------------------------------
class FaceFrameCabinet(GeoNodeCage):
    """Base class for all face frame cabinets.

    No drivers. All dimensions flow through the recalculate() method which
    reads from the cabinet's face_frame_cabinet PropertyGroup and writes
    dimensions/positions to all child parts.
    """

    default_width = inch(36)
    default_height = inch(34.5)
    default_depth = inch(24)
    default_cabinet_type = 'BASE'

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

            # 5) Build the new mid-stile + mid-div pair at new_gap_index.
            self._create_mid_parts_at(new_gap_index)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()
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

        self.recalculate()
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
        mid_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_mid_stile_commands'
        mid_stile.obj.rotation_euler.y = math.radians(-90)
        mid_stile.obj.rotation_euler.z = math.radians(90)
        mid_stile.set_input('Mirror Y', True)
        mid_stile.set_input('Mirror Z', True)

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
        left_stile.obj.rotation_euler.y = math.radians(-90)
        left_stile.obj.rotation_euler.z = math.radians(90)
        left_stile.set_input('Mirror Y', True)
        left_stile.set_input('Mirror Z', True)

        right_stile = CabinetPart()
        right_stile.create('Right End Stile')
        right_stile.obj.parent = self.obj
        right_stile.obj['hb_part_role'] = PART_ROLE_RIGHT_STILE
        right_stile.obj['CABINET_PART'] = True
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
            mid_stile.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_mid_stile_commands'
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
            available_width = cab_props.width

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

        remainder = parent_dim - n_splitters * splitter_w - locked_total
        share = remainder / len(unlocked) if unlocked else 0.0

        _DISTRIBUTING_WIDTHS.add(id(self.obj))
        try:
            for c in unlocked:
                self._write_node_size(c, share)
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
                self._ensure_kick_return(
                    PART_ROLE_LEFT_KICK_RETURN, 'Toe Kick Return Left',
                    mirror_z=True)
                self._ensure_kick_return(
                    PART_ROLE_RIGHT_KICK_RETURN, 'Toe Kick Return Right',
                    mirror_z=False)
            else:
                kick_subfront_segs = []
                finish_kick_segs = []
                self._reconcile_kick_subfronts([])
                self._reconcile_finish_kicks([])

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
        kick_seg_by_start = {s['start_bay']: s for s in kick_subfront_segs}
        finish_kick_seg_by_start = {s['start_bay']: s for s in finish_kick_segs}
        carc_bot_by_start = {s['start_bay']: s for s in carcass_bottom_segs}
        carc_back_by_start = {s['start_bay']: s for s in carcass_back_segs}
        front_str_by_start = {s['start_bay']: s for s in front_stretcher_segs}
        rear_str_by_start = {s['start_bay']: s for s in rear_stretcher_segs}
        carc_top_by_start = {s['start_bay']: s for s in carcass_top_segs}

        for child in self.obj.children:
            role = child.get('hb_part_role')
            bay_index = child.get('hb_bay_index', 0)

            # Bay cage handling (no hb_part_role; identified by tag)
            if child.get(TAG_BAY_CAGE):
                self._update_bay_cage(child, layout, bay_index)
                continue

            if not role:
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

            # ---- Mid stiles (gap-keyed) ----
            elif role == PART_ROLE_MID_STILE:
                # Backfill MENU_ID for cabinets created before right-click was added
                if not child.get('MENU_ID'):
                    child['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_mid_stile_commands'
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
            self._reconcile_textured_panels(layout)

        # Angled cabinet cutter: drives the trapezoidal silhouette on
        # the root cage, top, bottom, and any shelves. Lazy: created
        # on transition into angled mode, removed on transition out.
        if layout.is_angled and self._has_carcass():
            cutter_obj = self._ensure_angled_cutter()
            self._position_angled_cutter(cutter_obj, layout)
            self._apply_angled_cuts(cutter_obj)
        else:
            self._cleanup_angled_cutter_and_cuts()

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

            location, rotation_z, width, height, depth = (
                applied_panel_geometry(layout, side)
            )
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

        Spans the full cabinet width and full cabinet height. Refining
        for stepped cabinets or excluding the toe kick is deferred.
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

        existing.location = (0.0, thickness, 0.0)
        part.set_input('Length',    layout.dim_z)
        part.set_input('Width',     layout.dim_x)
        part.set_input('Thickness', thickness)

    # =====================================================================
    # Applied flush-X strips (single 1/4 part on the front of a side)
    # =====================================================================
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
            bottom_z = solver.bay_bottom_z(layout, bay_index)
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
        else:
            stile_to_floor = solver.right_stile_to_floor(layout)
            has_inset = layout.kick_inset_right > 0
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
            thickness = cab_props.material_thickness
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
                mod[node_input.identifier] = value
        mod.show_viewport = active
        mod.show_render = active

    def _update_mid_div_notches(self, mid_div_obj, panel):
        """Drive the two CPM_CORNERNOTCH modifiers on a slot-0 mid-div.

        The build path adds 'Notch Top Front' and 'Notch Top Back' with
        their Flip flags pre-set. Each recalc updates X / Y / Route Depth
        and toggles show_viewport / show_render based on the solver's
        notch_active flag. Slot-1 mid-divs (diff-depth case) have no
        notch modifiers and silently no-op here.
        """
        active = panel.get('notch_active', False)
        size_x = panel.get('notch_x', 0.0)
        size_y = panel.get('notch_y', 0.0)
        route = panel.get('notch_route_depth', 0.0)
        for name in ('Notch Top Front', 'Notch Top Back'):
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
                    mod[node_input.identifier] = value
            mod.show_viewport = active
            mod.show_render = active

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
            if descendant.get('hb_part_role') in BAY_SPLITTER_ROLES:
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
        rail.create(f'Bay Mid Rail {idx}')
        rail.obj.parent = split_obj
        rail.obj['hb_part_role'] = PART_ROLE_BAY_MID_RAIL
        rail.obj['CABINET_PART'] = True
        rail.obj['hb_split_node_name'] = rect['split_node_name']
        rail.obj['hb_splitter_index'] = rect['splitter_index']
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

            self._create_pull_for_front(front, leaf['role'], leaf)

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

        Orientation matches the left end stile pattern: rotation y=-90,
        z=90 with Mirror Y=True and Mirror Z=True. With those flags
        Length goes +Z, Width goes +X, Thickness goes +Y from the
        part's origin - the leaf's part_position picks the X / Z
        offsets so the panel anchors against the pivot's hinge corner.
        """
        part = CabinetPart()
        part.create(name)
        part.obj.parent = pivot_obj
        part.obj['hb_part_role'] = role
        part.obj['CABINET_PART'] = True
        part.obj.rotation_euler.y = math.radians(-90)
        part.obj.rotation_euler.z = math.radians(90)
        part.set_input('Mirror Y', True)
        part.set_input('Mirror Z', True)
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
        kind = 'drawer' if role in (PART_ROLE_DRAWER_FRONT, PART_ROLE_PULLOUT_FRONT) else 'door'
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

        # Vertical (X axis on door): zone-dependent.
        if kind == 'drawer':
            if scene_props.center_pulls_on_drawer_front:
                x = length / 2.0
            else:
                # Off-center moves the pull toward the top of the
                # drawer. Reuse the base vertical offset so the user
                # only has one offset to tune.
                x = length - scene_props.pull_vertical_location_base - half_pull_len
        elif cabinet_type == 'UPPER':
            x = scene_props.pull_vertical_location_upper + half_pull_len
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
                x = scene_props.pull_vertical_location_upper + half_pull_len
            elif length >= tall_offset:
                x = tall_offset + half_pull_len
            else:
                x = length - scene_props.pull_vertical_location_base - half_pull_len
        else:
            # BASE / LAP_DRAWER: measure DOWN from top of door.
            x = length - scene_props.pull_vertical_location_base - half_pull_len

        # Horizontal (Y axis on door): the leaf builder positions a
        # right-hinged door's local origin at the UNHINGED corner
        # (door.location.x is offset by -width so the door extends
        # back across the cabinet). Detecting that lets us flip the
        # pull to the correct edge without needing to thread
        # hinge_side through the leaf descriptor.
        if kind == 'drawer':
            # Drawers always horizontally centered. center_pulls_on_drawer_front
            # controls the vertical position, not horizontal.
            y = -width / 2.0
        elif front_part.obj.location.x < 0.0:
            # Right-hinged door: hinge at Y = -width, unhinged at Y = 0.
            y = -h_offset
        else:
            # Left-hinged door (incl. DOUBLE Left leaf): hinge at Y = 0,
            # unhinged at Y = -width.
            y = -(width - h_offset)

        # Mounting plane: pull sits flush against the door front face.
        # Door's local Z=0 is the front (maps to most negative world Y);
        # Z=-thickness is the back (toward cabinet). The cage's Mirror Z
        # makes geometry extend -Z from origin, but the origin itself is
        # the front face.
        z = 0.0

        instance = bpy.data.objects.new(f"Pull - {front_part.obj.name}", pull_obj.data)
        bpy.context.scene.collection.objects.link(instance)
        instance.parent = front_part.obj
        instance.location = (x, y, z)
        # rotation_x = -90 deg: pull body (modeled in -Y) ends up extending
        # in door-local +Z, which is away from the cabinet (beyond the
        # door front). Bar axis stays along door-local +X = vertical for
        # doors. For drawers (and pullouts) we add rotation_z = 90 deg
        # so the bar runs horizontal across the drawer front.
        rot_z = math.radians(90.0) if kind == 'drawer' else 0.0
        instance.rotation_euler = (math.radians(-90.0), 0.0, rot_z)
        instance['hb_part_role'] = 'PULL'
        instance['IS_CABINET_PULL'] = True
        return instance


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

        # Sync auto-computed shelf counts for any unlocked items before
        # the solver reads them. Writing shelf_qty fires its update
        # callback which would re-enter recalculate_face_frame_cabinet,
        # but the _RECALCULATING guard short-circuits that.
        auto_qty = solver.auto_shelf_qty(rect['cage_dim_z'])
        for item in op_props.interior_items:
            if item.kind == 'ADJUSTABLE_SHELF' and not item.unlock_shelf_qty:
                if item.shelf_qty != auto_qty:
                    item.shelf_qty = auto_qty

        for desc in solver.interior_item_descriptors(
            layout, rect, self.obj.face_frame_cabinet, op_props
        ):
            kind = desc['kind']
            if kind == 'ADJUSTABLE_SHELF':
                self._create_shelf_part(opening_obj, desc)
            elif kind == 'ACCESSORY':
                self._create_accessory_label(opening_obj, desc)

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
        text_obj.parent = opening_obj
        text_obj.location = desc['position']
        text_obj.rotation_euler = desc['rotation']
        text_obj['hb_part_role'] = desc['role']
        return text_obj

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


CABINET_NAME_DISPATCH = {
    "Base Door": BaseFaceFrameCabinet,
    "Base Door Drw": BaseFaceFrameCabinet,
    "Base Drawer": BaseFaceFrameCabinet,
    "Floating Base Cabinet": FloatingBaseFaceFrameCabinet,
    "Lap Drawer": LapDrawerFaceFrameCabinet,
    "Upper": UpperFaceFrameCabinet,
    "Upper Stacked": UpperFaceFrameCabinet,
    "Tall": TallFaceFrameCabinet,
    "Tall Stacked": TallFaceFrameCabinet,
    "Panel": PanelFaceFrameCabinet,
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
    face touches the side panel. Y range matches the side panel
    (between back of FF and back of cabinet); Z range matches the bay's
    vertical extent so the applied panel and the side panel align.

    BACK uses simple full-extent positioning for now; refining is
    deferred until applied-back behavior is settled.

    The standalone panel's local axes are: +X = width, +Y points INTO
    the panel (back face Y=0, front Y=-depth), +Z = up. Each side's
    rotation around Z aims the front face outward from the cabinet.
    """
    if side == 'LEFT':
        scribe = solver.left_scribe_offset(layout)
        bottom_z = solver.bay_bottom_z(layout, 0)
        top_z = solver.left_side_top_z(layout)
        # Rz(-pi/2): panel +X -> cabinet -Y, panel +Y -> cabinet +X.
        # Origin x = scribe (panel back face touches side outer face);
        # panel front face lands at cabinet x = 0 (flush with FF outer
        # face) when depth = scribe.
        location = (scribe, 0.0, bottom_z)
        rotation_z = -math.pi / 2.0
        width = layout.dim_y - layout.fft
        height = top_z - bottom_z
        return (location, rotation_z, width, height, scribe)
    if side == 'RIGHT':
        scribe = solver.right_scribe_offset(layout)
        last = layout.bay_count - 1
        bottom_z = solver.bay_bottom_z(layout, last)
        top_z = solver.right_side_top_z(layout)
        # Rz(+pi/2): panel +X -> cabinet +Y, panel +Y -> cabinet -X.
        # Origin x = dim_x - scribe; front face lands at dim_x (flush
        # with FF outer face) when depth = scribe.
        location = (layout.dim_x - scribe,
                    -layout.dim_y + layout.fft, bottom_z)
        rotation_z = math.pi / 2.0
        width = layout.dim_y - layout.fft
        height = top_z - bottom_z
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
    'UpperFaceFrameCabinet': UpperFaceFrameCabinet,
    'TallFaceFrameCabinet': TallFaceFrameCabinet,
    'LapDrawerFaceFrameCabinet': LapDrawerFaceFrameCabinet,
    'PanelFaceFrameCabinet': PanelFaceFrameCabinet,
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
    finally:
        _RECALCULATING.discard(id(root))
