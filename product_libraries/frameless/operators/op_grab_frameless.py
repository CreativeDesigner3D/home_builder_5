"""Grab for frameless cabinets: drag cabinet ends and opening dividers.

The frameless counterpart of the face frame library's Grab, for the
Cabinets selection mode. Every cabinet gets a handle on each end. Where
two cabinets stand butted on one run the two coinciding end handles fold
into one joint: dragging it widens one cabinet and narrows the other by
the same amount, so the run keeps its overall length. A free end
stretches its own cabinet and stops at the next cabinet or appliance on
the run. A left end keeps the cabinet's right side where it is.

Like the face frame Grab it is a mode you leave switched on: it only
claims a left click that lands on a handle, so selecting, right-click
menus and navigation keep working. Each drag is its own undo step.
While dragging, type a width (inches, fractions, feet'inches") for the
cabinet left of the handle; Shift turns the 1/8" snap off; Esc or
right-click drops the drag; Enter or Esc with no drag ends the mode.

In the Bays selection mode it offers the same end and joint handles
(a frameless cabinet is one bay, so its bay width follows the cabinet).
In the Openings mode every divider between two split openings is a
handle: dragging it makes one opening bigger and its neighbor smaller
by the same amount, so the rest of the split keeps its sizes. A typed
value sets the opening above (or left of) the divider.
"""

import math
import traceback

import bpy
import blf
import gpu
from bpy.app.handlers import persistent
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .... import hb_icons
from .... import hb_types
from .... import hb_utils
from ....units import inch


TAG_CABINET = 'IS_FRAMELESS_CABINET_CAGE'
# A wall scribe filler is grabbed like a cabinet: ends, a joint with
# the cabinet it stands against, its top and bottom, and a move handle.
TAG_FILLER = 'IS_CORNER_FILLER'

HIT_TOLERANCE_PX = 12.0
MIN_WIDTH = inch(3.0)
FILLER_MIN_WIDTH = inch(0.5)
SNAP_STEP = inch(0.125)
# Two ends this close are butted: one joint instead of two end handles.
BUTT_TOL = inch(0.0625)
# Cabinets whose backs sit this close along the run's depth axis share
# a run -- the ones an end stops at and a joint pairs with.
RUN_PLANE_TOL = inch(4.0)
# A moved cabinet's end snaps to another end inside this many pixels.
MOVE_SNAP_PX = 14.0
# Radius of the move handle at a cabinet's centre (unscaled px).
MOVE_HANDLE_R = 13.0
MOVE_CHIP = (0.13, 0.13, 0.14, 0.85)

GHOST_LINE = (0.85, 0.85, 0.85, 0.35)
JOINT_LINE = (0.85, 0.85, 0.85, 0.60)
HOVER_LINE = (1.00, 0.85, 0.20, 1.00)
ACTIVE_LINE = (1.00, 0.65, 0.10, 1.00)
DIM_TEXT = (1.00, 1.00, 1.00, 1.00)
ACTIVE_DIM_TEXT = (0.40, 0.90, 1.00, 1.00)
LABEL_BG = (0.13, 0.13, 0.14, 0.85)
LABEL_BORDER = (1.0, 1.0, 1.0, 0.25)


def _ui_scale():
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


GRAB_MODES = ('Cabinets', 'Bays', 'Openings')
MIN_OPENING = inch(2.0)
MIN_HEIGHT = inch(6.0)
# A cabinet whose bottom sits this far off the floor hangs on the wall:
# it gets a bottom handle as well as a top one.
HUNG_MIN_Z = inch(1.0)
HEIGHT_KINDS = ('TOP', 'BOTTOM')


def grab_mode_active(scene):
    """The frameless selection mode when Grab works in it, else None."""
    fl = getattr(scene, 'hb_frameless', None)
    mode = getattr(fl, 'frameless_selection_mode', '')
    return mode if mode in GRAB_MODES else None


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def _dims(obj):
    geo = hb_types.GeoNodeObject(obj)
    return (geo.get_input('Dim X'), geo.get_input('Dim Y'),
            geo.get_input('Dim Z'))


def _min_width(obj):
    """The narrowest a drag leaves this cabinet or filler."""
    if obj is not None and obj.get(TAG_FILLER):
        return FILLER_MIN_WIDTH
    return MIN_WIDTH


def _fills_gap(obj):
    """A wall scribe filler: its width is the gap it closes, so it is
    resized from the cabinet beside it rather than from its own far
    end."""
    try:
        from .. import scribe_fit
        return bool(scribe_fit.is_wall_scribe_filler(obj))
    except Exception:
        return False


def _grabbed(obj):
    """A product Grab puts handles on: a cabinet or a wall scribe
    filler."""
    return bool(obj.get(TAG_CABINET) or obj.get(TAG_FILLER))


def _entry(obj, appliance=False):
    try:
        dim_x, dim_y, dim_z = _dims(obj)
    except Exception:
        return None
    if not dim_x:
        return None
    mw = obj.matrix_world
    rot = mw.to_3x3()
    return {
        'name': obj.name,
        'origin': mw.translation.copy(),
        'x': (rot @ Vector((1.0, 0.0, 0.0))).normalized(),
        'y': (rot @ Vector((0.0, 1.0, 0.0))).normalized(),
        'dim_x': dim_x,
        'dim_y': dim_y,
        'dim_z': dim_z,
        'z_low': mw.translation.z,
        'z_high': mw.translation.z + dim_z,
        'appliance': appliance,
        'gap_filler': _fills_gap(obj),
    }


def _run_entries(scene):
    """Frameless cabinets and wall scribe fillers, plus the
    freestanding appliances that stand in a run: an end stops against
    an appliance and snaps to its sides, but it never joins a joint."""
    out = []
    for obj in scene.objects:
        if _grabbed(obj):
            if not obj.visible_get():
                continue
            e = _entry(obj)
        elif (obj.get('IS_APPLIANCE') and obj.get('APPLIANCE_TYPE')
                and not obj.get('IS_COUNTERTOP_APPLIANCE')):
            if not obj.visible_get():
                continue
            e = _entry(obj, appliance=True)
        else:
            continue
        if e is not None:
            out.append(e)
    return out


def _same_run(a, b):
    if a['x'].dot(b['x']) < 0.999:
        return False
    if abs((b['origin'] - a['origin']).dot(a['y'])) >= RUN_PLANE_TOL:
        return False
    return min(a['z_high'], b['z_high']) - max(a['z_low'], b['z_low']) > inch(1.0)


def _span_in(a, b):
    """b's (left, right) along a's X, measured from a's origin."""
    p = (b['origin'] - a['origin']).dot(a['x'])
    return p, p + b['dim_x']


def _neighbors(entries, a):
    return [(b,) + _span_in(a, b) for b in entries
            if b is not a and _same_run(a, b)]


def _free_end_room(entries, a, side):
    """How far a's free end can travel outward before it meets the next
    thing on the run, or None when nothing is in the way."""
    gaps = []
    for _b, left, right in _neighbors(entries, a):
        if side == 'RIGHT' and left >= a['dim_x'] - BUTT_TOL:
            gaps.append(left - a['dim_x'])
        elif side == 'LEFT' and right <= BUTT_TOL:
            gaps.append(-right)
    return max(0.0, min(gaps)) if gaps else None


def collect_handles(scene, mode='Cabinets'):
    """Handle records for a selection mode: opening dividers in Openings
    mode, cabinet ends and joints otherwise (no move handle in Bays)."""
    if mode == 'Openings':
        return collect_split_handles(scene)
    handles = collect_cabinet_handles(scene)
    if mode == 'Bays':
        handles = [h for h in handles if h['kind'] != 'MOVE']
    return handles


def collect_cabinet_handles(scene):
    """Handle records for every frameless cabinet in the scene.

    kind 'JOINT' (left, right): the shared end of two butted cabinets.
    kind 'END_RIGHT' / 'END_LEFT' (cab): a free end, with 'room' -- how
    far it may grow outward (None = unlimited). A wall scribe filler
    beside a cabinet has none: it is sized at the joint.
    kind 'MOVE' (cab): the handle at the cabinet's centre that slides
    the whole cabinet along its run.
    kind 'TOP' (cab): the top edge; dragging it sets the height and the
    bottom stays. kind 'BOTTOM' (cab), on a cabinet hung off the floor:
    the bottom edge; dragging it sets the height and the top stays.
    These two lie across the front at height 'z' (from the origin).
    Every record carries the frame it is drawn and dragged in: the
    owning cabinet's origin / x / front offset and its z span."""
    entries = _run_entries(scene)
    folded = set()
    # Names with a joint: a wall scribe filler beside a cabinet is
    # sized at that joint, and its end at the wall is left to the gap.
    jointed = set()
    handles = []
    for a in entries:
        if a['appliance']:
            continue
        for b, left, _right in _neighbors(entries, a):
            if b['appliance'] or abs(left - a['dim_x']) > BUTT_TOL:
                continue
            folded.add((a['name'], 'RIGHT'))
            folded.add((b['name'], 'LEFT'))
            jointed.update((a['name'], b['name']))
            handles.append({
                'kind': 'JOINT', 'left': a['name'], 'right': b['name'],
                'frame': a, 'pos': a['dim_x'],
                'z_low': max(a['z_low'], b['z_low']) - a['z_low'],
                'z_high': min(a['z_high'], b['z_high']) - a['z_low'],
            })
    for a in entries:
        if a['appliance']:
            continue
        for side, pos in (('LEFT', 0.0), ('RIGHT', a['dim_x'])):
            if (a['name'], side) in folded:
                continue
            if a['gap_filler'] and a['name'] in jointed:
                continue
            handles.append({
                'kind': 'END_' + side, 'cab': a['name'], 'frame': a,
                'pos': pos, 'z_low': 0.0, 'z_high': a['dim_z'],
                'room': _free_end_room(entries, a, side),
            })
        handles.append({
            'kind': 'MOVE', 'cab': a['name'], 'frame': a,
            'pos': a['dim_x'] / 2.0,
            'z_low': a['dim_z'] / 2.0, 'z_high': a['dim_z'] / 2.0,
        })
        handles.append({'kind': 'TOP', 'cab': a['name'], 'frame': a,
                        'pos': 0.0, 'z': a['dim_z']})
        if a['z_low'] > HUNG_MIN_Z:
            handles.append({'kind': 'BOTTOM', 'cab': a['name'], 'frame': a,
                            'pos': 0.0, 'z': 0.0})
    return handles


def move_group(scene, name):
    """The cabinets a move handle slides together: just its own cabinet,
    or, when that cabinet is selected, every selected frameless cabinet
    facing the same way on the same wall plane (bases and uppers alike).
    The dragged cabinet comes first."""
    cab = bpy.data.objects.get(name)
    if cab is None:
        return [name]
    try:
        if not cab.select_get():
            return [name]
    except Exception:
        return [name]
    a = _entry(cab)
    if a is None:
        return [name]
    out = [name]
    for obj in scene.objects:
        if obj is cab or not _grabbed(obj) or not obj.visible_get():
            continue
        try:
            if not obj.select_get():
                continue
        except Exception:
            continue
        b = _entry(obj)
        if b is None or a['x'].dot(b['x']) < 0.999:
            continue
        if abs((b['origin'] - a['origin']).dot(a['y'])) >= RUN_PLANE_TOL:
            continue
        out.append(obj.name)
    return out


def move_targets(scene, name, group=None):
    """Run positions (along the cabinet's X, from its origin) a moved
    cabinet's ends snap to: the ends of every other cabinet or appliance
    on its run, base or wall, and its wall's ends and the sides of the
    doors and windows in its way. Cabinets in `group` move along and
    are not targets."""
    entries = _run_entries(scene)
    a = next((e for e in entries if e['name'] == name), None)
    if a is None:
        return []
    skip = set(group or ())
    out = []
    for b in entries:
        if b is a or b['name'] in skip or a['x'].dot(b['x']) < 0.999:
            continue
        if abs((b['origin'] - a['origin']).dot(a['y'])) >= RUN_PLANE_TOL:
            continue
        out.extend(_span_in(a, b))
    try:
        from ...face_frame.operators.op_modify_cabinet import wall_targets
        out.extend(wall_targets(dict(a, obj=bpy.data.objects[name])))
    except Exception:
        pass
    return out


def apply_move(name, start, d):
    """Put the cabinet (and the rest of its move group) d along the run
    from where the move started."""
    group = start.get('group') or {name: start['world']}
    for member, origin in group.items():
        cab = bpy.data.objects.get(member)
        if cab is None:
            continue
        world = origin + start['x'] * d
        if cab.parent is not None:
            cab.location = cab.parent.matrix_world.inverted_safe() @ world
        else:
            cab.location = world


def _front_point(frame, pos, z):
    """World point on a cabinet's front plane (the root cage is built
    with Mirror Y, so its front is at local y = -depth)."""
    return (frame['origin'] + frame['x'] * pos
            - frame['y'] * frame['dim_y'] + Vector((0.0, 0.0, z)))


# ---------------------------------------------------------------------------
# Opening dividers (Openings mode)
# ---------------------------------------------------------------------------

def _overlay():
    from .. import dim_edit_overlay
    return dim_edit_overlay


def _solver():
    from .. import solver_frameless
    return solver_frameless


def _split_openings(splitter):
    """{index: opening cage} for a splitter's own openings (1 is the
    top of a vertical split, the left of a horizontal one)."""
    sf = _solver()
    out = {}
    for ch in splitter.children:
        if ch.get(sf.PART_ROLE_KEY) == 'OPENING':
            idx = ch.get(sf.SPLIT_INDEX_KEY)
            if idx is not None:
                out[int(idx)] = ch
    return out


def _split_prompts(splitter, vertical):
    """(calculator, {index: size prompt}) for a splitter."""
    calc = _solver().splitter_calculator(splitter)
    if calc is None:
        return None, {}
    suffix = 'Height' if vertical else 'Width'
    out = {}
    for i in _split_openings(splitter):
        p = calc.get_calculator_prompt('Opening %d %s' % (i, suffix))
        if p is not None:
            out[i] = p
    return calc, out


def _divider_handle(splitter, vertical, i, a, b):
    """Handle for the divider between opening i (above / left) and
    opening i + 1 (below / right), drawn on the openings' front plane.
    'axis' is the drag direction: up for a vertical split, right for a
    horizontal one."""
    ov = _overlay()
    adx, _ady, adz = ov._cage_dims(a)
    bdx, _bdy, bdz = ov._cage_dims(b)
    if min(adx, adz, bdx, bdz) <= 0.0:
        return None
    amw, bmw = ov._world_matrix(a), ov._world_matrix(b)
    rot = amw.to_3x3()
    ax = (rot @ Vector((1.0, 0.0, 0.0))).normalized()
    ay = (rot @ Vector((0.0, 1.0, 0.0))).normalized()
    az = (rot @ Vector((0.0, 0.0, 1.0))).normalized()
    if vertical:
        mid = (amw @ Vector((0.0, -0.003, 0.0))
               + bmw @ Vector((0.0, -0.003, bdz))) / 2.0
        p_a, p_b, axis = mid, mid + ax * adx, az
    else:
        mid = (amw @ Vector((adx, -0.003, 0.0))
               + bmw @ Vector((0.0, -0.003, 0.0))) / 2.0
        p_a, p_b, axis = mid, mid + az * adz, ax
    return {
        'kind': 'SPLIT', 'splitter': splitter.name, 'vertical': vertical,
        'index': i, 'openings': (a.name, b.name), 'frame': None,
        'pos': 0.0, 'p_a': p_a, 'p_b': p_b, 'axis': axis, 'normal': ay,
        'plane_p': p_a.copy(),
    }


def collect_split_handles(scene):
    """A 'SPLIT' handle on every divider between two split openings of
    every shown, editable frameless cabinet."""
    ov, sf = _overlay(), _solver()
    handles = []
    for cab in scene.objects:
        if not cab.get(TAG_CABINET):
            continue
        try:
            if not ov._cabinet_shown(cab) or not ov._cabinet_editable(cab):
                continue
        except Exception:
            continue
        for splitter in cab.children_recursive:
            if splitter.get(sf.SPLITTER_VERTICAL_TAG):
                vertical = True
            elif splitter.get(sf.SPLITTER_HORIZONTAL_TAG):
                vertical = False
            else:
                continue
            _calc, prompts = _split_prompts(splitter, vertical)
            openings = _split_openings(splitter)
            for i in sorted(openings):
                if (i + 1 not in openings or i not in prompts
                        or i + 1 not in prompts):
                    continue
                h = _divider_handle(splitter, vertical, i, openings[i],
                                    openings[i + 1])
                if h is not None:
                    handles.append(h)
    return handles


def _split_start(handle):
    splitter = bpy.data.objects[handle['splitter']]
    _calc, prompts = _split_prompts(splitter, handle['vertical'])
    i = handle['index']
    return {
        'a': prompts[i].distance_value, 'b': prompts[i + 1].distance_value,
        'snapshot': {k: (p.equal, p.distance_value)
                     for k, p in prompts.items()},
    }


def _resolve_split(context, splitter, calc):
    """Same sequence as a typed opening size: recompute the calculator,
    then re-solve the cabinet."""
    try:
        calc.calculate()
    except Exception:
        pass
    cabinet_bp = hb_utils.get_cabinet_bp(splitter)
    if cabinet_bp is not None:
        hb_utils.run_calc_fix(context, cabinet_bp)


def _split_sizes(handle, start, d):
    """(opening above / left, opening below / right) after the divider
    moved d along its axis (up / right)."""
    if handle['vertical']:
        return start['a'] - d, start['b'] + d
    return start['a'] + d, start['b'] - d


def _apply_split(context, handle, start, d):
    # In terms of the change to opening a, clamped so both openings
    # stay at least MIN_OPENING.
    sign = -1.0 if handle['vertical'] else 1.0
    da = min(max(sign * d, MIN_OPENING - start['a']),
             start['b'] - MIN_OPENING)
    d = sign * da
    splitter = bpy.data.objects[handle['splitter']]
    calc, prompts = _split_prompts(splitter, handle['vertical'])
    i = handle['index']
    size_a, size_b = _split_sizes(handle, start, d)
    pa, pb = prompts[i], prompts[i + 1]
    others_equal = any(p.equal and p.include for k, p in prompts.items()
                       if k not in (i, i + 1))
    # Normally both are held, so the openings still sharing equally keep
    # the same remainder. When nothing else shares, one of the two that
    # was sharing stays equal (b first) so the split still follows the
    # cabinet if it is resized later; it takes exactly its new size.
    spare = None
    if not others_equal:
        if start['snapshot'][i + 1][0]:
            spare = pb
        elif start['snapshot'][i][0]:
            spare = pa
    for p, size in ((pa, size_a), (pb, size_b)):
        if p is spare:
            p.equal = True
        else:
            p.equal = False
            p.distance_value = size
    _resolve_split(context, splitter, calc)
    return d


def _restore_split(context, handle, start):
    splitter = bpy.data.objects[handle['splitter']]
    calc, prompts = _split_prompts(splitter, handle['vertical'])
    for k, (equal, value) in start['snapshot'].items():
        if k in prompts:
            prompts[k].equal = equal
            prompts[k].distance_value = value
    _resolve_split(context, splitter, calc)


# ---------------------------------------------------------------------------
# Edits
# ---------------------------------------------------------------------------

def _set_width(context, obj, width):
    # The same input + re-solve a typed Cabinet Width edit makes.
    hb_types.GeoNodeCage(obj).set_input('Dim X', width)
    hb_utils.run_calc_fix(context, obj)


def _shift_along_own_x(obj, distance):
    """Move obj by distance along its own X, in its parent's space."""
    axis = obj.matrix_basis.to_3x3() @ Vector((1.0, 0.0, 0.0))
    obj.location = obj.location + axis.normalized() * distance


def _set_height(context, obj, height):
    # The same input + re-solve a typed Cabinet Height edit makes.
    hb_types.GeoNodeCage(obj).set_input('Dim Z', height)
    hb_utils.run_calc_fix(context, obj)


def _clamp_delta(handle, start, d):
    """Clamp the drag distance so no cabinet goes under MIN_WIDTH and a
    free end stops where the next cabinet starts. A height drag keeps
    MIN_HEIGHT, and a bottom stops at the floor."""
    kind = handle['kind']
    if kind == 'TOP':
        return max(d, MIN_HEIGHT - start['h'])
    if kind == 'BOTTOM':
        return min(max(d, -start['z_world']), start['h'] - MIN_HEIGHT)
    if kind == 'JOINT':
        lo = start.get('left_min', MIN_WIDTH) - start['left_w']
        hi = start['right_w'] - start.get('right_min', MIN_WIDTH)
    elif kind == 'END_RIGHT':
        lo = start.get('min_w', MIN_WIDTH) - start['w']
        room = handle.get('room')
        hi = room if room is not None else math.inf
    else:  # END_LEFT: dragging right narrows
        room = handle.get('room')
        lo = -room if room is not None else -math.inf
        hi = start['w'] - start.get('min_w', MIN_WIDTH)
    return min(max(d, lo), hi)


def primary_width(handle, start, d):
    """The width the drag is setting: the cabinet left of a joint or a
    right end, the cabinet itself for a left end, the opening above or
    left of a divider."""
    if handle['kind'] == 'SPLIT':
        return _split_sizes(handle, start, d)[0]
    if handle['kind'] == 'TOP':
        return start['h'] + d
    if handle['kind'] == 'BOTTOM':
        return start['h'] - d
    if handle['kind'] == 'JOINT':
        return start['left_w'] + d
    if handle['kind'] == 'END_RIGHT':
        return start['w'] + d
    return start['w'] - d


def delta_for_width(handle, start, width):
    if handle['kind'] == 'SPLIT':
        change = width - start['a']
        return -change if handle['vertical'] else change
    if handle['kind'] == 'TOP':
        return width - start['h']
    if handle['kind'] == 'BOTTOM':
        return start['h'] - width
    if handle['kind'] == 'JOINT':
        return width - start['left_w']
    if handle['kind'] == 'END_RIGHT':
        return width - start['w']
    return start['w'] - width


def start_state(handle):
    if handle['kind'] == 'SPLIT':
        return _split_start(handle)
    if handle['kind'] == 'MOVE':
        cab = bpy.data.objects[handle['cab']]
        world = cab.matrix_world.translation.copy()
        x = handle['frame']['x'].copy()
        w = handle['frame']['dim_x']
        group, lo, hi = {}, 0.0, w
        for member in move_group(bpy.context.scene, cab.name):
            obj = bpy.data.objects[member]
            o = obj.matrix_world.translation.copy()
            group[member] = o
            if member != cab.name:
                p = (o - world).dot(x)
                lo = min(lo, p)
                hi = max(hi, p + _dims(obj)[0])
        return {'world': world, 'x': x, 'w': w,
                'group': group, 'span': (lo, hi)}
    if handle['kind'] == 'JOINT':
        left = bpy.data.objects[handle['left']]
        right = bpy.data.objects[handle['right']]
        return {'left_w': _dims(left)[0], 'right_w': _dims(right)[0],
                'left_min': _min_width(left), 'right_min': _min_width(right),
                'right_loc': right.location.copy()}
    cab = bpy.data.objects[handle['cab']]
    w, _dy, h = _dims(cab)
    return {'w': w, 'h': h, 'min_w': _min_width(cab),
            'loc': cab.location.copy(),
            'world': cab.matrix_world.translation.copy(),
            'z_world': cab.matrix_world.translation.z}


def apply_delta(context, handle, start, d):
    """Set the cabinets a handle owns to the start state moved by d
    (along the run, or up for a top / bottom handle). Returns the
    clamped d actually applied."""
    if handle['kind'] == 'SPLIT':
        return _apply_split(context, handle, start, d)
    d = _clamp_delta(handle, start, d)
    if handle['kind'] == 'TOP':
        _set_height(context, bpy.data.objects[handle['cab']], start['h'] + d)
    elif handle['kind'] == 'BOTTOM':
        cab = bpy.data.objects[handle['cab']]
        world = start['world'] + Vector((0.0, 0.0, d))
        if cab.parent is not None:
            cab.location = cab.parent.matrix_world.inverted_safe() @ world
        else:
            cab.location = world
        _set_height(context, cab, start['h'] - d)
    elif handle['kind'] == 'JOINT':
        left = bpy.data.objects[handle['left']]
        right = bpy.data.objects[handle['right']]
        _set_width(context, left, start['left_w'] + d)
        right.location = start['right_loc']
        _shift_along_own_x(right, d)
        _set_width(context, right, start['right_w'] - d)
    elif handle['kind'] == 'END_RIGHT':
        _set_width(context, bpy.data.objects[handle['cab']], start['w'] + d)
    else:
        cab = bpy.data.objects[handle['cab']]
        cab.location = start['loc']
        _shift_along_own_x(cab, d)
        _set_width(context, cab, start['w'] - d)
    return d


def restore(context, handle, start):
    if handle['kind'] == 'SPLIT':
        _restore_split(context, handle, start)
    elif handle['kind'] == 'MOVE':
        apply_move(handle['cab'], start, 0.0)
    else:
        apply_delta(context, handle, start, 0.0)


def resize_in_run(context, obj, width):
    """Set a cabinet's width the way Grab would: a butted neighbor takes
    up the change (the right one first, then the left), so the run keeps
    its length. A free end stretches only into open space. Whatever the
    neighbors and open space can't absorb is applied to the right end
    on its own, as a plain width edit always was. Returns True."""
    change = width - _dims(obj)[0]
    # Right side first, then the left. The run is re-read between the two,
    # since the first step moves things. sign: the drag on that handle
    # that grows obj.
    for side_keys, sign in (((('JOINT', 'left'), ('END_RIGHT', 'cab')), 1.0),
                            ((('JOINT', 'right'), ('END_LEFT', 'cab')), -1.0)):
        if abs(change) < 1e-6:
            break
        handles = collect_cabinet_handles(context.scene)
        h = next((h for kind, key in side_keys for h in handles
                  if h['kind'] == kind and h.get(key) == obj.name), None)
        if h is None:
            continue
        d = apply_delta(context, h, start_state(h), change * sign)
        change -= d * sign
    if abs(change) > 1e-6:
        _set_width(context, obj, _dims(obj)[0] + change)
    return True


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _to_screen(region, rv3d, p):
    return view3d_utils.location_3d_to_region_2d(region, rv3d, p)


def _handle_segment(region, rv3d, h, frame=None):
    if h['kind'] == 'SPLIT':
        off = h['axis'] * h['pos']
        return (_to_screen(region, rv3d, h['p_a'] + off),
                _to_screen(region, rv3d, h['p_b'] + off))
    frame = frame or h['frame']
    if h['kind'] in HEIGHT_KINDS:
        # Across the front at its height; a drag shifts it by 'pos'.
        z = h['z'] + h['pos']
        return (_to_screen(region, rv3d, _front_point(frame, 0.0, z)),
                _to_screen(region, rv3d,
                           _front_point(frame, frame['dim_x'], z)))
    p1 = _to_screen(region, rv3d, _front_point(frame, h['pos'], h['z_low']))
    p2 = _to_screen(region, rv3d, _front_point(frame, h['pos'], h['z_high']))
    return p1, p2


def _seg_distance(p, a, b):
    ab = b - a
    denom = ab.length_squared
    t = 0.0 if denom == 0.0 else max(0.0, min(1.0, (p - a).dot(ab) / denom))
    return (p - (a + ab * t)).length


def _draw_line(shader, p1, p2, color, width):
    if p1 is None or p2 is None:
        return
    gpu.state.line_width_set(width)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES',
                     {"pos": [(p1.x, p1.y), (p2.x, p2.y)]}).draw(shader)


def _draw_label(x, y, text, color):
    s = _ui_scale()
    blf.size(0, 12 * s)
    w, h = blf.dimensions(0, text)
    hw, hh = w / 2 + 6 * s, h / 2 + 4 * s
    verts = ((x - hw, y - hh), (x + hw, y - hh),
             (x + hw, y + hh), (x - hw, y + hh))
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("color", LABEL_BG)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)
    blf.color(0, *color)
    blf.position(0, x - w / 2, y - h / 2, 0)
    blf.draw(0, text)


def format_inches(meters):
    inches = meters / 0.0254
    whole = int(inches)
    sixteenths = round((inches - whole) * 16)
    if sixteenths == 16:
        whole, sixteenths = whole + 1, 0
    if sixteenths == 0:
        return f'{whole}"'
    g = math.gcd(sixteenths, 16)
    return f'{whole} {sixteenths // g}/{16 // g}"'


def _width_label(region, rv3d, name, color):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return
    e = _entry(obj)
    if e is None:
        return
    p = _to_screen(region, rv3d,
                   _front_point(e, e['dim_x'] / 2.0, e['dim_z'] / 2.0))
    if p is not None:
        _draw_label(p.x, p.y, format_inches(e['dim_x']), color)


def _height_label(region, rv3d, name, color):
    """The cabinet's height, and its bottom off the floor when it hangs,
    at its centre while a top or bottom edge drags."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return
    e = _entry(obj)
    if e is None:
        return
    p = _to_screen(region, rv3d,
                   _front_point(e, e['dim_x'] / 2.0, e['dim_z'] / 2.0))
    if p is None:
        return
    text = "H " + format_inches(e['dim_z'])
    if e['z_low'] > HUNG_MIN_Z:
        text += "  |  off floor " + format_inches(e['z_low'])
    _draw_label(p.x, p.y, text, color)


def _draw_move_handle(shader, region, rv3d, h, frame, hot, s):
    """The move icon on a chip at the cabinet's centre, lit while
    hovered or dragged -- the face frame Grab's move handle."""
    c = _to_screen(region, rv3d,
                   _front_point(frame, h['pos'], h['z_low']))
    if c is None:
        return
    r = MOVE_HANDLE_R * s
    chip = ((ACTIVE_LINE[0], ACTIVE_LINE[1], ACTIVE_LINE[2], 0.95)
            if hot else MOVE_CHIP)
    pts = [(c.x, c.y)] + [(c.x + r * math.cos(2.0 * math.pi * i / 24),
                           c.y + r * math.sin(2.0 * math.pi * i / 24))
                          for i in range(25)]
    shader.uniform_float("color", chip)
    batch_for_shader(shader, 'TRI_FAN', {"pos": pts}).draw(shader)
    color = (0.08, 0.08, 0.09, 1.0) if hot else (1.0, 1.0, 1.0, 0.92)
    px = r * 1.5
    drawn = hb_icons.draw_icon('move', (c.x - px / 2.0, c.y - px / 2.0,
                                        px, px), color, size=16)
    shader.bind()
    if not drawn:
        _draw_line(shader, Vector((c.x - r * 0.6, c.y)),
                   Vector((c.x + r * 0.6, c.y)), color, 2.0 * s)


def _split_labels(region, rv3d, h):
    """The two openings' sizes at their centres while a divider drags."""
    splitter = bpy.data.objects.get(h['splitter'])
    if splitter is None:
        return
    ov = _overlay()
    _calc, prompts = _split_prompts(splitter, h['vertical'])
    for n, (name, idx) in enumerate(zip(h['openings'],
                                        (h['index'], h['index'] + 1))):
        cage = bpy.data.objects.get(name)
        if cage is None or idx not in prompts:
            continue
        anchor = ov._anchor_world(cage, 0.5, 0.5)
        p = _to_screen(region, rv3d, anchor) if anchor is not None else None
        if p is not None:
            _draw_label(p.x, p.y, format_inches(prompts[idx].distance_value),
                        ACTIVE_DIM_TEXT if n == 0 else DIM_TEXT)


def _involves(h, name):
    return name in (h.get('cab'), h.get('left'), h.get('right'))


def _draw_callback(op, context):
    try:
        _draw(op, context)
    except Exception:
        traceback.print_exc()


def _draw(op, context):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None or not op._handles:
        return
    s = _ui_scale()
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    gpu.state.blend_set('ALPHA')
    moving = (op._drag['cab'] if op._drag is not None
              and op._drag['kind'] == 'MOVE' else None)
    for h in op._handles:
        if h is op._drag or h is op._hover or h['kind'] == 'MOVE':
            continue
        if moving is not None and _involves(h, moving):
            continue      # its ends are travelling with the drag
        p1, p2 = _handle_segment(region, rv3d, h)
        joint = h['kind'] in ('JOINT', 'SPLIT')
        _draw_line(shader, p1, p2, JOINT_LINE if joint else GHOST_LINE,
                   (2.0 if joint else 1.0) * s)
    for h in op._handles:
        if h['kind'] == 'MOVE' and h is not op._drag:
            if moving is not None and h['cab'] == moving:
                continue
            _draw_move_handle(shader, region, rv3d, h, h['frame'],
                              h is op._hover, s)
    hot = op._drag or op._hover
    if hot is not None and hot['kind'] == 'MOVE':
        if op._drag is not None:
            _draw_move_handle(shader, region, rv3d,
                              dict(hot, pos=hot['pos'] + op._drag_d),
                              op._drag_frame, True, s)
    elif hot is not None:
        frame = op._drag_frame if op._drag is not None else None
        h = hot
        if frame is not None:
            # Draw the dragged handle where the end now is.
            h = dict(hot, pos=hot['pos'] + op._drag_d)
        p1, p2 = _handle_segment(region, rv3d, h, frame)
        _draw_line(shader, p1, p2,
                   ACTIVE_LINE if op._drag is not None else HOVER_LINE,
                   3.0 * s)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    if op._drag is not None and op._drag['kind'] == 'MOVE':
        h = op._drag
        c = _to_screen(region, rv3d, _front_point(
            op._drag_frame, h['pos'] + op._drag_d, h['z_low']))
        if c is not None:
            _draw_label(c.x, c.y - 28.0 * s,
                        ("\u2192 " if op._drag_d >= 0 else "\u2190 ")
                        + format_inches(abs(op._drag_d)), ACTIVE_DIM_TEXT)
    elif op._drag is not None and op._drag['kind'] == 'SPLIT':
        _split_labels(region, rv3d, op._drag)
    elif op._drag is not None and op._drag['kind'] in HEIGHT_KINDS:
        _height_label(region, rv3d, op._drag['cab'], ACTIVE_DIM_TEXT)
    elif op._drag is not None:
        h = op._drag
        names =([h['left'], h['right']] if h['kind'] == 'JOINT'
                 else [h['cab']])
        for i, name in enumerate(names):
            _width_label(region, rv3d, name,
                         ACTIVE_DIM_TEXT if i == 0 else DIM_TEXT)
    if op._drag is not None and op._typed:
        mx, my = op._mouse
        _draw_label(mx + 30 * s, my + 24 * s, op._typed + '_',
                    ACTIVE_DIM_TEXT)


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

_TYPE_CHARS = {
    'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
    'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9',
    'PERIOD': '.', 'NUMPAD_PERIOD': '.', 'SLASH': '/', 'NUMPAD_SLASH': '/',
    'SPACE': ' ', 'MINUS': '-', 'NUMPAD_MINUS': '-',
}
for _i in range(10):
    _TYPE_CHARS['NUMPAD_%d' % _i] = str(_i)


class hb_frameless_OT_grab(bpy.types.Operator):
    """Drag frameless cabinet ends to resize them. Where two cabinets
    are butted, dragging the joint between them moves width from one to
    the other"""
    bl_idname = "hb_frameless.grab"
    bl_label = "Grab"
    bl_description = (
        "Drag cabinet ends to resize them, or a top or bottom edge to "
        "change the height. Where two cabinets are butted, "
        "drag the joint to make one wider and the other narrower. In the "
        "Openings mode, drag the divider between two openings. Type a "
        "size while dragging; Shift turns snapping off. Each drag is its "
        "own undo step. Enter or Esc to finish"
    )
    # No 'UNDO': it pushes one step per drag instead.
    bl_options = {'REGISTER'}

    _handles = None
    _hover = None
    _drag = None
    _drag_frame = None
    _drag_start = None
    _drag_origin = None
    _drag_d = 0.0
    _move_targets = None
    _typed = ''
    _mouse = (0, 0)
    _draw_handle = None
    _last_mode = None

    @classmethod
    def poll(cls, context):
        return any(_grabbed(o) for o in context.scene.objects)

    # ---- lifecycle ----

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from a 3D Viewport")
            return {'CANCELLED'}
        self._last_mode = grab_mode_active(context.scene)
        self._collect(context)
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(
            "Grab  |  LMB: drag a cabinet end, top or bottom, the joint "
            "between two cabinets, or (Openings mode) a divider  |  "
            "Type: size  |  "
            "Shift: no snap  |  Enter / Esc: done")
        from ....operators.viewport_hud import register_active_modal
        register_active_modal(self)
        self._exit_requested = False
        self._exit_timer = None
        _live_grabs.add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._cleanup(context)

    def _cleanup(self, context):
        _live_grabs.discard(self)
        from ....operators.viewport_hud import unregister_active_modal
        unregister_active_modal(self)
        if self._draw_handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    self._draw_handle, 'WINDOW')
            except Exception:
                pass
            self._draw_handle = None
        timer = getattr(self, '_exit_timer', None)
        if timer is not None:
            try:
                context.window_manager.event_timer_remove(timer)
            except Exception:
                pass
            self._exit_timer = None
        try:
            if context.area is not None:
                context.area.header_text_set(None)
                context.area.tag_redraw()
        except Exception:
            pass

    def _collect(self, context):
        mode = grab_mode_active(context.scene)
        self._handles = collect_handles(context.scene, mode) if mode else []
        self._hover = None

    # ---- undo ----

    def forget_scene_refs(self):
        self._handles = []
        self._hover = None
        self._drag = None
        self._drag_frame = None
        self._typed = ''

    def refresh_after_undo(self):
        self._collect(bpy.context)

    # ---- picking / dragging ----

    def _pick(self, context, event):
        region, rv3d = context.region, context.region_data
        if region is None or rv3d is None:
            return None
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        s = _ui_scale()
        # A move disc wins over the lines inside it.
        for h in self._handles or ():
            if h['kind'] != 'MOVE':
                continue
            c = _to_screen(region, rv3d,
                           _front_point(h['frame'], h['pos'], h['z_low']))
            if c is not None and (c - mouse).length <= MOVE_HANDLE_R * s:
                return h
        best, best_d = None, HIT_TOLERANCE_PX * s
        for h in self._handles or ():
            if h['kind'] == 'MOVE':
                continue
            p1, p2 = _handle_segment(region, rv3d, h)
            if p1 is None or p2 is None:
                continue
            d = _seg_distance(mouse, p1, p2)
            if d < best_d:
                best, best_d = h, d
        return best

    def _run_param(self, context, event):
        """Where the cursor ray meets the dragged handle's front plane,
        as a distance along the run from the drag's frozen origin."""
        region, rv3d = context.region, context.region_data
        co = (event.mouse_region_x, event.mouse_region_y)
        ray_o = view3d_utils.region_2d_to_origin_3d(region, rv3d, co)
        ray_d = view3d_utils.region_2d_to_vector_3d(region, rv3d, co)
        frame = self._drag_frame
        if frame.get('kind') == 'SPLIT':
            normal, plane_p, axis = (frame['normal'], frame['plane_p'],
                                     frame['axis'])
        elif self._drag is not None and self._drag['kind'] in HEIGHT_KINDS:
            normal = frame['y']
            plane_p = _front_point(frame, 0.0, 0.0)
            axis = Vector((0.0, 0.0, 1.0))
        else:
            normal = frame['y']
            plane_p = _front_point(frame, 0.0, 0.0)
            axis = frame['x']
        denom = ray_d.dot(normal)
        if abs(denom) < 1e-6:
            # Looking along the front: fall back to the ground plane.
            normal = Vector((0.0, 0.0, 1.0))
            denom = ray_d.dot(normal)
            if abs(denom) < 1e-6:
                return None
        t = (plane_p - ray_o).dot(normal) / denom
        hit = ray_o + ray_d * t
        return (hit - plane_p).dot(axis)

    def _start_drag(self, context, event, h):
        self._drag = h
        self._drag_frame = dict(h['frame'] or h)
        self._drag_start = start_state(h)
        self._drag_d = 0.0
        self._typed = ''
        self._drag_origin = self._run_param(context, event)
        if self._drag_origin is None:
            self._drag = None
        self._move_targets = (
            move_targets(context.scene, h['cab'],
                         (self._drag_start or {}).get('group'))
            if self._drag is not None and h['kind'] == 'MOVE' else [])

    def _snap_move(self, context, d):
        """d with the nearer end flush to a target when one is within
        MOVE_SNAP_PX on screen."""
        targets = self._move_targets or []
        if not targets:
            return d
        region, rv3d = context.region, context.region_data
        frame, w = self._drag_frame, self._drag_start['w']
        edges = self._drag_start.get('span') or (0.0, w)
        mid = _front_point(frame, d + w / 2.0, frame['dim_z'] / 2.0)
        a = _to_screen(region, rv3d, mid)
        z = _to_screen(region, rv3d, mid + frame['x'] * 0.1)
        if a is None or z is None or (z - a).length < 1e-6:
            return d
        reach = MOVE_SNAP_PX * _ui_scale() / ((z - a).length / 0.1)
        best = None
        for t in targets:
            for edge in edges:
                gap = abs(t - (edge + d))
                if gap < reach and (best is None or gap < best[0]):
                    best = (gap, t - edge)
        return best[1] if best else d

    def _update_move(self, context, event):
        if self._typed:
            try:
                from ..dim_edit_overlay import parse_distance
                dist = parse_distance(self._typed)
            except Exception:
                dist = None
            if dist is None:
                return
            # Typed: that far in the way the drag is heading.
            d = -abs(dist) if self._drag_d < 0 else abs(dist)
        else:
            p = self._run_param(context, event)
            if p is None:
                return
            d = p - self._drag_origin
            if not event.shift:
                d = self._snap_move(context, d)
        apply_move(self._drag['cab'], self._drag_start, d)
        self._drag_d = d

    def _update_drag(self, context, event):
        if self._drag['kind'] == 'MOVE':
            self._update_move(context, event)
            return
        if self._typed:
            try:
                from ..dim_edit_overlay import parse_distance
                width = parse_distance(self._typed)
            except Exception:
                width = None
            if not width:
                return
            d = delta_for_width(self._drag, self._drag_start, width)
        else:
            p = self._run_param(context, event)
            if p is None:
                return
            d = p - self._drag_origin
            if not event.shift:
                width = primary_width(self._drag, self._drag_start, d)
                snapped = round(width / SNAP_STEP) * SNAP_STEP
                d = delta_for_width(self._drag, self._drag_start, snapped)
        self._drag_d = apply_delta(context, self._drag, self._drag_start, d)

    def _end_drag(self, context, commit):
        h, start = self._drag, self._drag_start
        self._drag = None
        self._drag_frame = None
        self._typed = ''
        if h is None:
            return
        if not commit:
            restore(context, h, start)
        elif abs(self._drag_d) > 1e-6:
            try:
                bpy.ops.ed.undo_push(message="Grab")
            except Exception:
                traceback.print_exc()
        self._drag_d = 0.0
        self._collect(context)

    # ---- events ----

    def modal(self, context, event):
        try:
            return self._modal(context, event)
        except Exception:
            traceback.print_exc()
            try:
                self._cleanup(context)
            except Exception:
                traceback.print_exc()
            return {'CANCELLED'}

    def _modal(self, context, event):
        if getattr(self, '_exit_requested', False):
            self._exit_requested = False
            if self._drag is not None:
                self._end_drag(context, commit=True)
            self._cleanup(context)
            return {'FINISHED'}

        mode = grab_mode_active(context.scene)
        if mode != self._last_mode:
            self._last_mode = mode
            if self._drag is not None:
                self._end_drag(context, commit=True)
            self._collect(context)
            context.area.tag_redraw()

        self._mouse = (event.mouse_region_x, event.mouse_region_y)

        if event.type == 'MOUSEMOVE':
            if self._drag is not None:
                self._update_drag(context, event)
            else:
                self._hover = self._pick(context, event)
            context.area.tag_redraw()
            return {'PASS_THROUGH'} if self._drag is None else {'RUNNING_MODAL'}

        if self._drag is None:
            # A mode you leave on claims only presses on its handles.
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                try:
                    from ....operators.viewport_hud import click_hits_widget
                    if click_hits_widget(context, context.area,
                                         event.mouse_region_x,
                                         event.mouse_region_y):
                        return {'PASS_THROUGH'}
                except Exception:
                    pass
                h = self._pick(context, event)
                if h is None:
                    return {'PASS_THROUGH'}
                self._start_drag(context, event, h)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type in ('RET', 'NUMPAD_ENTER', 'ESC') \
                    and event.value == 'PRESS':
                self._cleanup(context)
                return {'FINISHED'}
            return {'PASS_THROUGH'}

        # ---- dragging ----
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self._end_drag(context, commit=True)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in ('ESC', 'RIGHTMOUSE') and event.value == 'PRESS':
            self._end_drag(context, commit=False)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in ('RET', 'NUMPAD_ENTER') and event.value == 'PRESS':
            self._end_drag(context, commit=True)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS':
            if event.type in _TYPE_CHARS:
                self._typed += _TYPE_CHARS[event.type]
                self._update_drag(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type == 'QUOTE':
                self._typed += '"' if event.shift else "'"
                self._update_drag(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type == 'BACK_SPACE':
                self._typed = self._typed[:-1]
                self._update_drag(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.ctrl or event.oskey:
                # Undo mid-drag would pull the cabinets out from under it.
                return {'RUNNING_MODAL'}
        if event.type in ('LEFT_SHIFT', 'RIGHT_SHIFT'):
            self._update_drag(context, event)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}


# Running grabs, so undo / redo can drop and rebuild their handles (the
# records name objects that undo replaces).
_live_grabs = set()


@persistent
def _undo_pre(scene, *args):
    for op in list(_live_grabs):
        try:
            op.forget_scene_refs()
        except Exception:
            _live_grabs.discard(op)


@persistent
def _undo_post(scene, *args):
    for op in list(_live_grabs):
        try:
            op.refresh_after_undo()
        except Exception:
            traceback.print_exc()


_UNDO_HANDLERS = (
    (bpy.app.handlers.undo_pre, _undo_pre),
    (bpy.app.handlers.redo_pre, _undo_pre),
    (bpy.app.handlers.undo_post, _undo_post),
    (bpy.app.handlers.redo_post, _undo_post),
)


def register():
    bpy.utils.register_class(hb_frameless_OT_grab)
    for handlers, fn in _UNDO_HANDLERS:
        if fn not in handlers:
            handlers.append(fn)


def unregister():
    for handlers, fn in _UNDO_HANDLERS:
        if fn in handlers:
            handlers.remove(fn)
    _live_grabs.clear()
    bpy.utils.unregister_class(hb_frameless_OT_grab)
