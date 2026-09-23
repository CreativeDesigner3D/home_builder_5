"""Where a cabinet sits along its wall, for the Cabinets-mode size labels.

Both cabinet overlays (face frame and frameless dim_edit_overlay) show,
beside a cabinet's own W / H / D, how it sits in its run:

- the gap to the nearest neighbor on each side (another product whose
  height range overlaps the cabinet's, so a window above a base cabinet
  isn't its neighbor), when there is one and the gap is open;
- the distance from each end of the wall to the cabinet (only asked
  for on a selected cabinet: on every cabinet of a run they would stack
  along the same bottom edge).

The neighbor scan is the placement system's own
(PlacementMixin.get_wall_children_sorted), so the overlay reports the
same gaps placement snaps to. Everything comes back in cabinet-local X /
Z so each overlay can put it on its own front plane.
"""

from ... import hb_placement, hb_types
from ...units import inch

# Gaps / end distances at or below this are flush -- no label.
MIN_SHOWN = inch(0.5)

KINDS = ('CAB_GAP_L', 'CAB_GAP_R', 'CAB_END_L', 'CAB_END_R')


def _wall_length(wall_obj):
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return None
    try:
        return wall.get_input('Length')
    except Exception:
        return None


def run_dims(cabinet, width, height, ends=True):
    """[(kind, value, prefix, (x0, z), (x1, z), key)] for ``cabinet``,
    the endpoints in cabinet-local X / Z with x0 < x1. Empty unless the
    cabinet hangs straight off a wall (not grouped, not turned on it).
    ``ends`` adds the wall-end distances.

    Gaps run at mid height; wall-end distances run along the cabinet's
    bottom edge so the two rows don't collide. ``key`` names the span
    on the wall: two cabinets either side of one gap both report it,
    and the caller shows it once.
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
    if left:
        start = max(left)
        gap = x0 - start
        if gap > MIN_SHOWN:
            out.append(('CAB_GAP_L', gap, "← ", (-gap, mid), (0.0, mid),
                        key(start, x0)))
    if right:
        end = min(right)
        gap = end - x1
        if gap > MIN_SHOWN:
            out.append(('CAB_GAP_R', gap, "→ ",
                        (width, mid), (width + gap, mid), key(x1, end)))
    if not ends:
        return out
    if x0 > MIN_SHOWN:
        out.append(('CAB_END_L', x0, "Wall ← ", (-x0, 0.0), (0.0, 0.0),
                    ('END', cabinet.name, 'L')))
    end_r = wall_len - x1
    if end_r > MIN_SHOWN:
        out.append(('CAB_END_R', end_r, "Wall → ",
                    (width, 0.0), (width + end_r, 0.0),
                    ('END', cabinet.name, 'R')))
    return out
