"""Cabinet columns applied over face frame stiles.

A cabinet column is a split (half) turning applied to the FACE of the
frame over a stile: it stands proud of the face frame, so unlike a
decorative corner post nothing is notched or cut. On an end stile the
column sits flush with the cabinet's end (block face in line with the
outer edge of the frame), the rest of the stile showing as a reveal
beside it - which is why a stile carrying a column is widened (4" by
default, see STILE_WIDTH). Between bays it is centered on the mid
stile. Anatomy, top to bottom:

    end block   -- plain square block, turned dome on its inner end;
                   adjustable height, by default 1" taller than the
                   TOP rail (top and bottom blocks alike)
    spool       -- the turned transition (bead, taper, cap)
    shaft       -- the styled run between the spools: smooth or reeded
    spool       -- mirrored
    end block   -- mirrored
    floor block -- optional plain plinth at the floor (the catalog's
                   Bottom Block), for flush kicks or a stile extended
                   to the floor past a recessed kick

Every component is a surface of revolution about a vertical axis lying
ON the face frame's outer plane, sliced at that plane: the flat back
sits against the frame and the half-turning bulges outward. In
component-local space the axis is +Z, the back is the XZ plane, and
the bulge points -Y; the cabinet-level pass places each component at
its world axis point and rotates it to the (possibly angled) FF plane.

Split turnings lose half a saw kerf off the blank's radius, so a
component reads slightly shallower than wide; the vendor spec gives
the finished proud depths directly and the builder squashes Y by
proud / radius to match them.

Blocks and spools are separate purchasable parts (the catalog sells
spools without end blocks), so each component is its own object.
"""

import math

import bpy
import bmesh

from ...units import inch


# Blade kerf lost when the turned blank is split into two halves.
KERF = inch(0.094)

# Shortest styled shaft worth building. Below this the spools drop and
# the shaft runs plain between the blocks; below it again, no column.
MIN_SHAFT_RUN = inch(1.0)

# Extra length an end block runs past the top rail width.
BLOCK_PAST_RAIL = inch(1.0)

# Width a stile is opened up to when it takes a column: the large
# block (3-1/4") plus a reveal beside it.
STILE_WIDTH = inch(4.0)

# Fallback plinth height on a flush kick, where the frame bottom is
# the floor and there is no kick recess to fill.
DEFAULT_FLOOR_BLOCK = inch(4.0)

PART_ROLE = 'CABINET_COLUMN'

COMPONENTS = ('TOP_BLOCK', 'TOP_SPOOL', 'SHAFT',
              'BOTTOM_SPOOL', 'BOTTOM_BLOCK', 'FLOOR_BLOCK')

STYLE_ITEMS = [
    ('SMOOTH', "Smooth", "Plain half-round shaft"),
    ('REEDED', "Reeded", "Reeded shaft - half-round beads separated "
                         "by flat lands"),
]

SIZE_ITEMS = [
    ('SMALL', "Small", "2\" blocks, 1\" shaft"),
    ('LARGE', "Large", "3-1/4\" blocks, 1-1/2\" shaft"),
]

# Vendor spec, measured off the manufacturer drawings. block_proud /
# spool_proud are the post-split depths (radius less half a kerf).
SIZE_SPECS = {
    'SMALL': {
        'block_width': inch(2.063),
        'block_proud': inch(0.984),
        'dome_diameter': inch(1.813),
        'collar_diameter': inch(1.563),
        'dome_run': inch(0.625),
        'spool_diameter': inch(2.063),
        'spool_proud': inch(0.984),
        'spool_height': inch(2.719),
        'shaft_diameter': inch(1.0),
    },
    'LARGE': {
        'block_width': inch(3.25),
        'block_proud': inch(1.578),
        'dome_diameter': inch(2.831),
        'collar_diameter': inch(2.373),
        'dome_run': inch(1.0),
        'spool_diameter': inch(3.063),
        'spool_proud': inch(1.484),
        'spool_height': inch(4.063),
        'shaft_diameter': inch(1.5),
    },
}

# Spool outline, bottom face to top cap, measured off the large-spool
# drawing and normalized: (z / spool_height, r / max radius). The small
# spool is the same design scaled, so both sizes share the table.
# Wide bead at the bottom, neck, long gentle taper, fillet, cap.
SPOOL_PROFILE = (
    (0.000, 0.816),   # bottom face
    (0.020, 0.874),
    (0.045, 0.930),
    (0.070, 0.975),
    (0.081, 1.000),   # bead apex
    (0.140, 0.995),
    (0.166, 0.960),   # bead shoulder, neck begins
    (0.185, 0.850),
    (0.200, 0.762),
    (0.215, 0.714),   # neck lands on the taper
    (0.520, 0.640),   # taper, essentially straight
    (0.836, 0.571),   # taper top
    (0.859, 0.571),   # fillet under the cap
    (0.872, 0.610),
    (0.890, 0.665),
    (0.910, 0.694),   # cap apex
    (0.965, 0.694),
    (0.985, 0.660),
    (1.000, 0.571),   # top face
)

# Reeding across the exposed half-circumference.
REED_COUNT = 7
REED_LAND_RATIO = 0.383
REED_DEPTH_RATIO = 0.125    # of the shaft radius


def block_height_default(rail_width):
    """Standard default: an end block runs BLOCK_PAST_RAIL longer than
    the top rail (the caller passes the top rail width for both blocks;
    on a flush kick the bottom block's includes the kick it drops
    over)."""
    return max(inch(0.5), rail_width + BLOCK_PAST_RAIL)


def end_axis_offset(size):
    """FF-x from the frame's end to a column axis that puts the block
    flush with that end: half the block width."""
    spec = SIZE_SPECS.get(size, SIZE_SPECS['LARGE'])
    return spec['block_width'] / 2.0


# ----------------------------------------------------------------------
# Section radius functions (theta 0..180, 0 and 180 on the back plane)
# ----------------------------------------------------------------------
def _rect_radius(half_width, proud, deg):
    """Boundary distance of the block's half-rectangle section from the
    axis: |x| <= half_width, -proud <= y <= 0."""
    rad = math.radians(deg)
    c = abs(math.cos(rad))
    s = math.sin(rad)
    r_side = half_width / c if c > 1e-9 else float('inf')
    r_face = proud / s if s > 1e-9 else float('inf')
    return min(r_side, r_face)


def _reed_spans():
    """(start, end) of each reed in degrees across the half round, with
    equal lands between reeds and at both back edges."""
    width = 180.0 / (REED_COUNT + REED_LAND_RATIO * (REED_COUNT + 1))
    land = width * REED_LAND_RATIO
    return [(land + k * (width + land), land + k * (width + land) + width)
            for k in range(REED_COUNT)]


def _shaft_radius(style, radius, deg):
    if style == 'REEDED':
        depth = radius * REED_DEPTH_RATIO
        land = radius - depth
        for start, end in _reed_spans():
            if start <= deg <= end:
                u = 2.0 * (deg - start) / (end - start) - 1.0
                return land + depth * math.sqrt(max(0.0, 1.0 - u * u))
        return land
    return radius


def _shaft_degs(style):
    if style == 'REEDED':
        degs = {0.0, 90.0, 180.0}
        for start, end in _reed_spans():
            degs.add(start)
            degs.add(end)
            for i in range(1, 12):
                degs.add(start + (end - start) * i / 12.0)
        return sorted(degs)
    return [i * 6.0 for i in range(31)]


def _round_degs():
    return [i * 6.0 for i in range(31)]


def _block_degs(half_width, proud):
    """Rectangle corner angles plus a round sweep, so both the square
    body and the dome band sample cleanly on one angle set."""
    corner = math.degrees(math.atan2(proud, half_width))
    degs = {0.0, corner, 90.0, 180.0 - corner, 180.0}
    for i in range(31):
        degs.add(i * 6.0)
    return sorted(degs)


# ----------------------------------------------------------------------
# Mesh builder
# ----------------------------------------------------------------------
def _build_half_mesh(mesh, rings, degs, y_scale=1.0):
    """Regenerate mesh as a lofted half-turning.

    rings: [(z, [radius per deg])] bottom to top. Every ring is one
    axis vertex plus the boundary samples; the flat back closes through
    the axis vertices and the ends close as fans, so the shell is a
    closed manifold. Consecutive coincident rings are dropped (a loft
    between identical rings emits zero-area faces that validate()
    strips, tearing the shell open).
    """
    dirs = [(math.cos(math.radians(d)), -math.sin(math.radians(d)))
            for d in degs]
    n = len(degs)

    cleaned = []
    for z, radii in rings:
        if cleaned and abs(cleaned[-1][0] - z) < 1e-9:
            if all(abs(a - b) < 1e-9
                   for a, b in zip(cleaned[-1][1], radii)):
                continue
        cleaned.append((z, radii))

    verts = []
    for z, radii in cleaned:
        verts.append((0.0, 0.0, z))
        for r, (cx, cy) in zip(radii, dirs):
            verts.append((r * cx, r * cy * y_scale, z))

    stride = n + 1
    faces = []
    for i in range(len(cleaned) - 1):
        a = i * stride
        b = (i + 1) * stride
        for j in range(n - 1):
            faces.append((a + 1 + j, a + 2 + j, b + 2 + j, b + 1 + j))
        # Flat back: two quads per band through the axis vertices.
        faces.append((a, a + 1, b + 1, b))
        faces.append((a, b, b + n, a + n))
    last = (len(cleaned) - 1) * stride
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


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def build_block_mesh(mesh, spec, height, dome_end):
    """End block: square body with a turned dome transition on the end
    facing the spool. dome_end is 'TOP' (bottom block) or 'BOTTOM'
    (top block); None builds the plain floor plinth."""
    a = spec['block_width'] / 2.0
    b = spec['block_proud']
    degs = _block_degs(a, b)
    rect = [_rect_radius(a, b, d) for d in degs]

    if dome_end is None or height <= spec['dome_run'] * 1.5:
        rings = [(0.0, rect), (height, rect)]
        _build_half_mesh(mesh, rings, degs)
        return

    r_dome = spec['dome_diameter'] / 2.0
    r_collar = spec['collar_diameter'] / 2.0
    dome_run = spec['dome_run']

    # Band positions measured from the domed end inward.
    def band(offset_from_end):
        if dome_end == 'TOP':
            return height - offset_from_end
        return offset_from_end

    rings = [(band(height), rect), (band(dome_run), rect)]
    # Square -> dome-base circle over the outer 55% of the run, then
    # the dome curve down to the collar at the end face.
    blend_steps = 6
    for i in range(1, blend_steps + 1):
        t = i / float(blend_steps)
        s = _smoothstep(t)
        z = band(dome_run - dome_run * 0.55 * t)
        rings.append((z, [rd + (r_dome - rd) * s if rd > r_dome else rd
                          for rd in rect]))
    dome_steps = 6
    for i in range(1, dome_steps + 1):
        t = i / float(dome_steps)
        # Quarter-round ease: full dome radius easing onto the collar.
        r = r_collar + (r_dome - r_collar) * math.cos(t * math.pi / 2.0)
        z = band(dome_run * 0.45 * (1.0 - t))
        rings.append((z, [r] * len(degs)))
    rings.sort(key=lambda ring: ring[0])
    _build_half_mesh(mesh, rings, degs)


def build_spool_mesh(mesh, spec, flip):
    """Turned spool. The profile runs wide bead -> taper -> cap; the
    bottom spool sits bead-down (as drawn), the top spool is flipped
    so its bead meets the top block."""
    radius = spec['spool_diameter'] / 2.0
    height = spec['spool_height']
    degs = _round_degs()
    n = len(degs)
    rings = []
    for t, rr in SPOOL_PROFILE:
        z = (1.0 - t) * height if flip else t * height
        rings.append((z, [rr * radius] * n))
    rings.sort(key=lambda ring: ring[0])
    _build_half_mesh(mesh, rings, degs,
                     y_scale=spec['spool_proud'] / radius)


def build_shaft_mesh(mesh, spec, style, length):
    radius = spec['shaft_diameter'] / 2.0
    degs = _shaft_degs(style)
    radii = [_shaft_radius(style, radius, d) for d in degs]
    rings = [(0.0, radii), (length, radii)]
    _build_half_mesh(mesh, rings, degs,
                     y_scale=(radius - KERF / 2.0) / radius)


# ----------------------------------------------------------------------
# Objects
# ----------------------------------------------------------------------
def _link_beside(cabinet_obj, obj):
    for coll in cabinet_obj.users_collection:
        coll.objects.link(obj)
        return


def _column_children(cabinet_obj):
    for child in cabinet_obj.children:
        if child.get('hb_part_role') == PART_ROLE:
            yield child


def _find_part(cabinet_obj, key, component):
    for child in _column_children(cabinet_obj):
        if (child.get('hb_column_key') == key
                and child.get('hb_column_part') == component):
            return child
    return None


def ensure_part(cabinet_obj, key, component, label):
    """Find or lazily create one column component. A plain mesh,
    deliberately NOT tagged CABINET_PART: it is a purchased turning,
    not a sheet-stock cutpart. The material walk finds it by role."""
    obj = _find_part(cabinet_obj, key, component)
    if obj is not None:
        return obj
    name = 'Cabinet Column %s %s' % (label,
                                     component.title().replace('_', ' '))
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    obj['hb_part_role'] = PART_ROLE
    obj['hb_column_key'] = key
    obj['hb_column_part'] = component
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
    obj.parent = cabinet_obj
    _link_beside(cabinet_obj, obj)
    return obj


def cleanup(cabinet_obj, keep=()):
    """Remove column components not in keep, a set of
    (key, component). Called with no keep set this reverses the
    feature for the whole cabinet."""
    keep = set(keep)
    for child in list(_column_children(cabinet_obj)):
        tag = (child.get('hb_column_key'), child.get('hb_column_part'))
        if tag in keep:
            continue
        mesh = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def _component_stack(placement, spec):
    """[(component, z, build args...)] for one column, or None when the
    frame span can't hold even a plain shaft. Heights of 0 mean 'use
    the standard default' (top rail + 1", both blocks)."""
    zb = placement['z_bottom']
    zt = placement['z_top']
    if zt - zb < MIN_SHAFT_RUN:
        return None

    tb_h = placement.get('top_block_height') or block_height_default(
        placement.get('top_rail_width', 0.0))
    bb_h = placement.get('bottom_block_height') or block_height_default(
        placement.get('bottom_rail_width', 0.0))

    stack = []
    base_z = zb
    if placement.get('floor_block'):
        fb_h = placement.get('floor_block_height') or (
            zb if zb > inch(0.5) else DEFAULT_FLOOR_BLOCK)
        stack.append(('FLOOR_BLOCK', 0.0, fb_h))
        base_z = max(zb, fb_h)

    top_start = zt
    if placement.get('top_block', True):
        tb_h = min(tb_h, (zt - base_z) / 2.0)
        stack.append(('TOP_BLOCK', zt - tb_h, tb_h))
        top_start = zt - tb_h
    bottom_start = base_z
    if placement.get('bottom_block', True):
        bb_h = min(bb_h, (top_start - base_z) / 2.0)
        stack.append(('BOTTOM_BLOCK', base_z, bb_h))
        bottom_start = base_z + bb_h

    spool_h = spec['spool_height']
    shaft_z0 = bottom_start + spool_h
    shaft_z1 = top_start - spool_h
    if shaft_z1 - shaft_z0 >= MIN_SHAFT_RUN:
        stack.append(('BOTTOM_SPOOL', bottom_start, None))
        stack.append(('TOP_SPOOL', shaft_z1, None))
        stack.append(('SHAFT', shaft_z0, shaft_z1 - shaft_z0))
    elif top_start - bottom_start >= MIN_SHAFT_RUN:
        # Not enough room for the turned transitions: plain shaft
        # straight between the blocks.
        stack.append(('SHAFT', bottom_start, top_start - bottom_start))
    elif not stack:
        return None
    return stack


def apply_columns(cabinet_obj, placements):
    """Build / position / remove the cabinet's columns. Managed like
    the decorative corners: ensure, position, clean up -- safe to call
    every recalc. placements is a list of dicts:

        key, label            stile identity ('LEFT' / 'RIGHT' / 'MID_n')
        x, y, theta           axis point on the FF outer plane + plane angle
        z_bottom, z_top       frame extent the column spans
        style, size           SMOOTH / REEDED, SMALL / LARGE
        top_block, bottom_block, floor_block        booleans
        top_block_height, bottom_block_height,
        floor_block_height    0 = catalog default
        top_rail_width, bottom_rail_width           for the defaults:
                              both are the TOP rail width; the bottom
                              one adds the kick on a flush kick
    """
    keep = set()
    published = []
    for placement in placements:
        spec = SIZE_SPECS.get(placement.get('size', 'LARGE'),
                              SIZE_SPECS['LARGE'])
        stack = _component_stack(placement, spec)
        if not stack:
            continue
        key = placement['key']
        label = placement.get('label', key.title())
        style = placement.get('style', 'SMOOTH')
        for component, z, arg in stack:
            obj = ensure_part(cabinet_obj, key, component, label)
            if component in ('TOP_BLOCK', 'BOTTOM_BLOCK', 'FLOOR_BLOCK'):
                dome_end = {'TOP_BLOCK': 'BOTTOM',
                            'BOTTOM_BLOCK': 'TOP',
                            'FLOOR_BLOCK': None}[component]
                build_block_mesh(obj.data, spec, arg, dome_end)
            elif component == 'SHAFT':
                build_shaft_mesh(obj.data, spec, style, arg)
            else:
                build_spool_mesh(obj.data, spec,
                                 flip=(component == 'TOP_SPOOL'))
            obj.location = (placement['x'], placement['y'], z)
            obj.rotation_euler = (0.0, 0.0, placement.get('theta', 0.0))
            keep.add((key, component))
        published.append('%s:%s:%s' % (key, style,
                                       placement.get('size', 'LARGE')))

    cleanup(cabinet_obj, keep=keep)
    # Publish the applied spec on the root so downstream consumers
    # (drawings, reports) can read it without recomputing.
    if published:
        cabinet_obj['CABINET_COLUMNS'] = ','.join(published)
    elif 'CABINET_COLUMNS' in cabinet_obj:
        del cabinet_obj['CABINET_COLUMNS']
