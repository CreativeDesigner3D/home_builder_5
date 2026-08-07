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
from contextlib import contextmanager

from ... import hb_utils
from ...hb_types import (GeoNodeCage, GeoNodeCutpart, GeoNodeObject,
                         GeoNodeDrawerBox, CabinetPartModifier)
from ...units import inch, millimeter
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
# The cover clipped over a rail end. A bought part, not a cut one: it
# wears the negative material (see materials_closets) so nothing about
# the run's finish paints it, and whatever processes hardware
# downstream counts it there. Each one carries 'hb_clip_on_left', the
# hand of the claw it covers.
PART_ROLE_HANG_RAIL_COVER = 'CLOSET_HANG_RAIL_COVER'
PART_ROLE_BATTEN = 'CLOSET_BATTEN'
PART_ROLE_COUNTERTOP = 'CLOSET_COUNTERTOP'
PART_ROLE_BACKSPLASH = 'CLOSET_BACKSPLASH'
PART_ROLE_ACCENT_SHELF = 'CLOSET_TOP_ACCENT_SHELF'
PART_ROLE_FILLER = 'CLOSET_FILLER'
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
# The part the library does not name: a nailer, a valance, a strip of
# filler. It is dropped on its own rather than built into a run, so
# nothing sizes it and nothing moves it. Its size sits on its own
# geometry inputs and its place sits on its own transform, and it
# keeps both until the person changes them.
PART_ROLE_MISC = 'CLOSET_MISC_PART'
# The top laid across a whole run at once, rather than the piece
# per bay a run works out for itself. It is dropped rather than
# prompted, so it is sized and placed once, at the drop, and left
# alone after: a run resized later keeps the top it was given.
PART_ROLE_CONTINUOUS_TOP = 'CLOSET_CONTINUOUS_TOP'
# A bought item that hangs in the closet: a valet rod, a wire basket,
# an ironing board. The cage carries the choice; what hangs under it
# depends on the accessory. Three children are possible:
#   ..._ACCESSORY_MODEL  the bought model itself, instanced from the
#                        companion add-on. Absent when that add-on is
#                        not installed - the accessory still holds its
#                        space and still reports its size.
#   ..._ACCESSORY_PART   melamine the library cuts for it (the ironing
#                        board drawer's mount plate and cap shelf).
#   a front              for the insert family, built by the normal
#                        front path so it opens and takes a pull.
# Which accessory this is sits in PROP_ACCESSORY_KEY, matched against
# accessories_closets.CATALOG.
PART_ROLE_ACCESSORY = 'CLOSET_ACCESSORY'
PART_ROLE_ACCESSORY_PART = 'CLOSET_ACCESSORY_PART'
PART_ROLE_ACCESSORY_MODEL = 'CLOSET_ACCESSORY_MODEL'
# Accessory idprops, on the accessory cage:
#   key      catalog key (see accessories_closets.CATALOG)
#   color    finish name, '' = as it comes
#   fabric   fabric name, '' = none offered
#   z        distance (m) from the opening bottom to the accessory
#   warning  why this accessory does not fit where it was put; empty
#            or absent means there is nothing to say
PROP_ACCESSORY_KEY = 'hb_accessory_key'
PROP_ACCESSORY_COLOR = 'hb_accessory_color'
PROP_ACCESSORY_FABRIC = 'hb_accessory_fabric'
PROP_ACCESSORY_Z = 'hb_accessory_z'
PROP_ACCESSORY_WARNING = 'hb_accessory_warning'
PROP_ACCESSORY_MODEL = 'hb_accessory_model'
PROP_ACCESSORY_PANEL_LOC = 'hb_accessory_panel_loc'
PART_ROLE_ACCESSORY_BLOCK = 'CLOSET_ACCESSORY_BLOCK'
# A fixed shelf splits a bay top and bottom; a division splits one of
# those segments left and right. Both are bay structure rather than
# contents, so both live on the bay cage. A division carries the bottom
# of the segment it stands in ('hb_seg_bottom') and how far across the
# bay it stands ('hb_x_offset'), which is what lets a shelf put in or
# taken out underneath carry the divisions above it along with it.
PART_ROLE_DIVISION = 'CLOSET_DIVISION'
# Inserts. Fronts follow the prior library's half-overlay convention.
PART_ROLE_DOOR = 'CLOSET_DOOR_FRONT'
PART_ROLE_DRAWER_FRONT = 'CLOSET_DRAWER_FRONT'
PART_ROLE_DRAWER_BOX = 'CLOSET_DRAWER_BOX'
PART_ROLE_DRAWER_STRETCHER = 'CLOSET_DRAWER_STRETCHER'
PART_ROLE_CUBBY_DIVISION = 'CLOSET_CUBBY_DIVISION'
PART_ROLE_CUBBY_SHELF = 'CLOSET_CUBBY_SHELF'
# Slanted shoe shelves: a tilted shelf plus a purchased metal shoe fence.
PART_ROLE_SLANTED_SHELF = 'CLOSET_SLANTED_SHELF'
PART_ROLE_SHOE_FENCE = 'CLOSET_SHOE_FENCE'
# Double-sided island structure.
PART_ROLE_CENTER_BACK = 'CLOSET_CENTER_BACK'
# A back held in one opening, captured between the panels and shelves
# around it, rather than applied across the outside of the bay.
PART_ROLE_CAPTURED_BACK = 'CLOSET_CAPTURED_BACK'
# Corner-clearance bridge parts (starter-root children, lazily created
# by _layout_bridge_parts). Driven by starter-root idprops so the types
# module stays hot-reloadable:
#   hb_bridge_left / hb_bridge_right       1 = top bridge shelf on that end
#   hb_bridge_w_left / hb_bridge_w_right   span (m) past the end panel
#   hb_bridge_bot_left / hb_bridge_bot_right  1 = bottom shelf (+ kick)
PART_ROLE_BRIDGE_SHELF = 'CLOSET_BRIDGE_SHELF'
# Opening insert configuration - what fills one opening. These live on
# the opening's typed settings group now (hb_closet_opening); the keys
# below are the storage the group replaced, kept so a file saved before
# the change can be carried over on open. See
# carry_over_opening_settings(). Nothing else should read or write them.
PROP_ADJ_SHELF_QTY = 'hb_adj_shelf_qty'
PROP_DRAWER_QTY = 'hb_drawer_qty'
PROP_ROLLOUT_QTY = 'hb_rollout_qty'
PROP_ROLLOUT_HEIGHT = 'hb_rollout_height'
# Written on a tray rather than on the opening: a tray can hold a
# height and a vertical location of its own while the rest of the stack
# keeps the height the opening sets and the spacing the stack works
# out. The resolved figures are written back on every recalculation, so
# a dialog opens on what is on screen rather than on a default.
PROP_TRAY_HEIGHT = 'hb_tray_height'
PROP_UNLOCK_TRAY_HEIGHT = 'hb_unlock_tray_height'
PROP_TRAY_Z = 'hb_tray_z'
PROP_UNLOCK_TRAY_Z = 'hb_unlock_tray_z'
# Slanted shoe shelves: quantity, vertical spacing, tilt angle (radians),
# and the metal fence color.
PROP_SLANT_QTY = 'hb_slant_qty'
PROP_SLANT_SPACING = 'hb_slant_spacing'
PROP_SLANT_ANGLE = 'hb_slant_angle'
PROP_SLANT_COLOR = 'hb_slant_color'
PROP_DRAWER_FRONT_HEIGHT = 'hb_drawer_front_height'
# Per-opening box-system override. Empty / 'DEFAULT' falls back to the
# scene-wide box selection; any other value forces this opening's boxes
# to that system (or turns them off with 'NONE').
PROP_DRAWER_BOX_OVERRIDE = 'hb_drawer_box_override'
# Per-drawer accessory: a fitted drawer jewelry tray, chosen by color.
# Stored on the drawer FRONT ('' = none). The tray size (and name) is
# derived from the drawer's inside width and depth; the resolved name is
# stamped back on the front as hb_jewelry_tray_name for reporting.
PROP_JEWELRY_TRAY = 'hb_jewelry_tray'
PROP_JEWELRY_TRAY_NAME = 'hb_jewelry_tray_name'
# Per-front drawer-box overrides (on each drawer FRONT), matching the
# prior Drawer Options: a box-system override ('' / 'DEFAULT' defers to
# the opening/scene setting) and explicit box depth/height overrides
# (0 = use the system-calculated size). The layout also stamps the
# resolved box type, size tag, and opening height back on the front so
# the dialog can report the current drawer.
# Which way the grain runs on this one drawer front, set in Drawer
# Options. '' / 'DEFAULT' follows the room's Vertical Grain setting.
PROP_FRONT_GRAIN = 'hb_front_grain'
PROP_FRONT_BOX_OVERRIDE = 'hb_front_box_override'
PROP_BOX_DEPTH_OVERRIDE = 'hb_box_depth_override'
PROP_BOX_HEIGHT_OVERRIDE = 'hb_box_height_override'
PROP_BOX_TYPE_RESOLVED = 'hb_box_type'
PROP_BOX_SIZE_TAG = 'hb_box_size_tag'
# Why this drawer box is not a size that can be bought, carried on the
# box and on its front so the panels can read it without working it
# out again. Empty/absent means there is nothing to say.
PROP_BOX_WARNING = 'hb_box_warning'
PROP_OPEN_HEIGHT = 'hb_open_height'
# Per-front idprops (on each drawer FRONT object). A drawer stack fills
# its opening: the fronts the stack owns share the remaining span
# equally. Typing a front's height hands that front its own
# (hb_unlock_front_height=1) so it holds while the others absorb the
# difference - the same padlock reading the bays use, where the flag
# that is set is the one the user pinned. hb_front_height is rewritten
# every recalc with the resolved height, so overlay labels always read
# the true value.
#
# These stay on the part as idprops rather than moving to a settings
# group: a group belongs to a cage - the run, a bay, an opening - and
# the parts under one are laid out by the solve, so the whole part layer
# stays hot-reloadable.
PROP_FRONT_HEIGHT = 'hb_front_height'
PROP_UNLOCK_FRONT_HEIGHT = 'hb_unlock_front_height'
# Heights a pasted drawer bank is owed, left on the opening until the
# fronts it describes have been built and can be handed them.
PROP_PASTED_FRONT_PINS = 'hb_pasted_front_pins'
# The name the flag was saved under before the padlocks were made to
# read one way across the library. Same meaning, so it carries straight
# across. See carry_over_front_locks().
OLD_PROP_FRONT_LOCKED = 'hb_front_locked'
# ''|'LEFT'|'RIGHT'|'DOUBLE'|'LIFT_UP'|'TILT_OUT'
PROP_DOOR_SWING = 'hb_door_swing'
# The flag a tilt-out hamper was held under before it became one of the
# fronts a swing can name. Kept so a file saved before the change can be
# carried over on open. See carry_over_hampers().
PROP_IS_HAMPER = 'hb_is_hamper'
# How many fronts each swing hangs. A tilt-out hamper is a single
# bottom-hinged front, so it counts the same as any other single.
FRONT_QTY_BY_SWING = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2,
                      'LIFT_UP': 1, 'TILT_OUT': 1}
# Bay-level doors span the WHOLE bay (all segments), parented to the bay
# cage; set from the bay menu. Mutually exclusive with opening doors on
# the same side (setting one clears the other). These live on the bay's
# typed settings group now (hb_closet_bay); the keys below are the
# storage the group replaced, kept so a file saved before the change can
# be carried over on open. See carry_over_bay_fronts().
PROP_BAY_DOOR_SWING = 'hb_bay_door_swing'
PROP_BAY_IS_HAMPER = 'hb_bay_is_hamper'
PROP_CUBBY_COLS = 'hb_cubby_cols'
PROP_CUBBY_ROWS = 'hb_cubby_rows'
PROP_CUBBY_SETBACK = 'hb_cubby_setback'
# Opening idprop on double islands: which face the opening serves.
PROP_OPENING_SIDE = 'hb_opening_side'    # 'FRONT' (default) | 'BACK'

# Reentrance guards, same pattern as face_frame. Prop writes inside
# recalculate() (bay width redistribution) fire update callbacks that
# would otherwise recurse; the callbacks consult these sets and bail.
_RECALCULATING = set()
_DISTRIBUTING_WIDTHS = set()

# A batch that touches a run many times over - a preset that rewrites a
# dozen props, a paste that refills every opening, a room-wide sweep -
# would otherwise solve the run once per write. suspend_recalc() holds
# those requests, keeps one per run, and solves each of them once on the
# way out of the outermost block.
_RECALC_SUSPEND_DEPTH = 0
_PENDING_RECALC_NAMES = set()


@contextmanager
def suspend_recalc():
    """Hold every recalc asked for inside the block and run them once at
    the end, one per run. Nests: only leaving the outermost block solves
    anything. Runs are remembered by name rather than by object so a
    rebuild inside the block can't leave a stale pointer behind, and a
    run that has since been deleted is simply skipped."""
    global _RECALC_SUSPEND_DEPTH
    _RECALC_SUSPEND_DEPTH += 1
    try:
        yield
    finally:
        _RECALC_SUSPEND_DEPTH -= 1
        if _RECALC_SUSPEND_DEPTH == 0:
            pending = list(_PENDING_RECALC_NAMES)
            _PENDING_RECALC_NAMES.clear()
            for root_name in pending:
                root = bpy.data.objects.get(root_name)
                if root is None:
                    continue
                try:
                    recalculate_closet_starter(root)
                except Exception:
                    # One run failing to solve shouldn't strand the rest
                    # of the batch.
                    pass


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


def _stamp_warning(obj, message):
    """Carry a design warning on the part it belongs to, and take it
    off again the moment the part fits, so what the panels find is
    only ever what is wrong now."""
    if message:
        obj[PROP_BOX_WARNING] = message
    elif PROP_BOX_WARNING in obj:
        del obj[PROP_BOX_WARNING]


def _set_part_hidden(obj, hidden):
    obj.hide_viewport = hidden
    obj.hide_render = hidden


def _hang_rail_cover_z(rail_z, shelf_thickness):
    """Bottom of a rail cover, given the bottom of the rail it covers.
    The cover's top sits an inch below the underside of the shelf the
    rail drops from, which leaves it standing a little proud of the
    rail at both ends - it wraps the claw rather than sitting beside
    it."""
    return (rail_z + const.HANG_RAIL_DROP - shelf_thickness
            - const.HANG_RAIL_COVER_TOP_OFFSET
            - const.HANG_RAIL_COVER_WIDTH)


# Every surface and edge slot on a cutpart. A purchased metal rail is one
# material all the way round, so it fills all six rather than taking a
# separate banding.
_CUTPART_MATERIAL_SOCKETS = ('Top Surface', 'Bottom Surface',
                             'Edge W1', 'Edge W2', 'Edge L1', 'Edge L2')


def _set_fence_finish(fpart, mat):
    """Put one metal finish on every slot of a shoe fence."""
    for socket in _CUTPART_MATERIAL_SOCKETS:
        try:
            fpart.set_input(socket, mat)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Drawer jewelry trays (a fitted, purchased drawer accessory). Two
# families: fabric-lined trays in seven colors sized S/M/L/XL by the
# drawer's inside width, and contour trays in three colors sized by
# inside width and depth. The tray is bought as-is - the library records
# the color and derives the size/name; downstream reads the name.
# ---------------------------------------------------------------------------
JEWELRY_TRAY_FABRIC = ('Brown', 'Black', 'Navy Blue', 'Pearl', 'Silver',
                       'Burgundy', 'Green')
JEWELRY_TRAY_CONTOUR = ('Oyster', 'Pewter', 'Winter')
# Enum rows for the accessory dialog: 'None' plus every color.
JEWELRY_TRAY_COLOR_ITEMS = (
    [('NONE', "None", "No jewelry tray")]
    + [(c, c, c) for c in (JEWELRY_TRAY_FABRIC + JEWELRY_TRAY_CONTOUR)])

# Metal shoe-fence finishes (enum rows for the slanted-shelf dialog).
# These are material names, matched exactly on append, so each one has to
# read the way it is spelled in the accessory finishes blend - the
# polished finish is the same 'Polished Chrome' the pulls and the hang
# rods already use.
SHOE_FENCE_COLORS = ('Black', 'Polished Chrome', 'Slate Graphite',
                     'Matte Nickel', 'Matte Aluminum', 'Matte Gold')
SHOE_FENCE_COLOR_ITEMS = [(c, c, c) for c in SHOE_FENCE_COLORS]
# Colors saved under an earlier spelling, mapped onto the material that
# carries that finish now, so a shelf stack built before the rename keeps
# the finish it was given.
SHOE_FENCE_COLOR_ALIASES = {'Chrome': 'Polished Chrome'}


def shoe_fence_color(saved):
    """A saved fence color resolved to a current enum row. Anything
    unrecognized falls back to the first row rather than failing an enum
    assignment."""
    if not saved:
        return SHOE_FENCE_COLORS[0]
    saved = SHOE_FENCE_COLOR_ALIASES.get(saved, saved)
    return saved if saved in SHOE_FENCE_COLORS else SHOE_FENCE_COLORS[0]


def shoe_fence_material(saved):
    """Metal finish material for a shoe fence. None when the finishes
    blend has no such material - the fence then keeps the closet look
    rather than losing its surfaces."""
    from . import pulls_closets
    return pulls_closets.load_finish_material(shoe_fence_color(saved))


def drawer_inside_width(front_width, box_type):
    """Inside (usable) width of a drawer given its front width and the
    resolved box system, matching the prior library's tray-fit math:
    a 5/16" overlay each side plus a box-system side allowance."""
    overlay = inch(0.3125) * 2
    if box_type in ('AVANTECH', 'AVANTECH_ILL'):
        return front_width - overlay - inch(1.0) * 2
    if box_type == 'METABOX':
        return front_width - overlay - millimeter(31)
    if box_type == 'WOOD':
        return front_width - overlay - inch(0.327) * 2
    return 0.0


def jewelry_tray_name(color, inside_width, depth):
    """Resolved tray name for a color and drawer size (inside_width and
    depth in meters), or '' when the drawer is out of range for that
    tray. Bands match the prior library exactly."""
    if not color or color == 'NONE':
        return ''
    if color in JEWELRY_TRAY_CONTOUR:
        w_mid = inch(6.1875) < inside_width < inch(36.0)
        w_wide = inside_width >= inch(36.0)
        d_std = inch(10.0) < depth < inch(20.0)
        d_deep = depth > inch(20.0)
        size = ''
        if w_mid and d_std:
            size = '24 x 16'
        elif w_mid and d_deep:
            size = '24 x 20'
        elif w_wide and d_std:
            size = '36 x 16'
        elif w_wide and d_deep:
            size = '36 x 20'
        return "%s Contour Jewelry Tray %s" % (size, color) if size else ''
    if color in JEWELRY_TRAY_FABRIC:
        size = ''
        if inch(12.0) <= inside_width < inch(16.0):
            size = 'S'
        elif inch(16.0) <= inside_width < inch(24.0):
            size = 'M'
        elif inch(24.0) <= inside_width < inch(30.0):
            size = 'L'
        elif inch(30.0) <= inside_width <= inch(36.875):
            size = 'XL'
        return "%s Drawer Jewelry Tray %s" % (size, color) if size else ''
    return ''


def target_inside_width_for_tray(color, inside_width, depth):
    """The inside width (meters) the drawer should have so the chosen
    tray fits, or the current width when it already fits. Fabric trays
    need 12"-36.875"; contour trays need > 6.1875"."""
    if color in JEWELRY_TRAY_FABRIC:
        if inside_width < inch(12.0):
            return inch(14.0)
        if inside_width > inch(36.875):
            return inch(33.0)
    elif color in JEWELRY_TRAY_CONTOUR:
        if inside_width <= inch(6.1875):
            return inch(8.0)
    return inside_width


def resize_for_jewelry_tray(front):
    """Grow or shrink the drawer's bay so the assigned jewelry tray fits,
    mirroring the prior library's fit-the-opening behavior: a single-bay
    closet grows overall, a multi-bay closet resizes just this bay (the
    others redistribute). Returns True when a resize was applied."""
    color = front.get(PROP_JEWELRY_TRAY, '')
    if not color or color == 'NONE':
        return False
    inside_w = float(front.get('hb_inside_w', 0.0))
    depth = float(front.get('hb_open_depth', 0.0))
    if inside_w <= 0.0:
        return False
    target = target_inside_width_for_tray(color, inside_w, depth)
    if abs(target - inside_w) < inch(0.05):
        return False
    bay = find_bay_cage(front)
    root = find_starter_root(front)
    if bay is None or root is None:
        return False
    # inside width and bay width differ by a constant (panels + overlays
    # + box side), so the bay width that yields the target inside width is
    # a simple shift.
    actual_bay_w = GeoNodeCage(bay).get_input('Dim X')
    target_bay_w = target + (actual_bay_w - inside_w)
    bays = [c for c in root.children if c.get(TAG_BAY_CAGE)]
    if len(bays) <= 1:
        sp = root.hb_closet_starter
        sp.width = sp.width + (target_bay_w - actual_bay_w)
    else:
        bay.hb_closet_bay.width = target_bay_w  # setter locks + relays out
    return True


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
    """Hang rod. Uses the rod node group carried over from the prior
    library (round/oval profile with end cups); Dim X is the rod
    length along local +X."""

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
                    role=PART_ROLE_FIXED_SHELF, cleat=False):
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
    if cleat:
        add_shelf_cleat(shelf.obj)
    return shelf.obj


def add_shelf_cleat(shelf_obj):
    """Create the cleat that stiffens the wall behind a shelf. It rides
    under the shelf as a child, so it keeps its place when the shelf
    moves and it goes when the shelf goes."""
    cleat = CabinetPart()
    cleat.create('Cleat')
    cleat.obj.parent = shelf_obj
    cleat.obj['hb_part_role'] = PART_ROLE_CLEAT
    cleat.obj.rotation_euler.x = math.radians(90)
    shelf_obj['hb_shelf_cleat'] = 1
    return cleat.obj


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


def add_misc_part(name='Misc Part'):
    """Create a part the library does not size and does not place.

    It stands on its own rather than inside an opening, so no recalc
    ever reaches it: it is the size it was cut and it stays where it
    was put until the person moves it. Starts at the size most of
    them want to be, which the person then changes.
    """
    part = CabinetPart()
    part.create(name)
    part.obj['hb_part_role'] = PART_ROLE_MISC
    part.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    part.set_input('Length', inch(30))
    part.set_input('Width', inch(18))
    part.set_input('Thickness', inch(0.75))
    part.set_input('Mirror Y', True)
    return part.obj


def add_continuous_top(name='Continuous Top'):
    """Create a top meant to be laid across a whole run at once.

    Comes out the size any loose part comes out; the drop sizes it
    to whatever run it lands on. Nothing sizes it after that, so a
    run resized later keeps the top it was given until the person
    changes it.
    """
    part = CabinetPart()
    part.create(name)
    part.obj['hb_part_role'] = PART_ROLE_CONTINUOUS_TOP
    part.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    part.set_input('Thickness',
                   bpy.context.scene.hb_closets.shelf_thickness)
    part.set_input('Mirror Y', True)
    return part.obj


def fit_continuous_top(top_obj, root, x_offset=0.0, length=None):
    """Lay a top across a run: sitting on the panel tops, running
    the length of the run, and one projection deeper so it covers
    the front edges. Takes a length of its own when the top is one
    piece of a top that had to be split.
    """
    sp = root.hb_closet_starter
    sizes = run_sizes(root)
    if top_obj.parent is not root:
        top_obj.parent = root
        top_obj.matrix_parent_inverse.identity()
    top_obj.rotation_euler = (0.0, 0.0, 0.0)
    top_obj.location = (x_offset, 0.0, sp.height)
    part = GeoNodeCutpart(top_obj)
    part.set_input(
        'Length',
        (sp.width - x_offset) if length is None else length)
    part.set_input('Width',
                   sp.depth + const.CONTINUOUS_TOP_PROJECTION)
    part.set_input('Thickness', sizes.shelf_thickness)
    part.set_input('Mirror Y', True)
    return part


def split_continuous_top(top_obj):
    """A top longer than one length of material comes in two.

    Cuts the first piece at the length that can be cut and lays the
    rest of it beside, end to end, so what is seen is one top
    across the run and what is made is two parts. Hands back the
    second piece, or nothing when the top fits in one.
    """
    root = find_starter_root(top_obj)
    if root is None:
        return None
    part = GeoNodeCutpart(top_obj)
    total = float(part.get_input('Length'))
    limit = const.CONTINUOUS_TOP_MAX_LENGTH
    if total <= limit:
        return None
    part.set_input('Length', limit)
    second = add_continuous_top()
    second.parent = root
    second.matrix_parent_inverse.identity()
    second.rotation_euler = (0.0, 0.0, 0.0)
    second.location = (top_obj.location.x + limit,
                       top_obj.location.y, top_obj.location.z)
    second_part = GeoNodeCutpart(second)
    second_part.set_input('Length', total - limit)
    second_part.set_input('Width', part.get_input('Width'))
    second_part.set_input('Thickness',
                          part.get_input('Thickness'))
    second_part.set_input('Mirror Y', True)
    return second


def add_division(opening_obj, x_offset):
    """Create a vertical division splitting one opening left and right.

    Takes how far across the bay the division stands, measured to its
    left face in bay-interior X - the same datum an opening's own
    'hb_seg_left' is in, so a division put inside an opening that is
    already a column reads the same as one in a whole segment. It
    parents to the bay rather than to the opening, because what it
    divides stops existing the moment it is there. Position and size
    are written by the next recalculate().
    """
    bay_obj = find_bay_cage(opening_obj)
    if bay_obj is None:
        return None
    div = CabinetPart()
    div.create('Division')
    div.obj.parent = bay_obj
    div.obj['hb_part_role'] = PART_ROLE_DIVISION
    div.obj['hb_x_offset'] = float(x_offset)
    div.obj['hb_seg_bottom'] = float(opening_obj.get('hb_seg_bottom', 0.0))
    div.obj[PROP_OPENING_SIDE] = opening_obj.get(PROP_OPENING_SIDE, 'FRONT')
    div.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    div.obj.rotation_euler.y = math.radians(-90)
    div.set_input('Mirror Y', True)
    div.set_input('Mirror Z', True)
    return div.obj


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

    def _default_depth_for_type(self, scene_props):
        """Per-type default panel depth, falling back to
        the general default_panel_depth."""
        return {
            'BASE': scene_props.default_base_panel_depth,
            'TALL': scene_props.default_tall_panel_depth,
            'HANGING': scene_props.default_hanging_panel_depth,
        }.get(self.default_closet_type, scene_props.default_panel_depth)

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

        scene_props = run_sizes(self.obj)
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
            # A top surfaced in the closet material is a shelf, so
            # it is as thick as one.
            sp.countertop_thickness = (
                scene_props.shelf_thickness
                if scene_props.use_closet_material_for_countertops
                else scene_props.countertop_thickness)
            # A double-sided island is reachable from every side, so its
            # top overhangs all round; everything else only overhangs at
            # the front until a prompt says otherwise.
            if self.ctop_overhang_all:
                for side in ('front', 'rear', 'left', 'right'):
                    setattr(sp, 'countertop_overhang_' + side,
                            const.ISLAND_CTOP_OVERHANG)
            sp.width = scene_props.default_closet_width
            sp.height = self.default_height(scene_props)
            sp.depth = (self.default_depth
                        if self.default_depth is not None
                        else self._default_depth_for_type(scene_props))
            sp.top_accent_overhang = scene_props.default_accent_overhang
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
            bp.unlock_width = False
            bay_height = self._default_bay_height(scene_props, sp)
            bp.height = bay_height
            bp.depth = sp.depth
            bp.unlock_height = False
            bp.unlock_depth = False
            # A run whose bays seed to a height other than the run
            # height - a hanging run tops out above its bays - hands
            # each of those bays its own height, so the seeded values
            # survive the first solve.
            if abs(bay_height - sp.height) > 1e-6:
                bp.unlock_height = True
            bp.floor_mounted = self.floor_mounted
            self._build_bay_parts(bay.obj)

    def _build_bay_parts(self, bay_obj):
        """One bay's fixed parts + opening cage, in bay-local coords.
        Static rotations/mirrors are set here; recalculate() owns the
        positions and sizes. Toe kick / cleat orientation reproduces the
        prior library's build: rot_x -90 stands the kick board up
        behind the setback line; rot_x +90 stands the cleat against
        the back."""
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
                  if c.get('hb_part_role') == PART_ROLE_PANEL
                  and not c.get('hb_double_partition')]
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

    def _bay_cover(self, bay_obj, side):
        """The cover clipped over one end of this bay's hang rail.
        Made on demand, so a run built before covers landed gains them
        on its next recalculation. A bay has two ends, so they are told
        apart by the end they sit at rather than by role alone."""
        for c in bay_obj.children:
            if (c.get('hb_part_role') == PART_ROLE_HANG_RAIL_COVER
                    and c.get('hb_cover_side') == side):
                return c
        if not self.has_hang_rail:
            return None
        part = CabinetPart()
        part.create('Hang Rail Cover')
        part.obj.parent = bay_obj
        part.obj['hb_part_role'] = PART_ROLE_HANG_RAIL_COVER
        part.obj['hb_cover_side'] = side
        # The claw is screwed to the face of the panel its cover sits
        # against, so the hand follows the end: a cover at the LEFT end
        # of a rail is on the right face of the panel there, one at the
        # RIGHT end is on the left face of the next panel along.
        part.obj['hb_clip_on_left'] = 1 if side == 'RIGHT' else 0
        part.obj.rotation_euler.x = math.radians(90)
        return part.obj

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def _migrate_double_panel_numbering(self):
        """Runs saved while a doubled junction was numbered by the bay to
        its RIGHT stored the option one bay too far along. Shift it once,
        so those runs come back looking the way they were drawn."""
        if self.obj.get('hb_double_panel_numbering'):
            return
        self.obj['hb_double_panel_numbering'] = 1
        bay_objs = self._sorted_bays()
        old = [bool(b.hb_closet_bay.get('double_panel_left', False))
               for b in bay_objs]
        for i, bay_obj in enumerate(bay_objs):
            bp = bay_obj.hb_closet_bay
            if any(old):
                bp.double_panel_right = (old[i + 1] if i + 1 < len(old)
                                         else False)
            try:
                del bp['double_panel_left']
            except (KeyError, TypeError):
                pass

    def _spec_from_props(self, scene_props):
        sp = self.obj.hb_closet_starter
        bay_objs = self._sorted_bays()
        bays = []
        for idx, bay_obj in enumerate(bay_objs):
            bp = bay_obj.hb_closet_bay
            # Junction option: a doubled partition is numbered by the bay
            # on its LEFT, so a bay's left junction reads the option off
            # the bay before it (the first bay's left side is the end of
            # the run, which is never doubled).
            prev = bay_objs[idx - 1].hb_closet_bay if idx > 0 else None
            bays.append({
                'width': bp.width,
                'locked': bp.unlock_width,
                'height': bp.height,
                'depth': bp.depth,
                'floor': bp.floor_mounted,
                'remove_bottom': bp.remove_bottom,
                'remove_cleat': bp.remove_cleat,
                'double_left': bool(prev.double_panel_right) if prev
                               else False,
            })
        return SimpleNamespace(
            width=sp.width,
            height=sp.height,
            pt=scene_props.panel_thickness,
            st=scene_props.shelf_thickness,
            kick_height=sp.toe_kick_height,
            kick_setback=sp.toe_kick_setback,
            left_panel_off=sp.turn_off_left_panel,
            right_panel_off=sp.turn_off_right_panel,
            extend_panels=sp.extend_panels_to_countertop,
            extend_amount=sp.extend_panel_amount,
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
            scene_props = run_sizes(self.obj)
            sp = self.obj.hb_closet_starter

            # The run height and depth carry down to the bays. A bay
            # follows the run until it is handed a size of its own, and
            # goes back to following the moment that is cleared. Bay
            # writes here can't recurse - the update callbacks bail
            # while this starter is in _RECALCULATING.
            self._migrate_double_panel_numbering()
            for bay_obj in self._sorted_bays():
                bp = bay_obj.hb_closet_bay
                if not bp.unlock_height:
                    if abs(bp.height - sp.height) > 1e-9:
                        bp.height = sp.height
                if not bp.unlock_depth:
                    if abs(bp.depth - sp.depth) > 1e-9:
                        bp.depth = sp.depth

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
            self._layout_battens(layout, scene_props, sp)
            self._layout_fillers(layout, scene_props, sp)

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
        sp = self.obj.hb_closet_starter
        panels = self._sorted_panels()
        last = len(panels) - 1
        for i, (child, panel) in enumerate(zip(panels, layout['panels'])):
            child.location = (panel['x'], 0.0, panel['z'])
            part = GeoNodeCutpart(child)
            part.set_input('Length', panel['length'])
            part.set_input('Width', panel['depth'])
            part.set_input('Thickness', pt)
            # Turn Off Panel: hidden, thickness reclaimed by the solver.
            off = bool(panel.get('hidden'))
            child['hb_panel_off'] = 1 if off else 0
            _set_part_hidden(child, off)
            # End flags recorded on the panel: whether the end is
            # exposed, and whether its system holes run all the way
            # through. Flags only - they carry no geometry.
            if i == 0:
                child['hb_finished_end'] = 1 if sp.left_finished_end else 0
                child['hb_drill_through'] = 1 if sp.drill_through_left else 0
            elif i == last:
                child['hb_finished_end'] = 1 if sp.right_finished_end else 0
                child['hb_drill_through'] = 1 if sp.drill_through_right else 0
        self._reconcile_double_panels(layout, scene_props)

    def _reconcile_double_panels(self, layout, scene_props):
        """A second partition back-to-back at a
        doubled junction, serving the LEFT bay (the primary partition
        shifts right and serves only the RIGHT bay - the solver already
        placed it). Created/removed to match the layout."""
        pt = scene_props.panel_thickness
        want = {d['junction']: d for d in layout.get('doubles', [])}
        have = {}
        for c in list(self.obj.children):
            if c.get('hb_double_partition'):
                j = c.get('hb_double_index', -1)
                if j in want and j not in have:
                    have[j] = c
                else:
                    bpy.data.objects.remove(c, do_unlink=True)
        for j, d in want.items():
            c = have.get(j)
            if c is None:
                p = CabinetPart()
                p.create(f'Double Partition {j + 1}')
                p.obj.parent = self.obj
                p.obj['hb_part_role'] = PART_ROLE_PANEL
                p.obj['hb_double_partition'] = 1
                p.obj['hb_double_index'] = j
                p.obj.rotation_euler.y = math.radians(-90)
                p.set_input('Mirror Y', True)
                p.set_input('Mirror Z', True)
                c = p.obj
            c.location = (d['x'], 0.0, d['z'])
            part = GeoNodeCutpart(c)
            part.set_input('Length', d['length'])
            part.set_input('Width', d['depth'])
            part.set_input('Thickness', pt)

    def _layout_battens(self, layout, scene_props, sp):
        """A scribe strip laid flat on the FRONT face of an end panel,
        running that panel's full height. It covers the panel edge and
        carries whatever is left of its width past the outside of the
        run, so there is something to scribe to the wall. How thick and
        how wide is the room's, or this run's where it has taken either
        figure over. Cosmetic part.

        The strip lies in the face plane: Length runs up Z, Width runs
        across X (outward, away from the run) and Thickness stands proud
        of the front face. Rotation and mirroring are rewritten on every
        pass so a part built before this orientation was settled
        re-orients itself the next time the closet recalculates.
        """
        bays = layout['bays']
        panels = layout['panels']
        if not bays or not panels:
            return
        pt = scene_props.panel_thickness
        have = {c.get('hb_batten'): c for c in self.obj.children
                if c.get('hb_batten')}
        for side in ('LEFT', 'RIGHT'):
            c = have.get(side)
            if c is None:
                p = CabinetPart()
                p.create(f'{side.title()} Batten')
                p.obj.parent = self.obj
                p.obj['hb_part_role'] = PART_ROLE_BATTEN
                p.obj['hb_batten'] = side
                c = p.obj
            bay = bays[0] if side == 'LEFT' else bays[-1]
            panel = panels[0] if side == 'LEFT' else panels[-1]
            include = (sp.include_batten_left if side == 'LEFT'
                       else sp.include_batten_right)
            c.rotation_euler = (0.0, math.radians(-90), math.radians(90))
            part = GeoNodeCutpart(c)
            # Width runs off the outside of the run: away from -X on the
            # left, toward +X on the right.
            part.set_input('Mirror Y', side == 'RIGHT')
            part.set_input('Mirror Z', False)
            # Anchor on the face of the end panel that faces the run, so
            # the strip laps the panel and overhangs the outside.
            x = panel['x'] + pt if side == 'LEFT' else panel['x']
            # The panel entry already carries the height and the floor /
            # extend-to-countertop drop, so the strip tracks the panel.
            c.location = (x, -bay['depth'], panel['z'])
            part.set_input('Length', panel['length'])
            part.set_input('Width', scene_props.batten_width)
            part.set_input('Thickness', scene_props.batten_thickness)
            _set_part_hidden(c, not include)

    def _layout_fillers(self, layout, scene_props, sp):
        """A front scribe board standing
        past the end of the run to close the gap to a side wall. Ground
        truth from a live reference build: Length runs vertical, the filler
        WIDTH extends outward past the end (left filler -X, right +X),
        thickness = shelf material at the front face, origin at the end
        opening's front-bottom. Reconciled by width>0 (like
        battens)."""
        bays = layout['bays']
        if not bays:
            return
        st = scene_props.shelf_thickness
        have = {c.get('hb_filler'): c for c in self.obj.children
                if c.get('hb_filler')}
        for side in ('LEFT', 'RIGHT'):
            c = have.get(side)
            width = (sp.left_side_wall_filler if side == 'LEFT'
                     else sp.right_side_wall_filler)
            if c is None:
                if width <= 0.0:
                    continue
                p = CabinetPart()
                p.create(f'{side.title()} Filler')
                p.obj.parent = self.obj
                p.obj['hb_part_role'] = PART_ROLE_FILLER
                p.obj['hb_filler'] = side
                # Match the reference filler frame: Length -> vertical, Width
                # -> outward in X, Thickness -> depth at the front.
                p.obj.rotation_euler.y = math.radians(-90)
                p.obj.rotation_euler.z = math.radians(90)
                p.set_input('Mirror Z', True)
                c = p.obj
            bay = bays[0] if side == 'LEFT' else bays[-1]
            # Left filler at the closet's left edge (x=0) extruding -X
            # (out the left end); right filler at the right edge
            # (x=width) extruding +X. In HB5 Mirror Y False extrudes -X
            # and True extrudes +X (opposite of the reference frame), so the
            # RIGHT filler mirrors. Set each recalculate so pre-existing
            # fillers self-correct.
            GeoNodeCutpart(c).set_input('Mirror Y', side == 'RIGHT')
            x = 0.0 if side == 'LEFT' else sp.width
            c.location = (x, -bay['depth'], bay['z0'])
            part = GeoNodeCutpart(c)
            part.set_input('Length', bay['height'])
            part.set_input('Width', max(width, 0.001))
            part.set_input('Thickness', st)
            _set_part_hidden(c, width <= 0.0)

    def _layout_bays(self, layout, scene_props, sp):
        st = scene_props.shelf_thickness
        n_bays = len(layout['bays'])
        for bay_i, (bay_obj, bay) in enumerate(
                zip(self._sorted_bays(), layout['bays'])):
            cage = GeoNodeCage(bay_obj)
            bay_obj.location = (bay['x'], 0.0, bay['z0'])
            cage.set_input('Dim X', bay['width'])
            cage.set_input('Dim Y', bay['depth'])
            cage.set_input('Dim Z', bay['height'])
            bp = bay_obj.hb_closet_bay

            # Inset Bottom (run-wide) plus this bay's own Bottom Shelf
            # Inset hold the bottom shelf off the wall; the front edge
            # stays where it was, so the shelf just gets shallower. Only
            # a floor bay has a bottom to set in.
            inset_b = ((sp.inset_bottom + bp.bottom_shelf_inset)
                       if bay['floor'] else 0.0)
            inset_b = max(0.0, min(inset_b, bay['depth'] - 0.001))

            bottom = self._bay_part(bay_obj, PART_ROLE_BOTTOM_SHELF)
            if bottom is not None:
                bottom.location = (0.0, -inset_b, bay['bottom_z'])
                part = GeoNodeCutpart(bottom)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['depth'] - inset_b)
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

            # Inset Cleat lifts the cleat above the bottom shelf it sits
            # on, so it only applies where there is one: a floor bay
            # that still has its bottom.
            cleat_z = bay['cleat_z']
            if bay['floor'] and not bp.remove_bottom:
                cleat_z += sp.inset_cleat

            cleat = self._bay_part(bay_obj, PART_ROLE_CLEAT)
            if cleat is not None:
                cleat.location = (0.0, 0.0, cleat_z)
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
                # Use One Hang Rail Height forces an absolute rail height
                # (bay-local z = target - bay origin z0); otherwise each
                # bay's rail drops from its own top.
                if sp.use_one_hang_rail_height:
                    local_z = sp.hang_rail_height_location - bay['z0']
                else:
                    local_z = bay['height'] - const.HANG_RAIL_DROP
                # Extend Hang Rail Left/Right lengthen the end bays' rails
                # toward the walls (left rail also shifts its start left).
                rail_x = 0.0
                rail_len = bay['width']
                if bay_i == 0 and sp.extend_hang_rail_left > 0.0:
                    rail_x = -sp.extend_hang_rail_left
                    rail_len += sp.extend_hang_rail_left
                if bay_i == n_bays - 1 and sp.extend_hang_rail_right > 0.0:
                    rail_len += sp.extend_hang_rail_right
                rail.location = (rail_x, 0.0, local_z)
                part = GeoNodeCutpart(rail)
                part.set_input('Length', rail_len)
                part.set_input('Width', const.HANG_RAIL_WIDTH)
                part.set_input('Thickness', const.HANG_RAIL_THICKNESS)
                _set_part_hidden(
                    rail, (not self.has_hang_rail)
                    or sp.remove_hang_rail)

                # A cover clips over each rail end that lands on a
                # panel. Two bays side by side share the panel between
                # them and so share the one claw, which is why a bay
                # covers its left end only - the last bay in the run
                # covers its right end as well. An end lengthened
                # toward the wall runs out past the last panel, so its
                # cover stays back at the panel. It sits an inch out
                # from the wall, in front of the rail rather than
                # around it, because the claw is what it covers.
                cover_z = _hang_rail_cover_z(local_z, st)
                hide_cover = ((not self.has_hang_rail)
                              or sp.remove_hang_rail)
                for side in ('LEFT', 'RIGHT'):
                    cover = self._bay_cover(bay_obj, side)
                    if cover is None:
                        continue
                    cover_x = (0.0 if side == 'LEFT'
                               else bay['width']
                               - const.HANG_RAIL_COVER_LENGTH)
                    cover.location = (
                        cover_x,
                        -const.HANG_RAIL_COVER_STANDOFF, cover_z)
                    cpart = GeoNodeCutpart(cover)
                    cpart.set_input('Length',
                                    const.HANG_RAIL_COVER_LENGTH)
                    cpart.set_input('Width',
                                    const.HANG_RAIL_COVER_WIDTH)
                    cpart.set_input('Thickness',
                                    const.HANG_RAIL_COVER_DEPTH)
                    _set_part_hidden(
                        cover, hide_cover
                        or (side == 'RIGHT' and bay_i != n_bays - 1))

            back = self._bay_part(bay_obj, PART_ROLE_APPLIED_BACK)
            if back is not None:
                # The back laps onto the panels and shelves around its
                # bay by the overlay, and either starts above the kick
                # and bottom shelf or runs on down to the floor.
                ov = sp.applied_back_overlay
                back_z = (0.0 if sp.back_to_floor
                          else max(bay['interior_z'] - ov, 0.0))
                back.location = (-ov, 0.0, back_z)
                part = GeoNodeCutpart(back)
                part.set_input('Length', bay['width'] + ov * 2.0)
                part.set_input('Width',
                               max(bay['top_z'] + ov - back_z, 0.001))
                part.set_input('Thickness', const.APPLIED_BACK_THICKNESS)
                _set_part_hidden(back, False)

            # Center back (double islands): st thick, spanning the
            # interior. Centered in depth unless the bay names a
            # location. Horizontal grain for now; grain direction is
            # decided downstream.
            center_back = self._bay_part(bay_obj, PART_ROLE_CENTER_BACK)
            if center_back is not None:
                cb_y = bp.center_back_location
                if cb_y <= 0.0:
                    cb_y = bay['depth'] / 2.0 + st / 2.0
                cb_y = min(cb_y, bay['depth'])
                center_back.location = (0.0, -cb_y, bay['interior_z'])
                part = GeoNodeCutpart(center_back)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['interior_h'])
                part.set_input('Thickness', st)
                _set_part_hidden(center_back, not bp.include_center_back)

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
                    self._lay_out_shelf_cleat(sh, bay_obj, bay, st)

                bottoms = [0.0] + [b + st for b in boundaries]
                tops = boundaries + [bay['interior_h']]

                # Divisions: a vertical splitter inside one segment. Cut
                # from the panel thickness rather than the shelf's,
                # because what it is is a panel standing inside a bay.
                pt = scene_props.panel_thickness
                row_x = [[] for _ in bottoms]
                for div in self._bay_divisions(bay_obj, side):
                    k = min(max(int(div.get('hb_row', 0)), 0),
                            len(bottoms) - 1)
                    row_h = max(tops[k] - bottoms[k], 0.01)
                    x_off = max(0.0, min(float(div.get('hb_x_offset', 0.0)),
                                         bay['width'] - pt))
                    div['hb_x_offset'] = float(x_off)
                    div['hb_seg_bottom'] = float(bottoms[k])
                    div.location = (x_off, base_y,
                                    bay['interior_z'] + bottoms[k])
                    part = GeoNodeCutpart(div)
                    part.set_input('Length', row_h)
                    part.set_input('Width', o_depth)
                    part.set_input('Thickness', pt)
                    _set_part_hidden(div, False)
                    row_x[k].append(x_off)
                for xs in row_x:
                    xs.sort()

                openings = sorted(
                    [c for c in bay_obj.children
                     if c.get(TAG_OPENING_CAGE)
                     and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                    key=lambda o: (o.get('hb_opening_index', 0),
                                   o.get('hb_col_index', 0)))
                for op_obj in openings:
                    k = min(max(int(op_obj.get('hb_opening_index', 0)), 0),
                            len(bottoms) - 1)
                    xs = row_x[k]
                    j = min(max(int(op_obj.get('hb_col_index', 0)), 0),
                            len(xs))
                    b0 = bottoms[k]
                    seg_h = max(tops[k] - b0, 0.01)
                    x0 = 0.0 if j == 0 else xs[j - 1] + pt
                    x1 = bay['width'] if j >= len(xs) else xs[j]
                    seg_w = max(x1 - x0, 0.01)
                    op_obj['hb_seg_bottom'] = float(b0)
                    op_obj['hb_seg_left'] = float(x0)
                    op_obj.location = (x0, base_y,
                                       bay['interior_z'] + b0)
                    op_cage = GeoNodeCage(op_obj)
                    op_cage.set_input('Dim X', seg_w)
                    op_cage.set_input('Dim Y', o_depth)
                    op_cage.set_input('Dim Z', seg_h)
                    self._layout_opening_parts(op_obj, seg_w,
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

        Fronts use the prior library's half-overlay convention: each
        edge overlays its shared panel/shelf by (thickness - gap)/2.
        On a double
        island's BACK opening the fronts flip to the y=0 face (Mirror Z
        flips the extrude direction, set at part creation).
        """
        st = scene_props.shelf_thickness
        pt = scene_props.panel_thickness
        side = opening.get(PROP_OPENING_SIDE, 'FRONT')

        self._reconcile_adj_shelves(opening)
        self._reconcile_slanted_shelves(opening)
        self._reconcile_doors(opening, side)
        self._reconcile_drawers(opening, side)
        self._reconcile_rollouts(opening, side)
        self._reconcile_captured_back(opening)
        self._reconcile_cubbies(opening)

        sp = self.obj.hb_closet_starter
        lo, ro, to, bo = front_overlays(sp, scene_props, opening)
        v_gap = sp.vertical_gap
        h_gap = sp.horizontal_gap
        if side == 'BACK':
            front_y = sp.door_to_cabinet_gap
        else:
            front_y = -depth - sp.door_to_cabinet_gap

        # Blender works out an object's children by walking every
        # object in the file, so the list is taken once here and shared
        # by everything below rather than asked for again each time.
        children = list(opening.children)
        self._accessories(
            [c for c in children
             if c.get('hb_part_role') == PART_ROLE_ACCESSORY],
            width, depth, interior_h, side, front_y, lo, ro, to, bo,
            scene_props)

        groups = {}
        for child in children:
            role = child.get('hb_part_role')
            if role == PART_ROLE_ACCESSORY:
                # Laid out just above, cage and all. It is skipped here
                # rather than falling into groups so nothing downstream
                # mistakes an accessory's front for a drawer's.
                continue
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
                op = opening.hb_closet_opening
                z_off = child.get('hb_z_offset', const.ROD_TOP_OFFSET)
                z = (interior_h - z_off if child.get('hb_anchor_top')
                     else z_off)
                z = max(const.ROD_RADIUS,
                        min(z, interior_h - const.ROD_RADIUS))
                # Front to back the rod stands where the opening says it
                # does: so far out from the rear (wall side, Y=0), or so
                # far back from the front when the opening is set to read
                # that way. Either way it is clamped to stay inside a
                # shallow opening.
                from_rear = (depth - op.rod_from_front
                             if op.rod_set_from_front else op.rod_from_rear)
                rod_y = -min(max(from_rear, const.ROD_RADIUS),
                             max(depth - const.ROD_RADIUS, const.ROD_RADIUS))
                # The rod is cut shorter than its opening so it drops into
                # the cups, and it is centered in what is left.
                deduct = max(0.0, min(float(op.rod_width_deduction), width))
                rod_len = width - deduct
                child.location = (deduct / 2.0, rod_y, z)
                rod_geo = GeoNodeObject(child)
                rod_geo.set_input('Dim X', rod_len)
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
                    pulls_closets.reconcile_rod_hangers(
                        child, rod_len, allow=not op.remove_hangers)
                except Exception:
                    pass
            elif role is not None:
                groups.setdefault(role, []).append(child)

        # A shelf that rests on clips is cut narrower than the opening
        # so it can drop in, and it can be held back from the front
        # edge. Both figures are the room's unless this opening has
        # taken one over. Worked out once for the opening rather than
        # per shelf: every shelf in an opening is cut the same.
        _shp = opening.hb_closet_opening
        clip = max(0.0, float(
            _shp.shelf_clip_gap if _shp.unlock_shelf_clip_gap
            else scene_props.shelf_clip_gap))
        shelf_w = max(width - clip * 2.0, inch(1.0))
        adj_setback = max(0.0, float(
            _shp.shelf_setback if _shp.unlock_shelf_setback
            else scene_props.shelf_setback))

        # ----- Captured back: held in the opening, not applied -----
        # It stands against the structural rear of the opening and the
        # inset holds it forward of that. On a double island's back side
        # the rear is the far end of the opening rather than y=0, so the
        # part is placed there and extrudes the other way (Mirror Z).
        cap_back = groups.get(PART_ROLE_CAPTURED_BACK, [])
        if cap_back:
            child = cap_back[0]
            b_inset = max(0.0, min(float(_shp.back_inset),
                                   max(depth - st, 0.0)))
            child.location = (
                0.0,
                -(depth - b_inset) if side == 'BACK' else -b_inset,
                0.0)
            part = GeoNodeCutpart(child)
            part.set_input('Mirror Z', side == 'BACK')
            part.set_input('Length', width)
            part.set_input('Width', interior_h)
            part.set_input('Thickness', st)
            # Corner reliefs. On the part X runs in from the side and Y
            # down from the top edge. Flip Y True picks the top edge and
            # Flip X picks the right-hand side: the cut lands on the
            # corner at the part origin with both False (probed on the
            # L shelf, which is cut the same way).
            n_w = max(min(float(_shp.back_notch_width), width), 0.001)
            n_h = max(min(float(_shp.back_notch_height), interior_h),
                      0.001)
            for mod_name, flip_x, cuts in (
                    ('Notch Left', False, _shp.back_notch_left),
                    ('Notch Right', True, _shp.back_notch_right)):
                mod = child.modifiers.get(mod_name)
                if mod is None:
                    continue
                cpm = CabinetPartModifier(child)
                cpm.mod = mod
                cpm.set_input('X', n_w)
                cpm.set_input('Y', n_h)
                cpm.set_input('Route Depth', st + 0.001)
                cpm.set_input('Flip X', flip_x)
                cpm.set_input('Flip Y', True)
                mod.show_viewport = bool(cuts)
                mod.show_render = bool(cuts)

        # ----- Adjustable shelves: even spacing bottom-up -----
        adj = groups.get(PART_ROLE_ADJ_SHELF, [])
        if adj:
            adj.sort(key=lambda o: o.get('hb_adj_index', 0))
            # The prior library took every shelf's own thickness out
            # of the opening first, shared what was left between the
            # shelves and the space above and below them, then added a
            # thickness back for each shelf underneath. The clear space
            # between one shelf and the next is the same the whole way
            # up, which is what a shelf is set by.
            spacing = (interior_h - st * len(adj)) / (len(adj) + 1) + st
            adj_depth = max(depth - adj_setback, inch(1.0))
            for i, child in enumerate(adj):
                z = max(0.0, min(spacing * (i + 1), interior_h - st))
                child.location = (clip, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', shelf_w)
                part.set_input('Width', adj_depth)
                part.set_input('Thickness', st)

        # ----- Slanted shoe shelves (tilted, front metal fence) -----
        # Stacked bottom-up at a fixed vertical spacing; each shelf tilts
        # back by the shelf angle and is set back from the front so the
        # metal fence sits flush. The fence is a purchased rail across the
        # front, parented to the shelf so it rides the tilt.
        slants = groups.get(PART_ROLE_SLANTED_SHELF, [])
        if slants:
            slants.sort(key=lambda o: o.get('hb_slant_index', 0))
            spacing = float(opening.hb_closet_opening.slant_spacing)
            angle = float(opening.hb_closet_opening.slant_angle)
            setback = const.SLANT_SHELF_SETBACK
            shelf_depth = max(depth - setback, inch(1.0))
            y_front = -shelf_depth  # front edge in opening-local Y
            # The shelf tips down toward the front, and it pivots about
            # its REAR edge, so the front edge finishes a shelf-depth's
            # worth of rise below the origin. Lift the whole stack by
            # that rise: the bottom shelf's front lip then lands on the
            # opening floor instead of hanging through it, which is
            # where the prior library's stack started.
            rise = shelf_depth * math.sin(angle)
            # Tipping about the rear edge also swings the front edge
            # back, by a shelf depth less its own run once tilted. The
            # prior library pivoted about the FRONT edge instead, its
            # shelves reaching the opening face. Carry the stack forward
            # by that difference so the front lip lands on the face here
            # too, rather than standing off it by the tilt.
            y_slant = -shelf_depth * (1.0 - math.cos(angle))
            fence_mat = shoe_fence_material(
                opening.hb_closet_opening.slant_color)
            # The fence is held in from each end of the shelf and can
            # stand back from its front edge. Both are clamped to what
            # the shelf can actually carry, so a typed figure that is
            # too big leaves a fence rather than nothing.
            f_inset = min(max(float(_shp.slant_fence_inset), 0.0),
                          max((shelf_w - inch(1.0)) / 2.0, 0.0))
            f_room = (shelf_depth - const.SHOE_FENCE_DEPTH
                      - const.SHOE_FENCE_STANDOFF)
            f_back = min(max(float(_shp.slant_back_inset), 0.0),
                         max(f_room, 0.0))
            for i, child in enumerate(slants):
                z = spacing * i + rise
                # These rest on clips too, so they take the opening's
                # clip gap. Their setback is the fence's, not the
                # room's, which is why it is worked out above.
                child.location = (clip, y_slant, z)
                child.rotation_euler = (angle, 0.0, 0.0)
                part = GeoNodeCutpart(child)
                part.set_input('Length', shelf_w)
                part.set_input('Width', shelf_depth)
                part.set_input('Thickness', st)
                fence = next(
                    (c for c in child.children
                     if c.get('hb_part_role') == PART_ROLE_SHOE_FENCE), None)
                if fence is not None:
                    # Sit on the shelf top, frontmost strip, inset each side.
                    fence.location = (
                        f_inset,
                        y_front + const.SHOE_FENCE_STANDOFF
                        + const.SHOE_FENCE_DEPTH + f_back, st)
                    fpart = GeoNodeCutpart(fence)
                    fpart.set_input(
                        'Length',
                        max(shelf_w - 2 * f_inset, inch(1.0)))
                    fpart.set_input('Width', const.SHOE_FENCE_DEPTH)
                    fpart.set_input('Thickness', const.SHOE_FENCE_HEIGHT)
                    if fence_mat is not None:
                        _set_fence_finish(fpart, fence_mat)

        # ----- Doors (1 leaf, or 2 for DOUBLE swing) -----
        doors = groups.get(PART_ROLE_DOOR, [])
        if doors:
            doors.sort(key=lambda o: o.get('hb_door_index', 0))
            full = width + lo + ro
            if len(doors) == 2:
                leaf = (full - h_gap) / 2.0
            else:
                leaf = full
            for i, child in enumerate(doors):
                x = -lo + i * (leaf + h_gap)
                child.location = (x, front_y, -bo)
                part = GeoNodeCutpart(child)
                part.set_input('Length', leaf)
                part.set_input('Width', interior_h + to + bo)
                part.set_input('Thickness', const.FRONT_THICKNESS)
                _apply_front_style(child, is_drawer=False)
                _stash_door_closed(child, x, front_y, -bo, leaf, side,
                                   height=interior_h + to + bo)
                self._position_front_pull(
                    child,
                    'hamper' if child.get('hb_is_hamper') else 'door',
                    side, opening)
                apply_door_open(child, current_open_frac(child))

        # ----- Drawer stack (bottom-up fronts + boxes) -----
        # The stack FILLS the opening: fronts span the full front extent
        # (interior_h + to + bo) less the inter-front gaps. The fronts the
        # stack owns share the remainder equally; a front the user has
        # pinned holds its height while the rest absorb the difference.
        fronts = [c for c in groups.get(PART_ROLE_DRAWER_FRONT, [])
                  if not c.get('hb_rollout')]
        boxes = {c.get('hb_drawer_index', 0): c
                 for c in groups.get(PART_ROLE_DRAWER_BOX, [])
                 if not c.get('hb_rollout')}
        if fronts:
            fronts.sort(key=lambda o: o.get('hb_drawer_index', 0))
            n = len(fronts)
            span = interior_h + to + bo
            avail = span - (n - 1) * v_gap
            heights = _distribute_front_heights(
                avail,
                [(f.get(PROP_FRONT_HEIGHT, 0.0),
                  bool(f.get(PROP_UNLOCK_FRONT_HEIGHT, 0)))
                 for f in fronts])
            from . import drawer_boxes_closets as dbx
            # Opening-level default: opening override wins, else scene.
            _ovr = opening.hb_closet_opening.drawer_box_override
            default_box_type = (_ovr if _ovr and _ovr != 'DEFAULT'
                                else dbx.current_type())
            wood_d = max(depth - const.DRAWER_BOX_DEPTH_DEDUCT, inch(2.0))
            # A stretcher stands in the gap between one drawer and
            # the next, running back from the face by its own width
            # rather than the whole depth. What is typed is held to
            # what the opening has, so an oversized figure leaves a
            # stretcher the depth of the opening rather than one
            # hanging out past the back.
            strchs = groups.get(PART_ROLE_DRAWER_STRETCHER, [])
            strchs.sort(key=lambda o: o.get('hb_stretcher_index', 0))
            s_w = min(max(float(_shp.drawer_stretcher_width),
                          inch(0.5)),
                      max(depth, inch(0.5)))
            s_y = 0.0 if side == 'BACK' else -depth + s_w
            z = -bo
            for i, child in enumerate(fronts):
                dh = heights[i]
                # A front laps whatever it meets above and below
                # it - the overlay at the ends of the stack, half
                # of what the gap leaves over a stretcher in
                # between - so the opening left clear behind it is
                # its height less both laps. Every box system is
                # sized from that and stands on the floor of it,
                # the way the prior library sized and stood one.
                lap = max(st - v_gap, 0.0) / 2.0
                lap_dn = bo if i == 0 else lap
                lap_up = to if i == n - 1 else lap
                avail_h = max(dh - lap_dn - lap_up, 0.0)
                z_bot = z + lap_dn
                room = max(avail_h, inch(1.0))
                # Persist the resolved height so overlay labels read it.
                child[PROP_FRONT_HEIGHT] = dh
                child.location = (-lo, front_y, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width + lo + ro)
                part.set_input('Width', dh)
                part.set_input('Thickness', const.FRONT_THICKNESS)
                # Per-front box-system override wins over the opening
                # default; its material follows the resolved system.
                _fovr = child.get(PROP_FRONT_BOX_OVERRIDE, '')
                box_type = (_fovr if _fovr and _fovr != 'DEFAULT'
                            else default_box_type)
                box_mat = dbx.box_material(box_type)
                # Stamp the drawer's inside width and depth so the
                # accessory dialog can size a tray live; resolve the
                # jewelry-tray name so it tracks any resize.
                _inside = drawer_inside_width(width + lo + ro, box_type)
                child['hb_inside_w'] = _inside
                child['hb_open_depth'] = depth
                child[PROP_OPEN_HEIGHT] = avail_h
                child[PROP_BOX_TYPE_RESOLVED] = box_type
                _tray = child.get(PROP_JEWELRY_TRAY, '')
                if _tray and _tray != 'NONE':
                    child[PROP_JEWELRY_TRAY_NAME] = jewelry_tray_name(
                        _tray, _inside, depth)
                elif PROP_JEWELRY_TRAY_NAME in child:
                    del child[PROP_JEWELRY_TRAY_NAME]
                _apply_front_style(child, is_drawer=True)
                self._position_front_pull(child, 'drawer', side,
                                          opening)
                box = boxes.get(i)
                # Selected drawer box system decides the box proportions
                # (standard heights/slide lengths) or turns boxes off;
                # the WOOD path keeps the parametric deduct behavior.
                wood_h = max(avail_h - const.DRAWER_BOX_HEIGHT_DEDUCT,
                             inch(2.0))
                spec = dbx.size_box(box_type, avail_h, depth, wood_h,
                                    wood_d)
                warn = dbx.box_warning(box_type, avail_h, depth,
                                       wood_d)
                _stamp_warning(child, warn)
                # Explicit per-front size overrides (0 = system size).
                _dov = float(child.get(PROP_BOX_DEPTH_OVERRIDE, 0.0))
                _hov = float(child.get(PROP_BOX_HEIGHT_OVERRIDE, 0.0))
                box_d = spec[1] if spec is not None else wood_d
                if _dov > 0.0:
                    box_d = _dov
                child[PROP_BOX_SIZE_TAG] = (spec[2] if spec else 'NONE')
                if box is not None:
                    box['hb_drawer_box_type'] = box_type
                    box['hb_drawer_box_size'] = (spec[2] if spec
                                                 else 'NONE')
                    _stamp_warning(box, warn)
                    _set_part_hidden(box, spec is None)
                if box is not None and spec is not None:
                    box_h = _hov if _hov > 0.0 else spec[0]
                    # GeoNodeDrawerBox extrudes +Y from its origin, so
                    # anchor the origin at the face the drawer serves:
                    # box spans [y_box, y_box + box_d], front edge flush
                    # with the opening face, clearance at the rear.
                    y_box = (-box_d if side == 'BACK' else -depth)
                    # Each system holds its box in from the panel
                    # beside it and stands it off the floor of the
                    # clear opening by its own figures. The stand
                    # off gives way when what is left is tighter
                    # than it.
                    lift = min(dbx.floor_gap(box_type),
                               max(0.0, room - box_h))
                    s_gap = dbx.side_gap(box_type)
                    box_w = max(width - 2 * s_gap, inch(2.0))
                    box.location = (s_gap, y_box, z_bot + lift)
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
                apply_drawer_open(child, current_open_frac(child))
                # The stretcher belonging to this drawer sits in the
                # gap above it, the two fronts lapping it by half of
                # what the gap leaves. The top drawer of a stack has
                # the shelf above it instead, and there is one fewer
                # stretcher than drawers, so it is passed over.
                if i < len(strchs):
                    s_obj = strchs[i]
                    s_obj.location = (0.0, s_y,
                                      z + dh - (st - v_gap) / 2.0)
                    s_part = GeoNodeCutpart(s_obj)
                    s_part.set_input('Length', width)
                    s_part.set_input('Width', s_w)
                    s_part.set_input('Thickness', st)
                z += dh + v_gap

        # ----- Rollout trays -----
        # A tray stands the opening's Rollout Height (default 4") and
        # the stack is spaced with equal gaps above, below and between
        # (sizing from the prior library: 4" tray, 0.327" side clearance
        # for the slides). A tray can be given a height of its own, or a
        # location of its own, in which case it is held at what it was
        # given and the rest of the stack carries on sharing.
        rollouts = [c for c in groups.get(PART_ROLE_DRAWER_BOX, [])
                    if c.get('hb_rollout')]
        if rollouts:
            rollouts.sort(key=lambda o: o.get('hb_rollout_index', 0))
            from . import drawer_boxes_closets as dbx
            # A tray is a wood box on slides, which is what the prior
            # library built every one of them out of, so it is built
            # to the standard sizes a wood box is bought in. The
            # Rollout Height the opening is given is the room a tray
            # is allotted in the stack; the tray steps down to the
            # largest standard height that room takes.
            # A tray carries a front, the way the prior library built
            # every one of them. Lapped, the front stands proud of the
            # face and laps the opening the way a drawer front does.
            # Set inside instead, it is held back from each side by
            # the inset reveal and fills the front of the opening
            # depth with its own thickness, and the box behind it
            # gives that thickness up. Either way the box is held in
            # from each side by the overlay as well as the clearance
            # the slides want, so the front has the room it laps
            # clear of it.
            inset = bool(opening.hb_closet_opening.rollout_inset_front)
            ir = float(opening.hb_closet_opening.rollout_inset_reveal)
            ft = const.FRONT_THICKNESS
            f_off = ft if inset else 0.0
            box_x = lo + const.ROLLOUT_SLIDE_GAP
            box_w = max(width - lo - ro - 2 * const.ROLLOUT_SLIDE_GAP,
                        inch(2.0))
            # The depth steps down the same way, from what the opening
            # has left once an inset front has taken its own thickness
            # off the front of it. The tray is held at the face it
            # serves, so what it gives up comes off the back.
            d_avail = max(depth - f_off, inch(2.0))
            _bd = dbx.wood_depth(d_avail)
            box_d = max(d_avail if _bd is None else _bd, inch(2.0))
            if side == 'BACK':
                y_box = -box_d - f_off
                front_y_t = -f_off
            else:
                y_box = -depth + f_off
                front_y_t = -depth + f_off
            if inset:
                f_x = ir
                f_len = max(width - 2 * ir, inch(1.0))
            else:
                f_x = -lo
                f_len = width + lo + ro
            tfronts = sorted(
                (c for c in groups.get(PART_ROLE_DRAWER_FRONT, [])
                 if c.get('hb_rollout')),
                key=lambda o: o.get('hb_rollout_index', 0))
            n = len(rollouts)
            stack_h = float(opening.hb_closet_opening.rollout_height)
            heights = [tray_height(b, stack_h) for b in rollouts]
            shared = [i for i, b in enumerate(rollouts)
                      if not b.get(PROP_UNLOCK_TRAY_HEIGHT, 0)]
            gap = (interior_h - sum(heights)) / (n + 1)
            if gap < const.ROLLOUT_MIN_GAP:
                # Won't fit at the full height: hold the minimum gap and
                # shrink to the remainder. The trays sharing the stack
                # give the room up first, since a tray holding a height
                # was asked for that height; they all give room up only
                # when the sharing ones have none left to give.
                gap = const.ROLLOUT_MIN_GAP
                room = interior_h - (n + 1) * gap
                held = sum(h for i, h in enumerate(heights)
                           if i not in shared)
                share = ((room - held) / len(shared)) if shared else 0.0
                if shared and share >= const.ROLLOUT_MIN_HEIGHT:
                    for i in shared:
                        heights[i] = share
                else:
                    scale = room / (sum(heights) or 1.0)
                    heights = [max(h * scale, const.ROLLOUT_MIN_HEIGHT)
                               for h in heights]
            z = gap
            for i, box in enumerate(rollouts):
                h = heights[i]
                # A tray that was given a location stands at it, held
                # inside the opening; the rest keep the even spacing.
                if box.get(PROP_UNLOCK_TRAY_Z, 0):
                    z_tray = min(max(float(box.get(PROP_TRAY_Z, z)), 0.0),
                                 max(interior_h - h, 0.0))
                else:
                    z_tray = z
                # A tray steps down to the largest standard wood box
                # the room the stack set aside for it takes, and
                # stands off the floor of that room the way a wood box
                # stands off the floor of a drawer opening. Where the
                # room is smaller than the smallest standard the tray
                # keeps the parametric height so there is still one
                # that fits, and the warning gives the reason in the
                # words the prior library used for it.
                bh = dbx.wood_height(h)
                bh = h if bh is None else bh
                lift = min(dbx.floor_gap('WOOD'), max(0.0, h - bh))
                box['hb_drawer_box_type'] = 'WOOD'
                box['hb_drawer_box_size'] = 'WOOD'
                _stamp_warning(box, dbx.box_warning('WOOD', h,
                                                    d_avail, d_avail))
                _set_part_hidden(box, False)
                # Persist what the tray resolved to, so a dialog opens
                # on what is on screen rather than on a default.
                box[PROP_TRAY_HEIGHT] = h
                box[PROP_TRAY_Z] = z_tray
                # The tray is anchored at the face it serves and
                # runs back from it to the rear of the opening.
                box.location = (box_x, y_box, z_tray + lift)
                gb = GeoNodeObject(box)
                gb.set_input('Dim X', box_w)
                gb.set_input('Dim Y', box_d)
                gb.set_input('Dim Z', bh)
                # The front stands the whole of the room the stack set
                # aside for the tray, so a stack of them reads as a
                # bank of fronts with the gaps between them showing.
                fr = tfronts[i] if i < len(tfronts) else None
                if fr is not None:
                    fr.location = (f_x, front_y_t, z_tray)
                    fp = GeoNodeCutpart(fr)
                    fp.set_input('Length', f_len)
                    fp.set_input('Width', h)
                    fp.set_input('Thickness', ft)
                    _apply_front_style(fr, is_drawer=True)
                z += h + gap

        # ----- Cubby grid (divisions full height, shelves full width) -----
        # Both are held back from the front edge by the setback, so the
        # grid reads as recessed instead of finishing flush with the
        # panels.
        cub_setback = float(opening.hb_closet_opening.cubby_setback)
        cub_depth = max(depth - cub_setback, inch(1.0))
        # The uprights are cut from the divider thickness and the
        # shelves from the shelf thickness, which is how the prior
        # library had it: a grid can be divided in something other than
        # what its shelves are made of.
        dt = scene_props.divider_thickness
        divs = groups.get(PART_ROLE_CUBBY_DIVISION, [])
        if divs:
            divs.sort(key=lambda o: o.get('hb_cubby_index', 0))
            cols = len(divs) + 1
            cell_w = (width - len(divs) * dt) / cols
            for j, child in enumerate(divs):
                x = cell_w * (j + 1) + dt * j
                child.location = (x, 0.0, 0.0)
                part = GeoNodeCutpart(child)
                part.set_input('Length', interior_h)
                part.set_input('Width', cub_depth)
                part.set_input('Thickness', dt)
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
                part.set_input('Width', cub_depth)
                part.set_input('Thickness', st)

    # ----- regenerators (create/remove children to match config) -----

    def _position_front_pull(self, front, kind, side, opening=None):
        """Create/refresh the pull on a door / drawer / hamper front,
        using the face_frame pull assets and scene defaults (shared
        hardware across libraries). Closet front local space: X = width
        across, Y = height up, front face at Z = thickness. Doors get a
        vertical bar on the latch edge; drawers a centered horizontal
        bar; hampers a horizontal bar near the top. BACK-side island
        fronts are pending (mirrored mounting).

        An opening can say how the pulls on its own fronts sit, or that
        it wants none at all; anything it has not taken over follows the
        room. All of it is plain arithmetic written into the pull's
        location, so a run redraws in one pass."""
        existing = [c for c in front.children
                    if c.get('IS_CABINET_PULL')]
        try:
            from . import pulls_closets
            from ..face_frame import split_preview
            from ... import units
        except Exception:
            return
        op = opening.hb_closet_opening if opening is not None else None
        pull_obj = None
        if side != 'BACK' and not (op is not None and op.no_pulls):
            pull_obj = pulls_closets.resolve_pull_object()
        if pull_obj is None:
            for child in existing:
                bpy.data.objects.remove(child, do_unlink=True)
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
        # Drawer-front settings: the opening's own where it has taken
        # them over, the room's otherwise. A pair of pulls and their
        # spacing are the opening's alone - a whole run rarely wants
        # every front doubled, but one bank of wide drawers often does.
        centered = (bool(op.center_pull_on_front)
                    if (op is not None and op.unlock_center_pull)
                    else bool(getattr(cp, 'center_pulls_on_drawer_front',
                                      True)))
        v_drawer = (float(op.drawer_pull_vertical_location)
                    if (op is not None and op.unlock_pull_location)
                    else float(getattr(
                        cp, 'pull_vertical_location_drawers',
                        const.DRAWER_PULL_VERTICAL_LOCATION)))
        double = bool(op.double_pull_on_front) if op is not None else False
        pull_spacing = (float(op.distance_between_pulls) if op is not None
                        else const.DISTANCE_BETWEEN_PULLS)
        part = GeoNodeCutpart(front)
        width = part.get_input('Length')
        height = part.get_input('Width')
        thickness = part.get_input('Thickness')
        half = pulls_closets.pull_length(pull_obj) / 2.0
        z = thickness

        if kind == 'drawer':
            # The drawer figure is measured to the middle of the pull,
            # not to its edge the way the door figures below are.
            x = width / 2.0
            y = height / 2.0 if centered else height - v_drawer
            rot = (math.radians(-90.0), 0.0, 0.0)
        elif kind == 'hamper':
            # A hamper front takes the measured location even where the
            # room centers its drawer pulls, as the prior library had it.
            x = width / 2.0
            y = height - v_drawer
            rot = (math.radians(-90.0), 0.0, 0.0)
        elif front.get('hb_hinge') == 'TOP':
            # Lift-up door: horizontal bar centered near the bottom edge
            # (the free edge that lifts).
            x = width / 2.0
            y = v_base + half
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
            # Base / Tall / Upper, floor-referenced. On Auto the rule
            # is read off the door: hold the pull at the TALL height
            # off the floor; when the door bottom is already above that
            # height use the UPPER convention (near the bottom edge);
            # when the tall height would land past the door top use the
            # BASE convention (near the top edge). Naming one instead
            # holds the door to it, clamped to stay on the front.
            bottom_w = split_preview._world_matrix(front).translation.z
            tall_target = v_tall
            rule = (op.door_pull_location if op is not None else 'AUTO')
            base_y = height - v_base - half
            if rule == 'BASE':
                y = base_y
            elif rule == 'UPPER':
                y = v_upper + half
            elif rule == 'TALL':
                y = (tall_target - bottom_w) + half
            elif bottom_w >= tall_target:
                y = v_upper + half
            else:
                tall_y = (tall_target - bottom_w) + half
                y = tall_y if tall_y <= base_y else base_y
            y = min(max(y, half), max(height - half, half))
            rot = (math.radians(-90.0), 0.0, math.radians(90.0))

        # One pull, or a pair straddling the middle of the front where
        # the opening has asked for two.
        if double and kind in ('drawer', 'hamper'):
            offsets = (-pull_spacing / 2.0, pull_spacing / 2.0)
        else:
            offsets = (0.0,)
        existing.sort(key=lambda o: o.get('hb_pull_index', 0))
        while len(existing) > len(offsets):
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        while len(existing) < len(offsets):
            inst = bpy.data.objects.new(f"Pull - {front.name}",
                                        pull_obj.data)
            bpy.context.scene.collection.objects.link(inst)
            inst.parent = front
            inst['hb_part_role'] = 'PULL'
            inst['IS_CABINET_PULL'] = True
            existing.append(inst)
        for i, dx in enumerate(offsets):
            inst = existing[i]
            if inst.data is not pull_obj.data:
                inst.data = pull_obj.data
            # Model name rides the instance (the mesh datablock name is
            # the asset's internal name) - downstream reports key on it.
            inst['hb_pull_index'] = i
            inst['hb_pull_name'] = pulls_closets.current_pull_stem()
            inst.location = (x + dx, y, z)
            inst.rotation_euler = rot

    def _reconcile_adj_shelves(self, opening):
        qty = max(0, int(opening.hb_closet_opening.adj_shelf_qty))
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_ADJ_SHELF]
        existing.sort(key=lambda o: o.get('hb_adj_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        while len(existing) < qty:
            obj = add_fixed_shelf(opening, 0.0, role=PART_ROLE_ADJ_SHELF)
            obj['hb_adj_index'] = len(existing)
            existing.append(obj)

    def _reconcile_slanted_shelves(self, opening):
        """Slanted shoe shelves: create/remove tilted shelves to match the
        quantity, each carrying a metal shoe fence child (removed with it).
        Positions and angle come from the layout pass."""
        qty = max(0, int(opening.hb_closet_opening.slant_qty))
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_SLANTED_SHELF]
        existing.sort(key=lambda o: o.get('hb_slant_index', 0))
        while len(existing) > qty:
            _remove_part_tree(existing.pop())  # shelf + its fence child
        while len(existing) < qty:
            shelf = CabinetPart()
            shelf.create('Slanted Shelf')
            shelf.obj.parent = opening
            shelf.obj['hb_part_role'] = PART_ROLE_SLANTED_SHELF
            shelf.obj['hb_slant_index'] = len(existing)
            shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            shelf.set_input('Mirror Y', True)
            fence = CabinetPart()
            fence.create('Shoe Fence')
            fence.obj.parent = shelf.obj
            fence.obj['hb_part_role'] = PART_ROLE_SHOE_FENCE
            fence.set_input('Mirror Y', True)
            existing.append(shelf.obj)

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
        swing = (bay_obj.hb_closet_bay.door_swing
                 if side == 'FRONT' else '')
        qty = FRONT_QTY_BY_SWING.get(swing, 0)
        existing = [c for c in bay_obj.children
                    if c.get('hb_part_role') == PART_ROLE_DOOR
                    and c.get('hb_bay_door')]
        existing.sort(key=lambda o: o.get('hb_door_index', 0))
        hamper = 1 if swing == 'TILT_OUT' else 0
        name = 'Hamper Front' if hamper else 'Door'
        while len(existing) > qty:
            _remove_part_tree(existing.pop())  # front + its pull
        while len(existing) < qty:
            front = CabinetPart()
            front.create(name)
            front.obj.parent = bay_obj
            front.obj['hb_part_role'] = PART_ROLE_DOOR
            front.obj['hb_bay_door'] = 1
            front.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            front.obj.rotation_euler.x = math.radians(90)
            front.obj['hb_door_index'] = len(existing)
            front.obj['hb_is_hamper'] = hamper
            existing.append(front.obj)
        for i, obj in enumerate(existing):
            # Turning the hamper on or off under a front that is already
            # hanging has to reach that front: the pull it carries and
            # the edge it hinges on both read this, and only the build
            # above used to set it. Renamed with it so the outliner says
            # what the part is, and only when it actually changes, to
            # keep Blender from walking the numeric suffix every solve.
            if obj.get('hb_is_hamper', 0) != hamper:
                obj['hb_is_hamper'] = hamper
                obj.name = name
            if obj.get('hb_is_hamper'):
                obj['hb_hinge'] = 'BOTTOM'
            elif swing == 'DOUBLE':
                obj['hb_hinge'] = 'LEFT' if i == 0 else 'RIGHT'
            elif swing == 'LIFT_UP':
                obj['hb_hinge'] = 'TOP'
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
        sp = self.obj.hb_closet_starter
        # A door across a whole bay has no opening of its own, so it
        # takes the run's overlays as they come.
        lo, ro, to, bo = front_overlays(sp, scene_props)
        h_gap = sp.horizontal_gap
        front_y = base_y - o_depth - sp.door_to_cabinet_gap
        width = bay['width']
        interior_h = bay['interior_h']
        full = width + lo + ro
        leaf = (full - h_gap) / 2.0 if len(doors) == 2 else full
        for i, child in enumerate(doors):
            x = -lo + i * (leaf + h_gap)
            z = bay['interior_z'] - bo
            child.location = (x, front_y, z)
            part = GeoNodeCutpart(child)
            part.set_input('Length', leaf)
            part.set_input('Width', interior_h + to + bo)
            part.set_input('Thickness', const.FRONT_THICKNESS)
            _apply_front_style(child, is_drawer=False)
            _stash_door_closed(child, x, front_y, z, leaf, side,
                               height=interior_h + to + bo)
            self._position_front_pull(
                child, 'hamper' if child.get('hb_is_hamper') else 'door',
                side)
            apply_door_open(child, current_open_frac(child))

    def _reconcile_doors(self, opening, side):
        # A bay-wide door supersedes opening doors on its side.
        bay = find_bay_cage(opening)
        if (side == 'FRONT' and bay is not None
                and bay.hb_closet_bay.door_swing):
            swing = ''
        else:
            swing = opening.hb_closet_opening.door_swing
        qty = FRONT_QTY_BY_SWING.get(swing, 0)
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_DOOR]
        existing.sort(key=lambda o: o.get('hb_door_index', 0))
        hamper = 1 if swing == 'TILT_OUT' else 0
        name = 'Hamper Front' if hamper else 'Door'
        while len(existing) > qty:
            _remove_part_tree(existing.pop())  # front + its pull
        while len(existing) < qty:
            obj = self._make_front(opening, name, PART_ROLE_DOOR, side)
            obj['hb_door_index'] = len(existing)
            obj['hb_is_hamper'] = hamper
            existing.append(obj)
        # Hinge side per leaf (drives pull placement + open swing): a
        # tilt-out hamper hinges at the BOTTOM; a DOUBLE pair hinges
        # outward so the pulls meet at the center; a lift-up door hinges
        # at the TOP; singles hinge on their swing side.
        for i, obj in enumerate(existing):
            # Turning a front that is already hanging from a door into
            # a tilt-out has to reach that front: the pull it carries
            # and the edge it hinges on both read this. Renamed with it
            # so the outliner says what the part is, and only when it
            # actually changes, to keep Blender from walking the
            # numeric suffix every solve.
            if obj.get('hb_is_hamper', 0) != hamper:
                obj['hb_is_hamper'] = hamper
                obj.name = name
            if obj.get('hb_is_hamper'):
                obj['hb_hinge'] = 'BOTTOM'
            elif swing == 'DOUBLE':
                obj['hb_hinge'] = 'LEFT' if i == 0 else 'RIGHT'
            elif swing == 'LIFT_UP':
                obj['hb_hinge'] = 'TOP'
            else:
                obj['hb_hinge'] = swing or 'LEFT'

    def _reconcile_drawers(self, opening, side):
        qty = max(0, int(opening.hb_closet_opening.drawer_qty))
        fronts = [c for c in opening.children
                  if c.get('hb_part_role') == PART_ROLE_DRAWER_FRONT
                  and not c.get('hb_rollout')]
        boxes = [c for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_DRAWER_BOX
                 and not c.get('hb_rollout')]
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
        # A bank pasted from another opening arrives with the heights
        # its drawers were holding. They are handed over as the fronts
        # come into being and the note is torn up, so a paste lands on
        # the sizes that were copied and nothing is left to re-apply.
        pins = opening.get(PROP_PASTED_FRONT_PINS)
        if pins is not None:
            flat = list(pins)
            for front, (h, lk) in zip(fronts, zip(flat[::2], flat[1::2])):
                front[PROP_FRONT_HEIGHT] = float(h)
                front[PROP_UNLOCK_FRONT_HEIGHT] = int(lk)
            del opening[PROP_PASTED_FRONT_PINS]
        while len(boxes) < qty:
            box = GeoNodeDrawerBox()
            box.create('Drawer Box')
            box.obj.parent = opening
            box.obj['hb_part_role'] = PART_ROLE_DRAWER_BOX
            box.obj['hb_drawer_index'] = len(boxes)
            boxes.append(box.obj)
        # One stretcher between each drawer and the next, so a stack
        # of n carries n-1 of them: the shelf above the stack caps
        # the top and the opening carries the bottom drawer.
        want_s = max(qty - 1, 0)
        strchs = [c for c in opening.children
                  if c.get('hb_part_role') == PART_ROLE_DRAWER_STRETCHER]
        strchs.sort(key=lambda o: o.get('hb_stretcher_index', 0))
        while len(strchs) > want_s:
            bpy.data.objects.remove(strchs.pop(), do_unlink=True)
        while len(strchs) < want_s:
            part = CabinetPart()
            part.create('Drawer Stretcher')
            part.obj.parent = opening
            part.obj['hb_part_role'] = PART_ROLE_DRAWER_STRETCHER
            part.obj['hb_stretcher_index'] = len(strchs)
            part.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            part.set_input('Mirror Y', True)
            strchs.append(part.obj)

    def _reconcile_rollouts(self, opening, side):
        """Pullout trays: a drawer box on slides with a front on it.
        Box and front carry the same roles a drawer's do, tagged
        hb_rollout so the drawer reconciler leaves them alone; the
        opening layout spaces them."""
        qty = max(0, int(opening.hb_closet_opening.rollout_qty))
        boxes = [c for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_DRAWER_BOX
                 and c.get('hb_rollout')]
        boxes.sort(key=lambda o: o.get('hb_rollout_index', 0))
        while len(boxes) > qty:
            bpy.data.objects.remove(boxes.pop(), do_unlink=True)
        while len(boxes) < qty:
            box = GeoNodeDrawerBox()
            box.create('Rollout Tray')
            box.obj.parent = opening
            box.obj['hb_part_role'] = PART_ROLE_DRAWER_BOX
            box.obj['hb_rollout'] = 1
            box.obj['hb_rollout_index'] = len(boxes)
            boxes.append(box.obj)
        fronts = [c for c in opening.children
                  if c.get('hb_part_role') == PART_ROLE_DRAWER_FRONT
                  and c.get('hb_rollout')]
        fronts.sort(key=lambda o: o.get('hb_rollout_index', 0))
        while len(fronts) > qty:
            _remove_part_tree(fronts.pop())
        while len(fronts) < qty:
            obj = self._make_front(opening, 'Rollout Front',
                                   PART_ROLE_DRAWER_FRONT, side)
            obj['hb_rollout'] = 1
            obj['hb_rollout_index'] = len(fronts)
            fronts.append(obj)

    # -------------------------------------------------------------
    # Accessories
    # -------------------------------------------------------------
    def _acc_part(self, cage, name, role, kids, rotate_x=False):
        """Find-or-create one melamine child under an accessory cage,
        matched on role + name so an accessory can carry several."""
        for c in kids.get(role, ()):
            if c.get('hb_acc_part') == name:
                return c
        part = CabinetPart()
        part.create(name)
        part.set_input('Mirror Y', True)
        part.obj.parent = cage
        part.obj['hb_part_role'] = role
        part.obj['hb_acc_part'] = name
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        if rotate_x:
            part.obj.rotation_euler.x = math.radians(90)
        kids.setdefault(role, []).append(part.obj)
        return part.obj

    def _placeholder_material(self):
        """The one red material every placeholder shares."""
        name = const.ACCESSORY_PLACEHOLDER_MATERIAL
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
            mat.diffuse_color = const.ACCESSORY_PLACEHOLDER_COLOR
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf is not None:
                bsdf.inputs['Base Color'].default_value = (
                    const.ACCESSORY_PLACEHOLDER_COLOR)
                if 'Roughness' in bsdf.inputs:
                    bsdf.inputs['Roughness'].default_value = 0.9
        return mat

    def _acc_placeholder(self, cage, want, kids):
        """A red block standing in for a model that is not installed.

        It is drawn at the size the accessory claims rather than at
        the shape of the thing, because the shape is exactly what is
        not known here. What it is good for is seeing that the space
        has been taken and by roughly what - and seeing, plainly, that
        a model is missing."""
        found = kids.get(PART_ROLE_ACCESSORY_BLOCK) or ()
        block = found[0] if found else None
        if not want:
            if block is not None:
                _remove_part_tree(block)
                kids.pop(PART_ROLE_ACCESSORY_BLOCK, None)
            return None
        if block is None:
            mesh = bpy.data.meshes.new('Accessory Placeholder')
            block = bpy.data.objects.new('Accessory Placeholder', mesh)
            bpy.context.scene.collection.objects.link(block)
            block.parent = cage
            block.matrix_parent_inverse.identity()
            block['hb_part_role'] = PART_ROLE_ACCESSORY_BLOCK
            block['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            block.data.materials.append(self._placeholder_material())
            kids.setdefault(PART_ROLE_ACCESSORY_BLOCK,
                            []).append(block)
        # Red twice over: the material for a lit view, and the object
        # colour for the solid one. Most of the time a closet is drawn
        # in solid shading, where the material is not what is shown,
        # and a stand-in that reads as ordinary melamine is worse than
        # no stand-in at all.
        block.color = const.ACCESSORY_PLACEHOLDER_COLOR
        return block

    def _size_placeholder(self, kids, width, depth, height):
        """Rewrite the block to fill the space it stands for.

        The mesh is rebuilt rather than scaled, so the cage and the
        block read the same size in every list that measures them -
        but only when the size has actually changed. Rebuilding eight
        vertices is cheap; rebuilding them for every accessory on
        every recalculation is not."""
        found = kids.get(PART_ROLE_ACCESSORY_BLOCK) or ()
        block = found[0] if found else None
        if block is None:
            return
        size = (round(width, 7), round(depth, 7), round(height, 7))
        if tuple(block.get('hb_block_size', ())) == size:
            return
        block['hb_block_size'] = size
        verts = [(0.0, 0.0, 0.0), (width, 0.0, 0.0),
                 (width, -depth, 0.0), (0.0, -depth, 0.0),
                 (0.0, 0.0, height), (width, 0.0, height),
                 (width, -depth, height), (0.0, -depth, height)]
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        mesh = block.data
        mesh.clear_geometry()
        mesh.from_pydata(verts, [], faces)
        mesh.update()

    def _acc_model(self, cage, acc_def, kids):
        """The bought model under an accessory cage, or None.

        The catalog says which model an accessory should be showing
        and where that model is on this machine. When it is not here -
        nothing is offering closet accessories, or this particular one
        has not been installed - any model already hanging is taken
        off and a block is drawn in its place. The accessory still
        holds its space and still measures either way."""
        from . import accessories_closets as acc
        found = kids.get(PART_ROLE_ACCESSORY_MODEL) or ()
        existing = found[0] if found else None
        want = accessory_model_path_for(cage, acc_def)
        if not acc.model_is_installed(want):
            if existing is not None:
                _remove_part_tree(existing)
                kids.pop(PART_ROLE_ACCESSORY_MODEL, None)
            # Nothing to draw, so the space is drawn instead.
            self._acc_placeholder(cage, True, kids)
            return None
        name = accessory_model_name(cage, acc_def)
        if existing is not None:
            if existing.get(PROP_ACCESSORY_MODEL) == name:
                # Squared up on the way past, so a model that
                # was brought in turned - by an older build of
                # this library, or by hand - comes back straight.
                existing.rotation_euler = (0.0, 0.0, 0.0)
                self._acc_placeholder(cage, False, kids)
                return existing
            # The width was changed under it. These are bought at a
            # set size rather than stretched, so a different width is
            # a different thing and the old one comes out.
            _remove_part_tree(existing)
            kids.pop(PART_ROLE_ACCESSORY_MODEL, None)
        obj = acc.instance_accessory_model(want, acc_def.label)
        if obj is None:
            # Named but not there: the catalog offers it, it just has
            # not been installed. That reads the same to a person as
            # nothing being offered at all, so it draws the same.
            self._acc_placeholder(cage, True, kids)
            return None
        bpy.context.scene.collection.objects.link(obj)
        obj.parent = cage
        obj.matrix_parent_inverse.identity()
        # No turning. A model's depth runs back down +Y and so does
        # this library's; it is placed at the front and runs back from
        # there. Turning one end for end would stand it out in front
        # of the closet, which is a mistake worth not repeating.
        obj.rotation_euler.z = 0.0
        obj['hb_part_role'] = PART_ROLE_ACCESSORY_MODEL
        obj[PROP_ACCESSORY_MODEL] = name
        obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        kids.setdefault(PART_ROLE_ACCESSORY_MODEL, []).append(obj)
        # The real thing turned up, so the stand-in comes off.
        self._acc_placeholder(cage, False, kids)
        return obj

    def _accessories(self, cages, width, depth, interior_h, side,
                     front_y, lo, ro, to, bo, scene_props):
        """Bring every accessory in one opening into line, and place
        it, in a single pass.

        Reconciling and placing want exactly the same two things - the
        same catalog line and the same set of children - so they are
        done together. Asking Blender twice for an object's children
        is the expensive way to do nothing: it works them out by
        walking every object in the file, so each ask costs the whole
        scene. Here each cage is read once.

        An accessory whose catalog key is no longer offered is left
        standing but emptied, so a file saved against a fuller catalog
        opens rather than losing the person's work."""
        from . import accessories_closets as acc
        for cage in cages:
            kids = {}
            for child in cage.children:
                kids.setdefault(child.get('hb_part_role'),
                                []).append(child)
            acc_def = acc.get(cage.get(PROP_ACCESSORY_KEY, ''))
            if acc_def is None:
                for group in kids.values():
                    for child in group:
                        _remove_part_tree(child)
                continue

            # What it is, and what it is showing.
            self._acc_model(cage, acc_def, kids)
            if acc_def.family == acc.FAMILY_INSERT:
                self._acc_part(cage, 'Ironing Board Mount',
                               PART_ROLE_ACCESSORY_PART, kids)
                self._acc_part(cage, 'Accessory Shelf',
                               PART_ROLE_ACCESSORY_PART, kids)
                if not kids.get(PART_ROLE_DRAWER_FRONT):
                    front = self._make_front(
                        cage, 'Ironing Board Front',
                        PART_ROLE_DRAWER_FRONT, side)
                    front['hb_accessory_front'] = 1
                    kids.setdefault(PART_ROLE_DRAWER_FRONT,
                                    []).append(front)

            # Where it sits. A height set close to the floor is taken
            # to mean the floor.
            z = float(cage.get(PROP_ACCESSORY_Z, 0.0))
            if z < const.ACCESSORY_BOTTOM_SNAP_TOL:
                z = 0.0
            z = max(0.0, min(z, max(interior_h - acc_def.height, 0.0)))
            cage[PROP_ACCESSORY_Z] = z

            band = accessory_band(cage, acc_def, width)
            want_w = acc_def.band_width(band)
            want_d = acc_def.band_depth(band)
            geo = GeoNodeCage(cage)

            if acc_def.family == acc.FAMILY_PANEL:
                # It hangs off a panel, so it claims that panel's
                # thickness across, what it reaches back, and a hand's
                # height - enough to take hold of, not enough to
                # pretend it fills the opening.
                cage.location = (0.0, 0.0, z)
                cage_d = min(want_d or depth, depth)
                geo.set_input('Dim X', scene_props.panel_thickness)
                geo.set_input('Dim Y', cage_d)
                geo.set_input('Dim Z', const.ACCESSORY_PANEL_CAGE_H)
                self._layout_panel_accessory(
                    cage, acc_def, kids, width, depth,
                    scene_props.panel_thickness)
                self._size_placeholder(
                    kids, scene_props.panel_thickness, cage_d,
                    const.ACCESSORY_PANEL_CAGE_H)
            elif acc_def.family == acc.FAMILY_OPENING:
                # A pull-out is fitted at the front of the opening and
                # runs back its own depth, so the cage does the same.
                cage_d = min(acc_def.depth or depth, depth)
                cage.location = (0.0, -(depth - cage_d), z)
                geo.set_input('Dim X', width)
                geo.set_input('Dim Y', cage_d)
                geo.set_input('Dim Z', acc_def.reserved_height
                              or interior_h)
                self._layout_opening_accessory(cage, acc_def, kids,
                                               width, cage_d)
                self._size_placeholder(
                    kids, width, cage_d,
                    acc_def.reserved_height or interior_h)
            else:
                cage.location = (0.0, 0.0, z)
                geo.set_input('Dim X', acc_def.width or width)
                geo.set_input('Dim Y', acc_def.depth or depth)
                geo.set_input('Dim Z', acc_def.reserved_height
                              or interior_h)
                self._acc_ironing_board_drawer(
                    cage, acc_def, kids, width, depth, interior_h,
                    side, front_y, lo, ro, to, bo, scene_props)
                self._size_placeholder(
                    kids, acc_def.width or width,
                    acc_def.depth or depth,
                    acc_def.reserved_height or interior_h)

            self._warn_accessory_fit(cage, acc_def, want_w, want_d,
                                     width, depth, interior_h, z)

    def _warn_accessory_fit(self, cage, acc_def, want_w, want_d,
                            width, depth, interior_h, z):
        """What is wrong with where this accessory has been put, in the
        words the prior library used. One message, the first thing that
        does not fit, carried on the cage so the overlay and the report
        both read the same line."""
        msg = ''
        need_h = acc_def.reserved_height
        if want_w > 0.0 and width + 0.0005 < want_w:
            msg = ("%s needs %s of width; this opening is %s"
                   % (acc_def.label, _in_str(want_w), _in_str(width)))
        elif want_d > 0.0 and depth + 0.0005 < want_d:
            msg = ("%s needs %s of depth; this opening is %s"
                   % (acc_def.label, _in_str(want_d), _in_str(depth)))
        elif need_h > 0.0 and interior_h + 0.0005 < need_h:
            msg = ("%s needs %s of height with its clearances; this "
                   "opening is %s" % (acc_def.label, _in_str(need_h),
                                      _in_str(interior_h)))
        elif (need_h > 0.0 and z + need_h > interior_h + 0.0005):
            msg = ("%s does not clear the top of the opening where it "
                   "is set" % acc_def.label)
        if msg:
            cage[PROP_ACCESSORY_WARNING] = msg
        elif PROP_ACCESSORY_WARNING in cage:
            del cage[PROP_ACCESSORY_WARNING]
        _stamp_warning(cage, msg)
        return msg

    def _acc_ironing_board_drawer(self, cage, acc_def, kids, width,
                                  depth, interior_h, side, front_y,
                                  lo, ro, to, bo, scene_props):
        """The one accessory the library builds parts for.

        A compartment at the floor of the opening holds the folded
        board: a melamine plate it bolts to, a front that drops to open
        it, and a shelf capping the compartment. Everything above that
        shelf is left alone - a bay can carry the drawer at the bottom
        and shelves the rest of the way up, which is how it was drawn
        in the prior library.

        The plate is a fixed size (the board is bought at one size), so
        it is centered rather than stretched. The shelf and the front
        take the opening's width."""
        st = scene_props.shelf_thickness
        plat_t = const.IRONING_BOARD_PLATFORM_THICKNESS
        open_h = const.IRONING_BOARD_OPENING_HEIGHT
        # The plate the board bolts to: flush to the front edge, its
        # underside on the opening floor, centered left to right.
        plate = self._acc_part(cage, 'Ironing Board Mount',
                               PART_ROLE_ACCESSORY_PART, kids)
        p_w = min(const.IRONING_BOARD_PLATFORM_WIDTH, width)
        p_d = min(const.IRONING_BOARD_PLATFORM_DEPTH, depth)
        plate.location = ((width - p_w) / 2.0, -(depth - p_d), 0.0)
        pg = GeoNodeCutpart(plate)
        pg.set_input('Length', p_w)
        pg.set_input('Width', p_d)
        pg.set_input('Thickness', plat_t)
        # The shelf that caps the compartment. Its underside sits the
        # compartment height above the plate, so raising the plate
        # thickness raises the shelf with it.
        cap_z = min(open_h + plat_t, max(interior_h - st, 0.0))
        shelf = self._acc_part(cage, 'Accessory Shelf',
                               PART_ROLE_ACCESSORY_PART, kids)
        shelf.location = (0.0, 0.0, cap_z)
        sg = GeoNodeCutpart(shelf)
        sg.set_input('Length', width)
        sg.set_input('Width', depth)
        sg.set_input('Thickness', st)
        # The front covers the compartment and laps the shelf above it
        # by the standard overlay, the way a drawer front laps what it
        # meets. It opens on its bottom edge (the board folds down out
        # of it), which is the hinge HB5 already builds for a hamper.
        found = kids.get(PART_ROLE_DRAWER_FRONT) or ()
        front = found[0] if found else None
        if front is not None:
            f_h = cap_z + bo
            front.location = (-lo, front_y, -bo)
            fg = GeoNodeCutpart(front)
            fg.set_input('Length', width + lo + ro)
            fg.set_input('Width', f_h)
            fg.set_input('Thickness', const.FRONT_THICKNESS)
            front[PROP_FRONT_HEIGHT] = f_h
            front[PROP_OPEN_HEIGHT] = cap_z
            # Tilt-out, pivoting on its bottom edge: the hinge HB5
            # already builds for a hamper front, and the same motion
            # the prior library gave this front.
            front['hb_hinge'] = 'BOTTOM'
            _apply_front_style(front, is_drawer=True)
            # The pull follows the OPENING's settings (no pulls, 
            # location, doubles), not the cage's.
            self._position_front_pull(front, 'drawer', side,
                                      cage.parent)
            # An accessory front hangs off its own cage rather than off
            # an opening, so the shared open-fraction lookup does not
            # reach it. It carries its own figure instead.
            _stash_door_closed(front, -lo, front_y, -bo,
                               width + lo + ro, side, f_h)
            apply_door_open(front, float(front.get('hb_drawer_open',
                                                   0.0)))
        # The board itself stands on the plate.
        found = kids.get(PART_ROLE_ACCESSORY_MODEL) or ()
        model = found[0] if found else None
        if model is not None:
            model.location = (width / 2.0, -depth, plat_t)
        return cap_z + st

    def _layout_opening_accessory(self, cage, acc_def, kids, width,
                                  cage_d):
        """Seat one pull-out inside its cage.

        These are bought whole and are not cut to fit, so the model is
        centred across the opening rather than stretched, and it is
        pushed to the front where its runners land. Up and down, its
        own origin is the mounting line: the room the accessory wants
        below that line is what lifts it off the bottom of its cage,
        which is how the prior library sat them."""
        found = kids.get(PART_ROLE_ACCESSORY_MODEL) or ()
        if not found:
            return
        found[0].location = (width / 2.0, -cage_d,
                             acc_def.space_below - acc_def.model_drop)

    def _layout_panel_accessory(self, cage, acc_def, kids, width,
                                depth, pt):
        """Hang one accessory off the face of a panel.

        There are four faces to choose from - either side of the panel
        at each end of the opening - and the model is drawn to hang
        off one of them, reaching out in one direction only. Rather
        than keep four models, the one is mirrored to face the other
        way, which is what the prior library did.

        Front to back it sits at the front of the opening and reaches
        back, the way a rack pulls out."""
        from . import accessories_closets as acc
        loc = cage.get(PROP_ACCESSORY_PANEL_LOC,
                       acc.PANEL_DEFAULT_LOCATION)
        if loc not in acc.PANEL_LOCATION_KEYS:
            loc = acc.PANEL_DEFAULT_LOCATION
            cage[PROP_ACCESSORY_PANEL_LOC] = loc
        # x is the face it screws to; mirrored means it reaches the
        # other way, so that an inside face always reaches inward and
        # an outside face always reaches away.
        if loc == acc.PANEL_OUTSIDE_LEFT:
            x, mirror = -pt, False
        elif loc == acc.PANEL_INSIDE_LEFT:
            x, mirror = 0.0, True
        elif loc == acc.PANEL_INSIDE_RIGHT:
            x, mirror = width, False
        else:
            x, mirror = width + pt, True
        found = kids.get(PART_ROLE_ACCESSORY_MODEL) or ()
        if found:
            found[0].location = (x, -depth, 0.0)
            found[0].scale.x = -1.0 if mirror else 1.0
        return x, mirror

    def _reconcile_captured_back(self, opening):
        """One captured back per opening, carrying a corner relief at
        each top corner. The reliefs are always on the part and always
        sized; whether either one cuts is a setting, so toggling one
        costs a modifier switch rather than a rebuild."""
        want = bool(opening.hb_closet_opening.add_back)
        back = None
        for c in list(opening.children):
            if c.get('hb_part_role') != PART_ROLE_CAPTURED_BACK:
                continue
            if want and back is None:
                back = c
            else:
                _remove_part_tree(c)
        if want and back is None:
            part = CabinetPart()
            part.create('Captured Back')
            part.obj.parent = opening
            part.obj['hb_part_role'] = PART_ROLE_CAPTURED_BACK
            part.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            part.obj.rotation_euler.x = math.radians(90)
            part.add_part_modifier('CPM_CORNERNOTCH', 'Notch Left')
            part.add_part_modifier('CPM_CORNERNOTCH', 'Notch Right')
            back = part.obj
        # Older files: a back built before the reliefs landed is missing
        # them, so they are put on as we go past.
        if back is not None:
            for name in ('Notch Left', 'Notch Right'):
                if back.modifiers.get(name) is None:
                    GeoNodeCutpart(back).add_part_modifier(
                        'CPM_CORNERNOTCH', name)
        return back

    def _reconcile_cubbies(self, opening):
        cols = max(1, int(opening.hb_closet_opening.cubby_cols))
        rows = max(1, int(opening.hb_closet_opening.cubby_rows))
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

    def _lay_out_shelf_cleat(self, shelf, bay_obj, bay, st):
        """Size and place the cleat under a shelf that carries one. It
        hangs from the shelf's underside at the back of the bay, the
        same four inches deep as the wall cleat above it."""
        cleat = next((c for c in shelf.children
                      if c.get('hb_part_role') == PART_ROLE_CLEAT), None)
        if cleat is None:
            return
        # Turned on its edge the cleat stands up from its origin, so
        # it is dropped its own width to hang under the shelf instead.
        cleat.location = (0.0, 0.0, -const.CLEAT_WIDTH)
        cleat.rotation_euler = (math.radians(90), 0.0, 0.0)
        part = GeoNodeCutpart(cleat)
        part.set_input('Length', bay['width'])
        part.set_input('Width', const.CLEAT_WIDTH)
        part.set_input('Thickness', st)
        # A double island has no wall behind the shelf to cleat to.
        _set_part_hidden(
            cleat,
            self.is_double or bay_obj.hb_closet_bay.remove_shelf_cleat)

    def _bay_split_shelves(self, bay_obj, side):
        """Committed splitting shelves of one side, bottom-up."""
        shelves = [c for c in bay_obj.children
                   if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF
                   and c.get(PROP_OPENING_SIDE, 'FRONT') == side
                   and not c.get('hb_preview')]
        shelves.sort(key=lambda o: o.get('hb_z_offset', 0.0))
        return shelves

    def _bay_divisions(self, bay_obj, side):
        """Divisions of one side, left to right."""
        divs = [c for c in bay_obj.children
                if c.get('hb_part_role') == PART_ROLE_DIVISION
                and c.get(PROP_OPENING_SIDE, 'FRONT') == side]
        divs.sort(key=lambda o: o.get('hb_x_offset', 0.0))
        return divs

    def _reconcile_bay_openings(self, bay_obj):
        """Adopt committed fixed shelves up to bay level (they arrive as
        opening children from the add-part modal / older files) and keep
        exactly one opening cage per cell on each side.

        A shelf splits a bay into segments across its whole width; a
        division splits one of those segments into columns. So the cells
        are the segments crossed with the columns of the segment they
        are in, and each one holds one opening. Removing a shelf merges
        the segments it was between and removing a division merges the
        columns either side of it; either way the openings that merge
        keep their contents at the height they were put at."""
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
            cuts = [float(sh.get('hb_z_offset', 0.0))
                    for sh in self._bay_split_shelves(bay_obj, side)]
            rows = len(cuts) + 1
            # A division stands in one segment rather than across the
            # whole bay, so it is placed the way an opening is: by
            # counting the shelves underneath it. A shelf put in or
            # taken out below therefore carries the divisions above it
            # into their new segment instead of stranding them.
            row_cuts = [[] for _ in range(rows)]
            for div in self._bay_divisions(bay_obj, side):
                k = min(sum(1 for c in cuts
                            if c < float(div.get('hb_seg_bottom', 0.0))),
                        rows - 1)
                div['hb_row'] = k
                row_cuts[k].append(float(div.get('hb_x_offset', 0.0)))
            for xs in row_cuts:
                xs.sort()
            cells = [(k, j) for k in range(rows)
                     for j in range(len(row_cuts[k]) + 1)]
            openings = sorted(
                [c for c in bay_obj.children
                 if c.get(TAG_OPENING_CAGE)
                 and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                key=lambda o: (o.get('hb_opening_index', 0),
                               o.get('hb_col_index', 0)))

            # Put every opening back in the cell it is standing in. An
            # opening's bottom, height and left edge are the last
            # solve's and the cuts are this one's, so counting the cuts
            # underneath an opening and to the left of it says which
            # cell it is in now. Taking a shelf out of the middle of a
            # bay merges the two segments it was between, and this is
            # what leaves the openings above it holding what the user
            # put in them instead of sliding everything down a segment.
            # Adding one reads the same way from the other side: the
            # new segment opens where the shelf went in and the
            # openings around it stay as they are. A division reads
            # across instead of up and merges the same way when it goes.
            slots = {cell: [] for cell in cells}
            for op_obj in openings:
                bottom = float(op_obj.get('hb_seg_bottom', 0.0))
                left = float(op_obj.get('hb_seg_left', 0.0))
                try:
                    seg_h = float(GeoNodeCage(op_obj).get_input('Dim Z'))
                except Exception:
                    seg_h = 0.0
                k = min(sum(1 for c in cuts if c < bottom), rows - 1)
                j = min(sum(1 for x in row_cuts[k] if x < left),
                        len(row_cuts[k]))
                slots[(k, j)].append((bottom, left, seg_h, op_obj))

            for k, j in cells:
                members = slots[(k, j)]
                if not members:
                    op = ClosetOpening()
                    op.create(f'Opening {k + 1}' if not row_cuts[k]
                              else f'Opening {k + 1}.{j + 1}')
                    op.obj.parent = bay_obj
                    if side == 'BACK':
                        op.obj[PROP_OPENING_SIDE] = 'BACK'
                    op.obj['hb_opening_index'] = k
                    op.obj['hb_col_index'] = j
                    continue
                members.sort(key=lambda m: (m[0], m[1]))
                keeper = members[0][3]
                # A merged segment runs from the bottom of the lowest
                # opening in it to the top of the highest, so a part
                # measured from a bottom moves by the difference in
                # bottoms and one measured from a top by the difference
                # in tops. Either way it comes out at the height it was
                # already hanging at. Nothing in an opening is measured
                # across it, so a merge sideways only has to gather the
                # parts up.
                base = members[0][0]
                cap = max(b + h for b, _l, h, _o in members)
                for bottom, _left, seg_h, op_obj in members:
                    d_top = cap - (bottom + seg_h)
                    d_bot = bottom - base
                    for child in list(op_obj.children):
                        if 'hb_z_offset' in child:
                            d = d_top if child.get('hb_anchor_top') else d_bot
                            if d:
                                child['hb_z_offset'] = max(
                                    0.0, float(child['hb_z_offset']) + d)
                        if op_obj is not keeper:
                            child.parent = keeper
                    if op_obj is not keeper:
                        bpy.data.objects.remove(op_obj, do_unlink=True)
                keeper['hb_opening_index'] = k
                keeper['hb_col_index'] = j

    def _layout_starter_parts(self, layout, scene_props, sp):
        # Only a unit with a top to cap takes a countertop - a base run
        # or an island. A tall or hanging unit finishes at its own top
        # shelf, so the prompt is not offered there and a value left on
        # by an older file is ignored rather than built.
        want_ctop = self.has_countertop and sp.include_countertop
        ctop = self._root_part(PART_ROLE_COUNTERTOP)
        if ctop is not None and not self.has_countertop:
            # An older file that turned a top on where one is no longer
            # offered: take the part out rather than leave it hidden in
            # the outliner and on the part list.
            bpy.data.objects.remove(ctop, do_unlink=True)
            ctop = None
        if ctop is None and want_ctop:
            # Lazily created so the prompt works on units placed before
            # the countertop landed.
            part = CabinetPart()
            part.create('Countertop')
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_COUNTERTOP
            part.set_input('Mirror Y', True)
            ctop = part.obj
        if ctop is not None:
            part = GeoNodeCutpart(ctop)
            # Overhang per side. The run grows left/right by the side
            # overhangs and front/back by the front and rear ones; the
            # part is drawn from its back-left corner.
            # Overhang per side; the top is drawn from its back-left
            # corner, so the left and rear overhangs move its origin.
            oh_l = sp.countertop_overhang_left
            oh_r = sp.countertop_overhang_right
            oh_f = sp.countertop_overhang_front
            oh_b = sp.countertop_overhang_rear
            ctop.location = (-oh_l, oh_b, sp.height)
            part.set_input('Length', sp.width + oh_l + oh_r)
            part.set_input('Width', sp.depth + oh_f + oh_b)
            part.set_input('Thickness', sp.countertop_thickness)
            # Exposed-end treatment travels with the part so the edging
            # and corner work downstream match what was asked for here.
            ctop['hb_ctop_left_finished'] = (
                1 if sp.countertop_left_finished_end else 0)
            ctop['hb_ctop_right_finished'] = (
                1 if sp.countertop_right_finished_end else 0)
            # Only an exposed end has corners to round, so the
            # figure is recorded only where one of the two flags above
            # it is set. It is carried rather than cut into the top.
            ctop['hb_ctop_corner_radius'] = (
                const.COUNTERTOP_END_RADIUS
                if (sp.countertop_radius_finished_ends
                    and (sp.countertop_left_finished_end
                         or sp.countertop_right_finished_end))
                else 0.0)
            _set_part_hidden(ctop, not want_ctop)

        self._layout_backsplashes(scene_props, sp)
        self._layout_accent_shelf(scene_props, sp)

    def _backsplash_part(self, slot):
        for c in self.obj.children:
            if (c.get('hb_part_role') == PART_ROLE_BACKSPLASH
                    and c.get('hb_splash_slot') == slot):
                return c
        return None

    def _layout_backsplashes(self, scene_props, sp):
        """Upstands along the countertop's wall edges: one across the
        back, plus one at each end that meets a wall. An end marked
        finished is exposed, so it gets no splash. Lazily created the
        same way the countertop is, so turning the prompt on works on
        units built before it existed. Splash thickness follows the
        countertop's, matching the prior library.

        Each splash is anchored on the countertop edge it stands on, so
        its thickness has to grow back across the top rather than out
        past that edge: the rear one forward off the back edge and the
        right-hand one inward off the right edge, which is what the two
        mirrored slots below are for. The left one already grows the
        right way unmirrored. Orientation and mirroring are rewritten on
        every pass so a splash built before this was settled corrects
        itself the next time the closet recalculates."""
        on = (self.has_countertop and sp.include_countertop
              and sp.include_backsplash)
        oh_l = sp.countertop_overhang_left
        oh_r = sp.countertop_overhang_right
        oh_f = sp.countertop_overhang_front
        oh_b = sp.countertop_overhang_rear
        thk = sp.countertop_thickness
        run = sp.width + oh_l + oh_r
        reach = abs(sp.depth + oh_f + oh_b - thk)
        z = sp.height + thk
        specs = (
            ('REAR', on, "Backsplash",
             (-oh_l, oh_b, z), 0.0, run, True),
            ('LEFT', on and not sp.countertop_left_finished_end,
             "Left Backsplash", (-oh_l, oh_b - thk, z),
             math.radians(-90), reach, False),
            ('RIGHT', on and not sp.countertop_right_finished_end,
             "Right Backsplash", (sp.width + oh_r, oh_b - thk, z),
             math.radians(-90), reach, True),
        )
        for slot, show, label, loc, rot_z, length, mirror_z in specs:
            splash = self._backsplash_part(slot)
            if splash is not None and not self.has_countertop:
                # An older file that turned a top on where one is no
                # longer offered: take the splash out with it rather than
                # leave it hidden in the outliner and on the part list.
                bpy.data.objects.remove(splash, do_unlink=True)
                continue
            if splash is None:
                if not show:
                    continue
                part = CabinetPart()
                part.create(label)
                part.obj.parent = self.obj
                part.obj['hb_part_role'] = PART_ROLE_BACKSPLASH
                part.obj['hb_splash_slot'] = slot
                splash = part.obj
            # Tipped up on edge so its height stands off the top, then
            # turned to run along whichever edge it belongs to.
            splash.rotation_euler = (math.radians(-90), 0.0, rot_z)
            splash.location = loc
            cut = GeoNodeCutpart(splash)
            cut.set_input('Mirror Y', True)
            cut.set_input('Mirror Z', mirror_z)
            cut.set_input('Length', length)
            cut.set_input('Width', sp.backsplash_height)
            cut.set_input('Thickness', thk)
            _set_part_hidden(splash, not show)

    def _layout_accent_shelf(self, scene_props, sp):
        """A decorative shelf laid on top of the
        run at the panel top, projecting forward by the overhang and
        past each finished end by the same amount. One spanning piece
        (uniform run) - a plain shelf part identified by its
        role."""
        want = sp.add_top_accent_shelf
        shelf = None
        for c in self.obj.children:
            if c.get('hb_part_role') == PART_ROLE_ACCENT_SHELF:
                shelf = c
                break
        if shelf is None:
            if not want:
                return
            part = CabinetPart()
            part.create('Top Accent Shelf')
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_ACCENT_SHELF
            part.set_input('Mirror Y', True)
            shelf = part.obj
        ovh = sp.top_accent_overhang
        left = ovh if sp.left_finished_end else 0.0
        right = ovh if sp.right_finished_end else 0.0
        # Base at the panel top; projects forward by the overhang and
        # out past each finished end.
        shelf.location = (-left, 0.0, sp.height)
        part = GeoNodeCutpart(shelf)
        part.set_input('Length', sp.width + left + right)
        part.set_input('Width', sp.depth + ovh)
        part.set_input('Thickness', scene_props.shelf_thickness)
        _set_part_hidden(shelf, not want)

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
        # One-time migration: units built before the bridge prompts
        # existed carry the settings as idprops. Move them onto the
        # prompts once, then read the prompts from here on.
        for key in ('left', 'right'):
            if f'hb_bridge_{key}' in self.obj:
                setattr(sp, f'bridge_{key}',
                        bool(self.obj[f'hb_bridge_{key}']))
                del self.obj[f'hb_bridge_{key}']
            if f'hb_bridge_w_{key}' in self.obj:
                setattr(sp, f'bridge_{key}_width',
                        float(self.obj[f'hb_bridge_w_{key}']))
                del self.obj[f'hb_bridge_w_{key}']
            if f'hb_bridge_bot_{key}' in self.obj:
                setattr(sp, f'include_bottom_bridge_{key}',
                        bool(self.obj[f'hb_bridge_bot_{key}']))
                del self.obj[f'hb_bridge_bot_{key}']

        for side in ('LEFT', 'RIGHT'):
            key = side.lower()
            enabled = getattr(sp, f'bridge_{key}')
            span = getattr(sp, f'bridge_{key}_width')
            bottom_on = (enabled
                         and getattr(sp, f'include_bottom_bridge_{key}'))
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
            bp.unlock_width = False
            bp.height = src.height
            bp.depth = src.depth
            bp.unlock_height = src.unlock_height
            bp.unlock_depth = src.unlock_depth
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
    (a full-footprint cutpart with the inner corner cut away, square
    or rounded). No bays/openings - its own recalculate() lays the
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
    has_hang_rail = True
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

        scene_props = run_sizes(self.obj)
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
            corner_size = scene_props.default_corner_closet_size
            sp.width = corner_size
            sp.height = self.default_height(scene_props)
            sp.depth = corner_size
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
        # around. Construction only - the geometry, role and idprops
        # left here are what anything downstream reads.
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
        # Width-lookup key (the back-support width the L-shelf rear
        # notch derives from).
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

    def _corner_wall_part(self, key, name, role, rot_z):
        """One of the strips that stand against the two walls - the
        cleats the unit is fixed with and the rails it hangs from.
        Made on demand, so a corner built before these landed gains
        them on its next recalculation."""
        for c in self.obj.children:
            if c.get('hb_l_wall_part') == key:
                return c
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['hb_l_wall_part'] = key
        part.obj.rotation_euler.x = math.radians(90)
        part.obj.rotation_euler.z = math.radians(rot_z)
        return part.obj

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
            # The rounded front corner is a second cut on the same
            # corner rather than a setting on the first - only one of
            # the pair is ever shown.
            shelf.add_part_modifier('CPM_RADIUSNOTCH', 'L Radius')
            shelf.add_part_modifier('CPM_CORNERNOTCH', 'Back Notch')
            shelves.append(shelf.obj)
        # Older files: shelves built before the Back Partition and the
        # rounded corner landed are missing those cuts - add them so
        # the shelves reconcile.
        for shelf in shelves:
            if shelf.modifiers.get('Back Notch') is None:
                GeoNodeCutpart(shelf).add_part_modifier(
                    'CPM_CORNERNOTCH', 'Back Notch')
            if shelf.modifiers.get('L Radius') is None:
                GeoNodeCutpart(shelf).add_part_modifier(
                    'CPM_RADIUSNOTCH', 'L Radius')
        return shelves

    def recalculate(self):
        cabinet_id = id(self.obj)
        if cabinet_id in _RECALCULATING:
            return
        _RECALCULATING.add(cabinet_id)
        try:
            scene_props = run_sizes(self.obj)
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
            # An end panel turned off gives its thickness back to the
            # wing it stood at the end of: the shelves, that wing's toe
            # kick and the wing depth all reach out to where it was.
            # Left is the wing along the side wall, right the one along
            # the back wall - the pairing the covers already follow.
            left_off = bool(sp.turn_off_left_panel)
            right_off = bool(sp.turn_off_right_panel)
            l_pt = 0.0 if left_off else pt
            r_pt = 0.0 if right_off else pt
            LD = min(sp.l_left_depth, W - r_pt)
            RD = min(sp.l_right_depth, D - l_pt)
            bw = sp.l_back_width
            flip = sp.l_flip_partition
            use_radius = bool(sp.l_use_radius)
            rad = max(float(sp.l_corner_radius), 0.0)
            wo = self.obj.get('hb_l_wall_offset', const.L_WALL_OFFSET)
            # Mounting belongs to the unit, not to the class it was
            # placed from: a corner standing on the floor can be lifted
            # off it, and one on the wall set back down, by dragging
            # its bottom edge. The closet type is where that lives -
            # it is already what marks an Upper corner as wall-hung.
            floor = sp.closet_type != 'HANGING'
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
                # The end flags a run records on its own end panels,
                # recorded here the same way: whether the end is
                # exposed, and whether its system holes run all the
                # way through. Flags only - they carry no geometry.
                p['hb_panel_off'] = 1 if right_off else 0
                p['hb_finished_end'] = 1 if sp.right_finished_end else 0
                p['hb_drill_through'] = (
                    1 if sp.drill_through_right else 0)
                _set_part_hidden(p, right_off)
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
                p['hb_panel_off'] = 1 if left_off else 0
                p['hb_finished_end'] = 1 if sp.left_finished_end else 0
                p['hb_drill_through'] = 1 if sp.drill_through_left else 0
                _set_part_hidden(p, left_off)

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

            # ----- Wall cleats -----
            # A cleat against each wall for the unit to be fixed with,
            # off by default the way the prior library had it. Each one
            # sits on the bottom shelf, is held off its wall by the
            # wall offset, and stops clear of the back partition - so
            # the cleat on the partition's wall is the short one.
            cleat_z = kick + st + (sp.inset_cleat if floor else 0.0)
            show_cleat = bool(sp.l_add_cleat)
            part = self._corner_wall_part(
                'Back Cleat', 'Back Cleat', PART_ROLE_CLEAT, 0.0)
            part.location = ((wo + pt) if flip else bw, -wo, cleat_z)
            gp = GeoNodeCutpart(part)
            gp.set_input('Length', max(
                (W - 2.0 * pt - wo) if flip else (W - bw - pt), 0.001))
            gp.set_input('Width', const.CLEAT_WIDTH)
            gp.set_input('Thickness', pt)
            _set_part_hidden(part, not show_cleat)

            part = self._corner_wall_part(
                'Side Cleat', 'Side Cleat', PART_ROLE_CLEAT, -90.0)
            part.location = (wo + pt,
                             -bw if flip else -(wo + pt), cleat_z)
            gp = GeoNodeCutpart(part)
            gp.set_input('Length', max(
                (D - pt - bw) if flip else (D - wo - 2.0 * pt), 0.001))
            gp.set_input('Width', const.CLEAT_WIDTH)
            gp.set_input('Thickness', pt)
            _set_part_hidden(part, not show_cleat)

            # ----- Hang rails -----
            # A rail on each wall, dropped from the top of the unit the
            # same distance a run drops its own, or held at the one
            # height when the run is set to use it. The rail on the
            # partition's wall starts clear of it. Each rail is
            # lengthened at its outer end only - the two meet at the
            # corner, so there is nowhere for the inner ends to go.
            rail_z = (sp.hang_rail_height_location
                      if sp.use_one_hang_rail_height
                      else H - const.HANG_RAIL_DROP)
            hide_rail = bool(sp.remove_hang_rail)
            ext_l = max(float(sp.extend_hang_rail_left), 0.0)
            ext_r = max(float(sp.extend_hang_rail_right), 0.0)
            x0 = pt if flip else bw
            part = self._corner_wall_part(
                'Back Rail', 'Hang Rail Back', PART_ROLE_HANG_RAIL, 0.0)
            part.location = (x0, 0.0, rail_z)
            gp = GeoNodeCutpart(part)
            gp.set_input('Length', max(W - pt - x0 + ext_r, 0.001))
            gp.set_input('Width', const.HANG_RAIL_WIDTH)
            gp.set_input('Thickness', const.HANG_RAIL_THICKNESS)
            _set_part_hidden(part, hide_rail)

            y0 = bw if flip else pt
            part = self._corner_wall_part(
                'Side Rail', 'Hang Rail Side', PART_ROLE_HANG_RAIL,
                -90.0)
            part.location = (0.0, -y0, rail_z)
            gp = GeoNodeCutpart(part)
            gp.set_input('Length', max(D - pt - y0 + ext_l, 0.001))
            gp.set_input('Width', const.HANG_RAIL_WIDTH)
            gp.set_input('Thickness', const.HANG_RAIL_THICKNESS)
            # The side wall stands at x = 0, so this one's thickness
            # has to come back into the room rather than through it.
            gp.set_input('Mirror Z', True)
            _set_part_hidden(part, hide_rail)

            # ----- Hang rail covers -----
            # A cover over each rail end that lands on a panel. The two
            # outer ends always do. At the corner the rails meet, and
            # the one stopped by the back partition is the one clipped
            # to it - so which of the two inner covers shows follows
            # the wall the partition stands against.
            #
            # Every cover stands off its wall the inch a run's does.
            # The two inner ones sit against the partition's room-side
            # face, which the wall offset holds clear of the wall - so
            # they measure from wo + pt, not from where the rail was
            # cut short. The hand recorded on each is the side of the
            # panel the claw is screwed to.
            cover_z = _hang_rail_cover_z(rail_z, st)
            cl = const.HANG_RAIL_COVER_LENGTH
            so = const.HANG_RAIL_COVER_STANDOFF
            covers = (
                ('Back Cover', 'Hang Rail Cover Back', 0.0, True,
                 (W - pt - cl, -so, cover_z), False,
                 hide_rail or bool(sp.turn_off_right_panel)),
                ('Back Corner Cover', 'Hang Rail Cover Back Corner',
                 0.0, True, (wo + pt, -so, cover_z), False,
                 hide_rail or not flip),
                ('Side Cover', 'Hang Rail Cover Side', -90.0, False,
                 (so, -(D - pt - cl), cover_z), True,
                 hide_rail or bool(sp.turn_off_left_panel)),
                ('Side Corner Cover', 'Hang Rail Cover Side Corner',
                 -90.0, True, (so, -(wo + pt), cover_z), True,
                 hide_rail or bool(flip)),
            )
            for key, nm, rot_z, on_left, loc, mirror, hide in covers:
                part = self._corner_wall_part(
                    key, nm, PART_ROLE_HANG_RAIL_COVER, rot_z)
                part['hb_clip_on_left'] = 1 if on_left else 0
                part.location = loc
                gp = GeoNodeCutpart(part)
                gp.set_input('Length', cl)
                gp.set_input('Width', const.HANG_RAIL_COVER_WIDTH)
                gp.set_input('Thickness', const.HANG_RAIL_COVER_DEPTH)
                if mirror:
                    gp.set_input('Mirror Z', True)
                _set_part_hidden(part, hide)

            for c in self.obj.children:
                if c.get('hb_l_kick'):
                    # corner kick pair (receiver/mate butt
                    # joint), not two full-length boards: the side-wall
                    # kick (receiver) runs the full left wing, stopping a
                    # panel thickness short of the wing panel and of the
                    # back wall; the back-wall kick (mate) starts at the
                    # receiver's face plane and butts square into it.
                    # the pair reads off this geometry (the mate's end
                    # must land against the receiver's face, never
                    # cross it).
                    gp = GeoNodeCutpart(c)
                    if c['hb_l_kick'] == 'Right Wing Kick':
                        # Mate: receiver face -> right wing end panel
                        # (width - ld - pt + tks).
                        c.location = (LD - setback, -RD + setback, 0.0)
                        gp.set_input('Length',
                                     max(W - r_pt - (LD - setback),
                                         0.001))
                    else:
                        # Receiver: full side wall span
                        # (fabs(depth) - pt*2 from -depth + pt).
                        c.location = (LD - setback, -pt, 0.0)
                        gp.set_input('Length',
                                     max(D - pt - l_pt, 0.001))
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
                # offset (the partition and shelf formulas assume it).
                shelf.location = (wo, -wo, z)
                gp = GeoNodeCutpart(shelf)
                gp.set_input('Length', max(W - r_pt - wo, 0.001))
                gp.set_input('Width', max(D - l_pt - wo, 0.001))
                gp.set_input('Thickness', st)
                # The front corner comes away either square or
                # rounded, and which of the two a shelf takes is set
                # for the top, the bottom and the shelves between them
                # separately. Both cuts are on the shelf and both take
                # the same extents; only the chosen one is shown. Wing
                # depths are measured from the walls, so the wall
                # offset cancels out of those extents.
                if i == 0:
                    round_it = use_radius and bool(sp.l_radius_bottom)
                elif i == len(shelves) - 1:
                    round_it = use_radius and bool(sp.l_radius_top)
                else:
                    round_it = use_radius and bool(sp.l_radius_shelves)
                # The wings are measured from the walls, so the
                # corner the notch leaves stays put when a shelf grows
                # into the space an end panel gave up.
                cut_x = max(W - r_pt - LD, 0.001)
                cut_y = max(D - l_pt - RD, 0.001)
                notch = shelf.modifiers.get('L Notch')
                if notch is not None:
                    cpm = CabinetPartModifier(shelf)
                    cpm.mod = notch
                    cpm.set_input('X', cut_x)
                    cpm.set_input('Y', cut_y)
                    cpm.set_input('Route Depth', st + 0.001)
                    # Probed: True/True lands the cut on the front-
                    # inner corner, leaving the two wings.
                    cpm.set_input('Flip X', True)
                    cpm.set_input('Flip Y', True)
                    notch.show_viewport = not round_it
                    notch.show_render = not round_it
                lrad = shelf.modifiers.get('L Radius')
                if lrad is not None:
                    cpm = CabinetPartModifier(shelf)
                    cpm.mod = lrad
                    cpm.set_input('X', cut_x)
                    cpm.set_input('Y', cut_y)
                    cpm.set_input('Route Depth', st + 0.001)
                    # A radius wider than the cut itself would round
                    # past the wings, so it is held inside them.
                    cpm.set_input('Radius',
                                  max(min(rad, cut_x - 0.001,
                                          cut_y - 0.001), 0.0))
                    cpm.set_input('Resolution',
                                  const.L_CORNER_RADIUS_SEGMENTS)
                    cpm.set_input('Turn On', True)
                    # Same corner as the square cut. This one reads
                    # Flip Y the other way round, so it takes False
                    # where the square cut takes True (probed).
                    cpm.set_input('Flip X', True)
                    cpm.set_input('Flip Y', False)
                    lrad.show_viewport = round_it
                    lrad.show_render = round_it
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
    """Bay count for a given total width. Targets a 30" bay and never lets
    a bay exceed 30" (round up), so a run splits into the fewest bays that
    keep each opening <= 30".

    The quotient is rounded to four decimals before the ceiling so that an
    exact multiple of the target - 60" giving 2.0000000001 in floating
    point - cannot tip over into an extra bay.

    Nine is the hard ceiling: a starter carries at most nine openings.

    This is advisory only. It seeds the count while a run is being dragged
    out; once the run is placed the count is the user's and is never
    recomputed from the width again."""
    quotient = round(width / const.BAY_WIDTH_TARGET, 4)
    return max(const.MIN_BAY_QTY,
               min(const.MAX_BAY_QTY, int(math.ceil(quotient))))


def find_bay_cage(obj):
    """Walk up parents from obj to the containing bay cage, or None."""
    current = obj
    while current is not None:
        if current.get(TAG_BAY_CAGE):
            return current
        current = current.parent
    return None


DOOR_OPEN_ANGLE = math.radians(110.0)
# A tilt-out hamper front pivots at its bottom edge and tilts out this
# far when fully open (angle from the prior library).
HAMPER_TILT_ANGLE = math.radians(50.0)


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
    if hinge == 'TOP':
        # Lift-up: pivot at the TOP edge (a line parallel to +X at the
        # door top), the bottom swinging out into the room (-Y) and up.
        # The closed door stands with rot_x 90 spanning its height in
        # +Z; rotating that base by -angle about world X lifts the
        # bottom while the origin (bottom edge) moves so the top edge
        # stays put.
        h = door.get('hb_door_h', 0.0)
        ang = DOOR_OPEN_ANGLE * frac * swing
        # Bottom-origin offset from the top pivot is (0, 0, -h); rotate
        # it about X by -ang and re-anchor at the fixed top point.
        door.location = (cx,
                         cy - math.sin(ang) * h,
                         cz + h - math.cos(ang) * h)
        door.rotation_euler = (math.radians(90.0) - ang, 0.0, 0.0)
        return
    if hinge == 'BOTTOM':
        # Tilt-out hamper: pivot at the BOTTOM edge (the door origin),
        # the top swinging out into the room. The origin stays put; the
        # front just rotates about world X by the tilt angle.
        ang = HAMPER_TILT_ANGLE * frac * swing
        door.location = (cx, cy, cz)
        door.rotation_euler = (math.radians(90.0) + ang, 0.0, 0.0)
        return
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


def _stash_door_closed(door, cx, cy, cz, leaf, side, height=0.0):
    door['hb_door_cx'] = float(cx)
    door['hb_door_cy'] = float(cy)
    door['hb_door_cz'] = float(cz)
    door['hb_door_leaf'] = float(leaf)
    door['hb_door_side'] = side
    # Door height, needed to pivot a lift-up door about its top edge.
    door['hb_door_h'] = float(height)


def front_overlays(sp, scene_props, opening=None):
    """How far a front reaches over what it meets on each of its four
    sides, as (left, right, top, bottom).

    A half overlay splits what the front shares with its neighbour: the
    two meet over the middle of the panel or shelf between them and the
    gap is what shows, so each side covers half the thickness less half
    the gap. A side that is not a half overlay is held back from that
    edge by its reveal instead, leaving the edge showing - what a
    finished end or an exposed top wants. Left and right work off the
    panel thickness and the horizontal gap, top and bottom off the
    shelf thickness and the vertical gap.

    Hand in an opening to let it take over any side it has unlocked,
    the same way a face frame opening takes a side over from its
    cabinet. Worked out in plain arithmetic and written straight into
    the parts: there is nothing driven here, so a run redraws in one
    pass rather than waiting on a dependency graph.
    """
    st = scene_props.shelf_thickness
    pt = scene_props.panel_thickness
    lo = ((pt - sp.horizontal_gap) / 2.0 if sp.half_overlay_left
          else pt - sp.left_reveal)
    ro = ((pt - sp.horizontal_gap) / 2.0 if sp.half_overlay_right
          else pt - sp.right_reveal)
    to = ((st - sp.vertical_gap) / 2.0 if sp.half_overlay_top
          else st - sp.top_reveal)
    bo = ((st - sp.vertical_gap) / 2.0 if sp.half_overlay_bottom
          else st - sp.bottom_reveal)
    if opening is not None:
        op = opening.hb_closet_opening
        if op.unlock_left_overlay:
            lo = op.left_overlay
        if op.unlock_right_overlay:
            ro = op.right_overlay
        if op.unlock_top_overlay:
            to = op.top_overlay
        if op.unlock_bottom_overlay:
            bo = op.bottom_overlay
    return lo, ro, to, bo


def tray_height(tray, stack_h):
    """How tall one pull-out tray stands: the height it was given, or
    the height the stack sets when it is still sharing."""
    if not tray.get(PROP_UNLOCK_TRAY_HEIGHT, 0):
        return stack_h
    return max(float(tray.get(PROP_TRAY_HEIGHT, stack_h)),
               const.ROLLOUT_MIN_HEIGHT)


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


def current_open_frac(part):
    """How far one front is standing open right now, 0 closed .. 1 fully
    open. A front carries its own answer only once someone has clicked it
    in Open Door mode; until then it follows the Open Door / Open Drawer
    percentage set on the opening it fills, or on the bay when the front
    spans the whole bay."""
    key = ('hb_door_open' if part.get('hb_part_role') == PART_ROLE_DOOR
           else 'hb_drawer_open')
    own = part.get(key)
    if own is not None:
        return min(max(float(own), 0.0), 1.0)
    parent = part.parent
    if parent is None:
        return 0.0
    if parent.get(TAG_OPENING_CAGE):
        _op = parent.hb_closet_opening
        pct = _op.open_door if key == 'hb_door_open' else _op.open_drawer
    elif parent.get(TAG_BAY_CAGE):
        pct = parent.hb_closet_bay.open_door
    else:
        return 0.0
    return min(max(float(pct) / 100.0, 0.0), 1.0)


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
    per 12" of interior height (the prior library's default spacing),
    clamped to at least one."""
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


class _RunSizes:
    """The room's settings seen through one run's own.

    A run that has taken a part thickness over answers with its own
    figure; everything else falls straight through to the room. Built
    once at the top of a pass and handed down in place of the room, so
    every figure a pass reads is already the run's and nothing has to
    be kept in step. Read only - nothing writes back through it."""

    __slots__ = ('_room', '_own')

    def __init__(self, room, own):
        object.__setattr__(self, '_room', room)
        object.__setattr__(self, '_own', own)

    def __getattr__(self, name):
        own = object.__getattribute__(self, '_own')
        if name in own:
            return own[name]
        return getattr(object.__getattribute__(self, '_room'), name)


def run_sizes(obj, room=None):
    """The room's settings as the run holding `obj` sees them.

    Hands back the room itself when there is no run or the run has
    taken nothing over, which is the usual case, so reading a size
    through here costs nothing until someone sets an override."""
    room = room if room is not None else bpy.context.scene.hb_closets
    if obj is None:
        return room
    root = obj if obj.get(TAG_STARTER_CAGE) else find_starter_root(obj)
    if root is None:
        return room
    sp = root.hb_closet_starter
    own = {}
    for attr in const.RUN_THICKNESSES:
        if getattr(sp, 'unlock_' + attr, False):
            own[attr] = float(getattr(sp, attr))
    if not own:
        return room
    return _RunSizes(room, own)


def _wrap_starter(obj):
    """Wrap a starter root Object as its ClosetStarter subclass."""
    cls = WRAP_CLASS_REGISTRY.get(obj.get('CLASS_NAME', ''), ClosetStarter)
    instance = cls.__new__(cls)
    GeoNodeCage.__init__(instance, obj)
    return instance


# Opening settings used to live as loose custom properties on the
# opening cage, one key per setting. They live on a typed settings group
# now. A file saved before that change still carries the loose keys, so
# the first recalc after it opens moves them across and drops them. The
# move is one-way and self-clearing: once an opening has been carried
# over, the check below costs a handful of dictionary lookups and does
# nothing.
_OPENING_CARRIED_KEYS = (
    (PROP_ADJ_SHELF_QTY, 'adj_shelf_qty', int),
    (PROP_DRAWER_QTY, 'drawer_qty', int),
    (PROP_DRAWER_FRONT_HEIGHT, 'drawer_front_height', float),
    (PROP_DRAWER_BOX_OVERRIDE, 'drawer_box_override', str),
    (PROP_ROLLOUT_QTY, 'rollout_qty', int),
    (PROP_ROLLOUT_HEIGHT, 'rollout_height', float),
    (PROP_SLANT_QTY, 'slant_qty', int),
    (PROP_SLANT_SPACING, 'slant_spacing', float),
    (PROP_SLANT_ANGLE, 'slant_angle', float),
    (PROP_SLANT_COLOR, 'slant_color', str),
    (PROP_CUBBY_COLS, 'cubby_cols', int),
    (PROP_CUBBY_ROWS, 'cubby_rows', int),
    (PROP_CUBBY_SETBACK, 'cubby_setback', float),
    (PROP_DOOR_SWING, 'door_swing', str),
    (PROP_IS_HAMPER, 'is_hamper', bool),
)


def carry_over_bay_fronts(root):
    """Move a pre-typed-group bay-wide front onto the bay's settings
    group. One way and self-clearing, the same as the openings.

    The bay's fields relay the run out when they are written, and this
    runs from inside the recalc entry point, so the writes are made
    behind the reentrance guard - the solve that is already on its way
    picks them up."""
    stale = [bay for bay in root.children
             if bay.get(TAG_BAY_CAGE)
             and (PROP_BAY_DOOR_SWING in bay or PROP_BAY_IS_HAMPER in bay)]
    if not stale:
        return
    root_id = id(root)
    _RECALCULATING.add(root_id)
    try:
        for bay in stale:
            bp = bay.hb_closet_bay
            if PROP_BAY_DOOR_SWING in bay:
                try:
                    bp.door_swing = str(bay[PROP_BAY_DOOR_SWING])
                except (TypeError, ValueError):
                    pass  # unreadable leftover: the default stands
                del bay[PROP_BAY_DOOR_SWING]
            if PROP_BAY_IS_HAMPER in bay:
                try:
                    bp.is_hamper = bool(bay[PROP_BAY_IS_HAMPER])
                except (TypeError, ValueError):
                    pass
                del bay[PROP_BAY_IS_HAMPER]
    finally:
        _RECALCULATING.discard(root_id)


def carry_over_hampers(root):
    """Move a bay or an opening that was set to a tilt-out hamper with a
    flag of its own onto the front setting itself. One way and
    self-clearing, the same as the bay fronts above.

    A tilt-out hamper is one of the fronts a run can be given now rather
    than a flag hung beside them, so anything drawn before that reads
    its flag once and puts it back as the front it stood for."""
    stale = []
    for bay in root.children:
        if not bay.get(TAG_BAY_CAGE):
            continue
        if bay.hb_closet_bay.is_hamper:
            stale.append(bay.hb_closet_bay)
        for opening in bay.children:
            if (opening.get(TAG_OPENING_CAGE)
                    and opening.hb_closet_opening.is_hamper):
                stale.append(opening.hb_closet_opening)
    if not stale:
        return
    root_id = id(root)
    _RECALCULATING.add(root_id)
    try:
        for props in stale:
            # A flag with no front under it never stood for anything, so
            # it is dropped rather than made to hang one.
            if props.door_swing:
                props.door_swing = 'TILT_OUT'
            props.is_hamper = False
    finally:
        _RECALCULATING.discard(root_id)


def carry_over_front_locks(root):
    """Rename a drawer front's pinned-height flag on a run saved before
    the padlocks were made to read one way across the library.

    Nothing about the flag changed but its name - a set flag has always
    meant the user handed that front a height of its own. These are
    plain object idprops with no update callback behind them, so the
    writes cost no solve and the one already on its way reads them."""
    for obj in root.children_recursive:
        if OLD_PROP_FRONT_LOCKED not in obj:
            continue
        try:
            obj[PROP_UNLOCK_FRONT_HEIGHT] = (
                1 if obj[OLD_PROP_FRONT_LOCKED] else 0)
        except (TypeError, ValueError):
            pass  # unreadable leftover: the front goes back on the stack
        del obj[OLD_PROP_FRONT_LOCKED]


def carry_over_opening_settings(root):
    """Move any pre-typed-group opening settings onto the settings group.

    Values that fall outside a property's range are clamped by Blender on
    assignment rather than rejected, so a stale file cannot stop a
    starter from drawing."""
    openings = [o for bay in root.children if bay.get(TAG_BAY_CAGE)
                for o in bay.children if o.get(TAG_OPENING_CAGE)]
    for opening in openings:
        for key, name, cast in _OPENING_CARRIED_KEYS:
            if key not in opening:
                continue
            try:
                setattr(opening.hb_closet_opening, name, cast(opening[key]))
            except (TypeError, ValueError):
                pass  # unreadable leftover: the default stands
            del opening[key]


# Bay sizes used to be flagged the other way round, and the run carried
# a pair of locks of its own that held every bay at the run size. A file
# saved under those names keeps them as leftover keys; they are read
# once onto the unlock flags and then deleted.
_OLD_BAY_LOCK_KEYS = (
    ('width_locked', 'unlock_width'),
    ('height_locked', 'unlock_height'),
    ('depth_locked', 'unlock_depth'),
)
_OLD_RUN_LOCK_KEYS = (
    ('height_locked', 'unlock_height'),
    ('depth_locked', 'unlock_depth'),
)


def carry_over_lock_flags(root):
    """Bring a run saved under the old lock names forward.

    A bay flag carries straight across - it always meant what the unlock
    flag means, that the bay owns its own value. The run-wide locks are
    gone: a locked run held every bay at the run size whatever the bay
    itself said, so bays under one come forward following the run. Those
    run locks were on unless someone turned them off, so a key that was
    never written reads as on.

    A settings group holds its values under the property names, and a
    value written under a name the library has since dropped stays there
    as a leftover key. Reading and clearing go through the group itself
    for that reason - the key is not on the object, it is inside the
    group the object carries.
    """
    sp_data = root.hb_closet_starter
    sp_keys = set(sp_data.keys())
    stale_run = [old for old, _new in _OLD_RUN_LOCK_KEYS if old in sp_keys]
    stale_bay = []
    for bay in root.children:
        if not bay.get(TAG_BAY_CAGE):
            continue
        data = bay.hb_closet_bay
        keys = set(data.keys())
        if any(old in keys for old, _new in _OLD_BAY_LOCK_KEYS):
            stale_bay.append((data, keys))
    if not stale_run and not stale_bay:
        return
    run_held = {}
    for old, new in _OLD_RUN_LOCK_KEYS:
        try:
            run_held[new] = bool(sp_data.get(old, 1))
        except Exception:
            run_held[new] = True
    root_id = id(root)
    _RECALCULATING.add(root_id)
    try:
        for data, keys in stale_bay:
            for old, new in _OLD_BAY_LOCK_KEYS:
                if old not in keys:
                    continue
                try:
                    own = bool(data[old]) and not run_held.get(new, False)
                    setattr(data, new, own)
                except (TypeError, ValueError):
                    pass  # unreadable leftover: the default stands
                try:
                    del data[old]
                except (TypeError, KeyError):
                    pass
    finally:
        _RECALCULATING.discard(root_id)
    for old in stale_run:
        try:
            del sp_data[old]
        except (TypeError, KeyError):
            pass


def recalculate_closet_starter(obj):
    """Public recalc entry point for prop update callbacks and operators.
    Accepts the root or any descendant; no-ops while that starter is
    already mid-recalc, and defers to the end of the block while a
    suspend_recalc() batch is running."""
    root = find_starter_root(obj)
    if root is None:
        return
    if _RECALC_SUSPEND_DEPTH > 0:
        _PENDING_RECALC_NAMES.add(root.name)
        return
    if id(root) in _RECALCULATING:
        return
    carry_over_lock_flags(root)
    carry_over_opening_settings(root)
    carry_over_bay_fronts(root)
    carry_over_hampers(root)
    carry_over_front_locks(root)
    clear_hamper_shelves(root)
    _wrap_starter(root).recalculate()


def _in_str(value):
    """A metre figure in the inches the accessory is sold in, rounded
    the way a tape reads it."""
    return '%g"' % round(value / 0.0254, 2)


def accessory_band(cage, acc_def, width=0.0):
    """The width band this accessory was bought at.

    What the person chose is remembered on the cage. If the catalog
    has since stopped offering that width the nearest one stands in,
    so an older file still draws rather than coming up empty."""
    if not acc_def.bands:
        return None
    band = acc_def.band_by_model(cage.get(PROP_ACCESSORY_MODEL, ''))
    if band is None:
        band = acc_def.band_for_width(width or _cage_dim_x(cage))
    return band


def accessory_model_name(cage, acc_def):
    """What the drawing remembers this accessory being - the model's
    name, which means the same thing on any machine."""
    band = accessory_band(cage, acc_def)
    return band[2] if band else acc_def.model


def accessory_model_path_for(cage, acc_def):
    """Where that model is on this machine, or '' if it is not here."""
    band = accessory_band(cage, acc_def)
    return acc_def.path_for(band)


def _cage_dim_x(obj):
    """One cage's width, or 0 for anything that is not a cage."""
    try:
        return float(GeoNodeCage(obj).get_input('Dim X') or 0.0)
    except Exception:
        return 0.0


def add_accessory(opening, key):
    """Hang one accessory in an opening and hand back its cage.

    Only the choice is stored - what gets built under it, and whether
    a model shows up at all, is worked out on the next recalculation.
    That keeps a saved file honest when the companion add-on is
    installed, removed or updated underneath it."""
    from . import accessories_closets as acc
    acc_def = acc.get(key)
    if acc_def is None:
        return None
    cage = GeoNodeCage()
    cage.create(acc_def.label)
    # The closet is built with its back at y=0 and its front at
    # -depth, so the cage has to run that way too or the accessory is
    # drawn out through the wall.
    cage.set_input('Mirror Y', True)
    cage.obj.parent = opening
    cage.obj['hb_part_role'] = PART_ROLE_ACCESSORY
    cage.obj[PROP_ACCESSORY_KEY] = acc_def.key
    cage.obj[PROP_ACCESSORY_COLOR] = (acc_def.colors[0]
                                      if acc_def.colors else '')
    cage.obj[PROP_ACCESSORY_FABRIC] = (acc_def.fabrics[0]
                                       if acc_def.fabrics else '')
    cage.obj[PROP_ACCESSORY_Z] = 0.0
    # An accessory sold in widths arrives as the one nearest the
    # opening it was dropped in; the person can change it after.
    from . import accessories_closets as acc
    if acc_def.family == acc.FAMILY_PANEL:
        cage.obj[PROP_ACCESSORY_PANEL_LOC] = acc.PANEL_DEFAULT_LOCATION
        band = acc_def.bands[0] if acc_def.bands else None
    else:
        band = acc_def.band_for_width(_cage_dim_x(opening))
    if band is not None:
        cage.obj[PROP_ACCESSORY_MODEL] = band[2]
    cage.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    cage.obj['PROMPT_ID'] = 'hb_closets.accessory_prompts'
    return cage.obj


def clear_opening_contents(opening):
    """Strip one opening back to empty: put every insert setting back to
    its default (the regenerators remove their parts on the next recalc)
    and delete loose parts (rods). Splitting shelves are bay structure,
    not contents - clear_bay_contents handles those."""
    opening.hb_closet_opening.clear_contents()
    for child in list(opening.children):
        if child.get('hb_part_role') in (PART_ROLE_ROD,
                                         PART_ROLE_FIXED_SHELF,
                                         PART_ROLE_ACCESSORY):
            # rods carry hanger children; accessories carry their model
            # and any melamine cut for them
            _remove_part_tree(child)


def clear_bay_contents(bay_obj):
    """Strip a whole bay: every splitting shelf and division goes (the
    reconciler merges back to one opening per side), the bay-wide door
    config is cleared, and every opening's contents are cleared."""
    # property_unset puts a field back to its default without running
    # the update callback, so clearing the front here costs no solve of
    # its own; the caller recalculates once when the strip is done.
    bay_obj.hb_closet_bay.property_unset('door_swing')
    bay_obj.hb_closet_bay.property_unset('is_hamper')
    bay_obj.hb_closet_bay.property_unset('open_door')
    for child in list(bay_obj.children):
        if child.get('hb_part_role') in (PART_ROLE_FIXED_SHELF,
                                         PART_ROLE_DIVISION):
            # A shelf can carry a cleat of its own; that goes with the
            # shelf rather than being left standing on nothing.
            for sub in list(child.children):
                bpy.data.objects.remove(sub, do_unlink=True)
            bpy.data.objects.remove(child, do_unlink=True)
    for opening in [c for c in bay_obj.children if c.get(TAG_OPENING_CAGE)]:
        clear_opening_contents(opening)


# ---------------------------------------------------------------------------
# Copy / paste of bay & opening contents (a plain-dict clipboard so it
# survives object deletion and pastes onto any target).
# ---------------------------------------------------------------------------
def serialize_opening(opening):
    """Contents of one opening: its insert settings + loose rods (with
    their opening-local offsets)."""
    return {
        'adj': int(opening.hb_closet_opening.adj_shelf_qty),
        'drawer_qty': int(opening.hb_closet_opening.drawer_qty),
        'rollout_qty': int(opening.hb_closet_opening.rollout_qty),
        'rollout_h': float(opening.hb_closet_opening.rollout_height),
        'rollout_inset': int(
            bool(opening.hb_closet_opening.rollout_inset_front)),
        'rollout_ir': float(
            opening.hb_closet_opening.rollout_inset_reveal),
        'slant_qty': int(opening.hb_closet_opening.slant_qty),
        'slant_spacing': float(opening.hb_closet_opening.slant_spacing),
        'slant_angle': float(opening.hb_closet_opening.slant_angle),
        'slant_color': opening.hb_closet_opening.slant_color,
        'slant_fence_inset': float(
            opening.hb_closet_opening.slant_fence_inset),
        'slant_back_inset': float(
            opening.hb_closet_opening.slant_back_inset),
        'drawer_fh': float(opening.hb_closet_opening.drawer_front_height),
        'drawer_box': opening.hb_closet_opening.drawer_box_override,
        'drawer_stretcher_w': float(
            opening.hb_closet_opening.drawer_stretcher_width),
        # Per-drawer heights, bottom drawer first, with the flag saying
        # whether that drawer was holding the height or sharing.
        'drawer_fronts': [
            [float(c.get(PROP_FRONT_HEIGHT, 0.0)),
             int(bool(c.get(PROP_UNLOCK_FRONT_HEIGHT, 0)))]
            for c in sorted(
                (c for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_DRAWER_FRONT
                 and not c.get('hb_rollout')),
                key=lambda o: o.get('hb_drawer_index', 0))],
        'door_swing': opening.hb_closet_opening.door_swing,
        # How far the fronts here are drawn standing open, so a copy
        # reads the way the original did.
        'open_door': float(opening.hb_closet_opening.open_door),
        'open_drawer': float(opening.hb_closet_opening.open_drawer),
        'cubby_cols': int(opening.hb_closet_opening.cubby_cols),
        'cubby_rows': int(opening.hb_closet_opening.cubby_rows),
        'cubby_setback': float(opening.hb_closet_opening.cubby_setback),
        'rod_set_from_front':
            int(opening.hb_closet_opening.rod_set_from_front),
        'rod_from_front': float(opening.hb_closet_opening.rod_from_front),
        'rod_from_rear': float(opening.hb_closet_opening.rod_from_rear),
        'rod_deduct':
            float(opening.hb_closet_opening.rod_width_deduction),
        'remove_hangers': int(opening.hb_closet_opening.remove_hangers),
        # Any side of the front this opening took over from the run, so
        # a copied opening's front sits the way the original's did.
        'overlays': [
            [int(getattr(opening.hb_closet_opening, 'unlock_%s_overlay' % s)),
             float(getattr(opening.hb_closet_opening, '%s_overlay' % s))]
            for s in ('left', 'right', 'top', 'bottom')],
        # Which way the grain runs on the drawer fronts here, so a
        # copy reads the way the original did.
        'drawer_grain': opening.hb_closet_opening.drawer_grain,
        # How the shelves here are cut, so a copy drops into its
        # clips the way the original did.
        'shelf_gaps': [
            int(opening.hb_closet_opening.unlock_shelf_clip_gap),
            float(opening.hb_closet_opening.shelf_clip_gap),
            int(opening.hb_closet_opening.unlock_shelf_setback),
            float(opening.hb_closet_opening.shelf_setback)],
        # How this opening hardwares its fronts, so a copy is pulled
        # the way the original was.
        'pulls': [
            int(opening.hb_closet_opening.no_pulls),
            int(opening.hb_closet_opening.unlock_center_pull),
            int(opening.hb_closet_opening.center_pull_on_front),
            int(opening.hb_closet_opening.unlock_pull_location),
            float(opening.hb_closet_opening.drawer_pull_vertical_location),
            int(opening.hb_closet_opening.double_pull_on_front),
            float(opening.hb_closet_opening.distance_between_pulls),
            opening.hb_closet_opening.door_pull_location],
        # Whether this opening is closed at the back, and how, so a
        # copy is backed the way the original was.
        'back': [int(opening.hb_closet_opening.add_back),
                 float(opening.hb_closet_opening.back_inset),
                 int(opening.hb_closet_opening.back_notch_left),
                 int(opening.hb_closet_opening.back_notch_right),
                 float(opening.hb_closet_opening.back_notch_width),
                 float(opening.hb_closet_opening.back_notch_height)],
        'rods': [float(c.get('hb_z_offset', 0.0))
                 for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_ROD],
    }


def apply_opening_data(opening, data, recalc=True):
    """Rebuild an opening's contents from a serialize_opening() dict."""
    root = find_starter_root(opening)
    clear_opening_contents(opening)
    if data.get('adj'):
        opening.hb_closet_opening.adj_shelf_qty = data['adj']
    if data.get('drawer_qty'):
        opening.hb_closet_opening.drawer_qty = data['drawer_qty']
        opening.hb_closet_opening.drawer_front_height = data['drawer_fh']
        if data.get('drawer_box'):
            opening.hb_closet_opening.drawer_box_override = \
                data['drawer_box']
        opening.hb_closet_opening.drawer_stretcher_width = data.get(
            'drawer_stretcher_w', const.DRAWER_STRETCHER_WIDTH)
        # The fronts are not built yet, so the heights the copied bank
        # was holding wait on the opening for them.
        pins = data.get('drawer_fronts') or ()
        if pins:
            opening[PROP_PASTED_FRONT_PINS] = [
                float(v) for pair in pins for v in pair]
    if data.get('rollout_qty'):
        opening.hb_closet_opening.rollout_qty = data['rollout_qty']
        opening.hb_closet_opening.rollout_height = data.get('rollout_h',
                                                const.ROLLOUT_HEIGHT)
        opening.hb_closet_opening.rollout_inset_front = bool(
            data.get('rollout_inset', 0))
        opening.hb_closet_opening.rollout_inset_reveal = data.get(
            'rollout_ir', const.ROLLOUT_INSET_REVEAL)
    if data.get('slant_qty'):
        opening.hb_closet_opening.slant_qty = data['slant_qty']
        opening.hb_closet_opening.slant_spacing = data.get('slant_spacing',
                                               const.SLANT_SHELF_SPACING)
        opening.hb_closet_opening.slant_angle = data.get(
            'slant_angle', math.radians(const.SLANT_SHELF_ANGLE_DEG))
        if data.get('slant_color'):
            opening.hb_closet_opening.slant_color = data['slant_color']
        opening.hb_closet_opening.slant_fence_inset = data.get(
            'slant_fence_inset', const.SHOE_FENCE_INSET)
        opening.hb_closet_opening.slant_back_inset = data.get(
            'slant_back_inset', const.SHOE_FENCE_BACK_INSET)
    for s, pair in zip(('left', 'right', 'top', 'bottom'),
                       data.get('overlays') or ()):
        unlocked, value = pair
        if unlocked:
            setattr(opening.hb_closet_opening, '%s_overlay' % s,
                    float(value))
            setattr(opening.hb_closet_opening,
                    'unlock_%s_overlay' % s, True)
    dgrain = data.get('drawer_grain')
    if dgrain:
        opening.hb_closet_opening.drawer_grain = dgrain
    gaps = data.get('shelf_gaps')
    if gaps:
        _gp = opening.hb_closet_opening
        _gp.unlock_shelf_clip_gap = bool(gaps[0])
        _gp.shelf_clip_gap = gaps[1]
        _gp.unlock_shelf_setback = bool(gaps[2])
        _gp.shelf_setback = gaps[3]
    pulls = data.get('pulls')
    if pulls:
        _op = opening.hb_closet_opening
        _op.no_pulls = bool(pulls[0])
        _op.unlock_center_pull = bool(pulls[1])
        _op.center_pull_on_front = bool(pulls[2])
        _op.unlock_pull_location = bool(pulls[3])
        _op.drawer_pull_vertical_location = float(pulls[4])
        _op.double_pull_on_front = bool(pulls[5])
        _op.distance_between_pulls = float(pulls[6])
        # Copies taken before the door rule was a setting carry six.
        if len(pulls) > 7:
            _op.door_pull_location = str(pulls[7])
    if data.get('door_swing'):
        # A copy taken before the tilt-out hamper became a front of its
        # own carries the old flag, so it reads back as that front.
        opening.hb_closet_opening.door_swing = (
            'TILT_OUT' if data.get('is_hamper') else data['door_swing'])
    if data.get('cubby_cols', 1) > 1 or data.get('cubby_rows', 1) > 1:
        opening.hb_closet_opening.cubby_cols = data.get('cubby_cols', 1)
        opening.hb_closet_opening.cubby_rows = data.get('cubby_rows', 1)
        opening.hb_closet_opening.cubby_setback = data.get('cubby_setback',
                                               const.CUBBY_SETBACK)
    if data.get('rods'):
        op = opening.hb_closet_opening
        op.rod_set_from_front = bool(data.get('rod_set_from_front', 0))
        op.rod_from_front = data.get('rod_from_front', const.ROD_FROM_FRONT)
        op.rod_from_rear = data.get('rod_from_rear', const.ROD_FROM_REAR)
        op.rod_width_deduction = data.get('rod_deduct',
                                          const.ROD_WIDTH_DEDUCTION)
        op.remove_hangers = bool(data.get('remove_hangers', 0))
    back = data.get('back')
    if back and back[0]:
        _bk = opening.hb_closet_opening
        _bk.add_back = True
        _bk.back_inset = float(back[1])
        _bk.back_notch_left = bool(back[2])
        _bk.back_notch_right = bool(back[3])
        _bk.back_notch_width = float(back[4])
        _bk.back_notch_height = float(back[5])
    opening.hb_closet_opening.open_door = float(data.get('open_door', 0.0))
    opening.hb_closet_opening.open_drawer = float(
        data.get('open_drawer', 0.0))
    for z in data.get('rods', ()):
        add_rod(opening, z)
    if recalc and root is not None:
        recalculate_closet_starter(root)


def _front_openings(bay_obj):
    return sorted(
        [c for c in bay_obj.children
         if c.get(TAG_OPENING_CAGE)
         and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'],
        key=lambda o: (o.get('hb_opening_index', 0),
                       o.get('hb_col_index', 0)))


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
        'remove_shelf_cleat': bool(bp.remove_shelf_cleat),
        'bay_door_swing': bp.door_swing,
        'bay_open_door': float(bp.open_door),
        'shelves': list(shelves),
        # Which of those shelves carry a cleat of their own, held by the
        # same offsets so a paste puts one back under the same shelf.
        'shelf_cleats': sorted(
            c.get('hb_z_offset', 0.0) for c in bay_obj.children
            if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF
            and c.get('hb_shelf_cleat')
            and not c.get('hb_preview')
            and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'),
        # A division travels as the segment it is in and how far across
        # the bay it stands, which is what puts it back where it was in
        # a bay of the same width.
        'divisions': sorted(
            [int(c.get('hb_row', 0)), float(c.get('hb_x_offset', 0.0))]
            for c in bay_obj.children
            if c.get('hb_part_role') == PART_ROLE_DIVISION
            and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'),
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
    cleats = list(data.get('shelf_cleats', ()))
    for z in data.get('shelves', ()):
        add_fixed_shelf(front, z, cleat=z in cleats)
    recalculate_closet_starter(root)   # adopt shelves -> segments

    # Divisions go in against the segments the shelves have just made,
    # so they are put back one pass later than the shelves are.
    divisions = data.get('divisions', ())
    if divisions:
        segments = _front_openings(bay_obj)
        for row, x in divisions:
            target = next(
                (o for o in segments
                 if int(o.get('hb_opening_index', 0)) == int(row)), front)
            add_division(target, float(x))
        recalculate_closet_starter(root)   # adopt divisions -> columns

    # The construction flags each carry a solve of their own; holding
    # them means the openings and the flags land together on the one
    # solve at the end.
    with suspend_recalc():
        bp = bay_obj.hb_closet_bay
        bp.remove_bottom = data.get('remove_bottom', False)
        bp.remove_cleat = data.get('remove_cleat', False)
        bp.remove_shelf_cleat = data.get('remove_shelf_cleat', False)
        bp.open_door = float(data.get('bay_open_door', 0.0))
        if data.get('bay_door_swing'):
            bp.door_swing = ('TILT_OUT' if data.get('bay_is_hamper')
                             else data['bay_door_swing'])

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
    it. Callers skip this for a tilt-out hamper, whose basket stands
    in the whole opening; clear_hamper_shelves below takes the shelves
    back out of one whose front is changed to a hamper."""
    op = opening.hb_closet_opening
    # One column by one row is the empty state, not a cubby grid, so it
    # does not count as an interior.
    if (op.adj_shelf_qty or op.drawer_qty
            or op.cubby_cols > 1 or op.cubby_rows > 1):
        return
    for c in opening.children:
        if c.get('hb_part_role') == PART_ROLE_ROD:
            return
    opening.hb_closet_opening.adj_shelf_qty = default_adj_shelf_qty(opening)


def clear_hamper_shelves(root):
    """Take the adjustable shelves out of any opening whose front is a
    tilt-out hamper. The basket stands in the whole opening, so nothing
    fits behind it: an opening that was carrying shelves loses them the
    moment its front is changed to a hamper, whichever way the change
    was made. This runs from the recalc entry point so every route in -
    the opening's dropdown, the Add Doors menu, a bay-wide front, a run
    pasted or carried over - lands on the one rule.

    The count is cleared rather than ignored, so the opening reads back
    as the empty one it is drawn as."""
    stale = []
    for bay in root.children:
        if not bay.get(TAG_BAY_CAGE):
            continue
        bay_swing = bay.hb_closet_bay.door_swing
        for opening in bay.children:
            if not opening.get(TAG_OPENING_CAGE):
                continue
            op = opening.hb_closet_opening
            if not op.adj_shelf_qty:
                continue
            swing = op.door_swing
            # A bay-wide front spans the openings on the front side of
            # the bay, so that is the front they stand behind.
            if not swing and opening.get(
                    PROP_OPENING_SIDE, 'FRONT') == 'FRONT':
                swing = bay_swing
            if swing == 'TILT_OUT':
                stale.append(op)
    # Nothing here has an update callback behind it, so the writes cost
    # no solve of their own - the recalc they run inside picks them up.
    for op in stale:
        op.adj_shelf_qty = 0


# What each interior writes on an opening, and what an empty one of it
# reads back as. One opening holds one interior - the opening dialog's
# fill list has always worked that way - so the list lives here and the
# individual insert commands land on the same rule.
INTERIOR_FIELDS = {
    'ADJ_SHELVES': {'adj_shelf_qty': 0},
    'DRAWERS': {'drawer_qty': 0},
    'ROLLOUTS': {'rollout_qty': 0},
    'SLANTED_SHELVES': {'slant_qty': 0},
    'CUBBIES': {'cubby_cols': 1, 'cubby_rows': 1},
}


def clear_other_interiors(opening, keep):
    """Empty every interior but `keep` out of an opening.

    Called straight after an insert command has written its own
    settings, so asking for cubbies in an opening that is holding shoe
    shelves replaces them rather than building both in the one space.
    A quantity of nothing is a removal rather than a choice, so an
    interior that was emptied leaves the rest of the opening alone."""
    fields = INTERIOR_FIELDS.get(keep)
    if not fields:
        return
    op = opening.hb_closet_opening
    if all(getattr(op, n) == empty for n, empty in fields.items()):
        return
    for kind, others in INTERIOR_FIELDS.items():
        if kind == keep:
            continue
        for name, empty in others.items():
            if getattr(op, name) != empty:
                setattr(op, name, empty)


def segment_columns(opening):
    """How many columns the segment this opening stands in is divided
    into - 1 when the opening is a whole segment.

    A shelf runs the width of the bay, so a command that caps part of
    an opening with one has to know whether the opening is a column of
    a divided segment: capping the column would cut the columns beside
    it in two as well."""
    bay = find_bay_cage(opening)
    if bay is None:
        return 1
    side = opening.get(PROP_OPENING_SIDE, 'FRONT')
    row = int(opening.get('hb_opening_index', 0))
    return len([c for c in bay.children
                if c.get(TAG_OPENING_CAGE)
                and c.get(PROP_OPENING_SIDE, 'FRONT') == side
                and int(c.get('hb_opening_index', 0)) == row]) or 1


def _cfg_rod(opening):
    add_rod(opening, const.ROD_TOP_OFFSET)


def _cfg_doors(opening):
    opening.hb_closet_opening.door_swing = 'DOUBLE'
    seed_door_shelves(opening)


def _cfg_hamper(opening):
    # No shelves behind a tilt-out - the basket takes the opening.
    opening.hb_closet_opening.door_swing = 'TILT_OUT'


def apply_bay_config(bay_obj, config):
    """Clear the bay and build one of the standard configurations."""
    root = find_starter_root(bay_obj)
    if root is None:
        return False
    scene_props = run_sizes(root)
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
        return qty * (dh + root.hb_closet_starter.vertical_gap) - st

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
    # Which split, if any, carries a cleat behind it.
    cleat_at = None
    bay_door = None           # FULL_HEIGHT_DOORS -> bay-wide double door
    if config == 'ADJ_SHELVES':
        opening.hb_closet_opening.adj_shelf_qty = max(
            1, min(8, int(ih / inch(12.0))))
    elif config == 'DOUBLE_HANG':
        splits = [ih / 2.0]
        actions = [(0, _cfg_rod), (1, _cfg_rod)]
    elif config == 'DH_TOP_SHELF':
        # A shelf near the top leaves a storage opening above the two
        # hangs, which split what is left of the bay between them.
        hang_top = max(inch(2.0),
                       ih - const.TOP_SHELF_OPENING_HEIGHT - st)
        splits = [hang_top / 2.0, hang_top]
        actions = [(0, _cfg_rod), (1, _cfg_rod)]
    elif config == 'DH_MID_SHELF':
        # Two hangs with a storage band between them. The upper hang is
        # measured down from the top of the bay and the band hangs
        # under it, so the lower hang takes whatever is left.
        top = min(ih - const.MID_SHELF_OPENING_HEIGHT - st,
                  ih - st - inch(1.0))
        low = max(inch(1.0), top - const.MID_SHELF_BAND_HEIGHT)
        if top - low < st + inch(1.0):
            top = low + st + inch(1.0)
        splits = [low, top]
        # The shelf under the upper hang takes a cleat behind it, the
        # way the prior library built this configuration.
        cleat_at = top
        actions = [(0, _cfg_rod), (2, _cfg_rod)]
    elif drawer_qty is not None:
        qty = drawer_qty

        def _cfg_drawers(op, q=qty, h=dh):
            op.hb_closet_opening.drawer_qty = q
            op.hb_closet_opening.drawer_front_height = h

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
        add_fixed_shelf(opening, z, cleat=(z == cleat_at))
    recalculate_closet_starter(root)   # adopt splits -> segments

    openings = sorted(
        [c for c in bay_obj.children
         if c.get(TAG_OPENING_CAGE)
         and c.get(PROP_OPENING_SIDE, 'FRONT') == 'FRONT'],
        key=lambda o: o.get('hb_opening_index', 0))
    for idx, fn in actions:
        if idx < len(openings) and fn is not None:
            fn(openings[idx])
    # The bay-wide front relays the run out on its own, so the front and
    # the shelves behind it land together on the one solve at the end.
    with suspend_recalc():
        if bay_door:
            bp = bay_obj.hb_closet_bay
            bp.door_swing = bay_door
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
     ('DOOR_DOUBLE', "Double Door"),
     ('DOOR_LIFT_UP', "Lift Up Door"),
     ('DOOR_TILT_OUT', "Tilt Out Hamper")],
    [('DRAWERS_1', "1 Drawer"), ('DRAWERS_2', "2 Drawer"),
     ('DRAWERS_3', "3 Drawer"), ('DRAWERS_4', "4 Drawer"),
     ('DRAWERS_5', "5 Drawer"), ('DRAWERS_6', "6 Drawer"),
     ('DRAWERS_7', "7 Drawer"), ('DRAWERS_8', "8 Drawer")],
    [('CUBBIES', "Cubbies"),
     ('ROLLOUTS', "Rollout Trays")],
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
        opening.hb_closet_opening.adj_shelf_qty = \
            default_adj_shelf_qty(opening)
    elif config == 'DOOR_LEFT':
        opening.hb_closet_opening.door_swing = 'LEFT'
        seed_door_shelves(opening)
    elif config == 'DOOR_RIGHT':
        opening.hb_closet_opening.door_swing = 'RIGHT'
        seed_door_shelves(opening)
    elif config == 'DOOR_DOUBLE':
        opening.hb_closet_opening.door_swing = 'DOUBLE'
        seed_door_shelves(opening)
    elif config == 'DOOR_LIFT_UP':
        opening.hb_closet_opening.door_swing = 'LIFT_UP'
        seed_door_shelves(opening)
    elif config == 'DOOR_TILT_OUT':
        # No shelves behind a tilt-out - the basket takes the opening.
        opening.hb_closet_opening.door_swing = 'TILT_OUT'
    elif config == 'CUBBIES':
        opening.hb_closet_opening.cubby_cols = 3
        opening.hb_closet_opening.cubby_rows = 3
    elif config == 'ROLLOUTS':
        opening.hb_closet_opening.rollout_qty = const.ROLLOUT_DEFAULT_QTY
        opening.hb_closet_opening.rollout_height = const.ROLLOUT_HEIGHT
    elif config.startswith('DRAWERS_'):
        try:
            opening.hb_closet_opening.drawer_qty = int(config.split('_')[1])
            opening.hb_closet_opening.drawer_front_height = \
                const.DRAWER_FRONT_HEIGHT
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
