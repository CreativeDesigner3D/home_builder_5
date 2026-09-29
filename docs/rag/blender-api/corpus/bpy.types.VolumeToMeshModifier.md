<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeToMeshModifier.html -->

<a id="volumetomeshmodifier-modifier"></a>

# VolumeToMeshModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.VolumeToMeshModifier"></a>

### class bpy.types.VolumeToMeshModifier(Modifier)

<a id="bpy.types.VolumeToMeshModifier.adaptivity"></a>

#### bpy.types.VolumeToMeshModifier.adaptivity

Reduces the final face count by simplifying geometry where detail is not needed (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeToMeshModifier.grid_name"></a>

#### bpy.types.VolumeToMeshModifier.grid_name

Grid in the volume object that is converted to a mesh (default “”, never None)

**Type:**

str

<a id="bpy.types.VolumeToMeshModifier.object"></a>

#### bpy.types.VolumeToMeshModifier.object

Object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VolumeToMeshModifier.resolution_mode"></a>

#### bpy.types.VolumeToMeshModifier.resolution_mode

Mode for how the desired voxel size is specified (default `'GRID'`)

- `GRID`
  Grid – Use resolution of the volume grid.
- `VOXEL_AMOUNT`
  Voxel Amount – Desired number of voxels along one axis.
- `VOXEL_SIZE`
  Voxel Size – Desired voxel side length.

**Type:**

Literal[‘GRID’, ‘VOXEL_AMOUNT’, ‘VOXEL_SIZE’]

<a id="bpy.types.VolumeToMeshModifier.threshold"></a>

#### bpy.types.VolumeToMeshModifier.threshold

Voxels with a larger value are inside the generated mesh (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeToMeshModifier.use_smooth_shade"></a>

#### bpy.types.VolumeToMeshModifier.use_smooth_shade

Output faces with smooth shading rather than flat shaded (default False)

**Type:**

bool

<a id="bpy.types.VolumeToMeshModifier.voxel_amount"></a>

#### bpy.types.VolumeToMeshModifier.voxel_amount

Approximate number of voxels along one axis (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.VolumeToMeshModifier.voxel_size"></a>

#### bpy.types.VolumeToMeshModifier.voxel_size

Smaller values result in a higher resolution output (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeToMeshModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeToMeshModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeToMeshModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeToMeshModifier.bl_rna_get_subclass_py(id, default=None, /)

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
