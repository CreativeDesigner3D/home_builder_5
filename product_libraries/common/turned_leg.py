"""Turned legs: full-round furniture turnings that stand in for a square
leg post.

A turned leg is a square top block, a turned zone (the styled run:
beads, tapers, vase, optionally fluted or rope-twisted), and on some
styles a square foot block. Every style is a normalized profile table
measured off the vendor line drawings: ``profile`` is (z, r) with z the
fraction of the turned zone from its BOTTOM (0) to the underside of the
top block (1) and r the fraction of the blank's half-width, so one table
serves any blank size. ``total`` / ``block`` / ``foot`` are the vendor's
stock dimensions in inches; the leg is TRIMMED FROM THE TOP to the height
asked for (the top block shortens, the turning stays stock size), which is
how the legs are fitted on the bench.

Meshes are surfaces of revolution about the leg's own axis (canonical
frame: +Z up from the foot, origin at the bottom center); ``fit_cutpart``
drops one into a square-post cutpart's local box so the turning occupies
exactly the volume the post did, with the cutpart kept as the L/W/T
carrier (its box generator hidden) -- the same hand-off the profiled slab
fronts use.

Section modulations (all radius functions of theta, sheared by z for the
twist):
    flutes  -- concave grooves separated by lands over a zone
    rope    -- N-strand rope: lobed section swept helically over a zone
    twist   -- whole-turning helical shear (spiral / barley-twist legs);
               ``twist_turns`` per unit height, sign = handedness
    SQUARE  -- section is a square whose half-width follows the profile
               (tapered square legs)
"""

import math

import bpy
import bmesh
from mathutils import Vector

from ...units import inch


STATIC_TAG = 'HB_STATIC_TURNING'
STYLE_TAG = 'HB_TURNING_STYLE'

# Shortest top block worth keeping when a leg is trimmed; below this the
# turned zone compresses instead.
MIN_BLOCK = inch(1.5)

RING_SEGMENTS = 64
FLUTE_COUNT = 10
FLUTE_DEPTH = 0.10        # of the local radius
FLUTE_FILL = 0.68         # groove share of each pitch; the rest is land
ROPE_STRANDS = 4
ROPE_DEPTH = 0.18         # lobe depth, of the local radius
ROPE_HELIX_DEG = 45.0     # strand angle to the axis

SQUARE_STYLE = 'SQUARE'

# Vendor styles. Keys are stable identifiers (append only -- the combobox
# stores the index); ``blank`` is the stock square in inches.
STYLES = {
    'ENGLISH_COUNTRY': dict(
        name='English Country', blank=3.75, total=35.25, block=14.75, foot=0.0,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.0000, 0.2500), (0.0135, 0.7162), (0.0498, 0.9324), (0.0686, 0.9324),
            (0.0808, 0.8986), (0.1252, 0.6892), (0.1534, 0.7568), (0.1803, 0.9527),
            (0.2005, 0.9189), (0.2248, 0.7432), (0.2436, 0.8784), (0.2598, 0.9054),
            (0.2921, 0.7432), (0.3284, 0.7027), (0.3943, 0.6892), (0.4724, 0.7770),
            (0.5559, 0.9797), (0.5882, 0.9932), (0.6312, 0.9865), (0.6595, 0.9459),
            (0.7093, 0.8041), (0.7295, 0.8851), (0.7470, 0.8716), (0.7591, 0.8176),
            (0.7887, 0.9797), (0.7981, 1.0000), (0.8170, 1.0000), (0.8654, 0.7703),
            (0.8977, 0.7162), (0.9287, 0.7905), (0.9596, 0.9932), (0.9785, 1.0000),
            (0.9879, 0.9595), (1.0000, 1.0000),
        )),
    'FRENCH': dict(
        name='French', blank=3.75, total=35.25, block=12.75, foot=0.0,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.0000, 0.1849), (0.0157, 0.5068), (0.0617, 0.5479), (0.1063, 0.6781),
            (0.1549, 0.9863), (0.1706, 0.9726), (0.1798, 0.9863), (0.1942, 0.9726),
            (0.2152, 0.9863), (0.2520, 0.6986), (0.2808, 0.8082), (0.3412, 0.6027),
            (0.3688, 0.5342), (0.3924, 0.5137), (0.4226, 0.5137), (0.4606, 0.5822),
            (0.5656, 0.8973), (0.5997, 0.9521), (0.6680, 1.0000), (0.7441, 0.9589),
            (0.8005, 0.8493), (0.8202, 0.7808), (0.8373, 0.5205), (0.9094, 0.9932),
            (0.9423, 1.0000), (0.9606, 0.9452), (1.0000, 0.6781),
        )),
    'ESTATE': dict(
        name='Estate', blank=3.75, total=35.25, block=11.5, foot=0.0,
        section='ROUND', flutes=(0.12, 0.98), rope=None,
        profile=(
            (0.0000, 0.1206), (0.0092, 0.6099), (0.0358, 0.9362), (0.0555, 1.0000),
            (0.0798, 0.9220), (0.1052, 0.6596), (0.1387, 0.8369), (0.1503, 0.8298),
            (0.1642, 0.8511), (0.1850, 0.8440), (0.1861, 0.8582), (0.2092, 0.8582),
            (0.2358, 0.8865), (0.3040, 0.9007), (0.3387, 0.9362), (0.3595, 0.9291),
            (0.3746, 0.9433), (0.3815, 0.9291), (0.3861, 0.9504), (0.4220, 0.9433),
            (0.4370, 0.9574), (0.4821, 0.9574), (0.4855, 0.9716), (0.5815, 0.9787),
            (0.5965, 0.9929), (0.6324, 0.9858), (0.6532, 1.0000), (0.8347, 0.9716),
            (0.8809, 0.9787), (0.8994, 0.9574), (0.9260, 0.9645), (0.9630, 0.7518),
            (0.9792, 0.9787), (0.9908, 1.0000), (1.0000, 0.9645),
        )),
    'SQUARE_ESTATE': dict(
        name='Square Estate', blank=3.75, total=35.25, block=11.5, foot=0.0,
        section='SQUARE', flutes=None, rope=None,
        profile=(
            (0.0000, 0.0600), (0.0265, 0.6959), (0.0596, 0.9691), (0.0817, 0.8969),
            (0.1115, 0.6237), (0.1402, 0.7887), (0.2506, 0.8711), (0.4691, 0.9742),
            (0.4879, 0.9639), (0.5695, 0.9897), (0.6832, 0.9948), (0.8720, 0.9588),
            (0.9272, 0.9278), (0.9393, 0.9021), (0.9614, 0.7474), (1.0000, 0.9639),
        )),
    'LARGE_ENGLISH_COUNTRY': dict(
        name='Large English Country', blank=5.0, total=35.25, block=14.75, foot=0.0,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.0000, 0.1809), (0.0200, 0.7186), (0.0454, 0.8894), (0.0694, 0.9347),
            (0.0895, 0.9196), (0.1389, 0.6884), (0.1669, 0.7839), (0.1816, 0.9296),
            (0.1976, 0.9447), (0.2323, 0.7538), (0.2523, 0.8844), (0.2710, 0.8894),
            (0.2964, 0.7337), (0.3431, 0.6834), (0.3738, 0.6784), (0.4152, 0.7085),
            (0.4419, 0.7588), (0.5073, 0.9296), (0.5674, 0.9849), (0.6222, 0.9749),
            (0.6595, 0.9347), (0.7116, 0.8040), (0.7343, 0.8844), (0.7610, 0.8392),
            (0.7904, 0.9799), (0.8198, 0.9899), (0.8398, 0.9497), (0.8745, 0.7588),
            (0.9039, 0.7236), (0.9573, 0.9849), (0.9813, 0.9950), (0.9893, 0.9698),
            (1.0000, 1.0000),
        )),
    'FLUTED_CLASSIC': dict(
        name='Fluted Classic', blank=5.0, total=35.25, block=10.0, foot=4.5,
        section='ROUND', flutes=(0.23, 0.97), rope=None,
        profile=(
            (0.1782, 0.4825), (0.2138, 0.6974), (0.2206, 1.0000), (0.2319, 0.8421),
            (0.2353, 0.9605), (0.2432, 0.9254), (0.2896, 0.5175), (0.3201, 0.7456),
            (0.3462, 0.6272), (0.3688, 0.7500), (0.8812, 0.7500), (0.8959, 0.7456),
            (0.9140, 0.6272), (0.9412, 0.7456), (0.9717, 0.5175), (1.0000, 0.7149),
        )),
    'PLAIN_CLASSIC': dict(
        name='Plain Classic', blank=5.0, total=35.25, block=10.0, foot=4.5,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.1782, 0.4825), (0.2127, 0.6842), (0.2195, 1.0000), (0.2308, 0.8377),
            (0.2410, 0.9386), (0.2885, 0.5219), (0.3213, 0.7456), (0.3462, 0.6228),
            (0.3688, 0.7544), (0.8925, 0.7544), (0.9140, 0.6228), (0.9412, 0.7456),
            (0.9717, 0.5175), (1.0000, 0.7105),
        )),
    'ROPE_CLASSIC': dict(
        name='Rope Classic', blank=5.0, total=35.25, block=10.0, foot=4.5,
        section='ROUND', flutes=None, rope=(0.23, 0.97),
        profile=(
            (0.1782, 0.5256), (0.2184, 0.7222), (0.2299, 0.9957), (0.2391, 0.8248),
            (0.2425, 0.9658), (0.2506, 0.9359), (0.2977, 0.5342), (0.3218, 0.7179),
            (0.3402, 0.7265), (0.3575, 0.6325), (0.3759, 0.7650), (0.4161, 0.7650),
            (0.4437, 0.7137), (0.4713, 0.7650), (0.4897, 0.7650), (0.5172, 0.7137),
            (0.5483, 0.7692), (0.5644, 0.7650), (0.5885, 0.7179), (0.6195, 0.7692),
            (0.6345, 0.7692), (0.6621, 0.7179), (0.6920, 0.7692), (0.7115, 0.7650),
            (0.7345, 0.7179), (0.7621, 0.7650), (0.7828, 0.7650), (0.8069, 0.7179),
            (0.8402, 0.7692), (0.9000, 0.7650), (0.9184, 0.6239), (0.9345, 0.7222),
            (0.9402, 0.7350), (0.9529, 0.7265), (0.9770, 0.5385), (1.0000, 0.6838),
        )),
    'WILMINGTON': dict(
        name='Wilmington', blank=8.0, total=36.0, block=10.0, foot=0.0,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.0000, 0.1194), (0.0188, 0.5279), (0.0409, 0.5305), (0.0572, 0.5570),
            (0.0769, 0.7374), (0.1055, 0.8196), (0.1202, 0.8276), (0.1349, 0.8143),
            (0.1750, 0.6207), (0.1954, 0.7162), (0.2118, 0.7241), (0.2428, 0.5968),
            (0.7498, 0.9337), (0.7792, 0.8912), (0.8128, 0.7082), (0.8258, 0.7056),
            (0.8561, 0.7613), (0.8937, 0.9735), (0.9215, 0.9549), (0.9469, 0.7878),
            (0.9608, 0.7798), (1.0000, 1.0000),
        )),
    'ISLANDER': dict(
        name='Islander', blank=8.0, total=36.0, block=5.5, foot=7.0,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.2295, 1.0000), (0.2845, 0.6794), (0.3025, 0.6775), (0.3177, 0.5916),
            (0.3581, 0.5916), (0.3769, 0.6660), (0.4123, 0.6088), (0.8657, 0.7405),
            (0.8939, 0.7347), (0.9076, 0.7137), (0.9329, 0.6050), (0.9495, 0.6031),
            (0.9610, 0.6660), (0.9884, 0.6145), (1.0000, 0.8588),
        )),
    'CONCORD': dict(
        name='Concord', blank=8.0, total=36.0, block=10.0, foot=4.5,
        section='ROUND', flutes=None, rope=None,
        profile=(
            (0.1731, 1.0000), (0.2416, 0.9962), (0.2744, 0.8140), (0.2776, 0.9734),
            (0.2875, 0.7059), (0.2989, 0.7362), (0.3153, 0.7381), (0.3333, 0.6243),
            (0.3505, 0.5977), (0.3710, 0.6698), (0.3857, 0.6660), (0.4079, 0.6110),
            (0.8894, 0.7457), (0.9222, 0.7230), (0.9451, 0.6262), (0.9697, 0.5996),
            (0.9812, 0.6490), (0.9992, 0.6452), (1.0000, 0.8634),
        )),
}

STYLE_ORDER = (SQUARE_STYLE,) + tuple(STYLES)


def style_items():
    """Combobox labels, square post first, then the turnings by blank."""
    items = ['Square']
    for key in STYLES:
        s = STYLES[key]
        items.append('%s %s"' % (s['name'], _frac(s['blank'])))
    return items


def style_from_index(idx):
    try:
        return STYLE_ORDER[int(idx)]
    except (IndexError, ValueError, TypeError):
        return SQUARE_STYLE


def _frac(v):
    whole = int(v)
    rem = v - whole
    for d in (2, 4, 8, 16):
        n = round(rem * d)
        if abs(rem - n / d) < 1e-6:
            if n == 0:
                return str(whole)
            return '%d-%d/%d' % (whole, n, d) if whole else '%d/%d' % (n, d)
    return '%.2f' % v


# ----------------------------------------------------------------------
# Profile
# ----------------------------------------------------------------------
def _profile_r(profile, t):
    """Piecewise-linear r at fraction t of the turned zone."""
    if t <= profile[0][0]:
        return profile[0][1]
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        if t <= z1:
            if z1 - z0 < 1e-9:
                return r1
            u = (t - z0) / (z1 - z0)
            return r0 + (r1 - r0) * u
    return profile[-1][1]


def _zone_ts(profile, samples):
    """Sample fractions: every profile knot plus a uniform fill, so sharp
    beads keep their corners and long tapers stay smooth."""
    ts = {round(z, 5) for z, _ in profile}
    t0 = profile[0][0]
    for i in range(samples + 1):
        ts.add(round(t0 + (1.0 - t0) * i / samples, 5))
    return sorted(ts)


def _in_zone(zone, t, feather=0.02):
    """0..1 blend weight of a section modulation at fraction t: hard 1
    inside the zone, easing to 0 over ``feather`` at both ends."""
    if not zone:
        return 0.0
    z0, z1 = zone
    if t <= z0 or t >= z1:
        return 0.0
    e = min(t - z0, z1 - t)
    return min(1.0, e / feather) if feather > 0 else 1.0


def _rect_radius(half, deg):
    rad = math.radians(deg)
    c = abs(math.cos(rad))
    s = abs(math.sin(rad))
    return half / max(c, s, 1e-9)


def _section_radius(style, r, deg, t, twist_turns, height):
    """Radius at angle deg (0..360) for a ring at fraction t of the turned
    zone with base profile radius r."""
    if style['section'] == 'SQUARE':
        return _rect_radius(r, deg)
    out = r
    # helical shear for the twist and the rope: theta' = theta - k z
    z_abs = t * height
    if twist_turns:
        deg = deg - 360.0 * twist_turns * z_abs
    w = _in_zone(style.get('flutes'), t)
    if w > 0.0:
        pitch = 360.0 / FLUTE_COUNT
        u = (deg % pitch) / pitch
        if u < FLUTE_FILL:
            v = u / FLUTE_FILL
            out -= FLUTE_DEPTH * r * math.sin(math.pi * v) * w
    w = _in_zone(style.get('rope'), t)
    if w > 0.0:
        # strand helix: one full turn per 2*pi*r / tan(angle) of height
        pitch_len = 2.0 * math.pi * r / math.tan(math.radians(ROPE_HELIX_DEG))
        rot = 360.0 * (z_abs / pitch_len) if pitch_len > 1e-9 else 0.0
        lobe = 0.5 - 0.5 * math.cos(math.radians((deg - rot) * ROPE_STRANDS))
        out -= ROPE_DEPTH * r * lobe * w
    return out


# ----------------------------------------------------------------------
# Mesh
# ----------------------------------------------------------------------
def _add_box(verts, faces, x0, x1, y0, y1, z0, z1):
    b = len(verts)
    verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    faces.extend([(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                  (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5),
                  (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)])


def build_turned_leg(mesh, style_key, blank, height, twist_turns=0.0):
    """Regenerate ``mesh`` as a turned leg of ``style_key``: square top
    block over the turned zone (and foot block where the style has one),
    ``blank`` square, ``height`` tall, in the canonical frame (origin at
    the bottom center, +Z up). Trimmed from the top: the block takes up
    whatever the stock turned length leaves; a leg too short for the
    stock turning compresses the turning to keep MIN_BLOCK of block.
    ``twist_turns`` (turns per meter of turned zone) spirals the whole
    turned zone; sign is the handedness."""
    style = STYLES[style_key]
    half = blank / 2.0
    foot_h = inch(style['foot'])
    stock_turn = inch(style['total'] - style['block'])
    turn_len = min(stock_turn, max(height - MIN_BLOCK, inch(0.5)))
    if turn_len < foot_h + inch(0.5):
        foot_h = 0.0
    block_h = max(0.0, height - turn_len)

    verts = []
    faces = []
    profile = style['profile']
    degs = [360.0 * i / RING_SEGMENTS for i in range(RING_SEGMENTS)]
    rings = []
    t0 = profile[0][0]
    for t in _zone_ts(profile, 100):
        z = foot_h + (turn_len - foot_h) * ((t - t0) / max(1e-9, 1.0 - t0))
        r = _profile_r(profile, t) * half
        radii = [_section_radius(style, r, d, t, twist_turns, turn_len)
                 for d in degs]
        rings.append((z, radii))
    # loft
    base = len(verts)
    for z, radii in rings:
        for r, d in zip(radii, degs):
            a = math.radians(d)
            verts.append((r * math.cos(a), r * math.sin(a), z))
    n = RING_SEGMENTS
    for i in range(len(rings) - 1):
        a = base + i * n
        b = base + (i + 1) * n
        for j in range(n):
            k = (j + 1) % n
            faces.append((a + j, a + k, b + k, b + j))
    # end caps
    c0 = len(verts)
    verts.append((0.0, 0.0, rings[0][0]))
    for j in range(n):
        faces.append((c0, base + (j + 1) % n, base + j))
    c1 = len(verts)
    verts.append((0.0, 0.0, rings[-1][0]))
    top = base + (len(rings) - 1) * n
    for j in range(n):
        faces.append((c1, top + j, top + (j + 1) % n))
    # blocks -- flat-shaded; everything before this index is the turning
    n_turned_faces = len(faces)
    if block_h > 0.0:
        _add_box(verts, faces, -half, half, -half, half,
                 height - block_h, height)
    if foot_h > 0.0:
        _add_box(verts, faces, -half, half, -half, half, 0.0, foot_h)

    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    for i, p in enumerate(mesh.polygons):
        p.use_smooth = i < n_turned_faces
    mesh.update()


# ----------------------------------------------------------------------
# Cutpart hand-off
# ----------------------------------------------------------------------
def _cutpart_mod(obj):
    for mod in obj.modifiers:
        if (mod.type == 'NODES' and mod.node_group
                and mod.node_group.name == 'GeoNodeCutpart'):
            return mod
    return None


def _cutpart_box(obj):
    """(length, width, thickness, sx, sy, sz): the cutpart's inputs and
    the sign each runs along its local axis (Mirror flips to -1)."""
    from ... import hb_types
    part = hb_types.GeoNodeCutpart(obj)
    length = part.get_input('Length')
    width = part.get_input('Width')
    thick = part.get_input('Thickness')
    sx = -1.0 if part.get_input('Mirror X') else 1.0
    sy = -1.0 if part.get_input('Mirror Y') else 1.0
    sz = -1.0 if part.get_input('Mirror Z') else 1.0
    return length, width, thick, sx, sy, sz


def fit_cutpart(obj, style_key, twist_turns=0.0):
    """Turn a square-post cutpart into ``style_key``: build the turning
    into the object's own mesh inside the cutpart's local box (length =
    the leg height, width x thickness = the blank), hide the box
    generator, stamp the object. Square restores the plain post. Returns
    True when a turning was built."""
    if style_key == SQUARE_STYLE or style_key not in STYLES:
        clear_cutpart(obj)
        return False
    mod = _cutpart_mod(obj)
    if mod is None or obj.type != 'MESH':
        return False
    length, width, thick, sx, sy, sz = _cutpart_box(obj)
    if length <= 0.0 or width <= 0.0 or thick <= 0.0:
        return False
    blank = min(width, thick)
    build_turned_leg(obj.data, style_key, blank, length, twist_turns)

    # Canonical -> cutpart local. The length runs along local X (signed
    # sx); which end is UP depends on how the part is rotated: read the
    # world Z of the local length direction off the object's own basis
    # (placement rotates products about Z only, so the basis suffices and
    # no depsgraph evaluation is needed).
    length_dir = Vector((sx, 0.0, 0.0))
    up = (obj.matrix_basis.to_3x3() @ length_dir).z
    if up < 0.0:
        bottom = length_dir * length      # origin end is the top
        axis = -length_dir
    else:
        bottom = Vector((0.0, 0.0, 0.0))
        axis = length_dir
    center = Vector((0.0, sy * width / 2.0, sz * thick / 2.0))
    ey = Vector((0.0, 1.0, 0.0))
    ez = Vector((0.0, 0.0, 1.0))
    # canonical (x, y, z) -> local: z along the axis from the bottom,
    # (x, y) in the local Y/Z plane about the post's center
    for v in obj.data.vertices:
        cx, cy, cz = v.co
        v.co = bottom + center + axis * cz + ey * cx + ez * cy
    obj.data.update()

    mod.show_viewport = False
    mod.show_render = False
    obj[STATIC_TAG] = True
    obj[STYLE_TAG] = style_key
    sync_static_material(obj)
    return True


def clear_cutpart(obj):
    """Undo fit_cutpart: drop the static mesh + stamps, show the box
    generator again. No-op on a plain post."""
    if STATIC_TAG not in obj:
        return
    del obj[STATIC_TAG]
    if STYLE_TAG in obj:
        del obj[STYLE_TAG]
    if obj.type == 'MESH':
        obj.data.clear_geometry()
    mod = _cutpart_mod(obj)
    if mod is not None:
        mod.show_viewport = True
        mod.show_render = True


def sync_static_material(obj):
    """The box generator paints its faces from the cutpart's material
    inputs; a static turning has to carry the material itself. Mirror the
    Top Surface input into the mesh's single slot."""
    if STATIC_TAG not in obj or obj.type != 'MESH':
        return
    from ... import hb_types
    try:
        mat = hb_types.GeoNodeCutpart(obj).get_input('Top Surface')
    except Exception:
        mat = None
    if mat is None:
        return
    mesh = obj.data
    if len(mesh.materials) == 0:
        mesh.materials.append(mat)
    else:
        mesh.materials[0] = mat


# ----------------------------------------------------------------------
# Support frame integration
# ----------------------------------------------------------------------
LEG_STYLE_PROP = 'Leg Style'
PUBLISHED_STYLE_PROP = 'TURNED_LEG_STYLE'   # style key, only while turned
LEG_TWIST_PROP = 'Leg Twist'      # turns per meter of turned zone, signed
FRAME_LEG_NAMES = ('Front Left Leg', 'Front Right Leg',
                   'Back Left Leg', 'Back Right Leg')


def frame_leg_parts(frame_obj):
    for child in frame_obj.children:
        name = child.name.split('.')[0]
        if name in FRAME_LEG_NAMES and _cutpart_mod(child) is not None:
            yield child


def sync_frame_legs(frame_obj):
    """Apply the frame's Leg Style to its corner legs. Called from the
    prompts dialog on every change so leg size / height edits rebuild
    the turning; a frame without the property keeps square posts."""
    if LEG_STYLE_PROP not in frame_obj:
        return
    style_key = style_from_index(frame_obj.get(LEG_STYLE_PROP, 0))
    twist = float(frame_obj.get(LEG_TWIST_PROP, 0.0) or 0.0)
    for leg in frame_leg_parts(frame_obj):
        fit_cutpart(leg, style_key, twist)
    # Publish the applied style on the root so downstream consumers
    # (drawings, reports) read what was built rather than the raw index.
    if style_key != SQUARE_STYLE:
        frame_obj[PUBLISHED_STYLE_PROP] = style_key
    elif PUBLISHED_STYLE_PROP in frame_obj:
        del frame_obj[PUBLISHED_STYLE_PROP]


def size_frame_legs_from_style(frame_obj):
    """Picking a turned style sizes the frame's legs to the style's stock
    blank (the vendor turns them square at that size); Square leaves the
    user's sizes alone."""
    style_key = style_from_index(frame_obj.get(LEG_STYLE_PROP, 0))
    if style_key == SQUARE_STYLE:
        return
    blank = inch(STYLES[style_key]['blank'])
    frame_obj['Leg Width'] = blank
    frame_obj['Leg Depth'] = blank
