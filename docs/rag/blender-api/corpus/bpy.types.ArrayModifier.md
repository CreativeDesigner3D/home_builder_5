<!-- source: Blender Python API reference 5.2 / bpy.types.ArrayModifier.html -->

<a id="arraymodifier-modifier"></a>

# ArrayModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ArrayModifier"></a>

### class bpy.types.ArrayModifier(Modifier)

Array duplication modifier

<a id="bpy.types.ArrayModifier.constant_offset_displace"></a>

#### bpy.types.ArrayModifier.constant_offset_displace

Value for the distance between arrayed items (array of 3 items, in [-inf, inf], default (1.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ArrayModifier.count"></a>

#### bpy.types.ArrayModifier.count

Number of duplicates to make (in [1, inf], default 2)

**Type:**

int

<a id="bpy.types.ArrayModifier.curve"></a>

#### bpy.types.ArrayModifier.curve

Curve object to fit array length to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ArrayModifier.end_cap"></a>

#### bpy.types.ArrayModifier.end_cap

Mesh object to use as an end cap

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ArrayModifier.fit_length"></a>

#### bpy.types.ArrayModifier.fit_length

Length to fit array within (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ArrayModifier.fit_type"></a>

#### bpy.types.ArrayModifier.fit_type

Array length calculation method (default `'FIXED_COUNT'`)

- `FIXED_COUNT`
  Fixed Count – Duplicate the object a certain number of times.
- `FIT_LENGTH`
  Fit Length – Duplicate the object as many times as fits in a certain length.
- `FIT_CURVE`
  Fit Curve – Fit the duplicated objects to a curve.

**Type:**

Literal[‘FIXED_COUNT’, ‘FIT_LENGTH’, ‘FIT_CURVE’]

<a id="bpy.types.ArrayModifier.merge_threshold"></a>

#### bpy.types.ArrayModifier.merge_threshold

Limit below which to merge vertices (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.ArrayModifier.offset_object"></a>

#### bpy.types.ArrayModifier.offset_object

Use the location and rotation of another object to determine the distance and rotational change between arrayed items

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ArrayModifier.offset_u"></a>

#### bpy.types.ArrayModifier.offset_u

Amount to offset array UVs on the U axis (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ArrayModifier.offset_v"></a>

#### bpy.types.ArrayModifier.offset_v

Amount to offset array UVs on the V axis (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ArrayModifier.relative_offset_displace"></a>

#### bpy.types.ArrayModifier.relative_offset_displace

The size of the geometry will determine the distance between arrayed items (array of 3 items, in [-inf, inf], default (1.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ArrayModifier.start_cap"></a>

#### bpy.types.ArrayModifier.start_cap

Mesh object to use as a start cap

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ArrayModifier.use_constant_offset"></a>

#### bpy.types.ArrayModifier.use_constant_offset

Add a constant offset (default False)

**Type:**

bool

<a id="bpy.types.ArrayModifier.use_merge_vertices"></a>

#### bpy.types.ArrayModifier.use_merge_vertices

Merge vertices in adjacent duplicates (default False)

**Type:**

bool

<a id="bpy.types.ArrayModifier.use_merge_vertices_cap"></a>

#### bpy.types.ArrayModifier.use_merge_vertices_cap

Merge vertices in first and last duplicates (default False)

**Type:**

bool

<a id="bpy.types.ArrayModifier.use_object_offset"></a>

#### bpy.types.ArrayModifier.use_object_offset

Add another object’s transformation to the total offset (default False)

**Type:**

bool

<a id="bpy.types.ArrayModifier.use_relative_offset"></a>

#### bpy.types.ArrayModifier.use_relative_offset

Add an offset relative to the object’s bounding box (default True)

**Type:**

bool

<a id="bpy.types.ArrayModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ArrayModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ArrayModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ArrayModifier.bl_rna_get_subclass_py(id, default=None, /)

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
