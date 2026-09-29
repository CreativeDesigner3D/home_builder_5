<!-- source: Blender Python API reference 5.2 / bpy.types.MeshCacheModifier.html -->

<a id="meshcachemodifier-modifier"></a>

# MeshCacheModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.MeshCacheModifier"></a>

### class bpy.types.MeshCacheModifier(Modifier)

Cache Mesh

<a id="bpy.types.MeshCacheModifier.cache_format"></a>

#### bpy.types.MeshCacheModifier.cache_format

(default `'MDD'`)

**Type:**

Literal[‘MDD’, ‘PC2’]

<a id="bpy.types.MeshCacheModifier.deform_mode"></a>

#### bpy.types.MeshCacheModifier.deform_mode

(default `'OVERWRITE'`)

- `OVERWRITE`
  Overwrite – Replace vertex coordinates with cached values.
- `INTEGRATE`
  Integrate – Integrate deformation from this modifier’s input with the mesh-cache coordinates (useful for shape keys).

**Type:**

Literal[‘OVERWRITE’, ‘INTEGRATE’]

<a id="bpy.types.MeshCacheModifier.eval_factor"></a>

#### bpy.types.MeshCacheModifier.eval_factor

Evaluation time in seconds (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.eval_frame"></a>

#### bpy.types.MeshCacheModifier.eval_frame

The frame to evaluate (starting at 0) (in [0, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.eval_time"></a>

#### bpy.types.MeshCacheModifier.eval_time

Evaluation time in seconds (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.factor"></a>

#### bpy.types.MeshCacheModifier.factor

Influence of the deformation (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.filepath"></a>

#### bpy.types.MeshCacheModifier.filepath

Path to external displacements file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.MeshCacheModifier.flip_axis"></a>

#### bpy.types.MeshCacheModifier.flip_axis

(array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.MeshCacheModifier.forward_axis"></a>

#### bpy.types.MeshCacheModifier.forward_axis

(default `'POS_Y'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.MeshCacheModifier.frame_scale"></a>

#### bpy.types.MeshCacheModifier.frame_scale

Evaluation time in seconds (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.frame_start"></a>

#### bpy.types.MeshCacheModifier.frame_start

Add this to the start frame (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.MeshCacheModifier.interpolation"></a>

#### bpy.types.MeshCacheModifier.interpolation

(default `'LINEAR'`)

**Type:**

Literal[‘NONE’, ‘LINEAR’]

<a id="bpy.types.MeshCacheModifier.invert_vertex_group"></a>

#### bpy.types.MeshCacheModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.MeshCacheModifier.play_mode"></a>

#### bpy.types.MeshCacheModifier.play_mode

(default `'SCENE'`)

- `SCENE`
  Scene – Use the time from the scene.
- `CUSTOM`
  Custom – Use the modifier’s own time evaluation.

**Type:**

Literal[‘SCENE’, ‘CUSTOM’]

<a id="bpy.types.MeshCacheModifier.time_mode"></a>

#### bpy.types.MeshCacheModifier.time_mode

Method to control playback time (default `'FRAME'`)

- `FRAME`
  Frame – Control playback using a frame-number (ignoring time FPS and start frame from the file).
- `TIME`
  Time – Control playback using time in seconds.
- `FACTOR`
  Factor – Control playback using a value between 0 and 1.

**Type:**

Literal[‘FRAME’, ‘TIME’, ‘FACTOR’]

<a id="bpy.types.MeshCacheModifier.up_axis"></a>

#### bpy.types.MeshCacheModifier.up_axis

(default `'POS_Z'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.MeshCacheModifier.vertex_group"></a>

#### bpy.types.MeshCacheModifier.vertex_group

Name of the Vertex Group which determines the influence of the modifier per point (default “”, never None)

**Type:**

str

<a id="bpy.types.MeshCacheModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshCacheModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshCacheModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshCacheModifier.bl_rna_get_subclass_py(id, default=None, /)

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
