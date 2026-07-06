"""Editable dimension overlay for Cabinet / Bay / Opening / Face Frame
selection modes.

While the face-frame selection mode is 'Cabinets', 'Bays', 'Openings'
or 'Face Frame', a POST_PIXEL draw handler paints a value label on
every cabinet root (W / H / D, like the closet starter overlay), every
bay (its width), every leaf opening (its height), or every face-frame
member (its width -- stiles, rails, bay splitters) of every face-frame
cabinet in the viewport. Clicking a label starts a short-lived modal that captures
typed input (same distance grammar as placement typing: inches,
fractions, feet'inches"); Enter commits the value through the same
properties the sidebar edits, so redistribution and auto-hold behave
identically to a sidebar edit:

- Cabinet W/H/D -> Face_Frame_Cabinet_Props.width / height / depth --
  the same props the Cabinet Properties dialog edits, so the update
  callbacks recalc and bay redistribution behaves identically.
- Bay width   -> Face_Frame_Bay_Props.width (auto-locks + recalcs via
  _update_bay_width). Bay height / depth -> Face_Frame_Bay_Props.height
  / depth with the matching unlock flag flipped first (they're
  cabinet-driven until unlocked - mirrors the sidebar's lock icons).
- Opening height -> Face_Frame_Opening_Props.size with unlock_size
  flipped on first, so the typed height holds during redistribution
  (mirrors the Split Opening dialog's typed sizes). Only openings whose
  parent is an H-split are height-editable; bay-root openings and
  V-split children show a dimmed, read-only label (their height is
  driven by the bay / cabinet).
- Part width -> the same per-role targets the right-click Set Width
  dialog writes (ops_part_commands._fan_out_value), with the matching
  unlock flag flipped first so a later style apply keeps the value.
  Between-bay mid rails carry no width command, so they show a dimmed,
  read-only label of the built width.

Architecture mirrors operators/viewport_hud.py deliberately: a
permanent draw handler plus an addon-keymap click operator that
PASS_THROUGHs anything that isn't a label hit, so selection and other
tools are untouched and no persistent modal blocks Blender's autosave.
The label list is recomputed on click rather than cached, so draw and
hit-test can never drift apart. Cage geometry is read through
split_preview's stale-matrix-safe helpers (_cage_dims / _world_matrix),
which stay valid for cages created while hidden.
"""

import bpy
import blf
import gpu
from mathutils import Vector
from bpy_extras import view3d_utils

from ... import units
from ... import hb_placement
from ...hb_gpu_draw import get_visible_window_bounds
from ...hb_types import GeoNodeCutpart
from . import types_face_frame
from . import split_preview
from .operators import ops_part_commands

# ---- Style -------------------------------------------------------------

FONT_SIZE       = 12
PAD_X           = 6
PAD_Y           = 4
LABEL_BG        = (0.13, 0.13, 0.14, 0.85)
LABEL_BG_DIM    = (0.13, 0.13, 0.14, 0.45)
LABEL_BORDER    = (1.0, 1.0, 1.0, 0.25)
EDIT_BG         = (0.20, 0.43, 0.70, 0.95)   # matches HUD active blue
TEXT_COLOR      = (0.95, 0.95, 0.95, 1.0)
TEXT_COLOR_DIM  = (0.95, 0.95, 0.95, 0.45)
EDIT_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)

# Characters accepted by the typed-distance grammar (parse_typed_distance):
# digits, decimal point, fractions, feet/inch marks, embedded spaces.
_INPUT_CHARS = set("0123456789./-'\" ")

# ---- Module state -------------------------------------------------------

_draw_handle = None
_shutdown = False
# Active edit: {'name': object name, 'kind': 'BAY'|'OPENING',
#               'typed': str} or None. Written by the edit modal, read
# by the draw handler so the edited label renders as an input field.
_edit = None
_addon_keymaps = []


# ---- Typed-distance parsing (borrowed from PlacementMixin) --------------
# parse_typed_distance and its helpers only touch self via each other,
# so lending them to a tiny holder class reuses the exact placement
# grammar without dragging in the placement state machine.

class _DistanceParser:
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


# ---- Gating -------------------------------------------------------------

def _active_mode(context):
    """'Cabinets' / 'Bays' / 'Openings' / 'Face Frame' when the overlay
    should draw, else None. Mirrors the HUD's gating: real room scene,
    FACE FRAME tab, selection mode enabled and set to an overlay mode."""
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'FACE FRAME':
        return None
    ff = getattr(scene, 'hb_face_frame', None)
    if ff is None or not getattr(ff, 'face_frame_selection_mode_enabled', False):
        return None
    mode = getattr(ff, 'face_frame_selection_mode', '')
    return (mode if mode in ('Cabinets', 'Bays', 'Openings', 'Face Frame')
            else None)


def _sizes_scope(context):
    """Size-label scope from the scene prop: 'ALL', 'SELECTED' (labels
    only for cages in the current selection), or 'OFF'."""
    ff = getattr(context.scene, 'hb_face_frame', None)
    return getattr(ff, 'selection_mode_sizes_scope', 'ALL')


def _sizes_shown(context):
    return _sizes_scope(context) != 'OFF'


def _selected_label_names(context):
    """Object names eligible for labels in SELECTED scope: every
    selected object (plus the active one) and its ancestor chain.
    Ancestors are included so clicking any part of a cabinet keeps the
    labels that target an ENCLOSING cage - the Cabinets-mode W/H/D
    target the root cage, which is never the clicked object itself."""
    names = set()
    objs = list(getattr(context, 'selected_objects', ()) or ())
    act = getattr(context, 'active_object', None)
    if act is not None and act not in objs:
        objs.append(act)
    for obj in objs:
        node = obj
        while node is not None:
            names.add(node.name)
            node = node.parent
    return names


# ---- Sizes toggle pill ----------------------------------------------------
# Drawn in the slot the HUD's second row occupies for the grab toggles in
# other modes (that row is empty in Bays / Openings, so nothing collides).
# In Face Frame mode the grab toggle DOES occupy row two, so the pill
# drops one more row there.
# Constants mirror operators/viewport_hud.py so the pill sits flush with
# the HUD without importing its layout.

_HUD_MARGIN_Y = 12
_HUD_BTN_H = 24
_HUD_ROW_GAP = 6
def _toggle_label(context):
    """Pill text reflects the scope cycle (All -> Selected -> Off)."""
    scope = _sizes_scope(context)
    if scope == 'ALL':
        return "Sizes: All"
    if scope == 'SELECTED':
        return "Sizes: Sel"
    return "Sizes"


def _toggle_rect(context, area):
    """Region-local rect for the Sizes pill: centered, one HUD row
    below the selection-mode picker (two below in the modes where a
    grab toggle owns row two - all of them, now that Bays and Openings
    have grab commands; kept mode-driven so a future toggle-less mode
    reclaims the row)."""
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    x_min, x_max, _y_min, y_max = get_visible_window_bounds(area)
    blf.size(0, FONT_SIZE * s)
    w = blf.dimensions(0, _toggle_label(context))[0] + 24 * s
    h = _HUD_BTN_H * s
    row1_y = y_max - _HUD_MARGIN_Y * s - h
    rows_down = (2 if _active_mode(bpy.context)
                 in ('Cabinets', 'Bays', 'Openings', 'Face Frame') else 1)
    y = row1_y - rows_down * (h + _HUD_ROW_GAP * s)
    x = x_min + ((x_max - x_min) - w) / 2.0
    return (x, y, w, h)


# ---- Label collection ----------------------------------------------------

def _iter_cabinet_roots(scene):
    for obj in scene.objects:
        if obj.get(types_face_frame.TAG_CABINET_CAGE):
            yield obj


def _iter_bay_cages(cabinet):
    for child in cabinet.children:
        if child.get(types_face_frame.TAG_BAY_CAGE):
            yield child


def _iter_opening_cages(node):
    """Leaf opening cages under a bay, walking through split nodes."""
    for child in node.children:
        if child.get(types_face_frame.TAG_OPENING_CAGE):
            yield child
        elif child.get(types_face_frame.TAG_SPLIT_NODE):
            yield from _iter_opening_cages(child)


def _opening_height_editable(opening):
    """An opening's height is a real degree of freedom only when its
    parent is an H-split (size = span along Z). Bay-root openings and
    V-split children get their height from the bay / cabinet."""
    parent = opening.parent
    if parent is None or not parent.get(types_face_frame.TAG_SPLIT_NODE):
        return False
    return getattr(parent.face_frame_split, 'axis', 'H') == 'H'


def _iter_face_frame_parts(cabinet):
    """Face-frame members under a cabinet root -- the same hb_part_role
    rule Face Frame selection mode highlights (stiles, rails, bay
    splitters). Conditional parts the recalc has parked (hide_render)
    are skipped, matching Parts mode."""
    for child in cabinet.children_recursive:
        if child.hide_render:
            continue
        if child.get('hb_part_role') in types_face_frame.FACE_FRAME_PART_ROLES:
            yield child


def _cabinet_shown(cabinet, space=None):
    """False when the cabinet is hidden in the viewport (wall hidden with
    its children, subtree hidden, isolate / local view, collection off) so
    its labels vanish - and stop catching clicks - with it. Mirrors the
    closet overlay's _starter_shown. The root cage can't carry this test
    (it is hide_viewport=True by design even when the cabinet is fully on
    screen), so probe a structural member that is always visible when the
    cabinet is: the first face-frame part (stiles are never design-hidden;
    recalc-parked parts carry hide_render and are already skipped). Leg
    products and other cabinets with NO face-frame roles fall back to the
    first real mesh part - cages are excluded (their hide flags are
    selection-mode state, not product visibility) and so are 2D
    annotations (they can live outside the view layer)."""
    probe = next(_iter_face_frame_parts(cabinet), None)
    if probe is None:
        for child in cabinet.children_recursive:
            if child.type != 'MESH' or child.hide_render:
                continue
            if child.get('IS_GEONODE_CAGE') or child.get('IS_2D_ANNOTATION'):
                continue
            probe = child
            break
    if probe is None:
        return True
    try:
        if space is not None and getattr(space, 'type', '') == 'VIEW_3D':
            return probe.visible_get(viewport=space)
        return probe.visible_get()
    except Exception:
        return True


def _part_anchor_world(part):
    """World-space centre of a member's bounding box. Unlike cages, parts
    are real built meshes, so bound_box is authoritative."""
    bb = part.bound_box
    centre = Vector(((bb[0][0] + bb[6][0]) / 2.0,
                     (bb[0][1] + bb[6][1]) / 2.0,
                     (bb[0][2] + bb[6][2]) / 2.0))
    return part.matrix_world @ centre


def _label_anchor_world(cage):
    """World-space centre of the cage's front face (local Y = 0 plane).
    Uses split_preview's stale-matrix-safe world matrix so cages built
    while hidden still land on the cabinet."""
    dim_x, dim_z = split_preview._cage_dims(cage)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cage)
    return mw @ Vector((dim_x / 2.0, -0.003, dim_z / 2.0))


def _anchor_world(cage, fx, fz):
    """World point on a cage's front face at fractional X / Z. Same
    stale-matrix-safe readers as _label_anchor_world."""
    dim_x, dim_z = split_preview._cage_dims(cage)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cage)
    return mw @ Vector((dim_x * fx, -0.003, dim_z * fz))


def _root_anchor_world(cabinet, fx, fz):
    """World point on the cabinet's FRONT plane at fractional X / Z.
    A cabinet ROOT's local Y = 0 plane is its BACK (against the wall),
    so the front sits at -depth; bay cages need no such offset because
    their origin already sits on the front plane (see the BAY_H/BAY_D
    anchors in compute_labels). Keeps cabinet-mode labels on the same
    plane as bay-mode labels."""
    dim_x, dim_z = split_preview._cage_dims(cabinet)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cabinet)
    depth = cabinet.face_frame_cabinet.depth
    return mw @ Vector((dim_x * fx, -depth - 0.003, dim_z * fz))


def _cabinet_label_targets(cabinet):
    """(kind, anchor, value, prefix) for a cabinet root's three dims.
    Mirrors the closet starter overlay: each label sits where its edit
    ACTS - H at the top edge (the edge that moves), W dead-center of
    the front face, D at the bottom-front edge. All three anchor on the
    cabinet's FRONT plane (via _root_anchor_world) to match bay-mode
    labels. Values come from the SAME props a commit writes
    (face_frame_cabinet.width / height / depth) so typing back the
    shown value is a no-op."""
    props = cabinet.face_frame_cabinet
    return [
        ('CAB_H', _root_anchor_world(cabinet, 0.5, 1.0), props.height, "H "),
        ('CAB_W', _root_anchor_world(cabinet, 0.5, 0.5), props.width, "W "),
        ('CAB_D', _root_anchor_world(cabinet, 0.5, 0.0), props.depth, "D "),
    ]


def compute_labels(context, region, rv3d):
    """[(obj_name, kind, editable, locked, rect, text)] for every label
    currently on screen. rect is (x, y, w, h) region-local. ``locked``
    is the bay/opening hold flag (user-typed value held during
    redistribution); locked labels carry a bullet marker so users can
    see which values are pinned vs auto-calculated. Shared by the draw
    handler and the click operators so hits can't drift from pixels."""
    mode = _active_mode(context)
    if mode is None or rv3d is None:
        return []
    if not _sizes_shown(context):
        # Sizes toggled off: no labels drawn or clickable; the Sizes
        # pill itself is handled separately by the draw / click paths.
        return []
    scope = _sizes_scope(context)
    sel_names = (_selected_label_names(context)
                 if scope == 'SELECTED' else None)
    scene = context.scene
    unit_settings = scene.unit_settings
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    font_sz = FONT_SIZE * s
    blf.size(0, font_sz)

    labels = []
    space = getattr(context, 'space_data', None)
    for cabinet in _iter_cabinet_roots(scene):
        if not _cabinet_shown(cabinet, space):
            continue
        # Displayed values come from the SAME properties a commit writes
        # (face_frame_bay.width / face_frame_opening.size), never the cage
        # dims -- the two differ (frame overlaps), and typing back the
        # number you can see must be a no-op. Non-editable openings have
        # a meaningless size prop (root/V-child), so those read-only
        # labels show the built cage height instead.
        if mode == 'Cabinets':
            # Corner cabinets size through their own corner-section
            # props; skip them rather than show W/H/D labels that
            # wouldn't commit sensibly.
            if getattr(cabinet.face_frame_cabinet,
                       'corner_type', 'NONE') != 'NONE':
                continue
            targets = [
                (cabinet, kind, True, False, value, prefix, anchor)
                for kind, anchor, value, prefix
                in _cabinet_label_targets(cabinet)
            ]
        elif mode == 'Bays':
            targets = []
            for bay in _iter_bay_cages(cabinet):
                bp = bay.face_frame_bay
                targets.append((bay, 'BAY', True, bp.unlock_width,
                                bp.width, "W ", None))
                # Height / depth always display bp.height / bp.depth --
                # the exact values the solver reads and a commit writes
                # (the sidebar shows the same numbers behind its lock
                # icons), so typing back the shown value is a no-op.
                # While locked the system keeps them in sync; the
                # bullet marks user-pinned (unlocked) values. Anchors:
                # a face-frame bay cage's origin already sits at its
                # front plane (unlike closet bay cages, origin at the
                # BACK), so _anchor_world's -0.003 is the whole front
                # offset.
                targets.append((bay, 'BAY_H', True, bp.unlock_height,
                                bp.height, "H ",
                                _anchor_world(bay, 0.5, 1.0)))
                targets.append((bay, 'BAY_D', True, bp.unlock_depth,
                                bp.depth, "D ",
                                _anchor_world(bay, 0.5, 0.0)))
        elif mode == 'Openings':
            targets = []
            for bay in _iter_bay_cages(cabinet):
                for op in _iter_opening_cages(bay):
                    editable = _opening_height_editable(op)
                    props = op.face_frame_opening
                    value = (props.size if editable
                             else split_preview._cage_dims(op)[1])
                    targets.append((op, 'OPENING', editable,
                                    editable and props.unlock_size,
                                    value, "", None))
        else:
            # Face Frame: member widths. Editable labels read
            # _get_current_width -- the same per-role props the Set Width
            # dialog writes -- so typing back the shown value is a no-op.
            targets = []
            for part in _iter_face_frame_parts(cabinet):
                role = part.get('hb_part_role')
                editable = role in ops_part_commands._ROLES_WITH_WIDTH
                try:
                    if editable:
                        value = ops_part_commands._get_current_width(
                            part, role, cabinet)
                        locked = types_face_frame.part_width_is_unlocked(part)
                    else:
                        # Between-bay mid rails have no width command;
                        # show the built width read-only.
                        value = GeoNodeCutpart(part).get_input('Width')
                        locked = False
                except Exception:
                    continue
                targets.append((part, 'PART', editable, locked,
                                value, "", None))
        # SELECTED scope: keep only labels whose cage is part of the
        # current selection. The click handlers hit-test against this
        # same list, so filtered labels are not clickable either.
        if sel_names is not None:
            targets = [t for t in targets if t[0].name in sel_names]
        for cage, kind, editable, locked, value, prefix, anchor in targets:
            if anchor is None:
                anchor = (_part_anchor_world(cage) if kind == 'PART'
                          else _label_anchor_world(cage))
            if anchor is None:
                continue
            pt = view3d_utils.location_3d_to_region_2d(region, rv3d, anchor)
            if pt is None:
                continue
            text = prefix + units.unit_to_string(unit_settings, value)
            if locked:
                # Pinned (user-typed, held during redistribution). The
                # marker doubles as the affordance for "this one can be
                # reset to auto" (right-click, or X / 0 while editing).
                text = "• " + text
            tw, th = blf.dimensions(0, text)
            w = tw + 2 * PAD_X * s
            h = th + 2 * PAD_Y * s
            rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
            # Skip labels fully outside the region.
            if rect[0] + w < 0 or rect[0] > region.width:
                continue
            if rect[1] + h < 0 or rect[1] > region.height:
                continue
            labels.append((cage.name, kind, editable, locked, rect, text))
    return labels


# ---- Draw handler ---------------------------------------------------------

def _draw_label_rect(shader, rect, bg):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    from gpu_extras.batch import batch_for_shader
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
    batch_for_shader(
        shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def _draw_toggle_pill(shader, context, area, font_sz, s):
    """The Sizes show/hide pill -- HUD-styled, active blue while labels
    are shown."""
    rect = _toggle_rect(context, area)
    on = _sizes_shown(context)
    label = _toggle_label(context)
    _draw_label_rect(shader, rect, EDIT_BG if on else LABEL_BG)
    blf.size(0, font_sz)
    blf.color(0, *(EDIT_TEXT_COLOR if on else TEXT_COLOR))
    tw, th = blf.dimensions(0, label)
    blf.position(0, rect[0] + (rect[2] - tw) / 2.0,
                 rect[1] + (rect[3] - th) / 2.0, 0)
    blf.draw(0, label)


def _draw():
    """Permanent POST_PIXEL callback; cheap no-op outside the two modes."""
    if _shutdown:
        return
    context = bpy.context
    area = context.area
    region = context.region
    if area is None or area.type != 'VIEW_3D':
        return
    if region is None or region.type != 'WINDOW':
        return
    if _active_mode(context) is None:
        return
    labels = compute_labels(context, region, context.region_data)

    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    font_sz = FONT_SIZE * s
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    _draw_toggle_pill(shader, context, area, font_sz, s)
    for name, kind, editable, _locked, rect, text in labels:
        editing = (_edit is not None and _edit['name'] == name
                   and _edit['kind'] == kind)
        if editing:
            # In-progress typed value with a text cursor; empty buffer
            # shows the current value so the user sees what Enter keeps.
            typed = _edit['typed']
            shown = (typed + "|") if typed else text
            blf.size(0, font_sz)
            tw, th = blf.dimensions(0, shown)
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


# ---- Commit --------------------------------------------------------------

def _commit(obj, kind, value):
    """Write the typed value through the sidebar's own property paths."""
    if kind in ('CAB_W', 'CAB_H', 'CAB_D'):
        # Same props the Cabinet Properties dialog edits; the update
        # callbacks run the recalc and bay redistribution.
        attr = {'CAB_W': 'width', 'CAB_H': 'height', 'CAB_D': 'depth'}[kind]
        setattr(obj.face_frame_cabinet, attr, value)
        return True
    if kind == 'BAY':
        # Fires _update_bay_width: auto-locks the bay + recalcs so the
        # cabinet's other unlocked bays redistribute around it.
        obj.face_frame_bay.width = value
        return True
    if kind == 'BAY_H':
        # Unlock-first: bay height is cabinet-driven until the flag is
        # set (the sidebar greys the field behind a lock icon).
        bp = obj.face_frame_bay
        if not bp.unlock_height:
            bp.unlock_height = True
        bp.height = value
        return True
    if kind == 'BAY_D':
        bp = obj.face_frame_bay
        if not bp.unlock_depth:
            bp.unlock_depth = True
        bp.depth = value
        return True
    if kind == 'OPENING':
        props = obj.face_frame_opening
        # Hold-first so the redistribution triggered by the size write
        # keeps the typed height (mirrors the Split Opening dialog).
        if not props.unlock_size:
            props.unlock_size = True
        props.size = value
        return True
    if kind == 'PART':
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None or role not in ops_part_commands._ROLES_WITH_WIDTH:
            return False
        name = obj.name
        # Same sequence as the Set Width dialog: flip the unlock first so
        # a later style apply keeps the value. For bay-internal splitters
        # the flag write can recalc + rebuild the part, so re-resolve by
        # name (stable across recalc) before fanning out.
        ops_part_commands._flip_unlock_for_role(obj, role, root)
        obj = bpy.data.objects.get(name)
        if obj is None:
            return False
        with types_face_frame.suspend_recalc():
            ops_part_commands._fan_out_value(obj, role, root, value)
        return True
    return False


def _reset_to_auto(obj, kind):
    """Clear the bay's / opening's hold flag so redistribution owns the
    value again (the flag write's update callback runs the recalc). The
    inverse of the auto-lock a typed edit applies. No-op when already
    auto."""
    if kind == 'BAY':
        if obj.face_frame_bay.unlock_width:
            obj.face_frame_bay.unlock_width = False
            return True
        return False
    if kind == 'BAY_H':
        if obj.face_frame_bay.unlock_height:
            obj.face_frame_bay.unlock_height = False
            return True
        return False
    if kind == 'BAY_D':
        if obj.face_frame_bay.unlock_depth:
            obj.face_frame_bay.unlock_depth = False
            return True
        return False
    if kind == 'OPENING':
        props = obj.face_frame_opening
        if props.unlock_size:
            props.unlock_size = False
            return True
        return False
    if kind == 'PART':
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None or role not in ops_part_commands._ROLES_WITH_WIDTH:
            return False
        if not types_face_frame.part_width_is_unlocked(obj):
            return False
        # _lock_for_role clears the per-role unlock flag(s); each flag's
        # own update callback reverts the width to the default + recalcs.
        ops_part_commands._lock_for_role(obj, role, root)
        return True
    return False


# ---- Edit modal ------------------------------------------------------------

class hb_face_frame_OT_edit_dim_label(bpy.types.Operator):
    """Type a new value for the clicked bay-width / opening-height /
    part-width label. Enter commits, Esc / right-click / click-away
    cancels."""
    bl_idname = "hb_face_frame.edit_dim_label"
    bl_label = "Edit Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    kind: bpy.props.EnumProperty(
        items=[('BAY', "Bay Width", ""), ('OPENING', "Opening Height", ""),
               ('PART', "Part Width", ""),
               ('CAB_W', "Cabinet Width", ""),
               ('CAB_H', "Cabinet Height", ""),
               ('CAB_D', "Cabinet Depth", ""),
               ('BAY_H', "Bay Height", ""),
               ('BAY_D', "Bay Depth", "")],
        options={'HIDDEN'})  # type: ignore

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
            # State cleared externally or claimed by a newer edit --
            # die quietly WITHOUT _finish, which would stomp the other
            # edit's module state / text cursor.
            return {'CANCELLED'}

        # Navigation stays live so the user can orbit / zoom mid-edit;
        # labels reproject every draw and the edit is keyed by object.
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
                # Enter on an empty buffer keeps the current value.
                self._finish(context)
                return {'FINISHED'}
            if obj is not None and value == 0.0:
                # Typing 0 means "back to auto": clear the hold so
                # redistribution recalculates this bay / opening.
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
            # Reset to auto-calculated, mirroring the 0-Enter path.
            obj = bpy.data.objects.get(self.target_name)
            self._finish(context)
            if obj is not None:
                _reset_to_auto(obj, self.kind)
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            # Click-away cancels the edit and consumes the press --
            # predictable, and avoids racing a second edit modal
            # spawned from the same event.
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

        # Swallow everything else (keyboard shortcuts would surprise
        # mid-edit); harmless keys just do nothing.
        return {'RUNNING_MODAL'}


# ---- Click routing (addon keymap, mirrors viewport_hud) --------------------

class hb_face_frame_OT_dim_label_click(bpy.types.Operator):
    """Routes a viewport left-press to overlay labels. A press on an
    editable label starts the edit modal and is consumed; anything else
    passes through untouched."""
    bl_idname = "hb_face_frame.dim_label_click"
    bl_label = "Dimension Label Click"
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
            # An edit is already running; its own modal handles this press.
            return {'PASS_THROUGH'}
        # HUD widgets keep priority over labels that happen to sit
        # underneath them.
        try:
            from ...operators import viewport_hud
            if viewport_hud.click_hits_widget(
                    context, context.area,
                    event.mouse_region_x, event.mouse_region_y):
                return {'PASS_THROUGH'}
        except Exception:
            pass
        mx, my = event.mouse_region_x, event.mouse_region_y
        # Sizes pill first -- it stays clickable while labels are hidden.
        tx, ty, tw, th = _toggle_rect(context, context.area)
        if tx <= mx <= tx + tw and ty <= my <= ty + th:
            ff = context.scene.hb_face_frame
            ff.selection_mode_sizes_scope = {
                'ALL': 'SELECTED', 'SELECTED': 'OFF'}.get(
                    ff.selection_mode_sizes_scope, 'ALL')
            context.area.tag_redraw()
            return {'FINISHED'}
        for name, kind, editable, _locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if not editable:
                return {'PASS_THROUGH'}
            bpy.ops.hb_face_frame.edit_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


class hb_face_frame_OT_dim_label_reset(bpy.types.Operator):
    """Right-click on a pinned (•) label resets that bay width / opening
    height to auto-calculated. Presses anywhere else -- including on
    unpinned labels, which have nothing to reset -- pass through to the
    normal context menu / selection."""
    bl_idname = "hb_face_frame.dim_label_reset"
    bl_label = "Reset Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_face_frame_OT_dim_label_click.poll(context)

    def invoke(self, context, event):
        if _edit is not None:
            # The edit modal owns right-click (cancel) while it runs.
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


# ---- Lifecycle --------------------------------------------------------------

classes = (
    hb_face_frame_OT_edit_dim_label,
    hb_face_frame_OT_dim_label_click,
    hb_face_frame_OT_dim_label_reset,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        hb_face_frame_OT_dim_label_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        hb_face_frame_OT_dim_label_reset.bl_idname, 'RIGHTMOUSE', 'PRESS',
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
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
