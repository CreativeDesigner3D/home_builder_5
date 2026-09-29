<!-- source: Blender Python API reference 5.2 / bpy.types.FloatProperty.html -->

<a id="floatproperty-property"></a>

# FloatProperty(Property)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")

<a id="bpy.types.FloatProperty"></a>

### class bpy.types.FloatProperty(Property)

RNA floating-point number (single precision) property definition

<a id="bpy.types.FloatProperty.array_dimensions"></a>

#### bpy.types.FloatProperty.array_dimensions

Length of each dimension of the array (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.FloatProperty.array_length"></a>

#### bpy.types.FloatProperty.array_length

Maximum length of the array, 0 means unlimited (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.FloatProperty.default"></a>

#### bpy.types.FloatProperty.default

Default value for this number (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.default_array"></a>

#### bpy.types.FloatProperty.default_array

Default value for this array (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FloatProperty.hard_max"></a>

#### bpy.types.FloatProperty.hard_max

Hard maximum, trying to assign a value above will silently assign this maximum instead (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.hard_min"></a>

#### bpy.types.FloatProperty.hard_min

Hard minimum, trying to assign a value below will silently assign this minimum instead (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.is_array"></a>

#### bpy.types.FloatProperty.is_array

(default False, readonly)

**Type:**

bool

<a id="bpy.types.FloatProperty.precision"></a>

#### bpy.types.FloatProperty.precision

Number of digits after the dot used by buttons. Fraction is automatically hidden for exact integer values of fields with unit ‘NONE’ or ‘TIME’ (frame count) and step divisible by 100. (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.FloatProperty.soft_max"></a>

#### bpy.types.FloatProperty.soft_max

Soft maximum (<= hard_max), user cannot drag widgets above this value in the UI (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.soft_min"></a>

#### bpy.types.FloatProperty.soft_min

Soft minimum (>= hard_min), user cannot drag widgets below this value in the UI (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.step"></a>

#### bpy.types.FloatProperty.step

Step size used by number buttons, for floats 1/100th of the step size (in [0, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.FloatProperty.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FloatProperty.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FloatProperty.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FloatProperty.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Property.name, Property.identifier, Property.description, Property.translation_context, Property.type, Property.subtype, Property.srna, Property.unit, Property.icon, Property.is_readonly, Property.is_animatable, Property.is_overridable, Property.is_required, Property.is_argument_optional, Property.is_never_none, Property.is_hidden, Property.is_skip_save, Property.is_skip_preset, Property.is_output, Property.is_registered, Property.is_registered_optional, Property.is_runtime, Property.is_enum_flag, Property.is_library_editable, Property.is_path_output, Property.is_path_supports_blend_relative, Property.is_path_supports_templates, Property.is_deprecated, Property.deprecated_note, Property.deprecated_version, Property.deprecated_removal_version, Property.tags

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Property.bl_rna_get_subclass, Property.bl_rna_get_subclass_py
