<!-- source: Blender Python API reference 5.2 / bpy.types.WorldMistSettings.html -->

<a id="worldmistsettings-bpy-struct"></a>

# WorldMistSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.WorldMistSettings"></a>

### class bpy.types.WorldMistSettings(bpy_struct)

Mist settings for a World data-block

<a id="bpy.types.WorldMistSettings.depth"></a>

#### bpy.types.WorldMistSettings.depth

Distance over which the mist effect fades in (in [0, inf], default 25.0)

**Type:**

float

<a id="bpy.types.WorldMistSettings.falloff"></a>

#### bpy.types.WorldMistSettings.falloff

Type of transition used to fade mist (default `'QUADRATIC'`)

- `QUADRATIC`
  Quadratic – Use quadratic progression.
- `LINEAR`
  Linear – Use linear progression.
- `INVERSE_QUADRATIC`
  Inverse Quadratic – Use inverse quadratic progression.

**Type:**

Literal[‘QUADRATIC’, ‘LINEAR’, ‘INVERSE_QUADRATIC’]

<a id="bpy.types.WorldMistSettings.height"></a>

#### bpy.types.WorldMistSettings.height

Control how much mist density decreases with height (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.WorldMistSettings.intensity"></a>

#### bpy.types.WorldMistSettings.intensity

Overall minimum intensity of the mist effect (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.WorldMistSettings.start"></a>

#### bpy.types.WorldMistSettings.start

Starting distance of the mist, measured from the camera (in [0, inf], default 5.0)

**Type:**

float

<a id="bpy.types.WorldMistSettings.use_mist"></a>

#### bpy.types.WorldMistSettings.use_mist

Occlude objects with the environment color as they are further away (default False)

**Type:**

bool

<a id="bpy.types.WorldMistSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WorldMistSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WorldMistSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WorldMistSettings.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`World.mist_settings`](bpy.types.World.md#bpy.types.World.mist_settings "bpy.types.World.mist_settings") |  |
