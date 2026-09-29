<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleSystemModifier.html -->

<a id="particlesystemmodifier-modifier"></a>

# ParticleSystemModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ParticleSystemModifier"></a>

### class bpy.types.ParticleSystemModifier(Modifier)

Particle system simulation modifier

<a id="bpy.types.ParticleSystemModifier.particle_system"></a>

#### bpy.types.ParticleSystemModifier.particle_system

Particle System that this modifier controls (readonly, never None)

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem")

<a id="bpy.types.ParticleSystemModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleSystemModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleSystemModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleSystemModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Particle.uv_on_emitter`](bpy.types.Particle.md#bpy.types.Particle.uv_on_emitter "bpy.types.Particle.uv_on_emitter") - [`ParticleHairKey.co_object`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object "bpy.types.ParticleHairKey.co_object") - [`ParticleHairKey.co_object_set`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object_set "bpy.types.ParticleHairKey.co_object_set") | - [`ParticleSystem.mcol_on_emitter`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.mcol_on_emitter "bpy.types.ParticleSystem.mcol_on_emitter") - [`ParticleSystem.uv_on_emitter`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.uv_on_emitter "bpy.types.ParticleSystem.uv_on_emitter") |
