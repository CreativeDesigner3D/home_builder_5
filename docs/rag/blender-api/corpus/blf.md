<!-- source: Blender Python API reference 5.2 / blf.html -->

<a id="module-blf"></a>

# Font Drawing (blf)

This module provides access to Blender’s text drawing functions.

Submodules

- [Font Drawing Types (blf.types)](blf.types.md)

<a id="hello-world-text-example"></a>

## Hello World Text Example

Example of using the blf module. For this module to work we
need to use the GPU module [`gpu`](gpu.md#module-gpu "gpu") as well.

```python
# Import stand alone modules.
import blf
import bpy

font_info = {
    "font_id": 0,
    "handler": None,
}

def init():
    """init function - runs once"""
    import os
    # Create a new font object, use external TTF file.
    font_path = bpy.path.abspath('//Zeyada.ttf')
    # Store the font index - to use later.
    if os.path.exists(font_path):
        font_info["font_id"] = blf.load(font_path)
    else:
        # Default font.
        font_info["font_id"] = 0

    # Set the font drawing routine to run every frame.
    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(
        draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')

def draw_callback_px(self, context):
    """Draw on the viewports"""
    # BLF drawing routine.
    font_id = font_info["font_id"]
    blf.position(font_id, 2, 80, 0)
    blf.size(font_id, 50.0)
    blf.draw(font_id, "Hello World")

if __name__ == '__main__':
    init()
```

<a id="drawing-text-to-an-image"></a>

## Drawing Text to an Image

Example showing how text can be drawn into an image.
This can be done by binding an image buffer ([`imbuf`](imbuf.md#module-imbuf "imbuf")) to the font’s ID.

```python
import blf
import imbuf

image_size = 512, 512
font_size = 20

ibuf = imbuf.new(image_size)

font_id = blf.load("/path/to/font.ttf")

blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
blf.size(font_id, font_size)
blf.position(font_id, 0, image_size[1] - font_size, 0)

blf.enable(font_id, blf.WORD_WRAP)
blf.word_wrap(font_id, image_size[0])

with blf.bind_imbuf(font_id, ibuf, display_name="sRGB"):
    blf.draw_buffer(font_id, "Lots of wrapped text. " * 50)

imbuf.write(ibuf, filepath="/path/to/image.png")
```

<a id="blf.aspect"></a>

### blf.aspect(fontid, aspect)

Set the aspect for drawing text.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **aspect** (float) – The aspect ratio for non-uniform scaling of text.

<a id="blf.bind_imbuf"></a>

### blf.bind_imbuf(fontid, imbuf, *, display_name=None)

Context manager to draw text into an image buffer instead of the GPU’s context.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **imbuf** ([`imbuf.types.ImBuf`](imbuf.types.md#imbuf.types.ImBuf "imbuf.types.ImBuf")) – The image to draw into.
- **display_name** (str | None) – Ignored (formerly a color-space transform name), kept for backwards compatibility.

**Returns:**

The BLF ImBuf context manager.

**Return type:**

[`blf.types.BLFImBufContext`](blf.types.md#blf.types.BLFImBufContext "blf.types.BLFImBufContext")

<a id="blf.clipping"></a>

### blf.clipping(fontid, xmin, ymin, xmax, ymax)

Set the clipping, enable/disable using [`CLIPPING`](#blf.CLIPPING "blf.CLIPPING").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **xmin** (float) – Left edge of the clipping rectangle.
- **ymin** (float) – Bottom edge of the clipping rectangle.
- **xmax** (float) – Right edge of the clipping rectangle.
- **ymax** (float) – Top edge of the clipping rectangle.

<a id="blf.color"></a>

### blf.color(fontid, r, g, b, a)

Set the color for drawing text.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **r** (float) – Red channel 0.0 - 1.0.
- **g** (float) – Green channel 0.0 - 1.0.
- **b** (float) – Blue channel 0.0 - 1.0.
- **a** (float) – Alpha channel 0.0 - 1.0.

<a id="blf.dimensions"></a>

### blf.dimensions(fontid, text)

Return the width and height of the text.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **text** (str) – The text to measure.

**Returns:**

The width and height of the text.

**Return type:**

tuple[float, float]

<a id="blf.disable"></a>

### blf.disable(fontid, option)

Disable a font drawing option.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **option** (int) – One of [`ROTATION`](#blf.ROTATION "blf.ROTATION"), [`CLIPPING`](#blf.CLIPPING "blf.CLIPPING"), [`SHADOW`](#blf.SHADOW "blf.SHADOW"), [`MONOCHROME`](#blf.MONOCHROME "blf.MONOCHROME") or [`WORD_WRAP`](#blf.WORD_WRAP "blf.WORD_WRAP").

<a id="blf.draw"></a>

### blf.draw(fontid, text)

Draw text in the current context.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **text** (str) – The text to draw.

<a id="blf.draw_buffer"></a>

### blf.draw_buffer(fontid, text)

Draw text into the image buffer bound via [`blf.bind_imbuf()`](#blf.bind_imbuf "blf.bind_imbuf").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **text** (str) – The text to draw into the bound image buffer.

<a id="blf.enable"></a>

### blf.enable(fontid, option)

Enable a font drawing option.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **option** (int) – One of [`ROTATION`](#blf.ROTATION "blf.ROTATION"), [`CLIPPING`](#blf.CLIPPING "blf.CLIPPING"), [`SHADOW`](#blf.SHADOW "blf.SHADOW"), [`MONOCHROME`](#blf.MONOCHROME "blf.MONOCHROME") or [`WORD_WRAP`](#blf.WORD_WRAP "blf.WORD_WRAP").

<a id="blf.load"></a>

### blf.load(filepath)

Load a new font.

**Parameters:**

**filepath** (str | bytes) – The filepath of the font.

**Returns:**

The new font’s fontid or -1 if there was an error.

**Return type:**

int

<a id="blf.position"></a>

### blf.position(fontid, x, y, z)

Set the position for drawing text.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **x** (float) – X axis position to draw the text.
- **y** (float) – Y axis position to draw the text.
- **z** (float) – Z axis position to draw the text (typically 0).

<a id="blf.rotation"></a>

### blf.rotation(fontid, angle)

Set the text rotation angle, enable/disable using [`ROTATION`](#blf.ROTATION "blf.ROTATION").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **angle** (float) – The angle for text drawing to use (in radians).

<a id="blf.shadow"></a>

### blf.shadow(fontid, level, r, g, b, a)

Shadow options, enable/disable using [`SHADOW`](#blf.SHADOW "blf.SHADOW").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **level** (int) – The shadow type: 0 for none, 3 for 3x3 blur, 5 for 5x5 blur or 6 for outline. Other values raise a `TypeError`.
- **r** (float) – Shadow color (red channel 0.0 - 1.0).
- **g** (float) – Shadow color (green channel 0.0 - 1.0).
- **b** (float) – Shadow color (blue channel 0.0 - 1.0).
- **a** (float) – Shadow color (alpha channel 0.0 - 1.0).

<a id="blf.shadow_offset"></a>

### blf.shadow_offset(fontid, x, y)

Set the offset for shadow text, enable/disable using [`SHADOW`](#blf.SHADOW "blf.SHADOW").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **x** (int) – Horizontal shadow offset value in pixels.
- **y** (int) – Vertical shadow offset value in pixels.

<a id="blf.size"></a>

### blf.size(fontid, size)

Set the size for drawing text.

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **size** (float) – Point size of the font.

<a id="blf.unload"></a>

### blf.unload(filepath)

Unload an existing font.

**Parameters:**

**filepath** (str | bytes) – The filepath of the font.

<a id="blf.word_wrap"></a>

### blf.word_wrap(fontid, wrap_width)

Set the wrap width, enable/disable using [`WORD_WRAP`](#blf.WORD_WRAP "blf.WORD_WRAP").

**Parameters:**

- **fontid** (int) – The id of the typeface as returned by [`blf.load()`](#blf.load "blf.load"), for default font use 0.
- **wrap_width** (int) – The width (in pixels) to wrap words at.

<a id="blf.CLIPPING"></a>

### blf.CLIPPING

Constant value 2

**Type:**

int

<a id="blf.MONOCHROME"></a>

### blf.MONOCHROME

Constant value 128

**Type:**

int

<a id="blf.NO_FALLBACK"></a>

### blf.NO_FALLBACK

Constant value 524288

**Type:**

int

<a id="blf.ROTATION"></a>

### blf.ROTATION

Constant value 1

**Type:**

int

<a id="blf.SHADOW"></a>

### blf.SHADOW

Constant value 4

**Type:**

int

<a id="blf.WORD_WRAP"></a>

### blf.WORD_WRAP

Constant value 64

**Type:**

int
