<!-- source: Blender Python API reference 5.2 / bpy.types.ActionKeyframeStrip.html -->

<a id="actionkeyframestrip-actionstrip"></a>

# ActionKeyframeStrip(ActionStrip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ActionStrip`](bpy.types.ActionStrip.md#bpy.types.ActionStrip "bpy.types.ActionStrip")

<a id="bpy.types.ActionKeyframeStrip"></a>

### class bpy.types.ActionKeyframeStrip(ActionStrip)

Strip with a set of F-Curves for each action slot

<a id="bpy.types.ActionKeyframeStrip.channelbags"></a>

#### bpy.types.ActionKeyframeStrip.channelbags

(default None, readonly)

**Type:**

[`ActionChannelbags`](bpy.types.ActionChannelbags.md#bpy.types.ActionChannelbags "bpy.types.ActionChannelbags")[[`ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag")]

<a id="bpy.types.ActionKeyframeStrip.channelbag"></a>

#### bpy.types.ActionKeyframeStrip.channelbag(slot, *, ensure=False)

Find the ActionChannelbag for a specific Slot

**Parameters:**

- **slot** ([`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None) – Slot, The slot for which to find the channelbag
- **ensure** (bool) – Create if necessary, Ensure the channelbag exists for this slot, creating it if necessary (optional)

**Returns:**

Channels

**Return type:**

[`ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag")

<a id="bpy.types.ActionKeyframeStrip.key_insert"></a>

#### bpy.types.ActionKeyframeStrip.key_insert(slot, data_path, array_index, value, time)

key_insert

**Parameters:**

- **slot** ([`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None) – Slot, The slot that identifies which ‘thing’ should be keyed
- **data_path** (str) – Data Path, F-Curve data path (never None)
- **array_index** (int) – Array Index, Index of the animated array element, or -1 if the property is not an array (in [-inf, inf])
- **value** (float) – Value to key, Value of the animated property (in [-inf, inf])
- **time** (float) – Time of the key, Time, in frames, of the key (in [-inf, inf])

**Returns:**

Success, Whether the key was successfully inserted

**Return type:**

bool

<a id="bpy.types.ActionKeyframeStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionKeyframeStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionKeyframeStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionKeyframeStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ActionStrip.type

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ActionStrip.bl_rna_get_subclass, ActionStrip.bl_rna_get_subclass_py
