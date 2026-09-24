"""Open mode for frameless cabinets.

Stays running until Esc / right-click. While active, left-clicks on doors,
drawer fronts and pullout fronts toggle them open or closed with a short
tween. Clicks that don't hit an openable front pass through, so normal
viewport selection keeps working.

Each tween tick writes the opening's Open Amount and re-solves only that
opening's fronts, pulls and drawer boxes -- nothing else in the cabinet
reads the value, so no full recalc is needed.
"""

import time
import bpy
from bpy_extras import view3d_utils

from .. import solver_frameless


ANIM_DURATION = 0.4
TIMER_HZ = 60


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def openable_front(obj):
    """The door, drawer or pullout front at or above ``obj`` (a pull, a
    drawer box or an insert count as their front), or None. False fronts
    and appliance panels don't open."""
    while obj is not None:
        if obj.get('IS_CABINET_FRONT'):
            if obj.get('False Front', False):
                return None
            if (obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT')
                    or obj.get('IS_PULLOUT_FRONT')
                    or obj.get('IS_FLIP_UP_DOOR')):
                return obj
            return None
        obj = obj.parent
    return None


def opening_for_front(front_obj):
    """The insert cage that owns a front, or None."""
    parent = front_obj.parent if front_obj is not None else None
    if parent is not None and parent.get('IS_FRAMELESS_OPENING_CAGE'):
        return parent
    return None


def opening_to_toggle(obj):
    """The opening a command on ``obj`` opens or closes: the owner of the
    front it is part of, or the opening itself when it holds a front that
    opens."""
    opening = opening_for_front(openable_front(obj))
    if opening is None and obj is not None and obj.get('IS_FRAMELESS_OPENING_CAGE'):
        if any(openable_front(c) is c for c in obj.children):
            opening = obj
    return opening


def set_open_amount(insert_obj, amount):
    """Write an opening's open amount and move its fronts to match."""
    insert_obj[solver_frameless.OPEN_KEY] = min(max(float(amount), 0.0), 1.0)
    solver_frameless.solve_insert_parts(insert_obj)


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
        depsgraph, ray_origin, view_vector)
    return obj if hit else None


class hb_frameless_OT_open_mode(bpy.types.Operator):
    """Click doors, drawers, and pullouts to toggle them open.
    Esc or right-click exits the mode.
    """
    bl_idname = "hb_frameless.open_mode"
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
            1.0 / TIMER_HZ, window=context.window)
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "Open Mode  |  LMB: toggle front  |  Esc / RMB: exit")
        # Register with the HUD so its button can ask us to exit.
        from ....operators.viewport_hud import register_active_modal
        register_active_modal(self)
        self._exit_requested = False
        self._exit_timer = None
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _exit(self, context):
        # Snap any in-flight tweens to where they were heading.
        for tw in self._tweens:
            try:
                set_open_amount(tw['opening'], tw['target'])
            except (ReferenceError, AttributeError):
                pass
        self._tweens = []
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
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
        opening = opening_for_front(openable_front(hit))
        if opening is None:
            return False

        now = time.perf_counter()
        existing = next((tw for tw in self._tweens
                         if tw['opening'] is opening), None)
        if existing is not None:
            # Reverse from wherever it has got to.
            t = min(1.0, (now - existing['t0']) / existing['duration'])
            current = (existing['start']
                       + (existing['target'] - existing['start'])
                       * _smoothstep(t))
            existing['start'] = current
            existing['target'] = 1.0 - existing['target']
            existing['t0'] = now
            return True

        current = solver_frameless.open_amount(opening)
        self._tweens.append({
            'opening': opening,
            'start': current,
            'target': 0.0 if current > 0.5 else 1.0,
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
                    set_open_amount(tw['opening'], tw['target'])
                    continue
                t = elapsed / tw['duration']
                set_open_amount(tw['opening'],
                                tw['start'] + (tw['target'] - tw['start'])
                                * _smoothstep(t))
            except (ReferenceError, AttributeError):
                # The opening was deleted mid-tween.
                continue
            still_active.append(tw)
        self._tweens = still_active
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        if getattr(self, '_exit_requested', False):
            self._exit_requested = False
            self._exit(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            self._step_tweens(context)
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Clicks on HUD widgets pass through to the HUD.
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


class hb_frameless_OT_toggle_front_open(bpy.types.Operator):
    """Open or close the door, drawer or pullout the clicked part belongs to"""
    bl_idname = "hb_frameless.toggle_front_open"
    bl_label = "Open / Close"
    bl_description = "Open or close this door or drawer"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return opening_to_toggle(context.object) is not None

    def execute(self, context):
        opening = opening_to_toggle(context.object)
        if opening is None:
            return {'CANCELLED'}
        current = solver_frameless.open_amount(opening)
        set_open_amount(opening, 0.0 if current > 0.5 else 1.0)
        return {'FINISHED'}


classes = (
    hb_frameless_OT_open_mode,
    hb_frameless_OT_toggle_front_open,
)

register, unregister = bpy.utils.register_classes_factory(classes)
