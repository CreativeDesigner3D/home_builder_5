"""Closet door/drawer front style selection.

One scene-level dropdown styles every closet front. Styles are
parameter presets for the shared CPM_5PIECEDOOR part modifier (the same
node group the cabinet libraries use):

  Narrow Shaker/Miter        2.25" frame all around
  Wide Shaker/Miter          3" frame all around
  Contemporary Shaker/Miter  2.5" stiles, 3" rails (2" on drawers)
  Combination                2.5" stiles, 3" rails (2" on drawers)
  Slab                       flat (no modifier)

Panel: 1/4" thick, sitting flush in the frame opening. Each style
carries a MINIMUM front size; a front smaller than the minimum stays a slab so
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
import os

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
# The prior library sits the center panel flush in the frame
# opening, so there is no inset to set back.
_PANEL_INSET = 0.0


WRAP_GROUP_NAME = 'Closet Door Style'

# The Contemporary and Combination fronts carry an inner profile (reference
# assign_door_style): Contemporary the Traditional profile round the
# panel, set 3/4" in from the frame; Combination the Brunswick profile on
# its top and bottom rails only. CPM_5PIECEDOOR draws no inner profile, so
# these build on GeoNode5PieceDoor - the reference version's door builder,
# which ships with HB5 and takes the same sockets plus the profiles -
# through a wrapper of their own.
# style -> (inner profile, top/bottom-only profile, inner profile inset)
_PROFILED = {
    'CONTEMPORARY_SHAKER': ('InsideTraditionalDoorProfile', None,
                            inch(0.75)),
    'CONTEMPORARY_MITER': ('InsideTraditionalDoorProfile', None,
                           inch(0.75)),
    'COMBINATION': (None, 'InsideBrunswickDoorProfile', 0.0),
}
PROFILED_BASE = 'GeoNode5PieceDoor'
PROFILED_WRAP_NAME = 'Closet Door Style Profiled'
_WRAP_NAMES = (WRAP_GROUP_NAME, PROFILED_WRAP_NAME)


def _profiled_base_group():
    ng = bpy.data.node_groups.get(PROFILED_BASE)
    if ng is None:
        from ... import hb_types
        path = os.path.join(hb_types.geometry_nodes_path,
                            PROFILED_BASE + '.blend')
        with bpy.data.libraries.load(path) as (src, dst):
            dst.node_groups = [PROFILED_BASE]
        ng = bpy.data.node_groups.get(PROFILED_BASE)
    return ng


def _profile_object(name):
    """The inner profile curve, appended once from the door profiles."""
    if not name:
        return None
    obj = bpy.data.objects.get(name)
    if obj is not None:
        return obj
    from ..common import door_profiles
    try:
        with bpy.data.libraries.load(
                door_profiles.profile_path('INNER', name)) as (src, dst):
            dst.objects = [n for n in src.objects if n == name] or \
                list(src.objects)[:1]
    except Exception:
        return None
    return next((o for o in dst.objects if o is not None), None)


def _base_of(group):
    """The builder a style modifier runs: the group itself, or the one a
    rotation wrapper runs."""
    if group is not None and group.name in _WRAP_NAMES:
        return next((n.node_tree for n in group.nodes
                     if n.type == 'GROUP' and n.node_tree is not None),
                    None)
    return group
# Bump to rebuild the wrapper's node graph in existing files (the group
# datablock is kept, so scene modifiers pick the rebuild up in place).
_WRAP_VERSION = 2


def _wrapped_door_group(base_group, name=WRAP_GROUP_NAME):
    """Find-or-create the rotation wrapper around a 5-piece builder (see
    the module docstring). Mirrors the base interface so socket-by-name
    writes work unchanged. The builder re-homes its output, so after
    rotating back the result is translated to the INPUT geometry's
    bounding-box corner (X/Y only) - otherwise the door lands shifted by
    its own width."""
    ng = bpy.data.node_groups.get(name)
    if ng is not None and ng.get('hb_wrap_version') == _WRAP_VERSION:
        return ng
    if ng is None:
        ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
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


# Why a front is not the style it was given (types_closets.
# PROP_STYLE_WARNING), written each time its style is applied.
_PROP_STYLE_WARNING = 'hb_style_warning'


def _style_warning(front_obj, message):
    if message:
        front_obj[_PROP_STYLE_WARNING] = message
    elif _PROP_STYLE_WARNING in front_obj:
        del front_obj[_PROP_STYLE_WARNING]


_COLOR_WARNING = "Material Color not available for 5 Piece Doors"


def refresh_color_warnings(scene):
    """Re-judge every styled front against the front colour, for a
    colour change that does not re-solve the room."""
    try:
        from . import materials_closets
        bad = (materials_closets.front_color_name(scene.hb_closets)
               in materials_closets.NO_5PIECE_COLORS)
    except Exception:
        return
    for obj in scene.objects:
        # Closet fronts only: cabinet doors carry a style name too.
        if (obj.get('hb_part_role') not in ('CLOSET_DOOR_FRONT',
                                            'CLOSET_DRAWER_FRONT')
                or not obj.get('DOOR_STYLE_NAME')):
            continue
        current = obj.get(_PROP_STYLE_WARNING, '')
        if bad:
            _style_warning(obj, _COLOR_WARNING)
        elif current == _COLOR_WARNING:
            _style_warning(obj, '')


def _strip_style(front_obj):
    for mod in list(front_obj.modifiers):
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            front_obj.modifiers.remove(mod)
    if 'DOOR_STYLE_NAME' in front_obj:
        del front_obj['DOOR_STYLE_NAME']
    # A slab has no panel: drop the panel tags a styled front left, or a
    # door that was glass keeps reading as glass downstream.
    if 'hb_panel_type' in front_obj:
        del front_obj['hb_panel_type']
    if front_obj.get('IS_PREP_FOR_GLASS'):
        front_obj['IS_PREP_FOR_GLASS'] = False


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
    _style_warning(front_obj, '')
    if spec is None:  # SLAB / unknown
        _strip_style(front_obj)
        return
    try:
        from . import materials_closets
        no_5piece = (materials_closets.front_color_name(
            bpy.context.scene.hb_closets)
            in materials_closets.NO_5PIECE_COLORS)
    except Exception:
        no_5piece = False
    if no_5piece:
        # Built as asked, but not a front that can be ordered.
        _style_warning(front_obj, _COLOR_WARNING)
    stile_in, rail_in, drawer_rail_in, miter = spec
    rail_in = drawer_rail_in if is_drawer else rail_in
    stile = inch(stile_in)
    rail = inch(rail_in)

    part = hb_types.GeoNodeCutpart(front_obj)
    # A front cut length-up already runs its length the way the door
    # builder was authored for; one cut length-across does not, and
    # is turned into the builder's axis and back by the wrapper below.
    length_up = bool(front_obj.get('hb_front_length_up'))
    try:
        if length_up:
            f_width = part.get_input('Width')    # across
            f_height = part.get_input('Length')  # up
        else:
            f_width = part.get_input('Length')   # across
            f_height = part.get_input('Width')   # up
    except Exception:
        return
    min_h, min_w = _MIN_SIZES.get(style, (0.0, 0.0))
    # The style minimums are read as the reference read them
    # (valid_door_size_for_style): 'height' against the part's Length and
    # 'width' against its Width. That is the front's true height on a
    # door or a vertical-grain drawer front, and its width across on a
    # drawer front cut length-across.
    if (part.get_input('Length') < inch(min_h)
            or part.get_input('Width') < inch(min_w)
            or f_width < 2.0 * stile + inch(1.0)
            or f_height < 2.0 * rail + inch(1.0)):
        _strip_style(front_obj)
        _style_warning(front_obj,
                       "Front too small - defaulting to Slab style")
        return

    existing = None
    for mod in front_obj.modifiers:
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            existing = mod
            break
    profiled = _PROFILED.get(style)
    if existing is not None and profiled is None:
        # Back from a profiled style to a plain one: the profiled builder
        # is not the plain one, so the modifier is made afresh.
        base = _base_of(existing.node_group)
        if base is not None and base.name == PROFILED_BASE:
            front_obj.modifiers.remove(existing)
            existing = None
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
    # The builder this style runs - the profiled one for a profiled
    # style, else whichever plain one the modifier already carries -
    # straight through for a front cut length-up (it already runs its
    # length the way the builder was authored for), or inside its
    # rotation wrapper for one cut across. Worked out from the builder
    # each time, so nothing is ever wrapped twice (a double wrap turns
    # the build 180 and swaps the members back) and an out-of-date
    # wrapper rebuilds in place, keeping the datablock every scene
    # modifier already references.
    base = (_profiled_base_group() if profiled is not None
            else _base_of(mod.node_group))
    if base is not None:
        if length_up:
            if mod.node_group is not base:
                mod.node_group = base
        else:
            wrap = _wrapped_door_group(
                base, PROFILED_WRAP_NAME if profiled is not None
                else WRAP_GROUP_NAME)
            if mod.node_group is not wrap:
                mod.node_group = wrap

    style_mod.set_input('Left Stile Width', stile)
    style_mod.set_input('Right Stile Width', stile)
    style_mod.set_input('Top Rail Width', rail)
    style_mod.set_input('Bottom Rail Width', rail)
    style_mod.set_input('Use Miter', miter)
    style_mod.set_input('Panel Thickness', _PANEL_THICKNESS)
    style_mod.set_input('Panel Inset', _PANEL_INSET)
    if profiled is not None:
        inner, top_bottom, inset = profiled
        style_mod.set_input('Inner Profile', _profile_object(inner))
        style_mod.set_input('Inner Top Bottom Profile',
                            _profile_object(top_bottom))
        style_mod.set_input('Inner Profile Inset', inset)
    front_obj['DOOR_STYLE_NAME'] = style
    # Freshly added modifiers have empty material sockets; give the
    # members grain-correct materials right away.
    try:
        from . import materials_closets
        materials_closets.apply_front_member_materials(front_obj,
                                                       is_drawer)
    except Exception:
        pass


# The room style the fronts were last restyled to, so a change can tell
# what the fronts left out of it were wearing.
_PROP_LAST_ROOM_STYLE = 'hb_last_front_style'


# A front style written by a room change that skipped the front's kind
# (not by the person), so the next change that updates that kind can
# take it off again. Front Style on the front itself clears it.
PROP_STYLE_HELD_BY_ROOM = 'hb_style_held_by_room'


def _hold_fronts_out_of_restyle(scene, old_style):
    """The reference version's Update Doors in Room could restyle only the doors or only
    the drawer fronts. A kind left out keeps the style it had by being
    given it as its own (a front with a style of its own is not touched
    by the room's). Hampers follow the room either way, as in the reference."""
    room = scene.hb_closets
    doors = getattr(room, 'front_style_update_doors', True)
    drawers = getattr(room, 'front_style_update_drawer_fronts', True)
    from . import types_closets
    for obj in scene.objects:
        role = obj.get('hb_part_role')
        if role == types_closets.PART_ROLE_DOOR:
            update = doors or obj.get('hb_hinge') == 'BOTTOM'
        elif role == types_closets.PART_ROLE_DRAWER_FRONT:
            update = drawers
        else:
            continue
        held = bool(obj.get(PROP_STYLE_HELD_BY_ROOM))
        if update:
            # The skip is one-shot (as in the reference): a front held back by an
            # earlier change follows the room again once its kind is
            # updated. A style set on the front itself is left alone.
            if held:
                del obj[PROP_STYLE_HELD_BY_ROOM]
                if types_closets.PROP_FRONT_STYLE in obj:
                    del obj[types_closets.PROP_FRONT_STYLE]
        elif not obj.get(types_closets.PROP_FRONT_STYLE):
            obj[types_closets.PROP_FRONT_STYLE] = old_style
            obj[PROP_STYLE_HELD_BY_ROOM] = 1


def note_room_style(self=None, context=None):
    """Update Doors / Update Drawer Fronts toggled: remember the style
    the fronts are wearing now, so the next style change knows what to
    leave the fronts it skips in."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    scene[_PROP_LAST_ROOM_STYLE] = current_style()


def update_room(self=None, context=None):
    """Dropdown update callback: recalculate every starter - the front
    layout passes re-apply the style to each front. Doors or drawer
    fronts the room is set not to update keep the style they had
    (_hold_fronts_out_of_restyle)."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    new_style = current_style()
    old_style = scene.get(_PROP_LAST_ROOM_STYLE)
    if old_style and old_style != new_style:
        _hold_fronts_out_of_restyle(scene, old_style)
    scene[_PROP_LAST_ROOM_STYLE] = new_style
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
