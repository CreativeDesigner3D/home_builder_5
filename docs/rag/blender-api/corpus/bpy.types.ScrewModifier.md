<!-- source: Blender Python API reference 5.2 / bpy.types.ScrewModifier.html -->

<a id="screwmodifier-modifier"></a>

# ScrewModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ScrewModifier"></a>

### class bpy.types.ScrewModifier(Modifier)

Revolve edges

<a id="bpy.types.ScrewModifier.angle"></a>

#### bpy.types.ScrewModifier.angle

Angle of revolution (in [-inf, inf], default 6.28319)

**Type:**

float

<a id="bpy.types.ScrewModifier.axis"></a>

#### bpy.types.ScrewModifier.axis

Screw axis (default `'Z'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.ScrewModifier.iterations"></a>

#### bpy.types.ScrewModifier.iterations

Number of times to apply the screw operation (in [1, 10000], default 1)

**Type:**

int

<a id="bpy.types.ScrewModifier.merge_threshold"></a>

#### bpy.types.ScrewModifier.merge_threshold

Limit below which to merge vertices (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.ScrewModifier.object"></a>

#### bpy.types.ScrewModifier.object

Object to define the screw axis

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ScrewModifier.render_steps"></a>

#### bpy.types.ScrewModifier.render_steps

Number of steps in the revolution (in [1, 10000], default 16)

**Type:**

int

<a id="bpy.types.ScrewModifier.screw_offset"></a>

#### bpy.types.ScrewModifier.screw_offset

Offset the revolution along its axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ScrewModifier.steps"></a>

#### bpy.types.ScrewModifier.steps

Number of steps in the revolution (in [1, 10000], default 16)

**Type:**

int

<a id="bpy.types.ScrewModifier.use_merge_vertices"></a>

#### bpy.types.ScrewModifier.use_merge_vertices

Merge adjacent vertices (screw offset must be zero) (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_normal_calculate"></a>

#### bpy.types.ScrewModifier.use_normal_calculate

Calculate the order of edges (needed for meshes, but not curves) (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_normal_flip"></a>

#### bpy.types.ScrewModifier.use_normal_flip

Flip normals of lathed faces (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_object_screw_offset"></a>

#### bpy.types.ScrewModifier.use_object_screw_offset

Use the distance between the objects to make a screw (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_smooth_shade"></a>

#### bpy.types.ScrewModifier.use_smooth_shade

Output faces with smooth shading rather than flat shaded (default True)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_stretch_u"></a>

#### bpy.types.ScrewModifier.use_stretch_u

Stretch the U coordinates between 0 and 1 when UVs are present (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.use_stretch_v"></a>

#### bpy.types.ScrewModifier.use_stretch_v

Stretch the V coordinates between 0 and 1 when UVs are present (default False)

**Type:**

bool

<a id="bpy.types.ScrewModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ScrewModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ScrewModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ScrewModifier.bl_rna_get_subclass_py(id, default=None, /)

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
