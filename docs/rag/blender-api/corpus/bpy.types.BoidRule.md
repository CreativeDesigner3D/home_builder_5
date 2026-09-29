<!-- source: Blender Python API reference 5.2 / bpy.types.BoidRule.html -->

<a id="boidrule-bpy-struct"></a>

# BoidRule(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [BoidRuleAverageSpeed(BoidRule)](bpy.types.BoidRuleAverageSpeed.md)
- [BoidRuleAvoid(BoidRule)](bpy.types.BoidRuleAvoid.md)
- [BoidRuleAvoidCollision(BoidRule)](bpy.types.BoidRuleAvoidCollision.md)
- [BoidRuleFight(BoidRule)](bpy.types.BoidRuleFight.md)
- [BoidRuleFollowLeader(BoidRule)](bpy.types.BoidRuleFollowLeader.md)
- [BoidRuleGoal(BoidRule)](bpy.types.BoidRuleGoal.md)

<a id="bpy.types.BoidRule"></a>

### class bpy.types.BoidRule(bpy_struct)

<a id="bpy.types.BoidRule.name"></a>

#### bpy.types.BoidRule.name

Boid rule name (default “”, never None)

**Type:**

str

<a id="bpy.types.BoidRule.type"></a>

#### bpy.types.BoidRule.type

(default `'GOAL'`, readonly)

**Type:**

Literal[[Boidrule Type Items](bpy_types_enum_items/boidrule_type_items.md#rna-enum-boidrule-type-items)]

<a id="bpy.types.BoidRule.use_in_air"></a>

#### bpy.types.BoidRule.use_in_air

Use rule when boid is flying (default False)

**Type:**

bool

<a id="bpy.types.BoidRule.use_on_land"></a>

#### bpy.types.BoidRule.use_on_land

Use rule when boid is on land (default False)

**Type:**

bool

<a id="bpy.types.BoidRule.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoidRule.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoidRule.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoidRule.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.BoidRule.type "bpy.types.BoidRule.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.BoidRule.type "bpy.types.BoidRule.type")

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
| - [`BoidSettings.active_boid_state`](bpy.types.BoidSettings.md#bpy.types.BoidSettings.active_boid_state "bpy.types.BoidSettings.active_boid_state") - [`BoidState.active_boid_rule`](bpy.types.BoidState.md#bpy.types.BoidState.active_boid_rule "bpy.types.BoidState.active_boid_rule") | - [`BoidState.rules`](bpy.types.BoidState.md#bpy.types.BoidState.rules "bpy.types.BoidState.rules") |
