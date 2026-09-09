"""A support frame that follows a path, rather than one rectangular box.

A frame drawn through several points is built as one ordinary support
frame per span, grouped so the run behaves as a single item. Nothing
downstream has to learn a new kind of object: each span carries the same
prompts, parts and legs a single frame does. What this module adds is
where each span goes and how two that meet at a corner get out of each
other's way.

The path is the frame's BACK line and the body stands to the RIGHT of
the direction it was drawn, which is the same relationship a single
frame has to its own origin. Drawing the path the other way round puts
the body on the other side.
"""

import math

from mathutils import Vector

from ...units import inch


# Below this a span is not worth building -- two points landing almost on
# top of each other, or a span trimmed away by the corner that follows it.
MIN_SPAN_LENGTH = inch(1.0)


def _right_of(vec):
    """``vec`` turned 90 degrees to the right: the side a span's body
    stands on, given the direction it runs."""
    return Vector((vec.y, -vec.x))


def spans_for_path(points, depth, closed=False):
    """Where each span of a path-drawn frame sits.

    Returns one dict per span -- ``origin`` (x, y), ``angle`` (Z rotation
    in radians), ``length``, and ``joins_next`` -- in drawing order.

    A span is cut short where the span after it turns into its end. Turn
    right and the two bodies would overlap through the corner, so this
    one stops a frame's depth back and the corner belongs to the span
    that turns; turn left and they open away from each other, so it runs
    the full length. The cut is scaled by how square the turn is, which
    makes a right angle lose exactly the frame depth and a gentle bend
    lose almost nothing.
    """
    pts = [Vector((p[0], p[1])) for p in points]
    if closed and len(pts) > 2:
        pts.append(pts[0])

    spans = []
    for i in range(len(pts) - 1):
        start, end = pts[i], pts[i + 1]
        run = end - start
        length = run.length
        if length <= 1e-6:
            continue
        direction = run.normalized()

        following = None
        if i + 2 < len(pts):
            following = pts[i + 2]
        elif closed and len(pts) > 2:
            following = pts[1]

        trim = 0.0
        if following is not None:
            onward = following - end
            if onward.length > 1e-6:
                trim = depth * max(
                    0.0, -_right_of(onward.normalized()).dot(direction))

        spans.append({
            'origin': (start.x, start.y),
            'angle': math.atan2(direction.y, direction.x),
            'length': max(length - trim, 0.0),
            'joins_next': following is not None,
        })
    return spans


def build_path_frame(points, make_frame, depth, z=0.0, closed=False):
    """Build a support frame along ``points``; return the span roots.

    ``make_frame(length)`` builds one support frame of that length and
    returns the wrapper around it -- the caller supplies it so this works
    for either product library's frame. Spans too short to build are
    skipped, so a stray double-click adds nothing rather than a sliver.
    """
    from ..frameless import types_products

    roots = []
    for span in spans_for_path(points, depth, closed=closed):
        if span['length'] < MIN_SPAN_LENGTH:
            continue
        frame = make_frame(span['length'])
        obj = frame.obj
        obj.location = (span['origin'][0], span['origin'][1], z)
        obj.rotation_euler = (0.0, 0.0, span['angle'])
        if span['joins_next']:
            # The span that turns owns the corner: this one drops the end
            # it would otherwise close against that span's side, and the
            # legs that would stand a frame's depth short of the corner
            # post rather than under it.
            obj['Right Rail'] = False
            obj['Front Right Leg'] = False
            obj['Back Right Leg'] = False
        types_products.recalculate_support_frame(obj)
        roots.append(obj)
    return roots
