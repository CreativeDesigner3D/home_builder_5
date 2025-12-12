import bpy
import os
from .. import hb_layouts

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
        
        # Apply default scale
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
        
        # Apply default scale for floor plans
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
# REGISTRATION
# =============================================================================

classes = (
    home_builder_layouts_OT_create_elevation_view,
    home_builder_layouts_OT_create_plan_view,
    home_builder_layouts_OT_create_3d_view,
    home_builder_layouts_OT_create_all_elevations,
    home_builder_layouts_OT_update_elevation_view,
    home_builder_layouts_OT_delete_layout_view,
    home_builder_layouts_OT_go_to_layout_view,
    home_builder_layouts_OT_fit_view_to_content,
    home_builder_layouts_OT_render_layout,
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
