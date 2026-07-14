import bpy
import os
import math
from typing import Optional, Any
from . import units
from . import hb_utils

geometry_nodes_path = os.path.join(os.path.dirname(__file__),'geometry_nodes')
cabinet_part_modifiers_path = os.path.join(geometry_nodes_path,'CabinetPartModifiers')


# Cache of resolved input identifiers per geometry node group.
# Layout: { id(node_group): { input_name: identifier } }
#
# interface_update() syncs the modifier's input slots with the node group's
# interface and is what turns property writes into actual evaluation.
# Once we've called it for a given node group, the identifier for each
# input is stable for the group's lifetime, so subsequent writes can skip
# the call. interface_update is the dominant cost in set_input
# (~0.45ms/call); pure value writes are ~2000x faster.
_INPUT_IDENT_CACHE = {}


def _get_input_identifier(node_group, input_name):
    """Return the modifier-side identifier for input_name, caching across calls.

    On cache miss, runs interface_update so the modifier picks up the input
    and a stable identifier can be captured. Subsequent hits skip the call.
    """
    group_cache = _INPUT_IDENT_CACHE.get(id(node_group))
    if group_cache is not None:
        ident = group_cache.get(input_name)
        if ident is not None:
            return ident
    else:
        group_cache = {}
        _INPUT_IDENT_CACHE[id(node_group)] = group_cache

    if input_name not in node_group.interface.items_tree:
        raise ValueError(f"Input '{input_name}' not found in geometry node")

    node_group.interface_update(bpy.context)
    ident = node_group.interface.items_tree[input_name].identifier
    group_cache[input_name] = ident
    return ident


def _invalidate_input_cache(node_group):
    """Drop cached identifiers for a node group (used on schema mismatch)."""
    _INPUT_IDENT_CACHE.pop(id(node_group), None)


def _gn_input_data_path(mod, identifier):
    """Animatable data path for a geometry node modifier input value.

    Blender 5.2 moved modifier inputs from ID properties
    (modifiers["X"]["Socket_2"]) to RNA (modifiers["X"].properties.inputs.Socket_2.value).
    """
    return 'modifiers["' + mod.name + '"].properties.inputs.' + identifier + '.value'


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

    def draw_prop(self, layout, prop_name, text=None):
        """Draw a custom property in the UI if it exists on the object.
        
        Args:
            layout: The Blender UI layout to draw into
            prop_name: Name of the custom property
            text: Display label. None uses prop_name, "" hides label.
        """
        if prop_name in self.obj:
            display_text = prop_name if text is None else text
            layout.prop(self.obj, '["' + prop_name + '"]', text=display_text)

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
        data_path = _gn_input_data_path(mod, node_input.identifier)
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
        driver = self.obj.driver_add(_gn_input_data_path(mod, node_input.identifier))
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
        input_props = getattr(mod.properties.inputs, node_input.identifier)
        if icon == '':
            layout.prop(input_props,'value',text=text)
        else:
            layout.prop(input_props,'value',text=text,icon=icon)

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

        ident = _get_input_identifier(mod.node_group, input_name)
        try:
            getattr(mod.properties.inputs, ident).value = value
        except AttributeError:
            # Cached identifier no longer present on the modifier - schema
            # changed since we cached. Force a fresh interface_update and retry.
            _invalidate_input_cache(mod.node_group)
            ident = _get_input_identifier(mod.node_group, input_name)
            getattr(mod.properties.inputs, ident).value = value
        # Writing a modifier input via Python doesn't reliably tag the owning
        # object for depsgraph re-evaluation - interface_update used to do that
        # as a side effect. update_tag() is ~40x cheaper and restores live
        # geometry updates after a value change.
        self.obj.update_tag()

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

        ident = _get_input_identifier(mod.node_group, input_name)
        try:
            return getattr(mod.properties.inputs, ident).value
        except AttributeError:
            _invalidate_input_cache(mod.node_group)
            ident = _get_input_identifier(mod.node_group, input_name)
            return getattr(mod.properties.inputs, ident).value

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

    def has_modifier(self):
        """Check if this object still has its geometry node modifier.

        Returns False if the modifier has been applied (baked to mesh) or is
        otherwise missing. Callers that want to set_input/get_input on a wall
        or cabinet should guard with this so applied/static objects are
        skipped cleanly instead of raising.

        Returns:
            True if the tracked geometry node modifier exists, False otherwise.
        """
        if self.obj is None:
            return False
        if not hasattr(self.obj, 'home_builder') or not self.obj.home_builder.mod_name:
            return False
        mod = self.obj.modifiers.get(self.obj.home_builder.mod_name)
        if not mod or not mod.node_group:
            return False
        return True


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

    def get_connected_wall(self, direction='left', include_loop_seam=False):
        """
        Get the wall connected to this wall on the left or right side.
        
        Args:
            direction: 'left' for wall at start point, 'right' for wall at end point
            include_loop_seam: also find the neighbor across a closed
                room's closure seam. The COPY_LOCATION constraint chain is
                directional and never crosses the seam (the first-drawn
                anchor wall carries no constraint to the last-drawn wall),
                so the constraint walk reports None there even though the
                walls genuinely meet. Corner-aware placement wants the true
                geometric neighbor; chain WALKERS should leave this off or
                a closed loop never terminates.
            
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
        if include_loop_seam:
            return self._geometric_neighbor(direction)
        return None

    def _geometric_neighbor(self, direction='left'):
        """Neighboring wall by endpoint coincidence - the same
        end-to-start rule wall-chain detection uses (0.01 m tolerance,
        world XY). Closes the constraint chain's closure-seam blind spot;
        also bridges rooms that merely share a corner point, which is the
        right answer for corner-aware placement."""
        tol = 0.01

        def endpoints(obj, length):
            t = obj.matrix_world.translation
            rot = obj.matrix_world.to_euler().z
            return (t.x, t.y,
                    t.x + math.cos(rot) * length,
                    t.y + math.sin(rot) * length)

        try:
            sx, sy, ex, ey = endpoints(self.obj, self.get_input('Length'))
        except Exception:
            return None
        for obj in bpy.data.objects:
            if 'IS_WALL_BP' not in obj or obj == self.obj:
                continue
            other = GeoNodeWall(obj)
            if not other.has_modifier():
                continue
            try:
                osx, osy, oex, oey = endpoints(obj, other.get_input('Length'))
            except Exception:
                continue
            if direction == 'left':
                # Their end at our start
                if math.hypot(oex - sx, oey - sy) < tol:
                    return other
            else:
                # Their start at our end
                if math.hypot(osx - ex, osy - ey) < tol:
                    return other
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


def ensure_dimension_text_offset_basis(ng):
    """Rewire GeoNodeDimension's text offsets to span the page plane for
    ANY dim orientation. Idempotent versioning fixup for the node group
    shipped in GeoNodeDimension.blend (and embedded in existing files).

    As authored, 'Offset Text X Amount' translated the text in its
    READING frame (Combine XYZ.013 -> Transform) -- which stays screen-
    horizontal -- and 'Offset Text Amount' offsets along the curve
    NORMAL. On a vertical dimension both act horizontally (the normal of
    a vertical line is horizontal), so no input combination could move
    the text up/down. Fix: apply the X amount along the curve TANGENT at
    the text anchor instead (rotate (x,0,0) by the existing tangent
    alignment and add it to the anchor offset after Switch.002).
    Horizontal dims are unchanged (tangent == old reading direction);
    vertical dims gain X = along the line, Y = off the line.

    Called at dimension creation and from the Move Text modal so files
    saved before the fix heal on first use. Silently leaves unexpected
    topologies alone.
    """
    if ng is None or ng.nodes.get('Text X Tangent Rotate'):
        return
    cx = ng.nodes.get('Combine XYZ.013')
    xform = ng.nodes.get('Transform')
    align_t = ng.nodes.get('Align Rotation to Vector.003')
    sw2 = ng.nodes.get('Switch.002')
    sp4 = ng.nodes.get('Set Position.004')
    template = ng.nodes.get('Vector Rotate.001')
    if not all((cx, xform, align_t, sw2, sp4, template)):
        return
    # 1) Disconnect the reading-frame translate; zero the stale value.
    for link in list(cx.outputs[0].links):
        if link.to_node == xform:
            ng.links.remove(link)
    xform.inputs['Translation'].default_value = (0.0, 0.0, 0.0)
    # 2) Rotate (x, 0, 0) into the curve-tangent frame (same rotation
    #    source the perpendicular path aligns against).
    rot = ng.nodes.new(template.bl_idname)
    rot.name = 'Text X Tangent Rotate'
    rot.label = 'Text X Tangent Rotate'
    rot.rotation_type = template.rotation_type
    rot.location = (sw2.location.x, sw2.location.y - 220)
    ng.links.new(cx.outputs['Vector'], rot.inputs['Vector'])
    ng.links.new(align_t.outputs['Rotation'], rot.inputs['Rotation'])
    # 3) Sum with the switched perpendicular offset -> text anchor.
    add = ng.nodes.new('ShaderNodeVectorMath')
    add.name = 'Text Offset Add'
    add.label = 'Text Offset Add'
    add.operation = 'ADD'
    add.location = (sw2.location.x + 180, sw2.location.y - 110)
    for link in list(sw2.outputs['Output'].links):
        if link.to_node == sp4:
            ng.links.remove(link)
    ng.links.new(sw2.outputs['Output'], add.inputs[0])
    ng.links.new(rot.outputs['Vector'], add.inputs[1])
    ng.links.new(add.outputs['Vector'], sp4.inputs['Offset'])


class GeoNodeDimension(GeoNodeObject):

    @staticmethod
    def get_unit_type():
        """Get the Unit Type value based on Blender's unit settings.
        
        Returns:
            int: 0=inches, 1=feet, 2=millimeters, 3=centimeters, 4=meters
        """
        unit_settings = bpy.context.scene.unit_settings
        if unit_settings.system == 'METRIC':
            length_unit = unit_settings.length_unit
            if length_unit == 'MILLIMETERS':
                return 2
            elif length_unit == 'CENTIMETERS':
                return 3
            elif length_unit == 'METERS':
                return 4
            else:
                return 3  # Default metric to centimeters
        else:
            # IMPERIAL or NONE
            return 0  # Default to inches

    def create(self,name):
        props = bpy.context.scene.home_builder

        super().create_curve('GeoNodeDimension',name)
        # Versioning fixup: text offsets must span the page plane for
        # vertical dims too (no-op once patched; see the function docs).
        ensure_dimension_text_offset_basis(
            bpy.data.node_groups.get('GeoNodeDimension'))
        self.obj['IS_2D_ANNOTATION'] = True
        self.obj['IS_DIMENSION'] = True  
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_dimension_commands'  # right-click commands (ui/menus.py)
        self.set_input("Tick Length",props.annotation_dimension_tick_length)
        self.set_input("Tick Thickness",props.annotation_dimension_tick_thickness)
        self.set_input("Line Thickness",props.annotation_dimension_line_thickness)
        self.set_input("Extend Line",props.annotation_dimension_extend_line)
        self.set_input("Text Size",props.annotation_dimension_text_size)
        self.set_input("Unit Type", self.get_unit_type())

    def set_decimal(self, fine=False):
        """Calculate and set appropriate decimal precision for the dimension.
        
        Handles floating point precision issues by:
        1. Converting to display units based on unit type
        2. Snapping to the actual grid increment to clean floating point noise
        3. Stripping trailing zeros to show only meaningful decimals
        
        Args:
            fine: If True, use higher precision for fine snap increments
                  (e.g. 1/16" = 4 decimal places for inches)
        """
        p1 = self.obj.data.splines[0].points[0].co
        p2 = self.obj.data.splines[0].points[1].co 

        dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)   
        dist = math.fabs(dist)
        
        unit_type = self.get_unit_type()
        
        if unit_type == 0:  # inches
            display_value = units.meter_to_inch(dist)
            # Snap to actual increment to remove floating point noise
            snap_inc = 1/16 if fine else 1.0
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 4 if fine else 2
        elif unit_type == 1:  # feet
            display_value = units.meter_to_inch(dist) / 12
            snap_inc = (1/16) / 12 if fine else 1/12
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 4 if fine else 2
        elif unit_type == 2:  # millimeters
            display_value = dist * 1000
            snap_inc = 1.0 if fine else 10.0
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 2 if fine else 1
        elif unit_type == 3:  # centimeters
            display_value = dist * 100
            snap_inc = 0.1 if fine else 1.0
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 3 if fine else 2
        elif unit_type == 4:  # meters
            display_value = dist
            snap_inc = 0.001 if fine else 0.01
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 4 if fine else 3
        else:
            display_value = units.meter_to_inch(dist)
            snap_inc = 1/16 if fine else 1.0
            display_value = round(display_value / snap_inc) * snap_inc
            precision = 4 if fine else 2
        
        rounded = round(display_value, precision)
        
        # Check if it's effectively a whole number
        if abs(rounded - round(rounded)) < 0.001:
            self.set_input("Decimals", 0)
            return
        
        # Convert to string and strip trailing zeros
        text = f"{rounded:.{precision}f}".rstrip('0').rstrip('.')
        
        if '.' not in text:
            self.set_input("Decimals", 0)
        else:
            decimal_part = text.split('.')[1]
            self.set_input("Decimals", len(decimal_part))


class GeoNodeArrow(GeoNodeObject):
    """A 2D leader/pointer arrow annotation.

    Wraps the GeoNodeArrow geometry-node group (geometry_nodes/
    GeoNodeArrow.blend): a straight line with an optional arrowhead at
    the tip, used to point at a feature on a 2D drawing (e.g. a reveal
    or overlay callout on a shop detail). Unlike GeoNodeDimension this
    carries no measured text -- it's purely a pointer.

    The underlying curve is a 2-point POLY spline. The arrowhead is
    instanced on the FIRST control point (the node group selects
    spline index 0), so point[0] is the arrowHEAD/tip and point[1] is
    the plain tail. Set the spline points to aim the arrow:

        arrow = GeoNodeArrow()
        arrow.create("Reveal Arrow")
        arrow.obj.data.splines[0].points[0].co = (0, 0, 0, 0)      # tip (head)
        arrow.obj.data.splines[0].points[1].co = (0.05, 0, 0, 0)   # tail

    Node group inputs: Arrow Height, Arrow Length, Line Thickness,
    Material, Show Arrow. (No text/unit inputs -- see GeoNodeDimension
    for measured annotations.)
    """

    def create(self, name):
        props = bpy.context.scene.home_builder

        super().create_curve('GeoNodeArrow', name)
        self.obj['IS_2D_ANNOTATION'] = True

        # Line thickness shares the dimension-line setting so arrows and
        # dims read as the same annotation weight.
        self.set_input("Line Thickness", props.annotation_dimension_line_thickness)
        # The node group ships zero-size arrowheads; seed sensible
        # defaults (matches the residential 2d-detail arrow style).
        # There's no scene prop for arrowhead size, so use fixed
        # inch-based values the caller can override per-use.
        self.set_input("Arrow Height", units.inch(0.25))
        self.set_input("Arrow Length", units.inch(0.5))
        self.set_input("Show Arrow", True)


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
        driver = self.obj.driver_add(_gn_input_data_path(self.mod, node_input.identifier))
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

        ident = _get_input_identifier(self.mod.node_group, input_name)
        try:
            getattr(self.mod.properties.inputs, ident).value = value
        except AttributeError:
            _invalidate_input_cache(self.mod.node_group)
            ident = _get_input_identifier(self.mod.node_group, input_name)
            getattr(self.mod.properties.inputs, ident).value = value
        # See note in GeoNodeObject.set_input - the explicit tag replaces the
        # implicit dirty-flag that interface_update used to provide.
        self.obj.update_tag()

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

        ident = _get_input_identifier(self.mod.node_group, input_name)
        try:
            return getattr(self.mod.properties.inputs, ident).value
        except AttributeError:
            _invalidate_input_cache(self.mod.node_group)
            ident = _get_input_identifier(self.mod.node_group, input_name)
            return getattr(self.mod.properties.inputs, ident).value