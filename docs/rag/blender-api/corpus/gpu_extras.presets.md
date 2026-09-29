<!-- source: Blender Python API reference 5.2 / gpu_extras.presets.html -->

<a id="module-gpu_extras.presets"></a>

# gpu_extras submodule (gpu_extras.presets)

<a id="gpu_extras.presets.draw_circle_2d"></a>

### gpu_extras.presets.draw_circle_2d(position, color, radius, *, segments=None)

Draw a circle.

**Parameters:**

- **position** (Sequence[float]) – 2D position where the circle will be drawn.
- **color** (Sequence[float]) – Color of the circle (RGBA).
  To use transparency blend must be set to `ALPHA`, see: [`gpu.state.blend_set()`](gpu.state.md#gpu.state.blend_set "gpu.state.blend_set").
- **radius** (float) – Radius of the circle.
- **segments** (int | None) – How many segments will be used to draw the circle.
  Higher values give better results but the drawing will take longer.
  If None or not specified, an automatic value will be calculated.

<a id="gpu_extras.presets.draw_texture_2d"></a>

### gpu_extras.presets.draw_texture_2d(texture, position, width, height, is_scene_linear_with_rec709_srgb_target=False)

Draw a 2d texture.

**Parameters:**

- **texture** ([`gpu.types.GPUTexture`](gpu.types.md#gpu.types.GPUTexture "gpu.types.GPUTexture")) – GPUTexture to draw (e.g. gpu.texture.from_image(image) for [`bpy.types.Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")).
- **position** (Sequence[float]) – 2D position of the lower left corner.
- **width** (float) – Width of the image when drawn (not necessarily
  the original width of the texture).
- **height** (float) – Height of the image when drawn.
- **is_scene_linear_with_rec709_srgb_target** (bool) – True if the texture is stored in scene linear color space and
  the destination frame-buffer uses the Rec.709 sRGB color space
  (which is true when drawing textures acquired from [`bpy.types.Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") inside a
  ‘PRE_VIEW’, ‘POST_VIEW’ or ‘POST_PIXEL’ draw handler).
  Otherwise the color space is assumed to match the one of the frame-buffer. (default=False)
