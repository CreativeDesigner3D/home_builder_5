import bpy
import os
import math
from typing import Optional, Any
from . import units
from . import hb_utils

geometry_nodes_path = os.path.join(os.path.dirname(__file__),'geometry_nodes')
cabinet_part_modifiers_path = os.path.join(geometry_nodes_path,'CabinetPartModifiers')

class Variable():

    obj = None
    data_path = ""
    name = ""

    def __init__(self,obj,data_path,name):
        self.obj = obj
        self.data_path = data_path
        self.name = name


class GeoNodeObject:

    obj = None

    def __init__(self,obj: Optional[bpy.types.Object] = None):
        if obj:
            self.obj = obj

    def create(self,geo_node_name, name):
        """Load a geometry node group and create an object with it"""
        if geo_node_name not in bpy.data.node_groups:
            file_path = os.path.join(geometry_nodes_path, geo_node_name + '.blend')
            with bpy.data.libraries.load(file_path) as (data_from, data_to):
                data_to.node_groups = [geo_node_name]
        
        geo_node_group = bpy.data.node_groups[geo_node_name]
        mesh = bpy.data.meshes.new(name)
        self.obj = bpy.data.objects.new(name, mesh)
        
        # Add geometry nodes modifier
        mod = self.obj.modifiers.new(name=geo_node_name, type='NODES')
        mod.node_group = geo_node_group
        
        # Add custom properties to the object
        self.obj.home_builder.mod_name = mod.name
        # Link object to scene collection
        bpy.context.scene.collection.objects.link(self.obj)

    def create_curve(self,geo_node_name, name):
        hb_props = bpy.context.window_manager.home_builder
        add_on_prefs = hb_props.get_user_preferences(bpy.context)           
        """Load a geometry node group and create an object with it"""
        if geo_node_name not in bpy.data.node_groups:
            file_path = os.path.join(geometry_nodes_path, geo_node_name + '.blend')
            with bpy.data.libraries.load(file_path) as (data_from, data_to):
                data_to.node_groups = [geo_node_name]
        
        geo_node_group = bpy.data.node_groups[geo_node_name]
        curve = bpy.data.curves.new('Dimension','CURVE')
        spline = curve.splines.new('POLY')
        spline.points.add(1)
        self.obj = bpy.data.objects.new('Dimension',curve)
        
        # Add geometry nodes modifier
        mod = self.obj.modifiers.new(name=geo_node_name, type='NODES')
        mod.node_group = geo_node_group
        
        # Add custom properties to the object
        self.obj.home_builder.mod_name = mod.name
        self.obj.color = add_on_prefs.annotation_color
        # Link object to scene collection
        bpy.context.scene.collection.objects.link(self.obj)

    def add_empty(self,obj_name):
        obj = bpy.data.objects.new(obj_name,None)
        obj.empty_display_size = 0
        obj.parent = self.obj
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def add_property(self,name,type,value,combobox_items=[]):
        self.obj.home_builder.add_property(name,type,value,combobox_items)

    def set_property(self, prop_name, value):
        """Set a property value.
        
        Args:
            prop_name: Name of the property
            value: Value to set
        """
        self.obj[prop_name] = value

    def get_property(self, prop_name, default=None):
        """Get a property value.
        
        Args:
            prop_name: Name of the property
            default: Default value if property doesn't exist
            
        Returns:
            The property value or default
        """
        return self.obj.get(prop_name, default)

    def var_prop(self, prop_name, name):
        """Get a variable from a property"""
        return Variable(self.obj,'["' + prop_name + '"]',name)

    def var_input(self, input_name, name):
        """Safely set geometry node input value
        
        Args:
            input_name: Name of the input parameter
            Name: Name of the variable
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            raise ValueError("Object does not have geometry node modifier")
        
        try:
            mod = self.obj.modifiers[self.obj.home_builder.mod_name]
        except KeyError:
            raise ValueError(f"Modifier '{self.obj.home_builder.mod_name}' not found on object")
        
        if not mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = mod.node_group.interface.items_tree[input_name] 
        data_path = 'modifiers["' + mod.name + '"]["' + node_input.identifier + '"]'    
        return Variable(self.obj.id_data,data_path,name)

    def var_location(self,name,axis):
        data_path = 'location.' + axis
        return Variable(self.obj.id_data,data_path,name)

    def var_rotation(self,name,axis):
        data_path = 'rotation_euler.' + axis
        return Variable(self.obj.id_data,data_path,name)

    def var_hide(self,name):
        data_path = 'hide_viewport'
        return Variable(self.obj.id_data,data_path,name)

    def driver_location(self,axis,expression,variables=[]):
        if axis == 'x':
            index = 0
        elif axis == 'y':
            index = 1
        elif axis == 'z':
            index = 2

        driver = self.obj.driver_add('location',index)
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def driver_rotation(self,axis,expression,variables=[]):
        if axis == 'x':
            index = 0
        elif axis == 'y':
            index = 1
        elif axis == 'z':
            index = 2

        driver = self.obj.driver_add('rotation_euler',index)
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def driver_hide(self,expression,variables=[]):
        driver = self.obj.driver_add('hide_viewport')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression
        driver = self.obj.driver_add('hide_render')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def driver_input(self, input_name, expression, variables=[]):
        """Safely add driver to input
        
        Args:
            obj: Blender object with geometry node modifier
            input_name: Name of the input parameter
            value: Value to set
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            raise ValueError("Object does not have geometry node modifier")
        
        try:
            mod = self.obj.modifiers[self.obj.home_builder.mod_name]
        except KeyError:
            raise ValueError(f"Modifier '{self.obj.home_builder.mod_name}' not found on object")
        
        if not mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in mod.node_group.interface.items_tree:
            print("MOD",mod)
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = mod.node_group.interface.items_tree[input_name]
        driver = self.obj.driver_add('modifiers["' + mod.name + '"]["' + node_input.identifier + '"]')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def driver_prop(self, prop_name, expression, variables=[]):
        """Add driver to Blender Property
        
        Args:
            prop_name: Name of the property
            expression: Expression to set
            variables: Variables to use in the expression
            
        """

        driver = self.obj.driver_add(f'["{prop_name}"]')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def draw_input(self, layout, input_name, text, icon=''):
        """Safely draw a geometry node input value
        
        Args:
            layout: Layout to draw the input value
            name: Name of the input parameter
            text: Text to display
            icon: Icon to display
            input_name: Name of the input parameter
            value: Value to set
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            raise ValueError("Object does not have geometry node modifier")
        
        try:
            mod = self.obj.modifiers[self.obj.home_builder.mod_name]
        except KeyError:
            raise ValueError(f"Modifier '{self.obj.home_builder.mod_name}' not found on object")
        
        if not mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = mod.node_group.interface.items_tree[input_name]
        if icon == '':
            layout.prop(mod,'["' + node_input.identifier + '"]',text=text)
        else:
            layout.prop(mod,'["' + node_input.identifier + '"]',text=text,icon=icon)

    def set_input(self, input_name, value):
        """Safely set geometry node input value
        
        Args:
            obj: Blender object with geometry node modifier
            input_name: Name of the input parameter
            value: Value to set
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            raise ValueError("Object does not have geometry node modifier")
        
        try:
            mod = self.obj.modifiers[self.obj.home_builder.mod_name]
        except KeyError:
            raise ValueError(f"Modifier '{self.obj.home_builder.mod_name}' not found on object")
        
        if not mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = mod.node_group.interface.items_tree[input_name]
        # If interface_update is not called, the input will change but not update the model
        mod.node_group.interface_update(bpy.context)
        mod[node_input.identifier] = value

    def get_input(self,input_name):
        """Safely get geometry node input value
        
        Args:
            obj: Blender object with geometry node modifier
            input_name: Name of the input parameter
            value: Value to set
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            raise ValueError("Object does not have geometry node modifier")
        
        try:
            mod = self.obj.modifiers[self.obj.home_builder.mod_name]
        except KeyError:
            raise ValueError(f"Modifier '{self.obj.home_builder.mod_name}' not found on object")
        
        if not mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")

        node_input = mod.node_group.interface.items_tree[input_name]
        return mod[node_input.identifier]

    def has_input(self, input_name):
        """Check if a geometry node input exists.
        
        Args:
            input_name: Name of the input parameter to check
            
        Returns:
            True if the input exists, False otherwise
        """
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            return False
        
        mod = self.obj.modifiers.get(self.obj.home_builder.mod_name)
        if not mod or not mod.node_group:
            return False
        
        return input_name in mod.node_group.interface.items_tree


class GeoNodeWall(GeoNodeObject):

    obj_x = None

    def __init__(self,obj=None):
        super().__init__(obj)
        if obj:
            self.obj = obj
            for child in obj.children:
                if child.get('obj_x'):
                    self.obj_x = child
                    break

    def create(self,name):
        super().create('GeoNodeWall',name)
        hb_props = bpy.context.window_manager.home_builder
        add_on_prefs = hb_props.get_user_preferences(bpy.context)        
        self.obj['IS_WALL_BP'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_wall_commands'
        self.obj.color = add_on_prefs.wall_color

        length = self.var_input('Length', 'length')

        #Create a object to store the wall length used for constraints
        self.obj_x = bpy.data.objects.new("obj_x",None)
        self.obj_x.empty_display_size = .01
        self.obj_x.location = (0,0,0)
        self.obj_x.parent = self.obj
        self.obj_x["obj_x"] = True        
        self.obj_x.lock_location = (False,True,True)       
        self.obj_x.lock_rotation = (True,True,True) 
        bpy.context.scene.collection.objects.link(self.obj_x)

        driver = self.obj_x.driver_add('location',0)
        hb_utils.add_driver_variables(driver,[length])
        driver.driver.expression = 'length'

    def assign_materials(self,context):
        if not context.scene.home_builder.wall_material:
            #TODO: GET MATERIAL
            pass
        mat = context.scene.home_builder.wall_material
        self.set_input("Top Surface",mat)
        self.set_input("Bottom Surface",mat)
        self.set_input("Left Surface",mat)
        self.set_input("Right Surface",mat)
        self.set_input("Front Surface",mat)
        self.set_input("Back Surface",mat)

    def connect_to_wall(self,wall):
        constraint = self.obj.constraints.new('COPY_LOCATION')
        constraint.target = wall.obj_x

        wall.obj_x.home_builder.connected_object = self.obj

    def get_connected_wall(self, direction='left'):
        """
        Get the wall connected to this wall on the left or right side.
        
        Args:
            direction: 'left' for wall at start point, 'right' for wall at end point
            
        Returns:
            GeoNodeWall or None
        """
        if direction == 'left':
            # Left connection: this wall has a COPY_LOCATION constraint
            # targeting the obj_x of the previous wall
            for con in self.obj.constraints:
                if con.type == 'COPY_LOCATION':
                    target = con.target
                    if target and target.parent and 'IS_WALL_BP' in target.parent:
                        return GeoNodeWall(target.parent)
        elif direction == 'right':
            # Right connection: find any wall that has a COPY_LOCATION constraint
            # targeting our obj_x
            for obj in bpy.data.objects:
                if 'IS_WALL_BP' in obj and obj != self.obj:
                    for con in obj.constraints:
                        if con.type == 'COPY_LOCATION' and con.target == self.obj_x:
                            return GeoNodeWall(obj)
        return None

class GeoNodeCage(GeoNodeObject):

    def create(self,name):
        super().create('GeoNodeCage',name) 
        self.obj['IS_GEONODE_CAGE'] = True
        self.obj.display.show_shadows = False
        self.obj.display_type = 'WIRE'
        self.obj.color = (0,0,0,1)
        self.obj.visible_camera = False
        self.obj.visible_shadow = False
        self.obj.hide_render = True
        self.obj.hide_probe_volume = False
        self.obj.hide_probe_sphere = False
        self.obj.hide_probe_plane = False


class GeoNodeRectangle(GeoNodeObject):

    def create(self,name):
        super().create('GeoNodeRectangle',name)
        self.obj.color = (0,0,0,1)
        self.set_input("Dim X", 1)
        self.set_input("Dim Y", 1)
        self.set_input("Line Thickness", .001)


class GeoNodeCutpart(GeoNodeObject):

    def create(self,name):
        super().create('GeoNodeCutpart',name)  

    def add_part_modifier(self,token_type,token_name):
        cpm = CabinetPartModifier(self.obj)
        cpm.add_node(token_type,token_name)
        cpm.mod.show_viewport = True
        return cpm


class GeoNode5PieceDoor(GeoNodeObject):  

    def create(self,name):
        super().create('GeoNode5PieceDoor',name)       


class GeoNodeHardware(GeoNodeObject):  

    def create(self,name):
        super().create('GeoNodeHardware',name)  


class GeoNodeDrawerBox(GeoNodeObject):  

    def create(self,name):
        super().create('GeoNodeDrawerBox',name)  
        self.obj['IS_DRAWER_BOX'] = True
        self.set_input("Material Thickness",units.inch(0.5))
        self.set_input("Bottom Thickness",units.inch(0.25))
        self.set_input("Drawer Bottom Z Location",units.inch(0.5))


class GeoNodeDoorSwing(GeoNodeObject):  

    def create(self,name):
        super().create('GeoNodeDoorSwing',name)  
        self.obj['IS_2D_ANNOTATION'] = True
        self.obj.color = (0,0,0,1)
        self.set_input("Door Thickness",units.inch(1.5))


class GeoNodeDimension(GeoNodeObject):  

    def create(self,name):
        props = bpy.context.scene.home_builder

        super().create_curve('GeoNodeDimension',name)
        self.obj['IS_2D_ANNOTATION'] = True  
        self.obj['IS_DIMENSION'] = True  
        self.set_input("Tick Length",props.annotation_dimension_tick_length)
        self.set_input("Tick Thickness",props.annotation_dimension_tick_thickness)
        self.set_input("Line Thickness",props.annotation_dimension_line_thickness)
        self.set_input("Extend Line",props.annotation_dimension_extend_line)
        self.set_input("Text Size",props.annotation_dimension_text_size)

    def set_decimal(self):
        """Calculate and set appropriate decimal precision for the dimension.
        
        Handles floating point precision issues by:
        1. Rounding to 2 decimal places first (practical precision for inches)
        2. Checking if value is very close to a whole number
        3. Stripping trailing zeros to show only meaningful decimals
        """
        p1 = self.obj.data.splines[0].points[0].co
        p2 = self.obj.data.splines[0].points[1].co 

        dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)   
        inch_value = units.meter_to_inch(math.fabs(dist))
        
        # Round to 2 decimal places (practical precision for inches)
        rounded = round(inch_value, 2)
        
        # Check if it's effectively a whole number
        if abs(rounded - round(rounded)) < 0.001:
            self.set_input("Decimals", 0)
            return
        
        # Convert to string and strip trailing zeros
        text = f"{rounded:.2f}".rstrip('0').rstrip('.')
        
        if '.' not in text:
            self.set_input("Decimals", 0)
        else:
            decimal_part = text.split('.')[1]
            self.set_input("Decimals", len(decimal_part))

class CabinetPartModifier(GeoNodeObject):

    mod = None
    # node_group = None

    def get_node(self,token_type):
        token_path = os.path.join(cabinet_part_modifiers_path,token_type + ".blend")

        if token_type in bpy.data.node_groups:
            return bpy.data.node_groups[token_type]

        if os.path.exists(token_path):

            with bpy.data.libraries.load(token_path) as (data_from, data_to):
                for ng in data_from.node_groups:
                    if ng == token_type:
                        data_to.node_groups = [ng]
                        break    
            
            for ng in data_to.node_groups:
                return ng    

    def add_node(self,token_type,token_name):
        node_group = self.get_node(token_type)
        self.mod = self.obj.modifiers.new(name=token_name,type='NODES')
        self.mod.node_group = node_group
        # self.node_group = node_group
        self.mod.show_expanded = False   

    def driver_input(self, input_name, expression, variables=[]):
        """Safely add driver to input
        
        Args:
            input_name: Name of the input parameter
            expression: Expression to set
            variables: Variables to use in the expression
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not self.mod:
            raise ValueError("Cabinet Part Modifier not found")

        if not self.mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in self.mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = self.mod.node_group.interface.items_tree[input_name]
        driver = self.obj.driver_add('modifiers["' + self.mod.name + '"]["' + node_input.identifier + '"]')
        hb_utils.add_driver_variables(driver,variables)
        driver.driver.expression = expression         

    def driver_hide(self, expression, variables=[]):
        """Drive modifier visibility (show_viewport/show_render).
        
        Note: show_viewport=True means visible, so the expression should be
        inverted compared to object hide. Use show_viewport = NOT(hide_expression).
        """
        if not self.mod:
            raise ValueError("Cabinet Part Modifier not found")
        mod_path = 'modifiers["' + self.mod.name + '"].show_viewport'
        driver = self.obj.driver_add(mod_path)
        hb_utils.add_driver_variables(driver, variables)
        driver.driver.expression = expression
        mod_path_render = 'modifiers["' + self.mod.name + '"].show_render'
        driver = self.obj.driver_add(mod_path_render)
        hb_utils.add_driver_variables(driver, variables)
        driver.driver.expression = expression

    def set_input(self, input_name, value):
        """Safely set geometry node input value
        
        Args:
            input_name: Name of the input parameter
            value: Value to set
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not self.mod:
            raise ValueError("Cabinet Part Modifier not found")
        
        if not self.mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in self.mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")
        
        node_input = self.mod.node_group.interface.items_tree[input_name]
        # If interface_update is not called, the input will change but not update the model
        self.mod.node_group.interface_update(bpy.context)
        self.mod[node_input.identifier] = value

    def get_input(self,input_name):
        """Safely get geometry node input value
        
        Args:
            input_name: Name of the input parameter
            
        Raises:
            ValueError: If object doesn't have geometry node modifier or input not found
        """
        if not self.mod:
            raise ValueError("Cabinet Part Modifier not found")
        
        if not self.mod.node_group:
            raise ValueError("Geometry node modifier has no node group")
        
        if input_name not in self.mod.node_group.interface.items_tree:
            raise ValueError(f"Input '{input_name}' not found in geometry node")

        node_input = self.mod.node_group.interface.items_tree[input_name]
        return self.mod[node_input.identifier]        