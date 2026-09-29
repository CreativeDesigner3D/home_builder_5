<!-- source: Blender Python API reference 5.2 / bpy.types.Curves.html -->

<a id="curves-id"></a>

# Curves(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Curves"></a>

### class bpy.types.Curves(ID)

Hair data-block for hair curves

<a id="bpy.types.Curves.animation_data"></a>

#### bpy.types.Curves.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Curves.attributes"></a>

#### bpy.types.Curves.attributes

Geometry attributes (default None, readonly)

**Type:**

[`AttributeGroupCurves`](bpy.types.AttributeGroupCurves.md#bpy.types.AttributeGroupCurves "bpy.types.AttributeGroupCurves")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.Curves.color_attributes"></a>

#### bpy.types.Curves.color_attributes

Geometry color attributes (default None, readonly)

**Type:**

[`AttributeGroupCurves`](bpy.types.AttributeGroupCurves.md#bpy.types.AttributeGroupCurves "bpy.types.AttributeGroupCurves")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.Curves.curve_offset_data"></a>

#### bpy.types.Curves.curve_offset_data

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`IntAttributeValue`](bpy.types.IntAttributeValue.md#bpy.types.IntAttributeValue "bpy.types.IntAttributeValue")]

<a id="bpy.types.Curves.curves"></a>

#### bpy.types.Curves.curves

All curves in the data-block (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`CurveSlice`](bpy.types.CurveSlice.md#bpy.types.CurveSlice "bpy.types.CurveSlice")]

<a id="bpy.types.Curves.materials"></a>

#### bpy.types.Curves.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.Curves.normals"></a>

#### bpy.types.Curves.normals

The curve normal value at each of the curve’s control points (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FloatVectorValueReadOnly`](bpy.types.FloatVectorValueReadOnly.md#bpy.types.FloatVectorValueReadOnly "bpy.types.FloatVectorValueReadOnly")]

<a id="bpy.types.Curves.points"></a>

#### bpy.types.Curves.points

Control points of all curves (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`CurvePoint`](bpy.types.CurvePoint.md#bpy.types.CurvePoint "bpy.types.CurvePoint")]

<a id="bpy.types.Curves.position_data"></a>

#### bpy.types.Curves.position_data

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FloatVectorAttributeValue`](bpy.types.FloatVectorAttributeValue.md#bpy.types.FloatVectorAttributeValue "bpy.types.FloatVectorAttributeValue")]

<a id="bpy.types.Curves.selection_domain"></a>

#### bpy.types.Curves.selection_domain

(default `'POINT'`)

**Type:**

Literal[[Attribute Curves Domain Items](bpy_types_enum_items/attribute_curves_domain_items.md#rna-enum-attribute-curves-domain-items)]

<a id="bpy.types.Curves.surface"></a>

#### bpy.types.Curves.surface

Mesh object that the curves can be attached to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Curves.surface_collision_distance"></a>

#### bpy.types.Curves.surface_collision_distance

Distance to keep the curves away from the surface (in [1.192e-07, inf], default 0.005)

**Type:**

float

<a id="bpy.types.Curves.surface_uv_map"></a>

#### bpy.types.Curves.surface_uv_map

The name of the attribute on the surface mesh used to define the attachment of each curve (default “”, never None)

**Type:**

str

<a id="bpy.types.Curves.use_mirror_x"></a>

#### bpy.types.Curves.use_mirror_x

Enable symmetry in the X axis (default False)

**Type:**

bool

<a id="bpy.types.Curves.use_mirror_y"></a>

#### bpy.types.Curves.use_mirror_y

Enable symmetry in the Y axis (default False)

**Type:**

bool

<a id="bpy.types.Curves.use_mirror_z"></a>

#### bpy.types.Curves.use_mirror_z

Enable symmetry in the Z axis (default False)

**Type:**

bool

<a id="bpy.types.Curves.use_sculpt_collision"></a>

#### bpy.types.Curves.use_sculpt_collision

Enable collision with the surface while sculpting (default False)

**Type:**

bool

<a id="bpy.types.Curves.add_curves"></a>

#### bpy.types.Curves.add_curves(sizes)

add_curves

**Parameters:**

**sizes** (Sequence[int]) – Sizes, The number of points in each curve (array of 1 items, in [0, inf])

<a id="bpy.types.Curves.remove_curves"></a>

#### bpy.types.Curves.remove_curves(*, indices=(0,))

Remove all curves. If indices are provided, remove only the curves with the given indices.

**Parameters:**

**indices** (Sequence[int]) – Indices, The indices of the curves to remove (array of 1 items, in [0, inf], optional)

<a id="bpy.types.Curves.resize_curves"></a>

#### bpy.types.Curves.resize_curves(sizes, *, indices=(0,))

Resize all existing curves. If indices are provided, resize only the curves with the given indices. If the new size for a curve is smaller, the curve is trimmed. If the new size for a curve is larger, the new end values are default initialized.

**Parameters:**

- **sizes** (Sequence[int]) – Sizes, The number of points in each curve (array of 1 items, in [1, inf])
- **indices** (Sequence[int]) – Indices, The indices of the curves to resize (array of 1 items, in [0, inf], optional)

<a id="bpy.types.Curves.reorder_curves"></a>

#### bpy.types.Curves.reorder_curves(new_indices)

Reorder the curves by the new indices.

**Parameters:**

**new_indices** (Sequence[int]) – New indices, The new index for each of the curves (array of 1 items, in [0, inf])

<a id="bpy.types.Curves.set_types"></a>

#### bpy.types.Curves.set_types(*, type='CATMULL_ROM', indices=(0,))

Set the curve type. If indices are provided, set only the types with the given curve indices.

**Parameters:**

- **type** (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.md#rna-enum-curves-type-items)]) – Type, (optional)
- **indices** (Sequence[int]) – Indices, The indices of the curves to resize (array of 1 items, in [0, inf], optional)

<a id="bpy.types.Curves.unit_test_compare"></a>

#### bpy.types.Curves.unit_test_compare(*, curves=None, threshold=7.1526e-06)

unit_test_compare

**Parameters:**

- **curves** ([`Curves`](#bpy.types.Curves "bpy.types.Curves") | None) – Curves to compare to (optional)
- **threshold** (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)

**Returns:**

Return value, String description of result of comparison (never None)

**Return type:**

str

<a id="bpy.types.Curves.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Curves.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Curves.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Curves.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.curves` - [`BlendData.hair_curves`](bpy.types.BlendData.md#bpy.types.BlendData.hair_curves "bpy.types.BlendData.hair_curves") - [`BlendDataHairCurves.new`](bpy.types.BlendDataHairCurves.md#bpy.types.BlendDataHairCurves.new "bpy.types.BlendDataHairCurves.new") | - [`BlendDataHairCurves.remove`](bpy.types.BlendDataHairCurves.md#bpy.types.BlendDataHairCurves.remove "bpy.types.BlendDataHairCurves.remove") - [`Curves.unit_test_compare`](#bpy.types.Curves.unit_test_compare "bpy.types.Curves.unit_test_compare") |
