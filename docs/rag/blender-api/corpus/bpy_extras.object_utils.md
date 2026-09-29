<!-- source: Blender Python API reference 5.2 / bpy_extras.object_utils.html -->

<a id="module-bpy_extras.object_utils"></a>

# bpy_extras submodule (bpy_extras.object_utils)

<a id="bpy_extras.object_utils.add_object_align_init"></a>

### bpy_extras.object_utils.add_object_align_init(context, operator)

Return a matrix using the operator settings and view context.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context to use.
- **operator** ([`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – The operator, checked for location and rotation properties.

**Returns:**

the matrix from the context and settings.

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy_extras.object_utils.object_data_add"></a>

### bpy_extras.object_utils.object_data_add(context, obdata, operator=None, name=None)

Add an object using the view context and preference to initialize the
location, rotation and layer.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context to use.
- **obdata** ([`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – Valid object data to be used for the new object or None.
- **operator** ([`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – The operator, checked for location and rotation properties.
- **name** (str | None) – Optional name

**Returns:**

the newly created object in the scene.

**Return type:**

[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy_extras.object_utils.object_add_grid_scale"></a>

### bpy_extras.object_utils.object_add_grid_scale(context)

Return scale which should be applied on object
data to align it to grid scale.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

The grid scale.

**Return type:**

float

<a id="bpy_extras.object_utils.object_add_grid_scale_apply_operator"></a>

### bpy_extras.object_utils.object_add_grid_scale_apply_operator(operator, context)

Scale an operator’s distance values by the grid size.

**Parameters:**

- **operator** ([`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator")) – The operator to scale.
- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

<a id="bpy_extras.object_utils.world_to_camera_view"></a>

### bpy_extras.object_utils.world_to_camera_view(scene, obj, coord)

Returns the camera space coords for a 3d point.
(also known as: normalized device coordinates - NDC).

Where (0, 0) is the bottom left and (1, 1)
is the top right of the camera frame.
values outside 0-1 are also supported.
A negative ‘z’ value means the point is behind the camera.

Takes shift-x/y, lens angle and sensor size into account
as well as perspective/ortho projections.

**Parameters:**

- **scene** ([`bpy.types.Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")) – Scene to use for frame size.
- **obj** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – Camera object.
- **coord** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – World space location.

**Returns:**

a vector where X and Y map to the view plane and
Z is the depth on the view axis.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy_extras.object_utils.object_report_if_active_shape_key_is_locked"></a>

### bpy_extras.object_utils.object_report_if_active_shape_key_is_locked(obj, operator)

Checks if the active shape key of the specified object is locked, and reports an error if so.

If the object has no shape keys, there is nothing to lock, and the function returns False.

**Parameters:**

- **obj** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – Object to check.
- **operator** ([`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Currently running operator to report the error through. Use None to suppress emitting the message.

**Returns:**

True if the shape key was locked.

**Return type:**

bool

<a id="bpy_extras.object_utils.AddObjectHelper"></a>

### class bpy_extras.object_utils.AddObjectHelper

<a id="bpy_extras.object_utils.AddObjectHelper.align_update_callback"></a>

#### bpy_extras.object_utils.AddObjectHelper.align_update_callback(context)

Update callback for the align property, resets rotation for world alignment.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

<a id="bpy_extras.object_utils.AddObjectHelper.poll"></a>

#### classmethod bpy_extras.object_utils.AddObjectHelper.poll(context)

Check the scene is not linked from a library.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when the scene is local (not linked from a library).

**Return type:**

bool
