"""Painting a Drawing in the viewport.

The record is compiled once into a few vertex batches (one of
triangles, one of lines for each line width) and painted into an
offscreen texture; the viewport then only has to show the texture, so
zooming and panning a sheet cost nothing.

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


class Compiled:
    def __init__(self, drawing):
        self.width, self.height = drawing.width, drawing.height
        self.tri_pos, self.tri_col = [], []
        self.lines = {}             # width -> (positions, colours)
        self.texts = []
        self._batches = None
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
            lines = [(w, batch_for_shader(poly, 'LINES',
                                          {'pos': p, 'color': c}))
                     for w, (p, c) in sorted(self.lines.items()) if p]
            self._batches = (flat, poly, tris, lines)
        return self._batches


def render(compiled, scale):
    """Paint `compiled` into a new GPUOffScreen at `scale` pixels to the
    point. The caller frees it."""
    w = max(8, int(compiled.width * scale))
    h = max(8, int(compiled.height * scale))
    off = gpu.types.GPUOffScreen(w, h)
    flat, poly, tris, lines = compiled.batches()
    # Page points to clip space; depth 0..1, the later call nearer.
    proj = Matrix(((2.0 / compiled.width, 0, 0, -1.0),
                   (0, 2.0 / compiled.height, 0, -1.0),
                   (0, 0, -2.0, 1.0),
                   (0, 0, 0, 1.0)))
    pixels = Matrix(((2.0 / w, 0, 0, -1.0), (0, 2.0 / h, 0, -1.0),
                     (0, 0, -1.0, 0.0), (0, 0, 0, 1.0)))
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
                for width, batch in lines:
                    poly.bind()
                    poly.uniform_float('viewportSize', (w, h))
                    poly.uniform_float('lineWidth', max(1.0, width * scale))
                    batch.draw(poly)
            finally:
                gpu.state.depth_test_set('NONE')
                gpu.state.depth_mask_set(False)
            gpu.matrix.load_projection_matrix(pixels)
            gpu.state.blend_set('ALPHA')
            font = 0
            for x, y, text, size, angle, color, halo in compiled.texts:
                blf.size(font, max(1.0, size * scale))
                blf.color(font, *color)
                blf.position(font, x * scale, y * scale, 0.0)
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
