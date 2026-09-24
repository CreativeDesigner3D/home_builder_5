"""
Small pictures of finish colours: the two wood colours the finish
material mixes (style_options.color_rgb), streaked the way the wood's
grain streaks them, or flat where the wood has no grain (paint grade,
MDF). Made from the same numbers the material is, so there are no
pictures to keep up.

Two forms: a preview icon for native menus (icon_id) and a GPU texture
for the Options panel's own buttons (texture).
"""

import math

from . import style_options

SIZE = 32           # pixels a side

_pcoll = None
_textures = {}      # (color, wood) -> GPUTexture


def _srgb(c):
    """Linear (material) value -> display value."""
    c = max(min(c, 1.0), 0.0)
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * c ** (1.0 / 2.4) - 0.055


def _colors(color, wood, custom=None):
    if custom is not None:
        c = tuple(custom[:3])
        return c, c
    c1, c2 = style_options.color_rgb(color)
    return tuple(c1[:3]), tuple(c2[:3])


def swatch_pixels(color, wood, size=SIZE, custom=None):
    """RGBA floats, display-referred, bottom row first: the colour's
    two tones in grain streaks running up the swatch."""
    c1, c2 = _colors(color, wood, custom)
    g = style_options.grain_for_wood(wood)
    grained = custom is None and (g.get('noise_scale_1', 0.0) > 0.0
                                  or g.get('texture_variation_1', 0.0) > 0.0)
    # A little of the wood's own variation into the streak spacing, so
    # oak and maple read differently at a glance.
    streaks = 3.0 + min(g.get('texture_variation_1', 0.0), 12.0) * 0.35
    px = []
    for y in range(size):
        v = y / float(size)
        for x in range(size):
            u = x / float(size)
            if grained:
                wave = (u * streaks
                        + 0.18 * math.sin(v * 5.0 + u * 3.0)
                        + 0.06 * math.sin(v * 17.0 + u * 11.0))
                t = 0.5 + 0.5 * math.sin(wave * 2.0 * math.pi)
                t = t * t
            else:
                t = 0.0
            px.extend((_srgb(c1[0] + (c2[0] - c1[0]) * t),
                       _srgb(c1[1] + (c2[1] - c1[1]) * t),
                       _srgb(c1[2] + (c2[2] - c1[2]) * t), 1.0))
    return px


def has_swatch(color):
    """False for a colour with no colours on file (a custom stain, a
    limited edition): a white swatch would say something untrue."""
    return color in style_options.COLOR_RGB


def icon_id(color, wood):
    """Preview icon of a finish colour on a wood, for icon_value; 0 when
    the colour has no swatch."""
    global _pcoll
    if not has_swatch(color):
        return 0
    if _pcoll is None:
        import bpy.utils.previews
        _pcoll = bpy.utils.previews.new()
    key = "%s|%s" % (color, wood)
    pv = _pcoll.get(key)
    if pv is None:
        pv = _pcoll.new(key)
        pv.icon_size = (SIZE, SIZE)
        pv.icon_pixels_float = swatch_pixels(color, wood)
    return pv.icon_id


def texture(color, wood, custom=None):
    """GPU texture of a finish colour on a wood, for a POST_PIXEL
    draw (display-referred, like the panel's other pictures)."""
    key = (color, wood, tuple(custom[:3]) if custom is not None else None)
    tex = _textures.get(key)
    if tex is None:
        import gpu
        n = 16
        buf = gpu.types.Buffer('FLOAT', n * n * 4,
                               swatch_pixels(color, wood, n, custom))
        tex = gpu.types.GPUTexture((n, n), format='RGBA16F', data=buf)
        if len(_textures) > 200:
            _textures.clear()
        _textures[key] = tex
    return tex


def style_texture(style):
    """The swatch of a cabinet style's finish colour, or None."""
    color = getattr(style, 'finish_color', '')
    if not color or color == 'NONE':
        return None
    custom = None
    if style_options.is_custom_finish(color):
        custom = getattr(style, 'custom_finish_color', None)
    if custom is None and not has_swatch(color):
        return None
    return texture(color, getattr(style, 'finish_wood', ''), custom)


def style_icon(style, color):
    """A menu icon for ``color`` on a cabinet style's wood."""
    return icon_id(color, getattr(style, 'finish_wood', ''))


def unregister():
    global _pcoll
    if _pcoll is not None:
        import bpy.utils.previews
        bpy.utils.previews.remove(_pcoll)
        _pcoll = None
    _textures.clear()
