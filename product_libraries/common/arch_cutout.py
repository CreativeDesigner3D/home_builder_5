"""
Arch / circle cutout: a circular-segment or round hole or route cut
into a cutpart.

The companion of the CPM_CUTOUT rectangle, built as a geometry node
group in Python (there is no .blend asset for it) so the shape logic
stays readable here. Like CPM_CUTOUT it is self-contained - every value
it needs is a modifier input - so a copy of the part (the 2D drawings
draw a rotated copy) shows the cut too.

Inputs are in the part's local space, the same frame CPM_CUTOUT uses:

    X / End X, Y / End Y   the arch's bounding rectangle
    Flat Side              which side of that rectangle is the chord:
                           0 = X, 1 = End X, 2 = Y, 3 = End Y; the arch
                           bulges from it across the rectangle
    Open Edge              the chord lies on a part edge; the cutter
                           runs past it so the cut opens cleanly there
    Full Circle            cut the whole circle centred in the
                           rectangle instead (diameter = its shorter
                           side); Flat Side / Open Edge are ignored
    Route Depth / Flip Z   as CPM_CUTOUT (cut from the Z=0 face, or the
                           opposite face with Flip Z)
    Material               material on the cut walls

The chord is the rectangle's side length c along the flat side and the
rise h its depth across it; h is held to c / 2 at most (a half circle).
The circle through the chord ends and the apex has radius
R = (c^2 / 4 + h^2) / (2 h), centred h - R in from the chord midpoint,
and is clipped to the rectangle.
"""

import bpy

NODE_GROUP_NAME = 'CPM_ARCHCUTOUT'
# 2: Full Circle input.
VERSION = 2
VERSION_KEY = 'HB_ARCH_CUTOUT_VERSION'

# Circle resolution. Fine enough that the flat facets don't read on a
# 30" arch, cheap enough for the exact boolean.
CIRCLE_VERTICES = 96
# How far the cutter runs past an open edge (and the clip box past the
# circle in Z, so the two never share a face).
OVERSHOOT = 0.002

FLAT_SIDE_ITEMS = (0, 1, 2, 3)


# Interface, in order. Sockets are only ever added (by name), never
# rebuilt, so the values on cutouts already in a file survive a version
# upgrade of the nodes.
_SOCKETS = (
    ('Geometry', 'OUTPUT', 'NodeSocketGeometry'),
    ('Geometry', 'INPUT', 'NodeSocketGeometry'),
    ('X', 'INPUT', 'NodeSocketFloat'),
    ('End X', 'INPUT', 'NodeSocketFloat'),
    ('Y', 'INPUT', 'NodeSocketFloat'),
    ('End Y', 'INPUT', 'NodeSocketFloat'),
    ('Flat Side', 'INPUT', 'NodeSocketInt'),
    ('Open Edge', 'INPUT', 'NodeSocketBool'),
    ('Route Depth', 'INPUT', 'NodeSocketFloat'),
    ('Flip Z', 'INPUT', 'NodeSocketBool'),
    ('Material', 'INPUT', 'NodeSocketMaterial'),
    ('Full Circle', 'INPUT', 'NodeSocketBool'),
)


def ensure_node_group():
    """The arch cutout node group, built on first use and rebuilt in
    place when an older version is found."""
    ng = bpy.data.node_groups.get(NODE_GROUP_NAME)
    if ng is not None and ng.get(VERSION_KEY) == VERSION:
        return ng
    if ng is None:
        ng = bpy.data.node_groups.new(NODE_GROUP_NAME, 'GeometryNodeTree')
    _ensure_interface(ng)
    ng.nodes.clear()
    _build(ng)
    ng[VERSION_KEY] = VERSION
    return ng


def _ensure_interface(ng):
    have = {(i.name, i.in_out) for i in ng.interface.items_tree
            if i.item_type == 'SOCKET'}
    for name, in_out, socket_type in _SOCKETS:
        if (name, in_out) in have:
            continue
        s = ng.interface.new_socket(name, in_out=in_out,
                                    socket_type=socket_type)
        if name == 'Flat Side':
            s.min_value, s.max_value = 0, 3


def _build(ng):
    nodes, links = ng.nodes, ng.links
    gi = nodes.new('NodeGroupInput')
    go = nodes.new('NodeGroupOutput')

    def math(op, a, b=None):
        n = nodes.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]

    def combine(x, y, z):
        n = nodes.new('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]

    def index_switch(data_type, values):
        n = nodes.new('GeometryNodeIndexSwitch')
        n.data_type = data_type
        while len(n.index_switch_items) < len(values):
            n.index_switch_items.new()
        links.new(gi.outputs['Flat Side'], n.inputs['Index'])
        for i, v in enumerate(values):
            sock = n.inputs[i + 1]
            if isinstance(v, (int, float, tuple)):
                sock.default_value = v
            else:
                links.new(v, sock)
        return n.outputs[0]

    def switch(data_type, cond, if_false, if_true):
        n = nodes.new('GeometryNodeSwitch')
        n.input_type = data_type
        links.new(cond, n.inputs['Switch'])
        for sock, v in ((n.inputs['False'], if_false),
                        (n.inputs['True'], if_true)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            else:
                links.new(v, sock)
        return n.outputs[0]

    x0, x1 = gi.outputs['X'], gi.outputs['End X']
    y0, y1 = gi.outputs['Y'], gi.outputs['End Y']
    dx = math('SUBTRACT', x1, x0)
    dy = math('SUBTRACT', y1, y0)
    mid_x = math('MULTIPLY', math('ADD', x0, x1), 0.5)
    mid_y = math('MULTIPLY', math('ADD', y0, y1), 0.5)

    # Chord and rise per flat side; rise held to a half circle.
    chord = index_switch('FLOAT', (dy, dy, dx, dx))
    rise_raw = index_switch('FLOAT', (dx, dx, dy, dy))
    rise = math('MAXIMUM', math('MINIMUM', rise_raw,
                                math('MULTIPLY', chord, 0.5)), 1e-6)
    # R = (c^2 / 4 + h^2) / (2 h)
    radius = math('DIVIDE',
                  math('ADD', math('MULTIPLY', math('MULTIPLY', chord, chord),
                                   0.25),
                       math('MULTIPLY', rise, rise)),
                  math('MULTIPLY', rise, 2.0))
    inset = math('SUBTRACT', rise, radius)          # centre in from the chord
    full = gi.outputs['Full Circle']
    chord_mid = index_switch('VECTOR', (combine(x0, mid_y, 0.0),
                                        combine(x1, mid_y, 0.0),
                                        combine(mid_x, y0, 0.0),
                                        combine(mid_x, y1, 0.0)))
    normal = index_switch('VECTOR', ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0),
                                     (0.0, 1.0, 0.0), (0.0, -1.0, 0.0)))

    # Z: the cut's centre plane - the Z=0 face, or the opposite face with
    # Flip Z - and a mirrored part (geometry in negative local space) is
    # shifted to its own min corner, both as CPM_CUTOUT does.
    bbox = nodes.new('GeometryNodeBoundBox')
    links.new(gi.outputs['Geometry'], bbox.inputs['Geometry'])
    sep_min = nodes.new('ShaderNodeSeparateXYZ')
    links.new(bbox.outputs['Min'], sep_min.inputs[0])
    sep_max = nodes.new('ShaderNodeSeparateXYZ')
    links.new(bbox.outputs['Max'], sep_max.inputs[0])
    offs = []
    for i in range(3):
        mirrored = math('LESS_THAN', sep_max.outputs[i], 1e-6)
        offs.append(switch('FLOAT', mirrored, 0.0, sep_min.outputs[i]))
    thickness = math('SUBTRACT', sep_max.outputs[2], sep_min.outputs[2])
    z_face = switch('FLOAT', gi.outputs['Flip Z'], 0.0, thickness)
    z_centre = math('ADD', z_face, offs[2])
    offset = combine(offs[0], offs[1], z_centre)
    # Centred on the cut face, twice the depth tall, so exactly the route
    # depth lands in the part (CPM_CUTOUT's convention).
    height = math('MULTIPLY', gi.outputs['Route Depth'], 2.0)

    # Circle.
    cyl = nodes.new('GeometryNodeMeshCylinder')
    cyl.fill_type = 'NGON'
    cyl.inputs['Vertices'].default_value = CIRCLE_VERTICES
    # Full circle: the rectangle's inscribed circle, unclipped.
    full_radius = math('MULTIPLY', math('MINIMUM', dx, dy), 0.5)
    links.new(switch('FLOAT', full, radius, full_radius),
              cyl.inputs['Radius'])
    links.new(height, cyl.inputs['Depth'])
    centre = nodes.new('ShaderNodeVectorMath')
    centre.operation = 'MULTIPLY_ADD'
    links.new(normal, centre.inputs[0])
    links.new(combine(inset, inset, 0.0), centre.inputs[1])
    links.new(chord_mid, centre.inputs[2])
    rect_mid = combine(mid_x, mid_y, 0.0)
    arch_or_full = nodes.new('GeometryNodeSwitch')
    arch_or_full.input_type = 'VECTOR'
    links.new(full, arch_or_full.inputs['Switch'])
    links.new(centre.outputs[0], arch_or_full.inputs['False'])
    links.new(rect_mid, arch_or_full.inputs['True'])
    cyl_pos = nodes.new('ShaderNodeVectorMath')
    cyl_pos.operation = 'ADD'
    links.new(arch_or_full.outputs[0], cyl_pos.inputs[0])
    links.new(offset, cyl_pos.inputs[1])
    cyl_xf = nodes.new('GeometryNodeTransform')
    links.new(cyl.outputs['Mesh'], cyl_xf.inputs['Geometry'])
    links.new(cyl_pos.outputs[0], cyl_xf.inputs['Translation'])

    # Clip box: the rectangle, run past the chord on an open edge.
    over = switch('FLOAT', gi.outputs['Open Edge'], 0.0, OVERSHOOT)
    grow_lo = index_switch('VECTOR', (combine(over, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      combine(0.0, over, 0.0),
                                      (0.0, 0.0, 0.0)))
    grow_hi = index_switch('VECTOR', ((0.0, 0.0, 0.0),
                                      combine(over, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      combine(0.0, over, 0.0)))
    lo = nodes.new('ShaderNodeVectorMath')
    lo.operation = 'SUBTRACT'
    links.new(combine(x0, y0, 0.0), lo.inputs[0])
    links.new(grow_lo, lo.inputs[1])
    hi = nodes.new('ShaderNodeVectorMath')
    hi.operation = 'ADD'
    links.new(combine(x1, y1, 0.0), hi.inputs[0])
    links.new(grow_hi, hi.inputs[1])
    size = nodes.new('ShaderNodeVectorMath')
    size.operation = 'SUBTRACT'
    links.new(hi.outputs[0], size.inputs[0])
    links.new(lo.outputs[0], size.inputs[1])
    sep_size = nodes.new('ShaderNodeSeparateXYZ')
    links.new(size.outputs[0], sep_size.inputs[0])
    box = nodes.new('GeometryNodeMeshCube')
    links.new(combine(sep_size.outputs[0], sep_size.outputs[1],
                      math('ADD', height, OVERSHOOT)), box.inputs['Size'])
    box_mid = nodes.new('ShaderNodeVectorMath')
    box_mid.operation = 'MULTIPLY_ADD'
    links.new(size.outputs[0], box_mid.inputs[0])
    box_mid.inputs[1].default_value = (0.5, 0.5, 0.5)
    links.new(lo.outputs[0], box_mid.inputs[2])
    box_pos = nodes.new('ShaderNodeVectorMath')
    box_pos.operation = 'ADD'
    links.new(box_mid.outputs[0], box_pos.inputs[0])
    links.new(offset, box_pos.inputs[1])
    box_xf = nodes.new('GeometryNodeTransform')
    links.new(box.outputs['Mesh'], box_xf.inputs['Geometry'])
    links.new(box_pos.outputs[0], box_xf.inputs['Translation'])

    clip = nodes.new('GeometryNodeMeshBoolean')
    clip.operation = 'INTERSECT'
    clip.solver = 'EXACT'
    links.new(cyl_xf.outputs['Geometry'], clip.inputs['Mesh 2'])
    links.new(box_xf.outputs['Geometry'], clip.inputs['Mesh 2'])

    cutter = nodes.new('GeometryNodeSwitch')
    cutter.input_type = 'GEOMETRY'
    links.new(full, cutter.inputs['Switch'])
    links.new(clip.outputs['Mesh'], cutter.inputs['False'])
    links.new(cyl_xf.outputs['Geometry'], cutter.inputs['True'])

    set_mat = nodes.new('GeometryNodeSetMaterial')
    links.new(cutter.outputs[0], set_mat.inputs['Geometry'])
    links.new(gi.outputs['Material'], set_mat.inputs['Material'])

    cut = nodes.new('GeometryNodeMeshBoolean')
    cut.operation = 'DIFFERENCE'
    cut.solver = 'EXACT'
    links.new(gi.outputs['Geometry'], cut.inputs['Mesh 1'])
    links.new(set_mat.outputs['Geometry'], cut.inputs['Mesh 2'])
    links.new(cut.outputs['Mesh'], go.inputs['Geometry'])


def arch_rect(length, width, chord, rise, flat_side, open_edge, center,
              offset_length, offset_width):
    """The bounding rectangle (x0, x1, y0, y1) of an arch on a part face
    of ``length`` (X) by ``width`` (Y), kept on the face.

    ``flat_side`` names the part edge the arch's flat side faces
    ('LENGTH_START', 'LENGTH_END', 'WIDTH_START', 'WIDTH_END'). Open to
    the edge, the flat side sits on it and ``center`` / the offset along
    that edge place it; otherwise it is placed like a rectangle cutout
    (centred on the face, or at the two offsets). Returns None when the
    arch doesn't fit."""
    along_x = flat_side in ('WIDTH_START', 'WIDTH_END')
    rise = min(rise, chord / 2.0)
    ex, ey = (chord, rise) if along_x else (rise, chord)
    ex, ey = min(ex, length), min(ey, width)
    if ex <= 0.0 or ey <= 0.0:
        return None
    if center:
        x0, y0 = (length - ex) / 2.0, (width - ey) / 2.0
    else:
        x0, y0 = offset_length, offset_width
    if open_edge:
        if flat_side == 'LENGTH_START':
            x0 = 0.0
        elif flat_side == 'LENGTH_END':
            x0 = length - ex
        elif flat_side == 'WIDTH_START':
            y0 = 0.0
        else:
            y0 = width - ey
    x0 = min(max(x0, 0.0), length - ex)
    y0 = min(max(y0, 0.0), width - ey)
    return x0, x0 + ex, y0, y0 + ey


def circle_rect(length, width, diameter, center, offset_length,
                offset_width):
    """The square (x0, x1, y0, y1) bounding a full circle of ``diameter``
    on a part face, placed like a rectangle cutout and kept on the face.
    None when it does not fit."""
    d = min(diameter, length, width)
    if d <= 0.0:
        return None
    if center:
        x0, y0 = (length - d) / 2.0, (width - d) / 2.0
    else:
        x0, y0 = offset_length, offset_width
    x0 = min(max(x0, 0.0), length - d)
    y0 = min(max(y0, 0.0), width - d)
    return x0, x0 + d, y0, y0 + d


FLAT_SIDE_INDEX = {'LENGTH_START': 0, 'LENGTH_END': 1,
                   'WIDTH_START': 2, 'WIDTH_END': 3}
FLAT_SIDE_BY_INDEX = {v: k for k, v in FLAT_SIDE_INDEX.items()}
