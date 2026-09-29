<!-- source: Blender Python API reference 5.2 / bpy.types.ExplodeModifier.html -->

<a id="explodemodifier-modifier"></a>

# ExplodeModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ExplodeModifier"></a>

### class bpy.types.ExplodeModifier(Modifier)

Explosion effect modifier based on a particle system

<a id="bpy.types.ExplodeModifier.invert_vertex_group"></a>

#### bpy.types.ExplodeModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.particle_uv"></a>

#### bpy.types.ExplodeModifier.particle_uv

UV map to change with particle age (default “”, never None)

**Type:**

str

<a id="bpy.types.ExplodeModifier.protect"></a>

#### bpy.types.ExplodeModifier.protect

Clean vertex group edges (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ExplodeModifier.show_alive"></a>

#### bpy.types.ExplodeModifier.show_alive

Show mesh when particles are alive (default True)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.show_dead"></a>

#### bpy.types.ExplodeModifier.show_dead

Show mesh when particles are dead (default True)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.show_unborn"></a>

#### bpy.types.ExplodeModifier.show_unborn

Show mesh when particles are unborn (default True)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.use_edge_cut"></a>

#### bpy.types.ExplodeModifier.use_edge_cut

Cut face edges for nicer shrapnel (default False)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.use_size"></a>

#### bpy.types.ExplodeModifier.use_size

Use particle size for the shrapnel (default False)

**Type:**

bool

<a id="bpy.types.ExplodeModifier.vertex_group"></a>

#### bpy.types.ExplodeModifier.vertex_group

(default “”, never None)

**Type:**

str

<a id="bpy.types.ExplodeModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ExplodeModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ExplodeModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ExplodeModifier.bl_rna_get_subclass_py(id, default=None, /)

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
