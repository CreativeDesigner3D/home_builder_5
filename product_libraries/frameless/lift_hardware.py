"""Lift mechanisms for frameless flip-up doors.

A flip-up opening picks one of four lift types. Each puts a mechanism
housing on the inside of both cabinet sides at the top, with an arm out
to the front, and opens the front its own way:

- Stay lift: the front tilts up on its top edge.
- Bi-fold lift: the front is two panels that fold in half as they lift.
- Up and over: the front rises and tips back over the cabinet top.
- Vertical lift: the front slides straight up.

The hardware carries HARDWARE_TAG and the mechanism's name so a hardware
list can count it.
"""

import bpy
import math
from mathutils import Euler, Matrix, Vector
from ...units import inch
from . import solver_frameless

LIFT_KEY = 'Lift Mechanism'
STAY, BI_FOLD, UP_AND_OVER, VERTICAL = 0, 1, 2, 3
LIFT_ITEMS = [
    ('0', "Stay Lift", "Front tilts up on its top edge"),
    ('1', "Bi-Fold Lift", "Front is two panels that fold in half as they lift"),
    ('2', "Up and Over", "Front rises and tips back over the cabinet top"),
    ('3', "Vertical Lift", "Front slides straight up"),
]
LIFT_NAMES = [label for _key, label, _desc in LIFT_ITEMS]

HARDWARE_TAG = 'IS_LIFT_HARDWARE'
HARDWARE_NAME_KEY = 'hb_hardware_name'
UPPER_TAG = 'IS_LIFT_UPPER_FRONT'
SIDE_KEY = 'hb_lift_side'

# Housing thickness off the side, height and depth, per lift type.
HOUSING_SIZES = {
    STAY: (inch(1.25), inch(4.5), inch(7.0)),
    BI_FOLD: (inch(1.25), inch(7.0), inch(9.0)),
    UP_AND_OVER: (inch(1.25), inch(6.0), inch(10.0)),
    VERTICAL: (inch(1.25), inch(7.0), inch(10.0)),
}
HOUSING_SETBACK = inch(0.75)     # behind the carcass front
HOUSING_TOP_GAP = inch(0.25)     # below the top of the opening
ARM_WIDTH = inch(0.5)
ARM_THICKNESS = inch(0.75)
FOLD_GAP = inch(0.125)           # between the two panels of a bi-fold
FULL_TILT = math.radians(90.0)
UP_AND_OVER_TILT = math.radians(20.0)

_FRONT_ROTATION = Euler((math.radians(90.0), math.radians(-90.0), 0.0))


def lift_type(insert_obj):
    value = int(solver_frameless.prompt(insert_obj, LIFT_KEY, STAY))
    return value if value in HOUSING_SIZES else STAY


def lift_name(insert_obj):
    return LIFT_NAMES[lift_type(insert_obj)]


# ---------------------------------------------------------------------------
# Meshes
# ---------------------------------------------------------------------------

def _box_mesh(name, x0, x1, y0, y1, z0, z1):
    mesh = bpy.data.meshes.get(name)
    if mesh is not None:
        return mesh
    verts = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(_material())
    return mesh


def _material():
    mat = bpy.data.materials.get("HB Lift Hardware")
    if mat is None:
        mat = bpy.data.materials.new("HB Lift Hardware")
        mat.diffuse_color = (0.35, 0.35, 0.37, 1.0)
        mat.metallic = 0.6
        mat.roughness = 0.4
    return mat


def _housing_mesh():
    return _box_mesh("HB Lift Housing", 0.0, 1.0, 0.0, 1.0, 0.0, 1.0)


def _arm_mesh():
    # Runs along +Y from its origin so a scale on Y is its length.
    return _box_mesh("HB Lift Arm", -0.5, 0.5, 0.0, 1.0, -0.5, 0.5)


def _hardware(insert_obj, role, side, mesh):
    for child in insert_obj.children:
        if (child.get(HARDWARE_TAG) and child.get(solver_frameless.PART_ROLE_KEY) == role
                and child.get(SIDE_KEY) == side):
            return child
    obj = bpy.data.objects.new("Lift Housing" if role == 'LIFT_HOUSING' else "Lift Arm", mesh)
    for coll in insert_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = insert_obj
    obj[HARDWARE_TAG] = True
    obj[solver_frameless.PART_ROLE_KEY] = role
    obj[SIDE_KEY] = side
    return obj


def remove_hardware(insert_obj):
    for child in list(insert_obj.children):
        if child.get(HARDWARE_TAG):
            bpy.data.objects.remove(child, do_unlink=True)


# ---------------------------------------------------------------------------
# The bi-fold's upper panel
# ---------------------------------------------------------------------------

def _upper_front(insert_obj, lower):
    for child in insert_obj.children:
        if child.get(UPPER_TAG):
            return child
    from . import types_frameless
    from ... import hb_project
    front = types_frameless.CabinetFront()
    front.create('Flip Up Door Upper')
    obj = front.obj
    obj.parent = insert_obj
    obj.rotation_euler = _FRONT_ROTATION
    front.set_input("Mirror Y", True)
    obj['IS_DOOR_FRONT'] = True
    obj[UPPER_TAG] = True
    obj[solver_frameless.PART_ROLE_KEY] = 'LIFT_UPPER_FRONT'
    styles = hb_project.get_main_scene().hb_frameless.door_styles
    index = int(lower.get('DOOR_STYLE_INDEX', 0))
    if 0 <= index < len(styles):
        obj['DOOR_STYLE_INDEX'] = index
        try:
            styles[index].assign_style_to_front(obj)
        except Exception:
            pass
    return obj


def _remove_upper(insert_obj):
    for child in list(insert_obj.children):
        if child.get(UPPER_TAG):
            for sub in list(child.children_recursive):
                bpy.data.objects.remove(sub, do_unlink=True)
            bpy.data.objects.remove(child, do_unlink=True)


# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------

def _move(obj, rot, pivot, shift):
    """Carry a front from its closed placement about ``pivot``."""
    loc = Vector(obj.location)
    obj.rotation_euler = (rot @ _FRONT_ROTATION.to_matrix()).to_euler('XYZ')
    obj.location = pivot + rot @ (loc - pivot) + shift


def _carry(point, rot, pivot, shift):
    return pivot + rot @ (point - pivot) + shift


def solve(insert_obj, front, length, width, thickness, hidden):
    """Split, open and fit the hardware to one flip-up front, placed closed
    by the caller. Returns the length of the front that carries the pull."""
    kind = lift_type(insert_obj)
    dim_x, dim_y, dim_z = solver_frameless.cage_dims(insert_obj)
    amount = (solver_frameless.open_amount(insert_obj)
              if solver_frameless.OPEN_KEY in insert_obj else 0.0)
    x0, y0, z0 = front.location
    z_top = z0 + length
    face_y = y0 - thickness                     # the fronts' outer face

    upper = None
    lower_len = length
    if kind == BI_FOLD:
        lower_len = max((length - FOLD_GAP) / 2.0, 0.0)
        upper = _upper_front(insert_obj, front)
        solver_frameless.set_part(front, (x0, y0, z0), length=lower_len,
                                  visible=not front.hide_viewport)
        solver_frameless.set_part(upper, (x0, y0, z0 + lower_len + FOLD_GAP),
                                  length=lower_len, width=width,
                                  thickness=thickness, visible=not hidden)
        upper.rotation_euler = _FRONT_ROTATION
    else:
        _remove_upper(insert_obj)

    # Where the arms take hold of the moving front, closed.
    if kind == BI_FOLD:
        grip_z = z_top - lower_len / 2.0
    elif kind == STAY:
        grip_z = z_top - inch(3.0)
    else:
        grip_z = z_top - inch(4.0)
    ident = Matrix.Identity(3)
    zero = Vector((0.0, 0.0, 0.0))
    if kind == STAY:
        rot = Matrix.Rotation(-amount * FULL_TILT, 3, 'X')
        pivot, shift = Vector((0.0, face_y, z_top)), zero
        _move(front, rot, pivot, shift)
        grip = (rot, pivot, shift)
    elif kind == UP_AND_OVER:
        rot = Matrix.Rotation(-amount * UP_AND_OVER_TILT, 3, 'X')
        pivot = Vector((0.0, face_y, z_top))
        shift = Vector((0.0, 0.0, amount * (length + inch(0.5))))
        _move(front, rot, pivot, shift)
        grip = (rot, pivot, shift)
    elif kind == VERTICAL:
        shift = Vector((0.0, 0.0, amount * (length + inch(0.125))))
        _move(front, ident, zero, shift)
        grip = (ident, zero, shift)
    else:
        # The upper panel tilts up on the top edge; the lower hangs from
        # it at the fold and swings the other way, folding under it.
        rot_u = Matrix.Rotation(-amount * FULL_TILT, 3, 'X')
        pivot = Vector((0.0, face_y, z_top))
        hinge = Vector((0.0, face_y, z0 + lower_len + FOLD_GAP / 2.0))
        hinge_open = _carry(hinge, rot_u, pivot, zero)
        _move(upper, rot_u, pivot, zero)
        rot_l = Matrix.Rotation(amount * FULL_TILT, 3, 'X')
        _move(front, rot_l, hinge, hinge_open - hinge)
        grip = (rot_u, pivot, zero)

    # Housings on the sides, arms from each out to the front.
    hx, hz, hy = HOUSING_SIZES[kind]
    name = LIFT_NAMES[kind]
    usable = not hidden and dim_x > hx * 2.0 and dim_z > hz + HOUSING_TOP_GAP
    for side in (0, 1):
        housing = _hardware(insert_obj, 'LIFT_HOUSING', side, _housing_mesh())
        arm = _hardware(insert_obj, 'LIFT_ARM', side, _arm_mesh())
        x_side = 0.0 if side == 0 else dim_x - hx
        z_housing = dim_z - HOUSING_TOP_GAP - hz
        housing.location = (x_side, HOUSING_SETBACK, z_housing)
        housing.scale = (hx, hy, hz)
        x_c = x_side + hx / 2.0
        start = Vector((x_c, HOUSING_SETBACK + inch(1.0), z_housing + hz - inch(1.0)))
        end = _carry(Vector((x_c, y0, grip_z)), *grip)
        run = end - start
        arm.location = start
        arm.rotation_euler = (math.atan2(run.z, run.y) if run.length > 1e-6 else 0.0, 0.0, 0.0)
        arm.scale = (ARM_WIDTH, max(math.hypot(run.y, run.z), 1e-4), ARM_THICKNESS)
        for obj in (housing, arm):
            obj[HARDWARE_NAME_KEY] = name
            obj.hide_viewport = obj.hide_render = not usable
    return lower_len
