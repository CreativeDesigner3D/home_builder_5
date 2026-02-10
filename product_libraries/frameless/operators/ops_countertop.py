import bpy
import bmesh
import math
import mathutils
from .... import hb_types, hb_project, units


def get_cabinet_depth(cab_obj):
    """Get the effective depth of a cabinet for countertop purposes."""
    cage = hb_types.GeoNodeCage(cab_obj)
    if cab_obj.get('IS_CORNER_CABINET'):
        left_d = cab_obj.get('Left Depth', 0)
        right_d = cab_obj.get('Right Depth', 0)
        return max(left_d, right_d) if (left_d or right_d) else cage.get_input('Dim Y')
    return cage.get_input('Dim Y')


def gather_base_cabinets(context):
    """Collect base cabinets grouped by wall, plus islands."""
    wall_cabinets = {}
    island_cabinets = []

    for obj in context.scene.objects:
        if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
            continue
        if obj.get('CABINET_TYPE') != 'BASE':
            continue

        if obj.parent and obj.parent.get('IS_WALL_BP'):
            wall = obj.parent
            if wall not in wall_cabinets:
                wall_cabinets[wall] = []
            wall_cabinets[wall].append(obj)
        else:
            island_cabinets.append(obj)

    return wall_cabinets, island_cabinets


def build_wall_runs(wall_cabinets):
    """Group connected walls into runs (ordered lists of walls).
    Returns list of runs, where each run is a list of (wall_obj, cabinets) tuples."""
    if not wall_cabinets:
        return []

    used = set()
    runs = []

    for wall_obj in wall_cabinets:
        if wall_obj in used:
            continue

        run_start = wall_obj
        wall = hb_types.GeoNodeWall(run_start)
        while True:
            left = wall.get_connected_wall('left')
            if left and left.obj in wall_cabinets and left.obj not in used:
                run_start = left.obj
                wall = left
            else:
                break

        run = []
        current = run_start
        while current and current in wall_cabinets and current not in used:
            used.add(current)
            run.append((current, wall_cabinets[current]))
            wall = hb_types.GeoNodeWall(current)
            right = wall.get_connected_wall('right')
            if right and right.obj in wall_cabinets:
                current = right.obj
            else:
                break

        if run:
            runs.append(run)

    return runs


def get_wall_direction(wall_obj):
    """Get the normalized direction vector of a wall in world space."""
    angle = wall_obj.rotation_euler.z
    return mathutils.Vector((math.cos(angle), math.sin(angle), 0))


def get_wall_normal(wall_obj):
    """Get the outward-facing normal of a wall (toward room / -Y local)."""
    angle = wall_obj.rotation_euler.z
    # -Y local in world space
    return mathutils.Vector((math.sin(angle), -math.cos(angle), 0))


def create_rect_slab(wall_obj, cabinets, overhang_front, overhang_back, overhang_sides, 
                     thickness, has_left_conn, has_right_conn):
    """Create a rectangular countertop mesh in wall-local space.
    At connected ends, extend past cabinets by the full slab depth so the 
    bisect cut can create the miter."""
    cabinets.sort(key=lambda c: c.location.x)

    first_cab = cabinets[0]
    last_cab = cabinets[-1]
    last_cage = hb_types.GeoNodeCage(last_cab)

    start_x = first_cab.location.x
    end_x = last_cab.location.x + last_cage.get_input('Dim X')

    depths = [get_cabinet_depth(c) for c in cabinets]
    max_depth = max(depths) if depths else 0.6

    first_cage = hb_types.GeoNodeCage(first_cab)
    cab_height = first_cage.get_input('Dim Z')

    front_y = -(max_depth + overhang_front)
    back_y = overhang_back
    counter_depth = abs(front_y - back_y)

    z_bot = cab_height
    z_top = cab_height + thickness

    # At connected ends, extend by counter_depth to create overlap for miter cut
    if has_left_conn:
        start_x -= counter_depth
    else:
        start_x -= overhang_sides

    if has_right_conn:
        end_x += counter_depth
    else:
        end_x += overhang_sides

    verts = [
        (start_x, back_y,  z_bot),  # 0 back-left bottom
        (start_x, front_y, z_bot),  # 1 front-left bottom
        (end_x,   front_y, z_bot),  # 2 front-right bottom
        (end_x,   back_y,  z_bot),  # 3 back-right bottom
        (start_x, back_y,  z_top),  # 4 back-left top
        (start_x, front_y, z_top),  # 5 front-left top
        (end_x,   front_y, z_top),  # 6 front-right top
        (end_x,   back_y,  z_top),  # 7 back-right top
    ]

    faces = [
        (0, 1, 2, 3),  # bottom
        (4, 7, 6, 5),  # top
        (0, 4, 5, 1),  # left
        (2, 6, 7, 3),  # right
        (1, 5, 6, 2),  # front
        (0, 3, 7, 4),  # back
    ]

    mesh = bpy.data.meshes.new('Countertop')
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new('Countertop', mesh)
    obj.parent = wall_obj
    obj['IS_COUNTERTOP'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
    bpy.context.scene.collection.objects.link(obj)

    return obj


def miter_cut(ct_obj, plane_co, plane_no, keep_side_point):
    """Bisect countertop mesh with a plane, keeping the side that contains keep_side_point."""
    bm = bmesh.new()
    bm.from_mesh(ct_obj.data)

    # Transform plane to object-local space
    mat_inv = ct_obj.matrix_world.inverted()
    local_co = mat_inv @ plane_co
    # Normal needs rotation only (no translation)
    local_no = (mat_inv.to_3x3() @ plane_no).normalized()

    # Determine which side to keep: check which side the keep_side_point is on
    local_keep = mat_inv @ keep_side_point
    dot = (local_keep - local_co).dot(local_no)
    
    if dot >= 0:
        # Keep point is on positive side (normal direction), clear negative side
        co = False
        ci = True
    else:
        # Keep point is on negative side, clear positive side
        co = True
        ci = False
    
    bmesh.ops.bisect_plane(
        bm,
        geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=local_co,
        plane_no=local_no,
        clear_outer=co,
        clear_inner=ci,
    )

    # Fill the cut face
    edges_on_cut = [e for e in bm.edges if e.is_boundary]
    if edges_on_cut:
        bmesh.ops.contextual_create(bm, geom=edges_on_cut)

    bm.to_mesh(ct_obj.data)
    ct_obj.data.update()
    bm.free()


def compute_miter_plane(wall_a_obj, wall_b_obj):
    """Compute a miter plane between two connected walls.
    Returns (plane_point, plane_normal) in world space.
    The plane bisects the angle between the two walls."""
    wall_a = hb_types.GeoNodeWall(wall_a_obj)
    
    # Corner point is at wall_a's obj_x (end point) in world space
    corner = wall_a_obj.matrix_world @ wall_a.obj_x.location

    dir_a = get_wall_direction(wall_a_obj)
    dir_b = get_wall_direction(wall_b_obj)

    # Bisector direction: average of the two wall directions
    bisector = (dir_a + dir_b).normalized()

    # The bisector of wall directions IS the plane normal for the miter cut
    plane_normal = bisector

    return corner, plane_normal


def create_island_countertop(context, cab_obj):
    """Create a countertop for an island (non-wall) cabinet."""
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

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
    obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
    context.scene.collection.objects.link(obj)

    return obj


class hb_frameless_OT_add_countertops(bpy.types.Operator):
    bl_idname = "hb_frameless.add_countertops"
    bl_label = "Add Countertops"
    bl_description = "Add countertops to all base cabinets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wall_cabinets, island_cabinets = gather_base_cabinets(context)

        if not wall_cabinets and not island_cabinets:
            self.report({'WARNING'}, "No base cabinets found")
            return {'CANCELLED'}

        # Remove existing countertops
        existing = [o for o in context.scene.objects if o.get('IS_COUNTERTOP')]
        for obj in existing:
            bpy.data.objects.remove(obj, do_unlink=True)

        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        # Build connected wall runs
        runs = build_wall_runs(wall_cabinets)

        ct_count = 0
        # Store countertop objects with their run info for miter cutting
        run_cts = []  # list of lists: [[( wall_obj, ct_obj ), ...], ...]

        for run in runs:
            run_ct_list = []
            for i, (wall_obj, cabinets) in enumerate(run):
                has_left = i > 0
                has_right = i < len(run) - 1
                ct = create_rect_slab(
                    wall_obj, cabinets,
                    props.countertop_overhang_front,
                    props.countertop_overhang_back,
                    props.countertop_overhang_sides,
                    props.countertop_thickness,
                    has_left, has_right,
                )
                if ct:
                    run_ct_list.append((wall_obj, ct))
                    ct_count += 1
            run_cts.append(run_ct_list)

        # Update scene so matrix_world is current before miter cuts
        context.view_layer.update()

        # Apply miter cuts between adjacent countertops in each run
        for run_idx, run in enumerate(runs):
            run_ct_list = run_cts[run_idx]
            for i in range(len(run) - 1):
                wall_a_obj = run[i][0]
                wall_b_obj = run[i + 1][0]
                ct_a = run_ct_list[i][1]
                ct_b = run_ct_list[i + 1][1]

                plane_co, plane_no = compute_miter_plane(wall_a_obj, wall_b_obj)

                # For ct_a, keep the side toward wall_a's start (away from corner)
                # Use a point in the middle of ct_a's cabinets
                keep_a = wall_a_obj.matrix_world @ mathutils.Vector((0, 0, plane_co.z))
                # For ct_b, keep the side toward wall_b's end (away from corner)
                wall_b = hb_types.GeoNodeWall(wall_b_obj)
                wall_b_length = wall_b.get_input('Length')
                keep_b = wall_b_obj.matrix_world @ mathutils.Vector((wall_b_length, 0, plane_co.z))

                miter_cut(ct_a, plane_co, plane_no, keep_a)
                miter_cut(ct_b, plane_co, plane_no, keep_b)

        # Island countertops
        for cab_obj in island_cabinets:
            ct = create_island_countertop(context, cab_obj)
            if ct:
                ct_count += 1

        self.report({'INFO'}, f"Created {ct_count} countertop(s)")
        return {'FINISHED'}


class hb_frameless_OT_remove_countertops(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_countertops"
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


classes = (
    hb_frameless_OT_add_countertops,
    hb_frameless_OT_remove_countertops,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
