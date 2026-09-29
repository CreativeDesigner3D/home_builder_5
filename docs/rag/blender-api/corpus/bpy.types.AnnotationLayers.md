<!-- source: Blender Python API reference 5.2 / bpy.types.AnnotationLayers.html -->

<a id="annotationlayers-bpy-prop-collection"></a>

# AnnotationLayers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.AnnotationLayers"></a>

### class bpy.types.AnnotationLayers(bpy_prop_collection)

Collection of annotation layers

<a id="bpy.types.AnnotationLayers.active_index"></a>

#### bpy.types.AnnotationLayers.active_index

Index of active annotation layer (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.AnnotationLayers.active_note"></a>

#### bpy.types.AnnotationLayers.active_note

Note/Layer to add annotation strokes to (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.AnnotationLayers.new"></a>

#### bpy.types.AnnotationLayers.new(name, *, set_active=True)

Add a new annotation layer

**Parameters:**

- **name** (str) – Name, Name of the layer (never None)
- **set_active** (bool) – Set Active, Set the newly created layer to the active layer (optional)

**Returns:**

The newly created layer

**Return type:**

[`AnnotationLayer`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer "bpy.types.AnnotationLayer")

<a id="bpy.types.AnnotationLayers.remove"></a>

#### bpy.types.AnnotationLayers.remove(layer)

Remove a annotation layer

**Parameters:**

**layer** ([`AnnotationLayer`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer "bpy.types.AnnotationLayer") | None) – The layer to remove (never None)

<a id="bpy.types.AnnotationLayers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnnotationLayers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnnotationLayers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnnotationLayers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Annotation.layers`](bpy.types.Annotation.md#bpy.types.Annotation.layers "bpy.types.Annotation.layers") |  |
