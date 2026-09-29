<!-- source: Blender Python API reference 5.2 / bpy.types.ActionChannelbags.html -->

<a id="actionchannelbags-bpy-prop-collection"></a>

# ActionChannelbags(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ActionChannelbags"></a>

### class bpy.types.ActionChannelbags(bpy_prop_collection)

For each action slot, a list of animation channels that are meant for that slot

<a id="bpy.types.ActionChannelbags.new"></a>

#### bpy.types.ActionChannelbags.new(slot)

Add a new channelbag to the strip, to contain animation channels for a specific slot

**Parameters:**

**slot** ([`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None) – Action Slot, The slot that should be animated by this channelbag (never None)

**Returns:**

Newly created channelbag

**Return type:**

[`ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag")

<a id="bpy.types.ActionChannelbags.remove"></a>

#### bpy.types.ActionChannelbags.remove(channelbag)

Remove the channelbag from the strip

**Parameters:**

**channelbag** ([`ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag") | None) – The channelbag to remove

<a id="bpy.types.ActionChannelbags.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionChannelbags.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionChannelbags.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionChannelbags.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ActionKeyframeStrip.channelbags`](bpy.types.ActionKeyframeStrip.md#bpy.types.ActionKeyframeStrip.channelbags "bpy.types.ActionKeyframeStrip.channelbags") |  |
