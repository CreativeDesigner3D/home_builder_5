<!-- source: Blender Python API reference 5.2 / bpy.types.AnnotationStroke.html -->

<a id="annotationstroke-bpy-struct"></a>

# AnnotationStroke(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AnnotationStroke"></a>

### class bpy.types.AnnotationStroke(bpy_struct)

Freehand curve defining part of a sketch

<a id="bpy.types.AnnotationStroke.display_mode"></a>

#### bpy.types.AnnotationStroke.display_mode

Coordinate space that stroke is in (default `'3DSPACE'`)

- `3DSPACE`
  3D Space – Stroke is in 3D space.
- `2DSPACE`
  2D Space – Stroke is in 2D space, locked to the camera view.
- `2DIMAGE`
  2D Image – Stroke is in 2D image/UV space.

**Type:**

Literal[‘3DSPACE’, ‘2DSPACE’, ‘2DIMAGE’]

<a id="bpy.types.AnnotationStroke.points"></a>

#### bpy.types.AnnotationStroke.points

Stroke data points (default None, readonly)

**Type:**

[`AnnotationStrokePoints`](bpy.types.AnnotationStrokePoints.md#bpy.types.AnnotationStrokePoints "bpy.types.AnnotationStrokePoints")[[`AnnotationStrokePoint`](bpy.types.AnnotationStrokePoint.md#bpy.types.AnnotationStrokePoint "bpy.types.AnnotationStrokePoint")]

<a id="bpy.types.AnnotationStroke.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnnotationStroke.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnnotationStroke.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnnotationStroke.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`AnnotationFrame.strokes`](bpy.types.AnnotationFrame.md#bpy.types.AnnotationFrame.strokes "bpy.types.AnnotationFrame.strokes") - [`AnnotationStrokes.new`](bpy.types.AnnotationStrokes.md#bpy.types.AnnotationStrokes.new "bpy.types.AnnotationStrokes.new") | - [`AnnotationStrokes.remove`](bpy.types.AnnotationStrokes.md#bpy.types.AnnotationStrokes.remove "bpy.types.AnnotationStrokes.remove") |
