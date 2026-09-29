<!-- source: Blender Python API reference 5.2 / bpy.types.Mask.html -->

<a id="mask-id"></a>

# Mask(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Mask"></a>

### class bpy.types.Mask(ID)

Mask data-block defining mask for compositing

<a id="bpy.types.Mask.active_layer_index"></a>

#### bpy.types.Mask.active_layer_index

Index of active layer in list of all mask’s layers (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Mask.animation_data"></a>

#### bpy.types.Mask.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Mask.frame_end"></a>

#### bpy.types.Mask.frame_end

Final frame of the mask (used for sequencer) (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.Mask.frame_start"></a>

#### bpy.types.Mask.frame_start

First frame of the mask (used for sequencer) (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.Mask.layers"></a>

#### bpy.types.Mask.layers

Collection of layers which defines this mask (default None, readonly)

**Type:**

[`MaskLayers`](bpy.types.MaskLayers.md#bpy.types.MaskLayers "bpy.types.MaskLayers")[[`MaskLayer`](bpy.types.MaskLayer.md#bpy.types.MaskLayer "bpy.types.MaskLayer")]

<a id="bpy.types.Mask.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Mask.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Mask.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Mask.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.edit_mask` - [`BlendData.masks`](bpy.types.BlendData.md#bpy.types.BlendData.masks "bpy.types.BlendData.masks") - [`BlendDataMasks.new`](bpy.types.BlendDataMasks.md#bpy.types.BlendDataMasks.new "bpy.types.BlendDataMasks.new") - [`BlendDataMasks.remove`](bpy.types.BlendDataMasks.md#bpy.types.BlendDataMasks.remove "bpy.types.BlendDataMasks.remove") - [`CompositorNodeMask.mask`](bpy.types.CompositorNodeMask.md#bpy.types.CompositorNodeMask.mask "bpy.types.CompositorNodeMask.mask") - [`MaskStrip.mask`](bpy.types.MaskStrip.md#bpy.types.MaskStrip.mask "bpy.types.MaskStrip.mask") - [`NodeSocketMask.default_value`](bpy.types.NodeSocketMask.md#bpy.types.NodeSocketMask.default_value "bpy.types.NodeSocketMask.default_value") | - [`NodeTreeInterfaceSocketMask.default_value`](bpy.types.NodeTreeInterfaceSocketMask.md#bpy.types.NodeTreeInterfaceSocketMask.default_value "bpy.types.NodeTreeInterfaceSocketMask.default_value") - [`SpaceClipEditor.mask`](bpy.types.SpaceClipEditor.md#bpy.types.SpaceClipEditor.mask "bpy.types.SpaceClipEditor.mask") - [`SpaceImageEditor.mask`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.mask "bpy.types.SpaceImageEditor.mask") - [`StripModifier.input_mask_id`](bpy.types.StripModifier.md#bpy.types.StripModifier.input_mask_id "bpy.types.StripModifier.input_mask_id") - [`StripsMeta.new_mask`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_mask "bpy.types.StripsMeta.new_mask") - [`StripsTopLevel.new_mask`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_mask "bpy.types.StripsTopLevel.new_mask") |
