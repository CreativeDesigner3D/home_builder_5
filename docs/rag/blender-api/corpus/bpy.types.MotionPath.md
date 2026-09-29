<!-- source: Blender Python API reference 5.2 / bpy.types.MotionPath.html -->

<a id="motionpath-bpy-struct"></a>

# MotionPath(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MotionPath"></a>

### class bpy.types.MotionPath(bpy_struct)

Cache of the world-space positions of an element over a frame range

<a id="bpy.types.MotionPath.color"></a>

#### bpy.types.MotionPath.color

Custom color for motion path before the current frame (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.MotionPath.color_post"></a>

#### bpy.types.MotionPath.color_post

Custom color for motion path after the current frame (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.MotionPath.frame_end"></a>

#### bpy.types.MotionPath.frame_end

End frame of the stored range (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MotionPath.frame_start"></a>

#### bpy.types.MotionPath.frame_start

Starting frame of the stored range (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MotionPath.is_modified"></a>

#### bpy.types.MotionPath.is_modified

Path is being edited (default False)

**Type:**

bool

<a id="bpy.types.MotionPath.length"></a>

#### bpy.types.MotionPath.length

Number of frames cached (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MotionPath.line_thickness"></a>

#### bpy.types.MotionPath.line_thickness

Line thickness for motion path (in [1, 6], default 0)

**Type:**

int

<a id="bpy.types.MotionPath.lines"></a>

#### bpy.types.MotionPath.lines

Use straight lines between keyframe points (default False)

**Type:**

bool

<a id="bpy.types.MotionPath.points"></a>

#### bpy.types.MotionPath.points

Cached positions per frame (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MotionPathVert`](bpy.types.MotionPathVert.md#bpy.types.MotionPathVert "bpy.types.MotionPathVert")]

<a id="bpy.types.MotionPath.use_bone_head"></a>

#### bpy.types.MotionPath.use_bone_head

For PoseBone paths, use the bone head location when calculating this path (default False, readonly)

**Type:**

bool

<a id="bpy.types.MotionPath.use_custom_color"></a>

#### bpy.types.MotionPath.use_custom_color

Use custom color for this motion path (default False)

**Type:**

bool

<a id="bpy.types.MotionPath.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MotionPath.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MotionPath.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MotionPath.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Object.motion_path`](bpy.types.Object.md#bpy.types.Object.motion_path "bpy.types.Object.motion_path") | - [`PoseBone.motion_path`](bpy.types.PoseBone.md#bpy.types.PoseBone.motion_path "bpy.types.PoseBone.motion_path") |
