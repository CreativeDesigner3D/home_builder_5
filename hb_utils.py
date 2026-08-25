import bpy
from mathutils import Quaternion, Euler

# =============================================================================
# GEOMETRY NODE MODIFIER INPUT ACCESS (Blender 5.1 / 5.2 compatibility)
# =============================================================================
# Blender 5.2 moved geometry-node modifier inputs from ID properties
# (mod["Socket_2"]) to RNA (mod.properties.inputs.Socket_2.value). These
# helpers are the only place that knows both layouts, so call sites stay
# version-agnostic. A missing input raises KeyError on 5.1 and
# AttributeError on 5.2 - catch (KeyError, AttributeError) where needed,
# or use try_get_gn_input for a default instead.
GN_INPUTS_AS_RNA = bpy.app.version >= (5, 2, 0)


def get_gn_input(mod, identifier):
    """Read a geometry node modifier input value by socket identifier."""
    if GN_INPUTS_AS_RNA:
        return getattr(mod.properties.inputs, identifier).value
    return mod[identifier]


def set_gn_input(mod, identifier, value):
    """Write a geometry node modifier input value by socket identifier."""
    if GN_INPUTS_AS_RNA:
        getattr(mod.properties.inputs, identifier).value = value
    else:
        mod[identifier] = value


def try_get_gn_input(mod, identifier, default=None):
    """get_gn_input, returning default when the input is missing (or the
    identifier is empty / the socket has no value, e.g. Geometry)."""
    if not identifier:
        return default
    if GN_INPUTS_AS_RNA:
        item = getattr(mod.properties.inputs, identifier, None)
        return getattr(item, 'value', default) if item is not None else default
    return mod.get(identifier, default)


def gn_input_ui_ref(mod, identifier):
    """(owner, prop_name) pair for layout.prop() on a modifier input,
    or None when the input isn't drawable (missing / no value socket)."""
    if GN_INPUTS_AS_RNA:
        item = getattr(mod.properties.inputs, identifier, None)
        if item is None or not hasattr(item, 'value'):
            return None
        return item, 'value'
    if identifier not in mod.keys():
        return None
    return mod, '["%s"]' % identifier


def gn_input_data_path(mod, identifier):
    """Animatable data path (driver_add / path_resolve) for a geometry
    node modifier input value."""
    if GN_INPUTS_AS_RNA:
        return 'modifiers["%s"].properties.inputs.%s.value' % (mod.name, identifier)
    return 'modifiers["%s"]["%s"]' % (mod.name, identifier)


# =============================================================================
# BASE POINT HELPER FUNCTIONS
# =============================================================================

def get_cabinet_bp(obj):
    """Walk up the parent hierarchy to find the cabinet or part base point object.
    
    Finds objects with IS_FRAMELESS_CABINET_CAGE or IS_FRAMELESS_PRODUCT_CAGE markers.
    """
    if obj is None:
        return None
    if 'IS_FRAMELESS_CABINET_CAGE' in obj or 'IS_FRAMELESS_PRODUCT_CAGE' in obj:
        return obj
    if obj.parent:
        return get_cabinet_bp(obj.parent)
    return None


# A placed product sits ON a wall -- it is parented to one -- but it is
# not part of the wall. Anything walking a wall's children has to know
# where the wall stops and the things standing against it begin, or a
# cabinet gets treated as wall geometry. Two callers ask this now: the
# room dimension overlay (so selecting a cabinet does not label its wall)
# and the room collection sorter (so hiding a linked room's walls does
# not take its cabinets with them).
PRODUCT_ROOT_TAGS = (
    'IS_FACE_FRAME_CABINET_CAGE',
    'IS_FRAMELESS_CABINET_CAGE',
    'IS_CLOSET_STARTER_CAGE',
    'IS_APPLIANCE',
)


def is_product_root(obj, extra_tags=()):
    """True where ``obj`` is the root of a placed product."""
    if obj is None:
        return False
    return any(obj.get(tag) for tag in PRODUCT_ROOT_TAGS) or \
        any(obj.get(tag) for tag in extra_tags)


def get_product_bp(obj):
    """Walk up the parent hierarchy to find the part base point object.
    
    Only finds objects with IS_FRAMELESS_PRODUCT_CAGE marker (not cabinets).
    """
    if obj is None:
        return None
    if 'IS_FRAMELESS_PRODUCT_CAGE' in obj:
        return obj
    if obj.parent:
        return get_product_bp(obj.parent)
    return None


def get_bay_bp(obj):
    """Walk up the parent hierarchy to find the bay base point object."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_BAY_CAGE' in obj:
        return obj
    if obj.parent:
        return get_bay_bp(obj.parent)
    return None


def get_opening_bp(obj):
    """Walk up the parent hierarchy to find the opening base point object."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_OPENING_CAGE' in obj:
        return obj
    if obj.parent:
        return get_opening_bp(obj.parent)
    return None


def get_interior_bp(obj):
    """Walk up the parent hierarchy to find the interior base point object."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_INTERIOR_CAGE' in obj:
        return obj
    if obj.parent:
        return get_interior_bp(obj.parent)
    return None


def get_interior_part_bp(obj):
    """Check if object is an interior part."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_INTERIOR_PART' in obj:
        return obj
    return None


def get_interior_section_bp(obj):
    """Walk up the parent hierarchy to find the interior section base point object."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_INTERIOR_SECTION' in obj:
        return obj
    if obj.parent:
        return get_interior_section_bp(obj.parent)
    return None

def get_appliance_bp(obj):
    """Walk up the parent hierarchy to find the appliance base point object."""
    if obj is None:
        return None
    if 'IS_APPLIANCE' in obj:
        return obj
    if obj.parent:
        return get_appliance_bp(obj.parent)
    return None


def get_wall_bp(obj):
    """Walk up the parent hierarchy to find the wall base point object."""
    if obj is None:
        return None
    if 'IS_WALL_BP' in obj:
        return obj
    if obj.parent:
        return get_wall_bp(obj.parent)
    return None


def delete_obj_and_children(obj):
    """Delete an object and all of its children recursively."""

    if obj is None:
        return
    
    # Collect all objects to delete (children first)
    objects_to_delete = []
    
    def collect_children(o):
        for child in o.children:
            collect_children(child)
        objects_to_delete.append(o)
    
    collect_children(obj)
    
    # Delete all collected objects
    for o in objects_to_delete:
        bpy.data.objects.remove(o, do_unlink=True)


def run_calc_fix(context, obj=None, passes=2):
    """
    Workaround for Blender bug #133392 - grandchild drivers not updating.
    
    This function forces all drivers in an object hierarchy to recalculate
    by using frame change and touching driven properties.
    
    Args:
        context: Blender context
        obj: Optional object to update (updates all descendants)
             If None, updates all objects in the scene
        passes: Number of calculation passes (default 2 for reliability)
    """
    if obj:
        objects_to_update = [obj] + list(obj.children_recursive)
    else:
        objects_to_update = list(context.scene.objects)

    home_builder_calculators = []

    # Collect all calculators
    for o in objects_to_update:
        for calculator in o.home_builder.calculators:
            home_builder_calculators.append(calculator)

    # Run multiple passes to ensure all dependencies resolve
    for _ in range(passes):
        # Touch all objects and their modifiers
        for o in objects_to_update:
            # Touch location to mark transform dirty
            o.location = o.location
            # Touch geometry node modifiers to force recalc
            for mod in o.modifiers:
                if mod.type == 'NODES':
                    mod.show_viewport = mod.show_viewport
        
        # Calculate all calculators
        for calculator in home_builder_calculators:
            calculator.calculate()

        # Frame change forces complete driver reevaluation
        scene = context.scene
        current_frame = scene.frame_current
        scene.frame_set(current_frame + 1)
        scene.frame_set(current_frame)
        
        # Update depsgraph
        context.view_layer.update()
    
    # Force evaluated mesh read to ensure geometry nodes have processed
    depsgraph = context.evaluated_depsgraph_get()
    for o in objects_to_update:
        if o.type == 'MESH':
            try:
                o.evaluated_get(depsgraph)
            except:
                pass


def run_calc_fix_until_stable(context, obj=None, max_passes=5, tolerance=0.0001):
    """
    Run calc fix until dimensions stabilize or max passes reached.
    
    Args:
        context: Blender context
        obj: Optional object to update
        max_passes: Maximum number of passes before giving up
        tolerance: Tolerance for dimension comparison (in meters)
    
    Returns:
        Number of passes needed, or -1 if didn't stabilize
    """
    if obj:
        objects_to_update = [obj] + list(obj.children_recursive)
    else:
        objects_to_update = list(context.scene.objects)
    
    def get_dimensions_hash():
        """Get a hash of all object dimensions for comparison."""
        dims = []
        for o in objects_to_update:
            if o.type == 'MESH':
                dims.append((o.name, tuple(o.dimensions)))
        return dims
    
    previous_dims = None
    
    for pass_num in range(max_passes):
        run_calc_fix(context, obj, passes=1)
        current_dims = get_dimensions_hash()
        
        if previous_dims is not None:
            # Check if dimensions have stabilized
            stable = True
            for (name1, d1), (name2, d2) in zip(previous_dims, current_dims):
                for v1, v2 in zip(d1, d2):
                    if abs(v1 - v2) > tolerance:
                        stable = False
                        break
                if not stable:
                    break
            
            if stable:
                return pass_num + 1
        
        previous_dims = current_dims
    
    return -1  # Didn't stabilize

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

                    # Store viewport shading so layout views can switch to
                    # solid without losing the room scene's shading
                    scene['VIEW_SHADING_TYPE'] = space.shading.type
                    scene['VIEW_SHADING_COLOR_TYPE'] = space.shading.color_type
                    scene['VIEW_SHADING_XRAY'] = space.shading.show_xray

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

                    # Restore viewport shading if it was saved
                    if 'VIEW_SHADING_TYPE' in scene:
                        space.shading.type = scene['VIEW_SHADING_TYPE']
                        space.shading.color_type = scene.get('VIEW_SHADING_COLOR_TYPE', space.shading.color_type)
                        space.shading.show_xray = scene.get('VIEW_SHADING_XRAY', False)

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
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'ORTHO'
                    space.region_3d.view_rotation = Euler((0, 0, 0)).to_quaternion()
                    return True
    return False


def set_plan_view(distance=8.0):
    """Set the 3D viewport to a plan view centered on the origin.

    Unlike set_top_down_view this also resets the pan and zoom, for
    scenes that start out empty and so have nothing to frame.
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    r3d = space.region_3d
                    r3d.view_perspective = 'ORTHO'
                    r3d.view_rotation = Euler((0, 0, 0)).to_quaternion()
                    r3d.view_location = (0.0, 0.0, 0.0)
                    r3d.view_distance = distance
                    return True
    return False


def set_layout_shading():
    """Set the 3D viewport to solid shading for 2D layout and detail scenes."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.color_type = 'OBJECT'
                    space.shading.show_xray = False
                    # Keep viewport navigation from moving the page camera
                    space.lock_camera = False
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
