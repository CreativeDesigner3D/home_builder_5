import bpy
import bmesh
import math
from mathutils import Vector
from .... import hb_types, hb_project, units
from ...common import countertop_common


def get_cabinet_depth(cab_obj):
    """Get the effective depth of a cabinet for countertop purposes."""
    cage = hb_types.GeoNodeCage(cab_obj)
    if cab_obj.get('IS_CORNER_CABINET'):
        left_d = cab_obj.get('Left Depth', 0)
        right_d = cab_obj.get('Right Depth', 0)
        return max(left_d, right_d) if (left_d or right_d) else cage.get_input('Dim Y')
    return cage.get_input('Dim Y')


# Laminate constructions are sized off the door faces and scribed into
# walls; a run end this close to the end of its wall is against the wall.
WALL_END_TOL = units.inch(1.0)
MAX_FRONT_PROUD = units.inch(2.0)


def uses_laminate_rules(props):
    return getattr(props, 'countertop_construction', 'STANDARD') != 'STANDARD'


def front_proud(cabinets):
    """How far the doors and drawer fronts stand in front of the cabinet
    boxes - the most across ``cabinets`` (pulls are not fronts)."""
    proud = 0.0
    for cab in cabinets:
        try:
            dim_y = hb_types.GeoNodeCage(cab).get_input('Dim Y')
        except Exception:
            continue
        to_cab = cab.matrix_world.inverted()
        for part in cab.children_recursive:
            if part.type != 'MESH' or not part.get('IS_CABINET_FRONT'):
                continue
            for corner in part.bound_box:
                y = (to_cab @ (part.matrix_world @ Vector(corner))).y
                proud = max(proud, -y - dim_y)
    return min(proud, MAX_FRONT_PROUD)


def front_overhang(props, cabinets):
    """The front overhang measured from the cabinet box: for the laminate
    constructions the set overhang is off the door faces."""
    overhang = props.countertop_overhang_front
    if uses_laminate_rules(props):
        overhang += front_proud(cabinets)
    return overhang


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


def _x_range_on_wall(wall_obj, obj):
    """The (min, max) x an object's bounds cover in the wall's space."""
    to_wall = wall_obj.matrix_world.inverted() @ obj.matrix_world
    xs = [(to_wall @ Vector(c)).x for c in obj.bound_box]
    return min(xs), max(xs)


def extend_run_ends(wall_obj, cabinets, start_x, end_x, cab_height,
                    extend_left=True, extend_right=True):
    """Widen a front-side run over what finishes its ends: applied end
    panels on the end cabinets, and fillers or end panels standing in
    the run at base height. A taller panel at an end stops the top the
    way a tall cabinet does.

    Returns (start_x, end_x, tall_at_left, tall_at_right)."""
    tol = 0.005
    tall_left = tall_right = False

    for cab in cabinets:
        for child in cab.children:
            if extend_left and child.get('IS_APPLIED_END_LEFT'):
                start_x = min(start_x, _x_range_on_wall(wall_obj, child)[0])
            elif extend_right and child.get('IS_APPLIED_END_RIGHT'):
                end_x = max(end_x, _x_range_on_wall(wall_obj, child)[1])

    pieces = []
    for child in wall_obj.children:
        if not child.get('IS_FRAMELESS_PRODUCT_CAGE'):
            continue
        if child.get('PART_TYPE') not in ('PANEL', 'CORNER_FILLER'):
            continue
        if abs(child.rotation_euler.z) > 0.1:
            continue
        cage = hb_types.GeoNodeCage(child)
        x0 = child.location.x
        x1 = x0 + cage.get_input('Dim X')
        top = child.location.z + cage.get_input('Dim Z')
        if child.location.z > tol:
            continue
        pieces.append((x0, x1, top > cab_height + tol))

    # Follow touching pieces outward, so a filler beside an end panel
    # is covered too.
    changed = True
    while changed:
        changed = False
        for x0, x1, is_tall in pieces:
            if extend_left and not tall_left and abs(x1 - start_x) < tol:
                if is_tall:
                    tall_left = True
                else:
                    start_x = x0
                    changed = True
            if extend_right and not tall_right and abs(x0 - end_x) < tol:
                if is_tall:
                    tall_right = True
                else:
                    end_x = x1
                    changed = True

    return start_x, end_x, tall_left, tall_right


FRIDGE_TOL = units.inch(1.0)


def refrigerator_beside(wall_obj, start_x, end_x):
    """(left, right): is a refrigerator standing against the run's left
    or right end on this wall."""
    left = right = False
    for child in wall_obj.children:
        if (not child.get('IS_APPLIANCE')
                or child.get('APPLIANCE_TYPE') != 'REFRIGERATOR'
                or abs(child.rotation_euler.z) > 0.1):
            continue
        try:
            width = hb_types.GeoNodeCage(child).get_input('Dim X')
        except Exception:
            continue
        x0 = child.location.x
        if abs(x0 + width - start_x) < FRIDGE_TOL:
            left = True
        if abs(x0 - end_x) < FRIDGE_TOL:
            right = True
    return left, right


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

    overhang_front = front_overhang(props, cabinets)
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

    if hb_types.is_curved_wall(wall_obj):
        return countertop_common.create_curved_countertop(
            context, wall_obj, cabinets, overhang_front, overhang_sides,
            overhang_back, thickness, has_left_conn, has_right_conn, 'FRAMELESS')

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

    # Fillers, end panels and applied ends at the run's ends are under
    # the top too; corner ends keep the corner cabinet's own L.
    if not is_back_side:
        start_x, end_x, panel_tall_left, panel_tall_right = extend_run_ends(
            wall_obj, cabinets, start_x, end_x, cab_height,
            extend_left=left_corner is None,
            extend_right=right_corner is None)
        suppress_left = suppress_left or panel_tall_left
        suppress_right = suppress_right or panel_tall_right

    # --- Build the countertop mesh ---
    if is_back_side:
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_thickness = wall_node.get_input('Thickness')
        std_back_y = wall_thickness - overhang_back
        std_front_y = wall_thickness + std_depth + overhang_front
    else:
        std_front_y = -(std_depth + overhang_front)
        std_back_y = overhang_back

    # Apply side overhang. A laminate top's finished end standing in a
    # refrigerator opening takes the smaller refrigerator overhang.
    side_left = side_right = overhang_sides
    fridge_left = fridge_right = False
    if uses_laminate_rules(props) and not is_back_side:
        fridge_left, fridge_right = refrigerator_beside(wall_obj, start_x, end_x)
        if fridge_left:
            side_left = props.countertop_fridge_overhang
        if fridge_right:
            side_right = props.countertop_fridge_overhang
    sx = start_x - (side_left if not suppress_left else 0)
    ex = end_x + (side_right if not suppress_right else 0)

    # Laminate tops: an end that runs into a wall goes to the wall plus
    # the trim scribe, never an overhang into it. Corners and talls keep
    # their butt joints.
    wall_left = wall_right = False
    if uses_laminate_rules(props) and not is_back_side:
        scribe = props.countertop_trim_scribe
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall_node.get_input('Length')
        if (not suppress_left and left_corner is None
                and start_x <= WALL_END_TOL
                and wall_node.get_connected_wall('left')):
            sx = -scribe
            wall_left = True
        if (not suppress_right and right_corner is None
                and end_x >= wall_length - WALL_END_TOL
                and wall_node.get_connected_wall('right')):
            ex = wall_length + scribe
            wall_right = True

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
    context.scene.collection.objects.link(obj)
    countertop_common.finish(obj, 'FRAMELESS')
    if uses_laminate_rules(props) and not is_back_side and not has_l_shape:
        ends = []
        for at_wall, butted, fridge in ((wall_left, suppress_left, fridge_left),
                                        (wall_right, suppress_right, fridge_right)):
            if at_wall:
                ends.append(('WALL', props.countertop_trim_scribe))
            elif butted:
                ends.append(('BUTT', 0.0))
            else:
                ends.append(('FRIDGE' if fridge else 'FINISHED', 0.0))
        apply_laminate_build(obj, props, ends)

    return obj


# Built-up strips and the splash, local sizes (meters).
BUILDUP_DECK = units.inch(0.75)
BUILDUP_STRIP = {'front': units.inch(4.0), 'middle': units.inch(3.0),
                 'back': units.inch(3.0), 'end': units.inch(4.0)}
LAMINATE_SPLASH_THICKNESS = units.inch(0.75)


# The smallest radius a finished outside corner takes, by edge: banding
# needs a gentler curve than a laminate self edge.
MIN_CORNER_RADIUS = {'PVC_3MM': units.inch(3.0), 'SELF': units.inch(2.0)}
# A top butting the front edge of another can't be slid to fit, so its
# wall end gets this much scribe instead of the trim scribe.
BUTTED_WALL_SCRIBE = units.inch(1.0)
# Length a top butting a 3mm banded front edge is cut over, to reach
# under the banding.
BANDED_BUTT_EXTRA = units.inch(0.125)
# Field joints stay this far clear of a sink or cooktop cutout.
JOINT_CUTOUT_CLEAR = units.inch(3.0)


def laminate_edge(props):
    """'SELF' (laminate self edge) or 'PVC_3MM' (3mm banding). A slab
    comes laminated, so it is always banded."""
    if props.countertop_construction == 'SLAB':
        return 'PVC_3MM'
    return props.countertop_laminate_edge


def laminate_ends(obj):
    """The (kind, scribe) of a laminate top's left and right ends."""
    lam = countertop_common._dict(obj.get(countertop_common.LAMINATE_KEY))
    return [(lam.get('left', 'FINISHED'), float(lam.get('scribe_left', 0.0))),
            (lam.get('right', 'FINISHED'), float(lam.get('scribe_right', 0.0)))]


def apply_laminate_build(obj, props, ends, extra=(0.0, 0.0)):
    """Give a laminate wall top its build: the deck and strips of a
    built-up top, the splash and the corner radius. ``ends`` is (kind,
    scribe) for the left and right ends:

    - 'WALL' runs into a wall; the scribe is how far past its face;
    - 'CORNER' runs into the corner wall with another top along it;
    - 'JOIN' butts the front edge of another top;
    - 'BUTT' meets a tall cabinet or panel;
    - 'FINISHED' is open, and 'FRIDGE' is open beside a refrigerator,
      which takes no corner radius.

    Strips stop the build-up clearance short of a wall or a butted end,
    run to a joined one and on under a finished one, where the front
    corner takes the room's corner radius. ``extra`` is length the
    left / right ends are cut over the model, for the parts list."""
    gap = props.countertop_buildup_back_gap
    edge = laminate_edge(props)
    radius = props.countertop_corner_radius
    if radius > 0.0:
        radius = max(radius, MIN_CORNER_RADIUS.get(edge, 0.0))
    inset, walls, radii = [], [], []
    for kind, scribe in ends:
        inset.append({'WALL': scribe + gap, 'CORNER': gap, 'BUTT': gap,
                      'JOIN': 0.0}.get(kind, -1.0))
        walls.append({'WALL': scribe, 'CORNER': 0.0}.get(kind, -1.0))
        radii.append(radius if kind == 'FINISHED' else 0.0)
    obj[countertop_common.LAMINATE_KEY] = {
        'construction': props.countertop_construction, 'edge': edge,
        'left': ends[0][0], 'right': ends[1][0],
        'scribe_left': ends[0][1], 'scribe_right': ends[1][1],
        'extra_left': extra[0], 'extra_right': extra[1]}
    if props.countertop_construction == 'BUILT_UP':
        spec = dict(BUILDUP_STRIP, deck=BUILDUP_DECK, back_gap=gap,
                    left=inset[0], right=inset[1],
                    radius_left=radii[0], radius_right=radii[1])
        spec['front'] = props.countertop_buildup_front
        spec['middle'] = props.countertop_buildup_middle
        spec['back'] = props.countertop_buildup_back
        obj[countertop_common.BUILDUP_KEY] = spec
    elif countertop_common.BUILDUP_KEY in obj:
        del obj[countertop_common.BUILDUP_KEY]
    if props.countertop_splash == 'STANDARD':
        obj[countertop_common.SPLASH_KEY] = {
            'height': props.countertop_splash_height,
            'thickness': LAMINATE_SPLASH_THICKNESS,
            'left': walls[0], 'right': walls[1]}
    elif countertop_common.SPLASH_KEY in obj:
        del obj[countertop_common.SPLASH_KEY]
    countertop_common.ensure_outline(obj)
    points = countertop_common.outline_of(obj)
    rect = countertop_common.design_rect(obj)
    if rect:
        corners = countertop_common.corners_of(obj)
        for i, (x, y) in enumerate(points):
            if abs(y - rect[2]) > 1e-6:
                continue
            r = radii[0] if abs(x - rect[0]) < 1e-6 else radii[1]
            extras = tuple(corners[i][3:])
            corners[i] = ((countertop_common.CORNER_RADIUS, r, r) if r > 0.0
                          else countertop_common.SHARP) + extras
        countertop_common.set_outline(obj, points, corners)
    countertop_common.rebuild(obj)


def _move_end(obj, side, x):
    """Move a rectangular top's left (0) or right (1) end to local x."""
    rect = countertop_common.design_rect(obj)
    old = rect[side]
    points = [(x if abs(px - old) < 1e-6 else px, py)
              for px, py in countertop_common.outline_of(obj)]
    countertop_common.set_outline(obj, points,
                                  countertop_common.corners_of(obj))


def _front_in(obj, other, use_max):
    """Where ``other``'s footprint reaches along ``obj``'s x: the far
    side of it when use_max, else the near side."""
    to_obj = (countertop_common.world_matrix(obj).inverted()
              @ countertop_common.world_matrix(other))
    xs = [(to_obj @ Vector((x, y, 0.0))).x
          for x, y in countertop_common.outline_of(other)]
    return max(xs) if use_max else min(xs)


def _butt_into(props, obj, side, x, partner):
    """``obj``'s ``side`` end butts the front edge of ``partner`` at x."""
    _move_end(obj, side, x)
    ends = laminate_ends(obj)
    ends[side] = ('JOIN', 0.0)
    other = 1 - side
    kind, scribe = ends[other]
    if kind == 'WALL':
        target = max(BUTTED_WALL_SCRIBE, scribe)
        rect = countertop_common.design_rect(obj)
        step = target - scribe
        _move_end(obj, other, rect[other] + (step if other else -step))
        ends[other] = ('WALL', target)
    lam = countertop_common._dict(partner.get(countertop_common.LAMINATE_KEY))
    extra = [0.0, 0.0]
    if lam.get('edge') == 'PVC_3MM':
        extra[side] = BANDED_BUTT_EXTRA
    apply_laminate_build(obj, props, ends, tuple(extra))


def _into_corner(props, obj, side):
    ends = laminate_ends(obj)
    ends[side] = ('CORNER', 0.0)
    lam = countertop_common._dict(obj.get(countertop_common.LAMINATE_KEY))
    apply_laminate_build(obj, props, ends,
                         (lam.get('extra_left', 0.0), lam.get('extra_right', 0.0)))


def join_corner_tops(props, run):
    """Lay out the laminate tops meeting at each inside corner of a run.

    ``run`` is [(wall, [tops left to right])]. Where one top runs into
    the corner, the top on the other wall butts its front edge: it is
    cut to meet that edge (over by the banding when the edge is banded)
    and its wall end, if any, gets the butted wall scribe. The top
    running in takes no scribe at the corner."""
    tol = units.inch(0.5)
    for (wall_a, tops_a), (_wall_b, tops_b) in zip(run, run[1:]):
        if not tops_a or not tops_b:
            continue
        a, b = tops_a[-1], tops_b[0]
        if not (a.get(countertop_common.LAMINATE_KEY)
                and b.get(countertop_common.LAMINATE_KEY)):
            continue
        rect_a = countertop_common.design_rect(a)
        rect_b = countertop_common.design_rect(b)
        if not rect_a or not rect_b:
            continue
        length_a = hb_types.GeoNodeWall(wall_a).get_input('Length')
        a_in = rect_a[1] >= length_a - tol
        b_in = rect_b[0] <= tol
        if a_in:
            _butt_into(props, b, 0, _front_in(b, a, True), a)
            _into_corner(props, a, 1)
        elif b_in:
            _butt_into(props, a, 1, _front_in(a, b, False), b)
            _into_corner(props, b, 0)


def cutout_ranges(obj):
    """(x0, x1) in the top's own space of every sink or cooktop cutout
    under it."""
    from ...common import appliance_geo
    to_local = countertop_common.world_matrix(obj).inverted()
    rect = countertop_common.design_rect(obj)
    out = []
    for sink in bpy.context.scene.objects:
        if (not sink.get('IS_APPLIANCE')
                or appliance_geo.appliance_type(sink) not in ('SINK', 'COOKTOP')):
            continue
        for x0, x1, y0, y1, z0, z1 in appliance_geo.sink_cutout_boxes(sink):
            pts = [to_local @ (sink.matrix_world @ Vector((x, y, z0)))
                   for x in (x0, x1) for y in (y0, y1)]
            ys = [p.y for p in pts]
            if rect and (max(ys) <= rect[2] or min(ys) >= rect[3]):
                continue
            out.append((min(p.x for p in pts), max(p.x for p in pts)))
    return out


def cabinet_seams(wall_obj):
    """The x of every base cabinet edge along the front of a wall."""
    seams = set()
    for child in wall_obj.children:
        if (not child.get('IS_FRAMELESS_CABINET_CAGE')
                or abs(child.rotation_euler.z) > 0.1):
            continue
        width = hb_types.GeoNodeCage(child).get_input('Dim X')
        seams.add(round(child.location.x, 6))
        seams.add(round(child.location.x + width, 6))
    return sorted(seams)


def place_field_joints(obj, props):
    """Joint a laminate top wherever it runs past the max length: on
    cabinet seams near an even split, clear of sink cutouts."""
    points = countertop_common.outline_of(obj)
    if len(points) < 3:
        return
    xs = [x for x, _y in points]
    seams = cabinet_seams(obj.parent) if obj.parent else []
    joints = countertop_common.auto_joints(
        min(xs), max(xs), props.countertop_max_length, seams,
        cutout_ranges(obj), JOINT_CUTOUT_CLEAR)
    countertop_common.set_joints(obj, joints)
    countertop_common.rebuild(obj)


def create_group_countertop(context, group_obj, cabinets):
    """Create a single countertop spanning all base cabinets in a cage group."""
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

    overhang_front = front_overhang(props, cabinets)
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
    context.scene.collection.objects.link(obj)
    countertop_common.finish(obj, 'FRAMELESS')

    return obj


def gather_island_appliances(context, cabinets):
    """Under-counter appliances standing in an island.

    A dishwasher between two base cabinets is part of the island and has
    to be covered; without this the top stops at each cabinet and the
    dishwasher is left bare.
    """
    if not cabinets:
        return []
    cabinet_top = max(
        cab.matrix_world.translation.z
        + hb_types.GeoNodeCage(cab).get_input('Dim Z')
        for cab in cabinets)
    out = []
    for obj in context.scene.objects:
        if obj.parent is not None and obj.parent.get('IS_WALL_BP'):
            continue
        if countertop_common.is_under_counter(obj, cabinet_top):
            out.append(obj)
    return out


def create_island_countertops(context, cabinets, appliances):
    """One countertop per island, over all of its cabinets and the
    appliances standing between them."""
    props = hb_project.get_main_scene().hb_frameless
    picked = set(cabinets)
    made = []
    for group in countertop_common.group_members(
            list(cabinets) + list(appliances)):
        group_cabs = [m for m in group if m in picked]
        if not group_cabs:
            continue        # an appliance on its own is not an island
        ct = countertop_common.create_group_countertop(
            context, group,
            front_overhang(props, group_cabs),
            props.countertop_overhang_sides,
            props.countertop_overhang_back,
            props.countertop_thickness,
            'FRAMELESS',
            cabinets=group_cabs)
        if ct:
            made.append(ct)
    return made


def create_island_countertop(context, cab_obj):
    """Create a countertop for a lone island cabinet (not in a group)."""
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

    overhang_front = front_overhang(props, [cab_obj])
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
    context.scene.collection.objects.link(obj)
    countertop_common.finish(obj, 'FRAMELESS')

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

        # With a counter height in use, the cabinets come to it first so
        # the tops built below land on it.
        from .. import props_hb_frameless
        under = [c for cabs in wall_cabinets.values() for c in cabs]
        for _group, cabs in cage_groups:
            under.extend(cabs)
        under.extend(island_cabinets)
        props_hb_frameless.apply_counter_height(
            context.scene, under, force=self.selected_only)

        if not self.selected_only:
            # Remove existing countertops only when adding to all
            existing = [o for o in context.scene.objects if o.get('IS_COUNTERTOP')]
            for obj in existing:
                bpy.data.objects.remove(obj, do_unlink=True)

        runs = build_wall_runs(wall_cabinets)
        ct_count = 0

        props = hb_project.get_main_scene().hb_frameless
        for run in runs:
            run_tops = []
            for i, (wall_obj, cabinets) in enumerate(run):
                has_left = i > 0
                has_right = i < len(run) - 1
                # Split cabinets at ranges so countertops don't span over them
                sub_groups = split_cabinets_at_ranges(wall_obj, cabinets)
                wall_tops = []
                for gi, group in enumerate(sub_groups):
                    # Suppress overhang on sides adjacent to a range
                    left_conn = has_left if gi == 0 else True
                    right_conn = has_right if gi == len(sub_groups) - 1 else True
                    ct = create_wall_countertop(context, wall_obj, group, left_conn, right_conn)
                    if ct:
                        ct_count += 1
                        wall_tops.append(ct)
                run_tops.append((wall_obj, wall_tops))
            if uses_laminate_rules(props):
                join_corner_tops(props, run_tops)
                for _wall, tops in run_tops:
                    for ct in tops:
                        if ct.get(countertop_common.LAMINATE_KEY):
                            place_field_joints(ct, props)

        # Cage group countertops
        for group_obj, cabinets in cage_groups:
            ct = create_group_countertop(context, group_obj, cabinets)
            if ct:
                ct_count += 1

        # Island countertops -- one slab per island, not per cabinet
        if island_cabinets:
            appliances = gather_island_appliances(context, island_cabinets)
            ct_count += len(create_island_countertops(
                context, island_cabinets, appliances))

        # The room's countertop laminate, when one is chosen; new tops
        # are the only ones without it.
        props_hb_frameless.apply_countertop_material(
            [o for o in context.scene.objects if o.get('IS_COUNTERTOP')
             and o.get('HB_COUNTERTOP_LIB') == 'FRAMELESS'])

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


MAX_JOINTS = 8


def _laminate_top(context):
    obj = context.active_object
    if obj and obj.get('IS_COUNTERTOP') and obj.get(countertop_common.LAMINATE_KEY):
        return obj
    return None


def _top_span(obj):
    xs = [x for x, _y in countertop_common.outline_of(obj)]
    return min(xs), max(xs)


def _spread_joints(self, context):
    """New joint rows start evenly spaced; rows already set are kept."""
    count = self.count
    pos = list(self.positions)
    good = all(0.0 < pos[i] < self.length and (i == 0 or pos[i] > pos[i - 1])
               for i in range(count))
    if not good:
        for i in range(count):
            pos[i] = self.length * (i + 1) / (count + 1)
        self.positions = pos


class hb_frameless_OT_countertop_joints(bpy.types.Operator):
    bl_idname = "hb_frameless.countertop_joints"
    bl_label = "Field Joints"
    bl_description = ("Move, add or remove the field joints across this "
                      "laminate countertop")
    bl_options = {'REGISTER', 'UNDO'}

    count: bpy.props.IntProperty(name="Joints", min=0, max=MAX_JOINTS,
                                 update=_spread_joints)  # type: ignore
    positions: bpy.props.FloatVectorProperty(
        name="From Left", size=MAX_JOINTS, unit='LENGTH',
        precision=4)  # type: ignore
    length: bpy.props.FloatProperty(options={'HIDDEN'})  # type: ignore
    auto: bpy.props.BoolProperty(
        name="Place Automatically",
        description="Put the joints back where Add Countertops places them: "
                    "on cabinet seams, clear of sinks, no piece over the "
                    "max length")  # type: ignore

    @classmethod
    def poll(cls, context):
        return _laminate_top(context) is not None

    def invoke(self, context, event):
        obj = _laminate_top(context)
        x0, x1 = _top_span(obj)
        self.length = x1 - x0
        joints = [j - x0 for j in countertop_common.joints_of(obj)][:MAX_JOINTS]
        pos = [0.0] * MAX_JOINTS
        pos[:len(joints)] = joints
        self.positions = pos
        self.count = len(joints)
        self.auto = False
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        props = hb_project.get_main_scene().hb_frameless
        layout = self.layout
        layout.label(text="Top length: " + units.unit_to_string(
            context.scene.unit_settings, self.length))
        layout.prop(self, 'auto')
        col = layout.column(align=True)
        col.enabled = not self.auto
        col.prop(self, 'count')
        for i in range(self.count):
            col.prop(self, 'positions', index=i, text=f"Joint {i + 1} from Left")
        edges = [0.0] + sorted(self.positions[:self.count]) + [self.length]
        longest = max(b - a for a, b in zip(edges, edges[1:]))
        if not self.auto and longest > props.countertop_max_length + 1e-6:
            layout.label(text="A piece is longer than the max length ("
                         + units.unit_to_string(context.scene.unit_settings,
                                                props.countertop_max_length)
                         + ")", icon='ERROR')

    def execute(self, context):
        obj = _laminate_top(context)
        props = hb_project.get_main_scene().hb_frameless
        if self.auto:
            place_field_joints(obj, props)
            return {'FINISHED'}
        x0, _x1 = _top_span(obj)
        joints = [x0 + p for p in self.positions[:self.count]
                  if 0.0 < p < self.length]
        countertop_common.set_joints(obj, joints)
        countertop_common.rebuild(obj)
        return {'FINISHED'}


class hb_frameless_OT_countertop_parts(bpy.types.Operator):
    bl_idname = "hb_frameless.countertop_parts"
    bl_label = "Countertop Parts"
    bl_description = ("List the parts this laminate countertop is made "
                      "from, with the laminate pieces cut over for trimming")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return _laminate_top(context) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=760)

    def draw(self, context):
        from .. import countertop_parts
        obj = _laminate_top(context)
        layout = self.layout
        rows = countertop_parts.laminate_parts(obj)
        grid = layout.grid_flow(row_major=True, columns=6, even_columns=False,
                                align=True)
        for text in ("Qty", "Part", "Length", "Width", "Thick", "Material / Edges"):
            grid.label(text=text)
        for part in rows:
            grid.label(text=str(part['qty']))
            grid.label(text=part['name'])
            grid.label(text=countertop_parts.inches(part['length']))
            grid.label(text=countertop_parts.inches(part['width']))
            grid.label(text=countertop_parts.inches(part['thickness'])
                       if part['thickness'] else "-")
            grid.label(text=part['material'] + (" | " + part['edges']
                                                if part['edges'] else ""))
        for line in countertop_parts.notes(obj):
            layout.label(text=line, icon='INFO')

    def execute(self, context):
        return {'FINISHED'}


classes = (
    hb_frameless_OT_add_countertops,
    hb_frameless_OT_remove_countertops,
    hb_frameless_OT_countertop_boolean_cut,
    hb_frameless_OT_countertop_joints,
    hb_frameless_OT_countertop_parts,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
