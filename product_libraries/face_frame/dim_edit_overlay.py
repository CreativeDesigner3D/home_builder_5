"""Editable dimension overlay for Cabinet / Bay / Opening / Face Frame
selection modes.

While the face-frame selection mode is 'Cabinets', 'Bays', 'Openings'
or 'Face Frame', a POST_PIXEL draw handler paints a value label on
every cabinet root (W / H / D, like the closet starter overlay), every
bay (its width), every leaf opening (its height), or every face-frame
member (its width -- stiles, rails, bay splitters) of every face-frame
cabinet in the viewport. Every label names its dimension -- H 19.5",
W 1.5" -- so a number on a part says what it measures. Clicking a label starts a short-lived modal that captures
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
from ...hb_types import GeoNodeCage, GeoNodeCutpart
from . import types_face_frame
from . import split_preview
from . import appliance_panels
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
DIM_LINE_COLOR     = (0.90, 0.90, 0.90, 0.80)
DIM_LINE_COLOR_DIM = (0.90, 0.90, 0.90, 0.35)
TICK_PX         = 5
# Height dims run up the cage's left side this far in (capped at a
# quarter of the width for narrow cages).
HEIGHT_DIM_INSET = 0.0762

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


def _appliance_target(context):
    """The panelled appliance the active object belongs to, when its
    labels should draw: a room scene, sizes not switched off, and a
    panelled appliance under the cursor's selection.

    Deliberately NOT gated on the face-frame selection mode the cabinet
    labels use. An appliance has no bays, openings or frame members, and
    its panels are edited from the panel tab, which asks only that the
    appliance be selected -- so the labels on the model appear on the
    same terms as the tab rather than depending on which product tab
    the room happens to be showing.
    """
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    if not _sizes_shown(context):
        return None
    obj = getattr(context, 'object', None)
    while obj is not None:
        if obj.get('IS_APPLIANCE'):
            props = getattr(obj, 'appliance_panels', None)
            return obj if (props is not None and len(props.sections)) else None
        obj = obj.parent
    return None


def _sizes_scope(context):
    """Size-label scope from the scene prop: 'ALL', 'SELECTED_CABINET'
    (every label on a cabinet the selection belongs to), 'SELECTED'
    (labels only for cages in the current selection), or 'OFF'."""
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


# The Sizes scope control lives in the viewport HUD (see
# operators/viewport_hud._SizesButton). It used to be drawn here from a
# private copy of the HUD's layout constants plus a guess at which row
# was free -- a guess that went stale as soon as the HUD's rows changed.

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


def _height_dim_fx(cage):
    """Fractional X of a cage's height dim line (HEIGHT_DIM_INSET in
    from its left side)."""
    dim_x, _dim_z = split_preview._cage_dims(cage)
    if dim_x <= 0.0:
        return 0.5
    return min(HEIGHT_DIM_INSET / dim_x, 0.25)


def _root_depth_points(cabinet):
    """(front, middle, back) world points of the cabinet's depth dim,
    across the top at mid width. None when the cage has no size."""
    dim_x, dim_z = split_preview._cage_dims(cabinet)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cabinet)
    depth = cabinet.face_frame_cabinet.depth
    return (mw @ Vector((dim_x / 2.0, -depth, dim_z)),
            mw @ Vector((dim_x / 2.0, -depth / 2.0, dim_z)),
            mw @ Vector((dim_x / 2.0, 0.0, dim_z)))


def _bay_depth_points(bay):
    """(front, middle, back) world points of a bay's depth dim, across
    the top of the bay at mid width. Measured in the cabinet root's
    frame -- the bay depth runs from the face frame's front (root
    Y = -depth) to the cabinet back (root Y = 0), while the bay cage
    itself starts behind the frame."""
    cabinet = bay.parent
    top = _anchor_world(bay, 0.5, 1.0)
    if cabinet is None or top is None:
        return None
    cmw = split_preview._world_matrix(cabinet)
    local = cmw.inverted() @ top
    depth = bay.face_frame_bay.depth
    return tuple(cmw @ Vector((local.x, y, local.z))
                 for y in (-depth, -depth / 2.0, 0.0))


def _cabinet_label_targets(cabinet):
    """(kind, anchor, value, prefix) for a cabinet root's three dims.
    Each label sits at the middle of its dimension line (see
    _dim_line_world): W across the middle of the front face, H up the
    left side, D front to back across the top. W and H anchor on the
    cabinet's FRONT plane (via _root_anchor_world) to match bay-mode
    labels. Values come from the SAME props a commit writes
    (face_frame_cabinet.width / height / depth) so typing back the
    shown value is a no-op."""
    props = cabinet.face_frame_cabinet
    depth_pts = _root_depth_points(cabinet)
    return [
        ('CAB_H', _root_anchor_world(cabinet, _height_dim_fx(cabinet), 0.5),
         props.height, "H "),
        ('CAB_W', _root_anchor_world(cabinet, 0.5, 0.5), props.width, "W "),
        ('CAB_D', depth_pts[1] if depth_pts else None, props.depth, "D "),
    ]


def _part_width_line(part, value):
    """World endpoints across a face-frame member's width: through its
    bounding-box centre along whichever local axis measures ``value``
    (stiles are wide in X, rails in Z)."""
    bb = part.bound_box
    lo = Vector((min(c[0] for c in bb), min(c[1] for c in bb),
                 min(c[2] for c in bb)))
    hi = Vector((max(c[0] for c in bb), max(c[1] for c in bb),
                 max(c[2] for c in bb)))
    centre = (lo + hi) / 2.0
    rot = part.matrix_world.to_3x3()
    best = None
    for axis in range(3):
        half = Vector((0.0, 0.0, 0.0))
        half[axis] = (hi[axis] - lo[axis]) / 2.0
        err = abs((rot @ half).length * 2.0 - value)
        if best is None or err < best[0]:
            best = (err, half)
    if best is None or best[1].length < 1e-6:
        return None
    mw = part.matrix_world
    return mw @ (centre - best[1]), mw @ (centre + best[1])


def _dim_line_world(obj, kind, value):
    """(a, b) world endpoints of the dimension line a label sits on, or
    None for labels drawn without one (appliance panel faces)."""
    if kind == 'CAB_W':
        a = _root_anchor_world(obj, 0.0, 0.5)
        b = _root_anchor_world(obj, 1.0, 0.5)
    elif kind == 'CAB_H':
        fx = _height_dim_fx(obj)
        a = _root_anchor_world(obj, fx, 0.0)
        b = _root_anchor_world(obj, fx, 1.0)
    elif kind == 'CAB_D':
        pts = _root_depth_points(obj)
        if pts is None:
            return None
        a, b = pts[0], pts[2]
    elif kind == 'BAY':
        a = _anchor_world(obj, 0.0, 0.5)
        b = _anchor_world(obj, 1.0, 0.5)
    elif kind == 'BAY_D':
        pts = _bay_depth_points(obj)
        if pts is None:
            return None
        a, b = pts[0], pts[2]
    elif kind == 'BAY_H':
        fx = _height_dim_fx(obj)
        a = _anchor_world(obj, fx, 0.0)
        b = _anchor_world(obj, fx, 1.0)
    elif kind == 'OPENING':
        a = _anchor_world(obj, 0.5, 0.0)
        b = _anchor_world(obj, 0.5, 1.0)
    elif kind == 'PART':
        return _part_width_line(obj, value)
    else:
        return None
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


# ---- Appliance panels ----------------------------------------------------
# A panelled appliance carries the same kind of run a cabinet front does:
# faces that hold a size, and faces that share whatever is left. So its
# faces get labels on the same terms -- the height on each face, the
# width over each column -- and a typed value holds itself, exactly as
# it does in the panel editor.
#
# Gated on SELECTION rather than the Sizes scope's ALL: a fridge is a
# wall of faces, and labelling every one of them on every appliance in
# the room while you work on something else is noise. Selected is also
# the gate the PANELS tab uses, so the model and the tab light up
# together.

def _iter_panelled_appliances(scene):
    for obj in scene.objects:
        if not obj.get('IS_APPLIANCE'):
            continue
        props = getattr(obj, 'appliance_panels', None)
        if props is not None and len(props.sections):
            yield obj


def _ap_front_parts(appliance):
    """{section index: built front} -- a face nobody can see gets no
    label, which is also what keeps a stale index off the screen."""
    out = {}
    for child in appliance.children:
        if not child.get(appliance_panels.TAG_FRONT):
            continue
        index = child.get('AP_SECTION_INDEX')
        if index is not None:
            out[int(index)] = child
    return out


def _ap_anchor(appliance, dims, box, fz):
    """A world point on the panel plane of `box` (a solved face rect) at
    fractional height `fz`. Read off the appliance's own matrix rather
    than the part's bounding box, so it stays right whichever way the
    appliance is turned."""
    dim_x, dim_y, dim_z = dims
    x0, x1, z0, z1 = box[:4]
    return appliance.matrix_world @ Vector(
        ((x0 + x1) / 2.0, -dim_y - 0.01, z0 + (z1 - z0) * fz))


def _ap_targets(appliance, unit_settings):
    """(part, kind, editable, locked, value, prefix, anchor) for one
    appliance's faces, and for its columns when it has more than one."""
    props = appliance.appliance_panels
    cage = GeoNodeCage(appliance)
    dims = (cage.get_input('Dim X') or 0.0, cage.get_input('Dim Y') or 0.0,
            cage.get_input('Dim Z') or 0.0)
    if dims[0] <= 0.0 or dims[2] <= 0.0:
        return []
    try:
        faces = appliance_panels.solve(props, dims[0], dims[2])[0]
    except Exception:
        return []
    parts = _ap_front_parts(appliance)
    targets = []
    # The height on each face: what it holds, or what it currently
    # works out to -- typing either back holds that size, which is what
    # the editor's Hold chip does.
    for index, box in faces.items():
        part = parts.get(index)
        if part is None:
            continue
        sec = props.sections[index]
        value = sec.height if sec.height_hold else (box[3] - box[2])
        targets.append((part, 'AP_FACE', True, sec.height_hold, value, "H ",
                        _ap_anchor(appliance, dims, box, 0.5)))
    targets.extend(_ap_gap_targets(appliance, props, dims, faces, parts))
    # The width over each column, on its top face, where a column's
    # width is a thing the run has more than one of.
    if len(props.columns) > 1:
        for ci, column in enumerate(props.columns):
            top = max((i for i, s in enumerate(props.sections)
                       if s.column == ci and i in faces and i in parts),
                      key=lambda i: faces[i][3], default=None)
            if top is None:
                continue
            box = faces[top]
            value = column.width if column.width_hold else (box[1] - box[0])
            targets.append((parts[top], 'AP_COL', True, column.width_hold,
                            value, "W ",
                            _ap_anchor(appliance, dims, box, 0.92)))
    return targets


# The run's gaps, labelled where they are: the four around the outside,
# the one between columns, and the one between stacked faces. The last
# two are ONE size each in the model, so every gap of a kind reads and
# writes the same number -- typing into the gap you are looking at is
# just the nearest way to reach it.
_GAP_PROP = {
    'AP_GAP_T': 'reveal_top',
    'AP_GAP_B': 'reveal_bottom',
    'AP_GAP_L': 'reveal_left',
    'AP_GAP_R': 'reveal_right',
    'AP_GAP_C': 'column_gap',
    'AP_GAP_S': 'section_gap',
}
# The five that can hand their size back to the one every gap follows;
# the section gap IS that number for the inside of the run.
_GAP_AUTO = set(_GAP_PROP) - {'AP_GAP_S'}


def _gap_value(props, kind):
    """What a gap measures now, following the run's single size when the
    edge has not been given one of its own."""
    if kind == 'AP_GAP_C':
        return appliance_panels.column_gap(props)
    if kind == 'AP_GAP_S':
        return props.section_gap
    edge = _GAP_PROP[kind].split('_', 1)[1]
    return appliance_panels.reveal(props, edge)


def _gap_is_own(props, kind):
    """Whether this gap carries its own size rather than following."""
    if kind not in _GAP_AUTO:
        return False
    return getattr(props, _GAP_PROP[kind], -1.0) >= 0.0


def _ap_gap_targets(appliance, props, dims, faces, parts):
    """A label in each gap of the run. Positions come from the solved
    faces, so a gap is labelled where it actually opens up."""
    if not faces:
        return []
    dim_x, dim_y, dim_z = dims
    xs0 = min(b[0] for b in faces.values())
    xs1 = max(b[1] for b in faces.values())
    zs0 = min(b[2] for b in faces.values())
    zs1 = max(b[3] for b in faces.values())
    mid_x, mid_z = (xs0 + xs1) / 2.0, (zs0 + zs1) / 2.0
    kick = max(0.0, props.toe_kick)

    def target(kind, x, z):
        box = (x, x, z, z)      # a point; _ap_anchor reads the centre
        return (appliance, kind, True, _gap_is_own(props, kind),
                _gap_value(props, kind), "",
                _ap_anchor(appliance, dims, box, 0.5))

    out = [target('AP_GAP_T', mid_x, (zs1 + dim_z) / 2.0),
           target('AP_GAP_B', mid_x, (kick + zs0) / 2.0),
           target('AP_GAP_L', xs0 / 2.0, mid_z),
           target('AP_GAP_R', (xs1 + dim_x) / 2.0, mid_z)]

    # Between the columns, and between the faces stacked in each.
    bands = {}
    for i, box in faces.items():
        column = props.sections[i].column
        if column < 0:
            continue
        lo, hi = bands.get(column, (box[0], box[1]))
        bands[column] = (min(lo, box[0]), max(hi, box[1]))
    ordered = [bands[c] for c in sorted(bands)]
    for (a_lo, a_hi), (b_lo, b_hi) in zip(ordered, ordered[1:]):
        if b_lo - a_hi > 1e-6:
            out.append(target('AP_GAP_C', (a_hi + b_lo) / 2.0, mid_z))
    for column in sorted(bands):
        stack = sorted((faces[i] for i, s in enumerate(props.sections)
                        if s.column == column and i in faces),
                       key=lambda b: b[2])
        centre = (bands[column][0] + bands[column][1]) / 2.0
        for lower, upper in zip(stack, stack[1:]):
            if upper[2] - lower[3] > 1e-6:
                out.append(target('AP_GAP_S', centre,
                                  (lower[3] + upper[2]) / 2.0))
    # A full-width face has the same gap above or below it, on the
    # appliance's centre line so it is not labelled once per column.
    for i, box in faces.items():
        if props.sections[i].column >= 0:
            continue
        for edge, z in ((box[3], box[3] + props.section_gap / 2.0),
                        (box[2], box[2] - props.section_gap / 2.0)):
            if zs0 < edge < zs1:
                out.append(target('AP_GAP_S', mid_x, z))
    return out


def _select_in_panel_tab(part_name):
    """Clicking a face on the model selects that face in the panel tab,
    so the picture, the model and the rows underneath are all looking at
    the same face. Silent where the tab isn't there."""
    try:
        from ...operators import appliance_panel_tab
    except ImportError:
        return
    appliance, index = _ap_section(bpy.data.objects.get(part_name))
    if appliance is not None:
        appliance_panel_tab.select(appliance, index)
        appliance_panel_tab.tag_redraw()


def _ap_shown(appliance, space=None):
    """False when the appliance is hidden, so its labels vanish -- and
    stop catching clicks -- with it. Probes a built front, the same way
    _cabinet_shown probes a frame member: the appliance root is a cage
    and carries hide flags of its own."""
    probe = next(iter(_ap_front_parts(appliance).values()), None)
    if probe is None:
        return False
    try:
        if space is not None and getattr(space, 'type', '') == 'VIEW_3D':
            return probe.visible_get(viewport=space)
        return probe.visible_get()
    except Exception:
        return True


def _ap_section(part):
    """(appliance, section index) behind a face label, or (None, -1)."""
    appliance = part.parent if part is not None else None
    index = part.get('AP_SECTION_INDEX') if part is not None else None
    if appliance is None or index is None:
        return None, -1
    props = getattr(appliance, 'appliance_panels', None)
    if props is None or not 0 <= int(index) < len(props.sections):
        return None, -1
    return appliance, int(index)


def compute_labels(context, region, rv3d, lines_out=None):
    """[(obj_name, kind, editable, locked, rect, text)] for every label
    currently on screen. When ``lines_out`` is a list, the region-space
    dimension line under each label is appended to it as
    ``(points, editable)``. rect is (x, y, w, h) region-local. ``locked``
    is the bay/opening hold flag (user-typed value held during
    redistribution); locked labels carry a bullet marker so users can
    see which values are pinned vs auto-calculated. Shared by the draw
    handler and the click operators so hits can't drift from pixels."""
    mode = _active_mode(context)
    # Either half can light up on its own: the cabinet labels follow the
    # face-frame selection mode, the appliance's follow the selection.
    if (mode is None and _appliance_target(context) is None) or rv3d is None:
        return []
    if not _sizes_shown(context):
        # Sizes toggled off: no labels drawn or clickable; the Sizes
        # pill itself is handled separately by the draw / click paths.
        return []
    scope = _sizes_scope(context)
    sel_names = (_selected_label_names(context)
                 if scope in ('SELECTED', 'SELECTED_CABINET') else None)
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

    def _emit(targets):
        """Project a product's targets and add the ones on screen. One
        copy, so a cabinet label and an appliance label can't drift
        apart in size, marker or hit rect."""
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
            if lines_out is not None:
                line = _dim_line_world(cage, kind, value)
                if line is not None:
                    pts = _project_dim_line(region, rv3d, line, s)
                    if pts:
                        lines_out.append((pts, editable))

    for cabinet in (_iter_cabinet_roots(scene) if mode is not None else ()):
        if not _cabinet_shown(cabinet, space):
            continue
        # Cabinet scope: the whole cabinet's labels once anything in it
        # is selected (sel_names carries each selected object's
        # ancestors, so the root is in it).
        if scope == 'SELECTED_CABINET' and cabinet.name not in sel_names:
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
                                _anchor_world(bay, _height_dim_fx(bay),
                                              0.5)))
                depth_pts = _bay_depth_points(bay)
                targets.append((bay, 'BAY_D', True, bp.unlock_depth,
                                bp.depth, "D ",
                                depth_pts[1] if depth_pts else None))
        elif mode == 'Openings':
            targets = []
            # Non-editable openings (bay roots / V-split children) show
            # the solver leaf's real FF opening height -- cage minus the
            # top / bottom reveals, the same number Opening Properties
            # prints. The raw cage spans the front-overlay footprint,
            # which read one overlay too tall (e.g. 28.5" for a 27.5"
            # opening). Leaf heights resolve once per cabinet; anything
            # unresolvable falls back to the raw cage height.
            leaf_h = {}
            try:
                from . import solver_face_frame as solver
                layout_ss = solver.FaceFrameLayout(cabinet)
                for bay in _iter_bay_cages(cabinet):
                    bi = bay.get('hb_bay_index')
                    if bi is None:
                        continue
                    for lf in solver.bay_openings(
                            layout_ss, bi).get('leaves', []):
                        leaf_h[lf['obj_name']] = (
                            lf['cage_dim_z'] - lf['reveal_top']
                            - lf['reveal_bottom'])
            except Exception:
                pass
            for bay in _iter_bay_cages(cabinet):
                for op in _iter_opening_cages(bay):
                    editable = _opening_height_editable(op)
                    props = op.face_frame_opening
                    value = (props.size if editable
                             else leaf_h.get(
                                 op.name,
                                 split_preview._cage_dims(op)[1]))
                    targets.append((op, 'OPENING', editable,
                                    editable and props.unlock_size,
                                    value, "H ", None))
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
                                value, "W ", None))
        # SELECTED scope: keep only labels whose cage is part of the
        # current selection. The click handlers hit-test against this
        # same list, so filtered labels are not clickable either.
        if scope == 'SELECTED':
            targets = [t for t in targets if t[0].name in sel_names]
        _emit(targets)

    # Appliance panels: the selected appliance's own faces, in every
    # mode -- an appliance has no bays, openings or frame members of its
    # own, so its faces are the only thing it could label.
    ap_names = _selected_label_names(context)
    for appliance in _iter_panelled_appliances(scene):
        if appliance.name not in ap_names:
            continue
        if not _ap_shown(appliance, space):
            continue
        _emit(_ap_targets(appliance, unit_settings))
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
    # Same two gates as compute_labels: the cabinet labels follow the
    # face-frame selection mode, a panelled appliance's follow the
    # selection, and either on its own is reason enough to draw.
    if _active_mode(context) is None and _appliance_target(context) is None:
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
        pts = [p for line, ed in dim_lines if ed == editable for p in line]
        if pts:
            shader.uniform_float(
                "color", DIM_LINE_COLOR if editable else DIM_LINE_COLOR_DIM)
            batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)
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
    if kind in _GAP_PROP:
        # The label carries the appliance itself: a gap belongs to the
        # run, not to any one face.
        props = getattr(obj, 'appliance_panels', None)
        prop = _GAP_PROP[kind]
        if props is None:
            return False
        # Asked of the RNA, not with hasattr: setting a name a property
        # group does not have succeeds silently on the Python side and
        # writes nothing, so a run from before the gaps could be set
        # apart would read as edited without changing.
        if prop not in props.bl_rna.properties:
            return False
        setattr(props, prop, value)
        return True
    if kind in ('AP_FACE', 'AP_COL'):
        # A panel size that is typed is a size that is wanted, so it
        # holds itself and the rest of the run shares what is left --
        # the same rule the panel editor's typed fields follow.
        appliance, index = _ap_section(obj)
        if appliance is None:
            return False
        props = appliance.appliance_panels
        if kind == 'AP_FACE':
            sec = props.sections[index]
            sec.height = value
            sec.height_hold = True
            return True
        column = props.sections[index].column
        if not 0 <= column < len(props.columns):
            return False
        props.columns[column].width = value
        props.columns[column].width_hold = True
        return True
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
    if kind in _GAP_AUTO:
        # Back to following the run's single gap.
        props = getattr(obj, 'appliance_panels', None)
        if props is None or getattr(props, _GAP_PROP[kind], -1.0) < 0.0:
            return False
        setattr(props, _GAP_PROP[kind], -1.0)
        return True
    if kind in ('AP_FACE', 'AP_COL'):
        # Back to sharing -- the editor's Fill chip, from the model.
        appliance, index = _ap_section(obj)
        if appliance is None:
            return False
        props = appliance.appliance_panels
        if kind == 'AP_FACE':
            if props.sections[index].height_hold:
                props.sections[index].height_hold = False
                return True
            return False
        column = props.sections[index].column
        if 0 <= column < len(props.columns) and props.columns[column].width_hold:
            props.columns[column].width_hold = False
            return True
        return False
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
               ('BAY_D', "Bay Depth", ""),
               ('AP_FACE', "Panel Height", ""),
               ('AP_COL', "Panel Column Width", ""),
               ('AP_GAP_T', "Panel Gap Top", ""),
               ('AP_GAP_B', "Panel Gap Bottom", ""),
               ('AP_GAP_L', "Panel Gap Left", ""),
               ('AP_GAP_R', "Panel Gap Right", ""),
               ('AP_GAP_C', "Panel Gap Between Columns", ""),
               ('AP_GAP_S', "Panel Gap Between Faces", "")],
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
                and (_active_mode(context) is not None
                     or _appliance_target(context) is not None))

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
        for name, kind, editable, _locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if not editable:
                return {'PASS_THROUGH'}
            if kind in ('AP_FACE', 'AP_COL'):
                _select_in_panel_tab(name)
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
