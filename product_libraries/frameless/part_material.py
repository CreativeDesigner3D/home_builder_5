"""A part's own material: one board of a cabinet or product painted with
a material other than the one its place in the cabinet gives it (a
filler's return in the finish, a shelf in the door material).

The choice is stored on the part, so it holds through restyles and
re-solves: OVERRIDE_KEY names which of a style's materials the part
wears, STYLE_KEY which style (empty = the one its cabinet wears).
apply_materials_to_cabinet asks `materials()` for every part it paints."""

import bpy

from . import edgebanding_frameless as eb
from . import solver_frameless

OVERRIDE_KEY = 'hb_part_material_override'
STYLE_KEY = 'hb_part_material_style'

AUTO = 'AUTO'
CHOICES = (
    (AUTO, "Automatic"),
    ('FINISH', "Finish"),
    ('INTERIOR', "Interior"),
    ('FRONT', "Door Fronts"),
)
CHOICE_LABELS = dict(CHOICES)
OWN_STYLE = "Cabinet's Style"


def owner(obj):
    """The cabinet or product whose style paints the part; a misc part
    is its own."""
    if obj is None:
        return None
    if obj.get('IS_FRAMELESS_MISC_PART'):
        return obj
    return eb.owner_root(obj)


def takes_override(obj):
    """A board of a cabinet or product, or a misc part. Door and drawer
    fronts take their material from the front style instead, and a
    face frame product built on these parts wears the face frame styles."""
    root = owner(obj)
    if root is None or root.get('IS_FACE_FRAME_PRODUCT_CAGE'):
        return False
    return (obj is not None
            and bool(obj.get(solver_frameless.PART_ROLE_KEY)
                     or obj.get('IS_FRAMELESS_MISC_PART'))
            and 'CABINET_PART' in obj
            and not obj.get('IS_CABINET_FRONT'))


def choice(obj):
    value = obj.get(OVERRIDE_KEY)
    return value if value in CHOICE_LABELS else AUTO


def _styles():
    from ... import hb_project
    try:
        return hb_project.get_main_scene().hb_frameless.cabinet_styles
    except Exception:
        return ()


def style_names():
    return [s.name for s in _styles()]


def style_choice(obj):
    name = obj.get(STYLE_KEY) or ''
    return name if name in style_names() else OWN_STYLE


def materials(obj, own_style):
    """(top, bottom, edge) for a part with its own material, or None to
    leave it to the rules. A style since deleted falls back to the
    cabinet's own rather than dropping the choice."""
    picked = choice(obj)
    if picked == AUTO:
        return None
    style = own_style
    name = obj.get(STYLE_KEY)
    if name:
        for s in _styles():
            if s.name == name:
                style = s
                break
    carcass_edge, front_edge = style.get_edge_materials()
    if picked == 'FINISH':
        mat, _ = style.get_finish_material()
        return mat, mat, carcass_edge
    if picked == 'INTERIOR':
        mat, _ = style.get_interior_material()
        return mat, mat, carcass_edge
    mat, _ = style.get_front_material()
    return mat, mat, front_edge


def restyle(obj):
    """Repaint the part's cabinet or product so the choice shows."""
    root = owner(obj)
    if root is None:
        return
    style = eb._style(root)
    if style is not None:
        style.apply_materials_to_cabinet(root)


def set_choice(obj, value):
    if value == AUTO:
        obj.pop(OVERRIDE_KEY, None)
    elif value in CHOICE_LABELS:
        obj[OVERRIDE_KEY] = value
    restyle(obj)


def set_style(obj, name):
    if name == OWN_STYLE or name not in style_names():
        obj.pop(STYLE_KEY, None)
    else:
        obj[STYLE_KEY] = name
    restyle(obj)


def summary(obj):
    picked = choice(obj)
    if picked == AUTO:
        return CHOICE_LABELS[AUTO]
    name = obj.get(STYLE_KEY)
    label = CHOICE_LABELS[picked]
    return "%s (%s)" % (label, name) if name else label
