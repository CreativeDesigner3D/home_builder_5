<!-- source: Blender Python API reference 5.2 / bpy.types.KeyingSetPath.html -->

<a id="keyingsetpath-bpy-struct"></a>

# KeyingSetPath(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.KeyingSetPath"></a>

### class bpy.types.KeyingSetPath(bpy_struct)

Path to a setting for use in a Keying Set

<a id="bpy.types.KeyingSetPath.array_index"></a>

#### bpy.types.KeyingSetPath.array_index

Index to the specific setting if applicable (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.KeyingSetPath.data_path"></a>

#### bpy.types.KeyingSetPath.data_path

Path to property setting (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyingSetPath.group"></a>

#### bpy.types.KeyingSetPath.group

Name of Action Group to assign setting(s) for this path to (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyingSetPath.group_method"></a>

#### bpy.types.KeyingSetPath.group_method

Method used to define which Group-name to use (default `'NAMED'`)

**Type:**

Literal[[Keyingset Path Grouping Items](bpy_types_enum_items/keyingset_path_grouping_items.md#rna-enum-keyingset-path-grouping-items)]

<a id="bpy.types.KeyingSetPath.id"></a>

#### bpy.types.KeyingSetPath.id

ID-Block that keyframes for Keying Set should be added to (for Absolute Keying Sets only)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.KeyingSetPath.id_type"></a>

#### bpy.types.KeyingSetPath.id_type

Type of ID-block that can be used (default `'OBJECT'`)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.KeyingSetPath.use_entire_array"></a>

#### bpy.types.KeyingSetPath.use_entire_array

When an ‘array/vector’ type is chosen (Location, Rotation, Color, etc.), entire array is to be used (default False)

**Type:**

bool

<a id="bpy.types.KeyingSetPath.use_insertkey_needed"></a>

#### bpy.types.KeyingSetPath.use_insertkey_needed

Only insert keyframes where they’re needed in the relevant F-Curves (default False)

**Type:**

bool

<a id="bpy.types.KeyingSetPath.use_insertkey_override_needed"></a>

#### bpy.types.KeyingSetPath.use_insertkey_override_needed

Override default setting to only insert keyframes where they’re needed in the relevant F-Curves (default False)

**Type:**

bool

<a id="bpy.types.KeyingSetPath.use_insertkey_override_visual"></a>

#### bpy.types.KeyingSetPath.use_insertkey_override_visual

Override default setting to insert keyframes based on ‘visual transforms’ (default False)

**Type:**

bool

<a id="bpy.types.KeyingSetPath.use_insertkey_visual"></a>

#### bpy.types.KeyingSetPath.use_insertkey_visual

Insert keyframes based on ‘visual transforms’ (default False)

**Type:**

bool

<a id="bpy.types.KeyingSetPath.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyingSetPath.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyingSetPath.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyingSetPath.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`KeyingSet.paths`](bpy.types.KeyingSet.md#bpy.types.KeyingSet.paths "bpy.types.KeyingSet.paths") - [`KeyingSetPaths.active`](bpy.types.KeyingSetPaths.md#bpy.types.KeyingSetPaths.active "bpy.types.KeyingSetPaths.active") | - [`KeyingSetPaths.add`](bpy.types.KeyingSetPaths.md#bpy.types.KeyingSetPaths.add "bpy.types.KeyingSetPaths.add") - [`KeyingSetPaths.remove`](bpy.types.KeyingSetPaths.md#bpy.types.KeyingSetPaths.remove "bpy.types.KeyingSetPaths.remove") |
