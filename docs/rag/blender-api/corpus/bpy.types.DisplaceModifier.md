<!-- source: Blender Python API reference 5.2 / bpy.types.DisplaceModifier.html -->

<a id="displacemodifier-modifier"></a>

# DisplaceModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.DisplaceModifier"></a>

### class bpy.types.DisplaceModifier(Modifier)

Displacement modifier

<a id="bpy.types.DisplaceModifier.direction"></a>

#### bpy.types.DisplaceModifier.direction

(default `'NORMAL'`)

- `X`
  X – Use the texture’s intensity value to displace in the X direction.
- `Y`
  Y – Use the texture’s intensity value to displace in the Y direction.
- `Z`
  Z – Use the texture’s intensity value to displace in the Z direction.
- `NORMAL`
  Normal – Use the texture’s intensity value to displace along the vertex normal.
- `CUSTOM_NORMAL`
  Custom Normal – Use the texture’s intensity value to displace along the (averaged) custom normal (falls back to vertex).
- `RGB_TO_XYZ`
  RGB to XYZ – Use the texture’s RGB values to displace the mesh in the XYZ direction.

**Type:**

Literal[‘X’, ‘Y’, ‘Z’, ‘NORMAL’, ‘CUSTOM_NORMAL’, ‘RGB_TO_XYZ’]

<a id="bpy.types.DisplaceModifier.invert_vertex_group"></a>

#### bpy.types.DisplaceModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.DisplaceModifier.mid_level"></a>

#### bpy.types.DisplaceModifier.mid_level

Material value that gives no displacement (in [-inf, inf], default 0.5)

**Type:**

float

<a id="bpy.types.DisplaceModifier.space"></a>

#### bpy.types.DisplaceModifier.space

(default `'LOCAL'`)

- `LOCAL`
  Local – Direction is defined in local coordinates.
- `GLOBAL`
  Global – Direction is defined in global coordinates.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’]

<a id="bpy.types.DisplaceModifier.strength"></a>

#### bpy.types.DisplaceModifier.strength

Amount to displace geometry (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.DisplaceModifier.texture"></a>

#### bpy.types.DisplaceModifier.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.DisplaceModifier.texture_coords"></a>

#### bpy.types.DisplaceModifier.texture_coords

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

<a id="bpy.types.DisplaceModifier.texture_coords_bone"></a>

#### bpy.types.DisplaceModifier.texture_coords_bone

Bone to set the texture coordinates (default “”, never None)

**Type:**

str

<a id="bpy.types.DisplaceModifier.texture_coords_object"></a>

#### bpy.types.DisplaceModifier.texture_coords_object

Object to set the texture coordinates

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.DisplaceModifier.uv_layer"></a>

#### bpy.types.DisplaceModifier.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.DisplaceModifier.vertex_group"></a>

#### bpy.types.DisplaceModifier.vertex_group

Name of Vertex Group which determines influence of modifier per point (default “”, never None)

**Type:**

str

<a id="bpy.types.DisplaceModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DisplaceModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DisplaceModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DisplaceModifier.bl_rna_get_subclass_py(id, default=None, /)

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
