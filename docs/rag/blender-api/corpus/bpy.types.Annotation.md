<!-- source: Blender Python API reference 5.2 / bpy.types.Annotation.html -->

<a id="annotation-id"></a>

# Annotation(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Annotation"></a>

### class bpy.types.Annotation(ID)

Freehand annotation sketchbook

<a id="bpy.types.Annotation.animation_data"></a>

#### bpy.types.Annotation.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Annotation.layers"></a>

#### bpy.types.Annotation.layers

(default None, readonly)

**Type:**

[`AnnotationLayers`](bpy.types.AnnotationLayers.md#bpy.types.AnnotationLayers "bpy.types.AnnotationLayers")[[`AnnotationLayer`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer "bpy.types.AnnotationLayer")]

<a id="bpy.types.Annotation.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Annotation.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Annotation.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Annotation.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.annotations`](bpy.types.BlendData.md#bpy.types.BlendData.annotations "bpy.types.BlendData.annotations") - [`BlendDataAnnotations.new`](bpy.types.BlendDataAnnotations.md#bpy.types.BlendDataAnnotations.new "bpy.types.BlendDataAnnotations.new") - [`BlendDataAnnotations.remove`](bpy.types.BlendDataAnnotations.md#bpy.types.BlendDataAnnotations.remove "bpy.types.BlendDataAnnotations.remove") - [`MovieClip.annotation`](bpy.types.MovieClip.md#bpy.types.MovieClip.annotation "bpy.types.MovieClip.annotation") - [`MovieTrackingTrack.annotation`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack.annotation "bpy.types.MovieTrackingTrack.annotation") | - [`NodeTree.annotation`](bpy.types.NodeTree.md#bpy.types.NodeTree.annotation "bpy.types.NodeTree.annotation") - [`Scene.annotation`](bpy.types.Scene.md#bpy.types.Scene.annotation "bpy.types.Scene.annotation") - [`SpaceImageEditor.annotation`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.annotation "bpy.types.SpaceImageEditor.annotation") - [`SpaceSequenceEditor.annotation`](bpy.types.SpaceSequenceEditor.md#bpy.types.SpaceSequenceEditor.annotation "bpy.types.SpaceSequenceEditor.annotation") |
