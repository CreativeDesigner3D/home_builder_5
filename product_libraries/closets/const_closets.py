"""Closet library constants.

Values ported from the prior closet library so dealers migrating projects
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
# A captured back is held inside one opening, between the panels and
# shelves around it, instead of being applied across the outside of the
# bay. It is cut from the run's shelf thickness, so it has no thickness
# of its own. Both corner reliefs are optional and sized the way the
# prior library sized them: 3" down the side, 1-1/2" in from it.
CAPTURED_BACK_NOTCH_WIDTH = inch(1.5)
CAPTURED_BACK_NOTCH_HEIGHT = inch(3.0)
CLEAT_WIDTH = inch(4.0)
# End-panel batten: a cosmetic scribe strip against the
# inner face of an end panel at the front edge.
BATTEN_WIDTH = inch(1.125)
BATTEN_THICKNESS = inch(0.25)
# What the uprights in a cubby grid are cut from. Kept apart from the
# shelf thickness because the prior library carried its own figure for
# it, so a grid can be divided in something other than what its
# shelves are made of.
DIVIDER_THICKNESS = inch(0.75)
# The part thicknesses a run can take over from the room. The room and
# the starter carry the same field names, which is what lets a run be
# read through the room's settings without anything downstream having
# to know which figures were taken over.
RUN_THICKNESSES = (
    'panel_thickness',
    'shelf_thickness',
    'divider_thickness',
    'batten_thickness',
    'batten_width',
)
# Wall hang rail (the strip the closet hangs from / anchors to). The
# prior library's profile: 1.125 in tall x 0.25 in thick, rail bottom
# 3.3125 in below the section top.
HANG_RAIL_WIDTH = inch(1.125)
HANG_RAIL_THICKNESS = inch(0.25)
HANG_RAIL_DROP = inch(3.3125)
# The cover clipped over a rail end where it lands on a panel. It is
# bought rather than cut, so it wears a material of its own and is
# counted with the hardware. The prior library's block: 0.5 in along
# the rail, 1.75 in tall, 2.25 in out from the wall, its top an inch
# below the underside of the shelf the rail drops from.
HANG_RAIL_COVER_LENGTH = inch(0.5)
HANG_RAIL_COVER_WIDTH = inch(1.75)
HANG_RAIL_COVER_DEPTH = inch(2.25)
HANG_RAIL_COVER_TOP_OFFSET = inch(1.0)
# The cover stands clear of the wall rather than against it. What
# it wraps is the claw, which hangs off the front of the rail, so
# it starts an inch out from the wall and reaches back into the
# room from there - the rail itself is left alone behind it.
HANG_RAIL_COVER_STANDOFF = inch(1.0)

# ---------------------------------------------------------------------------
# Starter defaults
# ---------------------------------------------------------------------------
DEFAULT_WIDTH = inch(80.0)
DEFAULT_BAY_QTY = 4
DEFAULT_DEPTH = inch(14.0)

# Automatic bay count while a run is being dragged out. The run is split
# into the fewest bays that keep every bay at or under the target width.
# A starter carries at most MAX_BAY_QTY openings, so that is the hard
# ceiling on the count however wide the run gets.
BAY_WIDTH_TARGET = inch(30.0)
MIN_BAY_QTY = 1
MAX_BAY_QTY = 9

# Panel heights by starter type. The mm values are the 32mm-system
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

# Standard opening heights: the 32mm ladder the prior library offered
# for the opening above a hanging rod, 12.95mm through 1932.95mm in
# 32mm steps. The mm string is the identifier, so a height picked here
# is the same height the prior library produced.
OPENING_HEIGHT_MIN_MM = 12.95
OPENING_HEIGHT_COUNT = 61
OPENING_HEIGHT_ITEMS = [
    ('%.2f' % (OPENING_HEIGHT_MIN_MM + i * 32),
     inch_label(OPENING_HEIGHT_MIN_MM + i * 32),
     inch_label(OPENING_HEIGHT_MIN_MM + i * 32))
    for i in range(OPENING_HEIGHT_COUNT)
]
TOP_OPENING_HEIGHT_KEY = '716.95'   # the height the dropdown opens on

def opening_height(key):
    """Distance for an OPENING_HEIGHT_ITEMS identifier, which is the
    opening's height in millimeters."""
    try:
        return millimeter(float(key))
    except (TypeError, ValueError):
        return millimeter(float(TOP_OPENING_HEIGHT_KEY))

def nearest_opening_height_key(value):
    """Closest OPENING_HEIGHT_ITEMS identifier for a distance, or ''
    when the distance is off the ladder by more than half a step - an
    opening left somewhere of its own by a shelf dragged by hand."""
    mm = value / millimeter(1.0)
    n = int(round((mm - OPENING_HEIGHT_MIN_MM) / 32.0))
    n = min(max(n, 0), OPENING_HEIGHT_COUNT - 1)
    snapped = OPENING_HEIGHT_MIN_MM + n * 32
    return ('%.2f' % snapped) if abs(snapped - mm) <= 0.5 else ''

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

# Continuous top: one top laid across a whole run rather than the
# piece per bay a run works out for itself. It reaches past the
# front of what it caps, and a top longer than can be cut from one
# length of material comes in two pieces meeting at the cut length.
CONTINUOUS_TOP_PROJECTION = inch(1.0)
CONTINUOUS_TOP_MAX_LENGTH = inch(95.0)

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
# Hang-rod centerline distance from the rear (wall side) of the opening,
# and the same distance measured from the front edge for an opening set
# to read that way round.
ROD_FROM_REAR = inch(12.0)
ROD_FROM_FRONT = inch(2.0)
# How much shorter than its opening a rod is cut so it drops into the
# cups at each end.
ROD_WIDTH_DEDUCTION = inch(0.25)
# Double hang: the room the upper hang takes, in every one of the
# double-hang configurations. 40 3/4" on the standard ladder of opening
# heights (1036.95 mm), which is where a double hang is set out.
DOUBLE_HANG_TOP_OPENING = inch(40.8248)
# The shallow storage opening a top shelf leaves over the two hangs.
# A mid shelf needs no figure of its own: it sits where the upper
# hang's room finishes.
TOP_SHELF_OPENING_HEIGHT = inch(10.5866)
# Fronts (doors / drawer fronts / hampers). Half-overlay convention from
# the prior closet library: each front overlays a shared panel/shelf by
# (thickness - gap) / 2 so neighboring fronts split the reveal.
FRONT_THICKNESS = inch(0.75)
DOOR_TO_CABINET_GAP = inch(0.125)   # front face held off the carcass
FRONT_GAP = inch(0.125)             # gap between adjacent fronts

# How a front sits against what is around it, as the prior library had
# it. A half overlay splits what the front shares with its neighbour, so
# the two meet over the middle of the panel or shelf between them with
# the gap showing; a side that is not a half overlay is held back from
# that edge by its reveal instead, leaving the edge showing. The bottom
# comes in at nothing, so a bank of drawers finishes flush underneath.
VERTICAL_GAP = inch(0.125)          # between a front and the one above
HORIZONTAL_GAP = inch(0.125)        # between a front and the one beside
TOP_REVEAL = inch(0.0625)
BOTTOM_REVEAL = inch(0.0)
LEFT_REVEAL = inch(0.0625)
RIGHT_REVEAL = inch(0.0625)
# What a half overlay works out to on stock of the usual thickness. Only
# a starting value for a side an opening takes over for itself; the run
# works its own out from the thicknesses actually in use.
DEFAULT_OVERLAY = (FRONT_THICKNESS - FRONT_GAP) / 2.0

# Where a pull sits on a drawer front, and how far apart a pair of them
# is set when one front carries two. The drawer figure is measured from
# the top of the front down to the MIDDLE of the pull, where the door
# figures above are measured to the pull's edge. That is how the prior
# library had them and what gets measured on the floor, so it is kept.
DRAWER_PULL_VERTICAL_LOCATION = inch(1.5)
DISTANCE_BETWEEN_PULLS = inch(6.0)
# Where a door's pull sits on it. Three conventions, each measured from
# somewhere different: Base holds the pull down from the top edge of the
# door, Upper holds it up from the bottom edge, and Tall holds it at a
# height off the floor whatever the door is doing. Auto reads the door's
# own place in the run and picks the one that suits it, which is what an
# opening starts on; naming one holds the door to it.
DOOR_PULL_LOCATION_ITEMS = [
    ('AUTO', "Auto",
     "Pick the convention from where the door sits in the run"),
    ('BASE', "Base", "Hold the pull down from the top edge of the door"),
    ('TALL', "Tall", "Hold the pull at the tall height off the floor"),
    ('UPPER', "Upper",
     "Hold the pull up from the bottom edge of the door"),
]
DRAWER_FRONT_HEIGHT = millimeter(156.82)   # 6 1/4" front
# Minimum height the redistributor will assign to an unlocked drawer front
# when the stack fills its opening (mirrors MIN_BAY_WIDTH for widths).
MIN_DRAWER_FRONT = inch(2.0)
DRAWER_BOX_HEIGHT_DEDUCT = inch(1.25)
DRAWER_BOX_DEPTH_DEDUCT = inch(0.875)  # wood box, back of opening
# How far back from the face the stretcher between one drawer and
# the next runs. The prior library's figure.
DRAWER_STRETCHER_WIDTH = inch(6.0)

# Standard drawer front heights: the 32mm ladder the prior closet
# library ordered fronts from, 124.82mm and a 32mm step from there.
# The identifier is the front's cut height in millimeters, the name is
# the size the front is called by, and the description is the clear
# opening a front that size covers - a front stands taller than its
# opening because it half-overlays the shelf above and below it.
DRAWER_FRONT_HEIGHT_ITEMS = [
    ('124.82', '5"', 'Front over a 4 1/4" opening'),
    ('156.82', '6 1/4"', 'Front over a 5 1/2" opening'),
    ('188.82', '7 1/2"', 'Front over a 6 1/2" opening'),
    ('220.82', '8 3/4"', 'Front over an 8" opening'),
    ('252.82', '10"', 'Front over a 9 1/3" opening'),
    ('284.82', '11 1/4"', 'Front over a 10 1/2" opening'),
    ('316.82', '12 1/2"', 'Front over an 11 3/4" opening'),
    ('348.82', '13 3/4"', 'Front over a 13 1/8" opening'),
]
DRAWER_FRONT_HEIGHT_KEY = '156.82'   # the size a bank comes in at


def drawer_front_height(key):
    """Distance for a DRAWER_FRONT_HEIGHT_ITEMS identifier, which is
    the front's cut height in millimeters."""
    try:
        return millimeter(float(key))
    except (TypeError, ValueError):
        return DRAWER_FRONT_HEIGHT


def nearest_drawer_front_height(value):
    """Closest standard front height identifier for a distance, so a
    drawer sized by hand reads back as the size it landed nearest."""
    return min(DRAWER_FRONT_HEIGHT_ITEMS,
               key=lambda it: abs(drawer_front_height(it[0]) - value))[0]
# Double-sided island
ISLAND_DOUBLE_DEPTH = inch(30.0)
ISLAND_CTOP_OVERHANG = inch(1.5)    # island tops overhang all sides
# L Shelves (inside-corner units)
L_SHELF_SIZE = inch(24.0)           # corner footprint each way
L_SHELF_QTY = 3                     # interior L shelves between top/bottom
L_BACK_STRIP_WIDTH = inch(6.0)      # back partition width at the corner
# Corner construction: shelves and the back partition are held
# off the walls by the wall offset; the shelves' partition notch clears
# the partition by the router tool radius.
# A corner unit's rod runs along one wing rather than turning the
# corner - which is what the prior library did, and what the hardware
# allows. It stands this far off the wall it does not run along, and
# clear of the one it does.
# The parts worth spotting across a room read orange in the viewport:
# a shelf that is fixed rather than on clips, the way the prior library
# marked its lock shelves, so a stack says at a glance which of them is
# holding the unit square - and a panel that finishes an end, so a run
# says where its finished ends are without a prompt being opened to
# ask.
LOCK_SHELF_COLOR = (1.0, 0.7, 0.5, 1.0)
# The colour everything else takes.
PLAIN_PART_COLOR = (1.0, 1.0, 1.0, 1.0)

# The filler that closes an inside corner: two boards standing on
# edge, one lapping the other, and a top laid over both. The widths
# are what the prior library started them at.
CORNER_FILLER_WIDTH = inch(1.5)

L_ROD_FROM_WALL = inch(12.0)
L_ROD_END_GAP = inch(0.75)
# The other wing has to be at least this deep for clothes on the rod
# to clear it.
L_ROD_MIN_CLEAR = inch(24.0)
# Double hang: how far up the shelf between the two rods sits.
L_DOUBLE_TOP_OPENING = inch(40.8248)

L_WALL_OFFSET = inch(0.5)
L_NOTCH_TOOL_RADIUS = inch(0.25)
# The inside front corner of an L shelf is rounded by default
# rather than cut square. Segments are how finely the arc is
# drawn - fifteen reads smooth at shelf scale without loading
# the viewport with geometry.
L_CORNER_RADIUS = inch(6.0)
L_CORNER_RADIUS_SEGMENTS = 15
# Default distance from the opening TOP to a hang rod's center when the
# rod is added from the menu (modal placement types an exact height).
ROD_TOP_OFFSET = inch(2.145)
ADJ_SHELF_DEFAULT_QTY = 3
# A shelf that sits on clips is cut a touch narrower than the opening
# so it drops in, and it can be held back from the front edge. The
# prior library carried both figures at zero, which is a shelf filling
# the opening; a job that wants a drop-in clearance sets them.
SHELF_CLIP_GAP = inch(0.0)
SHELF_SETBACK = inch(0.0)
# Pullout trays (rollouts): drawer boxes with no fronts, spaced in an
# opening. Each tray stands ROLLOUT_HEIGHT tall (default 4"); the side
# clearance for the slides is ROLLOUT_SLIDE_GAP per side.
ROLLOUT_DEFAULT_QTY = 3
ROLLOUT_HEIGHT = inch(4.0)
ROLLOUT_SLIDE_GAP = inch(0.327)
# Smallest gap left between stacked trays / above and below the stack.
ROLLOUT_MIN_GAP = inch(1.0)
# A tray shorter than this is not worth building, so a stack that is
# squeezed for room stops shrinking its trays here.
ROLLOUT_MIN_HEIGHT = inch(2.0)
# A tray carries a front. Lapped, the front stands proud of the face and
# laps the opening the way a drawer front does; set inside instead, it
# is held back from each side of the opening by this reveal and fills
# the front of the opening depth with its own thickness. The prior
# library carried the reveal at an eighth.
ROLLOUT_INSET_REVEAL = inch(0.125)
# Dividing an opening left and right. A column narrower than this is
# not worth building, so a division that would leave one is refused.
DIVISION_MIN_WIDTH = inch(3.0)
# Cubbies: a grid of divisions and shelves filling an opening. Both can
# be held back from the front edge by the setback. The prior library ran
# both of them the full depth of the opening, so that is where this
# starts; the setback is here as a setting for anyone who wants one.
CUBBY_SETBACK = inch(0.0)
# A grid can take a band at the bottom or the top of an opening instead
# of the whole of it, capped by a shelf, which leaves the rest of the
# opening free for something else. This is how tall that band stands
# when it is first built.
CUBBY_HEIGHT = millimeter(556.95)
CUBBY_PLACEMENT_ITEMS = [
    ('BOTTOM', "Bottom",
     "Cubbies in a band at the bottom of the opening, shelf over them"),
    ('TOP', "Top",
     "Cubbies in a band at the top of the opening, shelf under them"),
    ('FILL', "Fill", "Cubbies filling the whole opening"),
]
# Smallest opening worth leaving behind a band. Asking for a band that
# would not leave this much fills the opening instead.
CUBBY_MIN_REMAINDER = inch(6.0)
# Slanted shoe shelves: angled shelves stacked bottom-up, each with a
# metal shoe fence across the front. Sizes ported from the prior library.
SLANT_SHELF_DEFAULT_QTY = 4
SLANT_SHELF_SPACING = inch(8.0)       # Distance Between Shelves
SLANT_SHELF_ANGLE_DEG = 17.25         # Shelf Angle (degrees)
SLANT_SHELF_SETBACK = inch(0.125)     # front setback with the metal fence
SHOE_FENCE_INSET = millimeter(19.0)   # fence inset from each side
SHOE_FENCE_DEPTH = inch(0.5)          # fence front-to-back size
SHOE_FENCE_HEIGHT = inch(1.5)         # fence height above the shelf
# How far back from the shelf's front edge the fence stands. The prior
# library carried this as its own setting and shipped it at zero, the
# fence flush with the front, so that is where it starts here too.
SHOE_FENCE_BACK_INSET = inch(0.0)
# The fence does not sit on the very lip of the shelf. It stands off the
# front edge by this much before the back inset is counted on top, which
# is the stand-off the prior library built the rail in at.
SHOE_FENCE_STANDOFF = millimeter(20.0)
# Modal add-part height snapping increment (fallback only; the 32mm
# system lattice below is what placement actually snaps to).
PART_Z_SNAP = inch(0.25)

# ---------------------------------------------------------------------------
# 32mm system. Panel/bay heights increment on a 32mm lattice with a 19mm
# base (819 / 1267 / 2131mm - the Base / Hanging / Tall defaults - all
# sit on it). Shelf and rod locations land on system holes: a 12.95mm
# base + n*32mm from the interior bottom (the prior library's
# opening-height enum steps on exactly this lattice).
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


# ---------------------------------------------------------------------------
# Accessories. Bought items that hang in a closet; the library places
# the model and holds the space, the companion add-on carries the
# models, the finishes and the part numbers. See accessories_closets.
# ---------------------------------------------------------------------------
# How close to the opening floor an accessory has to land before it is
# treated as sitting ON the floor rather than floating above it.
ACCESSORY_BOTTOM_SNAP_TOL = inch(0.5)
# Ironing Board Drawer: the melamine plate the board bolts to, and the
# compartment it folds into. Fixed sizes - the board is bought at one
# size and the plate is cut to suit it, so neither follows the opening.
IRONING_BOARD_PLATFORM_WIDTH = inch(12.0)
IRONING_BOARD_PLATFORM_DEPTH = inch(13.625)
IRONING_BOARD_PLATFORM_THICKNESS = inch(0.75)
# Clear height of the compartment the board lives in, measured from the
# opening floor to the underside of the shelf that caps it.
IRONING_BOARD_OPENING_HEIGHT = inch(5.0)

# How tall an accessory that hangs off a panel face draws its cage.
# It is a handle to take hold of, not a claim on the opening.
# Cleat hooks: a board across the back of the opening with hooks
# along it. The board is a hand's height, the hooks stand off its face
# by the thickness of the board, and they are spread between an inset
# at each end - all as the prior library had them.
# A wire basket is drawn from a rig rather than bought whole: its
# wires are laid out one to the inch, and how many there are follows
# how big it has been made. The counts the prior library drove them
# by, one per mesh.
BASKET_BACK_WIRE_OFFSET = -1
BASKET_FRONT_WIRE_OFFSET = -4
BASKET_MESH_BACK = 'Back Wire'
BASKET_MESH_FRONT = 'Front Wire'
BASKET_MESH_BOTTOM = 'Bottom Wire'

CLEAT_HOOK_HEIGHT = inch(4.0)
CLEAT_HOOK_QTY = 6
CLEAT_HOOK_END_INSET = inch(2.0)
# Where a cleat lands when it is let go. Low in the opening it is
# taken to belong on the floor, and near the top to belong flush with
# it - the two snaps the prior library dropped one by.
CLEAT_HOOK_FLOOR_REACH = inch(10.0)
CLEAT_HOOK_TOP_REACH = inch(5.0)

ACCESSORY_PANEL_CAGE_H = inch(2.0)

# An accessory with no model to show is drawn as a block of the space
# it claims, in a red nothing else in the room is, so it reads as
# something missing rather than something built.
ACCESSORY_PLACEHOLDER_COLOR = (0.8, 0.05, 0.05, 1.0)
ACCESSORY_PLACEHOLDER_MATERIAL = 'Accessory Placeholder'

# Dropping an accessory with the mouse. Heights land on a one inch
# grid. An accessory that hangs to the floor sits on it when dropped
# within an inch; everything else is taken to belong on the floor from
# the room it wants below it plus five inches up, which is the rule the
# prior library dropped them by.
ACCESSORY_DROP_GRID = inch(1.0)
ACCESSORY_FLOOR_SNAP = inch(1.0)
ACCESSORY_FLOOR_REACH = inch(5.0)
