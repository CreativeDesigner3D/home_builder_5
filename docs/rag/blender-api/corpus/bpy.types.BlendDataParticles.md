<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataParticles.html -->

<a id="blenddataparticles-bpy-prop-collection"></a>

# BlendDataParticles(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataParticles"></a>

### class bpy.types.BlendDataParticles(bpy_prop_collection)

Collection of particle settings

<a id="bpy.types.BlendDataParticles.new"></a>

#### bpy.types.BlendDataParticles.new(name)

Add a new particle settings instance to the main database

**Parameters:**

**name** (str) – New name for the data-block (never None)

**Returns:**

New particle settings data-block

**Return type:**

[`ParticleSettings`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings "bpy.types.ParticleSettings")

<a id="bpy.types.BlendDataParticles.remove"></a>

#### bpy.types.BlendDataParticles.remove(particle, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a particle settings instance from the current blendfile

**Parameters:**

- **particle** ([`ParticleSettings`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings "bpy.types.ParticleSettings") | None) – Particle Settings to remove (never None)
- **do_unlink** (bool) – Unlink all usages of those particle settings before deleting them (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this particle settings (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this particle settings (optional)

<a id="bpy.types.BlendDataParticles.tag"></a>

#### bpy.types.BlendDataParticles.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataParticles.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataParticles.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataParticles.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataParticles.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.particles`](bpy.types.BlendData.md#bpy.types.BlendData.particles "bpy.types.BlendData.particles") |  |
