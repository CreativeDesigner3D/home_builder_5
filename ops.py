import bpy
from .units import inch
from mathutils import Vector
import bmesh

class home_builder_OT_to_do(bpy.types.Operator):
    bl_idname = "home_builder.to_do"
    bl_label = "To Do"
    bl_description = "This is a placeholder for a to do list"

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        pass


class home_builder_OT_set_recommended_settings(bpy.types.Operator):
    bl_idname = "home_builder.set_recommended_settings"
    bl_label = "Set Recommended Settings"
    bl_description = "This will set the recommended blender settings"

    turn_off_relationship_lines: bpy.props.BoolProperty(name="Turn Off Relationship Lines",
                                                        description="This setting clutters the interface with unneeded relationship lines",
                                                        default=True)# type: ignore

    turn_on_object_color_type: bpy.props.BoolProperty(name="Turn On Object Color Type",
                                                        description="This setting turns on the object color type",
                                                        default=True)# type: ignore
    
    use_vertex_snapping: bpy.props.BoolProperty(name="Use Vertex Snapping",
                                                        description="This setting turns on vertex snapping",
                                                        default=True)# type: ignore

    turn_off_3d_cursor: bpy.props.BoolProperty(name="Turn Off 3D Cursor",
                                                        description="This setting turns off the 3D cursor",
                                                        default=True)# type: ignore

    show_wireframes: bpy.props.BoolProperty(name="Show Wireframes",
                                                        description="This setting shows the wireframes",
                                                        default=True)# type: ignore

    change_studio_lighting: bpy.props.BoolProperty(name="Change Studio Lighting",
                                                        description="This setting changes the studio lighting to the recommended lighting",
                                                        default=True)# type: ignore

    auto_run_python_scripts: bpy.props.BoolProperty(name="Auto Run Python Scripts",
                                                        description="This enables auto run python scripts which is required for cabinets to draw correctly",
                                                        default=True)# type: ignore

    def check(self, context):
        return True
    
    def get_view3d_space(self, context):
        """Find the first 3D view space in the current screen"""
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                return area.spaces.active
        return None

    def invoke(self, context, event):
        # Verify we have a 3D view available
        if not self.get_view3d_space(context):
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def execute(self, context):
        view = self.get_view3d_space(context)
        if not view:
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}
        
        overlay = view.overlay
        shading = view.shading        
        tool_settings = context.scene.tool_settings
        
        if self.turn_off_relationship_lines:
            overlay.show_relationship_lines = False
        if self.turn_on_object_color_type:
            shading.color_type = 'OBJECT'
        if self.turn_off_3d_cursor:
            overlay.show_cursor = False
        if self.show_wireframes:
            overlay.show_wireframes = True
            overlay.wireframe_threshold = 0.0
            overlay.wireframe_opacity = 0.8
        if self.change_studio_lighting:
            shading.studio_light = 'paint.sl'
        if self.use_vertex_snapping:
            tool_settings.snap_elements_base = {'VERTEX'}
        if self.auto_run_python_scripts:
            bpy.context.preferences.filepaths.use_scripts_auto_execute = True
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="These are the required Home Builder settings.")
        box.prop(self,'turn_on_object_color_type',text="Turn On Object Color Type - REQUIRED")
        box.prop(self,'auto_run_python_scripts',text="Auto Run Python Scripts - REQUIRED")
        box = layout.box()
        box.label(text="These are the recommended Home Builder settings.")        
        box.prop(self,'turn_off_relationship_lines')
        box.prop(self,'turn_off_3d_cursor')
        box.prop(self,'show_wireframes')
        box.prop(self,'change_studio_lighting')
        box.prop(self,'use_vertex_snapping')


class home_builder_OT_reload_addon(bpy.types.Operator):
    bl_idname = "home_builder.reload_addon"
    bl_label = "Reload Add-on"
    bl_description = "Reload the Home Builder add-on code without restarting Blender"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        import sys
        
        # Store current scene name to return to it
        current_scene = context.scene.name
        
        # Remove all home_builder modules from cache
        modules_to_remove = [k for k in list(sys.modules.keys()) if 'home_builder' in k]
        for mod in modules_to_remove:
            del sys.modules[mod]
        
        # Disable and re-enable addon
        bpy.ops.preferences.addon_disable(module='home_builder_5')
        bpy.ops.preferences.addon_enable(module='home_builder_5')
        
        # Try to return to previous scene
        if current_scene in bpy.data.scenes:
            context.window.scene = bpy.data.scenes[current_scene]
        
        self.report({'INFO'}, f"Reloaded Home Builder (cleared {len(modules_to_remove)} modules)")
        return {'FINISHED'}

class home_builder_annotations_OT_apply_settings_to_all(bpy.types.Operator):
    bl_idname = "home_builder_annotations.apply_settings_to_all"
    bl_label = "Apply Settings to All"
    bl_description = "Apply annotation settings to all annotations in the current scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        hb_scene = context.scene.home_builder
        
        lines_updated = 0
        texts_updated = 0
        dimensions_updated = 0
        
        for obj in context.scene.objects:
            # Update lines, polylines, circles
            if obj.type == 'CURVE' and (obj.get('IS_DETAIL_LINE') or obj.get('IS_DETAIL_POLYLINE') or obj.get('IS_DETAIL_CIRCLE')):
                # Line thickness
                obj.data.bevel_depth = hb_scene.annotation_line_thickness
                
                # Line color
                color = tuple(hb_scene.annotation_line_color) + (1.0,)
                obj.color = color
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    if mat and mat.use_nodes:
                        bsdf = mat.node_tree.nodes.get("Principled BSDF")
                        if bsdf:
                            bsdf.inputs["Base Color"].default_value = color
                
                lines_updated += 1
            
            # Update text annotations
            elif obj.type == 'FONT' and obj.get('IS_DETAIL_TEXT'):
                # Font
                if hb_scene.annotation_font:
                    obj.data.font = hb_scene.annotation_font
                
                # Text size
                obj.data.size = hb_scene.annotation_text_size
                
                # Text color
                color = tuple(hb_scene.annotation_text_color) + (1.0,)
                obj.color = color
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    if mat and mat.use_nodes:
                        bsdf = mat.node_tree.nodes.get("Principled BSDF")
                        if bsdf:
                            bsdf.inputs["Base Color"].default_value = color
                
                texts_updated += 1
            
            # Update dimensions
            elif obj.get('IS_2D_ANNOTATION') and obj.type == 'MESH':
                for mod in obj.modifiers:
                    if mod.type == 'NODES' and mod.node_group:
                        try:
                            mod["Socket_3"] = hb_scene.annotation_dimension_text_size
                        except:
                            pass
                        try:
                            mod["Socket_4"] = hb_scene.annotation_dimension_tick_length
                        except:
                            pass
                        try:
                            mod["Socket_5"] = hb_scene.annotation_dimension_line_thickness
                        except:
                            pass
                
                dimensions_updated += 1
        
        total = lines_updated + texts_updated + dimensions_updated
        self.report({'INFO'}, f"Updated {total} annotations ({lines_updated} lines, {texts_updated} texts, {dimensions_updated} dimensions)")
        return {'FINISHED'}




class home_builder_OT_rendering_settings(bpy.types.Operator):
    bl_idname = "home_builder.rendering_settings"
    bl_label = "Rendering Settings"
    bl_description = "Configure common Eevee rendering settings"
    bl_options = {'REGISTER', 'UNDO'}

    def check(self, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        eevee = scene.eevee
        render = scene.render
        view_settings = scene.view_settings
        
        # Samples
        box = layout.box()
        box.label(text="Quality", icon='RENDER_STILL')
        col = box.column(align=True)
        col.prop(eevee, "taa_render_samples", text="Render Samples")
        col.prop(eevee, "taa_samples", text="Viewport Samples")
        
        # Ray Tracing
        box = layout.box()
        box.label(text="Ray Tracing", icon='LIGHT_SUN')
        col = box.column(align=True)
        col.prop(eevee, "use_raytracing", text="Enable Ray Tracing")
        
        if eevee.use_raytracing:
            col.separator()
            col.prop(eevee.ray_tracing_options, "resolution_scale", text="Resolution Scale")
            col.prop(eevee.ray_tracing_options, "trace_max_roughness", text="Max Roughness")
            
            col.separator()
            col.label(text="Features:")
            row = col.row(align=True)
            row.prop(eevee, "use_shadow_jitter_viewport", text="Soft Shadows", toggle=True)
        
        # Freestyle
        box = layout.box()
        box.label(text="Freestyle", icon='MOD_LINEART')
        col = box.column(align=True)
        col.prop(render, "use_freestyle", text="Enable Freestyle")
        
        if render.use_freestyle:
            col.prop(render, "line_thickness_mode", text="Thickness Mode")
            if render.line_thickness_mode == 'ABSOLUTE':
                col.prop(render, "line_thickness", text="Line Thickness")
            
        # Transparent Background
        box = layout.box()
        box.label(text="Film", icon='IMAGE_DATA')
        col = box.column(align=True)
        col.prop(render, "film_transparent", text="Transparent Background")
        
        # Color Management
        box = layout.box()
        box.label(text="Color Management", icon='COLOR')
        col = box.column(align=True)
        col.prop(view_settings, "view_transform", text="View Transform")
        col.prop(view_settings, "look", text="Look")




class home_builder_OT_create_camera(bpy.types.Operator):
    bl_idname = "home_builder.create_camera"
    bl_label = "Create Camera"
    bl_description = "Create a camera from the current viewport view"
    bl_options = {'REGISTER', 'UNDO'}
    
    add_track_to: bpy.props.BoolProperty(
        name="Add Track To Target",
        description="Create an empty at scene center and track the camera to it",
        default=False
    )  # type: ignore
    
    add_backplate: bpy.props.BoolProperty(
        name="Add Lit Backplate",
        description="Create an emissive plane behind the scene that fills the camera view",
        default=False
    )  # type: ignore
    
    backplate_color: bpy.props.FloatVectorProperty(
        name="Backplate Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )  # type: ignore
    
    backplate_distance: bpy.props.FloatProperty(
        name="Backplate Distance",
        description="Distance from camera to backplate",
        default=50.0,
        min=1.0,
        max=1000.0,
        unit='LENGTH'
    )  # type: ignore

    def get_view3d_area(self, context):
        """Find the first 3D view area in the current screen"""
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                return area
        return None
    
    def get_scene_center(self, context):
        """Calculate the center of all mesh objects in the scene"""
        
        min_co = Vector((float('inf'), float('inf'), float('inf')))
        max_co = Vector((float('-inf'), float('-inf'), float('-inf')))
        has_objects = False
        
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                has_objects = True
                # Get world-space bounding box corners
                for corner in obj.bound_box:
                    world_co = obj.matrix_world @ Vector(corner)
                    min_co.x = min(min_co.x, world_co.x)
                    min_co.y = min(min_co.y, world_co.y)
                    min_co.z = min(min_co.z, world_co.z)
                    max_co.x = max(max_co.x, world_co.x)
                    max_co.y = max(max_co.y, world_co.y)
                    max_co.z = max(max_co.z, world_co.z)
        
        if has_objects:
            return (min_co + max_co) / 2
        return Vector((0, 0, 0))
    
    def create_backplate(self, context, cam_obj):
        """Create a lit backplate plane parented to the camera"""
        import math
        
        cam_data = cam_obj.data
        distance = self.backplate_distance
        
        # Calculate plane size to fill camera view
        # Using vertical FOV and aspect ratio
        render = context.scene.render
        aspect = render.resolution_x / render.resolution_y
        
        # Get vertical FOV
        if cam_data.sensor_fit == 'VERTICAL':
            vfov = 2 * math.atan(cam_data.sensor_height / (2 * cam_data.lens))
        else:
            hfov = 2 * math.atan(cam_data.sensor_width / (2 * cam_data.lens))
            vfov = 2 * math.atan(math.tan(hfov / 2) / aspect)
        
        # Calculate plane dimensions (add 10% margin)
        height = 2 * distance * math.tan(vfov / 2) * 1.1
        width = height * aspect
        
        # Create plane mesh
        mesh = bpy.data.meshes.new("Backplate")
        bm = bmesh.new()
        
        # Create vertices (plane facing +Z, will be rotated by parenting)
        hw, hh = width / 2, height / 2
        v1 = bm.verts.new((-hw, -hh, 0))
        v2 = bm.verts.new((hw, -hh, 0))
        v3 = bm.verts.new((hw, hh, 0))
        v4 = bm.verts.new((-hw, hh, 0))
        bm.faces.new((v1, v2, v3, v4))
        
        bm.to_mesh(mesh)
        bm.free()
        
        # Create object
        backplate = bpy.data.objects.new("Backplate", mesh)
        context.scene.collection.objects.link(backplate)
        
        # Position in front of camera (local -Z)
        backplate.parent = cam_obj
        backplate.location = (0, 0, -distance)
        backplate.rotation_euler = (math.radians(180), 0, 0)
        
        # Create emission material
        mat = bpy.data.materials.new(name="Backplate Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create emission shader
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = self.backplate_color
        emission.inputs['Strength'].default_value = 1.0
        emission.location = (0, 0)
        
        # Create output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Assign material
        backplate.data.materials.append(mat)
        
        # Disable shadow casting
        backplate.visible_shadow = False
        
        return backplate

    def invoke(self, context, event):
        if not self.get_view3d_area(context):
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        area = self.get_view3d_area(context)
        if not area:
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}
        
        space = area.spaces.active
        region_3d = space.region_3d
        
        # Create camera data and object
        cam_data = bpy.data.cameras.new(name="Camera")
        cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
        
        # Link to scene
        context.scene.collection.objects.link(cam_obj)
        
        # Set camera position and rotation from view
        cam_obj.matrix_world = region_3d.view_matrix.inverted()
        
        # Set as active camera
        context.scene.camera = cam_obj
        
        # Add track to constraint if requested
        if self.add_track_to:
            # Create empty at scene center
            center = self.get_scene_center(context)
            empty = bpy.data.objects.new(name="Camera Target", object_data=None)
            empty.empty_display_type = 'SPHERE'
            empty.empty_display_size = 0.1
            empty.location = center
            context.scene.collection.objects.link(empty)
            
            # Add Track To constraint
            constraint = cam_obj.constraints.new(type='TRACK_TO')
            constraint.target = empty
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
            
            # Select both, with camera active
            bpy.ops.object.select_all(action='DESELECT')
            empty.select_set(True)
            cam_obj.select_set(True)
            context.view_layer.objects.active = cam_obj
        else:
            # Select the camera
            bpy.ops.object.select_all(action='DESELECT')
            cam_obj.select_set(True)
            context.view_layer.objects.active = cam_obj
        
        # Add backplate if requested
        if self.add_backplate:
            backplate = self.create_backplate(context, cam_obj)
            backplate.select_set(True)
        
        # Lock camera to view and switch to camera view
        space.lock_camera = True
        space.region_3d.view_perspective = 'CAMERA'
        
        self.report({'INFO'}, f"Created camera: {cam_obj.name}")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "add_track_to")
        
        layout.separator()
        
        layout.prop(self, "add_backplate")
        if self.add_backplate:
            col = layout.column(align=True)
            col.prop(self, "backplate_color", text="Color")
            col.prop(self, "backplate_distance", text="Distance")

classes = (
    home_builder_OT_reload_addon,
    home_builder_OT_to_do,
    home_builder_OT_set_recommended_settings,
    home_builder_OT_rendering_settings,
    home_builder_OT_create_camera,
    home_builder_annotations_OT_apply_settings_to_all,
)

register, unregister = bpy.utils.register_classes_factory(classes)             