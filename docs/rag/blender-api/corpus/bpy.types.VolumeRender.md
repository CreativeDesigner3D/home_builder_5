<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeRender.html -->

<a id="volumerender-bpy-struct"></a>

# VolumeRender(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.VolumeRender"></a>

### class bpy.types.VolumeRender(bpy_struct)

Volume object render settings

<a id="bpy.types.VolumeRender.clipping"></a>

#### bpy.types.VolumeRender.clipping

Value under which voxels are considered empty space to optimize rendering (in [0, 1], default 0.001)

**Type:**

float

<a id="bpy.types.VolumeRender.precision"></a>

#### bpy.types.VolumeRender.precision

Specify volume data precision. Lower values reduce memory consumption at the cost of detail. (default `'HALF'`)

- `FULL`
  Full – Use 32-bit floating-point numbers for all data.
- `HALF`
  Half – Use 16-bit floating-point numbers for all data.
- `VARIABLE`
  Variable – Use variable bit quantization.

**Type:**

Literal[‘FULL’, ‘HALF’, ‘VARIABLE’]

<a id="bpy.types.VolumeRender.space"></a>

#### bpy.types.VolumeRender.space

Specify volume density and step size in object or world space (default `'OBJECT'`)

- `OBJECT`
  Object – Keep volume opacity and detail the same regardless of object scale.
- `WORLD`
  World – Specify volume step size and density in world space.

**Type:**

Literal[‘OBJECT’, ‘WORLD’]

<a id="bpy.types.VolumeRender.step_size"></a>

#### bpy.types.VolumeRender.step_size

Distance between volume samples. Lower values render more detail at the cost of performance. If set to zero, the step size is automatically determined based on voxel size. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeRender.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeRender.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeRender.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeRender.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Volume.render`](bpy.types.Volume.md#bpy.types.Volume.render "bpy.types.Volume.render") |  |
