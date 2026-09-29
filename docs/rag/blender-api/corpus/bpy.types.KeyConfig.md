<!-- source: Blender Python API reference 5.2 / bpy.types.KeyConfig.html -->

<a id="keyconfig-bpy-struct"></a>

# KeyConfig(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.KeyConfig"></a>

### class bpy.types.KeyConfig(bpy_struct)

Input configuration, including keymaps

<a id="bpy.types.KeyConfig.is_user_defined"></a>

#### bpy.types.KeyConfig.is_user_defined

Indicates that a keyconfig was defined by the user (default False, readonly)

**Type:**

bool

<a id="bpy.types.KeyConfig.keymaps"></a>

#### bpy.types.KeyConfig.keymaps

Key maps configured as part of this configuration (default None, readonly)

**Type:**

[`KeyMaps`](bpy.types.KeyMaps.md#bpy.types.KeyMaps "bpy.types.KeyMaps")[[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")]

<a id="bpy.types.KeyConfig.name"></a>

#### bpy.types.KeyConfig.name

Name of the key configuration (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyConfig.preferences"></a>

#### bpy.types.KeyConfig.preferences

(readonly)

**Type:**

[`KeyConfigPreferences`](bpy.types.KeyConfigPreferences.md#bpy.types.KeyConfigPreferences "bpy.types.KeyConfigPreferences") | None

<a id="bpy.types.KeyConfig.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyConfig.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyConfig.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyConfig.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GizmoGroup.setup_keymap`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.setup_keymap "bpy.types.GizmoGroup.setup_keymap") - [`KeyConfigurations.active`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.active "bpy.types.KeyConfigurations.active") - [`KeyConfigurations.addon`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.addon "bpy.types.KeyConfigurations.addon") - [`KeyConfigurations.default`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.default "bpy.types.KeyConfigurations.default") | - [`KeyConfigurations.new`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.new "bpy.types.KeyConfigurations.new") - [`KeyConfigurations.remove`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.remove "bpy.types.KeyConfigurations.remove") - [`KeyConfigurations.user`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.user "bpy.types.KeyConfigurations.user") - [`WindowManager.keyconfigs`](bpy.types.WindowManager.md#bpy.types.WindowManager.keyconfigs "bpy.types.WindowManager.keyconfigs") |
