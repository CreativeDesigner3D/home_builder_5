"""Closet door/drawer front style selection.

One scene-level dropdown styles every closet front. Styles are
parameter presets for the shared CPM_5PIECEDOOR part modifier (the same
node group the cabinet libraries use):

  Narrow Shaker/Miter        2.25" frame all around
  Wide Shaker/Miter          3" frame all around
  Contemporary Shaker/Miter  2.5" stiles, 3" rails (2" on drawers)
  Combination                2.5" stiles, 3" rails (2" on drawers)
  Slab                       flat (no modifier)

Panel: 1/4" thick, inset 1/2" from the frame face. Each style carries
a MINIMUM front size; a front smaller than the minimum stays a slab so
short drawer stacks never grow squeezed frames.

AXIS NOTE: closet front cutparts run Length ACROSS and Width UP - the
opposite of the cabinet door parts CPM_5PIECEDOOR was authored for -
so used directly the builder lays its through-members (stiles)
horizontally. The fronts therefore use a thin wrapper node group
('Closet Door Style'): rotate the geometry -90 in the face plane, run
the standard builder (its stile axis lands vertical), rotate back. The
builder sizes itself from the geometry bounds, so no re-homing is
needed, and every socket keeps its plain meaning (stile widths on
stiles, rail widths on rails).
"""
import math

import bpy

from ...units import inch


FRONT_STYLES = [
    ('SLAB', "Slab", "Flat fronts"),
    ('NARROW_SHAKER', "Narrow Shaker", ""),
    ('NARROW_MITER', "Narrow Miter", ""),
    ('CONTEMPORARY_SHAKER', "Contemporary Shaker", ""),
    ('CONTEMPORARY_MITER', "Contemporary Miter", ""),
    ('WIDE_SHAKER', "Wide Shaker", ""),
    ('WIDE_MITER', "Wide Miter", ""),
    ('COMBINATION', "Combination", ""),
]

# stile / door rail / drawer rail widths (inches) + miter flag.
_SPECS = {
    'NARROW_SHAKER': (2.25, 2.25, 2.25, False),
    'NARROW_MITER': (2.25, 2.25, 2.25, True),
    'WIDE_SHAKER': (3.0, 3.0, 3.0, False),
    'WIDE_MITER': (3.0, 3.0, 3.0, True),
    'CONTEMPORARY_SHAKER': (2.5, 3.0, 2.0, False),
    'CONTEMPORARY_MITER': (2.5, 3.0, 2.0, True),
    'COMBINATION': (2.5, 3.0, 2.0, False),
}

# Minimum front sizes (height, width in inches) per style; smaller
# fronts stay slabs.
_MIN_SIZES = {
    'NARROW_SHAKER': (5.5, 8.0625),
    'NARROW_MITER': (6.23, 6.23),
    'WIDE_SHAKER': (9.5, 9.5),
    'WIDE_MITER': (9.5, 9.5),
    'CONTEMPORARY_SHAKER': (5.5, 8.5),
    'CONTEMPORARY_MITER': (6.23, 6.0625),
    'COMBINATION': (7.0, 7.0),
}

_PANEL_THICKNESS = inch(0.25)
_PANEL_INSET = inch(0.5)


WRAP_GROUP_NAME = 'Closet Door Style'
# Bump to rebuild the wrapper's node graph in existing files (the group
# datablock is kept, so scene modifiers pick the rebuild up in place).
_WRAP_VERSION = 2


def _wrapped_door_group(base_group):
    """Find-or-create the rotation wrapper around the shared 5-piece
    builder (see the module docstring). Mirrors the base interface so
    socket-by-name writes work unchanged. The builder re-homes its
    output, so after rotating back the result is translated to the
    INPUT geometry's bounding-box corner (X/Y only) - otherwise the
    door lands shifted by its own width."""
    ng = bpy.data.node_groups.get(WRAP_GROUP_NAME)
    if ng is not None and ng.get('hb_wrap_version') == _WRAP_VERSION:
        return ng
    if ng is None:
        ng = bpy.data.node_groups.new(WRAP_GROUP_NAME,
                                      'GeometryNodeTree')
        for item in base_group.interface.items_tree:
            if item.item_type == 'SOCKET':
                ng.interface.new_socket(item.name, in_out=item.in_out,
                                        socket_type=item.socket_type)
    ng.nodes.clear()
    gin = ng.nodes.new('NodeGroupInput')
    gout = ng.nodes.new('NodeGroupOutput')
    rot_in = ng.nodes.new('GeometryNodeTransform')
    rot_out = ng.nodes.new('GeometryNodeTransform')
    rehome = ng.nodes.new('GeometryNodeTransform')
    grp = ng.nodes.new('GeometryNodeGroup')
    grp.node_tree = base_group
    bbox_in = ng.nodes.new('GeometryNodeBoundBox')
    bbox_out = ng.nodes.new('GeometryNodeBoundBox')
    delta = ng.nodes.new('ShaderNodeVectorMath')
    delta.operation = 'SUBTRACT'
    sep = ng.nodes.new('ShaderNodeSeparateXYZ')
    comb = ng.nodes.new('ShaderNodeCombineXYZ')
    rot_in.inputs['Rotation'].default_value = (0.0, 0.0,
                                               math.radians(-90.0))
    rot_out.inputs['Rotation'].default_value = (0.0, 0.0,
                                                math.radians(90.0))
    links = ng.links
    links.new(gin.outputs['Geometry'], rot_in.inputs['Geometry'])
    links.new(rot_in.outputs['Geometry'], grp.inputs['Geometry'])
    links.new(grp.outputs[0], rot_out.inputs['Geometry'])
    # Re-home: input bbox min - output bbox min, X/Y only (thickness
    # placement stays the builder's business).
    links.new(gin.outputs['Geometry'], bbox_in.inputs['Geometry'])
    links.new(rot_out.outputs['Geometry'], bbox_out.inputs['Geometry'])
    links.new(bbox_in.outputs['Min'], delta.inputs[0])
    links.new(bbox_out.outputs['Min'], delta.inputs[1])
    links.new(delta.outputs['Vector'], sep.inputs['Vector'])
    links.new(sep.outputs['X'], comb.inputs['X'])
    links.new(sep.outputs['Y'], comb.inputs['Y'])
    links.new(rot_out.outputs['Geometry'], rehome.inputs['Geometry'])
    links.new(comb.outputs['Vector'], rehome.inputs['Translation'])
    links.new(rehome.outputs['Geometry'], gout.inputs['Geometry'])
    for item in base_group.interface.items_tree:
        if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                and item.name != 'Geometry'):
            links.new(gin.outputs[item.name], grp.inputs[item.name])
    ng['hb_wrap_version'] = _WRAP_VERSION
    return ng


def current_style():
    return getattr(bpy.context.scene.hb_closets,
                   'closet_front_style', 'SLAB')


def _strip_style(front_obj):
    for mod in list(front_obj.modifiers):
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            front_obj.modifiers.remove(mod)
    if 'DOOR_STYLE_NAME' in front_obj:
        del front_obj['DOOR_STYLE_NAME']


def apply_style_to_front(front_obj, is_drawer, style=None):
    """Apply the selected style to one closet front cutpart. SLAB (and
    any front below the style's minimum size) strips the 'Door Style'
    modifier; otherwise the shared CPM_5PIECEDOOR modifier is
    added/updated with the style's widths. Called from the drawer/door
    layout passes every recalc, after the front's dims are written."""
    from ... import hb_types
    if style is None:
        style = current_style()
    spec = _SPECS.get(style)
    if spec is None:  # SLAB / unknown
        _strip_style(front_obj)
        return
    stile_in, rail_in, drawer_rail_in, miter = spec
    rail_in = drawer_rail_in if is_drawer else rail_in
    stile = inch(stile_in)
    rail = inch(rail_in)

    part = hb_types.GeoNodeCutpart(front_obj)
    try:
        f_width = part.get_input('Length')   # across
        f_height = part.get_input('Width')   # up
    except Exception:
        return
    min_h, min_w = _MIN_SIZES.get(style, (0.0, 0.0))
    if (f_height < inch(min_h) or f_width < inch(min_w)
            or f_width < 2.0 * stile + inch(1.0)
            or f_height < 2.0 * rail + inch(1.0)):
        _strip_style(front_obj)
        return

    existing = None
    for mod in front_obj.modifiers:
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            existing = mod
            break
    if existing is not None:
        style_mod = hb_types.CabinetPartModifier()
        style_mod.obj = front_obj
        style_mod.mod = existing
    else:
        style_mod = part.add_part_modifier('CPM_5PIECEDOOR', 'Door Style')

    # Route through the rotation wrapper (see module docstring) so the
    # builder's stiles land vertical; also migrates fronts that still
    # point at the RAW builder group (never re-wrap anything else -
    # a double wrap rotates the build 180 and swaps the members back).
    # An out-of-date wrapper rebuilds in place, keeping the datablock
    # every scene modifier already references.
    mod = style_mod.mod
    ngroup = mod.node_group
    if ngroup is not None:
        if ngroup.name.startswith('CPM_5PIECEDOOR'):
            mod.node_group = _wrapped_door_group(ngroup)
        elif (ngroup.name == WRAP_GROUP_NAME
                and ngroup.get('hb_wrap_version') != _WRAP_VERSION):
            base = next((n.node_tree for n in ngroup.nodes
                         if n.type == 'GROUP' and n.node_tree
                         is not None), None)
            if base is not None:
                _wrapped_door_group(base)

    style_mod.set_input('Left Stile Width', stile)
    style_mod.set_input('Right Stile Width', stile)
    style_mod.set_input('Top Rail Width', rail)
    style_mod.set_input('Bottom Rail Width', rail)
    style_mod.set_input('Use Miter', miter)
    style_mod.set_input('Panel Thickness', _PANEL_THICKNESS)
    style_mod.set_input('Panel Inset', _PANEL_INSET)
    front_obj['DOOR_STYLE_NAME'] = style
    # Freshly added modifiers have empty material sockets; give the
    # members grain-correct materials right away.
    try:
        from . import materials_closets
        materials_closets.apply_front_member_materials(front_obj,
                                                       is_drawer)
    except Exception:
        pass


def update_room(self=None, context=None):
    """Dropdown update callback: recalculate every starter - the front
    layout passes re-apply the style to each front."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
