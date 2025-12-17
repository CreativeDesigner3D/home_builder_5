import bpy
import os
import gpu
import blf
import math
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix, Euler
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from .. import hb_layouts
from .. import hb_types
from .. import units

# =============================================================================
# SCALE CALCULATION
# =============================================================================

# Drawing scales: maps scale string to (inches_on_paper, feet_in_reality)
# e.g., '1/4"=1\'' means 0.25 inches on paper = 1 foot in reality
DRAWING_SCALES = {
    # Imperial architectural scales
    '3"=1\'': (3.0, 1.0),        # Very detailed
    '1-1/2"=1\'': (1.5, 1.0),    # 1:8
    '1"=1\'': (1.0, 1.0),        # 1:12
    '3/4"=1\'': (0.75, 1.0),     # 1:16
    '1/2"=1\'': (0.5, 1.0),      # 1:24
    '3/8"=1\'': (0.375, 1.0),    # 1:32
    '1/4"=1\'': (0.25, 1.0),     # 1:48 - common for elevations
    '3/16"=1\'': (0.1875, 1.0),  # 1:64
    '1/8"=1\'': (0.125, 1.0),    # 1:96 - common for floor plans
    '1/16"=1\'': (0.0625, 1.0),  # 1:192
    # Metric/ratio scales
    '1:1': (1.0, 1.0),            # Full scale (inches to inches)
    '1:2': (1.0, 2.0),
    '1:4': (1.0, 4.0),
    '1:10': (1.0, 10.0),
    '1:20': (1.0, 20.0),
    '1:50': (1.0, 50.0),
}

# Paper sizes in inches (width, height) - portrait orientation
PAPER_SIZES_INCHES = {
    'LETTER': (8.5, 11.0),
    'LEGAL': (8.5, 14.0),
    'TABLOID': (11.0, 17.0),
    'A4': (8.27, 11.69),
    'A3': (11.69, 16.54),
}


def get_scale_factor(scale_str):
    """Get the scale factor: how many real-world feet per inch on paper.
    
    For '1/4"=1\'' this returns 4.0 (1 foot per 0.25 inches = 4 feet per inch)
    For '1:48' this would be similar (48 real units per 1 paper unit)
    """
    if scale_str not in DRAWING_SCALES:
        return 4.0  # Default to 1/4"=1'
    
    inches_on_paper, feet_in_reality = DRAWING_SCALES[scale_str]
    
    # For ratio scales like 1:50, treat as unitless ratio
    if scale_str.startswith('1:'):
        # 1:50 means 1 unit on paper = 50 units in reality
        # Return the ratio directly (will be applied to meters)
        return feet_in_reality / inches_on_paper
    else:
        # For imperial scales, return feet per inch on paper
        return feet_in_reality / inches_on_paper


def calculate_ortho_scale(paper_size, scale_str, landscape=True):
    """Calculate camera ortho_scale for given paper size and drawing scale.
    
    Args:
        paper_size: Paper size key ('LETTER', 'LEGAL', etc.)
        scale_str: Drawing scale string ('1/4"=1\'', '1:50', etc.)
        landscape: True for landscape, False for portrait
    
    Returns:
        ortho_scale in meters (Blender units)
    """
    if paper_size not in PAPER_SIZES_INCHES:
        paper_size = 'LETTER'
    
    paper_w, paper_h = PAPER_SIZES_INCHES[paper_size]
    
    if landscape:
        paper_w, paper_h = paper_h, paper_w
    
    scale_factor = get_scale_factor(scale_str)
    
    # For imperial scales (inches on paper to feet in reality)
    if not scale_str.startswith('1:'):
        # Calculate real-world height that fits on paper (in feet)
        real_height_feet = paper_h * scale_factor
        # Convert to meters for Blender
        real_height_meters = real_height_feet * 0.3048
    else:
        # For ratio scales, paper_h is in inches, scale is unitless
        # Assume working in meters, so paper represents paper_h * scale_factor meters
        # But we need a reference... let's assume 1 inch on paper at 1:1 = 1 meter
        # So at 1:50, 1 inch on paper = 50 meters
        # Paper height in inches * scale = real height in meters
        real_height_meters = (paper_h / 39.37) * scale_factor  # Convert paper inches to meters, then scale
    
    return real_height_meters


def update_layout_scale(self, context):
    """Callback when layout scale changes - updates camera ortho_scale."""
    scene = context.scene
    if not scene.get('IS_LAYOUT_VIEW'):
        return
    
    # Find the camera
    camera = scene.camera
    if not camera or camera.type != 'CAMERA':
        return
    
    # Get settings (use property access, not scene.get() which is for custom props)
    paper_size = scene.hb_paper_size
    scale_str = scene.hb_layout_scale
    landscape = scene.hb_paper_landscape
    
    # Calculate and set ortho_scale
    ortho_scale = calculate_ortho_scale(paper_size, scale_str, landscape)
    camera.data.ortho_scale = ortho_scale
    camera.scale = (ortho_scale, ortho_scale, ortho_scale)
    
    # Store scale in scene for title block
    scene['hb_layout_scale_display'] = scale_str
    
    # Update render resolution
    dpi = scene.get('PAPER_DPI', 150)
    paper_w, paper_h = PAPER_SIZES_INCHES.get(paper_size, (8.5, 11.0))
    if landscape:
        paper_w, paper_h = paper_h, paper_w
    
    scene.render.resolution_x = int(paper_w * dpi)
    scene.render.resolution_y = int(paper_h * dpi)
    
    # Update title block border to match new aspect ratio
    update_title_block_border(scene)


def update_title_block_border(scene):
    """Update title block border to match current page aspect ratio."""
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    aspect_ratio = res_x / res_y
    
    # Find the title block border object
    for obj in scene.objects:
        if "IS_TITLE_BLOCK_BOARDER" in obj:
            title_block = hb_types.GeoNodeRectangle(obj)
            # Update location (bottom-left corner)
            title_block.obj.location.x = -0.5
            title_block.obj.location.y = -0.5 / aspect_ratio
            title_block.set_input("Dim X", 1.0)
            title_block.set_input("Dim Y", 1.0 / aspect_ratio)
            break


def update_paper_size(self, context):
    """Callback when paper size changes."""
    update_layout_scale(self, context)


def update_paper_orientation(self, context):
    """Callback when paper orientation changes."""
    update_layout_scale(self, context)


# =============================================================================
# LAYOUT VIEW OPERATORS
# =============================================================================

class home_builder_layouts_OT_create_elevation_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.create_elevation_view"
    bl_label = "Create Elevation View"
    bl_description = "Create an elevation view for the selected wall"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object and 'IS_WALL_BP' in context.object
    
    def execute(self, context):
        wall_obj = context.object
        view = hb_layouts.ElevationView()
        scene = view.create(wall_obj)

        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        # Apply default scale and page size
        scene.hb_paper_size = 'LETTER'
        scene.hb_layout_scale = '1/4"=1\''
        
        self.report({'INFO'}, f"Created elevation view: {scene.name}")
        return {'FINISHED'}


class home_builder_layouts_OT_create_plan_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.create_plan_view"
    bl_label = "Create Plan View"
    bl_description = "Create a floor plan view of all walls"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        view = hb_layouts.PlanView()
        scene = view.create()

        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        # Apply default scale and page size for floor plans
        # scene.hb_paper_size = 'LEGAL'
        scene.hb_layout_scale = '1/4"=1\''
        
        self.report({'INFO'}, f"Created plan view: {scene.name}")
        return {'FINISHED'}


class home_builder_layouts_OT_create_3d_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.create_3d_view"
    bl_label = "Create 3D View"
    bl_description = "Create a 3D perspective view"
    bl_options = {'UNDO'}
    
    perspective: bpy.props.BoolProperty(
        name="Perspective",
        description="Use perspective projection (unchecked = isometric)",
        default=True
    )  # type: ignore
    
    def execute(self, context):
        view = hb_layouts.View3D()
        scene = view.create(perspective=self.perspective)

        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        view_type = "perspective" if self.perspective else "isometric"
        self.report({'INFO'}, f"Created 3D {view_type} view: {scene.name}")
        return {'FINISHED'}


class home_builder_layouts_OT_create_all_elevations(bpy.types.Operator):
    bl_idname = "home_builder_layouts.create_all_elevations"
    bl_label = "Create All Elevations"
    bl_description = "Create elevation views for all walls in the scene"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        views = hb_layouts.create_all_elevations()
        
        # Apply default scale to all
        for view in views:
            view.scene.hb_layout_scale = '1/4"=1\''
        
        self.report({'INFO'}, f"Created {len(views)} elevation views")
        return {'FINISHED'}


class home_builder_layouts_OT_create_multi_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.create_multi_view"
    bl_label = "Create Multi-View Layout"
    bl_description = "Create a multi-view layout showing plan, elevation, and side views"
    bl_options = {'UNDO'}
    
    include_plan: bpy.props.BoolProperty(
        name="Plan View (Top)",
        description="Include a top-down plan view",
        default=True
    )  # type: ignore
    
    include_front: bpy.props.BoolProperty(
        name="Front Elevation",
        description="Include a front elevation view",
        default=True
    )  # type: ignore
    
    include_back: bpy.props.BoolProperty(
        name="Back Elevation",
        description="Include a back elevation view",
        default=False
    )  # type: ignore
    
    include_left: bpy.props.BoolProperty(
        name="Left Side",
        description="Include a left side elevation view",
        default=True
    )  # type: ignore
    
    include_right: bpy.props.BoolProperty(
        name="Right Side",
        description="Include a right side elevation view",
        default=False
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return False
        if 'IS_CAGE_GROUP' in obj:
            return True
        return False
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select Views to Include:")
        
        col = layout.column(align=True)
        col.prop(self, "include_plan")
        
        layout.separator()
        layout.label(text="Elevations:")
        col = layout.column(align=True)
        col.prop(self, "include_front")
        col.prop(self, "include_back")
        col.prop(self, "include_left")
        col.prop(self, "include_right")
    
    def execute(self, context):
        source_obj = context.object
        
        views = []
        if self.include_plan:
            views.append('PLAN')
        if self.include_front:
            views.append('FRONT')
        if self.include_back:
            views.append('BACK')
        if self.include_left:
            views.append('LEFT')
        if self.include_right:
            views.append('RIGHT')
        
        if not views:
            self.report({'WARNING'}, "No views selected")
            return {'CANCELLED'}
        
        multi_view = hb_layouts.MultiView()
        scene = multi_view.create(source_obj, views)
        
        if scene:
            bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
            self.report({'INFO'}, f"Created multi-view layout: {scene.name}")
        
        return {'FINISHED'}


class home_builder_layouts_OT_update_elevation_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.update_elevation_view"
    bl_label = "Update Elevation View"
    bl_description = "Update the elevation view to reflect changes in the 3D model"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_ELEVATION_VIEW')
    
    def execute(self, context):
        view = hb_layouts.ElevationView(context.scene)
        view.update()
        
        self.report({'INFO'}, "Updated elevation view")
        return {'FINISHED'}


class home_builder_layouts_OT_delete_layout_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.delete_layout_view"
    bl_label = "Delete Layout View"
    bl_description = "Delete the layout view"
    bl_options = {'UNDO'}
    
    scene_name: bpy.props.StringProperty(name="Scene Name")  # type: ignore
    
    def execute(self, context):
        if self.scene_name and self.scene_name in bpy.data.scenes:
            scene = bpy.data.scenes[self.scene_name]
        elif context.scene.get('IS_LAYOUT_VIEW'):
            scene = context.scene
        else:
            self.report({'WARNING'}, "No layout view to delete")
            return {'CANCELLED'}
        
        scene_name = scene.name
        
        if scene == context.scene:
            main_scenes = [s for s in bpy.data.scenes if not s.get('IS_LAYOUT_VIEW') and s != scene]
            other_layouts = [s for s in bpy.data.scenes if s.get('IS_LAYOUT_VIEW') and s != scene]
            
            if main_scenes:
                context.window.scene = main_scenes[0]
            elif other_layouts:
                context.window.scene = other_layouts[0]
        
        bpy.data.scenes.remove(scene)
        
        self.report({'INFO'}, f"Deleted layout view: {scene_name}")
        return {'FINISHED'}


class home_builder_layouts_OT_go_to_layout_view(bpy.types.Operator):
    bl_idname = "home_builder_layouts.go_to_layout_view"
    bl_label = "Go To Layout View"
    bl_description = "Switch to a layout view scene"
    bl_options = {'UNDO'}
    
    scene_name: bpy.props.StringProperty(name="Scene Name")  # type: ignore
    
    def execute(self, context):
        if self.scene_name in bpy.data.scenes:
            context.window.scene = bpy.data.scenes[self.scene_name]
            
            if bpy.data.scenes[self.scene_name].get('IS_LAYOUT_VIEW'):
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.region_3d.view_perspective = 'CAMERA'
                        break
        
        return {'FINISHED'}


class home_builder_layouts_OT_fit_view_to_content(bpy.types.Operator):
    bl_idname = "home_builder_layouts.fit_view_to_content"
    bl_label = "Fit to Content"
    bl_description = "Adjust scale to fit all content on the page"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW') and context.scene.camera
    
    def execute(self, context):
        scene = context.scene
        view = hb_layouts.get_layout_view_from_scene(scene)
        
        if view and hasattr(view, 'wall_obj') and view.wall_obj:
            view._fit_camera_to_content(view.wall_obj)
            
            # Calculate what scale this represents and update the property
            # (This is approximate - finds nearest scale)
            ortho_scale = scene.camera.data.ortho_scale
            paper_size = scene.hb_paper_size
            landscape = scene.hb_paper_landscape
            
            # Find closest matching scale
            best_scale = '1/4"=1\''
            best_diff = float('inf')
            
            for scale_str in DRAWING_SCALES.keys():
                calc_ortho = calculate_ortho_scale(paper_size, scale_str, landscape)
                diff = abs(calc_ortho - ortho_scale)
                if diff < best_diff:
                    best_diff = diff
                    best_scale = scale_str
            
            # Don't trigger update callback (would reset ortho_scale)
            scene['hb_layout_scale'] = best_scale
            
            self.report({'INFO'}, f"Fit to content (approximate scale: {best_scale})")
        else:
            self.report({'WARNING'}, "Could not determine content bounds")
        
        return {'FINISHED'}


class home_builder_layouts_OT_render_layout(bpy.types.Operator):
    bl_idname = "home_builder_layouts.render_layout"
    bl_label = "Render Layout"
    bl_description = "Render the current layout view to an image"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW') and context.scene.camera
    
    def execute(self, context):
        scene = context.scene
        
        paper_size = scene.hb_paper_size
        landscape = scene.hb_paper_landscape
        dpi = scene.get('PAPER_DPI', 150)
        
        paper_w, paper_h = PAPER_SIZES_INCHES.get(paper_size, (8.5, 11.0))
        if landscape:
            paper_w, paper_h = paper_h, paper_w
        
        width = int(paper_w * dpi)
        height = int(paper_h * dpi)
        
        orig_resolution_x = scene.render.resolution_x
        orig_resolution_y = scene.render.resolution_y
        orig_film_transparent = scene.render.film_transparent
        orig_filepath = scene.render.filepath
        
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.film_transparent = False
        
        blend_filepath = bpy.data.filepath
        if blend_filepath:
            output_dir = os.path.dirname(blend_filepath)
        else:
            output_dir = os.path.expanduser("~")
        
        output_path = os.path.join(output_dir, f"{scene.name}.png")
        scene.render.filepath = output_path
        scene.render.image_settings.file_format = 'PNG'
        
        if not scene.world:
            scene.world = bpy.data.worlds.new(f"{scene.name}_World")
        scene.world.use_nodes = True
        bg_node = scene.world.node_tree.nodes.get('Background')
        if bg_node:
            bg_node.inputs['Color'].default_value = (1, 1, 1, 1)
        
        bpy.ops.render.render(write_still=True)
        
        scene.render.resolution_x = orig_resolution_x
        scene.render.resolution_y = orig_resolution_y
        scene.render.film_transparent = orig_film_transparent
        scene.render.filepath = orig_filepath
        
        self.report({'INFO'}, f"Rendered to: {output_path}")
        return {'FINISHED'}




# =============================================================================
# DIMENSION ANNOTATION OPERATOR
# =============================================================================

class home_builder_layouts_OT_add_dimension(bpy.types.Operator):
    bl_idname = "home_builder_layouts.add_dimension"
    bl_label = "Add Dimension"
    bl_description = "Click two points to measure, then click to place the dimension line"
    bl_options = {'UNDO'}
    
    # State machine: FIRST -> SECOND -> LEADER
    first_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    second_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    leader_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    state: bpy.props.StringProperty(default='FIRST')  # type: ignore
    
    # Snap settings
    snap_radius: bpy.props.FloatProperty(default=20.0)  # Pixels  # type: ignore
    
    # Current snap point for drawing
    current_snap_point = None
    current_snap_screen = None
    is_snapped = False
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')
    
    def invoke(self, context, event):
        self.state = 'FIRST'
        self.first_point = (0, 0, 0)
        self.second_point = (0, 0, 0)
        self.leader_point = (0, 0, 0)
        self.current_snap_point = None
        self.current_snap_screen = None
        self.is_snapped = False
        
        # Add draw handler
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback, args, 'WINDOW', 'POST_PIXEL')
        
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('CROSSHAIR')
        context.area.header_text_set("Click first point for dimension (snaps to vertices)")
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            # Update snap point for visual feedback
            coord = (event.mouse_region_x, event.mouse_region_y)
            if self.state == 'LEADER':
                # For leader placement, just get plane point (no snapping needed)
                self.current_snap_point = self.get_plane_point(context, coord)
                self.current_snap_screen = coord
                self.is_snapped = False
            else:
                self.current_snap_point, self.current_snap_screen, self.is_snapped = self.get_snapped_point_with_screen(context, coord)
        
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.current_snap_point is None:
                self.report({'WARNING'}, "Could not determine point location")
                return {'RUNNING_MODAL'}
            
            if self.state == 'FIRST':
                self.first_point = self.current_snap_point
                self.state = 'SECOND'
                context.area.header_text_set("Click second point for dimension (snaps to vertices)")
                return {'RUNNING_MODAL'}
            
            elif self.state == 'SECOND':
                self.second_point = self.current_snap_point
                self.state = 'LEADER'
                context.area.header_text_set("Click to place dimension line")
                return {'RUNNING_MODAL'}
            
            elif self.state == 'LEADER':
                self.leader_point = self.current_snap_point
                self.create_dimension(context)
                self.finish(context)
                return {'FINISHED'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.finish(context)
            self.report({'INFO'}, "Dimension cancelled")
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    @staticmethod
    def draw_callback(self, context):
        """Draw visual feedback for snapping and dimension preview."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return
        
        # Draw snap indicator
        if self.current_snap_screen:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(2.0)
            
            x, y = self.current_snap_screen
            
            if self.is_snapped:
                # Green circle for snapped point
                color = (0.0, 1.0, 0.0, 1.0)
                radius = 10
            else:
                # Yellow circle for unsnapped point
                color = (1.0, 1.0, 0.0, 0.8)
                radius = 6
            
            # Draw circle
            import math
            segments = 32
            circle_verts = []
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                cx = x + radius * math.cos(angle)
                cy = y + radius * math.sin(angle)
                circle_verts.append((cx, cy))
            
            shader.bind()
            shader.uniform_float("color", color)
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": circle_verts})
            batch.draw(shader)
            
            # Draw crosshair inside circle if snapped
            if self.is_snapped:
                cross_size = 6
                cross_verts = [
                    (x - cross_size, y), (x + cross_size, y),
                    (x, y - cross_size), (x, y + cross_size),
                ]
                batch = batch_for_shader(shader, 'LINES', {"pos": cross_verts})
                batch.draw(shader)
        
        # Draw dimension preview after first point is set
        if self.state in ('SECOND', 'LEADER') and self.current_snap_point:
            p1 = Vector(self.first_point)
            
            if self.state == 'SECOND':
                p2 = Vector(self.current_snap_point)
            else:
                p2 = Vector(self.second_point)
            
            # Check if this is an elevation view
            is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
            
            # Initialize variables
            start_3d = None
            end_3d = None
            dim_length = 0
            
            if is_elevation:
                # Elevation view: work in wall's local coordinate system
                
                # Get wall rotation
                wall_rotation_z = 0
                source_wall_name = context.scene.get('SOURCE_WALL')
                if source_wall_name and source_wall_name in bpy.data.objects:
                    wall_obj = bpy.data.objects[source_wall_name]
                    wall_rotation_z = wall_obj.rotation_euler.z
                
                # Transform points to wall-local space (rotate around Z by -wall_rotation)
                rot_matrix = Matrix.Rotation(-wall_rotation_z, 4, 'Z')
                rot_matrix_inv = Matrix.Rotation(wall_rotation_z, 4, 'Z')
                
                p1_local = rot_matrix @ p1
                p2_local = rot_matrix @ p2
                
                delta_x = p2_local.x - p1_local.x
                delta_z = p2_local.z - p1_local.z
                
                if abs(delta_x) > 0.001 or abs(delta_z) > 0.001:
                    is_horizontal = abs(delta_x) >= abs(delta_z)
                    
                    if self.state == 'LEADER' and self.current_snap_point:
                        cursor_local = rot_matrix @ Vector(self.current_snap_point)
                    else:
                        cursor_local = None
                    
                    if is_horizontal:
                        dim_length = abs(delta_x)
                        left_x = min(p1_local.x, p2_local.x)
                        right_x = max(p1_local.x, p2_local.x)
                        
                        if cursor_local:
                            dim_z = cursor_local.z
                        else:
                            dim_z = min(p1_local.z, p2_local.z) - units.inch(4)
                        
                        # Create points in wall-local space then transform back
                        start_local = Vector((left_x, p1_local.y, dim_z))
                        end_local = Vector((right_x, p1_local.y, dim_z))
                        
                        l1_start_local = Vector((left_x, p1_local.y, p1_local.z if p1_local.x < p2_local.x else p2_local.z))
                        l1_end_local = Vector((left_x, p1_local.y, dim_z))
                        l2_start_local = Vector((right_x, p1_local.y, p2_local.z if p1_local.x < p2_local.x else p1_local.z))
                        l2_end_local = Vector((right_x, p1_local.y, dim_z))
                    else:
                        dim_length = abs(delta_z)
                        bottom_z = min(p1_local.z, p2_local.z)
                        top_z = max(p1_local.z, p2_local.z)
                        
                        if cursor_local:
                            dim_x = cursor_local.x
                        else:
                            dim_x = min(p1_local.x, p2_local.x) - units.inch(4)
                        
                        start_local = Vector((dim_x, p1_local.y, bottom_z))
                        end_local = Vector((dim_x, p1_local.y, top_z))
                        
                        l1_start_local = Vector((p1_local.x if p1_local.z < p2_local.z else p2_local.x, p1_local.y, bottom_z))
                        l1_end_local = Vector((dim_x, p1_local.y, bottom_z))
                        l2_start_local = Vector((p2_local.x if p1_local.z < p2_local.z else p1_local.x, p1_local.y, top_z))
                        l2_end_local = Vector((dim_x, p1_local.y, top_z))
                    
                    # Transform back to world space
                    start_3d = rot_matrix_inv @ start_local
                    end_3d = rot_matrix_inv @ end_local
                    leader1_start = rot_matrix_inv @ l1_start_local
                    leader1_end = rot_matrix_inv @ l1_end_local
                    leader2_start = rot_matrix_inv @ l2_start_local
                    leader2_end = rot_matrix_inv @ l2_end_local
            else:
                # Plan view: work in XY plane
                delta = p2 - p1
                
                if delta.length > 0.001:
                    is_horizontal = abs(delta.x) >= abs(delta.y)
                    
                    if self.state == 'LEADER' and self.current_snap_point:
                        cursor_pos = Vector(self.current_snap_point)
                    else:
                        cursor_pos = None
                    
                    if is_horizontal:
                        dim_length = abs(delta.x)
                        left_x = min(p1.x, p2.x)
                        right_x = max(p1.x, p2.x)
                        
                        if cursor_pos:
                            dim_y = cursor_pos.y
                        else:
                            dim_y = min(p1.y, p2.y) - units.inch(4)
                        
                        start_3d = Vector((left_x, dim_y, 0))
                        end_3d = Vector((right_x, dim_y, 0))
                        
                        leader1_start = Vector((left_x, p1.y if p1.x < p2.x else p2.y, 0))
                        leader1_end = Vector((left_x, dim_y, 0))
                        leader2_start = Vector((right_x, p2.y if p1.x < p2.x else p1.y, 0))
                        leader2_end = Vector((right_x, dim_y, 0))
                    else:
                        dim_length = abs(delta.y)
                        bottom_y = min(p1.y, p2.y)
                        top_y = max(p1.y, p2.y)
                        
                        if cursor_pos:
                            dim_x = cursor_pos.x
                        else:
                            dim_x = min(p1.x, p2.x) - units.inch(4)
                        
                        start_3d = Vector((dim_x, bottom_y, 0))
                        end_3d = Vector((dim_x, top_y, 0))
                        
                        leader1_start = Vector((p1.x if p1.y < p2.y else p2.x, bottom_y, 0))
                        leader1_end = Vector((dim_x, bottom_y, 0))
                        leader2_start = Vector((p2.x if p1.y < p2.y else p1.x, top_y, 0))
                        leader2_end = Vector((dim_x, top_y, 0))
            
            # Draw the preview if we have valid points
            if start_3d and end_3d:
                # Convert to screen coordinates
                start_2d = location_3d_to_region_2d(region, rv3d, start_3d)
                end_2d = location_3d_to_region_2d(region, rv3d, end_3d)
                leader1_start_2d = location_3d_to_region_2d(region, rv3d, leader1_start)
                leader1_end_2d = location_3d_to_region_2d(region, rv3d, leader1_end)
                leader2_start_2d = location_3d_to_region_2d(region, rv3d, leader2_start)
                leader2_end_2d = location_3d_to_region_2d(region, rv3d, leader2_end)
                
                if start_2d and end_2d:
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    gpu.state.line_width_set(2.0)
                    
                    # Draw dimension line (cyan)
                    shader.bind()
                    shader.uniform_float("color", (0.0, 1.0, 1.0, 1.0))
                    
                    line_verts = [(start_2d.x, start_2d.y), (end_2d.x, end_2d.y)]
                    batch = batch_for_shader(shader, 'LINES', {"pos": line_verts})
                    batch.draw(shader)
                    
                    # Draw leader lines (cyan, lighter)
                    shader.uniform_float("color", (0.0, 0.8, 0.8, 0.6))
                    
                    if leader1_start_2d and leader1_end_2d:
                        leader_verts = [(leader1_start_2d.x, leader1_start_2d.y), 
                                       (leader1_end_2d.x, leader1_end_2d.y)]
                        batch = batch_for_shader(shader, 'LINES', {"pos": leader_verts})
                        batch.draw(shader)
                    
                    if leader2_start_2d and leader2_end_2d:
                        leader_verts = [(leader2_start_2d.x, leader2_start_2d.y), 
                                       (leader2_end_2d.x, leader2_end_2d.y)]
                        batch = batch_for_shader(shader, 'LINES', {"pos": leader_verts})
                        batch.draw(shader)
                    
                    # Draw dimension text
                    mid_2d = ((start_2d.x + end_2d.x) / 2, (start_2d.y + end_2d.y) / 2)
                    
                    # Format dimension in inches and fractional
                    dim_inches = dim_length / units.inch(1)
                    whole_inches = int(dim_inches)
                    frac = dim_inches - whole_inches
                    
                    # Convert to nearest 1/16
                    sixteenths = round(frac * 16)
                    if sixteenths == 16:
                        whole_inches += 1
                        sixteenths = 0
                    
                    if sixteenths == 0:
                        dim_text = f'{whole_inches}"'
                    elif sixteenths == 8:
                        dim_text = f'{whole_inches} 1/2"'
                    elif sixteenths == 4:
                        dim_text = f'{whole_inches} 1/4"'
                    elif sixteenths == 12:
                        dim_text = f'{whole_inches} 3/4"'
                    else:
                        # Simplify fraction
                        from math import gcd
                        g = gcd(sixteenths, 16)
                        num = sixteenths // g
                        denom = 16 // g
                        dim_text = f'{whole_inches} {num}/{denom}"'
                    
                    # Draw text background
                    font_id = 0
                    blf.size(font_id, 14)
                    text_width, text_height = blf.dimensions(font_id, dim_text)
                    
                    # Background rectangle
                    padding = 4
                    bg_verts = [
                        (mid_2d[0] - text_width/2 - padding, mid_2d[1] - text_height/2 - padding),
                        (mid_2d[0] + text_width/2 + padding, mid_2d[1] - text_height/2 - padding),
                        (mid_2d[0] + text_width/2 + padding, mid_2d[1] + text_height/2 + padding),
                        (mid_2d[0] - text_width/2 - padding, mid_2d[1] + text_height/2 + padding),
                    ]
                    bg_indices = [(0, 1, 2), (2, 3, 0)]
                    
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    shader.bind()
                    shader.uniform_float("color", (0.1, 0.1, 0.1, 0.9))
                    batch = batch_for_shader(shader, 'TRIS', {"pos": bg_verts}, indices=bg_indices)
                    batch.draw(shader)
                    
                    # Draw text
                    blf.position(font_id, mid_2d[0] - text_width/2, mid_2d[1] - text_height/2, 0)
                    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
                    blf.draw(font_id, dim_text)
            
            gpu.state.blend_set('NONE')
            gpu.state.line_width_set(1.0)
    
    def get_snapped_point_with_screen(self, context, coord):
        """Get 3D point with snapping and return screen position too."""
        
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        # Get depsgraph for evaluated meshes (geometry nodes)
        depsgraph = context.evaluated_depsgraph_get()
        
        # Try to find nearest vertex to snap to
        best_dist = self.snap_radius
        best_point = None
        is_snapped = False
        
        for obj in context.scene.objects:
            # Skip annotation objects
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            # Check collection instances
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices_with_dist(
                    context, obj, coord, region, rv3d, depsgraph, best_dist, is_elevation)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    is_snapped = True
                continue
            
            # Check regular mesh objects
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            # Get evaluated mesh (handles geometry nodes)
            eval_obj = obj.evaluated_get(depsgraph)
            try:
                eval_mesh = eval_obj.to_mesh()
                if eval_mesh:
                    for vert in eval_mesh.vertices:
                        world_co = matrix_world @ vert.co
                        screen_co = location_3d_to_region_2d(region, rv3d, world_co)
                        if screen_co is None:
                            continue
                        
                        dist = (Vector(coord) - screen_co).length
                        
                        if dist < best_dist:
                            best_dist = dist
                            # Keep full 3D coordinates - projection happens in create_dimension
                            best_point = (world_co.x, world_co.y, world_co.z)
                            is_snapped = True
                    
                    eval_obj.to_mesh_clear()
            except:
                pass
        
        # If we found a snap point, use it
        if best_point:
            screen_pos = location_3d_to_region_2d(region, rv3d, Vector(best_point))
            return best_point, (screen_pos.x, screen_pos.y) if screen_pos else None, True
        
        # Otherwise fall back to plane intersection
        plane_point = self.get_plane_point(context, coord)
        if plane_point:
            return plane_point, coord, False
        
        return None, None, False
    
    def _check_collection_vertices_with_dist(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist, is_elevation=False):
        """Check vertices in a collection instance and return best point with distance."""

        if not instance_obj.instance_collection:
            return None, float('inf')
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        
        for obj in instance_obj.instance_collection.objects:
            if obj.type != 'MESH':
                continue
            
            # Combined matrix: instance transform + object transform
            matrix_world = instance_matrix @ obj.matrix_world
            
            # Get evaluated mesh (handles geometry nodes)
            eval_obj = obj.evaluated_get(depsgraph)
            try:
                eval_mesh = eval_obj.to_mesh()
                if eval_mesh:
                    for vert in eval_mesh.vertices:
                        world_co = matrix_world @ vert.co
                        screen_co = location_3d_to_region_2d(region, rv3d, world_co)
                        if screen_co is None:
                            continue
                        
                        dist = (Vector(coord) - screen_co).length
                        
                        if dist < best_dist:
                            best_dist = dist
                            # Keep full 3D coordinates
                            best_point = (world_co.x, world_co.y, world_co.z)
                    
                    eval_obj.to_mesh_clear()
            except:
                pass
        
        return best_point, best_dist
    
    def get_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the appropriate layout plane.
        
        For plan views: projects to Z=0 (XY plane)
        For elevation views: projects to wall's plane (vertical plane aligned with wall)
        """
        
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        if is_elevation:
            # Get wall rotation to determine plane orientation
            wall_rotation_z = 0
            source_wall_name = context.scene.get('SOURCE_WALL')
            if source_wall_name and source_wall_name in bpy.data.objects:
                wall_obj = bpy.data.objects[source_wall_name]
                wall_rotation_z = wall_obj.rotation_euler.z
            
            # Plane normal is perpendicular to wall (points away from camera)
            # For wall with rotation 0, normal is (0, 1, 0)
            # Rotate this normal by wall's Z rotation
            plane_normal = Vector((0, 1, 0))
            rot_matrix = Matrix.Rotation(wall_rotation_z, 3, 'Z')
            plane_normal = rot_matrix @ plane_normal
            
            # Ray-plane intersection: plane passes through origin
            denom = direction.dot(plane_normal)
            if abs(denom) < 0.0001:
                return None
            
            t = -origin.dot(plane_normal) / denom
            point = origin + direction * t
            return (point.x, point.y, point.z)
        
        # Plan/multi views: XY plane (Z=0)
        if abs(direction.z) < 0.0001:
            return None
        t = -origin.z / direction.z
        point = origin + direction * t
        return (point.x, point.y, 0)
    
    def create_dimension(self, context):
        """Create a linear dimension annotation between the two clicked points."""
        
        p1 = Vector(self.first_point)
        p2 = Vector(self.second_point)
        leader_pos = Vector(self.leader_point)
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        if is_elevation:
            # Get wall rotation from the source wall or camera
            wall_rotation_z = 0
            source_wall_name = context.scene.get('SOURCE_WALL')
            if source_wall_name and source_wall_name in bpy.data.objects:
                wall_obj = bpy.data.objects[source_wall_name]
                wall_rotation_z = wall_obj.rotation_euler.z
            
            # Create rotation matrix to transform points into wall's local 2D space
            # Wall's local X runs along wall length, local Z is up
            rot_matrix = Matrix.Rotation(-wall_rotation_z, 4, 'Z')
            
            # Transform points to wall-local space
            p1_local = rot_matrix @ p1
            p2_local = rot_matrix @ p2
            leader_local = rot_matrix @ leader_pos
            
            # Now work in wall's local XZ plane
            delta_x = p2_local.x - p1_local.x
            delta_z = p2_local.z - p1_local.z
            
            if abs(delta_x) < 0.001 and abs(delta_z) < 0.001:
                self.report({'WARNING'}, "Points are too close together")
                return
            
            is_horizontal = abs(delta_x) >= abs(delta_z)
            
            if is_horizontal:
                dim_length = abs(delta_x)
                left_x = min(p1_local.x, p2_local.x)
                
                ref_z = p1_local.z if p1_local.x == left_x else p2_local.z
                leader_length = leader_local.z - ref_z
                
                # Start point in wall-local space
                start_local = Vector((left_x, p1_local.y, ref_z))
                # Horizontal dimension: rotated to stand up in wall plane
                local_rotation = (math.pi / 2, 0, 0)
            else:
                dim_length = abs(delta_z)
                bottom_z = min(p1_local.z, p2_local.z)
                
                ref_x = p1_local.x if p1_local.z == bottom_z else p2_local.x
                leader_length = -(leader_local.x - ref_x)
                
                # Start point in wall-local space
                start_local = Vector((ref_x, p1_local.y, bottom_z))
                # Vertical dimension
                local_rotation = (0, -math.pi / 2, math.pi / 2)
            
            # Transform start point back to world space
            rot_matrix_inv = Matrix.Rotation(wall_rotation_z, 4, 'Z')
            start_point = rot_matrix_inv @ start_local
            
            # Combine local rotation with wall rotation
            local_euler = Euler(local_rotation, 'XYZ')
            wall_euler = Euler((0, 0, wall_rotation_z), 'XYZ')
            
            # Apply rotations: first local, then wall
            combined_matrix = wall_euler.to_matrix().to_4x4() @ local_euler.to_matrix().to_4x4()
            rotation = combined_matrix.to_euler('XYZ')
        else:
            # Plan view: work in XY plane
            delta = p2 - p1
            
            if delta.length < 0.001:
                self.report({'WARNING'}, "Points are too close together")
                return
            
            is_horizontal = abs(delta.x) >= abs(delta.y)
            
            if is_horizontal:
                dim_length = abs(delta.x)
                left_x = min(p1.x, p2.x)
                
                ref_y = p1.y if p1.x == left_x else p2.y
                leader_length = leader_pos.y - ref_y
                
                start_point = Vector((left_x, ref_y, 0))
                rotation = (0, 0, 0)
            else:
                dim_length = abs(delta.y)
                bottom_y = min(p1.y, p2.y)
                
                ref_x = p1.x if p1.y == bottom_y else p2.x
                leader_length = -(leader_pos.x - ref_x)
                
                start_point = Vector((ref_x, bottom_y, 0))
                rotation = (0, 0, math.pi / 2)
        
        dim = hb_types.GeoNodeDimension()
        dim.create(f"Dimension_{len([o for o in context.scene.objects if 'IS_2D_ANNOTATION' in o])}")
        
        for scene in bpy.data.scenes:
            if dim.obj.name in scene.collection.objects:
                scene.collection.objects.unlink(dim.obj)
        
        context.scene.collection.objects.link(dim.obj)
        
        dim.obj.location = start_point
        dim.obj.rotation_euler = rotation
        
        # Set dimension length via curve endpoint
        if dim.obj.data.splines and len(dim.obj.data.splines[0].points) > 1:
            dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
        # Set leader length
        dim.set_input("Leader Length", leader_length)
        
        # Apply dimension settings from scene
        hb_scene = context.scene.home_builder
        dim.set_input("Text Size", hb_scene.annotation_dimension_text_size)
        dim.set_input("Tick Length", hb_scene.annotation_dimension_tick_length)
        
        bpy.ops.object.select_all(action='DESELECT')
        dim.obj.select_set(True)
        context.view_layer.objects.active = dim.obj
    
    def finish(self, context):
        """Clean up operator state."""
        # Remove draw handler
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        
        context.window.cursor_set('DEFAULT')
        context.area.header_text_set(None)
        context.area.tag_redraw()


class home_builder_layouts_OT_add_dimension_3d(bpy.types.Operator):
    bl_idname = "home_builder_layouts.add_dimension_3d"
    bl_label = "Add Dimension (3D View)"
    bl_description = "Click two points to add a dimension in 3D view (works from any angle)"
    bl_options = {'UNDO'}
    
    # State machine: FIRST -> SECOND -> LEADER
    first_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    second_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    leader_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    state: bpy.props.StringProperty(default='FIRST')  # type: ignore
    
    # Snap settings
    snap_radius: bpy.props.FloatProperty(default=20.0)  # type: ignore
    
    # Current snap point for drawing
    current_snap_point = None
    current_snap_screen = None
    is_snapped = False
    
    # View plane info
    view_plane = 'XY'  # 'XY', 'XZ', or 'YZ'
    plane_normal = None
    plane_point = None
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        # Works in any 3D view that's not a layout view
        return context.area and context.area.type == 'VIEW_3D'
    
    def invoke(self, context, event):
        self.state = 'FIRST'
        self.first_point = (0, 0, 0)
        self.second_point = (0, 0, 0)
        self.leader_point = (0, 0, 0)
        self.current_snap_point = None
        self.current_snap_screen = None
        self.is_snapped = False
        
        # Determine view plane based on current view direction
        self._detect_view_plane(context)
        
        # Add draw handler
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, 'WINDOW', 'POST_PIXEL')
        
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('CROSSHAIR')
        context.area.header_text_set(f"Click first point for dimension (snaps to vertices) - Plane: {self.view_plane}")
        
        return {'RUNNING_MODAL'}
    
    def _detect_view_plane(self, context):
        """Detect which plane the user is most aligned with based on view direction."""

        rv3d = context.region_data
        if not rv3d:
            self.view_plane = 'XY'
            self.plane_normal = Vector((0, 0, 1))
            return
        
        # Get view direction (camera looks down -Z in view space)
        view_matrix = rv3d.view_matrix.inverted()
        view_direction = Vector((0, 0, -1))
        view_direction.rotate(view_matrix.to_euler())
        view_direction.normalize()
        
        # Check which axis the view is most aligned with
        abs_x = abs(view_direction.x)
        abs_y = abs(view_direction.y)
        abs_z = abs(view_direction.z)
        
        if abs_z >= abs_x and abs_z >= abs_y:
            # Looking down Z axis - use XY plane
            self.view_plane = 'XY'
            self.plane_normal = Vector((0, 0, 1))
        elif abs_y >= abs_x and abs_y >= abs_z:
            # Looking down Y axis - use XZ plane
            self.view_plane = 'XZ'
            self.plane_normal = Vector((0, 1, 0))
        else:
            # Looking down X axis - use YZ plane
            self.view_plane = 'YZ'
            self.plane_normal = Vector((1, 0, 0))
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            coord = (event.mouse_region_x, event.mouse_region_y)
            if self.state == 'LEADER':
                self.current_snap_point = self._get_plane_point(context, coord)
                self.current_snap_screen = coord
                self.is_snapped = False
            else:
                self.current_snap_point, self.current_snap_screen, self.is_snapped = self._get_snapped_point(context, coord)
        
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.current_snap_point is None:
                self.report({'WARNING'}, "Could not determine point location")
                return {'RUNNING_MODAL'}
            
            if self.state == 'FIRST':
                self.first_point = self.current_snap_point
                self.state = 'SECOND'
                context.area.header_text_set(f"Click second point for dimension - Plane: {self.view_plane}")
                return {'RUNNING_MODAL'}
            
            elif self.state == 'SECOND':
                self.second_point = self.current_snap_point
                self.state = 'LEADER'
                context.area.header_text_set("Click to place dimension line")
                return {'RUNNING_MODAL'}
            
            elif self.state == 'LEADER':
                self.leader_point = self.current_snap_point
                self._create_dimension(context)
                self._finish(context)
                return {'FINISHED'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._finish(context)
            self.report({'INFO'}, "Dimension cancelled")
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def _get_plane_point(self, context, coord):
        """Get point on the detected view plane, passing through first_point if set."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        # Ray-plane intersection
        # Plane passes through first_point (or origin if not set)
        if self.state != 'FIRST' and self.first_point:
            plane_origin = Vector(self.first_point)
        else:
            plane_origin = Vector((0, 0, 0))
        
        denom = direction.dot(self.plane_normal)
        if abs(denom) < 0.0001:
            return None
        
        # Calculate intersection: t = (plane_origin - ray_origin) · normal / (direction · normal)
        t = (plane_origin - origin).dot(self.plane_normal) / denom
        point = origin + direction * t
        return (point.x, point.y, point.z)
    
    def _get_snapped_point(self, context, coord):
        """Get 3D point with snapping to nearest vertex."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.snap_radius
        best_point = None
        is_snapped = False
        
        for obj in context.visible_objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            eval_obj = obj.evaluated_get(depsgraph)
            try:
                eval_mesh = eval_obj.to_mesh()
                if eval_mesh:
                    for vert in eval_mesh.vertices:
                        world_co = matrix_world @ vert.co
                        screen_co = location_3d_to_region_2d(region, rv3d, world_co)
                        if screen_co is None:
                            continue
                        
                        dist = (Vector(coord) - screen_co).length
                        
                        if dist < best_dist:
                            best_dist = dist
                            # Keep actual vertex position - don't project
                            best_point = (world_co.x, world_co.y, world_co.z)
                            is_snapped = True
                    
                    eval_obj.to_mesh_clear()
            except:
                pass
        
        if best_point:
            screen_pos = location_3d_to_region_2d(region, rv3d, Vector(best_point))
            return best_point, (screen_pos.x, screen_pos.y) if screen_pos else None, True
        
        plane_point = self._get_plane_point(context, coord)
        if plane_point:
            return plane_point, coord, False
        
        return None, None, False
    
    def _project_to_plane(self, point):
        """Project a 3D point onto the view plane."""

        p = Vector(point)
        
        # Project onto plane passing through first_point (or origin if not set)
        if self.state != 'FIRST':
            plane_origin = Vector(self.first_point)
        else:
            plane_origin = Vector((0, 0, 0))
        
        # Distance from point to plane
        dist = (p - plane_origin).dot(self.plane_normal)
        
        # Project point onto plane
        projected = p - self.plane_normal * dist
        
        return (projected.x, projected.y, projected.z)
    
    @staticmethod
    def draw_callback_3d(self, context):
        """Draw visual feedback for snapping and dimension preview."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return
        
        # Draw snap indicator
        if self.current_snap_screen:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(2.0)
            
            x, y = self.current_snap_screen
            
            if self.is_snapped:
                color = (0.0, 1.0, 0.0, 1.0)
                radius = 10
            else:
                color = (1.0, 1.0, 0.0, 0.8)
                radius = 6
            
            segments = 32
            circle_verts = []
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                cx = x + radius * math.cos(angle)
                cy = y + radius * math.sin(angle)
                circle_verts.append((cx, cy))
            
            shader.bind()
            shader.uniform_float("color", color)
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": circle_verts})
            batch.draw(shader)
            
            if self.is_snapped:
                cross_size = 6
                cross_verts = [
                    (x - cross_size, y), (x + cross_size, y),
                    (x, y - cross_size), (x, y + cross_size),
                ]
                batch = batch_for_shader(shader, 'LINES', {"pos": cross_verts})
                batch.draw(shader)
        
        # Draw dimension preview
        if self.state in ('SECOND', 'LEADER') and self.current_snap_point:
            p1 = Vector(self.first_point)
            
            if self.state == 'SECOND':
                p2 = Vector(self.current_snap_point)
            else:
                p2 = Vector(self.second_point)
            
            # Calculate in the view plane's coordinate system
            if self.view_plane == 'XY':
                delta_h = p2.x - p1.x
                delta_v = p2.y - p1.y
            elif self.view_plane == 'XZ':
                delta_h = p2.x - p1.x
                delta_v = p2.z - p1.z
            else:  # YZ
                delta_h = p2.y - p1.y
                delta_v = p2.z - p1.z
            
            if abs(delta_h) > 0.001 or abs(delta_v) > 0.001:
                is_horizontal = abs(delta_h) >= abs(delta_v)
                
                if self.state == 'LEADER' and self.current_snap_point:
                    cursor_pos = Vector(self.current_snap_point)
                else:
                    cursor_pos = None
                
                # Calculate dimension line positions based on view plane
                if self.view_plane == 'XY':
                    if is_horizontal:
                        dim_length = abs(delta_h)
                        left = min(p1.x, p2.x)
                        right = max(p1.x, p2.x)
                        dim_pos = cursor_pos.y if cursor_pos else min(p1.y, p2.y) - units.inch(4)
                        
                        start_3d = Vector((left, dim_pos, p1.z))
                        end_3d = Vector((right, dim_pos, p1.z))
                        leader1_start = Vector((left, p1.y if p1.x < p2.x else p2.y, p1.z))
                        leader1_end = Vector((left, dim_pos, p1.z))
                        leader2_start = Vector((right, p2.y if p1.x < p2.x else p1.y, p1.z))
                        leader2_end = Vector((right, dim_pos, p1.z))
                    else:
                        dim_length = abs(delta_v)
                        bottom = min(p1.y, p2.y)
                        top = max(p1.y, p2.y)
                        dim_pos = cursor_pos.x if cursor_pos else min(p1.x, p2.x) - units.inch(4)
                        
                        start_3d = Vector((dim_pos, bottom, p1.z))
                        end_3d = Vector((dim_pos, top, p1.z))
                        leader1_start = Vector((p1.x if p1.y < p2.y else p2.x, bottom, p1.z))
                        leader1_end = Vector((dim_pos, bottom, p1.z))
                        leader2_start = Vector((p2.x if p1.y < p2.y else p1.x, top, p1.z))
                        leader2_end = Vector((dim_pos, top, p1.z))
                
                elif self.view_plane == 'XZ':
                    if is_horizontal:
                        dim_length = abs(delta_h)
                        left = min(p1.x, p2.x)
                        right = max(p1.x, p2.x)
                        dim_pos = cursor_pos.z if cursor_pos else min(p1.z, p2.z) - units.inch(4)
                        
                        start_3d = Vector((left, p1.y, dim_pos))
                        end_3d = Vector((right, p1.y, dim_pos))
                        leader1_start = Vector((left, p1.y, p1.z if p1.x < p2.x else p2.z))
                        leader1_end = Vector((left, p1.y, dim_pos))
                        leader2_start = Vector((right, p1.y, p2.z if p1.x < p2.x else p1.z))
                        leader2_end = Vector((right, p1.y, dim_pos))
                    else:
                        dim_length = abs(delta_v)
                        bottom = min(p1.z, p2.z)
                        top = max(p1.z, p2.z)
                        dim_pos = cursor_pos.x if cursor_pos else min(p1.x, p2.x) - units.inch(4)
                        
                        start_3d = Vector((dim_pos, p1.y, bottom))
                        end_3d = Vector((dim_pos, p1.y, top))
                        leader1_start = Vector((p1.x if p1.z < p2.z else p2.x, p1.y, bottom))
                        leader1_end = Vector((dim_pos, p1.y, bottom))
                        leader2_start = Vector((p2.x if p1.z < p2.z else p1.x, p1.y, top))
                        leader2_end = Vector((dim_pos, p1.y, top))
                
                else:  # YZ plane
                    if is_horizontal:
                        dim_length = abs(delta_h)
                        left = min(p1.y, p2.y)
                        right = max(p1.y, p2.y)
                        dim_pos = cursor_pos.z if cursor_pos else min(p1.z, p2.z) - units.inch(4)
                        
                        start_3d = Vector((p1.x, left, dim_pos))
                        end_3d = Vector((p1.x, right, dim_pos))
                        leader1_start = Vector((p1.x, left, p1.z if p1.y < p2.y else p2.z))
                        leader1_end = Vector((p1.x, left, dim_pos))
                        leader2_start = Vector((p1.x, right, p2.z if p1.y < p2.y else p1.z))
                        leader2_end = Vector((p1.x, right, dim_pos))
                    else:
                        dim_length = abs(delta_v)
                        bottom = min(p1.z, p2.z)
                        top = max(p1.z, p2.z)
                        dim_pos = cursor_pos.y if cursor_pos else min(p1.y, p2.y) - units.inch(4)
                        
                        start_3d = Vector((p1.x, dim_pos, bottom))
                        end_3d = Vector((p1.x, dim_pos, top))
                        leader1_start = Vector((p1.x, p1.y if p1.z < p2.z else p2.y, bottom))
                        leader1_end = Vector((p1.x, dim_pos, bottom))
                        leader2_start = Vector((p1.x, p2.y if p1.z < p2.z else p1.y, top))
                        leader2_end = Vector((p1.x, dim_pos, top))
                
                # Convert to screen and draw
                start_2d = location_3d_to_region_2d(region, rv3d, start_3d)
                end_2d = location_3d_to_region_2d(region, rv3d, end_3d)
                l1_start_2d = location_3d_to_region_2d(region, rv3d, leader1_start)
                l1_end_2d = location_3d_to_region_2d(region, rv3d, leader1_end)
                l2_start_2d = location_3d_to_region_2d(region, rv3d, leader2_start)
                l2_end_2d = location_3d_to_region_2d(region, rv3d, leader2_end)
                
                if start_2d and end_2d:
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    gpu.state.line_width_set(2.0)
                    
                    shader.bind()
                    shader.uniform_float("color", (0.0, 1.0, 1.0, 1.0))
                    
                    line_verts = [(start_2d.x, start_2d.y), (end_2d.x, end_2d.y)]
                    batch = batch_for_shader(shader, 'LINES', {"pos": line_verts})
                    batch.draw(shader)
                    
                    shader.uniform_float("color", (0.0, 0.8, 0.8, 0.6))
                    
                    if l1_start_2d and l1_end_2d:
                        batch = batch_for_shader(shader, 'LINES', {"pos": [(l1_start_2d.x, l1_start_2d.y), (l1_end_2d.x, l1_end_2d.y)]})
                        batch.draw(shader)
                    
                    if l2_start_2d and l2_end_2d:
                        batch = batch_for_shader(shader, 'LINES', {"pos": [(l2_start_2d.x, l2_start_2d.y), (l2_end_2d.x, l2_end_2d.y)]})
                        batch.draw(shader)
                    
                    # Draw dimension text
                    mid_2d = ((start_2d.x + end_2d.x) / 2, (start_2d.y + end_2d.y) / 2)
                    
                    dim_inches = dim_length / units.inch(1)
                    whole_inches = int(dim_inches)
                    frac = dim_inches - whole_inches
                    sixteenths = round(frac * 16)
                    if sixteenths == 16:
                        whole_inches += 1
                        sixteenths = 0
                    
                    if sixteenths == 0:
                        dim_text = f'{whole_inches}"'
                    elif sixteenths == 8:
                        dim_text = f'{whole_inches} 1/2"'
                    elif sixteenths == 4:
                        dim_text = f'{whole_inches} 1/4"'
                    elif sixteenths == 12:
                        dim_text = f'{whole_inches} 3/4"'
                    else:
                        from math import gcd
                        g = gcd(sixteenths, 16)
                        num = sixteenths // g
                        denom = 16 // g
                        dim_text = f'{whole_inches} {num}/{denom}"'
                    
                    font_id = 0
                    blf.size(font_id, 14)
                    text_width, text_height = blf.dimensions(font_id, dim_text)
                    
                    padding = 4
                    bg_verts = [
                        (mid_2d[0] - text_width/2 - padding, mid_2d[1] - text_height/2 - padding),
                        (mid_2d[0] + text_width/2 + padding, mid_2d[1] - text_height/2 - padding),
                        (mid_2d[0] + text_width/2 + padding, mid_2d[1] + text_height/2 + padding),
                        (mid_2d[0] - text_width/2 - padding, mid_2d[1] + text_height/2 + padding),
                    ]
                    bg_indices = [(0, 1, 2), (2, 3, 0)]
                    
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    shader.bind()
                    shader.uniform_float("color", (0.1, 0.1, 0.1, 0.9))
                    batch = batch_for_shader(shader, 'TRIS', {"pos": bg_verts}, indices=bg_indices)
                    batch.draw(shader)
                    
                    blf.position(font_id, mid_2d[0] - text_width/2, mid_2d[1] - text_height/2, 0)
                    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
                    blf.draw(font_id, dim_text)
            
            gpu.state.blend_set('NONE')
            gpu.state.line_width_set(1.0)
    
    def _create_dimension(self, context):
        """Create dimension based on detected view plane."""
        
        p1 = Vector(self.first_point)
        p2 = Vector(self.second_point)
        leader_pos = Vector(self.leader_point)
        
        # Calculate based on view plane
        if self.view_plane == 'XY':
            delta_h = p2.x - p1.x
            delta_v = p2.y - p1.y
            is_horizontal = abs(delta_h) >= abs(delta_v)
            
            if is_horizontal:
                dim_length = abs(delta_h)
                left_val = min(p1.x, p2.x)
                ref_v = p1.y if p1.x == left_val else p2.y
                leader_length = leader_pos.y - ref_v
                start_point = Vector((left_val, ref_v, p1.z))
                rotation = (0, 0, 0)
            else:
                dim_length = abs(delta_v)
                bottom_val = min(p1.y, p2.y)
                ref_h = p1.x if p1.y == bottom_val else p2.x
                leader_length = -(leader_pos.x - ref_h)
                start_point = Vector((ref_h, bottom_val, p1.z))
                rotation = (0, 0, math.pi / 2)
        
        elif self.view_plane == 'XZ':
            delta_h = p2.x - p1.x
            delta_v = p2.z - p1.z
            is_horizontal = abs(delta_h) >= abs(delta_v)
            
            if is_horizontal:
                dim_length = abs(delta_h)
                left_val = min(p1.x, p2.x)
                ref_v = p1.z if p1.x == left_val else p2.z
                leader_length = leader_pos.z - ref_v
                start_point = Vector((left_val, p1.y, ref_v))
                rotation = (math.pi / 2, 0, 0)
            else:
                dim_length = abs(delta_v)
                bottom_val = min(p1.z, p2.z)
                ref_h = p1.x if p1.z == bottom_val else p2.x
                leader_length = -(leader_pos.x - ref_h)
                start_point = Vector((ref_h, p1.y, bottom_val))
                rotation = (0, -math.pi / 2, math.pi / 2)
        
        else:  # YZ plane
            delta_h = p2.y - p1.y
            delta_v = p2.z - p1.z
            is_horizontal = abs(delta_h) >= abs(delta_v)
            
            if is_horizontal:
                dim_length = abs(delta_h)
                left_val = min(p1.y, p2.y)
                ref_v = p1.z if p1.y == left_val else p2.z
                leader_length = leader_pos.z - ref_v
                start_point = Vector((p1.x, left_val, ref_v))
                rotation = (math.pi / 2, 0, math.pi / 2)
            else:
                dim_length = abs(delta_v)
                bottom_val = min(p1.z, p2.z)
                ref_h = p1.y if p1.z == bottom_val else p2.y
                leader_length = -(leader_pos.y - ref_h)
                start_point = Vector((p1.x, ref_h, bottom_val))
                rotation = (0, -math.pi / 2, 0)
        
        if dim_length < 0.001:
            self.report({'WARNING'}, "Points are too close together")
            return
        
        dim = hb_types.GeoNodeDimension()
        dim.create(f"Dimension_{len([o for o in context.scene.objects if 'IS_2D_ANNOTATION' in o])}")
        
        for scene in bpy.data.scenes:
            if dim.obj.name in scene.collection.objects:
                scene.collection.objects.unlink(dim.obj)
        
        context.scene.collection.objects.link(dim.obj)
        
        dim.obj.location = start_point
        dim.obj.rotation_euler = rotation
        
        if dim.obj.data.splines and len(dim.obj.data.splines[0].points) > 1:
            dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
        dim.set_input("Leader Length", leader_length)
        
        bpy.ops.object.select_all(action='DESELECT')
        dim.obj.select_set(True)
        context.view_layer.objects.active = dim.obj
    
    def _finish(self, context):
        """Clean up operator state."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        
        context.window.cursor_set('DEFAULT')
        context.area.header_text_set(None)
        context.area.tag_redraw()


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    home_builder_layouts_OT_create_elevation_view,
    home_builder_layouts_OT_create_plan_view,
    home_builder_layouts_OT_create_3d_view,
    home_builder_layouts_OT_create_all_elevations,
    home_builder_layouts_OT_create_multi_view,
    home_builder_layouts_OT_update_elevation_view,
    home_builder_layouts_OT_delete_layout_view,
    home_builder_layouts_OT_go_to_layout_view,
    home_builder_layouts_OT_fit_view_to_content,
    home_builder_layouts_OT_render_layout,
    home_builder_layouts_OT_add_dimension,
    home_builder_layouts_OT_add_dimension_3d,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Layout view scene properties with update callbacks
    bpy.types.Scene.hb_layout_scale = bpy.props.EnumProperty(
        name="Scale",
        description="Drawing scale",
        items=[
            ('3"=1\'', '3" = 1\'', 'Very detailed - 1:4'),
            ('1-1/2"=1\'', '1-1/2" = 1\'', '1:8'),
            ('1"=1\'', '1" = 1\'', '1:12'),
            ('3/4"=1\'', '3/4" = 1\'', '1:16'),
            ('1/2"=1\'', '1/2" = 1\'', '1:24'),
            ('3/8"=1\'', '3/8" = 1\'', '1:32'),
            ('1/4"=1\'', '1/4" = 1\'', '1:48 - Common for elevations'),
            ('3/16"=1\'', '3/16" = 1\'', '1:64'),
            ('1/8"=1\'', '1/8" = 1\'', '1:96 - Common for floor plans'),
            ('1/16"=1\'', '1/16" = 1\'', '1:192'),
        ],
        default='1/4"=1\'',
        update=update_layout_scale
    )
    
    bpy.types.Scene.hb_paper_size = bpy.props.EnumProperty(
        name="Paper Size",
        description="Paper size for rendering",
        items=[
            ('LETTER', 'Letter (8.5" x 11")', ''),
            ('LEGAL', 'Legal (8.5" x 14")', ''),
            ('TABLOID', 'Tabloid (11" x 17")', ''),
            ('A4', 'A4 (210 x 297mm)', ''),
            ('A3', 'A3 (297 x 420mm)', ''),
        ],
        default='TABLOID',
        update=update_paper_size
    )
    
    bpy.types.Scene.hb_paper_landscape = bpy.props.BoolProperty(
        name="Landscape",
        description="Use landscape orientation",
        default=True,
        update=update_paper_orientation
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.hb_layout_scale
    del bpy.types.Scene.hb_paper_size
    del bpy.types.Scene.hb_paper_landscape
