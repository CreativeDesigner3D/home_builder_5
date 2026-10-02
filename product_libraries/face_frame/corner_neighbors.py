"""Keep the runs tight when a corner cabinet's legs are resized.

A corner cabinet's two arm ends sit on different walls: the right arm
ends at local (width, 0), the left arm at (0, -depth). When the user
changes width or depth, the arm end moves along that wall. Whatever
cabinet was butted against the old arm end is resized by the same amount
so it still meets the corner, with its far edge left where it was -
instead of a void (or an overlap) opening between them.

Only a direct user edit drives this. Writes made under suspend_recalc()
(placement, templates, batch copies) are system writes that position
cabinets themselves, so they are left alone.
"""

from mathutils import Vector

from ... import hb_utils, units
from . import exposure, types_face_frame

# How close a neighbour's end must sit to the old arm end to count as
# butted against it.
_MEET_TOL = units.inch(0.125)
_MIN_WIDTH = units.inch(1.0)


def _arm_end(mw, local):
    w = mw @ Vector(local)
    return Vector((w.x, w.y))


def _butted_neighbor(root, point):
    """(cabinet, end) whose end sits at `point`, or None."""
    for nb in exposure._scene_carcasses():
        if nb is root or exposure._is_corner_cabinet(nb):
            continue
        if not exposure._zspans_overlap(root, nb):
            continue
        for end in ('left', 'right'):
            if (exposure._end_meet_point(nb, end) - point).length <= _MEET_TOL:
                return nb, end
    return None


def follow_corner_resize(root, old_width, old_depth):
    """Resize the cabinets butted against `root`'s arm ends after its
    width / depth changed from (old_width, old_depth) to the current
    values. Returns the cabinets that were resized."""
    if types_face_frame._RECALC_SUSPEND_DEPTH > 0:
        return []
    cab = root.face_frame_cabinet
    if cab.corner_type == 'NONE':
        return []
    from .props_hb_face_frame import _width_axis
    mw = hb_utils.world_matrix(root)
    moves = (
        ((old_width, 0.0, 0.0), (cab.width, 0.0, 0.0)),
        ((0.0, -old_depth, 0.0), (0.0, -cab.depth, 0.0)),
    )
    changed = []
    with exposure.scene_scan():
        for local_old, local_new in moves:
            p_old = _arm_end(mw, local_old)
            p_new = _arm_end(mw, local_new)
            if (p_new - p_old).length < 1e-6:
                continue
            hit = _butted_neighbor(root, p_old)
            if hit is None:
                continue
            nb, end = hit
            nprops = nb.face_frame_cabinet
            if nprops.lock_width:
                continue
            axis = hb_utils.world_matrix(nb).to_3x3() @ Vector((1.0, 0.0, 0.0))
            if axis.length < 1e-9:
                continue
            axis.normalize()
            # How far the arm end moved along the neighbour's width axis.
            d = (p_new - p_old).dot(Vector((axis.x, axis.y)))
            new_width = nprops.width + (d if end == 'right' else -d)
            if new_width < _MIN_WIDTH:
                continue
            # A system write: the neighbour's own anchor side must not
            # shift it, and it must not auto-lock as a user edit would.
            types_face_frame._DISTRIBUTING_WIDTHS.add(id(nb))
            try:
                nprops.width = new_width
            finally:
                types_face_frame._DISTRIBUTING_WIDTHS.discard(id(nb))
            if end == 'left':
                # Origin is the left edge; slide it so the far (right)
                # edge holds.
                nb.location += _width_axis(nb) * d
            nb['HB_ANCHOR_LAST_WIDTH'] = new_width
            changed.append(nb)
    return changed
