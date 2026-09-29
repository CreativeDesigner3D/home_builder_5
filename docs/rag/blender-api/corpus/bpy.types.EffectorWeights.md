<!-- source: Blender Python API reference 5.2 / bpy.types.EffectorWeights.html -->

<a id="effectorweights-bpy-struct"></a>

# EffectorWeights(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.EffectorWeights"></a>

### class bpy.types.EffectorWeights(bpy_struct)

Effector weights for physics simulation

<a id="bpy.types.EffectorWeights.all"></a>

#### bpy.types.EffectorWeights.all

All effector’s weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.apply_to_hair_growing"></a>

#### bpy.types.EffectorWeights.apply_to_hair_growing

Use force fields when growing hair (default False)

**Type:**

bool

<a id="bpy.types.EffectorWeights.boid"></a>

#### bpy.types.EffectorWeights.boid

Boid effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.charge"></a>

#### bpy.types.EffectorWeights.charge

Charge effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.collection"></a>

#### bpy.types.EffectorWeights.collection

Limit effectors to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.EffectorWeights.curve_guide"></a>

#### bpy.types.EffectorWeights.curve_guide

Curve guide effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.drag"></a>

#### bpy.types.EffectorWeights.drag

Drag effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.force"></a>

#### bpy.types.EffectorWeights.force

Force effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.gravity"></a>

#### bpy.types.EffectorWeights.gravity

Global gravity weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.harmonic"></a>

#### bpy.types.EffectorWeights.harmonic

Harmonic effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.lennardjones"></a>

#### bpy.types.EffectorWeights.lennardjones

Lennard-Jones effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.magnetic"></a>

#### bpy.types.EffectorWeights.magnetic

Magnetic effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.smokeflow"></a>

#### bpy.types.EffectorWeights.smokeflow

Fluid Flow effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.texture"></a>

#### bpy.types.EffectorWeights.texture

Texture effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.turbulence"></a>

#### bpy.types.EffectorWeights.turbulence

Turbulence effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.vortex"></a>

#### bpy.types.EffectorWeights.vortex

Vortex effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.wind"></a>

#### bpy.types.EffectorWeights.wind

Wind effector weight (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.EffectorWeights.bl_rna_get_subclass"></a>

#### classmethod bpy.types.EffectorWeights.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.EffectorWeights.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.EffectorWeights.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothSettings.effector_weights`](bpy.types.ClothSettings.md#bpy.types.ClothSettings.effector_weights "bpy.types.ClothSettings.effector_weights") - [`DynamicPaintSurface.effector_weights`](bpy.types.DynamicPaintSurface.md#bpy.types.DynamicPaintSurface.effector_weights "bpy.types.DynamicPaintSurface.effector_weights") - [`FluidDomainSettings.effector_weights`](bpy.types.FluidDomainSettings.md#bpy.types.FluidDomainSettings.effector_weights "bpy.types.FluidDomainSettings.effector_weights") | - [`ParticleSettings.effector_weights`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.effector_weights "bpy.types.ParticleSettings.effector_weights") - [`RigidBodyWorld.effector_weights`](bpy.types.RigidBodyWorld.md#bpy.types.RigidBodyWorld.effector_weights "bpy.types.RigidBodyWorld.effector_weights") - [`SoftBodySettings.effector_weights`](bpy.types.SoftBodySettings.md#bpy.types.SoftBodySettings.effector_weights "bpy.types.SoftBodySettings.effector_weights") |
