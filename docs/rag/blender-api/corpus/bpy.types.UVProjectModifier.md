<!-- source: Blender Python API reference 5.2 / bpy.types.UVProjectModifier.html -->

<a id="uvprojectmodifier-modifier"></a>

# UVProjectModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.UVProjectModifier"></a>

### class bpy.types.UVProjectModifier(Modifier)

UV projection modifier to set UVs from a projector

<a id="bpy.types.UVProjectModifier.aspect_x"></a>

#### bpy.types.UVProjectModifier.aspect_x

Horizontal aspect ratio (only used for camera projectors) (in [1, inf], default 1.0)

**Type:**

float

<a id="bpy.types.UVProjectModifier.aspect_y"></a>

#### bpy.types.UVProjectModifier.aspect_y

Vertical aspect ratio (only used for camera projectors) (in [1, inf], default 1.0)

**Type:**

float

<a id="bpy.types.UVProjectModifier.projector_count"></a>

#### bpy.types.UVProjectModifier.projector_count

Number of projectors to use (in [1, 10], default 1)

**Type:**

int

<a id="bpy.types.UVProjectModifier.projectors"></a>

#### bpy.types.UVProjectModifier.projectors

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`UVProjector`](bpy.types.UVProjector.md#bpy.types.UVProjector "bpy.types.UVProjector")]

<a id="bpy.types.UVProjectModifier.scale_x"></a>

#### bpy.types.UVProjectModifier.scale_x

Horizontal scale (only used for camera projectors) (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.UVProjectModifier.scale_y"></a>

#### bpy.types.UVProjectModifier.scale_y

Vertical scale (only used for camera projectors) (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.UVProjectModifier.uv_layer"></a>

#### bpy.types.UVProjectModifier.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.UVProjectModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UVProjectModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UVProjectModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UVProjectModifier.bl_rna_get_subclass_py(id, default=None, /)

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
