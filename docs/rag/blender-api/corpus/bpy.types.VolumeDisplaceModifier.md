<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeDisplaceModifier.html -->

<a id="volumedisplacemodifier-modifier"></a>

# VolumeDisplaceModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.VolumeDisplaceModifier"></a>

### class bpy.types.VolumeDisplaceModifier(Modifier)

<a id="bpy.types.VolumeDisplaceModifier.strength"></a>

#### bpy.types.VolumeDisplaceModifier.strength

Strength of the displacement (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeDisplaceModifier.texture"></a>

#### bpy.types.VolumeDisplaceModifier.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.VolumeDisplaceModifier.texture_map_mode"></a>

#### bpy.types.VolumeDisplaceModifier.texture_map_mode

(default `'LOCAL'`)

- `LOCAL`
  Local – Use the local coordinate system for the texture coordinates.
- `GLOBAL`
  Global – Use the global coordinate system for the texture coordinates.
- `OBJECT`
  Object – Use the linked object’s local coordinate system for the texture coordinates.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’, ‘OBJECT’]

<a id="bpy.types.VolumeDisplaceModifier.texture_map_object"></a>

#### bpy.types.VolumeDisplaceModifier.texture_map_object

Object to use for texture mapping

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VolumeDisplaceModifier.texture_mid_level"></a>

#### bpy.types.VolumeDisplaceModifier.texture_mid_level

Subtracted from the texture color to get a displacement vector (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.VolumeDisplaceModifier.texture_sample_radius"></a>

#### bpy.types.VolumeDisplaceModifier.texture_sample_radius

Smaller values result in better performance but might cut off the volume (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VolumeDisplaceModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeDisplaceModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeDisplaceModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeDisplaceModifier.bl_rna_get_subclass_py(id, default=None, /)

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
