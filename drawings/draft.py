"""Drafting marks the symbolic views and the sheet composer share:
dimensions, hatching, view titles, the markers that point from one view
to another. Everything draws on a page-like object in page points."""

import math

from .. import hb_pdf

INK = (0.0, 0.0, 0.0)
GREY = (0.45, 0.45, 0.45)
MARK = (0.6, 0.6, 0.6)
WHITE = (1.0, 1.0, 1.0)
INCH = 0.0254


def text_centered(page, cx, y, text, size, halo=True):
    w = hb_pdf.text_width(text, size)
    page.fill_color(INK)
    page.text(cx - w / 2.0, y, text, size,
              halo=(WHITE, 2.5) if halo else None)
    return w


def dim_h(page, x0, x1, y, text, ext_to=None, size=7.0):
    """A horizontal dimension: a thin line broken round its value where
    the value fits, slash ticks, and extension lines back to `ext_to`."""
    page.stroke_color(GREY)
    page.line_width(0.4)
    w = hb_pdf.text_width(text, size) + 6.0
    cx = (x0 + x1) / 2.0
    if w < (x1 - x0) - 8.0:
        page.lines([((x0, y), (cx - w / 2, y)), ((cx + w / 2, y), (x1, y))])
        ty = y - size * 0.35
    else:
        page.lines([((x0, y), (x1, y))])
        ty = y + 3.0
    for x in (x0, x1):
        page.lines([((x - 2.5, y - 2.5), (x + 2.5, y + 2.5))])
        if ext_to is not None:
            if ext_to < y:
                page.lines([((x, ext_to + 3.0), (x, y + 4.0))])
            else:
                page.lines([((x, y - 4.0), (x, ext_to - 3.0))])
    text_centered(page, cx, ty, text, size)


def dim_v(page, y0, y1, x, text, ext_to=None, size=7.0, side=-1):
    """A vertical dimension, its value level beside the line: to the
    left (`side` -1) or the right (1)."""
    page.stroke_color(GREY)
    page.line_width(0.4)
    page.lines([((x, y0), (x, y1))])
    for y in (y0, y1):
        page.lines([((x - 2.5, y - 2.5), (x + 2.5, y + 2.5))])
        if ext_to is not None:
            if ext_to > x:
                page.lines([((x - 4.0, y), (ext_to - 3.0, y))])
            else:
                page.lines([((ext_to + 3.0, y), (x + 4.0, y))])
    w = hb_pdf.text_width(text, size)
    page.fill_color(INK)
    tx = x - w - 4.0 if side < 0 else x + 4.0
    page.text(tx, (y0 + y1) / 2.0 - size * 0.35, text, size,
              halo=(WHITE, 2.5))


def clip_segment(a, b, poly):
    """The part of segment a-b inside the convex polygon `poly`, or None."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1]
               - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sign = 1.0 if area > 0 else -1.0
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        nx, ny = -(q[1] - p[1]) * sign, (q[0] - p[0]) * sign   # inward
        num = (a[0] - p[0]) * nx + (a[1] - p[1]) * ny
        den = dx * nx + dy * ny
        if abs(den) < 1e-9:
            if num < 0:
                return None
            continue
        t = -num / den
        if den > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 >= t1:
            return None
    return ((a[0] + dx * t0, a[1] + dy * t0),
            (a[0] + dx * t1, a[1] + dy * t1))


def hatch(page, poly, gap=4.0):
    """A convex polygon outlined and hatched at 45 degrees (a wall cut
    through in plan)."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = y1 - y0
    segs = []
    c = x0 - span
    while c < x1:
        seg = clip_segment((c, y0), (c + span, y1), poly)
        if seg:
            segs.append(seg)
        c += gap
    page.stroke_color(INK)
    page.line_width(0.3)
    page.lines(segs)
    page.line_width(0.8)
    page.lines([(poly[i], poly[(i + 1) % len(poly)])
                for i in range(len(poly))])


def clip_below(poly, ymin):
    """`poly` cut off below y = ymin."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        pin, qin = p[1] >= ymin, q[1] >= ymin
        if pin:
            out.append(p)
        if pin != qin:
            t = (ymin - p[1]) / (q[1] - p[1])
            out.append((p[0] + (q[0] - p[0]) * t, ymin))
    return out


def hull(points):
    """Convex hull, counter-clockwise."""
    pts = sorted(set((round(x, 5), round(y, 5)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _bubble(page, cx, cy, r, top, bottom):
    page.fill_color(WHITE)
    page.stroke_color(INK)
    page.line_width(0.6)
    page.circle(cx, cy, r, fill=True, stroke=True)
    page.lines([((cx - r, cy), (cx + r, cy))])
    text_centered(page, cx, cy + r * 0.23, top, r * 0.62, halo=False)
    text_centered(page, cx, cy - r * 0.72, bottom, r * 0.5, halo=False)


def view_title(page, x, y, mark, sheet, title, scale, width=250.0):
    """The title under a view: its mark over the sheet it is on, its
    name over a rule, its scale under the rule's end."""
    r = 13.0
    page.stroke_color(INK)
    page.line_width(0.6)
    page.lines([((x + r, y), (x + r + width, y))])
    _bubble(page, x + r, y, r, mark, f"PG{sheet}")
    page.fill_color(INK)
    page.text(x + 2 * r + 14.0, y + 3.0, title, 8.0)
    w = hb_pdf.text_width(scale, 10.0)
    page.text(x + r + width - w, y - 11.0, scale, 10.0)


def elevation_marker(page, cx, cy, mark, sheet):
    """On a plan: which elevation looks at the wall above this point."""
    page.fill_color(MARK)
    page.polygon([(cx - 17, cy), (cx + 17, cy), (cx, cy + 17)], fill=True)
    _bubble(page, cx, cy, 11.0, mark, f"PG{sheet}")


def section_marker(page, x, y, mark, sheet):
    """On an elevation: where a section is cut, and which way it looks."""
    page.stroke_color(INK)
    page.line_width(0.6)
    page.dash(6.0, 2.0)
    page.lines([((x, y - 40.0), (x, y + 6.0))])
    page.dash()
    page.fill_color(MARK)
    page.polygon([(x, y + 4.0), (x, y + 30.0), (x + 15.0, y + 17.0)],
                 fill=True)
    _bubble(page, x, y + 17.0, 10.0, mark, f"PG{sheet}")


def rotated_label(page, x, y, text, size):
    """Text reading down the page from (x, y)."""
    page.fill_color(INK)
    page.text(x, y, text, size, angle=-math.pi / 2.0)


def dim_aligned(page, a, b, offset, text, size=7.0):
    """A dimension along a-b, standing off it by the vector `offset`:
    its value level, over a break in the line."""
    ox, oy = offset
    p, q = (a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)
    length = math.hypot(q[0] - p[0], q[1] - p[1])
    if length < 1e-6:
        return
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    w = hb_pdf.text_width(text, size) + 6.0
    # How much of the line a level value covers where it crosses it.
    cover = min(length - 8.0, abs(ux) * w + abs(uy) * (size + 4.0))
    mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
    page.stroke_color(GREY)
    page.line_width(0.4)
    if cover > 0.0:
        h = cover / 2.0
        page.lines([(p, (mid[0] - ux * h, mid[1] - uy * h)),
                    ((mid[0] + ux * h, mid[1] + uy * h), q)])
    else:
        page.lines([(p, q)])
    n = math.hypot(ox, oy) or 1.0
    nx, ny = ox / n, oy / n
    for end, start in ((p, a), (q, b)):
        # A slash across the line, and the extension line back to the wall.
        sx, sy = (ux + nx) * 2.5, (uy + ny) * 2.5
        page.lines([((end[0] - sx, end[1] - sy), (end[0] + sx, end[1] + sy)),
                    ((start[0] + nx * 3.0, start[1] + ny * 3.0),
                     (end[0] + nx * 4.0, end[1] + ny * 4.0))])
    text_centered(page, mid[0], mid[1] - size * 0.35, text, size)


def elevation_marker_toward(page, cx, cy, direction, mark, sheet):
    """On a plan: the elevation that looks along `direction` from here."""
    dx, dy = direction
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    px, py = -dy, dx
    page.fill_color(MARK)
    page.polygon([(cx + px * 17, cy + py * 17), (cx - px * 17, cy - py * 17),
                  (cx + dx * 17, cy + dy * 17)], fill=True)
    _bubble(page, cx, cy, 11.0, mark, f"PG{sheet}")


NOTE_SIZE = 6.5
NOTE_LEADING = 1.25


def note_box(at, text, tip=None, size=NOTE_SIZE):
    """(x0, y0, x1, y1) a note's text takes, and where each line
    starts: a note with a leader stands beside the leader's end and
    runs away from what it points at; one without is centred."""
    rows = text.split('\n') if text else ['']
    widths = [hb_pdf.text_width(r, size) for r in rows]
    w = max(widths + [size])
    step = size * NOTE_LEADING
    h = step * len(rows)
    top = at[1] + h / 2.0
    if tip is None:
        x0 = at[0] - w / 2.0
        starts = [at[0] - rw / 2.0 for rw in widths]
    elif tip[0] <= at[0]:
        x0 = at[0] + 3.0
        starts = [x0] * len(rows)
    else:
        x0 = at[0] - 3.0 - w
        starts = [at[0] - 3.0 - rw for rw in widths]
    lines = [(starts[i], top - step * i - size * 0.82, rows[i])
             for i in range(len(rows))]
    return (x0, top - h, x0 + w, top), lines


def note(page, at, text, tip=None, size=NOTE_SIZE):
    """A typed note, with a leader and arrowhead to `tip` when it has
    one. Returns the box its text takes."""
    box, lines = note_box(at, text, tip, size)
    if tip is not None:
        page.stroke_color(INK)
        page.line_width(0.45)
        page.lines([(at, tip)])
        dx, dy = at[0] - tip[0], at[1] - tip[1]
        n = math.hypot(dx, dy)
        if n > 1e-6:
            ux, uy = dx / n, dy / n
            px, py = -uy, ux
            page.fill_color(INK)
            page.polygon([tip,
                          (tip[0] + ux * 6.0 + px * 1.8,
                           tip[1] + uy * 6.0 + py * 1.8),
                          (tip[0] + ux * 6.0 - px * 1.8,
                           tip[1] + uy * 6.0 - py * 1.8)], fill=True)
    page.fill_color(INK)
    for x, y, row in lines:
        if row:
            page.text(x, y, row, size, halo=(WHITE, 2.5))
    return box
