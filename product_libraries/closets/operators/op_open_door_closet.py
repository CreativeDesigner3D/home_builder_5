"""Open Door mode for closets (Parts selection mode).

Mirrors the face_frame open-mode interaction: a persistent modal that
passes non-door clicks through (so viewport nav / selection keep
working). Clicking a door front tweens it open or closed by swinging it
about its hinge edge. The tween writes the door transform directly each
tick (no recalc); on completion the open state is committed to the
door's hb_door_open idprop so it survives later recalcs.

Entry point is the "Open Door" pill on the closet overlay's HUD row,
shown only in Parts mode.
"""
import time
import bpy
from bpy_extras import view3d_utils

from .. import types_closets

ANIM_DURATION = 0.35
TIMER_HZ = 60

_active = None


def open_door_is_active():
    return _active is not None


def request_open_door_exit():
    if _active is not None:
        _active._exit_requested = True


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


_OPENABLE = None  # set lazily from types_closets roles


def _raycast_front(context, event):
    """Return the openable front (door or drawer front) under the cursor,
    or None. Walks up from the hit object so a click on a pull or box
    still resolves to the front."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None
    coord = (event.mouse_region_x, event.mouse_region_y)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    dg = context.evaluated_depsgraph_get()
    hit, _loc, _n, _i, obj, _m = context.scene.ray_cast(dg, origin, direction)
    if not hit or obj is None:
        return None
    door_role = types_closets.PART_ROLE_DOOR
    front_role = types_closets.PART_ROLE_DRAWER_FRONT
    box_role = types_closets.PART_ROLE_DRAWER_BOX
    cur = obj
    while cur is not None:
        role = cur.get('hb_part_role')
        if role in (door_role, front_role):
            return cur
        if role == box_role:
            # Clicking the box opens its drawer front.
            idx = cur.get('hb_drawer_index', 0)
            parent = cur.parent
            if parent is not None:
                for c in parent.children:
                    if (c.get('hb_part_role') == front_role
                            and c.get('hb_drawer_index', 0) == idx):
                        return c
        cur = cur.parent
    return None


class hb_closets_OT_open_door_mode(bpy.types.Operator):
    """Toggle Open Door mode. Click a door to swing it, a drawer to
    slide it out; click again to close. Esc or right-click exits."""
    bl_idname = "hb_closets.open_door_mode"
    bl_label = "Open Door"
    bl_options = {'REGISTER'}

    _timer = None
    _tweens = None
    _exit_requested = False

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        global _active
        self._tweens = []
        self._exit_requested = False
        self._timer = context.window_manager.event_timer_add(
            1.0 / TIMER_HZ, window=context.window)
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "Open Door  |  LMB: swing a door  |  Esc / RMB: exit")
        _active = self
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _apply(self, part, kind, frac):
        if kind == 'DOOR':
            types_closets.apply_door_open(part, frac)
        else:
            types_closets.apply_drawer_open(part, frac)

    def _commit(self, part, kind, target):
        # Held as a fraction so a click and the Open Door / Open Drawer
        # percentage speak the same language. Whatever lands here is
        # this one front's own answer and outranks the percentage until
        # the percentage is set again.
        key = 'hb_door_open' if kind == 'DOOR' else 'hb_drawer_open'
        part[key] = 1.0 if target >= 0.5 else 0.0

    def _exit(self, context):
        global _active
        # Snap any in-flight tweens to their target and commit the state.
        for tw in self._tweens:
            try:
                self._apply(tw['part'], tw['kind'], tw['target'])
                self._commit(tw['part'], tw['kind'], tw['target'])
            except (ReferenceError, KeyError):
                pass
        self._tweens = []
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        try:
            context.workspace.status_text_set(None)
        except Exception:
            pass
        _active = None
        if context.area:
            context.area.tag_redraw()

    def _toggle_front(self, part):
        kind = ('DOOR'
                if part.get('hb_part_role') == types_closets.PART_ROLE_DOOR
                else 'DRAWER')
        now = time.perf_counter()
        existing = next((tw for tw in self._tweens if tw['part'] is part),
                        None)
        if existing is not None:
            elapsed = now - existing['t0']
            t = min(1.0, elapsed / ANIM_DURATION)
            current = (existing['start']
                       + (existing['target'] - existing['start'])
                       * _smoothstep(t))
            existing['start'] = current
            existing['target'] = 1.0 - existing['target']
            existing['t0'] = now
            return
        # Where this front is standing at the moment, which is the
        # opening's percentage when it has never been clicked, so a
        # part-open front swings on from where it is rather than jumping.
        current = types_closets.current_open_frac(part)
        self._tweens.append({
            'part': part,
            'kind': kind,
            'start': current,
            'target': 0.0 if current > 0.5 else 1.0,
            't0': now,
        })

    def _step(self, context):
        if not self._tweens:
            return
        now = time.perf_counter()
        still = []
        for tw in self._tweens:
            elapsed = now - tw['t0']
            try:
                if elapsed >= ANIM_DURATION:
                    self._apply(tw['part'], tw['kind'], tw['target'])
                    self._commit(tw['part'], tw['kind'], tw['target'])
                    continue
                t = elapsed / ANIM_DURATION
                frac = (tw['start']
                        + (tw['target'] - tw['start']) * _smoothstep(t))
                self._apply(tw['part'], tw['kind'], frac)
            except (ReferenceError, KeyError):
                continue
            still.append(tw)
        self._tweens = still
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        if self._exit_requested:
            self._exit_requested = False
            self._exit(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            self._step(context)
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Clicks on the overlay pill row pass through so the Open Door
            # pill can toggle this mode off.
            try:
                from .. import gpu_overlay_closets as ov
                mx, my = event.mouse_region_x, event.mouse_region_y
                mode = ov._active_mode(context)
                for _l, _k, (tx, ty, tw, th) in ov._filter_pill_rects(
                        context, context.area, mode):
                    if tx <= mx <= tx + tw and ty <= my <= ty + th:
                        return {'PASS_THROUGH'}
            except Exception:
                pass
            front = _raycast_front(context, event)
            if front is not None:
                self._toggle_front(front)
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._exit(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


def register():
    bpy.utils.register_class(hb_closets_OT_open_door_mode)


def unregister():
    global _active
    _active = None
    bpy.utils.unregister_class(hb_closets_OT_open_door_mode)
