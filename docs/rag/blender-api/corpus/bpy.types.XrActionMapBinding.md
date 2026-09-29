<!-- source: Blender Python API reference 5.2 / bpy.types.XrActionMapBinding.html -->

<a id="xractionmapbinding-bpy-struct"></a>

# XrActionMapBinding(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrActionMapBinding"></a>

### class bpy.types.XrActionMapBinding(bpy_struct)

Binding in an XR action map item

<a id="bpy.types.XrActionMapBinding.axis0_region"></a>

#### bpy.types.XrActionMapBinding.axis0_region

Action execution region for the first input axis (default `'ANY'`)

- `ANY`
  Any – Use any axis region for operator execution.
- `POSITIVE`
  Positive – Use positive axis region only for operator execution.
- `NEGATIVE`
  Negative – Use negative axis region only for operator execution.

**Type:**

Literal[‘ANY’, ‘POSITIVE’, ‘NEGATIVE’]

<a id="bpy.types.XrActionMapBinding.axis1_region"></a>

#### bpy.types.XrActionMapBinding.axis1_region

Action execution region for the second input axis (default `'ANY'`)

- `ANY`
  Any – Use any axis region for operator execution.
- `POSITIVE`
  Positive – Use positive axis region only for operator execution.
- `NEGATIVE`
  Negative – Use negative axis region only for operator execution.

**Type:**

Literal[‘ANY’, ‘POSITIVE’, ‘NEGATIVE’]

<a id="bpy.types.XrActionMapBinding.component_paths"></a>

#### bpy.types.XrActionMapBinding.component_paths

OpenXR component paths (default None, readonly)

**Type:**

[`XrComponentPaths`](bpy.types.XrComponentPaths.md#bpy.types.XrComponentPaths "bpy.types.XrComponentPaths")[[`XrComponentPath`](bpy.types.XrComponentPath.md#bpy.types.XrComponentPath "bpy.types.XrComponentPath")]

<a id="bpy.types.XrActionMapBinding.name"></a>

#### bpy.types.XrActionMapBinding.name

Name of the action map binding (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMapBinding.pose_location"></a>

#### bpy.types.XrActionMapBinding.pose_location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrActionMapBinding.pose_rotation"></a>

#### bpy.types.XrActionMapBinding.pose_rotation

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.XrActionMapBinding.profile"></a>

#### bpy.types.XrActionMapBinding.profile

OpenXR interaction profile path (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMapBinding.threshold"></a>

#### bpy.types.XrActionMapBinding.threshold

Input threshold for button/axis actions (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.XrActionMapBinding.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrActionMapBinding.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrActionMapBinding.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrActionMapBinding.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`XrActionMapBindings.find`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings.find "bpy.types.XrActionMapBindings.find") - [`XrActionMapBindings.new`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings.new "bpy.types.XrActionMapBindings.new") - [`XrActionMapBindings.new_from_binding`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings.new_from_binding "bpy.types.XrActionMapBindings.new_from_binding") - [`XrActionMapBindings.new_from_binding`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings.new_from_binding "bpy.types.XrActionMapBindings.new_from_binding") | - [`XrActionMapBindings.remove`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings.remove "bpy.types.XrActionMapBindings.remove") - [`XrActionMapItem.bindings`](bpy.types.XrActionMapItem.md#bpy.types.XrActionMapItem.bindings "bpy.types.XrActionMapItem.bindings") - [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_binding_create "bpy.types.XrSessionState.action_binding_create") |
