"""Desenho das telas 2D (T018; D-01). Usado dentro de handlers `POST_PIXEL`.

Primitivas em pixels sobre `hb_gpu_draw.py` (retângulo, contorno, linhas, texto) e em coordenadas do mundo 2D por
uma `canvas2d.view.View2D`. Todas as cores são RGBA. A unidade dos rótulos é a do usuário (`data/units.py`).
"""

import math

import blf  # type: ignore
import gpu  # type: ignore

from .. import compat, hb_gpu_draw
from ..data import units

FONT = 0
FONT_SIZE = 12

COLORS = {
    'panel': (0.11, 0.11, 0.12, 0.94),
    'pane': (0.17, 0.17, 0.18, 1.0),
    'border': (1.0, 1.0, 1.0, 0.18),
    'text': (0.92, 0.92, 0.92, 1.0),
    'muted': (0.65, 0.65, 0.68, 1.0),
    'reference': (0.25, 0.65, 1.0, 1.0),      # B
    'moving': (1.0, 0.62, 0.15, 1.0),         # A
    'target': (0.55, 0.55, 0.6, 0.55),
    'target_hot': (0.35, 1.0, 0.45, 1.0),
    'warning': (1.0, 0.35, 0.3, 1.0),
    'button': (0.26, 0.26, 0.28, 1.0),
    'button_hot': (0.36, 0.36, 0.40, 1.0),
    'button_primary': (0.2, 0.45, 0.8, 1.0),
}


def shader():
    sh = compat.get_builtin_shader('UNIFORM_COLOR')
    sh.bind()
    return sh


def begin():
    gpu.state.blend_set('ALPHA')
    return shader()


def end():
    gpu.state.blend_set('NONE')


# Pixels --------------------------------------------------------------------------------------------------------

def rect(sh, r, color):
    hb_gpu_draw.draw_rect(sh, r[0], r[1], r[2], r[3], color)


def outline(sh, r, color):
    hb_gpu_draw.draw_rect_outline(sh, r[0], r[1], r[2], r[3], color)


def lines(sh, points, color):
    if points:
        hb_gpu_draw.draw_lines(sh, points, color)


def dashed(p0, p1, dash=6.0, gap=4.0):
    """Pontos (pares) de uma linha tracejada entre p0 e p1, em pixels."""
    length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if length < 1e-6:
        return []
    ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
    pts, t = [], 0.0
    while t < length:
        e = min(t + dash, length)
        pts += [(p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * e, p0[1] + uy * e)]
        t = e + gap
    return pts


def text(x, y, value, color=None, size=FONT_SIZE):
    hb_gpu_draw.draw_text(FONT, x, y, size, color or COLORS['text'], value)


def text_width(value, size=FONT_SIZE):
    blf.size(FONT, size)
    return blf.dimensions(FONT, value)[0]


def button(sh, r, label, hot=False, primary=False):
    rect(sh, r, COLORS['button_primary'] if primary else (COLORS['button_hot'] if hot else COLORS['button']))
    outline(sh, r, COLORS['border'])
    w = text_width(label)
    text(r[0] + (r[2] - w) / 2.0, hb_gpu_draw.vcenter_baseline(r, FONT, FONT_SIZE), label)


def length_label(meters):
    return units.format_value(meters)


# Mundo 2D (por View2D) --------------------------------------------------------------------------------------------

def box(sh, view, lo, hi, color, fill=None):
    """Retângulo do mundo 2D (lo = (x, y) mínimo, hi = máximo) com contorno e preenchimento opcional."""
    a = view.to_screen(lo)
    b = view.to_screen(hi)
    r = (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]))
    if fill:
        rect(sh, r, fill)
    outline(sh, r, color)
    return r


def segment(sh, view, p0, p1, color, dashed_line=False):
    a, b = view.to_screen(p0), view.to_screen(p1)
    lines(sh, dashed(a, b) if dashed_line else [a, b], color)
