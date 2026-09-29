<!-- source: Blender Python API reference 5.2 / bpy.types.MaskParent.html -->

<a id="maskparent-bpy-struct"></a>

# MaskParent(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaskParent"></a>

### class bpy.types.MaskParent(bpy_struct)

Parenting settings for masking element

<a id="bpy.types.MaskParent.id"></a>

#### bpy.types.MaskParent.id

ID-block to which masking element would be parented to or to its property

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.MaskParent.id_type"></a>

#### bpy.types.MaskParent.id_type

Type of ID-block that can be used (default `'MOVIECLIP'`)

**Type:**

Literal[‘MOVIECLIP’]

<a id="bpy.types.MaskParent.parent"></a>

#### bpy.types.MaskParent.parent

Name of parent object in specified data-block to which parenting happens (default “”, never None)

**Type:**

str

<a id="bpy.types.MaskParent.sub_parent"></a>

#### bpy.types.MaskParent.sub_parent

Name of parent sub-object in specified data-block to which parenting happens (default “”, never None)

**Type:**

str

<a id="bpy.types.MaskParent.type"></a>

#### bpy.types.MaskParent.type

Parent Type (default `'POINT_TRACK'`)

**Type:**

Literal[‘POINT_TRACK’, ‘PLANE_TRACK’]

<a id="bpy.types.MaskParent.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskParent.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskParent.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskParent.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.MaskParent.type "bpy.types.MaskParent.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.MaskParent.type "bpy.types.MaskParent.type")

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
| - [`MaskSplinePoint.parent`](bpy.types.MaskSplinePoint.md#bpy.types.MaskSplinePoint.parent "bpy.types.MaskSplinePoint.parent") |  |
