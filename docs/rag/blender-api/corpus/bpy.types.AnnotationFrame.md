<!-- source: Blender Python API reference 5.2 / bpy.types.AnnotationFrame.html -->

<a id="annotationframe-bpy-struct"></a>

# AnnotationFrame(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AnnotationFrame"></a>

### class bpy.types.AnnotationFrame(bpy_struct)

Collection of related sketches on a particular frame

<a id="bpy.types.AnnotationFrame.frame_number"></a>

#### bpy.types.AnnotationFrame.frame_number

The frame on which this sketch appears (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.AnnotationFrame.select"></a>

#### bpy.types.AnnotationFrame.select

Frame is selected for editing in the Dope Sheet (default False)

**Type:**

bool

<a id="bpy.types.AnnotationFrame.strokes"></a>

#### bpy.types.AnnotationFrame.strokes

Freehand curves defining the sketch on this frame (default None, readonly)

**Type:**

[`AnnotationStrokes`](bpy.types.AnnotationStrokes.md#bpy.types.AnnotationStrokes "bpy.types.AnnotationStrokes")[[`AnnotationStroke`](bpy.types.AnnotationStroke.md#bpy.types.AnnotationStroke "bpy.types.AnnotationStroke")]

<a id="bpy.types.AnnotationFrame.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnnotationFrame.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnnotationFrame.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnnotationFrame.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`AnnotationFrames.copy`](bpy.types.AnnotationFrames.md#bpy.types.AnnotationFrames.copy "bpy.types.AnnotationFrames.copy") - [`AnnotationFrames.copy`](bpy.types.AnnotationFrames.md#bpy.types.AnnotationFrames.copy "bpy.types.AnnotationFrames.copy") - [`AnnotationFrames.new`](bpy.types.AnnotationFrames.md#bpy.types.AnnotationFrames.new "bpy.types.AnnotationFrames.new") | - [`AnnotationFrames.remove`](bpy.types.AnnotationFrames.md#bpy.types.AnnotationFrames.remove "bpy.types.AnnotationFrames.remove") - [`AnnotationLayer.active_frame`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer.active_frame "bpy.types.AnnotationLayer.active_frame") - [`AnnotationLayer.frames`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer.frames "bpy.types.AnnotationLayer.frames") |
