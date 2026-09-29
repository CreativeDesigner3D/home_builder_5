<!-- source: Blender Python API reference 5.2 / bpy.ops.image.html -->

<a id="module-bpy.ops.image"></a>

# Image Operators

<a id="bpy.ops.image.add_render_slot"></a>

### bpy.ops.image.add_render_slot()

Add a new render slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.change_frame"></a>

### bpy.ops.image.change_frame(*, frame=0)

Interactively change the current frame number

**Parameters:**

**frame** (int) – Frame, (in [-1048574, 1048574], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.clear_render_border"></a>

### bpy.ops.image.clear_render_border()

Clear the boundaries of the render region and disable render region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.clear_render_slot"></a>

### bpy.ops.image.clear_render_slot()

Clear the currently selected render slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.clipboard_copy"></a>

### bpy.ops.image.clipboard_copy()

Copy the image to the clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.clipboard_paste"></a>

### bpy.ops.image.clipboard_paste()

Paste new image from the clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.convert_to_mesh_plane"></a>

### bpy.ops.image.convert_to_mesh_plane(*, interpolation='Linear', extension='CLIP', use_auto_refresh=True, relative=True, shader='PRINCIPLED', emit_strength=1.0, use_transparency=True, render_method='DITHERED', use_backface_culling=False, show_transparent_back=True, overwrite_material=True, name_from='OBJECT', delete_ref=True)

Convert selected reference images to textured mesh plane

**Parameters:**

- **interpolation** (Literal['Linear', 'Closest', 'Cubic', 'Smart']) –

  Interpolation, Texture interpolation (optional)

  - `Linear`
    Linear – Linear interpolation.
  - `Closest`
    Closest – No interpolation (sample closest texel).
  - `Cubic`
    Cubic – Cubic interpolation.
  - `Smart`
    Smart – Bicubic when magnifying, else bilinear (OSL only).
- **extension** (Literal['CLIP', 'EXTEND', 'REPEAT']) –

  Extension, How the image is extrapolated past its original bounds (optional)

  - `CLIP`
    Clip – Clip to image size and set exterior pixels as transparent.
  - `EXTEND`
    Extend – Extend by repeating edge pixels of the image.
  - `REPEAT`
    Repeat – Cause the image to repeat horizontally and vertically.
- **use_auto_refresh** (bool) – Auto Refresh, Always refresh image on frame changes (optional)
- **relative** (bool) – Relative Paths, Use relative file paths (optional)
- **shader** (Literal['PRINCIPLED', 'SHADELESS', 'EMISSION']) –

  Shader, Node shader to use (optional)

  - `PRINCIPLED`
    Principled – Principled shader.
  - `SHADELESS`
    Shadeless – Only visible to camera and reflections.
  - `EMISSION`
    Emission – Emission shader.
- **emit_strength** (float) – Emission Strength, Strength of emission (in [0, inf], optional)
- **use_transparency** (bool) – Use Alpha, Use alpha channel for transparency (optional)
- **render_method** (Literal['DITHERED', 'BLENDED']) –

  Render Method, (optional)

  - `DITHERED`
    Dithered – Allows for grayscale hashed transparency, and compatible with render passes and ray-tracing. Also known as deferred rendering..
  - `BLENDED`
    Blended – Allows for colored transparency, but incompatible with render passes and ray-tracing. Also known as forward rendering..
- **use_backface_culling** (bool) – Backface Culling, Use backface culling to hide the back side of faces (optional)
- **show_transparent_back** (bool) – Show Backface, Render multiple transparent layers (may introduce transparency sorting problems) (optional)
- **overwrite_material** (bool) – Overwrite Material, Overwrite existing material with the same name (optional)
- **name_from** (Literal['OBJECT', 'IMAGE']) –

  Name After, Name for new mesh object and material (optional)

  - `OBJECT`
    Source Object – Name after object source with a suffix.
  - `IMAGE`
    Source Image – Name from loaded image.
- **delete_ref** (bool) – Delete Reference Object, Delete empty image object once mesh plane is created (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image_as_planes.py:1133](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image_as_planes.py#L1133)

<a id="bpy.ops.image.curves_point_set"></a>

### bpy.ops.image.curves_point_set(*, point='BLACK_POINT', size=1)

Set black point or white point for curves

**Parameters:**

- **point** (Literal['BLACK_POINT', 'WHITE_POINT']) – Point, Set black point or white point for curves (optional)
- **size** (int) – Sample Size, (in [1, 128], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.cycle_render_slot"></a>

### bpy.ops.image.cycle_render_slot(*, reverse=False)

Cycle through all non-void render slots

**Parameters:**

**reverse** (bool) – Cycle in Reverse, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.external_edit"></a>

### bpy.ops.image.external_edit(*, filepath='')

Edit image in an external application

**Parameters:**

**filepath** (str) – filepath, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image.py:54](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image.py#L54)

<a id="bpy.ops.image.file_browse"></a>

### bpy.ops.image.file_browse(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Open an image file browser, hold Shift to open the file, Alt to browse containing directory

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.flip"></a>

### bpy.ops.image.flip(*, use_flip_x=False, use_flip_y=False)

Flip the image

**Parameters:**

- **use_flip_x** (bool) – Horizontal, Flip the image horizontally (optional)
- **use_flip_y** (bool) – Vertical, Flip the image vertically (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.import_as_mesh_planes"></a>

### bpy.ops.image.import_as_mesh_planes(*, interpolation='Linear', extension='CLIP', use_auto_refresh=True, relative=True, shader='PRINCIPLED', emit_strength=1.0, use_transparency=True, render_method='DITHERED', use_backface_culling=False, show_transparent_back=True, overwrite_material=True, filepath='', align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), files=None, directory='', filter_image=True, filter_movie=True, filter_folder=True, force_reload=False, image_sequence=False, offset=True, offset_axis='+X', offset_amount=0.1, align_axis='CAM_AX', prev_align_axis='NONE', align_track=False, size_mode='ABSOLUTE', fill_mode='FILL', height=1.0, factor=600.0)

Create mesh plane(s) from image files with the appropriate aspect ratio

**Parameters:**

- **interpolation** (Literal['Linear', 'Closest', 'Cubic', 'Smart']) –

  Interpolation, Texture interpolation (optional)

  - `Linear`
    Linear – Linear interpolation.
  - `Closest`
    Closest – No interpolation (sample closest texel).
  - `Cubic`
    Cubic – Cubic interpolation.
  - `Smart`
    Smart – Bicubic when magnifying, else bilinear (OSL only).
- **extension** (Literal['CLIP', 'EXTEND', 'REPEAT']) –

  Extension, How the image is extrapolated past its original bounds (optional)

  - `CLIP`
    Clip – Clip to image size and set exterior pixels as transparent.
  - `EXTEND`
    Extend – Extend by repeating edge pixels of the image.
  - `REPEAT`
    Repeat – Cause the image to repeat horizontally and vertically.
- **use_auto_refresh** (bool) – Auto Refresh, Always refresh image on frame changes (optional)
- **relative** (bool) – Relative Paths, Use relative file paths (optional)
- **shader** (Literal['PRINCIPLED', 'SHADELESS', 'EMISSION']) –

  Shader, Node shader to use (optional)

  - `PRINCIPLED`
    Principled – Principled shader.
  - `SHADELESS`
    Shadeless – Only visible to camera and reflections.
  - `EMISSION`
    Emission – Emission shader.
- **emit_strength** (float) – Emission Strength, Strength of emission (in [0, inf], optional)
- **use_transparency** (bool) – Use Alpha, Use alpha channel for transparency (optional)
- **render_method** (Literal['DITHERED', 'BLENDED']) –

  Render Method, (optional)

  - `DITHERED`
    Dithered – Allows for grayscale hashed transparency, and compatible with render passes and ray-tracing. Also known as deferred rendering..
  - `BLENDED`
    Blended – Allows for colored transparency, but incompatible with render passes and ray-tracing. Also known as forward rendering..
- **use_backface_culling** (bool) – Backface Culling, Use backface culling to hide the back side of faces (optional)
- **show_transparent_back** (bool) – Show Backface, Render multiple transparent layers (may introduce transparency sorting problems) (optional)
- **overwrite_material** (bool) – Overwrite Material, Overwrite existing material with the same name (optional)
- **filepath** (str) – File Path, Filepath used for importing the file (optional, never None)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, (array of 3 items, in [-inf, inf], optional)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – files, (optional)
- **directory** (str) – directory, (optional, never None)
- **filter_image** (bool) – filter_image, (optional)
- **filter_movie** (bool) – filter_movie, (optional)
- **filter_folder** (bool) – filter_folder, (optional)
- **force_reload** (bool) – Force Reload, Force reload the image if it is already opened elsewhere in Blender (optional)
- **image_sequence** (bool) – Detect Image Sequences, Import sequentially numbered images as an animated image sequence instead of separate planes (optional)
- **offset** (bool) – Offset Planes, Offset planes from each other. If disabled, multiple planes will be created at the same location (optional)
- **offset_axis** (Literal['+X', '+Y', '+Z', '-X', '-Y', '-Z']) –

  Offset Direction, How planes are oriented relative to each others’ local axis (optional)

  - `+X`
    +X – Side by Side to the Left.
  - `+Y`
    +Y – Side by Side, Downward.
  - `+Z`
    +Z – Stacked Above.
  - `-X`
    -X – Side by Side to the Right.
  - `-Y`
    -Y – Side by Side, Upward.
  - `-Z`
    -Z – Stacked Below.
- **offset_amount** (float) – Offset Distance, Set distance between each plane (in [-inf, inf], optional)
- **align_axis** (Literal['+X', '+Y', '+Z', '-X', '-Y', '-Z', 'CAM', 'CAM_AX']) –

  Align, How to align the planes (optional)

  - `+X`
    +X – Facing positive X.
  - `+Y`
    +Y – Facing positive Y.
  - `+Z`
    +Z – Facing positive Z.
  - `-X`
    -X – Facing negative X.
  - `-Y`
    -Y – Facing negative Y.
  - `-Z`
    -Z – Facing negative Z.
  - `CAM`
    Face Camera – Facing camera.
  - `CAM_AX`
    Camera’s Main Axis – Facing the camera’s dominant axis.
- **prev_align_axis** (Literal['+X', '+Y', '+Z', '-X', '-Y', '-Z', 'CAM', 'CAM_AX', 'NONE']) –

  prev_align_axis, (optional)

  - `+X`
    +X – Facing positive X.
  - `+Y`
    +Y – Facing positive Y.
  - `+Z`
    +Z – Facing positive Z.
  - `-X`
    -X – Facing negative X.
  - `-Y`
    -Y – Facing negative Y.
  - `-Z`
    -Z – Facing negative Z.
  - `CAM`
    Face Camera – Facing camera.
  - `CAM_AX`
    Camera’s Main Axis – Facing the camera’s dominant axis.
  - `NONE`
    Undocumented.
- **align_track** (bool) – Track Camera, Add a constraint to make the planes track the camera (optional)
- **size_mode** (Literal['ABSOLUTE', 'CAMERA', 'DPI', 'DPBU']) –

  Size Mode, Method for computing the plane size (optional)

  - `ABSOLUTE`
    Absolute – Use absolute size.
  - `CAMERA`
    Scale to Camera Frame – Scale to fit or fill the camera frame.
  - `DPI`
    Pixels per Inch – Scale based on pixels per inch.
  - `DPBU`
    Pixels per Blender Unit – Scale based on pixels per Blender Unit.
- **fill_mode** (Literal['FILL', 'FIT']) –

  Scale, Method to scale the plane with the camera frame (optional)

  - `FILL`
    Fill – Fill camera frame, spilling outside the frame.
  - `FIT`
    Fit – Fit entire image within the camera frame.
- **height** (float) – Height, Height of the created plane (in [0.001, inf], optional)
- **factor** (float) – Definition, Number of pixels per inch or Blender Unit (in [1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image_as_planes.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image_as_planes.py#L857)

<a id="bpy.ops.image.invert"></a>

### bpy.ops.image.invert(*, invert_r=False, invert_g=False, invert_b=False, invert_a=False)

Invert image’s channels

**Parameters:**

- **invert_r** (bool) – Red, Invert red channel (optional)
- **invert_g** (bool) – Green, Invert green channel (optional)
- **invert_b** (bool) – Blue, Invert blue channel (optional)
- **invert_a** (bool) – Alpha, Invert alpha channel (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.match_movie_length"></a>

### bpy.ops.image.match_movie_length()

Set the image’s frame range to match the video’s duration

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.new"></a>

### bpy.ops.image.new(*, name='Untitled', width=1024, height=1024, color=(0.0, 0.0, 0.0, 1.0), alpha=True, generated_type='BLANK', float=False, use_stereo_3d=False, tiled=False)

Create a new image

**Parameters:**

- **name** (str) – Name, Image data-block name (optional, never None)
- **width** (int) – Width, Image width (in [1, inf], optional)
- **height** (int) – Height, Image height (in [1, inf], optional)
- **color** (Sequence[float]) – Color, Default fill color (array of 4 items, in [0, inf], optional)
- **alpha** (bool) – Alpha, Create an image with an alpha channel (optional)
- **generated_type** (Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]) – Generated Type, Fill the image with a grid for UV map testing (optional)
- **float** (bool) – 32-bit Float, Create image with 32-bit floating-point bit depth (optional)
- **use_stereo_3d** (bool) – Stereo 3D, Create an image with left and right views (optional)
- **tiled** (bool) – Tiled, Create a tiled image (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.open"></a>

### bpy.ops.image.open(*, allow_path_tokens=True, filepath='', directory='', files=None, hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', use_sequence_detection=True, use_udim_detecting=True)

Open image

**Parameters:**

- **allow_path_tokens** (bool) – Allow the path to contain substitution tokens (optional)
- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **use_sequence_detection** (bool) – Detect Sequences, Automatically detect animated sequences in selected images (based on file names) (optional)
- **use_udim_detecting** (bool) – Detect UDIMs, Detect selected UDIM files and load all matching tiles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.open_images"></a>

### bpy.ops.image.open_images(*, directory='', files=None, relative_path=True, use_sequence_detection=True, use_udim_detection=True)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **directory** (str) – directory, (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – files, (optional)
- **relative_path** (bool) – Relative Path, (optional)
- **use_sequence_detection** (bool) – Detect Sequence, (optional)
- **use_udim_detection** (bool) – Detect UDIM, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image.py:238](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image.py#L238)

<a id="bpy.ops.image.pack"></a>

### bpy.ops.image.pack()

Pack an image as embedded data into the .blend file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.project_apply"></a>

### bpy.ops.image.project_apply()

Project edited image back onto the object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image.py:192](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image.py#L192)

<a id="bpy.ops.image.project_edit"></a>

### bpy.ops.image.project_edit()

Edit a snapshot of the 3D Viewport in an external image editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/image.py:122](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/image.py#L122)

<a id="bpy.ops.image.read_viewlayers"></a>

### bpy.ops.image.read_viewlayers()

Read all the current scene’s view layers from cache, as needed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.reload"></a>

### bpy.ops.image.reload()

Reload current image from disk

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.remove_render_slot"></a>

### bpy.ops.image.remove_render_slot()

Remove the current render slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.render_border"></a>

### bpy.ops.image.render_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the boundaries of the render region and enable render region

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

<a id="bpy.ops.image.replace"></a>

### bpy.ops.image.replace(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Replace current image by another one from disk

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.resize"></a>

### bpy.ops.image.resize(*, size=(0, 0), all_udims=False)

Resize the image

**Parameters:**

- **size** (Sequence[int]) – Size, (array of 2 items, in [1, inf], optional)
- **all_udims** (bool) – All UDIM Tiles, Scale all the image’s UDIM tiles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.rotate_orthogonal"></a>

### bpy.ops.image.rotate_orthogonal(*, degrees='90')

Rotate the image

**Parameters:**

**degrees** (Literal['90', '180', '270']) –

Degrees, Amount of rotation in degrees (90, 180, 270) (optional)

- `90`
  90 Degrees – Rotate 90 degrees clockwise.
- `180`
  180 Degrees – Rotate 180 degrees clockwise.
- `270`
  270 Degrees – Rotate 270 degrees clockwise.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.sample"></a>

### bpy.ops.image.sample(*, size=1)

Use mouse to sample a color in current image

**Parameters:**

**size** (int) – Sample Size, (in [1, 128], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.sample_line"></a>

### bpy.ops.image.sample_line(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)

Sample a line and show it in Scope panels

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.save"></a>

### bpy.ops.image.save()

Save the image with current name and settings

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.save_all_modified"></a>

### bpy.ops.image.save_all_modified()

Save all modified images

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.save_as"></a>

### bpy.ops.image.save_as(*, save_as_render=False, copy=False, allow_path_tokens=True, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Save the image with another name and/or settings

**Parameters:**

- **save_as_render** (bool) – Save As Render, Save image with render color management.For display image formats like PNG, apply view and display transform.For intermediate image formats like OpenEXR, use the default render output color space(optional)
- **copy** (bool) – Copy, Create a new image file without modifying the current image in Blender (optional)
- **allow_path_tokens** (bool) – Allow the path to contain substitution tokens (optional)
- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.save_sequence"></a>

### bpy.ops.image.save_sequence()

Save a sequence of images

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.tile_add"></a>

### bpy.ops.image.tile_add(*, number=1002, count=1, label='', fill=True, color=(0.0, 0.0, 0.0, 1.0), generated_type='BLANK', width=1024, height=1024, float=False, alpha=True)

Adds a tile to the image

**Parameters:**

- **number** (int) – Number, UDIM number of the tile (in [1001, 2000], optional)
- **count** (int) – Count, How many tiles to add (in [1, inf], optional)
- **label** (str) – Label, Optional tile label (optional, never None)
- **fill** (bool) – Fill, Fill new tile with a generated image (optional)
- **color** (Sequence[float]) – Color, Default fill color (array of 4 items, in [0, inf], optional)
- **generated_type** (Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]) – Generated Type, Fill the image with a grid for UV map testing (optional)
- **width** (int) – Width, Image width (in [1, inf], optional)
- **height** (int) – Height, Image height (in [1, inf], optional)
- **float** (bool) – 32-bit Float, Create image with 32-bit floating-point bit depth (optional)
- **alpha** (bool) – Alpha, Create an image with an alpha channel (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.tile_fill"></a>

### bpy.ops.image.tile_fill(*, color=(0.0, 0.0, 0.0, 1.0), generated_type='BLANK', width=1024, height=1024, float=False, alpha=True)

Fill the current tile with a generated image

**Parameters:**

- **color** (Sequence[float]) – Color, Default fill color (array of 4 items, in [0, inf], optional)
- **generated_type** (Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]) – Generated Type, Fill the image with a grid for UV map testing (optional)
- **width** (int) – Width, Image width (in [1, inf], optional)
- **height** (int) – Height, Image height (in [1, inf], optional)
- **float** (bool) – 32-bit Float, Create image with 32-bit floating-point bit depth (optional)
- **alpha** (bool) – Alpha, Create an image with an alpha channel (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.tile_remove"></a>

### bpy.ops.image.tile_remove()

Removes a tile from the image

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.unpack"></a>

### bpy.ops.image.unpack(*, method='USE_LOCAL', id='')

Save an image packed in the .blend file to disk

**Parameters:**

- **method** (Literal[[Unpack Method Items](bpy_types_enum_items/unpack_method_items.md#rna-enum-unpack-method-items)]) – Method, How to unpack (optional)
- **id** (str) – Image Name, Image data-block name to unpack (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_all"></a>

### bpy.ops.image.view_all(*, fit_view=False)

View the entire image

**Parameters:**

**fit_view** (bool) – Fit View, Fit frame to the viewport (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_center_cursor"></a>

### bpy.ops.image.view_center_cursor()

Center the view so that the cursor is in the middle of the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_cursor_center"></a>

### bpy.ops.image.view_cursor_center(*, fit_view=False)

Set 2D cursor to center view location

**Parameters:**

**fit_view** (bool) – Fit View, Fit frame to the viewport (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_ndof"></a>

### bpy.ops.image.view_ndof()

Use a 3D mouse device to pan/zoom the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_pan"></a>

### bpy.ops.image.view_pan(*, offset=(0.0, 0.0))

Pan the view

**Parameters:**

**offset** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Offset, Offset in floating-point units, 1.0 is the width and height of the image (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_selected"></a>

### bpy.ops.image.view_selected()

View all selected UVs

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_zoom"></a>

### bpy.ops.image.view_zoom(*, factor=0.0, use_cursor_init=True)

Zoom in/out the image

**Parameters:**

- **factor** (float) – Factor, Zoom factor, values higher than 1.0 zoom in, lower values zoom out (in [-inf, inf], optional)
- **use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_zoom_border"></a>

### bpy.ops.image.view_zoom_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, zoom_out=False)

Zoom in the view to the nearest item contained in the border

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **zoom_out** (bool) – Zoom Out, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_zoom_in"></a>

### bpy.ops.image.view_zoom_in(*, location=(0.0, 0.0))

Zoom in the image (centered around 2D cursor)

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in screen coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_zoom_out"></a>

### bpy.ops.image.view_zoom_out(*, location=(0.0, 0.0))

Zoom out the image (centered around 2D cursor)

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in screen coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.image.view_zoom_ratio"></a>

### bpy.ops.image.view_zoom_ratio(*, ratio=0.0)

Set zoom ratio of the view

**Parameters:**

**ratio** (float) – Ratio, Zoom ratio, 1.0 is 1:1, higher is zoomed in, lower is zoomed out (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
