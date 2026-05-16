"""Open Mode modal operator.

Stays running until Esc / right-click. While active, left-clicks on doors,
drawer fronts, and pullout fronts toggle them open or closed via a tween
on each opening's swing_percent. Clicks that don't hit an openable front
pass through, so normal viewport selection keeps working.

The tween bypasses the full cabinet recalc on each frame: per tick we
just run the solver's front_leaves() with a swing-override proxy and
write the resulting pivot transforms directly. swing_percent is only
read by front_leaves, so no other parts depend on the interpolated
value. On tween completion the final value is committed through the
prop so the open state survives subsequent recalcs.
"""

import time
import bpy
from bpy_extras import view3d_utils

from .. import types_face_frame
from .. import solver_face_frame as solver


ANIM_DURATION = 0.4
TIMER_HZ = 60

# Fronts that physically open. Other front roles (FALSE_FRONT, INSET_PANEL)
# never move regardless of swing_percent, so clicks on them are ignored.
OPENING_FRONT_ROLES = frozenset({'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT'})


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


class _SwingOverrideProxy:
    """Wraps an opening_props instance so the solver sees an arbitrary
    swing value without us having to write through the real prop (which
    would trigger a full cabinet recalc on every tween tick).
    """
    __slots__ = ('_inner', '_swing')

    def __init__(self, inner, swing):
        object.__setattr__(self, '_inner', inner)
        object.__setattr__(self, '_swing', float(swing))

    def __getattr__(self, name):
        if name == 'swing_percent':
            return self._swing
        return getattr(self._inner, name)


def _find_opening_cage(obj):
    cur = obj
    while cur is not None:
        if cur.get(types_face_frame.TAG_OPENING_CAGE):
            return cur
        cur = cur.parent
    return None


def _find_owning_front(obj):
    """Walk obj's parent chain up to the first front part. Returns None
    if no front ancestor exists. Lets clicks on a front's children
    (pulls today; hinges or other decoration in the future) count as
    clicks on the front itself, since the raycast lands on whatever
    geometry sits topmost at the cursor."""
    cur = obj
    while cur is not None:
        if cur.get('hb_part_role') in OPENING_FRONT_ROLES:
            return cur
        cur = cur.parent
    return None


def _find_bay_cage(opening_cage):
    cur = opening_cage.parent
    while cur is not None:
        if cur.get(types_face_frame.TAG_BAY_CAGE):
            return cur
        cur = cur.parent
    return None


def _raycast_under_cursor(context, event):
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None
    coord = (event.mouse_region_x, event.mouse_region_y)
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    depsgraph = context.evaluated_depsgraph_get()
    hit, _loc, _norm, _idx, obj, _mat = context.scene.ray_cast(
        depsgraph, ray_origin, view_vector
    )
    return obj if hit else None


def _build_tween_context(opening_cage):
    """Resolve everything we need to animate this opening's fronts.

    Returns dict with cabinet props, layout, rect, pivot list, or None
    if the opening isn't in a valid cabinet structure.
    """
    root = types_face_frame.find_cabinet_root(opening_cage)
    if root is None:
        return None
    bay = _find_bay_cage(opening_cage)
    if bay is None:
        return None
    bay_index = bay.get('hb_bay_index')
    if bay_index is None:
        return None

    layout = solver.FaceFrameLayout(root)
    parts = solver.bay_openings(layout, int(bay_index))
    rect = next((r for r in parts['leaves']
                 if r['obj_name'] == opening_cage.name), None)
    if rect is None:
        return None

    # Pivots ordered left-to-right so DOUBLE-door leaves (solver returns
    # left first, then right) line up with the children we found.
    pivots = [c for c in opening_cage.children
              if c.get('hb_part_role') == 'FRONT_PIVOT']
    if not pivots:
        return None
    pivots.sort(key=lambda p: p.location.x)

    return {
        'opening': opening_cage,
        'cab_props': root.face_frame_cabinet,
        'op_props': opening_cage.face_frame_opening,
        'layout': layout,
        'rect': rect,
        'pivots': pivots,
    }


def _apply_swing(ctx, swing_value):
    """Run the leaf solver with an overridden swing value and write the
    resulting transforms to the existing pivots. No recalc, no part
    rebuild.
    """
    proxy = _SwingOverrideProxy(ctx['op_props'], swing_value)
    leaves = solver.front_leaves(
        ctx['layout'], ctx['rect'], ctx['cab_props'], proxy
    )
    for pivot, leaf in zip(ctx['pivots'], leaves):
        pivot.location = leaf['pivot_position']
        pivot.rotation_euler = leaf['pivot_rotation']


class hb_face_frame_OT_open_mode(bpy.types.Operator):
    """Click doors, drawers, and pullouts to toggle them open.
    Esc or right-click exits the mode.
    """
    bl_idname = "hb_face_frame.open_mode"
    bl_label = "Open Mode"
    bl_options = {'REGISTER'}

    _timer = None
    _tweens = None

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        self._tweens = []
        self._timer = context.window_manager.event_timer_add(
            1.0 / TIMER_HZ, window=context.window
        )
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "Open Mode  |  LMB: toggle front  |  Esc / RMB: exit"
        )
        # Register with the HUD's modal registry so the Disable button
        # can ask us to exit. Cleared in _exit.
        from ....operators.viewport_hud import register_active_modal
        register_active_modal(self)
        self._exit_requested = False
        self._exit_timer = None
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _exit(self, context):
        # Snap any in-flight tweens to their target and commit through
        # the prop so the open state is the persistent source of truth.
        for tw in self._tweens:
            try:
                _apply_swing(tw['ctx'], tw['target'])
                tw['ctx']['op_props'].swing_percent = tw['target']
            except (ReferenceError, AttributeError):
                pass
        self._tweens = []
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        # Clear any pending HUD exit-timer and unregister from the HUD
        # modal registry.
        exit_t = getattr(self, '_exit_timer', None)
        if exit_t is not None:
            try:
                context.window_manager.event_timer_remove(exit_t)
            except Exception:
                pass
            self._exit_timer = None
        from ....operators.viewport_hud import unregister_active_modal
        unregister_active_modal(self)
        try:
            context.workspace.status_text_set(None)
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def _handle_click(self, context, event):
        hit = _raycast_under_cursor(context, event)
        if hit is None:
            return False
        front = _find_owning_front(hit)
        if front is None:
            return False
        opening = _find_opening_cage(front)
        if opening is None:
            return False

        now = time.perf_counter()
        existing = next(
            (tw for tw in self._tweens
             if tw['ctx']['opening'] is opening),
            None,
        )
        if existing is not None:
            # Reverse direction from the current interpolated position.
            elapsed = now - existing['t0']
            t = min(1.0, elapsed / existing['duration'])
            current = (existing['start']
                       + (existing['target'] - existing['start'])
                       * _smoothstep(t))
            existing['start'] = current
            existing['target'] = 1.0 - existing['target']
            existing['t0'] = now
            return True

        ctx = _build_tween_context(opening)
        if ctx is None:
            return False
        current = float(ctx['op_props'].swing_percent)
        target = 0.0 if current > 0.5 else 1.0
        self._tweens.append({
            'ctx': ctx,
            'start': current,
            'target': target,
            't0': now,
            'duration': ANIM_DURATION,
        })
        return True

    def _step_tweens(self, context):
        if not self._tweens:
            return
        now = time.perf_counter()
        still_active = []
        for tw in self._tweens:
            elapsed = now - tw['t0']
            try:
                if elapsed >= tw['duration']:
                    # Final value goes through the prop so a later recalc
                    # comes up at the right open state.
                    tw['ctx']['op_props'].swing_percent = tw['target']
                    continue
                t = elapsed / tw['duration']
                swing = (tw['start']
                         + (tw['target'] - tw['start'])
                         * _smoothstep(t))
                _apply_swing(tw['ctx'], swing)
            except (ReferenceError, AttributeError):
                # Underlying objects got deleted - drop this tween.
                continue
            still_active.append(tw)
        self._tweens = still_active
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        # External exit request from the HUD's Disable button. Tween
        # cleanup runs inside _exit (snaps to target, removes timer).
        if getattr(self, '_exit_requested', False):
            self._exit_requested = False
            self._exit(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            self._step_tweens(context)
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Clicks on HUD widgets pass through so the HUD listener can
            # process them (e.g. Disable Open Door Mode). Otherwise the
            # raycast in _handle_click might consume the click.
            try:
                from ....operators.viewport_hud import click_hits_widget
                if click_hits_widget(context, context.area,
                                     event.mouse_region_x,
                                     event.mouse_region_y):
                    return {'PASS_THROUGH'}
            except Exception:
                pass
            if self._handle_click(context, event):
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.type in ('ESC', 'RIGHTMOUSE') and event.value == 'PRESS':
            self._exit(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


def register():
    bpy.utils.register_class(hb_face_frame_OT_open_mode)


def unregister():
    bpy.utils.unregister_class(hb_face_frame_OT_open_mode)
