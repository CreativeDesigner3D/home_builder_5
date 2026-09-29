<!-- source: Blender Python API reference 5.2 / bpy.types.StringProperty.html -->

<a id="stringproperty-property"></a>

# StringProperty(Property)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")

<a id="bpy.types.StringProperty"></a>

### class bpy.types.StringProperty(Property)

RNA text string property definition

<a id="bpy.types.StringProperty.default"></a>

#### bpy.types.StringProperty.default

String default value (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.StringProperty.length_max"></a>

#### bpy.types.StringProperty.length_max

Maximum length of the string, 0 means unlimited (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.StringProperty.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StringProperty.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StringProperty.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StringProperty.bl_rna_get_subclass_py(id, default=None, /)

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

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Struct.name_property`](bpy.types.Struct.md#bpy.types.Struct.name_property "bpy.types.Struct.name_property") |  |
