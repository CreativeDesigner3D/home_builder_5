from typing import Any
import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from . import types_frameless

def get_available_pulls():
    """Get list of available pull .blend files from the cabinet_pulls folder."""
    pulls_folder = os.path.join(os.path.dirname(__file__), 
                                'frameless_assets', 'cabinet_pulls')
    pulls = []
    if os.path.exists(pulls_folder):
        for f in os.listdir(pulls_folder):
            if f.endswith('.blend'):
                name = os.path.splitext(f)[0]
                pulls.append((name, f))
    return pulls

def get_pull_enum_items(self, context):
    """Dynamic enum items for pull selection."""
    items = []
    for name, filename in get_available_pulls():
        # Check for matching thumbnail
        thumb_path = os.path.join(os.path.dirname(__file__), 
                                  'frameless_assets', 'cabinet_pulls', 
                                  name + '.png')
        items.append((filename, name, f"Use {name}", 'OBJECT_DATA', len(items)))
    if not items:
        items.append(('NONE', "No Pulls Found", "No pull files in cabinet_pulls folder"))
    return items

# ============================================
# PULL FINISH DEFINITIONS
# ============================================

PULL_FINISHES = {
    'CHROME': {
        'name': 'Chrome',
        'color': (0.8, 0.8, 0.8, 1.0),
        'metallic': 1.0,
        'roughness': 0.1,
    },
    'BRUSHED_NICKEL': {
        'name': 'Brushed Nickel',
        'color': (0.6, 0.58, 0.55, 1.0),
        'metallic': 1.0,
        'roughness': 0.35,
    },
    'MATTE_BLACK': {
        'name': 'Matte Black',
        'color': (0.02, 0.02, 0.02, 1.0),
        'metallic': 0.9,
        'roughness': 0.5,
    },
    'OIL_RUBBED_BRONZE': {
        'name': 'Oil Rubbed Bronze',
        'color': (0.15, 0.08, 0.05, 1.0),
        'metallic': 0.8,
        'roughness': 0.4,
    },
    'POLISHED_BRASS': {
        'name': 'Polished Brass',
        'color': (0.85, 0.65, 0.2, 1.0),
        'metallic': 1.0,
        'roughness': 0.15,
    },
    'SATIN_BRASS': {
        'name': 'Satin Brass',
        'color': (0.75, 0.6, 0.25, 1.0),
        'metallic': 1.0,
        'roughness': 0.35,
    },
    'ANTIQUE_BRASS': {
        'name': 'Antique Brass',
        'color': (0.5, 0.38, 0.15, 1.0),
        'metallic': 0.85,
        'roughness': 0.45,
    },
    'STAINLESS_STEEL': {
        'name': 'Stainless Steel',
        'color': (0.55, 0.55, 0.55, 1.0),
        'metallic': 1.0,
        'roughness': 0.25,
    },
    'PEWTER': {
        'name': 'Pewter',
        'color': (0.4, 0.4, 0.42, 1.0),
        'metallic': 0.9,
        'roughness': 0.4,
    },
    'COPPER': {
        'name': 'Copper',
        'color': (0.72, 0.45, 0.2, 1.0),
        'metallic': 1.0,
        'roughness': 0.2,
    },
    'MATTE_GOLD': {
        'name': 'Matte Gold',
        'color': (0.83, 0.69, 0.22, 1.0),
        'metallic': 1.0,
        'roughness': 0.4,
    },
    'POLISHED_GOLD': {
        'name': 'Polished Gold',
        'color': (1.0, 0.84, 0.0, 1.0),
        'metallic': 1.0,
        'roughness': 0.1,
    },
}


def get_pull_finish_enum_items(self, context):
    """Generate enum items for pull finish dropdown"""
    items = []
    for key, data in PULL_FINISHES.items():
        items.append((key, data['name'], f"Apply {data['name']} finish to pulls"))
    return items


def get_or_create_pull_finish_material(finish_key):
    """Get or create a material for the specified pull finish"""
    import bpy
    
    if finish_key not in PULL_FINISHES:
        return None
    
    finish_data = PULL_FINISHES[finish_key]
    mat_name = f"Pull Finish - {finish_data['name']}"
    
    # Check if material already exists
    if mat_name in bpy.data.materials:
        return bpy.data.materials[mat_name]
    
    # Create new material
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the Principled BSDF node
    nodes = mat.node_tree.nodes
    principled = nodes.get('Principled BSDF')
    
    if principled:
        principled.inputs['Base Color'].default_value = finish_data['color']
        principled.inputs['Metallic'].default_value = finish_data['metallic']
        principled.inputs['Roughness'].default_value = finish_data['roughness']
    
    return mat


def get_or_create_glass_material():
    """Get or create a glass material for cabinet door panels.
    
    Creates a glass material using Glass BSDF mixed with Transparent BSDF
    for better EEVEE viewport display.
    """

    mat_name = "Cabinet_Door_Panel_Glass"
    
    # Check if material already exists and has correct setup
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
        # Verify it has a Glass BSDF node - if not, delete and recreate
        has_glass_node = False
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_GLASS':
                    has_glass_node = True
                    break
        if has_glass_node:
            return mat
        else:
            # Remove incorrect material
            bpy.data.materials.remove(mat)
    
    # Create new glass material
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Enable transparency settings for EEVEE
    mat.blend_method = 'BLEND'
    mat.use_backface_culling = False
    
    # Get the node tree
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create output node
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Create Mix Shader to blend Glass and Transparent
    mix_shader = nodes.new('ShaderNodeMixShader')
    mix_shader.location = (200, 0)
    mix_shader.inputs['Fac'].default_value = 0.2  # 20% transparent, 80% glass
    
    # Create Glass BSDF
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (0, 100)
    glass.inputs['Color'].default_value = (0.85, 0.92, 0.95, 1.0)  # Slight blue tint
    glass.inputs['Roughness'].default_value = 0.0
    glass.inputs['IOR'].default_value = 1.45
    
    # Create Transparent BSDF
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    transparent.location = (0, -100)
    transparent.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    
    # Connect nodes
    links.new(glass.outputs['BSDF'], mix_shader.inputs[1])
    links.new(transparent.outputs['BSDF'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    return mat


def load_pull_object(pull_filename):
    """Load a pull object from a .blend file."""
    if not pull_filename or pull_filename == 'NONE':
        return None
    
    pulls_folder = os.path.join(os.path.dirname(__file__), 
                                'frameless_assets', 'cabinet_pulls')
    pull_path = os.path.join(pulls_folder, pull_filename)
    
    if not os.path.exists(pull_path):
        return None
    
    with bpy.data.libraries.load(pull_path) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    # Return the first object loaded
    for obj in data_to.objects:
        return obj
    return None


from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from ... import units
from ... import hb_types
from ... import hb_project
from . import wood_materials
import bpy.utils.previews

# Preview collection for library thumbnails
preview_collections = {}

def get_library_previews():
    """Get or create the library preview collection."""
    if "library_previews" not in preview_collections:
        preview_collections["library_previews"] = bpy.utils.previews.new()
    return preview_collections["library_previews"]

def get_cabinet_previews():
    """Get or create the cabinet preview collection for standard thumbnails."""
    if "cabinet_previews" not in preview_collections:
        preview_collections["cabinet_previews"] = bpy.utils.previews.new()
    return preview_collections["cabinet_previews"]

def load_library_thumbnail(filepath, name):
    """Load a thumbnail image into the preview collection."""
    pcoll = get_library_previews()
    
    # Check if already loaded
    if name in pcoll:
        return pcoll[name].icon_id
    
    # Load the thumbnail
    if os.path.exists(filepath):
        thumb = pcoll.load(name, filepath, 'IMAGE')
        return thumb.icon_id
    
    return 0  # Return 0 if no thumbnail

def get_cabinet_thumbnail_path():
    """Get the path to the standard cabinet thumbnails folder."""
    return os.path.join(os.path.dirname(__file__), "frameless_thumbnails")

def load_cabinet_thumbnail(name):
    """Load a standard cabinet thumbnail by name (without extension)."""
    pcoll = get_cabinet_previews()
    
    # Check if already loaded
    if name in pcoll:
        return pcoll[name].icon_id
    
    # Build the filepath
    thumbnails_dir = get_cabinet_thumbnail_path()
    filepath = os.path.join(thumbnails_dir, f"{name}.png")
    
    # Load the thumbnail
    if os.path.exists(filepath):
        thumb = pcoll.load(name, filepath, 'IMAGE')
        return thumb.icon_id
    
    return 0  # Return 0 if no thumbnail

def clear_library_previews():
    """Clear all loaded previews."""
    if "library_previews" in preview_collections:
        pcoll = preview_collections["library_previews"]
        pcoll.clear()

def update_top_cabinet_clearance(self, context):
    from ... import hb_project
    
    # Get ceiling height from main scene
    main_scene = hb_project.get_main_scene()
    hb_props = main_scene.home_builder
    
    # Calculate heights based on clearance settings
    # Tall cabinet: goes from floor to ceiling minus clearance
    self.tall_cabinet_height = hb_props.ceiling_height - self.default_top_cabinet_clearance
    
    # Upper cabinet: fits between wall_cabinet_location and ceiling minus clearance
    self.upper_cabinet_height = hb_props.ceiling_height - self.default_top_cabinet_clearance - self.default_wall_cabinet_location

def update_include_drawer_boxes(self,context):
    if self.include_drawer_boxes:
        # Find all drawer fronts in the scene
        for obj in context.scene.objects:
            if obj.get("IS_DRAWER_FRONT"):
                # Check if drawer box already exists
                found_drawer_box = any(child.get('IS_DRAWER_BOX')for child in obj.children)
                if not found_drawer_box:
                    drawer_front = types_frameless.CabinetDrawerFront(obj)
                    drawer_front.add_drawer_box()
    else:
        # Find and remove all drawer boxes
        drawer_boxes = [obj for obj in context.scene.objects if obj.get('IS_DRAWER_BOX')]
        for db in drawer_boxes:
            bpy.data.objects.remove(db, do_unlink=True)

def update_show_machining(self,context):
    print('UPDATE SHOW MACHINING',self.show_machining)

def update_frameless_selection_mode(self,context):
    bpy.ops.hb_frameless.toggle_mode(search_obj_name="")


# =============================================================================
# CABINET STYLE SYSTEM
# =============================================================================

class Frameless_Cabinet_Style(PropertyGroup):
    """Cabinet style defining wood, finish, interior, and door overlay settings."""
    
    show_expanded: BoolProperty(
        name="Show Expanded",
        description="Show expanded style options",
        default=False
    )  # type: ignore
    
    # Wood/Material selection
    wood_species: EnumProperty(
        name="Wood Species",
        description="Wood species for cabinet exterior",
        items=[
            ('MAPLE', "Maple", "Maple wood"),
            ('OAK', "Oak", "Oak wood"),
            ('CHERRY', "Cherry", "Cherry wood"),
            ('WALNUT', "Walnut", "Walnut wood"),
            ('BIRCH', "Birch", "Birch wood"),
            ('HICKORY', "Hickory", "Hickory wood"),
            ('ALDER', "Alder", "Alder wood"),
            ('PAINT_GRADE', "Paint Grade", "Paint Grade"),
        ],
        default='MAPLE'
    )  # type: ignore
    
    # Finish/Stain
    stain_color: EnumProperty(
        name="Stain Color",
        description="Type of finish applied",
        items=[
            ('White', "White", "White"),
            ('Black', "Black", "Black"),
            ('Blue', "Blue", "Blue"),
            ('Green', "Green", "Green"),
            ('Red', "Red", "Red"),
            ('Yellow', "Yellow", "Yellow"),
            ('Brown', "Brown", "Brown"),
            ('Grey', "Grey", "Grey"),
        ],
        default='White'
    )  # type: ignore
    
    paint_color: EnumProperty(
        name="Paint Color",
        description="Type of finish applied",
        items=[
            ('White', "White", "White"),
            ('Black', "Black", "Black"),
            ('Blue', "Blue", "Blue"),
            ('Green', "Green", "Green"),
            ('Red', "Red", "Red"),
            ('Yellow', "Yellow", "Yellow"),
            ('Brown', "Brown", "Brown"),
            ('Grey', "Grey", "Grey"),
        ],
        default='White'
    )  # type: ignore
    
    # Interior material
    interior_material: EnumProperty(
        name="Interior Material",
        description="Material for cabinet interior",
        items=[
            ('MATCHING', "Matching Exterior", "Same as exterior wood"),
            ('MAPLE_PLY', "Maple Plywood", "Maple veneer plywood"),
            ('BIRCH_PLY', "Birch Plywood", "Birch veneer plywood"),
            ('WHITE_MELAMINE', "White Melamine", "White melamine"),
            ('ALMOND_MELAMINE', "Almond Melamine", "Almond melamine"),
            ('GREY_MELAMINE', "Grey Melamine", "Grey melamine"),
            ('PRE_FINISHED', "Pre-Finished", "Pre-finished interior"),
        ],
        default='MAPLE_PLY'
    )  # type: ignore
    
    # Door overlay
    door_overlay_type: EnumProperty(
        name="Door Overlay",
        description="Door overlay style",
        items=[
            ('FULL', "Full Overlay", "Full overlay - doors cover frame completely"),
            ('HALF', "Half Overlay", "Half overlay - partial frame reveal"),
            ('INSET', "Inset", "Inset - doors sit inside frame"),
        ],
        default='FULL'
    )  # type: ignore
    
    # Additional style options
    edge_banding: EnumProperty(
        name="Edge Banding",
        description="Edge banding type",
        items=[
            ('MATCHING', "Matching Wood", "Matching wood edge banding"),
            ('PVC', "PVC", "PVC edge banding"),
            ('ABS', "ABS", "ABS edge banding"),
            ('NONE', "None", "No edge banding"),
        ],
        default='MATCHING'
    )  # type: ignore

    material: bpy.props.PointerProperty(name="Material",type=bpy.types.Material)# type: ignore
    material_rotated: bpy.props.PointerProperty(name="Material Rotated",type=bpy.types.Material)# type: ignore
    interior_material: bpy.props.PointerProperty(name="Interior Material",type=bpy.types.Material)# type: ignore
    interior_material_rotated: bpy.props.PointerProperty(name="Interior Material Rotated",type=bpy.types.Material)# type: ignore

    def get_finish_material(self):
        if self.material and self.material_rotated:
            wood_materials.update_finish_material(self)
            return self.material,self.material_rotated
        else:
            library_path = os.path.join(os.path.dirname(__file__),'frameless_assets','materials','cabinet_material.blend')
            with bpy.data.libraries.load(library_path) as (data_from, data_to):
                data_to.materials = ["Wood"]  
            
            material = data_to.materials[0]            
            material.name = self.name + " Finish"
            self.material = material
            rotated_mat = material.copy()
            rotated_mat.name = material.name + " ROTATED"
            self.material_rotated = rotated_mat
            wood_materials.update_finish_material(self)
            return self.material,self.material_rotated

    def get_interior_material(self):
        if self.interior_material and self.interior_material_rotated:
            return self.interior_material,self.interior_material_rotated
        else:
            library_path = os.path.join(os.path.dirname(__file__),'frameless_assets','materials','cabinet_material.blend')
            with bpy.data.libraries.load(library_path) as (data_from, data_to):
                data_to.materials = ["Wood"]  
            
            material = data_to.materials[0]            
            material.name = self.name + " Interior"
            self.interior_material = material
            rotated_mat = material.copy()
            rotated_mat.name = material.name + " ROTATED"
            self.interior_material_rotated = rotated_mat
            return self.interior_material,self.interior_material_rotated

    def assign_style_to_cabinet(self, cabinet_obj):
        #Assign Properties to Cabinet done in ops_hb_frameless.py

        #Update all cabinet parts with correct materials
        self.get_finish_material()
        self.get_interior_material()
        for child in cabinet_obj.children_recursive:
            if 'CABINET_PART' in child:
                part = hb_types.GeoNodeObject(child)
                
                # Determine material based on Finish Top/Bottom properties
                finish_top = child.get('Finish Top', False)
                finish_bottom = child.get('Finish Bottom', True)
                
                top_mat = self.material if finish_top else self.interior_material
                bottom_mat = self.material if finish_bottom else self.interior_material
                
                part.set_input("Top Surface", top_mat)
                part.set_input("Bottom Surface", bottom_mat)
                part.set_input("Edge W1", self.material_rotated)
                part.set_input("Edge W2", self.material_rotated)
                part.set_input("Edge L1", self.material_rotated)
                part.set_input("Edge L2", self.material_rotated)
                
                # Also set Material input on any cabinet part modifiers (e.g., CPM_CORNERNOTCH)
                for mod in child.modifiers:
                    if mod.type == 'NODES' and mod.node_group:
                        if 'Material' in mod.node_group.interface.items_tree:
                            node_input = mod.node_group.interface.items_tree['Material']
                            mod[node_input.identifier] = self.material

        #Update cabinet door and drawer front overlays
        for child in cabinet_obj.children_recursive:
            if child.get('IS_FRAMELESS_OPENING_CAGE'):
                # Set Inset Front based on overlay type
                if 'Inset Front' in child:
                    child['Inset Front'] = (self.door_overlay_type == 'INSET')
                
                # Set Half Overlay properties based on overlay type
                # FULL: all half overlays False
                # HALF: all half overlays True (except where adjacent to cabinet edge)
                # INSET: half overlay doesn't matter, but set False for consistency
                is_half = (self.door_overlay_type == 'HALF')
                
                if 'Half Overlay Top' in child:
                    # Only set to half if not already overridden (e.g., stacked cabinets)
                    # Check if this is at the top of the cabinet
                    if not child.get('FORCE_HALF_OVERLAY_TOP', False):
                        child['Half Overlay Top'] = is_half
                        
                if 'Half Overlay Bottom' in child:
                    if not child.get('FORCE_HALF_OVERLAY_BOTTOM', False):
                        child['Half Overlay Bottom'] = is_half
                        
                if 'Half Overlay Left' in child:
                    if not child.get('FORCE_HALF_OVERLAY_LEFT', False):
                        child['Half Overlay Left'] = is_half
                        
                if 'Half Overlay Right' in child:
                    if not child.get('FORCE_HALF_OVERLAY_RIGHT', False):
                        child['Half Overlay Right'] = is_half

    def draw_cabinet_style_ui(self, layout, context):
        box = layout.box()
        box.prop(self, "name", text="Style Name")
        
        # Wood settings
        col = box.column(align=True)
        col.label(text="Wood & Finish:")
        col.prop(self, "wood_species", text="Wood")
        if self.wood_species != 'PAINT_GRADE':
            col.prop(self, "stain_color", text="Stain Color")
        else:
            col.prop(self, "paint_color", text="Paint Color")
        
        # Interior
        col = box.column(align=True)
        col.label(text="Interior:")
        col.prop(self, "interior_material", text="Material")
        
        # Door overlay
        col = box.column(align=True)
        col.label(text="Door Overlay:")
        col.prop(self, "door_overlay_type", text="Type")

        # Edge banding
        col = box.column(align=True)
        col.label(text="Edge Banding:")
        col.prop(self, "edge_banding", text="Type")
        
        # Paint style onto cabinets button
        row = box.row()
        row.scale_y = 1.3
        row.operator("hb_frameless.assign_cabinet_style_to_selected_cabinets", text="Assign Style", icon='BRUSH_DATA')
        
        # Update cabinets button with progress bar
        row = box.row()
        row.scale_y = 1.3
        if context.window_manager.home_builder.progress < 1.0:
            row.progress(
                text=str(int(context.window_manager.home_builder.progress * 100)) + "%",
                factor=context.window_manager.home_builder.progress
            )
        else:
            row.operator("hb_frameless.update_cabinets_from_style", text="Update Cabinets", icon='FILE_REFRESH')        


class HB_UL_cabinet_styles(UIList):
    """UIList for displaying cabinet styles."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon='MATERIAL')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='MATERIAL')


class HB_UL_door_styles(UIList):
    """UIList for displaying door styles."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False)
            # Show door type indicator
            if item.door_type == 'SLAB':
                row.label(text="", icon='MESH_PLANE')
            else:
                row.label(text="", icon='MOD_LATTICE')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='MOD_LATTICE')


class Frameless_Door_Style(PropertyGroup):
    """Door/Drawer Front style defining construction type, dimensions, and materials."""
    
    show_expanded: BoolProperty(
        name="Show Expanded",
        description="Show expanded style options",
        default=False
    )  # type: ignore
    
    # Door construction type
    door_type: EnumProperty(
        name="Door Type",
        description="Door construction type",
        items=[
            ('SLAB', "Slab", "Solid slab door"),
            ('5_PIECE', "5 Piece", "5-piece frame and panel door"),
        ],
        default='SLAB'
    )  # type: ignore
    
    # Panel/Center material
    panel_material: EnumProperty(
        name="Panel Material",
        description="Material for door panel center",
        items=[
            ('MATCH_CABINET', "Match Cabinet", "Match cabinet style material"),
            ('GLASS', "Glass", "Glass panel"),
        ],
        default='MATCH_CABINET'
    )  # type: ignore
    
    # Outside profile object (for routing/edge detail)
    outside_profile: PointerProperty(
        name="Outside Profile",
        type=bpy.types.Object
    )  # type: ignore
    
    # Inside profile object (for frame inner edge)
    inside_profile: PointerProperty(
        name="Inside Profile", 
        type=bpy.types.Object
    )  # type: ignore
    
    # 5 Piece Door Dimensions
    stile_width: FloatProperty(
        name="Stile Width",
        description="Width of left and right stiles",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    rail_width: FloatProperty(
        name="Rail Width",
        description="Width of top and bottom rails",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    # Mid Rail Options
    add_mid_rail: BoolProperty(
        name="Add Mid Rail",
        description="Add a horizontal mid rail",
        default=False
    )  # type: ignore
    
    center_mid_rail: BoolProperty(
        name="Center Mid Rail",
        description="Center the mid rail vertically",
        default=True
    )  # type: ignore
    
    mid_rail_width: FloatProperty(
        name="Mid Rail Width",
        description="Width of the mid rail",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    mid_rail_location: FloatProperty(
        name="Mid Rail Location",
        description="Distance from bottom of door to mid rail (if not centered)",
        default=units.inch(12.0),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    # Panel Options
    panel_thickness: FloatProperty(
        name="Panel Thickness",
        description="Thickness of the center panel",
        default=units.inch(0.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    panel_inset: FloatProperty(
        name="Panel Inset",
        description="How far panel is inset from frame face",
        default=units.inch(0.25),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    # Edge Profile
    edge_profile_type: EnumProperty(
        name="Edge Profile",
        description="Edge profile for slab doors",
        items=[
            ('SQUARE', "Square", "Square edge"),
            ('EASED', "Eased", "Slightly rounded edge"),
            ('OGEE', "Ogee", "Ogee profile"),
            ('BEVEL', "Bevel", "Beveled edge"),
            ('ROUNDOVER', "Roundover", "Rounded edge"),
        ],
        default='SQUARE'
    )  # type: ignore

    def get_parent_cabinet_style(self, front_obj):
        """Find the parent cabinet and return its cabinet style.
        
        Walks up the object hierarchy to find the cabinet cage,
        then returns the cabinet style associated with it.
        """
        from ... import hb_project
        
        # Walk up the hierarchy to find the cabinet
        current = front_obj
        cabinet_obj = None
        while current:
            if current.get('IS_FRAMELESS_CABINET_CAGE'):
                cabinet_obj = current
                break
            current = current.parent
        
        if not cabinet_obj:
            return None
        
        # Get the cabinet style index
        style_index = cabinet_obj.get('CABINET_STYLE_INDEX', 0)
        
        # Get cabinet styles from main scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if style_index < len(props.cabinet_styles):
            return props.cabinet_styles[style_index]
        elif len(props.cabinet_styles) > 0:
            return props.cabinet_styles[0]
        
        return None

    def assign_style_to_front(self, front_obj):
        """Assign this door style to a door or drawer front object.
        
        Returns:
            True if style was applied successfully
            False if style could not be applied (e.g., front too small)
            String with error message if validation failed
        """
        from . import types_frameless
        from ... import hb_types
        
        # Get the front wrapper
        if 'IS_DOOR_FRONT' in front_obj:
            front = types_frameless.CabinetDoor(front_obj)
        elif 'IS_DRAWER_FRONT' in front_obj:
            front = types_frameless.CabinetDrawerFront(front_obj)
        else:
            return False
        
        # Apply style based on door type
        if self.door_type == 'SLAB':
            # Remove any existing door style modifier
            for mod in front_obj.modifiers:
                if mod.type == 'NODES' and 'Door Style' in mod.name:
                    front_obj.modifiers.remove(mod)
        else:
            # For 5-piece doors, validate dimensions first
            # Length = height, Width = width (due to rotation)
            try:
                front_height = front.get_input("Length")
                front_width = front.get_input("Width")
            except:
                return "Could not read front dimensions"
            
            print(f"Front height: {units.meter_to_inch(front_height)}, Front width: {units.meter_to_inch(front_width)}")
            # Calculate minimum dimensions needed
            min_width = self.stile_width * 2 + units.inch(1) # Left + Right stiles
            min_height = self.rail_width * 2 + units.inch(1) # Top + Bottom rails
            
            # Add mid rail height if enabled in style OR if door is tall enough to auto-add
            auto_mid_rail_height = units.inch(45.5)
            if self.add_mid_rail or front_height > auto_mid_rail_height:
                min_height += self.mid_rail_width
            
            # Check if front is large enough
            if front_width < min_width:
                return f"Front too narrow ({front_width:.3f}m) for stile widths ({min_width:.3f}m minimum)"
            
            if front_height < min_height:
                return f"Front too short ({front_height:.3f}m) for rail widths ({min_height:.3f}m minimum)"
            
            # Check if door style modifier already exists
            existing_mod = None
            for mod in front_obj.modifiers:
                if mod.type == 'NODES' and 'Door Style' in mod.name:
                    existing_mod = mod
                    break
            
            if existing_mod:
                # Wrap existing modifier with CabinetPartModifier
                door_style_mod = hb_types.CabinetPartModifier()
                door_style_mod.obj = front_obj
                door_style_mod.mod = existing_mod
            else:
                # Add new modifier
                door_style_mod = front.add_part_modifier('CPM_5PIECEDOOR', 'Door Style')
            
            door_style_mod.set_input("Left Stile Width", self.stile_width)
            door_style_mod.set_input("Right Stile Width", self.stile_width)
            door_style_mod.set_input("Top Rail Width", self.rail_width)
            door_style_mod.set_input("Bottom Rail Width", self.rail_width)
            door_style_mod.set_input("Panel Thickness", self.panel_thickness)
            door_style_mod.set_input("Panel Inset", self.panel_inset)
            
            # Automatically add centered mid rail for doors taller than 45.5"
            auto_mid_rail_height = units.inch(45.5)
            needs_auto_mid_rail = front_height > auto_mid_rail_height
            
            # Mid rail: auto-add for tall doors, or use style setting
            if needs_auto_mid_rail or self.add_mid_rail:
                try:
                    door_style_mod.set_input("Add Mid Rail", True)
                    door_style_mod.set_input("Mid Rail Width", self.mid_rail_width)
                    
                    if needs_auto_mid_rail:
                        # Tall doors always get centered mid rail
                        door_style_mod.set_input("Center Mid Rail", True)
                    else:
                        # Use style settings for shorter doors
                        door_style_mod.set_input("Center Mid Rail", self.center_mid_rail)
                        if not self.center_mid_rail:
                            door_style_mod.set_input("Mid Rail Location", self.mid_rail_location)
                except:
                    pass  # Input may not exist on all door style modifiers
            else:
                # Disable mid rail if not needed
                try:
                    door_style_mod.set_input("Add Mid Rail", False)
                except:
                    pass
            
            # Inherit materials from parent cabinet's style
            cabinet_style = self.get_parent_cabinet_style(front_obj)
            if cabinet_style:
                material, material_rotated = cabinet_style.get_finish_material()
                # Stiles use regular material (vertical grain)
                door_style_mod.set_input("Stile Material", material)
                # Rails use rotated material (horizontal grain)
                door_style_mod.set_input("Rail Material", material_rotated)
                # Panel material depends on panel_material setting
                if self.panel_material == 'GLASS':
                    glass_mat = get_or_create_glass_material()
                    door_style_mod.set_input("Panel Material", glass_mat)
                else:
                    door_style_mod.set_input("Panel Material", material)
        
        # Store style reference on the object (only after successful application)
        front_obj['DOOR_STYLE_NAME'] = self.name
        return True

    def draw_door_style_ui(self, layout, context):
        """Draw the UI for this door style."""
        box = layout.box()
        box.prop(self, "name", text="Style Name")
        
        # Door type
        col = box.column(align=True)
        col.label(text="Construction:")
        col.prop(self, "door_type", text="Type")
        
        # Show relevant options based on door type
        if self.door_type == 'SLAB':
            col = box.column(align=True)
            col.label(text="Edge Profile:")
            col.prop(self, "edge_profile_type", text="")
        else:
            # 5-piece options
            col = box.column(align=True)
            col.label(text="Frame Dimensions:")
            col.prop(self, "stile_width", text="Stile Width")
            col.prop(self, "rail_width", text="Rail Width")
            col.prop(self, "mid_rail_width", text="Mid Rail Width")
            
            col = box.column(align=True)
            col.label(text="Panel:")
            col.prop(self, "panel_material", text="Material")
            col.prop(self, "panel_thickness", text="Thickness")
            col.prop(self, "panel_inset", text="Inset")
        
        # Profile objects
        col = box.column(align=True)
        col.label(text="Profiles:")
        col.prop(self, "outside_profile", text="Outside")
        if self.door_type != 'SLAB':
            col.prop(self, "inside_profile", text="Inside")
        
        # Assign button
        row = box.row()
        row.scale_y = 1.3
        row.operator("hb_frameless.assign_door_style_to_selected_fronts", text="Assign Style", icon='BRUSH_DATA')
        
        # Update fronts button
        row = box.row()
        row.scale_y = 1.3
        row.operator("hb_frameless.update_fronts_from_style", text="Update Fronts", icon='FILE_REFRESH')


class CalculatorCabinet(PropertyGroup):
    """Property group for calculator cabinet data used in Adjust Cabinet Sizes."""
    cabinet_obj: PointerProperty(name="Cabinet Object", type=bpy.types.Object) # type: ignore
    is_equal: BoolProperty(name="Equal Width", default=True) # type: ignore
    cabinet_width: FloatProperty(name="Width", subtype='DISTANCE', unit='LENGTH') # type: ignore


class Crown_Detail(PropertyGroup):
    """Crown molding detail stored as a reference to a detail scene."""
    
    # Reference to the detail scene where the crown profile is drawn
    detail_scene_name: StringProperty(
        name="Detail Scene",
        description="Name of the detail scene containing the crown profile"
    )  # type: ignore
    
    description: StringProperty(
        name="Description", 
        description="Description of this crown molding detail",
        default=""
    )  # type: ignore
    
    # Crown molding dimensions
    height: FloatProperty(
        name="Height",
        description="Height of the crown molding",
        default=0.0762,  # 3 inches
        min=0.0,
        unit='LENGTH'
    )  # type: ignore
    
    projection: FloatProperty(
        name="Projection",
        description="How far the crown projects from the cabinet face",
        default=0.0508,  # 2 inches
        min=0.0,
        unit='LENGTH'
    )  # type: ignore
    
    spring_angle: FloatProperty(
        name="Spring Angle",
        description="Angle of the crown molding (typically 38 or 45 degrees)",
        default=38.0,
        min=0.0,
        max=90.0,
        subtype='ANGLE'
    )  # type: ignore
    
    def get_detail_scene(self):
        """Get the detail scene object, if it exists."""
        if self.detail_scene_name and self.detail_scene_name in bpy.data.scenes:
            return bpy.data.scenes[self.detail_scene_name]
        return None


class HB_MT_crown_detail_library(bpy.types.Menu):
    """Menu for loading crown details from library."""
    bl_label = "Crown Detail Library"
    bl_idname = "HB_MT_crown_detail_library"
    
    def draw(self, context):
        from ... import hb_detail_library
        
        layout = self.layout
        
        # Check if we're in a crown detail view - show save option
        is_crown_detail = context.scene.get('IS_CROWN_DETAIL', False)
        if is_crown_detail:
            layout.operator("home_builder_details.save_to_library", 
                           text="Save Current Crown Detail", icon='FILE_NEW')
            layout.separator()
        
        # List saved crown details
        crown_details = hb_detail_library.get_library_details(detail_type="crown")
        
        if crown_details:
            layout.label(text="Load from Library:", icon='FILE_FOLDER')
            for detail in crown_details:
                op = layout.operator("home_builder_details.create_from_library",
                                    text=detail.get("name", "Unnamed"), 
                                    icon='IMPORT')
                op.filepath = detail.get("filepath", "")
                op.name = detail.get("name", "Crown Detail")
        else:
            layout.label(text="No saved crown details", icon='INFO')
        
        layout.separator()
        layout.operator("home_builder_details.open_library_folder",
                       text="Open Library Folder", icon='FILE_FOLDER')


class HB_UL_crown_details(UIList):
    """UIList for displaying crown details."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon='MOD_SIMPLEDEFORM')
            # Show if scene exists
            if item.get_detail_scene():
                row.label(text="", icon='CHECKMARK')
            else:
                row.label(text="", icon='ERROR')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='MOD_SIMPLEDEFORM')


class Frameless_Scene_Props(PropertyGroup):   
    
    frameless_selection_mode: EnumProperty(name="Frameless Selection Mode",
                    items=[('Cabinets',"Cabinets","Cabinets"),
                           ('Bays',"Bays","Bays"),
                           ('Openings',"Openings","Openings"),
                           ('Interiors',"Interiors","Interiors"),
                           ('Parts',"Parts","Parts")],
                    default='Cabinets',
                    update=update_frameless_selection_mode)# type: ignore

    #UI OPTIONS
    frameless_tabs: EnumProperty(name="Frameless Tabs",
                       items=[('LIBRARY',"Library","Library"),
                              ('OPTIONS',"Options","Options")],
                       default='LIBRARY')# type: ignore  

    show_cabinet_sizes: BoolProperty(name="Show Cabinet Sizes",description="Show Cabinet Sizes.",default=True)# type: ignore
    show_cabinet_library: BoolProperty(name="Show Cabinet Library",description="Show Cabinet Library.",default=True)# type: ignore
    show_corner_cabinet_library: BoolProperty(name="Show Corner Cabinet Library",description="Show Corner Cabinet Library.",default=False)# type: ignore
    show_appliance_library: BoolProperty(name="Show Appliance Library",description="Show Appliance Library.",default=False)# type: ignore
    show_part_library: BoolProperty(name="Show Part Library",description="Show Part Library.",default=False)# type: ignore
    show_user_library: BoolProperty(name="Show User Library",description="Show User Library.",default=False)# type: ignore
    show_general_options: BoolProperty(name="Show General Options",description="Show General Options.",default=False)# type: ignore
    show_handle_options: BoolProperty(name="Show Handle Options",description="Show Handle Options.",default=False)# type: ignore
    show_front_options: BoolProperty(name="Show Front Options",description="Show Front Options.",default=False)# type: ignore
    show_drawer_options: BoolProperty(name="Show Drawer Options",description="Show Drawer Options.",default=False)# type: ignore
    show_crown_details: BoolProperty(name="Show Crown Details",description="Show Crown Details.",default=False)# type: ignore
    show_toe_kick_details: BoolProperty(name="Show Toe Kick Details",description="Show Toe Kick Details.",default=False)# type: ignore
    show_upper_bottom_details: BoolProperty(name="Show Upper Bottom Details",description="Show Upper Bottom Details.",default=False)# type: ignore

    # Calculator cabinets for Adjust Cabinet Sizes operator
    calculator_cabinets: CollectionProperty(name="Calculator Cabinets", type=CalculatorCabinet) # type: ignore
    show_countertop_options: BoolProperty(name="Show Countertop Options",description="Show Countertop Options.",default=False)# type: ignore
    show_cabinet_styles: BoolProperty(name="Show Cabinet Styles",description="Show Cabinet Styles.",default=True)# type: ignore

    # CABINET STYLES
    cabinet_styles: CollectionProperty(type=Frameless_Cabinet_Style, name="Cabinet Styles")# type: ignore
    active_cabinet_style_index: IntProperty(name="Active Cabinet Style Index", default=0)# type: ignore

    #CABINET OPTIONS
    fill_cabinets: bpy.props.BoolProperty(name="Fill Cabinets",default = True)# type: ignore

    base_exterior: EnumProperty(name="Base Exterior",
                               items=[('Doors',"Doors","Doors"),
                                      ('Door Drawer','Door Drawer','Door Drawer'),
                                      ('2 Drawers','2 Drawers','2 Drawers'),
                                      ('3 Drawers','3 Drawers','3 Drawers'),
                                      ('4 Drawers','4 Drawers','4 Drawers'),
                                      ('Open','Open','Open')],
                               default='Door Drawer')# type: ignore

    include_drawer_boxes: bpy.props.BoolProperty(name="Include Drawer Boxes",default = True,update=update_include_drawer_boxes)# type: ignore

    base_corner_type: EnumProperty(name="Base Corner Type",
                               items=[('Diagonal Corner','Diagonal Corner','Diagonal Corner'),
                                      ('Pie Cut Corner','Pie Cut Corner','Pie Cut Corner'),
                                      ('Pie Cut 2 Drawer Base','Pie Cut 2 Drawer Base','Pie Cut 2 Drawer Base'),
                                      ('Pie Cut 3 Drawer Base','Pie Cut 3 Drawer Base','Pie Cut 3 Drawer Base'),
                                      ('Pie Cut 4 Drawer Base','Pie Cut 4 Drawer Base','Pie Cut 4 Drawer Base')],
                               default='Pie Cut Corner')# type: ignore  

    upper_corner_type: EnumProperty(name="Upper Corner Type",
                               items=[('Diagonal Corner','Diagonal Corner','Diagonal Corner'),
                                      ('Diagonal Stacked Corner','Diagonal Stacked Corner','Diagonal Stacked Corner'),
                                      ('Pie Cut Corner','Pie Cut Corner','Pie Cut Corner'),
                                      ('Pie Cut Stacked Corner','Pie Cut Stacked Corner','Pie Cut Stacked Corner')],
                               default='Pie Cut Corner')# type: ignore  

    upper_and_tall_corner_type: EnumProperty(name="Upper Corner Type",
                               items=[('Diagonal','Diagonal','Diagonal'),
                                      ('Diagonal Stacked','Diagonal Stacked','Diagonal Stacked'),
                                      ('Pie Cut','Pie Cut','Pie Cut'),
                                      ('Pie Cut Stacked','Pie Cut Stacked','Pie Cut Stacked')],
                               default='Diagonal')# type: ignore   

    #APPLIANCE SIZES
    refrigerator_height: FloatProperty(name="Refrigerator Height",
                                         description="Default Refrigerator height",
                                         default=units.inch(62.0),
                                         unit='LENGTH',
                                         precision=4)# type: ignore   

    refrigerator_cabinet_width: FloatProperty(name="Refrigerator Cabinet Width",
                                         description="Default Refrigerator cabinet width",
                                         default=units.inch(38.0),
                                         unit='LENGTH',
                                         precision=4)# type: ignore

    range_width: FloatProperty(name="Range Width",
                               description="Default Dishwasher Width",
                               default=units.inch(36.0),
                               unit='LENGTH',
                               precision=4)# type: ignore     

    dishwasher_width: FloatProperty(name="Dishwasher Width",
                                    description="Default Dishwasher Width",
                                    default=units.inch(24.0),
                                    unit='LENGTH',
                                    precision=4)# type: ignore

    #CABINET SIZES
    default_top_cabinet_clearance: FloatProperty(name="Default Top Cabinet Clearance",
                                                 description="Clearance to Hold Top Cabinets from Ceiling",
                                                 default=units.inch(12.0),
                                                 unit='LENGTH',
                                                 precision=4,
                                                 update=update_top_cabinet_clearance)# type: ignore              

    default_wall_cabinet_location: FloatProperty(name="Default Wall Cabinet Location",
                                                 description="Distance from Floor to Bottom of Wall Cabinet",
                                                 default=units.inch(54.0),
                                                 unit='LENGTH',
                                                 precision=4,
                                                 update=update_top_cabinet_clearance)# type: ignore  
    
    default_cabinet_width: FloatProperty(name="Default Cabinet Width",
                                                 description="Default width for cabinets",
                                                 default=units.inch(36.0),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
        
    base_cabinet_depth: FloatProperty(name="Base Cabinet Depth",
                                                 description="Default depth for base cabinets",
                                                 default=units.inch(23.125),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
    
    base_cabinet_height: FloatProperty(name="Base Cabinet Height",
                                                  description="Default height for base cabinets",
                                                  default=units.inch(34.5),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    base_inside_corner_size: FloatProperty(name="Base Inside Corner Size",
                                           description="Default width and depth for the inside base corner cabinets",
                                           default=units.inch(36.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore
    
    tall_inside_corner_size: FloatProperty(name="Tall Inside Corner Size",
                                           description="Default width and depth for the inside tall corner cabinets",
                                           default=units.inch(36.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore

    upper_inside_corner_size: FloatProperty(name="Upper Inside Corner Size",
                                           description="Default width and depth for the inside upper corner cabinets",
                                           default=units.inch(24.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore

    tall_cabinet_depth: FloatProperty(name="Tall Cabinet Depth",
                                                 description="Default depth for tall cabinets",
                                                 default=units.inch(25.5),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
    
    tall_cabinet_height: FloatProperty(name="Tall Cabinet Height",
                                                  description="Default height for tall cabinets",
                                                  default=units.inch(84.0),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    upper_cabinet_depth: FloatProperty(name="Upper Cabinet Depth",
                                                  description="Default depth for upper cabinets",
                                                  default=units.inch(13.0),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    upper_cabinet_height: FloatProperty(name="Upper Cabinet Height",
                                                   description="Default height for upper cabinets",
                                                   default=units.inch(30),
                                                   unit='LENGTH',
                                                   precision=4)# type: ignore
    
    base_width_blind: FloatProperty(name="Base Width Blind",
                                               description="Default width for base blind corner cabinets",
                                               default=units.inch(48.0),
                                               unit='LENGTH',
                                               precision=4)# type: ignore
    
    tall_width_blind: FloatProperty(name="Tall Width Blind",
                                               description="Default width for tall blind corner cabinets",
                                               default=units.inch(48.0),
                                               unit='LENGTH',
                                               precision=4)# type: ignore

    upper_width_blind: FloatProperty(name="Upper Width Blind",
                                                description="Default width for upper blind corner cabinets",
                                                default=units.inch(36.0),
                                                unit='LENGTH',
                                                precision=4)# type: ignore
    
    tall_cabinet_split_height: FloatProperty(name="Tall Cabinet Split Height",
                                                  description="Default height for the bottom opening of the tall split cabinet",
                                                  default=units.inch(54),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore

    upper_top_stacked_cabinet_height: FloatProperty(name="Upper Cabinet Top Stacked Height",
                                    description="Default height for the top opening of the upper cabinet stacked",
                                    default=units.inch(15),
                                    unit='LENGTH',
                                    precision=4)# type: ignore
    
    #CABINET GENERAL CONSTRUCTION OPTIONS
    show_machining: bpy.props.BoolProperty(name="Show Machining",default = True,update=update_show_machining)# type: ignore

    default_carcass_part_thickness: FloatProperty(name="Default Carcass Part Thickness",
                                                 description="",
                                                 default=units.inch(.75),
                                                 unit='LENGTH')# type: ignore

    default_toe_kick_height: FloatProperty(name="Default Toe Kick Height",
                                                 description="",
                                                 default=units.inch(4),
                                                 unit='LENGTH')# type: ignore
    
    default_toe_kick_setback: FloatProperty(name="Default Toe Kick Setback",
                                                 description="",
                                                 default=units.inch(2.5),
                                                 unit='LENGTH')# type: ignore
    
    default_toe_kick_type: EnumProperty(name="Toe Kick Type",
                       items=[('Notch Ends to Floor',"Notch Ends to Floor","Notch Ends to Floor"),
                              ('Ladder Style',"Ladder Style","Ladder Style"),
                              ('Leg Levelers',"Leg Levelers","Leg Levelers")],
                       default='Ladder Style')# type: ignore

    base_top_construction: EnumProperty(name="Base Top Construction",
                       items=[('Stretchers',"Stretchers","Stretchers"),
                              ('Full Top',"Full Top","Full Top")],
                       default='Stretchers')# type: ignore

    equal_drawer_stack_heights: BoolProperty(name="Equal Drawer Stack Heights", 
                                             description="Check this make all drawer stack heights equal. Otherwise the Top Drawer Height will be set.", 
                                                        default=False)# type: ignore
    
    top_drawer_front_height: FloatProperty(name="Top Drawer Front Height",
                                           description="Default top drawer front height.",
                                           default=units.inch(6.0),
                                           unit='LENGTH')# type: ignore

    door_styles: CollectionProperty(type=Frameless_Door_Style, name="Door Styles")# type: ignore
    active_door_style_index: IntProperty(name="Active Door Style Index", default=0)# type: ignore

    # CROWN DETAILS
    crown_details: CollectionProperty(type=Crown_Detail, name="Crown Details")# type: ignore
    active_crown_detail_index: IntProperty(name="Active Crown Detail Index", default=0)# type: ignore

    
    #CABINET PULL OPTIONS
    current_door_pull_object: PointerProperty(type=bpy.types.Object)# type: ignore
    current_drawer_front_pull_object: PointerProperty(type=bpy.types.Object)# type: ignore

    pull_dim_from_edge: FloatProperty(name="Pull Distance From Edge",
                                                 description="Distance from Edge of Door to center of pull",
                                                 default=units.inch(2.0),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_base: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Top of Base Door to Top of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_tall: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Tall Door to Center of Pull",
                                                 default=units.inch(45),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_upper: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Upper Door to Bottom of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_drawers: FloatProperty(name="Pull Vertical Location Drawers",
                                                 description="Distance from Top of Drawer Front to Center of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore
    
    center_pulls_on_drawer_front: BoolProperty(name="Center Pulls on Drawer Front", 
                                                        description="Check this to center pulls on drawer fronts. Otherwise vertical location will be used.", 
                                                        default=True)# type: ignore

    # Pull selection from library
    door_pull_selection: EnumProperty(
        name="Door Pull",
        description="Select pull style for doors",
        items=get_pull_enum_items,
    )# type: ignore
    
    drawer_pull_selection: EnumProperty(
        name="Drawer Pull", 
        description="Select pull style for drawers",
        items=get_pull_enum_items,
    )# type: ignore
    
    pull_finish: EnumProperty(
        name="Pull Finish",
        description="Select finish for cabinet pulls",
        items=get_pull_finish_enum_items,
    )# type: ignore


    def ensure_default_style(self):
        """Ensure at least one cabinet style exists."""

        # Get Cabinet Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        if len(props.cabinet_styles) == 0:
            style = props.cabinet_styles.add()
            style.name = "Default Style"
    
    def get_active_style(self):
        """Get the currently active cabinet style."""

        # Get Cabinet Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        if props.active_cabinet_style_index < len(props.cabinet_styles):
            return props.cabinet_styles[props.active_cabinet_style_index]
        return props.cabinet_styles[0]

    def draw_cabinet_styles_ui(self, layout, context):
        """Draw the cabinet styles UI section."""
        # Get Cabinet Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        # UIList for styles
        row = layout.row()
        row.template_list(
            "HB_UL_cabinet_styles", "",
            props, "cabinet_styles",
            props, "active_cabinet_style_index",
            rows=3
        )
        
        # Add/Remove buttons
        col = row.column(align=True)
        col.operator("hb_frameless.add_cabinet_style", icon='ADD', text="")
        col.operator("hb_frameless.remove_cabinet_style", icon='REMOVE', text="")
        col.separator()
        col.operator("hb_frameless.duplicate_cabinet_style", icon='DUPLICATE', text="")
        
        # Active style properties
        if props.cabinet_styles and props.active_cabinet_style_index < len(props.cabinet_styles):
            style = props.cabinet_styles[props.active_cabinet_style_index]
            style.draw_cabinet_style_ui(layout, context)

    def ensure_default_door_style(self):
        """Ensure at least one door style exists."""
        # Get Door Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        if len(props.door_styles) == 0:
            style = props.door_styles.add()
            style.name = "Default Door Style"
    
    def get_active_door_style(self):
        """Get the currently active door style."""
        # Get Door Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        if props.active_door_style_index < len(props.door_styles):
            return props.door_styles[props.active_door_style_index]
        if len(props.door_styles) > 0:
            return props.door_styles[0]
        return None

    def draw_door_styles_ui(self, layout, context):
        """Draw the door styles UI section."""
        # Get Door Styles from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # UIList for styles
        row = layout.row()
        row.template_list(
            "HB_UL_door_styles", "",
            props, "door_styles",
            props, "active_door_style_index",
            rows=3
        )
        
        # Add/Remove buttons
        col = row.column(align=True)
        col.operator("hb_frameless.add_door_style", icon='ADD', text="")
        col.operator("hb_frameless.remove_door_style", icon='REMOVE', text="")
        col.separator()
        col.operator("hb_frameless.duplicate_door_style", icon='DUPLICATE', text="")
        
        # Active style properties
        if props.door_styles and props.active_door_style_index < len(props.door_styles):
            style = props.door_styles[props.active_door_style_index]
            style.draw_door_style_ui(layout, context)   

    def draw_cabinet_sizes_ui(self,layout,context):
        unit_settings = context.scene.unit_settings      
        row = layout.row()
        row.label(text="Top Cabinet Clearance:")
        row.prop(self,'default_top_cabinet_clearance',text="")  
        row.operator('hb_frameless.update_cabinet_sizes',text="",icon='FILE_REFRESH')     
        row = layout.row()
        row.label(text="Upper Cabinet Dim to Floor:")
        row.prop(self,'default_wall_cabinet_location',text="")  
        row.label(text="",icon='BLANK1')
        row = layout.row()
        row.label(text="Sizes")
        row.label(text="Base")
        row.label(text="Tall")      
        row.label(text="Upper")
        row = layout.row()
        row.label(text="Depth:")
        row.prop(self,'base_cabinet_depth',text="")
        row.prop(self,'tall_cabinet_depth',text="")
        row.prop(self,'upper_cabinet_depth',text="")   
        row = layout.row()
        row.label(text="Height:")
        row.prop(self,'base_cabinet_height',text="")
        row.label(text=units.unit_to_string(unit_settings,self.tall_cabinet_height))
        row.label(text=units.unit_to_string(unit_settings,self.upper_cabinet_height))
        row = layout.row()
        row.label(text="Stacked Top Cabinet Height:") 
        row.prop(self,'upper_top_stacked_cabinet_height',text="")
        row = layout.row()
        row.label(text="Tall Split Height:") 
        row.prop(self,'tall_cabinet_split_height',text="")

    def draw_user_library_ui(self,layout,context):
        from .operators import ops_library
        
        # Header row with refresh and folder buttons
        row = layout.row()
        row.label(text="User Library")
        row.operator('hb_frameless.refresh_user_library', text="", icon='FILE_REFRESH')
        row.operator('hb_frameless.open_user_library_folder', text="", icon='FILE_FOLDER')
        
        # Create/Save buttons
        col = layout.column(align=True)
        col.operator('hb_frameless.create_cabinet_group', text="Create Cabinet Group", icon='ADD')
        col.operator('hb_frameless.save_cabinet_group_to_user_library', text="Save to Library", icon='FILE_TICK')
        
        layout.separator()
        
        # Get library items
        library_items = ops_library.get_user_library_items()
        
        if not library_items:
            box = layout.box()
            box.label(text="No saved cabinet groups", icon='INFO')
            box.label(text="Save a cabinet group to see it here")
        else:
            # Display library items
            box = layout.box()
            box.label(text=f"Saved Groups ({len(library_items)})", icon='ASSET_MANAGER')
            
            # Grid layout for items with thumbnails
            flow = box.column_flow(columns=2, align=True)
            
            for item in library_items:
                item_box = flow.box()
                
                # Item name with delete button
                row = item_box.row()
                row.label(text=item['name'])
                del_op = row.operator('hb_frameless.delete_library_item', text="", icon='X', emboss=False)
                del_op.filepath = item['filepath']
                del_op.item_name = item['name']
                
                # Show thumbnail if available
                if item['thumbnail']:
                    icon_id = load_library_thumbnail(item['thumbnail'], item['name'])
                    if icon_id:
                        item_box.template_icon(icon_value=icon_id, scale=5.0)
                
                # Load button
                op = item_box.operator('hb_frameless.load_cabinet_group_from_library', 
                                       text="Add to Scene", icon='IMPORT')
                op.filepath = item['filepath']

    def draw_cabinet_library_ui(self,layout,context):
        # Cabinet definitions: (display_name, cabinet_name, thumbnail_name)
        base_cabinets = [
            ("Door", "Base Door", "Base Door"),
            ("Door Drw", "Base Door Drw", "Base Door Drw"),
            ("Drawer", "Base Drawer", "Base Drw"),
            ("Lap Drawer", "Lap Drawer", "Lap Drw"),
        ]
        
        upper_cabinets = [
            ("Upper", "Upper", "Upper"),
            ("Upper Stacked", "Upper Stacked", "Upper Stacked"),
        ]
        
        tall_cabinets = [
            ("Tall", "Tall", "Tall"),
            ("Tall Stacked", "Tall Stacked", "Tall Stacked"),
        ]
        
        # Base cabinets
        layout.label(text="Base Cabinets:")
        flow = layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in base_cabinets:
            box = flow.box()
            box.scale_y = 0.9
            
            # Show thumbnail
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            
            # Button
            op = box.operator('hb_frameless.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name
        
        # Upper cabinets
        layout.label(text="Upper Cabinets:")
        flow = layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in upper_cabinets:
            box = flow.box()
            box.scale_y = 0.9
            
            # Show thumbnail
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            
            # Button
            op = box.operator('hb_frameless.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name
        
        # Tall cabinets
        layout.label(text="Tall Cabinets:")
        flow = layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in tall_cabinets:
            box = flow.box()
            box.scale_y = 0.9
            
            # Show thumbnail
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            
            # Button
            op = box.operator('hb_frameless.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

    def draw_cabinet_options_general(self,layout,context):
        unit_settings = context.scene.unit_settings
        size_box = layout.box()
        row = size_box.row()
        row.prop(self,'show_machining',text="Show Machining")
        row = size_box.row()
        row.label(text="Toe Kick:")
        row.operator('hb_frameless.update_toe_kick_prompts',text="",icon='FILE_REFRESH')
        row = size_box.row()
        row.prop(self,'default_toe_kick_height',text="Height")
        row.prop(self,'default_toe_kick_setback',text="Setback")
        row = size_box.row()
        row.prop(self,'default_toe_kick_type',text="Type")
        size_box = layout.box()
        row = size_box.row()
        row.label(text="Base Top Construction:")
        row.prop(self,'base_top_construction',text="")
        row.operator('hb_frameless.update_base_top_construction_prompts',text="",icon='FILE_REFRESH')        
        size_box = layout.box()            
        row = size_box.row()
        row.label(text="Drawers:")
        row.operator('hb_frameless.update_drawer_front_height_prompts',text="",icon='FILE_REFRESH')
        row = size_box.row()
        row.prop(self,'equal_drawer_stack_heights')
        if not self.equal_drawer_stack_heights:
            row = size_box.row()
            row.prop(self,'top_drawer_front_height',text="Top Drawer Front Height")

    def draw_cabinet_options_handles(self,layout,context):
        from ... import hb_project
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Pull Selection - Side by side thumbnails
        row = layout.row(align=True)
        
        # Door Pull column
        col = row.column(align=True)
        col.label(text="Door Pull:")
        col.prop(props, 'door_pull_selection', text="")
        door_pull_name = os.path.splitext(props.door_pull_selection)[0] if props.door_pull_selection else ""
        if door_pull_name:
            thumb_path = os.path.join(os.path.dirname(__file__), 
                                      'frameless_assets', 'cabinet_pulls', 
                                      door_pull_name + '.png')
            if os.path.exists(thumb_path):
                icon_id = load_library_thumbnail(thumb_path, f"pull_door_{door_pull_name}")
                if icon_id:
                    col.template_icon(icon_value=icon_id, scale=4.0)
        
        # Drawer Pull column
        col = row.column(align=True)
        col.label(text="Drawer Pull:")
        col.prop(props, 'drawer_pull_selection', text="")
        drawer_pull_name = os.path.splitext(props.drawer_pull_selection)[0] if props.drawer_pull_selection else ""
        if drawer_pull_name:
            thumb_path = os.path.join(os.path.dirname(__file__), 
                                      'frameless_assets', 'cabinet_pulls', 
                                      drawer_pull_name + '.png')
            if os.path.exists(thumb_path):
                icon_id = load_library_thumbnail(thumb_path, f"pull_drawer_{drawer_pull_name}")
                if icon_id:
                    col.template_icon(icon_value=icon_id, scale=4.0)
        
        # Finish dropdown inline
        row = layout.row(align=True)
        row.label(text="Finish:")
        row.prop(props, 'pull_finish', text="")
        
        layout.separator()
        
        # Pull Locations - compact grid
        col = layout.column(align=True)
        col.prop(props, 'pull_dim_from_edge', text="Edge Distance")
        
        col.separator()
        col.label(text="Door Pull Height:")
        row = col.row(align=True)
        row.prop(props, 'pull_vertical_location_base', text="Base")
        row.prop(props, 'pull_vertical_location_tall', text="Tall")
        row.prop(props, 'pull_vertical_location_upper', text="Upper")
        
        col.separator()
        row = col.row(align=True)
        row.prop(props, 'center_pulls_on_drawer_front', text="Center Drawer Pulls")
        if not props.center_pulls_on_drawer_front:
            col.prop(props, 'pull_vertical_location_drawers', text="Drawer Pull Height")
        
        layout.separator()
        
        # Update buttons - single row
        row = layout.row(align=True)
        row.operator('hb_frameless.update_cabinet_pulls', text="Pulls", icon='FILE_REFRESH')
        row.operator('hb_frameless.update_pull_locations', text="Locations", icon='FILE_REFRESH')
        row.operator('hb_frameless.update_pull_finish', text="Finish", icon='FILE_REFRESH')

    def draw_crown_details_ui(self, layout, context):
        """Draw the crown molding details UI section."""
        from ... import hb_project
        
        # Get Crown Details from Main Scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create new crown detail button with library dropdown
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("hb_frameless.create_crown_detail", text="Create Crown Detail", icon='ADD')
        row.menu("HB_MT_crown_detail_library", text="", icon='DOWNARROW_HLT')
        
        layout.separator()
        
        # UIList for crown details
        if len(props.crown_details) > 0:
            row = layout.row()
            row.template_list(
                "HB_UL_crown_details", "",
                props, "crown_details",
                props, "active_crown_detail_index",
                rows=3
            )
            
            # Add/Remove buttons
            col = row.column(align=True)
            col.operator("hb_frameless.create_crown_detail", icon='ADD', text="")
            col.operator("hb_frameless.delete_crown_detail", icon='REMOVE', text="")
            col.separator()
            col.operator("hb_frameless.edit_crown_detail", icon='GREASEPENCIL', text="")
            
            # Active crown detail properties
            if props.crown_details and props.active_crown_detail_index < len(props.crown_details):
                crown = props.crown_details[props.active_crown_detail_index]
                
                box = layout.box()
                box.prop(crown, "name", text="Name")
                box.prop(crown, "description", text="Description")
                
                col = box.column(align=True)
                col.label(text="Dimensions:")
                col.prop(crown, "height")
                col.prop(crown, "projection")
                col.prop(crown, "spring_angle")
                
                # Show detail scene status
                detail_scene = crown.get_detail_scene()
                if detail_scene:
                    row = box.row()
                    row.label(text=f"Profile Scene: {crown.detail_scene_name}", icon='CHECKMARK')
                else:
                    row = box.row()
                    row.label(text="No profile scene", icon='ERROR')
                
                # Assign to cabinets button
                layout.separator()
                row = layout.row()
                row.scale_y = 1.3
                row.operator("hb_frameless.assign_crown_to_cabinets", text="Assign to Selected Cabinets", icon='BRUSH_DATA')
        else:
            box = layout.box()
            box.label(text="No crown details defined", icon='INFO')
            box.label(text="Create a crown detail to define crown molding profiles")


    def draw_toe_kick_details_ui(self,layout,context):
        pass

    def draw_upper_bottom_details_ui(self,layout,context):
        pass

    def draw_drawer_box_ui(self, layout, context):
        """Draw the drawer box options UI section."""
        from ... import hb_project
        
        # Get props from main scene
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Include drawer boxes toggle
        row = layout.row()
        row.prop(props, 'include_drawer_boxes', text="Include Drawer Boxes in New Cabinets")

    def draw_library_ui(self,layout,context):

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, "frameless_tabs", 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, "frameless_tabs", 'OPTIONS', icon='PREFERENCES') 

        if self.frameless_tabs == 'LIBRARY':
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_cabinet_sizes',text="Cabinet Sizes",icon='TRIA_DOWN' if self.show_cabinet_sizes else 'TRIA_RIGHT',emboss=False)
            if self.show_cabinet_sizes:           
                self.draw_cabinet_sizes_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_cabinet_library',text="Cabinets",icon='TRIA_DOWN' if self.show_cabinet_library else 'TRIA_RIGHT',emboss=False)
            if self.show_cabinet_library:
                self.draw_cabinet_library_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_corner_cabinet_library',text="Corner Cabinets",icon='TRIA_DOWN' if self.show_corner_cabinet_library else 'TRIA_RIGHT',emboss=False)
            if self.show_corner_cabinet_library:

                row = box.row()
                row.label(text="Corner Cabinet Sizes")
                row = box.row()
                row.prop(self,'base_inside_corner_size',text="Base")
                row.prop(self,'tall_inside_corner_size',text="Tall")
                row.prop(self,'upper_inside_corner_size',text="Upper")
                row = box.row()
                row.label(text="Base Cabinet Type")
                row.prop(self,'base_corner_type',text="")
                row = box.row()
                row.label(text="Upper and Tall Cabinet Type")
                row.prop(self,'upper_and_tall_corner_type',text="")                

                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Base").cabinet_name = 'Base'
                row.operator('hb_frameless.draw_cabinet',text="Tall").cabinet_name = 'Tall'
                row.operator('hb_frameless.draw_cabinet',text="Upper").cabinet_name = 'Upper'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Base Blind").cabinet_name = 'Base Blind'
                row.operator('hb_frameless.draw_cabinet',text="Tall Blind").cabinet_name = 'Tall Blind'
                row.operator('hb_frameless.draw_cabinet',text="Upper Blind").cabinet_name = 'Upper Blind'  

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_appliance_library',text="Appliances",icon='TRIA_DOWN' if self.show_appliance_library else 'TRIA_RIGHT',emboss=False)
            if self.show_appliance_library:
                row = box.row()
                row.label(text="Refrigerator Height")
                row.prop(self,'refrigerator_height',text="")
                row = box.row()
                row.label(text="Widths")
                row = box.row()
                row.prop(self,'refrigerator_cabinet_width',text="Refrigerator")
                row = box.row()
                row.prop(self,'dishwasher_width',text="Dishwasher")
                row.prop(self,'range_width',text="Range")       

                # APPLIANCE CABINETS
                row = box.row()
                row.scale_y = 1.5  
                row.operator('hb_frameless.draw_cabinet',text="Refrigerator").cabinet_name = 'Refrigerator Cabinet'                 
                row.operator('hb_frameless.draw_cabinet',text="Base Built-In").cabinet_name = 'Base Built-In'
                row.operator('hb_frameless.draw_cabinet',text="Tall Built-In").cabinet_name = 'Tall Built-In'
                
                # STAND ALONE APPLIANCES
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Dishwasher").cabinet_name = 'Dishwasher'
                row.operator('hb_frameless.draw_cabinet',text="Refrigerator").cabinet_name = 'Refrigerator'
                row.operator('hb_frameless.draw_cabinet',text="Range").cabinet_name = 'Range'
                row.operator('hb_frameless.draw_cabinet',text="Range Hood").cabinet_name = 'Range Hood'  

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_part_library',text="Parts & Miscellaneous",icon='TRIA_DOWN' if self.show_part_library else 'TRIA_RIGHT',emboss=False)
            if self.show_part_library:
                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Misc Part").cabinet_name = 'Misc Part'
                row.operator('hb_frameless.draw_cabinet',text="Countertop").cabinet_name = 'Countertop'
                row.operator('hb_frameless.draw_cabinet',text="Half Wall").cabinet_name = 'Half Wall'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Floating Shelves").cabinet_name = 'Floating Shelves'
                row.operator('hb_frameless.draw_cabinet',text="Leg").cabinet_name = 'Leg'
                row.operator('hb_frameless.draw_cabinet',text="Support Frame").cabinet_name = 'Support Frame'  
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Floating Shelves").cabinet_name = 'Floating Shelves'
                row.operator('hb_frameless.draw_cabinet',text="Leg Column").cabinet_name = 'Leg Column'
                row.operator('hb_frameless.draw_cabinet',text="Valance").cabinet_name = 'Valance'                 

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_user_library',text="User",icon='TRIA_DOWN' if self.show_user_library else 'TRIA_RIGHT',emboss=False)
            if self.show_user_library:
                self.draw_user_library_ui(box,context)

        if self.frameless_tabs == 'OPTIONS':
            # CABINET STYLES - Show first in OPTIONS tab
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_cabinet_styles',text="Cabinet Styles",icon='TRIA_DOWN' if self.show_cabinet_styles else 'TRIA_RIGHT',emboss=False)
            if self.show_cabinet_styles:
                self.draw_cabinet_styles_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_front_options',text="Door and Drawer Front Styles",icon='TRIA_DOWN' if self.show_front_options else 'TRIA_RIGHT',emboss=False)
            if self.show_front_options:
                self.draw_door_styles_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_handle_options',text="Handles",icon='TRIA_DOWN' if self.show_handle_options else 'TRIA_RIGHT',emboss=False)
            if self.show_handle_options:
                size_box = box.box()
                self.draw_cabinet_options_handles(size_box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_general_options',text="General Construction",icon='TRIA_DOWN' if self.show_general_options else 'TRIA_RIGHT',emboss=False)
            if self.show_general_options:
                self.draw_cabinet_options_general(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_drawer_options',text="Drawer Boxes",icon='TRIA_DOWN' if self.show_drawer_options else 'TRIA_RIGHT',emboss=False)
            if self.show_drawer_options:
                self.draw_drawer_box_ui(box, context)
                
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_crown_details',text="Crown Details",icon='TRIA_DOWN' if self.show_crown_details else 'TRIA_RIGHT',emboss=False)
            if self.show_crown_details:
                self.draw_crown_details_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_toe_kick_details',text="Toe Kick Details",icon='TRIA_DOWN' if self.show_toe_kick_details else 'TRIA_RIGHT',emboss=False)
            if self.show_toe_kick_details:
                self.draw_toe_kick_details_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_upper_bottom_details',text="Upper Bottom Details",icon='TRIA_DOWN' if self.show_upper_bottom_details else 'TRIA_RIGHT',emboss=False)
            if self.show_upper_bottom_details:
                self.draw_upper_bottom_details_ui(box,context)

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_frameless = PointerProperty(
            name="Frameless Props",
            description="Frameless Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_frameless            


classes = (
    Frameless_Cabinet_Style,
    HB_UL_cabinet_styles,
    Frameless_Door_Style,
    HB_UL_door_styles,
    CalculatorCabinet,
    Crown_Detail,
    HB_MT_crown_detail_library,
    HB_UL_crown_details,
    Frameless_Scene_Props,
)

_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)

def register():
    _register_classes()
    # Initialize preview collections
    get_library_previews()
    get_cabinet_previews()

def unregister():
    _unregister_classes()
    # Clean up preview collections
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()         
