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


def gather_base_cabinets(context):
    """Collect base cabinets grouped by wall, cage groups, and lone islands."""
    wall_cabinets = {}
    cage_groups = []
    island_cabinets = []

    # Track cabinets that belong to cage groups so we don't double-count
    grouped_cabs = set()

    # Find cage groups first
    for obj in context.scene.objects:
        if obj.get('IS_CAGE_GROUP'):
            countertop_children = [c for c in obj.children 
                                   if (c.get('IS_FRAMELESS_CABINET_CAGE') and c.get('CABINET_TYPE') == 'BASE')
                                   or (c.get('IS_FRAMELESS_PRODUCT_CAGE') and c.get('PART_TYPE') == 'SUPPORT_FRAME')]
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

        if obj.parent and obj.parent.get('IS_WALL_BP'):
            wall = obj.parent
            if wall not in wall_cabinets:
                wall_cabinets[wall] = []
            wall_cabinets[wall].append(obj)
        else:
            island_cabinets.append(obj)

    return wall_cabinets, cage_groups, island_cabinets


def build_wall_runs(wall_cabinets):
    """Group connected walls into runs. Returns list of runs,
    where each run is a list of (wall_obj, cabinets) tuples."""
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


def create_wall_countertop(context, wall_obj, cabinets, has_left_conn, has_right_conn):
    """Create a straight rectangular countertop for cabinets on a single wall.
    Connected ends get no side overhang, exposed ends get overhang."""
    main_scene = hb_project.get_main_scene()
    props = main_scene.hb_frameless

    overhang_front = props.countertop_overhang_front
    overhang_sides = props.countertop_overhang_sides
    overhang_back = props.countertop_overhang_back
    thickness = props.countertop_thickness

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
    z_bot = cab_height
    z_top = cab_height + thickness

    # Side overhang only on exposed (non-connected) ends
    if not has_left_conn:
        start_x -= overhang_sides
    if not has_right_conn:
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

    def execute(self, context):
        wall_cabinets, cage_groups, island_cabinets = gather_base_cabinets(context)

        if not wall_cabinets and not cage_groups and not island_cabinets:
            self.report({'WARNING'}, "No base cabinets found")
            return {'CANCELLED'}

        # Remove existing countertops
        existing = [o for o in context.scene.objects if o.get('IS_COUNTERTOP')]
        for obj in existing:
            bpy.data.objects.remove(obj, do_unlink=True)

        runs = build_wall_runs(wall_cabinets)
        ct_count = 0

        for run in runs:
            for i, (wall_obj, cabinets) in enumerate(run):
                has_left = i > 0
                has_right = i < len(run) - 1
                ct = create_wall_countertop(context, wall_obj, cabinets, has_left, has_right)
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
