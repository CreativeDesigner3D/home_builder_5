<!-- source: Blender Python API reference 5.2 / bpy.app.icons.html -->

<a id="module-bpy.app.icons"></a>

# Application Icons (bpy.app.icons)

<a id="bpy.app.icons.new_triangles"></a>

### bpy.app.icons.new_triangles(range, coords, colors)

Create a new icon from triangle geometry.

**Parameters:**

- **range** (tuple[int, int]) – Pair of ints.
- **coords** (bytes) – Sequence of bytes (6 floats for one triangle) for (X, Y) coordinates.
- **colors** (bytes) – Sequence of bytes (12 for one triangle) for RGBA.

**Returns:**

Unique icon value (pass to interface `icon_value` argument).

**Return type:**

int

<a id="bpy.app.icons.new_triangles_from_file"></a>

### bpy.app.icons.new_triangles_from_file(filepath)

Create a new icon from triangle geometry.

**Parameters:**

**filepath** (str | bytes) – File path.

**Returns:**

Unique icon value (pass to interface `icon_value` argument).

**Return type:**

int

<a id="bpy.app.icons.release"></a>

### bpy.app.icons.release(icon_id)

Release the icon.

**Parameters:**

**icon_id** (int) – The icon id to release.
