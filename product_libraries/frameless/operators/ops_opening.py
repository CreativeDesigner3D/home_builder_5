import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_types, units

class hb_frameless_OT_change_bay_opening(bpy.types.Operator):
    bl_idname = "hb_frameless.change_bay_opening"
    bl_label = "Change Bay Opening"
    bl_description = "Change the type of opening in this bay"
    bl_options = {'UNDO'}

    opening_type: bpy.props.EnumProperty(
        name="Opening Type",
        items=[
            ('DOOR_DRAWER', "Door/Drawer", "Standard door with drawer option"),
            ('LEFT_DOOR', "Left Door", "Single left swing door"),
            ('RIGHT_DOOR', "Right Door", "Single right swing door"),
            ('DOUBLE_DOORS', "Double Doors", "Double swing doors"),
            ('SINGLE_DRAWER', "Single Drawer", "Single drawer"),
            ('2_DRAWER_STACK', "2 Drawer Stack", "Two equal drawers"),
            ('3_DRAWER_STACK', "3 Drawer Stack", "Three equal drawers"),
            ('4_DRAWER_STACK', "4 Drawer Stack", "Four equal drawers"),
            ('OPEN', "Open", "Open with no front"),
        ],
        default='DOOR_DRAWER'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            if 'IS_FRAMELESS_BAY_CAGE' in obj:
                return True
            bay_bp = hb_utils.get_bay_bp(obj)
            return bay_bp is not None
        return False

    def delete_bay_children(self, bay_obj):
        """Delete all children of the bay."""
        children = list(bay_obj.children)
        for child in children:
            self.delete_bay_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def add_cage_to_bay(self, bay, cage):
        """Add a cage to the bay with proper dimension drivers."""
        cage.create()
        cage.obj.parent = bay.obj
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        cage.driver_input('Dim X', 'dim_x', [dim_x])
        cage.driver_input('Dim Y', 'dim_y', [dim_y])
        cage.driver_input('Dim Z', 'dim_z', [dim_z])

    def get_cabinet_type(self, bay_obj):
        """Get the cabinet type from the cabinet parent."""
        cabinet_bp = hb_utils.get_cabinet_bp(bay_obj)
        if cabinet_bp:
            return cabinet_bp.get('CABINET_TYPE', 'BASE')
        return 'BASE'

    def create_doors(self, bay, door_swing):
        """Create doors opening with specified swing direction."""
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        doors = types_frameless.Doors()
        if cabinet_type == 'UPPER':
            doors.door_pull_location = "Upper"
        else:
            doors.door_pull_location = "Base"
        
        self.add_cage_to_bay(bay, doors)
        
        # Set door swing: 0=Left, 1=Right, 2=Double
        doors.obj['Door Swing'] = door_swing

    def create_drawer(self, bay):
        """Create single drawer opening."""
        drawer = types_frameless.Drawer()
        self.add_cage_to_bay(bay, drawer)

    def create_door_drawer(self, bay):
        """Create door/drawer combo (drawer on top, doors below)."""
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        drawer = types_frameless.Drawer()
        drawer.half_overlay_bottom = True
        
        door = types_frameless.Doors()
        door.half_overlay_top = True
        if cabinet_type == 'UPPER':
            door.door_pull_location = "Upper"
        else:
            door.door_pull_location = "Base"

        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [props.top_drawer_front_height, 0]
        splitter.opening_inserts = [drawer, door]
        self.add_cage_to_bay(bay, splitter)

    def create_drawer_stack(self, bay, count):
        """Create a stack of drawers."""
        props = bpy.context.scene.hb_frameless
        equal_drawer_stack_heights = props.equal_drawer_stack_heights
        
        if equal_drawer_stack_heights:
            top_drawer_height = 0
        else:
            top_drawer_height = props.top_drawer_front_height

        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = count - 1
        
        for i in range(count):
            drawer = types_frameless.Drawer()
            if i == 0:
                drawer.half_overlay_bottom = True
                splitter.opening_sizes.append(top_drawer_height)
            elif i == count - 1:
                drawer.half_overlay_top = True
                splitter.opening_sizes.append(0)
            else:
                drawer.half_overlay_top = True
                drawer.half_overlay_bottom = True
                splitter.opening_sizes.append(0)
            splitter.opening_inserts.append(drawer)
        
        self.add_cage_to_bay(bay, splitter)

    def execute(self, context):
        bay_obj = context.object if 'IS_FRAMELESS_BAY_CAGE' in context.object else hb_utils.get_bay_bp(context.object)
        if not bay_obj:
            self.report({'ERROR'}, "Could not find bay")
            return {'CANCELLED'}
        
        bay = types_frameless.CabinetBay(bay_obj)
        
        # Delete existing bay children
        self.delete_bay_children(bay_obj)
        
        # Create new opening based on type
        if self.opening_type == 'DOOR_DRAWER':
            self.create_door_drawer(bay)
        elif self.opening_type == 'LEFT_DOOR':
            self.create_doors(bay, door_swing=0)
        elif self.opening_type == 'RIGHT_DOOR':
            self.create_doors(bay, door_swing=1)
        elif self.opening_type == 'DOUBLE_DOORS':
            self.create_doors(bay, door_swing=2)
        elif self.opening_type == 'SINGLE_DRAWER':
            self.create_drawer(bay)
        elif self.opening_type == '2_DRAWER_STACK':
            self.create_drawer_stack(bay, 2)
        elif self.opening_type == '3_DRAWER_STACK':
            self.create_drawer_stack(bay, 3)
        elif self.opening_type == '4_DRAWER_STACK':
            self.create_drawer_stack(bay, 4)
        elif self.opening_type == 'OPEN':
            pass  # No children needed for open
        
        hb_utils.run_calc_fix(context, bay.obj)
        hb_utils.run_calc_fix(context, bay.obj)
        return {'FINISHED'}


class hb_frameless_OT_opening_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.opening_prompts"
    bl_label = "Opening Prompts"
    bl_description = "Edit opening properties"
    bl_options = {'UNDO'}

    door_swing: bpy.props.EnumProperty(
        name="Door Swing",
        items=[
            ('0', "Left", "Left swing"),
            ('1', "Right", "Right swing"),
            ('2', "Double", "Double doors"),
        ],
        default='2'
    ) # type: ignore

    inset_front: bpy.props.BoolProperty(name="Inset Front", default=False) # type: ignore

    opening = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            if 'IS_FRAMELESS_OPENING_CAGE' in obj:
                return True
            opening_bp = hb_utils.get_opening_bp(obj)
            return opening_bp is not None
        return False

    def invoke(self, context, event):
        opening_bp = context.object if 'IS_FRAMELESS_OPENING_CAGE' in context.object else hb_utils.get_opening_bp(context.object)
        self.opening = hb_types.GeoNodeCage(opening_bp)
        
        if 'Door Swing' in opening_bp:
            self.door_swing = str(opening_bp['Door Swing'])
        if 'Inset Front' in opening_bp:
            self.inset_front = opening_bp['Inset Front']
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def check(self, context):
        if 'Door Swing' in self.opening.obj:
            self.opening.obj['Door Swing'] = int(self.door_swing)
        if 'Inset Front' in self.opening.obj:
            self.opening.obj['Inset Front'] = self.inset_front
        hb_utils.run_calc_fix(context, self.opening.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        if 'Door Swing' in self.opening.obj:
            row = box.row()
            row.label(text="Door Swing:")
            row.prop(self, 'door_swing', text="")
        
        if 'Inset Front' in self.opening.obj:
            row = box.row()
            row.prop(self, 'inset_front')


class hb_frameless_OT_change_opening_type(bpy.types.Operator):
    bl_idname = "hb_frameless.change_opening_type"
    bl_label = "Change Opening Type"
    bl_description = "Change this opening to a different type"
    bl_options = {'UNDO'}

    opening_type: bpy.props.EnumProperty(
        name="Opening Type",
        items=[
            ('DOORS', "Doors", "Door opening"),
            ('DRAWER', "Drawer", "Drawer opening"),
            ('OPEN', "Open", "Open (no front)"),
        ],
        default='DOORS'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            if 'IS_FRAMELESS_OPENING_CAGE' in obj:
                return True
            opening_bp = hb_utils.get_opening_bp(obj)
            return opening_bp is not None
        return False

    def execute(self, context):
        opening_bp = context.object if 'IS_FRAMELESS_OPENING_CAGE' in context.object else hb_utils.get_opening_bp(context.object)
        # TODO: Implement opening type change
        self.report({'INFO'}, f"Opening will be changed to {self.opening_type}")
        return {'FINISHED'}


class hb_frameless_OT_custom_vertical_splitter(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_vertical_splitter"
    bl_label = "Custom Vertical Openings"
    bl_description = "Create custom vertical openings with adjustable sizes"
    bl_options = {'UNDO'}

    opening_count: bpy.props.IntProperty(
        name="Number of Openings",
        min=2, max=10,
        default=2
    ) # type: ignore

    # Opening heights (0 = equal distribution)
    opening_1_height: bpy.props.FloatProperty(name="Opening 1 Height", unit='LENGTH', default=0) # type: ignore
    opening_2_height: bpy.props.FloatProperty(name="Opening 2 Height", unit='LENGTH', default=0) # type: ignore
    opening_3_height: bpy.props.FloatProperty(name="Opening 3 Height", unit='LENGTH', default=0) # type: ignore
    opening_4_height: bpy.props.FloatProperty(name="Opening 4 Height", unit='LENGTH', default=0) # type: ignore
    opening_5_height: bpy.props.FloatProperty(name="Opening 5 Height", unit='LENGTH', default=0) # type: ignore

    # Opening inserts
    opening_1_insert: bpy.props.EnumProperty(name="Opening 1", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_2_insert: bpy.props.EnumProperty(name="Opening 2", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_3_insert: bpy.props.EnumProperty(name="Opening 3", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_4_insert: bpy.props.EnumProperty(name="Opening 4", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_5_insert: bpy.props.EnumProperty(name="Opening 5", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bay_bp = hb_utils.get_bay_bp(obj)
            opening_bp = hb_utils.get_opening_bp(obj)
            return bay_bp is not None or opening_bp is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def execute(self, context):
        # TODO: Implement the actual splitter creation
        # 1. Find parent bay or opening
        # 2. Delete existing children
        # 3. Create SplitterVertical with settings
        
        self.report({'INFO'}, f"Will create {self.opening_count} vertical openings")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'opening_count')
        
        box = layout.box()
        box.label(text="Opening Configuration (0 = Equal):")
        
        heights = [self.opening_1_height, self.opening_2_height, self.opening_3_height, 
                   self.opening_4_height, self.opening_5_height]
        inserts = ['opening_1_insert', 'opening_2_insert', 'opening_3_insert',
                   'opening_4_insert', 'opening_5_insert']
        height_props = ['opening_1_height', 'opening_2_height', 'opening_3_height',
                        'opening_4_height', 'opening_5_height']
        
        for i in range(min(self.opening_count, 5)):
            row = box.row(align=True)
            row.label(text=f"Opening {i+1}:")
            row.prop(self, height_props[i], text="Height")
            row.prop(self, inserts[i], text="")


class hb_frameless_OT_custom_horizontal_splitter(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_horizontal_splitter"
    bl_label = "Custom Horizontal Openings"
    bl_description = "Create custom horizontal openings with adjustable sizes"
    bl_options = {'UNDO'}

    opening_count: bpy.props.IntProperty(
        name="Number of Openings",
        min=2, max=10,
        default=2
    ) # type: ignore

    # Opening widths (0 = equal distribution)
    opening_1_width: bpy.props.FloatProperty(name="Opening 1 Width", unit='LENGTH', default=0) # type: ignore
    opening_2_width: bpy.props.FloatProperty(name="Opening 2 Width", unit='LENGTH', default=0) # type: ignore
    opening_3_width: bpy.props.FloatProperty(name="Opening 3 Width", unit='LENGTH', default=0) # type: ignore
    opening_4_width: bpy.props.FloatProperty(name="Opening 4 Width", unit='LENGTH', default=0) # type: ignore
    opening_5_width: bpy.props.FloatProperty(name="Opening 5 Width", unit='LENGTH', default=0) # type: ignore

    # Opening inserts
    opening_1_insert: bpy.props.EnumProperty(name="Opening 1", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_2_insert: bpy.props.EnumProperty(name="Opening 2", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_3_insert: bpy.props.EnumProperty(name="Opening 3", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_4_insert: bpy.props.EnumProperty(name="Opening 4", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_5_insert: bpy.props.EnumProperty(name="Opening 5", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bay_bp = hb_utils.get_bay_bp(obj)
            opening_bp = hb_utils.get_opening_bp(obj)
            return bay_bp is not None or opening_bp is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def execute(self, context):
        # TODO: Implement the actual splitter creation
        # 1. Find parent bay or opening
        # 2. Delete existing children
        # 3. Create SplitterHorizontal with settings
        
        self.report({'INFO'}, f"Will create {self.opening_count} horizontal openings")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'opening_count')
        
        box = layout.box()
        box.label(text="Opening Configuration (0 = Equal):")
        
        width_props = ['opening_1_width', 'opening_2_width', 'opening_3_width',
                       'opening_4_width', 'opening_5_width']
        inserts = ['opening_1_insert', 'opening_2_insert', 'opening_3_insert',
                   'opening_4_insert', 'opening_5_insert']
        
        for i in range(min(self.opening_count, 5)):
            row = box.row(align=True)
            row.label(text=f"Opening {i+1}:")
            row.prop(self, width_props[i], text="Width")
            row.prop(self, inserts[i], text="")


classes = (
    hb_frameless_OT_change_bay_opening,
    hb_frameless_OT_opening_prompts,
    hb_frameless_OT_change_opening_type,
    hb_frameless_OT_custom_vertical_splitter,
    hb_frameless_OT_custom_horizontal_splitter,
)

register, unregister = bpy.utils.register_classes_factory(classes)
