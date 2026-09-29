<!-- source: Blender Python API reference 5.2 / bpy.types.WarpModifier.html -->

<a id="warpmodifier-modifier"></a>

# WarpModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.WarpModifier"></a>

### class bpy.types.WarpModifier(Modifier)

Warp modifier

<a id="bpy.types.WarpModifier.bone_from"></a>

#### bpy.types.WarpModifier.bone_from

Bone to transform from (default “”, never None)

**Type:**

str

<a id="bpy.types.WarpModifier.bone_to"></a>

#### bpy.types.WarpModifier.bone_to

Bone defining offset (default “”, never None)

**Type:**

str

<a id="bpy.types.WarpModifier.falloff_curve"></a>

#### bpy.types.WarpModifier.falloff_curve

Custom falloff curve (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.WarpModifier.falloff_radius"></a>

#### bpy.types.WarpModifier.falloff_radius

Radius to apply (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.WarpModifier.falloff_type"></a>

#### bpy.types.WarpModifier.falloff_type

(default `'SMOOTH'`)

**Type:**

Literal[‘NONE’, ‘CURVE’, ‘SMOOTH’, ‘SPHERE’, ‘ROOT’, ‘INVERSE_SQUARE’, ‘SHARP’, ‘LINEAR’, ‘CONSTANT’]

<a id="bpy.types.WarpModifier.invert_vertex_group"></a>

#### bpy.types.WarpModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.WarpModifier.object_from"></a>

#### bpy.types.WarpModifier.object_from

Object to transform from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.WarpModifier.object_to"></a>

#### bpy.types.WarpModifier.object_to

Object to transform to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.WarpModifier.strength"></a>

#### bpy.types.WarpModifier.strength

(in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.WarpModifier.texture"></a>

#### bpy.types.WarpModifier.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.WarpModifier.texture_coords"></a>

#### bpy.types.WarpModifier.texture_coords

(default `'LOCAL'`)

- `LOCAL`
  Local – Use the local coordinate system for the texture coordinates.
- `GLOBAL`
  Global – Use the global coordinate system for the texture coordinates.
- `OBJECT`
  Object – Use the linked object’s local coordinate system for the texture coordinates.
- `UV`
  UV – Use UV coordinates for the texture coordinates.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’, ‘OBJECT’, ‘UV’]

<a id="bpy.types.WarpModifier.texture_coords_bone"></a>

#### bpy.types.WarpModifier.texture_coords_bone

Bone to set the texture coordinates (default “”, never None)

**Type:**

str

<a id="bpy.types.WarpModifier.texture_coords_object"></a>

#### bpy.types.WarpModifier.texture_coords_object

Object to set the texture coordinates

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.WarpModifier.use_volume_preserve"></a>

#### bpy.types.WarpModifier.use_volume_preserve

Preserve volume when rotations are used (default False)

**Type:**

bool

<a id="bpy.types.WarpModifier.uv_layer"></a>

#### bpy.types.WarpModifier.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.WarpModifier.vertex_group"></a>

#### bpy.types.WarpModifier.vertex_group

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.WarpModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WarpModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WarpModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WarpModifier.bl_rna_get_subclass_py(id, default=None, /)

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
