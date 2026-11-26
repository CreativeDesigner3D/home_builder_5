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
    EnumProperty,
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

    # Rooms: one scene per room (kitchen and bath jobs).
    # House: one house scene with levels - see hb_house.
    project_kind: EnumProperty(
        name="Project Kind",
        items=[('ROOMS', "Rooms", "Each room is its own scene"),
               ('HOUSE', "House", "The whole house in one scene, on levels")],
        default='ROOMS'
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
        if hasattr(bpy.types.Scene, 'hb_project'):
            del bpy.types.Scene.hb_project


# =============================================================================
# MAIN SCENE MANAGEMENT
# =============================================================================

def get_main_scene(context=None):
    """
    Get the main scene that stores project-level data.
    Always returns a scene if any exist. Will attempt to tag a new
    main scene if none is tagged, but handles restricted (draw) contexts
    gracefully by catching the write error.
    
    Args:
        context: Blender context (optional, uses bpy.context if None)
    
    Returns:
        The main scene, or None if no scenes exist
    """
    # Look for a scene with the main flag
    for scene in bpy.data.scenes:
        if scene.get('IS_MAIN_SCENE'):
            return scene
    
    # No main scene tagged - find best candidate
    room_scenes = get_room_scenes()
    if room_scenes:
        main = room_scenes[0]
    elif bpy.data.scenes:
        main = bpy.data.scenes[0]
    else:
        return None
    
    # Attempt to tag - this will fail silently in draw contexts
    try:
        main['IS_MAIN_SCENE'] = True
    except AttributeError:
        pass
    
    return main


def get_project_props(context=None):
    """
    Get project properties from the main scene.
    
    Args:
        context: Blender context (optional)
    
    Returns:
        Home_Builder_Project_Props instance
    """
    main = get_main_scene(context)
    if main:
        return main.hb_project
    return None


def ensure_main_scene(context=None):
    """
    Ensure a main scene is tagged. Call this on file load or after room deletion.
    
    Args:
        context: Blender context (optional)
    
    Returns:
        The main scene
    """
    main = get_main_scene(context)
    if main:
        return main
    
    # No main scene tagged - tag the first room scene or first scene
    room_scenes = get_room_scenes()
    if room_scenes:
        set_main_scene(room_scenes[0])
        return room_scenes[0]
    elif bpy.data.scenes:
        set_main_scene(bpy.data.scenes[0])
        return bpy.data.scenes[0]
    return None


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


# Registered scene property groups that hold project-level data on the
# main scene (project info, the style pools every room reads). Add-ons
# that keep their own project data on the main scene add their group
# names with register_project_property_group().
PROJECT_PROPERTY_GROUPS = ['hb_project', 'hb_face_frame', 'hb_frameless',
                           'hb_closets']


def register_project_property_group(name):
    """Have migrate_project_data carry another add-on's main-scene group."""
    if name not in PROJECT_PROPERTY_GROUPS:
        PROJECT_PROPERTY_GROUPS.append(name)


def unregister_project_property_group(name):
    if name in PROJECT_PROPERTY_GROUPS:
        PROJECT_PROPERTY_GROUPS.remove(name)


def _migrate_property_groups(old_scene, new_scene):
    """Copy the project-level property groups' stored values as they are.

    Registered properties are not custom properties, so the key copy in
    migrate_project_data never sees them. The raw copy runs no update
    callbacks: setting names through RNA would rename style copies to
    '.001' (products refer to styles by name) and some updates add
    styles of their own. The target's own values for these groups are
    replaced, since project-level reads only ever used the old main's.
    """
    try:
        src = old_scene.bl_system_properties_get()
        dst = new_scene.bl_system_properties_get(do_create=True)
    except AttributeError:
        return
    if src is None or dst is None:
        return
    for name in PROJECT_PROPERTY_GROUPS:
        if name not in src:
            continue
        try:
            if name in dst:
                del dst[name]
            dst[name] = src[name]
        except (TypeError, KeyError) as e:
            print(f"HB5: could not migrate scene group '{name}': {e}")


def migrate_project_data(old_scene, new_scene):
    """
    Copy project-level data from one scene to another.
    Call this BEFORE deleting a main scene so project data (project
    properties, integration IDs, revision counters) survives on the
    scene taking over as main.

    Copies the project-level property groups (PROJECT_PROPERTY_GROUPS)
    as they are, then the scene's custom properties, skipping per-scene
    view state and scene-type flags, and never overwriting custom values
    already set on the target scene.
    """
    if old_scene is None or new_scene is None or old_scene == new_scene:
        return
    _migrate_property_groups(old_scene, new_scene)
    skip_keys = {'IS_MAIN_SCENE', 'IS_LAYOUT_VIEW', 'IS_DETAIL_VIEW',
                 'IS_CROWN_DETAIL', 'home_builder', 'cycles'}
    for key in old_scene.keys():
        if key in skip_keys or key.startswith('VIEW_'):
            continue
        if key in new_scene:
            continue
        try:
            new_scene[key] = old_scene[key]
        except (TypeError, AttributeError) as e:
            print(f"HB5: could not migrate scene key '{key}': {e}")


def is_room_scene(scene):
    """Check if a scene is a regular room scene (not layout or detail)."""
    if scene.get('IS_LAYOUT_VIEW'):
        return False
    if scene.get('IS_DETAIL_VIEW'):
        return False
    return True


def get_settings_scene(context=None):
    """The scene whose per-room defaults apply to the objects being
    worked on right now.

    Ceiling height, and every size derived from it (top cabinet
    clearance, wall cabinet location, the tall and upper cabinet
    heights those produce), belong to the room, not the project: a 108"
    kitchen and a 156" first floor carry different values in the same
    file. Anything acting on the current scene's objects has to read
    that scene's own defaults, or it pushes another room's sizes onto
    them. Layout and detail scenes own no room, so they fall back to
    the main scene.

    Project-global data -- styles, pricing, project properties -- is a
    different question and keeps using get_main_scene().
    """
    ctx = context or bpy.context
    scene = getattr(ctx, 'scene', None)
    if scene is not None and is_room_scene(scene):
        return scene
    return get_main_scene(ctx)


def get_room_scenes():
    """Get all room scenes (excluding layout and detail scenes), sorted by sort_order."""
    rooms = [s for s in bpy.data.scenes if is_room_scene(s)]
    rooms.sort(key=lambda s: s.home_builder.sort_order)
    return rooms


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
