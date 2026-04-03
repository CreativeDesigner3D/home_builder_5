import bpy
import bmesh
import math
from .... import hb_types, hb_project, units


def get_cabinet_depth(cab_obj):
    """Get the effective depth of a cabinet for countertop purposes."""
    cage = hb_types.GeoNodeCage(cab_obj)
    if cab_obj.get('IS_CORNER_CABINET'):
        left_d = cab_obj.get('Left Depth', 0)
        right_d = cab_obj.get('Right Depth', 0)
        return max(left_d, right_d) if (left_d or right_d) else cage.get_input('Dim Y')
    return cage.get_input('Dim Y')


def get_cabinet_x_range(cab_obj):
    """Get the (x_start, x_end) range for a cabinet, handling back-side rotation."""
    cage = hb_types.GeoNodeCage(cab_obj)
    dim_x = cage.get_input('Dim X')
    is_back = (abs(cab_obj.rotation_euler.z - math.pi) < 0.1 or 
               abs(cab_obj.rotation_euler.z + math.pi) < 0.1)
    if is_back:
        return (cab_obj.location.x - dim_x, cab_obj.location.x)
    else:
        return (cab_obj.location.x, cab_obj.location.x + dim_x)


def split_cabinets_at_ranges(wall_obj, cabinets):
    """Split a wall's cabinet list into sub-groups separated by ranges.
    Returns a list of cabinet sub-groups that should each get their own countertop."""
    if not cabinets:
        return []

    # Find ranges on this wall
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

        # Check if this cabinet overlaps with any range
        overlaps_range = False
        for r_start, r_end in ranges:
            if cab_mid >= r_start and cab_mid <= r_end:
                overlaps_range = True
                break

        if not overlaps_range:
            # Check if a range sits between this cabinet and the previous one
            if current_group:
                prev_start, prev_end = get_cabinet_x_range(current_group[-1])
                for r_start, r_end in ranges:
                    if r_start >= prev_end - 0.01 and r_end <= cab_start + 0.01:
                        # Range is between previous and current cabinet - split here
                        groups.append(current_group)
                        current_group = []
                        break

            current_group.append(cab)

    if current_group:
        groups.append(current_group)

    return groups


def gather_base_cabinets(context, selected_only=False):
    """Collect base cabinets grouped by wall, cage groups, and lone islands.
    If selected_only is True, only include cabinets that are currently selected."""
    wall_cabinets = {}
    cage_groups = []
    island_cabinets = []

    # Build set of selected cabinet cages for filtering
    selected_cabs = set()
    if selected_only:
        for obj in context.selected_objects:
            if obj.get('IS_FRAMELESS_CABINET_CAGE') and obj.get('CABINET_TYPE') == 'BASE':
                selected_cabs.add(obj)
            # Also check if a child cage is selected (user might select a part)
            if obj.parent and obj.parent.get('IS_FRAMELESS_CABINET_CAGE') and obj.parent.get('CABINET_TYPE') == 'BASE':
                selected_cabs.add(obj.parent)
            # Walk up to find cabinet cage ancestor
            parent = obj.parent
            while parent:
                if parent.get('IS_FRAMELESS_CABINET_CAGE') and parent.get('CABINET_TYPE') == 'BASE':
                    selected_cabs.add(parent)
                    break
                parent = parent.parent

    # Track cabinets that belong to cage groups so we don't double-count
    grouped_cabs = set()

    # Find cage groups first
    for obj in context.scene.objects:
        if obj.get('IS_CAGE_GROUP'):
            countertop_children = [c for c in obj.children 
                                   if (c.get('IS_FRAMELESS_CABINET_CAGE') and c.get('CABINET_TYPE') == 'BASE')
                                   or (c.get('IS_FRAMELESS_PRODUCT_CAGE') and c.get('PART_TYPE') == 'SUPPORT_FRAME')]
            if selected_only:
                countertop_children = [c for c in countertop_children if c in selected_cabs]
            if countertop_children:
                cage_groups.append((obj, countertop_children))
                for c in countertop_children:
                    grouped_cabs.add(c)

    # Now find wall and lone island cabinets
    for obj in context.scene.objects:
        if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
            continue
        if obj.get('CABINET_TYPE') != 'BASE':
            continue
        if obj in grouped_cabs:
            continue
        if selected_only and obj not in selected_cabs:
            continue

        if obj.parent and obj.parent.get('IS_WALL_BP'):
            wall = obj.parent
            # Separate front-side and back-side cabinets on the same wall
            is_back = (abs(obj.rotation_euler.z - math.pi) < 0.1 or 
                       abs(obj.rotation_euler.z + math.pi) < 0.1)
            wall_key = (wall, is_back)
            if wall_key not in wall_cabinets:
                wall_cabinets[wall_key] = []
            wall_cabinets[wall_key].append(obj)
        else:
            island_cabinets.append(obj)

    return wall_cabinets, cage_groups, island_cabinets


def build_wall_runs(wall_cabinets):
    """Group connected walls into runs. Returns list of runs,
    where each run is a list of (wall_obj, cabinets) tuples.
    wall_cabinets is keyed by (wall_obj, is_back) tuples to keep
    front-side and back-side cabinets separate."""
    if not wall_cabinets:
        return []

    used = set()
    runs = []

    for wall_key in wall_cabinets:
        if wall_key in used:
            continue

        wall_obj, is_back = wall_key

        # Trace left to find the start of this run (only following same side)
        run_start = wall_obj
        wall = hb_types.GeoNodeWall(run_start)
        while True:
            left = wall.get_connected_wall('left')
            if left and (left.obj, is_back) in wall_cabinets and (left.obj, is_back) not in used:
                run_start = left.obj
                wall = left
            else:
                break

        # Build the run going right (only following same side)
        run = []
        current = run_start
        while current and (current, is_back) in wall_cabinets and (current, is_back) not in used:
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
    """Check if the first/last base cabinet in a run is adjacent to a tall cabinet.

    Returns:
        (tall_at_left, tall_at_right) - booleans
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
    tolerance = 0.005  # 5mm

    for child in wall_obj.children:
        if not child.get('IS_FRAMELESS_CABINET_CAGE'):
            continue
        if child.get('CABINET_TYPE') != 'TALL':
            continue

        cage = hb_types.GeoNodeCage(child)
        tall_left = child.location.x
        tall_right = child.location.x + cage.get_input('Dim X')

        # Tall right edge touches run left edge
        if abs(tall_right - run_left) < tolerance:
            tall_at_left = True
        # Tall left edge touches run right edge
        if abs(tall_left - run_right) < tolerance:
            tall_at_right = True

    return tall_at_left, tall_at_right


def create_wall_countertop(context, wall_obj, cabinets, has_left_conn, has_right_conn):
    """Create a countertop for cabinets on a single wall.

    Handles:
    - Connected ends (wall-to-wall): no side overhang
    - Adjacent tall cabinets: no side overhang on that end
    - Corner cabinets: L-shaped countertop with deeper section at corner
    - Front-side and back-side cabinet placement
    """
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

    overhang_front = props.countertop_overhang_front
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

    # Detect if cabinets are on the back side of the wall
    first_cab_raw = cabinets[0]
    is_back_side = (abs(first_cab_raw.rotation_euler.z - math.pi) < 0.1 or
                    abs(first_cab_raw.rotation_euler.z + math.pi) < 0.1)

    if is_back_side:
        x_ranges = []
        for cab in cabinets:
            cage = hb_types.GeoNodeCage(cab)
            dim_x = cage.get_input('Dim X')
            x_start = cab.location.x - dim_x
            x_end = cab.location.x
            x_ranges.append((x_start, x_end))
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

    # Standard (non-corner) cabinet depths
    std_depths = [get_cabinet_depth(c) for c in cabinets if not c.get('IS_CORNER_CABINET')]
    if not std_depths:
        std_depths = [get_cabinet_depth(c) for c in cabinets]
    std_depth = max(std_depths) if std_depths else 0.6

    first_cage = hb_types.GeoNodeCage(cabinets[0])
    cab_height = first_cage.get_input('Dim Z')

    z_bot = cab_height
    z_top = cab_height + thickness

    # --- Detect adjacent tall cabinets ---
    tall_at_left, tall_at_right = find_adjacent_tall_cabinets(wall_obj, cabinets)

    # Suppress side overhang when connected to another wall OR adjacent to a tall
    suppress_left = has_left_conn or tall_at_left
    suppress_right = has_right_conn or tall_at_right

    # --- Detect corner cabinets at ends ---
    cabinets_sorted = sorted(cabinets, key=lambda c: c.location.x)
    left_corner = cabinets_sorted[0] if cabinets_sorted[0].get('IS_CORNER_CABINET') else None
    right_corner = cabinets_sorted[-1] if cabinets_sorted[-1].get('IS_CORNER_CABINET') else None

    # --- Build the countertop mesh ---
    if is_back_side:
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_thickness = wall_node.get_input('Thickness')
        std_back_y = wall_thickness - overhang_back
        std_front_y = wall_thickness + std_depth + overhang_front
    else:
        std_front_y = -(std_depth + overhang_front)
        std_back_y = overhang_back

    # Apply side overhang
    sx = start_x - (overhang_sides if not suppress_left else 0)
    ex = end_x + (overhang_sides if not suppress_right else 0)

    # Check if we need an L-shape for corner cabinets
    has_l_shape = False
    if (left_corner or right_corner) and not is_back_side:
        has_l_shape = True

    if not has_l_shape:
        # Simple rectangular countertop
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
    else:
        # L-shaped countertop for corner cabinets
        # Uses Left Depth / Right Depth to determine the L-shape transition
        #
        # Corner cabinet L-shape footprint (top view):
        #   Wing along wall:  x=0 to Dim_X, depth = Right_Depth
        #   Wing into corner: x=0 to Left_Depth, depth = Dim_Y
        #
        # The step happens at Left_Depth (for left corner) or
        # at Dim_X - Right_Depth from end (for right corner)

        if left_corner:
            corner_cage = hb_types.GeoNodeCage(left_corner)
            corner_dim_y = corner_cage.get_input('Dim Y')
            corner_left_depth = left_corner.get('Left Depth', corner_dim_y)

            # Transition at Left Depth + overhang — step face is exposed
            corner_transition_x = start_x + corner_left_depth + overhang_front

            # Deep section depth: use Dim Y for corner cabinet's perpendicular wing
            # Also check if the adjacent wall has base cabinets that the deep section
            # should reach — extend to meet the nearest cabinet's back edge
            corner_depth = corner_dim_y
            if has_left_conn:
                adj_wall_node = hb_types.GeoNodeWall(wall_obj)
                adj_wall = adj_wall_node.get_connected_wall('left')
                if adj_wall:
                    # Find the nearest base cabinet on the adjacent wall to the corner
                    adj_length = adj_wall.get_input('Length')
                    for child in adj_wall.obj.children:
                        if (child.get('IS_FRAMELESS_CABINET_CAGE')
                                and child.get('CABINET_TYPE') == 'BASE'
                                and not child.get('IS_CORNER_CABINET')):
                            cage_child = hb_types.GeoNodeCage(child)
                            cab_end = child.location.x + cage_child.get_input('Dim X')
                            # Distance from corner along adjacent wall
                            dist_from_corner = adj_length - cab_end
                            if dist_from_corner <= corner_depth + 0.01:
                                # Cabinet is within reach of corner wing — extend to meet it
                                corner_depth = max(corner_depth, adj_length - child.location.x)

            corner_front_y = -(corner_depth + overhang_front)

            # L-shape: deeper on left (corner wing), standard on right
            #
            #  Back edge (y = std_back_y)
            #  +-------+-------------------------+
            #  |       |   standard depth         |  <- std_front_y
            #  |       +-------------------------+
            #  |  corner depth (Dim Y)            |
            #  +----------------------------------+  <- corner_front_y
            #  sx   transition(Left Depth)        ex

            verts = [
                # Bottom face (z_bot)
                (sx,                   std_back_y,    z_bot),  # 0  back-left
                (sx,                   corner_front_y, z_bot), # 1  front-left (deep)
                (corner_transition_x,  corner_front_y, z_bot), # 2  front corner step
                (corner_transition_x,  std_front_y,    z_bot), # 3  front step-in
                (ex,                   std_front_y,    z_bot), # 4  front-right
                (ex,                   std_back_y,     z_bot), # 5  back-right
                # Top face (z_top) - same XY, different Z
                (sx,                   std_back_y,    z_top),  # 6
                (sx,                   corner_front_y, z_top), # 7
                (corner_transition_x,  corner_front_y, z_top), # 8
                (corner_transition_x,  std_front_y,    z_top), # 9
                (ex,                   std_front_y,    z_top), # 10
                (ex,                   std_back_y,     z_top), # 11
            ]
            faces = [
                (0, 1, 2, 3, 4, 5),     # bottom
                (6, 11, 10, 9, 8, 7),   # top
                (0, 6, 7, 1),           # left side
                (1, 7, 8, 2),           # front-left (deep)
                (2, 8, 9, 3),           # step face
                (3, 9, 10, 4),          # front-right (std)
                (4, 10, 11, 5),         # right side
                (5, 11, 6, 0),          # back
            ]

        elif right_corner:
            corner_cage = hb_types.GeoNodeCage(right_corner)
            corner_dim_y = corner_cage.get_input('Dim Y')
            corner_right_depth = right_corner.get('Right Depth', corner_dim_y)

            # Transition at end - Right Depth - overhang — step face is exposed
            corner_transition_x = end_x - corner_right_depth - overhang_front

            # Deep section depth: check adjacent wall for cabinets to reach
            corner_depth = corner_dim_y
            if has_right_conn:
                adj_wall_node = hb_types.GeoNodeWall(wall_obj)
                adj_wall = adj_wall_node.get_connected_wall('right')
                if adj_wall:
                    for child in adj_wall.obj.children:
                        if (child.get('IS_FRAMELESS_CABINET_CAGE')
                                and child.get('CABINET_TYPE') == 'BASE'
                                and not child.get('IS_CORNER_CABINET')):
                            cage_child = hb_types.GeoNodeCage(child)
                            cab_end = child.location.x + cage_child.get_input('Dim X')
                            if cab_end <= corner_depth + 0.01:
                                corner_depth = max(corner_depth, cab_end)

            corner_front_y = -(corner_depth + overhang_front)

            # L-shape: standard on left, deeper on right (corner wing)
            verts = [
                # Bottom face (z_bot)
                (sx,                   std_back_y,     z_bot), # 0  back-left
                (sx,                   std_front_y,    z_bot), # 1  front-left (std)
                (corner_transition_x,  std_front_y,    z_bot), # 2  front step-out
                (corner_transition_x,  corner_front_y, z_bot), # 3  front corner step
                (ex,                   corner_front_y, z_bot), # 4  front-right (deep)
                (ex,                   std_back_y,     z_bot), # 5  back-right
                # Top face (z_top)
                (sx,                   std_back_y,     z_top), # 6
                (sx,                   std_front_y,    z_top), # 7
                (corner_transition_x,  std_front_y,    z_top), # 8
                (corner_transition_x,  corner_front_y, z_top), # 9
                (ex,                   corner_front_y, z_top), # 10
                (ex,                   std_back_y,     z_top), # 11
            ]
            faces = [
                (0, 1, 2, 3, 4, 5),     # bottom
                (6, 11, 10, 9, 8, 7),   # top
                (0, 6, 7, 1),           # left side
                (1, 7, 8, 2),           # front-left (std)
                (2, 8, 9, 3),           # step face
                (3, 9, 10, 4),          # front-right (deep)
                (4, 10, 11, 5),         # right side
                (5, 11, 6, 0),          # back
            ]

    mesh = bpy.data.meshes.new('Countertop')
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new('Countertop', mesh)
    obj.parent = wall_obj
    obj['IS_COUNTERTOP'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
    context.scene.collection.objects.link(obj)

    return obj


def create_group_countertop(context, group_obj, cabinets):
    """Create a single countertop spanning all base cabinets in a cage group."""
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

    overhang_front = props.countertop_overhang_front
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

    # Compute bounding box across all base cabinets in group-local space
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    cab_height = 0

    for cab in cabinets:
        cage = hb_types.GeoNodeCage(cab)
        dx = cage.get_input('Dim X')
        dy = cage.get_input('Dim Y')
        dz = cage.get_input('Dim Z')
        cab_height = max(cab_height, dz)

        cx = cab.location.x
        cy = cab.location.y

        min_x = min(min_x, cx)
        max_x = max(max_x, cx + dx)
        # Dim Y goes in -Y direction (Mirror Y)
        min_y = min(min_y, cy - dy)
        max_y = max(max_y, cy)

    # Countertop bounds with overhang on all sides
    start_x = min_x - overhang_sides
    end_x = max_x + overhang_sides
    front_y = min_y - overhang_front
    back_y = max_y + overhang_back
    z_bot = cab_height
    z_top = cab_height + thickness

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
    obj.parent = group_obj
    obj['IS_COUNTERTOP'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
    context.scene.collection.objects.link(obj)

    return obj


def create_island_countertop(context, cab_obj):
    """Create a countertop for a lone island cabinet (not in a group)."""
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

    selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Only add countertops to selected cabinets",
        default=False
    )  # type: ignore

    def execute(self, context):
        wall_cabinets, cage_groups, island_cabinets = gather_base_cabinets(context, self.selected_only)

        if not wall_cabinets and not cage_groups and not island_cabinets:
            if self.selected_only:
                self.report({'WARNING'}, "No base cabinets selected")
            else:
                self.report({'WARNING'}, "No base cabinets found")
            return {'CANCELLED'}

        if not self.selected_only:
            # Remove existing countertops only when adding to all
            existing = [o for o in context.scene.objects if o.get('IS_COUNTERTOP')]
            for obj in existing:
                bpy.data.objects.remove(obj, do_unlink=True)

        runs = build_wall_runs(wall_cabinets)
        ct_count = 0

        for run in runs:
            for i, (wall_obj, cabinets) in enumerate(run):
                has_left = i > 0
                has_right = i < len(run) - 1
                # Split cabinets at ranges so countertops don't span over them
                sub_groups = split_cabinets_at_ranges(wall_obj, cabinets)
                for gi, group in enumerate(sub_groups):
                    # Suppress overhang on sides adjacent to a range
                    left_conn = has_left if gi == 0 else True
                    right_conn = has_right if gi == len(sub_groups) - 1 else True
                    ct = create_wall_countertop(context, wall_obj, group, left_conn, right_conn)
                    if ct:
                        ct_count += 1

        # Cage group countertops
        for group_obj, cabinets in cage_groups:
            ct = create_group_countertop(context, group_obj, cabinets)
            if ct:
                ct_count += 1

        # Lone island countertops
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


class hb_frameless_OT_countertop_boolean_cut(bpy.types.Operator):
    bl_idname = "hb_frameless.countertop_boolean_cut"
    bl_label = "Cut Countertop"
    bl_description = "Add a boolean cut to the countertop using the selected cutting object (sink, cooktop, etc.)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def execute(self, context):
        selected = context.selected_objects
        active = context.active_object

        # Determine which is the countertop and which is the cutter
        countertop = None
        cutter = None

        for obj in selected:
            if obj.get('IS_COUNTERTOP'):
                countertop = obj
            else:
                cutter = obj

        if not countertop:
            self.report({'WARNING'}, "No countertop found in selection")
            return {'CANCELLED'}

        if not cutter:
            self.report({'WARNING'}, "No cutting object found in selection")
            return {'CANCELLED'}

        # Add boolean modifier
        mod = countertop.modifiers.new(name=f"Cut - {cutter.name}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        mod.solver = 'EXACT'

        # Hide the cutter in viewport
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter['IS_CUTTING_OBJ'] = True

        self.report({'INFO'}, f"Added boolean cut using {cutter.name}")
        return {'FINISHED'}


classes = (
    hb_frameless_OT_add_countertops,
    hb_frameless_OT_remove_countertops,
    hb_frameless_OT_countertop_boolean_cut,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
