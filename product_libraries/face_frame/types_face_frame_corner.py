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
from ...hb_types import CabinetPartModifier
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
        self._add_root_corner_notch()

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

        # Right Back: rectangular panel along the Y=0 wall.
        right_back = CabinetPart()
        right_back.create('Right Back')
        right_back.obj.parent = self.obj
        right_back.obj['hb_part_role'] = PART_ROLE_CORNER_RIGHT_BACK
        right_back.obj['CABINET_PART'] = True
        right_back.obj.rotation_euler.y = math.radians(-90)
        right_back.obj.rotation_euler.z = math.radians(-90)
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
        self._update_root_corner_notch()
        if cab_props.corner_type == 'PIE_CUT':
            self._recalculate_pie_cut()

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


# ---------------------------------------------------------------------------
# Dispatch (mutates registries in types_face_frame at import)
# ---------------------------------------------------------------------------
# CABINET_NAME_DISPATCH: catalog name -> subclass for catalog draw flow.
ff.CABINET_NAME_DISPATCH.update({
    "Pie Cut Base": BasePieCutCabinet,
    "Pie Cut Upper": UpperPieCutCabinet,
})

# WRAP_CLASS_REGISTRY: CLASS_NAME -> subclass for the prop-update wrap.
# Without this, prop writes (width / depth / etc.) would fall back to
# FaceFrameCabinet and run the standard reconcile path, which creates
# stretcher / standard rail / standard back / bottom parts that don't
# belong on a corner cabinet.
ff.WRAP_CLASS_REGISTRY.update({
    'BasePieCutCabinet': BasePieCutCabinet,
    'UpperPieCutCabinet': UpperPieCutCabinet,
})
