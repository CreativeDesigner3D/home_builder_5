"""Painting a Drawing in the viewport.

The record is compiled once into a batch of triangles and lists of
lines, and painted into an offscreen texture one pixel of the sheet to
one of the screen: the lines set on the pixel grid at whole-pixel
weights, so they come out solid black, never smeared grey. The
viewport shows the texture, stretched while the view is zoomed or
panned, and the sheet is painted again once it settles.

A drawing's calls are in paint order: a white face laid over the lines
behind it hides them. Each call is given a depth that rises with its
place in the record, and the offscreen's own depth buffer keeps that
order however the batches are grouped.
"""

import math

import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix
from mathutils.geometry import tessellate_polygon


# Lines are drawn this much heavier on screen than on paper: at a sheet's
# fit the paper's light and heavy weights would both round to one pixel.
SCREEN_WEIGHT = 1.6


class Compiled:
    def __init__(self, drawing):
        self.width, self.height = drawing.width, drawing.height
        self.tri_pos, self.tri_col = [], []
        self.lines = {}             # width -> (positions, colours)
        self.texts = []
        self.images = []            # (rgb, px_w, px_h, x, y, w, h)
        self._batches = None
        self._textures = None
        calls = drawing.calls
        n = len(calls) + 2
        stroke = fill = (0.0, 0.0, 0.0, 1.0)
        width, dash = 1.0, None
        ox = oy = 0.0
        stack = []
        for i, (name, args, kw) in enumerate(calls):
            z = (i + 1) / n
            if name == 'stroke_color':
                stroke = tuple(args[0][:3]) + (1.0,)
            elif name == 'fill_color':
                fill = tuple(args[0][:3]) + (1.0,)
            elif name == 'line_width':
                width = float(args[0])
            elif name == 'dash':
                on = args[0] if args else kw.get('on')
                off = args[1] if len(args) > 1 else kw.get('off')
                dash = (on, off or on) if on else None
            elif name == 'push':
                stack.append((ox, oy, stroke, fill, width, dash))
            elif name == 'pop':
                if stack:
                    ox, oy, stroke, fill, width, dash = stack.pop()
            elif name == 'translate':
                ox += args[0]
                oy += args[1]
            elif name == 'lines':
                self._segments(args[0], ox, oy, z, stroke, width, dash)
            elif name == 'rect':
                x, y, w, h = args[:4]
                do_fill = args[4] if len(args) > 4 else kw.get('fill', False)
                do_stroke = args[5] if len(args) > 5 else kw.get('stroke', True)
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                self._poly(pts, ox, oy, z, fill, stroke, width, dash,
                           do_fill, do_stroke)
            elif name == 'polygon':
                do_fill = args[1] if len(args) > 1 else kw.get('fill', True)
                do_stroke = args[2] if len(args) > 2 else kw.get('stroke', False)
                self._poly(list(args[0]), ox, oy, z, fill, stroke, width,
                           dash, do_fill, do_stroke)
            elif name == 'circle':
                cx, cy, r = args[:3]
                do_fill = args[3] if len(args) > 3 else kw.get('fill', False)
                do_stroke = args[4] if len(args) > 4 else kw.get('stroke', True)
                steps = 10 if r < 2.0 else 32
                pts = [(cx + r * math.cos(a * 2 * math.pi / steps),
                        cy + r * math.sin(a * 2 * math.pi / steps))
                       for a in range(steps)]
                self._poly(pts, ox, oy, z, fill, stroke, width, None,
                           do_fill, do_stroke)
            elif name == 'image':
                rgb, px_w, px_h, x, y, w, h = args[:7]
                self.images.append((rgb, px_w, px_h, x + ox, y + oy, w, h))
            elif name == 'text':
                x, y, text, size = args[:4]
                angle = args[4] if len(args) > 4 else kw.get('angle', 0.0)
                halo = args[6] if len(args) > 6 else kw.get('halo')
                if text:
                    self.texts.append((x + ox, y + oy, str(text), size,
                                       angle, fill, halo))

    def _segments(self, segments, ox, oy, z, color, width, dash):
        key = round(max(width, 0.1) * 20) / 20.0
        pos, col = self.lines.setdefault(key, ([], []))
        for a, b in segments:
            ax, ay, bx, by = a[0] + ox, a[1] + oy, b[0] + ox, b[1] + oy
            if dash is None:
                pos += [(ax, ay, z), (bx, by, z)]
                col += [color, color]
                continue
            length = math.hypot(bx - ax, by - ay)
            if length < 1e-6:
                continue
            on, off = dash
            ux, uy = (bx - ax) / length, (by - ay) / length
            t = 0.0
            while t < length:
                e = min(t + on, length)
                pos += [(ax + ux * t, ay + uy * t, z),
                        (ax + ux * e, ay + uy * e, z)]
                col += [color, color]
                t += on + off

    def _poly(self, pts, ox, oy, z, fill, stroke, width, dash, do_fill,
              do_stroke):
        if len(pts) < 2:
            return
        if do_fill and len(pts) >= 3:
            if len(pts) <= 4:
                tris = [(0, k, k + 1) for k in range(1, len(pts) - 1)]
            else:
                tris = tessellate_polygon([[(p[0], p[1], 0.0) for p in pts]])
            for tri in tris:
                for k in tri:
                    self.tri_pos.append((pts[k][0] + ox, pts[k][1] + oy, z))
                    self.tri_col.append(fill)
        if do_stroke:
            segs = [(pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts))]
            # A hair nearer than its own fill.
            self._segments(segs, ox, oy, z + 1e-7, stroke, width, dash)

    def batches(self):
        if self._batches is None:
            flat = gpu.shader.from_builtin('FLAT_COLOR')
            poly = gpu.shader.from_builtin('POLYLINE_FLAT_COLOR')
            tris = batch_for_shader(flat, 'TRIS', {
                'pos': self.tri_pos, 'color': self.tri_col}) \
                if self.tri_pos else None
            # The lines are batched at each paint, set on its pixels.
            self._batches = (flat, poly, tris, None)
        return self._batches


def _image_textures(compiled):
    """A texture for each image on the sheet, made once."""
    if compiled._textures is None:
        compiled._textures = []
        import numpy as np
        for rgb, px_w, px_h, x, y, w, h in compiled.images:
            try:
                rows = np.frombuffer(rgb, dtype=np.uint8).reshape(
                    px_h, px_w, 3)[::-1]            # bottom row first
                rgba = np.ones((px_h, px_w, 4), dtype=np.float32)
                rgba[:, :, :3] = rows / 255.0
                buf = gpu.types.Buffer('FLOAT', px_w * px_h * 4,
                                       rgba.ravel())
                tex = gpu.types.GPUTexture((px_w, px_h), format='RGBA8',
                                           data=buf)
                compiled._textures.append((tex, x, y, w, h))
            except Exception as exc:
                print("Drawings: image:", exc)
    return compiled._textures


def _pixel_widths(compiled, scale):
    """{whole pixels wide: (positions, colours)} of the sheet's lines at
    `scale`, in sheet pixels. A line is never thinner than one pixel,
    and one that runs square to the page sits on whole pixels -- in the
    middle of a pixel when it is an odd number wide -- so it is drawn
    solid, not smeared grey across two."""
    import numpy as np
    out = {}
    for width, (pos, col) in compiled.lines.items():
        if not pos:
            continue
        px = max(1, int(round(width * scale * SCREEN_WEIGHT)))
        p = np.asarray(pos, dtype=np.float64).reshape(-1, 2, 3)
        p[:, :, :2] *= scale
        half = 0.5 if px % 2 else 0.0
        d = np.abs(p[:, 1, :2] - p[:, 0, :2])
        for axis, square in ((0, d[:, 0] < 0.01), (1, d[:, 1] < 0.01)):
            # Square to the page: the line's own axis on the pixel grid,
            # its ends on whole pixels.
            p[square, :, axis] = np.floor(p[square, :, axis]) + half
            p[square, :, 1 - axis] = np.round(p[square, :, 1 - axis])
        smooth = ~((d[:, 0] < 0.01) | (d[:, 1] < 0.01))
        c = np.asarray(col, dtype=np.float32).reshape(-1, 2, 4)
        for key, rows in ((False, ~smooth), (True, smooth)):
            if rows.any():
                got = out.setdefault((px, key), ([], []))
                got[0].append(p[rows].reshape(-1, 3))
                got[1].append(c[rows].reshape(-1, 4))
    return {k: (np.concatenate(v[0]), np.concatenate(v[1]))
            for k, v in out.items()}


def render(compiled, scale, window=None):
    """Paint `compiled` into a new GPUOffScreen at `scale` pixels to the
    point. `window` (x, y, w, h in the sheet's pixels at that scale)
    paints only that part of it, one pixel of the sheet to one of the
    texture; the whole sheet when None. The caller frees it."""
    if window is None:
        window = (0, 0, compiled.width * scale, compiled.height * scale)
    wx, wy = int(round(window[0])), int(round(window[1]))
    w = max(8, int(round(window[2])))
    h = max(8, int(round(window[3])))
    off = gpu.types.GPUOffScreen(w, h)
    flat, poly, tris, _lines = compiled.batches()
    # Page points to clip space; depth 0..1, the later call nearer.
    proj = Matrix(((2.0 * scale / w, 0, 0, -1.0 - 2.0 * wx / w),
                   (0, 2.0 * scale / h, 0, -1.0 - 2.0 * wy / h),
                   (0, 0, -2.0, 1.0),
                   (0, 0, 0, 1.0)))
    # The lines come already in sheet pixels.
    line_proj = Matrix(((2.0 / w, 0, 0, -1.0 - 2.0 * wx / w),
                        (0, 2.0 / h, 0, -1.0 - 2.0 * wy / h),
                        (0, 0, -2.0, 1.0),
                        (0, 0, 0, 1.0)))
    pixels = Matrix(((2.0 / w, 0, 0, -1.0), (0, 2.0 / h, 0, -1.0),
                     (0, 0, -1.0, 0.0), (0, 0, 0, 1.0)))
    lines = []
    for (px, smooth), (pos, col) in sorted(
            _pixel_widths(compiled, scale).items()):
        lines.append((px, smooth, batch_for_shader(
            poly, 'LINES', {'pos': pos.tolist(), 'color': col.tolist()})))
    with off.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(1.0, 1.0, 1.0, 1.0), depth=1.0)
        with gpu.matrix.push_pop(), gpu.matrix.push_pop_projection():
            gpu.matrix.load_matrix(Matrix.Identity(4))
            gpu.matrix.load_projection_matrix(proj)
            gpu.state.blend_set('NONE')
            gpu.state.depth_mask_set(True)
            gpu.state.depth_test_set('LESS_EQUAL')
            try:
                if tris is not None:
                    flat.bind()
                    tris.draw(flat)
                gpu.matrix.load_projection_matrix(line_proj)
                for px, smooth, batch in lines:
                    poly.bind()
                    poly.uniform_float('viewportSize', (w, h))
                    poly.uniform_float('lineWidth', float(px))
                    try:
                        poly.uniform_bool('lineSmooth', smooth)
                    except Exception:
                        pass
                    if smooth:
                        gpu.state.blend_set('ALPHA')
                    batch.draw(poly)
                    gpu.state.blend_set('NONE')
            finally:
                gpu.state.depth_test_set('NONE')
                gpu.state.depth_mask_set(False)
            gpu.matrix.load_projection_matrix(pixels)
            if compiled.images:
                from gpu_extras.presets import draw_texture_2d
                for tex, x, y, iw, ih in _image_textures(compiled):
                    draw_texture_2d(tex, (x * scale - wx, y * scale - wy),
                                    iw * scale, ih * scale)
            gpu.state.blend_set('ALPHA')
            font = 0
            for x, y, text, size, angle, color, halo in compiled.texts:
                blf.size(font, max(1.0, size * scale))
                blf.color(font, *color)
                blf.position(font, round(x * scale) - wx,
                             round(y * scale) - wy, 0.0)
                if angle:
                    blf.enable(font, blf.ROTATION)
                    blf.rotation(font, angle)
                if halo:
                    blf.enable(font, blf.SHADOW)
                    blf.shadow(font, 5, 1.0, 1.0, 1.0, 1.0)
                    blf.shadow_offset(font, 0, 0)
                blf.draw(font, text)
                if angle:
                    blf.disable(font, blf.ROTATION)
                if halo:
                    blf.disable(font, blf.SHADOW)
            gpu.state.blend_set('NONE')
    return off
