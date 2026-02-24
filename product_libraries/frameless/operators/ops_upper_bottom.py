import bpy
import math
import os
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_details, hb_types, units


class hb_frameless_OT_create_upper_bottom_detail(bpy.types.Operator):
    """Create a new upper bottom detail"""
    bl_idname = "hb_frameless.create_upper_bottom_detail"
    bl_label = "Create Upper Bottom Detail"
    bl_description = "Create a new upper cabinet bottom detail with a 2D profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Name for the upper bottom detail",
        default="Upper Bottom Detail"
    )  # type: ignore
    
    def execute(self, context):
        # Get main scene props
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create a new upper bottom detail entry
        upper_bottom = props.upper_bottom_details.add()
        upper_bottom.name = self.name

        # Create a detail scene for the upper bottom profile
        detail = hb_details.DetailView()
        scene = detail.create(f"Upper Bottom - {self.name}")
        scene['IS_UPPER_BOTTOM_DETAIL'] = True
        
        # Store the scene name reference
        upper_bottom.detail_scene_name = scene.name
        
        # Set as active
        props.active_upper_bottom_detail_index = len(props.upper_bottom_details) - 1
        
        # Set upper bottom detail defaults
        hb_scene = scene.home_builder
        hb_scene.annotation_line_thickness = units.inch(0.02)
        
        # Set Calibri font as default if available
        for font in bpy.data.fonts:
            if 'calibri' in font.name.lower():
                hb_scene.annotation_font = font
                break
        
        # Draw a cabinet side detail as starting point
        self._draw_cabinet_side_detail(context, scene, props)
        
        # Switch to the detail scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        self.report({'INFO'}, f"Created upper bottom detail: {self.name}")
        return {'FINISHED'}
    
    def _draw_cabinet_side_detail(self, context, scene, props):
        """Draw the bottom-front corner of upper cabinet side profile."""
        
        # Make sure we're in the right scene
        original_scene = context.scene
        context.window.scene = scene
        
        # Get cabinet dimensions from props
        part_thickness = props.default_carcass_part_thickness
        door_to_cab_gap = units.inch(0.125)
        door_overlay = part_thickness - units.inch(.0625)
        door_thickness = units.inch(0.75)
        cabinet_depth = props.upper_cabinet_depth
        corner_size = units.inch(4)  # Visible height above/below
        
        # Position the detail so the bottom-front corner of the upper cabinet is at origin
        # -X axis goes toward the back (depth), +Y axis goes up (height)
        # Origin (0,0) is at the bottom-front corner of the cabinet side panel
        
        hb_scene = scene.home_builder
        
        # Draw cabinet side profile - full depth of upper cabinet
        side_profile = hb_details.GeoNodePolyline()
        side_profile.create("Cabinet Side")
        # Start at top of visible section (4" up from bottom)
        side_profile.set_point(0, Vector((0, corner_size, 0)))
        # Go down to bottom-front corner
        side_profile.add_point(Vector((0, 0, 0)))
        # Go back along bottom edge to full cabinet depth
        side_profile.add_point(Vector((-cabinet_depth, 0, 0)))
        # Go up along back edge
        side_profile.add_point(Vector((-cabinet_depth, corner_size, 0)))
        
        # Draw bottom panel - full depth
        bottom_panel = hb_details.GeoNodePolyline()
        bottom_panel.create("Cabinet Bottom")
        bottom_panel.set_point(0, Vector((0, part_thickness, 0)))
        bottom_panel.add_point(Vector((-cabinet_depth, part_thickness, 0)))
        
        # Draw door profile - bottom portion
        door_profile = hb_details.GeoNodePolyline()
        door_profile.create("Door Face")
        door_profile.set_point(0, Vector((door_to_cab_gap, corner_size, 0)))
        door_profile.add_point(Vector((door_to_cab_gap, part_thickness - door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap + door_thickness, part_thickness - door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap + door_thickness, corner_size, 0)))
        
        
        # --- DOOR OVERLAY LABEL ---
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
        
        door_center_x = door_to_cab_gap + door_thickness / 2
        door_mid_y = (part_thickness - door_overlay + corner_size) / 2
        leader_end_x = door_to_cab_gap + door_thickness + units.inch(2)
        
        door_leader = hb_details.GeoNodePolyline()
        door_leader.create("Door Overlay Leader")
        door_leader.set_point(0, Vector((door_center_x, door_mid_y, 0)))
        door_leader.add_point(Vector((leader_end_x, door_mid_y, 0)))
        
        overlay_text = hb_details.GeoNodeText()
        overlay_text.create("Door Overlay Label", overlay_type_text, hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            overlay_text.obj.data.font = hb_scene.annotation_font
        overlay_text.set_location(Vector((leader_end_x + units.inch(0.25), door_mid_y, 0)))
        overlay_text.set_alignment('LEFT', 'CENTER')
        
        # Add a label/text annotation
        text = hb_details.GeoNodeText()
        text.create("Label", "UPPER BOTTOM DETAIL", hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            text.obj.data.font = hb_scene.annotation_font
        text.set_location(Vector((0, -units.inch(1), 0)))
        text.set_alignment('CENTER', 'TOP')
        
        # Switch back to original scene
        context.window.scene = original_scene


class hb_frameless_OT_delete_upper_bottom_detail(bpy.types.Operator):
    """Delete the selected upper bottom detail"""
    bl_idname = "hb_frameless.delete_upper_bottom_detail"
    bl_label = "Delete Upper Bottom Detail"
    bl_description = "Delete the selected upper bottom detail and its profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.upper_bottom_details) > 0
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.upper_bottom_details:
            self.report({'WARNING'}, "No upper bottom details to delete")
            return {'CANCELLED'}
        
        index = props.active_upper_bottom_detail_index
        upper_bottom = props.upper_bottom_details[index]
        
        # Delete the associated detail scene if it exists
        detail_scene = upper_bottom.get_detail_scene()
        if detail_scene:
            if context.scene == detail_scene:
                context.window.scene = main_scene
            bpy.data.scenes.remove(detail_scene)
        
        # Remove from collection
        upper_bottom_name = upper_bottom.name
        props.upper_bottom_details.remove(index)
        
        # Update active index
        if props.active_upper_bottom_detail_index >= len(props.upper_bottom_details):
            props.active_upper_bottom_detail_index = max(0, len(props.upper_bottom_details) - 1)
        
        self.report({'INFO'}, f"Deleted upper bottom detail: {upper_bottom_name}")
        return {'FINISHED'}


class hb_frameless_OT_edit_upper_bottom_detail(bpy.types.Operator):
    """Edit the selected upper bottom detail profile"""
    bl_idname = "hb_frameless.edit_upper_bottom_detail"
    bl_label = "Edit Upper Bottom Detail"
    bl_description = "Open the upper bottom detail profile scene for editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.upper_bottom_details) == 0:
            return False
        upper_bottom = props.upper_bottom_details[props.active_upper_bottom_detail_index]
        return upper_bottom.get_detail_scene() is not None
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        upper_bottom = props.upper_bottom_details[props.active_upper_bottom_detail_index]
        detail_scene = upper_bottom.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Upper bottom detail scene not found")
            return {'CANCELLED'}
        
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=detail_scene.name)
        
        self.report({'INFO'}, f"Editing upper bottom detail: {upper_bottom.name}")
        return {'FINISHED'}




class hb_frameless_OT_assign_upper_bottom_to_cabinets(bpy.types.Operator):
    """Assign the selected upper bottom detail to selected upper cabinets"""
    bl_idname = "hb_frameless.assign_upper_bottom_to_cabinets"
    bl_label = "Assign Upper Bottom to Cabinets"
    bl_description = "Create upper bottom molding extrusions on selected upper cabinets using the active upper bottom detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.upper_bottom_details) == 0:
            return False
        for obj in context.selected_objects:
            if obj.get('IS_CABINET_BP') or obj.get('IS_FRAMELESS_CABINET_CAGE'):
                return True
        return False
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        upper_bottom = props.upper_bottom_details[props.active_upper_bottom_detail_index]
        detail_scene = upper_bottom.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Upper bottom detail scene not found")
            return {'CANCELLED'}
        
        # Get all molding profiles and solid lumber from the detail scene
        profiles = []
        for obj in detail_scene.objects:
            if obj.get('IS_MOLDING_PROFILE') or obj.get('IS_SOLID_LUMBER'):
                profiles.append(obj)
        
        if not profiles:
            self.report({'WARNING'}, "No molding profiles or solid lumber found in upper bottom detail")
            return {'CANCELLED'}
        
        # Collect unique UPPER cabinets from selection
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
                if cab_type == 'UPPER':
                    cabinets.append(cabinet_bp)
        
        if not cabinets:
            self.report({'WARNING'}, "No valid upper cabinets selected")
            return {'CANCELLED'}
        
        # Remove any existing upper bottom molding on selected cabinets
        for cabinet in cabinets:
            self._remove_existing_upper_bottom(cabinet)
            cabinet['UPPER_BOTTOM_DETAIL_NAME'] = upper_bottom.name
            cabinet['UPPER_BOTTOM_DETAIL_SCENE'] = upper_bottom.detail_scene_name
        
        # Get all walls and all cabinets in current scene for adjacency detection
        current_scene = context.scene
        all_walls = [o for o in current_scene.objects if o.get('IS_WALL_BP') or o.get('IS_WALL')]
        all_cabinets = [o for o in current_scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE')]
        
        # Analyze cabinet adjacency and group connected cabinets
        cabinet_groups = self._group_adjacent_cabinets(cabinets, all_cabinets, all_walls)
        
        # Create upper bottom molding for each group
        for group in cabinet_groups:
            for profile in profiles:
                self._create_upper_bottom_for_group(context, group, profile, all_walls, all_cabinets, current_scene)
        
        total_cabs = sum(len(g['cabinets']) for g in cabinet_groups)
        self.report({'INFO'}, f"Created upper bottom molding on {total_cabs} cabinet(s) in {len(cabinet_groups)} group(s)")
        return {'FINISHED'}
    
    def _remove_existing_upper_bottom(self, cabinet):
        """Remove any existing upper bottom molding children from the cabinet."""
        children_to_remove = []
        for child in cabinet.children:
            if child.get('IS_UPPER_BOTTOM_MOLDING') or child.get('IS_UPPER_BOTTOM_PROFILE_COPY'):
                children_to_remove.append(child)
        
        for child in children_to_remove:
            bpy.data.objects.remove(child, do_unlink=True)
    
    def _get_cabinet_bounds(self, cabinet):
        """Get world-space bounds of a cabinet using evaluated bounding box corners."""
        matrix = cabinet.matrix_world
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = cabinet.evaluated_get(depsgraph)
        world_corners = [matrix @ Vector(corner) for corner in eval_obj.bound_box]
        
        xs = [c.x for c in world_corners]
        ys = [c.y for c in world_corners]
        zs = [c.z for c in world_corners]
        
        return {
            'left_x': min(xs), 'right_x': max(xs),
            'front_y': min(ys), 'back_y': max(ys),
            'bottom_z': min(zs), 'top_z': max(zs),
            'width': max(xs) - min(xs),
            'depth': max(ys) - min(ys),
            'height': max(zs) - min(zs),
        }
    
    def _is_against_wall(self, cabinet, side, walls, tolerance=0.05):
        """Check if cabinet side is against a wall."""
        bounds = self._get_cabinet_bounds(cabinet)
        axis = self._get_wall_direction(cabinet)
        
        for wall in walls:
            corners = [wall.matrix_world @ Vector(c) for c in wall.bound_box]
            wxs = [c.x for c in corners]
            wys = [c.y for c in corners]
            w_min_x, w_max_x = min(wxs), max(wxs)
            w_min_y, w_max_y = min(wys), max(wys)
            w_thickness_x = w_max_x - w_min_x
            w_thickness_y = w_max_y - w_min_y
            
            if side == 'left':
                if axis == 'X':
                    if w_thickness_x < 0.2:
                        if (abs(bounds['left_x'] - w_max_x) < tolerance or 
                            abs(bounds['left_x'] - w_min_x) < tolerance):
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
                else:
                    if w_thickness_y < 0.2:
                        if (abs(bounds['back_y'] - w_max_y) < tolerance or 
                            abs(bounds['back_y'] - w_min_y) < tolerance):
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
            elif side == 'right':
                if axis == 'X':
                    if w_thickness_x < 0.2:
                        if (abs(bounds['right_x'] - w_min_x) < tolerance or 
                            abs(bounds['right_x'] - w_max_x) < tolerance):
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
                else:
                    if w_thickness_y < 0.2:
                        if (abs(bounds['front_y'] - w_min_y) < tolerance or 
                            abs(bounds['front_y'] - w_max_y) < tolerance):
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
            elif side == 'back':
                if axis == 'X':
                    if w_thickness_y < 0.2:
                        if abs(bounds['back_y'] - w_min_y) < tolerance or abs(bounds['back_y'] - w_max_y) < tolerance:
                            if bounds['left_x'] >= w_min_x - tolerance and bounds['right_x'] <= w_max_x + tolerance:
                                return True
                else:
                    if w_thickness_x < 0.2:
                        if abs(bounds['right_x'] - w_min_x) < tolerance or abs(bounds['right_x'] - w_max_x) < tolerance:
                            if bounds['front_y'] >= w_min_y - tolerance and bounds['back_y'] <= w_max_y + tolerance:
                                return True
        return False
    
    def _get_wall_direction(self, cabinet):
        """Get the wall direction for a cabinet. Returns 'X' or 'Y'."""
        if cabinet.parent and (cabinet.parent.get('IS_WALL_BP') or cabinet.parent.get('IS_WALL')):
            wall_rot_z = cabinet.parent.rotation_euler.z
            angle = abs(wall_rot_z) % math.pi
            if abs(angle - math.pi/2) < 0.1:
                return 'Y'
        return 'X'
    
    def _find_adjacent_cabinet(self, cabinet, side, all_cabinets, tolerance=0.02):
        """Find an UPPER cabinet adjacent to the given side."""
        bounds = self._get_cabinet_bounds(cabinet)
        axis = self._get_wall_direction(cabinet)
        
        for other in all_cabinets:
            if other == cabinet:
                continue
            
            other_bounds = self._get_cabinet_bounds(other)
            other_type = other.get('CABINET_TYPE', '')
            
            if other_type != 'UPPER':
                continue
            
            # Check if bottoms are at same height
            if abs(bounds['bottom_z'] - other_bounds['bottom_z']) > tolerance:
                continue
            
            if axis == 'X':
                if side == 'left':
                    if abs(other_bounds['right_x'] - bounds['left_x']) < tolerance:
                        return other
                elif side == 'right':
                    if abs(other_bounds['left_x'] - bounds['right_x']) < tolerance:
                        return other
            else:
                if side == 'left':
                    if abs(other_bounds['front_y'] - bounds['back_y']) < tolerance:
                        return other
                elif side == 'right':
                    if abs(other_bounds['back_y'] - bounds['front_y']) < tolerance:
                        return other
        return None
    
    def _group_adjacent_cabinets(self, selected_cabinets, all_cabinets, walls):
        """Group selected cabinets that are adjacent to each other."""
        if not selected_cabinets:
            return []
        
        axis = self._get_wall_direction(selected_cabinets[0])
        
        if axis == 'X':
            sorted_cabs = sorted(selected_cabinets, key=lambda c: self._get_cabinet_bounds(c)['left_x'])
        else:
            sorted_cabs = sorted(selected_cabinets, key=lambda c: self._get_cabinet_bounds(c)['back_y'], reverse=True)
        
        groups = []
        used = set()
        
        for cabinet in sorted_cabs:
            if cabinet in used:
                continue
            
            group_cabs = [cabinet]
            used.add(cabinet)
            
            current = cabinet
            while True:
                right_neighbor = self._find_adjacent_cabinet(current, 'right', all_cabinets)
                if right_neighbor and right_neighbor in selected_cabinets and right_neighbor not in used:
                    group_cabs.append(right_neighbor)
                    used.add(right_neighbor)
                    current = right_neighbor
                else:
                    break
            
            first_cab = group_cabs[0]
            last_cab = group_cabs[-1]
            
            left_against_wall = self._is_against_wall(first_cab, 'left', walls)
            right_against_wall = self._is_against_wall(last_cab, 'right', walls)
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
        """Map world-space bounds to wall-aligned coordinates."""
        if axis == 'X':
            return {
                'along_start': bounds['left_x'],
                'along_end': bounds['right_x'],
                'front': bounds['front_y'],
                'back': bounds['back_y'],
                'depth': bounds['back_y'] - bounds['front_y'],
            }
        else:
            return {
                'along_start': bounds['back_y'],
                'along_end': bounds['front_y'],
                'front': bounds['left_x'],
                'back': bounds['right_x'],
                'depth': bounds['right_x'] - bounds['left_x'],
            }
    
    def _make_world_point(self, along, depth, axis):
        """Convert wall-aligned coordinates to world XY point."""
        if axis == 'X':
            return Vector((along, depth, 0))
        else:
            return Vector((depth, along, 0))
    
    def _create_upper_bottom_for_group(self, context, group, profile, walls, all_cabinets, target_scene):
        """Create upper bottom molding extrusion for a group of cabinets."""
        
        cabinets = group['cabinets']
        first_cab = cabinets[0]
        last_cab = cabinets[-1]
        axis = group.get('axis', 'X')
        
        profile_offset_x = profile.location.x  # Depth offset
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
        profile_copy.name = f"UB_Profile_{profile.name}"
        profile_copy['IS_UPPER_BOTTOM_PROFILE_COPY'] = True
        
        # Build path points in WORLD coordinates
        world_points = []
        
        first_bounds = self._get_cabinet_bounds(first_cab)
        last_bounds = self._get_cabinet_bounds(last_cab)
        
        first_wb = self._get_wall_aligned_bounds(first_bounds, axis)
        last_wb = self._get_wall_aligned_bounds(last_bounds, axis)
        
        if profile_offset_x < 0:
            inset = abs(profile_offset_x)
            extend = 0
        else:
            inset = 0
            extend = profile_offset_x
        
        a_sign = 1 if axis == 'X' else -1
        
        # === LEFT SIDE ===
        if group['left_wall']:
            start_along = first_wb['along_start'] + a_sign * inset
            world_points.append(self._make_world_point(start_along, first_wb['front'] - extend + inset, axis))
        elif group['left_adjacent']:
            start_along = first_wb['along_start'] + a_sign * inset
            world_points.append(self._make_world_point(start_along, first_wb['front'] - extend + inset, axis))
        else:
            back_along = first_wb['along_start'] + a_sign * inset - a_sign * extend
            world_points.append(self._make_world_point(back_along, first_wb['back'], axis))
            world_points.append(self._make_world_point(back_along, first_wb['front'] - extend + inset, axis))
        
        # === RIGHT SIDE ===
        if group['right_wall']:
            end_along = last_wb['along_end'] - a_sign * inset
            world_points.append(self._make_world_point(end_along, last_wb['front'] - extend + inset, axis))
        elif group['right_adjacent']:
            end_along = last_wb['along_end'] - a_sign * inset
            world_points.append(self._make_world_point(end_along, last_wb['front'] - extend + inset, axis))
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
        curve_data = bpy.data.curves.new(name=f"UB_Path_{profile.name}", type='CURVE')
        curve_data.dimensions = '2D'
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = profile_copy
        curve_data.use_fill_caps = True
        
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(local_points) - 1)
        
        for i, pt in enumerate(local_points):
            spline.points[i].co = (pt.x, pt.y, pt.z, 1)
        
        ub_obj = bpy.data.objects.new(f"Upper_Bottom_{profile.name}", curve_data)
        target_scene.collection.objects.link(ub_obj)
        
        # Parent to first cabinet - position at bottom of cabinet
        ub_obj.parent = first_cab
        ub_obj.location = (0, 0, profile_offset_y)
        ub_obj['IS_UPPER_BOTTOM_MOLDING'] = True
        ub_obj['UB_PROFILE_NAME'] = profile.name
        
        # Add Smooth by Angle modifier
        smooth_mod = ub_obj.modifiers.new(name="Smooth by Angle", type='NODES')
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
        
        profile_copy.parent = ub_obj
        
        # Assign cabinet style material
        style_index = first_cab.get('CABINET_STYLE_INDEX', 0)
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if props.cabinet_styles and style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[style_index]
            material, _ = style.get_finish_material()
            if material:
                if len(ub_obj.data.materials) == 0:
                    ub_obj.data.materials.append(material)
                else:
                    ub_obj.data.materials[0] = material
        
        return ub_obj


classes = (
    hb_frameless_OT_create_upper_bottom_detail,
    hb_frameless_OT_delete_upper_bottom_detail,
    hb_frameless_OT_edit_upper_bottom_detail,
    hb_frameless_OT_assign_upper_bottom_to_cabinets,
)

register, unregister = bpy.utils.register_classes_factory(classes)
