<!-- source: Blender Python API reference 5.2 / gpu.texture.html -->

<a id="module-gpu.texture"></a>

# GPU Texture Utilities (gpu.texture)

This module provides utilities for textures.

<a id="gpu.texture.from_image"></a>

### gpu.texture.from_image(image)

Get GPUTexture corresponding to an Image data-block. The GPUTexture memory is shared with Blender.
Note: Colors read from the texture will be in scene linear color space and have premultiplied or straight alpha matching the image alpha mode.

**Parameters:**

**image** ([`bpy.types.Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")) – The Image data-block.

**Returns:**

The GPUTexture used by the image.

**Return type:**

[`gpu.types.GPUTexture`](gpu.types.md#gpu.types.GPUTexture "gpu.types.GPUTexture")
