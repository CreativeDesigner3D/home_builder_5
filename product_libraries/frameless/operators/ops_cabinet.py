import bpy
from .. import types_frameless
from .. import props_hb_frameless
import os
from mathutils import Vector
from .... import hb_utils, hb_types, units

class hb_frameless_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.cabinet_prompts"
    bl_label = "Cabinet Prompts"
    bl_description = "Edit cabinet properties"
    bl_options = {'UNDO'}

    cabinet_width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5) # type: ignore
    cabinet_height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5) # type: ignore
    cabinet_depth: bpy.props.FloatProperty(name="Depth", unit='LENGTH', precision=5) # type: ignore

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
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        self.cabinet.set_input('Dim X', self.cabinet_width)
        self.cabinet.set_input('Dim Z', self.cabinet_height)
        self.cabinet.set_input('Dim Y', self.cabinet_depth)
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


class hb_frameless_OT_drop_cabinet_to_countertop(bpy.types.Operator):
    bl_idname = "hb_frameless.drop_cabinet_to_countertop"
    bl_label = "Drop to Countertop"
    bl_description = "Lower cabinet height to standard countertop height (36 inches)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            if cabinet_bp and 'CABINET_TYPE' in cabinet_bp:
                return cabinet_bp['CABINET_TYPE'] in ['TALL', 'UPPER']
        return False

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        cabinet = hb_types.GeoNodeCage(cabinet_bp)
        countertop_height = units.inch(36)
        
        if cabinet_bp['CABINET_TYPE'] == 'UPPER':
            # For uppers, move the bottom of the cabinet to countertop height
            current_z = cabinet_bp.location.z
            current_height = cabinet.get_input('Dim Z')
            new_z = countertop_height
            cabinet_bp.location.z = new_z
        elif cabinet_bp['CABINET_TYPE'] == 'TALL':
            # For talls, reduce height so top is at countertop height
            cabinet.set_input('Dim Z', countertop_height)
        
        return {'FINISHED'}


class hb_frameless_OT_drop_cabinet_height(bpy.types.Operator):
    bl_idname = "hb_frameless.drop_cabinet_height"
    bl_label = "Drop Height"
    bl_description = "Lower the cabinet by a specified amount"
    bl_options = {'UNDO'}

    drop_amount: bpy.props.FloatProperty(
        name="Drop Amount",
        unit='LENGTH',
        precision=5,
        default=0.0762  # 3 inches
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        cabinet = hb_types.GeoNodeCage(cabinet_bp)
        current_height = cabinet.get_input('Dim Z')
        cabinet.set_input('Dim Z', current_height - self.drop_amount)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'drop_amount')


class hb_frameless_OT_raise_cabinet_bottom(bpy.types.Operator):
    bl_idname = "hb_frameless.raise_cabinet_bottom"
    bl_label = "Raise Bottom"
    bl_description = "Raise the bottom of the cabinet by a specified amount"
    bl_options = {'UNDO'}

    raise_amount: bpy.props.FloatProperty(
        name="Raise Amount",
        unit='LENGTH',
        precision=5,
        default=0.0762  # 3 inches
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        cabinet = hb_types.GeoNodeCage(cabinet_bp)
        current_height = cabinet.get_input('Dim Z')
        cabinet.set_input('Dim Z', current_height - self.raise_amount)
        cabinet_bp.location.z += self.raise_amount
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'raise_amount')


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
            ('BOTH', "Both", "Add to both sides"),
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

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        # TODO: Implement applied end panel creation
        self.report({'INFO'}, f"Applied end will be added to {self.side} side")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'side', expand=True)


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
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        hb_utils.delete_obj_and_children(cabinet_bp)
        return {'FINISHED'}


class hb_frameless_OT_create_cabinet_group(bpy.types.Operator):
    bl_idname = "hb_frameless.create_cabinet_group"
    bl_label = "Create Cabinet Group"
    bl_description = "This will create a cabinet group for all of the selected cabinets"

    def execute(self, context):
        # Get Selected Cabinets
        selected_cabinets = []
        for obj in context.selected_objects:
            if 'IS_FRAMELESS_CABINET_CAGE' in obj:
                cabinet_cage = types_frameless.Cabinet(obj)
                selected_cabinets.append(cabinet_cage)
        
        if not selected_cabinets:
            self.report({'WARNING'}, "No cabinets selected")
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
        toggle_cabinet_color(cabinet_group,True,type_name="IS_FRAMELESS_CABINET_CAGE",dont_show_parent=False)
        cabinet_group.select_set(True)
        context.view_layer.objects.active = cabinet_group
        for obj in cabinet_group.children_recursive:
            if 'IS_FRAMELESS_CABINET_CAGE' in obj:
                obj.hide_viewport = True
        return {'FINISHED'}


classes = (
    hb_frameless_OT_cabinet_prompts,
    hb_frameless_OT_drop_cabinet_to_countertop,
    hb_frameless_OT_drop_cabinet_height,
    hb_frameless_OT_raise_cabinet_bottom,
    hb_frameless_OT_add_applied_end,
    hb_frameless_OT_delete_cabinet,
    hb_frameless_OT_create_cabinet_group,
    hb_frameless_OT_select_cabinet_group,
)

register, unregister = bpy.utils.register_classes_factory(classes)
