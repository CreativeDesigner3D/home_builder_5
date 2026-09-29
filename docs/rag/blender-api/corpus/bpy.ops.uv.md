<!-- source: Blender Python API reference 5.2 / bpy.ops.uv.html -->

<a id="module-bpy.ops.uv"></a>

# Uv Operators

<a id="bpy.ops.uv.align"></a>

### bpy.ops.uv.align(*, axis='ALIGN_AUTO', position_mode='MEAN')

Aligns selected UV vertices on a line

**Parameters:**

- **axis** (Literal['ALIGN_S', 'ALIGN_T', 'ALIGN_U', 'ALIGN_AUTO', 'ALIGN_X', 'ALIGN_Y']) –

  Axis, Axis to align UV locations on (optional)

  - `ALIGN_S`
    Straighten – Align UV vertices along the line defined by the endpoints.
  - `ALIGN_T`
    Straighten X – Align UV vertices, moving them horizontally to the line defined by the endpoints.
  - `ALIGN_U`
    Straighten Y – Align UV vertices, moving them vertically to the line defined by the endpoints.
  - `ALIGN_AUTO`
    Align Auto – Automatically choose the direction on which there is most alignment already.
  - `ALIGN_X`
    Align Vertically – Align UV vertices on a vertical line.
  - `ALIGN_Y`
    Align Horizontally – Align UV vertices on a horizontal line.
- **position_mode** (Literal['MEAN', 'MIN', 'MAX']) –

  Position Mode, Method of calculating the alignment position (optional)

  - `MEAN`
    Mean – Align UVs along the mean position.
  - `MIN`
    Minimum – Align UVs along the minimum position.
  - `MAX`
    Maximum – Align UVs along the maximum position.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.align_rotation"></a>

### bpy.ops.uv.align_rotation(*, method='AUTO', axis='X', correct_aspect=False)

Align the UV island’s rotation

**Parameters:**

- **method** (Literal['AUTO', 'EDGE', 'GEOMETRY']) –

  Method, Method to calculate rotation angle (optional)

  - `AUTO`
    Auto – Align from all edges.
  - `EDGE`
    Edge – Only selected edges.
  - `GEOMETRY`
    Geometry – Align to Geometry axis.
- **axis** (Literal['X', 'Y', 'Z']) –

  Axis, Axis to align to (optional)

  - `X`
    X – X axis.
  - `Y`
    Y – Y axis.
  - `Z`
    Z – Z axis.
- **correct_aspect** (bool) – Correct Aspect, Take image aspect ratio into account (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/uvcalc_transform.py:360](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/uvcalc_transform.py#L360)

<a id="bpy.ops.uv.arrange_islands"></a>

### bpy.ops.uv.arrange_islands(*, initial_position='BOUNDING_BOX', axis='Y', align='MIN', order='LARGE_TO_SMALL', margin=0.05)

Arrange selected UV islands on a line

**Parameters:**

- **initial_position** (Literal['BOUNDING_BOX', 'UV_GRID', 'ACTIVE_UDIM', 'CURSOR']) –

  Initial Position, Initial position to arrange islands from (optional)

  - `BOUNDING_BOX`
    Bounding Box – Initial alignment based on the islands bounding box.
  - `UV_GRID`
    UV Grid – Initial alignment based on UV Tile Grid.
  - `ACTIVE_UDIM`
    Active UDIM – Initial alignment based on Active UDIM.
  - `CURSOR`
    2D Cursor – Initial alignment based on 2D cursor.
- **axis** (Literal['X', 'Y']) –

  Axis, Axis to arrange UV islands on (optional)

  - `X`
    X – Align UV islands along the X axis.
  - `Y`
    Y – Align UV islands along the Y axis.
- **align** (Literal['MIN', 'MAX', 'CENTER', 'NONE']) –

  Align, Location to align islands on (optional)

  - `MIN`
    Min – Align the islands to the min of the island.
  - `MAX`
    Max – Align the islands to the max side of the island.
  - `CENTER`
    Center – Align the islands to the center of the largest island.
  - `NONE`
    None – Preserve island alignment.
- **order** (Literal['LARGE_TO_SMALL', 'SMALL_TO_LARGE', 'Fixed']) –

  Order, Order of islands (optional)

  - `LARGE_TO_SMALL`
    Largest to Smallest – Sort islands from largest to smallest.
  - `SMALL_TO_LARGE`
    Smallest to Largest – Sort islands from smallest to largest.
  - `Fixed`
    Fixed – Preserve island order.
- **margin** (float) – Margin, Space between islands (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.average_islands_scale"></a>

### bpy.ops.uv.average_islands_scale(*, scale_uv=False, shear=False)

Average the size of separate UV islands, based on their area in 3D space

**Parameters:**

- **scale_uv** (bool) – Non-Uniform, Scale U and V independently (optional)
- **shear** (bool) – Shear, Reduce shear within islands (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.copy"></a>

### bpy.ops.uv.copy()

Copy selected UV vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.copy_mirrored_faces"></a>

### bpy.ops.uv.copy_mirrored_faces(*, mesh_axis='POS_X', uv_axis='X', precision=3)

Copy mirror UV coordinates based on a mirrored mesh

**Parameters:**

- **mesh_axis** (Literal[[Object Axis Flip Items](bpy_types_enum_items/object_axis_flip_items.md#rna-enum-object-axis-flip-items)]) – Mesh Axis, Mirror vertices based on mesh axis (optional)
- **uv_axis** (Literal[[Axis Xy Items](bpy_types_enum_items/axis_xy_items.md#rna-enum-axis-xy-items)]) – UV Axis, Axis to mirror UV coordinates (optional)
- **precision** (int) – Precision, Tolerance for finding vertex duplicates (in [1, 16], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.cube_project"></a>

### bpy.ops.uv.cube_project(*, cube_size=1.0, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)

Project the UV vertices of the mesh over the six faces of a cube

**Parameters:**

- **cube_size** (float) – Cube Size, Size of the cube to project on (in [0, inf], optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **clip_to_bounds** (bool) – Clip to Bounds, Clip UV coordinates to bounds after unwrapping (optional)
- **scale_to_bounds** (bool) – Scale to Bounds, Scale UV coordinates to bounds after unwrapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.cursor_set"></a>

### bpy.ops.uv.cursor_set(*, location=(0.0, 0.0))

Set 2D cursor location

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in normalized (0.0 to 1.0) coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.custom_region_set"></a>

### bpy.ops.uv.custom_region_set(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the boundaries of the user region

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.cylinder_project"></a>

### bpy.ops.uv.cylinder_project(*, direction='VIEW_ON_EQUATOR', align='POLAR_ZX', pole='PINCH', seam=False, radius=1.0, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)

Project the UV vertices of the mesh over the curved wall of a cylinder

**Parameters:**

- **direction** (Literal['VIEW_ON_EQUATOR', 'VIEW_ON_POLES', 'ALIGN_TO_OBJECT']) –

  Direction, Direction of the sphere or cylinder (optional)

  - `VIEW_ON_EQUATOR`
    View on Equator – 3D view is on the equator.
  - `VIEW_ON_POLES`
    View on Poles – 3D view is on the poles.
  - `ALIGN_TO_OBJECT`
    Align to Object – Align according to object transform.
- **align** (Literal['POLAR_ZX', 'POLAR_ZY']) –

  Align, How to determine rotation around the pole (optional)

  - `POLAR_ZX`
    Polar ZX – Polar 0 is X.
  - `POLAR_ZY`
    Polar ZY – Polar 0 is Y.
- **pole** (Literal['PINCH', 'FAN']) –

  Pole, How to handle faces at the poles (optional)

  - `PINCH`
    Pinch – UVs are pinched at the poles.
  - `FAN`
    Fan – UVs are fanned at the poles.
- **seam** (bool) – Preserve Seams, Separate projections by islands isolated by seams (optional)
- **radius** (float) – Radius, Radius of the sphere or cylinder (in [0, inf], optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **clip_to_bounds** (bool) – Clip to Bounds, Clip UV coordinates to bounds after unwrapping (optional)
- **scale_to_bounds** (bool) – Scale to Bounds, Scale UV coordinates to bounds after unwrapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.export_layout"></a>

### bpy.ops.uv.export_layout(*, filepath='', export_all=False, export_tiles='NONE', modified=False, mode='PNG', size=(1024, 1024), opacity=0.25, check_existing=True)

Export UV layout to file

**Parameters:**

- **filepath** (str) – filepath, (optional, never None)
- **export_all** (bool) – All UVs, Export all UVs in this mesh (not just visible ones) (optional)
- **export_tiles** (Literal['NONE', 'UDIM', 'UV']) –

  Export Tiles, Choose whether to export only the [0, 1] range, or all UV tiles (optional)

  - `NONE`
    None – Export only UVs in the [0, 1] range.
  - `UDIM`
    UDIM – Export tiles in the UDIM numbering scheme: 1001 + u_tile + 10*v_tile.
  - `UV`
    UVTILE – Export tiles in the UVTILE numbering scheme: u(u_tile + 1)_v(v_tile + 1).
- **modified** (bool) – Modified, Exports UVs from the modified mesh (optional)
- **mode** (Literal['SVG', 'EPS', 'PNG']) –

  Format, File format to export the UV layout to (optional)

  - `SVG`
    Scalable Vector Graphic (.svg) – Export the UV layout to a vector SVG file.
  - `EPS`
    Encapsulated PostScript (.eps) – Export the UV layout to a vector EPS file.
  - `PNG`
    PNG Image (.png) – Export the UV layout to a bitmap image.
- **size** (Sequence[int]) – Size, Dimensions of the exported file (array of 2 items, in [8, 32768], optional)
- **opacity** (float) – Fill Opacity, Set amount of opacity for exported UV layout (in [0, 1], optional)
- **check_existing** (bool) – check_existing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_mesh_uv_layout/__init__.py:139](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_mesh_uv_layout/__init__.py#L139)

<a id="bpy.ops.uv.follow_active_quads"></a>

### bpy.ops.uv.follow_active_quads(*, mode='LENGTH_AVERAGE')

Follow UVs from active quads along continuous face loops

**Parameters:**

**mode** (Literal['EVEN', 'LENGTH', 'LENGTH_AVERAGE']) –

Edge Length Mode, Method to space UV edge loops (optional)

- `EVEN`
  Even – Space all UVs evenly.
- `LENGTH`
  Length – Average space UVs edge length of each loop.
- `LENGTH_AVERAGE`
  Length Average – Average space UVs edge length of each loop.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/uvcalc_follow_active.py:302](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/uvcalc_follow_active.py#L302)

<a id="bpy.ops.uv.hide"></a>

### bpy.ops.uv.hide(*, unselected=False)

Hide (un)selected UV vertices

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.lightmap_pack"></a>

### bpy.ops.uv.lightmap_pack(*, PREF_CONTEXT='SEL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_BOX_DIV=12, PREF_MARGIN_DIV=0.1)

Pack each face’s UVs into the UV bounds

**Parameters:**

- **PREF_CONTEXT** (Literal['SEL_FACES', 'ALL_FACES']) –

  Selection, (optional)

  - `SEL_FACES`
    Selected Faces – Pack only selected faces.
  - `ALL_FACES`
    All Faces – Pack all faces in the mesh.
- **PREF_PACK_IN_ONE** (bool) – Share Texture Space, Objects share texture space, map all objects into a single UV map (optional)
- **PREF_NEW_UVLAYER** (bool) – New UV Map, Create a new UV map for every mesh packed (optional)
- **PREF_BOX_DIV** (int) – Pack Quality, Quality of the packing. Higher values will be slower but waste less space (in [1, 48], optional)
- **PREF_MARGIN_DIV** (float) – Margin, Size of the margin as a division of the UV (in [0.001, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/uvcalc_lightmap.py:664](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/uvcalc_lightmap.py#L664)

<a id="bpy.ops.uv.mark_seam"></a>

### bpy.ops.uv.mark_seam(*, clear=False)

Mark selected UV edges as seams

**Parameters:**

**clear** (bool) – Clear Seams, Clear instead of marking seams (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.minimize_stretch"></a>

### bpy.ops.uv.minimize_stretch(*, fill_holes=True, blend=0.0, iterations=0)

Reduce UV stretching by relaxing angles

**Parameters:**

- **fill_holes** (bool) – Fill Holes, Virtually fill holes in mesh before unwrapping, to better avoid overlaps and preserve symmetry (optional)
- **blend** (float) – Blend, Blend factor between stretch minimized and original (in [0, 1], optional)
- **iterations** (int) – Iterations, Number of iterations to run, 0 is unlimited when run interactively (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.move_on_axis"></a>

### bpy.ops.uv.move_on_axis(*, type='UDIM', axis='X', distance=1)

Move UVs on an axis

**Parameters:**

- **type** (Literal['DYNAMIC', 'PIXEL', 'UDIM']) –

  Type, Move Type (optional)

  - `DYNAMIC`
    Dynamic – Move by dynamic grid.
  - `PIXEL`
    Pixel – Move by pixel.
  - `UDIM`
    UDIM – Move by UDIM.
- **axis** (Literal['X', 'Y']) –

  Axis, Axis to move UVs on (optional)

  - `X`
    X axis – Move vertices on the X axis.
  - `Y`
    Y axis – Move vertices on the Y axis.
- **distance** (int) – Distance, Distance to move UVs (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.pack_islands"></a>

### bpy.ops.uv.pack_islands(*, udim_source='CLOSEST_UDIM', rotate=True, rotate_method='ANY', scale=True, merge_overlap=False, margin_method='SCALED', margin=0.001, pin=False, pin_method='LOCKED', shape_method='CONCAVE')

Transform all islands so that they fill up the UV/UDIM space as much as possible

**Parameters:**

- **udim_source** (Literal['CLOSEST_UDIM', 'ACTIVE_UDIM', 'ORIGINAL_AABB', 'CUSTOM_REGION']) –

  Pack to, (optional)

  - `CLOSEST_UDIM`
    Closest UDIM – Pack islands to closest UDIM.
  - `ACTIVE_UDIM`
    Active UDIM – Pack islands to active UDIM image tile or UDIM grid tile where 2D cursor is located.
  - `ORIGINAL_AABB`
    Original bounding box – Pack to starting bounding box of islands.
  - `CUSTOM_REGION`
    Custom Region – Pack islands to custom region.
- **rotate** (bool) – Rotate, Rotate islands to improve layout (optional)
- **rotate_method** (Literal['ANY', 'CARDINAL', 'AXIS_ALIGNED', 'AXIS_ALIGNED_X', 'AXIS_ALIGNED_Y']) –

  Rotation Method, (optional)

  - `ANY`
    Any – Any angle is allowed for rotation.
  - `CARDINAL`
    Cardinal – Only 90 degree rotations are allowed.
  - `AXIS_ALIGNED`
    Axis-aligned – Rotated to a minimal rectangle, either vertical or horizontal.
  - `AXIS_ALIGNED_X`
    Axis-aligned (Horizontal) – Rotate islands to be aligned horizontally.
  - `AXIS_ALIGNED_Y`
    Axis-aligned (Vertical) – Rotate islands to be aligned vertically.
- **scale** (bool) – Scale, Scale islands to fill unit square (optional)
- **merge_overlap** (bool) – Merge Overlapping, Overlapping islands stick together (optional)
- **margin_method** (Literal['SCALED', 'ADD', 'FRACTION']) –

  Margin Method, (optional)

  - `SCALED`
    Scaled – Use scale of existing UVs to multiply margin.
  - `ADD`
    Add – Just add the margin, ignoring any UV scale.
  - `FRACTION`
    Fraction – Specify a precise fraction of final UV output.
- **margin** (float) – Margin, Space between islands (in [0, 1], optional)
- **pin** (bool) – Lock Pinned Islands, Constrain islands containing any pinned UV’s (optional)
- **pin_method** (Literal['SCALE', 'ROTATION', 'ROTATION_SCALE', 'LOCKED']) –

  Pin Method, (optional)

  - `SCALE`
    Scale – Pinned islands won’t rescale.
  - `ROTATION`
    Rotation – Pinned islands won’t rotate.
  - `ROTATION_SCALE`
    Rotation and Scale – Pinned islands will translate only.
  - `LOCKED`
    All – Pinned islands are locked in place.
- **shape_method** (Literal['CONCAVE', 'CONVEX', 'AABB']) –

  Shape Method, (optional)

  - `CONCAVE`
    Exact Shape (Concave) – Uses exact geometry.
  - `CONVEX`
    Boundary Shape (Convex) – Uses convex hull.
  - `AABB`
    Bounding Box – Uses bounding boxes.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.paste"></a>

### bpy.ops.uv.paste()

Paste selected UV vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.pin"></a>

### bpy.ops.uv.pin(*, clear=False, invert=False)

Set/clear selected UV vertices as anchored between multiple unwrap operations

**Parameters:**

- **clear** (bool) – Clear, Clear pinning for the selection instead of setting it (optional)
- **invert** (bool) – Invert, Invert pinning for the selection instead of setting it (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.project_from_view"></a>

### bpy.ops.uv.project_from_view(*, orthographic=False, camera_bounds=True, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)

Project the UV vertices of the mesh as seen in current 3D view

**Parameters:**

- **orthographic** (bool) – Orthographic, Use orthographic projection (optional)
- **camera_bounds** (bool) – Camera Bounds, Map UVs to the camera region taking resolution and aspect into account (optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **clip_to_bounds** (bool) – Clip to Bounds, Clip UV coordinates to bounds after unwrapping (optional)
- **scale_to_bounds** (bool) – Scale to Bounds, Scale UV coordinates to bounds after unwrapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.randomize_uv_transform"></a>

### bpy.ops.uv.randomize_uv_transform(*, random_seed=0, use_loc=True, loc=(0.0, 0.0), use_rot=True, rot=0.0, use_scale=True, scale_even=False, scale=(1.0, 1.0))

Randomize the UV island’s location, rotation, and scale

**Parameters:**

- **random_seed** (int) – Random Seed, Seed value for the random generator (in [0, 10000], optional)
- **use_loc** (bool) – Randomize Location, Randomize the location values (optional)
- **loc** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Maximum distance the objects can spread over each axis (array of 2 items, in [-100, 100], optional)
- **use_rot** (bool) – Randomize Rotation, Randomize the rotation value (optional)
- **rot** (float) – Rotation, Maximum rotation (in [-6.28319, 6.28319], optional)
- **use_scale** (bool) – Randomize Scale, Randomize the scale values (optional)
- **scale_even** (bool) – Scale Even, Use the same scale value for both axes (optional)
- **scale** (Sequence[float]) – Scale, Maximum scale randomization over each axis (array of 2 items, in [-100, 100], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/uvcalc_transform.py:536](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/uvcalc_transform.py#L536)

<a id="bpy.ops.uv.remove_doubles"></a>

### bpy.ops.uv.remove_doubles(*, threshold=0.02, use_unselected=False, use_shared_vertex=False)

Selected UV vertices that are within a radius of each other are welded together

**Parameters:**

- **threshold** (float) – Merge Distance, Maximum distance between welded vertices (in [0, 10], optional)
- **use_unselected** (bool) – Unselected, Merge selected to other unselected vertices (optional)
- **use_shared_vertex** (bool) – Shared Vertex, Weld UVs based on shared vertices (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.reset"></a>

### bpy.ops.uv.reset()

Reset UV projection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.reveal"></a>

### bpy.ops.uv.reveal(*, select=True)

Reveal all hidden UV vertices

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.rip"></a>

### bpy.ops.uv.rip(*, mirror=False, release_confirm=False, use_accurate=False, location=(0.0, 0.0))

Rip selected vertices or a selected region

**Parameters:**

- **mirror** (bool) – Mirror Editing, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.rip_move"></a>

### bpy.ops.uv.rip_move(*, UV_OT_rip={}, TRANSFORM_OT_translate={})

Unstitch UVs and move the result

**Parameters:**

- **UV_OT_rip** (dict[str, Any]) – Rip UVs, Rip selected vertices or a selected region (optional, [`bpy.ops.uv.rip()`](#bpy.ops.uv.rip "bpy.ops.uv.rip") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.seams_from_islands"></a>

### bpy.ops.uv.seams_from_islands(*, mark_seams=True, mark_sharp=False)

Set mesh seams according to island setup in the UV editor

**Parameters:**

- **mark_seams** (bool) – Mark Seams, Mark boundary edges as seams (optional)
- **mark_sharp** (bool) – Mark Sharp, Mark boundary edges as sharp (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select"></a>

### bpy.ops.uv.select(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, location=(0.0, 0.0))

Select UV vertices

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_all"></a>

### bpy.ops.uv.select_all(*, action='TOGGLE')

Change selection of all UV vertices

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_box"></a>

### bpy.ops.uv.select_box(*, pinned=False, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Select UV vertices using box selection

**Parameters:**

- **pinned** (bool) – Pinned, Border select pinned UVs only (optional)
- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_by_winding"></a>

### bpy.ops.uv.select_by_winding(*, winding='NEGATIVE', extend=False)

Select UV faces by their winding

**Parameters:**

- **winding** (Literal['POSITIVE', 'NEGATIVE']) – Winding, Select faces with positive or negative winding (optional)
- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_circle"></a>

### bpy.ops.uv.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Select UV vertices using circle selection

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)
- **radius** (int) – Radius, (in [1, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_edge_ring"></a>

### bpy.ops.uv.select_edge_ring(*, extend=False, location=(0.0, 0.0))

Select an edge ring of connected UV vertices

**Parameters:**

- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_lasso"></a>

### bpy.ops.uv.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select UVs using lasso selection

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_less"></a>

### bpy.ops.uv.select_less()

Deselect UV vertices at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_linked"></a>

### bpy.ops.uv.select_linked(*, delimit=set())

Select all UV vertices linked to the active UV map

**Parameters:**

**delimit** (set[Literal['SEAM', 'SHARP', 'MATERIAL']]) –

Delimit, Delimit selection when selecting linked UVs (optional)

- `SEAM`
  Seam – Delimit by edge seams.
- `SHARP`
  Sharp – Delimit by sharp edges.
- `MATERIAL`
  Material – Delimit by face material.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_linked_pick"></a>

### bpy.ops.uv.select_linked_pick(*, extend=False, deselect=False, delimit=set(), location=(0.0, 0.0))

Select all UV vertices linked under the mouse

**Parameters:**

- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)
- **deselect** (bool) – Deselect, Deselect linked UV vertices rather than selecting them (optional)
- **delimit** (set[Literal['SEAM', 'SHARP', 'MATERIAL']]) –

  Delimit, Delimit selection when selecting linked UVs (optional)

  - `SEAM`
    Seam – Delimit by edge seams.
  - `SHARP`
    Sharp – Delimit by sharp edges.
  - `MATERIAL`
    Material – Delimit by face material.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_loop"></a>

### bpy.ops.uv.select_loop(*, extend=False, location=(0.0, 0.0))

Select a loop of connected UV vertices

**Parameters:**

- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_mode"></a>

### bpy.ops.uv.select_mode(*, type='VERTEX')

Change UV selection mode

**Parameters:**

**type** (Literal[[Mesh Select Mode Uv Items](bpy_types_enum_items/mesh_select_mode_uv_items.md#rna-enum-mesh-select-mode-uv-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_more"></a>

### bpy.ops.uv.select_more()

Select more UV vertices connected to initial selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_overlap"></a>

### bpy.ops.uv.select_overlap(*, extend=False)

Select all UV faces which overlap each other

**Parameters:**

**extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_pinned"></a>

### bpy.ops.uv.select_pinned()

Select all pinned UV vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_similar"></a>

### bpy.ops.uv.select_similar(*, type='PIN', compare='EQUAL', threshold=0.0)

Select similar UVs by property types

**Parameters:**

- **type** (Literal['PIN', 'LENGTH', 'LENGTH_3D', 'AREA', 'AREA_3D', 'MATERIAL', 'OBJECT', 'SIDES', 'WINDING', 'FACE']) –

  Type, (optional)

  - `PIN`
    Pinned.
  - `LENGTH`
    Length – Edge length in UV space.
  - `LENGTH_3D`
    Length 3D – Length of edge in 3D space.
  - `AREA`
    Area – Face area in UV space.
  - `AREA_3D`
    Area 3D – Area of face in 3D space.
  - `MATERIAL`
    Material.
  - `OBJECT`
    Object.
  - `SIDES`
    Polygon Sides.
  - `WINDING`
    Winding – Face direction defined by clockwise or anti-clockwise winding (facing up or facing down).
  - `FACE`
    Amount of Faces in Island.
- **compare** (Literal['EQUAL', 'GREATER', 'LESS']) – Compare, (optional)
- **threshold** (float) – Threshold, (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_split"></a>

### bpy.ops.uv.select_split()

Select only entirely selected faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.select_tile"></a>

### bpy.ops.uv.select_tile(*, extend=False, tile=(0, 0))

Select UVs in specified tile

**Parameters:**

- **extend** (bool) – Extend, Extend the selection (optional)
- **tile** (Sequence[int]) – Tile, Tile location to select UVs (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.shortest_path_pick"></a>

### bpy.ops.uv.shortest_path_pick(*, use_face_step=False, use_topology_distance=False, use_fill=False, skip=0, nth=1, offset=0, object_index=-1, index=-1)

Select shortest path between two selections

**Parameters:**

- **use_face_step** (bool) – Face Stepping, Traverse connected faces (includes diagonals and edge-rings) (optional)
- **use_topology_distance** (bool) – Topology Distance, Find the minimum number of steps, ignoring spatial distance (optional)
- **use_fill** (bool) – Fill Region, Select all paths between the source/destination elements (optional)
- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [0, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)
- **object_index** (int) – (in [-1, inf], optional)
- **index** (int) – (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.shortest_path_select"></a>

### bpy.ops.uv.shortest_path_select(*, use_face_step=False, use_topology_distance=False, use_fill=False, skip=0, nth=1, offset=0)

Select shortest path between two vertices/edges/faces

**Parameters:**

- **use_face_step** (bool) – Face Stepping, Traverse connected faces (includes diagonals and edge-rings) (optional)
- **use_topology_distance** (bool) – Topology Distance, Find the minimum number of steps, ignoring spatial distance (optional)
- **use_fill** (bool) – Fill Region, Select all paths between the source/destination elements (optional)
- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [0, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.smart_project"></a>

### bpy.ops.uv.smart_project(*, angle_limit=1.15192, margin_method='SCALED', rotate_method='AXIS_ALIGNED_Y', island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)

Projection unwraps the selected faces of mesh objects

**Parameters:**

- **angle_limit** (float) – Angle Limit, Lower for more projection groups, higher for less distortion (in [0, 1.5708], optional)
- **margin_method** (Literal['SCALED', 'ADD', 'FRACTION']) –

  Margin Method, (optional)

  - `SCALED`
    Scaled – Use scale of existing UVs to multiply margin.
  - `ADD`
    Add – Just add the margin, ignoring any UV scale.
  - `FRACTION`
    Fraction – Specify a precise fraction of final UV output.
- **rotate_method** (Literal['AXIS_ALIGNED', 'AXIS_ALIGNED_X', 'AXIS_ALIGNED_Y']) –

  Rotation Method, (optional)

  - `AXIS_ALIGNED`
    Axis-aligned – Rotated to a minimal rectangle, either vertical or horizontal.
  - `AXIS_ALIGNED_X`
    Axis-aligned (Horizontal) – Rotate islands to be aligned horizontally.
  - `AXIS_ALIGNED_Y`
    Axis-aligned (Vertical) – Rotate islands to be aligned vertically.
- **island_margin** (float) – Island Margin, Margin to reduce bleed from adjacent islands (in [0, 1], optional)
- **area_weight** (float) – Area Weight, Weight projection’s vector by faces with larger areas (in [0, 1], optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **scale_to_bounds** (bool) – Scale to Bounds, Scale UV coordinates to bounds after unwrapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.snap_cursor"></a>

### bpy.ops.uv.snap_cursor(*, target='PIXELS')

Snap cursor to target type

**Parameters:**

**target** (Literal['PIXELS', 'SELECTED', 'ORIGIN']) – Target, Target to snap the selected UVs to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.snap_selected"></a>

### bpy.ops.uv.snap_selected(*, target='PIXELS')

Snap selected UV vertices to target type

**Parameters:**

**target** (Literal['PIXELS', 'CURSOR', 'CURSOR_OFFSET', 'ADJACENT_UNSELECTED']) – Target, Target to snap the selected UVs to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.sphere_project"></a>

### bpy.ops.uv.sphere_project(*, direction='VIEW_ON_EQUATOR', align='POLAR_ZX', pole='PINCH', seam=False, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)

Project the UV vertices of the mesh over the curved surface of a sphere

**Parameters:**

- **direction** (Literal['VIEW_ON_EQUATOR', 'VIEW_ON_POLES', 'ALIGN_TO_OBJECT']) –

  Direction, Direction of the sphere or cylinder (optional)

  - `VIEW_ON_EQUATOR`
    View on Equator – 3D view is on the equator.
  - `VIEW_ON_POLES`
    View on Poles – 3D view is on the poles.
  - `ALIGN_TO_OBJECT`
    Align to Object – Align according to object transform.
- **align** (Literal['POLAR_ZX', 'POLAR_ZY']) –

  Align, How to determine rotation around the pole (optional)

  - `POLAR_ZX`
    Polar ZX – Polar 0 is X.
  - `POLAR_ZY`
    Polar ZY – Polar 0 is Y.
- **pole** (Literal['PINCH', 'FAN']) –

  Pole, How to handle faces at the poles (optional)

  - `PINCH`
    Pinch – UVs are pinched at the poles.
  - `FAN`
    Fan – UVs are fanned at the poles.
- **seam** (bool) – Preserve Seams, Separate projections by islands isolated by seams (optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **clip_to_bounds** (bool) – Clip to Bounds, Clip UV coordinates to bounds after unwrapping (optional)
- **scale_to_bounds** (bool) – Scale to Bounds, Scale UV coordinates to bounds after unwrapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.stitch"></a>

### bpy.ops.uv.stitch(*, use_limit=False, snap_islands=True, limit=0.01, static_island=0, active_object_index=0, midpoint_snap=False, clear_seams=True, mode='VERTEX', stored_mode='VERTEX', selection=None, objects_selection_count=(0, 0, 0, 0, 0, 0))

Stitch selected UV vertices by proximity

**Parameters:**

- **use_limit** (bool) – Use Limit, Stitch UVs within a specified limit distance (optional)
- **snap_islands** (bool) – Snap Islands, Snap islands together (on edge stitch mode, rotates the islands too) (optional)
- **limit** (float) – Limit, Limit distance in normalized coordinates (in [0, inf], optional)
- **static_island** (int) – Static Island, Island that stays in place when stitching islands (in [0, inf], optional)
- **active_object_index** (int) – Active Object, Index of the active object (in [0, inf], optional)
- **midpoint_snap** (bool) – Snap at Midpoint, UVs are stitched at midpoint instead of at static island (optional)
- **clear_seams** (bool) – Clear Seams, Clear seams of stitched edges (optional)
- **mode** (Literal['VERTEX', 'EDGE']) – Operation Mode, Use vertex or edge stitching (optional)
- **stored_mode** (Literal['VERTEX', 'EDGE']) – Stored Operation Mode, Use vertex or edge stitching (optional)
- **selection** (`bpy_prop_collection`[`SelectedUvElement`] | None) – Selection, (optional)
- **objects_selection_count** (Sequence[int]) – Objects Selection Count, (array of 6 items, in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.unwrap"></a>

### bpy.ops.uv.unwrap(*, method='CONFORMAL', fill_holes=False, correct_aspect=True, use_subsurf_data=False, use_original_bounds=False, margin_method='SCALED', margin=0.001, no_flip=False, iterations=10, use_weights=False, weight_group='uv_importance', weight_factor=1.0)

Unwrap the mesh of the object being edited

**Parameters:**

- **method** (Literal['ANGLE_BASED', 'CONFORMAL', 'MINIMUM_STRETCH']) – Method, Unwrapping method (Angle Based usually gives better results than Conformal, while being somewhat slower) (optional)
- **fill_holes** (bool) – Fill Holes, Virtually fill holes in mesh before unwrapping, to better avoid overlaps and preserve symmetry (optional)
- **correct_aspect** (bool) – Correct Aspect, Map UVs taking aspect ratio of the image associated with the material into account (optional)
- **use_subsurf_data** (bool) – Use Subdivision Surface, Map UVs taking vertex position after Subdivision Surface modifier has been applied (optional)
- **use_original_bounds** (bool) – Original Bounds, Unwrap islands into their original bounds, instead of re-packing (optional)
- **margin_method** (Literal['SCALED', 'ADD', 'FRACTION']) –

  Margin Method, (optional)

  - `SCALED`
    Scaled – Use scale of existing UVs to multiply margin.
  - `ADD`
    Add – Just add the margin, ignoring any UV scale.
  - `FRACTION`
    Fraction – Specify a precise fraction of final UV output.
- **margin** (float) – Margin, Space between islands (in [0, 1], optional)
- **no_flip** (bool) – No Flip, Prevent flipping UV’s, flipping may lower distortion depending on the position of pins (optional)
- **iterations** (int) – Iterations, Number of iterations when “Minimum Stretch” method is used (in [0, 10000], optional)
- **use_weights** (bool) – Importance Weights, Whether to take into account per-vertex importance weights (optional)
- **weight_group** (str) – Weight Group, Vertex group name for importance weights (modulating the deform) (optional, never None)
- **weight_factor** (float) – Weight Factor, How much influence the weightmap has for weighted parameterization, 0 being no influence (in [-10000, 10000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.uv.weld"></a>

### bpy.ops.uv.weld()

Weld selected UV vertices together

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
