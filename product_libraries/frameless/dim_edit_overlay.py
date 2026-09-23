"""Editable dimension overlay for the frameless Cabinets / Bays /
Openings selection modes.

While the frameless selection mode is 'Cabinets', 'Bays' or 'Openings',
a POST_PIXEL draw handler paints a value label on every frameless
cabinet in the viewport: W / H / D on the cabinet root, W / H on each
bay, and the variable size of each opening. Clicking an editable label
starts a short-lived modal that captures typed input (same distance
grammar as placement typing: inches, fractions, feet'inches"); Enter
commits the value through the same paths the sidebar dialogs use:

- Cabinet W/H/D -> the root cage's Dim X / Dim Z / Dim Y inputs plus
  run_calc_fix, exactly what hb_frameless.cabinet_prompts writes, so
  the carcass re-solves identically to a dialog edit.
- Bay W/H -> read-only. A frameless carcass carries one bay sized by
  the solver from the cabinet, so the label is a dimmed readout.
- Opening size -> the splitter's calculator prompt ('Opening N Height'
  under a vertical splitter, 'Opening N Width' under a horizontal one),
  with the prompt's ``equal`` flag cleared first so the typed value
  holds while the other openings share what is left -- the same edit
  hb_frameless.edit_splitter_openings makes. Openings that are not
  split children (a bay's single opening) show a dimmed, read-only
  height.

Architecture mirrors face_frame/dim_edit_overlay.py deliberately: a
permanent draw handler that is a cheap no-op outside the three modes,
an addon-keymap click router that only consumes presses landing on an
editable label, and a modal that owns the keyboard for the edit's
lifetime. Cage geometry is read from the modifier's Dim inputs rather
than bound_box so cages built while hidden still land on the cabinet.
"""

import bpy
import blf
import gpu
from mathutils import Vector
from bpy_extras import view3d_utils

from ... import units
from ... import hb_placement
from ... import hb_utils
from ...hb_types import GeoNodeCage
from . import solver_frameless

# ---- Style (matches face_frame/dim_edit_overlay.py) ----------------------

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

TAG_CABINET = 'IS_FRAMELESS_CABINET_CAGE'
TAG_BAY     = 'IS_FRAMELESS_BAY_CAGE'
TAG_OPENING = 'IS_FRAMELESS_OPENING_CAGE'

MODES = ('Cabinets', 'Bays', 'Openings')

# ---- Module state -------------------------------------------------------

_draw_handle = None
_shutdown = False
# Active edit: {'name': object name, 'kind': label kind, 'typed': str,
#               'owner': id(operator)} or None. Written by the edit
# modal, read by the draw handler so the edited label renders as an
# input field.
_edit = None
_addon_keymaps = []


# ---- Typed-distance parsing (borrowed from PlacementMixin) --------------

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
    """'Cabinets' / 'Bays' / 'Openings' when the overlay should draw,
    else None. Mirrors the HUD's gating: real room scene, FRAMELESS tab,
    selection mode set to an overlay mode. Frameless has no master
    enable bool -- 'Parts' / 'Interiors' are the neutral states."""
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'FRAMELESS':
        return None
    fl = getattr(scene, 'hb_frameless', None)
    if fl is None:
        return None
    mode = getattr(fl, 'frameless_selection_mode', '')
    return mode if mode in MODES else None


def _sizes_scope(context):
    """Size-label scope from the scene prop: 'ALL', 'SELECTED_CABINET'
    (every label on a cabinet the selection belongs to), 'SELECTED'
    (labels only for cages in the current selection), or 'OFF'."""
    fl = getattr(context.scene, 'hb_frameless', None)
    return getattr(fl, 'selection_mode_sizes_scope', 'ALL')


def _sizes_shown(context):
    return _sizes_scope(context) != 'OFF'


def _selected_label_names(context):
    """Object names eligible for labels in SELECTED scope: every
    selected object (plus the active one) and its ancestor chain, so
    clicking any part of a cabinet keeps the labels that target an
    ENCLOSING cage (the root W/H/D, a split opening above a door)."""
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


# ---- Cage geometry --------------------------------------------------------

def _cage_dims(obj):
    """(dim_x, dim_y, dim_z) read from the cage modifier's Dim inputs.
    bound_box is unreliable for a cage created while hidden (never
    depsgraph-evaluated); the modifier inputs are stored values."""
    for m in obj.modifiers:
        if m.type == 'NODES' and m.node_group:
            ids = {it.name: it.identifier
                   for it in m.node_group.interface.items_tree
                   if getattr(it, 'in_out', None) == 'INPUT'}
            dx = hb_utils.try_get_gn_input(m, ids.get('Dim X', ''))
            dy = hb_utils.try_get_gn_input(m, ids.get('Dim Y', ''))
            dz = hb_utils.try_get_gn_input(m, ids.get('Dim Z', ''))
            if dx is not None and dy is not None and dz is not None:
                return dx, dy, dz
    bb = obj.bound_box
    xs = [c[0] for c in bb]
    ys = [c[1] for c in bb]
    zs = [c[2] for c in bb]
    return max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)


def _world_matrix(obj):
    """World matrix rebuilt from the cabinet ROOT's matrix_world (always
    evaluated, and carrying any constraint-driven wall placement) walked
    back down through matrix_parent_inverse @ matrix_basis, so cages
    that were built hidden still land on the cabinet. Same reasoning as
    face_frame/split_preview._world_matrix."""
    chain = []
    node = obj
    while node is not None and not node.get(TAG_CABINET):
        chain.append(node)
        node = node.parent
    if node is None:
        node = obj
        chain = []
        while node.parent is not None:
            chain.append(node)
            node = node.parent
    mw = node.matrix_world.copy()
    for child in reversed(chain):
        mw = mw @ child.matrix_parent_inverse @ child.matrix_basis
    return mw


def _anchor_world(cage, fx, fz):
    """World point on a bay / opening cage's front face at fractional
    X / Z. Those cages' origins already sit on the front plane (the
    solver places the bay at y = -depth inside the root), so a small
    negative Y is the whole front offset."""
    dim_x, _dim_y, dim_z = _cage_dims(cage)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = _world_matrix(cage)
    return mw @ Vector((dim_x * fx, -0.003, dim_z * fz))


def _root_anchor_world(cabinet, fx, fz):
    """World point on the cabinet's FRONT plane at fractional X / Z. The
    root cage is built with Mirror Y, so its local Y = 0 plane is the
    BACK and the front sits at -depth. Keeps cabinet-mode labels on the
    same plane as bay / opening labels."""
    dim_x, dim_y, dim_z = _cage_dims(cabinet)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = _world_matrix(cabinet)
    return mw @ Vector((dim_x * fx, -dim_y - 0.003, dim_z * fz))


def _height_dim_fx(cage):
    """Fractional X of a cage's height dim line (HEIGHT_DIM_INSET in
    from its left side)."""
    dim_x, _dim_y, _dim_z = _cage_dims(cage)
    if dim_x <= 0.0:
        return 0.5
    return min(HEIGHT_DIM_INSET / dim_x, 0.25)


def _root_depth_points(cabinet):
    """(front, middle, back) world points of the cabinet's depth dim,
    across the top at mid width. The root's local Y = 0 is its BACK
    (see _root_anchor_world)."""
    dim_x, dim_y, dim_z = _cage_dims(cabinet)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = _world_matrix(cabinet)
    return (mw @ Vector((dim_x / 2.0, -dim_y, dim_z)),
            mw @ Vector((dim_x / 2.0, -dim_y / 2.0, dim_z)),
            mw @ Vector((dim_x / 2.0, 0.0, dim_z)))


def _pair(a, b):
    return None if a is None or b is None else (a, b)


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


# ---- Label collection ----------------------------------------------------

def _iter_cabinet_roots(scene):
    for obj in scene.objects:
        if obj.get(TAG_CABINET):
            yield obj


def _iter_bay_cages(cabinet):
    for child in cabinet.children_recursive:
        if child.get(TAG_BAY):
            yield child


def _iter_leaf_openings(bay):
    """Opening cages under a bay with no opening cage beneath them --
    the same cages Openings selection mode highlights (toggle_mode
    skips a parent that has a child of the same type)."""
    for child in bay.children_recursive:
        if not child.get(TAG_OPENING):
            continue
        if any(c.get(TAG_OPENING) for c in child.children_recursive):
            continue
        yield child


def _split_target(leaf, cabinet):
    """(split_opening, kind) for a leaf opening whose size is a
    calculator prompt on a splitter: the nearest ancestor (the leaf
    itself included) tagged as a split OPENING whose parent is a
    vertical / horizontal splitter cage. (None, None) when the leaf's
    size is handed down from the bay and has no prompt to edit."""
    node = leaf
    while node is not None and node is not cabinet:
        parent = node.parent
        if (parent is not None
                and node.get(solver_frameless.PART_ROLE_KEY) == 'OPENING'
                and node.get(solver_frameless.SPLIT_INDEX_KEY) is not None):
            if parent.get(solver_frameless.SPLITTER_VERTICAL_TAG):
                return node, 'OPENING_H'
            if parent.get(solver_frameless.SPLITTER_HORIZONTAL_TAG):
                return node, 'OPENING_W'
        node = parent
    return None, None


def _split_prompt(opening, kind):
    """The calculator prompt driving a split opening's size, or None."""
    parent = opening.parent
    if parent is None:
        return None
    calc = solver_frameless.splitter_calculator(parent)
    if calc is None:
        return None
    index = opening.get(solver_frameless.SPLIT_INDEX_KEY)
    if index is None:
        return None
    suffix = 'Height' if kind == 'OPENING_H' else 'Width'
    return calc.get_calculator_prompt('Opening %d %s' % (int(index), suffix))


def _cabinet_shown(cabinet, space=None):
    """False when the cabinet is hidden in the viewport (wall hidden with
    its children, subtree hidden, isolate / local view, collection off)
    so its labels vanish - and stop catching clicks - with it. The cages
    can't carry this test (toggle_mode hides / shows them per selection
    mode), so probe the first real mesh part; cages and 2D annotations
    are excluded, as are parts the solver has parked (hide_render)."""
    probe = None
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


def _cabinet_editable(cabinet):
    """A flattened cabinet (modifier applied) has no Dim inputs to
    write; its labels stay read-only, as cabinet_prompts refuses it."""
    try:
        return GeoNodeCage(cabinet).has_modifier()
    except Exception:
        return False


def compute_labels(context, region, rv3d, lines_out=None):
    """[(obj_name, kind, editable, locked, rect, text)] for every label
    currently on screen. When ``lines_out`` is a list, the region-space
    dimension line under each label is appended to it as
    ``(points, editable)``. rect is (x, y, w, h) region-local. ``locked``
    marks a split opening whose prompt is held (equal cleared); locked
    labels carry a bullet so users can see which values are pinned vs
    shared. obj_name is the object a commit writes -- for an editable
    opening that is the split opening, which may sit above the leaf
    cage the label is drawn on. Shared by the draw handler and the
    click operators so hits can't drift from pixels."""
    mode = _active_mode(context)
    if mode is None or rv3d is None:
        return []
    if not _sizes_shown(context):
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
    for cabinet in _iter_cabinet_roots(scene):
        if not _cabinet_shown(cabinet, space):
            continue
        # Cabinet scope: the whole cabinet's labels once anything in it
        # is selected (sel_names carries each selected object's
        # ancestors, so the root is in it).
        if scope == 'SELECTED_CABINET' and cabinet.name not in sel_names:
            continue
        # targets: (write_obj, kind, editable, locked, value, prefix,
        #           anchor, line) -- line is the (a, b) world dimension
        #           line the label sits at the middle of, or None.
        targets = []
        if mode == 'Cabinets':
            dim_x, dim_y, dim_z = _cage_dims(cabinet)
            editable = _cabinet_editable(cabinet)
            # W across the middle of the front, H up the left side, D
            # front to back across the top.
            fx = _height_dim_fx(cabinet)
            depth_pts = _root_depth_points(cabinet)
            targets = [
                (cabinet, 'CAB_H', editable, False, dim_z, "H ",
                 _root_anchor_world(cabinet, fx, 0.5),
                 _pair(_root_anchor_world(cabinet, fx, 0.0),
                       _root_anchor_world(cabinet, fx, 1.0))),
                (cabinet, 'CAB_W', editable, False, dim_x, "W ",
                 _root_anchor_world(cabinet, 0.5, 0.5),
                 _pair(_root_anchor_world(cabinet, 0.0, 0.5),
                       _root_anchor_world(cabinet, 1.0, 0.5))),
                (cabinet, 'CAB_D', editable, False, dim_y, "D ",
                 depth_pts[1] if depth_pts else None,
                 (depth_pts[0], depth_pts[2]) if depth_pts else None),
            ]
        elif mode == 'Bays':
            # Bay size is the solver's (carcass minus sides / bottom /
            # top), so these are readouts, not inputs.
            for bay in _iter_bay_cages(cabinet):
                dim_x, _dim_y, dim_z = _cage_dims(bay)
                fx = _height_dim_fx(bay)
                targets.append((bay, 'BAY_W', False, False, dim_x, "W ",
                                _anchor_world(bay, 0.5, 0.5),
                                _pair(_anchor_world(bay, 0.0, 0.5),
                                      _anchor_world(bay, 1.0, 0.5))))
                targets.append((bay, 'BAY_H', False, False, dim_z, "H ",
                                _anchor_world(bay, fx, 0.5),
                                _pair(_anchor_world(bay, fx, 0.0),
                                      _anchor_world(bay, fx, 1.0))))
        else:
            for bay in _iter_bay_cages(cabinet):
                for leaf in _iter_leaf_openings(bay):
                    split, kind = _split_target(leaf, cabinet)
                    prompt = (_split_prompt(split, kind)
                              if split is not None else None)
                    anchor = _anchor_world(leaf, 0.5, 0.5)
                    # Drawn on the leaf cage even when the label writes
                    # to a split above it.
                    height_line = _pair(_anchor_world(leaf, 0.5, 0.0),
                                        _anchor_world(leaf, 0.5, 1.0))
                    if prompt is not None:
                        # Displayed value is the prompt itself -- what
                        # the solver reads and a commit writes -- so
                        # typing back the shown value is a no-op.
                        prefix = "H " if kind == 'OPENING_H' else "W "
                        line = (height_line if kind == 'OPENING_H'
                                else _pair(_anchor_world(leaf, 0.0, 0.5),
                                           _anchor_world(leaf, 1.0, 0.5)))
                        targets.append((split, kind, True,
                                        not prompt.equal,
                                        prompt.distance_value, prefix,
                                        anchor, line))
                    else:
                        _dx, _dy, dim_z = _cage_dims(leaf)
                        targets.append((leaf, 'OPENING', False, False,
                                        dim_z, "H ", anchor, height_line))
        # SELECTED scope: keep only labels whose cage is part of the
        # current selection. The click handlers hit-test against this
        # same list, so filtered labels are not clickable either.
        if scope == 'SELECTED':
            targets = [t for t in targets if t[0].name in sel_names]
        for (obj, kind, editable, locked, value, prefix, anchor,
             line) in targets:
            if anchor is None or value is None:
                continue
            pt = view3d_utils.location_3d_to_region_2d(region, rv3d, anchor)
            if pt is None:
                continue
            text = prefix + units.unit_to_string(unit_settings, value)
            if locked:
                # Pinned (user-typed, held while the others share the
                # rest). The marker doubles as the affordance for "this
                # one can be reset to equal" (right-click, or X / 0
                # while editing).
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
            labels.append((obj.name, kind, editable, locked, rect, text))
            if lines_out is not None and line is not None:
                pts = _project_dim_line(region, rv3d, line, s)
                if pts:
                    lines_out.append((pts, editable))
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
    """Permanent POST_PIXEL callback; cheap no-op outside the modes."""
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

def _resolve_split(obj, kind):
    """(cabinet_bp, calculator, prompt) for a split-opening edit, or
    (None, None, None) when any link is missing."""
    prompt = _split_prompt(obj, kind)
    if prompt is None:
        return None, None, None
    calc = solver_frameless.splitter_calculator(obj.parent)
    return hb_utils.get_cabinet_bp(obj), calc, prompt


def _resolve_after_split_edit(context, cabinet_bp, calc):
    """Same sequence as hb_frameless.edit_splitter_openings: recompute
    the calculator, then re-solve the cabinet so every cage below the
    splitter picks up the new shares."""
    try:
        calc.calculate()
    except Exception:
        pass
    if cabinet_bp is not None:
        hb_utils.run_calc_fix(context, cabinet_bp)


def _commit(context, obj, kind, value):
    """Write the typed value through the dialogs' own paths."""
    if kind in ('CAB_W', 'CAB_H', 'CAB_D'):
        # Same inputs cabinet_prompts writes, then the same re-solve.
        cage = GeoNodeCage(obj)
        if not cage.has_modifier():
            return False
        name = {'CAB_W': 'Dim X', 'CAB_H': 'Dim Z', 'CAB_D': 'Dim Y'}[kind]
        cage.set_input(name, value)
        hb_utils.run_calc_fix(context, obj)
        return True
    if kind in ('OPENING_H', 'OPENING_W'):
        cabinet_bp, calc, prompt = _resolve_split(obj, kind)
        if prompt is None:
            return False
        # Hold-first: a prompt only keeps its value while it is not
        # sharing equally (mirrors the lock icon in Edit Opening Sizes).
        prompt.equal = False
        prompt.distance_value = value
        _resolve_after_split_edit(context, cabinet_bp, calc)
        return True
    return False


def _reset_to_auto(context, obj, kind):
    """Put a split opening back on equal share so the solver owns its
    size again. The inverse of the hold a typed edit applies. No-op
    when already equal."""
    if kind in ('OPENING_H', 'OPENING_W'):
        cabinet_bp, calc, prompt = _resolve_split(obj, kind)
        if prompt is None or prompt.equal:
            return False
        prompt.equal = True
        _resolve_after_split_edit(context, cabinet_bp, calc)
        return True
    return False


# ---- Edit modal ------------------------------------------------------------

class hb_frameless_OT_edit_dim_label(bpy.types.Operator):
    """Type a new value for the clicked cabinet-size / opening-size
    label. Enter commits, Esc / right-click / click-away cancels."""
    bl_idname = "hb_frameless.edit_dim_label"
    bl_label = "Edit Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    kind: bpy.props.EnumProperty(
        items=[('CAB_W', "Cabinet Width", ""),
               ('CAB_H', "Cabinet Height", ""),
               ('CAB_D', "Cabinet Depth", ""),
               ('OPENING_H', "Opening Height", ""),
               ('OPENING_W', "Opening Width", "")],
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
                # Typing 0 means "back to auto": release the hold so
                # the opening shares equally again.
                self._finish(context)
                _reset_to_auto(context, obj, self.kind)
                return {'FINISHED'}
            if obj is None or value is None or value <= 0.0:
                self.report({'WARNING'},
                            f"Could not read '{typed}' as a size")
                self._finish(context)
                return {'CANCELLED'}
            self._finish(context)
            _commit(context, obj, self.kind, value)
            return {'FINISHED'}

        if event.type in {'X', 'DEL'}:
            # Reset to auto-calculated, mirroring the 0-Enter path.
            obj = bpy.data.objects.get(self.target_name)
            self._finish(context)
            if obj is not None:
                _reset_to_auto(context, obj, self.kind)
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

class hb_frameless_OT_dim_label_click(bpy.types.Operator):
    """Routes a viewport left-press to overlay labels. A press on an
    editable label starts the edit modal and is consumed; anything else
    passes through untouched."""
    bl_idname = "hb_frameless.dim_label_click"
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
        for name, kind, editable, _locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if not editable:
                return {'PASS_THROUGH'}
            bpy.ops.hb_frameless.edit_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


class hb_frameless_OT_dim_label_reset(bpy.types.Operator):
    """Right-click on a pinned (•) opening label puts that opening back
    on equal share. Presses anywhere else -- including on unpinned
    labels, which have nothing to reset -- pass through to the normal
    context menu / selection."""
    bl_idname = "hb_frameless.dim_label_reset"
    bl_label = "Reset Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_frameless_OT_dim_label_click.poll(context)

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
            if obj is not None and _reset_to_auto(context, obj, kind):
                context.area.tag_redraw()
                return {'FINISHED'}
            return {'PASS_THROUGH'}
        return {'PASS_THROUGH'}


# ---- Lifecycle --------------------------------------------------------------

classes = (
    hb_frameless_OT_edit_dim_label,
    hb_frameless_OT_dim_label_click,
    hb_frameless_OT_dim_label_reset,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        hb_frameless_OT_dim_label_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        hb_frameless_OT_dim_label_reset.bl_idname, 'RIGHTMOUSE', 'PRESS',
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
