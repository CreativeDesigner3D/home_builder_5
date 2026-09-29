<!-- source: Blender Python API reference 5.2 / bpy.types.Lattice.html -->

<a id="lattice-id"></a>

# Lattice(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Lattice"></a>

### class bpy.types.Lattice(ID)

Lattice data-block defining a grid for deforming other objects

<a id="bpy.types.Lattice.animation_data"></a>

#### bpy.types.Lattice.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Lattice.interpolation_type_u"></a>

#### bpy.types.Lattice.interpolation_type_u

(default `'KEY_BSPLINE'`)

**Type:**

Literal[‘KEY_LINEAR’, ‘KEY_CARDINAL’, ‘KEY_CATMULL_ROM’, ‘KEY_BSPLINE’]

<a id="bpy.types.Lattice.interpolation_type_v"></a>

#### bpy.types.Lattice.interpolation_type_v

(default `'KEY_BSPLINE'`)

**Type:**

Literal[‘KEY_LINEAR’, ‘KEY_CARDINAL’, ‘KEY_CATMULL_ROM’, ‘KEY_BSPLINE’]

<a id="bpy.types.Lattice.interpolation_type_w"></a>

#### bpy.types.Lattice.interpolation_type_w

(default `'KEY_BSPLINE'`)

**Type:**

Literal[‘KEY_LINEAR’, ‘KEY_CARDINAL’, ‘KEY_CATMULL_ROM’, ‘KEY_BSPLINE’]

<a id="bpy.types.Lattice.is_editmode"></a>

#### bpy.types.Lattice.is_editmode

True when used in editmode (default False, readonly)

**Type:**

bool

<a id="bpy.types.Lattice.points"></a>

#### bpy.types.Lattice.points

Points of the lattice (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`LatticePoint`](bpy.types.LatticePoint.md#bpy.types.LatticePoint "bpy.types.LatticePoint")]

<a id="bpy.types.Lattice.points_u"></a>

#### bpy.types.Lattice.points_u

Points in U direction (cannot be changed when there are shape keys) (in [1, 64], default 0)

**Type:**

int

<a id="bpy.types.Lattice.points_v"></a>

#### bpy.types.Lattice.points_v

Points in V direction (cannot be changed when there are shape keys) (in [1, 64], default 0)

**Type:**

int

<a id="bpy.types.Lattice.points_w"></a>

#### bpy.types.Lattice.points_w

Points in W direction (cannot be changed when there are shape keys) (in [1, 64], default 0)

**Type:**

int

<a id="bpy.types.Lattice.shape_keys"></a>

#### bpy.types.Lattice.shape_keys

(readonly)

**Type:**

[`Key`](bpy.types.Key.md#bpy.types.Key "bpy.types.Key") | None

<a id="bpy.types.Lattice.use_outside"></a>

#### bpy.types.Lattice.use_outside

Only display and take into account the outer vertices (default False)

**Type:**

bool

<a id="bpy.types.Lattice.vertex_group"></a>

#### bpy.types.Lattice.vertex_group

Vertex group to apply the influence of the lattice (default “”, never None)

**Type:**

str

<a id="bpy.types.Lattice.transform"></a>

#### bpy.types.Lattice.transform(matrix, *, shape_keys=False)

Transform lattice by a matrix

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **shape_keys** (bool) – Transform Shape Keys (optional)

<a id="bpy.types.Lattice.update_gpu_tag"></a>

#### bpy.types.Lattice.update_gpu_tag()

update_gpu_tag

<a id="bpy.types.Lattice.unit_test_compare"></a>

#### bpy.types.Lattice.unit_test_compare(*, lattice=None, threshold=7.1526e-06)

unit_test_compare

**Parameters:**

- **lattice** ([`Lattice`](#bpy.types.Lattice "bpy.types.Lattice") | None) – Lattice to compare to (optional)
- **threshold** (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)

**Returns:**

Return value, String description of result of comparison (never None)

**Return type:**

str

<a id="bpy.types.Lattice.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Lattice.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Lattice.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Lattice.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - `bpy.context.lattice` - [`BlendData.lattices`](bpy.types.BlendData.md#bpy.types.BlendData.lattices "bpy.types.BlendData.lattices") - [`BlendDataLattices.new`](bpy.types.BlendDataLattices.md#bpy.types.BlendDataLattices.new "bpy.types.BlendDataLattices.new") | - [`BlendDataLattices.remove`](bpy.types.BlendDataLattices.md#bpy.types.BlendDataLattices.remove "bpy.types.BlendDataLattices.remove") - [`Lattice.unit_test_compare`](#bpy.types.Lattice.unit_test_compare "bpy.types.Lattice.unit_test_compare") |
