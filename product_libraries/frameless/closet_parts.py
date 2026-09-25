"""Closet and mudroom parts for frameless cabinets.

Coat hooks: any interior can carry a row of hooks on its back wall -- a
count, a height and a hook model from the closet library -- spread
evenly across it. Shoe shelves: an interior type of shelves tilted up
towards the back, each with a shoe stop along its front edge.
"""

import bpy
import math
from ...units import inch
from . import solver_frameless

HOOK_COUNT_KEY = 'Coat Hooks'
HOOK_HEIGHT_KEY = 'Coat Hook Height'
HOOK_STYLE_KEY = 'Coat Hook Style'
HOOK_TAG = 'IS_COAT_HOOK'
HOOK_SIGNATURE_KEY = 'hb_hook_signature'
HOOK_STYLES = [
    ('Hook Coat.blend', "Coat Hook", "Single coat hook"),
    ('Hook Double.blend', "Double Hook", "Double prong hook"),
    ('Hook Waterfall.blend', "Waterfall Hook", "Cascading hook"),
]
# Unset height: this far below the top of the interior.
HOOK_FROM_TOP = inch(10.0)

SHOE_TAG = 'IS_FRAMELESS_SHOE_SHELVES'
SHOE_PART_TAG = 'IS_SHOE_SHELF_PART'
SHOE_SIGNATURE_KEY = 'hb_shoe_signature'
SHOE_QTY_KEY = 'Shoe Shelf Quantity'
SHOE_ANGLE_KEY = 'Shoe Shelf Angle'
SHOE_STOP_KEY = 'Shoe Stop Height'
SHOE_PITCH = inch(9.0)       # shelf spacing an unset quantity is worked from


def _prompt(obj, name, default):
    value = obj.get(name, default)
    return default if value is None else value


def _remove(obj):
    for child in list(obj.children):
        _remove(child)
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if isinstance(data, bpy.types.Mesh) and data.users == 0:
        bpy.data.meshes.remove(data)


# ---------------------------------------------------------------------------
# Coat hooks
# ---------------------------------------------------------------------------

def _hook_mesh(style):
    """The shared mesh for a hook model, built once from the closet
    library's code-drawn models."""
    name = "HB Hook - " + style
    mesh = bpy.data.meshes.get(name)
    if mesh is not None:
        return mesh
    from ..closets import accessory_models
    src = accessory_models.build(style)
    if src is None or src.data is None:
        return None
    mesh = src.data
    mesh.name = name
    bpy.data.objects.remove(src, do_unlink=True)
    return mesh


def solve_hooks(interior_obj):
    count = int(_prompt(interior_obj, HOOK_COUNT_KEY, 0))
    existing = [c for c in interior_obj.children if c.get(HOOK_TAG)]
    if count <= 0:
        for obj in existing:
            bpy.data.objects.remove(obj, do_unlink=True)
        interior_obj.pop(HOOK_SIGNATURE_KEY, None)
        return
    dim_x, dim_y, dim_z = solver_frameless.cage_dims(interior_obj)
    height = float(_prompt(interior_obj, HOOK_HEIGHT_KEY, 0.0))
    if height <= 0.0:
        height = max(dim_z - HOOK_FROM_TOP, 0.0)
    style = _prompt(interior_obj, HOOK_STYLE_KEY, HOOK_STYLES[0][0])
    signature = repr((count, round(dim_x, 5), round(dim_y, 5),
                      round(height, 5), style))
    if interior_obj.get(HOOK_SIGNATURE_KEY) == signature and len(existing) == count:
        return
    for obj in existing:
        bpy.data.objects.remove(obj, do_unlink=True)
    mesh = _hook_mesh(style)
    if mesh is None:
        return
    for i in range(count):
        obj = bpy.data.objects.new("Coat Hook", mesh)
        for coll in interior_obj.users_collection:
            coll.objects.link(obj)
            break
        else:
            bpy.context.scene.collection.objects.link(obj)
        obj.parent = interior_obj
        obj[HOOK_TAG] = True
        obj['hb_part_role'] = 'COAT_HOOK'
        # The models reach along -X off their mounting face; on the back
        # wall they reach forward, towards -Y.
        obj.rotation_euler = (0.0, 0.0, math.radians(90.0))
        obj.location = (dim_x * (i + 1) / (count + 1), dim_y, height)
    interior_obj[HOOK_SIGNATURE_KEY] = signature


# ---------------------------------------------------------------------------
# Shoe shelves
# ---------------------------------------------------------------------------

def solve_shoe_shelves(interior_obj):
    from .types_frameless import CabinetPart
    dim_x, dim_y, dim_z = solver_frameless.cage_dims(interior_obj)
    mt = float(_prompt(interior_obj, 'Material Thickness', inch(0.75)))
    qty = int(_prompt(interior_obj, SHOE_QTY_KEY, 0))
    if qty <= 0:
        qty = max(int(dim_z // SHOE_PITCH), 1)
    angle = math.radians(float(_prompt(interior_obj, SHOE_ANGLE_KEY, 15.0)))
    stop_h = float(_prompt(interior_obj, SHOE_STOP_KEY, inch(1.5)))
    depth = max(dim_y - inch(0.25), 0.0)
    rise = depth * math.sin(angle)
    signature = repr((qty, round(dim_x, 5), round(dim_y, 5), round(dim_z, 5),
                      round(angle, 5), round(stop_h, 5), round(mt, 5)))
    existing = [c for c in interior_obj.children if c.get(SHOE_PART_TAG)]
    if interior_obj.get(SHOE_SIGNATURE_KEY) == signature and len(existing) == qty * 2:
        return
    for obj in existing:
        _remove(obj)
    # Shelves spread over the height with room above each for its rise.
    step = dim_z / (qty + 1)
    parts = []
    for k in range(qty):
        z = step * (k + 1) - rise / 2.0
        shelf = CabinetPart()
        shelf.create("Shoe Shelf")
        obj = shelf.obj
        obj.parent = interior_obj
        obj[SHOE_PART_TAG] = True
        obj['IS_FRAMELESS_INTERIOR_PART'] = True
        obj['hb_part_role'] = 'SHOE_SHELF'
        obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        obj['Finish Top'] = False
        obj['Finish Bottom'] = False
        # Tilted up towards the back about its front edge.
        obj.rotation_euler = (angle, 0.0, 0.0)
        obj.location = (0.0, 0.0, z)
        shelf.set_input('Length', dim_x)
        shelf.set_input('Width', depth)
        shelf.set_input('Thickness', mt)
        parts.append(obj)
        # The stop stands up off the front edge, square to the shelf.
        stop = CabinetPart()
        stop.create("Shoe Stop")
        sobj = stop.obj
        sobj.parent = interior_obj
        sobj[SHOE_PART_TAG] = True
        sobj['IS_FRAMELESS_INTERIOR_PART'] = True
        sobj['hb_part_role'] = 'SHOE_STOP'
        sobj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        sobj['Finish Top'] = False
        sobj['Finish Bottom'] = False
        sobj.rotation_euler = (angle + math.radians(90.0), 0.0, 0.0)
        sobj.location = (0.0, 0.0, z)
        stop.set_input('Length', dim_x)
        stop.set_input('Width', stop_h + mt)
        stop.set_input('Thickness', inch(0.75))
        stop.set_input('Mirror Z', True)
        parts.append(sobj)
    root = solver_frameless.cabinet_root(interior_obj)
    if root is not None:
        for obj in parts:
            solver_frameless._paint_interior(root, obj)
    interior_obj[SHOE_SIGNATURE_KEY] = signature
