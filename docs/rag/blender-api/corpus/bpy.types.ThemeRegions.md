<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeRegions.html -->

<a id="themeregions-bpy-struct"></a>

# ThemeRegions(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeRegions"></a>

### class bpy.types.ThemeRegions(bpy_struct)

Theme settings for regions that are common among editors

<a id="bpy.types.ThemeRegions.asset_shelf"></a>

#### bpy.types.ThemeRegions.asset_shelf

(readonly, never None)

**Type:**

[`ThemeRegionsAssetShelf`](bpy.types.ThemeRegionsAssetShelf.md#bpy.types.ThemeRegionsAssetShelf "bpy.types.ThemeRegionsAssetShelf")

<a id="bpy.types.ThemeRegions.channels"></a>

#### bpy.types.ThemeRegions.channels

(readonly, never None)

**Type:**

[`ThemeRegionsChannels`](bpy.types.ThemeRegionsChannels.md#bpy.types.ThemeRegionsChannels "bpy.types.ThemeRegionsChannels")

<a id="bpy.types.ThemeRegions.scrubbing"></a>

#### bpy.types.ThemeRegions.scrubbing

(readonly, never None)

**Type:**

[`ThemeRegionsScrubbing`](bpy.types.ThemeRegionsScrubbing.md#bpy.types.ThemeRegionsScrubbing "bpy.types.ThemeRegionsScrubbing")

<a id="bpy.types.ThemeRegions.sidebars"></a>

#### bpy.types.ThemeRegions.sidebars

(readonly, never None)

**Type:**

[`ThemeRegionsSidebars`](bpy.types.ThemeRegionsSidebars.md#bpy.types.ThemeRegionsSidebars "bpy.types.ThemeRegionsSidebars")

<a id="bpy.types.ThemeRegions.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeRegions.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeRegions.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeRegions.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.regions`](bpy.types.Theme.md#bpy.types.Theme.regions "bpy.types.Theme.regions") |  |
