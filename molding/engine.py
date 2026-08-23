"""Library-agnostic molding sweep geometry.

Everything here works on world-space plan (XY) geometry derived from
cabinet root objects plus a FACTS dict supplied by the per-library
adapters - the engine never reads library property groups itself.

Facts, one dict per member object (keyed by id(obj)):
    role:  'CABINET' or 'APPLIANCE' (appliances never carry molding;
           they bridge runs and break them with returns)
    corner: None, or {'ld': left arm thickness, 'rd': right arm
           thickness, 'diagonal': bool} - the L-footprint corner
           cabinet convention shared by both libraries (origin at the
           wall corner, left arm fronting local +X at x=ld, right arm
           fronting local -Y at y=-rd)
    kick:  {'skip', 'setback', 'stile_left', 'stile_right',
           'stile_left_w', 'stile_right_w', 'middle_skip'} - base
           molding only; middle_skip makes the between-stiles span a
           hard SKIP (refrigerator openings) instead of a RECESS
    finished_left / finished_right: bool - end treatments

Paths are built as raw front polylines, offset to the RIGHT of travel
with mitred joins (winding is normalized so right-of-travel is always
outward), and returned as world XY point lists ready for the caller
to localize and extrude.
"""

import bpy
import math
import mathutils

from .. import hb_types, units


# ---------------------------------------------------------------------------
# Object measurements
# ---------------------------------------------------------------------------

def cage_dims(obj):
    """(width, depth, height) from the root's GeoNode Dim inputs, with
    an evaluated-dimensions fallback."""
    try:
        geo = hb_types.GeoNodeObject(obj)
        x = geo.get_input('Dim X')
        y = geo.get_input('Dim Y')
        z = geo.get_input('Dim Z')
        if x and y and z:
            return x, y, z
    except Exception:
        pass
    d = obj.dimensions
    return d.x, d.y, d.z


def _xy(v3):
    return mathutils.Vector((v3.x, v3.y))


def footprint_xy(obj):
    """World XY footprint corners (back-left, back-right, front-left,
    front-right) - exact at any rotation."""
    w, d, _ = cage_dims(obj)
    mw = obj.matrix_world
    return [_xy(mw @ mathutils.Vector((lx, ly, 0.0)))
            for lx, ly in ((0.0, 0.0), (w, 0.0), (0.0, -d), (w, -d))]


def top_z(obj):
    _, _, h = cage_dims(obj)
    return obj.matrix_world.translation.z + h


def bottom_z(obj):
    return obj.matrix_world.translation.z


def front_normal_xy(obj):
    v = obj.matrix_world.to_3x3() @ mathutils.Vector((0.0, -1.0, 0.0))
    n = mathutils.Vector((v.x, v.y))
    if n.length > 1e-6:
        n.normalize()
    return n


# ---------------------------------------------------------------------------
# Run grouping
# ---------------------------------------------------------------------------

def members_touch(a, b, tolerance=0.02, align='top'):
    """True when two members' world plan AABBs touch (overlap once each
    is expanded by the tolerance) and they line up vertically. Crown
    groups on a shared TOP line; base and light rail on the BOTTOM."""
    if align == 'top':
        if abs(top_z(a) - top_z(b)) > tolerance:
            return False
    else:
        if abs(bottom_z(a) - bottom_z(b)) > tolerance:
            return False
    fa = footprint_xy(a)
    fb = footprint_xy(b)
    if (min(p.x for p in fa) - tolerance > max(p.x for p in fb)
            or min(p.x for p in fb) - tolerance > max(p.x for p in fa)):
        return False
    if (min(p.y for p in fa) - tolerance > max(p.y for p in fb)
            or min(p.y for p in fb) - tolerance > max(p.y for p in fa)):
        return False
    return True


def connected_components(members, align='top'):
    """Partition members into touch-connected components."""
    remaining = list(members)
    components = []
    while remaining:
        comp = [remaining.pop()]
        queue = list(comp)
        while queue:
            current = queue.pop()
            for other in list(remaining):
                if members_touch(current, other, align=align):
                    remaining.remove(other)
                    comp.append(other)
                    queue.append(other)
        components.append(comp)
    return components


def order_chain(component, align='top'):
    """Order a component into a linear chain by walking touch adjacency
    from an end (a member with a single touching neighbor). Unreachable
    members (branching layouts) are appended so they still receive a
    segment."""
    if len(component) <= 2:
        return list(component)
    neighbors = {
        id(c): [o for o in component
                if o is not c and members_touch(c, o, align=align)]
        for c in component
    }
    start = next(
        (c for c in component if len(neighbors[id(c)]) == 1), component[0])
    chain = [start]
    used = {id(start)}
    current = start
    while True:
        nxt = next(
            (o for o in neighbors[id(current)] if id(o) not in used), None)
        if nxt is None:
            break
        chain.append(nxt)
        used.add(id(nxt))
        current = nxt
    for c in component:
        if id(c) not in used:
            chain.append(c)
    return chain


# ---------------------------------------------------------------------------
# Offsetting
# ---------------------------------------------------------------------------

def offset_polyline_right(points, offset):
    """Offset an open XY polyline to the RIGHT of its direction of
    travel by `offset`, with mitred joins. Terminal points shift
    perpendicular only; callers apply end treatments. Consecutive
    duplicates are dropped."""
    pts = []
    for p in points:
        if not pts or (p - pts[-1]).length > 1e-6:
            pts.append(p)
    if len(pts) < 2 or abs(offset) < 1e-9:
        return pts
    lines = []
    for a, b in zip(pts, pts[1:]):
        d = (b - a).normalized()
        n = mathutils.Vector((d.y, -d.x))
        lines.append((a + n * offset, d, (b - a).length))
    out = [lines[0][0]]
    for (p1, d1, len1), (p2, d2, _l2) in zip(lines, lines[1:]):
        cross = d1.x * d2.y - d1.y * d2.x
        if abs(cross) < 1e-6:
            # Parallel continuation (collinear fronts or a square jog
            # already present as its own raw segment).
            out.append(p1 + d1 * len1)
            out.append(p2)
        else:
            t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / cross
            out.append(p1 + d1 * t)
    p_last, d_last, len_last = lines[-1]
    out.append(p_last + d_last * len_last)
    deduped = []
    for p in out:
        if not deduped or (p - deduped[-1]).length > 1e-6:
            deduped.append(p)
    return deduped


def offset_polygon_right(points, offset):
    """Closed-loop counterpart: offset every edge of the CLOSED loop to
    the right of travel, mitring every vertex including the seam."""
    pts = []
    for p in points:
        if not pts or (p - pts[-1]).length > 1e-6:
            pts.append(p)
    if pts and (pts[0] - pts[-1]).length < 1e-6:
        pts.pop()
    if len(pts) < 3 or abs(offset) < 1e-9:
        return pts
    lines = []
    n = len(pts)
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        d = (b - a).normalized()
        nrm = mathutils.Vector((d.y, -d.x))
        lines.append((a + nrm * offset, d))
    out = []
    for i in range(n):
        p1, d1 = lines[i - 1]
        p2, d2 = lines[i]
        cross = d1.x * d2.y - d1.y * d2.x
        if abs(cross) < 1e-6:
            out.append(p2)
        else:
            t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / cross
            out.append(p1 + d1 * t)
    return out


# ---------------------------------------------------------------------------
# Corner cabinet plan geometry
# ---------------------------------------------------------------------------

def corner_plan_data(obj, corner_facts):
    """Local plan data for an L-footprint corner cabinet.

    Returns dict:
        front: canonical raw front polyline, left arm end -> right arm
            end (two faces meeting at the notch, or the diagonal)
        left_end / right_end: (front_corner, back_corner) of each arm's
            end face
    """
    width, depth, _ = cage_dims(obj)
    ld = corner_facts.get('ld') or units.inch(24.0)
    rd = corner_facts.get('rd') or units.inch(24.0)
    left_front = mathutils.Vector((ld, -depth))
    right_front = mathutils.Vector((width, -rd))
    if corner_facts.get('diagonal'):
        front = [left_front, right_front]
    else:
        front = [left_front, mathutils.Vector((ld, -rd)), right_front]
    return {
        'front': front,
        'left_end': (left_front, mathutils.Vector((0.0, -depth))),
        'right_end': (right_front, mathutils.Vector((width, 0.0))),
    }


# ---------------------------------------------------------------------------
# Front-line chain sweep (crown / light rail)
# ---------------------------------------------------------------------------

def _assemble_front_raw(chain, facts):
    """Raw (unoffset) world-XY front polyline through the chain plus
    terminal end data and the winding probe. Straight members
    contribute their two front corners; corner members their notch /
    diagonal front, entered from whichever arm faces the incoming
    path."""
    points = []
    terminals = [None, None]
    first_straight = None

    def _center(obj):
        fp = footprint_xy(obj)
        return sum(fp, mathutils.Vector((0.0, 0.0))) / 4.0

    n = len(chain)
    for i, obj in enumerate(chain):
        mw = obj.matrix_world
        f = facts[id(obj)]
        prev_ref = points[-1] if points else None
        next_ref = _center(chain[i + 1]) if i + 1 < n else None

        if f.get('corner'):
            data = corner_plan_data(obj, f['corner'])
            pts = [_xy(mw @ mathutils.Vector((p.x, p.y, 0.0)))
                   for p in data['front']]
            ends = {}
            for key in ('left_end', 'right_end'):
                fp, bp = data[key]
                ends[key] = (
                    _xy(mw @ mathutils.Vector((fp.x, fp.y, 0.0))),
                    _xy(mw @ mathutils.Vector((bp.x, bp.y, 0.0))),
                )
            reverse = False
            if prev_ref is not None:
                reverse = ((prev_ref - pts[0]).length
                           > (prev_ref - pts[-1]).length)
            elif next_ref is not None:
                reverse = ((next_ref - pts[-1]).length
                           > (next_ref - pts[0]).length)
            entry_key, exit_key = 'left_end', 'right_end'
            if reverse:
                pts = list(reversed(pts))
                entry_key, exit_key = exit_key, entry_key
            points.extend(pts)
            if i == 0:
                terminals[0] = {
                    'obj': obj,
                    'side': 'left' if entry_key == 'left_end' else 'right',
                    'back': ends[entry_key][1],
                }
            if i == n - 1:
                terminals[1] = {
                    'obj': obj,
                    'side': 'left' if exit_key == 'left_end' else 'right',
                    'back': ends[exit_key][1],
                }
        else:
            width, depth, _ = cage_dims(obj)
            fl = _xy(mw @ mathutils.Vector((0.0, -depth, 0.0)))
            fr = _xy(mw @ mathutils.Vector((width, -depth, 0.0)))
            bl = _xy(mw @ mathutils.Vector((0.0, 0.0, 0.0)))
            br = _xy(mw @ mathutils.Vector((width, 0.0, 0.0)))
            if prev_ref is not None:
                left_first = ((prev_ref - fl).length
                              <= (prev_ref - fr).length)
            elif next_ref is not None:
                left_first = ((next_ref - fr).length
                              <= (next_ref - fl).length)
            else:
                left_first = True
            if left_first:
                ordered = ((fl, 'left', bl), (fr, 'right', br))
            else:
                ordered = ((fr, 'right', br), (fl, 'left', bl))
            if first_straight is None:
                fn = front_normal_xy(obj)
                if fn.length > 1e-6:
                    first_straight = (len(points), fn)
            points.extend([ordered[0][0], ordered[1][0]])
            if i == 0:
                terminals[0] = {'obj': obj, 'side': ordered[0][1],
                                'back': ordered[0][2]}
            if i == n - 1:
                terminals[1] = {'obj': obj, 'side': ordered[1][1],
                                'back': ordered[1][2]}
    return points, terminals, first_straight


def chain_sweep_points(chain, facts, face_offset, end_offset):
    """Swept path through a chain along the member fronts (crown /
    light rail), in world XY. Finished ends wrap around the extremity
    to the carcass rear; unfinished ends stop flush. Returns
    (points, chain) - chain possibly reversed - or None."""
    raw, terminals, first_straight = _assemble_front_raw(chain, facts)

    if first_straight is not None and len(raw) >= 2:
        idx, fn = first_straight
        travel = raw[idx + 1] - raw[idx]
        if travel.length > 1e-6:
            travel.normalize()
            right = mathutils.Vector((travel.y, -travel.x))
            if right.dot(fn) < 0:
                chain = list(reversed(chain))
                raw, terminals, first_straight = \
                    _assemble_front_raw(chain, facts)

    if len(raw) < 2:
        return None

    off = offset_polyline_right(raw, face_offset)

    for side_idx in (0, 1):
        term = terminals[side_idx]
        if term is None:
            continue
        outward = (raw[0] - raw[1]) if side_idx == 0 else (raw[-1] - raw[-2])
        if outward.length < 1e-6:
            continue
        outward.normalize()
        f = facts[id(term['obj'])]
        if not f.get('finished_%s' % term['side'], False):
            continue
        if side_idx == 0:
            off[0] = off[0] + outward * end_offset
            off.insert(0, term['back'] + outward * end_offset)
        else:
            off[-1] = off[-1] + outward * end_offset
            off.append(term['back'] + outward * end_offset)
    return off, chain


def rail_sweep_segments(chain, facts, face_offset, end_offset):
    """Light-rail path segments through a chain: chain_sweep_points
    plus raised-bay handling. A member's 'rail_skips' spans (bays whose
    bottom sits above the run line) break the run - the rail stops at
    the raised opening's edge and returns to the carcass rear (the
    wall), treated like a finished end - and pick back up with a
    matching return on the far side. Returns ([(points, False), ...],
    chain possibly reversed) or None."""
    if not any(facts[id(m)].get('rail_skips') for m in chain):
        result = chain_sweep_points(chain, facts, face_offset, end_offset)
        if result is None:
            return None
        pts, chain = result
        return [(pts, False)], chain

    raw, terminals, first_straight = _assemble_front_raw(chain, facts)
    if first_straight is not None and len(raw) >= 2:
        idx, fn = first_straight
        travel = raw[idx + 1] - raw[idx]
        if travel.length > 1e-6:
            travel.normalize()
            right = mathutils.Vector((travel.y, -travel.x))
            if right.dot(fn) < 0:
                chain = list(reversed(chain))
                raw, terminals, first_straight = \
                    _assemble_front_raw(chain, facts)
    if len(raw) < 2:
        return None

    def _center(obj):
        fp = footprint_xy(obj)
        return sum(fp, mathutils.Vector((0.0, 0.0))) / 4.0

    # Piecewise raw segments; each carries whether its start / end is a
    # wall return (those ends never get the terminal end treatment).
    segs = []
    seg_returns = []
    current = []
    flags = [False, False]

    def _close():
        nonlocal current, flags
        if len(current) >= 2:
            segs.append(current)
            seg_returns.append((flags[0], flags[1]))
        current = []
        flags = [False, False]

    n = len(chain)
    for i, obj in enumerate(chain):
        mw = obj.matrix_world
        f = facts[id(obj)]
        if current:
            prev_ref = current[-1]
        elif segs:
            prev_ref = segs[-1][-1]
        else:
            prev_ref = None
        next_ref = _center(chain[i + 1]) if i + 1 < n else None

        if f.get('corner'):
            data = corner_plan_data(obj, f['corner'])
            pts = [_xy(mw @ mathutils.Vector((p.x, p.y, 0.0)))
                   for p in data['front']]
            reverse = False
            if prev_ref is not None:
                reverse = ((prev_ref - pts[0]).length
                           > (prev_ref - pts[-1]).length)
            elif next_ref is not None:
                reverse = ((next_ref - pts[-1]).length
                           > (next_ref - pts[0]).length)
            if reverse:
                pts = list(reversed(pts))
            current.extend(pts)
            continue

        width, depth, _ = cage_dims(obj)

        def _front(x):
            return _xy(mw @ mathutils.Vector((x, -depth, 0.0)))

        def _back(x):
            return _xy(mw @ mathutils.Vector((x, 0.0, 0.0)))

        fl, fr = _front(0.0), _front(width)
        if prev_ref is not None:
            left_first = (prev_ref - fl).length <= (prev_ref - fr).length
        elif next_ref is not None:
            left_first = (next_ref - fr).length <= (next_ref - fl).length
        else:
            left_first = True

        # Kept intervals between skip zones, each carrying the kind of
        # the skip flanking it on either side (None = member edge).
        # 'OPEN' boundaries (raised bay - nothing at the run line) get
        # a wall return; 'BOX' boundaries (dropped bay - its box
        # stands across the run line) die flush into the box.
        skips = sorted(f.get('rail_skips') or [])
        kept = []
        cursor = 0.0
        prev_kind = None
        for s0, s1, kind in skips:
            if s0 - cursor > 1e-4:
                kept.append((cursor, s0, prev_kind, kind))
            cursor = max(cursor, s1)
            prev_kind = kind
        if width - cursor > 1e-4:
            kept.append((cursor, width, prev_kind, None))

        if left_first:
            ordered = kept
            start_x, end_x = 0.0, width
        else:
            ordered = [(b, a, kr, kl) for a, b, kl, kr in reversed(kept)]
            start_x, end_x = width, 0.0

        if not ordered:
            # Whole member skipped: seal any incoming rail at the
            # seam; a following member restarts from the far seam.
            if left_first:
                k_first, k_last = skips[0][2], skips[-1][2]
            else:
                k_first, k_last = skips[-1][2], skips[0][2]
            if current:
                if k_first == 'OPEN':
                    current.append(_back(start_x))
                flags[1] = True
                _close()
            if i + 1 < n:
                current = [_back(end_x)] if k_last == 'OPEN' else []
                flags[0] = True
            continue

        for j, (enter, exit_, k_in, k_out) in enumerate(ordered):
            if k_in is not None:
                if j == 0 and current:
                    # The skip touches the seam: seal the incoming
                    # rail there first.
                    if k_in == 'OPEN':
                        current.append(_back(start_x))
                    flags[1] = True
                    _close()
                current = [_back(enter)] if k_in == 'OPEN' else []
                flags[0] = True
            current.append(_front(enter))
            current.append(_front(exit_))
            if k_out is not None:
                if k_out == 'OPEN':
                    current.append(_back(exit_))
                flags[1] = True
                _close()
        if ordered and ordered[-1][3] is not None and i + 1 < n:
            current = [_back(end_x)] if ordered[-1][3] == 'OPEN' else []
            flags[0] = True
    _close()

    if not segs:
        return None

    out = [offset_polyline_right(pts, face_offset) for pts in segs]

    for side_idx in (0, 1):
        term = terminals[side_idx]
        if term is None:
            continue
        if side_idx == 0:
            if seg_returns[0][0] or len(segs[0]) < 2:
                continue
            outward = segs[0][0] - segs[0][1]
        else:
            if seg_returns[-1][1] or len(segs[-1]) < 2:
                continue
            outward = segs[-1][-1] - segs[-1][-2]
        if outward.length < 1e-6:
            continue
        outward.normalize()
        f = facts[id(term['obj'])]
        if not f.get('finished_%s' % term['side'], False):
            continue
        if side_idx == 0:
            out[0][0] = out[0][0] + outward * end_offset
            out[0].insert(0, term['back'] + outward * end_offset)
        else:
            out[-1][-1] = out[-1][-1] + outward * end_offset
            out[-1].append(term['back'] + outward * end_offset)

    segments = [(pts, False) for pts in out if len(pts) >= 2]
    return (segments, chain) if segments else None


def raised_rail_runs(obj, f, face_offset, end_offset,
                     open_left=True, open_right=True):
    """Standalone light-rail runs for a member's off-line bay levels -
    bays whose bottom sits above OR below the cabinet bottom line
    carry their own rail at their own line (the bottom-line run skips
    them, see rail_sweep_segments). One run per contiguous span per
    level. A span end dies flush where a lower zone's box stands at
    that level; it returns to the carcass rear where the adjacent zone
    sits higher still; a cabinet end wraps to the rear like a finished
    end when that side is open (no chain neighbor) and FINISHED.
    Returns [(points, dz)] with dz the level's height relative to the
    cabinet bottom line (negative for dropped bays)."""
    bays = f.get('rail_bays') or []
    if not bays:
        return []
    width, depth, _ = cage_dims(obj)
    mw = obj.matrix_world

    def _front(x):
        return _xy(mw @ mathutils.Vector((x, -depth, 0.0)))

    def _back(x):
        return _xy(mw @ mathutils.Vector((x, 0.0, 0.0)))

    def _zone_dz(x):
        best, best_d = 0.0, None
        for x0, x1, dz in bays:
            d = max(x0 - x, 0.0, x - x1)
            if best_d is None or d < best_d:
                best, best_d = dz, d
        return best

    out = []
    levels = sorted({round(dz, 3) for _x0, _x1, dz in bays
                     if abs(dz) > 0.02})
    for level in levels:
        spans = sorted((x0, x1) for x0, x1, dz in bays
                       if abs(round(dz, 3) - level) < 1e-6)
        merged = []
        for x0, x1 in spans:
            if merged and x0 - merged[-1][1] < 0.08:
                merged[-1] = (merged[-1][0], x1)
            else:
                merged.append((x0, x1))
        for x0, x1 in merged:
            at_left_end = x0 < 0.08
            at_right_end = width - x1 < 0.08
            if at_left_end:
                x0 = 0.0
            if at_right_end:
                x1 = width
            raw = [_front(x0), _front(x1)]
            if not at_left_end and _zone_dz(x0 - 0.01) > level:
                raw.insert(0, _back(x0))
            if not at_right_end and _zone_dz(x1 + 0.01) > level:
                raw.append(_back(x1))
            off = offset_polyline_right(raw, face_offset)
            if len(off) < 2:
                continue
            if at_left_end and open_left and f.get('finished_left'):
                o3 = mw.to_3x3() @ mathutils.Vector((-1.0, 0.0, 0.0))
                o = mathutils.Vector((o3.x, o3.y))
                if o.length > 1e-6:
                    o.normalize()
                    off[0] = off[0] + o * end_offset
                    off.insert(0, _back(0.0) + o * end_offset)
            if at_right_end and open_right and f.get('finished_right'):
                o3 = mw.to_3x3() @ mathutils.Vector((1.0, 0.0, 0.0))
                o = mathutils.Vector((o3.x, o3.y))
                if o.length > 1e-6:
                    o.normalize()
                    off[-1] = off[-1] + o * end_offset
                    off.append(_back(width) + o * end_offset)
            out.append((off, level))
    return out


# ---------------------------------------------------------------------------
# Kick-level span sweep (base molding)
# ---------------------------------------------------------------------------

def _kick_spans_local(obj, f):
    """Canonical (left -> right) LOCAL kick-level spans for a straight
    member: [(points, kind)] with kind 'FRONT' (always carries
    molding: flush faces, floor stiles including their side returns),
    'KICK' (always carries molding at the kick line - legs - and never
    receives a drop-boundary return), 'RECESS' (dropped unless opted
    in) or 'SKIP' (appliances, refrigerator openings)."""
    width, depth, _ = cage_dims(obj)
    V = mathutils.Vector
    front = -depth
    kick = f.get('kick') or {}
    if f.get('role') == 'APPLIANCE' or kick.get('skip'):
        return [([V((0.0, front)), V((width, front))], 'SKIP')]
    setback = kick.get('setback', 0.0)
    if kick.get('leg'):
        # Leg products: the leg's foot itself stays bare - the molding
        # lives INSIDE the toe kick, running across the leg at the
        # setback line (at the front when the leg has no kick).
        # Finished sides wrap from there to the rear via the terminal
        # end treatment. 'KICK' spans always carry molding but never
        # receive a drop-boundary return - they are already at the
        # kick line.
        r = front + setback
        return [([V((0.0, r)), V((width, r))], 'KICK')]
    if setback <= 1e-5:
        return [([V((0.0, front)), V((width, front))], 'FRONT')]
    r = front + setback
    spans = []
    left_stile = kick.get('stile_left') and kick.get('stile_left_w', 0.0) > 1e-5
    right_stile = kick.get('stile_right') and kick.get('stile_right_w', 0.0) > 1e-5
    x0 = kick.get('stile_left_w', 0.0) if left_stile else 0.0
    x1 = width - (kick.get('stile_right_w', 0.0) if right_stile else 0.0)
    if left_stile:
        spans.append(([V((0.0, front)), V((x0, front)), V((x0, r))], 'FRONT'))
    # middle_skip: no kick face exists between the stiles (refrigerator
    # openings) - the span is dropped outright, never opted back in.
    mid_kind = 'SKIP' if kick.get('middle_skip') else 'RECESS'
    # Flush sections (bays whose front runs to the floor) are carved
    # out of the recessed middle: the molding wraps out of the recess,
    # across the flush face, and back.
    cursor = x0
    for fx0, fx1 in kick.get('flush_spans') or []:
        fx0 = max(fx0, cursor)
        fx1 = min(fx1, x1)
        if fx1 - fx0 < 1e-5:
            continue
        if fx0 - cursor > 1e-5:
            spans.append(([V((cursor, r)), V((fx0, r))], mid_kind))
        spans.append(([V((fx0, r)), V((fx0, front)), V((fx1, front)),
                       V((fx1, r))], 'FRONT'))
        cursor = fx1
    if x1 - cursor > 1e-5:
        spans.append(([V((cursor, r)), V((x1, r))], mid_kind))
    if right_stile:
        spans.append(([V((x1, r)), V((x1, front)), V((width, front))],
                      'FRONT'))
    return spans


def _assemble_kick_spans(chain, facts):
    """World-space kick-level spans through the chain in travel order:
    ([(points, kind)], terminals). Corner members contribute their
    front polyline (inset to the kick face when recessed)."""
    spans = []
    terminals = [None, None]

    def _center(obj):
        fp = footprint_xy(obj)
        return sum(fp, mathutils.Vector((0.0, 0.0))) / 4.0

    n = len(chain)
    for i, obj in enumerate(chain):
        mw = obj.matrix_world
        f = facts[id(obj)]
        prev_ref = spans[-1][0][-1] if spans else None
        next_ref = _center(chain[i + 1]) if i + 1 < n else None

        width, depth, _ = cage_dims(obj)
        bl = _xy(mw @ mathutils.Vector((0.0, 0.0, 0.0)))
        br = _xy(mw @ mathutils.Vector((width, 0.0, 0.0)))
        fl = _xy(mw @ mathutils.Vector((0.0, -depth, 0.0)))
        fr = _xy(mw @ mathutils.Vector((width, -depth, 0.0)))

        if f.get('corner'):
            data = corner_plan_data(obj, f['corner'])
            local_pts = data['front']
            kick = f.get('kick') or {}
            kind = 'FRONT'
            if kick.get('skip'):
                kind = 'SKIP'
            elif kick.get('setback', 0.0) > 1e-5:
                local_pts = offset_polyline_right(
                    local_pts, -kick['setback'])
                kind = 'RECESS'
            cage_spans = [([
                _xy(mw @ mathutils.Vector((p.x, p.y, 0.0)))
                for p in local_pts], kind)]
            ends = {}
            for key in ('left_end', 'right_end'):
                fp, bp = data[key]
                ends[key] = (
                    _xy(mw @ mathutils.Vector((fp.x, fp.y, 0.0))),
                    _xy(mw @ mathutils.Vector((bp.x, bp.y, 0.0))),
                )
            first_pt = cage_spans[0][0][0]
            last_pt = cage_spans[-1][0][-1]
            reverse = False
            if prev_ref is not None:
                reverse = ((prev_ref - first_pt).length
                           > (prev_ref - last_pt).length)
            elif next_ref is not None:
                reverse = ((next_ref - last_pt).length
                           > (next_ref - first_pt).length)
            entry_key, exit_key = 'left_end', 'right_end'
            if reverse:
                cage_spans = [(list(reversed(p)), k)
                              for p, k in reversed(cage_spans)]
                entry_key, exit_key = exit_key, entry_key
            spans.extend(cage_spans)
            if i == 0:
                terminals[0] = {
                    'obj': obj,
                    'side': 'left' if entry_key == 'left_end' else 'right',
                    'front': ends[entry_key][0],
                    'back': ends[entry_key][1],
                }
            if i == n - 1:
                terminals[1] = {
                    'obj': obj,
                    'side': 'left' if exit_key == 'left_end' else 'right',
                    'front': ends[exit_key][0],
                    'back': ends[exit_key][1],
                }
        else:
            cage_spans = [
                ([_xy(mw @ mathutils.Vector((p.x, p.y, 0.0))) for p in pts],
                 kind)
                for pts, kind in _kick_spans_local(obj, f)
            ]
            # Orient by which SIDE of the member the neighbor sits on
            # (local-X projection) - endpoint-distance comparison flips
            # narrow members whose spans carry an asymmetric return
            # tail (legs, single floor stiles).
            inv = mw.inverted()

            def _local_x(p2):
                return (inv @ mathutils.Vector((p2.x, p2.y, 0.0))).x

            reverse = False
            if prev_ref is not None:
                reverse = _local_x(prev_ref) > width / 2.0
            elif next_ref is not None:
                reverse = _local_x(next_ref) < width / 2.0
            if reverse:
                cage_spans = [(list(reversed(p)), k)
                              for p, k in reversed(cage_spans)]
            spans.extend(cage_spans)
            if i == 0:
                terminals[0] = {'obj': obj,
                                'side': 'right' if reverse else 'left',
                                'front': fr if reverse else fl,
                                'back': br if reverse else bl}
            if i == n - 1:
                terminals[1] = {'obj': obj,
                                'side': 'left' if reverse else 'right',
                                'front': fl if reverse else fr,
                                'back': bl if reverse else br}
    return spans, terminals


def _stretch_segments(spans, include_recessed, x_off,
                      facts=None, terminals=None, island=False):
    """Offset path segments from a span list. Kept spans (FRONT and
    KICK always, RECESS when opted in) merge into stretches; a FRONT
    stretch that meets a dropped span appends its adjacent endpoint so
    the molding RETURNS into the finished kick. Stretches already at
    the kick line (KICK, RECESS) never return - they die in place
    rather than jutting out toward an appliance front. Chain-extremity ends get the finished /
    unfinished treatment (suppressed on island perimeters). Returns
    [(points, cyclic)]."""
    kept_kinds = ({'FRONT', 'KICK', 'RECESS'} if include_recessed
                  else {'FRONT', 'KICK'})
    n = len(spans)

    if island and all(kind in kept_kinds for _p, kind in spans):
        loop = []
        for pts, _kind in spans:
            loop.extend(pts)
        loop = offset_polygon_right(loop, x_off)
        return [(loop, True)] if len(loop) >= 3 else []

    order = list(range(n))
    if island:
        first_dropped = next(
            (k for k in order if spans[k][1] not in kept_kinds), None)
        if first_dropped is not None:
            order = order[first_dropped:] + order[:first_dropped]

    def _fresh_return(neighbors, pt):
        """False when a drop-boundary return point would double back
        over a return the kept span already carries (leg wraps end off
        the front line; re-adding the shared front corner would zig)."""
        return all((pt - p).length > 1e-6 for p in neighbors)

    segments = []
    current = None
    current_meta = None
    for pos, k in enumerate(order):
        pts, kind = spans[k]
        if kind in kept_kinds:
            if current is None:
                current = []
                current_meta = {'start_idx': k}
                if pos > 0 and kind == 'FRONT':
                    prev_k = order[pos - 1]
                    if spans[prev_k][1] not in kept_kinds:
                        p = spans[prev_k][0][-1]
                        if _fresh_return(pts[:2], p):
                            current.append(p)
            current.extend(pts)
            current_meta['end_idx'] = k
            current_meta['last_kind'] = kind
        else:
            if current is not None:
                if (current_meta.get('last_kind') == 'FRONT'
                        and _fresh_return(current[-2:], pts[0])):
                    current.append(pts[0])
                segments.append((current, current_meta))
                current = None
    if current is not None:
        if island:
            seam = spans[order[0]]
            if seam[1] not in kept_kinds:
                p = seam[0][0]
                if (current_meta.get('last_kind') == 'FRONT'
                        and _fresh_return(current[-2:], p)):
                    current.append(p)
        segments.append((current, current_meta))

    out = []
    reached = [False, False]
    for pts, meta in segments:
        off = offset_polyline_right(pts, x_off)
        if len(off) < 2:
            continue
        if not island and terminals is not None and facts is not None:
            for side_idx, at_extreme in (
                    (0, meta['start_idx'] == 0),
                    (1, meta['end_idx'] == n - 1)):
                if not at_extreme:
                    continue
                reached[side_idx] = True
                term = terminals[side_idx]
                if term is None:
                    continue
                outward = ((pts[0] - pts[1]) if side_idx == 0
                           else (pts[-1] - pts[-2]))
                if outward.length < 1e-6:
                    continue
                outward.normalize()
                f = facts[id(term['obj'])]
                if not f.get('finished_%s' % term['side'], False):
                    continue
                if side_idx == 0:
                    off[0] = off[0] + outward * x_off
                    off.insert(0, term['back'] + outward * x_off)
                else:
                    off[-1] = off[-1] + outward * x_off
                    off.append(term['back'] + outward * x_off)
        out.append((off, False))

    # A FINISHED end on a recessed-kick member carries molding no
    # matter what Include Recessed says - that option only governs the
    # recess line. With the recess line excluded, nothing reaches the
    # extremity and the side gets a standalone piece from the kick face
    # to the carcass rear, dying flush at both ends. (With it included,
    # the kept recess run reaches the extremity and the inline wrap
    # above miters around the corner instead.) It never runs to the
    # front corner: a stile extended to the floor turns the extremity
    # span FRONT and reaches it too.
    if not island and terminals is not None and facts is not None:
        for side_idx in (0, 1):
            if reached[side_idx]:
                continue
            term = terminals[side_idx]
            if term is None:
                continue
            if spans[0 if side_idx == 0 else -1][1] != 'RECESS':
                continue
            f = facts[id(term['obj'])]
            if not f.get('finished_%s' % term['side'], False):
                continue
            front = term.get('front')
            back = term.get('back')
            if front is None or back is None:
                continue
            toward_back = back - front
            depth_len = toward_back.length
            setback = (f.get('kick') or {}).get('setback', 0.0)
            if depth_len < 1e-6 or depth_len - setback < 1e-6:
                continue
            edge = front + toward_back * (setback / depth_len)
            raw = [back, edge] if side_idx == 0 else [edge, back]
            off = offset_polyline_right(raw, x_off)
            if len(off) >= 2:
                out.append((off, False))
    return out


def _island_perimeter_spans(members, facts):
    """Perimeter span walk for a free-standing island: a single row, or
    a back-to-back double row (two facings pi apart). A back-to-back
    island is not a linear chain - every back-row member touches the
    front row - but its perimeter is well defined. Returns the cyclic
    span list, or None when the layout isn't a recognizable island."""
    if any(facts[id(m)].get('corner') for m in members):
        return None
    rows = {}
    for m in members:
        rows.setdefault(round(m.matrix_world.to_euler().z, 2), []).append(m)
    if len(rows) > 2:
        return None
    row_list = list(rows.values())
    if len(row_list) == 2:
        keys = list(rows)
        diff = abs(keys[0] - keys[1]) % (2.0 * math.pi)
        if abs(diff - math.pi) > 0.05:
            return None

    def _travel(m):
        fn = front_normal_xy(m)
        if fn.length < 1e-6:
            return mathutils.Vector((1.0, 0.0))
        return mathutils.Vector((-fn.y, fn.x))

    def _center(m):
        fp = footprint_xy(m)
        return sum(fp, mathutils.Vector((0.0, 0.0))) / 4.0

    def _front_corners(m):
        w, d, _ = cage_dims(m)
        mw = m.matrix_world
        return (_xy(mw @ mathutils.Vector((0.0, -d, 0.0))),
                _xy(mw @ mathutils.Vector((w, -d, 0.0))))

    def _back_corners(m):
        w, _d, _ = cage_dims(m)
        mw = m.matrix_world
        return (_xy(mw @ mathutils.Vector((0.0, 0.0, 0.0))),
                _xy(mw @ mathutils.Vector((w, 0.0, 0.0))))

    def _corner_toward(corners, direction):
        a, b = corners
        return a if a.dot(direction) >= b.dot(direction) else b

    def _row_spans(row):
        t = _travel(row[0])
        ordered = sorted(row, key=lambda m: _center(m).dot(t))
        spans = []
        for m in ordered:
            mw = m.matrix_world
            xdir3 = mw.to_3x3() @ mathutils.Vector((1.0, 0.0, 0.0))
            forward = mathutils.Vector((xdir3.x, xdir3.y)).dot(t) > 0.0
            cage_spans = [
                ([_xy(mw @ mathutils.Vector((p.x, p.y, 0.0))) for p in pts],
                 kind)
                for pts, kind in _kick_spans_local(m, facts[id(m)])
            ]
            if not forward:
                cage_spans = [(list(reversed(p)), k)
                              for p, k in reversed(cage_spans)]
            spans.extend(cage_spans)
        return spans, ordered, t

    row_a = row_list[0]
    spans_a, ordered_a, t_a = _row_spans(row_a)
    spans = list(spans_a)

    if len(row_list) == 2:
        spans_b, ordered_b, _t_b = _row_spans(row_list[1])
        far_a = _corner_toward(_front_corners(ordered_a[-1]), t_a)
        far_b = _corner_toward(_front_corners(ordered_b[0]), t_a)
        near_b = _corner_toward(_front_corners(ordered_b[-1]), -t_a)
        near_a = _corner_toward(_front_corners(ordered_a[0]), -t_a)
        spans.append(([far_a, far_b], 'FRONT'))
        spans.extend(spans_b)
        spans.append(([near_b, near_a], 'FRONT'))
    else:
        far_f = _corner_toward(_front_corners(ordered_a[-1]), t_a)
        far_b = _corner_toward(_back_corners(ordered_a[-1]), t_a)
        near_b = _corner_toward(_back_corners(ordered_a[0]), -t_a)
        near_f = _corner_toward(_front_corners(ordered_a[0]), -t_a)
        spans.append(([far_f, far_b], 'FRONT'))
        back_pts = [far_b]
        for m in reversed(ordered_a):
            a, b = _back_corners(m)
            last = back_pts[-1]
            if (last - a).length <= (last - b).length:
                back_pts.extend([a, b])
            else:
                back_pts.extend([b, a])
        back_pts.append(near_b)
        spans.append((back_pts, 'FRONT'))
        spans.append(([near_b, near_f], 'FRONT'))
    return spans


def _stands_on_wall(obj):
    """True when this cabinet hangs off a wall.

    The whole parent chain is walked, not just obj.parent: a
    free-standing run gets collected under a group cage, and a cabinet
    parented to that cage is still free-standing. Testing the immediate
    parent alone reads a grouped island as wall-hung and costs it the
    perimeter walk below.
    """
    node = obj
    while node is not None:
        if node.get('IS_WALL_BP'):
            return True
        node = node.parent
    return False


def kick_sweep_segments(chain, facts, x_off, include_recessed):
    """[(world_points, cyclic)] base-molding segments for one run.
    Free-standing runs wrap as island perimeters; on-wall runs follow
    each member's own kick configuration with returns into finished
    kicks at every drop boundary."""
    raw, _terms, first_straight = _assemble_front_raw(chain, facts)
    if first_straight is not None and len(raw) >= 2:
        idx, fn = first_straight
        travel = raw[idx + 1] - raw[idx]
        if travel.length > 1e-6:
            travel.normalize()
            right = mathutils.Vector((travel.y, -travel.x))
            if right.dot(fn) < 0:
                chain = list(reversed(chain))

    if chain and not any(_stands_on_wall(c) for c in chain):
        perimeter = _island_perimeter_spans(chain, facts)
        if perimeter is not None:
            return _stretch_segments(perimeter, include_recessed, x_off,
                                     island=True)

    spans, terminals = _assemble_kick_spans(chain, facts)
    if not spans:
        return []
    return _stretch_segments(spans, include_recessed, x_off,
                             facts=facts, terminals=terminals, island=False)
