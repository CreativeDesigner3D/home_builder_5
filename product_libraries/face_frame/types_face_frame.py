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
_RECALCULATING = set()
_DISTRIBUTING_WIDTHS = set()


# Single string-enum role for parts.
PART_ROLE_LEFT_SIDE = 'LEFT_SIDE'
PART_ROLE_RIGHT_SIDE = 'RIGHT_SIDE'
PART_ROLE_TOP = 'TOP'  # solid top panel for Upper / Tall (Base / Lap use stretchers)
PART_ROLE_FRONT_STRETCHER = 'FRONT_STRETCHER'
PART_ROLE_REAR_STRETCHER = 'REAR_STRETCHER'
PART_ROLE_BOTTOM = 'BOTTOM'
PART_ROLE_BACK = 'BACK'

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

# Front parts (children of opening cages). Roles are reserved here so
# selection-mode filtering can pick them up; only DOOR is implemented in
# this pass. Drawer fronts and pullouts will use their own roles when
# they land.
PART_ROLE_DOOR = 'DOOR'
PART_ROLE_DRAWER_FRONT = 'DRAWER_FRONT'
PART_ROLE_PULLOUT_FRONT = 'PULLOUT_FRONT'
PART_ROLE_FALSE_FRONT = 'FALSE_FRONT'

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

    def _build_carcass_parts(self, bay_qty):
        """Body of create_carcass, factored out so the guard wrapping above
        is easy to read. Creates carcass parts, end stiles, bay cages, and
        mid stile parts. Initializes per-bay PropertyGroups.
        """
        # ----- Carcass -----
        left = CabinetPart()
        left.create('Left Side')
        left.obj.parent = self.obj
        left.obj['hb_part_role'] = PART_ROLE_LEFT_SIDE
        left.obj['CABINET_PART'] = True
        left.obj.rotation_euler.y = math.radians(-90)
        left.set_input('Mirror Y', True)
        left.set_input('Mirror Z', True)

        right = CabinetPart()
        right.create('Right Side')
        right.obj.parent = self.obj
        right.obj['hb_part_role'] = PART_ROLE_RIGHT_SIDE
        right.obj['CABINET_PART'] = True
        right.obj.rotation_euler.y = math.radians(-90)
        right.set_input('Mirror Y', True)
        right.set_input('Mirror Z', False)

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
            bp.height = cab_props.height - (cab_props.toe_kick_height
                                            if self._has_toe_kick() else 0.0)
            bp.depth = cab_props.depth
            bp.kick_height = 0.0
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

            # Mid Division: carcass partition behind this mid stile.
            mid_div = CabinetPart()
            mid_div.create(f'Mid Division {i + 1}')
            mid_div.obj.parent = self.obj
            mid_div.obj['hb_part_role'] = PART_ROLE_MID_DIVISION
            mid_div.obj['CABINET_PART'] = True
            mid_div.obj['hb_mid_stile_index'] = i
            mid_div.obj.rotation_euler.y = math.radians(-90)
            mid_div.set_input('Mirror Y', True)
            mid_div.set_input('Mirror Z', True)

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
        """For each bay where unlock_height is False, sync the bay's
        height to the cabinet height minus the effective toe kick. Bays
        with unlock_height=True keep their stored value, allowing
        per-bay overrides without losing the user's value.

        Unlike width, height isn't shared across bays - each bay gets
        the full carcass height. So this function just pushes the
        cabinet's value onto unlocked bays; no redistribution math.
        """
        cab_props = self.obj.face_frame_cabinet
        bays = sorted(
            [c for c in self.obj.children if c.get(TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if not bays:
            return
        has_toe_kick = self._has_toe_kick()
        for bay_obj in bays:
            bp = bay_obj.face_frame_bay
            if bp.unlock_height:
                continue
            # Effective kick: per-bay override when its own unlock is
            # set, else the cabinet default.
            if has_toe_kick:
                kick = (bp.kick_height if bp.unlock_kick_height
                        else cab_props.toe_kick_height)
            else:
                kick = 0.0
            target = cab_props.height - kick
            if abs(bp.height - target) > 1e-6:
                bp.height = target

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

        remainder = cab_props.width - consumed - locked_total
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
            # face frame opening rect.
            ff_height = bp.height - bp.top_rail_width - bp.bottom_rail_width
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
        # Then the width calculator before the solver reads bay widths.
        self._distribute_bay_widths()
        # Then redistribute sizes inside each bay's tree of openings /
        # splits. Order matters: bay widths need to be settled first
        # because each bay's tree's available width comes from bp.width.
        self._distribute_split_sizes()

        layout = solver.FaceFrameLayout(self.obj)
        carcass_depth = solver.carcass_inner_depth(layout)

        # Compute and reconcile rail segments before the dispatch loop
        top_segments = solver.top_rail_segments(layout)
        bottom_segments = solver.bottom_rail_segments(layout)
        carcass_bottom_segs = solver.carcass_bottom_segments(layout)
        carcass_back_segs = solver.carcass_back_segments(layout)
        self._reconcile_rails(PART_ROLE_TOP_RAIL, top_segments)
        self._reconcile_rails(PART_ROLE_BOTTOM_RAIL, bottom_segments)
        self._reconcile_carcass_bottoms(carcass_bottom_segs)
        self._reconcile_carcass_backs(carcass_back_segs)

        # Top construction branches on cabinet type:
        #   BASE / LAP_DRAWER -> Front + Rear stretchers
        #   UPPER / TALL      -> Solid top panel
        # Cleanup the other style's parts in case of cabinet-type change
        # or migration from a previous architecture.
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

        top_seg_by_start = {s['start_bay']: s for s in top_segments}
        bot_seg_by_start = {s['start_bay']: s for s in bottom_segments}
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

            part = GeoNodeCutpart(child)

            # ---- Carcass (sides shrink to leave room for the face frame at front) ----
            if role == PART_ROLE_LEFT_SIDE:
                pos = solver.left_side_position(layout)
                length, width, thickness = solver.left_side_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

            elif role == PART_ROLE_RIGHT_SIDE:
                pos = solver.right_side_position(layout)
                length, width, thickness = solver.right_side_dims(layout)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
                part.set_input('Thickness', thickness)

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
                if msi >= len(layout.mid_stiles):
                    child.hide_viewport = True
                    continue
                child.hide_viewport = False
                pos = solver.mid_division_position(layout, msi)
                length, width, thickness = solver.mid_division_dims(layout, msi)
                child.location = pos
                part.set_input('Length', length)
                part.set_input('Width', width)
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
        # Pass 3: backings (divisions / shelves) - delete & recreate
        self._reconcile_bay_backings(bay_obj, parts['backings'])

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
        FALSE_FRONT skips - false fronts are decorative and don't carry
        a pull. Returns the pull Object (or None if no pull is selected
        or the asset can't be loaded).

        The pull is parented to `front_part` so it inherits the swing /
        slide animation. Position is computed in front-part local space
        (X = Length axis, -Y = Width axis, -Z = out of cabinet). Pull
        rotation_euler.x = +90 deg maps the asset's bar axis along
        the door's vertical and orients its body in -Z (outward).
        """
        if role == PART_ROLE_FALSE_FRONT:
            return None
        scene_props = bpy.context.scene.hb_face_frame
        kind = 'drawer' if role in (PART_ROLE_DRAWER_FRONT, PART_ROLE_PULLOUT_FRONT) else 'door'
        pull_obj = pulls.resolve_pull_object(scene_props, kind)
        if pull_obj is None:
            return None

        cabinet_type = self.obj.face_frame_cabinet.cabinet_type
        length, width, thickness = leaf['part_dims']
        h_offset = scene_props.pull_horizontal_offset

        # Vertical (X axis on door): zone-dependent.
        if kind == 'drawer':
            if scene_props.center_pulls_on_drawer_front:
                x = length / 2.0
            else:
                # Off-center moves the pull toward the top of the
                # drawer. Reuse the base vertical offset so the user
                # only has one offset to tune.
                x = length - scene_props.pull_vertical_location_base
        elif cabinet_type == 'UPPER':
            x = scene_props.pull_vertical_location_upper
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
                x = scene_props.pull_vertical_location_upper
            elif length >= tall_offset:
                x = tall_offset
            else:
                x = length - scene_props.pull_vertical_location_base
        else:
            # BASE / LAP_DRAWER: measure DOWN from top of door.
            x = length - scene_props.pull_vertical_location_base

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
        """
        op_props = opening_obj.face_frame_opening

        # Wipe existing interior children. Match either by role tag or
        # by the explicit ACCESSORY marker we set on text objects, since
        # text-data objects can't carry the same custom prop conventions
        # quite as cleanly as mesh parts.
        for child in list(opening_obj.children):
            if child.get('hb_part_role') in INTERIOR_PART_ROLES:
                bpy.data.objects.remove(child, do_unlink=True)

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
    """Lap drawer cabinet: shallow drawer unit at counter height."""
    default_cabinet_type = 'LAP_DRAWER'

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
        self.create_carcass(has_toe_kick=True, bay_qty=bay_qty)


# ---------------------------------------------------------------------------
# Helpers - cabinet lookup and recalc-from-prop-update
# ---------------------------------------------------------------------------
CABINET_NAME_DISPATCH = {
    "Base Door": BaseFaceFrameCabinet,
    "Base Door Drw": BaseFaceFrameCabinet,
    "Base Drawer": BaseFaceFrameCabinet,
    "Lap Drawer": LapDrawerFaceFrameCabinet,
    "Upper": UpperFaceFrameCabinet,
    "Upper Stacked": UpperFaceFrameCabinet,
    "Tall": TallFaceFrameCabinet,
    "Tall Stacked": TallFaceFrameCabinet,
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


def _wrap_cabinet(obj):
    """Wrap a cabinet root Object as the appropriate FaceFrameCabinet subclass."""
    class_name = obj.get('CLASS_NAME', 'FaceFrameCabinet')
    cls_lookup = {
        'BaseFaceFrameCabinet': BaseFaceFrameCabinet,
        'UpperFaceFrameCabinet': UpperFaceFrameCabinet,
        'TallFaceFrameCabinet': TallFaceFrameCabinet,
        'LapDrawerFaceFrameCabinet': LapDrawerFaceFrameCabinet,
    }
    cls = cls_lookup.get(class_name, FaceFrameCabinet)
    instance = cls.__new__(cls)
    GeoNodeCage.__init__(instance, obj)
    return instance


def recalculate_face_frame_cabinet(obj):
    """Push current property values to all carcass parts. Safe entry point
    for property update callbacks. Walks up to find the cabinet root if obj
    is a child or descendant.

    Guarded against reentrance: if a recalc is already in progress for this
    cabinet (because a bay/cabinet prop write inside recalculate fired its
    update callback), this call exits immediately. The outer recalc will
    pick up the new value when it reads from props.
    """
    root = find_cabinet_root(obj)
    if root is None:
        return
    if id(root) in _RECALCULATING:
        return
    _RECALCULATING.add(id(root))
    try:
        cabinet = _wrap_cabinet(root)
        cabinet.recalculate()
    finally:
        _RECALCULATING.discard(id(root))
