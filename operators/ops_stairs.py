import bpy
import math
import bmesh
from mathutils import Vector, Matrix
from .. import hb_snap, hb_utils, units


# ---------------------------------------------------------------------------
# Mesh generation helpers
# ---------------------------------------------------------------------------

def add_flight_to_bmesh(bm, num_steps, stair_width, actual_riser, tread_depth, tread_thickness):
    """Add a complete flight of stairs to *bm* at the origin.

    Flight extends in +Y (run), width in +X, rise in +Z.
    Returns a list of all verts created so the caller can transform them.
    """
    created_verts = []
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
            bm.verts.new((x1, y_back,  z_tread)),
            bm.verts.new((x0, y_back,  z_tread)),
            bm.verts.new((x0, y_front, z_top)),
            bm.verts.new((x1, y_front, z_top)),
            bm.verts.new((x1, y_back,  z_top)),
            bm.verts.new((x0, y_back,  z_top)),
        ]
        bm.faces.new([vt[4], vt[5], vt[6], vt[7]])  # top
        bm.faces.new([vt[3], vt[2], vt[1], vt[0]])  # bottom
        bm.faces.new([vt[0], vt[4], vt[7], vt[3]])  # left
        bm.faces.new([vt[1], vt[2], vt[6], vt[5]])  # right
        bm.faces.new([vt[0], vt[1], vt[5], vt[4]])  # front
        bm.faces.new([vt[3], vt[7], vt[6], vt[2]])  # back
        created_verts.extend(vt)

        # Riser
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
            created_verts.extend(vr)

    total_run = num_steps * tread_depth
    total_rise = num_steps * actual_riser

    # Left stringer profile
    profile = [(0, 0)]
    for i in range(num_steps):
        y = i * tread_depth
        z = (i + 1) * actual_riser
        profile.append((y, z))
        profile.append(((i + 1) * tread_depth, z))
    profile.append((total_run, 0))

    left_verts  = [bm.verts.new((0,           y, z)) for y, z in profile]
    right_verts = [bm.verts.new((stair_width, y, z)) for y, z in profile]
    created_verts.extend(left_verts)
    created_verts.extend(right_verts)

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
        bm.verts.new((0,           total_run, 0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((stair_width, total_run, total_rise)),
        bm.verts.new((0,           total_run, total_rise)),
    ]
    bm.faces.new(bv)
    created_verts.extend(bv)

    # Bottom
    btv = [
        bm.verts.new((0,           0,         0)),
        bm.verts.new((stair_width, 0,         0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((0,           total_run, 0)),
    ]
    bm.faces.new(btv)
    created_verts.extend(btv)

    # Front face (first riser)
    fv = [
        bm.verts.new((0,           0, 0)),
        bm.verts.new((stair_width, 0, 0)),
        bm.verts.new((stair_width, 0, actual_riser)),
        bm.verts.new((0,           0, actual_riser)),
    ]
    bm.faces.new(fv)
    created_verts.extend(fv)

    return created_verts


def add_landing_box(bm, x0, y0, z0, x1, y1, z1):
    """Add an axis-aligned box to *bm*.  Returns created verts."""
    v = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    bm.faces.new([v[4], v[5], v[6], v[7]])  # top
    bm.faces.new([v[3], v[2], v[1], v[0]])  # bottom
    bm.faces.new([v[0], v[4], v[7], v[3]])  # left
    bm.faces.new([v[1], v[2], v[6], v[5]])  # right
    bm.faces.new([v[0], v[1], v[5], v[4]])  # front
    bm.faces.new([v[3], v[7], v[6], v[2]])  # back
    return v


# ---------------------------------------------------------------------------
# Stair type mesh builders
# ---------------------------------------------------------------------------

def create_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness,
                      stair_type='STRAIGHT', turn_direction='LEFT', landing_depth=None,
                      landing_height=None):
    """Main dispatch – builds the requested stair type and returns a Mesh."""

    if landing_depth is None:
        landing_depth = stair_width
    if landing_height is None:
        landing_height = total_rise / 2

    if stair_type == 'L_SHAPE':
        return _create_l_stair_mesh(stair_width, total_rise, riser_height,
                                    tread_depth, tread_thickness,
                                    landing_depth, turn_direction, landing_height)
    # Default: straight
    return _create_straight_stair_mesh(stair_width, total_rise, riser_height,
                                       tread_depth, tread_thickness)


def _create_straight_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness):
    num_steps = max(1, round(total_rise / riser_height))
    actual_riser = total_rise / num_steps

    bm = bmesh.new()
    add_flight_to_bmesh(bm, num_steps, stair_width, actual_riser, tread_depth, tread_thickness)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def _create_l_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness,
                          landing_depth, turn_direction, landing_height):
    """Two flights at 90 degrees connected by a landing platform.

    Flight 1 goes in +Y.  The landing sits at *landing_height*.
    Flight 2 covers the remaining rise (total_rise - landing_height).
    Each flight independently calculates its step count and actual riser.

    LEFT  turn -> flight 2 goes in -X direction.
    RIGHT turn -> flight 2 goes in +X direction.
    """
    flight1_rise = max(riser_height, min(landing_height, total_rise - riser_height))
    flight2_rise = total_rise - flight1_rise

    steps_flight1 = max(1, round(flight1_rise / riser_height))
    steps_flight2 = max(1, round(flight2_rise / riser_height))
    actual_riser1 = flight1_rise / steps_flight1
    actual_riser2 = flight2_rise / steps_flight2

    flight1_run = steps_flight1 * tread_depth

    bm = bmesh.new()

    # ---- Flight 1 (at origin, going +Y) ----
    add_flight_to_bmesh(bm, steps_flight1, stair_width, actual_riser1,
                        tread_depth, tread_thickness)

    # ---- Landing ----
    landing_z_bot = flight1_rise - tread_thickness
    landing_z_top = flight1_rise

    if turn_direction == 'LEFT':
        # Landing extends to the left (-X) to make room for flight 2
        lx0 = -landing_depth
        lx1 = stair_width
    else:
        # Landing extends to the right (+X)
        lx0 = 0
        lx1 = stair_width + landing_depth

    ly0 = flight1_run
    ly1 = flight1_run + stair_width

    add_landing_box(bm, lx0, ly0, landing_z_bot, lx1, ly1, landing_z_top)

    # ---- Flight 2 (create at origin then transform) ----
    flight2_verts = add_flight_to_bmesh(bm, steps_flight2, stair_width, actual_riser2,
                                        tread_depth, tread_thickness)

    if turn_direction == 'LEFT':
        # Rotate +90 deg around Z  then translate.
        # After rotation: flight runs in -X, width in +Y.
        # We want its front (y=0 before rot -> x=0 after rot) at x = 0,
        # and width (x=0..W before rot -> y=0..W after rot) at y = flight1_run .. flight1_run+W.
        rot = Matrix.Rotation(math.radians(90), 4, 'Z')
        xlate = Matrix.Translation(Vector((0, flight1_run, flight1_rise)))
    else:
        # Rotate -90 deg around Z then translate.
        # After rotation: flight runs in +X, width in -Y.
        # We want: front at x = stair_width, width spanning y = flight1_run .. flight1_run+W
        rot = Matrix.Rotation(math.radians(-90), 4, 'Z')
        xlate = Matrix.Translation(Vector((stair_width, flight1_run + stair_width, flight1_rise)))

    mat = xlate @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=flight2_verts)

    # ---- Finalize ----
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


# ---------------------------------------------------------------------------
# Rebuild helper
# ---------------------------------------------------------------------------

def rebuild_stair_mesh(obj):
    """Regenerate the stair mesh from the object's custom properties."""
    width           = obj.get('STAIR_WIDTH',           units.inch(36))
    total_rise      = obj.get('STAIR_TOTAL_RISE',      units.inch(96))
    riser_height    = obj.get('STAIR_RISER_HEIGHT',    units.inch(7.5))
    tread_depth     = obj.get('STAIR_TREAD_DEPTH',     units.inch(10.5))
    tread_thickness = obj.get('STAIR_TREAD_THICKNESS', units.inch(1))
    stair_type      = obj.get('STAIR_TYPE',            'STRAIGHT')
    turn_direction  = obj.get('STAIR_TURN_DIRECTION',  'LEFT')
    landing_depth   = obj.get('STAIR_LANDING_DEPTH',   width)
    landing_height  = obj.get('STAIR_LANDING_HEIGHT',  total_rise / 2)

    old_mesh = obj.data
    new_mesh = create_stair_mesh(width, total_rise, riser_height, tread_depth, tread_thickness,
                                 stair_type, turn_direction, landing_depth, landing_height)
    obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class home_builder_stairs_OT_place_stairs(bpy.types.Operator):
    """Place a staircase on the floor"""
    bl_idname = "home_builder_stairs.place_stairs"
    bl_label = "Place Stairs"
    bl_description = "Click on the floor to place a staircase"
    bl_options = {'REGISTER', 'UNDO'}

    stair_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('STRAIGHT', "Straight", "Straight staircase"),
            ('L_SHAPE',  "L-Shaped", "90\u00b0 turn with landing"),
        ],
        default='STRAIGHT',
    )  # type: ignore

    turn_direction: bpy.props.EnumProperty(
        name="Turn",
        items=[
            ('LEFT',  "Left",  "Second flight turns left"),
            ('RIGHT', "Right", "Second flight turns right"),
        ],
        default='LEFT',
    )  # type: ignore

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
        width           = units.inch(36)
        total_rise      = units.inch(96)
        riser_height    = units.inch(7.5)
        tread_depth     = units.inch(10.5)
        tread_thickness = units.inch(1)

        mesh = create_stair_mesh(width, total_rise, riser_height, tread_depth, tread_thickness,
                                 self.stair_type, self.turn_direction)

        self.preview_obj = bpy.data.objects.new('Stairs', mesh)
        self.preview_obj.location.z = 0
        context.scene.collection.objects.link(self.preview_obj)

        self.preview_obj['IS_STAIR']             = True
        self.preview_obj['MENU_ID']              = 'HOME_BUILDER_MT_stair_commands'
        self.preview_obj['STAIR_WIDTH']           = width
        self.preview_obj['STAIR_TOTAL_RISE']      = total_rise
        self.preview_obj['STAIR_RISER_HEIGHT']    = riser_height
        self.preview_obj['STAIR_TREAD_DEPTH']     = tread_depth
        self.preview_obj['STAIR_TREAD_THICKNESS'] = tread_thickness
        self.preview_obj['STAIR_TYPE']            = self.stair_type
        self.preview_obj['STAIR_TURN_DIRECTION']  = self.turn_direction
        self.preview_obj['STAIR_LANDING_DEPTH']   = width
        self.preview_obj['STAIR_LANDING_HEIGHT']  = total_rise / 2

        mat = bpy.data.materials.new(name="Stair Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
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
        label = "L-Shaped" if self.stair_type == 'L_SHAPE' else "Straight"
        num_steps = max(1, round(units.inch(96) / units.inch(7.5)))
        text = (f"{label} Stairs: {num_steps} steps | "
                "Click to place | R rotate | "
                "T toggle type | D toggle direction | ESC cancel")
        context.area.header_text_set(text)

    def confirm_placement(self, context):
        if not self.preview_obj:
            return False
        num_steps = max(1, round(
            self.preview_obj['STAIR_TOTAL_RISE'] / self.preview_obj['STAIR_RISER_HEIGHT']
        ))
        self.report({'INFO'}, f"Placed staircase: {num_steps} steps")
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

    def rebuild_preview(self, context):
        """Destroy and recreate the preview after a type/direction change."""
        loc = self.preview_obj.location.copy() if self.preview_obj else None
        rot = self.preview_obj.rotation_euler.copy() if self.preview_obj else None
        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None
        self.create_preview(context)
        if loc:
            self.preview_obj.location = loc
        if rot:
            self.preview_obj.rotation_euler = rot

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        self.mouse_pos = Vector((
            event.mouse_x - self.region.x,
            event.mouse_y - self.region.y
        ))
        if self.preview_obj:
            self.preview_obj.hide_set(True)
        hb_snap.main(self, event.ctrl, context)
        self.update_preview(context)
        self.update_header(context)

        # R - rotate 90 deg
        if event.type == 'R' and event.value == 'PRESS':
            if self.preview_obj:
                self.preview_obj.rotation_euler.z += math.radians(90)
            return {'RUNNING_MODAL'}

        # T - toggle stair type
        if event.type == 'T' and event.value == 'PRESS':
            if self.stair_type == 'STRAIGHT':
                self.stair_type = 'L_SHAPE'
            else:
                self.stair_type = 'STRAIGHT'
            self.rebuild_preview(context)
            return {'RUNNING_MODAL'}

        # D - toggle turn direction
        if event.type == 'D' and event.value == 'PRESS':
            if self.turn_direction == 'LEFT':
                self.turn_direction = 'RIGHT'
            else:
                self.turn_direction = 'LEFT'
            if self.stair_type == 'L_SHAPE':
                self.rebuild_preview(context)
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.confirm_placement(context):
                self.cleanup(context)
                return {'FINISHED'}

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
        context.area.header_text_set("Click to place | R rotate | T type | D direction | ESC cancel")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class home_builder_stairs_OT_stair_prompts(bpy.types.Operator):
    """Edit staircase properties"""
    bl_idname = "home_builder_stairs.stair_prompts"
    bl_label = "Stair Prompts"
    bl_description = "Edit the staircase dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    stair_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('STRAIGHT', "Straight", "Straight staircase"),
            ('L_SHAPE',  "L-Shaped", "90\u00b0 turn with landing"),
        ],
        default='STRAIGHT',
    )  # type: ignore

    turn_direction: bpy.props.EnumProperty(
        name="Turn Direction",
        items=[
            ('LEFT',  "Left",  "Second flight turns left"),
            ('RIGHT', "Right", "Second flight turns right"),
        ],
        default='LEFT',
    )  # type: ignore

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

    landing_depth: bpy.props.FloatProperty(
        name="Landing Depth", subtype='DISTANCE', unit='LENGTH',
        default=0.9144, min=0.3048, precision=5,
    )  # type: ignore

    landing_height: bpy.props.FloatProperty(
        name="Landing Height", subtype='DISTANCE', unit='LENGTH',
        default=1.2192, min=0.1905, precision=5,
        description="Height of the landing platform (splits rise between flights)",
    )  # type: ignore

    stair_obj = None

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_STAIR')

    def check(self, context):
        if not self.stair_obj:
            return False
        self.stair_obj['STAIR_WIDTH']           = self.stair_width
        self.stair_obj['STAIR_TOTAL_RISE']      = self.total_rise
        self.stair_obj['STAIR_RISER_HEIGHT']    = self.riser_height
        self.stair_obj['STAIR_TREAD_DEPTH']     = self.tread_depth
        self.stair_obj['STAIR_TREAD_THICKNESS'] = self.tread_thickness
        self.stair_obj['STAIR_TYPE']            = self.stair_type
        self.stair_obj['STAIR_TURN_DIRECTION']  = self.turn_direction
        self.stair_obj['STAIR_LANDING_DEPTH']   = self.landing_depth
        self.stair_obj['STAIR_LANDING_HEIGHT']  = self.landing_height
        rebuild_stair_mesh(self.stair_obj)
        return True

    def invoke(self, context, event):
        self.stair_obj = context.active_object
        if not self.stair_obj or not self.stair_obj.get('IS_STAIR'):
            self.report({'WARNING'}, "Select a staircase first")
            return {'CANCELLED'}
        self.stair_width     = self.stair_obj.get('STAIR_WIDTH',           units.inch(36))
        self.total_rise      = self.stair_obj.get('STAIR_TOTAL_RISE',      units.inch(96))
        self.riser_height    = self.stair_obj.get('STAIR_RISER_HEIGHT',    units.inch(7.5))
        self.tread_depth     = self.stair_obj.get('STAIR_TREAD_DEPTH',     units.inch(10.5))
        self.tread_thickness = self.stair_obj.get('STAIR_TREAD_THICKNESS', units.inch(1))
        self.stair_type      = self.stair_obj.get('STAIR_TYPE',            'STRAIGHT')
        self.turn_direction  = self.stair_obj.get('STAIR_TURN_DIRECTION',  'LEFT')
        self.landing_depth   = self.stair_obj.get('STAIR_LANDING_DEPTH',   self.stair_width)
        self.landing_height  = self.stair_obj.get('STAIR_LANDING_HEIGHT',  self.total_rise / 2)
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        unit_settings = context.scene.unit_settings
        layout = self.layout

        # Type selector
        box = layout.box()
        box.prop(self, 'stair_type')
        if self.stair_type == 'L_SHAPE':
            box.prop(self, 'turn_direction')
            box.prop(self, 'landing_depth')
            box.prop(self, 'landing_height')

        # Info box
        box = layout.box()
        if self.stair_type == 'L_SHAPE':
            landing_h = max(self.riser_height,
                            min(self.landing_height, self.total_rise - self.riser_height))
            flight2_rise = self.total_rise - landing_h
            steps1 = max(1, round(landing_h / self.riser_height))
            steps2 = max(1, round(flight2_rise / self.riser_height))
            box.label(text=f"Flight 1: {steps1} steps", icon='MOD_ARRAY')
            box.label(text=f"Flight 2: {steps2} steps")
            row = box.row()
            row.label(text="Total Steps:")
            row.label(text=str(steps1 + steps2))
        else:
            num_steps = max(1, round(self.total_rise / self.riser_height))
            total_run = num_steps * self.tread_depth
            box.label(text=f"Steps: {num_steps}", icon='MOD_ARRAY')
            row = box.row()
            row.label(text="Total Run:")
            row.label(text=units.unit_to_string(unit_settings, total_run))

        # Dimensions
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
