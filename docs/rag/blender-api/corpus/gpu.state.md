<!-- source: Blender Python API reference 5.2 / gpu.state.html -->

<a id="module-gpu.state"></a>

# GPU State Utilities (gpu.state)

This module provides access to the gpu state.

<a id="gpu.state.active_framebuffer_get"></a>

### gpu.state.active_framebuffer_get()

Return the active frame-buffer in context.

**Returns:**

The active framebuffer.

**Return type:**

[`gpu.types.GPUFrameBuffer`](gpu.types.md#gpu.types.GPUFrameBuffer "gpu.types.GPUFrameBuffer")

<a id="gpu.state.blend_get"></a>

### gpu.state.blend_get()

Current blending equation.

**Returns:**

The current blend mode.

**Return type:**

str

<a id="gpu.state.blend_set"></a>

### gpu.state.blend_set(mode)

Defines the fixed pipeline blending equation.

**Parameters:**

**mode** (Literal['NONE', 'ALPHA', 'ALPHA_PREMULT', 'ADDITIVE', 'ADDITIVE_PREMULT', 'MULTIPLY', 'SUBTRACT', 'INVERT']) –

The type of blend mode.

- `NONE` No blending.
- `ALPHA` The original color channels are interpolated according to the alpha value.
- `ALPHA_PREMULT` The original color channels are interpolated according to the alpha value with the new colors pre-multiplied by this value.
- `ADDITIVE` The original color channels are added by the corresponding ones.
- `ADDITIVE_PREMULT` The original color channels are added by the corresponding ones that are pre-multiplied by the alpha value.
- `MULTIPLY` The original color channels are multiplied by the corresponding ones.
- `SUBTRACT` The original color channels are subtracted by the corresponding ones.
- `INVERT` The original color channels are replaced by its complementary color.

<a id="gpu.state.clip_distances_set"></a>

### gpu.state.clip_distances_set(distances_enabled)

Sets the number of `gl_ClipDistance` planes used for clip geometry.

**Parameters:**

**distances_enabled** (int) – Number of clip distances enabled.

<a id="gpu.state.color_mask_set"></a>

### gpu.state.color_mask_set(r, g, b, a)

Enable or disable writing of frame buffer color components.

**Parameters:**

- **r** (bool) – Red component.
- **g** (bool) – Green component.
- **b** (bool) – Blue component.
- **a** (bool) – Alpha component.

<a id="gpu.state.depth_mask_get"></a>

### gpu.state.depth_mask_get()

Writing status in the depth component.

**Returns:**

True if writing to the depth component is enabled.

**Return type:**

bool

<a id="gpu.state.depth_mask_set"></a>

### gpu.state.depth_mask_set(value)

Write to depth component.

**Parameters:**

**value** (bool) – True for writing to the depth component.

<a id="gpu.state.depth_test_get"></a>

### gpu.state.depth_test_get()

Current depth_test equation.

**Returns:**

The current depth test mode.

**Return type:**

str

<a id="gpu.state.depth_test_set"></a>

### gpu.state.depth_test_set(mode)

Defines the depth_test equation.

**Parameters:**

**mode** (Literal['NONE', 'ALWAYS', 'LESS', 'LESS_EQUAL', 'EQUAL', 'GREATER', 'GREATER_EQUAL']) – The depth test equation name.

<a id="gpu.state.face_culling_set"></a>

### gpu.state.face_culling_set(culling)

Specify whether none, front-facing or back-facing facets can be culled.

**Parameters:**

**culling** (Literal['NONE', 'FRONT', 'BACK']) – The face culling mode.

<a id="gpu.state.front_facing_set"></a>

### gpu.state.front_facing_set(invert)

Specifies the orientation of front-facing polygons.

**Parameters:**

**invert** (bool) – True for clockwise polygons as front-facing.

<a id="gpu.state.line_width_get"></a>

### gpu.state.line_width_get()

Current width of rasterized lines.

**Returns:**

The current line width.

**Return type:**

float

<a id="gpu.state.line_width_set"></a>

### gpu.state.line_width_set(width)

Specify the width of rasterized lines.

**Parameters:**

**width** (float) – New width.

<a id="gpu.state.point_size_set"></a>

### gpu.state.point_size_set(size)

Specify the diameter of rasterized points.

When `program_point_size_set(False)` is set, this sets the `size`
uniform of point shaders. Any value set by `uniform_float("size", ...)`
on a point shader will be overwritten by this function. Use
`program_point_size_set(True)` to disable this override and control
point size via `gl_PointSize` in the vertex shader.

**Parameters:**

**size** (float) – New diameter.

<a id="gpu.state.program_point_size_set"></a>

### gpu.state.program_point_size_set(enable)

When enabled (True), point size is taken from the shader builtin
`gl_PointSize`. When disabled (False), the global state value can
be applied to the shader `size` uniform, overwriting any user-set
value.

**Parameters:**

**enable** (bool) – True to use shader `gl_PointSize`, False for global state.

<a id="gpu.state.scissor_get"></a>

### gpu.state.scissor_get()

Retrieve the scissors of the active framebuffer.
Note: Only valid between ‘scissor_set’ and a framebuffer rebind.

**Returns:**

The scissor of the active framebuffer as a tuple
(x, y, xsize, ysize).
x, y: lower left corner of the scissor rectangle, in pixels.
xsize, ysize: width and height of the scissor rectangle.

**Return type:**

tuple[int, int, int, int]

<a id="gpu.state.scissor_set"></a>

### gpu.state.scissor_set(x, y, xsize, ysize)

Specifies the scissor area of the active framebuffer.
Note: The scissor state is not saved upon framebuffer rebind.

**Parameters:**

- **x** (int) – Lower left corner x coordinate, in pixels.
- **y** (int) – Lower left corner y coordinate, in pixels.
- **xsize** (int) – Width of the scissor rectangle.
- **ysize** (int) – Height of the scissor rectangle.

<a id="gpu.state.scissor_test_set"></a>

### gpu.state.scissor_test_set(enable)

Enable/disable scissor testing on the active framebuffer.

**Parameters:**

**enable** (bool) – True - enable scissor testing.
False - disable scissor testing.

<a id="gpu.state.viewport_get"></a>

### gpu.state.viewport_get()

Viewport of the active framebuffer.

**Returns:**

The viewport as a tuple (x, y, xsize, ysize).

**Return type:**

tuple[int, int, int, int]

<a id="gpu.state.viewport_set"></a>

### gpu.state.viewport_set(x, y, xsize, ysize)

Specifies the viewport of the active framebuffer.
Note: The viewport state is not saved upon framebuffer rebind.

**Parameters:**

- **x** (int) – Lower left corner x coordinate, in pixels.
- **y** (int) – Lower left corner y coordinate, in pixels.
- **xsize** (int) – Width of the viewport.
- **ysize** (int) – Height of the viewport.
