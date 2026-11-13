"""Wall scribe fillers keep to the gap they close.

A filler stands in the space between a cabinet and a wall (or whatever
else ends the run). When that space changes -- the cabinet beside it is
resized or moved, or the filler's own width is typed -- the filler is
put back on the gap: its width becomes the gap's and it starts where
the gap starts, so it never runs into the wall or over the cabinet.

Only a narrow gap is followed (``FILL_MAX``); a wider one leaves the
filler as it stands. A filler that touches neither end of the gap it is
in was put there on purpose and is left alone too.
"""
import math
import traceback

from ... import hb_placement, hb_types, units
from . import types_products

# The widest gap a wall scribe filler fills of its own accord.
FILL_MAX = units.inch(6.0)
# Edges closer than this are the same edge.
TOL = units.inch(1.0 / 32.0)
# How far inside its own edge a filler is probed for the gap it is in.
PROBE = units.inch(1.0 / 16.0)


def is_wall_scribe_filler(obj):
    return (obj is not None and obj.get('PART_TYPE') == 'CORNER_FILLER'
            and obj.parent is not None and bool(obj.parent.get('IS_WALL_BP')))


def _side(obj):
    """True on the wall's front, False on its back, None when the
    filler is turned some other way."""
    turn = math.remainder(obj.rotation_euler.z, 2.0 * math.pi)
    if abs(turn) < 0.1:
        return True
    if abs(abs(turn) - math.pi) < 0.1:
        return False
    return None


def refit(filler):
    """Put ``filler`` back on the gap it stands in. True when it moved
    or changed width."""
    if not is_wall_scribe_filler(filler):
        return False
    on_front = _side(filler)
    if on_front is None:
        return False
    wall_obj = filler.parent
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return False
    cage = hb_types.GeoNodeCage(filler)
    width = cage.get_input('Dim X')
    if width <= 0.0:
        return False
    # A back-side filler is turned 180, so its origin is its right edge.
    if on_front:
        x0, x1 = filler.location.x, filler.location.x + width
    else:
        x0, x1 = filler.location.x - width, filler.location.x
    finder = hb_placement.PlacementMixin()
    for probe in (x0 + PROBE, x1 - PROBE):
        g0, g1, _snap = finder.find_placement_gap_by_side(
            wall_obj, probe, 0.0, on_front, wall.get_input('Thickness'),
            object_z_start=filler.location.z,
            object_height=cage.get_input('Dim Z'),
            object_depth=abs(cage.get_input('Dim Y')),
            exclude_obj=filler)
        if g0 is None or not (g0 <= probe <= g1):
            continue
        gap = g1 - g0
        if not (TOL < gap <= FILL_MAX + TOL):
            continue
        if not (abs(x0 - g0) <= TOL or abs(x1 - g1) <= TOL):
            continue
        if abs(x0 - g0) <= 1e-5 and abs(x1 - g1) <= 1e-5:
            return False
        cage.set_input('Dim X', gap)
        filler.location.x = g0 if on_front else g1
        types_products.recalculate_product(filler)
        return True
    return False


def _wall_span(obj, width):
    """(x0, x1) along the wall, or None when turned some other way."""
    on_front = _side(obj)
    if on_front is None:
        return None
    if on_front:
        return obj.location.x, obj.location.x + width
    return obj.location.x - width, obj.location.x


def neighbour_cabinet(filler):
    """The cabinet a wall scribe filler stands against: the one on the
    same side of the wall whose end meets the filler's cabinet edge at
    the filler's height."""
    if not is_wall_scribe_filler(filler):
        return None
    on_front = _side(filler)
    span = _wall_span(filler, hb_types.GeoNodeCage(filler).get_input('Dim X'))
    if span is None:
        return None
    cab_right = bool(filler.get('Cabinet On Right', True))
    # A back-side filler is turned 180, which swaps its sides.
    high = cab_right if on_front else not cab_right
    edge = span[1] if high else span[0]
    for obj in filler.parent.children:
        if not obj.get('IS_FRAMELESS_CABINET_CAGE') or _side(obj) != on_front:
            continue
        if abs(obj.location.z - filler.location.z) > TOL:
            continue
        other = _wall_span(obj, hb_types.GeoNodeCage(obj).get_input('Dim X'))
        if other is not None and abs((other[0] if high else other[1]) - edge) <= TOL:
            return obj
    return None


def bottom_return_finished(filler):
    """Whether a filler's bottom return shows a finished underside: it
    does when the bottom of the cabinet beside it is finished, or has a
    finished panel applied under it."""
    cabinet = neighbour_cabinet(filler)
    if cabinet is None:
        return False
    from . import solver_frameless
    from .operators import ops_finished_ends
    if int(cabinet.get(solver_frameless.FINISHED_BOTTOM_KEY, 0) or 0):
        return True
    return ops_finished_ends.finish_condition(cabinet, 'BOTTOM') == 'FINISHED'


def sync_bottom_return(filler):
    """Re-solve a filler whose bottom return's finish no longer matches
    the cabinet beside it. True when it changed."""
    if not filler.get(types_products.BOTTOM_RETURN_KEY):
        return False
    part = types_products.product_parts(filler).get('FILLER_BOTTOM_RETURN')
    if part is None:
        return False
    if bool(part.get('Finish Bottom')) == bottom_return_finished(filler):
        return False
    types_products.recalculate_product(filler)
    return True


def refit_scene(scene):
    """Refit every wall scribe filler in ``scene``, and put its bottom
    return's finish right. Returns those changed."""
    changed = []
    for obj in scene.objects:
        if not is_wall_scribe_filler(obj):
            continue
        try:
            moved = refit(obj)
            if sync_bottom_return(obj) or moved:
                changed.append(obj)
        except Exception:
            traceback.print_exc()
    return changed
