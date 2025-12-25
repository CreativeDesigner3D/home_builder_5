import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from . import hb_utils, hb_types
from .units import inch
from .hb_types import Variable

def update_main_tab(self,context):
    # TODO: Load the correct library based on the main_tab
    print("update_main_tab")


def update_product_tab(self,context):
    # TODO: Load the correct library based on the product_tab
    print("update_product_tab")


def update_line_thickness(self, context):
    """Update all curve line thicknesses in the scene."""
    for obj in context.scene.objects:
        if obj.type == 'CURVE':
            # Skip dimensions (they have their own thickness via geometry nodes)
            if obj.get('IS_2D_ANNOTATION'):
                continue
            # Update detail lines, polylines, circles, rectangles
            if obj.get('IS_DETAIL_LINE') or obj.get('IS_DETAIL_POLYLINE') or obj.get('IS_DETAIL_CIRCLE'):
                obj.data.bevel_depth = self.annotation_line_thickness


def update_line_color(self, context):
    """Update all annotation line colors in the scene."""
    color = tuple(self.annotation_line_color) + (1.0,)  # Add alpha
    for obj in context.scene.objects:
        if obj.type == 'CURVE':
            if obj.get('IS_DETAIL_LINE') or obj.get('IS_DETAIL_POLYLINE') or obj.get('IS_DETAIL_CIRCLE'):
                obj.color = color
                # Update material if exists
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    if mat and mat.use_nodes:
                        bsdf = mat.node_tree.nodes.get("Principled BSDF")
                        if bsdf:
                            bsdf.inputs["Base Color"].default_value = color


def update_text_size(self, context):
    """Update all text annotation sizes in the scene."""
    for obj in context.scene.objects:
        if obj.type == 'FONT' and obj.get('IS_DETAIL_TEXT'):
            obj.data.size = self.annotation_text_size


def update_text_color(self, context):
    """Update all text annotation colors in the scene."""
    color = tuple(self.annotation_text_color) + (1.0,)  # Add alpha
    for obj in context.scene.objects:
        if obj.type == 'FONT' and obj.get('IS_DETAIL_TEXT'):
            obj.color = color
            if obj.data.materials:
                mat = obj.data.materials[0]
                if mat and mat.use_nodes:
                    bsdf = mat.node_tree.nodes.get("Principled BSDF")
                    if bsdf:
                        bsdf.inputs["Base Color"].default_value = color


def update_dimension_text_size(self, context):
    """Update all dimension text sizes in the scene."""
    for obj in context.scene.objects:
        if obj.get('IS_DIMENSION'):
            dim = hb_types.GeoNodeDimension(obj)
            dim.set_input("Text Size", self.annotation_dimension_text_size)


def update_dimension_tick_length(self, context):
    """Update all dimension arrow sizes in the scene."""
    for obj in context.scene.objects:
        if obj.get('IS_DIMENSION'):
            dim = hb_types.GeoNodeDimension(obj)
            dim.set_input("Tick Length", self.annotation_dimension_tick_length)


def update_dimension_line_thickness(self, context):
    """Update all dimension line thicknesses in the scene."""
    for obj in context.scene.objects:
        if obj.get('IS_DIMENSION'):
            dim = hb_types.GeoNodeDimension(obj)
            dim.set_input("Line Thickness", self.annotation_dimension_line_thickness)


def update_font(self, context):
    """Update all text annotations to use the selected font."""
    if not self.annotation_font:
        return
    for obj in context.scene.objects:
        if obj.type == 'FONT' and obj.get('IS_DETAIL_TEXT'):
            obj.data.font = self.annotation_font

def update_show_entry_door_and_window_cages(self, context):
    for obj in context.scene.objects:
        if obj.get('IS_ENTRY_DOOR_BP'):
            obj.display_type = 'TEXTURED' if self.show_entry_door_and_window_cages else 'WIRE'
            obj.show_in_front = True if self.show_entry_door_and_window_cages else False
        if obj.get('IS_WINDOW_BP'):
            obj.display_type = 'TEXTURED' if self.show_entry_door_and_window_cages else 'WIRE'
            obj.show_in_front = True if self.show_entry_door_and_window_cages else False

class Calculator_Prompt(PropertyGroup):
    distance_value: FloatProperty(name="Distance Value",subtype='DISTANCE',precision=5)# type: ignore
    equal: BoolProperty(name="Equal",default=True)# type: ignore
    include: BoolProperty(name="Include In Calculation",default=True)# type: ignore

    def draw(self,layout):
        row = layout.row()
        row.active = False if self.equal else True
        row.prop(self,'distance_value',text=self.name)
        row.prop(self,'equal',text="")

    def get_var(self,calculator_name,name):
        prompt_path = 'home_builder.calculators["' + calculator_name + '"].prompts["' + self.name + '"]'
        return Variable(self.id_data, prompt_path + '.distance_value',name)    

    def get_value(self):
        return self.distance_value

    def set_value(self,value):
        self.distance_value = value


class Calculator(PropertyGroup):
    prompts: CollectionProperty(name="Prompts",type=Calculator_Prompt)# type: ignore
    distance_obj: PointerProperty(name="Distance Obj",type=bpy.types.Object)# type: ignore

    def set_total_distance(self,expression="",variables=[],value=0):
        data_path = 'home_builder.calculator_distance'
        driver = self.distance_obj.driver_add(data_path)
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def draw(self,layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text=self.name)
        props = row.operator('pc_prompts.add_calculator_prompt',text="",icon='ADD')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name
        props = row.operator('pc_prompts.edit_calculator',text="",icon='OUTLINER_DATA_GP_LAYER')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name
        
        box.prop(self.distance_obj.home_builder,'calculator_distance')
        box = col.box()
        for prompt in self.prompts:
            prompt.draw(box)
        box = col.box()
        row = box.row()
        row.scale_y = 1.3
        props = row.operator('pc_prompts.run_calculator')
        props.calculator_name = self.name
        props.obj_name = self.id_data.name        

    def add_calculator_prompt(self,name):
        prompt = self.prompts.add()
        prompt.name = name
        return prompt

    def get_calculator_prompt(self,name):
        if name in self.prompts:
            return self.prompts[name]

    def remove_calculator_prompt(self,name):
        pass

    def calculate(self):
        if not self.distance_obj:
            return
        self.distance_obj.hide_viewport = False
        bpy.context.view_layer.update()
        non_equal_prompts_total_value = 0
        equal_prompt_qty = 0
        calc_prompts = []
        for prompt in self.prompts:
            if prompt.equal:
                if prompt.include:
                    equal_prompt_qty += 1
                calc_prompts.append(prompt)
            else:
                if prompt.include:
                    non_equal_prompts_total_value += prompt.distance_value

        if equal_prompt_qty > 0:
            prompt_value = (self.distance_obj.home_builder.calculator_distance - non_equal_prompts_total_value) / equal_prompt_qty

            for prompt in calc_prompts:
                if prompt.include:
                    prompt.distance_value = prompt_value
                else:
                    prompt.distance_value = 0

            self.id_data.location = self.id_data.location 


class Home_Builder_Object_Props(PropertyGroup):
   
    mod_name: StringProperty(name="Mod Name", default="")

    connected_object: PointerProperty(name="Connected Object",
                                      type=bpy.types.Object,
                                      description="This is the used to store objects that are connected together.")# type: ignore  

    calculators: CollectionProperty(type=Calculator, name="Calculators")# type: ignore
    calculator_distance: FloatProperty(name="Calculator Distance",subtype='DISTANCE')# type: ignore
    calculator_index: IntProperty(name="Calculator Index")# type: ignore

    def add_property(self,name,type,value,combobox_items=[]):
        obj = self.id_data
        if type == 'CHECKBOX':
            obj[name] = value
            obj.id_properties_ensure()
            pm = obj.id_properties_ui(name)
            pm.update(description='HOME_BUILDER_PROP')

        if type == 'DISTANCE':
            obj[name] = value
            obj.id_properties_ensure()
            pm = obj.id_properties_ui(name)
            pm.update(subtype='DISTANCE',description='HOME_BUILDER_PROP')

        if type == 'ANGLE':
            obj[name] = value
            obj.id_properties_ensure()
            pm = obj.id_properties_ui(name)
            pm.update(subtype='ANGLE',description='HOME_BUILDER_PROP')

        if type == 'PERCENTAGE':
            obj[name] = value
            obj.id_properties_ensure()
            pm = obj.id_properties_ui(name)
            pm.update(subtype='PERCENTAGE',min=0,max=100,description='HOME_BUILDER_PROP')

        if type == 'QUANTITY':
            obj[name] = value
            obj.id_properties_ensure()
            pm = obj.id_properties_ui(name)
            pm.update(min=0,description='HOME_BUILDER_PROP')

        if type == 'COMBOBOX':
            obj[name] = value
            cb_list = []
            for item in combobox_items:
                tup_item = (item,item,item)
                cb_list.append(tup_item)
            pm = obj.id_properties_ui(name)
            pm.update(description='HOME_BUILDER_PROP',items=cb_list)    

    def add_calculator(self,calculator_name,calculator_object):
        calculator = self.calculators.add()
        calculator.distance_obj = calculator_object
        calculator.name = calculator_name
        return calculator

    def driver_prop(self, prop_name, expression, variables=[]):
        """Add driver to Blender Property
        
        Args:
            prop_name: Name of the property
            expression: Expression to set
            variables: Variables to use in the expression
            
        """

        driver = self.id_data.driver_add(f'["{prop_name}"]')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def var_prop(self, prop_name, name):
        """Get a variable from a property"""
        return Variable(self.id_data,'["' + prop_name + '"]',name)

    @classmethod
    def register(cls):
        bpy.types.Object.home_builder = PointerProperty(
            name="PyCab Props",
            description="PyCab Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.home_builder    



def get_molding_categories(self, context):
    """Get molding categories for enum dropdown."""
    import os
    addon_path = os.path.dirname(os.path.dirname(__file__))
    # Correct path to moldings folder
    moldings_path = os.path.join(os.path.dirname(__file__), "product_libraries", "frameless", "frameless_assets", "moldings")
    
    categories = []
    if os.path.exists(moldings_path):
        for folder in sorted(os.listdir(moldings_path)):
            folder_path = os.path.join(moldings_path, folder)
            if os.path.isdir(folder_path):
                categories.append((folder, folder, folder))
    
    return categories if categories else [('NONE', "No Categories", "")]


def get_molding_items(self, context):
    """Get molding items in the selected category for enum dropdown."""
    import os
    moldings_path = os.path.join(os.path.dirname(__file__), "product_libraries", "frameless", "frameless_assets", "moldings")
    
    category = self.molding_category if hasattr(self, 'molding_category') else ''
    if not category or category == 'NONE':
        return [('NONE', "Select Category First", "")]
    
    category_path = os.path.join(moldings_path, category)
    items = []
    
    if os.path.exists(category_path):
        for f in sorted(os.listdir(category_path)):
            if f.endswith('.blend'):
                name = os.path.splitext(f)[0]
                items.append((name, name, name))
    
    return items if items else [('NONE', "No Moldings", "")]


class Home_Builder_Scene_Props(PropertyGroup):
    main_tab: EnumProperty(name="Library Tabs",
                          items=[('ROOM',"Room","Show the Room Library"),
                                 ('PRODUCTS',"Product","Show the Products Library")],
                          default='ROOM',
                          update=update_main_tab)# type: ignore 

    product_tab: EnumProperty(name="Product Tab",
                          items=[('FRAMELESS',"Frameless","Show the Frameless Library"),
                                 ('FACE FRAME',"Face Frame","Show the Face Frame Library"),
                                 ('CLOSET',"Closet","Show the Closet Library")],
                          default='FRAMELESS',
                          update=update_product_tab)# type: ignore 

    room_name: StringProperty(name="Room Name", default="")
    room_type: StringProperty(name="Room Type", default="")

    wall_type: EnumProperty(name="Wall Type",
                          items=[('Exterior',"Exterior","Exterior Wall"),
                                 ('Interior',"Interior","Interior Wall"),
                                 ('Half',"Half","Half Wall"),
                                 ('Fake',"Fake","Fake Wall")],
                          default='Exterior')# type: ignore  

    ceiling_height: FloatProperty(name="Ceiling Height", default=inch(96),subtype='DISTANCE',precision=5)
    half_wall_height: FloatProperty(name="Half Wall Height", default=inch(34),subtype='DISTANCE',precision=5)
    fake_wall_height: FloatProperty(name="Fake Wall Height", default=inch(34),subtype='DISTANCE',precision=5)
    wall_thickness: FloatProperty(name="Wall Thickness", default=inch(4.5),subtype='DISTANCE',precision=5)

    door_single_width: FloatProperty(name="Door Single Width", default=inch(36),subtype='DISTANCE',precision=5)
    door_double_width: FloatProperty(name="Door Double Width", default=inch(72),subtype='DISTANCE',precision=5)
    door_height: FloatProperty(name="Door Height", default=inch(84),subtype='DISTANCE',precision=5)
    window_width: FloatProperty(name="Window Width", default=inch(34),subtype='DISTANCE',precision=5)
    window_height: FloatProperty(name="Window Height", default=inch(34),subtype='DISTANCE',precision=5)
    window_height_from_floor: FloatProperty(name="Window Height From Floor", default=inch(36),subtype='DISTANCE',precision=5)

    wall_material: PointerProperty(name="Wall Material", type=bpy.types.Material)# type: ignore

    show_entry_doors_and_windows: BoolProperty(name="Show Entry Doors and Windows", default=False)
    show_obstacles: BoolProperty(name="Show Obstacles", default=False)
    show_decorations: BoolProperty(name="Show Decorations", default=False)
    show_materials: BoolProperty(name="Show Materials", default=False)
    show_room_settings: BoolProperty(name="Show Room Settings", default=False)
    show_link_objects_from_rooms: BoolProperty(name="Show Link Objects From Rooms", default=False)

    show_entry_door_and_window_cages: BoolProperty(name="Show Entry Door and Window Cages", default=True,update=update_show_entry_door_and_window_cages)

    # Molding library selection
    molding_category: EnumProperty(
        name="Molding Category",
        description="Select molding category",
        items=get_molding_categories
    )# type: ignore
    
    molding_selection: EnumProperty(
        name="Molding",
        description="Select molding profile",
        items=get_molding_items
    )# type: ignore


    # ==========================================================================
    # ANNOTATION PROPERTIES
    # ==========================================================================
    
    # Line properties
    annotation_line_thickness: FloatProperty(
        name="Line Thickness",
        description="Thickness of annotation lines",
        default=inch(.05),
        min=0.0005,
        max=0.02,
        precision=4,
        unit='LENGTH',
        update=update_line_thickness
    )# type: ignore
    
    annotation_line_color: FloatVectorProperty(
        name="Line Color",
        description="Color for annotation lines",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        update=update_line_color
    )# type: ignore
    
    # Text properties
    annotation_font: PointerProperty(
        name="Font",
        description="Font for text annotations",
        type=bpy.types.VectorFont,
        update=update_font
    )# type: ignore
    
    annotation_text_size: FloatProperty(
        name="Text Size",
        description="Size of text annotations",
        default=0.05,
        min=0.001,
        max=0.5,
        precision=4,
        unit='LENGTH',
        update=update_text_size
    )# type: ignore
    
    annotation_text_color: FloatVectorProperty(
        name="Text Color",
        description="Color for text annotations",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        update=update_text_color
    )# type: ignore
    
    # Dimension properties
    annotation_dimension_text_size: FloatProperty(
        name="Dimension Text Size",
        description="Size of dimension text",
        default=inch(2),
        min=0.001,
        max=0.5,
        precision=4,
        unit='LENGTH',
        update=update_dimension_text_size
    )# type: ignore
    
    annotation_dimension_tick_length: FloatProperty(
        name="Tick Length",
        description="Size of dimension ticks",
        default=inch(1),
        min=0.001,
        max=0.1,
        precision=4,
        unit='LENGTH',
        update=update_dimension_tick_length
    )# type: ignore
    
    annotation_dimension_line_thickness: FloatProperty(
        name="Dimension Line Thickness",
        description="Thickness of dimension lines",
        default=inch(.05),
        min=0.0001,
        max=0.01,
        precision=4,
        unit='LENGTH',
        update=update_dimension_line_thickness
    )# type: ignore

    annotation_dimension_tick_thickness: FloatProperty(
        name="Dimension Tick Thickness",
        description="Thickness of dimension ticks",
        default=inch(.05),
        min=0.0001,
        max=0.01,
        precision=4,
        unit='LENGTH',
        update=update_dimension_line_thickness
    )# type: ignore

    annotation_dimension_extend_line: FloatProperty(
        name="Extend Line",
        description="Size of dimension extend line",
        default=inch(1),
        min=0.001,
        max=0.1,
        precision=4,
        unit='LENGTH',
        update=update_dimension_tick_length
    )# type: ignore

    @classmethod
    def register(cls):
        bpy.types.Scene.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.home_builder    

class Home_Builder_Window_Manager_Props(PropertyGroup):

    progress: FloatProperty(name="Progress",default=1.0)# type: ignore  

    def get_user_preferences(self,context):
        preferences = context.preferences
        add_on_prefs = preferences.addons[os.path.basename(os.path.dirname(__file__))].preferences
        return add_on_prefs

    @classmethod
    def register(cls):
        bpy.types.WindowManager.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.home_builder   

classes = (
    Calculator_Prompt,
    Calculator,
    Home_Builder_Object_Props,
    Home_Builder_Scene_Props,
    Home_Builder_Window_Manager_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)                     