<!-- source: Blender Python API reference 5.2 / bpy.types.Property.html -->

<a id="property-bpy-struct"></a>

# Property(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [BoolProperty(Property)](bpy.types.BoolProperty.md)
- [CollectionProperty(Property)](bpy.types.CollectionProperty.md)
- [EnumProperty(Property)](bpy.types.EnumProperty.md)
- [FloatProperty(Property)](bpy.types.FloatProperty.md)
- [IntProperty(Property)](bpy.types.IntProperty.md)
- [PointerProperty(Property)](bpy.types.PointerProperty.md)
- [StringProperty(Property)](bpy.types.StringProperty.md)

<a id="bpy.types.Property"></a>

### class bpy.types.Property(bpy_struct)

RNA property definition

<a id="bpy.types.Property.deprecated_note"></a>

#### bpy.types.Property.deprecated_note

A note regarding deprecation (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Property.deprecated_removal_version"></a>

#### bpy.types.Property.deprecated_removal_version

The Blender version this is expected to be removed (array of 3 items, in [-inf, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Property.deprecated_version"></a>

#### bpy.types.Property.deprecated_version

The Blender version this was deprecated (array of 3 items, in [-inf, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Property.description"></a>

#### bpy.types.Property.description

Description of the property for tooltips (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Property.icon"></a>

#### bpy.types.Property.icon

Icon of the item (default `'NONE'`, readonly)

**Type:**

Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]

<a id="bpy.types.Property.identifier"></a>

#### bpy.types.Property.identifier

Unique name used in the code and scripting (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Property.is_animatable"></a>

#### bpy.types.Property.is_animatable

Property is animatable through RNA (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_argument_optional"></a>

#### bpy.types.Property.is_argument_optional

True when the property is optional in a Python function implementing an RNA function (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_deprecated"></a>

#### bpy.types.Property.is_deprecated

The property is deprecated (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_enum_flag"></a>

#### bpy.types.Property.is_enum_flag

True when multiple enums (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_hidden"></a>

#### bpy.types.Property.is_hidden

True when the property is hidden (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_library_editable"></a>

#### bpy.types.Property.is_library_editable

Property is editable from linked instances (changes not saved) (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_never_none"></a>

#### bpy.types.Property.is_never_none

True when this value cannot be set to None (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_output"></a>

#### bpy.types.Property.is_output

True when this property is an output value from an RNA function (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_overridable"></a>

#### bpy.types.Property.is_overridable

Property is overridable through RNA (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_path_output"></a>

#### bpy.types.Property.is_path_output

Property is a filename, filepath or directory output (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_path_supports_blend_relative"></a>

#### bpy.types.Property.is_path_supports_blend_relative

Property is a path which supports the “//” prefix, signifying the location as relative to the “.blend” file’s directory (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_path_supports_templates"></a>

#### bpy.types.Property.is_path_supports_templates

Property is a path which supports the “{variable_name}” variable expression syntax, which substitutes the value of the referenced variable in place of the expression (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_readonly"></a>

#### bpy.types.Property.is_readonly

Property is editable through RNA (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_registered"></a>

#### bpy.types.Property.is_registered

Property is registered as part of type registration (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_registered_optional"></a>

#### bpy.types.Property.is_registered_optional

Property is optionally registered as part of type registration (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_required"></a>

#### bpy.types.Property.is_required

False when this property is an optional argument in an RNA function (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_runtime"></a>

#### bpy.types.Property.is_runtime

Property has been dynamically created at runtime (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_skip_preset"></a>

#### bpy.types.Property.is_skip_preset

True when the property is not saved in presets (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.is_skip_save"></a>

#### bpy.types.Property.is_skip_save

True when the property uses ghost values (default False, readonly)

**Type:**

bool

<a id="bpy.types.Property.name"></a>

#### bpy.types.Property.name

Human readable name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Property.srna"></a>

#### bpy.types.Property.srna

Struct definition used for properties assigned to this item (readonly)

**Type:**

[`Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None

<a id="bpy.types.Property.subtype"></a>

#### bpy.types.Property.subtype

Semantic interpretation of the property (default `'NONE'`, readonly)

**Type:**

Literal[[Property Subtype Items](bpy_types_enum_items/property_subtype_items.md#rna-enum-property-subtype-items)]

<a id="bpy.types.Property.tags"></a>

#### bpy.types.Property.tags

Subset of tags (defined in parent struct) that are set for this property (default set(), readonly)

**Type:**

set[str]

<a id="bpy.types.Property.translation_context"></a>

#### bpy.types.Property.translation_context

Translation context of the property’s name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Property.type"></a>

#### bpy.types.Property.type

Data type of the property (default `'BOOLEAN'`, readonly)

**Type:**

Literal[[Property Type Items](bpy_types_enum_items/property_type_items.md#rna-enum-property-type-items)]

<a id="bpy.types.Property.unit"></a>

#### bpy.types.Property.unit

Type of units for this property (default `'NONE'`, readonly)

**Type:**

Literal[[Property Unit Items](bpy_types_enum_items/property_unit_items.md#rna-enum-property-unit-items)]

<a id="bpy.types.Property.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Property.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Property.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Property.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Property.type "bpy.types.Property.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Property.type "bpy.types.Property.type")

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
| - `bpy.context.texture_user_property` - [`Function.parameters`](bpy.types.Function.md#bpy.types.Function.parameters "bpy.types.Function.parameters") | - [`Struct.properties`](bpy.types.Struct.md#bpy.types.Struct.properties "bpy.types.Struct.properties") |
