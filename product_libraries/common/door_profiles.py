"""
Door profile loading for the python-built door path.

Profiles ship as .blend files under face_frame_assets/door_profiles,
one curve object per file, drawn as a section through the cutter at
real-world scale. The loader appends the curve, applies the object's
baked transform (several assets carry rotations, offsets, or negative
scales), samples the bezier splines to a polyline, and projects onto
the section plane. Results are cached per file modification time, so
editing a profile .blend takes effect on the next build.

Raw sections are in drawing coordinates; edge_profile_section() turns
an OUTER / INNER section into sweep space -- u across the face from
the member edge, v through the thickness from the front face -- and
fits it to the door's actual thickness by stretching only the straight
run behind the cutter shape, so the cutter geometry is preserved no
matter what stock the profile was drawn against.
"""

import math
import os

import bpy
from mathutils import Matrix, Vector


PROFILE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'face_frame', 'face_frame_assets', 'door_profiles')

PROFILE_DIRS = {
    'OUTER': 'Outer Profiles',
    'INNER': 'Inner Profiles',
    'PANEL': 'Panel Profiles',
    'APPLIED': 'Applied Profiles',
    'MITERED': 'Mitered Profiles',
}

_cache = {}


def profile_path(category, name):
    return os.path.join(PROFILE_ROOT, PROFILE_DIRS[category], name + '.blend')


def list_profiles(category):
    """Sorted profile names (blend file stems) for a category; [] when
    the folder is missing."""
    folder = os.path.join(PROFILE_ROOT, PROFILE_DIRS[category])
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.splitext(f)[0] for f in os.listdir(folder)
                  if f.lower().endswith('.blend'))


def _sample_spline(sp, res):
    """Sample one spline to a point list (curve-local 3D tuples)."""
    pts = []
    if sp.type == 'BEZIER':
        bp = sp.bezier_points
        n = len(bp)
        if n == 0:
            return pts, False
        segs = n if sp.use_cyclic_u else n - 1
        for i in range(segs):
            a = bp[i]
            b = bp[(i + 1) % n]
            p0 = Vector(a.co)
            p1 = Vector(a.handle_right)
            p2 = Vector(b.handle_left)
            p3 = Vector(b.co)
            for s in range(res):
                t = s / res
                mt = 1.0 - t
                p = (p0 * (mt ** 3) + p1 * (3.0 * mt * mt * t)
                     + p2 * (3.0 * mt * t * t) + p3 * (t ** 3))
                pts.append(tuple(p))
        if not sp.use_cyclic_u:
            pts.append(tuple(bp[-1].co))
    else:
        pts = [tuple(p.co[:3]) for p in sp.points]
    return pts, bool(sp.use_cyclic_u)


def load_profile(category, name, res=16):
    """Load a profile section from its .blend.

    Returns a dict:
      points  -- [(a, b), ...] section polyline in the drawing plane,
                 object transform applied, consecutive duplicates dropped
      cyclic  -- True when the source spline is a closed loop
      name / category

    The longest spline wins when a file carries more than one. Raises
    FileNotFoundError for a missing file, ValueError for a file with no
    usable curve.
    """
    path = profile_path(category, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    key = (path, os.path.getmtime(path), res)
    if key in _cache:
        return _cache[key]

    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    best = None
    best_cyclic = False
    try:
        for ob in data_to.objects:
            if ob is None or ob.type != 'CURVE':
                continue
            m = Matrix.LocRotScale(ob.location, ob.rotation_euler, ob.scale)
            for sp in ob.data.splines:
                pts, cyclic = _sample_spline(sp, res)
                pts = [tuple(m @ Vector(p)) for p in pts]
                if best is None or len(pts) > len(best):
                    best = pts
                    best_cyclic = cyclic
    finally:
        for ob in data_to.objects:
            if ob is not None:
                cu = ob.data if ob.type == 'CURVE' else None
                bpy.data.objects.remove(ob)
                if cu is not None and cu.users == 0:
                    bpy.data.curves.remove(cu)
    if not best:
        raise ValueError("no curve in %s" % path)

    # Project onto the section plane: keep the two axes with the largest
    # extents (axis order preserved), require the dropped axis flat.
    ext = [max(p[i] for p in best) - min(p[i] for p in best)
           for i in range(3)]
    drop = ext.index(min(ext))
    keep = [i for i in range(3) if i != drop]
    pts2 = [(p[keep[0]], p[keep[1]]) for p in best]
    # A mirrored object transform (negative scale) reverses winding /
    # direction; that is fine -- consumers key off geometry, not order.
    out = []
    for p in pts2:
        if not out or abs(p[0] - out[-1][0]) > 1e-7 or abs(p[1] - out[-1][1]) > 1e-7:
            out.append(p)
    if best_cyclic and len(out) > 1 \
            and abs(out[0][0] - out[-1][0]) < 1e-7 \
            and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    result = dict(points=out, cyclic=best_cyclic, name=name,
                  category=category)
    _cache[key] = result
    return result


def _bbox_edges_of(p, ax0, ax1, ay0, ay1, ta, tb):
    e = set()
    if abs(p[0] - ax0) <= ta:
        e.add(('x', ax0))
    if abs(p[0] - ax1) <= ta:
        e.add(('x', ax1))
    if abs(p[1] - ay0) <= tb:
        e.add(('y', ay0))
    if abs(p[1] - ay1) <= tb:
        e.add(('y', ay1))
    return e


def _closed_cut_chain(pts):
    """Split a closed cutter-region outline into its cut curve and the
    two closing runs along the stock boundary.

    The Pulito-era Inside* drawings are the material chip bounded by
    the member's front face and the opening edge plane: two straight
    runs on perpendicular bbox edges meeting at the stock corner, plus
    the cut curve. Returns (chain, x_run_edge, y_run_edge) -- the cut
    curve point list plus the ('x'|'y', coordinate) identity of each
    closing run -- or None when no such corner exists."""
    n = len(pts)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax0, ax1, ay0, ay1 = min(xs), max(xs), min(ys), max(ys)
    ta = (ax1 - ax0) * 1e-3 + 1e-9
    tb = (ay1 - ay0) * 1e-3 + 1e-9
    seg = []
    for i in range(n):
        common = (_bbox_edges_of(pts[i], ax0, ax1, ay0, ay1, ta, tb)
                  & _bbox_edges_of(pts[(i + 1) % n], ax0, ax1, ay0, ay1, ta, tb))
        seg.append(sorted(common)[0] if common else None)

    def runs_from(i):
        """Walk the closing runs out from a candidate corner: returns
        (i0, i1, combined geometric length)."""
        ep = seg[(i - 1) % n]
        en = seg[i]
        j0 = i
        for _ in range(n):
            if seg[(j0 - 1) % n] != ep:
                break
            j0 = (j0 - 1) % n
        j1 = i
        for _ in range(n):
            if seg[j1 % n] != en:
                break
            j1 = (j1 + 1) % n
        j1 %= n
        length = (abs(pts[i][0] - pts[j0][0]) + abs(pts[i][1] - pts[j0][1])
                  + abs(pts[j1][0] - pts[i][0]) + abs(pts[j1][1] - pts[i][1]))
        return j0, j1, length

    # Chip drawings anchor the member's front-face / edge corner at the
    # ORIGIN (face on y=0, edge on x=0), so the closing corner is the
    # candidate whose runs lie on lines through the origin; combined
    # run length breaks any remaining tie (a cut shoulder on the bbox
    # can fake a second corner, and a quirk as deep as the edge run
    # makes the lengths alone ambiguous).
    corner = None
    best = None
    for i in range(n):
        ep = seg[(i - 1) % n]
        en = seg[i]
        if ep and en and ep[0] != en[0]:
            j0, j1, length = runs_from(i)
            off = abs(ep[1]) + abs(en[1])
            score = (off, -length)
            if best is None or score < best:
                best = score
                corner = i
                i0, i1 = j0, j1
    if corner is None:
        return None
    ep = seg[(corner - 1) % n]
    en = seg[corner]
    chain = []
    j = i1
    for _ in range(n + 1):
        chain.append(pts[j])
        if j == i0:
            break
        j = (j + 1) % n
    x_run = en if en[0] == 'x' else ep
    y_run = en if en[0] == 'y' else ep
    if x_run[0] != 'x' or y_run[0] != 'y':
        return None
    return chain, x_run, y_run


def sticking_section(profile, thickness):
    """INNER profile -> sweep section, same output as
    edge_profile_section (which handles the open DIP_* drawings).

    Closed drawings (the Pulito-era Inside* set) are the cutter chip:
    the closing run on a y-extreme is the member's front face, the run
    on an x-extreme the opening edge plane, and the remaining chain
    the cut. The section is closed down the opening wall to the door
    back."""
    if not profile['cyclic']:
        return edge_profile_section(profile, thickness)
    r = _closed_cut_chain(profile['points'])
    if r is None:
        return edge_profile_section(profile, thickness)
    chain, x_run, y_run = r
    edge_u = x_run[1]
    front_v = y_run[1]
    sec = [(abs(p[0] - edge_u), abs(p[1] - front_v)) for p in chain]
    if sec[0][1] > sec[-1][1]:
        sec.reverse()
    sec = [(u, min(v, thickness)) for (u, v) in sec]
    if sec[-1][1] < thickness - 1e-9:
        sec.append((sec[-1][0], thickness))
    return sec


def panel_profile_section(profile, max_depth):
    """PANEL profile -> raised-panel sweep data:
    dict(points=[(u, v), ...], field_u).

    u is measured inward from the panel edge, v behind the FIELD plane
    (the panel's front-most surface), points ordered field end first.
    Open DPP_* drawings carry a back-face run (full width on a
    y-extreme) plus the tongue end; closed PanelProfile* drawings are
    the removed chip -- the cut, the edge-plane run, and a rough line
    along the stock face. Depth is clamped to max_depth so a thick
    drawn panel cannot poke out the back of the door. Returns None
    when the drawing cannot be read."""
    pts = list(profile['points'])
    if len(pts) < 3:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax0, ax1, ay0, ay1 = min(xs), max(xs), min(ys), max(ys)
    ta = (ax1 - ax0) * 1e-3 + 1e-9
    tb = (ay1 - ay0) * 1e-3 + 1e-9

    def runs_on(seq, cyclic):
        """(edge, start, stop) for each straight run of >=1 segment on
        a bbox edge."""
        n = len(seq)
        segs = n if cyclic else n - 1
        out = []
        i = 0
        while i < segs:
            common = (_bbox_edges_of(seq[i], ax0, ax1, ay0, ay1, ta, tb)
                      & _bbox_edges_of(seq[(i + 1) % n], ax0, ax1, ay0, ay1, ta, tb))
            if not common:
                i += 1
                continue
            e = sorted(common)[0]
            j = i
            while j < segs:
                c2 = (_bbox_edges_of(seq[j % n], ax0, ax1, ay0, ay1, ta, tb)
                      & _bbox_edges_of(seq[(j + 1) % n], ax0, ax1, ay0, ay1, ta, tb))
                if e not in c2:
                    break
                j += 1
            out.append((e, i, j % n))
            i = j + 1
        return out

    if profile['cyclic']:
        # Remove the edge-plane run (an x-extreme), then split the rest
        # at the field point -- the point farthest from the edge.
        x_runs = [r for r in runs_on(pts, True) if r[0][0] == 'x']
        if not x_runs:
            return None
        e, i0, i1 = max(x_runs, key=lambda r: (r[2] - r[1]) % len(pts))
        edge_x = e[1]
        n = len(pts)
        chain = []
        j = i1
        for _ in range(n + 1):
            chain.append(pts[j])
            if j == i0:
                break
            j = (j + 1) % n
        k = max(range(len(chain)), key=lambda i: abs(chain[i][0] - edge_x))
        a, b = chain[:k + 1], chain[k:]
        field_y = chain[k][1]
        dev = lambda c: max(abs(p[1] - field_y) for p in c) if len(c) > 1 else 0.0
        cut = a if dev(a) > dev(b) else b
    else:
        # Open drawing: strip the back-face run (a y-extreme, joining
        # the edge), leaving the chain from the edge-back corner over
        # the tongue and raise to the field.
        y_runs = [r for r in runs_on(pts, False) if r[0][0] == 'y']
        cut = pts
        edge_x = None
        if y_runs:
            e, i0, i1 = max(y_runs, key=lambda r: r[2] - r[1])
            if i0 == 0:
                cut = pts[i1:]
                edge_x = pts[i1][0]
            elif i1 == len(pts) - 1:
                cut = pts[:i0 + 1]
                edge_x = pts[i0][0]
        if edge_x is None:
            return None
        field_y = cut[0][1] if abs(cut[0][0] - edge_x) > abs(cut[-1][0] - edge_x) \
            else cut[-1][1]
    if len(cut) < 2:
        return None

    sec = [(abs(p[0] - edge_x), p[1]) for p in cut]
    vs = [field_y - p[1] for p in sec]
    if sum(vs) < 0.0:
        vs = [-v for v in vs]
    sec = [(sec[i][0], max(vs[i], 0.0)) for i in range(len(sec))]
    if sec[0][0] < sec[-1][0]:
        sec.reverse()
    v_max = max(v for (u, v) in sec)
    if v_max > max_depth > 0.0:
        k = max_depth / v_max
        sec = [(u, v * k) for (u, v) in sec]
    return dict(points=sec, field_u=sec[0][0])


def sticking_strip(profile, thickness, panel_front=None):
    """INNER profile -> applied sticking strip cross-section.

    Frames stay rectangular parts; the sticking is a separate molding
    loop swept around each opening perimeter. The strip's FRONT surface
    is the profile curve flipped into the opening -- u >= 0 from the
    member's edge toward the opening, v from the front face -- closed
    down the opening-side wall, along the bottom, and up the member
    contact face. The bottom sits at ``panel_front`` when given (a
    recessed panel's plane) else at the curve's own deepest point.
    Returns a CLOSED counter-clockwise loop [(u, v), ...]."""
    sec = sticking_section(profile, thickness)
    if not sec:
        return None
    w = max(u for u, v in sec)
    if w <= 1e-9:
        return None
    curve = [(w - u, v) for (u, v) in sec]
    # Trim the straight run to the door back that sticking_section
    # appends / the drawing carries at the opening edge: the strip ends
    # at the curve's own depth (or the panel plane), not the door back.
    while len(curve) > 1 and curve[-1][0] >= w - 1e-9 \
            and curve[-2][0] >= w - 1e-9:
        curve.pop()
    vb = panel_front if panel_front is not None \
        else max(v for u, v in curve)
    vb = min(vb, thickness)
    curve = [(u, min(v, vb)) for (u, v) in curve]
    loop = []
    for p in curve:
        if not loop or abs(p[0] - loop[-1][0]) > 1e-9 \
                or abs(p[1] - loop[-1][1]) > 1e-9:
            loop.append(p)
    if len(loop) < 2:
        return None
    if loop[-1][1] < vb - 1e-9:
        loop.append((loop[-1][0], vb))
    if loop[-1][0] > 1e-9:
        loop.append((0.0, vb))
    if abs(loop[0][0]) > 1e-9 or abs(loop[0][1]) > 1e-9:
        loop.insert(0, (0.0, 0.0))
    # counter-clockwise in (u, v)
    area = 0.0
    n = len(loop)
    for i in range(n):
        a = loop[i]
        b = loop[(i + 1) % n]
        area += a[0] * b[1] - b[0] * a[1]
    if area < 0.0:
        loop.reverse()
    return loop


def applied_strip(profile, side='OUT', panel_front=None):
    """APPLIED profile -> decorative applied molding loop, swept around
    an opening like the sticking strip. Drawings are closed molding
    cross-sections positioned by their own coordinates, x measured
    from the opening edge, and read per ``side``:

    OUT -- seats proud ON the door face: +x runs outward onto the
    frame, y is the height proud of the face (u = -x, v = -y).
    IN  -- seats on the recessed panel INSIDE the opening: +x runs
    into the opening, y is the height up from the panel plane
    (u = +x, v = panel_front - y).

    The drawing owns its placement -- moving the curve in its .blend
    moves the molding on the door. Returns a CLOSED counter-clockwise
    loop."""
    pts = profile['points']
    if len(pts) < 3:
        return None
    if side == 'IN':
        base = panel_front if panel_front is not None else 0.0
        loop = [(p[0], base - p[1]) for p in pts]
    else:
        loop = [(-p[0], -p[1]) for p in pts]
    area = 0.0
    n = len(loop)
    for i in range(n):
        a = loop[i]
        b = loop[(i + 1) % n]
        area += a[0] * b[1] - b[0] * a[1]
    if area < 0.0:
        loop.reverse()
    return loop


def member_section(profile, thickness):
    """MITERED profile -> full-member sweep section.

    Mitered doors have no flat face: the entire member cross-section is
    one molding profile, mitred at the door corners. Drawings are OPEN
    polylines in (x, y) = (across the member from the OUTER edge, depth
    from the front-most surface), covering the outer edge line, the
    shaped face, and the drop down the opening edge -- the sweep uses
    them as-is. Returns [(u, v), ...] ordered outer-edge end first,
    both ends closed to the door back so the sweep seals the outer
    edge and the opening wall. The member width (max u) becomes the
    frame width for layout."""
    pts = list(profile['points'])
    if len(pts) < 2:
        return None
    u0 = min(p[0] for p in pts)
    v0 = min(p[1] for p in pts)
    pts = [(p[0] - u0, p[1] - v0) for p in pts]
    if pts[0][0] > pts[-1][0]:
        pts.reverse()
    pts = [(u, min(v, thickness)) for (u, v) in pts]
    if pts[0][1] < thickness - 1e-9:
        pts.insert(0, (pts[0][0], thickness))
    if pts[-1][1] < thickness - 1e-9:
        pts.append((pts[-1][0], thickness))
    return pts


def profile_from_object(ob, res=16):
    """Sample a scene curve object into the same dict load_profile
    returns, so a style's outside_profile / inside_profile pointer can
    reference a curve appended into the file. Returns None for a
    non-curve or empty object."""
    if ob is None or ob.type != 'CURVE':
        return None
    m = ob.matrix_world
    best = None
    best_cyclic = False
    for sp in ob.data.splines:
        pts, cyclic = _sample_spline(sp, res)
        pts = [tuple(m @ Vector(p)) for p in pts]
        if best is None or len(pts) > len(best):
            best = pts
            best_cyclic = cyclic
    if not best or len(best) < 2:
        return None
    ext = [max(p[i] for p in best) - min(p[i] for p in best)
           for i in range(3)]
    drop = ext.index(min(ext))
    keep = [i for i in range(3) if i != drop]
    pts2 = [(p[keep[0]], p[keep[1]]) for p in best]
    out = []
    for p in pts2:
        if not out or abs(p[0] - out[-1][0]) > 1e-7 or abs(p[1] - out[-1][1]) > 1e-7:
            out.append(p)
    if best_cyclic and len(out) > 1 \
            and abs(out[0][0] - out[-1][0]) < 1e-7 \
            and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return dict(points=out, cyclic=best_cyclic, name=ob.name,
                category=None)


def edge_profile_section(profile, thickness):
    """Orient an open OUTER / INNER edge outline into sweep space and
    fit it to the door thickness.

    The drawings trace the material boundary of the edge zone: a run
    along one face from the inner point out to the edge corner, the
    straight edge, then the cutter shape into the other face. That
    face run pins the whole frame -- its constant coordinate is the
    unshaped (back) face, its far end the inward direction, and the
    point where it meets the rest the edge plane -- so orientation is
    detected, not configured.

    Sweep space: u >= 0 across the face measured inward from the
    member edge, v in [0, thickness] through the door from the shaped
    (front) face. The face run itself is trimmed off (its corner point
    stays); the caps in sweep_edge_frame cover the flat faces.

    Thickness fit preserves the cutter shape: only the straight edge
    run behind the deepest shaped point stretches (or trims) to the
    actual thickness. A door thinner than the shaped region itself
    scales the whole v axis as a last resort.

    Returns [(u, v), ...] ordered from the front-face end to the back
    edge corner.
    """
    pts = list(profile['points'])
    ext_a = max(p[0] for p in pts) - min(p[0] for p in pts)
    ext_b = max(p[1] for p in pts) - min(p[1] for p in pts)
    if ext_a > ext_b:
        # Thickness axis (the larger extent) goes to v.
        pts = [(p[1], p[0]) for p in pts]
    u0 = min(p[0] for p in pts)
    v0 = min(p[1] for p in pts)
    pts = [(p[0] - u0, p[1] - v0) for p in pts]
    span_v = max(p[1] for p in pts)
    if span_v <= 1e-9:
        return pts
    tol = span_v * 1e-3

    def face_run(seq):
        """Points at the start of ``seq`` lying on a v-extreme: the
        drawing's face run. Returns the join index (0 = no run)."""
        v = seq[0][1]
        if min(v, span_v - v) > tol:
            return 0
        i = 0
        while i + 1 < len(seq) and abs(seq[i + 1][1] - v) < tol:
            i += 1
        return i

    r_start = face_run(pts)
    r_end = face_run(pts[::-1])
    if r_end > r_start:
        pts.reverse()
        r_start = r_end
    if r_start > 0:
        inner_u = pts[0][0]
        edge_u = pts[r_start][0]
        back_v = pts[0][1]
        pts = pts[r_start:]
    else:
        # No face run drawn: assume an edge line from face to face,
        # anchored with the edge at the deeper endpoint's u.
        inner_u = max(p[0] for p in pts)
        edge_u = min(p[0] for p in pts)
        back_v = pts[0][1]
    inward = 1.0 if inner_u >= edge_u else -1.0
    front_v = 0.0 if back_v > span_v / 2.0 else span_v
    pts = [(max((p[0] - edge_u) * inward, 0.0), abs(p[1] - front_v))
           for p in pts]
    if pts[0][1] > pts[-1][1]:
        pts.reverse()

    # Deepest shaped point: from the back end the section is a straight
    # run at the edge (u ~ 0) until the cutter shape starts.
    edge_run_u = pts[-1][0]
    shaped_v = 0.0
    for p in pts:
        if abs(p[0] - edge_run_u) > 1e-6:
            shaped_v = max(shaped_v, p[1])
    if shaped_v >= thickness or shaped_v <= 0.0:
        # No straight run to absorb the difference -- scale everything.
        return [(p[0], p[1] * thickness / span_v) for p in pts]
    k = (thickness - shaped_v) / (span_v - shaped_v) if span_v > shaped_v else 1.0
    return [(p[0], p[1] if p[1] <= shaped_v
             else shaped_v + (p[1] - shaped_v) * k) for p in pts]


# ---- Catalog edge profiles -----------------------------------------
# The catalog's "Door and Drawer Edge Profiles" chart is a set of
# exact geometric specs (roundover radii, chamfer legs, a bevel, a
# cove), so these sections are generated in code instead of drawn as
# .blend assets. Output matches edge_profile_section's sweep space.

_INCH = 0.0254


def _edge_arc(r, concave, segs=10):
    """Quarter-arc shaped run of radius r from the face landing (r, 0)
    to the edge (0, r): convex = roundover (arc centered inside the
    material), concave = cove scooped out of the arris (arc centered
    on the original corner)."""
    pts = []
    for i in range(segs + 1):
        t = math.radians(90.0 * i / segs)
        if concave:
            pts.append((r * math.cos(t), r * math.sin(t)))
        else:
            pts.append((r - r * math.sin(t), r - r * math.cos(t)))
    return pts


# ---- Drawn-cutter sections (digitized) ------------------------------
# Sections traced from the installed molding asset pack's edge
# drawings (Base Molding/<name> Edge.blend) -- the same
# cutters the catalog names refer to, so the door edge matches the
# shop's base/light-rail tooling. Each list is the shaped run in the
# builders' shared sweep space, in INCHES (u inward across the face
# from the member edge, v into the thickness from the front face),
# ordered from the front-face landing to where the cut exits. Sampled
# from the bezier outlines and simplified to 2.5-mil tolerance.
#
# 'New Cut' is a full-thickness sweep: the cut crosses the whole 3/4"
# stock and lands on the BACK face (u > 0 at v = 3/4), so its section
# ends off the edge plane -- named_edge_section continues the edge run
# from the landing point's u, not from 0.

_ESTATE_PTS = [
    (0.6636, 0.0000), (0.6409, 0.0072), (0.6262, 0.0202), (0.6182, 0.0398),
    (0.6166, 0.0658), (0.5228, 0.0658), (0.4985, 0.1074), (0.4624, 0.1437),
    (0.4147, 0.1747), (0.3633, 0.1976), (0.2840, 0.2210), (0.2010, 0.2363),
    (0.1064, 0.2463), (0.0000, 0.2511),
]

_ECLIPSE_PTS = [
    (0.4397, 0.0000), (0.4397, 0.0637), (0.3715, 0.0637), (0.3520, 0.1198),
    (0.3234, 0.1753), (0.2881, 0.2218), (0.2459, 0.2592), (0.1903, 0.2905),
    (0.1337, 0.3086), (0.0702, 0.3177), (0.0000, 0.3177),
]

_NEW_CUT_PTS = [
    (0.6181, 0.0000), (0.5898, 0.0288), (0.5527, 0.0578), (0.5099, 0.0834),
    (0.4616, 0.1055), (0.3686, 0.1347), (0.2186, 0.1633), (0.1479, 0.1894),
    (0.1108, 0.2105), (0.0821, 0.2323), (0.0384, 0.2819), (0.0171, 0.3233),
    (0.0038, 0.3717), (0.0000, 0.4179), (0.0037, 0.4697), (0.0099, 0.5036),
    (0.1098, 0.7500),
]

_CLASSIC_CUT_PTS = [
    (0.3778, 0.0000), (0.3778, 0.0700), (0.3201, 0.0716), (0.2760, 0.0814),
    (0.2392, 0.0991), (0.2097, 0.1247), (0.1918, 0.1501), (0.1783, 0.1803),
    (0.1651, 0.2490), (0.1009, 0.2490), (0.0794, 0.2758), (0.0555, 0.2954),
    (0.0290, 0.3078), (0.0000, 0.3131),
]

_DROP_RADIUS_PTS = [
    (0.3814, 0.0000), (0.3814, 0.1349), (0.3154, 0.1414), (0.2412, 0.1620),
    (0.1733, 0.1942), (0.1166, 0.2349), (0.0728, 0.2806), (0.0370, 0.3365),
    (0.0116, 0.4032), (0.0000, 0.4695),
]


def _poly(pts_inches):
    """Inch point list -> meters, for the digitized sections above."""
    return [(u * _INCH, v * _INCH) for (u, v) in pts_inches]


# 3/8" Inset (lipped door) edges: a 3/8 x 3/8 rabbet on the BACK of the
# door forms the lip that sits over the face-frame opening; the front
# arris of the lip is finished square, 1/8" roundover, or a full 3/8"
# roundover. Drafted from the names' standard lipped-door reading
# (no catalog drawing exists for these) -- adjust the constants if the
# shop's lip cutter differs.
_LIP = 0.375 * _INCH   # lip depth (v) and rabbet width (u)


def _inset_edge(front_pts):
    """Lipped-door section: ``front_pts`` shapes the front arris, the
    edge line continues to the lip depth, then the rabbet shoulder runs
    inward; named_edge_section's edge run continues from the shoulder
    (u = _LIP) to the door back."""
    pts = list(front_pts)
    if pts[-1][1] < _LIP - 1e-9:
        pts.append((0.0, _LIP))
    pts.append((_LIP, _LIP))
    return pts


# Lowercased catalog name -> zero-arg builder for the shaped run
# [(u, v), ...]; named_edge_section appends the straight edge run to
# the door back, continuing from the run's landing u (0 for ordinary
# edge cuts, the rabbet width for lipped edges, the back-face landing
# for New Cut's full sweep). Names follow the catalog chart / the
# cabinet style's ss_edge_profile items.
_EDGE_SECTION_BUILDERS = {
    '1/8" radius': lambda: _edge_arc(0.125 * _INCH, False),
    '1/4" radius': lambda: _edge_arc(0.25 * _INCH, False),
    '3/8" radius': lambda: _edge_arc(0.375 * _INCH, False),
    # 3/16 x 3/16 45-degree chamfer.
    'chamfer': lambda: [(0.1875 * _INCH, 0.0), (0.0, 0.1875 * _INCH)],
    '3/16" chamfer': lambda: [(0.1875 * _INCH, 0.0), (0.0, 0.1875 * _INCH)],
    # Long shallow bevel: ~3/4 across the face dropping ~1/4 into the
    # edge, square edge below (proportions read off the catalog
    # drawing, pdf page 147).
    'beveled': lambda: [(0.75 * _INCH, 0.0), (0.0, 0.25 * _INCH)],
    # Concave 3/8 cove scooped out of the front arris.
    'bay': lambda: _edge_arc(0.375 * _INCH, True),
    # Cabinet corner treatments (face-frame arris details): 1/4 cove and
    # a 1/4 x 1/4 chamfer alongside the shared radius cuts above.
    '1/4" cove': lambda: _edge_arc(0.25 * _INCH, True),
    'cove': lambda: _edge_arc(0.25 * _INCH, True),
    '1/4" x 1/4" chamfer': lambda: [(0.25 * _INCH, 0.0), (0.0, 0.25 * _INCH)],
    # Digitized from the molding edge asset pack (see above).
    'estate': lambda: _poly(_ESTATE_PTS),
    'eclipse': lambda: _poly(_ECLIPSE_PTS),
    'new cut': lambda: _poly(_NEW_CUT_PTS),
    'classic cut': lambda: _poly(_CLASSIC_CUT_PTS),
    'drop radius': lambda: _poly(_DROP_RADIUS_PTS),
    # 3/8" lipped-door edges (drafted; see _inset_edge).
    '3/8" inset square': lambda: _inset_edge([(0.0, 0.0)]),
    '3/8" inset 1/8" radius': lambda: _inset_edge(
        _edge_arc(0.125 * _INCH, False)),
    '3/8" inset radius': lambda: _inset_edge(
        _edge_arc(0.375 * _INCH, False)),
}


def named_edge_run(name):
    """Catalog edge / corner-treatment name -> the raw shaped run
    [(u, v), ...] in meters (u inward across the face from the member
    edge, v into the thickness from the front face), ordered from the
    face landing to where the cut exits the edge. No thickness fitting
    and no straight run appended -- callers sweeping a cutter along an
    arris want just the removed-corner outline. None for Square /
    empty / unknown names."""
    key = (name or '').strip().lower()
    build = _EDGE_SECTION_BUILDERS.get(key)
    if build is None:
        return None
    return list(build())


def named_edge_section(name, thickness):
    """Catalog edge profile name -> sweep section fitted to the door
    thickness, same output space as edge_profile_section (u >= 0 inward
    from the member edge, v in [0, thickness] from the front face,
    ordered front end first, ending at the back edge corner). Returns
    None -- a square edge -- for Square / empty / unknown names so
    callers can fall through cleanly."""
    key = (name or '').strip().lower()
    build = _EDGE_SECTION_BUILDERS.get(key)
    if build is None:
        return None
    pts = build()
    vmax = max(v for u, v in pts)
    if vmax >= thickness > 0.0:
        # Front thinner than the shaped region: scale the whole shape.
        k = thickness / vmax
        pts = [(u * k, v * k) for (u, v) in pts]
    if pts[-1][1] < thickness - 1e-9:
        # Straight run to the door back, continuing at the section's
        # landing u: 0 for ordinary edge cuts (on the edge plane), the
        # rabbet width for the lipped 3/8" Inset edges.
        pts.append((pts[-1][0], thickness))
    return pts


def sweep_edge_frame(section, width, height, inner=False):
    """Mitred sweep of an edge section around a width x height rect,
    for review builds and tests. Plane space: x across [0, width],
    z up [0, height], y = depth with the front face at y=0 and the
    back at y=thickness (matching edge_profile_section's v).

    inner=False sweeps an OUTER profile: the rect is the door outline
    and u runs inward. inner=True sweeps around an opening: the rect
    is the opening and u runs outward into the surrounding frame.

    Returns (verts, faces). Front and back faces are capped between
    the section endpoints so the result reads as a solid.
    """
    s = 1.0 if not inner else -1.0
    corners = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]
    dirs = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)]
    n = len(section)
    verts = []
    for (cx, cz), (dx, dz) in zip(corners, dirs):
        for (u, v) in section:
            verts.append((cx + s * dx * u, v, cz + s * dz * u))
    faces = []
    for c in range(4):
        a = c * n
        b = ((c + 1) % 4) * n
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
    # Caps between the four rings' first points (front) / last (back).
    faces.append((0 * n, 1 * n, 2 * n, 3 * n))
    faces.append((3 * n + n - 1, 2 * n + n - 1, 1 * n + n - 1, 0 * n + n - 1))
    return verts, faces
