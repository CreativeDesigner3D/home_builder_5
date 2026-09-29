<!-- source: Blender Python API reference 5.2 / bpy.types.WeightedNormalModifier.html -->

<a id="weightednormalmodifier-modifier"></a>

# WeightedNormalModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.WeightedNormalModifier"></a>

### class bpy.types.WeightedNormalModifier(Modifier)

<a id="bpy.types.WeightedNormalModifier.invert_vertex_group"></a>

#### bpy.types.WeightedNormalModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.WeightedNormalModifier.keep_sharp"></a>

#### bpy.types.WeightedNormalModifier.keep_sharp

Keep sharp edges as computed for default custom normals, instead of setting a single weighted normal for each vertex (default False)

**Type:**

bool

<a id="bpy.types.WeightedNormalModifier.mode"></a>

#### bpy.types.WeightedNormalModifier.mode

Weighted vertex normal mode to use (default `'FACE_AREA'`)

- `FACE_AREA`
  Face Area – Generate face area weighted normals.
- `CORNER_ANGLE`
  Corner Angle – Generate corner angle weighted normals.
- `FACE_AREA_WITH_ANGLE`
  Face Area & Angle – Generated normals weighted by both face area and angle.

**Type:**

Literal[‘FACE_AREA’, ‘CORNER_ANGLE’, ‘FACE_AREA_WITH_ANGLE’]

<a id="bpy.types.WeightedNormalModifier.thresh"></a>

#### bpy.types.WeightedNormalModifier.thresh

Threshold value for different weights to be considered equal (in [0, 10], default 0.01)

**Type:**

float

<a id="bpy.types.WeightedNormalModifier.use_face_influence"></a>

#### bpy.types.WeightedNormalModifier.use_face_influence

Use influence of face for weighting (default False)

**Type:**

bool

<a id="bpy.types.WeightedNormalModifier.vertex_group"></a>

#### bpy.types.WeightedNormalModifier.vertex_group

Vertex group name for modifying the selected areas (default “”, never None)

**Type:**

str

<a id="bpy.types.WeightedNormalModifier.weight"></a>

#### bpy.types.WeightedNormalModifier.weight

Corrective factor applied to faces’ weights, 50 is neutral, lower values increase weight of weak faces, higher values increase weight of strong faces (in [1, 100], default 50)

**Type:**

int

<a id="bpy.types.WeightedNormalModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WeightedNormalModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WeightedNormalModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WeightedNormalModifier.bl_rna_get_subclass_py(id, default=None, /)

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
