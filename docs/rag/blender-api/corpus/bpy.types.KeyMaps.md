<!-- source: Blender Python API reference 5.2 / bpy.types.KeyMaps.html -->

<a id="keymaps-bpy-prop-collection"></a>

# KeyMaps(bpy_prop_collection)

<a id="add-on-keymap-registration"></a>

## Add-on Keymap Registration

This example shows how an add-on can register custom keyboard shortcuts.
Keymaps are added to `keyconfigs.addon` and removed when unregistered.

Store `(keymap, keymap_item)` tuples for safe cleanup, as multiple add-ons may use the same keymap.

> **Note:**
>
> Users can customize add-on shortcuts in the Keymap Preferences.
> Add-on keymaps appear under their respective editors and can be
> modified or disabled without editing the add-on code.
>
> Add-ons should only manipulate keymaps in `keyconfigs.addon` and not manipulate the user’s keymaps
> because add-on keymaps serve as a default which users may customize.
> Modifying user keymaps directly interferes with users’ own preferences.

> **Warning:**
>
> Add-ons can add items to existing modal keymaps but cannot create
> new modal keymaps via Python. Use `modal=True` when targeting
> an existing modal keymap such as “Knife Tool Modal Map”.

```python
# In this example keymap registration functions are only split out for clarity,
# so skipping keymap registration in background mode doesn't interfere with other registration logic.

import bpy

# Store (keymap, keymap_item) for cleanup on unregister.
addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:
        return  # Can be None in background mode.

    # Target the 3D View; name must match Blender's built-in keymap exactly.
    km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')

    # Bind Shift+Alt+K to frame selected objects.
    kmi = km.keymap_items.new(
        idname="view3d.view_selected",
        type='K',
        value='PRESS',
        shift=True,
        alt=True,
    )
    kmi.properties.use_all_regions = True

    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    register_keymaps()

def unregister():
    unregister_keymaps()

if __name__ == "__main__":
    register()
```

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.KeyMaps"></a>

### class bpy.types.KeyMaps(bpy_prop_collection)

Collection of keymaps

<a id="bpy.types.KeyMaps.new"></a>

#### bpy.types.KeyMaps.new(name, *, space_type='EMPTY', region_type='WINDOW', modal=False, tool=False)

Ensure the keymap exists. This will return the one with the given name/space type/region type, or create a new one if it does not exist yet.

**Parameters:**

- **name** (str) – Name, (never None)
- **space_type** (Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]) – Space Type, (optional)
- **region_type** (Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]) – Region Type, (optional)
- **modal** (bool) – Modal, Keymap for modal operators. Modal keymaps are not supported for `KeyConfigs.addons`. (optional)
- **tool** (bool) – Tool, Keymap for active tools (optional)

**Returns:**

Key Map, Added key map

**Return type:**

[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.KeyMaps.remove"></a>

#### bpy.types.KeyMaps.remove(keymap)

remove

**Parameters:**

**keymap** ([`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap") | None) – Key Map, Removed key map (never None)

<a id="bpy.types.KeyMaps.clear"></a>

#### bpy.types.KeyMaps.clear()

Remove all keymaps.

<a id="bpy.types.KeyMaps.find"></a>

#### bpy.types.KeyMaps.find(name, *, space_type='EMPTY', region_type='WINDOW')

find

**Parameters:**

- **name** (str) – Name, (never None)
- **space_type** (Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]) – Space Type, (optional)
- **region_type** (Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]) – Region Type, (optional)

**Returns:**

Key Map, Corresponding key map

**Return type:**

[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.KeyMaps.find_match"></a>

#### bpy.types.KeyMaps.find_match(keymap)

find_match

**Parameters:**

**keymap** ([`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap") | None) – Key Map, The key map for comparison

**Returns:**

Key Map, Corresponding key map

**Return type:**

[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.KeyMaps.find_modal"></a>

#### bpy.types.KeyMaps.find_modal(name)

find_modal

**Parameters:**

**name** (str) – Operator Name, (never None)

**Returns:**

Key Map, Corresponding key map

**Return type:**

[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.KeyMaps.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyMaps.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyMaps.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyMaps.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`KeyConfig.keymaps`](bpy.types.KeyConfig.md#bpy.types.KeyConfig.keymaps "bpy.types.KeyConfig.keymaps") |  |
