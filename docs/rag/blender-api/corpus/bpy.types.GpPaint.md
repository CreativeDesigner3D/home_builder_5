<!-- source: Blender Python API reference 5.2 / bpy.types.GpPaint.html -->

<a id="gppaint-paint"></a>

# GpPaint(Paint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Paint`](bpy.types.Paint.md#bpy.types.Paint "bpy.types.Paint")

<a id="bpy.types.GpPaint"></a>

### class bpy.types.GpPaint(Paint)

<a id="bpy.types.GpPaint.color_mode"></a>

#### bpy.types.GpPaint.color_mode

Paint Mode (default `'MATERIAL'`)

- `MATERIAL`
  Material – Paint using the active material base color.
- `VERTEXCOLOR`
  Color Attribute – Paint the material with a color attribute.

**Type:**

Literal[‘MATERIAL’, ‘VERTEXCOLOR’]

<a id="bpy.types.GpPaint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GpPaint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GpPaint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GpPaint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Paint.brush, Paint.brush_asset_reference, Paint.palette, Paint.show_brush, Paint.show_brush_on_surface, Paint.show_low_resolution, Paint.use_sculpt_delay_updates, Paint.show_bvh_nodes, Paint.use_symmetry_x, Paint.use_symmetry_y, Paint.use_symmetry_z, Paint.use_symmetry_feather, Paint.cavity_curve, Paint.use_cavity, Paint.tile_offset, Paint.tile_x, Paint.tile_y, Paint.tile_z, Paint.show_strength_curve, Paint.show_size_curve, Paint.show_jitter_curve, Paint.unified_paint_settings, Paint.mesh_automasking_settings

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Paint.bl_rna_get_subclass, Paint.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`ToolSettings.gpencil_paint`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.gpencil_paint "bpy.types.ToolSettings.gpencil_paint") |  |
