"""
Python-built door geometry (no geometry nodes).

First step of moving door construction off the CPM_5PIECEDOOR geometry
node modifier: a door is real parts -- left / right stiles, top / bottom
rails, an optional mid rail, and inset panel(s) -- laid out from a
Face_Frame_Door_Style's construction fields. The wood hood bay doors
build from this now; cabinet fronts can migrate in the wider door
overhaul (outer / inner / panel profiles become sweeps along these same
rects without changing callers).

door_layout returns DATA rather than objects so any consumer can realize
the parts its own way (driven cutparts, static meshes, a future profile
sweep). Every rect dimension is linear in the door's overall width W or
height H, expressed as a (coefficient, offset) pair: value = coef * W +
offset (x / w against W; z / h against H). A static builder just
evaluates the pairs (evaluate_layout, or build_door_mesh for a ready
mesh in cutpart-local space); a driven builder (the wood hood) composes
them into driver expressions so the parts track their cage.
"""

from ...units import inch


# Master switch for the python-built cabinet-front door path: True has
# assign_style_to_front build fronts with build_door_mesh; False
# restores the CPM_5PIECEDOOR modifier path.
USE_PYTHON_DOORS = True


# Construction fields read off a Face_Frame_Door_Style, with the
# fallbacks used when no style resolves (matching the property defaults
# in props_hb_face_frame).
DOOR_STYLE_FALLBACK = {
    'door_type': '5_PIECE',
    'stile_width': inch(3.0),
    'rail_width': inch(3.0),
    'add_mid_rail': False,
    'center_mid_rail': True,
    'mid_rail_width': inch(3.0),
    'mid_rail_location': inch(12.0),
    'panel_thickness': inch(0.5),
    'panel_inset': inch(0.25),
    # Grid dividers (no Face_Frame_Door_Style fields yet -- consumers
    # set these on the info dict): counts of equally spaced mid rails /
    # mid stiles splitting the field into panel cells. mid_rail_count
    # overrides the legacy single add_mid_rail when > 0.
    'mid_rail_count': 0,
    'mid_stile_count': 0,
    # Per-side frame widths, also consumer-set: None falls back to the
    # uniform stile_width / rail_width (mid_stile_width to stile_width).
    # A per-side 0.0 is honored -- it drops that member so adjacent
    # doors can butt.
    'left_stile_width': None,
    'right_stile_width': None,
    'top_rail_width': None,
    'bottom_rail_width': None,
    'mid_stile_width': None,
    # Explicit mid-rail centerline as a (coef, offset) pair against the
    # door height. When set (and mid_rail_count is 0) it forces a single
    # mid rail there, winning over add_mid_rail / center_mid_rail /
    # mid_rail_location.
    'mid_rail_z': None,
}


def _frame_widths(info):
    """Effective member widths (left stile, right stile, mid stile,
    top rail, bottom rail, mid rail). The uniform widths are floored
    at 1/2"; per-side overrides fall back to them when None and are
    only floored at 0.0 so an explicit no-stile side stays empty."""
    sw = max(info['stile_width'], inch(0.5))
    rw = max(info['rail_width'], inch(0.5))
    mrw = max(info['mid_rail_width'], inch(0.5))

    def eff(key, base):
        v = info.get(key)
        return base if v is None else max(v, 0.0)

    return (eff('left_stile_width', sw), eff('right_stile_width', sw),
            eff('mid_stile_width', sw), eff('top_rail_width', rw),
            eff('bottom_rail_width', rw), mrw)


def door_style_info(style=None):
    """Plain-dict snapshot of a door style's construction fields
    (DOOR_STYLE_FALLBACK for None / missing fields), so the layout math
    doesn't hold RNA references."""
    info = dict(DOOR_STYLE_FALLBACK)
    if style is not None:
        for key in info:
            info[key] = getattr(style, key, info[key])
    return info


def layout_min_size(info):
    """(min_width, min_height) below which the 5-piece layout collapses
    (members would overlap); at or under these the caller should build
    the door as a slab instead."""
    if info.get('door_type') == 'SLAB':
        return 0.0, 0.0
    lsw, rsw, msw, trw, brw, mrw = _frame_widths(info)
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    if k == 0 and (info.get('add_mid_rail')
                   or info.get('mid_rail_z') is not None):
        k = 1
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    return lsw + rsw + m * msw + inch(0.5), trw + brw + k * mrw + inch(0.5)


def door_layout(info):
    """Part rects for one door in door-local space: x across from the
    left edge, z up from the bottom edge. Returns a list of dicts:

      key       -- 'slab' / 'left_stile' / 'right_stile' / 'top_rail' /
                   'bottom_rail' / 'mid_rail' / 'mid_stile' / 'panel'
      name      -- display name ("Left Stile", ...)
      x, w      -- (coef, offset) against the door width
      z, h      -- (coef, offset) against the door height
      thickness -- None = the caller's door thickness (frame members /
                   slab); a float for the thinner panel
      y_inset   -- setback of the part's front face from the door's
                   front face (panels; 0 for frame members)

    Mid rails / mid stiles divide the field into a grid of panel
    cells: mid rails run the full field width, mid stiles run between
    the rails segmented per panel row (six-panel-door construction).
    ``mid_rail_count`` (equally spaced) overrides the legacy single
    add_mid_rail when > 0; an explicit ``mid_rail_z`` centerline pair
    wins over add_mid_rail. Per-side frame widths come from the
    left/right stile and top/bottom rail overrides when set (a 0.0
    side emits a zero-width member the realizers skip); mid stiles
    use mid_stile_width, falling back to the outer stile width.
    """
    if info.get('door_type') == 'SLAB':
        return [dict(key='slab', name="Slab", x=(0.0, 0.0), w=(1.0, 0.0),
                     z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
                     y_inset=0.0)]
    lsw, rsw, msw, trw, brw, mrw = _frame_widths(info)
    p_th = max(info['panel_thickness'], inch(0.125))
    p_in = max(info['panel_inset'], 0.0)
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    mid_z = info.get('mid_rail_z')
    parts = [
        dict(key='left_stile', name="Left Stile", x=(0.0, 0.0), w=(0.0, lsw),
             z=(0.0, 0.0), h=(1.0, 0.0), thickness=None, y_inset=0.0),
        dict(key='right_stile', name="Right Stile", x=(1.0, -rsw),
             w=(0.0, rsw), z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
             y_inset=0.0),
        dict(key='bottom_rail', name="Bottom Rail", x=(0.0, lsw),
             w=(1.0, -(lsw + rsw)), z=(0.0, 0.0), h=(0.0, brw),
             thickness=None, y_inset=0.0),
        dict(key='top_rail', name="Top Rail", x=(0.0, lsw),
             w=(1.0, -(lsw + rsw)), z=(1.0, -trw), h=(0.0, trw),
             thickness=None, y_inset=0.0),
    ]
    # Panel rows as (z, h) linear pairs, with the mid rails between them.
    if k > 0:
        fh = (1.0, -(trw + brw + k * mrw))    # field height, linear in H
        rows = [((fh[0] * i / (k + 1), fh[1] * i / (k + 1) + brw + i * mrw),
                 (fh[0] / (k + 1), fh[1] / (k + 1)))
                for i in range(k + 1)]
        for i in range(1, k + 1):
            parts.append(dict(
                key='mid_rail',
                name="Mid Rail %d" % i if k > 1 else "Mid Rail",
                x=(0.0, lsw), w=(1.0, -(lsw + rsw)),
                z=(fh[0] * i / (k + 1),
                   fh[1] * i / (k + 1) + brw + (i - 1) * mrw),
                h=(0.0, mrw), thickness=None, y_inset=0.0))
    elif mid_z is not None or info.get('add_mid_rail'):
        # Single mid rail: the explicit centerline pair when given,
        # else the legacy centered / fixed-location fields. mz is the
        # rail's BOTTOM edge as a (coef, offset) pair.
        if mid_z is not None:
            mz = (mid_z[0], mid_z[1] - mrw / 2.0)
        elif info.get('center_mid_rail', True):
            mz = (0.5, -mrw / 2.0)
        else:
            mz = (0.0, max(info['mid_rail_location'], brw))
        parts.append(dict(key='mid_rail', name="Mid Rail", x=(0.0, lsw),
                          w=(1.0, -(lsw + rsw)), z=mz, h=(0.0, mrw),
                          thickness=None, y_inset=0.0))
        rows = [((0.0, brw), (mz[0], mz[1] - brw)),
                ((mz[0], mz[1] + mrw), (1.0 - mz[0], -trw - mz[1] - mrw))]
    else:
        rows = [((0.0, brw), (1.0, -(trw + brw)))]
    # Panel columns as (x, w) linear pairs; mid stiles between them,
    # one set per row (they butt the rails).
    if m > 0:
        cw = (1.0 / (m + 1), -(lsw + rsw + m * msw) / (m + 1))
        cols = [((c * cw[0], c * (cw[1] + msw) + lsw), cw)
                for c in range(m + 1)]
    else:
        cols = [((0.0, lsw), (1.0, -(lsw + rsw)))]
    grid = len(rows) > 1 or len(cols) > 1
    for r, (rz, rh) in enumerate(rows):
        for j in range(1, m + 1):
            name = ("Mid Stile %d-%d" % (r + 1, j) if len(rows) > 1
                    else ("Mid Stile %d" % j if m > 1 else "Mid Stile"))
            parts.append(dict(key='mid_stile', name=name,
                              x=(j * cw[0], j * (cw[1] + msw) + lsw - msw),
                              w=(0.0, msw), z=rz, h=rh,
                              thickness=None, y_inset=0.0))
        for c, (cx, cwid) in enumerate(cols):
            name = "Panel %d-%d" % (r + 1, c + 1) if grid else "Panel"
            parts.append(dict(key='panel', name=name, x=cx, w=cwid,
                              z=rz, h=rh, thickness=p_th, y_inset=p_in))
    return parts


def evaluate_layout(info, width, height):
    """door_layout realized at a concrete door size: the same part
    dicts with absolute rects alongside the linear pairs -- x0/x1
    across from the left edge, z0/z1 up from the bottom edge
    (door-local, meters)."""
    parts = []
    for part in door_layout(info):
        x0 = part['x'][0] * width + part['x'][1]
        z0 = part['z'][0] * height + part['z'][1]
        parts.append(dict(part,
                          x0=x0, x1=x0 + part['w'][0] * width + part['w'][1],
                          z0=z0, z1=z0 + part['h'][0] * height + part['h'][1]))
    return parts


# Material slot per part key for build_door_mesh, matching the
# (stile, rail, panel) triple it accepts.
_PART_MAT_SLOT = {
    'slab': 0, 'left_stile': 0, 'right_stile': 0, 'mid_stile': 0,
    'top_rail': 1, 'bottom_rail': 1, 'mid_rail': 1, 'panel': 2,
}


def _panel_grid(info, width, height):
    """Opening (panel-cell) rects from the layout, grouped into rows:
    [[(x0, z0, x1, z1), ...], ...] bottom row first, left to right."""
    rows = {}
    for p in evaluate_layout(info, width, height):
        if p['key'] != 'panel':
            continue
        rows.setdefault(round(p['z0'], 6), []).append(
            (p['x0'], p['z0'], p['x1'], p['z1']))
    return [sorted(rows[k]) for k in sorted(rows)]


def build_frame_geometry(info, width, height, thickness,
                         outer_section=None, inner_section=None):
    """The 5-piece FRAME with profiled edges, as (verts, faces, slots)
    in front-cutpart local space (same space as build_door_mesh; slots
    index the stile / rail / panel materials). Panels are the caller's
    job.

    The frame is built as swept bands plus flat lattices instead of
    per-member boxes: the outer section sweeps the door perimeter and
    the inner (sticking) section sweeps each panel opening, mitred at
    the corners -- which is also how cope-and-stick reads from the
    front. Flat front / back faces fill between the bands: four quads
    from the outer band to the openings' hull, strips between the
    openings across mid rails / mid stiles. A None section is a square
    edge (a plain wall), so any mix of outer / inner / no profile
    builds through the same path.

    Sections are [(u, v), ...] from door_profiles.edge_profile_section:
    u across the face from the member edge, v from the front face,
    ordered front end first.
    """
    sq = [(0.0, 0.0), (0.0, thickness)]
    osec = outer_section or sq
    isec = inner_section or sq
    W, H, T = width, height, thickness
    rows = _panel_grid(info, W, H)
    if not rows:
        return [], [], []

    verts, faces, slots = [], [], []

    def emit(x, z, v):
        # Door-local (x across from left, z up, v deep from the front
        # face) into cutpart-local, matching build_door_mesh's mapping.
        verts.append((z, -x, T - v))
        return len(verts) - 1

    def quad(a, b, c, d, slot):
        faces.append((a, b, c, d))
        slots.append(slot)

    _SIDE_SLOTS = (1, 0, 1, 0)   # bottom, right, top, left

    def ring(x0, z0, x1, z1, section, outward, flip):
        """Mitred sweep of ``section`` around a rect; u offsets run
        into the rect (outward=False, door perimeter) or away from it
        (outward=True, panel openings)."""
        corners = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
        dirs = ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
        s = -1.0 if outward else 1.0
        n = len(section)
        base = len(verts)
        for (cx, cz), (dx, dz) in zip(corners, dirs):
            for (u, v) in section:
                emit(cx + s * dx * u, cz + s * dz * u, v)
        for c in range(4):
            a = base + c * n
            b = base + ((c + 1) % 4) * n
            for k in range(n - 1):
                q = (a + k, a + k + 1, b + k + 1, b + k)
                if flip:
                    q = q[::-1]
                quad(*q, _SIDE_SLOTS[c])

    def rect_quad(x0, z0, x1, z1, v, slot, flip):
        if x1 - x0 <= 1e-9 or z1 - z0 <= 1e-9:
            return
        a = emit(x0, z0, v)
        b = emit(x1, z0, v)
        c = emit(x1, z1, v)
        d = emit(x0, z1, v)
        q = (a, b, c, d) if not flip else (d, c, b, a)
        quad(*q, slot)

    def lattice(o_off, s_off, v, flip):
        """Flat lattice at depth v: four quads between the outer band's
        inner rect and the openings' offset hull, then strips across
        the mid members."""
        ox0, oz0 = o_off, o_off
        ox1, oz1 = W - o_off, H - o_off
        fx0 = min(c[0] for r in rows for c in r) - s_off
        fx1 = max(c[2] for r in rows for c in r) + s_off
        fz0 = rows[0][0][1] - s_off
        fz1 = rows[-1][0][3] + s_off
        # Clamp the hull inside the outer rect (huge profiles on tiny
        # members would otherwise cross).
        fx0 = max(fx0, ox0); fz0 = max(fz0, oz0)
        fx1 = min(fx1, ox1); fz1 = min(fz1, oz1)
        Ac = ((ox0, oz0), (ox1, oz0), (ox1, oz1), (ox0, oz1))
        Bc = ((fx0, fz0), (fx1, fz0), (fx1, fz1), (fx0, fz1))
        for c in range(4):
            a0 = emit(*Ac[c], v)
            a1 = emit(*Ac[(c + 1) % 4], v)
            b1 = emit(*Bc[(c + 1) % 4], v)
            b0 = emit(*Bc[c], v)
            q = (a0, a1, b1, b0) if not flip else (b0, b1, a1, a0)
            quad(*q, _SIDE_SLOTS[c])
        for r in range(len(rows) - 1):
            rect_quad(fx0, rows[r][0][3] + s_off,
                      fx1, rows[r + 1][0][1] - s_off, v, 1, flip)
        for row in rows:
            for c in range(len(row) - 1):
                rect_quad(row[c][2] + s_off, row[c][1] - s_off,
                          row[c + 1][0] - s_off, row[c][3] + s_off,
                          v, 0, flip)

    ring(0.0, 0.0, W, H, osec, outward=False, flip=False)
    for row in rows:
        for (cx0, cz0, cx1, cz1) in row:
            ring(cx0, cz0, cx1, cz1, isec, outward=True, flip=True)
    lattice(osec[0][0], isec[0][0], 0.0, flip=False)
    lattice(osec[-1][0], isec[-1][0], T, flip=True)
    return verts, faces, slots


def _emit_raised_panel(verts, faces, slots, part, thickness, panel_section):
    """Raised panel for one opening cell, appended to the caller's
    lists in cutpart-local space: a mitred sweep of the panel section
    around the cell (field end first, u inward from the cell edge, v
    behind the field plane), a flat field plate, and a back plate
    flush with the door back like a flat panel. The field plane sits
    at the part's y_inset. Returns False -- caller keeps the flat box
    -- when the cell is too small for the raise."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    fu = panel_section['field_u']
    if min(x1 - x0, z1 - z0) <= 2.0 * fu + 1e-6:
        return False
    pf = part['y_inset']
    back_v = thickness - pf
    if back_v <= 1e-9:
        return False
    sec = [(u, min(v, back_v)) for (u, v) in panel_section['points']]
    if sec[-1][1] < back_v - 1e-9:
        sec.append((sec[-1][0], back_v))

    def emit(x, z, v):
        verts.append((z, -x, thickness - (pf + v)))
        return len(verts) - 1

    corners = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
    dirs = ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    n = len(sec)
    base = len(verts)
    for (cx, cz), (dx, dz) in zip(corners, dirs):
        for (u, v) in sec:
            emit(cx + dx * u, cz + dz * u, v)
    for c in range(4):
        a = base + c * n
        b = base + ((c + 1) % 4) * n
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
            slots.append(2)
    # Field plate between the four rings' field points.
    faces.append((base + 0 * n, base + 1 * n, base + 2 * n, base + 3 * n))
    slots.append(2)
    # Back plate between the rings' back points.
    faces.append((base + 3 * n + n - 1, base + 2 * n + n - 1,
                  base + 1 * n + n - 1, base + 0 * n + n - 1))
    slots.append(2)
    return True


def build_door_mesh(mesh, info, width, height, thickness, materials=None,
                    outer_section=None, inner_section=None,
                    panel_section=None):
    """Replace ``mesh``'s geometry with the door built as static boxes
    in front-cutpart local space: the door height runs along +X from
    the bottom edge at x=0, the width along -Y (a front cutpart with
    Mirror Y set) with the door's LEFT edge at y=0 -- for a face-frame
    front that is the viewer's left, unlike the CPM_5PIECEDOOR node,
    which rendered its Left / Right stile inputs on the opposite
    sides from their names. The front face is at z=thickness; panels
    sit back from it by their y_inset and use their own thickness.

    With an outer / inner edge section (door_profiles.
    edge_profile_section) the FRAME comes from build_frame_geometry --
    profiled bands swept around the perimeter / openings -- and only
    the panels stay boxes. With ``panel_section`` (door_profiles.
    panel_profile_section) panels build as raised panels instead,
    falling back to the flat box per cell when the cell is too small
    for the raise; the panel section combines freely with or without
    frame sections.

    ``materials`` is an optional (stile, rail, panel) triple assigned
    as the mesh's material slots; face material indices are set either
    way (mid stiles index as stiles, mid rails as rails). Zero-size
    members (e.g. a per-side stile width of 0.0) are skipped.
    """
    profiled = ((outer_section is not None or inner_section is not None)
                and info.get('door_type') != 'SLAB')
    if profiled:
        verts, faces, face_slots = build_frame_geometry(
            info, width, height, thickness, outer_section, inner_section)
        verts = list(verts)
        faces = list(faces)
        face_slots = list(face_slots)
    else:
        verts = []
        faces = []
        face_slots = []
    for part in evaluate_layout(info, width, height):
        if profiled and part['key'] != 'panel':
            continue
        if part['x1'] - part['x0'] <= 0.0 or part['z1'] - part['z0'] <= 0.0:
            continue
        if (part['key'] == 'panel' and panel_section is not None
                and _emit_raised_panel(verts, faces, face_slots, part,
                                       thickness, panel_section)):
            continue
        th = thickness if part['thickness'] is None else part['thickness']
        zf = thickness - part['y_inset']
        x0, x1 = part['z0'], part['z1']
        y0, y1 = -part['x1'], -part['x0']
        z0, z1 = zf - th, zf
        b = len(verts)
        verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        faces.extend([(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                      (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5),
                      (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)])
        face_slots.extend([_PART_MAT_SLOT[part['key']]] * 6)
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    # Slots first: clearing materials drops the material_index layer.
    if materials is not None:
        mesh.materials.clear()
        for mat in materials:
            mesh.materials.append(mat)
    attr = (mesh.attributes.get('material_index')
            or mesh.attributes.new('material_index', 'INT', 'FACE'))
    attr.data.foreach_set('value', face_slots)
    mesh.update()
