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
from ...units import inch

ROLE = 'ACCESSORY_MODEL'
# Object flag read by the material walk: slot 0 takes the cabinet's
# exterior finish (otherwise the model keeps its own wood).
FINISH_MATCH_KEY = 'hb_accessory_finish_match'
INTERIOR_HOST = 'opening_interior_accessory'

ROLLOUT_MODELS = frozenset({'rollout_tray_pegs', 'rollout_two_tier'})
ORGANIZER_MODELS = frozenset({'organizer_cubbies', 'organizer_letter_slots'})
MODELS = ROLLOUT_MODELS | ORGANIZER_MODELS

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


def descriptor(rect, cage_dim_y, item, front_y, back_setback):
    """Geometry descriptor for the item's model in opening-local space,
    or None (no model, or no room at all). Roll-outs are centered in the
    face frame opening at their unit width, standing on the opening
    bottom at the front of the cavity; organizers span the opening at
    their unit height. Anything larger than the opening is clipped."""
    spec = model_for(getattr(item, 'accessory_code', ''))
    if spec is None:
        return None
    model, params = spec
    cage_x, cage_z = rect['cage_dim_x'], rect['cage_dim_z']
    room_y = cage_dim_y - front_y - back_setback
    if model in ROLLOUT_MODELS:
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


_BUILDERS = {
    'rollout_tray_pegs':      _build_rollout_tray_pegs,
    'rollout_two_tier':       _build_rollout_two_tier,
    'organizer_cubbies':      _build_organizer_cubbies,
    'organizer_letter_slots': _build_organizer_letter_slots,
}


def _material(spec):
    name, color, metallic, rough = spec
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
    obj = hb_utils.new_object(name, mesh)
    if organizer:
        obj[FINISH_MATCH_KEY] = True
    return obj
