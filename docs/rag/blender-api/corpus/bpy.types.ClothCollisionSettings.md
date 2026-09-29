<!-- source: Blender Python API reference 5.2 / bpy.types.ClothCollisionSettings.html -->

<a id="clothcollisionsettings-bpy-struct"></a>

# ClothCollisionSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ClothCollisionSettings"></a>

### class bpy.types.ClothCollisionSettings(bpy_struct)

Cloth simulation settings for self collision and collision with other objects

<a id="bpy.types.ClothCollisionSettings.collection"></a>

#### bpy.types.ClothCollisionSettings.collection

Limit colliders to this Collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.ClothCollisionSettings.collision_quality"></a>

#### bpy.types.ClothCollisionSettings.collision_quality

How many collision iterations should be done (higher is better quality but slower) (in [1, 32767], default 2)

**Type:**

int

<a id="bpy.types.ClothCollisionSettings.damping"></a>

#### bpy.types.ClothCollisionSettings.damping

Amount of velocity lost on collision (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.distance_min"></a>

#### bpy.types.ClothCollisionSettings.distance_min

Minimum distance between collision objects before collision response takes effect (in [0.001, 1], default 0.015)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.friction"></a>

#### bpy.types.ClothCollisionSettings.friction

Friction force if a collision happened (higher = less movement) (in [0, 80], default 5.0)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.impulse_clamp"></a>

#### bpy.types.ClothCollisionSettings.impulse_clamp

Clamp collision impulses to avoid instability (0.0 to disable clamping) (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.self_distance_min"></a>

#### bpy.types.ClothCollisionSettings.self_distance_min

Minimum distance between cloth faces before collision response takes effect (in [0.001, 0.1], default 0.015)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.self_friction"></a>

#### bpy.types.ClothCollisionSettings.self_friction

Friction with self contact (in [0, 80], default 5.0)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.self_impulse_clamp"></a>

#### bpy.types.ClothCollisionSettings.self_impulse_clamp

Clamp collision impulses to avoid instability (0.0 to disable clamping) (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.ClothCollisionSettings.use_collision"></a>

#### bpy.types.ClothCollisionSettings.use_collision

Enable collisions with other objects (default True)

**Type:**

bool

<a id="bpy.types.ClothCollisionSettings.use_self_collision"></a>

#### bpy.types.ClothCollisionSettings.use_self_collision

Enable self collisions (default False)

**Type:**

bool

<a id="bpy.types.ClothCollisionSettings.vertex_group_object_collisions"></a>

#### bpy.types.ClothCollisionSettings.vertex_group_object_collisions

Triangles with all vertices in this group are not used during object collisions (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothCollisionSettings.vertex_group_self_collisions"></a>

#### bpy.types.ClothCollisionSettings.vertex_group_self_collisions

Triangles with all vertices in this group are not used during self collisions (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothCollisionSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ClothCollisionSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ClothCollisionSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ClothCollisionSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothModifier.collision_settings`](bpy.types.ClothModifier.md#bpy.types.ClothModifier.collision_settings "bpy.types.ClothModifier.collision_settings") |  |
