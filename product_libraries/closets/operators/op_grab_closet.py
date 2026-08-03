"""Modal operator: grab and stretch closet geometry.

Ported from face_frame's op_modify_cabinet pattern (hover-highlighted
boundaries, LMB-drag with fractional snap, typed numeric override,
Esc/RMB cancel, Enter/release commit) trimmed to the closet boundary
set:

- Interior PANELS   drag X: the two adjacent bays trade width; release
                    auto-locks both (same as typing their labels).
- End panels        drag X: overall starter width. The LEFT end keeps
                    the right edge planted by shifting the starter.
- TOP edge          drag Z: overall starter height. The bottom
                    stays planted, so on a hanging starter this is
                    the hang height.
- Fixed SHELVES     drag Z: the shelf slides between its neighbors;
                    the two openings trade height.
- DIVISIONS         drag X: the division slides between its neighbors
                    in its own segment; the two columns trade width.

All writes go through the same props/idprops the overlay labels commit,
so locking, propagation, and the split reconciler behave identically.
The entry point is the "Grab" pill in the closet overlay's filter row -
no HUD (core) changes.
"""
import bpy
import gpu
import blf
import math
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

from .... import units
from ....units import inch
from ....hb_types import GeoNodeCage, GeoNodeCutpart
from .. import types_closets
from ...face_frame import split_preview

# ---- Tunables (mirror face_frame's grab) ----------------------------------
HIT_TOLERANCE_PX = 12.0
MIN_BAY_WIDTH = inch(2.0)
MIN_OPENING = inch(1.0)
MIN_STARTER_WIDTH = inch(6.0)
MIN_STARTER_HEIGHT = inch(6.0)
# A corner wing has to stay wide enough to hold a shelf worth having.
MIN_WING_DEPTH = inch(3.0)
# The four sizes an inside corner is dragged by. All four are starter
# prompts, so they share one snapshot, one clamp and one restore.
L_SIZE_KINDS = ('L_END_R', 'L_END_L', 'L_DEPTH_R', 'L_DEPTH_L')
SNAP_STEPS = {'COARSE': inch(0.25), 'FINE': inch(0.125)}
GHOST_LINE = (0.85, 0.85, 0.85, 0.35)
HOVER_LINE = (1.00, 0.85, 0.20, 1.00)
ACTIVE_LINE = (1.00, 0.65, 0.10, 1.00)
DIM_TEXT = (1.00, 1.00, 1.00, 1.00)
_DIGIT_KEYS = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX',
               'SEVEN', 'EIGHT', 'NINE',
               'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
               'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9')

# Non-blocking layer state. Grab is a passive overlay: a permanent draw
# handler plus keymap listeners. Nothing blocks except an actual drag
# while the button is down - all other UI (selection, labels, menus,
# sidebar, HUD) stays live.
_enabled = False
_hover = None       # boundary dict under the cursor
_drag_op = None     # live drag operator instance, None between drags
_draw_handle = None
_addon_keymaps = []


def grab_is_active():
    return _enabled


def toggle_grab(on=None):
    global _enabled, _hover
    _enabled = (not _enabled) if on is None else bool(on)
    if not _enabled:
        _hover = None


def request_grab_exit():
    toggle_grab(False)


def _overlay_mode(context):
    try:
        from .. import gpu_overlay_closets as ov
        return ov._active_mode(context)
    except Exception:
        return None


def _bkey(b):
    """Stable identity for a boundary across recollections."""
    if b is None:
        return None
    return (b['kind'], b['root'], b.get('bay'), b.get('shelf'),
            b.get('div'), b.get('left'), b.get('side'))


def _pick_boundary(context, event, boundaries):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None
    mouse = Vector((event.mouse_region_x, event.mouse_region_y))
    best = None
    for b in boundaries:
        a2, c2 = _screen_seg(region, rv3d, b)
        if a2 is None or c2 is None:
            continue
        dist = _point_seg_dist(mouse, a2, c2)
        if dist <= HIT_TOLERANCE_PX and (best is None or dist < best[0]):
            best = (dist, b)
    return best[1] if best else None


# ---- Boundary collection ---------------------------------------------------

def _starter_dims(root):
    sp = root.hb_closet_starter
    return sp.width, sp.height, sp.depth


def _current_mode():
    try:
        from .. import gpu_overlay_closets as ov
        return ov._active_mode(bpy.context) or 'Bays'
    except Exception:
        return 'Bays'


def _corner_boundaries(root, mw, mode):
    """Handles for an inside-corner L unit, Starters mode only.

    Its local frame plants the corner at the origin: the right wing
    runs +X along the back wall and the left wing runs -Y along the
    side wall. Both overall sizes therefore grow away from the corner,
    so neither end shifts the object the way a run's left end does -
    the corner stays against the walls no matter which end is pulled.

    The right wing's end panel sets the width and the left wing's end
    panel sets the depth, each drawn on its own wing's front face so
    it reads as that wing's end. The two wing front edges at the top
    set the height together, and the two at the bottom set the
    mounting - lift them off the floor and the unit hangs. In between,
    every interior shelf front on a wing sets that wing's depth,
    pulling the inner corner of the L in or out. A wing's front reads
    as one face, so grabbing it anywhere between the top and bottom
    edges pulls that wing in or out.

    Every line is measured the way the recalculate measures it - the
    same wing clamps, the same shelf heights - so a handle always sits
    on geometry that is really there.
    """
    if mode != 'Starters':
        return []
    sp = root.hb_closet_starter
    scene_props = types_closets.run_sizes(root)
    st = scene_props.shelf_thickness
    pt = scene_props.panel_thickness
    W, D, H = sp.width, sp.depth, sp.height
    if W <= 0.0 or D <= 0.0 or H <= 0.0:
        return []
    # Wing depths ride inside the opposite overall size; the build
    # clamps them there, so the handles read the clamped values.
    LD = min(sp.l_left_depth, W - pt)
    RD = min(sp.l_right_depth, D - pt)
    # Only a corner standing on the floor carries a kick, and the
    # closet type is what says whether it does.
    kick = sp.toe_kick_height if sp.closet_type != 'HANGING' else 0.0
    # Three sets of wing-front lines: the mount at the bottom, the
    # wing depths on the shelves in between, the height at the top.
    # Every interior shelf front is a depth handle, so the whole front
    # of a wing pulls that wing in or out. One lone line partway up
    # reads as a shelf; a stack of them reads as the wing's front
    # face, which is what it is. The bottom-most and top-most shelves
    # are left out - their fronts land on the mount and height lines,
    # inside the same few pixels. The shelves are spaced the way the
    # build spaces them.
    n_sh = max(int(sp.l_shelf_qty) + 2, 2)
    z_bottom = kick
    z_top = H - st
    if n_sh >= 3:
        z_depths = [(i, z_bottom + (z_top - z_bottom) * i / (n_sh - 1) + st)
                    for i in range(1, n_sh - 1)]
    else:
        # Nothing interior to hang them on - one line halfway up keeps
        # the depths reachable.
        z_depths = [(0, (z_bottom + z_top) / 2.0 + st)]
    z_high = H
    # The shelves stop a panel thickness short of each end panel, and
    # the notch leaves the inner corner at (LD, -RD).
    x_out = W - pt
    y_out = -(D - pt)

    ax_x = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
    # Depth grows toward -Y, so that is the direction a pull outward
    # has to move in for the drag delta to come out positive.
    ax_y = (mw.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
    ax_z = (mw.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()

    out = []
    # Right wing end panel -> overall width.
    x_end = W - pt / 2.0
    out.append(dict(kind='L_END_R', root=root.name,
                    p0=mw @ Vector((x_end, -RD, 0.0)),
                    p1=mw @ Vector((x_end, -RD, H)), axis=ax_x))
    # Left wing end panel -> overall depth.
    y_end = -(D - pt / 2.0)
    out.append(dict(kind='L_END_L', root=root.name,
                    p0=mw @ Vector((LD, y_end, 0.0)),
                    p1=mw @ Vector((LD, y_end, H)), axis=ax_y))
    # Top front edge of each wing -> overall height. Two segments so
    # the whole top outline is grabbable; the side key keeps them
    # separate for hover highlighting.
    out.append(dict(kind='TOP', root=root.name, side='R',
                    p0=mw @ Vector((LD, -RD, z_high)),
                    p1=mw @ Vector((x_out, -RD, z_high)), axis=ax_z))
    out.append(dict(kind='TOP', root=root.name, side='L',
                    p0=mw @ Vector((LD, -RD, z_high)),
                    p1=mw @ Vector((LD, y_out, z_high)), axis=ax_z))
    # Shelf front edge of each wing -> that wing's depth. The shelf
    # index keeps the lines apart for hover highlighting.
    for _i, z_low in z_depths:
        out.append(dict(kind='L_DEPTH_R', root=root.name, shelf=_i,
                        p0=mw @ Vector((LD, -RD, z_low)),
                        p1=mw @ Vector((x_out, -RD, z_low)), axis=ax_y))
        out.append(dict(kind='L_DEPTH_L', root=root.name, shelf=_i,
                        p0=mw @ Vector((LD, -RD, z_low)),
                        p1=mw @ Vector((LD, y_out, z_low)), axis=ax_x))
    # Bottom front edge of each wing -> the mounting, the same way a
    # bay's bottom edge works. Two segments to match the top pair.
    out.append(dict(kind='L_BOTTOM', root=root.name, side='R',
                    p0=mw @ Vector((LD, -RD, 0.0)),
                    p1=mw @ Vector((x_out, -RD, 0.0)), axis=ax_z))
    out.append(dict(kind='L_BOTTOM', root=root.name, side='L',
                    p0=mw @ Vector((LD, -RD, 0.0)),
                    p1=mw @ Vector((LD, y_out, 0.0)), axis=ax_z))
    return out


def _collect_boundaries(scene, mode=None):
    """List of boundary dicts with world-space line segments, SCOPED BY
    SELECTION MODE: Starters mode grabs the whole
    closet (both ends + the full-width top edge); Bays mode grabs
    per-bay heights and panel width trades; shelves are grabbable in
    Bays and Openings modes. Recomputed per pick so it can't drift."""
    if mode is None:
        mode = _current_mode()
    out = []
    try:
        from .. import gpu_overlay_closets as ov
        _space = getattr(bpy.context, 'space_data', None)

        def _shown(r):
            return ov._starter_shown(r, _space)
    except Exception:
        def _shown(r):
            return True
    for root in scene.objects:
        if not root.get(types_closets.TAG_STARTER_CAGE):
            continue
        # Hidden closets (wall hidden/isolated) grow no grab handles -
        # same visibility rule as the overlay labels.
        if not _shown(root):
            continue
        mw = split_preview._world_matrix(root)
        w, h, d = _starter_dims(root)
        # An inside corner has perpendicular ends and no bays, so none
        # of the run collection below applies to it.
        _cls = types_closets.WRAP_CLASS_REGISTRY.get(
            root.get('CLASS_NAME', ''), types_closets.ClosetStarter)
        if getattr(_cls, 'is_corner', False):
            out.extend(_corner_boundaries(root, mw, mode))
            continue
        bays = sorted([c for c in root.children
                       if c.get(types_closets.TAG_BAY_CAGE)],
                      key=lambda o: o.get('hb_bay_index', 0))
        panels = sorted([c for c in root.children
                         if c.get('hb_part_role')
                         == types_closets.PART_ROLE_PANEL
                         and not c.get('hb_double_partition')],
                        key=lambda o: o.get('hb_panel_index', 0))
        n = len(bays)

        # Panels: verticals on the front face. Interior panels (Bays
        # mode) trade the two adjacent bays; end panels (Starters mode)
        # stretch the starter width.
        for i, panel in enumerate(panels):
            try:
                length = GeoNodeCutpart(panel).get_input('Length')
                thick = GeoNodeCutpart(panel).get_input('Thickness')
            except Exception:
                continue
            x = panel.location.x + thick / 2.0
            z0 = panel.location.z
            p0 = mw @ Vector((x, -d, z0))
            p1 = mw @ Vector((x, -d, z0 + length))
            axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
            if i == 0:
                if mode == 'Starters':
                    out.append(dict(kind='END_L', root=root.name,
                                    p0=p0, p1=p1, axis=axis))
            elif i == len(panels) - 1:
                if mode == 'Starters':
                    out.append(dict(kind='END_R', root=root.name,
                                    p0=p0, p1=p1, axis=axis))
            elif i - 1 < n and i < n and mode == 'Bays':
                out.append(dict(kind='PANEL', root=root.name,
                                left=bays[i - 1].name, right=bays[i].name,
                                p0=p0, p1=p1, axis=axis))

        # Whole-closet height: full-width top edge, Starters mode only
        # (no ambiguity with the per-bay handles - different mode).
        if mode == 'Starters':
            z_axis = (mw.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
            p0 = mw @ Vector((0.0, -d, h))
            p1 = mw @ Vector((w, -d, h))
            out.append(dict(kind='TOP', root=root.name,
                            p0=p0, p1=p1, axis=z_axis))

        # Per-bay height handles (Bays mode): a floor-mounted bay grabs
        # at its TOP edge; a hanging bay grabs at its BOTTOM edge (the
        # top stays at the mount height). Both write the bay's height
        # override.
        z_axis = (mw.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        if mode == 'Bays':
            for bay in bays:
                b_mw = split_preview._world_matrix(bay)
                b_w, b_h = split_preview._cage_dims(bay)
                try:
                    b_d = GeoNodeCage(bay).get_input('Dim Y')
                except Exception:
                    b_d = d
                if b_w <= 0.0 or b_h <= 0.0:
                    continue
                # Floor-mounted bays resize from their TOP edge. EVERY
                # bay gets a BOTTOM handle: on a hanging bay it resizes
                # (grow down); on a floor bay dragging it up CONVERTS to
                # hanging, and dragging any bottom back to the floor
                # converts to floor-mounted (mount-by-drag).
                if bay.hb_closet_bay.floor_mounted:
                    p0 = b_mw @ Vector((0.0, -b_d, b_h))
                    p1 = b_mw @ Vector((b_w, -b_d, b_h))
                    out.append(dict(kind='BAY_TOP', root=root.name,
                                    bay=bay.name, p0=p0, p1=p1, axis=z_axis))
                p0 = b_mw @ Vector((0.0, -b_d, 0.0))
                p1 = b_mw @ Vector((b_w, -b_d, 0.0))
                out.append(dict(kind='BAY_BOT', root=root.name,
                                bay=bay.name, p0=p0, p1=p1, axis=z_axis))

        # Splitting shelves: horizontals across their bay (Bays and
        # Openings modes).
        if mode not in ('Bays', 'Openings'):
            continue
        for bay in bays:
            b_mw = split_preview._world_matrix(bay)
            b_w, _bh = split_preview._cage_dims(bay)
            try:
                b_d = GeoNodeCage(bay).get_input('Dim Y')
            except Exception:
                b_d = d
            for side in (('FRONT', 'BACK')
                         if root.get('CLASS_NAME') == 'DoubleIslandClosetStarter'
                         else ('FRONT',)):
                for sh in [c for c in bay.children
                           if c.get('hb_part_role')
                           == types_closets.PART_ROLE_FIXED_SHELF
                           and c.get(types_closets.PROP_OPENING_SIDE,
                                     'FRONT') == side
                           and not c.get('hb_preview')]:
                    z = sh.location.z
                    y_face = -b_d if side != 'BACK' else 0.0
                    p0 = b_mw @ Vector((0.0, y_face, z))
                    p1 = b_mw @ Vector((b_w, y_face, z))
                    out.append(dict(kind='SHELF', root=root.name,
                                    bay=bay.name, shelf=sh.name, side=side,
                                    p0=p0, p1=p1, axis=z_axis))
                # Divisions: verticals standing inside one segment,
                # handled on the same face as that segment's shelves.
                # The handle runs the height of the part, so a division
                # in an upper segment is grabbed where it actually is.
                x_axis = (b_mw.to_3x3()
                          @ Vector((1.0, 0.0, 0.0))).normalized()
                for dv in [c for c in bay.children
                           if c.get('hb_part_role')
                           == types_closets.PART_ROLE_DIVISION
                           and c.get(types_closets.PROP_OPENING_SIDE,
                                     'FRONT') == side]:
                    try:
                        d_len = GeoNodeCutpart(dv).get_input('Length')
                        d_th = GeoNodeCutpart(dv).get_input('Thickness')
                    except Exception:
                        continue
                    x = dv.location.x + d_th / 2.0
                    z0 = dv.location.z
                    y_face = -b_d if side != 'BACK' else 0.0
                    p0 = b_mw @ Vector((x, y_face, z0))
                    p1 = b_mw @ Vector((x, y_face, z0 + d_len))
                    out.append(dict(kind='DIVISION', root=root.name,
                                    bay=bay.name, div=dv.name, side=side,
                                    p0=p0, p1=p1, axis=x_axis))
    return out


def _screen_seg(region, rv3d, b):
    a = view3d_utils.location_3d_to_region_2d(region, rv3d, b['p0'])
    c = view3d_utils.location_3d_to_region_2d(region, rv3d, b['p1'])
    return a, c


def _point_seg_dist(p, a, b):
    ab = b - a
    l2 = ab.length_squared
    if l2 <= 0.0:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
    return (p - (a + ab * t)).length


# ---- Draw ------------------------------------------------------------------

def _draw_line(shader, p1, p2, color, width):
    gpu.state.line_width_set(width)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES',
                     {"pos": (tuple(p1), tuple(p2))}).draw(shader)
    gpu.state.line_width_set(1.0)


def _draw():
    """Permanent POST_PIXEL layer; draws only while grab is enabled and
    a closet selection mode is active. Fully exception-guarded."""
    if not _enabled:
        return
    try:
        context = bpy.context
        area = context.area
        region = context.region
        if area is None or area.type != 'VIEW_3D':
            return
        if region is None or region.type != 'WINDOW':
            return
        if _overlay_mode(context) is None:
            return
        rv3d = context.region_data
        boundaries = _collect_boundaries(context.scene)
        hover_key = _bkey(_hover)
        drag_key = _bkey(_drag_op._drag_boundary) if _drag_op else None
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        for b in boundaries:
            a2, c2 = _screen_seg(region, rv3d, b)
            if a2 is None or c2 is None:
                continue
            k = _bkey(b)
            if drag_key is not None and k == drag_key:
                _draw_line(shader, a2, c2, ACTIVE_LINE, 3.0)
            elif drag_key is None and k == hover_key:
                _draw_line(shader, a2, c2, HOVER_LINE, 2.0)
            else:
                _draw_line(shader, a2, c2, GHOST_LINE, 1.0)
        if _drag_op is not None and _drag_op._drag_text:
            x, y = _drag_op._last_mouse
            blf.size(0, 13)
            blf.color(0, *DIM_TEXT)
            blf.position(0, x + 16, y + 12, 0)
            blf.draw(0, _drag_op._drag_text)
        gpu.state.blend_set('NONE')
    except Exception:
        pass


class hb_closets_OT_grab_mode(bpy.types.Operator):
    """Toggle the grab layer. Non-blocking: handles draw while a closet
    selection mode is active; only an actual drag consumes input."""
    bl_idname = "hb_closets.grab_mode"
    bl_label = "Grab Closet"

    def execute(self, context):
        toggle_grab()
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class hb_closets_OT_grab_hover(bpy.types.Operator):
    """MOUSEMOVE listener: refresh the hovered handle and always pass
    the event through."""
    bl_idname = "hb_closets.grab_hover"
    bl_label = "Grab Hover"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (_enabled and _drag_op is None
                and context.area is not None
                and context.area.type == 'VIEW_3D'
                and context.region is not None
                and context.region.type == 'WINDOW'
                and _overlay_mode(context) is not None)

    def invoke(self, context, event):
        global _hover
        boundaries = _collect_boundaries(context.scene)
        new_hover = _pick_boundary(context, event, boundaries)
        if _bkey(new_hover) != _bkey(_hover):
            _hover = new_hover
            if context.area:
                context.area.tag_redraw()
        return {'PASS_THROUGH'}


class hb_closets_OT_grab_drag(bpy.types.Operator):
    """LMB listener: a press on a grab handle runs the drag (snap /
    typed override / Esc-cancel); presses anywhere else pass through so
    every other tool keeps working."""
    bl_idname = "hb_closets.grab_drag"
    bl_label = "Grab Drag"
    bl_options = {'INTERNAL', 'UNDO'}

    _boundaries = None
    _drag_boundary = None
    _drag_active = False
    _drag_text = ""
    _last_mouse = (0, 0)
    _snap_mode = 'COARSE'
    _typed = ''
    _snapshot = None
    _px_per_unit = 1.0
    _mouse0 = None

    @classmethod
    def poll(cls, context):
        return (_enabled and _drag_op is None
                and context.area is not None
                and context.area.type == 'VIEW_3D'
                and context.region is not None
                and context.region.type == 'WINDOW'
                and _overlay_mode(context) is not None)

    def invoke(self, context, event):
        global _drag_op
        # Overlay labels / pills win where they overlap a handle -
        # clicking a value should type, not drag.
        try:
            from .. import gpu_overlay_closets as ov
            mx, my = event.mouse_region_x, event.mouse_region_y
            mode = ov._active_mode(context)
            for _l, _k, (tx, ty, tw, th) in ov._filter_pill_rects(
                    context, context.area, mode):
                if tx <= mx <= tx + tw and ty <= my <= ty + th:
                    return {'PASS_THROUGH'}
            for _n, _k2, _e, _lk, rect, _t in ov.compute_labels(
                    context, context.region, context.region_data):
                x, y, w, h = rect
                if x <= mx <= x + w and y <= my <= y + h:
                    return {'PASS_THROUGH'}
        except Exception:
            pass
        self._boundaries = _collect_boundaries(context.scene)
        pick = _pick_boundary(context, event, self._boundaries)
        if pick is None:
            return {'PASS_THROUGH'}
        self._snap_mode = 'COARSE'
        self._typed = ''
        self._drag_text = ''
        self._start_drag(context, event, pick)
        if not self._drag_active:
            return {'PASS_THROUGH'}
        _drag_op = self
        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set('SCROLL_XY')
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context, cancelled=False):
        global _drag_op
        _drag_op = None
        try:
            context.window.cursor_modal_restore()
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()
        return {'CANCELLED'} if cancelled else {'FINISHED'}

    def _start_drag(self, context, event, b):
        region, rv3d = context.region, context.region_data
        self._drag_boundary = b
        self._drag_active = True
        self._typed = ''
        self._mouse0 = Vector((event.mouse_region_x, event.mouse_region_y))
        # Pixels per world unit along the drag axis at the grab point.
        mid = (b['p0'] + b['p1']) / 2.0
        a2 = view3d_utils.location_3d_to_region_2d(region, rv3d, mid)
        c2 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, mid + b['axis'])
        if a2 is None or c2 is None:
            self._drag_active = False
            return
        self._axis2d = (c2 - a2)
        self._px_per_unit = max(self._axis2d.length, 1e-6)
        self._axis2d.normalize()
        self._snapshot = self._take_snapshot(b)

    @staticmethod
    def _end_shift_vector(root, shift):
        """Displacement that slides root by ``shift`` along its own
        local X, expressed in the space root.location lives in (the
        parent's space; world when unparented). The old code added the
        WORLD X axis to location - correct only on unrotated walls,
        since location is wall-local: on a rotated wall the world
        vector lands in the wrong frame and the closet slides the
        wrong way. Placement always writes matrix_parent_inverse =
        identity, so parent space == location space."""
        return root.rotation_euler.to_matrix() @ Vector((shift, 0.0, 0.0))

    def _take_snapshot(self, b):
        snap = {'kind': b['kind']}
        root = bpy.data.objects.get(b['root'])
        sp = root.hb_closet_starter
        snap['width'] = sp.width
        snap['height'] = sp.height
        snap['depth'] = sp.depth
        snap['loc'] = tuple(root.location)
        if b['kind'] in L_SIZE_KINDS:
            # Any one of a corner's four sizes can be pulled against
            # the others' clamps, so the whole set is restored on
            # cancel rather than just the one that was dragged.
            snap['ld'] = sp.l_left_depth
            snap['rd'] = sp.l_right_depth
        elif b['kind'] == 'L_BOTTOM':
            # Lifting a corner off the floor changes its type and takes
            # its kick out of the build, and the type it had on the
            # floor is remembered for when it lands again. All three
            # come back on a cancel.
            snap['ctype'] = sp.closet_type
            snap['kick'] = sp.toe_kick_height
            snap['floor_ctype'] = root.get('hb_floor_closet_type')
        elif b['kind'] == 'TOP':
            # Holding the bottom means overriding the build's own top
            # anchor and growing the hung bays with the run, so both
            # have to come back on a cancel.
            snap['last_h'] = root.get('hb_last_height')
            snap['bays'] = [
                (c.name, c.hb_closet_bay.height) for c in root.children
                if c.get(types_closets.TAG_BAY_CAGE)]
        elif b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            snap['lw'] = left.hb_closet_bay.width
            snap['rw'] = right.hb_closet_bay.width
            snap['ll'] = left.hb_closet_bay.unlock_width
            snap['rl'] = right.hb_closet_bay.unlock_width
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            snap['z'] = sh.get('hb_z_offset', 0.0)
        elif b['kind'] == 'DIVISION':
            dv = bpy.data.objects.get(b['div'])
            snap['x'] = dv.get('hb_x_offset', 0.0)
        elif b['kind'] in ('BAY_TOP', 'BAY_BOT'):
            bay = bpy.data.objects.get(b['bay'])
            snap['bh'] = bay.hb_closet_bay.height
            snap['floor'] = bay.hb_closet_bay.floor_mounted
            snap['runH'] = root.hb_closet_starter.height
            # Giving a bay its own height sets the bay's own padlock,
            # so a cancel has to put that back as well as the height.
            snap['bay_unlocked'] = bay.hb_closet_bay.unlock_height
            snap['shelves'] = [
                (c.name, c.get('hb_z_offset', 0.0))
                for c in bay.children
                if c.get('hb_part_role')
                == types_closets.PART_ROLE_FIXED_SHELF
                and not c.get('hb_preview')]
        return snap

    def _hold_shelves_absolute(self, bay, root, snap):
        """Bottom drags move the bay's interior bottom; shelves store
        offsets FROM that bottom, so uncompensated they'd ride along.
        Rewrite each committed shelf's offset from the drag snapshot so
        its absolute (off-the-floor) position holds. Drawer stacks keep
        riding the bottom (they sit on the base) and rods keep their
        top anchor - only splitter shelves hold."""
        scene_props = types_closets.run_sizes(root)
        st = scene_props.shelf_thickness
        kick_v = root.hb_closet_starter.toe_kick_height
        bp = bay.hb_closet_bay
        runH = snap['runH']
        old_base = ((0.0 + kick_v) if snap['floor']
                    else runH - snap['bh'])
        new_base = ((0.0 + kick_v) if bp.floor_mounted
                    else runH - bp.height)
        delta = new_base - old_base
        interior_h = bp.height - 2.0 * st - (kick_v if bp.floor_mounted
                                             else 0.0)
        for name, off0 in snap.get('shelves', ()):
            sh = bpy.data.objects.get(name)
            if sh is not None:
                sh['hb_z_offset'] = float(
                    max(0.0, min(off0 - delta, interior_h - st)))
        types_closets.recalculate_closet_starter(root)

    def _set_bay_height(self, root, bay, new_h, recalc=True):
        """Give a bay a height of its own, the way the Bays table does.

        A bay keeps its own height only while the run height is
        unlocked and the bay is locked; otherwise the next solve pulls
        it back to the run height. Typing into the Bays table performs
        that unlock through the property callback, so a drag has to do
        the same or the bay snaps back and nothing appears to happen.
        Hanging runs seed their bays shorter than the run and are
        already unlocked, which is why they were the only ones that
        worked. A height that matches the run puts the bay back on the
        run height instead of pinning it.

        Written behind the recalc guard so the height and lock
        callbacks don't each solve the run mid-drag; the caller decides
        when the single solve happens."""
        sp = root.hb_closet_starter
        bp = bay.hb_closet_bay
        own = abs(new_h - sp.height) > 1e-6
        rid = id(root)
        types_closets._RECALCULATING.add(rid)
        try:
            bp.height = new_h
            bp.unlock_height = own
        finally:
            types_closets._RECALCULATING.discard(rid)
        if recalc:
            types_closets.recalculate_closet_starter(root)

    def _set_bay_mount(self, root, bay, floor_mounted):
        """Flip a bay between floor-mounted and hanging without
        letting the property callback solve the run mid-drag."""
        bp = bay.hb_closet_bay
        if bp.floor_mounted == floor_mounted:
            return
        rid = id(root)
        types_closets._RECALCULATING.add(rid)
        try:
            bp.floor_mounted = floor_mounted
        finally:
            types_closets._RECALCULATING.discard(rid)

    def _set_run_top(self, root, new_h):
        """Move a starter's top, holding its bottom where it is.

        A hanging starter hangs from its top: the build reads a height
        change as growing the unit downward and slides the origin up by
        the same amount, so the top stays put and a drag on the top
        edge looks dead. The height the build last applied rides an
        idprop, and writing the new height there first tells it this
        edit is not one of those - the floor line holds and the top
        moves, which on a hanging starter is the hang height itself.

        A hung bay hangs from the run top too, so it grows with the run
        to leave its own bottom where it was. A floor bay already
        stands on the floor and keeps the height it was given. Bays
        that follow the run height need no help either way.
        """
        sp = root.hb_closet_starter
        delta = new_h - sp.height
        bays = [c for c in root.children
                if c.get(types_closets.TAG_BAY_CAGE)]

        def _write():
            for bay in bays:
                bp = bay.hb_closet_bay
                if bp.unlock_height and not bp.floor_mounted:
                    bp.height = max(self._min_bay_height(root, bay),
                                    bp.height + delta)
            sp.height = new_h
            root['hb_last_height'] = new_h

        self._write_guarded(root, _write)

    def _set_corner_bottom(self, root, new_h, loc):
        """Write a corner's height and standing position together, so
        the top lands in the same place the drag drew it."""
        sp = root.hb_closet_starter
        self._write_guarded(root, lambda: (
            setattr(sp, 'height', new_h),
            setattr(root, 'location', tuple(loc))))

    def _set_corner_mount(self, root, floor):
        """Stand an inside corner on the floor or hang it on the wall.

        A corner has no bays, so its mounting rides its own closet
        type - the same prompt the build reads to decide whether the
        unit carries a toe kick. The type it had on the floor is
        remembered, so a unit dropped back down is the kind of unit it
        was before it was lifted.

        Written behind the recalc guard so the property callbacks do
        not each solve the unit mid-drag; the caller runs the solve.
        """
        sp = root.hb_closet_starter
        if floor == (sp.closet_type != 'HANGING'):
            return
        rid = id(root)
        types_closets._RECALCULATING.add(rid)
        try:
            if floor:
                sp.closet_type = root.get('hb_floor_closet_type', 'TALL')
                # A corner placed as an Upper was built with no kick at
                # all. Standing it on the floor gives it the scene
                # default rather than leaving it on its shelf edges.
                if sp.toe_kick_height <= 0.0:
                    sp.toe_kick_height = (
                        bpy.context.scene.hb_closets.toe_kick_height)
            else:
                root['hb_floor_closet_type'] = sp.closet_type
                sp.closet_type = 'HANGING'
        finally:
            types_closets._RECALCULATING.discard(rid)

    def _set_corner_size(self, root, kind, value):
        """Clamp and write one of an inside corner's four sizes, and
        return what was written.

        The overall sizes grow away from the planted corner, so there
        is no origin shift to compensate. Each wing depth runs inside
        the opposite overall size and stops a panel thickness short of
        the end panel there - the same limit the build clamps to, so
        dragging can never ask for a wing the unit cannot hold.
        """
        sp = root.hb_closet_starter
        pt = types_closets.run_sizes(root).panel_thickness
        if kind == 'L_END_R':
            new = max(MIN_STARTER_WIDTH, sp.l_left_depth + pt, value)
            sp.width = new
        elif kind == 'L_END_L':
            new = max(MIN_STARTER_WIDTH, sp.l_right_depth + pt, value)
            sp.depth = new
        elif kind == 'L_DEPTH_R':
            new = max(MIN_WING_DEPTH, min(value, sp.depth - pt))
            sp.l_right_depth = new
        else:
            new = max(MIN_WING_DEPTH, min(value, sp.width - pt))
            sp.l_left_depth = new
        return new

    def _min_bay_height(self, root, bay):
        scene_props = types_closets.run_sizes(root)
        st = scene_props.shelf_thickness
        kick = (root.hb_closet_starter.toe_kick_height
                if bay.hb_closet_bay.floor_mounted else 0.0)
        return kick + 2.0 * st + MIN_OPENING

    def _snap_value(self, value, event):
        if event.shift or self._snap_mode == 'OFF':
            return value
        step = SNAP_STEPS.get(self._snap_mode, inch(0.25))
        return round(value / step) * step

    def _snap_height(self, value, event):
        """32mm-system panel/bay height lattice (19 + n*32mm). FINE
        falls back to 1/8\" for off-system tweaking; Shift/OFF is raw."""
        from .. import const_closets as const
        if event.shift or self._snap_mode == 'OFF':
            return value
        if self._snap_mode == 'FINE':
            return round(value / inch(0.125)) * inch(0.125)
        return const.snap_system_height(value)

    def _snap_hole(self, value, event):
        """32mm-system hole lattice (12.95 + n*32mm from the interior
        bottom) for shelf/rod locations."""
        from .. import const_closets as const
        if event.shift or self._snap_mode == 'OFF':
            return value
        if self._snap_mode == 'FINE':
            return round(value / inch(0.125)) * inch(0.125)
        return const.snap_system_hole(value)

    def _apply_drag(self, context, event):
        b = self._drag_boundary
        snap = self._snapshot
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self._last_mouse = (mouse.x, mouse.y)
        delta = (mouse - self._mouse0).dot(self._axis2d) / self._px_per_unit
        root = bpy.data.objects.get(b['root'])
        if root is None:
            return
        us = context.scene.unit_settings

        if b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            new_left = self._snap_value(snap['lw'] + delta, event)
            new_left = max(MIN_BAY_WIDTH,
                           min(new_left,
                               snap['lw'] + snap['rw'] - MIN_BAY_WIDTH))
            new_right = snap['lw'] + snap['rw'] - new_left
            lb, rb = left.hb_closet_bay, right.hb_closet_bay
            # Both bays take their widths over, inside the guard - the
            # padlocks relay the run out the same way the widths do, and
            # a drag can't afford three solves per mouse move.
            self._write_guarded(root, lambda: (
                setattr(lb, 'unlock_width', True),
                setattr(rb, 'unlock_width', True),
                setattr(lb, 'width', new_left),
                setattr(rb, 'width', new_right)))
            self._drag_text = "%s | %s" % (
                units.unit_to_string(us, new_left),
                units.unit_to_string(us, new_right))
        elif b['kind'] in ('END_L', 'END_R'):
            sp = root.hb_closet_starter
            sign = 1.0 if b['kind'] == 'END_R' else -1.0
            new_w = self._snap_value(snap['width'] + sign * delta, event)
            new_w = max(MIN_STARTER_WIDTH, new_w)
            if b['kind'] == 'END_L':
                # Keep the right edge planted: shift the origin by the
                # width change along the starter's local X (in location
                # space - see _end_shift_vector).
                shift = (snap['width'] - new_w)
                root.location = (Vector(snap['loc'])
                                 + self._end_shift_vector(root, shift))
            sp.width = new_w
            self._drag_text = "W " + units.unit_to_string(us, new_w)
        elif b['kind'] == 'TOP':
            sp = root.hb_closet_starter
            new_h = self._snap_height(snap['height'] + delta, event)
            new_h = max(MIN_STARTER_HEIGHT, new_h)
            self._set_run_top(root, new_h)
            # On a hanging starter the top edge IS the hang height, so
            # say so rather than calling it the height.
            label = "Hang Height" if sp.closet_type == 'HANGING' else "H"
            self._drag_text = "%s %s" % (
                label, units.unit_to_string(us, new_h))
        elif b['kind'] == 'L_BOTTOM':
            # The bottom edge is the mounting control, the way a bay's
            # bottom edge is: the top holds still, so pulling the
            # bottom up shortens the unit and hangs it, and letting it
            # back down to the floor stands it up at its full height
            # again. Continuous across the changeover, so there is no
            # step to drag through.
            top_z = snap['loc'][2] + snap['height']
            new_bottom = snap['loc'][2] + delta
            floor = new_bottom <= inch(1.0)
            self._set_corner_mount(root, floor)
            if floor:
                new_h = max(MIN_STARTER_HEIGHT, top_z)
                state = "Floor"
            else:
                # Snap the resulting HEIGHT to the 32mm lattice so a
                # hung corner is always a system panel height.
                new_h = self._snap_height(top_z - new_bottom, event)
                new_h = max(MIN_STARTER_HEIGHT, new_h)
                state = "Hung"
            loc = list(snap['loc'])
            loc[2] = top_z - new_h
            self._set_corner_bottom(root, new_h, loc)
            self._drag_text = "H %s (%s)" % (
                units.unit_to_string(us, new_h), state)
        elif b['kind'] in L_SIZE_KINDS:
            base = {'L_END_R': snap['width'], 'L_END_L': snap['depth'],
                    'L_DEPTH_R': snap['rd'],
                    'L_DEPTH_L': snap['ld']}[b['kind']]
            new = self._set_corner_size(
                root, b['kind'], self._snap_value(base + delta, event))
            label = {'L_END_R': "W", 'L_END_L': "D",
                     'L_DEPTH_R': "Right Wing",
                     'L_DEPTH_L': "Left Wing"}[b['kind']]
            self._drag_text = "%s %s" % (
                label, units.unit_to_string(us, new))
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            bay = bpy.data.objects.get(b['bay'])
            if sh is None or bay is None:
                return
            new_z = self._snap_hole(snap['z'] + delta, event)
            new_z = self._clamp_shelf(bay, sh, new_z)
            sh['hb_z_offset'] = float(new_z)
            types_closets.recalculate_closet_starter(root)
            below, above = self._shelf_gaps(bay, sh)
            self._drag_text = "%s below | %s above" % (
                units.unit_to_string(us, below),
                units.unit_to_string(us, above))
        elif b['kind'] == 'DIVISION':
            dv = bpy.data.objects.get(b['div'])
            bay = bpy.data.objects.get(b['bay'])
            if dv is None or bay is None:
                return
            new_x = self._clamp_division(
                bay, dv, self._snap_value(snap['x'] + delta, event))
            dv['hb_x_offset'] = float(new_x)
            types_closets.recalculate_closet_starter(root)
            left, right = self._division_gaps(bay, dv)
            self._drag_text = "%s | %s" % (
                units.unit_to_string(us, left),
                units.unit_to_string(us, right))
        elif b['kind'] == 'BAY_TOP':
            bay = bpy.data.objects.get(b['bay'])
            if bay is None:
                return
            new_h = self._snap_height(snap['bh'] + delta, event)
            new_h = max(self._min_bay_height(root, bay), new_h)
            self._set_bay_height(root, bay, new_h)
            self._drag_text = "H " + units.unit_to_string(us, new_h)
        elif b['kind'] == 'BAY_BOT':
            bay = bpy.data.objects.get(b['bay'])
            if bay is None:
                return
            # The bottom edge IS the mount control: its position (with a
            # constant top anchor at the run top) decides both height
            # and mounting. Near the floor -> floor-mounted; lifted ->
            # hanging with height = run_top - bottom. Continuous across
            # the transition, so a floor bay converts to hanging the
            # moment its bottom lifts, and back when it lands.
            run_top = root.hb_closet_starter.height
            bottom0 = 0.0 if snap['floor'] else run_top - snap['bh']
            new_bottom = bottom0 + delta
            # Set the mount first: the minimum height depends on it,
            # since only a floor bay carries the toe kick.
            floor = new_bottom <= inch(1.0)
            self._set_bay_mount(root, bay, floor)
            if floor:
                new_h = max(self._min_bay_height(root, bay), run_top)
                state = "Floor"
            else:
                # Snap the resulting HEIGHT to the 32mm lattice so a
                # hung bay is always a system panel height.
                new_h = self._snap_height(run_top - new_bottom, event)
                new_h = max(self._min_bay_height(root, bay), new_h)
                state = "Hung"
            # The shelf hold runs the solve, so skip the one here.
            self._set_bay_height(root, bay, new_h, recalc=False)
            self._hold_shelves_absolute(bay, root, snap)
            self._drag_text = "H %s (%s)" % (
                units.unit_to_string(us, new_h), state)
        if context.area:
            context.area.tag_redraw()

    def _write_guarded(self, root, fn):
        """Write bay widths without the auto-lock callback churn, then
        run one recalc."""
        rid = id(root)
        types_closets._RECALCULATING.add(rid)
        types_closets._DISTRIBUTING_WIDTHS.add(rid)
        try:
            fn()
        finally:
            types_closets._RECALCULATING.discard(rid)
            types_closets._DISTRIBUTING_WIDTHS.discard(rid)
        types_closets.recalculate_closet_starter(root)

    def _clamp_shelf(self, bay, sh, new_z):
        scene_props = types_closets.run_sizes(bay)
        st = scene_props.shelf_thickness
        side = sh.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        shelves = [c for c in bay.children
                   if c.get('hb_part_role')
                   == types_closets.PART_ROLE_FIXED_SHELF
                   and c.get(types_closets.PROP_OPENING_SIDE,
                             'FRONT') == side
                   and not c.get('hb_preview') and c is not sh]
        lo, hi = 0.0, None
        old = sh.get('hb_z_offset', 0.0)
        for other in shelves:
            oz = other.get('hb_z_offset', 0.0)
            if oz < old:
                lo = max(lo, oz + st + MIN_OPENING)
            else:
                hi = oz - st - MIN_OPENING if hi is None \
                    else min(hi, oz - st - MIN_OPENING)
        new_z = max(lo + 0.0, new_z)
        if hi is not None:
            new_z = min(new_z, hi)
        bp = bay.hb_closet_bay
        root = types_closets.find_starter_root(bay)
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        interior_h = bp.height - 2.0 * st - kick
        new_z = min(new_z, interior_h - st - MIN_OPENING)
        return max(new_z, MIN_OPENING)

    def _shelf_gaps(self, bay, sh):
        """(clear below, clear above) for the drag readout."""
        scene_props = types_closets.run_sizes(bay)
        st = scene_props.shelf_thickness
        side = sh.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        z = sh.get('hb_z_offset', 0.0)
        bp = bay.hb_closet_bay
        root = types_closets.find_starter_root(bay)
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        interior_h = bp.height - 2.0 * st - kick
        below_bound, above_bound = 0.0, interior_h
        for other in bay.children:
            if (other.get('hb_part_role')
                    != types_closets.PART_ROLE_FIXED_SHELF
                    or other is sh or other.get('hb_preview')
                    or other.get(types_closets.PROP_OPENING_SIDE,
                                 'FRONT') != side):
                continue
            oz = other.get('hb_z_offset', 0.0)
            if oz < z:
                below_bound = max(below_bound, oz + st)
            else:
                above_bound = min(above_bound, oz)
        return z - below_bound, above_bound - (z + st)

    def _division_row(self, bay, dv):
        """The other divisions standing in this one's segment, left to
        right. A division only has to keep clear of the ones sharing
        its row - one in the segment above or below is nothing to it,
        since a shelf runs between them."""
        side = dv.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        row = int(dv.get('hb_row', 0))
        others = [c for c in bay.children
                  if c.get('hb_part_role')
                  == types_closets.PART_ROLE_DIVISION
                  and c.get(types_closets.PROP_OPENING_SIDE,
                            'FRONT') == side
                  and int(c.get('hb_row', 0)) == row and c is not dv]
        others.sort(key=lambda o: o.get('hb_x_offset', 0.0))
        return others

    def _division_bounds(self, bay, dv):
        """(low, high) the division's left face is allowed between, so
        neither column either side of it comes out too narrow to
        build."""
        from .. import const_closets as const
        pt = types_closets.run_sizes(bay).panel_thickness
        b_w, _bh = split_preview._cage_dims(bay)
        lo = const.DIVISION_MIN_WIDTH
        hi = b_w - pt - const.DIVISION_MIN_WIDTH
        x = dv.get('hb_x_offset', 0.0)
        for other in self._division_row(bay, dv):
            ox = other.get('hb_x_offset', 0.0)
            if ox < x:
                lo = max(lo, ox + pt + const.DIVISION_MIN_WIDTH)
            else:
                hi = min(hi, ox - pt - const.DIVISION_MIN_WIDTH)
        return lo, hi

    def _clamp_division(self, bay, dv, new_x):
        lo, hi = self._division_bounds(bay, dv)
        if hi < lo:
            return lo
        return max(lo, min(new_x, hi))

    def _division_left_edge(self, bay, dv):
        """Where the column to the left of this division starts."""
        pt = types_closets.run_sizes(bay).panel_thickness
        x = dv.get('hb_x_offset', 0.0)
        base = 0.0
        for other in self._division_row(bay, dv):
            ox = other.get('hb_x_offset', 0.0)
            if ox < x:
                base = max(base, ox + pt)
        return base

    def _division_gaps(self, bay, dv):
        """(column left, column right) for the drag readout."""
        pt = types_closets.run_sizes(bay).panel_thickness
        b_w, _bh = split_preview._cage_dims(bay)
        x = dv.get('hb_x_offset', 0.0)
        right_bound = b_w
        for other in self._division_row(bay, dv):
            ox = other.get('hb_x_offset', 0.0)
            if ox >= x:
                right_bound = min(right_bound, ox)
        return x - self._division_left_edge(bay, dv), right_bound - (x + pt)

    def _end_drag(self, context, commit):
        if not self._drag_active:
            return
        b = self._drag_boundary
        if not commit:
            snap = self._snapshot
            root = bpy.data.objects.get(b['root'])
            if root is not None:
                sp = root.hb_closet_starter
                if b['kind'] == 'PANEL':
                    left = bpy.data.objects.get(b['left'])
                    right = bpy.data.objects.get(b['right'])
                    lb, rb = left.hb_closet_bay, right.hb_closet_bay
                    self._write_guarded(root, lambda: (
                        setattr(lb, 'width', snap['lw']),
                        setattr(rb, 'width', snap['rw']),
                        setattr(lb, 'unlock_width', snap['ll']),
                        setattr(rb, 'unlock_width', snap['rl'])))
                elif b['kind'] in ('END_L', 'END_R'):
                    root.location = snap['loc']
                    sp.width = snap['width']
                elif b['kind'] == 'TOP':
                    def _restore_top():
                        for name, h0 in snap.get('bays', ()):
                            bay = bpy.data.objects.get(name)
                            if bay is not None:
                                bay.hb_closet_bay.height = h0
                        sp.height = snap['height']
                        # Put the anchor back where it was so the next
                        # height edit from the properties panel behaves
                        # as though the drag never happened.
                        last_h = snap.get('last_h')
                        root['hb_last_height'] = (
                            snap['height'] if last_h is None else last_h)
                        root.location = snap['loc']
                    self._write_guarded(root, _restore_top)
                elif b['kind'] == 'L_BOTTOM':
                    def _restore_bottom():
                        sp.closet_type = snap['ctype']
                        sp.toe_kick_height = snap['kick']
                        sp.height = snap['height']
                        root.location = snap['loc']
                        if snap.get('floor_ctype') is None:
                            if 'hb_floor_closet_type' in root:
                                del root['hb_floor_closet_type']
                        else:
                            root['hb_floor_closet_type'] = (
                                snap['floor_ctype'])
                    self._write_guarded(root, _restore_bottom)
                elif b['kind'] in L_SIZE_KINDS:
                    def _restore_l_size():
                        sp.width = snap['width']
                        sp.depth = snap['depth']
                        sp.l_left_depth = snap['ld']
                        sp.l_right_depth = snap['rd']
                    self._write_guarded(root, _restore_l_size)
                elif b['kind'] == 'SHELF':
                    sh = bpy.data.objects.get(b['shelf'])
                    if sh is not None:
                        sh['hb_z_offset'] = float(snap['z'])
                        types_closets.recalculate_closet_starter(root)
                elif b['kind'] == 'DIVISION':
                    dv = bpy.data.objects.get(b['div'])
                    if dv is not None:
                        dv['hb_x_offset'] = float(snap['x'])
                        types_closets.recalculate_closet_starter(root)
                elif b['kind'] in ('BAY_TOP', 'BAY_BOT'):
                    bay = bpy.data.objects.get(b['bay'])
                    if bay is not None:
                        bp = bay.hb_closet_bay
                        for name, off0 in snap.get('shelves', ()):
                            sh = bpy.data.objects.get(name)
                            if sh is not None:
                                sh['hb_z_offset'] = float(off0)
                        # Restore behind the guard: writing the height
                        # would otherwise hand the bay its own through
                        # the callback and undo the restore.
                        self._write_guarded(root, lambda: (
                            setattr(bp, 'floor_mounted', snap['floor']),
                            setattr(bp, 'height', snap['bh']),
                            setattr(bp, 'unlock_height',
                                    snap['bay_unlocked'])))
        self._drag_active = False
        self._drag_boundary = None
        self._drag_text = ""
        self._typed = ''
        # Boundaries move with the geometry; recollect for clean lines.
        self._boundaries = _collect_boundaries(bpy.context.scene)

    def _apply_typed(self, context):
        """Typed value replaces the drag's primary parameter."""
        from ..gpu_overlay_closets import parse_distance
        value = parse_distance(self._typed) if self._typed else None
        self._typed = ''
        if value is None or value <= 0.0 or not self._drag_active:
            return
        b = self._drag_boundary
        snap = self._snapshot
        root = bpy.data.objects.get(b['root'])
        us = context.scene.unit_settings
        if b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            new_left = max(MIN_BAY_WIDTH,
                           min(value,
                               snap['lw'] + snap['rw'] - MIN_BAY_WIDTH))
            new_right = snap['lw'] + snap['rw'] - new_left
            lb, rb = left.hb_closet_bay, right.hb_closet_bay
            # Both bays take their widths over, inside the guard - the
            # padlocks relay the run out the same way the widths do, and
            # a drag can't afford three solves per mouse move.
            self._write_guarded(root, lambda: (
                setattr(lb, 'unlock_width', True),
                setattr(rb, 'unlock_width', True),
                setattr(lb, 'width', new_left),
                setattr(rb, 'width', new_right)))
        elif b['kind'] in ('END_L', 'END_R'):
            sp = root.hb_closet_starter
            if b['kind'] == 'END_L':
                shift = snap['width'] - value
                root.location = (Vector(snap['loc'])
                                 + self._end_shift_vector(root, shift))
            sp.width = max(MIN_STARTER_WIDTH, value)
        elif b['kind'] == 'TOP':
            self._set_run_top(root, max(MIN_STARTER_HEIGHT, value))
        elif b['kind'] == 'L_BOTTOM':
            # Typing sets the height, as it does on a bay bottom; the
            # top stays put and the mounting follows from where that
            # leaves the bottom.
            top_z = snap['loc'][2] + snap['height']
            new_h = max(MIN_STARTER_HEIGHT, value)
            loc = list(snap['loc'])
            loc[2] = top_z - new_h
            self._set_corner_mount(root, loc[2] <= inch(1.0))
            self._set_corner_bottom(root, new_h, loc)
        elif b['kind'] in L_SIZE_KINDS:
            self._set_corner_size(root, b['kind'], value)
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            bay = bpy.data.objects.get(b['bay'])
            if sh is not None and bay is not None:
                sh['hb_z_offset'] = float(self._clamp_shelf(bay, sh, value))
                types_closets.recalculate_closet_starter(root)
        elif b['kind'] == 'DIVISION':
            dv = bpy.data.objects.get(b['div'])
            bay = bpy.data.objects.get(b['bay'])
            if dv is not None and bay is not None:
                # A typed number is the width of the column to the LEFT
                # of the division, the way typing on a panel is the
                # width of the bay to its left.
                base = self._division_left_edge(bay, dv)
                dv['hb_x_offset'] = float(
                    self._clamp_division(bay, dv, base + value))
                types_closets.recalculate_closet_starter(root)
        elif b['kind'] in ('BAY_TOP', 'BAY_BOT'):
            bay = bpy.data.objects.get(b['bay'])
            if bay is not None:
                new_h = max(self._min_bay_height(root, bay), value)
                bottom = b['kind'] == 'BAY_BOT'
                self._set_bay_height(root, bay, new_h, recalc=not bottom)
                if bottom:
                    self._hold_shelves_absolute(bay, root, snap)
        self._end_drag(context, commit=True)

    # ---- modal ----
    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self._last_mouse = (event.mouse_region_x, event.mouse_region_y)
            self._apply_drag(context, event)
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self._end_drag(context, commit=True)
            return self._finish(context)

        if event.type == 'TAB' and event.value == 'PRESS':
            self._snap_mode = {'OFF': 'COARSE', 'COARSE': 'FINE',
                               'FINE': 'OFF'}[self._snap_mode]
            self.report({'INFO'}, f"Snap: {self._snap_mode}")
            return {'RUNNING_MODAL'}

        if event.value == 'PRESS':
            if event.type in _DIGIT_KEYS:
                self._typed += event.type[-1]
                self._drag_text = self._typed + '"?'
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type in ('PERIOD', 'SLASH'):
                self._typed += '.' if event.type == 'PERIOD' else '/'
                return {'RUNNING_MODAL'}
            if event.type == 'BACK_SPACE':
                self._typed = self._typed[:-1]
                return {'RUNNING_MODAL'}
            if event.type in {'RET', 'NUMPAD_ENTER'} and self._typed:
                self._apply_typed(context)
                return self._finish(context)
            if event.type in {'ESC', 'RIGHTMOUSE'}:
                self._end_drag(context, commit=False)
                return self._finish(context, cancelled=True)

        return {'RUNNING_MODAL'}


classes = (
    hb_closets_OT_grab_mode,
    hb_closets_OT_grab_hover,
    hb_closets_OT_grab_drag,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        hb_closets_OT_grab_drag.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        hb_closets_OT_grab_hover.bl_idname, 'MOUSEMOVE', 'ANY',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))


def register():
    global _draw_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    _register_keymaps()


def unregister():
    global _draw_handle, _drag_op
    toggle_grab(False)
    _drag_op = None
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()
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
