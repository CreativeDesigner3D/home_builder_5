"""A small vector PDF writer: lines, circles, Helvetica text and RGB
images, in page points with the origin at the bottom left.

Enough to print a drawing without any third-party package: the base-14
Helvetica fonts need no embedding, and an image goes in as a
Flate-compressed RGB stream.
"""

import math
import zlib

# Helvetica advance widths (1/1000 em), WinAnsi codes 32-126 then 160-255.
_W_ASCII = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333,
    278, 278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278,
    584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278,
    500, 667, 556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944,
    667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556,
    278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500,
    278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584)
_W_LATIN = (
    278, 333, 556, 556, 556, 556, 260, 556, 333, 737, 370, 556, 584, 333,
    737, 333, 400, 584, 333, 333, 333, 556, 537, 278, 333, 333, 365, 556,
    834, 834, 834, 611, 667, 667, 667, 667, 667, 667, 1000, 722, 667, 667,
    667, 667, 278, 278, 278, 278, 722, 722, 778, 778, 778, 778, 778, 584,
    778, 722, 722, 722, 722, 667, 667, 611, 556, 556, 556, 556, 556, 556,
    889, 500, 556, 556, 556, 556, 278, 278, 278, 278, 556, 556, 556, 556,
    556, 556, 556, 584, 611, 556, 556, 556, 556, 500, 556, 500)

REGULAR = 'F1'
BOLD = 'F2'
_FONTS = {REGULAR: 'Helvetica', BOLD: 'Helvetica-Bold'}
_KAPPA = 0.5522847498


def _encode(text):
    return text.encode('cp1252', errors='replace')


def text_width(text, size):
    """Width in points of `text` set in Helvetica at `size` (the bold
    face is close enough for centring)."""
    total = 0
    for c in _encode(text):
        if 32 <= c <= 126:
            total += _W_ASCII[c - 32]
        elif c >= 160:
            total += _W_LATIN[c - 160]
        else:
            total += 556
    return total * size / 1000.0


def _num(v):
    s = f"{v:.3f}".rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def _string(text):
    raw = _encode(text)
    return b'(' + raw.replace(b'\\', b'\\\\').replace(b'(', b'\\(') \
        .replace(b')', b'\\)') + b')'


class Page:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._ops = []
        self._images = []

    def _op(self, *parts):
        self._ops.append(' '.join(parts).encode('ascii'))

    # ---- state -----------------------------------------------------------

    def stroke_color(self, rgb):
        self._op(*(_num(c) for c in rgb[:3]), 'RG')

    def fill_color(self, rgb):
        self._op(*(_num(c) for c in rgb[:3]), 'rg')

    def line_width(self, w):
        self._op(_num(w), 'w')

    def dash(self, on=None, off=None):
        """Dashed strokes from here on, `on` drawn and `off` skipped;
        no arguments for solid again."""
        if on is None:
            self._op('[] 0 d')
        else:
            self._op('[' + _num(on), _num(on if off is None else off) + ']',
                     '0 d')

    # ---- drawing ---------------------------------------------------------

    def lines(self, segments):
        """Stroke [(p, q), ...] segments, each point (x, y)."""
        for p, q in segments:
            self._op(_num(p[0]), _num(p[1]), 'm', _num(q[0]), _num(q[1]),
                     'l')
        if segments:
            self._op('S')

    def rect(self, x, y, w, h, fill=False, stroke=True):
        self._op(_num(x), _num(y), _num(w), _num(h), 're')
        self._op('B' if fill and stroke else 'f' if fill else 'S')

    def polygon(self, points, fill=True, stroke=False):
        if len(points) < 3:
            return
        (x, y), rest = points[0], points[1:]
        self._op(_num(x), _num(y), 'm')
        for x, y in rest:
            self._op(_num(x), _num(y), 'l')
        self._op('h', 'B' if fill and stroke else 'f' if fill else 'S')

    def circle(self, cx, cy, r, fill=False, stroke=True):
        k = r * _KAPPA
        self._op(_num(cx + r), _num(cy), 'm')
        for (x1, y1, x2, y2, x3, y3) in (
                (cx + r, cy + k, cx + k, cy + r, cx, cy + r),
                (cx - k, cy + r, cx - r, cy + k, cx - r, cy),
                (cx - r, cy - k, cx - k, cy - r, cx, cy - r),
                (cx + k, cy - r, cx + r, cy - k, cx + r, cy)):
            self._op(*(_num(v) for v in (x1, y1, x2, y2, x3, y3)), 'c')
        self._op('B' if fill and stroke else 'f' if fill else 'S')

    def text(self, x, y, text, size, angle=0.0, font=REGULAR, halo=None):
        """`text` with its baseline starting at (x, y), turned `angle`
        radians about that point. `halo` (rgb, width) strokes a band
        of that colour under the glyphs first, so the text reads over
        line work."""
        if not text:
            return
        ca, sa = math.cos(angle), math.sin(angle)
        tm = ' '.join(_num(v) for v in (ca, sa, -sa, ca, x, y))
        body = _string(text).decode('latin-1')
        if halo is not None:
            rgb, width = halo
            self._op('q')
            self.stroke_color(rgb)
            self._op(_num(width), 'w', '1 J 1 j')
            self._op('BT', f'/{font}', _num(size), 'Tf', tm, 'Tm',
                     '1 Tr', body, 'Tj', 'ET')
            self._op('Q')
        self._op('BT', f'/{font}', _num(size), 'Tf', tm, 'Tm', '0 Tr',
                 body, 'Tj', 'ET')

    def image(self, rgb, px_w, px_h, x, y, w, h):
        """An RGB image (bytes, top row first, 3 bytes a pixel) drawn
        into the rectangle x, y, w, h."""
        name = f'Im{len(self._images) + 1}'
        self._images.append((name, rgb, px_w, px_h))
        self._op('q', _num(w), '0 0', _num(h), _num(x), _num(y), 'cm',
                 f'/{name}', 'Do', 'Q')

    def push(self):
        self._op('q')

    def pop(self):
        self._op('Q')


class Document:
    def __init__(self):
        self.pages = []

    def add_page(self, width, height):
        page = Page(width, height)
        self.pages.append(page)
        return page

    def save(self, path):
        objs = []                           # bytes of object n+1

        def new(body=b''):
            objs.append(body)
            return len(objs)

        catalog = new()
        pages_id = new()
        font_ids = {}
        for key, base in _FONTS.items():
            font_ids[key] = new(
                f'<< /Type /Font /Subtype /Type1 /BaseFont /{base} '
                f'/Encoding /WinAnsiEncoding >>'.encode('ascii'))
        fonts = ' '.join(f'/{k} {v} 0 R' for k, v in font_ids.items())
        kids = []
        for page in self.pages:
            xobjs = []
            for name, rgb, pw, ph in page._images:
                data = zlib.compress(bytes(rgb), 6)
                head = (f'<< /Type /XObject /Subtype /Image /Width {pw} '
                        f'/Height {ph} /ColorSpace /DeviceRGB '
                        f'/BitsPerComponent 8 /Filter /FlateDecode '
                        f'/Length {len(data)} >>\nstream\n').encode('ascii')
                xobjs.append((name, new(head + data + b'\nendstream')))
            content = zlib.compress(b'\n'.join(page._ops), 6)
            cid = new((f'<< /Length {len(content)} /Filter /FlateDecode >>'
                       f'\nstream\n').encode('ascii') + content
                      + b'\nendstream')
            res = f'/Font << {fonts} >>'
            if xobjs:
                res += ' /XObject << ' + ' '.join(
                    f'/{n} {i} 0 R' for n, i in xobjs) + ' >>'
            kids.append(new(
                (f'<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 '
                 f'{_num(page.width)} {_num(page.height)}] /Resources << '
                 f'{res} >> /Contents {cid} 0 R >>').encode('ascii')))
        objs[catalog - 1] = (f'<< /Type /Catalog /Pages {pages_id} 0 R >>'
                             .encode('ascii'))
        objs[pages_id - 1] = (
            f'<< /Type /Pages /Kids [{" ".join(f"{k} 0 R" for k in kids)}] '
            f'/Count {len(kids)} >>').encode('ascii')

        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += f'{i} 0 obj\n'.encode('ascii') + body + b'\nendobj\n'
        xref = len(out)
        out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n'.encode()
        for off in offsets:
            out += f'{off:010d} 00000 n \n'.encode()
        out += (f'trailer\n<< /Size {len(objs) + 1} /Root {catalog} 0 R >>\n'
                f'startxref\n{xref}\n%%EOF\n').encode('ascii')
        with open(path, 'wb') as fh:
            fh.write(out)
