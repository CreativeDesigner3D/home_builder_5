<!-- source: Blender Python API reference 5.2 / bpy.types.ActionChannelbag.html -->

<a id="actionchannelbag-bpy-struct"></a>

# ActionChannelbag(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ActionChannelbag"></a>

### class bpy.types.ActionChannelbag(bpy_struct)

Collection of animation channels, typically associated with an action slot

<a id="bpy.types.ActionChannelbag.fcurves"></a>

#### bpy.types.ActionChannelbag.fcurves

The individual F-Curves that animate the slot (default None, readonly)

**Type:**

[`ActionChannelbagFCurves`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves "bpy.types.ActionChannelbagFCurves")[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.ActionChannelbag.groups"></a>

#### bpy.types.ActionChannelbag.groups

Groupings of F-Curves for display purposes, in e.g. the dopesheet and graph editor (default None, readonly)

**Type:**

[`ActionChannelbagGroups`](bpy.types.ActionChannelbagGroups.md#bpy.types.ActionChannelbagGroups "bpy.types.ActionChannelbagGroups")[[`ActionGroup`](bpy.types.ActionGroup.md#bpy.types.ActionGroup "bpy.types.ActionGroup")]

<a id="bpy.types.ActionChannelbag.slot"></a>

#### bpy.types.ActionChannelbag.slot

The Slot that the Channelbag’s animation data is for (readonly)

**Type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy.types.ActionChannelbag.slot_handle"></a>

#### bpy.types.ActionChannelbag.slot_handle

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ActionChannelbag.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionChannelbag.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionChannelbag.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionChannelbag.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ActionChannelbags.new`](bpy.types.ActionChannelbags.md#bpy.types.ActionChannelbags.new "bpy.types.ActionChannelbags.new") - [`ActionChannelbags.remove`](bpy.types.ActionChannelbags.md#bpy.types.ActionChannelbags.remove "bpy.types.ActionChannelbags.remove") | - [`ActionKeyframeStrip.channelbag`](bpy.types.ActionKeyframeStrip.md#bpy.types.ActionKeyframeStrip.channelbag "bpy.types.ActionKeyframeStrip.channelbag") - [`ActionKeyframeStrip.channelbags`](bpy.types.ActionKeyframeStrip.md#bpy.types.ActionKeyframeStrip.channelbags "bpy.types.ActionKeyframeStrip.channelbags") |
