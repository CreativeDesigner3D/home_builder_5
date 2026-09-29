<!-- source: Blender Python API reference 5.2 / bpy.types.MeshAutomaskingSettings.html -->

<a id="meshautomaskingsettings-bpy-struct"></a>

# MeshAutomaskingSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshAutomaskingSettings"></a>

### class bpy.types.MeshAutomaskingSettings(bpy_struct)

Automasking settings for mesh painting & sculpting.

<a id="bpy.types.MeshAutomaskingSettings.boundary_edges_propagation_steps"></a>

#### bpy.types.MeshAutomaskingSettings.boundary_edges_propagation_steps

Distance where boundary edge automasking is going to protect vertices from the fully masked edge (in [1, 20], default 1)

**Type:**

int

<a id="bpy.types.MeshAutomaskingSettings.cavity_blur_steps"></a>

#### bpy.types.MeshAutomaskingSettings.cavity_blur_steps

The number of times the cavity mask is blurred (in [0, 25], default 0)

**Type:**

int

<a id="bpy.types.MeshAutomaskingSettings.cavity_curve"></a>

#### bpy.types.MeshAutomaskingSettings.cavity_curve

Curve used for the sensitivity (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.MeshAutomaskingSettings.cavity_curve_op"></a>

#### bpy.types.MeshAutomaskingSettings.cavity_curve_op

Curve used for the sensitivity (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.MeshAutomaskingSettings.cavity_factor"></a>

#### bpy.types.MeshAutomaskingSettings.cavity_factor

The contrast of the cavity mask (in [0, 5], default 1.0)

**Type:**

float

<a id="bpy.types.MeshAutomaskingSettings.start_normal_falloff"></a>

#### bpy.types.MeshAutomaskingSettings.start_normal_falloff

Extend the angular range with a falloff gradient (in [0.0001, 1], default 0.25)

**Type:**

float

<a id="bpy.types.MeshAutomaskingSettings.start_normal_limit"></a>

#### bpy.types.MeshAutomaskingSettings.start_normal_limit

The range of angles that will be affected (in [0.0001, 3.14159], default 0.349066)

**Type:**

float

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_boundary_edges"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_boundary_edges

Do not affect non manifold boundary edges (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_boundary_face_sets"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_boundary_face_sets

Do not affect vertices that belong to a face set boundary (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_cavity"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_cavity

Do not affect vertices on peaks, based on the surface curvature (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_cavity_inverted"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_cavity_inverted

Do not affect vertices within crevices, based on the surface curvature (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_custom_cavity_curve"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_custom_cavity_curve

Use custom curve (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_face_sets"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_face_sets

Affect only vertices that share face sets with the active vertex (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_start_normal"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_start_normal

Affect only vertices with a similar normal to where the stroke starts (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_topology"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_topology

Affect only vertices connected to the active vertex under the brush (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_view_normal"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_view_normal

Affect only vertices with a normal that faces the viewer (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.use_automasking_view_occlusion"></a>

#### bpy.types.MeshAutomaskingSettings.use_automasking_view_occlusion

Only affect vertices that are not occluded by other faces (slower performance) (default False)

**Type:**

bool

<a id="bpy.types.MeshAutomaskingSettings.view_normal_falloff"></a>

#### bpy.types.MeshAutomaskingSettings.view_normal_falloff

Extend the angular range with a falloff gradient (in [0.0001, 1], default 0.25)

**Type:**

float

<a id="bpy.types.MeshAutomaskingSettings.view_normal_limit"></a>

#### bpy.types.MeshAutomaskingSettings.view_normal_limit

The range of angles that will be affected (in [0.0001, 3.14159], default 1.5708)

**Type:**

float

<a id="bpy.types.MeshAutomaskingSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshAutomaskingSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshAutomaskingSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshAutomaskingSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Brush.mesh_automasking_settings`](bpy.types.Brush.md#bpy.types.Brush.mesh_automasking_settings "bpy.types.Brush.mesh_automasking_settings") | - [`Paint.mesh_automasking_settings`](bpy.types.Paint.md#bpy.types.Paint.mesh_automasking_settings "bpy.types.Paint.mesh_automasking_settings") |
