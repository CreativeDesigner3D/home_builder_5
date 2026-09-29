<!-- source: Blender Python API reference 5.2 / bpy.types.BoneColor.html -->

<a id="bonecolor-bpy-struct"></a>

# BoneColor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BoneColor"></a>

### class bpy.types.BoneColor(bpy_struct)

Theme color or custom color of a bone

<a id="bpy.types.BoneColor.custom"></a>

#### bpy.types.BoneColor.custom

The custom bone colors, used when palette is ‘CUSTOM’ (readonly, never None)

**Type:**

[`ThemeBoneColorSet`](bpy.types.ThemeBoneColorSet.md#bpy.types.ThemeBoneColorSet "bpy.types.ThemeBoneColorSet")

<a id="bpy.types.BoneColor.is_custom"></a>

#### bpy.types.BoneColor.is_custom

A color palette is user-defined, instead of using a theme-defined one (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneColor.palette"></a>

#### bpy.types.BoneColor.palette

Color palette to use (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’, ‘THEME01’, ‘THEME02’, ‘THEME03’, ‘THEME04’, ‘THEME05’, ‘THEME06’, ‘THEME07’, ‘THEME08’, ‘THEME09’, ‘THEME10’, ‘THEME11’, ‘THEME12’, ‘THEME13’, ‘THEME14’, ‘THEME15’, ‘THEME16’, ‘THEME17’, ‘THEME18’, ‘THEME19’, ‘THEME20’, ‘CUSTOM’]

<a id="bpy.types.BoneColor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoneColor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoneColor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoneColor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Bone.color`](bpy.types.Bone.md#bpy.types.Bone.color "bpy.types.Bone.color") - [`EditBone.color`](bpy.types.EditBone.md#bpy.types.EditBone.color "bpy.types.EditBone.color") | - [`PoseBone.color`](bpy.types.PoseBone.md#bpy.types.PoseBone.color "bpy.types.PoseBone.color") |
