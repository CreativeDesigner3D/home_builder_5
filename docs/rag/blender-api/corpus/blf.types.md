<!-- source: Blender Python API reference 5.2 / blf.types.html -->

<a id="module-blf.types"></a>

# Font Drawing Types (blf.types)

This module provides access to font drawing types.

<a id="blf.types.BLFImBufContext"></a>

### class blf.types.BLFImBufContext

Context manager returned by [`blf.bind_imbuf()`](blf.md#blf.bind_imbuf "blf.bind_imbuf") that binds an image buffer
as the destination for text drawing.

Special Methods

<a id="blf.types.BLFImBufContext.__enter__"></a>

#### blf.types.BLFImBufContext.__enter__()

**Return type:**

[`BLFImBufContext`](#blf.types.BLFImBufContext "blf.types.BLFImBufContext")

<a id="blf.types.BLFImBufContext.__exit__"></a>

#### blf.types.BLFImBufContext.__exit__(exc_type, exc_value, traceback)

**Parameters:**

- **exc_type** (type | None) – Exception type, or `None`.
- **exc_value** (BaseException | None) – Exception instance, or `None`.
- **traceback** (BaseException | None) – Traceback object, or `None`.

**Return type:**

bool
