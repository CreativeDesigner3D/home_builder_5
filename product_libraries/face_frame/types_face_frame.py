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


# ---------------------------------------------------------------------------
# Identity tags
# ---------------------------------------------------------------------------
TAG_CABINET_CAGE = 'IS_FACE_FRAME_CABINET_CAGE'
TAG_BAY_CAGE = 'IS_FACE_FRAME_BAY_CAGE'

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
PART_ROLE_TOP = 'TOP'
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

FACE_FRAME_PART_ROLES = frozenset({
    PART_ROLE_TOP_RAIL, PART_ROLE_BOTTOM_RAIL,
    PART_ROLE_LEFT_STILE, PART_ROLE_RIGHT_STILE,
    PART_ROLE_MID_STILE, PART_ROLE_MID_RAIL,
})

# Carcass interior partition behind each mid stile (one per gap).
PART_ROLE_MID_DIVISION = 'MID_DIVISION'


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

        # Run the width calculator before the solver reads bay widths.
        self._distribute_bay_widths()

        layout = solver.FaceFrameLayout(self.obj)
        carcass_depth = solver.carcass_inner_depth(layout)

        # Compute and reconcile rail segments before the dispatch loop
        top_segments = solver.top_rail_segments(layout)
        bottom_segments = solver.bottom_rail_segments(layout)
        carcass_bottom_segs = solver.carcass_bottom_segments(layout)
        carcass_back_segs = solver.carcass_back_segments(layout)
        carcass_top_segs = solver.carcass_top_segments(layout)
        self._reconcile_rails(PART_ROLE_TOP_RAIL, top_segments)
        self._reconcile_rails(PART_ROLE_BOTTOM_RAIL, bottom_segments)
        self._reconcile_carcass_bottoms(carcass_bottom_segs)
        self._reconcile_carcass_backs(carcass_back_segs)
        self._reconcile_carcass_tops(carcass_top_segs)

        top_seg_by_start = {s['start_bay']: s for s in top_segments}
        bot_seg_by_start = {s['start_bay']: s for s in bottom_segments}
        carc_bot_by_start = {s['start_bay']: s for s in carcass_bottom_segs}
        carc_back_by_start = {s['start_bay']: s for s in carcass_back_segs}
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


    def _reconcile_carcass_tops(self, segments):
        """Match Top carcass children against segments. Same three-pass
        delete/match/create as _reconcile_carcass_bottoms / _backs. Also
        cleans up any legacy non-segment Top (its hb_segment_start_bay is
        None which is never in wanted_starts).
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
        """Create one carcass top part keyed to its segment.

        Mirror Y/Z to match the existing single-top convention so the
        panel extends in -Y (front) and -Z (down) from its origin.
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
        """Position and size a single bay cage from the solver."""
        if bay_index >= layout.bay_count:
            bay_obj.hide_viewport = True
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
