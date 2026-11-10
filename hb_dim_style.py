"""Viewport dimensions drawn the way a drafter draws them.

The size overlays (cabinet / bay / opening / part labels, wall and door
labels) all project their dimension lines to region space as groups of
six points -- the line, then a perpendicular tick at each end. This
module paints those groups in drawing style instead of as UI widgets:

- a 45 degree architectural tick at each end instead of a perpendicular
  bar;
- the value sits IN the line: the line is broken where the label is,
  so the number reads as part of the dimension rather than a box laid
  over it;
- no label box; the text and the line carry a soft dark halo, so they
  read over a light cabinet face and the dark viewport alike.

Label rects are unchanged -- they stay the click targets the overlays
hit-test -- so only the painting moves here.
"""

import math

import blf
import gpu
from gpu_extras.batch import batch_for_shader

TICK_PX = 4.5            # half-length of a tick, per axis
LINE_PX = 1.0
TICK_LINE_PX = 2.0
HALO = (0.0, 0.0, 0.0, 0.55)
TEXT_HALO = (0.0, 0.0, 0.0, 1.0)
BREAK_PAD_PX = 3         # clear space either side of a value in its line


def polyline(region, pts, width, color):
    if not pts:
        return
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)


def stroke(region, pts, width, color, s=1.0, halo=HALO):
    """LINES with a halo under them (dark by default)."""
    if not pts:
        return
    polyline(region, pts, width + 2.0 * s, (halo[0], halo[1], halo[2],
                                            halo[3] * color[3]))
    polyline(region, pts, width, color)


def _clip_out(a, b, rect):
    """The parts of segment a-b outside rect (x, y, w, h)."""
    x0, y0 = rect[0], rect[1]
    x1, y1 = x0 + rect[2], y0 + rect[3]
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]),
                 (-dy, a[1] - y0), (dy, y1 - a[1])):
        if abs(p) < 1e-9:
            if q < 0:
                return [(a, b)]
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return [(a, b)]
    out = []
    if t0 > 1e-6:
        out.append((a, (a[0] + dx * t0, a[1] + dy * t0)))
    if t1 < 1.0 - 1e-6:
        out.append(((a[0] + dx * t1, a[1] + dy * t1), b))
    return out


def break_around(segments, rects, pad):
    """Segments with every rect (grown by pad) cut out of them."""
    grown = [(r[0] - pad, r[1] - pad, r[2] + 2 * pad, r[3] + 2 * pad)
             for r in rects]
    for r in grown:
        nxt = []
        for a, b in segments:
            nxt.extend(_clip_out(a, b, r))
        segments = nxt
    return segments


def slash(p, s, back=False):
    """A tick at p: '/' -- or '\\' for a line that itself runs along '/',
    where a '/' would lie on the line and vanish."""
    t = TICK_PX * s
    if back:
        return [(p[0] + t, p[1] - t), (p[0] - t, p[1] + t)]
    return [(p[0] - t, p[1] - t), (p[0] + t, p[1] + t)]


def _runs_along_slash(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return n > 1e-6 and abs(dx + dy) / (n * math.sqrt(2.0)) > 0.92


def split_groups(pts):
    """Old-style six-point groups -> (lines [(a, b)], ends [(p, back)])."""
    lines, ends = [], []
    for i in range(0, len(pts) - 5, 6):
        a, b = tuple(pts[i]), tuple(pts[i + 1])
        lines.append((a, b))
        back = _runs_along_slash(a, b)
        ends += [(a, back), (b, back)]
    return lines, ends


def paint_groups(region, pts, rects, color, s=1.0):
    """Paint six-point dimension groups in drawing style, the lines
    broken around ``rects`` (the labels on them)."""
    lines, ends = split_groups(pts)
    if not lines:
        return
    lines = break_around(lines, rects, BREAK_PAD_PX * s)
    stroke(region, [p for seg in lines for p in seg], LINE_PX * s, color, s)
    ticks = []
    for p, back in ends:
        ticks += slash(p, s, back)
    stroke(region, ticks, TICK_LINE_PX * s, color, s)


OUTLINE_LEVEL = 6        # blf shadow level that draws a crisp outline


def text(x, y, size, color, string):
    """A value with a dark outline and halo, baseline at (x, y)."""
    previous = gpu.state.blend_get()
    halo = (*TEXT_HALO[:3], TEXT_HALO[3] * color[3])
    blf.size(0, size)
    blf.enable(0, blf.SHADOW)
    blf.color(0, *color)
    blf.position(0, x, y, 0)
    # A soft halo first, then a hard outline stamped a pixel to each
    # side: a blurred shadow alone is too faint to carry a light value
    # over a white face.
    blf.shadow_offset(0, 0, 0)
    blf.shadow(0, 5, *halo)
    blf.draw(0, string)
    r = max(1, int(round(size / 14.0)))
    blf.shadow(0, OUTLINE_LEVEL, *halo)
    for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
        blf.shadow_offset(0, dx, dy)
        blf.draw(0, string)
    blf.shadow_offset(0, 0, 0)
    blf.disable(0, blf.SHADOW)
    gpu.state.blend_set(previous)


def label_text(rect, size, color, string):
    """``string`` centred in a label rect."""
    blf.size(0, size)
    tw = blf.dimensions(0, string)[0]
    th = blf.dimensions(0, "0123456789\"")[1]
    x = rect[0] + (rect[2] - tw) / 2.0
    y = rect[1] + (rect[3] - th) / 2.0
    text(math.floor(x), math.floor(y), size, color, string)
