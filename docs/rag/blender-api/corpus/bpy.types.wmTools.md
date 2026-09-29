<!-- source: Blender Python API reference 5.2 / bpy.types.wmTools.html -->

<a id="wmtools-bpy-prop-collection"></a>

# wmTools(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.wmTools"></a>

### class bpy.types.wmTools(bpy_prop_collection)

<a id="bpy.types.wmTools.from_space_view3d_mode"></a>

#### bpy.types.wmTools.from_space_view3d_mode(mode, *, create=False)

**Parameters:**

- **mode** (Literal[[Context Mode Items](bpy_types_enum_items/context_mode_items.md#rna-enum-context-mode-items)]) – Object mode
- **create** (bool) – Create, (optional)

**Return type:**

[`WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")

<a id="bpy.types.wmTools.from_space_image_mode"></a>

#### bpy.types.wmTools.from_space_image_mode(mode, *, create=False)

**Parameters:**

- **mode** (Literal[[Space Image Mode All Items](bpy_types_enum_items/space_image_mode_all_items.md#rna-enum-space-image-mode-all-items)]) – Image space mode
- **create** (bool) – Create, (optional)

**Return type:**

[`WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")

<a id="bpy.types.wmTools.from_space_node"></a>

#### bpy.types.wmTools.from_space_node(*, create=False)

**Parameters:**

**create** (bool) – Create, (optional)

**Return type:**

[`WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")

<a id="bpy.types.wmTools.from_space_sequencer"></a>

#### bpy.types.wmTools.from_space_sequencer(mode, *, create=False)

**Parameters:**

- **mode** (Literal[[Space Sequencer View Type Items](bpy_types_enum_items/space_sequencer_view_type_items.md#rna-enum-space-sequencer-view-type-items)]) – Sequencer view type
- **create** (bool) – Create, (optional)

**Return type:**

[`WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")

<a id="bpy.types.wmTools.bl_rna_get_subclass"></a>

#### classmethod bpy.types.wmTools.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.wmTools.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.wmTools.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`WorkSpace.tools`](bpy.types.WorkSpace.md#bpy.types.WorkSpace.tools "bpy.types.WorkSpace.tools") |  |
