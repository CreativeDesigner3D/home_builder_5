"""Countertop generation for face frame base cabinets.

Mirrors the frameless library's countertop pipeline but operates on
face frame cabinets (IS_FACE_FRAME_CABINET_CAGE markers) and reads
corner depths from the face_frame_cabinet PropertyGroup rather than
custom object properties.

Three entry points:
  hb_face_frame.add_countertops(selected_only=True/False)
  hb_face_frame.remove_countertops
  hb_face_frame.countertop_boolean_cut

Created countertops carry IS_COUNTERTOP=True so they can be removed
or modified by either library's tooling.
"""

import bpy
import bmesh
import math
from .... import hb_types, hb_project, units
from .. import types_face_frame
from . import ops_placement as ff_ops_placement


def _is_corner_face_frame(obj):
    """Face frame corner cabinets store corner_type on the property group
    rather than as an object-level marker like frameless does.
    """
    ff = getattr(obj, 'face_frame_cabinet', None)
    if ff is None:
        return False
    return getattr(ff, 'corner_type', 'NONE') != 'NONE'


def get_cabinet_depth(cab_obj):
    """Effective depth for countertop sizing.

    Corner cabinets prefer their per-side depths (left_depth / right_depth)
    when set; everything else uses the cage's Dim Y.
    """
    cage = hb_types.GeoNodeCage(cab_obj)
    if _is_corner_face_frame(cab_obj):
        ff = cab_obj.face_frame_cabinet
        ld = getattr(ff, 'left_depth', 0)
        rd = getattr(ff, 'right_depth', 0)
        if ld or rd:
            return max(ld, rd)
    return cage.get_input('Dim Y')


def get_cabinet_x_range(cab_obj):
    """Wall-local (x_start, x_end) for the cabinet, accounting for the
    180-degree rotation back-side cabinets get (their X origin is at the
    geometric right edge, with geometry extending in -X).
    """
    cage = hb_types.GeoNodeCage(cab_obj)
    dim_x = cage.get_input('Dim X')
    is_back = (abs(cab_obj.rotation_euler.z - math.pi) < 0.1
               or abs(cab_obj.rotation_euler.z + math.pi) < 0.1)
    if is_back:
        return (cab_obj.location.x - dim_x, cab_obj.location.x)
    return (cab_obj.location.x, cab_obj.location.x + dim_x)


def split_cabinets_at_ranges(wall_obj, cabinets):
    """Slice a wall's base-cabinet list into sub-runs at any range.

    A single countertop should not span over a range, so the cabinet list
    gets fragmented at every (front-side) range that sits between two
    cabinets. Returns a list of cabinet sub-groups.
    """
    if not cabinets:
        return []

    ranges = []
    for obj in wall_obj.children:
        if obj.get('IS_APPLIANCE') and obj.get('APPLIANCE_TYPE') == 'RANGE':
            cage = hb_types.GeoNodeCage(obj)
            r_start = obj.location.x
            r_end = r_start + cage.get_input('Dim X')
            ranges.append((r_start, r_end))

    if not ranges:
        return [cabinets]

    ranges.sort(key=lambda r: r[0])
    cabinets_sorted = sorted(cabinets, key=lambda c: get_cabinet_x_range(c)[0])

    groups = []
    current_group = []

    for cab in cabinets_sorted:
        cab_start, cab_end = get_cabinet_x_range(cab)
        cab_mid = (cab_start + cab_end) / 2

        overlaps_range = any(r_start <= cab_mid <= r_end for r_start, r_end in ranges)
        if overlaps_range:
            continue

        if current_group:
            prev_start, prev_end = get_cabinet_x_range(current_group[-1])
            for r_start, r_end in ranges:
                if r_start >= prev_end - 0.01 and r_end <= cab_start + 0.01:
                    groups.append(current_group)
                    current_group = []
                    break

        current_group.append(cab)

    if current_group:
        groups.append(current_group)

    return groups


def gather_base_cabinets(context, selected_only=False):
    """Collect face frame base cabinets, grouped by wall+side or as islands.

    Returns (wall_cabinets, island_cabinets) where wall_cabinets is keyed
    by (wall_obj, is_back_side) so front and back-side cabinets on the
    same wall are independent runs. (No cage-group concept yet for face
    frame; that path can be added when face frame produces IS_CAGE_GROUP
    objects.)
    """
    wall_cabinets = {}
    island_cabinets = []

    selected_cabs = set()
    if selected_only:
        for obj in context.selected_objects:
            cur = obj
            while cur is not None:
                if (cur.get(types_face_frame.TAG_CABINET_CAGE)
                        and cur.get('CABINET_TYPE') == 'BASE'):
                    selected_cabs.add(cur)
                    break
                cur = cur.parent

    for obj in context.scene.objects:
        if not obj.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        if obj.get('CABINET_TYPE') != 'BASE':
            continue
        if selected_only and obj not in selected_cabs:
            continue

        if obj.parent and obj.parent.get('IS_WALL_BP'):
            wall = obj.parent
            is_back = (abs(obj.rotation_euler.z - math.pi) < 0.1
                       or abs(obj.rotation_euler.z + math.pi) < 0.1)
            wall_cabinets.setdefault((wall, is_back), []).append(obj)
        else:
            island_cabinets.append(obj)

    return wall_cabinets, island_cabinets


def build_wall_runs(wall_cabinets):
    """Chain connected walls into runs.

    Result is a list of runs; each run is a list of (wall_obj, cabinets)
    tuples in left-to-right wall order. Front and back sides on the same
    wall are kept as separate runs because back-side cabinets have their
    own face-direction and rotation.
    """
    if not wall_cabinets:
        return []

    used = set()
    runs = []

    for wall_key in wall_cabinets:
        if wall_key in used:
            continue

        wall_obj, is_back = wall_key
        run_start = wall_obj
        wall = hb_types.GeoNodeWall(run_start)
        while True:
            left = wall.get_connected_wall('left')
            if (left and (left.obj, is_back) in wall_cabinets
                    and (left.obj, is_back) not in used):
                run_start = left.obj
                wall = left
            else:
                break

        run = []
        current = run_start
        while (current and (current, is_back) in wall_cabinets
               and (current, is_back) not in used):
            used.add((current, is_back))
            run.append((current, wall_cabinets[(current, is_back)]))
            wall = hb_types.GeoNodeWall(current)
            right = wall.get_connected_wall('right')
            if right and (right.obj, is_back) in wall_cabinets:
                current = right.obj
            else:
                break

        if run:
            runs.append(run)

    return runs


def find_adjacent_tall_cabinets(wall_obj, cabinets):
    """Detect tall cabinets butting up against the run's outer ends.

    The outer end of a run that meets a tall cabinet shouldn't get a
    side overhang (the tall cabinet would block it). Returns
    (tall_at_left, tall_at_right) booleans.
    """
    if not cabinets:
        return False, False

    cabinets_sorted = sorted(cabinets, key=lambda c: c.location.x)
    first_cab = cabinets_sorted[0]
    last_cab = cabinets_sorted[-1]
    last_cage = hb_types.GeoNodeCage(last_cab)
    run_left = first_cab.location.x
    run_right = last_cab.location.x + last_cage.get_input('Dim X')

    tall_at_left = False
    tall_at_right = False
    tolerance = 0.005

    for child in wall_obj.children:
        if not child.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        if child.get('CABINET_TYPE') != 'TALL':
            continue
        cage = hb_types.GeoNodeCage(child)
        tall_left = child.location.x
        tall_right = child.location.x + cage.get_input('Dim X')

        if abs(tall_right - run_left) < tolerance:
            tall_at_left = True
        if abs(tall_left - run_right) < tolerance:
            tall_at_right = True

    return tall_at_left, tall_at_right


def create_wall_countertop(context, wall_obj, cabinets, has_left_conn, has_right_conn):
    """Build a countertop mesh for a contiguous run of base cabinets on
    one wall. Connected ends and adjacent tall cabinets suppress side
    overhang; corner cabinets at run ends produce an L-shape that
    extends into the perpendicular wall.
    """
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_face_frame

    overhang_front = props.countertop_overhang_front
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

    first_cab_raw = cabinets[0]
    is_back_side = (abs(first_cab_raw.rotation_euler.z - math.pi) < 0.1
                    or abs(first_cab_raw.rotation_euler.z + math.pi) < 0.1)

    if is_back_side:
        x_ranges = []
        for cab in cabinets:
            cage = hb_types.GeoNodeCage(cab)
            dim_x = cage.get_input('Dim X')
            x_ranges.append((cab.location.x - dim_x, cab.location.x))
        x_ranges.sort(key=lambda r: r[0])
        start_x = x_ranges[0][0]
        end_x = x_ranges[-1][1]
    else:
        cabinets.sort(key=lambda c: c.location.x)
        first_cab = cabinets[0]
        last_cab = cabinets[-1]
        last_cage = hb_types.GeoNodeCage(last_cab)
        start_x = first_cab.location.x
        end_x = last_cab.location.x + last_cage.get_input('Dim X')

    std_depths = [get_cabinet_depth(c) for c in cabinets if not _is_corner_face_frame(c)]
    if not std_depths:
        std_depths = [get_cabinet_depth(c) for c in cabinets]
    std_depth = max(std_depths) if std_depths else 0.6

    first_cage = hb_types.GeoNodeCage(cabinets[0])
    cab_height = first_cage.get_input('Dim Z')

    z_bot = cab_height
    z_top = cab_height + thickness

    tall_at_left, tall_at_right = find_adjacent_tall_cabinets(wall_obj, cabinets)
    suppress_left = has_left_conn or tall_at_left
    suppress_right = has_right_conn or tall_at_right

    cabinets_sorted = sorted(cabinets, key=lambda c: c.location.x)
    left_corner = cabinets_sorted[0] if _is_corner_face_frame(cabinets_sorted[0]) else None
    right_corner = cabinets_sorted[-1] if _is_corner_face_frame(cabinets_sorted[-1]) else None

    if is_back_side:
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_thickness = wall_node.get_input('Thickness')
        std_back_y = wall_thickness - overhang_back
        std_front_y = wall_thickness + std_depth + overhang_front
    else:
        std_front_y = -(std_depth + overhang_front)
        std_back_y = overhang_back

    sx = start_x - (overhang_sides if not suppress_left else 0)
    ex = end_x + (overhang_sides if not suppress_right else 0)

    has_l_shape = (left_corner or right_corner) and not is_back_side

    if not has_l_shape:
        verts = [
            (sx, std_back_y,  z_bot),
            (sx, std_front_y, z_bot),
            (ex, std_front_y, z_bot),
            (ex, std_back_y,  z_bot),
            (sx, std_back_y,  z_top),
            (sx, std_front_y, z_top),
            (ex, std_front_y, z_top),
            (ex, std_back_y,  z_top),
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (2, 6, 7, 3),
            (1, 5, 6, 2),
            (0, 3, 7, 4),
        ]
    elif left_corner:
        # L-shape extending into left perpendicular wall. Transition X
        # is at left_depth + front overhang so the step face is exposed.
        ff = left_corner.face_frame_cabinet
        corner_cage = hb_types.GeoNodeCage(left_corner)
        corner_dim_y = corner_cage.get_input('Dim Y')
        corner_left_depth = getattr(ff, 'left_depth', 0) or corner_dim_y

        corner_transition_x = start_x + corner_left_depth + overhang_front
        corner_depth = corner_dim_y
        if has_left_conn:
            adj_wall_node = hb_types.GeoNodeWall(wall_obj)
            adj_wall = adj_wall_node.get_connected_wall('left')
            if adj_wall:
                adj_length = adj_wall.get_input('Length')
                for child in adj_wall.obj.children:
                    if (child.get(types_face_frame.TAG_CABINET_CAGE)
                            and child.get('CABINET_TYPE') == 'BASE'
                            and not _is_corner_face_frame(child)):
                        cage_child = hb_types.GeoNodeCage(child)
                        cab_end = child.location.x + cage_child.get_input('Dim X')
                        dist_from_corner = adj_length - cab_end
                        if dist_from_corner <= corner_depth + 0.01:
                            corner_depth = max(corner_depth, adj_length - child.location.x)

        corner_front_y = -(corner_depth + overhang_front)
        verts = [
            (sx,                  std_back_y,     z_bot),
            (sx,                  corner_front_y, z_bot),
            (corner_transition_x, corner_front_y, z_bot),
            (corner_transition_x, std_front_y,    z_bot),
            (ex,                  std_front_y,    z_bot),
            (ex,                  std_back_y,     z_bot),
            (sx,                  std_back_y,     z_top),
            (sx,                  corner_front_y, z_top),
            (corner_transition_x, corner_front_y, z_top),
            (corner_transition_x, std_front_y,    z_top),
            (ex,                  std_front_y,    z_top),
            (ex,                  std_back_y,     z_top),
        ]
        faces = [
            (0, 1, 2, 3, 4, 5),
            (6, 11, 10, 9, 8, 7),
            (0, 6, 7, 1),
            (1, 7, 8, 2),
            (2, 8, 9, 3),
            (3, 9, 10, 4),
            (4, 10, 11, 5),
            (5, 11, 6, 0),
        ]
    else:  # right_corner
        ff = right_corner.face_frame_cabinet
        corner_cage = hb_types.GeoNodeCage(right_corner)
        corner_dim_y = corner_cage.get_input('Dim Y')
        corner_right_depth = getattr(ff, 'right_depth', 0) or corner_dim_y

        corner_transition_x = end_x - corner_right_depth - overhang_front
        corner_depth = corner_dim_y
        if has_right_conn:
            adj_wall_node = hb_types.GeoNodeWall(wall_obj)
            adj_wall = adj_wall_node.get_connected_wall('right')
            if adj_wall:
                for child in adj_wall.obj.children:
                    if (child.get(types_face_frame.TAG_CABINET_CAGE)
                            and child.get('CABINET_TYPE') == 'BASE'
                            and not _is_corner_face_frame(child)):
                        cage_child = hb_types.GeoNodeCage(child)
                        cab_end = child.location.x + cage_child.get_input('Dim X')
                        if cab_end <= corner_depth + 0.01:
                            corner_depth = max(corner_depth, cab_end)

        corner_front_y = -(corner_depth + overhang_front)
        verts = [
            (sx,                  std_back_y,     z_bot),
            (sx,                  std_front_y,    z_bot),
            (corner_transition_x, std_front_y,    z_bot),
            (corner_transition_x, corner_front_y, z_bot),
            (ex,                  corner_front_y, z_bot),
            (ex,                  std_back_y,     z_bot),
            (sx,                  std_back_y,     z_top),
            (sx,                  std_front_y,    z_top),
            (corner_transition_x, std_front_y,    z_top),
            (corner_transition_x, corner_front_y, z_top),
            (ex,                  corner_front_y, z_top),
            (ex,                  std_back_y,     z_top),
        ]
        faces = [
            (0, 1, 2, 3, 4, 5),
            (6, 11, 10, 9, 8, 7),
            (0, 6, 7, 1),
            (1, 7, 8, 2),
            (2, 8, 9, 3),
            (3, 9, 10, 4),
            (4, 10, 11, 5),
            (5, 11, 6, 0),
        ]

    mesh = bpy.data.meshes.new('Countertop')
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new('Countertop', mesh)
    obj.parent = wall_obj
    obj['IS_COUNTERTOP'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_cabinet_commands'
    context.scene.collection.objects.link(obj)
    return obj


def create_island_countertop(context, cab_obj):
    """Single-cabinet island countertop. Sized to the cage with overhang
    on all sides.
    """
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_face_frame

    overhang_front = props.countertop_overhang_front
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

    cage = hb_types.GeoNodeCage(cab_obj)
    dim_x = cage.get_input('Dim X')
    dim_y = cage.get_input('Dim Y')
    dim_z = cage.get_input('Dim Z')

    start_x = -overhang_sides
    end_x = dim_x + overhang_sides
    front_y = -(dim_y + overhang_front)
    back_y = overhang_back
    z_bot = dim_z
    z_top = dim_z + thickness

    verts = [
        (start_x, back_y,  z_bot),
        (start_x, front_y, z_bot),
        (end_x,   front_y, z_bot),
        (end_x,   back_y,  z_bot),
        (start_x, back_y,  z_top),
        (start_x, front_y, z_top),
        (end_x,   front_y, z_top),
        (end_x,   back_y,  z_top),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (2, 6, 7, 3),
        (1, 5, 6, 2),
        (0, 3, 7, 4),
    ]

    mesh = bpy.data.meshes.new('Countertop')
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new('Countertop', mesh)
    obj.parent = cab_obj
    obj['IS_COUNTERTOP'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_cabinet_commands'
    context.scene.collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class hb_face_frame_OT_add_countertops(bpy.types.Operator):
    bl_idname = "hb_face_frame.add_countertops"
    bl_label = "Add Countertops"
    bl_description = "Add countertops to face frame base cabinets"
    bl_options = {'REGISTER', 'UNDO'}

    selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Only add countertops to selected face frame cabinets",
        default=False,
    )  # type: ignore

    def execute(self, context):
        wall_cabinets, island_cabinets = gather_base_cabinets(context, self.selected_only)

        if not wall_cabinets and not island_cabinets:
            if self.selected_only:
                self.report({'WARNING'}, "No face frame base cabinets selected")
            else:
                self.report({'WARNING'}, "No face frame base cabinets found")
            return {'CANCELLED'}

        # Adding to all replaces existing countertops; adding to selected
        # leaves untouched runs alone.
        if not self.selected_only:
            for obj in [o for o in context.scene.objects if o.get('IS_COUNTERTOP')]:
                bpy.data.objects.remove(obj, do_unlink=True)

        runs = build_wall_runs(wall_cabinets)
        ct_count = 0

        for run in runs:
            for i, (wall_obj, cabinets) in enumerate(run):
                has_left = i > 0
                has_right = i < len(run) - 1
                sub_groups = split_cabinets_at_ranges(wall_obj, cabinets)
                for gi, group in enumerate(sub_groups):
                    left_conn = has_left if gi == 0 else True
                    right_conn = has_right if gi == len(sub_groups) - 1 else True
                    ct = create_wall_countertop(
                        context, wall_obj, group, left_conn, right_conn)
                    if ct:
                        ct_count += 1

        for cab_obj in island_cabinets:
            ct = create_island_countertop(context, cab_obj)
            if ct:
                ct_count += 1

        self.report({'INFO'}, f"Created {ct_count} countertop(s)")
        return {'FINISHED'}


class hb_face_frame_OT_remove_countertops(bpy.types.Operator):
    bl_idname = "hb_face_frame.remove_countertops"
    bl_label = "Remove Countertops"
    bl_description = "Remove all countertops from the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removed = 0
        for obj in list(context.scene.objects):
            if obj.get('IS_COUNTERTOP'):
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
        self.report({'INFO'}, f"Removed {removed} countertop(s)")
        return {'FINISHED'}


class hb_face_frame_OT_countertop_boolean_cut(bpy.types.Operator):
    bl_idname = "hb_face_frame.countertop_boolean_cut"
    bl_label = "Cut Countertop"
    bl_description = (
        "Cut a hole in the active countertop using another selected mesh "
        "as the cutter (e.g. a sink stand-in). Select cutter then countertop."
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sel = [o for o in context.selected_objects if o.type == 'MESH']
        return len(sel) == 2

    def execute(self, context):
        sel = [o for o in context.selected_objects if o.type == 'MESH']
        if len(sel) != 2:
            self.report({'WARNING'}, "Select exactly two meshes (cutter + countertop)")
            return {'CANCELLED'}

        active = context.view_layer.objects.active
        if active is None or active not in sel:
            self.report({'WARNING'}, "Active object must be one of the two selected meshes")
            return {'CANCELLED'}

        countertop = active
        cutter = sel[0] if sel[1] is active else sel[1]

        mod = countertop.modifiers.new(name="CountertopCut", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        mod.solver = 'EXACT'

        # Apply immediately so the cut is permanent and the cutter can be
        # deleted without losing the result.
        prev_active = context.view_layer.objects.active
        context.view_layer.objects.active = countertop
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError as e:
            self.report({'WARNING'}, f"Boolean apply failed: {e}")
            countertop.modifiers.remove(mod)
            return {'CANCELLED'}
        finally:
            context.view_layer.objects.active = prev_active

        return {'FINISHED'}


classes = (
    hb_face_frame_OT_add_countertops,
    hb_face_frame_OT_remove_countertops,
    hb_face_frame_OT_countertop_boolean_cut,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
