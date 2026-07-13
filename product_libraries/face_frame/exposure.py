"""Side exposure detection for face frame cabinets.

For each face-frame cabinet, computes per-side exposure state
(UNEXPOSED / PARTIAL / EXPOSED) and a dishwasher-adjacent flag by
walking parent-wall siblings and comparing Z-bands. Then resolves the
finished-end-condition per side per the priority rule (dishwasher
wins, then partial, then full, then unexposed) - but only on sides
that still have the auto flag enabled.

Wall-edge handling is intentionally simple: a cabinet sitting at the
parent wall's start or end is treated as UNEXPOSED on that side
(perpendicular wall / corner case). A free-standing cabinet whose end
face sits flush against a wall face (peninsula) is likewise UNEXPOSED
on that side, with the wall scribe.

Back exposure is reduced to UNEXPOSED-when-wall-parented; partial
backs don't show up in practice.
"""
import bpy
from mathutils import Vector

from ... import hb_types, units
from . import types_face_frame


# Abutment / wall-edge tolerance. Matches the value used by the
# placement auto-merge so neighbor-finding agrees on what counts as
# touching.
EPS = 1e-4

# Auto scribe amounts for unfinished sides. Wall-against gets the
# larger value because real walls aren't straight and need room to
# scribe the side panel to. Neighbor-against gets a small gap to
# absorb face-frame stack-up across the run without crushing.
_WALL_SCRIBE = units.inch(0.5)
_NEIGHBOR_SCRIBE = units.inch(0.25)


# ---------------------------------------------------------------------------
# Neighbor probing (parent-wall siblings)
# ---------------------------------------------------------------------------

def _is_face_frame_carcass(obj):
    """True when obj is a face-frame cabinet root with a real carcass
    (BASE / TALL / UPPER / LAP_DRAWER). Filters out PANEL roots, which
    share the TAG_CABINET_CAGE marker but are standalone applied panels
    parented to a cabinet - they don't participate in exposure.
    """
    if not obj.get(types_face_frame.TAG_CABINET_CAGE):
        return False
    return obj.face_frame_cabinet.cabinet_type != 'PANEL'


def _neighbor_xspan(obj):
    """(x_min, x_max) in parent-wall local space, or None if obj is
    neither a face-frame carcass cabinet nor an appliance. Cabinets and
    appliances grow +X from location.x. Applied panels are excluded -
    see _is_face_frame_carcass.
    """
    x = obj.location.x
    if _is_face_frame_carcass(obj):
        return (x, x + obj.face_frame_cabinet.width)
    if obj.get('IS_APPLIANCE'):
        try:
            w = hb_types.GeoNodeObject(obj).get_input('Dim X')
        except Exception:
            return None
        return (x, x + w)
    return None


def _neighbor_zspan(obj):
    """(z_min, z_max) in parent-wall local space, or None for unrecognized
    children. Face frame cabinets read height from face_frame_cabinet;
    appliances read Dim Z from their GeoNodeObject input. Applied panels
    are excluded - see _is_face_frame_carcass.
    """
    z = obj.location.z
    if _is_face_frame_carcass(obj):
        return (z, z + obj.face_frame_cabinet.height)
    if obj.get('IS_APPLIANCE'):
        try:
            h = hb_types.GeoNodeObject(obj).get_input('Dim Z')
        except Exception:
            return None
        return (z, z + h)
    return None


def _is_dishwasher(obj):
    return bool(obj.get('IS_APPLIANCE')) and obj.get('APPLIANCE_TYPE') == 'DISHWASHER'


def _union_zcoverage(bands, z_min, z_max):
    """Union the given [z0, z1] bands clamped to [z_min, z_max] and
    return total covered length. Caller compares to (z_max - z_min) to
    classify FULL / PARTIAL / NONE.
    """
    clamped = []
    for (a, b) in bands:
        a = max(a, z_min)
        b = min(b, z_max)
        if b > a:
            clamped.append((a, b))
    if not clamped:
        return 0.0
    clamped.sort()
    merged = [clamped[0]]
    for (a, b) in clamped[1:]:
        ma, mb = merged[-1]
        if a <= mb + EPS:
            merged[-1] = (ma, max(mb, b))
        else:
            merged.append((a, b))
    return sum(b - a for (a, b) in merged)


# ---------------------------------------------------------------------------
# Per-side detection
# ---------------------------------------------------------------------------

def _wall_length(parent_obj):
    """Read the parent wall's Length input. None if parent isn't a
    GeoNodeWall (e.g. cabinet floating free).
    """
    if parent_obj is None:
        return None
    try:
        return hb_types.GeoNodeWall(parent_obj).get_input('Length')
    except Exception:
        return None


# End-against-wall abutment tolerances (peninsula anchor). Placement
# lands the end exactly flush; the gap tolerance absorbs manual nudges.
# Lateral overlap keeps a cabinet merely passing near a wall's end
# from reading as anchored to it.
_WALL_GAP_TOL = units.inch(0.125)
_WALL_LATERAL_TOL = units.inch(0.5)


def _end_abuts_wall(cab_obj, side):
    """True when a free-standing cabinet's left/right end face sits
    flush against a wall face - the peninsula anchor. That end is
    covered by the wall, so it reads UNEXPOSED with the wall scribe.
    """
    if cab_obj.parent is not None:
        return False
    if not _is_face_frame_carcass(cab_obj):
        return False
    cp = cab_obj.face_frame_cabinet
    mw = cab_obj.matrix_world
    # End face in plan: local x = 0 (left) or width (right), running
    # from the back plane (y=0) to the front (y=-depth).
    end_x = 0.0 if side == 'left' else cp.width
    p0w = mw @ Vector((end_x, 0.0, 0.0))
    p1w = mw @ Vector((end_x, -cp.depth, 0.0))
    p0 = Vector((p0w.x, p0w.y))
    p1 = Vector((p1w.x, p1w.y))
    n_local = Vector((-1.0, 0.0, 0.0)) if side == 'left' else Vector((1.0, 0.0, 0.0))
    n3 = mw.to_3x3() @ n_local
    end_normal = Vector((n3.x, n3.y))
    if end_normal.length < 1e-6:
        return False
    end_normal.normalize()

    cab_z0 = mw.translation.z
    cab_z1 = cab_z0 + cp.height

    for wall_obj in bpy.context.scene.objects:
        if 'IS_WALL_BP' not in wall_obj:
            continue
        try:
            wall = hb_types.GeoNodeWall(wall_obj)
            if not wall.has_modifier():
                continue
            length = wall.get_input('Length')
            thickness = wall.get_input('Thickness')
            height = wall.get_input('Height')
        except Exception:
            continue
        wm = wall_obj.matrix_world
        wall_z0 = wm.translation.z
        # Z overlap so a pony wall doesn't anchor an upper above it.
        if cab_z0 >= wall_z0 + height - EPS or cab_z1 <= wall_z0 + EPS:
            continue
        # Front face (local y=0, outward -Y) and back face (+Y).
        for face_y, ny in ((0.0, -1.0), (thickness, 1.0)):
            f0 = wm @ Vector((0.0, face_y, 0.0))
            f1 = wm @ Vector((length, face_y, 0.0))
            a0 = Vector((f0.x, f0.y))
            a1 = Vector((f1.x, f1.y))
            axis = a1 - a0
            if axis.length < 1e-6:
                continue
            axis_n = axis.normalized()
            w3 = wm.to_3x3() @ Vector((0.0, ny, 0.0))
            face_normal = Vector((w3.x, w3.y))
            if face_normal.length < 1e-6:
                continue
            face_normal.normalize()
            # The end must face INTO the wall face.
            if end_normal.dot(face_normal) > -0.7:
                continue
            # Both end-face corners on the wall-face plane...
            if (abs((p0 - a0).dot(face_normal)) > _WALL_GAP_TOL
                    or abs((p1 - a0).dot(face_normal)) > _WALL_GAP_TOL):
                continue
            # ...with real lateral overlap of the wall segment.
            t0 = (p0 - a0).dot(axis_n)
            t1 = (p1 - a0).dot(axis_n)
            lo, hi = min(t0, t1), max(t0, t1)
            if min(hi, axis.length) - max(lo, 0.0) >= _WALL_LATERAL_TOL:
                return True
    return False


def _side_exposure(cab_obj, side):
    """Returns (exposure_state, dishwasher_adjacent, wall_edge).

    wall_edge is True only when UNEXPOSED was reached by hitting the
    parent wall's start/end - it's the signal _resolve_scribe uses to
    pick 0.5" (wall) vs. 0.25" (neighbor) on unfinished sides. PARTIAL
    and EXPOSED never carry wall_edge=True since the early-return
    happens before the neighbor loop.
    """
    parent = cab_obj.parent
    if parent is None:
        # Free-standing (island / peninsula): an end flush against a
        # wall face is the peninsula anchor - covered, wall scribe.
        if _end_abuts_wall(cab_obj, side):
            return ('UNEXPOSED', False, True)
        return ('EXPOSED', False, False)

    cab = cab_obj.face_frame_cabinet
    cab_x = cab_obj.location.x
    cab_z = cab_obj.location.z
    cab_w = cab.width
    cab_h = cab.height
    wall_length = _wall_length(parent)

    if side == 'left' and cab_x <= EPS:
        return ('UNEXPOSED', False, True)
    if side == 'right' and wall_length is not None and (cab_x + cab_w) >= (wall_length - EPS):
        return ('UNEXPOSED', False, True)

    target_x = cab_x if side == 'left' else cab_x + cab_w
    bands = []
    dishwasher_seen = False

    for sib in parent.children:
        if sib is cab_obj:
            continue
        xspan = _neighbor_xspan(sib)
        if xspan is None:
            continue
        # Sibling's near edge must coincide with our side's X.
        sib_near_x = xspan[1] if side == 'left' else xspan[0]
        if abs(sib_near_x - target_x) > EPS:
            continue
        zspan = _neighbor_zspan(sib)
        if zspan is None:
            continue
        bands.append(zspan)
        if _is_dishwasher(sib):
            dishwasher_seen = True

    if not bands:
        return ('EXPOSED', False, False)

    coverage = _union_zcoverage(bands, cab_z, cab_z + cab_h)
    if coverage >= cab_h - EPS:
        return ('UNEXPOSED', dishwasher_seen, False)
    if coverage > EPS:
        return ('PARTIAL', dishwasher_seen, False)
    return ('EXPOSED', False, False)


# Back-to-back abutment tolerances. A cabinet placed against the back of
# another run sits with its carcass back plane flush against that run's
# back plane; these decide when two back faces read as the same plane.
_BACK_GAP_TOL = units.inch(0.125)    # plane separation along the normal
_BACK_LATERAL_TOL = units.inch(0.5)  # min lateral overlap to count


def _back_face_segment(cab_obj):
    """World-space back face of a free-standing face-frame carcass.

    Returns (p0, p1, outward_normal) as XY-plane mathutils Vectors, or
    None for wall-parented cabinets and non-carcass roots. The back-to-
    back case only arises between free-standing island runs.
    """
    if cab_obj.parent is not None:
        return None
    if not _is_face_frame_carcass(cab_obj):
        return None
    cp = cab_obj.face_frame_cabinet
    mw = cab_obj.matrix_world
    # Carcass origin is back-left; depth extrudes -Y toward the front, so
    # the back edge runs local (0,0) to (width,0) and the outward back
    # normal is local +Y (pointing away from the carcass interior).
    bl = mw @ Vector((0.0, 0.0, 0.0))
    br = mw @ Vector((cp.width, 0.0, 0.0))
    p0 = Vector((bl.x, bl.y))
    p1 = Vector((br.x, br.y))
    n3 = mw.to_3x3() @ Vector((0.0, 1.0, 0.0))
    normal = Vector((n3.x, n3.y))
    if normal.length > 1e-6:
        normal.normalize()
    return (p0, p1, normal)


def _backs_coincident(seg_a, seg_b):
    """True when two back-face segments sit back-to-back: same world
    plane, opposing outward normals, enough lateral overlap.
    """
    p0a, p1a, na = seg_a
    p0b, p1b, nb = seg_b
    # Opposing normals: the carcasses face into each other.
    if na.dot(nb) > -0.999:
        return False
    # Same plane: b's near endpoint sits on a's back line within tol.
    if abs((p0b - p0a).dot(na)) > _BACK_GAP_TOL:
        return False
    # Lateral overlap measured along a's back edge.
    axis = p1a - p0a
    length = axis.length
    if length < 1e-6:
        return False
    axis = axis / length
    tb0 = (p0b - p0a).dot(axis)
    tb1 = (p1b - p0a).dot(axis)
    b_lo, b_hi = min(tb0, tb1), max(tb0, tb1)
    overlap = min(length, b_hi) - max(0.0, b_lo)
    return overlap >= _BACK_LATERAL_TOL


def _find_back_abutting_cabinets(cab_obj):
    """Free-standing face-frame carcass cabinets whose back face is flush
    against cab_obj's back face. Empty for wall-parented cabinets: the
    back-to-back case only happens off-wall.
    """
    seg = _back_face_segment(cab_obj)
    if seg is None:
        return []
    hits = []
    for obj in bpy.context.scene.objects:
        if obj is cab_obj:
            continue
        other = _back_face_segment(obj)
        if other is None:
            continue
        if _backs_coincident(seg, other):
            hits.append(obj)
    return hits


def _back_exposure(cab_obj):
    """UNEXPOSED when the cabinet is wall-parented (back to the wall) or
    when its carcass back is flush against another free-standing run
    (island placed back-to-back). EXPOSED otherwise.
    """
    if cab_obj.parent is not None:
        return 'UNEXPOSED'
    if _find_back_abutting_cabinets(cab_obj):
        return 'UNEXPOSED'
    return 'EXPOSED'


# ---------------------------------------------------------------------------
# Finish-type resolution + per-cabinet recalc
# ---------------------------------------------------------------------------

def _resolve_finish_type(scene_props, exposure_state, dishwasher_adjacent,
                         side='left'):
    """Priority rule: dishwasher beats partial beats fully-exposed
    beats unexposed. Returns a value from FIN_END_ITEMS.

    The dishwasher branch reads the scene preference rather than a
    hardwired FLUSH_X, so shops that don't run a flush fin next to a
    dishwasher can pick a different type (or Unfinished for none).

    EXPOSED resolves per side: BACK reads the scene's
    default_finished_back_type, L/R the default_finished_end_type --
    a shop often runs a different treatment on an exposed island
    back than on exposed ends.
    """
    if dishwasher_adjacent:
        return scene_props.dishwasher_finished_end_type
    if exposure_state == 'PARTIAL':
        return 'FINISHED'
    if exposure_state == 'EXPOSED':
        if side == 'back':
            return scene_props.default_finished_back_type
        return scene_props.default_finished_end_type
    return 'UNFINISHED'


def _resolve_scribe(state, dishwasher, wall_edge, finish):
    """Auto scribe rule, keyed on the RESOLVED finish type: the solver
    only reads the typed scribe on UNFINISHED sides, so every other
    type zeroes out (avoids stale numbers in the UI when the dropdown
    shows a non-UNFINISHED type). On an UNFINISHED side, a dishwasher
    counts as a neighbor (0.25" stack-up gap); otherwise wall-edge
    UNEXPOSED gets 0.5" and neighbor-driven UNEXPOSED gets 0.25".
    """
    if finish != 'UNFINISHED':
        return 0.0
    if dishwasher:
        return _NEIGHBOR_SCRIBE
    if state == 'UNEXPOSED':
        return _WALL_SCRIBE if wall_edge else _NEIGHBOR_SCRIBE
    return 0.0


def _apply_side(cab, side, state, dishwasher, wall_edge, scene_props):
    """Writes exposure / dishwasher flags unconditionally, then (only
    when auto is on) writes finish_end_condition and scribe. Auto gets
    re-armed last because the per-side update callbacks on the finish
    enum and on scribe both flip it off when they fire.
    """
    setattr(cab, f'{side}_exposure', state)
    if side != 'back':
        setattr(cab, f'{side}_dishwasher_adjacent', dishwasher)
    if not getattr(cab, f'{side}_finish_end_auto'):
        return
    finish = _resolve_finish_type(scene_props, state, dishwasher, side)
    setattr(cab, f'{side}_finished_end_condition', finish)
    if side != 'back':
        setattr(cab, f'{side}_scribe',
                _resolve_scribe(state, dishwasher, wall_edge, finish))
        if finish == 'FLUSH_X':
            # Seed the amount from the scene default so the prefs field
            # actually drives what auto-pick produces (the per-cabinet
            # prop's own 4" default was the only source before). Manual
            # edits survive: a user edit flips auto off, and this whole
            # block is gated on auto above.
            setattr(cab, f'{side}_flush_x_amount',
                    scene_props.default_flush_x_amount)
    setattr(cab, f'{side}_finish_end_auto', True)


def recalc_cabinet_exposure(cab_obj):
    """Recompute exposure (+ dishwasher flag) for all three sides of one
    cabinet, then auto-pick finish type and scribe per side where
    allowed. PANEL roots are skipped - they're applied panels, not
    carcass cabinets, and their per-side props don't drive visible
    geometry.
    """
    if not _is_face_frame_carcass(cab_obj):
        return
    # Leg products pass the carcass test (cabinet_type BASE) so they
    # stay visible to the neighbor coverage scan - but their finish is
    # the leg_product.finish_type (auto_leg_finish_type), NOT the
    # cabinet finished-end conditions. Stamping conditions here put an
    # un-removable finished-end callout on legs in the 2D drawings
    # (the Leg Properties UI only exposes finish_type), e.g. a leg
    # beside a dishwasher carrying a '4\" FLUSH FIN' note nothing
    # could clear. Skip the stamp; legs keep their neighbor role.
    if cab_obj.get('IS_LEG_PRODUCT'):
        return
    cab = cab_obj.face_frame_cabinet
    scene_props = bpy.context.scene.hb_face_frame

    for side in ('left', 'right'):
        state, dishwasher, wall_edge = _side_exposure(cab_obj, side)
        _apply_side(cab, side, state, dishwasher, wall_edge, scene_props)

    # Back has no scribe column on the props so wall_edge is irrelevant;
    # pass False to keep the signature uniform.
    back_state = _back_exposure(cab_obj)
    _apply_side(cab, 'back', back_state, False, False, scene_props)


# ---------------------------------------------------------------------------
# Placement / sweep entry points
# ---------------------------------------------------------------------------

def _find_immediate_face_frame_neighbors(cab_obj):
    """Returns (left, right) face-frame carcass siblings abutting cab_obj.
    Used by the placement hook to refresh neighbors whose facing side
    just changed state. PANEL roots are skipped.
    """
    if cab_obj.parent is None:
        return (None, None)
    cab_x = cab_obj.location.x
    cab_w = cab_obj.face_frame_cabinet.width
    left = None
    right = None
    for sib in cab_obj.parent.children:
        if sib is cab_obj:
            continue
        if not _is_face_frame_carcass(sib):
            continue
        xspan = _neighbor_xspan(sib)
        if xspan is None:
            continue
        if abs(xspan[1] - cab_x) <= EPS:
            left = sib
        elif abs(xspan[0] - (cab_x + cab_w)) <= EPS:
            right = sib
    return (left, right)


def _find_immediate_face_frame_neighbors_of_point(parent_obj, target_x):
    """Returns face-frame cabinet siblings of parent_obj whose left or
    right edge touches target_x. Used by the appliance placement hook
    where the placed object isn't itself a cabinet.
    """
    hits = []
    if parent_obj is None:
        return hits
    for sib in parent_obj.children:
        if not _is_face_frame_carcass(sib):
            continue
        xspan = _neighbor_xspan(sib)
        if xspan is None:
            continue
        if abs(xspan[1] - target_x) <= EPS or abs(xspan[0] - target_x) <= EPS:
            hits.append(sib)
    return hits


def auto_leg_finish_type(leg_obj):
    """Pick a leg product's finish_type from its left/right exposure.

    Rules, in order:
    - A dishwasher beside the leg wins: finish the side OPPOSITE it
      (the dishwasher butts against the leg, so the show face points
      away). One dishwasher -> a single finished side; a dishwasher on
      each side -> FINISH_BOTH.
    - Otherwise a side counts as open (needs finish) when EXPOSED /
      PARTIAL; UNEXPOSED behind a cabinet / wall does not. Both open ->
      FINISH_BOTH, one open -> finish that side, neither -> INTERMEDIATE
      (a filler buried between cabinets).

    Uses the same sibling-abutment scan as cabinet side exposure, so it
    only sees neighbours on a shared parent wall; a free-standing
    (unparented) leg reports both sides exposed -> FINISH_BOTH.
    """
    le_state, le_dishwasher, _ = _side_exposure(leg_obj, 'left')
    re_state, re_dishwasher, _ = _side_exposure(leg_obj, 'right')

    # Dishwasher takes priority: the dishwasher butts against the leg
    # on that side, so the visible finished panel faces AWAY from it -
    # finish the OPPOSITE side. A dishwasher on each side -> FINISH_BOTH.
    if le_dishwasher or re_dishwasher:
        if le_dishwasher and re_dishwasher:
            return 'FINISH_BOTH'
        return 'FINISH_RIGHT' if le_dishwasher else 'FINISH_LEFT'

    # No dishwasher: open sides (EXPOSED / PARTIAL) get finished;
    # UNEXPOSED (cabinet / wall) doesn't.
    left_open = le_state != 'UNEXPOSED'
    right_open = re_state != 'UNEXPOSED'
    if left_open and right_open:
        return 'FINISH_BOTH'
    if left_open:
        return 'FINISH_LEFT'
    if right_open:
        return 'FINISH_RIGHT'
    return 'INTERMEDIATE'


def auto_floating_shelf_finish(shelf_obj):
    """(finish_left, finish_right) for a floating shelf from its end
    exposure. An end is finished (gets a closed panel) when EXPOSED /
    PARTIAL - open to view - and left open when a cabinet / wall covers
    it (UNEXPOSED). Uses the same vertical-overlap sibling scan as
    cabinet side exposure, so only neighbours at the shelf's height
    count; a free-standing shelf finishes both ends.
    """
    left_finished = _side_exposure(shelf_obj, 'left')[0] != 'UNEXPOSED'
    right_finished = _side_exposure(shelf_obj, 'right')[0] != 'UNEXPOSED'
    return (left_finished, right_finished)


def recalc_with_neighbors(cab_obj):
    """Placement convenience: recalc this cabinet, the immediate L/R
    face-frame neighbors whose facing side just changed coverage, and
    any free-standing run cab_obj was placed back-to-back against -
    those cabinets' backs just became unexposed.
    """
    # cab_obj may have just been placed or moved; refresh matrix_world
    # before the back-abutment scan reads sibling transforms.
    bpy.context.view_layer.update()
    with types_face_frame.suspend_recalc():
        recalc_cabinet_exposure(cab_obj)
        left, right = _find_immediate_face_frame_neighbors(cab_obj)
        if left is not None:
            recalc_cabinet_exposure(left)
        if right is not None:
            recalc_cabinet_exposure(right)
        for back_neighbor in _find_back_abutting_cabinets(cab_obj):
            recalc_cabinet_exposure(back_neighbor)


def recalc_after_appliance_placement(app_obj):
    """Placement hook for appliances. Refreshes any face-frame cabinet
    whose side now abuts the placed appliance.
    """
    parent = app_obj.parent
    if parent is None:
        return
    xspan = _neighbor_xspan(app_obj)
    if xspan is None:
        return
    touched = set()
    for x in xspan:
        for sib in _find_immediate_face_frame_neighbors_of_point(parent, x):
            touched.add(sib)
    if not touched:
        return
    with types_face_frame.suspend_recalc():
        for sib in touched:
            recalc_cabinet_exposure(sib)


def recalc_all_cabinet_exposure(context):
    """Sweep every face-frame carcass cabinet in the scene. Re-arms auto
    on all sides before computing so a prior manual override doesn't
    survive a user-initiated Recalculate request. PANEL roots are
    skipped.
    """
    cabs = [obj for obj in context.scene.objects
            if _is_face_frame_carcass(obj)]
    with types_face_frame.suspend_recalc():
        for obj in cabs:
            cp = obj.face_frame_cabinet
            cp.left_finish_end_auto = True
            cp.right_finish_end_auto = True
            cp.back_finish_end_auto = True
        for obj in cabs:
            recalc_cabinet_exposure(obj)
