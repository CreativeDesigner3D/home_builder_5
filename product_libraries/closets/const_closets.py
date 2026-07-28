"""Closet library constants.

Values ported from the legacy closet system so dealers migrating projects
see the same defaults. Heights are defined in millimeters (32mm-system
panel drilling heights); everything else is inches.
"""
from ...units import inch, millimeter


# ---------------------------------------------------------------------------
# Material thicknesses
# ---------------------------------------------------------------------------
PANEL_THICKNESS = inch(0.75)
SHELF_THICKNESS = inch(0.75)
COUNTERTOP_THICKNESS = inch(1.125)
APPLIED_BACK_THICKNESS = inch(0.75)
# How far an applied back laps onto the panels and shelves around the
# bay it closes.
APPLIED_BACK_OVERLAY = inch(0.3125)
CLEAT_WIDTH = inch(4.0)
# End-panel batten: a cosmetic scribe strip against the
# inner face of an end panel at the front edge.
BATTEN_WIDTH = inch(1.125)
BATTEN_THICKNESS = inch(0.25)
# Wall hang rail (the strip the closet hangs from / anchors to). Legacy
# profile: 1.125 in tall x 0.25 in thick, rail bottom 3.3125 in below
# the section top.
HANG_RAIL_WIDTH = inch(1.125)
HANG_RAIL_THICKNESS = inch(0.25)
HANG_RAIL_DROP = inch(3.3125)

# ---------------------------------------------------------------------------
# Starter defaults
# ---------------------------------------------------------------------------
DEFAULT_WIDTH = inch(80.0)
DEFAULT_BAY_QTY = 4
DEFAULT_DEPTH = inch(14.0)

# Panel heights by starter type. The mm values are legacy 32mm-system
# heights: Base 819mm = 32.25", Tall 2131mm = 83.94", Hanging 1267mm = 49.88".
BASE_PANEL_HEIGHT = millimeter(819)
TALL_PANEL_HEIGHT = millimeter(2131)
HANGING_PANEL_HEIGHT = millimeter(1267)

# Floor to TOP of a hanging (wall-mounted) unit. Chosen so a hanging
# section top-aligns with an adjacent tall tower (tall panel height).
HANGING_TOP_HEIGHT = millimeter(2131)


def inch_label(mm_value):
    """Readable inch-fraction label for a millimeter size ('32 1/4"')."""
    sixteenths = int(round(mm_value / 25.4 * 16.0))
    whole, rem = divmod(sixteenths, 16)
    if rem == 0:
        return '%d"' % whole
    num, den = rem, 16
    while num % 2 == 0:
        num //= 2
        den //= 2
    if whole:
        return '%d %d/%d"' % (whole, num, den)
    return '%d/%d"' % (num, den)


# Standard panel / section heights: the full 32mm-system lattice the
# prior library offered, 83mm through 3027mm in 32mm steps. The mm
# string is the identifier, so a height picked here is the same height
# the prior library produced.
PANEL_HEIGHT_MIN_MM = 83
PANEL_HEIGHT_MAX_MM = 3027
PANEL_HEIGHT_ITEMS = [
    (str(v), inch_label(v), inch_label(v))
    for v in range(PANEL_HEIGHT_MIN_MM, PANEL_HEIGHT_MAX_MM + 1, 32)
]


def nearest_panel_height_key(value):
    """Closest PANEL_HEIGHT_ITEMS identifier for a distance, or '' when
    the distance is off the lattice by more than half a step."""
    mm = value / millimeter(1.0)
    n = int(round((mm - PANEL_HEIGHT_MIN_MM) / 32.0))
    n = min(max(n, 0), (PANEL_HEIGHT_MAX_MM - PANEL_HEIGHT_MIN_MM) // 32)
    snapped = PANEL_HEIGHT_MIN_MM + n * 32
    return str(snapped) if abs(snapped - mm) <= 0.5 else ''

# ---------------------------------------------------------------------------
# Toe kick
# ---------------------------------------------------------------------------
DEFAULT_TOE_KICK_HEIGHT = millimeter(96)   # 3.78"
DEFAULT_TOE_KICK_SETBACK = inch(1.625)

# Standard kick-height choices (mm string, label) for the kick-height
# dropdown in the starter prompts. Custom is offered alongside these.
KICK_HEIGHT_ITEMS = [
    ('64', '2 1/2"', '2 1/2"'),
    ('96', '3 3/4"', '3 3/4"'),
    ('128', '5"', '5"'),
    ('160', '6 1/4"', '6 1/4"'),
    ('192', '7 1/2"', '7 1/2"'),
    ('224', '8 3/4"', '8 3/4"'),
    ('256', '10"', '10"'),
    ('288', '11 1/4"', '11 1/4"'),
    ('320', '12 1/2"', '12 1/2"'),
]

# ---------------------------------------------------------------------------
# Countertop (Base and Island starters)
# ---------------------------------------------------------------------------
COUNTERTOP_OVERHANG_FRONT = inch(1.875)
# Backsplash: an upstand along the wall edge of a countertop.
BACKSPLASH_HEIGHT = inch(4.0)
BACKSPLASH_THICKNESS = inch(0.75)
# Radius applied to a countertop's finished (exposed) end corners when
# the radius option is on.
COUNTERTOP_END_RADIUS = inch(1.5)

# Amount an end panel grows past the section top when it is extended to
# wrap a countertop.
EXTEND_PANEL_AMOUNT = inch(1.125)

# Bridge shelves spanning the gap to a corner neighbor.
BRIDGE_SHELF_WIDTH = inch(14.0)

# Top accent shelf: a decorative shelf laid on top of the run, projecting
# forward (and past finished ends) by the overhang. Default 1".
TOP_ACCENT_OVERHANG = inch(1.0)

# Minimum bay width the redistributor will assign to an unlocked bay.
MIN_BAY_WIDTH = inch(1.0)

# Automatic pull-off from a bare wall corner at placement, so the
# closet clears the return wall. A typed placement offset replaces it.
CORNER_PULL_OFF = inch(0.5)

# Island placement: standard aisle widths the clearance snap detents
# to, the engage window around each, and how far a clearance ray
# searches before a side reads as open.
AISLE_DETENTS = (inch(30.0), inch(36.0), inch(42.0), inch(48.0))
AISLE_SNAP_ENGAGE = inch(1.0)
CLEARANCE_MAX_REACH = inch(240.0)

# ---------------------------------------------------------------------------
# Interior parts
# ---------------------------------------------------------------------------
ROD_RADIUS = inch(1.0)
ROD_CUP_DEPTH = inch(0.2)
ROD_CUP_DEPTH_2 = inch(0.8)
# Hang-rod centerline distance from the rear (wall side) of the opening.
ROD_FROM_REAR = inch(12.0)
# Fronts (doors / drawer fronts / hampers). Half-overlay convention from
# the legacy closet system: each front overlays a shared panel/shelf by
# (thickness - gap) / 2 so neighboring fronts split the reveal.
FRONT_THICKNESS = inch(0.75)
DOOR_TO_CABINET_GAP = inch(0.125)   # front face held off the carcass
FRONT_GAP = inch(0.125)             # gap between adjacent fronts
DRAWER_FRONT_HEIGHT = inch(7.5)
# Minimum height the redistributor will assign to an unlocked drawer front
# when the stack fills its opening (mirrors MIN_BAY_WIDTH for widths).
MIN_DRAWER_FRONT = inch(2.0)
DRAWER_SLIDE_GAP = inch(0.5)        # per side, drawer box to panel
DRAWER_BOX_HEIGHT_DEDUCT = inch(1.25)
DRAWER_BOX_DEPTH_DEDUCT = inch(0.5)
DRAWER_BOX_Z_LIFT = inch(0.5)       # box bottom above front bottom edge
# Double-sided island
ISLAND_DOUBLE_DEPTH = inch(30.0)
ISLAND_CTOP_OVERHANG = inch(1.5)    # legacy islands overhang all sides
# L Shelves (inside-corner units)
L_SHELF_SIZE = inch(24.0)           # corner footprint each way
L_SHELF_QTY = 3                     # interior L shelves between top/bottom
L_BACK_STRIP_WIDTH = inch(6.0)      # back partition width at the corner
# Corner construction: shelves and the back partition are held
# off the walls by the wall offset; the shelves' partition notch clears
# the partition by the router tool radius.
L_WALL_OFFSET = inch(0.5)
L_NOTCH_TOOL_RADIUS = inch(0.25)
# Default distance from the opening TOP to a hang rod's center when the
# rod is added from the menu (modal placement types an exact height).
ROD_TOP_OFFSET = inch(2.5)
ADJ_SHELF_DEFAULT_QTY = 3
# Pullout trays (rollouts): drawer boxes with no fronts, spaced in an
# opening. Each tray stands ROLLOUT_HEIGHT tall (default 4"); the side
# clearance for the slides is ROLLOUT_SLIDE_GAP per side.
ROLLOUT_DEFAULT_QTY = 3
ROLLOUT_HEIGHT = inch(4.0)
ROLLOUT_SLIDE_GAP = inch(0.327)
# Smallest gap left between stacked trays / above and below the stack.
ROLLOUT_MIN_GAP = inch(1.0)
# Cubbies: a grid of divisions and shelves filling an opening. Both are
# held back from the front edge by the setback.
CUBBY_SETBACK = inch(0.25)
# Slanted shoe shelves: angled shelves stacked bottom-up, each with a
# metal shoe fence across the front. Sizes ported from the prior library.
SLANT_SHELF_DEFAULT_QTY = 4
SLANT_SHELF_SPACING = inch(8.0)       # Distance Between Shelves
SLANT_SHELF_ANGLE_DEG = 17.25         # Shelf Angle (degrees)
SLANT_SHELF_SETBACK = inch(0.125)     # front setback with the metal fence
SHOE_FENCE_INSET = millimeter(19.0)   # fence inset from each side
SHOE_FENCE_DEPTH = inch(0.5)          # fence front-to-back size
SHOE_FENCE_HEIGHT = inch(1.5)         # fence height above the shelf
# Modal add-part height snapping increment (legacy fallback; the 32mm
# system lattice below is what placement actually snaps to).
PART_Z_SNAP = inch(0.25)

# ---------------------------------------------------------------------------
# 32mm system. Panel/bay heights increment on a 32mm lattice with a 19mm
# base (819 / 1267 / 2131mm - the Base / Hanging / Tall defaults - all
# sit on it). Shelf and rod locations land on system holes: a 12.95mm
# base + n*32mm from the interior bottom (the legacy opening-height
# enum steps on exactly this lattice).
# ---------------------------------------------------------------------------
SYSTEM_PITCH = millimeter(32.0)
SYSTEM_HEIGHT_BASE = millimeter(19.0)
SYSTEM_HOLE_BASE = millimeter(12.95)


def snap_system_height(value):
    """Nearest 32mm-system panel/bay height (19 + n*32 mm)."""
    n = round((value - SYSTEM_HEIGHT_BASE) / SYSTEM_PITCH)
    return SYSTEM_HEIGHT_BASE + max(0, int(n)) * SYSTEM_PITCH


def snap_system_hole(value):
    """Nearest system hole (12.95 + n*32 mm from the interior bottom)."""
    n = round((value - SYSTEM_HOLE_BASE) / SYSTEM_PITCH)
    return SYSTEM_HOLE_BASE + max(0, int(n)) * SYSTEM_PITCH
