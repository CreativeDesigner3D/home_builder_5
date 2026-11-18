"""Inserts carried along a molding run: dentil blocks and twisted rope.

A swept molding shows the same section all along its run, so detail
that repeats along the length - the teeth of a dentil, the twist of a
rope - cannot live in the profile. A profile that carries such an
insert says so with custom properties:

    hb_molding_insert   'DENTIL' or 'ROPE'
    hb_sweep_base       the profile the run is swept with (the molding
                        without its insert), in the same category
    hb_insert_pocket    (x0, y0, x1, y1): where the insert sits, in
                        profile coordinates (metres)
    hb_dentil_width / hb_dentil_gap      tooth width and gap
    hb_rope_radius / hb_rope_lay         rope radius and twist length

The profile's own outline still draws the insert in a section; the run
is swept with the base outline and the insert is built here as a mesh
along each straight stretch, cut to the mitres at the corners.

Coordinates are the sweep's local frame: a run's plan points with the
section's x to the right of the direction of travel and its y up (how
a 2D curve lays out its bevel object).
"""

import math

import bmesh
import bpy
from mathutils import Vector

INSERT_TAG = 'IS_HB_MOLDING_INSERT'
KINDS = ('DENTIL', 'ROPE')

_ROPE_SEGMENTS = 16
_ROPE_STEP = 0.0254 / 8.0
_ROPE_DEPTH = 0.12       # how deep the strands' grooves run, of the radius
_ROPE_STRANDS = 3


def insert_spec(profile):
    """The insert a profile object carries, as a dict, or None."""
    if profile is None:
        return None
    kind = profile.get('hb_molding_insert')
    pocket = profile.get('hb_insert_pocket')
    if kind not in KINDS or pocket is None or len(pocket) != 4:
        return None
    spec = {'kind': kind, 'pocket': tuple(float(v) for v in pocket),
            'base': profile.get('hb_sweep_base')}
    for key in ('hb_dentil_width', 'hb_dentil_gap', 'hb_rope_radius',
                'hb_rope_lay'):
        if key in profile:
            spec[key[3:]] = float(profile[key])
    return spec


def _segments(points, cyclic):
    """[(A, B, t, R, m_start, m_end)] for each straight stretch: its ends,
    direction, right normal, and the plan normals of the planes it is cut
    to at each end (the mitre bisector at a corner, square at an open
    end). All 2D Vectors."""
    pts = [Vector((p[0], p[1])) for p in points]
    n = len(pts)
    if n < 2:
        return []
    count = n if cyclic else n - 1
    dirs = []
    for i in range(count):
        d = pts[(i + 1) % n] - pts[i]
        dirs.append(d.normalized() if d.length > 1e-9 else None)
    out = []
    for i in range(count):
        t = dirs[i]
        if t is None:
            continue
        prev = dirs[i - 1] if (cyclic or i > 0) else None
        nxt = dirs[(i + 1) % count] if (cyclic or i < count - 1) else None
        m0 = (prev + t).normalized() if prev is not None and (prev + t).length > 1e-6 else t
        m1 = (t + nxt).normalized() if nxt is not None and (t + nxt).length > 1e-6 else t
        out.append((pts[i], pts[(i + 1) % n], t, Vector((t.y, -t.x)), m0, m1))
    return out


def _span(seg, px):
    """(s0, s1): where the line ``px`` to the right of a stretch meets
    its end planes, measured along the stretch from its start."""
    a, b, t, r, m0, m1 = seg
    s0 = -px * r.dot(m0) / t.dot(m0)
    s1 = (b - a).length - px * r.dot(m1) / t.dot(m1)
    return s0, s1


def _dentil(bm, seg, spec):
    x0, y0, x1, y1 = spec['pocket']
    width = spec.get('dentil_width', 0.01905)
    gap = spec.get('dentil_gap', 0.009525)
    a, _b, t, r, _m0, _m1 = seg
    s_lo = max(_span(seg, x0)[0], _span(seg, x1)[0])
    s_hi = min(_span(seg, x0)[1], _span(seg, x1)[1])
    room = s_hi - s_lo
    n = int(math.floor((room + gap) / (width + gap) + 1e-9))
    if n < 1:
        return 0
    start = s_lo + (room - (n * width + (n - 1) * gap)) / 2.0
    for k in range(n):
        s = start + k * (width + gap)
        verts = []
        for ss in (s, s + width):
            for px in (x0, x1):
                p = a + t * ss + r * px
                for z in (y0, y1):
                    verts.append(bm.verts.new((p.x, p.y, z)))
        for idx in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                    (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            bm.faces.new([verts[i] for i in idx])
    return n


def _rope(bm, seg, spec):
    """A half-round rope on the pocket's back face, twisted: its radius
    dips in _ROPE_STRANDS grooves that wind along it once per lay."""
    x0, y0, _x1, y1 = spec['pocket']
    radius = spec.get('rope_radius', (y1 - y0) / 2.0)
    lay = spec.get('rope_lay', 0.03175)
    zc = (y0 + y1) / 2.0
    a, _b, t, r, _m0, _m1 = seg
    thetas = [-math.pi / 2.0 + math.pi * i / _ROPE_SEGMENTS
              for i in range(_ROPE_SEGMENTS + 1)]
    # Every vertex runs between its own end planes, so the rope's ends
    # lie on the mitres.
    ends = []
    for th in thetas:
        px = x0 + radius * math.cos(th)
        ends.append(_span(seg, px))
    length = max(e[1] - e[0] for e in ends)
    if length <= 0.0:
        return 0
    steps = max(2, int(math.ceil(length / _ROPE_STEP)))
    rings = []
    for i in range(steps + 1):
        u = i / steps
        ring = []
        for th, (s0, s1) in zip(thetas, ends):
            s = s0 + u * (s1 - s0)
            twist = 2.0 * math.pi * s / lay
            rr = radius * (1.0 - _ROPE_DEPTH * 0.5
                           * (1.0 - math.cos(_ROPE_STRANDS * th - twist)))
            px = x0 + rr * math.cos(th)
            pz = zc + rr * math.sin(th)
            p = a + t * s + r * px
            ring.append(bm.verts.new((p.x, p.y, pz)))
        rings.append(ring)
    last = len(thetas) - 1
    for ra, rb in zip(rings, rings[1:]):
        for k in range(last):
            bm.faces.new((ra[k], rb[k], rb[k + 1], ra[k + 1]))
        bm.faces.new((ra[last], rb[last], rb[0], ra[0]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    return 1


def build(sweep, spec, runs, material=None):
    """Build the insert along ``runs`` ([(local points, cyclic)] in the
    sweep's frame) as a mesh parented to ``sweep``. Returns the object,
    or None when nothing fits."""
    bm = bmesh.new()
    made = 0
    for points, cyclic in runs:
        for seg in _segments(points, cyclic):
            if spec['kind'] == 'DENTIL':
                made += _dentil(bm, seg, spec)
            else:
                made += _rope(bm, seg, spec)
    if not made:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    name = 'MoldingInsert'
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if spec['kind'] == 'ROPE':
        for poly in mesh.polygons:
            poly.use_smooth = True
    if material is not None:
        mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    for coll in sweep.users_collection:
        coll.objects.link(obj)
    obj[INSERT_TAG] = True
    obj.parent = sweep
    return obj
