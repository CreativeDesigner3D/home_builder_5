"""Applied-panel frame sizing.

Pass 1: computes rail and stile widths for an applied panel so it
reads as a visual continuation of the cabinet front. For PANELED with
a 5-piece door style, factors door overlay + door stile/rail widths
into the panel widths so the panel + door together would have looked
like one continuous frame had a door been mounted on the side. For
SLAB doors, no door style, or WORKING_FF / FALSE_FF (where the
"panel" is an applied face frame, not a panel), copies cabinet face
frame widths to the panel directly.

Gated by Face_Frame_Cabinet_Props.panel_frame_auto. When False, the
panel's stored widths stand and this module is a no-op.

Pass 2 (deferred): mirror the parent cabinet's bay-split structure
onto the panel - auto mid rails for horizontal splits, auto mid stile
for wide bays.
"""
import bpy

from ... import hb_types
from ... import hb_utils
from . import types_face_frame


def _resolve_door_style(cab_obj):
    """cabinet -> active cabinet style (by STYLE_NAME custom prop)
    -> door style (by name string into scene's door_styles pool).
    Returns the door style PropertyGroup or None if any link is
    missing / empty.
    """
    style_name = cab_obj.get('STYLE_NAME')
    if not style_name:
        return None
    from .props_hb_face_frame import get_style_props
    scene_props = get_style_props()
    cab_style = None
    for cs in scene_props.cabinet_styles:
        if cs.name == style_name:
            cab_style = cs
            break
    if cab_style is None:
        return None
    door_style_name = cab_style.door_style
    if not door_style_name or door_style_name == 'NONE':
        return None
    for ds in scene_props.door_styles:
        if ds.name == door_style_name:
            return ds
    return None


def _toe_kick_band(cab):
    """Bottom-rail growth needed for Base/Tall cabinets where the
    applied panel spans the full cabinet height (floor to top) and
    the bottom rail has to visually cover the toe-kick band so the
    panel's frame opening doesn't drop into the recess. Uppers and
    PANEL cabinets have no toe kick.
    """
    if cab.cabinet_type in ('BASE', 'TALL'):
        return cab.toe_kick_height
    return 0.0


def _stile_widths(cab, side):
    """Returns (panel_left_stile, panel_right_stile) for a panel on the
    given side, sourced from the cabinet's same-side face frame stile.

    The panel sits behind the face frame, which extends forward by
    face_frame_thickness. At the corner, the visible "vertical frame"
    is face_frame edge + panel's facing stile - so the panel's facing
    stile is the cabinet stile minus fft, making the visible corner
    width read as the cabinet stile dim. The panel's outer stile (the
    one against the wall) sees no face frame in front of it so takes
    the full cabinet stile width.

    BACK has no face frame on the back to sit behind, so neither stile
    gets the fft deduction. The back panel is rotated pi around Z, so
    its panel-left edge maps to the cabinet's right side and vice
    versa - each end of the back panel mirrors the cabinet stile it
    abuts.
    """
    fft = cab.face_frame_thickness
    if side == 'LEFT':
        return cab.left_stile_width, cab.left_stile_width - fft
    if side == 'RIGHT':
        return cab.right_stile_width - fft, cab.right_stile_width
    # BACK
    return cab.right_stile_width, cab.left_stile_width


def _match_cabinet_widths(cab, side):
    """Rails match cabinet face frame; stiles come from _stile_widths
    so the facing stile is reduced by face_frame_thickness like the
    5-piece path. Used for WORKING_FF, FALSE_FF, and PANELED with a
    non-5-piece (or absent) door style. Bottom rail extended by the
    toe-kick band for Base/Tall.
    """
    left_stile, right_stile = _stile_widths(cab, side)
    return {
        'top_rail_width':    cab.top_rail_width,
        'bottom_rail_width': cab.bottom_rail_width + _toe_kick_band(cab),
        'left_stile_width':  left_stile,
        'right_stile_width': right_stile,
    }


def _match_5_piece_door(cab, door_style, side):
    """5-piece PANELED sizing rule.

    Rails: the cabinet's rail is partly covered by door overlay;
    adding the door's own rail width back reconstructs the visible
    rail in panel-only form. Same logic for the bottom rail, plus
    the toe-kick band for Base/Tall.

    Stiles: sourced from the cabinet face frame (not the door) since
    what's visible at a corner is the face frame edge plus the panel
    behind it. See _stile_widths for the per-side mapping.
    """
    rail = door_style.rail_width
    top_rail = cab.top_rail_width - cab.default_top_overlay + rail
    bottom_rail = (
        cab.bottom_rail_width - cab.default_bottom_overlay
        + rail + _toe_kick_band(cab)
    )
    left_stile, right_stile = _stile_widths(cab, side)
    return {
        'top_rail_width':    top_rail,
        'bottom_rail_width': bottom_rail,
        'left_stile_width':  left_stile,
        'right_stile_width': right_stile,
    }


def resolve_panel_sizing(cab_obj, side, panel_condition):
    """Returns the dict of widths to write to the panel, or None when
    auto is off (caller should skip writes).
    """
    cab = cab_obj.face_frame_cabinet
    if not cab.panel_frame_auto:
        return None
    if panel_condition in ('WORKING_FF', 'FALSE_FF'):
        sizes = _match_cabinet_widths(cab, side)
    else:
        # PANELED: 5-piece door drives the rail formula for all three
        # sides including BACK. SLAB or missing door style falls back to
        # the match-cabinet path.
        door_style = _resolve_door_style(cab_obj)
        if door_style is None or door_style.door_type != '5_PIECE':
            sizes = _match_cabinet_widths(cab, side)
        else:
            sizes = _match_5_piece_door(cab, door_style, side)
    # The back panel has no cabinet face frame at its ends to align to,
    # so its left/right stiles match the mid stiles - a uniform stile
    # width reads cleanly across the whole back. LEFT/RIGHT panels keep
    # the corner-aligned widths from _stile_widths.
    if side == 'BACK':
        msw = _mid_stile_width_for_panel(cab_obj, cab, side)
        sizes['left_stile_width'] = msw
        sizes['right_stile_width'] = msw
    return sizes


def apply_panel_sizing(cab_obj, panel_obj, side, panel_condition):
    """Write computed widths to the panel. Stiles render from
    cabinet-level left/right_stile_width, but rails render from each
    bay's own top/bottom_rail_width - so we mirror the rail values to
    every bay as well. Style assignment uses the same pattern (see
    Face_Frame_Cabinet_Style._apply_face_frame_sizes_to_cabinet_inner).
    Wrapped in suspend_recalc so multiple writes coalesce into one
    panel recalc at exit.
    """
    sizes = resolve_panel_sizing(cab_obj, side, panel_condition)
    if sizes is None:
        return
    panel_props = panel_obj.face_frame_cabinet
    with types_face_frame.suspend_recalc():
        # Respect per-part unlocks: a rail/stile the user unlocked + overrode
        # on the applied panel's own face frame must survive a host-cabinet
        # recalc (which re-runs this auto-size). Locked parts keep following
        # the auto-calc. Mirrors _apply_face_frame_sizes_to_cabinet_inner.
        # Stiles render from the panel cabinet level, rails from each bay,
        # so each write is gated by the unlock flag at its own level.
        if not panel_props.unlock_top_rail:
            panel_props.top_rail_width = sizes['top_rail_width']
        if not panel_props.unlock_bottom_rail:
            panel_props.bottom_rail_width = sizes['bottom_rail_width']
        if not panel_props.unlock_left_stile:
            panel_props.left_stile_width = sizes['left_stile_width']
        if not panel_props.unlock_right_stile:
            panel_props.right_stile_width = sizes['right_stile_width']
        for child in panel_obj.children_recursive:
            if not child.get(types_face_frame.TAG_BAY_CAGE):
                continue
            bay = child.face_frame_bay
            if not bay.unlock_top_rail:
                bay.top_rail_width = sizes['top_rail_width']
            if not bay.unlock_bottom_rail:
                bay.bottom_rail_width = sizes['bottom_rail_width']


# ---------------------------------------------------------------------------
# Toe-kick corner notch on the panel's bottom rail + facing stile
# ---------------------------------------------------------------------------

# Which stile is "facing" (room-side) on a side panel. BACK has no facing
# stile - no notch on back panels.
_FACING_STILE_ROLE = {
    'LEFT':  types_face_frame.PART_ROLE_RIGHT_STILE,
    'RIGHT': types_face_frame.PART_ROLE_LEFT_STILE,
}

# CPM_CORNERNOTCH Flip X / Flip Y / Flip Z values per side, per part.
# These pick which corner of the part the notch removes. The cabinet
# side panel uses (False, True, False); panel parts have different
# rotations so the right combination has to be determined empirically.
# Starting values match the cabinet side; refine after visual check.
_NOTCH_FLIPS_BOTTOM_RAIL = {
    'LEFT':  (True, False, False),
    'RIGHT': (False, False, False),
}
_NOTCH_FLIPS_FACING_STILE = {
    'LEFT':  (False, True, False),
    'RIGHT': (False, True, False),
}

# Face frame thickness for the panel parts (3/4" standard). Used as the
# notch's Route Depth so the cut goes all the way through.
_PANEL_PART_THICKNESS = 0.75 * 0.0254  # meters

# Mid stile threshold. Panel regions wider than this get an
# auto-generated vertical splitter at their center.
_MID_STILE_WIDTH_THRESHOLD = 21.0 * 0.0254

# Applied-panel opening count by panel width: one opening up to 20",
# then one extra
# opening (and thus one extra mid stile) at roughly every 18" step,
# capped at 8 openings. Mid-stile count is openings - 1.
_PANEL_OPENING_WIDTH_BREAKS = (
    20.0 * 0.0254,   # <= -> 1 opening
    38.0 * 0.0254,   # <= -> 2
    56.0 * 0.0254,   # <= -> 3
    74.0 * 0.0254,   # <= -> 4
    92.0 * 0.0254,   # <= -> 5
    110.0 * 0.0254,  # <= -> 6
    128.0 * 0.0254,  # <= -> 7
)                    #  > last -> 8


def _panel_opening_qty(width):
    """Number of openings a real-bay applied panel of this width gets
    (per the width ladder above). Mid stiles = result - 1."""
    for i, brk in enumerate(_PANEL_OPENING_WIDTH_BREAKS):
        if width <= brk:
            return i + 1
    return len(_PANEL_OPENING_WIDTH_BREAKS) + 1


def apply_panel_toe_kick_notch(cab_obj, panel_obj, side):
    """Add or refresh a 'Notch Front Bottom' CPM_CORNERNOTCH on the
    panel's bottom rail and facing stile so the panel cleanly clears
    a NOTCH-type toe kick recess. Active only when the parent cabinet
    is BASE/TALL with toe_kick_type == 'NOTCH'; otherwise the modifier
    is left in place (lazily added) but hidden. BACK panels are
    skipped - the back has no toe kick to clear.

    X (depth) differs per part: the facing stile sits at the front of
    the panel and gets the full toe_kick_setback. The bottom rail
    starts BEHIND the facing stile, so its notch only has to remove
    what's left over after the stile took the front portion -
    setback minus the facing stile width.

    Y (height) is the same for both: toe_kick_height.
    """
    if side == 'BACK':
        return
    cab = cab_obj.face_frame_cabinet
    # A stile dropped to the floor fills the toe-kick recess on that end, so
    # the panel's parts must NOT be notched there. side LEFT/RIGHT maps to the
    # cabinet's same-side end stile. (toe_kick_type == 'NOTCH' below already
    # excludes FLUSH, where the stile is always to-floor.)
    # Leg products keep their toe kick on the leg_product propgroup (and
    # is_column / only_stile suppress it), not on the cabinet-level
    # toe-kick fields - so the applied-panel notch must follow those,
    # else it stays notched even when the leg's toe kick height is 0.
    is_leg = bool(cab_obj.get('IS_LEG_PRODUCT'))
    if is_leg:
        leg = cab_obj.leg_product
        active = ((not leg.is_column) and (not leg.only_stile)
                  and leg.toe_kick_height > 0.0)
    else:
        stile_to_floor = (cab.extend_left_stile_to_floor if side == 'LEFT'
                          else cab.extend_right_stile_to_floor)
        active = (
            cab.cabinet_type in ('BASE', 'TALL')
            and cab.toe_kick_type == 'NOTCH'
            and not stile_to_floor
        )

    facing_role = _FACING_STILE_ROLE.get(side)
    if facing_role is None:
        return

    bottom_rail = None
    facing_stile = None
    for c in panel_obj.children_recursive:
        role = c.get('hb_part_role')
        if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
            bottom_rail = c
        elif role == facing_role:
            facing_stile = c

    # Facing stile width comes from the same per-side rule as the
    # panel sizing - facing element is the second value for LEFT, the
    # first for RIGHT.
    left_stile, right_stile = _stile_widths(cab, side)
    facing_width = right_stile if side == 'LEFT' else left_stile
    if is_leg:
        setback = cab_obj.leg_product.toe_kick_setback
        kick = (0.0 if cab_obj.leg_product.is_column
                else cab_obj.leg_product.toe_kick_height)
    else:
        setback = cab.toe_kick_setback
        kick = cab.toe_kick_height

    # Axis mapping differs by part because their local rotations
    # differ. Bottom rail: X = depth-into-the-rail (setback), Y = kick
    # height. Facing stile: rotated such that X = kick height, Y =
    # setback - the same notch corner but the part's local X axis
    # points up the stile instead of along the rail.
    parts = []
    if bottom_rail is not None:
        parts.append((
            bottom_rail,
            _NOTCH_FLIPS_BOTTOM_RAIL[side],
            max(0.0, setback - facing_width),  # X = depth
            kick,                               # Y = height
        ))
    if facing_stile is not None:
        parts.append((
            facing_stile,
            _NOTCH_FLIPS_FACING_STILE[side],
            kick,      # X = height (stile runs vertically)
            setback,   # Y = depth
        ))

    for part_obj, flips, x_val, y_val in parts:
        _ensure_and_drive_notch(part_obj, active, x_val, y_val, flips)


def _ensure_and_drive_notch(part_obj, active, x_val, y_val, flips):
    """Lazily add Notch Front Bottom on part_obj, then refresh ALL
    inputs (including Flip X/Y/Z) and toggle visibility every recalc.
    Caller pre-computes x_val (depth) and y_val (height) since they
    differ per part.
    """
    mod = part_obj.modifiers.get('Notch Front Bottom')
    if mod is None:
        wrapper = hb_types.GeoNodeCutpart(part_obj)
        cpm = wrapper.add_part_modifier(
            'CPM_CORNERNOTCH', 'Notch Front Bottom')
        mod = cpm.mod
    if mod.node_group is None:
        return
    if not active:
        x_val = y_val = 0.0
        route = 0.0
    else:
        route = _PANEL_PART_THICKNESS
    ng = mod.node_group
    for input_name, value in (
        ('X', x_val),
        ('Y', y_val),
        ('Route Depth', route),
        ('Flip X', flips[0]),
        ('Flip Y', flips[1]),
        ('Flip Z', flips[2]),
    ):
        node_input = ng.interface.items_tree.get(input_name)
        if node_input is not None:
            hb_utils.set_gn_input(mod, node_input.identifier, value)
    mod.show_viewport = active
    mod.show_render = active



# ---------------------------------------------------------------------------
# Pass 2: panel split structure (mid rails + mid stiles)
# ---------------------------------------------------------------------------

def _strip_panel_carcass_parts(panel_obj):
    """Remove any MID_DIVISION / PARTITION_SKIN parts from a panel root.
    Panels carry no carcass, so these are always spurious - left over
    from older builds where insert_bay seeded them onto the panel."""
    stale = (types_face_frame.PART_ROLE_MID_DIVISION,
             types_face_frame.PART_ROLE_PARTITION_SKIN)
    for child in list(panel_obj.children):
        if child.get('hb_part_role') in stale:
            mesh = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if mesh is not None and getattr(mesh, 'users', 0) == 0:
                bpy.data.meshes.remove(mesh)


def apply_panel_split_structure(cab_obj, panel_obj, side):
    """Build the panel's internal opening tree.

    Decisions:
      1. Mid rail: only if the source bay (bay 0 for LEFT, last for
         RIGHT, none for BACK) has a door-over-door H-split. Width
         per the standard formula: 2*door_rail + bay_mid_rail -
         (top_overlay + bottom_overlay). Z-position locked to match
         the cabinet's mid rail in absolute cabinet space.
      2. Mid stile, NO mid rails: a panel >= 21" wide builds as TWO
         REAL BAYS -- the mid stile is a true bay divider, so the
         cabinet prompts read "2 bays" and per-bay editing works.
         (Was an in-bay V-split historically; converted by request.
         Existing single-bay panels migrate on their next recalc.)
      3. Mid stile, WITH mid rails (rail-matched LEFT / RIGHT
         panels): unchanged -- one bay, full-width H-split rail(s),
         and any leaf region >= 21" wide gets a centered in-bay
         V-split, each region checked independently. A bay divider
         runs full height and would cut the matched rail, so the
         rail look stays split-tree based.

    Bay quantity is reconciled in place (insert_bay / delete_bay), so
    a panel flips structure cleanly when a rail appears or disappears
    on the source cabinet. Trees are wipe-and-rebuild on every call;
    panels have no user state on their openings (all default
    front_type) so rebuilding is safe and idempotent.

    Gated by cab.panel_frame_auto.
    """
    if not cab_obj.face_frame_cabinet.panel_frame_auto:
        return
    panel_bay_obj = _find_panel_bay(panel_obj)
    if panel_bay_obj is None:
        return

    # Self-heal: panels have no carcass, so MID_DIVISION / PARTITION_SKIN
    # parts are always spurious. insert_bay historically seeded them onto
    # applied panels; strip any so panels built before the
    # _create_mid_parts_at guard converge to a clean state on recalc.
    _strip_panel_carcass_parts(panel_obj)

    panel_props = panel_obj.face_frame_cabinet
    # Manual mode: the user has pinned this panel's openings - via insert /
    # delete bay or an Opening-mode H / V split (both flip panel_split_auto
    # off). Leave the whole opening tree untouched so those edits survive
    # the host recalc; only the carcass-part strip above runs. Frame widths
    # still flow through apply_panel_sizing, gated separately by
    # panel_frame_auto.
    if not panel_props.panel_split_auto:
        return

    rails = _detect_panel_mid_rails(cab_obj, side, panel_bay_obj)
    wide = panel_props.width >= _MID_STILE_WIDTH_THRESHOLD
    # Openings scale with width when the panel splits into real bays
    # (no rail-matched H-split in play); see the width ladder above.
    n_open = _panel_opening_qty(panel_props.width)

    # Bay quantity: real-bay mid stile only when no rails are in play.
    # insert_bay / delete_bay manage their own recalc guards and were
    # built to run on a live cabinet -- call them OUTSIDE the suspend
    # block. insert_bay clones the anchor bay's tree, which is fine:
    # every bay tree is wiped + rebuilt below.
    desired_qty = n_open if not rails else 1
    bays = _sorted_panel_bays(panel_obj)
    pcab = types_face_frame._wrap_cabinet(panel_obj)
    while len(bays) < desired_qty:
        pcab.insert_bay(len(bays) - 1, 'AFTER')
        bays = _sorted_panel_bays(panel_obj)
    while len(bays) > desired_qty:
        pcab.delete_bay(len(bays) - 1)
        bays = _sorted_panel_bays(panel_obj)

    add_mid_stile = wide and desired_qty == 1

    # All mutation inside suspend_recalc so intermediate prop writes
    # don't trigger panel recalcs that would run the size redistributor
    # against a half-built tree and overwrite locked sizes with
    # share-of-remainder values. One panel recalc fires at exit.
    with types_face_frame.suspend_recalc():
        # The bay divider renders at the panel's own mid_stile_widths;
        # match it to the door-style stile so a real-bay stile prints
        # at the same width the in-bay V-split used.
        stile_w = _mid_stile_width_for_panel(
            cab_obj, cab_obj.face_frame_cabinet, side)
        for entry in panel_props.mid_stile_widths:
            entry.width = stile_w

        for bay_obj in bays:
            _wipe_bay_tree(bay_obj)
            if not rails and not add_mid_stile:
                _create_opening_under(bay_obj, child_index=0,
                                      opening_index=0)
                continue
            _build_panel_tree(
                bay_obj, rails, add_mid_stile, cab_obj, side,
            )


def _sorted_panel_bays(panel_obj):
    """The panel's bay cages in bay-index order."""
    return sorted(
        [c for c in panel_obj.children
         if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda b: b.face_frame_bay.bay_index,
    )


def _find_panel_bay(panel_obj):
    for c in panel_obj.children:
        if c.get(types_face_frame.TAG_BAY_CAGE):
            return c
    return None


def _bay_top_child(bay_obj):
    """The single top-level opening or split node under the bay."""
    kids = [c for c in bay_obj.children
            if (c.get(types_face_frame.TAG_OPENING_CAGE)
                or c.get(types_face_frame.TAG_SPLIT_NODE))]
    return kids[0] if len(kids) == 1 else None


def _detect_panel_mid_rails(cab_obj, side, panel_bay_obj):
    """Walk the source side's face frame and return a list of panel
    mid rails to render, sorted top to bottom by Z (descending).

    Each entry: {'z_bottom': panel-bay-local Z of the rail's bottom
    edge, 'splitter_width': the rail's height}.

    Two categories of mid rails are detected:
      1. Cabinet-level rail between two DOOR-front openings stacked
         vertically in the source bay (door-over-door split). Width
         per the standard formula = 2*door_rail + bay_mid_rail - 2*overlay,
         because the visible band combines both doors' rails plus the
         exposed portion of the cabinet's bay mid rail.
      2. Per-door mid rails - any door whose 5-piece style has
         Add Mid Rail set (manually or auto-added because front_length
         > 45.5"). Width = the door style's mid rail width.

    BACK panels: no per-door rails (no door-side correspondence). The
    cabinet-level case requires a stacked split in a bay, which BACK
    panels don't mirror.
    """
    if side == 'BACK':
        return []
    cab_bays = sorted(
        [c for c in cab_obj.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda b: b.face_frame_bay.bay_index,
    )
    if not cab_bays:
        return []
    source_bay_obj = cab_bays[0] if side == 'LEFT' else cab_bays[-1]

    rails = []
    cab_rail = _detect_cabinet_level_mid_rail(
        cab_obj, source_bay_obj, panel_bay_obj
    )
    if cab_rail is not None:
        rails.append(cab_rail)

    rails.extend(_detect_door_mid_rails(
        cab_obj, source_bay_obj, panel_bay_obj
    ))

    # Sort top to bottom (descending Z).
    rails.sort(key=lambda r: r['z_bottom'], reverse=True)
    return rails


def _detect_cabinet_level_mid_rail(cab_obj, source_bay_obj, panel_bay_obj):
    """The bay's top-level H-split between two DOOR fronts gives a
    cabinet-level mid rail. Returns None if the bay isn't shaped that
    way.
    """
    top = _bay_top_child(source_bay_obj)
    if top is None or not top.get(types_face_frame.TAG_SPLIT_NODE):
        return None
    split = top.face_frame_split
    if split.axis != 'H':
        return None
    kids = [c for c in top.children
            if c.get(types_face_frame.TAG_OPENING_CAGE)]
    if len(kids) != 2:
        return None
    if not all(c.face_frame_opening.front_type == 'DOOR' for c in kids):
        return None
    kids.sort(key=lambda c: c.get('hb_split_child_index', 0))

    # Source mid rail bottom Z, cabinet-local. Parent-chain sum reads
    # the values just written by the cabinet's recalc dispatch (which
    # ran before _reconcile_applied_panels); matrix_world here would
    # be stale until the next depsgraph evaluation.
    source_mid_rail_z = _find_source_mid_rail_z(top, cab_obj)
    if source_mid_rail_z is None:
        source_mid_rail_z = (
            source_bay_obj.location.z
            + kids[-1].face_frame_opening.size
        )

    cab = cab_obj.face_frame_cabinet
    door_rail = _door_rail_width(cab_obj)

    # Panel rail aligns with the visible band the door layout produces:
    # cabinet mid rail bottom + top_overlay (where bottom door's top
    # rail sits) - door_rail (so the panel rail's bottom edge matches
    # the door's bottom rail top edge). Collapses to mid_rail + overlay
    # for SLAB doors (door_rail = 0).
    panel_z_cab_local = (
        source_mid_rail_z
        + cab.default_top_overlay
        - door_rail
    )
    panel_z_bay_local = panel_z_cab_local - panel_bay_obj.location.z

    splitter_width = (
        2 * door_rail
        + split.splitter_width
        - cab.default_top_overlay
        - cab.default_bottom_overlay
    )

    return {
        'z_bottom': max(0.0, panel_z_bay_local),
        'splitter_width': max(0.0, splitter_width),
    }


_AUTO_MID_RAIL_DOOR_HEIGHT = 45.5 * 0.0254  # door length above which 5-piece auto-adds a mid rail


def _detect_door_mid_rails(cab_obj, source_bay_obj, panel_bay_obj):
    """Derive door mid rails from each rendered DOOR's Length (off
    the GeoNodeCutpart modifier, which _update_fronts_in_opening
    sets during the same recalc, BEFORE _reconcile_applied_panels)
    combined with the cabinet's door style settings.

    Avoided two earlier approaches that fail during a cabinet recalc:
      - reading CPM_5PIECEDOOR inputs on the door: the style modifier
        propagates AFTER the panel reconcile, so it isn't there yet.
      - computing door height from the cage's Dim Z: the cage extends
        beyond the FF opening by perimeter reveals, which vary per
        opening; the math compounds errors.

    Mirrored doors (Left/Right halves of a divided opening) share a
    Z; dedupe so a single mid rail spawns.
    """
    door_style = _resolve_door_style(cab_obj)
    if door_style is None or door_style.door_type != '5_PIECE':
        return []
    mid_rail_width = door_style.mid_rail_width
    if mid_rail_width <= 0:
        return []

    found = {}  # rounded z_cab key -> rail dict
    for door_obj in source_bay_obj.children_recursive:
        if door_obj.get('hb_part_role') != 'DOOR':
            continue

        length = _read_cutpart_length(door_obj)
        if length is None or length <= 0:
            continue

        auto = length > _AUTO_MID_RAIL_DOOR_HEIGHT
        if not (auto or door_style.add_mid_rail):
            continue

        # Auto-added mid rails are always centered; manual rails honor
        # the style's center_mid_rail toggle.
        if auto or door_style.center_mid_rail:
            rail_center_in_door = length / 2.0
        else:
            rail_center_in_door = door_style.mid_rail_location

        # Door bottom Z in cab-local coords - parent-chain walk
        # (door's local origin sits at its bottom edge).
        door_bottom_cab = 0.0
        o = door_obj
        while o is not None and o is not cab_obj:
            door_bottom_cab += o.location.z
            o = o.parent
        rail_bottom_cab = (
            door_bottom_cab + rail_center_in_door - mid_rail_width / 2.0
        )

        key = round(rail_bottom_cab, 5)
        if key in found:
            continue
        z_bay_local = rail_bottom_cab - panel_bay_obj.location.z
        found[key] = {
            'z_bottom': max(0.0, z_bay_local),
            'splitter_width': mid_rail_width,
        }
    return list(found.values())


def _read_cutpart_length(door_obj):
    """Return the door's Length input from its GeoNodeCutpart modifier
    (door height). None if not present.
    """
    for m in door_obj.modifiers:
        if m.type != 'NODES' or m.node_group is None:
            continue
        if m.node_group.name != 'GeoNodeCutpart':
            continue
        it = m.node_group.interface.items_tree.get('Length')
        if it is None:
            return None
        try:
            return hb_utils.get_gn_input(m, it.identifier)
        except Exception:
            return None
    return None


def _door_rail_width(cab_obj):
    door_style = _resolve_door_style(cab_obj)
    if door_style is not None and door_style.door_type == '5_PIECE':
        return door_style.rail_width
    return 0.0


def _find_source_mid_rail_z(split_node_obj, cab_obj):
    """Find the rendered BAY_MID_RAIL part for split_node_obj and
    return its Z in cabinet-local coords (= rail's bottom edge per
    _create_bay_mid_rail's contract). Returns None when no such part
    exists.

    Walks the parent chain summing local Z rather than reading
    matrix_world. The cabinet recalc positions parts via direct
    obj.location writes; matrix_world doesn't reflect those until the
    next depsgraph evaluation, so during the same recalc pass it
    returns stale (often zero) world coords.
    """
    for c in cab_obj.children_recursive:
        if c.get('hb_part_role') != 'BAY_MID_RAIL':
            continue
        if c.parent is not split_node_obj:
            continue
        z_acc = 0.0
        o = c
        while o is not None and o is not cab_obj:
            z_acc += o.location.z
            o = o.parent
        return z_acc
    return None


def _wipe_bay_tree(bay_obj):
    """Delete every descendant of the bay - opening cages, split nodes,
    AND everything parented under them (front pivots, fronts, interior
    items, etc.). Removing only the opening leaves its child pivots /
    fronts orphaned at world origin since they keep their world-space
    location after losing the parent transform.

    Walks the full descendant set and deletes in reverse so deeper
    objects unparent before their ancestors, same pattern as
    types_face_frame._remove_root_with_children.
    """
    descendants = list(bay_obj.children_recursive)
    for obj in reversed(descendants):
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)


def _create_opening_under(parent_obj, child_index, opening_index,
                          size=0.0, unlock_size=False, front_type='INSET_PANEL'):
    """Create one FaceFrameOpening parented to parent_obj."""
    op = types_face_frame.FaceFrameOpening()
    op.create('Opening')
    op.obj.parent = parent_obj
    op.obj['hb_split_child_index'] = child_index
    op_props = op.obj.face_frame_opening
    op_props.opening_index = opening_index
    # unlock_size before size for the same reason as in
    # _build_v_split_region - see comment there.
    op_props.unlock_size = unlock_size
    op_props.size = size
    op_props.front_type = front_type
    return op.obj


def _create_split_node_under(parent_obj, child_index, axis, splitter_width):
    """Create one Split Node empty parented to parent_obj."""
    node = bpy.data.objects.new('Split Node', None)
    bpy.context.scene.collection.objects.link(node)
    node.empty_display_type = 'PLAIN_AXES'
    node.empty_display_size = 0.001
    node[types_face_frame.TAG_SPLIT_NODE] = True
    node.parent = parent_obj
    node['hb_split_child_index'] = child_index
    sp = node.face_frame_split
    sp.axis = axis
    sp.splitter_width = splitter_width
    sp.add_backing = False
    return node


def _build_panel_tree(panel_bay_obj, rails, add_mid_stile, cab_obj, side):
    """Construct the panel's opening tree.

    `rails` is a list of {'z_bottom', 'splitter_width'} dicts in
    panel-bay-local coords, sorted top to bottom (descending Z).
    Empty list -> single leaf region (or V-split if add_mid_stile).

    With N rails the tree is N nested H-splits: outermost H-split for
    the topmost rail, each subsequent rail's H-split nested inside
    the previous H-split's bottom child. Each H-split's bottom child
    has `size` locked to that rail's bay-local Z (= distance from bay
    bottom to the rail's bottom edge), which is how the rail lands at
    the right height.

    Each leaf region (every H-split's top child + the innermost
    H-split's bottom child) gets a V-split when add_mid_stile is True,
    otherwise a single opening.
    """
    cab = cab_obj.face_frame_cabinet
    mid_stile_w = _mid_stile_width_for_panel(cab_obj, cab, side)

    op_counter = [0]
    def next_op_idx():
        v = op_counter[0]
        op_counter[0] = v + 1
        return v

    def make_leaf_region(parent, child_index, size, unlock):
        if add_mid_stile:
            _build_v_split_region(parent, child_index=child_index,
                                  mid_stile_w=mid_stile_w,
                                  size=size, unlock_size=unlock,
                                  next_op_idx=next_op_idx)
        else:
            _create_opening_under(parent, child_index=child_index,
                                  opening_index=next_op_idx(),
                                  size=size, unlock_size=unlock)

    if not rails:
        make_leaf_region(panel_bay_obj, child_index=0,
                         size=0.0, unlock=False)
        return

    # Walk rails top-to-bottom, nesting H-splits.
    current_parent = panel_bay_obj
    current_child_idx = 0
    parent_locked_size = 0.0
    parent_unlock = False

    for i, rail in enumerate(rails):
        is_last = (i == len(rails) - 1)
        h_split = _create_split_node_under(
            current_parent, child_index=current_child_idx,
            axis='H', splitter_width=rail['splitter_width'],
        )
        # If this H-split was placed as a locked-size bottom child of
        # an outer H-split, apply the lock here. Sets the H-split's
        # own size in its parent's frame - separate from its splitter
        # width (which goes on the H-split's children).
        if parent_unlock:
            h_split.face_frame_split.unlock_size = True
            h_split.face_frame_split.size = parent_locked_size

        # Top child of this H-split = region above this rail.
        make_leaf_region(h_split, child_index=0, size=0.0, unlock=False)

        if is_last:
            make_leaf_region(h_split, child_index=1,
                             size=rail['z_bottom'], unlock=True)
        else:
            # Bottom child is the next H-split; descend.
            current_parent = h_split
            current_child_idx = 1
            parent_locked_size = rail['z_bottom']
            parent_unlock = True


def _build_v_split_region(parent_obj, child_index, mid_stile_w,
                          size, unlock_size, next_op_idx):
    """Build a V-split + 2 equal opening children, attached to
    parent_obj at child_index. size + unlock_size are applied to the
    SPLIT NODE (so the parent containing the V-split is sized correctly
    when its container - e.g. H-split - decides positions).
    """
    v = _create_split_node_under(
        parent_obj, child_index=child_index,
        axis='V', splitter_width=mid_stile_w,
    )
    sp = v.face_frame_split
    # unlock_size before size: setting size first while unlock_size is
    # still False makes the redistributor (on the panel-recalc fired by
    # the size write) treat this node as unlocked and clobber the value
    # with share-of-remainder.
    sp.unlock_size = unlock_size
    sp.size = size
    _create_opening_under(v, child_index=0, opening_index=next_op_idx())
    _create_opening_under(v, child_index=1, opening_index=next_op_idx())


def _mid_stile_width_for_panel(cab_obj, cab, side):
    """Mid stile sits in open panel field with no face frame edge in
    front of it, so its visible width is its actual width - no fft
    deduction. Source from the active door style's stile width when
    available (the mid stile reads as a continuation of the 5-piece
    door pattern); for SLAB / no door style, fall back to the cabinet's
    left_stile_width.
    """
    door_style = _resolve_door_style(cab_obj)
    if door_style is not None and door_style.door_type == '5_PIECE':
        return door_style.stile_width
    return cab.left_stile_width
