"""Per-library fact providers for the molding engine.

The engine works on world geometry plus a FACTS dict; these adapters
read each library's property groups / tags and produce those facts, so
the engine itself stays library-agnostic. Both HB5 libraries are
covered: face frame and frameless.
"""

import bpy
import mathutils

from . import engine
from .. import hb_types, units


# Roots eligible per molding type, per library.
_CROWN_TYPES = ('UPPER', 'TALL')
_BASE_TYPES = ('BASE', 'TALL', 'LAP_DRAWER')
_RAIL_TYPES = ('UPPER',)


def _face_frame_roots(scene, types):
    out = []
    for obj in scene.objects:
        if not obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            continue
        ffc = getattr(obj, 'face_frame_cabinet', None)
        if ffc is None or ffc.cabinet_type not in types:
            continue
        out.append(obj)
    return out


def _frameless_roots(scene, types):
    out = []
    for obj in scene.objects:
        if not (obj.get('IS_FRAMELESS_CABINET_CAGE')
                or obj.get('IS_FRAMELESS_PRODUCT_CAGE')):
            continue
        if obj.get('CABINET_TYPE', '') not in types:
            continue
        out.append(obj)
    return out


def collect_targets(scene, molding_type):
    """Eligible molding-carrying roots in the room, across both
    libraries. molding_type in {'CROWN', 'BASE', 'LIGHT_RAIL'}."""
    types = {'CROWN': _CROWN_TYPES,
             'CAP': _CROWN_TYPES,
             'BASE': _BASE_TYPES,
             'LIGHT_RAIL': _RAIL_TYPES}[molding_type]
    return _face_frame_roots(scene, types) + _frameless_roots(scene, types)


def collect_bridges(scene):
    """Floor-standing appliances that sit inside runs (dishwashers,
    ranges, freestanding refrigerators): they keep a run in one piece
    and contribute skip spans."""
    out = []
    for obj in scene.objects:
        if not obj.get('IS_APPLIANCE'):
            continue
        if obj.matrix_world.translation.z > 0.02:
            continue  # mounted at height (wall ovens, OTR microwaves)
        out.append(obj)
    return out


# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------

_RECESSED_FF_KICKS = {'NOTCH', 'LOOSE', 'FLOATING'}

# Cages that are a cabinet in their own right rather than a part of the
# one above them.
_NESTED_CAGE_KEYS = ('IS_FACE_FRAME_CABINET_CAGE',
                     'IS_FRAMELESS_CABINET_CAGE',
                     'IS_FRAMELESS_PRODUCT_CAGE')


def _own_parts(cage):
    """Descendants that belong to CAGE's OWN face frame.

    An applied end panel is a face frame cabinet in its own right,
    parented to the cabinet it covers, and it carries its own rails,
    stiles and panels. children_recursive walks straight into one - and
    the panel's parts come out FIRST - so a plain recursive search
    reads the END's frame everywhere it means to read the FRONT's: the
    crown mounts off the panel's top rail instead of the rail the doors
    sit under, and the floor scan sees the panel's bottom rail (which
    runs to the floor by design) as a flush front.

    Stop at anything that is its own cabinet.
    """
    stack = list(cage.children)
    while stack:
        child = stack.pop()
        if any(child.get(key) for key in _NESTED_CAGE_KEYS):
            continue
        stack.extend(child.children)
        yield child


def _floor_flush_spans(cage):
    """LOCAL width spans (x0, x1) where a recessed-kick cabinet's
    front runs to the floor: a bay with its kick height zeroed builds
    its bottom rail down to the floor, and the mid stiles flanking it
    run to the floor with it - together they are the flush section the
    base molding wraps out of the recess. Read from the built geometry
    (it's exactly what's drawn); touching spans merge, so rail plus
    flanking stiles become one wrap. End stiles are handled by the
    stile facts instead."""
    found = []
    inv = cage.matrix_world.inverted()
    for child in _own_parts(cage):
        if child.get('hb_part_role') not in ('BOTTOM_RAIL', 'MID_STILE'):
            continue
        corners = [inv @ (child.matrix_world @ mathutils.Vector(c))
                   for c in child.bound_box]
        if min(c.z for c in corners) > 0.005:
            continue  # rail stops above the kick - bay is recessed
        xs = [c.x for c in corners]
        if max(xs) - min(xs) < 1e-4:
            continue
        found.append((min(xs), max(xs)))
    found.sort()
    merged = []
    for x0, x1 in found:
        if merged and x0 - merged[-1][1] < 1e-4:
            merged[-1] = (merged[-1][0], max(merged[-1][1], x1))
        else:
            merged.append((x0, x1))
    return merged


# Kick-face parts the base molding mounts against, front-most wins:
# the finish kick skin sits on the subfront, a loose kick carries its
# own front.
_KICK_FACE_ROLES = ('FINISH_TOE_KICK', 'LOOSE_KICK_FRONT',
                    'TOE_KICK_SUBFRONT')


def _measured_kick_setback(cage, ffc):
    """Setback from the CAGE front to the face the base molding mounts
    on, read from the front-most built kick-face part. The
    toe_kick_setback prop measures to the subfront from the cage
    front too, but a finish skin over the subfront moves the mounting
    face forward, so the built part is the one to read.
    Falls back to the prop when no kick-face part is built."""
    inv = cage.matrix_world.inverted()
    best = None
    for child in _own_parts(cage):
        if child.get('hb_part_role') not in _KICK_FACE_ROLES:
            continue
        corners = [inv @ (child.matrix_world @ mathutils.Vector(c))
                   for c in child.bound_box]
        if (max(c.z for c in corners) - min(c.z for c in corners) < 0.01
                or max(c.x for c in corners) - min(c.x for c in corners)
                < 0.01):
            continue  # dormant zero-size part
        y = min(c.y for c in corners)
        if best is None or y < best:
            best = y
    if best is None:
        return ffc.toe_kick_setback
    _width, depth, _height = engine.cage_dims(cage)
    return max(depth + best, 0.0)


def _finished_back_offset(obj):
    """How far a finished back stands proud of the cage's back plane.

    A finished back is built as a SEPARATE 3/4 panel layered behind the
    carcass (the carcass back keeps its own thickness), so an island's
    base molding has to wrap the panel's face - on the cage plane it
    ends up buried inside it. Measured off the built part; 0 when there
    isn't one.
    """
    inv = obj.matrix_world.inverted()
    best = 0.0
    for child in _own_parts(obj):
        if child.get('hb_part_role') != 'FINISHED_BACK':
            continue
        corners = [inv @ (child.matrix_world @ mathutils.Vector(c))
                   for c in child.bound_box]
        if (max(c.z for c in corners) - min(c.z for c in corners) < 0.01
                or max(c.x for c in corners) - min(c.x for c in corners)
                < 0.01):
            continue  # dormant zero-size part
        best = max(best, max(c.y for c in corners))
    return best


def _rail_bays(cage):
    """Per-zone light-rail data for an upper: sorted (x0, x1, dz)
    zones partitioning the cabinet width. dz is the zone's bottom line
    relative to the CABINET's bottom line - bay offsets are measured
    from the bay level nearest the root line, so raised bays go
    positive and dropped bays negative. The stile gap between two bays
    goes to the LOWER zone (its stile runs down with it); end stiles
    go to their end bay's zone."""
    bays = []
    for child in cage.children:
        if not child.get('IS_FACE_FRAME_BAY_CAGE'):
            continue
        bp = getattr(child, 'face_frame_bay', None)
        if bp is None or bp.width <= 1e-4:
            continue
        x = child.matrix_local.translation.x
        bays.append([x, x + bp.width, child.matrix_local.translation.z])
    if not bays:
        return []
    bays.sort()
    ref = min((z for _x0, _x1, z in bays), key=abs)
    width, _depth, _height = engine.cage_dims(cage)
    zones = [[x0, x1, z - ref] for x0, x1, z in bays]
    zones[0][0] = 0.0
    zones[-1][1] = width
    for a, b in zip(zones, zones[1:]):
        if a[2] <= b[2]:
            a[1] = b[0]
        else:
            b[0] = a[1]
    return [tuple(z) for z in zones]


def _rail_skip_spans(cage):
    """Zones of an upper the BOTTOM-LINE light rail skips: bays whose
    bottom line sits off the cabinet's bottom line, as
    [(x0, x1, kind)]. kind says how the run line meets the zone:
    'OPEN' (raised bay - nothing at the run line, the rail returns to
    the wall at the zone edges) or 'BOX' (dropped bay - its box stands
    across the run line, the rail dies flush into it). Either way the
    zone carries its own rail at its own line - see
    engine.raised_rail_runs."""
    bays = _rail_bays(cage)
    if len(bays) < 2:
        return []
    out = []
    for x0, x1, dz in bays:
        if abs(dz) <= 0.02:
            continue
        kind = 'OPEN' if dz > 0.0 else 'BOX'
        if out and out[-1][2] == kind and x0 - out[-1][1] < 1e-4:
            out[-1] = (out[-1][0], x1, kind)
        else:
            out.append((x0, x1, kind))
    return out


def _top_rail_width(cage):
    """Width of the built TOP_RAIL face-frame part, read from the
    geometry rather than the style props - it's exactly what's drawn."""
    for child in _own_parts(cage):
        if child.get('hb_part_role') != 'TOP_RAIL':
            continue
        try:
            width = hb_types.GeoNodeObject(child).get_input('Width')
        except Exception:
            width = None
        if width:
            return width
    return None


def _wall_bounds(scene):
    bounds = []
    for wall in scene.objects:
        if not wall.get('IS_WALL_BP'):
            continue
        corners = [wall.matrix_world @ mathutils.Vector(c)
                   for c in wall.bound_box]
        xs = [c.x for c in corners]
        ys = [c.y for c in corners]
        bounds.append((min(xs), max(xs), min(ys), max(ys)))
    return bounds


def _near_wall(point_xy, wall_bounds, tolerance=0.05):
    for x0, x1, y0, y1 in wall_bounds:
        if (x0 - tolerance <= point_xy.x <= x1 + tolerance
                and y0 - tolerance <= point_xy.y <= y1 + tolerance):
            return True
    return False


def _frameless_end_finished(obj, side, wall_bounds):
    """Frameless has no per-end exposure props: an end reads finished
    (molding wraps it) when it is NOT against a wall."""
    width, depth, _ = engine.cage_dims(obj)
    mw = obj.matrix_world
    x = 0.0 if side == 'left' else width
    mid = mw @ mathutils.Vector((x, -depth / 2.0, 0.0))
    outward3 = mw.to_3x3() @ mathutils.Vector(
        (-1.0 if side == 'left' else 1.0, 0.0, 0.0))
    outward = mathutils.Vector((outward3.x, outward3.y))
    if outward.length > 1e-6:
        outward.normalize()
    probe = mathutils.Vector((mid.x, mid.y)) + outward * 0.03
    return not _near_wall(probe, wall_bounds)


def finish_material(obj):
    """The exterior finish material of the cabinet's assigned style,
    resolved through its library's style system. None for appliances
    or when no style / material resolves."""
    try:
        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            style_name = obj.get('STYLE_NAME')
            if not style_name:
                return None
            from ..product_libraries.face_frame import props_hb_face_frame
            ff = props_hb_face_frame.get_style_props()
            style = next((cs for cs in ff.cabinet_styles
                          if cs.name == style_name), None)
            if style is None:
                return None
            material, _rotated = style.get_finish_material()
            return material
        if (obj.get('IS_FRAMELESS_CABINET_CAGE')
                or obj.get('IS_FRAMELESS_PRODUCT_CAGE')):
            from .. import hb_project
            main = hb_project.get_main_scene()
            props = getattr(main, 'hb_frameless', None)
            if props is None or not props.cabinet_styles:
                return None
            index = obj.get('CABINET_STYLE_INDEX', 0)
            if not 0 <= index < len(props.cabinet_styles):
                return None
            material, _rotated = \
                props.cabinet_styles[index].get_finish_material()
            return material
    except Exception:
        return None
    return None


def build_facts(scene, members):
    """FACTS dict (keyed by id(obj)) for the engine, covering every
    member: role, corner data, kick config, finished ends."""
    wall_bounds = _wall_bounds(scene)
    facts = {}
    for obj in members:
        if obj.get('IS_APPLIANCE'):
            facts[id(obj)] = {'role': 'APPLIANCE', 'corner': None,
                              'kick': {'skip': True, 'setback': 0.0},
                              'finished_left': False,
                              'finished_right': False}
            continue

        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            ffc = obj.face_frame_cabinet
            corner = None
            if getattr(ffc, 'corner_type', 'NONE') != 'NONE':
                corner = {'ld': ffc.left_depth, 'rd': ffc.right_depth,
                          'diagonal': ffc.corner_type == 'DIAGONAL'}
            if obj.get('CLASS_NAME') == 'RefrigeratorCabinet':
                # The end stiles run to the floor and carry molding
                # like legs; the opening between them (where the
                # refrigerator sits) has no kick face behind it, so it
                # is skipped outright - never a RECESS to opt into.
                # Returns die into the stile edges (one frame
                # thickness) instead of running back to a kick line.
                kick = {
                    'skip': False,
                    'setback': getattr(ffc, 'face_frame_thickness',
                                       0.0) or units.inch(0.75),
                    'middle_skip': True,
                    'stile_left': True,
                    'stile_right': True,
                    'stile_left_w': ffc.left_stile_width,
                    'stile_right_w': ffc.right_stile_width,
                }
            elif obj.get('IS_LEG_PRODUCT'):
                # Leg products: the leg's foot stays bare - base
                # molding runs INSIDE the toe kick, across the leg at
                # the setback line (at the front for columns /
                # stile-only legs, which have no kick). Finished sides
                # wrap from the setback line to the rear via the
                # finished-end treatment.
                leg = getattr(obj, 'leg_product', None)
                has_kick = (leg is not None and not leg.is_column
                            and not leg.only_stile
                            and leg.toe_kick_height > 0.0)
                kick = {
                    'skip': False,
                    'leg': True,
                    'setback': leg.toe_kick_setback if has_kick else 0.0,
                }
            elif ffc.toe_kick_type not in _RECESSED_FF_KICKS:
                kick = {'skip': False, 'setback': 0.0}
            else:
                kick = {
                    'skip': False,
                    'setback': _measured_kick_setback(obj, ffc),
                    'stile_left': ffc.extend_left_stile_to_floor,
                    'stile_right': ffc.extend_right_stile_to_floor,
                    'stile_left_w': ffc.left_stile_width,
                    'stile_right_w': ffc.right_stile_width,
                }
                flush = _floor_flush_spans(obj)
                if flush:
                    kick['flush_spans'] = flush
            fin_l = getattr(ffc, 'left_finished_end_condition',
                            'UNFINISHED') not in ('UNFINISHED', '', None)
            fin_r = getattr(ffc, 'right_finished_end_condition',
                            'UNFINISHED') not in ('UNFINISHED', '', None)
            if obj.get('IS_LEG_PRODUCT'):
                # Legs carry their exposure on leg_product.finish_type,
                # not the generic finished-end conditions: a finished
                # side gets the molding wrapped around it to the rear
                # (INTERMEDIATE legs sit between cabinets - no wrap).
                ft = getattr(getattr(obj, 'leg_product', None),
                             'finish_type', '')
                fin_l = fin_l or ft in ('FINISH_LEFT', 'FINISH_BOTH')
                fin_r = fin_r or ft in ('FINISH_RIGHT', 'FINISH_BOTH')
            # Crown mounting datum: the DOOR TOP (face-frame opening top
            # plus the door's top overlay). The room's crown reveal is
            # measured up from here, matching the crown detail drawing.
            crown_mount = None
            rail = _top_rail_width(obj)
            if rail:
                overlay = max(
                    getattr(ffc, 'default_top_overlay', 0.0) or 0.0, 0.0)
                crown_mount = {'rail_width': rail, 'door_overlay': overlay}
            facts[id(obj)] = {'role': 'CABINET', 'corner': corner,
                              'kick': kick,
                              'crown_mount': crown_mount,
                              'back_off': _finished_back_offset(obj),
                              'finished_left': fin_l,
                              'finished_right': fin_r}
            if ffc.cabinet_type == 'UPPER':
                skips = _rail_skip_spans(obj)
                if skips:
                    facts[id(obj)]['rail_skips'] = skips
                    facts[id(obj)]['rail_bays'] = _rail_bays(obj)
            continue

        # Frameless (cabinet or product cage).
        corner = None
        if obj.get('IS_CORNER_CABINET'):
            corner = {'ld': obj.get('Left Depth'),
                      'rd': obj.get('Right Depth'),
                      'diagonal': obj.get('CORNER_TYPE') == 'DIAGONAL'}
        setback = obj.get('Toe Kick Setback', 0.0) or 0.0
        kick = {'skip': False, 'setback': setback}
        facts[id(obj)] = {
            'role': 'CABINET', 'corner': corner, 'kick': kick,
            'back_off': _finished_back_offset(obj),
            'finished_left': _frameless_end_finished(obj, 'left',
                                                     wall_bounds),
            'finished_right': _frameless_end_finished(obj, 'right',
                                                      wall_bounds),
        }
    return facts
