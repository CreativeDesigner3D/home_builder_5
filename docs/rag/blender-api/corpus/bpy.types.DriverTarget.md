<!-- source: Blender Python API reference 5.2 / bpy.types.DriverTarget.html -->

<a id="drivertarget-bpy-struct"></a>

# DriverTarget(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.DriverTarget"></a>

### class bpy.types.DriverTarget(bpy_struct)

Source of input values for driver variables

<a id="bpy.types.DriverTarget.bone_target"></a>

#### bpy.types.DriverTarget.bone_target

Name of PoseBone to use as target (default “”, never None)

**Type:**

str

<a id="bpy.types.DriverTarget.context_property"></a>

#### bpy.types.DriverTarget.context_property

Type of a context-dependent data-block to access property from (default `'ACTIVE_SCENE'`)

- `ACTIVE_SCENE`
  Active Scene – Currently evaluating scene.
- `ACTIVE_VIEW_LAYER`
  Active View Layer – Currently evaluating view layer.

**Type:**

Literal[‘ACTIVE_SCENE’, ‘ACTIVE_VIEW_LAYER’]

<a id="bpy.types.DriverTarget.data_path"></a>

#### bpy.types.DriverTarget.data_path

RNA Path (from ID-block) to property used (default “”, never None)

**Type:**

str

<a id="bpy.types.DriverTarget.fallback_value"></a>

#### bpy.types.DriverTarget.fallback_value

The value to use if the data path cannot be resolved (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.DriverTarget.id"></a>

#### bpy.types.DriverTarget.id

ID-block that the specific property used can be found from (id_type property must be set first)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.DriverTarget.id_type"></a>

#### bpy.types.DriverTarget.id_type

Type of ID-block that can be used (default `'OBJECT'`)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.DriverTarget.is_fallback_used"></a>

#### bpy.types.DriverTarget.is_fallback_used

Indicates that the most recent variable evaluation used the fallback value (default False, readonly)

**Type:**

bool

<a id="bpy.types.DriverTarget.rotation_mode"></a>

#### bpy.types.DriverTarget.rotation_mode

Mode for calculating rotation channel values (default `'AUTO'`)

**Type:**

Literal[[Driver Target Rotation Mode Items](bpy_types_enum_items/driver_target_rotation_mode_items.md#rna-enum-driver-target-rotation-mode-items)]

<a id="bpy.types.DriverTarget.transform_space"></a>

#### bpy.types.DriverTarget.transform_space

Space in which transforms are used (default `'WORLD_SPACE'`)

- `WORLD_SPACE`
  World Space – Transforms include effects of parenting/restpose and constraints.
- `TRANSFORM_SPACE`
  Transform Space – Transforms don’t include parenting/restpose or constraints.
- `LOCAL_SPACE`
  Local Space – Transforms include effects of constraints but not parenting/restpose.

**Type:**

Literal[‘WORLD_SPACE’, ‘TRANSFORM_SPACE’, ‘LOCAL_SPACE’]

<a id="bpy.types.DriverTarget.transform_type"></a>

#### bpy.types.DriverTarget.transform_type

Driver variable type (default `'LOC_X'`)

**Type:**

Literal[‘LOC_X’, ‘LOC_Y’, ‘LOC_Z’, ‘ROT_X’, ‘ROT_Y’, ‘ROT_Z’, ‘ROT_W’, ‘SCALE_X’, ‘SCALE_Y’, ‘SCALE_Z’, ‘SCALE_AVG’]

<a id="bpy.types.DriverTarget.use_fallback_value"></a>

#### bpy.types.DriverTarget.use_fallback_value

Use the fallback value if the data path cannot be resolved, instead of failing to evaluate the driver (default False)

**Type:**

bool

<a id="bpy.types.DriverTarget.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DriverTarget.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DriverTarget.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DriverTarget.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`DriverVariable.targets`](bpy.types.DriverVariable.md#bpy.types.DriverVariable.targets "bpy.types.DriverVariable.targets") |  |
