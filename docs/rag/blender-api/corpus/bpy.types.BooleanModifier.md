<!-- source: Blender Python API reference 5.2 / bpy.types.BooleanModifier.html -->

<a id="booleanmodifier-modifier"></a>

# BooleanModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.BooleanModifier"></a>

### class bpy.types.BooleanModifier(Modifier)

Boolean operations modifier

<a id="bpy.types.BooleanModifier.collection"></a>

#### bpy.types.BooleanModifier.collection

Use mesh objects in this collection for Boolean operation

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.BooleanModifier.debug_options"></a>

#### bpy.types.BooleanModifier.debug_options

Debugging options, only when started with ‘-d’ (default set())

**Type:**

set[Literal[‘SEPARATE’, ‘NO_DISSOLVE’, ‘NO_CONNECT_REGIONS’]]

<a id="bpy.types.BooleanModifier.double_threshold"></a>

#### bpy.types.BooleanModifier.double_threshold

Threshold for checking overlapping geometry (in [0, 1], default 1e-06)

**Type:**

float

<a id="bpy.types.BooleanModifier.material_mode"></a>

#### bpy.types.BooleanModifier.material_mode

Method for setting materials on the new faces (default `'INDEX'`)

- `INDEX`
  Index Based – Set the material on new faces based on the order of the material slot lists. If a material does not exist on the modifier object, the face will use the same material slot or the first if the object does not have enough slots..
- `TRANSFER`
  Transfer – Transfer materials from non-empty slots to the result mesh, adding new materials as necessary. For empty slots, fall back to using the same material index as the operand mesh..

**Type:**

Literal[‘INDEX’, ‘TRANSFER’]

<a id="bpy.types.BooleanModifier.object"></a>

#### bpy.types.BooleanModifier.object

Mesh object to use for Boolean operation

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.BooleanModifier.operand_type"></a>

#### bpy.types.BooleanModifier.operand_type

(default `'OBJECT'`)

- `OBJECT`
  Object – Use a mesh object as the operand for the Boolean operation.
- `COLLECTION`
  Collection – Use a collection of mesh objects as the operand for the Boolean operation.

**Type:**

Literal[‘OBJECT’, ‘COLLECTION’]

<a id="bpy.types.BooleanModifier.operation"></a>

#### bpy.types.BooleanModifier.operation

(default `'DIFFERENCE'`)

- `INTERSECT`
  Intersect – Keep the part of the mesh that is common between all operands.
- `UNION`
  Union – Combine meshes in an additive way.
- `DIFFERENCE`
  Difference – Combine meshes in a subtractive way.

**Type:**

Literal[‘INTERSECT’, ‘UNION’, ‘DIFFERENCE’]

<a id="bpy.types.BooleanModifier.solver"></a>

#### bpy.types.BooleanModifier.solver

Method for calculating booleans (default `'EXACT'`)

- `FLOAT`
  Float – Simple solver with good performance, without support for overlapping geometry.
- `EXACT`
  Exact – Slower solver with the best results for coplanar faces.
- `MANIFOLD`
  Manifold – Fastest solver that works only on manifold meshes but gives better results.

**Type:**

Literal[‘FLOAT’, ‘EXACT’, ‘MANIFOLD’]

<a id="bpy.types.BooleanModifier.use_hole_tolerant"></a>

#### bpy.types.BooleanModifier.use_hole_tolerant

Better results when there are holes (slower) (default False)

**Type:**

bool

<a id="bpy.types.BooleanModifier.use_self"></a>

#### bpy.types.BooleanModifier.use_self

Allow self-intersection in operands (default False)

**Type:**

bool

<a id="bpy.types.BooleanModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BooleanModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BooleanModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BooleanModifier.bl_rna_get_subclass_py(id, default=None, /)

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
