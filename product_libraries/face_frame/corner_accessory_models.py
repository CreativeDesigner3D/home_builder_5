"""3D models for corner cabinet accessories, built procedurally.

Two families:

- Rotating susans inside a pie-cut or diagonal corner cabinet, driven by
  the cabinet's ``interior_option``. Trays come in the product's own
  diameters (20" to 32") and are NOT stretched to the cabinet: the tray
  size is picked from the cabinet width, stepped down only when it
  would not fit, and the unit is centered in the cavity. Pie-cut
  cabinets get a notched tray (90 degree notch facing the doors, sharp
  for revolving-door sets, rounded for kidney sets); diagonal cabinets
  get full-round trays.

    pole sets      2+ trays on a chrome center shaft (count by height)
    super susans   two heavy trays on bearings: floor and mid height
    not so lazy    lower rimmed tray, upper shelf with pan hooks and a
                   mid-level arrester rail, on a center shaft

- Blind corner swing-outs behind the door of a blind corner cabinet,
  from an ACCESSORY interior item whose product entry (published by the
  host application through accessory_registry) names one of
  ``OPENING_MODELS`` in its ``model`` field:

    blind_swingout   half-moon shelves on a post at the opening edge,
                     half in the blind area and half behind the door.
                     ``model_params``: finish ('polymer' / 'wood'),
                     sizes ([[min_opening_w, shelf_w, shelf_len], ...]
                     in inches; the largest size the opening takes is
                     used), tiers.
    blind_lemans     obround shelves pivoting on a post at the open end
                     of the opening, reaching into the blind area.
                     ``model_params``: shelf_width, shelf_length, tiers.
    magic_corner     a pair of front baskets centered in the opening and
                     a pair of rear baskets beside them in the blind
                     area, joined by the steel linkage on a post at the
                     open side. Baskets have wood floors and chrome
                     rails. ``model_params``: front_basket and
                     rear_basket ([width, depth] in inches), tiers.

Every model is ONE derived mesh with role ACCESSORY_MODEL: a purchased
unit, not a CABINET_PART, so cut lists and machining skip it. The susan
is parented to the corner cabinet root and rebuilt by its recalc; the
swing-out is parented to the opening and rebuilt by the interior wipe.
Material slot 0 is the tray (almond polymer or maple), slot 1 chrome.
"""

import math

import bpy
import bmesh

from ... import hb_utils
from . import accessory_materials
from ...units import inch

ROLE = 'ACCESSORY_MODEL'
# Marks the susan built by the corner recalc (so only it is replaced).
CORNER_KEY = 'hb_corner_accessory'
OPENING_KIND = 'CORNER_ACCESSORY_MODEL'
OPENING_MODELS = frozenset({'blind_swingout', 'blind_lemans',
                            'magic_corner'})

_MAT_POLYMER = ('Accessory Almond Polymer', (0.90, 0.86, 0.76, 1.0), 0.0, 0.45)
_MAT_MAPLE = ('Accessory Maple', (0.86, 0.72, 0.52, 1.0), 0.0, 0.5)
_MAT_CHROME = ('Accessory Chrome', (0.72, 0.74, 0.77, 1.0), 0.9, 0.2)

# Tray sections (deck thickness, overall rim height, rim thickness).
_POLY_TRAY = (inch(0.25), inch(1.0), inch(0.25))
_WOOD_TRAY = (inch(0.625), inch(1.625), inch(0.5))

SHAFT_R = inch(0.5)
HUB_R = inch(1.0)
HUB_H = inch(0.75)
WALL_CLEAR = inch(0.5)      # tray rim to carcass / face frame
KIDNEY_ROUND = inch(2.5)    # inside-corner radius of a kidney notch
POLE_WRAP = inch(2.5)       # tray radius kept round the shaft at the notch
MIN_DIAMETER = inch(14.0)

# interior_option -> (style, finish, notch kind in a pie-cut cabinet)
SUSAN_OPTIONS = {
    'POLYMER_KIDNEY_SUSANS_POLE': ('POLE', 'POLYMER', 'KIDNEY'),
    'WOOD_KIDNEY_SUSANS_POLE':    ('POLE', 'WOOD', 'KIDNEY'),
    'POLYMER_PIE_CUT_REVOLVING':  ('REVOLVING', 'POLYMER', 'PIE'),
    'WOOD_PIE_CUT_REVOLVING':     ('REVOLVING', 'WOOD', 'PIE'),
    'SUPER_SUSANS':               ('SUPER', 'WOOD', 'PIE'),
    'NOT_SO_LAZY_SUSANS':         ('NOT_SO_LAZY', 'WOOD', 'KIDNEY'),
}


# ---------------------------------------------------------------------------
# Sizing
# ---------------------------------------------------------------------------

def susan_diameter(style, cabinet_type, width):
    """Nominal tray diameter (inches) for a susan set in a corner cabinet
    ``width`` (meters) wide, before any fit check. Base sets step up at a
    34" cabinet; upper sets follow the cabinet width."""
    w = width / inch(1.0)
    if style == 'REVOLVING':
        return 28.0
    if cabinet_type == 'UPPER':
        if style == 'SUPER':
            return 20.0 if w <= 20.0 else (28.0 if w <= 28.0 else 32.0)
        return 20.0 if w <= 24.0 else 28.0
    if style in ('SUPER', 'NOT_SO_LAZY'):
        return 32.0 if w >= 34.0 - 1e-6 else 28.0
    return 28.0 if w >= 34.0 - 1e-6 else 24.0


def _pie_center(R, x_lo, y_lo, fx, fy, outer_x, outer_y, clip):
    """Center (x, y depth-positive) and notch offsets for a pie-cut tray
    of radius R: as close to the middle of the cavity as the back walls
    and the doors allow, the notch faces just behind the doors. None
    when it does not fit."""
    s_nom = 0.23 * R
    out = []
    for lo, front, outer in ((x_lo, fx, outer_x), (y_lo, fy, outer_y)):
        lo = lo + R
        if front < lo:
            return None
        hi = front - s_nom
        s = front - ((lo + hi) / 2.0 if hi > lo else lo)
        c = front - min(s, 0.45 * R)
        if c + R > outer:
            return None
        out.append(c)
    cx, cy = out
    # Clipped back corner: keep the tray off the angled back.
    if clip > 0.0 and (cx + cy - clip) / math.sqrt(2.0) < R + WALL_CLEAR:
        return None
    return cx, cy, fx - cx, fy - cy


def _diagonal_center(R, x_lo, y_lo, line, outer_x, outer_y, clip):
    """Center for a full-round tray in a diagonal cabinet: slid out along
    the corner bisector to the middle of the room between the back walls
    and the face frame. ``line`` is (nx, ny, d): n . p <= d keeps a
    point behind the frame (y depth-positive)."""
    nx, ny, d = line
    bx, by = x_lo + R, y_lo + R
    slack = d - (nx * bx + ny * by) - R
    if slack < 0.0:
        return None
    k = slack / (nx + ny) / 2.0
    cx, cy = bx + k, by + k
    if cx + R > outer_x or cy + R > outer_y:
        return None
    if clip > 0.0 and (cx + cy - clip) / math.sqrt(2.0) < R + WALL_CLEAR:
        return None
    return cx, cy, None, None


def susan_layout(cab_props, corner_type, cabinet_type, l_scribe=0.0,
                 r_scribe=0.0):
    """Placement for the cabinet's susan option, or None (no option /
    nothing fits). Coordinates are cabinet-root local: origin at the
    back corner, x along the right arm, -y along the left arm."""
    spec = SUSAN_OPTIONS.get(getattr(cab_props, 'interior_option', 'NONE'))
    if spec is None or corner_type not in ('PIE_CUT', 'DIAGONAL'):
        return None
    style, finish, notch = spec
    if corner_type == 'DIAGONAL':
        notch = None
    t = cab_props.material_thickness
    fft = cab_props.face_frame_thickness
    width, depth = cab_props.width, cab_props.depth
    ld, rd = cab_props.left_depth, cab_props.right_depth
    x_lo = l_scribe + t + WALL_CLEAR
    y_lo = r_scribe + t + WALL_CLEAR
    outer_x = width - t - WALL_CLEAR
    outer_y = depth - t - WALL_CLEAR
    clip = max(getattr(cab_props, 'clip_back_amount', 0.0), 0.0)
    if clip > 0.0:
        clip += t

    if corner_type == 'DIAGONAL':
        # Face frame runs from (ld, depth) to (width, rd); its back face
        # sits fft behind that line.
        ax, ay, bx, by = ld, depth, width, rd
        nx, ny = by - ay, ax - bx
        n = math.hypot(nx, ny)
        if n < 1e-9:
            return None
        nx, ny = nx / n, ny / n
        if nx * ax + ny * ay < 0.0:
            nx, ny = -nx, -ny
        line = (nx, ny, nx * ax + ny * ay - fft - WALL_CLEAR)

    D = susan_diameter(style, cabinet_type, width)
    while D * inch(1.0) >= MIN_DIAMETER - 1e-6:
        R = D * inch(1.0) / 2.0
        if corner_type == 'PIE_CUT':
            fit = _pie_center(R, x_lo, y_lo, ld - fft - WALL_CLEAR,
                              rd - fft - WALL_CLEAR, outer_x, outer_y,
                              clip)
        else:
            fit = _diagonal_center(R, x_lo, y_lo, line, outer_x, outer_y,
                                   clip)
        if fit is not None:
            cx, cy, sx, sy = fit
            return {'style': style, 'finish': finish, 'notch': notch,
                    'diameter': D, 'radius': R, 'center': (cx, -cy),
                    'notch_offsets': (sx, sy)}
        D -= 2.0
    return None


def _interior_z(cab_props, cabinet_type, has_kick):
    """(floor, ceiling) of the corner cavity, root-local z."""
    t = cab_props.material_thickness
    brw = cab_props.bottom_rail_width
    kick = cab_props.toe_kick_height if has_kick else 0.0
    floor = kick + brw
    ceil = cab_props.height - t - max(cab_props.top_scribe, 0.0)
    return floor, ceil


# ---------------------------------------------------------------------------
# Outlines
# ---------------------------------------------------------------------------

def _arc(cx, cy, rx, ry, a0, a1, step=math.radians(6.0)):
    n = max(2, int(math.ceil(abs(a1 - a0) / step)))
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n),
             cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def _tray_outline(R, notch, sx, sy):
    """Closed CCW outline of a susan tray centered on the origin. The
    notch removes {x > sx, y < -sy} (it faces the cabinet's doors). A
    notch reaching in to the shaft wraps round it; otherwise a kidney
    notch has a rounded inside corner and a pie cut a sharp one."""
    if notch is None:
        pts = _arc(0.0, 0.0, R, R, 0.0, 2.0 * math.pi)
        return pts[:-1]
    a0 = math.atan2(-sy, math.sqrt(max(R * R - sy * sy, 0.0)))
    a1 = math.atan2(-math.sqrt(max(R * R - sx * sx, 0.0)), sx)
    if a1 <= a0:
        a1 += 2.0 * math.pi
    pts = _arc(0.0, 0.0, R, R, a0, a1)
    rp = POLE_WRAP
    if sx < rp - inch(0.05) and sy < rp - inch(0.05):
        t1 = math.atan2(-math.sqrt(rp * rp - sx * sx), sx)
        t2 = math.atan2(-sy, math.sqrt(rp * rp - sy * sy))
        return pts + _arc(0.0, 0.0, rp, rp, t1, t2,
                          step=math.radians(10.0))
    rk = 0.0
    if notch == 'KIDNEY':
        rk = max(0.0, min(
            KIDNEY_ROUND,
            math.sqrt(max(R * R - sx * sx, 0.0)) - sy - inch(0.5),
            math.sqrt(max(R * R - sy * sy, 0.0)) - sx - inch(0.5)))
    if rk > inch(0.1):
        pts += _arc(sx + rk, -sy - rk, rk, rk, math.pi, math.pi / 2.0,
                    step=math.radians(15.0))
    else:
        pts.append((sx, -sy))
    return pts


def _offset(poly, d):
    """Offset a CCW polygon inward by d (mitered)."""
    n = len(poly)
    out = []
    for i in range(n):
        px, py = poly[i - 1]
        cx, cy = poly[i]
        qx, qy = poly[(i + 1) % n]
        e1 = (cx - px, cy - py)
        e2 = (qx - cx, qy - cy)
        l1 = math.hypot(*e1) or 1.0
        l2 = math.hypot(*e2) or 1.0
        n1 = (-e1[1] / l1, e1[0] / l1)
        n2 = (-e2[1] / l2, e2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        if bl < 1e-9:
            bx, by, scale = n1[0], n1[1], d
        else:
            bx, by = bx / bl, by / bl
            cos_h = bx * n1[0] + by * n1[1]
            scale = d / max(cos_h, 0.3)
        out.append((cx + bx * scale, cy + by * scale))
    return out


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def _slab(bm, poly, z0, z1, mi=0, dx=0.0, dy=0.0):
    if z1 - z0 <= 1e-6 or len(poly) < 3:
        return
    lo = [bm.verts.new((x + dx, y + dy, z0)) for x, y in poly]
    hi = [bm.verts.new((x + dx, y + dy, z1)) for x, y in poly]
    bm.faces.new(list(reversed(lo))).material_index = mi
    bm.faces.new(hi).material_index = mi
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i])).material_index = mi


def _band(bm, outer, inner, z0, z1, mi=0, dx=0.0, dy=0.0, closed=True):
    """Wall between two matching loops (a tray rim)."""
    if z1 - z0 <= 1e-6:
        return
    def ring(poly, z):
        return [bm.verts.new((x + dx, y + dy, z)) for x, y in poly]
    ol, oh = ring(outer, z0), ring(outer, z1)
    il, ih = ring(inner, z0), ring(inner, z1)
    n = len(outer)
    last = n if closed else n - 1
    for i in range(last):
        j = (i + 1) % n
        for f in ((ol[i], ol[j], oh[j], oh[i]),     # outer face
                  (ih[i], ih[j], il[j], il[i]),     # inner face
                  (oh[i], oh[j], ih[j], ih[i]),     # top
                  (il[i], il[j], ol[j], ol[i])):    # bottom
            bm.faces.new(f).material_index = mi
    if not closed:
        for k in (0, n - 1):
            q = (ol[k], il[k], ih[k], oh[k]) if k == 0 else \
                (oh[k], ih[k], il[k], ol[k])
            bm.faces.new(q).material_index = mi


def _cylinder(bm, cx, cy, r, z0, z1, mi=1, seg=16):
    poly = _arc(cx, cy, r, r, 0.0, 2.0 * math.pi,
                step=2.0 * math.pi / seg)[:-1]
    _slab(bm, poly, z0, z1, mi)


def _box(bm, x0, x1, y0, y1, z0, z1, mi=1):
    _slab(bm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mi)


def _tray(bm, poly, z0, section, mi=0, dx=0.0, dy=0.0):
    deck, rim_h, rim_t = section
    _slab(bm, poly, z0, z0 + deck, mi, dx, dy)
    _band(bm, poly, _offset(poly, rim_t), z0 + deck - inch(0.01),
          z0 + rim_h, mi, dx, dy)


def _rail_along(bm, pts, z, size=inch(0.1875), mi=1):
    """Square chrome rod following an open polyline at height z."""
    h = size / 2.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        ux, uy = dx / L, dy / L
        px, py = -uy * h, ux * h
        quad = [(x0 + px - ux * h, y0 + py - uy * h),
                (x0 - px - ux * h, y0 - py - uy * h),
                (x1 - px + ux * h, y1 - py + uy * h),
                (x1 + px + ux * h, y1 + py + uy * h)]
        _slab(bm, list(reversed(quad)) if _area(quad) < 0 else quad,
              z - h, z + h, mi)


def _area(poly):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1)
                     in zip(poly, poly[1:] + poly[:1]))


# ---------------------------------------------------------------------------
# Susan builders (local origin: tray center on the cavity floor)
# ---------------------------------------------------------------------------

def _susan_pole(bm, lay, height):
    R = lay['radius']
    sx, sy = lay['notch_offsets']
    poly = _tray_outline(R, lay['notch'], sx, sy)
    section = _POLY_TRAY if lay['finish'] == 'POLYMER' else _WOOD_TRAY
    h_in = height / inch(1.0)
    tiers = max(2, min(4, int(h_in // 12.0)))
    if lay['style'] == 'REVOLVING':
        tiers = 2
    base = inch(1.5)
    pitch = (height - base) / tiers
    _cylinder(bm, 0.0, 0.0, SHAFT_R, 0.0, height, seg=20)
    _cylinder(bm, 0.0, 0.0, HUB_R * 1.6, 0.0, inch(0.25), seg=24)
    for i in range(tiers):
        z = base + i * pitch
        _cylinder(bm, 0.0, 0.0, HUB_R, z - HUB_H, z, seg=20)
        _tray(bm, poly, z, section)


def _susan_super(bm, lay, height):
    R = lay['radius']
    sx, sy = lay['notch_offsets']
    poly = _tray_outline(R, lay['notch'], sx, sy)
    bearing = inch(0.5)
    ring_r = max(inch(4.0), 0.3 * R)
    for z in (0.0, height / 2.0):
        _cylinder(bm, 0.0, 0.0, ring_r, z, z + bearing, seg=32)
        _tray(bm, poly, z + bearing, _WOOD_TRAY)


def _susan_not_so_lazy(bm, lay, height):
    R = lay['radius']
    sx, sy = lay['notch_offsets']
    poly = _tray_outline(R, lay['notch'], sx, sy)
    shelf_t = inch(0.75)
    top = height - shelf_t
    _cylinder(bm, 0.0, 0.0, SHAFT_R, 0.0, height, seg=20)
    _cylinder(bm, 0.0, 0.0, HUB_R, inch(0.5), inch(1.25), seg=20)
    _tray(bm, poly, inch(1.25), _WOOD_TRAY)
    _slab(bm, poly, top, top + shelf_t, 0)
    # Pan hooks hang from the upper shelf along its round edge; the
    # arrester rail at mid level keeps the hanging pans from swinging.
    a0 = math.atan2(-sy, math.sqrt(max(R * R - sy * sy, 0.0)))
    a1 = math.atan2(-math.sqrt(max(R * R - sx * sx, 0.0)), sx)
    if a1 <= a0:
        a1 += 2.0 * math.pi
    pad = math.radians(12.0)
    hook_r = R - inch(1.25)
    hook_len = inch(2.5)
    for k in range(7):
        a = a0 + pad + (a1 - a0 - 2.0 * pad) * k / 6.0
        hx, hy = hook_r * math.cos(a), hook_r * math.sin(a)
        s = inch(0.125)
        _box(bm, hx - s, hx + s, hy - s, hy + s, top - hook_len, top)
        ox, oy = math.cos(a) * inch(0.75), math.sin(a) * inch(0.75)
        _box(bm, min(hx, hx + ox) - s, max(hx, hx + ox) + s,
             min(hy, hy + oy) - s, max(hy, hy + oy) + s,
             top - hook_len, top - hook_len + 2 * s)
    rail_r = R - inch(0.5)
    z_rail = height * 0.5
    arc = _arc(0.0, 0.0, rail_r, rail_r, a0 + pad / 2.0, a1 - pad / 2.0)
    _rail_along(bm, arc, z_rail)
    for a in (arc[0], arc[len(arc) // 2], arc[-1]):
        _cylinder(bm, a[0], a[1], inch(0.125), z_rail, top, seg=8)


_SUSAN_BUILDERS = {
    'POLE': _susan_pole,
    'REVOLVING': _susan_pole,
    'SUPER': _susan_super,
    'NOT_SO_LAZY': _susan_not_so_lazy,
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


def _finish_object(bm, name, finish):
    if not bm.faces:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(_material(
        _MAT_POLYMER if finish == 'POLYMER' else _MAT_MAPLE))
    mesh.materials.append(_material(_MAT_CHROME))
    return hb_utils.new_object(name, mesh)


def build_susan(lay, height, name="Corner Susan"):
    """Unlinked mesh object for a susan layout (see susan_layout)."""
    if lay is None or height <= inch(4.0):
        return None
    bm = bmesh.new()
    _SUSAN_BUILDERS[lay['style']](bm, lay, height)
    return _finish_object(bm, name, lay['finish'])


_SUSAN_NAMES = {
    'POLE': "Susans on Pole", 'REVOLVING': "Revolving Susans",
    'SUPER': "Super Susans", 'NOT_SO_LAZY': "Not So Lazy Susan",
}


def reconcile_corner_susan(cab_obj, cab_props, corner_type, cabinet_type,
                           has_kick, l_scribe=0.0, r_scribe=0.0):
    """Rebuild the corner cabinet's susan model from its interior option.
    Drops any previous one first, so recalcs never stack copies."""
    for child in list(cab_obj.children):
        if child.get(CORNER_KEY):
            data = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.meshes.remove(data)
    lay = susan_layout(cab_props, corner_type, cabinet_type,
                       l_scribe, r_scribe)
    if lay is None:
        return None
    floor, ceil = _interior_z(cab_props, cabinet_type, has_kick)
    name = '%d" %s' % (round(lay['diameter']), _SUSAN_NAMES[lay['style']])
    obj = build_susan(lay, ceil - floor, name)
    if obj is None:
        return None
    for coll in cab_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = cab_obj
    obj.location = (lay['center'][0], lay['center'][1], floor)
    obj['hb_part_role'] = ROLE
    obj[CORNER_KEY] = cab_props.interior_option
    obj['hb_accessory_size'] = lay['diameter']
    return obj


# ---------------------------------------------------------------------------
# Blind corner swing-outs (opening interior items)
# ---------------------------------------------------------------------------

def model_for(code):
    """(model, params) named by the product entry for ``code`` when it is
    one of this module's opening models, else None."""
    if not code:
        return None
    from ... import accessory_registry
    entry = accessory_registry.find(code)
    if not entry or entry.get('model') not in OPENING_MODELS:
        return None
    params = entry.get('model_params') or {}
    return entry['model'], (params if isinstance(params, dict) else {})


def _f(params, key, default):
    try:
        return float(params.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def descriptor(rect, cage_dim_y, item, front_y, back_setback):
    """Descriptor for a swing-out item in opening-local space (x right,
    y back from the cage front, z up), or None. The blind side is the
    one whose frame edge sits far in from the cage edge."""
    spec = model_for(getattr(item, 'accessory_code', ''))
    if spec is None:
        return None
    model, params = spec
    cage_x = rect['cage_dim_x']
    rev_l = max(0.0, rect.get('reveal_left', 0.0))
    rev_r = max(0.0, rect.get('reveal_right', 0.0))
    rev_b = max(0.0, rect.get('reveal_bottom', 0.0))
    rev_t = max(0.0, rect.get('reveal_top', 0.0))
    open_w = cage_x - rev_l - rev_r
    open_h = rect['cage_dim_z'] - rev_b - rev_t
    room_y = cage_dim_y - front_y - back_setback
    if open_w <= inch(1.0) or open_h <= inch(4.0) or room_y <= inch(4.0):
        return None
    blind_left = rev_l >= rev_r
    if model == 'magic_corner':
        return _magic_corner_descriptor(rect, item, params, front_y, room_y,
                                        open_w, open_h, blind_left)
    if model == 'blind_swingout':
        sizes = params.get('sizes') or [[12.0, 14.0, 33.0]]
        try:
            sizes = sorted((float(a), float(b), float(c)) for a, b, c in sizes)
        except (TypeError, ValueError):
            sizes = [(12.0, 14.0, 33.0)]
        pick = sizes[0]
        for s in sizes:
            if open_w >= inch(s[0]) - inch(0.01):
                pick = s
        shelf_w, shelf_len = inch(pick[1]), inch(pick[2])
        # The post stands at the opening edge on the blind side; the
        # shelf's flat edge centers on it, half in the blind area.
        post_x = rev_l if blind_left else cage_x - rev_r
        x0 = post_x - shelf_len / 2.0
    else:
        post_x = 0.0
        shelf_w = inch(_f(params, 'shelf_width', 18.0))
        shelf_len = inch(_f(params, 'shelf_length', 34.5))
        # Pivots at the open end of the opening, reaching into the blind.
        if blind_left:
            x0 = cage_x - rev_r - inch(1.0) - shelf_len
        else:
            x0 = rev_l + inch(1.0)
    shelf_len = min(shelf_len, cage_x - inch(0.5))
    x0 = min(max(x0, inch(0.25)), cage_x - inch(0.25) - shelf_len)
    shelf_w = min(shelf_w, room_y - inch(1.0))
    if shelf_w <= inch(2.0) or shelf_len <= inch(2.0):
        return None
    label = getattr(item, 'accessory_label', '') or item.accessory_code
    finish = str(params.get('finish', 'wood')).upper()
    return {
        'kind':     OPENING_KIND,
        'role':     ROLE,
        'name':     '%s Model' % label,
        'model':    model,
        'finish':   'POLYMER' if finish == 'POLYMER' else 'WOOD',
        'tiers':    int(_f(params, 'tiers', 2)),
        'blind_left': blind_left,
        'post_u':   (post_x - x0) if model == 'blind_swingout' else None,
        'position': (x0, front_y + inch(1.0), rev_b),
        'dims':     (shelf_len, shelf_w, open_h),
    }


def _magic_corner_descriptor(rect, item, params, front_y, room_y, open_w,
                             open_h, blind_left):
    """Front baskets centered in the opening hole, rear baskets beside
    them toward the blind side; each at its catalog size, clipped to the
    cavity."""
    cage_x = rect['cage_dim_x']
    rev_l = max(0.0, rect.get('reveal_left', 0.0))
    rev_b = max(0.0, rect.get('reveal_bottom', 0.0))

    def size(key, default):
        try:
            w, d = (float(v) for v in params.get(key, default))
        except (TypeError, ValueError):
            w, d = default
        return inch(w), inch(d)
    fw, fd = size('front_basket', (18.5, 15.375))
    rw, rd = size('rear_basket', (15.75, 15.375))
    fw = min(fw, open_w - inch(1.0))
    gap = inch(0.75)
    fx0 = rev_l + (open_w - fw) / 2.0
    if blind_left:
        rx0 = max(inch(0.5), fx0 - gap - rw)
        rw = min(rw, fx0 - gap - rx0)
        x0, x1 = rx0, fx0 + fw
    else:
        rx0 = fx0 + fw + gap
        rw = min(rw, cage_x - inch(0.5) - rx0)
        x0, x1 = fx0, rx0 + max(rw, 0.0)
    depth = min(max(fd, rd), room_y - inch(1.0))
    if fw <= inch(4.0) or depth <= inch(4.0) or open_h <= inch(6.0):
        return None
    label = getattr(item, 'accessory_label', '') or item.accessory_code
    return {
        'kind':     OPENING_KIND,
        'role':     ROLE,
        'name':     '%s Model' % label,
        'model':    'magic_corner',
        'finish':   'WOOD',
        'tiers':    int(_f(params, 'tiers', 2)),
        'blind_left': blind_left,
        'post_u':   None,
        # Basket spans along x, local to the unit: (u0, u1, depth).
        'front':    (fx0 - x0, fx0 - x0 + fw, min(fd, depth)),
        'rear':     ((rx0 - x0, rx0 - x0 + rw, min(rd, depth))
                     if rw > inch(4.0) else None),
        'position': (x0, front_y + inch(0.75), rev_b),
        'dims':     (x1 - x0, depth, open_h),
    }


def _basket(bm, u0, u1, d, z, rail_h=inch(2.5)):
    """Wood-floored basket with chrome rails round three sides and a
    lower front rail."""
    t = inch(0.5)
    _box(bm, u0, u1, 0.0, d, z, z + t, 0)
    r = inch(0.125)
    zt = z + t + rail_h
    corners = [(u0 + r, r), (u0 + r, d - r), (u1 - r, d - r), (u1 - r, r)]
    _rail_along(bm, corners, zt)
    _rail_along(bm, corners, z + t + rail_h * 0.5)
    for cx, cy in corners:
        _box(bm, cx - r, cx + r, cy - r, cy + r, z + t, zt + r)
    _rail_along(bm, [(u0 + r, r), (u1 - r, r)], z + t + inch(1.0))


def _build_magic_corner(bm, desc):
    L, A, H = desc['dims']
    tiers = max(1, min(3, desc['tiers']))
    pitch = min(max((H - inch(4.0)) / tiers, inch(8.0)), inch(14.0))
    levels = [inch(1.5) + pitch * i for i in range(tiers)
              if inch(1.5) + pitch * i + inch(3.0) <= H]
    fu0, fu1, fd = desc['front']
    for z in levels:
        _basket(bm, fu0, fu1, fd, z)
        if desc['rear'] is not None:
            ru0, ru1, rd = desc['rear']
            _basket(bm, ru0, ru1, rd, z)
    # Post at the open side of the front baskets with the linkage arms
    # running across to the rear baskets.
    post_u = fu1 + inch(0.75) if desc['blind_left'] else fu0 - inch(0.75)
    post_u = min(max(post_u, inch(0.5)), L - inch(0.5))
    top = (levels[-1] + inch(4.0)) if levels else H
    _box(bm, post_u - inch(0.5), post_u + inch(0.5), inch(1.0), inch(2.0),
         0.0, min(top, H))
    if desc['rear'] is not None:
        ru0, ru1, _rd = desc['rear']
        for z in levels:
            za = z - inch(0.5)
            u_a, u_b = sorted((post_u, (ru0 + ru1) / 2.0))
            _box(bm, u_a, u_b, A * 0.5 - inch(0.25), A * 0.5 + inch(0.25),
                 za, za + inch(0.375))


def _build_swingout(bm, desc):
    if desc.get('model') == 'magic_corner':
        _build_magic_corner(bm, desc)
        return
    L, A, H = desc['dims']
    section = _POLY_TRAY if desc['finish'] == 'POLYMER' else _WOOD_TRAY
    if desc['model'] == 'blind_swingout':
        # Half moon: flat edge at the front, arc to the back.
        poly = _arc(L / 2.0, 0.0, L / 2.0, A, 0.0, math.pi)
        post = (desc.get('post_u') or L / 2.0, -inch(0.5))
    else:
        # Obround shelf, post at the end nearest the open side.
        r = A / 2.0
        poly = (_arc(L - r, r, r, r, -math.pi / 2.0, math.pi / 2.0)
                + _arc(r, r, r, r, math.pi / 2.0, 1.5 * math.pi))
        post = ((L - r, r) if desc['blind_left'] else (r, r))
    tiers = max(1, min(4, desc['tiers']))
    pitch = min(max((H - inch(4.0)) / tiers, inch(7.0)), inch(12.0))
    top = min(H, inch(0.5) + pitch * (tiers - 1) + inch(6.0))
    _cylinder(bm, post[0], post[1], SHAFT_R, 0.0, top, seg=16)
    for i in range(tiers):
        z = inch(0.5) + pitch * i
        if z + section[1] > H:
            break
        _tray(bm, poly, z, section)
        _cylinder(bm, post[0], post[1], HUB_R * 0.8, z, z + section[1],
                  seg=16)


def attach_opening_model(opening_obj, desc):
    """Build, link and parent a swing-out descriptor's model."""
    bm = bmesh.new()
    _build_swingout(bm, desc)
    obj = _finish_object(bm, desc['name'], desc['finish'])
    if obj is None:
        return None
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = opening_obj
    obj.location = desc['position']
    obj['hb_part_role'] = desc['role']
    obj['IS_FACE_FRAME_INTERIOR_PART'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_interior_part_commands'
    return obj
