<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilFrames.html -->

<a id="greasepencilframes-bpy-prop-collection"></a>

# GreasePencilFrames(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.GreasePencilFrames"></a>

### class bpy.types.GreasePencilFrames(bpy_prop_collection)

Collection of Grease Pencil frames

<a id="bpy.types.GreasePencilFrames.new"></a>

#### bpy.types.GreasePencilFrames.new(frame_number)

Add a new Grease Pencil frame

**Parameters:**

**frame_number** (int) – Frame Number, The frame on which the drawing appears (in [-1048574, 1048574])

**Returns:**

The newly created frame

**Return type:**

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")

<a id="bpy.types.GreasePencilFrames.remove"></a>

#### bpy.types.GreasePencilFrames.remove(frame_number)

Remove a Grease Pencil frame

**Parameters:**

**frame_number** (int) – Frame Number, The frame number of the frame to remove (in [-1048574, 1048574])

<a id="bpy.types.GreasePencilFrames.copy"></a>

#### bpy.types.GreasePencilFrames.copy(from_frame_number, to_frame_number, *, instance_drawing=False)

Copy a Grease Pencil frame

**Parameters:**

- **from_frame_number** (int) – Source Frame Number, The frame number of the source frame (in [-1048574, 1048574])
- **to_frame_number** (int) – Frame Number of Copy, The frame number to copy the frame to (in [-1048574, 1048574])
- **instance_drawing** (bool) – Instance Drawing, Let the copied frame use the same drawing as the source (optional)

**Returns:**

The newly copied frame

**Return type:**

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")

<a id="bpy.types.GreasePencilFrames.move"></a>

#### bpy.types.GreasePencilFrames.move(from_frame_number, to_frame_number)

Move a Grease Pencil frame

**Parameters:**

- **from_frame_number** (int) – Source Frame Number, The frame number of the source frame (in [-1048574, 1048574])
- **to_frame_number** (int) – Target Frame Number, The frame number to move the frame to (in [-1048574, 1048574])

**Returns:**

The moved frame

**Return type:**

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")

<a id="bpy.types.GreasePencilFrames.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilFrames.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilFrames.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilFrames.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencilLayer.frames`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer.frames "bpy.types.GreasePencilLayer.frames") |  |
