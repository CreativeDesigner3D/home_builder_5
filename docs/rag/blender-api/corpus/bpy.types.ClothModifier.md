<!-- source: Blender Python API reference 5.2 / bpy.types.ClothModifier.html -->

<a id="clothmodifier-modifier"></a>

# ClothModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ClothModifier"></a>

### class bpy.types.ClothModifier(Modifier)

Cloth simulation modifier

<a id="bpy.types.ClothModifier.collision_settings"></a>

#### bpy.types.ClothModifier.collision_settings

(readonly, never None)

**Type:**

[`ClothCollisionSettings`](bpy.types.ClothCollisionSettings.md#bpy.types.ClothCollisionSettings "bpy.types.ClothCollisionSettings")

<a id="bpy.types.ClothModifier.hair_grid_max"></a>

#### bpy.types.ClothModifier.hair_grid_max

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ClothModifier.hair_grid_min"></a>

#### bpy.types.ClothModifier.hair_grid_min

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ClothModifier.hair_grid_resolution"></a>

#### bpy.types.ClothModifier.hair_grid_resolution

(array of 3 items, in [-inf, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ClothModifier.point_cache"></a>

#### bpy.types.ClothModifier.point_cache

(readonly, never None)

**Type:**

[`PointCache`](bpy.types.PointCache.md#bpy.types.PointCache "bpy.types.PointCache")

<a id="bpy.types.ClothModifier.settings"></a>

#### bpy.types.ClothModifier.settings

(readonly, never None)

**Type:**

[`ClothSettings`](bpy.types.ClothSettings.md#bpy.types.ClothSettings "bpy.types.ClothSettings")

<a id="bpy.types.ClothModifier.solver_result"></a>

#### bpy.types.ClothModifier.solver_result

(readonly)

**Type:**

[`ClothSolverResult`](bpy.types.ClothSolverResult.md#bpy.types.ClothSolverResult "bpy.types.ClothSolverResult") | None

<a id="bpy.types.ClothModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ClothModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ClothModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ClothModifier.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.cloth` | - [`ParticleSystem.cloth`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.cloth "bpy.types.ParticleSystem.cloth") |
