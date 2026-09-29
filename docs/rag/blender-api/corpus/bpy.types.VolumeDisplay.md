<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeDisplay.html -->

<a id="volumedisplay-bpy-struct"></a>

# VolumeDisplay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.VolumeDisplay"></a>

### class bpy.types.VolumeDisplay(bpy_struct)

Volume object display settings for 3D viewport

<a id="bpy.types.VolumeDisplay.density"></a>

#### bpy.types.VolumeDisplay.density

Thickness of volume display in the viewport (in [1e-05, inf], default 1.0)

**Type:**

float

<a id="bpy.types.VolumeDisplay.interpolation_method"></a>

#### bpy.types.VolumeDisplay.interpolation_method

Interpolation method to use for volumes in solid mode (default `'LINEAR'`)

- `LINEAR`
  Linear – Good smoothness and speed.
- `CUBIC`
  Cubic – Smoothed high quality interpolation, but slower.
- `CLOSEST`
  Closest – No interpolation.

**Type:**

Literal[‘LINEAR’, ‘CUBIC’, ‘CLOSEST’]

<a id="bpy.types.VolumeDisplay.slice_axis"></a>

#### bpy.types.VolumeDisplay.slice_axis

(default `'AUTO'`)

- `AUTO`
  Auto – Adjust slice direction according to the view direction.
- `X`
  X – Slice along the X axis.
- `Y`
  Y – Slice along the Y axis.
- `Z`
  Z – Slice along the Z axis.

**Type:**

Literal[‘AUTO’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.VolumeDisplay.slice_depth"></a>

#### bpy.types.VolumeDisplay.slice_depth

Position of the slice (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.VolumeDisplay.use_slice"></a>

#### bpy.types.VolumeDisplay.use_slice

Perform a single slice of the domain object (default False)

**Type:**

bool

<a id="bpy.types.VolumeDisplay.wireframe_detail"></a>

#### bpy.types.VolumeDisplay.wireframe_detail

Amount of detail for wireframe display (default `'COARSE'`)

- `COARSE`
  Coarse – Display one box or point for each intermediate tree node.
- `FINE`
  Fine – Display box for each leaf node containing 8×8 voxels.

**Type:**

Literal[‘COARSE’, ‘FINE’]

<a id="bpy.types.VolumeDisplay.wireframe_type"></a>

#### bpy.types.VolumeDisplay.wireframe_type

Type of wireframe display (default `'BOXES'`)

- `NONE`
  None – Don’t display volume in wireframe mode.
- `BOUNDS`
  Bounds – Display single bounding box for the entire grid.
- `BOXES`
  Boxes – Display bounding boxes for nodes in the volume tree.
- `POINTS`
  Points – Display points for nodes in the volume tree.

**Type:**

Literal[‘NONE’, ‘BOUNDS’, ‘BOXES’, ‘POINTS’]

<a id="bpy.types.VolumeDisplay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeDisplay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeDisplay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeDisplay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Volume.display`](bpy.types.Volume.md#bpy.types.Volume.display "bpy.types.Volume.display") |  |
