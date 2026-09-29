<!-- source: Blender Python API reference 5.2 / bpy.types.CameraDOFSettings.html -->

<a id="cameradofsettings-bpy-struct"></a>

# CameraDOFSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CameraDOFSettings"></a>

### class bpy.types.CameraDOFSettings(bpy_struct)

Depth of Field settings

<a id="bpy.types.CameraDOFSettings.aperture_blades"></a>

#### bpy.types.CameraDOFSettings.aperture_blades

Number of blades in aperture for polygonal bokeh (at least 3) (in [0, 16], default 0)

**Type:**

int

<a id="bpy.types.CameraDOFSettings.aperture_fstop"></a>

#### bpy.types.CameraDOFSettings.aperture_fstop

F-Stop ratio (lower numbers give more defocus, higher numbers give a sharper image) (in [0, inf], default 2.8)

**Type:**

float

<a id="bpy.types.CameraDOFSettings.aperture_ratio"></a>

#### bpy.types.CameraDOFSettings.aperture_ratio

Distortion to simulate anamorphic lens bokeh (in [0.01, inf], default 1.0)

**Type:**

float

<a id="bpy.types.CameraDOFSettings.aperture_rotation"></a>

#### bpy.types.CameraDOFSettings.aperture_rotation

Rotation of blades in aperture (in [-3.14159, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.CameraDOFSettings.focus_distance"></a>

#### bpy.types.CameraDOFSettings.focus_distance

Distance to the focus point for depth of field (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.CameraDOFSettings.focus_object"></a>

#### bpy.types.CameraDOFSettings.focus_object

Use this object to define the depth of field focal point

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CameraDOFSettings.focus_subtarget"></a>

#### bpy.types.CameraDOFSettings.focus_subtarget

Use this armature bone to define the depth of field focal point (default “”, never None)

**Type:**

str

<a id="bpy.types.CameraDOFSettings.use_dof"></a>

#### bpy.types.CameraDOFSettings.use_dof

Use Depth of Field (default False)

**Type:**

bool

<a id="bpy.types.CameraDOFSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CameraDOFSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CameraDOFSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CameraDOFSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Camera.dof`](bpy.types.Camera.md#bpy.types.Camera.dof "bpy.types.Camera.dof") |  |
