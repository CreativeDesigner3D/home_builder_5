# Home Builder 5 - Technical Documentation

This document provides technical details about the Home Builder 5 Blender add-on architecture for developers.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Core Modules](#core-modules)
3. [Type System](#type-system)
4. [Custom Properties & Markers](#custom-properties--markers)
5. [Geometry Nodes](#geometry-nodes)
6. [Operators](#operators)
7. [UI System](#ui-system)
8. [Product Libraries](#product-libraries)
9. [Layout Views System](#layout-views-system)
10. [Coding Conventions](#coding-conventions)

---

## Project Structure

```
home_builder_5/
├── __init__.py              # Main registration, addon metadata
├── hb_types.py              # Core type classes (GeoNode wrappers)
├── hb_props.py              # Blender PropertyGroups
├── hb_utils.py              # Utility functions
├── hb_layouts.py            # Layout view system
├── hb_placement.py          # Object placement logic
├── hb_snap.py               # Snapping system
├── hb_project.py            # Project management
├── hb_driver_functions.py   # Custom driver functions
├── units.py                 # Unit conversion (inch, foot, meter)
├── ops.py                   # General operators
│
├── operators/               # Operator modules
│   ├── walls.py             # Wall drawing operators
│   ├── doors_windows.py     # Door/window placement
│   ├── layouts.py           # Layout view operators
│   └── rooms.py             # Room management operators
│
├── ui/                      # UI panels
│   ├── view3d_sidebar.py    # Legacy sidebar (minimal)
│   ├── layouts_ui.py        # Main UI panels
│   ├── menus.py             # Context menus
│   └── menu_apend.py        # Menu extensions
│
├── product_libraries/       # Cabinet product systems
│   ├── frameless/           # European frameless cabinets
│   ├── face_frame/          # Traditional face frame cabinets
│   └── closets/             # Closet systems
│
├── geometry_nodes/          # .blend files with geometry node setups
│   ├── GeoNodeWall.blend
│   ├── GeoNodeCutpart.blend
│   ├── GeoNodeDimension.blend
│   ├── GeoNodeHardware.blend
│   └── CabinetPartModifiers/
│
└── assets/                  # Asset libraries
    ├── decorations/
    └── materials/
```

---

## Core Modules

### `__init__.py`
Main entry point. Handles addon registration/unregistration. Imports all submodules.

### `hb_types.py`
Contains wrapper classes for geometry node objects. These provide a Pythonic interface to create and manipulate geometry node-based objects.

### `hb_props.py`
Defines Blender PropertyGroups:
- `Home_Builder_Scene_Props` - Scene-level settings (wall height, thickness, tabs)
- `Home_Builder_Object_Props` - Object-level properties
- `Calculator` / `Calculator_Prompt` - Dimension calculator system

### `hb_utils.py`
Utility functions for:
- Driver management
- Object manipulation
- Collection handling
- File operations

### `hb_layouts.py`
Layout view system for 2D documentation:
- `LayoutView` base class
- `ElevationView`, `PlanView`, `ThreeDView`, `MultiView` subclasses
- Paper size management
- Camera setup for orthographic views

### `hb_placement.py`
Handles object placement logic including:
- Wall placement
- Cabinet placement on walls
- Snapping during placement

### `hb_snap.py`
Custom snapping system for:
- Wall endpoints
- Cabinet edges
- Grid snapping

### `units.py`
Unit conversion helpers:
```python
from .units import inch, foot, meter
height = inch(96)  # Returns 96 inches in Blender units
```

---

## Type System

### GeoNode Classes (hb_types.py)

All geometry node wrapper classes inherit from `GeoNodeObject`:

```python
class GeoNodeObject:
    obj: bpy.types.Object  # The Blender object
    
    def create(self, name: str)      # Create new object from template
    def set_input(self, name, value) # Set geometry node input
    def get_input(self, name)        # Get geometry node input value
```

**Available Types:**

| Class | Template File | Purpose |
|-------|---------------|---------|
| `GeoNodeWall` | GeoNodeWall.blend | Wall geometry |
| `GeoNodeCage` | GeoNodeCage.blend | Cabinet carcass |
| `GeoNodeCutpart` | GeoNodeCutpart.blend | Cabinet parts (panels, shelves) |
| `GeoNode5PieceDoor` | GeoNode5PieceDoor.blend | 5-piece door construction |
| `GeoNodeHardware` | GeoNodeHardware.blend | Hardware (hinges, pulls) |
| `GeoNodeDimension` | GeoNodeDimension.blend | Dimension annotations |
| `GeoNodeRectangle` | GeoNodeRectangle.blend | Simple rectangle shapes |

### Creating a GeoNode Object
```python
from . import hb_types

# Create a new wall
wall = hb_types.GeoNodeWall()
wall.create("My Wall")
wall.obj.location = (0, 0, 0)
wall.set_input("Length", 2.4384)  # 96 inches in meters
wall.set_input("Height", 2.4384)
wall.set_input("Thickness", 0.1143)  # 4.5 inches
```

---

## Custom Properties & Markers

Objects and scenes use custom properties (stored in `obj["PROPERTY_NAME"]`) as markers:

### Scene Markers

| Property | Type | Description |
|----------|------|-------------|
| `IS_ROOM_SCENE` | bool | Scene is a room (not a layout view) |
| `IS_LAYOUT_VIEW` | bool | Scene is a layout view |
| `IS_ELEVATION_VIEW` | bool | Layout is an elevation view |
| `IS_PLAN_VIEW` | bool | Layout is a floor plan |
| `IS_3D_VIEW` | bool | Layout is a 3D perspective/isometric |
| `IS_MULTI_VIEW` | bool | Layout is a multi-view (plan + elevations) |
| `SOURCE_WALL` | string | Name of source wall (for elevations) |
| `SOURCE_SCENE` | string | Name of source 3D scene |
| `PAPER_SIZE` | string | Paper size (LETTER, LEGAL, etc.) |
| `PAPER_LANDSCAPE` | bool | Landscape orientation |
| `PAPER_DPI` | int | Dots per inch for rendering |

### Object Markers

| Property | Type | Description |
|----------|------|-------------|
| `IS_WALL_BP` | bool | Object is a wall base point |
| `IS_CABINET_BP` | bool | Object is a cabinet base point |
| `IS_DOOR_BP` | bool | Object is a door base point |
| `IS_WINDOW_BP` | bool | Object is a window base point |
| `IS_2D_ANNOTATION` | bool | Object is a 2D annotation (dimension, etc.) |
| `WALL_SIDE` | string | Which side of wall ("LEFT" or "RIGHT") |

### Checking Markers
```python
# Check if object is a wall
if obj.get('IS_WALL_BP'):
    # Handle wall

# Check if scene is a layout view
if context.scene.get('IS_LAYOUT_VIEW'):
    # Handle layout view
```

---

## Geometry Nodes

Geometry node setups are stored in `.blend` files in `geometry_nodes/`.

### Loading Geometry Nodes
```python
from . import hb_utils

# Get path to geometry node file
path = hb_utils.get_addon_path() + "/geometry_nodes/GeoNodeWall.blend"

# Link/append the node group
with bpy.data.libraries.load(path) as (data_from, data_to):
    data_to.node_groups = data_from.node_groups
```

### Geometry Node Inputs
Each geometry node setup has named inputs that can be set via `set_input()`:

**GeoNodeWall:**
- `Length` (float) - Wall length
- `Height` (float) - Wall height
- `Thickness` (float) - Wall thickness

**GeoNodeDimension:**
- `Leader Length` (float) - Distance from measurement to dimension line
- `Text Size` (float) - Dimension text size
- `Arrow Size` (float) - Arrow/tick size

**GeoNodeCutpart:**
- `X Dimension` (float) - Width
- `Y Dimension` (float) - Depth
- `Z Dimension` (float) - Thickness

---

## Operators

### Naming Convention
```
{category}_{type}_OT_{action}
```

Examples:
- `home_builder_walls_OT_draw_walls`
- `home_builder_layouts_OT_create_elevation_view`
- `home_builder_OT_create_room`

### Operator Registration
```python
classes = (
    home_builder_OT_my_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

### Key Operators

**Room Management (`operators/rooms.py`):**
- `home_builder.create_room` - Create new room scene
- `home_builder.switch_room` - Switch to room
- `home_builder.delete_room` - Delete room
- `home_builder.rename_room` - Rename room
- `home_builder.duplicate_room` - Duplicate room

**Walls (`operators/walls.py`):**
- `home_builder_walls.draw_walls` - Interactive wall drawing

**Doors/Windows (`operators/doors_windows.py`):**
- `home_builder_doors_windows.place_door` - Place door on wall
- `home_builder_doors_windows.place_window` - Place window on wall

**Layouts (`operators/layouts.py`):**
- `home_builder_layouts.create_elevation_view` - Create wall elevation
- `home_builder_layouts.create_plan_view` - Create floor plan
- `home_builder_layouts.create_3d_view` - Create 3D view
- `home_builder_layouts.create_multi_view` - Create cabinet group layout
- `home_builder_layouts.add_dimension` - Add dimension in layout view
- `home_builder_layouts.add_dimension_3d` - Add dimension in 3D view

---

## UI System

All UI panels are in `ui/view3d_sidebar.py` under the "Home Builder" category tab.

### Panel Hierarchy

```
Home Builder (tab)
├── Rooms (HOME_BUILDER_PT_rooms)
│
├── Room Layout (HOME_BUILDER_PT_room_layout)
│   ├── Walls (subpanel)
│   ├── Doors & Windows (subpanel)
│   ├── Floor & Ceiling (subpanel)
│   ├── Lighting (subpanel)
│   └── Obstacles (subpanel)
│
├── Product Library (HOME_BUILDER_PT_product_library)
│   └── Library Content (subpanel, hidden header)
│
├── Layout Views (HOME_BUILDER_PT_layout_views)
│   ├── Create Views (subpanel)
│   └── Page Settings (subpanel, only in layout view)
│
├── Annotations (HOME_BUILDER_PT_annotations)
│
└── Settings (HOME_BUILDER_PT_settings)
```

### Panel Visibility
Some panels use `poll()` to control visibility:
```python
@classmethod
def poll(cls, context):
    # Only show when NOT in a layout view
    return not context.scene.get('IS_LAYOUT_VIEW')
```

### Creating Subpanels
```python
class HOME_BUILDER_PT_subpanel(bpy.types.Panel):
    bl_label = "My Subpanel"
    bl_parent_id = "HOME_BUILDER_PT_parent"  # Parent panel ID
    bl_options = {'DEFAULT_CLOSED'}  # Collapsed by default
```

---

## Product Libraries

Each product library (frameless, face_frame, closets) has:
- `__init__.py` - Registration
- `props_*.py` - PropertyGroup with `draw_library_ui()` method
- `ops_*.py` - Library-specific operators (optional)
- `types_*.py` - Type classes (optional)

### Library UI Pattern
```python
class MyLibraryProps(PropertyGroup):
    def draw_library_ui(self, layout, context):
        # Draw library-specific UI
        col = layout.column()
        col.operator("my_library.place_item")
```

---

## Layout Views System

### Creating a Layout View
```python
from . import hb_layouts

# Create elevation view
view = hb_layouts.ElevationView()
view.create_from_wall(wall_obj, source_scene)

# Create plan view
view = hb_layouts.PlanView()
view.create(source_scene)

# Set paper size
view.set_paper_size('LETTER', landscape=True, dpi=300)
```

### Layout View Scene Properties
When in a layout view, these scene properties are available:
- `scene.hb_paper_size` - Paper size enum
- `scene.hb_paper_landscape` - Landscape bool
- `scene.hb_layout_scale` - Scale enum

### Dimension Annotations
Dimensions use a three-click workflow:
1. First point (snaps to vertices)
2. Second point (snaps to vertices)
3. Leader placement (sets dimension line offset)

The dimension is created using `GeoNodeDimension` with:
- Curve endpoint defines dimension length
- `Leader Length` input defines offset from measurement points
- Rotation aligns dimension to view plane

---

## Coding Conventions

### File Naming
- `hb_*.py` - Core modules
- `ops_*.py` - Operators
- `props_*.py` - PropertyGroups
- `types_*.py` - Type classes
- `*_ui.py` - UI panels

### Operator ID Naming
```
{addon_name}.{action}           # General: home_builder.reload_addon
{addon_name}_{module}.{action}  # Module: home_builder_walls.draw_walls
```

### Property Type Hints
Use `# type: ignore` for Blender properties (required for registration):
```python
my_prop: bpy.props.FloatProperty(name="My Property")  # type: ignore
```

### Unit Handling
Always use the `units` module for dimensions:
```python
from .units import inch, foot

wall_height = inch(96)      # 8 feet
wall_thickness = inch(4.5)  # 4.5 inches
```

### Preserving Settings Across Scenes
When creating new scenes, copy unit and snap settings:
```python
# Store from original scene
unit_system = original_scene.unit_settings.system
snap_elements = set(context.tool_settings.snap_elements)

# Apply to new scene
new_scene.unit_settings.system = unit_system
context.tool_settings.snap_elements = snap_elements
```

---

## Quick Reference

### Common Imports
```python
import bpy
from mathutils import Vector, Matrix, Euler
from . import hb_types, hb_utils, units
from .units import inch, foot
```

### Getting Addon Path
```python
addon_path = hb_utils.get_addon_path()
```

### Finding Walls in Scene
```python
walls = [obj for obj in context.scene.objects if obj.get('IS_WALL_BP')]
```

### Finding Cabinets on Wall
```python
cabinets = [obj for obj in context.scene.objects 
            if obj.get('IS_CABINET_BP') and obj.parent == wall_obj]
```

### Switching Scenes
```python
context.window.scene = bpy.data.scenes['Room 1']
```

---

## Version History

- **v5.0** - Complete rewrite with geometry nodes
  - New room management system
  - Unified UI in "Home Builder" tab
  - Layout view system with dimensions
  - Multi-view cabinet group layouts
