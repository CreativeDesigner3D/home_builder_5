"""Selection-mode cages in Material Preview and Rendered shading.

The frameless side of face_frame.quiet_cages, which explains the idea:
in those two shadings a cage mode (Cabinets, Bays, Openings) keeps its
cages hidden so the finished cabinets are not traced over with cage
boxes. A click lands on a part and is promoted to the cage the mode
would have offered; only selected cages are revealed, and they go back
into hiding once nothing selects them. Solid shading is untouched.

The shading test is the face frame module's; the hooks are this
module's own, and only run on the Frameless tab, so the two libraries
never promote the same click.
"""
import bpy

from ... import hb_utils

# Modes whose selection targets are cages. Interiors and Parts offer
# real parts, which are visible geometry in any shading.
CAGE_MODES = {'Cabinets', 'Bays', 'Openings'}

_TICK = 0.25
# Ticks between full passes while the selection has not changed.
_FULL_PASS_EVERY = 8
_msgbus_owner = object()
_busy = False
_last_selection = None
_ticks_since_full = 0


# ---------------------------------------------------------------------------
# State queries
# ---------------------------------------------------------------------------

def _scene_mode(context=None):
    """The frameless selection mode when it is a cage mode on the
    Frameless tab of a room scene, else None."""
    scene = getattr(context or bpy.context, 'scene', None)
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'FRAMELESS':
        return None
    fl = getattr(scene, 'hb_frameless', None)
    mode = getattr(fl, 'frameless_selection_mode', '')
    return mode if mode in CAGE_MODES else None


def quiet_mode(context=None):
    """The active cage mode while cages should stay hidden, else None."""
    # Imported at call time: the face frame package imports this one.
    from ..face_frame.quiet_cages import shading_is_quiet
    mode = _scene_mode(context)
    if mode is None:
        return None
    return mode if shading_is_quiet(context) else None


def _is_selected(obj, view_layer=None, selected_names=None):
    if selected_names is not None:
        return obj.name in selected_names
    try:
        if view_layer is not None:
            return obj.select_get(view_layer=view_layer)
        return obj.select_get()
    except RuntimeError:
        return False


def is_partless(obj):
    """True for a cage with no visible part under it -- an empty opening,
    an appliance showing no model. Promotion needs a part to click, so
    these cages stay revealed to remain clickable."""
    for child in obj.children_recursive:
        if child.type != 'MESH' or child.get('IS_GEONODE_CAGE'):
            continue
        if not child.hide_viewport:
            return False
    return True


def keep_hidden(obj, mode, selected_names=None):
    """True when a mode-matching object takes the hidden path instead of
    being revealed: it is a cage, the mode is a cage mode on the
    Frameless tab, the shading is quiet, nothing has it selected, and it
    has a part to click."""
    if mode not in CAGE_MODES or not obj.get('IS_GEONODE_CAGE'):
        return False
    if _is_selected(obj, selected_names=selected_names):
        return False
    if quiet_mode() is None:
        return False
    return not is_partless(obj)


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

def _matches(obj, mode):
    from .operators.ops_placement import selection_mode_matches
    return selection_mode_matches(obj, mode)


def resolve_target(obj, mode):
    """The object the mode would have offered for a click on ``obj``: the
    first of obj and its ancestors the mode matches, else None.

    A countertop (and anything under it) is its own pick: island tops are
    parented to a cabinet, and promoting them would leave the top
    impossible to click."""
    o = obj
    while o is not None:
        if o.get('IS_COUNTERTOP'):
            return None
        if _matches(o, mode):
            return o
        o = o.parent
    return None


def _toggle(obj, mode, show):
    from .operators.ops_placement import (SELECTION_MODE_TAGS,
                                          toggle_cabinet_color)
    toggle_cabinet_color(obj, show, type_name=SELECTION_MODE_TAGS[mode],
                         dont_show_parent=False)


def _sweep(scene, view_layer, mode):
    """Hide every revealed cage nothing selects, except partless ones."""
    with hb_utils.children_index():
        for obj in scene.objects:
            if not obj.get('IS_GEONODE_CAGE') or obj.hide_viewport:
                continue
            if not _matches(obj, mode):
                continue
            if not _is_selected(obj, view_layer) and not is_partless(obj):
                _toggle(obj, mode, False)


def promote(context=None, force=True):
    """Swap selected parts for the cages the current quiet mode offers,
    then hide any revealed cage that is no longer selected.

    With ``force`` off (the timer) nothing runs while the selection is
    the same as last time, and the scene-wide sweep only runs every
    _FULL_PASS_EVERY ticks."""
    global _busy, _last_selection, _ticks_since_full
    if _busy:
        return
    context = context or bpy.context
    mode = quiet_mode(context)
    if mode is None:
        return
    scene = getattr(context, 'scene', None)
    view_layer = getattr(context, 'view_layer', None)
    if scene is None or view_layer is None:
        return
    active = view_layer.objects.active
    selected = [o for o in view_layer.objects.selected if o is not None]
    signature = (mode, active.name if active is not None else None,
                 frozenset(o.name for o in selected))
    if not force:
        _ticks_since_full += 1
        if (signature == _last_selection
                and _ticks_since_full < _FULL_PASS_EVERY):
            return
    _last_selection = signature
    _ticks_since_full = 0
    targets = []
    demoted = []
    for o in selected:
        target = resolve_target(o, mode)
        if target is None:
            continue            # walls, doors, annotations: left alone
        if target not in targets:
            targets.append(target)
        if target is not o:
            demoted.append(o)
    active_target = resolve_target(active, mode) if active is not None else None
    _busy = True
    try:
        if demoted or (active_target is not None
                       and active_target is not active):
            for o in demoted:
                try:
                    o.select_set(False, view_layer=view_layer)
                except RuntimeError:
                    pass
            for target in targets:
                _toggle(target, mode, True)
            if active_target is not None:
                view_layer.objects.active = active_target
        _sweep(scene, view_layer, mode)
    finally:
        _busy = False


def reapply_mode(context=None):
    """Re-run the mode over the scene without losing the selection: what
    the shading flip needs, where the toggle operator would deselect."""
    from .operators.ops_placement import apply_frameless_selection_mode
    context = context or bpy.context
    view_layer = getattr(context, 'view_layer', None)
    if view_layer is None:
        return
    prev_selected = {o.name for o in view_layer.objects
                     if _is_selected(o, view_layer)}
    prev_active = view_layer.objects.active
    apply_frameless_selection_mode(context)
    for o in view_layer.objects:
        try:
            o.select_set(o.name in prev_selected, view_layer=view_layer)
        except RuntimeError:
            pass
    if prev_active is not None:
        try:
            view_layer.objects.active = prev_active
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

def _tick():
    if quiet_mode() is None:
        return None             # stops until the next mode / shading change
    try:
        promote(force=False)
    except Exception as e:      # a timer that raises is unregistered
        print(f"frameless quiet_cages: {e}")
    return _TICK


def ensure_timer():
    try:
        if quiet_mode() is None:
            return
    except AttributeError:
        return                  # restricted context during startup
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=_TICK)


def after_mode_applied():
    """Called at the end of every selection-mode apply."""
    ensure_timer()


def _on_active_changed():
    try:
        promote()
    except Exception as e:
        print(f"frameless quiet_cages: {e}")


def _on_view_changed():
    """The shading or the library tab changed: cages come and go."""
    if _scene_mode() is None:
        return
    try:
        reapply_mode()
    except Exception as e:
        print(f"frameless quiet_cages: {e}")
    ensure_timer()


def ensure_subscriptions():
    """(Re)subscribe. msgbus subscriptions do not survive a .blend load,
    so load_post calls this too."""
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        owner=_msgbus_owner, args=(), notify=_on_active_changed)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.View3DShading, 'type'),
        owner=_msgbus_owner, args=(), notify=_on_view_changed)
    ensure_timer()


def _deferred_setup():
    try:
        ensure_subscriptions()
    except Exception as e:
        print(f"frameless quiet_cages: setup skipped: {e}")
    return None


def register():
    # Startup registration runs under a restricted context; subscribe once
    # the main loop is up.
    bpy.app.timers.register(_deferred_setup, first_interval=0.5)


def unregister():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    if bpy.app.timers.is_registered(_deferred_setup):
        bpy.app.timers.unregister(_deferred_setup)
