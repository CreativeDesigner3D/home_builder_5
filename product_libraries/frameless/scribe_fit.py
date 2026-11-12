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


def refit_scene(scene):
    """Refit every wall scribe filler in ``scene``. Returns those changed."""
    changed = []
    for obj in scene.objects:
        if not is_wall_scribe_filler(obj):
            continue
        try:
            if refit(obj):
                changed.append(obj)
        except Exception:
            traceback.print_exc()
    return changed
