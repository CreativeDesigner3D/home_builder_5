"""Closet material selection.

A bundled .blend of asset materials (assets/materials/library.blend)
feeds the scene-level material dropdowns in the closets sidebar: one
selection for the carcass (panels, shelves, kicks, bridge shelves) and
one for door/drawer fronts. Changing a dropdown re-applies to every
closet in the room; new placements pick the selection up through
ops_closet._apply_finish.

Countertops are surfaced in a different material entirely, so they read
from their own blend (assets/materials/countertops.blend) and their own
dropdown. Keeping them apart is what stops the eight laminates showing
up as panel choices - both dropdowns above read the library blend with
assets_only, so anything asset-marked in there is offered as a carcass
material. A toggle puts the closet material on the tops instead, for a
run that is meant to read as one piece.

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
COUNTERTOPS_BLEND = os.path.join(os.path.dirname(__file__), 'assets',
                                 'materials', 'countertops.blend')
# Hoisted to the front of the name list, so the dynamic enums (which
# default to their first item) default to it.
DEFAULT_MATERIAL = 'White'
DEFAULT_COUNTERTOP_MATERIAL = 'Gray Mesh'
# The order the countertop laminates have always been listed in. The
# names still come out of the blend, so a material added there shows up
# without a code change - it just lands after the known ones.
COUNTERTOP_ORDER = (
    'Gray Mesh', 'Pewter Mesh', 'Organic Cotton', 'Raw Cotton',
    'Earth', 'Flax Gauze', 'White Shalestone', 'Black Shalestone',
)

# Sentinel for the fronts / edgebanding dropdowns: follow the base
# material selection instead of picking an explicit one.
MATCH = 'MATCH'

# Door panel types: Vertical Grain = the front material (doors always
# run vertical grain); the rest are glass materials that live in
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
_ctop_names_cache = None
_ctop_enum_cache = None


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


def get_countertop_material_names():
    """Countertop material names from the countertops blend, in the
    listed order with anything unlisted after it (cached). Empty list
    when the blend is missing - the dropdown then shows a single None
    entry and application falls back to the closet material."""
    global _ctop_names_cache
    if _ctop_names_cache is None:
        found = []
        try:
            with bpy.data.libraries.load(
                    COUNTERTOPS_BLEND, assets_only=True) as (src, _dst):
                found = sorted(src.materials)
        except Exception:
            found = []
        known = [n for n in COUNTERTOP_ORDER if n in found]
        rest = [n for n in found if n not in COUNTERTOP_ORDER]
        _ctop_names_cache = known + rest
    return _ctop_names_cache


def countertop_material_enum_items(self, context):
    global _ctop_enum_cache
    if _ctop_enum_cache is None:
        items = [(n, n, "") for n in get_countertop_material_names()]
        _ctop_enum_cache = items or [('NONE', "None",
                                      "No countertop materials library")]
    return _ctop_enum_cache


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
    global _ctop_names_cache, _ctop_enum_cache
    _names_cache = None
    _enum_cache = None
    _match_enum_cache = None
    _ctop_names_cache = None
    _ctop_enum_cache = None


def load_material(name, blend=None):
    """Existing-or-appended material by name; None when unavailable.
    Looks in the materials library unless another blend is named."""
    if not name or name == 'NONE':
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    try:
        with bpy.data.libraries.load(blend or MATERIALS_BLEND) as (src,
                                                                   dst):
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


# Which way the grain runs on a drawer front. Doors always run
# vertical, so the only choice to make is the drawer fronts', and a
# single drawer can be turned the other way on its own.
GRAIN_OVERRIDE_ITEMS = [
    ('DEFAULT', "Use Default", "Follow the room's Vertical Grain setting"),
    ('VERTICAL', "Vertical", "Grain runs up the front"),
    ('HORIZONTAL', "Horizontal", "Grain runs across the front"),
]


def front_grain(front_obj, is_drawer):
    """Grain direction for one front.

    Doors always run vertical - the way a tall front is built - so
    there is nothing to look up for them. A drawer front reads the
    nearest thing that has an opinion: its own setting from Drawer
    Options first, then its opening's, then the room's Vertical Grain
    setting. Plain lookup on the way to picking a material, so a
    whole run re-grains in one pass with nothing driven."""
    if not is_drawer:
        return 'VERTICAL'
    try:
        from . import types_closets
    except Exception:
        types_closets = None
    if types_closets is not None:
        own = front_obj.get(types_closets.PROP_FRONT_GRAIN, '')
        if own in ('VERTICAL', 'HORIZONTAL'):
            return own
        try:
            opening = types_closets.find_opening_cage(front_obj)
        except Exception:
            opening = None
        if opening is not None:
            shared = opening.hb_closet_opening.drawer_grain
            if shared in ('VERTICAL', 'HORIZONTAL'):
                return shared
    props = bpy.context.scene.hb_closets
    return ('VERTICAL'
            if getattr(props, 'closet_drawer_vertical_grain', False)
            else 'HORIZONTAL')


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


def resolve_countertop_material(carcass=None):
    """The material for tops and their upstands: the countertop
    selection, or the closet material when the run is meant to read as
    one piece. Falls back to the closet material if the selection
    cannot be resolved, so a missing blend leaves a painted top rather
    than a grey one."""
    props = bpy.context.scene.hb_closets
    if carcass is None:
        carcass = load_material(
            getattr(props, 'closet_material', DEFAULT_MATERIAL))
    if getattr(props, 'use_closet_material_for_countertops', False):
        return carcass
    name = getattr(props, 'closet_countertop_material',
                   DEFAULT_COUNTERTOP_MATERIAL)
    return load_material(name, COUNTERTOPS_BLEND) or carcass


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
    grain = front_grain(front_obj, is_drawer)
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


def _fence_finish(fence_obj, cache):
    """Metal finish for one shoe fence, looked up through the opening
    that owns its shelf stack and cached per opening."""
    from . import types_closets
    opening = types_closets.find_opening_cage(fence_obj)
    if opening is None:
        return None
    key = opening.name
    if key not in cache:
        cache[key] = types_closets.shoe_fence_material(
            opening.hb_closet_opening.slant_color)
    return cache[key]


def apply_to_starter(root, carcass_name=None, front_name=None):
    """Assign the selected materials to every cutpart under a starter:
    fronts (door/drawer/hamper) get the fronts material (Match Closet
    follows the closet material) oriented by the grain the front
    resolves to - vertical on doors, and on drawer fronts whatever the
    room's Vertical Grain setting says unless that drawer carries a
    direction of its own. The library textures read horizontal as
    authored, so VERTICAL is the rotated in-plane variant.
    Tops and their upstands
    get the countertop selection. Everything else gets the closet
    material. Edge slots take the edgebanding selections (Match
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
    role_door = types_closets.PART_ROLE_DOOR
    role_drawer = types_closets.PART_ROLE_DRAWER_FRONT
    role_fence = types_closets.PART_ROLE_SHOE_FENCE
    # A top and its upstands are one surface, banded all the way round
    # in the same material.
    ctop_roles = (types_closets.PART_ROLE_COUNTERTOP,
                  types_closets.PART_ROLE_BACKSPLASH)
    ctop = resolve_countertop_material(carcass)
    ctop_edge = rotated_variant(ctop)
    fence_cache = {}
    for child in root.children_recursive:
        if child.type != 'MESH':
            continue
        role = child.get('hb_part_role')
        if role in (role_door, role_drawer):
            # Grain is worked out per front rather than once for the
            # run, so a drawer turned the other way gets the rotated
            # material while its neighbours do not.
            mat = (front_v
                   if front_grain(child, role == role_drawer) == 'VERTICAL'
                   else front)
            edge = front_edge
        elif role in ctop_roles:
            mat, edge = ctop, ctop_edge
        elif role == role_fence:
            # A purchased metal rail. It takes the finish chosen for its
            # shelf stack rather than the closet material, and it is one
            # material all the way round, so the edge slots match the
            # surfaces. An unresolvable finish leaves the part alone
            # instead of painting it like a panel.
            mat = _fence_finish(child, fence_cache)
            if mat is None:
                continue
            edge = mat
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
