"""3D models for accessory products placed in an opening interior.

An ACCESSORY interior item is data first: its code drives the legend
and the reports, and the opening shows a text label. When the product
entry the host application publishes for that code (through
accessory_registry) carries a ``model`` name, the opening also gets a
readable 3D model of the unit, built here from generic model types:

- rollout_tray_pegs:      a roll-out tray, low at the front and tall at
                          the back, with wire U pegs standing in the
                          front half and wire lid dividers in the back.
- rollout_two_tier:       a deep lower tray plus a shallower upper tier
                          riding over its back half; wire lid / pot
                          racks on the lower floor, wood dish pegs on
                          the upper one.
- organizer_cubbies:      an open plywood box the width of the opening
                          with a centered section split by a shelf into
                          a paper bay below and slots above.
- organizer_letter_slots: a low plywood box with a centered paper bay
                          (finger-notched shelf) and equal letter slots
                          out to each side.

Pull-out units, a chassis on bottom-mount slides with full-height
front and back panels (the door mounts to the front panel), open to
each side:

- can_storage_wood:       railed shelves (``shelves``; ``swivel`` adds a
                          turntable hub under each).
- can_storage_wire:       wire baskets on a light frame (``baskets``;
                          ``deluxe`` gives each a wood floor).
- utensil_pullout:        steel bins hanging through a top shelf plus
                          railed shelves below (``bins``, ``shelves``).
- knife_pullout:          bins and knife inserts under a top shelf.
- towel_pullout:          a towel bay over a shelf, storage behind it.
- canister_pullout:       canisters on the deck and on a shelf.
- tray_divider_pullout:   upright tray dividers (``dividers``).
- spice_pullout:          shallow rack, fixed shelves with wood rails or
                          adjustable shelves with chrome rails.
- wire_pantry:            steel frame with wire baskets (``baskets`` or
                          ``basket_steps`` by unit height).

A pull-out keeps its own product size and is centered in the opening,
never stretched to fill it: ``unit_width`` or ``sizes`` ([unit width,
minimum opening width] pairs, the largest that fits is used) or
``fit_width`` ([clearance, min, max] for a made-to-fit unit);
``unit_height`` or ``heights`` (pairs, as for widths) or
``height_range`` ([low, high]: the unit telescopes to the opening) or
``fill_height``; ``unit_depth``. Anything larger than the opening is
clipped. On a pull-out front the unit rides the front's slide.

The entry's optional ``model_params`` dict tunes a model (sizes in
inches): unit_width / unit_height, peg_count / divider_count,
lid_organizers / pot_organizers / dish_pegs, center_width, slot_min /
slot_max. Unknown model names leave the item label-only.

Each model is ONE derived mesh per item (like bar_storage.py): local
origin at the front-left-bottom of the unit, x right, y back, z up. The
interior recalc parents it to the opening and the standard interior
wipe rebuilds it every recalc. It is not a CABINET_PART: a purchased
unit, so cut lists and machining leave it alone. Material slot 0 is the
wood (roll-outs carry their own natural maple; organizers are stamped to
take the exterior finish in the material walk), slot 1 is chrome wire.
"""

import math

import bpy
import bmesh

from ... import hb_utils
from . import accessory_materials
from ...units import inch

ROLE = 'ACCESSORY_MODEL'
# Object flag read by the material walk: slot 0 takes the cabinet's
# exterior finish (otherwise the model keeps its own wood).
FINISH_MATCH_KEY = 'hb_accessory_finish_match'
INTERIOR_HOST = 'opening_interior_accessory'

ROLLOUT_MODELS = frozenset({'rollout_tray_pegs', 'rollout_two_tier'})
ORGANIZER_MODELS = frozenset({'organizer_cubbies', 'organizer_letter_slots'})
PULLOUT_MODELS = frozenset({
    'can_storage_wood', 'can_storage_wire', 'utensil_pullout',
    'knife_pullout', 'towel_pullout', 'canister_pullout',
    'tray_divider_pullout', 'spice_pullout', 'wire_pantry'})
MODELS = ROLLOUT_MODELS | ORGANIZER_MODELS | PULLOUT_MODELS

# Roll-outs: the unit rides side-mounted slides, so it runs this much
# narrower than the opening on each side, and stops short of the cavity
# back at a full-extension slide's length.
ROLLOUT_SLIDE_CLEARANCE = inch(0.75)
ROLLOUT_MAX_DEPTH = inch(21.0)
ROLLOUT_DEFAULT_WIDTH = inch(14.5)
ROLLOUT_DEFAULT_HEIGHT = inch(17.5)
ORGANIZER_DEFAULT_HEIGHT = inch(12.0)

WOOD_T = inch(0.5)          # tray / organizer panel stock
TRIM_T = inch(0.25)         # organizer front moulding (1/4" x 3/4")
TRIM_W = inch(0.75)
WIRE = inch(0.1875)         # square section standing in for chrome rod

_MAT_MAPLE = ('Accessory Maple', (0.86, 0.72, 0.52, 1.0), 0.0, 0.5)
_MAT_PLY = ('Accessory Plywood', (0.80, 0.66, 0.47, 1.0), 0.0, 0.6)
_MAT_CHROME = ('Accessory Chrome', (0.72, 0.74, 0.77, 1.0), 0.9, 0.2)
_MAT_STEEL = ('Accessory Steel', (0.45, 0.46, 0.48, 1.0), 0.3, 0.45)
_MAT_PLASTIC = ('Accessory Clear Plastic', (0.82, 0.88, 0.92, 1.0), 0.0, 0.15)

# Pull-out material slots (slot 0 wood and 1 chrome as above).
MI_STEEL = 2      # slides, steel frames, knife inserts
MI_PLASTIC = 3    # canisters

PULLOUT_DEFAULT_DEPTH = 21.6     # inches: a 24" deep base cabinet's unit
PULLOUT_DEFAULT_HEIGHT = 26.0
PULLOUT_REAR_CLEARANCE = inch(0.25)
RAIL = inch(0.15)                # chrome side rail rod


# ---------------------------------------------------------------------------
# Product lookup
# ---------------------------------------------------------------------------

def model_for(code):
    """(model, params) named by the product entry for ``code``, or None
    when the entry has no model this module knows."""
    if not code:
        return None
    from ... import accessory_registry
    entry = (accessory_registry.lookup(INTERIOR_HOST, code)
             or accessory_registry.find(code))
    if not entry:
        return None
    model = entry.get('model')
    if model not in MODELS:
        return None
    params = entry.get('model_params') or {}
    if not isinstance(params, dict):
        params = {}
    return model, params


def _p(params, key, default):
    try:
        return float(params.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def _pick_size(options, avail_in):
    """Catalog size for an opening: the largest [size, minimum opening]
    pair whose minimum fits ``avail_in`` (inches), else the smallest."""
    rows = []
    for row in options or ():
        try:
            rows.append((float(row[0]), float(row[1])))
        except (TypeError, ValueError, IndexError):
            continue
    if not rows:
        return None
    fit = [r for r in rows if r[1] <= avail_in + 1e-3]
    return max(fit)[0] if fit else min(rows)[0]


def pullout_size(params, open_w, open_h):
    """(width, height) of a pull-out unit, in meters, for a face frame
    opening hole of open_w x open_h: the product's own size from the
    entry (see the module notes), clipped to the hole."""
    ow, oh = open_w / inch(1.0), open_h / inch(1.0)
    w = None
    if 'unit_width' in params:
        w = _p(params, 'unit_width', 0.0)
    elif 'sizes' in params:
        w = _pick_size(params.get('sizes'), ow)
    elif 'fit_width' in params:
        try:
            clr, lo, hi = (float(v) for v in params.get('fit_width'))
            w = min(max(ow - clr, lo), hi)
        except (TypeError, ValueError):
            w = None
    if not w:
        w = ow - 0.5
    h = None
    if 'unit_height' in params:
        h = _p(params, 'unit_height', PULLOUT_DEFAULT_HEIGHT)
    elif 'heights' in params:
        h = _pick_size(params.get('heights'), oh)
    elif 'height_range' in params:
        try:
            lo, hi = (float(v) for v in params.get('height_range'))
            h = min(max(oh, lo), hi)
        except (TypeError, ValueError):
            h = None
    elif params.get('fill_height'):
        h = oh
    if not h:
        h = PULLOUT_DEFAULT_HEIGHT
    return min(inch(w), open_w), min(inch(h), open_h)


def _pullout_placement(params, rect, front_y, room_y):
    """(position, dims) of a pull-out unit in opening-local space: its
    own size, centered across the face frame opening hole, standing on
    the hole's bottom edge with its front panel at front_y."""
    rev_l = max(0.0, rect.get('reveal_left', 0.0))
    rev_r = max(0.0, rect.get('reveal_right', 0.0))
    rev_b = max(0.0, rect.get('reveal_bottom', 0.0))
    rev_t = max(0.0, rect.get('reveal_top', 0.0))
    open_w = rect['cage_dim_x'] - rev_l - rev_r
    open_h = rect['cage_dim_z'] - rev_b - rev_t
    if open_w <= 0.0 or open_h <= 0.0:
        return None
    w, h = pullout_size(params, open_w, open_h)
    depth = min(inch(_p(params, 'unit_depth', PULLOUT_DEFAULT_DEPTH)), room_y)
    if w <= inch(0.5) or h <= inch(0.5) or depth <= inch(0.5):
        return None
    return (rev_l + (open_w - w) / 2.0, front_y, rev_b), (w, depth, h)


def pullout_descriptor(code, rect, anchor, depth_space):
    """Descriptor for the unit behind a pull-out front, or None when the
    code names no pull-out model. ``anchor`` is the front pivot's
    closed position (opening-local): the unit's front panel sits against
    the back of the front, and the returned position is relative to the
    pivot so the unit rides the front's slide. ``depth_space`` is the
    depth from the back of the front to the cavity back."""
    spec = model_for(code)
    if spec is None or spec[0] not in PULLOUT_MODELS:
        return None
    model, params = spec
    ax, ay, az = anchor
    placed = _pullout_placement(
        params, rect, ay, depth_space - PULLOUT_REAR_CLEARANCE)
    if placed is None:
        return None
    (x0, y0, z0), dims = placed
    from ... import accessory_registry
    entry = accessory_registry.find(code) or {}
    return {
        'kind':     'ACCESSORY_MODEL',
        'role':     ROLE,
        'name':     '%s Model' % (entry.get('name') or code),
        'model':    model,
        'params':   dict(params),
        'position': (x0 - ax, y0 - ay, z0 - az),
        'dims':     dims,
    }


def descriptor(rect, cage_dim_y, item, front_y, back_setback):
    """Geometry descriptor for the item's model in opening-local space,
    or None (no model, or no room at all). Roll-outs are centered in the
    face frame opening at their unit width, standing on the opening
    bottom at the front of the cavity; organizers span the opening at
    their unit height; pull-out units stand at their own size, centered.
    Anything larger than the opening is clipped."""
    spec = model_for(getattr(item, 'accessory_code', ''))
    if spec is None:
        return None
    model, params = spec
    cage_x, cage_z = rect['cage_dim_x'], rect['cage_dim_z']
    room_y = cage_dim_y - front_y - back_setback
    if model in PULLOUT_MODELS:
        placed = _pullout_placement(params, rect, front_y, room_y)
        if placed is None:
            return None
        (x0, _y, z0), (w, depth, h) = placed
    elif model in ROLLOUT_MODELS:
        rev_l = max(0.0, rect.get('reveal_left', 0.0))
        rev_r = max(0.0, rect.get('reveal_right', 0.0))
        rev_b = max(0.0, rect.get('reveal_bottom', 0.0))
        rev_t = max(0.0, rect.get('reveal_top', 0.0))
        open_w = cage_x - rev_l - rev_r
        open_h = cage_z - rev_b - rev_t
        fit_w = open_w - 2.0 * ROLLOUT_SLIDE_CLEARANCE
        if fit_w <= 0.0:
            fit_w = open_w
        w = min(inch(_p(params, 'unit_width', 14.5)), fit_w)
        h = min(inch(_p(params, 'unit_height', 17.5)), open_h)
        depth = min(ROLLOUT_MAX_DEPTH, room_y)
        x0 = rev_l + (open_w - w) / 2.0
        z0 = rev_b
    else:
        x0 = z0 = 0.0
        w = cage_x
        if rect.get('finish_flush'):
            # A flush finish bands the opening; stay inside the band.
            x0 = rect.get('reveal_left', 0.0)
            z0 = rect.get('reveal_bottom', 0.0)
            w -= x0 + rect.get('reveal_right', 0.0)
            cage_z -= z0 + rect.get('reveal_top', 0.0)
        h = min(inch(_p(params, 'unit_height', 12.0)), cage_z)
        depth = room_y
    if w <= inch(0.5) or h <= inch(0.5) or depth <= inch(0.5):
        return None
    label = getattr(item, 'accessory_label', '') or item.accessory_code
    return {
        'kind':     'ACCESSORY_MODEL',
        'role':     ROLE,
        'name':     '%s Model' % label,
        'model':    model,
        'params':   dict(params),
        'position': (x0, front_y, z0),
        'dims':     (w, depth, h),
    }


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def _box(bm, x0, x1, y0, y1, z0, z1, mi=0):
    if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6 or z1 - z0 <= 1e-6:
        return
    v = [bm.verts.new((x, y, z))
         for z in (z0, z1) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
              (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f]).material_index = mi


def _prism(bm, poly, axis, a0, a1, mi=0):
    """Extrude a closed 2D outline along ``axis`` from a0 to a1. The
    outline is (y, z) for 'X', (x, z) for 'Y', (x, y) for 'Z'."""
    if a1 - a0 <= 1e-6 or len(poly) < 3:
        return

    def pt(u, v, a):
        if axis == 'X':
            return (a, u, v)
        if axis == 'Y':
            return (u, a, v)
        return (u, v, a)
    lo = [bm.verts.new(pt(u, v, a0)) for u, v in poly]
    hi = [bm.verts.new(pt(u, v, a1)) for u, v in poly]
    n = len(poly)
    bm.faces.new(list(reversed(lo))).material_index = mi
    bm.faces.new(hi).material_index = mi
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i])).material_index = mi


def _rod_x(bm, x0, x1, y, z, mi=1):
    _box(bm, x0, x1, y - WIRE / 2, y + WIRE / 2, z - WIRE / 2, z + WIRE / 2, mi)


def _rod_y(bm, x, y0, y1, z, mi=1):
    _box(bm, x - WIRE / 2, x + WIRE / 2, y0, y1, z - WIRE / 2, z + WIRE / 2, mi)


def _rod_z(bm, x, y, z0, z1, mi=1):
    _box(bm, x - WIRE / 2, x + WIRE / 2, y - WIRE / 2, y + WIRE / 2, z0, z1, mi)


def _peg(bm, cx, cy, z0, z1, r, mi=0):
    poly = [(cx + r * math.cos(math.radians(22.5 + 45 * i)),
             cy + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    _prism(bm, poly, 'Z', z0, z1, mi)


def _side_profile(d, low, high, rise_at, rise_len):
    """(y, z) outline of a tray side: ``low`` at the front, sweeping up
    on a quarter cove from ``rise_at`` to ``high`` over the back."""
    pts = [(0.0, 0.0), (0.0, low), (rise_at, low)]
    r = max(min(rise_len, high - low, d - rise_at - inch(0.5)), 0.0)
    if r > inch(0.25):
        # Cove centered above the start: level at first, upright at the
        # end, so the edge flows from the low front into the tall back.
        for i in range(1, 7):
            a = math.radians(15.0 * i)
            pts.append((rise_at + r * math.sin(a),
                        low + r - r * math.cos(a)))
        if high > low + r + 1e-6:
            pts.append((rise_at + r, high))
    elif high > low + 1e-6:
        pts.append((rise_at, high))
    pts += [(d, high), (d, 0.0)]
    return pts


def _tray(bm, x0, x1, d, z0, low, high, rise_at, rise_len, y0=0.0):
    """Open tray from y0 to y0 + d: floor, front, back and shaped sides."""
    t = WOOD_T
    w = x1 - x0
    if w <= 2 * t or d <= 2 * t:
        _box(bm, x0, x1, y0, y0 + d, z0, z0 + min(t, high))
        return
    prof = [(y0 + y, z0 + z) for y, z in _side_profile(d, low, high, rise_at,
                                                         rise_len)]
    _prism(bm, prof, 'X', x0, x0 + t)
    _prism(bm, prof, 'X', x1 - t, x1)
    _box(bm, x0 + t, x1 - t, y0, y0 + d, z0, z0 + t)              # floor
    _box(bm, x0 + t, x1 - t, y0, y0 + t, z0 + t, z0 + low)        # front
    _box(bm, x0 + t, x1 - t, y0 + d - t, y0 + d, z0 + t, z0 + high)  # back


def _spread(a, b, n):
    """n centers spread evenly across [a, b]."""
    if n <= 0:
        return []
    step = (b - a) / n
    return [a + step * (i + 0.5) for i in range(n)]


# ---------------------------------------------------------------------------
# Model builders: (bm, w, d, h, params)
# ---------------------------------------------------------------------------

def _build_rollout_tray_pegs(bm, w, d, h, params):
    t = WOOD_T
    low = min(inch(4.0), h)
    _tray(bm, 0.0, w, d, 0.0, low, h, d * 0.42, inch(3.0))
    floor = t
    # U pegs: an inverted U of chrome rod in the front half.
    pegs = int(_p(params, 'peg_count', 5))
    peg_h = min(inch(4.0), h - floor)
    py = d * 0.24
    for x in _spread(t + inch(0.5), w - t - inch(0.5), pegs):
        if peg_h <= WIRE:
            break
        for dx in (-inch(0.5), inch(0.5)):
            _rod_z(bm, x + dx, py, floor, floor + peg_h)
        _rod_x(bm, x - inch(0.5), x + inch(0.5), py, floor + peg_h)
    # Lid dividers: wire frames running front to back over the back.
    divs = int(_p(params, 'divider_count', pegs))
    div_h = min(inch(9.0), h - floor - inch(0.5))
    y0, y1 = d * 0.55, d - t - inch(0.5)
    if div_h > WIRE and y1 - y0 > inch(1.0):
        for x in _spread(t + inch(0.25), w - t - inch(0.25), divs):
            for y in (y0, (y0 + y1) / 2.0, y1):
                _rod_z(bm, x, y, floor, floor + div_h)
            _rod_y(bm, x, y0, y1, floor + div_h)
            _rod_y(bm, x, y0, y1, floor + inch(0.5))
    return True


def _rack(bm, x0, x1, y0, y1, z, height, loops, axis):
    """Wire rack standing on a floor: two base rails and ``loops``
    upright frames. axis 'Y' frames run front to back (lid racks), 'X'
    frames run side to side (pot racks)."""
    if x1 - x0 < inch(1.0) or y1 - y0 < inch(1.0) or height <= WIRE:
        return
    zt = z + height
    if axis == 'Y':
        for y in (y0, y1):
            _rod_x(bm, x0, x1, y, z + WIRE / 2)
        for x in _spread(x0, x1, loops):
            _rod_z(bm, x, y0, z, zt)
            _rod_z(bm, x, y1, z, zt)
            _rod_y(bm, x, y0, y1, zt)
    else:
        for x in (x0, x1):
            _rod_y(bm, x, y0, y1, z + WIRE / 2)
        for y in _spread(y0, y1, loops):
            _rod_z(bm, x0, y, z, zt)
            _rod_z(bm, x1, y, z, zt)
            _rod_x(bm, x0, x1, y, zt)


def _build_rollout_two_tier(bm, w, d, h, params):
    t = WOOD_T
    lower_h = min(h, max(h * 0.58, inch(4.0)))
    _tray(bm, 0.0, w, d, 0.0, lower_h * 0.5, lower_h, d * 0.12, inch(2.5))
    # Upper tier: a shallower tray over the back half, inside the lower
    # tray's sides, riding just above its rim.
    up_z = lower_h + inch(0.25)
    up_h = h - up_z
    up_y = d * 0.45
    ux0, ux1 = t + inch(0.125), w - t - inch(0.125)
    if up_h > inch(1.5) and ux1 - ux0 > inch(2.0):
        _tray(bm, ux0, ux1, d - up_y, up_z, up_h * 0.45, up_h,
              (d - up_y) * 0.15, inch(1.5), y0=up_y)
        # Wood dish pegs on the upper floor, a square in the middle.
        n = int(_p(params, 'dish_pegs', 4))
        floor = up_z + t
        peg_h = min(inch(5.0), up_h - t)
        cols = max(1, int(math.ceil(math.sqrt(n)))) if n > 0 else 0
        rows = int(math.ceil(n / cols)) if cols else 0
        cx0 = (ux0 + ux1) / 2.0 - (cols - 1) * inch(1.5)
        cy0 = up_y + (d - up_y) / 2.0 - (rows - 1) * inch(1.5)
        for i in range(n):
            if peg_h <= 0.0:
                break
            cx = cx0 + (i % cols) * inch(3.0)
            cy = cy0 + (i // cols) * inch(3.0)
            _peg(bm, cx, cy, floor, floor + peg_h, inch(0.375))
    # Wire racks on the lower floor, in the open front half.
    lids = int(_p(params, 'lid_organizers', 1))
    pots = int(_p(params, 'pot_organizers', 1))
    count = lids + pots
    rack_y0, rack_y1 = t + inch(1.0), min(up_y - inch(0.5), t + inch(7.0))
    rack_h = lower_h - t - inch(1.0)
    if count and rack_y1 - rack_y0 > inch(2.0):
        span = (w - 2 * t - inch(0.5)) / count
        x = t + inch(0.25)
        for k in range(count):
            lid = k < lids
            _rack(bm, x + inch(0.25), x + span - inch(0.25),
                  rack_y0, rack_y1, t,
                  min(rack_h, inch(4.0) if lid else inch(7.0)),
                  5 if lid else 3, 'Y' if lid else 'X')
            x += span
    return True


def _trimmed_box(bm, w, d, h):
    """Open-front organizer shell (top, bottom, ends) behind a band of
    front moulding. Returns the inside (x0, x1, z0, z1) and panel y0."""
    t, y0 = WOOD_T, TRIM_T
    _box(bm, 0.0, w, y0, d, 0.0, t)
    _box(bm, 0.0, w, y0, d, h - t, h)
    _box(bm, 0.0, t, y0, d, t, h - t)
    _box(bm, w - t, w, y0, d, t, h - t)
    _box(bm, 0.0, w, 0.0, y0, 0.0, TRIM_W)
    _box(bm, 0.0, w, 0.0, y0, h - TRIM_W, h)
    _box(bm, 0.0, TRIM_W, 0.0, y0, TRIM_W, h - TRIM_W)
    _box(bm, w - TRIM_W, w, 0.0, y0, TRIM_W, h - TRIM_W)
    return t, w - t, t, h - t, y0


def _upright(bm, x, y0, d, z0, z1):
    """Partition centered on x with its moulding strip."""
    t = WOOD_T
    _box(bm, x - t / 2, x + t / 2, y0, d, z0, z1)
    _box(bm, x - TRIM_W / 2, x + TRIM_W / 2, 0.0, y0, z0, z1)


def _shelf(bm, x0, x1, y0, d, z):
    t = WOOD_T
    _box(bm, x0, x1, y0, d, z - t / 2, z + t / 2)
    _box(bm, x0, x1, 0.0, y0, z - TRIM_W / 2, z + TRIM_W / 2)


def _build_organizer_cubbies(bm, w, d, h, params):
    if w <= 2 * WOOD_T or h <= 2 * WOOD_T or d <= TRIM_T + WOOD_T:
        _box(bm, 0.0, w, 0.0, d, 0.0, h)
        return True
    ix0, ix1, iz0, iz1, y0 = _trimmed_box(bm, w, d, h)
    cw = inch(_p(params, 'center_width', 12.0))
    cx = w / 2.0
    left, right = cx - cw / 2.0, cx + cw / 2.0
    if left - ix0 < inch(2.0):
        # Too narrow for side bays: the whole width is the center section.
        left, right = ix0, ix1
    else:
        _upright(bm, left, y0, d, iz0, iz1)
        _upright(bm, right, y0, d, iz0, iz1)
    # Paper bay below a shelf, three slots above it.
    shelf_z = iz0 + (iz1 - iz0) * 0.45
    _shelf(bm, left + WOOD_T / 2, right - WOOD_T / 2, y0, d, shelf_z)
    for i in (1, 2):
        _upright(bm, left + (right - left) * i / 3.0, y0, d,
                 shelf_z + WOOD_T / 2, iz1)
    return True


def _build_organizer_letter_slots(bm, w, d, h, params):
    if w <= 2 * WOOD_T or h <= 2 * WOOD_T or d <= TRIM_T + WOOD_T:
        _box(bm, 0.0, w, 0.0, d, 0.0, h)
        return True
    ix0, ix1, iz0, iz1, y0 = _trimmed_box(bm, w, d, h)
    cw = inch(_p(params, 'center_width', 12.0))
    s_min = inch(_p(params, 'slot_min', 4.0))
    s_max = inch(_p(params, 'slot_max', 5.0))
    cx = w / 2.0
    left, right = cx - cw / 2.0, cx + cw / 2.0
    side = left - WOOD_T / 2 - ix0
    if side >= s_min * 0.5:
        _upright(bm, left, y0, d, iz0, iz1)
        _upright(bm, right, y0, d, iz0, iz1)
        # Equal slots, as few as keep each one under the max width.
        n = max(1, int(math.ceil((side - 1e-6) / max(s_max + WOOD_T, 1e-6))))
        pitch = (side + WOOD_T) / n
        for i in range(1, n):
            _upright(bm, ix0 + pitch * i - WOOD_T / 2, y0, d, iz0, iz1)
            _upright(bm, ix1 - pitch * i + WOOD_T / 2, y0, d, iz0, iz1)
    else:
        left, right = ix0, ix1
    # Paper bay: a mid shelf with a finger notch at the front.
    t = WOOD_T
    sx0, sx1 = left + t / 2, right - t / 2
    z = (iz0 + iz1) / 2.0
    r = min(inch(1.25), (sx1 - sx0) / 4.0, (d - y0) / 3.0)
    poly = [(sx0, y0)]
    if r > inch(0.25):
        for i in range(9):
            a = math.radians(180.0 - 22.5 * i)
            poly.append((cx + r * math.cos(a), y0 + r * math.sin(a)))
    poly += [(sx1, y0), (sx1, d), (sx0, d)]
    _prism(bm, poly, 'Z', z - t / 2, z + t / 2)
    return True


# ---------------------------------------------------------------------------
# Pull-out units
# ---------------------------------------------------------------------------

PANEL_T = inch(0.5)
SLIDE_TOP = inch(1.37)           # top of the bottom-mount slides
TOP_RAIL_H = inch(1.45)          # wood rail along each open side at the top


def _bar(bm, x0, x1, y0, y1, z0, z1, t=RAIL, mi=1):
    """Square rod between two points that differ along one axis."""
    h = t / 2.0
    if abs(x1 - x0) > 1e-6:
        _box(bm, min(x0, x1), max(x0, x1), y0 - h, y0 + h, z0 - h, z0 + h, mi)
    elif abs(y1 - y0) > 1e-6:
        _box(bm, x0 - h, x0 + h, min(y0, y1), max(y0, y1), z0 - h, z0 + h, mi)
    else:
        _box(bm, x0 - h, x0 + h, y0 - h, y0 + h, min(z0, z1), max(z0, z1), mi)


def _chassis(bm, w, d, h, panel_t=PANEL_T, deck=True, top_rails=True,
             panel_mi=0):
    """Slides, deck and front / back panels of a pull-out. Returns the
    open inside (x0, x1, y0, y1, floor_z, top_z) between the panels;
    top_z is under the top rails."""
    sw = min(inch(1.6), w * 0.3)
    for x in (0.0, w - sw):
        _box(bm, x, x + sw, inch(0.13), d, inch(0.3), SLIDE_TOP, MI_STEEL)
    e = min(inch(0.08), w * 0.02)
    back = d - inch(0.57) if d > inch(4.0) else d
    floor = SLIDE_TOP
    if deck:
        _box(bm, e, w - e, 0.0, back, SLIDE_TOP, SLIDE_TOP + PANEL_T)
        floor = SLIDE_TOP + PANEL_T
    else:
        # Low steel strips along each side tie the panels together.
        bw = min(PANEL_T, w * 0.1)
        for x in (e, w - e - bw):
            _box(bm, x, x + bw, panel_t, back - panel_t,
                 floor, floor + inch(0.82), panel_mi)
    _box(bm, e, w - e, 0.0, panel_t, floor, h, panel_mi)
    _box(bm, e, w - e, back - panel_t, back, floor, h, panel_mi)
    top = h
    if top_rails and h - floor > TOP_RAIL_H * 2:
        rw = min(PANEL_T, w * 0.12)
        top = h - TOP_RAIL_H
        for x in (e, w - e - rw):
            _box(bm, x, x + rw, panel_t, back - panel_t, top, h)
    return e, w - e, panel_t, back - panel_t, floor, top


def _side_rails(bm, x0, x1, y0, y1, z, height, mi=1):
    """Chrome rail along each open side above a shelf: a top rod with an
    upright at each end."""
    if height <= RAIL:
        return
    y0, y1 = y0 + inch(0.3), y1 - inch(0.3)
    for x in (x0 + inch(0.5), x1 - inch(0.5)):
        _bar(bm, x, x, y0, y1, z + height, z + height, mi=mi)
        for y in (y0, y1):
            _bar(bm, x, x, y, y, z, z + height, mi=mi)


def _lips(bm, x0, x1, y0, y1, z, height=TOP_RAIL_H):
    """Wood lip along each open side of a shelf."""
    lw = min(PANEL_T, (x1 - x0) * 0.12)
    for x in (x0, x1 - lw):
        _box(bm, x, x + lw, y0, y1, z, z + height)


def _shelf_with_holes(bm, x0, x1, y0, y1, z, holes, t=PANEL_T):
    """Shelf from x0..x1 / y0..y1 with rectangular cut-outs (x0, x1, y0,
    y1) for bins and inserts, built as the grid cells around them."""
    xs = sorted({x0, x1} | {v for hx0, hx1, _a, _b in holes
                            for v in (hx0, hx1) if x0 < v < x1})
    ys = sorted({y0, y1} | {v for _a, _b, hy0, hy1 in holes
                            for v in (hy0, hy1) if y0 < v < y1})
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx = (xs[i] + xs[i + 1]) / 2.0
            cy = (ys[j] + ys[j + 1]) / 2.0
            if any(a < cx < b and c < cy < d for a, b, c, d in holes):
                continue
            _box(bm, xs[i], xs[i + 1], ys[j], ys[j + 1], z, z + t)


def _bin(bm, x0, x1, y0, y1, z0, z1, mi=1):
    """Open-top steel bin (floor and four walls)."""
    t = inch(0.06)
    if x1 - x0 <= 2 * t or y1 - y0 <= 2 * t or z1 - z0 <= t:
        return
    _box(bm, x0, x1, y0, y1, z0, z0 + t, mi)
    _box(bm, x0, x1, y0, y0 + t, z0, z1, mi)
    _box(bm, x0, x1, y1 - t, y1, z0, z1, mi)
    _box(bm, x0, x0 + t, y0 + t, y1 - t, z0, z1, mi)
    _box(bm, x1 - t, x1, y0 + t, y1 - t, z0, z1, mi)


def _even_levels(lo, hi, n):
    """n shelf heights spread evenly between lo and hi (exclusive)."""
    if n <= 0 or hi <= lo:
        return []
    step = (hi - lo) / (n + 1)
    return [lo + step * (i + 1) for i in range(n)]


def _build_can_storage_wood(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h)
    n = int(_p(params, 'shelves', 3))
    swivel = bool(params.get('swivel'))
    levels = [z for z in _even_levels(floor, top, n)
              if z + PANEL_T < top - inch(1.0)]
    rail_h = inch(2.7)
    tops = [floor] + [z + PANEL_T for z in levels]
    for z in levels:
        _box(bm, x0, x1, y0, y1, z, z + PANEL_T)
        if swivel:
            # Turntable hub under a swivel shelf.
            r = min(inch(1.0), (x1 - x0) / 4.0)
            _peg(bm, (x0 + x1) / 2.0, (y0 + y1) / 2.0,
                 z - inch(0.4), z, r, MI_STEEL)
    for i, z in enumerate(tops):
        nxt = levels[i] if i < len(levels) else top
        _side_rails(bm, x0, x1, y0, y1, z, min(rail_h, nxt - z - inch(0.5)))
    return True


def _wire_basket(bm, x0, x1, y0, y1, z, height, pitch=inch(1.0),
                 frames=3, floor_board=False):
    """Chrome wire basket: rods along y for the floor, end / middle
    frames across, and two rim rods down each side."""
    if x1 - x0 < inch(1.0) or y1 - y0 < inch(2.0):
        return
    n = max(2, int(round((x1 - x0) / pitch)) + 1)
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        _bar(bm, x, x, y0 + inch(0.4), y1 - inch(0.4), z, z)
    for k in range(frames):
        y = y0 + inch(0.4) + (y1 - y0 - inch(0.8)) * k / max(1, frames - 1)
        _bar(bm, x0, x1, y, y, z, z)
        _bar(bm, x0, x1, y, y, z + height, z + height)
        for x in (x0, x1):
            _bar(bm, x, x, y, y, z, z + height)
    for x in (x0, x1):
        _bar(bm, x, x, y0, y1, z + height * 0.45, z + height * 0.45)
        _bar(bm, x, x, y0, y1, z + height, z + height)
    if floor_board:
        _box(bm, x0 + RAIL, x1 - RAIL, y0 + inch(0.5), y1 - inch(0.5),
             z + RAIL / 2, z + RAIL / 2 + inch(0.25))


def _build_can_storage_wire(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h, deck=False)
    n = max(1, int(_p(params, 'baskets', 2)))
    bh = inch(2.15)
    inset = min(inch(0.8), w * 0.12)
    z_first = floor + inch(0.15)
    z_last = max(z_first, top - bh - inch(7.75))
    for k in range(n):
        z = z_first + ((z_last - z_first) * k / (n - 1) if n > 1 else 0.0)
        _wire_basket(bm, inset, w - inset, y0 + inch(0.25), y1 - inch(0.25),
                     z, bh, floor_board=bool(params.get('deluxe')))
    return True


def _bin_holes(x0, x1, y0, y1, rows, cols, bin_d, gap=inch(0.6)):
    """Bin footprints in a grid inside x0..x1 starting at the front."""
    out = []
    if rows <= 0 or cols <= 0:
        return out
    bw = (x1 - x0 - gap * (cols + 1)) / cols
    if bw <= inch(0.5):
        return out
    for c in range(cols):
        bx = x0 + gap + c * (bw + gap)
        for r in range(rows):
            by = y0 + gap + r * (bin_d + gap)
            if by + bin_d > y1:
                break
            out.append((bx, bx + bw, by, by + bin_d))
    return out


def _build_utensil_pullout(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h)
    shelf_z = max(floor + inch(6.0), top - inch(3.35))
    cols = 2 if w >= inch(10.5) else 1
    rows = int(_p(params, 'bins', 3))
    bin_d = (y1 - y0 - inch(0.6) * (rows + 1)) / max(rows, 1)
    holes = _bin_holes(x0, x1, y0, y1, rows, cols, min(bin_d, inch(5.4)))
    _shelf_with_holes(bm, x0, x1, y0, y1, shelf_z, holes)
    bin_h = min(inch(6.75), shelf_z - floor - inch(1.0))
    for bx0, bx1, by0, by1 in holes:
        _bin(bm, bx0 + inch(0.05), bx1 - inch(0.05), by0 + inch(0.05),
             by1 - inch(0.05), shelf_z + PANEL_T - bin_h,
             shelf_z + PANEL_T + inch(0.07))
    n = int(_p(params, 'shelves', 1))
    under = shelf_z - bin_h
    levels = _even_levels(floor, under, n)
    for z in levels:
        _box(bm, x0, x1, y0, y1, z, z + PANEL_T)
    for i, z in enumerate([floor] + [z + PANEL_T for z in levels]):
        nxt = levels[i] if i < len(levels) else under
        _side_rails(bm, x0, x1, y0, y1, z,
                    min(inch(2.7), nxt - z - inch(0.5)))
    return True


def _build_knife_pullout(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h)
    shelf_z = max(floor + inch(8.0), top - inch(3.6))
    cols = int(_p(params, 'bin_columns', 1))
    rows = int(_p(params, 'bins', 1))
    bin_d = inch(4.3) if cols > 1 else inch(5.35)
    holes = _bin_holes(x0, x1, y0, y0 + rows * (bin_d + inch(0.6))
                       + inch(0.6), rows, cols, bin_d)
    front_end = max([b[3] for b in holes] or [y0]) + inch(0.4)
    # Knife inserts fill the rest of the shelf behind the bins.
    kd = min(inch(13.0), y1 - front_end - inch(0.15))
    knives = []
    if kd > inch(2.0):
        n = int(_p(params, 'knife_inserts', 1))
        gap = inch(0.2)
        kw = (x1 - x0 - inch(0.3) - gap * (n - 1)) / max(n, 1)
        for i in range(n):
            kx = x0 + inch(0.15) + i * (kw + gap)
            knives.append((kx, kx + kw, y1 - kd, y1 - inch(0.15)))
    _shelf_with_holes(bm, x0, x1, y0, y1, shelf_z, holes + knives)
    bin_h = min(inch(6.75), shelf_z - floor - inch(1.0))
    for bx0, bx1, by0, by1 in holes:
        _bin(bm, bx0 + inch(0.05), bx1 - inch(0.05), by0 + inch(0.05),
             by1 - inch(0.05), shelf_z + PANEL_T - bin_h,
             shelf_z + PANEL_T + inch(0.07))
    kh = min(inch(10.0), shelf_z - floor - inch(0.5))
    for kx0, kx1, ky0, ky1 in knives:
        _box(bm, kx0, kx1, ky0, ky1, shelf_z + PANEL_T - kh,
             shelf_z + PANEL_T, MI_STEEL)
        # Knife slots across the insert's top.
        for y in _spread(ky0 + inch(0.5), ky1 - inch(0.5),
                         max(2, int((ky1 - ky0) / inch(1.25)))):
            _box(bm, kx0 + inch(0.3), kx1 - inch(0.3), y - inch(0.06),
                 y + inch(0.06), shelf_z + PANEL_T,
                 shelf_z + PANEL_T + inch(0.04), 1)
    _side_rails(bm, x0, x1, y0, y1, floor, inch(2.7))
    _side_rails(bm, x0, x1, y0, y1, shelf_z + PANEL_T,
                min(inch(1.5), top - shelf_z - PANEL_T - inch(0.3)))
    return True


def _build_towel_pullout(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h, top_rails=False)
    shelf_z = floor + (h - floor) * 0.49
    _box(bm, x0, x1, y0, y1, shelf_z, shelf_z + PANEL_T)
    st = shelf_z + PANEL_T
    _lips(bm, x0, x1, y0, y1, st)
    # Towel bay at the front, storage compartment behind a divider.
    div_y = y0 + (y1 - y0) * 0.5
    _box(bm, x0, x1, div_y, div_y + PANEL_T, st, h)
    rw = min(PANEL_T, w * 0.12)
    for x in (x0, x1 - rw):
        _box(bm, x, x + rw, div_y + PANEL_T, y1, h - TOP_RAIL_H, h)
        _box(bm, x, x + rw, div_y + PANEL_T, div_y + PANEL_T + TOP_RAIL_H,
             st + TOP_RAIL_H, h - TOP_RAIL_H)
    # Roll holder: a bar from the front panel to the divider.
    zb = min(st + inch(6.6), h - inch(2.0))
    cx = (x0 + x1) / 2.0
    _box(bm, cx - inch(0.25), cx + inch(0.25), y0, div_y, zb,
         zb + inch(1.45))
    _side_rails(bm, x0, x1, y0, y1, floor,
                min(inch(2.7), shelf_z - floor - inch(0.5)))
    return True


def _canister(bm, x0, x1, y0, y1, z0, z1):
    lid = min(inch(1.0), (z1 - z0) * 0.2)
    if z1 - z0 <= lid + inch(0.5):
        return
    _box(bm, x0 + inch(0.25), x1 - inch(0.25), y0 + inch(0.25),
         y1 - inch(0.25), z0, z1 - lid, MI_PLASTIC)
    _box(bm, x0, x1, y0, y1, z1 - lid, z1, MI_STEEL)


def _build_canister_pullout(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h, top_rails=False)
    shelf_z = floor + (h - floor) * 0.67
    _box(bm, x0, x1, y0, y1, shelf_z, shelf_z + PANEL_T)
    st = shelf_z + PANEL_T
    _lips(bm, x0, x1, y0, y1, floor)
    _lips(bm, x0, x1, y0, y1, st)
    cx0, cx1 = x0 + inch(0.4), x1 - inch(0.4)
    for count, zb, zt in ((int(_p(params, 'lower', 3)), floor,
                           min(shelf_z - inch(0.25), floor + inch(12.6))),
                          (int(_p(params, 'upper', 4)), st,
                           min(h - inch(0.25), st + inch(6.0)))):
        if count <= 0:
            continue
        pitch = (y1 - y0 - inch(0.3)) / count
        for i in range(count):
            cy = y0 + inch(0.15) + pitch * i
            _canister(bm, cx0, cx1, cy + inch(0.1), cy + pitch - inch(0.1),
                      zb, zt)
    return True


def _build_tray_divider_pullout(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h)
    n = int(_p(params, 'dividers', 1 if w < inch(7.75) else 2))
    dh = min(inch(10.0), top - floor - inch(2.0))
    dt = inch(0.25)
    for i in range(max(n, 0)):
        xd = x0 + (x1 - x0) * (i + 1) / (n + 1)
        _box(bm, xd - dt / 2, xd + dt / 2, y0, y1, floor, floor + dh)
        # T-bar riding the divider's top edge.
        _bar(bm, xd, xd, y0 + inch(0.5), y1 - inch(0.5), floor + dh,
             floor + dh, t=inch(0.25))
    # Side rails at two heights, carried on chrome uprights.
    lw = min(PANEL_T, (x1 - x0) * 0.12)
    rails = [floor + (top - floor) * 0.18, floor + (top - floor) * 0.62]
    for z in rails:
        for x in (x0, x1 - lw):
            _box(bm, x, x + lw, y0, y1, z, z + TOP_RAIL_H)
    for x in (x0 + lw / 2, x1 - lw / 2):
        for y in (y0 + (y1 - y0) * 0.33, y0 + (y1 - y0) * 0.72):
            _bar(bm, x, x, y, y, floor, rails[-1] + TOP_RAIL_H)
    return True


def _build_spice_pullout(bm, w, d, h, params):
    t = inch(0.27)
    x0, x1, y0, y1, floor, top = _chassis(bm, w, d, h, panel_t=t,
                                          top_rails=False)
    cap = PANEL_T
    _box(bm, x0, x1, 0.0, y1 + t, h - cap, h)
    top = h - cap
    if params.get('adjustable'):
        levels = _even_levels(floor, top, int(_p(params, 'shelves', 3)))
        for z in levels:
            _box(bm, x0, x1, y0, y1, z, z + PANEL_T)
        for i, z in enumerate([floor] + [z + PANEL_T for z in levels]):
            nxt = levels[i] if i < len(levels) else top
            _side_rails(bm, x0, x1, y0, y1, z,
                        min(inch(1.4), nxt - z - inch(0.5)))
        return True
    # Fixed shelves 5-1/2" apart with a 3/8" wood rail along each side.
    pitch = inch(_p(params, 'shelf_spacing', 5.5)) + PANEL_T
    z = floor
    rail = inch(0.375)
    while True:
        rz = z + inch(1.3)
        if rz + rail > top:
            break
        for x in (x0 + rail, x1 - rail):
            _bar(bm, x, x, y0, y1, rz, rz, t=rail, mi=0)
        z += pitch
        if z + PANEL_T > top - inch(2.0):
            break
        _box(bm, x0, x1, y0, y1, z - PANEL_T, z)
    return True


def _build_wire_pantry(bm, w, d, h, params):
    x0, x1, y0, y1, floor, top = _chassis(
        bm, w, d, h, deck=False, top_rails=False, panel_mi=MI_STEEL)
    n = int(_p(params, 'baskets', 0))
    if n <= 0:
        n = 4
        steps = params.get('basket_steps') or ()
        for row in steps:
            try:
                if h / inch(1.0) + 1e-3 >= float(row[0]):
                    n = int(row[1])
            except (TypeError, ValueError, IndexError):
                continue
    # Center posts front and back, joined by a bar over the top.
    cx = (x0 + x1) / 2.0
    pw = min(inch(0.74), w * 0.2)
    post_top = h - inch(1.17)
    for py0, py1 in ((y0, y0 + PANEL_T), (y1 - PANEL_T, y1)):
        _box(bm, cx - pw / 2, cx + pw / 2, py0, py1, floor, post_top,
             MI_STEEL)
    _box(bm, cx - pw / 2, cx + pw / 2, y0, y1, post_top,
         post_top + PANEL_T, MI_STEEL)
    bh = inch(3.0)
    inset = min(inch(0.8), w * 0.12)
    z_first = floor + inch(0.05)
    z_last = max(z_first, post_top - bh - inch(9.0))
    for k in range(max(1, n)):
        z = z_first + ((z_last - z_first) * k / (n - 1) if n > 1 else 0.0)
        _wire_basket(bm, inset, w - inset, y0 + inch(0.1), y1 - inch(0.1),
                     z, bh, pitch=inch(0.75), frames=2)
    return True


_BUILDERS = {
    'can_storage_wood':       _build_can_storage_wood,
    'can_storage_wire':       _build_can_storage_wire,
    'utensil_pullout':        _build_utensil_pullout,
    'knife_pullout':          _build_knife_pullout,
    'towel_pullout':          _build_towel_pullout,
    'canister_pullout':       _build_canister_pullout,
    'tray_divider_pullout':   _build_tray_divider_pullout,
    'spice_pullout':          _build_spice_pullout,
    'wire_pantry':            _build_wire_pantry,
    'rollout_tray_pegs':      _build_rollout_tray_pegs,
    'rollout_two_tier':       _build_rollout_two_tier,
    'organizer_cubbies':      _build_organizer_cubbies,
    'organizer_letter_slots': _build_organizer_letter_slots,
}


# Material spec name -> shared accessory material key.
_MATERIAL_KEYS = {
    'Accessory Maple': 'MAPLE',
    'Accessory Plywood': 'PLYWOOD',
    'Accessory Chrome': 'CHROME',
    'Accessory Steel': 'STEEL',
    'Accessory Clear Plastic': 'CLEAR_PLASTIC',
    'Accessory Almond Polymer': 'POLYMER',
}


def _material(spec):
    """The cabinet's own wood or a pull metal finish for this spec (see
    accessory_materials), else a plain material in the spec's colour."""
    name, color, metallic, rough = spec
    mat = accessory_materials.get(_MATERIAL_KEYS.get(name, ''))
    if mat is not None:
        return mat
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color
        mat.metallic = metallic
        mat.roughness = rough
    return mat


def build_object(model, name, w, depth, h, params=None):
    """Mesh object for a model, or None (unknown model / no room). The
    object is NOT linked; the caller links, parents and tags it."""
    builder = _BUILDERS.get(model)
    if builder is None or w <= 0.0 or h <= 0.0 or depth <= 0.0:
        return None
    bm = bmesh.new()
    ok = builder(bm, w, depth, h, params or {})
    if not ok or not bm.faces:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    organizer = model in ORGANIZER_MODELS
    mesh.materials.append(_material(_MAT_PLY if organizer else _MAT_MAPLE))
    mesh.materials.append(_material(_MAT_CHROME))
    if model in PULLOUT_MODELS:
        mesh.materials.append(_material(_MAT_STEEL))
        mesh.materials.append(_material(_MAT_PLASTIC))
    obj = hb_utils.new_object(name, mesh)
    if organizer:
        obj[FINISH_MATCH_KEY] = True
    return obj
