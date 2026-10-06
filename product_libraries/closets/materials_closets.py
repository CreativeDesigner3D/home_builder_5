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

# Bought parts - the hang rail covers - wear this instead of the run's
# finish. It is a negative material: it says the part never comes off a
# sheet, so nothing that paints the closet touches it and whatever
# processes hardware downstream counts it there instead. Kept in the
# file under a known name and marked with an idprop as well, so a
# rename does not lose track of it.
NEGATIVE_MATERIAL = 'Negative'
NEGATIVE_MATERIAL_KEY = 'hb_negative_material'
NEGATIVE_MATERIAL_COLOR = (0.05, 0.05, 0.06, 1.0)

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


def load_negative_material():
    """The material a bought part wears. Taken from the bundled blend
    when it holds one by that name, and made here when it does not, so
    a run always has one to hand its covers."""
    mat = load_material(NEGATIVE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(NEGATIVE_MATERIAL)
        mat.use_nodes = True
        mat.diffuse_color = NEGATIVE_MATERIAL_COLOR
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (
                NEGATIVE_MATERIAL_COLOR)
    mat[NEGATIVE_MATERIAL_KEY] = True
    return mat


# A misc part's unbanded edges show the bare board core, so what is
# drawn matches what is banded.
CORE_MATERIAL = 'Board Core'
CORE_MATERIAL_COLOR = (0.62, 0.50, 0.34, 1.0)
# Edges a misc part can be banded on, ticked on the part as
# hb_band_<edge> flags (unbanded until chosen).
MISC_BAND_EDGES = ('W1', 'W2', 'L1', 'L2')


def load_core_material():
    """The bare-board material for unbanded edges: the bundled blend's
    when it holds one by that name, otherwise made here."""
    mat = load_material(CORE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(CORE_MATERIAL)
        mat.use_nodes = True
        mat.diffuse_color = CORE_MATERIAL_COLOR
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = CORE_MATERIAL_COLOR
            bsdf.inputs['Roughness'].default_value = 0.9
    return mat


# Which edges each kind of part is banded on - the same table the pricing
# engine charges banding by (spaces pricing.closets CARCASS_EB_EDGES,
# the prior library's per-class ebl1/ebl2/ebw1/ebw2), so the model shows
# the banding the shop puts on and the cut list, labels and MV export
# (which read the edge slots) say the same. L2 is the front edge. A part
# not listed - fronts, tops, purchased rails - is banded all round.
BAND_EDGES = {
    'CLOSET_PANEL': ('L2', 'W1', 'W2'),
    'CLOSET_BOTTOM_SHELF': ('L2',),
    'CLOSET_TOP_SHELF': ('L2',),
    'CLOSET_FIXED_SHELF': ('L2',),
    'CLOSET_ADJ_SHELF': ('L2',),
    'CLOSET_CLEAT': ('L2',),
    'CLOSET_CUBBY_DIVISION': ('L2',),
    'CLOSET_CUBBY_SHELF': ('L2',),
    'CLOSET_BRIDGE_SHELF': ('L2',),
    'CLOSET_COUNTERTOP': ('L1', 'L2', 'W1', 'W2'),
    'CLOSET_BACKSPLASH': ('L1', 'L2', 'W1', 'W2'),
    'CLOSET_APPLIED_BACK': ('L1', 'L2', 'W1', 'W2'),
    'CLOSET_TOE_KICK': (),
    'CLOSET_CENTER_BACK': (),
    'CLOSET_HOOK_CLEAT': ('L1', 'L2', 'W1', 'W2'),
    'CLOSET_FILLER': ('L1', 'W1', 'W2'),
    'CLOSET_DRAWER_STRETCHER': ('L2',),
    'CLOSET_CAPTURED_BACK': (),
    'CLOSET_DIVISION': ('L2',),
    'CLOSET_SLANTED_SHELF': ('L2',),
    'CLOSET_TOP_ACCENT_SHELF': ('L1', 'L2'),
    'CLOSET_CONTINUOUS_TOP': ('L1', 'L2'),
    'CLOSET_IRONING_BOARD_MOUNT': ('L1', 'L2', 'W1', 'W2'),
    'CLOSET_L_LOCK_SHELF': ('L2',),
    'CLOSET_L_ADJ_SHELF': ('L2',),
}
# Parts with a generic role band as the part they are (pricing
# _ACCESSORY_PART_ROLES / _LOOSE_PART_ROLES).
_ACCESSORY_BAND_ROLES = {
    'Hook Cleat': 'CLOSET_HOOK_CLEAT',
    'Ironing Board Mount': 'CLOSET_IRONING_BOARD_MOUNT',
    'Accessory Shelf': 'CLOSET_FIXED_SHELF',
}
_LOOSE_BAND_ROLES = {
    'BACK': 'CLOSET_CAPTURED_BACK',
    'CLEAT': 'CLOSET_CLEAT',
    'SHELF': 'CLOSET_ADJ_SHELF',
    'COUNTERTOP': 'CLOSET_COUNTERTOP',
}


def banded_edges(obj):
    """The edges (of W1 W2 L1 L2) a part is banded on, or None for all
    four. A misc part bands the edges ticked on it; any other part what
    its kind always does (BAND_EDGES)."""
    if is_bandable_misc_part(obj):
        return tuple(e for e in MISC_BAND_EDGES if obj.get('hb_band_' + e))
    role = obj.get('hb_part_role')
    if obj.get('hb_l_index') is not None:
        if role == 'CLOSET_ADJ_SHELF':
            role = 'CLOSET_L_ADJ_SHELF'
        elif role in ('CLOSET_FIXED_SHELF', 'CLOSET_TOP_SHELF',
                      'CLOSET_BOTTOM_SHELF'):
            role = 'CLOSET_L_LOCK_SHELF'
    elif role == 'CLOSET_ACCESSORY_PART':
        role = _ACCESSORY_BAND_ROLES.get(obj.get('hb_acc_part'), role)
    elif role == 'CLOSET_MISC_PART':
        role = _LOOSE_BAND_ROLES.get(obj.get('hb_loose_kind'), role)
    edges = BAND_EDGES.get(role)
    if edges is None:
        return None
    extra = _context_band_edges(obj, role)
    return edges + tuple(e for e in extra if e not in edges)


def _context_band_edges(obj, role):
    """Edges the prior library banded beyond a part's usual ones because
    of where it stands (types_closet.py), mapped to HB5's frame - checked
    live on both 2026-10-06 (4.3: shelf / panel L1 = back, cleat L1 =
    top; HB5: L1 = back, cleat L2 = top):

    - an island's partitions and its top and bottom shelves show their
      back as well as their front: + the back edge (L1);
    - a cleat in a bay with its bottom removed has nothing under it, so
      its bottom edge shows too: + L1 (4.3 'ebl2 = remove_bottom')."""
    if role in ('CLOSET_PANEL', 'CLOSET_TOP_SHELF', 'CLOSET_BOTTOM_SHELF'):
        cur = obj.parent
        while cur is not None:
            if cur.get('IS_CLOSET_STARTER_CAGE'):
                if 'Island' in str(cur.get('CLASS_NAME', '')):
                    return ('L1',)
                break
            cur = cur.parent
        return ()
    if role == 'CLOSET_CLEAT' and obj.get('hb_part_role') == 'CLOSET_CLEAT':
        bay = obj.parent
        bp = getattr(bay, 'hb_closet_bay', None) if bay is not None else None
        if bp is not None and bool(getattr(bp, 'remove_bottom', False)):
            return ('L1',)
    return ()


def refresh_banding(obj):
    """Re-band a part in the banding it already wears, for when which
    edges it bands on changes with the layout (a cleat whose bay loses
    its bottom) rather than with a finish. No-op on an unfinished part."""
    from ... import hb_types
    try:
        part = hb_types.GeoNodeCutpart(obj)
        core = bpy.data.materials.get(CORE_MATERIAL)
        edge = None
        for e in MISC_BAND_EDGES:
            mat = part.get_input('Edge ' + e)
            if mat is not None and mat is not core:
                edge = mat
                break
        if edge is not None:
            _set_edges(part, obj, edge)
    except Exception:
        pass


def _set_edges(part, obj, edge):
    """Band the edges `obj` is banded on in `edge`; the rest show the
    bare board core."""
    banded = banded_edges(obj)
    core = load_core_material() if banded is not None         and len(banded) < len(MISC_BAND_EDGES) else None
    for e in MISC_BAND_EDGES:
        part.set_input('Edge ' + e,
                       edge if (banded is None or e in banded) else core)


def is_bandable_misc_part(obj):
    """A true misc part - not the loose back / cleat / shelf, which band
    the way the part they stand in for always does."""
    from . import types_closets
    return (obj.get('hb_part_role') == types_closets.PART_ROLE_MISC
            and obj.get('hb_loose_kind', 'MISC') == 'MISC')


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
    # The colour the variant is cut from: a turned texture is a drawing
    # concern, so cut lists, nests and pricing read the sheet by this
    # rather than by the variant's own name ('Dalia GRAIN V').
    variant['hb_base_material'] = mat.get('hb_base_material', mat.name)
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


def door_panel_type(front_obj):
    """The panel a door shows: its own panel when one was set on it,
    else the room's panel type."""
    from . import types_closets
    own = front_obj.get(types_closets.PROP_FRONT_PANEL, '')
    if own in {key for key, _label, _desc in PANEL_TYPES}:
        return own
    return getattr(bpy.context.scene.hb_closets, 'closet_panel_type',
                   'Vertical Grain')


def apply_front_member_materials(front_obj, is_drawer, front_mat=None):
    """Grain-correct materials on a styled front's Door Style modifier:
    stiles (vertical members) carry vertical grain, rails horizontal,
    and the panel follows the front's grain setting. The textures read
    along the part's length, so which material reads vertical depends
    on the way the front is cut: a length-up front (see fronts_closets)
    reads the plain material up itself and the rotated variant across,
    a length-across front the reverse. No-op for slab fronts (no
    modifier)."""
    mod = next((m for m in front_obj.modifiers
                if m.type == 'NODES' and 'Door Style' in m.name), None)
    if mod is None or mod.node_group is None:
        return
    props = bpy.context.scene.hb_closets
    if front_mat is None:
        front_mat = resolve_front_material()
    if front_mat is None:
        return
    rotated = vertical_variant(front_mat)
    if front_obj.get('hb_front_length_up'):
        vert_mat, horiz_mat = front_mat, rotated
    else:
        vert_mat, horiz_mat = rotated, front_mat
    grain = front_grain(front_obj, is_drawer)
    panel = horiz_mat if grain == 'HORIZONTAL' else vert_mat
    # Door panel type: glass selections replace the wood panel (drawer
    # fronts always keep the wood panel). Clear Glass reuses the shared
    # generated door-panel glass (Glass BSDF + Transparent mix - the
    # library's plain glass material doesn't read as glass in render);
    # Mirror / Frosted come from the materials library. The tag lets
    # the 2D layer hatch glass panels later.
    is_glass = False
    if not is_drawer:
        panel_type = door_panel_type(front_obj)
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
    _set_modifier_material(mod, 'Stile Material', vert_mat)
    _set_modifier_material(mod, 'Rail Material', horiz_mat)
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
    role_cover = types_closets.PART_ROLE_HANG_RAIL_COVER
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
        if role == types_closets.PART_ROLE_ACCESSORY_BLOCK:
            # A stand-in for something missing. It is meant to look
            # nothing like the room, so it keeps its red.
            continue
        if role == types_closets.PART_ROLE_ACCESSORY_MODEL:
            # A bought accessory arrives already finished, in whatever
            # it was ordered in. Painting it the closet material would
            # be wrong twice over - it is not a sheet good, and its
            # finish is a line on the order.
            continue
        if role in (role_door, role_drawer):
            # Grain is worked out per front rather than once for the
            # run, so a drawer turned the other way gets the rotated
            # material while its neighbours do not.
            #
            # The library textures read along the part's length. A
            # front cut length-up already has its length running up
            # it, so vertical grain is the plain material there and
            # the rotated one is what turns it sideways.
            want = front_grain(child, role == role_drawer)
            if child.get('hb_front_length_up'):
                mat = front if want == 'VERTICAL' else front_v
            else:
                mat = front_v if want == 'VERTICAL' else front
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
        elif role == role_cover:
            # A bought clip cover. Its material is what says so, and it
            # is the same all the way round - there is no banding on a
            # part that never sees a sheet.
            mat = load_negative_material()
            edge = mat
        else:
            mat, edge = carcass, carcass_edge
        if mat is None:
            continue
        part = hb_types.GeoNodeCutpart(child)
        try:
            part.set_input('Top Surface', mat)
            part.set_input('Bottom Surface', mat)
            # Unbanded edges show the bare board core.
            _set_edges(part, child, edge)
        except Exception:
            continue
        if role in (role_door, role_drawer):
            apply_front_member_materials(child, role == role_drawer,
                                         front_mat=front)
    return True


def apply_to_part(obj, carcass_name=None):
    """Assign the closet material and its edgebanding to one loose part
    standing outside a starter, so a part dropped on its own reads the
    same as the run beside it. Returns True when it took.
    """
    from ... import hb_types
    from . import types_closets
    props = bpy.context.scene.hb_closets
    if carcass_name is None:
        carcass_name = getattr(props, 'closet_material', DEFAULT_MATERIAL)
    carcass = load_material(carcass_name)
    if carcass is None:
        return False
    if types_closets.is_slab_countertop(obj):
        # A slab is the countertop laminate all the way round, and so
        # are its splashes - one board, banded in itself.
        ctop = resolve_countertop_material(carcass)
        edge = rotated_variant(ctop)
        for part_obj in [obj] + [c for c in obj.children
                                 if c.get('hb_part_role')
                                 == types_closets.PART_ROLE_BACKSPLASH]:
            try:
                part = hb_types.GeoNodeCutpart(part_obj)
                part.set_input('Top Surface', ctop)
                part.set_input('Bottom Surface', ctop)
                for e in MISC_BAND_EDGES:
                    part.set_input('Edge ' + e, edge)
            except Exception:
                continue
        return True
    edge = rotated_variant(
        _resolve_edge_base('closet_edge_material', carcass))
    try:
        part = hb_types.GeoNodeCutpart(obj)
        part.set_input('Top Surface', carcass)
        part.set_input('Bottom Surface', carcass)
        # Unbanded edges show the bare board core.
        _set_edges(part, obj, edge)
    except Exception:
        return False
    return True


def update_drawer_grain(self=None, context=None):
    """Room Vertical Grain update: a drawer front's grain decides which
    way it is CUT (length up for vertical), not only how it is painted,
    so every starter is laid out again before it is re-finished."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in list(scene.objects):
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
    update_room(self, context)


def update_room(self=None, context=None):
    """Dropdown update callback: re-apply to every starter in the
    scene, and to any loose part standing on its own outside one."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            apply_to_starter(obj)
        elif obj.get('hb_part_role') in (
                types_closets.PART_ROLE_MISC,
                types_closets.PART_ROLE_CONTINUOUS_TOP):
            apply_to_part(obj)
