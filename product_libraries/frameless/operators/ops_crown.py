import bpy
import math
import os
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_details, hb_types, units


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

        return self._assign_crown(context, cabinets)

    def _assign_crown(self, context, cabinets):
        """Assign the active crown detail to the given cabinet roots.

        Shared by the selection-based and whole-room operators: removes
        any existing crown from the cabinets, partitions them into
        touch-connected components, and builds one crown per component
        - through the corner-aware chain builder when the component
        contains a corner cabinet, otherwise through the original
        single-axis group builder (run per component so each run picks
        its own wall axis; a mixed-axis room would otherwise sort every
        run by the first cabinet's axis).
        """
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

        # Remove any existing crown molding on the target cabinets
        for cabinet in cabinets:
            self._remove_existing_crown(cabinet)
            cabinet['CROWN_DETAIL_NAME'] = crown.name
            cabinet['CROWN_DETAIL_SCENE'] = crown.detail_scene_name

        # Get all walls and all cabinets in current scene for adjacency detection
        current_scene = context.scene
        all_walls = [o for o in current_scene.objects if o.get('IS_WALL_BP') or o.get('IS_WALL')]
        all_cabinets = [o for o in current_scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE')]

        # Analyze cabinet adjacency and group connected cabinets.
        # Components that contain a corner cabinet route through the
        # corner-aware chain builder so the crown wraps the corner's
        # pie-cut / diagonal front; straight-only components keep the
        # original single-axis path builder.
        corner_chains = []
        cabinet_groups = []
        for component in self._connected_components(cabinets):
            if any(c.get('IS_CORNER_CABINET') for c in component):
                corner_chains.append(self._order_chain(component))
            else:
                cabinet_groups.extend(self._group_adjacent_cabinets(
                    component, all_cabinets, all_walls))

        # Create crown molding for each group
        for group in cabinet_groups:
            for profile in profiles:
                self._create_crown_for_group(context, group, profile, all_walls, all_cabinets, current_scene)

        for chain in corner_chains:
            for profile in profiles:
                self._create_crown_for_chain(context, chain, profile, all_walls, all_cabinets, current_scene)

        total_cabs = (sum(len(g['cabinets']) for g in cabinet_groups)
                      + sum(len(c) for c in corner_chains))
        group_count = len(cabinet_groups) + len(corner_chains)
        self.report({'INFO'}, f"Created crown molding on {total_cabs} cabinet(s) in {group_count} group(s)")
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

    # ---------------- corner-aware chaining ----------------
    # A selection that includes a corner cabinet can't be described by
    # the single-axis group model above: the run changes direction at
    # the corner and the crown must wrap the corner's pie-cut or
    # diagonal front. These helpers order such a selection into a
    # chain, build the raw front polyline through it, offset the
    # polyline outward with mitered joins, and extrude.

    def _cabs_touch(self, a, b, tolerance=0.02):
        """True when two cabinets' world AABBs touch (overlap once each
        is expanded by the tolerance) and their tops line up. Same
        criteria as the along-axis adjacency test, minus the shared-
        wall-axis assumption, so a corner cabinet joins both its runs.
        """
        ba = self._get_cabinet_bounds(a)
        bb = self._get_cabinet_bounds(b)
        if abs(ba['top_z'] - bb['top_z']) > tolerance:
            return False
        if (ba['left_x'] - tolerance > bb['right_x']
                or bb['left_x'] - tolerance > ba['right_x']):
            return False
        if (ba['front_y'] - tolerance > bb['back_y']
                or bb['front_y'] - tolerance > ba['back_y']):
            return False
        return True

    def _connected_components(self, cabinets):
        """Partition the selection into touch-connected components."""
        remaining = list(cabinets)
        components = []
        while remaining:
            comp = [remaining.pop()]
            queue = list(comp)
            while queue:
                current = queue.pop()
                for other in list(remaining):
                    if self._cabs_touch(current, other):
                        remaining.remove(other)
                        comp.append(other)
                        queue.append(other)
            components.append(comp)
        return components

    def _order_chain(self, component):
        """Order a connected component into a linear chain by walking
        touch adjacency from an end (a member with a single touching
        neighbor). Members a strict walk can't reach (branching
        selections) are appended so they still receive a crown segment
        rather than being dropped silently.
        """
        if len(component) <= 2:
            return list(component)
        neighbors = {
            id(c): [o for o in component
                    if o is not c and self._cabs_touch(c, o)]
            for c in component
        }
        start = next(
            (c for c in component if len(neighbors[id(c)]) == 1),
            component[0])
        chain = [start]
        used = {id(start)}
        current = start
        while True:
            nxt = next(
                (o for o in neighbors[id(current)] if id(o) not in used),
                None)
            if nxt is None:
                break
            chain.append(nxt)
            used.add(id(nxt))
            current = nxt
        for c in component:
            if id(c) not in used:
                chain.append(c)
        return chain

    def _corner_plan_data(self, corner):
        """Plan-space data for a corner cabinet in its LOCAL frame.

        Local convention (types_frameless.CornerCabinet): origin at the
        inside corner where the walls meet, left wing extending -Y with
        its front on the x=Left Depth plane, right wing extending +X
        with its front on the y=-Right Depth plane; the notch / chamfer
        spans between (ld, -dim_y) and (dim_x, -rd).

        Returns dict:
            front: canonical raw front polyline, left wing end to
                right wing end (local XY Vectors)
            left_end / right_end: (front_corner, back_corner) of each
                wing's end face
        """
        try:
            geo = hb_types.GeoNodeObject(corner)
            dim_x = geo.get_input('Dim X')
            dim_y = geo.get_input('Dim Y')
        except Exception:
            # Local-frame bound_box fallback.
            local = [Vector(c) for c in corner.bound_box]
            dim_x = max(c.x for c in local)
            dim_y = -min(c.y for c in local)
        ld = corner.get('Left Depth') or units.inch(24.0)
        rd = corner.get('Right Depth') or units.inch(24.0)

        left_front = Vector((ld, -dim_y))
        right_front = Vector((dim_x, -rd))
        if corner.get('CORNER_TYPE') == 'DIAGONAL':
            front = [left_front, right_front]
        else:  # PIECUT - two faces meeting at the notch corner
            front = [left_front, Vector((ld, -rd)), right_front]
        return {
            'front': front,
            'left_end': (left_front, Vector((0.0, -dim_y))),
            'right_end': (right_front, Vector((dim_x, 0.0))),
        }

    def _corner_world_xy(self, corner, local_pt):
        """Transform a local plan point of a corner cabinet to world XY."""
        w = corner.matrix_world @ Vector((local_pt.x, local_pt.y, 0.0))
        return Vector((w.x, w.y))

    def _straight_front_corners(self, cab):
        """(corner_a, corner_b, front_normal) for a straight cabinet:
        the two front corners of its world AABB (unordered) and the
        world front direction (local -Y, snapped to the dominant world
        axis - straight cabinets sit on axis-aligned walls).
        """
        b = self._get_cabinet_bounds(cab)
        fn3 = cab.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))
        if abs(fn3.x) >= abs(fn3.y):
            fn = Vector((1.0 if fn3.x > 0 else -1.0, 0.0))
            x = b['right_x'] if fn.x > 0 else b['left_x']
            return (Vector((x, b['front_y'])), Vector((x, b['back_y'])), fn)
        fn = Vector((0.0, 1.0 if fn3.y > 0 else -1.0))
        y = b['back_y'] if fn.y > 0 else b['front_y']
        return (Vector((b['left_x'], y)), Vector((b['right_x'], y)), fn)

    def _offset_polyline_right(self, points, offset):
        """Offset an open XY polyline to the RIGHT of its direction of
        travel by `offset`, with mitered joins (consecutive offset
        lines intersected). Terminal points shift perpendicular only;
        the callers apply the end treatments. Consecutive duplicate
        points are dropped first.
        """
        pts = []
        for p in points:
            if not pts or (p - pts[-1]).length > 1e-6:
                pts.append(p)
        if len(pts) < 2 or abs(offset) < 1e-9:
            return pts
        lines = []  # (offset segment start, direction, length)
        for a, b in zip(pts, pts[1:]):
            d = (b - a).normalized()
            n = Vector((d.y, -d.x))
            lines.append((a + n * offset, d, (b - a).length))
        out = [lines[0][0]]
        for (p1, d1, len1), (p2, d2, _len2) in zip(lines, lines[1:]):
            cross = d1.x * d2.y - d1.y * d2.x
            if abs(cross) < 1e-6:
                # Parallel continuation (collinear fronts or a square
                # depth jog already present as its own raw segment).
                out.append(p1 + d1 * len1)
                out.append(p2)
            else:
                t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / cross
                out.append(p1 + d1 * t)
        p_last, d_last, len_last = lines[-1]
        out.append(p_last + d_last * len_last)
        # Drop duplicates the parallel branch may have produced.
        deduped = []
        for p in out:
            if not deduped or (p - deduped[-1]).length > 1e-6:
                deduped.append(p)
        return deduped

    def _face_near_wall(self, probe_xy, walls, tolerance=0.05):
        """True when a world XY probe point (just beyond an end face)
        lands inside a wall's world AABB expanded by the tolerance."""
        for wall in walls:
            corners = [wall.matrix_world @ Vector(c) for c in wall.bound_box]
            xs = [c.x for c in corners]
            ys = [c.y for c in corners]
            if (min(xs) - tolerance <= probe_xy.x <= max(xs) + tolerance
                    and min(ys) - tolerance <= probe_xy.y <= max(ys) + tolerance):
                return True
        return False

    def _end_neighbor(self, probe_xy, top_z, all_cabinets, chain,
                      tolerance=0.05):
        """Crown-eligible cabinet outside the chain whose bounds contain
        the probe point - the unselected return the crown dies into."""
        for other in all_cabinets:
            if other in chain:
                continue
            if other.get('CABINET_TYPE', '') not in ('UPPER', 'TALL'):
                continue
            b = self._get_cabinet_bounds(other)
            if abs(b['top_z'] - top_z) > tolerance:
                continue
            if (b['left_x'] - tolerance <= probe_xy.x <= b['right_x'] + tolerance
                    and b['front_y'] - tolerance <= probe_xy.y <= b['back_y'] + tolerance):
                return other
        return None

    def _assemble_raw_polyline(self, chain):
        """Raw (unoffset) front polyline through the chain, in chain
        order, plus per-terminal end-face data.

        Returns (points, ends) where ends is a 2-list for the start and
        end terminals: dict(cab, back_corner, fn) - back_corner is the
        far corner of the terminal end face (for exposed return caps)
        and fn the terminal cabinet's front normal (None for corner
        wings, which only take butt or cap treatments).
        """
        points = []
        ends = [None, None]

        def corner_points(cab, prev_ref, next_ref):
            data = self._corner_plan_data(cab)
            pts = [self._corner_world_xy(cab, p) for p in data['front']]
            left_end = tuple(self._corner_world_xy(cab, p)
                             for p in data['left_end'])
            right_end = tuple(self._corner_world_xy(cab, p)
                              for p in data['right_end'])
            # Enter from whichever wing is nearer the incoming path;
            # with no incoming path, exit toward the next cabinet.
            reverse = False
            if prev_ref is not None:
                reverse = ((prev_ref - pts[0]).length
                           > (prev_ref - pts[-1]).length)
            elif next_ref is not None:
                reverse = ((next_ref - pts[-1]).length
                           > (next_ref - pts[0]).length)
            if reverse:
                pts = list(reversed(pts))
                left_end, right_end = right_end, left_end
            # entry face, exit face (front corner first in each pair)
            return pts, left_end, right_end

        def cab_center(cab):
            b = self._get_cabinet_bounds(cab)
            return Vector(((b['left_x'] + b['right_x']) / 2.0,
                           (b['front_y'] + b['back_y']) / 2.0))

        for i, cab in enumerate(chain):
            prev_ref = points[-1] if points else None
            next_ref = cab_center(chain[i + 1]) if i + 1 < len(chain) else None
            if cab.get('IS_CORNER_CABINET'):
                pts, entry_face, exit_face = corner_points(
                    cab, prev_ref, next_ref)
                points.extend(pts)
                if i == 0:
                    ends[0] = {'cab': cab, 'back': entry_face[1], 'fn': None}
                if i == len(chain) - 1:
                    ends[1] = {'cab': cab, 'back': exit_face[1], 'fn': None}
            else:
                ca, cb, fn = self._straight_front_corners(cab)
                # First point continues the incoming path; with no
                # incoming path yet, the SECOND point must lead toward
                # the next cabinet.
                if prev_ref is not None:
                    first_is_ca = ((prev_ref - ca).length
                                   <= (prev_ref - cb).length)
                elif next_ref is not None:
                    first_is_ca = ((next_ref - ca).length
                                   >= (next_ref - cb).length)
                else:
                    first_is_ca = True
                near, far = (ca, cb) if first_is_ca else (cb, ca)
                points.extend([near, far])
                b = self._get_cabinet_bounds(cab)
                depth_amt = (b['back_y'] - b['front_y']
                             if fn.x == 0 else b['right_x'] - b['left_x'])
                if i == 0:
                    ends[0] = {'cab': cab,
                               'back': near - fn * depth_amt, 'fn': fn}
                if i == len(chain) - 1:
                    ends[1] = {'cab': cab,
                               'back': far - fn * depth_amt, 'fn': fn}
        return points, ends

    def _create_crown_for_chain(self, context, chain, profile, walls,
                                all_cabinets, target_scene):
        """Crown for a run that includes corner cabinets.

        Builds the raw front polyline through the chain - straight
        cabinets contribute their front edge, corner cabinets their
        pie-cut or diagonal front - offsets it outward by the profile's
        depth offset with mitered joins (so the crown turns the corner
        with proper miters instead of cutting straight across the
        corner box), applies the wall / return / exposed end
        treatments, and extrudes the profile along the result.
        """
        if profile.location.x < 0:
            inset = abs(profile.location.x)
            extend = 0.0
        else:
            inset = 0.0
            extend = profile.location.x
        o = extend - inset

        raw, ends = self._assemble_raw_polyline(chain)

        # Winding: offsets go to the RIGHT of travel, so travel must
        # keep the cabinet fronts on the right. Check the first
        # straight cabinet; a lone corner cabinet is canonical (left
        # wing end -> right wing end) by construction.
        for i, cab in enumerate(chain):
            if not cab.get('IS_CORNER_CABINET'):
                _ca, _cb, fn = self._straight_front_corners(cab)
                # This cabinet contributed two consecutive raw points;
                # find them by locating its front line direction.
                idx = 0
                for j, c2 in enumerate(chain[:i]):
                    idx += (3 if (c2.get('IS_CORNER_CABINET')
                                  and c2.get('CORNER_TYPE') != 'DIAGONAL')
                            else 2)
                travel = (raw[idx + 1] - raw[idx])
                if travel.length > 1e-6:
                    travel.normalize()
                    right = Vector((travel.y, -travel.x))
                    if right.dot(fn) < 0:
                        chain = list(reversed(chain))
                        raw, ends = self._assemble_raw_polyline(chain)
                break

        if len(raw) < 2:
            return None

        off = self._offset_polyline_right(raw, o)

        # ---- end treatments ----
        top_z = self._get_cabinet_bounds(chain[0])['top_z']
        probe_dist = units.inch(1.0)

        for side in (0, 1):
            end = ends[side]
            if end is None:
                continue
            if side == 0:
                outward = raw[0] - raw[1]
                terminal = off[0]
            else:
                outward = raw[-1] - raw[-2]
                terminal = off[-1]
            if outward.length < 1e-6:
                continue
            outward.normalize()
            face_mid = (raw[0 if side == 0 else -1] + end['back']) / 2.0
            probe = face_mid + outward * probe_dist

            if self._face_near_wall(probe, walls):
                # Butt into the wall, held back by the profile inset.
                corrected = terminal - outward * inset
                if side == 0:
                    off[0] = corrected
                else:
                    off[-1] = corrected
                continue

            adjacent = self._end_neighbor(probe, top_z, all_cabinets, chain)
            if adjacent is not None:
                corrected = terminal - outward * inset
                jog = None
                fn = end['fn']
                if (fn is not None
                        and adjacent.get('CABINET_TYPE') == 'TALL'
                        and end['cab'].get('CABINET_TYPE') == 'UPPER'):
                    # Die into the deeper tall return at ITS front line.
                    adj_b = self._get_cabinet_bounds(adjacent)
                    adj_corners = [
                        Vector((adj_b['left_x'], adj_b['front_y'])),
                        Vector((adj_b['right_x'], adj_b['front_y'])),
                        Vector((adj_b['left_x'], adj_b['back_y'])),
                        Vector((adj_b['right_x'], adj_b['back_y'])),
                    ]
                    adj_front = max(c.dot(fn) for c in adj_corners)
                    cur_front = raw[0 if side == 0 else -1].dot(fn)
                    jog = corrected + fn * (adj_front - cur_front)
                if side == 0:
                    off[0] = corrected
                    if jog is not None:
                        off.insert(0, jog)
                else:
                    off[-1] = corrected
                    if jog is not None:
                        off.append(jog)
                continue

            # Exposed end: miter around the end and return to the back.
            mitered = terminal + outward * o
            back_pt = end['back'] + outward * o
            if side == 0:
                off[0] = mitered
                off.insert(0, back_pt)
            else:
                off[-1] = mitered
                off.append(back_pt)

        world_points = [Vector((p.x, p.y, 0.0)) for p in off]
        return self._extrude_profile_along_path(
            context, world_points, chain[0], profile, target_scene)
    
    def _extrude_profile_along_path(self, context, world_points, first_cab,
                                    profile, target_scene):
        """Copy the profile, build a 2D poly curve through world_points
        (converted local to first_cab, at its top plus the profile's
        height offset), bevel-extrude, parent, smooth and assign the
        cabinet style material. Shared tail of the straight-run and
        corner-aware crown builders. Returns the crown object.
        """
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

        first_bounds = self._get_cabinet_bounds(first_cab)

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

    def _create_crown_for_group(self, context, group, profile, walls, all_cabinets, target_scene):
        """Create crown molding extrusion for a group of cabinets."""

        cabinets = group['cabinets']
        first_cab = cabinets[0]
        last_cab = cabinets[-1]
        axis = group.get('axis', 'X')

        profile_offset_x = profile.location.x  # Depth offset (positive = forward)

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

        return self._extrude_profile_along_path(
            context, world_points, first_cab, profile, target_scene)


class hb_frameless_OT_assign_crown_to_room(hb_frameless_OT_assign_crown_to_cabinets):
    """Assign the active crown detail to every upper and tall cabinet
    in the room. Subclasses the selection operator for its grouping /
    path-building machinery; only the cabinet collection differs.
    """
    bl_idname = "hb_frameless.assign_crown_to_room"
    bl_label = "Assign Crown to Room"
    bl_description = (
        "Create crown molding on every upper and tall cabinet in this "
        "room using the active crown detail, wrapping runs and corners "
        "automatically"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.crown_details) > 0

    def execute(self, context):
        cabinets = [
            obj for obj in context.scene.objects
            if obj.get('IS_FRAMELESS_CABINET_CAGE')
            and obj.get('CABINET_TYPE', '') in ('UPPER', 'TALL')
        ]
        if not cabinets:
            self.report({'WARNING'}, "No upper or tall cabinets in this room")
            return {'CANCELLED'}
        return self._assign_crown(context, cabinets)


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
                    obj.data.dimensions = '2D'
                    obj.data.fill_mode = 'NONE'
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
    hb_frameless_OT_assign_crown_to_room,
    hb_frameless_OT_add_molding_profile,
    hb_frameless_OT_add_solid_lumber,
    hb_frameless_OT_browse_molding_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)
