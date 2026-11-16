"""An apron behind the doors of an opening.

A doors opening can ask for an apron: a fixed panel across the top of
the opening, standing behind the doors at the front of the cabinet, as
an apron-front or farmhouse sink needs. The doors stay full height and
close over it.

Apron Height is measured down from the top of the doors, so it lines
up with a drawer front of the same height in the cabinet next door.
The panel itself hangs from the top of the opening and is shorter by
the top overlay of the doors.
"""

import bpy
import math
from ...units import inch
from . import solver_frameless

# Prompts on the doors opening. Neither has to exist: an opening
# without them has no apron.
ADD_KEY = 'Add Apron'
HEIGHT_KEY = 'Apron Height'
DEFAULT_HEIGHT = inch(7.0)

APRON_ROLE = 'OPENING_APRON'
APRON_TAG = 'IS_OPENING_APRON'


def wanted(insert_obj):
    """Whether the opening's doors have an apron behind them."""
    return bool(insert_obj is not None and 'Door Swing' in insert_obj
                and insert_obj.get(ADD_KEY, False))


def height(insert_obj):
    try:
        return max(float(insert_obj.get(HEIGHT_KEY, DEFAULT_HEIGHT)), 0.0)
    except (TypeError, ValueError):
        return DEFAULT_HEIGHT


def aprons(insert_obj):
    return [c for c in insert_obj.children
            if c.get(solver_frameless.PART_ROLE_KEY) == APRON_ROLE]


def _new_apron(insert_obj):
    from . import types_frameless
    part = types_frameless.CabinetPart()
    part.create('Apron')
    obj = part.obj
    obj.parent = insert_obj
    obj[solver_frameless.PART_ROLE_KEY] = APRON_ROLE
    obj[APRON_TAG] = True
    # Behind the doors: drawn as hidden lines, picked with the interior.
    obj['IS_FRAMELESS_INTERIOR_PART'] = True
    # Length across the opening, width down from its top, thickness in
    # towards the back.
    obj.rotation_euler = (math.radians(-90.0), 0.0, 0.0)
    wanted_colls = list(insert_obj.users_collection)
    if wanted_colls and set(obj.users_collection) != set(wanted_colls):
        for coll in list(obj.users_collection):
            coll.objects.unlink(obj)
        for coll in wanted_colls:
            coll.objects.link(obj)
    root = solver_frameless.cabinet_root(insert_obj)
    if root is not None:
        solver_frameless._paint_like_cabinet(root, obj)
    return obj


def solve(insert_obj, dim_x, dim_z, top_overlay):
    """Build, size and place the opening's apron, or take it away."""
    existing = aprons(insert_obj)
    root = solver_frameless.cabinet_root(insert_obj)
    mt = inch(0.75)
    if root is not None:
        mt = float(solver_frameless.prompt(root, 'Material Thickness', mt))
    # Down from the top of the doors, never past the opening's bottom.
    panel = min(height(insert_obj) - top_overlay, dim_z)
    if not wanted(insert_obj) or panel <= 0.0 or dim_x <= 0.0:
        for obj in existing:
            bpy.data.objects.remove(obj, do_unlink=True)
        return None
    for obj in existing[1:]:
        bpy.data.objects.remove(obj, do_unlink=True)
    apron = existing[0] if existing else _new_apron(insert_obj)
    solver_frameless.set_part(apron, (0.0, 0.0, dim_z), length=dim_x,
                              width=panel, thickness=mt)
    return apron
