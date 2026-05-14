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

from mathutils import Vector

from ...hb_types import GeoNodeCage, GeoNodeCutpart, GeoNodeDrawerBox
from ...units import inch
from ..common import types_appliances
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
PART_ROLE_LEFT_KICK_RETURN = 'LEFT_KICK_RETURN'
PART_ROLE_RIGHT_KICK_RETURN = 'RIGHT_KICK_RETURN'
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

# Drawer box behind a drawer or pullout front. Parented to the front pivot
# (not the front part) so the box rides the slide animation but is sized
# from the opening cage's interior dimensions, independent of the front's
# overlay-inflated size. Not a member of FRONT_PART_ROLES; it's an interior
# part by structure even though it's spawned alongside the front.
PART_ROLE_DRAWER_BOX = 'DRAWER_BOX'

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
# Interior tree dividers: physical parts at split-node boundaries.
PART_ROLE_INTERIOR_DIVISION = 'INTERIOR_DIVISION'
PART_ROLE_INTERIOR_FIXED_SHELF = 'INTERIOR_FIXED_SHELF'

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
            self._create_drawer_box_for_front(pivot, leaf, rect)

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
        # so the bar runs horizontal across the drawer front.
        rot_z = math.radians(90.0) if kind == 'drawer' else 0.0
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
            auto_qty = solver.auto_shelf_qty(region_z)
            for item in region_props.interior_items:
                if item.kind == 'ADJUSTABLE_SHELF' and not item.unlock_shelf_qty:
                    if item.shelf_qty != auto_qty:
                        item.shelf_qty = auto_qty

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
        """Yield (region_props, region_cage_dim_z) pairs covering every
        leaf in the opening's interior tree. When the opening has no
        tree, yields exactly one pair: the opening's own props +
        cage_dim_z. Used by the auto-shelf-qty pass so each leaf seeds
        its shelf count from its own height, not the whole opening's.
        """
        root = solver._interior_tree_root(opening_obj)
        if root is None:
            yield (opening_obj.face_frame_opening,
                   opening_rect['cage_dim_z'])
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

        yield from _recurse(root, opening_rect['cage_dim_z'])

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

    def _create_rollout_box(self, opening_obj, desc):
        """Drawer box for ROLLOUT items. Uses GeoNodeDrawerBox parented
        to the opening cage in opening-local coords; origin sits at the
        box's front-left-bottom corner.
        """
        box = GeoNodeDrawerBox()
        box.create(desc['name'])
        box.obj.parent = opening_obj
        box.obj['hb_part_role'] = desc['role']
        box.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
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
        # Raise the back so it only spans the door zone above the
        # refrigerator. Mirrors the standard back z_origin formula
        # (top of bottom rail - mt) but anchored at the top of the
        # mid rail above the appliance opening: kick + bottom rail +
        # appliance + mid rail - mt. Captured at create-time; the
        # user can tweak from the cabinet prompts after.
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            cab_props.back_bottom_inset = (
                cab_props.toe_kick_height
                + cab_props.bottom_rail_width
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
    "Sink": SinkFaceFrameCabinet,
    "Lap Drawer": LapDrawerFaceFrameCabinet,
    "Upper": UpperFaceFrameCabinet,
    "Upper Stacked": UpperFaceFrameCabinet,
    "Tall": TallFaceFrameCabinet,
    "Tall Stacked": TallFaceFrameCabinet,
    "Refrigerator Cabinet": RefrigeratorCabinet,
    "Panel": PanelFaceFrameCabinet,
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
        _reapply_cabinet_style(root)
    finally:
        _RECALCULATING.discard(id(root))


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
    ff = bpy.context.scene.hb_face_frame
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


def break_cabinet_at_gap(cabinet, gap_index):
    """Break `cabinet` into two cabinets at the gap between bays
    `gap_index` and `gap_index+1`. Returns the new (right-half)
    cabinet root, or None on invalid input.

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
        boundary_default = cab_props.bay_mid_stile_width

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
        if left_has_unlocked and right_has_unlocked:
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
