<!-- source: Blender Python API reference 5.2 / bpy.types.Palette.html -->

<a id="palette-id"></a>

# Palette(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Palette"></a>

### class bpy.types.Palette(ID)

<a id="bpy.types.Palette.colors"></a>

#### bpy.types.Palette.colors

(default None, readonly)

**Type:**

[`PaletteColors`](bpy.types.PaletteColors.md#bpy.types.PaletteColors "bpy.types.PaletteColors")[[`PaletteColor`](bpy.types.PaletteColor.md#bpy.types.PaletteColor "bpy.types.PaletteColor")]

<a id="bpy.types.Palette.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Palette.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Palette.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Palette.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.palettes`](bpy.types.BlendData.md#bpy.types.BlendData.palettes "bpy.types.BlendData.palettes") - [`BlendDataPalettes.new`](bpy.types.BlendDataPalettes.md#bpy.types.BlendDataPalettes.new "bpy.types.BlendDataPalettes.new") | - [`BlendDataPalettes.remove`](bpy.types.BlendDataPalettes.md#bpy.types.BlendDataPalettes.remove "bpy.types.BlendDataPalettes.remove") - [`Paint.palette`](bpy.types.Paint.md#bpy.types.Paint.palette "bpy.types.Paint.palette") |
