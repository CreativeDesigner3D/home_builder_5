"""Grain matching across frameless fronts.

The library materials map their texture from each part's own object
space, so every front starts the grain at its own corner and a run of
doors reads as separate boards. A matched front instead wears a copy of
its material that maps from a reference shared by the whole run -- a
hidden empty oriented like the fronts, parented with the cabinets to
their wall -- so the grain carries from front to front as if the run
were cut from one sheet.

Which fronts match, and which way the grain runs, is the door style's
pick (Frameless_Door_Style.grain_match). Vertical keeps the grain as the
fronts are cut, up the front; horizontal turns it across.
"""

import bpy
import math
from mathutils import Matrix

GRAIN_MATCH_ITEMS = [
    ('NONE', "No Grain Match", "Each front shows its own grain"),
    ('VERTICAL', "Vertical Grain Match",
     "Grain runs up the fronts and carries across the run"),
    ('HORIZONTAL', "Horizontal Grain Match",
     "Grain runs across the fronts and carries from front to front"),
]
REFERENCE_TAG = 'IS_GRAIN_MATCH_REFERENCE'
REFERENCE_KEY = 'hb_grain_rotation'
BASE_KEY = 'hb_grain_base'
# Face materials a front carries; its edges keep their own mapping.
FACE_SOCKETS = ('Top Surface', 'Bottom Surface', 'Stile Material',
                'Rail Material', 'Panel Material')


def front_mode(front_obj):
    from . import props_hb_frameless
    style = props_hb_frameless.front_door_style(front_obj)
    return getattr(style, 'grain_match', 'NONE') if style else 'NONE'


def _world(obj):
    """World matrix from the authored transforms, so an object made
    earlier in the same operator (whose matrix_world is still stale) is
    placed right."""
    m = obj.matrix_basis.copy()
    while obj.parent is not None:
        m = obj.matrix_parent_inverse @ m
        obj = obj.parent
        m = obj.matrix_basis @ m
    return m


def _owner(front_obj):
    """The cabinet (or appliance) a front belongs to."""
    obj = front_obj
    while obj is not None:
        if obj.get('IS_FRAMELESS_CABINET_CAGE') or obj.get('IS_APPLIANCE'):
            return obj
        obj = obj.parent
    return front_obj


def reference_for(front_obj):
    """The run's grain reference: one per wall (or loose run) and front
    orientation, made the first time it is asked for."""
    owner = _owner(front_obj)
    parent = owner.parent
    rotation = _world(front_obj).to_quaternion()
    key = ','.join('%.3f' % v for v in rotation)
    pool = parent.children if parent is not None else [
        o for o in bpy.data.objects if o.parent is None]
    for obj in pool:
        if obj.get(REFERENCE_TAG) and obj.get(REFERENCE_KEY) == key:
            return obj
    ref = bpy.data.objects.new('Grain Match Reference', None)
    for coll in owner.users_collection:
        coll.objects.link(ref)
        break
    else:
        bpy.context.scene.collection.objects.link(ref)
    ref[REFERENCE_TAG] = True
    ref[REFERENCE_KEY] = key
    ref.empty_display_size = 0.05
    ref.hide_viewport = True
    ref.hide_render = True
    world = (Matrix.Translation(_world(owner).to_translation())
             @ rotation.to_matrix().to_4x4())
    if parent is not None:
        ref.parent = parent
        ref.matrix_parent_inverse.identity()
        ref.matrix_basis = _world(parent).inverted() @ world
    else:
        ref.matrix_basis = world
    return ref


def _base(mat):
    name = mat.get(BASE_KEY)
    return (bpy.data.materials.get(name) if name else None) or mat


def _mapped_by_object(mat):
    if not mat.use_nodes:
        return None
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_COORD' and node.outputs['Object'].links:
            return node
    return None


def matched(mat, ref, mode):
    """The material a front wears for ``mode``: the plain one for NONE,
    else a copy mapped from ``ref``. Solid colours have no grain and come
    back unchanged."""
    base = _base(mat)
    if mode == 'NONE' or ref is None or _mapped_by_object(base) is None:
        return base
    name = "%s | Match %s %s" % (base.name, ref.name, mode.title())
    variant = bpy.data.materials.get(name)
    if variant is None:
        variant = base.copy()
        variant.name = name
    variant[BASE_KEY] = base.name
    _mapped_by_object(variant).object = ref
    turn = math.radians(90.0) if mode == 'HORIZONTAL' else 0.0
    base_map = next((n for n in base.node_tree.nodes if n.type == 'MAPPING'), None)
    var_map = next((n for n in variant.node_tree.nodes if n.type == 'MAPPING'), None)
    if base_map is not None and var_map is not None:
        var_map.inputs['Rotation'].default_value[2] = (
            base_map.inputs['Rotation'].default_value[2] + turn)
    return variant


def apply_to_front(front_obj):
    """Put a front's face materials on the grain its door style asks
    for (or back to its own)."""
    from ... import hb_utils
    mode = front_mode(front_obj)
    ref = reference_for(front_obj) if mode != 'NONE' else None
    for mod in front_obj.modifiers:
        if mod.type != 'NODES' or mod.node_group is None:
            continue
        items = mod.node_group.interface.items_tree
        for socket in FACE_SOCKETS:
            if socket not in items:
                continue
            identifier = items[socket].identifier
            mat = hb_utils.try_get_gn_input(mod, identifier, None)
            if not isinstance(mat, bpy.types.Material):
                continue
            want = matched(mat, ref, mode)
            if want is not mat:
                hb_utils.set_gn_input(mod, identifier, want)
