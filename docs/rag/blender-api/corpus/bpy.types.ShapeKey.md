<!-- source: Blender Python API reference 5.2 / bpy.types.ShapeKey.html -->

<a id="shapekey-bpy-struct"></a>

# ShapeKey(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ShapeKey"></a>

### class bpy.types.ShapeKey(bpy_struct)

Shape key in a shape keys data-block

<a id="bpy.types.ShapeKey.data"></a>

#### bpy.types.ShapeKey.data

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`UnknownType`](bpy.types.UnknownType.md#bpy.types.UnknownType "bpy.types.UnknownType")]

<a id="bpy.types.ShapeKey.frame"></a>

#### bpy.types.ShapeKey.frame

Frame for absolute keys (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.ShapeKey.interpolation"></a>

#### bpy.types.ShapeKey.interpolation

Interpolation type for absolute shape keys (default `'KEY_LINEAR'`)

**Type:**

Literal[‘KEY_LINEAR’, ‘KEY_CARDINAL’, ‘KEY_CATMULL_ROM’, ‘KEY_BSPLINE’]

<a id="bpy.types.ShapeKey.lock_shape"></a>

#### bpy.types.ShapeKey.lock_shape

Protect the shape key from accidental sculpting and editing (default False)

**Type:**

bool

<a id="bpy.types.ShapeKey.mute"></a>

#### bpy.types.ShapeKey.mute

Toggle this shape key (default False)

**Type:**

bool

<a id="bpy.types.ShapeKey.name"></a>

#### bpy.types.ShapeKey.name

Name of Shape Key (default “”, never None)

**Type:**

str

<a id="bpy.types.ShapeKey.points"></a>

#### bpy.types.ShapeKey.points

Optimized access to shape keys point data, when using foreach_get/foreach_set accessors. Warning: Does not support legacy Curve shape keys. (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ShapeKeyPoint`](bpy.types.ShapeKeyPoint.md#bpy.types.ShapeKeyPoint "bpy.types.ShapeKeyPoint")]

<a id="bpy.types.ShapeKey.relative_key"></a>

#### bpy.types.ShapeKey.relative_key

Shape used as a relative key (never None)

**Type:**

[`ShapeKey`](#bpy.types.ShapeKey "bpy.types.ShapeKey")

<a id="bpy.types.ShapeKey.select"></a>

#### bpy.types.ShapeKey.select

Shape key selection state (default False)

**Type:**

bool

<a id="bpy.types.ShapeKey.slider_max"></a>

#### bpy.types.ShapeKey.slider_max

Maximum for slider (in [-10, 10], default 1.0)

**Type:**

float

<a id="bpy.types.ShapeKey.slider_min"></a>

#### bpy.types.ShapeKey.slider_min

Minimum for slider (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ShapeKey.value"></a>

#### bpy.types.ShapeKey.value

Value of shape key at the current frame (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ShapeKey.vertex_group"></a>

#### bpy.types.ShapeKey.vertex_group

Vertex weight group, to blend with basis shape (default “”, never None)

**Type:**

str

<a id="bpy.types.ShapeKey.normals_vertex_get"></a>

#### bpy.types.ShapeKey.normals_vertex_get()

Compute local space vertices’ normals for this shape key

**Returns:**

normals, (dynamic array, in [-1, 1])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ShapeKey.normals_polygon_get"></a>

#### bpy.types.ShapeKey.normals_polygon_get()

Compute local space faces’ normals for this shape key

**Returns:**

normals, (dynamic array, in [-1, 1])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ShapeKey.normals_split_get"></a>

#### bpy.types.ShapeKey.normals_split_get()

Compute local space face corners’ normals for this shape key

**Returns:**

normals, (dynamic array, in [-1, 1])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ShapeKey.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShapeKey.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShapeKey.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShapeKey.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothSettings.rest_shape_key`](bpy.types.ClothSettings.md#bpy.types.ClothSettings.rest_shape_key "bpy.types.ClothSettings.rest_shape_key") - [`Key.key_blocks`](bpy.types.Key.md#bpy.types.Key.key_blocks "bpy.types.Key.key_blocks") - [`Key.reference_key`](bpy.types.Key.md#bpy.types.Key.reference_key "bpy.types.Key.reference_key") - [`Object.active_shape_key`](bpy.types.Object.md#bpy.types.Object.active_shape_key "bpy.types.Object.active_shape_key") | - [`Object.shape_key_add`](bpy.types.Object.md#bpy.types.Object.shape_key_add "bpy.types.Object.shape_key_add") - [`Object.shape_key_remove`](bpy.types.Object.md#bpy.types.Object.shape_key_remove "bpy.types.Object.shape_key_remove") - [`Object.shape_keys_selected`](bpy.types.Object.md#bpy.types.Object.shape_keys_selected "bpy.types.Object.shape_keys_selected") - [`ShapeKey.relative_key`](#bpy.types.ShapeKey.relative_key "bpy.types.ShapeKey.relative_key") |
