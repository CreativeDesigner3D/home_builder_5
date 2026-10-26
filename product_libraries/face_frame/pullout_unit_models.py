"""3D models for more pull-out and in-cabinet units, built procedurally.

These extend accessory_models.py with further generic model types. They
follow the same rules: a product entry names the model in ``model`` and
tunes it in ``model_params``; the unit keeps its own product size and
is centered in the opening (sizing keys as in accessory_models); on a
pull-out front the unit rides the front's slide, and as an interior item
it stands in the opening. Local origin is the front-left-bottom of the
unit, x right, y back, z up.

Pull-outs behind a door front:

- trash_pullout:      one or two waste bins on a carrier. ``style``:
                      'wire' (aluminum and wire frame on bottom-mount
                      slides), 'deck' (dovetailed wood deck the bins
                      stand in) or 'top_deck' (a top-mounted deck the
                      bins hang through, on side-mount slides).
                      ``bin`` [width, depth, height] as placed,
                      ``bins`` 1 or 2, ``layout`` 'side' (side by side)
                      or 'tandem' (one behind the other).
- hamper_pullout:     ``style`` 'standard' (wood deck with a polymer
                      hamper and its lid, ``hamper`` [w, d, h]) or
                      'custom' (wood frame with perforated panels).
- vanity_organizer:   shelves with clear rails and small clear bins
                      (``levels``, ``bins``, ``bins_per_level``).
- grooming_organizer: a top shelf with two hanging steel bins, shelves
                      with clear rails below (``shelves``); ``outlet``
                      adds the outlet box.

Units standing in an opening:

- under_sink_l:       L-shaped deck around plumbing with a bin tower
                      (``notch_width``, ``front_depth``, ``bins``).
- under_sink_u:       U-shaped deck with dividers and a lidded waste
                      container (``notch_width``, ``front_depth``).
- under_sink_wire:    U-shaped chrome basket; ``floor`` 'wire' or
                      'solid'.
- hanging_pullout:    a wood channel under the cabinet top with hooks
                      (``hooks``); the unit is drawn at the top of the
                      opening.
- mixer_shelf:        a butcher block shelf on lift mechanisms, shown
                      lowered; the shelf runs ``shelf_inset`` narrower
                      than the opening.
- towel_bar:          a sliding towel bar at the top of one side
                      (``side`` 'left' / 'right', ``bars``).

Material slots: 0 wood, 1 chrome, 2 steel, 3 clear plastic (as for the
other pull-outs), then the EXTRA_MATERIALS keys in order: 4 gray
polymer, 5 white polymer, 6 hardboard, 7 black.
"""

import math

from . import accessory_models as am
from ...units import inch

MI_WOOD = 0
MI_CHROME = 1
MI_STEEL = 2
MI_CLEAR = 3
MI_GRAY = 4
MI_WHITE = 5
MI_HARDBOARD = 6
MI_BLACK = 7

EXTRA_MATERIALS = ('GRAY_PLASTIC', 'WHITE_PLASTIC', 'HARDBOARD',
                   'BLACK_PLASTIC')

T = inch(0.5)                 # deck / panel stock
ROD = inch(0.2)               # wire frame rod


def _p(params, key, default):
    return am._p(params, key, default)


def _box(bm, x0, x1, y0, y1, z0, z1, mi=MI_WOOD):
    am._box(bm, min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1),
            min(z0, z1), max(z0, z1), mi)


def _bar(bm, p0, p1, t=ROD, mi=MI_CHROME):
    """Square rod between two points that differ along one axis."""
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    am._bar(bm, x0, x1, y0, y1, z0, z1, t=t, mi=mi)


def _triple(params, key, default):
    try:
        vals = [float(v) for v in params.get(key, default)]
        if len(vals) == 3:
            return vals
    except (TypeError, ValueError):
        pass
    return list(default)


# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------

def _rrect(cx, cy, w, d, r, seg=3):
    """Rounded rectangle outline (counter-clockwise from above)."""
    w, d = max(w, 1e-4), max(d, 1e-4)
    r = max(min(r, w / 2.0 - 1e-5, d / 2.0 - 1e-5), 1e-5)
    pts = []
    corners = ((cx + w / 2 - r, cy - d / 2 + r, -90.0),
               (cx + w / 2 - r, cy + d / 2 - r, 0.0),
               (cx - w / 2 + r, cy + d / 2 - r, 90.0),
               (cx - w / 2 + r, cy - d / 2 + r, 180.0))
    for ccx, ccy, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def _loft(bm, cx, cy, rings, r, mi, seg=3):
    """Closed shell through rounded-rectangle rings (w, d, z), capped at
    the first and last ring. Rings run outside-in for a hollow tub."""
    loops = []
    for w, d, z in rings:
        rr = max(min(r, w / 2.0, d / 2.0) - 1e-4, 1e-4)
        loops.append([bm.verts.new((x, y, z))
                      for x, y in _rrect(cx, cy, w, d, rr, seg)])
    if len(loops) < 2:
        return
    bm.faces.new(list(reversed(loops[0]))).material_index = mi
    bm.faces.new(loops[-1]).material_index = mi
    n = len(loops[0])
    for a, b in zip(loops, loops[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i])).material_index = mi


def _tub(bm, cx, cy, z0, w, d, h, mi, taper=inch(0.6), r=inch(1.0),
         wall=inch(0.12), lip=inch(0.18), seg=3):
    """Open-top container: tapered walls, a rolled lip and an inner
    floor. (w, d) is the top size; the bottom is ``taper`` smaller."""
    if w <= 4 * wall or d <= 4 * wall or h <= 4 * wall:
        return
    wb, db = max(w - taper, w * 0.5), max(d - taper, d * 0.5)
    zt = z0 + h
    lh = min(inch(0.5), h * 0.08)
    rings = [(wb, db, z0),
             (w, d, zt - lh),
             (w + 2 * lip, d + 2 * lip, zt - lh * 0.6),
             (w + 2 * lip, d + 2 * lip, zt),
             (w - 2 * wall, d - 2 * wall, zt),
             (wb - 2 * wall, db - 2 * wall, z0 + wall)]
    _loft(bm, cx, cy, rings, r, mi, seg)


def _closed_tub(bm, cx, cy, z0, w, d, h, mi, taper=inch(0.5), r=inch(1.0),
                seg=3):
    """Solid tapered container (for one under a lid)."""
    wb, db = max(w - taper, w * 0.5), max(d - taper, d * 0.5)
    _loft(bm, cx, cy, [(wb, db, z0), (w, d, z0 + h)], r, mi, seg)


def _wall(bm, p, q, t, z0, z1, mi=MI_WOOD):
    """Panel standing on the left (inner, for a counter-clockwise
    outline) side of the axis-aligned edge p -> q."""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) > 1e-6:
        side = t if dx > 0 else -t
        _box(bm, x0, x1, y0, y0 + side, z0, z1, mi)
    elif abs(dy) > 1e-6:
        side = -t if dy > 0 else t
        _box(bm, x0, x0 + side, y0, y1, z0, z1, mi)


def _perforate(bm, a0, a1, b0, b1, plane, at, pitch=inch(1.0),
               size=inch(0.25), mi=MI_BLACK, sign=1.0):
    """Dots (single quads) on a panel face: plane 'X' puts them at x=at
    over (y, z) = (a, b); 'Y' at y=at over (x, z)."""
    na = int((a1 - a0) / pitch)
    nb = int((b1 - b0) / pitch)
    if na < 1 or nb < 1:
        return
    oa = a0 + ((a1 - a0) - (na - 1) * pitch) / 2.0
    ob = b0 + ((b1 - b0) - (nb - 1) * pitch) / 2.0
    s = size / 2.0
    off = inch(0.01) * sign
    for i in range(na):
        for j in range(nb):
            a, b = oa + i * pitch, ob + j * pitch
            if plane == 'X':
                pts = [(at + off, a - s, b - s), (at + off, a + s, b - s),
                       (at + off, a + s, b + s), (at + off, a - s, b + s)]
            else:
                pts = [(a - s, at + off, b - s), (a + s, at + off, b - s),
                       (a + s, at + off, b + s), (a - s, at + off, b + s)]
            bm.faces.new([bm.verts.new(v) for v in pts]).material_index = mi


def _lay_out(x0, x1, y0, y1, size, count, layout, gap=inch(0.5)):
    """Footprints (cx, cy, w, d) for ``count`` containers of ``size``
    (w, d) set side by side or one behind the other, centered in the
    area and shrunk to fit."""
    bw, bd = size
    aw, ad = x1 - x0, y1 - y0
    count = max(1, count)
    if layout == 'tandem':
        bw = min(bw, aw)
        bd = min(bd, (ad - gap * (count - 1)) / count)
        span = bd * count + gap * (count - 1)
        cy0 = y0 + (ad - span) / 2.0 + bd / 2.0
        return [((x0 + x1) / 2.0, cy0 + i * (bd + gap), bw, bd)
                for i in range(count)]
    bd = min(bd, ad)
    bw = min(bw, (aw - gap * (count - 1)) / count)
    span = bw * count + gap * (count - 1)
    cx0 = x0 + (aw - span) / 2.0 + bw / 2.0
    return [(cx0 + i * (bw + gap), (y0 + y1) / 2.0, bw, bd)
            for i in range(count)]


def _slides(bm, w, d, z1=inch(1.0), sw=inch(0.6)):
    """Bottom-mount slide members under each side."""
    for x in (0.0, w - sw):
        _box(bm, x, x + sw, inch(0.5), d, inch(0.2), z1, MI_STEEL)


def _deck_box(bm, w, d, side_h, front_h, floor_z=inch(0.75)):
    """Dovetailed wood deck: floor, sides and back at ``side_h``, the
    front (the door mounts to it) at ``front_h``. Returns the inside
    (x0, x1, y0, y1, floor_top)."""
    _slides(bm, w, d, z1=floor_z)
    _box(bm, 0.0, w, 0.0, d, floor_z, floor_z + T)
    top = floor_z + side_h
    _box(bm, 0.0, w, 0.0, T, floor_z, floor_z + front_h)
    _box(bm, 0.0, w, d - T, d, floor_z + T, top)
    _box(bm, 0.0, T, T, d - T, floor_z + T, top)
    _box(bm, w - T, w, T, d - T, floor_z + T, top)
    # Door brackets on the face of the front.
    for x in (inch(0.75), w - inch(1.75)):
        _box(bm, x, x + inch(1.0), -inch(0.12), 0.0,
             floor_z + front_h * 0.25, floor_z + front_h * 0.85, MI_STEEL)
    return T, w - T, T, d - T, floor_z + T


# ---------------------------------------------------------------------------
# Trash pull-outs
# ---------------------------------------------------------------------------

def _wire_frame(bm, x0, x1, y0, y1, z0, height, posts=True):
    """Chrome wire cradle: rectangles at the bottom and top, uprights
    at the corners and along the sides."""
    zt = z0 + height
    for z in (z0, zt) if height > ROD else (z0,):
        _bar(bm, (x0, y0, z), (x1, y0, z))
        _bar(bm, (x0, y1, z), (x1, y1, z))
        _bar(bm, (x0, y0, z), (x0, y1, z))
        _bar(bm, (x1, y0, z), (x1, y1, z))
    if not posts or height <= ROD:
        return
    n = max(2, int((y1 - y0) / inch(1.5)) + 1)
    for x in (x0, x1):
        for i in range(n):
            y = y0 + (y1 - y0) * i / (n - 1)
            _bar(bm, (x, y, z0), (x, y, zt))
    m = max(2, int((x1 - x0) / inch(1.5)) + 1)
    for i in range(1, m - 1):
        x = x0 + (x1 - x0) * i / (m - 1)
        _bar(bm, (x, y1, z0), (x, y1, zt))


def _build_trash_pullout(bm, w, d, h, params):
    style = params.get('style', 'deck')
    count = max(1, int(_p(params, 'bins', 1)))
    layout = params.get('layout', 'side')
    bw, bd, bh = (inch(v) for v in _triple(params, 'bin',
                                            (9.5, 14.0, 18.0)))
    if style == 'wire':
        # Aluminum and wire frame on bottom-mount slides.
        _slides(bm, w, d, z1=inch(1.1), sw=inch(0.7))
        x0, x1 = inch(0.35), w - inch(0.35)
        y0, y1 = inch(0.6), d - inch(0.4)
        base = inch(1.3)
        for x in (x0, x1):
            _box(bm, x - inch(0.35), x + inch(0.35), y0, y1, inch(1.1),
                 base, MI_STEEL)
        n = max(2, int((y1 - y0) / inch(2.0)) + 1)
        for i in range(n):
            y = y0 + (y1 - y0) * i / (n - 1)
            _bar(bm, (x0, y, base), (x1, y, base))
        _wire_frame(bm, x0, x1, y0, y1, base, min(h * 0.45, bh * 0.55))
        # Door mount uprights at the front.
        for x in (x0, x1 - inch(0.75)):
            _box(bm, x, x + inch(0.75), 0.0, inch(0.6), inch(1.1),
                 min(h, base + bh * 0.8), MI_STEEL)
        floor = base + ROD / 2
        spots = _lay_out(x0 + inch(0.3), x1 - inch(0.3), y0 + inch(0.3),
                         y1 - inch(0.3), (bw, bd), count, layout)
        for cx, cy, sw, sd in spots:
            _tub(bm, cx, cy, floor, sw, sd, min(bh, h - floor), MI_GRAY)
        return True
    if style == 'top_deck':
        # Deck at the top on side-mount slides; the bins hang through.
        sl = inch(0.5)
        dt = inch(0.75)
        top = h - dt
        for x in (0.0, w - sl):
            _box(bm, x, x + sl, inch(0.75), d, top - inch(1.5), top + inch(0.25),
                 MI_STEEL)
        x0, x1 = sl, w - sl
        _box(bm, x0, x1, 0.0, T, 0.0, h)                       # front
        _box(bm, x0, x1, d - T, d, top - inch(3.0), top)        # back rail
        spots = _lay_out(x0 + inch(0.5), x1 - inch(0.5), T + inch(0.5),
                         d - T - inch(0.5), (bw, bd), count, layout)
        holes = [(cx - sw / 2, cx + sw / 2, cy - sd / 2, cy + sd / 2)
                 for cx, cy, sw, sd in spots]
        am._shelf_with_holes(bm, x0, x1, T, d, top, holes, t=dt)
        for cx, cy, sw, sd in spots:
            hh = min(bh, h - inch(0.5))
            _tub(bm, cx, cy, h + inch(0.1) - hh, sw, sd, hh, MI_GRAY)
        return True
    # 'deck': the bins stand in a dovetailed wood deck.
    side_h = min(inch(5.0), h * 0.3)
    front_h = min(inch(8.0), h * 0.45)
    x0, x1, y0, y1, floor = _deck_box(bm, w, d, side_h, front_h)
    spots = _lay_out(x0 + inch(0.25), x1 - inch(0.25), y0 + inch(0.25),
                     y1 - inch(0.25), (bw, bd), count, layout)
    for cx, cy, sw, sd in spots:
        _tub(bm, cx, cy, floor, sw, sd, min(bh, h - floor), MI_GRAY)
    return True


# ---------------------------------------------------------------------------
# Hampers
# ---------------------------------------------------------------------------

def _build_hamper_pullout(bm, w, d, h, params):
    if params.get('style') == 'custom':
        # Wood frame with perforated hardboard panels, open at the top.
        _slides(bm, w, d, z1=inch(0.75))
        z0 = inch(0.75)
        post = inch(0.75)
        ht = inch(0.25)
        _box(bm, 0.0, w, 0.0, d, z0, z0 + T)                   # floor
        _box(bm, 0.0, w, 0.0, T, z0, h)                        # front
        for x in (0.0, w - post):
            for y in (T, d - post):
                _box(bm, x, x + post, y, y + post, z0, h)
        for z in (z0 + T, h - post):
            _box(bm, 0.0, post, T, d, z, z + post)
            _box(bm, w - post, w, T, d, z, z + post)
            _box(bm, post, w - post, d - post, d, z, z + post)
        pz0, pz1 = z0 + T + post, h - post
        # Panels set in the frame, dots on their outer faces.
        _box(bm, 0.0, ht, T + post, d - post, pz0, pz1, MI_HARDBOARD)
        _box(bm, w - ht, w, T + post, d - post, pz0, pz1, MI_HARDBOARD)
        _box(bm, post, w - post, d - ht, d, pz0, pz1, MI_HARDBOARD)
        _perforate(bm, T + post, d - post, pz0, pz1, 'X', 0.0, sign=-1.0)
        _perforate(bm, T + post, d - post, pz0, pz1, 'X', w)
        _perforate(bm, post, w - post, pz0, pz1, 'Y', d)
        return True
    # Standard: a white polymer hamper with its lid on a wood deck.
    side_h = min(inch(4.0), h * 0.25)
    front_h = min(inch(7.0), h * 0.4)
    x0, x1, y0, y1, floor = _deck_box(bm, w, d, side_h, front_h)
    hw, hd, hh = (inch(v) for v in _triple(params, 'hamper',
                                            (12.0, 15.0, 18.0)))
    hw, hd = min(hw, x1 - x0 - inch(0.5)), min(hd, y1 - y0 - inch(0.5))
    lid_t = inch(0.6)
    hh = min(hh, h - floor - inch(0.25))
    if hh <= inch(2.0):
        return True
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    _tub(bm, cx, cy, floor, hw, hd, hh, MI_WHITE, taper=inch(0.8),
         r=inch(1.5), wall=inch(0.15), lip=inch(0.25))
    # Vent slots down each side.
    zt = floor + hh
    for i in range(6):
        z = floor + hh * 0.3 + i * hh * 0.08
        for sx in (-1.0, 1.0):
            x = cx + sx * (hw / 2.0 - inch(0.4) * (1.0 - (z - floor) / hh))
            _box(bm, x - inch(0.03) * sx, x + inch(0.03) * sx,
                 cy - hd * 0.3, cy + hd * 0.3, z, z + inch(0.35), MI_BLACK)
    # Lid hinged at the back, standing open and leaning back a little.
    lean = inch(1.5)
    yb = cy + hd / 2.0 + inch(0.25)
    lid_h = min(hd, h - zt + hd)
    lid_top = min(zt + lid_h, h)
    run = lid_top - zt
    if run > inch(1.0):
        lean = min(lean, run * 0.3)
        prof = [(yb, zt), (yb + lid_t, zt), (yb + lid_t + lean, lid_top),
                (yb + lean, lid_top)]
        if yb + lid_t + lean <= d:
            am._prism(bm, prof, 'X', cx - hw / 2.0 - inch(0.2),
                      cx + hw / 2.0 + inch(0.2), MI_WHITE)
            # Handle slot near the top of the lid.
            _box(bm, cx - hw * 0.25, cx + hw * 0.25, yb - inch(0.02),
                 yb + lean * 0.9, lid_top - run * 0.2,
                 lid_top - run * 0.2 + inch(0.6), MI_BLACK)
    return True


# ---------------------------------------------------------------------------
# Vanity and grooming organizers
# ---------------------------------------------------------------------------

def _clear_rails(bm, x0, x1, y0, y1, z, height=inch(2.0)):
    """Clear rail along each open side of a shelf."""
    if height <= inch(0.25):
        return
    t = inch(0.15)
    for x in (x0, x1 - t):
        _box(bm, x, x + t, y0 + inch(0.25), y1 - inch(0.25), z, z + height,
             MI_CLEAR)


def _build_vanity_organizer(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = am._chassis(bm, w, d, h, top_rails=False)
    levels = max(1, int(_p(params, 'levels', 3)))
    bins = int(_p(params, 'bins', 6))
    per = max(1, int(_p(params, 'bins_per_level', 2)))
    pitch = (top - floor) / levels
    zs = [floor] + [floor + pitch * i for i in range(1, levels)]
    for z in zs[1:]:
        _box(bm, x0, x1, y0, y1, z - T, z)
    bw, bd, bh = inch(7.0), inch(4.75), inch(2.25)
    bw = min(bw, x1 - x0 - inch(0.4))
    # Bins fill the top levels first.
    left = bins
    for z in reversed(zs):
        _clear_rails(bm, x0, x1, y0, y1, z, min(inch(2.0), pitch * 0.4))
        n = min(per, left)
        if n <= 0 or bh > pitch - inch(0.5):
            continue
        left -= n
        span = (y1 - y0) / per
        for i in range(n):
            cy = y0 + span * (i + 0.5)
            _tub(bm, (x0 + x1) / 2.0, cy, z, bw, min(bd, span - inch(0.3)),
                 bh, MI_CLEAR, taper=inch(0.2), r=inch(0.4),
                 wall=inch(0.08), lip=inch(0.06))
    return True


def _build_grooming_organizer(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = am._chassis(bm, w, d, h, top_rails=False)
    outlet = bool(params.get('outlet'))
    shelf_z = top - inch(1.5)
    n = int(_p(params, 'shelves', 1))
    # Two round steel bins hanging through the top shelf, at the front.
    dia = min(inch(4.0), x1 - x0 - inch(0.6))
    bin_h = min(inch(6.0), shelf_z - floor - inch(2.0))
    holes, cups = [], []
    for i in range(2):
        cy = y0 + inch(0.5) + dia / 2.0 + i * (dia + inch(0.5))
        cx = (x0 + x1) / 2.0
        holes.append((cx - dia / 2, cx + dia / 2, cy - dia / 2, cy + dia / 2))
        cups.append((cx, cy))
    am._shelf_with_holes(bm, x0, x1, y0, y1, shelf_z - T, holes)
    for cx, cy in cups:
        if bin_h > inch(1.0):
            _tub(bm, cx, cy, shelf_z + inch(0.1) - bin_h, dia, dia, bin_h,
                 MI_STEEL, taper=inch(0.3), r=dia / 2.0, wall=inch(0.06),
                 lip=inch(0.12), seg=4)
    _clear_rails(bm, x0, x1, y0, y1, shelf_z, min(inch(2.0), h - shelf_z))
    if outlet:
        # Outlet box at the back of the top shelf.
        oy1 = y1 - inch(0.1)
        oy0 = oy1 - inch(2.6)
        ox0, ox1 = x0 + inch(0.4), x1 - inch(0.4)
        _box(bm, ox0, ox1, oy0, oy1, shelf_z, min(h, shelf_z + inch(4.2)),
             MI_WHITE)
        for k in range(2):
            z = shelf_z + inch(1.1) + k * inch(1.6)
            if z + inch(0.9) < h:
                _box(bm, (ox0 + ox1) / 2 - inch(0.6), (ox0 + ox1) / 2 + inch(0.6),
                     oy0 - inch(0.03), oy0, z, z + inch(0.9), MI_BLACK)
    under = shelf_z - T - bin_h - inch(0.5)
    levels = am._even_levels(floor, under, n) if n > 0 else []
    for z in levels:
        _box(bm, x0, x1, y0, y1, z, z + T)
    for i, z in enumerate([floor] + [z + T for z in levels]):
        nxt = levels[i] if i < len(levels) else shelf_z - T
        _clear_rails(bm, x0, x1, y0, y1, z, min(inch(2.0), nxt - z - inch(0.5)))
    return True


# ---------------------------------------------------------------------------
# Under-sink units
# ---------------------------------------------------------------------------

def _outline_walls(bm, outline, t, z0, z1, mi=MI_WOOD):
    for p, q in zip(outline, outline[1:] + outline[:1]):
        _wall(bm, p, q, t, z0, z1, mi)


def _build_under_sink_l(bm, w, d, h, params):
    nw = min(inch(_p(params, 'notch_width', 4.375)), w * 0.6)
    fd = min(inch(_p(params, 'front_depth', 6.875)), d * 0.5)
    fz = inch(0.75)
    _slides(bm, w, d, z1=fz)
    _box(bm, 0.0, w, 0.0, fd, fz, fz + T)
    _box(bm, nw, w, fd, d, fz, fz + T)
    floor = fz + T
    wall_h = min(inch(2.5), h - floor)
    outline = [(0.0, 0.0), (w, 0.0), (w, d), (nw, d), (nw, fd), (0.0, fd)]
    _outline_walls(bm, outline, T, floor, floor + wall_h)
    _box(bm, 0.0, w, -inch(0.0), T, floor, min(h, floor + inch(4.5)))
    # Bin tower over the back of the strip, open toward the plumbing.
    tx0, tx1 = nw, w
    ty0, ty1 = max(fd, d - inch(12.0)), d
    ttop = h
    if ttop - floor > inch(4.0) and tx1 - tx0 > inch(2.0):
        _box(bm, tx1 - T, tx1, ty0, ty1, floor, ttop)
        _box(bm, tx0, tx1, ty1 - T, ty1, floor, ttop)
        _box(bm, tx0, tx1, ty0, ty0 + T, floor, ttop)
        _box(bm, tx0, tx1, ty0, ty1, ttop - T, ttop)
        levels = 3
        pitch = (ttop - T - floor) / levels
        bins = int(_p(params, 'bins', 6))
        per = max(1, int(math.ceil(bins / float(levels))))
        for k in range(levels):
            z = floor + k * pitch
            if k:
                _box(bm, tx0, tx1 - T, ty0 + T, ty1 - T, z - T * 0.5, z)
            n = min(per, bins - k * per)
            span = (ty1 - ty0 - 2 * T) / per
            for i in range(max(n, 0)):
                cy = ty0 + T + span * (i + 0.5)
                _tub(bm, (tx0 + tx1 - T) / 2.0, cy, z,
                     tx1 - tx0 - T - inch(0.3), span - inch(0.3),
                     min(pitch - inch(0.6), inch(3.5)), MI_CLEAR,
                     taper=inch(0.2), r=inch(0.3), wall=inch(0.08),
                     lip=inch(0.05))
    return True


def _build_under_sink_u(bm, w, d, h, params):
    nwid = min(inch(_p(params, 'notch_width', 11.0)), w * 0.5)
    fd = min(inch(_p(params, 'front_depth', 6.875)), d * 0.5)
    nx0, nx1 = (w - nwid) / 2.0, (w + nwid) / 2.0
    fz = inch(0.75)
    _slides(bm, w, d, z1=fz)
    _box(bm, 0.0, w, 0.0, fd, fz, fz + T)
    _box(bm, 0.0, nx0, fd, d, fz, fz + T)
    _box(bm, nx1, w, fd, d, fz, fz + T)
    floor = fz + T
    wall_h = min(inch(3.0), h - floor)
    outline = [(0.0, 0.0), (w, 0.0), (w, d), (nx1, d), (nx1, fd),
               (nx0, fd), (nx0, d), (0.0, d)]
    _outline_walls(bm, outline, T, floor, floor + wall_h)
    # Dividers: across the left arm, and one in the front section.
    dt = inch(0.25)
    dh = wall_h - inch(0.5)
    for y in (fd + (d - fd) * 0.33, fd + (d - fd) * 0.66):
        _box(bm, T, nx0 - T, y - dt / 2, y + dt / 2, floor, floor + dh)
    for x in (nx0, nx1):
        _box(bm, x - dt / 2, x + dt / 2, T, fd, floor, floor + dh)
    _box(bm, T, nx0 - T, fd - dt / 2, fd + dt / 2, floor, floor + dh)
    # Lidded waste container on the right arm.
    cw = min(inch(7.5), w - nx1 - 2 * T - inch(0.3))
    cd = min(inch(9.0), d - fd - T - inch(0.3))
    ch = min(inch(10.0), h - floor - inch(0.8))
    if cw > inch(2.0) and cd > inch(2.0) and ch > inch(2.0):
        cx = (nx1 + w) / 2.0
        cy = d - T - inch(0.2) - cd / 2.0
        _closed_tub(bm, cx, cy, floor, cw, cd, ch, MI_STEEL, r=inch(1.0))
        _closed_tub(bm, cx, cy, floor + ch, cw + inch(0.3), cd + inch(0.3),
                    inch(0.6), MI_STEEL, taper=0.0, r=inch(1.1))
    return True


def _build_under_sink_wire(bm, w, d, h, params):
    nwid = min(inch(_p(params, 'notch_width', 12.0)), w * 0.5)
    nd = min(inch(_p(params, 'notch_depth', 11.0)), d * 0.6)
    nx0, nx1 = (w - nwid) / 2.0, (w + nwid) / 2.0
    fd = d - nd
    _slides(bm, w, d, z1=inch(0.8))
    z0 = inch(1.0)
    zt = h - ROD
    outline = [(0.0, 0.0), (w, 0.0), (w, d), (nx1, d), (nx1, fd),
               (nx0, fd), (nx0, d), (0.0, d)]
    for z in (z0, z0 + (zt - z0) * 0.5, zt):
        for p, q in zip(outline, outline[1:] + outline[:1]):
            _bar(bm, (p[0], p[1], z), (q[0], q[1], z))
    # Uprights along every edge.
    for p, q in zip(outline, outline[1:] + outline[:1]):
        length = abs(q[0] - p[0]) + abs(q[1] - p[1])
        n = max(2, int(length / inch(2.0)) + 1)
        for i in range(n - 1):
            f = i / float(n - 1)
            x, y = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
            _bar(bm, (x, y, z0), (x, y, zt))
    rects = [(0.0, w, 0.0, fd), (0.0, nx0, fd, d), (nx1, w, fd, d)]
    if params.get('floor') == 'solid':
        for x0, x1, y0, y1 in rects:
            _box(bm, x0 + ROD, x1 - ROD, y0 + ROD, y1 - ROD, z0 - inch(0.1),
                 z0 + inch(0.15), MI_GRAY)
    else:
        for x0, x1, y0, y1 in rects:
            n = max(2, int((x1 - x0) / inch(1.0)) + 1)
            for i in range(n):
                x = x0 + (x1 - x0) * i / (n - 1)
                _bar(bm, (x, y0, z0), (x, y1, z0), t=inch(0.12))
    return True


# ---------------------------------------------------------------------------
# Other units
# ---------------------------------------------------------------------------

def _build_hanging_pullout(bm, w, d, h, params):
    ch = min(inch(_p(params, 'channel_height', 5.125)), h)
    z0 = h - ch
    t = inch(0.5)
    _box(bm, 0.0, w, 0.0, d, h - t, h)                         # top
    _box(bm, 0.0, t, 0.0, d, z0, h - t)                        # sides
    _box(bm, w - t, w, 0.0, d, z0, h - t)
    _box(bm, t, w - t, 0.0, t, z0, h - t)                      # front cap
    _box(bm, t, w - t, d - t, d, z0, h - t)                    # back cap
    _box(bm, w / 2 - inch(0.6), w / 2 + inch(0.6), t, d - t,
         h - t - inch(0.5), h - t, MI_STEEL)                   # slide
    # Hooks hanging from a rod along the channel.
    rz = z0 + inch(1.0)
    cx = w / 2.0
    _bar(bm, (cx, t, rz), (cx, d - t, rz), t=inch(0.3), mi=MI_STEEL)
    hooks = max(1, int(_p(params, 'hooks', 7)))
    hl = min(inch(4.0), z0 + inch(0.5))
    ht = inch(0.25)
    for y in am._spread(t + inch(1.0), d - t - inch(1.0), hooks):
        zb = rz - hl
        _bar(bm, (cx, y, rz), (cx, y, zb), t=ht)
        _bar(bm, (cx, y - inch(1.0), zb), (cx, y, zb), t=ht)
        _bar(bm, (cx, y - inch(1.0), zb), (cx, y - inch(1.0), zb + inch(1.2)),
             t=ht)
    return True


def _build_mixer_shelf(bm, w, d, h, params):
    inset = inch(_p(params, 'shelf_inset', 3.0))
    st = inch(1.5)
    sx0, sx1 = inset / 2.0, w - inset / 2.0
    if sx1 - sx0 < inch(2.0):
        sx0, sx1 = 0.0, w
    sz = min(inch(_p(params, 'stored_height', 2.5)), max(h - st, 0.0))
    sy0, sy1 = inch(0.25), d - inch(0.5)
    _box(bm, sx0, sx1, sy0, sy1, sz, sz + st)
    # Lift mechanism on each side: a plate on the cabinet side and two
    # arms down to a bracket under the shelf edge.
    pt = inch(0.5)
    py0, py1 = d * 0.4, d - inch(1.5)
    pz1 = min(h, sz + inch(9.0))
    for x0, x1, bx0, bx1 in ((0.0, pt, sx0, sx0 + inch(0.25)),
                             (w - pt, w, sx1 - inch(0.25), sx1)):
        _box(bm, x0, x1, py0, py1, inch(0.75), pz1, MI_STEEL)
        _box(bm, min(x1, bx0), max(x0, bx1), sy0 + inch(1.0), sy1 - inch(1.0),
             sz - inch(0.6), sz, MI_STEEL)
        ax0, ax1 = (x1, sx0) if x0 == 0.0 else (sx1, x0)
        if ax1 - ax0 < inch(0.3):
            ax0, ax1 = (x1, x1 + inch(0.3)) if x0 == 0.0 else (x0 - inch(0.3), x0)
        for ya, za, yb in ((py0 + inch(1.5), pz1 - inch(2.0), d * 0.15),
                           (py0 + inch(5.5), pz1 - inch(4.5), d * 0.45)):
            zb = sz - inch(0.3)
            a = inch(0.6)
            prof = [(yb, zb - a / 2), (ya, za - a / 2), (ya, za + a / 2),
                    (yb, zb + a / 2)]
            am._prism(bm, prof, 'X', ax0, ax1, MI_STEEL)
    return True


def _build_towel_bar(bm, w, d, h, params):
    right = params.get('side', 'right') != 'left'
    mt = inch(0.6)
    xm0, xm1 = (w - mt, w) if right else (0.0, mt)
    z1 = h - inch(0.75)
    z0 = z1 - inch(1.5)
    _box(bm, xm0, xm1, inch(1.0), d, z0, z1, MI_STEEL)          # rail
    n = max(1, int(_p(params, 'bars', 3)))
    pitch = inch(0.9)
    zc = (z0 + z1) / 2.0
    # Carriage at the back, bars running forward to a front loop.
    sgn = -1.0 if right else 1.0
    xs = [(xm0 if right else xm1) + sgn * (inch(0.6) + i * pitch)
          for i in range(n)]
    cy0, cy1 = d - inch(3.0), d - inch(1.0)
    _box(bm, min(xs + [xm0]) - inch(0.3) if right else xm1,
         xm0 if right else max(xs) + inch(0.3), cy0, cy1,
         zc - inch(0.5), zc + inch(0.5), MI_CHROME)
    fy = inch(1.0)
    for x in xs:
        _bar(bm, (x, fy, zc), (x, cy0, zc), t=inch(0.3))
    _bar(bm, (min(xs), fy, zc), (max(xs), fy, zc), t=inch(0.3))
    return True


BUILDERS = {
    'trash_pullout':      _build_trash_pullout,
    'hamper_pullout':     _build_hamper_pullout,
    'vanity_organizer':   _build_vanity_organizer,
    'grooming_organizer': _build_grooming_organizer,
    'under_sink_l':       _build_under_sink_l,
    'under_sink_u':       _build_under_sink_u,
    'under_sink_wire':    _build_under_sink_wire,
    'hanging_pullout':    _build_hanging_pullout,
    'mixer_shelf':        _build_mixer_shelf,
    'towel_bar':          _build_towel_bar,
}
MODELS = frozenset(BUILDERS)
