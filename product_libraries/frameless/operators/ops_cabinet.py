import bpy
import math
from .. import types_frameless
from .. import props_hb_frameless
from . import ops_placement
import os
from mathutils import Vector
from .... import hb_utils, hb_types, hb_project, units

class hb_frameless_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.cabinet_prompts"
    bl_label = "Cabinet Prompts"
    bl_description = "Edit cabinet properties"
    bl_options = {'UNDO'}

    cabinet_width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5) # type: ignore
    cabinet_height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5) # type: ignore
    cabinet_depth: bpy.props.FloatProperty(name="Depth", unit='LENGTH', precision=5) # type: ignore
    toe_kick_height: bpy.props.FloatProperty(name="Toe Kick Height", unit='LENGTH', precision=5) # type: ignore
    toe_kick_setback: bpy.props.FloatProperty(name="Toe Kick Setback", unit='LENGTH', precision=5) # type: ignore
    remove_bottom: bpy.props.BoolProperty(name="Remove Bottom", default=False) # type: ignore
    finished_interior: bpy.props.BoolProperty(name="Finished Interior", default=False) # type: ignore

    cabinet = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def invoke(self, context, event):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        self.cabinet = hb_types.GeoNodeCage(cabinet_bp)
        self.cabinet_width = self.cabinet.get_input('Dim X')
        self.cabinet_height = self.cabinet.get_input('Dim Z')
        self.cabinet_depth = self.cabinet.get_input('Dim Y')
        
        # Get toe kick properties if they exist (BASE and TALL cabinets)
        if 'Toe Kick Height' in cabinet_bp:
            self.toe_kick_height = cabinet_bp['Toe Kick Height']
        if 'Toe Kick Setback' in cabinet_bp:
            self.toe_kick_setback = cabinet_bp['Toe Kick Setback']
        if 'Remove Bottom' in cabinet_bp:
            self.remove_bottom = cabinet_bp['Remove Bottom']
        self.finished_interior = cabinet_bp.get('Finished Interior', False)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        self.cabinet.set_input('Dim X', self.cabinet_width)
        self.cabinet.set_input('Dim Z', self.cabinet_height)
        self.cabinet.set_input('Dim Y', self.cabinet_depth)
        
        # Set toe kick properties if they exist
        if 'Toe Kick Height' in self.cabinet.obj:
            self.cabinet.obj['Toe Kick Height'] = self.toe_kick_height
        if 'Toe Kick Setback' in self.cabinet.obj:
            self.cabinet.obj['Toe Kick Setback'] = self.toe_kick_setback
        if 'Remove Bottom' in self.cabinet.obj:
            self.cabinet.obj['Remove Bottom'] = self.remove_bottom
        # Handle Finished Interior toggle
        old_finished = self.cabinet.obj.get('Finished Interior', False)
        if self.finished_interior != old_finished:
            self.cabinet.obj['Finished Interior'] = self.finished_interior
            # Re-apply style to update materials
            style_index = self.cabinet.obj.get('CABINET_STYLE_INDEX', 0)
            main_scene = hb_project.get_main_scene()
            props = main_scene.hb_frameless
            if len(props.cabinet_styles) > 0:
                if style_index < len(props.cabinet_styles):
                    style = props.cabinet_styles[style_index]
                else:
                    style = props.cabinet_styles[0]
                style.assign_style_to_cabinet(self.cabinet.obj)

        hb_utils.run_calc_fix(context, self.cabinet.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        
        row = col.row(align=True)
        row.label(text="Width:")
        row.prop(self, 'cabinet_width', text="")
        
        row = col.row(align=True)
        row.label(text="Height:")
        row.prop(self, 'cabinet_height', text="")
        
        row = col.row(align=True)
        row.label(text="Depth:")
        row.prop(self, 'cabinet_depth', text="")
        
        # Show toe kick options for BASE and TALL cabinets
        if 'Toe Kick Height' in self.cabinet.obj:
            box = layout.box()
            box.label(text="Toe Kick")
            col = box.column(align=True)
            
            row = col.row(align=True)
            row.label(text="Height:")
            row.prop(self, 'toe_kick_height', text="")
            
            row = col.row(align=True)
            row.label(text="Setback:")
            row.prop(self, 'toe_kick_setback', text="")
            
            row = col.row()
            row.prop(self, 'remove_bottom')
        
        # Base Top Construction for BASE cabinets
        if self.cabinet.obj.get('CABINET_TYPE') == 'BASE':
            box = layout.box()
            box.label(text="Base Top Construction")
            row = box.row()
            self.cabinet.draw_prop(row, 'Base Top Construction', text="")
        
        # Finished Interior option
        box = layout.box()
        box.label(text="Interior")
        row = box.row()
        row.prop(self, 'finished_interior')


class hb_frameless_OT_drop_cabinet_to_countertop(bpy.types.Operator):
    bl_idname = "hb_frameless.drop_cabinet_to_countertop"
    bl_label = "Drop to Countertop"
    bl_description = "Drop the bottom of an upper cabinet to the countertop surface"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp and cabinet_bp.get('CABINET_TYPE') == 'UPPER':
                return True
        return False

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        cabinet = hb_types.GeoNodeCage(cabinet_bp)
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        countertop_top = props.base_cabinet_height + props.countertop_thickness
        current_height = cabinet.get_input('Dim Z')
        current_top = cabinet_bp.location.z + current_height
        
        new_height = current_top - countertop_top
        cabinet.set_input('Dim Z', new_height)
        cabinet_bp.location.z = countertop_top
        hb_utils.run_calc_fix(context, cabinet.obj)
        
        return {'FINISHED'}


class hb_frameless_OT_add_applied_end(bpy.types.Operator):
    bl_idname = "hb_frameless.add_applied_end"
    bl_label = "Add Applied End"
    bl_description = "Add an applied finished end panel to the cabinet"
    bl_options = {'UNDO'}

    side: bpy.props.EnumProperty(
        name="Side",
        items=[
            ('LEFT', "Left", "Add to left side"),
            ('RIGHT', "Right", "Add to right side"),
            ('BACK', "Back", "Add to back"),
            ('BOTH', "Both", "Add to both left and right sides"),
        ],
        default='LEFT'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def has_applied_end(self, cabinet_obj, side):
        """Check if cabinet already has an applied end on the specified side."""
        for child in cabinet_obj.children:
            if child.get('IS_APPLIED_END_' + side):
                return True
        return False

    def remove_applied_end(self, cabinet_obj, side):
        """Remove existing applied end from specified side."""
        for child in list(cabinet_obj.children):
            if child.get('IS_APPLIED_END_' + side):
                hb_utils.delete_obj_and_children(child)

    def create_applied_end(self, context, cabinet_obj, side):
        """Create an applied end panel on the specified side.
        
        Panel covers full cabinet height (including toe kick area) and
        extends past the front to be flush with doors/drawers.
        """
        props = bpy.context.scene.hb_frameless
        cabinet = hb_types.GeoNodeCage(cabinet_obj)
        
        # Get cabinet dimensions
        dim_x = cabinet.var_input('Dim X', 'dim_x')
        dim_y = cabinet.var_input('Dim Y', 'dim_y')
        dim_z = cabinet.var_input('Dim Z', 'dim_z')
        
        # Extension to be flush with door front:
        # door_to_cabinet_gap (0.125") + front_thickness (0.75") = 0.875"
        door_to_cab_gap = units.inch(0.125)
        front_thickness = units.inch(0.75)
        front_extension = door_to_cab_gap + front_thickness
        
        # Create the applied end panel
        panel = types_frameless.CabinetPart()
        panel.create(f'Applied End {side.title()}')
        panel.obj['IS_APPLIED_END_' + side] = True
        panel.obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
        panel.obj['Finish Top'] = True
        panel.obj['Finish Bottom'] = True        
        panel.obj.parent = cabinet_obj
        
        # Position at floor level (Z=0) for full height coverage
        panel.obj.location.z = 0
        
        if side == 'LEFT':
            # Rotate panel to vertical orientation (side panel)
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.obj.location.x = 0
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", False)
            # Full cabinet height
            panel.driver_input("Length", 'dim_z', [dim_z])
            # Depth extends past front to be flush with door/drawer fronts
            panel.driver_input("Width", f'dim_y+{front_extension}', [dim_y])
            
        elif side == 'RIGHT':
            # Rotate panel to vertical orientation (side panel)
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.driver_location('x', 'dim_x', [dim_x])
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", True)
            # Full cabinet height
            panel.driver_input("Length", 'dim_z', [dim_z])
            # Depth extends past front to be flush with door/drawer fronts
            panel.driver_input("Width", f'dim_y+{front_extension}', [dim_y])
            
        elif side == 'BACK':
            # Back panel - at back of cabinet
            panel.obj.rotation_euler.x = math.radians(90)
            panel.obj.location.y = 0
            panel.set_input("Mirror Y", False)
            panel.set_input("Mirror Z", True)
            # Width matches cabinet width
            panel.driver_input("Length", 'dim_x', [dim_x])
            # Height is full cabinet height
            panel.driver_input("Width", 'dim_z', [dim_z])
        
        # Set thickness
        panel.set_input("Thickness", props.default_carcass_part_thickness)
        
        # Assign cabinet style material to the applied end
        style_index = cabinet_obj.get('CABINET_STYLE_INDEX', 0)
        main_scene = hb_project.get_main_scene()
        main_props = main_scene.hb_frameless
        if main_props.cabinet_styles and style_index < len(main_props.cabinet_styles):
            style = main_props.cabinet_styles[style_index]
            material, material_rotated = style.get_finish_material()
            if material:
                panel.set_input("Top Surface", material)
                panel.set_input("Bottom Surface", material)
                panel.set_input("Edge W1", material_rotated)
                panel.set_input("Edge W2", material_rotated)
                panel.set_input("Edge L1", material_rotated)
                panel.set_input("Edge L2", material_rotated)
                
                # Also set Material input on any cabinet part modifiers
                for mod in panel.obj.modifiers:
                    if mod.type == 'NODES' and mod.node_group:
                        if 'Material' in mod.node_group.interface.items_tree:
                            node_input = mod.node_group.interface.items_tree['Material']
                            mod[node_input.identifier] = material
        
        return panel.obj

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        if not cabinet_bp:
            self.report({'ERROR'}, "Could not find cabinet")
            return {'CANCELLED'}
        
        sides_to_add = []
        if self.side == 'LEFT':
            sides_to_add = ['LEFT']
        elif self.side == 'RIGHT':
            sides_to_add = ['RIGHT']
        elif self.side == 'BACK':
            sides_to_add = ['BACK']
        else:  # BOTH
            sides_to_add = ['LEFT', 'RIGHT']
        
        for side in sides_to_add:
            # Remove existing applied end if present
            if self.has_applied_end(cabinet_bp, side):
                self.remove_applied_end(cabinet_bp, side)
            
            # Create new applied end
            self.create_applied_end(context, cabinet_bp, side)
        
        # Run calc fix
        hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}


class hb_frameless_OT_remove_applied_end(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_applied_end"
    bl_label = "Remove Applied End"
    bl_description = "Remove an applied finished end panel from the cabinet"
    bl_options = {'UNDO'}

    side: bpy.props.EnumProperty(
        name="Side",
        items=[
            ('LEFT', "Left", "Remove from left side"),
            ('RIGHT', "Right", "Remove from right side"),
            ('BACK', "Back", "Remove from back"),
            ('BOTH', "Both", "Remove from both left and right sides"),
        ],
        default='LEFT'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp:
                # Check if cabinet has any applied ends
                for child in cabinet_bp.children:
                    if child.get('IS_APPLIED_END_LEFT') or child.get('IS_APPLIED_END_RIGHT') or child.get('IS_APPLIED_END_BACK'):
                        return True
        return False

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        if not cabinet_bp:
            self.report({'ERROR'}, "Could not find cabinet")
            return {'CANCELLED'}
        
        sides_to_remove = []
        if self.side == 'LEFT':
            sides_to_remove = ['LEFT']
        elif self.side == 'RIGHT':
            sides_to_remove = ['RIGHT']
        elif self.side == 'BACK':
            sides_to_remove = ['BACK']
        else:  # BOTH
            sides_to_remove = ['LEFT', 'RIGHT']
        
        for side in sides_to_remove:
            for child in list(cabinet_bp.children):
                if child.get('IS_APPLIED_END_' + side):
                    hb_utils.delete_obj_and_children(child)
        
        return {'FINISHED'}

class hb_frameless_OT_delete_cabinet(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_cabinet"
    bl_label = "Delete Cabinet"
    bl_description = "Delete the selected cabinet and all its parts"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def execute(self, context):
        cabinet_bps = set()
        for obj in context.selected_objects:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp:
                cabinet_bps.add(cabinet_bp)
        for cabinet_bp in cabinet_bps:
            hb_utils.delete_obj_and_children(cabinet_bp)
        return {'FINISHED'}


class hb_frameless_OT_create_cabinet_group(bpy.types.Operator):
    bl_idname = "hb_frameless.create_cabinet_group"
    bl_label = "Create Cabinet Group"
    bl_description = "This will create a cabinet group for all of the selected cabinets"

    CABINET_LIKE_MARKERS = ['IS_FRAMELESS_CABINET_CAGE', 'IS_FRAMELESS_PRODUCT_CAGE', 'IS_APPLIANCE']

    def execute(self, context):
        # Get Selected Cabinets, Products, and Appliances
        selected_cabinets = []
        for obj in context.selected_objects:
            if any(marker in obj for marker in self.CABINET_LIKE_MARKERS):
                cabinet_cage = types_frameless.Cabinet(obj)
                selected_cabinets.append(cabinet_cage)
        
        if not selected_cabinets:
            self.report({'WARNING'}, "No cabinets, products, or appliances selected")
            return {'CANCELLED'}
        
        # Find overall size and base point for new group
        base_point_location, base_point_rotation, overall_width, overall_depth, overall_height = \
            self.calculate_group_bounds(selected_cabinets)

        # Create Cabinet Group
        cabinet_group = types_frameless.Cabinet()
        cabinet_group.create("New Cabinet Group")
        cabinet_group.obj['IS_CAGE_GROUP'] = True
        cabinet_group.obj.parent = None
        cabinet_group.obj.location = base_point_location
        cabinet_group.obj.rotation_euler = base_point_rotation
        cabinet_group.set_input('Dim X', overall_width)
        cabinet_group.set_input('Dim Y', overall_depth)
        cabinet_group.set_input('Dim Z', overall_height)
        cabinet_group.set_input('Mirror Y', True)
        
        bpy.ops.object.select_all(action='DESELECT')

        # Reparent all selected cabinets to the new group
        # We need to preserve their world position while changing parent
        for selected_cabinet in selected_cabinets:
            # Store world matrix before reparenting
            world_matrix = selected_cabinet.obj.matrix_world.copy()
            
            # Set new parent
            selected_cabinet.obj.parent = cabinet_group.obj
            
            # Restore world position by calculating new local matrix
            selected_cabinet.obj.matrix_world = world_matrix
        
        cabinet_group.obj.select_set(True)
        context.view_layer.objects.active = cabinet_group.obj

        bpy.ops.hb_frameless.select_cabinet_group(toggle_on=True,cabinet_group_name=cabinet_group.obj.name)

        return {'FINISHED'}
    
    def calculate_group_bounds(self, selected_cabinets):
        """
        Calculate the overall bounds of selected cabinets in world space.
        Works for kitchen islands with cabinets at any rotation (0°, 90°, 180°, 270°).
        
        Cabinet coordinate system:
        - Origin at back-left-bottom
        - Dim X extends in +X (local)
        - Dim Y is MIRRORED, extends in -Y (local) toward front
        - Dim Z extends in +Z (local)
        
        Returns (location, rotation, width, depth, height)
        Location is at back-left-bottom of the world-space bounding box.
        """

        if not selected_cabinets:
            return (Vector((0, 0, 0)), (0, 0, 0), 0, 0, 0)
        
        # Initialize world-space bounds
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        min_z = float('inf')
        max_z = float('-inf')
        
        for cabinet in selected_cabinets:
            # Get cabinet dimensions
            cab_width = cabinet.get_input('Dim X')
            cab_depth = cabinet.get_input('Dim Y')
            cab_height = cabinet.get_input('Dim Z')
            
            # Define the 8 corners in cabinet's LOCAL space
            # Y is mirrored, so depth extends in -Y direction
            local_corners = [
                Vector((0, 0, 0)),                    # back-left-bottom (origin)
                Vector((cab_width, 0, 0)),            # back-right-bottom
                Vector((0, -cab_depth, 0)),           # front-left-bottom
                Vector((cab_width, -cab_depth, 0)),   # front-right-bottom
                Vector((0, 0, cab_height)),           # back-left-top
                Vector((cab_width, 0, cab_height)),   # back-right-top
                Vector((0, -cab_depth, cab_height)),  # front-left-top
                Vector((cab_width, -cab_depth, cab_height)),  # front-right-top
            ]
            
            # Transform each corner to world space using cabinet's full matrix
            world_matrix = cabinet.obj.matrix_world
            for local_corner in local_corners:
                world_corner = world_matrix @ local_corner
                min_x = min(min_x, world_corner.x)
                max_x = max(max_x, world_corner.x)
                min_y = min(min_y, world_corner.y)
                max_y = max(max_y, world_corner.y)
                min_z = min(min_z, world_corner.z)
                max_z = max(max_z, world_corner.z)
        
        # Calculate overall dimensions
        overall_width = max_x - min_x
        overall_depth = max_y - min_y
        overall_height = max_z - min_z
        
        # Group cage location: back-left-bottom of world AABB
        # Since group cage also has mirrored Y, origin is at back (max_y), not front (min_y)
        base_point_location = Vector((min_x, max_y, min_z))
        
        # Group rotation is (0, 0, 0) since we're using world-space AABB
        base_point_rotation = (0, 0, 0)
        
        return (base_point_location, base_point_rotation, overall_width, overall_depth, overall_height)


class hb_frameless_OT_select_cabinet_group(bpy.types.Operator):
    """Select Cabinet Group"""
    bl_idname = "hb_frameless.select_cabinet_group"
    bl_label = 'Select Cabinet Group'
    bl_description = "This will select the cabinet group"

    toggle_on: bpy.props.BoolProperty(name="Toggle On",default=False)# type: ignore

    cabinet_group_name: bpy.props.StringProperty(name="Cabinet Group Name",default="")# type: ignore

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        cabinet_group = bpy.data.objects[self.cabinet_group_name]
        ops_placement.toggle_cabinet_color(cabinet_group,True,type_name="IS_FRAMELESS_CABINET_CAGE",dont_show_parent=False)
        cabinet_group.select_set(True)
        context.view_layer.objects.active = cabinet_group
        for obj in cabinet_group.children_recursive:
            if 'IS_FRAMELESS_CABINET_CAGE' in obj:
                obj.hide_viewport = True
        return {'FINISHED'}



class hb_frameless_OT_adjust_multiple_cabinet_widths(bpy.types.Operator):
    """Adjust widths, offsets, and quantity of selected cabinets"""
    bl_idname = "hb_frameless.adjust_multiple_cabinet_widths"
    bl_label = "Adjust Cabinet Sizes"
    bl_description = "Adjust widths, positions, and quantity of selected cabinets"
    bl_options = {'REGISTER', 'UNDO'}

    total_number_of_cabinets = 0
    number_of_equal_cabinets = 0
    total_width = 0.0
    original_total_width = 0.0
    equal_cabinet_width = 0.0
    non_equal_cabinet_widths = 0.0
    start_x = 0.0

    # Gap boundaries
    gap_left_boundary = 0.0
    gap_right_boundary = 0.0
    gap_width = 0.0
    has_wall = False
    is_back_side = False
    wall_obj = None

    # For rotated cabinets (like islands)
    cabinet_direction = None
    start_position = None

    # Track quantity changes
    _prev_quantity = 0
    _added_cabinets = []

    left_offset: bpy.props.FloatProperty(
        name="Left Offset",
        description="X Location or offset from left gap boundary",
        subtype='DISTANCE',
        unit='LENGTH',
        default=0.0,
        precision=5,
    )  # type: ignore

    right_offset: bpy.props.FloatProperty(
        name="Right Offset",
        description="Offset from right gap boundary",
        subtype='DISTANCE',
        unit='LENGTH',
        default=0.0,
        precision=5,
    )  # type: ignore

    fill_gap: bpy.props.BoolProperty(
        name="Fill Gap",
        description="Redistribute cabinet widths to fill available space after offsets",
        default=False,
    )  # type: ignore

    quantity: bpy.props.IntProperty(
        name="Quantity",
        description="Number of cabinets",
        default=2,
        min=1,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp:
                return True
        return False

    def get_cab_x_range(self, cab_obj):
        """Get (x_start, x_end) for a cabinet accounting for back-side rotation."""
        cage = hb_types.GeoNodeCage(cab_obj)
        dim_x = cage.get_input('Dim X')
        is_back = (abs(cab_obj.rotation_euler.z - math.pi) < 0.1 or
                   abs(cab_obj.rotation_euler.z + math.pi) < 0.1)
        if is_back:
            return (cab_obj.location.x - dim_x, cab_obj.location.x)
        else:
            return (cab_obj.location.x, cab_obj.location.x + dim_x)

    def calculate_gap_boundaries(self, context, wall_obj, cabinet_objs):
        """Find the available gap boundaries around the selected cabinets."""
        wall_node = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall_node.get_input('Length')

        our_ranges = [self.get_cab_x_range(c) for c in cabinet_objs]
        our_min = min(r[0] for r in our_ranges)
        our_max = max(r[1] for r in our_ranges)

        cabinet_set = set(cabinet_objs)
        gap_left = 0.0
        gap_right = wall_length

        for obj in wall_obj.children:
            if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
                continue
            if obj in cabinet_set:
                continue
            obj_is_back = (abs(obj.rotation_euler.z - math.pi) < 0.1 or
                           abs(obj.rotation_euler.z + math.pi) < 0.1)
            if obj_is_back != self.is_back_side:
                continue
            x_start, x_end = self.get_cab_x_range(obj)
            if x_end <= our_min + 0.001:
                gap_left = max(gap_left, x_end)
            if x_start >= our_max - 0.001:
                gap_right = min(gap_right, x_start)

        return gap_left, gap_right

    def duplicate_cabinet(self, context, source_obj):
        """Duplicate a cabinet cage and all its children with full hierarchy."""
        # Store original state
        old_selected = [o.name for o in context.selected_objects]
        old_active = context.view_layer.objects.active.name if context.view_layer.objects.active else None

        # Collect all objects in the hierarchy
        all_objs = [source_obj] + list(source_obj.children_recursive)

        # Temporarily unhide all objects so they can be selected for duplication
        hidden_objs = {}
        for obj in all_objs:
            if obj.hide_viewport:
                hidden_objs[obj.name] = True
                obj.hide_viewport = False

        # Select only source hierarchy
        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_objs:
            obj.select_set(True)
        context.view_layer.objects.active = source_obj

        # Duplicate with full copy (not linked)
        bpy.ops.object.duplicate(linked=False)

        # The duplicated objects are now selected
        new_objs = list(context.selected_objects)

        # Find the new cabinet root (the one that was active)
        new_cabinet = context.view_layer.objects.active

        # Restore hidden state on original objects
        for obj_name in hidden_objs:
            if obj_name in bpy.data.objects:
                bpy.data.objects[obj_name].hide_viewport = True

        # Apply same hidden state to duplicated objects
        for new_obj in new_objs:
            # Match hidden state: find the original this was copied from
            # Blender names duplicates as "Name.001", "Name.002", etc.
            base_name = new_obj.name.rsplit('.', 1)[0]
            if base_name in hidden_objs:
                new_obj.hide_viewport = True

        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for name in old_selected:
            if name in bpy.data.objects:
                bpy.data.objects[name].select_set(True)
        if old_active and old_active in bpy.data.objects:
            context.view_layer.objects.active = bpy.data.objects[old_active]

        return new_cabinet

    def remove_cabinet_from_scene(self, cab_obj):
        """Remove a cabinet and all its children from the scene."""
        children = list(cab_obj.children_recursive)
        for child in reversed(children):
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(cab_obj, do_unlink=True)

    def handle_quantity_change(self, context):
        """Add or remove cabinets to match the quantity property."""
        props = context.scene.hb_frameless

        # Add cabinets
        while len(props.calculator_cabinets) < self.quantity:
            last = props.calculator_cabinets[-1]
            if not last.cabinet_obj:
                break
            new_obj = self.duplicate_cabinet(context, last.cabinet_obj)
            if not new_obj:
                break
            # Parent to same parent as source
            new_obj.parent = last.cabinet_obj.parent
            self._added_cabinets.append(new_obj.name)
            cab = props.calculator_cabinets.add()
            cab.cabinet_obj = new_obj
            cab.is_equal = True
            cab.cabinet_width = last.cabinet_width
            if not self.fill_gap:
                self.total_width += last.cabinet_width

        # Remove cabinets (don't go below 1)
        while len(props.calculator_cabinets) > self.quantity and len(props.calculator_cabinets) > 1:
            last_idx = len(props.calculator_cabinets) - 1
            last = props.calculator_cabinets[last_idx]
            if last.cabinet_obj:
                if not self.fill_gap:
                    self.total_width -= last.cabinet_width
                # Only remove from scene if it was added during this session
                if last.cabinet_obj.name in self._added_cabinets:
                    self._added_cabinets.remove(last.cabinet_obj.name)
                    self.remove_cabinet_from_scene(last.cabinet_obj)
                else:
                    self.remove_cabinet_from_scene(last.cabinet_obj)
            props.calculator_cabinets.remove(last_idx)

        self.total_number_of_cabinets = len(props.calculator_cabinets)

    def check(self, context):
        props = context.scene.hb_frameless

        # Handle quantity changes
        if len(props.calculator_cabinets) != self.quantity:
            self.handle_quantity_change(context)

        # Recalculate total width for fill mode
        if self.fill_gap and self.has_wall:
            self.total_width = max(0.01, self.gap_width - self.left_offset - self.right_offset)

        # Calculate Non Equal Cabinet Widths and Number of Equal Cabinets
        self.number_of_equal_cabinets = 0
        self.non_equal_cabinet_widths = 0.0
        for cabinet in props.calculator_cabinets:
            if cabinet.is_equal:
                self.number_of_equal_cabinets += 1
            else:
                self.non_equal_cabinet_widths += cabinet.cabinet_width

        # Calculate Width for All Equal Cabinets
        if self.number_of_equal_cabinets > 0:
            self.equal_cabinet_width = (self.total_width - self.non_equal_cabinet_widths) / self.number_of_equal_cabinets

        # Calculate effective start position
        if self.has_wall:
            if self.fill_gap:
                # Fill mode: offsets are relative to gap boundaries
                if self.is_back_side:
                    effective_start_x = self.gap_right_boundary - self.right_offset
                else:
                    effective_start_x = self.gap_left_boundary + self.left_offset
            else:
                # Non-fill mode: left_offset is absolute X location
                if self.is_back_side:
                    effective_start_x = self.left_offset + self.total_width
                else:
                    effective_start_x = self.left_offset
        else:
            effective_start_x = self.start_x

        # Position cabinets
        current_offset = 0.0
        for cabinet in props.calculator_cabinets:
            if cabinet.cabinet_obj:
                cabinet_cage = hb_types.GeoNodeCage(cabinet.cabinet_obj)
                cab_width = self.equal_cabinet_width if cabinet.is_equal else cabinet.cabinet_width

                if self.has_wall and self.is_back_side:
                    # Back side: direction is -X, start from right
                    cabinet_cage.obj.location.x = effective_start_x - current_offset
                elif self.has_wall:
                    # Front side: direction is +X, start from left
                    cabinet_cage.obj.location.x = effective_start_x + current_offset
                elif self.start_position and self.cabinet_direction:
                    # Island/rotated: use direction vector
                    new_pos = self.start_position + self.cabinet_direction * current_offset
                    cabinet_cage.obj.location.x = new_pos.x
                    cabinet_cage.obj.location.y = new_pos.y
                else:
                    cabinet_cage.obj.location.x = effective_start_x + current_offset

                if cabinet.is_equal:
                    cabinet.cabinet_width = self.equal_cabinet_width
                    cabinet_cage.set_input("Dim X", self.equal_cabinet_width)
                else:
                    cabinet_cage.set_input("Dim X", cabinet.cabinet_width)

                current_offset += cab_width
                hb_utils.run_calc_fix(context, cabinet_cage.obj)
        return True

    def invoke(self, context, event):
        props = context.scene.hb_frameless

        # Reset
        props.calculator_cabinets.clear()
        self._added_cabinets = []
        self.right_offset = 0.0
        self.fill_gap = False

        # Collect Cabinet Objects
        objs = []
        for obj in context.selected_objects:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp and cabinet_bp not in objs:
                objs.append(cabinet_bp)

        if len(objs) < 1:
            self.report({'WARNING'}, "Select at least 1 cabinet to adjust sizes")
            return {'CANCELLED'}

        # Determine if on a wall and which side
        first_parent = objs[0].parent
        self.has_wall = first_parent and first_parent.get('IS_WALL_BP')
        self.wall_obj = first_parent if self.has_wall else None
        self.is_back_side = (abs(objs[0].rotation_euler.z - math.pi) < 0.1 or
                             abs(objs[0].rotation_euler.z + math.pi) < 0.1)

        # Get cabinet direction from first cabinet's rotation
        first_rot = objs[0].rotation_euler.z
        self.cabinet_direction = Vector((math.cos(first_rot), math.sin(first_rot), 0))

        # Sort cabinets by position projected onto the cabinet direction
        def get_position_along_direction(obj):
            pos = Vector((obj.location.x, obj.location.y, 0))
            return pos.dot(self.cabinet_direction)

        objs.sort(key=get_position_along_direction, reverse=False)

        # Store start position
        self.start_position = Vector((objs[0].location.x, objs[0].location.y, objs[0].location.z))
        self.start_x = objs[0].location.x

        # Populate Collection and Set Properties
        self.total_width = 0.0
        for index, obj in enumerate(objs):
            cabinet = hb_types.GeoNodeCage(obj)
            cab = props.calculator_cabinets.add()
            cab.cabinet_obj = cabinet.obj
            cab.is_equal = True
            cab.cabinet_width = cabinet.get_input('Dim X')
            self.total_width += cabinet.get_input('Dim X')

        self.original_total_width = self.total_width
        self.total_number_of_cabinets = len(props.calculator_cabinets)
        self.quantity = self.total_number_of_cabinets

        # Calculate gap boundaries if on a wall
        if self.has_wall:
            self.gap_left_boundary, self.gap_right_boundary = self.calculate_gap_boundaries(
                context, self.wall_obj, objs)
            self.gap_width = self.gap_right_boundary - self.gap_left_boundary

            # Set initial X location from first cabinet's actual position
            if self.is_back_side:
                # Back side: rightmost location.x minus total width
                x_ranges = [self.get_cab_x_range(o) for o in objs]
                self.left_offset = min(r[0] for r in x_ranges)
            else:
                self.left_offset = objs[0].location.x
        else:
            self.left_offset = 0.0

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=450)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        props = context.scene.hb_frameless
        unit_settings = context.scene.unit_settings

        layout = self.layout

        # Quantity row
        box = layout.box()
        row = box.row()
        row.label(text="Cabinets:")
        row.prop(self, 'quantity', text="")

        # Total width
        row = box.row()
        row.label(text="Total Width:")
        row.label(text=units.unit_to_string(unit_settings, self.total_width))

        # Gap info and offsets (only for wall cabinets)
        if self.has_wall:
            row = box.row()
            row.label(text="Available Gap:")
            row.label(text=units.unit_to_string(unit_settings, self.gap_width))

            row = box.row()
            row.prop(self, 'fill_gap', text="Fill Available Space")

            if self.fill_gap:
                row = box.row()
                row.prop(self, 'left_offset', text="Left Offset")
                row.prop(self, 'right_offset', text="Right Offset")
            else:
                row = box.row()
                row.prop(self, 'left_offset', text="X Location")

        # Cabinet list
        box = layout.box()
        for index, cabinet in enumerate(props.calculator_cabinets):
            row = box.row()
            row.label(text='Cabinet ' + str(index + 1))
            row.prop(cabinet, 'is_equal', text="")
            if cabinet.is_equal:
                row.label(text="Width: " + units.unit_to_string(unit_settings, cabinet.cabinet_width))
            else:
                row.prop(cabinet, 'cabinet_width', text="Width:")


class hb_frameless_OT_finish_interior(bpy.types.Operator):
    bl_idname = "hb_frameless.finish_interior"
    bl_label = "Finish Interior"
    bl_description = "Change all interior surfaces of the cabinet to use the finish material"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        if not cabinet_bp:
            self.report({'WARNING'}, "No cabinet found")
            return {'CANCELLED'}

        # Toggle the Finished Interior flag
        is_currently_finished = cabinet_bp.get('Finished Interior', False)
        cabinet_bp['Finished Interior'] = not is_currently_finished

        # Get the cabinet style
        style_index = cabinet_bp.get('CABINET_STYLE_INDEX', 0)
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        if len(props.cabinet_styles) == 0:
            self.report({'WARNING'}, "No cabinet styles defined")
            return {'CANCELLED'}

        if style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[style_index]
        else:
            style = props.cabinet_styles[0]

        finish_mat, finish_mat_rotated = style.get_finish_material()
        interior_mat, interior_mat_rotated = style.get_interior_material()

        if cabinet_bp['Finished Interior']:
            # Apply finish material to all surfaces
            for child in cabinet_bp.children_recursive:
                if 'CABINET_PART' in child:
                    part = hb_types.GeoNodeObject(child)
                    part.set_input("Top Surface", finish_mat)
                    part.set_input("Bottom Surface", finish_mat)
                    part.set_input("Edge W1", finish_mat_rotated)
                    part.set_input("Edge W2", finish_mat_rotated)
                    part.set_input("Edge L1", finish_mat_rotated)
                    part.set_input("Edge L2", finish_mat_rotated)

                    # Also update Material input on any cabinet part modifiers
                    for mod in child.modifiers:
                        if mod.type == 'NODES' and mod.node_group:
                            if 'Material' in mod.node_group.interface.items_tree:
                                node_input = mod.node_group.interface.items_tree['Material']
                                mod[node_input.identifier] = finish_mat

            self.report({'INFO'}, "Cabinet interior finished")
        else:
            # Revert: use assign_style_to_cabinet logic (respects Finish Top/Bottom per part)
            style.assign_style_to_cabinet(cabinet_bp)
            self.report({'INFO'}, "Cabinet interior reverted to standard materials")

        return {'FINISHED'}


classes = (
    hb_frameless_OT_adjust_multiple_cabinet_widths,
    hb_frameless_OT_cabinet_prompts,
    hb_frameless_OT_drop_cabinet_to_countertop,
    hb_frameless_OT_add_applied_end,
    hb_frameless_OT_remove_applied_end,
    hb_frameless_OT_delete_cabinet,
    hb_frameless_OT_create_cabinet_group,
    hb_frameless_OT_select_cabinet_group,
    hb_frameless_OT_finish_interior,
)

register, unregister = bpy.utils.register_classes_factory(classes)
