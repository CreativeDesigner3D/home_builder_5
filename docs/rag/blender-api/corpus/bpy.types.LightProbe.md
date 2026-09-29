<!-- source: Blender Python API reference 5.2 / bpy.types.LightProbe.html -->

<a id="lightprobe-id"></a>

# LightProbe(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

Subclasses

- [LightProbePlane(LightProbe)](bpy.types.LightProbePlane.md)
- [LightProbeSphere(LightProbe)](bpy.types.LightProbeSphere.md)
- [LightProbeVolume(LightProbe)](bpy.types.LightProbeVolume.md)

<a id="bpy.types.LightProbe"></a>

### class bpy.types.LightProbe(ID)

Light Probe data-block for lighting capture objects

<a id="bpy.types.LightProbe.animation_data"></a>

#### bpy.types.LightProbe.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.LightProbe.clip_start"></a>

#### bpy.types.LightProbe.clip_start

Probe clip start, below which objects will not appear in reflections (in [1e-06, inf], default 0.8)

**Type:**

float

<a id="bpy.types.LightProbe.data_display_size"></a>

#### bpy.types.LightProbe.data_display_size

Viewport display size of the sampled data (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.LightProbe.influence_distance"></a>

#### bpy.types.LightProbe.influence_distance

Influence distance of the probe (in [0, inf], default 2.5)

**Type:**

float

<a id="bpy.types.LightProbe.invert_visibility_collection"></a>

#### bpy.types.LightProbe.invert_visibility_collection

Invert visibility collection (Deprecated) (default False)

**Type:**

bool

<a id="bpy.types.LightProbe.show_clip"></a>

#### bpy.types.LightProbe.show_clip

Show the clipping distances in the 3D view (default False)

**Type:**

bool

<a id="bpy.types.LightProbe.show_data"></a>

#### bpy.types.LightProbe.show_data

Deprecated, use use_data_display instead (default False)

**Type:**

bool

<a id="bpy.types.LightProbe.show_influence"></a>

#### bpy.types.LightProbe.show_influence

Show the influence volume in the 3D view (default True)

**Type:**

bool

<a id="bpy.types.LightProbe.type"></a>

#### bpy.types.LightProbe.type

Type of light probe (default `'SPHERE'`, readonly)

- `SPHERE`
  Sphere – Light probe that captures precise lighting from all directions at a single point in space.
- `PLANE`
  Plane – Light probe that captures incoming light from a single direction on a plane.
- `VOLUME`
  Volume – Light probe that captures low frequency lighting inside a volume.

**Type:**

Literal[‘SPHERE’, ‘PLANE’, ‘VOLUME’]

<a id="bpy.types.LightProbe.use_data_display"></a>

#### bpy.types.LightProbe.use_data_display

Display sampled data in the viewport to debug captured light (default False)

**Type:**

bool

<a id="bpy.types.LightProbe.visibility_bleed_bias"></a>

#### bpy.types.LightProbe.visibility_bleed_bias

Bias for reducing light-bleed on variance shadow maps (Deprecated) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.LightProbe.visibility_blur"></a>

#### bpy.types.LightProbe.visibility_blur

Filter size of the visibility blur (Deprecated) (in [0, 1], default 0.2)

**Type:**

float

<a id="bpy.types.LightProbe.visibility_buffer_bias"></a>

#### bpy.types.LightProbe.visibility_buffer_bias

Bias for reducing self shadowing (Deprecated) (in [0.001, 9999], default 1.0)

**Type:**

float

<a id="bpy.types.LightProbe.visibility_collection"></a>

#### bpy.types.LightProbe.visibility_collection

Restrict objects visible for this probe (Deprecated)

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.LightProbe.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LightProbe.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LightProbe.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LightProbe.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LightProbe.type "bpy.types.LightProbe.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LightProbe.type "bpy.types.LightProbe.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.lightprobe` - [`BlendData.lightprobes`](bpy.types.BlendData.md#bpy.types.BlendData.lightprobes "bpy.types.BlendData.lightprobes") | - [`BlendDataProbes.new`](bpy.types.BlendDataProbes.md#bpy.types.BlendDataProbes.new "bpy.types.BlendDataProbes.new") - [`BlendDataProbes.remove`](bpy.types.BlendDataProbes.md#bpy.types.BlendDataProbes.remove "bpy.types.BlendDataProbes.remove") |
