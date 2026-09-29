<!-- source: Blender Python API reference 5.2 / bpy.types.MaterialLineArt.html -->

<a id="materiallineart-bpy-struct"></a>

# MaterialLineArt(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaterialLineArt"></a>

### class bpy.types.MaterialLineArt(bpy_struct)

<a id="bpy.types.MaterialLineArt.intersection_priority"></a>

#### bpy.types.MaterialLineArt.intersection_priority

The intersection line will be included into the object with the higher intersection priority value (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.MaterialLineArt.mat_occlusion"></a>

#### bpy.types.MaterialLineArt.mat_occlusion

Faces with this material will behave as if it has set number of layers in occlusion (in [0, 255], default 1)

**Type:**

int

<a id="bpy.types.MaterialLineArt.use_intersection_priority_override"></a>

#### bpy.types.MaterialLineArt.use_intersection_priority_override

Override object and collection intersection priority value (default False)

**Type:**

bool

<a id="bpy.types.MaterialLineArt.use_material_mask"></a>

#### bpy.types.MaterialLineArt.use_material_mask

Use material masks to filter out occluded strokes (default False)

**Type:**

bool

<a id="bpy.types.MaterialLineArt.use_material_mask_bits"></a>

#### bpy.types.MaterialLineArt.use_material_mask_bits

(array of 8 items, default (False, False, False, False, False, False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.MaterialLineArt.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaterialLineArt.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaterialLineArt.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaterialLineArt.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Material.lineart`](bpy.types.Material.md#bpy.types.Material.lineart "bpy.types.Material.lineart") |  |
