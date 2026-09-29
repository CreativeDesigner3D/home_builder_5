<!-- source: Blender Python API reference 5.2 / bpy.types.BoidRuleFight.html -->

<a id="boidrulefight-boidrule"></a>

# BoidRuleFight(BoidRule)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`BoidRule`](bpy.types.BoidRule.md#bpy.types.BoidRule "bpy.types.BoidRule")

<a id="bpy.types.BoidRuleFight"></a>

### class bpy.types.BoidRuleFight(BoidRule)

<a id="bpy.types.BoidRuleFight.distance"></a>

#### bpy.types.BoidRuleFight.distance

Attack boids at max this distance (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidRuleFight.flee_distance"></a>

#### bpy.types.BoidRuleFight.flee_distance

Flee to this distance (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidRuleFight.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoidRuleFight.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoidRuleFight.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoidRuleFight.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, BoidRule.name, BoidRule.type, BoidRule.use_in_air, BoidRule.use_on_land

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, BoidRule.bl_rna_get_subclass, BoidRule.bl_rna_get_subclass_py
