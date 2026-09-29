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
from types import SimpleNamespace

from ... import hb_utils
from ...units import inch
from ...hb_types import CabinetPartModifier, GeoNodeCage
from ..frameless.types_frameless import CabinetPart
from . import types_face_frame as ff
from . import solver_face_frame as solver
from . import props_hb_face_frame as props_hb


# ---------------------------------------------------------------------------
# Identity tags
# ---------------------------------------------------------------------------
PART_ROLE_CORNER_BOTTOM = 'CORNER_BOTTOM'
PART_ROLE_CORNER_TOP = 'CORNER_TOP'
PART_ROLE_CORNER_LEFT_BACK = 'CORNER_LEFT_BACK'
PART_ROLE_CORNER_RIGHT_BACK = 'CORNER_RIGHT_BACK'
PART_ROLE_CORNER_LEFT_SIDE = 'CORNER_LEFT_SIDE'
PART_ROLE_CORNER_RIGHT_SIDE = 'CORNER_RIGHT_SIDE'
# Interior 45-degree drawer-channel walls (pie cut DRAWER only; the door
# pie cut has none). Distinct roles so they don't collide with the box's
# perpendicular CORNER_LEFT/RIGHT_SIDE panels in _children_by_corner_role.
PART_ROLE_CORNER_CHANNEL_LEFT = 'CORNER_CHANNEL_LEFT'
PART_ROLE_CORNER_CHANNEL_RIGHT = 'CORNER_CHANNEL_RIGHT'
# Hidden cutter cages that let each channel wall into the top / bottom / back.
PART_ROLE_CORNER_CHANNEL_LEFT_CUTTER = 'CORNER_CHANNEL_LEFT_CUTTER'
PART_ROLE_CORNER_CHANNEL_RIGHT_CUTTER = 'CORNER_CHANNEL_RIGHT_CUTTER'
PART_ROLE_CORNER_LEFT_KICK = 'CORNER_LEFT_KICK'
PART_ROLE_CORNER_RIGHT_KICK = 'CORNER_RIGHT_KICK'
PART_ROLE_CORNER_LEFT_FINISH_KICK = 'CORNER_LEFT_FINISH_KICK'
PART_ROLE_CORNER_RIGHT_FINISH_KICK = 'CORNER_RIGHT_FINISH_KICK'
# Loose ladder sub-base (LOOSE / LOOSE_FLUSH): the two existing kick
# boards serve as the front rails along each arm front; these four close
# the L-perimeter frame - a rear rail along each wall plus a short end
# board at each arm's outer end. Built only for BASE/TALL corners and
# shown only when the kick type is LOOSE / LOOSE_FLUSH.
PART_ROLE_CORNER_LOOSE_REAR_LEFT = 'CORNER_LOOSE_REAR_LEFT'
PART_ROLE_CORNER_LOOSE_REAR_RIGHT = 'CORNER_LOOSE_REAR_RIGHT'
PART_ROLE_CORNER_LOOSE_END_LEFT = 'CORNER_LOOSE_END_LEFT'
PART_ROLE_CORNER_LOOSE_END_RIGHT = 'CORNER_LOOSE_END_RIGHT'

# Diagonal-specific roles. The cutter is a child of the cabinet root
# carrying GeoNodeCage geometry; carcass parts that need the 45 degree
# face cut hold a Blender Boolean DIFFERENCE modifier referencing it.
PART_ROLE_DIAGONAL_CUTTER = 'DIAGONAL_CUTTER'
PART_ROLE_DIAGONAL_SIDE_CUTTER = 'DIAGONAL_SIDE_CUTTER'
PART_ROLE_DIAGONAL_KICK = 'DIAGONAL_KICK'
PART_ROLE_CORNER_INTERIOR = 'CORNER_INTERIOR'
PART_ROLE_CORNER_PARTITION = 'CORNER_PARTITION'
PART_ROLE_CORNER_TRAY_DIVIDER = 'CORNER_TRAY_DIVIDER'
PART_ROLE_CORNER_MID_RAIL = 'CORNER_MID_RAIL'
PART_ROLE_CORNER_FALSE_FRONT = 'CORNER_FALSE_FRONT'
PART_ROLE_CORNER_SHELF = 'CORNER_SHELF'
# Fixed shelf at a section boundary (TALL hutch / bookcase): full
# L-bounding panel like Top/Bottom, top face flush with the top of
# its mid rail. Carved by the same Diagonal Cut + Clip Back Cut pair.
PART_ROLE_CORNER_FIXED_SHELF = 'CORNER_FIXED_SHELF'
# Clip-back: a uniform 45 degree chamfer on the rear (wall-corner)
# of any corner cabinet. A GeoNodeCage cutter carves the rear
# corner off the bottom, top, and both backs; an angled back
# panel closes the clip face.
PART_ROLE_CORNER_BACK_CUTTER = 'CORNER_BACK_CUTTER'
PART_ROLE_CORNER_ANGLED_BACK = 'CORNER_ANGLED_BACK'

CORNER_PART_ROLES = frozenset({
    PART_ROLE_CORNER_BOTTOM,
    PART_ROLE_CORNER_TOP,
    PART_ROLE_CORNER_LEFT_BACK,
    PART_ROLE_CORNER_RIGHT_BACK,
    PART_ROLE_CORNER_LEFT_SIDE,
    PART_ROLE_CORNER_RIGHT_SIDE,
    PART_ROLE_CORNER_CHANNEL_LEFT,
    PART_ROLE_CORNER_CHANNEL_RIGHT,
    PART_ROLE_CORNER_CHANNEL_LEFT_CUTTER,
    PART_ROLE_CORNER_CHANNEL_RIGHT_CUTTER,
    PART_ROLE_CORNER_LEFT_KICK,
    PART_ROLE_CORNER_RIGHT_KICK,
    PART_ROLE_CORNER_LEFT_FINISH_KICK,
    PART_ROLE_CORNER_RIGHT_FINISH_KICK,
    PART_ROLE_CORNER_LOOSE_REAR_LEFT,
    PART_ROLE_CORNER_LOOSE_REAR_RIGHT,
    PART_ROLE_CORNER_LOOSE_END_LEFT,
    PART_ROLE_CORNER_LOOSE_END_RIGHT,
    PART_ROLE_DIAGONAL_CUTTER,
    PART_ROLE_DIAGONAL_SIDE_CUTTER,
    PART_ROLE_DIAGONAL_KICK,
    PART_ROLE_CORNER_INTERIOR,
    PART_ROLE_CORNER_PARTITION,
    PART_ROLE_CORNER_BACK_CUTTER,
    PART_ROLE_CORNER_ANGLED_BACK,
})


# Inset (revolving) doors sit inside the face frame opening with this
# gap to the surrounding frame on the rail and stile edges. Overlay
# doors do not use it - they extend over the frame instead.
INSET_DOOR_REVEAL = inch(0.125)


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
        hb_utils.set_gn_input(mod, ni.identifier, value)


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


def _find_corner_part(cab_obj, role, side, section_index):
    """Find a reconciled section part by role + side tag + section index."""
    for c in cab_obj.children:
        if (c.get('hb_part_role') == role
                and c.get('hb_face_frame_side') == side
                and c.get('hb_corner_section_index') == section_index):
            return c
    return None


def _front_gn_dims(front_obj):
    """Read a face-frame front's cutpart (Length, Width, Thickness) GeoNode
    inputs. Returns None if the modifier / inputs aren't present."""
    mod = front_obj.modifiers.get(front_obj.home_builder.mod_name)
    if mod is None or mod.node_group is None:
        return None
    names = {it.name: it.identifier
             for it in mod.node_group.interface.items_tree
             if getattr(it, 'in_out', '') == 'INPUT'}
    try:
        return (hb_utils.get_gn_input(mod, names['Length']),
                hb_utils.get_gn_input(mod, names['Width']),
                hb_utils.get_gn_input(mod, names['Thickness']))
    except (KeyError, AttributeError):
        return None


def _solve_section_heights(sections, available, rail_count, rail_width):
    """Distribute `available` clear FF height across the corner sections.
    Sections with unlock_height hold their stored height; the rest share
    the remainder equally. Mirrors solver_face_frame._redistribute_sizes.
    """
    consumed = rail_count * rail_width
    locked_total = sum(s.height for s in sections if s.unlock_height)
    unlocked = [s for s in sections if not s.unlock_height]
    remainder = available - consumed - locked_total
    share = remainder / len(unlocked) if unlocked else 0.0
    return [s.height if s.unlock_height else share for s in sections]


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
        if self.default_corner_type in ('PIE_CUT', 'PIE_CUT_DRAWER'):
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

    def _corner_kick_flags(self, cab_props):
        """Derive toe-kick presentation flags from toe_kick_type for the
        corner recalc paths. Mirrors the straight-cabinet semantics so all
        five base types work on corners:
          NOTCH    - recessed kick: sides run to the floor with a front-
                     bottom notch, recessed kick boards (+ optional finish
                     kick), FF sits above the kick.
          FLUSH    - no recess: sides to the floor (no notch), no kick
                     boards, FF bottom rail + stiles run to the floor.
          FLOATING - sides float by kick_height, kick left open (no boards
                     or ladder), FF above the kick.
          LOOSE / LOOSE_FLUSH - float like FLOATING; a separate corner
                     ladder sub-base is built by the per-shape recalc
                     (recessed for LOOSE, flush for LOOSE_FLUSH). For the
                     carcass / FF / kick-board flags they read as FLOATING.
        Uppers (no kick) collapse to sides-to-floor, no kick parts.
        """
        has_kick = self._has_toe_kick()
        tk = cab_props.toe_kick_type if has_kick else 'NOTCH'
        return SimpleNamespace(
            has_kick=has_kick,
            tk=tk,
            # Front kick boards are shown for NOTCH (recessed subfront)
            # AND LOOSE / LOOSE_FLUSH (they double as the ladder's front
            # rails along each arm). FLUSH / FLOATING hide them.
            front_rails=has_kick and tk in ('NOTCH', 'LOOSE', 'LOOSE_FLUSH'),
            side_notch=has_kick and tk == 'NOTCH',
            sides_to_floor=(not has_kick) or tk in ('NOTCH', 'FLUSH'),
            ff_to_floor=has_kick and tk == 'FLUSH',
            finish=(has_kick and tk == 'NOTCH'
                    and cab_props.include_finish_toe_kick),
            loose=has_kick and tk in ('LOOSE', 'LOOSE_FLUSH'),
            loose_flush=has_kick and tk == 'LOOSE_FLUSH',
        )

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
        elif self.default_corner_type == 'PIE_CUT_DRAWER':
            self._build_pie_cut_drawer_parts()
        else:
            raise NotImplementedError(
                f"Corner type {self.default_corner_type!r} not yet supported")

    def _build_corner_loose_ladder_parts(self):
        """Create the six LOOSE / LOOSE_FLUSH ladder parts shared by both
        corner shapes: two front kick rails (which also serve as the NOTCH
        recessed subfront on the pie cut) plus the L-perimeter rear rails
        and arm end boards. Orientation: Y-running boards use the Left Kick
        convention (rot X=-90, Z=90, Mirror Y); X-running boards use the
        Right Kick convention (rot X=-90, Z=180, Mirror Y + Mirror Z).
        Positioned / shown by _position_corner_loose_ladder in recalc.
        """
        specs = (
            ('Left Kick',             PART_ROLE_CORNER_LEFT_KICK,        90,  False),
            ('Right Kick',            PART_ROLE_CORNER_RIGHT_KICK,       180, True),
            ('Loose Kick Rear Left',  PART_ROLE_CORNER_LOOSE_REAR_LEFT,  90,  False),
            ('Loose Kick Rear Right', PART_ROLE_CORNER_LOOSE_REAR_RIGHT, 180, True),
            ('Loose Kick End Left',   PART_ROLE_CORNER_LOOSE_END_LEFT,   180, True),
            ('Loose Kick End Right',  PART_ROLE_CORNER_LOOSE_END_RIGHT,  90,  False),
        )
        for name, role, z_deg, mirror_z in specs:
            part = CabinetPart()
            part.create(name)
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = role
            part.obj['CABINET_PART'] = True
            part.obj.rotation_euler.x = math.radians(-90)
            part.obj.rotation_euler.z = math.radians(z_deg)
            part.set_input('Mirror Y', True)
            if mirror_z:
                part.set_input('Mirror Z', True)

    def _build_pie_cut_parts(self):
        """Create the pie cut carcass parts. Dimensions and positions
        are written by _recalculate_pie_cut so per-prop updates keep
        them in sync.
        """
        # Clear any stale section signature. create_cabinet_root sets
        # left_depth / right_depth before the carcass is built, and those
        # prop updates fire a recalc whose section reconcile runs with no
        # parts present. Clearing the signature here forces the real
        # post-build recalc to reconcile sections from scratch.
        self.obj['hb_pie_section_sig'] = ''
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
            self._build_corner_loose_ladder_parts()

            # Finish toe kicks: 0.25" cosmetic facing on each kick subfront
            # (pie-cut NOTCH only; the diagonal uses its diagonal kick).
            # Recalc shifts them forward by finish_thickness and hides them
            # when include_finish_toe_kick is off.
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

        # Doors and section mid rails are reconciled by
        # _reconcile_pie_cut_sections from cab_props.corner_sections -
        # one door per arm per section, mid rails between sections.

        # Tray Compartment partition: interior divider that walls off a
        # tray-storage strip on one leg of an odd-sized pie cut. Always
        # built; recalc shows/hides it and sets the side orientation from
        # cab_props.tray_compartment. Built in the Left Side orientation;
        # recalc re-aims the Z rotation for a right-side compartment.
        partition = CabinetPart()
        partition.create('Tray Partition')
        partition.obj.parent = self.obj
        partition.obj['hb_part_role'] = PART_ROLE_CORNER_PARTITION
        partition.obj['CABINET_PART'] = True
        partition.obj.rotation_euler.y = math.radians(-90)
        partition.obj.rotation_euler.z = math.radians(-90)
        partition.obj.hide_viewport = True
        partition.obj.hide_render = True

        # Tray compartment dividers: up to 10 thin vertical panels that
        # subdivide the tray compartment strip into slots. Pre-built and
        # hidden; recalc shows and evenly spaces the first
        # tray_compartment_qty of them. Parallel to the partition.
        for i in range(10):
            div = CabinetPart()
            div.create('Tray Divider %d' % (i + 1))
            div.obj.parent = self.obj
            div.obj['hb_part_role'] = PART_ROLE_CORNER_TRAY_DIVIDER
            div.obj['hb_corner_divider_index'] = i
            div.obj['CABINET_PART'] = True
            div.obj.rotation_euler.y = math.radians(-90)
            div.obj.rotation_euler.z = math.radians(-90)
            div.obj.hide_viewport = True
            div.obj.hide_render = True

        self._build_clip_back_parts()

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
        # Clear any stale section signature. create_cabinet_root sets
        # left_depth / right_depth before the carcass is built, and those
        # prop updates fire a recalc whose section reconcile runs with no
        # cutters present (shelves end up with no clip booleans). Clearing
        # the signature here forces the real post-build recalc to wipe
        # those premature parts and reconcile from scratch.
        self.obj['hb_diag_section_sig'] = ''
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
            # Loose ladder parts - the same L sub-base as the pie cut.
            # The diagonal kick above is the NOTCH front; these L parts
            # are shown only for LOOSE / LOOSE_FLUSH by the shared
            # positioner (which hides the diagonal kick when loose).
            self._build_corner_loose_ladder_parts()

        # Doors, mid rails, and per-section content are reconciled by
        # _reconcile_diagonal_sections from cab_props.corner_sections;
        # the build creates only the fixed carcass / face frame parts.

        self._build_clip_back_parts()

    def _recalculate_clip_back(self, cab_props, z_back_floor):
        """Position the clip-back cutter and angled back panel.

        The clip is a uniform 45 degree chamfer at the rear (0,0) wall
        corner; clip_back_amount is the leg cut off each wall. The cutter
        is a box whose near face lies on the clip line from (clip, 0) to
        (0, -clip) and which extends toward the corner. When the amount
        is 0 the four clip booleans are disabled and the angled back is
        hidden, so the cabinet is unchanged.
        """
        clip = cab_props.clip_back_amount
        height = cab_props.height
        t = cab_props.material_thickness
        active = clip > 0.0

        # Enable / disable the clip boolean on every part that carries
        # one: the four fixed crossing parts plus any open-section
        # shelves (which span the full carcass and reach the rear
        # corner). Shelves are multi-instance, so match by role on all
        # children rather than the fixed-roles one-per-role lookup.
        clip_roles = {
            PART_ROLE_CORNER_BOTTOM, PART_ROLE_CORNER_TOP,
            PART_ROLE_CORNER_LEFT_BACK, PART_ROLE_CORNER_RIGHT_BACK,
            PART_ROLE_CORNER_SHELF, PART_ROLE_CORNER_FIXED_SHELF,
        }
        for part in self.obj.children:
            if part.get('hb_part_role') not in clip_roles:
                continue
            mod = part.modifiers.get('Clip Back Cut')
            if mod is not None:
                mod.show_viewport = active
                mod.show_render = active

        cutter = next((c for c in self.obj.children
                       if c.get('hb_part_role')
                       == PART_ROLE_CORNER_BACK_CUTTER), None)
        angled = next((c for c in self.obj.children
                       if c.get('hb_part_role')
                       == PART_ROLE_CORNER_ANGLED_BACK), None)

        if not active:
            if angled is not None:
                angled.hide_viewport = True
                angled.hide_render = True
            return

        inv = 1.0 / math.sqrt(2.0)
        clip_len = clip * math.sqrt(2.0)
        margin = inch(2.0)

        # Cutter: box rotated 45 deg, near face on the clip line, growing
        # in local -X along the line and local +Y toward the rear corner.
        if cutter is not None:
            origin_x = clip + margin * inv
            origin_y = margin * inv
            cage_x = clip_len + 2.0 * margin
            cage_y = clip * inv + margin
            cage_z = height + 2.0 * margin
            cutter.location = (origin_x, origin_y, -margin)
            cutter.rotation_euler = (0.0, 0.0, math.radians(45.0))
            _set_mod_inputs(cutter, cutter.home_builder.mod_name, (
                ('Dim X', cage_x),
                ('Dim Y', cage_y),
                ('Dim Z', cage_z),
                ('Mirror X', True),
                ('Mirror Y', False),
                ('Mirror Z', False),
                ('Show Cage', True),
            ))

        # Angled back: vertical panel on the clip line. Built like the
        # wall-side backs (Length along Z); the -45 deg Z rotation aligns
        # Width with the clip line. Anchored at P1 = (clip, 0); Thickness
        # extends into the cabinet body.
        if angled is not None:
            angled.hide_viewport = False
            angled.hide_render = False
            back_height = height - z_back_floor - t
            angled.location = (clip, 0.0, z_back_floor)
            angled.rotation_euler.z = math.radians(-45.0)
            _set_mod_inputs(angled, angled.home_builder.mod_name, (
                ('Length', back_height),
                ('Width', clip_len),
                ('Thickness', t),
            ))

    def _build_clip_back_parts(self):
        """Create the clip-back cutter and angled back panel, and attach
        the clip boolean to the four parts that cross the rear corner.

        Shared by pie cut and diagonal: the rear corner is the (0,0)
        wall corner for both shapes. The cutter is a GeoNodeCage child
        of the cabinet root; Bottom, Top, and both Backs get a Boolean
        DIFFERENCE referencing it. recalc sizes the cutter from
        clip_back_amount and disables the whole feature when it is 0.
        """
        cutter = GeoNodeCage()
        cutter.create('Clip Back Cutter')
        cutter.obj.parent = self.obj
        cutter.obj['hb_part_role'] = PART_ROLE_CORNER_BACK_CUTTER
        cutter.set_input('Show Cage', True)
        cutter.obj.hide_viewport = True
        cutter_obj = cutter.obj

        # Angled back panel closing the clip face. Same orientation as
        # the wall-side backs (vertical, Length along Z); recalc adds the
        # 45 degree rotation and positions it on the clip line.
        angled = CabinetPart()
        angled.create('Angled Back')
        angled.obj.parent = self.obj
        angled.obj['hb_part_role'] = PART_ROLE_CORNER_ANGLED_BACK
        angled.obj['CABINET_PART'] = True
        angled.obj.rotation_euler.y = math.radians(-90)
        angled.set_input('Mirror Y', True)
        angled.set_input('Mirror Z', True)
        angled.obj.hide_viewport = True
        angled.obj.hide_render = True

        # Clip boolean on the four parts crossing the rear corner. The
        # sides sit at the front of each arm and are untouched.
        for role in (PART_ROLE_CORNER_BOTTOM, PART_ROLE_CORNER_TOP,
                     PART_ROLE_CORNER_LEFT_BACK,
                     PART_ROLE_CORNER_RIGHT_BACK):
            part = next((c for c in self.obj.children
                         if c.get('hb_part_role') == role), None)
            if part is None:
                continue
            mod = part.modifiers.new(name='Clip Back Cut', type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.object = cutter_obj

    def _clear_door_pull(self, door_obj):
        """Remove any pull instances parented to a corner door."""
        for child in list(door_obj.children):
            if child.get('hb_part_role') == 'PULL':
                bpy.data.objects.remove(child, do_unlink=True)

    def _refresh_door_pull(self, door_obj, length, width, thickness,
                           width_sign=-1.0, edge='CORNER'):
        """Clear and re-attach the pull on a corner door.

        Corner doors persist across recalc - unlike standard fronts,
        which are wiped and rebuilt each cycle - so any prior pull must
        be removed first or pulls accumulate. _create_pull_for_front
        handles asset resolution, vertical placement, and the mounting
        plane; it expects a CabinetPart-like wrapper exposing .obj and
        for a DOOR role only reads part_dims off the leaf, so a minimal
        descriptor is enough. Its horizontal heuristic assumes a
        standard front, so the Width-axis position is overridden here.

        width_sign is -1 for a door built Mirror Y True (Width grows in
        part-local -Y: the left and diagonal doors) and +1 for Mirror Y
        False (the pie cut right door). edge picks which end of the
        Width span carries the pull: 'CORNER' for the inside-corner
        meeting edge, 'OUTER' for the stile-side edge.
        """
        self._clear_door_pull(door_obj)
        pull = self._create_pull_for_front(
            SimpleNamespace(obj=door_obj),
            ff.PART_ROLE_DOOR,
            {'part_dims': (length, width, thickness)},
        )
        if pull is None:
            return
        h_offset = bpy.context.scene.hb_face_frame.pull_horizontal_offset
        if edge == 'OUTER':
            pull.location.y = width_sign * h_offset
        else:  # CORNER
            pull.location.y = width_sign * (width - h_offset)

    def _refresh_drawer_pull(self, front_obj, length, width, thickness, side):
        """Clear and re-attach a CENTERED drawer-style pull on a corner drawer
        front. Unlike a door pair (where only the active leaf carries an
        edge-offset pull), each stacked drawer front - both arms - gets its own
        pull. _create_pull_for_front with the DRAWER_FRONT role gives the
        drawer pull asset, a horizontal bar, and the drawer vertical placement;
        the horizontal centre is set per arm: the left front is built Mirror Y
        (Width spans part-local -Y, centre -W/2) and the right front Mirror Y
        False (Width spans +Y, centre +W/2).
        """
        self._clear_door_pull(front_obj)
        pull = self._create_pull_for_front(
            SimpleNamespace(obj=front_obj),
            ff.PART_ROLE_DRAWER_FRONT,
            {'part_dims': (length, width, thickness)},
        )
        if pull is None:
            return
        pull.location.y = -width / 2.0 if side == 'LEFT' else width / 2.0

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
        elif cab_props.corner_type == 'PIE_CUT_DRAWER':
            self._recalculate_pie_cut_drawer()

        # Ensure every corner part carries a right-click menu. Corner parts
        # are built outside the standard rectangular reconciliation, so they
        # miss the part-commands menu it assigns; without a MENU_ID a part
        # has no right-click menu at all (e.g. side panels couldn't reach
        # Set Finished End Condition). Assign the shared part-commands menu
        # to any part that has a role but no menu, without clobbering one
        # that already has a more specific menu.
        for _part_obj in self.obj.children_recursive:
            if _part_obj.get('hb_part_role') and not _part_obj.get('MENU_ID'):
                _part_obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'

    def _reconcile_pie_cut_sections(self, cab_props):
        """Create / remove the section-dependent pie cut parts - one door
        per arm per section, plus a mid rail per arm between sections -
        to match cab_props.corner_sections. A layout signature gates the
        rebuild so routine recalcs just reposition existing parts.

        Pie cut sections span both arms: section i produces a LEFT door
        and a RIGHT door, and each mid rail boundary produces a LEFT and
        a RIGHT mid rail. Doors and mid rails carry hb_corner_section_index
        so the recalc can address each one.
        """
        sections = cab_props.corner_sections
        sig = 'pie:' + '|'.join(s.content for s in sections)
        if self.obj.get('hb_pie_section_sig') == sig:
            return
        # Layout changed - wipe section parts (all pie cut doors plus the
        # arm mid rails) and rebuild. Stiles and rails share the LEFT /
        # RIGHT side tags but are not PART_ROLE_DOOR / CORNER_MID_RAIL.
        for child in list(self.obj.children):
            role = child.get('hb_part_role')
            side = child.get('hb_face_frame_side')
            is_section_part = (
                (role == ff.PART_ROLE_DOOR and side in ('LEFT', 'RIGHT'))
                or (role == PART_ROLE_CORNER_MID_RAIL
                    and side in ('LEFT', 'RIGHT'))
                or role == PART_ROLE_CORNER_SHELF)
            if is_section_part:
                for pull in list(child.children):
                    bpy.data.objects.remove(pull, do_unlink=True)
                bpy.data.objects.remove(child, do_unlink=True)
        n = len(sections)
        # One door per arm per section. Orientation matches the arm's
        # stile so the slab lies in that face frame plane.
        for i in range(n):
            left_door = CabinetPart()
            left_door.create('Left Door %d' % (i + 1))
            left_door.obj.parent = self.obj
            left_door.obj['hb_part_role'] = ff.PART_ROLE_DOOR
            left_door.obj['hb_face_frame_side'] = 'LEFT'
            left_door.obj['hb_corner_section_index'] = i
            left_door.obj['CABINET_PART'] = True
            left_door.obj.rotation_euler.y = math.radians(-90)
            left_door.obj.rotation_euler.z = math.radians(180)
            left_door.set_input('Mirror Y', True)

            right_door = CabinetPart()
            right_door.create('Right Door %d' % (i + 1))
            right_door.obj.parent = self.obj
            right_door.obj['hb_part_role'] = ff.PART_ROLE_DOOR
            right_door.obj['hb_face_frame_side'] = 'RIGHT'
            right_door.obj['hb_corner_section_index'] = i
            right_door.obj['CABINET_PART'] = True
            right_door.obj.rotation_euler.y = math.radians(-90)
            right_door.obj.rotation_euler.z = math.radians(90)
        # A mid rail per arm between each pair of adjacent sections.
        # Orientation matches that arm's bottom rail.
        for j in range(n - 1):
            left_rail = CabinetPart()
            left_rail.create('Left Mid Rail %d' % (j + 1))
            left_rail.obj.parent = self.obj
            left_rail.obj['hb_part_role'] = PART_ROLE_CORNER_MID_RAIL
            left_rail.obj['hb_face_frame_side'] = 'LEFT'
            left_rail.obj['hb_corner_section_index'] = j
            left_rail.obj['CABINET_PART'] = True
            left_rail.obj.rotation_euler.x = math.radians(-90)
            left_rail.obj.rotation_euler.z = math.radians(90)
            left_rail.set_input('Mirror Y', True)
            left_rail.set_input('Mirror Z', True)

            right_rail = CabinetPart()
            right_rail.create('Right Mid Rail %d' % (j + 1))
            right_rail.obj.parent = self.obj
            right_rail.obj['hb_part_role'] = PART_ROLE_CORNER_MID_RAIL
            right_rail.obj['hb_face_frame_side'] = 'RIGHT'
            right_rail.obj['hb_corner_section_index'] = j
            right_rail.obj['CABINET_PART'] = True
            right_rail.obj.rotation_euler.x = math.radians(-90)
            right_rail.obj.rotation_euler.z = math.radians(180)
            right_rail.set_input('Mirror Y', True)
        self.obj['hb_pie_section_sig'] = sig

    def _make_pie_cut_shelf(self, section_index, shelf_index):
        """Create one L-shaped pie-cut CORNER_SHELF, built like the Top /
        Bottom panels: a rectangular panel rotated into the corner with a
        CPM_CORNERNOTCH 'Front Notch' carving the L. Returns the object.
        """
        shelf = CabinetPart()
        shelf.create('Pie Cut Shelf %d.%d' % (section_index + 1, shelf_index + 1))
        shelf.obj.parent = self.obj
        shelf.obj['hb_part_role'] = PART_ROLE_CORNER_SHELF
        shelf.obj['hb_face_frame_side'] = 'PIE'
        shelf.obj['hb_corner_section_index'] = section_index
        shelf.obj['hb_corner_shelf_index'] = shelf_index
        shelf.obj['CABINET_PART'] = True
        # Interior tag so the Interiors selection mode shows the shelf
        # through the doors (show_in_front) and makes it selectable,
        # like every standard adjustable shelf.
        shelf.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        shelf.obj.rotation_euler.z = math.radians(-90)
        notch = shelf.add_part_modifier('CPM_CORNERNOTCH', 'Front Notch')
        notch.set_input('Flip X', True)
        notch.set_input('Flip Y', True)
        notch.mod.show_viewport = True
        notch.mod.show_render = True
        return shelf.obj

    def _ensure_pie_cut_section_shelves(self, section_index, qty):
        """Idempotently make exactly `qty` pie-cut CORNER_SHELF parts exist
        for `section_index` (create missing, remove extras). Count is
        auto-by-height, so it is reconciled here each recalc rather than in
        _reconcile_pie_cut_sections.
        """
        existing = sorted(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_CORNER_SHELF
             and c.get('hb_corner_section_index') == section_index),
            key=lambda c: c.get('hb_corner_shelf_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        for k in range(len(existing), qty):
            self._make_pie_cut_shelf(section_index, k)

    def _position_pie_cut_shelves(self, section_index, qty, sec_z0, sec_h,
                                  depth, width, t, fft, ld, rd,
                                  fflo, ffro, l_scribe, r_scribe):
        """Stack the section's pie-cut CORNER_SHELF parts evenly and size /
        notch them to match the Top / Bottom panels (same Length / Width
        and Front Notch formulas). No-op if qty <= 0 or the section is too
        short to fit the shelves.
        """
        if qty <= 0:
            return
        interior_h = sec_h - qty * solver.SHELF_THICKNESS
        if interior_h <= 0.0:
            return
        gap = interior_h / (qty + 1)
        for k in range(qty):
            shelf = next(
                (c for c in self.obj.children
                 if c.get('hb_part_role') == PART_ROLE_CORNER_SHELF
                 and c.get('hb_corner_section_index') == section_index
                 and c.get('hb_corner_shelf_index') == k),
                None)
            if shelf is None:
                continue
            # Stamp here too (runs every recalc) so shelves created
            # before the interior tag existed pick it up in old blends.
            shelf['IS_FACE_FRAME_INTERIOR_PART'] = True
            z_shelf = sec_z0 + (k + 1) * gap + k * solver.SHELF_THICKNESS
            shelf.location = (0.0, 0.0, z_shelf)
            _set_mod_inputs(shelf, shelf.home_builder.mod_name, (
                ('Length', depth - t - fflo - l_scribe),
                ('Width', width - t - ffro - r_scribe),
                ('Thickness', solver.SHELF_THICKNESS),
            ))
            _set_mod_inputs(shelf, 'Front Notch', (
                ('X', depth - rd + fft - t - fflo - l_scribe),
                ('Y', width - ld + fft - t - ffro - r_scribe),
                ('Route Depth', inch(0.76)),
            ))

    def _position_corner_loose_ladder(self, parts, *, t, kick_height,
                                      depth, width, ld, rd, fft,
                                      front_setback, left_scribe, right_scribe,
                                      il, ir, ibl, ibr,
                                      show_front_rails, ladder_vis):
        """Position the corner LOOSE / LOOSE_FLUSH toe-kick ladder. Shared
        by the pie-cut and diagonal recalcs so both build the identical
        L-perimeter sub-base ("same as the pie cut"): two front kick rails
        forming an L (front-left at X=fl_x running Y, front-right at Y=fr_y
        running X), a rear rail down each wall, and a short end board across
        each arm's outer end. The four toe-kick insets are applied -
        LEFT/RIGHT pull each arm's outer end inboard (the end board is its
        return closeout); BACK LEFT/RIGHT pull each rear rail off its wall.

        Geometry is cabinet-local; callers pass their own per-side scribe
        (the pie-cut keeps it in l_scribe/r_scribe with fflo/ffro = 0; the
        diagonal keeps it in fflo/ffro). `show_front_rails` gates the two
        front kicks (the pie-cut shows them for NOTCH too; the diagonal
        shows a diagonal kick for NOTCH and these only when loose);
        `ladder_vis` (= loose) gates the rear rails + end boards. Board
        thickness t extends toward the cabinet interior; Width is the kick
        height (stands on the floor at z=0).
        """
        fl_x = ld - fft - front_setback     # front-left rail X (left kick)
        fr_y = -rd + fft + front_setback    # front-right rail Y (right kick)
        WX = left_scribe + ibl              # left-wall rail X
        WY = -right_scribe - ibr            # back-wall rail Y
        LY = -depth + il                    # left arm outer end Y
        RX = width - ir                     # right arm outer end X

        left_kick = parts.get(PART_ROLE_CORNER_LEFT_KICK)
        if left_kick is not None:
            left_kick.hide_viewport = not show_front_rails
            left_kick.hide_render = not show_front_rails
            # Origin at the Left Side's back face (shifts with the left
            # scribe); the inside-corner end is anchored to the FF so only
            # the outer end moves with the left inset (il).
            left_kick.location = (fl_x, -depth + il + t + left_scribe, 0.0)
            _set_mod_inputs(left_kick, left_kick.home_builder.mod_name, (
                ('Length',
                 depth - rd + front_setback + fft - t - left_scribe - il),
                ('Width', kick_height),
                ('Thickness', t),
            ))

        right_kick = parts.get(PART_ROLE_CORNER_RIGHT_KICK)
        if right_kick is not None:
            right_kick.hide_viewport = not show_front_rails
            right_kick.hide_render = not show_front_rails
            right_kick.location = (
                width - ir - t - right_scribe, fr_y, 0.0)
            _set_mod_inputs(right_kick, right_kick.home_builder.mod_name, (
                ('Length',
                 width - ld + front_setback + fft - t - right_scribe - ir),
                ('Width', kick_height),
                ('Thickness', t),
            ))

        rear_left = parts.get(PART_ROLE_CORNER_LOOSE_REAR_LEFT)
        if rear_left is not None:
            rear_left.hide_viewport = not ladder_vis
            rear_left.hide_render = not ladder_vis
            if ladder_vis:
                rear_left.location = (WX + t, LY, 0.0)
                _set_mod_inputs(rear_left, rear_left.home_builder.mod_name, (
                    ('Length', WY - LY),
                    ('Width', kick_height),
                    ('Thickness', t),
                ))

        rear_right = parts.get(PART_ROLE_CORNER_LOOSE_REAR_RIGHT)
        if rear_right is not None:
            rear_right.hide_viewport = not ladder_vis
            rear_right.hide_render = not ladder_vis
            if ladder_vis:
                rear_right.location = (RX, WY - t, 0.0)
                _set_mod_inputs(rear_right, rear_right.home_builder.mod_name, (
                    ('Length', RX - WX - t),
                    ('Width', kick_height),
                    ('Thickness', t),
                ))

        end_left = parts.get(PART_ROLE_CORNER_LOOSE_END_LEFT)
        if end_left is not None:
            end_left.hide_viewport = not ladder_vis
            end_left.hide_render = not ladder_vis
            if ladder_vis:
                end_left.location = (fl_x, LY, 0.0)
                _set_mod_inputs(end_left, end_left.home_builder.mod_name, (
                    ('Length', fl_x - WX),
                    ('Width', kick_height),
                    ('Thickness', t),
                ))

        end_right = parts.get(PART_ROLE_CORNER_LOOSE_END_RIGHT)
        if end_right is not None:
            end_right.hide_viewport = not ladder_vis
            end_right.hide_render = not ladder_vis
            if ladder_vis:
                end_right.location = (RX, fr_y, 0.0)
                _set_mod_inputs(end_right, end_right.home_builder.mod_name, (
                    ('Length', WY - fr_y),
                    ('Width', kick_height),
                    ('Thickness', t),
                ))

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
        if not cab_props.corner_sections:
            props_hb.populate_corner_sections(cab_props)
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
        # Per-type toe-kick presentation (see _corner_kick_flags).
        kf = self._corner_kick_flags(cab_props)

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

        # Side panels run to the floor (NOTCH / FLUSH / upper) or float by
        # the kick height (FLOATING / LOOSE / LOOSE_FLUSH leave the kick
        # open). The front-bottom notch is only carved for NOTCH.
        side_z = 0.0 if kf.sides_to_floor else kick_height
        side_len = height if kf.sides_to_floor else height - kick_height

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
            left_side.location = (0.0, -depth + fflo + l_scribe, side_z)
            _set_mod_inputs(left_side, left_side.home_builder.mod_name, (
                ('Length', side_len),
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
                ls_mod.show_viewport = kf.side_notch
                ls_mod.show_render = kf.side_notch

        right_side = parts.get(PART_ROLE_CORNER_RIGHT_SIDE)
        if right_side is not None:
            # r_scribe shifts the side in -X (away from the face frame
            # outer edge at X=width). Right stile covers the gap.
            # Width unchanged.
            right_side.location = (width - ffro - r_scribe, 0.0, side_z)
            _set_mod_inputs(right_side, right_side.home_builder.mod_name, (
                ('Length', side_len),
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
                rs_mod.show_viewport = kf.side_notch
                rs_mod.show_render = kf.side_notch

        # Tray Compartment partition. Cavity-height interior divider that
        # walls a tray-storage strip off one leg. tray_compartment_width
        # is the clear width of that strip, measured from the leg's outer
        # side panel inner face. NONE (or zero width) hides the part.
        partition = parts.get(PART_ROLE_CORNER_PARTITION)
        if partition is not None:
            tc = cab_props.tray_compartment
            tcw = cab_props.tray_compartment_width
            if tc == 'NONE' or tcw <= 0.0:
                partition.hide_viewport = True
                partition.hide_render = True
            else:
                partition.hide_viewport = False
                partition.hide_render = False
                # Floor (z_back_floor) to ceiling (z_top), spanning the
                # arm depth from the back panel front face to the face
                # frame back face. LEFT = constant-Y panel like Left
                # Side; RIGHT = constant-X panel, Z rotation re-aimed.
                part_length = z_top - z_back_floor
                if tc == 'LEFT':
                    partition.rotation_euler.z = math.radians(-90)
                    partition.location = (
                        t,
                        -depth + fflo + l_scribe + t + tcw,
                        z_back_floor,
                    )
                    _set_mod_inputs(
                        partition, partition.home_builder.mod_name, (
                            ('Length', part_length),
                            ('Width', ld - fft - t),
                            ('Thickness', t),
                        ))
                else:  # RIGHT
                    partition.rotation_euler.z = math.radians(180)
                    partition.location = (
                        width - ffro - r_scribe - (2 * t) - tcw,
                        -t,
                        z_back_floor,
                    )
                    _set_mod_inputs(
                        partition, partition.home_builder.mod_name, (
                            ('Length', part_length),
                            ('Width', rd - fft - t),
                            ('Thickness', t),
                        ))

        # Tray compartment dividers. Up to 10 pre-built thin panels; show
        # and evenly space the first tray_compartment_qty across the
        # strip, hide the rest. Same orientation as the partition; spacing
        # follows (strip - qty * thickness) / (qty + 1).
        dividers = sorted(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_CORNER_TRAY_DIVIDER),
            key=lambda c: c.get('hb_corner_divider_index', 0))
        if dividers:
            tc = cab_props.tray_compartment
            tcw = cab_props.tray_compartment_width
            qty = cab_props.tray_compartment_qty
            dthk = cab_props.tray_compartment_divider_thickness
            setback = cab_props.tray_compartment_setback
            div_length = z_top - z_back_floor
            div_spacing = (
                (tcw - qty * dthk) / (qty + 1) if qty > 0 else 0.0)
            active = (tc in {'LEFT', 'RIGHT'} and tcw > 0.0
                      and qty > 0 and div_spacing > 0.0)
            for k, div in enumerate(dividers):
                if not active or k >= qty:
                    div.hide_viewport = True
                    div.hide_render = True
                    continue
                div.hide_viewport = False
                div.hide_render = False
                offset = (k + 1) * div_spacing + k * dthk
                if tc == 'LEFT':
                    div.rotation_euler.z = math.radians(-90)
                    div.location = (
                        t,
                        -depth + fflo + l_scribe + t + offset,
                        z_back_floor,
                    )
                    _set_mod_inputs(div, div.home_builder.mod_name, (
                        ('Length', div_length),
                        ('Width', ld - fft - t - setback),
                        ('Thickness', dthk),
                    ))
                else:  # RIGHT
                    div.rotation_euler.z = math.radians(180)
                    div.location = (
                        width - ffro - r_scribe - t - tcw + offset,
                        -t,
                        z_back_floor,
                    )
                    _set_mod_inputs(div, div.home_builder.mod_name, (
                        ('Length', div_length),
                        ('Width', rd - fft - t - setback),
                        ('Thickness', dthk),
                    ))

        # Front kick boards double as the ladder front rails for LOOSE /
        # LOOSE_FLUSH; LOOSE_FLUSH pulls them flush to the arm front
        # (setback 0) while NOTCH / LOOSE keep the recess setback.
        front_setback = 0.0 if kf.loose_flush else kick_setback

        # Toe-kick insets (corner). LEFT/RIGHT pull each arm's OUTER end
        # inboard; BACK LEFT/RIGHT pull each arm's rear (wall-side) rail
        # off its wall. Applied to the LOOSE / LOOSE_FLUSH ladder only
        # (kf.loose) - the end boards act as the outer-end return
        # closeouts. NOTCH / FLUSH / FLOATING ignore them (no ladder).
        il  = cab_props.inset_toe_kick_left       if kf.loose else 0.0
        ir  = cab_props.inset_toe_kick_right      if kf.loose else 0.0
        ibl = cab_props.inset_toe_kick_back_left  if kf.loose else 0.0
        ibr = cab_props.inset_toe_kick_back_right if kf.loose else 0.0
        # L-perimeter loose ladder (shared with the diagonal). The four
        # insets above are passed through; the pie-cut keeps its scribe in
        # l_scribe / r_scribe (fflo / ffro are 0 here) and shows the front
        # kicks for NOTCH too (they are the recessed subfront).
        self._position_corner_loose_ladder(
            parts, t=t, kick_height=kick_height, depth=depth, width=width,
            ld=ld, rd=rd, fft=fft, front_setback=front_setback,
            left_scribe=l_scribe, right_scribe=r_scribe,
            il=il, ir=ir, ibl=ibl, ibr=ibr,
            show_front_rails=kf.front_rails, ladder_vis=kf.loose)

        # Finish toe kicks: 0.25" facing on the front of each subfront.
        # ft shifts each finish kick forward into the room by its own
        # thickness; Length shrinks by ft so both finish kicks meet at
        # the (slightly forward) inside corner of the finish-kick plane.
        ft = cab_props.finish_toe_kick_thickness
        # Finish kicks face the recessed NOTCH subfront only.
        finish_visible = kf.finish

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
        # FLUSH drops the FF to the floor: stiles run full height and the
        # bottom rail grows down by kick_height (brw_eff). All other types
        # keep the FF above the kick. z_open_bot below stays constant
        # across types (z_ff_floor + brw_eff), so doors / sections don't
        # shift when the kick type changes.
        z_ff_floor = 0.0 if (kf.ff_to_floor or not has_kick) else kick_height
        stile_length = height - z_ff_floor
        brw_eff = brw_ff + (kick_height if kf.ff_to_floor else 0.0)

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
                ('Width', brw_eff),
                ('Thickness', fft),
            ))

        right_bot_rail = _find_ff_part(self.obj, ff.PART_ROLE_BOTTOM_RAIL, 'RIGHT')
        if right_bot_rail is not None:
            right_bot_rail.location = (width - rsw, -rd + fft, z_ff_floor)
            _set_mod_inputs(right_bot_rail, right_bot_rail.home_builder.mod_name, (
                ('Length', width - ld - lsw + fft),
                ('Width', brw_eff),
                ('Thickness', fft),
            ))

        # ---- Doors + section mid rails ---------------------------------
        # The FF opening between bottom and top rails is divided into the
        # stacked sections in cab_props.corner_sections (all DOORS for a
        # pie cut). Each section produces a LEFT and a RIGHT door; a mid
        # rail per arm separates adjacent sections. The exterior_option
        # swing mode applies per section, so a stacked cabinet gets one
        # pull per stacked level.
        self._reconcile_pie_cut_sections(cab_props)
        sections = cab_props.corner_sections
        n_sec = len(sections)
        mrw = cab_props.bay_mid_rail_width

        dt = cab_props.door_thickness
        top_ov = cab_props.default_top_overlay
        bot_ov = cab_props.default_bottom_overlay
        left_ov = cab_props.default_left_overlay
        right_ov = cab_props.default_right_overlay
        # Along-the-arm door dimensions are section-independent: each arm
        # opening runs from its stile inner edge to the inside corner.
        left_opening = depth - rd - lsw
        right_opening = width - ld - rsw

        # Revolving doors are inset - the panel sits inside the opening
        # with a reveal and the two doors meet flush at the corner.
        # Overlay modes oversize the panel and pull the corner side back
        # one door thickness so the opposing proud door has room.
        inset = cab_props.exterior_option == 'REVOLVING_DOORS'
        if inset:
            r = INSET_DOOR_REVEAL
            left_door_width = left_opening - r
            right_door_width = right_opening - r
            left_door_y = -depth + lsw + r
            right_door_x = width - rsw - r
            door_standoff = -dt
        else:
            left_door_width = left_opening - dt + left_ov
            right_door_width = right_opening - dt + right_ov
            left_door_y = -depth + lsw - left_ov
            right_door_x = width - rsw + right_ov
            door_standoff = (solver.DOOR_TO_FRAME_GAP
                             - cab_props.default_door_inset_amount)

        # Vertical section layout: opening from the top of the bottom
        # rail to the underside of the top rail, split per the section
        # heights (unlocked sections share the remainder equally).
        z_open_bot = z_ff_floor + brw_eff
        z_open_top = height - trw
        sec_heights = _solve_section_heights(
            sections, z_open_top - z_open_bot, n_sec - 1, mrw)

        ext = cab_props.exterior_option
        # Upper pie-cut corners get adjustable shelves behind their doors
        # (auto by section height), L-shaped like the Top/Bottom panels.
        is_upper = self.default_cabinet_type == 'UPPER'
        z_cursor = z_open_bot
        for i in range(n_sec - 1, -1, -1):
            sec_h = sec_heights[i]
            sec_z0 = z_cursor
            # Mirror the solved share into the height prop so the greyed
            # Height field reads the live opening size instead of the
            # prop default (12"). System write inside recalculate(); the
            # _RECALCULATING guard short-circuits the update callback's
            # re-entrant recalc.
            if (not sections[i].unlock_height
                    and abs(sections[i].height - sec_h) > 1e-7):
                sections[i].height = sec_h
            if inset:
                r = INSET_DOOR_REVEAL
                door_length = sec_h - 2.0 * r
                z_door = sec_z0 + r
            else:
                door_length = sec_h + top_ov + bot_ov
                z_door = sec_z0 - bot_ov

            left_door = _find_corner_part(
                self.obj, ff.PART_ROLE_DOOR, 'LEFT', i)
            if left_door is not None:
                left_door.location = (ld + door_standoff, left_door_y,
                                      z_door)
                _set_mod_inputs(
                    left_door, left_door.home_builder.mod_name, (
                        ('Length', door_length),
                        ('Width', left_door_width),
                        ('Thickness', dt),
                    ))
            right_door = _find_corner_part(
                self.obj, ff.PART_ROLE_DOOR, 'RIGHT', i)
            if right_door is not None:
                right_door.location = (right_door_x, -rd - door_standoff,
                                       z_door)
                _set_mod_inputs(
                    right_door, right_door.home_builder.mod_name, (
                        ('Length', door_length),
                        ('Width', right_door_width),
                        ('Thickness', dt),
                    ))

            # Pull dispatch for this section. Opens-first modes put the
            # pull on the corner-meeting edge of the named door; bifold
            # modes on the outer (stile-side) edge of the door away from
            # the hinge. width_sign is -1 for the Mirror-Y left door,
            # +1 for the right door.
            pull_spec = None
            if ext == 'LEFT_DOOR_OPENS_FIRST':
                pull_spec = (left_door, left_door_width, -1.0, 'CORNER')
            elif ext == 'RIGHT_DOOR_OPENS_FIRST':
                pull_spec = (right_door, right_door_width, 1.0, 'CORNER')
            elif ext in ('BIFOLD_LEFT_SWING', 'REVOLVING_DOORS'):
                pull_spec = (right_door, right_door_width, 1.0, 'OUTER')
            elif ext == 'BIFOLD_RIGHT_SWING':
                pull_spec = (left_door, left_door_width, -1.0, 'OUTER')
            pull_door = pull_spec[0] if pull_spec is not None else None
            for door in (left_door, right_door):
                if door is None:
                    continue
                if door is pull_door:
                    _, p_width, p_sign, p_edge = pull_spec
                    self._refresh_door_pull(
                        door, door_length, p_width, dt, p_sign, p_edge)
                else:
                    self._clear_door_pull(door)

            if is_upper:
                # Adjustable shelves behind the doors; L-shaped to match
                # the Top / Bottom panels. Auto by section height while
                # the section's qty is locked (synced into shelf_qty so
                # the UI shows the live count); unlock to override.
                sec = sections[i]
                auto_qty = solver.auto_shelf_qty(sec_h, depth)
                if not sec.unlock_shelf_qty and sec.shelf_qty != auto_qty:
                    # System write; the _RECALCULATING guard short-
                    # circuits the update callback's re-entrant recalc.
                    sec.shelf_qty = auto_qty
                qty = sec.shelf_qty if sec.unlock_shelf_qty else auto_qty
                self._ensure_pie_cut_section_shelves(i, qty)
                self._position_pie_cut_shelves(
                    i, qty, sec_z0, sec_h, depth, width, t, fft, ld, rd,
                    fflo, ffro, l_scribe, r_scribe)

            z_cursor = sec_z0 + sec_h
            if i > 0:
                # Mid rail per arm between section i and the one above.
                left_mr = _find_corner_part(
                    self.obj, PART_ROLE_CORNER_MID_RAIL, 'LEFT', i - 1)
                if left_mr is not None:
                    left_mr.location = (ld - fft, -depth + lsw, z_cursor)
                    _set_mod_inputs(
                        left_mr, left_mr.home_builder.mod_name, (
                            ('Length', depth - rd - lsw),
                            ('Width', mrw),
                            ('Thickness', fft),
                        ))
                right_mr = _find_corner_part(
                    self.obj, PART_ROLE_CORNER_MID_RAIL, 'RIGHT', i - 1)
                if right_mr is not None:
                    right_mr.location = (width - rsw, -rd + fft, z_cursor)
                    _set_mod_inputs(
                        right_mr, right_mr.home_builder.mod_name, (
                            ('Length', width - ld - lsw + fft),
                            ('Width', mrw),
                            ('Thickness', fft),
                        ))
                z_cursor += mrw

        self._recalculate_clip_back(cab_props, z_back_floor)

    # -----------------------------------------------------------------
    # Diagonal corner: recalculate
    # -----------------------------------------------------------------
    def _reconcile_diagonal_sections(self, cab_props):
        """Create / remove the section-dependent diagonal parts - mid
        rails and per-section door leaves - to match the current
        cab_props.corner_sections. A layout signature gates the rebuild
        so routine recalcs (height edits) skip the delete-and-recreate
        and just reposition the existing parts.
        """
        sections = cab_props.corner_sections
        # Swing is part of the layout signature: switching between the
        # double pair and a single leaf changes the door part set.
        sig = cab_props.diag_door_swing + '|' + '|'.join(
            '%s:%d' % (s.content, s.shelf_qty if s.content == 'OPEN' else 0)
            for s in sections)
        if self.obj.get('hb_diag_section_sig') == sig:
            return
        # Layout changed - wipe the section parts and rebuild from scratch.
        for child in list(self.obj.children):
            role = child.get('hb_part_role')
            side = child.get('hb_face_frame_side')
            is_section_part = (
                role == PART_ROLE_CORNER_MID_RAIL
                or role == PART_ROLE_CORNER_FALSE_FRONT
                or role == PART_ROLE_CORNER_SHELF
                or role == PART_ROLE_CORNER_FIXED_SHELF
                or (role == ff.PART_ROLE_DOOR
                    and side in ('DIAGONAL_LEFT', 'DIAGONAL_RIGHT')))
            if is_section_part:
                for pull in list(child.children):
                    bpy.data.objects.remove(pull, do_unlink=True)
                bpy.data.objects.remove(child, do_unlink=True)
        n = len(sections)
        # Mid rail between each pair of adjacent sections. Built with the
        # diagonal bottom-rail orientation; recalc adds the diagonal
        # angle and positions each rail at its section boundary.
        for j in range(n - 1):
            rail = CabinetPart()
            rail.create('Diagonal Mid Rail %d' % (j + 1))
            rail.obj.parent = self.obj
            rail.obj['hb_part_role'] = PART_ROLE_CORNER_MID_RAIL
            rail.obj['hb_face_frame_side'] = 'DIAGONAL'
            rail.obj['hb_corner_section_index'] = j
            rail.obj['CABINET_PART'] = True
            rail.obj.rotation_euler.x = math.radians(90)
            rail.set_input('Mirror Z', True)
        # Door leaves for each DOORS section: a double pair, or a single
        # full-width leaf whose side tag matches the hinge side
        # (LEFT_SWING hinges left, RIGHT_SWING hinges right).
        swing = cab_props.diag_door_swing
        if swing == 'LEFT_SWING':
            door_sides = ('DIAGONAL_LEFT',)
        elif swing == 'RIGHT_SWING':
            door_sides = ('DIAGONAL_RIGHT',)
        else:
            door_sides = ('DIAGONAL_LEFT', 'DIAGONAL_RIGHT')
        for i, sec in enumerate(sections):
            if sec.content != 'DOORS':
                continue
            for door_side in door_sides:
                leaf = 'Left' if door_side.endswith('LEFT') else 'Right'
                door = CabinetPart()
                door.create('Diagonal Door %d %s' % (i + 1, leaf))
                door.obj.parent = self.obj
                door.obj['hb_part_role'] = ff.PART_ROLE_DOOR
                door.obj['hb_face_frame_side'] = door_side
                door.obj['hb_corner_section_index'] = i
                door.obj['CABINET_PART'] = True
                door.obj.rotation_euler.y = math.radians(-90)
                door.obj.rotation_euler.z = math.radians(90)
                door.set_input('Mirror Y', True)
        # FALSE_FRONT section: one fixed panel, built like a door leaf
        # (proud of the FF, slab grows outward) but no pull.
        for i, sec in enumerate(sections):
            if sec.content != 'FALSE_FRONT':
                continue
            ff_panel = CabinetPart()
            ff_panel.create('Diagonal False Front %d' % (i + 1))
            ff_panel.obj.parent = self.obj
            ff_panel.obj['hb_part_role'] = PART_ROLE_CORNER_FALSE_FRONT
            ff_panel.obj['hb_face_frame_side'] = 'DIAGONAL'
            ff_panel.obj['hb_corner_section_index'] = i
            ff_panel.obj['CABINET_PART'] = True
            ff_panel.obj.rotation_euler.y = math.radians(-90)
            ff_panel.obj.rotation_euler.z = math.radians(90)
            ff_panel.set_input('Mirror Y', True)
        # OPEN section: a stack of shelves following the carcass. Each
        # shelf is a full L-bounding panel carved to the pentagon
        # silhouette by the same diagonal boolean cutter the Bottom and
        # Top panels use, and clipped at the rear corner by the clip-back
        # cutter - both found here by role and referenced from BOOLEAN
        # DIFFERENCE modifiers on each shelf.
        cutter_obj = next(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_DIAGONAL_CUTTER), None)
        back_cutter_obj = next(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_CORNER_BACK_CUTTER), None)
        for i, sec in enumerate(sections):
            if sec.content != 'OPEN':
                continue
            for k in range(sec.shelf_qty):
                shelf = CabinetPart()
                shelf.create('Diagonal Shelf %d.%d' % (i + 1, k + 1))
                shelf.obj.parent = self.obj
                shelf.obj['hb_part_role'] = PART_ROLE_CORNER_SHELF
                shelf.obj['hb_face_frame_side'] = 'DIAGONAL'
                shelf.obj['hb_corner_section_index'] = i
                shelf.obj['hb_corner_shelf_index'] = k
                shelf.obj['CABINET_PART'] = True
                shelf.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
                shelf.set_input('Mirror Y', True)
                if cutter_obj is not None:
                    cut = shelf.obj.modifiers.new(
                        name='Diagonal Cut', type='BOOLEAN')
                    cut.operation = 'DIFFERENCE'
                    cut.object = cutter_obj
                if back_cutter_obj is not None:
                    clip = shelf.obj.modifiers.new(
                        name='Clip Back Cut', type='BOOLEAN')
                    clip.operation = 'DIFFERENCE'
                    clip.object = back_cutter_obj
        # TALL hutch / bookcase: one FIXED shelf per section boundary,
        # top face flush with the top of its mid rail (positioned in
        # the recalc). Full L-bounding panel like Top/Bottom - the same
        # boolean pair carves the pentagon front and the rear clip.
        if self.default_cabinet_type == 'TALL':
            for j in range(n - 1):
                fixed = CabinetPart()
                fixed.create('Diagonal Fixed Shelf %d' % (j + 1))
                fixed.obj.parent = self.obj
                fixed.obj['hb_part_role'] = PART_ROLE_CORNER_FIXED_SHELF
                fixed.obj['hb_face_frame_side'] = 'DIAGONAL'
                fixed.obj['hb_corner_section_index'] = j
                fixed.obj['CABINET_PART'] = True
                fixed.set_input('Mirror Y', True)
                if cutter_obj is not None:
                    cut = fixed.obj.modifiers.new(
                        name='Diagonal Cut', type='BOOLEAN')
                    cut.operation = 'DIFFERENCE'
                    cut.object = cutter_obj
                if back_cutter_obj is not None:
                    clip = fixed.obj.modifiers.new(
                        name='Clip Back Cut', type='BOOLEAN')
                    clip.operation = 'DIFFERENCE'
                    clip.object = back_cutter_obj
        self.obj['hb_diag_section_sig'] = sig

    def _make_corner_shelf(self, section_index, shelf_index,
                           cutter_obj, back_cutter_obj):
        """Create one diagonal CORNER_SHELF part for a section, carved to
        the pentagon silhouette by the diagonal cutter and clipped at the
        rear corner by the back cutter - the same boolean pair the
        Top/Bottom panels use, so the shelf footprint matches them.
        Returns the new object.
        """
        shelf = CabinetPart()
        shelf.create('Diagonal Shelf %d.%d' % (section_index + 1, shelf_index + 1))
        shelf.obj.parent = self.obj
        shelf.obj['hb_part_role'] = PART_ROLE_CORNER_SHELF
        shelf.obj['hb_face_frame_side'] = 'DIAGONAL'
        shelf.obj['hb_corner_section_index'] = section_index
        shelf.obj['hb_corner_shelf_index'] = shelf_index
        shelf.obj['CABINET_PART'] = True
        shelf.obj['IS_FACE_FRAME_INTERIOR_PART'] = True
        shelf.set_input('Mirror Y', True)
        if cutter_obj is not None:
            cut = shelf.obj.modifiers.new(name='Diagonal Cut', type='BOOLEAN')
            cut.operation = 'DIFFERENCE'
            cut.object = cutter_obj
        if back_cutter_obj is not None:
            clip = shelf.obj.modifiers.new(name='Clip Back Cut', type='BOOLEAN')
            clip.operation = 'DIFFERENCE'
            clip.object = back_cutter_obj
        return shelf.obj

    def _ensure_diagonal_section_shelves(self, section_index, qty,
                                         cutter_obj, back_cutter_obj):
        """Idempotently make exactly `qty` CORNER_SHELF parts exist for
        `section_index`, creating any missing and removing extras. Used
        for DOORS-section shelves whose count is auto-by-height: the
        section signature can't gate an auto count, so it is reconciled
        here on each recalc rather than in _reconcile_diagonal_sections.
        """
        existing = sorted(
            (c for c in self.obj.children
             if c.get('hb_part_role') == PART_ROLE_CORNER_SHELF
             and c.get('hb_corner_section_index') == section_index),
            key=lambda c: c.get('hb_corner_shelf_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        for k in range(len(existing), qty):
            self._make_corner_shelf(section_index, k, cutter_obj, back_cutter_obj)

    def _position_diagonal_shelves(self, section_index, qty, sec_z0, sec_h,
                                   t, width, depth, fflo, ffro):
        """Stack the section's CORNER_SHELF parts evenly and size them to
        the inset Top/Bottom footprint (one material thickness in from the
        two backs; the boolean cutters carve the pentagon front). Shared by
        OPEN sections (count = Shelf Qty) and UPPER DOORS sections
        (count = auto-by-height). No-op if qty <= 0 or the section is too
        short to fit the shelves.
        """
        if qty <= 0:
            return
        interior_h = sec_h - qty * solver.SHELF_THICKNESS
        if interior_h <= 0.0:
            return
        gap = interior_h / (qty + 1)
        for k in range(qty):
            shelf = next(
                (c for c in self.obj.children
                 if c.get('hb_part_role') == PART_ROLE_CORNER_SHELF
                 and c.get('hb_corner_section_index') == section_index
                 and c.get('hb_corner_shelf_index') == k),
                None)
            if shelf is None:
                continue
            # Stamp here too (runs every recalc) so shelves created
            # before the interior tag existed pick it up in old blends.
            shelf['IS_FACE_FRAME_INTERIOR_PART'] = True
            z_shelf = sec_z0 + (k + 1) * gap + k * solver.SHELF_THICKNESS
            shelf.location = (t, -t, z_shelf)
            _set_mod_inputs(shelf, shelf.home_builder.mod_name, (
                ('Length', width - ffro - 2.0 * t),
                ('Width', depth - fflo - 2.0 * t),
                ('Thickness', solver.SHELF_THICKNESS),
            ))

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
        if not cab_props.corner_sections:
            props_hb.populate_corner_sections(cab_props)
        # Open bottom: drops the carcass bottom and the FF bottom rail
        # so the lowest opening runs to the carcass floor. User-driven
        # via the Remove Bottom checkbox (any config); the Hutch / Open
        # with Shelves configs used to force this by their lowest OPEN
        # section, which removed the bottom even when it was wanted.
        open_base = bool(cab_props.corner_remove_bottom)
        width = cab_props.width
        depth = cab_props.depth
        height = cab_props.height
        ld = cab_props.left_depth
        rd = cab_props.right_depth
        t = cab_props.material_thickness
        brw = cab_props.bottom_rail_width
        has_kick = self._has_toe_kick()
        kick_height = cab_props.toe_kick_height if has_kick else 0.0
        kf = self._corner_kick_flags(cab_props)
        # Side panels float by kick_height for FLOATING / LOOSE /
        # LOOSE_FLUSH; run to the floor otherwise (with a front-bottom
        # notch only for NOTCH). Mirrors the pie-cut side handling.
        side_z = 0.0 if kf.sides_to_floor else kick_height
        side_len = height if kf.sides_to_floor else height - kick_height

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
            bottom.hide_viewport = open_base
            bottom.hide_render = open_base

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
            left_side.location = (0.0, -depth + fflo, side_z)
            _set_mod_inputs(left_side, left_side.home_builder.mod_name, (
                ('Length', side_len),
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
                ls_mod.show_viewport = kf.side_notch
                ls_mod.show_render = kf.side_notch

        right_side = parts.get(PART_ROLE_CORNER_RIGHT_SIDE)
        if right_side is not None:
            right_side.location = (width - ffro, 0.0, side_z)
            _set_mod_inputs(right_side, right_side.home_builder.mod_name, (
                ('Length', side_len),
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
                rs_mod.show_viewport = kf.side_notch
                rs_mod.show_render = kf.side_notch

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

        # FLUSH drops the FF (stiles + bottom rail) to the floor and grows
        # the bottom rail down by kick_height (brw_eff); every other kick
        # type keeps the FF above the kick. Matches the pie-cut FF floor.
        z_ff_floor = 0.0 if (kf.ff_to_floor or not has_kick) else kick_height
        stile_length = height - z_ff_floor
        brw_eff = brw_ff + (kick_height if kf.ff_to_floor else 0.0)
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
                ('Width', brw_eff),
                ('Thickness', fft),
            ))
            bot_rail.hide_viewport = open_base
            bot_rail.hide_render = open_base

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
        # Diagonal kick is the NOTCH recessed subfront on the diagonal
        # face; LOOSE / LOOSE_FLUSH use the shared L ladder instead
        # (below), FLUSH / FLOATING have no kick board - so show it for
        # NOTCH only.
        diag_notch = kf.has_kick and kf.tk == 'NOTCH'
        diag_kick = parts.get(PART_ROLE_DIAGONAL_KICK)
        if diag_kick is not None:
            diag_kick.hide_viewport = not diag_notch
            diag_kick.hide_render = not diag_notch
        if diag_kick is not None and diag_notch:
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

        # Loose ladder (LOOSE / LOOSE_FLUSH): the same L sub-base as the
        # pie cut, inscribed in the diagonal footprint. front_setback
        # flushes the front rails for LOOSE_FLUSH; the four insets apply
        # on loose only. The diagonal keeps its per-side scribe in
        # fflo / ffro (the pie-cut keeps it in l_scribe / r_scribe).
        front_setback = 0.0 if kf.loose_flush else cab_props.toe_kick_setback
        il  = cab_props.inset_toe_kick_left       if kf.loose else 0.0
        ir  = cab_props.inset_toe_kick_right      if kf.loose else 0.0
        ibl = cab_props.inset_toe_kick_back_left  if kf.loose else 0.0
        ibr = cab_props.inset_toe_kick_back_right if kf.loose else 0.0
        self._position_corner_loose_ladder(
            parts, t=t, kick_height=kick_height, depth=depth, width=width,
            ld=ld, rd=rd, fft=fft, front_setback=front_setback,
            left_scribe=fflo, right_scribe=ffro,
            il=il, ir=ir, ibl=ibl, ibr=ibr,
            show_front_rails=kf.loose, ladder_vis=kf.loose)

        # ---- Sections: mid rails + per-section content --------------
        # The FF opening between the bottom and top rails is divided into
        # the stacked sections in cab_props.corner_sections (index 0 =
        # top). Mid rails separate adjacent sections; each DOORS section
        # carries a double-door pair. FALSE_FRONT and OPEN content land
        # in a later slice - those openings stay empty here. Sections lay
        # out from the bottom up.
        self._reconcile_diagonal_sections(cab_props)
        sections = cab_props.corner_sections
        n_sec = len(sections)
        mrw = cab_props.bay_mid_rail_width
        dt = cab_props.door_thickness
        top_ov = cab_props.default_top_overlay
        bot_ov = cab_props.default_bottom_overlay
        left_ov = cab_props.default_left_overlay
        right_ov = cab_props.default_right_overlay
        # Outward normal of the diagonal face is (uy, -ux); doors stand
        # off the FF front by the door-to-frame gap less any inset.
        standoff = (solver.DOOR_TO_FRAME_GAP
                    - cab_props.default_door_inset_amount)
        door_span = rail_length + left_ov + right_ov
        leaf_width = (door_span - solver.DOUBLE_DOOR_REVEAL) / 2.0
        right_shift = leaf_width + solver.DOUBLE_DOOR_REVEAL
        # Single-swing leaf spans the whole opening from the left rail
        # origin: no reveal split, no right shift. The existing pull
        # edges already land on the unhinged edge - the LEFT leaf's
        # 'CORNER' edge is its right end, and the RIGHT leaf's 'OUTER'
        # edge is the end at its origin, which IS the left end once the
        # shift is zeroed.
        if cab_props.diag_door_swing != 'DOUBLE_DOOR':
            leaf_width = door_span
            right_shift = 0.0
        # Opening runs from the top of the bottom rail to the underside
        # of the top rail. When the base is open the bottom rail is gone,
        # so the lowest opening starts at the carcass floor instead.
        z_open_bot = z_back_floor if open_base else z_ff_floor + brw_eff
        z_open_top = height - trw
        sec_heights = _solve_section_heights(
            sections, z_open_top - z_open_bot, n_sec - 1, mrw)
        # Upper corner cabinets get adjustable shelves behind their doors
        # (auto by section height), reusing the Top/Bottom boolean cutters.
        is_upper = self.default_cabinet_type == 'UPPER'
        diag_cutter = parts.get(PART_ROLE_DIAGONAL_CUTTER)
        diag_back_cutter = parts.get(PART_ROLE_CORNER_BACK_CUTTER)
        z_cursor = z_open_bot
        for i in range(n_sec - 1, -1, -1):
            sec_h = sec_heights[i]
            sec_z0 = z_cursor
            # Mirror the solved share into the height prop so the greyed
            # Height field reads the live opening size instead of the
            # prop default (12"). System write inside recalculate(); the
            # _RECALCULATING guard short-circuits the update callback's
            # re-entrant recalc.
            if (not sections[i].unlock_height
                    and abs(sections[i].height - sec_h) > 1e-7):
                sections[i].height = sec_h
            if sections[i].content == 'DOORS':
                # Double-door pair filling this section. Same horizontal
                # layout as a single-opening pair; Length and Z come from
                # the section.
                door_length = sec_h + top_ov + bot_ov
                z_door = sec_z0 - bot_ov
                left_door_x = rail_origin_x - left_ov * ux + standoff * uy
                left_door_y = rail_origin_y - left_ov * uy - standoff * ux
                d_left = _find_corner_part(
                    self.obj, ff.PART_ROLE_DOOR, 'DIAGONAL_LEFT', i)
                if d_left is not None:
                    d_left.location = (left_door_x, left_door_y, z_door)
                    d_left.rotation_euler.z = math.radians(90) + theta
                    _set_mod_inputs(d_left, d_left.home_builder.mod_name, (
                        ('Length', door_length),
                        ('Width', leaf_width),
                        ('Thickness', dt),
                    ))
                    self._refresh_door_pull(
                        d_left, door_length, leaf_width, dt,
                        width_sign=-1.0, edge='CORNER')
                d_right = _find_corner_part(
                    self.obj, ff.PART_ROLE_DOOR, 'DIAGONAL_RIGHT', i)
                if d_right is not None:
                    d_right.location = (
                        left_door_x + right_shift * ux,
                        left_door_y + right_shift * uy,
                        z_door,
                    )
                    d_right.rotation_euler.z = math.radians(90) + theta
                    _set_mod_inputs(d_right, d_right.home_builder.mod_name, (
                        ('Length', door_length),
                        ('Width', leaf_width),
                        ('Thickness', dt),
                    ))
                    self._refresh_door_pull(
                        d_right, door_length, leaf_width, dt,
                        width_sign=-1.0, edge='OUTER')
                if is_upper:
                    # Adjustable shelves behind the doors. Auto by section
                    # height while the section's qty is locked (synced into
                    # shelf_qty so the UI shows the live count); unlock to
                    # override. (FALSE_FRONT = sink apron, no shelves; OPEN
                    # handles its own shelf stack below.)
                    sec = sections[i]
                    auto_qty = solver.auto_shelf_qty(sec_h, depth)
                    if (not sec.unlock_shelf_qty
                            and sec.shelf_qty != auto_qty):
                        # System write; the _RECALCULATING guard short-
                        # circuits the update callback's re-entrant recalc.
                        sec.shelf_qty = auto_qty
                    qty = (sec.shelf_qty if sec.unlock_shelf_qty
                           else auto_qty)
                    self._ensure_diagonal_section_shelves(
                        i, qty, diag_cutter, diag_back_cutter)
                    self._position_diagonal_shelves(
                        i, qty, sec_z0, sec_h, t, width, depth, fflo, ffro)
            elif sections[i].content == 'FALSE_FRONT':
                # One fixed panel spanning the section opening, proud of
                # the FF like a door but with no pull and no center gap.
                panel_length = sec_h + top_ov + bot_ov
                z_panel = sec_z0 - bot_ov
                panel_x = rail_origin_x - left_ov * ux + standoff * uy
                panel_y = rail_origin_y - left_ov * uy - standoff * ux
                ff_panel = _find_corner_part(
                    self.obj, PART_ROLE_CORNER_FALSE_FRONT, 'DIAGONAL', i)
                if ff_panel is not None:
                    ff_panel.location = (panel_x, panel_y, z_panel)
                    ff_panel.rotation_euler.z = math.radians(90) + theta
                    _set_mod_inputs(
                        ff_panel, ff_panel.home_builder.mod_name, (
                            ('Length', panel_length),
                            ('Width', door_span),
                            ('Thickness', dt),
                        ))
            elif sections[i].content == 'OPEN':
                # Open shelves (created in the reconcile from the section's
                # Shelf Qty); position to match the Top/Bottom silhouette.
                self._position_diagonal_shelves(
                    i, sections[i].shelf_qty, sec_z0, sec_h,
                    t, width, depth, fflo, ffro)
            z_cursor = sec_z0 + sec_h
            if i > 0:
                # Mid rail between section i and the section above it.
                mid_rail = _find_corner_part(
                    self.obj, PART_ROLE_CORNER_MID_RAIL, 'DIAGONAL', i - 1)
                if mid_rail is not None:
                    mid_rail.location = (
                        rail_origin_x, rail_origin_y, z_cursor)
                    mid_rail.rotation_euler.z = theta
                    _set_mod_inputs(
                        mid_rail, mid_rail.home_builder.mod_name, (
                            ('Length', rail_length),
                            ('Width', mrw),
                            ('Thickness', fft),
                        ))
                # TALL hutch / bookcase: fixed shelf at this boundary,
                # top face flush with the TOP of the mid rail. Same
                # full L footprint as Top/Bottom; the boolean cutters
                # carve the pentagon front + rear clip.
                fixed = _find_corner_part(
                    self.obj, PART_ROLE_CORNER_FIXED_SHELF, 'DIAGONAL',
                    i - 1)
                if fixed is not None:
                    fixed.location = (0.0, 0.0, z_cursor + mrw - t)
                    _set_mod_inputs(fixed, fixed.home_builder.mod_name, (
                        ('Length', width - t - ffro),
                        ('Width', depth - t - fflo),
                        ('Thickness', t),
                    ))
                z_cursor += mrw

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

        self._recalculate_clip_back(cab_props, z_back_floor)

    # -----------------------------------------------------------------
    # Pie cut DRAWER corner: build (slice 1 - carcass only)
    # -----------------------------------------------------------------
    def _build_pie_cut_drawer_parts(self):
        """Build the pie-cut drawer corner carcass.

        Reuses the standard pie-cut build (corner-notched L box + L-shaped face
        frame + stacked section fronts) so it reads as a pie cut, then adds the
        two parallel 45-degree interior channel walls the drawer slides between.
        Those replace the box's perpendicular arm-end sides (which the recalc
        hides). Sizing / positions are written by _recalculate_pie_cut_drawer.
        """
        self._build_pie_cut_parts()

        # Interior channel walls. Built with the kick-part convention
        # (rot X=-90 -> Length=run, Width=height, Thickness=t); the slide-axis
        # angle (rot Z) and position are set in recalc.
        for name, role in (('Left Channel Side', PART_ROLE_CORNER_CHANNEL_LEFT),
                           ('Right Channel Side', PART_ROLE_CORNER_CHANNEL_RIGHT)):
            side = CabinetPart()
            side.create(name)
            side.obj.parent = self.obj
            side.obj['hb_part_role'] = role
            side.obj['CABINET_PART'] = True
            side.obj.rotation_euler.x = math.radians(-90)
            # Front-bottom toe-kick notch; sized + gated on a recessed kick in
            # recalc. Flip X=False/Flip Y=True lands it on the bottom (X=0) of
            # the front (run) end, same convention as the standard corner sides.
            notch = side.add_part_modifier('CPM_CORNERNOTCH', 'Notch Front Bottom')
            notch.set_input('Flip X', False)
            notch.set_input('Flip Y', True)
            notch.mod.show_viewport = False
            notch.mod.show_render = False

        # Channel cutters: a hidden cage per wall, let into the Top, Bottom and
        # the back it meets, so each full-height wall seats into those panels
        # via boolean DIFFERENCE instead of interpenetrating them. Sized and
        # positioned to wrap each wall plus a small clearance in recalc.
        cutters = {}
        for name, role in (
                ('Left Channel Cutter', PART_ROLE_CORNER_CHANNEL_LEFT_CUTTER),
                ('Right Channel Cutter', PART_ROLE_CORNER_CHANNEL_RIGHT_CUTTER)):
            cage = GeoNodeCage()
            cage.create(name)
            cage.obj.parent = self.obj
            cage.obj['hb_part_role'] = role
            cage.set_input('Show Cage', True)
            cage.obj.hide_viewport = True
            cutters[role] = cage.obj

        roles = _children_by_corner_role(self.obj)
        cl_obj = cutters[PART_ROLE_CORNER_CHANNEL_LEFT_CUTTER]
        cr_obj = cutters[PART_ROLE_CORNER_CHANNEL_RIGHT_CUTTER]

        def _add_channel_cut(part, cutter_obj, mod_name):
            if part is None:
                return
            mod = part.modifiers.new(name=mod_name, type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.object = cutter_obj

        # Each panel is clipped to the channel by BOTH half-space cutters
        # (remove the wing outboard of the left wall AND outboard of the right
        # wall), leaving only the strip between the two walls.
        for pr in (PART_ROLE_CORNER_BOTTOM, PART_ROLE_CORNER_TOP,
                   PART_ROLE_CORNER_LEFT_BACK, PART_ROLE_CORNER_RIGHT_BACK):
            _add_channel_cut(roles.get(pr), cl_obj, 'Channel Cut L')
            _add_channel_cut(roles.get(pr), cr_obj, 'Channel Cut R')

    # -----------------------------------------------------------------
    # Pie cut DRAWER corner: recalculate (slice 1 - carcass only)
    # -----------------------------------------------------------------
    def _recalculate_pie_cut_drawer(self):
        """Recalculate the pie-cut drawer corner.

        Drives the box + L face frame + stacked section fronts via the shared
        pie-cut recalc, then hides the box's perpendicular arm-end sides and
        positions the two 45-degree interior channel walls the drawer slides
        between. The stacked section count is the drawer count.

        ITERATE: sections render as door slabs for now; drawer-front styling is
        the next slice. Channel-wall width / run are first-cut defaults from the
        front-opening geometry.
        """
        cab_props = self.obj.face_frame_cabinet

        # Stacked drawer count from the per-cabinet prop. Content-only sync
        # here (no height writes) so this recalc can't re-enter through a
        # section-height update callback; the top-drawer height default is
        # applied by populate_pie_drawer_sections on the qty-change callback
        # and at create, not here.
        drawer_qty = cab_props.pie_drawer_qty
        secs = cab_props.corner_sections
        if len(secs) != drawer_qty:
            secs.clear()
            for _ in range(drawer_qty):
                secs.add().content = 'DOORS'

        # Box + L face frame + stacked fronts (shared pie-cut machinery).
        self._update_root_corner_notch()
        self._recalculate_pie_cut()

        # Drawer pulls: one CENTERED drawer-style pull on every section front
        # (both arms). The shared pie-cut recalc places door-style pulls (one
        # leaf of each pair, edge-offset, the other cleared) - a drawer stack
        # instead wants a centered pull on each front, so override them here.
        for front in self.obj.children:
            if front.get('hb_part_role') != ff.PART_ROLE_DOOR:
                continue
            side = front.get('hb_face_frame_side')
            if side not in ('LEFT', 'RIGHT'):
                continue
            dims = _front_gn_dims(front)
            if dims is not None:
                self._refresh_drawer_pull(front, dims[0], dims[1], dims[2], side)

        width = cab_props.width
        depth = cab_props.depth
        height = cab_props.height
        ld = cab_props.left_depth
        rd = cab_props.right_depth
        t = cab_props.material_thickness
        fft = cab_props.face_frame_thickness
        kf = self._corner_kick_flags(cab_props)
        kick_height = cab_props.toe_kick_height if self._has_toe_kick() else 0.0
        toe_kick_setback = cab_props.toe_kick_setback

        parts = _children_by_corner_role(self.obj)

        # Hide the box's perpendicular arm-end sides - the 45-degree channel
        # walls take their place (the drawer corner has no box sides).
        for role in (PART_ROLE_CORNER_LEFT_SIDE, PART_ROLE_CORNER_RIGHT_SIDE):
            s = parts.get(role)
            if s is not None:
                s.hide_viewport = True
                s.hide_render = True

        # ---- Channel walls: two parallel panels along the slide axis ----
        # The drawer pulls straight out the front, so the walls run along the
        # A-B normal n (not the box diagonal). Each sits on a front opening
        # corner -- LEFT on A=(ld,-depth), RIGHT on B=(width,-rd) -- and runs
        # back to a wall plane (LEFT -> x=0, RIGHT -> y=0). Full height (Length
        # runs +Z from the floor), Thickness = face-frame thickness; the origin
        # is nudged outward (along -/+u) by t for drawer clearance and the run
        # is recessed at the front by t. Orientation is the fixed
        # (-90, -90, atan2(-ux, uy)) basis: local X(Length)->+Z, Y(Width)->n,
        # Z(Thickness)->u. Derived analytically; matches a hand-placed
        # reference within ~1.5 mm. (Single-square cabinets are degenerate, so
        # the formula keys off A / B + the wall planes, which hold off-square.)
        diag_dx = width - ld
        diag_dy = depth - rd
        diag_len = math.sqrt(diag_dx * diag_dx + diag_dy * diag_dy)
        ux, uy = diag_dx / diag_len, diag_dy / diag_len
        nx, ny = uy, -ux                       # A-B normal toward the room (run)
        rot = (math.radians(-90), math.radians(-90), math.atan2(-ux, uy))
        # (role, front_x, front_y, lam_to_wall, outward_sign)
        # mirror_z flips the panel's thickness to the inboard side so both
        # walls present material toward the channel centre (the right wall's
        # +Z/thickness axis points outward without it).
        specs = (
            (PART_ROLE_CORNER_CHANNEL_LEFT,  ld,    -depth, ld / uy, -1.0, False),
            (PART_ROLE_CORNER_CHANNEL_RIGHT, width, -rd,    rd / ux,  1.0, True),
        )
        for role, fx, fy, lam, out_sgn, mirror_z in specs:
            side = parts.get(role)
            if side is None:
                continue
            bx, by = fx - nx * lam, fy - ny * lam      # back end at the wall
            ox = bx + out_sgn * ux * t                 # outward clearance
            oy = by + out_sgn * uy * t
            run = max(math.hypot(fx - bx, fy - by) - t, inch(3.0))
            side.location = (ox, oy, 0.0)
            side.rotation_euler = rot
            _set_mod_inputs(side, side.home_builder.mod_name, (
                ('Length', height),
                ('Width', run),
                ('Thickness', fft),
                ('Mirror Z', mirror_z),
            ))

            # Front-bottom toe-kick notch, shown only for a recessed kick.
            # The wall runs diagonally, so the notch depth measured along it has
            # to grow by 1/cos(angle) to land flush with the arm's kick face:
            # the perpendicular recess (setback plus one material thickness for
            # the visible finish-kick face) divided by the run direction's
            # component normal to that arm (uy for the left, ux for the right).
            perp = abs(uy) if role == PART_ROLE_CORNER_CHANNEL_LEFT else abs(ux)
            notch_y = ((toe_kick_setback + t) / perp
                       if perp > 1e-6 else toe_kick_setback)
            _set_mod_inputs(side, 'Notch Front Bottom', (
                ('X', kick_height),
                ('Y', notch_y),
                ('Route Depth', fft),
            ))
            nmod = side.modifiers.get('Notch Front Bottom')
            if nmod is not None:
                nmod.show_viewport = kf.side_notch
                nmod.show_render = kf.side_notch

            # Cutter cage wrapping this wall + clearance, so the Top / Bottom /
            # back it crosses get a clean let-in slot. Same rotation as the
            # wall (local X->+Z, Y->run n, Z->thickness u); grows +Z/+n/+u from
            # origin, so shift the origin back by each margin. The thickness
            # offset depends on which face the wall's material sits on
            # (mirror_z): left wall spans 0..+fft along u, right -fft..0.
            cutter_role = (PART_ROLE_CORNER_CHANNEL_LEFT_CUTTER
                           if role == PART_ROLE_CORNER_CHANNEL_LEFT
                           else PART_ROLE_CORNER_CHANNEL_RIGHT_CUTTER)
            cutter = parts.get(cutter_role)
            if cutter is not None:
                # Half-space cutter: removes everything OUTBOARD of this wall
                # (the dead-corner wing) from the Top / Bottom / backs, so only
                # the drawer channel between the two walls survives. The inboard
                # boundary sits clr inside the wall's outboard face (tucked
                # under the wall, no coplanar z-fight); the cage grows OUTBOARD
                # and spans far in run + height to clear the whole panel.
                vm = inch(0.5)
                clr = inch(0.02)
                big = inch(60.0)
                inboard_sign = 1.0 if not mirror_z else -1.0   # +u toward channel
                cutter.location = (ox - big * nx + inboard_sign * ux * clr,
                                   oy - big * ny + inboard_sign * uy * clr,
                                   -vm)
                cutter.rotation_euler = rot
                _set_mod_inputs(cutter, cutter.home_builder.mod_name, (
                    ('Dim X', height + 2.0 * vm),   # vertical: through top/bottom
                    ('Dim Y', 2.0 * big),           # run: whole panel both ways
                    ('Dim Z', big),                 # outboard: the whole wing
                    ('Mirror X', False),
                    ('Mirror Y', False),
                    ('Mirror Z', not mirror_z),     # grow OUTBOARD, away from channel
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


class UpperDiagonalCabinet(CornerFaceFrameCabinet):
    """Upper / wall diagonal corner cabinet (no toe kick)."""
    default_corner_type = 'DIAGONAL'
    default_cabinet_type = 'UPPER'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.upper_inside_corner_size
            self.default_depth = props.upper_inside_corner_size
            self.default_height = props.upper_cabinet_height
            self.default_left_depth = props.upper_cabinet_depth
            self.default_right_depth = props.upper_cabinet_depth

    def create(self, name="Diagonal Upper", bay_qty=1):
        super().create(name=name, bay_qty=bay_qty)
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            self.obj.location.z = scene.hb_face_frame.default_wall_cabinet_location


class TallDiagonalCabinet(CornerFaceFrameCabinet):
    """Tall diagonal corner cabinet (toe kick present)."""
    default_corner_type = 'DIAGONAL'
    default_cabinet_type = 'TALL'

    def __init__(self):
        super().__init__()
        scene = bpy.context.scene
        if hasattr(scene, 'hb_face_frame'):
            props = scene.hb_face_frame
            self.default_width = props.tall_inside_corner_size
            self.default_depth = props.tall_inside_corner_size
            self.default_height = props.tall_cabinet_height
            self.default_left_depth = props.tall_cabinet_depth
            self.default_right_depth = props.tall_cabinet_depth


class BasePieCutDrawerCabinet(CornerFaceFrameCabinet):
    """Base height pie cut DRAWER corner cabinet: 45-degree channel carcass
    (slice 1, carcass only). Drawer fronts (2 / 3 / 4) come in a later slice;
    the carcass is shared across those presets since the footprint is always
    square (width == depth)."""
    default_corner_type = 'PIE_CUT_DRAWER'
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

    def create(self, name="Pie Cut Drawer", bay_qty=1):
        super().create(name=name, bay_qty=bay_qty)
        # Seed the stacked drawer sections (pie_drawer_qty default) so the
        # top opening picks up the Top Drawer Opening Height default for a
        # 3 / 4 drawer stack; the recalc then solves the remaining shares.
        props_hb.populate_pie_drawer_sections(self.obj.face_frame_cabinet)


# ---------------------------------------------------------------------------
# Dispatch (mutates registries in types_face_frame at import)
# ---------------------------------------------------------------------------
# CABINET_NAME_DISPATCH: catalog name -> subclass for catalog draw flow.
ff.CABINET_NAME_DISPATCH.update({
    "Pie Cut Base": BasePieCutCabinet,
    "Pie Cut Upper": UpperPieCutCabinet,
    "Diagonal Base": BaseDiagonalCabinet,
    "Diagonal Upper": UpperDiagonalCabinet,
    "Diagonal Tall": TallDiagonalCabinet,
    "Pie Cut Drawer": BasePieCutDrawerCabinet,
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
    'UpperDiagonalCabinet': UpperDiagonalCabinet,
    'TallDiagonalCabinet': TallDiagonalCabinet,
    'BasePieCutDrawerCabinet': BasePieCutDrawerCabinet,
})
