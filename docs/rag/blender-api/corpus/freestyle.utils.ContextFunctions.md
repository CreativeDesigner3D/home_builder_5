<!-- source: Blender Python API reference 5.2 / freestyle.utils.ContextFunctions.html -->

<a id="module-freestyle.utils.ContextFunctions"></a>

# freestyle.utils submodule (freestyle.utils.ContextFunctions)

The Blender Freestyle.ContextFunctions submodule

<a id="freestyle.utils.ContextFunctions.get_border"></a>

### freestyle.utils.ContextFunctions.get_border()

Returns the border.

**Returns:**

A tuple of 4 numbers (xmin, ymin, xmax, ymax).

**Return type:**

tuple[int, int, int, int]

<a id="freestyle.utils.ContextFunctions.get_canvas_height"></a>

### freestyle.utils.ContextFunctions.get_canvas_height()

Returns the canvas height.

**Returns:**

The canvas height.

**Return type:**

int

<a id="freestyle.utils.ContextFunctions.get_canvas_width"></a>

### freestyle.utils.ContextFunctions.get_canvas_width()

Returns the canvas width.

**Returns:**

The canvas width.

**Return type:**

int

<a id="freestyle.utils.ContextFunctions.get_selected_fedge"></a>

### freestyle.utils.ContextFunctions.get_selected_fedge()

Returns the selected FEdge.

**Returns:**

The selected FEdge.

**Return type:**

`FEdge`

<a id="freestyle.utils.ContextFunctions.get_time_stamp"></a>

### freestyle.utils.ContextFunctions.get_time_stamp()

Returns the system time stamp.

**Returns:**

The system time stamp.

**Return type:**

int

<a id="freestyle.utils.ContextFunctions.load_map"></a>

### freestyle.utils.ContextFunctions.load_map(file_name, map_name, num_levels=4, sigma=1.0)

Loads an image map for further reading.

**Parameters:**

- **file_name** (str) – The name of the image file.
- **map_name** (str) – The name that will be used to access this image.
- **num_levels** (int) – The number of levels in the map pyramid
  (default = 4). If num_levels == 0, the complete pyramid is
  built.
- **sigma** (float) – The sigma value of the gaussian function.

<a id="freestyle.utils.ContextFunctions.read_complete_view_map_pixel"></a>

### freestyle.utils.ContextFunctions.read_complete_view_map_pixel(level, x, y)

Reads a pixel in the complete view map.

**Parameters:**

- **level** (int) – The level of the pyramid in which we wish to read the
  pixel.
- **x** (int) – The x coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.
- **y** (int) – The y coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.

**Returns:**

The floating-point value stored for that pixel.

**Return type:**

float

<a id="freestyle.utils.ContextFunctions.read_directional_view_map_pixel"></a>

### freestyle.utils.ContextFunctions.read_directional_view_map_pixel(orientation, level, x, y)

Reads a pixel in one of the oriented view map images.

**Parameters:**

- **orientation** (int) – The number telling which orientation we want to
  check.
- **level** (int) – The level of the pyramid in which we wish to read the
  pixel.
- **x** (int) – The x coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.
- **y** (int) – The y coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.

**Returns:**

The floating-point value stored for that pixel.

**Return type:**

float

<a id="freestyle.utils.ContextFunctions.read_map_pixel"></a>

### freestyle.utils.ContextFunctions.read_map_pixel(map_name, level, x, y)

Reads a pixel in a user-defined map.

**Parameters:**

- **map_name** (str) – The name of the map.
- **level** (int) – The level of the pyramid in which we wish to read the
  pixel.
- **x** (int) – The x coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.
- **y** (int) – The y coordinate of the pixel we wish to read. The origin
  is in the lower-left corner.

**Returns:**

The floating-point value stored for that pixel.

**Return type:**

float
