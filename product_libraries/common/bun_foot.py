"""Bun feet: short turned or shaped feet set under the corners of a
cabinet that stands on them instead of on a plain toe kick.

Every style is a profile table: ``profile`` is (z, h) in inches, z up
from the floor to the top of the foot at its stock ``height``, h the
half-width of the section at that height. Consecutive rows at the same z
make a step (a flat shoulder). The section decides how h is drawn:

    ROUND  -- a turning: circle of radius h
    RECT   -- square / rectangular block: half-widths (h + dx, h + dy)
    TAPER  -- block tapered on its two inner faces only: the two outer
              faces stay plumb and the inner ones lean in, so the foot
              reads square from the front and the side

Meshes are built straight into a part's local box: x in [0, width],
y in [0, depth], z in [0, height] (width runs along the cabinet front).
``outer_x`` / ``outer_y`` say which side of the box faces out of the
cabinet ('MIN' or 'MAX'); only the TAPER section is handed, the others
are symmetric. The foot is stretched in z to the height asked for and
kept at its stock footprint.
"""

import math

import bmesh

from ...units import inch


# Stamped on a part whose mesh carries the foot; the cutpart box is
# kept as the size carrier with its display hidden.
STATIC_TAG = 'HB_STATIC_BUN_FOOT'
STYLE_TAG = 'HB_BUN_FOOT_STYLE'

RING_SEGMENTS = 48
SMOOTH_ANGLE = math.radians(35.0)

# Square Tulip and Tulip share one shape; Tulip is the same foot cut to
# a 4 x 2-1/2 rectangle.
_TULIP_PROFILE = (
    (0.0, 0.808), (0.376, 0.827), (0.749, 0.877), (1.117, 0.957),
    (1.274, 1.004), (1.428, 1.065), (1.574, 1.137), (1.713, 1.22),
    (1.848, 1.316), (2.072, 1.502), (2.182, 1.575), (2.296, 1.635),
    (2.415, 1.682), (2.541, 1.718), (2.667, 1.74), (2.798, 1.75),
    (2.928, 1.746), (3.015, 1.731), (3.098, 1.704), (3.178, 1.663),
    (3.25, 1.609), (3.313, 1.545), (3.365, 1.472), (3.402, 1.395),
    (3.43, 1.309), (3.571, 1.309), (3.594, 1.246), (3.641, 1.202),
    (3.704, 1.185), (3.77, 1.202), (3.817, 1.246), (3.839, 1.309),
    (3.995, 1.309), (4.003, 1.411), (4.024, 1.476), (4.057, 1.538),
    (4.107, 1.595), (4.166, 1.639), (4.231, 1.669), (4.304, 1.686),
    (4.377, 1.687), (4.448, 1.672), (4.517, 1.643), (4.575, 1.601),
    (4.625, 1.547),
)

# Keys are stable identifiers (append only -- files store the key).
STYLES = {
    'NOUVEAU': {
        'name': "Nouveau", 'section': 'RECT', 'height': 4.0,
        'profile': (
            (0.0, 1.125), (2.562, 1.906), (2.562, 1.813), (2.656, 1.813),
            (2.736, 1.641), (2.906, 1.563), (3.048, 1.421), (3.245, 1.421),
            (3.331, 1.506), (3.388, 1.584), (3.408, 1.875), (3.5, 1.875),
            (3.5, 2.0), (4.0, 2.0),
        ),
    },
    'APEX': {
        'name': "Apex", 'section': 'TAPER', 'height': 4.0,
        'profile': ((0.0, 0.6875), (4.0, 1.375)),
    },
    'SQUARE_LILLE': {
        'name': "Square Lille", 'section': 'RECT', 'height': 4.5,
        'profile': (
            (0.0, 1.238), (0.019, 1.307), (0.088, 1.382), (0.239, 1.396),
            (0.343, 1.373), (0.443, 1.32), (0.501, 1.269), (0.587, 1.134),
            (0.702, 1.118), (0.744, 1.04), (0.811, 0.988), (0.897, 0.966),
            (0.983, 0.981), (1.34, 1.288), (1.495, 1.404), (1.658, 1.511),
            (1.826, 1.607), (2.0, 1.693), (2.36, 1.831), (2.736, 1.924),
            (2.962, 1.943), (3.185, 1.92), (3.295, 1.893), (3.506, 1.808),
            (3.603, 1.751), (3.781, 1.612), (3.85, 1.624), (3.875, 1.773),
            (3.942, 1.882), (3.989, 1.926), (4.101, 1.984), (4.166, 1.998),
            (4.294, 1.989), (4.411, 1.935), (4.5, 1.845),
        ),
    },
    'CRAFTSMAN': {
        'name': "Craftsman", 'section': 'ROUND', 'height': 4.5,
        'profile': (
            (0.0, 0.888), (0.091, 0.912), (0.25, 0.985), (0.315, 1.069),
            (0.39, 1.215), (0.602, 1.215), (0.723, 1.34), (0.855, 1.446),
            (1.004, 1.537), (1.161, 1.606), (1.324, 1.655), (1.494, 1.682),
            (1.667, 1.687), (1.836, 1.669), (2.005, 1.63), (2.165, 1.569),
            (2.316, 1.489), (2.456, 1.389), (2.583, 1.271), (2.802, 1.271),
            (2.847, 1.096), (2.887, 1.037), (2.94, 0.973), (3.009, 0.925),
            (3.089, 0.898), (3.171, 0.892), (3.25, 0.904), (3.326, 0.939),
            (3.39, 0.979), (3.472, 1.122), (3.687, 1.122), (3.702, 1.277),
            (3.726, 1.322), (3.763, 1.355), (3.811, 1.375), (4.5, 1.375),
        ),
    },
    'KENSINGTON': {
        'name': "Kensington", 'section': 'RECT', 'height': 4.5,
        'profile': (
            (0.0, 1.34), (0.352, 1.425), (0.711, 1.479), (1.073, 1.5),
            (1.152, 1.496), (1.304, 1.463), (1.378, 1.434), (1.699, 1.235),
            (1.905, 1.16), (2.124, 1.13), (2.149, 1.235), (2.213, 1.319),
            (2.257, 1.35), (2.357, 1.379), (2.412, 1.377), (2.512, 1.34),
            (2.586, 1.267), (2.626, 1.167), (2.884, 1.251), (3.124, 1.375),
            (3.25, 1.375), (3.25, 1.5), (4.5, 1.5),
        ),
    },
    'TULIP': {
        'name': "Tulip", 'section': 'RECT', 'height': 4.625,
        'dx': 0.25, 'dy': -0.5,
        'profile': _TULIP_PROFILE,
    },
    'SQUARE_TULIP': {
        'name': "Square Tulip", 'section': 'RECT', 'height': 4.625,
        'profile': _TULIP_PROFILE,
    },
    'FURNITURE': {
        'name': "Furniture", 'section': 'ROUND', 'height': 4.625,
        'profile': (
            (0.0, 0.813), (0.478, 0.873), (0.713, 0.925), (0.945, 0.993),
            (1.168, 1.077), (1.387, 1.177), (1.595, 1.291), (2.106, 1.627),
            (2.231, 1.684), (2.359, 1.723), (2.491, 1.745), (2.623, 1.75),
            (2.756, 1.737), (2.886, 1.706), (3.007, 1.661), (3.124, 1.599),
            (3.228, 1.525), (3.374, 1.381), (3.524, 1.38), (3.553, 1.318),
            (3.653, 1.265), (3.713, 1.262), (3.769, 1.28), (3.851, 1.355),
            (3.999, 1.355), (4.037, 1.446), (4.093, 1.523), (4.169, 1.587),
            (4.257, 1.628), (4.352, 1.648), (4.449, 1.643), (4.541, 1.615),
            (4.625, 1.565),
        ),
    },
}

DEFAULT_STYLE = 'NOUVEAU'


def style_items():
    """EnumProperty items, in display order."""
    return [(key, s['name'], "") for key, s in STYLES.items()]


def _style(style_key):
    return STYLES.get(style_key) or STYLES[DEFAULT_STYLE]


def stock_height(style_key):
    """The foot's stock height (meters)."""
    return inch(_style(style_key)['height'])


def footprint(style_key):
    """(width, depth) of the foot's widest section (meters); width runs
    along the cabinet front."""
    s = _style(style_key)
    h = max(r for _z, r in s['profile'])
    if s['section'] == 'TAPER':
        return inch(2.0 * h), inch(2.0 * h)
    return (inch(2.0 * (h + s.get('dx', 0.0))),
            inch(2.0 * (h + s.get('dy', 0.0))))


def _ring(style, h, width, depth):
    """One section of the foot as a closed loop of (x, y) in the box,
    for the canonical hand (outer faces at x = 0 and y = 0)."""
    sec = style['section']
    cx, cy = width / 2.0, depth / 2.0
    if sec == 'ROUND':
        return [(cx + h * math.cos(a), cy + h * math.sin(a))
                for a in (2.0 * math.pi * i / RING_SEGMENTS
                          for i in range(RING_SEGMENTS))]
    if sec == 'TAPER':
        x0, x1, y0, y1 = 0.0, 2.0 * h, 0.0, 2.0 * h
    else:
        hx = h + inch(style.get('dx', 0.0))
        hy = h + inch(style.get('dy', 0.0))
        x0, x1, y0, y1 = cx - hx, cx + hx, cy - hy, cy + hy
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def build_bun_foot(mesh, style_key, height, outer_x='MIN', outer_y='MIN'):
    """Regenerate ``mesh`` as a ``style_key`` foot filling the box
    [0, width] x [0, depth] x [0, height] (width / depth from
    ``footprint``). The profile is stretched to ``height``."""
    style = _style(style_key)
    width, depth = footprint(style_key)
    zscale = height / inch(style['height'])

    bm = bmesh.new()
    rings = []
    for z, h in style['profile']:
        z = inch(z) * zscale
        rings.append([bm.verts.new((x, y, z))
                      for x, y in _ring(style, inch(h), width, depth)])
    for lower, upper in zip(rings, rings[1:]):
        n = len(lower)
        for j in range(n):
            k = (j + 1) % n
            bm.faces.new((lower[j], lower[k], upper[k], upper[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    # Steps leave coincident rings at a shoulder's inner edge only when
    # the profile repeats a row; merge any doubles so the shell is clean.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)

    flip_x = outer_x == 'MAX'
    flip_y = outer_y == 'MAX'
    if flip_x or flip_y:
        for v in bm.verts:
            x, y, z = v.co
            v.co = (width - x if flip_x else x,
                    depth - y if flip_y else y, z)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    # Turnings and curved block faces shade smooth; the block's corners
    # and shoulders stay crisp.
    try:
        mesh.set_sharp_from_angle(angle=SMOOTH_ANGLE)
    except AttributeError:
        pass
    mesh.update()


# ----------------------------------------------------------------------
# Cutpart hand-off
# ----------------------------------------------------------------------
def _cutpart_mod(obj):
    mod_name = getattr(getattr(obj, 'home_builder', None), 'mod_name', '')
    mod = obj.modifiers.get(mod_name) if mod_name else None
    if mod is not None:
        return mod
    for mod in obj.modifiers:
        if (mod.type == 'NODES' and mod.node_group
                and mod.node_group.name == 'GeoNodeCutpart'):
            return mod
    return None


def fit_cutpart(obj, style_key, height, outer_x='MIN', outer_y='MIN'):
    """Draw a foot into an unrotated cutpart: the cutpart keeps the box
    (Length = width along X, Width = depth along Y, Thickness = height
    along Z) for downstream reads, its display is hidden and the mesh
    carries the foot. Rebuilt only when the style, height or hand
    changed. Returns the (width, depth) the box was sized to."""
    from ... import hb_types
    width, depth = footprint(style_key)
    part = hb_types.GeoNodeCutpart(obj)
    part.set_input('Length', width)
    part.set_input('Width', depth)
    part.set_input('Thickness', height)

    sig = '%s|%.6f|%s|%s' % (style_key, height, outer_x, outer_y)
    if obj.get(STATIC_TAG) != sig or len(obj.data.vertices) == 0:
        build_bun_foot(obj.data, style_key, height, outer_x, outer_y)
        obj[STATIC_TAG] = sig
    obj[STYLE_TAG] = style_key
    mod = _cutpart_mod(obj)
    if mod is not None:
        mod.show_viewport = False
        mod.show_render = False
    return width, depth


def set_material(obj, mat):
    """The hidden cutpart can't paint the foot; put the finish on the
    mesh's own slot."""
    if mat is None or obj.type != 'MESH':
        return
    me = obj.data
    if len(me.materials) == 0:
        me.materials.append(mat)
    else:
        me.materials[0] = mat
