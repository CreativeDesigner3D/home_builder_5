"""Finished-opening shelf nosing profiles.

A nosing is a solid-stock profile applied to the front edge of an
adjustable shelf in a finished opening. Two families:

- Shelf-thickness nosings (Clover, Kelli): decorative nose the same
  height as the shelf board, for shelves up to 36" wide.
- Extra-height nosings (Mini Mantle, 3/8" Drop Radius, Classic, Square,
  1/8" Radius, 3/8" Radius): a deeper band (1-1/4" to 3" high) that
  drops below the shelf, used on openings 36" to 48" wide.

Profiles are generated as 2D outlines in section space and swept along
the shelf front as a static mesh; the interior recalc wipes and
rebuilds them with the rest of the interior parts. Section space:
``d`` runs forward from the shelf front face, ``z`` runs down from the
shelf top (z <= 0), so the outline starts at the top-back corner
(0, 0) and ends at the bottom-back corner (0, -H).

The decorative outlines (Clover, Kelli, Mini Mantle, Classic) are
approximations of the catalog profiles; refine the outline builders
here to match shop tooling without touching any caller.
"""

import bpy
import bmesh
import math

from ...units import inch

# Solid stock the nosing is milled from (front-to-back).
NOSE_STOCK_DEPTH = inch(0.75)

NOSING_STYLE_ITEMS = [
    ('NONE', "None", "No nosing on the shelf front edge"),
    ('CLOVER', "Clover", "Shelf-thickness clover nose, shelves up to 36\" wide"),
    ('KELLI', "Kelli", "Shelf-thickness bullnose with step, shelves up to 36\" wide"),
    ('MINI_MANTLE', "Mini Mantle Moulding", "Extra-height mantle band, 1-1/2\" high"),
    ('DROP_RADIUS', "3/8\" Drop Radius", "Extra-height, 3/8\" roundover top, 1/8\" radius bottom edge"),
    ('CLASSIC', "Classic", "Extra-height, roundover top with cove bottom edge"),
    ('SQUARE', "Square", "Extra-height, square bottom edge"),
    ('RADIUS_18', "1/8\" Radius", "Extra-height, 1/8\" radius edges"),
    ('RADIUS_38', "3/8\" Radius", "Extra-height, 3/8\" radius edges"),
]

# Styles whose overall height comes from the item's nosing-height prop
# (1-1/4" to 3"). Clover / Kelli always match the shelf thickness.
EXTRA_HEIGHT_STYLES = frozenset({
    'MINI_MANTLE', 'DROP_RADIUS', 'CLASSIC',
    'SQUARE', 'RADIUS_18', 'RADIUS_38',
})


def _arc(cx, cz, r, a0, a1, segments=8):
    """Sample an arc around (cx, cz) from angle a0 to a1 (degrees,
    CCW positive), excluding the start point."""
    pts = []
    for i in range(1, segments + 1):
        a = math.radians(a0 + (a1 - a0) * i / segments)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def nosing_outline(style, shelf_thickness, height):
    """Closed section outline for a nosing style as (d, z) points.
    The implicit closing edge from the last point back to the first is
    the flat back face glued to the shelf front edge."""
    D = NOSE_STOCK_DEPTH
    T = shelf_thickness
    if style == 'CLOVER':
        # Two half-round lobes meeting at a pinch, full shelf thickness.
        back = inch(0.25)
        r = T / 4.0
        pts = [(0.0, 0.0), (back, 0.0)]
        pts += _arc(back, -r, r, 90, -90, 10)
        pts += _arc(back, -3.0 * r, r, 90, -90, 10)
        pts.append((0.0, -T))
        return pts
    if style == 'KELLI':
        # Half-round nose over a small step, full shelf thickness.
        r = inch(0.3125)
        dk = inch(0.625)
        pts = [(0.0, 0.0), (dk - r, 0.0)]
        pts += _arc(dk - r, -r, r, 90, -90, 12)
        pts.append((inch(0.125), -2.0 * r))
        pts.append((inch(0.125), -T))
        pts.append((0.0, -T))
        return pts
    H = max(height, T)
    if style in ('RADIUS_18', 'RADIUS_38'):
        r = inch(0.125) if style == 'RADIUS_18' else inch(0.375)
        pts = [(0.0, 0.0), (D - r, 0.0)]
        pts += _arc(D - r, -r, r, 90, 0, 6)
        pts.append((D, -(H - r)))
        pts += _arc(D - r, -(H - r), r, 0, -90, 6)
        pts.append((0.0, -H))
        return pts
    if style == 'DROP_RADIUS':
        r1, r2, taper = inch(0.375), inch(0.125), inch(0.0625)
        pts = [(0.0, 0.0), (D - r1, 0.0)]
        pts += _arc(D - r1, -r1, r1, 90, 0, 8)
        pts.append((D - taper, -(H - r2)))
        pts += _arc(D - taper - r2, -(H - r2), r2, 0, -90, 4)
        pts.append((0.0, -H))
        return pts
    if style == 'CLASSIC':
        rt, rb = inch(0.25), inch(0.25)
        pts = [(0.0, 0.0), (D - rt, 0.0)]
        pts += _arc(D - rt, -rt, rt, 90, 0, 8)
        pts.append((D, -(H - rb)))
        pts += _arc(D, -H, rb, 90, 180, 8)
        pts.append((0.0, -H))
        return pts
    if style == 'MINI_MANTLE':
        # Projecting top band with a cove under it, flat face below.
        rc = inch(0.25)
        band = inch(0.625)
        rb = inch(0.0625)
        pts = [(0.0, 0.0), (D, 0.0), (D, -band)]
        pts += _arc(D, -band - rc, rc, 90, 180, 8)
        pts.append((D - rc, -(H - rb)))
        pts += _arc(D - rc - rb, -(H - rb), rb, 0, -90, 3)
        pts.append((0.0, -H))
        return pts
    # SQUARE and any unknown style fall back to plain square stock.
    return [(0.0, 0.0), (D, 0.0), (D, -H), (0.0, -H)]


def build_nosing_object(name, length, style, shelf_thickness, height):
    """Sweep the style's outline along +X into a new (unlinked) mesh
    object. Object origin is the back-top-left corner of the nosing:
    the back face sits on the shelf front edge (section d maps to -Y)
    and the top is flush with the shelf top (section z maps to +Z)."""
    outline = nosing_outline(style, shelf_thickness, height)
    clean = [outline[0]]
    for p in outline[1:]:
        if (abs(p[0] - clean[-1][0]) > 1e-7
                or abs(p[1] - clean[-1][1]) > 1e-7):
            clean.append(p)
    bm = bmesh.new()
    ring0 = [bm.verts.new((0.0, -d, z)) for d, z in clean]
    ring1 = [bm.verts.new((length, -d, z)) for d, z in clean]
    bm.faces.new(ring0)
    bm.faces.new(list(reversed(ring1)))
    n = len(clean)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return bpy.data.objects.new(name, mesh)
