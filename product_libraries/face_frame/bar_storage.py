"""Tableware & Bar Storage Solutions (catalog printed pages 293-295).

Interior-insert geometry for the wine / bar storage products. Each
builder returns one unlinked mesh object covering the whole insert; the
interior recalc parents it to the opening cage, and the standard
interior wipe rebuilds it every recalc (the meshes are fully derived
from the opening size, so nothing user-authored lives on them).

Products and their catalog rules:

- WINE_CUBBY (WRC):     1/2" plywood egg-crate; openings 4"-6" equally
                        spaced (min-opening chart pitch 4-1/2").
- WINE_CELLAR (WRWCR):  3/4" hardwood partitions; openings exactly
                        4" x 4" (chart pitch 4-3/4"), grid centered.
- WINE_LATTICE (WRL):   45-degree lattice, max 3-3/4" square bottle
                        openings; front + rear lattice frames.
- WINE_X (WRXS/WRXR):   two 3/4" plywood panels crossing corner to
                        corner (edge-on to the front).
- WINE_DIAGONAL (WRD):  parallel 3/4" panels at 45 degrees, spaced
                        equally between 4" and 7".
- WINE_HALF_CIRCLE (WRHC): 2-1/2" tall scalloped rails (front + back),
                        bottles 5" on center, rows at min 6-1/2".
- STEMWARE_RACK (SR):   slotted slats under a top panel; 1" slots at
                        4" on center.
- PLATE_RACK (PR):      3/8" birch dowels 2" on center, two ranks.

All units sit at the FRONT of the cavity and are blocked off at 12"
deep ("Deep cabinets will be blocked off at 12" ") - the descriptor
builder in solver_face_frame caps the depth before calling in here.

Geometry convention: local origin at the front-left-bottom of the
insert volume; x runs right (0..w), y runs back (0..depth), z runs up
(0..h). Front-view outlines are built in the x-z plane and prism-
extruded along +Y (or x-y outlines along +Z for dowels).
"""

import bpy
import bmesh
import math

from ...units import inch

# Kinds owned by this module (must match the Face_Frame_Interior_Item
# enum identifiers). Solver + recalc route on membership here.
KINDS = frozenset({
    'WINE_CUBBY', 'WINE_CELLAR', 'WINE_LATTICE', 'WINE_X',
    'WINE_DIAGONAL', 'WINE_HALF_CIRCLE', 'STEMWARE_RACK', 'PLATE_RACK',
})

KIND_LABELS = {
    'WINE_CUBBY':       'Wine Storage Cubby',
    'WINE_CELLAR':      'Wine Cellar Rack',
    'WINE_LATTICE':     'Lattice Wine Rack',
    'WINE_X':           'X-Style Wine Rack',
    'WINE_DIAGONAL':    'Diagonal Wine Dividers',
    'WINE_HALF_CIRCLE': 'Half Circle Wine Rack',
    'STEMWARE_RACK':    'Stemware Rack',
    'PLATE_RACK':       'Plate Rack',
}

# Catalog: "Deep cabinets will be blocked off at 12"".
MAX_DEPTH = inch(12.0)

# Count computations floor exact catalog sizes (chart openings) that
# land a hair under an integer in float meters; nudge before flooring.
_EPS = 1e-6


def _floor_count(value, step):
    return int(value / step + _EPS)


# ---------------------------------------------------------------------------
# bmesh helpers
# ---------------------------------------------------------------------------

def _dedup(poly):
    out = []
    for p in poly:
        if not out or (abs(p[0] - out[-1][0]) > 1e-7
                       or abs(p[1] - out[-1][1]) > 1e-7):
            out.append(p)
    if len(out) > 2 and (abs(out[0][0] - out[-1][0]) < 1e-7
                         and abs(out[0][1] - out[-1][1]) < 1e-7):
        out.pop()
    return out


def _add_prism_y(bm, poly, y0, y1):
    """Extrude an x-z outline between two Y planes."""
    poly = _dedup(poly)
    if len(poly) < 3 or y1 - y0 <= 1e-7:
        return
    ring0 = [bm.verts.new((x, y0, z)) for x, z in poly]
    ring1 = [bm.verts.new((x, y1, z)) for x, z in poly]
    bm.faces.new(ring0)
    bm.faces.new(list(reversed(ring1)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))


def _add_prism_z(bm, poly, z0, z1):
    """Extrude an x-y outline between two Z planes (dowels)."""
    poly = _dedup(poly)
    if len(poly) < 3 or z1 - z0 <= 1e-7:
        return
    ring0 = [bm.verts.new((x, y, z0)) for x, y in poly]
    ring1 = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(ring0)
    bm.faces.new(list(reversed(ring1)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))


def _rect_poly(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def _clip_poly(poly, w, h):
    """Sutherland-Hodgman clip of a convex x-z polygon to [0,w]x[0,h]."""

    def clip_edge(pts, inside, intersect):
        out = []
        n = len(pts)
        for i in range(n):
            a = pts[i]
            b = pts[(i + 1) % n]
            ia = inside(a)
            if ia:
                out.append(a)
                if not inside(b):
                    out.append(intersect(a, b))
            elif inside(b):
                out.append(intersect(a, b))
        return out

    def at_x(a, b, x):
        t = (x - a[0]) / (b[0] - a[0])
        return (x, a[1] + t * (b[1] - a[1]))

    def at_z(a, b, z):
        t = (z - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), z)

    pts = list(poly)
    for inside, intersect in (
        (lambda p: p[0] >= 0.0, lambda a, b: at_x(a, b, 0.0)),
        (lambda p: p[0] <= w,   lambda a, b: at_x(a, b, w)),
        (lambda p: p[1] >= 0.0, lambda a, b: at_z(a, b, 0.0)),
        (lambda p: p[1] <= h,   lambda a, b: at_z(a, b, h)),
    ):
        if len(pts) < 3:
            return []
        pts = clip_edge(pts, inside, intersect)
    pts = _dedup(pts)
    return pts if len(pts) >= 3 else []


def _band_poly(x0, z0, x1, z1, width):
    """Rectangle band of the given width centered on a segment."""
    dx = x1 - x0
    dz = z1 - z0
    length = math.hypot(dx, dz)
    if length <= 1e-9:
        return []
    nx = -dz / length * width / 2.0
    nz = dx / length * width / 2.0
    return [(x0 + nx, z0 + nz), (x1 + nx, z1 + nz),
            (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)]


def _arc(cx, cz, r, a0, a1, segments=10):
    """Sample an arc (degrees, CCW positive), excluding the start."""
    pts = []
    for i in range(1, segments + 1):
        a = math.radians(a0 + (a1 - a0) * i / segments)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------------------
# Grid fitting
# ---------------------------------------------------------------------------

def _fit_openings(span, op_min, op_max, member_t):
    """Max/mid count of equally-spaced openings so each lands between
    op_min and op_max. Returns 0 when the span can't host one."""
    if span < op_min:
        return 0
    n_max = _floor_count(span + member_t, op_min + member_t)
    n_min = int(math.ceil((span + member_t) / (op_max + member_t) - _EPS))
    target = (op_min + op_max) / 2.0
    n = int(round((span + member_t) / (target + member_t)))
    # When no count satisfies both bounds (span falls between chart
    # sizes), n_min > n_max; prefer fewer, larger openings over
    # cramped under-minimum ones.
    return max(1, min(n_max, max(n_min, n)))


def _grid_members(bm, w, h, depth, cols, rows, t,
                  x0=0.0, grid_w=None, z0=0.0, grid_h=None,
                  perimeter=False):
    """Emit the vertical / horizontal members of an egg-crate grid.
    cols/rows are OPENING counts; members sit between openings (and on
    the grid perimeter when requested and the grid floats inside the
    opening)."""
    if grid_w is None:
        grid_w = w
    if grid_h is None:
        grid_h = h
    op_w = (grid_w - (cols - 1) * t) / cols
    op_h = (grid_h - (rows - 1) * t) / rows

    xs = [x0 + (k + 1) * op_w + k * t for k in range(cols - 1)]
    zs = [z0 + (k + 1) * op_h + k * t for k in range(rows - 1)]
    if perimeter:
        # Perimeter members only when the margin can host the full
        # stock; smaller leftovers stay open against the carcass.
        if x0 >= t:
            xs = [x0 - t] + xs
        if w - (x0 + grid_w) >= t:
            xs = xs + [x0 + grid_w]
        if z0 >= t:
            zs = [z0 - t] + zs
        if h - (z0 + grid_h) >= t:
            zs = zs + [z0 + grid_h]

    zlo = max(0.0, z0 - (t if perimeter else 0.0))
    zhi = min(h, z0 + grid_h + (t if perimeter else 0.0))
    xlo = max(0.0, x0 - (t if perimeter else 0.0))
    xhi = min(w, x0 + grid_w + (t if perimeter else 0.0))
    for x in xs:
        _add_prism_y(bm, _rect_poly(x, zlo, x + t, zhi), 0.0, depth)
    for z in zs:
        _add_prism_y(bm, _rect_poly(xlo, z, xhi, z + t), 0.0, depth)


# ---------------------------------------------------------------------------
# Product builders (each fills a bmesh; dims in meters)
# ---------------------------------------------------------------------------

def _build_wine_cubby(bm, w, h, depth):
    """WRC: 1/2" ply egg-crate, openings 4"-6" equally spaced filling
    the opening. The 7-row ordering max is a pricing-time rule, not
    enforced here."""
    t = inch(0.5)
    cols = _fit_openings(w, inch(4.0), inch(6.0), t)
    rows = _fit_openings(h, inch(4.0), inch(6.0), t)
    if cols < 1 or rows < 1:
        return False
    _grid_members(bm, w, h, depth, cols, rows, t)
    return cols > 1 or rows > 1


def _build_wine_cellar(bm, w, h, depth):
    """WRWCR: 3/4" hardwood partitions at the chart's 4-3/4" column
    pitch (exact 4" openings); rows ride on thin removable rack rails
    at a 4" vertical pitch over a 3/4" base (chart heights: 4",
    8-3/4", 12-3/4" ... 28-3/4" for the 7-row max). Grid centered when
    the opening runs larger than the chart size."""
    t = inch(0.75)
    op = inch(4.0)
    rail_t = inch(0.375)
    cols = _floor_count(w + t, op + t)
    rows = min(7, _floor_count(h - t, op))
    if cols < 1 or rows < 1:
        # A single-row unit still needs the base + one bottle course.
        if cols < 1 or h < op:
            return False
        rows = 1
    grid_w = cols * op + (cols - 1) * t
    grid_h = t + rows * op
    if grid_h > h:
        grid_h = h
    x0 = (w - grid_w) / 2.0
    z0 = (h - grid_h) / 2.0

    # Vertical partitions: internal boundaries, plus the grid's outer
    # edges when the margin can host the full stock (smaller leftovers
    # stay open against the carcass).
    xs = [x0 + (k + 1) * op + k * t for k in range(cols - 1)]
    has_perim = x0 >= t
    if has_perim:
        xs = [x0 - t] + xs + [x0 + grid_w]
    for x in xs:
        _add_prism_y(bm, _rect_poly(x, z0, x + t, z0 + grid_h), 0.0, depth)

    # Base rail + thin removable rack rails between bottle courses.
    xlo = max(0.0, x0 - (t if has_perim else 0.0))
    xhi = min(w, x0 + grid_w + (t if has_perim else 0.0))
    _add_prism_y(bm, _rect_poly(xlo, z0, xhi, z0 + t), 0.0, depth)
    for k in range(1, rows):
        z = z0 + t + k * op - rail_t / 2.0
        _add_prism_y(bm, _rect_poly(xlo, z, xhi, z + rail_t), 0.0, depth)
    return True


# Lattice / X / diagonal front-view member width. The real members are
# 3/4" stock seen edge-on; 3/4" is also what the catalog line drawings
# read as.
_DIAG_T = inch(0.75)
# Lattice / plate / half-circle frame depth for the front + rear
# assemblies ("Plate & Lattice Wine Rack (Cross Section)" shows two
# frames with the bottle / plate spanning between).
_FRAME_D = inch(1.75)


def _dual_frame_layers(depth):
    """Front + rear y-extents for the two-frame products; collapses to
    a single frame when the cavity is too shallow for two."""
    if depth >= 3.0 * _FRAME_D:
        return [(0.0, _FRAME_D), (depth - _FRAME_D, depth)]
    return [(0.0, min(depth, _FRAME_D))]


def _diag_bands(w, h, pitch, direction):
    """45-degree band centerline segments covering the w x h rect.
    direction +1 = bottom-left to top-right, -1 = top-left to
    bottom-right. Returns segments long enough to cross the rect;
    callers clip."""
    c = math.sqrt(0.5)
    span = (w + h) * c
    count = int(span // pitch) + 2
    # Perp coordinate of the rect center; bands are laid symmetrically
    # around it so the pattern is centered.
    segs = []
    cx, cz = w / 2.0, h / 2.0
    ext = w + h  # long enough to cross any corner
    for k in range(-count, count + 1):
        # Band center point offset along the perp normal.
        if direction > 0:
            nx, nz = -c, c
            dxu, dzu = c, c
        else:
            nx, nz = c, c
            dxu, dzu = c, -c
        px = cx + nx * k * pitch
        pz = cz + nz * k * pitch
        segs.append((px - dxu * ext, pz - dzu * ext,
                     px + dxu * ext, pz + dzu * ext))
    return segs


def _build_wine_lattice(bm, w, h, depth):
    """WRL: 45-degree lattice with max 3-3/4" square bottle openings,
    as front + rear frames."""
    pitch = inch(3.75) + _DIAG_T
    layers = _dual_frame_layers(depth)
    any_geo = False
    for direction in (1, -1):
        for x0, z0, x1, z1 in _diag_bands(w, h, pitch, direction):
            poly = _clip_poly(_band_poly(x0, z0, x1, z1, _DIAG_T), w, h)
            if poly:
                any_geo = True
                for y0, y1 in layers:
                    _add_prism_y(bm, poly, y0, y1)
    return any_geo


def _build_wine_x(bm, w, h, depth):
    """WRXS / WRXR: two full-depth panels crossing corner to corner."""
    for seg in ((0.0, 0.0, w, h), (0.0, h, w, 0.0)):
        poly = _clip_poly(_band_poly(*seg, _DIAG_T), w, h)
        if poly:
            _add_prism_y(bm, poly, 0.0, depth)
    return True


def _build_wine_diagonal(bm, w, h, depth):
    """WRD: parallel full-depth panels at 45 degrees (bottom-left to
    top-right), spaced equally between 4" and 7" perpendicular."""
    c = math.sqrt(0.5)
    span = (w + h) * c
    if span < inch(4.0):
        return False
    # k dividers -> k+1 gaps. Aim near the middle of the 4"-7" range,
    # then clamp the spacing back into it where possible.
    k = max(1, int(round(span / inch(5.5))) - 1)
    while k > 1 and span / (k + 1) < inch(4.0):
        k -= 1
    while span / (k + 1) > inch(7.0):
        k += 1
    s = span / (k + 1)
    # Perp coordinate p of a point = (z - x) * c, range [-w*c, h*c].
    any_geo = False
    for i in range(k):
        p = -w * c + s * (i + 1)
        # Point on the centerline: intersect p with the rect diagonal
        # parameterization x = t - p/(2c)... simpler: a point with
        # (z - x) * c = p is (0, p/c) when p >= 0 else (-p/c, 0).
        if p >= 0.0:
            px, pz = 0.0, p / c
        else:
            px, pz = -p / c, 0.0
        ext = w + h
        poly = _clip_poly(
            _band_poly(px - ext * c, pz - ext * c,
                       px + ext * c, pz + ext * c, _DIAG_T), w, h)
        if poly:
            any_geo = True
            _add_prism_y(bm, poly, 0.0, depth)
    return any_geo


def _build_half_circle(bm, w, h, depth):
    """WRHC: rows of scalloped rails (front + back), bottles 5" on
    center, rail 2-1/2" tall, min 6-1/2" per row."""
    rail_h = inch(2.5)
    rail_t = inch(0.75)
    pitch = inch(5.0)
    r = inch(1.5)
    if h < inch(6.5) or w < pitch:
        return False
    rows = max(1, _floor_count(h, inch(6.5)))
    row_h = h / rows

    n = max(1, _floor_count(w - inch(1.0), pitch))
    first_cx = w / 2.0 - (n - 1) * pitch / 2.0

    # Scalloped outline in x-z with base at z=0 (translated per row).
    pts = [(0.0, 0.0), (0.0, rail_h)]
    for i in range(n):
        cx = first_cx + i * pitch
        pts.append((cx - r, rail_h))
        pts.extend(_arc(cx, rail_h, r, 180.0, 360.0, 12))
    pts.extend([(w, rail_h), (w, 0.0)])

    y_pairs = [(inch(0.5), inch(0.5) + rail_t)]
    if depth - inch(1.25) > y_pairs[0][1]:
        y_pairs.append((depth - inch(1.25), depth - inch(1.25) + rail_t))
    for k in range(rows):
        z0 = k * row_h
        row_pts = [(x, z0 + z) for x, z in pts]
        for y0, y1 in y_pairs:
            _add_prism_y(bm, row_pts, y0, y1)
    return True


def _build_stemware(bm, w, h, depth):
    """SR: top blocking panel with slotted slats hanging under it;
    1" slots at 4" on center (slats 3" wide), 3/4" foot gap."""
    panel_t = inch(0.75)
    slat_t = inch(0.75)
    slat_w = inch(3.0)
    pitch = inch(4.0)
    foot_gap = inch(0.75)
    if h < panel_t + foot_gap + slat_t:
        return False
    # Top panel.
    _add_prism_y(bm, _rect_poly(0.0, h - panel_t, w, h), 0.0, depth)
    # Slats centered: slot centerlines at 4" o.c.; a slat spans the 3"
    # between neighboring slots, plus half-slats closing the two ends.
    z1 = h - panel_t - foot_gap
    z0 = z1 - slat_t
    n_slots = max(1, _floor_count(w - inch(2.0), pitch))
    first_slot = w / 2.0 - (n_slots - 1) * pitch / 2.0
    edges = [0.0]
    for i in range(n_slots):
        cx = first_slot + i * pitch
        edges.extend([cx - inch(0.5), cx + inch(0.5)])
    edges.append(w)
    for i in range(0, len(edges), 2):
        x0, x1 = edges[i], edges[i + 1]
        if x1 - x0 > inch(0.25):
            _add_prism_y(bm, _rect_poly(x0, z0, x1, z1), 0.0, depth)
    return True


def _build_plate_rack(bm, w, h, depth):
    """PR: 3/8" birch dowels 2" on center, two ranks the plate stands
    between (cross-section shows ~4" between ranks)."""
    r = inch(0.1875)
    pitch = inch(2.0)
    n = max(2, _floor_count(w - inch(1.0), pitch) + 1)
    first_cx = w / 2.0 - (n - 1) * pitch / 2.0
    mid = depth / 2.0
    ys = [max(r + inch(0.25), mid - inch(2.0)),
          min(depth - r - inch(0.25), mid + inch(2.0))]
    octa = [(math.cos(a) * r, math.sin(a) * r)
            for a in [math.radians(22.5 + 45.0 * i) for i in range(8)]]
    for cy in ys:
        for i in range(n):
            cx = first_cx + i * pitch
            poly = [(cx + px, cy + py) for px, py in octa]
            _add_prism_z(bm, poly, 0.0, h)
    return True


_BUILDERS = {
    'WINE_CUBBY':       _build_wine_cubby,
    'WINE_CELLAR':      _build_wine_cellar,
    'WINE_LATTICE':     _build_wine_lattice,
    'WINE_X':           _build_wine_x,
    'WINE_DIAGONAL':    _build_wine_diagonal,
    'WINE_HALF_CIRCLE': _build_half_circle,
    'STEMWARE_RACK':    _build_stemware,
    'PLATE_RACK':       _build_plate_rack,
}


def build_bar_storage_object(kind, name, w, h, depth):
    """Build the insert mesh for a kind, or None when the opening is
    too small (or the kind unknown). The returned object is NOT linked
    to any collection; the caller links, parents, and tags it."""
    builder = _BUILDERS.get(kind)
    if builder is None or w <= 0.0 or h <= 0.0 or depth <= 0.0:
        return None
    bm = bmesh.new()
    ok = builder(bm, w, h, depth)
    if not ok or len(bm.faces) == 0:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return bpy.data.objects.new(name, mesh)
