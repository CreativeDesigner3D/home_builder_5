<!-- source: Blender Python API reference 5.2 / bpy.types.MultiresModifier.html -->

<a id="multiresmodifier-modifier"></a>

# MultiresModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.MultiresModifier"></a>

### class bpy.types.MultiresModifier(Modifier)

Multiresolution mesh modifier

<a id="bpy.types.MultiresModifier.boundary_smooth"></a>

#### bpy.types.MultiresModifier.boundary_smooth

Controls how open boundaries are smoothed (default `'ALL'`)

**Type:**

Literal[[Subdivision Boundary Smooth Items](bpy_types_enum_items/subdivision_boundary_smooth_items.md#rna-enum-subdivision-boundary-smooth-items)]

<a id="bpy.types.MultiresModifier.filepath"></a>

#### bpy.types.MultiresModifier.filepath

Path to external displacements file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.MultiresModifier.is_external"></a>

#### bpy.types.MultiresModifier.is_external

Store multires displacements outside the .blend file, to save memory (default False, readonly)

**Type:**

bool

<a id="bpy.types.MultiresModifier.levels"></a>

#### bpy.types.MultiresModifier.levels

Number of subdivisions to use in the viewport (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.MultiresModifier.quality"></a>

#### bpy.types.MultiresModifier.quality

Accuracy of vertex positions, lower value is faster but less precise (in [1, 10], default 4)

**Type:**

int

<a id="bpy.types.MultiresModifier.render_levels"></a>

#### bpy.types.MultiresModifier.render_levels

The subdivision level visible at render time (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.MultiresModifier.sculpt_levels"></a>

#### bpy.types.MultiresModifier.sculpt_levels

Number of subdivisions to use in sculpt mode (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.MultiresModifier.show_only_control_edges"></a>

#### bpy.types.MultiresModifier.show_only_control_edges

Skip drawing/rendering of interior subdivided edges (default True)

**Type:**

bool

<a id="bpy.types.MultiresModifier.total_levels"></a>

#### bpy.types.MultiresModifier.total_levels

Number of subdivisions for which displacements are stored (in [0, 255], default 0, readonly)

**Type:**

int

<a id="bpy.types.MultiresModifier.use_creases"></a>

#### bpy.types.MultiresModifier.use_creases

Use mesh crease information to sharpen edges or corners (default True)

**Type:**

bool

<a id="bpy.types.MultiresModifier.use_custom_normals"></a>

#### bpy.types.MultiresModifier.use_custom_normals

Interpolates existing custom normals to resulting mesh (default False)

**Type:**

bool

<a id="bpy.types.MultiresModifier.use_sculpt_base_mesh"></a>

#### bpy.types.MultiresModifier.use_sculpt_base_mesh

Make Sculpt Mode tools deform the base mesh while previewing the displacement of higher subdivision levels (default False)

**Type:**

bool

<a id="bpy.types.MultiresModifier.uv_smooth"></a>

#### bpy.types.MultiresModifier.uv_smooth

Controls how smoothing is applied to UVs (default `'PRESERVE_BOUNDARIES'`)

**Type:**

Literal[[Subdivision Uv Smooth Items](bpy_types_enum_items/subdivision_uv_smooth_items.md#rna-enum-subdivision-uv-smooth-items)]

<a id="bpy.types.MultiresModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MultiresModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MultiresModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MultiresModifier.bl_rna_get_subclass_py(id, default=None, /)

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
