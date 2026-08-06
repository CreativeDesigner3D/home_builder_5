"""Decorative corner posts on a cabinet's vertical corners.

A decorative corner is a turned / milled post let into a vertical
corner of the cabinet: the corner is notched square, the post fills the
notch, and its outer face carries a profile. Islands and exposed run
ends are the usual hosts, so the post is offered per corner (front
left / right, back left / right).

Anatomy, bottom to top (the catalog calls the plain square sections
"square blocks" and each bead ring a "transition detail"):

    square block  -- fills the notch flush with both cabinet faces,
                     so it reads proud of the profiled shaft
    astragal      -- half-round bead ring standing proud of both faces
    shaft         -- the styled run: 2" radius / colonial / fluted
    astragal
    square block  -- the block crown moulding dies into

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
"""

import math

import bpy
import bmesh

from ...units import inch


# Nominal post face size. The catalog corners are 2" x 2".
DEFAULT_SIZE = inch(2.0)
# Bead ring height and how far it stands proud of the cabinet faces.
ASTRAGAL_HEIGHT = inch(0.75)
ASTRAGAL_PROJECTION = inch(0.25)
# Plain square-block run between a transition detail and the post end.
DEFAULT_BLOCK_RUN = inch(3.0)
# Depth the reeds are cut below the shaft's outer radius.
REED_DEPTH = inch(0.1875)
REED_COUNT = 5
# Land (flat) between reeds, as a fraction of one reed's width. Five
# reeds and six lands at this ratio put the reed pitch at about 1/2"
# on a 2" post, which is the catalog's fluting.
REED_LAND_RATIO = 0.383

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
]

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

# Parts the corner notch cuts through. An explicit allow-list, like the
# pipe chase's: the notch box overshoots the cabinet faces so the
# boolean never grazes a coplanar face, and that overshoot reaches into
# the door plane -- fronts must stay out of it.
CUT_PART_ROLES = frozenset({
    # Face frame
    'LEFT_STILE', 'RIGHT_STILE',
    'LEFT_REFRIG_STILE', 'RIGHT_REFRIG_STILE',
    'FULL_OVERLAY_STILE',
    'TOP_RAIL', 'BOTTOM_RAIL',
    # Carcass
    'LEFT_SIDE', 'RIGHT_SIDE', 'TOP', 'BOTTOM',
    'BACK', 'FINISHED_BACK',
    'FRONT_STRETCHER', 'REAR_STRETCHER',
    # Applied end skins and blind ends
    'FLUSH_X', 'BEADBOARD', 'SHIPLAP',
    'BLIND_PANEL_LEFT', 'BLIND_PANEL_RIGHT',
    'LEFT_SIDE_RETURN', 'RIGHT_SIDE_RETURN',
    'LEFT_SIDE_RETURN_STILE', 'RIGHT_SIDE_RETURN_STILE',
    # Finished bottom panel under an upper
    'FINISHED_BOTTOM',
    # Toe kick, for the options that run the post past it to the floor
    'TOE_KICK_SUBFRONT', 'FINISH_TOE_KICK', 'MID_FINISH_KICK',
    'LEFT_CORNER_FINISH_KICK', 'RIGHT_CORNER_FINISH_KICK',
    'LEFT_KICK_RETURN', 'RIGHT_KICK_RETURN',
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


def _sample_degrees(style):
    """Angles the section is sampled at, 0 to 90 inclusive. 45 is always
    present: the square blocks crease there."""
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


def _style_radius(style, size, deg):
    """Shaft radius at one section angle."""
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


def _band_radii(kind, style, size, deg, bulge):
    if kind == _SQUARE:
        return _square_radius(size, deg)
    if kind == _ASTRAGAL:
        return size + ASTRAGAL_PROJECTION * bulge
    return _style_radius(style, size, deg)


# ----------------------------------------------------------------------
# Vertical band stack
# ----------------------------------------------------------------------
def post_bottom_z(bottom_option, kick_height):
    """Cabinet-local Z the post starts at. The two 'to floor' options
    run past a kick; the others sit on the cabinet box bottom."""
    if bottom_option in ('EXTENDED_FLOOR', 'FLUSH_BLOCK'):
        return 0.0
    return max(0.0, kick_height)


def band_stack(height, kick_height, bottom_option, top_detail, block_run):
    """[(z0, z1, kind)] bottom to top, or None when there is no room.

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
        a0 = max(0.0, kick_height) + block_run
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


def _band_rings(bands):
    """[(z, kind, bulge)] rings for the loft. Bands meet at a shared Z
    with different radii, so each boundary emits two rings and the quads
    between them close the step as a horizontal face. The astragal
    subdivides so its bead reads round."""
    rings = []
    for z0, z1, kind in bands:
        if kind == _ASTRAGAL:
            steps = 8
            for i in range(steps + 1):
                t = i / float(steps)
                rings.append((z0 + (z1 - z0) * t,
                              kind, math.sin(math.pi * t)))
        else:
            rings.append((z0, kind, 0.0))
            rings.append((z1, kind, 0.0))
    return rings


# ----------------------------------------------------------------------
# Mesh
# ----------------------------------------------------------------------
def build_post_mesh(mesh, style, size, bands):
    """Regenerate mesh as the lofted post in post-local section space.

    Section space: the notch's inner corner is the origin, the post
    fills the first quadrant, and the cabinet faces are u = size and
    v = size. Every ring is one centre vertex plus the boundary
    samples, so the two flat cut faces fall out of the loft.
    """
    degs = _sample_degrees(style)
    dirs = [(math.cos(math.radians(d)), math.sin(math.radians(d)))
            for d in degs]
    n = len(degs)

    # Resolve each ring's radii, then drop a ring that repeats the one
    # under it: a plain shaft meets its astragal at the same radius, and
    # lofting between two identical rings would emit a band of zero-area
    # faces for mesh.validate() to strip, tearing the shell open.
    rings = []
    for z, kind, bulge in _band_rings(bands):
        radii = [_band_radii(kind, style, size, deg, bulge) for deg in degs]
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
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
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
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
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
        'top_detail': getattr(cab_props, 'decorative_corner_top_detail',
                              True),
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
    size = min(spec['size'], width / 2.0, depth / 2.0)
    bands = None
    if style != 'NONE' and corners and size > 0.0:
        bands = band_stack(height, spec['kick_height'], spec['bottom'],
                           spec['top_detail'], spec['block_run'])
    if bands is None:
        cleanup(cabinet_obj)
        _apply_cuts(cabinet_obj, {})
        for key in ('DECORATIVE_CORNER_STYLE', 'DECORATIVE_CORNERS'):
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
        build_post_mesh(post.data, style, size, bands)
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
    # Publish the applied spec on the root so downstream consumers
    # (drawings, reports) can read it without recomputing. Cleared above
    # when the corners are removed.
    cabinet_obj['DECORATIVE_CORNER_STYLE'] = style
    cabinet_obj['DECORATIVE_CORNERS'] = ','.join(corners)
