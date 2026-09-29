<!-- source: Blender Python API reference 5.2 / bpy_extras.keyconfig_utils.html -->

<a id="module-bpy_extras.keyconfig_utils"></a>

# bpy_extras submodule (bpy_extras.keyconfig_utils)

<a id="bpy_extras.keyconfig_utils.addon_keymap_register"></a>

### bpy_extras.keyconfig_utils.addon_keymap_register(keymap_data)

Register a set of keymaps for addons using a list of keymaps.

See ‘blender_default.py’ for examples of the format this takes.

**Parameters:**

**keymap_data** (list[tuple[str, dict[str, Any], dict[str, Any]]]) – A list of keymap definitions to register.

<a id="bpy_extras.keyconfig_utils.addon_keymap_unregister"></a>

### bpy_extras.keyconfig_utils.addon_keymap_unregister(keymap_data)

Unregister a set of keymaps for addons.

**Parameters:**

**keymap_data** (list[tuple[str, dict[str, Any], dict[str, Any]]]) – A list of keymap definitions to unregister.

<a id="bpy_extras.keyconfig_utils.keyconfig_test"></a>

### bpy_extras.keyconfig_utils.keyconfig_test(kc)

Test a key configuration for duplicate key-map item assignments.

**Parameters:**

**kc** ([`bpy.types.KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig")) – The key configuration to test.

**Returns:**

True if any duplicates were found.

**Return type:**

bool
