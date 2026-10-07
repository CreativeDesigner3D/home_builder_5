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


def distribute_widths(total_width, panel_thickness, bays):
    """Split the interior width across bays.

    bays: list of dicts with 'width' and 'locked'. Locked bays hold their
    width; unlocked bays share the remainder equally (min MIN_BAY_WIDTH,
    so an over-constrained starter degrades visibly instead of going
    negative). Returns a list of widths, one per bay.
    """
    n = len(bays)
    interior = total_width - (n + 1) * panel_thickness
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
    widths = distribute_widths(spec.width, spec.pt, spec.bays)

    # Panel left edges: panel 0 at x=0, then alternate panel/bay runs.
    xs = [0.0]
    for w in widths:
        xs.append(xs[-1] + spec.pt + w)

    panels = []
    for i in range(n + 1):
        left = spec.bays[i - 1] if i > 0 else None
        right = spec.bays[i] if i < n else None
        sides = [s for s in (left, right) if s is not None]
        top = max(_side_top(s, spec.height) for s in sides)
        bottom = min(_side_bottom(s, spec.height) for s in sides)
        panels.append({
            'x': xs[i],
            'z': bottom,
            'length': top - bottom,
            'depth': max(s['depth'] for s in sides),
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
            'x': xs[i] + spec.pt,
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

    return {'widths': widths, 'panels': panels, 'bays': bays_out}
