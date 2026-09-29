<!-- source: Blender Python API reference 5.2 / bpy.types.MaskLayer.html -->

<a id="masklayer-bpy-struct"></a>

# MaskLayer(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaskLayer"></a>

### class bpy.types.MaskLayer(bpy_struct)

Single layer used for masking pixels

<a id="bpy.types.MaskLayer.alpha"></a>

#### bpy.types.MaskLayer.alpha

Render Opacity (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MaskLayer.blend"></a>

#### bpy.types.MaskLayer.blend

Method of blending mask layers (default `'ADD'`)

**Type:**

Literal[‘MERGE_ADD’, ‘MERGE_SUBTRACT’, ‘ADD’, ‘SUBTRACT’, ‘LIGHTEN’, ‘DARKEN’, ‘MUL’, ‘REPLACE’, ‘DIFFERENCE’]

<a id="bpy.types.MaskLayer.falloff"></a>

#### bpy.types.MaskLayer.falloff

Falloff type of the feather (default `'SMOOTH'`)

**Type:**

Literal[[Proportional Falloff Curve Only Items](bpy_types_enum_items/proportional_falloff_curve_only_items.md#rna-enum-proportional-falloff-curve-only-items)]

<a id="bpy.types.MaskLayer.fill_solver"></a>

#### bpy.types.MaskLayer.fill_solver

Triangulation solver for filling 2D curves (default `'CDT'`)

- `SWEEP_LINE`
  Sweep Line – Fast without support for self-intersection.
- `CDT`
  Delaunay – Constrained Delaunay Triangulation (CDT), robust with support for self-intersections.

**Type:**

Literal[‘SWEEP_LINE’, ‘CDT’]

<a id="bpy.types.MaskLayer.hide"></a>

#### bpy.types.MaskLayer.hide

Restrict visibility in the viewport (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.hide_render"></a>

#### bpy.types.MaskLayer.hide_render

Restrict renderability (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.hide_select"></a>

#### bpy.types.MaskLayer.hide_select

Restrict selection in the viewport (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.invert"></a>

#### bpy.types.MaskLayer.invert

Invert the mask black/white (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.name"></a>

#### bpy.types.MaskLayer.name

Unique name of layer (default “”, never None)

**Type:**

str

<a id="bpy.types.MaskLayer.select"></a>

#### bpy.types.MaskLayer.select

Layer is selected for editing in the Dope Sheet (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.splines"></a>

#### bpy.types.MaskLayer.splines

Collection of splines which defines this layer (default None, readonly)

**Type:**

[`MaskSplines`](bpy.types.MaskSplines.md#bpy.types.MaskSplines "bpy.types.MaskSplines")[[`MaskSpline`](bpy.types.MaskSpline.md#bpy.types.MaskSpline "bpy.types.MaskSpline")]

<a id="bpy.types.MaskLayer.use_fill_holes"></a>

#### bpy.types.MaskLayer.use_fill_holes

Calculate holes when filling overlapping curves (default True)

**Type:**

bool

<a id="bpy.types.MaskLayer.use_fill_overlap"></a>

#### bpy.types.MaskLayer.use_fill_overlap

Calculate self intersections and overlap before filling (only for the sweep-line solver) (default False)

**Type:**

bool

<a id="bpy.types.MaskLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskLayer.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mask.layers`](bpy.types.Mask.md#bpy.types.Mask.layers "bpy.types.Mask.layers") - [`MaskLayers.active`](bpy.types.MaskLayers.md#bpy.types.MaskLayers.active "bpy.types.MaskLayers.active") | - [`MaskLayers.new`](bpy.types.MaskLayers.md#bpy.types.MaskLayers.new "bpy.types.MaskLayers.new") - [`MaskLayers.remove`](bpy.types.MaskLayers.md#bpy.types.MaskLayers.remove "bpy.types.MaskLayers.remove") |
