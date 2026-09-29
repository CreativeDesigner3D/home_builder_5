<!-- source: Blender Python API reference 5.2 / bpy.types.RetimingKey.html -->

<a id="retimingkey-bpy-struct"></a>

# RetimingKey(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RetimingKey"></a>

### class bpy.types.RetimingKey(bpy_struct)

Key mapped to particular frame that can be moved to change playback speed

<a id="bpy.types.RetimingKey.timeline_frame"></a>

#### bpy.types.RetimingKey.timeline_frame

Position of retiming key in timeline (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.RetimingKey.remove"></a>

#### bpy.types.RetimingKey.remove()

Remove retiming key

<a id="bpy.types.RetimingKey.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RetimingKey.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RetimingKey.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RetimingKey.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ImageStrip.retiming_keys`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.retiming_keys "bpy.types.ImageStrip.retiming_keys") - [`MovieStrip.retiming_keys`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.retiming_keys "bpy.types.MovieStrip.retiming_keys") - [`RetimingKeys.add`](bpy.types.RetimingKeys.md#bpy.types.RetimingKeys.add "bpy.types.RetimingKeys.add") | - [`SceneStrip.retiming_keys`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.retiming_keys "bpy.types.SceneStrip.retiming_keys") - [`SoundStrip.retiming_keys`](bpy.types.SoundStrip.md#bpy.types.SoundStrip.retiming_keys "bpy.types.SoundStrip.retiming_keys") |
