"""
Diamond vent: a pattern of four diamond holes cut through a door.

The pattern is set out in thirds: four equal diamonds in a box three
diamonds wide and three tall - one in the middle of the top third, one
in the middle of the bottom third, one at each end of the middle third.
Neighbouring diamonds meet on the third lines, so the bottom point of
the top diamond is level with the top points of the side ones, and its
side points are plumb with their inner points. One diamond's width and
height (2" by 2-2/3" unless set per door, a 6" by 8" pattern) size the
whole thing. It sits centred on the door's panel field (the slab itself
on a slab door), moved up or down by a per-door amount, and cuts all
the way through the part.

The cut is a geometry node modifier ('Diamond Vent', node group
CPM_DIAMONDVENT) at the end of the front's stack, built in Python like
the arch cutout. It is self-contained - the pattern centre is a modifier
input and the cut walls take the material of the face they cut through
- so the drawing copies of a front show the holes too.

Fronts are torn down and rebuilt as new objects on every recalc, so the
choice is stamped per leaf on the front's durable store (its opening
cage; a cage-less door is its own store), the same way the per-door
hardware callouts are, and sync() re-applies it whenever a door style
is assigned to a front.

Front-local frame (the cutpart convention): X runs up the door, Y
across it, Z through its thickness.
"""

import bpy

from ... import hb_utils
from ...units import inch

NODE_GROUP_NAME = 'CPM_DIAMONDVENT'
VERSION = 4
VERSION_KEY = 'HB_DIAMOND_VENT_VERSION'
MODIFIER_NAME = 'Diamond Vent'

# Per-leaf store key prefix: '<key>_<leaf index>' = True, with the
# optional per-door settings under '<key>_<leaf index>_<suffix>'.
VENT_KEY = 'HB_DOOR_VENT'
_WIDTH_SUFFIX = '_W'
_HEIGHT_SUFFIX = '_H'
_RISE_SUFFIX = '_Z'

# One diamond. The pattern is three of these wide and three tall.
DEFAULT_DIAMOND_WIDTH = inch(2.0)
DEFAULT_DIAMOND_HEIGHT = inch(8.0) / 3.0
MIN_DIAMOND_SIZE = inch(0.25)
# Diamond centres, in front-local (X up the door, Y across it), from
# the pattern centre, in whole diamonds: (heights up, widths across).
DIAMOND_CENTRES = (
    (1.0, 0.0),     # top
    (-1.0, 0.0),    # bottom
    (0.0, 1.0),
    (0.0, -1.0),
)
# How far each cutter runs past the door's faces, so the cut never
# shares a face with them.
OVERSHOOT = 0.002

# Faces carrying these material slots on a python-built door are its
# panel field (door_builder: 0 stile, 1 rail, 2 panel, 3 glass).
_PANEL_SLOTS = (2, 3)

# Named attribute marking the cutter's faces through the boolean, so
# the hole walls can take the cut face's material afterwards.
_WALL_ATTR = 'hb_vent_wall'

_SOCKETS = (
    ('Geometry', 'OUTPUT', 'NodeSocketGeometry'),
    ('Geometry', 'INPUT', 'NodeSocketGeometry'),
    ('Offset X', 'INPUT', 'NodeSocketFloat'),
    ('Offset Y', 'INPUT', 'NodeSocketFloat'),
    ('Diamond Width', 'INPUT', 'NodeSocketFloat'),
    ('Diamond Height', 'INPUT', 'NodeSocketFloat'),
)
_SOCKET_DEFAULTS = {
    'Diamond Width': DEFAULT_DIAMOND_WIDTH,
    'Diamond Height': DEFAULT_DIAMOND_HEIGHT,
}


# ---- Node group --------------------------------------------------------

def ensure_node_group():
    """The vent node group, built on first use and rebuilt in place when
    an older version is found."""
    ng = bpy.data.node_groups.get(NODE_GROUP_NAME)
    if ng is not None and ng.get(VERSION_KEY) == VERSION:
        return ng
    if ng is None:
        ng = bpy.data.node_groups.new(NODE_GROUP_NAME, 'GeometryNodeTree')
    have = {(i.name, i.in_out) for i in ng.interface.items_tree
            if i.item_type == 'SOCKET'}
    for name, in_out, socket_type in _SOCKETS:
        if (name, in_out) not in have:
            sock = ng.interface.new_socket(name, in_out=in_out,
                                           socket_type=socket_type)
            if name in _SOCKET_DEFAULTS:
                sock.default_value = _SOCKET_DEFAULTS[name]
    ng.nodes.clear()
    _build(ng)
    ng[VERSION_KEY] = VERSION
    return ng


def _build(ng):
    nodes, links = ng.nodes, ng.links
    gi = nodes.new('NodeGroupInput')
    go = nodes.new('NodeGroupOutput')

    def vmath(op, a, b):
        n = nodes.new('ShaderNodeVectorMath')
        n.operation = op
        for sock, v in ((n.inputs[0], a), (n.inputs[1], b)):
            if isinstance(v, tuple):
                sock.default_value = v
            else:
                links.new(v, sock)
        return n.outputs[0]

    # Pattern centre: the door's bounds centre, moved by the offsets
    # (panel field centre less bounds centre, written by sync()).
    bbox = nodes.new('GeometryNodeBoundBox')
    links.new(gi.outputs['Geometry'], bbox.inputs['Geometry'])
    mid = vmath('MULTIPLY', vmath('ADD', bbox.outputs['Min'],
                                  bbox.outputs['Max']), (0.5, 0.5, 0.5))
    offset = nodes.new('ShaderNodeCombineXYZ')
    links.new(gi.outputs['Offset X'], offset.inputs[0])
    links.new(gi.outputs['Offset Y'], offset.inputs[1])
    centre = vmath('ADD', mid, offset.outputs[0])
    size = nodes.new('ShaderNodeSeparateXYZ')
    links.new(vmath('SUBTRACT', bbox.outputs['Max'], bbox.outputs['Min']),
              size.inputs[0])
    depth = nodes.new('ShaderNodeMath')
    depth.operation = 'ADD'
    links.new(size.outputs[2], depth.inputs[0])
    depth.inputs[1].default_value = 2.0 * OVERSHOOT

    # One diamond: a four-sided prism (cylinder vertices land on the
    # axes, so its points face up / down / left / right), unit radius,
    # scaled to the diamond and through the door's whole thickness.
    prism = nodes.new('GeometryNodeMeshCylinder')
    prism.fill_type = 'NGON'
    prism.inputs['Vertices'].default_value = 4
    prism.inputs['Radius'].default_value = 1.0
    prism.inputs['Depth'].default_value = 1.0

    def times(sock, factor):
        n = nodes.new('ShaderNodeMath')
        n.operation = 'MULTIPLY'
        links.new(sock, n.inputs[0])
        n.inputs[1].default_value = factor
        return n.outputs[0]

    scale = nodes.new('ShaderNodeCombineXYZ')
    links.new(times(gi.outputs['Diamond Height'], 0.5), scale.inputs[0])
    links.new(times(gi.outputs['Diamond Width'], 0.5), scale.inputs[1])
    links.new(depth.outputs[0], scale.inputs[2])
    # One diamond's size as a vector, so each centre is a whole number
    # of diamonds from the pattern centre.
    step = nodes.new('ShaderNodeCombineXYZ')
    links.new(gi.outputs['Diamond Height'], step.inputs[0])
    links.new(gi.outputs['Diamond Width'], step.inputs[1])

    join = nodes.new('GeometryNodeJoinGeometry')
    for cx, cy in DIAMOND_CENTRES:
        xf = nodes.new('GeometryNodeTransform')
        links.new(prism.outputs['Mesh'], xf.inputs['Geometry'])
        links.new(vmath('ADD', centre,
                        vmath('MULTIPLY', step.outputs[0], (cx, cy, 0.0))),
                  xf.inputs['Translation'])
        links.new(scale.outputs[0], xf.inputs['Scale'])
        links.new(xf.outputs['Geometry'], join.inputs['Geometry'])

    mark = nodes.new('GeometryNodeStoreNamedAttribute')
    mark.data_type = 'BOOLEAN'
    mark.domain = 'FACE'
    mark.inputs['Name'].default_value = _WALL_ATTR
    mark.inputs['Value'].default_value = True
    links.new(join.outputs['Geometry'], mark.inputs['Geometry'])

    # A python-built door is several closed parts that touch (stiles,
    # rails, panel, sticking strips), so the exact solver has to treat
    # the door as self-intersecting or it drops whole parts.
    cut = nodes.new('GeometryNodeMeshBoolean')
    cut.operation = 'DIFFERENCE'
    cut.solver = 'EXACT'
    cut.inputs['Self Intersection'].default_value = True
    cut.inputs['Hole Tolerant'].default_value = True
    links.new(gi.outputs['Geometry'], cut.inputs['Mesh 1'])
    links.new(mark.outputs['Geometry'], cut.inputs['Mesh 2'])

    # Hole walls take the material index of the nearest door face they
    # cut through - the panel (or the slab). Sampled from the cut mesh
    # itself, walls left out, since the boolean can renumber the
    # material slots when two of them hold the same material.
    was_wall = nodes.new('GeometryNodeInputNamedAttribute')
    was_wall.data_type = 'BOOLEAN'
    was_wall.inputs['Name'].default_value = _WALL_ATTR
    door_faces = nodes.new('GeometryNodeSeparateGeometry')
    door_faces.domain = 'FACE'
    links.new(cut.outputs['Mesh'], door_faces.inputs['Geometry'])
    links.new(was_wall.outputs['Attribute'], door_faces.inputs['Selection'])
    nearest = nodes.new('GeometryNodeSampleNearestSurface')
    nearest.data_type = 'INT'
    links.new(door_faces.outputs['Inverted'], nearest.inputs['Mesh'])
    links.new(nodes.new('GeometryNodeInputMaterialIndex').outputs[0],
              nearest.inputs['Value'])
    links.new(nodes.new('GeometryNodeInputPosition').outputs[0],
              nearest.inputs['Sample Position'])
    set_index = nodes.new('GeometryNodeSetMaterialIndex')
    links.new(cut.outputs['Mesh'], set_index.inputs['Geometry'])
    links.new(was_wall.outputs['Attribute'], set_index.inputs['Selection'])
    links.new(nearest.outputs['Value'], set_index.inputs['Material Index'])

    drop = nodes.new('GeometryNodeRemoveAttribute')
    drop.inputs['Name'].default_value = _WALL_ATTR
    links.new(set_index.outputs['Geometry'], drop.inputs['Geometry'])
    links.new(drop.outputs['Geometry'], go.inputs['Geometry'])


# ---- Per-door choice ----------------------------------------------------

def _store_and_key(front_obj):
    from . import props_hb_face_frame as props
    store = props._front_frame_store(front_obj)
    i = props.front_leaf_index(front_obj, store)
    return store, '%s_%d' % (VENT_KEY, i)


def has_vent(front_obj):
    """True when this door carries the diamond vent."""
    store, key = _store_and_key(front_obj)
    return bool(store.get(key, False))


def set_vent(front_obj, on):
    """Stamp (or clear) the vent on this door's leaf and apply it now.
    Clearing it drops the door's own size and position too."""
    store, key = _store_and_key(front_obj)
    if on:
        store[key] = True
    else:
        for k in (key, key + _WIDTH_SUFFIX, key + _HEIGHT_SUFFIX,
                  key + _RISE_SUFFIX):
            if k in store:
                del store[k]
    sync(front_obj)


def vent_settings(front_obj):
    """(diamond width, diamond height, rise) of this door's vent: one
    diamond's size, and how far the pattern sits above the panel centre
    (negative = below)."""
    store, key = _store_and_key(front_obj)
    width = float(store.get(key + _WIDTH_SUFFIX, DEFAULT_DIAMOND_WIDTH))
    height = float(store.get(key + _HEIGHT_SUFFIX, DEFAULT_DIAMOND_HEIGHT))
    rise = float(store.get(key + _RISE_SUFFIX, 0.0))
    return (max(width, MIN_DIAMOND_SIZE), max(height, MIN_DIAMOND_SIZE),
            rise)


def set_vent_settings(front_obj, width, height, rise):
    """Keep this door's diamond size and rise and apply them now. The
    door needs the vent already (set_vent)."""
    store, key = _store_and_key(front_obj)
    store[key + _WIDTH_SUFFIX] = max(float(width), MIN_DIAMOND_SIZE)
    store[key + _HEIGHT_SUFFIX] = max(float(height), MIN_DIAMOND_SIZE)
    store[key + _RISE_SUFFIX] = float(rise)
    sync(front_obj)


# ---- On the door's page -------------------------------------------------
# The same settings as fields: whether the door has the vent, the
# pattern's overall size (three diamonds wide and tall) and how far it
# sits above the panel centre. Each write is applied at once.

VENT_SCHEMA = 'FF_DOOR_VENT'


def pattern_size(front_obj):
    """(overall width, overall height, rise) of this door's pattern."""
    width, height, rise = vent_settings(front_obj)
    return width * 3.0, height * 3.0, rise


def set_pattern_size(front_obj, width=None, height=None, rise=None):
    """Change any of the pattern's overall width, overall height and
    rise on a door that has the vent, keeping the rest."""
    if not has_vent(front_obj):
        return
    now = pattern_size(front_obj)
    width = now[0] if width is None else float(width)
    height = now[1] if height is None else float(height)
    rise = now[2] if rise is None else float(rise)
    set_vent_settings(front_obj, width / 3.0, height / 3.0, rise)


def vent_owner(front_obj):
    """The door's vent settings as an owner the field engine reads."""
    from ...operators import prop_proxy as P
    if VENT_SCHEMA not in P._schemas:
        P.register(VENT_SCHEMA, {
            'on': P.computed(has_vent, lambda o, v: set_vent(o, bool(v)),
                             type='BOOLEAN'),
            'width': P.computed(
                lambda o: pattern_size(o)[0],
                lambda o, v: set_pattern_size(o, width=v),
                unit='LENGTH', precision=4, hard_min=MIN_DIAMOND_SIZE * 3.0),
            'height': P.computed(
                lambda o: pattern_size(o)[1],
                lambda o, v: set_pattern_size(o, height=v),
                unit='LENGTH', precision=4, hard_min=MIN_DIAMOND_SIZE * 3.0),
            'rise': P.computed(
                lambda o: pattern_size(o)[2],
                lambda o, v: set_pattern_size(o, rise=v),
                unit='LENGTH', precision=4),
        })
    return P.owner(front_obj, VENT_SCHEMA)


def vent_fields():
    on = {'when': lambda o: bool(o.on)}
    return (
        ('bool', 'on', "Diamond Vent"),
        ('distance', 'width', "Vent Width", on),
        ('distance', 'height', "Vent Height", on),
        ('distance', 'rise', "Vent Move Up", on),
    )


def _vent_modifier(front_obj):
    for mod in front_obj.modifiers:
        if (mod.type == 'NODES' and mod.node_group
                and mod.node_group.name == NODE_GROUP_NAME):
            return mod
    return None


def _panel_offset(front_obj):
    """(x, y) from the door mesh's bounds centre to its panel field's
    centre, or (0, 0) when the door has no panel faces (a slab, or a
    door built by a modifier rather than into its own mesh)."""
    if 'HB_DOOR_FRAME' not in front_obj or 'HB_STATIC_SLAB' in front_obj:
        return 0.0, 0.0
    me = front_obj.data
    if me is None or not me.vertices:
        return 0.0, 0.0
    co = [v.co for v in me.vertices]
    panel = set()
    for poly in me.polygons:
        if poly.material_index in _PANEL_SLOTS:
            panel.update(poly.vertices)
    if not panel:
        return 0.0, 0.0

    def centre(points, axis):
        vals = [p[axis] for p in points]
        return (min(vals) + max(vals)) / 2.0

    field = [co[i] for i in panel]
    return (centre(field, 0) - centre(co, 0),
            centre(field, 1) - centre(co, 1))


def sync(front_obj):
    """Bring the front's vent modifier in line with its stamp: add (or
    re-centre) it at the end of the stack, or take it off."""
    if front_obj is None or front_obj.type != 'MESH':
        return
    mod = _vent_modifier(front_obj)
    if not has_vent(front_obj):
        if mod is not None:
            front_obj.modifiers.remove(mod)
        return
    if mod is None:
        mod = front_obj.modifiers.new(MODIFIER_NAME, 'NODES')
    mod.node_group = ensure_node_group()
    # Last in the stack, so it cuts whatever the door style built.
    last = len(front_obj.modifiers) - 1
    if front_obj.modifiers.find(mod.name) != last:
        front_obj.modifiers.move(front_obj.modifiers.find(mod.name), last)
    off_x, off_y = _panel_offset(front_obj)
    width, height, rise = vent_settings(front_obj)
    values = {
        'Offset X': off_x + rise,
        'Offset Y': off_y,
        'Diamond Width': width,
        'Diamond Height': height,
    }
    for item in mod.node_group.interface.items_tree:
        if item.item_type != 'SOCKET' or item.in_out != 'INPUT':
            continue
        if item.name in values:
            hb_utils.set_gn_input(mod, item.identifier, values[item.name])
    front_obj.update_tag()


def _on_recalc(root):
    """After a cabinet recalc: the rebuilt doors that a door style
    didn't pass through (no style resolved) still need their vents."""
    for obj in root.children_recursive:
        if obj.get('hb_part_role') == 'DOOR':
            sync(obj)


def register():
    from . import types_face_frame
    if _on_recalc not in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.append(_on_recalc)


def unregister():
    from . import types_face_frame
    if _on_recalc in types_face_frame.POST_RECALC_HOOKS:
        types_face_frame.POST_RECALC_HOOKS.remove(_on_recalc)
