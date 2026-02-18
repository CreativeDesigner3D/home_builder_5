import bpy
import math
import os
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_details, hb_types, units

class hb_frameless_OT_create_crown_detail(bpy.types.Operator):
    """Create a new crown molding detail"""
    bl_idname = "hb_frameless.create_crown_detail"
    bl_label = "Create Crown Detail"
    bl_description = "Create a new crown molding detail with a 2D profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Name for the crown detail",
        default="Crown Detail"
    )  # type: ignore
    
    
    def execute(self, context):

        # Get main scene props
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create a new crown detail entry
        crown = props.crown_details.add()
        crown.name = self.name

        # Create a detail scene for the crown profile
        detail = hb_details.DetailView()
        scene = detail.create(f"Crown - {self.name}")
        scene['IS_CROWN_DETAIL'] = True
        
        # Store the scene name reference
        crown.detail_scene_name = scene.name
        
        # Set as active
        props.active_crown_detail_index = len(props.crown_details) - 1
        
        # Set crown detail defaults
        hb_scene = scene.home_builder
        hb_scene.annotation_line_thickness = units.inch(0.02)
        
        # Set Calibri font as default if available
        for font in bpy.data.fonts:
            if 'calibri' in font.name.lower():
                hb_scene.annotation_font = font
                break
        
        # Draw a cabinet side detail as starting point to add crown molding details to
        self._draw_cabinet_side_detail(context, scene, props)
        
        # Switch to the detail scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        self.report({'INFO'}, f"Created crown detail: {self.name}")
        return {'FINISHED'}
    
    def _draw_cabinet_side_detail(self, context, scene, props):
        """Draw the top-front corner of cabinet side profile (4 inch section)."""

        # Make sure we're in the right scene
        original_scene = context.scene
        context.window.scene = scene
        
        # Get cabinet dimensions from props
        part_thickness = props.default_carcass_part_thickness
        door_to_cab_gap = units.inch(0.125) # Standard door gap TODO: look to frameless props for this
        door_overlay = part_thickness - units.inch(.0625) # Standard door overlay TODO: look to cabinet style door overlay
        door_thickness = units.inch(0.75)  # Standard door thickness
        
        # Only show 4" of the corner
        corner_size = units.inch(4)
        
        # Position the detail so the top-front corner of the cabinet side is at origin
        # -X axis goes toward the back (depth), +Y axis goes up (height)
        # Origin (0,0) is at the top-front corner of the cabinet side panel
        
        hb_scene = scene.home_builder

        # Draw cabinet side profile - L-shaped corner section
        side_profile = hb_details.GeoNodePolyline()
        side_profile.create("Cabinet Side")
        # Start at bottom of visible section (4" down from top)
        side_profile.set_point(0, Vector((0, -corner_size, 0)))
        # Go up to top-front corner
        side_profile.add_point(Vector((0, 0, 0)))
        # Go back along top edge (4" toward back)
        side_profile.add_point(Vector((-corner_size, 0, 0)))
        
        # Draw top panel - just the front portion visible in the corner
        top_panel = hb_details.GeoNodePolyline()
        top_panel.create("Cabinet Top")
        # Draw single line to show the top panel
        top_panel.set_point(0, Vector((0, -part_thickness, 0)))
        top_panel.add_point(Vector((-corner_size, -part_thickness, 0)))
        
        # Draw door profile - just the top portion visible in the corner
        door_profile = hb_details.GeoNodePolyline()
        door_profile.create("Door Face")
        # Draw U Shape Door Profile for the corner
        door_profile.set_point(0, Vector((door_to_cab_gap, -corner_size, 0)))
        door_profile.add_point(Vector((door_to_cab_gap, -part_thickness+door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap+door_thickness, -part_thickness+door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap+door_thickness, -corner_size, 0)))

        # --- CLEARANCE DIMENSION ---
        # Vertical dimension from top of cabinet (Y=0) to ceiling line
        top_clearance = props.default_top_cabinet_clearance
        clearance_dim = hb_types.GeoNodeDimension()
        clearance_dim.create("Clearance Dimension")
        clearance_dim.obj.location = Vector((-corner_size - units.inch(0.5), 0, 0))
        clearance_dim.obj.rotation_euler.z = math.pi / 2  # Vertical
        clearance_dim.obj.data.splines[0].points[1].co = (top_clearance, 0, 0, 1)
        clearance_dim.set_input("Leader Length", units.inch(-0.5))
        clearance_dim.set_decimal()
        
        # --- CEILING LINE ---
        # Get ceiling height and top cabinet clearance
        main_scene_hb = hb_project.get_main_scene().home_builder
        ceiling_height = main_scene_hb.ceiling_height
        top_clearance = props.default_top_cabinet_clearance
        
        # Ceiling line is at top_clearance above the top of the cabinet (Y=0)
        ceiling_y = top_clearance
        
        # Draw ceiling line spanning the detail width
        detail_left = -corner_size - units.inch(1)
        detail_right = door_to_cab_gap + door_thickness + units.inch(2)
        
        ceiling_line = hb_details.GeoNodePolyline()
        ceiling_line.create("Ceiling Line")
        ceiling_line.set_point(0, Vector((detail_left, ceiling_y, 0)))
        ceiling_line.add_point(Vector((detail_right, ceiling_y, 0)))
        
        # Add ceiling height label
        ceiling_height_inches = round(ceiling_height / units.inch(1))
        ceiling_text = hb_details.GeoNodeText()
        ceiling_text.create("Ceiling Label", f'CEILING HT. {ceiling_height_inches}"', hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            ceiling_text.obj.data.font = hb_scene.annotation_font
        ceiling_text.set_location(Vector((detail_right + units.inch(0.25), ceiling_y, 0)))
        ceiling_text.set_alignment('LEFT', 'CENTER')
        
        # --- DOOR OVERLAY LABEL ---
        # Get overlay type from active cabinet style
        overlay_type_text = "FULL OVERLAY"
        if props.cabinet_styles:
            style_index = props.active_cabinet_style_index
            if style_index < len(props.cabinet_styles):
                style = props.cabinet_styles[style_index]
                overlay_type = style.door_overlay_type
                if overlay_type == 'FULL':
                    overlay_type_text = "FULL OVERLAY"
                elif overlay_type == 'HALF':
                    overlay_type_text = "HALF OVERLAY"
                elif overlay_type == 'INSET':
                    overlay_type_text = "INSET"
        
        # Draw leader line pointing to the door
        door_center_x = door_to_cab_gap + door_thickness / 2
        door_mid_y = (-part_thickness + door_overlay + (-corner_size)) / 2
        leader_end_x = door_to_cab_gap + door_thickness + units.inch(2)
        
        door_leader = hb_details.GeoNodePolyline()
        door_leader.create("Door Overlay Leader")
        door_leader.set_point(0, Vector((door_center_x, door_mid_y, 0)))
        door_leader.add_point(Vector((leader_end_x, door_mid_y, 0)))
        
        # Add overlay type text at end of leader
        overlay_text = hb_details.GeoNodeText()
        overlay_text.create("Door Overlay Label", overlay_type_text, hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            overlay_text.obj.data.font = hb_scene.annotation_font
        overlay_text.set_location(Vector((leader_end_x + units.inch(0.25), door_mid_y, 0)))
        overlay_text.set_alignment('LEFT', 'CENTER')

        # Add a label/text annotation
        text = hb_details.GeoNodeText()
        text.create("Label", "CROWN DETAIL", hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            text.obj.data.font = hb_scene.annotation_font
        text.set_location(Vector((0, -corner_size - units.inch(1), 0)))
        text.set_alignment('CENTER', 'TOP')
        
        # Switch back to original scene
        context.window.scene = original_scene


class hb_frameless_OT_delete_crown_detail(bpy.types.Operator):
    """Delete the selected crown detail"""
    bl_idname = "hb_frameless.delete_crown_detail"
    bl_label = "Delete Crown Detail"
    bl_description = "Delete the selected crown molding detail and its profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.crown_details) > 0
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.crown_details:
            self.report({'WARNING'}, "No crown details to delete")
            return {'CANCELLED'}
        
        index = props.active_crown_detail_index
        crown = props.crown_details[index]
        
        # Delete the associated detail scene if it exists
        detail_scene = crown.get_detail_scene()
        if detail_scene:
            # Make sure we're not deleting the current scene
            if context.scene == detail_scene:
                # Switch to main scene first
                context.window.scene = main_scene
            
            bpy.data.scenes.remove(detail_scene)
        
        # Remove from collection
        crown_name = crown.name
        props.crown_details.remove(index)
        
        # Update active index
        if props.active_crown_detail_index >= len(props.crown_details):
            props.active_crown_detail_index = max(0, len(props.crown_details) - 1)
        
        self.report({'INFO'}, f"Deleted crown detail: {crown_name}")
        return {'FINISHED'}


class hb_frameless_OT_edit_crown_detail(bpy.types.Operator):
    """Edit the selected crown detail profile"""
    bl_idname = "hb_frameless.edit_crown_detail"
    bl_label = "Edit Crown Detail"
    bl_description = "Open the crown detail profile scene for editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.crown_details) == 0:
            return False
        crown = props.crown_details[props.active_crown_detail_index]
        return crown.get_detail_scene() is not None
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        crown = props.crown_details[props.active_crown_detail_index]
        detail_scene = crown.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Crown detail scene not found")
            return {'CANCELLED'}
        
        # Switch to the detail scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=detail_scene.name)
        
        self.report({'INFO'}, f"Editing crown detail: {crown.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_crown_to_cabinets(bpy.types.Operator):
    """Assign the selected crown detail to selected cabinets"""
    bl_idname = "hb_frameless.assign_crown_to_cabinets"
    bl_label = "Assign Crown to Cabinets"
    bl_description = "Create crown molding extrusions on selected cabinets using the active crown detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.crown_details) == 0:
            return False
        # Check if any cabinets are selected
        for obj in context.selected_objects:
            if obj.get('IS_CABINET_BP') or obj.get('IS_FRAMELESS_CABINET_CAGE'):
                return True
        return False
    
    def execute(self, context):
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        crown = props.crown_details[props.active_crown_detail_index]
        detail_scene = crown.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Crown detail scene not found")
            return {'CANCELLED'}
        
        # Get all molding profiles and solid lumber from the detail scene
        profiles = []
        for obj in detail_scene.objects:
            if obj.get('IS_MOLDING_PROFILE') or obj.get('IS_SOLID_LUMBER'):
                profiles.append(obj)
        
        if not profiles:
            self.report({'WARNING'}, "No molding profiles or solid lumber found in crown detail")
            return {'CANCELLED'}
        
        # Collect unique cabinets from selection (only UPPER and TALL get crown)
        cabinets = []
        for obj in context.selected_objects:
            cabinet_bp = None
            if obj.get('IS_CABINET_BP') or obj.get('IS_FRAMELESS_CABINET_CAGE'):
                cabinet_bp = obj
            elif obj.parent:
                if obj.parent.get('IS_CABINET_BP') or obj.parent.get('IS_FRAMELESS_CABINET_CAGE'):
                    cabinet_bp = obj.parent
            
            if cabinet_bp and cabinet_bp not in cabinets:
                cab_type = cabinet_bp.get('CABINET_TYPE', '')
                if cab_type in ('UPPER', 'TALL'):
                    cabinets.append(cabinet_bp)
        
        if not cabinets:
            self.report({'WARNING'}, "No valid upper or tall cabinets selected")
            return {'CANCELLED'}
        
        # Remove any existing crown molding on selected cabinets
        for cabinet in cabinets:
            self._remove_existing_crown(cabinet)
            cabinet['CROWN_DETAIL_NAME'] = crown.name
            cabinet['CROWN_DETAIL_SCENE'] = crown.detail_scene_name
        
        # Get all walls and all cabinets in current scene for adjacency detection
        current_scene = context.scene
        all_walls = [o for o in current_scene.objects if o.get('IS_WALL_BP') or o.get('IS_WALL')]
        all_cabinets = [o for o in current_scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE')]
        
        # Analyze cabinet adjacency and group connected cabinets
        cabinet_groups = self._group_adjacent_cabinets(cabinets, all_cabinets, all_walls)
        
        # Create crown molding for each group
        for group in cabinet_groups:
            for profile in profiles:
                self._create_crown_for_group(context, group, profile, all_walls, all_cabinets, current_scene)
        
        total_cabs = sum(len(g['cabinets']) for g in cabinet_groups)
        self.report({'INFO'}, f"Created crown molding on {total_cabs} cabinet(s) in {len(cabinet_groups)} group(s)")
        return {'FINISHED'}
    
    def _remove_existing_crown(self, cabinet):
        """Remove any existing crown molding children from the cabinet."""
        children_to_remove = []
        for child in cabinet.children:
            if child.get('IS_CROWN_MOLDING') or child.get('IS_CROWN_PROFILE_COPY'):
                children_to_remove.append(child)
        
        for child in children_to_remove:
            bpy.data.objects.remove(child, do_unlink=True)
    
    def _get_cabinet_bounds(self, cabinet):
        """Get world-space bounds of a cabinet using evaluated bounding box corners."""
        matrix = cabinet.matrix_world
        
        # Use evaluated object to get proper bound_box for geometry node objects
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = cabinet.evaluated_get(depsgraph)
        
        # Transform all bounding box corners to world space
        world_corners = [matrix @ Vector(corner) for corner in eval_obj.bound_box]
        
        # Find min/max in each axis
        xs = [c.x for c in world_corners]
        ys = [c.y for c in world_corners]
        zs = [c.z for c in world_corners]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        
        return {
            'left_x': min_x,
            'right_x': max_x,
            'front_y': min_y,
            'back_y': max_y,
            'bottom_z': min_z,
            'top_z': max_z,
            'width': max_x - min_x,
            'depth': max_y - min_y,
            'height': max_z - min_z,
        }
    
    def _is_against_wall(self, cabinet, side, walls, tolerance=0.05):
        """Check if cabinet side is against a wall.
        
        Uses world-space bounding boxes for both cabinet and wall to handle
        rotated walls. 'side' is relative to the cabinet arrangement:
          'left' = start of run, 'right' = end of run, 'back' = wall side
        """
        bounds = self._get_cabinet_bounds(cabinet)
        axis = self._get_wall_direction(cabinet)
        
        for wall in walls:
            # Use world-space bounding box for rotated walls
            from mathutils import Vector
            corners = [wall.matrix_world @ Vector(c) for c in wall.bound_box]
            wxs = [c.x for c in corners]
            wys = [c.y for c in corners]
            w_min_x, w_max_x = min(wxs), max(wxs)
            w_min_y, w_max_y = min(wys), max(wys)
            w_thickness_x = w_max_x - w_min_x
            w_thickness_y = w_max_y - w_min_y
            
            if side == 'left':
                if axis == 'X':
                    # Left = min X edge; wall should be thin in X (perpendicular wall)
                    if w_thickness_x < 0.2:
                        if (abs(bounds['left_x'] - w_max_x) < tolerance or 
                            abs(bounds['left_x'] - w_min_x) < tolerance):
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
                else:
                    # Y-axis run: left = max Y (start); wall should be thin in Y (perpendicular wall)
                    if w_thickness_y < 0.2:
                        if (abs(bounds['back_y'] - w_max_y) < tolerance or 
                            abs(bounds['back_y'] - w_min_y) < tolerance):
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
            
            elif side == 'right':
                if axis == 'X':
                    # Right = max X edge; wall should be thin in X
                    if w_thickness_x < 0.2:
                        if (abs(bounds['right_x'] - w_min_x) < tolerance or 
                            abs(bounds['right_x'] - w_max_x) < tolerance):
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
                else:
                    # Y-axis run: right = min Y (end); wall should be thin in Y
                    if w_thickness_y < 0.2:
                        if (abs(bounds['front_y'] - w_min_y) < tolerance or 
                            abs(bounds['front_y'] - w_max_y) < tolerance):
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
            
            elif side == 'back':
                if axis == 'X':
                    # Back = max Y; wall thin in Y
                    if w_thickness_y < 0.2:
                        if abs(bounds['back_y'] - w_min_y) < tolerance or abs(bounds['back_y'] - w_max_y) < tolerance:
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
                else:
                    # Y-axis: back = max X; wall thin in X
                    if w_thickness_x < 0.2:
                        if abs(bounds['right_x'] - w_min_x) < tolerance or abs(bounds['right_x'] - w_max_x) < tolerance:
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
        
        return False
    
    def _get_wall_direction(self, cabinet):
        """Get the wall direction for a cabinet. Returns 'X' or 'Y'."""
        if cabinet.parent and (cabinet.parent.get('IS_WALL_BP') or cabinet.parent.get('IS_WALL')):
            wall_rot_z = cabinet.parent.rotation_euler.z
            import math
            # If wall is rotated ~90 or ~270 degrees, cabinets run along Y
            angle = abs(wall_rot_z) % math.pi
            if abs(angle - math.pi/2) < 0.1:
                return 'Y'
        return 'X'
    
    def _find_adjacent_cabinet(self, cabinet, side, all_cabinets, tolerance=0.02):
        """Find a cabinet adjacent to the given side. Works for both X and Y arrangements."""
        bounds = self._get_cabinet_bounds(cabinet)
        cab_type = cabinet.get('CABINET_TYPE', '')
        axis = self._get_wall_direction(cabinet)
        
        for other in all_cabinets:
            if other == cabinet:
                continue
            
            other_bounds = self._get_cabinet_bounds(other)
            other_type = other.get('CABINET_TYPE', '')
            
            # Only consider UPPER and TALL cabinets for crown
            if other_type not in ('UPPER', 'TALL'):
                continue
            
            # Check if tops are at same height (with tolerance)
            if abs(bounds['top_z'] - other_bounds['top_z']) > tolerance:
                continue
            
            if axis == 'X':
                if side == 'left':
                    if abs(other_bounds['right_x'] - bounds['left_x']) < tolerance:
                        return other
                elif side == 'right':
                    if abs(other_bounds['left_x'] - bounds['right_x']) < tolerance:
                        return other
            else:  # Y axis
                if side == 'left':
                    # "Left" = the end with higher Y (start of run)
                    if abs(other_bounds['front_y'] - bounds['back_y']) < tolerance:
                        return other
                elif side == 'right':
                    # "Right" = the end with lower Y (end of run)
                    if abs(other_bounds['back_y'] - bounds['front_y']) < tolerance:
                        return other
        
        return None
    
    def _group_adjacent_cabinets(self, selected_cabinets, all_cabinets, walls):
        """Group selected cabinets that are adjacent to each other."""
        if not selected_cabinets:
            return []
        
        # Determine arrangement axis from first cabinet's wall
        axis = self._get_wall_direction(selected_cabinets[0])
        
        # Sort cabinets by position along the arrangement axis
        if axis == 'X':
            sorted_cabs = sorted(selected_cabinets, key=lambda c: self._get_cabinet_bounds(c)['left_x'])
        else:
            # For Y axis, sort by back_y descending (highest Y = start of run)
            sorted_cabs = sorted(selected_cabinets, key=lambda c: self._get_cabinet_bounds(c)['back_y'], reverse=True)
        
        groups = []
        used = set()
        
        for cabinet in sorted_cabs:
            if cabinet in used:
                continue
            
            # Start a new group
            group_cabs = [cabinet]
            used.add(cabinet)
            
            # Find all connected cabinets to the right (end of run)
            current = cabinet
            while True:
                right_neighbor = self._find_adjacent_cabinet(current, 'right', all_cabinets)
                if right_neighbor and right_neighbor in selected_cabinets and right_neighbor not in used:
                    group_cabs.append(right_neighbor)
                    used.add(right_neighbor)
                    current = right_neighbor
                else:
                    break
            
            # Analyze group
            first_cab = group_cabs[0]
            last_cab = group_cabs[-1]
            
            # Check wall adjacency
            left_against_wall = self._is_against_wall(first_cab, 'left', walls)
            right_against_wall = self._is_against_wall(last_cab, 'right', walls)
            
            # Check if there's an unselected adjacent cabinet (for returns)
            left_adjacent = self._find_adjacent_cabinet(first_cab, 'left', all_cabinets)
            right_adjacent = self._find_adjacent_cabinet(last_cab, 'right', all_cabinets)
            
            groups.append({
                'cabinets': group_cabs,
                'left_wall': left_against_wall,
                'right_wall': right_against_wall,
                'left_adjacent': left_adjacent,
                'right_adjacent': right_adjacent,
                'axis': axis,
            })
        
        return groups
    
    def _get_wall_aligned_bounds(self, bounds, axis):
        """Map world-space bounds to wall-aligned coordinates.
        
        Returns dict with:
            along_start: Start position along the wall (left/first end)
            along_end: End position along the wall (right/last end)  
            front: Front face position (into room)
            back: Back face position (against wall)
            depth: Cabinet depth (back - front for X, or right_x - left_x for Y)
        
        For X-axis walls: along=X, depth=Y (front=min_y, back=max_y)
        For Y-axis walls: along=-Y, depth=-X (front=min_x, back=max_x)
        """
        if axis == 'X':
            return {
                'along_start': bounds['left_x'],
                'along_end': bounds['right_x'],
                'front': bounds['front_y'],
                'back': bounds['back_y'],
                'depth': bounds['back_y'] - bounds['front_y'],
            }
        else:  # Y axis - wall runs along -Y
            return {
                'along_start': bounds['back_y'],   # High Y = start of run
                'along_end': bounds['front_y'],     # Low Y = end of run
                'front': bounds['left_x'],          # Min X = front (into room)
                'back': bounds['right_x'],          # Max X = back (wall)
                'depth': bounds['right_x'] - bounds['left_x'],
            }
    
    def _make_world_point(self, along, depth, axis):
        """Convert wall-aligned (along, depth) coordinates to world XY point.
        
        For X-axis: along=X, depth=Y → (along, depth, 0)
        For Y-axis: along=Y, depth=X → (depth, along, 0)
        """
        if axis == 'X':
            return Vector((along, depth, 0))
        else:
            return Vector((depth, along, 0))
    
    def _create_crown_for_group(self, context, group, profile, walls, all_cabinets, target_scene):
        """Create crown molding extrusion for a group of cabinets."""
        
        cabinets = group['cabinets']
        first_cab = cabinets[0]
        last_cab = cabinets[-1]
        axis = group.get('axis', 'X')
        
        profile_offset_x = profile.location.x  # Depth offset (positive = forward)
        profile_offset_y = profile.location.y  # Height offset
        
        # Copy the profile curve
        profile_copy = profile.copy()
        profile_copy.data = profile.data.copy()
        target_scene.collection.objects.link(profile_copy)
        
        profile_copy.location = (0, 0, 0)
        profile_copy.rotation_euler = (0, 0, 0)
        profile_copy.scale = (1, 1, 1)
        profile_copy.data.dimensions = '2D'
        profile_copy.data.bevel_depth = 0
        profile_copy.data.fill_mode = 'NONE'
        profile_copy.hide_viewport = True
        profile_copy.hide_render = True
        profile_copy.name = f"Crown_Profile_{profile.name}"
        profile_copy['IS_CROWN_PROFILE_COPY'] = True
        
        # Build path points in WORLD coordinates
        world_points = []
        
        first_bounds = self._get_cabinet_bounds(first_cab)
        last_bounds = self._get_cabinet_bounds(last_cab)
        
        # Get wall-aligned bounds
        first_wb = self._get_wall_aligned_bounds(first_bounds, axis)
        last_wb = self._get_wall_aligned_bounds(last_bounds, axis)
        
        # Calculate profile adjustments
        if profile_offset_x < 0:
            inset = abs(profile_offset_x)
            extend = 0
        else:
            inset = 0
            extend = profile_offset_x
        
        # Along-wall sign: +1 for X (increasing), -1 for Y (decreasing)
        a_sign = 1 if axis == 'X' else -1
        
        # === LEFT SIDE (start of run) ===
        if group['left_wall']:
            start_along = first_wb['along_start'] + a_sign * inset
            world_points.append(self._make_world_point(start_along, first_wb['front'] - extend + inset, axis))
        elif group['left_adjacent']:
            adj_bounds = self._get_cabinet_bounds(group['left_adjacent'])
            adj_wb = self._get_wall_aligned_bounds(adj_bounds, axis)
            adj_type = group['left_adjacent'].get('CABINET_TYPE', '')
            
            start_along = first_wb['along_start'] + a_sign * inset
            
            if adj_type == 'TALL' and first_cab.get('CABINET_TYPE') == 'UPPER':
                world_points.append(self._make_world_point(start_along, adj_wb['front'] - extend + inset, axis))
            
            world_points.append(self._make_world_point(start_along, first_wb['front'] - extend + inset, axis))
        else:
            back_along = first_wb['along_start'] + a_sign * inset - a_sign * extend
            world_points.append(self._make_world_point(back_along, first_wb['back'], axis))
            world_points.append(self._make_world_point(back_along, first_wb['front'] - extend + inset, axis))
        
        # === MIDDLE - transitions between cabinets ===
        for i in range(len(cabinets) - 1):
            current_cab = cabinets[i]
            next_cab = cabinets[i + 1]
            current_bounds = self._get_cabinet_bounds(current_cab)
            next_bounds = self._get_cabinet_bounds(next_cab)
            current_wb = self._get_wall_aligned_bounds(current_bounds, axis)
            next_wb = self._get_wall_aligned_bounds(next_bounds, axis)
            
            current_type = current_cab.get('CABINET_TYPE', '')
            next_type = next_cab.get('CABINET_TYPE', '')
            
            trans_along = current_wb['along_end']
            
            depth_diff = abs(current_wb['depth'] - next_wb['depth'])
            
            if depth_diff > 0.01:
                if current_type == 'TALL' and next_type == 'UPPER':
                    trans_adj = trans_along - a_sign * inset + a_sign * extend
                    world_points.append(self._make_world_point(trans_adj, current_wb['front'] - extend + inset, axis))
                    world_points.append(self._make_world_point(trans_adj, next_wb['front'] - extend + inset, axis))
                elif current_type == 'UPPER' and next_type == 'TALL':
                    trans_adj = trans_along + a_sign * inset - a_sign * extend
                    world_points.append(self._make_world_point(trans_adj, current_wb['front'] - extend + inset, axis))
                    world_points.append(self._make_world_point(trans_adj, next_wb['front'] - extend + inset, axis))
        
        # === RIGHT SIDE (end of run) ===
        if group['right_wall']:
            end_along = last_wb['along_end'] - a_sign * inset
            world_points.append(self._make_world_point(end_along, last_wb['front'] - extend + inset, axis))
        elif group['right_adjacent']:
            adj_bounds = self._get_cabinet_bounds(group['right_adjacent'])
            adj_wb = self._get_wall_aligned_bounds(adj_bounds, axis)
            adj_type = group['right_adjacent'].get('CABINET_TYPE', '')
            
            end_along = last_wb['along_end'] - a_sign * inset
            
            world_points.append(self._make_world_point(end_along, last_wb['front'] - extend + inset, axis))
            
            if adj_type == 'TALL' and last_cab.get('CABINET_TYPE') == 'UPPER':
                world_points.append(self._make_world_point(end_along, adj_wb['front'] - extend + inset, axis))
        else:
            back_along = last_wb['along_end'] - a_sign * inset + a_sign * extend
            world_points.append(self._make_world_point(back_along, last_wb['front'] - extend + inset, axis))
            world_points.append(self._make_world_point(back_along, last_wb['back'], axis))
        
        # Convert world points to local coordinates relative to first cabinet
        first_inv = first_cab.matrix_world.inverted()
        local_points = []
        for pt in world_points:
            local_pt = first_inv @ pt
            local_points.append(Vector((local_pt.x, local_pt.y, 0)))
        
        # Create the curve
        curve_data = bpy.data.curves.new(name=f"Crown_Path_{profile.name}", type='CURVE')
        curve_data.dimensions = '2D'
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = profile_copy
        curve_data.use_fill_caps = True
        
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(local_points) - 1)
        
        for i, pt in enumerate(local_points):
            spline.points[i].co = (pt.x, pt.y, pt.z, 1)
        
        crown_obj = bpy.data.objects.new(f"Crown_{profile.name}", curve_data)
        target_scene.collection.objects.link(crown_obj)
        
        # Parent to first cabinet
        crown_obj.parent = first_cab
        crown_obj.location = (0, 0, first_bounds['height'] + profile_offset_y)
        crown_obj['IS_CROWN_MOLDING'] = True
        crown_obj['CROWN_PROFILE_NAME'] = profile.name
        
        # Add Smooth by Angle modifier
        smooth_mod = crown_obj.modifiers.new(name="Smooth by Angle", type='NODES')
        if "Smooth by Angle" not in bpy.data.node_groups:
            essentials_path = os.path.join(
                bpy.utils.resource_path('LOCAL'),
                "datafiles", "assets", "nodes", "geometry_nodes_essentials.blend"
            )
            if os.path.exists(essentials_path):
                with bpy.data.libraries.load(essentials_path) as (data_from, data_to):
                    if "Smooth by Angle" in data_from.node_groups:
                        data_to.node_groups = ["Smooth by Angle"]
        if "Smooth by Angle" in bpy.data.node_groups:
            smooth_mod.node_group = bpy.data.node_groups["Smooth by Angle"]
        
        profile_copy.parent = crown_obj
        profile_copy['IS_CROWN_PROFILE_COPY'] = True
        
        # Assign cabinet style material to crown
        style_index = first_cab.get('CABINET_STYLE_INDEX', 0)
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if props.cabinet_styles and style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[style_index]
            material, _ = style.get_finish_material()
            if material:
                if len(crown_obj.data.materials) == 0:
                    crown_obj.data.materials.append(material)
                else:
                    crown_obj.data.materials[0] = material
        
        return crown_obj


def get_bundled_molding_path():
    """Get the path to the bundled molding library folder."""
    frameless_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(frameless_dir, "frameless_assets", "moldings")


def get_all_molding_paths():
    """Get all molding library paths (bundled + user libraries with moldings/ subfolder)."""
    from .... import hb_assets
    return hb_assets.get_all_subfolder_paths("moldings", get_bundled_molding_path())


def get_molding_categories():
    """Get list of molding categories (subfolders) across all library paths."""
    categories_set = set()
    for moldings_path in get_all_molding_paths():
        if os.path.exists(moldings_path):
            for folder in os.listdir(moldings_path):
                folder_path = os.path.join(moldings_path, folder)
                if os.path.isdir(folder_path):
                    categories_set.add(folder)
    categories = [(c, c, c) for c in sorted(categories_set)]
    return categories if categories else [('NONE', "No Categories", "No molding categories found")]


def get_molding_items(category):
    """Get list of molding items in a category across all library paths."""
    items = []
    seen_names = set()
    for moldings_path in get_all_molding_paths():
        category_path = os.path.join(moldings_path, category)
        if os.path.exists(category_path):
            for f in sorted(os.listdir(category_path)):
                if f.endswith('.blend'):
                    name = os.path.splitext(f)[0]
                    if name not in seen_names:
                        seen_names.add(name)
                        filepath = os.path.join(category_path, f)
                        thumb_path = os.path.join(category_path, name + '.png')
                        items.append({
                            'name': name,
                            'filepath': filepath,
                            'thumbnail': thumb_path if os.path.exists(thumb_path) else None
                        })
    return items


class hb_frameless_OT_add_molding_profile(bpy.types.Operator):
    """Add a molding profile from the library to the current detail scene"""
    bl_idname = "hb_frameless.add_molding_profile"
    bl_label = "Add Molding Profile"
    bl_description = "Add a molding profile from the library to the current crown detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="Filepath",
        description="Path to the molding blend file"
    )  # type: ignore
    
    molding_name: bpy.props.StringProperty(
        name="Name",
        description="Name of the molding"
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        # Must be in a crown detail scene
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def execute(self, context):
        
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"Molding file not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Load the molding profile from the blend file
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        # Link the loaded objects to the current scene
        imported_objects = []
        for obj in data_to.objects:
            if obj is not None:
                context.scene.collection.objects.link(obj)
                imported_objects.append(obj)
                
                # Mark as molding profile
                obj['IS_MOLDING_PROFILE'] = True
                obj['MOLDING_NAME'] = self.molding_name
                
                # Apply scene annotation settings if it's a curve
                if obj.type == 'CURVE':
                    hb_scene = context.scene.home_builder
                    obj.data.bevel_depth = hb_scene.annotation_line_thickness
                    color = tuple(hb_scene.annotation_line_color) + (1.0,)
                    obj.color = color
        
        # Select the imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in imported_objects:
            obj.select_set(True)
        
        if imported_objects:
            context.view_layer.objects.active = imported_objects[0]
            # Position at origin for user to move
            for obj in imported_objects:
                obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"Added molding profile: {self.molding_name}")
        return {'FINISHED'}


class hb_frameless_OT_add_solid_lumber(bpy.types.Operator):
    """Add a custom solid lumber profile to the detail"""
    bl_idname = "hb_frameless.add_solid_lumber"
    bl_label = "Add Solid Lumber"
    bl_description = "Add a custom solid lumber rectangle profile to the current detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Thickness of the lumber",
        default=0.01905,  # 0.75 inches
        min=0.001,
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    width: bpy.props.FloatProperty(
        name="Width",
        description="Width of the lumber",
        default=0.0381,  # 1.5 inches
        min=0.001,
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    orientation: bpy.props.EnumProperty(
        name="Orientation",
        description="Orientation of the lumber profile",
        items=[
            ('HORIZONTAL', "Horizontal", "Add lumber as a horizontal part"),
            ('VERTICAL', "Vertical", "Add lumber as a vertical part"),
        ],
        default='HORIZONTAL'
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        # Must be in a detail view scene
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "thickness")
        layout.prop(self, "width")
        
        layout.separator()
        layout.label(text="Orientation:")
        layout.prop(self, "orientation", expand=True)
    
    def execute(self, context):
        scene = context.scene
        hb_scene = scene.home_builder
        
        # Determine dimensions based on orientation
        if self.orientation == 'HORIZONTAL':
            rect_width = self.width
            rect_height = self.thickness
        else:  # VERTICAL
            rect_width = self.thickness
            rect_height = self.width
        
        # Create a rectangle polyline for the lumber profile
        lumber = hb_details.GeoNodePolyline()
        lumber.create("Solid Lumber")
        
        # Draw rectangle starting at origin
        lumber.set_point(0, Vector((0, 0, 0)))
        lumber.add_point(Vector((rect_width, 0, 0)))
        lumber.add_point(Vector((rect_width, rect_height, 0)))
        lumber.add_point(Vector((0, rect_height, 0)))
        lumber.close()
        
        # Mark as solid lumber
        lumber.obj['IS_SOLID_LUMBER'] = True
        lumber.obj['LUMBER_THICKNESS'] = self.thickness
        lumber.obj['LUMBER_WIDTH'] = self.width
        lumber.obj['LUMBER_ORIENTATION'] = self.orientation
        
        # Select the new object
        bpy.ops.object.select_all(action='DESELECT')
        lumber.obj.select_set(True)
        context.view_layer.objects.active = lumber.obj
        
        # Report dimensions in inches for user feedback
        thickness_in = self.thickness * 39.3701
        width_in = self.width * 39.3701
        self.report({'INFO'}, f"Added {thickness_in:.2f}\" x {width_in:.2f}\" solid lumber ({self.orientation.lower()})")
        
        return {'FINISHED'}


class hb_frameless_OT_browse_molding_library(bpy.types.Operator):
    """Browse and add molding profiles from the library"""
    bl_idname = "hb_frameless.browse_molding_library"
    bl_label = "Molding Library"
    bl_description = "Browse molding profiles and add them to the current detail"
    bl_options = {'REGISTER'}
    
    category: bpy.props.EnumProperty(
        name="Category",
        description="Molding category",
        items=lambda self, context: get_molding_categories()
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # Category selector
        layout.prop(self, "category", text="Category")
        
        layout.separator()
        
        # Get items in selected category
        items = get_molding_items(self.category)
        
        if not items:
            layout.label(text="No moldings in this category", icon='INFO')
            return
        
        # Display items in a grid
        box = layout.box()
        flow = box.column_flow(columns=2, align=True)
        
        for item in items:
            item_box = flow.box()
            item_box.label(text=item['name'])
            
            # Show thumbnail if available
            if item['thumbnail']:
                # Load thumbnail into preview collection
                icon_id = props_hb_frameless.load_library_thumbnail(item['thumbnail'], item['name'])
                if icon_id:
                    item_box.template_icon(icon_value=icon_id, scale=4.0)
            
            # Add button
            op = item_box.operator("hb_frameless.add_molding_profile", text="Add", icon='ADD')
            op.filepath = item['filepath']
            op.molding_name = item['name']
    
    def execute(self, context):
        return {'FINISHED'}





# =============================================================================
# RIGHT-CLICK MENU OPERATORS
# =============================================================================


classes = (
    hb_frameless_OT_create_crown_detail,
    hb_frameless_OT_delete_crown_detail,
    hb_frameless_OT_edit_crown_detail,
    hb_frameless_OT_assign_crown_to_cabinets,
    hb_frameless_OT_add_molding_profile,
    hb_frameless_OT_add_solid_lumber,
    hb_frameless_OT_browse_molding_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)
