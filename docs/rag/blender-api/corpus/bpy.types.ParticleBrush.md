<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleBrush.html -->

<a id="particlebrush-bpy-struct"></a>

# ParticleBrush(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ParticleBrush"></a>

### class bpy.types.ParticleBrush(bpy_struct)

Particle editing brush

<a id="bpy.types.ParticleBrush.count"></a>

#### bpy.types.ParticleBrush.count

Particle count (in [1, 1000], default 10)

**Type:**

int

<a id="bpy.types.ParticleBrush.curve"></a>

#### bpy.types.ParticleBrush.curve

(readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.ParticleBrush.length_mode"></a>

#### bpy.types.ParticleBrush.length_mode

(default `'GROW'`)

- `GROW`
  Grow – Make hairs longer.
- `SHRINK`
  Shrink – Make hairs shorter.

**Type:**

Literal[‘GROW’, ‘SHRINK’]

<a id="bpy.types.ParticleBrush.puff_mode"></a>

#### bpy.types.ParticleBrush.puff_mode

(default `'ADD'`)

- `ADD`
  Add – Make hairs more puffy.
- `SUB`
  Sub – Make hairs less puffy.

**Type:**

Literal[‘ADD’, ‘SUB’]

<a id="bpy.types.ParticleBrush.size"></a>

#### bpy.types.ParticleBrush.size

Radius of the brush in pixels (in [1, 32767], default 50)

**Type:**

int

<a id="bpy.types.ParticleBrush.steps"></a>

#### bpy.types.ParticleBrush.steps

Brush steps (in [1, 32767], default 10)

**Type:**

int

<a id="bpy.types.ParticleBrush.strength"></a>

#### bpy.types.ParticleBrush.strength

Brush strength (in [0.001, 1], default 0.5)

**Type:**

float

<a id="bpy.types.ParticleBrush.use_puff_volume"></a>

#### bpy.types.ParticleBrush.use_puff_volume

Apply puff to unselected end-points (helps maintain hair volume when puffing root) (default False)

**Type:**

bool

<a id="bpy.types.ParticleBrush.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleBrush.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleBrush.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleBrush.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ParticleEdit.brush`](bpy.types.ParticleEdit.md#bpy.types.ParticleEdit.brush "bpy.types.ParticleEdit.brush") |  |
