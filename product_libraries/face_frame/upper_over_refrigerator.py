"""An upper dropped over a standalone refrigerator raises a bay over it.

A refrigerator standing on the wall is a placement obstacle like any
other product, so an upper used to stop at its side. When the fridge is
short enough for an upper to sit on top of it, the upper can now be
placed across it instead: while it is placed, such a fridge doesn't
block (fridges_under() feeds the placement exclusions), and when it is
dropped the bays are laid out so one bay spans the fridge and is raised
-- shortened from the bottom, uppers being top-aligned -- to sit on the
fridge's top (plan() + apply()).

Where the stiles go: a mid stile hangs down to the lower of the two bays
it separates, so the stiles either side of the raised bay sit just
OUTSIDE the fridge -- the raised bay's frame spans the fridge and
nothing hangs in front of it. The upper's own end stiles count toward
the span when the raised bay is at an end.

Only a fresh placement does this; moving or duplicating an upper keeps
the fridge as an obstacle.
"""

import math

from ... import hb_types
from ...units import inch
from ..common import appliance_geo

# The raised bay has to keep at least this much height, or there's no
# upper to speak of over the fridge -- the fridge stays an obstacle.
MIN_RAISED_HEIGHT = inch(6.0)
# Narrowest opening the raised bay may have.
MIN_RAISED_OPENING = inch(3.0)
# A piece of the upper beside the fridge narrower than this can't hold a
# bay of its own; it joins the raised bay (which then overhangs the
# fridge a little) instead.
MIN_SIDE_SPAN = inch(6.0)
# Same-side test: the fridge and the upper stand off the same wall face.
SAME_SIDE_TOL = inch(6.0)
MAX_BAY_WIDTH = inch(36.0)


def _is_standalone_refrigerator(obj):
    if not obj.get('IS_APPLIANCE'):
        return False
    if obj.get('APPLIANCE_TYPE') != 'REFRIGERATOR':
        return False
    # One housed in a cabinet belongs to that cabinet, not the wall run.
    return not obj.get(appliance_geo.CABINET_APPLIANCE_FLAG)


def _extent(fridge):
    """(x0, x1, top_z) in its wall's local space, or None."""
    cage = hb_types.GeoNodeCage(fridge)
    try:
        w = cage.get_input('Dim X')
        h = cage.get_input('Dim Z')
    except Exception:
        return None
    x0 = fridge.location.x
    return x0, x0 + w, fridge.location.z + h


def fridges_under(wall, upper_x0, upper_x1, upper_y, upper_top):
    """[(fridge, x0, x1, top_z)] for standalone refrigerators on
    ``wall`` (on the upper's side) that an upper topping out at
    ``upper_top`` can sit over with a raised bay. ``upper_x0`` /
    ``upper_x1`` limit it to fridges the upper overlaps and ``upper_y``
    to its side of the wall; pass None to skip either test (the
    placement preview, which doesn't know yet where the upper lands)."""
    if wall is None or not wall.get('IS_WALL_BP'):
        return []
    out = []
    for child in wall.children:
        if not _is_standalone_refrigerator(child):
            continue
        if (upper_y is not None
                and abs(child.location.y - upper_y) > SAME_SIDE_TOL):
            continue
        ext = _extent(child)
        if ext is None:
            continue
        x0, x1, top = ext
        if upper_top - top < MIN_RAISED_HEIGHT:
            continue
        if upper_x0 is not None and (x1 <= upper_x0 or x0 >= upper_x1):
            continue
        out.append((child, x0, x1, top))
    return out


def side_bay_counts(upper_x0, width, fridge):
    """(left_bays, right_bays) either side of the raised bay, or None
    when the upper doesn't reach over ``fridge`` far enough to raise a
    bay. Decided before the cabinet is built -- the bay count is a
    create() argument."""
    _obj, f0, f1, _top = fridge
    a = max(f0, upper_x0) - upper_x0
    b = min(f1, upper_x0 + width) - upper_x0
    if b - a < MIN_RAISED_OPENING:
        return None
    left = a if a >= MIN_SIDE_SPAN else 0.0
    right = (width - b) if width - b >= MIN_SIDE_SPAN else 0.0
    n_left = math.ceil(left / MAX_BAY_WIDTH) if left > 0.0 else 0
    n_right = math.ceil(right / MAX_BAY_WIDTH) if right > 0.0 else 0
    return n_left, n_right


def plan(cab_props, upper_x0, upper_z, fridge, counts):
    """[(opening_width, raised_height or None)] per bay, left to right,
    for a built cabinet with ``sum(counts) + 1`` bays, or None when the
    stiles leave no room."""
    _obj, f0, f1, top = fridge
    n_left, n_right = counts
    width = cab_props.width
    lsw = cab_props.left_stile_width
    rsw = cab_props.right_stile_width
    mids = [m.width for m in cab_props.mid_stile_widths]
    if len(mids) < n_left + n_right:
        return None
    a = max(f0, upper_x0) - upper_x0 if n_left else 0.0
    b = min(f1, upper_x0 + width) - upper_x0 if n_right else width

    bays = []
    if n_left:
        # lsw, then n_left bays each followed by its mid stile; the last
        # of those stiles ends where the fridge starts.
        room = a - lsw - sum(mids[:n_left])
        bays += [(room / n_left, None)] * n_left
    raised = (b - a
              - (lsw if not n_left else 0.0)
              - (rsw if not n_right else 0.0))
    bays.append((raised, cab_props.height - (top - upper_z)))
    if n_right:
        room = (width - b) - rsw - sum(mids[n_left:n_left + n_right])
        bays += [(room / n_right, None)] * n_right

    if any(w < MIN_RAISED_OPENING for w, _h in bays):
        return None
    if bays[n_left][1] < MIN_RAISED_HEIGHT:
        return None
    return bays


def apply(cab_obj, bay_plan):
    """Write ``bay_plan`` onto the cabinet's bays: every width held (so
    the stiles land where the plan put them), the raised bay's height
    held at its raised size."""
    from . import types_face_frame
    bays = sorted(
        [c for c in cab_obj.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0))
    if len(bays) != len(bay_plan):
        return False
    with types_face_frame.suspend_recalc():
        for bay_obj, (width, height) in zip(bays, bay_plan):
            bp = bay_obj.face_frame_bay
            bp.unlock_width = True
            bp.width = width
            if height is not None:
                bp.unlock_height = True
                bp.height = height
    return True
