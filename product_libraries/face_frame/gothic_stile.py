"""Gothic stiles: ball cuts routed down a face frame end stile.

An integral Gothic stile is the cabinet's own end stile, made wider
(3" typical, up to 6") with half-round "ball cuts" routed down its face:
3/8" round grooves, equally spaced across the stile with 5/16" lands
between them on the typical three, stopped short of each end of the
stile and finished round where the cutter lifts out.

The grooves are booleans against round-ended cutters built in the
stile's own frame, like the corner treatment's arris cutters
(types_face_frame._position_corner_treatment_cutter): x along the
stile's Length (x = 0 at its bottom), y across its Width (sign per
'Mirror Y', u = 0 on the outer edge), the front face on z = 0 with the
thickness running in per 'Mirror Z'.

The root publishes what was built (GOTHIC_STILES = "SIDE:length:width"
entries in metres, GOTHIC_BALL_CUTS) so drawings and pricing read the
built stile rather than recomputing it.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from ... import hb_utils
from ...units import inch

BALL_CUT_DIAMETER = inch(0.375)
# Land between neighbouring cuts on the typical stile.
BALL_CUT_LAND = inch(0.3125)
DEFAULT_BALL_CUTS = 3
DEFAULT_ROUTE_STOP = inch(1.0)
# Stile width a Gothic stile is set to when switched on, and the most
# the catalog makes one.
DEFAULT_WIDTH = inch(3.0)
MAX_WIDTH = inch(6.0)

PART_ROLE_CUTTER = 'GOTHIC_STILE_CUTTER'
MOD_NAME = 'Gothic Ball Cuts'
SIDES = ('LEFT', 'RIGHT')

_SEGMENTS = 16
_CAP_RINGS = 4


def cut_centers(width, count):
    """Positions of the ball cuts across a stile, measured from its
    outer edge: centred on the stile at the catalog pitch (diameter +
    land), spread wider only if the stile is too narrow for that, and
    dropping cuts that cannot fit."""
    count = max(0, int(count))
    pitch = BALL_CUT_DIAMETER + BALL_CUT_LAND
    while count > 0:
        span = pitch * (count - 1)
        if span + BALL_CUT_DIAMETER * 1.5 <= width:
            break
        count -= 1
    if count <= 0:
        return []
    mid = width / 2.0
    return [mid + pitch * (k - (count - 1) / 2.0) for k in range(count)]


def _capsule(bm, ml, y, x0, x1, ys, zs, r):
    """One round-ended groove cutter along x from x0 to x1 at y, centred
    on the front face (z = 0) so half of it is in the stile."""
    rings = []
    # Ring stations along x: a hemisphere at each end, straight between.
    stations = []
    for i in range(_CAP_RINGS + 1):
        a = math.pi / 2.0 * (1.0 - i / _CAP_RINGS)
        stations.append((x0 + r - r * math.cos(a), r * math.sin(a)))
    for i in range(_CAP_RINGS + 1):
        a = math.pi / 2.0 * (i / _CAP_RINGS)
        stations.append((x1 - r + r * math.sin(a), r * math.cos(a)))
    first = last = None
    for idx, (x, rr) in enumerate(stations):
        if rr < 1e-9:
            v = bm.verts.new(ml @ Vector((x, ys * y, 0.0)))
            if idx == 0:
                first = v
            else:
                last = v
            rings.append(None)
            continue
        ring = []
        for k in range(_SEGMENTS):
            t = 2.0 * math.pi * k / _SEGMENTS
            ring.append(bm.verts.new(ml @ Vector(
                (x, ys * (y + rr * math.cos(t)), zs * rr * math.sin(t)))))
        rings.append(ring)
    body = [r_ for r_ in rings if r_ is not None]
    for a, b in zip(body, body[1:]):
        for k in range(_SEGMENTS):
            k2 = (k + 1) % _SEGMENTS
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if first is not None:
        a = body[0]
        for k in range(_SEGMENTS):
            bm.faces.new((first, a[(k + 1) % _SEGMENTS], a[k]))
    if last is not None:
        a = body[-1]
        for k in range(_SEGMENTS):
            bm.faces.new((last, a[k], a[(k + 1) % _SEGMENTS]))


def build_cutter(cutter, part, ml, count, route_stop):
    """Rebuild ``cutter`` as the ball-cut grooves of one stile, in the
    cabinet's frame (``ml`` = stile local -> cabinet). Returns the
    number of cuts built (0 clears it)."""
    try:
        length = part.get_input('Length')
        width = part.get_input('Width')
        mirror_y = bool(part.get_input('Mirror Y'))
        mirror_z = bool(part.get_input('Mirror Z'))
    except Exception:
        cutter.data.clear_geometry()
        return 0
    r = BALL_CUT_DIAMETER / 2.0
    stop = max(0.0, route_stop)
    x0, x1 = stop, length - stop
    centers = cut_centers(width, count)
    if not centers or x1 - x0 < 2.0 * r + inch(0.5):
        cutter.data.clear_geometry()
        return 0
    ys = -1.0 if mirror_y else 1.0
    zs = -1.0 if mirror_z else 1.0
    bm = bmesh.new()
    for y in centers:
        _capsule(bm, ml, y, x0, x1, ys, zs, r)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(cutter.data)
    bm.free()
    cutter.location = (0.0, 0.0, 0.0)
    cutter.rotation_euler = (0.0, 0.0, 0.0)
    return len(centers)


def _cutters(cabinet_obj):
    return [c for c in cabinet_obj.children
            if c.get('hb_part_role') == PART_ROLE_CUTTER]


def ensure_cutter(cabinet_obj, side):
    for child in _cutters(cabinet_obj):
        if child.get('hb_side') == side:
            return child
    name = 'Gothic Stile Cutter %s' % side.title()
    cutter = hb_utils.new_object(name, bpy.data.meshes.new(name))
    cutter['hb_part_role'] = PART_ROLE_CUTTER
    cutter['hb_side'] = side
    cutter.parent = cabinet_obj
    cutter.display_type = 'WIRE'
    cutter.hide_render = True
    cutter.hide_viewport = True
    for coll in cabinet_obj.users_collection:
        coll.objects.link(cutter)
        break
    return cutter


def wanted_sides(cab_props):
    return [s for s in SIDES
            if getattr(cab_props, 'gothic_stile_%s' % s.lower(), False)]


def apply(cabinet_obj, cab_props, stiles, matrix_to_root, cutpart_cls):
    """Cut (or clear) the ball cuts on the cabinet's Gothic end stiles.

    ``stiles`` maps 'LEFT' / 'RIGHT' to that end stile object (or None).
    Safe every recalc: cutters, booleans and the published props for
    sides switched off are removed."""
    count = getattr(cab_props, 'gothic_ball_cuts', DEFAULT_BALL_CUTS)
    stop = getattr(cab_props, 'gothic_route_stop', DEFAULT_ROUTE_STOP)
    live = {}
    built = []
    for side in wanted_sides(cab_props):
        stile = stiles.get(side)
        if stile is None or stile.hide_viewport:
            continue
        part = cutpart_cls(stile)
        cutter = ensure_cutter(cabinet_obj, side)
        n = build_cutter(cutter, part, matrix_to_root(stile, cabinet_obj),
                         count, stop)
        if not n:
            continue
        live[stile.name] = cutter
        mod = stile.modifiers.get(MOD_NAME)
        if mod is None:
            mod = stile.modifiers.new(name=MOD_NAME, type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.solver = 'EXACT'
        mod.material_mode = 'TRANSFER'
        if mod.object is not cutter:
            mod.object = cutter
        try:
            built.append('%s:%.5f:%.5f' % (side, part.get_input('Length'),
                                           part.get_input('Width')))
        except Exception:
            built.append('%s:0:0' % side)
        cabinet_obj['GOTHIC_BALL_CUTS'] = n

    # Drop booleans on stiles that no longer carry a live cutter, and
    # cutters for sides switched off.
    live_cutters = set(live.values())
    for child in cabinet_obj.children:
        mod = child.modifiers.get(MOD_NAME) if child.type == 'MESH' else None
        if mod is not None and live.get(child.name) is None:
            child.modifiers.remove(mod)
    for cutter in _cutters(cabinet_obj):
        if cutter not in live_cutters:
            mesh = cutter.data
            bpy.data.objects.remove(cutter, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
    if built:
        cabinet_obj['GOTHIC_STILES'] = ','.join(built)
    else:
        for key in ('GOTHIC_STILES', 'GOTHIC_BALL_CUTS'):
            if key in cabinet_obj:
                del cabinet_obj[key]
