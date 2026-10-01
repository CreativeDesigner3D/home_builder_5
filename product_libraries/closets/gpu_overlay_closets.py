"""Editable dimension overlay for closet Starters / Bays / Openings modes.

Step 1 of the closet GPU editing surface (dims; toggles and content chips
follow). While the closet selection mode is active, a POST_PIXEL draw
handler paints value labels:

- Starters mode: W / H / D on every starter root. Committing writes the
  hb_closet_starter props, so bay propagation and the hanging top-anchor
  behave exactly like a sidebar edit.
- Bays mode: every bay's width (auto-locks on commit, pinned labels carry
  a bullet and right-click / 0-Enter resets to auto) PLUS every opening's
  height, so both are editable without a mode switch.
- Openings mode: every opening's clear height as a dimension up its
  left side; typing one moves the bounding fixed shelf onto the 32mm
  holes.

Opening height is a DERIVED value in closets (the clear space between
the fixed shelves that bound it), so committing one moves the shelf
above it (below it, for the top opening) onto the 32mm holes. Typing
back the displayed value lands on the same hole - a no-op.

Architecture mirrors face_frame/dim_edit_overlay.py deliberately: a
permanent draw handler plus addon-keymap click operators that
PASS_THROUGH anything that isn't a label hit, so selection and tools are
untouched and no persistent modal blocks autosave. Labels are recomputed
on click rather than cached, so draw and hit-test can never drift.
"""

import bpy
import blf
import math
import gpu
from mathutils import Vector
from bpy_extras import view3d_utils

from ... import units
from ... import hb_placement
from ...hb_types import GeoNodeCutpart
from ...hb_gpu_draw import get_visible_window_bounds
from . import types_closets
from . import const_closets as const
# Stale-matrix-safe cage readers (valid for cages created while hidden).
from ..face_frame import split_preview

# ---- Style (matches face_frame's overlay) ---------------------------------

FONT_SIZE       = 12
PAD_X           = 6
PAD_Y           = 4
LABEL_BG        = (0.13, 0.13, 0.14, 0.85)
LABEL_BG_DIM    = (0.13, 0.13, 0.14, 0.45)
LABEL_BORDER    = (1.0, 1.0, 1.0, 0.25)
EDIT_BG         = (0.20, 0.43, 0.70, 0.95)
TEXT_COLOR      = (0.95, 0.95, 0.95, 1.0)
TEXT_COLOR_DIM  = (0.95, 0.95, 0.95, 0.45)
EDIT_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
DIM_LINE_COLOR     = (0.90, 0.90, 0.90, 0.80)
DIM_LINE_COLOR_DIM = (0.90, 0.90, 0.90, 0.35)
TICK_PX         = 5
# Opening height dims stand this far in from the opening's left side
# (at most a quarter of its width), clear of the rod and drawer labels
# that sit on the centerline.
HEIGHT_DIM_INSET = units.inch(3.0)
# Smallest clear height a typed opening height may leave the opening
# on the other side of the shelf it moves.
MIN_OPENING_CLEAR = units.inch(1.0)

_INPUT_CHARS = set("0123456789./-'\" ")

_HUD_MARGIN_Y = 12
_HUD_BTN_H = 24
_HUD_ROW_GAP = 6
_PILL_GAP = 4

# Widget-family filters. Each is (pill label, scene idprop key, kind
# prefixes it controls, modes it applies to). Scene idprops (default on)
# need no registration and save with the file.
# Structural add/remove-bay pills and contents chips were removed in
# design review (too busy) - those actions live on the right-click
# menus. The overlay keeps dims, mount toggles, and the Grab pill.
_FILTERS = [
    ("Dims", 'hb_ov_show_dims',
     ('STARTER_', 'BAY_', 'OPEN_H', 'PART_Z', 'ROD_TOP', 'DRAWER_H',
      'TOGGLE_LOCK'),
     ('Starters', 'Bays', 'Openings')),
    ("Bottoms", 'hb_ov_show_mount',
     ('TOGGLE_BOTTOM',), ('Bays',)),
]


def _filter_on(scene, key):
    return bool(scene.get(key, 1))


def _kind_visible(scene, kind):
    for _label, key, prefixes, _modes in _FILTERS:
        if kind.startswith(prefixes):
            return _filter_on(scene, key)
    return True


# The Dims pill is a 3-state cycle stored in its idprop: 1 = All
# (default, and what an old saved True reads as), 2 = Selected (labels
# only for cages in the current selection), 0 = Off. _filter_on treats
# 2 as truthy so the family stays on; the per-target filter in
# compute_labels narrows it. Mirrors face_frame's Sizes pill.
_DIMS_KEY = 'hb_ov_show_dims'


def _dims_scope(scene):
    try:
        value = int(scene.get(_DIMS_KEY, 1))
    except (TypeError, ValueError):
        value = 1
    return {0: 'OFF', 2: 'SELECTED'}.get(value, 'ALL')


def _selection_name_sets(context):
    """(raw, expanded): names of the selected objects (+ active), and
    that set expanded with every ancestor. A label is in-selection when
    its object is in the expanded set (labels that target an ENCLOSING
    cage - e.g. starter W/H/D while a bay is selected) or when one of
    ITS ancestors is directly selected (labels that target a child
    part - rods, drawer fronts - of a selected opening or bay)."""
    raw = set()
    expanded = set()
    objs = list(getattr(context, 'selected_objects', ()) or ())
    act = getattr(context, 'active_object', None)
    if act is not None and act not in objs:
        objs.append(act)
    for obj in objs:
        raw.add(obj.name)
        node = obj
        while node is not None:
            expanded.add(node.name)
            node = node.parent
    return raw, expanded


def _obj_in_selection(obj, raw, expanded):
    if obj.name in expanded:
        return True
    node = obj.parent
    while node is not None:
        if node.name in raw:
            return True
        node = node.parent
    return False

# Label kinds. STARTER_* commit hb_closet_starter props; BAY_W commits
# the bay width (auto-lock); OPEN_H inverse-writes the bay height.
KIND_ITEMS = [
    ('STARTER_W', "Starter Width", ""),
    ('STARTER_H', "Starter Height", ""),
    ('STARTER_D', "Starter Depth", ""),
    ('BAY_W', "Bay Width", ""),
    ('OPEN_H', "Opening Height", ""),
    # Bay top height OFF THE FLOOR (world Z); committing moves the top.
    ('BAY_H', "Bay Height", ""),
    # Bay depth, at the bottom-front of the bay.
    ('BAY_D', "Bay Depth", ""),
    # Per-part height (fixed shelf underside, opening-local)
    ('PART_Z', "Part Height", ""),
    # Hang rod: its center down from the top of its opening
    ('ROD_TOP', "Rod From Top", ""),
    # Drawer stack front height (opening idprop)
    ('DRAWER_H', "Drawer Front Height", ""),
]

# ---- Module state ----------------------------------------------------------

_draw_handle = None
_shutdown = False
_edit = None   # {'name', 'kind', 'typed', 'owner'} while an edit runs
_addon_keymaps = []


class _DistanceParser:
    """Borrow the placement mixin's typed-distance grammar. All four
    methods are needed - parse_typed_distance calls the other three
    through self (face_frame's overlay lends the same set)."""
    parse_typed_distance = hb_placement.PlacementMixin.parse_typed_distance
    _parse_feet_inches = hb_placement.PlacementMixin._parse_feet_inches
    _extract_number = hb_placement.PlacementMixin._extract_number
    _number_to_scene_units = hb_placement.PlacementMixin._number_to_scene_units
    typed_value = ""


_parser = _DistanceParser()


def parse_distance(text):
    """Typed string -> metres, or None. Same grammar as placement typing."""
    try:
        return _parser.parse_typed_distance(text)
    except Exception:
        return None


# ---- Gating ----------------------------------------------------------------

def _active_mode(context):
    """'Starters' / 'Bays' / 'Openings' when the overlay should draw."""
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'CLOSET':
        return None
    props = getattr(scene, 'hb_closets', None)
    if props is None or not getattr(props, 'closet_selection_mode_enabled', False):
        return None
    mode = getattr(props, 'closet_selection_mode', '')
    return mode if mode in ('Starters', 'Bays', 'Openings', 'Parts') else None


def _filter_pill_rects(context, area, mode):
    """[(label, key, rect)] for the filter pills applicable to the
    active mode - one centered row below the HUD's mode picker.

    Grab and the Dims scope are HUD widgets now, on the mode row itself
    (viewport_hud's _ClosetGrabPill and _ClosetDimsButton), where face
    frame has kept its pair all along: they modify what the mode does,
    so they belong beside the mode rather than on a row of their own.
    Add Shelf and Add Rod went to the product library, which is where
    everything else that makes a part is chosen from. What is left here
    is the visibility families and the Open Door action.
    """
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    x_min, x_max, _y_min, y_max = get_visible_window_bounds(area)
    blf.size(0, FONT_SIZE * s)
    pills = []
    for label, key, _p, modes in _FILTERS:
        if mode not in modes:
            continue
        if key == _DIMS_KEY:
            # The family entry stays - the label filter still reads it -
            # but its pill is the HUD's now.
            continue
        pills.append((label, key))
    # Open Door is a HUD icon on the mode row now (viewport_hud's
    # _ClosetOpenDoorButton), matching the cabinet libraries.
    if not pills:
        return []
    widths = [blf.dimensions(0, label)[0] + 24 * s for label, _k in pills]
    h = _HUD_BTN_H * s
    total = sum(widths) + _PILL_GAP * s * max(0, len(pills) - 1)
    row1_y = y_max - _HUD_MARGIN_Y * s - h
    y = row1_y - (h + _HUD_ROW_GAP * s)
    x = x_min + ((x_max - x_min) - total) / 2.0
    rects = []
    for (label, key), w in zip(pills, widths):
        rects.append((label, key, (x, y, w, h)))
        x += w + _PILL_GAP * s
    return rects


# ---- Label collection --------------------------------------------------------

def _iter_starter_roots(scene):
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            yield obj


def _iter_bay_cages(starter):
    for child in starter.children:
        if child.get(types_closets.TAG_BAY_CAGE):
            yield child


def _iter_opening_cages(bay):
    for child in bay.children:
        if child.get(types_closets.TAG_OPENING_CAGE):
            yield child


def _starter_shown(starter, space=None):
    """False when the closet is hidden in the viewport (wall hidden with
    its children, subtree hidden, isolate / local view, collection off)
    so its labels and grab handles vanish with it. The cages can't carry
    this test - toggle_mode hides/shows them per selection mode - so
    probe a structural part that is always visible when the closet is:
    the first partition panel (never design-hidden, present on every
    starter class including L shelves)."""
    for child in starter.children:
        if (child.get('hb_part_role') == types_closets.PART_ROLE_PANEL
                and not child.get('hb_double_partition')
                and not child.get('hb_panel_off')):
            try:
                if (space is not None
                        and getattr(space, 'type', '') == 'VIEW_3D'):
                    return child.visible_get(viewport=space)
                return child.visible_get()
            except Exception:
                return True
    return True


def _anchor_world(cage, fx, fz):
    """World point on a cage's front face at fractional X / Z."""
    dim_x, dim_z = split_preview._cage_dims(cage)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cage)
    return mw @ Vector((dim_x * fx, -0.003, dim_z * fz))


def _starter_label_targets(starter):
    """(kind, anchor, value) for the three starter dims. Each label sits
    where its edit ACTS: H at the top edge centered -
    the edge that moves when you change the height; W dead-center of the
    front face; D on the bottom-front edge centered on the width. Values
    come from the SAME props a commit writes so typing them back is a
    no-op."""
    sp = starter.hb_closet_starter
    return [
        ('STARTER_H', _anchor_world(starter, 0.5, 1.0), sp.height, "H "),
        ('STARTER_W', _anchor_world(starter, 0.5, 0.5), sp.width, "W "),
        ('STARTER_D', _anchor_world(starter, 0.5, 0.0), sp.depth, "D "),
    ]


def _height_dim_line(opening):
    """World (bottom, top) of an opening's height dimension line."""
    dim_x, _dim_z = split_preview._cage_dims(opening)
    fx = min(HEIGHT_DIM_INSET / dim_x, 0.25) if dim_x > 0.0 else 0.5
    a = _anchor_world(opening, fx, 0.0)
    b = _anchor_world(opening, fx, 1.0)
    if a is None or b is None:
        return None
    return a, b


def _project_dim_line(region, rv3d, line, s):
    """Region-space LINES points (the line plus an end tick at each
    end) for a world-space dimension line, or []."""
    a = view3d_utils.location_3d_to_region_2d(region, rv3d, line[0])
    b = view3d_utils.location_3d_to_region_2d(region, rv3d, line[1])
    if a is None or b is None:
        return []
    d = b - a
    if d.length < 1e-6:
        return []
    tick = Vector((-d.y, d.x)).normalized() * TICK_PX * s
    return [tuple(p) for p in (a, b, a - tick, a + tick, b - tick, b + tick)]


def compute_labels(context, region, rv3d, lines_out=None):
    """[(obj_name, kind, editable, locked, rect, text)] currently on
    screen. Shared by draw and the click operators. When ``lines_out``
    is a list, the region-space dimension lines the labels sit on are
    appended to it as (points, editable)."""
    mode = _active_mode(context)
    if mode is None or rv3d is None:
        return []
    scene = context.scene
    unit_settings = scene.unit_settings
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    blf.size(0, FONT_SIZE * s)

    space = getattr(context, 'space_data', None)
    targets = []   # (obj, kind, editable, locked, anchor, value, prefix)
    dim_lines = {}  # (obj name, kind) -> world (a, b)
    for starter in _iter_starter_roots(scene):
        if not _starter_shown(starter, space):
            continue
        if mode == 'Starters':
            for kind, anchor, value, prefix in _starter_label_targets(starter):
                targets.append((starter, kind, True, False,
                                anchor, value, prefix))
            continue
        # Same placement rule as the starter labels: a label sits where
        # its edit ACTS. Bay width = mid-face of the bay (panels move
        # sideways around it); opening height = the opening's top edge;
        # part labels ride the part they move.
        for bay in _iter_bay_cages(starter):
            if mode == 'Bays':
                bp = bay.hb_closet_bay
                targets.append((bay, 'BAY_W', True, bp.unlock_width,
                                _anchor_world(bay, 0.5, 0.5),
                                bp.width, "W "))
                # Bay depth: drawn at the FRONT edge of the bay floor
                # (full -Y), centered on width - so in a side view it
                # sits at the front instead of stacking on the front-
                # face W / H labels.
                b_mw = split_preview._world_matrix(bay)
                b_w, _bh = split_preview._cage_dims(bay)
                d_anchor = b_mw @ Vector((b_w * 0.5, -bp.depth, 0.001))
                targets.append((bay, 'BAY_D', True, False,
                                d_anchor, bp.depth, "D "))
            # Opening heights split by concern: Bays mode shows only the
            # TOPMOST segment per side (that label edits the bay height);
            # Openings mode shows only the capped segments (those labels
            # move their capping shelf). Keeps shelf information out of
            # Bays mode and bay-level values out of Openings mode.
            openings_by_side = {}
            for opening in _iter_opening_cages(bay):
                side = opening.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
                openings_by_side.setdefault(side, []).append(opening)
            top_index = {side: max(o.get('hb_opening_index', 0) for o in ops)
                         for side, ops in openings_by_side.items()}
            shelves_by_side = {}
            for side in openings_by_side:
                shelves_by_side[side] = sorted(
                    [c for c in bay.children
                     if c.get('hb_part_role')
                     == types_closets.PART_ROLE_FIXED_SHELF
                     and c.get(types_closets.PROP_OPENING_SIDE,
                               'FRONT') == side
                     and not c.get('hb_preview')],
                    key=lambda o: o.get('hb_z_offset', 0.0))
            for opening in _iter_opening_cages(bay):
                side = opening.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
                idx = opening.get('hb_opening_index', 0)
                is_top = (idx == top_index[side])
                o_w, interior_h = split_preview._cage_dims(opening)
                if mode == 'Bays' and is_top:
                    # Bay height reads OFF THE FLOOR (world Z of the bay
                    # top) and sits on the top edge - the line the grab
                    # handle drags. One emission per side.
                    bay_top_world = (split_preview._world_matrix(bay)
                                     .translation.z
                                     + bay.hb_closet_bay.height)
                    targets.append((bay, 'BAY_H', True, False,
                                    _anchor_world(bay, 0.5, 1.0),
                                    bay_top_world, "H "))
                elif (mode == 'Openings'
                        and int(opening.get('hb_col_index', 0)) == 0):
                    # Every opening's clear height, as a dimension up
                    # its left side - one per row; the columns of a
                    # divided row share it. Typing one moves the fixed
                    # shelf that bounds it (the one above, or below for
                    # the top opening) onto the 32mm holes, rounding the
                    # opening down; a bay with
                    # no fixed shelf has nothing to move.
                    line = _height_dim_line(opening)
                    if line is not None:
                        editable = bool(shelves_by_side.get(side))
                        dim_lines[(opening.name, 'OPEN_H')] = line
                        targets.append((opening, 'OPEN_H', editable, False,
                                        (line[0] + line[1]) / 2.0,
                                        interior_h, ""))
                if mode != 'Openings':
                    continue
                # Per-part labels: a rod shows how far its center
                # hangs below the top of its opening, as a dimension
                # from the rod up to the top - the figure it is hung
                # by; a drawer stack shows its front height at the
                # stack's top edge.
                o_mw = split_preview._world_matrix(opening)
                for child in opening.children:
                    role = child.get('hb_part_role')
                    if (role == types_closets.PART_ROLE_ROD
                            and not child.get('hb_preview')):
                        rod_z = child.location.z
                        line = (o_mw @ Vector((o_w / 2.0, -0.003, rod_z)),
                                o_mw @ Vector((o_w / 2.0, -0.003,
                                               interior_h)))
                        dim_lines[(child.name, 'ROD_TOP')] = line
                        targets.append((child, 'ROD_TOP', True, False,
                                        (line[0] + line[1]) / 2.0,
                                        max(interior_h - rod_z, 0.0), ""))
                    elif role == types_closets.PART_ROLE_DRAWER_FRONT:
                        # Every drawer front carries its own editable height
                        # label at its center; the bullet marks the fronts
                        # the user has pinned, which the stack redistributes
                        # around.
                        # The height the front is standing at right now:
                        # a pinned front squeezed by its opening labels
                        # what is on screen, not the height it is owed.
                        dh = child.get(
                            types_closets.PROP_FRONT_HEIGHT_SOLVED,
                            child.get(types_closets.PROP_FRONT_HEIGHT,
                                      const.DRAWER_FRONT_HEIGHT))
                        pinned = bool(child.get(
                            types_closets.PROP_UNLOCK_FRONT_HEIGHT, 0))
                        anchor = o_mw @ Vector(
                            (o_w / 2.0, -0.003,
                             child.location.z + dh / 2.0))
                        targets.append((child, 'DRAWER_H', True, pinned,
                                        anchor, dh, ""))

    # SELECTED scope on the Dims pill: keep only labels whose object
    # belongs to the current selection (itself, an enclosing cage, or a
    # part hanging under a selected cage). Toggle widgets (the Bottoms
    # family) are gated by their own pill, not the Dims scope; a
    # filtered bay's lock glyph disappears with its BAY_W label because
    # the glyph keys off the visible label rect.
    if _dims_scope(scene) == 'SELECTED':
        raw, expanded = _selection_name_sets(context)
        targets = [t for t in targets
                   if _obj_in_selection(t[0], raw, expanded)]

    labels = []
    for obj, kind, editable, locked, anchor, value, prefix in targets:
        if anchor is None:
            continue
        pt = view3d_utils.location_3d_to_region_2d(region, rv3d, anchor)
        if pt is None:
            continue
        text = prefix + units.unit_to_string(unit_settings, value)
        # BAY_W carries a dedicated lock glyph (added below) instead of
        # the bullet prefix.
        if locked and kind != 'BAY_W':
            text = "• " + text
        tw, th = blf.dimensions(0, text)
        w = tw + 2 * PAD_X * s
        h = th + 2 * PAD_Y * s
        rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
        if rect[0] + w < 0 or rect[0] > region.width:
            continue
        if rect[1] + h < 0 or rect[1] > region.height:
            continue
        labels.append((obj.name, kind, editable, locked, rect, text))
        if lines_out is not None:
            line = dim_lines.get((obj.name, kind))
            if line is not None:
                pts = _project_dim_line(region, rv3d, line, s)
                if pts:
                    lines_out.append((pts, editable))

    # ----- Toggle widgets (Bays mode). Reuses the label tuple shape:
    # editable=False keeps them out of the edit modal; the ``locked``
    # slot carries the ACTIVE state for pill coloring. -----
    if mode == 'Bays':
        bay_w_rects = {name: rect for name, kind, _e, _l, rect, _t in labels
                       if kind == 'BAY_W'}
        for starter in _iter_starter_roots(scene):
            if not _starter_shown(starter, space):
                continue
            for bay in _iter_bay_cages(starter):
                bp = bay.hb_closet_bay
                # Lock glyph flush right of the bay's width label.
                lrect = bay_w_rects.get(bay.name)
                if lrect is not None:
                    glyph = "•" if bp.unlock_width else "○"
                    gw, _gh = blf.dimensions(0, glyph)
                    gh = lrect[3]
                    grect = (lrect[0] + lrect[2] + 2 * s, lrect[1],
                             gw + 2 * PAD_X * s, gh)
                    labels.append((bay.name, 'TOGGLE_LOCK', False,
                                   bp.unlock_width, grect, glyph))
                # Bottom on/off pill just above the bay's bottom edge -
                # the very bottom-front is the bay depth (BAY_D) label, so
                # the pill sits a touch higher to clear it.
                anchor = _anchor_world(bay, 0.5, 0.08)
                if anchor is None:
                    continue
                pt = view3d_utils.location_3d_to_region_2d(
                    region, rv3d, anchor)
                if pt is None:
                    continue
                text = "Bottom"
                tw, th = blf.dimensions(0, text)
                w = tw + 2 * PAD_X * s
                h = th + 2 * PAD_Y * s
                rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
                if (rect[0] + w < 0 or rect[0] > region.width
                        or rect[1] + h < 0 or rect[1] > region.height):
                    continue
                labels.append((bay.name, 'TOGGLE_BOTTOM', False,
                               not bp.remove_bottom, rect, text))

    # Per-family visibility filters (the pills below the HUD).
    return [entry for entry in labels if _kind_visible(scene, entry[1])]


# ---- Draw handler ------------------------------------------------------------

def _draw_label_rect(shader, rect, bg):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    from gpu_extras.batch import batch_for_shader
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def _draw_filter_pills(shader, context, area, font_sz, mode):
    """One pill per widget family applicable to the mode; active blue
    while that family is shown. The Open Door pill mirrors its modal
    state instead."""
    for label, key, rect in _filter_pill_rects(context, area, mode):
        if key == '__open_door__':
            try:
                from .operators import op_open_door_closet
                on = op_open_door_closet.open_door_is_active()
            except Exception:
                on = False
        else:
            on = _filter_on(context.scene, key)
        _draw_label_rect(shader, rect, EDIT_BG if on else LABEL_BG)
        blf.size(0, font_sz)
        blf.color(0, *(EDIT_TEXT_COLOR if on else TEXT_COLOR))
        tw, th = blf.dimensions(0, label)
        blf.position(0, rect[0] + (rect[2] - tw) / 2.0,
                     rect[1] + (rect[3] - th) / 2.0, 0)
        blf.draw(0, label)


def _draw():
    """Permanent POST_PIXEL callback; cheap no-op outside closet modes.
    Fully exception-guarded - a draw error must never spam the viewport."""
    if _shutdown:
        return
    try:
        context = bpy.context
        area = context.area
        region = context.region
        if area is None or area.type != 'VIEW_3D':
            return
        if region is None or region.type != 'WINDOW':
            return
        mode = _active_mode(context)
        if mode is None:
            return
        dim_lines = []
        labels = compute_labels(context, region, context.region_data,
                                dim_lines)

        s = 1.0
        try:
            s = bpy.context.preferences.system.ui_scale
        except AttributeError:
            pass
        font_sz = FONT_SIZE * s
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        from gpu_extras.batch import batch_for_shader
        for editable in (True, False):
            pts = [p for line, ed in dim_lines if ed == editable
                   for p in line]
            if pts:
                shader.uniform_float(
                    "color",
                    DIM_LINE_COLOR if editable else DIM_LINE_COLOR_DIM)
                batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)
        _draw_filter_pills(shader, context, area, font_sz, mode)
        for name, kind, editable, _locked, rect, text in labels:
            if kind.startswith('TOGGLE_'):
                # Toggle pill/glyph: ``_locked`` slot = active state.
                _draw_label_rect(shader, rect,
                                 EDIT_BG if _locked else LABEL_BG)
                blf.size(0, font_sz)
                blf.color(0, *(EDIT_TEXT_COLOR if _locked else TEXT_COLOR))
                tw, th = blf.dimensions(0, text)
                blf.position(0, rect[0] + (rect[2] - tw) / 2.0,
                             rect[1] + (rect[3] - th) / 2.0, 0)
                blf.draw(0, text)
                continue
            editing = (_edit is not None and _edit['name'] == name
                       and _edit['kind'] == kind)
            if editing:
                typed = _edit['typed']
                shown = (typed + "|") if typed else text
                blf.size(0, font_sz)
                tw, _th = blf.dimensions(0, shown)
                w = max(rect[2], tw + 2 * PAD_X * s)
                rect = (rect[0], rect[1], w, rect[3])
                _draw_label_rect(shader, rect, EDIT_BG)
                blf.color(0, *EDIT_TEXT_COLOR)
                blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
                blf.draw(0, shown)
            else:
                _draw_label_rect(shader, rect,
                                 LABEL_BG if editable else LABEL_BG_DIM)
                blf.size(0, font_sz)
                blf.color(0, *(TEXT_COLOR if editable else TEXT_COLOR_DIM))
                blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
                blf.draw(0, text)
        gpu.state.blend_set('NONE')
    except Exception:
        pass


# ---- Accessory space box -------------------------------------------------------
# The room an accessory asks its opening for - the space below its
# mounting line and above it that the maker says it needs to work - drawn
# as a wire box across the opening while the accessory is selected, the
# way the prior library showed it. Only then: a room of closets full of
# boxes would bury what they are drawn round.

SPACE_BOX_COLOR = (0.35, 0.75, 1.0, 0.9)
_space_handle = None


def _selected_accessory(context):
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    from . import types_closets
    return types_closets.find_accessory_cage(obj)


def _space_box_lines(cage):
    """World-space line pairs for one accessory's reserved space, or
    None when it is not in an opening or not in the catalog."""
    from . import types_closets
    from . import accessories_closets as acc
    from ...hb_types import GeoNodeCage
    opening = cage.parent
    if opening is None or not opening.get(types_closets.TAG_OPENING_CAGE):
        return None
    acc_def = acc.get(cage.get(types_closets.PROP_ACCESSORY_KEY, ''))
    if acc_def is None:
        return None
    z0, z1 = types_closets.accessory_span(cage, acc_def)
    if z1 - z0 <= 1e-5:
        return None
    try:
        op_cage = GeoNodeCage(opening)
        w = op_cage.get_input('Dim X')
        d = op_cage.get_input('Dim Y')
    except Exception:
        return None
    m = opening.matrix_world
    corners = [m @ Vector((x, y, z)) for z in (z0, z1)
               for y in (0.0, -d) for x in (0.0, w)]
    # 0-3 the bottom (x, y), 4-7 the top.
    edges = ((0, 1), (2, 3), (0, 2), (1, 3),
             (4, 5), (6, 7), (4, 6), (5, 7),
             (0, 4), (1, 5), (2, 6), (3, 7))
    return [corners[i] for pair in edges for i in pair]


def _draw_space_box():
    if _shutdown:
        return
    try:
        cage = _selected_accessory(bpy.context)
        if cage is None:
            return
        lines = _space_box_lines(cage)
        if not lines:
            return
        from gpu_extras.batch import batch_for_shader
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": lines})
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('NONE')
        gpu.state.line_width_set(2.0)
        shader.bind()
        shader.uniform_float("color", SPACE_BOX_COLOR)
        batch.draw(shader)
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')
    except Exception:
        pass


# ---- Commit ------------------------------------------------------------------

def _commit(obj, kind, value):
    """Write the typed value through the same property paths the dialogs
    use, so update callbacks / redistribution / regenerators all fire."""
    if kind == 'STARTER_W':
        obj.hb_closet_starter.width = value
        return True
    if kind == 'STARTER_H':
        # A typed height comes DOWN to the 32mm system: the number is
        # the space there is, so a run must not come back taller than
        # it. The Custom Height field in the starter's properties is
        # where an off-system height is asked for on purpose.
        obj.hb_closet_starter.height = const.snap_system_height_down(value)
        return True
    if kind == 'STARTER_D':
        obj.hb_closet_starter.depth = value
        return True
    if kind == 'BAY_W':
        # Fires _update_bay_width: auto-locks + redistributes the rest.
        obj.hb_closet_bay.width = value
        return True
    if kind == 'BAY_D':
        obj.hb_closet_bay.depth = value
        return True
    if kind == 'OPEN_H':
        return _commit_opening_height(obj, value)
    if kind == 'BAY_H':
        # Typed value = desired bay top off the floor. Move the top by
        # the delta (floor bays: top lands exactly at the value; hanging
        # bays keep their run-top anchor, so the height change shifts
        # the bottom instead).
        root = types_closets.find_starter_root(obj)
        if root is None:
            return False
        bp = obj.hb_closet_bay
        scene_props = types_closets.run_sizes(obj)
        st = scene_props.shelf_thickness
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        top_world = (split_preview._world_matrix(obj).translation.z
                     + bp.height)
        min_h = kick + 2.0 * st + units.inch(1.0)
        bp.height = max(min_h, bp.height + (value - top_world))
        return True
    if kind == 'PART_Z':
        root = types_closets.find_starter_root(obj)
        if root is None:
            return False
        parent = obj.parent
        if parent is not None and parent.get(types_closets.TAG_BAY_CAGE):
            # Splitting shelf: value IS the bay-interior offset.
            obj['hb_z_offset'] = float(max(0.0, value))
            types_closets.recalculate_closet_starter(root)
            return True
        # Opening-child part (rod): displayed value is opening-local Z;
        # convert to its anchor convention (rods ride the opening top).
        if parent is None:
            return False
        _w, interior_h = split_preview._cage_dims(parent)
        if obj.get('hb_anchor_top'):
            obj['hb_z_offset'] = float(max(0.0, interior_h - value))
        else:
            obj['hb_z_offset'] = float(max(0.0, value))
        types_closets.recalculate_closet_starter(root)
        return True
    if kind == 'ROD_TOP':
        # Typed value = rod center down from the top of its opening. A
        # rod never hangs closer to the shelf above than its cups allow.
        root = types_closets.find_starter_root(obj)
        parent = obj.parent
        if root is None or parent is None:
            return False
        _w, interior_h = split_preview._cage_dims(parent)
        drop = min(max(value, const.ROD_TOP_OFFSET), interior_h)
        obj['hb_z_offset'] = float(drop)
        obj['hb_anchor_top'] = 1
        types_closets.recalculate_closet_starter(root)
        return True
    if kind == 'DRAWER_H':
        # obj is a single drawer FRONT. Hand it this height and let the
        # stack spread what is left over the fronts it still owns.
        root = types_closets.find_starter_root(obj)
        if root is None:
            return False
        obj[types_closets.PROP_FRONT_HEIGHT] = float(max(0.0, value))
        obj[types_closets.PROP_UNLOCK_FRONT_HEIGHT] = 1
        types_closets.recalculate_closet_starter(root)
        return True
    return False


def _snap_shelf_offset(target, lo, hi, up=False):
    """The 32mm-system hole at or below ``target`` (at or above when
    ``up``) that lies within [lo, hi] - bay-interior offsets of a fixed
    shelf's underside - or None when no hole fits."""
    pitch = const.SYSTEM_PITCH
    # A target already on a hole must not lose a step to float error.
    tol = 0.00005
    n = (target - const.SYSTEM_HOLE_BASE) / pitch
    n = math.ceil(n - tol / pitch) if up else math.floor(n + tol / pitch)
    z = const.SYSTEM_HOLE_BASE + max(0, n) * pitch
    while z < lo - 1e-6:
        z += pitch
    while z > hi + 1e-6:
        z -= pitch
    if z < lo - 1e-6 or z < 0.0:
        return None
    return z


def _commit_opening_height(opening, value):
    """Give an opening the typed clear height by moving the fixed shelf
    that bounds it - the shelf above it, or for the top opening the
    shelf below it. The shelf lands on the 32mm-system hole that gives
    the asked-for height or the next one down - never taller than typed
    - and never closer than MIN_OPENING_CLEAR to the shelf or bay limit
    on its other side; the neighbouring opening
    takes up the difference."""
    bay = types_closets.find_bay_cage(opening)
    root = types_closets.find_starter_root(opening)
    if bay is None or root is None:
        return False
    side = opening.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
    shelves = sorted(
        [c for c in bay.children
         if c.get('hb_part_role') == types_closets.PART_ROLE_FIXED_SHELF
         and c.get(types_closets.PROP_OPENING_SIDE, 'FRONT') == side
         and not c.get('hb_preview')],
        key=lambda o: o.get('hb_z_offset', 0.0))
    if not shelves:
        return False
    rows = [o for o in _iter_opening_cages(bay)
            if o.get(types_closets.PROP_OPENING_SIDE, 'FRONT') == side]
    top = max(rows, key=lambda o: o.get('hb_opening_index', 0))
    interior_h = (float(top.get('hb_seg_bottom', 0.0))
                  + split_preview._cage_dims(top)[1])
    st = types_closets.run_sizes(bay).shelf_thickness
    idx = int(opening.get('hb_opening_index', 0))
    zs = [float(sh.get('hb_z_offset', 0.0)) for sh in shelves]
    # A typed height is the most the opening may be: the shelf lands on
    # the hole that gives the opening that height or the next one down.
    if idx < len(shelves):
        # Capped: the shelf above moves (down to a hole); the opening's
        # floor stays.
        k = idx
        target = float(opening.get('hb_seg_bottom', 0.0)) + value
        up = False
    else:
        # Top opening: the shelf below moves (up to a hole); the bay
        # top stays.
        k = len(shelves) - 1
        target = interior_h - value - st
        up = True
    lo = (zs[k - 1] + st if k > 0 else 0.0) + MIN_OPENING_CLEAR
    hi = ((zs[k + 1] if k + 1 < len(zs) else interior_h)
          - st - MIN_OPENING_CLEAR)
    z = _snap_shelf_offset(target, lo, hi, up)
    if z is None:
        return False
    shelves[k]['hb_z_offset'] = float(z)
    types_closets.recalculate_closet_starter(root)
    return True


def _reset_to_auto(obj, kind):
    """Hand a pinned value back so the run owns it again. BAY_W puts a
    bay width back on the run; DRAWER_H puts a drawer front back on the
    stack, which then fills evenly."""
    if kind == 'BAY_W' and obj.hb_closet_bay.unlock_width:
        # Handing the width back carries its own recalc.
        obj.hb_closet_bay.unlock_width = False
        return True
    if kind == 'DRAWER_H' and obj.get(
            types_closets.PROP_UNLOCK_FRONT_HEIGHT):
        obj[types_closets.PROP_UNLOCK_FRONT_HEIGHT] = 0
        root = types_closets.find_starter_root(obj)
        if root is not None:
            types_closets.recalculate_closet_starter(root)
        return True
    return False


# ---- Edit modal ----------------------------------------------------------------

class hb_closets_OT_edit_dim_label(bpy.types.Operator):
    """Type a new value for the clicked dimension label. Enter commits,
    0-Enter / X resets a bay width to auto, Esc / click-away cancels."""
    bl_idname = "hb_closets.edit_dim_label"
    bl_label = "Edit Closet Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    kind: bpy.props.EnumProperty(items=KIND_ITEMS, options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        global _edit
        if bpy.data.objects.get(self.target_name) is None:
            return {'CANCELLED'}
        _edit = {'name': self.target_name, 'kind': self.kind, 'typed': "",
                 'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('TEXT')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        global _edit
        _edit = None
        try:
            context.window.cursor_set('DEFAULT')
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        global _edit
        if _edit is None or _edit.get('owner') != id(self):
            return {'CANCELLED'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}

        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'}:
            typed = _edit['typed']
            obj = bpy.data.objects.get(self.target_name)
            value = parse_distance(typed) if typed else None
            if not typed:
                self._finish(context)
                return {'FINISHED'}
            if obj is not None and value == 0.0:
                self._finish(context)
                _reset_to_auto(obj, self.kind)
                return {'FINISHED'}
            if obj is None or value is None or value <= 0.0:
                self.report({'WARNING'},
                            f"Could not read '{typed}' as a size")
                self._finish(context)
                return {'CANCELLED'}
            self._finish(context)
            _commit(obj, self.kind, value)
            return {'FINISHED'}

        if event.type in {'X', 'DEL'}:
            obj = bpy.data.objects.get(self.target_name)
            self._finish(context)
            if obj is not None:
                _reset_to_auto(obj, self.kind)
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'BACK_SPACE':
            _edit['typed'] = _edit['typed'][:-1]
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        ch = event.unicode
        if ch and ch in _INPUT_CHARS:
            _edit['typed'] += ch
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}


# ---- Click routing --------------------------------------------------------------

class hb_closets_OT_dim_label_click(bpy.types.Operator):
    """Routes a viewport left-press to overlay labels; everything else
    passes through untouched."""
    bl_idname = "hb_closets.dim_label_click"
    bl_label = "Closet Dimension Label Click"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (not _shutdown
                and context.area is not None
                and context.area.type == 'VIEW_3D'
                and context.region is not None
                and context.region.type == 'WINDOW'
                and _active_mode(context) is not None)

    def invoke(self, context, event):
        if _edit is not None:
            return {'PASS_THROUGH'}
        try:
            from ...operators import viewport_hud
            if viewport_hud.click_hits_widget(
                    context, context.area,
                    event.mouse_region_x, event.mouse_region_y):
                return {'PASS_THROUGH'}
        except Exception:
            pass
        mx, my = event.mouse_region_x, event.mouse_region_y
        mode = _active_mode(context)
        for _label, key, (tx, ty, tw, th) in _filter_pill_rects(
                context, context.area, mode):
            if tx <= mx <= tx + tw and ty <= my <= ty + th:
                if key == '__open_door__':
                    from .operators import op_open_door_closet
                    if op_open_door_closet.open_door_is_active():
                        op_open_door_closet.request_open_door_exit()
                    else:
                        bpy.ops.hb_closets.open_door_mode('INVOKE_DEFAULT')
                else:
                    context.scene[key] = (0 if _filter_on(context.scene, key)
                                          else 1)
                context.area.tag_redraw()
                return {'FINISHED'}
        for name, kind, editable, _locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if kind == 'TOGGLE_BOTTOM':
                bay = bpy.data.objects.get(name)
                if bay is not None:
                    bp = bay.hb_closet_bay
                    # Update callback runs the recalc (kick hides with
                    # the bottom).
                    bp.remove_bottom = not bp.remove_bottom
                    context.area.tag_redraw()
                return {'FINISHED'}
            if kind == 'TOGGLE_LOCK':
                bay = bpy.data.objects.get(name)
                if bay is not None:
                    bp = bay.hb_closet_bay
                    if bp.unlock_width:
                        _reset_to_auto(bay, 'BAY_W')
                    else:
                        # Give the bay its own width, held at what it
                        # measures now while the rest of the run is
                        # redistributed around it.
                        bp.unlock_width = True
                    context.area.tag_redraw()
                return {'FINISHED'}
            if not editable:
                return {'PASS_THROUGH'}
            bpy.ops.hb_closets.edit_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


class hb_closets_OT_dim_label_reset(bpy.types.Operator):
    """Right-click on a pinned (•) bay width resets it to auto."""
    bl_idname = "hb_closets.dim_label_reset"
    bl_label = "Reset Closet Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_closets_OT_dim_label_click.poll(context)

    def invoke(self, context, event):
        if _edit is not None:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        for name, kind, editable, locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if not (editable and locked):
                return {'PASS_THROUGH'}
            obj = bpy.data.objects.get(name)
            if obj is not None and _reset_to_auto(obj, kind):
                context.area.tag_redraw()
                return {'FINISHED'}
            return {'PASS_THROUGH'}
        return {'PASS_THROUGH'}


# ---- Lifecycle --------------------------------------------------------------------

classes = (
    hb_closets_OT_edit_dim_label,
    hb_closets_OT_dim_label_click,
    hb_closets_OT_dim_label_reset,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        hb_closets_OT_dim_label_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        hb_closets_OT_dim_label_reset.bl_idname, 'RIGHTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    global _draw_handle, _shutdown
    _shutdown = False
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    global _space_handle
    _space_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_space_box, (), 'WINDOW', 'POST_VIEW')
    _register_keymaps()


def unregister():
    global _draw_handle, _shutdown, _edit
    _shutdown = True
    _edit = None
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    global _space_handle
    if _space_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_space_handle, 'WINDOW')
        except Exception:
            pass
        _space_handle = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
