"""A drawing as a record of drawing calls.

A Drawing stands in for hb_pdf.Page: whatever draws on a page can draw
on one of these instead, and the calls are kept rather than written.
The record can then be measured, cached, set into another drawing at an
offset, written to a PDF page, or painted in the viewport -- the same
record every time, so what is previewed is what prints.

Units are page points, origin bottom left, y up.
"""

import math


class Drawing:
    def __init__(self, width=0.0, height=0.0):
        self.width = width
        self.height = height
        self.calls = []
        # Named points other drawings line up on, in this drawing's units.
        self.anchors = {}
        # Whatever the view that made it wants its sheet to know (the
        # drafting scale's label, the points to the metre it drew at).
        self.info = {}

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)

        def call(*args, **kw):
            self.calls.append((name, args, kw))
        return call

    def place(self, target, x=0.0, y=0.0):
        """Draw this record on `target` (a page or another Drawing) with
        its origin at (x, y)."""
        target.push()
        target.translate(x, y)
        for name, args, kw in self.calls:
            getattr(target, name)(*args, **kw)
        target.pop()

    def bounds(self):
        """(x0, y0, x1, y1) of the line work and text origins."""
        xs, ys = [], []
        ox = oy = 0.0
        stack = []
        for name, args, _kw in self.calls:
            if name == 'push':
                stack.append((ox, oy))
            elif name == 'pop':
                if stack:
                    ox, oy = stack.pop()
            elif name == 'translate':
                ox += args[0]
                oy += args[1]
            elif name == 'lines':
                for a, b in args[0]:
                    xs += [a[0] + ox, b[0] + ox]
                    ys += [a[1] + oy, b[1] + oy]
            elif name == 'polygon':
                xs += [p[0] + ox for p in args[0]]
                ys += [p[1] + oy for p in args[0]]
            elif name == 'rect':
                xs += [args[0] + ox, args[0] + args[2] + ox]
                ys += [args[1] + oy, args[1] + args[3] + oy]
            elif name == 'circle':
                xs += [args[0] - args[2] + ox, args[0] + args[2] + ox]
                ys += [args[1] - args[2] + oy, args[1] + args[2] + oy]
            elif name == 'text':
                xs.append(args[0] + ox)
                ys.append(args[1] + oy)
        if not xs:
            return 0.0, 0.0, self.width, self.height
        return min(xs), min(ys), max(xs), max(ys)


# ---- Cropping -------------------------------------------------------------------

def _clip_segment(p, q, box):
    """The part of p-q inside box (x0, y0, x1, y1), or None (Liang-Barsky)."""
    x0, y0, x1, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for edge_p, edge_q in ((-dx, p[0] - x0), (dx, x1 - p[0]),
                           (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(edge_p) < 1e-12:
            if edge_q < 0.0:
                return None
            continue
        t = edge_q / edge_p
        if edge_p < 0.0:
            if t > t1:
                return None
            t0 = max(t0, t)
        else:
            if t < t0:
                return None
            t1 = min(t1, t)
    return ((p[0] + t0 * dx, p[1] + t0 * dy),
            (p[0] + t1 * dx, p[1] + t1 * dy))


def _clip_polygon(points, box):
    """The polygon cut down to box (Sutherland-Hodgman)."""
    x0, y0, x1, y1 = box
    edges = ((lambda p: p[0] >= x0, lambda p, q: (x0, p[1] + (q[1] - p[1])
              * (x0 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[0] <= x1, lambda p, q: (x1, p[1] + (q[1] - p[1])
              * (x1 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[1] >= y0, lambda p, q: (p[0] + (q[0] - p[0])
              * (y0 - p[1]) / (q[1] - p[1]), y0)),
             (lambda p: p[1] <= y1, lambda p, q: (p[0] + (q[0] - p[0])
              * (y1 - p[1]) / (q[1] - p[1]), y1)))
    out = list(points)
    for inside, cross in edges:
        if not out:
            break
        pts, out = out, []
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
            prev = cur
    return out


def _arg(args, kw, i, name, default):
    return args[i] if len(args) > i else kw.get(name, default)


def _within(box, x0, y0, x1, y1):
    return box[0] <= x0 and x1 <= box[2] and box[1] <= y0 and y1 <= box[3]


def _clear_of(box, x0, y0, x1, y1):
    return x1 < box[0] or x0 > box[2] or y1 < box[1] or y0 > box[3]


def crop(drawing, box):
    """A copy of `drawing` with only what lies inside `box` (x0, y0, x1,
    y1, in the drawing's units): lines and outlines cut at its edges,
    fills cut to it, text kept where it starts inside, images cut to it.
    Its anchors and info are kept, so it stands where the whole one did."""
    out = Drawing(drawing.width, drawing.height)
    out.anchors = dict(drawing.anchors)
    out.info = dict(drawing.info)
    ox = oy = 0.0
    stack = []
    calls = out.calls

    def outline(points):
        segs = [_clip_segment(points[i - 1], points[i], local)
                for i in range(len(points))]
        segs = [s for s in segs if s is not None]
        if segs:
            calls.append(('lines', (segs,), {}))

    def shape(points, fill, stroke):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        if _clear_of(local, min(xs), min(ys), max(xs), max(ys)):
            return False
        if fill:
            cut = _clip_polygon(points, local)
            if len(cut) >= 3:
                calls.append(('polygon', (cut,), {'fill': True,
                                                  'stroke': False}))
        if stroke:
            outline(points)
        return True

    for name, args, kw in drawing.calls:
        local = (box[0] - ox, box[1] - oy, box[2] - ox, box[3] - oy)
        if name == 'push':
            stack.append((ox, oy))
        elif name == 'pop':
            if stack:
                ox, oy = stack.pop()
        elif name == 'translate':
            ox += args[0]
            oy += args[1]
        elif name == 'lines':
            segs = [_clip_segment(a, b, local) for a, b in args[0]]
            segs = [s for s in segs if s is not None]
            if segs:
                calls.append(('lines', (segs,), {}))
            continue
        elif name in ('rect', 'polygon', 'circle'):
            if name == 'rect':
                x, y, w, h = args[:4]
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                fill = _arg(args, kw, 4, 'fill', False)
                stroke = _arg(args, kw, 5, 'stroke', True)
            elif name == 'polygon':
                pts = list(args[0])
                fill = _arg(args, kw, 1, 'fill', True)
                stroke = _arg(args, kw, 2, 'stroke', False)
            else:
                cx, cy, r = args[:3]
                if _within(local, cx - r, cy - r, cx + r, cy + r):
                    calls.append((name, args, kw))
                    continue
                pts = [(cx + r * math.cos(i * math.pi / 24.0),
                        cy + r * math.sin(i * math.pi / 24.0))
                       for i in range(48)]
                fill = _arg(args, kw, 3, 'fill', False)
                stroke = _arg(args, kw, 4, 'stroke', True)
            if pts and _within(local, min(p[0] for p in pts),
                               min(p[1] for p in pts),
                               max(p[0] for p in pts),
                               max(p[1] for p in pts)):
                calls.append((name, args, kw))
            elif len(pts) >= 3:
                shape(pts, fill, stroke)
            continue
        elif name == 'text':
            x, y = args[0], args[1]
            if not (local[0] - 0.5 <= x <= local[2] + 0.5
                    and local[1] - 0.5 <= y <= local[3] + 0.5):
                continue
        elif name == 'image':
            rgb, pw, ph, x, y, w, h = args[:7]
            if _clear_of(local, x, y, x + w, y + h):
                continue
            if not _within(local, x, y, x + w, y + h) and w > 0 and h > 0:
                # The pixels inside the box; rows run top first.
                c0 = max(0, int(math.floor((local[0] - x) / w * pw)))
                c1 = min(pw, int(math.ceil((local[2] - x) / w * pw)))
                r0 = max(0, int(math.floor((y + h - local[3]) / h * ph)))
                r1 = min(ph, int(math.ceil((y + h - local[1]) / h * ph)))
                if c1 <= c0 or r1 <= r0:
                    continue
                data = bytes(rgb)
                rows = [data[(r * pw + c0) * 3:(r * pw + c1) * 3]
                        for r in range(r0, r1)]
                args = (b''.join(rows), c1 - c0, r1 - r0,
                        x + c0 * w / pw, y + h - r1 * h / ph,
                        (c1 - c0) * w / pw, (r1 - r0) * h / ph)
                kw = {}
        calls.append((name, args, kw))
    return out
