"""An upper placed across a range or cooktop centers a bay over it.

A range is shorter than the uppers, so it never blocked them, and an
upper running across it laid its bays out evenly with no regard for
where the cooking surface was. Now a fresh upper that covers a range
standing on the wall -- or a cooktop set into a base cabinet on the
wall -- is laid out the way an upper over a refrigerator is
(upper_over_refrigerator): one bay over the cooking surface, its
opening the width of the range with the stiles just outside it, and
bays either side for the rest. The bay keeps its full height.

An over-the-range microwave goes under that bay when asked for (M while
placing): the bay's Under Cabinet Appliance, sized to the range, which
raises the opening over it.

Only a fresh placement does this, like the refrigerator.
"""

from ... import hb_types
from ..common import appliance_geo
from . import upper_over_refrigerator as _fridge

# Same-side test: the range and the upper stand off the same wall face.
SAME_SIDE_TOL = _fridge.SAME_SIDE_TOL
# The upper has to cover the cooking surface to within this.
COVER_TOL = 0.0127


def _cage_dim(obj, name):
    try:
        return hb_types.GeoNodeCage(obj).get_input(name)
    except Exception:
        return None


def _wall_local_x_span(wall, obj, width):
    """(x0, x1) of ``obj``'s width along ``wall``, in wall space. Built
    from the parent chain (matrix_parent_inverse @ matrix_basis) rather
    than matrix_world, which is stale for anything placed in the same
    pass."""
    from mathutils import Matrix, Vector
    m = Matrix.Identity(4)
    node = obj
    while node is not None and node != wall:
        m = node.matrix_parent_inverse @ node.matrix_basis @ m
        node = node.parent
    a = m @ Vector((0.0, 0.0, 0.0))
    b = m @ Vector((width, 0.0, 0.0))
    return min(a.x, b.x), max(a.x, b.x)


def _is_cooking(obj, kind):
    return (obj.get('IS_APPLIANCE')
            and obj.get('APPLIANCE_TYPE') == kind)


def cooking_spots(wall, upper_y):
    """[(appliance, x0, x1, None)] for the ranges and cooktops on
    ``wall``, on the upper's side (``upper_y`` None skips that test).
    A range stands on the wall by itself; a cooktop sits in a base
    cabinet's bay. Shaped like upper_over_refrigerator's fridge tuples
    so its bay layout functions take them."""
    if wall is None or not wall.get('IS_WALL_BP'):
        return []
    out = []
    for child in wall.children:
        if (upper_y is not None
                and abs(child.location.y - upper_y) > SAME_SIDE_TOL):
            continue
        if (_is_cooking(child, 'RANGE')
                and not child.get(appliance_geo.CABINET_APPLIANCE_FLAG)):
            found = [child]
        else:
            found = [o for o in child.children_recursive
                     if _is_cooking(o, 'COOKTOP')]
        for obj in found:
            width = _cage_dim(obj, 'Dim X')
            if not width:
                continue
            x0, x1 = _wall_local_x_span(wall, obj, width)
            out.append((obj, x0, x1, None))
    return out


def pick(wall, upper_x0, width, upper_y):
    """(spot, counts) for an upper at ``upper_x0`` .. ``+width`` on
    ``wall``: the range or cooktop it covers and the bays either side
    of the one centered over it, or None. Only a cooking surface the
    upper covers whole counts. Counts (0, 0) is an upper about the
    range's width: one bay, already over it, that only takes the
    microwave. The placement preview and the drop both ask this."""
    upper_x1 = upper_x0 + width
    spots = [s for s in cooking_spots(wall, upper_y)
             if s[1] >= upper_x0 - COVER_TOL and s[2] <= upper_x1 + COVER_TOL]
    if not spots:
        return None
    spot = min(spots, key=lambda s: abs((s[1] + s[2]) / 2.0
                                        - (upper_x0 + upper_x1) / 2.0))
    counts = _fridge.side_bay_counts(upper_x0, width, spot)
    if counts is None:
        return None
    return spot, counts


def plan(cab_props, upper_x0, upper_z, spot, counts):
    """Bay widths for the built cabinet, the center bay at full height
    (see upper_over_refrigerator.plan), or None."""
    return _fridge.plan(cab_props, upper_x0, upper_z, spot, counts,
                        raise_bay=False)


def apply(cab_obj, bay_plan, counts, spot, microwave):
    """Write the bay widths (a one-bay upper keeps its own), then hang
    the microwave under the center bay when asked for, sized to the
    cooking surface."""
    if counts != (0, 0) and not _fridge.apply(cab_obj, bay_plan):
        return False
    if not microwave:
        return True
    from . import types_face_frame
    bays = sorted(
        [c for c in cab_obj.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0))
    center = bays[counts[0]].face_frame_bay
    center.under_cabinet_appliance_width = spot[2] - spot[1]
    center.under_cabinet_appliance = 'MICROWAVE'
    return True
