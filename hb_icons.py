"""Bitmap icons for the GPU-drawn viewport UI, baked from SVG.

The hand-built glyphs in `hb_gpu_ui` are line segments: one pixel wide,
never antialiased, so a diagonal or a curve comes out stepped. These
icons are drawn as vectors in `icons/svg/`, rendered by
`icons/bake_icons.mjs` into white-on-transparent PNGs at a run of pixel
sizes, and drawn here as textured squares tinted to the caller's colour.

Each size is rendered from the vector rather than resampled, and the
one nearest the UI scale is drawn at its own pixel size on whole-pixel
coordinates -- so what lands on screen is exactly what the renderer
antialiased, with no second filtering pass to soften it.

`icon_glyph(name)` returns a callable with the glyph signature
(shader, rect, color), so an icon drops in wherever a glyph is taken.
"""

import os
import struct
import zlib

import bpy
import gpu
from gpu_extras.batch import batch_for_shader


ICON_DIR = os.path.join(os.path.dirname(__file__), "icons", "png")

# The icon's height at 100% UI scale. The SVG sources are drawn on a
# 16-unit grid, so this is the size their pixel lines land true at.
ICON_SIZE = 16

_sizes = {}       # name -> sorted baked sizes on disk
_textures = {}    # (name, size) -> GPUTexture, or None if it failed


def _read_png_alpha(path):
    """Width, height and alpha rows (top row first) of an 8-bit RGBA PNG.

    Only what the bake writes: colour type 6, no interlace. Blender
    could load it through bpy.data.images, but that writes an image
    datablock into the user's file from inside a draw callback; a PNG
    this small decodes in a blink without it.
    """
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat = 8, []
    width = height = 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, depth, ctype, _, _, interlace = struct.unpack(
                ">IIBBBBB", body)
            if depth != 8 or ctype != 6 or interlace:
                raise ValueError("expected 8-bit RGBA, non-interlaced")
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
        pos += 12 + length

    raw = zlib.decompress(b"".join(idat))
    bpp, stride = 4, width * 4
    rows, prev = [], bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        ftype = raw[start]
        cur = bytearray(raw[start + 1:start + 1 + stride])
        if ftype == 1:                                   # Sub
            for i in range(bpp, stride):
                cur[i] = (cur[i] + cur[i - bpp]) & 0xFF
        elif ftype == 2:                                 # Up
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 0xFF
        elif ftype == 3:                                 # Average
            for i in range(stride):
                left = cur[i - bpp] if i >= bpp else 0
                cur[i] = (cur[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:                                 # Paeth
            for i in range(stride):
                a = cur[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[i] = (cur[i] + pred) & 0xFF
        rows.append(cur[3::4])
        prev = cur
    return width, height, rows


def _baked_sizes(name):
    sizes = _sizes.get(name)
    if sizes is None:
        prefix = name + "_"
        sizes = []
        try:
            for f in os.listdir(ICON_DIR):
                if f.startswith(prefix) and f.endswith(".png"):
                    tail = f[len(prefix):-4]
                    if tail.isdigit():
                        sizes.append(int(tail))
        except OSError:
            pass
        sizes.sort()
        _sizes[name] = sizes
    return sizes


def _texture(name, size):
    key = (name, size)
    if key not in _textures:
        tex = None
        try:
            w, h, rows = _read_png_alpha(
                os.path.join(ICON_DIR, "%s_%d.png" % (name, size)))
            # White ink with the PNG's coverage as alpha; the shader's
            # colour does the tinting. Rows go bottom-up for the GPU.
            pixels = []
            for alpha in reversed(rows):
                for a in alpha:
                    pixels.extend((1.0, 1.0, 1.0, a / 255.0))
            buf = gpu.types.Buffer('FLOAT', len(pixels), pixels)
            tex = gpu.types.GPUTexture((w, h), format='RGBA8', data=buf)
            # Drawn 1:1 on whole pixels, so sample texels exactly.
            tex.filter_mode(False)
        except Exception as e:
            print("Home Builder: icon %s_%d failed to load: %s"
                  % (name, size, e))
        _textures[key] = tex
    return _textures[key]


def scale():
    """Blender's UI scale. hb_gpu_ui has the same, but it imports this
    module, so this one cannot import it back."""
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


def has_icon(name):
    return bool(_baked_sizes(name))


# Clearance kept between a fitted icon and the edge of its rect, per side.
FIT_PAD = 3


def draw_icon(name, rect, color, size=None):
    """Draw icon `name` centred in `rect`, tinted `color`.

    `size` is the unscaled height. Left out, the icon fits the rect:
    ICON_SIZE in a full button, smaller in a chip too tight for it. The
    baked size nearest that at the current UI scale is drawn at its
    native pixels. Returns False when the icon is not available, so a
    caller can fall back.
    """
    sizes = _baked_sizes(name)
    if not sizes:
        return False
    s = scale()
    rx, ry, rw, rh = rect
    if size is None:
        want = min(ICON_SIZE * s, min(rw, rh) - FIT_PAD * 2 * s)
    else:
        want = size * s
    px = min(sizes, key=lambda b: (abs(b - want), -b))
    tex = _texture(name, px)
    if tex is None:
        return False
    x0 = round(rx + (rw - px) / 2.0)
    y0 = round(ry + (rh - px) / 2.0)
    x1, y1 = x0 + px, y0 + px
    shader = gpu.shader.from_builtin('IMAGE_COLOR')
    batch = batch_for_shader(shader, 'TRI_FAN', {
        "pos": ((x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)),
        "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
    })
    shader.uniform_sampler("image", tex)
    shader.uniform_float("color", color)
    batch.draw(shader)
    return True


def icon_glyph(name, fallback=None, size=None):
    """A glyph callable that draws icon `name`, or `fallback` (another
    glyph) when the icon's PNGs are missing. `size` as for draw_icon."""
    def glyph(shader, rect, color):
        if not draw_icon(name, rect, color, size) and fallback is not None:
            fallback(shader, rect, color)
    glyph.__name__ = "icon_" + name
    return glyph
