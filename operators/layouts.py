import bpy
import os
from .. import hb_layouts
from .. import hb_types

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
    bl_description = "Click two points to add a linear dimension annotation (snaps to vertices)"
    bl_options = {'UNDO'}
    
    # State machine
    first_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    second_point: bpy.props.FloatVectorProperty(size=3)  # type: ignore
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
        import gpu
        from gpu_extras.batch import batch_for_shader
        import blf
        from mathutils import Vector
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        from .. import units
        
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
        if self.state == 'SECOND' and self.current_snap_point:
            p1 = Vector(self.first_point)
            p2 = Vector(self.current_snap_point)
            
            delta = p2 - p1
            
            if delta.length > 0.001:
                # Determine horizontal or vertical
                is_horizontal = abs(delta.x) >= abs(delta.y)
                
                if is_horizontal:
                    dim_length = abs(delta.x)
                    # Preview line positions
                    left_x = min(p1.x, p2.x)
                    right_x = max(p1.x, p2.x)
                    dim_y = min(p1.y, p2.y) - units.inch(4)
                    
                    start_3d = Vector((left_x, dim_y, 0))
                    end_3d = Vector((right_x, dim_y, 0))
                    
                    # Leader lines
                    leader1_start = Vector((left_x, min(p1.y, p2.y), 0))
                    leader1_end = Vector((left_x, dim_y, 0))
                    leader2_start = Vector((right_x, min(p1.y, p2.y), 0))
                    leader2_end = Vector((right_x, dim_y, 0))
                else:
                    dim_length = abs(delta.y)
                    # Preview line positions
                    bottom_y = min(p1.y, p2.y)
                    top_y = max(p1.y, p2.y)
                    dim_x = min(p1.x, p2.x) - units.inch(4)
                    
                    start_3d = Vector((dim_x, bottom_y, 0))
                    end_3d = Vector((dim_x, top_y, 0))
                    
                    # Leader lines
                    leader1_start = Vector((min(p1.x, p2.x), bottom_y, 0))
                    leader1_end = Vector((dim_x, bottom_y, 0))
                    leader2_start = Vector((min(p1.x, p2.x), top_y, 0))
                    leader2_end = Vector((dim_x, top_y, 0))
                
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
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        from mathutils import Vector
        
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        # Try to find nearest vertex to snap to
        best_dist = self.snap_radius
        best_point = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.type != 'MESH' or obj.get('IS_2D_ANNOTATION'):
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices_with_dist(
                    context, obj, coord, region, rv3d, best_dist)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    is_snapped = True
                continue
            
            matrix_world = obj.matrix_world
            
            if obj.data and hasattr(obj.data, 'vertices'):
                for vert in obj.data.vertices:
                    world_co = matrix_world @ vert.co
                    screen_co = location_3d_to_region_2d(region, rv3d, world_co)
                    if screen_co is None:
                        continue
                    
                    dist = (Vector(coord) - screen_co).length
                    
                    if dist < best_dist:
                        best_dist = dist
                        best_point = (world_co.x, world_co.y, 0)
                        is_snapped = True
        
        # If we found a snap point, use it
        if best_point:
            screen_pos = location_3d_to_region_2d(region, rv3d, Vector(best_point))
            return best_point, (screen_pos.x, screen_pos.y) if screen_pos else None, True
        
        # Otherwise fall back to plane intersection
        plane_point = self.get_plane_point(context, coord)
        if plane_point:
            return plane_point, coord, False
        
        return None, None, False
    
    def _check_collection_vertices_with_dist(self, context, instance_obj, coord, region, rv3d, best_dist):
        """Check vertices in a collection instance and return best point with distance."""
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        from mathutils import Vector
        
        if not instance_obj.instance_collection:
            return None, float('inf')
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        
        for obj in instance_obj.instance_collection.objects:
            if obj.type != 'MESH' or not obj.data or not hasattr(obj.data, 'vertices'):
                continue
            
            matrix_world = instance_matrix @ obj.matrix_world
            
            for vert in obj.data.vertices:
                world_co = matrix_world @ vert.co
                screen_co = location_3d_to_region_2d(region, rv3d, world_co)
                if screen_co is None:
                    continue
                
                dist = (Vector(coord) - screen_co).length
                
                if dist < best_dist:
                    best_dist = dist
                    best_point = (world_co.x, world_co.y, 0)
        
        return best_point, best_dist
    
    def get_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the layout plane (Z=0)."""
        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
        
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        if abs(direction.z) < 0.0001:
            return None
        
        t = -origin.z / direction.z
        point = origin + direction * t
        
        return (point.x, point.y, 0)
    
    def create_dimension(self, context):
        """Create a linear dimension annotation between the two clicked points."""
        from mathutils import Vector
        from .. import units
        import math
        
        p1 = Vector(self.first_point)
        p2 = Vector(self.second_point)
        
        delta = p2 - p1
        
        if delta.length < 0.001:
            self.report({'WARNING'}, "Points are too close together")
            return
        
        is_horizontal = abs(delta.x) >= abs(delta.y)
        
        if is_horizontal:
            dim_length = abs(delta.x)
            angle = 0
            left_x = min(p1.x, p2.x)
            start_point = Vector((left_x, min(p1.y, p2.y) - units.inch(4), 0))
        else:
            dim_length = abs(delta.y)
            angle = math.pi / 2
            bottom_y = min(p1.y, p2.y)
            start_point = Vector((min(p1.x, p2.x) - units.inch(4), bottom_y, 0))
        
        dim = hb_types.GeoNodeDimension()
        dim.create(f"Dimension_{len([o for o in context.scene.objects if 'IS_2D_ANNOTATION' in o])}")
        
        for scene in bpy.data.scenes:
            if dim.obj.name in scene.collection.objects:
                scene.collection.objects.unlink(dim.obj)
        
        context.scene.collection.objects.link(dim.obj)
        
        dim.obj.location = start_point
        dim.obj.rotation_euler = (0, 0, angle)
        
        if dim.obj.data.splines and len(dim.obj.data.splines[0].points) > 1:
            dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
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
