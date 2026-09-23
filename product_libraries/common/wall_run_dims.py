"""Where a cabinet sits along its wall, for the Cabinets-mode size labels.

Both cabinet overlays (face frame and frameless dim_edit_overlay) show,
beside a cabinet's own W / H / D, how it sits in its run: on each side,
a dimension to the nearest thing there -- the next product or appliance
whose height range overlaps the cabinet's (so a window above a base
cabinet isn't its neighbor), or the end of the wall when nothing is
between. A dimension never runs across another product, and a flush
side gets none.

The neighbor scan is the placement system's own
(PlacementMixin.get_wall_children_sorted), so the overlay reports the
same gaps placement snaps to. Everything comes back in cabinet-local X /
Z so each overlay can put it on its own front plane.
"""

from ... import hb_placement, hb_types
from ...units import inch

# At or below this a side is flush -- no label. Small on purpose: an
# 1/8" reveal beside an appliance is exactly what should show.
MIN_SHOWN = inch(1.0 / 32.0)

KINDS = ('CAB_GAP_L', 'CAB_GAP_R', 'CAB_END_L', 'CAB_END_R')


def _wall_length(wall_obj):
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return None
    try:
        return wall.get_input('Length')
    except Exception:
        return None


def run_dims(cabinet, width, height):
    """[(kind, value, prefix, (x0, z), (x1, z), key)] for ``cabinet``,
    the endpoints in cabinet-local X / Z with x0 < x1, at mid height.
    Empty unless the cabinet hangs straight off a wall (not grouped,
    not turned on it).

    CAB_GAP_* runs to a neighbor, CAB_END_* to the wall end. ``key``
    names the span on the wall: two cabinets either side of one gap
    both report it, and the caller shows it once.
    """
    wall_obj = cabinet.parent
    if wall_obj is None or not wall_obj.get('IS_WALL_BP'):
        return []
    if abs(cabinet.rotation_euler.z) > 1e-3:
        return []
    wall_len = _wall_length(wall_obj)
    if not wall_len or width <= 0.0 or height <= 0.0:
        return []

    x0 = cabinet.location.x
    x1 = x0 + width
    z0 = cabinet.location.z
    neighbors = hb_placement.PlacementMixin.get_wall_children_sorted(
        None, wall_obj, exclude_obj=cabinet,
        object_z_start=z0, object_height=height)
    eps = inch(1.0 / 32.0)
    left = [e for s, e, _o in neighbors if e <= x0 + eps]
    right = [s for s, e, _o in neighbors if s >= x1 - eps]

    def key(a, b):
        return (wall_obj.name, round(a, 4), round(b, 4))

    out = []
    mid = height / 2.0
    start = max(left) if left else 0.0
    gap = x0 - start
    if gap > MIN_SHOWN:
        out.append(('CAB_GAP_L' if left else 'CAB_END_L', gap,
                    "← " if left else "Wall ← ",
                    (-gap, mid), (0.0, mid), key(start, x0)))
    end = min(right) if right else wall_len
    gap = end - x1
    if gap > MIN_SHOWN:
        out.append(('CAB_GAP_R' if right else 'CAB_END_R', gap,
                    "→ " if right else "Wall → ",
                    (width, mid), (width + gap, mid), key(x1, end)))
    return out
