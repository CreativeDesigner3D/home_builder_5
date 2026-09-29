<!-- source: Blender Python API reference 5.2 / bpy.types.GPencilSculptGuide.html -->

<a id="gpencilsculptguide-bpy-struct"></a>

# GPencilSculptGuide(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GPencilSculptGuide"></a>

### class bpy.types.GPencilSculptGuide(bpy_struct)

Guides for drawing

<a id="bpy.types.GPencilSculptGuide.angle"></a>

#### bpy.types.GPencilSculptGuide.angle

Direction of lines (in [-6.28319, 6.28319], default 0.0)

**Type:**

float

<a id="bpy.types.GPencilSculptGuide.angle_snap"></a>

#### bpy.types.GPencilSculptGuide.angle_snap

Angle snapping (in [-6.28319, 6.28319], default 0.0)

**Type:**

float

<a id="bpy.types.GPencilSculptGuide.location"></a>

#### bpy.types.GPencilSculptGuide.location

Custom reference point for guides (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.GPencilSculptGuide.reference_object"></a>

#### bpy.types.GPencilSculptGuide.reference_object

Object used for reference point

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GPencilSculptGuide.reference_point"></a>

#### bpy.types.GPencilSculptGuide.reference_point

Type of speed guide (default `'CURSOR'`)

- `CURSOR`
  Cursor – Use cursor as reference point.
- `CUSTOM`
  Custom – Use custom reference point.
- `OBJECT`
  Object – Use object as reference point.

**Type:**

Literal[‘CURSOR’, ‘CUSTOM’, ‘OBJECT’]

<a id="bpy.types.GPencilSculptGuide.spacing"></a>

#### bpy.types.GPencilSculptGuide.spacing

Guide spacing (in [0, inf], default 20.0)

**Type:**

float

<a id="bpy.types.GPencilSculptGuide.type"></a>

#### bpy.types.GPencilSculptGuide.type

Type of speed guide (default `'CIRCULAR'`)

- `CIRCULAR`
  Circular – Use single point to create rings.
- `RADIAL`
  Radial – Use single point as direction.
- `PARALLEL`
  Parallel – Parallel lines.
- `GRID`
  Grid – Grid allows horizontal and vertical lines.
- `ISO`
  Isometric – Grid allows isometric and vertical lines.

**Type:**

Literal[‘CIRCULAR’, ‘RADIAL’, ‘PARALLEL’, ‘GRID’, ‘ISO’]

<a id="bpy.types.GPencilSculptGuide.use_guide"></a>

#### bpy.types.GPencilSculptGuide.use_guide

Enable speed guides (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptGuide.use_snapping"></a>

#### bpy.types.GPencilSculptGuide.use_snapping

Enable snapping to guides angle or spacing options (default False)

**Type:**

bool

<a id="bpy.types.GPencilSculptGuide.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GPencilSculptGuide.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GPencilSculptGuide.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GPencilSculptGuide.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.GPencilSculptGuide.type "bpy.types.GPencilSculptGuide.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.GPencilSculptGuide.type "bpy.types.GPencilSculptGuide.type")

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
| - [`GPencilSculptSettings.guide`](bpy.types.GPencilSculptSettings.md#bpy.types.GPencilSculptSettings.guide "bpy.types.GPencilSculptSettings.guide") |  |
