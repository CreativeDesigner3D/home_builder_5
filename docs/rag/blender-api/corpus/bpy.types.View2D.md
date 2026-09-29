<!-- source: Blender Python API reference 5.2 / bpy.types.View2D.html -->

<a id="view2d-bpy-struct"></a>

# View2D(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.View2D"></a>

### class bpy.types.View2D(bpy_struct)

Scroll and zoom for a 2D region

<a id="bpy.types.View2D.region_to_view"></a>

#### bpy.types.View2D.region_to_view(x, y)

Transform region coordinates to 2D view

**Parameters:**

- **x** (float) – x, Region x coordinate (in [-inf, inf])
- **y** (float) – y, Region y coordinate (in [-inf, inf])

**Returns:**

Result, View coordinates (array of 2 items, in [-inf, inf])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.View2D.view_to_region"></a>

#### bpy.types.View2D.view_to_region(x, y, *, clip=True)

Transform 2D view coordinates to region

**Parameters:**

- **x** (float) – x, 2D View x coordinate (in [-inf, inf])
- **y** (float) – y, 2D View y coordinate (in [-inf, inf])
- **clip** (bool) – Clip, Clip coordinates to the visible region (optional)

**Returns:**

Result, Region coordinates (array of 2 items, in [-inf, inf])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.View2D.bl_rna_get_subclass"></a>

#### classmethod bpy.types.View2D.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.View2D.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.View2D.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Region.view2d`](bpy.types.Region.md#bpy.types.Region.view2d "bpy.types.Region.view2d") |  |
