"""Closet starter construction classes.

Base / Tall / Hanging / Island starters that build panels, top and
bottom fixed shelves, cleats, toe kicks, openings, and (Base/Island)
countertops. No drivers - all dimension propagation runs
through recalculate(), which reads the hb_closet_starter / hb_closet_bay
PropertyGroups, asks solver_closets for the layout, and writes positions
and GeoNode inputs to every part.

Structure:
    starter root cage (TAG_STARTER_CAGE)
    +-- panel parts 0..N          (shared verticals; panel i left of bay i)
    +-- countertop / applied-back parts (starter-level, per class flags)
    +-- bay cages (TAG_BAY_CAGE, hb_bay_index)
        +-- bottom shelf, top shelf, toe kick, cleat  (bay-local coords)
        +-- opening cage (TAG_OPENING_CAGE)           (interior volume)

Conventions match face_frame: origin back-left at floor, +X right,
-Y forward, +Z up. Vertical panels rotate y=-90 so Length runs up +Z,
Width runs -Y (Mirror Y), Thickness extrudes +X (Mirror Z).
"""
import bpy
import math

from ... import hb_utils
from ...hb_types import (GeoNodeCage, GeoNodeCutpart, GeoNodeObject,
                         GeoNodeDrawerBox, CabinetPartModifier)
from ...units import inch
from ..frameless.types_frameless import CabinetPart
from . import solver_closets as solver
from . import const_closets as const

from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Identity tags / part roles
# ---------------------------------------------------------------------------
TAG_STARTER_CAGE = 'IS_CLOSET_STARTER_CAGE'
TAG_BAY_CAGE = 'IS_CLOSET_BAY_CAGE'
TAG_OPENING_CAGE = 'IS_CLOSET_OPENING_CAGE'

PART_ROLE_PANEL = 'CLOSET_PANEL'
PART_ROLE_BOTTOM_SHELF = 'CLOSET_BOTTOM_SHELF'
PART_ROLE_TOP_SHELF = 'CLOSET_TOP_SHELF'
PART_ROLE_TOE_KICK = 'CLOSET_TOE_KICK'
PART_ROLE_CLEAT = 'CLOSET_CLEAT'
PART_ROLE_HANG_RAIL = 'CLOSET_HANG_RAIL'
PART_ROLE_COUNTERTOP = 'CLOSET_COUNTERTOP'
PART_ROLE_APPLIED_BACK = 'CLOSET_APPLIED_BACK'

# Interior parts added by the user. These live under an opening
# cage and carry idprops instead of a PropertyGroup so the whole layer
# stays hot-reloadable:
#   'hb_z_offset'   distance (m) from the opening bottom (or top when
#                   'hb_anchor_top') to the part's underside / rod center
#   'hb_anchor_top' 1 = z_offset measures down from the opening top, so
#                   the part rides the top when the bay height changes
#                   (rods hang; shelves usually anchor to the bottom)
PART_ROLE_FIXED_SHELF = 'CLOSET_FIXED_SHELF'
PART_ROLE_ADJ_SHELF = 'CLOSET_ADJ_SHELF'
PART_ROLE_ROD = 'CLOSET_ROD'
# Inserts. Fronts follow the legacy half-overlay convention.
PART_ROLE_DOOR = 'CLOSET_DOOR_FRONT'
PART_ROLE_DRAWER_FRONT = 'CLOSET_DRAWER_FRONT'
PART_ROLE_DRAWER_BOX = 'CLOSET_DRAWER_BOX'
PART_ROLE_CUBBY_DIVISION = 'CLOSET_CUBBY_DIVISION'
PART_ROLE_CUBBY_SHELF = 'CLOSET_CUBBY_SHELF'
# Double-sided island structure.
PART_ROLE_CENTER_BACK = 'CLOSET_CENTER_BACK'
# Corner-clearance bridge parts (starter-root children, lazily created
# by _layout_bridge_parts). Driven by starter-root idprops so the types
# module stays hot-reloadable:
#   hb_bridge_left / hb_bridge_right       1 = top bridge shelf on that end
#   hb_bridge_w_left / hb_bridge_w_right   span (m) past the end panel
#   hb_bridge_bot_left / hb_bridge_bot_right  1 = bottom shelf (+ kick)
PART_ROLE_BRIDGE_SHELF = 'CLOSET_BRIDGE_SHELF'
# Opening idprops: insert configuration, reconciled by regenerators on
# every recalc (create/remove children to match, then lay out).
PROP_ADJ_SHELF_QTY = 'hb_adj_shelf_qty'
PROP_DRAWER_QTY = 'hb_drawer_qty'
PROP_DRAWER_FRONT_HEIGHT = 'hb_drawer_front_height'
# Per-front idprops (on each drawer FRONT object). A drawer stack fills its
# opening: unlocked fronts share the remaining span equally. Editing a
# front's height locks it (hb_front_locked=1) so it holds while the others
# absorb the difference. hb_front_height is rewritten every recalc with the
# resolved height, so overlay labels always read the true value.
PROP_FRONT_HEIGHT = 'hb_front_height'
PROP_FRONT_LOCKED = 'hb_front_locked'
PROP_DOOR_SWING = 'hb_door_swing'        # ''|'LEFT'|'RIGHT'|'DOUBLE'
PROP_IS_HAMPER = 'hb_is_hamper'
# Bay-level doors span the WHOLE bay (all segments), parented to the bay
# cage; set from the bay menu. Mutually exclusive with opening doors on
# the same side (setting one clears the other).
PROP_BAY_DOOR_SWING = 'hb_bay_door_swing'
PROP_BAY_IS_HAMPER = 'hb_bay_is_hamper'
PROP_CUBBY_COLS = 'hb_cubby_cols'
PROP_CUBBY_ROWS = 'hb_cubby_rows'
# Opening idprop on double islands: which face the opening serves.
PROP_OPENING_SIDE = 'hb_opening_side'    # 'FRONT' (default) | 'BACK'

# Reentrance guards, same pattern as face_frame. Prop writes inside
# recalculate() (bay width redistribution) fire update callbacks that
# would otherwise recurse; the callbacks consult these sets and bail.
_RECALCULATING = set()
_DISTRIBUTING_WIDTHS = set()


def _apply_front_style(front_obj, is_drawer):
    """Apply the scene's front-style selection to one front (see
    fronts_closets). Best-effort: a missing module/selection leaves the
    front a slab rather than failing the recalc."""
    try:
        from . import fronts_closets
        fronts_closets.apply_style_to_front(front_obj, is_drawer)
    except Exception:
        pass


def _remove_part_tree(obj):
    """Remove a part AND its descendants. bpy.data.objects.remove()
    re-homes a removed object's children to the world keeping their
    LOCAL transform, so deleting a front alone strands its pull near
    the scene origin. Any part that can carry children (fronts with
    pulls) must be removed through this."""
    for child in list(obj.children):
        _remove_part_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def _set_part_hidden(obj, hidden):
    obj.hide_viewport = hidden
    obj.hide_render = hidden


# ---------------------------------------------------------------------------
# Cage classes
# ---------------------------------------------------------------------------
class ClosetBay(GeoNodeCage):
    """Bay cage: one section between two vertical panels. Carries the
    per-bay overrides (width/height/depth/floor_mounted) on
    obj.hb_closet_bay; its parts live in bay-local coordinates."""

    def create(self, name="Bay"):
        super().create(name)
        self.obj[TAG_BAY_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_bay_commands'
        self.set_input('Mirror Y', True)


class ClosetOpening(GeoNodeCage):
    """Opening cage: the interior volume of a bay between the fixed top
    and bottom shelves. User-added interior parts (shelves, rods) parent
    here and are laid out in opening-local coordinates."""

    def create(self, name="Opening"):
        super().create(name)
        self.obj[TAG_OPENING_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_opening_commands'
        self.set_input('Mirror Y', True)


class ClosetRod(GeoNodeObject):
    """Hang rod. Uses the legacy rod node group (round/oval profile with
    end cups); Dim X is the rod length along local +X."""

    def create(self, name="Closet Rod"):
        super().create('GeoNodeClosetRod', name)
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        self.set_input('Radius', const.ROD_RADIUS)
        self.set_input('Cup Depth', const.ROD_CUP_DEPTH)
        self.set_input('Cup Depth 2', const.ROD_CUP_DEPTH_2)
        # Profile/finish are (re)written from the scene rod options on
        # every recalc - this is just the creation default.
        self.set_input('Is Oval', True)


# ---------------------------------------------------------------------------
# Interior part builders (module-level: operators call these directly)
# ---------------------------------------------------------------------------
def add_fixed_shelf(opening_obj, z_offset, anchor_top=False,
                    role=PART_ROLE_FIXED_SHELF):
    """Create a shelf part under an opening. Position/size are written by
    the next recalculate(); only static orientation is set here."""
    shelf = CabinetPart()
    shelf.create('Fixed Shelf' if role == PART_ROLE_FIXED_SHELF
                 else 'Adjustable Shelf')
    shelf.obj.parent = opening_obj
    shelf.obj['hb_part_role'] = role
    shelf.obj['hb_z_offset'] = float(z_offset)
    shelf.obj['hb_anchor_top'] = 1 if anchor_top else 0
    shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    shelf.set_input('Mirror Y', True)
    return shelf.obj


def add_rod(opening_obj, z_offset):
    """Create a hang rod under an opening, anchored to the opening top so
    it keeps its hang height when the bay grows."""
    rod = ClosetRod()
    rod.create()
    rod.obj.parent = opening_obj
    rod.obj['hb_part_role'] = PART_ROLE_ROD
    rod.obj['hb_z_offset'] = float(z_offset)
    rod.obj['hb_anchor_top'] = 1
    return rod.obj


# ---------------------------------------------------------------------------
# Starter base class
# ---------------------------------------------------------------------------
class ClosetStarter(GeoNodeCage):
    """Base class for all closet starters. No drivers - see module doc."""

    default_closet_type = 'BASE'
    has_toe_kick = True
    floor_mounted = True
    # Whether any bay can ever sit on the floor (and thus get a kick).
    # True even for Hanging so a bay dropped to the floor gets a kick.
    allows_toe_kick = True
    has_countertop = False
    has_applied_back = False
    # Double-sided (island) construction: center back per bay, front and
    # back opening cages, rear toe kick, countertop overhang all around.
    is_double = False
    # Wall-mounted starters carry a hang rail behind each bay top;
    # islands have no wall side, so their classes clear this.
    has_hang_rail = True
    ctop_overhang_all = False
    # None = use the scene default panel depth at create time.
    default_depth = None

    # -----------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------
    def default_height(self, scene_props):
        # Starter ENVELOPE height (floor to run top). A Hanging starter
        # is the same floor-standing envelope as a Tall - only its bays
        # are pre-set to hang (see _default_bay_height); the difference
        # is settings, not placement.
        return {
            'BASE': scene_props.base_panel_height,
            'TALL': scene_props.tall_panel_height,
            'HANGING': scene_props.hanging_top_height,
            'ISLAND': scene_props.base_panel_height,
        }[self.default_closet_type]

    def _default_bay_height(self, scene_props, sp):
        """Initial per-bay height. Full starter height by default; a
        Hanging starter seeds shorter hanging bays under the run top."""
        return sp.height

    def create_starter(self, name, bay_qty=const.DEFAULT_BAY_QTY):
        """Create the root cage, seed props, and build all parts. The
        body runs under the reentrance guards so prop seeding doesn't
        trigger nested recalcs; the trailing recalculate() lays out
        everything once."""
        super().create(name)
        self.obj[TAG_STARTER_CAGE] = True
        self.obj['CLASS_NAME'] = self.__class__.__name__
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_starter_commands'
        self.obj.display_type = 'WIRE'
        self.set_input('Mirror Y', True)

        scene_props = bpy.context.scene.hb_closets
        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            sp = self.obj.hb_closet_starter
            sp.closet_type = self.default_closet_type
            # Toe-kick height is seeded from the scene whenever the
            # starter CAN have floor bays (so a hanging bay converted to
            # the floor via drag gets a proper kick). Uppers with no
            # floor ever keep 0.
            sp.toe_kick_height = (scene_props.toe_kick_height
                                  if self.allows_toe_kick else 0.0)
            sp.toe_kick_setback = scene_props.toe_kick_setback
            sp.include_countertop = self.has_countertop
            sp.width = scene_props.default_closet_width
            sp.height = self.default_height(scene_props)
            sp.depth = (self.default_depth
                        if self.default_depth is not None
                        else scene_props.default_panel_depth)
            self._build_parts(bay_qty, scene_props)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()

    def _build_parts(self, bay_qty, scene_props):
        """Create panels, starter-level parts, and bay subtrees. All
        positions/dimensions are written later by recalculate()."""
        sp = self.obj.hb_closet_starter
        bay_qty = max(1, int(bay_qty))

        # ----- Vertical panels 0..N (panel i = left panel of bay i) -----
        for i in range(bay_qty + 1):
            panel = CabinetPart()
            panel.create(f'Partition {i + 1}')
            panel.obj.parent = self.obj
            panel.obj['hb_part_role'] = PART_ROLE_PANEL
            panel.obj['hb_panel_index'] = i
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.set_input('Mirror Y', True)
            panel.set_input('Mirror Z', True)

        # ----- Starter-level optional parts -----
        if self.has_countertop:
            ctop = CabinetPart()
            ctop.create('Countertop')
            ctop.obj.parent = self.obj
            ctop.obj['hb_part_role'] = PART_ROLE_COUNTERTOP
            ctop.set_input('Mirror Y', True)

        # ----- Bays -----
        equal_width = (sp.width - (bay_qty + 1) * scene_props.panel_thickness) / bay_qty
        for i in range(bay_qty):
            bay = ClosetBay()
            bay.create(f'Bay {i + 1}')
            bay.obj.parent = self.obj
            bay.obj['hb_bay_index'] = i
            bp = bay.obj.hb_closet_bay
            bp.bay_index = i
            bp.width = equal_width
            bp.width_locked = False
            bp.height = self._default_bay_height(scene_props, sp)
            bp.depth = sp.depth
            bp.floor_mounted = self.floor_mounted
            self._build_bay_parts(bay.obj)

    def _build_bay_parts(self, bay_obj):
        """One bay's fixed parts + opening cage, in bay-local coords.
        Static rotations/mirrors are set here; recalculate() owns the
        positions and sizes. Toe kick / cleat orientation reproduces the
        legacy build: rot_x -90 stands the kick board up behind the
        setback line; rot_x +90 stands the cleat against the back."""
        bottom = CabinetPart()
        bottom.create('Bottom Shelf')
        bottom.obj.parent = bay_obj
        bottom.obj['hb_part_role'] = PART_ROLE_BOTTOM_SHELF
        bottom.set_input('Mirror Y', True)

        top = CabinetPart()
        top.create('Top Shelf')
        top.obj.parent = bay_obj
        top.obj['hb_part_role'] = PART_ROLE_TOP_SHELF
        top.set_input('Mirror Y', True)

        kick = CabinetPart()
        kick.create('Toe Kick')
        kick.obj.parent = bay_obj
        kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK
        kick.obj.rotation_euler.x = math.radians(-90)
        kick.set_input('Mirror Y', True)

        cleat = CabinetPart()
        cleat.create('Cleat')
        cleat.obj.parent = bay_obj
        cleat.obj['hb_part_role'] = PART_ROLE_CLEAT
        cleat.obj.rotation_euler.x = math.radians(90)
        # A double island has no wall side; the center back stiffens the
        # unit and the cleat would float mid-carcass - skip it.
        if self.is_double:
            _set_part_hidden(cleat.obj, True)
            cleat.obj['hb_always_hidden'] = 1

        if self.has_applied_back:
            back = CabinetPart()
            back.create('Applied Back')
            back.obj.parent = bay_obj
            back.obj['hb_part_role'] = PART_ROLE_APPLIED_BACK
            back.obj.rotation_euler.x = math.radians(90)
            back.set_input('Mirror Z', True)

        if self.is_double:
            rear_kick = CabinetPart()
            rear_kick.create('Rear Toe Kick')
            rear_kick.obj.parent = bay_obj
            rear_kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK
            rear_kick.obj['hb_rear'] = 1
            rear_kick.obj.rotation_euler.x = math.radians(-90)
            rear_kick.set_input('Mirror Y', True)
            rear_kick.set_input('Mirror Z', True)

            center_back = CabinetPart()
            center_back.create('Center Back')
            center_back.obj.parent = bay_obj
            center_back.obj['hb_part_role'] = PART_ROLE_CENTER_BACK
            center_back.obj.rotation_euler.x = math.radians(90)
            center_back.set_input('Mirror Z', True)

            back_opening = ClosetOpening()
            back_opening.create('Opening 1 Back')
            back_opening.obj.parent = bay_obj
            back_opening.obj['hb_opening_index'] = 1
            back_opening.obj[PROP_OPENING_SIDE] = 'BACK'

        opening = ClosetOpening()
        opening.create('Opening 1')
        opening.obj.parent = bay_obj
        opening.obj['hb_opening_index'] = 0

    # -----------------------------------------------------------------
    # Child lookups
    # -----------------------------------------------------------------
    def _sorted_bays(self):
        bays = [c for c in self.obj.children if c.get(TAG_BAY_CAGE)]
        bays.sort(key=lambda o: o.get('hb_bay_index', 0))
        return bays

    def _sorted_panels(self):
        panels = [c for c in self.obj.children
                  if c.get('hb_part_role') == PART_ROLE_PANEL]
        panels.sort(key=lambda o: o.get('hb_panel_index', 0))
        return panels

    def _root_part(self, role):
        for c in self.obj.children:
            if c.get('hb_part_role') == role:
                return c
        return None

    def _bay_part(self, bay_obj, role):
        for c in bay_obj.children:
            if c.get('hb_part_role') == role:
                return c
        return None

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def _spec_from_props(self, scene_props):
        sp = self.obj.hb_closet_starter
        bays = []
        for bay_obj in self._sorted_bays():
            bp = bay_obj.hb_closet_bay
            bays.append({
                'width': bp.width,
                'locked': bp.width_locked,
                'height': bp.height,
                'depth': bp.depth,
                'floor': bp.floor_mounted,
                'remove_bottom': bp.remove_bottom,
                'remove_cleat': bp.remove_cleat,
            })
        return SimpleNamespace(
            width=sp.width,
            height=sp.height,
            pt=scene_props.panel_thickness,
            st=scene_props.shelf_thickness,
            kick_height=sp.toe_kick_height,
            kick_setback=sp.toe_kick_setback,
            bays=bays,
        )

    def recalculate(self):
        """Read props -> solve layout -> write every part. Safe to call
        repeatedly; guarded against reentry from prop update callbacks."""
        cabinet_id = id(self.obj)
        if cabinet_id in _RECALCULATING:
            return
        _RECALCULATING.add(cabinet_id)
        try:
            scene_props = bpy.context.scene.hb_closets
            sp = self.obj.hb_closet_starter

            # Starter height/depth edits propagate to every bay still at
            # the previous starter value; individually overridden bays
            # keep their override. The last-applied values ride idprops
            # (also used below for the hanging top-anchor). Bay writes
            # here can't recurse - the update callbacks bail while this
            # starter is in _RECALCULATING.
            last_h = self.obj.get('hb_last_height')
            last_d = self.obj.get('hb_last_depth')
            for bay_obj in self._sorted_bays():
                bp = bay_obj.hb_closet_bay
                if (last_h is not None
                        and abs(bp.height - last_h) < 1e-6
                        and abs(sp.height - last_h) > 1e-9):
                    bp.height = sp.height
                if (last_d is not None
                        and abs(bp.depth - last_d) < 1e-6
                        and abs(sp.depth - last_d) > 1e-9):
                    bp.depth = sp.depth
            self.obj['hb_last_depth'] = sp.depth

            spec = self._spec_from_props(scene_props)
            if not spec.bays:
                return
            layout = solver.compute_layout(spec)

            # Write redistributed widths back without auto-locking them.
            _DISTRIBUTING_WIDTHS.add(cabinet_id)
            try:
                for bay_obj, w in zip(self._sorted_bays(), layout['widths']):
                    bay_obj.hb_closet_bay.width = w
            finally:
                _DISTRIBUTING_WIDTHS.discard(cabinet_id)

            self._layout_panels(layout, scene_props)
            self._layout_bays(layout, scene_props, sp)
            self._layout_starter_parts(layout, scene_props, sp)
            self._layout_bridge_parts(layout, scene_props, sp)

            # Hanging starters anchor at their TOP (the wall mount): a
            # height edit grows the unit downward. The last-applied
            # height rides an idprop so only true height edits shift the
            # origin - manual moves (G) are untouched.
            if sp.closet_type == 'HANGING':
                last_h = self.obj.get('hb_last_height')
                if last_h is not None and abs(last_h - sp.height) > 1e-9:
                    self.obj.location.z += (last_h - sp.height)
            self.obj['hb_last_height'] = sp.height

            self.set_input('Dim X', sp.width)
            self.set_input('Dim Y', sp.depth)
            self.set_input('Dim Z', sp.height)
        finally:
            _RECALCULATING.discard(cabinet_id)

    def _layout_panels(self, layout, scene_props):
        pt = scene_props.panel_thickness
        for child, panel in zip(self._sorted_panels(), layout['panels']):
            child.location = (panel['x'], 0.0, panel['z'])
            part = GeoNodeCutpart(child)
            part.set_input('Length', panel['length'])
            part.set_input('Width', panel['depth'])
            part.set_input('Thickness', pt)

    def _layout_bays(self, layout, scene_props, sp):
        st = scene_props.shelf_thickness
        for bay_obj, bay in zip(self._sorted_bays(), layout['bays']):
            cage = GeoNodeCage(bay_obj)
            bay_obj.location = (bay['x'], 0.0, bay['z0'])
            cage.set_input('Dim X', bay['width'])
            cage.set_input('Dim Y', bay['depth'])
            cage.set_input('Dim Z', bay['height'])
            bp = bay_obj.hb_closet_bay

            bottom = self._bay_part(bay_obj, PART_ROLE_BOTTOM_SHELF)
            if bottom is not None:
                bottom.location = (0.0, 0.0, bay['bottom_z'])
                part = GeoNodeCutpart(bottom)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['depth'])
                part.set_input('Thickness', st)
                _set_part_hidden(bottom, bp.remove_bottom)

            top = self._bay_part(bay_obj, PART_ROLE_TOP_SHELF)
            if top is not None:
                top.location = (0.0, 0.0, bay['top_z'])
                part = GeoNodeCutpart(top)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['depth'])
                part.set_input('Thickness', st)
                _set_part_hidden(top, False)

            for kick in bay_obj.children:
                if kick.get('hb_part_role') != PART_ROLE_TOE_KICK:
                    continue
                if kick.get('hb_rear'):
                    kick.location = (0.0, -sp.toe_kick_setback, 0.0)
                else:
                    kick.location = (0.0, -bay['depth'] + sp.toe_kick_setback,
                                     0.0)
                part = GeoNodeCutpart(kick)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['kick'])
                part.set_input('Thickness', st)
                _set_part_hidden(kick, (not bay['floor'])
                                 or bp.remove_bottom
                                 or bay['kick'] <= 0.0)

            cleat = self._bay_part(bay_obj, PART_ROLE_CLEAT)
            if cleat is not None:
                cleat.location = (0.0, 0.0, bay['cleat_z'])
                part = GeoNodeCutpart(cleat)
                part.set_input('Length', bay['width'])
                part.set_input('Width', const.CLEAT_WIDTH)
                part.set_input('Thickness', st)
                _set_part_hidden(cleat, bp.remove_cleat
                                 or bool(cleat.get('hb_always_hidden')))

            # Hang rail: the wall strip each bay hangs from / anchors
            # to. Lazily created (like the countertop) so starters
            # built before rails existed gain one on their next
            # recalculate. Bay-local: against the back plane (y=0,
            # thickness into the room), rail bottom HANG_RAIL_DROP
            # below the bay top, spanning the bay interior. Root
            # idprop 'hb_remove_hang_rail' hides the whole starter's
            # rails.
            rail = self._bay_part(bay_obj, PART_ROLE_HANG_RAIL)
            if rail is None and self.has_hang_rail:
                rail_part = CabinetPart()
                rail_part.create('Hang Rail')
                rail_part.obj.parent = bay_obj
                rail_part.obj['hb_part_role'] = PART_ROLE_HANG_RAIL
                rail_part.obj.rotation_euler.x = math.radians(90)
                rail = rail_part.obj
            if rail is not None:
                rail.location = (
                    0.0, 0.0,
                    bay['height'] - const.HANG_RAIL_DROP)
                part = GeoNodeCutpart(rail)
                part.set_input('Length', bay['width'])
                part.set_input('Width', const.HANG_RAIL_WIDTH)
                part.set_input('Thickness', const.HANG_RAIL_THICKNESS)
                _set_part_hidden(
                    rail, (not self.has_hang_rail)
                    or bool(self.obj.get('hb_remove_hang_rail')))

            back = self._bay_part(bay_obj, PART_ROLE_APPLIED_BACK)
            if back is not None:
                back.location = (0.0, 0.0, bay['interior_z'])
                part = GeoNodeCutpart(back)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['interior_h'])
                part.set_input('Thickness', const.APPLIED_BACK_THICKNESS)
                _set_part_hidden(back, False)

            # Center back (double islands): st thick, centered in depth,
            # spanning the interior. Horizontal grain for now; the
            # machining layer decides grain later.
            center_back = self._bay_part(bay_obj, PART_ROLE_CENTER_BACK)
            if center_back is not None:
                center_back.location = (
                    0.0, -(bay['depth'] / 2.0 + st / 2.0), bay['interior_z'])
                part = GeoNodeCutpart(center_back)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['interior_h'])
                part.set_input('Thickness', st)

            # Openings. Fixed shelves are SPLITTERS: committed shelves
            # live at bay level and divide the interior into segments,
            # one opening cage per segment (per side on double islands).
            # The reconciler adopts freshly committed shelves, matches
            # the opening count to the segments, and preserves contents
            # when a shelf removal merges segments.
            self._reconcile_bay_openings(bay_obj)
            half_depth = (bay['depth'] - st) / 2.0
            sides = ('FRONT', 'BACK') if self.is_double else ('FRONT',)
            for side in sides:
                if self.is_double:
                    o_depth = half_depth
                    base_y = (0.0 if side == 'BACK'
                              else -(bay['depth'] / 2.0 + st / 2.0))
                else:
                    o_depth = bay['depth']
                    base_y = 0.0

                # Splitting shelves: clamp into the interior, lay out at
                # bay level, and collect the segment boundaries.
                boundaries = []
                for sh in self._bay_split_shelves(bay_obj, side):
                    z_off = max(0.0, min(sh.get('hb_z_offset', 0.0),
                                         bay['interior_h'] - st))
                    sh['hb_z_offset'] = float(z_off)
                    sh.location = (0.0, base_y, bay['interior_z'] + z_off)
                    part = GeoNodeCutpart(sh)
                    part.set_input('Length', bay['width'])
                    part.set_input('Width', o_depth)
                    part.set_input('Thickness', st)
                    _set_part_hidden(sh, False)
                    boundaries.append(z_off)

                openings = sorted(
                    [c for c in bay_obj.children
                     if c.get(TAG_OPENING_CAGE)
                     and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                    key=lambda o: o.get('hb_opening_index', 0))
                bottoms = [0.0] + [b + st for b in boundaries]
                tops = boundaries + [bay['interior_h']]
                for op_obj, b0, t0 in zip(openings, bottoms, tops):
                    seg_h = max(t0 - b0, 0.01)
                    op_obj['hb_seg_bottom'] = float(b0)
                    op_obj.location = (0.0, base_y,
                                       bay['interior_z'] + b0)
                    op_cage = GeoNodeCage(op_obj)
                    op_cage.set_input('Dim X', bay['width'])
                    op_cage.set_input('Dim Y', o_depth)
                    op_cage.set_input('Dim Z', seg_h)
                    self._layout_opening_parts(op_obj, bay['width'],
                                               o_depth, seg_h, scene_props)

                # Bay-wide doors span the full interior (all segments).
                self._layout_bay_doors(bay_obj, side, bay, base_y,
                                       o_depth, scene_props)

    def _layout_opening_parts(self, opening, width, depth, interior_h,
                              scene_props):
        """Reconcile + lay out user-added parts and inserts in
        opening-local coords.

        Fixed shelves / rods keep their stored offset (from the bottom,
        or from the top when anchored there) clamped into the interior.
        Adjustable shelves / doors / drawers / cubbies are reconciled to
        the opening's config idprops (regenerators create/remove children
        to match, so config edits and old files always converge).

        Fronts use the legacy half-overlay convention: each edge overlays
        its shared panel/shelf by (thickness - gap)/2. On a double
        island's BACK opening the fronts flip to the y=0 face (Mirror Z
        flips the extrude direction, set at part creation).
        """
        st = scene_props.shelf_thickness
        pt = scene_props.panel_thickness
        side = opening.get(PROP_OPENING_SIDE, 'FRONT')

        self._reconcile_adj_shelves(opening)
        self._reconcile_doors(opening, side)
        self._reconcile_drawers(opening, side)
        self._reconcile_cubbies(opening)

        lo = ro = (pt - const.FRONT_GAP) / 2.0
        to = bo = (st - const.FRONT_GAP) / 2.0
        if side == 'BACK':
            front_y = const.DOOR_TO_CABINET_GAP
        else:
            front_y = -depth - const.DOOR_TO_CABINET_GAP

        groups = {}
        for child in list(opening.children):
            role = child.get('hb_part_role')
            if role == PART_ROLE_FIXED_SHELF:
                z_off = child.get('hb_z_offset', 0.0)
                z = (interior_h - z_off if child.get('hb_anchor_top')
                     else z_off)
                z = max(0.0, min(z, interior_h - st))
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)
            elif role == PART_ROLE_ROD:
                z_off = child.get('hb_z_offset', const.ROD_TOP_OFFSET)
                z = (interior_h - z_off if child.get('hb_anchor_top')
                     else z_off)
                z = max(const.ROD_RADIUS,
                        min(z, interior_h - const.ROD_RADIUS))
                # Rod centerline sits 12" out from the rear (wall side,
                # Y=0), clamped to stay within a shallow opening.
                rod_y = -min(const.ROD_FROM_REAR, max(depth - const.ROD_RADIUS,
                                                      const.ROD_RADIUS))
                child.location = (0.0, rod_y, z)
                rod_geo = GeoNodeObject(child)
                rod_geo.set_input('Dim X', width)
                # Rod profile + finish follow the scene rod options.
                props = bpy.context.scene.hb_closets
                rod_geo.set_input(
                    'Is Oval',
                    getattr(props, 'closet_rod_type', 'OVAL') == 'OVAL')
                try:
                    from . import pulls_closets
                    rod_mat = pulls_closets.load_finish_material(
                        getattr(props, 'closet_rod_finish',
                                'Polished Chrome'))
                    if rod_mat is not None:
                        rod_geo.set_input('Material', rod_mat)
                    pulls_closets.reconcile_rod_hangers(child, width)
                except Exception:
                    pass
            elif role is not None:
                groups.setdefault(role, []).append(child)

        # ----- Adjustable shelves: even spacing bottom-up -----
        adj = groups.get(PART_ROLE_ADJ_SHELF, [])
        if adj:
            adj.sort(key=lambda o: o.get('hb_adj_index', 0))
            spacing = interior_h / (len(adj) + 1)
            for i, child in enumerate(adj):
                z = max(0.0, min(spacing * (i + 1), interior_h - st))
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)

        # ----- Doors (1 leaf, or 2 for DOUBLE swing) -----
        doors = groups.get(PART_ROLE_DOOR, [])
        if doors:
            doors.sort(key=lambda o: o.get('hb_door_index', 0))
            full = width + lo + ro
            if len(doors) == 2:
                leaf = (full - const.FRONT_GAP) / 2.0
            else:
                leaf = full
            for i, child in enumerate(doors):
                x = -lo + i * (leaf + const.FRONT_GAP)
                child.location = (x, front_y, -bo)
                part = GeoNodeCutpart(child)
                part.set_input('Length', leaf)
                part.set_input('Width', interior_h + to + bo)
                part.set_input('Thickness', const.FRONT_THICKNESS)
                _apply_front_style(child, is_drawer=False)
                _stash_door_closed(child, x, front_y, -bo, leaf, side)
                self._position_front_pull(
                    child,
                    'hamper' if child.get('hb_is_hamper') else 'door',
                    side)
                apply_door_open(
                    child, 1.0 if child.get('hb_door_open') else 0.0)

        # ----- Drawer stack (bottom-up fronts + boxes) -----
        # The stack FILLS the opening: fronts span the full front extent
        # (interior_h + to + bo) less the inter-front gaps. Unlocked fronts
        # share the remainder equally; a front the user has resized holds
        # its height (hb_front_locked) while the rest absorb the difference.
        fronts = groups.get(PART_ROLE_DRAWER_FRONT, [])
        boxes = {c.get('hb_drawer_index', 0): c
                 for c in groups.get(PART_ROLE_DRAWER_BOX, [])}
        if fronts:
            fronts.sort(key=lambda o: o.get('hb_drawer_index', 0))
            n = len(fronts)
            span = interior_h + to + bo
            avail = span - (n - 1) * const.FRONT_GAP
            heights = _distribute_front_heights(
                avail,
                [(f.get(PROP_FRONT_HEIGHT, 0.0),
                  bool(f.get(PROP_FRONT_LOCKED, 0))) for f in fronts])
            from . import drawer_boxes_closets as dbx
            box_type = dbx.current_type()
            box_mat = dbx.box_material(box_type)
            box_w = max(width - 2 * const.DRAWER_SLIDE_GAP, inch(2.0))
            wood_d = max(depth - const.DRAWER_BOX_DEPTH_DEDUCT, inch(2.0))
            z = -bo
            for i, child in enumerate(fronts):
                dh = heights[i]
                # Persist the resolved height so overlay labels read it.
                child[PROP_FRONT_HEIGHT] = dh
                child.location = (-lo, front_y, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width + lo + ro)
                part.set_input('Width', dh)
                part.set_input('Thickness', const.FRONT_THICKNESS)
                _apply_front_style(child, is_drawer=True)
                self._position_front_pull(child, 'drawer', side)
                box = boxes.get(i)
                # Selected drawer box system decides the box proportions
                # (standard heights/slide lengths) or turns boxes off;
                # the WOOD path keeps the parametric deduct behavior.
                wood_h = max(dh - const.DRAWER_BOX_HEIGHT_DEDUCT,
                             inch(2.0))
                spec = dbx.size_box(box_type, dh, depth, wood_h, wood_d)
                box_d = spec[1] if spec is not None else wood_d
                if box is not None:
                    box['hb_drawer_box_type'] = box_type
                    box['hb_drawer_box_size'] = (spec[2] if spec
                                                 else 'NONE')
                    _set_part_hidden(box, spec is None)
                if box is not None and spec is not None:
                    box_h = spec[0]
                    # GeoNodeDrawerBox extrudes +Y from its origin, so
                    # anchor the origin at the face the drawer serves:
                    # box spans [y_box, y_box + box_d], front edge flush
                    # with the opening face, clearance at the rear.
                    y_box = (-box_d if side == 'BACK' else -depth)
                    box.location = (const.DRAWER_SLIDE_GAP, y_box,
                                    max(z, 0.0) + const.DRAWER_BOX_Z_LIFT)
                    gb = GeoNodeObject(box)
                    gb.set_input('Dim X', box_w)
                    gb.set_input('Dim Y', box_d)
                    gb.set_input('Dim Z', box_h)
                    # Always write the slot: None resets a previously
                    # applied system material to the node default (the
                    # WOOD look) when the selection changes.
                    try:
                        gb.set_input('Material', box_mat)
                    except Exception:
                        pass
                # Open-drawer support: stash closed Y + travel, then apply
                # the persistent open state (Open Door mode toggles it).
                travel = min(box_d, inch(12.0))
                _stash_drawer_closed(child, box, travel, side)
                apply_drawer_open(
                    child, 1.0 if child.get('hb_drawer_open') else 0.0)
                z += dh + const.FRONT_GAP

        # ----- Cubby grid (divisions full height, shelves full width) -----
        divs = groups.get(PART_ROLE_CUBBY_DIVISION, [])
        if divs:
            divs.sort(key=lambda o: o.get('hb_cubby_index', 0))
            cols = len(divs) + 1
            cell_w = (width - len(divs) * st) / cols
            for j, child in enumerate(divs):
                x = cell_w * (j + 1) + st * j
                child.location = (x, 0.0, 0.0)
                part = GeoNodeCutpart(child)
                part.set_input('Length', interior_h)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)
        cub_shelves = groups.get(PART_ROLE_CUBBY_SHELF, [])
        if cub_shelves:
            cub_shelves.sort(key=lambda o: o.get('hb_cubby_index', 0))
            rows = len(cub_shelves) + 1
            cell_h = (interior_h - len(cub_shelves) * st) / rows
            for k, child in enumerate(cub_shelves):
                z = cell_h * (k + 1) + st * k
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)

    # ----- regenerators (create/remove children to match config) -----

    def _position_front_pull(self, front, kind, side):
        """Create/refresh the pull on a door / drawer / hamper front,
        using the face_frame pull assets and scene defaults (shared
        hardware across libraries). Closet front local space: X = width
        across, Y = height up, front face at Z = thickness. Doors get a
        vertical bar on the latch edge; drawers a centered horizontal
        bar; hampers a horizontal bar near the top. BACK-side island
        fronts are pending (mirrored mounting)."""
        existing = next((c for c in front.children
                         if c.get('IS_CABINET_PULL')), None)
        try:
            from . import pulls_closets
            from ..face_frame import split_preview
            from ... import units
        except Exception:
            return
        pull_obj = None
        if side != 'BACK':
            pull_obj = pulls_closets.resolve_pull_object()
        if pull_obj is None:
            if existing is not None:
                bpy.data.objects.remove(existing, do_unlink=True)
            return
        # Closet-scoped placement settings; getattr defaults keep the
        # math working when the scene props are not registered.
        cp = bpy.context.scene.hb_closets
        v_base = getattr(cp, 'pull_vertical_location_base',
                         units.inch(1.5))
        v_tall = getattr(cp, 'pull_vertical_location_tall',
                         units.inch(45.0))
        v_upper = getattr(cp, 'pull_vertical_location_upper',
                          units.inch(1.5))
        h_edge = getattr(cp, 'pull_horizontal_offset', units.inch(2.0))
        part = GeoNodeCutpart(front)
        width = part.get_input('Length')
        height = part.get_input('Width')
        thickness = part.get_input('Thickness')
        half = pulls_closets.pull_length(pull_obj) / 2.0
        z = thickness

        if kind == 'drawer':
            x = width / 2.0
            if getattr(cp, 'center_pulls_on_drawer_front', True):
                y = height / 2.0
            else:
                y = height - v_base - half
            rot = (math.radians(-90.0), 0.0, 0.0)
        elif kind == 'hamper':
            x = width / 2.0
            y = height - v_base - half
            rot = (math.radians(-90.0), 0.0, 0.0)
        else:
            hinge = front.get('hb_hinge', 'LEFT')
            # 5-piece doors center the pull on the latch stile; slab
            # doors keep the fixed from-edge offset.
            stile_w = None
            mod = next((m for m in front.modifiers
                        if m.type == 'NODES' and 'Door Style' in m.name),
                       None)
            if mod is not None and mod.node_group is not None:
                for item in mod.node_group.interface.items_tree:
                    if (item.item_type == 'SOCKET'
                            and item.in_out == 'INPUT'
                            and item.name == 'Left Stile Width'):
                        stile_w = hb_utils.try_get_gn_input(mod, item.identifier)
                        break
            offset = (stile_w / 2.0) if stile_w else h_edge
            if hinge == 'LEFT':
                x = width - offset
            else:
                x = offset
            # Base / Tall / Upper rule, floor-referenced: hold the pull
            # at the TALL height off the floor; when the door bottom is
            # already above that height use the UPPER convention (near
            # the bottom edge); when the tall height would land past
            # the door top use the BASE convention (near the top edge).
            bottom_w = split_preview._world_matrix(front).translation.z
            tall_target = v_tall
            if bottom_w >= tall_target:
                y = v_upper + half
            else:
                tall_y = (tall_target - bottom_w) + half
                base_y = height - v_base - half
                y = tall_y if tall_y <= base_y else base_y
            rot = (math.radians(-90.0), 0.0, math.radians(90.0))

        if existing is not None:
            inst = existing
            if inst.data is not pull_obj.data:
                inst.data = pull_obj.data
        else:
            inst = bpy.data.objects.new(f"Pull - {front.name}",
                                        pull_obj.data)
            bpy.context.scene.collection.objects.link(inst)
            inst.parent = front
            inst['hb_part_role'] = 'PULL'
            inst['IS_CABINET_PULL'] = True
        # Model name rides the instance (the mesh datablock name is the
        # asset's internal name) - pricing keys on it.
        inst['hb_pull_name'] = pulls_closets.current_pull_stem()
        inst.location = (x, y, z)
        inst.rotation_euler = rot

    def _reconcile_adj_shelves(self, opening):
        qty = max(0, int(opening.get(PROP_ADJ_SHELF_QTY, 0)))
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_ADJ_SHELF]
        existing.sort(key=lambda o: o.get('hb_adj_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        while len(existing) < qty:
            obj = add_fixed_shelf(opening, 0.0, role=PART_ROLE_ADJ_SHELF)
            obj['hb_adj_index'] = len(existing)
            existing.append(obj)

    def _make_front(self, opening, name, role, side):
        """Vertical slab front. rot_x 90 stands the part up (thickness
        extrudes -Y); BACK-side fronts Mirror Z to extrude +Y instead."""
        front = CabinetPart()
        front.create(name)
        front.obj.parent = opening
        front.obj['hb_part_role'] = role
        front.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        front.obj.rotation_euler.x = math.radians(90)
        if side == 'BACK':
            front.set_input('Mirror Z', True)
        return front.obj

    def _reconcile_bay_doors(self, bay_obj, side):
        """Bay-wide doors: parented to the bay cage, hb_bay_door=1.
        FRONT side only for now (double-island back-side bay doors are a
        follow-up)."""
        swing = (bay_obj.get(PROP_BAY_DOOR_SWING, '')
                 if side == 'FRONT' else '')
        qty = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2}.get(swing, 0)
        existing = [c for c in bay_obj.children
                    if c.get('hb_part_role') == PART_ROLE_DOOR
                    and c.get('hb_bay_door')]
        existing.sort(key=lambda o: o.get('hb_door_index', 0))
        while len(existing) > qty:
            _remove_part_tree(existing.pop())  # front + its pull
        while len(existing) < qty:
            name = ('Hamper Front' if bay_obj.get(PROP_BAY_IS_HAMPER)
                    else 'Door')
            front = CabinetPart()
            front.create(name)
            front.obj.parent = bay_obj
            front.obj['hb_part_role'] = PART_ROLE_DOOR
            front.obj['hb_bay_door'] = 1
            front.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            front.obj.rotation_euler.x = math.radians(90)
            front.obj['hb_door_index'] = len(existing)
            front.obj['hb_is_hamper'] = (
                1 if bay_obj.get(PROP_BAY_IS_HAMPER) else 0)
            existing.append(front.obj)
        for i, obj in enumerate(existing):
            if swing == 'DOUBLE':
                obj['hb_hinge'] = 'LEFT' if i == 0 else 'RIGHT'
            else:
                obj['hb_hinge'] = swing or 'LEFT'
        return existing

    def _layout_bay_doors(self, bay_obj, side, bay, base_y, o_depth,
                          scene_props):
        doors = self._reconcile_bay_doors(bay_obj, side)
        if not doors:
            return
        st = scene_props.shelf_thickness
        pt = scene_props.panel_thickness
        lo = ro = (pt - const.FRONT_GAP) / 2.0
        to = bo = (st - const.FRONT_GAP) / 2.0
        front_y = base_y - o_depth - const.DOOR_TO_CABINET_GAP
        width = bay['width']
        interior_h = bay['interior_h']
        full = width + lo + ro
        leaf = (full - const.FRONT_GAP) / 2.0 if len(doors) == 2 else full
        for i, child in enumerate(doors):
            x = -lo + i * (leaf + const.FRONT_GAP)
            z = bay['interior_z'] - bo
            child.location = (x, front_y, z)
            part = GeoNodeCutpart(child)
            part.set_input('Length', leaf)
            part.set_input('Width', interior_h + to + bo)
            part.set_input('Thickness', const.FRONT_THICKNESS)
            _apply_front_style(child, is_drawer=False)
            _stash_door_closed(child, x, front_y, z, leaf, side)
            self._position_front_pull(
                child, 'hamper' if child.get('hb_is_hamper') else 'door',
                side)
            apply_door_open(
                child, 1.0 if child.get('hb_door_open') else 0.0)

    def _reconcile_doors(self, opening, side):
        # A bay-wide door supersedes opening doors on its side.
        bay = find_bay_cage(opening)
        if (side == 'FRONT' and bay is not None
                and bay.get(PROP_BAY_DOOR_SWING)):
            swing = ''
        else:
            swing = opening.get(PROP_DOOR_SWING, '')
        qty = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2}.get(swing, 0)
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_DOOR]
        existing.sort(key=lambda o: o.get('hb_door_index', 0))
        while len(existing) > qty:
            _remove_part_tree(existing.pop())  # front + its pull
        while len(existing) < qty:
            name = 'Hamper Front' if opening.get(PROP_IS_HAMPER) else 'Door'
            obj = self._make_front(opening, name, PART_ROLE_DOOR, side)
            obj['hb_door_index'] = len(existing)
            obj['hb_is_hamper'] = 1 if opening.get(PROP_IS_HAMPER) else 0
            existing.append(obj)
        # Hinge side per leaf (drives pull placement): singles hinge on
        # their swing side; a DOUBLE pair hinges outward so the pulls
        # meet at the center.
        for i, obj in enumerate(existing):
            if swing == 'DOUBLE':
                obj['hb_hinge'] = 'LEFT' if i == 0 else 'RIGHT'
            else:
                obj['hb_hinge'] = swing or 'LEFT'

    def _reconcile_drawers(self, opening, side):
        qty = max(0, int(opening.get(PROP_DRAWER_QTY, 0)))
        fronts = [c for c in opening.children
                  if c.get('hb_part_role') == PART_ROLE_DRAWER_FRONT]
        boxes = [c for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_DRAWER_BOX]
        fronts.sort(key=lambda o: o.get('hb_drawer_index', 0))
        boxes.sort(key=lambda o: o.get('hb_drawer_index', 0))
        while len(fronts) > qty:
            _remove_part_tree(fronts.pop())  # front + its pull
        while len(boxes) > qty:
            bpy.data.objects.remove(boxes.pop(), do_unlink=True)
        while len(fronts) < qty:
            obj = self._make_front(opening, 'Drawer Front',
                                   PART_ROLE_DRAWER_FRONT, side)
            obj['hb_drawer_index'] = len(fronts)
            fronts.append(obj)
        while len(boxes) < qty:
            box = GeoNodeDrawerBox()
            box.create('Drawer Box')
            box.obj.parent = opening
            box.obj['hb_part_role'] = PART_ROLE_DRAWER_BOX
            box.obj['hb_drawer_index'] = len(boxes)
            boxes.append(box.obj)

    def _reconcile_cubbies(self, opening):
        cols = max(1, int(opening.get(PROP_CUBBY_COLS, 1)))
        rows = max(1, int(opening.get(PROP_CUBBY_ROWS, 1)))
        want_divs = cols - 1
        want_shelves = rows - 1
        divs = [c for c in opening.children
                if c.get('hb_part_role') == PART_ROLE_CUBBY_DIVISION]
        shelves = [c for c in opening.children
                   if c.get('hb_part_role') == PART_ROLE_CUBBY_SHELF]
        divs.sort(key=lambda o: o.get('hb_cubby_index', 0))
        shelves.sort(key=lambda o: o.get('hb_cubby_index', 0))
        while len(divs) > want_divs:
            bpy.data.objects.remove(divs.pop(), do_unlink=True)
        while len(shelves) > want_shelves:
            bpy.data.objects.remove(shelves.pop(), do_unlink=True)
        while len(divs) < want_divs:
            div = CabinetPart()
            div.create('Cubby Division')
            div.obj.parent = opening
            div.obj['hb_part_role'] = PART_ROLE_CUBBY_DIVISION
            div.obj['hb_cubby_index'] = len(divs)
            div.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            div.obj.rotation_euler.y = math.radians(-90)
            div.set_input('Mirror Y', True)
            div.set_input('Mirror Z', True)
            divs.append(div.obj)
        while len(shelves) < want_shelves:
            obj = add_fixed_shelf(opening, 0.0, role=PART_ROLE_CUBBY_SHELF)
            obj['hb_cubby_index'] = len(shelves)
            shelves.append(obj)

    def _bay_split_shelves(self, bay_obj, side):
        """Committed splitting shelves of one side, bottom-up."""
        shelves = [c for c in bay_obj.children
                   if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF
                   and c.get(PROP_OPENING_SIDE, 'FRONT') == side
                   and not c.get('hb_preview')]
        shelves.sort(key=lambda o: o.get('hb_z_offset', 0.0))
        return shelves

    def _reconcile_bay_openings(self, bay_obj):
        """Adopt committed fixed shelves up to bay level (they arrive as
        opening children from the add-part modal / older files) and keep
        exactly one opening cage per interior segment on each side.
        Removing a shelf merges segments; the removed opening's contents
        re-home into the lowest surviving opening rather than dying."""
        for opening in [c for c in bay_obj.children
                        if c.get(TAG_OPENING_CAGE)]:
            seg_bottom = opening.get('hb_seg_bottom', 0.0)
            side = opening.get(PROP_OPENING_SIDE, 'FRONT')
            for child in list(opening.children):
                if (child.get('hb_part_role') == PART_ROLE_FIXED_SHELF
                        and not child.get('hb_preview')):
                    child.parent = bay_obj
                    # Opening-local -> bay-interior datum. Top-anchored
                    # offsets convert via the segment the shelf was in.
                    z_off = child.get('hb_z_offset', 0.0)
                    if child.get('hb_anchor_top'):
                        try:
                            seg_h = GeoNodeCage(opening).get_input('Dim Z')
                        except Exception:
                            seg_h = 0.0
                        z_off = max(0.0, seg_h - z_off)
                    child['hb_z_offset'] = float(seg_bottom + z_off)
                    child['hb_anchor_top'] = 0
                    child[PROP_OPENING_SIDE] = side

        sides = ('FRONT', 'BACK') if self.is_double else ('FRONT',)
        for side in sides:
            want = len(self._bay_split_shelves(bay_obj, side)) + 1
            openings = sorted(
                [c for c in bay_obj.children
                 if c.get(TAG_OPENING_CAGE)
                 and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                key=lambda o: o.get('hb_opening_index', 0))
            while len(openings) > want:
                extra = openings.pop()
                for child in list(extra.children):
                    child.parent = openings[0]
                bpy.data.objects.remove(extra, do_unlink=True)
            while len(openings) < want:
                op = ClosetOpening()
                op.create(f'Opening {len(openings) + 1}')
                op.obj.parent = bay_obj
                if side == 'BACK':
                    op.obj[PROP_OPENING_SIDE] = 'BACK'
                openings.append(op.obj)
            for i, op_obj in enumerate(openings):
                op_obj['hb_opening_index'] = i

    def _layout_starter_parts(self, layout, scene_props, sp):
        ctop = self._root_part(PART_ROLE_COUNTERTOP)
        if ctop is None and sp.include_countertop:
            # Lazily create the part so include_countertop works on
            # starters whose class didn't seed one (Tall/Hanging, and
            # units placed before this landed).
            part = CabinetPart()
            part.create('Countertop')
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_COUNTERTOP
            part.set_input('Mirror Y', True)
            ctop = part.obj
        if ctop is not None:
            part = GeoNodeCutpart(ctop)
            if self.ctop_overhang_all:
                oh = const.ISLAND_CTOP_OVERHANG
                ctop.location = (-oh, oh, sp.height)
                part.set_input('Length', sp.width + 2 * oh)
                part.set_input('Width', sp.depth + 2 * oh)
            else:
                ctop.location = (0.0, 0.0, sp.height)
                part.set_input('Length', sp.width)
                part.set_input('Width',
                               sp.depth + const.COUNTERTOP_OVERHANG_FRONT)
            part.set_input('Thickness', scene_props.countertop_thickness)
            _set_part_hidden(ctop, not sp.include_countertop)

    def _bridge_part(self, side, slot):
        for c in self.obj.children:
            if (c.get('hb_part_role') == PART_ROLE_BRIDGE_SHELF
                    and c.get('hb_bridge_side') == side
                    and c.get('hb_bridge_slot') == slot):
                return c
        return None

    def _layout_bridge_parts(self, layout, scene_props, sp):
        """Corner-clearance bridge shelves (idprop-driven, lazy-created
        like the countertop). When a starter is pulled back from a wall
        corner to leave access clearance beside a perpendicular
        neighbor, the top bridge shelf spans the gap from this starter's
        end panel to the neighbor's body; an optional bottom shelf +
        kick close the gap at the floor. Parts ride the corner-side
        bay's depth and shelf heights so they line up with that bay's
        fixed shelves (top_z / bottom_z are shelf undersides)."""
        st = scene_props.shelf_thickness
        for side in ('LEFT', 'RIGHT'):
            key = side.lower()
            enabled = bool(self.obj.get(f'hb_bridge_{key}'))
            span = float(self.obj.get(f'hb_bridge_w_{key}', 0.0))
            bottom_on = (enabled
                         and bool(self.obj.get(f'hb_bridge_bot_{key}')))
            bay = layout['bays'][0 if side == 'LEFT' else -1]
            base_x = -span if side == 'LEFT' else sp.width
            specs = (
                ('TOP', enabled),
                ('BOTTOM', bottom_on),
                ('KICK', bottom_on and bay['floor'] and bay['kick'] > 0.0),
            )
            for slot, slot_on in specs:
                part_obj = self._bridge_part(side, slot)
                show = slot_on and span > 1e-4
                if part_obj is None:
                    if not show:
                        continue
                    part = CabinetPart()
                    part.create(f"{side.title()} Bridge "
                                + ('Toe Kick' if slot == 'KICK'
                                   else 'Shelf'))
                    part.obj.parent = self.obj
                    part.obj['hb_part_role'] = PART_ROLE_BRIDGE_SHELF
                    part.obj['hb_bridge_side'] = side
                    part.obj['hb_bridge_slot'] = slot
                    if slot == 'KICK':
                        # Same stand-up orientation as the bay kicks.
                        part.obj.rotation_euler.x = math.radians(-90)
                    part.set_input('Mirror Y', True)
                    part_obj = part.obj
                cut = GeoNodeCutpart(part_obj)
                if slot == 'KICK':
                    # The strip runs past the far end of the gap by the
                    # kick setback so it meets the neighbor's recessed
                    # kick line instead of stopping at its side panel.
                    kick_len = span + sp.toe_kick_setback
                    kick_x = -kick_len if side == 'LEFT' else sp.width
                    part_obj.location = (
                        kick_x, -bay['depth'] + sp.toe_kick_setback, 0.0)
                    cut.set_input('Length', kick_len)
                    cut.set_input('Width', bay['kick'])
                else:
                    z = bay['z0'] + (bay['top_z'] if slot == 'TOP'
                                     else bay['bottom_z'])
                    part_obj.location = (base_x, 0.0, z)
                    cut.set_input('Length', span)
                    cut.set_input('Width', bay['depth'])
                cut.set_input('Thickness', st)
                _set_part_hidden(part_obj, not show)

    # -----------------------------------------------------------------
    # Structural mutation (insert / delete bay)
    # -----------------------------------------------------------------
    def insert_bay(self, anchor_index, direction):
        """Insert a new bay next to an existing one.

        direction: 'BEFORE' (new bay takes the anchor's slot) or 'AFTER'.
        The new bay copies the anchor's height/depth/floor_mounted and
        comes in unlocked at width 0, so the redistributor immediately
        gives it an equal share. Panel i is the LEFT panel of bay i, so
        inserting at index k adds one panel at index k+1 and bumps every
        panel index >= k+1 and bay index >= k.
        """
        bays = self._sorted_bays()
        if not bays:
            return None
        anchor_index = max(0, min(anchor_index, len(bays) - 1))
        anchor_bay = bays[anchor_index]
        k = anchor_index if direction == 'BEFORE' else anchor_index + 1

        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            for bay_obj in bays:
                idx = bay_obj.get('hb_bay_index', 0)
                if idx >= k:
                    bay_obj['hb_bay_index'] = idx + 1
                    bay_obj.hb_closet_bay.bay_index = idx + 1
            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx >= k + 1:
                    panel_obj['hb_panel_index'] = idx + 1

            panel = CabinetPart()
            panel.create(f'Partition {k + 2}')
            panel.obj.parent = self.obj
            panel.obj['hb_part_role'] = PART_ROLE_PANEL
            panel.obj['hb_panel_index'] = k + 1
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.set_input('Mirror Y', True)
            panel.set_input('Mirror Z', True)

            bay = ClosetBay()
            bay.create(f'Bay {k + 1}')
            bay.obj.parent = self.obj
            bay.obj['hb_bay_index'] = k
            src = anchor_bay.hb_closet_bay
            bp = bay.obj.hb_closet_bay
            bp.bay_index = k
            bp.width = 0.0
            bp.width_locked = False
            bp.height = src.height
            bp.depth = src.depth
            bp.floor_mounted = src.floor_mounted
            self._build_bay_parts(bay.obj)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()
        return bay.obj

    def delete_bay(self, bay_index):
        """Delete the bay at bay_index plus one shared panel. Refuses to
        leave zero bays. Deleting bay k removes panel k+1 (the panel to
        its right), except for the last bay which removes panel k."""
        bays = self._sorted_bays()
        if len(bays) <= 1:
            return False
        bay_index = max(0, min(bay_index, len(bays) - 1))
        removed_panel_idx = (bay_index + 1
                             if bay_index < len(bays) - 1 else bay_index)

        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            bay_obj = bays[bay_index]
            for child in list(bay_obj.children_recursive):
                bpy.data.objects.remove(child, do_unlink=True)
            bpy.data.objects.remove(bay_obj, do_unlink=True)

            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx == removed_panel_idx:
                    bpy.data.objects.remove(panel_obj, do_unlink=True)
                    break
            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx > removed_panel_idx:
                    panel_obj['hb_panel_index'] = idx - 1
            for other in self._sorted_bays():
                idx = other.get('hb_bay_index', 0)
                if idx > bay_index:
                    other['hb_bay_index'] = idx - 1
                    other.hb_closet_bay.bay_index = idx - 1
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()
        return True


# ---------------------------------------------------------------------------
# Starter subclasses
# ---------------------------------------------------------------------------
class BaseClosetStarter(ClosetStarter):
    default_closet_type = 'BASE'
    has_countertop = True


class TallClosetStarter(ClosetStarter):
    default_closet_type = 'TALL'


class HangingClosetStarter(ClosetStarter):
    """Same floor-standing envelope as Tall, but its bays hang from the
    run top (leaving open space below). Grabbing a bay's bottom edge and
    dragging it to the floor converts that bay to floor-mounted."""
    default_closet_type = 'HANGING'
    has_toe_kick = False       # initial bays hang (no kick shown)
    floor_mounted = False
    allows_toe_kick = True     # a bay dropped to the floor gets a kick

    def _default_bay_height(self, scene_props, sp):
        return scene_props.hanging_panel_height


class IslandClosetStarter(ClosetStarter):
    has_hang_rail = False
    """Single-sided island: Base geometry plus an applied back closing
    the rear face."""
    default_closet_type = 'ISLAND'
    has_countertop = True
    has_applied_back = True


class DoubleIslandClosetStarter(IslandClosetStarter):
    """Double-sided island: deep carcass accessible from both faces with
    a center back in each bay, rear toe kick, and a countertop that
    overhangs all around. Each bay carries FRONT and BACK openings."""
    has_applied_back = False
    is_double = True
    ctop_overhang_all = True
    default_depth = const.ISLAND_DOUBLE_DEPTH


class LShelfClosetStarter(GeoNodeCage):
    """Inside-corner L-shelf unit: two wing panels against the walls,
    wall support strips at the corner, and a stack of L-shaped shelves
    (a full-footprint cutpart with the inner corner notched out via
    CPM_CORNERNOTCH). No bays/openings - its own recalculate() lays the
    whole unit out. Local space: corner at the origin, right wing runs
    +X along the back wall, left wing runs -Y along the side wall.

    Reuses Closet_Starter_Props for W/H/D (so the overlay labels and
    prompts work unchanged); wing depths and shelf count ride idprops:
      'hb_l_left_depth' / 'hb_l_right_depth' / 'hb_l_shelf_qty'
    """
    default_closet_type = 'BASE'
    has_toe_kick = True
    floor_mounted = True
    is_corner = True
    # Placement flags read by the place modal.
    default_depth = const.L_SHELF_SIZE

    def default_height(self, scene_props):
        return {
            'BASE': scene_props.base_panel_height,
            'TALL': scene_props.tall_panel_height,
            'UPPER': scene_props.hanging_panel_height,
        }[self.default_closet_type]

    def create_starter(self, name, bay_qty=1):
        super().create(name)
        self.obj[TAG_STARTER_CAGE] = True
        self.obj['CLASS_NAME'] = self.__class__.__name__
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_starter_commands'
        self.obj.display_type = 'WIRE'
        self.set_input('Mirror Y', True)

        scene_props = bpy.context.scene.hb_closets
        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        try:
            sp = self.obj.hb_closet_starter
            sp.closet_type = ('HANGING'
                              if self.default_closet_type == 'UPPER'
                              else self.default_closet_type)
            sp.toe_kick_height = (scene_props.toe_kick_height
                                  if self.has_toe_kick else 0.0)
            sp.toe_kick_setback = scene_props.toe_kick_setback
            sp.include_countertop = False
            sp.l_left_depth = float(scene_props.default_panel_depth)
            sp.l_right_depth = float(scene_props.default_panel_depth)
            sp.l_shelf_qty = const.L_SHELF_QTY
            sp.l_back_width = float(const.L_BACK_STRIP_WIDTH)
            sp.l_flip_partition = False
            # Construction default with no prompt (wall offset).
            self.obj['hb_l_wall_offset'] = float(const.L_WALL_OFFSET)
            sp.width = const.L_SHELF_SIZE
            sp.height = self.default_height(scene_props)
            sp.depth = const.L_SHELF_SIZE
            self._build_parts(scene_props)
        finally:
            _RECALCULATING.discard(cabinet_id)
        self.recalculate()

    def _build_parts(self, scene_props):
        # Wing end panels (verticals like the run panels).
        for role_idx, pname in ((0, 'Right Wing Panel'),
                                (1, 'Left Wing Panel')):
            panel = CabinetPart()
            panel.create(pname)
            panel.obj.parent = self.obj
            panel.obj['hb_part_role'] = PART_ROLE_PANEL
            panel.obj['hb_panel_index'] = role_idx
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.set_input('Mirror Y', True)
            panel.set_input('Mirror Z', True)
        # Back Partition: one
        # full-height vertical strip lying parallel to the back wall
        # (or the side wall when flipped) that the L shelves notch
        # around. Construction only - all machining/tokens belong to
        # downstream machining, which reads the geometry,
        # role, and idprops left here.
        self._make_back_partition()
        # Toe kicks (one per wing front; hidden for hung units).
        for pname, rz, my, mz in (('Right Wing Kick', 0.0, True, False),
                                  ('Left Wing Kick', -90.0, True, True)):
            kick = CabinetPart()
            kick.create(pname)
            kick.obj.parent = self.obj
            kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK
            kick.obj['hb_l_kick'] = pname
            kick.obj.rotation_euler.x = math.radians(-90)
            kick.obj.rotation_euler.z = math.radians(rz)
            kick.set_input('Mirror Y', my)
            kick.set_input('Mirror Z', mz)

    def _make_back_partition(self):
        part = CabinetPart()
        part.create('Back Partition')
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = PART_ROLE_PANEL
        part.obj['hb_panel_index'] = 2
        part.obj['hb_l_partition'] = True
        # Width-lookup key read by downstream machining (the
        # back-support width the L-shelf rear machining derives from).
        part.obj['hb_l_strip'] = 'Back Partition'
        part.obj.rotation_euler.y = math.radians(-90)
        part.set_input('Mirror Y', True)
        part.set_input('Mirror Z', True)
        return part

    def _reconcile_back_partition(self):
        """Ensure one Back Partition exists; drop the earlier horizontal
        wall strips (pre-partition construction) from older files."""
        part = None
        for c in list(self.obj.children):
            if c.get('hb_l_partition'):
                part = c
            elif c.get('hb_l_strip') in ('Back Wall Strip',
                                         'Side Wall Strip'):
                bpy.data.objects.remove(c, do_unlink=True)
        if part is None:
            part = self._make_back_partition().obj
        return part

    def _reconcile_l_shelves(self):
        want = max(0, int(self.obj.hb_closet_starter.l_shelf_qty)) + 2
        shelves = [c for c in self.obj.children
                   if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF]
        shelves.sort(key=lambda o: o.get('hb_l_index', 0))
        while len(shelves) > want:
            bpy.data.objects.remove(shelves.pop(), do_unlink=True)
        while len(shelves) < want:
            shelf = CabinetPart()
            shelf.create('L Shelf')
            shelf.obj.parent = self.obj
            shelf.obj['hb_part_role'] = PART_ROLE_FIXED_SHELF
            shelf.obj['hb_l_index'] = len(shelves)
            shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            shelf.set_input('Mirror Y', True)
            shelf.add_part_modifier('CPM_CORNERNOTCH', 'L Notch')
            shelf.add_part_modifier('CPM_CORNERNOTCH', 'Back Notch')
            shelves.append(shelf.obj)
        # Older files: shelves created before the Back Partition landed
        # have no Back Notch modifier - add it so they reconcile.
        for shelf in shelves:
            if shelf.modifiers.get('Back Notch') is None:
                GeoNodeCutpart(shelf).add_part_modifier(
                    'CPM_CORNERNOTCH', 'Back Notch')
        return shelves

    def recalculate(self):
        cabinet_id = id(self.obj)
        if cabinet_id in _RECALCULATING:
            return
        _RECALCULATING.add(cabinet_id)
        try:
            scene_props = bpy.context.scene.hb_closets
            sp = self.obj.hb_closet_starter
            # One-time migration: pre-prompt idprops -> product prompts
            # (updates are no-ops here; we're inside _RECALCULATING).
            for key, attr, cast in (('hb_l_left_depth', 'l_left_depth', float),
                                    ('hb_l_right_depth', 'l_right_depth', float),
                                    ('hb_l_shelf_qty', 'l_shelf_qty', int)):
                if key in self.obj:
                    setattr(sp, attr, cast(self.obj[key]))
                    del self.obj[key]
            st = scene_props.shelf_thickness
            pt = scene_props.panel_thickness
            W, D, H = sp.width, sp.depth, sp.height
            LD = min(sp.l_left_depth, W - pt)
            RD = min(sp.l_right_depth, D - pt)
            bw = sp.l_back_width
            flip = sp.l_flip_partition
            wo = self.obj.get('hb_l_wall_offset', const.L_WALL_OFFSET)
            floor = self.floor_mounted
            kick = sp.toe_kick_height if floor else 0.0
            setback = sp.toe_kick_setback

            panels = sorted([c for c in self.obj.children
                             if c.get('hb_part_role') == PART_ROLE_PANEL
                             and not c.get('hb_l_partition')],
                            key=lambda o: o.get('hb_panel_index', 0))
            if len(panels) == 2:
                # Right wing end panel: plane faces X at x = W - pt,
                # spanning the right wing depth.
                p = panels[0]
                p.location = (W - pt, 0.0, 0.0)
                gp = GeoNodeCutpart(p)
                gp.set_input('Length', H)
                gp.set_input('Width', RD)
                gp.set_input('Thickness', pt)
                # Left wing end panel: plane faces Y at y = -(D - pt),
                # spanning the left wing depth (rotate the vertical
                # panel 90 about Z so its Width runs along +X).
                p = panels[1]
                p.rotation_euler.z = math.radians(90)
                p.location = (0.0, -(D - pt), 0.0)
                gp = GeoNodeCutpart(p)
                gp.set_input('Length', H)
                gp.set_input('Width', LD)
                gp.set_input('Thickness', pt)
                gp.set_input('Mirror Z', False)

            # Back Partition (defaults, verified against a live
            # corner build): unflipped it lies parallel to the
            # back wall - x in [0, bw], y in [-wo - pt, -wo], full
            # height; flipped it moves to the side wall - x in
            # [wo, wo + pt], y in [0, -bw].
            partition = self._reconcile_back_partition()
            gp = GeoNodeCutpart(partition)
            if flip:
                partition.rotation_euler.z = 0.0
                partition.location = (wo, 0.0, 0.0)
            else:
                partition.rotation_euler.z = math.radians(90)
                partition.location = (0.0, -wo, 0.0)
            gp.set_input('Length', H)
            gp.set_input('Width', max(bw, 0.001))
            gp.set_input('Thickness', pt)
            # Thickness direction follows the wing-panel pattern:
            # rot_z 90 + Mirror Z False extends -Y (back wall);
            # rot_z 0 + Mirror Z True extends +X (side wall).
            gp.set_input('Mirror Z', bool(flip))

            for c in self.obj.children:
                if c.get('hb_l_kick'):
                    # corner kick pair (receiver/mate butt
                    # joint), not two full-length boards: the side-wall
                    # kick (receiver) runs the full left wing, stopping a
                    # panel thickness short of the wing panel and of the
                    # back wall; the back-wall kick (mate) starts at the
                    # receiver's face plane and butts square into it.
                    # the downstream wing-kick machining resolves
                    # the pair from this geometry (the mate's end must
                    # land against the receiver's face, never cross it).
                    gp = GeoNodeCutpart(c)
                    if c['hb_l_kick'] == 'Right Wing Kick':
                        # Mate: receiver face -> right wing end panel
                        # (width - ld - pt + tks).
                        c.location = (LD - setback, -RD + setback, 0.0)
                        gp.set_input('Length',
                                     max(W - pt - (LD - setback), 0.001))
                    else:
                        # Receiver: full side wall span
                        # (fabs(depth) - pt*2 from -depth + pt).
                        c.location = (LD - setback, -pt, 0.0)
                        gp.set_input('Length', max(D - 2.0 * pt, 0.001))
                    gp.set_input('Width', kick)
                    gp.set_input('Thickness', st)
                    _set_part_hidden(c, (not floor) or kick <= 0.0)

            # L shelves: bottom above the kick, top under the unit top,
            # the rest evenly between. Footprint W x D with the inner
            # front corner notched away to leave the two wings.
            shelves = self._reconcile_l_shelves()
            interior_lo = kick + (st if floor else st)
            z_bottom = kick
            z_top = H - st
            n_mid = max(0, len(shelves) - 2)
            for i, shelf in enumerate(shelves):
                if i == 0:
                    z = z_bottom
                elif i == len(shelves) - 1:
                    z = z_top
                else:
                    z = z_bottom + (z_top - z_bottom) * i / (len(shelves) - 1)
                # shelves are held off both walls by the wall
                # offset (partition and machining formulas assume it).
                shelf.location = (wo, -wo, z)
                gp = GeoNodeCutpart(shelf)
                gp.set_input('Length', max(W - pt - wo, 0.001))
                gp.set_input('Width', max(D - pt - wo, 0.001))
                gp.set_input('Thickness', st)
                notch = shelf.modifiers.get('L Notch')
                if notch is not None:
                    cpm = CabinetPartModifier(shelf)
                    cpm.mod = notch
                    # Wing depths measured from the walls, so the wall
                    # offset cancels out of the notch extents.
                    cpm.set_input('X', max(W - pt - LD, 0.001))
                    cpm.set_input('Y', max(D - pt - RD, 0.001))
                    cpm.set_input('Route Depth', st + 0.001)
                    # Probed: True/True lands the cut on the front-
                    # inner corner, leaving the two wings.
                    cpm.set_input('Flip X', True)
                    cpm.set_input('Flip Y', True)
                    notch.show_viewport = True
                    notch.show_render = True
                # Back Notch: clears the Back Partition at the rear
                # corner (the shelf's back-support notch: pt deep,
                # back-width less the wall offset plus the router tool
                # radius along the partition's wall; axes swap when the
                # partition flips to the side wall).
                bnotch = shelf.modifiers.get('Back Notch')
                if bnotch is not None:
                    cpm = CabinetPartModifier(shelf)
                    cpm.mod = bnotch
                    reach = max(bw - wo + const.L_NOTCH_TOOL_RADIUS, 0.001)
                    cpm.set_input('X', pt if flip else reach)
                    cpm.set_input('Y', reach if flip else pt)
                    cpm.set_input('Route Depth', st + 0.001)
                    # False/False lands the cut on the rear corner at
                    # the shelf origin (the room corner).
                    cpm.set_input('Flip X', False)
                    cpm.set_input('Flip Y', False)
                    bnotch.show_viewport = True
                    bnotch.show_render = True

            self.set_input('Dim X', W)
            self.set_input('Dim Y', D)
            self.set_input('Dim Z', H)
        finally:
            _RECALCULATING.discard(cabinet_id)


class LShelfBaseStarter(LShelfClosetStarter):
    default_closet_type = 'BASE'


class LShelfTallStarter(LShelfClosetStarter):
    default_closet_type = 'TALL'


class LShelfUpperStarter(LShelfClosetStarter):
    default_closet_type = 'UPPER'
    has_toe_kick = False
    floor_mounted = False


CLOSET_NAME_DISPATCH = {
    'Base': BaseClosetStarter,
    'Tall': TallClosetStarter,
    'Hanging': HangingClosetStarter,
    'Island': IslandClosetStarter,
    'Island Double': DoubleIslandClosetStarter,
    'L Shelf Base': LShelfBaseStarter,
    'L Shelf Tall': LShelfTallStarter,
    'L Shelf Upper': LShelfUpperStarter,
}

WRAP_CLASS_REGISTRY = {cls.__name__: cls for cls in CLOSET_NAME_DISPATCH.values()}
WRAP_CLASS_REGISTRY['ClosetStarter'] = ClosetStarter


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------
def get_starter_class(starter_name):
    """Return the ClosetStarter subclass for a library item name."""
    return CLOSET_NAME_DISPATCH.get(starter_name)


def auto_bay_qty(width):
    """Bay count for a given total width. Targets a 42" bay and never
    lets a bay exceed 42" (round up), so a run splits into the fewest
    bays that keep each opening <= 42". Used by the placement modal."""
    target = inch(42.0)
    return max(1, min(9, int(math.ceil(width / target))))


def find_bay_cage(obj):
    """Walk up parents from obj to the containing bay cage, or None."""
    current = obj
    while current is not None:
        if current.get(TAG_BAY_CAGE):
            return current
        current = current.parent
    return None


DOOR_OPEN_ANGLE = math.radians(110.0)


def apply_door_open(door, frac):
    """Position a door front for an open fraction (0 closed .. 1 fully
    open) by swinging it about its hinge edge. Reads the closed-state
    params stashed on the door at layout time (hb_door_cx/cy/cz/leaf,
    hb_door_side) + hb_hinge. Used both by the layout (persistent state
    from hb_door_open) and by the interactive open-door modal.

    Door local frame: parented to its opening/bay, base rotation
    (rx=90); its Length runs +X (hinge at the origin for a LEFT hinge,
    at origin+leaf for a RIGHT hinge). Fronts swing OUT of the room face
    (-Y front side, +Y back side)."""
    cx = door.get('hb_door_cx')
    if cx is None:
        return
    cy = door.get('hb_door_cy', 0.0)
    cz = door.get('hb_door_cz', 0.0)
    leaf = door.get('hb_door_leaf', 0.0)
    side = door.get('hb_door_side', 'FRONT')
    hinge = door.get('hb_hinge', 'LEFT')
    # A front-face door (face toward -Y) swings its free edge OUT into
    # the room: LEFT hinge -> negative Z rotation, RIGHT -> positive.
    # Back-side island doors mirror.
    swing = -1.0 if side == 'BACK' else 1.0
    if hinge == 'LEFT':
        ez = -DOOR_OPEN_ANGLE * frac * swing
        loc = (cx, cy, cz)
    else:  # RIGHT hinge: pivot at the far (origin+leaf) edge
        ez = DOOR_OPEN_ANGLE * frac * swing
        off_x = math.cos(ez) * (-leaf)
        off_y = math.sin(ez) * (-leaf)
        loc = (cx + leaf + off_x, cy + off_y, cz)
    door.location = loc
    door.rotation_euler = (math.radians(90.0), 0.0, ez)


def _stash_door_closed(door, cx, cy, cz, leaf, side):
    door['hb_door_cx'] = float(cx)
    door['hb_door_cy'] = float(cy)
    door['hb_door_cz'] = float(cz)
    door['hb_door_leaf'] = float(leaf)
    door['hb_door_side'] = side


def _distribute_front_heights(avail, fronts):
    """Split the available front span among a drawer stack so it fills the
    opening. `fronts` is a list of (height, locked) per front, bottom-up.
    Locked fronts keep their height; unlocked fronts share the remainder
    equally (floored at MIN_DRAWER_FRONT). If every front is locked, scale
    them proportionally to fit. Vertical analog of the bay-width solver."""
    out = [h for h, _l in fronts]
    unlocked = [i for i, (_h, lk) in enumerate(fronts) if not lk]
    if unlocked:
        locked_sum = sum(h for h, lk in fronts if lk)
        share = (avail - locked_sum) / len(unlocked)
        share = max(share, const.MIN_DRAWER_FRONT)
        for i in unlocked:
            out[i] = share
    else:
        total = sum(out) or 1.0
        scale = avail / total
        out = [h * scale for h in out]
    return out


def apply_drawer_open(front, frac):
    """Slide a drawer front (and its matching box) out of the carcass by
    an open fraction. Front-face drawers slide toward -Y (into the room);
    back-side ones toward +Y. Reads the closed Y stashed on each part
    (hb_slide_y0) and the travel distance on the front (hb_slide_dist)."""
    dist = front.get('hb_slide_dist')
    if dist is None:
        return
    side = front.get('hb_door_side', 'FRONT')
    delta = (dist * frac) * (1.0 if side == 'BACK' else -1.0)
    parent = front.parent
    idx = front.get('hb_drawer_index', 0)
    parts = [front]
    if parent is not None:
        for c in parent.children:
            if (c.get('hb_part_role') == PART_ROLE_DRAWER_BOX
                    and c.get('hb_drawer_index', 0) == idx):
                parts.append(c)
                break
    for part in parts:
        y0 = part.get('hb_slide_y0')
        if y0 is not None:
            part.location = (part.location.x, y0 + delta, part.location.z)


def _stash_drawer_closed(front, box, dist, side):
    front['hb_slide_y0'] = float(front.location.y)
    front['hb_slide_dist'] = float(dist)
    front['hb_door_side'] = side
    if box is not None:
        box['hb_slide_y0'] = float(box.location.y)


def default_adj_shelf_qty(opening):
    """Sensible starting shelf count for an opening: aim for ~one shelf
    per 12" of interior height (the legacy default spacing), clamped to
    at least one."""
    try:
        interior_h = GeoNodeCage(opening).get_input('Dim Z')
    except Exception:
        interior_h = 0.0
    return max(1, min(12, int(interior_h / inch(12.0))))


def find_opening_cage(obj):
    """Resolve the opening cage for any object in a closet hierarchy:
    the object's own opening if it's under one, else the (single)
    opening of its bay."""
    current = obj
    while current is not None:
        if current.get(TAG_OPENING_CAGE):
            return current
        current = current.parent
    bay = find_bay_cage(obj)
    if bay is None:
        return None
    for child in bay.children:
        if child.get(TAG_OPENING_CAGE):
            return child
    return None


def find_starter_root(obj):
    """Walk up parents from obj to the closet starter root, or None."""
    current = obj
    while current is not None:
        if current.get(TAG_STARTER_CAGE):
            return current
        current = current.parent
    return None


def _wrap_starter(obj):
    """Wrap a starter root Object as its ClosetStarter subclass."""
    cls = WRAP_CLASS_REGISTRY.get(obj.get('CLASS_NAME', ''), ClosetStarter)
    instance = cls.__new__(cls)
    GeoNodeCage.__init__(instance, obj)
    return instance


def recalculate_closet_starter(obj):
    """Public recalc entry point for prop update callbacks and operators.
    Accepts the root or any descendant; no-ops while that starter is
    already mid-recalc."""
    root = find_starter_root(obj)
    if root is None or id(root) in _RECALCULATING:
        return
    _wrap_starter(root).recalculate()


def clear_opening_contents(opening):
    """Strip one opening back to empty: clear every insert config idprop
    (the regenerators remove their parts on the next recalc) and delete
    loose parts (rods). Splitting shelves are bay structure, not
    contents - clear_bay_contents handles those."""
    for key in (PROP_ADJ_SHELF_QTY, PROP_DRAWER_QTY,
                PROP_DRAWER_FRONT_HEIGHT, PROP_DOOR_SWING, PROP_IS_HAMPER,
                PROP_CUBBY_COLS, PROP_CUBBY_ROWS):
        if key in opening:
            del opening[key]
    for child in list(opening.children):
        if child.get('hb_part_role') in (PART_ROLE_ROD,
                                         PART_ROLE_FIXED_SHELF):
            _remove_part_tree(child)  # rods carry hanger children


def clear_bay_contents(bay_obj):
    """Strip a whole bay: every splitting shelf goes (the reconciler
    merges back to one opening per side), the bay-wide door config is
    cleared, and every opening's contents are cleared."""
    for key in (PROP_BAY_DOOR_SWING, PROP_BAY_IS_HAMPER):
        if key in bay_obj:
            del bay_obj[key]
    for child in list(bay_obj.children):
        if child.get('hb_part_role') == PART_ROLE_FIXED_SHELF:
            bpy.data.objects.remove(child, do_unlink=True)
    for opening in [c for c in bay_obj.children if c.get(TAG_OPENING_CAGE)]:
        clear_opening_contents(opening)


# ---------------------------------------------------------------------------
# Copy / paste of bay & opening contents (a plain-dict clipboard so it
# survives object deletion and pastes onto any target).
# ---------------------------------------------------------------------------
def serialize_opening(opening):
    """Contents of one opening: its insert config idprops + loose rods
    (with their opening-local offsets)."""
    return {
        'adj': int(opening.get(PROP_ADJ_SHELF_QTY, 0)),
        'drawer_qty': int(opening.get(PROP_DRAWER_QTY, 0)),
        'drawer_fh': float(opening.get(PROP_DRAWER_FRONT_HEIGHT,
                                       const.DRAWER_FRONT_HEIGHT)),
        'door_swing': opening.get(PROP_DOOR_SWING, ''),
        'is_hamper': int(opening.get(PROP_IS_HAMPER, 0)),
        'cubby_cols': int(opening.get(PROP_CUBBY_COLS, 1)),
        'cubby_rows': int(opening.get(PROP_CUBBY_ROWS, 1)),
        'rods': [float(c.get('hb_z_offset', 0.0))
                 for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_ROD],
    }


def apply_opening_data(opening, data, recalc=True):
    """Rebuild an opening's contents from a serialize_opening() dict."""
    root = find_starter_root(opening)
    clear_opening_contents(opening)
    if data.get('adj'):
        opening[PROP_ADJ_SHELF_QTY] = data['adj']
    if data.get('drawer_qty'):
        opening[PROP_DRAWER_QTY] = data['drawer_qty']
        opening[PROP_DRAWER_FRONT_HEIGHT] = data['drawer_fh']
    if data.get('door_swing'):
        opening[PROP_DOOR_SWING] = data['door_swing']
        opening[PROP_IS_HAMPER] = data.get('is_hamper', 0)
    if data.get('cubby_cols', 1) > 1 or data.get('cubby_rows', 1) > 1:
        opening[PROP_CUBBY_COLS] = data.get('cubby_cols', 1)
        opening[PROP_CUBBY_ROWS] = data.get('cubby_rows', 1)
    for z in data.get('rods', ()):
        add_rod(opening, z)
    if recalc and root is not None:
        recalculate_closet_starter(root)


def _front_openings(bay_obj):
    return sorted(
        [c for c in bay_obj.children
         if c.get(TAG_OPENING_CAGE)
         and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'],
        key=lambda o: o.get('hb_opening_index', 0))


def serialize_bay(bay_obj):
    """Full contents of a bay: splitting shelves (offsets), bay-wide door
    config, bottom/cleat flags, and every front-side opening's contents."""
    bp = bay_obj.hb_closet_bay
    shelves = sorted(
        c.get('hb_z_offset', 0.0) for c in bay_obj.children
        if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF
        and not c.get('hb_preview')
        and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT')
    return {
        'remove_bottom': bool(bp.remove_bottom),
        'remove_cleat': bool(bp.remove_cleat),
        'bay_door_swing': bay_obj.get(PROP_BAY_DOOR_SWING, ''),
        'bay_is_hamper': int(bay_obj.get(PROP_BAY_IS_HAMPER, 0)),
        'shelves': list(shelves),
        'openings': [serialize_opening(o) for o in _front_openings(bay_obj)],
    }


def apply_bay_data(bay_obj, data):
    """Rebuild a bay's contents from a serialize_bay() dict (clears the
    target bay first)."""
    root = find_starter_root(bay_obj)
    if root is None:
        return False
    clear_bay_contents(bay_obj)
    recalculate_closet_starter(root)   # merge to one opening per side

    front = next((c for c in bay_obj.children
                  if c.get(TAG_OPENING_CAGE)
                  and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'), None)
    if front is None:
        return False
    for z in data.get('shelves', ()):
        add_fixed_shelf(front, z)
    recalculate_closet_starter(root)   # adopt shelves -> segments

    bp = bay_obj.hb_closet_bay
    bp.remove_bottom = data.get('remove_bottom', False)
    bp.remove_cleat = data.get('remove_cleat', False)
    if data.get('bay_door_swing'):
        bay_obj[PROP_BAY_DOOR_SWING] = data['bay_door_swing']
        bay_obj[PROP_BAY_IS_HAMPER] = data.get('bay_is_hamper', 0)

    for op_obj, od in zip(_front_openings(bay_obj),
                          data.get('openings', ())):
        apply_opening_data(op_obj, od, recalc=False)
    recalculate_closet_starter(root)
    return True


# ---------------------------------------------------------------------------
# Bay configurations (the closet "Change Bay" presets). Each recipe is
# splits (fixed-shelf heights in bay-interior Z, bottom-up) plus per-
# section content actions - everything composes from the primitives the
# rest of the library already uses, so overlay labels / grab handles /
# regenerators all work on the result.
# ---------------------------------------------------------------------------
# Grouped for the menu (separators between groups); the flat BAY_CONFIGS
# below feeds the operator enum.
BAY_CONFIG_GROUPS = [
    [('ADJ_SHELVES', "Adjustable Shelves")],
    [('DOUBLE_HANG', "Double Hang"),
     ('DH_TOP_SHELF', "Double Hang with Top Shelf"),
     ('DH_MID_SHELF', "Double Hang with Mid Shelf")],
    [('DOORS_3DR', "Doors Over 3 Drawers"),
     ('DOORS_4DR', "Doors Over 4 Drawers"),
     ('DOORS_5DR', "Doors Over 5 Drawers"),
     ('DOORS_6DR', "Doors Over 6 Drawers")],
    [('DOORS_OPEN_3DR', "Doors Open 3 Drawers"),
     ('DOORS_OPEN_4DR', "Doors Open 4 Drawers"),
     ('DOORS_OPEN_5DR', "Doors Open 5 Drawers"),
     ('DOORS_OPEN_6DR', "Doors Open 6 Drawers")],
    [('OPEN_OVER_DOORS', "Base Doors"),
     ('DOORS_OVER_OPEN', "Upper Doors"),
     ('FULL_HEIGHT_DOORS', "Full Height Doors")],
]
BAY_CONFIGS = [item for group in BAY_CONFIG_GROUPS for item in group]


def seed_door_shelves(opening):
    """Door openings include adjustable shelves behind the doors by
    default. Seeds the opening's shelf count unless something else
    already occupies it (an existing shelf count, drawers, cubbies, or
    a rod) - adding doors over an existing interior never overwrites
    it. Hampers are the callers' business (a tilt-out basket leaves no
    room for shelves)."""
    if (opening.get(PROP_ADJ_SHELF_QTY)
            or opening.get(PROP_DRAWER_QTY)
            or opening.get(PROP_CUBBY_COLS)):
        return
    for c in opening.children:
        if c.get('hb_part_role') == PART_ROLE_ROD:
            return
    opening[PROP_ADJ_SHELF_QTY] = default_adj_shelf_qty(opening)


def _cfg_rod(opening):
    add_rod(opening, const.ROD_TOP_OFFSET)


def _cfg_doors(opening):
    opening[PROP_DOOR_SWING] = 'DOUBLE'
    opening[PROP_IS_HAMPER] = 0
    seed_door_shelves(opening)


def _cfg_hamper(opening):
    opening[PROP_DOOR_SWING] = 'LEFT'
    opening[PROP_IS_HAMPER] = 1


def apply_bay_config(bay_obj, config):
    """Clear the bay and build one of the standard configurations."""
    root = find_starter_root(bay_obj)
    if root is None:
        return False
    scene_props = bpy.context.scene.hb_closets
    st = scene_props.shelf_thickness
    clear_bay_contents(bay_obj)
    recalculate_closet_starter(root)   # merge back to one opening/side

    opening = next((c for c in bay_obj.children
                    if c.get(TAG_OPENING_CAGE)
                    and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'), None)
    if opening is None:
        return False
    bp = bay_obj.hb_closet_bay
    kick = (root.hb_closet_starter.toe_kick_height
            if bp.floor_mounted else 0.0)
    ih = bp.height - 2.0 * st - kick
    dh = const.DRAWER_FRONT_HEIGHT

    def cap_z(qty):
        # Drawer-bank cap: top front half-overlays the shelf.
        return qty * (dh + const.FRONT_GAP) - st

    # Parse "Doors Over N Drawers" (DOORS_NDR) and "Doors Open N Drawers"
    # (DOORS_OPEN_NDR - same build with the doors shown open).
    drawer_qty = None
    doors_open = False
    if config.endswith('DR'):
        doors_open = config.startswith('DOORS_OPEN_')
        prefix = 'DOORS_OPEN_' if doors_open else 'DOORS_'
        if config.startswith(prefix):
            try:
                drawer_qty = int(config[len(prefix):-2])
            except ValueError:
                drawer_qty = None

    splits = []
    actions = []
    bay_door = None           # FULL_HEIGHT_DOORS -> bay-wide double door
    if config == 'ADJ_SHELVES':
        opening[PROP_ADJ_SHELF_QTY] = max(1, min(8, int(ih / inch(12.0))))
    elif config == 'DOUBLE_HANG':
        splits = [ih / 2.0]
        actions = [(0, _cfg_rod), (1, _cfg_rod)]
    elif config == 'DH_TOP_SHELF':
        hang_top = ih - inch(12.0)   # 12" storage band above the hangs
        splits = [hang_top / 2.0, hang_top]
        actions = [(0, _cfg_rod), (1, _cfg_rod)]
    elif config == 'DH_MID_SHELF':
        # Two hangs with a 12" shelf band between them.
        splits = [ih / 2.0,
                  min(ih / 2.0 + inch(12.0), ih - st - inch(1.0))]
        actions = [(0, _cfg_rod), (2, _cfg_rod)]
    elif drawer_qty is not None:
        qty = drawer_qty

        def _cfg_drawers(op, q=qty, h=dh):
            op[PROP_DRAWER_QTY] = q
            op[PROP_DRAWER_FRONT_HEIGHT] = h

        cap = cap_z(qty)
        if doors_open:
            # THREE segments: drawers (bottom), open (middle, no front),
            # doors (top). The remainder above the drawer bank is split
            # evenly between the open middle and the doors.
            mid = cap + (ih - cap) / 2.0
            splits = [cap, mid]
            actions = [(0, _cfg_drawers), (2, _cfg_doors)]
        else:
            # Doors directly over the drawer bank (two segments).
            splits = [cap]
            actions = [(0, _cfg_drawers), (1, _cfg_doors)]
    elif config == 'OPEN_OVER_DOORS':
        # Open section on top, doors on the bottom.
        splits = [ih / 2.0]
        actions = [(0, _cfg_doors)]
    elif config == 'DOORS_OVER_OPEN':
        # Doors on top, open section on the bottom.
        splits = [ih / 2.0]
        actions = [(1, _cfg_doors)]
    elif config == 'FULL_HEIGHT_DOORS':
        # Bay-wide double doors, no split.
        bay_door = 'DOUBLE'
    else:
        return False

    for z in splits:
        add_fixed_shelf(opening, z)
    recalculate_closet_starter(root)   # adopt splits -> segments

    openings = sorted(
        [c for c in bay_obj.children
         if c.get(TAG_OPENING_CAGE)
         and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'],
        key=lambda o: o.get('hb_opening_index', 0))
    for idx, fn in actions:
        if idx < len(openings) and fn is not None:
            fn(openings[idx])
    if bay_door:
        bay_obj[PROP_BAY_DOOR_SWING] = bay_door
        bay_obj[PROP_BAY_IS_HAMPER] = 0
        seed_door_shelves(opening)
    recalculate_closet_starter(root)
    return True


# ---------------------------------------------------------------------------
# Opening configurations ("Change Opening" - swap one opening's contents).
# ---------------------------------------------------------------------------
OPENING_CONFIG_GROUPS = [
    [('ADJ_SHELVES', "Adjustable Shelves")],
    [('DOOR_LEFT', "Left Swing Door"),
     ('DOOR_RIGHT', "Right Swing Door"),
     ('DOOR_DOUBLE', "Double Door")],
    [('DRAWERS_1', "1 Drawer"), ('DRAWERS_2', "2 Drawer"),
     ('DRAWERS_3', "3 Drawer"), ('DRAWERS_4', "4 Drawer"),
     ('DRAWERS_5', "5 Drawer"), ('DRAWERS_6', "6 Drawer"),
     ('DRAWERS_7', "7 Drawer"), ('DRAWERS_8', "8 Drawer")],
    [('CUBBIES', "Cubbies")],
]
OPENING_CONFIGS = [item for group in OPENING_CONFIG_GROUPS for item in group]


def apply_opening_config(opening, config):
    """Swap an opening's contents to a single standard configuration
    (clears the opening first)."""
    root = find_starter_root(opening)
    if root is None:
        return False
    clear_opening_contents(opening)
    if config == 'ADJ_SHELVES':
        opening[PROP_ADJ_SHELF_QTY] = default_adj_shelf_qty(opening)
    elif config == 'DOOR_LEFT':
        opening[PROP_DOOR_SWING] = 'LEFT'
        seed_door_shelves(opening)
    elif config == 'DOOR_RIGHT':
        opening[PROP_DOOR_SWING] = 'RIGHT'
        seed_door_shelves(opening)
    elif config == 'DOOR_DOUBLE':
        opening[PROP_DOOR_SWING] = 'DOUBLE'
        seed_door_shelves(opening)
    elif config == 'CUBBIES':
        opening[PROP_CUBBY_COLS] = 3
        opening[PROP_CUBBY_ROWS] = 3
    elif config.startswith('DRAWERS_'):
        try:
            opening[PROP_DRAWER_QTY] = int(config.split('_')[1])
            opening[PROP_DRAWER_FRONT_HEIGHT] = const.DRAWER_FRONT_HEIGHT
        except (ValueError, IndexError):
            return False
    else:
        return False
    recalculate_closet_starter(root)
    return True


def delete_starter(root_obj):
    """Remove a starter root and every descendant object."""
    for child in list(root_obj.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(root_obj, do_unlink=True)
