<!-- source: Blender Python API reference 5.2 / bpy.types.GPencilSculptSettings.html -->

<a id="gpencilsculptsettings-bpy-struct"></a>

# GPencilSculptSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GPencilSculptSettings"></a>

### class bpy.types.GPencilSculptSettings(bpy_struct)

General properties for Grease Pencil stroke sculpting tools

<a id="bpy.types.GPencilSculptSettings.guide"></a>

#### bpy.types.GPencilSculptSettings.guide

(readonly)

**Type:**

[`GPencilSculptGuide`](bpy.types.GPencilSculptGuide.md#bpy.types.GPencilSculptGuide "bpy.types.GPencilSculptGuide") | None

<a id="bpy.types.GPencilSculptSettings.intersection_threshold"></a>

#### bpy.types.GPencilSculptSettings.intersection_threshold

Threshold for stroke intersections (in [0, 10], default 0.1)

**Type:**

float

<a id="bpy.types.GPencilSculptSettings.lock_axis"></a>

#### bpy.types.GPencilSculptSettings.lock_axis

(default `'VIEW'`)

- `VIEW`
  View – Align strokes to current view plane.
- `AXIS_Y`
  Front (X-Z) – Project strokes to plane locked to Y.
- `AXIS_X`
  Side (Y-Z) – Project strokes to plane locked to X.
- `AXIS_Z`
  Top (X-Y) – Project strokes to plane locked to Z.
- `CURSOR`
  Cursor – Align strokes to current 3D cursor orientation.

**Type:**

Literal[‘VIEW’, ‘AXIS_Y’, ‘AXIS_X’, ‘AXIS_Z’, ‘CURSOR’]

<a id="bpy.types.GPencilSculptSettings.multiframe_falloff_curve"></a>

#### bpy.types.GPencilSculptSettings.multiframe_falloff_curve

Custom curve to control falloff of brush effect by Grease Pencil frames (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.GPencilSculptSettings.thickness_primitive_curve"></a>

#### bpy.types.GPencilSculptSettings.thickness_primitive_curve

Custom curve to control primitive thickness (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.GPencilSculptSettings.use_automasking_layer_active"></a>

#### bpy.types.GPencilSculptSettings.use_automasking_layer_active

Affect only the Active Layer (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_automasking_layer_stroke"></a>

#### bpy.types.GPencilSculptSettings.use_automasking_layer_stroke

Affect only strokes below the cursor (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_automasking_material_active"></a>

#### bpy.types.GPencilSculptSettings.use_automasking_material_active

Affect only the Active Material (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_automasking_material_stroke"></a>

#### bpy.types.GPencilSculptSettings.use_automasking_material_stroke

Affect only strokes below the cursor (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_automasking_stroke"></a>

#### bpy.types.GPencilSculptSettings.use_automasking_stroke

Affect only strokes below the cursor (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_multiframe_falloff"></a>

#### bpy.types.GPencilSculptSettings.use_multiframe_falloff

Use falloff effect when edit in multiframe mode to compute brush effect by frame (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_scale_thickness"></a>

#### bpy.types.GPencilSculptSettings.use_scale_thickness

Scale the stroke thickness when transforming strokes (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.use_thickness_curve"></a>

#### bpy.types.GPencilSculptSettings.use_thickness_curve

Use curve to define primitive stroke thickness (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GPencilSculptSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GPencilSculptSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GPencilSculptSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ToolSettings.gpencil_sculpt`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.gpencil_sculpt "bpy.types.ToolSettings.gpencil_sculpt") |  |
