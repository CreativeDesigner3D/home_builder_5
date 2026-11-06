"""The room's existing baseboard, drawn along its walls.

The room settings say whether the room has a baseboard and how big it
is (``scene.home_builder.base_board`` and its sizes). Add Baseboard puts
that baseboard on every wall of the room: a strip on the room face of
each wall (local Y = 0, running toward -Y) from the floor up, broken at
entry doors that reach the floor. A double notch adds the quarter round
in front of it. Products that stand against the wall read the same
sizes to clear it -- a closet notches its partitions and holds its
bottom shelf off the wall -- whether or not the strips are drawn.

The strips are plain meshes parented to their wall and rebuilt from
scratch whenever the sizes change, so nothing about them has to be kept
in step by hand.
"""

import math

import bpy
import bmesh
from mathutils import Vector

from .. import hb_types

TAG = 'IS_WALL_BASEBOARD'
MATERIAL_NAME = 'Baseboard'
MATERIAL_COLOR = (0.92, 0.91, 0.88, 1.0)
NOTCHED = ('SINGLE_NOTCH', 'DOUBLE_NOTCH')


# A curved wall's baseboard: a piece per this much of its arc
ARC_STEP = math.radians(3.0)


def baseboard_profile(scene):
    """[(height, depth)] of the strips the room's baseboard is drawn
    with, back to front: the baseboard, then the quarter round standing
    in front of it for a double notch. Empty when the room has none to
    draw or its sizes are unset."""
    hb = scene.home_builder
    if hb.base_board not in NOTCHED:
        return []
    out = []
    if hb.base_board_height_1 > 0.0 and hb.base_board_width_1 > 0.0:
        out.append((hb.base_board_height_1, hb.base_board_width_1))
        if (hb.base_board == 'DOUBLE_NOTCH'
                and hb.base_board_height_2 > 0.0
                and hb.base_board_width_2 > 0.0):
            out.append((hb.base_board_height_2, hb.base_board_width_2))
    return out


def _material():
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if mat is None:
        mat = bpy.data.materials.new(MATERIAL_NAME)
        mat.use_nodes = True
        mat.diffuse_color = MATERIAL_COLOR
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = MATERIAL_COLOR
    return mat


def _wall_length(wall_obj):
    try:
        return float(hb_types.GeoNodeWall(wall_obj).get_input('Length'))
    except Exception:
        return 0.0


def _door_spans(wall_obj, height):
    """(x0, x1) along the wall of the entry doors that reach down into
    the baseboard: the strip stops at each one."""
    spans = []
    for child in wall_obj.children:
        if not child.get('IS_ENTRY_DOOR_BP'):
            continue
        if child.location.z >= height:
            continue
        try:
            w = float(hb_types.GeoNodeCage(child).get_input('Dim X'))
        except Exception:
            continue
        if hb_types.is_curved_wall(wall_obj):
            # A door stands square to the arc: its span is the stations
            # its two sides stand over
            from . import walls as hb_walls
            m = child.matrix_world
            x0 = hb_walls.curved_wall_station(wall_obj, m @ Vector((0.0, 0.0, 0.0)))[0]
            x1 = hb_walls.curved_wall_station(wall_obj, m @ Vector((w, 0.0, 0.0)))[0]
            spans.append((min(x0, x1), max(x0, x1)))
            continue
        spans.append((child.location.x, child.location.x + w))
    return sorted(spans)


def _runs(length, spans):
    """The stretches of [0, length] left between the door spans."""
    runs = []
    x = 0.0
    for x0, x1 in spans:
        if x0 > x + 1e-4:
            runs.append((x, min(x0, length)))
        x = max(x, x1)
    if length > x + 1e-4:
        runs.append((x, length))
    return runs


def _strip_mesh(name, runs, height, depth, arc=0.0, length=0.0, y_offset=0.0):
    """One mesh holding a strip per run, on the wall's room face. On a
    curved wall (`arc`, over the wall's `length`) each run is cut into
    pieces of at most ARC_STEP and bent onto the arc; `y_offset` is where
    the object stands off the wall, so the bend is taken from the face."""
    from .. import hb_wall_graph
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    curved = abs(arc) > 1e-5 and length > 0.0
    for x0, x1 in runs:
        n = 1
        if curved:
            n = max(1, math.ceil(abs(arc) * (x1 - x0) / length / ARC_STEP))
        rings = []
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            ring = []
            for y, z in ((0.0, 0.0), (-depth, 0.0), (-depth, height), (0.0, height)):
                if curved:
                    bx, by = hb_wall_graph.bend(x, y + y_offset, length, arc)
                    ring.append(bm.verts.new((bx, by - y_offset, z)))
                else:
                    ring.append(bm.verts.new((x, y, z)))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((a[i], a[j], b[j], b[i]))
        bm.faces.new(rings[0])
        bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return me


def room_walls(scene):
    return [o for o in scene.objects if o.get('IS_WALL_BP')]


def has_baseboards(scene):
    return any(o.get(TAG) for o in scene.objects)


def remove_baseboards(scene):
    for obj in [o for o in scene.objects if o.get(TAG)]:
        me = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def build_baseboards(scene):
    """(Re)draw the room's baseboard along every wall. Returns how many
    walls got one."""
    remove_baseboards(scene)
    profile = baseboard_profile(scene)
    if not profile:
        return 0
    mat = _material()
    count = 0
    for wall_obj in room_walls(scene):
        length = _wall_length(wall_obj)
        if length <= 0.0:
            continue
        # Each strip runs one depth past the wall end, so the strips of
        # two walls meeting at a corner close it.
        depth_back = 0.0
        made = False
        for i, (height, depth) in enumerate(profile):
            total = depth_back + depth
            runs = _runs(length + total, _door_spans(wall_obj, height))
            if not runs:
                continue
            name = "Baseboard" if i == 0 else "Quarter Round"
            me = _strip_mesh(name, runs, height, depth,
                             hb_types.wall_arc_angle(wall_obj), length, -depth_back)
            me.materials.append(mat)
            obj = bpy.data.objects.new(name, me)
            obj[TAG] = True
            scene.collection.objects.link(obj)
            obj.parent = wall_obj
            obj.matrix_parent_inverse.identity()
            obj.location = (0.0, -depth_back, 0.0)
            depth_back = total
            made = True
        count += made
    return count


def refresh(scene):
    """Keep drawn baseboards matching the room's sizes: a room that has
    them gets them redrawn, one that does not is left alone."""
    if has_baseboards(scene):
        build_baseboards(scene)


class home_builder_OT_add_wall_baseboard(bpy.types.Operator):
    """Draw the room's baseboard along every wall (from Room Information's baseboard sizes)"""
    bl_idname = "home_builder.add_wall_baseboard"
    bl_label = "Add Baseboard"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not baseboard_profile(context.scene):
            self.report({'WARNING'}, "Set the baseboard to Single or "
                        "Double Notch with its height and width first")
            return {'CANCELLED'}
        n = build_baseboards(context.scene)
        self.report({'INFO'}, f"Baseboard added to {n} wall(s)")
        return {'FINISHED'}


class home_builder_OT_remove_wall_baseboard(bpy.types.Operator):
    """Take the drawn baseboard off every wall"""
    bl_idname = "home_builder.remove_wall_baseboard"
    bl_label = "Remove Baseboard"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_baseboards(context.scene)
        return {'FINISHED'}


classes = (
    home_builder_OT_add_wall_baseboard,
    home_builder_OT_remove_wall_baseboard,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
