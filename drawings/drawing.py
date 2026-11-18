"""A drawing as a record of drawing calls.

A Drawing stands in for hb_pdf.Page: whatever draws on a page can draw
on one of these instead, and the calls are kept rather than written.
The record can then be measured, cached, set into another drawing at an
offset, written to a PDF page, or painted in the viewport -- the same
record every time, so what is previewed is what prints.

Units are page points, origin bottom left, y up.
"""


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
