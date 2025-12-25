import bpy

def run_calc_fix(context, obj=None):
    """
    Workaround for Blender bug #133392 - grandchild drivers not updating.
    
    This function forces all drivers in an object hierarchy to recalculate
    by using frame change and touching driven properties.
    
    Args:
        context: Blender context
        obj: Optional object to update (updates all descendants)
             If None, updates all objects in the scene
    """
    if obj:
        objects_to_update = [obj] + list(obj.children_recursive)
    else:
        objects_to_update = list(context.scene.objects)

    home_builder_calculators = []

    # Touch all objects and their modifiers
    for o in objects_to_update:
        # Touch location to mark transform dirty
        o.location = o.location
        for calculator in o.home_builder.calculators:
            home_builder_calculators.append(calculator)
        # Touch geometry node modifiers to force recalc
        for mod in o.modifiers:
            if mod.type == 'NODES':
                mod.show_viewport = mod.show_viewport
    
    for calculator in home_builder_calculators:
        calculator.calculate()

    # Frame change forces complete driver reevaluation
    scene = context.scene
    current_frame = scene.frame_current
    scene.frame_set(current_frame + 1)
    scene.frame_set(current_frame)
    
    # Final view layer update
    context.view_layer.update()

def add_driver_variables(driver,variables):
    for var in variables:
        new_var = driver.driver.variables.new()
        new_var.type = 'SINGLE_PROP'
        new_var.name = var.name
        new_var.targets[0].data_path = var.data_path
        new_var.targets[0].id = var.obj

# =============================================================================
# VIEW MANAGEMENT FUNCTIONS
# =============================================================================

def save_view_state(scene):
    """Save the current 3D view state to a scene's custom properties."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    r3d = space.region_3d
                    
                    # Store view location
                    scene['VIEW_LOCATION_X'] = r3d.view_location.x
                    scene['VIEW_LOCATION_Y'] = r3d.view_location.y
                    scene['VIEW_LOCATION_Z'] = r3d.view_location.z
                    
                    # Store view rotation (as quaternion)
                    scene['VIEW_ROTATION_W'] = r3d.view_rotation.w
                    scene['VIEW_ROTATION_X'] = r3d.view_rotation.x
                    scene['VIEW_ROTATION_Y'] = r3d.view_rotation.y
                    scene['VIEW_ROTATION_Z'] = r3d.view_rotation.z
                    
                    # Store view distance
                    scene['VIEW_DISTANCE'] = r3d.view_distance
                    
                    # Store view perspective mode
                    scene['VIEW_PERSPECTIVE'] = r3d.view_perspective
                    
                    return True
    return False


def restore_view_state(scene):
    """Restore a saved view state from a scene's custom properties."""
    # Check if view state was saved
    if 'VIEW_LOCATION_X' not in scene:
        return False
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    r3d = space.region_3d
                    
                    # Restore view location
                    r3d.view_location.x = scene.get('VIEW_LOCATION_X', 0)
                    r3d.view_location.y = scene.get('VIEW_LOCATION_Y', 0)
                    r3d.view_location.z = scene.get('VIEW_LOCATION_Z', 0)
                    
                    # Restore view rotation
                    from mathutils import Quaternion
                    r3d.view_rotation = Quaternion((
                        scene.get('VIEW_ROTATION_W', 1),
                        scene.get('VIEW_ROTATION_X', 0),
                        scene.get('VIEW_ROTATION_Y', 0),
                        scene.get('VIEW_ROTATION_Z', 0)
                    ))
                    
                    # Restore view distance
                    r3d.view_distance = scene.get('VIEW_DISTANCE', 10)
                    
                    # Restore view perspective
                    r3d.view_perspective = scene.get('VIEW_PERSPECTIVE', 'PERSP')
                    
                    return True
    return False


def set_camera_view():
    """Set the 3D viewport to camera view."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    return True
    return False


def set_top_down_view():
    """Set the 3D viewport to top-down orthographic view."""
    from mathutils import Euler
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'ORTHO'
                    space.region_3d.view_rotation = Euler((0, 0, 0)).to_quaternion()
                    return True
    return False


def frame_all_objects():
    """Frame all objects in the current scene in the 3D viewport."""
    # Select all objects temporarily
    original_selection = [obj for obj in bpy.context.selected_objects]
    original_active = bpy.context.view_layer.objects.active
    
    bpy.ops.object.select_all(action='DESELECT')
    
    has_objects = False
    for obj in bpy.context.scene.objects:
        if obj.type in ('MESH', 'CURVE', 'FONT', 'EMPTY'):
            obj.select_set(True)
            has_objects = True
    
    if has_objects:
        # Frame selected - need proper context with area AND region
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with bpy.context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_selected()
                        break
                break
    
    # Restore selection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selection:
        if obj.name in bpy.context.scene.objects:
            obj.select_set(True)
    if original_active and original_active.name in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = original_active


def is_room_scene(scene):
    """Check if a scene is a room scene (not layout or detail)."""
    if scene.get('IS_LAYOUT_VIEW'):
        return False
    if scene.get('IS_DETAIL_VIEW'):
        return False
    if scene.get('IS_CROWN_DETAIL'):
        return False
    return True
