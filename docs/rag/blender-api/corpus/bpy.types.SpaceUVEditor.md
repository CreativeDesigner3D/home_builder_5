<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceUVEditor.html -->

<a id="spaceuveditor-bpy-struct"></a>

# SpaceUVEditor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SpaceUVEditor"></a>

### class bpy.types.SpaceUVEditor(bpy_struct)

UV editor data for the image editor space

<a id="bpy.types.SpaceUVEditor.custom_grid_subdivisions"></a>

#### bpy.types.SpaceUVEditor.custom_grid_subdivisions

Number of grid units in UV space that make one UV Unit (array of 2 items, in [1, 5000], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.SpaceUVEditor.display_stretch_type"></a>

#### bpy.types.SpaceUVEditor.display_stretch_type

Type of stretch to display (default `'ANGLE'`)

- `ANGLE`
  Angle – Angular distortion between UV and 3D angles.
- `AREA`
  Area – Area distortion between UV and 3D faces.

**Type:**

Literal[‘ANGLE’, ‘AREA’]

<a id="bpy.types.SpaceUVEditor.edge_display_type"></a>

#### bpy.types.SpaceUVEditor.edge_display_type

Display style for UV edges (default `'OUTLINE'`)

- `OUTLINE`
  Outline – Display white edges with black outline.
- `DASH`
  Dash – Display dashed black-white edges.
- `BLACK`
  Black – Display black edges.
- `WHITE`
  White – Display white edges.

**Type:**

Literal[‘OUTLINE’, ‘DASH’, ‘BLACK’, ‘WHITE’]

<a id="bpy.types.SpaceUVEditor.grid_shape_source"></a>

#### bpy.types.SpaceUVEditor.grid_shape_source

Specify source for the grid shape (default `'DYNAMIC'`)

- `DYNAMIC`
  Dynamic – Dynamic grid.
- `FIXED`
  Fixed – Manually set grid divisions.
- `PIXEL`
  Pixel – Grid aligns with pixels from image.

**Type:**

Literal[‘DYNAMIC’, ‘FIXED’, ‘PIXEL’]

<a id="bpy.types.SpaceUVEditor.lock_bounds"></a>

#### bpy.types.SpaceUVEditor.lock_bounds

Constraint to stay within the image bounds while editing (default False)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.pixel_round_mode"></a>

#### bpy.types.SpaceUVEditor.pixel_round_mode

Round UVs to pixels while editing (default `'DISABLED'`)

- `DISABLED`
  Disabled – Don’t round to pixels.
- `CORNER`
  Corner – Round to pixel corners.
- `CENTER`
  Center – Round to pixel centers.

**Type:**

Literal[‘DISABLED’, ‘CORNER’, ‘CENTER’]

<a id="bpy.types.SpaceUVEditor.show_faces"></a>

#### bpy.types.SpaceUVEditor.show_faces

Display faces over the image (default True)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_grid_over_image"></a>

#### bpy.types.SpaceUVEditor.show_grid_over_image

Show the grid over the image (default True)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_metadata"></a>

#### bpy.types.SpaceUVEditor.show_metadata

Display metadata properties of the image (default False)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_modified_edges"></a>

#### bpy.types.SpaceUVEditor.show_modified_edges

Display edges after modifiers are applied (default False)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_pixel_coords"></a>

#### bpy.types.SpaceUVEditor.show_pixel_coords

Display UV coordinates in pixels rather than from 0.0 to 1.0 (default True)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_stretch"></a>

#### bpy.types.SpaceUVEditor.show_stretch

Display faces colored according to the difference in shape between UVs and their 3D coordinates (blue for low distortion, red for high distortion) (default False)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.show_uv"></a>

#### bpy.types.SpaceUVEditor.show_uv

Display overlay of UV layer (default True)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.stretch_opacity"></a>

#### bpy.types.SpaceUVEditor.stretch_opacity

Opacity of the UV Stretch overlay (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceUVEditor.tile_grid_shape"></a>

#### bpy.types.SpaceUVEditor.tile_grid_shape

How many tiles will be shown in the background (array of 2 items, in [1, 100], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.SpaceUVEditor.use_live_unwrap"></a>

#### bpy.types.SpaceUVEditor.use_live_unwrap

Continuously unwrap the selected UV island while transforming pinned vertices (default False)

**Type:**

bool

<a id="bpy.types.SpaceUVEditor.uv_edge_opacity"></a>

#### bpy.types.SpaceUVEditor.uv_edge_opacity

Opacity of edges in UV overlays (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceUVEditor.uv_face_opacity"></a>

#### bpy.types.SpaceUVEditor.uv_face_opacity

Opacity of faces in UV overlays (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceUVEditor.uv_opacity"></a>

#### bpy.types.SpaceUVEditor.uv_opacity

Opacity of UV overlays (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceUVEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceUVEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceUVEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceUVEditor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceImageEditor.uv_editor`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.uv_editor "bpy.types.SpaceImageEditor.uv_editor") |  |
