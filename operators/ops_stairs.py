import bpy
import math
import bmesh
from mathutils import Vector
from .. import hb_snap, hb_utils, units


def create_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness):
    """Create a straight staircase mesh.
    
    Origin is at the front-bottom corner (first step).
    Stairs extend in +Y (away from viewer) and +Z (upward).
    Width is along +X.
    """
    num_steps = max(1, round(total_rise / riser_height))
    actual_riser = total_rise / num_steps
    
    bm = bmesh.new()
    
    x0, x1 = 0, stair_width
    
    for i in range(num_steps):
        z_top = (i + 1) * actual_riser
        z_tread = z_top - tread_thickness
        y_front = i * tread_depth
        y_back = (i + 1) * tread_depth
        
        # Tread box
        vt = [
            bm.verts.new((x0, y_front, z_tread)),
            bm.verts.new((x1, y_front, z_tread)),
            bm.verts.new((x1, y_back, z_tread)),
            bm.verts.new((x0, y_back, z_tread)),
            bm.verts.new((x0, y_front, z_top)),
            bm.verts.new((x1, y_front, z_top)),
            bm.verts.new((x1, y_back, z_top)),
            bm.verts.new((x0, y_back, z_top)),
        ]
        bm.faces.new([vt[4], vt[5], vt[6], vt[7]])  # top
        bm.faces.new([vt[3], vt[2], vt[1], vt[0]])  # bottom
        bm.faces.new([vt[0], vt[4], vt[7], vt[3]])  # left
        bm.faces.new([vt[1], vt[2], vt[6], vt[5]])  # right
        bm.faces.new([vt[0], vt[1], vt[5], vt[4]])  # front
        bm.faces.new([vt[3], vt[7], vt[6], vt[2]])  # back
        
        # Riser (vertical face in front of tread)
        z_riser_bottom = i * actual_riser
        z_riser_top = z_tread
        if z_riser_top > z_riser_bottom + 0.001:
            vr = [
                bm.verts.new((x0, y_front, z_riser_bottom)),
                bm.verts.new((x1, y_front, z_riser_bottom)),
                bm.verts.new((x1, y_front, z_riser_top)),
                bm.verts.new((x0, y_front, z_riser_top)),
            ]
            bm.faces.new([vr[0], vr[1], vr[2], vr[3]])
    
    total_run = num_steps * tread_depth
    
    # Left stringer - step profile side wall
    profile = []
    profile.append((0, 0))  # front bottom
    for i in range(num_steps):
        y = i * tread_depth
        z_top = (i + 1) * actual_riser
        profile.append((y, z_top))
        profile.append(((i + 1) * tread_depth, z_top))
    profile.append((total_run, 0))  # back bottom
    
    left_verts = [bm.verts.new((0, y, z)) for y, z in profile]
    right_verts = [bm.verts.new((stair_width, y, z)) for y, z in profile]
    
    if len(left_verts) >= 3:
        try:
            bm.faces.new(left_verts)
        except:
            pass
    if len(right_verts) >= 3:
        try:
            bm.faces.new(list(reversed(right_verts)))
        except:
            pass
    
    # Back wall
    bv = [
        bm.verts.new((0, total_run, 0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((stair_width, total_run, total_rise)),
        bm.verts.new((0, total_run, total_rise)),
    ]
    bm.faces.new(bv)
    
    # Bottom
    btv = [
        bm.verts.new((0, 0, 0)),
        bm.verts.new((stair_width, 0, 0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((0, total_run, 0)),
    ]
    bm.faces.new(btv)
    
    # Front face (lowest riser)
    fv = [
        bm.verts.new((0, 0, 0)),
        bm.verts.new((stair_width, 0, 0)),
        bm.verts.new((stair_width, 0, actual_riser)),
        bm.verts.new((0, 0, actual_riser)),
    ]
    bm.faces.new(fv)
    
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return mesh


def rebuild_stair_mesh(obj):
    """Regenerate the stair mesh from the object's custom properties."""
    width = obj.get('STAIR_WIDTH', units.inch(36))
    total_rise = obj.get('STAIR_TOTAL_RISE', units.inch(96))
    riser_height = obj.get('STAIR_RISER_HEIGHT', units.inch(7.5))
    tread_depth = obj.get('STAIR_TREAD_DEPTH', units.inch(10.5))
    tread_thickness = obj.get('STAIR_TREAD_THICKNESS', units.inch(1))
    
    old_mesh = obj.data
    new_mesh = create_stair_mesh(width, total_rise, riser_height, tread_depth, tread_thickness)
    obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh)


class home_builder_stairs_OT_place_stairs(bpy.types.Operator):
    """Place a straight staircase on the floor"""
    bl_idname = "home_builder_stairs.place_stairs"
    bl_label = "Place Stairs"
    bl_description = "Click on the floor to place a staircase"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Modal state
    preview_obj = None
    region = None
    mouse_pos = None
    hit_location = None
    hit_object = None
    hit_face_index = None
    hit_grid = False
    view_point = None
    
    def create_preview(self, context):
        """Create the stair preview mesh."""
        width = units.inch(36)
        total_rise = units.inch(96)
        riser_height = units.inch(7.5)
        tread_depth = units.inch(10.5)
        tread_thickness = units.inch(1)
        
        mesh = create_stair_mesh(width, total_rise, riser_height, tread_depth, tread_thickness)
        
        self.preview_obj = bpy.data.objects.new('Stairs', mesh)
        self.preview_obj.location.z = 0
        context.scene.collection.objects.link(self.preview_obj)
        
        # Store params as custom props
        self.preview_obj['IS_STAIR'] = True
        self.preview_obj['MENU_ID'] = 'HOME_BUILDER_MT_stair_commands'
        self.preview_obj['STAIR_WIDTH'] = width
        self.preview_obj['STAIR_TOTAL_RISE'] = total_rise
        self.preview_obj['STAIR_RISER_HEIGHT'] = riser_height
        self.preview_obj['STAIR_TREAD_DEPTH'] = tread_depth
        self.preview_obj['STAIR_TREAD_THICKNESS'] = tread_thickness
        
        # Material
        mat = bpy.data.materials.new(name="Stair Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.6, 0.45, 0.3, 1.0)
        self.preview_obj.data.materials.append(mat)
    
    def update_preview(self, context):
        if not self.preview_obj:
            return
        
        if self.hit_location:
            loc = Vector(self.hit_location)
            loc.x = hb_snap.snap_value_to_grid(loc.x)
            loc.y = hb_snap.snap_value_to_grid(loc.y)
            loc.z = 0
            self.preview_obj.location = loc
            self.preview_obj.hide_set(False)
        else:
            self.preview_obj.hide_set(True)
    
    def update_header(self, context):
        num_steps = max(1, round(units.inch(96) / units.inch(7.5)))
        text = f"Stairs: {num_steps} steps | Click to place | R to rotate 90\u00b0 | ESC cancel"
        context.area.header_text_set(text)
    
    def confirm_placement(self, context):
        if not self.preview_obj:
            return False
        
        num_steps = max(1, round(
            self.preview_obj['STAIR_TOTAL_RISE'] / self.preview_obj['STAIR_RISER_HEIGHT']
        ))
        self.report({'INFO'}, f"Placed staircase: {num_steps} steps")
        
        # Select the placed stair
        bpy.ops.object.select_all(action='DESELECT')
        self.preview_obj.select_set(True)
        context.view_layer.objects.active = self.preview_obj
        
        self.preview_obj = None
        return True
    
    def cleanup(self, context):
        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None
        context.area.header_text_set(None)
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        
        # Raycast
        self.mouse_pos = Vector((
            event.mouse_x - self.region.x,
            event.mouse_y - self.region.y
        ))
        if self.preview_obj:
            self.preview_obj.hide_set(True)
        hb_snap.main(self, event.ctrl, context)
        self.update_preview(context)
        self.update_header(context)
        
        # R to rotate 90 degrees
        if event.type == 'R' and event.value == 'PRESS':
            if self.preview_obj:
                self.preview_obj.rotation_euler.z += math.radians(90)
            return {'RUNNING_MODAL'}
        
        # Click to place
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.confirm_placement(context):
                self.cleanup(context)
                return {'FINISHED'}
        
        # Cancel
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cleanup(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Must be used in 3D viewport")
            return {'CANCELLED'}
        
        self.region = context.region
        self.preview_obj = None
        
        self.create_preview(context)
        
        context.area.header_text_set("Click to place stairs | R to rotate | ESC to cancel")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class home_builder_stairs_OT_stair_prompts(bpy.types.Operator):
    """Edit staircase properties"""
    bl_idname = "home_builder_stairs.stair_prompts"
    bl_label = "Stair Prompts"
    bl_description = "Edit the staircase dimensions"
    bl_options = {'REGISTER', 'UNDO'}
    
    stair_width: bpy.props.FloatProperty(
        name="Width", subtype='DISTANCE', unit='LENGTH',
        default=0.9144, min=0.3048, precision=5,
    )  # type: ignore
    
    total_rise: bpy.props.FloatProperty(
        name="Total Rise", subtype='DISTANCE', unit='LENGTH',
        default=2.4384, min=0.3048, precision=5,
    )  # type: ignore
    
    riser_height: bpy.props.FloatProperty(
        name="Riser Height", subtype='DISTANCE', unit='LENGTH',
        default=0.1905, min=0.1016, max=0.3048, precision=5,
    )  # type: ignore
    
    tread_depth: bpy.props.FloatProperty(
        name="Tread Depth", subtype='DISTANCE', unit='LENGTH',
        default=0.2667, min=0.1524, precision=5,
    )  # type: ignore
    
    tread_thickness: bpy.props.FloatProperty(
        name="Tread Thickness", subtype='DISTANCE', unit='LENGTH',
        default=0.0254, min=0.0127, precision=5,
    )  # type: ignore
    
    stair_obj = None
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_STAIR')
    
    def check(self, context):
        if not self.stair_obj:
            return False
        
        self.stair_obj['STAIR_WIDTH'] = self.stair_width
        self.stair_obj['STAIR_TOTAL_RISE'] = self.total_rise
        self.stair_obj['STAIR_RISER_HEIGHT'] = self.riser_height
        self.stair_obj['STAIR_TREAD_DEPTH'] = self.tread_depth
        self.stair_obj['STAIR_TREAD_THICKNESS'] = self.tread_thickness
        
        rebuild_stair_mesh(self.stair_obj)
        return True
    
    def invoke(self, context, event):
        self.stair_obj = context.active_object
        if not self.stair_obj or not self.stair_obj.get('IS_STAIR'):
            self.report({'WARNING'}, "Select a staircase first")
            return {'CANCELLED'}
        
        # Read current values from object
        self.stair_width = self.stair_obj.get('STAIR_WIDTH', units.inch(36))
        self.total_rise = self.stair_obj.get('STAIR_TOTAL_RISE', units.inch(96))
        self.riser_height = self.stair_obj.get('STAIR_RISER_HEIGHT', units.inch(7.5))
        self.tread_depth = self.stair_obj.get('STAIR_TREAD_DEPTH', units.inch(10.5))
        self.tread_thickness = self.stair_obj.get('STAIR_TREAD_THICKNESS', units.inch(1))
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        return {'FINISHED'}
    
    def draw(self, context):
        unit_settings = context.scene.unit_settings
        layout = self.layout
        
        num_steps = max(1, round(self.total_rise / self.riser_height))
        actual_riser = self.total_rise / num_steps
        total_run = num_steps * self.tread_depth
        
        box = layout.box()
        box.label(text=f"Steps: {num_steps}", icon='MOD_ARRAY')
        row = box.row()
        row.label(text="Total Run:")
        row.label(text=units.unit_to_string(unit_settings, total_run))
        
        box = layout.box()
        box.prop(self, 'stair_width')
        box.prop(self, 'total_rise')
        box.prop(self, 'riser_height')
        box.prop(self, 'tread_depth')
        box.prop(self, 'tread_thickness')


class home_builder_stairs_OT_delete_stairs(bpy.types.Operator):
    """Delete the selected staircase"""
    bl_idname = "home_builder_stairs.delete_stairs"
    bl_label = "Delete Stairs"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_STAIR')
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.get('IS_STAIR'):
            bpy.data.objects.remove(obj, do_unlink=True)
            self.report({'INFO'}, "Staircase deleted")
        return {'FINISHED'}


class HOME_BUILDER_MT_stair_commands(bpy.types.Menu):
    bl_label = "Stair Commands"
    bl_idname = "HOME_BUILDER_MT_stair_commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_stairs.stair_prompts", text="Stair Prompts", icon='PREFERENCES')
        layout.separator()
        layout.operator("home_builder_stairs.delete_stairs", text="Delete Stairs", icon='X')


classes = (
    home_builder_stairs_OT_place_stairs,
    home_builder_stairs_OT_stair_prompts,
    home_builder_stairs_OT_delete_stairs,
    HOME_BUILDER_MT_stair_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
