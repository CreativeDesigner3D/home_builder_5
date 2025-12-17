"""
Home Builder Project Management

This module handles project-level data that persists across all scenes.
Data is stored on the "main scene" which is tagged with IS_MAIN_SCENE.

Usage:
    from . import hb_project
    
    # Get project properties (finds/creates main scene tag if needed)
    project = hb_project.get_project_props(context)
    print(project.project_name)
    
    # Get main scene
    main = hb_project.get_main_scene(context)
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    PointerProperty,
)


# =============================================================================
# PROJECT PROPERTIES
# =============================================================================

class Home_Builder_Project_Props(PropertyGroup):
    """
    Project-level properties stored on the main scene.
    These persist across all room scenes in the project.
    """
    
    # Project identification
    project_name: StringProperty(
        name="Project Name",
        description="Name of the project",
        default="New Project"
    )  # type: ignore
    
    project_number: StringProperty(
        name="Project Number",
        description="Project number or ID",
        default=""
    )  # type: ignore
    
    # Designer info
    designer_name: StringProperty(
        name="Designer",
        description="Name of the designer",
        default=""
    )  # type: ignore
    
    designer_phone: StringProperty(
        name="Designer Phone",
        description="Designer phone number",
        default=""
    )  # type: ignore
    
    designer_email: StringProperty(
        name="Designer Email",
        description="Designer email address",
        default=""
    )  # type: ignore
    
    # Client info
    client_name: StringProperty(
        name="Client Name",
        description="Client name",
        default=""
    )  # type: ignore
    
    client_address: StringProperty(
        name="Address",
        description="Client street address",
        default=""
    )  # type: ignore
    
    client_city: StringProperty(
        name="City",
        description="Client city",
        default=""
    )  # type: ignore
    
    client_state: StringProperty(
        name="State",
        description="Client state/province",
        default=""
    )  # type: ignore
    
    client_zip: StringProperty(
        name="Zip",
        description="Client zip/postal code",
        default=""
    )  # type: ignore
    
    client_phone: StringProperty(
        name="Phone",
        description="Client phone number",
        default=""
    )  # type: ignore
    
    client_email: StringProperty(
        name="Email",
        description="Client email address",
        default=""
    )  # type: ignore
    
    # Project notes
    project_notes: StringProperty(
        name="Notes",
        description="Project notes",
        default=""
    )  # type: ignore
    
    # Project dates
    project_date: StringProperty(
        name="Date",
        description="Project date",
        default=""
    )  # type: ignore
    
    @classmethod
    def register(cls):
        bpy.types.Scene.hb_project = PointerProperty(
            name="Home Builder Project",
            description="Project-level properties",
            type=cls,
        )
    
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_project


# =============================================================================
# MAIN SCENE MANAGEMENT
# =============================================================================

def get_main_scene(context=None, create_tag=True):
    """
    Get the main scene that stores project-level data.
    
    Args:
        context: Blender context (optional, uses bpy.context if None)
        create_tag: If True, tags the first available scene as main if none found
    
    Returns:
        The main scene, or None if not found and create_tag=False
    """
    # Look for a scene with the main flag
    for scene in bpy.data.scenes:
        if scene.get('IS_MAIN_SCENE'):
            return scene
    
    # No main scene found
    if not create_tag:
        return None
    
    # Tag a scene as main - prefer first room scene, otherwise first scene
    room_scenes = get_room_scenes()
    if room_scenes:
        main = room_scenes[0]
    elif bpy.data.scenes:
        main = bpy.data.scenes[0]
    else:
        return None
    
    main['IS_MAIN_SCENE'] = True
    return main


def get_project_props(context=None):
    """
    Get project properties from the main scene.
    
    Args:
        context: Blender context (optional)
    
    Returns:
        Home_Builder_Project_Props instance
    """
    main = get_main_scene(context, create_tag=True)
    if main:
        return main.hb_project
    return None


def ensure_main_scene(context=None):
    """
    Ensure a main scene is tagged. Call this on file load.
    
    Args:
        context: Blender context (optional)
    
    Returns:
        The main scene
    """
    return get_main_scene(context, create_tag=True)


def is_main_scene(scene):
    """Check if a scene is the main scene."""
    return scene.get('IS_MAIN_SCENE', False)


def set_main_scene(scene):
    """
    Set a scene as the main scene.
    Removes the tag from any other scene first.
    """
    # Remove tag from all scenes
    for s in bpy.data.scenes:
        if 'IS_MAIN_SCENE' in s:
            del s['IS_MAIN_SCENE']
    
    # Tag the new main scene
    scene['IS_MAIN_SCENE'] = True


def is_room_scene(scene):
    """Check if a scene is a regular room scene (not layout or detail)."""
    if scene.get('IS_LAYOUT_VIEW'):
        return False
    if scene.get('IS_DETAIL_VIEW'):
        return False
    return True


def get_room_scenes():
    """Get all room scenes (excluding layout and detail scenes)."""
    return [s for s in bpy.data.scenes if is_room_scene(s)]


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    Home_Builder_Project_Props,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    Home_Builder_Project_Props.register()


def unregister():
    Home_Builder_Project_Props.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
