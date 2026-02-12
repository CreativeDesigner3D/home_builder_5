import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
)
from . import units


# =============================================================================
# OBSTACLE TYPE DEFINITIONS
# =============================================================================

# Format: (id, name, description, icon, width, height, depth, default_height_from_floor, surface)
# surface: 'WALL', 'FLOOR', 'CEILING', 'ANY'

WALL_OBSTACLES = [
    ('OUTLET_STANDARD', "Standard Outlet", "Standard electrical outlet", 'PLUGIN', 
     units.inch(2.75), units.inch(4.5), units.inch(0.25), units.inch(12), 'WALL'),
    ('OUTLET_DOUBLE', "Double Outlet", "Double-gang electrical outlet", 'PLUGIN', 
     units.inch(4.5), units.inch(4.5), units.inch(0.25), units.inch(12), 'WALL'),
    ('OUTLET_GFCI', "GFCI Outlet", "Ground fault circuit interrupter outlet", 'PLUGIN', 
     units.inch(2.75), units.inch(4.5), units.inch(0.25), units.inch(42), 'WALL'),
    ('SWITCH_SINGLE', "Light Switch", "Single light switch", 'LIGHT', 
     units.inch(2.75), units.inch(4.5), units.inch(0.25), units.inch(48), 'WALL'),
    ('SWITCH_DOUBLE', "Double Switch", "Double light switch", 'LIGHT', 
     units.inch(4.5), units.inch(4.5), units.inch(0.25), units.inch(48), 'WALL'),
    ('SWITCH_DIMMER', "Dimmer Switch", "Dimmer light switch", 'LIGHT', 
     units.inch(2.75), units.inch(4.5), units.inch(0.25), units.inch(48), 'WALL'),
    ('THERMOSTAT', "Thermostat", "Wall thermostat", 'TEMP', 
     units.inch(3), units.inch(4), units.inch(1.5), units.inch(52), 'WALL'),
    ('VENT_WALL', "Wall Vent", "HVAC wall vent/register", 'MESH_GRID', 
     units.inch(14), units.inch(6), units.inch(2), units.inch(6), 'WALL'),
    ('VENT_WALL_LARGE', "Large Wall Vent", "Large HVAC wall vent", 'MESH_GRID', 
     units.inch(30), units.inch(6), units.inch(2), units.inch(6), 'WALL'),
    ('VENT_RETURN', "Return Vent", "HVAC return air vent", 'MESH_GRID', 
     units.inch(20), units.inch(20), units.inch(2), units.inch(12), 'WALL'),
    ('ACCESS_PANEL', "Access Panel", "Wall access panel", 'CHECKBOX_DEHLT', 
     units.inch(14), units.inch(14), units.inch(1), units.inch(48), 'WALL'),
    ('ACCESS_PANEL_LARGE', "Large Access Panel", "Large wall access panel", 'CHECKBOX_DEHLT', 
     units.inch(24), units.inch(24), units.inch(1), units.inch(36), 'WALL'),
    ('CABLE_OUTLET', "Cable/Data Outlet", "Cable TV or data outlet", 'LINKED', 
     units.inch(2.75), units.inch(4.5), units.inch(0.25), units.inch(12), 'WALL'),
    ('INTERCOM', "Intercom", "Wall intercom panel", 'SPEAKER', 
     units.inch(4), units.inch(5), units.inch(2), units.inch(52), 'WALL'),
    ('FIRE_ALARM', "Fire Alarm Pull", "Fire alarm pull station", 'ERROR', 
     units.inch(3), units.inch(5), units.inch(3), units.inch(48), 'WALL'),
]

FLOOR_OBSTACLES = [
    ('VENT_FLOOR', "Floor Vent", "HVAC floor vent/register", 'MESH_GRID', 
     units.inch(12), units.inch(4), units.inch(2), 0, 'FLOOR'),
    ('VENT_FLOOR_LARGE', "Large Floor Vent", "Large HVAC floor vent", 'MESH_GRID', 
     units.inch(14), units.inch(6), units.inch(2), 0, 'FLOOR'),
    ('FLOOR_DRAIN', "Floor Drain", "Floor drain", 'SORTTIME', 
     units.inch(4), units.inch(4), units.inch(4), 0, 'FLOOR'),
    ('FLOOR_OUTLET', "Floor Outlet", "Floor electrical outlet", 'PLUGIN', 
     units.inch(4), units.inch(4), units.inch(4), 0, 'FLOOR'),
    ('FLOOR_BOX', "Floor Box", "Multi-service floor box", 'PLUGIN', 
     units.inch(6), units.inch(6), units.inch(4), 0, 'FLOOR'),
]

CEILING_OBSTACLES = [
    ('LIGHT_RECESSED', "Recessed Light", "Recessed ceiling light", 'LIGHT', 
     units.inch(6), units.inch(6), units.inch(8), 0, 'CEILING'),
    ('LIGHT_RECESSED_SMALL', "Small Recessed Light", "Small recessed light (4\")", 'LIGHT', 
     units.inch(4), units.inch(4), units.inch(6), 0, 'CEILING'),
    ('LIGHT_SURFACE', "Surface Light", "Surface mount ceiling light", 'LIGHT', 
     units.inch(12), units.inch(12), units.inch(4), 0, 'CEILING'),
    ('CEILING_FAN', "Ceiling Fan", "Ceiling fan", 'FORCE_VORTEX', 
     units.inch(52), units.inch(52), units.inch(12), 0, 'CEILING'),
    ('CEILING_FAN_SMALL', "Small Ceiling Fan", "Small ceiling fan (42\")", 'FORCE_VORTEX', 
     units.inch(42), units.inch(42), units.inch(12), 0, 'CEILING'),
    ('VENT_CEILING', "Ceiling Vent", "HVAC ceiling vent", 'MESH_GRID', 
     units.inch(24), units.inch(24), units.inch(2), 0, 'CEILING'),
    ('SMOKE_DETECTOR', "Smoke Detector", "Smoke/fire detector", 'ERROR', 
     units.inch(5), units.inch(5), units.inch(2), 0, 'CEILING'),
    ('CO_DETECTOR', "CO Detector", "Carbon monoxide detector", 'ERROR', 
     units.inch(5), units.inch(5), units.inch(2), 0, 'CEILING'),
    ('SPRINKLER', "Fire Sprinkler", "Fire sprinkler head", 'OUTLINER_DATA_LIGHTPROBE', 
     units.inch(3), units.inch(3), units.inch(4), 0, 'CEILING'),
    ('EXHAUST_FAN', "Exhaust Fan", "Bathroom/kitchen exhaust fan", 'FORCE_VORTEX', 
     units.inch(10), units.inch(10), units.inch(6), 0, 'CEILING'),
]

MISC_OBSTACLES = [
    ('CUSTOM_RECT', "Custom Rectangle", "Custom rectangular obstacle", 'MESH_PLANE', 
     units.inch(12), units.inch(12), units.inch(2), units.inch(36), 'ANY'),
    ('CUSTOM_CIRCLE', "Custom Circle", "Custom circular obstacle", 'MESH_CIRCLE', 
     units.inch(6), units.inch(6), units.inch(2), units.inch(36), 'ANY'),
    ('PIPE_VERTICAL', "Vertical Pipe", "Vertical pipe/conduit", 'META_CAPSULE', 
     units.inch(4), units.inch(96), units.inch(4), 0, 'ANY'),
    ('PIPE_HORIZONTAL', "Horizontal Pipe", "Horizontal pipe/conduit", 'META_CAPSULE', 
     units.inch(48), units.inch(4), units.inch(4), units.inch(84), 'WALL'),
    ('COLUMN', "Column/Post", "Structural column or post", 'MESH_CYLINDER', 
     units.inch(12), units.inch(96), units.inch(12), 0, 'FLOOR'),
    ('BEAM', "Beam", "Structural beam", 'MESH_CUBE', 
     units.inch(48), units.inch(12), units.inch(6), units.inch(84), 'CEILING'),
]

# Combine all obstacles for enum
def get_obstacle_items(self, context):
    """Generate enum items for obstacle type selection."""
    items = []
    
    # Add category headers and obstacles
    items.append(('HEADER_WALL', "── Wall Obstacles ──", "", 'NONE', 0))
    for i, obs in enumerate(WALL_OBSTACLES):
        items.append((obs[0], obs[1], obs[2], obs[3], i + 1))
    
    items.append(('HEADER_FLOOR', "── Floor Obstacles ──", "", 'NONE', 100))
    for i, obs in enumerate(FLOOR_OBSTACLES):
        items.append((obs[0], obs[1], obs[2], obs[3], 100 + i + 1))
    
    items.append(('HEADER_CEILING', "── Ceiling Obstacles ──", "", 'NONE', 200))
    for i, obs in enumerate(CEILING_OBSTACLES):
        items.append((obs[0], obs[1], obs[2], obs[3], 200 + i + 1))
    
    items.append(('HEADER_MISC', "── Misc Obstacles ──", "", 'NONE', 300))
    for i, obs in enumerate(MISC_OBSTACLES):
        items.append((obs[0], obs[1], obs[2], obs[3], 300 + i + 1))
    
    return items


def get_obstacle_data(obstacle_id):
    """Get obstacle data tuple by ID."""
    all_obstacles = WALL_OBSTACLES + FLOOR_OBSTACLES + CEILING_OBSTACLES + MISC_OBSTACLES
    for obs in all_obstacles:
        if obs[0] == obstacle_id:
            return obs
    return None


def update_obstacle_type(self, context):
    """Update dimensions when obstacle type changes."""
    obs_data = get_obstacle_data(self.obstacle_type)
    if obs_data and not obs_data[0].startswith('HEADER_'):
        self.obstacle_width = obs_data[4]
        self.obstacle_height = obs_data[5]
        self.obstacle_depth = obs_data[6]
        self.obstacle_height_from_floor = obs_data[7]


# =============================================================================
# PROPERTY GROUPS
# =============================================================================

class Obstacles_Scene_Props(PropertyGroup):
    """Scene-level obstacle properties."""
    
    obstacle_type: EnumProperty(
        name="Obstacle Type",
        description="Type of obstacle to place",
        items=get_obstacle_items,
        update=update_obstacle_type
    )  # type: ignore
    
    obstacle_width: FloatProperty(
        name="Width",
        description="Obstacle width",
        default=units.inch(2.75),
        min=units.inch(0.5),
        max=units.inch(120),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    obstacle_height: FloatProperty(
        name="Height",
        description="Obstacle height",
        default=units.inch(4.5),
        min=units.inch(0.5),
        max=units.inch(120),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    obstacle_depth: FloatProperty(
        name="Depth",
        description="Obstacle depth (into wall/floor)",
        default=units.inch(2),
        min=units.inch(0.25),
        max=units.inch(24),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    obstacle_height_from_floor: FloatProperty(
        name="Height from Floor",
        description="Height of obstacle center from floor (for wall obstacles)",
        default=units.inch(12),
        min=0,
        max=units.inch(120),
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    show_obstacle_dimensions: BoolProperty(
        name="Show Dimensions",
        description="Show obstacle dimensions in the UI",
        default=True
    )  # type: ignore
    
    
    def get_obstacle_data(self):
        """Get obstacle data tuple"""
        all_obstacles = WALL_OBSTACLES + FLOOR_OBSTACLES + CEILING_OBSTACLES + MISC_OBSTACLES
        for obs in all_obstacles:
            if obs[0] == self.obstacle_type:
                return obs
        return None

    def draw_obstacle_ui(self, layout, context):
        """Draw the obstacle selection UI."""
        col = layout.column(align=True)
        
        # Obstacle type selector
        col.prop(self, "obstacle_type", text="")
        
        # Don't allow placing header items
        if self.obstacle_type.startswith('HEADER_'):
            col.label(text="Select an obstacle type", icon='INFO')
            return
        
        col.separator()
        
        # Place button
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("home_builder_obstacles.place_obstacle", 
                    text="Place Obstacle", icon='ADD')
        
        # Dimensions
        if self.show_obstacle_dimensions:
            box = layout.box()
            box.label(text="Dimensions:", icon='ARROW_LEFTRIGHT')
            
            col = box.column(align=True)
            col.use_property_split = True
            col.use_property_decorate = False
            
            col.prop(self, "obstacle_width", text="Width")
            col.prop(self, "obstacle_height", text="Height")
            col.prop(self, "obstacle_depth", text="Depth")
            
            # Show height from floor for wall obstacles
            obs_data = get_obstacle_data(self.obstacle_type)
            if obs_data and obs_data[8] == 'WALL':
                col.prop(self, "obstacle_height_from_floor", text="From Floor")
    
    @classmethod
    def register(cls):
        bpy.types.Scene.hb_obstacles = PointerProperty(
            name="Obstacle Props",
            description="Home Builder Obstacle Properties",
            type=cls,
        )
    
    @classmethod
    def unregister(cls):
        if hasattr(bpy.types.Scene, 'hb_obstacles'):
            del bpy.types.Scene.hb_obstacles


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    Obstacles_Scene_Props,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    Obstacles_Scene_Props.register()


def unregister():
    Obstacles_Scene_Props.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
