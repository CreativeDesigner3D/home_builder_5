<!-- source: Blender Python API reference 5.2 / bpy.types.SequenceTimelineChannel.html -->

<a id="sequencetimelinechannel-bpy-struct"></a>

# SequenceTimelineChannel(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SequenceTimelineChannel"></a>

### class bpy.types.SequenceTimelineChannel(bpy_struct)

<a id="bpy.types.SequenceTimelineChannel.lock"></a>

#### bpy.types.SequenceTimelineChannel.lock

(default False)

**Type:**

bool

<a id="bpy.types.SequenceTimelineChannel.mute"></a>

#### bpy.types.SequenceTimelineChannel.mute

(default False)

**Type:**

bool

<a id="bpy.types.SequenceTimelineChannel.name"></a>

#### bpy.types.SequenceTimelineChannel.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.SequenceTimelineChannel.number"></a>

#### bpy.types.SequenceTimelineChannel.number

Channel number (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SequenceTimelineChannel.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequenceTimelineChannel.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequenceTimelineChannel.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequenceTimelineChannel.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MetaStrip.channels`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.channels "bpy.types.MetaStrip.channels") | - [`SequenceEditor.channels`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.channels "bpy.types.SequenceEditor.channels") |
