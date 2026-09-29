<!-- source: Blender Python API reference 5.2 / bpy.types.Paint.html -->

<a id="paint-bpy-struct"></a>

# Paint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [CurvesSculpt(Paint)](bpy.types.CurvesSculpt.md)
- [GpPaint(Paint)](bpy.types.GpPaint.md)
- [GpSculptPaint(Paint)](bpy.types.GpSculptPaint.md)
- [GpVertexPaint(Paint)](bpy.types.GpVertexPaint.md)
- [GpWeightPaint(Paint)](bpy.types.GpWeightPaint.md)
- [ImagePaint(Paint)](bpy.types.ImagePaint.md)
- [Sculpt(Paint)](bpy.types.Sculpt.md)
- [VertexPaint(Paint)](bpy.types.VertexPaint.md)

<a id="bpy.types.Paint"></a>

### class bpy.types.Paint(bpy_struct)

<a id="bpy.types.Paint.brush"></a>

#### bpy.types.Paint.brush

Active brush (readonly)

**Type:**

[`Brush`](bpy.types.Brush.md#bpy.types.Brush "bpy.types.Brush") | None

<a id="bpy.types.Paint.brush_asset_reference"></a>

#### bpy.types.Paint.brush_asset_reference

A weak reference to the matching brush asset, used e.g. to restore the last used brush on file load (readonly)

**Type:**

[`AssetWeakReference`](bpy.types.AssetWeakReference.md#bpy.types.AssetWeakReference "bpy.types.AssetWeakReference") | None

<a id="bpy.types.Paint.cavity_curve"></a>

#### bpy.types.Paint.cavity_curve

Editable cavity curve (readonly, never None)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping")

<a id="bpy.types.Paint.mesh_automasking_settings"></a>

#### bpy.types.Paint.mesh_automasking_settings

(readonly, never None)

**Type:**

[`MeshAutomaskingSettings`](bpy.types.MeshAutomaskingSettings.md#bpy.types.MeshAutomaskingSettings "bpy.types.MeshAutomaskingSettings")

<a id="bpy.types.Paint.palette"></a>

#### bpy.types.Paint.palette

Active Palette

**Type:**

[`Palette`](bpy.types.Palette.md#bpy.types.Palette "bpy.types.Palette") | None

<a id="bpy.types.Paint.show_brush"></a>

#### bpy.types.Paint.show_brush

(default True)

**Type:**

bool

<a id="bpy.types.Paint.show_brush_on_surface"></a>

#### bpy.types.Paint.show_brush_on_surface

(default False)

**Type:**

bool

<a id="bpy.types.Paint.show_bvh_nodes"></a>

#### bpy.types.Paint.show_bvh_nodes

Show the underlying BVH nodes as differently colored faces (default False)

**Type:**

bool

<a id="bpy.types.Paint.show_jitter_curve"></a>

#### bpy.types.Paint.show_jitter_curve

(default False)

**Type:**

bool

<a id="bpy.types.Paint.show_low_resolution"></a>

#### bpy.types.Paint.show_low_resolution

For multires, show low resolution while navigating the view (default False)

**Type:**

bool

<a id="bpy.types.Paint.show_size_curve"></a>

#### bpy.types.Paint.show_size_curve

(default False)

**Type:**

bool

<a id="bpy.types.Paint.show_strength_curve"></a>

#### bpy.types.Paint.show_strength_curve

(default False)

**Type:**

bool

<a id="bpy.types.Paint.tile_offset"></a>

#### bpy.types.Paint.tile_offset

Stride at which tiled strokes are copied (array of 3 items, in [0.01, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Paint.tile_x"></a>

#### bpy.types.Paint.tile_x

Tile along X axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.tile_y"></a>

#### bpy.types.Paint.tile_y

Tile along Y axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.tile_z"></a>

#### bpy.types.Paint.tile_z

Tile along Z axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.unified_paint_settings"></a>

#### bpy.types.Paint.unified_paint_settings

(readonly, never None)

**Type:**

[`UnifiedPaintSettings`](bpy.types.UnifiedPaintSettings.md#bpy.types.UnifiedPaintSettings "bpy.types.UnifiedPaintSettings")

<a id="bpy.types.Paint.use_cavity"></a>

#### bpy.types.Paint.use_cavity

Mask painting according to mesh geometry cavity (default False)

**Type:**

bool

<a id="bpy.types.Paint.use_sculpt_delay_updates"></a>

#### bpy.types.Paint.use_sculpt_delay_updates

Update the geometry when it enters the view, providing faster view navigation (default False)

**Type:**

bool

<a id="bpy.types.Paint.use_symmetry_feather"></a>

#### bpy.types.Paint.use_symmetry_feather

Reduce the strength of the brush where it overlaps symmetrical daubs (default True)

**Type:**

bool

<a id="bpy.types.Paint.use_symmetry_x"></a>

#### bpy.types.Paint.use_symmetry_x

Mirror brush across the X axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.use_symmetry_y"></a>

#### bpy.types.Paint.use_symmetry_y

Mirror brush across the Y axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.use_symmetry_z"></a>

#### bpy.types.Paint.use_symmetry_z

Mirror brush across the Z axis (default False)

**Type:**

bool

<a id="bpy.types.Paint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Paint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Paint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Paint.bl_rna_get_subclass_py(id, default=None, /)

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
