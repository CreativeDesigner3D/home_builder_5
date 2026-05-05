"""Corner face frame cabinets - pie cut, diagonal, corner drawer.

CornerFaceFrameCabinet shares the cabinet root, bay tree, and opening /
front infrastructure from FaceFrameCabinet. Carcass build and the recalc
path dispatch on default_corner_type. Tiny size-variant subclasses
(BasePieCutCabinet, UpperPieCutCabinet, TallPieCutCabinet) match the
existing per-cabinet-type subclass pattern in types_face_frame.

Slice 3 deliverable: full carcass parts (Bottom, Top, Left/Right Back,
Left/Right Side, Left/Right Kick) with corner-shape booleans wired and
driven from cab_props through a corner-specific recalculate(). Face
frames, bays, and doors land in slices 4 and 5.
"""
import bpy
import math

from ...units import inch
from ...hb_types import CabinetPartModifier, GeoNodeCage
from ..frameless.types_frameless import CabinetPart
from . import types_face_frame as ff


# ---------------------------------------------------------------------------
# Identity tags
# ---------------------------------------------------------------------------
PART_ROLE_CORNER_BOTTOM = 'CORNER_BOTTOM'
PART_ROLE_CORNER_TOP = 'CORNER_TOP'
PART_ROLE_CORNER_LEFT_BACK = 'CORNER_LEFT_BACK'
PART_ROLE_CORNER_RIGHT_BACK = 'CORNER_RIGHT_BACK'
PART_ROLE_CORNER_LEFT_SIDE = 'CORNER_LEFT_SIDE'
PART_ROLE_CORNER_RIGHT_SIDE = 'CORNER_RIGHT_SIDE'
PART_ROLE_CORNER_LEFT_KICK = 'CORNER_LEFT_KICK'
PART_ROLE_CORNER_RIGHT_KICK = 'CORNER_RIGHT_KICK'
PART_ROLE_CORNER_LEFT_FINISH_KICK = 'CORNER_LEFT_FINISH_KICK'
PART_ROLE_CORNER_RIGHT_FINISH_KICK = 'CORNER_RIGHT_FINISH_KICK'

# Diagonal-specific roles. The cutter is a child of the cabinet root
# carrying GeoNodeCage geometry; carcass parts that need the 45 degree
# face cut hold a Blender Boolean DIFFERENCE modifier referencing it.
PART_ROLE_DIAGONAL_CUTTER = 'DIAGONAL_CUTTER'
PART_ROLE_DIAGONAL_SIDE_CUTTER = 'DIAGONAL_SIDE_CUTTER'
PART_ROLE_DIAGONAL_KICK = 'DIAGONAL_KICK'
PART_ROLE_CORNER_INTERIOR = 'CORNER_INTERIOR'

CORNER_PART_ROLES = frozenset({
    PART_ROLE_CORNER_BOTTOM,
    PART_ROLE_CORNER_TOP,
    PART_ROLE_CORNER_LEFT_BACK,
    PART_ROLE_CORNER_RIGHT_BACK,
    PART_ROLE_CORNER_LEFT_SIDE,
    PART_ROLE_CORNER_RIGHT_SIDE,
    PART_ROLE_CORNER_LEFT_KICK,
    PART_ROLE_CORNER_RIGHT_KICK,
    PART_ROLE_CORNER_LEFT_FINISH_KICK,
    PART_ROLE_CORNER_RIGHT_FINISH_KICK,
    PART_ROLE_DIAGONAL_CUTTER,
    PART_ROLE_DIAGONAL_SIDE_CUTTER,
    PART_ROLE_DIAGONAL_KICK,
    PART_ROLE_CORNER_INTERIOR,
})


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _set_mod_input(obj, mod_name, input_name, value):
    """Set one named input on a named modifier of obj. No-op if the
    modifier or its node group or the input is missing.

    interface_update() is required before the assignment - without it
    the modifier socket gets the new value but the geometry node graph
    doesn't re-evaluate, leaving the object's mesh stale. Mirrors the
    pattern in GeoNodeObject.set_input().
    """
    mod = obj.modifiers.get(mod_name)
    if mod is None or mod.node_group is None:
        return
    ni = mod.node_group.interface.items_tree.get(input_name)
    if ni is not None:
        mod.node_group.interface_update(bpy.context)
        mod[ni.identifier] = value


def _set_mod_inputs(obj, mod_name, pairs):
    """Bulk variant: pairs is iterable of (input_name, value)."""
    for k, v in pairs:
        _set_mod_input(obj, mod_name, k, v)


def _children_by_corner_role(cab_obj):
    """Return {role: child_obj} for direct children whose hb_part_role
    is one of the corner-specific roles.
    """
    out = {}
    for c in cab_obj.children:
        role = c.get('hb_part_role')
        if role in CORNER_PART_ROLES:
            out[role] = c
    return out


def _find_ff_part(cab_obj, role, side):
    """Find a face frame part by hb_part_role + hb_face_frame_side tag.

    Corner cabinets reuse the standard rail / stile roles plus an
    hb_face_frame_side tag (LEFT or RIGHT) so per-side parts share
    the existing role enum without doubling it.
    """
    for c in cab_obj.children:
        if c.get('hb_part_role') == role and c.get('hb_face_frame_side') == side:
            return c
    return None


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------
class CornerFaceFrameCabinet(ff.FaceFrameCabinet):
    """Unified corner cabinet. default_corner_type drives shape-specific
    construction; default_cabinet_type drives size-class behavior (toe
    kick presence, default heights / depths).
    """

    default_corner_type = 'PIE_CUT'
    default_cabinet_type = 'BASE'

    # Pie cut footprint is square - Dim X = Dim Y = default_width.
    default_width = inch(36)
    default_depth = inch(36)
    default_height = inch(34.5)

    # Stub-side length perpendicular to each wall. Drives the L-shape of
    # the carcass and the inset of each face frame from the wall corner.
    default_left_depth = inch(24)
    default_right_depth = inch(24)

    def create_cabinet_root(self, name):
        super().create_cabinet_root(name)
        cab_props = self.obj.face_frame_cabinet
        cab_props.corner_type = self.default_corner_type
        cab_props.left_depth = self.default_left_depth
        cab_props.right_depth = self.default_right_depth
        if self.default_corner_type == 'PIE_CUT':
            self._add_root_corner_notch()
        # DIAGONAL: root chamfer (Boolean DIFFERENCE referencing the
        # Diagonal Cutter object) is added in _build_diagonal_parts
        # because the cutter object doesn't exist until carcass build.

    def _add_root_corner_notch(self):
        """Add the root cage's corner-notch modifier. Inputs are
        refreshed every recalc by _update_root_corner_notch.

        Cage runs Mirror Y = True so geometry extends -Y from origin.
        Wall corner sits at (0, 0); room corner at (+width, -depth).
        Flip X = Flip Y = True positions the notch opposite the base
        point, in the room-facing corner.
        """
        cpm = CabinetPartModifier(self.obj)
        cpm.add_node('CPM_CORNERNOTCH', 'Front Notch')
        cpm.set_input('Flip X', True)
        cpm.set_input('Flip Y', True)
        cpm.mod.show_viewport = True
        cpm.mod.show_render = True

    def _update_root_corner_notch(self):
        """Drive the root cage notch inputs from cab_props."""
        cab_props = self.obj.face_frame_cabinet
        _set_mod_inputs(self.obj, 'Front Notch', (
            ('X', cab_props.width - cab_props.left_depth),
            ('Y', cab_props.depth - cab_props.right_depth),
            ('Route Depth', cab_props.height + inch(1.0)),
        ))

    def create(self, name="Corner Cabinet", bay_qty=1):
        self.create_cabinet_root(name)
        self.create_carcass(has_toe_kick=self._has_toe_kick(), bay_qty=1)

    def _has_toe_kick(self):
        return self.default_cabinet_type in ('BASE', 'TALL')

    # -----------------------------------------------------------------
    # Carcass build (overrides FaceFrameCabinet._build_carcass_parts)
    # -----------------------------------------------------------------
    def _build_carcass_parts(self, bay_qty):
        """Corner cabinets dispatch on default_corner_type. Bay system
        is not built in slice 3; bays / face frames / doors come later.
        """
        if self.default_corner_type == 'PIE_CUT':
            self._build_pie_cut_parts()
        elif self.default_corner_type == 'DIAGONAL':
            self._build_diagonal_parts()
        else:
            raise NotImplementedError(
                f"Corner type {self.default_corner_type!r} not yet supported")

    def _build_pie_cut_parts(self):
        """Create the pie cut carcass parts. Dimensions and positions
        are written by _recalculate_pie_cut so per-prop updates keep
        them in sync.
        """
        # Bottom: solid panel + corner-notch boolean for the L-cut.
        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.obj['hb_part_role'] = PART_ROLE_CORNER_BOTTOM
        bottom.obj['CABINET_PART'] = True
        bottom.obj.rotation_euler.z = math.radians(-90)
        b_notch = bottom.add_part_modifier('CPM_CORNERNOTCH', 'Front Notch')
        b_notch.set_input('Flip X', True)
        b_notch.set_input('Flip Y', True)
        b_notch.mod.show_viewport = True
        b_notch.mod.show_render = True

        # Top: same construction as bottom (no stretchers for pie cut).
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.obj['hb_part_role'] = PART_ROLE_CORNER_TOP
        top.obj['CABINET_PART'] = True
        top.obj.rotation_euler.z = math.radians(-90)
        t_notch = top.add_part_modifier('CPM_CORNERNOTCH', 'Front Notch')
        t_notch.set_input('Flip X', True)
        t_notch.set_input('Flip Y', True)
        t_notch.mod.show_viewport = True
        t_notch.mod.show_render = True

        # Left Back: rectangular panel along the X=0 wall.
        left_back = CabinetPart()
        left_back.create('Left Back')
        left_back.obj.parent = self.obj
        left_back.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_BACK
        left_back.obj['CABINET_PART'] = True
        left_back.obj.rotation_euler.y = math.radians(-90)
        left_back.set_input('Mirror Y', True)
        left_back.set_input('Mirror Z', True)
        left_back.set_input('Mirror Z', True)

        # Right Back: rectangular panel along the Y=0 wall.
        right_back = CabinetPart()
        right_back.create('Right Back')
        right_back.obj.parent = self.obj
        right_back.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_BACK
        right_back.obj['CABINET_PART'] = True
        right_back.obj.rotation_euler.y = math.radians(-90)
        right_back.obj.rotation_euler.z = math.radians(-90)
        right_back.set_input('Mirror Z', True)
        right_back.set_input('Mirror Z', True)

        # Left Side: perpendicular stub framing the door opening. Carries
        # a front-bottom corner notch for kick clearance, gated in recalc
        # on toe-kick presence.
        left_side = CabinetPart()
        left_side.create('Left Side')
        left_side.obj.parent = self.obj
        left_side.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_SIDE
        left_side.obj['CABINET_PART'] = True
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.obj.rotation_euler.z = math.radians(-90)
        ls_notch = left_side.add_part_modifier(
            'CPM_CORNERNOTCH', 'Notch Front Bottom')
        ls_notch.set_input('Flip X', False)
        ls_notch.set_input('Flip Y', True)
        ls_notch.mod.show_viewport = False
        ls_notch.mod.show_render = False

        # Right Side: mirror of left side.
        right_side = CabinetPart()
        right_side.create('Right Side')
        right_side.obj.parent = self.obj
        right_side.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_SIDE
        right_side.obj['CABINET_PART'] = True
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.obj.rotation_euler.z = math.radians(180)
        right_side.set_input('Mirror Z', True)
        rs_notch = right_side.add_part_modifier(
            'CPM_CORNERNOTCH', 'Notch Front Bottom')
        rs_notch.set_input('Flip X', False)
        rs_notch.set_input('Flip Y', True)
        rs_notch.mod.show_viewport = False
        rs_notch.mod.show_render = False

        # Kicks (Base / Tall only). Created up front so a later
        # cabinet_type change can show / hide via the recalc path
        # without rebuilding parts.
        if self._has_toe_kick():
            left_kick = CabinetPart()
            left_kick.create('Left Kick')
            left_kick.obj.parent = self.obj
            left_kick.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_KICK
            left_kick.obj['CABINET_PART'] = True
            left_kick.obj.rotation_euler.x = math.radians(-90)
            left_kick.obj.rotation_euler.z = math.radians(90)
            left_kick.set_input('Mirror Y', True)

            right_kick = CabinetPart()
            right_kick.create('Right Kick')
            right_kick.obj.parent = self.obj
            right_kick.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_KICK
            right_kick.obj['CABINET_PART'] = True
            right_kick.obj.rotation_euler.x = math.radians(-90)
            right_kick.obj.rotation_euler.z = math.radians(180)
            right_kick.set_input('Mirror Y', True)
            right_kick.set_input('Mirror Z', True)

            # Finish toe kick: 0.25" cosmetic facing applied to the
            # front of each kick subfront. Same orientation as the
            # subfront; recalc shifts the position forward by
            # finish_thickness so the finish kick's back face is
            # flush with the subfront's front. Hidden in recalc when
            # include_finish_toe_kick is off.
            left_finish = CabinetPart()
            left_finish.create('Left Finish Kick')
            left_finish.obj.parent = self.obj
            left_finish.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_FINISH_KICK
            left_finish.obj['CABINET_PART'] = True
            left_finish.obj.rotation_euler.x = math.radians(-90)
            left_finish.obj.rotation_euler.z = math.radians(90)
            left_finish.set_input('Mirror Y', True)

            right_finish = CabinetPart()
            right_finish.create('Right Finish Kick')
            right_finish.obj.parent = self.obj
            right_finish.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_FINISH_KICK
            right_finish.obj['CABINET_PART'] = True
            right_finish.obj.rotation_euler.x = math.radians(-90)
            right_finish.obj.rotation_euler.z = math.radians(180)
            right_finish.set_input('Mirror Y', True)
            right_finish.set_input('Mirror Z', True)

        # Face frame: two FFs meeting at the inside corner of the L.
        # Each FF has one stile (on the inside-corner edge), one top
        # rail, one bottom rail. Standard hb_part_role values plus an
        # hb_face_frame_side tag so selection-mode part filters keep
        # working without doubling the role enum. Asymmetric joint:
        # right FF is exposed (its rails are fft longer); left FF tucks.

        left_stile = CabinetPart()
        left_stile.create('Left Stile')
        left_stile.obj.parent = self.obj
        left_stile.obj['hb_part_role'] = ff.PART_ROLE_LEFT_STILE
        left_stile.obj['hb_face_frame_side'] = 'LEFT'
        left_stile.obj['CABINET_PART'] = True
        left_stile.obj.rotation_euler.y = math.radians(-90)
        left_stile.obj.rotation_euler.z = math.radians(180)
        left_stile.set_input('Mirror Y', True)

        right_stile = CabinetPart()
        right_stile.create('Right Stile')
        right_stile.obj.parent = self.obj
        right_stile.obj['hb_part_role'] = ff.PART_ROLE_RIGHT_STILE
        right_stile.obj['hb_face_frame_side'] = 'RIGHT'
        right_stile.obj['CABINET_PART'] = True
        right_stile.obj.rotation_euler.y = math.radians(-90)
        right_stile.obj.rotation_euler.z = math.radians(90)

        left_top_rail = CabinetPart()
        left_top_rail.create('Left Top Rail')
        left_top_rail.obj.parent = self.obj
        left_top_rail.obj['hb_part_role'] = ff.PART_ROLE_TOP_RAIL
        left_top_rail.obj['hb_face_frame_side'] = 'LEFT'
        left_top_rail.obj['CABINET_PART'] = True
        left_top_rail.obj.rotation_euler.x = math.radians(-90)
        left_top_rail.obj.rotation_euler.z = math.radians(90)
        left_top_rail.set_input('Mirror Z', True)

        right_top_rail = CabinetPart()
        right_top_rail.create('Right Top Rail')
        right_top_rail.obj.parent = self.obj
        right_top_rail.obj['hb_part_role'] = ff.PART_ROLE_TOP_RAIL
        right_top_rail.obj['hb_face_frame_side'] = 'RIGHT'
        right_top_rail.obj['CABINET_PART'] = True
        right_top_rail.obj.rotation_euler.x = math.radians(-90)
        right_top_rail.obj.rotation_euler.z = math.radians(180)

        left_bot_rail = CabinetPart()
        left_bot_rail.create('Left Bottom Rail')
        left_bot_rail.obj.parent = self.obj
        left_bot_rail.obj['hb_part_role'] = ff.PART_ROLE_BOTTOM_RAIL
        left_bot_rail.obj['hb_face_frame_side'] = 'LEFT'
        left_bot_rail.obj['CABINET_PART'] = True
        left_bot_rail.obj.rotation_euler.x = math.radians(-90)
        left_bot_rail.obj.rotation_euler.z = math.radians(90)
        left_bot_rail.set_input('Mirror Y', True)
        left_bot_rail.set_input('Mirror Z', True)

        right_bot_rail = CabinetPart()
        right_bot_rail.create('Right Bottom Rail')
        right_bot_rail.obj.parent = self.obj
        right_bot_rail.obj['hb_part_role'] = ff.PART_ROLE_BOTTOM_RAIL
        right_bot_rail.obj['hb_face_frame_side'] = 'RIGHT'
        right_bot_rail.obj['CABINET_PART'] = True
        right_bot_rail.obj.rotation_euler.x = math.radians(-90)
        right_bot_rail.obj.rotation_euler.z = math.radians(180)
        right_bot_rail.set_input('Mirror Y', True)

        # Doors. One per face frame, parented directly to the cabinet
        # root (no opening tree). Same hb_part_role + side tag pattern
        # as the rails so existing PART_ROLE_DOOR filters keep working.
        # Orientation matches the corresponding stile so the door's
        # face is parallel to its face frame plane.
        left_door = CabinetPart()
        left_door.create('Left Door')
        left_door.obj.parent = self.obj
        left_door.obj['hb_part_role'] = ff.PART_ROLE_DOOR
        left_door.obj['hb_face_frame_side'] = 'LEFT'
        left_door.obj['CABINET_PART'] = True
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.obj.rotation_euler.z = math.radians(180)
        left_door.set_input('Mirror Y', True)

        right_door = CabinetPart()
        right_door.create('Right Door')
        right_door.obj.parent = self.obj
        right_door.obj['hb_part_role'] = ff.PART_ROLE_DOOR
        right_door.obj['hb_face_frame_side'] = 'RIGHT'
        right_door.obj['CABINET_PART'] = True
        right_door.obj.rotation_euler.y = math.radians(-90)
        right_door.obj.rotation_euler.z = math.radians(90)

    # -----------------------------------------------------------------
    # Diagonal corner: build
    # -----------------------------------------------------------------
    def _build_diagonal_parts(self):
        """Create the diagonal carcass parts plus the boolean cutter
        object. The cutter is a child of the cabinet root carrying a
        GeoNodeCage; Bottom, Top, and both Sides hold a Blender
        BOOLEAN DIFFERENCE modifier referencing it. Backs are at the
        wall planes and aren't cut. Slice 1 scope: carcass-only - face
        frame, doors, kicks, interior come in subsequent slices.
        """
        # Cutter must exist before the parts that reference it.
        cutter = GeoNodeCage()
        cutter.create('Diagonal Cutter')
        cutter.obj.parent = self.obj
        cutter.obj['hb_part_role'] = PART_ROLE_DIAGONAL_CUTTER
        # Show Cage must be True or the geo node group emits no
        # geometry and the Boolean has nothing to subtract. hide_view-
        # port keeps the wireframe out of the artist's way; Booleans
        # read modifier data directly so the operation is unaffected.
        cutter.set_input('Show Cage', True)
        cutter.obj.hide_viewport = True
        cutter_obj = cutter.obj

        # Root chamfer: same Boolean DIFFERENCE the carcass parts use,
        # applied to the root cage so its silhouette becomes a pentagon
        # (chamfered rectangle) rather than the rectangular bounding box
        # produced by Dim X / Dim Y alone. Replaces the corner notch
        # modifier used for pie cut.
        root_cut = self.obj.modifiers.new(name='Diagonal Cut', type='BOOLEAN')
        root_cut.operation = 'DIFFERENCE'
        root_cut.object = cutter_obj

        # Side cutter: identical orientation and Y / Z extent to the
        # main diagonal cutter, but with no margin extension along the
        # unit_AB direction. cage_x is set in recalc to exactly diag_len
        # so the cut lands precisely at the FF stile edges instead of
        # overshooting past A and B by `margin` and shaving the wall-
        # side ends of the side panels.
        side_cutter = GeoNodeCage()
        side_cutter.create('Side Cutter')
        side_cutter.obj.parent = self.obj
        side_cutter.obj['hb_part_role'] = PART_ROLE_DIAGONAL_SIDE_CUTTER
        side_cutter.set_input('Show Cage', True)
        side_cutter.obj.hide_viewport = True
        side_cutter_obj = side_cutter.obj

        def add_diagonal_cut(part):
            mod = part.obj.modifiers.new(name='Diagonal Cut', type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.object = cutter_obj

        def add_side_cut(part):
            mod = part.obj.modifiers.new(name='Diagonal Cut', type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.object = side_cutter_obj

        # Bottom + Top: rectangular panels, no Front Notch (boolean
        # cutter handles the diagonal face). Mirror Y so the panel
        # extends in -Y from origin same as pie cut.
        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.obj['hb_part_role'] = PART_ROLE_CORNER_BOTTOM
        bottom.obj['CABINET_PART'] = True
        bottom.set_input('Mirror Y', True)
        add_diagonal_cut(bottom)

        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.obj['hb_part_role'] = PART_ROLE_CORNER_TOP
        top.obj['CABINET_PART'] = True
        top.set_input('Mirror Y', True)
        add_diagonal_cut(top)

        # Backs: at the X=0 and Y=0 walls. Same orientation as pie
        # cut. No boolean cut - the diagonal cutter doesn't reach the
        # wall planes.
        left_back = CabinetPart()
        left_back.create('Left Back')
        left_back.obj.parent = self.obj
        left_back.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_BACK
        left_back.obj['CABINET_PART'] = True
        left_back.obj.rotation_euler.y = math.radians(-90)
        left_back.set_input('Mirror Y', True)
        left_back.set_input('Mirror Z', True)

        right_back = CabinetPart()
        right_back.create('Right Back')
        right_back.obj.parent = self.obj
        right_back.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_BACK
        right_back.obj['CABINET_PART'] = True
        right_back.obj.rotation_euler.y = math.radians(-90)
        right_back.obj.rotation_euler.z = math.radians(-90)
        right_back.set_input('Mirror Z', True)

        # Sides: same orientation as pie cut. The diagonal cutter
        # carves the angled inside-corner end. Kick clearance notch
        # comes in the toe-kick slice.
        left_side = CabinetPart()
        left_side.create('Left Side')
        left_side.obj.parent = self.obj
        left_side.obj['hb_part_role'] = PART_ROLE_CORNER_LEFT_SIDE
        left_side.obj['CABINET_PART'] = True
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.obj.rotation_euler.z = math.radians(-90)
        ls_notch = left_side.add_part_modifier(
            'CPM_CORNERNOTCH', 'Notch Front Bottom')
        ls_notch.set_input('Flip X', False)
        ls_notch.set_input('Flip Y', True)
        ls_notch.mod.show_viewport = False
        ls_notch.mod.show_render = False
        add_side_cut(left_side)

        right_side = CabinetPart()
        right_side.create('Right Side')
        right_side.obj.parent = self.obj
        right_side.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_SIDE
        right_side.obj['CABINET_PART'] = True
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.obj.rotation_euler.z = math.radians(180)
        right_side.set_input('Mirror Z', True)
        rs_notch = right_side.add_part_modifier(
            'CPM_CORNERNOTCH', 'Notch Front Bottom')
        rs_notch.set_input('Flip X', False)
        rs_notch.set_input('Flip Y', True)
        rs_notch.mod.show_viewport = False
        rs_notch.mod.show_render = False
        add_side_cut(right_side)

        # Face frame parts. Single face frame on the diagonal plane:
        # left + right stiles at A and B (the diagonal endpoints on the
        # left and right arm front faces), bottom and top rails butting
        # between them. Build sets the standard cabinet stile / bay
        # mid-rail orientations; recalc overrides rotation_euler.z to
        # add the diagonal angle theta and positions origins from
        # cab_props. hb_face_frame_side='DIAGONAL' disambiguates these
        # from any future per-side parts and keeps _find_ff_part queries
        # consistent with the pie cut convention.
        left_stile = CabinetPart()
        left_stile.create('Left Stile')
        left_stile.obj.parent = self.obj
        left_stile.obj['hb_part_role'] = ff.PART_ROLE_LEFT_STILE
        left_stile.obj['hb_face_frame_side'] = 'DIAGONAL'
        left_stile.obj['CABINET_PART'] = True
        left_stile.obj.rotation_euler.y = math.radians(-90)
        left_stile.obj.rotation_euler.z = math.radians(90)
        left_stile.set_input('Mirror Y', True)
        left_stile.set_input('Mirror Z', True)

        right_stile = CabinetPart()
        right_stile.create('Right Stile')
        right_stile.obj.parent = self.obj
        right_stile.obj['hb_part_role'] = ff.PART_ROLE_RIGHT_STILE
        right_stile.obj['hb_face_frame_side'] = 'DIAGONAL'
        right_stile.obj['CABINET_PART'] = True
        right_stile.obj.rotation_euler.y = math.radians(-90)
        right_stile.obj.rotation_euler.z = math.radians(90)
        right_stile.set_input('Mirror Y', False)
        right_stile.set_input('Mirror Z', True)

        bot_rail = CabinetPart()
        bot_rail.create('Bottom Rail')
        bot_rail.obj.parent = self.obj
        bot_rail.obj['hb_part_role'] = ff.PART_ROLE_BOTTOM_RAIL
        bot_rail.obj['hb_face_frame_side'] = 'DIAGONAL'
        bot_rail.obj['CABINET_PART'] = True
        bot_rail.obj.rotation_euler.x = math.radians(90)
        bot_rail.set_input('Mirror Z', True)

        top_rail = CabinetPart()
        top_rail.create('Top Rail')
        top_rail.obj.parent = self.obj
        top_rail.obj['hb_part_role'] = ff.PART_ROLE_TOP_RAIL
        top_rail.obj['hb_face_frame_side'] = 'DIAGONAL'
        top_rail.obj['CABINET_PART'] = True
        top_rail.obj.rotation_euler.x = math.radians(90)
        top_rail.set_input('Mirror Z', True)

        # Toe kick subfront on the diagonal. Created only on cabinet
        # types with a kick (Base / Tall) - same gating as pie cut.
        if self._has_toe_kick():
            diag_kick = CabinetPart()
            diag_kick.create('Diagonal Toe Kick')
            diag_kick.obj.parent = self.obj
            diag_kick.obj['hb_part_role'] = PART_ROLE_DIAGONAL_KICK
            diag_kick.obj['CABINET_PART'] = True
            diag_kick.obj.rotation_euler.x = math.radians(90)
            diag_kick.set_input('Mirror Z', True)

    # -----------------------------------------------------------------
    # Recalculate (overrides FaceFrameCabinet.recalculate)
    # -----------------------------------------------------------------
    def recalculate(self):
        """Corner cabinet recalc. Drives root cage dimensions, root
        corner notch, and corner-shape-specific carcass parts directly
        from cab_props. Bypasses the standard FaceFrameCabinet
        reconciliation methods (which assume rectangular geometry).
        """
        cab_props = self.obj.face_frame_cabinet
        self.set_input('Dim X', cab_props.width)
        self.set_input('Dim Y', cab_props.depth)
        self.set_input('Dim Z', cab_props.height)
        if cab_props.corner_type == 'PIE_CUT':
            self._update_root_corner_notch()
            self._recalculate_pie_cut()
        elif cab_props.corner_type == 'DIAGONAL':
            self._recalculate_diagonal()

    def _recalculate_pie_cut(self):
        """Write dimensions and positions to all pie cut carcass parts
        from cab_props. Backs and sides shift up by (kick_height + brw)
        on Base/Tall; Bottom sits at top of toe kick area; Top sits at
        height - t. Side lengths drive from left_depth / right_depth.
        Bottom and Top notches eat the front-corner volume to give the
        L-shape from a rectangular panel. Side front-bottom notches
        (kick clearance) are show/hide-gated on toe-kick presence.
        """
        cab_props = self.obj.face_frame_cabinet
        width = cab_props.width
        depth = cab_props.depth
        height = cab_props.height
        ld = cab_props.left_depth
        rd = cab_props.right_depth
        t = cab_props.material_thickness
        fft = cab_props.face_frame_thickness
        brw = cab_props.bottom_rail_width
        has_kick = self._has_toe_kick()
        kick_height = cab_props.toe_kick_height if has_kick else 0.0
        kick_setback = cab_props.toe_kick_setback

        # Slice 3 has no face frame yet, so overlays are zero and
        # finished ends are off. These plug into the reference formulas
        # in the same way IF(lfe, 0, fflo) would.
        fflo = 0.0
        ffro = 0.0

        # Scribe: hold the carcass back from the walls. left_scribe
        # shifts the X=0 wall plane to X=left_scribe; right_scribe
        # shifts the Y=0 wall plane to Y=-right_scribe. Face frames,
        # kicks, doors are anchored to the inside-corner edges (X=ld,
        # Y=-rd) and are unaffected.
        l_scribe = cab_props.left_scribe
        r_scribe = cab_props.right_scribe

        z_back_floor = (kick_height + brw) if has_kick else brw
        z_bottom = (kick_height + brw - t) if has_kick else (brw - t)
        z_top = height - t

        parts = _children_by_corner_role(self.obj)

        bottom = parts.get(PART_ROLE_CORNER_BOTTOM)
        if bottom is not None:
            # Backs and walls don't move with scribe - origin stays at
            # (0, 0). Length axis is along Y so l_scribe (Left Side's
            # +Y shift) shrinks Length and the Y-direction notch dim.
            # Width axis is along X so r_scribe shrinks Width and the
            # X-direction notch dim. Inside-corner edges (rd, ld) are
            # face-frame anchored and don't move.
            bottom.location = (0.0, 0.0, z_bottom)
            _set_mod_inputs(bottom, bottom.home_builder.mod_name, (
                ('Length', depth - t - fflo - l_scribe),
                ('Width', width - t - ffro - r_scribe),
                ('Thickness', t),
            ))
            _set_mod_inputs(bottom, 'Front Notch', (
                ('X', depth - rd + fft - t - fflo - l_scribe),
                ('Y', width - ld + fft - t - ffro - r_scribe),
                ('Route Depth', inch(0.76)),
            ))

        top = parts.get(PART_ROLE_CORNER_TOP)
        if top is not None:
            top.location = (0.0, 0.0, z_top)
            _set_mod_inputs(top, top.home_builder.mod_name, (
                ('Length', depth - t - fflo - l_scribe),
                ('Width', width - t - ffro - r_scribe),
                ('Thickness', t),
            ))
            _set_mod_inputs(top, 'Front Notch', (
                ('X', depth - rd + fft - t - fflo - l_scribe),
                ('Y', width - ld + fft - t - ffro - r_scribe),
                ('Route Depth', inch(0.76)),
            ))

        left_back = parts.get(PART_ROLE_CORNER_LEFT_BACK)
        if left_back is not None:
            # At X=0 wall (unchanged). Captured in Y between Left
            # Side's shifted back face (Y=-depth+t+fflo+l_scribe) and
            # Right Back's room face (Y=-t), so Width shrinks by
            # l_scribe.
            left_back.location = (0.0, -t, z_back_floor)
            back_height = height - z_back_floor - t
            _set_mod_inputs(left_back, left_back.home_builder.mod_name, (
                ('Length', back_height),
                ('Width', depth - t * 2 - fflo - l_scribe),
                ('Thickness', t),
            ))

        right_back = parts.get(PART_ROLE_CORNER_RIGHT_BACK)
        if right_back is not None:
            # At Y=0 wall (unchanged). Captured in X between origin
            # and Right Side's shifted back face (X=width-t-ffro-
            # r_scribe), so Width shrinks by r_scribe.
            right_back.location = (0.0, 0.0, z_back_floor)
            back_height = height - z_back_floor - t
            _set_mod_inputs(right_back, right_back.home_builder.mod_name, (
                ('Length', back_height),
                ('Width', width - t - ffro - r_scribe),
                ('Thickness', t),
            ))

        left_side = parts.get(PART_ROLE_CORNER_LEFT_SIDE)
        if left_side is not None:
            # l_scribe shifts the side in +Y (away from the face frame
            # outer edge at Y=-depth). The face frame stile - which
            # extends Y=-depth..Y=-depth+lsw - covers the resulting gap
            # so long as l_scribe < lsw - t. Width unchanged.
            left_side.location = (0.0, -depth + fflo + l_scribe, 0.0)
            _set_mod_inputs(left_side, left_side.home_builder.mod_name, (
                ('Length', height),
                ('Width', ld - fft),
                ('Thickness', t),
            ))
            _set_mod_inputs(left_side, 'Notch Front Bottom', (
                ('X', kick_height),
                ('Y', kick_setback),
                ('Route Depth', t),
            ))
            ls_mod = left_side.modifiers.get('Notch Front Bottom')
            if ls_mod is not None:
                ls_mod.show_viewport = has_kick
                ls_mod.show_render = has_kick

        right_side = parts.get(PART_ROLE_CORNER_RIGHT_SIDE)
        if right_side is not None:
            # r_scribe shifts the side in -X (away from the face frame
            # outer edge at X=width). Right stile covers the gap.
            # Width unchanged.
            right_side.location = (width - ffro - r_scribe, 0.0, 0.0)
            _set_mod_inputs(right_side, right_side.home_builder.mod_name, (
                ('Length', height),
                ('Width', rd - fft),
                ('Thickness', t),
            ))
            _set_mod_inputs(right_side, 'Notch Front Bottom', (
                ('X', kick_height),
                ('Y', kick_setback),
                ('Route Depth', t),
            ))
            rs_mod = right_side.modifiers.get('Notch Front Bottom')
            if rs_mod is not None:
                rs_mod.show_viewport = has_kick
                rs_mod.show_render = has_kick

        left_kick = parts.get(PART_ROLE_CORNER_LEFT_KICK)
        if left_kick is not None:
            # Kick origin sits at Left Side's back face, which shifts
            # with l_scribe. Length shrinks by the same amount; the
            # inside-corner end of the kick is anchored to the face
            # frame and doesn't move.
            left_kick.location = (
                ld - fft - kick_setback, -depth + t + fflo + l_scribe, 0.0)
            _set_mod_inputs(left_kick, left_kick.home_builder.mod_name, (
                ('Length',
                 depth - rd + kick_setback + fft - t - fflo - l_scribe),
                ('Width', kick_height),
                ('Thickness', t),
            ))

        right_kick = parts.get(PART_ROLE_CORNER_RIGHT_KICK)
        if right_kick is not None:
            # Mirror of left: origin at Right Side's back face which
            # shifts with r_scribe; Length shrinks accordingly.
            right_kick.location = (
                width - t - ffro - r_scribe,
                -rd + fft + kick_setback, 0.0)
            _set_mod_inputs(right_kick, right_kick.home_builder.mod_name, (
                ('Length',
                 width - ld + kick_setback + fft - t - ffro - r_scribe),
                ('Width', kick_height),
                ('Thickness', t),
            ))

        # Finish toe kicks: 0.25" facing on the front of each subfront.
        # ft shifts each finish kick forward into the room by its own
        # thickness; Length shrinks by ft so both finish kicks meet at
        # the (slightly forward) inside corner of the finish-kick plane.
        ft = cab_props.finish_toe_kick_thickness
        finish_visible = has_kick and cab_props.include_finish_toe_kick

        left_finish = parts.get(PART_ROLE_CORNER_LEFT_FINISH_KICK)
        if left_finish is not None:
            left_finish.hide_viewport = not finish_visible
            left_finish.hide_render = not finish_visible
            if finish_visible:
                # Origin at Y = -depth + fflo (the front face of the
                # side, room side) instead of -depth + t + fflo (back
                # face). Length grows by t so the panel still ends at
                # the finish-kick inside corner. Without this the kick
                # recess exposed by the side notch is not covered for
                # the front-t slice.
                left_finish.location = (
                    ld - fft - kick_setback + ft,
                    -depth + fflo, 0.0)
                _set_mod_inputs(
                    left_finish, left_finish.home_builder.mod_name, (
                        ('Length',
                         depth - rd + kick_setback + fft - fflo - ft),
                        ('Width', kick_height),
                        ('Thickness', ft),
                    ))

        right_finish = parts.get(PART_ROLE_CORNER_RIGHT_FINISH_KICK)
        if right_finish is not None:
            right_finish.hide_viewport = not finish_visible
            right_finish.hide_render = not finish_visible
            if finish_visible:
                # Mirror of left: origin at X = width - ffro (front face
                # of right side) instead of width - t - ffro (back face);
                # Length grows by t to keep the inside-corner end fixed.
                right_finish.location = (
                    width - ffro,
                    -rd + fft + kick_setback - ft, 0.0)
                _set_mod_inputs(
                    right_finish, right_finish.home_builder.mod_name, (
                        ('Length',
                         width - ld + kick_setback + fft - ffro - ft),
                        ('Width', kick_height),
                        ('Thickness', ft),
                    ))

        # ---- Face frame -------------------------------------------------
        # Stile heights span height - kick_height on Base/Tall (kick area
        # is exposed below the stile) and full height on Upper. Rails sit
        # at z = kick_height (Base/Tall) or z = 0 (Upper) for the bottom
        # rail; top rails at z = height - trw. Rail Length writes mirror
        # the asymmetric joint: right Length includes +fft so the right
        # FF visually sits proud of the left.
        lsw = cab_props.left_stile_width
        rsw = cab_props.right_stile_width
        trw = cab_props.top_rail_width
        brw_ff = cab_props.bottom_rail_width
        z_ff_floor = kick_height if has_kick else 0.0
        stile_length = height - kick_height if has_kick else height

        left_stile = _find_ff_part(self.obj, ff.PART_ROLE_LEFT_STILE, 'LEFT')
        if left_stile is not None:
            left_stile.location = (ld - fft, -depth, z_ff_floor)
            _set_mod_inputs(left_stile, left_stile.home_builder.mod_name, (
                ('Length', stile_length),
                ('Width', lsw),
                ('Thickness', fft),
            ))

        right_stile = _find_ff_part(self.obj, ff.PART_ROLE_RIGHT_STILE, 'RIGHT')
        if right_stile is not None:
            right_stile.location = (width, -rd + fft, z_ff_floor)
            _set_mod_inputs(right_stile, right_stile.home_builder.mod_name, (
                ('Length', stile_length),
                ('Width', rsw),
                ('Thickness', fft),
            ))

        left_top_rail = _find_ff_part(self.obj, ff.PART_ROLE_TOP_RAIL, 'LEFT')
        if left_top_rail is not None:
            left_top_rail.location = (ld - fft, -depth + lsw, height)
            _set_mod_inputs(left_top_rail, left_top_rail.home_builder.mod_name, (
                ('Length', depth - rd - lsw),
                ('Width', trw),
                ('Thickness', fft),
            ))

        right_top_rail = _find_ff_part(self.obj, ff.PART_ROLE_TOP_RAIL, 'RIGHT')
        if right_top_rail is not None:
            right_top_rail.location = (width - rsw, -rd + fft, height)
            _set_mod_inputs(right_top_rail, right_top_rail.home_builder.mod_name, (
                ('Length', width - ld - lsw + fft),
                ('Width', trw),
                ('Thickness', fft),
            ))

        left_bot_rail = _find_ff_part(self.obj, ff.PART_ROLE_BOTTOM_RAIL, 'LEFT')
        if left_bot_rail is not None:
            left_bot_rail.location = (ld - fft, -depth + lsw, z_ff_floor)
            _set_mod_inputs(left_bot_rail, left_bot_rail.home_builder.mod_name, (
                ('Length', depth - rd - lsw),
                ('Width', brw_ff),
                ('Thickness', fft),
            ))

        right_bot_rail = _find_ff_part(self.obj, ff.PART_ROLE_BOTTOM_RAIL, 'RIGHT')
        if right_bot_rail is not None:
            right_bot_rail.location = (width - rsw, -rd + fft, z_ff_floor)
            _set_mod_inputs(right_bot_rail, right_bot_rail.home_builder.mod_name, (
                ('Length', width - ld - lsw + fft),
                ('Width', brw_ff),
                ('Thickness', fft),
            ))

        # ---- Doors -----------------------------------------------------
        # Door spans the opening between top / bottom rails plus top and
        # bottom overlays (vertical Length); along the face frame, it
        # spans from the stile edge to the inside corner, less one
        # door thickness so the opposing door can sit proud at the
        # corner. Stile-side gets a single overlay; inside-corner side
        # is a butt joint with the perpendicular face frame so no
        # overlay on that end. Pivot / swing animation isn't wired in
        # this slice - doors sit at their closed position.
        dt = cab_props.door_thickness
        top_ov = cab_props.default_top_overlay
        bot_ov = cab_props.default_bottom_overlay
        left_ov = cab_props.default_left_overlay
        right_ov = cab_props.default_right_overlay
        door_length = (height - kick_height - trw - brw_ff + top_ov + bot_ov
                       if has_kick
                       else height - trw - brw_ff + top_ov + bot_ov)
        z_door = ((kick_height + brw_ff - bot_ov) if has_kick
                  else (brw_ff - bot_ov))

        left_door = _find_ff_part(self.obj, ff.PART_ROLE_DOOR, 'LEFT')
        if left_door is not None:
            left_door.location = (ld, -depth + lsw - left_ov, z_door)
            _set_mod_inputs(left_door, left_door.home_builder.mod_name, (
                ('Length', door_length),
                ('Width', depth - rd - lsw - dt + left_ov),
                ('Thickness', dt),
            ))

        right_door = _find_ff_part(self.obj, ff.PART_ROLE_DOOR, 'RIGHT')
        if right_door is not None:
            right_door.location = (width - rsw + right_ov, -rd, z_door)
            _set_mod_inputs(right_door, right_door.home_builder.mod_name, (
                ('Length', door_length),
                ('Width', width - ld - rsw - dt + right_ov),
                ('Thickness', dt),
            ))

    # -----------------------------------------------------------------
    # Diagonal corner: recalculate
    # -----------------------------------------------------------------
    def _recalculate_diagonal(self):
        """Drive dimensions and positions for diagonal carcass parts
        plus the boolean cutter. The cutter sits at the midpoint of
        the diagonal cut line A=(ld, -depth) -> B=(width, -rd),
        rotated so its local +Y points toward the room corner. With
        Mirror X=True the cage extends symmetrically along the
        diagonal direction; +Y carves the triangular wedge between
        the diagonal line and the room outer corner. Scribe support
        and the kick clearance notch on the sides are deferred to
        their own slices so the carcass-only pass stays focused.
        """
        cab_props = self.obj.face_frame_cabinet
        width = cab_props.width
        depth = cab_props.depth
        height = cab_props.height
        ld = cab_props.left_depth
        rd = cab_props.right_depth
        t = cab_props.material_thickness
        brw = cab_props.bottom_rail_width
        has_kick = self._has_toe_kick()
        kick_height = cab_props.toe_kick_height if has_kick else 0.0

        # Left / Right scribe = how far the carcass body recedes from
        # the FF diagonal endpoints A (left) and B (right). At scribe=0
        # the carcass meets the FF stile back face exactly; at scribe>0
        # the carcass falls short by that amount, leaving the FF stile
        # to overhang for jobsite trimming. Same semantic as the
        # standard cabinet's Left/Right Scribe prop.
        fflo = cab_props.left_scribe
        ffro = cab_props.right_scribe

        z_back_floor = (kick_height + brw) if has_kick else brw
        z_bottom = (kick_height + brw - t) if has_kick else (brw - t)
        z_top = height - t

        parts = _children_by_corner_role(self.obj)

        # Bottom + Top: full L-bounding rectangles (no notch input -
        # the boolean cutter does the corner cut).
        bottom = parts.get(PART_ROLE_CORNER_BOTTOM)
        if bottom is not None:
            bottom.location = (0.0, 0.0, z_bottom)
            _set_mod_inputs(bottom, bottom.home_builder.mod_name, (
                ('Length', width - t - ffro),
                ('Width', depth - t - fflo),
                ('Thickness', t),
            ))

        top = parts.get(PART_ROLE_CORNER_TOP)
        if top is not None:
            top.location = (0.0, 0.0, z_top)
            _set_mod_inputs(top, top.home_builder.mod_name, (
                ('Length', width - t - ffro),
                ('Width', depth - t - fflo),
                ('Thickness', t),
            ))

        # Backs at wall planes - identical formulas to pie cut.
        left_back = parts.get(PART_ROLE_CORNER_LEFT_BACK)
        if left_back is not None:
            left_back.location = (0.0, -t, z_back_floor)
            back_height = height - z_back_floor - t
            _set_mod_inputs(left_back, left_back.home_builder.mod_name, (
                ('Length', back_height),
                ('Width', depth - t * 2 - fflo),
                ('Thickness', t),
            ))

        right_back = parts.get(PART_ROLE_CORNER_RIGHT_BACK)
        if right_back is not None:
            right_back.location = (0.0, 0.0, z_back_floor)
            back_height = height - z_back_floor - t
            _set_mod_inputs(right_back, right_back.home_builder.mod_name, (
                ('Length', back_height),
                ('Width', width - t - ffro),
                ('Thickness', t),
            ))

        # Sides: at the L-front faces. Diagonal cutter trims the
        # inside-corner end at the 45 deg plane. Width spans the full
        # arm length; the boolean carves whatever crosses the cut.
        left_side = parts.get(PART_ROLE_CORNER_LEFT_SIDE)
        if left_side is not None:
            left_side.location = (0.0, -depth + fflo, 0.0)
            _set_mod_inputs(left_side, left_side.home_builder.mod_name, (
                ('Length', height),
                ('Width', ld + fflo),
                ('Thickness', t),
            ))
            _set_mod_inputs(left_side, 'Notch Front Bottom', (
                ('X', kick_height),
                ('Y', cab_props.toe_kick_setback),
                ('Route Depth', t),
            ))
            ls_mod = left_side.modifiers.get('Notch Front Bottom')
            if ls_mod is not None:
                ls_mod.show_viewport = has_kick
                ls_mod.show_render = has_kick

        right_side = parts.get(PART_ROLE_CORNER_RIGHT_SIDE)
        if right_side is not None:
            right_side.location = (width - ffro, 0.0, 0.0)
            _set_mod_inputs(right_side, right_side.home_builder.mod_name, (
                ('Length', height),
                ('Width', rd + ffro),
                ('Thickness', t),
            ))
            _set_mod_inputs(right_side, 'Notch Front Bottom', (
                ('X', kick_height),
                ('Y', cab_props.toe_kick_setback),
                ('Route Depth', t),
            ))
            rs_mod = right_side.modifiers.get('Notch Front Bottom')
            if rs_mod is not None:
                rs_mod.show_viewport = has_kick
                rs_mod.show_render = has_kick

        # ---- Face frame -------------------------------------------------
        # Face frame parts sit on the diagonal plane. Baseline rotations
        # written at build time are the standard rectangular face frame
        # orientations; here we override rotation_euler.z to add the
        # diagonal angle theta = atan2(depth-rd, width-ld) on top of that
        # baseline. With L=+Z, W=+X (left) / -X (right), T=+Y in the
        # un-rotated frame, applying Rz(theta) gives Width along
        # +/- unit_AB and Thickness along +inward_normal. Stile widths and
        # rail widths come from cab_props - same defaults as the standard
        # face frame cabinet. FF front face is flush with the diagonal
        # carcass cut plane (origin at A for left stile, B for right);
        # thickness extends inward.
        fft = cab_props.face_frame_thickness
        lsw = cab_props.left_stile_width
        rsw = cab_props.right_stile_width
        trw = cab_props.top_rail_width
        brw_ff = cab_props.bottom_rail_width

        diag_dx_ff = width - ld
        diag_dy_ff = depth - rd
        diag_len_ff = math.sqrt(diag_dx_ff * diag_dx_ff
                                + diag_dy_ff * diag_dy_ff)
        ux = diag_dx_ff / diag_len_ff
        uy = diag_dy_ff / diag_len_ff
        theta = math.atan2(diag_dy_ff, diag_dx_ff)

        z_ff_floor = kick_height if has_kick else 0.0
        stile_length = (height - kick_height) if has_kick else height
        rail_length = diag_len_ff - lsw - rsw
        rail_origin_x = ld + lsw * ux
        rail_origin_y = -depth + lsw * uy

        left_stile = _find_ff_part(
            self.obj, ff.PART_ROLE_LEFT_STILE, 'DIAGONAL')
        if left_stile is not None:
            left_stile.location = (ld, -depth, z_ff_floor)
            left_stile.rotation_euler.z = math.radians(90) + theta
            _set_mod_inputs(left_stile, left_stile.home_builder.mod_name, (
                ('Length', stile_length),
                ('Width', lsw),
                ('Thickness', fft),
            ))

        right_stile = _find_ff_part(
            self.obj, ff.PART_ROLE_RIGHT_STILE, 'DIAGONAL')
        if right_stile is not None:
            right_stile.location = (width, -rd, z_ff_floor)
            right_stile.rotation_euler.z = math.radians(90) + theta
            _set_mod_inputs(right_stile, right_stile.home_builder.mod_name, (
                ('Length', stile_length),
                ('Width', rsw),
                ('Thickness', fft),
            ))

        bot_rail = _find_ff_part(
            self.obj, ff.PART_ROLE_BOTTOM_RAIL, 'DIAGONAL')
        if bot_rail is not None:
            bot_rail.location = (rail_origin_x, rail_origin_y, z_ff_floor)
            bot_rail.rotation_euler.z = theta
            _set_mod_inputs(bot_rail, bot_rail.home_builder.mod_name, (
                ('Length', rail_length),
                ('Width', brw_ff),
                ('Thickness', fft),
            ))

        top_rail = _find_ff_part(
            self.obj, ff.PART_ROLE_TOP_RAIL, 'DIAGONAL')
        if top_rail is not None:
            top_rail.location = (rail_origin_x, rail_origin_y, height - trw)
            top_rail.rotation_euler.z = theta
            _set_mod_inputs(top_rail, top_rail.home_builder.mod_name, (
                ('Length', rail_length),
                ('Width', trw),
                ('Thickness', fft),
            ))

        # Toe kick subfront. Spans between the two side panel notch
        # inner corners so the kick fits exactly in the notch setbacks.
        # LEFT corner = (LEFT notch inner X-edge, LEFT panel inner
        # Y-face). RIGHT corner = (RIGHT panel inner X-face, RIGHT
        # notch inner Y-edge). For symmetric corners with matching
        # scribes the resulting line is parallel to A-B (same angle as
        # the FF); for asymmetric cases the kick angle adapts so it
        # connects cleanly to both notches.
        diag_kick = parts.get(PART_ROLE_DIAGONAL_KICK)
        if diag_kick is not None and has_kick:
            kick_setback = cab_props.toe_kick_setback
            kick_left_x = ld + fflo - kick_setback
            kick_left_y = -depth + fflo + t
            kick_right_x = width - ffro - t
            kick_right_y = -(rd + ffro) + kick_setback
            kick_dx = kick_right_x - kick_left_x
            kick_dy = kick_right_y - kick_left_y
            kick_length = math.sqrt(kick_dx * kick_dx + kick_dy * kick_dy)
            kick_angle = math.atan2(kick_dy, kick_dx)
            diag_kick.location = (kick_left_x, kick_left_y, 0.0)
            diag_kick.rotation_euler.z = kick_angle
            _set_mod_inputs(diag_kick, diag_kick.home_builder.mod_name, (
                ('Length', kick_length),
                ('Width', kick_height),
                ('Thickness', t),
            ))

        # Cutter: cage box anchored just behind A=(ld, -depth) along
        # -unit_AB, extending in local -X toward (and past) B=(width,
        # -rd) and in local +Y perpendicular to AB toward the room
        # corner C=(width, -depth). Mirror X=True grows the cage in
        # local -X from origin (NOT centered); Mirror Y/Z=False grow
        # in +Y and +Z. rot_z is chosen so local +Y = unit perpen-
        # dicular to AB (rotated 90 deg CW from unit_AB) which equals
        # (diag_dy, -diag_dx)/diag_len.
        cutter = parts.get(PART_ROLE_DIAGONAL_CUTTER)
        if cutter is not None:
            diag_dx = width - ld
            diag_dy = depth - rd
            diag_len = math.sqrt(diag_dx * diag_dx + diag_dy * diag_dy)
            ux = diag_dx / diag_len
            uy = diag_dy / diag_len
            margin = inch(2.0)
            # Local +Y world dir = (-sin rot_z, cos rot_z). Set it to
            # (diag_dy, -diag_dx)/diag_len -> rot_z = atan2(-dy, -dx).
            rot_z = math.atan2(-diag_dy, -diag_dx)
            # Inward shift by fft: recesses the cut plane behind the
            # diagonal A-B line by face-frame-thickness so carcass
            # parts (Top, Bottom, Sides, root cage) stop at the FF back
            # face instead of overlapping the FF. Inward unit vector
            # is (-uy, ux).
            origin_x = ld - margin * ux - fft * uy
            origin_y = -depth - margin * uy + fft * ux
            cage_x = diag_len + 2.0 * margin
            # Perpendicular distance from line AB to room corner C is
            # (diag_dx * diag_dy) / diag_len (collapses to diag_len/2
            # only when ld == rd). Plus fft to cover the recessed slab
            # between the cut plane and the A-B line; plus margin to
            # cut past the room corner surface.
            cage_y = (diag_dx * diag_dy) / diag_len + fft + margin
            cage_z = height + 2.0 * margin
            cutter.location = (origin_x, origin_y, -margin)
            cutter.rotation_euler = (0.0, 0.0, rot_z)
            _set_mod_inputs(cutter, cutter.home_builder.mod_name, (
                ('Dim X', cage_x),
                ('Dim Y', cage_y),
                ('Dim Z', cage_z),
                ('Mirror X', True),
                ('Mirror Y', False),
                ('Mirror Z', False),
                ('Show Cage', True),
            ))

        # Side cutter: same orientation and Y/Z as the main cutter; X
        # spans exactly the FF width so the cut on the side panels lands
        # right at the FF stile edges. Origin sits at A shifted inward
        # by fft (no margin offset along unit_AB).
        side_cutter = parts.get(PART_ROLE_DIAGONAL_SIDE_CUTTER)
        if side_cutter is not None:
            diag_dx_s = width - ld
            diag_dy_s = depth - rd
            diag_len_s = math.sqrt(diag_dx_s * diag_dx_s
                                   + diag_dy_s * diag_dy_s)
            ux_s = diag_dx_s / diag_len_s
            uy_s = diag_dy_s / diag_len_s
            margin_s = inch(2.0)
            rot_z_s = math.atan2(-diag_dy_s, -diag_dx_s)
            side_origin_x = ld - fft * uy_s
            side_origin_y = -depth + fft * ux_s
            side_cage_x = diag_len_s
            side_cage_y = (diag_dx_s * diag_dy_s) / diag_len_s + fft + margin_s
            side_cage_z = height + 2.0 * margin_s
            side_cutter.location = (side_origin_x, side_origin_y, -margin_s)
            side_cutter.rotation_euler = (0.0, 0.0, rot_z_s)
            _set_mod_inputs(side_cutter,
                            side_cutter.home_builder.mod_name, (
                ('Dim X', side_cage_x),
                ('Dim Y', side_cage_y),
                ('Dim Z', side_cage_z),
                ('Mirror X', True),
                ('Mirror Y', False),
                ('Mirror Z', False),
                ('Show Cage', True),
            ))


# ---------------------------------------------------------------------------
# Size variants
# ---------------------------------------------------------------------------
class BasePieCutCabinet(CornerFaceFrameCabinet):
    """Base height pie cut corner cabinet (toe kick present)."""
    default_corner_type = 'PIE_CUT'
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            # Outer bounding square uses the corner-specific scene prop
            # rather than the standard base_cabinet_depth (which is the
            # rectangular cabinet's depth, not the corner's diagonal).
            self.default_width = props.base_inside_corner_size
            self.default_depth = props.base_inside_corner_size
            self.default_height = props.base_cabinet_height
            self.default_left_depth = props.base_cabinet_depth
            self.default_right_depth = props.base_cabinet_depth

    def create(self, name="Pie Cut Base", bay_qty=1):
        super().create(name=name, bay_qty=bay_qty)


class UpperPieCutCabinet(CornerFaceFrameCabinet):
    """Upper / wall pie cut corner cabinet (no toe kick)."""
    default_corner_type = 'PIE_CUT'
    default_cabinet_type = 'UPPER'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            # Outer bounding square uses the corner-specific scene prop
            # rather than the standard upper_cabinet_depth (which is the
            # rectangular cabinet's depth, not the corner's diagonal).
            self.default_width = props.upper_inside_corner_size
            self.default_depth = props.upper_inside_corner_size
            self.default_height = props.upper_cabinet_height
            self.default_left_depth = props.upper_cabinet_depth
            self.default_right_depth = props.upper_cabinet_depth

    def create(self, name="Pie Cut Upper", bay_qty=1):
        super().create(name=name, bay_qty=bay_qty)
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            self.obj.location.z = scene.hb_face_frame.default_wall_cabinet_location


class BaseDiagonalCabinet(CornerFaceFrameCabinet):
    """Base height diagonal corner cabinet (45 deg front face)."""
    default_corner_type = 'DIAGONAL'
    default_cabinet_type = 'BASE'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.base_inside_corner_size
            self.default_depth = props.base_inside_corner_size
            self.default_height = props.base_cabinet_height
            self.default_left_depth = props.base_cabinet_depth
            self.default_right_depth = props.base_cabinet_depth


# ---------------------------------------------------------------------------
# Dispatch (mutates registries in types_face_frame at import)
# ---------------------------------------------------------------------------
# CABINET_NAME_DISPATCH: catalog name -> subclass for catalog draw flow.
ff.CABINET_NAME_DISPATCH.update({
    "Pie Cut Base": BasePieCutCabinet,
    "Pie Cut Upper": UpperPieCutCabinet,
    "Diagonal Base": BaseDiagonalCabinet,
})

# WRAP_CLASS_REGISTRY: CLASS_NAME -> subclass for the prop-update wrap.
# Without this, prop writes (width / depth / etc.) would fall back to
# FaceFrameCabinet and run the standard reconcile path, which creates
# stretcher / standard rail / standard back / bottom parts that don't
# belong on a corner cabinet.
ff.WRAP_CLASS_REGISTRY.update({
    'BasePieCutCabinet': BasePieCutCabinet,
    'UpperPieCutCabinet': UpperPieCutCabinet,
    'BaseDiagonalCabinet': BaseDiagonalCabinet,
})
