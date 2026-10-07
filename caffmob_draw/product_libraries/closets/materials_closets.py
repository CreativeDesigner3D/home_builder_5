"""Closet material selection.

A bundled .blend of asset materials (assets/materials/library.blend)
feeds the scene-level material dropdowns in the closets sidebar: one
selection for the carcass (panels, shelves, kicks, countertops, bridge
shelves) and one for door/drawer fronts. Changing a dropdown re-applies
to every closet in the room; new placements pick the selection up
through ops_closet._apply_finish.

Materials are appended on first use and reused by name afterwards, so
switching back and forth never duplicates datablocks. Enum item tuples
are cached at module level - Blender's dynamic-enum callbacks require
the returned strings to stay referenced (the classic enum-items
lifetime gotcha).
"""
import math
import os
import bpy

from ... import hb_utils


MATERIALS_BLEND = os.path.join(os.path.dirname(__file__), 'assets',
                               'materials', 'library.blend')
# Hoisted to the front of the name list, so the dynamic enums (which
# default to their first item) default to it.
DEFAULT_MATERIAL = 'White'

# Sentinel for the fronts / edgebanding dropdowns: follow the base
# material selection instead of picking an explicit one.
MATCH = 'MATCH'

# Door panel types: Vertical Grain = the front material (oriented by
# the door grain setting); the rest are glass materials that live in
# the library blend (not asset-marked - they only make sense as door
# panels, never as a carcass pick).
PANEL_TYPES = [
    ('Vertical Grain', "Vertical Grain", "Wood panel"),
    ('Clear Glass', "Clear Glass", ""),
    ('Mirror Glass', "Mirror Glass", ""),
    ('Frosted Matte Glass', "Frosted Matte Glass", ""),
]

_names_cache = None
_enum_cache = None
_match_enum_cache = None


def get_material_names():
    """Material names available in the bundled library blend (cached).
    Empty list when the blend is missing/unreadable - the dropdown then
    shows a single None entry and application no-ops."""
    global _names_cache
    if _names_cache is None:
        names = []
        try:
            # assets_only: the library carries helper datablocks (2D
            # display variants, glass for front panel types) that are
            # not user-facing choices - only asset-marked materials are.
            with bpy.data.libraries.load(
                    MATERIALS_BLEND, assets_only=True) as (src, _dst):
                names = sorted(src.materials)
        except Exception:
            names = []
        if DEFAULT_MATERIAL in names:
            names.remove(DEFAULT_MATERIAL)
            names.insert(0, DEFAULT_MATERIAL)
        _names_cache = names
    return _names_cache


def material_enum_items(self, context):
    global _enum_cache
    if _enum_cache is None:
        items = [(n, n, "") for n in get_material_names()]
        _enum_cache = items or [('NONE', "None", "No materials library")]
    return _enum_cache


def match_enum_items(self, context):
    """Items for the fronts / edgebanding dropdowns: Match Closet first
    (= the dynamic-enum default), then the explicit materials."""
    global _match_enum_cache
    if _match_enum_cache is None:
        items = [(MATCH, "Match Closet",
                  "Follow the closet material selection")]
        items += [(n, n, "") for n in get_material_names()]
        _match_enum_cache = items
    return _match_enum_cache


def refresh():
    """Drop the caches so a changed library blend re-scans."""
    global _names_cache, _enum_cache, _match_enum_cache
    _names_cache = None
    _enum_cache = None
    _match_enum_cache = None


def load_material(name):
    """Existing-or-appended material by name; None when unavailable."""
    if not name or name == 'NONE':
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    try:
        with bpy.data.libraries.load(MATERIALS_BLEND) as (src, dst):
            if name in src.materials:
                dst.materials = [name]
    except Exception:
        return None
    return bpy.data.materials.get(name)


def _mapping_variant(mat, suffix, rot_x=0.0, rot_z=0.0):
    """Find-or-create a copy of mat with its texture mapping rotated.
    Materials without a Mapping node (solid colors) have no direction
    and are returned unchanged. The rotation is (re)written on every
    call so stale variants self-repair."""
    if mat is None or not mat.use_nodes:
        return mat
    if not any(n.type == 'MAPPING' for n in mat.node_tree.nodes):
        return mat
    name = mat.name + suffix
    variant = bpy.data.materials.get(name)
    if variant is None:
        variant = mat.copy()
        variant.name = name
    mapping = next((n for n in variant.node_tree.nodes
                    if n.type == 'MAPPING'), None)
    if mapping is not None:
        rotation = mapping.inputs['Rotation'].default_value
        rotation[0] = rot_x
        rotation[2] = rot_z
    return variant


def rotated_variant(mat):
    """Edge variant: grain turned 90 degrees about X so it reads along
    the banding on a cutpart's edge faces."""
    return _mapping_variant(mat, " ROTATED", rot_x=math.radians(90.0))


def vertical_variant(mat):
    """Vertical-grain face variant: the library textures read
    HORIZONTAL as authored, so vertical grain is the 90-degree in-plane
    (about Z) rotation."""
    return _mapping_variant(mat, " GRAIN V", rot_z=math.radians(90.0))


def _set_modifier_material(mod, socket_name, mat):
    ng = mod.node_group
    for item in ng.interface.items_tree:
        if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                and item.name == socket_name):
            hb_utils.set_gn_input(mod, item.identifier, mat)
            return


def resolve_front_material(carcass=None):
    """The fronts material: an explicit selection, or the closet
    material when set to Match Closet."""
    props = bpy.context.scene.hb_closets
    if carcass is None:
        carcass = load_material(
            getattr(props, 'closet_material', DEFAULT_MATERIAL))
    selection = getattr(props, 'closet_front_material', MATCH)
    if selection in ('', MATCH):
        return carcass
    return load_material(selection) or carcass


def apply_front_member_materials(front_obj, is_drawer, front_mat=None):
    """Grain-correct materials on a styled front's Door Style modifier:
    stiles (vertical members) carry vertical grain (the in-plane
    variant - the textures read horizontal as authored), rails the
    material as-is, and the panel follows the front's grain setting.
    The fronts route the builder through a rotation wrapper (see
    fronts_closets), so the sockets keep their plain meaning. No-op for
    slab fronts (no modifier)."""
    mod = next((m for m in front_obj.modifiers
                if m.type == 'NODES' and 'Door Style' in m.name), None)
    if mod is None or mod.node_group is None:
        return
    props = bpy.context.scene.hb_closets
    if front_mat is None:
        front_mat = resolve_front_material()
    if front_mat is None:
        return
    vertical = vertical_variant(front_mat)
    grain = getattr(props,
                    'closet_drawer_grain' if is_drawer
                    else 'closet_door_grain',
                    'HORIZONTAL' if is_drawer else 'VERTICAL')
    panel = front_mat if grain == 'HORIZONTAL' else vertical
    # Door panel type: glass selections replace the wood panel (drawer
    # fronts always keep the wood panel). Clear Glass reuses the shared
    # generated door-panel glass (Glass BSDF + Transparent mix - the
    # library's plain glass material doesn't read as glass in render);
    # Mirror / Frosted come from the materials library. The tag lets
    # the 2D layer hatch glass panels later.
    is_glass = False
    if not is_drawer:
        panel_type = getattr(props, 'closet_panel_type',
                             'Vertical Grain')
        if panel_type != 'Vertical Grain':
            glass = None
            if panel_type == 'Clear Glass':
                try:
                    from ..face_frame.props_hb_face_frame import (
                        Face_Frame_Cabinet_Style)
                    glass = (Face_Frame_Cabinet_Style
                             ._get_glass_panel_material())
                except Exception:
                    glass = None
            if glass is None:
                glass = load_material(panel_type)
            if glass is not None:
                panel = glass
                is_glass = True
        front_obj['hb_panel_type'] = panel_type
    front_obj['IS_PREP_FOR_GLASS'] = is_glass
    _set_modifier_material(mod, 'Stile Material', vertical)
    _set_modifier_material(mod, 'Rail Material', front_mat)
    _set_modifier_material(mod, 'Panel Material', panel)
    front_obj.update_tag()


def _resolve_edge_base(prop_name, fallback):
    """Edgebanding base material for one of the edge dropdowns: an
    explicit selection, or `fallback` (the matching surface material)
    when set to Match."""
    selection = getattr(bpy.context.scene.hb_closets, prop_name, MATCH)
    if selection in ('', MATCH):
        return fallback
    return load_material(selection) or fallback


def apply_to_starter(root, carcass_name=None, front_name=None):
    """Assign the selected materials to every cutpart under a starter:
    fronts (door/drawer/hamper) get the fronts material (Match Closet
    follows the closet material) oriented by the door/drawer grain
    setting - the library textures read horizontal as authored, so
    VERTICAL is the rotated in-plane variant. Everything else gets the
    closet material. Edge slots take the edgebanding selections (Match
    = the surface material) as their X-rotated variant so grain reads
    along the banding; styled fronts additionally get per-member
    modifier materials. Non-cutpart meshes (cages, rods, pulls, drawer
    boxes without slots) are skipped by the per-part exception guard.
    Returns True when anything could be applied - callers fall back to
    the cabinet-style finish on False.
    """
    from ... import hb_types
    from . import types_closets
    props = bpy.context.scene.hb_closets
    if carcass_name is None:
        carcass_name = getattr(props, 'closet_material',
                               DEFAULT_MATERIAL)
    carcass = load_material(carcass_name)
    if front_name is None:
        front = resolve_front_material(carcass)
    else:
        front = (carcass if front_name in ('', MATCH)
                 else load_material(front_name) or carcass)
    if carcass is None and front is None:
        return False
    carcass_edge = rotated_variant(
        _resolve_edge_base('closet_edge_material', carcass))
    front_edge = rotated_variant(
        _resolve_edge_base('closet_front_edge_material', front))
    front_v = vertical_variant(front)
    door_grain = getattr(props, 'closet_door_grain', 'VERTICAL')
    drawer_grain = getattr(props, 'closet_drawer_grain', 'HORIZONTAL')
    door_face = front if door_grain == 'HORIZONTAL' else front_v
    drawer_face = front if drawer_grain == 'HORIZONTAL' else front_v
    role_door = types_closets.PART_ROLE_DOOR
    role_drawer = types_closets.PART_ROLE_DRAWER_FRONT
    for child in root.children_recursive:
        if child.type != 'MESH':
            continue
        role = child.get('hb_part_role')
        if role == role_door:
            mat, edge = door_face, front_edge
        elif role == role_drawer:
            mat, edge = drawer_face, front_edge
        else:
            mat, edge = carcass, carcass_edge
        if mat is None:
            continue
        part = hb_types.GeoNodeCutpart(child)
        try:
            part.set_input('Top Surface', mat)
            part.set_input('Bottom Surface', mat)
            part.set_input('Edge W1', edge)
            part.set_input('Edge W2', edge)
            part.set_input('Edge L1', edge)
            part.set_input('Edge L2', edge)
        except Exception:
            continue
        if role in (role_door, role_drawer):
            apply_front_member_materials(child, role == role_drawer,
                                         front_mat=front)
    return True


def update_room(self=None, context=None):
    """Dropdown update callback: re-apply to every starter in the scene."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            apply_to_starter(obj)
