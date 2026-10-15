"""Tambour: a run of narrow slats set edge to edge along an arc, the way
an applied tambour wraps a curved corner.

A placed tambour is one static mesh object. Its frame: origin at the
start of the run on the floor plane (z = the bottom of the slats), local
X along the chord to the end point, local Z up. The run is an arc
through the two ends bowed ``sagitta`` off the chord along local Y (0 =
straight). Slats stand with their flat back on the arc and their face
toward ``face`` (+1 = local +Y side, -1 = local -Y side).

Everything that shapes it lives in custom properties on the object, so
the mesh can be rebuilt from them (``rebuild``) and a duplicate carries
its settings:

    TAMBOUR_CHORD, TAMBOUR_SAGITTA, TAMBOUR_FACE, TAMBOUR_HEIGHT (m)
    TAMBOUR_PROFILE        'HALF_ROUND' | 'FLAT'
    TAMBOUR_SLAT_WIDTH, TAMBOUR_SLAT_THICKNESS, TAMBOUR_GAP (m)

HALF_ROUND is a slat with a flat back, straight sides and a fully
rounded face (a bullnose); at a thickness of half its width or less it
is a plain half round. FLAT is a rectangle.
"""

import math

import bpy
import bmesh
from mathutils import Vector

from ...units import inch

TAMBOUR_TAG = 'IS_TAMBOUR'
MENU_ID = 'HOME_BUILDER_MT_tambour_commands'

PROFILE_ITEMS = (
    ('HALF_ROUND', "Half Round", "Flat back, rounded face"),
    ('FLAT', "Flat", "Rectangular slat"),
)

# Defaults per profile: (width, thickness).
PROFILE_DEFAULTS = {
    'HALF_ROUND': (inch(0.25), inch(0.25)),
    'FLAT': (inch(0.75), inch(0.25)),
}

ROUND_SEGMENTS = 8          # facets across a rounded face
MIN_SLAT = inch(1.0 / 32.0)

_PROPS = ('TAMBOUR_CHORD', 'TAMBOUR_SAGITTA', 'TAMBOUR_FACE',
          'TAMBOUR_HEIGHT', 'TAMBOUR_PROFILE', 'TAMBOUR_SLAT_WIDTH',
          'TAMBOUR_SLAT_THICKNESS', 'TAMBOUR_GAP')


# ---- the run ----------------------------------------------------------------

def arc_points(chord, sagitta, steps=64):
    """Points along the run in its local XY, start to end."""
    if abs(sagitta) < 1e-6 or chord <= 0.0:
        return [Vector((chord * i / steps, 0.0)) for i in range(steps + 1)]
    centre, radius, a0, sweep = _arc(chord, sagitta)
    return [centre + Vector((math.cos(a0 + sweep * i / steps),
                             math.sin(a0 + sweep * i / steps))) * radius
            for i in range(steps + 1)]


def _arc(chord, sagitta):
    """(centre, radius, start angle, signed sweep) of the arc through
    (0, 0) and (chord, 0) with its middle at (chord / 2, sagitta)."""
    half = chord / 2.0
    radius = (half * half + sagitta * sagitta) / (2.0 * abs(sagitta))
    cy = sagitta - math.copysign(radius, sagitta)
    centre = Vector((half, cy))
    a0 = math.atan2(-cy, -half)
    # Angle the run turns through: 2 x the half-angle of the chord, which
    # covers both a shallow bow and one deeper than a half circle.
    theta = 2.0 * math.atan2(half, radius - abs(sagitta))
    # Bowed toward +Y the run goes over the top of the circle, clockwise.
    sweep = -math.copysign(theta, sagitta)
    return centre, radius, a0, sweep


def arc_length(chord, sagitta):
    if abs(sagitta) < 1e-6:
        return chord
    _c, radius, _a0, sweep = _arc(chord, sagitta)
    return abs(sweep) * radius


def _frame_at(chord, sagitta, s):
    """(point, unit tangent) at arc length ``s`` from the start."""
    if abs(sagitta) < 1e-6:
        return Vector((s, 0.0)), Vector((1.0, 0.0))
    centre, radius, a0, sweep = _arc(chord, sagitta)
    a = a0 + math.copysign(s / radius, sweep)
    radial = Vector((math.cos(a), math.sin(a)))
    tangent = Vector((-radial.y, radial.x)) * math.copysign(1.0, sweep)
    return centre + radial * radius, tangent


def default_face(sagitta):
    """Which side the slat faces show on when nobody has said: the
    hollow side of a bowed run (where the arc's centre is), the -Y side
    of a straight one."""
    if abs(sagitta) < 1e-6:
        return -1
    return -1 if sagitta > 0 else 1


# ---- slats ------------------------------------------------------------------

def slat_profile(profile, width, thickness):
    """Closed outline (u across the width, v out from the back), counter-
    clockwise, back edge first."""
    hw = width / 2.0
    if profile == 'FLAT':
        return [(-hw, 0.0), (hw, 0.0), (hw, thickness), (-hw, thickness)]
    # Half round / bullnose: straight sides to where the round starts.
    r = hw
    side = max(thickness - r, 0.0)
    squash = min(thickness / r, 1.0) if r > 0 else 1.0
    pts = [(-hw, 0.0), (hw, 0.0)]
    for i in range(ROUND_SEGMENTS + 1):
        a = math.pi * i / ROUND_SEGMENTS
        pts.append((r * math.cos(a), side + r * math.sin(a) * squash))
    # The two ends of the round sit on the sides at v = side; with no
    # straight side they repeat the back corners.
    out = []
    for p in pts:
        if not out or (Vector(p) - Vector(out[-1])).length > 1e-9:
            out.append(p)
    if (Vector(out[0]) - Vector(out[-1])).length <= 1e-9:
        out.pop()
    return out


def slat_layout(chord, sagitta, width, gap):
    """Arc-length positions of slat centres: as many slats as fit at
    ``width + gap``, the pitch eased so the run ends flush both ends."""
    length = arc_length(chord, sagitta)
    pitch = max(width + gap, MIN_SLAT)
    n = max(1, int(round((length + gap) / pitch)))
    step = length / n
    return [step * (i + 0.5) for i in range(n)]


def read(obj):
    """The run's settings off ``obj``, defaults filled in."""
    profile = obj.get('TAMBOUR_PROFILE', 'HALF_ROUND')
    if profile not in PROFILE_DEFAULTS:
        profile = 'HALF_ROUND'
    dw, dt = PROFILE_DEFAULTS[profile]
    sagitta = float(obj.get('TAMBOUR_SAGITTA', 0.0))
    return {
        'chord': float(obj.get('TAMBOUR_CHORD', inch(12.0))),
        'sagitta': sagitta,
        'face': int(obj.get('TAMBOUR_FACE', default_face(sagitta))) or -1,
        'height': float(obj.get('TAMBOUR_HEIGHT', inch(34.5))),
        'profile': profile,
        'width': float(obj.get('TAMBOUR_SLAT_WIDTH', dw)),
        'thickness': float(obj.get('TAMBOUR_SLAT_THICKNESS', dt)),
        'gap': float(obj.get('TAMBOUR_GAP', 0.0)),
    }


def write(obj, settings):
    obj['TAMBOUR_CHORD'] = settings['chord']
    obj['TAMBOUR_SAGITTA'] = settings['sagitta']
    obj['TAMBOUR_FACE'] = 1 if settings['face'] > 0 else -1
    obj['TAMBOUR_HEIGHT'] = settings['height']
    obj['TAMBOUR_PROFILE'] = settings['profile']
    obj['TAMBOUR_SLAT_WIDTH'] = settings['width']
    obj['TAMBOUR_SLAT_THICKNESS'] = settings['thickness']
    obj['TAMBOUR_GAP'] = settings['gap']


def slat_count(settings):
    return len(slat_layout(settings['chord'], settings['sagitta'],
                           settings['width'], settings['gap']))


def build_into(mesh, settings):
    """Write the slats for ``settings`` into ``mesh`` (replacing it)."""
    width = max(settings['width'], MIN_SLAT)
    thickness = max(settings['thickness'], MIN_SLAT)
    height = max(settings['height'], MIN_SLAT)
    profile = slat_profile(settings['profile'], width, thickness)
    face = 1.0 if settings['face'] > 0 else -1.0
    bm = bmesh.new()
    uv = bm.loops.layers.uv.verify()
    for s in slat_layout(settings['chord'], settings['sagitta'], width,
                         settings['gap']):
        point, tangent = _frame_at(settings['chord'], settings['sagitta'], s)
        normal = Vector((-tangent.y, tangent.x)) * face
        ring = [point + tangent * u + normal * v for u, v in profile]
        # The ring must wind counter-clockwise seen from above so the
        # sides face out; mirroring by ``face`` reverses it.
        area = sum(a.x * b.y - b.x * a.y
                   for a, b in zip(ring, ring[1:] + ring[:1]))
        if area < 0:
            ring.reverse()
        low = [bm.verts.new((p.x, p.y, 0.0)) for p in ring]
        high = [bm.verts.new((p.x, p.y, height)) for p in ring]
        bm.faces.new(list(reversed(low)))
        bm.faces.new(high)
        n = len(ring)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((low[i], low[j], high[j], high[i]))
    # Box projection in metres, grain up the slats.
    for f in bm.faces:
        nz = abs(f.normal.z)
        for loop in f.loops:
            co = loop.vert.co
            if nz > 0.9:
                loop[uv].uv = (co.x, co.y)
            elif abs(f.normal.x) > abs(f.normal.y):
                loop[uv].uv = (co.y, co.z)
            else:
                loop[uv].uv = (co.x, co.z)
    mats = list(mesh.materials)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    for m in mats:
        mesh.materials.append(m)
    mesh.update()


def create(context, settings, name="Tambour"):
    """A new tambour object (linked to the active collection), at the
    origin with identity rotation; the caller places it."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    obj[TAMBOUR_TAG] = True
    obj['MENU_ID'] = MENU_ID
    write(obj, settings)
    build_into(mesh, settings)
    return obj


def rebuild(obj):
    """Rebuild ``obj``'s slats from its own settings. A duplicate shares
    nothing: the mesh is made single-user first."""
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    build_into(obj.data, read(obj))


def tambour_root(obj):
    while obj is not None:
        if obj.get(TAMBOUR_TAG):
            return obj
        obj = obj.parent
    return None


def profile_label(settings):
    return {k: label for k, label, _d in PROFILE_ITEMS}.get(
        settings['profile'], settings['profile'])
