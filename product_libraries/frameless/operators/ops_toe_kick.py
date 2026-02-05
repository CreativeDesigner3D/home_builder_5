import bpy
import math
import os
from mathutils import Vector
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_project, hb_details, hb_types, units


class hb_frameless_OT_create_toe_kick_detail(bpy.types.Operator):
    """Create a new toe kick detail"""
    bl_idname = "hb_frameless.create_toe_kick_detail"
    bl_label = "Create Toe Kick Detail"
    bl_description = "Create a new toe kick detail with a 2D profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Name for the toe kick detail",
        default="Toe Kick Detail"
    )  # type: ignore
    
    def execute(self, context):
        # Get main scene props
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create a new toe kick detail entry
        toe_kick = props.toe_kick_details.add()
        toe_kick.name = self.name

        # Create a detail scene for the toe kick profile
        detail = hb_details.DetailView()
        scene = detail.create(f"Toe Kick - {self.name}")
        scene['IS_TOE_KICK_DETAIL'] = True
        
        # Store the scene name reference
        toe_kick.detail_scene_name = scene.name
        
        # Set as active
        props.active_toe_kick_detail_index = len(props.toe_kick_details) - 1
        
        # Set toe kick detail defaults
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
        
        self.report({'INFO'}, f"Created toe kick detail: {self.name}")
        return {'FINISHED'}
    
    def _draw_cabinet_side_detail(self, context, scene, props):
        """Draw the bottom-front corner of cabinet side profile."""
        
        # Make sure we're in the right scene
        original_scene = context.scene
        context.window.scene = scene
        
        # Get cabinet dimensions from props
        part_thickness = props.default_carcass_part_thickness
        door_to_cab_gap = units.inch(0.125)
        door_overlay = part_thickness - units.inch(.0625)
        door_thickness = units.inch(0.75)
        toe_kick_height = props.default_toe_kick_height
        toe_kick_setback = props.default_toe_kick_setback
        
        # Only show 4" of the corner
        corner_size = units.inch(4)
        
        # Position the detail so the bottom-front corner of the cabinet side is at origin
        # -X axis goes toward the back (depth), +Y axis goes up (height)
        # Origin (0,0) is at the bottom-front corner of the cabinet side panel
        
        hb_scene = scene.home_builder
        
        # Draw cabinet side profile - bottom corner section
        side_profile = hb_details.GeoNodePolyline()
        side_profile.create("Cabinet Side")
        # Start at top of visible section (4" up from bottom of cabinet)
        side_profile.set_point(0, Vector((0, corner_size, 0)))
        # Go down to bottom-front corner of cabinet side
        side_profile.add_point(Vector((0, 0, 0)))
        # Go back along bottom edge toward toe kick setback
        side_profile.add_point(Vector((-toe_kick_setback, 0, 0)))
        # Go down to floor
        side_profile.add_point(Vector((-toe_kick_setback, -toe_kick_height, 0)))
        
        # Draw bottom panel
        bottom_panel = hb_details.GeoNodePolyline()
        bottom_panel.create("Cabinet Bottom")
        bottom_panel.set_point(0, Vector((0, part_thickness, 0)))
        bottom_panel.add_point(Vector((-corner_size, part_thickness, 0)))
        
        # Draw door profile - bottom portion visible in the corner
        door_profile = hb_details.GeoNodePolyline()
        door_profile.create("Door Face")
        door_profile.set_point(0, Vector((door_to_cab_gap, corner_size, 0)))
        door_profile.add_point(Vector((door_to_cab_gap, part_thickness - door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap + door_thickness, part_thickness - door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap + door_thickness, corner_size, 0)))
        
        # --- FLOOR LINE ---
        detail_left = -corner_size - units.inch(1)
        detail_right = door_to_cab_gap + door_thickness + units.inch(2)
        
        floor_line = hb_details.GeoNodePolyline()
        floor_line.create("Floor Line")
        floor_line.set_point(0, Vector((detail_left, -toe_kick_height, 0)))
        floor_line.add_point(Vector((detail_right, -toe_kick_height, 0)))
        
        # Floor label
        floor_text = hb_details.GeoNodeText()
        floor_text.create("Floor Label", "FLOOR", hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            floor_text.obj.data.font = hb_scene.annotation_font
        floor_text.set_location(Vector((detail_right + units.inch(0.25), -toe_kick_height, 0)))
        floor_text.set_alignment('LEFT', 'CENTER')
        
        # --- TOE KICK HEIGHT DIMENSION ---
        tk_dim = hb_types.GeoNodeDimension()
        tk_dim.create("Toe Kick Height Dimension")
        tk_dim.obj.location = Vector((-corner_size - units.inch(0.5), -toe_kick_height, 0))
        tk_dim.obj.rotation_euler.z = math.pi / 2
        tk_dim.obj.data.splines[0].points[1].co = (toe_kick_height, 0, 0, 1)
        tk_dim.set_input("Leader Length", units.inch(-0.5))
        tk_dim.set_decimal()
        
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
        text.create("Label", "TOE KICK DETAIL", hb_scene.annotation_text_size)
        if hb_scene.annotation_font:
            text.obj.data.font = hb_scene.annotation_font
        text.set_location(Vector((0, -toe_kick_height - units.inch(1), 0)))
        text.set_alignment('CENTER', 'TOP')
        
        # Switch back to original scene
        context.window.scene = original_scene


class hb_frameless_OT_delete_toe_kick_detail(bpy.types.Operator):
    """Delete the selected toe kick detail"""
    bl_idname = "hb_frameless.delete_toe_kick_detail"
    bl_label = "Delete Toe Kick Detail"
    bl_description = "Delete the selected toe kick detail and its profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.toe_kick_details) > 0
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.toe_kick_details:
            self.report({'WARNING'}, "No toe kick details to delete")
            return {'CANCELLED'}
        
        index = props.active_toe_kick_detail_index
        toe_kick = props.toe_kick_details[index]
        
        # Delete the associated detail scene if it exists
        detail_scene = toe_kick.get_detail_scene()
        if detail_scene:
            if context.scene == detail_scene:
                context.window.scene = main_scene
            bpy.data.scenes.remove(detail_scene)
        
        # Remove from collection
        toe_kick_name = toe_kick.name
        props.toe_kick_details.remove(index)
        
        # Update active index
        if props.active_toe_kick_detail_index >= len(props.toe_kick_details):
            props.active_toe_kick_detail_index = max(0, len(props.toe_kick_details) - 1)
        
        self.report({'INFO'}, f"Deleted toe kick detail: {toe_kick_name}")
        return {'FINISHED'}


class hb_frameless_OT_edit_toe_kick_detail(bpy.types.Operator):
    """Edit the selected toe kick detail profile"""
    bl_idname = "hb_frameless.edit_toe_kick_detail"
    bl_label = "Edit Toe Kick Detail"
    bl_description = "Open the toe kick detail profile scene for editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.toe_kick_details) == 0:
            return False
        toe_kick = props.toe_kick_details[props.active_toe_kick_detail_index]
        return toe_kick.get_detail_scene() is not None
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        toe_kick = props.toe_kick_details[props.active_toe_kick_detail_index]
        detail_scene = toe_kick.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Toe kick detail scene not found")
            return {'CANCELLED'}
        
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=detail_scene.name)
        
        self.report({'INFO'}, f"Editing toe kick detail: {toe_kick.name}")
        return {'FINISHED'}


classes = (
    hb_frameless_OT_create_toe_kick_detail,
    hb_frameless_OT_delete_toe_kick_detail,
    hb_frameless_OT_edit_toe_kick_detail,
)

register, unregister = bpy.utils.register_classes_factory(classes)
