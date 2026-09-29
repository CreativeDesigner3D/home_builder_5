<!-- source: Blender Python API reference 5.2 / bpy.types.RenderSlots.html -->

<a id="renderslots-bpy-prop-collection"></a>

# RenderSlots(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.RenderSlots"></a>

### class bpy.types.RenderSlots(bpy_prop_collection)

Collection of render layers

<a id="bpy.types.RenderSlots.active"></a>

#### bpy.types.RenderSlots.active

Active render slot of the image

**Type:**

[`RenderSlot`](bpy.types.RenderSlot.md#bpy.types.RenderSlot "bpy.types.RenderSlot") | None

<a id="bpy.types.RenderSlots.active_index"></a>

#### bpy.types.RenderSlots.active_index

Active render slot of the image (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.RenderSlots.new"></a>

#### bpy.types.RenderSlots.new(*, name='')

Add a render slot to the image

**Parameters:**

**name** (str) – Name, New name for the render slot (optional, never None)

**Returns:**

Newly created render layer

**Return type:**

[`RenderSlot`](bpy.types.RenderSlot.md#bpy.types.RenderSlot "bpy.types.RenderSlot")

<a id="bpy.types.RenderSlots.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RenderSlots.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RenderSlots.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RenderSlots.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.render_slots`](bpy.types.Image.md#bpy.types.Image.render_slots "bpy.types.Image.render_slots") |  |
