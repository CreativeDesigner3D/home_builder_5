"""Decorative corner posts on a cabinet's vertical corners.

A decorative corner is a turned / milled post let into a vertical
corner of the cabinet: the carcass is notched square, the post fills the
notch, and its outer face carries a profile. Islands and exposed run
ends are the usual hosts, so the post is offered per corner (front
left / right, back left / right).

The face frame is NOT notched. On a front corner the whole frame moves
over by the post size and its end stile butts into the post (see
solver_face_frame.decorative_corner_insets); only carcass parts, end
skins and kicks are cut around it. The stile beside a post is a 1-1/2"
member (1-1/4" on full overlay) -- props_hb_face_frame writes that
width when the corner is switched on.

Anatomy, bottom to top (the vendor calls the plain square sections
"square blocks"; a bead ring over a short square is one "transition
detail"):

    square block  -- the transition detail's base, DETAIL_HEIGHT tall,
                     flush with both cabinet faces so it reads proud of
                     the profiled shaft
    astragal      -- half-round bead ring standing proud of both
                     cabinet faces, run a short way past each face
                     and rounded off into it (returned into itself)
    shaft         -- the styled run: 2" radius / colonial / fluted
    astragal
    square block  -- the "square block run" crown moulding dies into

Section geometry. Every band is a radius function about the notch's
INNER corner, so one loft builds the whole post. Post-local section
space puts that inner corner at the origin with the post filling the
first quadrant; the two cabinet faces the corner opens onto are the
planes ``u = size`` and ``v = size``, and the two flat faces at
``theta = 0`` / ``theta = 90`` are the notch's cut faces:

    square    r(theta) = size / max(cos, sin)   (corner at size * sqrt2)
    shaft     r(theta) = the style profile, <= size
    astragal  r(theta) = size + projection * bulge, proud of both faces

A plain shaft at ``r = size`` is a quarter round tangent to both
cabinet faces -- that is the 2" radius style, and it is why the styles
share one radius model. The profile is symmetric about the 45 degree
diagonal, so all four corners are pure Z rotations of one mesh.

The colonial outline is a measured table of the catalog profile
(fillet, cove, bead, quirk, ovolo) normalized to the post size; refine
COLONIAL_HALF_PROFILE to match shop tooling without touching any
caller.

Clipped corners are the same post with a flat 45 degree face: the
straight line from one cabinet face to the other across the notch,
``r(theta) = size / (cos + sin)``, so a 2" corner shows a 2-13/16"
face. They have no transition details or square blocks - the clip runs
the full post. The size is free (2", 6", 12" ...), unlike the turned
styles. The Gothic version routes half-round ball cuts down the clip,
equally spaced across it and stopped short of each end.
"""

import math

import bpy
import bmesh

from ... import hb_utils
from ...units import inch


# Nominal post face size. The catalog corners are 2" x 2".
DEFAULT_SIZE = inch(2.0)
# Bead ring height, how far it stands proud of the cabinet faces, and
# how far it runs past each face before rounding off into it.
ASTRAGAL_HEIGHT = inch(0.75)
ASTRAGAL_PROJECTION = inch(0.25)
ASTRAGAL_RETURN = inch(0.5)
# Square base of a transition detail (under the bead ring at the
# bottom of the post).
DEFAULT_DETAIL_HEIGHT = inch(3.0)
# Plain square-block run above the top transition detail, for crown.
DEFAULT_BLOCK_RUN = inch(3.0)
# End stile beside a post: standard overlays / full overlay.
STILE_WIDTH = inch(1.5)
STILE_WIDTH_FULL_OVERLAY = inch(1.25)
# Depth the reeds are cut below the shaft's outer radius.
REED_DEPTH = inch(0.1875)
REED_COUNT = 5
# Land (flat) between reeds, as a fraction of one reed's width. Five
# reeds and six lands at this ratio put the reed pitch at about 1/2"
# on a 2" post, which is the catalog's fluting.
REED_LAND_RATIO = 0.383
# Gothic clipped corner: half-round ball cuts down the clipped face,
# equally spaced across it, stopped short of both ends of the post.
BALL_CUT_DIAMETER = inch(0.375)
DEFAULT_BALL_CUTS = 3
DEFAULT_ROUTE_STOP = inch(1.0)
# Stepped ball cuts (as on a Gothic stile): the centre cut stops this far
# below the top of the post, and each cut out from it is STEP_SHORTER
# shorter at both ends. 0 = every cut stops at the route stop.
DEFAULT_CENTER_CUT_TOP = inch(1.0)
STEP_SHORTER = inch(1.0)

# Shortest shaft worth building. Below this the post drops its end
# details rather than emitting slivers.
MIN_SHAFT_RUN = inch(1.0)

PART_ROLE = 'DECORATIVE_CORNER'
PART_ROLE_CUTTER = 'DECORATIVE_CORNER_CUTTER'
CUT_MOD_NAME = 'Decorative Corner'

STYLE_ITEMS = [
    ('NONE', "None", "No decorative corners"),
    ('RADIUS', "2\" Radius",
     "Quarter round tangent to both cabinet faces"),
    ('COLONIAL', "Colonial",
     "Milled colonial outline - fillet, cove, bead, quirk and ovolo"),
    ('FLUTED', "Fluted (Reeded)",
     "Reeded shaft - half-round beads separated by flat lands"),
    ('CLIPPED', "Clipped Corner",
     "Flat 45 degree clip across the corner, any size"),
    ('GOTHIC', "Clipped Corner - Gothic (Ball Cut)",
     "Clipped corner with half-round ball cuts routed down the clip"),
]

# Styles that cut the corner off flat rather than turning a post. They
# take any size and have no transition details or square blocks.
CLIPPED_STYLES = frozenset({'CLIPPED', 'GOTHIC'})


def is_clipped(style):
    return style in CLIPPED_STYLES

BOTTOM_ITEMS = [
    ('STANDARD', "Standard Application",
     "Post stops at the bottom of the cabinet box, no bottom detail"),
    ('RECESSED_KICK', "Recessed Kick with Transition Detail",
     "Post stops at the bottom of the cabinet box over a recessed "
     "kick, ending in a transition detail"),
    ('EXTENDED_FLOOR', "Recessed Kick, Stile to Floor",
     "Post runs past a recessed kick to the floor, with a transition "
     "detail at the box bottom"),
    ('FLUSH_BLOCK', "Flush Kick with Square Bottom Block",
     "Post runs to the floor over a flush kick, with a transition "
     "detail above a square bottom block"),
]

# Corner key -> (is_right_end, is_front). Cabinet local space runs
# X 0..width left to right, Y 0 (back) to -depth (front), Z 0..height.
CORNERS = (
    ('FRONT_LEFT', "Front Left"),
    ('FRONT_RIGHT', "Front Right"),
    ('BACK_LEFT', "Back Left"),
    ('BACK_RIGHT', "Back Right"),
)

# Bands, outermost first so a stack reads bottom to top.
_SQUARE = 'SQUARE'
_ASTRAGAL = 'ASTRAGAL'
_SHAFT = 'SHAFT'
# Plain clip, the unrouted ends of a Gothic clipped corner.
_CLIP = 'CLIP'

# Parts the corner notch cuts through. An explicit allow-list, like the
# pipe chase's: the notch box overshoots the cabinet faces so the
# boolean never grazes a coplanar face, and that overshoot reaches into
# the door plane -- fronts must stay out of it. The face frame is not
# here either: it is built inboard of the post (its end stile butts
# into it) rather than notched.
CUT_PART_ROLES = frozenset({
    # Carcass
    'LEFT_SIDE', 'RIGHT_SIDE', 'TOP', 'BOTTOM',
    # A seamed side is two boards; the post notch runs the
    # full corner, so both of them get cut.
    'LEFT_SIDE_SEAM', 'RIGHT_SIDE_SEAM',
    'BACK', 'FINISHED_BACK',
    'FRONT_STRETCHER', 'REAR_STRETCHER',
    # Applied end skins and blind ends
    'FLUSH_X', 'BEADBOARD', 'SHIPLAP', 'V_GROOVE',
    'BLIND_PANEL_LEFT', 'BLIND_PANEL_RIGHT',
    'LEFT_SIDE_RETURN', 'RIGHT_SIDE_RETURN',
    'LEFT_SIDE_RETURN_STILE', 'RIGHT_SIDE_RETURN_STILE',
    # Finished bottom panel under an upper
    'FINISHED_BOTTOM',
    # Toe kick, for the options that run the post past it to the floor
    'TOE_KICK_SUBFRONT', 'FINISH_TOE_KICK', 'MID_FINISH_KICK',
    'REAR_FINISH_TOE_KICK',
    'LEFT_CORNER_FINISH_KICK', 'RIGHT_CORNER_FINISH_KICK',
    'LEFT_KICK_RETURN', 'RIGHT_KICK_RETURN',
    'LEFT_KICK_RETURN_CLOSURE', 'RIGHT_KICK_RETURN_CLOSURE',
    'LEFT_KICK_CLOSURE_FINISH', 'RIGHT_KICK_CLOSURE_FINISH',
    'LOOSE_KICK_FRONT', 'LOOSE_KICK_REAR',
    'LOOSE_KICK_END_LEFT', 'LOOSE_KICK_END_RIGHT',
})

# Colonial outline, measured off the catalog section and normalized to
# the post size: (theta degrees from the first cabinet face, r / size).
# Only the first half is stored -- the profile is symmetric about the
# 45 degree diagonal and _style_radius mirrors it.
COLONIAL_HALF_PROFILE = (
    (0.00, 1.00000),
    (2.90, 0.99112),
    (4.63, 0.97631),
    (6.14, 0.95530),
    (7.35, 0.92882),
    (8.43, 0.88046),   # fillet lands on the cove
    (10.49, 0.88578),
    (10.89, 0.86121),
    (11.75, 0.84155),
    (12.83, 0.82829),
    (14.11, 0.82018),
    (15.49, 0.81745),  # cove bottom
    (16.88, 0.82028),
    (18.76, 0.83520),
    (20.50, 0.80217),  # quirk under the ovolo
    (22.54, 0.83799),
    (24.67, 0.87010),
    (26.88, 0.89848),
    (29.16, 0.92341),
    (31.49, 0.94483),
    (33.87, 0.96290),
    (36.29, 0.97745),
    (38.74, 0.98855),
    (41.24, 0.99604),
    (43.78, 0.99974),
    (45.00, 1.00000),  # ovolo apex on the diagonal
)


# ----------------------------------------------------------------------
# Section profiles
# ----------------------------------------------------------------------
def _reed_spans():
    """(start, end) of each reed in degrees, with equal lands between
    them and at both ends, so the reeding is symmetric about 45."""
    width = 90.0 / (REED_COUNT + REED_LAND_RATIO * (REED_COUNT + 1))
    land = width * REED_LAND_RATIO
    return [(land + k * (width + land), land + k * (width + land) + width)
            for k in range(REED_COUNT)]


def _clip_point(size, s):
    """(u, v) on the clipped face, ``s`` along it from the 45 degree
    diagonal (positive towards the u face)."""
    half = size / 2.0
    k = s / math.sqrt(2.0)
    return half + k, half - k


def _ball_cut_centers(size, count):
    """Positions of the ball cuts along the clipped face, measured from
    its centre: equally spaced, with the same gap at both edges. A face
    too narrow for the count keeps as many as fit."""
    face = size * math.sqrt(2.0)
    count = max(0, int(count))
    while count > 0:
        pitch = face / (count + 1)
        if pitch >= BALL_CUT_DIAMETER * 1.25:
            break
        count -= 1
    if count <= 0:
        return []
    pitch = face / (count + 1)
    return [-face / 2.0 + pitch * (k + 1) for k in range(count)]


def _sample_degrees(style, size=DEFAULT_SIZE, ball_cuts=DEFAULT_BALL_CUTS):
    """Angles the section is sampled at, 0 to 90 inclusive. 45 is always
    present: the square blocks crease there."""
    if style == 'CLIPPED':
        # A straight clip: its two ends and the diagonal are exact.
        return [0.0, 45.0, 90.0]
    if style == 'GOTHIC':
        degs = {0.0, 45.0, 90.0}
        rg = BALL_CUT_DIAMETER / 2.0
        for c in _ball_cut_centers(size, ball_cuts):
            for i in range(13):
                u, v = _clip_point(size, c - rg + 2.0 * rg * i / 12.0)
                degs.add(math.degrees(math.atan2(v, u)))
        return sorted(d for d in degs if 0.0 <= d <= 90.0)
    if style == 'COLONIAL':
        degs = {0.0, 45.0, 90.0}
        for deg, _ratio in COLONIAL_HALF_PROFILE:
            degs.add(deg)
            degs.add(90.0 - deg)
        return sorted(degs)
    if style == 'FLUTED':
        degs = {0.0, 45.0, 90.0}
        for start, end in _reed_spans():
            degs.add(start)
            degs.add(end)
            for i in range(1, 12):
                degs.add(start + (end - start) * i / 12.0)
        return sorted(degs)
    # Plain quarter round: 3 degree steps hold the arc well under a
    # thousandth of an inch off on a 2" post.
    return [i * 3.0 for i in range(31)]


def _lerp_table(table, deg):
    """Linear read of a (degrees, ratio) table, clamped at both ends."""
    if deg <= table[0][0]:
        return table[0][1]
    for i in range(1, len(table)):
        d1, r1 = table[i]
        if deg <= d1:
            d0, r0 = table[i - 1]
            span = d1 - d0
            if span <= 0.0:
                return r1
            return r0 + (r1 - r0) * (deg - d0) / span
    return table[-1][1]


def _clip_radius(size, deg):
    """Radius of the flat clip: the line from one cabinet face to the
    other across the notch."""
    rad = math.radians(deg)
    return size / (math.cos(rad) + math.sin(rad))


def _style_radius(style, size, deg, ball_cuts=DEFAULT_BALL_CUTS,
                  active=None):
    """Shaft radius at one section angle. ``active`` limits a Gothic
    clip to the ball cuts of those indices (None = all of them)."""
    if style == 'CLIPPED':
        return _clip_radius(size, deg)
    if style == 'GOTHIC':
        rad = math.radians(deg)
        cs = math.cos(rad) + math.sin(rad)
        r0 = size / cs
        # Where this ray meets the clip, along the clip from its centre.
        s = r0 * (math.cos(rad) - math.sin(rad)) / math.sqrt(2.0)
        rg = BALL_CUT_DIAMETER / 2.0
        for k, c in enumerate(_ball_cut_centers(size, ball_cuts)):
            if active is not None and k not in active:
                continue
            if abs(s - c) < rg:
                depth = math.sqrt(max(0.0, rg * rg - (s - c) ** 2))
                # Back along the ray far enough to sit ``depth`` under
                # the clipped face.
                return r0 - depth * math.sqrt(2.0) / cs
        return r0
    if style == 'COLONIAL':
        half = deg if deg <= 45.0 else 90.0 - deg
        return size * _lerp_table(COLONIAL_HALF_PROFILE, half)
    if style == 'FLUTED':
        land = size - REED_DEPTH
        for start, end in _reed_spans():
            if start <= deg <= end:
                # Half-round bead: vertical tangents onto the lands.
                u = 2.0 * (deg - start) / (end - start) - 1.0
                return land + REED_DEPTH * math.sqrt(max(0.0, 1.0 - u * u))
        return land
    return size


def _square_radius(size, deg):
    """Radius of the notch square itself, so a square block is a band of
    the same loft. Proud of the shaft everywhere but the two ends."""
    rad = math.radians(deg)
    return size / max(math.cos(rad), math.sin(rad))


def _band_radii(kind, style, size, deg, bulge, ball_cuts=DEFAULT_BALL_CUTS):
    if kind == _SQUARE:
        return _square_radius(size, deg)
    if kind == _CLIP:
        return _clip_radius(size, deg)
    if isinstance(kind, tuple):
        # (_SHAFT, cut indices): a stepped Gothic band where only some of
        # the ball cuts run.
        return _style_radius(style, size, deg, ball_cuts, kind[1])
    if style in CLIPPED_STYLES:
        return _style_radius(style, size, deg, ball_cuts)
    # The bead ring is its own shell (see _ring_shell); the main loft
    # runs the shaft straight through its band.
    return _style_radius(style, size, deg)


def _ring_shell(style, size, z0, z1, base_index):
    """(verts, faces) of one bead ring as a closed tube shell.

    The ring is a half-round bead swept about the notch corner: proud
    of both cabinet faces by ASTRAGAL_PROJECTION at its apex, running
    ASTRAGAL_RETURN past each face onto the frame / side and rounding
    off there (a bead returned into itself), the way the shop makes
    it. Its inner surface tucks just under the shaft's deepest cut so
    the ring reads as turned from the post, and its extension past the
    faces sits a hair inside the cabinet planes so nothing is coplanar.
    """
    ret_deg = math.degrees(ASTRAGAL_RETURN / size)
    inset = inch(0.005)
    r_base = size - inset
    r_in = min(_style_radius(style, size, d) for d in _sample_degrees(style))
    r_in = min(r_in, r_base) - inch(0.03)
    z_steps = 8
    end_steps = 6

    degs = [-ret_deg + ret_deg * i / end_steps for i in range(end_steps)]
    degs += [i * 3.0 for i in range(31)]
    degs += [90.0 + ret_deg * (i + 1) / end_steps for i in range(end_steps)]

    def end_scale(deg):
        over = -deg if deg < 0.0 else (deg - 90.0 if deg > 90.0 else 0.0)
        if over <= 0.0:
            return 1.0
        u = min(over / ret_deg, 1.0)
        return math.sqrt(max(0.0, 1.0 - u * u))

    verts = []
    sections = []
    for deg in degs:
        rad = math.radians(deg)
        cx, cy = math.cos(rad), math.sin(rad)
        scale = end_scale(deg)
        loop = []
        # Closed section: inner bottom -> inner top -> outer, top to
        # bottom, so consecutive sections loft into a tube.
        loop.append((r_in * cx, r_in * cy, z0))
        loop.append((r_in * cx, r_in * cy, z1))
        for i in range(z_steps + 1):
            t = 1.0 - i / float(z_steps)
            r = r_base + ASTRAGAL_PROJECTION * math.sin(math.pi * t) * scale
            loop.append((r * cx, r * cy, z0 + (z1 - z0) * t))
        sections.append(len(verts))
        verts.extend(loop)
    m = z_steps + 3
    faces = []
    for k in range(len(sections) - 1):
        a = base_index + sections[k]
        b = base_index + sections[k + 1]
        for j in range(m):
            j2 = (j + 1) % m
            faces.append((a + j, a + j2, b + j2, b + j))
    first = base_index + sections[0]
    last = base_index + sections[-1]
    faces.append(tuple(first + j for j in range(m)))
    faces.append(tuple(last + j for j in reversed(range(m))))
    return verts, faces


# ----------------------------------------------------------------------
# Vertical band stack
# ----------------------------------------------------------------------
def post_bottom_z(bottom_option, kick_height):
    """Cabinet-local Z the post starts at. The two 'to floor' options
    run past a kick; the others sit on the cabinet box bottom."""
    if bottom_option in ('EXTENDED_FLOOR', 'FLUSH_BLOCK'):
        return 0.0
    return max(0.0, kick_height)


def band_stack(height, kick_height, bottom_option, top_detail, block_run,
               detail_height=DEFAULT_DETAIL_HEIGHT):
    """[(z0, z1, kind)] bottom to top, or None when there is no room.

    The bottom transition detail is a bead ring over a DETAIL_HEIGHT
    square base (the "to floor" options run that base on down past the
    kick); the top detail is a bead ring under the square block run
    crown moulding dies into. The two lengths are independent - a
    taller crown block must not stretch the detail at the floor.

    End details are all-or-nothing: if adding them would leave less
    than MIN_SHAFT_RUN of shaft the post falls back to one plain run,
    rather than emitting a stack of slivers on a short cabinet.
    """
    z_bot = post_bottom_z(bottom_option, kick_height)
    z_top = height
    if z_top - z_bot <= 0.0:
        return None
    lower = []
    upper = []
    shaft_z0, shaft_z1 = z_bot, z_top
    if bottom_option != 'STANDARD':
        a0 = max(0.0, kick_height) + detail_height
        lower = [(z_bot, a0, _SQUARE), (a0, a0 + ASTRAGAL_HEIGHT, _ASTRAGAL)]
        shaft_z0 = a0 + ASTRAGAL_HEIGHT
    if top_detail:
        b0 = z_top - block_run - ASTRAGAL_HEIGHT
        upper = [(b0, b0 + ASTRAGAL_HEIGHT, _ASTRAGAL),
                 (b0 + ASTRAGAL_HEIGHT, z_top, _SQUARE)]
        shaft_z1 = b0
    if shaft_z1 - shaft_z0 < MIN_SHAFT_RUN:
        return [(z_bot, z_top, _SHAFT)]
    return lower + [(shaft_z0, shaft_z1, _SHAFT)] + upper


def _stepped_cut_spans(z_bot, z_top, count, stop, center_top):
    """{cut index: (z0, z1)} for stepped ball cuts: the centre cut (the
    middle two on an even count) runs from ``stop`` above the bottom to
    ``center_top`` below the top, each cut further out STEP_SHORTER
    shorter at both ends. Cuts too short to route are left out."""
    mid = (count - 1) / 2.0
    spans = {}
    for k in range(count):
        step = math.floor(abs(k - mid) + 1e-9) * STEP_SHORTER
        z0, z1 = z_bot + stop + step, z_top - center_top - step
        if z1 - z0 >= MIN_SHAFT_RUN:
            spans[k] = (z0, z1)
    return spans


def clipped_band_stack(height, kick_height, bottom_option, style,
                       route_stop=DEFAULT_ROUTE_STOP, center_top=0.0,
                       size=DEFAULT_SIZE, ball_cuts=DEFAULT_BALL_CUTS):
    """[(z0, z1, kind)] for a clipped corner, or None when there is no
    room. The clip runs the whole post; a Gothic corner's ball cuts stop
    ``route_stop`` short of each end, and a post too short to route
    stays a plain clip. ``center_top`` > 0 steps the cuts (see
    _stepped_cut_spans): bands where only some cuts run carry the kind
    (_SHAFT, frozenset of cut indices)."""
    z_bot = post_bottom_z(bottom_option, kick_height)
    z_top = height
    if z_top - z_bot <= 0.0:
        return None
    if style != 'GOTHIC':
        return [(z_bot, z_top, _CLIP)]
    stop = max(0.0, route_stop)
    if center_top > 0.0:
        count = len(_ball_cut_centers(size, ball_cuts))
        spans = _stepped_cut_spans(z_bot, z_top, count, stop, center_top)
        if not spans:
            return [(z_bot, z_top, _CLIP)]
        cuts = sorted({z_bot, z_top} | {z for s in spans.values() for z in s})
        bands = []
        for a, b in zip(cuts, cuts[1:]):
            if b - a <= 1e-9:
                continue
            mid_z = (a + b) / 2.0
            on = frozenset(k for k, (z0, z1) in spans.items()
                           if z0 <= mid_z <= z1)
            if not on:
                kind = _CLIP
            elif len(on) == count:
                kind = _SHAFT
            else:
                kind = (_SHAFT, on)
            if bands and bands[-1][2] == kind:
                bands[-1] = (bands[-1][0], b, kind)
            else:
                bands.append((a, b, kind))
        return bands
    if z_top - z_bot - 2.0 * stop < MIN_SHAFT_RUN:
        return [(z_bot, z_top, _CLIP)]
    if stop <= 0.0:
        return [(z_bot, z_top, _SHAFT)]
    return [(z_bot, z_bot + stop, _CLIP),
            (z_bot + stop, z_top - stop, _SHAFT),
            (z_top - stop, z_top, _CLIP)]


def _band_rings(bands):
    """[(z, kind, bulge)] rings for the loft. Bands meet at a shared Z
    with different radii, so each boundary emits two rings and the quads
    between them close the step as a horizontal face. The bead rings
    are separate shells, so their bands loft as plain shaft here."""
    rings = []
    for z0, z1, kind in bands:
        rings.append((z0, kind, 0.0))
        rings.append((z1, kind, 0.0))
    return rings


# ----------------------------------------------------------------------
# Mesh
# ----------------------------------------------------------------------
def build_post_mesh(mesh, style, size, bands, ball_cuts=DEFAULT_BALL_CUTS):
    """Regenerate mesh as the lofted post in post-local section space.

    Section space: the notch's inner corner is the origin, the post
    fills the first quadrant, and the cabinet faces are u = size and
    v = size. Every ring is one centre vertex plus the boundary
    samples, so the two flat cut faces fall out of the loft. The bead
    rings are added as their own shells afterwards.
    """
    degs = _sample_degrees(style, size, ball_cuts)
    dirs = [(math.cos(math.radians(d)), math.sin(math.radians(d)))
            for d in degs]
    n = len(degs)

    # Resolve each ring's radii, then drop a ring that repeats the one
    # under it: a plain shaft meets its astragal at the same radius, and
    # lofting between two identical rings would emit a band of zero-area
    # faces for mesh.validate() to strip, tearing the shell open.
    rings = []
    for z, kind, bulge in _band_rings(bands):
        radii = [_band_radii(kind, style, size, deg, bulge, ball_cuts)
                 for deg in degs]
        if rings and abs(rings[-1][0] - z) < 1e-9:
            prev = rings[-1][1]
            if all(abs(a - b) < 1e-9 for a, b in zip(prev, radii)):
                continue
        rings.append((z, radii))

    verts = []
    for z, radii in rings:
        verts.append((0.0, 0.0, z))
        for r, (cx, cy) in zip(radii, dirs):
            verts.append((r * cx, r * cy, z))

    stride = n + 1
    faces = []
    for i in range(len(rings) - 1):
        a = i * stride
        b = (i + 1) * stride
        for j in range(n - 1):
            faces.append((a + 1 + j, a + 2 + j, b + 2 + j, b + 1 + j))
        # The two flat faces against the notch, sharing the centre edge.
        faces.append((a, a + 1, b + 1, b))
        faces.append((a, b, b + n, a + n))
    last = (len(rings) - 1) * stride
    for j in range(n - 1):
        faces.append((0, 1 + j, 2 + j))
        faces.append((last, last + 2 + j, last + 1 + j))

    # Bead rings: one closed shell each, proud of the faces and
    # returned into them, sitting over the shaft the loft ran through.
    for z0, z1, kind in bands:
        if kind != _ASTRAGAL:
            continue
        rv, rf = _ring_shell(style, size, z0, z1, len(verts))
        verts.extend(rv)
        faces.extend(rf)

    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# ----------------------------------------------------------------------
# Placement
# ----------------------------------------------------------------------
def corner_placement(corner, width, depth, size):
    """(x, y, rotation_z) putting the post's section origin on the
    notch's inner corner with u / v pointing at the two cabinet faces.

    The section is symmetric about its diagonal, so which face u takes
    is free -- picking the one that keeps the frame right-handed makes
    all four corners pure rotations of one mesh.
    """
    if corner == 'FRONT_LEFT':
        return size, -depth + size, math.pi
    if corner == 'FRONT_RIGHT':
        return width - size, -depth + size, -math.pi / 2.0
    if corner == 'BACK_LEFT':
        return size, -size, math.pi / 2.0
    return width - size, -size, 0.0


def corner_notch_box(corner, width, depth, size, z0, z1, margin):
    """(x0, x1, y0, y1, z0, z1) of the notch cutter. The box is the
    notch square pushed past the two cabinet faces it opens onto so the
    boolean never grazes a coplanar face."""
    if corner in ('FRONT_LEFT', 'BACK_LEFT'):
        x0, x1 = -margin, size
    else:
        x0, x1 = width - size, width + margin
    if corner in ('FRONT_LEFT', 'FRONT_RIGHT'):
        y0, y1 = -depth - margin, -depth + size
    else:
        y0, y1 = -size, margin
    return x0, x1, y0, y1, z0, z1


# ----------------------------------------------------------------------
# Objects
# ----------------------------------------------------------------------
def _link_beside(cabinet_obj, obj):
    for coll in cabinet_obj.users_collection:
        coll.objects.link(obj)
        return


def _find_child(cabinet_obj, role, corner):
    for child in cabinet_obj.children:
        if (child.get('hb_part_role') == role
                and child.get('hb_corner') == corner):
            return child
    return None


def ensure_post(cabinet_obj, corner, label):
    """Find or lazily create one corner's post object. A plain mesh,
    deliberately NOT tagged CABINET_PART: it is milled stock, not a
    sheet-stock cutpart, so part-collection passes (reports, machining)
    must not pick it up as one. The material walk finds it by role."""
    obj = _find_child(cabinet_obj, PART_ROLE, corner)
    if obj is not None:
        return obj
    name = 'Decorative Corner %s' % label
    obj = hb_utils.new_object(name, bpy.data.meshes.new(name))
    obj['hb_part_role'] = PART_ROLE
    obj['hb_corner'] = corner
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_cabinet_commands'
    obj.parent = cabinet_obj
    _link_beside(cabinet_obj, obj)
    return obj


def ensure_cutter(cabinet_obj, corner, label):
    """Find or lazily create one corner's notch cutter. Hidden in the
    viewport; a boolean still reads its mesh regardless."""
    obj = _find_child(cabinet_obj, PART_ROLE_CUTTER, corner)
    if obj is not None:
        return obj
    name = 'Decorative Corner Cutter %s' % label
    obj = hb_utils.new_object(name, bpy.data.meshes.new(name))
    obj['hb_part_role'] = PART_ROLE_CUTTER
    obj['hb_corner'] = corner
    obj.parent = cabinet_obj
    obj.display_type = 'WIRE'
    obj.hide_render = True
    obj.hide_viewport = True
    _link_beside(cabinet_obj, obj)
    return obj


def _rebuild_box(obj, x0, x1, y0, y1, z0, z1):
    verts = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    mesh = obj.data
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)


def _cut_mod_name(corner):
    return '%s %s' % (CUT_MOD_NAME, corner.title().replace('_', ' '))


def _iter_cut_targets(cabinet_obj):
    stack = list(cabinet_obj.children)
    while stack:
        obj = stack.pop()
        role = obj.get('hb_part_role')
        if role not in (PART_ROLE, PART_ROLE_CUTTER):
            if role in CUT_PART_ROLES and obj.type == 'MESH':
                yield obj
            stack.extend(obj.children)


def _apply_cuts(cabinet_obj, cutters):
    """Ensure every target carries one boolean per live corner and drop
    the modifiers of corners that have been switched off. Idempotent;
    safe every recalc."""
    live = {_cut_mod_name(c): cutter for c, cutter in cutters.items()}
    for part in _iter_cut_targets(cabinet_obj):
        for corner, _label in CORNERS:
            name = _cut_mod_name(corner)
            cutter = live.get(name)
            mod = part.modifiers.get(name)
            if cutter is None:
                if mod is not None:
                    part.modifiers.remove(mod)
                continue
            if mod is None:
                mod = part.modifiers.new(name=name, type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
            if mod.object is not cutter:
                mod.object = cutter


# ----------------------------------------------------------------------
# Shelves around a clipped corner's pocket
# ----------------------------------------------------------------------
# A clipped corner sits in a pocket blocked out with 3/4" stock behind
# the notch, so the shelves are notched around the pocket and its
# blocking rather than running through the corner.
POCKET_BLOCKING = inch(0.75)
SHELF_NOTCH_ROLES = frozenset({'ADJUSTABLE_SHELF', 'INTERIOR_FIXED_SHELF'})
SHELF_NOTCH_MOD_PREFIX = 'Corner Pocket '
# Overlaps thinner than this are float noise, not a notch.
_NOTCH_EPS = inch(1.0 / 64.0)


def _shelf_notch_mod_name(corner):
    return SHELF_NOTCH_MOD_PREFIX + corner.replace('_', ' ').title()


def pocket_rect(corner, width, depth, size):
    """(x0, x1, y0, y1) in cabinet space that a clipped corner's pocket
    and its blocking take out of the cabinet interior."""
    reach = size + POCKET_BLOCKING
    if corner in ('FRONT_LEFT', 'BACK_LEFT'):
        x0, x1 = -1.0, reach
    else:
        x0, x1 = width - reach, width + 1.0
    if corner in ('FRONT_LEFT', 'FRONT_RIGHT'):
        y0, y1 = -depth - 1.0, -depth + reach
    else:
        y0, y1 = -reach, 1.0
    return x0, x1, y0, y1


def _local_to_cabinet(obj, cabinet_obj):
    """obj's matrix in cabinet space from the parent chain's stored
    transforms, so it is right mid-recalc before the depsgraph runs."""
    m = obj.matrix_parent_inverse @ obj.matrix_basis
    p = obj.parent
    while p is not None and p is not cabinet_obj:
        m = p.matrix_parent_inverse @ p.matrix_basis @ m
        p = p.parent
    return m if p is cabinet_obj else None


def _iter_notch_shelves(cabinet_obj):
    stack = list(cabinet_obj.children)
    while stack:
        obj = stack.pop()
        if obj.get('IS_FACE_FRAME_CABINET_CAGE') and obj is not cabinet_obj:
            # A nested cabinet notches its own shelves.
            continue
        if obj.get('hb_part_role') in SHELF_NOTCH_ROLES and obj.type == 'MESH':
            yield obj
        stack.extend(obj.children)


def _shelf_corner_notches(shelf, cabinet_obj, rects):
    """{corner: (flip_x, flip_y, x, y)} for each pocket that takes a
    corner out of this shelf, in the shelf's own Length / Width axes."""
    from ...hb_types import GeoNodeObject
    part = GeoNodeObject(shelf)
    try:
        length = part.get_input('Length')
        w = part.get_input('Width')
        mirror_y = bool(part.get_input('Mirror Y'))
    except Exception:
        return {}
    m = _local_to_cabinet(shelf, cabinet_obj)
    if m is None or length <= 0.0 or w <= 0.0:
        return {}
    y_far = -w if mirror_y else w
    out = {}
    for corner, (rx0, rx1, ry0, ry1) in rects.items():
        # The pocket back in shelf space. Shelves only ever sit square to
        # the cabinet, so the rectangle maps to a rectangle.
        inv = m.inverted()
        from mathutils import Vector
        pts = [inv @ Vector((x, y, 0.0)) for x in (rx0, rx1)
               for y in (ry0, ry1)]
        lx0 = max(0.0, min(p.x for p in pts))
        lx1 = min(length, max(p.x for p in pts))
        ly_lo, ly_hi = sorted((0.0, y_far))
        ly0 = max(ly_lo, min(p.y for p in pts))
        ly1 = min(ly_hi, max(p.y for p in pts))
        nx = lx1 - lx0
        ny = ly1 - ly0
        if nx <= _NOTCH_EPS or ny <= _NOTCH_EPS:
            continue
        # Only a pocket over a shelf corner is a corner notch; one that
        # spans the whole shelf would leave nothing to build.
        at_x0 = lx0 <= _NOTCH_EPS
        at_x1 = lx1 >= length - _NOTCH_EPS
        at_y0 = abs(ly0 - min(0.0, y_far)) <= _NOTCH_EPS
        at_y1 = abs(ly1 - max(0.0, y_far)) <= _NOTCH_EPS
        if at_x0 == at_x1 or at_y0 == at_y1:
            continue
        # The notch node's own corner is the part origin (x = 0, y = 0);
        # Flip Y moves it to the far Width edge.
        origin_end_y0 = (min(0.0, y_far) == 0.0)
        flip_y = at_y1 if origin_end_y0 else at_y0
        out[corner] = (at_x1, flip_y, nx, ny)
    return out


def notch_shelves(cabinet_obj, width, depth, size, corners):
    """Keep one corner notch per clipped-corner pocket on every shelf
    the pocket reaches; drop the notches of corners that are gone.
    Called after the interiors are rebuilt; idempotent."""
    rects = {c: pocket_rect(c, width, depth, size) for c in corners}
    for shelf in _iter_notch_shelves(cabinet_obj):
        notches = _shelf_corner_notches(shelf, cabinet_obj, rects) if rects else {}
        for corner, _label in CORNERS:
            name = _shelf_notch_mod_name(corner)
            mod = shelf.modifiers.get(name)
            spec = notches.get(corner)
            if spec is None:
                if mod is not None:
                    shelf.modifiers.remove(mod)
                continue
            flip_x, flip_y, nx, ny = spec
            from ...hb_types import GeoNodeCutpart
            if mod is None:
                cpm = GeoNodeCutpart(shelf).add_part_modifier(
                    'CPM_CORNERNOTCH', name)
                mod = cpm.mod
            ng = mod.node_group
            if ng is None:
                continue
            thickness = 0.0
            try:
                from ...hb_types import GeoNodeObject
                thickness = GeoNodeObject(shelf).get_input('Thickness')
            except Exception:
                thickness = inch(0.75)
            for input_name, value in (('X', nx), ('Y', ny),
                                      ('Route Depth', thickness),
                                      ('Flip X', flip_x),
                                      ('Flip Y', flip_y)):
                node_input = ng.interface.items_tree.get(input_name)
                if node_input is not None:
                    hb_utils.set_gn_input(mod, node_input.identifier, value)
        if notches:
            shelf['CORNER_POCKET_NOTCH'] = ','.join(sorted(notches))
        elif 'CORNER_POCKET_NOTCH' in shelf:
            del shelf['CORNER_POCKET_NOTCH']


def cleanup(cabinet_obj, keep_corners=()):
    """Remove posts, cutters and boolean modifiers for every corner not
    in keep_corners. Called with no keep set this reverses the feature."""
    keep = set(keep_corners)
    for child in list(cabinet_obj.children):
        role = child.get('hb_part_role')
        if role not in (PART_ROLE, PART_ROLE_CUTTER):
            continue
        if child.get('hb_corner') in keep:
            continue
        mesh = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def post_size(cab_props, width, depth):
    """Face size the posts on this cabinet are built at: the standard
    2" (the size prop, kept for older files), but never more than half
    the cabinet in either direction or two posts on one face would
    collide. The solver reads this too, to pull the face frame in by
    the same amount the post takes."""
    size = max(inch(0.25),
               getattr(cab_props, 'decorative_corner_size', DEFAULT_SIZE))
    return min(size, width / 2.0, depth / 2.0)


def stile_width(cabinet_obj):
    """Width of an end stile that butts into a post: 1-1/2", or 1-1/4"
    when the cabinet's style is full overlay."""
    from . import types_face_frame
    if types_face_frame._resolve_style_overlay(cabinet_obj) == 'FULL':
        return STILE_WIDTH_FULL_OVERLAY
    return STILE_WIDTH


def spec_from_props(cab_props, has_toe_kick):
    """Read the cabinet's decorative-corner props into a plain dict.
    getattr defaults keep this safe against older files."""
    style = getattr(cab_props, 'decorative_corner_style', 'NONE')
    corners = [key for key, _label in CORNERS
               if getattr(cab_props,
                          'decorative_corner_%s' % key.lower(), False)]
    kick = (getattr(cab_props, 'toe_kick_height', 0.0)
            if has_toe_kick else 0.0)
    return {
        'style': style,
        'corners': corners,
        'bottom': getattr(cab_props, 'decorative_corner_bottom', 'STANDARD'),
        'size': max(inch(0.25),
                    getattr(cab_props, 'decorative_corner_size',
                            DEFAULT_SIZE)),
        'block_run': max(0.0,
                         getattr(cab_props, 'decorative_corner_block_run',
                                 DEFAULT_BLOCK_RUN)),
        'detail_height': max(0.0,
                             getattr(cab_props,
                                     'decorative_corner_detail_height',
                                     DEFAULT_DETAIL_HEIGHT)),
        'top_detail': getattr(cab_props, 'decorative_corner_top_detail',
                              True),
        'ball_cuts': getattr(cab_props, 'decorative_corner_ball_cuts',
                             DEFAULT_BALL_CUTS),
        'route_stop': max(0.0, getattr(cab_props,
                                       'decorative_corner_route_stop',
                                       DEFAULT_ROUTE_STOP)),
        'center_top': max(0.0, getattr(cab_props,
                                       'decorative_corner_center_cut_top',
                                       DEFAULT_CENTER_CUT_TOP)),
        'kick_height': kick,
    }


def apply_corners(cabinet_obj, width, depth, height, spec):
    """Build / position / remove the cabinet's decorative corners.

    Managed like the pipe chase: ensure, position, cut, clean up -- safe
    to call every recalc. A no-op (with cleanup) when the style is NONE
    or no corner is switched on.
    """
    style = spec.get('style', 'NONE')
    corners = list(spec.get('corners') or ())
    # A post may not eat more than half the cabinet in either direction,
    # or two corners on the same face would collide.
    size = min(spec.get('size', DEFAULT_SIZE), width / 2.0, depth / 2.0)
    bands = None
    if is_clipped(style) and corners and size > 0.0:
        bands = clipped_band_stack(
            height, spec.get('kick_height', 0.0),
            spec.get('bottom', 'STANDARD'), style,
            spec.get('route_stop', DEFAULT_ROUTE_STOP),
            center_top=spec.get('center_top', 0.0), size=size,
            ball_cuts=spec.get('ball_cuts', DEFAULT_BALL_CUTS))
    elif style != 'NONE' and corners and size > 0.0:
        bands = band_stack(height, spec.get('kick_height', 0.0),
                           spec.get('bottom', 'STANDARD'),
                           spec.get('top_detail', True),
                           spec.get('block_run', DEFAULT_BLOCK_RUN),
                           spec.get('detail_height', DEFAULT_DETAIL_HEIGHT))
    if bands is None:
        cleanup(cabinet_obj)
        _apply_cuts(cabinet_obj, {})
        notch_shelves(cabinet_obj, width, depth, 0.0, ())
        for key in ('DECORATIVE_CORNER_STYLE', 'DECORATIVE_CORNERS',
                    'DECORATIVE_CORNER_SIZE'):
            if key in cabinet_obj:
                del cabinet_obj[key]
        return

    cleanup(cabinet_obj, keep_corners=corners)
    z0 = bands[0][0]
    z1 = bands[-1][1]
    margin = inch(0.5)
    # Start the cut a hair below the post so the boolean never has to
    # resolve a face coplanar with the carcass bottom.
    cut_z0 = z0 - margin if z0 <= 0.0 else z0 - inch(0.01)
    labels = dict(CORNERS)
    cutters = {}
    for corner in corners:
        label = labels.get(corner, corner.title())
        post = ensure_post(cabinet_obj, corner, label)
        build_post_mesh(post.data, style, size, bands,
                        spec.get('ball_cuts', DEFAULT_BALL_CUTS))
        x, y, rot = corner_placement(corner, width, depth, size)
        post.location = (x, y, 0.0)
        post.rotation_euler = (0.0, 0.0, rot)
        post.hide_viewport = False
        post.hide_render = False

        cutter = ensure_cutter(cabinet_obj, corner, label)
        _rebuild_box(cutter, *corner_notch_box(
            corner, width, depth, size, cut_z0, height + margin, margin))
        cutters[corner] = cutter

    _apply_cuts(cabinet_obj, cutters)
    # Shelves give way to a clipped corner's pocket. Turned posts keep
    # their current shelves.
    notch_shelves(cabinet_obj, width, depth, size,
                  corners if is_clipped(style) else ())
    # Publish the applied spec on the root so downstream consumers
    # (drawings, reports) can read it without recomputing. Cleared above
    # when the corners are removed.
    cabinet_obj['DECORATIVE_CORNER_STYLE'] = style
    cabinet_obj['DECORATIVE_CORNERS'] = ','.join(corners)
    # Size as built (after the half-cabinet cap), in metres.
    cabinet_obj['DECORATIVE_CORNER_SIZE'] = size
