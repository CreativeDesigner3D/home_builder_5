"""Finished ends marked in the solid viewport.

A closet run paints a finished end panel (and a fixed shelf) in the
room's marking colour, so where a run is finished reads off the
viewport without generating a drawing. Frameless cabinets do the same
for their finished ends: a side or back finished in the cabinet
material, or an applied slab / five-piece panel over it, wears the
marking colour. Everything else keeps the colour it would have had.

The marking is ``obj.color`` only. Drawings show a room through a
collection instance, and Workbench colours an instance by the instance
object, so the marking never reaches a printed page.
"""

import bpy

# Stamped on a part painted as finished, so a part that stops being
# finished can be put back, and a later repaint (a selection mode, the
# style colours) knows to keep the marking.
CUE_KEY = 'hb_finish_cue'

# The sides whose finish is marked. A finished top or bottom is how most
# tall and upper cabinets come in, so marking those would colour nearly
# every cabinet and say nothing.
CUE_SIDES = ('LEFT', 'RIGHT', 'BACK')

_DEFAULT_COLOR = (1.0, 0.35, 0.05, 1.0)
_PLAIN = (1.0, 1.0, 1.0, 1.0)


def marking_color(obj=None):
    """The room's marking colour, shared with the closet library so a
    room reads the same whatever it is built from."""
    try:
        from ..closets import types_closets
        return tuple(types_closets.lock_shelf_color(obj))
    except Exception:
        return _DEFAULT_COLOR


def cue_color(obj):
    """The marking colour when ``obj`` is a marked finished part, else None."""
    if obj is None or not obj.get(CUE_KEY):
        return None
    return marking_color(obj)


def _plain_color(obj):
    """What the part wears unmarked: its style colour, or white."""
    try:
        from ..face_frame import props_hb_face_frame
        return (props_hb_face_frame.style_color_for_object(
            obj, highlight=False) or _PLAIN)
    except Exception:
        return _PLAIN


def finished_parts(cabinet_obj):
    """The parts of a frameless cabinet that finish one of CUE_SIDES."""
    from .operators import ops_finished_ends
    from . import solver_frameless
    parts = []
    carcass = None
    for side in CUE_SIDES:
        condition = ops_finished_ends.finish_condition(cabinet_obj, side)
        if condition in ('SLAB', '5PIECE'):
            for child in cabinet_obj.children:
                if child.get('IS_APPLIED_END_' + side):
                    parts.append(child)
                    parts.extend(c for c in child.children_recursive
                                 if not c.get('IS_2D_ANNOTATION'))
        elif condition == 'FINISHED':
            if carcass is None:
                carcass = solver_frameless.carcass_parts(cabinet_obj)
            part = carcass.get(ops_finished_ends.FINISH_SIDE_ROLES[side])
            if part is not None:
                parts.append(part)
    return parts


def mark_cabinet(cabinet_obj):
    """Paint a frameless cabinet's finished ends in the marking colour
    and put back any part that is no longer finished. Returns how many
    parts are marked."""
    if cabinet_obj is None or not cabinet_obj.get('IS_FRAMELESS_CABINET_CAGE'):
        return 0
    try:
        marked = finished_parts(cabinet_obj)
    except Exception:
        return 0
    marked_names = {o.name for o in marked}
    color = marking_color(cabinet_obj)
    for obj in marked:
        obj[CUE_KEY] = True
        obj.color = color
    for obj in cabinet_obj.children_recursive:
        if obj.get(CUE_KEY) and obj.name not in marked_names:
            del obj[CUE_KEY]
            obj.color = _plain_color(obj)
    return len(marked)


def mark_scene(scene=None):
    """Mark every frameless cabinet in a room (or every room)."""
    objs = scene.objects if scene is not None else bpy.data.objects
    total = 0
    for obj in objs:
        if obj.get('IS_FRAMELESS_CABINET_CAGE'):
            total += mark_cabinet(obj)
    return total
