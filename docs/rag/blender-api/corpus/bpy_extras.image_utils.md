<!-- source: Blender Python API reference 5.2 / bpy_extras.image_utils.html -->

<a id="module-bpy_extras.image_utils"></a>

# bpy_extras submodule (bpy_extras.image_utils)

<a id="bpy_extras.image_utils.load_image"></a>

### bpy_extras.image_utils.load_image(imagepath, dirname='', place_holder=False, recursive=False, ncase_cmp=True, convert_callback=None, verbose=False, relpath=None, check_existing=False, force_reload=False)

Return an image from the file path with options to search multiple paths
and return a placeholder if it’s not found.

**Parameters:**

- **imagepath** (str) – The image filename
  If a path precedes it, this will be searched as well.
- **dirname** (str) – is the directory where the image may be located - any file at
  the end will be ignored.
- **place_holder** (bool) – if True a new place holder image will be created.
  this is useful so later you can relink the image to its original data.
- **recursive** (bool) – If True, directories will be recursively searched.
  Be careful with this if you have files in your root directory because
  it may take a long time.
- **ncase_cmp** (bool) – on non windows systems, find the correct case for the file.
- **convert_callback** (Callable[[str], str] | None) – a function that takes an existing path and returns
  a new one. Use this when loading image formats blender may not support,
  the CONVERT_CALLBACK can take the path for a GIF (for example),
  convert it to a PNG and return the PNG’s path.
  For formats blender can read, simply return the path that is given.
- **verbose** (bool) – If True, print extra information when searching for the image.
- **relpath** (str | None) – If not None, make the file relative to this path.
- **check_existing** (bool) – If true,
  returns already loaded image data-block if possible
  (based on file path).
- **force_reload** (bool) – If true,
  force reloading of image (only useful when `check_existing`
  is also enabled).

**Returns:**

an image or None

**Return type:**

[`bpy.types.Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None
