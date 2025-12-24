"""
Detail Library Management for Home Builder 5

Handles saving and loading 2D details to/from a user library.
Details are stored as individual blend files with embedded thumbnails.
"""

import bpy
import os
import json
from datetime import datetime


def get_user_library_path() -> str:
    """Get the path to the user's detail library folder."""
    # Store in Blender's config folder
    config_path = bpy.utils.user_resource('CONFIG')
    library_path = os.path.join(config_path, "home_builder", "detail_library")
    
    # Create if it doesn't exist
    if not os.path.exists(library_path):
        os.makedirs(library_path)
    
    return library_path


def get_library_index_path() -> str:
    """Get the path to the library index file."""
    return os.path.join(get_user_library_path(), "library_index.json")


def load_library_index() -> dict:
    """Load the library index, or create a new one if it doesn't exist."""
    index_path = get_library_index_path()
    
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return {"details": []}


def save_library_index(index: dict):
    """Save the library index."""
    index_path = get_library_index_path()
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)


def generate_detail_filename(name: str) -> str:
    """Generate a unique filename for a detail."""
    import re
    
    # Clean the name
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{clean_name}_{timestamp}.blend"


def save_detail_to_library(context, name: str, description: str = "") -> tuple:
    """
    Save the current detail view to the user library.
    
    Returns (success: bool, message: str, filepath: str)
    """
    scene = context.scene
    
    # Verify we're in a detail view (either regular or crown detail)
    is_detail = scene.get('IS_DETAIL_VIEW', False)
    is_crown_detail = scene.get('IS_CROWN_DETAIL', False)
    
    if not is_detail and not is_crown_detail:
        return (False, "Not in a detail view", "")
    
    # Get all detail objects in the scene
    detail_objects = []
    for obj in scene.objects:
        # Include curves, text, and other detail objects
        if obj.type in {'CURVE', 'FONT', 'MESH'}:
            detail_objects.append(obj)
    
    if not detail_objects:
        return (False, "No objects in detail view", "")
    
    # Generate filename
    filename = generate_detail_filename(name)
    library_path = get_user_library_path()
    filepath = os.path.join(library_path, filename)
    
    # Create a data block set for the objects we want to save
    # We need to save the objects and their dependencies
    
    # Write the blend file with only the detail objects
    data_blocks = set()
    
    for obj in detail_objects:
        data_blocks.add(obj)
        # Add object data (curve, font, etc)
        if obj.data:
            data_blocks.add(obj.data)
        # Add materials
        if hasattr(obj.data, 'materials'):
            for mat in obj.data.materials:
                if mat:
                    data_blocks.add(mat)
    
    # Write to file
    bpy.data.libraries.write(filepath, data_blocks, fake_user=True)
    
    # Update library index
    index = load_library_index()
    
    # Determine detail type
    detail_type = "crown" if is_crown_detail else "detail"
    
    detail_entry = {
        "name": name,
        "description": description,
        "filename": filename,
        "filepath": filepath,
        "date_created": datetime.now().isoformat(),
        "object_count": len(detail_objects),
        "detail_type": detail_type,
        "is_crown_detail": is_crown_detail,
    }
    
    index["details"].append(detail_entry)
    save_library_index(index)
    
    return (True, f"Saved '{name}' to library", filepath)


def get_library_details(detail_type: str = None) -> list:
    """
    Get list of all details in the library.
    
    Args:
        detail_type: Optional filter - "crown" for crown details only, 
                     "detail" for regular details only, None for all
    """
    index = load_library_index()
    
    # Verify files still exist
    valid_details = []
    library_path = get_user_library_path()
    
    for detail in index.get("details", []):
        filepath = os.path.join(library_path, detail.get("filename", ""))
        if os.path.exists(filepath):
            detail["filepath"] = filepath  # Update path in case library moved
            
            # Filter by type if specified
            if detail_type is not None:
                stored_type = detail.get("detail_type", "detail")
                if stored_type != detail_type:
                    continue
            
            valid_details.append(detail)
    
    return valid_details


def load_detail_from_library(context, filepath: str) -> tuple:
    """
    Load a detail from the library into the current detail view.
    
    Returns (success: bool, message: str, objects: list)
    """
    scene = context.scene
    
    # Verify we're in a detail view
    is_detail = scene.get('IS_DETAIL_VIEW', False)
    is_crown_detail = scene.get('IS_CROWN_DETAIL', False)
    
    if not is_detail and not is_crown_detail:
        return (False, "Not in a detail view", [])
    
    if not os.path.exists(filepath):
        return (False, f"File not found: {filepath}", [])
    
    # Get existing object names to identify new objects after append
    existing_objects = set(obj.name for obj in scene.objects)
    
    # Append all objects from the library file
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    # Link appended objects to scene
    new_objects = []
    for obj in data_to.objects:
        if obj is not None:
            scene.collection.objects.link(obj)
            new_objects.append(obj)
    
    if not new_objects:
        return (False, "No objects found in library file", [])
    
    # Select the new objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in new_objects:
        obj.select_set(True)
    
    if new_objects:
        context.view_layer.objects.active = new_objects[0]
    
    return (True, f"Loaded {len(new_objects)} objects", new_objects)


def get_detail_info(filepath: str) -> dict:
    """
    Get the stored info for a detail by its filepath.
    
    Returns the detail entry dict or empty dict if not found.
    """
    index = load_library_index()
    library_path = get_user_library_path()
    
    for detail in index.get("details", []):
        detail_filepath = os.path.join(library_path, detail.get("filename", ""))
        if detail_filepath == filepath or detail.get("filepath") == filepath:
            return detail
    
    return {}


def delete_detail_from_library(filename: str) -> tuple:
    """
    Delete a detail from the library.
    
    Returns (success: bool, message: str)
    """
    library_path = get_user_library_path()
    filepath = os.path.join(library_path, filename)
    
    # Delete the file
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Update index
    index = load_library_index()
    index["details"] = [d for d in index["details"] if d.get("filename") != filename]
    save_library_index(index)
    
    return (True, f"Deleted {filename}")
