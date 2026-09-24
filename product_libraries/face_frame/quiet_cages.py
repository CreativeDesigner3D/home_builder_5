"""Selection-mode cages in Material Preview and Rendered shading.

A cage mode (Cabinets, Bays, Openings, Applied Panels) draws its cages
solid and in front so a click lands on the cage rather than the door
behind it. In Solid shading the cage is a light wash and reads fine. In
Material Preview and Rendered the cage surfaces are already invisible
(camera ray visibility is off on every cage) and what is left is the
wireframe overlay tracing every cage box in front of the finished
cabinets - which is what makes those views busy.

So in those two shadings a cage mode keeps its cages hidden. The click
lands on a part, and the part is promoted to the cage the mode would
have offered (the first of its ancestors the mode matches). Only cages
that end up selected are revealed, and they go back into hiding once
nothing selects them. Solid shading is untouched.

Two hooks feed this: a msgbus subscription on the active object (instant
promotion on a click) and a light timer that runs only while a cage mode
is quiet (box select, deselect-all and undo change the selection without
publishing an active-object change). A second msgbus subscription on the
viewport shading re-applies the mode when the user flips between Solid
and Material Preview, so the cages come and go with the shading.
"""
import bpy

from ... import hb_utils

# Shading types where cages stay hidden.
QUIET_SHADING_TYPES = {'MATERIAL', 'RENDERED'}

# Opening contents with no front to click through to the opening's cage.
_FRONTLESS_FRONT_TYPES = frozenset({'NONE', 'APPLIANCE'})

# Modes whose selection targets are cages. Face Frame, Interiors and
# Parts offer real parts, which are visible geometry in any shading.
CAGE_MODES = {'Cabinets', 'Bays', 'Openings', 'Applied Panels'}

_TICK = 0.25
# Ticks between full passes while the selection has not changed. The
# per-tick check only reads the selected objects; the full pass walks
# the scene for revealed cages nothing selects.
_FULL_PASS_EVERY = 8
_msgbus_owner = object()
_busy = False
_last_selection = None
_ticks_since_full = 0


# ---------------------------------------------------------------------------
# State queries
# ---------------------------------------------------------------------------

def _view3d_space(context=None):
    """The 3D view whose shading decides: the one in context, else the
    largest one on the screen (timers and msgbus callbacks have none)."""
    context = context or bpy.context
    space = getattr(context, 'space_data', None)
    if space is not None and getattr(space, 'type', '') == 'VIEW_3D':
        return space
    screens = []
    screen = getattr(context, 'screen', None)
    if screen is not None:
        screens.append(screen)
    else:
        wm = getattr(context, 'window_manager', None) \
            or bpy.context.window_manager
        screens.extend(w.screen for w in wm.windows)
    best = None
    for scr in screens:
        for area in scr.areas:
            if area.type != 'VIEW_3D':
                continue
            if best is None \
                    or area.width * area.height > best.width * best.height:
                best = area
    return best.spaces.active if best is not None else None


def shading_is_quiet(context=None):
    space = _view3d_space(context)
    return space is not None \
        and space.shading.type in QUIET_SHADING_TYPES


def _scene_props(context=None):
    scene = getattr(context or bpy.context, 'scene', None)
    return getattr(scene, 'hb_face_frame', None) if scene else None


def quiet_mode(context=None):
    """The active cage mode while cages should stay hidden, else None."""
    ff = _scene_props(context)
    if ff is None or not ff.face_frame_selection_mode_enabled:
        return None
    mode = ff.face_frame_selection_mode
    if mode not in CAGE_MODES:
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


def is_frontless(obj):
    """True for an opening cage with no door or drawer in front of it, or
    a bay cage holding one. Promotion needs a part under the cage to click,
    and what shows through an empty opening (sides, back, stiles) belongs
    to the cabinet, so these cages stay revealed to remain clickable."""
    from . import types_face_frame
    if obj.get(types_face_frame.TAG_OPENING_CAGE):
        return obj.face_frame_opening.front_type in _FRONTLESS_FRONT_TYPES
    if not obj.get(types_face_frame.TAG_BAY_CAGE):
        return False
    with hb_utils.children_index():
        stack = list(obj.children)
        while stack:
            o = stack.pop()
            if o.get(types_face_frame.TAG_OPENING_CAGE):
                if o.face_frame_opening.front_type in _FRONTLESS_FRONT_TYPES:
                    return True
            elif o.get(types_face_frame.TAG_SPLIT_NODE):
                stack.extend(o.children)
    return False


def keep_hidden(obj, mode, selected_names=None):
    """True when a mode-matching object takes the hidden path instead of
    being revealed: it is a cage, the mode is a cage mode, the shading is
    quiet, nothing has it selected, and it has a front to click.
    ``selected_names`` stands in for the live selection where a caller
    has snapshotted it."""
    if mode not in CAGE_MODES or not obj.get('IS_GEONODE_CAGE'):
        return False
    if _is_selected(obj, selected_names=selected_names):
        return False
    if not shading_is_quiet():
        return False
    return not is_frontless(obj)


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

def _matches(obj, mode):
    from .operators.ops_cabinet import _selection_mode_matches
    return _selection_mode_matches(obj, mode)


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


def _reveal(obj, mode):
    from .operators.ops_cabinet import SELECTION_MODE_TAGS
    from ..frameless.operators.ops_placement import toggle_cabinet_color
    toggle_cabinet_color(obj, True,
                         type_name=SELECTION_MODE_TAGS.get(mode, ''),
                         dont_show_parent=False)


def _hide(obj, mode):
    from .operators.ops_cabinet import SELECTION_MODE_TAGS
    from ..frameless.operators.ops_placement import toggle_cabinet_color
    toggle_cabinet_color(obj, False,
                         type_name=SELECTION_MODE_TAGS.get(mode, ''))


def _sweep(scene, view_layer, mode):
    """Hide every revealed cage nothing selects, except frontless ones."""
    with hb_utils.children_index():
        for obj in scene.objects:
            if not obj.get('IS_GEONODE_CAGE') or obj.hide_viewport:
                continue
            if not _matches(obj, mode):
                continue
            if not _is_selected(obj, view_layer) and not is_frontless(obj):
                _hide(obj, mode)


def promote(context=None, force=True):
    """Swap selected parts for the cages the current quiet mode offers,
    then hide any revealed cage that is no longer selected.

    With ``force`` off (the timer) nothing runs while the selection is
    the same as last time, and the scene-wide sweep for revealed cages
    only runs every _FULL_PASS_EVERY ticks - so an idle scene costs the
    timer a read of the selected objects and nothing more."""
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
    # The selected collection can hand back None for a base whose
    # object was just removed; the timer can land right after one.
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
                _reveal(target, mode)
            if active_target is not None:
                view_layer.objects.active = active_target
        _sweep(scene, view_layer, mode)
    finally:
        _busy = False


def reapply_mode(context=None):
    """Re-run the mode over the scene without losing the selection: what
    the shading flip needs, where the toggle operator would deselect."""
    from .operators.ops_cabinet import apply_face_frame_selection_mode
    context = context or bpy.context
    view_layer = getattr(context, 'view_layer', None)
    if view_layer is None:
        return
    prev_selected = {o.name for o in view_layer.objects
                     if _is_selected(o, view_layer)}
    prev_active = view_layer.objects.active
    apply_face_frame_selection_mode(context)
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
        print(f"quiet_cages: {e}")
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
        print(f"quiet_cages: {e}")


def _on_shading_changed():
    ff = _scene_props()
    if ff is None or not ff.face_frame_selection_mode_enabled:
        return
    if ff.face_frame_selection_mode not in CAGE_MODES:
        return
    try:
        reapply_mode()
    except Exception as e:
        print(f"quiet_cages: {e}")
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
        owner=_msgbus_owner, args=(), notify=_on_shading_changed)
    ensure_timer()


def _deferred_setup():
    try:
        ensure_subscriptions()
    except Exception as e:
        print(f"quiet_cages: setup skipped: {e}")
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
