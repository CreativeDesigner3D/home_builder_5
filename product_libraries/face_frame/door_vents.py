"""
Diamond vent: a fixed pattern of four diamond holes cut through a door.

The pattern is a static shop detail, not a parametric one: four
diamonds 1.20" wide by 0.90" tall, set out as a larger diamond in a
4.00" by 3.00" box - left / right diamonds 1.40" either side of centre,
top / bottom diamonds 1.05" above and below it. It sits centred on the
door's panel field (the slab itself on a slab door) and cuts all the
way through the part.

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
VERSION = 3
VERSION_KEY = 'HB_DIAMOND_VENT_VERSION'
MODIFIER_NAME = 'Diamond Vent'

# Per-leaf store key prefix: '<key>_<leaf index>' = True.
VENT_KEY = 'HB_DOOR_VENT'

# The pattern, in front-local (X up the door, Y across it), from its
# centre: (centre x, centre y) of each diamond.
DIAMOND_HALF_HEIGHT = inch(0.90) / 2.0
DIAMOND_HALF_WIDTH = inch(1.20) / 2.0
DIAMOND_CENTRES = (
    (inch(1.05), 0.0),     # top
    (-inch(1.05), 0.0),    # bottom
    (0.0, inch(1.40)),
    (0.0, -inch(1.40)),
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
)


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
            ng.interface.new_socket(name, in_out=in_out,
                                    socket_type=socket_type)
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
    scale = nodes.new('ShaderNodeCombineXYZ')
    scale.inputs[0].default_value = DIAMOND_HALF_HEIGHT
    scale.inputs[1].default_value = DIAMOND_HALF_WIDTH
    links.new(depth.outputs[0], scale.inputs[2])

    join = nodes.new('GeometryNodeJoinGeometry')
    for cx, cy in DIAMOND_CENTRES:
        xf = nodes.new('GeometryNodeTransform')
        links.new(prism.outputs['Mesh'], xf.inputs['Geometry'])
        links.new(vmath('ADD', centre, (cx, cy, 0.0)),
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
    """Stamp (or clear) the vent on this door's leaf and apply it now."""
    store, key = _store_and_key(front_obj)
    if on:
        store[key] = True
    elif key in store:
        del store[key]
    sync(front_obj)


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
    for item in mod.node_group.interface.items_tree:
        if item.item_type != 'SOCKET' or item.in_out != 'INPUT':
            continue
        if item.name == 'Offset X':
            hb_utils.set_gn_input(mod, item.identifier, off_x)
        elif item.name == 'Offset Y':
            hb_utils.set_gn_input(mod, item.identifier, off_y)
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
