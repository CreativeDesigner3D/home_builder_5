<!-- source: Blender Python API reference 5.2 / bpy.types.SimpleDeformModifier.html -->

<a id="simpledeformmodifier-modifier"></a>

# SimpleDeformModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.SimpleDeformModifier"></a>

### class bpy.types.SimpleDeformModifier(Modifier)

Simple deformation modifier to apply effects such as twisting and bending

<a id="bpy.types.SimpleDeformModifier.angle"></a>

#### bpy.types.SimpleDeformModifier.angle

Angle of deformation (in [-inf, inf], default 0.785398)

**Type:**

float

<a id="bpy.types.SimpleDeformModifier.deform_axis"></a>

#### bpy.types.SimpleDeformModifier.deform_axis

Deform around local axis (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.SimpleDeformModifier.deform_method"></a>

#### bpy.types.SimpleDeformModifier.deform_method

(default `'TWIST'`)

- `TWIST`
  Twist – Rotate around the Z axis of the modifier space.
- `BEND`
  Bend – Bend the mesh over the Z axis of the modifier space.
- `TAPER`
  Taper – Linearly scale along Z axis of the modifier space.
- `STRETCH`
  Stretch – Stretch the object along the Z axis of the modifier space.

**Type:**

Literal[‘TWIST’, ‘BEND’, ‘TAPER’, ‘STRETCH’]

<a id="bpy.types.SimpleDeformModifier.factor"></a>

#### bpy.types.SimpleDeformModifier.factor

Amount to deform object (in [-inf, inf], default 0.785398)

**Type:**

float

<a id="bpy.types.SimpleDeformModifier.invert_vertex_group"></a>

#### bpy.types.SimpleDeformModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.SimpleDeformModifier.limits"></a>

#### bpy.types.SimpleDeformModifier.limits

Lower/Upper limits for deform (array of 2 items, in [0, 1], default (0.0, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SimpleDeformModifier.lock_x"></a>

#### bpy.types.SimpleDeformModifier.lock_x

Do not allow deformation along the X axis (default False)

**Type:**

bool

<a id="bpy.types.SimpleDeformModifier.lock_y"></a>

#### bpy.types.SimpleDeformModifier.lock_y

Do not allow deformation along the Y axis (default False)

**Type:**

bool

<a id="bpy.types.SimpleDeformModifier.lock_z"></a>

#### bpy.types.SimpleDeformModifier.lock_z

Do not allow deformation along the Z axis (default False)

**Type:**

bool

<a id="bpy.types.SimpleDeformModifier.origin"></a>

#### bpy.types.SimpleDeformModifier.origin

Offset the origin and orientation of the deformation

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SimpleDeformModifier.vertex_group"></a>

#### bpy.types.SimpleDeformModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.SimpleDeformModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SimpleDeformModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SimpleDeformModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SimpleDeformModifier.bl_rna_get_subclass_py(id, default=None, /)

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
