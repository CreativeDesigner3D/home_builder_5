"""
Edge profiles for wood tops.

A wood top's edge is either milled into the slab itself or cut on an
applied hardwood band; either way the section is the same, so one
profile set serves both. The set extends the shelf-nosing styles --
those already cover the roundover / radius family and a top can be
nosed with the same stock -- with the two shapes that only ever show up
on a top edge: ogee and bullnose.

Outlines follow the shelf-nosing contract: (d, z) points in meters,
d forward from the profile's back face and z down from the top face
(z <= 0), ordered from the top-back corner around the free boundary to
the bottom-back corner, WITHOUT the closing back-face edge.

Like shelf_nosing, an asset pack can register a provider that supplies
exact profile outlines; the shapes generated here are the fallback so
this library works standalone. The provider is separate from the
shelf-nosing one on purpose: the same style name can be a different
shape on a top than on a shelf (a milled top edge is not an applied
band), and a single provider could not tell the two apart.
"""

import math

from . import shelf_nosing
from ...units import inch


# Profiles a top edge can carry that a shelf nosing never does.
_TOP_ONLY_ITEMS = [
    ('OGEE', "Ogee",
     "Convex roll over a cove, square face to the underside"),
    ('BULLNOSE', "Bullnose", "Full half-round across the edge thickness"),
]

EDGE_STYLE_ITEMS = shelf_nosing.NOSING_STYLE_ITEMS + _TOP_ONLY_ITEMS

_TOP_ONLY_STYLES = frozenset(key for key, _l, _d in _TOP_ONLY_ITEMS)

_ARC_STEPS = 12


_outline_provider = None


def register_outline_provider(fn):
    global _outline_provider
    _outline_provider = fn


def unregister_outline_provider(fn=None):
    global _outline_provider
    if fn is None or _outline_provider is fn:
        _outline_provider = None


def _arc(cd, cz, r, a0, a1, steps=_ARC_STEPS, skip_first=False):
    """Points along an arc from a0 to a1 (degrees), centred (cd, cz)."""
    out = []
    for i in range(1 if skip_first else 0, steps + 1):
        a = math.radians(a0 + (a1 - a0) * (i / steps))
        out.append((cd + r * math.cos(a), cz + r * math.sin(a)))
    return out


def _generated_outline(style, thickness):
    """Fallback shapes for the top-only profiles, proportional to the
    edge thickness so they hold up at any stock size."""
    t = thickness
    if style == 'BULLNOSE':
        r = t / 2.0
        return _arc(0.0, -r, r, 90, -90)
    # OGEE: a short flat off the top face, a convex quarter rolling out
    # and down, then a cove that flares back OUT to the full projection,
    # and a square face to the underside. The cove opening outward is
    # what makes it read as an ogee rather than a bulge.
    flat = 0.08 * t
    r1 = 0.30 * t
    r2 = 0.26 * t
    pts = [(0.0, 0.0), (flat, 0.0)]
    pts += _arc(flat, -r1, r1, 90, 0, skip_first=True)
    # cove centred outboard of the convex end, sweeping down and out
    pts += _arc(flat + r1, -r1 - r2, r2, 90, 0, skip_first=True)
    pts.append((flat + r1 + r2, -t))
    return pts


def edge_outline(style, thickness, height):
    """Section outline for a top edge style, or None for no profile.

    Provider first, then the generated top-only shapes, then the shared
    shelf-nosing outlines for every style the two sets have in common.
    """
    if not style or style == 'NONE':
        return None
    if _outline_provider is not None:
        try:
            outline = _outline_provider(style, thickness, height)
        except Exception:
            outline = None
        if outline:
            return outline if _has_projection(outline) else None
    if style in _TOP_ONLY_STYLES:
        return _generated_outline(style, thickness)
    return shelf_nosing.nosing_outline(style, thickness, height)


def _has_projection(outline):
    """False for an outline that never leaves the back face.

    A square top edge IS the board's own face, so its outline is a flat
    line. Milling that produces a zero-width prism against a core that
    has already been shrunk by the stock depth -- i.e. a notch out of
    the top. Callers treat it as 'no profile' instead.
    """
    return bool(outline) and max(d for d, _z in outline) > 1e-6


def stock_depth(outline):
    """How far back from the outer face the profiled band reaches.

    The nosing stock depth is the floor -- a profile shallower than the
    stock leaves a flat behind it, which is how applied nosing is
    actually run -- but a profile deeper than the stock grows the band
    rather than poking out past the top's outer face.
    """
    if not outline:
        return shelf_nosing.NOSE_STOCK_DEPTH
    return max(shelf_nosing.NOSE_STOCK_DEPTH,
               max(d for d, _z in outline),
               inch(0.0))
