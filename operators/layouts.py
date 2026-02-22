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
from .. import hb_placement
from .. import units
from .. import hb_utils
from .. import hb_snap

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_addon_prefs():
    """Get addon preferences for layout defaults."""
    import os
    addon_name = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
    prefs = bpy.context.preferences.addons.get(addon_name)
    if prefs:
        return prefs.preferences
    return None


def apply_default_layout_settings(scene):
    """Apply default paper size and scale from addon preferences to a layout scene."""
    prefs = get_addon_prefs()
    if prefs:
        scene.hb_paper_size = prefs.default_paper_size
        scene.hb_layout_scale = prefs.default_layout_scale
        scene.hb_paper_landscape = prefs.default_paper_landscape
    else:
        # Fallback defaults if preferences not available
        scene.hb_paper_size = 'LEGAL'
        scene.hb_layout_scale = '1/4"=1\''
        scene.hb_paper_landscape = True


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
        
        # Apply default settings from addon preferences
        apply_default_layout_settings(scene)
        
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
        
        # Apply default settings from addon preferences
        apply_default_layout_settings(scene)
        
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
        
        # Apply default settings from addon preferences to all
        for view in views:
            apply_default_layout_settings(view.scene)
        
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
            # Apply default settings from addon preferences
            apply_default_layout_settings(scene)
            
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
                target_scene = main_scenes[0]
                context.window.scene = target_scene
                # Restore view for room scenes
                if hb_utils.is_room_scene(target_scene):
                    hb_utils.restore_view_state(target_scene)
            elif other_layouts:
                context.window.scene = other_layouts[0]
                hb_utils.set_camera_view()
        
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
            # Save current view state if in a room scene
            current_scene = context.scene
            if hb_utils.is_room_scene(current_scene):
                hb_utils.save_view_state(current_scene)
            
            target_scene = bpy.data.scenes[self.scene_name]
            context.window.scene = target_scene
            
            # Set appropriate view for the scene type
            if target_scene.get('IS_LAYOUT_VIEW'):
                # Layout views use camera view
                hb_utils.set_camera_view()
            elif target_scene.get('IS_DETAIL_VIEW') or target_scene.get('IS_CROWN_DETAIL'):
                # Detail views use top-down orthographic and frame all
                hb_utils.set_top_down_view()
                hb_utils.frame_all_objects()
            elif hb_utils.is_room_scene(target_scene):
                # Room scenes restore their saved view
                hb_utils.restore_view_state(target_scene)
        
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
        
        # Store original settings
        orig_resolution_x = scene.render.resolution_x
        orig_resolution_y = scene.render.resolution_y
        orig_film_transparent = scene.render.film_transparent
        orig_use_compositing = scene.render.use_compositing
        
        # Set render resolution
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        
        # Enable transparency for render
        scene.render.film_transparent = True
        
        # Enable compositing
        scene.render.use_compositing = True
        
        # Set up compositor for white background
        self._setup_compositor_white_background(context, scene)
        
        # Render to Blender's internal image
        bpy.ops.render.render()
        
        # Get the render result and save to a named image
        image_name = f"{scene.name}_Render"
        
        # Remove existing image with same name if it exists
        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])
        
        # Save render result to temp file, then load as new image
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{image_name}.png")
        
        # Save the render result to temp file
        orig_filepath = scene.render.filepath
        orig_format = scene.render.image_settings.file_format
        scene.render.filepath = temp_path
        scene.render.image_settings.file_format = 'PNG'
        
        # Get render result and save it
        render_result = bpy.data.images.get('Render Result')
        if render_result:
            render_result.save_render(temp_path, scene=scene)
            
            # Load the saved image
            new_image = bpy.data.images.load(temp_path)
            new_image.name = image_name
            new_image.pack()
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Open in Image Editor if available, otherwise open new window
            image_editor_found = False
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = new_image
                    image_editor_found = True
                    break
            
            if not image_editor_found:
                # Open a new window with Image Editor
                bpy.ops.wm.window_new()
                new_window = context.window_manager.windows[-1]
                new_screen = new_window.screen
                
                # Change the area type to Image Editor
                for area in new_screen.areas:
                    area.type = 'IMAGE_EDITOR'
                    area.spaces.active.image = new_image
                    break
        
        scene.render.filepath = orig_filepath
        scene.render.image_settings.file_format = orig_format
        
        # Restore original settings
        scene.render.resolution_x = orig_resolution_x
        scene.render.resolution_y = orig_resolution_y
        scene.render.film_transparent = orig_film_transparent
        
        self.report({'INFO'}, f"Rendered: {image_name}")
        return {'FINISHED'}
    
    def _setup_compositor_white_background(self, context, scene):
        """Set up compositor nodes to add white background to transparent render."""
        # Enable compositing
        scene.render.use_compositing = True
        
        # Set color management to Standard for accurate colors
        scene.view_settings.view_transform = 'Standard'
        
        # In Blender 5.0, compositor uses node group architecture
        tree = scene.compositing_node_group
        
        if tree is None:
            # Create a new compositor node tree
            tree = bpy.data.node_groups.new(
                name=f"{scene.name}_Compositor",
                type='CompositorNodeTree'
            )
            scene.compositing_node_group = tree
        
        nodes = tree.nodes
        links = tree.links
        
        # Clear existing nodes
        for node in list(nodes):
            nodes.remove(node)
        
        # Clear existing interface sockets
        tree.interface.clear()
        
        # Create output socket on the node group interface
        tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        
        # Create nodes
        render_layers = nodes.new('CompositorNodeRLayers')
        render_layers.location = (0, 300)
        
        # White color input
        white_color = nodes.new('CompositorNodeRGB')
        white_color.location = (0, 100)
        white_color.outputs[0].default_value = (1, 1, 1, 1)  # White
        
        alpha_over = nodes.new('CompositorNodeAlphaOver')
        alpha_over.location = (300, 300)
        
        # Group Output node (replaces CompositorNodeComposite in Blender 5.0)
        group_output = nodes.new('NodeGroupOutput')
        group_output.location = (600, 300)
        
        # Viewer node for preview
        viewer = nodes.new('CompositorNodeViewer')
        viewer.location = (600, 100)
        
        # Link nodes: White background under render
        # Alpha Over: inputs[0]=Background, inputs[1]=Foreground
        links.new(white_color.outputs[0], alpha_over.inputs[0])  # Background (white)
        links.new(render_layers.outputs['Image'], alpha_over.inputs[1])  # Foreground (render)
        links.new(alpha_over.outputs[0], group_output.inputs[0])  # To output
        links.new(alpha_over.outputs[0], viewer.inputs[0])  # To viewer


# =============================================================================
# EXPORT ALL LAYOUTS TO PDF OPERATOR
# =============================================================================

class home_builder_layouts_OT_export_all_to_pdf(bpy.types.Operator):
    bl_idname = "home_builder_layouts.export_all_to_pdf"
    bl_label = "Export All Layouts to PDF"
    bl_description = "Render all layout views and export to a single PDF file"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the PDF file",
        subtype='FILE_PATH',
        default="//layouts.pdf"
    )  # type: ignore
    
    dpi: bpy.props.EnumProperty(
        name="DPI",
        description="Resolution for rendering (higher = better quality, larger file)",
        items=[
            ('150', '150 DPI (Draft)', 'Quick preview quality'),
            ('200', '200 DPI (Good)', 'Good quality for screen viewing'),
            ('300', '300 DPI (Print)', 'Standard print quality'),
            ('600', '600 DPI (High)', 'High quality print'),
        ],
        default='300'
    )  # type: ignore
    
    filter_glob: bpy.props.StringProperty(
        default="*.pdf",
        options={'HIDDEN'}
    )  # type: ignore
    
    def invoke(self, context, event):
        # Set default filename based on blend file
        if bpy.data.filepath:
            blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
            self.filepath = os.path.join(os.path.dirname(bpy.data.filepath), f"{blend_name}_layouts.pdf")
        else:
            self.filepath = "//layouts.pdf"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            from PIL import Image
        except ImportError:
            self.report({'ERROR'}, "Pillow is required for PDF export. Please reinstall the Home Builder extension.")
            return {'CANCELLED'}
        
        import tempfile
        
        # Get all layout view scenes, sorted by sort_order
        layout_scenes = [s for s in bpy.data.scenes if s.get('IS_LAYOUT_VIEW')]
        layout_scenes.sort(key=lambda s: s.home_builder.sort_order)
        
        if not layout_scenes:
            self.report({'WARNING'}, "No layout views found")
            return {'CANCELLED'}
        
        # Store original scene
        original_scene = context.window.scene
        
        # Render each layout and collect images
        temp_images = []
        pil_images = []
        
        try:
            for scene in layout_scenes:
                # Switch to this scene
                context.window.scene = scene
                
                if not scene.camera:
                    continue
                
                # Get paper size and calculate render resolution
                paper_size = scene.hb_paper_size
                landscape = scene.hb_paper_landscape
                
                paper_w, paper_h = PAPER_SIZES_INCHES.get(paper_size, (8.5, 11.0))
                if landscape:
                    paper_w, paper_h = paper_h, paper_w
                
                dpi = int(self.dpi)
                width = int(paper_w * dpi)
                height = int(paper_h * dpi)
                
                # Calculate Freestyle thickness scale (base DPI is 150)
                thickness_scale = dpi / 150.0
                
                # Store original settings
                orig_resolution_x = scene.render.resolution_x
                orig_resolution_y = scene.render.resolution_y
                orig_film_transparent = scene.render.film_transparent
                orig_use_compositing = scene.render.use_compositing
                
                # Store and scale Freestyle line thicknesses
                orig_lineset_thicknesses = {}
                for view_layer in scene.view_layers:
                    if view_layer.use_freestyle:
                        for lineset in view_layer.freestyle_settings.linesets:
                            orig_lineset_thicknesses[lineset.name] = lineset.linestyle.thickness
                            lineset.linestyle.thickness = lineset.linestyle.thickness * thickness_scale
                
                # Set render resolution
                scene.render.resolution_x = width
                scene.render.resolution_y = height
                scene.render.resolution_percentage = 100
                
                # Enable transparency for render
                scene.render.film_transparent = True
                
                # Enable compositing
                scene.render.use_compositing = True
                
                # Set up compositor for white background
                self._setup_compositor_white_background(context, scene)
                
                # Render
                bpy.ops.render.render()
                
                # Save to temp file
                temp_path = os.path.join(tempfile.gettempdir(), f"{scene.name}_temp.png")
                temp_images.append(temp_path)
                
                render_result = bpy.data.images.get('Render Result')
                if render_result:
                    render_result.save_render(temp_path, scene=scene)
                    
                    # Load with PIL and convert to RGB (PDF doesn't support RGBA)
                    pil_img = Image.open(temp_path).convert('RGB')
                    pil_images.append(pil_img)
                
                # Restore settings
                scene.render.resolution_x = orig_resolution_x
                scene.render.resolution_y = orig_resolution_y
                scene.render.film_transparent = orig_film_transparent
                scene.render.use_compositing = orig_use_compositing
                
                # Restore Freestyle line thicknesses
                for view_layer in scene.view_layers:
                    if view_layer.use_freestyle:
                        for lineset in view_layer.freestyle_settings.linesets:
                            if lineset.name in orig_lineset_thicknesses:
                                lineset.linestyle.thickness = orig_lineset_thicknesses[lineset.name]
            
            # Save as PDF
            if pil_images:
                output_path = bpy.path.abspath(self.filepath)
                
                # First image saves, rest are appended
                pil_images[0].save(
                    output_path,
                    "PDF",
                    resolution=int(self.dpi),
                    save_all=True,
                    append_images=pil_images[1:] if len(pil_images) > 1 else []
                )
                
                self.report({'INFO'}, f"Exported {len(pil_images)} layouts to: {output_path}")
                
                # Open the PDF automatically
                import subprocess
                import platform
                try:
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', output_path])
                except Exception as e:
                    self.report({'WARNING'}, f"Could not open PDF: {e}")
            else:
                self.report({'WARNING'}, "No layouts were rendered")
                return {'CANCELLED'}
                
        finally:
            # Clean up temp files
            for temp_path in temp_images:
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            # Restore original scene
            context.window.scene = original_scene
        
        return {'FINISHED'}
    
    def _setup_compositor_white_background(self, context, scene):
        """Set up compositor nodes to add white background to transparent render."""
        # Enable compositing
        scene.render.use_compositing = True
        
        # Set color management to Standard for accurate colors
        scene.view_settings.view_transform = 'Standard'
        
        # In Blender 5.0, compositor uses node group architecture
        tree = scene.compositing_node_group
        
        if tree is None:
            # Create a new compositor node tree
            tree = bpy.data.node_groups.new(
                name=f"{scene.name}_Compositor",
                type='CompositorNodeTree'
            )
            scene.compositing_node_group = tree
        
        nodes = tree.nodes
        links = tree.links
        
        # Clear existing nodes
        for node in list(nodes):
            nodes.remove(node)
        
        # Clear existing interface sockets
        tree.interface.clear()
        
        # Create output socket on the node group interface
        tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        
        # Create nodes
        render_layers = nodes.new('CompositorNodeRLayers')
        render_layers.location = (0, 300)
        
        # White color input
        white_color = nodes.new('CompositorNodeRGB')
        white_color.location = (0, 100)
        white_color.outputs[0].default_value = (1, 1, 1, 1)  # White
        
        alpha_over = nodes.new('CompositorNodeAlphaOver')
        alpha_over.location = (300, 300)
        
        # Group Output node
        group_output = nodes.new('NodeGroupOutput')
        group_output.location = (600, 300)
        
        # Viewer node for preview
        viewer = nodes.new('CompositorNodeViewer')
        viewer.location = (600, 100)
        
        # Link nodes: White background under render
        links.new(white_color.outputs[0], alpha_over.inputs[0])  # Background (white)
        links.new(render_layers.outputs['Image'], alpha_over.inputs[1])  # Foreground (render)
        links.new(alpha_over.outputs[0], group_output.inputs[0])  # To output
        links.new(alpha_over.outputs[0], viewer.inputs[0])  # To viewer


# =============================================================================
# DIMENSION ANNOTATION OPERATOR
# =============================================================================

class home_builder_layouts_OT_add_dimension(bpy.types.Operator, hb_placement.DimensionOperatorMixin):
    bl_idname = "home_builder_layouts.add_dimension"
    bl_label = "Add Dimension"
    bl_description = "Click two points to measure, then click to place. Press O for ortho lock."
    bl_options = {'UNDO'}
    
    # Preview dimension
    preview_dim = None
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')
    
    def invoke(self, context, event):
        self.region = context.region
        self.region_data = context.region_data
        
        self.init_dimension_state()
        self.preview_dim = None
        
        self.add_dimension_draw_handler(context)
        
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('CROSSHAIR')
        self.update_dimension_header(context)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        result = self.handle_dimension_event(context, event)
        
        if result == 'FINISHED':
            return {'FINISHED'}
        elif result == 'CANCELLED':
            return {'CANCELLED'}
        elif result == 'PASS_THROUGH':
            return {'PASS_THROUGH'}
        elif result == 'RUNNING_MODAL':
            return {'RUNNING_MODAL'}
        
        return {'RUNNING_MODAL'}
    
    def get_snap_point(self, context, coord: tuple):
        """Get snapped point for layout views (snaps to mesh vertices)."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.SNAP_RADIUS
        best_point = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices_with_dist(
                    context, obj, coord, region, rv3d, depsgraph, best_dist, is_elevation)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    is_snapped = True
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                
                if is_elevation:
                    screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                else:
                    proj_pos = Vector((world_pos.x, world_pos.y, 0))
                    screen_pos = location_3d_to_region_2d(region, rv3d, proj_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        if is_elevation:
                            best_point = world_pos.copy()
                        else:
                            best_point = Vector((world_pos.x, world_pos.y, 0))
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_point:
            screen = location_3d_to_region_2d(region, rv3d, best_point)
            screen_pos = (screen.x, screen.y) if screen else coord
            return (best_point, screen_pos, True)
        
        plane_point = self.get_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _check_collection_vertices_with_dist(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist, is_elevation):
        """Check vertices in a collection instance for snapping."""
        collection = instance_obj.instance_collection
        if not collection:
            return (None, best_dist)
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            combined_matrix = instance_matrix @ obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = combined_matrix @ vert.co
                
                if is_elevation:
                    screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                else:
                    proj_pos = Vector((world_pos.x, world_pos.y, 0))
                    screen_pos = location_3d_to_region_2d(region, rv3d, proj_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        if is_elevation:
                            best_point = world_pos.copy()
                        else:
                            best_point = Vector((world_pos.x, world_pos.y, 0))
            
            eval_obj.to_mesh_clear()
        
        return (best_point, best_dist)
    
    def get_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the appropriate layout plane."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        if is_elevation:
            wall_rotation_z = 0
            source_wall_name = context.scene.get('SOURCE_WALL')
            if source_wall_name and source_wall_name in bpy.data.objects:
                wall_obj = bpy.data.objects[source_wall_name]
                wall_rotation_z = wall_obj.rotation_euler.z
            
            plane_normal = Vector((0, 1, 0))
            rot_matrix = Matrix.Rotation(wall_rotation_z, 3, 'Z')
            plane_normal = rot_matrix @ plane_normal
            
            denom = direction.dot(plane_normal)
            if abs(denom) > 0.0001:
                t = -origin.dot(plane_normal) / denom
                return origin + direction * t
            return origin
        else:
            if abs(direction.z) > 0.0001:
                t = -origin.z / direction.z
                point = origin + direction * t
                return Vector((point.x, point.y, 0))
            return Vector((origin.x, origin.y, 0))
    
    def create_preview_dimension(self, context):
        """Create the preview dimension object."""
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        self.preview_dim = hb_types.GeoNodeDimension()
        self.preview_dim.create("Dimension")
        self.preview_dim.obj['IS_2D_ANNOTATION'] = True
        
        # Set initial rotation based on view type
        if is_elevation:
            self.preview_dim.obj.rotation_euler = (math.pi / 2, 0, 0)  # Stand up for wall plane
        else:
            self.preview_dim.obj.rotation_euler = (0, 0, 0)  # Flat in XY for plan view
        
        self.preview_dim.obj.location = self.first_point
    
    def update_dimension_preview(self, context):
        """Update the preview dimension as mouse moves."""
        if not self.preview_dim:
            return
        
        is_elevation = context.scene.get('IS_ELEVATION_VIEW', False)
        
        if is_elevation:
            self._update_elevation_preview(context)
        else:
            self._update_plan_preview(context)
    
    def _update_plan_preview(self, context):
        """Update preview for plan view.
        
        Plan view looks down -Z axis, so dimensions lay flat in XY plane.
        - Horizontal (along X): rotation (0, 0, 0)
        - Vertical (along Y): rotation (0, 0, pi/2)
        """
        if self.dim_state == self.DIM_STATE_SECOND:
            p1 = self.first_point
            p2 = self.current_point
            
            delta_x = p2.x - p1.x
            delta_y = p2.y - p1.y
            
            if abs(delta_x) < 0.001 and abs(delta_y) < 0.001:
                return
            
            is_horizontal = abs(delta_x) >= abs(delta_y)
            
            if is_horizontal:
                dim_length = abs(delta_x)
                left_x = min(p1.x, p2.x)
                ref_y = p1.y if p1.x == left_x else p2.y
                self.preview_dim.obj.location = Vector((left_x, ref_y, 0))
                self.preview_dim.obj.rotation_euler = (0, 0, 0)  # Flat in XY, along X
            else:
                dim_length = abs(delta_y)
                bottom_y = min(p1.y, p2.y)
                ref_x = p1.x if p1.y == bottom_y else p2.x
                self.preview_dim.obj.location = Vector((ref_x, bottom_y, 0))
                self.preview_dim.obj.rotation_euler = (0, 0, math.pi / 2)  # Flat in XY, along Y
            
            self.preview_dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
        elif self.dim_state == self.DIM_STATE_OFFSET:
            p1 = self.first_point
            p2 = self.second_point
            offset_pos = self.current_point
            
            delta_x = p2.x - p1.x
            delta_y = p2.y - p1.y
            
            is_horizontal = abs(delta_x) >= abs(delta_y)
            
            if is_horizontal:
                left_x = min(p1.x, p2.x)
                ref_y = p1.y if p1.x == left_x else p2.y
                leader_length = offset_pos.y - ref_y
            else:
                bottom_y = min(p1.y, p2.y)
                ref_x = p1.x if p1.y == bottom_y else p2.x
                leader_length = -(offset_pos.x - ref_x)
            
            self.preview_dim.set_input("Leader Length", leader_length)
    
    def _update_elevation_preview(self, context):
        """Update preview for elevation view."""
        wall_rotation_z = 0
        source_wall_name = context.scene.get('SOURCE_WALL')
        if source_wall_name and source_wall_name in bpy.data.objects:
            wall_obj = bpy.data.objects[source_wall_name]
            wall_rotation_z = wall_obj.rotation_euler.z
        
        rot_matrix = Matrix.Rotation(-wall_rotation_z, 4, 'Z')
        
        if self.dim_state == self.DIM_STATE_SECOND:
            p1 = self.first_point
            p2 = self.current_point
            
            p1_local = rot_matrix @ p1
            p2_local = rot_matrix @ p2
            
            delta_x = p2_local.x - p1_local.x
            delta_z = p2_local.z - p1_local.z
            
            if abs(delta_x) < 0.001 and abs(delta_z) < 0.001:
                return
            
            is_horizontal = abs(delta_x) >= abs(delta_z)
            
            if is_horizontal:
                dim_length = abs(delta_x)
                left_x = min(p1_local.x, p2_local.x)
                ref_z = p1_local.z if p1_local.x == left_x else p2_local.z
                start_local = Vector((left_x, p1_local.y, ref_z))
                local_rotation = (math.pi / 2, 0, 0)
            else:
                dim_length = abs(delta_z)
                bottom_z = min(p1_local.z, p2_local.z)
                ref_x = p1_local.x if p1_local.z == bottom_z else p2_local.x
                start_local = Vector((ref_x, p1_local.y, bottom_z))
                local_rotation = (0, -math.pi / 2, math.pi / 2)
            
            rot_matrix_inv = Matrix.Rotation(wall_rotation_z, 4, 'Z')
            start_point = rot_matrix_inv @ start_local
            
            local_euler = Euler(local_rotation, 'XYZ')
            wall_euler = Euler((0, 0, wall_rotation_z), 'XYZ')
            combined_matrix = wall_euler.to_matrix().to_4x4() @ local_euler.to_matrix().to_4x4()
            final_euler = combined_matrix.to_euler('XYZ')
            
            self.preview_dim.obj.location = start_point
            self.preview_dim.obj.rotation_euler = final_euler
            self.preview_dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
        elif self.dim_state == self.DIM_STATE_OFFSET:
            p1 = self.first_point
            p2 = self.second_point
            offset_pos = self.current_point
            
            p1_local = rot_matrix @ p1
            p2_local = rot_matrix @ p2
            leader_local = rot_matrix @ offset_pos
            
            delta_x = p2_local.x - p1_local.x
            delta_z = p2_local.z - p1_local.z
            
            is_horizontal = abs(delta_x) >= abs(delta_z)
            
            if is_horizontal:
                left_x = min(p1_local.x, p2_local.x)
                ref_z = p1_local.z if p1_local.x == left_x else p2_local.z
                leader_length = leader_local.z - ref_z
            else:
                bottom_z = min(p1_local.z, p2_local.z)
                ref_x = p1_local.x if p1_local.z == bottom_z else p2_local.x
                leader_length = -(leader_local.x - ref_x)
            
            self.preview_dim.set_input("Leader Length", leader_length)
    
    def finalize_dimension(self, context):
        """Finalize the dimension."""
        if self.preview_dim:
            self.preview_dim.set_decimal()
    
    def cancel_dimension(self, context):
        """Delete the preview dimension on cancel."""
        if self.preview_dim and self.preview_dim.obj:
            bpy.data.objects.remove(self.preview_dim.obj, do_unlink=True)
        self.preview_dim = None



class home_builder_layouts_OT_add_dimension_3d(bpy.types.Operator, hb_placement.DimensionOperatorMixin):
    bl_idname = "home_builder_layouts.add_dimension_3d"
    bl_label = "Add Dimension (3D View)"
    bl_description = "Click two points to add a dimension in 3D view. Press O for ortho lock."
    bl_options = {'UNDO'}
    
    # Preview dimension
    preview_dim = None
    
    # View plane info
    view_plane = 'XY'
    plane_normal = None
    
    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'
    
    def invoke(self, context, event):
        self.region = context.region
        self.region_data = context.region_data
        
        self.init_dimension_state()
        self.preview_dim = None
        
        self._detect_view_plane(context)
        self.add_dimension_draw_handler(context)
        
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('CROSSHAIR')
        self.update_dimension_header(context)
        
        return {'RUNNING_MODAL'}
    
    def get_dimension_header_text(self) -> str:
        """Override to include view plane info."""
        base_text = super().get_dimension_header_text()
        return f"{base_text} | Plane: {self.view_plane}"
    
    def _detect_view_plane(self, context):
        """Detect which plane the user is most aligned with."""
        rv3d = context.region_data
        if not rv3d:
            self.view_plane = 'XY'
            self.plane_normal = Vector((0, 0, 1))
            return
        
        view_matrix = rv3d.view_matrix.inverted()
        view_direction = Vector((0, 0, -1))
        view_direction.rotate(view_matrix.to_euler())
        view_direction.normalize()
        
        abs_x = abs(view_direction.x)
        abs_y = abs(view_direction.y)
        abs_z = abs(view_direction.z)
        
        if abs_z >= abs_x and abs_z >= abs_y:
            self.view_plane = 'XY'
            self.plane_normal = Vector((0, 0, 1))
        elif abs_y >= abs_x and abs_y >= abs_z:
            self.view_plane = 'XZ'
            self.plane_normal = Vector((0, 1, 0))
        else:
            self.view_plane = 'YZ'
            self.plane_normal = Vector((1, 0, 0))
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        result = self.handle_dimension_event(context, event)
        
        if result == 'FINISHED':
            return {'FINISHED'}
        elif result == 'CANCELLED':
            return {'CANCELLED'}
        elif result == 'PASS_THROUGH':
            return {'PASS_THROUGH'}
        elif result == 'RUNNING_MODAL':
            return {'RUNNING_MODAL'}
        
        return {'RUNNING_MODAL'}
    
    def get_snap_point(self, context, coord: tuple):
        """Snap to mesh vertices in 3D views.
        
        In perspective view, we snap to where vertices APPEAR on screen.
        For the first point, we keep the actual vertex position (establishes the plane).
        For subsequent points, we project to a plane through the first point.
        """
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        best_dist = self.SNAP_RADIUS
        best_world_pos = None
        best_screen_pos = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                
                # Compare screen position of ACTUAL vertex
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_world_pos = world_pos.copy()
                        best_screen_pos = (screen_pos.x, screen_pos.y)
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_world_pos:
            if self.first_point is None:
                # FIRST point: keep actual vertex position - this establishes the working plane
                result_point = best_world_pos.copy()
            else:
                # Subsequent points: project to plane through first_point
                result_point = self._project_to_plane(best_world_pos)
            
            screen = location_3d_to_region_2d(region, rv3d, result_point)
            screen_pos = (screen.x, screen.y) if screen else best_screen_pos
            return (result_point, screen_pos, True)
        
        plane_point = self.get_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _project_to_plane(self, point: Vector) -> Vector:
        """Project a 3D point onto the detected view plane.
        
        If first_point is set, projects to a plane passing through first_point.
        Otherwise projects to plane at origin.
        """
        # Use first_point as plane reference if available
        if self.first_point:
            ref = self.first_point
        else:
            ref = Vector((0, 0, 0))
        
        if self.view_plane == 'XY':
            return Vector((point.x, point.y, ref.z))
        elif self.view_plane == 'XZ':
            return Vector((point.x, ref.y, point.z))
        else:  # YZ
            return Vector((ref.x, point.y, point.z))
    
    def get_plane_point(self, context, coord):
        """Get point on the detected view plane.
        
        If first_point is set, intersects with plane passing through first_point.
        Otherwise intersects with plane at origin.
        """
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        ray_direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        # Plane passes through first_point if set, otherwise origin
        if self.first_point:
            plane_co = self.first_point
        else:
            plane_co = Vector((0, 0, 0))
        
        # Ray-plane intersection: plane defined by point and normal
        # t = (plane_co - ray_origin).dot(normal) / ray_direction.dot(normal)
        denom = ray_direction.dot(self.plane_normal)
        if abs(denom) > 0.0001:
            t = (plane_co - ray_origin).dot(self.plane_normal) / denom
            return ray_origin + ray_direction * t
        
        return self._project_to_plane(ray_origin)
    
    def apply_ortho_constraint(self, point: Vector) -> Vector:
        """Override to handle 3D ortho based on view plane."""
        if not self.ortho_mode or not self.first_point:
            return point
        
        if self.view_plane == 'XY':
            dh = point.x - self.first_point.x
            dv = point.y - self.first_point.y
            z = self.first_point.z
            
            if self.ortho_direction == 'AUTO':
                self.ortho_direction = 'HORIZONTAL' if abs(dh) >= abs(dv) else 'VERTICAL'
            
            if self.ortho_direction == 'HORIZONTAL':
                return Vector((point.x, self.first_point.y, z))
            else:
                return Vector((self.first_point.x, point.y, z))
        
        elif self.view_plane == 'XZ':
            dh = point.x - self.first_point.x
            dv = point.z - self.first_point.z
            y = self.first_point.y
            
            if self.ortho_direction == 'AUTO':
                self.ortho_direction = 'HORIZONTAL' if abs(dh) >= abs(dv) else 'VERTICAL'
            
            if self.ortho_direction == 'HORIZONTAL':
                return Vector((point.x, y, self.first_point.z))
            else:
                return Vector((self.first_point.x, y, point.z))
        
        else:  # YZ
            dh = point.y - self.first_point.y
            dv = point.z - self.first_point.z
            x = self.first_point.x
            
            if self.ortho_direction == 'AUTO':
                self.ortho_direction = 'HORIZONTAL' if abs(dh) >= abs(dv) else 'VERTICAL'
            
            if self.ortho_direction == 'HORIZONTAL':
                return Vector((x, point.y, self.first_point.z))
            else:
                return Vector((x, self.first_point.y, point.z))
    
    def create_preview_dimension(self, context):
        """Create the preview dimension object."""
        self.preview_dim = hb_types.GeoNodeDimension()
        self.preview_dim.create("Dimension")
        
        # Ensure it's in the current scene
        for scene in bpy.data.scenes:
            if self.preview_dim.obj.name in scene.collection.objects:
                scene.collection.objects.unlink(self.preview_dim.obj)
        context.scene.collection.objects.link(self.preview_dim.obj)
        
        self.preview_dim.obj.location = self.first_point
    
    def update_dimension_preview(self, context):
        """Update the preview dimension as mouse moves."""
        if not self.preview_dim:
            return
        
        if self.dim_state == self.DIM_STATE_SECOND:
            p1 = self.first_point
            p2 = self.current_point
            
            result = self._calculate_dimension_params(p1, p2, p1)  # Use p1 as placeholder for offset
            if result:
                start_point, rotation, dim_length, _ = result
                self.preview_dim.obj.location = start_point
                self.preview_dim.obj.rotation_euler = rotation
                self.preview_dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
        
        elif self.dim_state == self.DIM_STATE_OFFSET:
            p1 = self.first_point
            p2 = self.second_point
            offset_pos = self.current_point
            
            result = self._calculate_dimension_params(p1, p2, offset_pos)
            if result:
                start_point, rotation, dim_length, leader_length = result
                self.preview_dim.obj.location = start_point
                self.preview_dim.obj.rotation_euler = rotation
                self.preview_dim.obj.data.splines[0].points[1].co = (dim_length, 0, 0, 1)
                self.preview_dim.set_input("Leader Length", leader_length)
    
    def _calculate_dimension_params(self, p1, p2, leader_pos):
        """Calculate dimension parameters based on view plane."""
        if self.view_plane == 'XY':
            delta_h = p2.x - p1.x
            delta_v = p2.y - p1.y
            is_horizontal = abs(delta_h) >= abs(delta_v)
            
            if abs(delta_h) < 0.001 and abs(delta_v) < 0.001:
                return None
            
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
            
            if abs(delta_h) < 0.001 and abs(delta_v) < 0.001:
                return None
            
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
        
        else:  # YZ
            delta_h = p2.y - p1.y
            delta_v = p2.z - p1.z
            is_horizontal = abs(delta_h) >= abs(delta_v)
            
            if abs(delta_h) < 0.001 and abs(delta_v) < 0.001:
                return None
            
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
        
        return (start_point, rotation, dim_length, leader_length)
    
    def finalize_dimension(self, context):
        """Finalize the dimension."""
        if self.preview_dim:
            self.preview_dim.set_decimal()
    
    def cancel_dimension(self, context):
        """Delete the preview dimension on cancel."""
        if self.preview_dim and self.preview_dim.obj:
            bpy.data.objects.remove(self.preview_dim.obj, do_unlink=True)
        self.preview_dim = None





# =============================================================================
# LINE DRAWING OPERATOR FOR LAYOUTS
# =============================================================================

class home_builder_layouts_OT_draw_line(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_layouts.draw_line"
    bl_label = "Draw Line"
    bl_description = "Draw a 2D polyline on the layout. Click to place points, type for exact length. Press L to lock angle."
    bl_options = {'UNDO'}
    
    # Snap radius in pixels
    SNAP_RADIUS = 20
    
    # Polyline state
    polyline = None
    current_point: Vector = None  # The last confirmed point (world space on view plane)
    point_count: int = 0  # Number of confirmed points
    
    # Ortho mode (snap to 0, 45, 90 degree angles)
    ortho_mode: bool = True
    ortho_angle: float = 0.0
    
    # Angle lock state
    angle_locked: bool = False
    locked_angle: float = 0.0
    
    # Tracking state
    tracking_point: Vector = None
    is_tracking: bool = False
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # View plane info (calculated once at start)
    view_plane_normal: Vector = None
    view_plane_point: Vector = None
    view_right: Vector = None  # Camera's right direction (for angle calculations)
    view_up: Vector = None     # Camera's up direction
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        return (context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')) and context.scene.camera
    
    def _setup_view_plane(self, context):
        """Calculate the view plane based on camera orientation.
        
        The view plane is perpendicular to the camera's view direction,
        positioned slightly in front of the camera.
        """
        camera = context.scene.camera
        if not camera:
            return False
        
        cam_matrix = camera.matrix_world
        
        # Camera's local axes in world space
        # Camera looks down its local -Z axis
        cam_forward = -(cam_matrix.to_3x3() @ Vector((0, 0, 1)))
        cam_forward.normalize()
        
        cam_right = cam_matrix.to_3x3() @ Vector((1, 0, 0))
        cam_right.normalize()
        
        cam_up = cam_matrix.to_3x3() @ Vector((0, 1, 0))
        cam_up.normalize()
        
        # View plane normal is opposite of camera forward (pointing toward camera)
        self.view_plane_normal = -cam_forward
        
        # View plane point - slightly in front of camera
        # Use a small offset along camera forward direction
        self.view_plane_point = camera.location + cam_forward * 0.5
        
        # Store camera axes for 2D angle calculations on the view plane
        self.view_right = cam_right
        self.view_up = cam_up
        
        return True
    
    def _get_view_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the view plane."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        # Get ray from mouse position
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        ray_direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        # Ray-plane intersection
        # Plane equation: dot(point - plane_point, plane_normal) = 0
        # Ray equation: point = ray_origin + t * ray_direction
        # Solving for t: t = dot(plane_point - ray_origin, plane_normal) / dot(ray_direction, plane_normal)
        
        denom = ray_direction.dot(self.view_plane_normal)
        if abs(denom) < 0.0001:
            # Ray is parallel to plane
            return None
        
        t = (self.view_plane_point - ray_origin).dot(self.view_plane_normal) / denom
        
        return ray_origin + ray_direction * t
    
    def _world_to_view_2d(self, point: Vector) -> tuple:
        """Convert a world point on the view plane to 2D coordinates in view space.
        
        Returns (x, y) where x is along view_right and y is along view_up.
        """
        # Vector from plane origin to point
        offset = point - self.view_plane_point
        
        # Project onto view axes
        x = offset.dot(self.view_right)
        y = offset.dot(self.view_up)
        
        return (x, y)
    
    def _view_2d_to_world(self, x: float, y: float) -> Vector:
        """Convert 2D view coordinates back to world point on the view plane."""
        return self.view_plane_point + self.view_right * x + self.view_up * y
    
    def get_snap_point(self, context, coord: tuple):
        """Get snapped point for layout views (snaps to mesh vertices).
        
        Returns point in world space on the view plane.
        """
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.SNAP_RADIUS
        best_point = None
        best_screen_pos = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            # Skip our own polyline
            if self.polyline and obj == self.polyline.obj:
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices(
                    context, obj, coord, region, rv3d, depsgraph, best_dist)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    best_screen_pos = result[2]
                    is_snapped = True
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        # Project the snapped point onto our view plane
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_point:
            return (best_point, best_screen_pos, True)
        
        # No snap - return point on view plane from mouse
        plane_point = self._get_view_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _project_to_view_plane(self, world_point: Vector) -> Vector:
        """Project a world point onto the view plane."""
        # Vector from plane point to world point
        offset = world_point - self.view_plane_point
        
        # Remove the component along the plane normal
        dist_to_plane = offset.dot(self.view_plane_normal)
        projected = world_point - self.view_plane_normal * dist_to_plane
        
        return projected
    
    def _check_collection_vertices(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist):
        """Check vertices in a collection instance for snapping."""
        collection = instance_obj.instance_collection
        if not collection:
            return (None, best_dist, None)
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        best_screen_pos = None
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            combined_matrix = instance_matrix @ obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = combined_matrix @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
            
            eval_obj.to_mesh_clear()
        
        return (best_point, best_dist, best_screen_pos)
    
    def get_snapped_position(self, context) -> Vector:
        """Get position with snapping applied (world space on view plane)."""
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        point, screen_pos, snapped = self.get_snap_point(context, coord)
        
        self.is_snapped = snapped
        self.snap_screen_pos = screen_pos
        
        return point
    
    def create_polyline(self, context):
        """Create a new polyline object on the view plane."""
        from .. import hb_details
        
        # Get annotation settings from scene
        hb_scene = context.scene.home_builder
        line_thickness = hb_scene.annotation_line_thickness
        line_color = tuple(hb_scene.annotation_line_color) + (1.0,)
        
        # Create curve
        curve = bpy.data.curves.new("Line", 'CURVE')
        curve.dimensions = '3D'
        
        # Create initial spline with one point at origin (will be updated)
        spline = curve.splines.new('POLY')
        spline.points[0].co = (0, 0, 0, 1)
        
        # Create object
        obj = bpy.data.objects.new("Line", curve)
        obj['IS_DETAIL_POLYLINE'] = True
        obj['IS_2D_ANNOTATION'] = True
        obj.color = line_color
        
        context.scene.collection.objects.link(obj)
        
        # Create material
        mat = bpy.data.materials.new("Line_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = line_color
        curve.materials.append(mat)
        
        curve.bevel_depth = line_thickness
        
        # Create a simple wrapper object to hold the curve
        class PolylineWrapper:
            def __init__(self, obj):
                self.obj = obj
            
            def set_point(self, index, point):
                """Set point in world coordinates."""
                if self.obj and self.obj.type == 'CURVE':
                    spline = self.obj.data.splines[0]
                    if index < len(spline.points):
                        spline.points[index].co = (point.x, point.y, point.z, 1)
            
            def add_point(self, point):
                """Add point in world coordinates."""
                if self.obj and self.obj.type == 'CURVE':
                    spline = self.obj.data.splines[0]
                    spline.points.add(1)
                    idx = len(spline.points) - 1
                    spline.points[idx].co = (point.x, point.y, point.z, 1)
        
        self.polyline = PolylineWrapper(obj)
        
        # Add to Freestyle Ignore collection
        ignore_collection = bpy.data.collections.get(f"{context.scene.name}_Freestyle_Ignore")
        if ignore_collection and obj.name not in ignore_collection.objects:
            ignore_collection.objects.link(obj)
        
        self.register_placement_object(obj)
        self.point_count = 0
        self.current_point = None
    
    def _set_preview_point(self, point: Vector):
        """Set the preview (last) point of the polyline (world coords on view plane)."""
        if self.polyline and self.polyline.obj:
            spline = self.polyline.obj.data.splines[0]
            idx = len(spline.points) - 1
            self.polyline.set_point(idx, point)
    
    def _get_preview_point(self) -> Vector:
        """Get the current preview point position in world space."""
        if self.polyline and self.polyline.obj:
            spline = self.polyline.obj.data.splines[0]
            idx = len(spline.points) - 1
            co = spline.points[idx].co
            return Vector((co[0], co[1], co[2]))
        return Vector((0, 0, 0))
    
    def _get_segment_length(self) -> float:
        """Get the length of the current segment (in view plane)."""
        if self.current_point:
            preview = self._get_preview_point()
            # Get 2D coordinates on view plane
            p1_2d = self._world_to_view_2d(self.current_point)
            p2_2d = self._world_to_view_2d(preview)
            dx = p2_2d[0] - p1_2d[0]
            dy = p2_2d[1] - p1_2d[1]
            return math.sqrt(dx * dx + dy * dy)
        return 0.0
    
    def _confirm_point(self):
        """Confirm the current preview point and add a new preview point."""
        if self.polyline and self.polyline.obj:
            self.current_point = self._get_preview_point().copy()
            self.point_count += 1
            
            # Unlock angle after placing point
            self.angle_locked = False
            
            # Add a new point for the next preview
            self.polyline.add_point(self.current_point)
    
    def _update_from_mouse(self, context):
        """Update preview point based on mouse position."""
        if self.point_count == 0:
            return
        
        # Reset tracking state
        self.is_tracking = False
        self.tracking_point = None
        
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        
        # Get current point in 2D view space
        curr_2d = self._world_to_view_2d(self.current_point)
        
        # When angle is locked, project along locked angle
        if self.angle_locked and self.current_point:
            point, screen_pos, snapped = self.get_snap_point(context, coord)
            
            if snapped and point:
                # Project along locked angle to align with snap point
                projected = self._project_to_locked_angle(point)
                if projected:
                    self.is_snapped = True
                    self.is_tracking = True
                    self.tracking_point = point.copy()
                    self._set_preview_point(projected)
                    # Update screen pos
                    screen = location_3d_to_region_2d(context.region, context.region_data, projected)
                    self.snap_screen_pos = (screen.x, screen.y) if screen else coord
                    return
            
            # No snap - extend along locked angle
            self.is_snapped = False
            end_point = self._get_view_plane_point(context, coord)
            if end_point:
                end_point = self._constrain_to_locked_angle(end_point)
                self._set_preview_point(end_point)
                screen = location_3d_to_region_2d(context.region, context.region_data, end_point)
                self.snap_screen_pos = (screen.x, screen.y) if screen else coord
            return
        
        # Normal behavior (not locked)
        point, screen_pos, snapped = self.get_snap_point(context, coord)
        
        if snapped and point:
            self.is_snapped = True
            self.snap_screen_pos = screen_pos
            if self.current_point:
                # Calculate angle in view plane
                end_2d = self._world_to_view_2d(point)
                dx = end_2d[0] - curr_2d[0]
                dy = end_2d[1] - curr_2d[1]
                self.ortho_angle = math.atan2(dy, dx)
            self._set_preview_point(point)
            return
        
        self.is_snapped = False
        end_point = self._get_view_plane_point(context, coord)
        
        if self.current_point and end_point:
            # Work in 2D view coordinates
            end_2d = self._world_to_view_2d(end_point)
            dx = end_2d[0] - curr_2d[0]
            dy = end_2d[1] - curr_2d[1]
            
            if abs(dx) < 0.0001 and abs(dy) < 0.0001:
                return
            
            length = math.sqrt(dx * dx + dy * dy)
            
            if self.ortho_mode:
                angle = math.atan2(dy, dx)
                snap_angle = round(math.degrees(angle) / 45) * 45
                self.ortho_angle = math.radians(snap_angle)
                
                # Calculate new endpoint in 2D, then convert back to 3D
                new_x = curr_2d[0] + math.cos(self.ortho_angle) * length
                new_y = curr_2d[1] + math.sin(self.ortho_angle) * length
                end_point = self._view_2d_to_world(new_x, new_y)
            else:
                self.ortho_angle = math.atan2(dy, dx)
            
            # Update screen position for feedback
            screen = location_3d_to_region_2d(context.region, context.region_data, end_point)
            self.snap_screen_pos = (screen.x, screen.y) if screen else coord
        
        if end_point:
            self._set_preview_point(end_point)
    
    def _project_to_locked_angle(self, snap_point: Vector) -> Vector:
        """Project along locked angle to align with snap point."""
        if not self.current_point:
            return None
        
        # Work in 2D view coordinates
        curr_2d = self._world_to_view_2d(self.current_point)
        snap_2d = self._world_to_view_2d(snap_point)
        
        cos_a = math.cos(self.locked_angle)
        sin_a = math.sin(self.locked_angle)
        
        x0, y0 = curr_2d
        sx, sy = snap_2d
        
        # Calculate t for alignment
        t_x = None
        if abs(cos_a) > 0.001:
            t_x = (sx - x0) / cos_a
        
        t_y = None
        if abs(sin_a) > 0.001:
            t_y = (sy - y0) / sin_a
        
        # Use the axis that's more perpendicular to the locked angle
        t = None
        if abs(cos_a) > abs(sin_a):
            t = t_x
        else:
            t = t_y
        
        if t is not None:
            new_x = x0 + t * cos_a
            new_y = y0 + t * sin_a
            return self._view_2d_to_world(new_x, new_y)
        
        return None
    
    def _constrain_to_locked_angle(self, end_point: Vector) -> Vector:
        """Constrain point to locked angle direction."""
        if not self.current_point:
            return end_point
        
        # Work in 2D view coordinates
        curr_2d = self._world_to_view_2d(self.current_point)
        end_2d = self._world_to_view_2d(end_point)
        
        cos_a = math.cos(self.locked_angle)
        sin_a = math.sin(self.locked_angle)
        
        dx = end_2d[0] - curr_2d[0]
        dy = end_2d[1] - curr_2d[1]
        length = dx * cos_a + dy * sin_a
        
        new_x = curr_2d[0] + cos_a * length
        new_y = curr_2d[1] + sin_a * length
        
        return self._view_2d_to_world(new_x, new_y)
    
    def _finalize(self):
        """Finalize the polyline by removing the trailing preview point."""
        if self.polyline and self.polyline.obj and self.point_count > 0:
            spline = self.polyline.obj.data.splines[0]
            if len(spline.points) > self.point_count:
                points_data = [(p.co[0], p.co[1], p.co[2]) for p in spline.points[:self.point_count]]
                
                self.polyline.obj.data.splines.clear()
                new_spline = self.polyline.obj.data.splines.new('POLY')
                new_spline.points.add(len(points_data) - 1)
                for i, (x, y, z) in enumerate(points_data):
                    new_spline.points[i].co = (x, y, z, 1)
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.LENGTH
    
    def on_typed_value_changed(self):
        if self.typed_value and self.polyline and self.point_count > 0:
            parsed = self.parse_typed_distance()
            if parsed is not None:
                self._update_preview_from_length(bpy.context, parsed)
        self.update_header(bpy.context)
    
    def apply_typed_value(self):
        parsed = self.parse_typed_distance()
        if parsed is not None and self.polyline and self.point_count > 0:
            self._update_preview_from_length(bpy.context, parsed)
            self._confirm_point()
        self.stop_typing()
    
    def _update_preview_from_length(self, context, length: float):
        """Update preview point based on typed length and current angle."""
        if self.current_point:
            curr_2d = self._world_to_view_2d(self.current_point)
            new_x = curr_2d[0] + math.cos(self.ortho_angle) * length
            new_y = curr_2d[1] + math.sin(self.ortho_angle) * length
            end_point = self._view_2d_to_world(new_x, new_y)
            self._set_preview_point(end_point)
    
    def update_header(self, context):
        if self.is_tracking and self.angle_locked:
            snap_text = " [LOCK+SNAP]"
        elif self.angle_locked:
            snap_text = " [LOCK]"
        elif self.is_snapped:
            snap_text = " [SNAP]"
        else:
            snap_text = ""
        
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Segment Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.point_count > 0:
            length = self._get_segment_length()
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            
            if self.angle_locked:
                angle_deg = round(math.degrees(self.locked_angle))
            else:
                angle_deg = round(math.degrees(self.ortho_angle))
            
            mode = "Ortho" if self.ortho_mode else "Free"
            
            close_text = " | C: close" if self.point_count >= 2 else ""
            lock_hint = "L: unlock" if self.angle_locked else "L: lock"
            text = f"Length: {length_str} | {angle_deg}° | {mode}{snap_text} | {lock_hint}{close_text} | Right-click: finish"
        else:
            text = f"Click to place first point{snap_text} | Right-click/Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        self.init_placement(context)
        
        # Reset state
        self.polyline = None
        self.current_point = None
        self.point_count = 0
        self.ortho_mode = True
        self.ortho_angle = 0.0
        self.angle_locked = False
        self.locked_angle = 0.0
        self.tracking_point = None
        self.is_tracking = False
        self.is_snapped = False
        self.snap_screen_pos = None
        
        # Setup view plane based on camera
        if not self._setup_view_plane(context):
            self.report({'ERROR'}, "No camera found in scene")
            return {'CANCELLED'}
        
        # Add draw handler for snap indicator
        from ..operators.details import draw_snap_indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create polyline
        self.create_polyline(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.polyline and self.polyline.obj:
            self.polyline.obj.hide_set(True)
        self.update_snap(context, event)
        if self.polyline and self.polyline.obj:
            self.polyline.obj.hide_set(False)
        
        # Update preview point position
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.point_count == 0:
                pos = self.get_snapped_position(context)
                if pos:
                    self.polyline.set_point(0, pos)
            else:
                self._update_from_mouse(context)
        
        self.update_header(context)
        
        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.point_count == 0:
                start = self.get_snapped_position(context)
                if start:
                    self.polyline.set_point(0, start)
                    self.current_point = start.copy()
                    self.point_count = 1
                    self.polyline.add_point(start)
            else:
                self._confirm_point()
            return {'RUNNING_MODAL'}
        
        # Right click - finish
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            if self.point_count > 1:
                self._finalize()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            else:
                self.cancel_placement(context)
                hb_placement.clear_header_text(context)
                return {'CANCELLED'}
        
        # C key - close the shape
        if event.type == 'C' and event.value == 'PRESS':
            if self.point_count >= 2:
                self._remove_draw_handler()
                self._finalize()
                
                if self.polyline and self.polyline.obj:
                    self.polyline.obj.data.splines[0].use_cyclic_u = True
                
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Alt - toggle ortho mode
        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            self.ortho_mode = not self.ortho_mode
            self.angle_locked = False
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # L - lock/unlock angle
        if event.type == 'L' and event.value == 'PRESS':
            if self.point_count > 0:
                if self.angle_locked:
                    self.angle_locked = False
                else:
                    self.locked_angle = self.ortho_angle
                    self.angle_locked = True
                self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class home_builder_layouts_OT_draw_rectangle(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_layouts.draw_rectangle"
    bl_label = "Draw Rectangle"
    bl_description = "Draw a rectangle by clicking two corners or typing dimensions. Snaps to existing vertices."
    bl_options = {'UNDO'}
    
    # Snap radius in pixels
    SNAP_RADIUS = 20
    
    # Rectangle state
    polyline = None
    first_corner: Vector = None  # First corner in world space on view plane
    has_first_corner: bool = False
    
    # Typed dimensions
    typed_width: str = ""
    typed_height: str = ""
    typing_width: bool = False  # True = typing width, False = typing height
    is_typing: bool = False
    
    # Current dimensions (for display and rectangle update)
    current_width: float = 0.0
    current_height: float = 0.0
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # View plane info (calculated once at start)
    view_plane_normal: Vector = None
    view_plane_point: Vector = None
    view_right: Vector = None  # Camera's right direction (width axis)
    view_up: Vector = None     # Camera's up direction (height axis)
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        return (context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')) and context.scene.camera
    
    def _setup_view_plane(self, context):
        """Calculate the view plane based on camera orientation."""
        camera = context.scene.camera
        if not camera:
            return False
        
        cam_matrix = camera.matrix_world
        
        # Camera's local axes in world space
        cam_forward = -(cam_matrix.to_3x3() @ Vector((0, 0, 1)))
        cam_forward.normalize()
        
        cam_right = cam_matrix.to_3x3() @ Vector((1, 0, 0))
        cam_right.normalize()
        
        cam_up = cam_matrix.to_3x3() @ Vector((0, 1, 0))
        cam_up.normalize()
        
        # View plane normal is opposite of camera forward
        self.view_plane_normal = -cam_forward
        
        # View plane point - slightly in front of camera
        self.view_plane_point = camera.location + cam_forward * 0.5
        
        # Store camera axes for 2D calculations
        self.view_right = cam_right
        self.view_up = cam_up
        
        return True
    
    def _get_view_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the view plane."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        ray_direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        denom = ray_direction.dot(self.view_plane_normal)
        if abs(denom) < 0.0001:
            return None
        
        t = (self.view_plane_point - ray_origin).dot(self.view_plane_normal) / denom
        
        return ray_origin + ray_direction * t
    
    def _world_to_view_2d(self, point: Vector) -> tuple:
        """Convert a world point on the view plane to 2D coordinates in view space."""
        offset = point - self.view_plane_point
        x = offset.dot(self.view_right)
        y = offset.dot(self.view_up)
        return (x, y)
    
    def _view_2d_to_world(self, x: float, y: float) -> Vector:
        """Convert 2D view coordinates back to world point on the view plane."""
        return self.view_plane_point + self.view_right * x + self.view_up * y
    
    def _project_to_view_plane(self, world_point: Vector) -> Vector:
        """Project a world point onto the view plane."""
        offset = world_point - self.view_plane_point
        dist_to_plane = offset.dot(self.view_plane_normal)
        projected = world_point - self.view_plane_normal * dist_to_plane
        return projected
    
    def get_snap_point(self, context, coord: tuple):
        """Get snapped point for layout views (snaps to mesh vertices)."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.SNAP_RADIUS
        best_point = None
        best_screen_pos = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            # Skip our own polyline
            if self.polyline and obj == self.polyline.obj:
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices(
                    context, obj, coord, region, rv3d, depsgraph, best_dist)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    best_screen_pos = result[2]
                    is_snapped = True
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_point:
            return (best_point, best_screen_pos, True)
        
        plane_point = self._get_view_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _check_collection_vertices(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist):
        """Check vertices in a collection instance for snapping."""
        collection = instance_obj.instance_collection
        if not collection:
            return (None, best_dist, None)
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        best_screen_pos = None
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            combined_matrix = instance_matrix @ obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = combined_matrix @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
            
            eval_obj.to_mesh_clear()
        
        return (best_point, best_dist, best_screen_pos)
    
    def get_snapped_position(self, context) -> Vector:
        """Get position with snapping applied (world space on view plane)."""
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        point, screen_pos, snapped = self.get_snap_point(context, coord)
        
        self.is_snapped = snapped
        self.snap_screen_pos = screen_pos
        
        return point
    
    def create_rectangle(self, context):
        """Create a new rectangle polyline object on the view plane."""
        # Get annotation settings from scene
        hb_scene = context.scene.home_builder
        line_thickness = hb_scene.annotation_line_thickness
        line_color = tuple(hb_scene.annotation_line_color) + (1.0,)
        
        # Create curve
        curve = bpy.data.curves.new("Rectangle", 'CURVE')
        curve.dimensions = '3D'
        
        # Create initial spline with 4 points
        spline = curve.splines.new('POLY')
        spline.points.add(3)  # Add 3 more points (4 total)
        for i in range(4):
            spline.points[i].co = (0, 0, 0, 1)
        
        # Close the rectangle
        spline.use_cyclic_u = True
        
        # Create object
        obj = bpy.data.objects.new("Rectangle", curve)
        obj['IS_DETAIL_POLYLINE'] = True
        obj['IS_2D_ANNOTATION'] = True
        obj.color = line_color
        
        context.scene.collection.objects.link(obj)
        
        # Create material
        mat = bpy.data.materials.new("Rectangle_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = line_color
        curve.materials.append(mat)
        
        curve.bevel_depth = line_thickness
        
        # Create a simple wrapper
        class RectWrapper:
            def __init__(self, obj):
                self.obj = obj
            
            def set_point(self, index, point):
                if self.obj and self.obj.type == 'CURVE':
                    spline = self.obj.data.splines[0]
                    if index < len(spline.points):
                        spline.points[index].co = (point.x, point.y, point.z, 1)
        
        self.polyline = RectWrapper(obj)
        
        # Add to Freestyle Ignore collection
        ignore_collection = bpy.data.collections.get(f"{context.scene.name}_Freestyle_Ignore")
        if ignore_collection and obj.name not in ignore_collection.objects:
            ignore_collection.objects.link(obj)
        
        self.register_placement_object(obj)
    
    def update_rectangle_from_corners(self, second_corner: Vector):
        """Update rectangle points based on two corners (world coords on view plane)."""
        if not self.first_corner or not self.polyline:
            return
        
        # Get 2D coordinates in view space
        c1_2d = self._world_to_view_2d(self.first_corner)
        c2_2d = self._world_to_view_2d(second_corner)
        
        # Calculate width and height in view space
        self.current_width = abs(c2_2d[0] - c1_2d[0])
        self.current_height = abs(c2_2d[1] - c1_2d[1])
        
        # Get min/max coordinates
        min_x = min(c1_2d[0], c2_2d[0])
        max_x = max(c1_2d[0], c2_2d[0])
        min_y = min(c1_2d[1], c2_2d[1])
        max_y = max(c1_2d[1], c2_2d[1])
        
        # Set the 4 corners in world space (counter-clockwise from bottom-left)
        self.polyline.set_point(0, self._view_2d_to_world(min_x, min_y))  # Bottom-left
        self.polyline.set_point(1, self._view_2d_to_world(max_x, min_y))  # Bottom-right
        self.polyline.set_point(2, self._view_2d_to_world(max_x, max_y))  # Top-right
        self.polyline.set_point(3, self._view_2d_to_world(min_x, max_y))  # Top-left
    
    def update_rectangle_from_dimensions(self, width: float, height: float):
        """Update rectangle based on typed dimensions."""
        if not self.first_corner or not self.polyline:
            return
        
        self.current_width = width
        self.current_height = height
        
        # Get first corner in 2D view space
        c1_2d = self._world_to_view_2d(self.first_corner)
        
        # Calculate second corner (extend in positive direction)
        c2_x = c1_2d[0] + width
        c2_y = c1_2d[1] + height
        
        # Set the 4 corners in world space
        self.polyline.set_point(0, self._view_2d_to_world(c1_2d[0], c1_2d[1]))  # Bottom-left
        self.polyline.set_point(1, self._view_2d_to_world(c2_x, c1_2d[1]))       # Bottom-right
        self.polyline.set_point(2, self._view_2d_to_world(c2_x, c2_y))           # Top-right
        self.polyline.set_point(3, self._view_2d_to_world(c1_2d[0], c2_y))       # Top-left
    
    def parse_dimension(self, value_str: str) -> float:
        """Parse a typed dimension string to meters. Returns 0.0 if parsing fails."""
        if not value_str:
            return 0.0
        result = self.parse_typed_distance(value_str)
        return result if result is not None else 0.0
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        
        if not self.has_first_corner:
            text = f"Click first corner{snap_text} | Right-click/Esc to cancel"
        elif self.is_typing:
            if self.typing_width:
                text = f"Width: {self.typed_width}_ | Tab for height | Enter to confirm | Esc to cancel"
            else:
                width_str = units.unit_to_string(context.scene.unit_settings, self.parse_dimension(self.typed_width) or self.current_width)
                text = f"Width: {width_str} | Height: {self.typed_height}_ | Enter to confirm | Esc to cancel"
        else:
            width_str = units.unit_to_string(context.scene.unit_settings, self.current_width)
            height_str = units.unit_to_string(context.scene.unit_settings, self.current_height)
            text = f"Width: {width_str} | Height: {height_str}{snap_text} | Type for exact size | Click to place"
        
        hb_placement.draw_header_text(context, text)
    
    def handle_typing(self, event) -> bool:
        """Handle keyboard input for typing dimensions. Returns True if event was consumed."""
        # Number keys to start or continue typing
        if event.type in hb_placement.NUMBER_KEYS and event.value == 'PRESS':
            if not self.is_typing:
                # Start typing width
                self.is_typing = True
                self.typing_width = True
                self.typed_width = hb_placement.NUMBER_KEYS[event.type]
                self.typed_height = ""
            elif self.typing_width:
                self.typed_width += hb_placement.NUMBER_KEYS[event.type]
            else:
                self.typed_height += hb_placement.NUMBER_KEYS[event.type]
            
            # Update rectangle preview
            self._update_from_typed()
            return True
        
        if not self.is_typing:
            return False
        
        # Backspace
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.typing_width:
                if self.typed_width:
                    self.typed_width = self.typed_width[:-1]
                else:
                    self.is_typing = False
            else:
                if self.typed_height:
                    self.typed_height = self.typed_height[:-1]
                else:
                    self.typing_width = True
            self._update_from_typed()
            return True
        
        # Tab - switch between width and height
        if event.type == 'TAB' and event.value == 'PRESS':
            self.typing_width = not self.typing_width
            return True
        
        # Enter - confirm
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            width = self.parse_dimension(self.typed_width)
            height = self.parse_dimension(self.typed_height)
            
            if width > 0 and height > 0:
                self.update_rectangle_from_dimensions(width, height)
                return False  # Let modal handle the finish
            elif width > 0 and not self.typed_height:
                self.typing_width = False
                return True
            return True
        
        # Escape - cancel typing
        if event.type == 'ESC' and event.value == 'PRESS':
            self.is_typing = False
            self.typed_width = ""
            self.typed_height = ""
            return True
        
        return False
    
    def _update_from_typed(self):
        """Update rectangle from currently typed values."""
        width = self.parse_dimension(self.typed_width) if self.typed_width else self.current_width
        height = self.parse_dimension(self.typed_height) if self.typed_height else self.current_height
        
        width = width or 0.0
        height = height or 0.0
        
        if width > 0 or height > 0:
            self.update_rectangle_from_dimensions(
                width if width > 0 else 0.1,
                height if height > 0 else 0.1
            )
    
    def execute(self, context):
        self.init_placement(context)
        
        # Reset state
        self.polyline = None
        self.first_corner = None
        self.has_first_corner = False
        self.is_snapped = False
        self.snap_screen_pos = None
        self.typed_width = ""
        self.typed_height = ""
        self.typing_width = False
        self.is_typing = False
        self.current_width = 0.0
        self.current_height = 0.0
        
        # Setup view plane based on camera
        if not self._setup_view_plane(context):
            self.report({'ERROR'}, "No camera found in scene")
            return {'CANCELLED'}
        
        # Add draw handler for snap indicator
        from ..operators.details import draw_snap_indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create rectangle
        self.create_rectangle(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing input first (only after first corner is placed)
        if self.has_first_corner and self.handle_typing(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Check if we should finish after Enter with valid dimensions
        if self.has_first_corner and event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            width = self.parse_dimension(self.typed_width) if self.typed_width else 0
            height = self.parse_dimension(self.typed_height) if self.typed_height else 0
            
            if width > 0 and height > 0:
                self.update_rectangle_from_dimensions(width, height)
                self._remove_draw_handler()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
        
        # Update snap (only if not typing)
        if not self.is_typing:
            if self.polyline and self.polyline.obj:
                self.polyline.obj.hide_set(True)
            self.update_snap(context, event)
            if self.polyline and self.polyline.obj:
                self.polyline.obj.hide_set(False)
            
            # Get current position with snapping
            current_pos = self.get_snapped_position(context)
            
            # Update rectangle preview
            if not self.has_first_corner:
                # Before first click, show rectangle at cursor (zero size)
                if current_pos:
                    self.polyline.set_point(0, current_pos)
                    self.polyline.set_point(1, current_pos)
                    self.polyline.set_point(2, current_pos)
                    self.polyline.set_point(3, current_pos)
            else:
                # After first click, update rectangle from first corner to cursor
                if current_pos:
                    self.update_rectangle_from_corners(current_pos)
        
        self.update_header(context)
        
        # Left click - place corner
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_first_corner:
                current_pos = self.get_snapped_position(context)
                if current_pos:
                    self.first_corner = current_pos.copy()
                    self.has_first_corner = True
                    self.update_rectangle_from_corners(current_pos)
            elif not self.is_typing:
                # Confirm rectangle
                self._remove_draw_handler()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        if event.type == 'ESC' and event.value == 'PRESS' and not self.is_typing:
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class home_builder_layouts_OT_draw_circle(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_layouts.draw_circle"
    bl_label = "Draw Circle"
    bl_description = "Draw a circle by clicking center then setting radius. Type for exact size."
    bl_options = {'UNDO'}
    
    # Snap radius in pixels
    SNAP_RADIUS = 20
    SEGMENTS = 32  # Number of segments for smooth circle
    
    # Circle state
    circle_obj = None
    center: Vector = None  # Center in world space on view plane
    has_center: bool = False
    
    # Typed radius
    typed_radius: str = ""
    is_typing: bool = False
    
    # Current radius for display
    current_radius: float = 0.0
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # View plane info
    view_plane_normal: Vector = None
    view_plane_point: Vector = None
    view_right: Vector = None
    view_up: Vector = None
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        return (context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')) and context.scene.camera
    
    def _setup_view_plane(self, context):
        """Calculate the view plane based on camera orientation."""
        camera = context.scene.camera
        if not camera:
            return False
        
        cam_matrix = camera.matrix_world
        
        cam_forward = -(cam_matrix.to_3x3() @ Vector((0, 0, 1)))
        cam_forward.normalize()
        
        cam_right = cam_matrix.to_3x3() @ Vector((1, 0, 0))
        cam_right.normalize()
        
        cam_up = cam_matrix.to_3x3() @ Vector((0, 1, 0))
        cam_up.normalize()
        
        self.view_plane_normal = -cam_forward
        self.view_plane_point = camera.location + cam_forward * 0.5
        self.view_right = cam_right
        self.view_up = cam_up
        
        return True
    
    def _get_view_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the view plane."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        ray_direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        denom = ray_direction.dot(self.view_plane_normal)
        if abs(denom) < 0.0001:
            return None
        
        t = (self.view_plane_point - ray_origin).dot(self.view_plane_normal) / denom
        return ray_origin + ray_direction * t
    
    def _world_to_view_2d(self, point: Vector) -> tuple:
        """Convert a world point on the view plane to 2D coordinates in view space."""
        offset = point - self.view_plane_point
        x = offset.dot(self.view_right)
        y = offset.dot(self.view_up)
        return (x, y)
    
    def _view_2d_to_world(self, x: float, y: float) -> Vector:
        """Convert 2D view coordinates back to world point on the view plane."""
        return self.view_plane_point + self.view_right * x + self.view_up * y
    
    def _project_to_view_plane(self, world_point: Vector) -> Vector:
        """Project a world point onto the view plane."""
        offset = world_point - self.view_plane_point
        dist_to_plane = offset.dot(self.view_plane_normal)
        return world_point - self.view_plane_normal * dist_to_plane
    
    def get_snap_point(self, context, coord: tuple):
        """Get snapped point for layout views."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.SNAP_RADIUS
        best_point = None
        best_screen_pos = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            if self.circle_obj and obj == self.circle_obj:
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices(
                    context, obj, coord, region, rv3d, depsgraph, best_dist)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    best_screen_pos = result[2]
                    is_snapped = True
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_point:
            return (best_point, best_screen_pos, True)
        
        plane_point = self._get_view_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _check_collection_vertices(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist):
        """Check vertices in a collection instance for snapping."""
        collection = instance_obj.instance_collection
        if not collection:
            return (None, best_dist, None)
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        best_screen_pos = None
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            combined_matrix = instance_matrix @ obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = combined_matrix @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
            
            eval_obj.to_mesh_clear()
        
        return (best_point, best_dist, best_screen_pos)
    
    def get_snapped_position(self, context) -> Vector:
        """Get position with snapping applied."""
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        point, screen_pos, snapped = self.get_snap_point(context, coord)
        
        self.is_snapped = snapped
        self.snap_screen_pos = screen_pos
        
        return point
    
    def create_circle(self, context):
        """Create a new circle object on the view plane."""
        # Get annotation settings
        hb_scene = context.scene.home_builder
        line_thickness = hb_scene.annotation_line_thickness
        line_color = tuple(hb_scene.annotation_line_color) + (1.0,)
        
        # Create curve
        curve = bpy.data.curves.new("Circle", 'CURVE')
        curve.dimensions = '3D'
        
        # Create circular spline
        spline = curve.splines.new('POLY')
        spline.points.add(self.SEGMENTS - 1)
        
        # Initialize with small radius (will be updated)
        radius = 0.001
        for i in range(self.SEGMENTS):
            angle = 2 * math.pi * i / self.SEGMENTS
            # Local coordinates in view_right/view_up space
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            spline.points[i].co = (x, y, 0, 1)
        
        spline.use_cyclic_u = True
        
        # Create object
        obj = bpy.data.objects.new("Circle", curve)
        obj['IS_DETAIL_CIRCLE'] = True
        obj['IS_2D_ANNOTATION'] = True
        obj.color = line_color
        
        context.scene.collection.objects.link(obj)
        
        # Create material
        mat = bpy.data.materials.new("Circle_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = line_color
        curve.materials.append(mat)
        
        curve.bevel_depth = line_thickness
        
        self.circle_obj = obj
        
        # Add to Freestyle Ignore collection
        ignore_collection = bpy.data.collections.get(f"{context.scene.name}_Freestyle_Ignore")
        if ignore_collection and obj.name not in ignore_collection.objects:
            ignore_collection.objects.link(obj)
        
        self.register_placement_object(obj)
    
    def _update_circle_points(self, center: Vector, radius: float):
        """Update circle points on the view plane."""
        if not self.circle_obj or self.circle_obj.type != 'CURVE':
            return
        
        spline = self.circle_obj.data.splines[0]
        
        for i in range(len(spline.points)):
            angle = 2 * math.pi * i / len(spline.points)
            # Calculate point on circle in view plane space
            local_x = radius * math.cos(angle)
            local_y = radius * math.sin(angle)
            # Convert to world position
            world_pos = center + self.view_right * local_x + self.view_up * local_y
            spline.points[i].co = (world_pos.x, world_pos.y, world_pos.z, 1)
    
    def parse_radius(self, value_str: str) -> float:
        """Parse a typed radius string to meters."""
        if not value_str:
            return 0.0
        result = self.parse_typed_distance(value_str)
        return result if result is not None else 0.0
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        
        if not self.has_center:
            text = f"Click to place center{snap_text} | Right-click/Esc to cancel"
        elif self.is_typing:
            text = f"Radius: {self.typed_radius}_ | Enter to confirm | Esc to cancel typing"
        else:
            radius_str = units.unit_to_string(context.scene.unit_settings, self.current_radius)
            diameter_str = units.unit_to_string(context.scene.unit_settings, self.current_radius * 2)
            text = f"Radius: {radius_str} | Diameter: {diameter_str}{snap_text} | Type for exact | Click to place"
        
        hb_placement.draw_header_text(context, text)
    
    def handle_typing(self, event) -> bool:
        """Handle keyboard input for typing radius."""
        if event.type in hb_placement.NUMBER_KEYS and event.value == 'PRESS':
            if not self.is_typing:
                self.is_typing = True
                self.typed_radius = hb_placement.NUMBER_KEYS[event.type]
            else:
                self.typed_radius += hb_placement.NUMBER_KEYS[event.type]
            
            radius = self.parse_radius(self.typed_radius)
            if radius > 0 and self.center:
                self._update_circle_points(self.center, radius)
                self.current_radius = radius
            return True
        
        if not self.is_typing:
            return False
        
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.typed_radius:
                self.typed_radius = self.typed_radius[:-1]
                radius = self.parse_radius(self.typed_radius)
                if radius > 0 and self.center:
                    self._update_circle_points(self.center, radius)
                    self.current_radius = radius
            else:
                self.is_typing = False
            return True
        
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            radius = self.parse_radius(self.typed_radius)
            if radius > 0 and self.center:
                self._update_circle_points(self.center, radius)
                self.current_radius = radius
                return False  # Let modal finish
            return True
        
        if event.type == 'ESC' and event.value == 'PRESS':
            self.is_typing = False
            self.typed_radius = ""
            return True
        
        return False
    
    def execute(self, context):
        self.init_placement(context)
        
        # Reset state
        self.circle_obj = None
        self.center = None
        self.has_center = False
        self.is_snapped = False
        self.snap_screen_pos = None
        self.typed_radius = ""
        self.is_typing = False
        self.current_radius = 0.0
        
        # Setup view plane
        if not self._setup_view_plane(context):
            self.report({'ERROR'}, "No camera found in scene")
            return {'CANCELLED'}
        
        # Add draw handler
        from ..operators.details import draw_snap_indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create circle
        self.create_circle(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing
        if self.has_center and self.handle_typing(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Check for Enter to finish
        if self.has_center and event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            radius = self.parse_radius(self.typed_radius) if self.typed_radius else self.current_radius
            if radius > 0:
                self._update_circle_points(self.center, radius)
                self._remove_draw_handler()
                if self.circle_obj in self.placement_objects:
                    self.placement_objects.remove(self.circle_obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
        
        # Update snap
        if not self.is_typing:
            if self.circle_obj:
                self.circle_obj.hide_set(True)
            self.update_snap(context, event)
            if self.circle_obj:
                self.circle_obj.hide_set(False)
            
            current_pos = self.get_snapped_position(context)
            
            if not self.has_center:
                # Move circle to cursor (tiny radius)
                if current_pos:
                    self._update_circle_points(current_pos, 0.001)
            else:
                # Update radius from cursor distance
                if current_pos and self.center:
                    center_2d = self._world_to_view_2d(self.center)
                    current_2d = self._world_to_view_2d(current_pos)
                    dx = current_2d[0] - center_2d[0]
                    dy = current_2d[1] - center_2d[1]
                    radius = math.sqrt(dx * dx + dy * dy)
                    
                    if radius > 0.001:
                        self._update_circle_points(self.center, radius)
                        self.current_radius = radius
        
        self.update_header(context)
        
        # Left click
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_center:
                current_pos = self.get_snapped_position(context)
                if current_pos:
                    self.center = current_pos.copy()
                    self.has_center = True
            elif not self.is_typing:
                if self.current_radius > 0.001:
                    self._remove_draw_handler()
                    if self.circle_obj in self.placement_objects:
                        self.placement_objects.remove(self.circle_obj)
                    hb_placement.clear_header_text(context)
                    return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        if event.type == 'ESC' and event.value == 'PRESS' and not self.is_typing:
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class home_builder_layouts_OT_add_text(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_layouts.add_text"
    bl_label = "Add Text"
    bl_description = "Add text annotation. Click to place, then Tab to edit."
    bl_options = {'UNDO'}
    
    # Snap radius in pixels
    SNAP_RADIUS = 20
    
    # Text state
    text_obj = None
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # View plane info
    view_plane_normal: Vector = None
    view_plane_point: Vector = None
    view_right: Vector = None
    view_up: Vector = None
    
    # Draw handler
    _handle = None
    
    @classmethod
    def poll(cls, context):
        return (context.scene.get('IS_LAYOUT_VIEW') or context.scene.get('IS_MULTI_VIEW')) and context.scene.camera
    
    def _setup_view_plane(self, context):
        """Calculate the view plane based on camera orientation."""
        camera = context.scene.camera
        if not camera:
            return False
        
        cam_matrix = camera.matrix_world
        
        cam_forward = -(cam_matrix.to_3x3() @ Vector((0, 0, 1)))
        cam_forward.normalize()
        
        cam_right = cam_matrix.to_3x3() @ Vector((1, 0, 0))
        cam_right.normalize()
        
        cam_up = cam_matrix.to_3x3() @ Vector((0, 1, 0))
        cam_up.normalize()
        
        self.view_plane_normal = -cam_forward
        self.view_plane_point = camera.location + cam_forward * 0.5
        self.view_right = cam_right
        self.view_up = cam_up
        
        return True
    
    def _get_view_plane_point(self, context, coord):
        """Convert 2D mouse coordinates to 3D point on the view plane."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        ray_direction = region_2d_to_vector_3d(region, rv3d, coord)
        
        denom = ray_direction.dot(self.view_plane_normal)
        if abs(denom) < 0.0001:
            return None
        
        t = (self.view_plane_point - ray_origin).dot(self.view_plane_normal) / denom
        return ray_origin + ray_direction * t
    
    def _project_to_view_plane(self, world_point: Vector) -> Vector:
        """Project a world point onto the view plane."""
        offset = world_point - self.view_plane_point
        dist_to_plane = offset.dot(self.view_plane_normal)
        return world_point - self.view_plane_normal * dist_to_plane
    
    def _get_text_rotation(self, context):
        """Get the rotation needed to face the camera."""
        # Simply use the camera's rotation - text should be parallel to view plane
        camera = context.scene.camera
        if camera:
            return camera.rotation_euler.copy()
        return Euler((0, 0, 0))
    
    def get_snap_point(self, context, coord: tuple):
        """Get snapped point for layout views."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None, None, False
        
        depsgraph = context.evaluated_depsgraph_get()
        
        best_dist = self.SNAP_RADIUS
        best_point = None
        best_screen_pos = None
        is_snapped = False
        
        for obj in context.scene.objects:
            if obj.get('IS_2D_ANNOTATION'):
                continue
            
            if self.text_obj and obj == self.text_obj:
                continue
            
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                result = self._check_collection_vertices(
                    context, obj, coord, region, rv3d, depsgraph, best_dist)
                if result[0] is not None and result[1] < best_dist:
                    best_point = result[0]
                    best_dist = result[1]
                    best_screen_pos = result[2]
                    is_snapped = True
                continue
            
            if obj.type != 'MESH':
                continue
            
            matrix_world = obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = matrix_world @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
                        is_snapped = True
            
            eval_obj.to_mesh_clear()
        
        if best_point:
            return (best_point, best_screen_pos, True)
        
        plane_point = self._get_view_plane_point(context, coord)
        return (plane_point, coord, False)
    
    def _check_collection_vertices(self, context, instance_obj, coord, region, rv3d, depsgraph, best_dist):
        """Check vertices in a collection instance for snapping."""
        collection = instance_obj.instance_collection
        if not collection:
            return (None, best_dist, None)
        
        instance_matrix = instance_obj.matrix_world
        best_point = None
        best_screen_pos = None
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            combined_matrix = instance_matrix @ obj.matrix_world
            
            try:
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
            except:
                continue
            
            for vert in mesh.vertices:
                world_pos = combined_matrix @ vert.co
                screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                
                if screen_pos:
                    dist = (Vector(coord) - screen_pos).length
                    if dist < best_dist:
                        best_dist = dist
                        best_point = self._project_to_view_plane(world_pos)
                        best_screen_pos = (screen_pos.x, screen_pos.y)
            
            eval_obj.to_mesh_clear()
        
        return (best_point, best_dist, best_screen_pos)
    
    def get_snapped_position(self, context) -> Vector:
        """Get position with snapping applied."""
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        point, screen_pos, snapped = self.get_snap_point(context, coord)
        
        self.is_snapped = snapped
        self.snap_screen_pos = screen_pos
        
        return point
    
    def create_text(self, context):
        """Create a new text object on the view plane."""
        hb_scene = context.scene.home_builder
        
        # Create font/text data
        text_data = bpy.data.curves.new("Text", 'FONT')
        text_data.body = "TEXT"
        text_data.size = hb_scene.annotation_text_size
        text_data.align_x = 'LEFT'
        text_data.align_y = 'BOTTOM'
        
        # Create object
        obj = bpy.data.objects.new("Text", text_data)
        obj['IS_DETAIL_TEXT'] = True
        obj['IS_2D_ANNOTATION'] = True
        
        # Apply text color
        color = tuple(hb_scene.annotation_text_color) + (1.0,)
        obj.color = color
        
        context.scene.collection.objects.link(obj)
        
        # Create material
        mat = bpy.data.materials.new("Text_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
        text_data.materials.append(mat)
        
        # Set extrude for visibility
        text_data.extrude = 0.001
        
        # Apply font - prefer Calibri if available, then annotation_font setting
        calibri_font = None
        for font in bpy.data.fonts:
            if 'calibri' in font.name.lower() and 'regular' in font.name.lower():
                calibri_font = font
                break
            elif 'calibri' in font.name.lower() and calibri_font is None:
                calibri_font = font
        
        if calibri_font:
            obj.data.font = calibri_font
        elif hb_scene.annotation_font:
            obj.data.font = hb_scene.annotation_font
        
        # Set rotation to face camera
        obj.rotation_euler = self._get_text_rotation(context)
        
        self.text_obj = obj
        
        # Add to Freestyle Ignore collection
        ignore_collection = bpy.data.collections.get(f"{context.scene.name}_Freestyle_Ignore")
        if ignore_collection and obj.name not in ignore_collection.objects:
            ignore_collection.objects.link(obj)
        
        self.register_placement_object(obj)
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        text = f"Click to place text{snap_text} | Tab to edit after placing | Right-click/Esc to cancel"
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        self.init_placement(context)
        
        # Reset state
        self.text_obj = None
        self.is_snapped = False
        self.snap_screen_pos = None
        
        # Setup view plane
        if not self._setup_view_plane(context):
            self.report({'ERROR'}, "No camera found in scene")
            return {'CANCELLED'}
        
        # Add draw handler
        from ..operators.details import draw_snap_indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create text object
        self.create_text(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.text_obj:
            self.text_obj.hide_set(True)
        self.update_snap(context, event)
        if self.text_obj:
            self.text_obj.hide_set(False)
        
        # Get current position with snapping
        current_pos = self.get_snapped_position(context)
        
        # Update text position
        if current_pos and self.text_obj:
            self.text_obj.location = current_pos
        
        self.update_header(context)
        
        # Left click - place text
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            current_pos = self.get_snapped_position(context)
            if current_pos and self.text_obj:
                self.text_obj.location = current_pos
                
                # Select the text object so user can Tab to edit
                bpy.ops.object.select_all(action='DESELECT')
                self.text_obj.select_set(True)
                context.view_layer.objects.active = self.text_obj
                
                self._remove_draw_handler()
                if self.text_obj in self.placement_objects:
                    self.placement_objects.remove(self.text_obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class home_builder_layouts_OT_add_detail_to_layout(bpy.types.Operator):
    bl_idname = "home_builder_layouts.add_detail_to_layout"
    bl_label = "Add Detail to Layout"
    bl_description = "Add a 2D detail to the current layout view"
    bl_options = {'UNDO'}
    
    detail_scene_name: bpy.props.StringProperty(name="Detail Scene")  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW')
    
    def execute(self, context):
        if self.detail_scene_name not in bpy.data.scenes:
            self.report({'ERROR'}, f"Detail scene '{self.detail_scene_name}' not found")
            return {'CANCELLED'}
        
        detail_scene = bpy.data.scenes[self.detail_scene_name]
        layout_scene = context.scene
        camera = layout_scene.camera
        
        if not camera:
            self.report({'ERROR'}, "Layout view has no camera")
            return {'CANCELLED'}
        
        # Get or create a collection for the detail scene's objects
        collection_name = f"{detail_scene.name}_Collection"
        
        if collection_name in bpy.data.collections:
            detail_collection = bpy.data.collections[collection_name]
            # Ensure all objects are black
            for obj in detail_collection.objects:
                obj.color = (0, 0, 0, 1)
        else:
            # Create a new collection and link all detail objects to it
            detail_collection = bpy.data.collections.new(collection_name)
            detail_collection['IS_DETAIL_COLLECTION'] = True
            detail_collection['SOURCE_DETAIL'] = detail_scene.name
            
            # Link objects from the detail scene to this collection
            for obj in detail_scene.objects:
                # Skip cameras and lights
                if obj.type in {'CAMERA', 'LIGHT'}:
                    continue
                
                # Set object color to black for layout rendering
                obj.color = (0, 0, 0, 1)
                
                # Link object to collection (object can be in multiple collections)
                if obj.name not in detail_collection.objects:
                    detail_collection.objects.link(obj)
        
        # Create collection instance in the layout scene
        instance = bpy.data.objects.new(f"Detail_{detail_scene.name}", None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = detail_collection
        instance.empty_display_size = 0.01
        instance.color = (0, 0, 0, 1)  # Black for layout rendering
        instance['IS_DETAIL_INSTANCE'] = True
        instance['SOURCE_DETAIL'] = detail_scene.name
        
        # Link instance to layout scene
        layout_scene.collection.objects.link(instance)
        
        # Parent to camera
        instance.parent = camera
        
        # Position at center of view
        instance.location = (0, 0, -0.1)
        
        # Add to Freestyle Ignore collection
        ignore_collection = bpy.data.collections.get(f"{layout_scene.name}_Freestyle_Ignore")
        if ignore_collection and instance.name not in ignore_collection.objects:
            ignore_collection.objects.link(instance)
        
        # Select the instance for easy repositioning
        bpy.ops.object.select_all(action='DESELECT')
        instance.select_set(True)
        context.view_layer.objects.active = instance
        
        self.report({'INFO'}, f"Added detail '{detail_scene.name}' to layout. Move to reposition.")
        return {'FINISHED'}


# =============================================================================
# REGISTRATION
# =============================================================================

class home_builder_layouts_OT_move_layout_view(bpy.types.Operator):
    """Move layout view up or down in the list"""
    bl_idname = "home_builder_layouts.move_layout_view"
    bl_label = "Move Layout View"
    bl_description = "Move layout view up or down in the list"
    bl_options = {'UNDO'}
    
    move_up: bpy.props.BoolProperty(name="Move Up") # type: ignore

    def ensure_sort_orders_initialized(self, layout_views):
        """Make sure all scenes have unique sort_order values."""
        orders = [s.home_builder.sort_order for s in layout_views]
        if len(set(orders)) <= 1:
            sorted_by_name = sorted(layout_views, key=lambda s: s.name)
            for i, scene in enumerate(sorted_by_name):
                scene.home_builder.sort_order = i

    def execute(self, context):
        layout_views = [s for s in bpy.data.scenes if s.get('IS_LAYOUT_VIEW')]
        
        if len(layout_views) < 2:
            return {'CANCELLED'}
        
        self.ensure_sort_orders_initialized(layout_views)
        layout_views = sorted(layout_views, key=lambda s: s.home_builder.sort_order)
        
        scene = context.scene
        
        if scene not in layout_views:
            return {'CANCELLED'}
        
        idx = layout_views.index(scene)
        
        if idx == 0 and self.move_up:
            return {'CANCELLED'}
        if idx == len(layout_views) - 1 and not self.move_up:
            return {'CANCELLED'}
        
        if self.move_up:
            neighbor = layout_views[idx - 1]
        else:
            neighbor = layout_views[idx + 1]
        
        scene.home_builder.sort_order, neighbor.home_builder.sort_order = \
            neighbor.home_builder.sort_order, scene.home_builder.sort_order
        
        return {'FINISHED'}


classes = (
    home_builder_layouts_OT_create_elevation_view,
    home_builder_layouts_OT_draw_rectangle,
    home_builder_layouts_OT_draw_circle,
    home_builder_layouts_OT_add_text,
    home_builder_layouts_OT_create_plan_view,
    home_builder_layouts_OT_create_3d_view,
    home_builder_layouts_OT_create_all_elevations,
    home_builder_layouts_OT_create_multi_view,
    home_builder_layouts_OT_update_elevation_view,
    home_builder_layouts_OT_delete_layout_view,
    home_builder_layouts_OT_go_to_layout_view,
    home_builder_layouts_OT_fit_view_to_content,
    home_builder_layouts_OT_render_layout,
    home_builder_layouts_OT_export_all_to_pdf,
    home_builder_layouts_OT_add_dimension,
    home_builder_layouts_OT_draw_line,
    home_builder_layouts_OT_add_dimension_3d,
    home_builder_layouts_OT_add_detail_to_layout,
    home_builder_layouts_OT_move_layout_view,
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
    
    if hasattr(bpy.types.Scene, 'hb_layout_scale'):
        del bpy.types.Scene.hb_layout_scale
    if hasattr(bpy.types.Scene, 'hb_paper_size'):
        del bpy.types.Scene.hb_paper_size
    if hasattr(bpy.types.Scene, 'hb_paper_landscape'):
        del bpy.types.Scene.hb_paper_landscape
