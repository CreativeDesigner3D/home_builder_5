<!-- source: Blender Python API reference 5.2 / bpy.types.BoidState.html -->

<a id="boidstate-bpy-struct"></a>

# BoidState(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BoidState"></a>

### class bpy.types.BoidState(bpy_struct)

Boid state for boid physics

<a id="bpy.types.BoidState.active_boid_rule"></a>

#### bpy.types.BoidState.active_boid_rule

(readonly)

**Type:**

[`BoidRule`](bpy.types.BoidRule.md#bpy.types.BoidRule "bpy.types.BoidRule") | None

<a id="bpy.types.BoidState.active_boid_rule_index"></a>

#### bpy.types.BoidState.active_boid_rule_index

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.BoidState.falloff"></a>

#### bpy.types.BoidState.falloff

(in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.BoidState.name"></a>

#### bpy.types.BoidState.name

Boid state name (default “”, never None)

**Type:**

str

<a id="bpy.types.BoidState.rule_fuzzy"></a>

#### bpy.types.BoidState.rule_fuzzy

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidState.rules"></a>

#### bpy.types.BoidState.rules

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoidRule`](bpy.types.BoidRule.md#bpy.types.BoidRule "bpy.types.BoidRule")]

<a id="bpy.types.BoidState.ruleset_type"></a>

#### bpy.types.BoidState.ruleset_type

How the rules in the list are evaluated (default `'FUZZY'`)

- `FUZZY`
  Fuzzy – Rules are gone through top to bottom (only the first rule which effect is above fuzziness threshold is evaluated).
- `RANDOM`
  Random – A random rule is selected for each boid.
- `AVERAGE`
  Average – All rules are averaged.

**Type:**

Literal[‘FUZZY’, ‘RANDOM’, ‘AVERAGE’]

<a id="bpy.types.BoidState.volume"></a>

#### bpy.types.BoidState.volume

(in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidState.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoidState.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoidState.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoidState.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BoidSettings.states`](bpy.types.BoidSettings.md#bpy.types.BoidSettings.states "bpy.types.BoidSettings.states") |  |
