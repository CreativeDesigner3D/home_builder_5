"""Closet starter layout solver.

Pure geometry math - no bpy. types_closets builds a spec from the live
PropertyGroups, this module returns explicit positions/dimensions, and
types_closets writes them to the objects. Keeping the math bpy-free means
this module can be hot-reloaded for smoke tests without a Blender restart.

Coordinate conventions (match face_frame):
- Starter origin at back-left, floor level. +X right, -Y forward, +Z up.
- Panels are numbered 0..N (N = bay count); panel i is the LEFT panel of
  bay i. Every panel anchors at its left edge and extrudes +X.
- Bay-local space: origin at the bay's back-left-bottom envelope corner.
  For a floor-mounted bay the envelope bottom is the FLOOR (the toe kick
  lives inside the envelope); for a hanging bay it is the underside of
  the bay's bottom shelf.

Panel sizing between two bays reproduces the legacy shared-panel rules:
the panel spans from the lowest neighbor bottom to the highest neighbor
top, so a floor-mounted bay next to a hanging bay yields a full-height
panel. Depth is the max of the neighbor depths.
"""

from . import const_closets as const


def distribute_widths(total_width, panel_thickness, bays, panel_total=None):
    """Split the interior width across bays.

    bays: list of dicts with 'width' and 'locked'. Locked bays hold their
    width; unlocked bays share the remainder equally (min MIN_BAY_WIDTH,
    so an over-constrained starter degrades visibly instead of going
    negative). Returns a list of widths, one per bay.

    panel_total: combined thickness of all vertical panels. Defaults to
    the plain (n+1) * pt; turned-off end panels and doubled junctions
    change it.
    """
    n = len(bays)
    if panel_total is None:
        panel_total = (n + 1) * panel_thickness
    interior = total_width - panel_total
    locked_total = sum(b['width'] for b in bays if b['locked'])
    unlocked = [i for i, b in enumerate(bays) if not b['locked']]
    widths = [b['width'] for b in bays]
    if unlocked:
        share = (interior - locked_total) / len(unlocked)
        share = max(share, const.MIN_BAY_WIDTH)
        for i in unlocked:
            widths[i] = share
    elif widths and locked_total > 0:
        # Every bay locked: nothing can absorb a total-width change, so
        # scale all bays proportionally - panels must still close to the
        # starter width.
        scale = interior / locked_total
        widths = [w * scale for w in widths]
    return widths


def _side_top(bay, height):
    """Absolute Z of a panel's top on one neighbor side."""
    return bay['height'] if bay['floor'] else height


def _side_bottom(bay, height):
    """Absolute Z of a panel's bottom on one neighbor side."""
    return 0.0 if bay['floor'] else height - bay['height']


def compute_layout(spec):
    """Full starter layout.

    spec attributes: width, height, pt (panel thickness), st (shelf
    thickness), kick_height, kick_setback, and bays - a list of dicts with
    width, locked, height, depth, floor, remove_bottom, remove_cleat.

    Returns a dict:
      widths:  final bay widths (write back to the bay props)
      panels:  list of dicts (x, z, length, depth) for panels 0..N
      bays:    list of dicts with the bay envelope (x, z0, width, height,
               depth, kick, floor) and bay-local part placements
               (bottom_z, top_z, cleat_z, interior_z, interior_h).
    """
    n = len(spec.bays)
    left_off = getattr(spec, 'left_panel_off', False)
    right_off = getattr(spec, 'right_panel_off', False)

    # Per-junction panel thickness: a turned-off
    # end panel gives its thickness back to the interior; a doubled
    # junction (bay['double_left']) takes two.
    t = []
    for i in range(n + 1):
        if i == 0:
            t.append(0.0 if left_off else spec.pt)
        elif i == n:
            t.append(0.0 if right_off else spec.pt)
        else:
            t.append(spec.pt * 2.0
                     if spec.bays[i].get('double_left') else spec.pt)
    widths = distribute_widths(spec.width, spec.pt, spec.bays,
                               panel_total=sum(t))

    # Junction left edges + bay left edges.
    xs = [0.0]
    bay_x = []
    for i, w in enumerate(widths):
        bay_x.append(xs[i] + t[i])
        xs.append(bay_x[i] + w)

    panels = []
    doubles = []
    for i in range(n + 1):
        left = spec.bays[i - 1] if i > 0 else None
        right = spec.bays[i] if i < n else None
        doubled = 0 < i < n and bool(spec.bays[i].get('double_left'))
        if doubled:
            # Doubled junction: the second panel
            # serves the LEFT bay; the primary panel shifts right one
            # thickness and serves the RIGHT bay only.
            doubles.append({
                'junction': i,
                'x': xs[i],
                'z': _side_bottom(left, spec.height),
                'length': (_side_top(left, spec.height)
                           - _side_bottom(left, spec.height)),
                'depth': left['depth'],
            })
            sides = [right]
            px = xs[i] + spec.pt
        else:
            sides = [s for s in (left, right) if s is not None]
            px = xs[i]
        top = max(_side_top(s, spec.height) for s in sides)
        bottom = min(_side_bottom(s, spec.height) for s in sides)
        panels.append({
            'x': px,
            'z': bottom,
            'length': top - bottom,
            'depth': max(s['depth'] for s in sides),
            'hidden': (i == 0 and left_off) or (i == n and right_off),
        })

    bays_out = []
    for i, b in enumerate(spec.bays):
        kick = spec.kick_height if b['floor'] else 0.0
        z0 = 0.0 if b['floor'] else spec.height - b['height']
        bottom_z = kick                       # bay-local underside of bottom shelf
        top_z = b['height'] - spec.st         # bay-local underside of top shelf
        interior_z = bottom_z + spec.st
        interior_h = max(top_z - interior_z, const.MIN_BAY_WIDTH / 4.0)
        # Cleat rides the bottom shelf; with the bottom removed it drops
        # to the bay envelope bottom (legacy behavior: the wall cleat
        # anchors the panels at the floor / hang line instead).
        cleat_z = 0.0 if b['remove_bottom'] else interior_z
        bays_out.append({
            'x': bay_x[i],
            'z0': z0,
            'width': widths[i],
            'height': b['height'],
            'depth': b['depth'],
            'kick': kick,
            'floor': b['floor'],
            'bottom_z': bottom_z,
            'top_z': top_z,
            'cleat_z': cleat_z,
            'interior_z': interior_z,
            'interior_h': interior_h,
        })

    return {'widths': widths, 'panels': panels, 'doubles': doubles,
            'bays': bays_out}
