<!-- source: Blender Python API reference 5.2 / imbuf.types.html -->

<a id="module-imbuf.types"></a>

# Image Buffer Types (imbuf.types)

This module provides access to image buffer types.

> **Note:**
>
> Image buffer is also the structure used by [`bpy.types.Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")
> ID type to store and manipulate image data at runtime.

<a id="imbuf.types.ImBuf"></a>

### class imbuf.types.ImBuf

<a id="imbuf.types.ImBuf.convert_buffer_type"></a>

#### imbuf.types.ImBuf.convert_buffer_type(buffer_type)

Convert the image’s pixel buffer to the given type.
When the image is already of the given type this is a no-op.
The previous buffer is freed.

**Parameters:**

**buffer_type** (Literal['BYTE', 'FLOAT']) – The buffer type.

<a id="imbuf.types.ImBuf.copy"></a>

#### imbuf.types.ImBuf.copy()

Return a copy of the image.

**Returns:**

A copy of the image.

**Return type:**

[`ImBuf`](#imbuf.types.ImBuf "imbuf.types.ImBuf")

<a id="imbuf.types.ImBuf.crop"></a>

#### imbuf.types.ImBuf.crop(min, max)

Crop the image in-place.

**Parameters:**

- **min** (tuple[int, int]) – Minimum pixel coordinates (X, Y), inclusive.
- **max** (tuple[int, int]) – Maximum pixel coordinates (X, Y), inclusive.

<a id="imbuf.types.ImBuf.free"></a>

#### imbuf.types.ImBuf.free()

Clear image data immediately (causing an error on re-use).

<a id="imbuf.types.ImBuf.resize"></a>

#### imbuf.types.ImBuf.resize(size, *, method='FAST')

Resize the image in-place.

**Parameters:**

- **size** (tuple[int, int]) – New size.
- **method** (str) – Method of resizing (‘FAST’, ‘BILINEAR’).

<a id="imbuf.types.ImBuf.with_buffer"></a>

#### imbuf.types.ImBuf.with_buffer(*, write=False, region=None)

Return a context manager that yields a `memoryview` of the image’s pixel data, shaped `(height, width, channels)`.

Usage:

```python
with image.with_buffer(write=True) as buf:
    buf[0, 0, 0] = 255  # set red channel of pixel (0, 0)
```

**Parameters:**

- **write** (bool) – When true the buffer is writable.
- **region** (tuple[tuple[int, int], tuple[int, int]] | None) – Optional sub-region `((x_min, y_min), (x_max, y_max))`, clamped to image bounds. When set the shape becomes `(region_height, region_width, channels)`.

**Returns:**

A context manager yielding a `memoryview` of pixel data.

**Return type:**

[`ImBufBuffer`](#imbuf.types.ImBufBuffer "imbuf.types.ImBufBuffer")

<a id="imbuf.types.ImBuf.buffer_type"></a>

#### imbuf.types.ImBuf.buffer_type

Type of the image’s pixel buffer (`'BYTE'` or `'FLOAT'`).

**Type:**

str

<a id="imbuf.types.ImBuf.channels"></a>

#### imbuf.types.ImBuf.channels

Number of color channels.

**Type:**

int

<a id="imbuf.types.ImBuf.compress"></a>

#### imbuf.types.ImBuf.compress

Compression level for formats that support lossless compression levels (0 - 100, clamped).

**Type:**

int

<a id="imbuf.types.ImBuf.file_type"></a>

#### imbuf.types.ImBuf.file_type

The file type identifier.

**Type:**

str

<a id="imbuf.types.ImBuf.filepath"></a>

#### imbuf.types.ImBuf.filepath

Filepath associated with this image.

**Type:**

str | bytes

<a id="imbuf.types.ImBuf.planes"></a>

#### imbuf.types.ImBuf.planes

Number of bits per pixel for the byte buffer.
Used when reading and writing image files.

- 8: Gray-scale.
- 16: Gray-scale with alpha.
- 24: RGB.
- 32: RGBA.

> **Note:**
>
> This value may be set by the file format on load,
> and determines how many channels are written on save.

**Type:**

int

<a id="imbuf.types.ImBuf.ppm"></a>

#### imbuf.types.ImBuf.ppm

Pixels per meter.

**Type:**

tuple[float, float]

<a id="imbuf.types.ImBuf.quality"></a>

#### imbuf.types.ImBuf.quality

Quality for formats that support lossy compression (0 - 100, clamped).

**Type:**

int

<a id="imbuf.types.ImBuf.size"></a>

#### imbuf.types.ImBuf.size

Size of the image in pixels.

**Type:**

tuple[int, int]

Special Methods

<a id="imbuf.types.ImBuf.__hash__"></a>

#### imbuf.types.ImBuf.__hash__()

**Return type:**

int

<a id="imbuf.types.ImBuf.__repr__"></a>

#### imbuf.types.ImBuf.__repr__()

**Return type:**

str

<a id="imbuf.types.ImBufBuffer"></a>

### class imbuf.types.ImBufBuffer

Special Methods

<a id="imbuf.types.ImBufBuffer.__enter__"></a>

#### imbuf.types.ImBufBuffer.__enter__()

**Return type:**

[`ImBufBuffer`](#imbuf.types.ImBufBuffer "imbuf.types.ImBufBuffer")

<a id="imbuf.types.ImBufBuffer.__exit__"></a>

#### imbuf.types.ImBufBuffer.__exit__(exc_type, exc_value, traceback)

**Parameters:**

- **exc_type** (type | None) – Exception type, or `None`.
- **exc_value** (BaseException | None) – Exception instance, or `None`.
- **traceback** (BaseException | None) – Traceback object, or `None`.

**Return type:**

bool

<a id="imbuf.types.ImBufBuffer.__repr__"></a>

#### imbuf.types.ImBufBuffer.__repr__()

**Return type:**

str

<a id="imbuf.types.ImBufFileType"></a>

### class imbuf.types.ImBufFileType

<a id="imbuf.types.ImBufFileType.file_extensions"></a>

#### imbuf.types.ImBufFileType.file_extensions

The file extensions associated with this image file type (e.g. `(".jpg", ".jpeg")`).

**Type:**

tuple[str, …]

<a id="imbuf.types.ImBufFileType.has_read_file"></a>

#### imbuf.types.ImBufFileType.has_read_file

True when images of this file type can be read from a file.

**Type:**

bool

<a id="imbuf.types.ImBufFileType.has_read_memory"></a>

#### imbuf.types.ImBufFileType.has_read_memory

True when images of this file type can be read from memory.

**Type:**

bool

<a id="imbuf.types.ImBufFileType.has_write_file"></a>

#### imbuf.types.ImBufFileType.has_write_file

True when images of this file type can be written to a file.

**Type:**

bool

<a id="imbuf.types.ImBufFileType.has_write_memory"></a>

#### imbuf.types.ImBufFileType.has_write_memory

True when images of this file type can be written to memory.

**Type:**

bool

<a id="imbuf.types.ImBufFileType.id"></a>

#### imbuf.types.ImBufFileType.id

The identifier for this image file type (e.g. `"PNG"`, `"JPEG"`).

**Type:**

str

Special Methods

<a id="imbuf.types.ImBufFileType.__hash__"></a>

#### imbuf.types.ImBufFileType.__hash__()

**Return type:**

int

<a id="imbuf.types.ImBufFileType.__repr__"></a>

#### imbuf.types.ImBufFileType.__repr__()

**Return type:**

str
