<!-- source: Blender Python API reference 5.2 / bpy.types.IDOverrideLibrary.html -->

<a id="idoverridelibrary-bpy-struct"></a>

# IDOverrideLibrary(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.IDOverrideLibrary"></a>

### class bpy.types.IDOverrideLibrary(bpy_struct)

Struct gathering all data needed by overridden linked IDs

<a id="bpy.types.IDOverrideLibrary.hierarchy_root"></a>

#### bpy.types.IDOverrideLibrary.hierarchy_root

Library override ID used as root of the override hierarchy this ID is a member of (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.IDOverrideLibrary.is_in_hierarchy"></a>

#### bpy.types.IDOverrideLibrary.is_in_hierarchy

Whether this library override is defined as part of a library hierarchy, or as a single, isolated and autonomous override (default True)

**Type:**

bool

<a id="bpy.types.IDOverrideLibrary.is_system_override"></a>

#### bpy.types.IDOverrideLibrary.is_system_override

Whether this library override exists only for the override hierarchy, or if it is actually editable by the user (default False)

**Type:**

bool

<a id="bpy.types.IDOverrideLibrary.properties"></a>

#### bpy.types.IDOverrideLibrary.properties

List of overridden properties (default None, readonly)

**Type:**

[`IDOverrideLibraryProperties`](bpy.types.IDOverrideLibraryProperties.md#bpy.types.IDOverrideLibraryProperties "bpy.types.IDOverrideLibraryProperties")[[`IDOverrideLibraryProperty`](bpy.types.IDOverrideLibraryProperty.md#bpy.types.IDOverrideLibraryProperty "bpy.types.IDOverrideLibraryProperty")]

<a id="bpy.types.IDOverrideLibrary.reference"></a>

#### bpy.types.IDOverrideLibrary.reference

Linked ID used as reference by this override (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.IDOverrideLibrary.operations_update"></a>

#### bpy.types.IDOverrideLibrary.operations_update()

Update the library override operations based on the differences between this override ID and its reference

<a id="bpy.types.IDOverrideLibrary.reset"></a>

#### bpy.types.IDOverrideLibrary.reset(*, do_hierarchy=True, set_system_override=False)

Reset this override to match again its linked reference ID

**Parameters:**

- **do_hierarchy** (bool) – Also reset all the dependencies of this override to match their reference linked IDs (optional)
- **set_system_override** (bool) – Reset all user-editable overrides as (non-editable) system overrides (optional)

<a id="bpy.types.IDOverrideLibrary.destroy"></a>

#### bpy.types.IDOverrideLibrary.destroy(*, do_hierarchy=True)

Delete this override ID and remap its usages to its linked reference ID instead

**Parameters:**

**do_hierarchy** (bool) – Also delete all the dependencies of this override and remap their usages to their reference linked IDs (optional)

<a id="bpy.types.IDOverrideLibrary.resync"></a>

#### bpy.types.IDOverrideLibrary.resync(scene, *, view_layer=None, residual_storage=None, do_hierarchy_enforce=False, do_whole_hierarchy=False)

Resync the data-block and its sub-hierarchy, or the whole hierarchy if requested

**Parameters:**

- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – The scene to operate in (for contextual things like keeping active object active, ensuring all overridden objects remain instantiated, etc.) (never None)
- **view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – The view layer to operate in (same usage as the `scene` data, in case it is not provided the scene’s collection will be used instead) (optional)
- **residual_storage** ([`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None) – Collection where to store objects that are instantiated in any other collection anymore (garbage collection, will be created if needed and none is provided) (optional)
- **do_hierarchy_enforce** (bool) – Enforce restoring the dependency hierarchy between data-blocks to match the one from the reference linked hierarchy (WARNING: if some ID pointers have been purposely overridden, these will be reset to their default value) (optional)
- **do_whole_hierarchy** (bool) – Resync the whole hierarchy this data-block belongs to, not only its own sub-hierarchy (optional)

**Returns:**

Success, Whether the resync process was successful or not

**Return type:**

bool

<a id="bpy.types.IDOverrideLibrary.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IDOverrideLibrary.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IDOverrideLibrary.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IDOverrideLibrary.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ID.override_library`](bpy.types.ID.md#bpy.types.ID.override_library "bpy.types.ID.override_library") |  |
